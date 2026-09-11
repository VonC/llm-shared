# Code review transcript for v0.11.0

- Exchange: code/code/v0.11.0/code-review-requestor
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-review-requestor.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor - Step 1

- Recorded: 2026-08-13T09:59:21+02:00
- Exchange: code/code/v0.11.0/code-review-requestor
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-review-requestor.md
- Implementation step: 1
- Outcome: request

### Review identity for step 1 code-review-requestor round 1

Umbrella draft: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-review-requestor.md
Implementation step: 1
Review round: 1

### Requestor assessment for step 1 code-review-requestor round 1

Step 1 is fully implemented against the plan and validation checklist. The
paired renderer carries exact code-family plan, implementation-step, round,
umbrella, assessment, implementation report, change summary, writer response,
and optional guidance identity. The command boundary rejects unsafe or
inconsistent caller-owned paths before producing either output.

Groundhog completed with static checks, affected tests, all 1,641 tests, 100%
coverage, and duration gates passing.

### Implementation report for step 1 code-review-requestor round 1

Implemented `CodeReviewRoundInput`, `CodeReviewRequestRender`, pure paired
rendering, the canonical request template, and a self-locating batch launcher.
The CLI reads each ignored UTF-8 input once and writes the two validated outputs
once. Focused tests cover exact identity, policy instructions, optional
guidance, malformed inputs, unsafe paths, Git failures, missing templates, and
shared-envelope mismatches.

During the required Groundhog loop, two pre-existing excluded tests exceeded
their accepted duration. Their real Git setup was moved into fixtures, and the
main-guard test now isolates dispatch with an already-tested plan. Their
measured calls fell from 8.98s and 7.23s to below 0.005s and 0.01s without
removing assertions.

### Change summary for step 1 code-review-requestor round 1

Staged paths for Step 1:

- `bin/code_review_request.bat`
- `templates/code-review-request.template.md`
- `tools/code_review_request.py`
- `tests/unit/tools/test_code_review_request/__init__.py`
- `tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py`
- `tests/unit/tools/prepare_release/test_prepare_release_plan.py`
- `tests/unit/tools/prepare_release/test_prepare_release_plan_git.py`
- `docs/v0.11.0/plan.v0.11.0.code-review-requestor.validation.md`

`a.commit` contains three groups: the duration-test repair, paired code-review
rendering, and the required trailing Step 1 validation commit.

### Writer response for step 1 code-review-requestor round 1

Writer response: This is Round 1, so there is no earlier reviewer feedback. Review the exact
Step 1 scope, the staged implementation and tests, the validation evidence,
and whether `a.commit` accurately groups all staged paths.

### Reviewer focus for step 1 code-review-requestor round 1

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-round-1 -->

## Round 1 by human - Step 1 - escalation

- Recorded: 2026-08-13T10:40:30+02:00
- Exchange: code/code/v0.11.0/code-review-requestor
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-review-requestor.md
- Implementation step: 1
- Outcome: escalation

exchange was abandoned while waiting for reviewer

<!-- review-entry-id: escalation-round-1 -->

## Round 1 by reviewer - Step 1

- Recorded: 2026-08-13T10:50:14+02:00
- Exchange: code/code/v0.11.0/code-review-requestor
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-review-requestor.md
- Implementation step: 1
- Outcome: answer

Step 1 was checked against the requirement, design, plan step, validation
record, staged changes, and `a.commit`. The verdict
`Yes. Step 1 has been fully implemented.` is confirmed after one polishing-only
reviewer repair. No commit was made.

The staged set is exactly the five files Step 1 names plus the two duration
repairs and the validation record, eight in total, and `a.commit` assigns all
eight to three dependency-ordered groups with the validation commit last and each
path appearing once.

The renderer matches its declared surface. `CodeReviewRoundInput` rejects a
non-code family, a nonpositive round, an invalid timestamp, and empty authored
fields; `CodeReviewRequestRender` rejects an incomplete pair; and
`code_review_context` derives fixed `code` identity from the exact plan filename
and a non-empty step. Rendering is pure and reparses its own output, failing
closed when the round-trip envelope differs or `## JSON` is missing, which is
stronger than the step required. Filesystem, Git, and argument handling stay at
the command boundary and the launcher carries no logic.

Measurements were taken rather than accepted: 20 focused tests pass,
`tools/code_review_request.py` reports 100% coverage across 175 statements with
none missed, and pyright, ruff, and `ty` are clean.

