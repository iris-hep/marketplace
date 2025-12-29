# xAOD Event and Sample Weights

Unless otherwise requested by the user, use the following guidelines to determine how to do event weighting:

- **Single MC or Data Dataset**: Apply only the MC event weight.
- **Multiple MC Datasets**: Apply the MC event weight and the cross section scaling. If the cross section values aren't available for any one sample, then don't apply it for any samples (and make sure to tell the user in the notes you are missing that information). The normal way to plot this is with a stacked histogram.
- **MC and Data**: Apply the MC event weights and the cross section, and scale to the integrated luminosity of the data. The normal way to plot this is to use a stacked histogram and the data as filled black circles.

Always make sure to tell the user what event weights you are applying. If the above guidance tells you to apply event weights but you don't know how, warn the user.

If any calculations are required (e.g. cross section times integrated luminosity, etc), do them in the code so the user can update things as they wish.

It is not uncommon for a user to ask for a MC sample to be scaled by x10 or similar. Make sure to put the scale factor in the legend entry for that sample.

## MC Event Weight

This is encoded on the `EventInfo` object (there is only one), and it is the first `mcEventWeight`:

```python
query = (FuncADLQueryPHYSLITE()
    .Select(lambda e: e.EventInfo("EventInfo").mcEventWeight(0))
```

## Data

When including data we need to calculate the luminosity of the data we are including and rescale any MC to that. The proper way is not current available in this system. For now, scale the luminosity for a particular run by the number of events you are looking at (you'll have to count the number of events).

The dataset will contain a tag detailing which run you are looking at. We are using an estimate of the number of events - 10^9 per year.

Dataset | Number of Events | Total Luminosity |
| --- | --- | --- |
| data24_13p6TeV | 200000000000000 | 52.4 femto-barns^-1 |
| data22_13p6TeV | 200000000000000 | 52.4 femto-barns^-1 |
| data23_13p6TeV | 200000000000000 | 52.4 femto-barns^-1 |
| data24_13p6TeV | 200000000000000 | 52.4 femto-barns^-1 |
| data25_13p6TeV | 150000000000000 | 39.3 femto-barns^-1 |

## Cross-section Scaling and MC

Each event in a sample is scaled by a constant scale factor:

`sf = L * sigma / N_S`

- `L` - the target integrated luminosity for the plot. Use 1 femto-barn-1 by default.
- `sigma` the cross section of the sample - see below. Doublecheck the units of these numbers.
- `N_S` sum of all the per-event weights (the `mcEventWeight(0)` above). This must be taken as the sum over all events in the file - before any cuts. Gather the `mcEventWeight(0)` for all events in the file.

The cross-section table is below, organized by run number and name. Every ATLAS sample is unique by run number, which is in the name of the dataset. For example, "mc23_13p6TeV:mc23_13p6TeV.801167.Py8EG_A14NNPDF23LO_jj_JZ2.deriv.DAOD_PHYSLITE.e8514_e8528_a911_s4114_r15224_r15225_p6697" is an MC dataset with run number 801167 and name Py8EG_A14NNPDF23LO_jj_JZ2 (or JZ2). Data leads with "data..." in the name.

Run Number | Name | Cross Section
--- | --- | ---
801167/364702 | Py8EG_A14NNPDF23LO_jj_JZ2 | 2582600000.0 pico-barn
801168/364703 | Py8EG_A14NNPDF23LO_jj_JZ3 | 28528000.0 pico-barn
513109/700325 | MGPy8EG_Zmumu_FxFx3jHT2bias_SW_CFilterBVeto | 2.39 nano-barn
601237/410471 | PhPy8EG_A14_ttbar_hdamp258p75_allhad | 812 pico-barn
701005/700588 | Sh_2214_lllvjj | 53.1 femto-barn

Make sure to do all calculations in the code; don't do the math in your head. The user may well want to take the code and change some of the parameters.

## Event Scaling and Information on the Plot

When applying this scaling, detail what you are doing in some detail in the notes. On the plot, only put the integrated luminosity you rescaled the MC to (`L=xx fb^-1`). Do not mention what scaling was applied, etc., on the plot itself. We want as little possible to detract from the display of the data. If you aren't doing the luminosity rescaling, don't put anything on the plot.
