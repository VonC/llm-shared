---
name: implement-step
description: 'Implement a step of a feature, based on the feature notes and issue notes for that step, and any other relevant context. The step to implement is the one mentioned in the prompt, for example "implement step 2 of the CDC gap feature".'
user-invocable: true
metadata:
  - "This skill is used to implement a step of a feature, based on the feature notes and issue notes for that step, and any other relevant context."
  - "The step to implement is the one mentioned in the prompt, for example "implement step 2 of the CDC gap feature"."
  - "The context that can inform your implementation includes the feature notes and issue notes for that step, as well as any other relevant context in your current conversation and any .md files in your context."
  - "Before writing code, write a short analysis of the issue and a brief description of the implementation. Only then write the code, following `copilot-instructions.md` in your project, which means write the class in full (no "`# ...existing code...`" comment)."
  - "Always update the docstring at the very top of the modified classes to explain the fix. That applies to test classes as well."
  - "Preserve existing code and docstrings and comments; only update them to explain and accommodate your implementation. Check if any comment is obsolete considering the current code and remove them. Do not remove comments like `# Act` unless the whole section has been removed as part of your fix. Read and follow instructions from #file:../preserve_code.md ."
  - "When writing an answer in markdown, follow instructions from #file:./markdown.instructions.md"
argument-hint: 'Provide the step XXXX to implement, for example "implement step 2 of the CDC gap feature".'
---

Include "Step XXXX" in the title of this conversation. (replace XXXX with the step mentioned in the prompt, for example '2', for "Step 2 of the CDC gap feature").

Read carefully the markdown files in your context to understand the context.

Based on the design design markdown and the plan markdown, follow instructions from #file:../../prompts/implement-plan.prompt.md , and implement step XXXX (see your prompt), doing a `check.bat` to see if there is any error or linter warning to fix, then (once there is no more error or warning), doing a `pytest` on new or updated test files to check any new or modified test class passes.

Make sure no new computation would introduce any O(n2) or O(nlog(n)) process.

Make sure DDD-Hexagonal architecture is strictly respected: no violation, no smell.

Make sure no existing feature or reporting capability is impaired.

Each new test must follow the convention `...\tests\unit\xxx\yyy\...\test_filename\test_filename_tdd.py` , and you must check if a pbt is needed as well. And do not forget the `__init__.py` to create or to update, for test and non-test code.

