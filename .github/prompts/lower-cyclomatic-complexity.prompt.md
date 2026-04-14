---
agent: ask
description: 'Lower cyclomatic complexity in the codebase.'
---

This code has a high cyclomatic complexity, above 10.

First, if you have in your context files under the `src\` or `tools\` folder or subfolders, check those files ends with `# eof`. If they do not, stop right there and list those incomplete files. If they do, go on with your instructions.

Can you refactor it to reduce its complexity below 10, while keeping the same behavior and logic? It should call subfunctions with names which explain the subfunction logic. The sequence of subfunction calls in the main function should be easy to read and understand, illustrating the purpose of the main function.

Rewrite the all class. You must preserve existing comments, and add new ones from the refactored functions.  
Read your instructions in `.github\copilot-instructions.md` ( #file:../copilot-instructions.md ) and `.github\python.instructions.md` ( #file:../python.instructions.md ). Avoid `Type of "xxx" is partially unknown`: every type must be fully typed. Read and follow instructions from #file:../preserve_code.md .

Here is now the list of classes or functions to refactor, with their cyclomatic complexity:
