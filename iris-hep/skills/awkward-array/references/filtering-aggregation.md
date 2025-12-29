# Filtering and Aggregation

## Filtering

- Filtering uses NumPy-like boolean masks.
- The mask structure must match the array being masked.

## Aggregation operations

- `ak.sum`: sum over an `axis`.
- `ak.count`: count non-empty elements along an `axis` (counts values).
- `ak.num`: count slots (like `len`), independent of empties.

Notes:
- There is no `ak.max` or `ak.min`; use Python's `max`/`min` if needed.
- Do not pass `None` for `axis` in Awkward functions.
