# Independent specification review before phase advancement

Apply this gate after reviewing or consolidating a requirement, issue, design,
or implementation plan, including a pass that raises no new questions.
Review requests and question answers do not authorize consolidation. Keep the
question blocks and recorded answers unless the express-intent gate in
[`consolidate-then-review-ask-questions.md`](../instructions/consolidate-then-review-ask-questions.md)
has passed. A combined-skill invocation with only a document path does not pass it.
Answered questions, a decisions table, a clean working tree, and the writer's
own assessment are not evidence of an independent review.

## Check review authority for the exact specification

Honor `stop here` or an explicit human hold before creating an exchange.
When this invocation replays an already authorized `Consolidate` action,
verify that the exact exchange reports `owning-action-pending` and
`owning_action_authorized: true` through the requestor workflow. Return the
settled result to that requestor for completion; do not start a duplicate
exchange or automatically launch the next phase.

Otherwise, freshly sample review mode with the canonical full-path
`rvw_status.bat` launcher. State its result. Do not infer mode from an earlier
listing, question count, or transcript filename.

- With review mode enabled, route the exact specification to the specialized
  requestor, even when there are no open questions. Ask for independent
  assessment of the whole specification and any missing questions; do not
  manufacture questions to make routing work. Preserve existing live exchange
  precedence and the independent reviewer role boundary.
- With review mode disabled, report that independent review has not been
  performed and stop before the next phase. An explicit human request for an
  independent review authorizes enabling the marker through the documented
  review-mode setup, then publishing the request. Otherwise leave the marker
  unchanged. A failed status check is an error, never permission to advance.
- A human may explicitly waive independent review for the exact specification.
  Report that waiver accurately. Choosing question answers or invoking
  consolidation is not a waiver.

## Keep review evidence separate from author decisions

A review is published only after `publish-request` reports `published` for the
exact identity and round. It is not complete merely because the request exists.
Use the shared exchange's answer, convergence and human-authorization gates;
never present Q01-style author decisions as reviewer findings.

Reviewer convergence and explicit user decisions are separate. A proposed
answer can pass review while remaining undecided. The human may enter
[explain-undecided-questions.md](../instructions/explain-undecided-questions.md)
at convergence; that discussion retains the exchange and every question block.
After its decisions and comments are recorded, a fresh independent round must
check their consistency and find any newly necessary questions. Earlier
convergence does not cover those subsequent changes. Honor an explicit review
waiver accurately, but never infer one from answering the final question.

The ordinary next-phase handoff is available only after this gate has been
satisfied by the existing review workflow or an explicit human waiver. A
no-question pass must never bypass this gate. A printed next command describes
routing; it does not independently authorize execution.
