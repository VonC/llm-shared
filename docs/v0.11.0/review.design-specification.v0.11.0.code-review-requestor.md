# Specification review transcript for v0.11.0

- Exchange: specification/design-specification/v0.11.0/code-review-requestor
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/design.v0.11.0.code-review-requestor.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-08-12T16:55:07+02:00
- Exchange: specification/design-specification/v0.11.0/code-review-requestor
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/design.v0.11.0.code-review-requestor.md
- Outcome: request

### Review identity for design-specification code-review-requestor round 1

Umbrella draft: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: C:/Users/vonc/git/llm-shared/docs/v0.11.0/design.v0.11.0.code-review-requestor.md
Review round: 1

### Requestor assessment for design-specification code-review-requestor round 1

The design preserves the six settled requirement clarifications and defines the activation boundary, role ownership, exact code-review identity, specialized request content, staged repair assessment, automated-round classification, and durable human commit gate. Four design questions remain: how `implement-step` hands exact context to the specialized requestor, the paired renderer interface, the durable-authorization continuation into existing commit mechanics, and the evidence contract for accepting bounded reviewer repairs. Each has design-level alternatives and a recommended answer. Please check whether any architectural interface or state-flow question is missing and whether the recommendations align with the existing shared exchange and workflow-router patterns without reopening feature scope.

### Change summary for design-specification code-review-requestor round 1

Initial design-review round. Created the implementation code-review requestor design from the consolidated feature request and added Q01 through Q04 covering delegation, rendering, authorized commit continuation, and repair-scope assessment. No prior design-review feedback has been applied.

### Writer response for design-specification code-review-requestor round 1

Writer response: This is the first automated design-review round. The writer currently recommends options A1, B1, C1, and D1 and requests review of their compatibility with the existing requestor, router, renderer, and commit-gate boundaries.

### Reviewer focus for design-specification code-review-requestor round 1

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

## Round 1 by reviewer

- Recorded: 2026-08-12T17:03:19+02:00
- Exchange: specification/design-specification/v0.11.0/code-review-requestor
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/design.v0.11.0.code-review-requestor.md
- Outcome: answer

### Reviewer assessment for design-specification code-review-requestor round 1

The design carries the settled feature correctly and reads as a design rather
than a restated requirement. The decision table preserves all six requirement
clarifications, including the four-category substantive class for Q02 that the
specification round corrected, so the enumeration that was inconsistent in the
feature request is consistent here. The activation boundary, role ownership,
exact identity, request body, staged review subject, and human commit gate are
each stated once and referenced from the acceptance table.

Three factual claims were checked against the repository rather than accepted.
The code-review family policy in the activation section is right: `commit-ready`
with `Rework and review again` and `Commit` is the form used throughout the
exchange lifecycle, acceptance, and model suites, and `FamilyPolicy` validates
only token shape, so the registered value is a convention this design correctly
adopts. `pw skill <name>` exists as a real subparser, so Q01's mechanism is not
hypothetical. Q02's option B1 mirrors the existing specification request
renderer flag-for-flag, and Q03's option C1 matches the shared requestor rule
that a later session seeing a pending authorization must finish it without
asking the human twice.

Two design-level gaps remain, and both are interface or state-flow decisions
rather than implementation detail.

The first is that Q01's chosen mechanism cannot carry an implementation step.
`render_command` produces exactly one host prefix, one instruction name, the
the space-delimited `on` token and one document path. There is no step slot. Code review needs
the plan and the step: the exchange core requires an implementation-step
identifier, and this design states that the envelope and authored summary both
carry plan, step, round, and umbrella. Q01 settles which router surface hands
off, but not how the step survives that handoff, and the three obvious
resolutions produce visibly different contracts.

The second is that a substantive repair the reviewer converges on cannot reach
another automated round the way the design describes. The round-classification
section says such an answer cannot converge in that round and that another
automated round reviews the substantive change after requestor assessment. The
shared core does not permit the requestor to do that. A convergence answer puts
the exchange in `convergence-gate`, and `consume_answer` short-circuits on that
state and restores the gate rather than consuming the answer as intermediate.
The only exits are the human's `Commit` and `Rework and review again`. Since the
reviewer is a separate deferred effort that may not honor the Q02 rule, the
design must say what the requestor does with a non-compliant convergence
instead of describing an automated round it cannot start.

Neither gap questions a settled decision. Q01 through Q04 are the right
questions with the right answers, and the recommended options are the ones this
reviewer would choose. What is missing is one interface decision under Q01 and
one state-flow decision under the round-classification rule.

### Question verdicts for design-specification code-review-requestor round 1

Q01 -- How does the implementation workflow enter the specialized requestor?

Verdict: right question, right answer, incomplete interface. The reviewer would
also choose A1. It matches the specification-review delegation pattern, keeps
live-exchange precedence in one router, and yields an inspectable handoff, and
`pw skill <skill_name>` exists as a real subparser so the mechanism is
implementable today. A2's con is accurate about pushing invocation context into
`implement-step`, and A3's con correctly names the boundary it blurs. The gap is
that A1 does not say how the implementation step reaches the requestor, and the
current rendered command has no room for it. This is a design decision because
the three resolutions differ in contract, not in code style, and is proposed
below as Q05.

Q02 -- What paired renderer interface composes a code-review request?

Verdict: settled. The reviewer would choose B1. It mirrors the existing
specification request renderer, which takes exact identity flags plus separate
ignored files for assessment, change summary, writer response, and optional
guidance and writes paired outputs in one run, so B1 is a proven shape rather
than a new one. B2's con is right that mixing machine identity with long-form
Markdown makes caller preparation fragile, and B3's con is right that deriving
the summary by parsing the request couples transcript behavior to headings and
breaks the paired-output boundary the shared design already relies on. The
stated con for B1, several small scratch files, is the correct cost to accept.
Nothing to change.

Q03 -- Who owns the transition from durable commit authorization to the
existing commit gate?

Verdict: settled. The reviewer would choose C1. It is the only option that
satisfies the shared requestor rule that a session observing a pending
authorization finishes the authorized action rather than asking again, which is
exactly what C2 would violate by re-presenting the same choice. C3's con is
right that executing Git directly moves commit mechanics into the review role
and bypasses the owning workflow. The stated con for C1, one added router
transition, is the correct cost. Nothing to change.

Q04 -- How is reviewer repair scope checked before the requestor accepts it?

Verdict: settled. The reviewer would choose D1. Its four evidence sources map
onto four distinct failure modes: the plan step bounds scope, the repaired-path
inventory from the feature's Q05 answer bounds surface, the staged diff bounds
content, and the check result bounds completeness. D2's con is the decisive one
and is stated precisely: a completeness check can pass while unrelated staged
work is also present, so it cannot evidence scope. D3's con correctly identifies
that judgment without a fixed evidence set is not consistently validatable.
Nothing to change.

Q05 -- How does the exact implementation step reach the specialized requestor?
(missing, must be added)

Q01 settles that `implement-step` asks `pw` for the specialized command and runs
it verbatim, but `render_command` emits one host prefix, one instruction name,
the space-delimited `on` token and one document path, with no step component. Code review
needs both the plan and the step, since the exchange core requires an
implementation-step identifier and this design states that both the envelope and
the authored summary carry plan, step, round, and umbrella.

Options should be: extend the rendered command with an explicit step token so
the printed handoff is self-contained; keep the command document-only and have
the requestor re-derive the current step from the durable workflow record that
the handoff already updates; or have the router write exact plan and step
context to a known location that the requestor reads. The reviewer recommends
the first, because Q01's own stated pro is an inspectable, resumable handoff
carrying exact context, and a command that omits the step satisfies neither
inspectability nor resumability. It also keeps step resolution in the router,
which Q01 already made the single routing authority.

Q06 -- What does the requestor do when a convergence recommendation follows a
substantive repair? (missing, must be added)

The round-classification rule says a reviewer answer changing code, tests,
acceptance behavior, or commit grouping cannot converge in that round, and that
another automated round follows requestor assessment. The requestor cannot
produce that outcome on its own. A convergence answer moves the exchange to
`convergence-gate`; `consume_answer` short-circuits on that state and restores
the gate instead of consuming the answer, so no automated round can start. Only
the human choices `Commit` and `Rework and review again` leave that state. The
reviewer belongs to a deferred effort, so the design cannot assume every answer
honors the rule.

Options should be: present the gate to the human with the writer assessment
recommending `Rework and review again` and the substantive evidence that
triggered it; escalate the round as an artifact or protocol inconsistency; or
record it as an explicit disagreement. The reviewer recommends the first,
because the state is a legitimate convergence gate rather than a corrupted
exchange, the human already owns that decision point, and the existing override
path already records the choice and resets the counters. Escalation would turn a
recoverable disagreement into a stopped exchange, and the disagreement path is
defined for intermediate answers the requestor can actually consume.

### Requested changes for design-specification code-review-requestor round 1

Requested changes: Change 1 -- add Q05 on how the implementation step reaches the requestor.

Title it "How does the exact implementation step reach the specialized
requestor?". Its description must state that Q01 settles the router surface but
not the step, that the current rendered command carries one host prefix, one
instruction name, and one document path with no step component, and that code
review needs plan and step together because the exchange core requires an
implementation-step identifier and this design has both the envelope and the
authored summary carry plan, step, round, and umbrella.

Offer three options: extend the rendered command with an explicit step token so
the printed handoff is self-contained; keep the command document-only and have
the requestor re-derive the current step from the durable workflow record the
handoff already updates; or have the router write exact plan and step context to
a known location the requestor reads. Recommend and answer the first, on the
ground that Q01's own pro promises an inspectable, resumable handoff carrying
exact context, and a command omitting the step delivers neither.

Change 2 -- add Q06 on a convergence recommendation after a substantive repair.

Title it "What does the requestor do when a convergence recommendation follows a
substantive repair?". Its description must state that the reviewer is a deferred
effort that may not honor the round-classification rule, that a convergence
answer moves the exchange to `convergence-gate`, that answer consumption
short-circuits on that state and restores the gate rather than consuming the
answer, and that only the human choices leave it.

Offer three options: present the gate to the human with a writer assessment
recommending `Rework and review again` and the substantive evidence; escalate
the round as a protocol inconsistency; or record it as an explicit disagreement.
Recommend and answer the first, on the ground that the state is a legitimate
convergence gate rather than a corrupted exchange, the human already owns that
decision, and the override path already records the choice and resets counters.

Change 3 -- correct the round-classification prose so it does not promise an
automated round the requestor cannot start.

In "Round classification after repairs", replace the second sentence of the
first paragraph. Replace:

After the requestor assesses the result, another automated round reviews the
substantive change.

with:

When the answer requests changes, the requestor assesses the result and
publishes another automated round for the substantive change. When the answer
instead recommends commit readiness, the exchange has already reached its
human gate, so the requestor presents the substantive evidence with a
recommendation to choose `Rework and review again` rather than starting a round
it cannot start.

Change 4 -- align the matching acceptance case with change 3.

In the acceptance table, the row "Reviewer changes code, tests, acceptance
behavior, or grouping" currently expects "Publish another automated round after
requestor assessment". Split or qualify it so the expected outcome distinguishes
a change request, which the requestor consumes and continues, from a commit-ready
recommendation, which reaches the human gate with a recommended override. Keep
the existing reason, which remains correct for both.

Change 5 -- record both new decisions in the design decisions table.

Add one row for each new question, in the same form as the existing six, naming
the decision, the section it is integrated in, and the rejected alternatives.
Q05 integrates in "Activation and role boundaries / Commit-gate activation
boundary" and in "Request identity and content / Exact plan and step identity".
Q06 integrates in "Repair assessment and repeated rounds / Round classification
after repairs" and in "Convergence and human-owned commit authority".

Leave Q01 through Q04, the family policy block, the confirmed technical facts,
the scope sections, and every other acceptance row unchanged.

### Writer instructions for design-specification code-review-requestor round 1

Apply the changes below to
`docs/v0.11.0/design.v0.11.0.code-review-requestor.md` only. Do not change the
feature request, whose six decisions this design already carries correctly, and
do not change the umbrella draft.

Keep Q01 through Q04 exactly as they are, including their options, pros, cons,
recommendations, and answers. Add the two new questions after Q04 as Q05 and
Q06, using the same description, BBQ, options, recommendation, and answer
structure the existing four use. Add their rows to the design decisions table in
the existing form.

Changes 3 and 4 are corrections to prose that currently describes an automated
round the requestor cannot start. Apply them together so the narrative section
and the acceptance table agree.

After editing, re-read the round-classification section beside the acceptance
table and confirm both now distinguish a change request from a commit-ready
recommendation. Then publish the next round; the reviewer will check the two new
questions and the two corrected passages rather than reopening Q01 through Q04.

### Final reviewer decision for design-specification code-review-requestor round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-08-12T17:22:32+02:00
- Exchange: specification/design-specification/v0.11.0/code-review-requestor
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/design.v0.11.0.code-review-requestor.md
- Outcome: request

### Review identity for design-specification code-review-requestor round 2

Umbrella draft: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: C:/Users/vonc/git/llm-shared/docs/v0.11.0/design.v0.11.0.code-review-requestor.md
Review round: 2

### Requestor assessment for design-specification code-review-requestor round 2

Round 1 feedback was accepted in full. Q01 through Q04 remain unchanged. Q05 now makes the `pw` handoff self-contained by carrying an explicit implementation-step token with the exact plan. Q06 now defines the only valid recovery when a commit-ready recommendation follows substantive reviewer repairs: preserve the legitimate convergence gate, present the substantive evidence, and recommend the human choose `Rework and review again`. The activation and identity sections integrate Q05; the round-classification, convergence, acceptance-case, and decision-table sections integrate Q06. Please verify the two new questions and confirm that the narrative and acceptance rows now distinguish an intermediate changes-requested answer from a convergence recommendation without promising an unavailable requestor transition.

### Change summary for design-specification code-review-requestor round 2

Applied all five round 1 requested changes. Added Q05 with explicit step-token command options and E1; added Q06 with convergence-gate recovery options and F1; corrected round-classification prose to split changes-requested from commit-ready answers; split the substantive-repair acceptance row along the same boundary; added both design decisions to the table. Q01 through Q04 and all protected sections remain unchanged.

### Writer response for design-specification code-review-requestor round 2

Writer response: The writer accepts the round 1 review with no disagreement. The design now uses a self-contained plan-and-step handoff and no longer claims the requestor can consume a convergence answer or start an automated round from `convergence-gate`. For a non-compliant commit-ready recommendation after substantive repairs, it uses the existing human override path and recommends `Rework and review again`.

### Reviewer focus for design-specification code-review-requestor round 2

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-08-12T17:36:44+02:00
- Exchange: specification/design-specification/v0.11.0/code-review-requestor
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/design.v0.11.0.code-review-requestor.md
- Outcome: answer

### Reviewer assessment for design-specification code-review-requestor round 2

All five round 1 changes were applied, and two of them were applied better than
requested. Q05 and Q06 are well built: their descriptions state the mechanical
constraints rather than asserting a conclusion, their options are materially
distinct, and their rejected options carry the reasons that actually decide
them. Q06's F3 con is the sharpest line in the document, because it identifies
that the disagreement transition belongs to intermediate answers the requestor
can consume and therefore cannot move a convergence gate at all. The
round-classification correction also improved on the wording supplied: "cannot
validly finish the workflow in that round" is more accurate than the phrasing
requested, since such an answer can reach the gate and simply cannot conclude
there.

Q01 through Q04 are unchanged, as requested, and remain correct. The two new
integrations landed in the right sections: the activation boundary and the
exact plan-and-step identity section both now describe a self-contained command
carrying plan and step, and the convergence section states that the gate stays
legitimate, that the writer assessment recommends the override, and that the
requestor neither consumes the convergence answer nor escalates a recoverable
disagreement.

Two defects remain, and both are consequences of round 1 instructions that were
incomplete rather than of anything the writer did wrong.

The first is a decision-table identifier collision that change 5 introduced. The
table's six existing rows are the consolidated feature request's decisions and
use that document's identifiers, which run Q01 through Q06. The design's own
open questions use a separate sequence that now also runs Q01 through Q06.
Adding design rows for Q05 and Q06 into the requirement-numbered table produced
two rows labelled Q05 and two labelled Q06, with different meanings. The round 1
instruction asked for those rows without noticing that the table was already
holding requirement identifiers, so the collision is the instruction's fault.
It is still a real traceability defect: "Q05" in this document now resolves to
either the staged-repair rule or the step-token handoff, and consolidation will
multiply the problem when it folds the design's own six answers into the same
table.

