# Awkward Arrays and File I/O

## Reading and writing

- Prefer `awkward`'s built-in I/O functions when available for your format.
- Use `ak.to_parquet` and `ak.from_parquet` for Parquet.
- Use `ak.to_json` and `ak.from_json` for JSON when needed (beware of large
  files).

## Common patterns

```python
import awkward as ak
from pathlib import Path

# Parquet round-trip
ak.to_parquet(array, "data.parquet")
array2 = ak.from_parquet("data.parquet")

# JSON round-trip
ak.to_json(array, "data.json")
array3 = ak.from_json(Path("data.json"))
```

Notes:

- **`from_json` path asymmetry**: `ak.to_json` accepts string paths for output,
  but `ak.from_json` interprets a bare string as JSON content. Pass a
  `pathlib.Path` to read from a file.
- Ensure the format preserves jagged structure.
- For large datasets, prefer columnar formats like Parquet.
