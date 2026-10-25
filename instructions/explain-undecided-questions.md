# Explain undecided specification questions

Use this workflow to explain and record human decisions for the exact
requirement, issue, design, or implementation plan selected by the user.
It is the requestor's human discussion phase after specification convergence.
Do not take a reviewer role, consolidate, stage, or commit through this skill.
Preserve every existing question ID, option, recommendation, and explanation.

## Enter or resume the discussion

Read [the shell rules](../rules/run_commands.md). Resolve `<LLM_SHARED_DIR>`
from this canonical file's parent `instructions` directory. Resolve the exact
document from the user's path or the unambiguous active specification; never
pick between several documents by modification time.

For a live review, use [review-resume.md](review-resume.md) for identity and
ownership pickup when needed, then [spec-review-requestor.md](spec-review-requestor.md).
Only enter the discussion at its `convergence-gate`. If a round is pending,
finish that requestor round first. An already authorized owning action follows
its durable authorization; this skill does not reset it. With no live exchange,
the user may request explanations directly; retain the independent-review gate
for the later handoff and do not claim independent convergence occurred.

Selecting `Explain undecided questions`, or explicitly invoking this skill,
authorizes recording the user's answers and a follow-up independent review
after all questions are decided. Tell the user this when starting. It does not
authorize consolidation. Honor a later hold or scope correction.

Run the read-only scanner from the consuming project:

```powershell
& "<LLM_SHARED_DIR>\bin\question_decisions.bat" <document-path>
```

Read its JSON and exit code. An `Answer to Qxx` heading or a recommendation is
not a human decision. Only explicit records in that answer section count.
Exit 2 or diagnostics require reconciliation before advancing; never treat a
failed scan as zero remaining questions. The
[scanner reference](../wiki/reference/question-decisions.md) defines the fields.

Keep a task-owned continuation note named
`a.question-explanation.<document-stem>.local.md` in the configured artifact
home, using [the state template](../templates/question-explanation-state.template.md).
Resolve that home under [artifact_files.md](../rules/artifact_files.md), or use
the validated home returned by the live exchange. This note is not protocol
coordination or a reviewer `QUESTION_STATE` capture. Never put ownership tokens
in it. Update it after each explanation, recorded answer, and review handoff;
write a complete temporary replacement and replace the old note atomically.

Read an existing note before starting a new batch. Reconcile its document,
exchange, round, digest, and question identities with current disk and protocol
state. A digest change demands reconciliation, not an automatic reset. If IDs
were removed or reordered, do not silently recalculate progress or assume a
decision. Resolve the changed scope with the user when evidence is insufficient.
If appended questions or a reopened earlier question fall outside the captured
batch, reconcile the batch scope before displaying progress. Never display a
negative percentage or one above 100%, or silently reset `I` to hide the change.

## Explain one question and record one decision

For a new batch, save `I` as the first undecided question's **position** and
`Total` as `question_count`. Save their question IDs and the ordered batch IDs
too. Keep `I` fixed through answers and pauses; the scanner never owns it.
Use document positions for arithmetic, so non-contiguous numeric IDs work.
For the current position `x`, display
`{question-id}/{last-question-id} {percentage}%`, where IDs include their `Q`
prefix, and:

```text
percentage = round(100 * (x - I + 1) / (Total - I + 1))
```

This is position in the explanation sequence, not a claim that the displayed
question has been decided. Q59 through Q73 yields `Q59/Q73 7%` at the start
and `Q73/Q73 100%` on the last question. A single-question batch displays 100%
but remains awaiting a decision until the user answers. An empty batch has no
percentage. Skip already decided questions without changing `I` or renumbering.

1. Select the first remaining undecided question from a fresh scan. Read its
   full block and dependencies, including any relevant earlier user comments.
2. Explain it with [question-explanation.template.md](../templates/question-explanation.template.md):
   concrete behavior, realistic example, options and tradeoffs, recommendation,
   and effects on other questions. Keep it within the document's scope.