The second is that the target-behavior diagram was not corrected alongside the
prose and the acceptance table. It still routes "substantive repair or requested
rework" to another automated round, which is exactly the claim changes 3 and 4
removed from the other two places. Round 1 named the round-classification
section and the acceptance row but not the diagram, so this passage kept the
superseded routing while the rest of the document moved.

Neither defect touches a settled decision. Q01 through Q06 are the right
questions with the right answers, and this reviewer would choose A1, B1, C1, D1,
E1, and F1.

### Question verdicts for design-specification code-review-requestor round 2

Q01 through Q04 -- delegation, renderer interface, commit continuation, and
repair-scope evidence.

Verdict: settled and unchanged, as requested. Not reopened; the round 2 edits
introduced no contradiction with any of them. The reviewer's answers remain A1,
B1, C1, and D1 for the reasons recorded in round 1: `pw skill` is a real router
surface, B1 mirrors the existing specification request renderer flag for flag,
C1 is the only option compatible with the shared rule against asking the human
twice, and D1's four evidence sources map onto four distinct failure modes that
no single signal covers.

Q05 -- How does the exact implementation step reach the specialized requestor?

Verdict: settled. The reviewer's answer is E1. The description states the
constraint correctly, that the rendered command carries a host prefix, an
instruction name, and one document path with no step component, while code
review needs both because the exchange core requires an implementation-step
identifier. The options are materially distinct in contract rather than in
style: E1 changes the command, E2 changes where the step is resolved, and E3
adds an artifact. E1's own con is honest about extending an existing
document-only contract, and that cost is the right one to accept, because Q01
selected the router precisely for an inspectable and resumable handoff and a
command missing the step provides neither. E2's con correctly identifies that
the visible command becomes incomplete, and E3's con correctly identifies that a
side-channel artifact acquires its own identity, lifecycle, and recovery
obligations. Nothing to change.

Q06 -- What does the requestor do when a convergence recommendation follows a
substantive repair?

Verdict: settled, and the best-argued question in the document. The reviewer's
answer is F1. The description is accurate on every mechanical point: the
reviewer is a deferred effort that may not honor the rule, a convergence answer
moves the exchange to `convergence-gate`, answer consumption short-circuits on
that state and restores the gate, and only the two human choices leave it. F1's
con is honest that a reviewer policy violation now costs a human action that an
intermediate answer would have absorbed automatically. F2's con correctly
distinguishes a recoverable recommendation disagreement from a genuinely
inconsistent exchange, which matters because escalation is the harder state to
leave. F3's con is exact and is the reason F3 is not merely worse but
unavailable. Nothing to change.

Missing questions: none. The design now settles delegation, the renderer
boundary, authorized commit continuation, repair-scope evidence, step transport,
and non-compliant convergence. What remains is not a decision but the
consistency of two passages with decisions already made.

Identifier namespaces -- structural, not a question.

The design carries two independent `Q0x` sequences: the decision table holds the
consolidated feature request's six identifiers, and the open-questions section
holds the design's own six. They now overlap completely. This needs resolving
before consolidation folds the design answers into the same table, because at
that point the document would contain up to four rows sharing two identifiers.

### Requested changes for design-specification code-review-requestor round 2

Requested changes: Change 1 -- separate the two `Q0x` identifier namespaces in the decision table.

This reverses part of round 1's change 5, which asked for the two new rows
without noticing the table already used requirement identifiers. Apply all three
parts together.

First, retitle the table so its source is explicit. Replace the heading
`## Design decisions for v0.11.0 implementation code review requests` with
`## Requirement decisions carried into the v0.11.0 code review requestor design`,
and add one sentence directly beneath it:

The identifiers below are the consolidated feature request's decision
identifiers. This design's own open questions use their own sequence and are
recorded separately once they are consolidated.

Second, prefix the six existing row identifiers so they cannot collide with the
design's sequence: change `Q01` through `Q06` in the first column to `FR-Q01`
through `FR-Q06`. Leave every decision, integration reference, and rejected
alternative in those six rows unchanged.

