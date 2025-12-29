# Flattening

Always specify `axis` explicitly.

```python
import awkward as ak

array = ak.Array([[0, 1, 2], [], [3, 4], [5, 6, 7]])
flat_level1 = ak.flatten(array, axis=1)
flat_all = ak.flatten(array, axis=None)
```

Notes:
- `axis=None` completely flattens the array.
- `axis=1` requires at least one level of nesting.
