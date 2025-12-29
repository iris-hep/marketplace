# Records and Fields

## Combine parallel arrays with ak.zip

```python
import awkward as ak

ages = ak.Array([18, 32, 41])
names = ak.Array(["Dorit", "Caitlin", "Bryn"])
people = ak.zip({"age": ages, "name": names})
print(ak.to_list(people))
# [{'age': 18, 'name': 'Dorit'}, {'age': 32, 'name': 'Caitlin'}, {'age': 41, 'name': 'Bryn'}]
```

## Add a field with ak.with_field

```python
import awkward as ak

arr = ak.Array([{"x": 1, "y": 2}, {"x": 3, "y": 4}])
new_field_values = ak.Array([100, 200])
arr_with_z = ak.with_field(arr, new_field_values, where="z")
print(ak.to_list(arr_with_z))
# [{'x': 1, 'y': 2, 'z': 100}, {'x': 3, 'y': 4, 'z': 200}]
```

Notes:
- `ak.with_field` returns a new array; it does not mutate in place.
- `arr["newfield"] = values` uses `ak.with_field` internally.
