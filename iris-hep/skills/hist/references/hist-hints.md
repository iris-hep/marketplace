# Hist (scikit-hep) library code snippets

## Importing

```python
from hist import Hist # To get the histo creating object
```

## Creating a histogram (QuickConstruct)

```python
# Define a 2D histogram: 10 bins in x [0,1), variable bins for y
h = (
    Hist.new.Reg(10, 0, 1, name="x", label="x-axis")
       .Var(range(10), name="y", label="y-axis")
       .Int64()  # use 64-bit integer storage for counts
)
```

The `Reg` method creates a regular (uniform-width) binned axis for the histogram. You specify the number of bins, the lower and upper edges, and optionally the axis name and label. For example, `.Reg(10, 0, 1, name="x", label="x-axis")` creates an axis named "x" with 10 bins from 0 (inclusive) to 1 (exclusive), each bin having equal width.

The `Var` method in the Hist API creates a variable-width binned axis for your histogram. Unlike .Reg, which makes bins of equal width, `Var` lets you specify the exact bin edges, so each bin can have a different width.

Labels can contains `LaTeX` (and should for `eta` ($\eta$) and `pt` ($p_{T}$)). If you are using a f-string or `str.format(...)` that the curly LaTeX braces must be escaped. Make sure you surround the math symbols with `$`!!

The storage type is either `Int64` or `Weight`. If you are doing just counts in the histogram, use `.Int64()`. If you are building a weighted histogram (say with mc weights) then use `.Weight()`. You can use only one of the two. Do not use both - Do not chain Int64 and Weight! You'll get an error ("Hist object has no attribute XXX")

## Filling a histogram with data

```python
# Fill histogram using named axes
h.fill(x=[3, 5, 2], y=[1, 4, 6])
```

Note that `.fill` returns `None`.

## Viewing histogram counts and errors

```python
# Access bin counts and calculate uncertainties
counts = h.view()               # NumPy view of counts in histogram
variances = h.variances()       # Variance of counts in each bin
errors = np.sqrt(variances)     # Standard errors (sqrt of variances)
```

## Indexing a histogram with UHI syntax

```python
# Project and slice using unified histogram indexing (UHI)
h_proj = h.project("x")                      # project onto the x-axis only
value  = h[{"y": 0.5j + 3, "x": 5j}]         # get content at x≈5 and y bin containing 0.5
h_rebin = h[0.3j:, ::2j]                     # x from 0.3 to end, rebin y-axis by factor 2
```

## Creating a multi-axis histogram with categories

```python
# Define a multi-dimensional histogram: one regular axis and several categorical axes
histogram = (
    Hist.new.Reg(25, 50, 550, name="mass", label="Mass [GeV]")   # 25 bins from 50 to 550
       .StrCat(["4j1b", "4j2b"], name="region", label="Region")  # two region categories
       .StrCat([], name="process", label="Process", growth=True) # processes, added as they appear
       .StrCat([], name="variation", label="Systematic variation", growth=True)
       .Weight()  # use weight storage to allow weighted entries
)
```

## Filling a multi-dimensional histogram

```python
# Fill the histogram (e.g., with events from a ttbar process in region "4j2b")
mass_values = [100, 105, 110]  # example mass data
histogram.fill(mass=mass_values, region="4j2b", process="ttbar", variation="nominal", weight=1.0)
```

## Extracting a slice from a multi-dimensional histogram

```python
# Select a specific slice: e.g., the "ttbar" process in region "4j2b" for all mass bins
h_sig = histogram[:, "4j2b", "ttbar", "nominal"]
```

## Plotting a 1D histogram with mplhep style

Use the `fix, ax = plt.subplots()` to create the plots. Use the default `figsize` unless otherwise instructed (e.g. don't specify it). DO NOT Specify a `figsize`! Leave it at the default!

```python
import matplotlib.pyplot as plt
import mplhep as hep
plt.style.use(hep.style.ATLAS)  # use a ATLAS-inspired style for HEP plots

# Plot the 1D slice with filled histogram style
fig, ax = plt.subplots()
histogram.plot(histtype="fill", linewidth=1, edgecolor="gray", label="ttbar")
ax.legend()
ax.set_xlabel("Mass ($m_H$) [GeV]")
ax.set_title("Higgs Mass")
```

* Possible values for `histtype`: fill, step, errorbar, band, bar, barstep. Anything else will cause an error. By default use `fill`.
* Titles and axes labels can contains `LaTeX` (and should for `eta` ($\eta$) and `pt` ($p_{T}$)). If you are using a f-string or `str.format(...)` that the curly LaTeX braces must be escaped.

## Plotting a 2D histogram

```python
import matplotlib.pyplot as plt
import mplhep as hep

fig, ax = plt.subplots()
mplhep.hist2dplot(h)  # display 2D histogram as colormesh
```

## Saving a plot to a file

```python
fig.savefig("histogram.png")
plt.close(fig)
```

* You can also use `fig.savefig(...)`, of course, if you have the `fig` from making sub plots.
* `plt.close(fig)` the figure after saving it to a file to free up memory.
* Do not change the `dpi` with other arguments - just provide the filename argument to `savefig`.

## Notes

* Keep histogram titles short - otherwise they are larger than the histogram itself. For example, don't include the dataset name in the overall plot title (e.g. `plt.title` or `ax.set_title`).
  * Good: "Jet $p_T$
  * Bad: "Jet $p_T$ in Data18 With Eta Cut"
* Place extra information in the legend or write it on the plot somewhere.
