# Hist advanced notes

## 1) UHI indexing and rebinning

- Use complex numbers for bin selection (e.g., `5j` selects the bin containing 5).
- Use complex ranges for slices (e.g., `0.3j:`).
- Rebin with a complex step (e.g., `::2j` rebins by 2).
- Project with `h.project("axis_name")` to reduce dimensionality.

Example:

```python
h_proj = h.project("x")
value = h[{"y": 0.5j + 3, "x": 5j}]
h_rebin = h[0.3j:, ::2j]
```

## 2) Plotting conventions

- Use `plt.subplots()` without specifying `figsize` unless explicitly requested.
- Use `hist.plot(histtype="fill")` for 1D; allowed `histtype` values are
  `fill`, `step`, `errorbar`, `band`, `bar`, `barstep`.
- Use `mplhep.hist2dplot(h)` for 2D plots.

## 3) Label and LaTeX gotchas

- Wrap math in `$...$` and escape braces in f-strings or `.format(...)`.
- Prefer short titles; move extra info into legends or annotations.

## 4) Storage and weights

- Choose exactly one: `.Int64()` for counts or `.Weight()` for weighted fills.
- Expect an attribute error if you attempt to chain both.

## 5) Categorical axes

- Use `StrCat([...])` for fixed categories.
- Use `StrCat([], growth=True)` to add categories on the fly.
