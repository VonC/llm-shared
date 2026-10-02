# Code review transcript for v0.13.0

- Exchange: code/code/v0.13.0/full_suite_levels
- Reviewed document: docs/v0.13.0/plan.v0.13.0.full_suite_levels.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor - Step 0

- Recorded: 2026-10-02T09:36:38+02:00
- Exchange: code/code/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/plan.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Implementation step: 0
- Outcome: request

### Review identity for step 0 full_suite_levels (round 1)

Umbrella draft: none
Implementation plan: docs/v0.13.0/plan.v0.13.0.full_suite_levels.md
Implementation step: 0
Review round: 1

### Code review evidence for step 0 full_suite_levels (round 1)

request_index_tree: 9ac8bb381cae84d955b141ddd1dc382396c962d8
resolved_validation_set:

- ghog day (sources: project, plan)
- rg -n 'xfail\(strict=True' tests/unit/tools/test_groundhog_levels_perf (sources: plan)
- rg -n 'timeout\(GATE_TIMEOUT_SECONDS\)' tests/unit/tools/test_groundhog_levels_perf (sources: plan)

commit_plan_result:

```text
state: valid
ready: true
group 1: test(groundhog): add leveled walk cost gates
group 1 path: tests/unit/tools/test_groundhog_levels_perf/__init__.py
group 1 path: tests/unit/tools/test_groundhog_levels_perf/test_groundhog_levels_perf_tdd.py
group 2: docs(full_suite_levels): record step 0 validation
group 2 path: docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md
staged path: docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md
staged path: tests/unit/tools/test_groundhog_levels_perf/__init__.py
staged path: tests/unit/tools/test_groundhog_levels_perf/test_groundhog_levels_perf_tdd.py
```

### Requestor assessment for step 0 full_suite_levels (round 1)

Step 0 is fully implemented. The validation plan records the exact Yes
verdict for Step 0; Steps 1 to 8 remain pending, so its document-level line
stays `No, it is not implemented.`. This round covers only the test-only cost
gates and their validation record; no production file changed.

The groundhog walk (`ghog day`, the Step 0 gate arguments) finished on
2026-10-02 at 09:26:28 +02:00 with `exit=0`. Ty, Pyright, Ruff, Radon,
Vulture, the 650-line big-file gate, the Markdown check, ShellCheck and the
EOF check passed. The affected phase reported `fail=0 warn=0 xfail=5`; the
full phase reported `fail=0 warn=0 xfail=5 cov=100` in 3m 37.1s, so the only
xfails of the suite are the five new gates. The first walk of the step stopped
at check.bat on a Pyright `reportUnusedFunction` for the private autouse
fixture; renaming it to the public `clear_ambient_selectors`, as the
repository names its other autouse fixtures, cleared it before the green walk.

The two plan completion patterns, `xfail\(strict=True` and
`timeout\(GATE_TIMEOUT_SECONDS\)`, each list five gates over
`tests/unit/tools/test_groundhog_levels_perf`. `rg` is not on the PowerShell
PATH of the writer's shell, so the same ripgrep patterns ran through the
harness search tool.

Coverage is configured for `tools` and omits `*/tests/*`, so both new files
sit outside the gate; every top-level helper of the gate file is referenced by
a gate and the autouse fixture applies to all five. Physical counts are 7 for
the package initializer and 265 for the gate file, against an advisory 190:
recorded as variance below the 550 band, not missing work. No new type, no
production import, and no `O(n^2)` or `O(n log n)` computation was added.

### Implementation report for step 0 full_suite_levels (round 1)

Added the `tests/unit/tools/test_groundhog_levels_perf` package: an
initializer with the plan's `Unit test package for tools/...` docstring and
`# eof`, and `test_groundhog_levels_perf_tdd.py` with five gates. Each gate
carries `@pytest.mark.timeout(GATE_TIMEOUT_SECONDS)` with
`GATE_TIMEOUT_SECONDS: Final = 5` and
`@pytest.mark.xfail(strict=True, reason="removed in Step <N>")`, drives
`cli.main` through `QueueSpawns` and `make_deps` on a `tmp_path` project
(`check.bat`, `pyproject.toml`, `src/mod.py`, `tests/test_mod.py`), and
asserts exit codes and spawned child commands.

Step 2 gates:

- `test_default_walk_spawns_no_full_run`: a green `ghog day` spawns exactly
  the check.bat child and one `--no-cov` affected child.
- `test_upgrade_spawns_only_the_full_run`: after a green default walk,
  `ghog day --full=cov` exits 0 with one child that carries `--cov-report`
  and neither `--cov-append` nor `--durations=0`, counted on the second
  invocation's own queue.
- `test_stronger_saved_proof_spawns_nothing`: after a green `--full=speed`
  walk on a sequential project, `ghog day --full=cov` exits 0 and spawns
  nothing. Asking for `cov` keeps the gate valid even if the speed walk's
  floor write moves the timing fingerprint, since a timing mismatch caps the
  saved proof at `cov`, which still meets the request.

Step 4 gates, on a project whose `.ghog-groups` declares `sentinel` with
`tests/sentinel/**` and `src/sentinel/**`, plus `src/sentinel/core.py`,
`tests/sentinel/test_core.py` and a `tests/sentinel/conftest.py` that is no
test file:

- `test_grouped_walk_passes_only_group_test_files`: `ghog day --full=pass
  --group=sentinel` exits 0, its first child is check.bat, and its two other
  children carry exactly `tests/sentinel/test_core.py` as `.py` positional
  paths; paths are compared after resolving against the root, so a relative
  or absolute spelling both qualify.
- `test_grouped_walk_walks_the_tree_once`: the same walk exits 0 with its two
  group children and one `pathlib.Path.rglob` call, counted through a
  `monkeypatch` wrapper that still walks for real. `--full=pass` keeps the
  gate off the group coverage data file.

Every gate fails today on an assertion, never on an error: `_run(argv, deps)`
returns argparse's `SystemExit(2)` code for the unknown `--full` or `--group`
option, every spawn queue holds the children the pre-change walk pops (a
default walk pops three, so the default-walk gate fails on its count), and an
autouse fixture deletes `GHOG_FULL` and `GHOG_GROUP` so an ambient selector
cannot change a gate. No PBT was added: the plan states fixed counting
contracts need none.

The validation plan's Step 0 section records the Yes verdict with evidence,
and its theme sentence now says Step 0 is checked and Steps 1 to 8 pending.

Writer notes: `.reviews/a.full_suite_levels.step0.journal.md` and
`.reviews/a.full_suite_levels.step0.handoff.md`.

### Change summary for step 0 full_suite_levels (round 1)

Three staged paths are covered by the mechanically valid root `a.commit`
(`commit-plan-check` reports `state: valid`, `ready: true`):

1. test(groundhog): add leveled walk cost gates
   - `tests/unit/tools/test_groundhog_levels_perf/__init__.py`
   - `tests/unit/tools/test_groundhog_levels_perf/test_groundhog_levels_perf_tdd.py`
2. docs(full_suite_levels): record step 0 validation
   - `docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md`

The gate package comes first; the completed validation record is the final
documentation group with the exact `record step 0 validation` title. No
production file, caller or unrelated file changed.

### Writer response for step 0 full_suite_levels (round 1)

Writer response:

This is the first implementation review round for Step 0. There is no earlier
code-review feedback to accept or dispute. The settled design and plan
decisions are implemented only to the extent assigned to Step 0: the gates
encode the contracts Steps 2 and 4 must meet, and no behavior is implemented
ahead of those steps.

### Reviewer focus for step 0 full_suite_levels (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-0-round-1 -->

### LLM nature completion for reviewer (exchange 1)

Recorded nature: `codex`

Completed artifacts:

- `.reviews/a.review-active.code.code.v0.13.0.full_suite_levels.md`
- `.reviews/a.review-requested.code.v0.13.0.full_suite_levels.md`

<!-- review-entry-id: llm-nature-completion-reviewer-exchange-1 -->

## Round 1 by reviewer - Step 0

- Recorded: 2026-10-02T09:44:22+02:00
- Exchange: code/code/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/plan.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 0
- Outcome: answer

### Assessed index identity for step 0 full_suite_levels (exchange 1) (round 1)

Baseline index tree: 9ac8bb381cae84d955b141ddd1dc382396c962d8

Assessed index tree: d94e77cac513534dce15621bc53e43fdee96c8a3

### Implementation check for step 0 full_suite_levels (exchange 1) (round 1)

Result:

Yes. Step 0 has been fully implemented.

The staged package implements all five planned contracts through cli.main, QueueSpawns and make_deps on temporary projects. The default gate requires exactly check.bat and affected --no-cov. The upgrade gate measures only the second invocation and requires one covered child without appended coverage or durations. The stronger-proof gate requires zero children when cov follows speed. The grouped gates require the sentinel test file on both test children and exactly one Path.rglob call, after successful execution.

All five gates carry the five-second timeout and strict xfail with the correct Step 2 or Step 4 owner. The SystemExit adapter makes unsupported selectors fail at exit-code assertions. The three-child fake queues cover the current walk; the default gate fails at the expected count. Fixtures clear both ambient selectors and restore patches. The 265-line test module and seven-line initializer remain below the repository ceiling.

No production class changed, no DDD-Hexagonal boundary changed, and no new production complexity or reporting behavior was introduced. The helpers are all referenced: _write through the project builders, the other helpers through the gates, and the autouse fixture through pytest. The coverage gate measures tools and omits tests, so the requestor's 100% is not a coverage claim for these new tests. Expected-failure gates intentionally stop at their first failing assertion until their owning step.

No blocking implementation, performance, coverage, or feature-integrity finding remains.

Validation plan effects:

Updated only Step 0 in docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md: recorded the independent assessment, corrected the temporary-project maximum from seven files to eight, and explicitly included the transitively used _write helper. The exact Yes sentence remains. Other steps and the document-level pending verdict remain unchanged. No umbrella applies.

### Pre-repair mandatory checks and coverage for step 0 full_suite_levels (exchange 1) (round 1)

Request-time tree matched the captured baseline 9ac8bb381cae84d955b141ddd1dc382396c962d8. The requestor records a green ghog day completed 2026-10-02 at 09:26:28 +02:00, with five expected failures in affected and full phases and tools coverage 100%. This is requestor evidence, not an independent rerun.

The reviewer inspected the staged diff, plan Step 0, validation record, coverage configuration, existing day walk, shared fake process support, and a.commit. No executed ghog evidence was necessary for this test-only assessment; neither the requestor validation set nor coverage was rerun.

### Resolved validation set and sources for step 0 full_suite_levels (exchange 1) (round 1)

The current resolver contract retains these commands and source labels:

- ghog day (sources: project, plan).
- rg -n 'xfail\(strict=True' tests/unit/tools/test_groundhog_levels_perf (source: plan).
- rg -n 'timeout\(GATE_TIMEOUT_SECONDS\)' tests/unit/tools/test_groundhog_levels_perf (source: plan).

.review-validation is absent, so the current project default remains ghog day. Step 0 supplies the same walk and two counting checks; the request adds none.

### Resolver drift and direction for step 0 full_suite_levels (exchange 1) (round 1)

No drift in commands, order, or source labels. The current default and Step 0 completion criteria match the request's resolved_validation_set. The reviewer did not execute that set.

### Repository state around validation for step 0 full_suite_levels (exchange 1) (round 1)

Baseline index: 9ac8bb381cae84d955b141ddd1dc382396c962d8.
Assessed index: d94e77cac513534dce15621bc53e43fdee96c8a3.

The umbrella comparison reports applicable=false and changed=false. The validation-state comparison reports acceptable=false because the validation plan and index changed. Inspection and the attributable patch explain both differences: only the permitted Step 0 validation metadata was edited and staged. Both test-file digests are unchanged; no untracked difference or tracked validation side effect was reported. This permitted metadata exception satisfies the reviewer boundary.

### Repair inventory for step 0 full_suite_levels (exchange 1) (round 1)

Repairs made:

- docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md: polishing-only review metadata; added independent assessment and corrected the file-count and helper-reference descriptions. The evidence launcher attributed the patch to the captured pre-repair blob, and only that patch was applied to the index. No implementation or test repair.

Paths staged:

- `tests/unit/tools/test_groundhog_levels_perf/__init__.py`
- `tests/unit/tools/test_groundhog_levels_perf/test_groundhog_levels_perf_tdd.py`
- `docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md`

### Commit plan assessment for step 0 full_suite_levels (exchange 1) (round 1)

The reviewer independently ran commit-plan-check.bat --format json against the received state: exit 0, state valid, ready true, diagnostics [].

1. test(groundhog): add leveled walk cost gates
   Paths: `tests/unit/tools/test_groundhog_levels_perf/__init__.py` and `tests/unit/tools/test_groundhog_levels_perf/test_groundhog_levels_perf_tdd.py`.
2. docs(full_suite_levels): record step 0 validation
   Path: `docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md`.

These are the exact three staged paths. Tests precede their validation record; subjects and scope are accurate. The reviewer metadata edit changes no membership, ordering, or grouping, so a.commit remains accurate and was not amended.

### Findings and boundaries for step 0 full_suite_levels (exchange 1) (round 1)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 0 full_suite_levels (exchange 1) (round 1)

The advisory review is complete. Present the commit-ready human gate using the existing requestor workflow; no commit is authorized by this recommendation. No rework is required.

### Decision rationale for step 0 full_suite_levels (exchange 1) (round 1)

Recommend commit-ready. All six readiness criteria pass: exact identity and request-time index; complete Step 0 implementation; requestor validation evidence and satisfactory static coverage assessment; attributable staged scope; no unresolved current or carried finding; and mechanically valid, accurate a.commit grouping.

No substantive code or test repair occurred. The only reviewer changes are permitted Step 0 validation metadata. The generic request scope asks for repairs, but there is no literal Human guidance block authorizing implementation repair, and none was performed. The commit choice remains with the human.

### Final reviewer decision for step 0 full_suite_levels (exchange 1) (round 1)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-0-round-1 -->

## Round 1 by human - Step 0 - human-confirmation

- Recorded: 2026-10-02T10:43:03+02:00
- Exchange: code/code/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/plan.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 0
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-1 -->

## Round 1 by requestor - Step 1

- Recorded: 2026-10-02T12:04:17+02:00
- Exchange: code/code/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/plan.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Implementation step: 1
- Outcome: request

### Review identity for step 1 full_suite_levels (round 1)

Umbrella draft: none
Implementation plan: docs/v0.13.0/plan.v0.13.0.full_suite_levels.md
Implementation step: 1
Review round: 1

### Code review evidence for step 1 full_suite_levels (round 1)

request_index_tree: 7b5934e6b965901f884da5221fcecf13fed7ebdc
resolved_validation_set:

- ghog day (sources: project, plan)
- rg -n 'def classify|class _Progress|def postfix|def setup_reason' tools/groundhog/commands.py (sources: plan)
- rg -n 'from tools.groundhog import .*commands' tools/groundhog/levels.py tools/groundhog/proof.py tools/groundhog/verdicts.py (sources: plan)

commit_plan_result:

```text
state: valid
ready: true
group 1: docs(full_suite_levels): code-span transcript paths
group 1 path: docs/v0.13.0/review.code.v0.13.0.full_suite_levels.md
group 2: refactor(groundhog): extract verdicts and progress
group 2 path: tools/groundhog/verdicts.py
group 2 path: tools/groundhog/progress.py
group 2 path: tools/groundhog/commands.py
group 2 path: tools/groundhog/cli.py
group 2 path: tools/groundhog/status.py
group 2 path: tests/unit/tools/test_groundhog_verdicts/__init__.py
group 2 path: tests/unit/tools/test_groundhog_verdicts/test_groundhog_verdicts_tdd.py
group 2 path: tests/unit/tools/test_groundhog_progress/__init__.py
group 2 path: tests/unit/tools/test_groundhog_progress/test_groundhog_progress_tdd.py
group 2 path: tests/unit/tools/test_groundhog_cli.py
group 2 path: tests/unit/tools/test_groundhog_commands.py
group 3: feat(groundhog): add level, proof and marker models
group 3 path: tools/groundhog/levels.py
group 3 path: tools/groundhog/proof.py
group 3 path: tools/groundhog/snapshot.py
group 3 path: tools/groundhog/__init__.py
group 3 path: tests/unit/tools/test_groundhog_levels/__init__.py
group 3 path: tests/unit/tools/test_groundhog_levels/test_groundhog_levels_tdd.py
group 3 path: tests/unit/tools/test_groundhog_levels/test_groundhog_levels_pbt.py
group 3 path: tests/unit/tools/test_groundhog_proof/__init__.py
group 3 path: tests/unit/tools/test_groundhog_proof/test_groundhog_proof_tdd.py
group 3 path: tests/unit/tools/test_groundhog_proof/test_groundhog_proof_pbt.py
group 3 path: tests/unit/tools/test_groundhog_snapshot_marker/__init__.py
group 3 path: tests/unit/tools/test_groundhog_snapshot_marker/test_groundhog_snapshot_marker_tdd.py
group 4: docs(full_suite_levels): record step 1 validation
group 4 path: docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md
staged path: docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md
staged path: docs/v0.13.0/review.code.v0.13.0.full_suite_levels.md
staged path: tests/unit/tools/test_groundhog_cli.py
staged path: tests/unit/tools/test_groundhog_commands.py
staged path: tests/unit/tools/test_groundhog_levels/__init__.py
staged path: tests/unit/tools/test_groundhog_levels/test_groundhog_levels_pbt.py
staged path: tests/unit/tools/test_groundhog_levels/test_groundhog_levels_tdd.py
staged path: tests/unit/tools/test_groundhog_progress/__init__.py
staged path: tests/unit/tools/test_groundhog_progress/test_groundhog_progress_tdd.py
staged path: tests/unit/tools/test_groundhog_proof/__init__.py
staged path: tests/unit/tools/test_groundhog_proof/test_groundhog_proof_pbt.py
staged path: tests/unit/tools/test_groundhog_proof/test_groundhog_proof_tdd.py
staged path: tests/unit/tools/test_groundhog_snapshot_marker/__init__.py
staged path: tests/unit/tools/test_groundhog_snapshot_marker/test_groundhog_snapshot_marker_tdd.py
staged path: tests/unit/tools/test_groundhog_verdicts/__init__.py
staged path: tests/unit/tools/test_groundhog_verdicts/test_groundhog_verdicts_tdd.py
staged path: tools/groundhog/__init__.py
staged path: tools/groundhog/cli.py
staged path: tools/groundhog/commands.py
staged path: tools/groundhog/levels.py
staged path: tools/groundhog/progress.py
staged path: tools/groundhog/proof.py
staged path: tools/groundhog/snapshot.py
staged path: tools/groundhog/status.py
staged path: tools/groundhog/verdicts.py
```

### Requestor assessment for step 1 full_suite_levels (round 1)

Step 1 is fully implemented. The validation plan records the exact Yes
verdict for Step 1; Steps 2 to 8 remain pending, so its document-level line
stays `No, it is not implemented.` and its theme sentence now names Steps 0 and
1 as checked. The day walk itself is unchanged: the new level, proof and
marker models are pure and not wired yet.

The groundhog walk (`ghog day`, the Step 1 gate arguments) finished on
2026-10-02 at 11:57:02 +02:00 with `exit=0`, and `ghog status` reports
`state=done exit=0`. Ty, Pyright, Ruff, Radon, Vulture, the 650-line big-file
gate, the Markdown check, ShellCheck and the EOF check passed. The affected
phase reported `fail=0`; the full phase reported `fail=0 warn=0 xfail=5
cov=100`, the five xfails being the Step 0 gates, which stay strict `xfail`.

Earlier walks of the step stopped on fixed causes: Ruff S105 on a constant
named `UNPROVEN_TOKEN` (renamed `UNPROVEN`), Radon grade C on the marker parser
(split into `_marker_values` and `_parse_marker`), Pyright
`reportUnknownLambdaType` on three lambdas passed through
`dataclasses.replace` (typed local functions now), and the Markdown check
MD050 on bare `__init__.py` paths in the committed Step 0 transcript (now code
spans). One walk at 11:47 crashed in the xdist scheduler with a `KeyError` on
a worker controller and no failing test ids; `ghog single` on the eight step
test targets then passed in focus (158 tests, the five gates xfailed) and the
next walk was green, so the crash did not reproduce.

Both plan completion patterns return nothing:
`def classify|class _Progress|def postfix|def setup_reason` over
`tools/groundhog/commands.py`, and `from tools.groundhog import .*commands`
over `levels.py`, `proof.py` and `verdicts.py`. No groundhog acceptance test
was edited.

Coverage is configured for `tools` and omits `*/tests/*` and
`*/__init__.py`; every staged production file is measured and the walk reached
`cov=100`. Each new module has its own test package that covers it alone
(verdicts, progress, levels, proof, and the marker additions of `snapshot.py`
beside the unchanged legacy snapshot tests). The two edited legacy files,
`test_groundhog_commands.py` and `test_groundhog_cli.py`, now cover their
namesake modules on their own.

`commands.py` is at 415 lines, under the mandatory 500. Every other file stays
below 550; counts above their advisory estimates are recorded as variance.
`levels.py` and `proof.py` touch no file, process or environment, `proof.py`
reads markers through the `SavedProof` protocol it declares, and `snapshot.py`
depends on them, never the reverse. No new `O(n^2)` or `O(n log n)` computation
was added; `source_files` keeps the one existing sort.

### Implementation report for step 1 full_suite_levels (round 1)

Freed `tools/groundhog/commands.py` and added the pure models of the leveled
walk, with no behavior change.

