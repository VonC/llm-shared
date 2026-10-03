# v0.13.0 full_suite_levels implementation tracking and validation

No, it is not implemented.

This document tracks the nine steps of the
[implementation plan](plan.v0.13.0.full_suite_levels.md), from the Step 0 cost
gates to the Step 8 acceptance mapping; Steps 0 to 2 are implemented and
checked, and Steps 3 to 8 are not implemented yet.

> Markdown lint note: never leave a space immediately inside an inline code span
> (MD038); write a needed space as the token `[space]`, as in `` `[space]${x}` ``.
> The empty placeholder ends in `)_.` so the line is not pure italic text (MD036).

---

## File-based IO cost clarification for v0.13.0 full_suite_levels (implementation)

All implementation work must respect the IO classification established in
[the plan](plan.v0.13.0.full_suite_levels.md). The key constraints carried
forward from the plan are:

- A noop or upgrade decision reads only the walk's own scope marker, the floor
  file for the timing fingerprint, and the existing digest walk.
- Group membership reuses the digest's single file walk; `.ghog-groups` is read
  once and only when a group is selected, never by a whole-suite run.
- A `--scope-file` run reads one capture and checks each listed file once; it
  never matches patterns or reads the declaration.
- Markers, status lines and capture copies are written through a temporary
  file and an atomic replace; `pw scope` and `pw progress` read only the
  requirement's metadata lines, never the draft.

---

## Complexity Bound Clarification for v0.13.0 (implementation)

The scaling target for all v0.13.0 code paths is:

- **O(1) amortized per hot-loop event**: one parse per streamed pytest line,
  one compiled-pattern match per project file, one existence check per
  captured file.
- **O(n) total per phase**: one project walk per invocation for digest and
  membership, one pass over the sorted lists for fingerprints and the folder
  set, one data-file analysis over the resolved sources.

Every implemented step should be reviewed against this bound in its
Performance check section.

---

## Step 0. Add the cost gates of the leveled walk

### Analysis of Step 0 implementation state

Yes. Step 0 has been fully implemented.

The new `tests/unit/tools/test_groundhog_levels_perf` package holds the five
planned gates, each bounded by `GATE_TIMEOUT_SECONDS` and marked strict
`xfail` with its owning step. They assert spawned child commands and exit
codes through `cli.main`, and the fresh `ghog day` walk reports them as the
five xfails of both the affected and the full phase.

Independent reviewer assessment (round 1) confirms that the staged tests match
Step 0 and that `a.commit` passes the mechanical checker with both groups in
dependency order. The reviewer assessed coverage statically and relied on the
requestor's recorded green walk; no validation command was repeated.

### Goal for Step 0

Add five time-bound, spawn-counting gates for the default walk, the upgrade,
the stronger-proof noop and the grouped walk, each a strict `xfail` owned by
Step 2 or Step 4.

### Step 0 improvement expectations

- The five gates xfail on the pre-change walk without erroring.
- Each gate carries `pytest.mark.timeout(GATE_TIMEOUT_SECONDS)` and asserts
  spawned commands, not wall-clock time.
- No production file changes.

### What was implemented for Step 0

- **Gate package**: `tests/unit/tools/test_groundhog_levels_perf/__init__.py`
  carries the package docstring and `# eof`;
  `test_groundhog_levels_perf_tdd.py` holds the gates, with
  `GATE_TIMEOUT_SECONDS: Final = 5` on each.
- **Step 2 gates**: `test_default_walk_spawns_no_full_run` expects exactly the
  check.bat and `--no-cov` affected children of a green default walk;
  `test_upgrade_spawns_only_the_full_run` expects one covered full child
  (`--cov-report`, no `--cov-append`, no `--durations=0`) from
  `ghog day --full=cov` after a green default walk;
  `test_stronger_saved_proof_spawns_nothing` expects a sequential
  `--full=speed` walk to make the following `--full=cov` walk spawn nothing.
