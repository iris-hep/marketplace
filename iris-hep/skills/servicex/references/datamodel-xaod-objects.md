# xAOD Objects: Jets, Muons, Photons, Electrons

It is possible to access all these objects from the top event level, e.g.,

```python
query = FuncADLQueryPHYS() \
    .Select(lambda e: e.Jets()) \
    .Select(lambda jets: {
        "pt": jets.Select(lambda j: j.pt() / 1000.0),
        "eta": jets.Select(lambda j: j.eta() / 1000.0),
    })
```

These objects all have `pt`, `eta`, `phi` (with methods by those names). To access `px`, `py`, `pz` you have to get the 4-vector first:

```python
query = FuncADLQueryPHYS() \
    .Select(lambda e: e.Jets()) \
    .Select(lambda jets: {
        "pt": jets.Select(lambda j: j.p4().px() / 1000.0),
    })
```
