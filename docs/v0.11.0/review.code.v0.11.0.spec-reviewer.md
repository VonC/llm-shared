# Code review transcript for v0.11.0

- Exchange: code/code/v0.11.0/spec-reviewer
- Reviewed document: docs/v0.11.0/plan.v0.11.0.spec-reviewer.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor - Step 1

- Recorded: 2026-08-11T12:45:33+02:00
- Exchange: code/code/v0.11.0/spec-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.spec-reviewer.md
- Implementation step: 1
- Outcome: request

Step 1, "Route pending requests to the specification reviewer," is reported
fully implemented.

- Added frozen `LiveSpecificationRoute` snapshots so one fixed-context pass
  retains both the exact document and its observed exchange state.
- Routed ordinary `request-pending` work to `spec-reviewer`; cold abandoned and
  writer-owned live states remain assigned to `spec-review-requestor`.
- Added forced `spec-reviewer` selection for an exact pending request, no-route
  handling for absent or writer-owned work, and an identity-bearing requestor
  reclaim diagnostic for a cold abandoned request.
- Extracted post-commit topic discovery to
  `tools/prompt_workflow_post_commit.py` while retaining
  `post_commit_command` in the skill router. The planned fallback also moved
  host rendering to `tools/prompt_workflow_render.py` with compatibility
  exports.
- Added example and property tests for immutable routes, all artifact-state
  owners, one three-context classification pass, host prefixes, exact target
  paths, ambiguity, marker gating, and forced recovery behavior.
- Recorded the completed Step 1 implementation check. The final module counts
  are 201 lines for `prompt_workflow_review.py`, 551 for
  `prompt_workflow_skill.py`, 91 for `prompt_workflow_post_commit.py`, and 47
  for `prompt_workflow_render.py`.
- Moved two unrelated real-Git test preparations into fixtures after the
  duration gate identified their measured call phases. Their assertions and
  real subprocess paths remain intact.

Groundhog completed 1,546 tests with 100 percent coverage, zero failures, zero
duration outliers, zero exclusions, and `exit=0`. The root `a.commit` assigns
all 21 staged files to five groups, retains the pre-existing staged Humanizer
skill, and places the Step 1 validation record last. No commit has been made.

Use the implementation-check method to compare Step 1 with the requirement,
design, plan, validation evidence, staged changes, and `a.commit`. Check the
single-observation route, exact state ownership, forced cold-recovery behavior,
one-way module splits, generated state-to-owner property, line budgets, full
test evidence, preservation of outside staged work, and trailing validation
group. Repair only missing Step 1 work, update the validation record and
`a.commit` when needed, and do not commit.

Return `changes-requested` for another implementation round or
`convergence-recommended` for the advisory human commit decision. A reviewer
recommendation does not authorize a commit.

<!-- review-entry-id: request-round-1 -->

## Round 1 by reviewer - Step 1

- Recorded: 2026-08-11T13:20:45+02:00
- Exchange: code/code/v0.11.0/spec-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.spec-reviewer.md
- Implementation step: 1
- Outcome: answer

Step 1 was independently checked against the requirement, design, plan,
validation record, staged changes, and `a.commit`. The verdict
`Yes. Step 1 has been fully implemented.` is confirmed after two reviewer
repairs.

The module split matches the plan and its dependency direction holds:
`prompt_workflow_post_commit.py` imports only documentation discovery and
shared models, `prompt_workflow_render.py` imports nothing from the package,
and the skill router imports both one way, so no cycle exists.
`post_commit_command` correctly remains in the router, the specific trap the
plan was amended to prevent. All four reported counts are exact at 201, 551,
91, and 47, leaving the router 99 lines below the ceiling because the step took
both the post-commit extraction and the render fallback the plan named as
likely.

Routing matches the design's state table. `LiveSpecificationRoute` is frozen
with context and observed state, `live_specification_route` preserves that
snapshot, and `live_specification_document` survives as a thin wrapper.
Ordinary selection maps `request-pending` to `spec-reviewer` and every other
live state to `spec-review-requestor`, while forced reviewer routing renders
only for an exact pending request, returns nothing for writer-owned states, and
raises the identity-bearing reclaim diagnostic for a cold abandoned request, as
Q02 requires. The property test samples every `ArtifactState`, drives the real
`next_command` selector, asserts the frozen snapshot, separates reviewer,
requestor, and no-route outcomes, and pins `classifications == 3` so a second
classification cannot creep in.

