# Where the human stays in the loop

<img src="../assets/logo-llm-shared-review-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

## Invocation model

The user starts the high-level skill and owns the documented decisions. The AI
owns intermediate skills, launchers, checks, and evidence gathering; a human is
not expected to run those prerequisites merely to keep automation moving.

🔁 The workflow automates every transition it safely can, and keeps a
short, deliberate list of stops where a human decides. Knowing the list
is knowing the workflow: everything between two stops runs by itself.

## 📏 The design rule behind the stops

A stop earns its place when the decision is irreversible, or when only
the author knows the answer. Everything else — writing a document,
running a review, checking an implementation, drafting commit messages —
is reversible text on disk, so the chain runs it without asking.

## ✋ The stops of the document phase

- **The four menus of /process-draft** — title, slug, version, branch
  layout. Naming and versioning shape everything downstream.
- **The review table** — the one `[STOP]` of the write, review,
  consolidate loop: the model asks, the human answers the
  `Q0x | Title | Recommended Answer` table. The chain resumes on the
  consolidation, not on a "go ahead".

## 🚪 The optional stop between documents and code

The settled plan is the border between text and code, and crossing it is
a default, not an inevitability. When the last consolidation settles the
plan, the chain starts the implementation of the plan's first step by
itself; a fresh plan, on the other hand, always meets its review round
first — the routing reads consolidated decisions (`| Qxx` rows or the
"No open questions" row), never a merely seeded decisions heading. The
author who wants to read the settled plan before any code moves says so:
`stop here` in the consolidation invocation, or any explicit instruction
not to implement, turns the handoff into a printed next step and a stop.

## 🛑 The stop of the implement chain

The chain — implement, check, fill gaps, group commits — runs with no
menu until `a.commit` is written. Writing the messages is automatic;
**making the commits is not**. The commit gate presents the grouped plan
and waits for `go ahead` (or the contextual
`go ahead, and implement step <next>`). Every concrete choice still
commits first — a follow-up never skips the gate.

## ⏸️ The pauses of the release preparation

`/prepare-release` pauses wherever the repository's history is about to
change shape: the dirty-tree decision, the rebase-or-merge choice when
the branch is behind `main`, each rebase conflict, the merge message
review, the title pick, the notes review — and it never tags and never
pushes. `brel`, the tag, is always typed by the author.

## 🔒 What is never automated

Three acts stay manual by design: answering the review questions,
approving the commits, and creating the tag. They are the three points
where the author's intent enters the system — everything else is
derivable from what is already on disk.

## 👉 Where each gate is described

- [Answer a review round](../how-to/answer-a-review-round.md) for the
  review stop.
- [Group a dirty tree into conventional commits](../how-to/group-commits-into-conventional-messages.md)
  for the commit gate.
- [Prepare a release from any branch](../how-to/prepare-a-release.md) for
  the full pause table.
