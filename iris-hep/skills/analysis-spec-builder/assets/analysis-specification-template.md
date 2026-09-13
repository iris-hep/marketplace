# {{Analysis/Workflow Name}}

{{Short description of the analysis (no more than 2 lines). State the physics or analysis goal, not the implementation details.}}

{{Optional sections may be omitted when they are not relevant. For a simple plotting task, the specification can remain short. For a source-derived or complex analysis, include the additional provenance, regions, background, validation, systematic, and statistical details needed to make the analysis logic unambiguous.}}

## Source and Scope

{{Include this section for source-derived analyses, adaptations, or refinements. Omit it for a simple direct request with no external source.}}

* Analysis mode: {{Source-derived reconstruction / source-derived with requested changes / refinement of an existing specification}}
* Source(s): {{Paper, note, thesis, existing specification, or other authoritative source}}
* Analysis intent: {{Run- and implementation-independent description of what the analysis is trying to select, measure, or test}}
* Source realization: {{Important run-, detector-, trigger-, or software-specific realization of the analysis intent, if useful}}
* Requested deviations from the source: {{Explicitly list user-requested changes; say `None` if reconstructing the source exactly}}
* Added or modernized elements: {{Any deliberate additions not present in the source, such as a new background method or statistical treatment. Do not present these as source-derived.}}

## Data Samples

{{List all data and simulation samples needed for this work. Preserve explicit dataset identifiers verbatim when provided. Do not invent modern dataset names for legacy/source-derived analyses. If only specific benchmark parameter combinations exist, list the actual tuples or combinations rather than independent parameter lists.}}

| Data Sample | Role(s) In Analysis |
| --- | --- |
| {{ds 1}} | {{Signal, background, signal region, control region, validation, etc. Include a short description of how it is used.}} |
| {{ds 2}} | {{Signal, background, signal region, control region, validation, etc. Include a short description of how it is used.}} |

## Backgrounds

{{List the relevant backgrounds and how each is treated. Omit this section only when the task genuinely has no background-estimation component. Distinguish source-derived methods from user-requested replacements.}}

* {{Background 1}}
    * Importance: {{Dominant / subdominant / negligible / not quantified}}
    * Estimation method: {{Data-driven, simulation, sideband, ABCD, template fit, etc.}}
    * Control/validation sample(s): {{If applicable}}
* {{Background 2}}
    * ...

## Data Required

Below is the specific information needed from each data sample above.

### {{ds 1}}

* {{Object/event variable 1}}
* {{Object/event variable 2}}
* {{Trigger, event-cleaning, truth, weight, or metadata information if required}}

### {{ds 2}}

* {{Object/event variable 1}}
* ...

{{For source-derived analyses, include detector- or run-specific quantities only when they are needed to reproduce the source realization or to enable a later translation. Do not invent unavailable field names, container names, or calibration versions.}}

## Triggers

{{List triggers only when relevant. For each trigger, state its purpose, the important selection logic, and any offline plateau requirement. If a trigger can sculpt a control-region or background-estimation variable, state that explicitly. Say `None` if no trigger requirement is needed.}}

* {{trigger 1}}
    * Role: {{Signal / control / validation}}
    * Selection: {{Important trigger-level requirements}}
    * Offline requirement: {{Threshold or matching needed for efficient use, if known}}
    * Interaction with analysis variables: {{Any relevant sculpting or object-role consequence}}
* {{trigger 2}}
    * ...

## Object Definitions and Roles

{{Include when the analysis uses nontrivial object definitions or when objects have different roles. Omit for very simple analyses.}}

* {{Object type or role}}
    * Analysis intent: {{Physics meaning of the object requirement}}
    * Source realization: {{Run-/detector-specific implementation if source-derived and useful}}
    * Kinematic/quality requirements: {{Only those needed to define the analysis}}
* {{Tag / probe / trigger-matched / leading / subleading / candidate object}}
    * {{Define the role explicitly. Do not assume trigger-matched means leading unless that is actually required.}}

## Analysis Regions

{{Include for analyses with signal, control, validation, sideband, or ABCD regions. Omit for analyses with only one undivided event selection. Define the common preselection once, then specify exactly what changes between regions.}}

Common preselection:

* {{Requirement 1}}
* {{Requirement 2}}

| Region | Purpose | Additional or modified requirements |
| --- | --- | --- |
| {{Signal Region / A}} | {{Signal selection / pass-pass region / etc.}} | {{Exact requirements beyond common preselection}} |
| {{Control Region B}} | {{Background constraint}} | {{Exact differences from signal region}} |
| {{Control Region C}} | {{Background constraint}} | {{Exact differences from signal region}} |
| {{Validation Region}} | {{Closure / modeling validation}} | {{Exact requirements}} |

{{If a region is claimed to be identical to another selection, such as ABCD region A being the final signal region, define it so that this equivalence can be checked directly.}}

