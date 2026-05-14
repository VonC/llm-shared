# Implement step instructions

Include "Step XXXX" in the title of this conversation (replace XXXX with the step mentioned in the prompt, for example '2', for "Step 2 of the CDC gap feature").

Read carefully the markdown files in your context to understand the context.

Based on the design markdown and the plan markdown, follow instructions from [`implement-plan.prompt.md`](../.github/prompts/implement-plan.prompt.md), and implement step XXXX (see your prompt), doing a `check.bat` to see if there is any error or linter warning to fix, then (once there is no more error or warning), doing a `pytest` on new or updated test files to check any new or modified test class passes.

Make sure no new computation would introduce any O(n^2) or O(n log(n)) process.

Make sure DDD-Hexagonal architecture is strictly respected: no violation, no smell.

Make sure no existing feature or reporting capability is impaired.

Each new test must follow the convention `...\tests\unit\xxx\yyy\...\test_filename\test_filename_tdd.py`, and you must check if a pbt is needed as well. And do not forget the `__init__.py` to create or to update, for test and non-test code.

Before writing code, write a short analysis of the issue and a brief description of the implementation. Only then write the code, following the project instructions in `CLAUDE.md` (and `copilot-instructions.md` for Copilot users), which means write the class in full (no "`# ...existing code...`" comment).

Always update the docstring at the very top of the modified classes to explain the fix. That applies to test classes as well.

Preserve existing code and docstrings and comments; only update them to explain and accommodate your implementation. Check if any comment is obsolete considering the current code and remove them. Do not remove comments like `# Act` unless the whole section has been removed as part of your fix. Read and follow instructions from [`preserve_code.md`](../rules/preserve_code.md).

When writing an answer in markdown, follow instructions from [`markdown.md`](../rules/markdown.md).
