# xAOD Trigger Decisions, Trigger Names, and Matching

Use this page when a query needs an ATLAS trigger decision, a list of fired trigger names, or matching between a trigger object and an offline object. The examples target `func_adl_servicex_xaodr25` and Release 25 PHYSLITE/PHYS inputs.

## Two different trigger operations

Import the built-in helpers from `func_adl_servicex_xaodr25`:

```python
from func_adl_servicex_xaodr25 import tdt_chain_fired, tmt_match_object
```

- `tdt_chain_fired("HLT_j30_...")` asks the Trigger Decision Tool whether the named chain passed for the current event. The argument is passed to the ATLAS tool, so a valid chain pattern can be used where appropriate.
- `tmt_match_object("HLT_j30_...", jet)` reads precomputed Run 2 `TrigMatch_<chain>` composites through `Trig::MatchFromCompositeTool`. It does not select events by itself; combine it with `tdt_chain_fired` when the event must have fired the chain. In this tool, the optional `dr` argument is ignored: the matching threshold was chosen when the composites were produced. It is not the matcher for Run 3 `HLTNav_Summary` navigation.

The trigger helpers add the required C++ tools and libraries during translation. Do not replace them with an `awkward` operation inside the ServiceX query.

## Identify Run 2 versus Run 3 navigation before matching

The trigger decision is queried the same way in both navigation formats, but the offline-object matcher is different. Inspect the file before writing a matching query. On an authenticated Windows shell, the following checks the first file without delivering events:

```powershell
uvx --from git+https://github.com/ssl-hep/ServiceX_analysis_utils servicex-get-structure `
  "mc23_13p6TeV:mc23_13p6TeV.801166.Py8EG_A14NNPDF23LO_jj_JZ1.deriv.DAOD_PHYSLITE.e8514_e8586_s4618_s4619_r17610_r17609_p7266_tid50426175_00" `
  --filter-branch HLTNav_Summary
```

- If `HLTNav_Summary_*` appears, the file has Run 3 navigation. Use the `Trig::R3MatchingTool` template below.
- `TrigMatch_<chain>` and `AnalysisTrigMatch_<chain>` are Run 2 precomputed matching composites. The built-in `tmt_match_object` reads the `TrigMatch_` prefix. For `AnalysisTrigMatch_`, configure `MatchFromCompositeTool.InputPrefix` as shown below.
- `TrigNavigation` indicates legacy navigation, but by itself does not establish that the precomputed composites needed by `tmt_match_object` exist. Inspect the actual matching containers before using that helper.
- An empty result for `HLTNav_Summary` does not prove Run 2; inspect the other names as well. Authentication is required for this structure query.

The MC23 PHYSLITE validation file used for these examples contains `HLTNav_Summary_DAODSlimmed` and `HLTNav_Summary_DAODSlimmedAux`, so it takes the Run 3 path.

### What PHYS and PHYSLITE retain for Run 3 matching

