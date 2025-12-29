# xAOD Taus

Load `references/datamodel-xaod-objects.md` alongside this file for shared object access patterns.

Tau jets use a different accessor name:

```python
query = FuncADLQueryPHYS() \
    .Select(lambda e: e.TauJets("AnalysisTauJets")) \
    .Select(lambda taus: {
        "pt": taus.Select(lambda t: t.pt() / 1000.0),
        "eta": taus.Select(lambda t: t.eta() / 1000.0),
    })
```
