---
description: Audit the full git history of a repository for confidential words against the watch list in a.sensitive.replacements.local.txt (phase 1), then rewrite that history on a fresh clone with git filter-repo, re-audit and restore the remotes without pushing (phase 2). Use when the user asks to sanitize a repo history or make a repository publishable.
---

1. Locate the shared instruction body `instructions/sanitize-git-history.md`: in this
   workspace root when the workspace is llm-shared itself, else under the
   sibling clone `../llm-shared`, else under a `llm-shared` submodule folder.
2. Read that file in full.
3. Follow it exactly, treating any text given after the slash command as its
   arguments.
