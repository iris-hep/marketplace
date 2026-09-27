# xAOD trigger decisions and routing

Use with `func_adl_servicex_xaodr25` and a Release 25 executor. Choose the operation first:

| User needs | Read |
| --- | --- |
| Filter events or return a trigger-pass boolean | This page |
| Discover fired chain names in a file | [Trigger names](datamodel-xaod-trigger-names.md) |
| Match offline objects using precomputed composites | [Run 2 matching](datamodel-xaod-trigger-matching-run2.md) |
| Match offline objects using `HLTNav_Summary_*` | [Run 3 matching](datamodel-xaod-trigger-matching-run3.md) |
| Choose data triggers or find unprescaled chains | [Trigger selection and TriggerAPI](datamodel-xaod-trigger-selection.md) |

Read only the page for the requested operation. A passed event decision does not prove an offline-object match or an unprescaled chain.

## Event decisions

Use `tdt_chain_fired` inside a ServiceX query. Supply `chain` from the user's request or a verified menu; do not invent a chain. These examples assume that variable is already defined.

```python
from func_adl_servicex_xaodr25 import FuncADLQueryPHYSLITE, tdt_chain_fired

base_query = FuncADLQueryPHYSLITE()
selected_query = (
    base_query
    .Where(lambda event: tdt_chain_fired(chain))
    .Select(lambda event: {"fired": True})
)
```

For PHYS, use `FuncADLQueryPHYS`. Add the required offline collections and output columns using the normal [query and delivery patterns](servicex-hints.md).

To measure a pass fraction, return one boolean for every examined event; do not filter first:

```python
frequency_query = base_query.Select(
    lambda event: {"fired": tdt_chain_fired(chain)}
)
```

After delivery, divide the number of true values by the number of rows. Report both counts and handle zero rows. A fraction from one file is not a dataset-wide rate.

For an OR of known chains, use an explicit expression:

```python
or_query = base_query.Where(
    lambda event: tdt_chain_fired(chain_a) or tdt_chain_fired(chain_b)
)
```

## Before object matching

Inspect actual containers with `checkxAOD.py input.pool.root`, or an authenticated `servicex-get-structure "<Rucio DID>" --filter-branch <prefix>` call. Check each relevant prefix; no result for one prefix is not proof of another format.

| Stored content | Matching choice |
| --- | --- |
| `HLTNav_Summary_*` | Run 3 page; use the exact summary key |
| `TrigMatch_<chain>` | Run 2 page; built-in `tmt_match_object` |
| `AnalysisTrigMatch_<chain>` | Run 2 page; explicit prefix override |
| Only `TrigNavigation` | Legacy navigation matcher required; precomputed-composite recipes do not apply |

Choose from stored navigation/composites, not the campaign name or AnalysisBase version. If several formats coexist, inspect the chain's available content before choosing.

Validate with `NFiles=1` and inspect returned fields. Keep event decisions and object matches separate; an empty matched collection must remain empty.