Extraction from `commands.py` (637 to 415 lines):

- `tools/groundhog/verdicts.py`: `classify`, `_classify_no_tests`,
  `_classify_coverage`, `setup_reason` and `measures_coverage` (the former
  `_measures_coverage`), moved verbatim.
- `tools/groundhog/progress.py`: `Progress` (the former `_Progress`) and
  `postfix`, moved verbatim, plus `sub_label`. `Progress` calls `sub_label`,
  so leaving the label in `commands.py` would have made `progress` import
  `commands`, which imports `progress`. `cli.run_exclude` and
  `status.run_with_lifecycle` now call `progress.sub_label`, a one-line change
  each; two `cli.py` comments that called `commands.py` at its line budget now
  say it was.
- `commands.py` imports both modules, renames its local sink variable to
  `sink`, and keeps its CRLF line endings.

New pure models:

- `tools/groundhog/levels.py`: `FullLevel` (`IntEnum`, `NONE < PASS < COV <
  SPEED`, with `token`), `LevelSource`, `ResolvedLevel`, `ACCEPTED_LEVELS`,
  `GHOG_FULL_ENV`, `LevelError(GroundhogError)` with the message
  `invalid full level '<value>' from <--full|GHOG_FULL>; accepted values:
  pass, cov, speed`, `command_default`, `resolve_level(sub, param, environ)`
  (the parameter wins and the variable is then not read; an empty variable is
  absent; no stripping or case folding), `effective_level`, `level_selector`
  (empty at `none`), `proof_token` (`unproven` for `None`) and
  `level_from_token` for the marker reader.
- `tools/groundhog/proof.py`: `Gate` (valued by the lowest level its failure
  contradicts), `Decision`, `accumulate(earned, saved, contradicted)`,
  `cap_for_timing`, `decide(saved, requested, *, digest_matches,
  timing_matches, force)`, `effective_saved(marker, *, scope_key,
  fingerprint, digest, timing)` and `earned_by_direct_full(level, exit_code,
  *, parallel)`, which follows the design's direct full table (a failing run
  keeps the level below its one failed gate only when that gate was judged at
  the run's level). The `SavedProof` protocol is the marker port.
- `tools/groundhog/snapshot.py`: `ProofMarker`, `read_proof_marker` (exactly
  the five keys in order, a `whole` or valid `group:<name>` scope, lowercase
  sha256 hex for fingerprint, timing and digest, a known proof token),
  `write_proof_marker` (side file then `replace`, an `OSError` logged),
  `remove_proof_marker`, `marker_path_for`, the public `source_files`,
  `source_digest(root, files=None)`, `timing_fingerprint` (the active gate
  floor and the exclusion entries in file order, line 1 left out) and
  `WHOLE_SCOPE_FINGERPRINT`. `is_unchanged` and `write_marker` stay for Step 2.
- `tools/groundhog/__init__.py`: the package docstring names the new modules.

Tests:

- New packages `test_groundhog_verdicts`, `test_groundhog_progress`,
  `test_groundhog_levels` (TDD and PBT), `test_groundhog_proof` (TDD and PBT)
  and `test_groundhog_snapshot_marker`, each with an initializer docstring and
  `# eof`. The classify and setup-reason cases moved unchanged from
  `test_groundhog_cli.py`, the outliers-last case from
  `test_groundhog_commands.py`, and the label and postfix cases to
  `test_groundhog_progress`. `test_groundhog_progress` is not in the plan's
  file list; it exists so `progress.py` reaches 100% in its own package.
- The proof tests encode every example of the design's "Proof after a walk"
  and the direct full table; the PBT files check the rejection of any
  non-accepted level from either source, the accumulation bounds, noop exactly
  when requested <= saved, walk on `--force` or a stale digest, and the timing
  cap.
- `test_groundhog_commands.py` gains nine CLI-driven tests and
  `test_groundhog_cli.py` four dispatch tests, so each covers its namesake
  module on its own, as the implement-step rule asks of an edited legacy unit
  test.

Documentation:

- The validation plan's Step 1 section records the Yes verdict, evidence, line
  counts and the four checks.
- The Step 0 code review transcript wraps its staged-path and commit-plan
  paths in code spans; formatting only, needed for the Markdown check.

Writer notes: `.reviews/a.full_suite_levels.step1.journal.md` and
`.reviews/a.full_suite_levels.step1.handoff.md`.

### Change summary for step 1 full_suite_levels (round 1)

Twenty-five staged paths are covered by the mechanically valid root
`a.commit` (`commit-plan-check` reports `state: valid`, `ready: true`, no
diagnostics):

1. docs(full_suite_levels): code-span transcript paths
   - `docs/v0.13.0/review.code.v0.13.0.full_suite_levels.md`
2. refactor(groundhog): extract verdicts and progress
   - `tools/groundhog/verdicts.py`
   - `tools/groundhog/progress.py`
   - `tools/groundhog/commands.py`
   - `tools/groundhog/cli.py`
   - `tools/groundhog/status.py`
   - `tests/unit/tools/test_groundhog_verdicts/__init__.py`
   - `tests/unit/tools/test_groundhog_verdicts/test_groundhog_verdicts_tdd.py`
   - `tests/unit/tools/test_groundhog_progress/__init__.py`
   - `tests/unit/tools/test_groundhog_progress/test_groundhog_progress_tdd.py`
   - `tests/unit/tools/test_groundhog_cli.py`
   - `tests/unit/tools/test_groundhog_commands.py`
3. feat(groundhog): add level, proof and marker models
   - `tools/groundhog/levels.py`
   - `tools/groundhog/proof.py`
   - `tools/groundhog/snapshot.py`
   - `tools/groundhog/__init__.py`
   - `tests/unit/tools/test_groundhog_levels/__init__.py`
   - `tests/unit/tools/test_groundhog_levels/test_groundhog_levels_tdd.py`
   - `tests/unit/tools/test_groundhog_levels/test_groundhog_levels_pbt.py`
   - `tests/unit/tools/test_groundhog_proof/__init__.py`
   - `tests/unit/tools/test_groundhog_proof/test_groundhog_proof_tdd.py`
   - `tests/unit/tools/test_groundhog_proof/test_groundhog_proof_pbt.py`
   - `tests/unit/tools/test_groundhog_snapshot_marker/__init__.py`
   - `tests/unit/tools/test_groundhog_snapshot_marker/test_groundhog_snapshot_marker_tdd.py`
4. docs(full_suite_levels): record step 1 validation
   - `docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md`

The independent transcript repair comes first. The extraction precedes the new
models because the package docstring of group 3 names `verdicts` and
`progress`, and the marker tests of group 3 import `proof`. The completed
validation record is the final documentation group with the exact
`record step 1 validation` title.

### Writer response for step 1 full_suite_levels (round 1)

Writer response:

This is the first implementation review round for Step 1. There is no earlier
code-review feedback on this step to accept or dispute.

Three choices go beyond the plan's file list and are stated for review:
`sub_label` moved to `progress.py` with `Progress` to avoid an import cycle,
which touches one line each in `cli.py` and `status.py`; a
`test_groundhog_progress` package was added so `progress.py` is covered in its
own package; and the two edited legacy test files were completed to cover
`commands.py` and `cli.py` on their own. `levels.py` reads the `SUB_FULL` name
from `runner.py`, where every groundhog module reads its subcommand names, and
calls nothing there.

### Reviewer focus for step 1 full_suite_levels (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-1-round-1 -->

## Round 1 by reviewer - Step 1

- Recorded: 2026-10-02T12:16:56+02:00
- Exchange: code/code/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/plan.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 1
- Outcome: answer

### Assessed index identity for step 1 full_suite_levels (exchange 1) (round 1)

Baseline index tree: 7b5934e6b965901f884da5221fcecf13fed7ebdc

Assessed index tree: 40dc600fbd6ddc1138c35e961ea8117f5453797c

### Implementation check for step 1 full_suite_levels (exchange 1) (round 1)

Result:

Yes. Step 1 has been fully implemented.

The extraction preserves verdict and progress behavior, updates the CLI/status callers, and reduces `tools/groundhog/commands.py` to 415 lines, below the step's 500-line limit. The new level resolver, proof rules and snapshot marker adapter match the step's contracts; live walk wiring remains assigned to Step 2. Step 0 acceptance tests are unchanged.

The static review covered parameter/environment/default precedence, invalid level tokens, command selection, accumulation and failure caps, timing demotion, noop/upgrade/walk decisions, scope/source fingerprints, direct-full outcomes, strict five-key marker parsing, atomic replacement and cleanup, timing fingerprints, and reuse of the source file list. TDD and property tests exercise the principal success, failure and boundary branches. The executable modules remain inside the configured unit coverage gate; no static coverage gap was found. This is an assessment of code and test coverage, not a fresh coverage measurement.

Dependencies keep pure proof rules independent of the snapshot adapter through the `SavedProof` protocol. The extraction introduces no command-layer cycle, and the new calculations add no material complexity or scaling concern. The progress test package and CLI/status changes support the planned extraction.

Validation plan effects:

Updated only the Step 1 section in `docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md`: added this independent assessment and corrected its description of the structurally compatible snapshot marker. Other steps and the document-level completion status are unchanged. No umbrella applies. The metadata patch was proven attributable before staging.

### Pre-repair mandatory checks and coverage for step 1 full_suite_levels (exchange 1) (round 1)

The requestor records a completed green `ghog day` at 2026-10-02 11:57:02 +02:00, confirmed by `ghog status`: check gates green; affected failures 0; full failures 0, warnings 0, five expected strict xfails, and coverage 100%. The request also records an earlier xdist scheduler failure followed by a successful focused run and green walk. The reviewer did not repeat the walk, run focused tests, or measure coverage; static inspection found no concern requiring optional reviewer test execution.

The independent commit-plan checker returned exit 0, state `valid`, `ready: true`, four groups and no diagnostics. A supplemental default `git diff --cached --check` reported preserved CRLF endings as whitespace; the read-only check with `core.whitespace=cr-at-eol` returned exit 0. No line endings or Git configuration were changed.

### Resolved validation set and sources for step 1 full_suite_levels (exchange 1) (round 1)

The ordered requestor validation set is:

1. `ghog day` — sources: project default and plan.
2. `rg -n 'def classify|class _Progress|def postfix|def setup_reason' tools/groundhog/commands.py` — source: plan; the moved definitions are expected to be absent.
3. `rg -n 'from tools.groundhog import .*commands' tools/groundhog/levels.py tools/groundhog/proof.py tools/groundhog/verdicts.py` — source: plan; command-layer imports are expected to be absent.

These commands remain requestor-owned. The reviewer inspected the corresponding source and diffs without running the resolved set.

### Resolver drift and direction for step 1 full_suite_levels (exchange 1) (round 1)

None. The request's ordered commands and source labels match the current resolver contract, project default and exact Step 1 plan. No `.review-validation` override exists.

### Repository state around validation for step 1 full_suite_levels (exchange 1) (round 1)

Request-time index and received baseline both equal `7b5934e6b965901f884da5221fcecf13fed7ebdc`. The assessed index is `40dc600fbd6ddc1138c35e961ea8117f5453797c`.

The before/after state tool reports `acceptable: false` with exactly the Step 1 validation document and `<index>` changed. Both changes are accounted for by the permitted, attributable reviewer metadata patch; there are no unrelated tracked changes or untracked/ignored validation side effects. No validation commands mutated the repository. The umbrella comparison is not applicable and unchanged.

### Repair inventory for step 1 full_suite_levels (exchange 1) (round 1)

Repairs made:

- No implementation or test repair was made. No literal `Human guidance:` repair authorization was present. The two validation-record edits are reviewer metadata only; their exact attributable patch was staged. `a.commit` required no amendment.

Paths staged:

- `docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md` (only the attributable reviewer metadata patch).

### Commit plan assessment for step 1 full_suite_levels (exchange 1) (round 1)

The independent checker returned `state: valid`, `ready: true`, and an empty diagnostics list, covering all 25 staged paths exactly once. The four ordered groups are:

1. `docs(full_suite_levels): code-span transcript paths`
2. `refactor(groundhog): extract verdicts and progress`
3. `feat(groundhog): add level, proof and marker models`
4. `docs(full_suite_levels): record step 1 validation`

Membership, dependency order, scope and conventional subjects are appropriate. The request describes the first group as a formatting correction to the prior generated transcript; it is separate from implementation. The reviewer did not use that transcript as working context. The validation metadata remains in its existing documentation group.

### Findings and boundaries for step 1 full_suite_levels (exchange 1) (round 1)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 1 full_suite_levels (exchange 1) (round 1)

No rework is requested. The `commit-ready` recommendation is advisory; the human owns the convergence choice and the requestor owns any subsequent commit workflow.

### Decision rationale for step 1 full_suite_levels (exchange 1) (round 1)

Recommend `commit-ready`. All six readiness checks pass: exact identity and baseline; complete Step 1 implementation; requestor green validation plus an independent static assessment with no coverage gap; attributable staged scope; no unresolved findings; and a mechanically valid, semantically appropriate commit plan. This round made no substantive repair. The recommendation does not authorize a commit.

### Final reviewer decision for step 1 full_suite_levels (exchange 1) (round 1)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-1-round-1 -->

## Round 1 by human - Step 1 - human-confirmation

- Recorded: 2026-10-02T13:00:49+02:00
- Exchange: code/code/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/plan.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 1
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-1 -->

## Round 1 by requestor - Step 2

- Recorded: 2026-10-02T18:33:07+02:00
- Exchange: code/code/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/plan.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Implementation step: 2
- Outcome: request

### Review identity for step 2 full_suite_levels (round 1)

Umbrella draft: none
Implementation plan: docs/v0.13.0/plan.v0.13.0.full_suite_levels.md
Implementation step: 2
Review round: 1

### Code review evidence for step 2 full_suite_levels (round 1)

request_index_tree: aca312cd26a47c059a00b97e56919a0f48567f4e
resolved_validation_set:

- ghog day --full=speed (sources: project)
- ghog day --full=cov (sources: plan)
- rg -n 'is_unchanged|write_marker\(' tools/groundhog (sources: plan)
- rg -n 'full=none|--full=default' tools/groundhog (sources: plan)
- rg -n '\x22ghog day\x22' tools/code_review_validation.py (sources: plan)
- rg -n 'call :run_one timings' bin/ghog_cycle.bat (sources: plan)

commit_plan_result:

```text
state: valid
ready: true
group 1: test(tools): answer git in process in slow tests
group 1 path: tests/unit/tools/test_prompt_workflow_docs_layout_acceptance/test_prompt_workflow_docs_layout_acceptance_tdd.py
group 1 path: tests/acceptance/review_resume/conftest.py
group 1 path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_concurrency_tdd.py
group 2: feat(groundhog): walk by level with saved proof
group 2 path: tools/groundhog/__init__.py
group 2 path: tools/groundhog/levels.py
group 2 path: tools/groundhog/context.py
group 2 path: tools/groundhog/runner.py
group 2 path: tools/groundhog/verdicts.py
group 2 path: tools/groundhog/durations_summary.py
group 2 path: tools/groundhog/evidence.py
group 2 path: tools/groundhog/snapshot.py
group 2 path: tools/groundhog/reporting_nextstep.py
group 2 path: tools/groundhog/reporting.py
group 2 path: tools/groundhog/commands.py
group 2 path: tools/groundhog/day.py
group 2 path: tools/groundhog/status.py
group 2 path: tools/groundhog/detach.py
group 2 path: tools/groundhog/cli.py
group 2 path: bin/ghog_cycle.bat
group 2 path: tests/unit/tools/conftest.py
group 2 path: tests/unit/tools/groundhog_acceptance_support.py
group 2 path: tests/unit/tools/test_groundhog_acceptance.py
group 2 path: tests/unit/tools/test_groundhog_acceptance_day.py
group 2 path: tests/unit/tools/test_groundhog_acceptance_durations.py
group 2 path: tests/unit/tools/test_groundhog_acceptance_levels/__init__.py
group 2 path: tests/unit/tools/test_groundhog_acceptance_levels/support.py
group 2 path: tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_levels_tdd.py
group 2 path: tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_proof_tdd.py
group 2 path: tests/unit/tools/test_groundhog_cli.py
group 2 path: tests/unit/tools/test_groundhog_commands.py
group 2 path: tests/unit/tools/test_groundhog_detach.py
group 2 path: tests/unit/tools/test_groundhog_evidence/__init__.py
group 2 path: tests/unit/tools/test_groundhog_evidence/test_groundhog_evidence_tdd.py
group 2 path: tests/unit/tools/test_groundhog_levels_perf/test_groundhog_levels_perf_tdd.py
group 2 path: tests/unit/tools/test_groundhog_reporting.py
group 2 path: tests/unit/tools/test_groundhog_reporting_nextstep.py
group 2 path: tests/unit/tools/test_groundhog_runner.py
group 2 path: tests/unit/tools/test_groundhog_snapshot.py
group 2 path: tests/unit/tools/test_groundhog_status.py
group 2 path: tests/unit/tools/test_groundhog_verdicts/test_groundhog_verdicts_tdd.py
group 3: feat(review): default validation proves speed
group 3 path: tools/code_review_validation.py
group 3 path: tests/unit/tools/test_code_review_validation/test_code_review_validation_tdd.py
group 3 path: tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py
group 3 path: tests/unit/tools/test_code_review_request_commit_plan/test_code_review_request_commit_plan_tdd.py
group 3 path: tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py
group 3 path: tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py
group 3 path: tests/unit/tools/test_code_reviewer_acceptance/fixtures.py
group 3 path: tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_acceptance_tdd.py
group 4: feat(prepare-release): prove cov before merging
group 4 path: tools/prepare_release/prepare_release_plan_workflow.py
group 4 path: tests/unit/tools/prepare_release/test_prepare_release_plan_workflow.py
group 5: docs(full_suite_levels): record step 2 validation
group 5 path: docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md
staged path: bin/ghog_cycle.bat
staged path: docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md
staged path: tests/acceptance/review_resume/conftest.py
staged path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_concurrency_tdd.py
staged path: tests/unit/tools/conftest.py
staged path: tests/unit/tools/groundhog_acceptance_support.py
staged path: tests/unit/tools/prepare_release/test_prepare_release_plan_workflow.py
staged path: tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py
staged path: tests/unit/tools/test_code_review_request_commit_plan/test_code_review_request_commit_plan_tdd.py
staged path: tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py
staged path: tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py
staged path: tests/unit/tools/test_code_review_validation/test_code_review_validation_tdd.py
staged path: tests/unit/tools/test_code_reviewer_acceptance/fixtures.py
staged path: tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_acceptance_tdd.py
staged path: tests/unit/tools/test_groundhog_acceptance.py
staged path: tests/unit/tools/test_groundhog_acceptance_day.py
staged path: tests/unit/tools/test_groundhog_acceptance_durations.py
staged path: tests/unit/tools/test_groundhog_acceptance_levels/__init__.py
staged path: tests/unit/tools/test_groundhog_acceptance_levels/support.py
staged path: tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_levels_tdd.py
staged path: tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_proof_tdd.py
staged path: tests/unit/tools/test_groundhog_cli.py
staged path: tests/unit/tools/test_groundhog_commands.py
staged path: tests/unit/tools/test_groundhog_detach.py
staged path: tests/unit/tools/test_groundhog_evidence/__init__.py
staged path: tests/unit/tools/test_groundhog_evidence/test_groundhog_evidence_tdd.py
staged path: tests/unit/tools/test_groundhog_levels_perf/test_groundhog_levels_perf_tdd.py
staged path: tests/unit/tools/test_groundhog_reporting.py
staged path: tests/unit/tools/test_groundhog_reporting_nextstep.py
staged path: tests/unit/tools/test_groundhog_runner.py
staged path: tests/unit/tools/test_groundhog_snapshot.py
staged path: tests/unit/tools/test_groundhog_status.py
staged path: tests/unit/tools/test_groundhog_verdicts/test_groundhog_verdicts_tdd.py
staged path: tests/unit/tools/test_prompt_workflow_docs_layout_acceptance/test_prompt_workflow_docs_layout_acceptance_tdd.py
staged path: tools/code_review_validation.py
staged path: tools/groundhog/__init__.py
staged path: tools/groundhog/cli.py
staged path: tools/groundhog/commands.py
staged path: tools/groundhog/context.py
staged path: tools/groundhog/day.py
staged path: tools/groundhog/detach.py
staged path: tools/groundhog/durations_summary.py
staged path: tools/groundhog/evidence.py
staged path: tools/groundhog/levels.py
staged path: tools/groundhog/reporting.py
staged path: tools/groundhog/reporting_nextstep.py
staged path: tools/groundhog/runner.py
staged path: tools/groundhog/snapshot.py
staged path: tools/groundhog/status.py
staged path: tools/groundhog/verdicts.py
staged path: tools/prepare_release/prepare_release_plan_workflow.py
```

### Requestor assessment for step 2 full_suite_levels (round 1)

Step 2 is fully implemented. The validation plan records the exact Yes verdict
for Step 2; Steps 3 to 8 remain pending, so its document-level line stays
`No, it is not implemented.` and its theme sentence now names Steps 0 to 2 as
checked.

The plan's gate walk, `ghog day --full=cov`, ended on 2026-10-02 at 17:03:53
+02:00 with `exit=0`: check green, `ghog affected --no-cov` green, the
parallel `ghog full` green with `xfail=2` (the two Step 4 cost gates) and
`cov=100`, closing `full=cov src=param proof=cov reused=none scope=whole`.
`ghog status` replayed that done line with `exit=0`. The three Step 2 cost
gates pass without `xfail`.

