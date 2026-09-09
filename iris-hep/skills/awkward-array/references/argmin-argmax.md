# argmin/argmax on Jagged Arrays

Use `keepdims=True` to preserve list structure for slicing.

```python
import awkward as ak

array = ak.Array([[7, 5, 7], [], [2], [8, 2]])  # type='4 * var * int64'
max_values = ak.argmax(array, axis=1, keepdims=True)  # type='4 * 1 * ?int64'
print(max_values)               # [[0], [None], [0], [0]]
print(array[max_values])        # [[7], [None], [2], [8]] type='4 * var * ?int64'
print(ak.firsts(array[max_values]))  # [7, None, 2, 8]
```

After slicing with argmin/argmax:

- Use `ak.firsts` to extract the single element per sublist (returns `None` for
  empty events — the safe default).
- Alternatively, `ak.flatten(..., axis=1)` removes the extra list level and
  returns `[7, None, 2, 8]` of type `4 * ?int64`.
