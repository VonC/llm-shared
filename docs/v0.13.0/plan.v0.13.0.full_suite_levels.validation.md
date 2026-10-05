# v0.13.0 full_suite_levels implementation tracking and validation

Yes, it is implemented.

This document tracks the nine steps of the
[implementation plan](plan.v0.13.0.full_suite_levels.md), from the Step 0 cost
gates to the Step 8 acceptance mapping. All nine steps are implemented,
including two sub-second acceptance journeys, the complete design mapping
and whole-suite lifecycle gates for every integration destination.

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

Yes. Step 4 has been fully implemented.

Run commands retain one scope through collection, coverage, duration judging,
proof, reporting and detachment. Group evidence is isolated; grouped timing
preserves shared settings. The final staged-source `ghog day --full=speed`
completed at 2026-10-03T15:53:20+02:00 with `proof=speed`, `reused=none`,
`scope=whole` and `exit=0`. Its full coverage step reported `fail=0 warn=0
xfail=0 cov=100 exit=0`; sequential timings reported `fail=0 warn=0 xfail=0
cov=skipped outliers=0 excluded=0 exit=0`. Freshness and `state=done` were
confirmed. The plan's explicit `ghog day --full=cov --whole-suite` also
passed by reusing this stronger proof.

Review repairs keep empty grouped affected runs green without changing saved
proof, avoid an extra whole-suite inventory scan, normalize new files to LF
and preserve original module titles. Both former suite warnings were SQLite
connections left open when corrupt coverage data failed to load. Closing the
data handle on every path removes them; the malformed-evidence regression
checks for resource warnings, and the final whole-suite run reports none.

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

- `scope.py`, `cli.py` and `context.py` resolve explicit selectors before
  `GHOG_GROUP`, default to whole-suite scope, reject conflicting selectors
  with setup exit 5, validate bound captures and retain a shared inventory.
  Explicit selection does not consult the environment default.
- `runner.py` narrows grouped affected, full and timing collection to the
  resolved test paths. Covered runs add the minimal source folders and
  disable pytest's aggregate coverage gate. Spawn environment overrides are
  restored in `finally`, including when the spawn factory raises.
- `group_coverage.py`, `commands.py` and `verdicts.py` use isolated coverage
  data, resetting it for full runs and appending for affected runs. Coverage's
  configured line/branch calculation judges exactly the resolved sources at
  100%, including never-executed sources and sources outside project defaults.
  Missing, stale, corrupt or incompatible evidence produces setup exit 5;
  malformed sources cannot be silently ignored. Failed, empty and crashed
  test runs retain their original verdicts. Coverage data is closed even
  when corrupt input fails while opening the database.
- `durations.py` and `durations_summary.py` judge grouped timing against the
  saved floor and group-local exclusions without writing shared settings.
  Existing floor and exclusion writes remain confined to the whole-suite
  branch.
- `day.py` and `evidence.py` use scope-specific markers, membership
  fingerprints and the shared inventory for proof. Membership, patterns and
  source changes invalidate the appropriate proof; timing changes cap proof
  at `cov`. A covered affected run records no full proof.
- `reporting.py`, `reporting_nextstep.py`, `status.py` and `detach.py` carry
  scope through evidence, repair commands, success/noop messages and lost-run
  recovery. Detachment writes a bound group capture atomically before spawn,
  or passes `--whole-suite` explicitly.
- Both prepare-release operations now end in
  `ghog day --full=cov --whole-suite`. Unit and CLI acceptance cases cover
  the new paths, and both Step 4 performance gates retain their timeouts with
  their `xfail` markers removed.

### New types or classes introduced for Step 4

- `ScopeError` represents scope-selection setup failures.
- `GroupCoverage` carries the full-precision percentage, gap rows and an
  evidence error from the coverage adapter.
- `Invocation` now carries the resolved scope and optional shared inventory;
  `StreamConfig` carries spawn-only environment overrides. These extend
  existing types rather than introduce competing execution models.
- Test support adds `CoverageSpawns`, a deterministic spawn factory that
  records commands and writes coverage evidence to the supplied data path.

### Architecture check for Step 4

The existing pure scope and proof models remain independent of process,
filesystem and coverage libraries. Scope resolution and coverage inspection
are adapters; command/day orchestration connects them to runner ports and
reporting. The floor-only duration calculation is pure, while reading and
persisting settings remain in the duration adapter. Shared inventory is
passed through the invocation rather than recovered by a hidden traversal.
No new reverse dependency, misplaced domain rule or duplicated proof model
was found.

No, there is nothing that needs to be addressed in the architecture.

### Performance check for Step 4

Declaration-based group selection requests one lazy inventory, shared with
the day proof. Whole-suite and captured scopes do not request it; day builds
its existing inventory when needed. Default and explicit whole-suite check
regressions forbid a scan, and the grouped-day cost gate requires exactly
one. Whole-suite full, affected and single commands retain their existing IO.

Coverage folder reduction uses linear radix ordering and a single reduction;
grouped duration ordering uses fixed-width float radix ordering. The new
paths introduce no quadratic or comparison-sort computation. Both active
performance gates pass, and the final sequential timing pass reports zero
outliers and zero exclusions.

Final production line counts are `scope.py` 81, `group_coverage.py` 104,
`context.py` 133, `cli.py` 553, `runner.py` 339, `commands.py` 559,
`verdicts.py` 154, `durations.py` 396, `durations_summary.py` 172, `day.py`
406, `evidence.py` 149, `reporting.py` 514, `reporting_nextstep.py` 597,
`status.py` 401, `detach.py` 201 and `__init__.py` 73. The release workflow
is 442 lines. New test/support files are at most 180 lines; modified legacy
test files are at most 510. All remain below the 650-line ceiling.
`cli.py`, `commands.py` and `reporting_nextstep.py` fall within the
550-650 advisory risk band; further growth belongs in focused collaborators.
The detached adapter keeps `status.py` below its 550-line extraction trigger.
The staged byte audit finds no mixed line endings and confirms all ten
original module summary lines are preserved.

No, there is no performance issue that needs to be addressed.

### Unit test coverage check for Step 4

The configured coverage source is `tools`, with a 100% gate. Tests,
`__init__.py`, ports/protocols and the configuration's named thin adapters
are omitted. All changed production behavior is inside the measured scope;
the changed package initializer contains documentation only. The existing
green walk provides `cov=100` evidence for that scope. This implementation
check did not run tests.

Static inspection connects `scope.py` to its dedicated TDD package and
`group_coverage.py` to its dedicated TDD/PBT package. Those cases cover
selection precedence, invalid environment values, capture validation,
minimal folder reduction, configured coverage and relative paths, branch
gaps, never-executed sources, strict source errors and evidence failures.
The folder-reduction PBT checks coverage and non-nesting properties.

Existing runner, duration, detach, command, reporting and release unit tests
cover their respective extensions, including all four environment-restoration
combinations and the unchanged whole-suite behavior. The group acceptance
package exercises orchestration, failure precedence, proof isolation,
invalidation, saved-floor timing, readonly exclusions and captured membership
through `cli.main`. These cross-module acceptance cases are assessed for
their behavior rather than assigned a separate per-file unit coverage target.
Boundary cases also exercise unknown CLI options, missing duration rows and
direct invocations without a prebuilt inventory.

No, there is no unit-tested class below 100% that needs completing.

### Feature integrity for Step 4

Whole-suite collection, coverage judging, duration persistence and inventory
cost retain their existing behavior. Explicit whole-suite restart and release
commands remain stable even when `GHOG_GROUP` names another scope. Unknown
options retain argparse's usage-error behavior. Single-file runs preserve
their explicit test paths, and the check phase remains project-wide.

Grouped runs isolate coverage files and proof, retain prior proof on unusable
coverage evidence, and leave shared floor/exclusion data unchanged. A covered
affected run with no selected test and an unrelated project `TOTAL 50%`
returns exit 0 and preserves the saved group marker byte-for-byte. Captures
retain bound membership after declaration edits and reject deleted or altered
members without falling back. Reporting carries scope in normal and recovery
paths. No existing feature or reporting loss was found.

The real whole-suite speed walk proves coverage and sequential durations.
Grouped timing and detachment use deterministic test doubles for their
boundary cases. This Step 4 result does not complete the later workflow and
documentation steps.

---

