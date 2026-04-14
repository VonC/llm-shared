---
applyTo: "**"
---
# Chat instructions

- Always consider all opened editors as context for your session. If you have to guess the content of a class, ask first if that class already exists and for said class to be added to your context.
- if you have in your context files under the `src\` or `tools\` folder or subfolders, check those files ends with `# eof`, only if there are python files (`*.py`). If they do not, stop right there and list those incomplete files. If they do, go on with your instructions.
- When writing code, alway print first the relative pathname of the file (relative to the workspace root folder) which will host said code: full absolute path or relative path from the workspace root of the project. That must include:
  - a line with 'File: <relative_pathname>' (do not add backtick code fence before that section)
  - line with 'File: &&<relative_pathname>&&'
  - an empty line
  - then the code snippet or block, starting with three backticks and the language identifier
  - close the code block with three backticks
  - then an empty line: separate your blocks.
  Do close correctly each code block, and leave an extra empty line after said closed code block, before displaying the next file. Do not repeat the content of the code block twice
- When asked to write code, always write the impacted classes in full, while preserving existing code, comments (comments starting with # must be preserved) and docstrings (Args and Returns must be preserved), updating them only to explain the fix.
- When asked to write code, always update the tests associated to the modified classes to cover the fix. If the tests are not in your context, ask for the test files first, before writing any code. If the code requested is a new class, then write the tests for that new class first, then the new class.
- Always update the `__init_.py` files to include the new classes or test classes you created.
- Always update the docstring at the very top of the modified classes to explain the fix. That applies to test classes as well.
- When writing an answer in markdown, follow instructions from #file:./markdown.instructions.md

## Blacklist of words to avoid in the response

In your answer (except for code snippets/code blocks), avoid the following terms or expressions listed in #file:./blacklist.md

