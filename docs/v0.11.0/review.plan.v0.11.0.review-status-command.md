# Specification review transcript for v0.11.0

- Exchange: specification/plan/v0.11.0/review-status-command
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-status-command.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-08-29T23:52:31+02:00
- Exchange: specification/plan/v0.11.0/review-status-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-status-command.md
- Outcome: request

### Review identity for plan review-status-command (round 1)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/plan.v0.11.0.review-status-command.md
Review round: 1

### Requestor assessment for plan review-status-command (round 1)

The implementation plan contains four ordered, independently checkable steps
and a matching unimplemented validation skeleton. It identifies every new
production and test file, TDD and property-based coverage, focused and full
workflow commands, line budgets, split guidance, complexity bounds, and bounded
file IO.

Eight open questions cover the material implementation choices still present:
the immutable record mechanism, explicit JSON projection, initial projection
helper placement, the private IO test seam, the property-based test boundary,
renderer regression evidence, launcher test ownership, and acceptance fixture
extraction. Their options and answered recommendations are sufficient to make
implementation deterministic after consolidation. I found no missing question
that belongs to the plan rather than the already-settled requirement or design.

The recommended answers favor dependency-free frozen dataclasses, explicit
schema projection, cohesive initial modules with measured splitting, controlled
private test seams, layered fast properties, representative golden rendering,
distinct launcher unit and acceptance evidence, and one proactive acceptance
`conftest.py`. No reviewer wording suggestion exists yet in round 1.

### Change summary for plan review-status-command (round 1)

This is the initial implementation-plan review round. The writer created the
four-step implementation plan and its validation skeleton beside the settled
review-status requirement and design. The requirement, design, plan, and
validation plan now state the bounded file-IO contract explicitly. The plan
also contains eight implementation-only questions with recommendations and
answered defaults.

### Writer response for plan review-status-command (round 1)

Writer response: This is the initial request, so there is no earlier reviewer feedback to accept
or reject. The writer asks the reviewer to verify that the plan can be executed
file by file, that its tests and split points are proportionate, and that the
eight recommended implementation answers are complete without reopening the
settled feature or design.

### Reviewer focus for plan review-status-command (round 1)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

## Round 1 by reviewer

- Recorded: 2026-08-29T23:57:50+02:00
- Exchange: specification/plan/v0.11.0/review-status-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-status-command.md
- Outcome: answer

### Reviewer assessment for plan review-status-command round 1

The plan is well built and its factual base is exact. Four ordered steps, every new file named, budgets and split points stated, and eight questions that stay at implementation level without reopening the settled requirement or design. I agree with all eight recommended answers as choices. One of them contradicts the step it governs, which is the substance of this round.

I verified the confirmed technical facts against the code rather than reading them. All eight line counts are exact: `review_exchange_models.py` at 555, `review_exchange_store.py` at 633, `review_exchange_observer.py` at 139, `review_exchange_paths.py` at 231, `review_exchange_models_coordination.py` at 238, `review_exchange_models_envelope.py` at 220, `review_exchange_state.py` at 277, and `review_exchange_transcript_identity.py` at 46. All three named public boundaries exist where the plan says: `parse_json_markdown`, `current_request_occurrence`, and `ReviewExchangeObserver.classify`.

The risk-band handling is careful in a way worth naming. `review_exchange_store.py` sits at 633 lines, seventeen below the ceiling, and the plan avoids touching it by reading coordination content through the public `parse_json_markdown` rather than a private store method. That is the difference between a plan that would have forced an unrelated split mid-effort and one that does not.

The launcher lesson from the preceding requirement has been absorbed properly. Q07 splits launcher coverage between focused unit tests for self-location, runtime selection, caller-directory preservation, `PYTHONPATH`, and exit forwarding, and real caller-root parity in Step 4 acceptance. Step 3 states that `rvw_status.bat` retains the caller directory as the default discovery origin. That is exactly the shape `commit-plan-check.bat` had to be corrected into, applied from the start rather than after a defect.

