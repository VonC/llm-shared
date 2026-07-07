# From draft note to settled requirement

<img src="../assets/logo-llm-shared-documents-transparent.png" alt="" height="90" align="right">

<!-- markdownlint-disable MD013 -->

📝 In this tutorial you take a raw idea through the first phase of the
workflow: capture it as a draft, let `/process-draft` classify and branch
it, and drive it to a requirement document with an approved decision
table. Allow 20 to 30 minutes. You need a project wired to llm-shared (see
[the setup tutorial](01-plug-llm-shared-into-your-project.md)) and a
`version.txt` file at the project root.

## 1. Write the draft

Create `docs\draft.progress-log.md` (any name works, no version yet) and
describe, in plain language: the desired behavior, what is missing or
broken today, the constraints, an example, the expected outcome. Do not
think about code; think about what you want.

## 2. Run /process-draft

```txt
/process-draft on docs\draft.progress-log.md
```

The skill reads the draft and walks you through four short menus, one at a
time:

1. the classification (`- Type:` line: one feature-request, one issue, or
   a collection of both) with three witty title proposals,
2. three collision-checked slug proposals,
3. the target version, derived from `version.txt` (keep `X.Y.Z`, or step
   major, minor, or patch),
4. the branch layout: a new sibling worktree, or `git switch -c <slug>` in
   the current tree.

It then calls the `new_draft` tool, which renames the file to
`docs\draft.vX.Y.Z.<slug>.md` and creates the effort branch.

## 3. Let the chain write the requirement

`/process-draft` ends on a multi-choice fed by `pw skill`. For a
single-topic draft, pick the proposed
`/write-requirement on docs/draft.vX.Y.Z.<slug>.md`. The skill validates
its three inputs (type, version, topic label), then writes
`docs\feature-request.vX.Y.Z.<slug>.md` (or `issue.`) from the
[requirement template](../reference/templates.md).

No "go ahead" is needed here: the writing skill ends by running
`pw skill`, which prints the next command, and the model runs it straight
away.

## 4. Stop at the review table

That next command is `/review-ask-questions`. The skill challenges the
document it just wrote and posts its open questions as a table:

```txt
| Q0x | Title | Recommended Answer |
```

This is the one human stop of the document phase. Read each `Qxx` block in
the document (options, pros and cons, recommended choice) and answer in
the chat, for example: `Q01: option A2. Q02: option B1.`

## 5. Consolidate and settle

Run (or accept) `/consolidate-then-review-ask-questions on docs\...`. The
skill folds each answer into the document body, records them in a decision
table, strips the open-questions section, and either asks a new round or
declares the document settled. When it settles, `pw skill` hands off to
`/write-design` — the same write, review, consolidate loop then repeats
for the design and for the plan.

## 6. Look at what landed on disk

```txt
docs\draft.vX.Y.Z.<slug>.md            the classified draft
docs\feature-request.vX.Y.Z.<slug>.md  the requirement with its decision table
a.prompt_memory                        the branch-locked workflow state
```

The requirement document now carries not just the need, but the questions
that were asked and the answers that were given: the trail a future reader
(human or LLM) will use.

## 👉 Next steps after the requirement

- [Answer a review round](../how-to/answer-a-review-round.md) for the
  review mechanics in detail.
- [Run the implement chain on one plan step](04-run-the-implement-chain.md)
  once design and plan are settled.
- [Why documents come before code](../explanation/why-documents-before-code.md)
  for the reasoning behind the phases.
