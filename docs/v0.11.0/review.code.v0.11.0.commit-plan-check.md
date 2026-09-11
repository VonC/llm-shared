# Code review transcript for v0.11.0

- Exchange: code/code/v0.11.0/commit-plan-check
- Reviewed document: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor - Step 1

- Recorded: 2026-08-26T13:00:18+02:00
- Exchange: code/code/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
- Implementation step: 1
- Outcome: request

### Review identity for step 1 commit-plan-check (round 1)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
Implementation step: 1
Review round: 1

### Code review evidence for step 1 commit-plan-check (round 1)

request_index_tree: 25d13fc7fc2b8f46a86f86d22c89ee82b2598cc5
resolved_validation_set:

- ghog day (sources: project)
- ghog single tests/unit/tools/test_commit_plan_support/test_commit_plan_support_tdd.py tests/unit/tools/test_git_batch_commit_workflow_process.py (sources: plan)
- rg -n staged_paths tools/commit_plan_support.py tools/git_batch_commit_workflow.py tests/unit/tools/test_commit_plan_support tests/unit/tools/test_git_batch_commit_workflow_process.py (sources: plan)
- git diff --cached --check (sources: request)

### Requestor assessment for step 1 commit-plan-check (round 1)

Step 1 is fully implemented against the settled plan.

The implementation uses one public staged-path inventory function, preserves
the batch workflow's compatibility helper as a thin delegate, and leaves the
validator and commit execution unchanged. The support boundary performs one Git
call and one linear NUL decode with no per-path filesystem probes.

Focused tests cover the exact Git arguments, repository root, command options,
path order, whitespace, deletions, both rename sides, and empty inventory. The
final groundhog walk reported
`fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0`.

No DDD-Hexagonal boundary smell, performance issue, line-budget breach, unit
coverage gap, or impaired feature behavior was found.

### Implementation report for step 1 commit-plan-check (round 1)

The new `tools/commit_plan_support.py` module owns
`staged_paths(root)`. It invokes
`git diff --cached --name-only --no-renames -z` through the existing
cross-platform Git adapter and returns ordered nonempty NUL-delimited paths.

`tools/git_batch_commit_workflow.py` retains `_staged_paths(root)` as a private
compatibility seam and delegates directly to the new public function. Its
existing validation call still passes that tuple to `validate_commit_plan`
before any mutation.

The new focused test leaf proves the subprocess and decoding contract. The
existing workflow test now proves delegation and unchanged validator wiring.
All implementation and test files remain below their advisory budgets.

### Change summary for step 1 commit-plan-check (round 1)

The staged tree contains ten paths in four proposed commit groups:

1. Repair the persisted specification-review transcript's ordered-list spacing.
2. Stabilize verification-gate tests by naming a threshold, removing duplicated
   legacy assertions, and eliminating one redundant lifecycle classification.
3. Add the shared staged inventory function, batch delegate, and focused tests.
4. Record the required Step 1 validation evidence as the final commit.

The root `a.commit` contains these subjects in dependency order:

- `docs(commit-plan): fix review list formatting`
- `test(workflow): stabilize verification gates`
- `feat(commit-plan): share staged path inventory`
- `docs(commit-plan-check): record step 1 validation`

### Writer response for step 1 commit-plan-check (round 1)

Writer response: This is the initial implementation review round, so there is no earlier reviewer
feedback or disagreement to assess.

The writer requests review of the exact Step 1 scope, all staged paths, the
implementation-check result, and the proposed four-group `a.commit` plan.

### Reviewer focus for step 1 commit-plan-check (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-1-round-1 -->

## Round 1 by reviewer - Step 1

- Recorded: 2026-08-26T13:15:50+02:00
- Exchange: code/code/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
- Implementation step: 1
- Outcome: answer

### Assessed index identity for step 1 commit-plan-check (exchange 1) (round 1)

Baseline index tree: 25d13fc7fc2b8f46a86f86d22c89ee82b2598cc5

Assessed index tree: 25d13fc7fc2b8f46a86f86d22c89ee82b2598cc5

### Implementation check for step 1 commit-plan-check (exchange 1) (round 1)

Result: Yes. Step 1 has been fully implemented. I reached that verdict independently rather than by accepting the requestor's assessment, and it matches theirs.

The shared boundary is real and singular. `tools/commit_plan_support.py` owns `staged_paths(root)`, which runs the exact tuple `("diff", "--cached", "--name-only", "--no-renames", "-z")` through the existing cross-platform Git adapter with `GitCommandOptions(capture_output=True, encoding="utf-8")` and returns the ordered nonempty NUL-decoded tuple. The decisive parity evidence is negative rather than positive: `--no-renames` and `-z` no longer appear anywhere in `tools/git_batch_commit_workflow.py`, so no second Git invocation survived the extraction.

The compatibility seam behaves as Q02 settled it. `git_batch_commit_workflow._staged_paths(root)` is now a one-line delegate to `commit_plan_support.staged_paths(root)` with no inventory policy of its own, and `_validate_commit_plan_for_root` still passes that tuple to the unchanged public validator before any mutation. Because the delegate resolves the module attribute at call time, both existing monkeypatch seams still work, and I confirmed both survive at `tests/unit/tools/test_git_batch_commit_workflow_process.py:248` and `:298`.

The import removal is safe. `run_cross_platform_git_command` and `GitCommandOptions` have no remaining use in the workflow module, so dropping that import leaves no dangling reference.

Test coverage matches the contract the plan required. The new focused leaf pins the exact argument tuple, the repository root passed as `cwd`, the capture and encoding options, order and whitespace preservation including a leading space, a trailing space and an embedded newline, deletion membership, both `--no-renames` rename sides kept separate, and empty-segment handling that cannot manufacture phantom paths. The rewritten workflow test proves the delegate forwards the exact root and returns the public result unchanged, and the argument assertions it gave up were not lost but relocated to the module that now owns them.

Every line budget holds, and the extraction paid for itself. `tools/commit_plan_support.py` is 38 lines against an 80-line advisory, `tools/git_batch_commit_workflow.py` fell from 484 to 481 against a 490 advisory, the new test leaf is 4 and 135 lines against 5 and 180, and the updated workflow test fell from 353 to 347 against 370. Nothing approaches the 550 risk band or the 650 ceiling.

Architecture is clean in the direction that matters. The neutral support module depends only on the Git command adapter, the committing workflow depends on the support boundary, and no reverse dependency exists. Parser, validator, renderer, and commit-execution responsibilities stayed out of the support module, which is what keeps the Step 2 checker able to consume it without importing commit execution.

Performance is one Git subprocess call and one linear split-and-filter pass. There is no per-path filesystem probe, no nested membership scan, no added sort, and no quadratic or log-linear work introduced.

No existing behavior is impaired. The validator receives the same ordered tuple by the same call path, rename and deletion semantics are unchanged because the Git arguments are byte-identical, and commit execution was not touched.

Validation plan effects: I made no change to the validation plan. The writer had already recorded the Step 1 rows, and I found them correct, so there was nothing for reviewer mode to write.

The recorded rows conform to the template contract. The first sentence under `### Analysis of Step 1 implementation state` is exactly `Yes. Step 1 has been fully implemented.` with no prefix and no restatement of the step title, followed by a blank line and then a prose summary. Because the verdict is Yes, no `### Missing work for Step 1` section is required and none is present.

The document-level status line is correctly left at `No, it is not implemented.` Steps 2, 3 and 4 still read `Not started`, so the flip to `Yes, it is implemented.` would have been wrong here. I re-read all four `### Analysis of Step N implementation state` sections to confirm that.

The per-section content is accurate against the code rather than merely plausible. The architecture, performance, unit coverage and feature integrity sections each end with the required explicit yes-or-no sentence, and each of those four verdicts matches what I found independently.

No umbrella row was completed, and reviewer mode correctly suppressed that section: Step 1 is not the final step, and the umbrella digest is unchanged.

### Pre-repair mandatory checks and coverage for step 1 commit-plan-check (exchange 1) (round 1)

Coverage and correctness reproduce. Gate stability does not.

A plain `ghog day` does not re-prove the recorded result. It short-circuits with `No Python file changed since the last green ghog day walk - nothing to do (use --force to walk anyway)` and reports `cov=skipped outliers=skipped excluded=skipped exit=0`. Accepting that as coverage evidence would have been accepting a cached verdict, so I forced a real walk instead.

I ran `ghog day --force` twice, and the two runs disagree:

- Run one: `ghog full done fail=0 warn=0 xfail=0 cov=100 outliers=1 excluded=0 exit=8`.
- Run two: `ghog full done fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0`, reporting `Objective reached`.

The correctness and coverage axes are stable and match the requestor's claim: `fail=0`, `warn=0`, `xfail=0`, and `cov=100` on both runs across 2,010 tests. `ghog single` on the two Step 1 test files is also green with nothing failing in focus and no focus-versus-suite interaction.

The duration axis is not stable, and the flapping call is the one this commit set out to stabilize. Both runs name `tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_lifecycle_answers_tdd.py::test_reviewer_wait_spans_answer_pending_until_the_replacement_request` as the slowest call in the suite. Run one measured it at `0.55s` against the `0.50s` floor, which produced the single outlier and step exit `8`. Run two measured the same call at `0.41s`, under the floor, which produced `outliers=0` and exit `0`.

That is the flapping case the tool explicitly refuses to accept as fixed by re-measurement: "a call only slightly above the floor will flap on the next jitter, so do not just re-measure - shorten each call listed above the floor until it lands well below the floor with margin to spare". The measured spread of `0.41s` to `0.55s` around a `0.50s` floor is exactly that condition.

This matters for attribution rather than blame. Group 2 of the staged set modifies this very test, and its commit body states the intent: the test "repeated a persisted-state read during its fake wait, leaving it vulnerable to duration-floor jitter". The change is a genuine improvement, since it removes one `core.classify()` persisted-state read per poll and halves the poll count by moving `poll_interval` from `1` to `2`. The clock is a fake with no real sleep, so the remaining cost is real protocol artifact IO from `publish_answer`, `consume_answer`, `continue_round`, and `_start_and_request`. The improvement was not enough to clear the floor with margin, so the stated goal of that group is not yet met.

The requestor's recorded line is therefore reproducible but not dependable. `outliers=0 excluded=0 exit=0` is a real result that I obtained on run two, and it is recorded in the validation plan as settled repository-gate evidence. It is one sample of a two-sided distribution that straddles the floor.

The pre-existing accepted exclusion is healthy and unrelated: `tests/unit/tools/markdown_check/test_launcher/test_launcher_tdd.py::test_root_launcher_runs_without_an_activated_project_environment` is recorded at `0.85s` and currently measures `0.72s` and `0.76s`, comfortably inside its accepted budget.

I also ran the repository Markdown gate. It reports no finding for the plan, the validation plan, or either review transcript, so MD024 and MD025 hold across the appended rounds.

### Resolved validation set and sources for step 1 commit-plan-check (exchange 1) (round 1)

The request resolved four commands. I ran the union of that set and the current plan-derived resolver set, so five distinct commands were executed.

- `ghog day` — source `project`. The repository gate.
- `ghog single tests/unit/tools/test_commit_plan_support/test_commit_plan_support_tdd.py tests/unit/tools/test_git_batch_commit_workflow_process.py` — source `plan`. Targeted Step 1 tests.
- `rg -n staged_paths tools/commit_plan_support.py tools/git_batch_commit_workflow.py tests/unit/tools/test_commit_plan_support tests/unit/tools/test_git_batch_commit_workflow_process.py` — source `request`, narrowed relative to the plan.
- `rg -n "staged_paths|--no-renames|-z|validate_commit_plan" tools/commit_plan_support.py tools/git_batch_commit_workflow.py tests/unit/tools/test_commit_plan_support tests/unit/tools/test_git_batch_commit_workflow_process.py` — source `plan`, the full pattern at `docs/v0.11.0/plan.v0.11.0.commit-plan-check.md:324`, added by the union.
- `git diff --cached --check` — source `request`.

Every command ran. None was unavailable, so there is no missing mandatory evidence on the availability axis.

`git diff --cached --check` returned exit `0` with no whitespace or conflict-marker finding across the ten staged paths.

Both `rg` commands pass and together supply the parity evidence. The narrowed request form returns 25 matching lines. The full plan pattern additionally proves the negative that matters: `--no-renames` and `-z` now appear only in `tools/commit_plan_support.py` at lines 20 and 21 and in the focused test's argument assertion, and appear nowhere in `tools/git_batch_commit_workflow.py`, while `validate_commit_plan` is still reached through `_staged_paths(root)` at `tools/git_batch_commit_workflow.py:201`. One Git inventory implementation exists, and delegation is covered by tests.

`ghog single` on the two Step 1 test files reports `fail=0 warn=0 xfail=0 exit=0` with nothing still failing in focus and nothing passing in focus while failing in the full suite.

`ghog day` needed care and is reported in the pre-repair validation evidence rather than here, because a plain invocation does not re-prove the recorded result.

### Resolver drift and direction for step 1 commit-plan-check (exchange 1) (round 1)

One drift was found, and it narrows the request relative to the plan.

The plan's Step 1 completion criteria at `docs/v0.11.0/plan.v0.11.0.commit-plan-check.md:324` specify:

```text
rg -n "staged_paths|--no-renames|-z|validate_commit_plan" tools/commit_plan_support.py tools/git_batch_commit_workflow.py tests/unit/tools/test_commit_plan_support tests/unit/tools/test_git_batch_commit_workflow_process.py
```

The request's resolved validation set carries the narrowed form instead:

```text
rg -n staged_paths tools/commit_plan_support.py tools/git_batch_commit_workflow.py tests/unit/tools/test_commit_plan_support tests/unit/tools/test_git_batch_commit_workflow_process.py
```

Direction: the request command is a strict subset of the plan command. It drops the `--no-renames`, `-z`, and `validate_commit_plan` alternatives, which are exactly the terms that prove the Git inventory was not duplicated and that the validator still receives the shared result. The narrowed form alone could pass while a second Git invocation survived in the workflow module.

I ran the union rather than either alone. Both commands were executed and both pass. The full plan pattern supplies the evidence the narrowed form would have missed: `--no-renames` and `-z` now appear only in `tools/commit_plan_support.py` at lines 20 and 21 and in the focused test assertion, and no longer appear anywhere in `tools/git_batch_commit_workflow.py`. That is the decisive parity evidence for Step 1.

No drift was found in the other three commands. This drift is reported, not repaired; the resolved set belongs to the requestor.

### Repository state around validation for step 1 commit-plan-check (exchange 1) (round 1)

My assessment produced no repository side effect. I made no repair, so the only writes were ignored root `a.*` reviewer evidence files.

Index identity held throughout. The request-time `request_index_tree` is `25d13fc7fc2b8f46a86f86d22c89ee82b2598cc5`, and `capture-index-tree` returned the identical value both before assessment and after the validation runs, so no early rejection was triggered and no staged change occurred during review.

The umbrella is untouched. `umbrella-digest capture` and `umbrella-digest compare` on `docs/v0.11.0/draft.v0.11.0.review-mode.md` both return `020d1d67f9a3dca50a2651e6dd7b6717b3f1a7ef5521c5eaf4a27de6e2c3b79c` with `changed: false`, so no boundary violation exists.

The validation-state comparison is clean. Using the same ordered ten-path set before and after, `validation-state compare` returns `acceptable: true` with empty `tracked_paths`, `untracked_paths`, and `ignored_paths`. No tracked validation side effect appeared, so nothing had to be left unstaged and unreverted.

One expected and acceptable difference sits outside that set. Running the full gate refreshed ignored coverage and test-selection artifacts such as `.coverage`, `.testmondata`, `a.ghog.log`, and `a.ghog.outliers`. These are ignored validation artifacts, which the contract explicitly accepts, and none is tracked or staged.

The only untracked path in the working tree is `docs/v0.11.0/review.code.v0.11.0.commit-plan-check.md`, this exchange's own transcript, created by the protocol rather than by my assessment.

### Repair inventory for step 1 commit-plan-check (exchange 1) (round 1)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 1 commit-plan-check (exchange 1) (round 1)

`a.commit` is mechanically accurate. I verified it rather than reading it, by running the repository's own public validator over the exact index: `parse_clipboard_content(content, interactive=False)`, then `commit_plan_support.staged_paths(root)`, then `validate_commit_plan(blocks, staged_paths)`.

The result is ten staged paths, four ordered groups, `valid=True`, and zero diagnostics. Every staged path appears exactly once and no planned path is absent from the index.

Group membership matches the staged set exactly:

- Group 1 `docs(commit-plan): fix review list formatting` carries the one spec-review transcript path.
- Group 2 `test(workflow): stabilize verification gates` carries the three verification-gate test paths.
- Group 3 `feat(commit-plan): share staged path inventory` carries the two production paths and the three Step 1 test paths.
- Group 4 `docs(commit-plan-check): record step 1 validation` carries the validation plan.

Ordering is least to most dependent and is correct: the transcript repair and the gate maintenance are independent, the feature follows, and the validation record depends on the feature it documents. Every subject is a conventional commit with an accurate scope.

One observation that needs no change now. The untracked `docs/v0.11.0/review.code.v0.11.0.commit-plan-check.md` is this exchange's own transcript and is deliberately absent from `a.commit`, since the round is still open and the transcript keeps growing. It must be included when the commit is finally taken, which the `git add -A` grouping pass at the commit gate will pick up.

I did not amend `a.commit`. Membership, ordering, scope, and subjects are all already accurate, so an amendment would have been a substantive change to commit grouping with no defect to correct.

### Findings and boundaries for step 1 commit-plan-check (exchange 1) (round 1)

Unresolved findings:

- Paired review renderers inline caller-authored Markdown directly after a `Label:` prefix and a following space on the same line, so any authored block that begins with a list item, heading, fence, or blockquote is structurally broken in both the published artifact and the versioned transcript. Verified call sites: `tools/spec_review_answer.py:188` (`Requested changes:` plus a following space), `tools/spec_review_request.py:177` and `:189` (`Writer response:` plus a following space), `tools/code_review_request.py:211` and `:223` (`Writer response:` plus a following space), and `tools/code_review_answer.py:335` and `:336` (`Result:` and `Validation plan effects:`, each plus a following space). The correct idiom already exists in the same file at `tools/code_review_answer.py:288`, where `_inventory` emits `f"{label}:\n\n"` before its list.
- This defect produced the exact damage that group 1 of the staged set repairs by hand: the round-one requested-change list in `docs/v0.11.0/review.plan.v0.11.0.commit-plan-check.md` was flattened onto its `Requested changes:` label line. Because the cause is unfixed, every future round whose authored block starts with a list or heading reproduces it and requires another hand edit to a versioned protocol artifact.
- The caller-authored heading contract in `instructions/review-requestor.md` is also unimplemented. That instruction states that generated request sections are level 2 and generated transcript sections are level 3, so caller-authored headings are shifted to level 3 or level 4 and qualified with identity, slug, exchange, and a final `(round N)` suffix. No such shift or qualification occurs: reviewer-authored `##` headings appear verbatim at level 2 inside level-3 sections in `docs/v0.11.0/review.plan.v0.11.0.commit-plan-check.md` at lines 138, 155, 171, 187, 204, 222, 263, 320, 365, 386, 400, 408, 543, 566, 580 and 596. MD024 and MD025 currently pass only because every authored heading text happened to be unique; the outline is already wrong and a future collision would become a transcript defect rather than a caught one.

Boundary-crossing work:

- Repairing the label-inlining defect would touch `tools/spec_review_answer.py`, `tools/spec_review_request.py`, `tools/code_review_request.py`, and `tools/code_review_answer.py`. None is named by Step 1, so I left all four unchanged and report them here rather than editing them.
- `tools/code_review_request.py` is additionally a Step 3 file in this same plan, where the requestor publication gate is added. A renderer fix landed there now would collide with Step 3, so the sequencing belongs to the writer rather than to this step.
- Implementing the caller-authored heading shift and qualification contract would touch the same renderer modules plus the shared section helpers. It is review-mode tooling work outside Step 1 and is reported rather than attempted.
- Groups 1 and 2 of the staged set are outside Step 1's plan file list. I assessed them because they are staged and carried by this commit plan, but I made no change to them. Their presence is legitimate under the grouped-commit rule that stages the whole tree and groups every staged change by its own dependencies.

### Writer instructions for step 1 commit-plan-check (exchange 1) (round 1)

Step 1 itself needs no rework. The implementation, its tests, its budgets, and the `a.commit` grouping are all correct, and I am not asking for a single change to `tools/commit_plan_support.py`, `tools/git_batch_commit_workflow.py`, or either Step 1 test file. Please do not rework them.

The requested changes are these.

Give the flapping test real margin. `tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_lifecycle_answers_tdd.py::test_reviewer_wait_spans_answer_pending_until_the_replacement_request` measured `0.55s` and `0.41s` on two forced walks against a `0.50s` floor, so the gate returns exit `8` on some runs and exit `0` on others. That file is already staged in group 2, and group 2's own commit body names this jitter as the problem it set out to solve, so this is finishing the work that group already claims rather than new scope. Follow `instructions/fix_slow_test.md` and shorten the call until it lands well below the floor with margin, then confirm with `ghog single` on that file followed by a forced `ghog day`. The dominant cost is real protocol artifact IO across `publish_answer`, `consume_answer`, `continue_round`, and `_start_and_request`, not the fake clock, so the reduction has to come from doing less artifact work per poll rather than from tuning `poll_interval` again. If the call proves irreducible under that instruction, the sanctioned alternative is `ghog exclude <node id> <measured seconds>`; do not raise the floor on line 2 of `a.ghog.outliers`.

Correct the recorded gate evidence in the validation plan. `docs/v0.11.0/plan.v0.11.0.commit-plan-check.validation.md` records `fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0` as settled repository-gate evidence for Step 1. That line is one sample from a distribution that straddles the floor, and a plain `ghog day` cannot re-prove it because it short-circuits to `cov=skipped`. Once the test has margin, re-run `ghog day --force` and record the result together with the fact that `--force` is required to reproduce it. If you prefer to keep the current wording, it must at least stop presenting `outliers=0 exit=0` as stable.

