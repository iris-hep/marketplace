# {{Analysis/Workflow Name}}

{{Short description of the analysis (no more than 2 lines)}}

## Data Samples

{{List all the data samples that are needed for this work below in the table. If the dataset has been explicitly named, include that too so the information is not lost.}}

| Data Sample | Derivation | Role(s) In Analysis |
| --- | --- | --- |
| {{ds 1}} | {{PHYS/PHYSLITE/LLM1, etc. Leave blank unless told by dataset name or user}} | {{Signal/Background, Control Region, etc.}} |
| {{ds 2}} | {{PHYS/PHYSLITE/LLM1, etc. Leave blank unless told by dataset name or user}} | {{Signal/Background, Control Region, etc.}} |

## Histograms

{{List each histogram that should be produced as a summary histogram. These may be used as input into a statistical analysis or just a cross checks.}}

1. {{Histogram 1 Title}}
    * x Axis
        * {{Detailed description of what should be plotted}}
        * {{Label for axis, including units if unit-full quantity (e.g. `$p_T$ [GeV]`, or `$\eta$`) - use LaTeX formatting for labels}}}
        * {{Info on binning and axis limits if specified by user. Leave blank unless given explicit instructions.}}
        * {{Info on how many entries per event, or per combination in an event, etc.}}
    * {{List other axes here}}
2. {{Histogram 2 Title}}
    * x Axis
        * ...

## Analysis Steps

{{Turning the event data into the histogram often requires complex manipulations. If any high level manipulations are required, they should be listed here. They should be broken down into reusable calculations as makes most sense.}}

1. {{Selection}}
    * {{What event level or object level cuts are getting applied}}
1. {{Variable Name}}
    * {{Calculated}}
    * {{Combinatorics should be mentioned explicitly - in particular when trying to select the best combination.}}
1. {{Repeat the above steps as needed}}
    * ...

## Workflow

{{List the steps that are required to process the files to put together the final set of histograms. Below are the most common steps, but it would make sense to add others (for example, training ML)}}

1. Data Extraction and NTuple Skimming
    * {{Filtering: What event/objects filtering can be done at the source data file level. For example, you'll never need to look at events with less than 3 jets. This reduces storage for the work, and storage is one of the most expensive items. Explicitly say `No Filtering` if none is called for.}}
    * {{List of variables that should be extracted from the data and passed downstream.}}
2. Data Analysis & Histogramming
    * {{What new variables should be constructed from what was read from the input files in step 1.}}
    * {{Work here should include any combinatorics building, high level event filtering, etc.}}
    * {{The above variables should be used to directly fill the requested histograms.}}

{{If systematic errors are to be taken into account, that likely means all the above steps have to be repeated for each systematic error. Make a note here if this is the case - don't say anything if systematic errors aren't needed.}}

## Statistical Analysis

{{List the statistical analysis (if any) that needs to be done on the previous data}}

## Tools

{{This section is a series of bullet points giving some guidance to the tools that should be used to accomplish previous parts.}}

* {{tool 1}}
  * {{Any comments about its usage}}
* {{Tool 2}}
  * ...
