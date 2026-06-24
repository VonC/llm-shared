# Passing the Baton

- Type: feature-request

## Goal of this document

I need to identify which instructions in the main workflow have a handoff to the next instruction, and which ones only provide guidance for the next step. The goal is to make sure that the instructions that require a handoff have a strong automated next step instruction, meaning it should instruct to call the next skill without waiting for user review or go ahead.

I also need for pw (prompt_workflow) to assiste the handoff by providing a deterministic way to get some of the names or elements needed for the next instruction, so that the handoff can be automated. For example, if an instruction produces a document with a name like `feature-request.vX.Y.Z.<slug>.md`, the handoff should provide a way to get that name and pass it to the next instruction.

## Current state of the instructions

### Instruction chaining matrix

This table lists the instruction bodies in the order they are used by the
main workflow described in `README.md` and `DEVELOPMENT.md`. The second column
records whether the instruction itself chains to another instruction, either
through an explicit handoff mechanism or through simple next-step guidance.

| Instruction | Chaining status |
| --- | --- |
| `instructions/process-draft.md` | Simple conditional handoff. Step 7 points a single-topic draft to `write-requirement.md`, or a multi-topic draft to `split-and-define.md`; it is guidance, not `pw handoff`. |
| `instructions/split-and-define.md` | Simple manual continuation. It creates the ordered list of feature requests and issues; `DEVELOPMENT.md` says to run `write-requirement.md` for each item. |
| `instructions/write-requirement.md` | Simple next-step note. It says open questions are handled later by `review-ask-questions.md`; no automatic handoff. |
| `instructions/review-ask-questions.md` | Manual review-loop step. It appends question blocks; the next step is `consolidate-then-review-ask-questions.md`, but there is no automatic handoff. |
| `instructions/consolidate-then-review-ask-questions.md` | Manual loop/ready signal. It stops when there are no new questions and says the document is ready for the next phase; no automatic handoff. |
| `instructions/write-design.md` | Simple next-step note. It says open questions are addressed later by `review-ask-questions.md`; no automatic handoff. |
| `instructions/review-ask-questions.md` on the design | Manual review-loop step. Same instruction as above, reused for design review before consolidation. |
| `instructions/consolidate-then-review-ask-questions.md` on the design | Manual loop/ready signal. Same instruction as above, reused until design is ready for planning. |
| `instructions/write-plans.md` | Simple next-step note plus `pw` workflow placement. It says the plan review uses `review-ask-questions.md` on the plain plan only and is wired between plan writing and implementation; no handoff section in the instruction body. |
| `instructions/review-ask-questions.md` on the plan | Manual review-loop step. Same instruction as above, reused for plan review. |
| `instructions/consolidate-then-review-ask-questions.md` on the plan | Manual loop/ready signal. Same instruction as above, reused until coding can start. |
| `instructions/implement-step.md` | Automatic `pw handoff`. Its `## Handoff` section runs `pw handoff check <x>`, which writes an `implementation-check.md` prompt and explicitly authorizes running the returned prompt immediately. |
| `instructions/implementation-check.md` | Automatic `pw handoff`. Its `## Handoff` section runs `pw handoff after-check <x>`; `pw` routes `No` to `implement-missing-step.md` or `Yes` to `group-commits-msg.md`. |
| `instructions/implement-missing-step.md` | Automatic `pw handoff`. Its `## Handoff` section runs `pw handoff check <x>`, returning to `implementation-check.md` for the same step. |
| `instructions/group-commits-msg.md` | Chain stop at the commit gate. It writes and formats `a.commit`, then waits for the user's `go ahead` before validation and real commits; no automatic next instruction. |
| `instructions/update-merge-commit-msg.md` | Conditional handoff to `prepare-release`. When `a.prepare-release.active` exists, it returns control to `prepare-release.md`; otherwise it finishes standalone after the merge-message review flow. |
| `instructions/prepare-release-notes.md` | Conditional handoff to `prepare-release`; standalone next-step guidance otherwise. With `a.prepare-release.active`, it returns control to `prepare-release.md`; when run directly, it tells the user to run `brel`. |
| `instructions/prepare-release.md` | Umbrella chain with flag-file handoffs. It calls `group-commits-msg.md`, `update-merge-commit-msg.md`, `prepare-release-notes.md`, and the `ghog day` loop, then stops before `brel`. |

