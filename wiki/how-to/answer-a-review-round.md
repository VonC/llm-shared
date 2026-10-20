# How to answer a review round

<img src="../assets/logo-llm-shared-review-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

## Invocation model

The AI creates the review round; the human supplies answers. Questions and
answers remain in the document during review. Consolidation requires an
express human instruction for that document or the review gate's `Consolidate`
choice. A combined-skill invocation with only a document path is ambiguous
and preserves the questions.

## Separate independent-review rounds

This guide covers the human-answered **self-review loop** for open questions.
For the opt-in exchange between separate agents, first read
[why independent review mode separates authority](../explanation/independent-review-mode-and-human-authority.md).

🔁 Goal: answer the open questions a review skill raised on a requirement,
design or plan, and get the answers folded into the document.

## 🔍 What a review round produces

`/review-ask-questions on docs/<type>.vX.Y.Z.<slug>.md` appends an
`## Open questions` section to the document, one `Qxx` block per question.
Each block follows the
[open-question template](../reference/templates.md): a description, a BBQ
rewording (how two people at a barbecue would say it, closed by an
"In this picture: ..." mapping that names the concrete concept behind each
analogy element), two or three
options with pros and cons, and a recommended option. The chat ends with
the summary table:

```txt
| Q0x | Title | Recommended Answer |
```

This is a deliberate stop: nothing runs until a human answers.

## 📋 Steps to answer and fold

1. Read the `Qxx` blocks in the document, not just the table — the options
   and their cons are where the trade-offs live.

2. Answer in the chat, one line per question. Accept the recommendation or
   override it; free-text answers are fine:

   ```txt
   Q01: option A2
   Q02: option B1, but keep the old flag as an alias
   ```

3. When you want the answered questions integrated and removed, explicitly
   request consolidation:

   ```txt
   /consolidate-then-review-ask-questions on docs/<type>.vX.Y.Z.<slug>.md consolidate the answered questions
   ```

4. The skill runs plain `git reset`, stages only the exact document, writes a
   single-group root `a.commit`, and batch-commits
   `docs(<scope>): record pre-consolidation questions`, using the topic slug
   when it fits or the normalized document type otherwise. It stops before the
   fold if the commit contains another path or the index is not empty afterward.

5. The skill integrates each answer into the document body, records it in
   a decision table (named for the type: requirement clarifications,
   design decisions, implementation decisions), and strips the
   open-questions section with `oqm.bat --strip`.

6. If new questions are needed, the skill appends them and presents a new
   `Q0x` table. Whether or not questions remain, it then applies the
   [independent review gate](../../rules/specification-review-gate.md).
   With review mode enabled, the exact document goes to the specification
   requestor. With review mode disabled, the workflow stops before the next
   phase unless the human explicitly waives independent review for that document.
   Answering questions or asking for consolidation does not waive review.
7. When the document is settled, the skill groups and batch-commits the
   remaining non-ignored changes and requires `git status --porcelain` to be
   empty before completing the workflow. An already authorized exchange
   consolidation returns to its requestor for completion and the human's next
   choice. A printed `pw skill` command alone does not authorize advancement.

The writing skills use `pw skill --after-write requirement|design|plan` so a
new artifact receives its first writer assessment. That assessment and the
independent review are separate gates.

## ✋ Holding the chain at the implementation gate

An explicit hold prevents phase advancement even when review is complete.
To settle the plan and hold implementation, say so in the consolidation invocation:

```txt
/consolidate-then-review-ask-questions on <effort-dir>/plan.vX.Y.Z.<slug>.md consolidate the answered questions and stop here
```

Any explicit instruction not to implement works the same way: the skill
still folds the answers, strips the questions and writes the decision
table, then presents the applicable next review or workflow action and stops.
The absence of a hold does not waive independent review.

## 🤷 When a round raises no question

When the document has no existing question blocks, the writer assessment
records "No open questions" in the decision table, preserving existing
decisions. When answered questions remain, keep those blocks and report that
no additional questions were found. Neither case authorizes consolidation.
It still applies the independent review gate. A settled design needs an
independent design review before plans unless the human explicitly waives it.
No-question findings are never evidence that an independent reviewer has
assessed the document.

## ✅ Check after the fold

The snapshot commit immediately before the fold contains only the answered
document. The document then has no `## Open questions` section left, its
decision table references every `Qxx`, all post-fold changes are committed
through `group-commits-msg`, and `git status --porcelain` is empty before
phase advancement. Verify that the independent review gate and any human hold
also permit the next action.

Related: [Why the LLM reviews its own work](../explanation/why-the-llm-reviews-its-own-work.md),
[Where the human stays in the loop](../explanation/where-the-human-stays-in-the-loop.md).
