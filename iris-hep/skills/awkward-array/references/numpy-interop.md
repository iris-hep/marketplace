# NumPy Interop

- Some NumPy functions dispatch on Awkward arrays when the data are NumPy-like (non-jagged).
- `np.stack` works when the inputs are effectively 2D.
- There is no `ak.stack`.
