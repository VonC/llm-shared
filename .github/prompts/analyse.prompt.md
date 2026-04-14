---
agent: ask
description: 'Analyze'
---

Your goal is to write an analysis based on the context provided, without writing code, by first challenging and asking question about the context, and requesting any source code file you need to provide a complete analysis.

Use the source file list in `source.list`, `source.tests.list`, `source.web.list` and `source.tests.web.list` to request any source code file you might need for your analysis.

First, if you have in your context files under the `src\` or `tools\` folder or subfolders, check those files ends with `# eof`. If they do not, stop right there and list those incomplete files. If they do, go on with your instructions.

You need to provide an analysis, asking for possible additional files in your context if needed, without writing code.  

It is about challenging and debating the current point, not about writing code.

You write a answer in markdown, so respect instructions for markdown lists in #file:./../markdown.instructions.md .