## Histograms

{{List each summary histogram or table that should be produced. These may be final observables, statistical inputs, validation plots, or cross-checks. Do not invent binning if neither the user nor source specifies it; state only the required range/features or leave binning to implementation. Include 2-D plots when correlations are central to the method.}}

1. {{Histogram 1 Title}}
    * Purpose
        * {{Final observable / control-region validation / closure / diagnostic / etc.}}
    * x Axis
        * {{Detailed description of what should be plotted}}
        * {{Axis label, including units if dimensional, e.g. `$p_T$ [GeV]` or `$\eta$`}}
        * {{Binning or axis limits only if specified or required by the analysis logic}}
        * {{Number of entries per event, object, or combination}}
    * {{List other axes here if needed}}
2. {{Histogram 2 Title}}
    * ...

## Analysis Steps

{{Describe the high-level transformations from source data to the final regions, observables, and predictions. These should be physics-analysis operations, not low-level implementation instructions. Break reusable calculations out explicitly.}}

1. {{Common event selection}}
    * {{Event-level requirements and ordering where it matters}}
2. {{Object selection and role assignment}}
    * {{Define candidate, tag, probe, trigger-matched, leading/subleading roles as needed}}
3. {{Derived variable or reconstruction}}
    * {{How the variable is calculated}}
    * {{Mention combinatorics explicitly when selecting a best combination}}
4. {{Signal/control/validation region construction}}
    * {{How events are assigned to regions}}
5. {{Background estimation, if needed}}
    * {{Control variables, transfer relation, normalization, fit, or template method}}
    * {{Known or plausible correlations and how they are validated}}
    * {{Treatment of signal or other-background contamination}}
6. {{Signal modeling or parameter extrapolation, if needed}}
    * {{Generated benchmark points}}
    * {{Interpolation, reweighting, efficiency map, analytic convolution, or extrapolation method. Preserve the mechanism actually used by the source.}}
7. {{Validation and closure}}
    * {{Closure tests, sidebands, alternative samples, stability tests, or source-comparison checks}}

## Workflow

{{List the processing stages needed to produce the final histograms and statistical inputs. Add or remove stages as appropriate, for example ML training or calibration derivation.}}

1. Data Extraction and NTuple Skimming
    * Filtering: {{What event/object filtering can safely be done at the source-data level. Do not filter away events needed for control regions or pass/fail definitions. Say `No Filtering` if none is appropriate.}}
    * Variables: {{List the variables that must be passed downstream.}}
2. Data Analysis and Histogramming
    * {{Construct derived variables, object roles, combinations, and region flags.}}
    * {{Apply high-level event filtering and fill the requested histograms/tables.}}
3. {{Background Estimation / Model Construction / ML Training / other stage, if needed}}
    * {{Describe the stage at analysis level.}}
4. {{Statistical Model Construction, if needed}}
    * {{List the regions/observables entering the likelihood and the components constrained by data.}}

## Validation and Cross-checks

{{Include when the analysis has a nontrivial background method, parameter extrapolation, trigger efficiency, ML model, or other component requiring explicit validation. Omit for simple direct plotting tasks.}}

* {{Closure test or validation 1}}
* {{Stability versus relevant kinematics, pile-up, detector region, or other variables}}
* {{Independent control sample or source-comparison check}}
* {{Signal contamination check, if relevant}}

## Systematic Uncertainties

{{Include when systematic uncertainties are part of the requested analysis or source. Separate their provenance so source-derived uncertainties are not confused with new-method or modernization uncertainties. Omit when no systematics are required.}}

### Source-analysis uncertainties

* {{Uncertainty explicitly present in the source analysis}}
* ...

### New-method uncertainties

* {{Uncertainty introduced by a user-requested replacement or new background/modeling method}}
* ...

### Modernization/adaptation uncertainties

* {{Uncertainty expected only for a later run/adaptation or newly modernized implementation}}
* ...

{{State which analysis stages or model components must be repeated or varied for each class of systematic when that matters. Correlate uncertainties only when they share a physical source.}}

## Statistical Analysis

{{Describe the statistical inference, if any. Say `None` for a pure plotting/reconstruction task.}}

* Observable(s) / regions entering the model: {{Signal region, control regions, shape histograms, etc.}}
* Parameter(s) of interest: {{Cross section, branching ratio, signal strength, mass, efficiency, etc.}}
* Background constraints: {{How background normalizations or transfer factors enter the model}}
* Nuisance parameters: {{Main statistical and systematic constraints}}
* Test statistic / interval method: {{Profile likelihood, CLs, confidence interval, significance test, etc.}}
* Expected and observed outputs: {{Only claim outputs supported by the source or explicitly added by the requested modernization}}
* Source-vs-modernized treatment: {{For source-derived analyses, state whether this reproduces the source statistical procedure or deliberately changes it}}
