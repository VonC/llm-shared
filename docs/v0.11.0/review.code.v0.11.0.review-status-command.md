# Code review transcript for v0.11.0

- Exchange: code/code/v0.11.0/review-status-command
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-status-command.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor - Step 3

- Recorded: 2026-08-30T18:16:40+02:00
- Exchange: code/code/v0.11.0/review-status-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-status-command.md
- Implementation step: 3
- Outcome: request

### Review identity for step 3 review-status-command (round 1)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.review-status-command.md
Implementation step: 3
Review round: 1

### Code review evidence for step 3 review-status-command (round 1)

request_index_tree: b4252174b8dfb31213ffb38d0cef49c625d6bf12
resolved_validation_set:

- ghog day (sources: project)
- ghog single tests/unit/tools/test_review_status_render/test_review_status_render_tdd.py tests/unit/tools/test_review_status_cli/test_review_status_cli_tdd.py (sources: plan)
- rg -n -e Role: -e Specialization: -e Owner: -e Umbrella: -e schema_version -e=--format -e=--root tools/review_status_render.py tools/review_status_cli.py rvw_status.bat tests/unit/tools/test_review_status_render tests/unit/tools/test_review_status_cli (sources: plan)
- .\commit-plan-check.bat --format json (sources: request)

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(review-status): expose status command
group 1 path: rvw_status.bat
group 1 path: tools/review_status_cli.py
group 1 path: tools/review_status_render.py
group 2: test(review-status): cover command adapters
group 2 path: tests/unit/tools/test_review_status_cli/__init__.py
group 2 path: tests/unit/tools/test_review_status_cli/test_review_status_cli_tdd.py
group 2 path: tests/unit/tools/test_review_status_render/__init__.py
group 2 path: tests/unit/tools/test_review_status_render/test_review_status_render_tdd.py
group 3: docs(review-status-command): record step 3 validation
group 3 path: docs/v0.11.0/plan.v0.11.0.review-status-command.validation.md
staged path: docs/v0.11.0/plan.v0.11.0.review-status-command.validation.md
staged path: rvw_status.bat
staged path: tests/unit/tools/test_review_status_cli/__init__.py
staged path: tests/unit/tools/test_review_status_cli/test_review_status_cli_tdd.py
staged path: tests/unit/tools/test_review_status_render/__init__.py
staged path: tests/unit/tools/test_review_status_render/test_review_status_render_tdd.py
staged path: tools/review_status_cli.py
staged path: tools/review_status_render.py
```

### Requestor assessment for step 3 review-status-command (round 1)

Step 3 is fully implemented with no missing work found by implementation-check.

- Static analysis passes Ty, Pyright, Ruff, Radon, Vulture, file-size,
  Markdown, ShellCheck, and EOF checks.
- The focused renderer and CLI leaves pass all 19 calls.
- The detached Groundhog walk reached `state=done`, `exit=0` with 2,200
  full-suite calls, 100% coverage, and no duration outliers.
- The renderer is a pure projection over `ReviewStatusResult`; the CLI owns one
  root resolution, collection, render, stream decision, and typed status.
- The launcher is exercised as a real Windows process against a controlled
  runtime and preserves caller directory, arguments, `PYTHONPATH`, and status.
- Existing review, workflow, launcher, and documentation behavior remains
  green under the full repository gate.

### Implementation report for step 3 review-status-command (round 1)

Step 3 adds the public `rvw_status` command surface.

- `tools/review_status_render.py` produces labelled human blocks and compact
  Unicode JSON from the immutable normalized result.
- `tools/review_status_cli.py` discovers the caller Git root or validates an
  explicit root, evaluates status once, routes output, and returns `0`, `3`,
  or `2` from the typed outcome.
- `rvw_status.bat` selects the newest installed llm-shared Python without
  changing the caller directory and forwards arguments and process status.
- Renderer and CLI test leaves cover healthy, empty, damaged, and mixed
  evidence, all command outcomes, root failures, direct module execution, and
  the controlled batch adapter.
- The validation plan records the completed implementation-check evidence.

### Change summary for step 3 review-status-command (round 1)

The staged tree contains these eight paths:

- `tools/review_status_render.py`
- `tools/review_status_cli.py`
- `rvw_status.bat`
- `tests/unit/tools/test_review_status_render/__init__.py`
- `tests/unit/tools/test_review_status_render/test_review_status_render_tdd.py`
- `tests/unit/tools/test_review_status_cli/__init__.py`
- `tests/unit/tools/test_review_status_cli/test_review_status_cli_tdd.py`
- `docs/v0.11.0/plan.v0.11.0.review-status-command.validation.md`

The reviewed root `a.commit` has three dependency-ordered groups:

1. `feat(review-status): expose status command`
2. `test(review-status): cover command adapters`
3. `docs(review-status-command): record step 3 validation`

### Writer response for step 3 review-status-command (round 1)

Writer response: This is the first review round. There is no earlier reviewer feedback,
accepted repair, reversal, or disagreement to report.

### Reviewer focus for step 3 review-status-command (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-3-round-1 -->

## Round 1 by human - Step 3 - escalation

- Recorded: 2026-08-30T23:16:50+02:00
- Exchange: code/code/v0.11.0/review-status-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-status-command.md
- Implementation step: 3
- Outcome: escalation

exchange was abandoned while waiting for reviewer

<!-- review-entry-id: escalation-round-1 -->

## Round 1 by human - Step 3 - human-reclaim

- Recorded: 2026-08-31T08:49:12+02:00
- Exchange: code/code/v0.11.0/review-status-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-status-command.md
- Implementation step: 3
- Outcome: human-reclaim

Human decision to resume code review round 1 for step 3 after an abandoned wait.

The recorded escalation was a stopped handoff rather than a failure. The requestor published round 1 for implementation step 3 and entered its bounded wait. No reviewer session was active while that wait ran, so the exchange reached its timeout with the answer still absent and the protocol escalated it with the reason that the exchange was abandoned while waiting for the reviewer.

No cancellation occurred. The coordination record carries status escalated with a cleared lease and a human next actor; it carries no confirmed outcome and no confirmation label, so nothing was cancelled and no human decision was recorded against the round.

No review work was lost and no artifact was damaged. At the moment of this decision the request is present at 7234 bytes, the answer is absent because no reviewer answer was ever published, and the versioned transcript is present at 6091 bytes. That is the intact escalated shape the forced resume requires, and the artifact shape names the reviewer as the actor to resume.

The human reviewed this evidence and directed that the exchange resume in place at the same round rather than being resolved or archived. The reviewer then performs its normal round-one assessment of the staged step 3 implementation and publishes the paired answer through the shared exchange.

This is the second interruption of this kind in this effort and the third live instance of the escalated shape the review-status design now carries acceptance rows for. A returning agent again had to reconstruct identity, round, and responsible role from durable files, and a human again had to authorize a manual forced reclaim. Both are the work the review-status and review-resume requirements exist to remove.

<!-- review-entry-id: human-reclaim-round-1 -->

## Round 1 by reviewer - Step 3

- Recorded: 2026-08-31T09:02:29+02:00
- Exchange: code/code/v0.11.0/review-status-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-status-command.md
- Implementation step: 3
- Outcome: answer

### Assessed index identity for step 3 review-status-command (exchange 1) (round 1)

Baseline index tree: b4252174b8dfb31213ffb38d0cef49c625d6bf12

Assessed index tree: b4252174b8dfb31213ffb38d0cef49c625d6bf12

### Implementation check for step 3 review-status-command (exchange 1) (round 1)

Result: No. Step 3 has NOT been fully implemented. The renderer, the CLI, and the tests are good work, but the staged launcher is not the launcher that was validated, and the difference is behavioral rather than cosmetic.

I drafted this check as a Yes and reversed it when the evidence boundary compared the index against the working tree. That comparison is the only thing in the round that could have caught this, and it is worth saying plainly that reading the working-tree file alone would have led me to approve a defect.

`rvw_status.bat` is staged as added and modified. The staged blob is 942 bytes and its invocation line reads `"%REVIEW_STATUS_PYTHON%" -m tools.review_status_cli %*`. The working-tree file is 1397 bytes and reads `"%REVIEW_STATUS_PYTHON%" -P -m tools.review_status_cli %*`, together with the six-line comment explaining why the flag is required. The `-P` fix and its rationale exist only in the working tree and were never staged, so the commit would ship the version without them.

That difference is not stylistic. I verified the failure it causes. From a directory containing its own `tools` package, with `PYTHONPATH` pointing at the shared root, `python -m tools.review_status_cli` without `-P` exits with `No module named tools.review_status_cli`, because the caller's directory is prepended to `sys.path` ahead of `PYTHONPATH` and shadows the shared package. With `-P` the same invocation resolves correctly while the working directory stays with the caller. So the staged launcher fails exactly where the settled Q12 decision requires it to work, in a consuming project that happens to define a `tools` package.

The green gate does not contradict this, and the reason is worth recording. The launcher test copies `project_root / "rvw_status.bat"`, which is the working-tree file, so it exercises the unstaged fix rather than the staged blob. Every launcher assertion passes against a file that is not what would be committed. That is inherent to testing a repository file by path rather than by index content, not a defect in the test, but it means the suite cannot detect this class of divergence and the reviewer's index-versus-worktree comparison is the only guard.

Everything else in the step is correct, and I verified it rather than assuming.

The renderer and CLI match the settled design. The human report prints `Umbrella`, `Implementation step`, `Role`, `Specialization`, and `Owner` as separate labelled fields with `none` as the explicit umbrella fallback, and the lease block carries the renewal and expiry timestamps option E1 requires. The CLI exposes `--root` and `--format human|json` defaulting to human, and maps outcomes to the settled zero, three and two statuses.

Root resolution is correct and correct for an unobvious reason. `_resolve_root` walks upward from `Path.cwd()` and deliberately does not use `tools._models.find_project_root`, even though the plan's confirmed facts cite that helper. Using it would let the `PRJ_DIR` environment variable override the caller's directory, which is the ambient-state failure the settled Q12 decision exists to prevent. I hit that override myself while probing the sibling command, where it masked the real behavior until I cleared the variable. The deviation is right, and it is undocumented.

The launcher test is otherwise the strongest of its kind here. It builds an installed tree with two dated environments and a stub target, clears `PRJ_DIR`, presets an existing `PYTHONPATH`, runs from a separate caller directory, and asserts working directory, newest-runtime selection, path prepending without discarding the existing entry, argument forwarding, and exit-status forwarding.

Every line budget holds with room: renderer 119 against 220, CLI 101 against 180, launcher 27 against 35, renderer test 230 against 330, CLI test 330 against 330.

The validation plan is accurate for steps 1 through 3 with step 4 not started, and the document-level line correctly stays negative.

One cross-command inconsistency is worth recording though it is outside this step. `review_status_cli._git_marker` uses `(root / ".git").exists()`, which accepts a linked worktree where `.git` is a file, while `commit_plan_check._resolve_root` uses `.is_dir()`, which rejects one. The review-status behavior is the more correct of the two.

Validation plan effects: I made no change to the validation plan. Reviewer mode may write only the reviewed step's rows, and I am reporting a No verdict against the requestor's recorded Yes, so editing their rows underneath them would obscure the disagreement rather than resolve it.

The recorded rows state `Yes. Step 3 has been fully implemented.` My independent assessment is `No. Step 3 has NOT been fully implemented.`, because the staged launcher omits the `-P` flag that the working-tree file carries, and the staged version fails in the consuming-project case the settled Q12 decision exists to serve.

The rows are otherwise accurate against the code I read. The renderer, CLI, and test descriptions match what the modules and tests actually do, and the line figures match my own measurements.

The evidence claim needs one correction rather than rewording. The recorded gate result is real and I reproduced it twice, but it was obtained against the working tree, and the launcher test that supports it copies the working-tree file by path. Once the `-P` fix is staged, the same evidence will describe the committed content; until then it describes something else.

Under the writer-owned contract, a No verdict also requires a `### Missing work for Step 3` section listing each missing element concretely. That section does not exist, which is consistent with the writer having reached a Yes. The work list is a single item and is supplied in my writer instructions so it can be transferred directly if the verdict is revised.

The document-level status line is correctly `No, it is not implemented.` Step 4 still reads `Not started`, so no flip was due regardless of this step's verdict.

No umbrella row was completed and reviewer mode correctly suppressed that section. The umbrella digest is unchanged at `dea13b3adfb5027e4bb2d826619634049e044befb09319a142ed2c9dbcb0a353`, confirmed by `umbrella-digest compare` reporting `changed: false`.

### Pre-repair mandatory checks and coverage for step 3 review-status-command (exchange 1) (round 1)

The gate is green twice over, and it does not cover the defect this round found.

Both forced walks agree. `ghog day --force` reported `ghog full done fail=0
warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0` with `Objective reached`
on each run, reaching the check, affected, and full phases every time.

The check phase now passes, which it did not in the preceding plan review. The
two committed transcript MD032 findings I reported there have been repaired, and
markdown-check reports no finding for this effort's documents.

Duration has comfortable margin. The slowest call across both walks is
`tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_transcript_identity_tdd.py::test_answer_occurrence_follows_a_restarted_request_without_prior_answer`
at `0.36s` and `0.38s` against the `0.50s` floor, with zero outliers.

`ghog single` over the two Step 3 test files is green, with nothing failing in
focus and no focus-versus-suite interaction.

The resolved `rg` command returns 25 matching lines across the renderer, CLI,
launcher, and both test leaves, covering the labelled report fields, the schema
version, and both command flags.

`commit-plan-check.bat --format json` reports `state=valid`, `ready=true`, eight
staged paths, three ordered groups, and no diagnostics.

The limit of that evidence is the point of this round. Every one of those
commands reads the working tree. The launcher test in particular copies
`project_root / "rvw_status.bat"`, so it validates the unstaged file. The
staged blob differs from it in a way that changes behavior, and no command in
the resolved set compares the two. The reviewer's index-versus-worktree
comparison is what surfaced it.

