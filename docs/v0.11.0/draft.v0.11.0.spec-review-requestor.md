# Request specification reviews

- Type: feature-request
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md

## Settled split entry

- Order: 2
- Key title: Request specification reviews
- Slug: `spec-review-requestor`
- Status: pending
- Depends on: `review-exchange-core`
- Regroups: the review-requestor behavior triggered after
  `review-ask-questions` or `consolidate-then-review-ask-questions` adds open
  questions to a feature request, issue, design specification, or implementation
  plan; the references from those existing skills to the complementary
  requestor role; and the repeated revise-or-consolidate loop.
- Boundary rationale: specification authorship owns deciding whether reviewer
  feedback requires another review round or permits consolidation, while the
  shared exchange mechanics belong to the core requirement.

## Requestor workflow

When `review-ask-questions` or `consolidate-then-review-ask-questions` adds open
questions to a feature request, issue, design specification, or implementation
plan, the workflow checks for the project-root `a.review-mode` marker. Without
that marker, the existing human-review flow remains unchanged.

When review mode is active, the writer must not stop for the user's review of
the new open questions. Through `pw`, it invokes the complementary specification
review requestor role and performs the following work:

1. Create or reuse `review.type.vX.Y.Z.slug.md` beside the reviewed document.
   When the transcript does not exist, initialize it from the review type and
   version template. Agents append to this versioned transcript but do not read
   it back as working context.
2. Delete a stale project-root `a.review-answer.type.vX.Y.Z.slug.md` when one
   exists.
3. Create or overwrite the project-root
   `a.review-requested.type.vX.Y.Z.slug.md`. Its summary names the umbrella
   draft, or states `Umbrella draft: none`, and names the exact reviewed
   specification and round. Those fields must match the machine-readable
   exchange identity.
4. Include the writer's generated feedback and this conclusion in the request:

   > Let me know if questions are missing in the plan, if you agree with the
   > existing questions, what answer would you chose for said existing
   > questions. No consolidation for now, but if you have a better way to phrase
   > the questions or answers, please suggest it.
   > At the end of your review, write a
   > review-answer.type.vX.Y.Z.slug.md leave instructions for the writer to make
   > the recommended changes, and make a decision:
   >
   > - if there are very few edits (just word polishing), recommend convergence
   >   and consolidation
   > - if there are more than word-polishing edits, request the recommended
   >   changes and another automated review round.
5. Append the same requestor feedback to the versioned transcript.
6. Wait for the matching root answer, then distinguish an intermediate change
   request from a convergence recommendation.

## Repeated review and human confirmation

For an intermediate round, the writer applies the recommended changes to the
reviewed specification, deletes the consumed answer, and creates a replacement
request with an updated identity-bearing summary and the same conclusion. The
automated dialogue continues, and both roles append their feedback to the
versioned transcript.

For a convergence recommendation, the writer retains the answer as decision
evidence and enters `awaiting-human-confirmation`. The reviewer recommendation
is advisory: only the human may select `Consolidate` or
`Revise and review again`.

- `Consolidate` authorizes consolidation and continuation.
- `Revise and review again` records the override and optional human guidance,
  resets the no-progress counters, and starts a replacement automated round.
- The answer is deleted only after the confirmed action is applied.

Ordinary rounds remain automated. The shared no-progress, disagreement,
timeout, abandonment, and inconsistent-artifact rules bound the dialogue and
escalate it when required. `awaiting-human-confirmation` remains distinct from
the `escalated` state.

## Skill and tool scope

- Keep the requestor process, template, and script in its own role or skill.
- Update `review-ask-questions` and
  `consolidate-then-review-ask-questions` with a small reference to that
  complementary requestor role, including the review-mode trigger and transcript
  append duty.
- Add the template and script that generate the specification review-requested
  artifact.
- Reuse the artifact lifecycle, safe file operations, exchange identity,
  termination criteria, and human-intervention rules supplied by
  `review-exchange-core`; do not duplicate or redefine the reviewer role here.
- Add the required LLM-specific wrappers or adapters that locate the canonical
  shared instruction.

## Concrete rules and constraints

- Activate only when the project-root `a.review-mode` file exists.
- Keep transient request and answer artifacts at the project root so the
  existing `a.*` ignore rule applies.
- Keep the versioned review transcript beside the reviewed specification.
- Automatically apply intermediate change requests and repeat the review.
- Treat a consolidation recommendation as advisory.
- Enter `awaiting-human-confirmation` only at convergence.
- Consolidate only after the human explicitly selects `Consolidate`.
