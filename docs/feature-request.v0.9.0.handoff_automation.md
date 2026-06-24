# Automated handoffs across the requirement-to-release workflow

## Why the workflow needs automated handoffs

As an author driving a feature from a raw draft to a release, I run a chain of
instructions: `process-draft`, `split-and-define`, `write-requirement`,
`review-ask-questions`, `consolidate-then-review-ask-questions`, `write-design`,
`write-plans`, then the implementation loop. Today most of those steps end on a
prose note that names the next instruction but stops there, so I retype the next
skill call and its document name by hand at every step. The request is to make
the steps that should chain do so on their own: each one calls the next skill
with the right document name and does not wait for a user review or a go-ahead,
while `pw` (prompt_workflow) hands the instruction the exact names it needs so
the call is deterministic.

## CDC revision that introduces automated workflow handoffs

Earlier CDC state: only the implementation loop chains on its own. The bodies of
`implement-step.md`, `implementation-check.md`, and `implement-missing-step.md`
carry a `## Handoff` section that runs `pw handoff ...` and authorizes running
the returned prompt right away. Every step before that loop chains by a prose
next-step note only: `write-requirement`, `write-design`, and `write-plans` each
say open questions are handled later by `review-ask-questions`; `process-draft`
points a single-topic draft at `write-requirement` or a multi-topic draft at
`split-and-define` as guidance, not as an automatic handoff. `pw` itself prints a
user-facing sentence of the form "Follow the instruction... Context is ...".

The revision adds three things to that earlier state:

- Strong automated handoffs on the writing and consolidation steps, so they call the next skill without waiting for user review or go-ahead.
- A next-step hint on the review step, and multi-choice next-step lists on the two splitting steps, each list closing with a free-text "Type something else" entry.
- A `--skill` mode on `pw` that returns only the next-step command string the LLM needs, with the right `/` or `$` prefix for the host session, instead of the user-facing sentence.

## Current behavior in v0.9.0

- `write-requirement.md` writes `feature-request.vX.Y.Z.<slug>.md` or `issue.vX.Y.Z.<slug>.md`, then only notes that `review-ask-questions` runs later; it does not call it.
- `write-design.md` writes `design.vX.Y.Z.<slug>.md`, then only notes that `review-ask-questions` runs later; it does not call it.
- `write-plans.md` writes a plan and a validation plan, then only notes the plan review; it does not call `review-ask-questions`.
- `review-ask-questions.md` appends question blocks and stops; it gives no hint of the consolidation step that follows.
- `consolidate-then-review-ask-questions.md` stops when no new questions remain and says the document is ready for the next phase, but does not call that next phase.
- `process-draft.md` ends on prose guidance toward `write-requirement` or `split-and-define`; it does not offer a selectable list.
- `split-and-define.md` produces an ordered list of requirements and relies on `DEVELOPMENT.md` telling the user to run `write-requirement` for each; it does not offer a selectable list.
- `pw` returns a user-facing "Follow the instruction... Context is ..." sentence and has no mode that returns a bare next-step command.

## Gap to close in the implementation for handoff automation

1. Add an automatic `## Handoff` to `write-requirement.md` that, right after the requirement file is written, calls `/review-ask-questions` on that exact `feature-request.vX.Y.Z.<slug>.md` or `issue.vX.Y.Z.<slug>.md`, with no wait for review or go-ahead.
2. Add the same automatic `## Handoff` to `write-design.md`: after `design.vX.Y.Z.<slug>.md` is written, call `/review-ask-questions` on it.
3. Add the same automatic `## Handoff` to `write-plans.md`: after the plan is written, call `/review-ask-questions` on the `plan.vX.Y.Z.<slug>.md` only, and leave the validation plan alone.
4. Complete the `## Handoff` of `consolidate-then-review-ask-questions.md` so that, once every open question is answered and no new one is raised, it calls the next instruction the main workflow prescribes: `write-design` for a feature-request or issue, `write-plans` for a design, or `implement-step` for a plan. `pw` supplies the next instruction name and the document name to call it on; for a plan, `pw` extracts the first step to implement and passes it to `implement-step`.
5. Add a next-step hint to `review-ask-questions.md`: `/consolidate-then-review-ask-questions` on the `<doc type>.vX.Y.Z.<slug>.md` it just reviewed, carrying the reviewed document name. Emit it as plain text carrying the reviewed document name as the guaranteed behavior; where a host can render a gray, Tab-completable prompt, show it that way (gray on Claude, plain on Codex), with the reliable trigger for that gray hint on both hosts still to be studied. This stays a hint, not an automatic call, because a human review sits between a review round and the consolidation.
6. Make `process-draft.md` present a multi-choice next-step list: `/write-requirement` on the `draft.vX.Y.Z.<slug>.md` it just produced, `/split-and-define` on the same draft, and a last "Type something else" free-text entry. `pw` supplies the produced draft name.
7. Make `split-and-define.md` present a multi-choice next-step list: one `/write-requirement` entry per slug it just defined, with no cap and in the order the split defined them, on the matching `feature-request.vX.Y.Z.<slugN>.md` or `issue.vX.Y.Z.<slugN>.md`, plus a last "Type something else" entry. `pw` supplies the list of slugs.
8. Add a `--skill` mode to `pw` that returns only the next-step command string, for example `/write-design on the design.vX.Y.Z.<slug>.md`, with no backticks around the `/skill-name` and no surrounding "Follow the instruction... Context is ..." wrapper.
9. Make `pw --skill` auto-detect a Claude or a Codex session and emit the matching command prefix (`/` for Claude, `$` for Codex), and accept an explicit host override the caller passes when detection cannot decide.
10. Let `pw --skill` return a multi-line list of next steps when several apply, one `/skill-name` plus document name per line; the instruction body adds the final "Type something else" free-text entry, which `pw` does not emit.
11. Make `pw --skill` derive the current step from the documents present on the branch: a new draft on `main` or on a branch not named after the slug yields `/process-draft` on the new draft; a `draft.vX.Y.Z.<slug>.md` alone on the slug branch yields `/write-requirement` on the matching requirement; a `feature-request.vX.Y.Z.<slug>.md` or `issue.vX.Y.Z.<slug>.md` with no consolidation table yields `/review-ask-questions` on it; with a consolidation table, an LLM-passed parameter chooses between `/consolidate-then-review-ask-questions` and `/write-design`. When several of these documents are present at once, the reported step follows the most advanced artifact, using the order draft, requirement, design, plan.

## Per-instruction handoff and hint map

| Instruction | Next step it must trigger | What pw supplies |
| --- | --- | --- |
| `process-draft.md` | Multi-choice: `/write-requirement` or `/split-and-define` on the draft, plus "Type something else" | the produced `draft.vX.Y.Z.<slug>.md` name |
| `split-and-define.md` | Multi-choice: one `/write-requirement` per defined slug, plus "Type something else" | the list of slugs it defined |
| `write-requirement.md` | Automatic `/review-ask-questions` on the produced requirement | the `feature-request.vX.Y.Z.<slug>.md` or `issue.vX.Y.Z.<slug>.md` name |
| `write-design.md` | Automatic `/review-ask-questions` on the produced design | the `design.vX.Y.Z.<slug>.md` name |
| `write-plans.md` | Automatic `/review-ask-questions` on the plan only | the `plan.vX.Y.Z.<slug>.md` name; the validation plan is left alone |
| `review-ask-questions.md` | Hint: `/consolidate-then-review-ask-questions` on the reviewed document | the reviewed `<doc type>.vX.Y.Z.<slug>.md` name |
| `consolidate-then-review-ask-questions.md` | When no new questions: `write-design` (feature-request or issue), `write-plans` (design), or `implement-step` (plan) | the next instruction name and document name; for a plan, the first step to implement |

## Confirmed rules for handoff automation

- A handoff fires only after its document is fully written, and it names that exact document.
- The automated handoffs (`write-requirement`, `write-design`, `write-plans`, and `consolidate-then-review-ask-questions` on a settled document) call the next skill without waiting for a user review or go-ahead.
- The author can hold the chain at a writing step by passing a "stop here" signal to that writing skill when invoking it. The signal goes to the skill that writes the document, never to the next skill, and it must be given at invocation, not after the skill has run and the handoff is under way.
- The review step is always named `/review-ask-questions`; there is no `/ask-questions` alias anywhere in the workflow.
- `review-ask-questions` stays a hint, not an automatic call, because a human review sits between the review round and the consolidation.
- The review hint is always emitted as plain text carrying the reviewed document name. Where a host can render a gray, Tab-completable prompt, the hint is shown that way (gray on Claude, plain on Codex); the reliable trigger for that gray hint on both hosts is still to be studied.
- `consolidate-then-review-ask-questions` auto-advances only once every open question carries an accepted answer and the latest round raises no new question; one unanswered question holds the chain at the consolidate step.
- Every multi-choice list ends with a "Type something else" free-text entry that the instruction body provides; `pw` does not emit that entry. When the author uses it, the typed text passes through unchanged as the next call, with no name check and no required document, because the author may state a need that names no document.
- `split-and-define` lists one entry per slug it defined, with no cap, in the order the split defined them.
- `pw --skill` returns only the command string or strings, with no "Follow the instruction... Context is ..." wrapper and no backticks around the `/skill-name`.
- `pw --skill` auto-detects the host and emits the matching prefix (`/` for Claude, `$` for Codex), and accepts an explicit host override the caller passes when detection cannot decide.
- When several `vX.Y.Z.<slug>` documents are present at once, `pw --skill` reports the step that follows the most advanced artifact, using the order draft, requirement, design, plan.
- `write-plans` hands off only the plan, never the validation plan.

## Acceptance criteria for handoff automation

