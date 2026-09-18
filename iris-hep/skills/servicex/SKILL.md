---
name: servicex
description: >-
  Use when querying ATLAS data remotely via ServiceX: fetching branches from
  ROOT NTuples with the Uproot backend, writing FuncADL queries against
  DAOD_PHYS or DAOD_PHYSLITE, selecting datasets by Rucio name or EOS path,
  delivering data as awkward arrays, using servicex_analysis_utils helpers,
  debugging ServiceX cache or backend issues, or initializing ServiceX with
  servicex init.
---

# ServiceX

## Overview

ServiceX is a data delivery service for ATLAS: you submit a query against a
dataset (identified by Rucio name or EOS path), and ServiceX runs the
transformation on CERN infrastructure and streams results back as files you can
load into Python. It eliminates the need to download full data files locally
before analysis.

ServiceX supports two query backends:

| Backend     | Best for                            | Speed  |
| ----------- | ----------------------------------- | ------ |
| `UprootRaw` | ROOT NTuples / flat data structures | Fast   |
| `FuncADL`   | xAOD derivations (PHYSLITE / PHYS)  | Slower |

**Start with `UprootRaw`** unless you specifically need xAOD object access.

## When to Use

- Fetching specific branches from ROOT NTuples stored in Rucio or EOS
- Extracting columns from DAOD_PHYS or DAOD_PHYSLITE without downloading full
  xAOD files
- Iterating quickly on object selection before committing to a full NTuple
  production
- Analysis facility workflows where ATLAS grid access is not available locally
- ATLAS Open Data workflows (`atlasopenmagic` provides dataset containers)

## Key Concepts

| Concept                   | Notes                                                                                   |
| ------------------------- | --------------------------------------------------------------------------------------- |
| `deliver(spec)`           | Main entry point — returns `{sample_name: [Path, ...]}` of result files                 |
| `ServiceXSpec` / `Sample` | Wrap dataset + query + options into a typed spec object                                 |
| `dataset.Rucio(...)`      | Dataset stored in Rucio (GRID); pass the full DID string                                |
| `dataset.FileList([...])` | Dataset accessible via URL (EOS, xrootd, https)                                         |
| `query.UprootRaw([...])`  | Uproot backend: select branches and cuts from a ROOT tree                               |
| `FuncADLQueryPHYSLITE`    | FuncADL backend: LINQ-style queries against ATLAS xAOD derivations                      |
| `NFiles=1`                | Limit files for testing — always use `NFiles=1` in development                          |
| `ignore_local_cache=True` | Forces re-delivery; use when debugging stale results                                    |
| `OutputFormat`            | `General` option: `root-rntuple` (recommended), `root-ttree` (default), or `parquet`    |
| `Delivery`                | `General` option: omit to download files; `"URLs"` to stream remotely (expires ~7 days) |
| `to_awk(results)`         | Convenience from `servicex_analysis_utils` — loads **all** files into memory at once;   |
|                           | only suitable for small datasets                                                        |

## Canonical Patterns

### Setup

**Install required packages:**

```bash
pip install servicex servicex-analysis-utils awkward
# For FuncADL xAOD queries only:
pip install func_adl_servicex_xaodr25
```

**Initialize the client (one-time per environment):**

```bash
servicex init
```

This launches a wizard: select your analysis facility, follow the sign-in link,
copy the token from the page, and paste it when prompted. Accept the default
downloads directory. You'll see "Configuration Complete" when done.

### Uproot Backend (NTuples — recommended starting point)

```python
import uproot
from servicex import deliver, ServiceXSpec, Sample, dataset, query

# Dataset in Rucio:
ntuple_dataset = dataset.Rucio("user.atlas:my-ntuple-dataset.root")
# Or from EOS:
# ntuple_dataset = dataset.FileList(["root://eospublic.cern.ch//eos/path/to/file.root"])

uproot_query = query.UprootRaw([{
    "treename": "reco",
    "filter_name": ["jet_pt", "jet_eta", "met"],
    "cut": "(jet_pt > 20000)",  # cuts use branch names directly, in native units
}])

spec = ServiceXSpec(
    General={"OutputFormat": "root-rntuple"},  # avoids TTree failures on PHYSLITE skims
    Sample=[
        Sample(
            Name="my_sample",
            Dataset=ntuple_dataset,
            Query=uproot_query,
            NFiles=1,  # always 1 during development
        )
    ],
)

results = deliver(spec)

# results["my_sample"] is a list of local file paths
for path in results["my_sample"]:
    with uproot.open(path) as f:
        arr = f["reco"].arrays(library="ak")
        jet_pt_GeV = arr["jet_pt"] / 1000.0  # convert MeV → GeV
```