The [PHYS](https://gitlab.cern.ch/atlas/athena/-/blob/release/25.0.57/PhysicsAnalysis/DerivationFramework/DerivationFrameworkPhys/python/PHYS.py) and [PHYSLITE](https://gitlab.cern.ch/atlas/athena/-/blob/release/25.0.57/PhysicsAnalysis/DerivationFramework/DerivationFrameworkPhys/python/PHYSLITE.py) configurations set `IncludeJetTriggerContent = False` and `IncludeEGammaTriggerContent = False`. Those switches omit the broad signature-specific trigger containers; they do **not** disable trigger decisions or all offline matching. For Run 3, both call `AddRun3TrigNavSlimmingCollectionsToSlimmingHelper`, which registers `HLTNav_Summary_DAODSlimmed` and `HLTNav_RepackedFeatures_Particle` for DAOD output. The latter is a compact `xAOD::ParticleContainer` with trigger-feature four-vectors. See the [navigation slimming configuration](https://gitlab.cern.ch/atlas/athena/-/blob/release/25.0.57/Trigger/TrigAnalysis/TrigNavSlimmingMT/python/TrigNavSlimmingMTConfig.py).

The reduction happens upstream, during AOD-to-DAOD production:

1. [PhysCommonConfig](https://gitlab.cern.ch/atlas/athena/-/blob/release/25.0.57/PhysicsAnalysis/DerivationFramework/DerivationFrameworkPhys/python/PhysCommonConfig.py) passes `TriggerListsHelper.Run3TriggerNames` to `TriggerMatchingCommonRun3Cfg`.
2. [TriggerListsHelper](https://gitlab.cern.ch/atlas/athena/-/blob/release/25.0.57/PhysicsAnalysis/DerivationFramework/DerivationFrameworkPhys/python/TriggerListsHelper.py) assembles that list from selected TriggerAPI categories, including Run 3 jets and electrons, plus [run3ExtraMatchingTriggers.txt](https://gitlab.cern.ch/atlas/athena/-/blob/release/25.0.57/PhysicsAnalysis/DerivationFramework/DerivationFrameworkPhys/data/run3ExtraMatchingTriggers.txt) and `flags.Trigger.derivationsExtraChains`. It is a selection, not every chain in the trigger menu.
3. [TriggerMatchingCommonRun3Cfg](https://gitlab.cern.ch/atlas/athena/-/blob/release/25.0.57/PhysicsAnalysis/DerivationFramework/DerivationFrameworkPhys/python/TriggerMatchingCommonConfig.py) passes the list as `chainsFilter` to `TrigNavSlimmingMTDerivationCfg`. The [slimmer](https://gitlab.cern.ch/atlas/athena/-/blob/release/25.0.57/Trigger/TrigAnalysis/TrigNavSlimmingMT/src/TrigNavSlimmingMTAlg.cxx) resolves those names against the input menu, retains passing branches for selected chains, keeps final features, and repacks their links into the compact container. The decision bits queried by `TrigDecisionTool::isPassed` are separate from this reduced matching navigation.

When PHYSLITE is made from PHYS, `PHYSLITEKernelCfg` skips the AOD-only common augmentations; `TrigNavSlimmingMTDerivationCfg` also skips creation if `HLTNav_Summary_DAODSlimmed` is already in the input. Thus PHYS-to-PHYSLITE production cannot recover a chain's matching branch once PHYS has omitted it. For direct AOD-to-PHYSLITE production, the same common Run 3 chain-selection path runs. AMI identifies `p7266` as Athena 25.0.57, and the MC23 JZ1 PHYSLITE sample used here has **AOD as its immediate parent**: its navigation was slimmed directly from AOD, not inherited from PHYS. The linked files above are from that production release. Check the p-tag and provenance again for other datasets; the file-level checks below establish what a particular DAOD actually contains.

**Decide what is present in a particular file and event:**

| Check | What it establishes |
| --- | --- |
| Chain appears in the menu and `isPassed(chain)` is true | The chain was configured and its event decision passed. This says nothing about retained matching objects. |
| `HLTNav_Summary_DAODSlimmed` and `HLTNav_RepackedFeatures_Particle` exist | The file has the Run 3 DAOD navigation format. This says nothing about a particular chain. |
| The chain's `HLT::Identifier(chain).numeric()` decision ID appears on relevant slimmed navigation nodes | The chain has retained navigation decisions in that event. Multi-leg chains also use leg IDs. A decision ID alone is not proof of a valid particle feature. |
| `TrigDecisionTool::features<xAOD::IParticleContainer>(Trig::FeatureRequestDescriptor(chain))` yields links | Count both valid and invalid links. At least one valid link shows some online particle content survives; mixed valid/invalid results can still make `R3MatchingTool` throw `Bad link info`. Test matching only after checking every returned link. |

Use `HLT::Identifier` and `TrigCompositeUtils::decisionIDs` to inspect stored numeric IDs; do not use Python's `hash()` or assume the readable chain name is stored as a navigation branch. The [slimmer implementation](https://gitlab.cern.ch/atlas/athena/-/blob/release/25.0.57/Trigger/TrigAnalysis/TrigNavSlimmingMT/src/TrigNavSlimmingMTAlg.cxx) creates chain and leg IDs for the filter and intersects them with node IDs. For routine analysis, query valid features through the TDT rather than manually traversing the graph; its feature request handles the chain's navigation and leg structure. Inspect PHYS and PHYSLITE independently if the production route or p-tag is uncertain.

### What `L1RD0_FILLED` means

`RD0` is an L1 random item. The `_FILLED` suffix applies the filled-bunch crossing requirement; it does not mean that the event contains a jet. A chain such as `HLT_j45_L1RD0_FILLED` therefore uses a random filled-bunch L1 seed and applies its jet requirement at HLT. The L1 seed can be prescaled, and the HLT chain can have a separate prescale. The chain name alone does not provide either prescale, so use the trigger menu or prescale metadata when a rate or efficiency needs to be interpreted.

An event-level decision and object matching answer different questions. `tdt_chain_fired` asks whether the trigger decision says that the chain passed. `R3MatchingTool` additionally needs a retained, valid feature link for that chain in the slimmed navigation. Repacking is normal and works for retained features. A passed chain can therefore produce an empty matched offline collection if its branch was filtered out, its final feature was not retained or retrievable, or no offline object passes matching. Inspect the feature links before interpreting an empty match collection; do not infer that the HLT found no jet from that result alone.

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

The Python return annotation and the metadata must describe a collection of strings. Keep the variable/function name `fired_trigger_names` unchanged between the decorator, definition, and query. A raw custom collection cannot be placed directly in a dictionary field. Flatten it with `SelectMany`, then return one scalar string per output row:

```python
trigger_names_query = (
    FuncADLQueryPHYSLITE()
    .SelectMany(lambda e: fired_trigger_names("EF_j.*"))
    .Select(lambda name: {"fired_trigger": name})
)
```

Use `"HLT_j.*"` for current HLT jet chains. The exact available prefix is data-taking-period dependent; discover it from the first file before selecting a chain for a larger query.

## Delivery and returned layout

Use one delivery with `NFiles=1` while developing. The flattened trigger-name query returns one scalar string row per fired trigger, so deduplicate those rows after delivery:

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
names = sorted(set(events["fired_trigger"]))
```

If no chain matches the pattern, `names` is empty. Preserve that result and check the pattern against the trigger naming convention before trying a broader pattern. A large list of strings can stress ROOT output and memory; use a narrower pattern or return booleans for a known chain when possible.

## Run 3 offline-object matching template

For a file with `HLTNav_Summary_*`, define a second callable backed by `Trig::R3MatchingTool`. The public API takes one `xAOD::IParticle`, a chain name, a delta-R threshold, and a `rerun` flag. The template passes `False` for `rerun`, which matches the navigation already stored in the DAOD. Keep this callable separate from `tmt_match_object`; the latter initializes the Run 2 `MatchFromCompositeTool`.

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

The [ATLAS `R3MatchingTool` header](https://atlas-sw-doxygen.web.cern.ch/atlas-sw-doxygen/atlas_main--Doxygen/docs/html/d3/d5f/R3MatchingTool_8h_source.html) documents the single-object overload as `match(recoObject, chain, matchThreshold, rerun)`. If the chain needs trigger re-execution, change the final argument deliberately and document that choice; do not silently use the Run 2 helper on a Run 3 file.

The matching tool owns nested Trigger Decision and scoring tools. Initialize explicit config, TDT, and `Trig::DRScoringTool` handles first, then pass them through `m_r3mt.setProperty("TrigDecisionTool", m_r3TrigDec.getHandle())` and `m_r3mt.setProperty("ScoringTool", m_r3Score.getHandle())` before initializing `m_r3mt`; otherwise the worker cannot retrieve the default nested tools. For Run 3, the TDT also needs `NavigationFormat="TrigComposite"` and the exact `HLTSummary` branch stored by the input derivation. `HLTNav_Summary_DAODSlimmed` is correct for the PHYSLITE/PHYS validation files used here; use the branch discovered with `servicex-get-structure` for another derivation.

These three TDT properties deliberately have different types:

| Property | C++ property type | Value in the template |
| --- | --- | --- |
| `ConfigTool` | `ToolHandle`/`PublicToolHandle<TrigConf::ITrigConfigTool>` | `m_r3TrigConf.getHandle()`; this is the configured tool instance. |
| `TrigDecisionKey` | `SG::ReadHandleKey<xAOD::TrigDecision>` | The StoreGate key string `"xTrigDecision"`. |
| `NavigationFormat` | `Gaudi::Property<std::string>` | The format token `"TrigComposite"`, rather than a tool or data-object name. |
| `HLTSummary` | `SG::ReadHandleKey<TrigCompositeUtils::DecisionContainer>` | The StoreGate key string for the summary container, such as `"HLTNav_Summary_DAODSlimmed"`. |

The two key strings must match the data products in the input file, but they do not need to match the tool name or each other. The [TDT header](https://atlas-sw-doxygen.web.cern.ch/atlas-sw-doxygen/atlas_main--Doxygen/docs/html/d7/df7/TrigDecisionTool_8h_source.html) declares these properties and documents the allowed navigation-format tokens.

### The corresponding Python configuration

In an Athena configuration, Python constructs the same tools and sets their Gaudi properties. It does not replace the C++ initialization in a standalone ServiceX transform: the transform worker must receive equivalent C++ metadata. The ATLAS Python helper chooses the navigation container from input flags; the explicit form below shows the properties that the ServiceX callable must reproduce:

```python
from AthenaConfiguration.ComponentFactory import CompFactory
from TrigDecisionTool.TrigDecisionToolConfig import (
    getRun3NavigationContainerFromInput,
)

tdt = CompFactory.Trig.TrigDecisionTool("TrigDecisionTool")
tdt.TrigConfigSvc = cfgsvc
tdt.NavigationFormat = "TrigComposite"
tdt.HLTSummary = getRun3NavigationContainerFromInput(flags)
acc.addPublicTool(tdt, primary=True)
```

For the DAOD files in the examples, `getRun3NavigationContainerFromInput(flags)` resolves to `HLTNav_Summary_DAODSlimmed`. In the injected C++ template above, this is written explicitly because the ServiceX query does not have Athena `flags`. The [ATLAS Python TDT configuration](https://atlas-sw-doxygen.web.cern.ch/atlas-sw-doxygen/atlas_main--Doxygen/docs/html/d6/da1/namespacepython_1_1TrigDecisionToolConfig.html) and [TDT property declarations](https://atlas-sw-doxygen.web.cern.ch/atlas-sw-doxygen/atlas_main--Doxygen/docs/html/d7/df7/TrigDecisionTool_8h_source.html) are the authoritative references for these settings.

`Trig::R3MatchingTool::initialize()` itself only retrieves its configured decision and scoring tools. It does not infer the navigation format or summary container; those are TDT properties. The [R3 matcher implementation](https://atlas-sw-doxygen.web.cern.ch/atlas-sw-doxygen/atlas_main--Doxygen/docs/html/de/dba/classTrig_1_1R3MatchingTool.html) shows this retrieval sequence. A passed event decision can therefore coexist with zero matched objects when the derivation has no compatible feature links. Its matching path constructs `Trig::FeatureRequestDescriptor frd(chain)` and requests `m_r3TrigDec->features<xAOD::IParticleContainer>(frd)` before comparing objects. Use that exact request in a diagnostic, count valid links, and only then interpret the matching result:

```cpp
Trig::FeatureRequestDescriptor frd(chain);
auto features = m_r3TrigDec->features<xAOD::IParticleContainer>(frd);
const auto n_features = features.size();
const auto n_valid = std::count_if(features.begin(), features.end(),
                                  [](const auto& link) { return link.isValid(); });
// Include <algorithm> when injecting this into a ServiceX query.
```

One local positive control used `HLT_e60_lhvloose_L1eEM26M` on the JZ2 MC23 PHYSLITE file `DAOD_PHYSLITE.50426179._000001.pool.root.1` with AnalysisBase 25.2.80: 14 of 20,000 events passed, each passing event returned one particle feature, and eight events had an offline `AnalysisElectrons` object matched by the same `R3MatchingTool` template. This verifies that the TDT navigation setup and delta-R matching path can work on this PHYSLITE file. The electron control alone does not explain the zero-feature result for the previously tested simple jet chains.

A scan of all fired `HLT_j.*` chains in that same 20,000-event JZ2 file found 254 fired chain names. Of these, 37 returned any particle features and 19 returned at least one valid link. Only two chains had events with **all** returned links valid, and both produced offline `AnalysisJets` matches using `R3MatchingTool` with delta-R threshold 0.2:

| Chain | Fired events | Events with matched offline jets | Matched offline jets |
| --- | ---: | ---: | ---: |
| `HLT_j70_j50a_j0_DJMASS1000j50dphi200x400deta_L1jMJJ-500-NFF` | 50 | 49 | 175 |
| `HLT_j0_HT940_pf_ftf_preselcHT450_L1HT190-jJ40s5pETA21` | 1 | 1 | 15 |

The other 17 chains with some valid links had mixed valid/invalid feature links in every observed event. A direct `R3MatchingTool` call on one such event threw `Bad link info`; the scan skipped matching these mixed-link events, so their zero *tested* matches are not evidence that the offline jets cannot match. For comparison, `HLT_j45_L1RD0_FILLED` fired in 19,282 of these events but returned no particle feature links. These are one-file observations, not guarantees for every p-tag or dataset.

### Repeat the matching inventory on another Run 3 file

The [standalone scan script](../scripts/scan_run3_matching.py) contains the actual `func_adl_callable`/C++ method used for this check. It iterates configured chains matching a narrow pattern, requires each chain's event decision to pass, counts returned and valid `xAOD::IParticleContainer` feature links, and calls `R3MatchingTool::match(*jet, chain, dr, false)` only when **all** returned links are valid. It writes a ROOT result and `trigger_matching_counts.csv` with fired, feature, mixed-link, and matched-event counts. A mixed-link event is recorded separately; the script does not turn the tool's potential `Bad link info` exception into a false negative match.

On Windows, with `atlas_al9` WSL2 and AnalysisBase 25.2.80 installed, run from the marketplace root with a local file and an output directory outside the repository:

```powershell
$script = 'iris-hep/skills/servicex/scripts/scan_run3_matching.py'
$inputFile = 'C:\path\to\DAOD_PHYSLITE.pool.root.1'
$outDir = 'C:\path\to\trigger-scan-output'
uv run --script $script --input $inputFile --out $outDir --release 25.2.80 --pattern 'HLT_j.*'
```

The script's PEP 723 metadata installs `servicex-local==1.2.1`, `func-adl-servicex-xaodr25`, `uproot`, and `awkward`. Match the `xaodr25` query package to a Release 25 executor. For PHYS, add `--data-format phys --jet-key <actual offline jet container>`; inspect the file's StoreGate keys before choosing that key. For another Run 3 navigation output, set `--hlt-summary` to the discovered `HLTNav_Summary_*` name. Narrow `--pattern` to a trigger family when a full menu scan is unnecessary. One input file is intentional: counts are evidence about that file, not a whole dataset.

On an aarch64 WSL installation, ServiceX Local 1.2.1 may compile successfully but its generated `runner.sh` still source `x86_64*/setup.sh`. Follow [the local WSL2 runner fix](servicex-local-wsl2.md): use the request directory printed in the error, change that one generated line to `source aarch64*/setup.sh`, and rerun its `wsl_transform_script.sh`. The output destination is printed in the log and embedded in that request's `kick_off.py`. Then run `uv run --script $script --read-root <produced-ROOT-path> --out $outDir` to write the same CSV without submitting another transform. Keep the generated log, request ID, and output ROOT file when reporting a result.

### Repeat the inventory on Run 2 precomputed matching

Check the first file for `TrigMatch_*` and `AnalysisTrigMatch_*` branches with `servicex-get-structure --filter-branch` (use each prefix separately). The chain names are the suffixes of the **non-Aux** `TrigMatch_<chain>` or `AnalysisTrigMatch_<chain>` container names. This identifies which precomputed matching containers were written; a trigger decision alone does not. Inspect `TrigNavigation` separately, since that legacy navigation container does not imply that either precomputed matching prefix exists.

For a `TrigMatch_<chain>` container, use the built-in [`tmt_match_object` helper](https://github.com/iris-hep/func-adl-types-atlas/blob/main/metadata/trigger.py) on that **known chain**. Its underlying [ATLAS `MatchFromCompositeTool`](https://gitlab.cern.ch/atlas/athena/-/blob/release/25.0.57/Trigger/TrigAnalysis/TriggerMatchingTool/Root/MatchFromCompositeTool.cxx) retrieves `InputPrefix + chain`, where `InputPrefix` defaults to `TrigMatch_`. The helper's `dr` argument has no effect on this precomputed result; use the derivation configuration to find the threshold applied upstream.

```python
from func_adl_servicex_xaodr25 import FuncADLQueryPHYS, tdt_chain_fired, tmt_match_object

chain = "HLT_j..."  # A suffix found under TrigMatch_ in this file.
query = (FuncADLQueryPHYS()
    .Select(lambda event: {"jets": event.Jets(calibrate=False)})
    .Where(lambda collections: tdt_chain_fired(chain))
    .Select(lambda collections: {
        "all_jet_pt_GeV": collections.jets.Select(lambda jet: jet.pt() / 1000.0),
        "matched_jet_pt_GeV": collections.jets
            .Where(lambda jet: tmt_match_object(chain, jet))
            .Select(lambda jet: jet.pt() / 1000.0),
    })
)
```

Use `FuncADLQueryPHYSLITE()` and its offline jet collection for PHYSLITE. Deliver this query with `NFiles=1` for each candidate chain and count passing events, events with matched jets, and matched jets from the returned jagged arrays:

```python
import awkward as ak
from servicex import Sample, ServiceXSpec, dataset, deliver
from servicex_analysis_utils import to_awk

sample = Sample(Name="run2_match", Dataset=dataset.Rucio(dataset_name), NFiles=1, Query=query)
rows = to_awk(deliver(ServiceXSpec(Sample=[sample])))["run2_match"]
matched_per_event = ak.num(rows["matched_jet_pt_GeV"])
print({
    "passing_events": len(rows),
    "events_with_matched_jets": int(ak.sum(matched_per_event > 0)),
    "matched_jets": int(ak.sum(matched_per_event)),
})
```

If there are many candidate chains, narrow the branch-name prefix first; do not submit every configured menu chain.

For `AnalysisTrigMatch_<chain>`, the built-in helper's `TrigMatch_` prefix is wrong. Configure a `Trig::MatchFromCompositeTool` with `InputPrefix="AnalysisTrigMatch_"` and call it instead:

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

# In the query above, replace tmt_match_object(chain, jet) with
# analysis_match_object(chain, jet).
```

This Run 2 prefix override follows the tool's `InputPrefix` property. It compiled and initialized under AnalysisBase 25.2.80 in a zero-event smoke run, but has **not** been tested on a Run 2 file or matching composite. Test a one-file transform with real Run 2 data before treating its counts as validated. If the file has only `TrigNavigation` and no precomputed composites, this recipe does not apply: select a legacy-navigation matching tool appropriate to that release rather than calling `MatchFromCompositeTool`.

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
trigger_names_query = (
    base_query
    .SelectMany(lambda e: fired_trigger_names("EF_j.*"))
    .Select(lambda name: {"fired_trigger": name})
)
# Change only the pattern to "HLT_j.*" for HLT jet chains.
events = to_awk(deliver(ServiceXSpec(Sample=[Sample(
    Name="jet_trigger_names", Dataset=dataset.Rucio(dataset_name),
    NFiles=1, Query=trigger_names_query
)])))["jet_trigger_names"]
fired_jet_chains = sorted(set(events["fired_trigger"]))
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

First require the chain to have fired. Then return both all offline jets and the matched subset from those same events. The Run 3 matcher uses the requested delta-R cone; the Run 2 precomputed matcher uses the criterion fixed when its composites were produced. Choose the matcher from the navigation check above:

```python
chain = "HLT_j30_momemfrac006_L1jJ160"
matching_query = (base_query
    .Where(lambda e: tdt_chain_fired(chain))
    .Select(lambda e: {"jets": e.Jets()})
    .Select(lambda c: {
        "all_jet_pt": c.jets.Select(lambda j: j.pt() / 1000.0),
        "matched_jet_pt": c.jets
            .Where(lambda j: tmt_match_object(chain, j))
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

For Run 3, replace only the matcher call in the query with the custom callable above:

```python
matching_query = (base_query
    .Where(lambda e: tdt_chain_fired(chain))
    .Select(lambda e: {"jets": e.Jets()})
    .Select(lambda c: {
        "all_jet_pt": c.jets.Select(lambda j: j.pt() / 1000.0),
        "matched_jet_pt": c.jets
            .Where(lambda j: r3_match_object(chain, j, 0.2))
            .Select(lambda j: j.pt() / 1000.0),
    })
)
```

Do not include both matcher tools in one query while debugging navigation-format problems. Keep the event decision as `tdt_chain_fired(chain)` in either version.

Fill two histograms with the same GeV axis and overlay them. `matched_pt` may be empty even when the event fired; that is a valid matching result, not an instruction to substitute all jets. A zero-jet event contributes no entries to either flattened array.

For the MC23 PHYSLITE validation file described above, `HLT_j260_L1jJ125` fired in one selected event and `HLT_j45_L1RD0_FILLED` fired in 15,751 events, but the Run 3 matcher returned zero matched offline jets for both chains. Widening the matching cone from 0.2 to 0.7 did not change that result. This means the decision and matching queries are separate measurements; inspect the stored navigation and chain features before interpreting an empty matched collection as a physics conclusion.

The same check on the corresponding PHYS JZ1 and JZ3 samples used `FuncADLQueryPHYS` with `e.Jets(calibrate=False)`. The default calibrated `e.Jets()` form failed remotely before delivering events; record the ServiceX request ID and obtain the worker log before diagnosing that as a query or trigger failure. With `calibrate=False`, the Run 3 matcher completed successfully and returned zero matched jets for `HLT_j45_L1RD0_FILLED` (15,754 passing events, 156,760 offline jets) and `HLT_j260_L1jJ125` (14,331 passing events, 154,128 offline jets).

For a higher-slice stress test, the JZ4 PHYSLITE file `mc23_13p6TeV:mc23_13p6TeV.801169.Py8EG_A14NNPDF23LO_jj_JZ4.deriv.DAOD_PHYSLITE.e8514_e8586_s4618_s4619_r17610_r17609_p7266_tid50426195_00` had `HLT_j260_L1jJ125` passing in 59,935 of 60,000 examined events (99.89%). With the explicit Run 3 navigation properties above, the successful matching delivery contained 658,848 offline jets, zero matched jets, and zero `features<xAOD::IParticleContainer>("HLT_j260_L1jJ125")` entries in every selected event. A high trigger pass fraction therefore does not by itself prove that the derivation retained usable offline-to-trigger links.

## Dependencies and checks

For a standalone script, list `func_adl_servicex_xaodr25`, `servicex`, `servicex-analysis-utils`, `awkward`, `numpy`, and the plotting package in its PEP 723 dependency block. Keep `NFiles=1` until the query translates and the returned fields have been inspected. Check the generated C++ when introducing the name-list callable: it must contain the Trigger Decision Tool initialization, `getListOfTriggers`, and `isPassed(..., TrigDefs::Physics)`. If a transform fails after translation and the ServiceX logs are needed, follow the normal `HELP USER` path from the main ServiceX skill.

For a disposable Windows smoke test, put the query in a temporary Python file and run it with the matching release package isolated by `uvx`:

```powershell
uvx --with func-adl-servicex-xaodr25 --with servicex --with servicex-analysis-utils --with awkward python .\trigger_test.py --mode discover
```

Use `func_adl_servicex_xaodr21` in the command instead when the target backend is Release 21. The query package and ServiceX xAOD executor must use the same release suffix.
