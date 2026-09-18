# Vector advanced backends: NumPy, Numba, SymPy, PyTree

These are optional, less-common ways to use `vector` beyond the standard
awkward-array workflow. Each depends on an extra package not required by the
base `vector` install.

## NumPy structured array (`vector.array`) — fixed-shape collections

```python
import numpy as np
# vector.array wraps np.ndarray with vector methods via structured dtype
muons = vector.array(
    {"pt": np.array([30.0, 45.0]), "phi": np.array([0.5, -1.2]),
     "eta": np.array([1.2, -0.8]), "mass": np.full(2, 0.105)}
)
print(muons.px, muons.energy)  # vectorized, operates on whole array
```

## Numba-compiled loop over awkward arrays — best for large ragged collections

```python
import numba as nb
import numpy as np

@nb.njit
def sum_mass(array):
    out = np.empty(len(array), np.float64)
    for i, event in enumerate(array):
        total = vector.obj(px=0.0, py=0.0, pz=0.0, E=0.0)
        for vec in event:
            total = total + vec
        out[i] = total.mass
    return out

# array is a vector.Array (awkward) with Momentum4D records
masses = sum_mass(array)
```

JIT compilation has a cold-start cost but can be significantly faster on large
arrays; actual speedups depend on workload, hardware, and versions. NumPy
array (`vector.array`) support inside Numba is incomplete (upstream issue
[#43]); `vector.obj` and `vector.Array` (awkward) work.

## Symbolic vectors with SymPy — derive formulas or generate code

```python
import sympy

# Symbols must be declared real=True; complex assumptions break trig simplifications
x, y, z, t = sympy.symbols("x y z t", real=True)

v = vector.VectorSympy4D(x=x, y=y, z=z, t=t)
v.rho            # sqrt(x**2 + y**2)
v.is_timelike()  # t**2 - x**2 - y**2 - z**2 > 0

expr = v.boost(v.to_beta3()).t
expr.simplify()                       # returns simplified SymPy expression
expr.subs({x: 3, y: 2, z: 1, t: 10}) # substitute concrete values

# Convert to Fortran/C/LaTeX for downstream use
import sympy.printing.fortran
print(sympy.printing.fortran.fcode(expr.simplify()))
```

The SymPy backend avoids piecewise if-then branches in symbolic expressions,
so its sign convention for space-like/negative time-like 4-vectors differs
from other backends (which follow ROOT). For physical momentum vectors
(positive time-like), all backends agree.

## PyTree integration — flatten vector state for scipy/optree algorithms

```python
# Requires: pip install optree
pytree = vector.register_pytree()  # one-time call; returns flatten/unflatten interface

state = {
    "position": vector.obj(x=1.0, y=2.0, z=3.0, t=0.0),
    "momentum": vector.obj(x=0.0, y=10.0, z=0.0, t=14.0),
}
flat, treedef = pytree.flatten(state)   # flat is a plain list of 8 scalars
reconstructed = pytree.unflatten(treedef, flat)  # round-trips exactly

# Typical use: wrap scipy.integrate.solve_ivp so the integrator sees a 1D array
def wrapped_solve(fun, t_span, y0, t_eval):
    flat_y0, treedef = pytree.flatten(y0)
    def flat_fun(t, flat_y):
        state = pytree.unflatten(treedef, flat_y)
        dstate_dt = fun(t, state)
        flat_dstate_dt, _ = pytree.flatten(dstate_dt)
        return flat_dstate_dt
    from scipy.integrate import solve_ivp
    sol = solve_ivp(flat_fun, t_span, flat_y0, t_eval=t_eval)
    return pytree.unflatten(treedef, sol.y)
```

`optree` is not a default `vector` dependency — install it separately;
`register_pytree()` raises `ImportError` without it. Call it once at module
level before any flatten/unflatten use.