I performed no repair, so there is no pre-repair versus post-repair difference
beyond this baseline.

### Resolved validation set and sources for step 3 review-status-command (exchange 1) (round 1)

The request resolved four commands and I ran all four.

- `ghog day` — source `project`. Run as `ghog day --force`, twice, because a
  plain invocation short-circuits to `cov=skipped`.
- `ghog single tests/unit/tools/test_review_status_render/test_review_status_render_tdd.py tests/unit/tools/test_review_status_cli/test_review_status_cli_tdd.py` — source `plan`.
- `rg -n -e Role: -e Specialization: -e Owner: -e Umbrella: -e schema_version -e=--format -e=--root tools/review_status_render.py tools/review_status_cli.py rvw_status.bat tests/unit/tools/test_review_status_render tests/unit/tools/test_review_status_cli` — source `plan`.
- `.\commit-plan-check.bat --format json` — source `request`.

Every command ran and every command passed.

Both forced walks completed every phase with `cov=100 outliers=0 excluded=0
exit=0` and `Objective reached`. `ghog single` is green. The `rg` command returns
25 matching lines across the renderer, CLI, launcher, and both test leaves.
`commit-plan-check.bat --format json` reports `state=valid`, `ready=true`, eight
staged paths, three ordered groups, and no diagnostics.

I additionally ran two commands outside the resolved set, and both mattered.
`git diff --cached --check` exits `0`. More importantly, the evidence boundary's
`validation-state compare` returned `acceptable: false` for `rvw_status.bat`,
which is how the staged-versus-worktree divergence was found.

That divergence is the reason to read this section carefully. Every command in
the resolved set observes the working tree, and the launcher test copies the
working-tree file by path, so a green result here says nothing about the staged
blob. The resolved set is correct for what it covers; it simply does not cover
index content, and nothing in it could have caught this.

### Resolver drift and direction for step 3 review-status-command (exchange 1) (round 1)

No drift. The resolved rg command matches the plan pattern for this step, and
`ghog single` carries the plan file list. Comparing the request set against the
current plan-derived resolver set, the union adds nothing, so I ran the resolved
set as given.

One observation rather than drift: no command in the set compares index content
with the working tree, which is the gap this round exposed. That is a coverage
boundary of the set rather than a deviation from the plan.

### Repository state around validation for step 3 review-status-command (exchange 1) (round 1)

My assessment produced no repository side effect. I made no repair, so the only writes were ignored root `a.*` reviewer evidence files and ignored validation artifacts.

Index identity held throughout. The request-time `request_index_tree` is `b4252174b8dfb31213ffb38d0cef49c625d6bf12`, and `capture-index-tree` returned that identical value both before assessment and after two forced walks, the focused run, the Markdown gate, and every probe. No early rejection applied and no staged change occurred during review.

The umbrella is untouched. `umbrella-digest compare` returns `dea13b3adfb5027e4bb2d826619634049e044befb09319a142ed2c9dbcb0a353` before and after with `changed: false`.

The validation-state comparison is the finding of this round rather than a formality. Using the same ordered eight-path set before and after, `validation-state compare` returns `acceptable: false` with `rvw_status.bat` in `tracked_paths`. That path is staged as added and modified: the staged blob invokes the module without `-P`, while the working-tree file adds `-P` and a six-line comment explaining why it is required.

I attributed the difference rather than assuming it. No test writes that file; the only reference in the suite is `shutil.copy2(project_root / "rvw_status.bat", launcher)`, which reads it. The divergence is therefore an unstaged writer edit rather than a validation side effect, and the comparison surfaced it because the launcher fix landed in the working tree without reaching the index.

I left the file exactly as found, unstaged and unreverted, which the contract requires and which also preserves the evidence. Staging it would have swept pre-existing unstaged writer work into the index, and reverting it would have destroyed the correct fix.

My probes ran entirely outside the repository. I created a scratch Git repository under the session scratchpad carrying its own `tools` package, ran both launchers and both direct module invocations against it with `PRJ_DIR` cleared, and removed it afterwards. Nothing was written into this project.

Ignored validation artifacts were refreshed as expected by the two walks, including `.coverage`, `.testmondata`, `a.ghog.log`, and `a.ghog.outliers`. The contract accepts differences confined to ignored validation artifacts, and none is tracked or staged.

One untracked path remains outside the staged set. `docs/v0.11.0/review.code.v0.11.0.review-status-command.md` holds this exchange's rounds and is correctly unstaged while the round is open.

### Repair inventory for step 3 review-status-command (exchange 1) (round 1)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 3 review-status-command (exchange 1) (round 1)

`a.commit` is accurate, and I verified it with the shipped checker rather than by reading it. `commit-plan-check.bat --format json` returns `state=valid`, `ready=true`, eight staged paths, three ordered groups, and zero diagnostics.

Group membership matches the index exactly:

- Group 1 `feat(review-status): expose status command` carries `rvw_status.bat`, `tools/review_status_cli.py`, and `tools/review_status_render.py`.
- Group 2 `test(review-status): cover command adapters` carries the two new test leaf initializers and their two test modules.
- Group 3 `docs(review-status-command): record step 3 validation` carries the validation plan alone and is the final commit.

Separating production from tests into groups 1 and 2 is a defensible reading of least-to-most dependent, since the tests depend on the modules they exercise. It differs from the pattern the commit-plan-check effort used, where production and its focused tests shared one feature group, but nothing in the grouping rules requires either shape and both orders are honest about what depends on what.

Ordering is correct: the command, then the tests that cover it, then the validation record that documents both. All three subjects are conventional commits with accurate scopes, and each body describes what its diff does.

I did not amend `a.commit`. Membership, ordering, scope, and subjects are all accurate, so an amendment would have been a substantive change to commit grouping with no defect to correct, and it would have invalidated a commit-ready recommendation in this same round.

One carry-forward for the commit gate, unchanged in shape across this effort. `docs/v0.11.0/review.code.v0.11.0.review-status-command.md` is untracked and holds this exchange's rounds, so the `git add -A` grouping pass at the gate will stage it. It passes the repository Markdown gate, so staging it is safe.

### Findings and boundaries for step 3 review-status-command (exchange 1) (round 1)

Unresolved findings:

- The staged `rvw_status.bat` is not the launcher that was validated, and the version that would be committed carries a reproducible failure. The staged blob is 942 bytes and invokes `"%REVIEW_STATUS_PYTHON%" -m tools.review_status_cli %*`. The working-tree file is 1397 bytes and invokes the same module with `-P`, together with a six-line comment explaining why that flag is required. Git reports the path as added and modified, so the fix and its rationale exist only outside the index.
- The failure is verified rather than inferred. From a directory containing its own `tools` package, with `PYTHONPATH` pointing at the shared root, `python -m tools.review_status_cli` without `-P` exits with `No module named tools.review_status_cli`, because the caller's directory is prepended to `sys.path` ahead of `PYTHONPATH` and shadows the shared package. With `-P` the same invocation resolves correctly while the working directory stays with the caller. The staged launcher therefore fails in exactly the consuming-project case that the settled Q12 caller-root decision exists to serve.
- The passing gate does not cover this, and the reason should be recorded rather than assumed. The launcher test copies `project_root / "rvw_status.bat"`, which resolves to the working-tree file, so every launcher assertion is made against the unstaged fix rather than the staged blob. Testing a repository file by path rather than by index content is normal and is not itself a defect, but it means the suite structurally cannot detect a staged-versus-worktree divergence, and the reviewer's index comparison was the only thing that surfaced it.
- I did not stage the working-tree fix. Staging pre-existing unstaged writer work is forbidden to this role, and doing so would also have converted an unreviewed edit into reviewed content without evidence. The file is left exactly as found, unstaged and unreverted.
- The deliberate avoidance of `tools._models.find_project_root` in `_resolve_root` is correct but undocumented. That helper prefers the `PRJ_DIR` environment variable over the caller's directory, so using it would let ambient environment state redirect the command to another repository, which is the failure the settled Q12 decision exists to prevent. Nothing in the module records why the shared helper was passed over, so a later reader could reasonably replace the hand-rolled upward walk with it and silently reintroduce the override.

Boundary-crossing work: None.

### Writer instructions for step 3 review-status-command (exchange 1) (round 1)

The renderer, the CLI, the tests, and the commit grouping are all correct and need no rework. The requested changes concern what is in the index rather than what is in the working tree.

Stage the `-P` fix and its comment. `rvw_status.bat` is currently staged without them, so the commit would ship a launcher that fails with `No module named tools.review_status_cli` whenever a caller's repository defines its own `tools` package. The working-tree file already contains the correct invocation and the explanatory comment; it simply needs to reach the index. Re-run the commit-plan check afterwards so `a.commit` is validated against the corrected staged content.

Confirm nothing else diverges between index and working tree before republishing. This round found the divergence only because the reviewer compared the two, and the same comparison should be part of the requestor's own pre-publication check rather than a reviewer backstop.

Record why `find_project_root` is not used. `_resolve_root` walks upward from the caller's directory rather than calling `tools._models.find_project_root`, and that is the right choice, because the shared helper prefers the `PRJ_DIR` environment variable and would let ambient environment state redirect the command to another repository. A short comment naming that reason would stop a later reader from replacing the hand-rolled walk with the shared helper and silently reintroducing the override the settled Q12 decision forbids. The plan's confirmed facts cite that helper as an available building block, which makes the substitution more likely rather than less.

Consider whether the launcher test should assert against index content as well as the working-tree file. The current test is strong and I would keep it as it is, since testing the real file by path is what proves the shipped behavior. But nothing in the suite compares the staged blob with the working tree, so this defect class remains invisible to the gate. If that check belongs anywhere it is in the requestor's pre-publication step rather than in a unit test, and I raise it as a question rather than a requested change.

Two smaller items need no action in this step. The cross-command inconsistency where `review_status_cli._git_marker` accepts a linked worktree through `(root / ".git").exists()` while `commit_plan_check._resolve_root` rejects one through `.is_dir()` is worth carrying forward; the review-status behavior is the more correct of the two. And the `a.commit` grouping, which separates production from tests rather than combining them as the previous effort did, is a defensible reading of least-to-most dependent and needs no change.

### Decision rationale for step 3 review-status-command (exchange 1) (round 1)

I am publishing `changes-requested`, and I made no repair, so nothing here prevents a commit-ready recommendation in the next round.

Five of the six readiness-floor results pass. Identity is exact, with the envelope, human-readable identity, plan, step, round, and exchange occurrence in agreement and the request-time index tree matching the live index before and after all validation. Mandatory validation and coverage pass, confirmed across two forced walks. Staged attribution is clean. There are no carried findings. The `a.commit` grouping is mechanically valid with zero diagnostics.

Implementation completeness is the result that fails, and it fails on one file. `rvw_status.bat` is staged as added and modified: the staged blob invokes `python -m tools.review_status_cli` without `-P`, while the working-tree file adds `-P` and the comment explaining why. The fix exists but never reached the index, so the commit would ship the version without it.

I verified the consequence rather than reasoning about it. From a directory carrying its own `tools` package, with `PYTHONPATH` set to the shared root, the staged invocation exits with `No module named tools.review_status_cli`, because the caller's directory is prepended to `sys.path` ahead of `PYTHONPATH`. With `-P` it resolves correctly and the working directory still belongs to the caller. So the staged launcher fails precisely in the consuming-project case that the settled Q12 caller-root decision exists to serve, which is the same class of defect this umbrella already corrected once in `commit-plan-check.bat`.

I want to be explicit that I nearly missed it. I had drafted this check as a Yes on the strength of reading the working-tree launcher, which contains the fix and a clear comment. The evidence boundary's index-versus-worktree comparison is what reversed the verdict, and it is the only thing in the round that could have. The passing gate is not evidence against this finding: every command in the resolved set reads the working tree, and the launcher test copies the repository file by path, so it validated the unstaged version. That is normal test construction rather than a defect, but it means the suite structurally cannot see this divergence.

I did not stage the working-tree fix, and the reason is not timidity. Staging pre-existing unstaged writer work is forbidden to this role, and doing it would also have converted an unreviewed edit into reviewed content without evidence, while destroying the very difference that constitutes the finding. The file is left exactly as found, unstaged and unreverted.

The rest of the step is good work and I said so in detail. The renderer and CLI match the settled design field for field, the launcher test is the strongest of its kind in this repository, and root resolution is correct for an unobvious reason: it deliberately avoids `find_project_root` because that helper would let `PRJ_DIR` override the caller. That reasoning is undocumented, which is why I asked for a comment rather than a change.

One item is worth carrying beyond this step. The requestor's own pre-publication check would have caught this, and a reviewer's index comparison should be a backstop rather than the primary guard. That belongs in the requestor workflow rather than in a unit test, and I raised it as a question rather than a requested change.

This assessment is advisory and authorizes nothing. Only the human may choose `Commit` or `Rework and review again`.

### Final reviewer decision for step 3 review-status-command (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-3-round-1 -->

## Round 2 by requestor - Step 3

- Recorded: 2026-08-31T11:03:57+02:00
- Exchange: code/code/v0.11.0/review-status-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-status-command.md
- Implementation step: 3
- Outcome: request

### Review identity for step 3 review-status-command (round 2)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.review-status-command.md
Implementation step: 3
Review round: 2

### Code review evidence for step 3 review-status-command (round 2)

request_index_tree: 409a5d48d01d2113a1ea0900857121ee5e67e57d
resolved_validation_set:

- ghog day (sources: project)
- ghog single tests/unit/tools/test_review_status_render/test_review_status_render_tdd.py tests/unit/tools/test_review_status_cli/test_review_status_cli_tdd.py (sources: plan)
- rg -n -e Role: -e Specialization: -e Owner: -e Umbrella: -e schema_version -e=--format -e=--root tools/review_status_render.py tools/review_status_cli.py rvw_status.bat tests/unit/tools/test_review_status_render tests/unit/tools/test_review_status_cli (sources: plan)
- .\commit-plan-check.bat --format json (sources: request)

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(review-status): expose status command
group 1 path: rvw_status.bat
group 1 path: tools/review_status_cli.py
group 1 path: tools/review_status_render.py
group 2: test(review-status): cover command adapters
group 2 path: tests/unit/tools/test_review_status_cli/__init__.py
group 2 path: tests/unit/tools/test_review_status_cli/test_review_status_cli_tdd.py
group 2 path: tests/unit/tools/test_review_status_render/__init__.py
group 2 path: tests/unit/tools/test_review_status_render/test_review_status_render_tdd.py
group 3: docs(review-status-command): record step 3 validation
group 3 path: docs/v0.11.0/plan.v0.11.0.review-status-command.validation.md
staged path: docs/v0.11.0/plan.v0.11.0.review-status-command.validation.md
staged path: rvw_status.bat
staged path: tests/unit/tools/test_review_status_cli/__init__.py
staged path: tests/unit/tools/test_review_status_cli/test_review_status_cli_tdd.py
staged path: tests/unit/tools/test_review_status_render/__init__.py
staged path: tests/unit/tools/test_review_status_render/test_review_status_render_tdd.py
staged path: tools/review_status_cli.py
staged path: tools/review_status_render.py
```

### Requestor assessment for step 3 review-status-command (round 2)

Step 3 is fully implemented after accepting the round-one index repair.

- Static analysis passes Ty, Pyright, Ruff, Radon, Vulture, file-size,
  Markdown, ShellCheck, and EOF checks.
- The focused renderer and CLI leaves pass all 19 calls after the repair.
- The new detached Groundhog walk passed static checks, affected tests, and all
  2,200 full-suite calls. Its repository-wide coverage result is 99% only
  because a concurrent, unrelated workstream changed workflow/spec-review
  production files without complete coverage; none belongs to this staged set.
- The renderer is a pure projection over `ReviewStatusResult`; the CLI owns one
  root resolution, collection, render, stream decision, and typed status.
- The launcher is exercised as a real Windows process against a controlled
  runtime and preserves caller directory, arguments, `PYTHONPATH`, and status.
- The Step 3 staged paths have no index-versus-working-tree divergence, and
  `commit-plan-check.bat --format json` remains valid for all eight paths.

### Implementation report for step 3 review-status-command (round 2)

Step 3 adds the public `rvw_status` command surface.

- `tools/review_status_render.py` produces labelled human blocks and compact
  Unicode JSON from the immutable normalized result.
- `tools/review_status_cli.py` discovers the caller Git root or validates an
  explicit root, evaluates status once, routes output, and returns `0`, `3`,
  or `2` from the typed outcome.
- `rvw_status.bat` selects the newest installed llm-shared Python without
  changing the caller directory, uses Python `-P` so a caller-local `tools`
  package cannot shadow llm-shared, and forwards arguments and process status.
- `tools/review_status_cli.py` documents why caller-root discovery deliberately
  avoids the ambient `PRJ_DIR` override in `find_project_root`.
- Renderer and CLI test leaves cover healthy, empty, damaged, and mixed
  evidence, all command outcomes, root failures, direct module execution, and
  the controlled batch adapter.
- The validation plan records the completed implementation-check evidence.

### Change summary for step 3 review-status-command (round 2)

The staged tree contains these eight paths:

- `tools/review_status_render.py`
- `tools/review_status_cli.py`
- `rvw_status.bat`
- `tests/unit/tools/test_review_status_render/__init__.py`
- `tests/unit/tools/test_review_status_render/test_review_status_render_tdd.py`
- `tests/unit/tools/test_review_status_cli/__init__.py`
- `tests/unit/tools/test_review_status_cli/test_review_status_cli_tdd.py`
- `docs/v0.11.0/plan.v0.11.0.review-status-command.validation.md`

The reviewed root `a.commit` has three dependency-ordered groups:

1. `feat(review-status): expose status command`
2. `test(review-status): cover command adapters`
3. `docs(review-status-command): record step 3 validation`

### Human guidance and writer response for step 3 review-status-command (round 2)

Human guidance:

Human decision to resume code review round 1 for step 3 after an abandoned wait.

The recorded escalation was a stopped handoff rather than a failure. The requestor published round 1 for implementation step 3 and entered its bounded wait. No reviewer session was active while that wait ran, so the exchange reached its timeout with the answer still absent and the protocol escalated it with the reason that the exchange was abandoned while waiting for the reviewer.

No cancellation occurred. The coordination record carries status escalated with a cleared lease and a human next actor; it carries no confirmed outcome and no confirmation label, so nothing was cancelled and no human decision was recorded against the round.

No review work was lost and no artifact was damaged. At the moment of this decision the request is present at 7234 bytes, the answer is absent because no reviewer answer was ever published, and the versioned transcript is present at 6091 bytes. That is the intact escalated shape the forced resume requires, and the artifact shape names the reviewer as the actor to resume.

The human reviewed this evidence and directed that the exchange resume in place at the same round rather than being resolved or archived. The reviewer then performs its normal round-one assessment of the staged step 3 implementation and publishes the paired answer through the shared exchange.

This is the second interruption of this kind in this effort and the third live instance of the escalated shape the review-status design now carries acceptance rows for. A returning agent again had to reconstruct identity, round, and responsible role from durable files, and a human again had to authorize a manual forced reclaim. Both are the work the review-status and review-resume requirements exist to remove.

Writer response: Round-one feedback is accepted with no disagreement.

- Staged the existing `rvw_status.bat` `-P` fix and its rationale, so the index
  now matches the launcher behavior exercised by the tests.
- Documented why `_resolve_root` must walk upward from the caller instead of
  using `find_project_root`, whose `PRJ_DIR` override could redirect the query.
- Removed trailing blank lines in the two new test-package initializers so the
  staged diff passes `git diff --cached --check`.
- Confirmed no Step 3 path still differs between index and working tree, and
  revalidated the unchanged three-group `a.commit` against all eight paths.

The focused 19-call test set is green. A fresh full walk passes static checks,
affected tests, and all 2,200 suite calls, but reports 99% coverage from a
separate concurrent workstream's unstaged workflow/spec-review files. Those
unrelated files are preserved outside this review's index.

### Reviewer focus for step 3 review-status-command (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-3-round-2 -->

## Round 2 by reviewer - Step 3

- Recorded: 2026-08-31T11:11:30+02:00
- Exchange: code/code/v0.11.0/review-status-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-status-command.md
- Implementation step: 3
- Outcome: answer

### Assessed index identity for step 3 review-status-command (exchange 1) (round 2)

Baseline index tree: 409a5d48d01d2113a1ea0900857121ee5e67e57d

Assessed index tree: 409a5d48d01d2113a1ea0900857121ee5e67e57d

### Implementation check for step 3 review-status-command (exchange 1) (round 2)

Result: Yes. Step 3 has been fully implemented. Every round-one item is fixed, and I verified each against the index rather than the working tree, because the index is what round one showed could differ.

The launcher fix is staged. `git show :rvw_status.bat` now contains `"%REVIEW_STATUS_PYTHON%" -P -m tools.review_status_cli %*` at line 31, and the path is staged as added with no working-tree modification. The `AM` state that produced the round-one finding is gone, so the committed launcher is now the launcher the tests exercise.

The root-resolution rationale is recorded where it will be read. `tools/review_status_cli.py` carries the comment at the branch itself, stating that `find_project_root` is not used because its `PRJ_DIR` override could redirect a caller-root status query to an unrelated repository. That is accurate and it sits immediately above the upward walk it protects, which is where a later reader tempted by the shared helper would look.

The whitespace items are fixed. Both new test-package initializers end without a trailing blank line, and `git diff --cached --check` exits zero across all eight staged paths.

No Step 3 path diverges between index and working tree. I checked every staged path individually rather than relying on the summary, and the eight are staged clean.

The implementation itself is unchanged from what I accepted in round one and remains correct. The renderer prints `Umbrella`, `Implementation step`, `Role`, `Specialization`, and `Owner` as separate labelled fields with `none` as the explicit umbrella fallback, and carries the renewal and expiry timestamps option E1 requires. The CLI exposes `--root` and `--format human|json` defaulting to human and maps outcomes to zero, three, and two. The launcher test builds an installed tree with two dated environments, clears `PRJ_DIR`, presets an existing `PYTHONPATH`, and asserts caller directory, newest-runtime selection, path prepending, argument forwarding, and status forwarding against a real process.

Step 3's own validation evidence is green. The focused run over both test leaves passes with nothing failing in focus and no focus-versus-suite interaction, the resolved grep returns 25 matching lines across the renderer, CLI, launcher, and both leaves, and the commit plan validates with eight paths, three groups, and no diagnostics.

The one cross-command inconsistency I noted in round one is unchanged and still outside this step. `review_status_cli._git_marker` accepts a linked worktree through `(root / ".git").exists()` while `commit_plan_check._resolve_root` rejects one through `.is_dir()`, and the review-status behavior remains the more correct of the two.

The step is complete. What prevents a commit-ready recommendation is the state of the repository around it, not this step's work, and that is reported separately.

Validation plan effects: I made no change to the validation plan. Reviewer mode may write only the
reviewed step's rows, and the rows for Step 3 are accurate about the
implementation, so there was nothing for this role to write.

My verdict agrees with the recorded `Yes. Step 3 has been fully implemented.`
The round-one divergence is repaired, the staged content is correct, and the
implementation, tests, and launcher all match what the rows describe.

One recorded claim does not reproduce and should be re-measured rather than
reworded. The rows and the round-two assessment report a detached walk that
passed static checks, affected tests, and all 2,200 full-suite calls at 99
percent coverage. My forced walk stopped in the check phase, so no full-suite
or coverage figure exists for this tree. That evidence was presumably accurate
when it was taken; it does not describe the repository now, and the validation
plan should carry the figure a repaired tree actually produces.

The document-level status line is correctly `No, it is not implemented.` Step 4
still reads `Not started`, so no flip was due.

No umbrella row was completed and reviewer mode correctly suppressed that
section. The umbrella digest is unchanged at
`dea13b3adfb5027e4bb2d826619634049e044befb09319a142ed2c9dbcb0a353`, confirmed by
`umbrella-digest compare` reporting `changed: false`.

### Pre-repair mandatory checks and coverage for step 3 review-status-command (exchange 1) (round 2)

Mandatory validation does not pass for this working tree, and the failure is
outside Step 3.

`ghog day --force` reported `ghog check done fail=0 warn=0 xfail=0 exit=1` and
stopped there. Because the walk opens with the static check, it never ran the
affected phase or the full suite, so there is no coverage figure, no duration
measurement, and no full-suite result for this state.

Three static steps failed: `ty(1)`, `pyright(1)`, and `big_files(1)`. The type
errors are both at
`tests/unit/tools/test_spec_reviewer_acceptance/test_spec_reviewer_acceptance_tdd.py:65`,
an attribute access on a possibly-None `Path`. The size failure is
`tools/prompt_workflow_skill.py` at 656 lines against the 650 ceiling, up from
647 at `HEAD`. Both paths are unstaged and neither is among Step 3's eight
staged paths.

Every other static step passed, including Ruff, Radon, Vulture, markdown-check,
ShellCheck, and the EOF check.

Step 3's own evidence is green. `ghog single` over both new test leaves passes
with nothing failing in focus and no focus-versus-suite interaction. The
resolved grep returns 25 matching lines across the renderer, CLI, launcher, and
both leaves. `commit-plan-check.bat --format json` reports `state=valid`,
`ready=true`, eight staged paths, three ordered groups, and no diagnostics.
`git diff --cached --check` exits `0`.

The requestor's recorded walk does not reproduce. Their assessment reports a
detached walk passing static checks, affected tests, and all 2,200 full-suite
calls at 99 percent coverage. My forced walk never reached the suite. That
figure was presumably accurate when measured; it does not describe the
repository as it now stands, so it cannot serve as this round's coverage
evidence.

I performed no repair, so there is no pre-repair versus post-repair difference
beyond this baseline. No coverage figure can be quoted for this state until the
three static failures are resolved or the workstreams are separated.

### Resolved validation set and sources for step 3 review-status-command (exchange 1) (round 2)

The request resolved four commands and I ran all four.

- `ghog day` — source `project`. Run as `ghog day --force`. It failed in its
  check phase with `exit=1` and never reached the affected or full runs.
- `ghog single tests/unit/tools/test_review_status_render/test_review_status_render_tdd.py tests/unit/tools/test_review_status_cli/test_review_status_cli_tdd.py` — source `plan`. Green.
- `rg -n -e Role: -e Specialization: -e Owner: -e Umbrella: -e schema_version -e=--format -e=--root ...` — source `plan`. Returns 25 matching lines.
- `.\commit-plan-check.bat --format json` — source `request`. Reports
  `state=valid`, `ready=true`, eight staged paths, three ordered groups, no
  diagnostics.

Three of the four passed. The fourth failed outside this step, on three static
checks in unstaged files belonging to a concurrent workstream.

I additionally ran `git diff --cached --check`, which exits `0`, and inspected
the staged blob of `rvw_status.bat` directly rather than the working-tree file,
because round one showed those can differ. The staged blob now carries the `-P`
flag.

The set is correct for what it covers. It cannot isolate this step from
concurrent unstaged work, and it does not compare index content with the working
tree, so the reviewer's own index inspection and the forced walk remain the two
things that decide readiness here.

### Resolver drift and direction for step 3 review-status-command (exchange 1) (round 2)

No drift. The resolved rg command and `ghog single` file list both match the
plan for this step, and the union adds nothing.

One coverage boundary is worth naming again. No command in the set compares
index content with the working tree, which is what round one turned on, and no
command isolates this step from concurrent unstaged work, which is what this
round turns on. Both are properties of the set rather than deviations from the
plan.

### Repository state around validation for step 3 review-status-command (exchange 1) (round 2)

My assessment produced no repository side effect. I made no repair, so the only
writes were ignored root `a.*` reviewer evidence files and ignored validation
artifacts.

Index identity held throughout. The request-time `request_index_tree` is
`409a5d48d01d2113a1ea0900857121ee5e67e57d`, and `capture-index-tree` returned
that identical value before assessment and after the forced walk, the focused
run, and every inspection.

The umbrella is untouched. `umbrella-digest compare` returns
`dea13b3adfb5027e4bb2d826619634049e044befb09319a142ed2c9dbcb0a353` before and
after with `changed: false`.

The validation-state comparison is clean this round, which is the round-one
finding closing. Using the same ordered eight-path set before and after,
`validation-state compare` returns `acceptable: true` with empty
`tracked_paths`, `untracked_paths`, and `ignored_paths`. Round one returned
`acceptable: false` for `rvw_status.bat`; that path is now staged with no
working-tree modification.

The working tree holds substantial unstaged work outside this review. A
concurrent workstream has modified instructions, several `tools` modules
including `prompt_workflow_skill.py`, and several test files, and
`commit-plan-check.bat` still carries its own unstaged `-P` fix. None of that is
mine, none is staged, and I left all of it exactly as found. It is reported
because the commit gate stages the whole tree, not because it affects the
reviewed index.

Ignored validation artifacts were refreshed by the walk, including `a.ghog.log`.
Because the walk stopped in its check phase, coverage and duration artifacts
were not regenerated.

One untracked path remains outside the staged set.
`docs/v0.11.0/review.code.v0.11.0.review-status-command.md` holds this
exchange's rounds and is correctly unstaged while the round is open.

### Repair inventory for step 3 review-status-command (exchange 1) (round 2)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 3 review-status-command (exchange 1) (round 2)

`a.commit` is accurate for the staged set, and I verified it with the shipped
checker rather than by reading it. `commit-plan-check.bat --format json` returns
`state=valid`, `ready=true`, eight staged paths, three ordered groups, and zero
diagnostics.

Group membership matches the index exactly. Group 1
`feat(review-status): expose status command` carries the launcher and the two
production modules. Group 2 `test(review-status): cover command adapters`
carries the two test leaf initializers and their two test modules. Group 3
`docs(review-status-command): record step 3 validation` carries the validation
plan alone and is the final commit.

Ordering is least to most dependent and every subject is a conventional commit
with an accurate scope. The grouping is unchanged from round one and needed no
change.

I did not amend `a.commit`. Membership, ordering, scope, and subjects are all
accurate for what is staged, so an amendment would have been a substantive
change to commit grouping with no defect to correct.

One thing about this plan is accurate today and will not survive the commit
gate unchanged. It describes eight staged paths, but the grouped-commit handoff
stages the whole tree, and the tree currently holds a substantial unstaged
concurrent workstream plus the still-unstaged `commit-plan-check.bat` fix.
Whoever reaches the gate will therefore regenerate the plan over a much larger
staged set, and the three groups here will not be the three groups committed.
That is normal for this workflow rather than a defect in the plan, but it is the
mechanism by which the unrelated gate failures would attach themselves to this
step's commit.

### Findings and boundaries for step 3 review-status-command (exchange 1) (round 2)

Unresolved findings:

- The repository gate is red, and no coverage or duration evidence exists for this working tree. `ghog day --force` stopped in its first phase with `ghog check done fail=0 warn=0 xfail=0 exit=1`, so the affected and full runs never executed. Three static steps failed: `ty(1)`, `pyright(1)`, and `big_files(1)`.
- None of the three belongs to Step 3, and I verified that rather than assuming it. The type errors are both at `tests/unit/tools/test_spec_reviewer_acceptance/test_spec_reviewer_acceptance_tdd.py:65`, reported as an attribute access on a possibly-None `Path`. The size failure is `tools/prompt_workflow_skill.py` at 656 lines against the 650 ceiling; that file is 647 lines at `HEAD`, so a concurrent change pushed it nine lines over. Both paths are unstaged, and neither appears in Step 3's eight staged paths.
- The requestor's recorded evidence does not reproduce. The round-two assessment states that a detached walk passed static checks, affected tests, and all 2,200 full-suite calls, reporting 99 percent coverage attributable to a concurrent workstream. My forced walk never reached the suite, so there is no full-suite result and no coverage figure for this tree at all. The claim was presumably true when it was measured; it is not true of the repository as it now stands.
- The consequence reaches the commit gate rather than staying an inconvenience, which is why I treat it as blocking rather than as an observation. The grouped-commit handoff stages the whole tree with `git add -A`, so selecting `Commit` from this state would sweep the unstaged concurrent workstream into the commit alongside Step 3, including a production file nine lines over the repository ceiling and a test file carrying two type errors. The repository would then be committed in a state that fails its own gate, and the failure would arrive attached to this step's commit rather than to the work that caused it.
- Step 3's own evidence is green and I want that recorded beside the finding rather than lost behind it. The focused run over both new test leaves passes, the resolved grep returns 25 matching lines, `git diff --cached --check` exits zero, the commit plan validates with eight paths and three groups and no diagnostics, and no staged path diverges from the working tree. Nothing in the staged set contributes to any of the three failures.

Boundary-crossing work: None.

### Human guidance response for step 3 review-status-command (exchange 1) (round 2)

Human guidance: Human decision to resume code review round 1 for step 3 after an abandoned wait.

The recorded escalation was a stopped handoff rather than a failure. The requestor published round 1 for implementation step 3 and entered its bounded wait. No reviewer session was active while that wait ran, so the exchange reached its timeout with the answer still absent and the protocol escalated it with the reason that the exchange was abandoned while waiting for the reviewer.

No cancellation occurred. The coordination record carries status escalated with a cleared lease and a human next actor; it carries no confirmed outcome and no confirmation label, so nothing was cancelled and no human decision was recorded against the round.

No review work was lost and no artifact was damaged. At the moment of this decision the request is present at 7234 bytes, the answer is absent because no reviewer answer was ever published, and the versioned transcript is present at 6091 bytes. That is the intact escalated shape the forced resume requires, and the artifact shape names the reviewer as the actor to resume.

The human reviewed this evidence and directed that the exchange resume in place at the same round rather than being resolved or archived. The reviewer then performs its normal round-one assessment of the staged step 3 implementation and publishes the paired answer through the shared exchange.

This is the second interruption of this kind in this effort and the third live instance of the escalated shape the review-status design now carries acceptance rows for. A returning agent again had to reconstruct identity, round, and responsible role from durable files, and a human again had to authorize a manual forced reclaim. Both are the work the review-status and review-resume requirements exist to remove.

Guidance response: The guidance carried into this round is the summary recorded when the human authorized the forced resume of round one after the overnight wait timed out. It is accurate as evidence and I stand by it, having written it from the artifact state at the time.

It informed this review in one concrete way. It established that the escalation was a stopped handoff rather than a failure and that the artifact shape named the reviewer as the actor to resume, which let me pick up round one as an ordinary round instead of treating the exchange as damaged. It gave the interruption no weight beyond that in either round's assessment.

It overrode nothing and could not have. Guidance cannot change exchange identity, the authority of the current staged state, or the disposition rules, and nothing in it asked to. The reclaim restored the same round and identity, and both rounds were assessed against the index the request named.

One observation in that guidance has now been borne out twice rather than once. It noted that a returning agent had to reconstruct identity, round, and responsible role from durable files, and that a human had to authorize a manual forced reclaim. That was the second such interruption in this effort. The command being built here is specified to report exactly those facts, and the resume command in the following requirement is specified to restore this shape without the manual step. This round's own blocker is a different kind of state problem, a tree the gate cannot measure, which the status command would also surface as evidence a returning caller could act on.

Nothing in the guidance bears on the disposition. That rests on the repository gate failing in its check phase with no coverage result for this tree, which is unrelated to the interruption the guidance describes.

### Writer instructions for step 3 review-status-command (exchange 1) (round 2)

Do not rework Step 3. Every round-one item is fixed and verified, the staged content is correct, and the implementation, tests, launcher, and commit grouping all need no change. The requested work is about the state of the repository around this step.

The blocker is that `ghog day --force` fails in its check phase, so no coverage or duration evidence exists for this tree. Three static steps fail, and all three sit in unstaged files belonging to a concurrent workstream: `ty` and `pyright` both report an attribute access on a possibly-None `Path` at `tests/unit/tools/test_spec_reviewer_acceptance/test_spec_reviewer_acceptance_tdd.py:65`, and the size check reports `tools/prompt_workflow_skill.py` at 656 lines against the 650 ceiling, up from 647 at `HEAD`.

Resolve those three before republishing, or separate the two workstreams so this step can be validated on its own. Either route works and the choice is yours, because both restore a measurable gate. What does not work is republishing with the tree in this state, since the recorded walk cannot be reproduced and the readiness floor has no coverage result to stand on.

Correct the recorded evidence once the gate runs again. The round-two assessment states that a detached walk passed static checks, affected tests, and all 2,200 full-suite calls at 99 percent coverage. That is not reproducible now, and the validation plan should record the figure the repaired tree actually produces rather than one measured against a different state.

Treat the commit gate as the reason this matters. The grouped-commit handoff stages the whole tree, so choosing `Commit` from here would carry the concurrent workstream into this step's commit, including a file over the repository ceiling and a test with two type errors. The failure would then be attached to Step 3's commit rather than to the work that caused it, which is worse for history than the delay.

Two smaller items need no action in this step. The cross-command inconsistency where `review_status_cli._git_marker` accepts a linked worktree through `(root / ".git").exists()` while `commit_plan_check._resolve_root` rejects one through `.is_dir()` is worth carrying forward, with the review-status behavior being the more correct of the two. And `commit-plan-check.bat` still sits modified and unstaged with its own `-P` fix, so it needs a home at whichever commit gate eventually takes it.

One process note, offered rather than requested. Round one found a staged-versus-worktree divergence and this round found a tree the gate cannot measure. Both were visible from `git status` and a forced walk before publishing. A pre-publication check that runs the gate and compares index against working tree would catch this class before a request goes out, rather than spending a review round on it.

### Decision rationale for step 3 review-status-command (exchange 1) (round 2)

I am publishing `changes-requested`, and I made no repair, so nothing here prevents a commit-ready recommendation in the next round.

I want the shape of this answer to be unmistakable, because it is unusual. Step 3 is complete. Every round-one item is fixed, I verified each against the index rather than the working tree, and I am requesting no change to the implementation, the tests, the launcher, or the commit grouping. What fails is the repository around the step.

Five readiness-floor results pass. Identity is exact and the request-time index tree matches the live index throughout. Implementation completeness is a Yes I re-derived. Staged attribution is clean, with the round-one divergence closed and `validation-state compare` now returning `acceptable: true` where it returned `acceptable: false` before. There are no carried findings against the step. The `a.commit` grouping is mechanically valid.

Mandatory validation is the result that fails. `ghog day --force` stopped in its check phase with `exit=1`, so no coverage figure, duration measurement, or full-suite result exists for this tree. Three static steps failed: two type errors at `tests/unit/tools/test_spec_reviewer_acceptance/test_spec_reviewer_acceptance_tdd.py:65`, and `tools/prompt_workflow_skill.py` at 656 lines against the 650 ceiling, up from 647 at `HEAD`. I checked each against the staged set: all three sit in unstaged files belonging to a concurrent workstream, and none is among Step 3's eight staged paths.

The requestor's recorded evidence does not reproduce, and that matters independently of blame. Their assessment reports a walk that passed static checks and all 2,200 full-suite calls at 99 percent coverage, attributing the shortfall to a concurrent workstream. My walk never reached the suite. The figure was presumably accurate when measured, but it describes a different tree, and a readiness floor cannot rest on a measurement that no longer reproduces.

The reason I treat this as blocking rather than noting it and recommending commit-ready is the commit gate itself. The grouped-commit handoff stages the whole tree, so choosing `Commit` from this state would sweep the concurrent workstream into this step's commit, carrying a production file over the repository ceiling and a test file with two type errors. The repository would be committed in a state that fails its own gate, and that failure would arrive attached to Step 3 rather than to the work that caused it. Recommending commit-ready while knowing that would be the wrong call even though the step itself is finished.

I considered whether this is disproportionate, since none of it is Step 3's fault and the step is genuinely done. It is not disproportionate, because the readiness floor is about whether this commit can safely be taken, not only about whether the step's code is correct. The fix is also cheap and does not touch this step: repair the three failures, or separate the workstreams so the step can be validated alone. Either restores a measurable gate, and the choice is the writer's.

One pattern is worth naming after two rounds. Round one found a staged-versus-worktree divergence, and this round found a tree the gate cannot measure. Both were visible from `git status` and a forced walk before the request went out, and both cost a review round that could have been spent on the implementation. That belongs in the requestor's pre-publication check rather than in a reviewer's backstop, and I raised it as a suggestion rather than a requested change.

This assessment is advisory and authorizes nothing. Only the human may choose `Commit` or `Rework and review again`.

### Final reviewer decision for step 3 review-status-command (exchange 1) (round 2)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-3-round-2 -->

## Round 3 by requestor - Step 3

- Recorded: 2026-08-31T11:56:06+02:00
- Exchange: code/code/v0.11.0/review-status-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-status-command.md
- Implementation step: 3
- Outcome: request

### Review identity for step 3 review-status-command (round 3)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.review-status-command.md
Implementation step: 3
Review round: 3

### Code review evidence for step 3 review-status-command (round 3)

request_index_tree: f55f4f5a1480c061d6fd92c232013b72633b0f27
resolved_validation_set:

- ghog day (sources: project)
- ghog single tests/unit/tools/test_review_status_render/test_review_status_render_tdd.py tests/unit/tools/test_review_status_cli/test_review_status_cli_tdd.py (sources: plan)
- rg -n -e Role: -e Specialization: -e Owner: -e Umbrella: -e schema_version -e=--format -e=--root tools/review_status_render.py tools/review_status_cli.py rvw_status.bat tests/unit/tools/test_review_status_render tests/unit/tools/test_review_status_cli (sources: plan)
- .\commit-plan-check.bat --format json (sources: request)

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(review-status): expose status command
group 1 path: rvw_status.bat
group 1 path: tools/review_status_cli.py
group 1 path: tools/review_status_render.py
group 2: test(review-status): cover command adapters
group 2 path: tests/unit/tools/test_review_status_cli/__init__.py
group 2 path: tests/unit/tools/test_review_status_cli/test_review_status_cli_tdd.py
group 2 path: tests/unit/tools/test_review_status_render/__init__.py
group 2 path: tests/unit/tools/test_review_status_render/test_review_status_render_tdd.py
group 3: docs(review-status-command): record step 3 validation
group 3 path: docs/v0.11.0/plan.v0.11.0.review-status-command.validation.md
staged path: docs/v0.11.0/plan.v0.11.0.review-status-command.validation.md
staged path: rvw_status.bat
staged path: tests/unit/tools/test_review_status_cli/__init__.py
staged path: tests/unit/tools/test_review_status_cli/test_review_status_cli_tdd.py
staged path: tests/unit/tools/test_review_status_render/__init__.py
staged path: tests/unit/tools/test_review_status_render/test_review_status_render_tdd.py
staged path: tools/review_status_cli.py
staged path: tools/review_status_render.py
```

