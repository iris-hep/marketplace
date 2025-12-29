# Best Practices

- Prefer Awkward 2.0 APIs and syntax.
- Filter early: apply event-level cuts before heavy combinatorics or derived calculations.
- Build an event data model (EDM) with `ak.zip`/records, then add derived fields back into the EDM.
- Avoid `axis=None` for Awkward functions; choose a concrete axis deliberately.
