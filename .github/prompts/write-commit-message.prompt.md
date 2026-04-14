---
agent: ask
description: 'Write a conventional commit message based on the provided code changes.'
---

Your goal is to analyse the set of Git diff hunks in #file:../../a.diff , and create a commit message based on the 'conventional commit' convention.

Consider the diff #file:../../a.diff , but also any other file in your context and write a conventional commit message:

```log
type(topic): subject
(empty line)
Why:
(empty line)
A detailed reason for the change. Multiple sentences. Use specific terms, not generalities.
(empty line)
A detailed description of the "now" state that this commit now allows. Multiple sentences. Use specific terms, not generalities.
(empty line)
What:
(empty line)
- list of changes...
- ... done for that commit
```

Be mindful of empty lines:

- Add an empty line between the title and the Why section.
- Add an empty line between `Why:` and its section.
- Add an empty line between between the reason and the "now" state" within the `Why:` section.
- Add an empty line between between the end of the `Why:` section and the `What:` section.
- Add an empty line between `What:` and its section.

Reminder, conventional commit means, the title must start with '<type>[optional scope]: description', with 52 characters max.  
Types other than `fix:` and `feat:` are `build:`, `chore:`, `ci:`, `docs:`, `style:`, `refactor:`, `perf:`, `test:`, and others.

Do not add a footer. Do not add an introduction like 'The title should be...' or 'My name is GitHub Copilot'. Just print the title and the body of the commit message without any other comment.

- The title must not exceed 52 characters
- The body and footer lines must not exceed 80 characters, and must not be indented, no prefix spaces.

Make sure the body includes two sections, 'Why' and 'What':

- in the 'Why' section, do not use generic 'Improved xxx' without explaining why xxx is improved.
- in the 'What' section, make a list of modifications, each line starting with a dash.

Make sure to read your instructions ( #file:..\copilot-instructions.md ): those include a list a word you must not use in the commit message (beside code/snippets).

Note that `git diff` (when #file:../../a.diff is present in your context) output includes context lines (lines that start with neither '`+`' nor '`-`'). These context lines show code that exists before or after the changes but were not modified. Only analyze the actual changes (lines starting with '`+`' or '`-`') when generating the commit message.

Do pay attention to line lengths (52 chars max for title, 80 chars max for each lines in the commit body message), and do not use words listed in the "Blacklist of words to avoid in the response" of #file:..\copilot-instructions.md .
