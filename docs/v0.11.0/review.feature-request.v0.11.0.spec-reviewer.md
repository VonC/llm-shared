# Specification review transcript for v0.11.0

- Exchange: specification/feature-request/v0.11.0/spec-reviewer
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.spec-reviewer.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-08-09T19:37:32+02:00
- Exchange: specification/feature-request/v0.11.0/spec-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.spec-reviewer.md
- Outcome: request

### Review identity for feature-request spec-reviewer round 1

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/feature-request.v0.11.0.spec-reviewer.md
Review round: 1

### Requestor assessment for feature-request spec-reviewer round 1

The new v0.11.0 feature request defines the independent specification reviewer
role, exact identity and pending-request validation, full-document assessment,
paired answer publication, advisory dispositions, recovery, role authority,
and bounded IO. Nine requirement-level questions now cover the remaining
behavioral choices: review depth, concurrent pending requests, marker removal,
document drift, empty-question requests, human guidance, convergence threshold,
cross-document findings, and feedback concreteness.

No additional requirement-level question is currently apparent. Each existing
question has three distinct options with benefits and costs, one recommended
choice, and a filled answer. The reviewer should check whether any scope,
expected behavior, acceptance case, or edge condition remains unspecified and
should challenge the recommended answers where a different choice better fits
the shared review-mode contract.

No reviewer wording suggestion has been applied yet because this is round 1.

### Change summary for feature-request spec-reviewer round 1

Created the focused `spec-reviewer` feature request from umbrella item 3. Added
the user story, current gap, exact reviewer workflow, fourteen acceptance
criteria, bounded-IO expectations, dependencies, code references, and nine
open questions with recommended answers.

### Writer response for feature-request spec-reviewer round 1

Writer response: This is the first review round. There is no earlier reviewer response to accept
or dispute. Please assess the full current feature request, with special
attention to the nine open questions and their recommended answers.

### Reviewer focus for feature-request spec-reviewer round 1

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

## Round 1 by human

- Recorded: 2026-08-09T19:40:14+02:00
- Exchange: specification/feature-request/v0.11.0/spec-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.spec-reviewer.md
- Outcome: escalation

wait timed out while answer was absent

<!-- review-entry-id: escalation-round-1 -->

## Round 2 by human - Timeout resolution

- Recorded: 2026-08-09T20:17:26+02:00
- Exchange: specification/feature-request/v0.11.0/spec-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.spec-reviewer.md
- Outcome: human-resolution

Human resolution: the reviewer is actively preparing the specification review
answer. Clear the answer-wait timeout escalation and start a fresh review round
for the same reviewed specification, umbrella, and question set. The timeout
does not indicate disagreement, abandonment, or invalid review evidence.

<!-- review-entry-id: human-resolution-round-2 -->

## Round 2 by requestor

- Recorded: 2026-08-09T20:20:05+02:00
- Exchange: specification/feature-request/v0.11.0/spec-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.spec-reviewer.md
- Outcome: request

### Review identity for feature-request spec-reviewer round 2

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/feature-request.v0.11.0.spec-reviewer.md
Review round: 2

### Requestor assessment for feature-request spec-reviewer round 2

The new v0.11.0 feature request defines the independent specification reviewer
role, exact identity and pending-request validation, full-document assessment,
paired answer publication, advisory dispositions, recovery, role authority,
and bounded IO. Nine requirement-level questions now cover the remaining
behavioral choices: review depth, concurrent pending requests, marker removal,
document drift, empty-question requests, human guidance, convergence threshold,
cross-document findings, and feedback concreteness.

No additional requirement-level question is currently apparent. Each existing
question has three distinct options with benefits and costs, one recommended
choice, and a filled answer. The reviewer should check whether any scope,
expected behavior, acceptance case, or edge condition remains unspecified and
should challenge the recommended answers where a different choice better fits
the shared review-mode contract.

No reviewer wording suggestion has been applied yet because no answer was
published before the round-1 wait expired. The document and its nine questions
remain unchanged for round 2.

### Change summary for feature-request spec-reviewer round 2

No reviewed-document change was made after round 1. The human resolved the
answer-wait timeout because the reviewer is actively preparing its response;
round 2 republishes the same feature request and nine questions with fresh
exchange identity.

### Writer response for feature-request spec-reviewer round 2

Writer response: No reviewer answer was available before the round-1 bounded wait expired. The
human confirmed that the reviewer is still working and resolved the timeout.
There is no feedback to accept or dispute and no document change between
rounds. Please complete the pending assessment of the full current feature
request, with special attention to the nine open questions and their
recommended answers.

### Reviewer focus for feature-request spec-reviewer round 2

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by human - Answer wait escalation

- Recorded: 2026-08-09T20:24:33+02:00
- Exchange: specification/feature-request/v0.11.0/spec-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.spec-reviewer.md
- Outcome: escalation

wait timed out while answer was absent

<!-- review-entry-id: escalation-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-08-09T20:34:16+02:00
- Exchange: specification/feature-request/v0.11.0/spec-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.spec-reviewer.md
- Outcome: answer

### Reviewer assessment for feature-request spec-reviewer round 2

The requirement is well formed and accurate against the completed
`review-exchange-core` and `spec-review-requestor` contracts: family policy,
the `design` to `design-specification` mapping, the reserved `wait-request` and
`publish-answer` pairing, consumed-request removal, and the advisory-convergence
boundary all match what the core implements. All nine recommended answers are
the ones I would choose, with Q03 keeping its decision but needing its
mechanism corrected.

Three gaps need requirement-level work. Acceptance criterion 2 cannot hold as
written: `prompt_workflow_skill.next_command` renders `spec-review-requestor`
for every non-idle state, and that role maps `request-pending` to waiting for
an answer, so a pending request summons the writer to wait while nothing
summons a reviewer. The requirement never covers a reviewer round that expires
before publication, which this exchange hit twice, at 19:40:14 and again at
20:24:33, both with `wait timed out while answer was absent`, leaving a
finished assessment unpublishable because `reclaim` refuses escalated
exchanges. Q03 claims cancellation survives marker removal; testing shows every
operation returns `disabled` with exit `3` while the marker is absent, `cancel`
included, and routing surfaces nothing, so marker removal is a global pause.
The recovery section also mixes authorities, listing `cancellation`,
`resolution`, and `archival` among rules the reviewer uses when those belong to
the human and only `reclaim` is the reviewer's.

### Requested changes for feature-request spec-reviewer round 2

1. State the routing split in the workflow and in criterion 2: `request-pending`
   routes to `spec-reviewer`, every other non-idle state to
   `spec-review-requestor`, and this requirement changes that shared selection.
2. Add an open question and acceptance criterion for a reviewer round that
   escalates before publication, recommending that the assessment is retained
   and republished in the fresh round after human resolution.
3. Correct Q03's mechanism while keeping option A: while the marker is absent
   every operation returns `disabled` with exit `3` and routing surfaces
   nothing, so the marker must be restored before live work can be finished or
   cancelled.
4. Split recovery authority in the termination section and criterion 12:
   `reclaim` for the reviewer, `cancel`, `resolve`, and `archive` for the human.
5. Recommended: size the requestor's answer wait for a full reviewer turn, or
   state that the reviewer publishes without the requestor blocking on
   `wait-answer`.

Disposition: changes-requested. Apply the changes and start another automated
round; no consolidation on this round.

Recorded for the durable history: this answer was published after the human
instructed that the two answer-wait timeouts reflect a hand-driven process
rather than a protocol signal. The round 2 coordination record was restored
from `escalated` to `active` on that explicit authority, with the request
artifact, the reviewed document, and both escalation entries left untouched.

<!-- review-entry-id: answer-round-2 -->

## Round 3 by requestor

- Recorded: 2026-08-09T20:49:44+02:00
- Exchange: specification/feature-request/v0.11.0/spec-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.spec-reviewer.md
- Outcome: request

### Review identity for feature-request spec-reviewer round 3

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/feature-request.v0.11.0.spec-reviewer.md
Review round: 3

### Requestor assessment for feature-request spec-reviewer round 3

The v0.11.0 feature request now defines the independent specification reviewer
role, role-specific live routing, exact identity and request validation,
full-document assessment, paired answer publication, advisory dispositions,
marker suspension, recovery authority, preserved timed-out assessments, and
policy-sized waits. Ten requirement-level questions cover the remaining
behavioral choices.