The defect is that Q08 and Step 4 disagree about the same file. Q08 accepts option 8A, creating `tests/acceptance/review_status/conftest.py` from the start for repository and durable-exchange builders. Step 4 implements option 8B in three separate places. Its file list names only the acceptance package initializer, the leaf initializer, and the scenario test, with no `conftest.py`. Its split guidance is conditional rather than proactive, saying builders are extracted if the acceptance file reaches the 550-line risk band. And its budget still gives the scenario file 520 lines, which is the figure that assumes builders were never extracted, while the conftest has no budget at all.

An implementer following Step 4 would build 8B. An implementer following Q08 would build 8A. The 520-line estimate is what makes this more than bookkeeping: it sits thirty lines below the risk band, which is precisely the margin Q08 exists to remove, and it is the estimate that would be wrong once builders move out.

One smaller point concerns configuration loading rather than a question. Step 2 requires exact assertions for configuration loads, and the reported result carries the configured timeout that lease freshness is derived from. `ReviewConfiguration.load` returns an object with review mode disabled and a fallback timeout when the marker is absent, and raises only when a present marker is malformed. Both branches reach the status result, so the timeout reported in a repository without an active marker is a fallback rather than a configured value. Asserting both branches keeps that honest. No new question is needed, because the existing loader already settles the behavior.

Everything else holds. The four steps are correctly ordered and independently checkable, the validation skeleton mirrors them with all four steps recorded as not started and the document-level line correctly negative, and the property-based boundary is scoped to enumeration and ordering rather than applied to finite tables where parameterized examples are clearer. The complexity and IO clarifications match the settled design, and no step introduces a wall-clock gate where the design defines none.

One observation belongs here even though it is not a defect in this plan, because it is red now and the writer will meet it on the first implementation walk. The repository Markdown gate fails on two committed transcripts: the feature-request transcript at line 186 and the design transcript at line 223, both MD032, both because the label-inlining renderer defect flattened an ordered list onto its `Requested changes:` label line. Those lists were well formed when I authored them. This is the third transcript that defect has damaged across two efforts, it now reproduces on every round where requested changes are a list, and `ghog day` will stop at its check phase until it is addressed.

### Question verdicts for plan review-status-command round 1

## Verdict on Q01 immutable record mechanism

Agree with option 1A, frozen dataclasses plus string-valued enums.

This matches how the surrounding code already works. `ArtifactState`, `Actor`, and `CoordinationStatus` are string enums, and the exchange models are frozen dataclasses with validating post-init hooks. Choosing the same mechanism keeps the new result readable beside the types it wraps and adds no dependency, which matters for a diagnostic command that must run after a restart with nothing set up.

## Verdict on Q02 ownership of JSON schema projection

Agree with option 2A, per-record explicit projection.

Correct, and consistent with the precedent this repository already set: `CommitPlanCheckResult.structured_payload` and `CodeReviewEvidence.to_payload` both project explicitly rather than reflecting over fields. Generic dataclass conversion would make the wire format a side effect of field names, so a later rename would silently break `rvw_resume`. The small amount of deterministic mapping code is the price of a stable schema, and the answer says so.

## Verdict on Q03 initial placement of projection helpers

Agree with option 3A, one initial service module with a named split path.

Same shape as the equivalent decision in the preceding effort, and right for the same reason: a 450-line advisory estimate against a 650 ceiling does not justify pre-splitting, and the plan already names both the destination and the trigger. Premature separation would spread one service across files before any measurement supports it.

## Verdict on Q04 read-boundary injection

Agree with option 4A, a private IO dependency bundle.

The requirement is to prove bounded reads, exact candidate enumeration, and the absence of writes without widening the public contract. A private seam does that while `collect_review_status(root, wall_clock)` stays the public shape. The con is honest, since a private seam is a test-visible internal, but the alternative of widening the command signature for testability would be worse for a command other tooling will call.

## Verdict on Q05 property-based test boundary

Agree with option 5A, the layered strategy.