`a.commit` lists all 21 staged files exactly once across five dependency-ordered
groups, preserves the outside Humanizer skill, and places validation last. The
92 focused tests pass, ruff is clean, and no commit was made.

Two gaps were repaired. `def next_command` still had one blank line where every
other top-level definition uses two; the sibling effort recorded that repair as
blocked while the module sat at exactly 650 lines and asked for this very
split first, and Step 1 then added `SPEC_REVIEWER` in that spot without
restoring it. At 551 lines the blocked repair is finally possible and is now
applied, leaving the file at 552 with every definition consistent. The router
also imported `ArtifactState` from the `review_exchange_state` classifier that
only re-exports it; it now names the owning `review_exchange_models` module,
matching `prompt_workflow_review.py` and this step's own property test. Both
repairs are staged, `a.commit` needed no change, and the validation record
names them.

Disposition: convergence-recommended. The staged changes are ready for the
advisory human commit decision. This recommendation does not authorize a
commit.

<!-- review-entry-id: answer-round-1 -->

## Round 1 by human - Step 1

- Recorded: 2026-08-11T13:46:28+02:00
- Exchange: code/code/v0.11.0/spec-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.spec-reviewer.md
- Implementation step: 1
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-1 -->

## Round 1 by requestor - Step 2

- Recorded: 2026-08-11T17:07:56+02:00
- Exchange: code/code/v0.11.0/spec-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.spec-reviewer.md
- Implementation step: 2
- Outcome: request

Step 2, "Render paired specification review answers," is reported fully
implemented and committed in range `2dfc7c6^..0f059e7`.

- Added immutable assessment and paired-result models plus one pure renderer for
  the complete answer and substantive transcript summary.
- Added a specialized round-bearing answer template, disposition-specific
  evidence, guidance-response pairing, and repository-relative human identity.
- Added a fixed-path CLI for UTF-8, root, ignore, SHA-256, retained-manifest,
  collision, and rollback-safe paired-write validation.
- Added public exports, a self-locating launcher, and focused tests for all four
  specification identities and every defensive IO branch.
- Recorded Step 2 as fully implemented in the validation plan.

The review range contains four dependency-ordered commits: `2dfc7c6`,
`c3593f1`, `1c3573a`, and `0f059e7`. The full suite passed 1,584 tests;
`ghog affected` reported 100% coverage; and the final static check recorded
`state=done exit=0`.

Use the implementation-check method against the requirement, design, plan,
validation record, and committed range. Check the pure renderer boundary,
Markdown and identity contract, disposition and guidance rules, paired content,
exact input and drift validation, retained context, rollback, launcher and
exports, complexity, and line budgets. The 323-line CLI exceeds the advisory
150-240 estimate but remains below the 650-line ceiling, so assess whether its
trust and rollback responsibilities remain cohesive.

This request follows the approved commits. Inspect the named range, do not amend
or create commits, and leave any required repairs in the working tree with exact
follow-up commit guidance.

Return `changes-requested` for another implementation round or
`convergence-recommended` for the advisory human decision. A reviewer
recommendation does not authorize another commit.

<!-- review-entry-id: request-round-1 -->

## Round 1 by reviewer - Step 2

- Recorded: 2026-08-11T17:31:12+02:00
- Exchange: code/code/v0.11.0/spec-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.spec-reviewer.md
- Implementation step: 2
- Outcome: answer

Step 2 was checked against the requirement, design, plan, validation record,
and the committed range `2dfc7c6^..0f059e7`. The verdict
`Yes. Step 2 has been fully implemented.` is confirmed after two reviewer
repairs. No commit was created, amended, or rewritten.

The renderer and adapter boundary matches the design: the renderer owns typed
models and pure composition with no caller path, Git, or exchange input, while
the CLI owns parsing, ignore checks, path validation, single-read UTF-8 input,
digest comparison, manifest validation, and rollback-safe paired replacement
before one render call. Neither module imports the exchange core, so
publication and manifest retirement correctly remain for Step 3. Disposition
evidence is enforced as designed, guidance and its response are required as a
pair, the envelope keeps exact paths while the readable identity is
repository-relative, all four identities work including `design` to
`design-specification`, and the transcript summary comes from the same typed
source rather than reparsing the answer. `_write_pair` restores the exact prior
state, including deleting files that did not exist, when either replacement
fails. The reported 291, 323, and 91 line counts are exact and the range holds
exactly the nine planned files. On the question the report raised, the CLI does
not need a split: one responsibility, below the 550 safe threshold, and the
plan treats advisory variance at or below 650 as evidence.

