# Specification review transcript for v0.11.0

- Exchange: specification/plan/v0.11.0/code-review-requestor
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-review-requestor.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-08-12T19:25:10+02:00
- Exchange: specification/plan/v0.11.0/code-review-requestor
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-review-requestor.md
- Outcome: request

### Review identity for plan code-review-requestor round 1

Umbrella draft: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-review-requestor.md
Review round: 1

### Requestor assessment for plan code-review-requestor round 1

The four-step plan maps the settled design to paired rendering, canonical requestor instructions/adapters, commit-gate and `pw` integration, and final acceptance coverage. The validation skeleton uses matching Step 1 through Step 4 sections. Four implementation-level questions remain: whether step-aware command syntax stays in Step 3, how authorized commit continuation is tested safely, how repair-scope policy and executable evidence are divided between Steps 2 and 4, and whether risk-band routers split only on measured ceiling breach. Each question includes complete alternatives and a recommended answer. Please review file ownership, step ordering, test seams, command gates, and line-budget constraints only; do not reopen feature or design decisions.

### Change summary for plan code-review-requestor round 1

Initial implementation-plan review round. Wrote the four-step implementation plan and aligned validation skeleton, performed current source/test-tree and physical-line-count checks, added shared `ghog` execution commands, and added Q01 through Q04 for remaining implementation choices. No prior plan-review feedback has been applied.

### Writer response for plan code-review-requestor round 1

Writer response: This is the first automated plan-review round. The writer recommends A1, B1, C1, and D1: keep command syntax with Step 3 routing, use temporary repositories with only the final commit subprocess seam intercepted, test repair scope at instruction and acceptance levels, and split risk-band routers only if measured growth crosses 650 lines.

### Reviewer focus for plan code-review-requestor round 1

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

## Round 1 by reviewer

- Recorded: 2026-08-12T19:41:01+02:00
- Exchange: specification/plan/v0.11.0/code-review-requestor
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-review-requestor.md
- Outcome: answer

### Reviewer assessment for plan code-review-requestor round 1

This is a strong implementation plan. Every measurable claim in it was checked
against the repository rather than read for plausibility, and all of them hold.
All ten baseline line counts are exact: 572, 552, 558, 201, 47, 413, 77, 120,
69, and 137. `render_command` really does emit only `<skill> on <document>`.
`_implementation_command` really does exist in the skill module and derives the
next uncommitted step. The batch-commit mechanics really do live behind a
subprocess boundary in `tools/git_batch_commit_git.py`, which is what makes
Q02's chosen seam a real seam rather than an aspiration. The four steps are
ordered by dependency, each new responsibility lands in a new module or leaf
test package rather than in a risk-band file, and the deferred items match the
umbrella.

The four questions are the right implementation-level questions, and this
reviewer would choose A1, B1, C1, and D1 as recommended. Q02 is the best of
them: it puts the mock at the external side-effect boundary instead of mocking
the behavior under test, and its recommendation remembers to cover the failure
path so authorization stays pending for replay, which matches the shared
owning-action contract.

Two gaps block implementation, and both are concrete rather than stylistic.

The first is that the step token has no defined syntax. Q01 settles which step
owns the command extension but not what the extended command looks like. Step 3
names `render_step_command` and requires a test that step-aware Codex and Claude
rendering work while ordinary rendering stays byte-compatible, and that test
cannot be written without the exact expected string. The form is also
user-visible, because a human copies the printed command into the reviewer
session, and three plausible shapes produce three different parsers.

The second is that Step 4 has no way to produce the code-family answer it
depends on. Its behavior section says shared exchange answer publication
simulates the deferred reviewer, but no renderer can produce that artifact:
`spec_review_answer_cli` derives its context through `specification_context`,
which hardcodes the specification family and maps a document prefix to a type
token, so a plan document yields a specification-family `plan` identity rather
than the `code` identity with an implementation step that a code exchange
requires. `publish-answer` will accept hand-authored Markdown whose envelope
matches, so the scenario is achievable, but the plan does not say how the
fixture builds it, and the three available routes differ enough that two
implementers would not converge.

