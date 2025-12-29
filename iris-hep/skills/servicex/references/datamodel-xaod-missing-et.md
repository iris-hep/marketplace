# xAOD Missing ET

Access:

```python
query = FuncADLQueryPHYS() \
    .Select(lambda e: e.MissingET().First()) \
    .Select(lambda m: {"met": m.met() / 1000.0})
```

Despite being only a single missing ET for the event, it is stored as a sequence. Thus you must get the first object and then access the `.met()` method from there. Note that the missing ET object has `met`, `mpy`, `mpx`, etc. It adds an `m` in front of everything.
