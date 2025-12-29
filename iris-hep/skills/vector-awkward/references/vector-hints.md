# Vector + Awkward Array Reference

Some additional details beyond the simplest uses of `vector`.

## Registering Awkward Behaviors

Always call `vector.register_awkward()` once at the start of a session so Awkward
records named `Vector2D`, `Vector3D`, `Vector4D`, `Momentum3D`, `Momentum4D`, etc.
pick up vector methods and properties.

```python
import vector
vector.register_awkward()
```

## Building Vector Records with ak.zip

Use `ak.zip` with `with_name` to tag records so vector behavior applies. Use standard
field names so vector can infer coordinates.

```python
import awkward as ak

events = ak.Array({
    "electron": ak.zip(
        {"pt": [50.0, 30.2], "eta": [1.4, -0.8], "phi": [2.1, 0.5], "mass": [0.0005, 0.0005]},
        with_name="Momentum4D",
    )
})
```

- Use `Momentum3D` for spatial calculations like deltaR.
- Use `Momentum4D` for invariant mass or boosts.
- Alternate field sets like `px`, `py`, `pz`, `E` also work.

## deltaR Between Collections

Use `ak.cartesian` or `ak.combinations` to form pairs, then call `deltaR`:

```python
pairs = ak.cartesian([events.electron, events.muon])
electrons, muons = ak.unzip(pairs)
dR = electrons.deltaR(muons)
```

Both inputs must be vector-behaving arrays with compatible lengths.

## Other Methods

Vector provides many methods such as `cross` for cross products and other geometric
operations. Refer to vector API docs for the full list when needed.
