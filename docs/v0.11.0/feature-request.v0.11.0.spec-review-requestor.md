# Request specification reviews

## Umbrella revision that introduces specification review requests

The review-mode umbrella separates the review exchange into a shared protocol
and specialized writer and reviewer roles. The completed
`review-exchange-core` requirement supplies the common artifact lifecycle,
identity validation, state transitions, bounded waits, convergence gate, and
human-intervention rules.

This requirement adds the specification-writer side of that exchange. It
connects the existing open-question workflows to the shared requestor
coordination role and owns the repeated revise-or-consolidate loop. The
independent specification reviewer remains a separate requirement.

## User story for specification review requests

As a specification writer working in review mode, I want new open questions to
be sent to an independent reviewer automatically, so reviewer feedback can be
applied through bounded rounds while consolidation remains subject to explicit
human confirmation at convergence.

## Current behavior in v0.11.0

- `review-ask-questions` writes open questions and stops for a human answer.
- `consolidate-then-review-ask-questions` integrates answered questions and
  stops again when it raises follow-up questions.
- Neither workflow delegates its new questions to the shared
  `review-requestor` coordination role when `a.review-mode` exists.
- The shared review exchange can manage specification artifacts and state, but
  no specialized writer workflow currently authors the specification request,
  assesses its answer, or owns the revise-or-consolidate cycle.

## Gap to close for specification review requests

1. Add the specialized specification-requestor behavior that authors request
   and transcript content while delegating every protocol mutation to the
   shared review exchange command.
2. Add small integration references from `review-ask-questions` and
   `consolidate-then-review-ask-questions` so each workflow detects review mode
   after it places new questions.
3. Publish an identity-bearing specification review request instead of stopping
   for a human when review mode is active.
4. Apply intermediate reviewer changes and start replacement review rounds
   automatically.
5. Stop at `awaiting-human-confirmation` when the reviewer recommends
   convergence, and consolidate only after the human selects `Consolidate`.
6. Preserve the existing non-review behavior when the opt-in marker is absent.

## Expected specification requestor workflow

### Activation and delegation

Only after either existing question workflow places at least one new open
question in a feature request, issue, design specification, or implementation
plan does it check the project-root `a.review-mode` marker. A pass that raises
no new question keeps the existing settled-document continuation and creates no
review exchange.

- An explicit `stop here` instruction is checked before any shared exchange
  status or activation operation. It holds the current invocation without
  creating a coordination artifact.
- When the marker is absent, the workflow keeps its existing human-review stop.
- When the marker is present, the writer invokes the complementary
  specification requestor role through `pw` and does not wait for the user to
  answer the questions directly.
- The specialized writer owns its analysis, edits, authored feedback,
  convergence assessment, and any human-authorized consolidation. The shared
  `review-requestor` role owns the coordination sequence and protocol commands.

The specification exchange family is registered with convergence signal
`consolidation-ready`, another-round label `Revise and review again`, and
continue-owning-workflow label `Consolidate`. The requestor passes
those exact values to every shared exchange operation.

### Request and transcript artifacts

For a reviewed document named `type.vX.Y.Z.slug.md`, the requestor derives the
artifact type through the exchange core's registered mapping. Source type
`design` maps to artifact type `design-specification`; `feature-request`,
`issue`, and `plan` retain their source type. The requestor must then:

1. Create or reuse `review.type.vX.Y.Z.slug.md` beside the reviewed document.
   When absent, initialize it from the specification review transcript template.
   Agents append their authored feedback to this versioned transcript and do
   not reread it as working context.
2. Remove a stale project-root `a.review-answer.type.vX.Y.Z.slug.md` through the
   shared exchange lifecycle before publishing a replacement request.
3. Create or overwrite the ignored project-root
   `a.review-requested.type.vX.Y.Z.slug.md` through the shared exchange command.
4. Put the complete machine-readable exchange envelope and authored Markdown in
   the request content file, and put the substantive requestor feedback in the
   transcript-summary file.
