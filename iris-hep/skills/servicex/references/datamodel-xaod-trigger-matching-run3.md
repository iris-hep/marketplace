# Match using Run 3 navigation

Use after finding `HLTNav_Summary_*` in the input. Copy the callable below, changing `HLTSummary` to the exact container key. It matches one offline `xAOD::IParticle` to retained features for a chain.

## Callable

```python
import ast
from typing import Tuple, TypeVar

from func_adl import ObjectStream, func_adl_callable

T = TypeVar("T")


def _add_r3_matching_tool(s: ObjectStream[T]) -> ObjectStream[T]:
    return s.MetaData(
        {
            "metadata_type": "inject_code",
            "name": "run3_trigger_matching_tool",
            "header_includes": [
                "AsgTools/AnaToolHandle.h",
                "TrigConfInterfaces/ITrigConfigTool.h",
                "TrigDecisionTool/TrigDecisionTool.h",
                "TriggerMatchingTool/IMatchingTool.h",
                "TriggerMatchingTool/IMatchScoringTool.h",
                "TriggerMatchingTool/R3MatchingTool.h",
            ],
            "private_members": [
                "asg::AnaToolHandle<TrigConf::ITrigConfigTool> m_r3TrigConf;",
                "asg::AnaToolHandle<Trig::TrigDecisionTool> m_r3TrigDec;",
                "asg::AnaToolHandle<Trig::IMatchScoringTool> m_r3Score;",
                "asg::AnaToolHandle<Trig::IMatchingTool> m_r3mt;",
            ],
            "instance_initialization": [
                'm_r3TrigConf("TrigConf::xAODConfigTool/xAODConfigTool")',
                'm_r3TrigDec("Trig::TrigDecisionTool/TrigDecisionTool")',
                'm_r3Score("Trig::DRScoringTool/DRScoringTool")',
                'm_r3mt("Trig::R3MatchingTool/R3MatchingTool")',
            ],
            "initialize_lines": [
                "ANA_CHECK(m_r3TrigConf.initialize());",
                'ANA_CHECK(m_r3TrigDec.setProperty("ConfigTool", m_r3TrigConf.getHandle()));',
                'ANA_CHECK(m_r3TrigDec.setProperty("TrigDecisionKey", "xTrigDecision"));',
                'ANA_CHECK(m_r3TrigDec.setProperty("NavigationFormat", "TrigComposite"));',
                'ANA_CHECK(m_r3TrigDec.setProperty("HLTSummary", "HLTNav_Summary_DAODSlimmed"));',
                "ANA_CHECK(m_r3TrigDec.initialize());",
                "ANA_CHECK(m_r3Score.initialize());",
                'ANA_CHECK(m_r3mt.setProperty("TrigDecisionTool", m_r3TrigDec.getHandle()));',
                'ANA_CHECK(m_r3mt.setProperty("ScoringTool", m_r3Score.getHandle()));',
                "ANA_CHECK(m_r3mt.initialize());",
            ],
            "link_libraries": [
                "TriggerMatchingToolLib",
                "TrigDecisionToolLib",
                "TrigConfInterfaces",
            ],
        }
    )


def _r3_match_object_processor(
    s: ObjectStream[T], a: ast.Call
) -> Tuple[ObjectStream[T], ast.Call]:
    new_s = s.MetaData(
        {
            "metadata_type": "add_cpp_function",
            "name": "r3_match_object",
            "include_files": [],
            "arguments": ["trigger", "offline_object", "dr"],
            "code": [
                "auto result = m_r3mt->match(*offline_object, trigger, dr, false);",
            ],
            "result_name": "result",
            "return_type": "bool",
        }
    )
    return _add_r3_matching_tool(new_s), a


@func_adl_callable(_r3_match_object_processor)
def r3_match_object(trigger: str, offline_object, dr: float = 0.2) -> bool:
    """Return whether an offline object matches a Run 3 trigger object."""
    ...
```

Keep these configuration details:

- Initialize the config, decision, and scoring tools before the matcher; pass explicit handles.
- Set TDT `NavigationFormat="TrigComposite"` and the discovered `HLTSummary`.
- Dereference `offline_object`: func_adl supplies a pointer, but the matcher requires a reference.
- Keep `rerun=false` for stored DAOD navigation. The `dr` value is a matching threshold, not a trigger selection.

## Query

Supply a verified `chain` and an analysis-appropriate `dr`. This electron example can be adapted to other offline particle collections.

```python
from func_adl_servicex_xaodr25 import FuncADLQueryPHYSLITE, tdt_chain_fired

query = (
    FuncADLQueryPHYSLITE()
    .Where(lambda event: tdt_chain_fired(chain))
    .Select(lambda event: {"objects": event.Electrons()})
    .Select(lambda c: {
        "all_pt_GeV": c.objects.Select(lambda obj: obj.pt() / 1000.0),
        "matched_pt_GeV": c.objects
            .Where(lambda obj: r3_match_object(chain, obj, dr))
            .Select(lambda obj: obj.pt() / 1000.0),
    })
)
```

Use `FuncADLQueryPHYS` for PHYS and [standard delivery](servicex-hints.md) with `NFiles=1`. The template has produced offline matches in Release 25 PHYSLITE tests; success for another chain or derivation must be checked.

A single-object match does not identify a unique leg or prove that the object alone satisfied a multi-object chain.

## Empty matches or Bad link info

DAOD slimming retains selected chains and features. A passed decision or a summary container does not prove that a particular chain has usable features. Check the same feature request used by the matcher:

```cpp
Trig::FeatureRequestDescriptor frd(chain);
auto features = m_r3TrigDec->features<xAOD::IParticleContainer>(frd);
const auto n_features = features.size();
const auto n_valid = std::count_if(features.begin(), features.end(),
                                  [](const auto& link) { return link.isValid(); });
// Include <algorithm> in injected C++.
```

| Observation | Interpretation |
| --- | --- |
| No features | No particle features returned for this request; changing delta-R cannot recover missing links |
| Some invalid links | Matching can throw `Bad link info`; skipping the event leaves its match unresolved |
| All links valid, no match | No match at the chosen threshold; inspect offline objects and chain semantics |

Never replace empty matches with all offline objects. Record the input file, chain, object collection, threshold, and tested counts.

For a requested **jet inventory**, the existing [local scan script](../scripts/scan_run3_matching.py) provides per-chain counts. It is jet-specific; do not use it unchanged for electrons, muons, or other objects. Run `uv run --script iris-hep/skills/servicex/scripts/scan_run3_matching.py --help` for input, output, release, summary, pattern, and jet-key options. Read [local WSL2 setup and recovery](https://github.com/iris-hep/marketplace/blob/main/iris-hep/skills/servicex/references/servicex-local-wsl2.md) before executing it. Mixed-link events are skipped and recorded separately; only positive `matched_events` verifies a match. Results apply to the tested file.

For deeper diagnosis, check the input's production release and provenance before consulting [navigation slimming configuration](https://gitlab.cern.ch/atlas/athena/-/blob/release/25.0.57/Trigger/TrigAnalysis/TrigNavSlimmingMT/python/TrigNavSlimmingMTConfig.py) (linked example: Athena 25.0.57).

API sources: [R3MatchingTool](https://atlas-sw-doxygen.web.cern.ch/atlas-sw-doxygen/atlas_main--Doxygen/docs/html/de/dba/classTrig_1_1R3MatchingTool.html), [TDT configuration](https://atlas-sw-doxygen.web.cern.ch/atlas-sw-doxygen/atlas_main--Doxygen/docs/html/df/d1a/namespacepython_1_1TrigDecisionToolConfig.html).