- `write-requirement.md`, `write-design.md`, and `write-plans.md` each end on a `## Handoff` section that issues a single `/review-ask-questions` call carrying the just-written document name and states it runs without waiting.
- Invoking one of those writing skills with the "stop here" signal writes the document and does not fire its handoff; invoked without the signal, the handoff fires.
- `consolidate-then-review-ask-questions.md` issues the `pw`-provided next call only once every open question is answered and no new one is raised: `/write-design` on the design document for a feature-request or issue source, `/write-plans` for a design, or `/implement-step` on the first step for a plan; in the plan case the first step name appears in the call.
- `review-ask-questions.md` ends with a plain-text consolidation hint that includes the reviewed document name; on a host where a gray, Tab-completable prompt can be triggered, the hint is shown that way.
- `process-draft.md` and `split-and-define.md` present the multi-choice lists described above, populated from the `pw`-provided draft name or slug list, and each closes with a "Type something else" entry; `split-and-define` lists one entry per slug, with no cap, in split order.
- Selecting "Type something else" passes the typed text through unchanged as the next call.
- `pw --skill` prints bare next-step command strings with the host-correct prefix and no context block, and prints one line per step when several next steps apply; the prefix follows host auto-detection (`/` for Claude, `$` for Codex) unless the caller passes a host override.
- `pw --skill` returns the right step for each on-disk state: a new draft yields `/process-draft` on that draft; a draft alone on the slug branch yields `/write-requirement` on the matching requirement; a feature-request or issue with no consolidation table yields `/review-ask-questions` on it; with a consolidation table, the LLM-passed parameter selects `/consolidate-then-review-ask-questions` or `/write-design`. When several artifacts are present, the reported step follows the most advanced one (draft, requirement, design, plan).

## File-based IO cost clarification for handoff automation

`pw skill` keeps the document-loading phase a small index-read, not a metadata-loading delay:

- It lists the `docs/` directory once and reads only the marker lines it needs (open-questions and decisions-table) on the matched documents, never a full parse.
- Host detection reads two environment values and touches no file.
- `pw skill` writes nothing: no `a.prompt.txt`, no clipboard, no memory file; it prints to stdout only.

## Code references for handoff automation

- `instructions/write-requirement.md`, `instructions/write-design.md`, `instructions/write-plans.md`: gain an automatic `## Handoff` that calls `/review-ask-questions` on the document just written.
- `instructions/consolidate-then-review-ask-questions.md`: its `## Handoff` is completed to call the next workflow instruction on a no-new-questions outcome.
- `instructions/review-ask-questions.md`: gains the consolidation next-step hint carrying the reviewed document name.
- `instructions/process-draft.md`, `instructions/split-and-define.md`: gain the multi-choice next-step lists with the trailing "Type something else" entry.
- `instructions/implement-step.md`, `instructions/implementation-check.md`, `instructions/implement-missing-step.md`: the existing `pw handoff` sections to mirror for shape and wording.
- `tools/prompt_workflow.py`: the `pw` hub that parses the command line and dispatches; the entry point for the `--skill` flag.
- `tools/prompt_workflow_handoff.py`: the handoff logic that builds the next-step message; where the `--skill` string is produced and the `/` or `$` prefix is chosen.
- `tools/prompt_workflow_docs.py`: the document detection that reads which `vX.Y.Z.<slug>` files are present, used to derive the current step.
- `tools/prompt_workflow_steps.py`: the step parsing that extracts the first step to implement from a plan, passed to `implement-step`.
- `bin/prompt_workflow.bat`: the `pw` wrapper that resolves the venv python and forwards the arguments.

## Requirement clarifications

These rows record the choices settled in review (Q01 to Q08); each names the
question that settled it, the section where it is integrated, and the options
that were turned down.

| Area | Decision | Question | Integrated in | Rejected alternatives |
| --- | --- | --- | --- | --- |
| Auto-advance opt-out | Handoffs fire by default; an explicit "stop here" signal passed to the writing skill at invocation holds the chain at that step | Q01 | Confirmed rules, Acceptance criteria | Always fire with no opt-out; confirm on every handoff |
| Review command name | One name, `/review-ask-questions`, everywhere; no `/ask-questions` | Q02 | Gap item 11, Confirmed rules | Adopt `/ask-questions` as an alias; keep both names |
| Consolidate trigger | Auto-advance only once every open question is answered and no new one is raised | Q03 | Gap item 4, Confirmed rules, Acceptance criteria | Advance when a round adds nothing new; advance and list any leftover |
| pw --skill precedence | Report the step after the most advanced artifact, order draft, requirement, design, plan | Q04 | Gap item 11, Confirmed rules, Acceptance criteria | Least advanced wins; list every candidate |
| Split list scope | One entry per defined slug, no cap, in split order | Q05 | Gap item 7, Confirmed rules | Cap at three; reorder by type |
| Review hint form | Plain text carrying the document name is the guaranteed baseline; a per-host gray Tab-completable hint where it can be triggered, trigger still to study | Q06 | Gap item 5, Confirmed rules, Acceptance criteria | Gray hint required for acceptance; plain text only |
| Type something else | Pass the typed text through unchanged; no name check, no required document | Q07 | Confirmed rules, Acceptance criteria | Check the name and require a document; pass through with a warning |
| Host prefix | Auto-detect the host (`/` Claude, `$` Codex) with an explicit caller override | Q08 | Gap item 9, Confirmed rules, Acceptance criteria | Auto-detect only; require the host every call |