Both duration repairs were checked for assertion loss. The conflicting-merge
repair is exact, with `objects_before` still captured before the preview and all
four assertions unchanged. The main-guard repair additionally substitutes
`build_release_plan` with a canned plan, which the report and docstring disclose;
it remains sound because the test targets the `__main__` dispatch boundary, the
real planner path is covered by the CLI tests in the same module, coverage stays
at 100 percent, and the stub mirrors the production keyword-only signature so a
signature change raises `TypeError` instead of diverging silently.

One repair was made, to
`docs/v0.11.0/plan.v0.11.0.code-review-requestor.validation.md`. The Performance
check compared the two line counts only with the 650-line ceiling, while both
exceed their step advisory bands: the renderer is 382 against 280-380 and its
tests are 437 against 300-430. The shared execution checklist requires recording
advisory variance, so the paragraph now names both bands, states the overruns are
small and far below the ceiling, and records why no split is required. The repair
is documentation only, so it is polishing-only and does not force another round.
`a.commit` needed no amendment.

Two items are returned as feedback rather than edited, because both would be
substantive changes outside Step 1. Paired output writing is sequential rather
than atomic, so an IO error on the second write could leave a partial pair; every
validation failure is already proven to leave no pair, and the sibling
`spec_review_answer_cli` guards the same boundary with a temporary file,
`os.replace`, and rollback, which would make the two renderers consistent. The
Step 1 completion grep also targets the template for identity literals that live
only in the module, so later contract checks should target composed output or
only the file holding the literals.

Disposition: commit-ready. The staged changes are ready for the advisory human
commit decision. This recommendation does not authorize a commit.

<!-- review-entry-id: answer-round-1 -->

## Round 1 by human - Step 1 - human-confirmation

- Recorded: 2026-08-13T11:11:20+02:00
- Exchange: code/code/v0.11.0/code-review-requestor
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-review-requestor.md
- Implementation step: 1
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-1 -->

## Round 1 by requestor - Step 2

- Recorded: 2026-08-13T11:53:21+02:00
- Exchange: code/code/v0.11.0/code-review-requestor
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-review-requestor.md
- Implementation step: 2
- Outcome: request

### Review identity for step 2 code-review-requestor round 1

Umbrella draft: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-review-requestor.md
Implementation step: 2
Review round: 1

### Requestor assessment for step 2 code-review-requestor round 1

## Requestor assessment

Yes. Step 2 has been fully implemented.

The canonical specialized requestor instruction and all four host adapters are
present. The instruction fixes the code-family policy, delegates shared state
transitions, assesses staged repairs and commit grouping, and preserves durable
human authorization. Thirteen focused contract tests pass. The full repository
walk reports 100% coverage with zero failures, warnings, outliers, or
exclusions.

Please verify the exact Step 2 scope, instruction contract, adapter structure,
test sufficiency, validation record, and proposed commit grouping.

### Implementation report for step 2 code-review-requestor round 1

## Implementation report

- Added `instructions/code-review-requestor.md` as the canonical specialized
  role over `instructions/review-requestor.md`.
- Registered the fixed `code`, `commit-ready`, `Rework and review again`, and
  `Commit` policy with exact plan-step identity.
- Covered disabled, idle, active, pending, abandoned, convergence,
  authorization-pending, and escalation states.
- Defined paired request rendering, exact answer-path reading, staged-repair
  evidence, explicit repair-reversal disagreement, `a.commit` assessment, and
  substantive-change handling.
- Added direct workflow, Codex instruction, Codex skill, and Claude skill
  adapters.
- Added focused token/order and adapter-structure tests.
- Recorded the Step 2 implementation check in the validation plan.

Validation evidence:

- 13 focused Step 2 tests pass.
- `ghog day` completed with `exit=0`.
- Full suite: 100% coverage; 0 failures, warnings, outliers, or exclusions.
- No architecture, performance, coverage, or feature-integrity issue was found.

### Change summary for step 2 code-review-requestor round 1

## Staged changes and proposed commits

Nine Step 2 paths are staged:

- `instructions/code-review-requestor.md`
- `.agent/workflows/code-review-requestor.md`
- `.agents/llm-shared/instructions/code-review-requestor.md`
- `.agents/llm-shared/skills/code-review-requestor/SKILL.md`
- `.claude/skills/code-review-requestor/SKILL.md`
- `tests/unit/tools/test_code_review_requestor_instruction/__init__.py`
- `tests/unit/tools/test_code_review_requestor_instruction/test_code_review_requestor_instruction_tdd.py`
- `tests/unit/tools/test_instruction_structure/test_code_review_requestor_adapters_tdd.py`
- `docs/v0.11.0/plan.v0.11.0.code-review-requestor.validation.md`

`a.commit` assigns every path once in dependency order:

1. `feat(code-review): add specialized requestor` — canonical role, adapters,
   and contract tests.
2. `docs(code-review-requestor): record step 2 validation` — validation record.

No Step 2 commit has been made.

### Writer response for step 2 code-review-requestor round 1

Writer response: ## Writer response

This is Step 2 round 1. There is no earlier Step 2 reviewer feedback or
disagreement to address.

Step 1 was reviewed, authorized by the human, committed through the canonical
batch path, and completed before this step began.

### Reviewer focus for step 2 code-review-requestor round 1

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-round-1 -->

## Round 1 by reviewer - Step 2

- Recorded: 2026-08-13T13:41:48+02:00
- Exchange: code/code/v0.11.0/code-review-requestor
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-review-requestor.md
- Implementation step: 2
- Outcome: answer

Step 2 was checked against the requirement, design, plan step, validation
record, staged changes, and `a.commit`. The verdict
`Yes. Step 2 has been fully implemented.` is confirmed after two polishing-only
reviewer repairs. No commit was made.

All eight files Step 2 names are present, and `a.commit` assigns all ten staged
paths across two dependency-ordered groups with the validation group last and
each path appearing exactly once.

The canonical instruction registers the fixed `code` and `commit-ready` policy
with both human labels, delegates every durable transition to the shared
requestor, and covers all eleven observable states. It carries the two decisions
the design added late: a substantive repair arriving with a commit-ready
recommendation retains the legitimate gate and recommends `Rework and review
again` rather than starting a round the requestor cannot start, and a requestor
reversal is recorded as explicit disagreement rather than hidden behind a
generic changed-work signal. It also forbids consuming a convergence answer.

The adapters are guarded rather than merely written. The workflow body is pinned
to the shared `review-requestor.md` wrapper with only the instruction name
substituted, which is the regression the sibling effort repaired twice; the
packaged Codex instruction and four-level skill link are pinned exactly; and
every adapter is proven to contain no policy or lifecycle token.

Measurements were taken rather than accepted: 71 focused tests pass, pyright,
ruff, and `ty` are clean, the mandated policy grep finds sixteen matching lines,
and both test modules are exactly the 151 and 107 lines claimed. The record's
explanation that those counts sit below their 260-380 and 120-190 advisory bands
because assertions are concise rather than absent holds: seven contracts cover
policy, the ordered delegation chain, all states and prohibitions, the four-part
evidence order, reversal handling, the substantive categories with the
convergence gate, and the commit replay order.

Two repairs were made to `instructions/code-review-requestor.md`. The third item
of the four-part evidence list had merged the evidence item with its supporting
rule and no longer parsed, leaving an agent unable to tell whether item 3 was the
staged diff or a staging obligation; it now names the staged diff and both
obligations while preserving the ordering and every pinned token. The `a.commit`
assessment paragraph also had a 157-character first line in a file that wraps
near 79, and is rewrapped with its contiguous contract token intact. Both change
wording and formatting only, altering no rule, test, acceptance behavior, or
commit grouping, so they are polishing-only. `a.commit` needed no amendment.

Two items are returned as feedback. The staged set includes the versioned
transcript and `a.commit` commits it with the validation group, which captures
only the requestor entry because the answer and human confirmation are appended
afterwards; deciding once whether the transcript is committed per round or per
completed step would avoid a trailing documentation commit after every step. Two
adapters also differ from their siblings by a single trailing blank line, which
breaks nothing and is noted only because the forms are otherwise identical.

Disposition: commit-ready. The staged changes are ready for the advisory human
commit decision. This recommendation does not authorize a commit.

<!-- review-entry-id: answer-round-1 -->

## Round 1 by human - Step 2

- Recorded: 2026-08-13T14:07:52+02:00
- Exchange: code/code/v0.11.0/code-review-requestor
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-review-requestor.md
- Implementation step: 2
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-1 -->

## Round 1 by requestor - Step 3

- Recorded: 2026-08-13T17:58:41+02:00
- Exchange: code/code/v0.11.0/code-review-requestor
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-review-requestor.md
- Implementation step: 3
- Outcome: request

### Review identity for step 3 code-review-requestor round 1

Umbrella draft: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-review-requestor.md
Implementation step: 3
Review round: 1

### Requestor assessment for step 3 code-review-requestor round 1

Yes. Step 3 has been fully implemented.

The exact-path router, step-aware command, durable live-state precedence, and
authorized batch-commit continuation match the plan. Groundhog finished with
1,671 passing tests, 100% coverage, no warnings, xfails, or duration outliers;
the static-check phase was clean. The implementation-check found no
architecture, performance, coverage, or feature-integrity issue.

### Implementation report for step 3 code-review-requestor round 1

Step 3 adds `tools/prompt_workflow_code_review.py` as the bounded adapter over
the shared exchange core. It derives one plan-step identity, checks only fixed
artifact paths, preserves marker-off routing, resumes durable live state, and
fails closed on identity or step disagreement.

The shared renderer now provides a literal space followed by the `step <id>` suffix without
changing ordinary rendering. The skill router and CLI expose the specialized
requestor and `code-review-commit`; the latter delegates exactly once to the
existing strict batch-commit command and completes the exchange only after a
successful return. The two workflow instructions record post-grouping marker
sampling and the no-second-choice authorized continuation.

Focused tests cover cold, live, inconsistent, marker-off, mismatched-step,
rendering, CLI, subprocess success, and replay failure paths. Groundhog-required
fixture repairs move real Git setup outside measured call phases without
removing assertions or changing production behavior.

### Change summary for step 3 code-review-requestor round 1

The staged tree contains 19 paths in three dependency-ordered `a.commit`
groups:

1. `test(groundhog): shorten duration-gated setup` — seven test and fixture
   files that retain the same assertions while moving setup out of measured
   call phases.
2. `feat(code-review): route commit gate requests` — four production workflow
   files, two instructions, and five focused test files for the Step 3 surface.
3. `docs(code-review-requestor): record step 3 validation` — the validation
   record, last.

Every staged path appears exactly once. `a.commit` passes
`bin/gcba.bat -n a.commit`.

### Writer response for step 3 code-review-requestor round 1

Writer response: This is round 1, so there is no earlier reviewer feedback or repair reversal.
The writer requests review of the complete staged Step 3 result, including the
Groundhog duration repairs that were required to reach `state=done exit=0`.

### Reviewer focus for step 3 code-review-requestor round 1

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-round-1 -->

## Round 1 by reviewer - Step 3

- Recorded: 2026-08-13T19:11:07+02:00
- Exchange: code/code/v0.11.0/code-review-requestor
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-review-requestor.md
- Implementation step: 3
- Outcome: answer

Step 3 was checked against the requirement, design, plan step, validation
record, staged changes, and `a.commit`. The step is substantially correct, and
one substantive defect was found and repaired, so another round is required. No
commit was made.

All four mandated completion greps pass. The step-token criterion added during
plan review earns its place: `render_step_command` is literally
`f"{render_command(...)} step {implementation_step}"`, and its test asserts
`step_aware == f"{ordinary} step 4A"`, which is exactly the byte-identical
strict-prefix property the design settled. Every line budget holds, with the
router at 246 against 220-340 and both risk-band routers inside their bands
without a split, which is the settled splitting answer applied literally.
`a.commit` covers all twenty staged paths across three dependency-ordered groups,
each exactly once, validation last.

The seven duration repairs were checked across the whole group rather than
sampled: ninety-one insertions, thirty-three deletions, and not one removed
assertion. Skipping Git initialization for the escalation acceptance case is
sound, because that test drives `start` and `escalate` without ever calling
`activate`, and only `activate` requires a repository.