Third, remove the two rows added in round 2, the one beginning "Extend the
rendered requestor handoff" and the one beginning "When a commit-ready
recommendation follows a substantive repair". The design's own decisions are
not consolidated yet, which is why its Q01 through Q04 are absent from the
table too; recording only two of six is the inconsistency to remove. The
consolidation step will add all six design decisions under their own
identifiers.

If you prefer to keep both sets in one table, the acceptable alternative is to
add a `Source` column whose value is `feature request` or `design` on every
row, and to add the four missing design rows so the table is complete rather
than partial. Do not leave the table with duplicate bare identifiers.

Change 2 -- correct the target-behavior diagram to match the settled routing.

The diagram in "Target behavior for v0.11.0 implementation review" still carries
the routing that changes 3 and 4 removed from the prose and the acceptance
table. Round 1 named those two places but not the diagram.

Replace these two lines:

```txt
                 -> substantive repair or requested rework: another automated round
                 -> polishing-only repair plus commit-ready recommendation: human gate
```

with:

```txt
                 -> changes requested: consume and publish another automated round
                 -> substantive repair plus commit-ready recommendation: human gate, override recommended
                 -> polishing-only repair plus commit-ready recommendation: human gate
```

Leave every other line of the diagram unchanged, including the marker sample,
the absent-marker branch, the publication line, and the two human-choice lines.

After both changes, search the document for any remaining sentence that sends a
substantive repair to another automated round without distinguishing a
changes-requested answer from a commit-ready recommendation. The prose in
"Round classification after repairs", the convergence section, and the two
acceptance rows are already correct; the diagram was the last place carrying the
superseded form.

### Writer instructions for design-specification code-review-requestor round 2

Apply the changes below to
`docs/v0.11.0/design.v0.11.0.code-review-requestor.md` only. Do not change the
feature request or the umbrella draft.

Keep Q01 through Q06 in the open-questions section exactly as they are,
including every description, BBQ, option, pro, con, recommendation, and answer.
Both changes are to material outside that section: one to the decision table and
its heading, one to the target-behavior diagram.

Change 1 partly reverses round 1's change 5. That instruction was wrong, not the
edit made in response to it: it asked for two new rows without noticing the
table already held the consolidated feature request's identifiers. Remove those
two rows and make the remaining namespace explicit so consolidation has a clean
table to extend.

After editing, confirm two things. The decision table must contain no duplicate
identifier, and no passage anywhere in the document may still route a
substantive repair to another automated round without distinguishing a
changes-requested answer from a commit-ready recommendation.

Then publish the next round. The reviewer will check only the decision table and
the diagram, and will not reopen Q01 through Q06.

### Final reviewer decision for design-specification code-review-requestor round 2

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-2 -->

## Round 3 by requestor

- Recorded: 2026-08-12T17:50:41+02:00
- Exchange: specification/design-specification/v0.11.0/code-review-requestor
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/design.v0.11.0.code-review-requestor.md
- Outcome: request

### Review identity for design-specification code-review-requestor round 3

Umbrella draft: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: C:/Users/vonc/git/llm-shared/docs/v0.11.0/design.v0.11.0.code-review-requestor.md
Review round: 3

### Requestor assessment for design-specification code-review-requestor round 3

Round 2 feedback was accepted in full. The carried decision section now explicitly identifies its feature-request source and uses unique `FR-Q01` through `FR-Q06` identifiers. The prematurely added design Q05 and Q06 rows were removed; all six design questions remain only in the open-question section until consolidation records the complete design decision set. The target-flow diagram now separates changes-requested answers, substantive-repair commit-ready recommendations that reach the human gate with override recommended, and polishing-only commit-ready recommendations. Please verify only the corrected decision namespace and target diagram; Q01 through Q06 remain settled and unchanged.

### Change summary for design-specification code-review-requestor round 3

Applied both round 2 changes. Retitled the inherited decision section, added its source explanation, renamed the six inherited ids to `FR-Q01` through `FR-Q06`, and removed the two premature design rows. Replaced the superseded diagram branch with three distinct routes for changes-requested, substantive commit-ready, and polishing-only commit-ready answers. Verified no duplicate decision identifier and no remaining unqualified substantive-repair route to another automated round.

