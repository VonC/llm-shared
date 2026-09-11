# Specification review requestor instruction

Use this instruction when a specification writer delegates review of new open
questions. The writer remains responsible for the reviewed requirement,
design, or plan, including assessment, document edits, responses, convergence
wording, and human-authorized consolidation.

Read and follow `instructions/review-requestor.md` in full before running any
exchange command. That shared instruction owns durable coordination. This
specialized instruction supplies specification policy, authored content, and
the owning action only.

Before writing or editing the reviewed specification or any caller-owned
Markdown input, read and follow [`../rules/markdown.md`](../rules/markdown.md).
Apply those rules to every accepted edit and covered-wording edit before
publishing the next round.

## Exact policy for specification requestor operations

Pass this unchanged policy to every shared exchange operation:

```text
--family specification
--convergence-signal consolidation-ready
--another-round-label "Revise and review again"
--continue-owning-workflow-label "Consolidate"
```

Also pass `--document <exact-reviewed-specification>` and, when the current
effort has one, `--umbrella <exact-umbrella-draft>`. Do not pass an
implementation step for specification review. Let the shared core map a source
`design` document to the `design-specification` exchange type.

Never create, overwrite, rename, or delete a protocol artifact by hand. Run
all coordination through
`& "<LLM_SHARED_DIR>\bin\review_exchange.bat"`, and use paths returned by
that launcher instead of reconstructing nearby names.

## Ordered round sequence for specification requestors

1. Run `status` with the exact document, optional umbrella, and fixed policy.
   A `disabled` outcome returns control to the calling question workflow's
   existing human-review stop without creating exchange state.
2. For the first active review, run `activate`. If the observed state is
   `idle`, run `start` once. Do not restart a live identity.
3. Prepare separate ignored root `a.*` UTF-8 files for assessment, change
   summary, writer response, and optional guidance. Run
   `& "<LLM_SHARED_DIR>\bin\spec_review_request.bat"` with exact context and round flags plus two
   distinct ignored root output paths.
4. Pass the renderer's complete request output and substantive summary output
   to `publish-request`. Do not edit the published request or transcript.
5. Do not start, spawn, delegate, invoke, or message a reviewer. Run
   `wait-answer` immediately in this same requestor session through the shared
   requestor.
   Do not pass `--timeout-seconds` to `wait-answer`; use the complete timeout
   configured by `a.review-mode`. Read its one final JSON result after the
   bounded wait returns.
6. When an intermediate answer requests substantive changes, apply accepted
   edits, assess disagreement, then call `consume-answer` with the truthful
   `reviewed-work-changed` value and the `disagreement` flag only when the
   roles explicitly disagree.
7. If the exchange remains active, call `continue`, render the replacement
   round from the updated document and response, publish it, and wait again.
8. For a convergence recommendation, retain the answer, apply covered wording
   edits, present the human gate, and call `confirm` only with the exact choice
   the human selected.

Never read the versioned transcript as working context. After a wait or status
result reports an answer, read only the exact `paths.answer` file returned for
the current identity.

Reject this requestor task if an automated reviewer or a parent agent acting as
reviewer spawned, delegated, started, invoked, or messaged it. The reviewer
publishes an answer and waits; it never creates the requestor continuation.

## State handling for specification requestors

Use the shared diagnostic and state without recreating its classifier:

| Observed state | Specialized action |
| --- | --- |
| `disabled` | Return to the existing non-review-mode human stop. |
| `idle` | Activate, start round 1, render, and publish. |
| `round-in-progress` | Resume the expected requestor work for the persisted round. |
| `request-pending` | Keep the published request and wait for the exact answer. |
| `answer-pending` | Read only `paths.answer`, then assess the reviewer feedback. |
| `abandoned-request` | Call `reclaim`, then resume waiting with unchanged evidence. |
| `abandoned-answer` | Call `reclaim`, then assess the retained exact answer. |
| `abandoned-mid-round` | Call `reclaim`, then resume the persisted owner action. |
| `convergence-gate` | Re-present the recommendation, assessment, identity, and choices. |
| `owning-action-pending` | Resume authorized consolidation without asking again. |
| `escalated` | Stop for the shared human-resolution path; never reclaim it. |