The scoping is the good part. Properties are applied where the input space is genuinely large and order-sensitive, which is candidate enumeration and result ordering, while the finite state, role, lease, artifact, action, renderer, and process-status tables stay parameterized examples. That keeps generated examples from paying filesystem cost on every case and keeps failures readable, which is the same reasoning the plan gives for not adding a wall-clock gate.

## Verdict on Q06 renderer regression evidence

Agree with option 6A, mixed golden and focused assertions.

Complete golden strings for every case would make each formatting change a wall of diff noise, and targeted assertions alone would let whole-document drift pass. Representative goldens for the wire and human contracts plus focused field assertions elsewhere is the proportionate answer.

## Verdict on Q07 launcher coverage split

Agree with option 7A, focused unit forwarding plus real acceptance parity.

This is the round's best question, because it is the preceding requirement's defect turned into a decision. There, launcher coverage was a unit test that matched text inside the batch file, so it passed against a launcher that reported the wrong repository entirely, and the defect surfaced only when the behavior was executed. Option 7A puts executable argument and exit-code forwarding in the unit leaf with a controlled target and reserves real caller-root parity for acceptance, so neither layer is text matching and neither duplicates the other's setup. Option 7C is correctly rejected for delaying quoting and exit-forwarding discovery to the final step.

## Verdict on Q08 acceptance fixture extraction timing

Agree with option 8A as the choice, but the plan does not implement it.

The reasoning for 8A is sound. A 520-line estimate sits thirty lines below the risk band, the builders are genuinely reusable, and one conventional `conftest.py` is a responsibility-based split rather than fragmentation. Option 8B's con names the real cost, which is a mechanical split forced during the final implementation step.

Step 4 nevertheless describes 8B. Its file list omits `conftest.py` entirely, its split guidance extracts builders only if the acceptance file reaches 550, and its 520-line budget is the no-extraction figure while the conftest has no budget. All three need to follow the accepted answer, and the scenario estimate should drop to reflect builders living elsewhere.

## Verdict on overall question coverage

The eight questions are the right eight and I found no missing implementation decision. They cover the mechanism, the wire format, module granularity, the test seam, the property boundary, rendering evidence, launcher layering, and fixture timing, which is the full set of choices Steps 1 through 4 leave open. None reopens the settled requirement or design, and none prescribes behavior that those documents already fixed.

One coverage point sits below question level and is noted in the writer instructions rather than requested as a question: Step 2 should assert both branches of configuration loading, since the reported timeout differs when the review-mode marker is absent.

### Requested changes for plan review-status-command round 1

Requested changes: Add `tests/acceptance/review_status/conftest.py` to the Step 4 file list as a new file to be created, so the step implements the accepted Q08 option 8A.

Rewrite Step 4's split guidance so repository and durable-exchange builders live in `conftest.py` from the start, instead of moving there only if the acceptance file reaches the 550-line risk band, and keep the existing later trigger for splitting protocol-state construction from subprocess invocation.

Lower the acceptance scenario file's 520-line advisory estimate to reflect builders living in `conftest.py`, and give `conftest.py` its own advisory estimate, below-550 note, and 650 ceiling entry.

State the resulting headroom in the Q08 answer, since the reason for choosing 8A was that thirty lines below the risk band is too little margin.

Add both configuration-load branches to the Step 2 test list: the marker present, where the reported timeout is the configured value, and the marker absent, where it is the fallback and review mode is disabled.

### Writer instructions for plan review-status-command round 1

## Instruction to make Step 4 implement the accepted Q08 answer

Keep option 8A. Bring Step 4 into line with it in the three places where it currently describes 8B.

Add `tests/acceptance/review_status/conftest.py` to the Step 4 file list as a new file to be created, alongside the acceptance package initializer, the leaf initializer, and the scenario test.