One substantive repair was made. `run_batch_commit` located its launcher as
`cwd / "bin" / "gcba.bat"`, deriving it from the reviewed project root. That was
the only `bin/` path built anywhere in `tools/`, and the one place it should not
be, because `gcba.bat` ships with llm-shared rather than with the project under
review. The repository explicitly supports llm-shared as the root, under the
root, or outside it, which is what `instruction_prefix` exists to resolve and
what the workflow adapter's three-step locate body assumes. In a sibling-clone or
submodule deployment the previous code would look for the launcher under the
consuming project, failing after the human had already chosen `Commit`, and
because a failed owning action retains its authorization for replay, every retry
would fail identically. The launcher now resolves through `llm_shared_dir()`
while the working directory stays the reviewed project, so behavior is unchanged
where llm-shared is the root. The test previously pinned the temporary project
path, encoding the assumption; it now pins the llm-shared launcher, asserts it
exists, and asserts it is not under the temporary root. The module stays at 100%
coverage, 91 focused tests pass, and pyright, ruff, and `ty` are clean. The
validation record's two affected counts were corrected from 240 to 246 and from
381 to 383 with the advisory variance restated.

That repair changes production code and a test, so it is substantive, and a
substantive repair cannot validly finish the workflow in the same round. That is
the only reason for `changes-requested`; no other Step 3 work is missing.
`a.commit` needed no amendment.

Two items are returned as feedback. The request's change summary states nineteen
staged paths and describes Group 3 as the validation record alone, while twenty
are staged and Group 3 also holds the versioned transcript; `a.commit` itself is
correct, so only the next summary needs to match. `resolve_code_review_route`
also builds the plan-step context twice and reads the child draft each time;
both are pure and constant-cost, but a single resolution reused by the probe and
the observation would match the plan's stated resolve-once wording.

Disposition: changes-requested. This answer does not authorize a commit.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor - Step 3

- Recorded: 2026-08-13T19:26:19+02:00
- Exchange: code/code/v0.11.0/code-review-requestor
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-review-requestor.md
- Implementation step: 3
- Outcome: request

### Review identity for step 3 code-review-requestor round 2

Umbrella draft: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-review-requestor.md
Implementation step: 3
Review round: 2

### Requestor assessment for step 3 code-review-requestor round 2

Yes. Step 3 has been fully implemented after accepting the round-1 repair.

The batch launcher now comes from `steps.llm_shared_dir()` while `cwd` remains
the reviewed project. This is the correct boundary for root, submodule, and
sibling deployments and prevents an authorized replay from repeatedly looking
under the consuming project. The focused Step 3 Groundhog run is green, the
validation record names the boundary, and no other implementation gap remains.

### Implementation report for step 3 code-review-requestor round 2

Step 3 adds `tools/prompt_workflow_code_review.py` as the bounded adapter over
the shared exchange core. It derives one plan-step identity, checks only fixed
artifact paths, preserves marker-off routing, resumes durable live state, and
fails closed on identity or step disagreement.

The shared renderer now provides a literal space followed by the `step <id>` suffix without
changing ordinary rendering. The skill router and CLI expose the specialized
requestor and `code-review-commit`; the latter delegates exactly once to the
existing strict batch-commit command and completes the exchange only after a
successful return. The two workflow instructions record post-grouping marker
sampling and the no-second-choice authorized continuation.

Focused tests cover cold, live, inconsistent, marker-off, mismatched-step,
rendering, CLI, subprocess success, and replay failure paths. Groundhog-required
fixture repairs move real Git setup outside measured call phases without
removing assertions or changing production behavior.

Round 1 repaired `run_batch_commit` so the installed `gcba.bat` is located from
llm-shared rather than the reviewed root. Its test asserts the launcher exists,
is not under the temporary consuming root, and still runs with that consuming
root as `cwd`. The router is 246 lines and its focused test is 383 lines; the
recorded advisory variance remains below the hard ceiling.

### Change summary for step 3 code-review-requestor round 2

The staged tree contains 20 paths in three dependency-ordered `a.commit`
groups:

1. `test(groundhog): shorten duration-gated setup` — seven test and fixture
   files that retain the same assertions while moving setup out of measured
   call phases.
2. `feat(code-review): route commit gate requests` — four production workflow
   files, two instructions, and five focused test files for the Step 3 surface.
3. `docs(code-review-requestor): record step 3 validation` — the validation
   record and versioned review transcript, last.

Every staged path appears exactly once. The three repaired paths remain in their
existing groups, so `a.commit` is unchanged and passes
`bin/gcba.bat -n a.commit`.

### Writer response for step 3 code-review-requestor round 2

Writer response: Round 1's launcher-resolution repair is accepted without disagreement. The
writer verified that `gcba.bat` belongs to llm-shared while the reviewed project
must remain the subprocess working directory, retained the reviewer edits, and
added the deployment boundary to the validation record. The focused Step 3
Groundhog run passes. `a.commit` needed no amendment.