### Writer response for design-specification code-review-requestor round 3

Writer response: The writer accepts the round 2 review with no disagreement. The defects originated in the earlier requested edits, and both are now corrected without changing Q01 through Q06. The document has a clean inherited-decision namespace ready for later design consolidation and one consistent state-flow description across the diagram, narrative, and acceptance cases.

### Reviewer focus for design-specification code-review-requestor round 3

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-3 -->

## Round 3 by reviewer

- Recorded: 2026-08-12T18:53:31+02:00
- Exchange: specification/design-specification/v0.11.0/code-review-requestor
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/design.v0.11.0.code-review-requestor.md
- Outcome: answer

### Reviewer assessment for design-specification code-review-requestor round 3

Both round 2 changes were applied exactly, and the results were verified
mechanically rather than read for plausibility.

The identifier collision is gone. The table now holds exactly six rows carrying
`FR-Q01` through `FR-Q06`, each appearing once, and no bare `Q0x` identifier
remains in any table in the document. The heading names its source, the added
sentence states that the design's own questions use a separate sequence and are
recorded separately once consolidated, and the two prematurely added rows are
removed so the table is uniformly inherited rather than two-thirds inherited.
Every decision, integration reference, and rejected-alternative cell in those
six rows is unchanged, and each `Integrated in` value still resolves to a
section that exists in the document.

The routing is now consistent in all three places. The document contains three
statements that send work to another automated round, and each one is qualified
by a changes-requested answer: the diagram's first branch, the
round-classification sentence, and the acceptance row for a substantive repair
that requests changes. No passage sends a substantive repair to another
automated round without distinguishing the answer type, which was the last
remaining form of the superseded claim. The diagram's three branches now match
the prose and the two acceptance rows exactly.

The six design questions are untouched, and their answers remain A1, B1, C1,
D1, E1, and F1.

One observation, not a defect. The three sibling designs in this version each
carry a `Design decisions for v0.11.0 <topic>` section holding their own
consolidated decisions, and none of them carries an inherited requirement table
at all. This design is the first to carry one, which is why the renamed heading
diverges from the sibling pattern rather than breaking it. Nothing in
`write-design`, `write-plans`, or the templates keys on that heading, so the
divergence has no downstream effect, and the traceability the inherited table
provides is worth keeping. The document already records where its own decisions
will land, so the only thing left to get right happens at consolidation, and it
is supplied as covered wording below.

Every design-level decision is settled and no question is missing. The
delegation surface, renderer boundary, authorized commit continuation,
repair-scope evidence contract, step transport, and non-compliant convergence
recovery are all answered, and each answer holds against the shared exchange
behavior it depends on.

### Question verdicts for design-specification code-review-requestor round 3

Q01 through Q04 -- delegation, renderer interface, commit continuation, and
repair-scope evidence.

Verdict: settled and unchanged across all three rounds, as requested. Not
reopened; round 3 touched only the decision table and the diagram. The
reviewer's answers remain A1, B1, C1, and D1. `pw skill` is a real router
surface, B1 mirrors the existing specification request renderer flag for flag,
C1 is the only option compatible with the shared rule against asking the human
to authorize the same commit twice, and D1's four evidence sources each cover a
failure mode that no single signal covers.

Q05 -- How does the exact implementation step reach the specialized requestor?

Verdict: settled and unchanged. The reviewer's answer remains E1. The rendered
command genuinely has no step component today, code-review identity genuinely
requires one, and E1 is the only option that keeps the handoff both inspectable
and resumable, which are the two properties Q01 selected the router for.

Q06 -- What does the requestor do when a convergence recommendation follows a
substantive repair?

Verdict: settled and unchanged. The reviewer's answer remains F1. Its
description remains accurate on every mechanical point, and F3's con remains the
line that decides the question, because the disagreement transition is not
merely a worse choice but an unavailable one from a convergence gate.

Decision-table namespace -- resolved.

The collision reported in round 2 is fixed and verified: six rows, six distinct
`FR-Q0x` identifiers, no bare `Q0x` identifier in any table, and the design's
own six questions remaining only in the open-question section until
consolidation. The heading and its added sentence make the source explicit, so a
later reader cannot mistake an inherited decision for a design decision.

