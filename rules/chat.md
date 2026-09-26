# Shared chat instructions

- Always consider all opened editors as context for your session. If you have
  to guess the content of a class, ask first if that class already exists and
  for that class to be added to your context.
- If you have in your context files under the `src/` or `tools/` folder or
  subfolders, check those files end with `# eof`, only if there are Python
  files (`*.py`). If they do not, stop and list those incomplete files. If
  they do, continue with your instructions.
- When writing code, always print first the pathname of the file relative to
  the workspace root. That must include:
  - a line with `File: <relative_pathname>` (do not add a code fence before
    that section),
  - a line with `File: &&<relative_pathname>&&`,
  - an empty line,
  - the code block, starting with three backticks and the language identifier,
  - the closing three backticks,
  - and an empty line before the next file.
  Do not repeat the content of the code block twice.
- When asked to write code, write the impacted classes in full while
  preserving existing code, comments, and docstrings. Preserve `Args` and
  `Returns`, updating them only to explain the fix.
- When asked to write code, update the tests associated with the modified
  classes to cover the fix. If the tests are not in your context, ask for the
  test files before writing code. For a new class, write its tests first.
- Update `__init__.py` files to include new classes or test classes.
- Update the docstring at the top of modified classes to explain the fix. This
  applies to test classes too.
- When writing Markdown, follow [`markdown.md`](markdown.md).
- When writing or rewriting a file, follow
  [`preserve_code.md`](preserve_code.md).
- When running a shell command, follow [`run_commands.md`](run_commands.md).
- When creating any `a.*` working file (scratch, script, captured output, log,
  evidence, report, private note), follow
  [`artifact_files.md`](artifact_files.md): it lives in the review artifact
  home (`.reviews`), never at the project root, apart from six listed files.
- When adding or modifying an LLM-specific Markdown adapter, follow
  [`llm-specific-adapters.md`](llm-specific-adapters.md).

## Blacklist of words to avoid in responses

Except in code snippets and code blocks, avoid the terms and expressions in
[`blacklist.md`](blacklist.md).

