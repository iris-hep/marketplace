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

**All unique pairs per event**:

```python
combos = ak.combinations(jets, 2, axis=1)
j1, j2 = ak.unzip(combos)
```

**Leading object per event (keepdims is required for slicing)**:

```python
lead_idx = ak.argmax(jets.pt, axis=1, keepdims=True)
lead = ak.firsts(jets[lead_idx])   # None for empty events
```

**Add a derived field**:

```python
jets = ak.with_field(jets, jets.pt / 1000, "pt_gev")
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

## Docs

https://awkward-array.org/doc/main/