### FuncADL Backend (xAOD / PHYSLITE)

```python
from servicex import deliver, ServiceXSpec, Sample, dataset
from func_adl_servicex_xaodr25 import FuncADLQueryPHYSLITE

# Two-Select pattern: first collect objects, then extract columns
jet_query = (
    FuncADLQueryPHYSLITE()
    .Select(lambda e: {"jets": e.Jets()})
    .Select(lambda c: {"jet_pt": c.jets.Select(lambda j: j.pt() / 1000.0)})  # GeV
)

results = deliver(ServiceXSpec(Sample=[
    Sample(Name="jet_pt_fetch", Dataset=dataset.Rucio(rucio_did), Query=jet_query, NFiles=1),
]))
# results["jet_pt_fetch"] is a list of local file paths; the output tree is
# always named "servicex" for FuncADL (vs. whatever `treename` you set for
# UprootRaw). See references/servicex-hints.md for filtering, multiple
# collections, and a full worked example with a real dataset DID.
```

### URL Delivery (Remote Streaming)

Receive URLs for direct remote access instead of downloading files (these
expire within ~7 days, so only use this for short-lived access):

```python
spec = ServiceXSpec(
    General={"Delivery": "URLs"},
    Sample=[Sample(Name="data", Dataset=ds, Query=q, NFiles=1)],
)
results = deliver(spec)  # results["data"] contains URLs, not local paths
```

## Query Backend Selection

| Situation                                       | Use                    |
| ----------------------------------------------- | ---------------------- |
| Dataset name contains `PHYSLITE`                | `FuncADLQueryPHYSLITE` |
| Dataset name contains `DAOD_PHYS`               | `FuncADLQueryPHYS`     |
| ATLAS OpenData (usually has "OpenData" in name) | `FuncADLQueryPHYSLITE` |
| Working with ROOT NTuples / flat trees          | `query.UprootRaw`      |
| Not sure — start here                           | `query.UprootRaw`      |

For `FuncADLQueryPHYS` (non-PHYSLITE derivations), calibrations run
automatically. Pass `calibrated=False` to a collection to skip calibration, but
note that PHYSLITE has no uncalibrated objects.

## PHYSLITE vs PHYS

| Feature            | PHYSLITE                                  | PHYS                                    |
| ------------------ | ----------------------------------------- | --------------------------------------- |
| Size               | ~10× smaller                              | Full derivation                         |
| Object collections | `AnalysisJets`, `AnalysisElectrons`, etc. | `AntiKt4EMPFlowJets`, `Electrons`, etc. |
| CP recommendations | Default CP tools configured               | Requires manual tool setup              |
| Availability       | Most mc20/mc23 campaigns                  | All campaigns                           |

## xAOD Object Names (PHYSLITE)

| Object    | FuncADL accessor        |
| --------- | ----------------------- |
| Jets      | `e.Jets()`              |
| Electrons | `e.Electrons()`         |
| Muons     | `e.Muons()`             |
| Taus      | `e.TauJets("AnalysisTauJets")` |
| Photons   | `e.Photons()`           |
| MET       | `e.MissingET().First()` |

See `references/datamodel-xaod-missing-et.md` and
`references/datamodel-xaod-tau.md` for why MET and Taus need the extra call.

## Troubleshooting

| Symptom                                | Likely Cause                         | Fix                                                    |
| -------------------------------------- | ------------------------------------ | ------------------------------------------------------ |
| Same result after query fix            | Cached result returned               | Add `ignore_local_cache=True`                          |
| UprootRaw transform fails on PHYSLITE  | Default TTree output incompatible    | Add `General={"OutputFormat": "root-rntuple"}` to spec |
| Empty array for a collection           | Wrong collection name for derivation | Check PHYSLITE vs PHYS names                           |
| `ModuleNotFoundError: func_adl...`     | FuncADL package not installed        | `pip install func_adl_servicex_xaodr25`                |
| `ModuleNotFoundError: servicex_anal..` | Utils package missing                | `pip install servicex-analysis-utils`                  |
| "Transform completed with failures"    | C++ error in backend                 | Involve user — only they can see logs                  |
| "Method xxx not found on object"       | Wrong accessor for this derivation   | Check xAOD object schema for your type                 |
| `servicex init` not found              | CLI not installed                    | `pip install servicex` then retry                      |

## Gotchas

- **Units are MeV in xAOD**: `j.pt()` returns MeV. Divide by 1000 before any
  GeV-scale comparisons or histograms.
- **Units in UprootRaw cuts are native**: NTuple branch cuts use whatever units
  are in the tree (often MeV for ATLAS NTuples — check your sample).
