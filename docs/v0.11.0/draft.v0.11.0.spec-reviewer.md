# Respond to specification reviews

- Type: feature-request
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md

## Selected umbrella item

| Order | Type | Key title | Slug | Status | Requirement | Validation plan |
| --- | --- | --- | --- | --- | --- | --- |
| 3 | Feature-request | Respond to specification reviews | `spec-reviewer` | pending | - | - |

## Requirement details from the umbrella

- Type: Feature-request
- Key title: Respond to specification reviews
- Slug: `spec-reviewer`
- Regroups: the new `spec-reviewer` skill, its LLM-specific wrapper or adapter,
  and its request-reading and answer-generation template and script.
- Boundary rationale: the independent reviewer must have a focused role that
  evaluates open-question instructions without inheriting the writer's
  responsibility to edit or consolidate the reviewed specification.
- Concrete rules and constraints: accept the document name returned by `pw`;
  wait for the matching project-root
  `a.review-requested.type.vX.Y.Z.slug.md`; validate its umbrella,
  reviewed-specification, and round identity; provide constructive feedback
  and either request changes or recommend convergence in
  `a.review-answer.type.vX.Y.Z.slug.md`; keep that recommendation advisory;
  append the same feedback to the sibling transcript; and delete the consumed
  request when the answer becomes ready.
- Depends on: `review-exchange-core`, `spec-review-requestor`.

## Reviewer workflow to add

The `spec-reviewer` role receives the exact feature request, issue, design
specification, or implementation plan selected by `pw`. It waits through the
shared exchange for the matching request artifact and validates the request's
machine-readable and human-readable identity before treating it as authority.

The reviewer assesses whether the writer's open questions are complete,
well-phrased, and supplied with sound options, recommendations, and answers.
It returns constructive feedback through the shared exchange. Substantive gaps
produce a change request and another automated round; wording-only findings or
a settled specification may produce a convergence recommendation.

The answer publication writes
`a.review-answer.type.vX.Y.Z.slug.md`, appends the same feedback to the
versioned sibling `review.type.vX.Y.Z.slug.md` transcript, and removes the
consumed request as one shared lifecycle transition. The reviewer does not
edit or consolidate the reviewed specification and does not reread the
append-only transcript as working context.

## Shared convergence and recovery constraints

Intermediate change-request rounds remain automated. A convergence
recommendation is advisory: it moves the requestor to durable
`awaiting-human-confirmation` but cannot authorize consolidation. Only the
human's later `Consolidate` choice authorizes the owning writer workflow;
`Revise and review again` records an override and begins another round.

The reviewer must use the review-exchange core's bounded exact-file wait,
identity checks, lease and reclaim rules, no-progress and disagreement limits,
and escalation path. Timeout, abandonment, inconsistent artifacts, and
unresolved disagreement stop for human intervention rather than creating an
unbounded dialogue.

Every reviewer implementation must preserve the established artifact layout:
transient `a.review-requested.*` and `a.review-answer.*` files stay at the
project root under the existing `a.*` ignore rule, while the append-only
versioned transcript stays beside the reviewed specification. Human-readable
summaries name the umbrella draft or `none`, the exact reviewed specification,
and the review round, matching the exchange envelope.

## Skill, adapter, template, and launcher boundaries

Add one canonical `spec-reviewer` instruction and thin LLM-specific wrappers
that locate it in the same form as the existing shared-skill adapters. Add the
reviewer-specific request-reading and answer-generation template and script,
using shared exchange utilities for artifact identity, publication, transcript
append, waiting, and cleanup rather than duplicating the protocol.

This item does not change the specification writer workflow, implement the
code-review requestor or reviewer roles, or write the final Diataxis
documentation set. Those responsibilities remain with their later umbrella
items.
