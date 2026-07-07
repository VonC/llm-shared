# Why grouped commits, least dependent first

<img src="../assets/logo-llm-shared-trail-transparent.png" alt="" height="90" align="right">

<!-- markdownlint-disable MD013 -->

📊 By commit time, a working tree rarely holds one change. It holds the
goal change, the small fixes noticed along the way, the paired test
updates, a doc tweak. `/group-commits-msg` exists because of two failure
modes of committing that pile by hand.

## ⚠️ The two failure modes

**Forgetting.** The author no longer remembers every change made in the
tree. Squashing everything into one "WIP" commit hides the small fixes
forever: they never get a message, so they never get a why.

**Ordering.** A commit that modifies a file used by a later commit must
land first, or the midway states of the repository are incoherent: tests
fail between two commits, and a future `git bisect` lands on a state
that never really existed. Grouping least dependent first keeps every
intermediate state coherent.

## 🔍 What the skill rebuilds from the diff

The skill reads the staged diff (`a.diff` keeps the snapshot), regroups
the files by dependency, and writes one conventional message per group
into `a.commit` — rebuilding the story of the change from the evidence,
including the parts the author forgot. The author reviews the plan;
`gcba` replays it as real commits in order.

## 💬 Why the body carries Why and What

The Conventional Commits spec stops at the title, and the title is enough
for a changelog generator. It is not enough for the next readers: the
author six months later, the new contributor reading the history in
order, the LLM handed only the files and the log. The `Why:` paragraphs
carry the reason and the resulting state; the `What:` list carries the
actual modifications. The diff tells what changed; only the body tells
what it was for.

## 🚧 The honest limit of the grouping

The skill is only as good as the staged diff. When a feature and an
unrelated refactor are staged together, it produces two well-formed
commits, but only along the split the diff supports. The fix is manual
and cheap: edit `a.commit`, or stage in two passes.

## 👉 Where the format and the recipe live

- [Commit message format](../reference/commit-message-format.md) for the
  52/80 rules and the file format.
- [Group a dirty tree into conventional commits](../how-to/group-commits-into-conventional-messages.md)
  for the step-by-step recipe.
