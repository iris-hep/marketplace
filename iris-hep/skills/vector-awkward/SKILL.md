---
name: vector-awkward
description: >-
  Use when computing 4-vector quantities in Python: invariant mass, deltaR,
  transverse momentum, boost, or any Lorentz vector arithmetic over collections
  of particles. Also use when registering scikit-hep vector behaviors on
  awkward-array records so that ak.zip objects gain Momentum4D methods, or when
  constructing vector objects from (pt, phi, eta, mass) or (px, py, pz, energy)
  field conventions.
---

# Vector

## Overview

The `vector` library provides Lorentz vector arithmetic for NumPy arrays,
awkward-array records, and scalar objects. The key design: register behaviors on
`ak.Array` records once, then use physics methods (`.deltaR()`, `.mass`,
`.boost(...)`) directly without manual kinematic math.

## When to Use

- Computing invariant mass or transverse mass of particle combinations
- Computing deltaR between two objects for overlap removal or matching
- Boosting to the rest frame of a parent particle
- Any operation that would otherwise require manual `px = pt * cos(phi)` etc.

## Key Concepts

| Concept                     | Notes                                                                          |
| --------------------------- | ------------------------------------------------------------------------------ |
| `vector.register_awkward()` | One-time call; mutates global behavior dict — call at module level             |
| Field name conventions      | `pt/phi/eta/mass` OR `px/py/pz/energy` — vector auto-detects                   |
| `Momentum4D`                | The most common type for HEP 4-vectors                                         |
| `.deltaR(other)`            | ΔR = √(Δη² + Δφ²) — available as method after behavior registration            |
| `.mass` property            | Invariant mass from E²-p² = m²                                                 |
| `vector.obj(...)`           | Single scalar Python object — fast in Numba, slow in plain Python loops        |
| `vector.array(...)`         | NumPy structured-array subclass — vectorized, good for fixed-shape collections |
| `vector.zip(...)`           | Like `ak.zip` but auto-sets `with_name`; no need to specify record type        |
| `.to_*()`                   | Explicit coordinate conversion (`to_xyzt`, `to_rhophithetatau`, etc.)          |
| `VectorSympy*D`             | Symbolic vector types (SymPy backend); all operations return SymPy expressions |
| `vector.register_pytree()`  | Returns a pytree interface (flatten/unflatten); requires `optree` package      |

## Canonical Patterns

**Register behaviors (do once at module top)**:

```python
import vector
vector.register_awkward()
```

Alternatively, install behaviors only in a single array without touching global
`ak.behavior`:

```python
import awkward as ak
arr = ak.Array([...], with_name="Momentum4D",
               behavior=vector.backends.awkward.behavior)
```

**Build a Momentum4D record array from NTuple columns**:

```python
import awkward as ak
# vector.zip auto-infers the record name from field names; no with_name needed
jets = vector.zip(
    {"pt": events["jet_pt"], "phi": events["jet_phi"],
     "eta": events["jet_eta"], "mass": events["jet_m"]},
)
# equivalently: ak.zip({...}, with_name="Momentum4D")
# Now jets.deltaR(other), jets.mass, jets.px, etc. all work
```

**Invariant mass of all jet pairs**:

```python
combos = ak.combinations(jets, 2, axis=1)
j1, j2 = ak.unzip(combos)
mjj = (j1 + j2).mass / 1000  # MeV → GeV
```

**Boost to rest frame of a parent**:

```python
# parent must be a vector object
boosted = daughter.boost(-parent.to_beta3())
```

**Explicit coordinate conversion (numerical precision)**:

```python
v = vector.obj(px=3.0, py=4.0, pz=0.0, energy=5.0)
v.pt   # reads rho — no copy, computed on the fly
v2 = v.to_rhophithetatau()  # force storage in a different coordinate system
```

**Scalar Python object (`vector.obj`) — single vector or Numba use**:

```python
v = vector.obj(pt=30.0, phi=0.5, eta=1.2, mass=0.105)  # single muon
print(v.px, v.py, v.pz, v.energy)
```

