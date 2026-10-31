---
name: sanitize-git-history
description: 'Audit the full Git history of any repository for confidential words, automatically using the contextual scanner with literal terms or a.sensitive.replacements.local.txt, then rewrite that history with git filter-repo before publishing. Phase 1 reports matching commit, tag, path, and blob lines and drafts or refreshes the rules plus an optional mailmap. Phase 2 rewrites a fresh clone, re-audits, verifies changed commits, restores remotes, and stops before any push. Use when the user asks to inspect or sanitize history, scrub sensitive terms, or make a repository publishable.'
user-invocable: true
argument-hint: 'Name the phase and optionally the repo, for example "sanitize-git-history phase 1" or "sanitize-git-history phase 2 on ../myrepo". Default is phase 1 on the current project.'
---

[Instruction](../../../instructions/sanitize-git-history.md)
