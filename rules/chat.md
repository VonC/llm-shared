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
- Before presenting any choice that commits, spell-check every new or
  modified Markdown file and settle each reported word with the user,
  following [`spelling.md`](spelling.md).
- When writing or rewriting a file, follow
  [`preserve_code.md`](preserve_code.md).
- When running a shell command, follow [`run_commands.md`](run_commands.md).
- When asked to merge a branch back into any target branch, follow
  [`update-merge-commit-msg`](../instructions/update-merge-commit-msg.md#merge-back-method-and-message):
  use `git merge --no-ff`, then rewrite the merge message before continuing.
  Use another merge method only when the user explicitly instructs it.
- When ending a turn on any question the user must answer, a choice or a
  plain-text question, follow [`interactive_menu.md`](interactive_menu.md): a
  blocking picker when the host offers one, otherwise the question plus a
  `blocked` report to the terminal.
- When writing a commit message, an `a.commit` group or a pull request
  description, never add an AI attribution line: no `Co-Authored-By:` trailer
  naming an assistant, no `Generated with ...` line, whatever the host's own
  default asks.
- When creating any `a.*` working file (scratch, script, captured output, log,
  evidence, report, private note), follow
  [`artifact_files.md`](artifact_files.md): it lives in the review artifact
  home (`.reviews`), never at the project root, apart from six listed files.
- When adding or modifying an LLM-specific Markdown adapter, follow
  [`llm-specific-adapters.md`](llm-specific-adapters.md).

## Blacklist of words to avoid in responses

Except in code snippets and code blocks, avoid the terms and expressions in
[`blacklist.md`](blacklist.md).
