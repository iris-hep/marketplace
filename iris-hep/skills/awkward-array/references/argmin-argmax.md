# argmin/argmax on Jagged Arrays

Use `keepdims=True` to preserve list structure for slicing.

```python
import awkward as ak

array = ak.Array([[7, 5, 7], [], [2], [8, 2]])
max_values = ak.argmax(array, axis=1, keepdims=True)
print(max_values)               # [[0], [None], [0], [0]]
print(array[max_values])        # [[7], [None], [2], [8]]
print(ak.flatten(array[max_values], axis=0))  # [7, None, 2, 8]
```

After slicing with argmin/argmax:
- Use `ak.flatten(..., axis=0)` to remove the extra list level, or
- Use `ak.firsts` to extract the first element per list.
