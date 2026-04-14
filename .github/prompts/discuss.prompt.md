---
agent: ask
description: 'Discuss'
---

Your goal is to answer the question asked in your prompt, based on your context and, if relevant, your previous answer, but without writing code.

First, if you have in your context files under the `src\` or `tools\` folder or subfolders, check those files ends with `# eof`. If they do not, stop right there and list those incomplete files. If they do, go on with your instructions.

You need to provide answers, asking for possible additional files in your context if needed, without writing code.  
Do request any source file that might help you in your answer by looking source file list in #file:./../../source.list

It is about challenging and debating the current point, not about writing code.

You write a answer in markdown, so respect instructions for markdown lists in #file:./../markdown.instructions.md .
