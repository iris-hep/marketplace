# ServiceX Local on WSL2

Use this reference when a hosted ATLAS ServiceX xAOD/PHYSLITE transform is
failing and its worker log is unavailable. It runs the same FuncADL xAOD code
generation and science step locally, using a Windows Python process and the
`atlas_al9` WSL2 distro. Replace `C:\Temp\servicex-local\run-001` with a
temporary directory you control. Do not use the repository directory for data
or generated files.

## Install the Windows-side environment

Run these commands in PowerShell. A normal Python virtual environment is fine;
`uv` is convenient for a disposable environment.

```powershell
$Work = 'C:\Temp\servicex-local\run-001'
New-Item -ItemType Directory -Force $Work | Out-Null
uv venv "$Work\.venv"
& "$Work\.venv\Scripts\python.exe" -m pip install `
  'servicex-local==1.2.1' `
  'func-adl-servicex-xaodr25' `
  'uproot'
```

The local package includes the ServiceX client, analysis utilities, and the
local xAOD code generator dependencies. If installation fails, report the
Python version and the package resolver error before trying a different
version.

## Resolve and verify AnalysisBase

The WSL runner creates a temporary working directory and runs
`asetup AnalysisBase,<release>,here`. Resolve the default release in another
temporary directory so the exact version is known before the Python call:

```powershell
$Release = (wsl -d atlas_al9 -- bash -ic @'
set -o pipefail
setupATLAS >/dev/null || exit 1
release_work=$(mktemp -d)
trap 'rm -rf "$release_work"' EXIT
cd "$release_work"
asetup --stable AnalysisBase,25.2,latest >/dev/null || exit 1
env | sed -n 's/^AtlasVersion=//p'
'@).Trim()
if ([string]::IsNullOrWhiteSpace($Release)) { throw 'AnalysisBase release resolution returned no AtlasVersion' }
"Resolved AnalysisBase release: $Release"
```

For a pinned release, replace the resolution command with
`asetup AnalysisBase,25.2.<patch>` and still print the exported `AtlasVersion`
value (use `env | sed -n 's/^AtlasVersion=//p'` if shell expansion is empty). A failed
setup is a failed preflight; do not pass an unverified version to the WSL
transformer. The release must match the query package (`xaodr25` here).

The stable alias is only a candidate. Run the jet script once with
`ignore_local_cache=True` and treat a C++ compile as the compatibility test. If
the generated code fails on a changed xAOD API, retry with an earlier stable
`25.2` patch and record both versions. During validation, `25.2.111` failed at
`xAOD::TFileAccessTracer::enableDataSubmission`, while `25.2.80` compiled the
same generated query; the latter is the package-matched fallback for this
runbook, not a Docker image tag.

## Check VOMS and download one file

The download needs an ATLAS VOMS proxy. The command below only initializes a
proxy when the current one is expired or missing; it may prompt for the user's
certificate credentials.

```powershell
$WslWork = (wsl -d atlas_al9 -- wslpath -a $Work).Trim()
if ([string]::IsNullOrWhiteSpace($WslWork)) { throw 'Could not convert the Windows work path to WSL' }
wsl -d atlas_al9 -- bash -ic "set -eo pipefail; setupATLAS >/dev/null; lsetup rucio >/dev/null; if ! voms-proxy-info -timeleft | grep -Eq '[1-9]'; then voms-proxy-init --voms atlas; fi; voms-proxy-info -timeleft | grep -Eq '[1-9]'; mkdir -p '$WslWork'; rucio get --no-subdir --dir '$WslWork' 'mc23_13p6TeV:DAOD_PHYSLITE.50426177._000001.pool.root.1'"
```

For example, here is a Run 3 jet file. Use it only if no specific file is
given by the user:

```text
mc23_13p6TeV:mc23_13p6TeV.801166.Py8EG_A14NNPDF23LO_jj_JZ1.deriv.DAOD_PHYSLITE.e8514_e8586_s4618_s4619_r17610_r17609_p7266_tid50426177_00
```

Use `rucio list-files <dataset-DID>` before downloading if the file name or
replica status is uncertain. Confirm the downloaded file exists in `$Work` and
record its byte size and the checksum reported by Rucio.

## Run the one-file jet transform

Save the following as `$Work\run_local.py`, replacing `RELEASE` and
`INPUT_FILE` with the resolved release and Windows path. This deliberately
assembles the working WSL path rather than calling `local_deliver()`; the
high-level WSL route is tracked in [ServiceX-Local issue #98](https://github.com/ssl-hep/ServiceX-Local/issues/98).

```python
from pathlib import Path
import logging

import uproot
from servicex import Sample, ServiceXSpec, dataset
from func_adl_servicex_xaodr25 import FuncADLQueryPHYSLITE
from servicex_local.adaptor import SXLocalAdaptor
from servicex_local.codegen import LocalXAODCodegen
from servicex_local.deliver import deliver
from servicex_local.science_images import WSL2ScienceImage

INPUT_FILE = Path(r"INPUT_FILE")
RELEASE = "RELEASE"
CACHE_DIR = INPUT_FILE.parent / "servicex-cache"

if not INPUT_FILE.is_file():
    raise FileNotFoundError(INPUT_FILE)

# INFO is required to expose the complete AnalysisBase runner output.
logging.basicConfig(level=logging.INFO, force=True)
base_query = FuncADLQueryPHYSLITE()
jet_query = (
    base_query
    .Select(lambda e: {"jets": e.Jets()})
    .Select(lambda c: {
        "jet_pt": c.jets.Select(lambda j: j.pt() / 1000.0),
        "jet_eta": c.jets.Select(lambda j: j.eta()),
    })
)

spec = ServiceXSpec(
    Sample=[
        Sample(
            Name="jets",
            Dataset=dataset.FileList([str(INPUT_FILE)]),
            Query=jet_query,
        )
    ]
)

adaptor = SXLocalAdaptor(
    LocalXAODCodegen(),
    WSL2ScienceImage("atlas_al9", RELEASE),
    CACHE_DIR,
    "http://localhost:5001",
)
results = deliver(
    spec,
    adaptor=adaptor,
    ignore_local_cache=True,
    display_progress=False,
)

paths = [Path(p) for p in results["jets"]]
if len(paths) != 1 or not paths[0].is_file():
    raise RuntimeError(f"Unexpected ServiceX Local result: {paths}")
with uproot.open(paths[0]) as root_file:
    tree = root_file["atlas_xaod_tree"]
    keys = [str(k) for k in tree.keys()]
    print({"output": str(paths[0]), "entries": tree.num_entries, "branches": keys})
    assert tree.num_entries > 0
    assert any("jet_pt" in key for key in keys)
    assert any("jet_eta" in key for key in keys)
```

Run it with:

```powershell
& "$Work\.venv\Scripts\python.exe" "$Work\run_local.py"
```

The WSL science runner writes a `wsl_log.txt` beside the generated transformer
files under the system temporary directory. Search for it if the Python call
raises:

```powershell
Get-ChildItem $env:TEMP -Filter wsl_log.txt -Recurse -ErrorAction SilentlyContinue |
  Sort-Object LastWriteTime -Descending | Select-Object -First 5 FullName,LastWriteTime
```

Read the newest log before retrying. A missing input or proxy is an access
failure; `asetup` output is a release failure; C++ compiler or xAOD accessor
errors are code-generation/science-image failures. Use a new cache directory or
keep `ignore_local_cache=True` after changing the query.

On `atlas_al9` with `servicex-local==1.2.1`, the compile can succeed and the
subsequent runner can still fail at `source x86_64*/setup.sh` because this WSL
installation reports an `aarch64-el9-gcc14-opt` platform. In the generated
request directory, edit that one line in `runner.sh` to
`source aarch64*/setup.sh`, then rerun the generated
`wsl_transform_script.sh`. The output is written beside the generated files;
open it with `uproot` and verify `atlas_xaod_tree`, `jet_pt`, `jet_eta`, and a
positive entry count. Keep the original `wsl_log.txt` and note the workaround.

## Package limitation and working WSL assembly

The documented high-level API is `local_deliver(spec, xAODConfig(...))`, but
`servicex-local==1.2.1` builds an image string from the Docker transformer name
even when its platform is WSL2. Its WSL implementation instead splits the
image string into `wsl_distro:AnalysisBase_release`, so the high-level call
tries to use the Docker image name as a WSL distro. The direct assembly above
supplies the expected `atlas_al9:<release>` value and is the supported path for
this skill until [issue #98](https://github.com/ssl-hep/ServiceX-Local/issues/98)
is fixed.
