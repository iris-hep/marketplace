# Analysis Spec Builder Examples

The first examples show intentionally small analysis requests. The final example shows how to reconstruct a published analysis while keeping source-derived content separate from a user-requested methodological change.

# Example 1: Plot ETmiss for Open Data dataset

Plot the missing transverse energy (ETmiss) distribution for all events in the specified Open Data dataset.

## Data Samples

| Data Sample | Role(s) In Analysis |
| --- | --- |
| W+Jets Dataset | Data |

## Backgrounds

None required for this plotting task.

## Data Required

W+Jets Dataset

* Missing ET

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
2. ETmiss
    * Read event-level missing transverse energy.

## Workflow

1. Data Extraction and NTuple Skimming
    * Filtering: No filtering.
    * Variables: event-level ETmiss magnitude and any required metadata for dataset bookkeeping.
2. Data Analysis & Histogramming
    * Fill ETmiss histogram with one entry per event.

## Statistical Analysis

None.

# Example 2: Trijet Top Candidate pT and Max b-tag in Closest-mass Trijet

Select events with at least three jets and, per event, build all trijet combinations to find the one with invariant mass closest to 172.5 GeV. Plot the trijet pT and the maximum b-tagging discriminant among the jets in that trijet.

## Data Samples

| Data Sample | Role(s) In Analysis |
| --- | --- |
| PHYSLITE | Signal (ttbar all-hadronic) |

## Backgrounds

Not required for this object-reconstruction exercise.

## Data Required

PHYSLITE

* Jet pt, eta, phi, and mass.
* Jet b-tagging discriminant.

## Histograms

1. Trijet pT (closest-mass trijet)
    * x Axis
        * Transverse momentum of the trijet four-momentum whose invariant mass is closest to 172.5 GeV in each event.
        * `$p_T^{3j}$ [GeV]`
        * Binning: 50 bins, 0 to 500 GeV.
        * One entry per event if at least one trijet exists.
2. Max b-tag discriminant in closest-mass trijet
    * x Axis
        * Maximum b-tagging discriminant value among the three jets in the selected trijet.
        * `max b-tag discriminant`
        * Binning: 50 bins, 0 to 1 for a normalized discriminant.
        * One entry per event if at least one trijet exists.

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
    * Maximum b-tag discriminant among the three selected jets.

## Workflow

1. Data Extraction and NTuple Skimming
    * Filtering: keep only events with at least three jets passing baseline selection when possible.
    * Variables: jet pt, eta, phi, mass, and b-tag discriminant. The exact field name is an implementation detail unless specified by the user.
2. Data Analysis & Histogramming
    * Build trijet combinations, compute mass and pT, and select the combination closest to 172.5 GeV.
    * Compute the maximum b-tag discriminant in the selected trijet.
    * Fill the two histograms with one entry per selected event.

## Statistical Analysis

None.

# Example 3: Reconstructed ttbar Mass Near 3 TeV (Single-Lepton Channel)

Plot the reconstructed ttbar invariant mass near 3 TeV in single-lepton events from the specified Rucio dataset.

## Data Samples

| Data Sample | Role(s) In Analysis |
| --- | --- |
| user.zmarshal:user.zmarshal.301333_OpenData_v1_p6026_2024-04-23 | Data (signal region) |

## Backgrounds

The request does not specify a background estimate. Do not invent one for this reconstruction-and-plotting task.

## Data Required

* Lepton four-vectors and identification/isolation information.
* Jet four-vectors and b-tagging information.
* Missing transverse momentum magnitude and phi.
* Event weights if present.
* Run/luminosity/event identifiers for bookkeeping.

## Histograms

1. Reconstructed `m_ttbar` (single-lepton)
    * x Axis
        * Reconstructed invariant mass of the ttbar system in the single-lepton channel, using one leptonic top and one hadronic top reconstruction.
        * `$m_{t\bar{t}}$ [GeV]`
        * Proposed range 2000-4000 GeV with 40-80 bins.
        * One entry per selected event using the best combination.

## Analysis Steps

1. Event Selection
    * Exactly one isolated charged lepton (electron or muon).
    * Missing transverse momentum consistent with leptonic W decay.
    * At least 4 jets, with at least 2 b-tagged jets.
    * The b-tagging working point is not specified by the request and should remain unresolved until needed.
