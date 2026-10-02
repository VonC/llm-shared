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