One smaller point concerns how Step 2 asserts the instruction contract. Q03's
option C1 is right that both the instruction surface and the executable
behavior need coverage, and C3's con names the real risk. The refinement worth
making is in how those assertions are written: instruction tests that pin
verbatim sentences become change detectors that can lock a defect in place. This
repository has a live example, since two tests asserted the reviewer
instruction's manifest-retirement wording and would have kept passing while that
rule stayed wrong. Step 2 should assert required tokens and their required
ordering rather than whole sentences.

One observation that needs no change. The plan calls 650 the repository ceiling
throughout, which matches the sibling plans in this version. The automated gate
in `bin/check_big_files.bat` actually fails at 700. That makes 650 a stricter
process ceiling enforced by the plan's own checkpoints rather than by tooling,
which strengthens D1 rather than weakening it, because a drift to 660 would pass
the gate and only the step's line-budget checkpoint would catch it.

### Question verdicts for plan code-review-requestor round 1

Q01 -- Which step owns the `pw` command-syntax extension?

Verdict: right question, right answer, incomplete. The reviewer would choose A1.
The step-aware helper has no standalone user outcome, so A3's fifth
implementation and validation cycle would buy an isolated test boundary that the
new focused module and its separate test package already provide. A2's con is
correct that host workflow command rendering and request-artifact rendering are
different responsibilities that should not share a step. A1's con is honest
about Step 3 being the broadest step, and that cost is acceptable because Step 3
is the only vertical slice in the plan. What A1 does not settle is the syntax of
the extended command, which Step 3's own rendering test requires. Proposed below
as Q05.

Q02 -- How should authorized commit continuation be acceptance-tested without
making real repository commits?

Verdict: settled, and the strongest question in the plan. The reviewer would
choose B1. The seam it names is real: `tools/git_batch_commit_git.py` wraps the
commit in a subprocess boundary, so intercepting there leaves routing, durable
authorization, and Git-derived context executing for real. B2's con is decisive,
because mocking every Git and exchange operation removes exactly the composition
the test exists to prove. B3's con is right that making cleanup part of test
correctness is a defect rather than a cost. The recommendation's second half
matters as much as the first: covering the failure path so authorization remains
pending for replay is what proves the owning-action contract rather than only
the happy path. Nothing to change.

Q03 -- Where should repaired-path and staged-diff scope assessment be tested?

Verdict: settled, with one refinement to how the Step 2 half is written. The
reviewer would choose C1. C2's con is right that instruction-structure tests
cannot prove the workflow supplies all four evidence sources, and C3's con names
the real failure mode, which is an adapter or instruction edit silently removing
mandatory guidance while fixtures still manufacture compliant behavior. The
duplication is intentional and justified. The refinement is that instruction
assertions must target the contract rather than its prose, because a test
pinning verbatim sentences turns into a change detector that preserves whatever
the sentence says, including a mistake. Requested as a change to Step 2's tests
rather than as a change to the answer.

Q04 -- Should Step 3 split a risk-band router before adding code-review
delegation?

Verdict: settled. The reviewer would choose D1. D2's con is correct that
requiring a split converts an unrelated refactor into mandatory feature work
while both baselines are already within policy, and D3 is simply out of bounds.
D1 is also the option that keeps the new responsibility in
`prompt_workflow_code_review.py`, which is what actually protects the risk-band
files. Worth knowing while applying it: the automated gate fails at 700, not
650, so the 650 ceiling this plan enforces is a process rule that only the
step's own line-budget checkpoint will catch. That makes the Step 3 checkpoint
load-bearing rather than advisory. No change to the answer.

Q05 -- What exact command syntax carries the implementation step? (missing,
must be added)

The design settled that the rendered command carries the step; the plan settles
which step builds it; neither settles its form. `render_command` currently emits
`{prefix}{name} on {document}` and nothing else. Step 3 requires a test proving
step-aware Codex and Claude rendering while ordinary rendering stays
byte-compatible, and that test needs an exact expected string. The form is also
the human-visible handoff copied into the reviewer session.

Options should be: a trailing space followed by the keyword token `step <id>` appended after
the document; a trailing space followed by the flag token `--step <id>`; or a compact document
qualifier such as `<document>#<id>`. The reviewer recommends the trailing
keyword token, because it reads as prose in the same way the existing space-delimited `on` token
separator does, stays unambiguous for step ids like `4A`, and leaves the
ordinary command a strict prefix of the step-aware one, which makes the
byte-compatibility assertion in Step 3 trivial to state.

