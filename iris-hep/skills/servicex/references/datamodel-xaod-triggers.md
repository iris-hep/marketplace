# xAOD Trigger Decisions, Trigger Names, and Matching

Use this page when a query needs an ATLAS trigger decision, a list of fired trigger names, or matching between a trigger object and an offline object. The examples target `func_adl_servicex_xaodr25` and Release 25 PHYSLITE/PHYS inputs.

## Two different trigger operations

Import the built-in helpers from `func_adl_servicex_xaodr25`:

```python
from func_adl_servicex_xaodr25 import tdt_chain_fired, tmt_match_object
```

- `tdt_chain_fired("HLT_j30_...")` asks the Trigger Decision Tool whether the named chain passed for the current event. The argument is passed to the ATLAS tool, so a valid chain pattern can be used where appropriate.
- `tmt_match_object("HLT_j30_...", jet, 0.2)` asks the Trigger Matching Tool whether an offline object is within the requested delta-R of an object accepted by that chain. It does not select events by itself; combine it with `tdt_chain_fired` when the event must have fired the chain.

The trigger helpers add the required C++ tools and libraries during translation. Do not replace them with an `awkward` operation inside the ServiceX query.

## Filter events by a chain

Use a top-level `Where` for an event decision. Keep the chain name in a Python variable so it can be changed without rewriting the query:

```python
from func_adl_servicex_xaodr25 import FuncADLQueryPHYSLITE
from func_adl_servicex_xaodr25 import tdt_chain_fired

chain = "HLT_j30_momemfrac006_L1jJ160"
query = (FuncADLQueryPHYSLITE()
    .Where(lambda e: tdt_chain_fired(chain))
    .Select(lambda e: {"fired": True})
)
```

For an OR of chains, call the helper once per chain:

```python
chains = ["HLT_e7_lhmedium_mu24_L1MU14FCH", "HLT_e7_lhmedium_L1eEM5_mu24_L1MU14FCH"]
query = FuncADLQueryPHYSLITE().Where(
    lambda e: any(tdt_chain_fired(name) for name in chains)
)
```

## Return the names of fired chains

`tdt_chain_fired` is deliberately a boolean operation. To return trigger names, add a small callable that injects C++ and returns a `std::vector<std::string>`. This is useful for trigger-menu inspection, but it can produce a large result. Always pass a narrow pattern such as `"EF_j.*"` or `"HLT_j.*"`; do not request `".*"` for a full dataset.

The following template initializes the same Trigger Decision Tool used by `tdt_chain_fired`, obtains configured chains matching the requested pattern, and keeps only chains that passed the Physics decision for the current event:

```python
import ast
from typing import List, Tuple, TypeVar

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
def fired_trigger_names(pattern: str) -> List[str]:
    """Return configured chains matching pattern that passed this event."""
    ...
```

The Python return annotation and the metadata must describe a collection of strings. Keep the variable/function name `fired_trigger_names` unchanged between the decorator, definition, and query. The final ServiceX selection is a single dictionary:

```python
trigger_names_query = FuncADLQueryPHYSLITE().Select(
    lambda e: {"fired_triggers": fired_trigger_names("EF_j.*")}
)
```

Use `"HLT_j.*"` for current HLT jet chains. The exact available prefix is data-taking-period dependent; discover it from the first file before selecting a chain for a larger query.

## Delivery and returned layout

Use one delivery with `NFiles=1` while developing. The trigger-name query returns one jagged string collection per event, so flatten and deduplicate it after delivery:

```python
import awkward as ak

from servicex import Sample, ServiceXSpec, dataset, deliver
from servicex_analysis_utils import to_awk

sample = Sample(
    Name="trigger_names",
    Dataset=dataset.Rucio(dataset_name),
    NFiles=1,
    Query=trigger_names_query,
)
delivered = deliver(ServiceXSpec(Sample=[sample]))
events = to_awk(delivered)["trigger_names"]
names = sorted(set(name for event in events["fired_triggers"] for name in event))
```

If no chain matches the pattern, `names` is empty. Preserve that result and check the pattern against the trigger naming convention before trying a broader pattern. A large list of strings can stress ROOT output and memory; use a narrower pattern or return booleans for a known chain when possible.

## Four common trigger questions

The snippets below assume `dataset_name`, `base_query = FuncADLQueryPHYSLITE()`, and the normal `deliver` setup from `references/servicex-hints.md`.

### 1. How often did a trigger fire?