2. Object Definitions
    * Identify jets, b-tagged jets, leptons, and missing transverse momentum.
3. Leptonic Top Reconstruction
    * Use lepton + MET to reconstruct W -> l nu using the W-mass constraint for the neutrino pz.
    * Combine the leptonic W with a b-tagged jet to form a leptonic-top candidate.
4. Hadronic Top Reconstruction
    * From the remaining jets, choose a b-tagged jet and two non-b jets to form a hadronic-top candidate.
5. Combination Choice
    * Select the combination minimizing a chi2-like metric based on consistency with the W- and top-mass hypotheses.
    * The exact chi2 definition is not specified and should not be invented unless the user wants a fully specified reconstruction.
6. ttbar Mass
    * Combine the selected leptonic- and hadronic-top four-vectors to form `m_ttbar`.

## Workflow

1. Data Extraction and NTuple Skimming
    * Filtering: require at least 1 lepton and at least 4 jets at the source if possible.
    * Variables: lepton 4-vectors and IDs, jet 4-vectors, b-tag information, MET and MET phi, event weights if any, and run/lumi/event identifiers.
2. Data Analysis & Histogramming
    * Build leptonic- and hadronic-top candidates.
    * Apply the stated event selections.
    * Choose the best reconstruction combination.
    * Fill the `m_ttbar` histogram.

## Statistical Analysis

No statistical analysis is required beyond the histogram.

# Example 4: Published Legacy Analysis with a User-Requested Background-Method Replacement

This example illustrates a source-derived specification. The user asks to reproduce the physics selection of a published legacy analysis, but to replace the published multijet estimate with an ABCD method. The specification keeps the source selection faithful while making the requested replacement explicit.

## Data Samples

| Data Sample | Role(s) In Analysis |
| --- | --- |
| Collision data described by the source analysis | Signal region and nominal data-driven background estimate |
| Independent inclusive-jet or multijet control data described by the source | ABCD closure and validation only |
| Dedicated non-collision control samples described by the source | Cosmic-ray and beam-related background estimates |
| Source benchmark signal MC samples | Signal acceptance and interpretation |

Do not invent a modern dataset identifier if the source does not provide one. If the generated signal points are sparse, preserve the actual benchmark tuples rather than listing each parameter independently.

## Backgrounds

* Multijet/QCD: replace the source method with the user-requested ABCD method.
* Cosmic-ray background: preserve the dedicated source-derived control method unless the user asks to replace it.
* Beam-related background: preserve the dedicated source-derived control method unless the user asks to replace it.
* Other backgrounds: include only if supported by the source or explicitly requested.

## Data Required

* Candidate-object kinematics and the observables entering the signal selection.
* Trigger decision and trigger-object matching.
* Object-quality and isolation information.
* Event-cleaning variables.
* Variables defining the two ABCD discriminants.
* Variables needed to evaluate closure versus important kinematic or pile-up dependencies.
* Signal truth information required for source-derived acceptance or lifetime reweighting.
* Dedicated control-sample metadata for non-collision backgrounds.

## Histograms

1. Candidate-object kinematics
    * Plot the key object pT/ET and eta distributions after common preselection.
2. ABCD discriminant 1
    * Plot the first probe-object discriminant with the nominal pass/fail boundary shown.
3. ABCD discriminant 2
    * Plot the second probe-object discriminant with the nominal pass/fail boundary shown.
4. ABCD plane
    * Two-dimensional distribution of discriminant 1 versus discriminant 2 for the probe object.
    * Draw the A/B/C/D boundaries explicitly.
5. ABCD yields
    * Four event categories A, B, C, and D after the common preselection.
6. ABCD closure/nonclosure
    * Plot `N_A N_D / (N_B N_C)` or the equivalent fitted nonclosure factor in validation samples or sidebands.
7. Cutflow
    * Include common event selection, trigger, object selection, control-region branching, and final signal selection.
8. Signal acceptance versus the scanned model parameter
    * Preserve the source method for interpolation, reweighting, or efficiency-map convolution. Do not replace it with a generic generated-grid interpolation unless that is what the source actually did.

## Analysis Steps