The project default of the request's validation set is now
`ghog day --full=speed`. Its first run upgraded from the saved `cov` proof:
check and affected reused, the full run green. It then failed the sequential
timing pass on eight pre-existing Git-bound test calls (exit 8, `proof=cov`).
Those calls were shortened, not excluded, as the implementation report
details. The final `ghog day --full=speed` walk ended at 18:29:53 +02:00 with
`exit=0` on the whole chain: check, affected, the full run at `cov=100`, and
the timing pass with `outliers=0 excluded=0` (slowest call 0.77s), closing
`proof=speed reused=none`. A following `ghog day --full=cov` was a noop met
by that saved `speed` proof.

Ty, Pyright, Ruff, Radon, Vulture, the 650-line big-file gate, the Markdown
check, ShellCheck and the EOF check passed. Earlier walks of the step stopped
on fixed causes:

- Radon grade C on `runner.pytest_command`, fixed by extracting `_measures`.
- Radon grade C on the AT11 `--full=cov` test, fixed by folding its asserts.
- Three coverage lines, fixed by removing the two unused integer wrappers and
  adding the exit-5 and exit-9 no-gate walk cases.
- A Pyright tuple-key type and a Ruff TC004 in the two repaired acceptance
  modules.

The four plan completion patterns return nothing:

- `is_unchanged|write_marker\(` over `tools/groundhog`;
- `full=none|--full=default` over `tools/groundhog`;
- `"ghog day"` over `tools/code_review_validation.py`;
- `call :run_one timings` over `bin/ghog_cycle.bat`.

Coverage is configured for `tools` and omits `*/tests/*` and
`*/__init__.py`; every staged production file is measured and the walks
reached `cov=100`. The new `evidence.py` and `detach.py` have their own test
packages (`test_groundhog_evidence`, `test_groundhog_detach.py`).
`day.py` is covered by its level and proof acceptance package and the day
acceptance file. Each other edited module is covered by its namesake test:
the runner, reporting, next-step, status, snapshot, CLI, commands and
verdicts tests.

Every Python file stays at or below 650 lines. `status.py` passed the plan's
550 trigger and was split as its guidance prescribes (391 lines, plus
`detach.py` at 194). `reporting_nextstep.py` is at 561, inside the 550-to-650
band and above its advisory estimate; that is recorded as variance.

`levels.py` and `proof.py` stay pure, and `levels.py` no longer imports the
`runner` adapter. The environment is read only through `Deps.environ`. No new
`O(n^2)` or `O(n log n)` computation was added: a walk computes one digest
over the existing sorted file walk, reads one five-line marker, and reads the
floor file only when a marker exists and once at the write.

### Implementation report for step 2 full_suite_levels (round 1)

Wired the full-suite levels and the saved proof through groundhog, and moved
every caller that needs a full-suite proof to its explicit level.

Level resolution and run shapes:

- `context.Invocation` gains `level` (`None` means the command default),
  `level_source` and `in_walk`; `context.Deps` gains `environ`, the only read
  of `GHOG_FULL`.