All round-2 reviewer findings were accepted. Q03 now describes the marker as a
global gate that suspends new and existing exchange operations until restored.
Q10 covers a completed assessment whose round expires before publication. The
body and acceptance criteria now split reviewer `reclaim` authority from human
`cancel`, `resolve`, and `archive` authority, and define the requestor/reviewer
routing split.

No additional requirement-level question is currently apparent. Each question
has distinct options with benefits and costs, one recommended choice, and a
filled answer. The reviewer should verify the applied changes and identify any
remaining scope, behavior, acceptance, or edge-condition gap.

### Change summary for feature-request spec-reviewer round 3

Applied every required round-2 change and the optional wait clarification.
Added the `request-pending` reviewer route and requestor route for other live
states, corrected marker-removal behavior, split reviewer and human recovery
authority, added retained-assessment recovery and policy-sized wait criteria,
rewrote Q03, and added Q10 for expiration before answer publication.

### Writer response for feature-request spec-reviewer round 3

Writer response: Accepted all round-2 findings with no disagreement. The routing split is now
explicit in the workflow and acceptance criteria. Q03 and the marker behavior
match the verified global gate. Reviewer `reclaim` authority is separated from
human cancellation and stopped-state recovery. Q10 and its matching criterion
preserve and revalidate a completed assessment after timeout recovery. The
requestor wait now uses the full configured review timeout without a shorter
caller override. Please verify these changes and assess all ten questions.

### Reviewer focus for feature-request spec-reviewer round 3

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-3 -->

## Round 3 by reviewer

- Recorded: 2026-08-09T21:00:49+02:00
- Exchange: specification/feature-request/v0.11.0/spec-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.spec-reviewer.md
- Outcome: answer

### Reviewer assessment for feature-request spec-reviewer round 3

Every round-2 change is applied faithfully, and two are better than proposed.

The routing split appears in the workflow and in a rewritten criterion 2:
`request-pending` routes to `spec-reviewer`, every other non-idle state to
`spec-review-requestor`, competing live routes fail closed with all candidates
reported, and the text names `prompt_workflow_skill.next_command` as the shared
selection this requirement changes rather than inherits. The marker is now a
global gate whose removal suspends operations and routing for existing
exchanges with `disabled` and exit `3`, and Q03 is rewritten around that
verified behavior with a fitting new picture and no false cancellation promise.
Recovery authority is split as asked, with reviewer `reclaim` limited to an
intact abandoned request and `cancel`, `resolve`, and `archive` reserved to the
human, mirrored in criterion 12. Q10 and criterion 15 cover an expired round and
add revalidation before republication, which is a correct improvement because
Q04 makes the current document authoritative, so a retained assessment must be
rechecked for drift rather than replayed. The optional wait clarification is
applied in the workflow and as criterion 16.

All ten recommended answers are the ones I would choose. No requirement-level
question is missing and no substantive decision remains open; the requirement is
implementable as written.

### Wording edits covered by this convergence recommendation

1. Spell out the abandoned-request path the routing rule already implies: it
   routes to `spec-review-requestor`, which reclaims and returns the exchange
   to `request-pending`, where routing reaches `spec-reviewer`; the reviewer's
   own `reclaim` covers a lease expiring during its session. Otherwise the rule
   can read as making the reviewer unreachable after a lease expiry.
2. In "Boundaries and dependencies", name both artifacts this requirement
   modifies in the completed `spec-review-requestor` effort: the shared
   live-route selection and the `wait-answer` timeout bound.
3. In criterion 13, add the retained-and-revalidated republication path from
   criterion 15 to the listed test targets.

Disposition: convergence-recommended. Apply the three wording edits before the
human gate, state that they are applied in the convergence summary, and present
the `Consolidate` and `Revise and review again` choices. This recommendation is
advisory and does not authorize consolidation.

<!-- review-entry-id: answer-round-3 -->

## Round 3 by human

- Recorded: 2026-08-10T08:55:24+02:00
- Exchange: specification/feature-request/v0.11.0/spec-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.spec-reviewer.md
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-3 -->