Record the renderer defect instead of only repairing its output. Group 1 hand-edits `docs/v0.11.0/review.plan.v0.11.0.commit-plan-check.md`, a versioned protocol artifact, to repair damage the tooling caused and will cause again. The cause is that paired renderers inline caller-authored Markdown directly after a `Label:` prefix and a following space on the same line, at `tools/spec_review_answer.py:188`, `tools/spec_review_request.py:177` and `:189`, `tools/code_review_request.py:211` and `:223`, and `tools/code_review_answer.py:335` and `:336`. The correct idiom already exists in the same file at `tools/code_review_answer.py:288`, where `_inventory` emits `f"{label}:\n\n"` before its list. At minimum, amend group 1's commit body to name that root cause and those call sites so the workaround is greppable in history rather than reading as a one-off formatting nit. Do not fix the renderers inside this step: `tools/code_review_request.py` is a Step 3 file in this same plan and a change there now would collide with the Step 3 publication gate. Decide where that work belongs, given that umbrella rows 9 and 10 are still pending.

Reconcile the resolved validation set with the plan. The request carried `rg -n staged_paths ...`, while the plan's Step 1 completion criteria at `docs/v0.11.0/plan.v0.11.0.commit-plan-check.md:324` specify the wider `rg -n "staged_paths|--no-renames|-z|validate_commit_plan" ...`. The narrowed form drops exactly the terms that prove the Git command was not duplicated. I ran the union and both pass, so nothing is broken, but later rounds should carry the plan's pattern so the parity evidence is not silently weakened.

One optional observation, not a requested change. The caller-authored heading contract in `instructions/review-requestor.md` promises that renderers shift authored headings to level 3 or 4 and qualify them with identity and a `(round N)` suffix. No shift or qualification happens, so authored `##` headings sit at level 2 inside level-3 sections in both transcripts. MD024 and MD025 pass today only because every authored heading text happened to be unique. It belongs with the same tooling decision as the label defect.

### Decision rationale for step 1 commit-plan-check (exchange 1) (round 1)

I am publishing `changes-requested`, and I made no repair of any kind this round.

Five of the six readiness-floor results pass. Identity is exact: the request envelope, human-readable identity, plan, step, round, and exchange occurrence all agree, and the request-time index tree `25d13fc7fc2b8f46a86f86d22c89ee82b2598cc5` still matches the live index, so no early rejection applied. Implementation completeness is a genuine Yes that I derived independently. Staged attribution is clean, with every staged path belonging to a coherent group and no pre-existing unstaged work swept into the index. The `a.commit` grouping is mechanically valid against the exact index, with four groups, ten paths, and zero validator diagnostics. Coverage is `100` and the suite is green on every run I made.

The sixth result, mandatory validation, does not pass stably, and that is the blocking reason. `ghog day --force` returned exit `8` on one run and exit `0` on another, because the suite's slowest call flaps across the duration floor at `0.55s` and `0.41s` against `0.50s`. The repository's own gate therefore does not reliably report its objective as reached. The tool is explicit that re-measuring is not a fix for a call sitting that close to the floor, so I did not treat the green run as the answer. The flapping call is in a file this commit already stages, in the group whose commit body claims to have addressed that exact jitter, so the gap is between that group's stated intent and its measured effect rather than a defect I am importing from elsewhere.

Two verified findings remain unresolved, and the answer model itself refuses to pair them with a commit-ready recommendation. The renderer label-inlining defect is reproducible across seven call sites in four modules, it already damaged a versioned protocol artifact, and group 1 of this commit repairs that damage by hand without recording the cause, so the workaround will be needed again next round. The unimplemented caller-authored heading contract is the same class of defect and currently passes lint only by luck.

I deliberately did not repair any of it. The renderer fix lies outside Step 1 and would touch `tools/code_review_request.py`, which is a Step 3 file in this same plan, so repairing it here would both cross the step boundary and collide with later planned work. Amending group 1's commit body would have been a substantive change to commit grouping, which cannot validly finish the workflow in the same round, so I requested it rather than performing it. Because I made no substantive repair, nothing in this answer invalidates a commit-ready recommendation in the next round.

What I am asking for is proportionate. Step 1's implementation is correct and I explicitly asked that it not be reworked. The blocking item is finishing the stabilization that group 2 already started, in a file already staged, plus correcting one evidence line and recording one root cause. None of it requires reopening a settled requirement, design, or plan decision.

This recommendation is advisory and authorizes nothing. Only the human may choose `Commit` or `Rework and review again`, and a green checker or gate result would not by itself confer commit authority.

### Final reviewer decision for step 1 commit-plan-check (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-1-round-1 -->

## Round 2 by requestor - Step 1

- Recorded: 2026-08-26T13:30:21+02:00
- Exchange: code/code/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
- Implementation step: 1
- Outcome: request

### Review identity for step 1 commit-plan-check (round 2)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
Implementation step: 1
Review round: 2

### Code review evidence for step 1 commit-plan-check (round 2)

request_index_tree: 5d8fde87ef62ef4ffd16d968b45a25a1519cd982
resolved_validation_set:

- ghog day (sources: project)
- ghog single tests/unit/tools/test_commit_plan_support/test_commit_plan_support_tdd.py tests/unit/tools/test_git_batch_commit_workflow_process.py (sources: plan)
- rg -n --regexp=staged_paths --regexp=--no-renames --regexp=-z --regexp=validate_commit_plan tools/commit_plan_support.py tools/git_batch_commit_workflow.py tests/unit/tools/test_commit_plan_support tests/unit/tools/test_git_batch_commit_workflow_process.py (sources: plan)
- ghog day --force (sources: request)
- git diff --cached --check (sources: request)

### Requestor assessment for step 1 commit-plan-check (round 2)

Step 1 remains fully implemented, and every required round-one correction is
now incorporated.

The lifecycle timing repair moves first-round artifact setup into a pytest
fixture while preserving the complete answer-consume-continue-request wait in
the measured call. Re-measurement reports 0.27s in setup and no slow call-phase
entry. The focused groundhog run is green.

A forced `ghog day --force` bypassed the cached no-op and reported
`fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0` across 2,010 tests.
The validation plan now names that forced evidence explicitly.

The commit plan retains accurate membership and order. Group 1 now records the
four deferred renderer call-site families that caused the transcript damage,
and group 2 describes the fixture-based timing repair.

### Implementation report for step 1 commit-plan-check (round 2)

The Step 1 production implementation is unchanged from round 1 because the
reviewer independently found it complete and requested no rework there.

The required timing repair changes only
`test_review_exchange_lifecycle_answers_tdd.py`. A fixture now performs harness
creation, round-one request publication, and answer publication during pytest
setup. The measured call still drives `wait_for_exact` through answer
consumption, continuation, round-two publication, and exact request discovery.

The validation record now states that the green coverage and duration evidence
came from `ghog day --force`. The root commit plan records the deferred renderer
root cause without changing group boundaries or subjects.

### Change summary for step 1 commit-plan-check (round 2)

The staged tree still contains the same ten paths and four groups. Round-one
repairs changed two already-staged paths and the ignored root commit plan:

- Move lifecycle artifact setup to a fixture for duration margin
- Record the forced green groundhog result in the Step 1 validation block
- Name the deferred label-inlining renderer call sites in group 1
- Update group 2 wording to match the fixture-based repair

The final subject remains
`docs(commit-plan-check): record step 1 validation` as required.

### Writer response for step 1 commit-plan-check (round 2)

Writer response: All required round-one feedback was accepted with no disagreement.

The flapping lifecycle call now performs its real protocol artifact setup in a
pytest fixture. The measured call retains every transition and assertion but no
longer reports as a slow call; the only reported duration is 0.27s in setup.
A focused run and a forced full groundhog walk are green, with 100% coverage and
no outlier.

The validation plan explicitly names `ghog day --force`, so the recorded result
cannot be mistaken for the cached no-op. Group 1's body now names
`tools/spec_review_answer.py`, `tools/spec_review_request.py`,
`tools/code_review_request.py`, and `tools/code_review_answer.py` as the deferred
label-inlining root cause. No renderer was changed in Step 1 because that work
belongs to later review-mode planning and would collide with Step 3.

The round-two validation set carries all four parity terms: `staged_paths`,
`--no-renames`, `-z`, and `validate_commit_plan`. The optional authored-heading
finding remains deferred with the related renderer work.

### Reviewer focus for step 1 commit-plan-check (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-1-round-2 -->

## Round 2 by reviewer - Step 1

- Recorded: 2026-08-26T13:40:20+02:00
- Exchange: code/code/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
- Implementation step: 1
- Outcome: answer

### Assessed index identity for step 1 commit-plan-check (exchange 1) (round 2)

Baseline index tree: 5d8fde87ef62ef4ffd16d968b45a25a1519cd982

Assessed index tree: 5d8fde87ef62ef4ffd16d968b45a25a1519cd982

### Implementation check for step 1 commit-plan-check (exchange 1) (round 2)

Result: Yes. Step 1 has been fully implemented. That verdict is unchanged from round one, and I re-derived it rather than carrying it forward on trust.

The Step 1 production work is byte-identical to what I already accepted. `git diff --cached --stat` over the five Step 1 paths reports exactly the same shape as round one, and the line counts are unchanged at 38 for `tools/commit_plan_support.py`, 481 for `tools/git_batch_commit_workflow.py`, 135 for the new focused test, and 347 for the updated workflow test. The requestor honored my request not to rework correct code.

Parity still holds under the widened validation command. `--no-renames` and `-z` appear nowhere in `tools/git_batch_commit_workflow.py`, so no second Git invocation exists, and `validate_commit_plan` is still reached through the delegate. That is the negative evidence the round-one narrowed command would have missed, and the round-two set now proves it directly.

The round-one blocker is genuinely fixed rather than re-measured. The repair moves first-round harness creation, request publication, and answer publication into the `replacement_request_round` fixture, leaving the measured call to drive `wait_for_exact` through answer consumption, round continuation, round-two publication, and exact request discovery. This is the technique `instructions/fix_slow_test.md` prescribes at line 40 for per-call heavy construction, which states that moving it to a fixture "also takes it out of the call phase the rule measures".

The fixture is function-scoped rather than module- or session-scoped, and that is correct here rather than a shortcut. It depends on `tmp_path`, which is itself function-scoped, so a broader scope is not available. It also has exactly one consumer, so "paid once" and "paid per call" are the same cost, and the instruction's reason for preferring a broader scope does not apply.

Test coverage of the behavior is fully preserved. All six assertions are unchanged, and the call still enters the wait while the exchange sits in answer-pending, so the span the test name claims is still proven by construction rather than by the removed `classify()` guard, which was a callback condition rather than an assertion.

Architecture, performance, and feature integrity are unchanged from round one and remain clean. The support module still depends only on the Git command adapter, the inventory is still one subprocess call and one linear decode, and no existing behavior is impaired.

Validation plan effects: I made no change to the validation plan again this round. The requestor's rows were already correct, so reviewer mode had nothing to write.

The round-one correction I asked for is present. The repository gate evidence line now reads that the forced `ghog day --force` bypassed the cached green no-op and completed with `fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0`. That removes the ambiguity I flagged, since a plain `ghog day` reports `cov=skipped` and cannot substantiate the claim.

The template contract still holds. The first sentence under `### Analysis of Step 1 implementation state` is exactly `Yes. Step 1 has been fully implemented.`, followed by a blank line and a prose summary, with no prefix and no restatement of the step title. No `### Missing work for Step 1` section is required or present for a Yes verdict.

The document-level status line is still correctly `No, it is not implemented.` I re-read all four `### Analysis of Step N implementation state` sections and Steps 2, 3 and 4 still read `Not started`, so the flip to `Yes, it is implemented.` would be wrong.

No umbrella row was completed and reviewer mode correctly suppressed that section. The umbrella digest is unchanged at `020d1d67f9a3dca50a2651e6dd7b6717b3f1a7ef5521c5eaf4a27de6e2c3b79c`, confirmed by `umbrella-digest compare` reporting `changed: false`.

One optional wording nit, carrying no consequence: the evidence line reads "the final forced `ghog day --force`", where "forced" and `--force` duplicate each other. It could simply read "the final `ghog day --force`". This does not need another round.

### Pre-repair mandatory checks and coverage for step 1 commit-plan-check (exchange 1) (round 2)

The gate is now stably green with real margin, which is what round one could not establish.

I ran `ghog day --force` twice again, because a single green walk is exactly what misled the round-one evidence. Both runs agree:

- Run one: `ghog full done fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0`, reporting `Objective reached`.
- Run two: `ghog full done fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0`, reporting `Objective reached`.

The duration axis is no longer marginal. `tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_lifecycle_answers_tdd.py::test_reviewer_wait_spans_answer_pending_until_the_replacement_request` has dropped out of the reported slow list entirely. It is no longer the slowest call in the suite, where in round one it measured `0.55s` and `0.41s` against the `0.50s` floor.

The new slowest call is a different and pre-existing test, `tests/unit/tools/test_review_exchange_transcript_identity_tdd.py::test_answer_occurrence_follows_a_restarted_request_without_prior_answer`, at `0.33s` on both runs against the `0.50s` floor. That is 34 percent below the floor and identical across runs, which is the margin `instructions/fix_slow_test.md` asks for rather than a value that will flap on the next jitter.

`ghog single` on the repaired lifecycle test and both Step 1 test files is green, with nothing still failing in focus and nothing passing in focus while failing in the full suite.

`git diff --cached --check` returns exit `0` with no whitespace or conflict-marker finding across the ten staged paths.

Both `rg` parity checks pass, and the widened round-two command supplies the negative evidence directly.

The recorded evidence is now honest about how to reproduce it. The validation plan names `ghog day --force` and states that it bypassed the cached green no-op, so the recorded result can no longer be confused with the `cov=skipped` short-circuit that a plain `ghog day` produces.

The pre-existing accepted exclusion remains healthy and unrelated, with `test_root_launcher_runs_without_an_activated_project_environment` recorded at `0.85s` and currently measuring `0.75s`.

The repository Markdown gate reports no finding for the plan, the validation plan, or either review transcript, so MD024 and MD025 continue to hold across all appended rounds.

### Resolved validation set and sources for step 1 commit-plan-check (exchange 1) (round 2)

The request resolved five commands, and I ran all five. The current plan-derived
resolver set adds nothing this round, so the union equals the resolved set.

- `ghog day` — source `project`. The repository gate.
- `ghog day --force` — source `request`. Added this round so the recorded
  evidence is reproducible rather than a cached no-op.
- `ghog single tests/unit/tools/test_commit_plan_support/test_commit_plan_support_tdd.py tests/unit/tools/test_git_batch_commit_workflow_process.py` — source `plan`.
- `rg -n --regexp=staged_paths --regexp=--no-renames --regexp=-z --regexp=validate_commit_plan tools/commit_plan_support.py tools/git_batch_commit_workflow.py tests/unit/tools/test_commit_plan_support tests/unit/tools/test_git_batch_commit_workflow_process.py` — source `plan`, now carrying all four parity terms.
- `git diff --cached --check` — source `request`.

Every command ran and every command passed. Nothing was unavailable, so there is
no missing mandatory evidence.

I additionally ran `ghog single` on the repaired lifecycle test alongside the two
Step 1 test files, and ran `ghog day --force` twice rather than once, because a
single sample is what made the round-one evidence unreliable.

### Resolver drift and direction for step 1 commit-plan-check (exchange 1) (round 2)

The round-one drift is resolved, and no new drift was found.

The narrowed `rg -n staged_paths ...` command is gone. The round-two resolved set carries all four parity terms through explicit patterns:

```text
rg -n --regexp=staged_paths --regexp=--no-renames --regexp=-z --regexp=validate_commit_plan tools/commit_plan_support.py tools/git_batch_commit_workflow.py tests/unit/tools/test_commit_plan_support tests/unit/tools/test_git_batch_commit_workflow_process.py
```

That form is equivalent in coverage to the plan's alternation at `docs/v0.11.0/plan.v0.11.0.commit-plan-check.md:324` and is safer as a command line, because `--regexp=-z` cannot be mistaken for an `rg` option the way a bare `-z` alternative inside a quoted alternation can. I consider this an improvement on the plan's literal text rather than a deviation from it, and no further reconciliation is needed.

The set also gained `ghog day --force` from the `request` source. That directly addresses the round-one problem that a plain `ghog day` short-circuits to `cov=skipped` and cannot re-prove a recorded result. The resolved set now names the command that actually produces the evidence.

Comparing the round-two request set against the current plan-derived resolver set, the union adds nothing. Every plan command is present, so I ran the resolved set as given rather than a wider union this round.

### Repository state around validation for step 1 commit-plan-check (exchange 1) (round 2)

My assessment produced no repository side effect. I made no repair, so the only writes were ignored root `a.*` reviewer evidence files and ignored validation artifacts.

Index identity held throughout. The round-two request-time `request_index_tree` is `5d8fde87ef62ef4ffd16d968b45a25a1519cd982`, and `capture-index-tree` returned that identical value both before assessment and after two forced full gate walks. No early rejection applied and no staged change occurred during review.

The staged set is unchanged in membership. The same ten paths are staged as in round one; the round-one repairs modified content within two already-staged paths and the ignored root commit plan, without adding or removing any path.

The umbrella is untouched. `umbrella-digest compare` returns `020d1d67f9a3dca50a2651e6dd7b6717b3f1a7ef5521c5eaf4a27de6e2c3b79c` before and after with `changed: false`, so no boundary violation exists.

The validation-state comparison is clean. Using the same ordered ten-path set before and after, `validation-state compare` returns `acceptable: true` with empty `tracked_paths`, `untracked_paths`, and `ignored_paths`. No tracked validation side effect appeared, so nothing had to be left unstaged and unreverted.

Ignored validation artifacts were refreshed as expected by the forced walks, including `.coverage`, `.testmondata`, `a.ghog.log`, and `a.ghog.outliers`. The contract explicitly accepts differences confined to ignored validation artifacts, and none of these is tracked or staged.

The only untracked path in the working tree remains `docs/v0.11.0/review.code.v0.11.0.commit-plan-check.md`, this exchange's own transcript, created by the protocol rather than by my assessment.

### Repair inventory for step 1 commit-plan-check (exchange 1) (round 2)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 1 commit-plan-check (exchange 1) (round 2)

`a.commit` remains accurate, and I re-verified it mechanically rather than by reading it. Running the repository's own `parse_clipboard_content(content, interactive=False)`, then `commit_plan_support.staged_paths(root)`, then `validate_commit_plan(blocks, staged_paths)` against the live index returns ten staged paths, four ordered groups, `valid=True`, and zero diagnostics.

Membership, grouping, order, and subjects are unchanged from round one and still correct. Group 1 carries the spec-review transcript, group 2 the three verification-gate tests, group 3 the two production paths and three Step 1 test paths, and group 4 the validation plan. Ordering remains least to most dependent, and every subject is a conventional commit with an accurate scope. The final subject is still `docs(commit-plan-check): record step 1 validation`.

The round-one instruction about group 1 was satisfied. Its body now states that paired review renderers place caller-authored Markdown directly after a label, and it names `tools/spec_review_answer.py`, `tools/spec_review_request.py`, `tools/code_review_request.py`, and `tools/code_review_answer.py` as the deferred root cause, with an explicit note that Step 1 repairs only the existing transcript. The workaround is now greppable in history instead of reading as a one-off formatting nit, which is exactly what I asked for.

Group 2's body was updated to match what the code now does, describing the move of replacement-round artifact setup into a fixture rather than the earlier wording about a repeated persisted-state read alone. The commit message and the diff agree.

I did not amend `a.commit`. Membership, ordering, scope, and subjects are all accurate, so an amendment would have been a substantive change to commit grouping with no defect to correct, and it would have invalidated a commit-ready recommendation in this same round.

One carry-forward for the commit gate, unchanged from round one and needing no action now. The untracked `docs/v0.11.0/review.code.v0.11.0.commit-plan-check.md` is this exchange's own transcript and is deliberately absent from `a.commit` while the round is still open. The `git add -A` grouping pass at the commit gate will pick it up.

### Findings and boundaries for step 1 commit-plan-check (exchange 1) (round 2)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 1 commit-plan-check (exchange 1) (round 2)

No change is required. Every round-one item is addressed and I am requesting nothing further.

Do not rework Step 1. The production implementation, its tests, the budgets, and the commit grouping are all correct, and the round-two repair to the lifecycle test is the right technique applied correctly.

One optional wording nit, which does not need another round and can be applied or ignored before the commit gate: the validation plan's evidence line reads "the final forced `ghog day --force`", where "forced" and `--force` duplicate each other. "the final `ghog day --force`" reads cleaner.

Two items are deferred by agreement rather than dropped, and should reach the pending review-mode requirements rather than being lost once this commit lands. The first is the label-inlining defect in `tools/spec_review_answer.py`, `tools/spec_review_request.py`, `tools/code_review_request.py`, and `tools/code_review_answer.py`, where the correct idiom already exists at `tools/code_review_answer.py:288`. Sequence it after Step 3, since Step 3 modifies `tools/code_review_request.py`. The second is the unimplemented caller-authored heading shift and qualification contract in `instructions/review-requestor.md`, which belongs with the same work.

At the commit gate, remember that the `git add -A` grouping pass will pick up `docs/v0.11.0/review.code.v0.11.0.commit-plan-check.md`, this exchange's transcript, which is deliberately absent from `a.commit` while the round is open.

If the human selects `Commit`, run the existing commit step. If the human selects `Rework and review again`, treat the wording nit as the full scope of that round unless the human supplies guidance that adds to it.

### Decision rationale for step 1 commit-plan-check (exchange 1) (round 2)

I am recommending `commit-ready`, and I made no repair of any kind in either round, so nothing in this exchange invalidates that recommendation.

All six readiness-floor results now pass. Identity is exact, with the request envelope, human-readable identity, plan, step, round, and exchange occurrence in agreement, and the request-time index tree `5d8fde87ef62ef4ffd16d968b45a25a1519cd982` matching the live index before and after two forced gate walks. Implementation completeness is a Yes I re-derived rather than carried forward. Mandatory validation and coverage now pass stably. Staged attribution is clean across the same ten paths. There is no unresolved finding against this step. The `a.commit` grouping is mechanically valid with zero validator diagnostics.

The round-one blocker is genuinely resolved rather than re-measured, which is the distinction I said I would hold to. Two forced walks now return `cov=100 outliers=0 excluded=0 exit=0` with `Objective reached`, where round one straddled the floor at `0.55s` and `0.41s`. The repaired call has left the slow list entirely, and the suite's slowest call is now a different, pre-existing test at `0.33s` against a `0.50s` floor, identical on both runs. That is margin, not a lucky sample. The technique used is the one `instructions/fix_slow_test.md` prescribes at line 40, and the function scope of the new fixture is forced by its `tmp_path` dependency rather than chosen, with a single consumer making the broader-scope advice moot.

