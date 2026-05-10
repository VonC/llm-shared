---
name: implementation-check
description: 'Check if a step of a feature has been fully implemented, based on the feature notes and issue notes for that step, and any other relevant context. The step to check is the one mentioned in the prompt, for example "check step 2 implementation of the CDC gap feature".'
user-invocable: true
metadata:
  - "This skill is used to check if a step of a feature has been fully implemented, based on the feature notes and issue notes for that step, and any other relevant context."
  - "The step to check is the one mentioned in the prompt, for example "check step 2 implementation of the CDC gap feature"."
  - "The context that can inform your analysis includes the feature notes and issue notes for that step, as well as any other relevant context in your current conversation and any .md files in your context, and any Git diff `a.diff` present in your context and at the root folder of the project."
  - "When writing an answer in markdown, follow instructions from #file:./markdown.instructions.md"
argument-hint: 'Provide the step XXXX, version and name: for instance, 'step 2 v9.3.0 sentinels'.
---

Your goal is to analyze if the step from the `docs\plan.vX.Y.Z.<topic>.md` plan in your context -- step indicated in your prompt -- has been fully implemented, based on the files present in your context, or based on a Git diff `a.diff` present at the root folder of the project. Write this analysis as a markdown answer, and update `docs\plan.vX.Y.Z.<topic>.validation.md` with that analysis.

Check your prompt and your context for the step to check, for example "step 2 v9.3.0 sentinels", checking if yes or no step XXXXX from `docs\plan.vX.Y.Z.<topic>.md` was fully implemented, and asserting the state of the DDD-Hexagonal architecture (is there any smell or violation?).

Read first the `docs\plan.vX.Y.Z.<topic>.md` plan in your context, and only check the step you were instructed to in the prompt.

Start with a general short confirmation in the first `## Analysis of Step x Implementation` section: yes or no the step has been fully implemented.

- if it is not yet implemented, do not write code, but explain what is missing.
- if it is, do not write code, but write a `## Analysis of Step x Implementation` section in which you summarize the goal and detail the implementation changes done to implement said goal. Detail also any new type or class introduced in the context of said implementation.

Then, in case it is fully implemented, write also a sub-section `### Architecture check for Step x`, in which you assess if you detect any DDD-Hexagonal (adapters-ports) architecture violation or smell, any layer using other layers it should not, or other internal lib it should not. In particular, is there any class which is importing another class it should not (either a layer importing another wrong layer, or importing a technical lib when it should be business-only). Is there any function whose intent should not be in a particular class or layer?

Follow the template defined in [`templates/implementation-step-analysis.template.md`](../../../templates/implementation-step-analysis.template.md).

`a.diff` in your context is updated: do you see any DDD-Hexagonal smell or violation?

Is there any new computation which could be O(n^2) or O(n log n)?

Is there any existing feature or reporting capability impaired?

At the end of the "Architecture check for Step x", add a simple short phrase stating if, yes or no, there is anything possibly needed fixing (architecture smell, or violation, or girth too big, or anything else).  
Again, if anything is mentioned, even "acceptable", even "for later", even if "minor", it counts as "yes, there is something that needs to be addressed". If nothing is mentioned, it counts as "no, there is nothing that needs to be addressed".

At the end of the "Performance check for Step x", add a simple short phrase stating if, yes or no, there is any performance issue that needs to be addressed.

When writing an answer in markdown, follow instructions from [`markdown.instructions.md`](../../markdown.instructions.md).

Note how each list item uses only one space between a list item marker and the list item content: `- **Change 2**: explain ...`, not `-   **Change 2**: explain ...` (3 spaces after the list item marker dash).

Check your answer: do you see list items with 3 spaces as in `-   xxx`? Change them to one space: `- xxx`.