Q06 -- How does Step 4 produce the code-family answer that simulates the
deferred reviewer? (missing, must be added)

Step 4 states that shared exchange answer publication simulates the reviewer,
but no existing renderer can produce a code-family answer.
`spec_review_answer_cli` builds its context through `specification_context`,
which hardcodes the specification family and derives the type token from the
document prefix, so a plan document produces a specification `plan` identity
rather than the `code` identity with an implementation step. `publish-answer`
validates the envelope against the exchange identity, so the fixture must supply
a correctly shaped code answer by some other means.

Options should be: hand-author the answer Markdown inside the acceptance
fixture; add a small test-local builder that composes a valid code answer
envelope and body; or bring part of the deferred `code-reviewer` renderer
forward into this effort. The reviewer recommends the second. Hand-authored
Markdown repeated across many scenarios drifts from the envelope contract
silently, while a test-local builder keeps one definition of a valid code answer
without adding production surface that belongs to the deferred effort, which the
third option would do in violation of this plan's own scope.

### Requested changes for plan code-review-requestor round 1

Requested changes: Change 1 -- add Q05 on the step-token command syntax.

Title it "What exact command syntax carries the implementation step?". Its
description must state that the design settled that the command carries the step
and Q01 settled which step builds it, that `render_command` currently emits a
host prefix, an instruction name, the space-delimited `on` token, and one document path,
that Step 3 requires an exact expected string to assert step-aware rendering
against byte-compatible ordinary rendering, and that the form is the
human-visible handoff copied into the reviewer session.

Offer three options: a trailing keyword token appended after the document; a
flag-style suffix; or a compact document qualifier. Recommend and answer the
trailing keyword token, on the ground that it matches the existing space-delimited `on` token
separator's prose style, stays unambiguous for step ids such as `4A`, and leaves
the ordinary command a strict prefix of the step-aware one so Step 3's
byte-compatibility assertion is direct.

Then record the chosen literal form in Step 3's "Classes and behavior" beside
`render_step_command`, so the step can be implemented and tested without
reopening the question.

Change 2 -- add Q06 on producing the code-family answer in Step 4.

Title it "How does Step 4 produce the code-family answer that simulates the
deferred reviewer?". Its description must state that Step 4 relies on shared
exchange answer publication to stand in for the deferred reviewer, that
`spec_review_answer_cli` derives context through `specification_context`, which
hardcodes the specification family and maps the document prefix to a type token,
so a plan document yields a specification `plan` identity rather than the `code`
identity with an implementation step, and that `publish-answer` validates the
envelope against the exchange identity.

Offer three options: hand-author the answer Markdown inside each acceptance
fixture; add a test-local builder that composes one valid code answer envelope
and body; or bring part of the deferred `code-reviewer` renderer forward.
Recommend and answer the test-local builder, on the ground that repeated
hand-authored Markdown drifts from the envelope contract silently while the
third option adds production surface this plan explicitly defers.

Then name that builder in Step 4's "Files involved" and "Classes and behavior",
so the fixture layer has an owner.

Change 3 -- make Step 2's instruction assertions target the contract, not its
prose.

In Step 2 "Tests first", the first bullet currently asserts a list of literal
strings. Add one sentence after that bullet list:

Instruction assertions check required tokens and their required ordering rather
than whole sentences, so a wording change does not fail the suite and a rule
change does.

This is not a change to Q03's answer, which stays C1. It closes the failure mode
that instruction tests otherwise introduce: a test pinning verbatim prose
preserves whatever that prose says, including a mistake, and this repository has
a live example in the reviewer instruction's manifest-retirement rule, where two
tests asserted the wording and would have kept passing while the rule was wrong.

Leave Q01 through Q04, all four step structures, every line-budget checkpoint,
the confirmed technical facts, and the validation plan unchanged.

### Writer instructions for plan code-review-requestor round 1

Apply the changes below to
`docs/v0.11.0/plan.v0.11.0.code-review-requestor.md` only. Do not change the
feature request, the design, the validation plan, or the umbrella draft.

