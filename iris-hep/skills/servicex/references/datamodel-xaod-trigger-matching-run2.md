# Match using Run 2 precomputed composites

Use only after finding `TrigMatch_<chain>` or `AnalysisTrigMatch_<chain>` containers in the input. Ignore Aux containers when extracting chain-name suffixes. `TrigNavigation` alone is insufficient.

## Select the prefix

- `TrigMatch_<chain>`: import `tmt_match_object` from `func_adl_servicex_xaodr25`.
- `AnalysisTrigMatch_<chain>`: use `analysis_match_object` below.
- Neither prefix: these recipes do not apply. Consult the release's legacy-navigation matching configuration.

The built-in helper uses `Trig::MatchFromCompositeTool`, whose default `InputPrefix` is `TrigMatch_`. Its optional `dr` argument is ignored: the matching criterion was fixed when the composites were produced.

## Query

Supply a known `chain` and use offline objects referenced by the composites. This electron example returns all and matched pT values in the same passed events; adapt the collection to the requested object type.

```python
from func_adl_servicex_xaodr25 import (
    FuncADLQueryPHYSLITE, tdt_chain_fired, tmt_match_object,
)

query = (
    FuncADLQueryPHYSLITE()
    .Where(lambda event: tdt_chain_fired(chain))
    .Select(lambda event: {"objects": event.Electrons()})
    .Select(lambda c: {
        "all_pt_GeV": c.objects.Select(lambda obj: obj.pt() / 1000.0),
        "matched_pt_GeV": c.objects
            .Where(lambda obj: tmt_match_object(chain, obj))
            .Select(lambda obj: obj.pt() / 1000.0),
    })
)
```

Deliver with `NFiles=1` using [standard delivery](servicex-hints.md). Matching alone does not filter events. Count passing events and events with nonempty matched arrays separately.

## AnalysisTrigMatch prefix override

Copy this callable when the stored prefix is `AnalysisTrigMatch_`; replace `tmt_match_object(chain, obj)` in the query with `analysis_match_object(chain, obj)`.

```python
import ast
from typing import Tuple, TypeVar
from func_adl import ObjectStream, func_adl_callable

T = TypeVar("T")

def _analysis_match_processor(s: ObjectStream[T], a: ast.Call) -> Tuple[ObjectStream[T], ast.Call]:
    new_s = s.MetaData({
        "metadata_type": "add_cpp_function", "name": "analysis_match_object",
        "include_files": [], "arguments": ["chain", "offline_object"],
        "code": ["auto result = m_analysisMatch->match(*offline_object, chain);"],
        "result_name": "result", "return_type": "bool",
    })
    return new_s.MetaData({
        "metadata_type": "inject_code", "name": "analysis_match_tool",
        "header_includes": [
            "AsgTools/AnaToolHandle.h", "TriggerMatchingTool/IMatchingTool.h",
            "TriggerMatchingTool/MatchFromCompositeTool.h",
        ],
        "private_members": ["asg::AnaToolHandle<Trig::IMatchingTool> m_analysisMatch;"],
        "instance_initialization": ['m_analysisMatch("Trig::MatchFromCompositeTool/MatchFromCompositeTool")'],
        "initialize_lines": [
            'ANA_CHECK(m_analysisMatch.setProperty("InputPrefix", "AnalysisTrigMatch_"));',
            "ANA_CHECK(m_analysisMatch.initialize());",
        ],
        "link_libraries": ["TriggerMatchingToolLib"],
    }), a

@func_adl_callable(_analysis_match_processor)
def analysis_match_object(chain: str, offline_object) -> bool:
    ...

```

The override compiled and initialized under AnalysisBase 25.2.80 in a zero-event smoke run; matching on real Run 2 composites remains unvalidated. Validate against the user's input before claiming success.

Sources: [built-in helper metadata](https://github.com/iris-hep/func-adl-types-atlas/blob/main/metadata/trigger.py), [MatchFromCompositeTool implementation](https://gitlab.cern.ch/atlas/athena/-/blob/release/25.0.57/Trigger/TrigAnalysis/TriggerMatchingTool/Root/MatchFromCompositeTool.cxx).
