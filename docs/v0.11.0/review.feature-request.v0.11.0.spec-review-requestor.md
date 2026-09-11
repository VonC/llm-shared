# Specification review transcript for v0.11.0

- Exchange: specification/feature-request/v0.11.0/spec-review-requestor
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.spec-review-requestor.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-08-06T13:34:53+02:00
- Exchange: specification/feature-request/v0.11.0/spec-review-requestor
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.spec-review-requestor.md
- Outcome: request

### Review scope for specification requestor round 1

Review the feature request and its five open questions as requirement content.
Check the requested behavior, boundaries, acceptance criteria, failure cases,
and consistency with the completed review-exchange-core requirement and design.
Do not introduce implementation-plan choices in this review.

Assess whether questions are missing, whether each existing option set covers
the meaningful requirement-level alternatives, whether the recommended answers
are consistent with the v0.11.0 core contract, and whether any wording should be
changed before consolidation.

### Requestor assessment for specification requestor round 1

The feature request covers activation from both open-question workflows,
identity-bearing request publication, transcript aggregation, automated
intermediate rounds, convergence-only human confirmation, and preservation of
the non-review path. Five open questions currently recommend:

1. starting a specification exchange only when new open questions exist;
2. letting an explicit `stop here` instruction suppress publication for that
   invocation;
3. deriving the artifact type token from the reviewed filename prefix;
4. applying wording-only convergence edits before human confirmation; and
5. starting a replacement round whenever the human selects
   `Revise and review again`, even without guidance or a document edit.

The reread found three points that need particular reviewer attention:

- Q03 recommends the source filename prefix, but the completed core contract
  requires the `design-specification` protocol token and maps it to a
  `design.vX.Y.Z.slug.md` source while retaining `design-specification` in all
  review artifact names.
- The feature request asks for a requestor instruction, request template, and
  generation script in acceptance criterion 12. The core already owns the
  canonical coordination instruction, shared envelope template, launcher, and
  common lifecycle. Confirm which specialized specification-requestor surfaces
  remain in scope without duplicating those core-owned pieces.
- The specialized family must register `consolidation-ready`,
  `Revise and review again`, and `Consolidate`. The human labels appear in the
  requirement, but the convergence signal is not yet an explicit confirmed
  rule or acceptance criterion.

Please also check whether the wording-only convergence behavior in Q04 preserves
the rule that the reviewer recommendation is advisory, and whether Q05 remains
bounded when a human repeatedly requests another round on unchanged work.

<!-- review-entry-id: request-round-1 -->

## Round 1 by reviewer

- Recorded: 2026-08-06T14:53:21+02:00
- Exchange: specification/feature-request/v0.11.0/spec-review-requestor
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.spec-review-requestor.md
- Outcome: answer

### Reviewer assessment for specification reviewer round 1

No open question is missing. The two consistency gaps flagged by the requestor
are confirmed, and both are fully decided by the completed review-exchange-core
contract, so they need direct requirement edits rather than new open questions.

Question-by-question: Q01, Q02, Q04, and Q05 keep their recommended answers.
Q02 acts before any exchange operation, so an explicit hold leaves no protocol
state to repair. Q04 preserves the advisory rule because wording-only edits are
writer-owned document actions while the exchange still enters
`awaiting-human-confirmation` with the answer retained and no consolidation
before the human selects `Consolidate`. Q05 remains bounded because every
replacement round on unchanged work returns to the convergence gate, so each
repetition costs the human an explicit choice.

Q03 loses its recommended answer. The core contract fixes the specification
type tokens as `feature-request`, `issue`, `design-specification`, and `plan`,
with one filename bridge mapping `design-specification` to the
`design.vX.Y.Z.slug.md` source prefix while review artifacts retain the full
token. Option Q03-A would print a bare `design` token the core rejects, and
option Q03-B invents an unregistered `implementation-plan` token. The correct
answer derives the token from the reviewed filename prefix through the core's
registered mapping.

### Requested changes for specification reviewer round 1

1. Rework Q03 so the accepted answer is the core-registered token mapping,
   deterministic from the reviewed filename prefix with `design` mapping to
   `design-specification`, and update the option set, recommendation, and
   answer accordingly.
2. Add a confirmed rule and acceptance criterion registering the specification
   family policy at exchange start: convergence signal `consolidation-ready`
   with display labels `Revise and review again` (another-round) and
   `Consolidate` (continue-owning-workflow).
3. Rescope acceptance criterion 12 to the specialized surfaces this requirement
   owns — the specialized requestor instruction layered on the shared
   coordination instruction, specialized request-content authoring on the
   shared template, `pw` routing, LLM wrappers, and the two question-workflow
   references — with the core-owned instruction, template, launcher, and
   lifecycle referenced, not duplicated.
4. Fix the prescribed reviewer direction: name the exact project-root artifact
   `a.review-answer.type.vX.Y.Z.slug.md` published through the shared exchange
   command, and replace "missing in the plan" with "missing in the reviewed
   specification".
5. Optional wording-only polish for Q02, Q04, and Q05 boundedness and
   already-applied-edit statements.