Rewrite the split guidance so extraction is the starting position rather than a threshold response. It currently reads that builders move to `conftest.py` if the acceptance file reaches the 550-line risk band, which is exactly option 8B. State instead that repository and durable-exchange builders live in `conftest.py` from the start and that public scenario assertions stay in the test leaf. Keep the existing second clause about splitting protocol-state construction from subprocess invocation if the conftest itself approaches the risk band, since that remains a genuine later trigger.

Correct the line budgets. The scenario file's 520-line advisory estimate assumes the builders are still inside it, and it should drop to reflect their extraction. Give `tests/acceptance/review_status/conftest.py` its own advisory estimate, below-550 note, and 650 ceiling entry so the shared execution checklist can measure it like every other file.

State the resulting margin in the Q08 answer. The reason 8A was chosen is that thirty lines of headroom is too little; the revised estimates should show the headroom the decision buys, otherwise the next reader cannot tell whether the choice worked.

## Instruction to cover both configuration-load branches in Step 2

Step 2 requires exact assertions for configuration loads, and the status result reports the configured timeout that lease freshness is derived from. `ReviewConfiguration.load` returns an object with review mode disabled and a fallback timeout when `a.review-mode` is absent, and raises only when a present marker is malformed.

Add both branches to the Step 2 test list: a repository with the marker present, where the reported timeout is the configured value, and a repository without it, where the reported timeout is the fallback and review mode is disabled. This needs no new question, because the existing loader already settles the behavior; it is missing evidence rather than a missing decision.

## Instruction on what to leave unchanged

Keep the confirmed technical facts, which I verified against the code and found exact, including the deliberate choice to read coordination content through the public `parse_json_markdown` so `review_exchange_store.py` stays at 633 lines and clear of the ceiling.

Keep the four-step order, the validation skeleton, the Step 0 assessment that adds no wall-clock gate, and the property-based scoping that applies Hypothesis to enumeration and ordering while leaving the finite tables as parameterized examples.

Keep every one of the eight recommended answers. Seven need no change at all, and Q08 needs its step brought to it rather than the answer weakened.

Keep Q07 and its Step 3 wording in particular. The split between executable unit forwarding and real acceptance parity, with the launcher retaining the caller directory as the default discovery origin, is the corrected shape of the preceding requirement's launcher defect, and it should not drift back toward text matching.

## Instruction about the repository gate before implementation begins

This is outside the reviewed plan and outside my authority to repair, but it will block the first implementation walk.

The repository Markdown gate currently fails on two committed transcripts: `docs/v0.11.0/review.feature-request.v0.11.0.review-status-command.md` at line 186 and `docs/v0.11.0/review.design-specification.v0.11.0.review-status-command.md` at line 223, both MD032. Both are caused by the label-inlining renderer defect flattening a well-formed ordered list onto its `Requested changes:` label line.

This is the third transcript that defect has damaged across two efforts, and it now reproduces on every round whose requested changes are a list. The cause is the four call sites in `tools/spec_review_answer.py`, `tools/spec_review_request.py`, `tools/code_review_request.py`, and `tools/code_review_answer.py`, with the correct idiom already present at `tools/code_review_answer.py:288`. Repairing the two lines unblocks the gate; fixing the call sites stops the next transcript from joining them.

### Final reviewer decision for plan review-status-command round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-08-30T00:04:04+02:00
- Exchange: specification/plan/v0.11.0/review-status-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-status-command.md
- Outcome: request

### Review identity for plan review-status-command (round 2)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/plan.v0.11.0.review-status-command.md
Review round: 2

### Requestor assessment for plan review-status-command (round 2)

The round-1 finding was valid and has been fully applied without disagreement.
Step 4 now creates `tests/acceptance/review_status/conftest.py` from the start,
places repository and durable-exchange builders there, budgets it at 240 lines,
and reduces the scenario leaf estimate from 520 to 380 lines. The split guidance
now treats that extraction as the starting layout and retains only the later
trigger that separates protocol-state construction from subprocess invocation
if the conftest approaches the risk band.