`vector.obj` returns a plain Python object, not a NumPy array — slow in
Python loops, but compiles efficiently under `@nb.njit` (no advantage for
just a few vectors, though). For NumPy-array, Numba-loop, SymPy-symbolic, or
PyTree/scipy use, see `references/vector-advanced.md`.

## Gotchas

- **`register_awkward()` before any vector access**: Calling `.deltaR()` on an
  `ak.Array` without prior registration raises `AttributeError`. If you see
  this, you forgot the registration call.
- **`vector.obj` is a scalar, not an array**: It represents one vector. For
  arrays of vectors use `vector.array(...)` (NumPy backend) or
  `ak.zip(..., with_name="Momentum4D")` (awkward backend). Lists of `vector.obj`
  are slow in plain Python — use `vector.array` or Numba instead.
- **NumPy backend Numba support is incomplete**: `@nb.njit` works with
  `vector.obj` and `vector.Array` (awkward), but NumPy array (`vector.array`)
  support inside Numba is incomplete (upstream issue [#43]).
- **Multiple spellings are valid for energy and mass** — all four rows below are
  recognized by every backend (objects, NumPy, awkward):

  | temporal coord | synonyms                | notes                          |
  | -------------- | ----------------------- | ------------------------------ |
  | Cartesian time | `t`, `e`, `E`, `energy` | four-momentum energy component |
  | proper time    | `tau`, `m`, `M`, `mass` | invariant mass / proper time   |

  The real constraint is **don't mix coordinate systems**: `pt/phi/eta/energy`
  is fine; `pt` with `px` is not — vector picks the convention from the full set
  of field names and raises if they conflict.

- **SymPy sign convention differs for space-like/negative time-like 4-vectors**:
  The SymPy backend avoids piecewise if-then branches in symbolic expressions,
  so its conventions for such vectors differ from other backends (which follow
  ROOT). For physical momentum vectors (positive time-like), all backends agree.
- **`register_pytree()` requires `optree`**: `optree` is not a default vector
  dependency. Install it separately; `register_pytree()` raises `ImportError`
  without it. Call it once at module level before any flatten/unflatten use.
- **Units are your responsibility**: Vector does no unit conversion. If pT is in
  MeV, masses and energies are in MeV throughout. Divide by 1000 explicitly
  before presenting in GeV.
- **`with_name` is required for ak.zip** to get behavior:
  `ak.zip({...}, with_name="Momentum4D")`. Without it, records are plain dicts.
- **Addition of 4-vectors**: `j1 + j2` returns a new `Momentum4D` vector —
  invariant mass is then `(j1 + j2).mass`.

## Interop

- **awkward**: Required for jagged/variable-length collections;
  `register_awkward()` enables methods on `ak.Array` records
- **uproot**: Fields read from ROOT files usually need renaming to match vector
  conventions
- **hist**: Compute quantities with vector, then flatten and fill `Hist`
- **numpy**: `vector.array(...)` creates NumPy-backed vectors for fixed-shape
  data; vectorized but not suitable for variable-length/jagged structure
- **numba**: `@nb.njit` works with `vector.obj` and `vector.Array` (awkward);
  best for custom loops over large ragged arrays where awkward vectorization
  cannot express the logic
- **sympy**: `VectorSympy2D/3D/4D` and `MomentumSympy2D/3D/4D` give fully
  symbolic coordinate transforms; useful for deriving kinematic formulas and
  code-generating Fortran/C/LaTeX output
- **optree**: `vector.register_pytree()` enables flatten/unflatten of vector
  objects and nested structures containing them; integrates with
  `scipy.integrate`, optimizers, and any algorithm expecting a 1D numeric array

## Reference Material

- `references/vector-hints.md`: use for the baseline
  `ak.zip(..., with_name=...)` record-building pattern, the `deltaR`
  cartesian-pairing recipe, and a pointer to other vector methods like
  `cross`.
- `references/vector-advanced.md`: use when the user needs NumPy-array
  vectors (`vector.array`), Numba-JIT-compiled loops over vector objects,
  symbolic/SymPy vector algebra, or PyTree integration
  (`vector.register_pytree()`) for `scipy`/optimizer workflows.

## Docs

https://vector.readthedocs.io/en/latest/