Target-behavior diagram -- resolved.

The diagram now carries three distinct branches that match the round-
classification prose and both acceptance rows. Checked across the whole
document, every route to another automated round is conditioned on a
changes-requested answer.

Missing questions: none. Three rounds have settled the complete design-level
decision surface, and this round found no new contradiction, no unqualified
routing, and no duplicate identifier.

### Convergence evidence for design-specification code-review-requestor round 3

Covered wording: This recommendation covers one consolidation instruction. No further review
round is needed to apply it.

When consolidation records the design's own six answers, add them under a new
section rather than extending the inherited table. Use the sibling heading form
so this design matches `design.v0.11.0.spec-reviewer.md`,
`design.v0.11.0.spec-review-requestor.md`, and
`design.v0.11.0.review-exchange-core.md`:

## Design decisions for v0.11.0 implementation code review requests

Place it immediately after the inherited requirement table, keep the same four
columns, and use the design's own `Q01` through `Q06` identifiers in its first
column. Leave the inherited `FR-Q01` through `FR-Q06` table exactly as it is,
including its heading and its source sentence.

This keeps the two namespaces visually separate, matches the repository's design
convention for a document's own decisions, and preserves the requirement
traceability that the inherited table adds. Appending design rows to the
inherited table instead would recreate the duplicate-identifier defect that
round 2 removed.

No other edit is covered by this recommendation, and none is needed.

Convergence rationale: Every design-level decision is settled, and the two defects that blocked
round 2 are verified fixed rather than reported fixed.

The design answers six questions that together cover the decision surface this
requirement needs: how the implementation workflow enters the specialized
requestor, what renderer interface composes a request, who owns the transition
from durable authorization to the existing commit action, what evidence bounds
an accepted reviewer repair, how the implementation step reaches the requestor,
and what happens when a convergence recommendation follows a substantive repair.
No further feature-level or design-level question is missing, and none of the
six is redundant or reaches into the deferred reviewer role.

The answers hold against the mechanisms they depend on, which was checked
directly rather than assumed. The code-review family policy matches the form
used across the exchange suites. The router surface named by Q01 exists. The
renderer shape named by Q02 mirrors the shipped specification request CLI. The
continuation rule named by Q03 matches the shared requirement not to ask the
human twice. The convergence behavior named by Q06 matches the core, which
short-circuits answer consumption at a convergence gate and leaves only the two
human choices.

Round 3 fixed both reported defects completely. The inherited decision table
carries six distinct `FR-Q0x` identifiers with no bare `Q0x` identifier
remaining anywhere, and every route to another automated round is now
conditioned on a changes-requested answer across the diagram, the prose, and the
acceptance rows. Both were verified by scanning the whole document rather than
the edited passages.

What remains is one consolidation instruction, supplied as covered wording,
naming the section heading under which the design's own decisions belong. It
changes no decision and settles no question; it prevents the consolidation step
from reintroducing the duplicate-identifier defect. Spending another automated
round to place a heading would be the mechanical loop this design's own
round-classification rule argues against.

This recommendation is advisory. It does not authorize consolidation, and the
human retains the choice between consolidating and another round.

### Writer instructions for design-specification code-review-requestor round 3

No further review round is required. Proceed to consolidation for this design,
applying the one covered instruction about where the design's own decisions
belong.

Do not reopen Q01 through Q06. Do not change the inherited requirement table,
its heading, or its source sentence. Do not change the target-behavior diagram,
the round-classification prose, or the acceptance rows; all three now agree and
were verified against each other.

Do not change the feature request or the umbrella draft. The umbrella row for
this item belongs to the later implementation check, not to this design round.

Present this recommendation to the human with the identity summary and your own
assessment. The choices are `Consolidate` and `Revise and review again`. This
recommendation is advisory and does not authorize consolidation; only the human
selection does.

### Final reviewer decision for design-specification code-review-requestor round 3

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-3 -->

## Round 3 by human

- Recorded: 2026-08-12T19:08:20+02:00
- Exchange: specification/design-specification/v0.11.0/code-review-requestor
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/design.v0.11.0.code-review-requestor.md
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-3 -->