Keep Q01 through Q04 exactly as they are, including every option, pro, con,
recommendation, and answer. Add the two new questions after Q04 as Q05 and Q06,
using the same description, BBQ, options, recommendation, and answer structure
the existing four use.

Changes 1 and 2 each have a second half that matters as much as the question:
record the chosen command form in Step 3's "Classes and behavior", and name the
answer builder in Step 4's "Files involved" and "Classes and behavior". A
question answered but not reflected in its step leaves the step no more
implementable than before.

Do not restate the design's decisions in the plan. Both new questions are
implementation choices that the design deliberately left open, not
reconsiderations of settled behavior.

After editing, confirm that Step 3 states the literal step-aware command form
and that Step 4 names the component producing its code-family answers. Then
publish the next round; the reviewer will check the two new questions, their
step integration, and the Step 2 test sentence, and will not reopen Q01 through
Q04.

### Final reviewer decision for plan code-review-requestor round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-08-12T19:59:20+02:00
- Exchange: specification/plan/v0.11.0/code-review-requestor
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-review-requestor.md
- Outcome: request

### Review identity for plan code-review-requestor round 2

Umbrella draft: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-review-requestor.md
Review round: 2

### Requestor assessment for plan code-review-requestor round 2

Round 1 feedback was accepted in full. Q01 through Q04 remain unchanged. Q05 fixes the exact human-visible command as `<skill> on <document> step <id>` and Step 3 records that literal form beside `render_step_command`. Q06 assigns valid code-family answer construction to `tests/unit/tools/test_code_review_requestor_acceptance/code_answer_builder.py`, which is now named in Step 4 files and behavior. Step 2 instruction tests now assert required tokens and ordering rather than whole prose sentences. Please verify these two new questions and their step integration without reopening the four settled implementation questions, line budgets, or validation skeleton.

### Change summary for plan code-review-requestor round 2

Applied all three round 1 requested changes. Added Q05 and its literal trailing space followed by `step <id>` contract to Step 3. Added Q06 and named a test-local code answer builder in Step 4 files and behavior. Added the Step 2 token-and-order assertion rule. All existing step structures, baselines, checkpoints, validation sections, and Q01 through Q04 remain unchanged.

### Writer response for plan code-review-requestor round 2

Writer response: The writer accepts the round 1 review with no disagreement. The plan is now directly implementable where it previously lacked an expected command string and a valid source of code-family test answers. The writer recommends E1 and F2 and requests verification of their integration into Steps 3 and 4.

### Reviewer focus for plan code-review-requestor round 2

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-08-12T20:03:50+02:00
- Exchange: specification/plan/v0.11.0/code-review-requestor
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-review-requestor.md
- Outcome: answer

### Reviewer assessment for plan code-review-requestor round 2

All three round 1 changes were applied, and both of the two-part changes were
applied in full, which was the specific risk called out last round. Q05 fixes
the command form and Step 3 records it literally beside `render_step_command`,
including the property that makes it testable: the ordinary command remains a
byte-identical strict prefix. Q06 selects the test-local builder and Step 4
names `code_answer_builder.py` in both its files list and its behavior section,
so the fixture layer has an owner rather than an intention.

The two new questions are well built. Q05's options are genuinely distinct in
contract rather than in taste, and E1's con is honest that a positional phrase
is something specialized parsers must recognize. E3's con is the one that
decides it, since conflating document identity with step identity is a cost no
brevity gain offsets. Q06's description restates the mechanism accurately, and
F2's con is honest that a test helper must track shared envelope changes. F3's
con correctly frames bringing the deferred renderer forward as a scope
violation rather than merely early work.

The Step 2 refinement landed verbatim and in the right place, directly after the
three assertion bullets, so it governs all of them.

Q01 through Q04 are unchanged and remain correct, and every baseline, checkpoint,
and validation section is intact. The plan is now implementable end to end:
Step 3 has its exact expected string and Step 4 has its answer source, which
were the two things missing last round.

Four mechanical omissions remain, all of them completeness rather than
correctness, and all supplied as covered wording below.

