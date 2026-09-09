---
name: hist
description: >-
  Use when creating, filling, slicing, or plotting histograms with the
  scikit-hep hist library: defining axes (Regular, Variable, StrCategory),
  filling with weighted data, using UHI indexing (loc, rebin, sum), applying
  mplhep ATLAS style, producing ratio panels for data/MC comparisons, or
  projecting multi-dimensional histograms.
---

# Hist

## Overview

`hist` is the scikit-hep histogram library built on top of `boost-histogram`. It
provides a `Hist` class with named axes, Unified Histogram Indexing (UHI),
direct plotting via `mplhep`, and easy conversion to pyhf workspaces. Always use
`Hist` (not raw `bh.Histogram`) for analysis work.

## When to Use

- Building any 1D or 2D histogram in a Python analysis
- Filling histograms from awkward or numpy arrays (with or without weights)
- Plotting with ATLAS style (`mplhep.style.ATLAS`)
- Slicing, rebinning, or summing axes before plotting
- Converting to pyhf workspace JSON via `cabinetry`

## Key Concepts

| Axis type                                             | Use case                           |
| ----------------------------------------------------- | ---------------------------------- |
| `hist.axis.Regular(n, lo, hi, name=..., label=...)`   | Uniform binning                    |
| `hist.axis.Variable([edges], name=..., label=...)`    | Non-uniform bins                   |
| `hist.axis.StrCategory([...], name=..., growth=True)` | String labels (regions, samples)   |
| `hist.axis.IntCategory([...], name=...)`              | Integer labels (run numbers, etc.) |

UHI indexing: `h[loc(val)]` selects by value; `h[::rebin(2)]` rebins by 2;
`h[sum]` sums over an axis.

## Canonical Patterns

**Create and fill a 1D histogram**:

```python
import hist, numpy as np
h = hist.Hist(hist.axis.Regular(50, 0, 500, name="pt", label=r"$p_T$ [GeV]"))
h.fill(pt=jet_pts_gev, weight=event_weights)
```

**2D histogram**:

```python
h2 = hist.Hist(
    hist.axis.Regular(50, 0, 500, name="pt", label=r"$p_T$ [GeV]"),
    hist.axis.Regular(30, -3, 3, name="eta", label=r"$\eta$"),
)
h2.fill(pt=jet_pts, eta=jet_etas)
```

**UHI slicing — select a range and rebin**:

```python
h_central = h[100j:400j]      # values between 100 and 400 (j suffix = value not index)
h_coarse  = h[::hist.rebin(2)]  # rebin by factor 2
```

**Project a 2D histogram**:

```python
h_pt_only = h2.project("pt")   # marginalise over eta
```

**Plot with ATLAS style**:

```python
import matplotlib.pyplot as plt, mplhep
mplhep.style.use("ATLAS")
fig, ax = plt.subplots()
h.plot1d(ax=ax)
ax.set_xlabel(r"$p_T$ [GeV]")
fig.savefig("jet_pt.pdf")
```

**Data/MC ratio panel**:

```python
fig, (ax_main, ax_ratio) = plt.subplots(
    2, 1, gridspec_kw={"height_ratios": [3, 1]}, sharex=True
)
mplhep.histplot(h_mc, ax=ax_main, label="MC", histtype="fill")
mplhep.histplot(h_data, ax=ax_main, label="Data", histtype="errorbar")
ratio = h_data.values() / h_mc.values()
ax_ratio.axhline(1, color="black", linewidth=0.8)
ax_ratio.plot(h_mc.axes[0].centers, ratio, "k.")
ax_ratio.set_ylim(0.5, 1.5)
ax_ratio.set_ylabel("Data / MC")
fig.savefig("jet_pt_ratio.pdf")
```

**Sum over a flow-aware axis**:

```python
total = h[hist.sum]        # sum all bins including overflow
no_overflow = h[1:-1].sum()  # sum without overflow bins
```

## Gotchas

- **`flow=True` vs `flow=False`**: `Regular` axes have overflow/underflow by
  default; `.values()` excludes them, `.values(flow=True)` includes them. `sum`
  in UHI includes flow by default.
- **Fill kwargs must match axis names**: `h.fill(pt=arr)` requires the axis was
  named `"pt"`. Positional filling (`h.fill(arr)`) works for single-axis
  histograms only.
- **Weight keyword**: Always `weight=`, not a positional argument.
- **`plot1d` vs `mplhep.histplot`**: `h.plot1d()` is a convenience wrapper;
  `mplhep.histplot(h)` gives more control. For ratio panels, use
  `mplhep.histplot` directly.
- **Modifying filled histograms**: `Hist` objects are mutable; `h += other_h`
  accumulates fills from multiple chunks.
- **pT axes in GeV not MeV**: Divide by 1000 before filling if your NTuples
  store MeV.

## Interop

- **awkward**: `ak.to_numpy(ak.flatten(arr))` → feed directly to `.fill()`
- **pyhf / cabinetry**: build templates and a workspace with
  `cabinetry.templates.build()` / `cabinetry.workspace.build()`; cabinetry reads
  ROOT histograms via its `contrib.histogram_reader`
- **mplhep**: `mplhep.style.use("ATLAS")` sets ATLAS plot style; all `histplot`
  calls accept `Hist` natively
- **numpy**: `h.values()` returns a numpy array; `h.axes[i].centers` gives bin
  centers

## Docs

https://hist.readthedocs.io/en/latest/
