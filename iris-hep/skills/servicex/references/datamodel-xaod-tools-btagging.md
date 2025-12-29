# xAOD Tool Access and B-Tagging

Tools are C++ objects used by the framework that is actually extracting the data for servicex. The code is written by the ATLAS experiment. Helper functions are created by two methods,

- `make_a_tool` - defines the tool and schedules it to run in the C++ framework during the servicex translation.
- `make_tool_accessor` defines a small light-weight function in C++ that will return a value from the tool.

These are defined in the `xaod_hints` module if you need to define special tools from user instructions. In many cases you find tool helpers. Examples below show you how to use these functions.

Whenever you use these tool helpers, copy `xaod_hints.py` from the skill assets into the user's package source directory so imports work:

```bash
cp /home/gwatts/code/llm/skill-test/.codex/skills/servicex/assets/xaod_hints.py /path/to/your/package/
```

## BTaggingSelectionTool: getting jet b-tagging results

The `BTaggingSelectionTool` tool gets either a tag weight/discriminant for b-or-charm tagging or a tagged/not-tagged result for a working point. The working points are provided by the FTAG group in ATLAS.

Working Point Info:

- Working point names: `FixedCutBEff_65`, `FixedCutBEff_70`, `FixedCutBEff_77`, `FixedCutBEff_85`, `FixedCutBEff_90`
- [Further information for user](https://ftag.docs.cern.ch/recommendations/algs/r22-preliminary/#gn2v01-b-tagging)
- By default choose the `FixedCutBEff_77` working point.
- Make sure to let the user know what operating point in your text explanation.

To define the tool you must:

```python
query = FuncADLQueryPHYSLITE()
```

Make sure the `{tool_name}` is different if you need to define multiple tools (because user needs more than one operating point). Name them something reasonable so the code makes sense.

```python
# Specific for the below code
from func_adl_servicex_xaodr25.xAOD.jet_v1 import Jet_v1
from xaod_hints import make_a_tool, make_tool_accessor

# Define the tool. This passes `init_lines` for Run 3.
query_base, tag_tool_info = make_a_tool(
    physlite,
    "{tool_name}",
    "BTaggingSelectionTool",
    include_files=["xAODBTaggingEfficiency/BTaggingSelectionTool.h"],
    init_lines=[
        # Use this line no matter open data or ATLAS data
        'ANA_CHECK(asg::setProperty({tool_name}, "OperatingPoint", "FixedCutBEff_77"));',

        # Uncomment the next 3 lines if you are running on ATLAS OpenData only
        # 'ANA_CHECK(asg::setProperty({tool_name}, "TaggerName", "DL1dv01"));',
        # 'ANA_CHECK(asg::setProperty({tool_name}, "FlvTagCutDefinitionsFileName", "xAODBTaggingEfficiency/13TeV/2022-22-13TeV-MC20-CDI-2022-07-28_v1.root"));',

        # This line must be run last no matter what type of data you are running on
        "ANA_CHECK({tool_name}->initialize());",
    ],
    link_libraries=["xAODBTaggingEfficiencyLib"],
)

# If you need the tag weight. Tag weights, output of a GNN, are between -10 and 15.
tag_weight = make_tool_accessor(
    tag_tool_info,
    function_name="tag_weight",
    # false in next line for b-tagging weight, true for c-tagging weight
    source_code=["ANA_CHECK({tool_name}->getTaggerWeight(*jet, result, false));"],
    arguments=[("jet", Jet_v1)],
    return_type_cpp="double",
    return_type_python="float",
)

# If you need to know if a jet is tagged or not.
jet_is_tagged = make_tool_accessor(
    tag_tool_info,
    function_name="jet_is_tagged",
    source_code=[
        "result = static_cast<bool>({tool_name}->accept(*jet));"
    ],
    arguments=[("jet", Jet_v1)],
    return_type_cpp="bool",
    return_type_python="bool",
)
```

Usage of `jet_is_tagged` in `func_adl` is straight forward:

```python
query = (query_base
    .Select(lambda e: e.Jets().Select(lambda j: jet_is_tagged(j)))
```

Make sure to use `base_query` here: the `make_a_tool` must have been called on the query first.

You must uncomment one set or the other of the initialization lines in the code. Look for the comment about uncommenting the proper code. It will not work otherwise.
