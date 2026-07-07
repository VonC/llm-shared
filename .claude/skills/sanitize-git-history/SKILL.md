---
name: sanitize-git-history
description: 'Audit the full git history of any repository for confidential words (people, companies, internal hosts and emails), then rewrite that history with git filter-repo before publishing. Phase 1 scans every commit message, tag, file path and file version ever committed against the watch list in a.sensitive.replacements.local.txt, reports the hits, and drafts or refreshes that replacement-rules file plus an optional a.mailmap.local.txt. Phase 2 rewrites a fresh clone with those files, re-audits, verifies which commits changed, restores the remotes, and stops before any push. Use when the user asks to sanitize a repo history, scrub sensitive terms, or make a repository publishable.'
user-invocable: true
argument-hint: 'Name the phase and optionally the repo, for example "sanitize-git-history phase 1" or "sanitize-git-history phase 2 on ../myrepo". Default is phase 1 on the current project.'
---

[Instruction](../../../instructions/sanitize-git-history.md)

The instruction body carries the full two-phase workflow:

- [`../instructions/sanitize-git-history.md`](../../../instructions/sanitize-git-history.md)
  — the audit steps (messages, tags, paths, blobs, identities), the
  replacement-rules file format and its no-comment trap, the filter-repo
  rewrite, and the post-rewrite verifications.

Inputs: the repository (current project by default), the git-ignored
`a.sensitive.replacements.local.txt` watch list at its root (drafted by
phase 1 when missing), and an optional `a.mailmap.local.txt` for
identities. The skill never pushes: publishing the rewritten history is
always left to the user.
