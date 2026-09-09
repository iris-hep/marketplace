# Flattening

Always specify `axis` explicitly.

```python
import awkward as ak

array = ak.Array([[0, 1, 2], [], [3, 4], [5, 6, 7]])
flat_level1 = ak.flatten(array, axis=1)   # [0, 1, 2, 3, 4, 5, 6, 7]
flat_all = ak.flatten(array, axis=None)   # same here, but drops structure
```

## axis=0 special behavior

`axis=0` does not remove a list level — it only removes `None` values at the top
level. This is a common source of bugs when flattening argmax/argmin results.

```python
# axis=0 removes top-level None only
array = ak.Array([[1.1, 2.2], None, [3.3], [], [4.4]])
ak.flatten(array, axis=0)   # [[1.1, 2.2], [3.3], [], [4.4]]

# axis=1 removes one list level (and drops None sublists)
ak.flatten(array, axis=1)   # [1.1, 2.2, 3.3, 4.4]
```

## Unflattening

`ak.unflatten` rebuilds nested structure from a flat array and a counts array.

```python
flat = ak.Array([1, 2, 3, 4, 5])
counts = ak.Array([2, 0, 3])
ak.unflatten(flat, counts, axis=0)   # [[1, 2], [], [3, 4, 5]]
```