Q08 now records the resulting 170-line scenario headroom below the 550-line risk
band. Step 2 also covers both configuration-load branches: marker present with
the configured timeout and marker absent with disabled mode and the fallback
timeout. The validation skeleton names the new conftest and the two timeout
branches.

All eight recommended answers remain unchanged, their implementation details
now agree with every numbered step, and no additional implementation question
is missing. The two known transcript MD032 findings remain outside this plan
review and were not altered in this round.

### Change summary for plan review-status-command (round 2)

Applied every round-1 requested plan change. Added the proactive Step 4
`conftest.py`, assigned its file responsibility and 240-line budget, lowered the
scenario estimate to 380 lines, rewrote split guidance to match Q08 option 8A,
and recorded the resulting 170-line risk-band headroom in Q08. Added
marker-present and marker-absent configuration evidence to Step 2 and mirrored
the affected file and evidence in the validation plan.

### Writer response for plan review-status-command (round 2)

Writer response: I agree with the round-1 assessment. The conflict between Step 4 and accepted
Q08 option 8A was substantive and is now removed in the file list, fixture
ownership, budgets, split guidance, and question rationale. I also accepted the
configuration-loading coverage point and added both existing loader branches.
No recommendation was rejected and there is no disagreement between writer and
reviewer.

### Reviewer focus for plan review-status-command (round 2)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-08-30T00:07:19+02:00
- Exchange: specification/plan/v0.11.0/review-status-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-status-command.md
- Outcome: answer

### Reviewer assessment for plan review-status-command round 2

Every round-one item is applied, and applied in all the places the round-one finding named rather than only in the one that was easiest to change. I verified each against the current document.

Confirmed applied:

- `tests/acceptance/review_status/conftest.py` is now in the Step 4 file list as a new file to be created.
- The split guidance is proactive rather than conditional: builders live in the conftest from the start and public scenario assertions stay in the test leaf, with the later trigger retained for splitting protocol-state construction from subprocess invocation.
- The budgets moved together. The conftest has its own 240-line advisory entry with the below-550 note and the 650 ceiling, and the scenario leaf dropped from 520 to 380.
- Q08's answer records the resulting headroom, which was the point of choosing 8A rather than a detail about it.
- Step 2 covers both configuration-load branches, marker present reporting the configured timeout and marker absent returning disabled mode with the fallback.
- The validation plan mirrors both the new conftest file and the two timeout branches, so the evidence obligation moved with the plan rather than lagging it.

All eight questions and their answers are intact, and none of the seven I accepted unchanged in round one was disturbed.

I checked the new material rather than only confirming my own request. Two things are worth recording.

The extraction raised the total estimate rather than redistributing it. One 520-line file became a 240-line conftest and a 380-line leaf, so the sum grew by a hundred lines. That is the ordinary cost of extraction, since fixtures acquire a module docstring, imports, decorators, and explicit signatures that inline helpers did not need. Both files sit well below the risk band and the ceiling, so nothing is owed here beyond noticing that the sum is expected to grow.

Step 4's completion criteria did not need updating, which I checked rather than assumed. Its grep is scoped to the whole `tests/acceptance/review_status` directory, so the new conftest is already inside the evidence it collects.

Two details in the surrounding step deserve to be called out as good, because they are the settled lessons of the two preceding requirements applied before anything is built. Step 4 invokes the launcher from a nested caller path and the direct module against the same root, parses both JSON payloads, and compares them in full. That is a stronger parity test than the one `commit-plan-check` eventually needed, and it is here from the start rather than after a defect. And the criteria bind the acceptance file to every row of the design's acceptance table, which now includes the escalated and wait-timeout-escalation rows that exist because this exchange was itself interrupted overnight.

The plan settles every implementation decision a developer needs. Four ordered steps, every new file named with a budget and a split path, tests specified before behavior, property-based coverage scoped to enumeration and ordering while the finite tables stay parameterized, and no wall-clock gate invented where the design defines none.

The two committed transcript MD032 findings are unchanged and remain outside this plan review, as the requestor correctly notes. They are still red, and the first implementation walk will stop at the check phase until they are addressed. I confirmed that my round-one answer added no new finding of its own.

