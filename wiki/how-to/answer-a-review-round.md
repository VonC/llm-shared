# How to answer a review round

<img src="../assets/logo-llm-shared-review-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

## Invocation model

The AI creates and later consolidates the review round; the human supplies the
answers. Invoke consolidation directly only when resuming an existing answered
document outside the original automated chain.

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
     chain on the plan's first step, whose id comes from the validation
     plan and is not always `1`) with no "go ahead".

## ✋ Holding the chain at the implementation gate

The settled-plan handoff starts the implementation by default. To settle
the plan without starting it, say so in the consolidation invocation:

```txt
/consolidate-then-review-ask-questions on docs/plan.vX.Y.Z.<slug>.md stop here
```

Any explicit instruction not to implement works the same way: the skill
still folds the answers, strips the questions and writes the decision
table, then prints the `/implement-step` line as the next step instead of
running it. Without such an instruction, the default stands and the first
step starts at once.

## 🤷 When a round raises no question

The review skill then writes a one-row decision table (its row keeps the
words "No open questions", which the routing reads as the settled
signal), so the document reads as settled and the skill runs `pw skill`
and the command it prints, skipping the consolidation round. The same
`stop here` hold applies when the settled document is a plan.

## ✅ Check after the fold

The document has no `## Open questions` section left, its decision table
references every `Qxx`, and `pw skill` prints the next phase's command.

Related: [Why the LLM reviews its own work](../explanation/why-the-llm-reviews-its-own-work.md),
[Where the human stays in the loop](../explanation/where-the-human-stays-in-the-loop.md).
