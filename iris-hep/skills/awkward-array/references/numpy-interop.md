# NumPy Interop

## Converting to NumPy

`ak.to_numpy(array)` converts to a NumPy array but only succeeds when the data
are numerical and regular (nested lists have equal lengths in each dimension).
Ragged arrays raise an error — flatten or pad first.

```python
import awkward as ak

# Regular works
ak.to_numpy(ak.Array([[1, 2], [3, 4]]))   # shape (2, 2)

# Ragged fails — flatten first
flat = ak.to_numpy(ak.flatten(jets.pt, axis=1))

# Missing values produce a NumPy masked array by default
ak.to_numpy(ak.Array([1, None, 3]))
# allow_missing=False raises instead of masking
```

## NumPy ufuncs

Many NumPy ufuncs dispatch on Awkward arrays automatically:

- `np.sqrt(ak_array)`, `np.log(ak_array)`, etc. work element-wise
- Python builtins `abs()` works (there is no `ak.abs`)
- `np.stack` works when inputs are effectively regular

There is no `ak.stack` or `ak.expand_dims`.
