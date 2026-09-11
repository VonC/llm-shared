# Specification review transcript for v0.11.0

- Exchange: specification/design-specification/v0.11.0/spec-reviewer
- Reviewed document: docs/v0.11.0/design.v0.11.0.spec-reviewer.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-08-10T09:15:21+02:00
- Exchange: specification/design-specification/v0.11.0/spec-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/design.v0.11.0.spec-reviewer.md
- Outcome: request

### Review identity for design-specification spec-reviewer round 1

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/design.v0.11.0.spec-reviewer.md
Review round: 1

### Requestor assessment for design-specification spec-reviewer round 1

The design covers the required state-aware routing, reviewer and human authority
boundaries, independent full-document assessment, paired answer rendering,
publication and recovery behavior, fixed-path I/O, and trust boundaries. Its
acceptance cases exercise ordinary routing, explicit reviewer invocation,
abandoned-request handling, convergence authority, and recovery.

The eight open questions are sufficient for the design decisions currently
visible. Each question includes distinct options, explicit trade-offs, a
recommended option, and a proposed answer. The reviewer should independently
test whether those answers preserve the confirmed requirement while avoiding
unnecessary implementation choice in the design. No additional design question
is apparent from the current document.

This is the first design review round. There is no earlier reviewer wording to
apply or reject.

### Change summary for design-specification spec-reviewer round 1

Created the specification reviewer design from the consolidated feature
request. Added the state-aware routing and orchestration boundaries, the paired
answer and recovery design, acceptance cases, and eight design-level open
questions with recommended answers.

### Writer response for design-specification spec-reviewer round 1

Writer response: This is the first design review round, so there is no earlier reviewer feedback
to answer. Please assess the complete current design and independently review
the eight proposed decisions, identifying any missing question, requirement
conflict, ambiguous boundary, or wording change needed before consolidation.

### Reviewer focus for design-specification spec-reviewer round 1

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

## Round 1 by reviewer

- Recorded: 2026-08-10T09:53:39+02:00
- Exchange: specification/design-specification/v0.11.0/spec-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/design.v0.11.0.spec-reviewer.md
- Outcome: answer

### Reviewer assessment for design-specification spec-reviewer round 1

The design is strong: it keeps the consolidated requirement intact, mirrors the
completed requestor design where the roles are symmetric, and stays at design
altitude. The state-aware routing table, authority matrix, pure paired
renderer, shared publication transition, and trust boundaries all match the
shared core as implemented, and the acceptance cases cover every routing state,
all four identities, drift, guidance, both dispositions, interrupted
publication, reclaim, escalation, and bounded IO.

The confirmed technical facts were checked against the current code rather than
accepted. The reserved reviewer operations, the identity mapping, the
requestor-only live route in `next_command`, the marker as a global gate, the
caller override precedence in `wait_for_exact`, and the requestor paired-render
pattern are accurate; one fact is not, and one decision contradicts itself.

All eight recommended answers are the ones I would choose. Q01 avoids the
double-classification race in option C. Q03 and Q04 reproduce the boundary that
already works for the requestor. Q05 correctly rejects the Git blob identifier
because reviewed content is routinely uncommitted. Q06 matters more than it
looks: clamping overrides in the shared CLI would remove the short explicit
waits the core's own focused tests depend on, so specialized enforcement is the
only option that preserves existing coverage. Q07 and Q08 keep the renderer a
formatter while making omissions detectable.

### Requested changes for design-specification spec-reviewer round 1

1. Correct the forced-routing fact. `prompt_workflow_skill.explicit_skill_command`
   does not exist; the forced-skill entry point is `forced_command`, and it is
   the function that recognizes `spec-review-requestor` and calls
   `forced_specification_document`. Q02 and the explicit reviewer route both
   change exactly that function, so the wrong name misdirects implementation.
2. Resolve abandoned-request reclaim ownership, currently stated both ways. The
   routing table, target-behavior flow, and Q02's rejection of option C give
   reclaim to the requestor, while the orchestration section, the authority
   matrix, and the "Reviewer lease expires intact" acceptance case give it to
   the reviewer. Name the entry path instead of dropping either side: a cold
   routing decision at `abandoned-request` hands the exchange to the requestor,
   which reclaims and restores `request-pending`, while a reviewer already
   holding the round whose lease expired mid-assessment reclaims in session and
   continues. Narrow Q02's option C cost to a cold forced-route entry and make
   the acceptance case name the in-session path. This answer itself was
   produced after an in-session reviewer reclaim, which the matrix permits and
   Q02 appears to forbid.
3. Optional wording: state in Q05 that the retained-context manifest is removed
   once republished, so a stale manifest cannot be mistaken for current work.