### Requestor assessment for step 3 review-status-command (round 3)

Step 3 is fully implemented after accepting the round-one index repair and
clearing the round-two repository gate blocker.

- Static analysis passes Ty, Pyright, Ruff, Radon, Vulture, file-size,
  Markdown, ShellCheck, and EOF checks.
- The focused renderer and CLI leaves pass all 19 calls after the repair.
- The final detached Groundhog walk reached `state=done`, `exit=0`: static
  checks, the affected test, and all 2,202 full-suite calls pass at 100%
  coverage with no duration outliers.
- The renderer is a pure projection over `ReviewStatusResult`; the CLI owns one
  root resolution, collection, render, stream decision, and typed status.
- The launcher is exercised as a real Windows process against a controlled
  runtime and preserves caller directory, arguments, `PYTHONPATH`, and status.
- The Step 3 staged paths have no index-versus-working-tree divergence, and
  `commit-plan-check.bat --format json` remains valid for all eight paths.

### Implementation report for step 3 review-status-command (round 3)

Step 3 adds the public `rvw_status` command surface.

- `tools/review_status_render.py` produces labelled human blocks and compact
  Unicode JSON from the immutable normalized result.
- `tools/review_status_cli.py` discovers the caller Git root or validates an
  explicit root, evaluates status once, routes output, and returns `0`, `3`,
  or `2` from the typed outcome.
