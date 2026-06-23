---
name: implement-step
description: 'Implement a step of a feature, based on the feature notes and issue notes for that step, and any other relevant context. The step to implement is the one mentioned in the prompt, for example "implement step 2 of the CDC gap feature".'
user-invocable: true
metadata:
  - "This skill is used to implement a step of a feature, based on the feature notes and issue notes for that step, and any other relevant context."
  - 'The step to implement is the one mentioned in the prompt, for example "implement step 2 of the CDC gap feature".'
  - "The context that can inform your implementation includes the feature notes and issue notes for that step, as well as any other relevant context in your current conversation and any .md files in your context."
  - 'Before writing code, write a short analysis of the issue and a brief description of the implementation. Only then write the code, following `copilot-instructions.md` in your project, which means write the class in full (no "`# ...existing code...`" comment).'
  - "Always update the docstring at the very top of the modified classes to explain the fix. That applies to test classes as well."
  - "Preserve existing code and docstrings and comments; only update them to explain and accommodate your implementation. Check if any comment is obsolete considering the current code and remove them. Do not remove comments like `# Act` unless the whole section has been removed as part of your fix. Read and follow instructions from #file:../../../rules/preserve_code.md ."
  - "When writing an answer in markdown, follow instructions from #file:../../../rules/markdown.md"
argument-hint: 'Provide the step XXXX to implement, for example "implement step 2 of the CDC gap feature".'
---

[Instruction](../../../instructions/implement-step.md)
