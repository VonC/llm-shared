---
name: implementation-check
description: 'Check whether one plan step is fully implemented, update the validation plan, and when the final step completes a collected effort, mark its matching umbrella row completed with evidence paths. Use when the user asks to check a plan step implementation.'
user-invocable: true
metadata:
  - "This skill is used to check if a step of a feature has been fully implemented, based on the feature notes and issue notes for that step, and any other relevant context."
  - "The step to check is the one mentioned in the prompt, for example "check step 2 implementation of the CDC gap feature"."
  - "The context that can inform your analysis includes the feature notes and issue notes for that step, as well as any other relevant context in your current conversation and any .md files in your context, and any Git diff `a.diff` present in your context and in the review artifact home (`.reviews/a.diff`) of the project."
  - "When writing an answer in markdown, follow instructions from #file:../../../rules/markdown.md"
argument-hint: "Provide the step XXXX, version and name: for instance, 'step 2 v9.3.0 sentinels'."
---

[Instruction](../../../instructions/implementation-check.md)
