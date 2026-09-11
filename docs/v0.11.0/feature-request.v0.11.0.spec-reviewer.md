# Respond to specification reviews

## Umbrella revision that introduces specification review responses

The review-mode umbrella separates the shared exchange protocol, the
specification writer, and the independent specification reviewer into distinct
responsibilities. The completed `review-exchange-core` requirement supplies
the identity, artifact, state-transition, bounded-wait, recovery, transcript,
and convergence contracts. The completed `spec-review-requestor` requirement
connects question-writing workflows to that core and owns specification edits,
repeated writer rounds, and the human-authorized consolidation decision.

This requirement adds the responder side of the specification exchange: one
focused reviewer role that reads the exact published request, assesses the
writer's open questions, and publishes either actionable changes or an
advisory convergence recommendation.

## User story for specification review responses

As an independent specification reviewer working in review mode, I want to
receive the exact question-bearing specification and its review request, so I
can identify missing questions, assess the proposed choices and answers, and
return constructive feedback without taking over the writer's authority to
edit or consolidate the specification.

## Current behavior in v0.11.0

- The shared review exchange can wait for a request, validate reviewer answer
  envelopes, publish an answer, append its transcript summary, and remove the
  consumed request through one lifecycle transition.
- The specification requestor can publish identity-bearing requests for
  feature requests, issues, design specifications, and implementation plans.
- No canonical `spec-reviewer` instruction defines how an independent reviewer
  assesses those requests or chooses an answer disposition.
- No reviewer-specific wrapper, answer renderer, template, or launcher turns
  the assessment into paired answer and transcript content.
- `pw` has no completed specialized reviewer handoff that binds the reviewed
  document returned by the workflow to the matching pending request.

## Gap to close for specification review responses

1. Add a canonical `spec-reviewer` role with thin LLM-specific adapters.
2. Accept the exact reviewed document selected by `pw` and derive its shared
   specification-exchange identity without scanning nearby documents.
3. Wait for and validate the matching request before reviewing any content.
4. Assess missing questions, question wording, available options, recommended
   choices, and proposed answers while leaving document edits to the writer.
5. Render and publish a paired answer artifact and transcript summary with
   either a change request or a convergence recommendation.
6. Use the shared publication transition so the answer becomes visible, the
   same feedback is appended to the sibling transcript, and the consumed
   request is removed according to the core recovery contract.
7. Preserve bounded waits, escalation, advisory convergence, and human-only
   consolidation authority.

## Expected specification reviewer workflow

### Reviewer activation and exact identity

The `spec-reviewer` role accepts the reviewed document path returned by `pw`.
Supported source documents are feature requests, issues, designs, and plans;
the shared mapping retains `feature-request`, `issue`, and `plan` and maps
`design` to the `design-specification` artifact type.

The reviewer derives the exact family, type token, version, slug, reviewed
document, and optional umbrella context through the shared exchange model. It
uses family `specification`, convergence signal `consolidation-ready`, another
round label `Revise and review again`, and owning-workflow label `Consolidate`
for every operation. It does not discover work by enumerating documentation
folders or reading versioned transcript history.

Live specification routing divides the two specialized roles by exchange
state. A `request-pending` exchange routes to `spec-reviewer`; every other
non-idle state routes to `spec-review-requestor`, which owns publication,
answer handling, convergence, and continuation. This requirement changes the
shared selection in `prompt_workflow_skill.next_command`; it does not inherit
the current requestor-only live route unchanged. When several exact live routes
compete, `pw` fails closed and reports every candidate instead of choosing one.
An `abandoned-request` routes first to `spec-review-requestor`, which reclaims
the stale request and restores `request-pending`; routing then reaches
`spec-reviewer`. The reviewer's own `reclaim` authority applies when its lease
expires during that reviewer session.

The project-root `a.review-mode` marker gates every exchange operation, not
only first activation. Removing it blocks new exchanges and suspends operations
and routing for existing exchanges: launchers return `disabled` with exit `3`
and `pw` surfaces no live review. The marker must be restored before live work
can finish or be cancelled through the shared lifecycle.

### Pending-request wait and validation

The reviewer waits through the shared `wait-request` operation for the exact
project-root `a.review-requested.type.vX.Y.Z.slug.md`. The wait is bounded by
the exchange policy and may observe only the derived request and coordination
paths.

Before assessment, the reviewer validates that:

- the envelope role is `requestor` and its family, type token, version, slug,
  round, reviewed-document path, and umbrella path match the invocation;
- the human-readable summary contains exactly one `Umbrella draft`,
  `Reviewed specification`, and `Review round` field matching the envelope;
- the request starts with one H1 title, uses `## JSON` as its first section,
  and starts each later top-level authored section at H2; and
- the live coordination record expects reviewer ownership for the same round.

An absent, stale, malformed, mismatched, duplicate, interrupted, or escalated
exchange fails closed through the shared diagnostic and recovery contract. The
reviewer does not repair protocol artifacts by hand or substitute a nearby
request.

The requestor's counterpart `wait-answer` call uses the project policy's full
review timeout and does not replace it with a shorter caller override. A normal
round must leave enough time for one complete reviewer turn; a hand-driven
request publication must not manufacture an early protocol escalation merely
because the human starts the reviewer separately.

### Independent specification assessment

The reviewer reads the full exact reviewed specification and the validated
request, using the request and open-question section as its focus. The current
document is authoritative: when its content conflicts with the published
request, the reviewer assesses the current text and returns the mismatch as
`changes-requested` rather than reviewing obsolete request wording.

It assesses the writer's questions independently and reports:

- questions that are missing, redundant, out of scope, or unclear;
- whether each option is materially distinct and includes relevant benefits,
  costs, and consequences;
- whether the recommended choice follows from the stated requirement, design,
  or implementation constraints;
- what answer the reviewer would choose for each existing question and why;
- wording corrections that preserve the intended decision; and
- disagreements or missing evidence that require another writer round.

The reviewer may propose replacement wording and concrete answers, but it does
not edit the reviewed document, resolve its open-question section, consolidate
it, or continue the writer's owning workflow.

When human guidance is present in a replacement request, the reviewer addresses
it explicitly while retaining identity, safety, and document-scope rules. For
each accepted problem, the reviewer gives a concrete proposed answer or
replacement wording whenever the evidence supports one; otherwise it states
that evidence is insufficient rather than inventing an answer.

A request whose current specification has no open question receives
`changes-requested` with instructions for the requestor to settle or cancel the
inconsistent round. A defect that belongs to an earlier document or lies beyond
the selected document's scope also receives a precise change request that names
the boundary and leaves correction or rerouting to the writer. Repeated
unchanged disagreement remains subject to the shared no-progress and
escalation limits.

### Answer rendering and publication

The reviewer-specific renderer produces two outputs from one assessment:

1. A complete answer for the ignored project-root
   `a.review-answer.type.vX.Y.Z.slug.md`, containing the exchange envelope,
   exact human-readable identity, constructive feedback, writer instructions,
   and one disposition.
2. A substantive transcript summary containing the same reviewer findings for
   the sibling `review.type.vX.Y.Z.slug.md` document.

The answer is valid Markdown with one H1 title, `## JSON` as its first section,
and later authored top-level sections at H2. The renderer accepts exact ignored
caller-owned inputs and writes caller-selected ignored outputs; it does not
mutate the request, answer, coordination record, or transcript itself.

The reviewer publishes both outputs through the shared `publish-answer`
operation. Shared publication validates the answer again, makes the answer
visible, appends the reviewer summary exactly once, and removes the consumed
request under the core's atomic transition and recovery rules. The specialized
role does not delete or append those artifacts independently.

### Reviewer disposition and writer authority

The answer disposition is one of:

- `changes-requested` when missing questions, substantive decision gaps,
  unsupported answers, disagreement, or more than wording-only edits require
  another automated writer round; or
- `convergence-recommended` when the specification questions and answers are
  settled apart from very small wording changes that the writer can apply
  before presenting the convergence gate.

A convergence recommendation is advisory. The reviewer cannot call
`Consolidate`, confirm convergence for the human, complete the exchange, or
delete the retained convergence answer. The requestor assesses the answer and
presents the human choices `Consolidate` and `Revise and review again`; only the
human's durable selection grants the corresponding owning-workflow authority.

The reviewer recommends convergence only when every in-scope decision is
settled and no more than wording-only edits remain. A substantive concern,
including one described as nonblocking, requires `changes-requested` or an
explicitly deferred requirement boundary rather than premature convergence.

### Bounded termination and recovery

The reviewer observes the shared timeout, lease, interruption, no-progress,
disagreement, inconsistency, and escalation rules. It may call `reclaim` only
for an intact abandoned request whose lease expired while reviewer ownership
remained authoritative. It never calls `cancel`, `resolve`, or `archive`:
those are human-authority operations, and cancellation additionally requires a
convergence gate the reviewer cannot own.

When the exchange escalates before a completed answer can be published, the
reviewer retains its assessment in caller-owned ignored input, reports that
human resolution is required, and stops. After `resolve` or `archive` creates a
fresh round, the reviewer revalidates the current document and request identity
and republishes the retained assessment with the fresh round identity rather
than discarding sound review evidence or publishing against a stale round.

A timeout or invalid state retains diagnostic evidence and stops for human
intervention. A reviewer session does not create an unbounded polling loop,
silently restart a round, or publish after ownership has changed.

## Acceptance criteria for specification review responses

1. A canonical `spec-reviewer` instruction and its thin LLM-specific adapters
   identify the reviewed document as their required input and reference the
   shared review protocol instead of restating it.
2. `pw` routes a `request-pending` specification exchange to `spec-reviewer`
   for the exact supported feature request, issue, design, or plan; every other
   non-idle specification state routes to `spec-review-requestor`, and multiple
   competing live routes fail closed with every exact candidate reported.
3. The reviewer derives the mapped artifact type, version, slug, reviewed
   document, umbrella, and current round from exact context without scanning
   documentation trees or reading transcript history.
4. The reviewer waits only through the shared bounded `wait-request` operation
   and fails closed for absent, malformed, stale, mismatched, escalated, or
   multiply resolved work.
5. The reviewer validates matching machine-readable and human-readable
   request identity before assessing the specification.
6. The assessment covers missing questions, wording, option quality,
   recommendations, proposed answers, and any disagreement requiring writer
   action.
7. The reviewer does not edit, answer in place, or consolidate the reviewed
   specification and does not continue the writer workflow.
8. A reviewer-specific template and renderer produce one answer artifact and
   one transcript summary from the same assessment without mutating exchange
   artifacts directly.
9. Every answer starts with an H1 title, uses `## JSON` as its first section,
   starts later top-level authored sections at H2, and carries exactly one
   matching umbrella, reviewed-specification, and round identity.
10. Answer publication uses the shared launcher with family `specification`
    and the registered labels, appends the reviewer summary once, exposes the
    answer, and removes the consumed request through one recoverable shared
    transition.
11. `changes-requested` gives the writer concrete work and another automated
    round; `convergence-recommended` remains advisory and enters the requestor's
    human-confirmation path without granting consolidation authority.
12. Timeout, abandonment, interruption, no progress, disagreement, and
    inconsistent state terminate or escalate through the core rules with
    evidence retained for recovery; the reviewer may reclaim only an intact
    abandoned request, while `cancel`, `resolve`, and `archive` remain
    human-authority operations it never invokes.
13. Automated tests cover all four document identities, exact pending-request
    routing, request validation, both dispositions, paired rendering,
    publication ordering, transcript append behavior, request removal,
    recovery after an interrupted answer transition, retained-assessment
    revalidation and republication after timeout recovery, and the
    reviewer-role authority boundary.
14. The specialized reviewer performs a bounded number of exact-path metadata
    checks and file reads per invocation; runtime work does not grow with the
    number of documents or historical transcript entries.