Treat inconsistent, interrupted, and repair-required results exactly as the
shared requestor directs. An intact expired active round uses `reclaim`; an
escalated exchange never does.

## Authored inputs for specification request rounds

For each round, assess the current specification and its open questions. The
assessment must state whether questions are missing, whether existing options
and answers are sufficient, and whether reviewer wording suggestions were
applied. The change summary reports document changes since the preceding
round. The writer response explains accepted changes and any disagreement.

The paired renderer receives:

- the exact reviewed document and optional umbrella as flags;
- the current positive round as a flag;
- separate ignored UTF-8 files for assessment, change summary, writer
  response, and optional guidance; and
- separate ignored root outputs for complete request content and substantive
  transcript summary.

When a confirmed replacement round has guidance, preserve it verbatim under
the literal `Human guidance:` label. Keep the writer response and resulting
document changes separate from that guidance.

The shared publication operation validates that the request's umbrella,
reviewed specification, and round match the machine envelope. Do not author
the request and transcript summary independently, and do not parse one output
to construct the other.

## Intermediate feedback handling for specification requestors

Apply accepted substantive changes outside the exchange transition lock.
Record whether the reviewed work actually changed. If a recommendation cannot
be accepted because it conflicts with confirmed requirements, describe that
conflict and set the disagreement signal rather than silently ignoring it.

Intermediate rounds do not enter a human confirmation gate. Consume the exact
answer only after its recommendations have been applied or assessed, continue
the durable round, then publish the updated writer response automatically.
Shared no-progress and clarification bounds decide when automation must stop.

## Convergence gate for specification requestors

Apply covered wording edits before presenting the human gate. Tell the human
which edits are already present in the reviewed document, and show:

- the exact umbrella or `none`;
- the exact reviewed specification and round;
- the reviewer recommendation;
- the writer assessment; and
- `Revise and review again` and `Consolidate`.

The reviewer recommendation never authorizes consolidation.
Do not call `consume-answer` for a convergence recommendation. Retain the
answer as evidence while the shared state is `convergence-gate`.

When the human selects `Revise and review again`, pass that exact label to
`confirm`, include a guidance file only when guidance was supplied, and render
the replacement request. An unchanged document is valid for the replacement
round, while the shared bounds still prevent an unbounded loop.

When the human selects `Consolidate`, pass that exact label to `confirm` and
require `owning_action_authorized: true` before any owning action. If a later
session reports `owning-action-pending`, do not ask the human again.

## Authorized consolidation replay for specification requestors

After durable authorization, invoke the canonical
`consolidate-then-review-ask-questions` workflow on the exact reviewed
document. Do not add a private consolidation path and do not let the shared
core edit the specification. That canonical workflow first resets the index and
creates its required one-file pre-consolidation question snapshot commit before
it changes or strips the reviewed specification.

The consolidation handoff may start a new session. Normal `pw skill`
live-exchange precedence must return the settled document to this role. Verify
the settled decision marker: the open-ended questions section is absent and
the document contains its canonical clarification or decision record. Only
after that verification succeeds may the requestor call `complete`.

After `complete` removes the retained answer and coordination state, rerun `pw skill`.
Ordinary document routing then selects the next workflow phase. If consolidation
failed or the settled decision marker is absent, leave the authorization durable,
report the failure, and do not complete the exchange.

For a bare user `resume`, follow [the canonical resume instruction](review-resume.md)
through migration, role and identity gates, and automatic `claim` before
continuing this exact exchange. Keep its capability in session and pass the
paired ownership flags to every fenced operation. After exchange release, run
and follow `pw skill` immediately.
