---
name: awkward-array
description: >-
  Use when working with jagged or variable-length arrays in Python HEP analysis:
  building event records with ak.zip, filtering nested arrays, computing
  combinatorics (cartesian products or combinations), flattening ragged arrays,
  using argmin/argmax with keepdims, broadcasting per-event weights to
  per-object, or debugging OptionType/None-padding issues in Awkward 2.x
  workflows.
---

# Awkward Array

## Overview

Awkward Array provides NumPy-like idioms for variable-length, nested, and
record-structured data — the natural shape of HEP event data. Version 2.x
(current) has a substantially different API from 1.x; do not mix patterns.

## When to Use

- Reading TTrees via uproot (returns `ak.Array` automatically)
- Building physics-object records and applying per-object selection
- Computing pair quantities (invariant mass, deltaR) via combinatorics
- Broadcasting per-event scalars to per-object arrays for weighted fills
- Preparing arrays for histogram filling or NumPy interop

## Key Concepts

| Concept        | Notes                                                        |
| -------------- | ------------------------------------------------------------ |
| `ak.type(arr)` | Inspect type — e.g., `var * {pt: float64}`                   |
| `OptionType`   | `None` values from `pad_none` or `firsts` on empty events    |
| Behaviors      | `vector.register_awkward()` adds 4-vector methods to records |
| `ak.num(arr)`  | Per-event count (number of jets per event, etc.)             |

## Canonical Patterns

**Build a record from columns**:

```python
import awkward as ak
jets = ak.zip({"pt": events["jet_pt"], "eta": events["jet_eta"],
               "phi": events["jet_phi"], "mass": events["jet_m"]})
```

**Filter objects, then events**:

```python
good_jets = jets[jets.pt > 25_000]                    # per-object mask, MeV
events_ok = good_jets[ak.num(good_jets) >= 2]         # per-event mask
```

**Broadcast per-event weight to per-object for weighted fills**:

```python
flat_w = ak.flatten(ak.broadcast_arrays(events.weight, jets.pt)[0])
flat_pt = ak.flatten(jets.pt)
h.fill(pt=ak.to_numpy(flat_pt), weight=ak.to_numpy(flat_w))
```

## Gotchas

- **`firsts` vs `[:, 0]`**: `firsts` returns `None` for empty events; `[:, 0]`
  raises. Use `firsts` whenever collections may be empty.
- **`flatten` depth**: Default `axis=1` flattens one level. `axis=None` flattens
  everything — rarely correct.
- **`option` propagation**: Once `OptionType` enters, operations propagate
  `None`. Call `ak.drop_none` or `ak.fill_none` before NumPy interop.
- **`to_numpy` on ragged**: Fails unless regular. Always flatten or select a
  fixed depth first.
- **Behavior registration is global**: Call `vector.register_awkward()` once at
  module level; it mutates the global dict.
- **2.x breaking changes from 1.x**: Many top-level functions were renamed or
  removed; behavior registration changed. Do not copy 1.x examples verbatim.

## Interop

- **uproot**: `tree.arrays()` returns `ak.Array` — no conversion needed
- **vector**: `register_awkward()` gives records with `pt/phi/eta/mass` Lorentz
  methods
- **hist**: Flatten arrays before `Hist.fill()`; broadcast weights first
- **coffea**: NanoEvents columns are `ak.Array`; all coffea processors consume
  awkward natively

## Reference guide

Load only the reference files that match the task:

- `references/best-practices.md`: use when deciding overall approach — filter
  early, build the EDM with `ak.zip` then add derived fields, and when
  `axis=None` is (and isn't) the right choice for a reducer.
- `references/records.md`: use when combining parallel arrays into a record
  with `ak.zip` or adding a field with `ak.with_field` (it returns a new
  array, it doesn't mutate).
- `references/filtering-aggregation.md`: use when choosing between `ak.sum`,
  `ak.count`, and `ak.num`, or reasoning about `axis=None` reducer behavior.
- `references/sorting.md`: use for `ak.sort` (`ascending=`, per-axis sorting).
- `references/combinatorics.md`: use when building pairwise (`ak.cartesian`)
  or n-way (`ak.combinations`) object combinations before invariant-mass or
  deltaR calculations.
- `references/argmin-argmax.md`: use when selecting the leading/trailing
  object per event with `ak.argmax`/`ak.argmin` (`keepdims=True`) plus
  `ak.firsts`.
- `references/flattening.md`: use for `ak.flatten` axis rules — especially
  the `axis=0` (drops only top-level `None`) vs `axis=1` (removes a list
  level) distinction — and `ak.unflatten`.
- `references/numpy-interop.md`: use when converting to NumPy (`ak.to_numpy`
  regularity requirements, masked-array behavior for `None`) or relying on
  NumPy ufunc dispatch.
- `references/pitfalls.md`: use for missing-function traps (no `ak.abs`,
  `ak.take`, `ak.expand_dims`) and the `ak.from_json` string-vs-path gotcha.
- `references/awkward-files.md`: use for Parquet/JSON I/O patterns, including
  the `ak.from_json` path-vs-string asymmetry.

## Docs

https://awkward-array.org/doc/main/
