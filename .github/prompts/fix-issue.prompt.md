---
agent: ask
description: 'Fix a class or classes in the provided code changes.'
---

Your goal is to fix the code to address the issue described in the question below.

Consider your context, and the question below asking you to update one or several classes to fix a bug or an issue.

Fist, read your instructions ( #file:..\copilot-instructions.md )

Second, if you have in your context files under the `src\` or `tools\` folder or subfolders, check those files ends with `# eof`. If they do not, stop right there and list those incomplete files, but also list other classes not in your context you might need.  
If they do, go on with your instructions.

Before writing code, write a short analysis of the issue, and a short description of the fixes. Only then write the code, following #file:..\copilot-instructions.md , which means write the class in full (no "`# ...existing code...`" comment)

Ask first for any file missing in your context, but also mention in your answer files in your context not needed for your analysis

Always update the docstring at the very top of the modified classes to explain the fix. That applies to test classes as well.

Preserve existing code and docstrings and comments, only update them to explain and accommodate your fixes.
Do not remove comments like `# Act` unless the all section has been removed as part of your fix. Read and follow instructions from #file:../preserve_code.md .

If you rewrite any existing code, start, before each code, by recognizing the instructions from #file:../preserve_code.md , that is the need to preserve comments (unless they need to be amended in the context of your refactoring): say "I will preserve existing comments, unless they need to be amended as part of the refactoring" before writing any code, then rewrite the existing code you were about to write, respecting that directive.  
Do not put "I will preserve existing comments, unless they need to be amended as part of the refactoring" as a comment in the code. Only say it and respect that directive when writing code.

You must separate properly with empty lines each code block with empty lines, before writing the next block (preceded with Files, as instructed in #file:..\copilot-instructions.md ).  
A code block starts with backticks and the language identifier, and ends with backticks. Do not repeat the content of that code block twice.

For each class rewritten, check also if the imports for that class are compliant with a DDD-Hexagonal (port-adapter) architecture.