## Step 5. Read the effort scope and print it through pw

### Analysis of Step 5 implementation state

Yes. Step 5 has been fully implemented.

The shared reader resolves requirement metadata, `pw scope` prints the
explicit selector or completed ghog command, and `pw progress` shows the
scope and its source. The fresh `ghog day --full=cov --whole-suite` walk
passed with `fail=0 warn=0 xfail=0 cov=100 exit=0`, and `ghog status`
confirmed `state=done proof=cov scope=whole`. The local launcher prints
`ghog day --full=cov --whole-suite` for this effort. A following
`ghog day --full=speed --whole-suite` added the timing pass at
2026-10-03T23:26:46+02:00 with `outliers=0 excluded=0 proof=speed`. The
project default `ghog day --full=speed` then reused that whole-suite speed
proof on unchanged sources at 23:31:30.

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

- `tools/effort_scope.py` reads only metadata before the first level-two heading
  from the selected requirement. Missing requirements and absent metadata
  return whole-suite scope with distinct reasons. Explicit whole-suite
  metadata avoids a project inventory; named groups use the existing group
  resolver over one `snapshot.source_files` inventory.
- Empty or duplicate metadata, unreadable requirements and invalid or empty
  groups raise `EffortScopeError` naming the requirement and cause. The
  reader never consults draft metadata or `GHOG_GROUP`.
- `tools/prompt_workflow_scope.py` resolves the current topic and workflow
  state, prints an explicit selector or a command retaining the caller's
  ghog arguments, and refuses existing selectors in equals or separated
  forms. Invalid scope exits 2; an unresolved topic exits 3. Command
  rendering preserves arguments containing spaces.
- The parser accepts the `scope` subcommand and remaining ghog arguments;
  the main report dispatcher calls it. Progress appends the scope after the
  step and optional journal, or after the phase without a step. Invalid
  declarations appear as errors without a fallback or a proof claim.
- `instructions/run-pw.md` documents the command forms and progress row.
  Dedicated reader and workflow test packages cover the new behavior,
  including activation after step 2, switching and removal. Existing parser
  tests cover the command forms and root option. Two legacy progress
  expectations were updated for the added row; new progress cases stay in
  the new scope package, as the plan's split guidance intends.

### New types or classes introduced for Step 5

`EffortScope` is an immutable dataclass carrying the existing `ResolvedScope`,
the source requirement path and a display reason. `EffortScopeError` is the
reader's validation error, translated into command diagnostics or a progress
row by the workflow adapter. No additional scope model or matching policy
was introduced.

### Architecture check for Step 5

The reader owns requirement IO and delegates group rules to groundhog's
existing resolver. The workflow adapter owns topic selection, command output
and progress rendering. Parser and dispatch changes stay at the CLI
boundary; domain scope models do not import workflow presentation. No
DDD-Hexagonal layer violation or duplicated scope policy was found.

No, there is nothing that needs to be addressed.

### Performance check for Step 5

Header parsing stops at the first level-two heading. Whole-suite selection
does not scan the project. Group selection obtains one inventory and reuses
the established group resolver; a unit test asserts that single inventory
call. Selector rejection and command construction are linear in the input
arguments. No new quadratic or comparison-sort computation was introduced.

Final production line counts are `effort_scope.py` 92,
`prompt_workflow_scope.py` 69, `prompt_workflow.py` 545,
`prompt_workflow_parser.py` 190 and `prompt_workflow_progress.py` 492.
The new reader and workflow test modules are 143 and 178 lines, their package
markers one line each, parser tests 143 and existing progress tests 505.
Every changed Python file remains below the 650-line ceiling.

No, there is no performance issue that needs to be addressed.

### Unit test coverage check for Step 5

The configured coverage source is `tools`, with a 100% gate; tests,
`__init__.py`, protocols and named thin adapters are omitted. All five
changed production modules are measured. The writer's completed walk and
read-only coverage report show 100% for each, totaling 523 statements and
zero misses. This implementation check did not run tests.

Static inspection connects the reader to its dedicated TDD package covering
all source forms, fingerprint and provenance, duplicate and empty metadata,
unknown and empty groups, unreadable files, header termination and inventory
cost. The workflow package covers command output, caller-selector rejection,
resolution failures, scope changes, ambient-group independence and progress
ordering with and without a journal. Existing main, parser and progress
unit tests continue covering their respective modules. Every new top-level
production symbol is exercised or called by these adapters.

The finite metadata cases use parameterization. No additional PBT is needed
for this step: pattern matching and fingerprint properties remain covered by
the group resolver's earlier tests.

No, there is no unit-tested class below 100% that needs completing.

### Feature integrity for Step 5

Existing workflow routing and progress fields are retained, including the
umbrella-specific report. Requirement changes take effect on the next scope
command without changing group declarations; stale draft metadata and
ambient group selection cannot override the explicit selector. Invalid
metadata prints no runnable command. Tests and the full coverage walk show
no loss of existing features or reporting. Round-bound review scope remains
the separately planned Step 6 work.

---

## Step 6. Validate requests in the effort scope and bind the round scope

### Analysis of Step 6 implementation state

Yes. Step 6 has been fully implemented.

Requests now resolve the effort scope, preserve declared validation commands,
render exact-scope proof, and require disclosure of changed replacement scopes.
Publication validates and binds a capture to the round; status, reviewer
collection, progress and every coordination cleanup use that capture. The
required whole-suite coverage walk passed on 2026-10-04 with `exit=0`.

The renderer's transcript summary now renders validation commands as literal
Markdown code spans, using a fence longer than any embedded backtick run.
Six regression cases preserve angle brackets, dunder paths and boundary
backticks without changing the JSON command strings. The human-authorized
one-line transcript correction is applied, and fresh full validation passes.

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

- Extracted the renderer's four file helpers to `code_review_request_files.py`
  and added `code_review_request_scope.py` for workflow-based requirement
  lookup, `snapshot.effective_proof`, previous-round scope and change reasons.
- Added declared/default provenance in `code_review_validation.py`. Only the
  built-in default receives the effort selector. Declared walks retain their
  literal commands, receive the qualified migration notice when appropriate,
  and claim a grouped speed walk only with the explicit matching selector.
- Added required `--scope-capture-output`, optional `--scope-change-file`,
  `test_scope` in the envelope and evidence, and paired request/transcript
  scope sections. Invalid groups and unsupported plan layouts fail explicitly.
- Added `review_exchange_scope.py` to validate publication input, atomically
  write `paths.scope`, validate bound status, and remove or archive the capture.
  Publication rejects incomplete, mismatched or missing captures before any
  publication mutation and records the fingerprint inside the transition lock.
- Added the request-only CLI input and optional core port argument. Status
  reports `bound_scope` and exposes `paths.scope` only for valid bound evidence;
  legacy publications clear old captures and report missing evidence.
- Wired capture retirement into completion, forced completion and escalation
  resolution, and capture archival into archive resolution. The capture is
  retired before coordination, preserving retry context on cleanup failure.
- Added current/bound scope comparison to progress, including same-name group
  definition changes and damaged-coordination reporting.
- Updated the four minimum instruction contracts and the request template.
  Reviewers consume `ghog affected --no-cov --scope-file=<paths.scope>` and
  treat missing, legacy or refused captures as missing evidence.
- Added tests for proof invalidation and recovery, capture lifecycle, legacy
  behavior, model strictness, command provenance, instruction contracts and a
  renderer/publish/status/frozen-affected/replacement round trip. Extended the
  registry PBT for the new capture kind and adapted existing renderer fixtures.

Plan variances are limited to test support: the CLI fake core must accept and
record the new optional capture argument, so its existing test file changed
despite the plan's freeze guidance. It remains at 647 lines; new boundary cases
live in the boundary module. Renderer tests now import extracted helpers and
use supported `docs/` plan layouts. The store test excludes the new JSON
archive kind from its Markdown-only parameterization; scope archival has its
own tests. The production store and both status modules remain unchanged.

The pre-review speed run exposed a ten-second Git setup timeout in the
reviewer acceptance fixture. Its bounded timeout is now thirty seconds;
real-Git behavior, assertions and the separate duration gate are unchanged.
The request template has a local MD041 directive at its end because the
renderer supplies the document title and the authored first heading must
remain unchanged. Focused renderer and reviewer acceptance tests pass.

The pre-review speed gate also flagged the new round-trip call at 1.00s.
Pyinstrument identified repeated Windows path resolution as its largest
filesystem cost. A fixture used by that test alone caches actual resolutions
of stable, symlink-free paths. Every assertion, capture read and core
transition remains real; the isolated call now measures 0.75s and its focused
test file passes. The fresh whole-suite timing pass measured it at 0.80s,
with zero duration outliers.

### New types or classes introduced for Step 6

`ProjectValidation` carries commands and their declared/default provenance.
Existing round input and evidence types, `Envelope`, `CoordinationRecord` and
`ArtifactPaths` gain optional scope metadata or the capture path. `ArchiveKind`
and `RegisteredArtifactKind` gain scope variants. The three new modules contain
functions and introduce no parallel scope or proof model.

### Architecture check for Step 6

Workflow selection remains in the request/progress adapters; proof validity
remains in `snapshot.effective_proof`; capture validity remains in
`scope_capture.validate_capture`. Exchange filesystem work is isolated in the
scope helper and invoked by the existing locked publication and human
transitions. Models validate data without importing workflow or filesystem
adapters. No DDD-Hexagonal layer violation was found.

Post-change physical line counts satisfy the mandatory limits:

| Files | Lines |
| --- | --- |
| `code_review_request.py` | 578 (mandatory target 590) |
| `code_review_request_files.py`, `code_review_request_scope.py`, `review_exchange_scope.py` | 82, 78, 76 |
| `code_review_validation.py`, `prompt_workflow_scope.py` | 235, 93 |
| `review_exchange_models.py`, `review_exchange_models_coordination.py`, `review_exchange_models_envelope.py` | 564, 311, 268 |
| `review_exchange_cli.py`, `review_exchange_cli_ownership.py`, `review_exchange_cli_parser.py` | 523, 193, 161 |
| `review_exchange_human.py`, `review_exchange_publication.py` | 489, 413 |
| `review_artifact_registry.py`, `review_exchange_paths.py`, `tools/__init__.py` | 308, 230, 94 |
| Renderer tests, commit-plan tests, IO acceptance tests | 605, 254, 301 |
| New request-scope tests, exchange-scope tests, model-scope tests | 411, 207, 76 |
| CLI tests, CLI boundary tests, paths tests, store tests | 647, 457, 425, 456 |
| Progress scope tests, validation tests | 234, 212 |
| Registry tests and PBT | 138, 53 |
| Reviewer acceptance fixture helpers | 295 |
| Requestor, shared-requestor, reviewer and implementation-check instruction tests | 240, 91, 248, 105 |
| Commit-plan acceptance contracts, each new test-package initializer | 280, 1 |

Advisory estimate differences require no split; every changed Python file is
at or below 650 lines.

The two round 1 maintainability findings are resolved:

- `code_review_request_scope.resolve_request_scope` receives the renderer's
  validated `context.identity` and builds the `Topic` from its version and
  slug. `_PLAN_RE` remains the single plan-name parser. The request-scope test
  package passes, including unsupported layouts and the round trip.
- The staged
  `tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_contracts_tdd.py`
  now has 280 CRLF lines and no LF-only lines, preserving its HEAD convention.
  The scan of all 45 staged paths found no mixed line endings.

No, there is nothing that needs to be addressed in the architecture check.

### Performance check for Step 6

New command recognition and payload construction are linear in their input;
scope comparisons and the number of lifecycle artifacts are bounded. The
implementation reuses existing scope resolution and proof validation instead
of adding another membership scan or validity algorithm. No new quadratic or
sorting computation was introduced. New behavior tests use temporary files,
in-process calls and fake child execution; no new subprocess is added to their
round trips. This step changes no performance gate. The post-review whole-suite
`speed` walk establishes duration proof separately from the required `cov`
objective. No performance issue needs addressing.

### Unit test coverage check for Step 6

The configured coverage source is `tools` with `fail_under = 100`; it includes
every production Python file changed by this step. Tests and Markdown are not
production coverage targets. Existing unit packages cover renderer/file
helpers, validation, CLI/ownership/parser, models, paths, registry and progress.
The new request-scope and exchange-scope packages exercise their helpers and
the publication/human paths through the real core; the existing model package
contains the strict optional-scope tests. Registry round-trip PBT includes the
new kind. Additional PBT is unnecessary for the finite transition matrix.

Static review confirms coverage of declared/default commands, invalid input,
legacy records, proof changes from timing configuration or group definitions,
all capture exits, archive collisions and write failure. The final missing
branch, damaged coordination in progress, has a regression test preserving
current scope while reporting bound evidence as missing.

Pre-review requestor gate evidence after the test-support repairs:

```text
ghog day --full=speed --whole-suite
ghog full: fail=0 warn=0 xfail=0 cov=100 exit=0
ghog day: fail=0 warn=0 xfail=0 cov=skipped outliers=0 excluded=0 exit=0
full=speed src=param proof=speed reused=none scope=whole
timings ended=2026-10-04T03:02:00+02:00

ghog day --full=cov --whole-suite
fail=0 warn=0 xfail=0 cov=skipped outliers=skipped excluded=skipped exit=0
full=cov src=param proof=speed reused=all scope=whole
```

The speed walk completed successfully, including the whole-suite 100% coverage
pass and timing pass. The explicit plan command then reused that stronger
proof on unchanged sources. Static checks passed, including type checking,
lint, complexity and line limits; the separate mandatory Markdown gate also
passed. No unit-tested production module below 100% needed completing at that
point. Round 1 subsequently found three MD050 errors in the published
transcript and requested the identity/line-ending repairs above. The focused
request-scope tests pass after those repairs. The human authorized the exact
three-line transcript formatting correction; it is applied and the Markdown
gate passes.

Fresh round 2 validation after all repairs passed on 2026-10-04:

```text
ghog day --full=speed --whole-suite
ghog full: fail=0 warn=0 xfail=0 cov=100 exit=0
ghog day: fail=0 warn=0 xfail=0 cov=skipped outliers=0 excluded=0 exit=0
full=speed src=param proof=speed reused=none scope=whole
timings ended=2026-10-04T16:57:58+02:00

ghog day --full=cov --whole-suite
fail=0 warn=0 xfail=0 cov=skipped outliers=skipped excluded=skipped exit=0
full=cov src=param proof=speed reused=all scope=whole
```

Both logs passed the freshness check and `ghog status` confirmed completion.
The timing phase's `cov=skipped` does not replace the full phase's measured
100% coverage. The explicit coverage command reused the stronger speed proof
on unchanged sources. All seven plan additions, including the five completion
searches and the focused round-trip test, meet their criteria and are supplied
to the replacement review renderer without altering the project default.

Fresh round 3 validation after the command-formatting repair passed:

```text
ghog day --full=speed --whole-suite
ghog full: fail=0 warn=0 xfail=0 cov=100 exit=0
ghog day: fail=0 warn=0 xfail=0 cov=skipped outliers=0 excluded=0 exit=0
full=speed src=param proof=speed reused=none scope=whole
timings ended=2026-10-04T17:51:56+02:00

ghog day --full=cov --whole-suite
fail=0 warn=0 xfail=0 cov=skipped outliers=skipped excluded=skipped exit=0
full=cov src=param proof=speed reused=all scope=whole
```

Both logs passed the freshness check. The full phase measured 100% coverage;
the explicit coverage command reused that stronger speed proof on unchanged
sources. The round-trip call measured 0.78s against the 1.00s floor. Focused
renderer and scope tests pass, including the six command-formatting cases.
No unit-tested production module below 100% needs completing.

### Feature integrity for Step 6

Legacy envelopes and records round-trip without scope fields, while new code
requests carry strictly validated evidence. Direct renderer inputs retain
their optional defaults. Declared validation and plan/request additions remain
literal, and changed requirement/group data cannot silently alter a published
round's test collection. The round-trip test proves that the core-owned capture
still selects the original tests after a definition edit and ambient override.

Required inspections confirm extraction of the renderer's private file
helpers, a request-only capture parser option, cleanup in every required
transition, and all four instruction contracts. `git diff --check` passes.

Validation commands now remain literal in the transcript summary, including
`scope-file=<paths.scope>`, dunder paths and backtick runs. JSON retains the
exact original command strings. The repository Markdown checker rejects the
old summary preview with MD033 and accepts the corrected preview. Publication
preflight uses this checker as well as the mandatory npm Markdown gate.

Upgrade documentation follow-up for Step 7 or release notes: restart
long-running review processes after upgrading to the new scope artifact kind.
A watcher started with older code cannot classify the new capture file;
fresh processes using the current code recognize it.

---

## Step 7. Update the workflow instructions, templates and groundhog manuals

### Analysis of Step 7 implementation state

Yes. Step 7 has been fully implemented.

The workflow instructions, templates, provider adapters and manuals now name
the level and scope required by each phase. The whole-suite coverage walk
passed with `proof=cov`, `cov=100` and `exit=0` on 2026-10-05; all 22 edited
implementation Markdown files passed markdownlint. Step 8's acceptance
mapping remains separate work.

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

- Development instructions (`implement-step`, `implement-missing-step` and
  `split-large-file`) execute the command printed by `pw scope day`, describe
  check plus affected tests and the deliberate default full-stage skip, and
  preserve the printed repair and restart arguments.
- `implement-step` now orders the review-off speed pass after review-mode
  sampling and before the commit menu. It compares staged trees and saved
  exclusion listings, returns changed or unverified evidence through
  implementation-check and grouping, and records accepted exclusions in the
  journal, handoff and menu. `group-commits-msg` defers its menu accordingly.
- `write-plans` and its template resolve scope at execution time; the step
  handoff and journal record the actual gate command, selector and level.
- The groundhog loop states level and scope precedence, proof/status keys,
  parallel timing limits and exit 8 only at speed, retaining its lifecycle and
  freshness safeguards and exactly two `.\senv.bat &&` calls. The slow-test
  procedure restarts at speed in the same scope.
- The requestor instruction requires resolved validation before every
  publication, keeps declared commands authoritative, explains migration,
  records accepted exclusions and scope-change reasons, and discloses pending
  scope differences without starting a walk at a commit-ready answer.
- Every release gate now explicitly requires
  `ghog day --full=cov --whole-suite`. The four changed provider adapters
  retain metadata and a single canonical redirect body.
- `process-draft` places the scope menu after branch layout, validates new
  group sections and carries them to a new child worktree. `write-requirement`
  copies the draft choice only for new requirements and retains the existing
  requirement's authority. Both requirement template shapes include scope.
- `GROUNDHOG.md`, `DEVELOPMENT.md` and `tools/Pytest reset specs.md` cover
  levels, selection, proof reuse, grouped coverage and timing, scope changes,
  review migration and exclusion comparison. The specification adds Q71-Q79
  and AT20-AT28 while identifying superseded historical rules.
- A new instruction-contract test package pins these boundaries; requestor
  contracts cover the new policy while retaining role-isolation checks.

### New types or classes introduced for Step 7

None. This step changes Markdown instructions and tests only. The new test
module adds whitespace-normalizing `_read` and assertion helper `_contains`;
both are used by its collected policy tests. Its package includes `__init__.py`.

### Architecture check for Step 7

Runtime domain, application and infrastructure dependencies are unchanged.
Canonical instructions own workflow policy, and provider adapters point
directly to canonical files. The requestor retains its shared exchange
lifecycle and cannot initiate a reviewer.

| Python file | Before | After | Limit |
| --- | --- | --- | --- |
| New instruction-contract module | 0 | 138 | 650 |
| Requestor instruction-contract module | 240 | 254 | 650 |
| Existing instruction-structure module | 649 | 649, unchanged | 650 |

No architecture smell, violation or file-size issue needs to be addressed.

### Performance check for Step 7

No runtime computation or performance gate changed. Contract tests read
bounded documentation and perform whitespace normalization and fixed token
checks; their work is linear in the text size, with no new quadratic or
sorting algorithm. Property-based tests are unnecessary for these literal
policy contracts. The plan explicitly requires coverage, rather than a speed
gate, for this step's implementation proof.

No performance issue needs to be addressed.

### Unit test coverage check for Step 7

The recorded `ghog day --full=cov --whole-suite` walk finished on
2026-10-05 at 00:22:09 +02:00 with `fail=0`, `warn=0`, `xfail=0`, `cov=100`,
`proof=cov` and `exit=0`; `ghog status` confirmed `state=done`. Its check
phase also passed typing, lint, file-size and repository Markdown checks.
The initial Ruff failure on two literal counts was corrected with named
constants before the successful walk.

`pyproject.toml` measures `source = ["tools"]` and omits tests, package
initializers and the listed thin wrappers. This gate therefore establishes
100% for its configured runtime scope, not a percentage for Markdown or the
new test module. No runtime class was added or modified. Static inspection
shows every new test helper is referenced and all public `test_*` functions
are pytest collection entry points. Existing instruction-structure tests
remain unchanged and passed in the whole-suite walk.

No unit-tested class below 100% needs completing. No top-level symbol outside
the measured scope is unreferenced.

### Feature integrity for Step 7

All 25 implementation paths match Step 7's scope. Required searches found no
`full coverage pass` phrase under `instructions`, found every explicit release
coverage gate, and confirmed the requestor speed default and
`Rework and review again` label. Independent markdownlint on all 22 changed
implementation Markdown files reported `Summary: 0 issues in 0 files`.

Existing groundhog lifecycle, printed repair commands, review role isolation
and adapter responsibilities remain represented in the contracts. No runtime
feature or reporting capability was removed. The private journal retains
before/after line counts and the successful coverage log; the validation
plan records the durable verdict without claiming Step 8 is complete.

The first review found a stale `ghog day` restart in the "Check for files too
big" bullet of `instructions/split-large-file.md`. That bullet now follows
the printed restart command with its resolved level and scope, matching the
scope-preserving development flow above it. The requestor also completed
whole-suite speed validation with `proof=speed`, `outliers=0`, `excluded=0`
and `exit=0` at 00:45:17 +02:00 on 2026-10-05.

---

## Step 8. Prove every design acceptance case

### Analysis of Step 8 implementation state

Yes. Step 8 has been fully implemented.

Two compact journeys exercise the groundhog CLI, workflow resolver, request
renderer and review exchange on tiny isolated efforts. Their measured calls
are 0.33s and 0.23s, with 0.04s and 0.04s
setup. The fresh whole-suite speed walk ended at 2026-10-05T18:18:00+02:00 with 3,585 tests
passing, 100% coverage and no outlier or exclusion. The explicit whole-suite
coverage command reused the unchanged speed proof. All 95 design acceptance
rows map to collected tests. Every long-lived integration destination now
requires whole-suite validation before promotion or resumed topic handoff.

### Goal for Step 8

Prove the cross-component workflows, map every design acceptance case to
exact passing test node IDs, and close the release lifecycle bypasses for
main, generic integration and umbrella integration.

### Step 8 improvement expectations

- Published review scope remains bound to its captured members; replacements
  disclose scope changes and validate current proof before publication.
- Requirement scope overrides ambient selection. Every promotion candidate,
  on-main preparation and resumed integrated topic requires whole-suite cov.
- Valid whole-suite proof may be reused for unchanged sources; group proof
  cannot satisfy that gate. A different post-merge tree requires validation.
- Review-off comparisons distinguish added timing exclusions from automatic
  tightening. Every design row has executable evidence, with no remaining
  expected-failure marker in the active performance package.

### What was implemented for Step 8

The acceptance package contains
`tests/unit/tools/test_full_suite_levels_acceptance/__init__.py`,
`tests/unit/tools/test_full_suite_levels_acceptance/conftest.py`,
`tests/unit/tools/test_full_suite_levels_acceptance/test_full_suite_levels_review_acceptance_tdd.py`
and
`tests/unit/tools/test_full_suite_levels_acceptance/test_full_suite_levels_workflow_acceptance_tdd.py`.

Its fixture initializes real effort documents, group declarations, coverage
data and ignored review artifacts without launching Git. It isolates
`PRJ_DIR` and the working directory. Unrelated Git readiness, staged-tree
identity, activation and branch discovery use existing injected seams. The
release graph uses the existing in-memory Git protocol. Fixture-local path
resolution caching is restored by monkeypatch. Scope, proof, captures,
persistence and exclusion comparisons remain real. `CoverageSpawns` accepts
public `extra_lines` rather than requiring private transcript mutation.