- `rvw_status.bat` selects the newest installed llm-shared Python without
  changing the caller directory, uses Python `-P` so a caller-local `tools`
  package cannot shadow llm-shared, and forwards arguments and process status.
- `tools/review_status_cli.py` documents why caller-root discovery deliberately
  avoids the ambient `PRJ_DIR` override in `find_project_root`.
- Renderer and CLI test leaves cover healthy, empty, damaged, and mixed
  evidence, all command outcomes, root failures, direct module execution, and
  the controlled batch adapter.
- The validation plan records the completed implementation-check evidence.

### Change summary for step 3 review-status-command (round 3)

The staged tree contains these eight paths:

- `tools/review_status_render.py`
- `tools/review_status_cli.py`
- `rvw_status.bat`
- `tests/unit/tools/test_review_status_render/__init__.py`
- `tests/unit/tools/test_review_status_render/test_review_status_render_tdd.py`
- `tests/unit/tools/test_review_status_cli/__init__.py`
- `tests/unit/tools/test_review_status_cli/test_review_status_cli_tdd.py`
- `docs/v0.11.0/plan.v0.11.0.review-status-command.validation.md`

The reviewed root `a.commit` has three dependency-ordered groups:

1. `feat(review-status): expose status command`
2. `test(review-status): cover command adapters`
3. `docs(review-status-command): record step 3 validation`

### Human guidance and writer response for step 3 review-status-command (round 3)

Human guidance:

Human decision to resume code review round 1 for step 3 after an abandoned wait.

The recorded escalation was a stopped handoff rather than a failure. The requestor published round 1 for implementation step 3 and entered its bounded wait. No reviewer session was active while that wait ran, so the exchange reached its timeout with the answer still absent and the protocol escalated it with the reason that the exchange was abandoned while waiting for the reviewer.

No cancellation occurred. The coordination record carries status escalated with a cleared lease and a human next actor; it carries no confirmed outcome and no confirmation label, so nothing was cancelled and no human decision was recorded against the round.

No review work was lost and no artifact was damaged. At the moment of this decision the request is present at 7234 bytes, the answer is absent because no reviewer answer was ever published, and the versioned transcript is present at 6091 bytes. That is the intact escalated shape the forced resume requires, and the artifact shape names the reviewer as the actor to resume.

The human reviewed this evidence and directed that the exchange resume in place at the same round rather than being resolved or archived. The reviewer then performs its normal round-one assessment of the staged step 3 implementation and publishes the paired answer through the shared exchange.

This is the second interruption of this kind in this effort and the third live instance of the escalated shape the review-status design now carries acceptance rows for. A returning agent again had to reconstruct identity, round, and responsible role from durable files, and a human again had to authorize a manual forced reclaim. Both are the work the review-status and review-resume requirements exist to remove.

Writer response: Round-one feedback is accepted with no disagreement.

- Staged the existing `rvw_status.bat` `-P` fix and its rationale, so the index
  now matches the launcher behavior exercised by the tests.
- Documented why `_resolve_root` must walk upward from the caller instead of
  using `find_project_root`, whose `PRJ_DIR` override could redirect the query.
- Removed trailing blank lines in the two new test-package initializers so the
  staged diff passes `git diff --cached --check`.
- Confirmed no Step 3 path still differs between index and working tree, and
  revalidated the unchanged three-group `a.commit` against all eight paths.

Round-two feedback is also accepted with no disagreement. Step 3 itself needed
no further change; the surrounding worktree was repaired so the repository gate
can be measured before the residual commit pass stages it:

- Narrowed the acceptance fixture's optional umbrella before path access,
  clearing both Ty and Pyright findings.
- Split the over-limit workflow router into a 430-line hub plus focused review
  and continuation modules of 208 and 138 lines, preserving public entry points.
- Added a public continuation-path test for the split fallback and restored
  repository coverage to 100%.
- Refreshed the Step 3 validation plan with the final 2,202-call evidence.

The final detached walk reached `state=done`, `exit=0`: all static checks, the
affected test, and all 2,202 full-suite calls pass at 100% coverage with zero
warnings, failures, duration outliers, or exclusions. The unchanged Step 3
index remains eight paths covered by the same valid three-group `a.commit`.

### Reviewer focus for step 3 review-status-command (round 3)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-3-round-3 -->

## Round 3 by reviewer - Step 3

- Recorded: 2026-08-31T12:07:04+02:00
- Exchange: code/code/v0.11.0/review-status-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-status-command.md
- Implementation step: 3
- Outcome: answer

### Assessed index identity for step 3 review-status-command (exchange 1) (round 3)

Baseline index tree: f55f4f5a1480c061d6fd92c232013b72633b0f27

Assessed index tree: f55f4f5a1480c061d6fd92c232013b72633b0f27

### Implementation check for step 3 review-status-command (exchange 1) (round 3)

Result: Yes. Step 3 has been fully implemented. Both earlier blockers are cleared, and I verified each against the evidence that exposed it rather than against the summary that reports it.

The round-one finding stays fixed. `git show :rvw_status.bat` still contains the `-P` invocation, no staged path diverges from the working tree, and `git diff --cached --check` exits zero across all eight paths. The staged launcher is still the launcher the tests exercise.

The round-two blocker is genuinely gone rather than reframed. `ghog day --force` now completes every phase, where it previously stopped in its check phase with three static failures. The check phase reports `exit=0`, and the full run reports `fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0` with `Objective reached`.

Each of the three round-two failures was addressed at its cause. `tools/prompt_workflow_skill.py` measured 656 lines against the 650 ceiling and now measures 430, so it was split rather than exempted. The two type errors at `test_spec_reviewer_acceptance_tdd.py:65` no longer appear, and both `ty` and `pyright` pass. Those files remain unstaged and outside this step, which is why the fix belonged to the concurrent workstream rather than to Step 3.

Coverage is back at 100 percent rather than the 99 percent reported in round two, and this time the figure is one I measured on the tree in front of me rather than one carried from an earlier state.

The implementation is unchanged from what I accepted in round one and remains correct. The renderer prints `Umbrella`, `Implementation step`, `Role`, `Specialization`, and `Owner` as separate labelled fields with `none` as the explicit umbrella fallback, and carries the renewal and expiry timestamps option E1 requires. The CLI exposes `--root` and `--format human|json` defaulting to human and maps outcomes to zero, three, and two. The documented reason for avoiding `find_project_root` still sits immediately above the upward walk it protects.

The launcher test remains the strongest of its kind here, building an installed tree with two dated environments, clearing `PRJ_DIR`, presetting an existing `PYTHONPATH`, and asserting caller directory, newest-runtime selection, path prepending, argument forwarding, and status forwarding against a real process.

Step 3's own evidence is green on every axis. The focused run over both leaves passes, the resolved grep returns 25 matching lines, the commit plan validates with eight paths, three groups, and no diagnostics, and the duration margin is comfortable with the suite's slowest call at 0.35 seconds against a 0.50 floor.

One cross-command inconsistency remains and is still outside this step. `review_status_cli._git_marker` accepts a linked worktree through `(root / ".git").exists()` while `commit_plan_check._resolve_root` rejects one through `.is_dir()`, and the review-status behavior remains the more correct of the two.

Validation plan effects: I made no change to the validation plan. The rows for Step 3 are accurate and my
verdict agrees with them, so reviewer mode had nothing to write.

The recorded `Yes. Step 3 has been fully implemented.` matches my independent
assessment. No `### Missing work for Step 3` section is required and none is
present.

The evidence claim that failed to reproduce in round two now does. The rows
report a detached walk reaching `state=done` with `exit=0`, static checks, the
affected test, and the full suite passing at 100 percent coverage with no
duration outliers. I reproduced that twice on the current tree, where round
two's walk never reached the suite at all.

The correction I asked for in round two was to record the figure a repaired tree
actually produces rather than one measured against a different state, and that
is what the rows now carry.

The document-level status line is correctly `No, it is not implemented.` Step 4
still reads `Not started`, so no flip was due.

No umbrella row was completed and reviewer mode correctly suppressed that
section. The umbrella digest is unchanged at
`dea13b3adfb5027e4bb2d826619634049e044befb09319a142ed2c9dbcb0a353`, confirmed by
`umbrella-digest compare` reporting `changed: false`.

### Pre-repair mandatory checks and coverage for step 3 review-status-command (exchange 1) (round 3)

The gate is green twice over, and both figures are ones I measured on the tree
in front of me.

Both forced walks agree exactly. `ghog day --force` reported
`ghog full done fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0` with
`Objective reached` on each run, reaching the check, affected, and full phases
every time.

The check phase now passes with `exit=0`, where round two stopped there with
`exit=1` and three static failures. Each of those three was fixed at its cause
rather than exempted. `tools/prompt_workflow_skill.py` measured 656 lines
against the 650 ceiling and now measures 430, so it was split. The two type
errors at `test_spec_reviewer_acceptance_tdd.py:65` no longer appear and both
`ty` and `pyright` pass.

Coverage is 100 percent rather than the 99 percent reported in round two, and
this run reached the suite so the figure exists for this tree rather than being
carried from an earlier state.

Duration has comfortable margin. The slowest call on both walks is
`tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_transcript_identity_tdd.py::test_answer_occurrence_follows_a_restarted_request_without_prior_answer`
at `0.35s` against the `0.50s` floor, 30 percent below it, with zero outliers.

`ghog single` over both Step 3 test leaves is green, with nothing failing in
focus and no focus-versus-suite interaction.

The resolved grep returns 25 matching lines across the renderer, CLI, launcher,
and both leaves.

`commit-plan-check.bat --format json` reports `state=valid`, `ready=true`, eight
staged paths, three ordered groups, and no diagnostics.

`git diff --cached --check` exits `0`, and I confirmed directly from the staged
blob that `rvw_status.bat` still carries the `-P` invocation, because round one
showed the index and working tree can differ.

I performed no repair, so there is no pre-repair versus post-repair difference
beyond this baseline.

### Resolved validation set and sources for step 3 review-status-command (exchange 1) (round 3)

The request resolved four commands and I ran all four. Every one passed.

- `ghog day` — source `project`. Run as `ghog day --force`, twice, because round
  two failed here and one green sample is not evidence of stability.
- `ghog single tests/unit/tools/test_review_status_render/test_review_status_render_tdd.py tests/unit/tools/test_review_status_cli/test_review_status_cli_tdd.py` — source `plan`.
- `rg -n -e Role: -e Specialization: -e Owner: -e Umbrella: -e schema_version -e=--format -e=--root ...` — source `plan`.
- `.\commit-plan-check.bat --format json` — source `request`.

Both walks completed every phase with `cov=100 outliers=0 excluded=0 exit=0` and
`Objective reached`. `ghog single` is green. The grep returns 25 matching lines.
The commit plan validates with eight paths, three groups, and no diagnostics.

I additionally ran `git diff --cached --check`, which exits `0`, and read the
staged blob of `rvw_status.bat` directly rather than the working-tree file,
because round one established that those can differ and the difference was
behavioral.

The set is now sufficient for this step. Its two coverage boundaries, no
index-versus-worktree comparison and no isolation from concurrent unstaged work,
both mattered in earlier rounds and neither bites here: the staged set matches
the working tree, and the concurrent workstream now passes the gate on its own.

### Resolver drift and direction for step 3 review-status-command (exchange 1) (round 3)

No drift. The resolved rg command and the `ghog single` file list both match
the plan for this step, and the union adds nothing.