What remains on this document is optional wording only, listed separately and carrying no implementation consequence. There is no disagreement between the roles in this exchange.

### Question verdicts for plan review-status-command round 2

## Round two verdict on Q01 through Q07

Unchanged and agreed. I accepted these seven in round one, asked for no change to any of them, and none was made.

Q07 remains the one I would most want preserved through consolidation. Its split between executable unit forwarding and real acceptance parity is the corrected shape of the launcher defect from the preceding requirement, and Step 4 now strengthens it further by invoking the launcher from a nested caller path rather than merely from a different repository.

## Round two verdict on Q08 acceptance fixture extraction timing

Agree with option 8A, and the plan now implements it.

The round-one problem was never the choice; it was that Step 4 described option 8B in its file list, its split guidance, and its budget while the answer selected 8A. All three now agree with the answer. The conftest is a named file with its own budget, the guidance treats extraction as the starting layout, and the scenario estimate dropped to reflect builders living elsewhere.

The answer also now carries the fact that justified the choice. Round one chose 8A because thirty lines of headroom below the risk band was too little; the answer now states the 170 lines the split produces. That turns the rationale into something a later reader can check rather than take on trust.

One wording point sits inside that sentence. It calls 240 an estimate and then calls the resulting headroom measured, but both figures are advisory until implementation counts them. That is listed as optional wording, and it changes nothing about the decision.

## Round two verdict on the configuration-load coverage point

Applied as asked, and correctly scoped.

Step 2 now covers the marker-present branch reporting the configured timeout and the marker-absent branch returning disabled mode with the fallback. That was deliberately not raised as a new question in round one, because `ReviewConfiguration.load` already settles the behavior in code; it was missing evidence rather than a missing decision, and it has been added as evidence.

The validation plan mirrors both branches, so the obligation is recorded where the implementation check will look for it.

## Round two verdict on remaining question coverage

The set remains the right eight and is complete. I looked again for an implementation decision the four steps leave open and found none. Record mechanism, wire format, module granularity, test seam, property boundary, rendering evidence, launcher layering, and fixture timing cover the choices the steps present.

No question is missing, redundant, unclear, or outside scope, and none reopens the settled requirement or design.

### Convergence evidence for plan review-status-command round 2

Covered wording: These are optional and carry no implementation consequence. The plan is executable exactly as written if none is applied.

The Q08 answer calls the 240-line figure an estimate and then calls the resulting 170 lines of headroom measured. Both are advisory until implementation counts them, and the shared execution checklist is what turns them into measurements later. Reading "170 lines of estimated risk-band headroom" would keep the two halves of the sentence consistent.

The Step 4 budget list would benefit from one sentence noting that the total estimate rose from 520 to 620 lines across two files, because extraction adds a module docstring, imports, fixture decorators, and explicit signatures that inline helpers did not need. Without it, a reader comparing the two rounds may wonder whether the scenario estimate was simply moved rather than genuinely reduced.

Step 2's configuration bullet packs both branches into one sentence with two subordinate clauses. Splitting it into two bullets, one per branch, would match how the surrounding bullets in that list are shaped and make each branch independently checkable during the implementation check.

None of these changes a decision, an option, an answer, a file list, a budget, or an acceptance obligation.

Convergence rationale: I recommend convergence because the round-one contradiction is resolved everywhere it appeared, the supporting evidence moved with it, and I could not find a new gap.

The round-one finding was that Q08 accepted one option while Step 4 described another in three separate places. A partial fix would have been easy to mistake for a complete one, so I checked all three: the file list now names the conftest, the split guidance now treats extraction as the starting layout rather than a threshold response, and the budgets moved together with a 240-line entry for the fixture file and a reduction from 520 to 380 for the scenario leaf. The validation plan mirrors the new file and the new evidence, so the implementation check will look for what the plan now promises.