- **Step 4 gates**: on a `tmp_path` project whose `.ghog-groups` declares
  `sentinel`, `test_grouped_walk_passes_only_group_test_files` expects the
  affected and full children of `ghog day --full=pass --group=sentinel` to
  carry exactly `tests/sentinel/test_core.py` as their `.py` positional paths
  (the group's `conftest.py` and the outside `tests/test_mod.py` excluded);
  `test_grouped_walk_walks_the_tree_once` expects the same walk to exit 0
  with its two group children and one `pathlib.Path.rglob` call, counted
  through `monkeypatch`.
- **Assertion-only failure before the owner**: `_run(argv, deps)` returns
  argparse's `SystemExit` code, every spawn queue holds the children the
  pre-change walk pops, and an autouse fixture clears `GHOG_FULL` and
  `GHOG_GROUP`, so each gate fails on an exit-code or spawn-count assertion
  today, never on an error or an ambient selector.
- **Validation evidence**: the `ghog day` walk ended on 2026-10-02 at
  09:26:28 +02:00 with `exit=0`: check green, `ghog affected --no-cov` with
  `xfail=5`, and `ghog full` with `fail=0 xfail=5 cov=100`. Both plan `rg`
  patterns (`xfail\(strict=True` and `timeout\(GATE_TIMEOUT_SECONDS\)`) list
  five gates. Physical counts are 7 for the initializer and 265 for the gate
  file; the gate file exceeds the advisory 190 because of its documented
  project builders, which is variance below the 550 band, not missing work.

### New types or classes introduced for Step 0

No new type or class was introduced. The step is test-only: module-level
project builders, the `_run` exit-code helper, the `_count_rglob` counter and
the five gate functions reuse `QueueSpawns`, `make_deps` and
`passing_transcript` from `tests/unit/tools/groundhog_acceptance_support.py`.

### Architecture check for Step 0

- **Test boundary**: the gates drive the public `tools.groundhog.cli.main`
  entry point and read only `EXIT_OBJECTIVE_MET` from
  `tools.groundhog.models`; the single faked element is the process factory,
  as in the existing groundhog acceptance tests.
- **Production code**: no file under `tools/` changed, so no layer gained an
  import or a responsibility.
- **Global patch scope**: the `Path.rglob` counter and the environment
  clearing go through `monkeypatch`, restored after each gate.

No DDD-Hexagonal violation or adapter smell is visible. No, there is nothing
that needs to be addressed.

### Performance check for Step 0

- **No new `O(n^2)` or `O(n log n)` path**: no production computation was
  added; each gate builds a project of at most eight files.
- **Hot-path bound**: the rglob counter appends one entry per call and
  delegates the walk unchanged; the spawn assertions read the recorded
  command lists once.
- **Startup or background path**: none; the gates spawn no real process.
- **Plan-bound alignment**: the gates encode the plan's bounds as counts
  (no full child by default, one child on upgrade, none on noop, one tree
  walk per grouped invocation), so a later regression fails on work done,
  not on wall-clock time.

No, there is no performance issue that needs to be addressed.

### Unit test coverage check for Step 0

The coverage gate measures `source = ["tools"]` and omits `*/tests/*` in
`pyproject.toml`, so both staged files sit outside it and the walk's
`cov=100` says nothing about them. No class file under `tools/` is impacted.
Statically, every top-level helper of the gate file is referenced by a gate
or another helper: `_write`, `_project`, `_grouped_project`, `_green_walk`,
`_green_group_walk`, `_day`,
`_run`, `_python_paths`, `_group_spawn_count` and `_count_rglob`;
`clear_ambient_selectors` is an autouse fixture that pytest applies to every
gate. Until the owning steps land, the code after each gate's first failing
assertion does not execute, by design of a strict `xfail` gate.

No, there is no unit-tested class below 100% that needs completing for Step 0.
No, no top-level symbol of the staged files outside the coverage gate is
unreferenced.

### Feature integrity for Step 0

- **Existing feature behavior**: no production file changed; the full suite
  passed with no failure and only the five new xfails.
- **Reporting or diagnostics**: the groundhog closing lines now count five
  xfails in a walk that runs the gates; no report format changed.
- **Compatibility or rollout note**: Step 2 removes `xfail` from the three
  Step 2 gates and Step 4 from the two Step 4 gates; a strict `xfail` that
  passes earlier fails the suite, which surfaces any premature behavior
  change.

No existing feature or reporting capability appears impaired.

---

## Step 1. Free commands.py and add the pure level, proof and marker models

### Analysis of Step 1 implementation state

Yes. Step 1 has been fully implemented.

`tools/groundhog/commands.py` drops from 637 to 415 lines, under its
mandatory 500, once the verdicts and the progress sink move out verbatim to
`verdicts.py` and `progress.py`. The pure `levels.py` and `proof.py` modules
and the key=value proof marker in `snapshot.py` exist with TDD and PBT tests
and stay unused by the walk, which is unchanged. The `ghog day` walk ends
with `exit=0`, both plan `rg` checks return nothing, and no groundhog
acceptance test was edited.

Independent reviewer assessment (round 1) confirms the Step 1 implementation
and its static unit-test coverage. The received index matches the request,
the validation resolver has no drift, and the independent `a.commit` checker
reports four valid groups with no diagnostics. The reviewer relied on the
requestor's recorded green walk and did not repeat tests or measure coverage.

### Goal for Step 1

Move the verdicts and the progress sink out of `commands.py` without behavior
change, and add the pure `levels`, `proof` and marker models with their unit
and property tests.

### Step 1 improvement expectations

- `commands.py` at most 500 lines, every existing test green with updated
  references.
- Level resolution, proof accumulation and cap, noop and upgrade decisions and
  the key=value marker covered by TDD and PBT tests.
- The walk itself unchanged.

### What was implemented for Step 1

- **Verdicts module**: `tools/groundhog/verdicts.py` holds `classify`,
  `_classify_no_tests`, `_classify_coverage`, `setup_reason` and
  `measures_coverage` (the former `_measures_coverage`), moved verbatim;
  `commands.run_tests` and `_report` call them through `verdicts.`.
- **Progress module**: `tools/groundhog/progress.py` holds `Progress` (the
  former `_Progress`) and `postfix`, moved verbatim, plus `sub_label`, which
  `Progress` calls: leaving it in `commands.py` would have made `progress`
  import `commands` back. `commands.py`, `cli.run_exclude` and
  `status.run_with_lifecycle` call `progress.sub_label`.
- **commands.py headroom**: the module keeps the executors, the report
  assembly and the emitters; its docstring records the move, and the
  `cli.py` comments that called it at its line budget now say it was.
- **Levels**: `tools/groundhog/levels.py` adds `FullLevel` (`NONE < PASS <
  COV < SPEED`, with `token`), `LevelSource`, `ResolvedLevel`,
  `ACCEPTED_LEVELS`, `GHOG_FULL_ENV`, `LevelError(GroundhogError)` naming
  the value, its origin (`--full` or `GHOG_FULL`) and the accepted values,
  `command_default`, `resolve_level` (parameter, then a non-empty variable,
  then the default; the environment is an injected lookup, never read when
  the parameter is given), `effective_level`, `level_selector` (empty at
  `none`), `proof_token` (`unproven` for `None`) and `level_from_token`
  for the marker reader.
- **Proof rules**: `tools/groundhog/proof.py` adds `Gate` (valued by the
  lowest level its failure contradicts), `Decision` (`NOOP`, `UPGRADE`,
  `WALK`), `accumulate`, `cap_for_timing`, `decide`, `effective_saved`
  (scope, fingerprint and digest must match, then the timing cap) and
  `earned_by_direct_full` (the design's direct `ghog full` table, `cov` for
  a green parallel `speed` run). Markers reach it through the `SavedProof`
  protocol.
- **Proof marker**: `tools/groundhog/snapshot.py` adds `ProofMarker`, the
  strict `read_proof_marker` (exactly the five keys in order, a valid scope
  key, sha256 hex values, a known proof token), `write_proof_marker` (side
  file then `replace`, a failure logged), `remove_proof_marker`,
  `marker_path_for` (`a.ghog.day.ok` for `whole`, `a.ghog.day.<name>.ok`
  for `group:<name>`, `ValueError` otherwise), the public `source_files`,
  `source_digest(root, files=None)`, `timing_fingerprint` (active gate floor
  and exclusion entries, line 1 left out) and `WHOLE_SCOPE_FINGERPRINT`.
  `is_unchanged` and `write_marker` stay for Step 2 to remove.
- **Package docstring**: `tools/groundhog/__init__.py` names the four new
  modules and the marker.
- **Tests**: new packages `test_groundhog_verdicts` (the classify and
  setup-reason cases moved unchanged from `test_groundhog_cli.py`, the
  outliers-last case from `test_groundhog_commands.py`, plus a
  `measures_coverage` case), `test_groundhog_progress` (the label and
  postfix cases moved there, plus direct sink cases in both modes),
  `test_groundhog_levels` (TDD and PBT), `test_groundhog_proof` (TDD and PBT)
  and `test_groundhog_snapshot_marker`. `test_groundhog_commands.py` gains
  nine CLI-driven tests and `test_groundhog_cli.py` four dispatch tests, so
  each covers its namesake module on its own.
- **Transcript lint**: the staged-path and commit-plan paths of the Step 0
  code review transcript are now code spans; their bare `__init__.py` read as
  underscore emphasis (MD050) and failed the markdown check of the walk.
  Formatting only.
- **Validation evidence**: the `ghog day` walk ended on 2026-10-02 at
  11:57:02 +02:00 with `exit=0`: check green, `ghog affected --no-cov`
  green, `ghog full` with `fail=0 xfail=5 cov=100`; `ghog status` reports
  `state=done exit=0`. An earlier walk at 11:47 crashed in the xdist
  scheduler (`KeyError` on a worker controller) and did not reproduce;
  `ghog single` on the eight step test targets passed in focus (158 tests,
  the five Step 0 gates xfailed). Both plan `rg` patterns return nothing.
- **Line counts**: `commands.py` 415 (mandatory at most 500), `verdicts.py`
  140, `progress.py` 145, `levels.py` 212, `proof.py` 240, `snapshot.py`
  406, `cli.py` 399, `status.py` 507; tests `test_groundhog_cli.py` 468,
  `test_groundhog_commands.py` 500, verdicts 186, progress 239, levels 151,
  levels PBT 64, proof 207, proof PBT 87, marker 268. Counts above their
  advisory estimates (`levels`, `proof`, `snapshot`, the verdicts and marker
  tests, `test_groundhog_commands.py`) are variance below the 550 band, not
  missing work.

### New types or classes introduced for Step 1

- `progress.Progress`: the per-mode progress sink, moved and made public.
- `levels.FullLevel` (`IntEnum`), `levels.LevelSource` (`StrEnum`),
  `levels.ResolvedLevel` (frozen dataclass) and `levels.LevelError`
  (`GroundhogError` carrying `value` and `origin`).
- `proof.Gate` and `proof.Decision` (enums) and `proof.SavedProof`, the
  read-only protocol of a saved marker.
- `snapshot.ProofMarker`: the frozen five-field marker record, which
  satisfies `SavedProof`.

### Architecture check for Step 1

- **Pure domain modules**: `levels.py` and `proof.py` touch no file, process
  or environment; `resolve_level` receives the environment as a callable.
  `proof.py` imports only `levels` and the exit codes of `models`;
  `levels.py` imports `models` and the `SUB_FULL` name from `runner`, the
  module that owns every groundhog subcommand name, and calls nothing there.
- **Port direction**: `proof.effective_saved` reads the marker through the
  `SavedProof` protocol declared in `proof.py`; `snapshot.py`, the file
  adapter, imports `levels` and supplies a structurally compatible marker.
  The proof rules do not import the snapshot adapter.
- **No cycle**: `verdicts`, `levels` and `proof` never import `commands` (the
  plan `rg` check returns nothing); `progress` imports `reporting`,
  `runner` and `models` only, and `commands` imports `progress` and
  `verdicts`.
- **Responsibilities**: classification lives in `verdicts`, presentation of
  progress in `progress`, run orchestration and reports in `commands`; the
  new models hold rules only and are not wired yet.

No DDD-Hexagonal violation or adapter smell is visible. No, there is nothing
that needs to be addressed.

### Performance check for Step 1

- **No new `O(n^2)` or `O(n log n)` path**: `source_files` keeps the one
  existing sort; `source_digest(root, files)` lets a later caller reuse that
  walk instead of walking twice.
- **Marker and fingerprint IO**: the reader parses one five-line file; the
  writer writes one side file and replaces; `timing_fingerprint` reads the
  floor file through the existing floor and exclusion readers and hashes the
  entries in file order, linear in the entries.
- **Pure rules**: `accumulate`, `decide`, `effective_saved` and
  `earned_by_direct_full` are constant-time over at most four gates.
- **Startup or background path**: none added; the walk does not call the new
  modules yet.

No, there is no performance issue that needs to be addressed.

### Unit test coverage check for Step 1

The gate measures `source = ["tools"]` and omits `*/tests/*` and
`*/__init__.py` in `pyproject.toml`; every staged class file sits under
`tools/groundhog`, so the walk's `cov=100` covers them, and the
docstring-only `tools/groundhog/__init__.py` is omitted by design.

- `verdicts.py`: `test_groundhog_verdicts` reaches every branch (crash,
  usage error, no tests per subcommand, failures, gate unset, TOTAL miss,
  gap, outliers last, each setup reason, `measures_coverage`).
- `progress.py`: `test_groundhog_progress` drives the sink in LLM mode
  (governed and suppressed lines, plain and judged finish) and user mode
  (no total, bar opening, advance, top-off, crash catch-up, no bar), plus
  `postfix` and `sub_label`.
- `levels.py` and `proof.py`: their TDD files cover every function and
  branch; the PBT files add the rejection, source, accumulation, noop, walk
  and timing-cap invariants.
- `snapshot.py`: the plan splits it between the unchanged
  `test_groundhog_snapshot.py`, which covers the pre-existing digest and
  legacy marker functions, and `test_groundhog_snapshot_marker`, which covers
  every Step 1 addition, including the write and remove failure paths and
  each malformed-marker case.
- `commands.py`: `test_groundhog_commands.py` now reaches every executor
  path on its own (missing and failing check.bat, the exit-9 and
  missing-pytest stops, sequential full with reset, baseline and nag, gap
  rows, missing TOTAL, crash, covered affected, focus run with and without a
  baseline, init success and failure, plus the duration scenarios).
- `cli.py`: `test_groundhog_cli.py` now routes status, the live-run
  refusal, the detached walk, init and the `__main__` guard beside its
  existing cases, so it covers the module on its own.
- `status.py`: only its label lookup changed, to `progress.sub_label`, with
  identical behavior; `test_groundhog_status.py` was not edited by the step.

No, there is no unit-tested class below 100% that needs completing for
Step 1.

### Feature integrity for Step 1

- **Existing feature behavior**: the moved functions are unchanged and keep
  the `groundhog` logger, so progress, closing and next-step lines are
  identical; the day walk, its snapshot noop and its markers are untouched.
- **Reporting or diagnostics**: no report format changed; the closing lines
  of the walk read as before.
- **Compatibility or rollout note**: the five Step 0 gates stay strict
  `xfail`; the new modules wait for Step 2, which also removes
  `is_unchanged` and `write_marker`.

No existing feature or reporting capability appears impaired.

---

## Step 2. Run the walk and the full run by level, with saved proof

### Analysis of Step 2 implementation state

Yes. Step 2 has been fully implemented.

The level-shaped walks, saved-proof reuse, evidence reporting and caller
defaults are implemented. Independent reviewer assessment of rounds 1 to 3
found two gaps, both now fixed with their regressions:

- **R1**: a pytest child interruption was treated as a contradicted gate and
  could discard valid saved proof. Round 2 matched only the bare banner;
  round 3 recognized the bare and messaged `KeyboardInterrupt` banners and
  the `pytest.exit` banner, but a `pytest.exit` returning 0 or 1 still read
  as a finished run, green and earning proof. Round 4 makes the banner crash
  the run whatever its return code, so such a child exits 4, earns nothing
  and judges no gate.
- **R2**: the no-baseline `ghog single` message now keeps the carried level
  (confirmed by the round 2 assessment).

The requestor found and fixed a third gap while validating round 3:

- **Digest after check.bat**: the walk recorded the digest taken before
  check.bat. When check.bat auto-fixed a source, the saved proof matched no
  source state, and a forced walk could carry an older saved proof onto the
  fixed sources. The walk now takes the digest again after a green
  check.bat, as the tests then run on those sources (confirmed by the
  round 3 assessment).

The requestor's `ghog day --full=speed` and `ghog day --full=cov` validation
walks are green on the repaired sources.

Round 4 independent reviewer assessment confirms R1 is complete: the
interruption banner sets `crashed` independently of the child's return code,
so custom codes 0 and 1 exit 4 and earn no proof. The regression cases cover
direct full runs, walks without a marker, and interrupted affected, full and
timing children with a saved marker. Failures or internal errors reported
first still judge a gate. R2 and the source-digest repair remain complete.
The reviewer inspected coverage statically and found no gap; the validation
walks above remain requestor evidence.

### Goal for Step 2

Wire levels and saved proof through the CLI, the walk, the full run, the
reports, the status file and the detached walk, and move the requestor
default, the prepare-release operations and the no-argument cycle to their
explicit levels.

### Step 2 improvement expectations

- Plain `ghog day` stops after the affected tests with the skip line; each
  level runs its own full-run shape and verdict; restart lines carry the level
  and never `--full=none`.
- The proof marker drives noops and upgrades, is capped by any contradicted
  gate, and is rewritten or removed after every walk that judged a gate.
- The closing and status lines carry `full=`, `src=`, `proof=`, `reused=` and
  `scope=`; the three Step 2 gates pass without `xfail`.

### What was implemented for Step 2

- **Invocation and seams**: `context.Invocation` gains `level` (`None` means
  the command default), `level_source` and `in_walk`, the flag a step derived
  by the walk carries so its report leaves the next step to the walk;
  `context.Deps` gains `environ`, the one read of `GHOG_FULL`.
- **CLI resolution**: a `leveled` parent parser gives `check`, `full`,
  `affected`, `single` and `day` a free-string `--full`; `cli.main` resolves
  the level after the root and before the live-run check and the lifecycle
  bracket (`_with_level`), and a `LevelError` prints
  `ghog: invalid full level '<value>' from <--full|GHOG_FULL>; accepted values: pass, cov, speed`
  and returns 5 without writing `a.ghog.status`. `timings`, `status`,
  `init` and `exclude` never read the variable.
- **Run shapes**: `runner.pytest_command(..., level=FullLevel.SPEED)` builds a
  `full` run at `pass` with `--no-cov` and no `--durations`, at `cov` covered
  without `--durations`, at `speed` as before; `runner._measures` holds that
  decision. `verdicts.measures_coverage` is false for `full` at `pass`, and
  `durations_summary.measures_durations` builds its probe command at the
  effective level, so a run below `speed` never rewrites the floor file.
- **Evidence**: new `tools/groundhog/evidence.py` holds `Reused`,
  `RunEvidence` (`closing_keys`, `running_keys`), `RunOutcome` (code,
  evidence, the last counters and closing values) and `for_invocation`:
  level keys for a walk and a direct `ghog full`, `scope=` alone for any other
  run and every step inside a walk.
- **Day walk**: `day.walk` reads `snapshot.effective_proof` and asks
  `proof.decide`: a noop prints the noop line (`reused=all`), an upgrade
  prints a `reused from snapshot` header for check and affected and runs the
  full step, otherwise the whole chain runs. At `none` it stops after a green
  affected step with the skip line; at parallel `speed` a green full step is
  followed by a timed `timings` step. Each failed gate is recorded, the proof
  is accumulated and capped (`proof.accumulate`), and `snapshot.save_proof`
  rewrites or removes the marker on the digest the test steps ran on; exits
  5 and 9 write nothing. The walk ends
  with its own `ghog day done` closing line repeating the last step's
  counters with the five evidence keys.
- **Direct runs**: `commands.run_tests_outcome` runs a pytest subcommand at
  its level and returns a `RunOutcome`; a direct `ghog full` reports
  `proof.earned_by_direct_full` and, green on a parallel project at `speed`,
  the `cov` success line plus the line saying durations were not measured.
- **Next-step builders**: `reporting_nextstep` replaces every fixed restart
  string with builders fed by `restart_command(level, scope_selector="")`
  and `carried_selector(level)`: check, affected, single, coverage-gap,
  outlier and timing-failure lines carry the level, never a `none` selector;
  `success_line` gives one line per level naming the whole suite,
  `noop_line` names the request, the saved proof and that no check ran, the
  covered-affected gate-reached line names `ghog check` then the walk at the
  carried level, and a standalone `ghog affected --no-cov` with no level keeps
  `Next: ghog full`. `StepContext` carries the level, the walk flag and the
  parallel flag. The exclusion hint states that an exclusion is accepted only
  after an attempted improvement.
- **Reporting**: `reporting.ClosingMetrics` gains `evidence`, appended by
  `closing_line` after `exit=` (the value object keeps the line at the
  five-argument lint limit, so the plan's `closing_line(..., evidence="")`
  reads as this field); `step_reused_line` heads a reused step,
  `status_killed_line(level)` relaunches a killed run at its recorded level,
  and `crash_block` restarts at the carried level.
- **Status and detach**: `status.write_running` and `write_done` add the
  running and closing keys (before `exit=` on the done line), `_dispatch`
  returns a `RunOutcome`, and a killed run is relaunched at the `full=` of
  its recorded line. `status.py` passed the plan's 550-line trigger, so its
  split guidance applies: `run_day_detached`, `default_detach_factory`,
  `_spawn_survivor` and `_detached_day_command` move to new
  `tools/groundhog/detach.py`, where `--full=<token>` is forwarded only for
  a `param` level.
- **Snapshot**: the one-line digest writer and its comparison are removed;
  `effective_proof(root, scope_key, fingerprint, files=None)` returns the
  current digest and the saved proof valid for it, and `save_proof` writes or
  removes the scope's marker with a timing fingerprint computed after the
  walk's own writes.
- **Levels**: `levels.py` no longer imports `runner` (a local `_FULL_SUB`
  names the subcommand); the runner now imports `FullLevel`, so the old
  import would have been a load-order cycle, and the pure model no longer
  depends on the process adapter.
- **Callers**: `code_review_validation.DEFAULT_PROJECT_VALIDATION_COMMANDS`
  is `("ghog day --full=speed",)`; `prepare_release_plan_workflow` names
  `run ghog day --full=cov` and `run git range-diff and ghog day --full=cov`;
  the no-argument `bin/ghog_cycle.bat` runs `day` alone, as its header says.
- **Integer wrappers removed**: the plan's Q05 kept `day.run_day` and
  `commands.run_tests` as integer wrappers to avoid test churn. Once the
  status dispatch uses `walk` and `run_tests_outcome`, no caller or test
  calls them, so they are removed rather than kept as dead code.
- **Review repairs (R1, R2)**:
  - The parser records pytest's interruption banner: the crash message pytest
    prints between `!` runs for a `KeyboardInterrupt`, bare or with a message,
    or an explicit `pytest.exit`. A collection error prints `Interrupted: N
    errors during collection` instead. The banner marks the run crashed
    whatever its return code, 0 and 1 included, since `pytest.exit` may end
    an unfinished suite with either. `RunResult.interrupted` marks a child
    stopped by a signal or with that banner, before it reported any failure
    or internal error.
  - The pure `proof.judges_gate` names the outcomes that judge no gate: a
    setup error, a project without a pytest suite and such an interrupted
    child. `RunOutcome.judged` carries it, and the walk writes nothing after
    them, so the saved proof stays as it was. A collection error (the same
    exit without the banner) and a failure reported before the interruption
    still contradict their gate.
  - `reporting_nextstep.no_baseline_line(level)` replaces the fixed
    no-baseline notice, so `ghog single ... --full=cov` without a failure
    baseline names `ghog full --full=cov`, and plain `ghog full` with no
    level.
- **Digest after check.bat**: HEAD's walk wrote its digest at the end, after
  any check.bat auto-fix. The first Step 2 walk froze the digest of its start
  instead. A round 3 validation walk showed the effect: check.bat's Ruff fix
  moved the sources, and the next `ghog day --full=cov` ran the whole chain
  again instead of a noop. A green check.bat now moves the walk's state to a
  fresh digest (`EffectiveProof.on_sources`), which keeps the saved proof
  only when that digest did not change. The marker records the sources the
  test steps judged, and a saved proof of the sources before a fix no longer
  survives a forced walk.
- **Speed validation repairs**: the first `ghog day --full=speed` walk, the
  first ever to judge speed in this parallel project, flagged eight
  pre-existing Git-bound test calls above the one-second floor. They were
  shortened, not excluded. `test_prompt_workflow_docs_layout_acceptance_tdd.py`
  answers the six read-only `git` commands of `pw` in process from the files
  on disk (`_FreshBranchGit`, any other command fails). The `review_resume`
  foreground cancellation answers its preflight's two home queries in process
  (`_IgnoredHomeGit`). The `review_resume` acceptance `ReviewRepository` copies
  a seed repository built once per test process. The slowest repaired call
  dropped from 6.21s to 0.10s, with every assertion kept. A later walk saw the
  markdown-check launcher contract at 1.08s (a `cmd.exe` and Python start of
  about half a second); its real launch now runs once in a fixture, outside
  the measured call. A third saw the three-cycle one-discovery review scenario
  at 1.03s (0.6s to 0.8s alone); its first cycle is now a fixture, and two
  tests each drive one more cycle with the same discovery (0.30s and 0.26s).
- **Tests**: new `test_groundhog_acceptance_levels` (a `support` module, one
  test per level row in `test_groundhog_acceptance_levels_tdd.py`, one per
  proof row plus the exit-5 and exit-9 no-gate cases in
  `test_groundhog_acceptance_proof_tdd.py`) and `test_groundhog_evidence`;
  AT11 and AT16 of `test_groundhog_acceptance_day.py` cover the default
  two-step walk, the `--full=cov` chain, the proof marker and its removal;
  the runner, reporting, next-step, status, detach, snapshot, CLI, commands,
  verdicts and acceptance tests follow the builders and the new keys; the
  review tests carry the new default literal and the prepare-release test
  pins the two operation strings. The shared `conftest.py` clears
  `GHOG_FULL` for every unit test and `make_deps` takes an `environ`
  mapping. The three Step 2 cost gates lose their `xfail`.
- **Validation evidence**: the `ghog day --full=cov` walk ended on 2026-10-02
  at 17:03:53 +02:00 with `exit=0`: check green with no ruff auto-fix,
  `ghog affected --no-cov` green, `ghog full` green with `xfail=2` (the two
  Step 4 gates) and `cov=100`; its closing line ends with
  `full=cov src=param proof=cov reused=none scope=whole` and `ghog status`
  replays it with `exit=0`. After the review repairs, the speed repairs and
  the digest fix, the requestor validation `ghog day --full=speed` ended on
  2026-10-02 at 22:36:26 +02:00 with `exit=0` on the whole chain: check with
  no auto-fix, affected, the parallel full run at `cov=100`, then the
  sequential timing pass with `outliers=0 excluded=0` (slowest call 0.41s),
  closing `proof=speed reused=none`. A following `ghog day --full=cov` was a
  noop met by that saved `speed` proof (`reused=all`). The four plan `rg`
  patterns return nothing.
- **Line counts**: `commands.py` 531, `status.py` 391 after the split,
  `detach.py` 194, `reporting.py` 509, `cli.py` 459,
  `reporting_nextstep.py` 581, `runner.py` 315, `day.py` 401,
  `evidence.py` 149, `snapshot.py` 485, `context.py` 121, `parser.py` 270;
  tests: acceptance levels 257, acceptance proof 403, support 169,
  `test_groundhog_acceptance_day.py` 299, `test_groundhog_status.py` 484,
  `test_groundhog_detach.py` 407, `test_code_review_request_tdd.py` 600 (three
  docstring lines beside the literal update). Counts above their advisory
  estimates (`reporting_nextstep.py` in the 550-through-650 band, `reporting`,
  `cli`, `runner`, `day`, `evidence`, the status and detach tests) are
  variance at or below 650, not missing work.

### New types or classes introduced for Step 2

- `evidence.Reused` (`StrEnum`: `none`, `check+affected`, `all`).
- `evidence.RunEvidence` (frozen dataclass: scope key, resolved level,
  proof, reuse) and `evidence.RunOutcome` (frozen dataclass: code, evidence,
  last counters and closing values).
- `snapshot.EffectiveProof` (frozen dataclass: current digest, valid saved
  proof; `on_sources(digest)` moves it to the digest after check.bat).
- `reporting_nextstep.StepContext` (frozen dataclass: carried level, walk
  flag, parallel flag).
- `day._Walk` (private dataclass: the running record of one walk) and
  `commands._Judged` (private frozen dataclass: one judged pytest run).
- `tools/groundhog/detach.py`: a module, not a class, holding the detached
  launch moved out of `status.py`.

### Architecture check for Step 2

- **Pure models stay pure**: `levels.py` and `proof.py` import only each
  other and `models`; `levels.py` dropped its `runner` import, so the
  adapter now depends on the model and not the reverse.
- **Adapters and the walk**: `snapshot.py` (file adapter) applies the
  pure `proof.effective_saved` rule and writes markers; `day.py`
  sequences the steps through `commands` and `snapshot`; `status.py`
  owns the lifecycle file and `detach.py` the survivor spawn, each importing
  downward only (`detach` uses `status` for the lifecycle file; `context`
  and `cli` import `detach`). No import cycle: every changed module imports
  cleanly whichever loads first.
- **Evidence placement**: `evidence.py` holds value objects and one builder;
  it imports subcommand names from `runner` and the whole-suite scope key
  from `snapshot`, the modules that own those names since Step 1, and calls
  no IO there. Text rendering stays in `reporting` and `reporting_nextstep`,
  which stay pure.
- **Seams**: the environment is read only through `Deps.environ`, and the
  survivor spawn only through `Deps.detach_factory`; tests never touch the
  process environment.
- **No-gate rule**: which outcomes judge no gate is the pure
  `proof.judges_gate`; the parser and the runner only report what the child
  printed and returned, and the walk reads the `judged` flag of the outcome.

No DDD-Hexagonal violation or adapter smell is visible. No, there is nothing
that needs to be addressed.

### Performance check for Step 2

- **No new `O(n^2)` or `O(n log n)` path**: a noop or an upgrade computes
  the source digest once over the existing sorted file walk; the whole chain
  computes it once more after a green check.bat, as HEAD's walk did at its
  end, so its IO stays at today's two digest walks. The marker read parses
  five lines, and the timing fingerprint reads the floor file only when a
  marker was read, then once more at the marker write.
- **Noop cost**: a noop now skips check.bat as well as the tests; an upgrade
  skips check and affected; the default walk skips the full run, which the
  three cost gates verify by counting spawned children.
- **Status and reports**: the evidence keys are fixed-size strings; the
  killed-run relaunch applies one regular expression to one status line.
- **Startup or background path**: none added; the detached launch keeps its
  bounded handshake.

No, there is no performance issue that needs to be addressed.

### Unit test coverage check for Step 2

The gate measures `source = ["tools"]` and omits `*/tests/*` and
`*/__init__.py` in `pyproject.toml`; every staged production class file sits
under `tools`, and the docstring-only `tools/groundhog/__init__.py` is
omitted by design. The requestor reports `cov=100`. The reviewer assessed
the source scope and unit tests statically and did not measure coverage.

- `evidence.py`: `test_groundhog_evidence` covers both key renderings, the
  absent proof, the scope-only evidence, `for_invocation` per subcommand,
  with an earned proof and inside a walk, and the outcome defaults.
- `day.py`: its packages (`test_groundhog_acceptance_levels`,
  `test_groundhog_levels_perf`) and `test_groundhog_acceptance_day.py` reach
  the noop, the upgrade, the whole chain, the check and affected stops, the
  exit-9 affected stop, the exit-5 full and timing stops, the parallel timing
  pass (green, failing, crashing, outliers) and the marker write and removal.
- `detach.py`: `test_groundhog_detach.py`, its namesake, covers the launch,
  the handshake, the spawn failure, the silent child, the forced and the
  parameter-level forwarding, the environment level left out, and every
  survivor spawn branch.
- `status.py`: `test_groundhog_status.py` covers the keyed running and done
  lines, the walk and pytest-subcommand lifecycle, the check dispatch, and the
  killed-run relaunch with a recorded, an unknown and no level.
- `reporting_nextstep.py`, `reporting.py`, `runner.py`, `snapshot.py`,
  `cli.py`, `verdicts.py` and `commands.py`: their namesake tests cover every
  new builder and branch: the per-level lines and the extended Q30 rule, the
  appended keys, the reused and killed lines, the run shape per level,
  `effective_proof` and `save_proof`, the level resolution and its errors,
  `measures_coverage` per level, and the direct runs.
- `durations_summary.py` and `context.py`: one argument and three dataclass
  fields changed; neither module has a namesake unit test from before this
  effort, and their lines are reached by the commands and CLI tests under the
  gate.
- `code_review_validation.py` and `prepare_release_plan_workflow.py`: their
  namesake tests pin the new default and the two operation strings.

- Review repairs:
  - `test_groundhog_parser.py` covers the three real interruption banners
    (bare and messaged `KeyboardInterrupt`, `pytest.exit`) and the
    collection-error banner it must not match.
  - `test_groundhog_runner.py` covers the crash and interrupted flags for a
    signal, each banner, a `pytest.exit` returning 3, 1 or 0, a bare
    interrupted exit, the collection-error banner, a failure first (exit 2
    and exit 1) and an internal error first.
  - `test_groundhog_proof_tdd.py` covers `judges_gate` per outcome.
  - The proof acceptance file runs a forced walk with a saved `speed` marker
    for each banner and return code (bare, messaged, `pytest.exit` returning
    2, 1 and 0), whose affected, full or timing child is interrupted. Each
    exits 4 and leaves the marker byte for byte unchanged. For the same five
    children, a walk at `pass` without a saved marker writes none and closes
    `proof=unproven`, and a direct `ghog full --full=pass` exits 4 and claims
    no proof. One more walk, whose failure precedes the interruption, is
    capped to `none`.
  - The next-step and level acceptance files cover the no-baseline line at
    `pass`, `cov`, `speed` and `none`, never printing `--full=none`.
  - `test_groundhog_snapshot.py` covers `EffectiveProof.on_sources` on an
    unchanged and a moved digest. The proof acceptance file runs a walk
    whose check.bat fixes a source, and the same walk again is a noop. A
    forced walk over a saved `speed` proof records `cov` on the fixed digest.

No, there is no unit-tested class below 100% that needs completing for
Step 2.

### Feature integrity for Step 2

- **Existing feature behavior**: plain `ghog day` now stops after the
  affected tests, as the design requires; every caller that needs a
  full-suite proof names its level in the same step (requestor default
  `speed`, prepare-release `cov`), and the no-argument cycle runs `day` alone.
  A direct `ghog full` keeps its single-run shape at its `speed` default.
- **Reporting or diagnostics**: closing and status lines keep every current
  key and append the evidence keys after them, so readers matching keys by
  name keep working; `ghog status` replays the new done line. The groundhog
  manual, the specification and the wiki page still quote
  `Objective reached`; Step 7 updates the manual and specification, and the
  wiki is left to the prepare-release documentation audit, as the plan's
  rollout note states.
- **Compatibility or rollout note**: a marker written before this step reads
  as no proof, so the first walk after the upgrade runs in full and rewrites
  it with `proof=` keys. Restart lines carry no scope selector until Step 4
  adds `--whole-suite`. The two grouped cost gates stay strict `xfail` for
  Step 4.

- **Review repairs**: an interrupted child exits 4 with its crash block, as
  a pytest interruption did before; a `pytest.exit` returning 0 or 1, which
  read as a finished green run, now does too. Only the interruption's effect
  on the saved proof changed. The no-baseline notice keeps its wording with
  the level selector added. A walk whose check.bat auto-fixes sources again
  serves the next walk, as HEAD's end-of-walk digest did.

No existing feature or reporting capability appears impaired.

---

## Step 3. Declare groups, capture scopes, and list exclusions

### Analysis of Step 3 implementation state

Yes. Step 3 has been fully implemented.

Declarations resolve against the shared inventory, captures round-trip with
strict identity and file checks, and group and exclusion listings provide
the specified read-only output and exit-5 diagnostics. Slashed and anchored
folder patterns include descendants, the exclusion module has direct unit
tests for its strict APIs, and the changed CRLF files retain their format.

The project `ghog day --full=speed` walk finished on 2026-10-03 at 10:37:12
+02:00. Its coverage phase reported `cov=100`; the final timing phase closed
with `fail=0 warn=0 xfail=2 cov=skipped outliers=0 excluded=0 exit=0
full=speed src=param proof=speed reused=none scope=whole`. The final
`cov=skipped` describes that timing phase, not the earlier coverage phase.
The plan's `ghog day --full=cov` then finished at 10:38:35 +02:00 with
`fail=0 warn=0 xfail=0 cov=skipped outliers=skipped excluded=skipped exit=0
full=cov src=param proof=speed reused=all scope=whole`: the unchanged-source
speed proof met the requested objective without repeating tests. Both logs
passed the freshness check and `ghog status` confirmed `state=done exit=0`.
The two expected failures in the measured walk remain assigned to Step 4.

### Goal for Step 3

Add the `.ghog-groups` reader, the gitignore-style matcher, the group resolver
and fingerprint, the tools-level captured-scope model, and the read-only
`ghog groups` and `ghog exclude --list [--since]` listings.

### Step 3 improvement expectations

- `ghog groups <name>` applies the exit-5 rules a run will apply, each message
  naming the cause or the empty side.
- Captures round-trip and refuse an incomplete, tampered or stale capture.
- The exclusion listing and comparison print `exclusions=<count>`, `changed`,
  `unchanged`, `unreadable` or `unverified` as the design states.

### What was implemented for Step 3

- `group_patterns.py` compiles normalized rules with `glob.translate` and
  applies ordered inclusion and exclusion. Segment wildcards, recursive
  wildcards, basename rules, folder rules and last-match precedence are
  covered, including the sentinel example and descendant matching for
  slashed and anchored folder names.
- `project_settings.py` reads pytest and coverage settings once per
  resolution phase. Its public accessors expose filename patterns, omissions,
  sources and branch measurement; coverage lists preserve spaces and Windows
  separators. `gate.py` imports the shared TOML table helper.
- `groups.py` validates declarations and names, resolves both sides from the
  supplied `snapshot.source_files` inventory, filters pytest filenames and
  coverage omissions, and rejects empty membership with the side named.
  Sources outside the configured coverage source remain eligible.
- `scope_capture.py` provides complete scope values, canonical fingerprints,
  JSON serialization, strict schema and identity checks, missing-file checks
  and atomic capture replacement. Provenance is retained separately from
  identity, and whole-suite identity preserves the established fingerprint.
- `linear_order.py` supplies iterative UTF-8 trie ordering for canonical
  membership, fingerprints and exclusion output without a comparison sort.
- `exclusions.py` adds strict reading, complete saved-listing parsing and
  comparisons that report only added or raised exceptions. Reading respects
  the configured artifact home and legacy location without migration.
- `listings.py`, `cli.py`, `context.py` and `runner.py` wire `ghog groups
  [name]` and `ghog exclude --list [--since=<file>]`. Listings dispatch before
  live-run and lifecycle handling, consume environment setup output, and
  return exit 5 for invalid combinations or unusable evidence.

### New types or classes introduced for Step 3

- `ScopeKind` distinguishes whole and group scopes; frozen `ResolvedScope`
  carries patterns, membership, fingerprint and provenance, with stable key,
  selector, label and JSON representations. `CaptureError` preserves the
  shared `bound scope unusable` diagnostic prefix.
- Frozen `Pattern` holds a compiled expression and its inclusion decision;
  frozen `Declaration` holds the two ordered pattern lists. `GroupError`
  identifies declaration and membership failures.
- Frozen `Settings` holds one resolution phase's collection and coverage
  settings. Internal `_Node` stores trie edges and terminal values, including
  duplicates. `_SubcommandParser` converts listing parser failures to setup
  errors while preserving other commands' argparse behavior.

### Architecture check for Step 3

Matching and fingerprint computation are pure. The shared capture module has
no groundhog or review-exchange dependency; its explicit filesystem helpers
validate listed files and publish captures without resolving a group again.
Declaration and configuration IO stays in the group and settings adapters.
Listings orchestrate those adapters and render through `commands.emit_summary`;
the CLI owns argument validation and read-only dispatch.

The structural checks find no `pathspec` or `fnmatch` in the group matcher,
no groundhog or review imports in the capture module, and only the declaration
read in `groups.py`. The existing inventory is passed into resolution.

Every changed Python file remains below the 650-line ceiling. Production
counts are CLI 528, exclusions 270, gate 107, context 128, runner 319,
package initializer 69, capture 243, ordering 56, patterns 89, groups 169,
listings 69 and settings 136. New unit-test files are at most 133 lines;
the modified gate test is 118 lines and the exclusion unit tests remain below
350 lines. No split is required. The staged CLI and runner blobs contain
only CRLF line endings. The staged whitespace check passes with
`core.whitespace=cr-at-eol`, preserving that established convention.

No DDD-Hexagonal violation or adapter smell is visible. No, there is nothing
that needs to be addressed.

### Performance check for Step 3

The resolver does not walk the tree again or open source and test contents.
All-group listing reads the declaration and settings once, and each group's
rules are compiled once before scanning the supplied inventory. For fixed
declarations, membership work is linear in the inventory and path input.
Across variable declarations the explicit bound is the inventory multiplied
by the declared rules, as the plan permits.

Canonical ordering uses an iterative trie over UTF-8 bytes with at most 256
edges per node. It is linear in input bytes, preserves duplicate values and
does not recurse on long prefixes. Fingerprinting and capture serialization
are linear passes over their content; capture validation checks each distinct
listed file once. Exclusion comparison uses dictionary membership and a
single pass. No new comparison sort or pairwise membership scan is introduced.

No, there is no performance issue that needs to be addressed.

### Unit test coverage check for Step 3

The configured gate measures `source = ["tools"]` with `fail_under = 100`.
It omits tests, package initializers and the existing explicitly listed thin
adapters and interfaces. Every changed executable production module is in
scope; the changed groundhog initializer contains documentation only.
The completed `day --full=speed` walk's coverage phase reports `cov=100`, and
its separate timing phase reports no outliers. This implementation check
assessed the source and unit tests statically and ran no test command.

- `test_scope_capture` covers whole and group round trips, selectors, labels,
  schema/type errors, malformed or altered content, invalid relative paths,
  fingerprint mismatch, vanished files and atomic-write failure cleanup.
  Its property test proves file-order independence.
- `test_groundhog_group_patterns` covers the required wildcard and precedence
  examples, with properties for basename depth, cancelling exclusions and
  segment boundaries.
- `test_groundhog_groups` covers declaration errors, empty sides, settings
  filters, non-Python inventory entries, sources outside the coverage root,
  membership identity and the single declaration read.
- `test_groundhog_project_settings` covers defaults, accessors, configuration
  formats, precedence, malformed optional settings and coverage path syntax.
  Existing `test_groundhog_gate.py` still exercises the moved table helper
  through gate loading.
- `test_groundhog_listings` covers both CLI commands, output and comparisons,
  malformed and unreadable evidence, duplicate saved entries, exit-5 argument
  diagnostics, preserved live-run state and legacy files, and unchanged parser
  errors for other commands. Existing CLI and runner unit tests retain
  coverage of their prior behavior; invocation fields are exercised through
  the CLI tests.
- `test_groundhog_exclusions.py` directly covers the strict reader's absent
  file and section, root fallback without migration, home precedence,
  comment and blank lines, malformed and non-finite or negative durations,
  and undecodable evidence. It covers stable listing order and counts,
  round trips, empty and ambiguous saved output, duplicate nodes and invalid
  counts, and added, raised, lowered, unchanged and removed exceptions.
  Together with its existing tolerant-read and write tests, every statement
  of `exclusions.py` is exercised by its own unit test file.
- `test_linear_order` compares Unicode ordering with Python's lexical order
  using generated lists and covers long shared prefixes without recursion.

No, there is no unit-tested class below 100% that needs completing for Step 3.
No changed executable production file lies outside the coverage gate.

### Feature integrity for Step 3

Existing whole-suite execution, proof markers, duration collection and
reporting remain unchanged. This step introduces no run scope selector;
grouped execution and its two expected-failure gates belong to Step 4.
The tolerant exclusion reader and exclusion writes retain their prior roles;
strict evidence reading is confined to the new listings. Read-only listings
do not replace lifecycle state, migrate a legacy floor file or replay setup
text into saved exclusion evidence. No existing feature or reporting
capability appears impaired.

---

## Step 4. Select a scope and run, gate and prove inside a group

### Analysis of Step 4 implementation state

Not started. Step 4 is not implemented because Step 3 has not landed yet.

Run commands accept no scope selector and every run still covers the whole
suite.

### Goal for Step 4

Resolve one scope per invocation, narrow the affected, full and timing runs to
the group's test files, judge the group coverage gate and grouped durations,
keep one marker per scope, and carry the scope through restart lines,
evidence keys, the detached walk and the prepare-release operations.

### Step 4 improvement expectations

- A grouped walk passes only the group's test files, judges 100% over the
  group's sources from a scope-owned data file, and leaves `a.ghog.outliers`
  untouched.
- Proof is valid only for the exact scope, fingerprint and digest; a timing
  change caps it at `cov`.
- The two Step 4 gates pass without `xfail`; no gate remains `xfail`.

### What was implemented for Step 4

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 4

_(empty — no check has taken place yet.)_.

### Architecture check for Step 4

_(empty — no check has taken place yet.)_.

### Performance check for Step 4

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 4

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 4

_(empty — no check has taken place yet.)_.

---

## Step 5. Read the effort scope and print it through pw

### Analysis of Step 5 implementation state

Not started. Step 5 is not implemented because Step 4 has not landed yet.

No effort-scope reader, `pw scope` command or `scope` progress line exists
yet.

### Goal for Step 5

Add `tools/effort_scope.py`, `pw scope [ghog arguments]` and the `scope` line
of `pw progress`, reading only the requirement's `- Test group:` line.

### Step 5 improvement expectations

- `pw scope day` prints the completed command with `--group=<name>` or
  `--whole-suite`, whatever `GHOG_GROUP` holds.
- An invalid or duplicated group line is an error naming the requirement and
  the cause, never a fallback; the draft is never read.
- `pw progress` shows the scope and its source.

### What was implemented for Step 5

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 5

_(empty — no check has taken place yet.)_.

### Architecture check for Step 5

_(empty — no check has taken place yet.)_.

### Performance check for Step 5

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 5

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 5

_(empty — no check has taken place yet.)_.

---

## Step 6. Validate requests in the effort scope and bind the round scope

### Analysis of Step 6 implementation state

Not started. Step 6 is not implemented because Step 5 has not landed yet.

The renderer still renders the default without a selector and the exchange
keeps no scope for a published round.

### Goal for Step 6

Complete the requestor's default validation with the effort scope, render the
scope evidence, the migration notice, the group statement and the scope-change
block, bind each published code round to a core-owned capture that follows the
coordination record through every removal or archival, and ship the minimum
requestor and reviewer invocation instructions with the new required
arguments.

### Step 6 improvement expectations

- The project default renders as `ghog day --full=speed` plus the effort
  selector; declared sets stay unchanged and never claim a group proof they do
  not establish.
- `test_scope` proof comes from `snapshot.effective_proof`, the walk's own
  rule: a timing-only change shows at most `cov` until a new `speed` walk,
  for the whole suite and for a group.
- `publish-request --scope-capture-file` validates and copies the capture to
  `paths.scope`; `status` reports `bound_scope`, or `missing` for a legacy
  request; `complete`, `complete --force` and `resolve` remove the capture,
  `archive` archives it.
- The requestor, review-requestor, reviewer and implementation-check
  instructions name the new arguments and the `--scope-file=<paths.scope>`
  evidence; every renderer caller test passes the required output; a
  round-trip test renders, publishes and consumes the bound scope.
- A replacement whose scope changed requires `--scope-change-file`;
  `pw progress` shows the `bound` line and any `pending change`;
  `code_review_request.py` ends at or below 590 lines.

### What was implemented for Step 6

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 6

_(empty — no check has taken place yet.)_.

### Architecture check for Step 6

_(empty — no check has taken place yet.)_.

### Performance check for Step 6

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 6

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 6

_(empty — no check has taken place yet.)_.

---

## Step 7. Update the workflow instructions, templates and groundhog manuals

### Analysis of Step 7 implementation state

Not started. Step 7 is not implemented because Step 6 has not landed yet.

The instructions still describe one walk objective and no scope.

### Goal for Step 7

Apply the rest of the design's workflow instruction list on top of Step 6's
invocation contracts: development walks through `pw scope day`, the review-off
`speed` pass, the groundhog loop by level and scope, the requestor's `speed`
validation policy, the prepare-release gate at `cov` on the whole suite, the
scope menu of process-draft and write-requirement, and the groundhog manuals
and specification.

### Step 7 improvement expectations

- Each instruction names the command, level and scope the design gives its
  phase; adapters remain redirects.
- Pinned instruction tests follow the new wording; new contracts live in their
  own package; `groundhog.md` keeps exactly two `.\senv.bat &&` calls.
- Every edited Markdown file passes markdownlint.

### What was implemented for Step 7

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 7

_(empty — no check has taken place yet.)_.

### Architecture check for Step 7

_(empty — no check has taken place yet.)_.

### Performance check for Step 7

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 7

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 7

_(empty — no check has taken place yet.)_.

---

## Step 8. Prove every design acceptance case

### Analysis of Step 8 implementation state

Not started. Step 8 is not implemented because Step 7 has not landed yet.

The cross-component acceptance package and the row-to-test mapping do not
exist yet.

### Goal for Step 8

Add an acceptance package that drives groundhog, `pw`, the request renderer and
the review exchange together on `tmp_path` repositories, and map every design
acceptance row to its passing tests.

### Step 8 improvement expectations

- Review flows (captured scope after a same-name edit, refused capture, legacy
  request, replacement with and without a scope-change reason, migration
  notice, no false group claim) pass end to end.
- Workflow flows (`pw scope` precedence over `GHOG_GROUP`, stale draft,
  prepare-release on the whole suite, the review-off exclusion comparison)
  pass end to end.
- This section gains a table mapping every design acceptance row to its test
  node ids.

### What was implemented for Step 8

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 8

_(empty — no check has taken place yet.)_.

### Architecture check for Step 8

_(empty — no check has taken place yet.)_.

### Performance check for Step 8

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 8

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 8

_(empty — no check has taken place yet.)_.