The review journey earns grouped speed proof, renders the scoped default
command and publishes the capture. Same-name definition drift preserves the
captured affected files despite the ambient group; progress reports pending
change. The workflow journey resolves an ungrouped requirement against an
ambient group, distinguishes baseline tightening from added exclusions and
executes the printed whole-suite coverage gate. It also checks main
preparation and divergent topic and integration promotions.

`tools/prepare_release/prepare_release_plan_workflow.py` now gates on-main
preparation, direct topic promotion, current integration promotion and
already-integrated topic continuation. Existing replay and main-sync gates
remain; already-released topics remain a no-op. The canonical release
instruction requires the tested candidate tree for main, develop, configured
integration names and umbrella slugs. It checks post-merge tree equality and
requires a new gate when the tree differs. Requirement, design, plan and
provider metadata reflect that lifecycle contract.

`tests/unit/tools/test_prepare_release_whole_suite/__init__.py` and
`tests/unit/tools/test_prepare_release_whole_suite/test_prepare_release_whole_suite_tdd.py`
provide 12 topic cases across direct, replay and integrated routes, six
current/sync integration cases and one released-topic no-op. Existing planner
expectations and nine parametrized static instruction contracts are updated.
These fast synthetic cases supplement acceptance row 53.

The scope component test now initializes and validates its published
first-round baseline in a fixture. Every original assertion remains; the
call still verifies frozen membership, required scope-change disclosure and
replacement publication. Its package and module docstrings describe the
initialization. Two additional declaration parameters establish that plain
day and unscoped speed commands cannot claim group speed. Removed execution
journeys retain coverage through existing component tests in the mapping.

The performance-package docstrings describe its five active cost gates;
their assertions and timeout limits are unchanged. Its xfail search returns
no matches. No new PBT is needed for the concrete journeys and topology
cases; Steps 1, 3 and 4 cover the relevant level, group and proof properties.

### New types or classes introduced for Step 8

`Effort` is a test-only dataclass grouping the tiny project, document context,
artifact paths and public-entry helpers. No production type was added.

### Architecture check for Step 8

Release planning retains its existing repository port and model. The new
operation tuples add no technical import or layer dependency. Acceptance
orchestration belongs to the test adapter and uses public entry points and
the existing pytest process boundary. Every fixture helper is referenced.

Physical line counts are 458 for the planner, 425 for the scope component
test, 190 for the acceptance fixture, 72 and 71 for its two journeys, and
139 for the synthetic topology module. Every file is below 650 lines.

No architecture smell, violation or size issue needs addressing.

### Performance check for Step 8

The production correction adds constant-size operation tuples. It introduces
no quadratic computation, sorting process or extra repository traversal.
Existing default, upgrade, noop and grouped gates still check child counts
and tree-walk counts under their five-second timeouts.

The retained review and workflow calls measure 0.33s and
0.23s; setup measures 0.04s and 0.04s. The flagged
scope replacement call measures 0.48s, setup 0.33s, after
profiling publication I/O and initializing its validated baseline in the
fixture. All 19 synthetic topology calls are below one second. The full
speed verdict reports zero outliers and exclusions; no timing floor was
raised and no exclusion was accepted.

No, there is no performance issue that needs to be addressed in Step 8.

### Unit test coverage check for Step 8

The gate measures `tools` under `[tool.coverage.run]`, with
`fail_under = 100` and configured omissions. The speed walk's covered full
stage met `cov=100`; the explicit cov command reused its speed proof.
The amended release planner is inside that measured scope and has 100%
line coverage. Its existing and new synthetic unit cases exercise every
changed route. The acceptance, support and scope test files are outside the
measured source scope, so the gate percentage does not describe them.

Static exercise is complete: pytest collects every new test and fixture;
the fixture constructs `Effort` and every method and helper is referenced
by a journey or another package helper. The shared support constructor is
exercised by group tests and the two journeys. Both declaration parameters
and all lifecycle cases passed in the whole-suite walk. The mapping checker
verifies 95 ordered scenarios, nonempty mappings, private-evidence equality
and 102 exact collected selectors with existing source functions.

No unit-tested class below 100% needs completing. No top-level symbol outside
the configured coverage scope is unreferenced.

### Feature integrity for Step 8

The expanded whole-suite gate closes lifecycle bypasses while retaining
destination routing, replay, integration history and released-topic no-ops.
Tests assert public command output, gate ordering, proof, publication
artifacts, captured membership and exclusion comparisons. Grouped
development and review remain supported; group proof cannot waive promotion
validation. The fresh whole-suite speed walk ended at 2026-10-05T18:18:00+02:00 with:

```text
llm-shared_full_suite_levels: ghog day done fail=0 warn=0 xfail=0 cov=skipped outliers=0 excluded=0 exit=0 full=speed src=param proof=speed reused=none scope=whole
```

Its covered full stage reported `cov=100 exit=0`; the separate sequential
timing stage accounts for the closing `cov=skipped`. The explicit
`ghog day --full=cov --whole-suite` returned
`exit=0 proof=speed reused=all` on unchanged sources. No exclusion is accepted.
The performance-package xfail search returns no matches. Whole-suite
scope identity remains unchanged and independent of membership; changed
sources required fresh proof. All design rows have executable evidence.

### Design acceptance mapping for Step 8

Rows follow the order of the design's "Acceptance Cases for v0.13.0 full suite
levels" table. Instruction-only cases combine the Step 7 text contracts with
the tests for their called tools. Each listed node ID passed in the recorded
whole-suite speed walk; the mapping checker verifies the complete ordered
design table and each selector's collected ID and existing source function.

