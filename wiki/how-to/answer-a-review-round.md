# How to answer a review round

<img src="../assets/logo-llm-shared-review-transparent.png" alt="" height="90" align="right">

<!-- markdownlint-disable MD013 -->

🔁 Goal: answer the open questions a review skill raised on a requirement,
design or plan, and get the answers folded into the document.

## 🔍 What a review round produces

`/review-ask-questions on docs/<type>.vX.Y.Z.<slug>.md` appends an
`## Open questions` section to the document, one `Qxx` block per question.
Each block follows the
[open-question template](../reference/templates.md): a description, a BBQ
rewording (how two people at a barbecue would say it), two or three
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

3. Run (or accept) the consolidation:

   ```txt
   /consolidate-then-review-ask-questions on docs/<type>.vX.Y.Z.<slug>.md
   ```

4. The skill integrates each answer into the document body, records it in
   a decision table (named for the type: requirement clarifications,
   design decisions, implementation decisions), and strips the
   open-questions section with `oqm.bat --strip`.

5. Two endings are possible:

   - new questions are needed — the skill appends a fresh round and stops
     with a new `Q0x` table; go back to step 1,
   - the document is settled — the skill runs `pw skill` and hands off to
     the next phase (`/write-design`, `/write-plans`, or the implement
     chain) with no "go ahead".

## 🤷 When a round raises no question

The review skill then writes a one-row decision table, so the document
reads as settled and `pw skill` advances directly, skipping the
consolidation round.

## ✅ Check after the fold

The document has no `## Open questions` section left, its decision table
references every `Qxx`, and `pw skill` prints the next phase's command.

Related: [Why the LLM reviews its own work](../explanation/why-the-llm-reviews-its-own-work.md),
[Where the human stays in the loop](../explanation/where-the-human-stays-in-the-loop.md).
