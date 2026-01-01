Delegate to the atlas-analysis-planner agent with the following task:

**Analysis Request:**
$ARGUMENTS

**Agent Instructions:**
- Interpret this as an ATLAS physics-analysis task in the IRIS-HEP context

The agent will use the Task tool with subagent_type='iris-hep:atlas-analysis-planner' to delegate this analysis planning request.

It will output the analysis specification as a file called `specification.md`

Do not attempt to write any code.