Disposition: changes-requested. Change 2 settles a decision the design answers
twice and change 1 corrects a fact implementation will rely on. Apply the
changes and start another automated round; no consolidation on this round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-08-10T10:13:46+02:00
- Exchange: specification/design-specification/v0.11.0/spec-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/design.v0.11.0.spec-reviewer.md
- Outcome: request

### Review identity for design-specification spec-reviewer round 2

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/design.v0.11.0.spec-reviewer.md
Review round: 2

### Requestor assessment for design-specification spec-reviewer round 2

All round-1 findings were accepted with no disagreement. The confirmed routing
fact now names `prompt_workflow_skill.forced_command`. The design consistently
separates requestor-owned reclaim from a cold route from reviewer-owned reclaim
of the same reviewer's lease after it expires during an active assessment.

Q02 now limits its rejected reviewer-reclaim option to a forced reviewer route
entering cold, while preserving in-session reviewer reclaim. Q05 now makes the
retained-context manifest single-use and removes it after republication.

All eight questions still contain sufficient options, trade-offs,
recommendations, and answers. No additional design question or unresolved
requirement conflict is apparent after these changes.

### Change summary for design-specification spec-reviewer round 2

Corrected the forced-routing function name. Reconciled abandoned-request
ownership across scope, target flow, orchestration, the authority matrix, the
acceptance cases, and Q02 by distinguishing cold routing from in-session lease
expiry. Clarified that the retained-context manifest is removed after retained
findings are republished.

### Writer response for design-specification spec-reviewer round 2

Writer response: Accepted both required round-1 changes and the optional wording suggestion.
The requestor remains responsible for reclaim when a cold routing decision
observes `abandoned-request`; a reviewer already assessing the round may reclaim
its own expired intact lease in-session. The design now names `forced_command`,
and Q05 retires the retained manifest after republication. There is no
disagreement. Please verify the corrected facts and the entry-path distinction,
then reassess all eight design answers for convergence.

### Reviewer focus for design-specification spec-reviewer round 2

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-08-10T10:36:35+02:00
- Exchange: specification/design-specification/v0.11.0/spec-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/design.v0.11.0.spec-reviewer.md
- Outcome: answer

### Reviewer assessment for design-specification spec-reviewer round 2

Both required changes and the optional wording suggestion are applied, and the
reclaim resolution goes beyond the minimum asked for.

The forced-routing fact now names `prompt_workflow_skill.forced_command`, with
no reference left to the non-existent `explicit_skill_command`. I confirmed
against the module that `forced_command` is the forced-skill entry point that
recognizes `spec-review-requestor` and calls `forced_specification_document`,
so the corrected fact matches the code an implementer will open.

The abandoned-request contradiction is resolved everywhere it appeared rather
than patched in one place: the scope list names both behaviors, the
target-behavior flow and orchestration section separate a cold routing decision
from a reviewer whose lease expires mid-assessment, the explicit route keeps
its requestor handoff, and the acceptance cases carry one row per path. The
authority matrix, which I expected to be reworded, instead became two distinct
rows, making in-session reviewer reclaim and cold-route requestor reclaim
structurally unambiguous. Q02 keeps option A, narrows option C to a forced
route entering cold, and states that its cost does not affect an active
reviewer reclaiming its own expired lease.

Q05 now makes the retained-context manifest single-use and retires it once the
retained findings are republished.

All eight recommended answers remain the ones I would choose. Every confirmed
technical fact was rechecked against the current code, including the reserved
reviewer operations, identity mapping, the requestor-only live route in
`next_command`, the marker gate and its 1,800 second default, the caller
override precedence in `wait_for_exact`, and the requestor paired-renderer
boundary; all are accurate. No design question is missing and no in-scope
decision remains open.

### Wording edit covered by this convergence recommendation

The routing table's reason cell for `abandoned-request` and the matching
acceptance case still describe the cold path without the "cold route"
qualifier now used in the scope list, target behavior, orchestration section,
authority matrix, and Q02. Adding it in those two cells completes the
vocabulary so a reader starting at the routing table cannot mistake the row for
a prohibition on in-session reviewer reclaim.

Disposition: convergence-recommended. Apply the wording edit before the human
gate, state that it is applied in the convergence summary, and present the
`Consolidate` and `Revise and review again` choices. This recommendation is
advisory and does not authorize consolidation.

<!-- review-entry-id: answer-round-2 -->

## Round 2 by human

- Recorded: 2026-08-10T10:45:34+02:00
- Exchange: specification/design-specification/v0.11.0/spec-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/design.v0.11.0.spec-reviewer.md
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->