Return one boolean per examined event, without filtering the event stream. Count both the denominator and numerator in Python:

```python
chain = "HLT_j30_momemfrac006_L1jJ160"
frequency_query = (base_query
    .Select(lambda e: {"fired": tdt_chain_fired(chain)})
)

events = to_awk(deliver(ServiceXSpec(Sample=[Sample(
    Name="trigger_frequency", Dataset=dataset.Rucio(dataset_name),
    NFiles=1, Query=frequency_query
)])))["trigger_frequency"]
examined = len(events["fired"])
passed = int(ak.sum(events["fired"]))
fraction = passed / examined if examined else 0.0
```

Report `passed`, `examined`, and `fraction`; a one-file result is a validation measurement, not a dataset-wide rate.

### 2. Which jet triggers fired in the first file?

Use the name-list callable with a narrow prefix and deduplicate across events:

```python
trigger_names_query = base_query.Select(
    lambda e: {"fired_triggers": fired_trigger_names("EF_j.*")}
)
# Change only the pattern to "HLT_j.*" for HLT jet chains.
events = to_awk(deliver(ServiceXSpec(Sample=[Sample(
    Name="jet_trigger_names", Dataset=dataset.Rucio(dataset_name),
    NFiles=1, Query=trigger_names_query
)])))["jet_trigger_names"]
fired_jet_chains = sorted(set(
    name for event in events["fired_triggers"] for name in event
))
```

Do not return every configured trigger from a full dataset. If the output is empty, first inspect whether the file uses `HLT_j` rather than `EF_j` names.

### 3. Leading jet pT in events that fired a trigger

Filter events with the decision helper, return all jet pT values, and take the leading value in Awkward after delivery. The event-level `Where` keeps trigger logic in ServiceX; `mask_identity=True` makes zero-jet events explicit:

```python
chain = "HLT_j30_momemfrac006_L1jJ160"
leading_query = (base_query
    .Where(lambda e: tdt_chain_fired(chain))
    .Select(lambda e: {"jets": e.Jets()})
    .Select(lambda c: {"jet_pt": c.jets.Select(lambda j: j.pt() / 1000.0)})
)
events = to_awk(deliver(ServiceXSpec(Sample=[Sample(
    Name="leading_jet_pt", Dataset=dataset.Rucio(dataset_name),
    NFiles=1, Query=leading_query
)])))["leading_jet_pt"]
leading_pt = ak.max(events["jet_pt"], axis=1, mask_identity=True)
```

Plot or histogram `ak.drop_none(leading_pt)`. If every selected event has zero jets, the result is empty and should be reported as such.

### 4. Matched trigger-jet pT compared with all jet pT

First require the chain to have fired. Then return both all offline jets and the subset within the matching cone. The same event supplies both distributions:

```python
chain = "HLT_j30_momemfrac006_L1jJ160"
matching_query = (base_query
    .Where(lambda e: tdt_chain_fired(chain))
    .Select(lambda e: {"jets": e.Jets()})
    .Select(lambda c: {
        "all_jet_pt": c.jets.Select(lambda j: j.pt() / 1000.0),
        "matched_jet_pt": c.jets
            .Where(lambda j: tmt_match_object(chain, j, 0.2))
            .Select(lambda j: j.pt() / 1000.0),
    })
)
events = to_awk(deliver(ServiceXSpec(Sample=[Sample(
    Name="matched_jet_pt", Dataset=dataset.Rucio(dataset_name),
    NFiles=1, Query=matching_query
)])))["matched_jet_pt"]
all_pt = ak.flatten(events["all_jet_pt"])
matched_pt = ak.flatten(events["matched_jet_pt"])
```

Fill two histograms with the same GeV axis and overlay them. `matched_pt` may be empty even when the event fired; that is a valid matching result, not an instruction to substitute all jets. A zero-jet event contributes no entries to either flattened array.

## Dependencies and checks

For a standalone script, list `func_adl_servicex_xaodr25`, `servicex`, `servicex-analysis-utils`, `awkward`, `numpy`, and the plotting package in its PEP 723 dependency block. Keep `NFiles=1` until the query translates and the returned fields have been inspected. Check the generated C++ when introducing the name-list callable: it must contain the Trigger Decision Tool initialization, `getListOfTriggers`, and `isPassed(..., TrigDefs::Physics)`. If a transform fails after translation and the ServiceX logs are needed, follow the normal `HELP USER` path from the main ServiceX skill.