3. Save `awaiting-user-decision`, the question ID, and whether the explanation
   was delivered. Ask for the user's choice or clarification and wait. Do not
   answer on their behalf or advance because they asked for more explanation.
4. On an explicit choice, update only that question's answer and necessary
   clarifications. Replace its active pending marker with
   `User decision: confirmed — <choice and agreed qualifications>`, with the
   rationale, relevant comments, and decision date nearby. Preserve the
   historical recommendation even when the user chooses differently. Existing
   `Confirmed by the user: ...` records remain valid and need no conversion.
   Move superseded status prose into a clearly quoted historical note if it is
   needed; do not leave both pending and confirmed as active records.
5. An explicit user decision that a conditional question is inapplicable can
   be recorded as confirmed with its condition and reason. A dependent question
   is not automatically decided by another answer. Record a deferred choice as
   `User decision: deferred`; it remains undecided.
6. Rescan the whole document without `--after` before choosing the next item.
   `--after Qxx` is a navigation aid only; earlier unresolved questions still
   count. Persist `explaining` with the next question, or the final phase below.

Targeted answer/clarification edits are authorized here; do not run `oqm --strip`
or regenerate the entire question section merely to record an answer. Keep
decision comments in the document, with a concise change list in the private
note for the next review request. If an answer reopens an earlier decision,
record that explicitly rather than retaining a misleading confirmed status.

## Finish with a fresh independent review

When a successful full scan shows zero undecided questions, save
`follow-up-review-required` **before** any review command, and tell the user:

> All questions now have recorded user decisions. A new review round must
> examine those decisions and your comments for inconsistencies and identify
> any additional questions they raise.

The retained convergence answer describes the earlier document. It does not
review the subsequent human decisions and comments. Keep all question blocks.
If the skill starts with zero undecided questions and no saved discussion or
post-convergence changes, report that fact and return to the ordinary gate;
do not invent an explanation batch or a required duplicate review.

Unless the user has placed a hold, use the already recorded follow-up authority:

- At the same live `convergence-gate`, the specification requestor calls
  `confirm` with the existing exact label `Revise and review again`, including
  the user's guidance. Never send `Explain undecided questions` to `confirm`.
- If there is no live exchange, apply
  [specification-review-gate.md](../rules/specification-review-gate.md) and enter
  the specification requestor for this exact document. This skill's explicit
  invocation authorizes the independent review setup, but does not create or
  contact a reviewer session; role isolation still applies.

The replacement request must identify the decided questions, recorded comments,
and changes since convergence, and ask for full-specification consistency,
effects on earlier decisions and related documents, and missing/new questions.
Reviewer recommendations cannot overwrite human choices; surface conflicts.
Use the ordinary requestor publication and exact-answer wait. Before publishing
after an interruption, inspect the existing exchange: resume an advanced or
already-published round, never confirm or publish it twice.

After successful publication, record `follow-up-review-in-progress`, the round
and publication evidence in the note. At subsequent convergence, mark this
batch `reviewed` with the new round and reviewed-document evidence. New
undecided questions receive a new batch and starting `I` when the human selects
explanation again. With none remaining, present the ordinary consolidation or
another-review choices. All decisions plus review never auto-consolidate.

## Pause and resume

[pause-session.md](pause-session.md) copies the phase, fixed `I` and endpoint,
current/next IDs, decision status, follow-up authority, and exact next action
into its snapshot, linking the continuation note. Resume rescans and reconciles:

- `explaining`: explain the first still-undecided question using saved `I`.
- `awaiting-user-decision`: restore the pending question; retain any delivered
  explanation and continue its clarification or answer rather than skipping it.
- `follow-up-review-required`: initiate the authorized replacement review.
- `follow-up-review-in-progress`: resume that round through review ownership.
- `reviewed`: use the current convergence gate, without launching a duplicate.

A saved phase never restores review ownership or grants missing permission.
If a user's answer was durably recorded just before interruption, the scan may
advance the stale note. If zero remain, move to the required-review phase even
when the pause occurred between recording the last answer and updating the note.