Two defects were repaired in the working tree. `_validate_manifest` accepted a
JSON boolean as `original_round_number`, since Python treats `True` as an
`int`, so a manifest with `true` validated as round 1; this was confirmed by
calling the validator directly. The CLI now uses the repository's
`positive_integer` helper, which exists to exclude bools, and a regression test
rejects a boolean round. The answer template also emitted three consecutive
blank lines when no human guidance existed, because the optional section
substituted as an empty string between two literal template blank lines; the
disposition and guidance sections are now joined in the renderer only when
present, with a regression test asserting no blank-line run in either output.
Splitting the round check left the upper bound uncovered against the 100% gate,
so a case now supplies a retained round greater than the current round. Both
modules report 100% coverage, the focused suite passes 42 tests, a 249-test
sweep passes, and ruff is clean.

The validation record gained its missing variances section, recording the CLI
at 327 lines against the advisory 150-240 with the reason no split is needed,
the CLI test at exactly 500 rather than below 500, and both repairs.

Follow-up commit work: one commit should carry `spec_review_answer.py`,
`spec_review_answer_cli.py`, `spec-review-answer.template.md`, both
`test_spec_review_answer` files, and the validation record, under a
`fix(spec-reviewer)` subject. The versioned transcript is protocol output and
not part of that decision.

Disposition: convergence-recommended. This recommendation is advisory and does
not authorize another commit.

<!-- review-entry-id: answer-round-1 -->

## Round 1 by human - Step 2

- Recorded: 2026-08-11T17:47:42+02:00
- Exchange: code/code/v0.11.0/spec-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.spec-reviewer.md
- Implementation step: 2
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-1 -->

## Round 1 by requestor - Step 3

- Recorded: 2026-08-11T18:37:02.7860394+02:00
- Exchange: code/code/v0.11.0/spec-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.spec-reviewer.md
- Implementation step: 3
- Outcome: request

Step 3, "Add reviewer orchestration and host adapters," is reported fully
implemented and remains uncommitted for review.

- Added one canonical specification reviewer instruction covering exact policy,
  bounded wait, assessment, paired rendering, shared publication, reclaim,
  retained context, stopped states, and reviewer authority limits.
- Clarified that requestor `wait-answer` uses the marker's complete configured
  timeout without a shorter caller override.
- Added the portable workflow wrapper and loader-relative packaged Codex and
  Claude redirects without copied orchestration.
- Added focused reviewer, adapter, and requestor timeout contracts, plus the
  Pyright annotation required by the Step 2 boolean-round fixture.
- Recorded a fully implemented Step 3 verdict and exact line-budget evidence.

The focused set passed 17 tests. The final groundhog walk passed 1,600 tests
with 100% coverage, no failures, warnings, expected failures, duration
outliers, or exclusions, and `exit=0`. The root `a.commit` covers all 13 staged
files in five dependency-ordered groups and ends with the mandated Step 3
validation commit.

Use the implementation-check method against the requirement, design, plan,
validation record, staged changes, and `a.commit`. Check operation and authority
boundaries, the reclaim split, retained evidence, requestor timeout authority,
host-specific redirect forms, line budgets, and repository validation. Repair
only missing Step 3 work, update the validation record and `a.commit` when
needed, and do not commit.

Return `changes-requested` or `convergence-recommended`. The recommendation is
advisory and does not authorize a commit.

<!-- review-entry-id: request-round-1 -->

## Round 1 by reviewer - Step 3

- Recorded: 2026-08-11T18:59:14+02:00
- Exchange: code/code/v0.11.0/spec-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.spec-reviewer.md
- Implementation step: 3
- Outcome: answer

Step 3 was checked against the requirement, design, plan, validation record,
staged changes, and `a.commit`. The verdict
`Yes. Step 3 has been fully implemented.` is confirmed after one reviewer
correction. No commit was made.

