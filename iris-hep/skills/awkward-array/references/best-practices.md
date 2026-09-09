# Best Practices

- Prefer Awkward 2.0 APIs and syntax.
- Filter early: apply event-level cuts before heavy combinatorics or derived
  calculations.
- Build an event data model (EDM) with `ak.zip`/records, then add derived fields
  back into the EDM.
- `axis=None` is valid for reducers and `ak.flatten`, but it collapses all
  structure — choose a concrete axis deliberately to preserve per-event
  semantics.
