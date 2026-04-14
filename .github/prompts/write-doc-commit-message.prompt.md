---
agent: ask
description: 'Write a conventional commit message based on a markdown document.'
---

Your goal is to analyse the markdown document in your context from the `docs\` folder, and create a commit message based on the 'conventional commit' convention, explaining:

- why the topics discussed in the document are important to address in the codebase
- what actions were taken to address those topics in the codebase

The commit message must be a conventional commit, as described in #file:write-commit-message.prompt.md (pay attention to line length, and to the Why and What structure, with intermediate empty lines after the `Why:` and the `What:`). The title being 52 chars in length including the type and scope, use abbreviations when needed to keep it short.

The conventional commit message must be a '`docs:`' type commit, and a topic. And its content must make clear that the commit is about documenting a plan for code changes, not the code changes themselves (no need to say it literally). The `What:` section must focus on what the document introduces, not on code changes, and should be presented as a list of bullet points, again after the mandatory empty line after the `What:`.

Do pay attention to line lengths, as specified in #file:write-commit-message.prompt.md (52 chars max for title, 80 chars max for each lines in the commit body message), and do not use words listed in the "Blacklist of words to avoid in the response" of #file:../copilot-instructions.md .
