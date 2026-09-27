# Select data triggers and query prescales

Use when choosing chains or asking which triggers are unprescaled. A chain name or event-pass count cannot answer this. Prescales vary across runs and luminosity blocks.

1. Establish the data-taking period, analysis Good Runs List (GRL), object signature, and offline selection.
2. Consult the current ATLAS recommendations below; follow the relevant signature-group links for thresholds and turn-ons.
3. Query menu/prescale metadata for that scope. Report the period/GRL used; do not present a permanent list valid for all Run 2 or Run 3 data.

## Authoritative references

- [Lowest unprescaled triggers](https://twiki.cern.ch/twiki/bin/viewauth/Atlas/LowestUnprescaled): year/period tables and configuration browsers.
- Recommendations: [Run 2](https://twiki.cern.ch/twiki/bin/viewauth/Atlas/TriggerRecommendationsForAnalysisGroupsFullRun2), [Run 3](https://twiki.cern.ch/twiki/bin/viewauth/Atlas/Run3TriggerRecommendations).
- GRLs: [Run 2](https://twiki.cern.ch/twiki/bin/view/AtlasProtected/GoodRunListsForAnalysisRun2), [Run 3](https://twiki.cern.ch/twiki/bin/view/AtlasProtected/GoodRunListsForAnalysisRun3).
- TriggerAPI: [software guide](https://atlas-software.docs.cern.ch/athena/trigger/analysis/menutriggerapi/), [ATLAS documentation](https://twiki.cern.ch/twiki/bin/viewauth/Atlas/TriggerAPI).

ATLAS pages may require authentication. Look up signature-specific recommendations when needed rather than copying thresholds or chain lists into this skill.

## TriggerAPI workflow

TriggerAPI runs in an Athena environment providing `TriggerMenuMT.TriggerAPI`; it is separate from the ServiceX query environment. Use the release/setup recommended by the current software guide. Check `tapis --help` in that release before using the CLI.

For the session interface, supply the analysis GRL and a supported `TriggerType`:

```python
from TriggerMenuMT.TriggerAPI import TriggerAPISession, TriggerType

print([item.name for item in TriggerType])
session = TriggerAPISession("path/to/grl.xml")
```

Choose `trigger_type` from the printed categories to match the requested signature, then query:

```python
chains = session.getLowestUnprescaled(triggerType=trigger_type)
by_run = session.getLowestUnprescaledByRun(triggerType=trigger_type)
live_fractions = session.getLiveFractions(triggerType=trigger_type)
session.save("trigger-api-session.json")
```

Whole-GRL chain results are sets; the per-run result is keyed by run. Reload saved metadata with `TriggerAPISession(json="trigger-api-session.json")`. Check the installed API documentation for run-range filters and other inputs.

The older `TriggerAPI.getLowestUnprescaled(TriggerPeriod..., TriggerType...)` interface uses predefined periods. Follow the documentation for the installed release and target period; do not mix legacy and session-interface examples.

These examples are documentation guidance, not a live query result. Prescale-weighted live fractions are approximate selection aids, not an official luminosity calculation. A menu-only session describes menu intent rather than measured data-taking history. TriggerAPI does not establish which object-matching features survive in a DAOD; use the [matching format guide](datamodel-xaod-triggers.md#before-object-matching) for that.
