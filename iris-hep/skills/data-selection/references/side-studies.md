# Side-study protocol

Read this reference only when a dataset, derivation, or object-content question needs empirical evidence. Side studies inform dataset selection but are not part of datasets.yaml.

## Define one decision per study

Each study prompt must state:

- the decision the study can change;
- candidate derivations or object collections;
- exact known logical dataset sources, or a bounded catalog lookup;
- the smallest representative sample to start with;
- object, truth, event, and fiducial definitions;
- required plots and numerical summaries;
- calibration and matching requirements;
- acceptance criteria;
- notebook and rendered-view paths;
- a request to return specific questions if blocked.

Do not delegate an unbounded request to determine which derivation is best.

## Preferred execution pattern

Use ServiceX for column-level access and the UChicago Analysis Facility when available. Assume an existing servicex.yaml may provide credentials, but report missing configuration rather than inventing it.

Begin with NFiles=1 or an equivalently small fraction. Prefer exact matched files or common event identifiers when comparing derivations. Expand only when counts make the requested efficiency or tail comparison statistically inconclusive.

Independent questions may run in parallel. Examples include required content availability, exact object equivalence across derivations, alternate object-collection performance for the signal topology, and acceptance near detector boundaries.

## Notebook standard

The notebook is executable evidence and a report section. Include:

1. Decision question and why it matters.
2. Exact logical sources, tested files or fraction, production tags, and ServiceX request IDs.
3. Object definitions, calibration state, units, and event joins.
4. Cuts, denominator, numerator, matching algorithm, and ambiguity handling.
5. Cutflow and object counts.
6. Plots with labeled axes, units, legends, and uncertainties where meaningful.
7. Integrated numerical results and relevant binned values.
8. Limitations and whether failures are technical or physical.
9. A direct conclusion: supports the smaller derivation, justifies escalation, or remains inconclusive.
10. Specific next questions and the smallest follow-up test for each.

Export HTML or Markdown beside the notebook when practical. Keep plot-producing code in the notebook so each displayed plot is traceable one-to-one to its calculation.

## Review gate

The coordinating agent must verify that the notebook ran on the claimed inputs, plot code matches displayed output, event joins and units are correct, denominators represent the target topology, conclusions do not exceed the tested fraction, and technical failures are not reported as derivation inadequacy.

After review, update datasets.yaml only with the chosen logical dataset, stable metadata, and data format. Keep ServiceX identifiers, sampled files and fractions, notebooks, rendered reports, plots, alternatives, rationale, and open questions in separate working evidence. Do not copy them into the canonical specification.