### Supporting instructions

These instruction files are not part of the main first-to-last
feature-to-release path, or they are invoked only as helper flows from that
path.

| Instruction | Chaining status |
| --- | --- |
| `instructions/groundhog.md` | Helper loop. It drives `ghog day` until the test objective is met; callers resume their own workflow after it exits green. |
| `instructions/fix_slow_test.md` | Helper loop inside groundhog. It sends control back to `groundhog.md` after a slow-call fix; no standalone workflow handoff. |
| `instructions/activity-report.md` | Standalone workflow. It pauses for review, renders HTML/PDF after `go ahead`, then confirms and hands back; no next instruction. |
| `instructions/git-history-report.md` | Standalone report instruction. It has a hand-off note for the report artifact, but no automatic next skill. |
| `instructions/review-and-update-project-docs.md` | Standalone documentation maintenance instruction. It reports after updating docs; no chaining. |
| `instructions/split-large-file.md` | Standalone refactoring instruction. It uses `ghog day` for verification, but does not hand off to another instruction. |
| `instructions/write-release-notes-summary.md` | Helper/standalone release-summary writer. It drafts the summary structure used by release notes; no automatic handoff. |

## Updates needed

### Handoff needed

Here is the list of instructions from which I need an handoff with a strong automated next step instruction, meaning it should instruct to call the next skill without waiting for user review or go ahead:

- `instructions/write-requirement.md`: it must call `/review-ask-questions.md` of the `feature-request.vX.Y.Z.<slug>.md` or the `issue.vX.Y.Z.<slug>.md` it just produced.
- `instructions/write-design.md`: it must call `/review-ask-questions.md` of the `design.vX.Y.Z.<slug>.md` it just produced. The handoff must be there, and must automate that call.
- `instructions/write-plans.md`: it must call `/review-ask-questions.md` of the `plan.vX.Y.Z.<slug>.md`. The handoff must be there, and must automate that call. (note: write-plans also produce a validation plan, but this one can be left alone.)
- `instructions/consolidate-then-review-ask-questions.md`: its handoff must be completed to automatically call the next step (provided by pw) if there are no more open questions to ask on the current document. The next step is to call the next instruction in the main workflow, which is `write-design.md` for a feature request or issue, or `write-plans.md` for a design, or implement first step for a plan. pw must be able to provide the next instruction name and the document name to call it on, so that the handoff can be automated. For implementation, pw must be able to successfully extract the name of the first step to implement from the plan, and provide it to the next instruction.

### Hint needed

Here is the list of instructions from which I need an hint of what the next step should be. If that hint can be ready in gray in the prompt (for me to use the Tab key to auto-complete), please provide it in gray. If not, please provide it in normal text.

- `instructions/review-ask-questions.md` must leave as hint: `/consolidate-then-review-ask-questions` on the `<doc type>.vX.Y.Z.<slug>.md` it just reviewed. Meaning the hint must include the document name being reviewed. There is no automatic chaining here, since a review is needed. But since the next step is a consolidation, it should be clear (as a hint ready to be auto-completed) that the next step is to consolidate the questions and then review them.

### Multiple next steps

The Handoff must instruct the LLM to make a multi-choice list of the next steps, and then call the next skill based on the choice made. Each multi-choice must come with a last choice named "Type something else" that allows the user to type a different instruction name. The user must be able to select a choice (or type in the last item) to trigger the next skill with the right argument.

The multi-choice list must apply for the following instructions:

- `instructions/process-draft.md` must make the LLM ask to chose between:
  - `instructions/write-requirement.md` on the `draft.vX.Y.Z.<slug>.md` it just produced,
  - `instructions/split-and-define.md` on the `draft.vX.Y.Z.<slug>.md` it just produced, (or "type something else" to allow the user to type a different instruction name)

  Here the pw must be able to provide the name of the draft it just produced, so that the user can select one of them to continue with the next instruction.

