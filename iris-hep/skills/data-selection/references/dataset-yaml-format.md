# Dataset YAML format

datasets.yaml is the sole authored dataset specification. It is a declarative contract for downstream consumers.

## Design boundary

The file represents:

    named physics sample -> logical source + stable metadata + physical data format

It does not represent:

    logical source -> resolver or transform -> files, replicas, chunks, caches, or outputs

RDF, Coffea, ServiceX, AnalysisBase, and other adapters may resolve the same logical source differently. Their request IDs, manifests, files, configuration, and products are runtime state and must remain outside datasets.yaml.

## Required invariants

- The root contains $schema, schema_version, analysis, and datasets.
- schema_version matches the bundled contract, currently 0.2.0.
- Every dataset key is stable, lowercase, and meaningful to the analysis.
- Every dataset has exactly one logical source.
- metadata.process is the physics-process label used by the analysis.
- metadata.data_type is data, mc, or embedded.
- Physical serialization is described by data_format.
- A selected derivation may be recorded as stable metadata, but its study history is not stored here.
- No field records execution, validation history, or discovery provenance.

## Logical source variants

### Rucio

    source:
      type: rucio
      did: "scope:name"
      did_type: dataset

Use a complete scope-qualified DID. Record whether it identifies a container, dataset, or file when known.

### CMS DAS

    source:
      type: cms_das
      dataset: "/PrimaryDataset/ProcessedDataset/DataTier"

### Explicit files or URIs

    source:
      type: files
      uris:
        - "root://host/path/file.root"

Use explicit URIs only when the files themselves are the durable specified input and no logical catalog identifier exists. Do not replace a Rucio or DAS source with resolved PFNs.

ServiceX is not a source type when it transforms a Rucio or DAS dataset. It is a downstream consumer of this specification.

## Metadata

The schema standardizes common stable fields while allowing experiment-specific additions. Prefer explicit units in names, such as cross_section_pb.

Useful common fields include:

- experiment
- process
- data_type
- collision_era
- collision_energy_tev
- campaign
- year
- dsid
- run_range
- derivation
- cross_section_pb
- filter_efficiency
- k_factor
- generator
- production_tags

Do not fill unknown numeric values with zero. Omit them or use null.

## Data format

data_format.type describes physical serialization, such as ROOT or Parquet. data_format.object names the ROOT tree, RNTuple, or equivalent logical object.

ATLAS derivation names are stable properties of the selected dataset and belong in metadata.derivation. They are not execution records.

## Deliberately excluded content

Do not add:

- ServiceX request IDs or backend parameters;
- resolved files, replicas, manifests, or cache locations;
- tested files, event counts, or sample fractions;
- notebooks, plots, reports, or study status;
- catalog lookup timestamps or citations;
- rejected alternatives, rationales, or open questions;
- job status or processing history.

Those may live in separate study reports, execution manifests, logs, or provenance systems. They must not become part of the analysis input contract.

## Documentation generation

Documentation is a deterministic view of validated YAML. A renderer may display only the logical sources, stable metadata, and data formats present in the specification. Corrections are made in YAML and the documentation regenerated.