5. Include each applicable human-readable identity field exactly once:
   `Umbrella draft`, `Reviewed specification`, and `Review round`. The umbrella
   field names the exact umbrella path or states `none`; all fields agree with
   the exchange envelope and command context.

The published request is valid Markdown: it starts with one H1 title, its first
section is `## JSON` with the fenced exchange envelope, and its identity,
assessment, review instructions, and conclusion are H2 sections. The request
must not jump from the H1 title to H3 authored content.

The authored request ends with the prescribed reviewer direction:

> Let me know if questions are missing in the reviewed specification, if you
> agree with the existing questions, and what answer you would choose for those
> existing questions.
> No consolidation for now, but if you have a better way to phrase the
> questions or answers, please suggest it.
> At the end of your review, publish the project-root
> `a.review-answer.type.vX.Y.Z.slug.md` through the shared review exchange,
> leave instructions for the writer to make the recommended changes, and make
> a decision:
>
> - if there are very few edits (just word polishing), recommend convergence
>   and consolidation
> - if there are more than word-polishing edits, request the recommended
>   changes and another automated review round.

### Intermediate rounds

When the answer requests more than word-polishing changes, the requestor:

1. Reads only the exact answer path returned by the shared exchange command.
2. Applies the recommended changes to the reviewed specification and assesses
   any disagreement.
3. Consumes the answer with the correct reviewed-work-changed and disagreement
   signals.
4. Continues the active exchange when protocol state permits it.
5. Authors a replacement request with the updated round identity and the same
   prescribed conclusion.
6. Publishes the replacement request, appends its substantive feedback to the
   transcript, and waits for the next answer.

These rounds continue without a human stop until convergence or a shared
termination rule produces an escalation.

### Convergence and human authority

A reviewer recommendation for consolidation is advisory. At that point, the
requestor retains the answer as evidence, enters
`awaiting-human-confirmation`, and presents the human with:

- the umbrella identity or `none`;
- the exact reviewed specification and review round;
- the reviewer recommendation;
- the requestor's assessment, including a statement that any wording edits
  covered by the convergence recommendation are already applied; and
- the choices `Consolidate` and `Revise and review again`.

`Consolidate` grants the owning workflow authority to consolidate and continue.
The requestor calls the shared completion operation only after consolidation
succeeds. `Revise and review again` records the override and optional human
guidance, resets the no-progress counters, and starts a replacement automated
round. When an unchanged replacement receives the same convergence result,
the workflow returns to the human convergence gate after applying the shared
round and no-progress bounds; it does not start an unbounded automated loop.
The answer is deleted only after the confirmed action is applied.

The durable state prevents a later session from asking for the same human
decision twice. `awaiting-human-confirmation` remains distinct from the
`escalated` state used for timeout, abandonment, no progress, disagreement, and
inconsistent artifacts.

## Acceptance criteria for specification review requests

1. With no project-root `a.review-mode`, both existing question workflows retain
   their current human-review behavior and create no review exchange artifacts.
2. With `a.review-mode`, either workflow delegates to the specification
   requestor after it places new open questions in a feature request, issue,
   design specification, or implementation plan.
3. The requestor uses the shared review exchange launcher for status,
   activation, publication, waiting, answer consumption, continuation,
   confirmation, escalation, cancellation, resolution, archival, and
   completion; it does not mutate protocol artifacts by hand.
4. The request artifact, answer artifact, and sibling transcript use the
   exchange-core-mapped reviewed type plus the exact version and slug naming
   convention.
5. Every published request contains one matching umbrella identity, reviewed
   specification identity, and positive review-round identity in both its
   human-readable summary and machine-readable envelope.
6. The request contains the writer's feedback and the prescribed reviewer
   direction, and the same substantive feedback is appended to the versioned
   transcript.
7. An intermediate answer is applied and consumed, then a new automated round
   starts with updated identity and no human confirmation stop.
8. A convergence recommendation retains its answer and enters
   `awaiting-human-confirmation`; it does not consolidate by itself.
