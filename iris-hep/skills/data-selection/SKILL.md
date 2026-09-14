---
name: data-selection
description: Select and justify experiment analysis datasets and record the result in a backend-neutral YAML specification. Use when an analysis needs logical dataset identifiers, Run-2 versus Run-3 choices, AMI or Rucio dataset selection, or evidence for an ATLAS derivation choice.
---

# Data Selection

Produce or update datasets.yaml as the single authored specification of analysis inputs. It describes what the downstream analysis should consume, not how the datasets were discovered, tested, resolved, transferred, cached, or processed.

Do not author a parallel datasets.md. When documentation is requested, generate it from the validated YAML and label the rendered document as derived output.

## Keep the specification declarative

Start from [assets/datasets-template.yaml](assets/datasets-template.yaml). Read [references/dataset-yaml-format.md](references/dataset-yaml-format.md) before adding source types or metadata fields. Validate against [assets/datasets.schema.json](assets/datasets.schema.json).

Each named dataset contains only:

- a stable analysis key;
- one logical source, such as a Rucio DID, CMS DAS dataset, or explicit URI list;
- stable physics and production metadata;
- the physical serialization and object or tree name.

Do not put execution history in datasets.yaml. In particular, exclude ServiceX request IDs, replica or file-resolution results, tested files or fractions, cache paths, manifests, notebook or report paths, timestamps, job status, study records, rejected alternatives, and open questions.

A downstream RDF, Coffea, ServiceX, AnalysisBase, or other adapter resolves the logical source and may create transient manifests or transformed products. Those products must not be written back into the canonical specification.

## Establish the analysis context

Record the experiment, Run 2, Run 3, or other collision era, collision energy, data-taking years, MC campaigns, and relevant reconstruction or calibration constraints before selecting datasets.

Do not silently translate a Run-2 list into Run 3. When the era is ambiguous and materially changes the selection, ask one focused question. Keep separate records when campaigns, derivations, or normalization metadata differ.

Use authoritative catalog information where available. Preserve complete scope-qualified Rucio DIDs, exact production tags, campaign names, DSIDs or run ranges, and normalization metadata. Unknown values should be omitted or null, never invented.

## Apply the ATLAS derivation evidence ladder

For ATLAS datasets, use this order:

1. Use PHYSLITE when it contains the required calibrated objects, event information, truth information, and decorations with adequate performance.
2. Use PHYS only when there is an obvious, named reason PHYSLITE cannot satisfy the analysis, or a focused study demonstrates the failure.
3. Use LLP1 or another larger or bespoke derivation only when there is an equally explicit reason PHYS is inadequate, supported by a focused study when the claim is empirical.

A larger derivation is not justified by familiarity, historical precedent, convenience, or an isolated catalog, ServiceX, or transform failure. Separate access failures from missing EDM content and physics-performance failures.

The studies and their execution records are decision evidence outside datasets.yaml. Once the decision is reviewed, record only the selected DID and its stable derivation metadata in the specification.

## Commission focused side studies

When catalog inspection cannot settle a content or performance question, spawn one bounded sub-agent study per independent question and run independent studies in parallel when capacity permits. Read [references/side-studies.md](references/side-studies.md) before delegating or reviewing them.

Prefer ServiceX for small columnar tests. Start with one matched file or a small representative fraction, then expand only when statistical precision or sample diversity is demonstrably inadequate.

When model selection is controllable:

- Use a Sol-class model at medium reasoning for coordination, catalog research, study design, YAML synthesis, and review.
- Use Luna at high reasoning for bounded ServiceX and plotting studies with explicit inputs, cuts, plots, and acceptance criteria.
- Escalate to Sol high or a more capable model when truth definitions, EDM interpretation, campaign provenance, or failure diagnosis remain ambiguous.

These are routing defaults, not availability requirements. The coordinator must review notebooks, numerical conclusions, and the resulting YAML selection before accepting them.

Require evidence for the actual topology. A displaced-jet analysis, for example, should test jets matched to LLPs decaying in the relevant detector region rather than relying only on inclusive jets. Comparisons used for decisions must have compatible calibration states and event samples.

## Complete and validate

Before delivering datasets.yaml:

- resolve every selected sample to an authoritative logical identifier;
- confirm era, campaign, reconstruction, derivation, and normalization compatibility;
- review any empirical derivation evidence in its separate notebook or report;
- ensure unresolved questions that could change dataset identity are settled or report that the specification remains incomplete;
- remove every execution-specific field;
- validate the YAML against the bundled JSON Schema.

The completed YAML is the downstream contract. Study artifacts may explain why it was chosen, but they are not part of that contract.