The remaining renderer defect is deferred by explicit decision, and the human should see that clearly at this gate. Paired review renderers still inline caller-authored Markdown after a `Label:` prefix and a following space in `tools/spec_review_answer.py`, `tools/spec_review_request.py`, `tools/code_review_request.py`, and `tools/code_review_answer.py`, and the caller-authored heading shift promised by `instructions/review-requestor.md` is still unimplemented. Neither is caused by Step 1, neither touches Step 1 code, and repairing them here would cross the step boundary and collide with Step 3, which modifies `tools/code_review_request.py`. My round-one instruction was to record the cause rather than fix it, and group 1's commit body now names all four modules, so the workaround is documented in history instead of silently normalized. I classify this as tracked future work for the pending review-mode requirements, not as an unresolved finding against Step 1, and I would not block this commit on it.

I did not amend `a.commit` in either round. Its membership, ordering, scope, and subjects were accurate throughout, so an amendment would have been a substantive change to commit grouping with no defect to correct.

This recommendation is advisory and authorizes nothing. A green gate and a valid commit plan are mechanical evidence only; they do not confer commit authority. Only the human may choose `Commit` or `Rework and review again`.

### Final reviewer decision for step 1 commit-plan-check (exchange 1) (round 2)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-1-round-2 -->

## Round 2 by human - Step 1 - human-confirmation

- Recorded: 2026-08-26T15:57:15+02:00
- Exchange: code/code/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
- Implementation step: 1
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->

## Round 1 by requestor - Step 2

- Recorded: 2026-08-26T18:23:05+02:00
- Exchange: code/code/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
- Implementation step: 2
- Outcome: request

### Review identity for step 2 commit-plan-check (round 1)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
Implementation step: 2
Review round: 1

### Code review evidence for step 2 commit-plan-check (round 1)

request_index_tree: 4d9b89f8a2e497e4d935b3b694511f849c53d55a
resolved_validation_set:

- ghog day (sources: project)
- rg -n CommitPlanCheck tools/commit_plan_check.py commit-plan-check.bat tests/unit/tools/test_commit_plan_check (sources: plan)
- commit-plan-check.bat --format json (sources: request)

### Requestor assessment for step 2 commit-plan-check (round 1)

Step 2 is fully implemented against its exact plan slice.

- Static checks pass for type safety, lint, complexity, file girth, Markdown,
  shell, and EOF rules.
- The final detached Groundhog day passes all 2,039 tests with 100% coverage,
  no warnings, expected failures, or duration outliers.
- The checker preserves parser, staged-inventory, and validator boundaries,
  introduces no DDD-Hexagonal dependency inversion, and contains no mutation
  path.
- Each nonempty check performs one plan read, one parser pass, one staged Git
  inventory, one validator call, and one projection without quadratic work.
- Existing batch commit execution and its root-plan dry-run rejection remain
  unchanged.

### Implementation report for step 2 commit-plan-check (round 1)

The implementation adds `CommitPlanCheckState` and the frozen
`CommitPlanCheckResult`, then composes the public parser, shared staged-path
inventory, and public validator in `check_commit_plan(root)`.

Human and compact JSON renderers project the same immutable result. The CLI
supports discovered or explicit roots and maps ready, expected non-ready, and
operational outcomes to statuses 0, 3, and 2 with the required stream split.
The root launcher delegates to `python -m tools.commit_plan_check` and preserves
the CLI status.

The focused unit suite covers all six states, exact collaborator use, output
schema and ordering, CLI boundaries, module execution, discovery, operational
failures, and launcher delegation.

### Change summary for step 2 commit-plan-check (round 1)

The staged implementation contains exactly these paths:

- `commit-plan-check.bat`
- `tools/commit_plan_check.py`
- `tests/unit/tools/test_commit_plan_check/__init__.py`
- `tests/unit/tools/test_commit_plan_check/test_commit_plan_check_tdd.py`
- `docs/v0.11.0/plan.v0.11.0.commit-plan-check.validation.md`

The validated root `a.commit` contains two ordered groups:

1. `feat(commit-plan-check): expose read-only plan checker` contains the
   production checker, root launcher, and focused tests.
2. `docs(commit-plan-check): record step 2 validation` contains the required
   validation-plan evidence and is the final commit.

`commit-plan-check.bat --format json` reports `state=valid`, `ready=true`, all
five staged paths, both ordered groups, and no diagnostics.

### Writer response for step 2 commit-plan-check (round 1)

Writer response: None for round 1.

There is no earlier reviewer feedback, accepted repair, or disagreement to
report.

### Reviewer focus for step 2 commit-plan-check (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-2-round-1 -->

## Round 1 by reviewer - Step 2

- Recorded: 2026-08-26T18:53:53+02:00
- Exchange: code/code/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
- Implementation step: 2
- Outcome: answer

### Assessed index identity for step 2 commit-plan-check (exchange 1) (round 1)

Baseline index tree: 4d9b89f8a2e497e4d935b3b694511f849c53d55a

Assessed index tree: 4d9b89f8a2e497e4d935b3b694511f849c53d55a

### Implementation check for step 2 commit-plan-check (exchange 1) (round 1)

Result: No. Step 2 has NOT been fully implemented. The service, renderers, and module CLI are correct and well tested, but the shipped root launcher does not satisfy the entry-point parity and root-discovery contract that Step 2 owns, so one of the step's two adapters is wrong.

Almost everything else is right, and I verified it against the code rather than the report.

The settled Q06 parsing boundary is honored exactly. `check_commit_plan(root)` resolves `<root>/a.commit`, returns `missing-plan` when it is absent, reads the file exactly once through `_read_plan`, returns `empty-plan` on empty or whitespace content, then parses with the public `parse_clipboard_content(content, interactive=False)`. The committing workflow's private `_read_and_parse_content` is not imported, so the read-only checker carries no dependency on commit execution and no clipboard fallback.

The failure taxonomy is complete and correctly ordered. Missing, empty, malformed, invalid, empty-staged, and operational outcomes are each reachable and distinct, and `CommitMessageError` is caught separately from the broad operational guard so a malformed plan reports `invalid-plan` at status three rather than an operational failure at status two.

The writer closed a gap the plan did not name. Nonempty content that parses to zero blocks returns `empty-plan` before the inventory call, covered by `test_nonempty_content_without_blocks_is_an_empty_plan`. That ordering matters: `validate_commit_plan([], [])` produces no diagnostics, so reaching the validator with zero blocks and an empty index would have reported a ready plan. The early return forecloses that, and I confirmed the behavior live rather than by reading.

The structured contract matches the design exactly. `structured_payload` emits `schema_version` 1 with `state`, `ready`, `staged_paths`, `groups` carrying `position`, `subject`, and `paths`, and `diagnostics`, with deterministic ordering. `_result_from_validation` checks the empty inventory before validity, so a nonempty plan against an empty index reports `empty-staged-set` as the design's acceptance table requires.

The module CLI status and stream mapping is correct. Operational failures write one stable diagnostic to stderr and return `2`, while ready and expected non-ready results write the complete rendered evidence to stdout and return `0` or `3`, so automation can parse evidence before observing status three.

Architecture, performance, and feature integrity are clean. The checker depends only on the neutral inventory boundary, the public parser, the public validator, and shared root discovery, with no reverse dependency. There is no reset, add, remove, commit, or file write anywhere in the production path, and the only repository access is one plan read and one read-only index query. Each nonempty call performs one read, one parse, one inventory, one validation, and one projection, with no per-path probe and no added sort.

The defect is confined to `commit-plan-check.bat`. Its `pushd` to the launcher directory replaces the caller's working directory, so the launcher and the module report different repositories from the same starting point. That is a Step 2 deliverable failing a Step 2 contract, which is why this check is a No rather than a Yes with an observation. The details, the demonstration, and a verified fix are in the findings.

Validation plan effects: I made no change to the validation plan. Reviewer mode may write only the reviewed step's rows, and I am reporting a No verdict that the writer must reconcile with their own recorded Yes, so editing their rows underneath them would obscure the disagreement rather than resolve it.

The recorded rows state `Yes. Step 2 has been fully implemented.` My independent assessment is `No. Step 2 has NOT been fully implemented.`, because the shipped root launcher does not satisfy the entry-point parity and root-discovery contract that Step 2 owns. When the launcher is fixed, the writer's verdict becomes correct and the rows will need only the evidence corrections below.

Two recorded claims currently overstate what is proven. The focused-verification bullet lists "launcher delegation" among covered behavior, but the only launcher test reads the batch file as text and asserts four substrings, all of which pass against the defective launcher. The file-girth bullet states that the files "remain below their split triggers and the 650-line repository ceiling", which is true, but omits that `tests/unit/tools/test_commit_plan_check/test_commit_plan_check_tdd.py` is 497 lines against the 420-line advisory estimate at `docs/v0.11.0/plan.v0.11.0.commit-plan-check.md:468`. The plan's shared execution checklist item 8 requires that variance to be recorded as evidence.

Under the writer-owned contract, a No verdict also requires a `### Missing work for Step 2` section listing each missing element concretely. That section does not exist, which is consistent with the writer having reached a Yes. The concrete work list is supplied in my writer instructions so it can be transferred directly if the verdict is revised.

The rest of the rows are accurate and should be kept. The typed service, shared orchestration, equivalent evidence, architecture, performance, and coverage sections all match what I found in the code, and the gate evidence line correctly reports the detached full walk.

The document-level status line is correctly `No, it is not implemented.` Steps 3 and 4 still read `Not started`, so no flip was due regardless of this step's verdict.

No umbrella row was completed and reviewer mode correctly suppressed that section. The umbrella digest is unchanged at `020d1d67f9a3dca50a2651e6dd7b6717b3f1a7ef5521c5eaf4a27de6e2c3b79c`, confirmed by `umbrella-digest compare` reporting `changed: false`.

### Pre-repair mandatory checks and coverage for step 2 commit-plan-check (exchange 1) (round 1)

The repository gate is green with real margin, and I forced the walk rather than trusting a cached verdict.

`ghog day --force` reported `ghog full done fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0` with `Objective reached` across 2,039 tests. Correctness, warnings, expected failures, coverage, and duration all pass.

The duration axis is comfortable rather than marginal. The suite's slowest call is `tests/unit/tools/test_commit_plan_check/test_commit_plan_check_tdd.py::test_module_main_and_root_launcher_delegate_to_the_same_cli` at `0.29s` against the `0.50s` floor, which is 42 percent below it. That call is the new subprocess-based test added by this step, and it is well inside budget. The Step 1 lifecycle call that flapped in the previous exchange no longer appears in the slow list at all, so the fixture repair has held across a further round of changes.

`ghog single` on the focused Step 2 test file is green, with nothing still failing in focus and nothing passing in focus while failing in the full suite.

Both `rg` checks pass. The narrowed request form matches, and the wider plan pattern returns 73 lines with all six otherwise-dropped terms present in the production module, evidencing the composed service, `interactive=False` parsing, the format flag, the versioned schema, and the status contract.

`commit-plan-check.bat --format json` returned `state=valid`, `ready=true`, five staged paths, two ordered groups, and zero diagnostics, at status `0`. That result is accurate for this repository, and I used the shipped checker itself as my commit-plan evidence.

The single validation caveat is the one this round is blocking on. That launcher result is correct only because validation ran with the working directory at the llm-shared root. From any other working directory the same command describes llm-shared rather than the caller, which I demonstrated live. So the gate evidence proves the service and the module CLI, and does not yet prove the launcher.

I also ran the repository Markdown gate, which reports no finding for the plan, the validation plan, or either review transcript, so MD024 and MD025 continue to hold.

I performed no repair, so there is no pre-repair versus post-repair difference to report beyond this baseline.

### Resolved validation set and sources for step 2 commit-plan-check (exchange 1) (round 1)

The request resolved three commands. The current plan-derived resolver set adds
two more, so I ran five in total as the union.

- `ghog day` — source `project`. Run as `ghog day --force`, because a plain
  invocation short-circuits to `cov=skipped` when no Python file changed since
  the last green walk and cannot re-prove a recorded result.
- `rg -n CommitPlanCheck tools/commit_plan_check.py commit-plan-check.bat tests/unit/tools/test_commit_plan_check` — source `request`, narrowed relative to the plan.
- `commit-plan-check.bat --format json` — source `request`.
- `rg -n "CommitPlanCheck|check_commit_plan|interactive=False|--format|schema_version|return 3|return 2" tools/commit_plan_check.py commit-plan-check.bat tests/unit/tools/test_commit_plan_check` — source `plan`, at `docs/v0.11.0/plan.v0.11.0.commit-plan-check.md:449`, added by the union.
- `ghog single tests/unit/tools/test_commit_plan_check/test_commit_plan_check_tdd.py` — source `plan`, at `docs/v0.11.0/plan.v0.11.0.commit-plan-check.md:481`, added by the union.

Every command ran and every command passed. Nothing was unavailable, so there
is no missing mandatory evidence on the availability axis.

One passing command carries a caveat that matters. `commit-plan-check.bat
--format json` returned `state=valid`, `ready=true`, five staged paths, two
ordered groups, and no diagnostics, which is correct. It is correct only
because the working directory during validation was the llm-shared root. The
same command from any other working directory reports llm-shared rather than
the caller, so its standing as evidence depends on the launcher fix requested
in this round.

### Resolver drift and direction for step 2 commit-plan-check (exchange 1) (round 1)

Two drifts were found, both narrowing the request relative to the plan, and both are the same pattern I reported and saw corrected during Step 1.

The `rg` command is narrowed. The request carries:

```text
rg -n CommitPlanCheck tools/commit_plan_check.py commit-plan-check.bat tests/unit/tools/test_commit_plan_check
```

The plan's Step 2 completion criteria at `docs/v0.11.0/plan.v0.11.0.commit-plan-check.md:449` specify:

```text
rg -n "CommitPlanCheck|check_commit_plan|interactive=False|--format|schema_version|return 3|return 2" tools/commit_plan_check.py commit-plan-check.bat tests/unit/tools/test_commit_plan_check
```

Direction: the request is a strict subset. It keeps only the type-name term and drops `check_commit_plan`, `interactive=False`, `--format`, `schema_version`, `return 3`, and `return 2`. Those dropped terms are precisely the evidence that the service is composed as settled, that Q06's `interactive=False` parsing is used, that the format flag exists, that the structured schema is versioned, and that the status contract is implemented. The narrowed form would pass on a module that had the right class names and none of that behavior.

The `ghog single` command is missing. The plan's Step 2 timing-run readiness at `docs/v0.11.0/plan.v0.11.0.commit-plan-check.md:481` specifies `ghog single tests/unit/tools/test_commit_plan_check/test_commit_plan_check_tdd.py`, and the resolved set does not contain it.

I ran the union rather than the resolved set alone. The full plan pattern returns 73 matching lines, with all six dropped terms present in the production module, so the composition and status contract are evidenced. `ghog single` on the focused test file is green with nothing failing in focus and no focus-versus-suite interaction.

This is the second consecutive first round in which the resolved set arrives narrower than the plan. It was corrected for Step 1 in round two, and the same correction is due here. The reliable fix is to derive the plan-sourced commands from the plan text rather than re-authoring them per request.

### Repository state around validation for step 2 commit-plan-check (exchange 1) (round 1)

My assessment produced no repository side effect. I made no repair, so the only writes were ignored root `a.*` reviewer evidence files and ignored validation artifacts.

Index identity held throughout. The request-time `request_index_tree` is `4d9b89f8a2e497e4d935b3b694511f849c53d55a`, and `capture-index-tree` returned that identical value both before assessment and after the forced gate walk, the focused run, and every probe. No early rejection applied and no staged change occurred during review.

The umbrella is untouched. `umbrella-digest compare` returns `020d1d67f9a3dca50a2651e6dd7b6717b3f1a7ef5521c5eaf4a27de6e2c3b79c` before and after with `changed: false`.

The validation-state comparison is clean. Using the same ordered five-path set before and after, `validation-state compare` returns `acceptable: true` with empty `tracked_paths`, `untracked_paths`, and `ignored_paths`.

My entry-point probes ran entirely outside the repository. To demonstrate the launcher divergence I created a scratch Git repository under the session scratchpad, outside this working tree, and ran both entry points against it with `PRJ_DIR` cleared. That repository is not inside the project, nothing was written into the project, and the checker itself performed no write in either invocation, which independently exercises the read-only contract.

Ignored validation artifacts were refreshed as expected by the forced walk, including `.coverage`, `.testmondata`, `a.ghog.log`, and `a.ghog.outliers`. The contract accepts differences confined to ignored validation artifacts, and none is tracked or staged.

One tracked path outside the staged set is modified and correctly so. `docs/v0.11.0/review.code.v0.11.0.commit-plan-check.md` carries the appended Step 2 request and is not staged while this round is open, exactly as in the Step 1 exchange. The `git add -A` grouping pass at the commit gate will pick it up.

### Repair inventory for step 2 commit-plan-check (exchange 1) (round 1)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 2 commit-plan-check (exchange 1) (round 1)

`a.commit` is accurate, and I verified it with the checker this step just shipped rather than by reading it. `commit-plan-check.bat --format json` from the repository root returns `state=valid`, `ready=true`, five staged paths, two ordered groups, and zero diagnostics at status `0`.

Group membership matches the staged set exactly:

- Group 1 `feat(commit-plan-check): expose read-only plan checker` carries `commit-plan-check.bat`, `tools/commit_plan_check.py`, and the two focused test paths.
- Group 2 `docs(commit-plan-check): record step 2 validation` carries the validation plan and is the final commit.

Ordering is least to most dependent and correct, since the validation record documents the implementation that precedes it. Both subjects are conventional commits with accurate scopes, and both bodies describe what the diffs actually do.

This plan uses a different authored shape from the Step 1 plan, with `git add -- <path>` lines and unfenced message bodies rather than `## Group N` headings, `git add -A <path>` lines, and fenced blocks. The public parser accepts both, and the shipped checker confirms this one parses into exactly two ordered groups with exact membership, so the difference is presentational rather than a defect. It is worth keeping in mind only because the two shapes now coexist in this effort's history.

I did not amend `a.commit`. Membership, ordering, scope, and subjects are all accurate, so an amendment would have been a substantive change to commit grouping with no defect to correct.

One consequence of the launcher finding reaches this assessment honestly. The command I used as commit-plan evidence produced a correct answer only because my working directory was the llm-shared root. That does not weaken the conclusion for this repository, since the module entry point and my own validator run agree with it, but it does mean the same command is not yet trustworthy as the shared readiness floor Step 4 intends it to be.

### Findings and boundaries for step 2 commit-plan-check (exchange 1) (round 1)

Unresolved findings:

- The root launcher discards the caller's working directory, so the two shipped entry points disagree about which repository they check. `commit-plan-check.bat` runs `pushd "%COMMIT_PLAN_CHECK_ROOT%"` before `python -m tools.commit_plan_check`, which makes `find_project_root(Path.cwd())` resolve to the llm-shared repository rather than the caller's. I demonstrated the divergence directly, from one working directory in a scratch repository with `PRJ_DIR` cleared so environment precedence could not mask it: the module entry point returned `{"state":"empty-plan","ready":false}` with status `3`, describing that repository correctly, while the launcher returned `{"state":"valid","ready":true}` with status `0`, describing llm-shared instead.
- This breaks three settled contracts. The plan's Step 2 expected outcome requires that "Both entry points emit identical ordered evidence without changing Git or repository files". The design's first acceptance row requires that a valid root plan makes "Both entry points report identical ordered groups and return `0`". Design Q07 settles root resolution as "Discover the root from the current directory by default and accept optional `--root <path>`", and the `pushd` removes that default.
- The consequence is a false green on a readiness gate, which is the most damaging way this feature can fail. Step 4 will place `commit-plan-check.bat` in the code reviewer's readiness floor and in `group-commits-msg` before commit grouping. llm-shared is a shared tooling repository consumed by other projects through `LLM_SHARED_DIR`, so a reviewer or grouping run whose working directory sits in a consuming project would receive `ready=true` and status `0` describing llm-shared's plan while the caller's own `a.commit` is missing, empty, or mismatched.
- A fix is available and I verified it works before recommending it. Replacing the `pushd` with a `PYTHONPATH` entry that points at the launcher directory keeps the caller's working directory intact: running the module with `PYTHONPATH` set to the llm-shared root and the working directory left in the scratch repository returned `{"state":"empty-plan","ready":false}` with status `3`, exactly matching the module entry point. The `--root` passthrough already works and returned the same correct result, so it remains a usable workaround but cannot substitute for a correct default.
- The launcher delegation test cannot detect this class of defect because it never executes the launcher. `test_module_main_and_root_launcher_delegate_to_the_same_cli` reads `commit-plan-check.bat` as text and asserts that it contains `-m tools.commit_plan_check`, `%ERRORLEVEL%`, `exit /b 2`, and `exit /b`. Every one of those assertions passes against the current defective launcher. Its module half runs only `--help` with `cwd=root`, so it exercises neither discovery nor parity. Step 2's own test list claims "root-launcher delegation" coverage and the validation plan repeats that claim, but what is proven is file content rather than behavior.
- The Step 2 test file exceeds its advisory line estimate without the variance being recorded. `tests/unit/tools/test_commit_plan_check/test_commit_plan_check_tdd.py` measures 497 physical lines against the plan's advisory estimate of 420 at `docs/v0.11.0/plan.v0.11.0.commit-plan-check.md:468`. That is not a failure, since the file stays below the 550 risk band and the 650 ceiling, but the plan's shared execution checklist item 8 requires that a file exceeding only an advisory estimate has "the variance recorded as evidence". The validation plan states that the files "remain below their split triggers and the 650-line repository ceiling" without acknowledging the overrun.

Boundary-crossing work:

- Fixing the launcher is inside Step 2 rather than across a boundary, since `commit-plan-check.bat` is named by the step and is already staged. I did not repair it anyway, and the reason is scope quality rather than ownership: the correct fix pairs a launcher change with a replacement test that executes both entry points against one temporary repository, and that test is the evidence the step is missing. Writing the fix without its test would hand back a change whose only proof is my prose, and writing both would be a substantive repair that cannot validly finish this round in any case.
- The mechanism also carries a small decision the writer should own. Preserving the caller's working directory can be done by prepending the launcher directory to `PYTHONPATH`, which I verified works, or by capturing `%CD%` before the `pushd` and injecting it as `--root` only when the caller did not pass one. I recommend the first as simpler and side-effect-free, but choosing between them is a design call at the adapter boundary rather than an unambiguous repair.
- The label-inlining renderer defect carried over from the Step 1 exchange is still present and still deferred by agreement. It affects `tools/spec_review_answer.py`, `tools/spec_review_request.py`, `tools/code_review_request.py`, and `tools/code_review_answer.py`, and the correct idiom already exists at `tools/code_review_answer.py:288`. It remains outside Step 2, and `tools/code_review_request.py` is a Step 3 file, so repairing it here would still collide with Step 3. It is recorded in the Step 1 commit history as agreed.
- The unimplemented caller-authored heading shift contract in `instructions/review-requestor.md` is likewise unchanged and deferred with the same tooling work.
- The repeated narrowing of plan-sourced validation commands between the plan text and the resolved set is a requestor-side concern rather than implementation work. I report it with its direction and ran the union; I did not alter the resolved set, which belongs to the requestor.

### Writer instructions for step 2 commit-plan-check (exchange 1) (round 1)

The service, renderers, module CLI, and test matrix are good work and need no rework. The requested changes are confined to the launcher, one test, and two recorded claims.

Fix the launcher so it stops discarding the caller's working directory. In `commit-plan-check.bat`, the `pushd "%COMMIT_PLAN_CHECK_ROOT%"` and matching `popd` exist so `python -m tools.commit_plan_check` can resolve the `tools` package, but they also destroy the cwd that Q07 makes the default root. Prepend the launcher directory to `PYTHONPATH` instead and drop the `pushd` and `popd` pair, keeping the `%ERRORLEVEL%` capture and `exit /b` passthrough exactly as they are. I verified this before recommending it: with the working directory left in a scratch repository and `PYTHONPATH` pointing at the llm-shared root, the module returned `{"state":"empty-plan","ready":false}` and status `3`, identical to the module entry point run the same way, where the current launcher returned `{"state":"valid","ready":true}` and status `0`.

Do not copy `markdown-check.bat` here. That launcher uses the same `pushd`, and for it the behavior is harmless because scanning llm-shared's own tree is its purpose. Step 2's checker is the opposite case: its subject is whichever repository the caller is standing in, so the pattern must diverge deliberately. It is worth a short comment in the launcher saying why, so a later reader does not "restore consistency" with the other root launcher.

Replace the text-matching launcher test with one that executes the launcher. `test_module_main_and_root_launcher_delegate_to_the_same_cli` currently reads `commit-plan-check.bat` and asserts it contains `-m tools.commit_plan_check`, `%ERRORLEVEL%`, `exit /b 2`, and `exit /b`. All four assertions pass against the defective launcher, so the test cannot fail for the reason it exists. Make it run both entry points from one temporary Git repository with its own `a.commit` and assert that the JSON payloads and the exit statuses are identical. Guard it for Windows if needed, since the launcher is a batch file. Step 4 already plans real-repository parity acceptance, so if you prefer to keep the unit test lightweight, say explicitly in the Step 2 evidence that launcher parity is proven in Step 4 rather than claiming it here.

Correct two claims that currently overstate what is proven. The Step 2 focused-verification bullet in the validation plan lists "launcher delegation" among covered behavior; until the test above exists, that reads as behavioral coverage which does not exist. Also record the line-budget variance: `tests/unit/tools/test_commit_plan_check/test_commit_plan_check_tdd.py` is 497 lines against the 420-line advisory estimate at `docs/v0.11.0/plan.v0.11.0.commit-plan-check.md:468`. The file is comfortably below the 550 risk band and the 650 ceiling, so nothing needs splitting, but the plan's shared execution checklist item 8 requires the variance to be recorded as evidence rather than passed over. The current wording only states that the files remain below their split triggers and the ceiling.

Re-run the evidence after the launcher change. `commit-plan-check.bat --format json` is in the resolved validation set and currently produces a correct result only because the working directory happens to be the llm-shared root, so its value as evidence depends on the fix.

Two things deliberately need no change. The `a.commit` plan is accurate as it stands, with two ordered groups, exact membership, and conventional subjects, and I confirmed it with the shipped checker itself. The zero-block early return you added ahead of the inventory call is not in the plan text but is correct and worth keeping, because reaching the validator with zero blocks and an empty index would otherwise report a ready plan.

### Decision rationale for step 2 commit-plan-check (exchange 1) (round 1)

I am publishing `changes-requested`, and I made no repair, so nothing here prevents a commit-ready recommendation in the next round.

This is a disagreement about one deliverable, not about the step's quality. The requestor assessed Step 2 as fully implemented, and most of it plainly is: the typed result, the six-state taxonomy, the Q06 parsing boundary, the versioned structured schema, the status and stream contract, the architecture direction, and a genuinely strong 21-case test matrix all hold up under independent checking. The writer also closed a gap the plan never named, returning `empty-plan` for nonempty content that parses to zero blocks, which forecloses a real hole where `validate_commit_plan([], [])` would otherwise have reported a ready plan.

The blocking reason is that one of Step 2's two shipped entry points is wrong. `commit-plan-check.bat` runs `pushd` to its own directory before invoking the module, which replaces the caller's working directory and defeats the root discovery that design Q07 settles as the default. I did not infer this from reading the batch file. I built a scratch repository outside the project, cleared `PRJ_DIR` so environment precedence could not mask the behavior, and ran both entry points from the same working directory: the module returned `empty-plan` at status `3`, describing that repository, while the launcher returned `valid` with `ready=true` at status `0`, describing llm-shared. That directly contradicts the plan's Step 2 outcome that both entry points emit identical evidence and the design's first acceptance row requiring both to report identical groups.

The consequence is what makes it blocking rather than a note. Step 4 will place this exact launcher in the code reviewer's readiness floor and in `group-commits-msg` ahead of commit grouping. llm-shared is consumed by other projects through `LLM_SHARED_DIR`, so a run whose working directory sits in a consuming project would return `ready=true` and status `0` for llm-shared's plan while the caller's own `a.commit` is missing, empty, or mismatched. A readiness gate that reports a false green is the worst available failure mode for this feature, and it would be inherited by Steps 3 and 4 rather than caught there.

The existing test cannot catch it, which is why the green gate is not reassurance here. `test_module_main_and_root_launcher_delegate_to_the_same_cli` reads the batch file as text and asserts four substrings that all appear in the defective launcher, and its module half runs only `--help` with the working directory already set to the root. The full walk is genuinely green at `cov=100 outliers=0 exit=0` across 2,039 tests with comfortable duration margin, and it still proves nothing about launcher parity.

I did not repair it, and I want the reason on the record. The launcher is in scope, so ownership was not the obstacle. The fix belongs with a test that executes both entry points against one temporary repository, and that test is precisely the missing evidence; shipping the change without it would leave my prose as its only proof. The mechanism is also a small adapter-boundary decision between a `PYTHONPATH` entry and injecting `--root` from a captured `%CD%`. I verified the `PYTHONPATH` approach produces output identical to the module from a foreign working directory, so the recommendation is grounded rather than speculative, but the choice is the writer's.

Two smaller items ride along. The resolved validation set again arrived narrower than the plan, dropping five terms from the `rg` pattern and omitting `ghog single` entirely; I ran the union and both additions pass. The Step 2 test file is 497 lines against a 420-line advisory, which needs no split but does need its variance recorded under the plan's own checklist item 8.

This assessment is advisory and authorizes nothing. Only the human may choose `Commit` or `Rework and review again`.

### Final reviewer decision for step 2 commit-plan-check (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-2-round-1 -->

## Round 2 by requestor - Step 2

- Recorded: 2026-08-26T19:27:32+02:00
- Exchange: code/code/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
- Implementation step: 2
- Outcome: request

### Review identity for step 2 commit-plan-check (round 2)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
Implementation step: 2
Review round: 2

### Code review evidence for step 2 commit-plan-check (round 2)

request_index_tree: b99b838d31fa916c508eb3e3720f014fc5abf283
resolved_validation_set:

- ghog day (sources: project)
- rg -n --regexp CommitPlanCheck --regexp check_commit_plan --regexp interactive=False --regexp=--format --regexp schema_version --regexp return\s+3 --regexp return\s+2 tools/commit_plan_check.py commit-plan-check.bat tests/unit/tools/test_commit_plan_check (sources: plan)
- ghog single tests/unit/tools/test_commit_plan_check/test_commit_plan_check_tdd.py (sources: plan)
- commit-plan-check.bat --format json (sources: request)

### Requestor assessment for step 2 commit-plan-check (round 2)

Step 2 is fully implemented after the round-1 corrections.

- The batch launcher now preserves the caller's working directory and exposes
  llm-shared imports through `PYTHONPATH`, so default root discovery and
  `--root` remain module-equivalent.
- A real Windows parity test runs both entry points from the same temporary Git
  repository with `PRJ_DIR` cleared and asserts identical status and JSON.
- The final detached Groundhog day passes all 2,039 tests at 100% coverage,
  with no warnings, expected failures, or duration outliers.
- Static, architecture, performance, mutation, and feature-integrity evidence
  remains green.

### Implementation report for step 2 commit-plan-check (round 2)

Round 2 preserves the complete checker service and changes only the adapter
boundary and its evidence.

`commit-plan-check.bat` no longer changes directories. It prepends its own root
to `PYTHONPATH`, invokes the same module from the caller's cwd, captures the
module status, and returns it unchanged.

Executable adapter coverage moved into a dedicated test leaf. Its parity test
creates one real repository, runs the module and batch launcher from that
foreign cwd, and compares their statuses and structured results. Real process
setup is module-scoped so the measured assertion call remains below the suite
duration floor without dropping any assertion.

The validation plan now records executable parity and the focused service
test's 33-line advisory variance.

### Change summary for step 2 commit-plan-check (round 2)

The reviewed index contains exactly six staged paths:

- `commit-plan-check.bat`
- `tools/commit_plan_check.py`
- `tests/unit/tools/test_commit_plan_check/__init__.py`
- `tests/unit/tools/test_commit_plan_check/test_commit_plan_check_tdd.py`
- `tests/unit/tools/test_commit_plan_check/test_commit_plan_check_adapter_tdd.py`
- `docs/v0.11.0/plan.v0.11.0.commit-plan-check.validation.md`

The amended and validated root `a.commit` still contains two ordered groups.
The implementation group now includes the split adapter test; the final group
remains `docs(commit-plan-check): record step 2 validation`.

The live checker reports `state=valid`, `ready=true`, all six staged paths,
both ordered groups, and no diagnostics.

### Writer response for step 2 commit-plan-check (round 2)

Writer response: Accepted all round-1 findings with no disagreement.

- Replaced launcher `pushd` and `popd` with caller-cwd-preserving `PYTHONPATH`
  setup.
- Replaced text-only launcher assertions with executable module-to-batch parity
  from a foreign temporary repository.
- Split adapter coverage into a dedicated test leaf before approaching the
  550-line risk threshold.
- Recorded the 453-line service test's 33-line advisory variance and corrected
  the launcher-coverage claim.
- Re-ran both focused tests, the complete Groundhog day, and the amended
  commit-plan check successfully.

### Reviewer focus for step 2 commit-plan-check (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-2-round-2 -->

## Round 2 by reviewer - Step 2

- Recorded: 2026-08-26T19:35:54+02:00
- Exchange: code/code/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
- Implementation step: 2
- Outcome: answer

### Assessed index identity for step 2 commit-plan-check (exchange 1) (round 2)

Baseline index tree: b99b838d31fa916c508eb3e3720f014fc5abf283

Assessed index tree: b99b838d31fa916c508eb3e3720f014fc5abf283

### Implementation check for step 2 commit-plan-check (exchange 1) (round 2)

Result: Yes. Step 2 has been fully implemented. This reverses my round-one No, and the reversal rests on my own re-execution of the failing scenario rather than on the change summary.

The launcher defect is genuinely fixed. `commit-plan-check.bat` no longer changes directory; it prepends its own root to `PYTHONPATH`, preserving an existing value when one is set, and invokes the same module from the caller's working directory while still capturing and returning the module status. The file carries a comment stating why it must differ from the other root launcher, which is what stops a later reader from "restoring consistency" with `markdown-check.bat`.

I re-ran the exact scenario that failed in round one. From a scratch repository outside this project, with `PRJ_DIR` cleared so environment precedence could not mask the result, both entry points now agree on every path I exercised. On a plan with no groups, both returned `{"state":"empty-plan","ready":false}` at status `3`. On an unparseable plan, both returned identical `invalid-plan` evidence at status `3`. On a valid plan with matching staged membership, both returned `{"state":"valid","ready":true}` with the same single group and staged path at status `0`. In round one the same ready comparison produced `empty-plan` at status `3` from the module and `valid` at status `0` from the launcher, so the design's first acceptance row is now satisfied where it previously failed.

I also confirmed the stream contract holds under a noisy path, which I had not tested before. When the parser rejects a plan it writes its own explanatory prose, and that prose goes to stderr: stdout carried nothing but the JSON object and parsed cleanly. Automation can therefore read structured evidence before observing status three, as the design requires.

The replacement test is real coverage rather than restated intent. `test_module_and_root_launcher_check_the_same_caller_repository` builds a real Git repository with a staged file and a matching plan, clears `PRJ_DIR`, exposes imports through `PYTHONPATH` without overriding root discovery, runs both adapters from that foreign working directory, and asserts equal return codes, equal empty stderr, and equal parsed JSON. It would have failed against the round-one launcher, because the two payloads would have described different repositories. That is the property the old text-matching test could not express.

The extraction into a second file in the same leaf follows the plan's own split guidance and the repository's convention, where leaves such as `tests/unit/tools/test_review_exchange_lifecycle/` already hold several test files. Module-scoped process setup keeps the subprocess cost outside the measured call without dropping an assertion, and `tmp_path_factory` supports that scope, so unlike the Step 1 case a broader scope was available and was used.

The service itself is unchanged and still correct. `tools/commit_plan_check.py` remains at 247 lines with the same Q06 parsing boundary, the same six-state taxonomy and ordering, the same versioned structured schema, and the same status and stream mapping I accepted in round one.

Every budget holds. The checker is 247 lines against a 360 advisory, the launcher 27 against 35, the package marker 2 against 5, the focused service test 453 against a 420 advisory, and the new adapter leaf 131 lines. Nothing reaches the 550 risk band or the 650 ceiling.

Architecture, performance, and feature integrity are unchanged and clean. The dependency direction still runs one way, the production path still contains no reset, add, remove, commit, or file write, and each nonempty call still performs one read, one parse, one inventory, one validation, and one projection.

Validation plan effects: I made no change to the validation plan. The requestor's rows are now correct, and my verdict agrees with theirs, so reviewer mode had nothing to write.

The round-one disagreement is resolved. Their rows record `Yes. Step 2 has been fully implemented.` and my independent assessment now reaches the same verdict, because the launcher defect that made it a No is fixed and verified. No `### Missing work for Step 2` section is required, and none is present.

Both overstated claims are corrected. The focused-verification bullet now describes "executable module-to-launcher parity from a foreign Git repository" rather than generic launcher delegation, which matches what the new adapter test actually proves. The file-girth bullet now records the variance explicitly, stating that the focused service test at 453 lines exceeds its 420-line advisory estimate by 33 lines and that the recorded variance remains below the split trigger and the ceiling. That satisfies the plan's shared execution checklist item 8, which requires the variance to be recorded rather than passed over.

The remaining rows are accurate against the code. The launcher line count is recorded as 27 and measures 27, the checker as 247 and measures 247, and the evidence-parity row correctly states that expected non-readiness emits complete evidence on stdout, which I verified independently including under parser rejection.

The document-level status line is correctly `No, it is not implemented.` Steps 3 and 4 still read `Not started`, so no flip was due.

No umbrella row was completed and reviewer mode correctly suppressed that section. The umbrella digest is unchanged at `020d1d67f9a3dca50a2651e6dd7b6717b3f1a7ef5521c5eaf4a27de6e2c3b79c`, confirmed by `umbrella-digest compare` reporting `changed: false`.

### Pre-repair mandatory checks and coverage for step 2 commit-plan-check (exchange 1) (round 2)

The repository gate is green with comfortable margin, and I forced the walk rather than accepting a cached verdict.

`ghog day --force` reported `ghog full done fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0` with `Objective reached` across 2,039 tests.

The duration axis is healthy. The slowest call is `tests/unit/tools/test_review_exchange_recovery_acceptance/test_review_exchange_recovery_acceptance_tdd.py::test_abandoned_request_is_reclaimed_by_a_fresh_session` at `0.28s` against the `0.50s` floor, which is 44 percent below it. The new adapter parity test does not appear in the slow list at all, so its module-scoped subprocess setup succeeded in keeping real process cost out of the measured call. The Step 1 lifecycle call that flapped two exchanges ago is likewise absent.

The suite count is unchanged at 2,039, which is consistent rather than suspicious. The text-only delegation test was replaced by the executable parity test and the module-guard test was moved to the new leaf, so the net change is zero.

`ghog single` on the focused service test is green.

Both `rg` forms pass and are equivalent, each returning 75 lines, and all six terms the round-one command dropped are present in the production module.

`commit-plan-check.bat --format json` returns `state=valid`, `ready=true`, six staged paths, two ordered groups, and zero diagnostics at status `0`.

The round-one caveat on that last command is now discharged. Its result no longer depends on the working directory, because I confirmed from a scratch repository outside the project, with `PRJ_DIR` cleared, that the launcher and the module produce identical JSON and identical status on the empty-plan, invalid-plan, and valid paths. I also confirmed that parser prose goes to stderr and stdout carries only parseable JSON.

The repository Markdown gate reports no finding for the plan, the validation plan, or either review transcript, so MD024 and MD025 continue to hold.

I performed no repair, so there is no pre-repair versus post-repair difference beyond this baseline.

### Resolved validation set and sources for step 2 commit-plan-check (exchange 1) (round 2)

The request resolved four commands and I ran all four. The current plan-derived
resolver set adds nothing this round, so the union equals the resolved set.

- `ghog day` — source `project`. Run as `ghog day --force`, because a plain
  invocation short-circuits to `cov=skipped` and cannot re-prove a result.
- `rg -n --regexp CommitPlanCheck --regexp check_commit_plan --regexp interactive=False --regexp=--format --regexp schema_version --regexp return\s+3 --regexp return\s+2 tools/commit_plan_check.py commit-plan-check.bat tests/unit/tools/test_commit_plan_check` — source `plan`, now carrying every parity term.
- `ghog single tests/unit/tools/test_commit_plan_check/test_commit_plan_check_tdd.py` — source `plan`, restored this round.
- `commit-plan-check.bat --format json` — source `request`.

Every command ran and every command passed.

The `rg` command is now equivalent to the plan's canonical alternation at
`docs/v0.11.0/plan.v0.11.0.commit-plan-check.md:449`. I ran both forms and each
returns exactly 75 matching lines, so the `--regexp` spelling with `return\s+3`
and `return\s+2` loses no coverage. All six previously dropped terms are present
in the production module.

`ghog single` on the focused service test is green, with nothing failing in
focus and no focus-versus-suite interaction.

`commit-plan-check.bat --format json` reports `state=valid`, `ready=true`, six
staged paths, two ordered groups, and no diagnostics at status `0`. Unlike round
one this result no longer depends on the working directory being the llm-shared
root, since I verified the same command agrees with the module entry point from
a foreign repository.

### Resolver drift and direction for step 2 commit-plan-check (exchange 1) (round 2)

No drift this round. Both round-one drifts are corrected.

The `rg` command now carries every parity term. The resolved form uses explicit
`--regexp` flags with `return\s+3` and `return\s+2` where the plan at
`docs/v0.11.0/plan.v0.11.0.commit-plan-check.md:449` uses a quoted alternation
with `return 3` and `return 2`. I ran both forms rather than assuming
equivalence, and each returns exactly 75 matching lines over the same three
paths, so the spelling difference costs no coverage. As in Step 1, the
`--regexp` form is the safer command line, because `--regexp=--format` cannot be
mistaken for an option the way a bare `--format` alternative inside a quoted
pattern can.

`ghog single tests/unit/tools/test_commit_plan_check/test_commit_plan_check_tdd.py`
is restored to the resolved set from the `plan` source, matching
`docs/v0.11.0/plan.v0.11.0.commit-plan-check.md:481`.

Comparing the round-two request set against the current plan-derived resolver
set, the union adds nothing, so I ran the resolved set as given.

One process note rather than a finding. This is the second effort in which the
first round arrived narrower than the plan and the second round corrected it.
Deriving the plan-sourced commands from the plan text, rather than re-authoring
them per request, would remove the class rather than the instance.

### Repository state around validation for step 2 commit-plan-check (exchange 1) (round 2)

My assessment produced no repository side effect. I made no repair, so the only writes were ignored root `a.*` reviewer evidence files and ignored validation artifacts.

Index identity held throughout. The request-time `request_index_tree` is `b99b838d31fa916c508eb3e3720f014fc5abf283`, and `capture-index-tree` returned that identical value both before assessment and after the forced gate walk, the focused run, the Markdown gate, and every entry-point probe. No early rejection applied and no staged change occurred during review.

The umbrella is untouched. `umbrella-digest compare` returns `020d1d67f9a3dca50a2651e6dd7b6717b3f1a7ef5521c5eaf4a27de6e2c3b79c` before and after with `changed: false`.

The validation-state comparison is clean. Using the same ordered six-path set before and after, `validation-state compare` returns `acceptable: true` with empty `tracked_paths`, `untracked_paths`, and `ignored_paths`.

My parity probes ran entirely outside the repository. I created a scratch Git repository under the session scratchpad, exercised the empty-plan, invalid-plan, and valid paths through both entry points with `PRJ_DIR` cleared, and removed it afterwards. Nothing was written into this project, and the checker performed no write in any invocation, which independently exercises the read-only contract from a second direction.

Ignored validation artifacts were refreshed as expected by the forced walk, including `.coverage`, `.testmondata`, `a.ghog.log`, and `a.ghog.outliers`. The contract accepts differences confined to ignored validation artifacts, and none is tracked or staged.