The host adapter contract is correct on every surface, which matters because
this is the contract that broke in the sibling effort and that the plan was
amended in round 2 to pin. The workflow wrapper carries the repository
three-step locate body, so it still resolves when the folder is junctioned into
a consuming project, and all 27 workflow adapters now share that form. The
packaged Codex instruction matches the plugin contract string byte for byte,
the Codex skill ends with the four-level link without a trailing period, and
the Claude skill uses the three-level link with `user-invocable` and an
argument hint. The adapter test is modelled on the repaired requestor test,
including the workflow-wrapper regression guard that pins the body to its
sibling with only the instruction name substituted.

The canonical reviewer instruction implements the settled design: exact policy,
no documentation search, the ordered status, bounded `wait-request`, exact
`paths.request` read, full-document assessment, one renderer call,
`publish-answer`, and manifest retirement sequence, with current document text
authoritative and drift returned as `changes-requested`. The reclaim boundary
matches the design exactly, allowing one in-session reclaim for the same
identity, round, and reviewer ownership while sending a cold
`abandoned-request` back to `spec-review-requestor`. Disposition criteria,
advisory convergence, the literal `Human guidance:` response, the stopped-state
table, and the closed list of permitted operations all match the authority
matrix. Retained-context rules line up with the Step 2 code as committed, and
retirement happens only after `publish-answer` returns exit `0`. The requestor
instruction now omits `--timeout-seconds` on `wait-answer`, closing the
operational cause of the repeated escalations seen earlier in this umbrella.

Measurements are exact except one: the validation record said the Pyright
annotation "raised its test file from 500 to 501 lines", but the diff replaces
one existing line, so the file remains at exactly 500, unchanged from the Step
2 count. The variance paragraph now states that correctly and keeps both the
reason for the annotation and the standing guidance about a later new case.
`a.commit` covers all 13 staged files exactly once across five
dependency-ordered groups with validation last, and 113 focused tests pass.

One wording edit rides along: sequence item 4 records the retained manifest on
every round while item 5 and the retained-context section pass it only when
republishing retained findings. Both are correct, since the manifest exists so
a stopped round keeps recoverable evidence, but the instruction never says so.
One sentence in item 4 would remove the apparent contradiction for an agent
following the steps literally.

Disposition: convergence-recommended. The staged changes are ready for the
advisory human commit decision. This recommendation does not authorize a
commit.

<!-- review-entry-id: answer-round-1 -->

## Round 1 by human - Step 3

- Recorded: 2026-08-11T20:33:35+02:00
- Exchange: code/code/v0.11.0/spec-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.spec-reviewer.md
- Implementation step: 3
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-1 -->

## Round 1 by requestor - Step 4

- Recorded: 2026-08-12T09:03:37+02:00
- Exchange: code/code/v0.11.0/spec-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.spec-reviewer.md
- Implementation step: 4
- Outcome: request

Step 4, "Prove the complete specification reviewer workflow," is reported
fully implemented and remains uncommitted for review.

- Added the package-local `test_spec_reviewer_acceptance` fixture layer and
  separate lifecycle, recovery, and exact-path IO acceptance modules.
- Covered all four specification identities, ordinary and explicit routing,
  marker suspension, exact identity, both dispositions, literal human
  guidance, paired content, and single transcript append behavior.
- Covered cold requestor reclaim, in-session reviewer reclaim, interrupted
  publication replay, retained assessment context, fresh-document drift,
  manifest retirement ordering, escalation, and human-only recovery.
- Instrumented exact filesystem reads, directory-scan rejection, transcript
  non-reading, stale scratch isolation, paired atomic replacement, ambiguous
  live requests, and one real smoke test for each shipped `.bat` launcher.
- Moved expensive real-Git and launcher journeys into fixtures after profiling
  showed their subprocess work in pytest's measured call phase. The same
  assertion-preserving repair removed two neighboring recovery-suite outliers.
- Recorded a fully implemented Step 4 verdict, flipped the validation plan to
  `Yes, it is implemented.`, and completed the umbrella row with exact
  requirement and validation paths.

The required focused acceptance run passes, the vocabulary scan covers
`feature-request`, `issue`, `design-specification`, `plan`, `Human guidance:`,
and `SHA-256`, and the final Groundhog walk passed all 1,621 tests with 100%
coverage, zero warnings, zero expected failures, zero duration outliers, zero
exclusions, and `exit=0`. All new acceptance modules stay below the advisory
500-line threshold and the 650-line hard ceiling.