The replacement summary also corrects the earlier narrative from 19 to 20
staged paths and names both files in Group 3. No repair was reversed.

### Reviewer focus for step 3 code-review-requestor round 2

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer - Step 3

- Recorded: 2026-08-13T19:46:30+02:00
- Exchange: code/code/v0.11.0/code-review-requestor
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-review-requestor.md
- Implementation step: 3
- Outcome: answer

The single outstanding item from round 1 was confirming the substantive
launcher-resolution repair. It is confirmed, and the verdict
`Yes. Step 3 has been fully implemented.` now holds with no reviewer repair in
this round. No commit was made.

The repair survived intact rather than being reworked or quietly reverted.
`run_batch_commit` still resolves the launcher through `steps.llm_shared_dir()`
while `cwd` remains the reviewed project, and the test still pins the llm-shared
launcher, asserts the file exists, and asserts the resolved path is not under the
temporary project root. That last assertion is what prevents the original
project-root assumption from returning unnoticed.

The validation record now names the deployment boundary in its architecture
section and names it correctly: `gcba.bat` resolves from
`steps.llm_shared_dir()` while the reviewed project remains the working
directory, so root, submodule, and sibling llm-shared deployments execute the
same installed launcher against the correct staged tree.

Every measurement in the record is exact against the current tree: router 246,
renderer 57, skill router 583, CLI 579, routing test 383, integration test 48.
The two counts the repair shifted were carried through and the advisory-band
variance is restated at three lines rather than one. Both risk-band routers
remain inside their mandatory ceilings without a split.

`a.commit` is unchanged and still covers all twenty staged paths across three
dependency-ordered groups, each exactly once, with validation last. The request
narrative now states twenty staged paths and names both Group 3 files, resolving
the first feedback item.

Ninety-one focused tests pass across the router, skill, and instruction
integration suites; `tools/prompt_workflow_code_review.py` reports 100% coverage
at ninety-two statements with none missed; pyright, ruff, and `ty` are clean.

The second feedback item was correctly left alone. `resolve_code_review_route`
still builds its plan-step context twice, which was raised as an observation
rather than a requested change; acting on it would have been a substantive
production edit forcing a third round over an advisory point. The observation
stands for a later step if the resolve-once wording is ever tightened.

This round contains no reviewer edit of any kind, which is what allows it to
close. Disposition: commit-ready. The staged changes are ready for the advisory
human commit decision. This recommendation does not authorize a commit.

<!-- review-entry-id: answer-round-2 -->

## Round 2 by human - Step 3

- Recorded: 2026-08-13T19:57:06+02:00
- Exchange: code/code/v0.11.0/code-review-requestor
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-review-requestor.md
- Implementation step: 3
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->

## Round 1 by requestor - Step 4

- Recorded: 2026-08-13T20:59:01+02:00
- Exchange: code/code/v0.11.0/code-review-requestor
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-review-requestor.md
- Implementation step: 4
- Outcome: request

### Review identity for step 4 code-review-requestor round 1

Umbrella draft: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-review-requestor.md
Implementation step: 4
Review round: 1

### Requestor assessment for step 4 code-review-requestor round 1

Yes. Step 4 has been fully implemented.

Ten repository-level acceptance tests prove the complete opt-in requestor
lifecycle, bounded repair and disagreement paths, exact IO rules, human
override, durable Commit replay, single execution, and cleanup. Groundhog
finished 1,681 tests at 100% coverage with no failures, warnings, xfails, or
duration outliers. The final implementation-check found no architecture,
performance, coverage, or feature-integrity issue.

### Implementation report for step 4 code-review-requestor round 1

Step 4 adds a test-local `CodeAnswer` builder that emits strict code-family
answers for the exact plan, step, round, umbrella, disposition, repaired paths,
and recommendation while leaving the deferred reviewer renderer out of scope.

The lifecycle suite composes marker routing, exact step rendering, public
request rendering, shared answer publication, staged-path inventory, a.commit
assessment, changes-requested continuation, explicit disagreement escalation,
polishing and substantive convergence, human override, reclaim, durable Commit
authorization, later-session replay, one batch call, and cleanup.

The IO suite rejects plan, step, round, and umbrella mismatch; tracked scratch
inputs; unrelated staged paths as identity; duplicate live exchange; scans;
transcript reads; and reclaim after escalation. Duration-only fixture changes
move real Git setup outside measured call phases without removing assertions.