- `instructions/split-and-define.md` must make the LLM ask to chose between:
  - `instructions/write-requirement.md` on the `feature-request.vX.Y.Z.<slug1>.md` or `issue.vX.Y.Z.<slug1>.md` it just defined from its split of `draft.vX.Y.Z.<slug>.md`,
  - `instructions/write-requirement.md` on the `feature-request.vX.Y.Z.<slug2>.md` or `issue.vX.Y.Z.<slug2>.md` it just defined from its split of `draft.vX.Y.Z.<slug>.md`,
  - `instructions/write-requirement.md` on the `feature-request.vX.Y.Z.<slug3>.md` or `issue.vX.Y.Z.<slug3>.md` it just defined from its split of `draft.vX.Y.Z.<slug>.md`,

  Here the pw must be able to provide the list of slugs it just defined, so that the user can select one of them to continue with the next instruction.

## Updates expected

### Written instructions updates

The md files needs to be updated to include the handoff and hint instructions described above. The handoff instructions must be clear and deterministic, providing the necessary information for the next instruction to be called automatically. The hint instructions must be provided in a way that allows for easy auto-completion.

Whenever pw can provide the name of a document or a list of slugs, it must be included in the handoff or hint instructions to ensure that the next instruction can be called with the correct arguments.

### pw update: skill mode

The pw (prompt_workflow) needs to be updated to detect the handoff and hint instructions in the md files, and to provide the necessary information for the next instruction to be called automatically. This includes providing the name of a document or a list of slugs when needed. You need to consider each instructions listed above and analyze how the pw can deduce the next instruction name and the document name to call it on, so that the handoff can be automated. (or if it is already able to do so)

Right now, pw provide a sentence "Follow the instruction... Context is ..."

I need a `--skill` mode that will provide the same message (or new messages) but simply returning the ext string the LLM needs (instead of a user-facing message), like "/consolidate-then-review-ask-questions on the `<doc type>.vX.Y.Z.<slug>.md`", or "/write-design on the `design.vX.Y.Z.<slug>.md`", or "/write-plans on the `plan.vX.Y.Z.<slug>.md`", or "/implement-step on the first step of the `plan.vX.Y.Z.<slug>.md`". Note the lack of backtick around the /skill-name, since the LLM will need to interpret /skill-name directly as a command to call the next skill.

pw must somehow detect if it is in a Claude or Codex session, because the skill will be called with / in Claude, but with $ in Codex. So the skill mode must return the right prefix for the next skill call, depending on the LLM being used.

In `--skill` mode, there is no context listing all the previous document to consider, only /skill-name and the document name to call it on. The LLM will be able to call the next skill directly, without any user-facing message or context.

Depending on the step, pw --skill might return a multi-line string with a list of next steps, each one starting with /skill-name and the document name to call it on. The LLM will be able to select a choice (or type in the last item) to trigger the next skill with the right argument, but the handoff must instruct the LLM to leave the last choice for "Type something else", that item being a text entry field. That last item is not provided by pw, but is left for the LLM to provide as a text entry field for the user to type in a different instruction name.

`pw --skill` must be able to recognize there is a new draft on the main branch (or a branch not named after the slug) and propose /process-draft on the new `<draft.vX.Y.Z.<slug>.md>`". But if it sees, in addition to the draft, other `vX.Y.Z.<slug>` documents, it must use them to derive the step it is in, and provide the right next skill to call, with the right document name. For example, if it sees a `draft.vX.Y.Z.<slug>.md` alone, but already in the right branch (named after the slug), it must propose `/write-requirement on the feature-request.vX.Y.Z.<slug>.md` as the next skill to call.

If it sees a `feature-request.vX.Y.Z.<slug>.md` or `issue.vX.Y.Z.<slug>.md`, it must propose `/ask-questions on the feature-request.vX.Y.Z.<slug>.md` or `/ask-questions on the issue.vX.Y.Z.<slug>.md` as the next skill to call, if it does not see any consolidation table in the document. If it sees one, then it can take a parameter from the LLM to determine if the next step is still `/consolidate-then-review-ask-questions on feature-request or issue.vX.Y.Z.<slug>.md` or `/write-design from the feature-request or issue.vX.Y.Z.<slug>.md`.
