# Awkward Arrays and File I/O

## Reading and writing

- Prefer `awkward`'s built-in I/O functions when available for your format.
- Use `ak.to_parquet` and `ak.from_parquet` for Parquet.
- Use `ak.to_json` and `ak.from_json` for JSON when needed (beware of large files).

## Common patterns

```python
import awkward as ak

# Parquet round-trip
ak.to_parquet(array, "data.parquet")
array2 = ak.from_parquet("data.parquet")

# JSON round-trip
ak.to_json(array, "data.json")
array3 = ak.from_json("data.json")
```

Notes:

- Ensure the format preserves jagged structure.
- For large datasets, prefer columnar formats like Parquet.
