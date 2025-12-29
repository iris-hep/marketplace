# Pitfalls and Gotchas

- `ak.fill_like(array, value)` requires `value` to be numeric.
- Use Python's `abs`; there is no `ak.abs`.
- There is no `ak.take`.
- There is no `ak.expand_dims`.
