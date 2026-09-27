# Discover fired trigger names

Read only when the user needs names, rather than a boolean for a known chain. Use a narrow, verified chain pattern and `NFiles=1`. Configured menu chains and chains observed to fire are different sets.

## Callable

Copy this Release 25 callable into the query script. Preserve its function name and collection metadata.

```python
import ast
from typing import Iterable, Tuple, TypeVar

from func_adl import ObjectStream, func_adl_callable

T = TypeVar("T")


def _add_trigger_decision_tool(s: ObjectStream[T]) -> ObjectStream[T]:
    return s.MetaData(
        {
            "metadata_type": "inject_code",
            "name": "trigger_decision_tool_for_name_list",
            "header_includes": [
                "AsgTools/AnaToolHandle.h",
                "TrigConfInterfaces/ITrigConfigTool.h",
                "TrigDecisionTool/TrigDecisionTool.h",
                "string",
                "vector",
            ],
            "private_members": [
                "asg::AnaToolHandle<TrigConf::ITrigConfigTool> m_trigConfNames;",
                "asg::AnaToolHandle<Trig::TrigDecisionTool> m_trigDecNames;",
            ],
            "instance_initialization": [
                'm_trigConfNames("TrigConf::xAODConfigTool/xAODConfigTool")',
                'm_trigDecNames("Trig::TrigDecisionTool/TrigDecisionTool")',
            ],
            "initialize_lines": [
                "ANA_CHECK(m_trigConfNames.initialize());",
                'ANA_CHECK(m_trigDecNames.setProperty("ConfigTool", m_trigConfNames.getHandle()));',
                'ANA_CHECK(m_trigDecNames.setProperty("TrigDecisionKey", "xTrigDecision"));',
                "ANA_CHECK(m_trigDecNames.initialize());",
            ],
            "link_libraries": ["TrigDecisionToolLib", "TrigConfInterfaces"],
        }
    )


def _fired_trigger_names_processor(
    s: ObjectStream[T], a: ast.Call
) -> Tuple[ObjectStream[T], ast.Call]:
    new_s = s.MetaData(
        {
            "metadata_type": "add_cpp_function",
            "name": "fired_trigger_names",
            "include_files": ["string", "vector"],
            "arguments": ["pattern"],
            "code": [
                "std::vector<std::string> result;",
                "for (const auto& chain : m_trigDecNames->getListOfTriggers(pattern)) {",
                "    if (m_trigDecNames->isPassed(chain, TrigDefs::Physics)) result.push_back(chain);",
                "}",
            ],
            "return_type": "std::string",
            "return_is_collection": True,
        }
    )
    return _add_trigger_decision_tool(new_s), a


@func_adl_callable(_fired_trigger_names_processor)
def fired_trigger_names(pattern: str) -> Iterable[str]:
    """Return configured chains matching pattern that passed this event."""
    ...
```

## Query and delivery

Define `pattern` as a narrow trigger-family regex appropriate to the input menu. Flatten the custom collection with `SelectMany`; returning it directly as a dictionary field fails translation/output.

```python
from func_adl_servicex_xaodr25 import FuncADLQueryPHYSLITE
from servicex import Sample, ServiceXSpec, dataset, deliver
from servicex_analysis_utils import to_awk

query = (
    FuncADLQueryPHYSLITE()
    .SelectMany(lambda event: fired_trigger_names(pattern))
    .Select(lambda name: {"fired_trigger": name})
)
sample = Sample(
    Name="trigger_names", Dataset=dataset.Rucio(dataset_name),
    NFiles=1, Query=query,
)
rows = to_awk(deliver(ServiceXSpec(Sample=[sample])))["trigger_names"]
names = sorted(set(rows["fired_trigger"]))
```

Supply `dataset_name` and `pattern` before running. Use `FuncADLQueryPHYS` for PHYS.

Each output row is one fired chain name, not one event; event grouping is lost. An empty result can mean no matching chain fired or the pattern is wrong. Inspect the input menu before broadening it. Do not scan the full menu over a full dataset.

Dependencies: `func_adl_servicex_xaodr25`, `servicex`, `servicex-analysis-utils`. When debugging translation, check that generated C++ includes TDT initialization, `getListOfTriggers`, and `isPassed(..., TrigDefs::Physics)`.
