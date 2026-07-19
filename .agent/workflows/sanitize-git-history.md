---
description: Audit Git history by automatically running the contextual sensitive-history scanner against terms or a.sensitive.replacements.local.txt, then optionally rewrite a fresh clone with git filter-repo, re-audit, and stop before pushing.
---

1. Locate the shared instruction body `instructions/sanitize-git-history.md`: in this
   workspace root when the workspace is llm-shared itself, else under the
   sibling clone `../llm-shared`, else under a `llm-shared` submodule folder.
2. Read that file in full.
3. Follow it exactly, treating any text given after the slash command as its
   arguments.