Three substantive new Python modules have no line-budget checkpoint:
`test_prompt_workflow_code_review_tdd.py` and
`test_implement_step_integration_tdd.py` from Step 3, and
`code_answer_builder.py` from Step 4. Steps 1 and 2 give every substantive
module they create a checkpoint, and `__init__.py` files are consistently
unbudgeted across all four steps, so these three are the only inconsistency. The
builder is the one that matters most in practice: its direct analogue in the
sibling effort, the acceptance `fixtures.py`, finished at 288 lines against a
120-220 advisory band, so a shared-fixture module is exactly the file that tends
to overrun. The hard ceiling still applies to all three through shared checklist
item 7, so what is missing is the early warning, not the enforcement.

Step 3 also has no `rg` contract check for the command form Q05 just fixed.
Steps 1, 2, and 4 each pin their newly introduced contract with a grep, and
Step 3's two greps cover the no-scan property and the thin integration instead.
The command form is the plan's most byte-sensitive new contract and the only one
a human reads directly, so it is the natural candidate for that check.

None of this changes a decision, blocks implementation, or requires
reassessment. All four are one-line additions in the plan's own established
form.

### Question verdicts for plan code-review-requestor round 2

Q01 through Q04 -- command-syntax ownership, authorized commit testing,
repair-scope test placement, and risk-band router splitting.

Verdict: settled and unchanged across both rounds, as requested. Not reopened;
round 2 touched only the two new questions, their step integration, and the
Step 2 assertion sentence. The reviewer's answers remain A1, B1, C1, and D1.
Q02's seam remains verified against `tools/git_batch_commit_git.py`, and D1
remains the correct reading of a 650 ceiling that the plan's own checkpoints
enforce.

Q05 -- What exact command syntax carries the implementation step?

Verdict: settled. The reviewer's answer is E1. The description is accurate about
what `render_command` emits today and about why Step 3 needs an exact string.
The three options differ in contract rather than in taste: E1 extends the prose
form, E2 mixes launcher flags into host skill prose, and E3 changes what the
document token means. E1's con is honest that specialized parsers must recognize
a positional phrase, and that cost is worth paying for the property Step 3
depends on, namely that the ordinary command stays a byte-identical prefix so
compatibility is directly assertable. E3's con is the decisive one. The literal
form is correctly recorded in Step 3 beside `render_step_command`, so the answer
reaches the step that implements it. Nothing to change.

Q06 -- How does Step 4 produce the code-family answer that simulates the
deferred reviewer?

Verdict: settled. The reviewer's answer is F2. The description states the
mechanism correctly: `specification_context` hardcodes the specification family
and derives the type token from the document prefix, so a plan yields a
specification `plan` identity while `publish-answer` validates against the live
code identity. F1's con is right that a repeated envelope contract drifts
silently, which is the failure mode a builder exists to prevent. F3's con
correctly names the scope violation rather than treating early work as merely
premature. F2's con is honest that the helper must track shared envelope
changes, and that is the right cost, because one tracked definition beats many
untracked copies. The builder is named in both Step 4's files list and its
behavior section. Nothing to change.

Step 2 assertion rule -- resolved.

The added sentence sits directly after the three assertion bullets, so it
governs all of them, and it states both halves of the intent: a wording change
must not fail the suite and a rule change must. Nothing to change.

Missing questions: none. Two rounds have settled command-syntax ownership and
its literal form, the commit-continuation test seam, repair-scope test
placement, risk-band splitting policy, and the code-family answer source. No
further implementation choice is open, and none of the six questions is
redundant or reaches into feature or design scope.

Remaining items are not questions. Three new Python modules lack a line-budget
checkpoint and one newly fixed contract lacks its grep check. Both follow
directly from the plan's own conventions and are supplied as covered wording.

### Convergence evidence for plan code-review-requestor round 2

Covered wording: This recommendation covers four one-line additions. Apply them during
consolidation; none needs another review round.

First, add the two missing Step 3 line-budget checkpoint entries. In the Step 3
addendums list, after the `test_prompt_workflow_skill_rendering.py` entry, add:

- `test_prompt_workflow_code_review_tdd.py`: baseline 0; below-550 safe; ceiling
  650; advisory final count 260-380.
- `test_implement_step_integration_tdd.py`: baseline 0; below-550 safe; ceiling
  650; advisory final count 120-200.