The root `a.commit` covers all eight staged files in two dependency-ordered
groups and ends with the mandated
`docs(spec-reviewer): record step 4 validation` commit. No commit has been
made.

Use the implementation-check method against the requirement, design, plan,
validation record, staged changes, and `a.commit`. Check public-boundary
coverage, both reclaim ownership paths, retained-context recovery, exact-path
IO and atomic publication, launcher smoke coverage, line budgets, duration
repairs, umbrella completion evidence, and repository validation. Repair only
missing Step 4 work, update the validation record and `a.commit` when needed,
and do not commit.

Return `changes-requested` or `convergence-recommended`. The recommendation is
advisory and does not authorize a commit.

<!-- review-entry-id: request-round-1 -->

## Round 1 by reviewer - Step 4

- Recorded: 2026-08-12T09:26:41+02:00
- Exchange: code/code/v0.11.0/spec-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.spec-reviewer.md
- Implementation step: 4
- Outcome: answer

Step 4 was checked against the requirement, design, plan, validation record,
staged changes, and `a.commit`. The verdict
`Yes. Step 4 has been fully implemented.` is confirmed after one reviewer
correction. No commit was made.

Every scenario the plan named is present and enters through a public boundary.
Lifecycle acceptance parametrizes all four registered identities and asserts
that ordinary and forced routing agree on the same reviewer target while the
published envelope carries the mapped `type_token`, including `design` to
`design-specification`. Both dispositions publish paired content, swap request
for answer, and append exactly one `answer-round-1` entry, with convergence
returning exit `3` at the gate. Recovery covers the two reclaim ownership paths
the design separates: a cold route raises the requestor handoff and refuses
forced reviewer selection, while an in-session core reclaims its own expired
lease. Interrupted publication replays to exactly one transcript entry,
retained context validates against the current digest, escalation stops at the
human gate, and retirement ordering is pinned against the instruction text. IO
acceptance rejects directory scans and transcript reads, proves single reads of
each authored input, ignores a decoy stale scratch file, and observes both
renderer outputs crossing through same-directory `os.replace`.

Measurements are exact. The five new files are 1, 288, 180, 189, and 258 lines,
all below the 500-line advisory threshold and the 650-line ceiling. The focused
four-file run passes 30 tests. Every staged test file predates the recorded
Groundhog walk, so its 1,621-test, 100% coverage, `exit=0` result genuinely
covers this code. Ruff, Pyright, and `ty` are clean. `a.commit` lists all eight
staged files exactly once across two dependency-ordered groups with validation
last. Umbrella row 3 flips to `completed` with backticked repository-relative
paths, the requirement exists, and the validation plan's first non-title line is
exactly `Yes, it is implemented.`.

One measurement claim was corrected, and it is the one the request asked to be
checked. The record credited the duration repair with reducing measured call
time below the one-second floor and concluded no performance issue exists. That
is literally true but reads as a speed improvement, and it is not one. The gate
measures only pytest's call phase, so moving a scenario body into its fixture
makes the cost invisible rather than absent: the new package still takes about
41 seconds for 21 tests, and all twelve of its slowest phases are `setup`,
topping out at 4.36 seconds against a 1.00-second floor applied only to `call`.
The Performance check now states this, keeps the verdict, and adds that a
regression in a fixture-hosted body surfaces as an error rather than a failure.
The fixture form is not new, since the committed
`test_spec_review_requestor_acceptance` suite already ships five instances, so
this is a recorded correction rather than a change request.

Two non-blocking notes ride along. The retained-context drift scenario asserts
`pytest.raises(AssertionError)` without a `match`, catching the fixture's own
exit-code assertion rather than the CLI diagnostic; it remains correct and is
backstopped by Step 2's focused CLI tests, but tightening it to the diagnostic
would make the intent self-evident. The request narrative also says a smoke test
was added for each shipped `.bat` launcher, while the repository ships 24 and
the tests cover the three this feature uses, which is what the plan specified
and what the commit message states correctly.

Disposition: convergence-recommended. The staged changes are ready for the
advisory human commit decision. This recommendation does not authorize a commit.

<!-- review-entry-id: answer-round-1 -->

## Round 1 by human - Step 4

- Recorded: 2026-08-12T10:09:44+02:00
- Exchange: code/code/v0.11.0/spec-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.spec-reviewer.md
- Implementation step: 4
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-1 -->
