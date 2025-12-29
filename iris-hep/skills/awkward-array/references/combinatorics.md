# Combinatorics for Multi-Object Quantities

Use combinatorics when you need same-sized arrays for pairwise or n-way calculations.

## ak.cartesian

```python
pairs = ak.cartesian({"m": muons, "e": electrons}, axis=1)
# pairs.m are muons aligned with electrons
```

## ak.combinations

```python
combo = ak.combinations(jets, 3, fields=["j1", "j2", "j3"], axis=1)
# combo.j1, combo.j2, combo.j3 are the three jets per combination
```

Notes:
- Use combinatorics before DeltaR or invariant mass calculations when objects per event are mismatched.
