---
description: Run pw workflow commands reliably from a non-interactive shell by calling prompt_workflow.bat directly instead of relying on the interactive doskey alias. Use when a workflow asks to run pw skill, pw handoff, or another pw command from tools.
---

1. Locate the shared instruction body `instructions/run-pw.md`: in this
   workspace root when the workspace is llm-shared itself, else under the
   sibling clone `../llm-shared`, else under a `llm-shared` submodule folder.
2. Read that file in full.
3. Follow it exactly, treating any text given after the slash command as its
   arguments.
