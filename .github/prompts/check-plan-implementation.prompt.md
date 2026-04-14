---
agent: ask
description: 'Check a development plan step implementation.'
---

Your goal is to analyze if the step from the `plan.vX.Y.Z.xxx.md` markdown plan in your context -- step indicated in your prompt -- has been fully implemented, based on the files present in your context, or based on a Git diff `a.diff` present in your context and at the root folder of the project. You need to write this analysis as a markdown answer, respecting instructions from #file:../markdown.instructions.md .

Again, read first the  `plan.vX.Y.Z.xxx.md` markdown plan in your context, and only check the step you will be instructed to in the prompt.

Start with a general short confirmation in the first `## Analysis of Step x Implementation` section: yes or no the step has been fully implemented.

- if it is not yet implemented, do not write code, but explain what is missing
- if it is, do not write code, but write a `## Analysis of Step x Implementation` section in which you summarize the goal and detail the implementation changes done to implement said goal.  
  Detail also any new type or class introduced in the context of said implementation.

Then, in case it is fully implemented, write also a sub-section `### Architecture check for Step x`, in which you assess if you detect any DDD-Hexagonal (adapters-ports) architecture violation or smell, any layer using other layers it should not, or other internal lib it should not. In particular, is there any class which is importing another class it should not (either a layer importing another wrong layer, or importing a technical lib when it should be business-only). Is there any function whose intent should not be in a particular class or layer?

So the full structure of your analysis must be:

```md
## Analysis of Step x Implementation

Yes/No Step x has been or has not been fully implemented

### Goal for Step x

The goal of Step x was ...

### What was implemented for Step x

The changes in the provided diff fully implement this step:

- **Change 1**: explain how it participate to implement said step
- **Change 2**: explain how it participate to implement said step
- ...

### New types/classes introduced for Step x

- `aNewClass`: short description

### Architecture check for Step x

- **XXX Layer**: explain how there is no violation (or, on the contrary, highlight smells and violation)
- **YYY Layer**: explain how there is no violation (or, on the contrary, highlight smells and violation)

Short conclusion on the state of the architecture after this step x implementation.
```

You write a markdown document, so respect instructions for markdown lists in #file:./../markdown.instructions.md .

Note how each list item uses only one space between a list item marker and the list item content: `- **Change 2**: explain ...`, not `-   **Change 2**: explain ...` (3 spaces after the list item marker dash).

Check your answer: do you see list items with 3 spaces as in `-   xxx`? Change them to one space: `- xxx`
