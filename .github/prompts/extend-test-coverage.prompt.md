---
agent: ask
description: 'Extend the tests of a class to cover more scenarios.'
---

Your goal is to extend the tests of the code currently in your context to cover more scenarios listed in your prompt.

First, if you have in your context files under the `src\` or `tools\` folder or subfolders, check those files ends with `# eof`. If they do not, stop right there and list those incomplete files. If they do, go on with your instructions.

Ask first for any file missing in your context, but also mention in your answer files in your context not needed for your analysis.  
In particular, ask (if not present in your context) for the TDD (and PBT if applicable) test class files in relation with the class whose test coverage needs to be extended.

If you find yourself writing a brand new file test, make sure to do so only after asking for that test file in your context: if I confirm it does not exist, then you can write it.

Always consider if you also need to write PBT tests in addition of extending TDD tests.

You rewrite the test class (or classes) in full, and you must separate properly with empty lines each code block with empty lines, before writing the next block (preceded with Files, as instructed in #file:..\copilot-instructions.md ).

Do respect existing code, comment and docstrings, as instructed in #file:../preserve_code.md .

For each class rewritten, check also if the imports for that class are compliant with a DDD-Hexagonal (port-adapter) architecture, but only if said imports have changed as part of your fix.

Here are the code paths of the currently selected file not covered by test, that you now must cover:
