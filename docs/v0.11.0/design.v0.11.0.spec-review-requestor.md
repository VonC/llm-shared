# Design v0.11.0 -- Specification Review Requestor

Reference feature request:
[feature-request.v0.11.0.spec-review-requestor.md](feature-request.v0.11.0.spec-review-requestor.md)

---

## Context for v0.11.0 specification review requests

The shared review exchange now supplies exact-path coordination, durable
round state, transcript persistence, convergence authorization, and recovery.
This design adds the specification-writer side of that exchange. It connects
the existing question workflows to the shared requestor role without moving
requirement authorship or consolidation decisions into the transport layer.

## Scope for v0.11.0 specification review requests

The v0.11.0 outcomes are:

1. Specification writers delegate newly authored open questions to an
   automated reviewer when review mode is active.
2. A specialized requestor composes specification feedback and drives repeated
   rounds through the shared exchange contract.
3. Convergence returns authority to the human before the owning writer
   consolidates and continues its normal workflow.

Everything else is supporting design context for those outcomes or explicitly
deferred.

### In scope for v0.11.0 specification review requests

- Activation from feature-request, issue, design, and plan question workflows.
- Specification-specific request content, identity, artifact naming, and
  transcript summaries.
- Writer-owned application of reviewer feedback across intermediate rounds.
- Human-authorized convergence choices and continuation into consolidation.
- Canonical and host-specific instruction surfaces for the complementary role.

### Deferred from v0.11.0 specification review requests to later umbrella topics

- The independent `spec-reviewer` role and its answer-generation behavior.
- The implementation-code requestor and code reviewer roles.
- End-user documentation for the complete review-mode feature set.
- Any change to the review exchange transport, persistence, or recovery model.

---

## Confirmed technical facts for v0.11.0 specification review requests

**The shared requestor contract already exists**: the canonical
`review-requestor` instruction delegates every lifecycle operation to
`review_exchange.bat`, requires caller-owned request and summary inputs, and
keeps specialized analysis and owning actions outside the protocol layer.

**The exchange core already recognizes specification identities**: supported
types are `feature-request`, `issue`, `design-specification`, and `plan`; the
launcher maps a reviewed `design.*` filename to `design-specification` before
constructing the exchange identity.

**Question workflows already own specification mutation**:
`review-ask-questions` and `consolidate-then-review-ask-questions` place and
strip open-question sections through `oqm`, but neither canonical instruction
currently delegates those questions to a specification requestor in review
mode.

**Workflow routing is disk-derived**: `pw skill` resolves the current effort
from the branch and on-disk documents, while its explicit `--after-write`
surface routes a newly written requirement, design, or plan to its review.

**A canonical host adapter pattern is present**: the existing
`.agents/llm-shared/instructions/review-requestor.md` adapter points to the
shared coordination instruction, so the specialized role can follow the same
single-source pattern.

---

## Current behavior for v0.11.0 specification review requests

The current question workflows finish by returning control to a human or by
following the normal settled-document handoff. They do not distinguish review
mode and do not initiate a requestor/reviewer exchange.

```txt
specification writer
  -> author or consolidate open questions through oqm
  -> questions remain: stop for human review
  -> no questions remain: continue through pw
```

The shared exchange can coordinate a specification round when invoked with an
exact document and family policy, but no specialized specification-writer role
currently supplies the content or owns the repeated-round assessment.

## Target behavior for v0.11.0 specification review requests

The target flow preserves the existing behavior unless both new questions and
the project-root review-mode marker are present. A direct `stop here` hold is
resolved before any exchange operation.

```txt
specification writer places one or more new questions
  -> explicit hold: stop with no exchange artifact
  -> review mode absent: retain the existing human stop
  -> review mode present: delegate through pw to specification requestor
       -> shared requestor coordinates publication and waiting
       -> specialized writer assesses and applies intermediate feedback
       -> repeated automated rounds continue within shared bounds
       -> convergence enters the durable human gate
            -> Revise and review again: publish a replacement round
            -> Consolidate: owning writer consolidates, then completes exchange
```

A no-question pass never creates an empty exchange. It follows the existing
settled-document continuation.

---

## Activation and role boundaries for v0.11.0 specification review requests

### Question-present activation boundary

The two question workflows remain responsible for deciding whether they have
placed at least one new question. Only that condition reaches review-mode
delegation. Marker absence and an explicit hold are non-review outcomes, so
neither may create or repair coordination state.

Each question workflow keeps only that trigger detection and one delegation
reference. Both delegate to the same specialized specification requestor,
which owns the full specification-round orchestration path instead of
duplicating it in either originating workflow.

The delegated family policy is fixed for the lifetime of the exchange:

- family: `specification`;
- convergence signal: `consolidation-ready`;
- another-round label: `Revise and review again`;
- continue-owning-workflow label: `Consolidate`.

### Specialized writer and shared requestor ownership

The specialized writer owns the reviewed document, open-question analysis,
request feedback, reviewer-change assessment, document edits, convergence
summary, and human-authorized consolidation. The shared requestor owns status,
activation, publication, waits, answer consumption, continuation,
confirmation, escalation, recovery, and completion.

This boundary keeps the coordination instruction role-neutral. Specification
vocabulary and judgments stay in the specialized role, while all durable state
transitions stay in the exchange core.

## Request composition and identity for v0.11.0 specification review requests

### Artifact identity derived from the reviewed specification

The exact reviewed filename supplies version and slug. Its source prefix is
resolved through the core mapping: `design` becomes `design-specification`,
while `feature-request`, `issue`, and `plan` remain unchanged. Request, answer,
coordination, tombstone, and transcript identities all use that resolved type.

The request envelope and authored identity section carry the same exact
umbrella path or `none`, reviewed specification path, and positive round. The
umbrella identity comes from the `pw`-resolved effort's umbrella draft; an
effort with no umbrella uses `none`. The core validates those values before
publication.

### Authored request and transcript boundary

The complete request is valid Markdown with one H1 title, `## JSON` as its
first section, and H2 authored sections after the envelope. It asks the
reviewer to inspect missing questions, existing options and answers, and
possible wording improvements. Its conclusion names the exact project-root
answer and requires publication through the shared exchange.

The specialized renderer accepts one validated specification-round input and
returns the complete request plus its substantive transcript summary as one
paired result. Both outputs therefore share identity, round, assessment, and
change-summary data without deriving the summary by parsing Markdown headings
or authoring the two identities independently.

The transcript summary contains the requestor's substantive feedback without
fixed coordination boilerplate. The shared exchange appends it under the
requestor role and round; the writer does not reread the transcript as working
context.

## Repeated rounds and convergence for v0.11.0 specification review requests

### Intermediate change rounds

For a substantive change request, the writer reads only the answer path
returned by the exchange, applies accepted changes, records whether the
reviewed work changed and whether a disagreement exists, consumes the answer,
and continues the active exchange. The replacement request carries the new
round identity and reports the applied changes.

Shared timeout, abandonment, no-progress, disagreement, and inconsistent
artifact rules stop the automated dialogue. The specialized role reports those
outcomes but does not reproduce their state machine.

When a later session resumes a matching live exchange, it continues an intact
round directly while its lease remains current. If that active lease expired,
the expected actor renews the round in place through the shared `reclaim`
operation before continuing. An escalated exchange is not reclaimed and still
requires human resolution.

### Convergence and owning action

For convergence-recommended feedback, the writer applies covered wording edits
before the gate and states that they are already applied. The answer remains as
evidence while the human sees the reviewer recommendation, the writer's
assessment, exact identity, and the two registered choices.

`Revise and review again` starts a replacement round even when the human gives
no guidance and the document is unchanged. Shared bounds prevent an automated
loop; an unchanged repeated convergence result returns to the human gate. When
guidance is supplied, the replacement summary preserves it verbatim as a
literal `Human guidance: <text>` line and presents the writer's response and
resulting document changes separately.

`Consolidate` durably authorizes the owning writer to integrate answers, remove
the open-question section, add the decision record, and continue its normal
workflow. The requestor invokes the canonical consolidation workflow on the
exact reviewed document and carries the durable authorization across that
handoff. The exchange completes only after the canonical owning action
succeeds.

---

## File-based IO cost clarification for v0.11.0 specification review requests

- `pw` resolves the current effort once, then checks a bounded set of exact
  reviewed-document and coordination paths before ordinary routing.
- The specialized renderer consumes one validated round input and writes its
  paired request and transcript summary once; it does not parse one generated
  Markdown artifact to construct the other.
- Shared exchange operations retain their constant exact-path reads, atomic
  writes, and bounded transcript-tail repair behavior.
- Resumption reads durable coordination state but never scans or reloads the
  sibling transcript.

## Design decisions for v0.11.0 specification review requests

| Question | Decision | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | Resolve an exact matching live exchange before ordinary document-derived routing; renew an intact expired round through `reclaim`, while escalated state requires human resolution. | Repeated rounds and convergence / Intermediate change rounds | Originating-session-only invocation; a separate manual resume command. |
| Q02 | Render the complete request and substantive transcript summary together from one validated specification-round input. | Request composition and identity / Authored request and transcript boundary | Parse the summary from request Markdown; author both outputs independently. |
| Q03 | Keep trigger detection and one delegation reference in each question workflow, with all round orchestration in one specialized requestor. | Activation and role boundaries / Question-present activation boundary | Duplicate orchestration in both workflows; move specification trigger logic into the role-neutral requestor. |
| Q04 | Invoke the canonical consolidation workflow on the exact reviewed document after durable authorization, and complete the exchange only after it succeeds. | Repeated rounds and convergence / Convergence and owning action | Add a private requestor consolidation path; let the shared core mutate specifications. |
| Q05 | Preserve override guidance verbatim as `Human guidance: <text>`, followed separately by the writer response and resulting changes. | Repeated rounds and convergence / Convergence and owning action | Paraphrase the guidance; omit it after applying document changes. |

## Acceptance cases for v0.11.0 specification review requests

| Scenario | Expected outcome | Reason |
| --- | --- | --- |
| No new open question | Continue the settled workflow without exchange artifacts. | Review mode is question-driven, not a general final-review pass. |
| New questions with review mode absent | Keep the existing human-review stop. | The feature remains opt-in. |
| New questions with an explicit hold | Stop before status or activation and create no coordination artifact. | Direct human control takes priority for the invocation. |
| New design questions with review mode active | Use specification type `design-specification` and publish round 1 through the shared exchange. | The core mapping is the identity source of truth. |
| Reviewer requests substantive changes | Apply accepted changes, consume the answer, and publish the next automated round. | Intermediate rounds do not require a human gate. |
| Reviewer recommends convergence with wording edits | Apply the wording, retain the answer, and enter human confirmation with an applied-edits statement. | The human reviews the resulting specification. |
| Human selects `Revise and review again` without guidance | Record the override and publish a bounded replacement round. | The displayed choice has no hidden edit prerequisite. |
| Human selects `Consolidate` | Consolidate through the owning workflow, then complete the exchange. | Only durable human authorization permits continuation. |