One tracked path outside the staged set is modified and correctly so. `docs/v0.11.0/review.code.v0.11.0.commit-plan-check.md` carries the appended Step 2 rounds and is not staged while this round is open.

### Repair inventory for step 2 commit-plan-check (exchange 1) (round 2)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 2 commit-plan-check (exchange 1) (round 2)

`a.commit` is accurate after its amendment, and I verified it with the checker this step ships rather than by reading it. `commit-plan-check.bat --format json` returns `state=valid`, `ready=true`, six staged paths, two ordered groups, and zero diagnostics at status `0`.

The amendment is correct and minimal. Group 1 `feat(commit-plan-check): expose read-only plan checker` now also carries `tests/unit/tools/test_commit_plan_check/test_commit_plan_check_adapter_tdd.py` alongside the launcher, the checker module, the package marker, and the focused service test. Group 2 `docs(commit-plan-check): record step 2 validation` still carries the validation plan alone and remains the final commit.

Membership matches the index exactly, with all six staged paths planned and no planned path absent. Ordering is least to most dependent, since the validation record documents the implementation that precedes it. Both subjects are conventional commits with accurate scopes, and both bodies describe what the diffs actually do.

Placing the new adapter test in the implementation group rather than a separate one is the right call. It is part of the same deliverable and would not stand alone as a coherent commit.

I did not amend `a.commit`. Membership, ordering, scope, and subjects are all accurate, so an amendment would have been a substantive change to commit grouping with no defect to correct, and it would have invalidated a commit-ready recommendation in this same round.

Unlike round one, my commit-plan evidence no longer carries a working-directory caveat. The command I used is now trustworthy from any directory, which I confirmed against a scratch repository, so the same command can serve as the shared readiness floor Step 4 intends.

One carry-forward for the commit gate, unchanged in shape from the Step 1 exchange and needing no action now. `docs/v0.11.0/review.code.v0.11.0.commit-plan-check.md` is tracked, carries this exchange's appended rounds, and is deliberately unstaged while the round is open. The `git add -A` grouping pass at the commit gate will pick it up.

### Findings and boundaries for step 2 commit-plan-check (exchange 1) (round 2)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 2 commit-plan-check (exchange 1) (round 2)

No change is required. Every round-one item is addressed and I am requesting nothing further.

Do not rework Step 2. The launcher fix, the executable parity test, the test-leaf split, and both evidence corrections are all correct as they stand.

Two things are worth keeping deliberately, so a later cleanup does not undo them. The comment in `commit-plan-check.bat` explaining why it preserves the caller's directory should stay, because the original defect came from copying `markdown-check.bat`, and without that note the `pushd` is likely to be restored in the name of consistency. The module scope on the adapter fixture should also stay, since it is what keeps real subprocess cost out of the measured call and off the duration floor.

Two items remain deferred by agreement rather than dropped, and should reach the pending review-mode requirements rather than being lost. The first is the label-inlining defect in `tools/spec_review_answer.py`, `tools/spec_review_request.py`, `tools/code_review_request.py`, and `tools/code_review_answer.py`, where the correct idiom already exists at `tools/code_review_answer.py:288`; sequence it after Step 3, which modifies `tools/code_review_request.py`. The second is the unimplemented caller-authored heading shift and qualification contract in `instructions/review-requestor.md`.

One process note for Step 3, offered rather than requested. Both first rounds in this effort arrived with a plan-sourced validation command narrower than the plan text, and both were corrected in round two. Deriving those commands from the plan rather than re-authoring them per request would remove the pattern.

At the commit gate, remember that the `git add -A` grouping pass will pick up `docs/v0.11.0/review.code.v0.11.0.commit-plan-check.md`, which carries this exchange's rounds and is deliberately unstaged while the round is open.

If the human selects `Commit`, run the existing commit step. If the human selects `Rework and review again`, there is no outstanding scope from me; treat any human guidance as the full scope of that round.

### Decision rationale for step 2 commit-plan-check (exchange 1) (round 2)

I am recommending `commit-ready`, and I made no repair in either round, so nothing in this exchange invalidates the recommendation.

All six readiness-floor results pass. Identity is exact, with the envelope, human-readable identity, plan, step, round, and exchange occurrence in agreement and the request-time index tree `b99b838d31fa916c508eb3e3720f014fc5abf283` matching the live index before and after all validation. Implementation completeness is now a Yes, reversing my round-one No. Mandatory validation and coverage pass with margin. Staged attribution is clean across six paths. No unresolved finding remains against this step. The `a.commit` grouping is valid with zero diagnostics.

The reversal is earned by re-execution, not by the change summary. I rebuilt the failing scenario from round one: a scratch repository outside this project, `PRJ_DIR` cleared so environment precedence could not mask the result, both entry points invoked from that foreign working directory. Where round one produced `empty-plan` at status `3` from the module against `valid` with `ready=true` at status `0` from the launcher, the two now agree byte for byte on the empty-plan path, the invalid-plan path, and the valid path, statuses included. The design's first acceptance row, which round one failed, now holds.

The fix is also the right shape rather than merely effective. The launcher preserves the caller's working directory by extending `PYTHONPATH` instead of changing directory, preserves an existing `PYTHONPATH` when present, still captures and returns the module status, and carries a comment explaining why it must diverge from `markdown-check.bat`. That comment matters more than it looks, because the defect originated in copying that pattern.

The replacement test can now fail for the reason it exists. The old assertion read the batch file as text and passed against the defective launcher. The new one builds a real repository, runs both adapters from a foreign working directory, and compares statuses, stderr, and parsed JSON, so it would have caught the original divergence. Module-scoped setup keeps the real process cost outside the measured call, and the gate confirms it: the parity test does not appear in the slow list, and the suite's slowest call sits 44 percent below the floor.

Two smaller round-one items are also closed. The advisory variance is now recorded explicitly at 453 against 420 lines, satisfying the plan's checklist item 8, and the launcher-coverage claim now says what the test actually proves. The resolved validation set carries every parity term and the restored `ghog single`; I ran both `rg` spellings and confirmed they return identical counts rather than assuming equivalence.

I checked one thing this round that I had not tested before, because a fix can shift a stream contract. When the parser rejects a plan it writes explanatory prose, and that prose goes to stderr: stdout carried only the JSON object and parsed cleanly. Automation can read structured evidence before observing status three, as the design requires.

One item remains deferred by agreement and the human should see it at this gate. The label-inlining defect in `tools/spec_review_answer.py`, `tools/spec_review_request.py`, `tools/code_review_request.py`, and `tools/code_review_answer.py` is unchanged, with the correct idiom already present at `tools/code_review_answer.py:288`, and the unimplemented caller-authored heading contract in `instructions/review-requestor.md` travels with it. Neither is caused by Step 2, neither touches Step 2 code, and `tools/code_review_request.py` belongs to Step 3, so repairing either here would cross the boundary and collide with planned work. Both are recorded in the Step 1 commit history. I classify them as tracked future work for the pending review-mode requirements rather than unresolved findings against Step 2, and I would not block this commit on them.

This recommendation is advisory and authorizes nothing. A green gate, a valid commit plan, and verified entry-point parity are mechanical evidence only. Only the human may choose `Commit` or `Rework and review again`.

### Final reviewer decision for step 2 commit-plan-check (exchange 1) (round 2)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-2-round-2 -->

## Round 2 by human - Step 2 - human-confirmation

- Recorded: 2026-08-26T20:06:06+02:00
- Exchange: code/code/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
- Implementation step: 2
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->

## Round 1 by requestor - Step 3

- Recorded: 2026-08-27T09:16:00+02:00
- Exchange: code/code/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
- Implementation step: 3
- Outcome: request

### Review identity for step 3 commit-plan-check (round 1)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
Implementation step: 3
Review round: 1

### Code review evidence for step 3 commit-plan-check (round 1)

request_index_tree: 20f249d9c5a8a5bdb1aaf863be0f90d8ab45460b
resolved_validation_set:

- ghog day (sources: project)
- rg -n -e commit_plan -e check_commit_plan -e request_index_tree -e capture_index_tree -e ready tools/code_review_request.py tests/unit/tools/test_code_review_request tests/unit/tools/test_code_review_request_commit_plan tests/unit/tools/test_code_reviewer_acceptance tests/unit/tools/test_code_review_requestor_acceptance (sources: plan)
- ghog single tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py tests/unit/tools/test_code_review_request_commit_plan/test_code_review_request_commit_plan_tdd.py tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_acceptance_tdd.py tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py (sources: plan)
- commit-plan-check.bat --format json (sources: request)

commit_plan_result:

```text
state: valid
ready: true
group 1: chore(env): resolve Claude launcher path
group 1 path: senv.doskey
group 2: feat(commit-plan-check): gate review requests
group 2 path: tools/code_review_request.py
group 2 path: tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py
group 2 path: `tests/unit/tools/test_code_review_request_commit_plan/__init__.py`
group 2 path: tests/unit/tools/test_code_review_request_commit_plan/test_code_review_request_commit_plan_tdd.py
group 2 path: tests/unit/tools/test_code_reviewer_acceptance/fixtures.py
group 2 path: tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_acceptance_tdd.py
group 2 path: tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py
group 2 path: tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py
group 3: docs(commit-plan-check): record step 3 validation
group 3 path: docs/v0.11.0/plan.v0.11.0.commit-plan-check.validation.md
staged path: docs/v0.11.0/plan.v0.11.0.commit-plan-check.validation.md
staged path: senv.doskey
staged path: tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py
staged path: tests/unit/tools/test_code_review_request_commit_plan/__init__.py
staged path: tests/unit/tools/test_code_review_request_commit_plan/test_code_review_request_commit_plan_tdd.py
staged path: tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py
staged path: tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py
staged path: tests/unit/tools/test_code_reviewer_acceptance/fixtures.py
staged path: tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_acceptance_tdd.py
staged path: tools/code_review_request.py
```

### Requestor assessment for step 3 commit-plan-check (round 1)

Step 3 is fully implemented against the exact publication-enforcement slice.

- The final detached Groundhog walk passes static checks, focused tests, the
  full suite, 100% coverage, and the duration gate with no warnings or expected
  failures.
- The specialized adapter depends on the read-only checker and neutral evidence
  boundaries; no dependency points back from the checker or exchange core.
- Each request adds two constant-count tree captures around one checker call,
  with linear projections over existing typed evidence.
- Existing envelope validation, paired writes, validation-command resolution,
  exchange publication, and direct role-neutral publication remain intact.
- Production and test files remain below the 650-line split trigger. The
  validation plan records the small advisory variances for the renderer and its
  established rendering test.

### Implementation report for step 3 commit-plan-check (round 1)

The implementation extends `CodeReviewRoundInput` with one required typed ready
`CommitPlanCheckResult`. `_CodeReviewEvidence` places its full structured
payload beside the existing request index tree and resolved validation set,
while the transcript summary uses the shared human renderer on the same value.

The command adapter now captures tree A, calls `check_commit_plan(root)` once,
rejects non-ready or operational evidence, captures tree B, rejects drift, and
only then renders and writes both outputs. Small validation helpers keep the
input invariant below the repository complexity threshold.

A dedicated test leaf covers direct typed-boundary rejection, exact call order,
complete evidence, all three rejection classes, and preservation of both
outputs. Existing renderer, reviewer, and requestor acceptance builders now
supply typed ready evidence and retain their previous behavior.

### Change summary for step 3 commit-plan-check (round 1)

The staged set contains exactly these ten paths:

- `senv.doskey`
- `tools/code_review_request.py`
- `tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py`
- `tests/unit/tools/test_code_review_request_commit_plan/__init__.py`
- `tests/unit/tools/test_code_review_request_commit_plan/test_code_review_request_commit_plan_tdd.py`
- `tests/unit/tools/test_code_reviewer_acceptance/fixtures.py`
- `tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_acceptance_tdd.py`
- `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py`
- `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py`
- `docs/v0.11.0/plan.v0.11.0.commit-plan-check.validation.md`

The formatted root `a.commit` contains three ordered groups:

1. `chore(env): resolve Claude launcher path` isolates the pre-existing shell
   alias change staged by the repository-wide handoff.
2. `feat(commit-plan-check): gate review requests` contains the Step 3 adapter
   and test implementation.
3. `docs(commit-plan-check): record step 3 validation` contains only the
   required trailing validation record.

`commit-plan-check.bat --format json` reports `state=valid`, `ready=true`, all
ten staged paths, all three groups, and no diagnostics.

### Writer response for step 3 commit-plan-check (round 1)

Writer response: Writer response: None for round 1.

There is no earlier reviewer feedback, accepted repair, or disagreement to
report.

### Reviewer focus for step 3 commit-plan-check (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-3-round-1 -->

## Round 1 by reviewer - Step 3

- Recorded: 2026-08-27T09:26:03+02:00
- Exchange: code/code/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
- Implementation step: 3
- Outcome: answer

### Assessed index identity for step 3 commit-plan-check (exchange 1) (round 1)

Baseline index tree: 20f249d9c5a8a5bdb1aaf863be0f90d8ab45460b

Assessed index tree: 20f249d9c5a8a5bdb1aaf863be0f90d8ab45460b

### Implementation check for step 3 commit-plan-check (exchange 1) (round 1)

Result: No. Step 3 has NOT been fully implemented. The enforcement gate itself is correct and well covered, but the same change also embeds the commit-plan human rendering into the versioned transcript without a fence, which fails the repository's Markdown gate and therefore the whole `ghog day` walk.

The parts I checked independently are genuinely right, and I want that on the record before the defect.

The enforced order matches the settled design exactly. `_render_from_arguments` captures tree A with `capture_index_tree(root)`, calls `_ready_commit_plan(root)` once, captures tree B, rejects any difference with `index changed during commit plan check`, constructs the typed input, renders, and only then writes both outputs. Every rejection raises before either `_write_utf8` call, so no rejected path can leave a partial or stale artifact behind.

Q07 option 7B is honored precisely. `commit_plan_result` is a required field on `CodeReviewRoundInput`, placed before the defaulted `human_guidance` so the dataclass ordering stays valid, and `__post_init__` delegates to `_validate_request_evidence`, which refuses a non-ready result with `commit plan result must be ready`. Non-ready request content is therefore unconstructible, not merely unreachable through the command path.

Operational failure stays separate from expected non-readiness. `_ready_commit_plan` tests `CommitPlanCheckState.OPERATIONAL_FAILURE` first and raises a distinct message, so a checker that could not decide is never reported as a plan that is not ready.

Design Q06 on durable evidence is satisfied. `_CodeReviewEvidence` carries the complete `structured_payload()` beside the request index tree and resolved validation set, and its `summary()` derives the human form from the same in-memory value through `render_human` rather than reparsing JSON.

Q04 is honored in the risk-band file. `tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py` gained 18 lines consisting of one import, one shared `_READY_RESULT` constant, one argument in the shared `_round_input` builder, evidence-parity assertions, and one checker seam helper. Every new gate case lives in the dedicated leaf, whose three tests cover direct typed-boundary rejection, exact call order between matching tree captures before writes, and the guarantee that a rejected gate creates or changes neither output.

The complexity extraction is reasonable. Pulling `_validate_authored_inputs` and `_validate_request_evidence` out of `__post_init__` keeps that method within the repository complexity threshold without moving checker policy out of `tools/commit_plan_check.py`.

Both advisory variances are recorded as the plan's shared checklist item 8 requires. `tools/code_review_request.py` is 552 lines against a 545 advisory and the renderer test is 568 against 560, and the validation plan states both overruns and their distance from the 650 split trigger accurately. The remaining five touched files sit inside their estimates.

The defect is confined to how that correct evidence reaches Markdown. Because `summary()` emits `render_human` output unfenced, staged paths containing a dunder are parsed as strong emphasis and the transcript fails MD050. That is a Step 3 deliverable breaking a repository gate the umbrella declares binding, which is why this is a No rather than a Yes with an observation. The demonstration and a contained fix are in the findings and writer instructions.

Validation plan effects: I made no change to the validation plan. Reviewer mode may write only the reviewed step's rows, and I am reporting a No verdict against the requestor's recorded Yes, so editing their rows underneath them would obscure the disagreement rather than resolve it.

The recorded rows state `Yes. Step 3 has been fully implemented.` My independent assessment is `No. Step 3 has NOT been fully implemented.`, because the same change that adds the enforcement gate also writes unfenced command output into the versioned transcript and fails the repository's Markdown gate. When the fence lands, the writer's verdict becomes correct and the rows need only the evidence correction below.

One recorded claim does not reproduce. The Step 3 rows and the round-one assessment both report a passing detached Groundhog walk covering static checks, focused tests, the full suite, coverage, and the duration gate. My forced walk stopped at the static check phase with `exit=1`, so the full suite, coverage, and duration figures were never produced for this staged state. That line needs re-running and re-recording rather than rewording.

The line-girth row is accurate and complete, and satisfies the plan's shared execution checklist item 8. It records `tools/code_review_request.py` at 552 lines as seven above its 545-line advisory, and the renderer test at 568 as eight above its 560-line advisory, with both below the 650-line split trigger, and states that the other touched test files remain inside their Step 3 estimates. I measured all seven files and every figure matches.

Under the writer-owned contract, a No verdict also requires a `### Missing work for Step 3` section listing each missing element concretely. That section does not exist, which is consistent with the writer having reached a Yes. The concrete work list is supplied in my writer instructions so it can be transferred directly if the verdict is revised.

The document-level status line is correctly `No, it is not implemented.` Step 4 still reads `Not started`, so no flip was due regardless of this step's verdict.

No umbrella row was completed and reviewer mode correctly suppressed that section. The umbrella digest is unchanged at `020d1d67f9a3dca50a2651e6dd7b6717b3f1a7ef5521c5eaf4a27de6e2c3b79c`, confirmed by `umbrella-digest compare` reporting `changed: false`.

### Pre-repair mandatory checks and coverage for step 3 commit-plan-check (exchange 1) (round 1)

Mandatory validation does not pass for this staged state, and the failure is in the repository gate rather than in the Step 3 tests.

`ghog day --force` reported `ghog check done fail=0 warn=0 xfail=0 cov=skipped outliers=skipped excluded=skipped exit=1` and stopped there. Because the walk opens with the static check, it never ran the affected phase or the full suite, so there is no coverage figure, no duration measurement, and no full-suite result for this state. Treating a walk that ended at its first phase as evidence of a passing suite would be exactly the cached-verdict mistake I have been forcing walks to avoid.

Every other static step inside that phase passed: ty, pyright, ruff, radon complexity, vulture, the 650-line big-file check, shellcheck, and the EOF check all reported OK. The single failing step is markdown-check, reported as `Failed steps for project 'llm-shared': markdown(1)`.

The two markdown findings are `docs/v0.11.0/review.code.v0.11.0.commit-plan-check.md:1257` and `:1268`, both `MD050: strong style [Expected: asterisk; Actual: underscore]`. Both lines carry `tests/unit/tools/test_code_review_request_commit_plan/__init__.py`, where the dunder is parsed as underscore-strong emphasis because Step 3 embeds the commit-plan human rendering into the transcript unfenced.

The rule is legitimately in force. `.markdownlint.json` disables only MD013 and constrains MD033 to `img`, so MD050 runs at its default, which is the rule set the umbrella's Markdown requirement adopts. This is a real gate failure, not a configuration artifact.

The Step 3 tests themselves are healthy. `ghog single` across all five Step 3 test files is green with nothing failing in focus and no focus-versus-suite interaction, so the defect is in what the code writes into a versioned document rather than in the gate logic or its coverage.

The `rg` evidence passes and shows no drift, with the resolved `-e` spelling and the plan's alternation each returning 118 lines over the same paths.

`commit-plan-check.bat --format json` reports `state=valid`, `ready=true`, ten staged paths, three ordered groups, and no diagnostics, so the commit plan itself is sound.

`git diff --cached --check`, which I ran although it is absent from this round's set, exits `2` with `tests/unit/tools/test_code_review_request_commit_plan/__init__.py:2: new blank line at EOF`.

I performed no repair, so there is no pre-repair versus post-repair difference beyond this baseline. No coverage figure can be quoted for this state until the gate reaches the full phase again.

### Resolved validation set and sources for step 3 commit-plan-check (exchange 1) (round 1)

The request resolved four commands and I ran all four. The current plan-derived
resolver set adds nothing, so the union equals the resolved set.

- `ghog day` — source `project`. Run as `ghog day --force`, because a plain
  invocation short-circuits to `cov=skipped` and cannot re-prove a result.
- `rg -n -e commit_plan -e check_commit_plan -e request_index_tree -e capture_index_tree -e ready tools/code_review_request.py tests/unit/tools/test_code_review_request tests/unit/tools/test_code_review_request_commit_plan tests/unit/tools/test_code_reviewer_acceptance tests/unit/tools/test_code_review_requestor_acceptance` — source `plan`.
- `ghog single tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py tests/unit/tools/test_code_review_request_commit_plan/test_code_review_request_commit_plan_tdd.py tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_acceptance_tdd.py tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py` — source `plan`.
- `commit-plan-check.bat --format json` — source `request`.

Every command ran. Three passed and one failed.

`ghog day --force` failed. It stopped in its first phase with
`ghog check done fail=0 warn=0 xfail=0 exit=1` and never reached the affected or
full runs, so no coverage, duration, or full-suite result exists for this
staged state. The failing step is markdown-check.

The `rg` command passes and carries no drift. I ran both the `-e` spelling from
the resolved set and the plan's quoted alternation at
`docs/v0.11.0/plan.v0.11.0.commit-plan-check.md:580`, and each returns exactly
118 matching lines, so the two forms are equivalent.

`ghog single` over all five Step 3 test files is green, with nothing failing in
focus and nothing passing in focus while failing in the full suite.

`commit-plan-check.bat --format json` reports `state=valid`, `ready=true`, ten
staged paths, three ordered groups, and no diagnostics.

I additionally ran `git diff --cached --check`, which is absent from this
round's resolved set but was request-sourced for Step 1. It reports one finding
and exits `2`.

### Resolver drift and direction for step 3 commit-plan-check (exchange 1) (round 1)

No drift in the plan-sourced commands this round, which is a change from both
earlier steps.

The `rg` command carries every parity term. The resolved set uses repeated `-e`
flags where the plan at
`docs/v0.11.0/plan.v0.11.0.commit-plan-check.md:580` uses a quoted alternation.
I ran both forms rather than assuming equivalence, and each returns exactly 118
matching lines over the same five paths, so the spelling costs no coverage.

