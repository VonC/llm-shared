# Split large file or class

Your goal is to split the file or class file mentioned in the prompt and present in your context.
Split by responsibilities 'xxx' identified in the file or class, and create for each responsibility a new file named with the original name plus `_xxx` (for example, if the original file is `foo.py` and you identify a responsibility 'bar', you will create a new file named `foo_bar.py`). The goal is to make it more SOLID (mostly on the "Single Responsibility Principle" side) and to avoid big files. A file is considered big when it has more than 650 lines of code, but to be safe, you should aim for files with less than 550 lines of code after the split, to leave room for future evolutions without risking to exceed the 650 line limit.

That class is too big or does too many things.

- If it is not a test class, you must refactor it by splitting it into several smaller classes, each with a single responsibility. Each class must be in its file, same name plus `_xxx`, with `xxx` being one of the responsibilities identified in the original class.
- If it is a test class, you must split it into many smaller test classes, each testing the same original class. Each test class must be in its file. Keep the `_tdd.py` or `_pbt.py` suffix for test files, and do not forget the `__init__.py` to create or to update, for test and non-test code. Do precede that suffix with `_xxx`, `xxx` being one of the responsibilities identified in the original test class.

The goal is to have smaller classes, in smaller files, each with a single responsibility. The original file must be split into many smaller files. Depending on your design, the original file and class can remain (but smaller, with a single responsibility) or be removed (if it had no single responsibility).

Decide what to do with the original file:

- simple shell documenting the split.
- a hub calling the other split files.

Always update the `__init__.py` file (if found in the same folder as the file being split).

If the original file remains, make sure to trim each docstring to remove obsolete or redundant elements. I need fewer lines. Preserve comments. Preserve function docstrings with their `Args`: do not remove `Args:` documentation.

First, read your instructions (`CLAUDE.md` in your project; `copilot-instructions.md` for Copilot users).

Second, if you have (in your context) files under the `src\` or `tools\` folder or subfolders, check that those files end with `# eof`. If they do not, stop right there and list those incomplete files, but also list other classes not in your context you might need.
If they do, go on with your instructions.

Before writing code, write a short analysis of the issue and a brief description of the split. Only then write the code, following the project instructions, which means write the class in full (no "`# ...existing code...`" comment).

Ask first for any file missing in your context, but also mention in your answer files in your context not needed for your analysis.

Always update the docstring at the very top of the modified classes to explain the fix. That applies to test classes as well.

Preserve existing code and docstrings and comments; only update them to explain and accommodate your split. Check if any comment is obsolete considering the current code and remove them.
Do not remove comments like `# Act` unless the whole section has been removed as part of your fix. Read and follow instructions from [`preserve_code.md`](../rules/preserve_code.md).

If you move any existing code as part of your split, start, before each code, by recognizing the instructions from [`preserve_code.md`](../rules/preserve_code.md), that is, the need to preserve comments (unless they need to be amended in the context of your refactoring): say "I will preserve existing comments, unless they need to be amended as part of the refactoring" before writing any code, then rewrite the existing code you were about to write, respecting that directive.
Do not put "I will preserve existing comments, unless they have to be amended as part of the refactoring" as a comment in the code. Only say it and respect that directive when writing and splitting code.

You must separate properly with empty lines each code block with empty lines before writing the next block (preceded with `File:`, as instructed in `CLAUDE.md`).
A code block starts with backticks and the language identifier and ends with backticks. Do not repeat the content of that code block twice.

For each class rewritten, check also if the imports for that class are compliant with a DDD-Hexagonal (port-adapter) architecture.

Diagnostic:

- execute `ghog day` (from the root of the project): the groundhog walk runs check.bat, the tests affected by the split, and the full suite with coverage, stopping at the first non-green step with the fix to apply. Do not call `check.bat` or `pytest` directly; groundhog is in charge of check and tests (see [`GROUNDHOG.md`](../GROUNDHOG.md) and [`groundhog.md`](groundhog.md)). An LLM runs it as one redirected shell call from the project root, then branches on the exit code and reads only the tail of `a.ghog.log`:

  ```bat
  cmd /d /c "<llm-shared>\bin\ghog.bat day > a.ghog.log 2>&1"
  ```

- the walk is finished only when `a.ghog.status` reads `state=done`; a growing log proves nothing. When the harness can kill long calls, run `cmd /d /c "<llm-shared>\bin\ghog.bat day --detach"` (no redirect) instead, then poll `cmd /d /c "<llm-shared>\bin\ghog.bat status"` (never redirected) until its exit code is no longer 6: exit 7 means the run was lost (relaunch), any other code is the walk's own.
- a "Check for files too big" failure from check.bat is expected while the split is in progress (the original file still exists): finish the split first, then run `ghog day` again.

Repeat fix-and-walk until `ghog day` reports the objective (`exit=0`).

Finally, prepare a commit message following the structure described in [`write-commit-message.prompt.md`](../.github/prompts/write-commit-message.prompt.md), with a "Why:" section having two detailed parts (multiple sentences per part) using specific terms (no generalities). Consider for that commit message only the files you have modified as part of your split, and not any other file in your context that you have not modified. Do not mention in the commit message any file you have not modified, even if it is in your context.

Write only in this last step the commit message, do not commit the code.