The two coverage boundaries I named in earlier rounds are unchanged properties
of the set rather than deviations: no command compares index content with the
working tree, and no command isolates this step from concurrent unstaged work.
Both mattered in earlier rounds and neither bites here, because the staged set
matches the working tree and the concurrent workstream now passes the gate.

### Repository state around validation for step 3 review-status-command (exchange 1) (round 3)

My assessment produced no repository side effect. I made no repair, so the only
writes were ignored root `a.*` reviewer evidence files and ignored validation
artifacts.

Index identity held throughout. The request-time `request_index_tree` is
`f55f4f5a1480c061d6fd92c232013b72633b0f27`, and `capture-index-tree` returned
that identical value before assessment and after two forced walks, the focused
run, and every inspection.

The umbrella is untouched. `umbrella-digest compare` returns
`dea13b3adfb5027e4bb2d826619634049e044befb09319a142ed2c9dbcb0a353` before and
after with `changed: false`.

The validation-state comparison is clean. Using the same ordered eight-path set
before and after, `validation-state compare` returns `acceptable: true` with
empty `tracked_paths`, `untracked_paths`, and `ignored_paths`. No staged path
diverges from the working tree, which is the round-one finding staying closed.

The concurrent workstream is still unstaged and still outside this review, but
its state has changed in the way that matters. `tools/prompt_workflow_skill.py`
is now 430 lines rather than 656, and the type errors in
`test_spec_reviewer_acceptance_tdd.py` are gone, so the tree as a whole now
passes the repository gate. None of that work is mine and I left all of it
exactly as found.

Ignored validation artifacts were refreshed by the two walks, including
`.coverage`, `.testmondata`, `a.ghog.log`, and `a.ghog.outliers`. The contract
accepts differences confined to ignored validation artifacts, and none is
tracked or staged.

One untracked path remains outside the staged set.
`docs/v0.11.0/review.code.v0.11.0.review-status-command.md` holds this
exchange's rounds and is correctly unstaged while the round is open.

### Repair inventory for step 3 review-status-command (exchange 1) (round 3)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 3 review-status-command (exchange 1) (round 3)

`a.commit` is accurate, and I verified it with the shipped checker rather than
by reading it. `commit-plan-check.bat --format json` returns `state=valid`,
`ready=true`, eight staged paths, three ordered groups, and zero diagnostics.

Group membership matches the index exactly. Group 1
`feat(review-status): expose status command` carries the launcher and the two
production modules. Group 2 `test(review-status): cover command adapters`
carries the two test leaf initializers and their two test modules. Group 3
`docs(review-status-command): record step 3 validation` carries the validation
plan alone and is the final commit.

Ordering is least to most dependent and every subject is a conventional commit
with an accurate scope. The grouping is unchanged across all three rounds and
needed no change in any of them.

I did not amend `a.commit`. Membership, ordering, scope, and subjects are all
accurate, so an amendment would have been a substantive change to commit
grouping with no defect to correct, and it would have invalidated a commit-ready
recommendation in this same round.

The round-two caveat about this plan is now materially smaller but has not
vanished. The grouped-commit handoff stages the whole tree, and a concurrent
workstream is still unstaged, so the plan regenerated at the gate will cover
more than these eight paths. What changed is the consequence: that workstream
now passes the repository gate on its own, so sweeping it in no longer carries a
ceiling violation or a type error into this step's commit. It still means the
three groups reviewed here are not the three groups that will be committed, and
whoever reaches the gate should expect to group the wider set.

### Findings and boundaries for step 3 review-status-command (exchange 1) (round 3)

Unresolved findings: None.

Boundary-crossing work: None.

### Human guidance response for step 3 review-status-command (exchange 1) (round 3)

Human guidance: Human decision to resume code review round 1 for step 3 after an abandoned wait.

The recorded escalation was a stopped handoff rather than a failure. The requestor published round 1 for implementation step 3 and entered its bounded wait. No reviewer session was active while that wait ran, so the exchange reached its timeout with the answer still absent and the protocol escalated it with the reason that the exchange was abandoned while waiting for the reviewer.

No cancellation occurred. The coordination record carries status escalated with a cleared lease and a human next actor; it carries no confirmed outcome and no confirmation label, so nothing was cancelled and no human decision was recorded against the round.

No review work was lost and no artifact was damaged. At the moment of this decision the request is present at 7234 bytes, the answer is absent because no reviewer answer was ever published, and the versioned transcript is present at 6091 bytes. That is the intact escalated shape the forced resume requires, and the artifact shape names the reviewer as the actor to resume.

The human reviewed this evidence and directed that the exchange resume in place at the same round rather than being resolved or archived. The reviewer then performs its normal round-one assessment of the staged step 3 implementation and publishes the paired answer through the shared exchange.

This is the second interruption of this kind in this effort and the third live instance of the escalated shape the review-status design now carries acceptance rows for. A returning agent again had to reconstruct identity, round, and responsible role from durable files, and a human again had to authorize a manual forced reclaim. Both are the work the review-status and review-resume requirements exist to remove.

Guidance response: The guidance carried through these rounds is the summary recorded when the human
authorized the forced resume of round one after the wait was abandoned. It is
accurate as evidence and I stand by it.

It informed the review in one concrete way and no more. It established that the
escalation was a stopped handoff rather than a failure and that the artifact
shape named the reviewer as the actor to resume, which let me take up round one
as an ordinary round instead of treating the exchange as damaged. Beyond that it
carried no weight in any of the three assessments.

It overrode nothing and could not have. Guidance cannot change exchange
identity, the authority of the current staged state, or the disposition rules,
and nothing in it asked to. Each round was assessed against the index its
request named, and the two blockers I raised were found by inspecting that index
and by running the gate, not by anything the guidance said.

One observation in it has aged well. It noted that a returning agent had to
reconstruct identity, round, and responsible role from durable files, and that a
human had to authorize a manual forced reclaim. This exchange then spent two
further rounds on state problems that were visible from `git status` and a
forced walk. The command being built here is specified to report exactly that
class of fact, and the resume command in the following requirement is specified
to restore this shape without the manual step, so the guidance described the
work the effort is doing while the effort was doing it.

Nothing in the guidance bears on this round's disposition, which rests on a
green gate reproduced twice, a clean index comparison, and a valid commit plan.

### Writer instructions for step 3 review-status-command (exchange 1) (round 3)

No change is required. Every item from rounds one and two is closed and I am
requesting nothing further. Do not rework Step 3.

Three things are worth keeping deliberately, because each was earned rather than
incidental.

Keep the `-P` flag and its comment in `rvw_status.bat`. Without it the command
fails wherever a caller's repository defines its own `tools` package, and the
comment is what stops a later reader from removing a flag whose purpose is not
obvious from the line itself.

Keep the comment above the upward walk in `_resolve_root` explaining why
`find_project_root` is not used. The plan's confirmed facts cite that helper as
an available building block, which makes the substitution likely rather than
unlikely, and it would silently reintroduce the ambient `PRJ_DIR` override.

Keep the launcher test's controlled-runtime construction. It proves caller
directory, newest-runtime selection, path prepending with an existing entry
preserved, argument forwarding, and status forwarding against a real process,
and it is the corrected shape of a defect this umbrella already shipped once.

One item carries beyond this step and needs no action here. `review_status_cli`
accepts a linked worktree through `(root / ".git").exists()` while
`commit_plan_check` rejects one through `.is_dir()`. The review-status behavior
is the more correct of the two, so the reconciliation belongs on the older
command.

At the commit gate, expect the grouped-commit handoff to stage more than these
eight paths, because a concurrent workstream is still unstaged along with
`commit-plan-check.bat` and its own `-P` fix. That workstream now passes the
repository gate on its own, so sweeping it in no longer risks carrying a
failure into this commit, but the three groups reviewed here will not be the
three groups committed and the wider set will need grouping.

If the human selects `Commit`, run the existing commit step. If the human
selects `Rework and review again`, there is no outstanding scope from me; treat
any human guidance as the full scope of that round.

### Decision rationale for step 3 review-status-command (exchange 1) (round 3)

I am recommending `commit-ready`, and I made no repair in any of the three rounds, so nothing in this exchange invalidates the recommendation.

All six readiness-floor results pass. Identity is exact and the request-time index tree matches the live index throughout. Implementation completeness is a Yes I re-derived rather than carried forward. Mandatory validation and coverage pass, confirmed across two forced walks. Staged attribution is clean with no divergence between index and working tree. There is no unresolved finding against this step. The `a.commit` grouping is mechanically valid with zero diagnostics.

Both earlier blockers are closed at their cause, and I checked each against the evidence that exposed it rather than the summary that reports it.

Round one found that the staged launcher omitted the `-P` flag its working-tree copy carried, so the commit would have shipped a launcher that fails wherever a caller's repository defines its own `tools` package. The staged blob now carries the flag, no staged path diverges, and I read that blob directly rather than the file on disk.

Round two found a tree the gate could not measure, failing in its check phase on two type errors and a production file nine lines over the repository ceiling. All three are gone. The oversized module was split from 656 lines to 430 rather than exempted, and both type checkers now pass. That the fix was made properly rather than suppressed is worth as much as the green result.

Coverage is the number this round can actually stand on. Round two's recorded 99 percent came from a walk against a different tree and could not be reproduced; both of my walks reached the suite and reported 100 percent with zero outliers and identical slowest-call timings.

The implementation itself was correct from round one and I have not asked for a change to it since. The renderer and CLI match the settled design field for field, root resolution correctly avoids the ambient `PRJ_DIR` override with the reason recorded at the branch it protects, and the launcher test remains the strongest of its kind in this repository, proving caller-directory preservation, runtime selection, path prepending, argument forwarding, and status forwarding against a real process.

Two things carry beyond this step and neither blocks it. The cross-command inconsistency where `review_status_cli` accepts a linked worktree while `commit_plan_check` rejects one is worth reconciling, with the review-status behavior being the more correct of the two. And the concurrent workstream remains unstaged, so the plan regenerated at the commit gate will cover more than these eight paths; the difference from round two is that sweeping it in no longer carries a gate failure into this step's commit.

One process observation stands from earlier rounds. Round one turned on a staged-versus-worktree divergence and round two on a tree the gate could not measure, and both were visible from `git status` and a forced walk before the request went out. That belongs in the requestor's pre-publication check rather than in a reviewer's backstop, and it is the kind of thing the status command being built here is meant to make cheap.

This recommendation is advisory and authorizes nothing. A green gate, a valid commit plan, and a clean index comparison are mechanical evidence only. Only the human may choose `Commit` or `Rework and review again`.

### Final reviewer decision for step 3 review-status-command (exchange 1) (round 3)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-3-round-3 -->

## Round 3 by human - Step 3 - human-confirmation

- Recorded: 2026-08-31T15:31:05+02:00
- Exchange: code/code/v0.11.0/review-status-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-status-command.md
- Implementation step: 3
- Outcome: human-confirmation

Human choice: Rework and review again
Outcome: another-round
Guidance: The human selected `Rework and review again` after extending the requirement.
The requestor must add the public `$llm-shared:review-status-command` skill,
make its adapter refer to canonical instructions that invoke `rvw_status`,
update Step 3 and its validation evidence, implement and validate the change,
then publish the replacement review round.

<!-- review-entry-id: human-confirmation-round-3 -->

## Round 4 by requestor - Step 3

- Recorded: 2026-08-31T16:22:54+02:00
- Exchange: code/code/v0.11.0/review-status-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-status-command.md
- Implementation step: 3
- Outcome: request

### Review identity for step 3 review-status-command (round 4)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.review-status-command.md
Implementation step: 3
Review round: 4

### Code review evidence for step 3 review-status-command (round 4)

request_index_tree: d043674908f2eb6cf921f1e47d17200d6f6f6bac
resolved_validation_set:

- ghog day (sources: project)
- ghog single tests/unit/tools/test_review_status_render/test_review_status_render_tdd.py tests/unit/tools/test_review_status_cli/test_review_status_cli_tdd.py tests/unit/tools/test_instruction_structure/test_review_status_command_adapters_tdd.py (sources: plan)
- rg -n -e Role: -e Specialization: -e Owner: -e Umbrella: -e schema_version -e=--format -e=--root -e review-status-command -e rvw_status tools/review_status_render.py tools/review_status_cli.py rvw_status.bat instructions/review-status-command.md .agents/llm-shared/skills/review-status-command tests/unit/tools/test_review_status_render tests/unit/tools/test_review_status_cli tests/unit/tools/test_instruction_structure/test_review_status_command_adapters_tdd.py (sources: plan)
- .\commit-plan-check.bat --format json (sources: request)
- .\markdown-check.bat --root . (sources: request)

commit_plan_result:

```text
state: valid
ready: true
group 1: docs(review-status): require public skill
group 1 path: docs/v0.11.0/design.v0.11.0.review-status-command.md
group 1 path: docs/v0.11.0/draft.v0.11.0.review-mode.md
group 1 path: docs/v0.11.0/feature-request.v0.11.0.review-status-command.md
group 1 path: docs/v0.11.0/plan.v0.11.0.review-status-command.md
group 2: feat(review-status): expose status skill
group 2 path: .agent/workflows/review-status-command.md
group 2 path: .agents/llm-shared/.codex-plugin/plugin.json
group 2 path: .agents/llm-shared/instructions/review-status-command.md
group 2 path: .agents/llm-shared/skills/review-status-command/SKILL.md
group 2 path: .claude/skills/review-status-command/SKILL.md
group 2 path: .github/skills/review-status-command/SKILL.md
group 2 path: instructions/review-status-command.md
group 2 path: rvw_status.bat
group 2 path: tools/review_status_cli.py
group 2 path: tools/review_status_render.py
group 3: test(review-status): cover skill and command
group 3 path: tests/unit/tools/test_instruction_structure/test_review_status_command_adapters_tdd.py
group 3 path: tests/unit/tools/test_review_status_cli/__init__.py
group 3 path: tests/unit/tools/test_review_status_cli/test_review_status_cli_tdd.py
group 3 path: tests/unit/tools/test_review_status_render/__init__.py
group 3 path: tests/unit/tools/test_review_status_render/test_review_status_render_tdd.py
group 4: docs(review-status): record step 3 completion
group 4 path: docs/v0.11.0/plan.v0.11.0.review-status-command.validation.md
staged path: .agent/workflows/review-status-command.md
staged path: .agents/llm-shared/.codex-plugin/plugin.json
staged path: .agents/llm-shared/instructions/review-status-command.md
staged path: .agents/llm-shared/skills/review-status-command/SKILL.md
staged path: .claude/skills/review-status-command/SKILL.md
staged path: .github/skills/review-status-command/SKILL.md
staged path: docs/v0.11.0/design.v0.11.0.review-status-command.md
staged path: docs/v0.11.0/draft.v0.11.0.review-mode.md
staged path: docs/v0.11.0/feature-request.v0.11.0.review-status-command.md
staged path: docs/v0.11.0/plan.v0.11.0.review-status-command.md
staged path: docs/v0.11.0/plan.v0.11.0.review-status-command.validation.md
staged path: instructions/review-status-command.md
staged path: rvw_status.bat
staged path: tests/unit/tools/test_instruction_structure/test_review_status_command_adapters_tdd.py
staged path: tests/unit/tools/test_review_status_cli/__init__.py
staged path: tests/unit/tools/test_review_status_cli/test_review_status_cli_tdd.py
staged path: tests/unit/tools/test_review_status_render/__init__.py
staged path: tests/unit/tools/test_review_status_render/test_review_status_render_tdd.py
staged path: tools/review_status_cli.py
staged path: tools/review_status_render.py
```

### Requestor assessment for step 3 review-status-command (round 4)

Yes. Step 3 is fully implemented for the revised command-and-skill scope.

- Scope: the draft, requirement, design, and Step 3 plan now require the public
  `$llm-shared:review-status-command` skill and keep `rvw_status` as the typed
  evidence source.
- Feature behavior: one canonical instruction invokes the launcher by full
  path from the caller repository, interprets statuses `0`, `3`, and `2`, and
  forbids review or Git mutation. Codex, Claude, GitHub, and workflow adapters
  link directly to that instruction.
- Package discovery: the llm-shared plugin scans `./skills/`, contains the new
  `review-status-command/SKILL.md`, and carries cachebuster
  `0.1.0+codex.20260831140034`.
- Tests: the new adapter leaf adds three calls for canonical references, public
  metadata, and copied-policy rejection. The existing renderer and CLI leaves
  retain their 19 calls.
- Static and package checks: Markdown, staged whitespace, skill validation,
  plugin validation, and the commit-plan checker pass.
- Coverage and regression: detached `ghog day` reached `state=done`, `exit=0`;
  all 2,205 tests passed at 100% coverage with zero failures, warnings, xfails,
  exclusions, or duration outliers.
- Index integrity: all 20 staged paths match their working copies. The remaining
  unstaged paths are outside Step 3 and passed the same repository gate.

No missing work remains for Step 3.

### Implementation report for step 3 review-status-command (round 4)

Round 4 retains the reviewed renderer, CLI, launcher, and their command tests,
then adds the public skill requested at the round-3 human gate.

The implementation adds `instructions/review-status-command.md` as the single
workflow source. It tells an agent to run the full-path `rvw_status.bat` from
the caller repository, select human or JSON output, interpret the typed process
status, and stop without changing review or Git state.

Thin adapters were added for the llm-shared Codex plugin, shared instruction
discovery, Claude, GitHub, and the workflow host. A focused structure test pins
their direct canonical references, public name, invocation metadata, short
bodies, and absence of copied protocol or mutation rules.

The plugin cachebuster was refreshed through the plugin update helper. The
skill and complete plugin both pass their shipped validators.

### Change summary for step 3 review-status-command (round 4)

The index contains exactly 20 Step 3 paths, with no staged-path working-copy
divergence.

Scope documents:

- `docs/v0.11.0/design.v0.11.0.review-status-command.md`
- `docs/v0.11.0/draft.v0.11.0.review-mode.md`
- `docs/v0.11.0/feature-request.v0.11.0.review-status-command.md`
- `docs/v0.11.0/plan.v0.11.0.review-status-command.md`

Feature paths:

- `.agent/workflows/review-status-command.md`
- `.agents/llm-shared/.codex-plugin/plugin.json`
- `.agents/llm-shared/instructions/review-status-command.md`
- `.agents/llm-shared/skills/review-status-command/SKILL.md`
- `.claude/skills/review-status-command/SKILL.md`
- `.github/skills/review-status-command/SKILL.md`
- `instructions/review-status-command.md`
- `rvw_status.bat`
- `tools/review_status_cli.py`
- `tools/review_status_render.py`

Test paths:

- `tests/unit/tools/test_instruction_structure/test_review_status_command_adapters_tdd.py`
- `tests/unit/tools/test_review_status_cli/__init__.py`
- `tests/unit/tools/test_review_status_cli/test_review_status_cli_tdd.py`
- `tests/unit/tools/test_review_status_render/__init__.py`
- `tests/unit/tools/test_review_status_render/test_review_status_render_tdd.py`

Validation path:

- `docs/v0.11.0/plan.v0.11.0.review-status-command.validation.md`

`a.commit` is valid and ready with four ordered groups:

1. `docs(review-status): require public skill`
2. `feat(review-status): expose status skill`
3. `test(review-status): cover skill and command`
4. `docs(review-status): record step 3 completion`

### Human guidance and writer response for step 3 review-status-command (round 4)

Human guidance:

The human selected `Rework and review again` after extending the requirement.
The requestor must add the public `$llm-shared:review-status-command` skill,
make its adapter refer to canonical instructions that invoke `rvw_status`,
update Step 3 and its validation evidence, implement and validate the change,
then publish the replacement review round.

Writer response: The requestor accepts the human's `Rework and review again` direction without
disagreement.

Round 3 correctly approved the earlier eight command paths, but its conclusion
became incomplete when the human added a public skill to the requirement. The
requestor therefore updated the draft, requirement, design, plan, validation
plan, implementation, tests, plugin metadata, and commit grouping before this
replacement request.

All earlier reviewer findings remain closed: the launcher keeps `-P`, root
resolution does not use the ambient `PRJ_DIR` helper, package formatting and
nullable umbrella handling remain intact, the workflow router remains split,
and the repository gate reproduces at 100% coverage.

### Reviewer focus for step 3 review-status-command (round 4)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-3-round-4 -->

## Round 4 by reviewer - Step 3

- Recorded: 2026-08-31T16:57:18+02:00
- Exchange: code/code/v0.11.0/review-status-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-status-command.md
- Implementation step: 3
- Outcome: answer

### Assessed index identity for step 3 review-status-command (exchange 1) (round 4)

Baseline index tree: d043674908f2eb6cf921f1e47d17200d6f6f6bac

Assessed index tree: 7f0dc551a4676aed544745551b2fcc0a4646d395

### Implementation check for step 3 review-status-command (exchange 1) (round 4)

Result: Yes. Step 3 has been fully implemented.

I reached that verdict from the staged tree in front of me rather than from the
requestor's summary, and the round-4 delta is smaller than it looks.

Every one of the seven paths round 3 approved is byte-identical today. I
compared the retained round-3 baseline digests against a fresh
`validation-state capture` over the same paths: `tools/review_status_render.py`,
`tools/review_status_cli.py`, `rvw_status.bat`, both test leaves, and both leaf
initializers all report the same digest as the tree round 3 assessed
(`f55f4f5a1480c061d6fd92c232013b72633b0f27`). The reviewed renderer, CLI, and
launcher were therefore carried forward untouched, and the correctness I
accepted in round 3 needs no re-litigation.

The round-4 addition is the public skill, and it satisfies the revised Step 3
file list in full. All fourteen planned paths exist: the canonical
`instructions/review-status-command.md`, the workflow router, the four thin
provider adapters, the plugin manifest refresh, the new adapter test leaf, and
the previously reviewed command paths.

The canonical instruction carries the behavior and nothing else. It names the
full-path launcher invocation, keeps the caller's working directory as the
default repository, restricts `--root` to an explicitly named target, selects
human or JSON output, maps statuses `0`, `3`, and `2` onto trustworthy,
untrustworthy, and operational outcomes exactly as `ReviewStatusResult`
defines them, and forbids renewing, reclaiming, repairing, resuming,
cancelling, completing, staging, and committing. Its one external reference,
`rules/run_commands.md`, exists.

The adapters are thin and each points directly at that canonical file. I
resolved every relative link by hand: `.claude` and `.github` climb three
levels to the repository root, `.agents/llm-shared/skills/...` climbs four, and
`.agents/llm-shared/instructions/...` climbs three. All four land on the
canonical instruction. Bodies are one to three lines, well under the eight-line
ceiling the new test pins.

I also exercised the documented invocation rather than only reading it. Running
`rvw_status.bat` by full path from `tests/unit` resolved upward to the
repository root and produced the labelled report, so the caller-preservation
contract the skill depends on holds in a real process, not only in the
controlled-executable test.

The new test leaf follows the shape of its three sibling adapter tests in
`test_instruction_structure`, using the same `steps.llm_shared_dir()` anchor,
and pins the three things worth pinning: direct canonical references with a
body-length bound, the public discovery name with `user-invocable: true` where
the host requires it, and the absence of copied protocol or mutation policy.

No missing work remains for Step 3.

Three things I checked sit outside this step, and I left all three untouched.

Mixed line endings in two staged documents are pre-existing rather than
introduced here. `design.v0.11.0.review-status-command.md` and
`feature-request.v0.11.0.review-status-command.md` now mix 254 CRLF with 40 LF
lines and 159 CRLF with 114 LF lines, and their `HEAD` blobs were already mixed
at 258/20 and 221/22, with thirteen tracked Markdown files mixed repo-wide
today. This round added LF lines to files that were already mixed; it did not
create the condition. With no `.gitattributes` rule for Markdown and
`core.autocrlf` set to `false`, choosing a normalization direction is a
repository-wide decision outside this step and outside reviewer authority.

The plugin manifest diff reads as twenty-four changed lines for a one-token
change. `.agents/llm-shared/.codex-plugin/plugin.json` went from CRLF to LF
across the whole file while only the cachebuster value changed. That rewrite
comes from the external `update_plugin_cachebuster.py` helper the documented
update path runs, which is the file's owning writer, so LF is what every future
refresh will produce and restoring CRLF would only make the next run dirty the
file again. Noise in this commit, self-correcting afterwards.

The `_git_marker` inconsistency I raised in round 3 is unchanged.
`review_status_cli._git_marker` accepts a linked worktree through
`(root / ".git").exists()` while `commit_plan_check._resolve_root` rejects one
through `.is_dir()`. The review-status behavior remains the more correct of the
two, and aligning them belongs to whichever effort owns that decision.

Validation plan effects: I changed the validation plan, in the Step 3 rows only, and the change is one
I could not leave to the writer because the document contradicted its own
convention.

The staged Step 3 section carried no closing verdict sentence in any of its
four assessed sub-sections. `instructions/implementation-check.md` requires one
at the end of the architecture, performance, and unit-test-coverage
sub-sections, `templates/write-plans.validation.template.md` asks for a closing
conclusion in each, and Steps 1 and 2 of this same document already carry all
four. Step 3 was the only step written without them.

I added exactly four sentences, in the wording Steps 1 and 2 established:

- `No, there is nothing that needs to be addressed for Step 3.`
- `No, there is no performance issue that needs to be addressed for Step 3.`
- `No, there is no unit-tested class below 100% that needs completing for Step 3.`
- `No existing feature or reporting capability appears impaired for Step 3.`

Each records my own assessment rather than a restatement of the writer's prose.
I reached them from my own architecture, performance, and coverage review of
the staged tree, and each agrees with the bullets already present in its
sub-section.

Nothing else in the document changed. I left the rest of the Step 3 rows exactly
as written, because I checked them against the tree and found them accurate:
the file list matches the fourteen planned paths, the implementation bullets
match what is staged, the private `_InvocationError` and `_ArgumentParser`
types exist as described, and the recorded gate figures reproduce.

The document-level status line correctly remains `No, it is not implemented.`
Step 4 still reads `Not started`, so no flip was due, and I made none.

No umbrella row was completed. Reviewer mode suppresses that section, and the
effort is not finished in any case.

### Pre-repair mandatory checks and coverage for step 3 review-status-command (exchange 1) (round 4)

I recorded one pre-repair blob before touching anything, through
`bin/code_review_evidence.bat --repository . record-pre-repair-blob`.

- `docs/v0.11.0/plan.v0.11.0.review-status-command.validation.md` — object
  `e18fa0ecc259b3f563a190d6d12c07eb6c581881`, `writer_deleted: false`.

That is the only path I edited, so it is the only blob that needed recording.
The command paths, adapters, plugin manifest, scope documents, and test leaves
were read and never written, so no baseline was required for them.

The blob was recorded before the first edit rather than after it, which is what
lets `attribute-reviewer-patch` prove the resulting patch is mine alone.

### Resolved validation set and sources for step 3 review-status-command (exchange 1) (round 4)

The request resolved five commands. I ran all five, and every one passed.

- `ghog day` — source `project`. Run as `ghog day --force`, twice: once against
  the received tree and once after my validation-plan repair, because a repair
  I make is a change the gate has not yet seen.
- `ghog single tests/unit/tools/test_review_status_render/test_review_status_render_tdd.py tests/unit/tools/test_review_status_cli/test_review_status_cli_tdd.py tests/unit/tools/test_instruction_structure/test_review_status_command_adapters_tdd.py`
  — source `plan`.
- `rg -n -e Role: -e Specialization: -e Owner: -e Umbrella: -e schema_version -e=--format -e=--root -e review-status-command -e rvw_status ...`
  — source `plan`.
- `.\commit-plan-check.bat --format json` — source `request`. Run twice, before
  and after my repair.
