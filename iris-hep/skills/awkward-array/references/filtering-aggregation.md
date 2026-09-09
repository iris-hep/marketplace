# Filtering and Aggregation

## Filtering

- Filtering uses NumPy-like boolean masks.
- The mask structure must match the array being masked.

## Aggregation operations

- `ak.sum`: sum over an `axis`.
- `ak.count`: count non-empty elements along an `axis` (counts values).
- `ak.num`: count slots (like `len`), independent of empties.

Notes:

- `ak.max` and `ak.min` exist as reducers; pass `axis=` to control the reduction
  axis. `axis=None` flattens everything and returns a scalar.
- `axis=None` is valid for all reducers (`ak.sum`, `ak.max`, `ak.min`, `ak.any`,
  `ak.all`) and `ak.flatten`, but it collapses all structure — choose a concrete
  axis deliberately to preserve per-event semantics.