`ghog single` is present with the plan's exact five-file list, matching
`docs/v0.11.0/plan.v0.11.0.commit-plan-check.md` for this step.

Comparing the request set against the current plan-derived resolver set, the
union adds nothing, so I ran the resolved set as given.

One command has silently left the set across steps, and it is worth naming as
drift of a different kind. `git diff --cached --check` was request-sourced for
Step 1, where it passed and formed part of that round's evidence. It is absent
from the Step 2 and Step 3 sets. I ran it anyway this round and it exits `2`
with `tests/unit/tools/test_code_review_request_commit_plan/__init__.py:2: new
blank line at EOF`. Nothing in the plan requires that command, so its absence is
not a deviation from the plan; it is a narrowing of the request-sourced evidence
this exchange used to carry, and restoring it costs nothing.

### Repository state around validation for step 3 commit-plan-check (exchange 1) (round 1)

My assessment produced no repository side effect. I made no repair, so the only writes were ignored root `a.*` reviewer evidence files and ignored validation artifacts.

Index identity held throughout. The request-time `request_index_tree` is `20f249d9c5a8a5bdb1aaf863be0f90d8ab45460b`, and `capture-index-tree` returned that identical value both before assessment and after the forced walk, the focused run, and every inspection. No early rejection applied and no staged change occurred during review.

The umbrella is untouched. `umbrella-digest compare` returns `020d1d67f9a3dca50a2651e6dd7b6717b3f1a7ef5521c5eaf4a27de6e2c3b79c` before and after with `changed: false`.

The validation-state comparison is clean. Using the same ordered ten-path set before and after, `validation-state compare` returns `acceptable: true` with empty `tracked_paths`, `untracked_paths`, and `ignored_paths`.

Ignored validation artifacts were refreshed as expected, including `a.ghog.log`. Because the walk stopped at its check phase, the coverage and duration artifacts were not regenerated this round. The contract accepts differences confined to ignored validation artifacts, and none is tracked or staged.

One tracked path outside the staged set is modified, and it is the one carrying the defect. `docs/v0.11.0/review.code.v0.11.0.commit-plan-check.md` holds the appended Step 3 request, including the unfenced commit-plan block that fails MD050. It is correctly unstaged while the round is open, so it is not part of the reviewed index, but it is part of the working tree the gate scans, which is why the gate fails against a staged set that is itself clean.

I inspected line endings while reading the diff and record the observation here rather than as a finding, since nothing forbids it. The committed blob of `tools/code_review_request.py` is uniformly CRLF with 497 line breaks, while the staged blob is mixed with 449 CRLF and 103 bare LF, so roughly a hundred diff lines carry no textual change. `.gitattributes` declares no end-of-line policy, and the file's sibling modules in `tools/` are LF.

### Repair inventory for step 3 commit-plan-check (exchange 1) (round 1)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 3 commit-plan-check (exchange 1) (round 1)

`a.commit` is accurate, and I verified it with the shipped checker rather than by reading it. `commit-plan-check.bat --format json` returns `state=valid`, `ready=true`, ten staged paths, three ordered groups, and zero diagnostics.

Group membership matches the index exactly:

- Group 1 `chore(env): resolve Claude launcher path` carries `senv.doskey` alone.
- Group 2 `feat(commit-plan-check): gate review requests` carries `tools/code_review_request.py` and the seven Step 3 test paths.
- Group 3 `docs(commit-plan-check): record step 3 validation` carries the validation plan alone and is the final commit.

Isolating `senv.doskey` into its own group is exactly right, and worth saying so explicitly. It is a pre-existing shell-alias change unrelated to Step 3 that the repository-wide handoff swept into the index. The grouping rule requires such a change to be ranked by its own dependencies and given a fitting group rather than dropped or folded into the feature, and that is what happened. Its `chore(env)` scope and subject describe it honestly rather than hiding it inside the Step 3 commit.

Ordering is least to most dependent and correct: the unrelated environment change first, the feature it does not depend on second, and the validation record that documents that feature last. All three subjects are conventional commits with accurate scopes.

I did not amend `a.commit`. Membership, ordering, scope, and subjects are all accurate, so an amendment would have been a substantive change to commit grouping with no defect to correct.

One consequence of the blocking finding reaches the commit rather than the plan. The transcript `docs/v0.11.0/review.code.v0.11.0.commit-plan-check.md` is tracked, currently modified, and deliberately unstaged while the round is open, so it is correctly absent from `a.commit`. The `git add -A` grouping pass at the commit gate will stage it, which means the commit would carry a file that fails the repository's Markdown gate unless the fence is applied first. That is another reason the fix belongs before the gate rather than after it.

### Findings and boundaries for step 3 commit-plan-check (exchange 1) (round 1)

Unresolved findings:

- The repository gate fails, and Step 3's own new code is the cause. `ghog day --force` stops in its first phase with `ghog check done fail=0 warn=0 xfail=0 exit=1`, never reaching the affected or full runs. The failing step is markdown-check, which reports `docs/v0.11.0/review.code.v0.11.0.commit-plan-check.md:1257: MD050: strong style [Expected: asterisk; Actual: underscore]` and the same rule at line 1268. Both flagged lines are staged-path lines containing `tests/unit/tools/test_code_review_request_commit_plan/__init__.py`, where the `__init__` dunder is parsed as underscore-strong emphasis.
- The mechanism is new in this step. `_CodeReviewEvidence.summary()` now appends `render_human(self.commit_plan_result)` to the transcript summary, and that block is emitted as bare Markdown rather than inside a fence. I confirmed it in the transcript: the `commit_plan_result:` label is followed by unfenced `state:`, `ready:`, `group N path:`, and `staged path:` lines. The paired JSON projection in the request is correctly fenced, so only the human summary path is affected. `render_human` itself is Step 2 code and is fine; it is a plain-text renderer, and the defect is embedding plain text into Markdown without a fence.
- This is not a one-off. Every staged path containing a dunder breaks the transcript, and `__init__.py` is present in every new test leaf this effort creates, including the one Step 3 itself adds. The gate stayed green through Steps 1 and 2 only because the human commit-plan block did not yet reach the transcript. MD050 is legitimately enforced: `.markdownlint.json` disables only MD013 and constrains MD033, so every other rule runs at its default, which is exactly the rule set the umbrella's Markdown requirement adopts.
- The requestor's recorded evidence does not reproduce. The round-one assessment states that "The final detached Groundhog walk passes static checks, focused tests, the full suite, 100% coverage, and the duration gate with no warnings or expected failures". My forced walk never reached the full suite, because the static check phase failed first. The focused runs are genuinely green, so the divergence is confined to the gate as a whole rather than to the Step 3 tests.
- The fix is contained but carries a test consequence worth naming. Fencing the embedded human block inside `summary()` removes Markdown parsing from those lines entirely. The existing renderer test asserts the current unfenced shape with `assert "commit_plan_result:\n\nstate: valid\nready: true" in rendered.transcript_summary`, so that assertion must move with the fix, and a regression case whose staged set contains a dunder path is what would keep the gate honest afterwards.
- `git diff --cached --check` reports one finding, and it is no longer in the resolved validation set. It returns `tests/unit/tools/test_code_review_request_commit_plan/__init__.py:2: new blank line at EOF` at exit `2`. That command was request-sourced for Step 1, where it passed, and has been absent since. The same trailing-blank shape exists in the `tests/unit/tools/test_commit_plan_check/__init__.py` that Step 2 committed, so this is a small repeated pattern rather than a new mistake, and the repository's own EOF check accepts it. I report it because the command that detects it used to be part of this exchange's evidence and quietly stopped being so.

Boundary-crossing work:

- Fixing the unfenced transcript block is inside Step 3, not across a boundary. `tools/code_review_request.py` is named by the step and is already staged, and the change is a few lines in `_CodeReviewEvidence.summary()`. I did not repair it for the same reason as in earlier steps: the fix belongs with the assertion that currently pins the broken shape and with a regression case covering a dunder path, and shipping the code change without that test would leave the gate depending on whether a future round happens to stage such a path. A repair of that size would also be substantive and could not finish this round in any case.
- The label-inlining renderer defect is unchanged and still deferred by agreement, affecting `tools/spec_review_answer.py`, `tools/spec_review_request.py`, `tools/code_review_request.py`, and `tools/code_review_answer.py`, with the correct idiom already at `tools/code_review_answer.py:288`. Its relationship to this effort has shifted, and I note that rather than leaving my earlier advice standing unexamined: I previously recommended sequencing it after Step 3 because Step 3 modifies `tools/code_review_request.py`. Step 3 has now landed those changes, so that collision risk is largely spent and this is a reasonable point to schedule the work.
- The unimplemented caller-authored heading shift and qualification contract in `instructions/review-requestor.md` remains deferred with the same tooling work.
- `senv.doskey` is staged and outside Step 3's plan file list, but it required no action from me. It is a pre-existing environment change swept in by the repository-wide handoff, and the commit plan already isolates it in its own `chore(env)` group with an honest subject, which is what the grouping rule requires.
- The `git diff --cached --check` finding in the new package marker is inside Step 3 and would be trivial to change, but the same shape is already committed in the Step 2 package marker, so altering only the new one would introduce an inconsistency without settling the convention. I report it and leave the choice to the writer rather than making a silent local decision.

### Writer instructions for step 3 commit-plan-check (exchange 1) (round 1)

The gate implementation is good work and needs no rework. Do not touch the enforcement order, the typed input invariant, the new test leaf, or the risk-band file, all of which are correct.

Fence the embedded commit-plan human block so the transcript stops breaking Markdown. In `_CodeReviewEvidence.summary()`, the `render_human(self.commit_plan_result)` output is currently appended as bare Markdown, so any staged path containing a dunder is parsed as underscore-strong emphasis and the transcript fails MD050. Wrap that block in a fenced code span, which is also the honest representation, since the content is command output rather than prose. The paired JSON projection is already fenced in the request, so this brings the human projection into line with it rather than inventing a new convention.

Move the assertion that currently pins the unfenced shape. `tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py` asserts `"commit_plan_result:\n\nstate: valid\nready: true" in rendered.transcript_summary`, which encodes exactly the form that breaks. Update it to assert the fenced shape. Keep the change inside the shared-fixture and parity budget that Q04 sets for that file; the file is already 568 lines against a 560 advisory, so this is a place to substitute rather than add.

Add a regression case that would fail without the fence. The most direct one is a commit-plan result whose `staged_paths` include a dunder path such as `tests/unit/tools/test_x/__init__.py`, asserting that the rendered transcript summary keeps that path inside a fence. Put it in the dedicated leaf rather than the risk-band file. Without such a case the gate returns to depending on whether a given round happens to stage a dunder path, which is exactly how this reached round one unnoticed.

Re-run `ghog day --force` after the fix and correct the recorded evidence. The round-one assessment and the validation plan both state that the walk passed the full suite and the duration gate. My forced walk stopped at the check phase with `exit=1`, so it never reached them. Once the fence lands, re-run and record the result that actually reproduces.

Consider restoring `git diff --cached --check` to the resolved validation set. It was request-sourced for Step 1 and has been absent since, and it currently reports `tests/unit/tools/test_code_review_request_commit_plan/__init__.py:2: new blank line at EOF`. The finding is small and matches the shape Step 2 already committed, so fixing the file is optional; restoring the command is the part worth doing, because this exchange used to carry that evidence and silently stopped.

Consider normalizing the line endings in `tools/code_review_request.py`. Its committed blob is uniformly CRLF at 497 line breaks, while the staged blob is mixed at 449 CRLF and 103 bare LF, so about a hundred lines appear in the diff with no textual change. Its sibling modules in `tools/` are LF, and the repository declares no end-of-line policy in `.gitattributes`, so nothing is violated. Normalizing the file to LF would converge it with its siblings and make this step's diff show only real changes. This is a judgement call and I am not requesting it.

One wording nit that needs no round of its own. The round-one request rendered `Writer response: Writer response: None for round 1.` because the authored file opens with the same label the renderer prepends. Dropping the label from the authored text removes the duplication.

Two items remain deferred by agreement rather than dropped. The label-inlining defect still affects `tools/spec_review_answer.py`, `tools/spec_review_request.py`, `tools/code_review_request.py`, and `tools/code_review_answer.py`, with the correct idiom already at `tools/code_review_answer.py:288`. Now that Step 3 has landed its changes to `tools/code_review_request.py`, the collision risk I raised in earlier rounds is largely spent, so this is a reasonable moment to schedule that work. The unimplemented caller-authored heading contract in `instructions/review-requestor.md` travels with it.

### Decision rationale for step 3 commit-plan-check (exchange 1) (round 1)

I am publishing `changes-requested`, and I made no repair, so nothing here prevents a commit-ready recommendation in the next round.

This is a disagreement about one consequence of the change, not about the gate design. The requestor assessed Step 3 as fully implemented, and the enforcement work genuinely is. The order is exactly as settled, with tree A captured, one checker call, tree B captured, drift and non-readiness rejected, and both writes reached only afterwards. Q07 option 7B is honored, so non-ready request content is unconstructible rather than merely unreachable. Q04 is honored, with the 550-line risk-band file taking only an import, a shared constant, one builder argument, parity assertions, and a seam helper, while all three new gate cases live in the dedicated leaf. Both advisory variances are recorded accurately, and the commit plan is valid with `senv.doskey` correctly isolated in its own `chore(env)` group.

The blocking reason is that the same change writes command output into a versioned Markdown document without a fence. `_CodeReviewEvidence.summary()` now appends `render_human(self.commit_plan_result)` as bare Markdown, so staged paths containing a dunder are parsed as underscore-strong emphasis. The transcript fails MD050 at two lines, both carrying `test_code_review_request_commit_plan/__init__.py`, and markdown-check is the one failing step inside `ghog check`, which fails the whole walk with `exit=1` before the affected or full phases run.

The evidence gap matters as much as the defect. The round-one assessment and the validation plan both record a walk that passed the full suite, coverage, and the duration gate. My forced walk never reached any of those phases. The Step 3 tests are genuinely green under `ghog single`, so the divergence is confined to the gate as a whole, but no coverage or duration figure exists for this staged state, and one should not be recorded as though it does.

I weighed whether this is disproportionate, because it is two lint findings on a file that is not even staged. It is not disproportionate, for three reasons. The rule is legitimately in force, since `.markdownlint.json` disables only MD013 and constrains MD033, leaving MD050 at its default in exactly the rule set the umbrella adopts. The failure is systemic rather than incidental, because every new test leaf this effort creates contains an `__init__.py`, and the gate stayed green through Steps 1 and 2 only because the human block did not yet reach the transcript. And the transcript is tracked, so the `git add -A` grouping pass at the commit gate would stage a file that fails the repository's own Markdown gate.

I did not repair it, and the reason is scope quality rather than ownership. The file is in Step 3 and the fence itself is a few lines, but the existing renderer test asserts the broken shape verbatim, so the fix must move that assertion, and without a regression case covering a dunder path the gate returns to depending on what a given round happens to stage. That combination is the writer's to land, and a repair of that size would be substantive and could not finish this round regardless.

Two smaller items ride along and neither blocks on its own. `git diff --cached --check` has quietly left the resolved set since Step 1 and currently reports one finding in the new package marker, matching a shape Step 2 already committed. And `tools/code_review_request.py` moved from uniformly CRLF to mixed line endings, putting about a hundred textless lines in the diff; nothing forbids it, and I flag it as a judgement call rather than a request.

One correction to my own earlier advice, since it would otherwise stand unexamined. In the previous two exchanges I recommended sequencing the deferred label-inlining renderer fix after Step 3, because Step 3 modifies `tools/code_review_request.py`. Step 3 has now landed those changes, so that collision risk is largely spent and the work can reasonably be scheduled.

This assessment is advisory and authorizes nothing. Only the human may choose `Commit` or `Rework and review again`.

### Final reviewer decision for step 3 commit-plan-check (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-3-round-1 -->

## Round 2 by requestor - Step 3

- RecordedI : 2026-08-27T10:49:07+02:00
- Exchange: code/code/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
- Implementation step: 3
- Outcome: request

### Review identity for step 3 commit-plan-check (round 2)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
Implementation step: 3
Review round: 2

### Code review evidence for step 3 commit-plan-check (round 2)

request_index_tree: a8c60932205eab12d332a4e0ad8cde8337346c78
resolved_validation_set:

- ghog day (sources: project)
- rg -n -e commit_plan -e check_commit_plan -e request_index_tree -e capture_index_tree -e ready tools/code_review_request.py tests/unit/tools/test_code_review_request tests/unit/tools/test_code_review_request_commit_plan tests/unit/tools/test_code_reviewer_acceptance tests/unit/tools/test_code_review_requestor_acceptance (sources: plan)
- ghog single tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py tests/unit/tools/test_code_review_request_commit_plan/test_code_review_request_commit_plan_tdd.py tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_acceptance_tdd.py tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py (sources: plan)
- commit-plan-check.bat --format json (sources: request)
- git diff --cached --check (sources: request)

commit_plan_result:

```text
state: valid
ready: true
group 1: chore(env): resolve Claude launcher path
group 1 path: senv.doskey
group 2: feat(commit-plan-check): gate review requests
group 2 path: tools/code_review_request.py
group 2 path: tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py
group 2 path: tests/unit/tools/test_code_review_request_commit_plan/__init__.py
group 2 path: tests/unit/tools/test_code_review_request_commit_plan/test_code_review_request_commit_plan_tdd.py
group 2 path: tests/unit/tools/test_code_reviewer_acceptance/fixtures.py
group 2 path: tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_acceptance_tdd.py
group 2 path: tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py
group 2 path: tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py
group 3: docs(commit-plan-check): record step 3 validation
group 3 path: docs/v0.11.0/plan.v0.11.0.commit-plan-check.validation.md
staged path: docs/v0.11.0/plan.v0.11.0.commit-plan-check.validation.md
staged path: senv.doskey
staged path: tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py
staged path: tests/unit/tools/test_code_review_request_commit_plan/__init__.py
staged path: tests/unit/tools/test_code_review_request_commit_plan/test_code_review_request_commit_plan_tdd.py
staged path: tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py
staged path: tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py
staged path: tests/unit/tools/test_code_reviewer_acceptance/fixtures.py
staged path: tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_acceptance_tdd.py
staged path: tools/code_review_request.py
```

### Requestor assessment for step 3 commit-plan-check (round 2)

Step 3 is complete after applying the round-1 repairs.

- Review publication requires a typed, ready commit-plan result captured from
  one index tree.
- Index drift is rejected before any caller-owned output is written.
- The human commit-plan projection is fenced as plain command output, so paths
  containing dunder names cannot be parsed as Markdown emphasis.
- The final detached Groundhog walk completed with zero failures, warnings, or
  expected failures, 100% coverage, and no duration outliers.
- `commit-plan-check.bat --format json` reports `state=valid` and `ready=true`.
- `git diff --cached --check` passes.

### Implementation report for step 3 commit-plan-check (round 2)

Round 1 identified a Markdown integration defect in the new human commit-plan
evidence. The following repairs were applied:

- `tools/code_review_request.py` now encloses `render_human(...)` in a `text`
  fence inside the transcript summary.
- The renderer assertion now pins the fenced shape.
- The dedicated commit-plan test leaf now exercises an `__init__.py` staged
  path and verifies that it remains inside the fence.
- The extra blank line at EOF in the new package marker was removed.
- The validation-plan evidence and file counts were refreshed.
- With explicit user authorization, only the two missing fence delimiters were
  added around the already-versioned round-1 transcript evidence block. Its
  evidence content was not rewritten.

No changes were made to the enforcement order, typed-input invariant, or the
commit-plan grouping contract.

### Change summary for step 3 commit-plan-check (round 2)

The prepared `a.commit` remains valid and covers all ten staged paths in three
groups:

1. `chore(env): resolve Claude launcher path` for `senv.doskey`.
2. `feat(commit-plan-check): gate review requests` for the renderer and its
   unit and acceptance tests.
3. `docs(commit-plan-check): record step 3 validation` for the validation plan.

Round-1 repair work changed the renderer, its tests, the new package marker,
and validation evidence within those existing groups. The code-review
transcript also contains the protocol entries plus the authorized two-line
historical fence repair; it is not part of the staged Step 3 commit plan.

### Writer response for step 3 commit-plan-check (round 2)

Writer response: The round-1 findings are accepted.

The human commit-plan result is now fenced, the existing shape assertion moved
with it, a dunder-path regression was added in the dedicated leaf, and the new
package marker no longer has a trailing blank line. The detached Groundhog walk
was rerun after the repairs and is green. The historical round-1 evidence block
received only its missing fence delimiters under explicit user authorization.

The optional broad line-ending normalization was not performed because it is
outside this focused repair and no repository policy requires it. The narrower
`git diff --cached --check` finding was corrected and the command now passes.

### Reviewer focus for step 3 commit-plan-check (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-3-round-2 -->

## Round 2 by reviewer - Step 3

- Recorded: 2026-08-27T11:01:43+02:00
- Exchange: code/code/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
- Implementation step: 3
- Outcome: answer

### Assessed index identity for step 3 commit-plan-check (exchange 1) (round 2)

Baseline index tree: a8c60932205eab12d332a4e0ad8cde8337346c78

Assessed index tree: a8c60932205eab12d332a4e0ad8cde8337346c78

### Implementation check for step 3 commit-plan-check (exchange 1) (round 2)

Result: Yes. Step 3 has been fully implemented. This reverses my round-one No, and the reversal rests on re-running the failing gate and inspecting the fix rather than on the change summary.

The Markdown defect is genuinely fixed at its cause. `_CodeReviewEvidence.summary()` now encloses the `render_human` output in a `text` fence, which is also the honest representation, since that block is command output rather than prose. The paired JSON projection was already fenced, so the two projections are now consistent.

I confirmed the fix on live output rather than only in the diff. The round-two request that this exchange itself produced carries its `commit_plan_result:` block inside a fenced text block, with `tests/unit/tools/test_code_review_request_commit_plan/__init__.py` sitting literally inside it on two lines. That is the same content shape that failed MD050 in round one, now rendered safely by the fixed code.

The regression test would fail without the fence rather than merely describe it. `test_transcript_fences_dunder_paths_as_command_output` renders a real transcript summary whose staged paths include `tests/unit/tools/test_x/__init__.py`, splits the summary on the fence delimiter, and asserts the dunder path is inside. Without the fence that split raises rather than quietly passing, so the test cannot silently stop protecting the gate.

The assertion that previously pinned the broken shape moved with the fix rather than being deleted. The renderer test now asserts that the transcript summary opens the commit-plan block with a text fence followed by the valid and ready lines, and the risk-band file stayed at 568 lines, so the change was a substitution inside the Q04 budget rather than an addition.

The repository gate now passes end to end. `ghog day --force` completed every phase with `cov=100 outliers=0 excluded=0 exit=0` and reported `Objective reached`, where round one stopped at the static check with `exit=1`. markdown-check reports no finding for the plan, the validation plan, or either review transcript.

The smaller round-one items are also closed. The new package marker now ends without a trailing blank line, and `git diff --cached --check` is restored to the resolved validation set and exits `0`.

The enforcement work I accepted in round one is unchanged and still correct. The order remains tree A, one checker call, tree B, rejection of non-readiness, operational failure, and drift, then construction, rendering, and only then both writes. Q07 option 7B still holds, with `commit_plan_result` required and `__post_init__` refusing a non-ready result. The dedicated leaf still covers direct typed-boundary rejection, exact call order, and the guarantee that a rejected gate creates or changes neither output, and now covers the fence as well.

Both advisory variances are recorded accurately against my own measurements. `tools/code_review_request.py` is 559 lines and the validation plan records it as 14 above its 545-line advisory; the renderer test is 568 and is recorded as eight above its 560-line advisory. Both remain below the 650-line split trigger, and the new leaf at 241 lines is inside its 260-line estimate. That satisfies the plan's shared execution checklist item 8.

Architecture, performance, and feature integrity are unchanged from round one and remain clean. The gate adds two constant-count tree captures around one checker call, the dependency direction still runs one way, and existing envelope validation, paired writes, validation-set resolution, and role-neutral publication are all intact.

Validation plan effects: I made no change to the validation plan. The requestor's rows are now correct and my verdict agrees with theirs, so reviewer mode had nothing to write.

The round-one disagreement is resolved. Their rows record `Yes. Step 3 has been fully implemented.` and my independent assessment now reaches the same verdict, because the Markdown defect is fixed at its cause and the repository gate passes end to end. No `### Missing work for Step 3` section is required, and none is present.

The evidence claim that failed to reproduce in round one now does. The rows record a detached walk completing with `fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0`, and my own forced walk produced exactly that, having reached every phase rather than stopping at the static check.

The girth row is accurate and complete. It records `tools/code_review_request.py` at 559 lines as 14 above its 545-line advisory and the renderer test at 568 as eight above its 560-line advisory, both below the 650-line split trigger, and states that the other touched test files remain inside their estimates. I measured all of them and every figure matches, so the plan's shared execution checklist item 8 is satisfied.

The evidence rows now describe what the code actually does. The projection row states that the human commit-plan result is rendered inside a Markdown-safe text fence, and the focused-verification row names the literal dunder path inside that fence. Both match the implementation and the test I exercised, so neither overstates coverage the way round one's launcher-style claim would have.

The document-level status line is correctly `No, it is not implemented.` Step 4 still reads `Not started`, so no flip was due.

No umbrella row was completed and reviewer mode correctly suppressed that section. The umbrella digest is unchanged at `020d1d67f9a3dca50a2651e6dd7b6717b3f1a7ef5521c5eaf4a27de6e2c3b79c`, confirmed by `umbrella-digest compare` reporting `changed: false`.

### Pre-repair mandatory checks and coverage for step 3 commit-plan-check (exchange 1) (round 2)

The repository gate now passes end to end, and I confirmed it twice rather than once, because round one failed here and a single green sample is what the tool itself warns against trusting.

Both forced walks agree. `ghog day --force` reported `ghog full done fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0` with `Objective reached` on each run, having reached the check, affected, and full phases every time. In round one the same command stopped at the static check with `exit=1` and produced no coverage or duration figure at all, so this is the first Step 3 state with a complete walk behind it.

markdown-check, the step that failed round one, now reports no finding for the plan, the validation plan, or either review transcript. I ran it separately as well as through the walk.

`ghog single` across all five Step 3 test files is green, with nothing failing in focus and nothing passing in focus while failing in the full suite.

Both `rg` forms pass and are equivalent, each returning 119 lines over the same five paths, so the resolved `-e` spelling loses nothing against the plan's alternation.

`commit-plan-check.bat --format json` reports `state=valid`, `ready=true`, ten staged paths, three ordered groups, and zero diagnostics.

`git diff --cached --check` is back in the resolved set and exits `0`, having reported one finding in round one when it was absent from the set and I ran it anyway.

One duration observation that is not a finding and not attributable to this step. The suite's slowest call on both walks is `tests/unit/tools/markdown_check/test_rule_properties/test_rule_properties_pbt.py::test_md001_matches_every_invalid_heading_increment`, measuring `0.47s` and then `0.40s` against the `0.50s` floor. Both are under the floor and `outliers` is zero on both runs, so the gate is genuinely green. The `0.47s` sample sits within six percent of the floor, which is the margin the tool describes as prone to flapping. The test is a pre-existing property-based test belonging to the Markdown checker rather than to Step 3, and nothing in this step made it slower, so I record it as a watch item for whoever owns that suite rather than as work for this round.

I performed no repair, so there is no pre-repair versus post-repair difference beyond this baseline.

### Resolved validation set and sources for step 3 commit-plan-check (exchange 1) (round 2)

The request resolved five commands and I ran all five. The current plan-derived
resolver set adds nothing, so the union equals the resolved set.

- `ghog day` — source `project`. Run as `ghog day --force`, twice, because a
  plain invocation short-circuits to `cov=skipped` and because round one failed
  in this command's first phase.
- `rg -n -e commit_plan -e check_commit_plan -e request_index_tree -e capture_index_tree -e ready tools/code_review_request.py tests/unit/tools/test_code_review_request tests/unit/tools/test_code_review_request_commit_plan tests/unit/tools/test_code_reviewer_acceptance tests/unit/tools/test_code_review_requestor_acceptance` — source `plan`.
- `ghog single tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py tests/unit/tools/test_code_review_request_commit_plan/test_code_review_request_commit_plan_tdd.py tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_acceptance_tdd.py tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py` — source `plan`.
- `commit-plan-check.bat --format json` — source `request`.
- `git diff --cached --check` — source `request`, restored this round.

Every command ran and every command passed.

Both forced walks completed every phase with `cov=100 outliers=0 excluded=0
exit=0` and `Objective reached`.

Both `rg` spellings return exactly 119 matching lines, so the resolved form and
the plan's alternation are equivalent.

`ghog single` over all five Step 3 test files is green.

`commit-plan-check.bat --format json` reports `state=valid`, `ready=true`, ten
staged paths, three ordered groups, and no diagnostics.

`git diff --cached --check` exits `0`. Its restoration closes the quiet
narrowing I reported in round one, when it had been absent since Step 1 and
reported a real finding once I ran it unprompted.

### Resolver drift and direction for step 3 commit-plan-check (exchange 1) (round 2)

No drift this round.

The `rg` command carries every parity term. I ran both the resolved `-e`
spelling and the plan's quoted alternation at
`docs/v0.11.0/plan.v0.11.0.commit-plan-check.md:580`, and each returns exactly
119 matching lines over the same five paths, so the two forms are equivalent.

`ghog single` is present with the plan's exact five-file list for this step.

`git diff --cached --check` is restored to the resolved set from the `request`
source, which closes the quiet narrowing I reported in round one. It now exits
`0`, because the trailing blank line in the new package marker was removed.

Comparing the round-two request set against the current plan-derived resolver
set, the union adds nothing, so I ran the resolved set as given.

### Repository state around validation for step 3 commit-plan-check (exchange 1) (round 2)

My assessment produced no repository side effect. I made no repair, so the only writes were ignored root `a.*` reviewer evidence files and ignored validation artifacts.

Index identity held throughout. The request-time `request_index_tree` is `a8c60932205eab12d332a4e0ad8cde8337346c78`, and `capture-index-tree` returned that identical value both before assessment and after two forced walks, the focused run, and the Markdown gate. No early rejection applied and no staged change occurred during review.

The umbrella is untouched. `umbrella-digest compare` returns `020d1d67f9a3dca50a2651e6dd7b6717b3f1a7ef5521c5eaf4a27de6e2c3b79c` before and after with `changed: false`.

The validation-state comparison is clean. Using the same ordered ten-path set before and after, `validation-state compare` returns `acceptable: true` with empty `tracked_paths`, `untracked_paths`, and `ignored_paths`.

The staged set is unchanged in membership from round one. The same ten paths are staged; the round-one repairs changed content inside three already-staged paths and the validation record without adding or removing any path.

Ignored validation artifacts were refreshed as expected by the two walks, including `.coverage`, `.testmondata`, `a.ghog.log`, and `a.ghog.outliers`. The contract accepts differences confined to ignored validation artifacts, and none is tracked or staged.

One tracked path outside the staged set is modified, and its state is now correct rather than defective. `docs/v0.11.0/review.code.v0.11.0.commit-plan-check.md` carries the appended Step 3 rounds plus the two authorized fence delimiters around the round-one evidence block. It remains unstaged while the round is open. Unlike round one, it now passes the repository's Markdown gate, so the `git add -A` grouping pass at the commit gate would stage a clean file.

I verified that the historical content inside those delimiters was not rewritten. The round-one block still carries `request_index_tree: 20f249d9c5a8a5bdb1aaf863be0f90d8ab45460b` with the same three groups and ten staged paths I assessed in round one.

### Repair inventory for step 3 commit-plan-check (exchange 1) (round 2)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 3 commit-plan-check (exchange 1) (round 2)

`a.commit` is accurate, and I verified it with the shipped checker rather than by reading it. `commit-plan-check.bat --format json` returns `state=valid`, `ready=true`, ten staged paths, three ordered groups, and zero diagnostics.

Membership, grouping, order, and subjects are unchanged from round one and still correct:

- Group 1 `chore(env): resolve Claude launcher path` carries `senv.doskey` alone.
- Group 2 `feat(commit-plan-check): gate review requests` carries `tools/code_review_request.py` and the seven Step 3 test paths.
- Group 3 `docs(commit-plan-check): record step 3 validation` carries the validation plan alone and is the final commit.

The round-one repairs landed inside the existing groups rather than reshaping them, which is the right outcome. The fence change touched the renderer, its tests, and the new package marker, all already members of group 2, and the refreshed evidence stayed in group 3. No group boundary, order, or subject needed to move, and none did.

Isolating `senv.doskey` in its own `chore(env)` group remains correct. It is a pre-existing environment change swept in by the repository-wide handoff, ranked by its own dependencies and given an honest subject rather than being folded into the feature commit.

Ordering is least to most dependent: the unrelated environment change, then the feature that does not depend on it, then the validation record that documents that feature. All three subjects are conventional commits with accurate scopes.

I did not amend `a.commit`. Membership, ordering, scope, and subjects are all accurate, so an amendment would have been a substantive change to commit grouping with no defect to correct, and it would have invalidated a commit-ready recommendation in this same round.

The round-one carry-forward is now discharged rather than merely noted. The transcript `docs/v0.11.0/review.code.v0.11.0.commit-plan-check.md` is still tracked, still modified, and still correctly unstaged while the round is open, so the `git add -A` grouping pass at the commit gate will stage it. Because the historical block was fenced and the renderer fixed, that pass now stages a file that passes the repository's Markdown gate, which was not true in round one.

### Findings and boundaries for step 3 commit-plan-check (exchange 1) (round 2)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 3 commit-plan-check (exchange 1) (round 2)

No change is required. Every round-one item is addressed and I am requesting nothing further.

Do not rework Step 3. The enforcement order, the typed-input invariant, the fence fix, the moved assertion, the dunder regression test, and the commit grouping are all correct as they stand.

Two things are worth keeping deliberately, so a later cleanup does not undo them. The text fence in `_CodeReviewEvidence.summary()` is load-bearing rather than cosmetic: without it any staged dunder path breaks the versioned transcript and the repository gate. And `test_transcript_fences_dunder_paths_as_command_output` is what keeps that true, since it splits on the fence delimiter and therefore fails hard rather than silently if the fence is removed.

One judgement call was declined and I agree with the reasoning. The optional line-ending normalization of `tools/code_review_request.py` was not performed because it is outside this focused repair and no repository policy requires it. That is a fair call; the file remains mixed and the diff still carries about a hundred textless lines, which is a cost worth paying only when someone chooses to normalize it deliberately.

One duration item to hand on rather than act on now. The suite's slowest call is `tests/unit/tools/markdown_check/test_rule_properties/test_rule_properties_pbt.py::test_md001_matches_every_invalid_heading_increment`, measuring `0.47s` and `0.40s` against the `0.50s` floor across my two walks. It is under the floor and unrelated to Step 3, so nothing is due here, but the `0.47s` sample is close enough that it may surface as an outlier in a later step's walk. If it does, `instructions/fix_slow_test.md` is the route, and it belongs to the Markdown-checker suite rather than to this effort.

Two items remain deferred by agreement rather than dropped. The label-inlining defect affects `tools/spec_review_answer.py`, `tools/spec_review_request.py`, `tools/code_review_request.py`, and `tools/code_review_answer.py`, with the correct idiom already at `tools/code_review_answer.py:288`. Step 3 has now landed its changes to `tools/code_review_request.py`, so the collision risk that justified deferring this is largely spent and it can reasonably be scheduled. The unimplemented caller-authored heading shift and qualification contract in `instructions/review-requestor.md` travels with it.

At the commit gate, the `git add -A` grouping pass will stage `docs/v0.11.0/review.code.v0.11.0.commit-plan-check.md`, which carries this exchange's rounds and the authorized fence repair. Unlike round one, that file now passes the Markdown gate, so staging it is safe.

If the human selects `Commit`, run the existing commit step. If the human selects `Rework and review again`, there is no outstanding scope from me; treat any human guidance as the full scope of that round.

### Decision rationale for step 3 commit-plan-check (exchange 1) (round 2)

I am recommending `commit-ready`, and I made no repair in either round, so nothing in this exchange invalidates the recommendation.

All six readiness-floor results pass. Identity is exact, with the envelope, human-readable identity, plan, step, round, and exchange occurrence in agreement and the request-time index tree `a8c60932205eab12d332a4e0ad8cde8337346c78` matching the live index before and after all validation. Implementation completeness is now a Yes, reversing my round-one No. Mandatory validation and coverage pass, confirmed twice. Staged attribution is clean across the same ten paths. No unresolved finding remains against this step. The `a.commit` grouping is valid with zero diagnostics.

The reversal is earned by re-running the gate that failed, not by reading the change summary. Round one stopped at the static check with `exit=1` and produced no coverage or duration figure at all. Both walks this round completed every phase with `cov=100 outliers=0 excluded=0 exit=0` and `Objective reached`, and markdown-check, the single failing step in round one, now reports nothing.

The fix addresses the cause rather than the symptom. Fencing the `render_human` output in `_CodeReviewEvidence.summary()` removes Markdown parsing from that block entirely, which is also the honest representation for command output and brings the human projection into line with the already-fenced JSON one. I confirmed it on live output: the round-two request this exchange produced carries its dunder paths literally inside a text fence.

The regression test can fail for the reason it exists, which is the property I asked for. `test_transcript_fences_dunder_paths_as_command_output` renders a real summary containing `tests/unit/tools/test_x/__init__.py` and splits on the fence delimiter, so without the fence it raises rather than quietly passing. The assertion that previously pinned the broken shape moved with the fix instead of being deleted, and the risk-band file stayed at 568 lines, so Q04's budget was respected by substitution rather than addition.

One action needs the human's eye at this gate, and I would rather name it than let it pass as routine. The writer added two fence delimiters to the already-versioned round-one evidence block inside the review transcript, stating that this was done under explicit user authorization. I verified the change is minimal and content-preserving: the historical `request_index_tree: 20f249d9c5a8a5bdb1aaf863be0f90d8ab45460b`, the same three groups, and the same ten staged paths all survive unaltered inside the new delimiters. I cannot independently confirm the authorization, since no human input reached me during this exchange, and I record that limit rather than implying I checked it. The action was also necessary rather than convenient, because the code fix changes only future renderings and the historical block would otherwise have kept the gate red permanently.

Two smaller round-one items are closed. The new package marker no longer carries a trailing blank line, and `git diff --cached --check` is restored to the resolved set and exits `0`, closing the quiet narrowing I reported.

One duration observation is deliberately not a finding. The suite's slowest call on both walks is a pre-existing Markdown-checker property test, measuring `0.47s` and `0.40s` against a `0.50s` floor. Both are under the floor with zero outliers, so the gate is genuinely green, but the first sample sits within six percent of it. Nothing in Step 3 made that test slower, so I record it as a watch item for its owners rather than work for this round.

Two items remain deferred by agreement, and the human should see them here. The label-inlining defect still affects `tools/spec_review_answer.py`, `tools/spec_review_request.py`, `tools/code_review_request.py`, and `tools/code_review_answer.py`, with the correct idiom already at `tools/code_review_answer.py:288`, and the unimplemented caller-authored heading contract in `instructions/review-requestor.md` travels with it. As I noted in round one, Step 3 has now landed its changes to `tools/code_review_request.py`, so the collision risk that justified deferring the work is largely spent and it can reasonably be scheduled. Neither is caused by Step 3, and I classify both as tracked future work rather than unresolved findings against it.

This recommendation is advisory and authorizes nothing. Only the human may choose `Commit` or `Rework and review again`.

### Final reviewer decision for step 3 commit-plan-check (exchange 1) (round 2)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-3-round-2 -->

## Round 2 by human - Step 3 - human-confirmation

- Recorded: 2026-08-27T13:10:03+02:00
- Exchange: code/code/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
- Implementation step: 3
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->

## Round 1 by requestor - Step 4

- Recorded: 2026-08-27T14:52:14+02:00
- Exchange: code/code/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
- Implementation step: 4
- Outcome: request

### Review identity for step 4 commit-plan-check (round 1)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
Implementation step: 4
Review round: 1

### Code review evidence for step 4 commit-plan-check (round 1)

request_index_tree: 9fcd0968a43c8f20c826f67e9f1927a67b746eaf
resolved_validation_set:

- ghog day (sources: project)
- rg -n -e commit-plan-check -e status -e readiness -e never.authorizes -e independent instructions/code-reviewer.md instructions/group-commits-msg.md tests/unit/tools/test_code_reviewer_instruction tests/unit/tools/test_group_commit_message_prompt_tdd.py tests/acceptance/commit_plan_check (sources: plan)
- ghog single tests/unit/tools/test_code_reviewer_instruction/test_code_reviewer_instruction_tdd.py tests/unit/tools/test_group_commit_message_prompt_tdd.py tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_acceptance_tdd.py (sources: plan)
- commit-plan-check.bat --format json (sources: request)
- git diff --cached --check (sources: request)

commit_plan_result:

```text
state: valid
ready: true
group 1: chore(editor): add workflow vocabulary
group 1 path: .vscode/settings.json
group 2: docs(commit-plan-check): fix format example
group 2 path: docs/v0.11.0/design.v0.11.0.commit-plan-check.md
group 3: docs(commit-plan-check): wire readiness checks
group 3 path: instructions/code-reviewer.md
group 3 path: instructions/group-commits-msg.md
group 4: test(commit-plan-check): cover readiness rollout
group 4 path: tests/acceptance/commit_plan_check/__init__.py
group 4 path: tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/__init__.py
group 4 path: tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_acceptance_tdd.py
group 4 path: tests/unit/tools/test_code_review_requestor_instruction/test_implement_step_integration_tdd.py
group 4 path: tests/unit/tools/test_code_reviewer_instruction/test_code_reviewer_instruction_tdd.py
group 4 path: tests/unit/tools/test_group_commit_message_prompt_tdd.py
group 4 path: tests/unit/tools/test_instruction_structure/test_consolidation_commit_contract_tdd.py
group 5: docs(commit-plan-check): record step 4 validation
group 5 path: docs/v0.11.0/draft.v0.11.0.review-mode.md
group 5 path: docs/v0.11.0/plan.v0.11.0.commit-plan-check.validation.md
staged path: .vscode/settings.json
staged path: docs/v0.11.0/design.v0.11.0.commit-plan-check.md
staged path: docs/v0.11.0/draft.v0.11.0.review-mode.md
staged path: docs/v0.11.0/plan.v0.11.0.commit-plan-check.validation.md
staged path: instructions/code-reviewer.md
staged path: instructions/group-commits-msg.md
staged path: tests/acceptance/commit_plan_check/__init__.py
staged path: tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/__init__.py
staged path: tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_acceptance_tdd.py
staged path: tests/unit/tools/test_code_review_requestor_instruction/test_implement_step_integration_tdd.py
staged path: tests/unit/tools/test_code_reviewer_instruction/test_code_reviewer_instruction_tdd.py
staged path: tests/unit/tools/test_group_commit_message_prompt_tdd.py
staged path: tests/unit/tools/test_instruction_structure/test_consolidation_commit_contract_tdd.py
```

### Requestor assessment for step 4 commit-plan-check (round 1)

Step 4 is fully implemented.

- Scope: the code-reviewer and commit-grouping instructions independently run the JSON commit-plan checker and handle statuses 0, 3, and 2 without treating mechanical readiness as commit authority.
- Tests: the planned unit instruction contracts and real-Git acceptance suite pass, including valid, missing, empty, mismatched, renamed, failed, redirected, immutable, and requestor-drift cases.
- Static checks and coverage: the final detached Groundhog run completed with no failures, warnings, expected failures, coverage gaps, or duration outliers.
- Architecture: the rollout reuses the existing checker launchers and review request renderer; no parallel validation implementation was introduced.
- Performance: the requestor-rejection test moved repository setup into its fixture after profiling found the measured call dominated by Git ignore probes. Its setup is reported separately and the measured call stays below the duration floor.
- Feature integrity: the implementation-check record marks Step 4 fully implemented and the umbrella row links the completed requirement and validation plan.

### Implementation report for step 4 commit-plan-check (round 1)

Step 4 completes the commit-plan-check rollout at the review and commit boundaries.

