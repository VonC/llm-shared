---
name: sanitize-git-history
description: 'Audit the full git history of a repository for confidential words against the watch list in a.sensitive.replacements.local.txt (phase 1), then rewrite that history on a fresh clone with git filter-repo, re-audit and restore the remotes without pushing (phase 2). Use when the user asks to sanitize a repo history or make a repository publishable.'
---

[Instruction](../../instructions/sanitize-git-history.md)