- **Cache is aggressive**: If you fix a query bug but get the same result, use
  `ignore_local_cache=True`. Do not use `ignore_cache=True` (old API, no-op).
- **`NFiles=None` means all files**: `NFiles=0` behavior is undefined — use
  `None` for full dataset or a positive integer for testing.
- **Call `deliver` once**: Put all samples in one `ServiceXSpec`. Multiple
  `deliver` calls waste round trips.
- **No awkward in FuncADL queries**: Use `Select` / `Where` instead — awkward
  functions are not available inside the lambda DSL.
- **Use `Dataset=` on `Sample`, not `RucioDID=`**: the `Sample.RucioDID` field
  is deprecated in ServiceX 3.x. Pass a dataset object via
  `Dataset=dataset.Rucio(...)`.
- **PHYSLITE vs PHYS collection names differ**: Using the wrong collection name
  (e.g. `AntiKt4EMPFlowJets` on PHYSLITE) returns empty results silently.
- **FuncADL requires `func_adl_servicex_xaodr25`**: Install separately; not
  included in the base `servicex` package.
- **FuncADL output tree is always `"servicex"`**: When opening FuncADL result
  files with uproot, use `f["servicex"]`. For UprootRaw, the tree name is
  whatever you set in the `treename` field of your query dict.
- **Default output format is `root-ttree`**: This can silently fail on PHYSLITE
  skims. Prefer `General={"OutputFormat": "root-rntuple"}` in all UprootRaw
  specs.
- **URL delivery expires**: Files served via `Delivery: URLs` typically expire
  within 7 days or less. Download them if persistence beyond that is needed.
- **Transform failures**: "Transform completed with failures" errors need the
  user to click the provided link — only the job owner can see the logs. If you
  see this after fixing type errors, involve the user.

## Interop

- **servicex_analysis_utils**: `to_awk(results)` is a convenience helper that
  loads all result files into a single in-memory awkward array — only suitable
  for small datasets; for large data iterate over file paths with uproot instead
- **uproot**: For local ROOT files, use uproot directly — ServiceX only adds
  value for remote or large datasets
- **awkward**: Results from `to_awk` are `ak.Array` — use awkward operations for
  filtering, flattening, and array math
- **Rucio/AMI**: Use `rucio` or `ami` (pyAMI) to find dataset DIDs before
  querying ServiceX
- **atlasopenmagic**: Provides ATLAS Open Data dataset identifiers ready for use
  with `dataset.Rucio(...)` or `dataset.FileList([...])`

## References

- Load `references/servicex-hints.md` for the full FuncADL query-building
  workflow (two-`Select` pattern, object- vs event-level filtering, choosing
  the base query by dataset name, a full worked example for each backend, and
  the "Transform completed with failures" → HELP USER error-handling rule).
- Load `references/servicex-async-hints.md` only when async delivery is
  explicitly requested (`deliver_async` with an `asyncio.wait_for` timeout
  wrapper, and the version-compatibility fallback to sync `deliver`).
- Load the relevant `references/datamodel-xaod-*.md` topic file(s) to keep
  context small:
  - `references/datamodel-xaod-units.md`: MeV→GeV and mm→m conversion rule
    for all xAOD kinematic/distance quantities.
  - `references/datamodel-xaod-objects.md`: accessing Jets/Electrons/Muons/
    Photons at the event level and getting px/py/pz via `.p4()`.
  - `references/datamodel-xaod-tau.md`: TauJets use a different accessor
    (`e.TauJets("AnalysisTauJets")`) than other objects.
  - `references/datamodel-xaod-missing-et.md`: MissingET is a one-element
    sequence — call `.First()` before `.met()`/`.mpx()`/`.mpy()`.
  - `references/datamodel-xaod-tlorentzvector.md`: TLorentzVector method
    names (`Pt()`, `Eta()`, `DeltaR()`, etc.) for 4-vector objects.
  - `references/datamodel-xaod-tools-btagging.md`: use for b-/c-tagging via
    `BTaggingSelectionTool` (`make_a_tool`/`make_tool_accessor`, FTAG working
    points, copying `assets/xaod_hints.py` into the user's package).
  - `references/datamodel-xaod-event-weights.md`: use when combining MC
    and/or data samples — MC event weight, cross-section scaling formula,
    per-run luminosity table, and plot-annotation conventions.

## Docs

- ServiceX docs / tutorial: https://tryservicex.org
- ServiceX frontend source: https://github.com/ssl-hep/ServiceX_frontend
- FuncADL xAOD R25 package: https://pypi.org/project/func-adl-servicex-xaodr25/
- servicex-analysis-utils: https://github.com/ssl-hep/servicex_analysis_utils
