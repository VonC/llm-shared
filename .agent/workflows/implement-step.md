---
description: Implement a step of a feature, based on the feature notes and issue notes for that step, and any other relevant context. The step to implement is the one mentioned in the prompt, for example "implement step 2 of the CDC gap feature".
---

1. Locate the shared instruction body `instructions/implement-step.md`: in this
   workspace root when the workspace is llm-shared itself, else under the
   sibling clone `../llm-shared`, else under a `llm-shared` submodule folder.
2. Read that file in full.
3. Follow it exactly, treating any text given after the slash command as its
   arguments.