9. Only the exact `Consolidate` choice authorizes consolidation and continuation.
10. `Revise and review again` records the override and optional guidance,
    resets no-progress counters, and publishes a replacement round.
11. Shared timeout, abandonment, no-progress, disagreement, and
    inconsistent-artifact outcomes stop automation through the established
    escalation and recovery contract.
12. Automated tests cover the specification requestor instruction, its
    specialized request generation surface, `pw` routing, LLM-specific
    wrappers, and both existing question-workflow integrations. Tests reference
    the shared requestor instruction, templates, launcher, and lifecycle as
    core dependencies rather than duplicating their protocol coverage here.
13. Every published request starts with an H1 title, uses `## JSON` as its first
    section, and starts each later top-level authored section at H2.
14. Every shared exchange operation uses family `specification`, convergence
    signal `consolidation-ready`, another-round label
    `Revise and review again`, and continue-owning-workflow label `Consolidate`.

## File-based IO cost clarification for specification review requests

- Normal routing checks only the constant set of exact specification and
  coordination paths for the resolved effort; it does not scan documentation
  trees or load transcript history.
- Request rendering reads each caller-owned feedback or guidance input once and
  produces the paired request and transcript summary without reparsing either
  Markdown output.
- Publication, waiting, continuation, reclaim, and completion remain delegated
  to the shared exchange's exact-path and atomic-write contract.
- The sibling transcript is append-only evidence and is never a working-context
  input for the specification requestor.

## Requirement clarifications

| Question | Decision | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | Start specification review only after at least one new open question is placed; otherwise retain the settled-document continuation. | Expected specification requestor workflow / Activation and delegation; acceptance criterion 2 | Review every pass, including an empty one; ask the human whether a settled document should enter review mode. |
| Q02 | A literal `stop here` instruction holds before any shared exchange operation and creates no coordination artifact. | Expected specification requestor workflow / Activation and delegation | Let review mode override the hold; publish a request but stop waiting. |
| Q03 | Resolve the source filename prefix through the exchange core mapping: `design` becomes `design-specification`, while `feature-request`, `issue`, and `plan` remain unchanged. | Expected specification requestor workflow / Request and transcript artifacts; acceptance criterion 4 | Copy every source prefix exactly; use one generic `specification` token. |
| Q04 | Apply convergence-recommended wording edits before the human gate, retain the answer as evidence, and state in the human summary that the edits are already applied. | Expected specification requestor workflow / Convergence and human authority | Defer all edits until consolidation; force another automated round for wording-only changes. |
| Q05 | Honor `Revise and review again` without requiring guidance or a document edit; bound an unchanged repeated result and return it to the human convergence gate. | Expected specification requestor workflow / Convergence and human authority; acceptance criterion 10 | Require guidance or an edit; return immediately to the gate without publishing the selected replacement round. |

## Boundaries and dependencies

- `review-exchange-core` remains the source of truth for artifact safety,
  identity checks, protocol state, waits, termination, recovery, and durable
  human authorization.
- This requirement owns specification-writer integration and assessment. It
  does not implement the independent `spec-reviewer` role.
- This requirement does not change the implementation-code review workflow.
- Review transcripts remain beside their source documents; transient
  coordination files remain at the project root under the existing `a.*`
  ignore convention.

## Code references for specification review requests

- `instructions/review-ask-questions.md`: writes initial open questions and
  currently stops for human review.
- `instructions/consolidate-then-review-ask-questions.md`: integrates answers,
  may write follow-up questions, and currently stops when questions remain.
- `instructions/review-requestor.md`: defines the shared requestor coordination
  sequence and the boundary between protocol operations and specialized writer
  work.
- `bin/review_exchange.bat`: exposes the shared review exchange operations to
  non-interactive workflows.
- `templates/review-request.template.md`: supplies the common request envelope
  and authored Markdown shape.
- `.agents/llm-shared/instructions/review-ask-questions.md` and
  `.agents/llm-shared/instructions/consolidate-then-review-ask-questions.md`:
  locate the canonical instructions for LLM-specific hosts.
