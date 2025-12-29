# ServiceX FuncADL xAOD Code Snippets

Use ServiceX to fetch data from `rucio` datasets on the GRID, skimming out only the data required from the events needed.

Best practice (details below):

1. Define your `base_query`
2. Select the collections you need (jets, electrons)

    - This should be a top level `Select`
    - Select all the collections you need - do not make separate queries.
    - Include singletons (like met or EventInfo) - you have to extract them at this level to use later.
    - Apply selections at the object level if need be (using a nested `.Where`). This is important as it can dramatically reduce the amount of data that needs to be shipped out of ServiceX.
    - Do not select the columns (like pt, eta, etc.) at this stage. Do that at the next stage.

3. Apply any event level selections needed

    - Use a top level `.Where` to do this.
    - For example, only events with at least 2 jets.
    - This is important as it can dramatically reduce the amount of data that needs to be shipped out of ServiceX.
    - You can't go back to the root event object from step 2 here - you can only reference what you defined in step 2.

4. Select the items from the collections that need to be sent to the client. The jet pT or eta, MET.

    - At this point the `Select` statement is over the dictionary of collections you built in step 2.
    - And scale to the proper units (GeV, etc.).
    - The final `Select` must be a single outer level `Select` with a dictionary as its result.

5. Execute the query to fetch the data.

Notes:

- Quantities returned from servicex should be in units most people use at the LHC - GeV, meters, etc. Please convert from whatever the units of the input files are in.
- NEVER nest a dictionary inside another dictionary. That will for sure cause a servicex crash.

## A Simple Full Example

This example fetches the jet $p_T$'s from a PHYSLITE formatted xAOD data sample stored by `rucio`.

```python
from func_adl_servicex_xaodr25 import FuncADLQueryPHYSLITE
from servicex import deliver, ServiceXSpec, Sample, dataset

# The base query should run against PHYSLITE.
base_query = FuncADLQueryPHYSLITE()

# Query: get all jet pT
jet_pts_query = (base_query
    .Select(lambda evt: {"jets": evt.Jets()})
    .Select(lambda collections: collections.jets.Select(lambda jet:
    {
        "jet_pt": jet.pt() / 1000.0,
    })
)

# Do the fetch
# Define the rucio dataset identifier (DID).
ds_name = ("mc23_13p6TeV:mc23_13p6TeV.801167.Py8EG_A14NNPDF23LO_jj_JZ2.deriv.DAOD_PHYSLITE.e8514_e8528_a911_s4114_r15224_r15225_p6697")

all_jet_pts_delivered = deliver(
    ServiceXSpec(
        Sample=[
            Sample(
                Name="jet_pt_fetch",
                Dataset=dataset.Rucio(ds_name),
                NFiles=1,
                Query=jet_pts_query,
            )
        ]
    ),
)
```

- `all_jet_pts_delivered` is a dictionary indexed by sample name. It contains a list of paths to ROOT files (in the form of a `GuardList`). For `NFiles=1`, there will be only a single file.
  - If it makes sense in the code, add a command line option, or a default option to the function you are working on to change NFiles (e.g. `--n-files` with alias `-n`). It should default to 1, and `None` would be all files in the dataset. For the command line, `0` would represent all files. The user may already have some code that deals with this - in which case use that infrastructure.

## The `deliver` function

- Default to `NFiles=1` because large datasets can take a lot of time. While adding a command line option to change it is fine, defaulting to the full dataset is not - until the user has done sufficient testing.
- The query can be re-used.
- Use `dataset.Rucio` for a `rucio` dataset, use `dataset.FileList` for a list of web accessible datasets (via `https` or `xrootd://`)
- Only call deliver once - make sure all the data you want is in the query, even if multiple samples - just add more to the `Sample` array.

There are two ways to access the output of the `deliver` function.

1. If the output is small enough you expect to be able to run in-memory. For quick studies, etc., this works very well and is quite easy.

  a. Make sure the `servicex_analysis_utilities` package is included in the project's dependencies.
  b. The following code will turn the output above into a single awkward array:

  ```python
  from servicex_analysis_utils import to_awk

  all_jets_pts_awk = to_awk(all_jet_pts_delivered)
  jet_pts = all_jets_pts_awk["jet_pt_fetch"]
  ```