| Row | Design acceptance scenario | Passing test node IDs |
| --- | --- | --- |
| 1 | `ghog day`, `GHOG_FULL` unset, all green | `tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_levels_tdd.py::test_default_walk_skips_the_full_suite` |
| 2 | `GHOG_FULL=cov`, `ghog day` | `tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_levels_tdd.py::test_environment_level_walks_and_restarts_explicitly` |
| 3 | `GHOG_FULL=speed`, `ghog_cycle.bat` with no argument | `tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_levels_tdd.py::test_cycle_without_arguments_runs_day_alone`, `tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_levels_tdd.py::test_parallel_speed_walk_judges_the_timing_pass` |
| 4 | `GHOG_FULL=cov`, `ghog full --full=pass` | `tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_levels_tdd.py::test_parameter_wins_over_the_environment` |
| 5 | `GHOG_FULL=fast`, `ghog day` | `tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_levels_tdd.py::test_invalid_levels_exit_five_naming_the_values[argv0-environ0-'fast' from GHOG_FULL]` |
| 6 | `ghog day --full=fast` or `--full=none` | `tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_levels_tdd.py::test_invalid_levels_exit_five_naming_the_values[argv1-environ1-'fast' from --full]`, `tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_levels_tdd.py::test_invalid_levels_exit_five_naming_the_values[argv2-environ2-'none' from --full]` |
| 7 | `GHOG_FULL=fast`, `ghog day --full=cov` | `tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_levels_tdd.py::test_valid_parameter_overrides_an_invalid_variable` |
| 8 | `--full=pass`, a coverage gap and slow calls | `tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_levels_tdd.py::test_pass_level_judges_neither_coverage_nor_speed` |
| 9 | `--full=cov`, parallel project, green | `tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_levels_tdd.py::test_cov_level_in_a_parallel_project_runs_no_timing_pass` |
| 10 | `--full=speed`, parallel day walk, outlier in timings | `tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_levels_tdd.py::test_parallel_speed_walk_judges_the_timing_pass` |
| 11 | direct `ghog full`, parallel project, green | `tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_levels_tdd.py::test_direct_parallel_full_never_claims_speed` |
| 12 | direct `ghog full --full=pass`, test failure | `tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_levels_tdd.py::test_direct_pass_failure_is_unproven_and_carries_the_level` |
| 13 | `--full=cov` full fails, then `ghog single` green | `tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_levels_tdd.py::test_green_single_restarts_the_walk_at_the_carried_level` |
| 14 | `GHOG_FULL=speed`, check fails | `tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_levels_tdd.py::test_environment_speed_restarts_a_failing_check_explicitly` |
| 15 | default walk fails in the affected step | `tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_levels_tdd.py::test_failing_default_walk_restarts_plainly` |
| 16 | saved `speed`, unchanged sources, `ghog day` | `tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_proof_tdd.py::test_stronger_saved_proof_is_a_noop` |
| 17 | saved `none`, unchanged sources, `--full=cov` | `tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_proof_tdd.py::test_lower_saved_proof_is_upgraded` |
| 18 | saved `pass`, `--full=cov`, coverage gap | `tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_proof_tdd.py::test_higher_gate_failure_keeps_the_lower_proof` |
| 19 | saved `pass`, `--full=cov`, full test failure | `tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_proof_tdd.py::test_full_failure_caps_the_saved_proof` |
| 20 | parallel `--full=speed`, no marker, green full run, timing pass fails a test | `tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_proof_tdd.py::test_timing_pass_failure_caps_the_earned_proof` |
| 21 | parallel `--full=speed`, no marker, green full run, timing pass crashes | `tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_proof_tdd.py::test_timing_pass_crash_caps_the_earned_proof` |
| 22 | parallel `--force --full=speed`, saved `speed`, timing pass fails a test | `tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_proof_tdd.py::test_forced_timing_failure_caps_the_saved_proof` |
| 23 | parallel `--full=speed`, green full run, outliers only in timings | `tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_proof_tdd.py::test_timing_outliers_keep_the_cov_proof` |
| 24 | legacy one-line marker, unchanged sources, `ghog day` | `tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_proof_tdd.py::test_legacy_marker_is_no_proof` |
| 25 | `--detach --full=cov` | `tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_proof_tdd.py::test_detached_walk_keeps_its_level_and_evidence` |
| 26 | review mode on, default policy, round 1 | `tests/unit/tools/test_code_review_requestor_instruction/test_code_review_requestor_instruction_tdd.py::test_requestor_owns_the_full_validation_walk`, `tests/unit/tools/test_full_suite_levels_acceptance/test_full_suite_levels_review_acceptance_tdd.py::test_published_capture_survives_same_name_drift` |
| 27 | review mode on, replacement round, unchanged validated digest, readable marker recording `speed` for the same scope | `tests/unit/tools/test_code_review_requestor_instruction/test_code_review_requestor_instruction_tdd.py::test_requestor_owns_the_full_validation_walk`, `tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_proof_tdd.py::test_stronger_saved_proof_is_a_noop`, `tests/unit/tools/test_code_review_request_scope/test_code_review_request_scope_tdd.py::test_requirement_scope_and_current_proof` |
| 28 | review mode on, replacement round, marker unreadable, legacy, or proving only `cov` | `tests/unit/tools/test_code_review_requestor_instruction/test_code_review_requestor_instruction_tdd.py::test_requestor_owns_the_full_validation_walk`, `tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_proof_tdd.py::test_legacy_marker_is_no_proof`, `tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_proof_tdd.py::test_lower_saved_proof_is_upgraded`, `tests/unit/tools/test_groundhog_snapshot.py::test_unreadable_marker_means_no_proof` |
| 29 | review mode on, replacement round changed only a gate configuration file | `tests/unit/tools/test_code_review_requestor_instruction/test_code_review_requestor_instruction_tdd.py::test_requestor_owns_the_full_validation_walk`, `tests/unit/tools/test_groundhog_snapshot.py::test_digest_covers_the_gate_configuration` |
| 30 | review mode on, replacement round changed Python code | `tests/unit/tools/test_code_review_requestor_instruction/test_code_review_requestor_instruction_tdd.py::test_requestor_owns_the_full_validation_walk`, `tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_proof_tdd.py::test_python_change_invalidates_the_saved_proof` |
| 31 | requestor needs `ghog exclude` to reach `speed` | `tests/unit/tools/test_code_review_requestor_instruction/test_code_review_requestor_instruction_tdd.py::test_validation_policy_preserves_declared_commands_and_bound_scope`, `tests/unit/tools/test_code_review_request_scope/test_code_review_request_scope_tdd.py::test_rendered_proof_downgrades_and_recovers[exclusions---whole-suite]` |
| 32 | commit-ready answer | `tests/unit/tools/test_code_review_requestor_instruction/test_code_review_requestor_instruction_tdd.py::test_validation_policy_preserves_declared_commands_and_bound_scope`, `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py::test_substantive_commit_ready_stays_at_gate_for_human_override` |
| 33 | `.review-validation` declares plain `ghog day` | `tests/unit/tools/test_code_review_request_scope/test_code_review_request_scope_tdd.py::test_default_scope_and_declared_commands` |
| 34 | review mode off, `speed` pass changes nothing | `tests/unit/tools/test_full_suite_levels_instructions/test_full_suite_levels_instructions_tdd.py::test_review_off_compares_tree_and_exclusions_before_menu`, `tests/unit/tools/test_full_suite_levels_acceptance/test_full_suite_levels_workflow_acceptance_tdd.py::test_review_off_scope_comparison_and_release`, `tests/unit/tools/test_groundhog_listings/test_groundhog_listings_tdd.py::test_listing_and_semantic_comparison` |
| 35 | review mode off, `speed` pass changes a test or production file | `tests/unit/tools/test_full_suite_levels_instructions/test_full_suite_levels_instructions_tdd.py::test_review_off_compares_tree_and_exclusions_before_menu`, `tests/unit/tools/test_code_review_evidence/test_code_review_evidence_tdd.py::test_capture_index_tree_uses_the_index_without_inspecting_worktree`, `tests/unit/tools/test_code_review_evidence/test_code_review_evidence_boundaries_tdd.py::test_umbrella_and_validation_payload_failures_are_typed` |
| 36 | review mode off, `speed` pass needs only `ghog exclude` | `tests/unit/tools/test_full_suite_levels_instructions/test_full_suite_levels_instructions_tdd.py::test_review_off_compares_tree_and_exclusions_before_menu`, `tests/unit/tools/test_full_suite_levels_acceptance/test_full_suite_levels_workflow_acceptance_tdd.py::test_review_off_scope_comparison_and_release`, `tests/unit/tools/test_groundhog_listings/test_groundhog_listings_tdd.py::test_listing_and_semantic_comparison` |
| 37 | review mode off, pre-existing exclusions untouched, the walk only lowers a baseline or drops a stale entry and rewrites line 1 | `tests/unit/tools/test_full_suite_levels_instructions/test_full_suite_levels_instructions_tdd.py::test_review_off_compares_tree_and_exclusions_before_menu`, `tests/unit/tools/test_groundhog_listings/test_groundhog_listings_tdd.py::test_listing_and_semantic_comparison`, `tests/unit/tools/test_full_suite_levels_acceptance/test_full_suite_levels_workflow_acceptance_tdd.py::test_review_off_scope_comparison_and_release` |
| 38 | review mode off, second pass after an exclusion recheck | `tests/unit/tools/test_full_suite_levels_instructions/test_full_suite_levels_instructions_tdd.py::test_review_off_compares_tree_and_exclusions_before_menu`, `tests/unit/tools/test_full_suite_levels_acceptance/test_full_suite_levels_workflow_acceptance_tdd.py::test_review_off_scope_comparison_and_release`, `tests/unit/tools/test_groundhog_listings/test_groundhog_listings_tdd.py::test_listing_and_semantic_comparison` |
| 39 | review mode off, `--since` cannot read the saved or current listing | `tests/unit/tools/test_full_suite_levels_instructions/test_full_suite_levels_instructions_tdd.py::test_review_off_compares_tree_and_exclusions_before_menu`, `tests/unit/tools/test_groundhog_listings/test_groundhog_listings_tdd.py::test_unreadable_exclusion_file`, `tests/unit/tools/test_groundhog_listings/test_groundhog_listings_tdd.py::test_bad_saved_listing_is_unverified[None]`, `tests/unit/tools/test_groundhog_listings/test_groundhog_listings_tdd.py::test_bad_saved_listing_is_unverified[]`, `tests/unit/tools/test_groundhog_listings/test_groundhog_listings_tdd.py::test_bad_saved_listing_is_unverified[exclusions=unreadable\n]`, `tests/unit/tools/test_groundhog_listings/test_groundhog_listings_tdd.py::test_bad_saved_listing_is_unverified[junk\nexclusions=1\n]`, `tests/unit/tools/test_groundhog_listings/test_groundhog_listings_tdd.py::test_bad_saved_listing_is_unverified[node = 1\nexclusions=0\n]`, `tests/unit/tools/test_groundhog_listings/test_groundhog_listings_tdd.py::test_bad_saved_listing_is_unverified[node = 1\nnode = 2\nexclusions=2\n]` |
| 40 | `ghog exclude --list`, floor file absent or without a section | `tests/unit/tools/test_groundhog_listings/test_groundhog_listings_tdd.py::test_absent_exclusions_are_empty[1\n2\n]`, `tests/unit/tools/test_groundhog_listings/test_groundhog_listings_tdd.py::test_absent_exclusions_are_empty[None]` |
| 41 | commit-ready answer, declared set that establishes no `speed` | `tests/unit/tools/test_code_review_requestor_instruction/test_code_review_requestor_instruction_tdd.py::test_validation_policy_preserves_declared_commands_and_bound_scope`, `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py::test_substantive_commit_ready_stays_at_gate_for_human_override`, `tests/unit/tools/test_code_review_request_scope/test_code_review_request_scope_tdd.py::test_default_scope_and_declared_commands`, `tests/unit/tools/test_code_review_request_scope/test_code_review_request_scope_tdd.py::test_declared_group_statement[ghog day-False]` |
| 42 | `ghog day --full=cov --group=sentinel` | `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_walk_narrows_collection_and_names_scope` |
| 43 | group source file never executed by the group's tests | `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_group_gate_tdd.py::test_unexecuted_source_fails_hundred_percent_gate` |
| 44 | whole-suite `cov` proof on unchanged sources, then `--full=cov --group=sentinel` | `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_proof_isolated_by_scope` |
| 45 | saved `sentinel` proof, then `--full=cov --group=other` | `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_proof_isolated_by_scope` |
| 46 | `--group=nope`, or `.ghog-groups` unreadable with `--group=sentinel` | `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_bad_group_stops_before_spawn[malformed]`, `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_bad_group_stops_before_spawn[source]`, `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_bad_group_stops_before_spawn[test]`, `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_bad_group_stops_before_spawn[unknown]`, `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_bad_group_stops_before_spawn[unreadable]` |
| 47 | `.ghog-groups` unreadable, whole-suite walk | `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_whole_ignores_invalid_environment_and_declaration` |
| 48 | group whose test patterns match no test file | `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_bad_group_stops_before_spawn[malformed]`, `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_bad_group_stops_before_spawn[source]`, `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_bad_group_stops_before_spawn[test]`, `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_bad_group_stops_before_spawn[unknown]`, `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_bad_group_stops_before_spawn[unreadable]` |
| 49 | group whose source patterns match no source file | `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_bad_group_stops_before_spawn[malformed]`, `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_bad_group_stops_before_spawn[source]`, `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_bad_group_stops_before_spawn[test]`, `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_bad_group_stops_before_spawn[unknown]`, `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_bad_group_stops_before_spawn[unreadable]` |
| 50 | valid group, nothing affected, default walk | `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_nothing_affected_is_green_but_empty_full_is_error[day-extra0-0-none]`, `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_nothing_affected_is_green_but_empty_full_is_error[full-extra1-5-unproven]` |
| 51 | valid group whose test files hold no test, `--full=pass` | `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_nothing_affected_is_green_but_empty_full_is_error[day-extra0-0-none]`, `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_nothing_affected_is_green_but_empty_full_is_error[full-extra1-5-unproven]` |
| 52 | `GHOG_GROUP=nope`, `ghog day --whole-suite` | `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_whole_ignores_invalid_environment_and_declaration` |
| 53 | `GHOG_GROUP=sentinel`, prepare-release green gate | `tests/unit/tools/test_full_suite_levels_instructions/test_full_suite_levels_instructions_tdd.py::test_release_requires_coverage_of_whole_suite`, `tests/unit/tools/test_full_suite_levels_acceptance/test_full_suite_levels_workflow_acceptance_tdd.py::test_review_off_scope_comparison_and_release` |
| 54 | `GHOG_GROUP=sentinel`, ungrouped effort, development walk | `tests/unit/tools/test_full_suite_levels_acceptance/test_full_suite_levels_workflow_acceptance_tdd.py::test_review_off_scope_comparison_and_release`, `tests/unit/tools/test_prompt_workflow_scope/test_prompt_workflow_scope_tdd.py::test_cli_prints_explicit_scope_independent_of_environment[None-arguments1---whole-suite]` |
| 55 | grouped `--full=cov` walk fails a test | `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_failure_repair_carries_explicit_scope[--group=sentinel]`, `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_failure_repair_carries_explicit_scope[--whole-suite]`, `tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_levels_tdd.py::test_green_single_restarts_the_walk_at_the_carried_level` |
| 56 | whole-suite walk fails with `GHOG_GROUP=sentinel` set | `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_failure_repair_carries_explicit_scope[--group=sentinel]`, `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_failure_repair_carries_explicit_scope[--whole-suite]` |
| 57 | saved group proof, a test file added under the group folder | `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_group_edits_invalidate_proof[membership]`, `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_group_edits_invalidate_proof[pattern]` |
| 58 | saved group proof, the group's source patterns edited | `tests/unit/tools/test_code_review_request_scope/test_code_review_request_scope_tdd.py::test_definition_edit_invalidates_previously_saved_proof` |
| 59 | grouped `--full=speed`, a call above the floor | `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_grouped_speed_reads_floor_and_preserves_exclusions` |
| 60 | grouped `speed` walk, an exclusion recorded for a test outside the group | `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_grouped_speed_reads_floor_and_preserves_exclusions` |
| 61 | saved group `speed` proof, then `ghog exclude` adds an entry | `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_changed_exclusions_cap_group_speed_proof` |
| 62 | `--detach --group=sentinel` | `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_group_capture_tdd.py::test_detach_writes_capture_before_child_and_status_keeps_scope[--group=sentinel]`, `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_group_capture_tdd.py::test_detach_writes_capture_before_child_and_status_keeps_scope[--whole-suite]` |
| 63 | detached grouped walk running, requirement switched to another group | `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_group_capture_tdd.py::test_detach_writes_capture_before_child_and_status_keeps_scope[--group=sentinel]`, `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_group_capture_tdd.py::test_detach_writes_capture_before_child_and_status_keeps_scope[--whole-suite]`, `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_group_capture_tdd.py::test_capture_survives_changed_declaration` |
| 64 | reviewer evidence in a grouped round | `tests/unit/tools/test_full_suite_levels_acceptance/test_full_suite_levels_review_acceptance_tdd.py::test_published_capture_survives_same_name_drift` |
| 65 | grouped effort, default policy | `tests/unit/tools/test_full_suite_levels_acceptance/test_full_suite_levels_review_acceptance_tdd.py::test_published_capture_survives_same_name_drift` |
| 66 | grouped effort, `.review-validation` declares `ghog day --full=speed` | `tests/unit/tools/test_code_review_request_scope/test_code_review_request_scope_tdd.py::test_default_scope_and_declared_commands`, `tests/unit/tools/test_code_review_request_scope/test_code_review_request_scope_tdd.py::test_declared_group_statement[ghog day --full=speed-False]` |
| 67 | process-draft, existing valid group chosen | `tests/unit/tools/test_full_suite_levels_instructions/test_full_suite_levels_instructions_tdd.py::test_scope_menu_follows_branch_choice_and_handles_children`, `tests/unit/tools/test_groundhog_listings/test_groundhog_listings_tdd.py::test_groups_listing`, `tests/unit/tools/test_prompt_workflow_scope/test_prompt_workflow_scope_tdd.py::test_scope_changes_take_effect_after_step_two`, `tests/unit/tools/test_prompt_workflow_scope/test_prompt_workflow_scope_tdd.py::test_cli_prints_explicit_scope_independent_of_environment[sentinel-arguments0---group=sentinel]` |
| 68 | process-draft, new group | `tests/unit/tools/test_full_suite_levels_instructions/test_full_suite_levels_instructions_tdd.py::test_scope_menu_follows_branch_choice_and_handles_children`, `tests/unit/tools/test_groundhog_listings/test_groundhog_listings_tdd.py::test_groups_listing`, `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_bad_group_stops_before_spawn[malformed]`, `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_bad_group_stops_before_spawn[source]`, `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_bad_group_stops_before_spawn[test]`, `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_bad_group_stops_before_spawn[unknown]`, `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_bad_group_stops_before_spawn[unreadable]` |
| 69 | process-draft whole suite, then write-requirement | `tests/unit/tools/test_full_suite_levels_instructions/test_full_suite_levels_instructions_tdd.py::test_scope_menu_follows_branch_choice_and_handles_children`, `tests/unit/tools/test_prompt_workflow_scope/test_prompt_workflow_scope_tdd.py::test_cli_prints_explicit_scope_independent_of_environment[whole suite-arguments2-ghog day --whole-suite]` |
| 70 | write-requirement on a draft without the line | `tests/unit/tools/test_full_suite_levels_instructions/test_full_suite_levels_instructions_tdd.py::test_scope_menu_follows_branch_choice_and_handles_children`, `tests/unit/tools/test_prompt_workflow_scope/test_prompt_workflow_scope_tdd.py::test_no_requirement_prints_whole_suite` |
| 71 | requirement line added after step 2 | `tests/unit/tools/test_prompt_workflow_scope/test_prompt_workflow_scope_tdd.py::test_scope_changes_take_effect_after_step_two` |
| 72 | requirement switched to another group, or set to `whole suite` | `tests/unit/tools/test_prompt_workflow_scope/test_prompt_workflow_scope_tdd.py::test_scope_changes_take_effect_after_step_two` |
| 73 | draft still names `sentinel`, requirement line removed | `tests/unit/tools/test_prompt_workflow_scope/test_prompt_workflow_scope_tdd.py::test_cli_prints_explicit_scope_independent_of_environment[None-arguments1---whole-suite]` |
| 74 | deactivation of `sentinel` | `tests/unit/tools/test_prompt_workflow_scope/test_prompt_workflow_scope_tdd.py::test_scope_changes_take_effect_after_step_two`, `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_proof_isolated_by_scope` |
| 75 | same group name, patterns edited while a round is published | `tests/unit/tools/test_full_suite_levels_acceptance/test_full_suite_levels_review_acceptance_tdd.py::test_published_capture_survives_same_name_drift` |
| 76 | scope changed while a round is published | `tests/unit/tools/test_full_suite_levels_acceptance/test_full_suite_levels_review_acceptance_tdd.py::test_published_capture_survives_same_name_drift`, `tests/unit/tools/test_code_review_request_scope/test_code_review_request_scope_tdd.py::test_render_publish_status_affected_and_replacement` |
| 77 | replacement request rendered after a scope change without `--scope-change-file` | `tests/unit/tools/test_code_review_request_scope/test_code_review_request_scope_tdd.py::test_scope_change_requires_reason`, `tests/unit/tools/test_code_review_request_scope/test_code_review_request_scope_tdd.py::test_render_publish_status_affected_and_replacement` |
| 78 | commit-ready answer with a pending scope change | `tests/unit/tools/test_full_suite_levels_acceptance/test_full_suite_levels_review_acceptance_tdd.py::test_published_capture_survives_same_name_drift`, `tests/unit/tools/test_code_review_requestor_instruction/test_code_review_requestor_instruction_tdd.py::test_validation_policy_preserves_declared_commands_and_bound_scope`, `tests/unit/tools/test_code_review_request_scope/test_code_review_request_scope_tdd.py::test_render_publish_status_affected_and_replacement`, `tests/unit/tools/test_prompt_workflow_scope/test_prompt_workflow_scope_tdd.py::test_progress_reports_bound_and_pending_scope[definition]` |
| 79 | scope switched back to a group whose marker is still valid | `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py::test_proof_isolated_by_scope` |
| 80 | `pw progress`, grouped effort with an active round | `tests/unit/tools/test_full_suite_levels_acceptance/test_full_suite_levels_review_acceptance_tdd.py::test_published_capture_survives_same_name_drift`, `tests/unit/tools/test_prompt_workflow_scope/test_prompt_workflow_scope_tdd.py::test_progress_reports_bound_and_pending_scope[definition]`, `tests/unit/tools/test_prompt_workflow_scope/test_prompt_workflow_scope_tdd.py::test_progress_reports_bound_and_pending_scope[legacy]`, `tests/unit/tools/test_prompt_workflow_scope/test_prompt_workflow_scope_tdd.py::test_progress_reports_bound_and_pending_scope[missing]`, `tests/unit/tools/test_prompt_workflow_scope/test_prompt_workflow_scope_tdd.py::test_progress_reports_bound_and_pending_scope[none]`, `tests/unit/tools/test_prompt_workflow_scope/test_prompt_workflow_scope_tdd.py::test_progress_reports_bound_and_pending_scope[whole]` |
| 81 | `pw scope`, requirement naming an unknown group | `tests/unit/tools/test_prompt_workflow_scope/test_prompt_workflow_scope_tdd.py::test_bad_group_prints_only_a_diagnostic` |
| 82 | round published for `sentinel` with tests under `tests/old/**`, then the same group's patterns edited to `tests/new/**` before reviewer evidence | `tests/unit/tools/test_full_suite_levels_acceptance/test_full_suite_levels_review_acceptance_tdd.py::test_published_capture_survives_same_name_drift` |
| 83 | same, with a captured test file deleted before reviewer evidence | `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_group_capture_tdd.py::test_unusable_bound_scope_stops[deleted]` |
| 84 | capture edited after publication (fingerprint no longer matches its content) | `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_group_capture_tdd.py::test_unusable_bound_scope_stops[conflict]`, `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_group_capture_tdd.py::test_unusable_bound_scope_stops[deleted]`, `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_group_capture_tdd.py::test_unusable_bound_scope_stops[edited]` |
| 85 | live code-review request published without `test_scope` | `tests/unit/tools/test_code_review_requestor_instruction/test_code_review_requestor_instruction_tdd.py::test_validation_policy_preserves_declared_commands_and_bound_scope`, `tests/unit/tools/test_code_review_request_scope/test_code_review_request_scope_tdd.py::test_legacy_replacement_clears_scope`, `tests/unit/tools/test_prompt_workflow_scope/test_prompt_workflow_scope_tdd.py::test_progress_reports_bound_and_pending_scope[legacy]` |
| 86 | `--scope-file` together with `--group` or `--whole-suite` | `tests/unit/tools/test_groundhog_scope/test_groundhog_scope_tdd.py::test_conflicting_selectors[options1]`, `tests/unit/tools/test_groundhog_scope/test_groundhog_scope_tdd.py::test_conflicting_selectors[options2]` |
| 87 | detached grouped walk, `.ghog-groups` edited between launch and the child's start | `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_group_capture_tdd.py::test_detach_writes_capture_before_child_and_status_keeps_scope[--group=sentinel]`, `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_group_capture_tdd.py::test_detach_writes_capture_before_child_and_status_keeps_scope[--whole-suite]`, `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_group_capture_tdd.py::test_capture_survives_changed_declaration` |
| 88 | group source `lib/widget.py` outside the project's coverage `source`, fully exercised by the group's tests | `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_group_gate_tdd.py::test_external_source_and_omit` |
| 89 | same source never executed by the group's tests | `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_group_gate_tdd.py::test_external_source_and_omit`, `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_group_gate_tdd.py::test_unexecuted_source_fails_hundred_percent_gate` |
| 90 | group source pattern matching a file the project's `omit` excludes | `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_group_gate_tdd.py::test_external_source_and_omit` |
| 91 | grouped covered run whose data file is missing, unreadable or older than the run | `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_group_gate_tdd.py::test_bad_data_preserves_saved_proof[invalid]`, `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_group_gate_tdd.py::test_bad_data_preserves_saved_proof[missing]`, `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_group_gate_tdd.py::test_bad_data_preserves_saved_proof[stale]` |
| 92 | project measuring branches, group source with every line run but a branch missed | `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_group_gate_tdd.py::test_missed_branch_fails_group_gate` |
| 93 | saved `cov` proof, only line 2 of `a.ghog.outliers` or an exclusion changed, `--full=cov` | `tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_proof_tdd.py::test_timing_change_keeps_a_lower_saved_proof` |
| 94 | saved `speed` proof, only an exclusion changed, `--full=speed` | `tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_proof_tdd.py::test_timing_change_caps_a_saved_speed_proof`, `tests/unit/tools/test_code_review_request_scope/test_code_review_request_scope_tdd.py::test_rendered_proof_downgrades_and_recovers[exclusions---whole-suite]` |
| 95 | saved `speed` proof, a Python file changed, `--full=cov` | `tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_proof_tdd.py::test_python_change_invalidates_the_saved_proof` |