1. Reconstruct the source common event selection
    * Preserve source-derived data quality, event cleaning, object kinematics, and topology requirements.
    * Phrase source-specific detector or track-quality details as the source realization of the underlying physics requirement when a run-independent specification is desired.
2. Define object roles explicitly
    * Identify the trigger-matched/tag object and the second/probe object.
    * Do not assume that the trigger-matched object is the leading object unless the source says so.
3. Preserve the nominal signal-object requirements
    * The tag object satisfies the complete source-derived signal-like offline selection required to define the event.
    * The probe object is the object on which the two ABCD discriminants are opened.
4. Construct the user-requested ABCD regions
    * X = probe passes/fails discriminant 1.
    * Y = probe passes/fails discriminant 2.
    * A = X pass, Y pass.
    * B = X pass, Y fail.
    * C = X fail, Y pass.
    * D = X fail, Y fail.
    * Verify explicitly that A is identical to the nominal two-object signal region after the common preselection.
5. Check trigger sculpting
    * Confirm that the trigger does not directly force the probe to pass one of the ABCD discriminants.
    * If the trigger applies the discriminant to the tag object, state this and keep the ABCD definition on the probe.
6. Estimate multijet/QCD
    * Use `N_A^QCD = kappa * N_B^QCD * N_C^QCD / N_D^QCD` as the defining transfer relation.
    * Do not assume `kappa = 1` without closure.
    * Determine or constrain nonclosure in nominal-trigger validation regions when possible.
    * Use independently triggered multijet data as an additional validation sample rather than assuming its correlation structure transfers exactly.
    * Test closure versus probe kinematics, tag kinematics, pile-up, and any event variable known to influence the discriminants.
7. Treat contamination consistently
    * Evaluate signal contamination in B, C, and D for every relevant signal hypothesis.
    * Include cosmic, beam-related, and other supported backgrounds in all affected regions rather than assuming they appear only in A.
8. Preserve source signal extrapolation
    * If the source uses event reweighting, an efficiency map, or an analytic decay convolution to move between generated and interpreted signal points, document that method faithfully.
    * Validate any interpolation/reweighting against explicit generated samples when available.
9. Preserve dedicated non-collision background methods
    * Reproduce the source logic for cosmic-ray and beam-related control samples unless the user requested a replacement.

## Workflow

1. Data Extraction and NTuple Skimming
    * Apply only safe common preselection at extraction time.
    * Retain all variables needed to move events among A/B/C/D; do not skim away failed probe-discriminant states.
    * Retain dedicated control samples separately.
2. Data Analysis & Histogramming
    * Build tag/probe roles.
    * Construct common selection and A/B/C/D region flags.
    * Produce the 2-D discriminant plane and closure plots before using region A in the final result.
    * Evaluate signal contamination and non-collision contamination in all four regions.
3. Statistical Model Construction
    * Represent A/B/C/D simultaneously when appropriate.
    * Parameterize QCD yields using the ABCD relation and a nonclosure nuisance.
    * Include signal and non-QCD backgrounds in every region where they contribute.
    * Correlate systematic uncertainties only when they share a physical source.

## Statistical Analysis

Use the statistical method specified by the source for unchanged parts of the interpretation. For the user-requested ABCD replacement, a simultaneous likelihood over A/B/C/D is preferred when appropriate, with the QCD transfer relation and nonclosure uncertainty represented explicitly.

If this is a modernization relative to the published source, label it as part of the requested background-method replacement rather than implying that the source analysis used the same likelihood.

---

## What Example 4 Is Intended To Teach

These notes are guidance for the skill and are not part of a generated specification.

* A source-derived specification should not silently substitute modern formats or algorithms.
* The physics intent and source-specific realization can both be preserved.
* A user-requested change should be isolated, then propagated only where logically necessary.
* A control-region method must be checked against the trigger and object-role logic.
* "Region A is the signal region" is a statement that must be verified, not assumed.
* Sparse benchmark tuples should not be expanded into nonexistent combinations.
* Lifetime or parameter extrapolation must follow the mechanism actually used in the source.
* A second review pass should catch contradictions among the trigger, selection, ABCD regions, workflow, and statistical model.

## For Review

{{- Item one the user should review}}
{{- Item two the user should review}}