### Change summary for step 4 code-review-requestor round 1

The staged tree contains seven paths in two dependency-ordered `a.commit`
groups:

1. `test(code-review): prove requestor lifecycle` — the four new acceptance
   package files plus one duration fixture repair.
2. `docs(code-review-requestor): record step 4 validation` — the completed
   validation plan and umbrella evidence row, last.

Every staged path appears exactly once. `a.commit` passes
`bin/gcba.bat -n a.commit`.

### Writer response for step 4 code-review-requestor round 1

Writer response: This is Step 4 round 1, so there is no earlier Step 4 reviewer feedback or
repair reversal. The writer requests review of the final acceptance slice, its
duration-gate repair, the completed effort validation, and the umbrella status
transition. No commit has been made.

### Reviewer focus for step 4 code-review-requestor round 1

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-round-1 -->

## Round 1 by reviewer - Step 4

- Recorded: 2026-08-13T21:10:45+02:00
- Exchange: code/code/v0.11.0/code-review-requestor
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-review-requestor.md
- Implementation step: 4
- Outcome: answer

Step 4 was checked against the requirement, design, plan step, validation
record, umbrella draft, staged changes, and `a.commit`. The verdict
`Yes. Step 4 has been fully implemented.` is confirmed after one polishing-only
reviewer repair. No commit was made.

The ten acceptance tests cover every surface Step 4 named. Six lifecycle
journeys carry marker-absent and marker-present routing with exact step
transport, substantive repair with disagreement and override, second recorded
reversal, substantive commit-ready held at the gate, authorized replay with
cleanup, and expired-request reclaim. Four IO journeys carry identity mismatch,
tracked scratch rejection, scan and transcript-read rejection with unrelated
staging, and duplicate live exchange with escalation staying stopped.

Two prove decisions this umbrella settled late rather than merely exercising
code. The second-reversal test makes the disagreement bound executable, with the
first recorded reversal consuming the single clarification round and the second
escalating. The substantive commit-ready test proves that such an answer stays
at the legitimate gate instead of starting a round the requestor cannot start.

The code-answer builder implements its settled answer correctly, composing the
strict envelope through the shared `Envelope` and `render_envelope_markdown`
rather than reimplementing it, and adding no production surface belonging to the
deferred reviewer.

The duration repair preserves every assertion despite showing two removed
`pytest.raises` lines: both were inline `match=` forms converted to captured
`.value` comparisons, so the exception type is still asserted in the fixture and
both exact messages are still asserted in the test body.

Umbrella completion is properly evidenced. Row 4 flips to `completed` with
backticked repository-relative requirement and validation paths, the requirement
exists, the validation plan opens with exactly `Yes, it is implemented.`, all
four step analyses read `Yes`, no stale `Missing work` section remains, and every
other row is untouched. `a.commit` covers all eight staged paths across two
dependency-ordered groups, each once, with validation and umbrella evidence last.

One repair was made to the validation record. The Performance check reported the
lifecycle suite at 427 lines and the IO suite at 252; both files are 426 and 254,
verified three ways including the `(Get-Content).Count` form the plan prescribes,
so this was not a methodology difference. Neither correction changes a
conclusion, since both suites stay inside their 400-540 and 170-260 advisory
bands. The repair is documentation only and therefore polishing-only.
`a.commit` needed no amendment.

One item is returned as feedback. The change summary states seven staged paths
and describes Group 2 as two files, while eight are staged and Group 2 holds
three because the versioned transcript is grouped with them. `a.commit` itself is
correct. This is the same miscount Step 3 round 1 carried, which suggests the
sentence is written from the step summary rather than derived from `a.commit`.

The builder's 76 lines fall below the 150-260 band this reviewer supplied during
plan review. That is not omitted work: the builder delegates envelope
construction to the shared models instead of restating the contract, so the band
was too wide, and the record explains the variance correctly.

Disposition: commit-ready. This completes the four-step effort. The staged
changes are ready for the advisory human commit decision. This recommendation
does not authorize a commit.

<!-- review-entry-id: answer-round-1 -->

## Round 1 by human - Step 4

- Recorded: 2026-08-13T21:18:05+02:00
- Exchange: code/code/v0.11.0/code-review-requestor
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-review-requestor.md
- Implementation step: 4
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-1 -->