- `instructions/code-reviewer.md` adds an independent JSON checker call to the six-part readiness floor, branches on all three statuses, and states that success is mechanical evidence rather than authority.
- `instructions/group-commits-msg.md` runs the read-only checker after staging and formatting, repairs status 3, stops on status 2, and reaches its menu only on status 0.
- The acceptance suite exercises both launchers and both formats in real repositories while comparing repository state before and after each read-only call.
- Unit instruction contracts cover the new reviewer and grouping sequence plus requestor and consolidation compatibility.
- The validation plan records the implementation, performance investigation, and successful global gate; the umbrella row is completed.

### Change summary for step 4 commit-plan-check (round 1)

The staged index contains 13 paths organized by the prepared `a.commit` into five ordered groups.

1. `chore(editor): add workflow vocabulary`
   - `.vscode/settings.json`
2. `docs(commit-plan-check): fix format example`
   - `docs/v0.11.0/design.v0.11.0.commit-plan-check.md`
3. `docs(commit-plan-check): wire readiness checks`
   - `instructions/code-reviewer.md`
   - `instructions/group-commits-msg.md`
4. `test(commit-plan-check): cover readiness rollout`
   - the three acceptance package and test paths under `tests/acceptance/commit_plan_check/`
   - the four affected instruction-contract test paths under `tests/unit/tools/`
5. `docs(commit-plan-check): record step 4 validation`
   - `docs/v0.11.0/draft.v0.11.0.review-mode.md`
   - `docs/v0.11.0/plan.v0.11.0.commit-plan-check.validation.md`

The JSON readiness checker reports `state=valid`, `ready=true`, and no diagnostics for this exact staged inventory.

### Writer response for step 4 commit-plan-check (round 1)

Writer response: This is the first code-review round for Step 4. There is no earlier reviewer feedback or disagreement to record.

### Reviewer focus for step 4 commit-plan-check (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-4-round-1 -->

## Round 1 by reviewer - Step 4

- Recorded: 2026-08-27T15:05:53+02:00
- Exchange: code/code/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
- Implementation step: 4
- Outcome: answer

### Assessed index identity for step 4 commit-plan-check (exchange 1) (round 1)

Baseline index tree: 9fcd0968a43c8f20c826f67e9f1927a67b746eaf

Assessed index tree: 9fcd0968a43c8f20c826f67e9f1927a67b746eaf

### Implementation check for step 4 commit-plan-check (exchange 1) (round 1)

Result: Yes. Step 4 has been fully implemented. This is the effort's final step, and I checked the completion machinery as carefully as the rollout itself, because a wrong umbrella transition would outlive this review.

The reviewer instruction wiring matches the settled design. `instructions/code-reviewer.md` inserts an independent `commit-plan-check.bat --format json` run as step 6, before grouping, ordering, scope, or subjects are assessed, and requires the state, ready value, ordered groups, staged paths, and every diagnostic to be recorded in reviewer evidence. It branches on all three statuses, treats status three as mechanical non-readiness and status two as an untrustworthy decision, and blocks a commit-ready recommendation on either. The added prose states that status zero satisfies only the mechanical `a.commit` result of the six-part readiness floor and never authorizes a commit, which is exactly the boundary the design draws.

The grouping instruction matches it too. `instructions/group-commits-msg.md` runs the checker after formatting and staging, repairs on status three using the returned diagnostics and reruns, stops and reports on status two without presenting choices, and reaches the human menu only on status zero. It states explicitly that this earlier read-only gate does not replace the final batch validation before mutation.

One detail there is worth calling out as correct rather than incidental. The instruction invokes the checker as `"%LLM_SHARED_DIR%\commit-plan-check.bat"` from the project root, which depends on the launcher preserving the caller's working directory. That is precisely the defect I blocked in Step 2 round one, so this usage is only safe because that fix landed, and it now exercises it in the workflow rather than only in tests.

The renumbering consequences were followed through rather than left dangling. Inserting the checker as step 7 shifted the menu to step 8, and both affected contract tests were updated in step: `test_implement_step_integration_tdd.py` now asserts "Steps 1 through 7" and `test_consolidation_commit_contract_tdd.py` asserts "Steps 1 through 7" and "do not present the Step 8 menu". Those two files are outside the plan's Step 4 list, but they are necessary compatibility updates rather than scope creep.

The acceptance suite covers every row of the design's acceptance table. The parameterized fixture runs valid, missing-plan, empty-plan, empty-staged-set, and mismatch scenarios across both adapters and both formats, which is four runs per scenario. Separate tests cover the staged rename with both sides, the failed Git inventory with a stable operational diagnostic, caller-owned redirection as the only observable change, and requestor rejection on both invalid plan and index drift with no outputs written. The reviewer-rerun row is covered by the instruction contract test.

The immutability proof matches what the design demands. `_RepositoryState` snapshots `head`, `index_tree`, `staged_paths`, `worktree_diff`, `plan_bytes`, and `ignored_root` before and after each call, which is the exact set the design names, and the comparison runs for both valid and invalid calls.

The final-step completion machinery is correct in every particular I could check. All four `### Analysis of Step N implementation state` sections now open with the exact Yes sentence, so the document-level line correctly flipped from `No, it is not implemented.` to `Yes, it is implemented.` Umbrella row 8 moved from `pending` to `completed` with the requirement and validation-plan paths filled in, and I re-read both named files: they exist, and the validation plan's first non-title line is `Yes, it is implemented.` Row order, type, key title, and slug are unchanged, rows 9 and 10 are untouched, and the requirement-detail subsections are unmodified.

The design-document edit is a Markdown repair rather than a design change. `--format human|json` inside a table cell splits that cell on the unescaped pipe, and the change to `human/json` restores the table. I note the accuracy cost separately, but nothing about Q03's decision, its integration point, or its rejected alternatives changed.

Line budgets are all accounted for. `instructions/code-reviewer.md` at 223 lines is inside its 225 advisory, and the two overruns are recorded as the plan's shared checklist item 8 requires: `instructions/group-commits-msg.md` at 169 lines is 34 above its 135 advisory, and the acceptance leaf at 418 lines is 38 above its 380 advisory and well below the 550-line helper-extraction trigger, so no `conftest.py` split is due.

Architecture, performance, and feature integrity are clean. The rollout adds no parallel validation implementation, reusing the shipped launcher and the existing request renderer. The instructions add one bounded command call rather than a scan or poll. Existing batch execution still validates before mutation, and the reviewer and grouping roles keep their distinct authority boundaries.

Validation plan effects: I made no change to the validation plan. The requestor's rows are correct and my verdict agrees with theirs, so reviewer mode had nothing to write.

The recorded rows state `Yes. Step 4 has been fully implemented.` and my independent assessment reaches the same verdict, so no `### Missing work for Step 4` section is required and none is present.

The document-level status flip is correct and I verified its precondition rather than assuming it. All four `### Analysis of Step N implementation state` sections now open with the exact `Yes. Step N has been fully implemented.` sentence, so the opening line rightly moved from `No, it is not implemented.` to `Yes, it is implemented.` This is the one step in the effort where that flip was due, and it happened here rather than early.

The girth row is accurate and complete against my own measurements, and it records both overruns as the plan's shared execution checklist item 8 requires. `instructions/code-reviewer.md` at 223 lines is inside its 225-line advisory. `instructions/group-commits-msg.md` at 169 lines is recorded as 34 above its 135-line advisory. The acceptance leaf at 418 lines is recorded as 38 above its 380-line advisory and below the 550-line helper-extraction trigger, so no `conftest.py` split is due and none was made.

The evidence rows describe what the code and instructions actually do rather than what was intended. The scope, tests, architecture, performance and feature-integrity entries each match something I checked directly, including the acceptance suite's scenario list and the reviewer and grouping status branches.

One row records a performance investigation rather than a bare result, which is the right shape. The requestor-rejection test moved its repository setup into a fixture after profiling attributed the measured call to Git ignore probes, and the setup cost is reported separately. That is the same technique `instructions/fix_slow_test.md` prescribes and that Step 1 used, applied with a stated cause rather than by trial.

Reviewer mode correctly did not complete the umbrella row itself. The writer completed it, which is the writer-owned behavior for a final step, and my role was to verify it rather than perform it. The umbrella digest is unchanged across my assessment at `dea13b3adfb5027e4bb2d826619634049e044befb09319a142ed2c9dbcb0a353`, confirmed by `umbrella-digest compare` reporting `changed: false`, so nothing I did altered it.

### Pre-repair mandatory checks and coverage for step 4 commit-plan-check (exchange 1) (round 1)

The repository gate passes with margin, and I ran it twice because this is the effort's final step and the umbrella transition rides on it.

Both forced walks agree. `ghog day --force` reported `ghog full done fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0` with `Objective reached` on each run, reaching the check, affected, and full phases every time.

The static check phase passes cleanly, which matters here because it is where Step 3 round one failed. `ghog check done ... exit=0`, with markdown-check among the passing steps, and I confirmed separately that markdown-check reports no finding for the plan, the design, the validation plan, the umbrella draft, or either review transcript.

The duration axis is comfortable. The slowest call across the two walks is `tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_transcript_identity_tdd.py::test_answer_occurrence_follows_a_restarted_request_without_prior_answer` at `0.38s` and then `0.30s` against the `0.50s` floor, so between 24 and 40 percent below it with zero outliers on both runs. The Markdown property test I flagged as a watch item in Step 3 did not surface in either walk.

`ghog single` across the two instruction contract files and the acceptance leaf is green, with nothing failing in focus and nothing passing in focus while failing in the full suite.

Both `rg` forms pass and are equivalent, each returning 60 matching lines over the same five paths, so the resolved `-e` spelling loses nothing against the plan's alternation.

`commit-plan-check.bat --format json` reports `state=valid`, `ready=true`, thirteen staged paths, five ordered groups, and zero diagnostics.

`git diff --cached --check` exits `0` with no whitespace or conflict-marker finding across the thirteen staged paths.

I performed no repair, so there is no pre-repair versus post-repair difference beyond this baseline.

### Resolved validation set and sources for step 4 commit-plan-check (exchange 1) (round 1)

The request resolved five commands and I ran all five. The current plan-derived
resolver set adds nothing, so the union equals the resolved set.

- `ghog day` — source `project`. Run as `ghog day --force`, twice, because a
  plain invocation short-circuits to `cov=skipped` and because this is the final
  step of the effort.
- `rg -n -e commit-plan-check -e status -e readiness -e never.authorizes -e independent instructions/code-reviewer.md instructions/group-commits-msg.md tests/unit/tools/test_code_reviewer_instruction tests/unit/tools/test_group_commit_message_prompt_tdd.py tests/acceptance/commit_plan_check` — source `plan`.
- `ghog single tests/unit/tools/test_code_reviewer_instruction/test_code_reviewer_instruction_tdd.py tests/unit/tools/test_group_commit_message_prompt_tdd.py tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_acceptance_tdd.py` — source `plan`.
- `commit-plan-check.bat --format json` — source `request`.
- `git diff --cached --check` — source `request`.

Every command ran and every command passed.

Both forced walks completed every phase with `cov=100 outliers=0 excluded=0
exit=0` and `Objective reached`.

Both `rg` spellings return exactly 60 matching lines, so the resolved form and
the plan's alternation are equivalent.

`ghog single` over the two instruction contract files and the acceptance leaf is
green.

`commit-plan-check.bat --format json` reports `state=valid`, `ready=true`,
thirteen staged paths, five ordered groups, and no diagnostics.

`git diff --cached --check` exits `0`.

There is a pleasing symmetry worth recording. The command this effort built is
now part of the evidence set that reviews the effort's own final step, and the
instruction this step wires makes that rerun mandatory for every future code
review rather than a habit I adopted voluntarily from Step 2 onward.

### Resolver drift and direction for step 4 commit-plan-check (exchange 1) (round 1)

No drift this round.

The `rg` command carries every term the plan specifies. I ran both the resolved
`-e` spelling and the plan's quoted alternation at
`docs/v0.11.0/plan.v0.11.0.commit-plan-check.md:726`, and each returns exactly
60 matching lines over the same five paths, so the two forms are equivalent.

`ghog single` is present with the plan's exact three-file list for this step.

`git diff --cached --check` remains in the set from the `request` source, where
it was restored during Step 3 round two after having quietly left the set since
Step 1. It stayed this round, which is the outcome I asked for.

Comparing the request set against the current plan-derived resolver set, the
union adds nothing, so I ran the resolved set as given.

Across the effort the pattern is now settled. Steps 1, 2 and 3 each opened with
a plan-sourced command narrower than the plan text and corrected it in round
two; Step 4 opened correct. Whatever changed in how the set is derived is
working, and it is worth keeping for the remaining umbrella requirements.

### Repository state around validation for step 4 commit-plan-check (exchange 1) (round 1)

My assessment produced no repository side effect. I made no repair, so the only writes were ignored root `a.*` reviewer evidence files and ignored validation artifacts.

Index identity held throughout. The request-time `request_index_tree` is `9fcd0968a43c8f20c826f67e9f1927a67b746eaf`, and `capture-index-tree` returned that identical value both before assessment and after two forced walks, the focused run, the Markdown gate, and every inspection. No early rejection applied and no staged change occurred during review.

The umbrella needs a word of its own this round, because it is staged rather than merely present. `docs/v0.11.0/draft.v0.11.0.review-mode.md` carries the completed row 8 and is part of the reviewed index, which is correct for a final step. My baseline captured it in that state, and `umbrella-digest compare` returns `dea13b3adfb5027e4bb2d826619634049e044befb09319a142ed2c9dbcb0a353` before and after with `changed: false`, so my assessment left it untouched. Reviewer mode never completed or edited that row; the writer did, and I verified the result.

The validation-state comparison is clean. Using the same ordered thirteen-path set before and after, `validation-state compare` returns `acceptable: true` with empty `tracked_paths`, `untracked_paths`, and `ignored_paths`.

Ignored validation artifacts were refreshed as expected by the two walks, including `.coverage`, `.testmondata`, `a.ghog.log`, and `a.ghog.outliers`. The contract accepts differences confined to ignored validation artifacts, and none is tracked or staged.

One tracked path outside the staged set is modified, as in every round of this effort. `docs/v0.11.0/review.code.v0.11.0.commit-plan-check.md` carries the appended Step 4 request and is correctly unstaged while the round is open. It passes the repository Markdown gate, so the `git add -A` grouping pass at the commit gate will stage a clean file.

### Repair inventory for step 4 commit-plan-check (exchange 1) (round 1)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 4 commit-plan-check (exchange 1) (round 1)

`a.commit` is accurate, and I verified it with the checker this effort shipped rather than by reading it. `commit-plan-check.bat --format json` returns `state=valid`, `ready=true`, thirteen staged paths, five ordered groups, and zero diagnostics.

Group membership matches the index exactly:

- Group 1 `chore(editor): add workflow vocabulary` carries `.vscode/settings.json`.
- Group 2 `docs(commit-plan-check): fix format example` carries the design document.
- Group 3 `docs(commit-plan-check): wire readiness checks` carries the two instruction files.
- Group 4 `test(commit-plan-check): cover readiness rollout` carries the three acceptance package paths and the four instruction-contract test paths.
- Group 5 `docs(commit-plan-check): record step 4 validation` carries the umbrella draft and the validation plan.

The grouping decisions are good, and two deserve saying so explicitly. Isolating `.vscode/settings.json` into its own `chore(editor)` group is correct: it is unrelated editor configuration swept in by the repository-wide handoff, and the grouping rule requires ranking it by its own dependencies with an honest subject rather than folding it into the rollout. Separating the design-document Markdown repair into its own `docs` group is also right, since it is a rendering fix rather than part of the readiness wiring and would have been misleading inside group 3.

Placing the umbrella draft beside the validation plan in the final group is required rather than merely tidy. The implementation-check contract states that the umbrella edit belongs in the same grouped commit as the final validation update, so the later feature merge carries the status transition into the integration branch. Group 5 does exactly that, and it is last.

Ordering is least to most dependent throughout: unrelated editor configuration, then an independent documentation repair, then the instruction wiring, then the tests that cover it, then the validation and umbrella record that documents the whole. All five subjects are conventional commits with accurate scopes, and each body describes what its diff actually does.

I did not amend `a.commit`. Membership, ordering, scope, and subjects are all accurate, so an amendment would have been a substantive change to commit grouping with no defect to correct, and it would have invalidated a commit-ready recommendation in this same round.

One carry-forward for the commit gate, unchanged in shape across this effort. `docs/v0.11.0/review.code.v0.11.0.commit-plan-check.md` is tracked, modified, and deliberately unstaged while the round is open, so the `git add -A` grouping pass at the gate will stage it. It currently passes the repository Markdown gate, so staging it is safe.

### Findings and boundaries for step 4 commit-plan-check (exchange 1) (round 1)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 4 commit-plan-check (exchange 1) (round 1)

No change is required. I am requesting nothing, and Step 4 needs no rework.

One optional accuracy point, offered rather than requested. The design-document repair changed `--format human|json` to `--format human/json` inside a table cell. The repair is warranted, because an unescaped pipe splits the cell, but the replacement no longer matches the CLI's real syntax, and the design is the document later readers will treat as reference. Escaping the pipe as `human\|json` renders as `human|json` and keeps both the table and the accuracy. Apply it or leave it; it does not need another round.

Two things are worth keeping deliberately, so a later cleanup does not undo them. The grouping instruction invokes the checker through `%LLM_SHARED_DIR%` from the caller's project root, which is only correct because the Step 2 launcher preserves the caller's working directory; anyone tempted to "simplify" either side should read the Step 2 round-one findings first. And the acceptance suite's `_RepositoryState` snapshot fields are the exact set the design requires for its immutability proof, so trimming them would silently weaken that proof.

Two items remain deferred by agreement rather than dropped, and this is a good moment to schedule them. The label-inlining defect affects `tools/spec_review_answer.py`, `tools/spec_review_request.py`, `tools/code_review_request.py`, and `tools/code_review_answer.py`, with the correct idiom already at `tools/code_review_answer.py:288`. The unimplemented caller-authored heading shift and qualification contract in `instructions/review-requestor.md` travels with it. Both are review-mode tooling work, both are now free of any collision with this effort, and umbrella rows 9 and 10 remain pending as natural homes.

One caution for whoever writes those rounds, learned the hard way in this exchange. Inline triple-backtick runs in authored prose pair with each other across the whole document, so removing one can unbalance the rest and turn two lint findings into many. Write a literal fence marker as a fenced example or describe it in words rather than inlining it.

At the commit gate, the `git add -A` grouping pass will stage `docs/v0.11.0/review.code.v0.11.0.commit-plan-check.md`, which carries this exchange's rounds and currently passes the Markdown gate.

If the human selects `Commit`, run the existing commit step. Note that this commit carries the completed umbrella row, so it is the one that moves requirement 8 to done for the later feature merge. If the human selects `Rework and review again`, there is no outstanding scope from me; treat any human guidance as the full scope of that round.

### Decision rationale for step 4 commit-plan-check (exchange 1) (round 1)

I am recommending `commit-ready`, and I made no repair, so nothing in this round invalidates the recommendation.

All six readiness-floor results pass. Identity is exact, with the envelope, human-readable identity, plan, step, round, and exchange occurrence in agreement and the request-time index tree `9fcd0968a43c8f20c826f67e9f1927a67b746eaf` matching the live index before and after all validation. Implementation completeness is a Yes I derived independently. Mandatory validation and coverage pass, confirmed across two forced walks. Staged attribution is clean across thirteen paths. No unresolved finding remains. The `a.commit` grouping is valid with zero diagnostics.

This is the first step of the effort I am recommending on the first round, and the reason is that the things that blocked earlier rounds were all done correctly here without being asked. The evidence claim reproduces rather than needing a forced re-run to contradict it. The resolved validation set arrived carrying every plan term rather than a narrowed subset. Both line-budget overruns are recorded under checklist item 8 rather than passed over. The renumbering that inserting a step forced was followed through into both affected contract tests rather than left to fail later.

The rollout matches the design at both boundaries. The reviewer instruction runs the checker independently before assessing anything, records the full result, branches on all three statuses, and states that status zero satisfies only the mechanical `a.commit` part of the readiness floor and never authorizes a commit. The grouping instruction runs it after formatting and staging, repairs on status three, stops on status two, reaches the menu only on status zero, and says plainly that it does not replace the final batch validation.

One detail closes a loop from earlier in this effort. The grouping instruction invokes the checker through `%LLM_SHARED_DIR%` from the caller's project root, which only produces the caller's readiness because the Step 2 launcher preserves the working directory. That was the defect I blocked in Step 2 round one, and this step is what puts the fixed behavior into the workflow rather than only into tests.

The acceptance suite covers every row of the design's table, including the two empty states that must stay distinct and the caller-redirection case, and it proves immutability with exactly the snapshot fields the design names, across both adapters and both formats. That is the evidence the feature is ultimately judged by, and it is complete.

Because this is the final step, I checked the completion machinery as carefully as the rollout. All four step verdicts now read Yes, so the document-level flip to `Yes, it is implemented.` was due. Umbrella row 8 moved from pending to completed with both paths filled in, and I re-read both named files and confirmed the validation plan's first non-title line is `Yes, it is implemented.` Row order, key title, slug, neighbouring rows, and the requirement-detail subsections are untouched. Reviewer mode did not perform that transition; the writer did, and my job was to verify it, which I did.

Two observations carry no request and should not hold up the gate. The design-document edit is a genuine Markdown table repair, since an unescaped pipe splits the cell, but `--format human/json` no longer matches the CLI's actual `--format human|json` syntax; escaping the pipe would have preserved both, and it is worth a moment's thought before the design is read as reference. Separately, the label-inlining defect in the four renderer modules and the unimplemented caller-authored heading contract remain deferred by agreement, are unrelated to Step 4, and now have no remaining collision with planned work in this effort.

I should also record my own error from the previous exchange plainly, since it touched the artifact this step commits. My Step 3 round-two answer introduced MD038 findings into the review transcript through inline fence markers in prose, which failed the gate and was repaired by amending the Step 3 review commit. The transcript now passes, and I verified that before recommending here.

This recommendation is advisory and authorizes nothing. Completing the umbrella row does not commit it, and a green gate is mechanical evidence rather than authority. Only the human may choose `Commit` or `Rework and review again`.

### Final reviewer decision for step 4 commit-plan-check (exchange 1) (round 1)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-4-round-1 -->

## Round 1 by human - Step 4 - human-confirmation

- Recorded: 2026-08-27T17:06:48+02:00
- Exchange: code/code/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
- Implementation step: 4
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-1 -->
