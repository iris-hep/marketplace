# Plot ETmiss for Open Data dataset

Plot the missing transverse energy (ETmiss) distribution for all events in the specified Open Data dataset.

## Data Samples

| Data Sample | Derivation | Role(s) In Analysis |
| --- | --- | --- |
| user.zmarshal:user.zmarshal.364702_OpenData_v1_p6026_2024-04-23 | PHYSLITE | Data |

## Histograms

1. ETmiss
    * x Axis
        * Missing transverse energy magnitude for each event.
        * `$E_T^{miss}$ [GeV]`
        * Default binning: 0 to 500 GeV in 50 bins.
        * One entry per event.

## Analysis Steps

1. Event selection
    * No selection; include all events.
1. ETmiss
    * Read event-level missing transverse energy.

## Workflow

1. Data Extraction and NTuple Skimming
    * Filtering: No Filtering.
    * Variables: event-level ETmiss (magnitude) and any required metadata for dataset bookkeeping.
2. Data Analysis & Histogramming
    * Fill ETmiss histogram with one entry per event.

## Statistical Analysis

None.

## Tools

* servicex
  * Use func_adl to access the specified dataset and retrieve ETmiss.
* awkward
  * Event-level array handling.
* hist
  * Fill and store histogram as PNG.
* vector
  * Not required unless ETmiss needs vector construction; only use if needed.

# Trijet Top Candidate pT and Max b-tag in Closest-mass Trijet

Select events with at least three jets and, per event, build all trijet combinations to find the one with invariant mass closest to 172.5 GeV. Plot the trijet pT and the maximum b-tagging discriminant among the jets in that trijet.

## Data Samples

| Data Sample | Derivation | Role(s) In Analysis |
| --- | --- | --- |
| opendata:mc20_13TeV.410471.PhPy8EG_A14_ttbar_hdamp258p75_allhad.deriv.DAOD_PHYSLITE.e6337_s3681_r13167_p6026 | PHYSLITE | Signal (ttbar all-hadronic) |

## Histograms

1. Trijet pT (closest-mass trijet)
    * x Axis
        * Transverse momentum of the trijet four-momentum whose invariant mass is closest to 172.5 GeV in each event.
        * `$p_T^{3j}$ [GeV]`
        * Binning: 50 bins, 0 to 500 GeV.
        * One entry per event (if at least one trijet exists).
2. Max b-tag discriminant in closest-mass trijet
    * x Axis
        * Maximum b-tagging discriminant value among the three jets in the selected trijet.
        * `max b-tag discriminant`
        * Binning: 50 bins, 0 to 1 (normalized discriminant).
        * One entry per event (if at least one trijet exists).

## Analysis Steps

1. Event and jet selection
    * Require at least three jets passing baseline selection.
    * Use jets with pT > 25 GeV and |eta| < 2.5.
2. Build trijet combinations
    * For each event, build all 3-jet combinations and compute their invariant mass and trijet four-momentum.
3. Closest-mass trijet selection
    * Select the trijet with invariant mass closest to 172.5 GeV.
4. Derived quantities
    * Trijet pT from the selected trijet four-momentum.
    * Max b-tag discriminant from the three jets in the selected trijet.

## Workflow

1. Data Extraction and NTuple Skimming
    * Filtering: keep only events with at least three jets passing baseline selection.
    * Variables: jet pt, eta, phi, mass, and b-tag discriminant (exact field name to be specified).
2. Data Analysis & Histogramming
    * Build trijet combinations, compute mass and pT, select closest to 172.5 GeV.
    * Compute max b-tag discriminant in the selected trijet.
    * Fill the two histograms with one entry per selected event.

## Statistical Analysis

None.

## Tools

* servicex (func_adl)
  * Extract PHYSLITE jets and apply event/jet filtering.
* awkward
  * Build combinations and select closest-mass trijet.
* vector
  * Compute trijet four-momenta, mass, and pT.
* hist
  * Fill and save histograms as PNG.

# Reconstructed $t\bar{t}$ Mass Near 3 TeV (Single-Lepton Channel)

Plot the reconstructed $t\bar{t}$ invariant mass near 3 TeV in single-lepton events from the specified Rucio dataset.

## Data Samples

| Data Sample | Derivation | Role(s) In Analysis |
| --- | --- | --- |
| user.zmarshal:user.zmarshal.301333_OpenData_v1_p6026_2024-04-23 | PHYSLITE | Data (signal region) |

## Histograms

1. Reconstructed $m_{t\bar{t}}$ (single-lepton)
    * x Axis
        * Reconstructed invariant mass of the $t\bar{t}$ system in the single-lepton channel, using one leptonic top and one hadronic top reconstruction.
        * `$m_{t\bar{t}}$ [GeV]`
        * Proposed range 2000-4000 GeV with 40-80 bins (adjustable).
        * One entry per selected event (best combination per event).

## Analysis Steps

1. Event Selection
    * Exactly one isolated charged lepton (electron or muon).
    * Missing transverse momentum consistent with leptonic $W$ decay.
    * At least 4 jets, with at least 2 b-tagged jets (working point TBD).
2. Object Definitions
    * Identify jets, b-tagged jets, leptons, and missing transverse momentum (MET).
3. Leptonic Top Reconstruction
    * Use lepton + MET to reconstruct $W \to \ell\nu$ (solve neutrino $p_z$ with $m_W$ constraint).
    * Combine leptonic $W$ with a b-tagged jet to form leptonic top candidate.
4. Hadronic Top Reconstruction
    * From remaining jets, choose a b-tagged jet + two non-b jets to form hadronic top candidate.
5. Combination Choice
    * Select the combination minimizing a chi2-like metric (e.g., deviations from $m_W$ and $m_t$).
6. $t\bar{t}$ Mass
    * Combine leptonic and hadronic top four-vectors to form $m_{t\bar{t}}$.

## Workflow

1. Data Extraction and NTuple Skimming
    * Filtering: Require at least 1 lepton and at least 4 jets at the source if possible.
    * Variables: lepton 4-vectors and IDs, jet 4-vectors, b-tag flags, MET and MET phi, event weights if any, run/lumi/event identifiers.
2. Data Analysis & Histogramming
    * Build leptonic and hadronic top candidates per event as described.
    * Apply single-lepton and jet/b-jet selections.
    * Fill the $m_{t\bar{t}}$ histogram with the best combination per event.

## Statistical Analysis

No statistical analysis required beyond the histogram.

## Tools

* servicex (func_adl)
  * Query and skim the PHYSLITE dataset from Rucio.
* awkward
  * Event-level selection, combinatorics, and array operations.
* vector
  * Four-vector reconstruction and invariant mass calculations.
* hist
  * Histogramming and PNG output.