1. Use the ROOT files directly. These can be used with RDataFrame or `uproot`. If you have to deal with a very large amount of data that won't fit in memory, this is the proper approach.

    a. The following code gets a list of all the ROOT files (if `NFiles==1` then there will be only one).

    ```python
    file_list = [str(p) for p in all_jet_pts_delivered['jet_pt_fetch']
    ```

## Base Query

Queries have to start from a base, like `FuncADLQueryPHYSLITE`.

- Assume all queries are on Release 25 datasets (the `func_adl_servicex_xaodr25` package)
- Use `FuncADLQueryPHYSLITE` for ATLAS PHYSLITE samples - that have already had calibrations, etc., applied.
- Use `FuncADLQueryPHYS` for ATLAS PHYS or other derivations (like LLP1, etc.). These aren't calibrated, so this will try to run calibrations.

The `base_query` is a sequence of events. Each event contains collections of objects like Jets and Electrons. `evt.Jets()` gets you the collection of jets for a particular event. You can pass `calibrated=False` to prevent calibration in `PHYS`, but note that `PHYSLITE` does not have uncalibrated jets (or other objects) in it! This `func_adl` language is based on LINQ.

`ServiceX` queries can not contain references to `awkward` functions. Instead, use `Select`, `Where`, to effect the same operations.

To tell what kind of data you are looking at, scan the name of the dataset:

- If it has PHYSLITE in it, it is PHYSLITE.
- If it has DAOD_PHYS in it, it is PHYS.
- If it is OpenData, then it is PHYSLITE. It usually has OpenData in the name somewhere. There are a few differences in how you code against OpenData - look carefully at the instructions.

## Filtering in a Query

Use the `Where` operator to filter objects by a condition, and replace the above nested `Select` (the `jets.Select(lambda jet:`) with a `.Where(lambda jet: jet.pt()/1000.0 > 200.)`. You can have a complex expression and can use `and` and `or` from python operators. You can also have a sequence of `.Where` statements chained.

You can also filter events by putting a `.Where` at the top level. Here is an example that looks for at least 2 jets with a pT cut:

```python
query = (FuncADLQueryPHYSLITE()
    .Where(lambda e: e.Jets()
                      .Where(lambda j: j.pt() / 1000.0 > 30.0)
                      .Count() >= 2)
    .Select(lambda e: {'NumJets': e.Jets().Count()})
)
```

## Multiple Object Collections

FuncADL queries can return multiple collections simultaneously (e.g. electrons and muons). The best practice it to chain two top level `Select` statements. The first selects the required collections and applies any top level selections to those object. The second builds the return data and any necessary calculations.

```python
query = (FuncADLQueryPHYSLITE()
    .Select(lambda e: {
        'ele': e.Electrons().Select(lambda e: e.pt()/1000 > 30), 
        'mu': e.Muons().Select(lambda m: abs(m.eta()) < 2.5)
    }))
    .Select(lambda pairs: {
        'ele_pt':  pairs.ele.Select(lambda ele: ele.pt()/1000),
        'ele_eta': pairs.ele.Select(lambda ele: ele.eta())
        'mu_pt': pairs.mu.Select(lambda mu: mu.pt()/1000),
        'mu_eta': pairs.mu.Select(lambda mu: mu.eta())
    })
```

Note:

- Any collations or items you want to access in the second select statement must be passed through from the first.

## Errors

If you encounter an error after running, there are two types. The first give you type errors, and those you can solve just by reading the error message carefully and perhaps not doing whatever the code complained about. You might have to look carefully for this message - for example "Method xxx not found on object."

The second type of error there isn't much you can do to get more information, however. You'll find an error that looks like "Transform "xxx" completed with failures." And something in `stdout` about clicking on `HERE` to get more information. Sadly, only the requester can do that. If that happens just reply with "HELP USER" and that will be a signal. Note that you might get an error as mentioned above and this - in which case try to solve the error before getting the user involved. A common case here is you request some data that should be in the datafiles, but is not.