- `cli.py`: a `leveled` parent parser gives `check`, `full`, `affected`,
  `single` and `day` a free-string `--full`; `main` resolves the level once,
  after the root and before the live-run check and the lifecycle bracket, and
  a `LevelError` prints
  `ghog: invalid full level '<value>' from <--full|GHOG_FULL>; accepted values: pass, cov, speed`
  and returns 5 (never argparse's 2) without writing `a.ghog.status`.
- `runner.pytest_command(..., level=FullLevel.SPEED)`: a `full` run at `pass`
  carries `--no-cov` and no `--durations`, at `cov` it is covered without
  `--durations`, at `speed` it is unchanged; `_measures` holds the decision.
  `verdicts.measures_coverage` is false for `full` at `pass`, and
  `durations_summary.measures_durations` probes at the effective level.

Proof and the walk:

- `tools/groundhog/evidence.py` (new): `Reused`, `RunEvidence` with
  `closing_keys` and `running_keys`, `RunOutcome`, and `for_invocation`.
- `snapshot.py`: the one-line digest writer and its comparison are removed;
  `effective_proof` returns the digest and the saved proof valid for it
  through `proof.effective_saved`, and `save_proof` writes or removes the
  scope marker with a timing fingerprint taken after the walk's writes.
- `day.walk`: noop (noop line, `reused=all`, not even check.bat runs), upgrade
  (reused headers for check and affected, `reused=check+affected`) or the
  whole chain; stop with the skip line at `none`; the full step at the level;
  at parallel `speed` a timed sequential `timings` step after a green full
  step. Failed gates cap the accumulated proof; the marker is rewritten or
  removed; exits 5 and 9 write nothing. The walk ends with a `ghog day done`
  closing line that repeats the last step's counters and appends the five
  keys.
- `commands.run_tests_outcome` returns a `RunOutcome`; a direct `ghog full`
  reports `proof.earned_by_direct_full`, and a green parallel run at `speed`
  prints the `cov` success line and the durations-not-measured line.

Reports and lifecycle:

- `reporting_nextstep.py`: every fixed restart string is a builder over
  `restart_command(level, scope_selector="")` and `carried_selector`, never
  printing a `none` selector; one success line per level; the noop line; the
  covered-affected gate-reached line naming `ghog check` then the walk; a
  standalone `ghog affected --no-cov` with no level keeps `Next: ghog full`;
  `StepContext` carries level, walk and parallel flags; the exclusion hint
  says an exclusion is accepted only after an attempted improvement.
- `reporting.py`: `ClosingMetrics.evidence` appended after `exit=`,
  `step_reused_line`, `status_killed_line(level)`, and a crash block that
  restarts at the carried level.
- `status.py`: the running line adds `full= src= scope= proof=pending`, the
  done line the closing keys before `exit=`; `_dispatch` returns a
  `RunOutcome`; a killed run relaunches at its recorded `full=`.
- `detach.py` (new, the plan's split of `status.py` past 550 lines): the
  detached launch and the survivor spawn, forwarding `--full` only for a
  `param` level.
- `levels.py` drops its `runner` import; the integer wrappers `run_day` and
  `run_tests` are removed (no caller).

Callers:

- `code_review_validation.DEFAULT_PROJECT_VALIDATION_COMMANDS` is
  `("ghog day --full=speed",)`.
- `prepare_release_plan_workflow.py` names `run ghog day --full=cov` and
  `run git range-diff and ghog day --full=cov`.
- `bin/ghog_cycle.bat` runs `day` alone when called with no argument.

Tests:

- New `test_groundhog_acceptance_levels` package: a shared `support` module,
  one test per level row of the design acceptance table, one per proof row,
  plus the exit-5 (full step and timing pass) and exit-9 no-gate cases, a
  detached `--full=cov` walk run in process and observed through
  `ghog status`, and the `ghog_cycle.bat` file-content contract.
- New `test_groundhog_evidence` package.
- AT11 and AT16 of `test_groundhog_acceptance_day.py` now cover the default
  two-step walk, the `--full=cov` chain, the proof marker and its removal.
- Runner, reporting, next-step (the Q30 rule now also forbids a `none`
  selector at every level), status, detach, snapshot, CLI, commands, verdicts
  and acceptance tests follow the builders and the keys.
- The shared `conftest.py` clears `GHOG_FULL` for every unit test, and
  `make_deps` takes an `environ` mapping.
- The three Step 2 cost gates in `test_groundhog_levels_perf` lose their
  `xfail` and keep their timeout.
- Review tests carry the new default literal; the prepare-release planner
  tests pin both operation strings.

Speed repairs made for this round's validation:

The first `ghog day --full=speed` walk on these sources was also the first
walk that ever judged speed in this parallel project. It flagged eight
pre-existing calls above the one-second floor, none of them in code this
step touches: seven in `test_prompt_workflow_docs_layout_acceptance_tdd.py`
(6.21s, 2.70s, 2.66s, 2.59s, 1.31s, 1.29s, 1.25s) and the foreground
cancellation of `test_review_resume_concurrency_tdd.py` (1.27s). Profiling
put the time in real `git` spawns of about 0.13s each. No call is excluded;
each test is now fast, with every assertion kept:

- `test_prompt_workflow_docs_layout_acceptance_tdd.py`: every scenario runs on
  one repository state, a branch freshly created from `main` with each effort
  file untracked. Each `pw` call spawned four to six `git` reads for it. A
  recording of the call phase showed six distinct read commands.
  `_FreshBranchGit` replaces `prompt_workflow_git.run_git`, the seam that
  module documents for tests. It answers those six commands from the files
  actually on disk and fails on any other command, so a new git dependency
  of `pw` cannot pass unnoticed. The fixture no longer builds a real
  repository. The `git` helpers above the seam still run, and
  `test_prompt_workflow_git.py` keeps covering `run_git` itself. The slowest
  call is now 0.10s.
- `test_review_resume_concurrency_tdd.py`: the in-process cancellation's
  preflight spawned four `git` processes, three home-tracking checks and one
  ignore check. `_IgnoredHomeGit` stands in for `subprocess.run` during that
  one call and answers both reads as real git does for the fixture's
  self-ignored home. Any other command, or a query outside the home, fails
  the test. The call is now 0.02s, and the package's process-based scenarios
  keep the real git path covered.
- `tests/acceptance/review_resume/conftest.py`: `ReviewRepository` copies a
  seed repository built once per test process and per home and family,
  under pytest's temporary root, instead of running `git init`, two
  configuration writes, an add and a commit for every scenario. Each copy
  loads its configuration once, which also cuts the fixture setup that
  precedes the measured calls.

Writer notes: `.reviews/a.full_suite_levels.step2.journal.md` and
`.reviews/a.full_suite_levels.step2.handoff.md`.

### Change summary for step 2 full_suite_levels (round 1)

Fifty-one staged paths are covered by the mechanically valid root
`a.commit` (`commit-plan-check` reports `state: valid`, `ready: true`, no
diagnostics):

1. test(tools): answer git in process in slow tests
   - `tests/unit/tools/test_prompt_workflow_docs_layout_acceptance/test_prompt_workflow_docs_layout_acceptance_tdd.py`
   - `tests/acceptance/review_resume/conftest.py`
   - `tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_concurrency_tdd.py`
2. feat(groundhog): walk by level with saved proof
   - `tools/groundhog/__init__.py`, `levels.py`, `context.py`, `runner.py`,
     `verdicts.py`, `durations_summary.py`, `evidence.py` (new),
     `snapshot.py`, `reporting_nextstep.py`, `reporting.py`, `commands.py`,
     `day.py`, `status.py`, `detach.py` (new), `cli.py`
   - `bin/ghog_cycle.bat`
   - `tests/unit/tools/conftest.py`,
     `tests/unit/tools/groundhog_acceptance_support.py`
   - `tests/unit/tools/test_groundhog_acceptance_levels/` (new: `__init__.py`,
     `support.py`, `test_groundhog_acceptance_levels_tdd.py`,
     `test_groundhog_acceptance_proof_tdd.py`)
   - `tests/unit/tools/test_groundhog_evidence/` (new: `__init__.py`,
     `test_groundhog_evidence_tdd.py`)
   - `tests/unit/tools/test_groundhog_acceptance.py`,
     `test_groundhog_acceptance_day.py`,
     `test_groundhog_acceptance_durations.py`, `test_groundhog_cli.py`,
     `test_groundhog_commands.py`, `test_groundhog_detach.py`,
     `test_groundhog_reporting.py`, `test_groundhog_reporting_nextstep.py`,
     `test_groundhog_runner.py`, `test_groundhog_snapshot.py`,
     `test_groundhog_status.py`,
     `test_groundhog_levels_perf/test_groundhog_levels_perf_tdd.py`,
     `test_groundhog_verdicts/test_groundhog_verdicts_tdd.py`
3. feat(review): default validation proves speed
   - `tools/code_review_validation.py`
   - `tests/unit/tools/test_code_review_validation/test_code_review_validation_tdd.py`
   - `tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py`
   - `tests/unit/tools/test_code_review_request_commit_plan/test_code_review_request_commit_plan_tdd.py`
   - `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py`
   - `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py`
   - `tests/unit/tools/test_code_reviewer_acceptance/fixtures.py`
   - `tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_acceptance_tdd.py`
4. feat(prepare-release): prove cov before merging
   - `tools/prepare_release/prepare_release_plan_workflow.py`
   - `tests/unit/tools/prepare_release/test_prepare_release_plan_workflow.py`
5. docs(full_suite_levels): record step 2 validation
   - `docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md`

The test-speed group comes first: it depends on nothing in this step and
shortens the eight pre-existing calls the `speed` validation flagged. The
groundhog group follows: the two caller groups name `--full`, which only
exists once it lands. Its production modules and tests cannot be split by
file, because the tests pin the level-aware builders and the evidence keys
that the same modules introduce. The completed validation record is the final
documentation group with the exact `record step 2 validation` title.

### Writer response for step 2 full_suite_levels (round 1)

Writer response:

This is the first implementation review round for Step 2. There is no earlier
code-review feedback on this step to accept or dispute.

Five choices depart from the plan's wording and are stated for review:

- The closing-line evidence travels as a `ClosingMetrics.evidence` field, not
  as a sixth `closing_line` argument: the value object exists to keep the line
  at the project's five-argument lint limit. The rendered line is the one the
  plan describes, keys appended after `exit=`.
- `Invocation` gains `in_walk` beside `level` and `level_source`: the design
  requires a green affected step inside a walk to stop printing
  `Next: ghog full`, and a parallel `speed` full step inside a walk to leave
  its success line to the timing pass, so a step report has to know it runs
  inside the walk.
- `status.py` reached 555 lines, past the plan's 550 extraction trigger, so
  the plan's split guidance was applied in this step: the detached launch and
  the survivor spawn now live in `tools/groundhog/detach.py`.
- The integer wrappers `day.run_day` and `commands.run_tests` are removed. The
  plan's Q05 kept them to avoid test churn; once the status dispatch uses
  `walk` and `run_tests_outcome`, no caller and no test calls them, so keeping
  them would only leave dead code.
- `levels.py` no longer imports `runner`: `runner.pytest_command` now imports
  `FullLevel`, and the old import became a load-order cycle when `levels`
  loads first; the pure model also stops depending on the process adapter.

The plan's Step 2 gate is `ghog day --full=cov`; the request's resolved set
also carries the new project default `ghog day --full=speed`, which was run
green on the same sources before this request. Reaching `speed` required
shortening eight pre-existing Git-bound test calls: two acceptance test
modules now answer their `git` reads in process, and the `review_resume`
acceptance fixture copies a once-built seed repository. No call is excluded,
and no production file outside this step changed for them; the
implementation report details each repair.

### Reviewer focus for step 2 full_suite_levels (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-2-round-1 -->

## Round 1 by reviewer - Step 2

- Recorded: 2026-10-02T19:19:02+02:00
- Exchange: code/code/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/plan.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 2
- Outcome: answer

### Assessed index identity for step 2 full_suite_levels (exchange 1) (round 1)

Baseline index tree: aca312cd26a47c059a00b97e56919a0f48567f4e

Assessed index tree: 09fad0a4940f192b31590a9706314b62a65e11e2

### Implementation check for step 2 full_suite_levels (exchange 1) (round 1)

Result:

No. Step 2 has NOT been fully implemented.

The level model, CLI resolution, level-shaped full runs, proof reuse and cap model, evidence/status/detach wiring, and caller defaults are present. Two gaps remain: interrupted pytest children are treated as failed proof gates (R1), and a single-run report without a failure baseline drops its selected level (R2). The exact Step 2 validation rows now record both gaps and their required regressions.

The model/adapter separation is coherent; the detach extraction follows the plan's threshold. No new quadratic computation or separate performance blocker was found. Removal of the unused integer wrappers and the ClosingMetrics evidence field are disclosed implementation variations with no observed remaining caller. Later-step scope/group and documentation work was not assessed as missing Step 2 work.

Static coverage review: pyproject.toml measures source=["tools"] and excludes tests, `__init__.py` and named thin adapters. All changed executable production files are in measured scope. The existing unit tests cover the principal level, proof, reporting, runner, status, snapshot and CLI paths. R1 and R2 require behavioral regressions; the requestor's 100% line result does not establish those cases.

Validation plan effects:

Changed only Step 2 rows in docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md: the exact No sentence, short rationale, Missing work for Step 2 after What was implemented, static coverage qualification and feature-integrity conclusion. Other steps, the plan, implementation, tests and a.commit were not edited. The evidence launcher attributed the patch from pre-edit blob 673a817c9ab4645ee0c8d5ca550ecead5c8000c5; only that patch was staged. This is review metadata, not a substantive repair.

### Pre-repair mandatory checks and coverage for step 2 full_suite_levels (exchange 1) (round 1)

Requestor evidence: ghog day --full=cov completed 2026-10-02 17:03:53 +02:00 with exit=0 and cov=100; ghog day --full=speed completed 18:29:53 +02:00 with exit=0, cov=100, outliers=0 and excluded=0. The request records the remaining two strict xfails as Step 4 gates and a later cov noop met by saved speed proof.

Reviewer evidence: static inspection of the exact staged implementation and tests, request-time tree comparison, independent commit-plan-check, attribution and before/after repository-state checks. Neither ghog check nor ghog affected --no-cov was needed to establish these deterministic branch defects. No test, full walk or coverage measurement was run by the reviewer. Requestor validation is reported evidence, not an independently repeated result.

### Resolved validation set and sources for step 2 full_suite_levels (exchange 1) (round 1)

The request and current resolver produce the same ordered set and sources:

1. ghog day --full=speed — project.
2. ghog day --full=cov — plan.
3. rg -n 'is_unchanged|write_marker\(' tools/groundhog — plan.
4. rg -n 'full=none|--full=default' tools/groundhog — plan.
5. rg -n '\x22ghog day\x22' tools/code_review_validation.py — plan.
6. rg -n 'call :run_one timings' bin/ghog_cycle.bat — plan.

The local .review-validation file is absent; the current load_project_validation_commands default is ghog day --full=speed. resolve_code_review_validation preserves this default followed by the Step 2 additions, with no request additions. This comparison was made from the current resolver and exact plan/request; none of these requestor commands was executed by the reviewer.

### Resolver drift and direction for step 2 full_suite_levels (exchange 1) (round 1)

None. Ordered commands and source labels agree; no additions, removals or source-label drift.

### Repository state around validation for step 2 full_suite_levels (exchange 1) (round 1)

Request-time and reviewer baseline index: aca312cd26a47c059a00b97e56919a0f48567f4e. Final assessed index: 09fad0a4940f192b31590a9706314b62a65e11e2.

The same ordered 51-path validation set was captured before and after assessment. The helper reports tracked differences only for docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md and `<index>`, with no untracked or ignored differences. Its raw acceptable=false result reflects the intentional tracked review metadata edit; the diff and attribution prove all changed rows belong to Step 2. There is no tracked validation side effect or writer-work overlap. No runtime validation commands ran.

Umbrella: none. The launcher comparison is applicable=false, changed=false. No umbrella row was modified.

### Repair inventory for step 2 full_suite_levels (exchange 1) (round 1)

Repairs made:

- Review metadata only: changed Step 2 validation rows to No, recorded R1/R2 and their missing regression cases, and qualified the static coverage assessment. No implementation or test repair.

Paths staged:

- docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md (reviewer metadata patch only)

### Commit plan assessment for step 2 full_suite_levels (exchange 1) (round 1)

Independently ran commit-plan-check.bat --format json before assessment, and again after staging the Step 2 metadata. Both returned exit=0, state=valid, ready=true, five ordered groups, 51 staged paths and diagnostics=[]. The initial complete JSON is retained in .reviews/a.full_suite_levels.step2.tmp.r1.resume-commit-plan.json; the final JSON is retained in .reviews/a.full_suite_levels.step2.tmp.r1.final-commit-plan.json.

Ordered groups:

1. test(tools): answer git in process in slow tests (3 paths)
2. feat(groundhog): walk by level with saved proof (37 paths)
3. feat(review): default validation proves speed (8 paths)
4. feat(prepare-release): prove cov before merging (2 paths)
5. docs(full_suite_levels): record step 2 validation (1 paths)

Grouping separates the speed-test repairs, groundhog feature, review caller default, release caller default and validation documentation. Ordering, scoped membership and conventional subjects match the staged work; a.commit needs no amendment. Mechanical readiness does not resolve R1/R2 or authorize a commit.

### Findings and boundaries for step 2 full_suite_levels (exchange 1) (round 1)

Unresolved findings:

- R1 — P2 — Preserve saved proof when only the pytest child is interrupted. At tools/groundhog/day.py:83-87 and :155-156, only setup/no-suite exits are marked as no-gate, while every EXIT_SUITE_CRASH contradicts FULL_TESTS. runner.run_pytest (tools/groundhog/runner.py:272-275) sets crashed for PYTEST_INTERRUPTED and negative child exits as well as internal errors, and verdicts.classify maps them all to EXIT_SUITE_CRASH. Therefore a forced walk over saved speed proof whose full or timing child is interrupted downgrades the marker to none; an interruption during affected removes it. This violates the design's explicit rule that interrupted/lost runs judge no gate and keep saved proof unchanged. Carry a no-gate/interruption distinction through the run outcome and skip marker writes for those outcomes while retaining caps for actual suite errors/failures. Add saved-marker regression cases for affected, full and timings children interrupted before a verdict.
- R2 — P2 — Preserve the selected level in the no-baseline single-run guidance. At tools/groundhog/reporting_nextstep.py:534-535, comparison=None returns the unchanged MSG_NO_BASELINE, whose command is bare ghog full. Running ghog single tests/test_x.py --full=cov before any failure baseline exists therefore directs the caller to a default-speed run (or another GHOG_FULL value), losing the explicitly selected cov objective. Render the baseline-missing instruction from the carried level and cover pass, cov, speed and none without printing --full=none. The existing new single-run acceptance case creates a baseline and misses this path.

Boundary-crossing work: None.

### Writer instructions for step 2 full_suite_levels (exchange 1) (round 1)

Address R1 and R2 within Step 2 and add the specified regression cases. Reassess the Step 2 validation rows after the fixes. Run the requestor-owned resolved validation set, retaining fresh results and updating a.commit only if staged membership changes, then publish the replacement review request through the normal requestor workflow. No implementation or test repair was made by this reviewer, and no Human guidance block was supplied.

### Decision rationale for step 2 full_suite_levels (exchange 1) (round 1)

Recommend changes-requested. The six readiness-floor results are:

1. Identity — PASS: exact plan, step 2, round 1, occurrence 1, code identity and baseline index agree with the live request.
2. Implementation completeness — FAIL: R1 and R2 remain in the Step 2 proof and repair-message behavior.
3. Validation and coverage — INCOMPLETE: requestor cov/speed evidence is green and source scope includes the changed production files, but static review identifies the two missing behavioral regressions. Reviewer runtime/coverage checks were not repeated.
4. Staged attribution — PASS: the sole reviewer change is attributable Step 2 validation metadata; no substantive repair or unrelated staged work.
5. Unresolved findings — FAIL: R1 and R2 remain open.
6. a.commit — PASS: independent checker exit=0/state=valid/ready=true, all 51 paths in five accurate groups, diagnostics empty.

The implementation and unresolved-findings failures block commit-readiness despite the green reported walks and valid commit plan.

### Final reviewer decision for step 2 full_suite_levels (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-2-round-1 -->

## Round 2 by requestor - Step 2

- Recorded: 2026-10-02T20:41:53+02:00
- Exchange: code/code/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/plan.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 2
- Outcome: request

### Review identity for step 2 full_suite_levels (round 2)

Umbrella draft: none
Implementation plan: docs/v0.13.0/plan.v0.13.0.full_suite_levels.md
Implementation step: 2
Review round: 2

### Code review evidence for step 2 full_suite_levels (round 2)

request_index_tree: 49daf397a5af85d20ff109ffbda43ddf33b37ec8
resolved_validation_set:

- ghog day --full=speed (sources: project)
- ghog day --full=cov (sources: plan)
- rg -n 'is_unchanged|write_marker\(' tools/groundhog (sources: plan)
- rg -n 'full=none|--full=default' tools/groundhog (sources: plan)
- rg -n '\x22ghog day\x22' tools/code_review_validation.py (sources: plan)
- rg -n 'call :run_one timings' bin/ghog_cycle.bat (sources: plan)

commit_plan_result:

```text
state: valid
ready: true
group 1: test(tools): answer git in process in slow tests
group 1 path: tests/unit/tools/test_prompt_workflow_docs_layout_acceptance/test_prompt_workflow_docs_layout_acceptance_tdd.py
group 1 path: tests/acceptance/review_resume/conftest.py
group 1 path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_concurrency_tdd.py
group 1 path: tests/unit/tools/markdown_check/test_launcher/test_launcher_tdd.py
group 1 path: tests/unit/tools/test_review_resume/test_review_resume_lifecycle_tdd.py
group 2: feat(groundhog): walk by level with saved proof
group 2 path: tools/groundhog/__init__.py
group 2 path: tools/groundhog/levels.py
group 2 path: tools/groundhog/models.py
group 2 path: tools/groundhog/parser.py
group 2 path: tools/groundhog/proof.py
group 2 path: tools/groundhog/context.py
group 2 path: tools/groundhog/runner.py
group 2 path: tools/groundhog/verdicts.py
group 2 path: tools/groundhog/durations_summary.py
group 2 path: tools/groundhog/evidence.py
group 2 path: tools/groundhog/snapshot.py
group 2 path: tools/groundhog/reporting_nextstep.py
group 2 path: tools/groundhog/reporting.py
group 2 path: tools/groundhog/commands.py
group 2 path: tools/groundhog/day.py
group 2 path: tools/groundhog/status.py
group 2 path: tools/groundhog/detach.py
group 2 path: tools/groundhog/cli.py
group 2 path: bin/ghog_cycle.bat
group 2 path: tests/unit/tools/conftest.py
group 2 path: tests/unit/tools/groundhog_acceptance_support.py
group 2 path: tests/unit/tools/test_groundhog_acceptance.py
group 2 path: tests/unit/tools/test_groundhog_acceptance_day.py
group 2 path: tests/unit/tools/test_groundhog_acceptance_durations.py
group 2 path: tests/unit/tools/test_groundhog_acceptance_levels/__init__.py
group 2 path: tests/unit/tools/test_groundhog_acceptance_levels/support.py
group 2 path: tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_levels_tdd.py
group 2 path: tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_proof_tdd.py
group 2 path: tests/unit/tools/test_groundhog_cli.py
group 2 path: tests/unit/tools/test_groundhog_commands.py
group 2 path: tests/unit/tools/test_groundhog_detach.py
group 2 path: tests/unit/tools/test_groundhog_evidence/__init__.py
group 2 path: tests/unit/tools/test_groundhog_evidence/test_groundhog_evidence_tdd.py
group 2 path: tests/unit/tools/test_groundhog_levels_perf/test_groundhog_levels_perf_tdd.py
group 2 path: tests/unit/tools/test_groundhog_reporting.py
group 2 path: tests/unit/tools/test_groundhog_reporting_nextstep.py
group 2 path: tests/unit/tools/test_groundhog_runner.py
group 2 path: tests/unit/tools/test_groundhog_snapshot.py
group 2 path: tests/unit/tools/test_groundhog_status.py
group 2 path: tests/unit/tools/test_groundhog_verdicts/test_groundhog_verdicts_tdd.py
group 2 path: tests/unit/tools/test_groundhog_parser.py
group 2 path: tests/unit/tools/test_groundhog_proof/test_groundhog_proof_tdd.py
group 3: feat(review): default validation proves speed
group 3 path: tools/code_review_validation.py
group 3 path: tests/unit/tools/test_code_review_validation/test_code_review_validation_tdd.py
group 3 path: tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py
group 3 path: tests/unit/tools/test_code_review_request_commit_plan/test_code_review_request_commit_plan_tdd.py
group 3 path: tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py
group 3 path: tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py
group 3 path: tests/unit/tools/test_code_reviewer_acceptance/fixtures.py
group 3 path: tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_acceptance_tdd.py
group 4: feat(prepare-release): prove cov before merging
group 4 path: tools/prepare_release/prepare_release_plan_workflow.py
group 4 path: tests/unit/tools/prepare_release/test_prepare_release_plan_workflow.py
group 5: docs(full_suite_levels): record step 2 code review
group 5 path: docs/v0.13.0/review.code.v0.13.0.full_suite_levels.md
group 6: docs(full_suite_levels): record step 2 validation
group 6 path: docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md
staged path: bin/ghog_cycle.bat
staged path: docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md
staged path: docs/v0.13.0/review.code.v0.13.0.full_suite_levels.md
staged path: tests/acceptance/review_resume/conftest.py
staged path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_concurrency_tdd.py
staged path: tests/unit/tools/conftest.py
staged path: tests/unit/tools/groundhog_acceptance_support.py
staged path: tests/unit/tools/markdown_check/test_launcher/test_launcher_tdd.py
staged path: tests/unit/tools/prepare_release/test_prepare_release_plan_workflow.py
staged path: tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py
staged path: tests/unit/tools/test_code_review_request_commit_plan/test_code_review_request_commit_plan_tdd.py
staged path: tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py
staged path: tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py
staged path: tests/unit/tools/test_code_review_validation/test_code_review_validation_tdd.py
staged path: tests/unit/tools/test_code_reviewer_acceptance/fixtures.py
staged path: tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_acceptance_tdd.py
staged path: tests/unit/tools/test_groundhog_acceptance.py
staged path: tests/unit/tools/test_groundhog_acceptance_day.py
staged path: tests/unit/tools/test_groundhog_acceptance_durations.py
staged path: tests/unit/tools/test_groundhog_acceptance_levels/__init__.py
staged path: tests/unit/tools/test_groundhog_acceptance_levels/support.py
staged path: tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_levels_tdd.py
staged path: tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_proof_tdd.py
staged path: tests/unit/tools/test_groundhog_cli.py
staged path: tests/unit/tools/test_groundhog_commands.py
staged path: tests/unit/tools/test_groundhog_detach.py
staged path: tests/unit/tools/test_groundhog_evidence/__init__.py
staged path: tests/unit/tools/test_groundhog_evidence/test_groundhog_evidence_tdd.py
staged path: tests/unit/tools/test_groundhog_levels_perf/test_groundhog_levels_perf_tdd.py
staged path: tests/unit/tools/test_groundhog_parser.py
staged path: tests/unit/tools/test_groundhog_proof/test_groundhog_proof_tdd.py
staged path: tests/unit/tools/test_groundhog_reporting.py
staged path: tests/unit/tools/test_groundhog_reporting_nextstep.py
staged path: tests/unit/tools/test_groundhog_runner.py
staged path: tests/unit/tools/test_groundhog_snapshot.py
staged path: tests/unit/tools/test_groundhog_status.py
staged path: tests/unit/tools/test_groundhog_verdicts/test_groundhog_verdicts_tdd.py
staged path: tests/unit/tools/test_prompt_workflow_docs_layout_acceptance/test_prompt_workflow_docs_layout_acceptance_tdd.py
staged path: tests/unit/tools/test_review_resume/test_review_resume_lifecycle_tdd.py
staged path: tools/code_review_validation.py
staged path: tools/groundhog/__init__.py
staged path: tools/groundhog/cli.py
staged path: tools/groundhog/commands.py
staged path: tools/groundhog/context.py
staged path: tools/groundhog/day.py
staged path: tools/groundhog/detach.py
staged path: tools/groundhog/durations_summary.py
staged path: tools/groundhog/evidence.py
staged path: tools/groundhog/levels.py
staged path: tools/groundhog/models.py
staged path: tools/groundhog/parser.py
staged path: tools/groundhog/proof.py
staged path: tools/groundhog/reporting.py
staged path: tools/groundhog/reporting_nextstep.py
staged path: tools/groundhog/runner.py
staged path: tools/groundhog/snapshot.py
staged path: tools/groundhog/status.py
staged path: tools/groundhog/verdicts.py
staged path: tools/prepare_release/prepare_release_plan_workflow.py
```

### Requestor assessment for step 2 full_suite_levels (round 2)

Step 2 is fully implemented, with both round 1 findings fixed. The
validation plan records the exact Yes verdict for Step 2 again, after
reassessing the reviewer's round 1 rows. The missing-work section is gone,
and R1 and R2 are recorded with their repairs. Steps 3 to 8 remain pending,
so the document-level line stays `No, it is not implemented.`.

The requestor validation `ghog day --full=speed` ended on 2026-10-02 at
20:38:11 +02:00 with `exit=0` on the whole chain:

- check.bat green, with no auto-fix;
- `ghog affected --no-cov` green;
- the parallel `ghog full` green with `xfail=2` (the two Step 4 cost gates)
  and `cov=100`;
- the sequential timing pass with `outliers=0 excluded=0`, slowest call
  0.48s.

The walk closed on `full=speed src=param proof=speed reused=none
scope=whole`. A following `ghog day --full=cov`, the plan's gate, was a noop
met by that saved `speed` proof (`reused=all`). The four plan `rg` completion
patterns return nothing.

Walks of this round stopped on fixed causes before that green walk:

- the Markdown check on two terms of the round 1 answer appended to the
  versioned transcript, now code spans;
- two timing-pass outliers just above the floor, the markdown-check launcher
  contract (1.08s) and the three-cycle one-discovery review scenario (1.03s),
  both shortened as the implementation report details.

A sequential durations run of the whole suite found no call at or above 0.4s
apart from those repaired cases. No call is excluded.

Static checks passed: Ty, Pyright, Ruff, Radon, Vulture, the 650-line
big-file gate, the Markdown check, ShellCheck and the EOF check. Coverage
reached `cov=100` over `tools`. The round 2 production changes are covered by
their namesake tests: parser, runner, proof, next-step, CLI and commands. The
walk acceptance package covers the interrupted affected, full and timing
children and the failure-before-interruption cap.

Every Python file stays at or below 650 lines. `reporting_nextstep.py` is at
581, inside the 550-to-650 band, recorded as variance. The no-gate decision is
the pure `proof.judges_gate`. The parser and runner only report what the child
printed and returned, and the walk reads `RunOutcome.judged`. No new
`O(n^2)` or `O(n log n)` computation was added: the banner check is one regular
expression per output line.

### Implementation report for step 2 full_suite_levels (round 2)

Wired the full-suite levels and the saved proof through groundhog, and moved
every caller that needs a full-suite proof to its explicit level.

Round 2 repairs of the round 1 findings:

- R1, `tools/groundhog/parser.py`: records pytest's `KeyboardInterrupt`
  banner (`keyboard_interrupt`); a collection error ends with the same exit 2
  and no such banner.
- R1, `tools/groundhog/models.py`: `RunResult.interrupted`, set by
  `runner._interrupted` for a signal exit, or exit 2 with the banner, when no
  failure and no internal error was reported first.
- R1, `tools/groundhog/proof.py`: the pure `judges_gate(exit_code, *,
  interrupted)`, false for a setup error, a project without a pytest suite
  and an interrupted child.
- R1, `tools/groundhog/evidence.py`, `commands.py`, `day.py`: `RunOutcome.judged`
  carries that rule from every pytest outcome, and the walk stops on it and
  writes no marker, in place of its former exit list. The exit code and crash
  block of an interrupted child are unchanged.
- R2, `tools/groundhog/reporting_nextstep.py`: `no_baseline_line(level)`
  replaces the fixed no-baseline notice of a focus run.
- Tests:
  - the parser banner case;
  - the runner's interrupted-flag cases (signal, banner, bare exit 2, failure
    first, internal error first);
  - `judges_gate` per outcome;
  - the interrupted affected, full and timing children keeping a saved
    `speed` marker, and a failure before the interruption capping it;
  - the no-baseline line at every level, with a CLI acceptance case.
- `docs/v0.13.0/review.code.v0.13.0.full_suite_levels.md`: `__init__.py` and
  `<index>` in the round 1 answer are code spans, formatting only, for the
  Markdown check.
- `tests/unit/tools/markdown_check/test_launcher/test_launcher_tdd.py`: the
  first round 2 speed walk measured its real launcher contract at 1.08s. A
  `cmd.exe` and Python start costs about half a second of it. The unchanged
  real launch now runs once in the `launcher_run` fixture, beside the Git
  input it already built there, and the measured call only asserts on the
  recorded result.
- `tests/unit/tools/test_review_resume/test_review_resume_lifecycle_tdd.py`:
  the next speed walk measured the three-cycle one-discovery scenario at
  1.03s (0.6s to 0.8s alone). Its first discover, claim and answer cycle is
  now the `first_round_answered` fixture. Two tests each drive one more cycle
  with that same discovery: the code exchange's next round (0.30s) and a
  later specification exchange (0.26s).

Level resolution and run shapes:

- `context.Invocation` gains `level` (`None` means the command default),
  `level_source` and `in_walk`; `context.Deps` gains `environ`, the only read
  of `GHOG_FULL`.
- `cli.py`: a `leveled` parent parser gives `check`, `full`, `affected`,
  `single` and `day` a free-string `--full`; `main` resolves the level once,
  after the root and before the live-run check and the lifecycle bracket, and
  a `LevelError` prints
  `ghog: invalid full level '<value>' from <--full|GHOG_FULL>; accepted values: pass, cov, speed`
  and returns 5 (never argparse's 2) without writing `a.ghog.status`.
- `runner.pytest_command(..., level=FullLevel.SPEED)`: a `full` run at `pass`
  carries `--no-cov` and no `--durations`, at `cov` it is covered without
  `--durations`, at `speed` it is unchanged; `_measures` holds the decision.
  `verdicts.measures_coverage` is false for `full` at `pass`, and
  `durations_summary.measures_durations` probes at the effective level.

Proof and the walk:

- `tools/groundhog/evidence.py` (new): `Reused`, `RunEvidence` with
  `closing_keys` and `running_keys`, `RunOutcome`, and `for_invocation`.
- `snapshot.py`: the one-line digest writer and its comparison are removed;
  `effective_proof` returns the digest and the saved proof valid for it
  through `proof.effective_saved`, and `save_proof` writes or removes the
  scope marker with a timing fingerprint taken after the walk's writes.
- `day.walk`: noop (noop line, `reused=all`, not even check.bat runs), upgrade
  (reused headers for check and affected, `reused=check+affected`) or the
  whole chain; stop with the skip line at `none`; the full step at the level;
  at parallel `speed` a timed sequential `timings` step after a green full
  step. Failed gates cap the accumulated proof; the marker is rewritten or
  removed; exits 5 and 9 write nothing. The walk ends with a `ghog day done`
  closing line that repeats the last step's counters and appends the five
  keys.
- `commands.run_tests_outcome` returns a `RunOutcome`; a direct `ghog full`
  reports `proof.earned_by_direct_full`, and a green parallel run at `speed`
  prints the `cov` success line and the durations-not-measured line.

Reports and lifecycle:

- `reporting_nextstep.py`: every fixed restart string is a builder over
  `restart_command(level, scope_selector="")` and `carried_selector`, never
  printing a `none` selector; one success line per level; the noop line; the
  covered-affected gate-reached line naming `ghog check` then the walk; a
  standalone `ghog affected --no-cov` with no level keeps `Next: ghog full`;
  `StepContext` carries level, walk and parallel flags; the exclusion hint
  says an exclusion is accepted only after an attempted improvement.
- `reporting.py`: `ClosingMetrics.evidence` appended after `exit=`,
  `step_reused_line`, `status_killed_line(level)`, and a crash block that
  restarts at the carried level.
- `status.py`: the running line adds `full= src= scope= proof=pending`, the
  done line the closing keys before `exit=`; `_dispatch` returns a
  `RunOutcome`; a killed run relaunches at its recorded `full=`.
- `detach.py` (new, the plan's split of `status.py` past 550 lines): the
  detached launch and the survivor spawn, forwarding `--full` only for a
  `param` level.
- `levels.py` drops its `runner` import; the integer wrappers `run_day` and
  `run_tests` are removed (no caller).

Callers:

- `code_review_validation.DEFAULT_PROJECT_VALIDATION_COMMANDS` is
  `("ghog day --full=speed",)`.
- `prepare_release_plan_workflow.py` names `run ghog day --full=cov` and
  `run git range-diff and ghog day --full=cov`.
- `bin/ghog_cycle.bat` runs `day` alone when called with no argument.

Tests:

- New `test_groundhog_acceptance_levels` package: a shared `support` module,
  one test per level row of the design acceptance table, one per proof row,
  plus the exit-5 (full step and timing pass) and exit-9 no-gate cases, a
  detached `--full=cov` walk run in process and observed through
  `ghog status`, and the `ghog_cycle.bat` file-content contract.
- New `test_groundhog_evidence` package.
- AT11 and AT16 of `test_groundhog_acceptance_day.py` now cover the default
  two-step walk, the `--full=cov` chain, the proof marker and its removal.
- Runner, reporting, next-step (the Q30 rule now also forbids a `none`
  selector at every level), status, detach, snapshot, CLI, commands, verdicts
  and acceptance tests follow the builders and the keys.
- The shared `conftest.py` clears `GHOG_FULL` for every unit test, and
  `make_deps` takes an `environ` mapping.
- The three Step 2 cost gates in `test_groundhog_levels_perf` lose their
  `xfail` and keep their timeout.
- Review tests carry the new default literal; the prepare-release planner
  tests pin both operation strings.

Speed repairs made for this round's validation:

The first `ghog day --full=speed` walk on these sources was also the first
walk that ever judged speed in this parallel project. It flagged eight
pre-existing calls above the one-second floor, none of them in code this
step touches: seven in `test_prompt_workflow_docs_layout_acceptance_tdd.py`
(6.21s, 2.70s, 2.66s, 2.59s, 1.31s, 1.29s, 1.25s) and the foreground
cancellation of `test_review_resume_concurrency_tdd.py` (1.27s). Profiling
put the time in real `git` spawns of about 0.13s each. No call is excluded;
each test is now fast, with every assertion kept:

- `test_prompt_workflow_docs_layout_acceptance_tdd.py`: every scenario runs on
  one repository state, a branch freshly created from `main` with each effort
  file untracked. Each `pw` call spawned four to six `git` reads for it. A
  recording of the call phase showed six distinct read commands.
  `_FreshBranchGit` replaces `prompt_workflow_git.run_git`, the seam that
  module documents for tests. It answers those six commands from the files
  actually on disk and fails on any other command, so a new git dependency
  of `pw` cannot pass unnoticed. The fixture no longer builds a real
  repository. The `git` helpers above the seam still run, and
  `test_prompt_workflow_git.py` keeps covering `run_git` itself. The slowest
  call is now 0.10s.
- `test_review_resume_concurrency_tdd.py`: the in-process cancellation's
  preflight spawned four `git` processes, three home-tracking checks and one
  ignore check. `_IgnoredHomeGit` stands in for `subprocess.run` during that
  one call and answers both reads as real git does for the fixture's
  self-ignored home. Any other command, or a query outside the home, fails
  the test. The call is now 0.02s, and the package's process-based scenarios
  keep the real git path covered.
- `tests/acceptance/review_resume/conftest.py`: `ReviewRepository` copies a
  seed repository built once per test process and per home and family,
  under pytest's temporary root, instead of running `git init`, two
  configuration writes, an add and a commit for every scenario. Each copy
  loads its configuration once, which also cuts the fixture setup that
  precedes the measured calls.

Writer notes: `.reviews/a.full_suite_levels.step2.journal.md` and
`.reviews/a.full_suite_levels.step2.handoff.md`.

### Change summary for step 2 full_suite_levels (round 2)

Fifty-nine staged paths are covered by the mechanically valid root
`a.commit` (`commit-plan-check` reports `state: valid`, `ready: true`, no
diagnostics):

1. test(tools): answer git in process in slow tests
   - `tests/unit/tools/test_prompt_workflow_docs_layout_acceptance/test_prompt_workflow_docs_layout_acceptance_tdd.py`
   - `tests/acceptance/review_resume/conftest.py`
   - `tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_concurrency_tdd.py`
   - `tests/unit/tools/markdown_check/test_launcher/test_launcher_tdd.py`
   - `tests/unit/tools/test_review_resume/test_review_resume_lifecycle_tdd.py`
2. feat(groundhog): walk by level with saved proof
   - `tools/groundhog/__init__.py`, `levels.py`, `models.py`, `parser.py`,
     `proof.py`, `context.py`, `runner.py`,
     `verdicts.py`, `durations_summary.py`, `evidence.py` (new),
     `snapshot.py`, `reporting_nextstep.py`, `reporting.py`, `commands.py`,
     `day.py`, `status.py`, `detach.py` (new), `cli.py`
   - `bin/ghog_cycle.bat`
   - `tests/unit/tools/conftest.py`,
     `tests/unit/tools/groundhog_acceptance_support.py`
   - `tests/unit/tools/test_groundhog_acceptance_levels/` (new: `__init__.py`,
     `support.py`, `test_groundhog_acceptance_levels_tdd.py`,
     `test_groundhog_acceptance_proof_tdd.py`)
   - `tests/unit/tools/test_groundhog_evidence/` (new: `__init__.py`,
     `test_groundhog_evidence_tdd.py`)
   - `tests/unit/tools/test_groundhog_acceptance.py`,
     `test_groundhog_acceptance_day.py`,
     `test_groundhog_acceptance_durations.py`, `test_groundhog_cli.py`,
     `test_groundhog_commands.py`, `test_groundhog_detach.py`,
     `test_groundhog_reporting.py`, `test_groundhog_reporting_nextstep.py`,
     `test_groundhog_runner.py`, `test_groundhog_snapshot.py`,
     `test_groundhog_status.py`,
     `test_groundhog_levels_perf/test_groundhog_levels_perf_tdd.py`,
     `test_groundhog_verdicts/test_groundhog_verdicts_tdd.py`,
     `test_groundhog_parser.py`, `test_groundhog_proof/test_groundhog_proof_tdd.py`
3. feat(review): default validation proves speed
   - `tools/code_review_validation.py`
   - `tests/unit/tools/test_code_review_validation/test_code_review_validation_tdd.py`
   - `tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py`
   - `tests/unit/tools/test_code_review_request_commit_plan/test_code_review_request_commit_plan_tdd.py`
   - `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py`
   - `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py`
   - `tests/unit/tools/test_code_reviewer_acceptance/fixtures.py`
   - `tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_acceptance_tdd.py`
4. feat(prepare-release): prove cov before merging
   - `tools/prepare_release/prepare_release_plan_workflow.py`
   - `tests/unit/tools/prepare_release/test_prepare_release_plan_workflow.py`
5. docs(full_suite_levels): record step 2 code review
   - `docs/v0.13.0/review.code.v0.13.0.full_suite_levels.md`
6. docs(full_suite_levels): record step 2 validation
   - `docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md`

The test-speed group comes first: it depends on nothing in this step and
shortens the pre-existing calls the `speed` validation walks flagged. The
groundhog group follows: the two caller groups name `--full`, which only
exists once it lands. Its production modules and tests cannot be split by
file, because the tests pin the level-aware builders and the evidence keys
that the same modules introduce. The transcript group records the Step 2
review rounds, with two code spans the Markdown check needed, and precedes
the validation group. The completed validation record is the final
documentation group with the exact `record step 2 validation` title.

### Writer response for step 2 full_suite_levels (round 2)

Writer response:

Both round 1 findings are accepted and fixed in this round, with the
regressions the answer asked for. The reviewer's Step 2 validation metadata
patch was accepted, then reassessed after the fixes: the step now reads Yes,
the missing-work section is gone, and the round 1 findings are recorded with
their repairs.

- **R1, interrupted pytest child**: accepted. The design says an
  interrupted run judges no gate. groundhog cannot tell an interruption from
  a collection error by the exit code alone: pytest exits 2 for both. So the
  parser now records pytest's `KeyboardInterrupt` banner, and
  `RunResult.interrupted` marks a signal exit, or exit 2 with that banner,
  when no failure and no internal error was reported first. The pure
  `proof.judges_gate` names every no-gate outcome (exit 5, exit 9, an
  interrupted child), `RunOutcome.judged` carries it, and the walk's own exit
  list is gone. The exit code stays 4 with its crash block; only the proof
  effect changed. A collection error and a failure seen before the
  interruption still contradict their gate. Regressions:
  - the runner's interrupted-flag cases;
  - the parser's banner case;
  - `judges_gate` per outcome;
  - a forced walk with a saved `speed` marker whose affected, full or timing
    child is interrupted (kept);
  - one whose failure precedes the interruption (capped).
- **R2, no-baseline focus notice**: accepted. `no_baseline_line(level)`
  replaces the fixed notice, so `ghog single ... --full=cov` without a failure
  baseline names `ghog full --full=cov`. It stays plain `ghog full` with no
  level and never prints `--full=none`. Next-step tests cover `pass`, `cov`,
  `speed` and `none`, and an acceptance case drives the CLI with no baseline.

The answer also carried a bare `__init__.py` and a raw `<index>` that the
Markdown check rejects in the versioned transcript; both are now code spans,
formatting only, committed with the transcript in its own documentation
group.

### Reviewer focus for step 2 full_suite_levels (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-2-round-2 -->

## Round 2 by reviewer - Step 2

- Recorded: 2026-10-02T20:51:28+02:00
- Exchange: code/code/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/plan.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 2
- Outcome: answer

### Assessed index identity for step 2 full_suite_levels (exchange 1) (round 2)

Baseline index tree: 49daf397a5af85d20ff109ffbda43ddf33b37ec8

Assessed index tree: 15576d69109a140d2b6c5e65971cf48623b8d5aa

### Implementation check for step 2 full_suite_levels (exchange 1) (round 2)

Result:

No. Step 2 has NOT been fully implemented.

The current request, exact Step 2 plan, staged implementation and unit tests were assessed independently. The round 2 delta was compared with the previously assessed round 1 tree. R2 is resolved: no_baseline_line carries pass, cov and speed and omits a none selector. R1 now handles signals and the bare KeyboardInterrupt banner, preserving genuine collection and internal-error failures, but still misses valid interruption banners containing an exception message or explicit pytest cancellation.

The level wiring, saved-proof orchestration, caller defaults, status and detached reporting remain consistent with the reviewed step. The new judged flag keeps the no-gate decision in the pure proof module. No new architecture or complexity defect was identified. The two additional test fixture changes retain their exercised operations and assertions.

The reported coverage gate measures tools, with the configured omissions including tests and `__init__.py`. All changed executable production modules are within that source scope. Parser, runner, proof, next-step and walk tests cover the added branches, but lack the real interruption forms described in R1. Coverage was assessed statically, not measured by the reviewer.

Validation plan effects:

Updated and staged only the Step 2 rows of `docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md`: the exact No verdict, the remaining R1 work list, the resolved R2 status, and the coverage and feature-integrity conclusions. Other steps and the document-level status were left intact. No umbrella applies. The metadata patch is attributable to the reviewer.

### Pre-repair mandatory checks and coverage for step 2 full_suite_levels (exchange 1) (round 2)

The requestor reports a complete `ghog day --full=speed` walk ending 2026-10-02 20:38:11 +02:00 with exit 0, check and affected green, the parallel full run at cov=100 with two Step 4 xfails, and the sequential timing pass at outliers=0, excluded=0 and slowest call 0.48s. The subsequent plan `ghog day --full=cov` was a noop satisfied by saved speed proof; all four completion searches returned no matches.

The reviewer ran no test or coverage command this round. Static code and unit-test inspection, including the installed pytest interruption-reporting implementation, was sufficient to establish the remaining defect. The reported green walk is not independent reviewer execution evidence.

### Resolved validation set and sources for step 2 full_suite_levels (exchange 1) (round 2)

- `ghog day --full=speed` (sources: project).
- `ghog day --full=cov` (sources: plan).
- `rg -n 'is_unchanged|write_marker\(' tools/groundhog` (sources: plan).
- `rg -n 'full=none|--full=default' tools/groundhog` (sources: plan).
- `rg -n '\x22ghog day\x22' tools/code_review_validation.py` (sources: plan).
- `rg -n 'call :run_one timings' bin/ghog_cycle.bat` (sources: plan).

### Resolver drift and direction for step 2 full_suite_levels (exchange 1) (round 2)

No drift found. `.review-validation` is absent, and the current resolver default is `ghog day --full=speed`. The exact plan supplies the cov walk and four completion searches shown in the request, with no request additions. The ordered commands and source labels agree with the current resolver contract. The reviewer did not run this requestor-owned set.

### Repository state around validation for step 2 full_suite_levels (exchange 1) (round 2)

Request-time and independently captured baseline index: `49daf397a5af85d20ff109ffbda43ddf33b37ec8`. Final assessed index after the metadata patch: `15576d69109a140d2b6c5e65971cf48623b8d5aa`.

Before and after captures used the same ordered set of 59 staged paths, including the exact validation plan. The comparison reports acceptable=false solely for the intentional validation-plan change and `<index>` change; there are no new untracked or ignored path differences. Inspection classifies both differences as the permitted Step 2 metadata patch. No runtime validation was executed, so there are no test-command side effects. The umbrella comparison reports applicable=false and changed=false.

`attribute-reviewer-patch` returned attributable=true; only that exact patch was applied to the index. Pre-existing writer state was preserved. Retained evidence is in the canonical manifest and the round 2 ignored caller files.

### Repair inventory for step 2 full_suite_levels (exchange 1) (round 2)

Repairs made:

- `docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md`: polishing-only review metadata; records the remaining R1 defect and resolved R2. No implementation or test repair was made.

Paths staged:

- `docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md`: only the attributable reviewer metadata patch was staged.

### Commit plan assessment for step 2 full_suite_levels (exchange 1) (round 2)

Independent `commit-plan-check.bat --format json` ran before assessment and after the metadata patch. Both returned exit 0, state=valid, ready=true, 59 staged paths and no diagnostics. The ordered groups are:

1. `test(tools): answer git in process in slow tests` (5 paths).
2. `feat(groundhog): walk by level with saved proof` (42 paths).
3. `feat(review): default validation proves speed` (8 paths).
4. `feat(prepare-release): prove cov before merging` (2 paths).
5. `docs(full_suite_levels): record step 2 code review` (1 paths).
6. `docs(full_suite_levels): record step 2 validation` (1 paths).

All staged paths remain assigned exactly once. The test changes precede the groundhog implementation; the two caller groups follow the new CLI capability; review and validation records are separate final documentation groups. Membership, dependency order, scope and conventional subjects remain accurate. `a.commit` was not changed. This mechanical result does not establish implementation readiness or authorize a commit.

### Findings and boundaries for step 2 full_suite_levels (exchange 1) (round 2)

Unresolved findings:

- R1 (P2, carried; partially fixed): accept pytest interruption banners with messages. `tools/groundhog/parser.py:94` matches only `!+ KeyboardInterrupt !+`. A test or plugin that raises `KeyboardInterrupt("stopped")` produces a banner containing `KeyboardInterrupt: stopped`; explicit `pytest.exit("stopped")` also takes pytest's interruption path with exit 2 and an Exit message. The installed `_pytest.main.wrap_session` routes both through `pytest_keyboard_interrupt`, and `_pytest.terminal.TerminalReporter._report_keyboardinterrupt` renders `excrepr.reprcrash.message`, not a fixed title. Neither form matches the new regex, so `runner._interrupted` at lines 305-306 returns false despite no failed test or internal error. A forced walk with saved speed proof still removes its marker when the affected child cancels, or caps it to none when the full/timing child cancels. Recognize these actual interruption forms while keeping collection errors and prior failures distinct, and add parser/runner plus forced-walk regressions that assert the saved marker bytes remain unchanged. The new canned transcripts exercise only the bare banner and therefore miss this remaining design-contract violation.

Boundary-crossing work: None.

### Writer instructions for step 2 full_suite_levels (exchange 1) (round 2)

Finish the remaining R1 interruption classification and regression coverage described above. Keep the already-correct R2 level-aware no-baseline behavior. Preserve collection-error and prior-failure contradiction behavior; do not classify every exit 2 as an interruption.

Reassess the Step 2 validation rows after the repair, run the requestor-owned resolved validation set, update the staged commit plan if membership changes, and publish the replacement request with its fresh index tree. No literal `Human guidance:` block was present; the reviewer made no substantive repair.

### Decision rationale for step 2 full_suite_levels (exchange 1) (round 2)

Recommend changes-requested. The six readiness-floor results are:

1. Identity: PASS. Code identity, exact plan, Step 2, round 2, occurrence 1 and baseline index agree with the live request.
2. Implementation completeness: FAIL. R1 still permits valid interruptions to discard saved proof; R2 is resolved.
3. Validation and coverage: INCOMPLETE. Requestor evidence is reported green within the configured coverage scope, but static review identifies missing behavioral regressions. No reviewer runtime or coverage rerun was needed to establish the defect.
4. Staged attribution: PASS. Only the attributable Step 2 validation metadata patch was staged by the reviewer.
5. Unresolved findings: FAIL. The remaining R1 case is open.
6. `a.commit`: PASS. The independent final check reports valid, ready=true, six ordered groups, 59 paths and no diagnostics.

The recommendation is advisory and does not authorize a commit.

### Final reviewer decision for step 2 full_suite_levels (exchange 1) (round 2)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-2-round-2 -->

## Round 3 by requestor - Step 2

- Recorded: 2026-10-02T21:52:59+02:00
- Exchange: code/code/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/plan.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 2
- Outcome: request

### Review identity for step 2 full_suite_levels (round 3)

Umbrella draft: none
Implementation plan: docs/v0.13.0/plan.v0.13.0.full_suite_levels.md
Implementation step: 2
Review round: 3

### Code review evidence for step 2 full_suite_levels (round 3)

request_index_tree: 4bb8679452bdadda628dd33355823a6d58b63fd3
resolved_validation_set:

- ghog day --full=speed (sources: project)
- ghog day --full=cov (sources: plan)
- rg -n 'is_unchanged|write_marker\(' tools/groundhog (sources: plan)
- rg -n 'full=none|--full=default' tools/groundhog (sources: plan)
- rg -n '\x22ghog day\x22' tools/code_review_validation.py (sources: plan)
- rg -n 'call :run_one timings' bin/ghog_cycle.bat (sources: plan)

commit_plan_result:

```text
state: valid
ready: true
group 1: test(tools): answer git in process in slow tests
group 1 path: tests/unit/tools/test_prompt_workflow_docs_layout_acceptance/test_prompt_workflow_docs_layout_acceptance_tdd.py
group 1 path: tests/acceptance/review_resume/conftest.py
group 1 path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_concurrency_tdd.py
group 1 path: tests/unit/tools/markdown_check/test_launcher/test_launcher_tdd.py
group 1 path: tests/unit/tools/test_review_resume/test_review_resume_lifecycle_tdd.py
group 2: feat(groundhog): walk by level with saved proof
group 2 path: tools/groundhog/__init__.py
group 2 path: tools/groundhog/levels.py
group 2 path: tools/groundhog/models.py
group 2 path: tools/groundhog/parser.py
group 2 path: tools/groundhog/proof.py
group 2 path: tools/groundhog/context.py
group 2 path: tools/groundhog/runner.py
group 2 path: tools/groundhog/verdicts.py
group 2 path: tools/groundhog/durations_summary.py
group 2 path: tools/groundhog/evidence.py
group 2 path: tools/groundhog/snapshot.py
group 2 path: tools/groundhog/reporting_nextstep.py
group 2 path: tools/groundhog/reporting.py
group 2 path: tools/groundhog/commands.py
group 2 path: tools/groundhog/day.py
group 2 path: tools/groundhog/status.py
group 2 path: tools/groundhog/detach.py
group 2 path: tools/groundhog/cli.py
group 2 path: bin/ghog_cycle.bat
group 2 path: tests/unit/tools/conftest.py
group 2 path: tests/unit/tools/groundhog_acceptance_support.py
group 2 path: tests/unit/tools/test_groundhog_acceptance.py
group 2 path: tests/unit/tools/test_groundhog_acceptance_day.py
group 2 path: tests/unit/tools/test_groundhog_acceptance_durations.py
group 2 path: tests/unit/tools/test_groundhog_acceptance_levels/__init__.py
group 2 path: tests/unit/tools/test_groundhog_acceptance_levels/support.py
group 2 path: tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_levels_tdd.py
group 2 path: tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_proof_tdd.py
group 2 path: tests/unit/tools/test_groundhog_cli.py
group 2 path: tests/unit/tools/test_groundhog_commands.py
group 2 path: tests/unit/tools/test_groundhog_detach.py
group 2 path: tests/unit/tools/test_groundhog_evidence/__init__.py
group 2 path: tests/unit/tools/test_groundhog_evidence/test_groundhog_evidence_tdd.py
group 2 path: tests/unit/tools/test_groundhog_levels_perf/test_groundhog_levels_perf_tdd.py
group 2 path: tests/unit/tools/test_groundhog_reporting.py
group 2 path: tests/unit/tools/test_groundhog_reporting_nextstep.py
group 2 path: tests/unit/tools/test_groundhog_runner.py
group 2 path: tests/unit/tools/test_groundhog_snapshot.py
group 2 path: tests/unit/tools/test_groundhog_status.py
group 2 path: tests/unit/tools/test_groundhog_verdicts/test_groundhog_verdicts_tdd.py
group 2 path: tests/unit/tools/test_groundhog_parser.py
group 2 path: tests/unit/tools/test_groundhog_proof/test_groundhog_proof_tdd.py
group 3: feat(review): default validation proves speed
group 3 path: tools/code_review_validation.py
group 3 path: tests/unit/tools/test_code_review_validation/test_code_review_validation_tdd.py
group 3 path: tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py
group 3 path: tests/unit/tools/test_code_review_request_commit_plan/test_code_review_request_commit_plan_tdd.py
group 3 path: tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py
group 3 path: tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py
group 3 path: tests/unit/tools/test_code_reviewer_acceptance/fixtures.py
group 3 path: tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_acceptance_tdd.py
group 4: feat(prepare-release): prove cov before merging
group 4 path: tools/prepare_release/prepare_release_plan_workflow.py
group 4 path: tests/unit/tools/prepare_release/test_prepare_release_plan_workflow.py
group 5: docs(full_suite_levels): record step 2 code review
group 5 path: docs/v0.13.0/review.code.v0.13.0.full_suite_levels.md
group 6: docs(full_suite_levels): record step 2 validation
group 6 path: docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md
staged path: bin/ghog_cycle.bat
staged path: docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md
staged path: docs/v0.13.0/review.code.v0.13.0.full_suite_levels.md
staged path: tests/acceptance/review_resume/conftest.py
staged path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_concurrency_tdd.py
staged path: tests/unit/tools/conftest.py
staged path: tests/unit/tools/groundhog_acceptance_support.py
staged path: tests/unit/tools/markdown_check/test_launcher/test_launcher_tdd.py
staged path: tests/unit/tools/prepare_release/test_prepare_release_plan_workflow.py
staged path: tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py
staged path: tests/unit/tools/test_code_review_request_commit_plan/test_code_review_request_commit_plan_tdd.py
staged path: tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py
staged path: tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py
staged path: tests/unit/tools/test_code_review_validation/test_code_review_validation_tdd.py
staged path: tests/unit/tools/test_code_reviewer_acceptance/fixtures.py
staged path: tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_acceptance_tdd.py
staged path: tests/unit/tools/test_groundhog_acceptance.py
staged path: tests/unit/tools/test_groundhog_acceptance_day.py
staged path: tests/unit/tools/test_groundhog_acceptance_durations.py
staged path: tests/unit/tools/test_groundhog_acceptance_levels/__init__.py
staged path: tests/unit/tools/test_groundhog_acceptance_levels/support.py
staged path: tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_levels_tdd.py
staged path: tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_proof_tdd.py
staged path: tests/unit/tools/test_groundhog_cli.py
staged path: tests/unit/tools/test_groundhog_commands.py
staged path: tests/unit/tools/test_groundhog_detach.py
staged path: tests/unit/tools/test_groundhog_evidence/__init__.py
staged path: tests/unit/tools/test_groundhog_evidence/test_groundhog_evidence_tdd.py
staged path: tests/unit/tools/test_groundhog_levels_perf/test_groundhog_levels_perf_tdd.py
staged path: tests/unit/tools/test_groundhog_parser.py
staged path: tests/unit/tools/test_groundhog_proof/test_groundhog_proof_tdd.py
staged path: tests/unit/tools/test_groundhog_reporting.py
staged path: tests/unit/tools/test_groundhog_reporting_nextstep.py
staged path: tests/unit/tools/test_groundhog_runner.py
staged path: tests/unit/tools/test_groundhog_snapshot.py
staged path: tests/unit/tools/test_groundhog_status.py
staged path: tests/unit/tools/test_groundhog_verdicts/test_groundhog_verdicts_tdd.py
staged path: tests/unit/tools/test_prompt_workflow_docs_layout_acceptance/test_prompt_workflow_docs_layout_acceptance_tdd.py
staged path: tests/unit/tools/test_review_resume/test_review_resume_lifecycle_tdd.py
staged path: tools/code_review_validation.py
staged path: tools/groundhog/__init__.py
staged path: tools/groundhog/cli.py
staged path: tools/groundhog/commands.py
staged path: tools/groundhog/context.py
staged path: tools/groundhog/day.py
staged path: tools/groundhog/detach.py
staged path: tools/groundhog/durations_summary.py
staged path: tools/groundhog/evidence.py
staged path: tools/groundhog/levels.py
staged path: tools/groundhog/models.py
staged path: tools/groundhog/parser.py
staged path: tools/groundhog/proof.py
staged path: tools/groundhog/reporting.py
staged path: tools/groundhog/reporting_nextstep.py
staged path: tools/groundhog/runner.py
staged path: tools/groundhog/snapshot.py
staged path: tools/groundhog/status.py
staged path: tools/groundhog/verdicts.py
staged path: tools/prepare_release/prepare_release_plan_workflow.py
```

### Requestor assessment for step 2 full_suite_levels (round 3)

Step 2 is fully implemented: R1 is now complete and R2 stays fixed. The
validation plan again records the exact Yes verdict for Step 2, after
reassessing the reviewer's round 2 rows. The missing-work section is gone, and
the review repairs record every banner form. The plan also records the
requestor's own round 3 finding: the walk now takes its digest after
check.bat. Steps 3 to 8 remain pending, so the document-level line stays
`No, it is not implemented.`.

The requestor validation `ghog day --full=speed` ended on 2026-10-02 at
21:49:42 +02:00 with `exit=0` on the whole chain:

- check.bat green, with no auto-fix;
- `ghog affected --no-cov` green;
- the parallel `ghog full` green with `xfail=2` (the two Step 4 cost gates)
  and `cov=100`;
- the sequential timing pass with `outliers=0 excluded=0`, slowest call
  0.37s.

The walk closed on `full=speed src=param proof=speed reused=none
scope=whole`. A following `ghog day --full=cov`, the plan's gate, was a noop
met by that saved `speed` proof (`reused=all`). The four plan `rg` completion
patterns return nothing.

One earlier round 3 walk, on the R1 repair alone, was also green at `speed`.
In it, check.bat's Ruff fixed one file, `test_groundhog_parser.py`, and the
`ghog day --full=cov` that followed ran the whole chain at `cov` instead of a
noop. That exposed the start-of-walk digest described in the writer response.
The fix and its regressions are in this request, and the green walk above
ran on them.

Static checks passed: Ty, Pyright, Ruff, Radon, Vulture, the 650-line
big-file gate, the Markdown check, ShellCheck and the EOF check. Coverage
reached `cov=100` over `tools`. The round 3 production changes are covered by
their namesake tests: parser, runner and snapshot. The walk acceptance
package covers each interruption banner on the affected, full and timing
children with the marker bytes unchanged, and both check.bat fix cases. No
call is excluded.

Every Python file stays at or below 650 lines. `reporting_nextstep.py` is at
581, inside the 550-to-650 band, recorded as variance. `day.py` is at 401
and `snapshot.py` at 485. The banner rule is one regular expression per output
line. The digest fix adds one digest walk after a green check.bat, on the
whole chain only, which matches HEAD's walk: it digested at its start and
again at its end. A noop or an upgrade keeps its single digest walk. No new
`O(n^2)` or `O(n log n)` computation was added.

### Implementation report for step 2 full_suite_levels (round 3)

Wired the full-suite levels and the saved proof through groundhog, and moved
every caller that needs a full-suite proof to its explicit level.

Round 3 completion of R1 (round 2 matched only the bare banner):

- `tools/groundhog/parser.py`: `_INTERRUPTION_BANNER_RE` matches the crash
  message pytest prints between `!` runs for a `KeyboardInterrupt`, bare or
  with a message, and for an explicit `pytest.exit`
  (`_pytest.outcomes.Exit: <message>`). The forms were captured from the
  installed pytest on throwaway suites. The collection-error banner
  (`Interrupted: 1 error during collection`) still does not match. The flag
  is renamed `interruption_banner`.
- `tools/groundhog/runner.py`: `_interrupted` accepts the banner with any
  failing exit code (`code != PYTEST_OK`), since `pytest.exit` sets its own
  return code. A failure or internal error reported first, a collection
  error and an exit 2 without the banner still judge the gate.
- Tests:
  - `test_groundhog_parser.py`: the three real banners recorded, and the
    collection banner not;
  - `test_groundhog_runner.py`: nine interrupted-flag cases (each banner, a
    `pytest.exit` at exit 3, a signal; not a bare exit 2, the collection
    banner, a failure first or an internal error first);
  - `test_groundhog_acceptance_proof_tdd.py`: the interrupted-children walk
    is parametrized over the three banners (`support.INTERRUPTED_CHILDREN`).
    For each, the affected, full and timing children leave the saved marker
    byte for byte unchanged.

Round 3 requestor finding, digest after check.bat:

- `tools/groundhog/snapshot.py`: `EffectiveProof.on_sources(digest)` returns
  the same state on an unchanged digest, else no saved proof on the new one.
- `tools/groundhog/day.py`: `_Walk.state` holds the digest and the saved
  proof; the whole chain moves it to a fresh `source_digest` right after a
  green check.bat, and `_record_proof(record)` writes that digest. A noop and
  an upgrade run no check.bat and keep their one digest walk.
- Tests: `test_groundhog_snapshot.py` (`on_sources`); the proof acceptance
  file's `_FixingCheck` factory rewrites a source when check.bat spawns:
  `test_check_fix_proves_the_fixed_sources` (the same walk again spawns
  nothing) and `test_check_fix_drops_the_proof_of_the_old_sources` (a forced
  walk over saved `speed` records `cov` on the fixed digest).

Round 2 repairs of the round 1 findings:

- R1, `tools/groundhog/parser.py`: records pytest's interruption banner; a
  collection error ends with the same exit 2 and another banner.
- R1, `tools/groundhog/models.py`: `RunResult.interrupted`, set by
  `runner._interrupted` for a signal exit, or a failing exit with the banner,
  when no failure and no internal error was reported first.
- R1, `tools/groundhog/proof.py`: the pure `judges_gate(exit_code, *,
  interrupted)`, false for a setup error, a project without a pytest suite
  and an interrupted child.
- R1, `tools/groundhog/evidence.py`, `commands.py`, `day.py`: `RunOutcome.judged`
  carries that rule from every pytest outcome, and the walk stops on it and
  writes no marker, in place of its former exit list. The exit code and crash
  block of an interrupted child are unchanged.
- R2, `tools/groundhog/reporting_nextstep.py`: `no_baseline_line(level)`
  replaces the fixed no-baseline notice of a focus run.
- Tests:
  - the parser banner cases;
  - the runner's interrupted-flag cases;
  - `judges_gate` per outcome;
  - the interrupted affected, full and timing children keeping a saved
    `speed` marker, and a failure before the interruption capping it;
  - the no-baseline line at every level, with a CLI acceptance case.
- `docs/v0.13.0/review.code.v0.13.0.full_suite_levels.md`: `__init__.py` and
  `<index>` in the round 1 answer are code spans, formatting only, for the
  Markdown check.
- `tests/unit/tools/markdown_check/test_launcher/test_launcher_tdd.py`: the
  first round 2 speed walk measured its real launcher contract at 1.08s. A
  `cmd.exe` and Python start costs about half a second of it. The unchanged
  real launch now runs once in the `launcher_run` fixture, beside the Git
  input it already built there, and the measured call only asserts on the
  recorded result.
- `tests/unit/tools/test_review_resume/test_review_resume_lifecycle_tdd.py`:
  the next speed walk measured the three-cycle one-discovery scenario at
  1.03s (0.6s to 0.8s alone). Its first discover, claim and answer cycle is
  now the `first_round_answered` fixture. Two tests each drive one more cycle
  with that same discovery: the code exchange's next round (0.30s) and a
  later specification exchange (0.26s).

Level resolution and run shapes:

- `context.Invocation` gains `level` (`None` means the command default),
  `level_source` and `in_walk`; `context.Deps` gains `environ`, the only read
  of `GHOG_FULL`.
- `cli.py`: a `leveled` parent parser gives `check`, `full`, `affected`,
  `single` and `day` a free-string `--full`; `main` resolves the level once,
  after the root and before the live-run check and the lifecycle bracket, and
  a `LevelError` prints
  `ghog: invalid full level '<value>' from <--full|GHOG_FULL>; accepted values: pass, cov, speed`
  and returns 5 (never argparse's 2) without writing `a.ghog.status`.
- `runner.pytest_command(..., level=FullLevel.SPEED)`: a `full` run at `pass`
  carries `--no-cov` and no `--durations`, at `cov` it is covered without
  `--durations`, at `speed` it is unchanged; `_measures` holds the decision.
  `verdicts.measures_coverage` is false for `full` at `pass`, and
  `durations_summary.measures_durations` probes at the effective level.

Proof and the walk:

- `tools/groundhog/evidence.py` (new): `Reused`, `RunEvidence` with
  `closing_keys` and `running_keys`, `RunOutcome`, and `for_invocation`.
- `snapshot.py`: the one-line digest writer and its comparison are removed;
  `effective_proof` returns the digest and the saved proof valid for it
  through `proof.effective_saved`, and `save_proof` writes or removes the
  scope marker with a timing fingerprint taken after the walk's writes.
- `day.walk`: noop (noop line, `reused=all`, not even check.bat runs), upgrade
  (reused headers for check and affected, `reused=check+affected`) or the
  whole chain; stop with the skip line at `none`; the full step at the level;
  at parallel `speed` a timed sequential `timings` step after a green full
  step. Failed gates cap the accumulated proof; the marker is rewritten or
  removed; exits 5 and 9 write nothing. The walk ends with a `ghog day done`
  closing line that repeats the last step's counters and appends the five
  keys.
- `commands.run_tests_outcome` returns a `RunOutcome`; a direct `ghog full`
  reports `proof.earned_by_direct_full`, and a green parallel run at `speed`
  prints the `cov` success line and the durations-not-measured line.

Reports and lifecycle:

- `reporting_nextstep.py`: every fixed restart string is a builder over
  `restart_command(level, scope_selector="")` and `carried_selector`, never
  printing a `none` selector; one success line per level; the noop line; the
  covered-affected gate-reached line naming `ghog check` then the walk; a
  standalone `ghog affected --no-cov` with no level keeps `Next: ghog full`;
  `StepContext` carries level, walk and parallel flags; the exclusion hint
  says an exclusion is accepted only after an attempted improvement.
- `reporting.py`: `ClosingMetrics.evidence` appended after `exit=`,
  `step_reused_line`, `status_killed_line(level)`, and a crash block that
  restarts at the carried level.
- `status.py`: the running line adds `full= src= scope= proof=pending`, the
  done line the closing keys before `exit=`; `_dispatch` returns a
  `RunOutcome`; a killed run relaunches at its recorded `full=`.
- `detach.py` (new, the plan's split of `status.py` past 550 lines): the
  detached launch and the survivor spawn, forwarding `--full` only for a
  `param` level.
- `levels.py` drops its `runner` import; the integer wrappers `run_day` and
  `run_tests` are removed (no caller).

Callers:

- `code_review_validation.DEFAULT_PROJECT_VALIDATION_COMMANDS` is
  `("ghog day --full=speed",)`.
- `prepare_release_plan_workflow.py` names `run ghog day --full=cov` and
  `run git range-diff and ghog day --full=cov`.
- `bin/ghog_cycle.bat` runs `day` alone when called with no argument.

Tests:

- New `test_groundhog_acceptance_levels` package: a shared `support` module,
  one test per level row of the design acceptance table, one per proof row,
  plus the exit-5 (full step and timing pass) and exit-9 no-gate cases, a
  detached `--full=cov` walk run in process and observed through
  `ghog status`, and the `ghog_cycle.bat` file-content contract.
- New `test_groundhog_evidence` package.
- AT11 and AT16 of `test_groundhog_acceptance_day.py` now cover the default
  two-step walk, the `--full=cov` chain, the proof marker and its removal.
- Runner, reporting, next-step (the Q30 rule now also forbids a `none`
  selector at every level), status, detach, snapshot, CLI, commands, verdicts
  and acceptance tests follow the builders and the keys.
- The shared `conftest.py` clears `GHOG_FULL` for every unit test, and
  `make_deps` takes an `environ` mapping.
- The three Step 2 cost gates in `test_groundhog_levels_perf` lose their
  `xfail` and keep their timeout.
- Review tests carry the new default literal; the prepare-release planner
  tests pin both operation strings.

Speed repairs made for this round's validation:

The first `ghog day --full=speed` walk on these sources was also the first
walk that ever judged speed in this parallel project. It flagged eight
pre-existing calls above the one-second floor, none of them in code this
step touches: seven in `test_prompt_workflow_docs_layout_acceptance_tdd.py`
(6.21s, 2.70s, 2.66s, 2.59s, 1.31s, 1.29s, 1.25s) and the foreground
cancellation of `test_review_resume_concurrency_tdd.py` (1.27s). Profiling
put the time in real `git` spawns of about 0.13s each. No call is excluded;
each test is now fast, with every assertion kept:

- `test_prompt_workflow_docs_layout_acceptance_tdd.py`: every scenario runs on
  one repository state, a branch freshly created from `main` with each effort
  file untracked. Each `pw` call spawned four to six `git` reads for it. A
  recording of the call phase showed six distinct read commands.
  `_FreshBranchGit` replaces `prompt_workflow_git.run_git`, the seam that
  module documents for tests. It answers those six commands from the files
  actually on disk and fails on any other command, so a new git dependency
  of `pw` cannot pass unnoticed. The fixture no longer builds a real
  repository. The `git` helpers above the seam still run, and
  `test_prompt_workflow_git.py` keeps covering `run_git` itself. The slowest
  call is now 0.10s.
- `test_review_resume_concurrency_tdd.py`: the in-process cancellation's
  preflight spawned four `git` processes, three home-tracking checks and one
  ignore check. `_IgnoredHomeGit` stands in for `subprocess.run` during that
  one call and answers both reads as real git does for the fixture's
  self-ignored home. Any other command, or a query outside the home, fails
  the test. The call is now 0.02s, and the package's process-based scenarios
  keep the real git path covered.
- `tests/acceptance/review_resume/conftest.py`: `ReviewRepository` copies a
  seed repository built once per test process and per home and family,
  under pytest's temporary root, instead of running `git init`, two
  configuration writes, an add and a commit for every scenario. Each copy
  loads its configuration once, which also cuts the fixture setup that
  precedes the measured calls.

Writer notes: `.reviews/a.full_suite_levels.step2.journal.md` and
`.reviews/a.full_suite_levels.step2.handoff.md`.

### Change summary for step 2 full_suite_levels (round 3)

Fifty-nine staged paths are covered by the mechanically valid root
`a.commit` (`commit-plan-check` reports `state: valid`, `ready: true`, no
diagnostics):

1. test(tools): answer git in process in slow tests
   - `tests/unit/tools/test_prompt_workflow_docs_layout_acceptance/test_prompt_workflow_docs_layout_acceptance_tdd.py`
   - `tests/acceptance/review_resume/conftest.py`
   - `tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_concurrency_tdd.py`
   - `tests/unit/tools/markdown_check/test_launcher/test_launcher_tdd.py`
   - `tests/unit/tools/test_review_resume/test_review_resume_lifecycle_tdd.py`
2. feat(groundhog): walk by level with saved proof
   - `tools/groundhog/__init__.py`, `levels.py`, `models.py`, `parser.py`,
     `proof.py`, `context.py`, `runner.py`,
     `verdicts.py`, `durations_summary.py`, `evidence.py` (new),
     `snapshot.py`, `reporting_nextstep.py`, `reporting.py`, `commands.py`,
     `day.py`, `status.py`, `detach.py` (new), `cli.py`
   - `bin/ghog_cycle.bat`
   - `tests/unit/tools/conftest.py`,
     `tests/unit/tools/groundhog_acceptance_support.py`
   - `tests/unit/tools/test_groundhog_acceptance_levels/` (new: `__init__.py`,
     `support.py`, `test_groundhog_acceptance_levels_tdd.py`,
     `test_groundhog_acceptance_proof_tdd.py`)
   - `tests/unit/tools/test_groundhog_evidence/` (new: `__init__.py`,
     `test_groundhog_evidence_tdd.py`)
   - `tests/unit/tools/test_groundhog_acceptance.py`,
     `test_groundhog_acceptance_day.py`,
     `test_groundhog_acceptance_durations.py`, `test_groundhog_cli.py`,
     `test_groundhog_commands.py`, `test_groundhog_detach.py`,
     `test_groundhog_reporting.py`, `test_groundhog_reporting_nextstep.py`,
     `test_groundhog_runner.py`, `test_groundhog_snapshot.py`,
     `test_groundhog_status.py`,
     `test_groundhog_levels_perf/test_groundhog_levels_perf_tdd.py`,
     `test_groundhog_verdicts/test_groundhog_verdicts_tdd.py`,
     `test_groundhog_parser.py`, `test_groundhog_proof/test_groundhog_proof_tdd.py`
3. feat(review): default validation proves speed
   - `tools/code_review_validation.py`
   - `tests/unit/tools/test_code_review_validation/test_code_review_validation_tdd.py`
   - `tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py`
   - `tests/unit/tools/test_code_review_request_commit_plan/test_code_review_request_commit_plan_tdd.py`
   - `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py`
   - `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py`
   - `tests/unit/tools/test_code_reviewer_acceptance/fixtures.py`
   - `tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_acceptance_tdd.py`
4. feat(prepare-release): prove cov before merging
   - `tools/prepare_release/prepare_release_plan_workflow.py`
   - `tests/unit/tools/prepare_release/test_prepare_release_plan_workflow.py`
5. docs(full_suite_levels): record step 2 code review
   - `docs/v0.13.0/review.code.v0.13.0.full_suite_levels.md`
6. docs(full_suite_levels): record step 2 validation
   - `docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md`

The test-speed group comes first: it depends on nothing in this step and
shortens the pre-existing calls the `speed` validation walks flagged. The
groundhog group follows: the two caller groups name `--full`, which only
exists once it lands. Its production modules and tests cannot be split by
file, because the tests pin the level-aware builders and the evidence keys
that the same modules introduce. The transcript group records the Step 2
review rounds, with two code spans the Markdown check needed, and precedes
the validation group. The completed validation record is the final
documentation group with the exact `record step 2 validation` title.

Round 3 changes no membership: the R1 completion and the digest fix
stay in the groundhog group, and the validation record stays last.

### Writer response for step 2 full_suite_levels (round 3)

Writer response:

R1 is accepted and now complete; R2 was confirmed fixed in round 2 and is
unchanged. The reviewer's Step 2 validation metadata patch was accepted, then
reassessed after the fix: the step reads Yes again, the missing-work section
is gone, and the review repairs record the banner forms.

- **R1, interruption banners with a message or from `pytest.exit`**:
  accepted. The round 2 rule matched only the bare banner. The installed
  pytest was run on throwaway suites to capture the banners it really prints:
  - `KeyboardInterrupt`, bare: `!!! KeyboardInterrupt !!!`, exit 2;
  - `KeyboardInterrupt("stopped")`: `!!! KeyboardInterrupt: stopped !!!`,
    exit 2;
  - `pytest.exit("stopped")`: `!!! _pytest.outcomes.Exit: stopped !!!`,
    exit 2, or the given code (3 with `returncode=3`);
  - a collection error: `!!! Interrupted: 1 error during collection !!!`,
    exit 2.

  The parser's `_INTERRUPTION_BANNER_RE` now accepts the crash message of a
  `KeyboardInterrupt` or a `_pytest.outcomes.Exit`, with or without a
  message, and still rejects the collection-error banner. Its flag is
  renamed `interruption_banner`. `runner._interrupted` accepts that banner
  with any failing exit code, not only 2, because `pytest.exit` sets its own.
  A prior failed test or internal error still makes the child judge its gate,
  and an exit 2 without the banner is still a collection error. Regressions:
  - the parser records the three real banners and not the collection one;
  - the runner flags each banner, a `pytest.exit` with exit 3 and a signal,
    and does not flag a bare exit 2, the collection banner, a failure first
    or an internal error first;
  - the forced-walk acceptance test is parametrized over the three banners
    for the interrupted affected, full and timing children, and asserts the
    saved marker bytes are unchanged, not only its proof level.

The requestor found and fixed one more gap while validating this round, not
raised by the reviewer:

- **Digest taken before check.bat**: the first round 3 speed walk was green,
  but check.bat's Ruff fixed one file, and the plan's `ghog day --full=cov`
  ran the whole chain again instead of a noop. HEAD's `write_marker`
  computed the digest at the end of the walk, after any check.bat fix. The
  Step 2 walk froze the digest of its start, so its marker matched no source
  state. Worse, a forced walk over a saved proof could carry that older
  proof onto the fixed sources. A green check.bat now moves the walk's
  state to a fresh digest, through the new `EffectiveProof.on_sources`,
  which keeps the saved proof only when the digest did not move. The marker
  records the sources the test steps judged. A file edited during the test
  steps still invalidates the proof, as with the start digest; HEAD's end
  digest would have proven it. Regressions:
  - `on_sources` on an unchanged and a moved digest;
  - a walk whose check.bat fixes a source, then the same walk as a noop;
  - a forced walk over a saved `speed` proof whose check.bat fixes a source,
    recording `cov` on the fixed digest.

### Reviewer focus for step 2 full_suite_levels (round 3)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-2-round-3 -->

## Round 3 by reviewer - Step 2

- Recorded: 2026-10-02T22:09:01+02:00
- Exchange: code/code/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/plan.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 2
- Outcome: answer

### Assessed index identity for step 2 full_suite_levels (exchange 1) (round 3)

Baseline index tree: 4bb8679452bdadda628dd33355823a6d58b63fd3

Assessed index tree: 94d3e277e78c945899b9a1a10617af052f972add

### Implementation check for step 2 full_suite_levels (exchange 1) (round 3)

Result:

No. Step 2 has NOT been fully implemented.

The level-shaped runs, noop/upgrade decisions, status and restart evidence, detached forwarding, caller defaults and post-check digest refresh are implemented. R2 is resolved. R1 remains incomplete for pytest.exit custom return codes: an interrupted run can report success and claim proof. Static architecture and performance assessment found no additional issue; the missing behavioral tests are listed in R1.

Validation plan effects:

Updated only the Step 2 analysis, missing-work list, unit-test assessment and feature-integrity rows in docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md. Added concrete R1 code and regression-test work immediately after What was implemented. No other step, document-level status or umbrella was edited.

### Pre-repair mandatory checks and coverage for step 2 full_suite_levels (exchange 1) (round 3)

Requestor evidence: ghog day --full=speed finished 2026-10-02 21:49:42 +02:00 with exit=0, cov=100, outliers=0, excluded=0 and two expected Step 4 xfails; the following cov walk reused the saved speed proof. The request also reports all four plan searches clear. These are requestor results, not reviewer executions. No reviewer ghog check, affected, day, full or coverage command was run: source and test inspection establish R1 without another execution. pyproject.toml measures tools (with configured omissions, including `__init__.py`); the new behavioral gap is not disproved by 100% line coverage.

### Resolved validation set and sources for step 2 full_suite_levels (exchange 1) (round 3)

- `ghog day --full=speed` (sources: project)
- `ghog day --full=cov` (sources: plan)
- `rg -n 'is_unchanged|write_marker\(' tools/groundhog` (sources: plan)
- `rg -n 'full=none|--full=default' tools/groundhog` (sources: plan)
- `rg -n '\x22ghog day\x22' tools/code_review_validation.py` (sources: plan)
- `rg -n 'call :run_one timings' bin/ghog_cycle.bat` (sources: plan)

### Resolver drift and direction for step 2 full_suite_levels (exchange 1) (round 3)

No drift found. The current .review-validation file is absent, so load_project_validation_commands supplies ghog day --full=speed from the staged default. The Step 2 plan supplies the cov walk and four searches; no request-only additions are declared. Applying the current resolver's ordered-union rule yields the six commands and source labels embedded in the request. This comparison did not execute those commands.

### Repository state around validation for step 2 full_suite_levels (exchange 1) (round 3)

The received tree matched request tree 4bb8679452bdadda628dd33355823a6d58b63fd3. A second validation-state capture immediately before the metadata edit was identical to the initial capture. After the metadata edit, the launcher comparison names only the Step 2 validation document and `<index>`; these are the attributable, permitted metadata patch and its staging, not validation side effects. Assessed tree: 94d3e277e78c945899b9a1a10617af052f972add. The umbrella comparison is not applicable and unchanged (no umbrella). No other tracked or untracked validation-path difference and no ignored validation-artifact difference occurred. The protocol-owned transcript has a pre-existing unstaged difference; it was not read, staged or edited by hand.

### Repair inventory for step 2 full_suite_levels (exchange 1) (round 3)

Repairs made:

- Review metadata only: recorded Step 2 as incomplete and added R1 missing work and assessment corrections in the validation plan. No implementation or test repair.

Paths staged:

- docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md: staged only the patch returned as attributable by code_review_evidence against blob 03ced8bef2e5125b9889a41177e304783cbddf11.

### Commit plan assessment for step 2 full_suite_levels (exchange 1) (round 3)

Independent commit-plan-check.bat --format json returned state=valid, ready=true, exit=0, diagnostics=[]. Its 59 staged paths are assigned exactly once to six ordered groups:

1. `test(tools): answer git in process in slow tests` (5 paths)
2. `feat(groundhog): walk by level with saved proof` (42 paths)
3. `feat(review): default validation proves speed` (8 paths)
4. `feat(prepare-release): prove cov before merging` (2 paths)
5. `docs(full_suite_levels): record step 2 code review` (1 paths)
6. `docs(full_suite_levels): record step 2 validation` (1 paths)

Grouping separates validation-speed test changes, groundhog implementation/tests, review default, release caller and the two review documents. Subjects and dependency order are consistent with the staged changes. The metadata patch adds no path or group and a.commit is unchanged; the mechanical result does not establish implementation readiness.

### Findings and boundaries for step 2 full_suite_levels (exchange 1) (round 3)

Unresolved findings:

- R1 [P2]: Make the interruption verdict independent of pytest.exit's custom return code. In tools/groundhog/runner.py:275-287, an interruption banner with code 1 sets interrupted=True but crashed=False; verdicts.classify (tools/groundhog/verdicts.py:74-85) ignores interrupted and returns 0 when no failure was parsed and coverage is disabled. Thus a direct ghog full --full=pass reports success and proof=pass, and a day walk can stop at an interrupted child with exit=0. Code 0 is also excluded by runner.py:307, so an interrupted pass-level full child is judged successful and the walk can persist pass proof, causing a later noop despite tests never finishing. The installed pytest main.py:336-345 explicitly honors custom exit codes including 0 and 1 while calling its interruption hook. Existing runner regressions cover custom code 3 only, which already satisfies the crash-code check. Treat the banner as an incomplete run for verdicts and proof regardless of its return code; retain prior-failure/internal-error caps. Add direct-full and day regressions for codes 0 and 1, including no saved marker, unchanged saved marker, and interrupted affected/full/timing children. This is a static finding; no reproduction command was executed.

Boundary-crossing work: None.

### Writer instructions for step 2 full_suite_levels (exchange 1) (round 3)

Complete the two R1 missing-work bullets in the Step 2 validation plan: unify interruption classification with the crash/non-success verdict and suppress newly earned proof, then add custom-code 0/1 regression coverage without losing the existing failure-first caps. Run the resolved requestor validation set on the repaired sources, update Step 2 evidence and publish a fresh round with its current index tree. No literal Human guidance block was present, so the reviewer made no implementation repair.

### Decision rationale for step 2 full_suite_levels (exchange 1) (round 3)

changes-requested. Readiness floor: exact identity PASS (code v0.13.0 full_suite_levels, step 2, round 3, occurrence 1); completeness FAIL (R1); validation/coverage FAIL for the missing behavioral regression, with the requestor's green results acknowledged; staged attribution PASS (metadata-only patch); unresolved findings FAIL (R1); a.commit PASS (independent mechanical check). No substantive reviewer repair and no boundary-crossing work. This is advisory and grants no commit authority.

### Final reviewer decision for step 2 full_suite_levels (exchange 1) (round 3)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-2-round-3 -->

## Round 4 by requestor - Step 2

- Recorded: 2026-10-02T22:39:20+02:00
- Exchange: code/code/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/plan.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 2
- Outcome: request

### Review identity for step 2 full_suite_levels (round 4)

Umbrella draft: none
Implementation plan: docs/v0.13.0/plan.v0.13.0.full_suite_levels.md
Implementation step: 2
Review round: 4

### Code review evidence for step 2 full_suite_levels (round 4)

request_index_tree: d0a192412b48c40aad0df611bc7061ef5b1839db
resolved_validation_set:

- ghog day --full=speed (sources: project)
- ghog day --full=cov (sources: plan)
- rg -n 'is_unchanged|write_marker\(' tools/groundhog (sources: plan)
- rg -n 'full=none|--full=default' tools/groundhog (sources: plan)
- rg -n '\x22ghog day\x22' tools/code_review_validation.py (sources: plan)
- rg -n 'call :run_one timings' bin/ghog_cycle.bat (sources: plan)

commit_plan_result:

```text
state: valid
ready: true
group 1: test(tools): answer git in process in slow tests
group 1 path: tests/unit/tools/test_prompt_workflow_docs_layout_acceptance/test_prompt_workflow_docs_layout_acceptance_tdd.py
group 1 path: tests/acceptance/review_resume/conftest.py
group 1 path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_concurrency_tdd.py
group 1 path: tests/unit/tools/markdown_check/test_launcher/test_launcher_tdd.py
group 1 path: tests/unit/tools/test_review_resume/test_review_resume_lifecycle_tdd.py
group 2: feat(groundhog): walk by level with saved proof
group 2 path: tools/groundhog/__init__.py
group 2 path: tools/groundhog/levels.py
group 2 path: tools/groundhog/models.py
group 2 path: tools/groundhog/parser.py
group 2 path: tools/groundhog/proof.py
group 2 path: tools/groundhog/context.py
group 2 path: tools/groundhog/runner.py
group 2 path: tools/groundhog/verdicts.py
group 2 path: tools/groundhog/durations_summary.py
group 2 path: tools/groundhog/evidence.py
group 2 path: tools/groundhog/snapshot.py
group 2 path: tools/groundhog/reporting_nextstep.py
group 2 path: tools/groundhog/reporting.py
group 2 path: tools/groundhog/commands.py
group 2 path: tools/groundhog/day.py
group 2 path: tools/groundhog/status.py
group 2 path: tools/groundhog/detach.py
group 2 path: tools/groundhog/cli.py
group 2 path: bin/ghog_cycle.bat
group 2 path: tests/unit/tools/conftest.py
group 2 path: tests/unit/tools/groundhog_acceptance_support.py
group 2 path: tests/unit/tools/test_groundhog_acceptance.py
group 2 path: tests/unit/tools/test_groundhog_acceptance_day.py
group 2 path: tests/unit/tools/test_groundhog_acceptance_durations.py
group 2 path: tests/unit/tools/test_groundhog_acceptance_levels/__init__.py
group 2 path: tests/unit/tools/test_groundhog_acceptance_levels/support.py
group 2 path: tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_levels_tdd.py
group 2 path: tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_proof_tdd.py
group 2 path: tests/unit/tools/test_groundhog_cli.py
group 2 path: tests/unit/tools/test_groundhog_commands.py
group 2 path: tests/unit/tools/test_groundhog_detach.py
group 2 path: tests/unit/tools/test_groundhog_evidence/__init__.py
group 2 path: tests/unit/tools/test_groundhog_evidence/test_groundhog_evidence_tdd.py
group 2 path: tests/unit/tools/test_groundhog_levels_perf/test_groundhog_levels_perf_tdd.py
group 2 path: tests/unit/tools/test_groundhog_reporting.py
group 2 path: tests/unit/tools/test_groundhog_reporting_nextstep.py
group 2 path: tests/unit/tools/test_groundhog_runner.py
group 2 path: tests/unit/tools/test_groundhog_snapshot.py
group 2 path: tests/unit/tools/test_groundhog_status.py
group 2 path: tests/unit/tools/test_groundhog_verdicts/test_groundhog_verdicts_tdd.py
group 2 path: tests/unit/tools/test_groundhog_parser.py
group 2 path: tests/unit/tools/test_groundhog_proof/test_groundhog_proof_tdd.py
group 3: feat(review): default validation proves speed
group 3 path: tools/code_review_validation.py
group 3 path: tests/unit/tools/test_code_review_validation/test_code_review_validation_tdd.py
group 3 path: tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py
group 3 path: tests/unit/tools/test_code_review_request_commit_plan/test_code_review_request_commit_plan_tdd.py
group 3 path: tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py
group 3 path: tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py
group 3 path: tests/unit/tools/test_code_reviewer_acceptance/fixtures.py
group 3 path: tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_acceptance_tdd.py
group 4: feat(prepare-release): prove cov before merging
group 4 path: tools/prepare_release/prepare_release_plan_workflow.py
group 4 path: tests/unit/tools/prepare_release/test_prepare_release_plan_workflow.py
group 5: docs(full_suite_levels): record step 2 code review
group 5 path: docs/v0.13.0/review.code.v0.13.0.full_suite_levels.md
group 6: docs(full_suite_levels): record step 2 validation
group 6 path: docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md
staged path: bin/ghog_cycle.bat
staged path: docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md
staged path: docs/v0.13.0/review.code.v0.13.0.full_suite_levels.md
staged path: tests/acceptance/review_resume/conftest.py
staged path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_concurrency_tdd.py
staged path: tests/unit/tools/conftest.py
staged path: tests/unit/tools/groundhog_acceptance_support.py
staged path: tests/unit/tools/markdown_check/test_launcher/test_launcher_tdd.py
staged path: tests/unit/tools/prepare_release/test_prepare_release_plan_workflow.py
staged path: tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py
staged path: tests/unit/tools/test_code_review_request_commit_plan/test_code_review_request_commit_plan_tdd.py
staged path: tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py
staged path: tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py
staged path: tests/unit/tools/test_code_review_validation/test_code_review_validation_tdd.py
staged path: tests/unit/tools/test_code_reviewer_acceptance/fixtures.py
staged path: tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_acceptance_tdd.py
staged path: tests/unit/tools/test_groundhog_acceptance.py
staged path: tests/unit/tools/test_groundhog_acceptance_day.py
staged path: tests/unit/tools/test_groundhog_acceptance_durations.py
staged path: tests/unit/tools/test_groundhog_acceptance_levels/__init__.py
staged path: tests/unit/tools/test_groundhog_acceptance_levels/support.py
staged path: tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_levels_tdd.py
staged path: tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_proof_tdd.py
staged path: tests/unit/tools/test_groundhog_cli.py
staged path: tests/unit/tools/test_groundhog_commands.py
staged path: tests/unit/tools/test_groundhog_detach.py
staged path: tests/unit/tools/test_groundhog_evidence/__init__.py
staged path: tests/unit/tools/test_groundhog_evidence/test_groundhog_evidence_tdd.py
staged path: tests/unit/tools/test_groundhog_levels_perf/test_groundhog_levels_perf_tdd.py
staged path: tests/unit/tools/test_groundhog_parser.py
staged path: tests/unit/tools/test_groundhog_proof/test_groundhog_proof_tdd.py
staged path: tests/unit/tools/test_groundhog_reporting.py
staged path: tests/unit/tools/test_groundhog_reporting_nextstep.py
staged path: tests/unit/tools/test_groundhog_runner.py
staged path: tests/unit/tools/test_groundhog_snapshot.py
staged path: tests/unit/tools/test_groundhog_status.py
staged path: tests/unit/tools/test_groundhog_verdicts/test_groundhog_verdicts_tdd.py
staged path: tests/unit/tools/test_prompt_workflow_docs_layout_acceptance/test_prompt_workflow_docs_layout_acceptance_tdd.py
staged path: tests/unit/tools/test_review_resume/test_review_resume_lifecycle_tdd.py
staged path: tools/code_review_validation.py
staged path: tools/groundhog/__init__.py
staged path: tools/groundhog/cli.py
staged path: tools/groundhog/commands.py
staged path: tools/groundhog/context.py
staged path: tools/groundhog/day.py
staged path: tools/groundhog/detach.py
staged path: tools/groundhog/durations_summary.py
staged path: tools/groundhog/evidence.py
staged path: tools/groundhog/levels.py
staged path: tools/groundhog/models.py
staged path: tools/groundhog/parser.py
staged path: tools/groundhog/proof.py
staged path: tools/groundhog/reporting.py
staged path: tools/groundhog/reporting_nextstep.py
staged path: tools/groundhog/runner.py
staged path: tools/groundhog/snapshot.py
staged path: tools/groundhog/status.py
staged path: tools/groundhog/verdicts.py
staged path: tools/prepare_release/prepare_release_plan_workflow.py
```

### Requestor assessment for step 2 full_suite_levels (round 4)

Step 2 is fully implemented: R1 is now complete for custom return codes. R2
and the check.bat digest fix stay as the round 3 assessment confirmed them.
The validation plan again records the exact Yes verdict for Step 2, after
reassessing the reviewer's round 3 rows. The missing-work section is gone, and
the review repairs and the test rows name `pytest.exit` returning 0 and 1.
Steps 3 to 8 remain pending, so the document-level line stays
`No, it is not implemented.`.

The requestor validation `ghog day --full=speed` ended on 2026-10-02 at
22:36:26 +02:00 with `exit=0` on the whole chain:

- check.bat green, with no auto-fix;
- `ghog affected --no-cov` green;
- the parallel `ghog full` green with `xfail=2` (the two Step 4 cost gates)
  and `cov=100`;
- the sequential timing pass with `outliers=0 excluded=0`, slowest call
  0.41s.

The walk closed on `full=speed src=param proof=speed reused=none
scope=whole`. A following `ghog day --full=cov`, the plan's gate, was a noop
met by that saved `speed` proof (`reused=all`). The four plan `rg` completion
patterns return nothing.

One earlier round 4 walk stopped at check.bat's Markdown check. The round 3
answer appended to the versioned transcript carried a bare `__init__.py` and
a raw `<index>`. Both are now code spans, formatting only.

Static checks passed: Ty, Pyright, Ruff, Radon, Vulture, the 650-line
big-file gate, the Markdown check, ShellCheck and the EOF check. Coverage
reached `cov=100` over `tools`. The round 4 production change is covered by
the runner tests. The walk acceptance package covers five interrupted
children: the bare and messaged `KeyboardInterrupt`, and `pytest.exit`
returning 2, 1 and 0. Each crashes its step, earns no proof and keeps the
saved marker byte for byte. Without a saved marker, each leaves none, and a
direct `ghog full --full=pass` claims none. No call is excluded.

Every Python file stays at or below 650 lines. `runner.py` is at 315.
`reporting_nextstep.py` is at 581, inside the 550-to-650 band, recorded as
variance. The change adds one boolean read per finished child and no new
`O(n^2)` or `O(n log n)` computation.

### Implementation report for step 2 full_suite_levels (round 4)

Wired the full-suite levels and the saved proof through groundhog, and moved
every caller that needs a full-suite proof to its explicit level.

Round 4 completion of R1 for custom return codes:

- `tools/groundhog/runner.py`: `run_pytest` marks the run crashed on the
  interruption banner whatever its return code (a `pytest.exit` may return
  0 or 1 on an unfinished suite); `_interrupted` takes a signal or the
  banner without the former `code != PYTEST_OK` condition. The crash gives
  exit 4 and no earned proof; the interrupted flag keeps the saved marker.
  A failure or internal error reported first still judges the gate.
- `tools/groundhog/models.py`: the `RunResult` fix note names `pytest.exit`
  with any return code.
- Tests:
  - `test_groundhog_runner.py`: the `pytest.exit` banner at codes 1 and 0
    (crashed, interrupted), and a failure before it at code 1 (crashed, not
    interrupted);
  - `support.py`: `INTERRUPTED_CHILDREN` now holds five children, the
    `pytest.exit` banner also at codes 1 and 0, with `INTERRUPTION_IDS`;
  - `test_groundhog_acceptance_proof_tdd.py`: the marker-preservation walk
    runs all five; new `test_interrupted_suite_earns_no_proof` checks, for
    each, a `--full=pass` walk without a marker (exit 4, no marker,
    `proof=unproven`) and a direct `ghog full --full=pass` (exit 4,
    `proof=unproven`).

Round 3 completion of R1 (round 2 matched only the bare banner):

- `tools/groundhog/parser.py`: `_INTERRUPTION_BANNER_RE` matches the crash
  message pytest prints between `!` runs for a `KeyboardInterrupt`, bare or
  with a message, and for an explicit `pytest.exit`
  (`_pytest.outcomes.Exit: <message>`). The forms were captured from the
  installed pytest on throwaway suites. The collection-error banner
  (`Interrupted: 1 error during collection`) still does not match. The flag
  is renamed `interruption_banner`.
- `tools/groundhog/runner.py`: `_interrupted` accepts the banner with any
  failing exit code (`code != PYTEST_OK`), since `pytest.exit` sets its own
  return code. A failure or internal error reported first, a collection
  error and an exit 2 without the banner still judge the gate.
- Tests:
  - `test_groundhog_parser.py`: the three real banners recorded, and the
    collection banner not;
  - `test_groundhog_runner.py`: nine interrupted-flag cases (each banner, a
    `pytest.exit` at exit 3, a signal; not a bare exit 2, the collection
    banner, a failure first or an internal error first);
  - `test_groundhog_acceptance_proof_tdd.py`: the interrupted-children walk
    is parametrized over the three banners (`support.INTERRUPTED_CHILDREN`).
    For each, the affected, full and timing children leave the saved marker
    byte for byte unchanged.

Round 3 requestor finding, digest after check.bat:

- `tools/groundhog/snapshot.py`: `EffectiveProof.on_sources(digest)` returns
  the same state on an unchanged digest, else no saved proof on the new one.
- `tools/groundhog/day.py`: `_Walk.state` holds the digest and the saved
  proof; the whole chain moves it to a fresh `source_digest` right after a
  green check.bat, and `_record_proof(record)` writes that digest. A noop and
  an upgrade run no check.bat and keep their one digest walk.
- Tests: `test_groundhog_snapshot.py` (`on_sources`); the proof acceptance
  file's `_FixingCheck` factory rewrites a source when check.bat spawns:
  `test_check_fix_proves_the_fixed_sources` (the same walk again spawns
  nothing) and `test_check_fix_drops_the_proof_of_the_old_sources` (a forced
  walk over saved `speed` records `cov` on the fixed digest).

Round 2 repairs of the round 1 findings:

- R1, `tools/groundhog/parser.py`: records pytest's interruption banner; a
  collection error ends with the same exit 2 and another banner.
- R1, `tools/groundhog/models.py`: `RunResult.interrupted`, set by
  `runner._interrupted` for a signal exit, or a failing exit with the banner,
  when no failure and no internal error was reported first.
- R1, `tools/groundhog/proof.py`: the pure `judges_gate(exit_code, *,
  interrupted)`, false for a setup error, a project without a pytest suite
  and an interrupted child.
- R1, `tools/groundhog/evidence.py`, `commands.py`, `day.py`: `RunOutcome.judged`
  carries that rule from every pytest outcome, and the walk stops on it and
  writes no marker, in place of its former exit list. The exit code and crash
  block of an interrupted child are unchanged.
- R2, `tools/groundhog/reporting_nextstep.py`: `no_baseline_line(level)`
  replaces the fixed no-baseline notice of a focus run.
- Tests:
  - the parser banner cases;
  - the runner's interrupted-flag cases;
  - `judges_gate` per outcome;
  - the interrupted affected, full and timing children keeping a saved
    `speed` marker, and a failure before the interruption capping it;
  - the no-baseline line at every level, with a CLI acceptance case.
- `docs/v0.13.0/review.code.v0.13.0.full_suite_levels.md`: `__init__.py` and
  `<index>` in the round 1 answer are code spans, formatting only, for the
  Markdown check.
- `tests/unit/tools/markdown_check/test_launcher/test_launcher_tdd.py`: the
  first round 2 speed walk measured its real launcher contract at 1.08s. A
  `cmd.exe` and Python start costs about half a second of it. The unchanged
  real launch now runs once in the `launcher_run` fixture, beside the Git
  input it already built there, and the measured call only asserts on the
  recorded result.
- `tests/unit/tools/test_review_resume/test_review_resume_lifecycle_tdd.py`:
  the next speed walk measured the three-cycle one-discovery scenario at
  1.03s (0.6s to 0.8s alone). Its first discover, claim and answer cycle is
  now the `first_round_answered` fixture. Two tests each drive one more cycle
  with that same discovery: the code exchange's next round (0.30s) and a
  later specification exchange (0.26s).

Level resolution and run shapes:

- `context.Invocation` gains `level` (`None` means the command default),
  `level_source` and `in_walk`; `context.Deps` gains `environ`, the only read
  of `GHOG_FULL`.
- `cli.py`: a `leveled` parent parser gives `check`, `full`, `affected`,
  `single` and `day` a free-string `--full`; `main` resolves the level once,
  after the root and before the live-run check and the lifecycle bracket, and
  a `LevelError` prints
  `ghog: invalid full level '<value>' from <--full|GHOG_FULL>; accepted values: pass, cov, speed`
  and returns 5 (never argparse's 2) without writing `a.ghog.status`.
- `runner.pytest_command(..., level=FullLevel.SPEED)`: a `full` run at `pass`
  carries `--no-cov` and no `--durations`, at `cov` it is covered without
  `--durations`, at `speed` it is unchanged; `_measures` holds the decision.
  `verdicts.measures_coverage` is false for `full` at `pass`, and
  `durations_summary.measures_durations` probes at the effective level.

Proof and the walk:

- `tools/groundhog/evidence.py` (new): `Reused`, `RunEvidence` with
  `closing_keys` and `running_keys`, `RunOutcome`, and `for_invocation`.
- `snapshot.py`: the one-line digest writer and its comparison are removed;
  `effective_proof` returns the digest and the saved proof valid for it
  through `proof.effective_saved`, and `save_proof` writes or removes the
  scope marker with a timing fingerprint taken after the walk's writes.
- `day.walk`: noop (noop line, `reused=all`, not even check.bat runs), upgrade
  (reused headers for check and affected, `reused=check+affected`) or the
  whole chain; stop with the skip line at `none`; the full step at the level;
  at parallel `speed` a timed sequential `timings` step after a green full
  step. Failed gates cap the accumulated proof; the marker is rewritten or
  removed; exits 5 and 9 write nothing. The walk ends with a `ghog day done`
  closing line that repeats the last step's counters and appends the five
  keys.
- `commands.run_tests_outcome` returns a `RunOutcome`; a direct `ghog full`
  reports `proof.earned_by_direct_full`, and a green parallel run at `speed`
  prints the `cov` success line and the durations-not-measured line.

Reports and lifecycle:

- `reporting_nextstep.py`: every fixed restart string is a builder over
  `restart_command(level, scope_selector="")` and `carried_selector`, never
  printing a `none` selector; one success line per level; the noop line; the
  covered-affected gate-reached line naming `ghog check` then the walk; a
  standalone `ghog affected --no-cov` with no level keeps `Next: ghog full`;
  `StepContext` carries level, walk and parallel flags; the exclusion hint
  says an exclusion is accepted only after an attempted improvement.
- `reporting.py`: `ClosingMetrics.evidence` appended after `exit=`,
  `step_reused_line`, `status_killed_line(level)`, and a crash block that
  restarts at the carried level.
- `status.py`: the running line adds `full= src= scope= proof=pending`, the
  done line the closing keys before `exit=`; `_dispatch` returns a
  `RunOutcome`; a killed run relaunches at its recorded `full=`.
- `detach.py` (new, the plan's split of `status.py` past 550 lines): the
  detached launch and the survivor spawn, forwarding `--full` only for a
  `param` level.
- `levels.py` drops its `runner` import; the integer wrappers `run_day` and
  `run_tests` are removed (no caller).

Callers:

- `code_review_validation.DEFAULT_PROJECT_VALIDATION_COMMANDS` is
  `("ghog day --full=speed",)`.
- `prepare_release_plan_workflow.py` names `run ghog day --full=cov` and
  `run git range-diff and ghog day --full=cov`.
- `bin/ghog_cycle.bat` runs `day` alone when called with no argument.

Tests:

- New `test_groundhog_acceptance_levels` package: a shared `support` module,
  one test per level row of the design acceptance table, one per proof row,
  plus the exit-5 (full step and timing pass) and exit-9 no-gate cases, a
  detached `--full=cov` walk run in process and observed through
  `ghog status`, and the `ghog_cycle.bat` file-content contract.
- New `test_groundhog_evidence` package.
- AT11 and AT16 of `test_groundhog_acceptance_day.py` now cover the default
  two-step walk, the `--full=cov` chain, the proof marker and its removal.
- Runner, reporting, next-step (the Q30 rule now also forbids a `none`
  selector at every level), status, detach, snapshot, CLI, commands, verdicts
  and acceptance tests follow the builders and the keys.
- The shared `conftest.py` clears `GHOG_FULL` for every unit test, and
  `make_deps` takes an `environ` mapping.
- The three Step 2 cost gates in `test_groundhog_levels_perf` lose their
  `xfail` and keep their timeout.
- Review tests carry the new default literal; the prepare-release planner
  tests pin both operation strings.

Speed repairs made for this round's validation:

The first `ghog day --full=speed` walk on these sources was also the first
walk that ever judged speed in this parallel project. It flagged eight
pre-existing calls above the one-second floor, none of them in code this
step touches: seven in `test_prompt_workflow_docs_layout_acceptance_tdd.py`
(6.21s, 2.70s, 2.66s, 2.59s, 1.31s, 1.29s, 1.25s) and the foreground
cancellation of `test_review_resume_concurrency_tdd.py` (1.27s). Profiling
put the time in real `git` spawns of about 0.13s each. No call is excluded;
each test is now fast, with every assertion kept:

- `test_prompt_workflow_docs_layout_acceptance_tdd.py`: every scenario runs on
  one repository state, a branch freshly created from `main` with each effort
  file untracked. Each `pw` call spawned four to six `git` reads for it. A
  recording of the call phase showed six distinct read commands.
  `_FreshBranchGit` replaces `prompt_workflow_git.run_git`, the seam that
  module documents for tests. It answers those six commands from the files
  actually on disk and fails on any other command, so a new git dependency
  of `pw` cannot pass unnoticed. The fixture no longer builds a real
  repository. The `git` helpers above the seam still run, and
  `test_prompt_workflow_git.py` keeps covering `run_git` itself. The slowest
  call is now 0.10s.
- `test_review_resume_concurrency_tdd.py`: the in-process cancellation's
  preflight spawned four `git` processes, three home-tracking checks and one
  ignore check. `_IgnoredHomeGit` stands in for `subprocess.run` during that
  one call and answers both reads as real git does for the fixture's
  self-ignored home. Any other command, or a query outside the home, fails
  the test. The call is now 0.02s, and the package's process-based scenarios
  keep the real git path covered.
- `tests/acceptance/review_resume/conftest.py`: `ReviewRepository` copies a
  seed repository built once per test process and per home and family,
  under pytest's temporary root, instead of running `git init`, two
  configuration writes, an add and a commit for every scenario. Each copy
  loads its configuration once, which also cuts the fixture setup that
  precedes the measured calls.

Writer notes: `.reviews/a.full_suite_levels.step2.journal.md` and
`.reviews/a.full_suite_levels.step2.handoff.md`.

### Change summary for step 2 full_suite_levels (round 4)

Fifty-nine staged paths are covered by the mechanically valid root
`a.commit` (`commit-plan-check` reports `state: valid`, `ready: true`, no
diagnostics):

1. test(tools): answer git in process in slow tests
   - `tests/unit/tools/test_prompt_workflow_docs_layout_acceptance/test_prompt_workflow_docs_layout_acceptance_tdd.py`
   - `tests/acceptance/review_resume/conftest.py`
   - `tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_concurrency_tdd.py`
   - `tests/unit/tools/markdown_check/test_launcher/test_launcher_tdd.py`
   - `tests/unit/tools/test_review_resume/test_review_resume_lifecycle_tdd.py`
2. feat(groundhog): walk by level with saved proof
   - `tools/groundhog/__init__.py`, `levels.py`, `models.py`, `parser.py`,
     `proof.py`, `context.py`, `runner.py`,
     `verdicts.py`, `durations_summary.py`, `evidence.py` (new),
     `snapshot.py`, `reporting_nextstep.py`, `reporting.py`, `commands.py`,
     `day.py`, `status.py`, `detach.py` (new), `cli.py`
   - `bin/ghog_cycle.bat`
   - `tests/unit/tools/conftest.py`,
     `tests/unit/tools/groundhog_acceptance_support.py`
   - `tests/unit/tools/test_groundhog_acceptance_levels/` (new: `__init__.py`,
     `support.py`, `test_groundhog_acceptance_levels_tdd.py`,
     `test_groundhog_acceptance_proof_tdd.py`)
   - `tests/unit/tools/test_groundhog_evidence/` (new: `__init__.py`,
     `test_groundhog_evidence_tdd.py`)
   - `tests/unit/tools/test_groundhog_acceptance.py`,
     `test_groundhog_acceptance_day.py`,
     `test_groundhog_acceptance_durations.py`, `test_groundhog_cli.py`,
     `test_groundhog_commands.py`, `test_groundhog_detach.py`,
     `test_groundhog_reporting.py`, `test_groundhog_reporting_nextstep.py`,
     `test_groundhog_runner.py`, `test_groundhog_snapshot.py`,
     `test_groundhog_status.py`,
     `test_groundhog_levels_perf/test_groundhog_levels_perf_tdd.py`,
     `test_groundhog_verdicts/test_groundhog_verdicts_tdd.py`,
     `test_groundhog_parser.py`, `test_groundhog_proof/test_groundhog_proof_tdd.py`
3. feat(review): default validation proves speed
   - `tools/code_review_validation.py`
   - `tests/unit/tools/test_code_review_validation/test_code_review_validation_tdd.py`
   - `tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py`
   - `tests/unit/tools/test_code_review_request_commit_plan/test_code_review_request_commit_plan_tdd.py`
   - `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py`
   - `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py`
   - `tests/unit/tools/test_code_reviewer_acceptance/fixtures.py`
   - `tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_acceptance_tdd.py`
4. feat(prepare-release): prove cov before merging
   - `tools/prepare_release/prepare_release_plan_workflow.py`
   - `tests/unit/tools/prepare_release/test_prepare_release_plan_workflow.py`
5. docs(full_suite_levels): record step 2 code review
   - `docs/v0.13.0/review.code.v0.13.0.full_suite_levels.md`
6. docs(full_suite_levels): record step 2 validation
   - `docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md`

The test-speed group comes first: it depends on nothing in this step and
shortens the pre-existing calls the `speed` validation walks flagged. The
groundhog group follows: the two caller groups name `--full`, which only
exists once it lands. Its production modules and tests cannot be split by
file, because the tests pin the level-aware builders and the evidence keys
that the same modules introduce. The transcript group records the Step 2
review rounds, with two code spans the Markdown check needed, and precedes
the validation group. The completed validation record is the final
documentation group with the exact `record step 2 validation` title.

Rounds 3 and 4 change no membership: the R1 completion and the digest fix
stay in the groundhog group, and the validation record stays last.

### Writer response for step 2 full_suite_levels (round 4)

Writer response:

R1 is accepted and completed for custom return codes. R2 and the
check.bat digest fix, both confirmed by the round 3 assessment, are
unchanged. The reviewer's Step 2 validation metadata patch was accepted, then
reassessed after the repair: the step reads Yes again, the missing-work
section is gone, and the review repairs and test rows name codes 0 and 1.

- **R1, `pytest.exit` with return code 0 or 1**: accepted. Round 3 tied the
  crash verdict to the exit code (2, 3 or a signal) and the interruption
  flag to a non-zero code. So a banner with code 1 was interrupted but not
  crashed, and `verdicts.classify` read it as green. A banner with code 0
  was neither, and could earn and save proof for a suite that never
  finished. In `runner.run_pytest`, the interruption banner now marks the
  run crashed whatever its return code, and `_interrupted` no longer
  requires a non-zero code. Such a child exits 4 with its crash block. A
  crash earns no proof (`proof.earned_by_direct_full` and the walk's
  `_judge`), and the walk writes nothing after it. A failure or an internal
  error reported before the banner still makes the child judge its gate,
  so the existing caps hold. A collection error, which prints another
  banner, is unchanged. Regressions:
  - runner: the `pytest.exit` banner with codes 1 and 0 is crashed and
    interrupted; a failure before it, with code 1, is crashed and not
    interrupted;
  - the forced-walk acceptance test runs five children (bare, messaged,
    `pytest.exit` returning 2, 1 and 0). For each, the interrupted affected,
    full and timing children exit 4 and keep the saved marker byte for byte;
  - `test_interrupted_suite_earns_no_proof`, for the same five children: a
    `--full=pass` walk without a saved marker exits 4, writes no marker and
    closes `proof=unproven`; a direct `ghog full --full=pass` exits 4 and
    closes `proof=unproven`.

The round 3 answer appended a bare `__init__.py` and a raw `<index>` to the
versioned transcript, which the Markdown check rejects, as in round 1. Both
are now code spans, formatting only, committed with the transcript in its
own documentation group.

### Reviewer focus for step 2 full_suite_levels (round 4)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-2-round-4 -->

## Round 4 by reviewer - Step 2

- Recorded: 2026-10-02T22:48:34+02:00
- Exchange: code/code/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/plan.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 2
- Outcome: answer

### Assessed index identity for step 2 full_suite_levels (exchange 1) (round 4)

Baseline index tree: d0a192412b48c40aad0df611bc7061ef5b1839db

Assessed index tree: f4198f7576d28ffdf716e37f3a7b0741d39155d1

### Implementation check for step 2 full_suite_levels (exchange 1) (round 4)

Result:

Yes. Step 2 has been fully implemented.

Round 4 closes R1. In `runner.run_pytest`, an interruption banner now sets `crashed` independently of the child's return code. `verdicts.classify` therefore returns suite-crash exit 4 for `pytest.exit` codes 0 and 1 as well as 2 and 3. The direct-full proof path earns nothing from that verdict. The interrupted flag still excludes a failure or internal error reported first, so those outcomes continue to cap saved proof.

The runner tests assert both flags for the custom codes. The acceptance tests cover all five banner/code combinations through affected, full and timing children, asserting exit 4 and byte-for-byte saved-marker preservation. They also cover a day walk without a marker and a direct full run, both with unproven proof after interruption. The failure-before-interruption cap remains covered.

R2's carried-level restart notice and the post-check source-digest repair remain complete. The reviewed level selection, saved-proof reuse, evidence/status reporting, detached forwarding and caller defaults are unchanged by this round. The documented wrapper removal and helper extraction remain within the step. No new architecture, performance, static coverage or feature-integrity gap was found. The two strict expected failures belong to Step 4.

Validation plan effects:

Updated only the Step 2 analysis in `docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md` to record the independent round 4 assessment and evidence limits. Its first sentence remains `Yes. Step 2 has been fully implemented.` No missing-work section remains. Document-level status, other steps and umbrella state were not changed.

### Pre-repair mandatory checks and coverage for step 2 full_suite_levels (exchange 1) (round 4)

Received tree: `d0a192412b48c40aad0df611bc7061ef5b1839db`, exactly matching the request.

Requestor evidence reports a successful `ghog day --full=speed` ending 2026-10-02 at 22:36:26 +02:00: check without auto-fix, affected tests, covered parallel full suite at 100%, and sequential timings with zero outliers or exclusions. The following `ghog day --full=cov` reused that saved speed proof. All four completion searches were clear.

The reviewer did not execute the resolved validation set, rerun coverage, or run optional focused evidence commands in this round. Coverage was assessed statically against the configured `tools` source scope and the relevant unit and acceptance tests. The requestor's executed results are identified as requestor evidence throughout.

### Resolved validation set and sources for step 2 full_suite_levels (exchange 1) (round 4)

- `ghog day --full=speed` (sources: project).
- `ghog day --full=cov` (sources: plan).
- `rg -n 'is_unchanged|write_marker\(' tools/groundhog` (sources: plan).
- `rg -n 'full=none|--full=default' tools/groundhog` (sources: plan).
- `rg -n '\x22ghog day\x22' tools/code_review_validation.py` (sources: plan).
- `rg -n 'call :run_one timings' bin/ghog_cycle.bat` (sources: plan).

### Resolver drift and direction for step 2 full_suite_levels (exchange 1) (round 4)

None. The current `DEFAULT_PROJECT_VALIDATION_COMMANDS` supplies `ghog day --full=speed`; no `.review-validation` declaration exists. Step 2 supplies the coverage walk and four completion searches, and the request supplies no additional command. Comparing the current resolver's ordered-union contract with these inputs yields the same six commands and source labels as the embedded request set. The validation commands were not executed by the reviewer.

### Repository state around validation for step 2 full_suite_levels (exchange 1) (round 4)

The evidence launcher captured the same ordered 64-path set before and after assessment. The comparison reports only the validation-plan path and `<index>` as tracked differences; both are explained by the attributed Step 2 review metadata patch. There are no ignored-artifact changes or untracked-path changes in that boundary.

The applicable-umbrella check is false before and after: this exchange has no umbrella. The pre-existing unstaged transcript change remains unstaged and untouched by the reviewer. There was no implementation/test repair or validation side effect. Assessed index tree: `f4198f7576d28ffdf716e37f3a7b0741d39155d1`.

### Repair inventory for step 2 full_suite_levels (exchange 1) (round 4)

Repairs made:

- Review metadata only: added the round 4 assessment to the Step 2 validation analysis. The evidence launcher returned `attributable: true`; the exact patch was staged. No substantive repair was made.

Paths staged:

- `docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md`: only the attributable nine-line Step 2 assessment addition.

### Commit plan assessment for step 2 full_suite_levels (exchange 1) (round 4)

The reviewer independently ran the canonical `commit-plan-check.bat --format json` against the received tree. It returned exit 0, `state: valid`, `ready: true`, and no diagnostics, with 59 staged paths.

1. `test(tools): answer git in process in slow tests` (5 paths).
2. `feat(groundhog): walk by level with saved proof` (42 paths).
3. `feat(review): default validation proves speed` (8 paths).
4. `feat(prepare-release): prove cov before merging` (2 paths).
5. `docs(full_suite_levels): record step 2 code review` (1 paths).
6. `docs(full_suite_levels): record step 2 validation` (1 paths).

The groups separate the necessary test-duration repairs, groundhog behavior, review default, release gate, review record and validation metadata. The conventional subjects and dependency order fit those scopes. The reviewer metadata patch changes neither membership nor ordering, so `a.commit` needs no amendment. This mechanical pass is one readiness result, not commit authorization.

### Findings and boundaries for step 2 full_suite_levels (exchange 1) (round 4)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 2 full_suite_levels (exchange 1) (round 4)

No implementation rework is requested for Step 2. Consume this advisory answer through the exchange and follow the existing human convergence gate. The reviewer does not authorize or perform a commit.

### Decision rationale for step 2 full_suite_levels (exchange 1) (round 4)

All six readiness results pass: exact identity and request-time tree; complete Step 2 implementation; green requestor validation with no static coverage gap; attributable staged scope; no unresolved current or carried findings; and an independently valid commit plan. This round changed review metadata only. Recommend `commit-ready` as an advisory assessment.

### Final reviewer decision for step 2 full_suite_levels (exchange 1) (round 4)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-2-round-4 -->

## Round 4 by human - Step 2 - human-confirmation

- Recorded: 2026-10-02T23:48:14+02:00
- Exchange: code/code/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/plan.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 2
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-4 -->