Second, add the missing Step 4 checkpoint. In the Step 4 addendums list, before
the two acceptance test entries, add:

- `code_answer_builder.py`: baseline 0; below-550 safe; ceiling 650; advisory
  final count 150-260.

Set that band deliberately wider than a first guess. The direct analogue in the
sibling effort, `tests/unit/tools/test_spec_reviewer_acceptance/fixtures.py`,
finished at 288 lines against a 120-220 advisory band, so a shared acceptance
fixture module is the file most likely to overrun. A band that anticipates that
is more useful than one the step immediately exceeds.

Third, add the missing Step 3 contract check. In the Step 3 completion criteria,
after the existing thin-integration grep, add:

- `rg --line-number " step " tools/prompt_workflow_render.py tests/unit/tools/test_prompt_workflow_skill/test_prompt_workflow_skill_rendering.py` finds the literal step-token contract in both the renderer and its test.

This mirrors how Steps 1, 2, and 4 each pin their newly introduced contract, and
it covers the plan's most byte-sensitive new surface, which is also the only one
a human reads directly from a copied command.

No other edit is covered by this recommendation, and none is needed. Do not
change any question, option, recommendation, answer, step structure, existing
checkpoint, or validation section.

Convergence rationale: Every implementation-level decision is settled, and the two gaps that blocked
round 1 are verified closed rather than reported closed.

The plan can now be implemented end to end. Step 3 has the exact expected string
its rendering test requires, recorded literally beside `render_step_command`
with the strict-prefix property that makes byte-compatibility directly
assertable. Step 4 has a named owner for the code-family answers its scenarios
depend on, which no existing renderer can produce. Those were the two things
missing last round, and both were fixed in full, including the second half of
each change that carries the answer into its step.

The six questions cover the complete implementation decision surface: which step
owns the command extension, what that command literally looks like, how
authorized commit continuation is tested without touching the developer
repository, where repair-scope assessment is proved, whether a risk-band router
must be split first, and where valid code-family test answers come from. No
further question is open.

The plan's factual base was checked directly rather than assumed. All ten
baseline line counts are exact. `render_command` emits only the document form.
`_implementation_command` exists and derives the next uncommitted step. The
commit mechanics sit behind a real subprocess boundary, which is what makes
Q02's seam a seam. `specification_context` hardcodes the specification family,
which is what makes Q06 necessary. Each of those is load-bearing for an answer,
and each holds.

What remains is four one-line additions in the plan's own established form:
three line-budget checkpoints for new Python modules and one grep check for the
contract Q05 fixed. They change no decision and block no work. The hard 650
ceiling already applies to all three modules through shared checklist item 7, so
the missing checkpoints remove an early warning rather than an enforcement, and
the missing grep duplicates a property the Step 3 test bullet already requires.
Spending another exchange cycle to add four lines would be the mechanical round
this plan's own step design avoids.

This recommendation is advisory. It does not authorize consolidation, and the
human retains the choice between consolidating and another round.

### Writer instructions for plan code-review-requestor round 2

No further review round is required. Proceed to consolidation for this plan,
applying the four covered additions.

Do not reopen Q01 through Q06. Do not change any step's analysis, files,
tests-first bullets, classes-and-behavior section, split guidance, or existing
line-budget entries. Do not change the confirmed technical facts, whose ten
baseline counts were verified exact this round, and do not change the validation
plan, which this review did not assess.

The four covered additions are all insertions: two Step 3 checkpoint entries,
one Step 4 checkpoint entry, and one Step 3 completion-criteria grep. Add them
without renumbering or rewording anything around them.

Do not change the feature request, the design, or the umbrella draft. The
umbrella row for this item belongs to the later implementation check.

Present this recommendation to the human with the identity summary and your own
assessment. The choices are `Consolidate` and `Revise and review again`. This
recommendation is advisory and does not authorize consolidation; only the human
selection does.

### Final reviewer decision for plan code-review-requestor round 2

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-2 -->

## Round 2 by human

- Recorded: 2026-08-12T20:38:38+02:00
- Exchange: specification/plan/v0.11.0/code-review-requestor
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-review-requestor.md
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->
