---
name: implementation-check
description: 'Check if a step of a feature has been fully implemented, based on the feature notes and issue notes for that step, and any other relevant context. The step to check is the one mentioned in the prompt, for example "check step 2 implementation of the CDC gap feature".'
user-invocable: true
argument-hint: "Provide the step XXXX, version and name: for instance, 'step 2 v9.3.0 sentinels'."
---

Follow instructions from [`check-plan-implementation.prompt.md`](../../../.github/prompts/check-plan-implementation.prompt.md) and update `docs\plan.vX.Y.Z.xxx.implementation.md`, checking if yes or no step XXXXX from `docs\plan.vX.Y.Z.xxx.md` was fully implemented, and asserting the state of the DDD-Hexagonal architecture (is there any smell or violation?).

Look for your prompt and your context to find the step to check, for example "step 2 v9.3.0 sentinels", and check if it is fully implemented based on the files in your context and the Git diff `a.diff` in your context.

`a.diff` in your context is updated: do you see any DDD-Hexagonal smell or violation?

Is there any new computation which could be O(n2) or O(nlog(n))?

Is there any existing feature or reporting capability impaired?

At the end of the "Architecture check for Step x", add a simple short phrase stating if, yes or no, there is anything possibly needed fixing (architecture smell, or violation, or girth too big, or anything else).  
Again, if anything is mentioned, even "acceptable", even "for later", even if "minor", it counts as "yes, there is something that needs to be addressed". If nothing is mentioned, it counts as "no, there is nothing that needs to be addressed".

At the end of the "Performance check for Step x", add a simple short phrase stating if, yes or no, there is any performance issue that needs to be addressed.

When writing an answer in markdown, follow instructions from [`markdown.instructions.md`](../../markdown.instructions.md).