The answer also gained the fact that motivated the choice. Choosing 8A was justified by headroom, and the answer now states the 170 lines the split produces rather than leaving a later reader to recompute it.

The configuration point was applied at the right altitude. I raised it as missing evidence rather than a missing decision, because the loader already settles the behavior in code, and it was added as two test branches rather than as a ninth question.

I verified rather than accepted. I re-read the Step 4 file list, budgets, and split guidance; confirmed the completion criteria needed no change because their grep already covers the whole acceptance directory; confirmed all eight questions and answers survive intact; and confirmed the validation plan names both the conftest and the two timeout branches. I also noticed and checked something the change summary did not mention, which is that the total estimate rose by a hundred lines across the two files. That is ordinary extraction overhead and both files stay far below the risk band, so it is worth a sentence rather than a round.

Two parts of Step 4 are stronger than what the preceding requirements ended up with, and they arrived before any code exists. Launcher parity is proven from a nested caller path against the direct module with full payload comparison, which is a harder test than the one `commit-plan-check` needed after its defect. And the acceptance obligation is bound to every row of the design's acceptance table, which now includes the escalation rows that exist only because this exchange was itself interrupted overnight and had to be recovered by hand.

What remains is three optional phrasing items, none of which changes a decision, option, answer, file list, budget, or acceptance obligation. That is wording-only by this exchange's standard, so another automated round would not improve the plan.

One thing outside this plan should not be lost at the gate. The repository Markdown gate is red on two committed transcripts, and the first implementation walk will stop at its check phase until they are repaired. That is unrelated to this plan's readiness and unrelated to any decision in it, but it stands between consolidation and a green Step 1.

This recommendation is advisory. It does not authorize consolidation, and the human remains the only party who may choose `Consolidate` or `Revise and review again`.

### Writer instructions for plan review-status-command round 2

No substantive change is required. Do not open another revision cycle on my account.

If the human selects `Consolidate`, proceed with the canonical `consolidate-then-review-ask-questions` workflow on `docs/v0.11.0/plan.v0.11.0.review-status-command.md`. When consolidating:

- Carry every accepted answer for Q01 through Q08 into the decision record with its reason. Q07's reason in particular should survive in full, because it encodes why launcher coverage is split between executable unit forwarding and real acceptance parity, and that split exists to prevent a repeat of a defect that a text-matching launcher test could not catch.
- Keep the Step 4 conftest as a named file with its own budget. Folding it back into the split guidance as a conditional extraction would restore the exact conflict this round removed.
- Keep the nested-caller-path parity requirement in Step 4. Invoking the launcher from a nested path rather than merely from another repository is what proves caller-directory preservation rather than assuming it.
- Keep the binding of the acceptance file to every row of the design's acceptance table. That table now includes the escalation rows, and they are the ones a future regression in the role mapping would break first.

The three phrasing suggestions in the covered-wording input are optional. Apply any, all, or none before consolidation; none alters a decision.

One item stands between consolidation and a green first implementation step, and it is outside this plan. The repository Markdown gate fails on `docs/v0.11.0/review.feature-request.v0.11.0.review-status-command.md` at line 186 and `docs/v0.11.0/review.design-specification.v0.11.0.review-status-command.md` at line 223, both MD032, both committed. Repairing those two lines unblocks the gate. Fixing the four label-inlining call sites in `tools/spec_review_answer.py`, `tools/spec_review_request.py`, `tools/code_review_request.py`, and `tools/code_review_answer.py`, using the idiom already present at `tools/code_review_answer.py:288`, stops the next transcript from joining them. I avoided a fourth occurrence this round by authoring requested changes as prose rather than a list, which is a workaround rather than a fix.

If the human instead selects `Revise and review again`, treat the covered wording as the full scope of that round unless the human supplies guidance that adds to it.

### Final reviewer decision for plan review-status-command round 2

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-2 -->

## Round 2 by human - human-confirmation

- Recorded: 2026-08-30T11:27:52+02:00
- Exchange: specification/plan/v0.11.0/review-status-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-status-command.md
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->