- `.\markdown-check.bat --root .` — source `request`. Run twice, before and
  after my repair, because my repair edits Markdown.

Results.

Both `ghog day --force` walks completed every phase. The received tree reported
`ghog check ... exit=0`, `ghog affected --no-cov ... exit=0`, and
`ghog full done fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0`
with `Objective reached`. The post-repair walk reproduced it.

`ghog single` over the three Step 3 leaves reports `fail=0 warn=0 xfail=0
exit=0`, with nothing failing in focus and no focus-versus-suite interaction
suspect.

The resolved `rg` returns 51 matching lines across all eight targets: 5 in the
CLI, 4 in the renderer, 1 in the launcher, 3 in the canonical instruction, 2 in
the Codex skill adapter, 13 in the renderer leaf, 14 in the CLI leaf, and 9 in
the new adapter leaf. The required visible fields and the `--format` and
`--root` contract are all present.

`commit-plan-check.bat --format json` returns `state=valid`, `ready=true`,
twenty staged paths, four ordered groups, and zero diagnostics, both before and
after my repair.

`markdown-check.bat --root .` exits `0` with no output, both before and after
my repair, so the four sentences I added break no Markdown rule.

I also verified one figure the request states rather than accepting it. A direct
`pytest --collect-only -q` reports `2205 tests collected`, matching the
requestor's `2,205` exactly.

The set is sufficient for this step. Its one boundary is unchanged from earlier
rounds: no resolved command isolates this step from the concurrent unstaged
workstream. That does not bite here, because both full walks covered the whole
tree and reached the objective with the concurrent work in place.

### Resolver drift and direction for step 3 review-status-command (exchange 1) (round 4)

No drift.

The `ghog single` file list in the request matches the Step 3 completion
criteria exactly, including the newly added adapter leaf. The resolved `rg`
covers the same eight targets the plan names, with the plan's single quoted
alternation expressed as repeated `-e` patterns and the same nine alternatives.
That difference is the resolver's own normalization of one pattern, not a
change of scope or direction.

The two request-sourced commands, `commit-plan-check.bat --format json` and
`markdown-check.bat --root .`, add mechanical readiness and Markdown evidence
the plan does not itself name. Both are legitimate additions in the request
direction, and I ran both.

The union of the request set and the current resolver set adds nothing beyond
the five commands already listed, so there was nothing extra to run.

The set's one standing coverage boundary is unchanged rather than new: no
resolved command isolates this step from the concurrent unstaged workstream.

### Repository state around validation for step 3 review-status-command (exchange 1) (round 4)

Index identity held where it had to, and moved only where I moved it.

The request-time `request_index_tree` is
`d043674908f2eb6cf921f1e47d17200d6f6f6bac`, and `capture-index-tree` returned
that identical value before I assessed anything, so no early rejection was due
and the tree I reviewed is the tree the writer published. After staging my one
attributable validation-plan patch, the index is
`7f0dc551a4676aed544745551b2fcc0a4646d395`. That single move is mine and is
accounted for below.

The umbrella is untouched by me. `umbrella-digest capture` before assessment and
`umbrella-digest compare` after both return
`ad271b9914c33762110a029797483b4fb5caeef05d8724496482cc3a6835b9bb` with
`changed: false`. The digest differs from the one round 3 recorded because the
writer legitimately staged the row 9 title change this round; it did not move
during my assessment.

The validation-state comparison is not clean, and every entry in it is mine.
Using the same ordered twenty-path set before and after, `validation-state
compare` returns `acceptable: false` with `tracked_paths` of
`docs/v0.11.0/plan.v0.11.0.review-status-command.validation.md` and `<index>`,
and empty `untracked_paths` and `ignored_paths`. Those two entries are the
permitted reviewed-step validation-row repair and the index move that staging it
caused. No writer path differs, and no tracked validation side effect appeared.

No staged path diverges from its working copy. `git diff --name-only` lists only
concurrent unstaged workstream files and none of the twenty staged paths.

The staged umbrella edit stays inside what a requestor may change. It renames
row 9 from `Report active review status` to `Report active review status through
a skill` and updates the matching requirement detail and key title. The row's
`Status` remains `pending`, no row was completed, and row order, slug, and every
other row are unchanged.

The concurrent workstream is where I found it. `tools/prompt_workflow_*.py`,
`instructions/code-reviewer.md`, `instructions/review-requestor.md`,
`instructions/spec-reviewer.md`, `senv.doskey`, `commit-plan-check.bat`,
`.vscode/settings.json`, and the related test files remain modified and
unstaged. I read some of them as my own operating instructions and changed none
of them.

Ignored validation artifacts were refreshed by my two forced walks, the focused
run, and the checkers, including `.coverage`, `.testmondata`, `a.ghog.log`,
`a.ghog.outliers`, and my own root `a.rsc-round4.*` evidence files. The contract
accepts differences confined to ignored artifacts, and none of them is tracked
or staged.

One untracked path stays outside the staged set by design.
`docs/v0.11.0/review.code.v0.11.0.review-status-command.md` holds this
exchange's rounds and is correctly unstaged while the round is open.

### Repair inventory for step 3 review-status-command (exchange 1) (round 4)

Repairs made:

- `docs/v0.11.0/plan.v0.11.0.review-status-command.validation.md` -- added the four closing verdict sentences the Step 3 architecture, performance, unit-test-coverage, and feature-integrity sub-sections were missing; polishing-only; `attribute-reviewer-patch` returned `attributable: true`; staged.

Paths staged:

- `docs/v0.11.0/draft.v0.11.0.review-mode.md`
- `docs/v0.11.0/feature-request.v0.11.0.review-status-command.md`
- `docs/v0.11.0/design.v0.11.0.review-status-command.md`
- `docs/v0.11.0/plan.v0.11.0.review-status-command.md`
- `instructions/review-status-command.md`
- `.agent/workflows/review-status-command.md`
- `.agents/llm-shared/instructions/review-status-command.md`
- `.agents/llm-shared/skills/review-status-command/SKILL.md`
- `.claude/skills/review-status-command/SKILL.md`
- `.github/skills/review-status-command/SKILL.md`
- `.agents/llm-shared/.codex-plugin/plugin.json`
- `rvw_status.bat`
- `tools/review_status_cli.py`
- `tools/review_status_render.py`
- `tests/unit/tools/test_instruction_structure/test_review_status_command_adapters_tdd.py`
- `tests/unit/tools/test_review_status_cli/__init__.py`
- `tests/unit/tools/test_review_status_cli/test_review_status_cli_tdd.py`
- `tests/unit/tools/test_review_status_render/__init__.py`
- `tests/unit/tools/test_review_status_render/test_review_status_render_tdd.py`
- `docs/v0.11.0/plan.v0.11.0.review-status-command.validation.md` (also carries my staged reviewer patch)

### Commit plan assessment for step 3 review-status-command (exchange 1) (round 4)

`a.commit` is accurate, and I verified it with the shipped checker rather than
by reading it.

`commit-plan-check.bat --format json` returns `state=valid`, `ready=true`,
twenty staged paths, four ordered groups, and zero diagnostics. I ran it twice,
against the received index and again after staging my repair, and both runs
agree.

Group membership matches the index exactly:

1. `docs(review-status): require public skill` — the draft, feature request,
   design, and plan, which is the scope change that made this round necessary.
2. `feat(review-status): expose status skill` — the canonical instruction, four
   adapters, plugin manifest, launcher, CLI, and renderer.
3. `test(review-status): cover skill and command` — the new adapter leaf and
   both command leaves with their initializers.
4. `docs(review-status): record step 3 completion` — the validation plan alone,
   last.

Ordering runs least to most dependent, scope is accurate on every subject, and
each subject is a well-formed conventional commit. Documentation of intent
precedes the implementation it describes, tests follow the code they cover, and
the validation record lands last, which is the ordering the workflow expects.

I did not amend `a.commit`. My repair changes the content of the file that is
already group 4's sole member, so membership, ordering, scope, and subjects all
remain correct, and an amendment would have been a change to commit grouping
with no defect to correct.

One caveat carries forward from round 3, unchanged in kind and unchanged in
consequence. The grouped-commit handoff stages the whole tree with `git add -A`,
and a concurrent workstream is still unstaged, so the plan regenerated at the
commit gate will cover more than these twenty paths. That workstream passes the
repository gate on its own — both of my full walks included it — so sweeping it
in carries no failing check into this step's commit. It does mean the four
groups reviewed here are not the four groups that will be committed, and
whoever reaches the gate should expect to group the wider set.

### Findings and boundaries for step 3 review-status-command (exchange 1) (round 4)

Unresolved findings: None.

Boundary-crossing work: None.

### Human guidance response for step 3 review-status-command (exchange 1) (round 4)

Human guidance: The human selected `Rework and review again` after extending the requirement.
The requestor must add the public `$llm-shared:review-status-command` skill,
make its adapter refer to canonical instructions that invoke `rvw_status`,
update Step 3 and its validation evidence, implement and validate the change,
then publish the replacement review round.

Guidance response: The guidance names four requirements, and I checked each against the tree
rather than against the writer's account of it.

The public skill exists and is discoverable. `review-status-command` is present
in the Codex plugin under `.agents/llm-shared/skills/`, which the manifest scans
through `"skills": "./skills/"`, and the manifest's cachebuster was refreshed to
`0.1.0+codex.20260831140034` so the installed plugin reloads. Claude and GitHub
adapters carry `user-invocable: true`, and the workflow router is in place. I
can confirm the Claude adapter loads from outside the file as well as inside it:
this session lists `review-status-command` among its available skills.

The adapters refer to canonical instructions rather than reimplementing them.
Every one of the five files points directly at
`instructions/review-status-command.md`, with bodies of one to three lines. I
resolved each relative link by hand and all four link adapters land on the
canonical file. No adapter carries protocol or mutation prose, and the new test
pins that absence for `review_exchange.bat`, `git add`, `lease_renewed_at`, and
`owning-action-pending`.

The canonical instruction invokes `rvw_status` rather than duplicating it. It
runs the launcher by full path from the caller repository, keeps the caller's
directory as the default target, restricts `--root` to an explicitly named
repository, and interprets statuses `0`, `3`, and `2`. It reproduces no
discovery or classification logic, and it forbids every mutating protocol
action.

Step 3 and its validation evidence were updated, and I completed that update.
The plan's Step 3 file list, tests-first section, behavior section, and line
budgets all cover the skill, and the validation plan records the check. Its four
sub-sections were missing their closing verdict sentences, which the
implementation-check instruction requires and which Steps 1 and 2 already carry;
I added those four sentences and staged them.

The guidance directed additional scope. It did not ask me to relax identity,
staged-state, evidence, or disposition rules, and I applied all of them
unchanged.

### Writer instructions for step 3 review-status-command (exchange 1) (round 4)

No rework is required. Step 3 is complete and my recommendation is
`commit-ready`, so these instructions are for the gate rather than for another
implementation round.

Three things to carry forward.

Keep my staged validation-plan patch. The Step 3 architecture, performance,
unit-test-coverage, and feature-integrity sub-sections now end with their
required verdict sentences, matching Steps 1 and 2. They are already staged in
group 4; do not revert them when regenerating the commit plan.

Expect the commit gate to stage more than these twenty paths. The
grouped-commit handoff runs `git add -A`, and the concurrent workstream in
`tools/prompt_workflow_*.py`, `instructions/*.md`, `senv.doskey`,
`commit-plan-check.bat`, `.vscode/settings.json`, and the related test files is
still unstaged. Group that wider set from least to most dependent like any
other staged change; it passes the repository gate on its own, so it carries no
failing check into this commit. Keep
`docs(review-status): record step 3 completion` last.

Step 4 remains `Not started`, and the document-level status line correctly stays
`No, it is not implemented.` Do not flip it, and do not complete umbrella row 9,
until Step 4's acceptance and read-only rollout work is done and checked.

### Decision rationale for step 3 review-status-command (exchange 1) (round 4)

I recommend `commit-ready`. The recommendation is advisory and authorizes
nothing; the human owns the commit decision at the convergence gate.

All six readiness-floor results pass.

Identity is exact. The envelope, the human-readable request, the plan, the
declared step, the round, the exchange occurrence, and the request-time index
tree all agree, and the named step exists in the plan.

The implementation is complete. My own check returns `Yes. Step 3 has been fully
implemented.` against all fourteen planned paths, and the seven paths round 3
approved are byte-identical to the tree it assessed.

Mandatory validation and coverage pass. Both forced walks reached `cov=100` with
`fail=0`, `outliers=0`, and `exit=0`; the focused run over the three Step 3
leaves is green; the resolved grep returns 51 lines; Markdown and commit-plan
checks exit `0` before and after my repair.

Staged scope is attributable. Twenty writer paths, no divergence from their
working copies, one reviewer patch proved `attributable: true`, and nothing of
the concurrent unstaged workstream swept in.

No finding is unresolved. The one defect I found is repaired in this round, and
both earlier rounds' findings remain closed on evidence I re-checked rather than
inherited.

`a.commit` is accurate, verified twice with the shipped checker rather than by
reading it, and needed no amendment.

This round made no substantive repair. My single edit writes the reviewed step's
own validation rows, which the reviewer instruction names as review metadata; it
changes no code, test, acceptance behavior, or commit grouping, so it does not
disqualify a commit-ready recommendation in the same round.

What the human is deciding is narrower than the diff suggests. The command
itself was already accepted in round 3 and is unchanged; this round adds the
public skill the human asked for, and it is a canonical instruction with four
thin adapters that copy no policy. The one thing to carry into the gate is that
the grouped-commit handoff will stage the wider tree, so the commit will cover
more than the twenty paths reviewed here.

### Final reviewer decision for step 3 review-status-command (exchange 1) (round 4)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-3-round-4 -->

## Round 4 by human - Step 3 - human-confirmation

- Recorded: 2026-08-31T18:32:07+02:00
- Exchange: code/code/v0.11.0/review-status-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-status-command.md
- Implementation step: 3
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-4 -->