Disposition: changes-requested. Apply the requested changes and start another
automated review round; no consolidation on this round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-08-06T15:18:16+02:00
- Exchange: specification/feature-request/v0.11.0/spec-review-requestor
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.spec-review-requestor.md
- Outcome: request

### Review scope for spec-review-requestor round 2

Review the amended feature request and all five open questions. Check that the
round 1 changes resolve the exchange-core identity, family-policy, ownership,
reviewer-direction, and convergence details without adding behavior owned by a
later umbrella topic.

### Requestor update for spec-review-requestor round 2

- Q03 now derives the artifact type from the reviewed filename through the
  exchange core's registered mapping: `design` maps to
  `design-specification`; `feature-request`, `issue`, and `plan` retain their
  tokens. The former unregistered `implementation-plan` alternative is gone.
- The requirement registers family `specification`, convergence signal
  `consolidation-ready`, another-round label `Revise and review again`, and
  continue-owning-workflow label `Consolidate`, with a matching acceptance
  criterion.
- Test scope now covers only the specialized requestor surfaces and
  integrations while treating the shared instruction, templates, launcher,
  and lifecycle as exchange-core dependencies.
- The prescribed conclusion refers to the reviewed specification and directs
  publication of the exact project-root answer through the shared exchange.
- Q02 states that an explicit hold is checked before any exchange operation and
  creates no coordination artifact. Q04 states that the convergence summary
  identifies wording edits already applied. Q05 returns an unchanged repeated
  result to the bounded human convergence gate instead of an automated loop.

### Reviewer instructions for spec-review-requestor round 2

Report any missing open question, disagreement with an option or answer, or
remaining substantive correction. If the amended specification needs more
than word polishing, give exact change instructions and request another
automated round. If only word polishing remains, identify the wording edits
and recommend convergence.

<!-- review-entry-id: request-round-2 -->

## Round 2 by human

- Recorded: 2026-08-06T17:11:04+02:00
- Exchange: specification/feature-request/v0.11.0/spec-review-requestor
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.spec-review-requestor.md
- Outcome: escalation

The round 2 request published at 2026-08-06T15:18:16+02:00 became abandoned
before its answer could be published: the reviewer finished verifying the
amended specification after the coordination lease, last renewed at
2026-08-06T15:21:07+02:00, had expired, so answer publication was refused with
`answer publication requires a request pending`.

The round 2 request evidence is intact at the project root and its substantive
content is already recorded in this transcript under `Round 2 by requestor`.
No artifacts conflict; this is a lease expiry between sessions, not an
inconsistent state.

The completed reviewer verification found every round 1 requested change
applied faithfully and only word polishing remaining. That assessment will be
resubmitted as the reviewer answer of the replacement round after human
recovery starts it.

<!-- review-entry-id: escalation-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-08-06T17:46:01+02:00
- Exchange: specification/feature-request/v0.11.0/spec-review-requestor
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.spec-review-requestor.md
- Outcome: answer

### Reviewer assessment for specification reviewer round 2

Every round 1 requested change is applied faithfully, and each resolution
stays inside requirement content: Q03 now resolves the reviewed filename
prefix through the exchange core's registered mapping with `design` becoming
`design-specification` and keeps the exact-prefix copy only as a rejected
option; the family registration is a confirmed rule with convergence signal
`consolidation-ready` and the two display labels, enforced by new acceptance
criterion 14; acceptance criterion 12 covers only the specialized requestor
surfaces and references the shared instruction, templates, launcher, and
lifecycle as exchange-core dependencies; the prescribed reviewer direction
names the reviewed specification and the exact project-root answer artifact
published through the shared exchange; and the Q02 pre-operation hold, Q04
already-applied statement, and Q05 bounded return to the convergence gate are
all stated.

No open question is missing. All five recommended answers — Q01-A, Q02-A, the
reworked Q03-A, Q04-A, and Q05-A — are correct and consistent with the
completed review-exchange-core contract.

### Remaining wording edits for specification reviewer round 2

Only word polishing remains, covered by this convergence recommendation:

1. In the prescribed reviewer direction, insert the missing "and": "if you
   agree with the existing questions, and what answer you would choose".
2. In the family registration rule, align "another-round action label" and
   "continue-owning-workflow action label" with the acceptance criterion 14
   vocabulary "another-round label" and "continue-owning-workflow label".

The abandonment escalation recorded earlier in this transcript was superseded
by an explicit human instruction to complete round 2 with its answer; the
coordination lease was restored on that authority and this answer completes
the round.

Disposition: convergence-recommended. Apply the two wording edits before the
human gate per the Q04-A rule, state that they are applied in the convergence
summary, and present the `Consolidate` and `Revise and review again` choices.
This recommendation is advisory and does not authorize consolidation.

<!-- review-entry-id: answer-round-2 -->

## Round 2 by human2

- Recorded: 2026-08-06T19:13:54+02:00
- Exchange: specification/feature-request/v0.11.0/spec-review-requestor
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.spec-review-requestor.md
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->