15. When escalation prevents a completed assessment from being published, the
    reviewer retains that assessment, stops for human resolution, revalidates
    the fresh round and current document, and republishes the same findings
    with fresh identity rather than discarding them or using a stale round.
16. The requestor's `wait-answer` call uses the complete configured review
    timeout without a shorter caller override, so one ordinary reviewer turn
    can finish before timeout escalation.

## File-based IO cost clarification for specification review responses

- Reviewer routing derives one supported document and its fixed exchange paths;
  it does not use `glob`, `rglob`, `iterdir`, or transcript reads.
- A normal round reads the exact reviewed specification, request, coordination
  record, and caller-owned assessment inputs a constant number of times.
- Rendering produces paired in-memory content and publication writes each
  target through the shared exact-path and atomic-transition contract.
- Waiting is bounded by policy and probes only the matching request and
  coordination state; elapsed time does not widen the candidate set.

## Requirement clarifications for specification review responses

| Question | Decision | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | Review the full specification, with the request and open questions as the focus. | Independent specification assessment | Review only the question section; review only the request summary |
| Q02 | Fail closed and report all exact candidates when several specification requests are pending. | Reviewer activation and exact identity; acceptance criterion 2 | Select the oldest request; add interactive routing |
| Q03 | Marker removal suspends new and existing exchange operations until the marker is restored. | Reviewer activation and exact identity | Permit live operations without the marker; cancel pending exchanges automatically |
| Q04 | Treat the current exact document as authoritative and report request drift as `changes-requested`. | Independent specification assessment | Reject every document change; trust an obsolete request summary |
| Q05 | Return `changes-requested` when the current specification contains no open question. | Independent specification assessment | Recommend convergence; escalate immediately |
| Q06 | Address recorded human guidance explicitly without letting it override identity, safety, or scope. | Independent specification assessment | Treat guidance as optional; let guidance override protocol rules |
| Q07 | Recommend convergence only when all in-scope decisions are settled and only wording edits remain. | Reviewer disposition and writer authority | Require a zero-edit document; permit unresolved nonblocking concerns |
| Q08 | Report an earlier-document or out-of-scope defect precisely and leave correction or rerouting to the writer. | Independent specification assessment | Escalate every cross-document finding; ignore the defect |
| Q09 | Give concrete non-editing wording or answers when evidence supports them and state when it does not. | Independent specification assessment | Give diagnosis only; edit the specification directly |
| Q10 | Retain a completed timed-out assessment, stop for human recovery, then revalidate and republish it with fresh identity. | Bounded termination and recovery; acceptance criterion 15 | Discard and reassess; stop the reviewer permanently |

## Boundaries and dependencies for specification review responses

- Depends on `review-exchange-core` for identity, storage, lifecycle, waiting,
  transcript, recovery, escalation, and human-confirmation policy.
- Depends on `spec-review-requestor` for request content, writer-side changes,
  repeated rounds, convergence assessment, and consolidation continuation.
- Includes the canonical reviewer instruction, thin host adapters, `pw`
  routing, answer template, paired renderer, launcher, and focused tests.
- Modifies two shared artifacts completed by `spec-review-requestor`: live-route
  selection and the requestor's `wait-answer` timeout bound.
- Excludes specification edits, consolidation, code-review roles, and the final
  review-mode Diataxis documentation set assigned to later umbrella items.

## Code references for specification review responses

- `tools/review_exchange_core.py`: owns bounded request waiting, answer
  validation and publication, transcript append, request consumption, recovery,
  and reviewer ownership transitions.
- `tools/review_exchange_cli.py`: exposes `wait-request` and `publish-answer`
  through the shared command adapter.
- `tools/review_exchange_models_envelope.py`: validates role, disposition,
  round, context, and human-readable identity fields.
- `tools/prompt_workflow_review.py`: derives exact specification contexts and
  observes live review state without transcript reads.
- `instructions/review-requestor.md`: defines the shared role boundary and
  reserves reviewer operations for a specialized reviewer adapter.
- `instructions/spec-review-requestor.md`: defines request content, writer-side
  repeated rounds, and the human-authorized consolidation boundary consumed by
  this complementary role.
