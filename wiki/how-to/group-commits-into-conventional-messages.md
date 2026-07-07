# How to group a dirty tree into conventional commits

<img src="../assets/logo-llm-shared-trail-transparent.png" alt="" height="90" align="right">

<!-- markdownlint-disable MD013 -->

📊 Goal: turn a working tree holding several unrelated changes into an
ordered series of conventional commits, each with a `Why:` / `What:` body.

## 📋 Steps from staged diff to replayed commits

1. Stage the slice you want to commit (`git add .` only when nothing
   unrelated is lying around).

2. Build the prompt:

   ```cmd
   gcmp
   ```

   `gcmp` writes `a.diff` (a snapshot of the staged diff), clears
   `a.commit`, builds a `/group-commits-msg` prompt from the staged files
   and copies it to the clipboard.

3. Paste the prompt into the agent and add a word of context after the
   trailing `Context:` line. The skill reads the diff, groups the files
   from least dependent to most dependent, and writes one commit message
   per group into `a.commit`, formatted by `wac.bat`. A trailing docs
   group (`docs(<topic>): record step <n> completion`) always goes last.

4. Review `a.commit`. The grouping is only as good as the staged diff: if
   a feature and an unrelated refactor are mixed, edit the file by hand or
   stage in two passes. `a.diff` is there to justify each group.

5. Replay:

   ```cmd
   gcba
   ```

   or say `go ahead` at the multi-choice the skill presents. `gcba`
   validates `a.commit` first, then creates the commits in order.

## 🚪 The commit gate choices

When the skill runs inside the implement chain, the go-ahead menu is built
by `pw skill --after-commit <x>` and offers the contextual follow-up:
`Go ahead`, `Go ahead, and implement step <next>`, or
`Go ahead, and prepare-release` once the last plan step is committed.
Every concrete choice commits first.

## ✅ Check after the replay

`git log --oneline` shows one commit per group, least dependent first,
each title 52 characters or less, each body carrying `Why:` and `What:`
sections wrapped at 80 columns.

Related: [Commit message format](../reference/commit-message-format.md),
[Why grouped commits, least dependent first](../explanation/why-grouped-commits.md).
