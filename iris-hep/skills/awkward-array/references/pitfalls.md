# Pitfalls and Gotchas

- `ak.full_like(array, value)` requires `value` to be coercible to the array's
  dtype.
- Use Python's `abs()`; there is no `ak.abs`.
- There is no `ak.take`.
- There is no `ak.expand_dims`.
- `ak.from_json("file.json")` parses the string as JSON content, not a file
  path. Use `ak.from_json(Path("file.json"))` to read from a file. `ak.to_json`
  does not have this asymmetry — it accepts string paths.
