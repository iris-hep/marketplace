---
name: analysis-spec-builder
description: Build and iteratively refine physics analysis specifications from user requirements, source documents, or both, using analysis-specification-template.md. Use when the user asks to create or update an analysis spec, formalize a quick analysis task, or reconstruct/adapt an analysis from a paper or note.
---

# Analysis Spec Builder

Build a technically precise analysis specification from the available evidence. Keep the specification as run- and implementation-independent as the user's goal allows, while preserving source-specific details when they are essential to the analysis definition.

The output is a specification of _what the analysis does and why_, not a low-level implementation plan.

## Request Modes

First classify the task into one of these modes:

1. **Direct analysis request**
   - The user describes an analysis or plot directly.
   - Fill in reasonable defaults only when they are conventional and low-risk.

2. **Source-derived reconstruction**
   - The user provides a paper, note, thesis, existing analysis, or prior specification and asks to reconstruct it.
   - Treat the source as authoritative for what the original analysis did.
   - Do not silently modernize, correct, or substitute details.

3. **Source-derived analysis with requested changes**
   - Reconstruct the source analysis, but explicitly replace or modify only the parts requested by the user.
   - Preserve the original logic everywhere else unless the requested change forces a dependent change.
   - Clearly distinguish source-derived content from user-requested modifications.

4. **Specification refinement**
   - The user provides an existing specification and asks to improve or update it.
   - Preserve unaffected decisions and revise only what is necessary.

## Workflow

1. Read the template from `./assets/analysis-specification-template.md` (relative to this file, in the `analysis-spec-builder` subdirectory).
2. Read all user-provided source material that is relevant to the requested analysis.
3. Identify the analysis intent before extracting implementation details:
   - target physics/process or measurement,
   - event topology,
   - signal-defining observables,
   - main backgrounds,
   - control/validation strategy,
   - statistical output.
4. Draft a filled-in specification by replacing all `{{...}}` placeholders with concrete content.
5. If a source analysis is being reconstructed, perform a separate **source-fidelity and consistency review** of the draft before finalizing it.
6. Ask focused follow-up questions only for missing details that are critical to defining the analysis. Do not block on non-critical implementation details.
7. Write the final content to `specification.md` unless the user provides a different path.

## Drafting Rules

- Replace every `{{...}}` placeholder with real content; do not leave placeholders in the final spec.
- Keep the tone concise and technical; preserve the template section order.
- Use ASCII-only text unless the template already uses non-ASCII (for example LaTeX labels inside backticks).
- Preserve explicit dataset identifiers, analysis names, benchmark definitions, and user-specified choices verbatim.
- This is a specification, not a step-by-step implementation plan.
- Include enough detail that a later implementation step can reproduce the analysis logic without having to rediscover the intent.
- Do not invent exact container names, calibration versions, trigger-chain names, working points, dataset identifiers, or software releases unless they are provided by the user or source.
- If a detail is missing but not critical, say that it is not specified or leave it at the appropriate conceptual level rather than fabricating a concrete value.
- If a missing detail changes the physics definition, control-region definition, normalization, or statistical interpretation, ask a short follow-up question.
- When a user explicitly requests a deviation from a source analysis, that request overrides the source for that component. Propagate any logically necessary consequences of that change, but do not modify unrelated parts of the analysis.

## Analysis Intent vs. Run-Specific Realization

For source-derived analyses, preserve both of these levels when useful:

- **Analysis intent:** the physics purpose of a requirement.
  - Example: require a displaced-jet candidate to be track-isolated.
- **Source realization:** how that requirement was implemented in the source.
  - Example: zero good tracks above a stated pT threshold inside a stated cone, with a source-specific track-quality definition.

Prefer the intent as the primary specification language when the user wants a run-independent analysis. Include the source realization when it is needed to define the original analysis precisely or will be useful for a later translation to another run.

Do not turn a source-specific implementation into a timeless physics requirement unless the source supports that interpretation.

## Data and Dataset Defaults

- For a direct, modern ATLAS analysis request with no data format specified, PHYSLITE may be proposed as a default when appropriate.
- Do **not** apply the PHYSLITE default when reconstructing a published or legacy analysis. Preserve the source's data description, or state that the concrete dataset/derivation identifier is not specified.
- Do not infer that a source analysis used a modern data format, derivation, trigger model, calibration, or reconstruction release.
- Keep generated signal benchmark combinations as actual tuples or a table when only specific mass/parameter combinations exist. Do not convert them into independent lists that imply nonexistent combinations.

## Selections, Objects, and Regions

Write selections so that the event logic is unambiguous.

Check all of the following:

- which object is the leading, trigger-matched, tag, probe, or candidate object;
- whether thresholds apply to a specific object or merely to at least one object;
- whether "exactly N jets" means exactly N reconstructed jets or exactly N jets satisfying a candidate selection;
- whether trigger requirements preselect or sculpt an observable later used for a control region;
- whether a control-region definition is applied before or after common event selections;
- whether the stated signal region is exactly equivalent to the nominal pass/pass control-region definition when an ABCD method is used.

If multiple objects play different roles, name those roles explicitly rather than relying only on "leading" and "subleading" when that would be ambiguous.

## Background Methods

When documenting a background estimate, specify:

- the background being estimated;
- the data or simulation sample used;
- the control/sideband variables;
- the region definitions;
- the normalization or transfer relation;
- closure/validation tests;
- known or plausible correlations;
- contamination from signal or other backgrounds;
- statistical treatment and nuisance parameters.

## Systematic Uncertainties

Separate systematic uncertainties into useful categories:

1. **Source-analysis uncertainties**
   - uncertainties explicitly used in the reference analysis.

2. **New-method uncertainties**
   - uncertainties introduced by a user-requested replacement such as an ABCD estimate.

3. **Modernization/adaptation uncertainties**
   - uncertainties that may be needed in a future run or implementation but were not part of the source analysis.

Do not present a newly invented or modernized uncertainty as if it came from the source.

Preserve unusual source-specific performance issues when they are important to the analysis intent, such as calibrations for non-standard jets or the effect of pile-up on track isolation.

## Statistical Analysis

State the statistical model at the level justified by the request and source.

For source-derived analyses:

- preserve the source test statistic, limit-setting method, counting/shape treatment, and treatment of nuisance parameters when known;
- distinguish source behavior from sensible modern additions;
- do not claim the source produced expected limits, simultaneous control-region fits, asymptotic limits, or other outputs unless it did;
- if a modernized statistical treatment is added because it is natural for a new background method, label it as part of the requested modification rather than source reconstruction.

For new analyses, default to `cabinetry` and `pyhf` when statistical inference is needed unless the user specifies another framework.

## Source-Fidelity and Consistency Review

For any nontrivial source-derived specification, perform a second pass after drafting. This pass is mandatory even when no follow-up question is needed.

Check the draft against the source for:

1. **Thresholds and inequalities**
   - pT/ET, eta, timing, MET, isolation, mass windows, multiplicities.

2. **Object roles**
   - trigger-matched vs leading object, tag vs probe, leading vs subleading.

3. **Selection ordering**
   - common preselection, trigger, object selection, final signal selection.

4. **Region equivalence**
   - verify that the nominal signal region and any A/pass-pass region are actually the same selection when claimed.

5. **Trigger/control-region interactions**
   - verify that the trigger does not make a stated sideband inaccessible or strongly pre-sculpt a discriminant without this being acknowledged.

6. **Background logic**
   - control sample, normalization, correlations, closure, contamination, and whether a requested replacement method is internally consistent.

7. **Signal benchmarks**
   - exact generated parameter combinations, not just the union of values.

8. **Parameter extrapolation**
   - verify whether the source used interpolation, reweighting, efficiency maps, generated grids, or another method.

9. **Systematics provenance**
   - source-derived vs newly introduced uncertainties.

10. **Statistical interpretation**
    - observed vs expected outputs, likelihood structure, test statistic, toys vs asymptotics, and limit parameter.

11. **Internal contradictions**
    - compare Data Samples, Data Required, Triggers, Histograms, Analysis Steps, Workflow, and Statistical Analysis for inconsistent definitions.

If the review finds a contradiction, fix it before writing the final file. If the source itself is ambiguous, state the ambiguity rather than guessing.

For a simple one-plot or small direct analysis, use a lightweight version of this review: verify that the requested data, selection, histogram definition, and workflow agree with one another.

## Follow-up Questions

Make a best-effort attempt to fill in the specification from the source and any other information provided before asking questions. Ask only about missing details that materially change the physics definition, control or validation logic, normalization, or statistical interpretation.

In the section labeled `## For Review`, list the assumptions you made due to non-critical missing information so the user can review and modify them later if needed.

- Group questions by topic.
- Do not ask about low-level implementation details that belong to a later planning stage.
- When the source is explicit, do not ask the user to reconfirm it.

## Output

- If the user asks for a draft or is iterating interactively, provide the full draft specification in the response.
- If the user explicitly asks for a file to be produced immediately, write it without requiring a separate confirmation step.
- Otherwise, provide the draft and write the final file after the user confirms it.
- Default output path: `specification.md`.
