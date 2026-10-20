# Discover unfamiliar xAOD accessors

Use this route when the usual object recipes do not cover a requested quantity,
or a query reports an unknown method. Do not guess an accessor, decoration type,
enum number, or overload. Keep a short record of the package version and the
source file/signature that established the accessor.

## 1. Inspect the installed Python stubs

The release-specific query package contains generated Python interface files,
not the event data itself. For Release 25, locate the files in the same Python
environment that will run the query:

```python
from importlib.metadata import version
from pathlib import Path
import func_adl_servicex_xaodr25 as xaod

print(version("func_adl_servicex_xaodr25"))
print(Path(xaod.__file__).parent)
```

For another release, use its query package. Follow the collection's return type
from `event_collection.py` to the object module, for example `xAOD/muon_v1.py` or
`xAOD/jet_v1.py`. Search that file for the requested quantity and related terms;
follow imported enum definitions and inherited interfaces too. Read the method
signature and its metadata/callback rather than relying on `dir()` alone.
For example, a muon's segment count is exposed as `nMuonSegments()`.

Some APIs take an output-reference argument and return a success boolean.
Do not histogram that boolean as the requested value or pass a Python variable
expecting C++ to modify it. Prefer a supported value-returning overload such as
the muon `uint8SummaryValue` when its argument enum and semantics match. Import
the named enum from the module identified by the signature; different summary
enum classes are not interchangeable.

Templates are not necessarily missing: the package explicitly supports some
parameterized calls. For example, after verifying the stored attribute type,
`jet.getAttribute[cpp_float]("EMFrac")` uses
`cpp_float` from `func_adl_servicex_xaodr25.type_support`. Check that file for
other supported types before injecting C++. A method absent from the stubs is
not evidence that the underlying xAOD object lacks it.

## 2. Inspect the matching Athena source

If the stubs cannot express the operation, read the corresponding headers in
[Athena](https://gitlab.cern.ch/atlas/athena), using the backend's release tag
(for example `release/25.2.80`), rather than assuming the default branch matches.
Start under `Event/xAOD/<package>/<package>/versions/`, and follow the `.icc`,
implementation `.cxx`, enum header, or base class as needed. Examples:

- `xAODMuon/versions/Muon_v1.h` for muon accessors.
- `xAODJet/versions/Jet_v1.h` and `Jet_v1.icc` for jet templates.
- `xAODTracking/TrackingPrimitives.h` for track-summary enums.

If the web page returns an HTML login or bot challenge, it is not a header.
For public files, GitLab's repository-files API is another way to read the
source. URL-encode the project, file path, and ref, for example:

```text
https://gitlab.cern.ch/api/v4/projects/atlas%2Fathena/repository/files/Event%2FxAOD%2FxAODJet%2FxAODJet%2Fversions%2FJet_v1.h/raw?ref=release%2F25.2.80
```

Verify the exact overload, template type, constness, return type, required
headers, units, and missing-value behavior. Check derivation slimming settings
or the input file to establish that the auxiliary field/association is retained;
a header only proves that an API exists. Missing data is different from a
physical zero. Do not silently replace a missing attribute with zero.

## 3. Wrap an unsupported operation in a small C++ callable

Use `func_adl_callable` with `add_cpp_function` metadata for a simple operation
that needs no analysis tool. Use the tool helpers in
[the tool reference](datamodel-xaod-tools-btagging.md) only when an actual tool
is needed. Keep the Python function name, metadata `name`, argument names, and
Python/C++ return types consistent. Declare a local `result` in `code` (or set
`result_name` explicitly); metadata `return_type` does not declare that variable.

For example, `Jet_v1.h` in Release 25 declares
`template<typename T> std::vector<const T*> getAssociatedObjects(const std::string&) const`.
It throws if the association is absent, and thinned links become null pointers.
This callable counts valid tracks without dereferencing null pointers:

```python
import ast
from typing import Tuple, TypeVar

from func_adl import ObjectStream, func_adl_callable
from func_adl_servicex_xaodr25 import FuncADLQueryPHYSLITE
from func_adl_servicex_xaodr25.xAOD.jet_v1 import Jet_v1

T = TypeVar("T")


def _ghost_track_count_cpp(
    stream: ObjectStream[T], call: ast.Call
) -> Tuple[ObjectStream[T], ast.Call]:
    return stream.MetaData({
        "metadata_type": "add_cpp_function",
        "name": "ghost_track_count",
        "include_files": ["xAODJet/Jet.h", "xAODTracking/TrackParticle.h"],
        "arguments": ["jet"],
        "code": [
            "int result = 0;",
            'for (const auto* track : jet->getAssociatedObjects<xAOD::TrackParticle>("GhostTrack")) {',
            "    if (track != nullptr) ++result;",
            "}",
        ],
        "return_type": "int",
    }), call


@func_adl_callable(_ghost_track_count_cpp)
def ghost_track_count(jet: Jet_v1) -> int:
    """Count non-null tracks in the GhostTrack association on the worker."""
    ...


query = (
    FuncADLQueryPHYSLITE()
    .Select(lambda event: {"jets": event.Jets()})
    .Select(lambda c: {
        "ghost_track_count": c.jets.Select(lambda jet: ghost_track_count(jet)),
    })
)
```

The Python function is a query marker, not a client-side implementation.
The callback attaches the C++ metadata when the query uses it. Keep all needed
collections in the query's first selection and return a flat dictionary in the
last selection. Preserve empty object lists when an event count is needed.

## Validate the discovery

First build the query and inspect its translated C++: confirm the intended
accessor, enum/template, headers, return type, and null checks survived
translation. This catches interface errors without fetching a dataset. Then
run one real file with the normal ServiceX delivery workflow and check the
output's event/object counts, value range, and units. Record both the API source
and runtime evidence. Python construction or C++ generation alone does not
prove that the worker compiles or that the field exists in a particular file.
