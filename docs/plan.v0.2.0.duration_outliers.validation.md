# v0.2.0 duration-outliers implementation tracking and validation

Partially implemented: steps 1 to 4 are done, steps 5 to 6 remain.

This document tracks the duration-outliers feature (decisions Q34 to Q47 of
`design.v0.2.0.duration_outliers.md`) step by step against the repository state.
Steps 1 (per-call duration capture into `RunStats`), 2 (the pure true-outlier
rule in `durations.py`) and 3 (the two-line `a.ghog.outliers` floor file in
`floor.py`) are done, and step 4 (classification, progress output and report
wiring) is now done too: `EXIT_DURATION_OUTLIERS` (8) is wired through the run,
the `avg=`/`outliers=` output and the windowed report are emitted, and the auto
floor is persisted. Steps 5 (the skill exit-8 playbook) and 6 (acceptance tests)
remain.

---

## File-based IO cost clarification for the duration-outliers feature (implementation)

All implementation work must respect the IO classification from
`plan.v0.2.0.duration_outliers.md`:

- the durations come from the stream the parent already reads, not a second pytest
  or coverage invocation.
- `a.ghog.outliers` is a two-line read at run start, a tiny index-read.
- the floor write at run end uses the atomic side-file replace of `snapshot.py` and
  `status.py`.
- no directory scan is added on any path.

---

## Complexity bound clarification for the duration-outliers feature (implementation)

The scaling target for every reviewed step:

- **O(1) per streamed line**: the duration-line capture is a constant-cost branch.
- **O(n) to O(n log n) once per full run**: median, MAD and the outlier scan over
  the collected test count, one sort at most; no `O(n^2)` path.

Each implemented step is reviewed against this bound in its Performance check.

---

## Step 1. Capture per-call durations into RunStats

### Analysis of Step 1 implementation state

Yes. Step 1 has been fully implemented.

The full command now adds `--durations=0 --durations-min=0`, the parser captures the
`slowest durations` block into a new call-phase `RunStats.durations` map, and every
non-full run leaves the map empty. The capture opens on its banner and closes on the
next banner, the final summary line included; a parametrized id with spaces is kept
whole. The `ghog day` walk is green in one pass.

### Goal for Step 1

Add pytest's `--durations` output to the full command and parse the
`slowest durations` block into a new call-phase `RunStats.durations` map; non-full
runs stay empty.

### Step 1 improvement expectations

- after a full run, `RunStats.durations` maps each node id to its call seconds.
- the affected and single commands carry no `--durations` flags and produce no map.
- the durations-section capture stops at the next banner and at the final summary.

### What was implemented for Step 1

- **models.py field**: `RunStats` gains `durations: dict[str, float]`, default empty, node id to call-phase seconds; the class docstring records the call-phase-only intent and the empty-on-non-full-run rule (Q36, Q39).
- **runner.py flags**: `pytest_command` appends `--durations=0 --durations-min=0` on the full branch only, gated on `sub == SUB_FULL`; the single command returns early and the affected (covered) command skips the flags, so only the full run is timed (Q39).
- **parser.py capture**: a `_DURATION_RE` regex and a `_feed_durations` step record the call-phase seconds while a `slowest durations` banner is open; the node group is `.+\S`, so a parametrized id holding a space stays whole (Q49); any later banner — the final summary line, itself a banner, included — closes the capture.
- **Tests**: `test_groundhog_parser.py` adds four cases (call-phase-only with setup/teardown skipped and a post-banner line dropped, summary-line close, no-banner empty map, space-bearing parametrized id); `test_groundhog_runner.py` updates the full-command assertion with the two flags and adds a case proving the affected and single commands stay untimed.
- **Validation evidence**: `ghog day` reports `exit=0`, `state=done`, `cov=100`, `fail=0` over 728 tests; `rg "durations" tools/groundhog` finds the field (`models.py:81`), the flags (`runner.py:113`) and the capture (`parser.py:147`).

### New types or classes introduced for Step 1

- No new production class or type. Step 1 is a field, a parser step and a flag branch: `RunStats.durations` (a dataclass field), the `_DURATIONS_TITLE`, `_DURATION_RE` and `_CALL_PHASE` module-level constants of `parser.py`, the private method `PytestOutputParser._feed_durations`, and one `SUB_FULL` branch in `runner.pytest_command`. No new module was added — `durations.py` and `floor.py` belong to Steps 2 and 3.

### Architecture check for Step 1

- **parser layer (output adapter)**: the durations capture sits beside the existing failure-block and coverage-table captures inside `PytestOutputParser`, the streamed-output parsing adapter; it reads text only, writes to `RunStats`, and imports nothing new (`re` was already used). Correct placement.
- **models layer**: `RunStats` stays a plain counter dataclass with no behavior, its imports unchanged; the new field follows the `failed_ids`/`last_started` shape. No rule logic (median, MAD, floor) leaked in — that is held for the pure `durations.py` of Step 2.
- **runner layer**: `pytest_command` only builds an argument list; the `SUB_FULL` gate adds no IO and no computation, so the boundary between command building and the deferred rule module is kept.

No DDD-Hexagonal violation or adapter smell is visible in Step 1. No, there is nothing that needs to be addressed for Step 1.

### Performance check for Step 1

- **No new `O(n^2)` or `O(n log n)` path**: the capture is a constant-cost branch per streamed line — one banner match, at most one duration match, one dict insert — the same shape as the coverage-table capture next to it.
- **Hot-path bound**: `_feed_durations` runs once per output line, O(1) amortized; it never scans the accumulated map and never sorts.
- **Startup or background path**: none added; the flag wiring is a constant-time list build done once per run.
- **Plan-bound alignment**: Step 1 only captures; the `O(n log n)` median and MAD work is deferred to Step 2, so this step stays at O(1) per line.

Step 1 stays inside the plan's complexity target. No, there is no performance issue that needs to be addressed for Step 1.

### Unit test coverage check for Step 1

- **`tools/groundhog/parser.py` (`PytestOutputParser`)**: the new `_feed_durations` statements are all reached by the four added parser tests — the banner-open path, the banner-close path (named banner and summary line), the not-capturing early return, the call-phase insert, and the setup/teardown skip. Covered at 100%.
- **`tools/groundhog/runner.py` (`pytest_command`)**: the new `SUB_FULL` branch is reached by the updated full-command test; the not-full path by the affected and single tests. Covered at 100%.
- **`tools/groundhog/models.py` (`RunStats`)**: the `durations` default factory runs on every `RunStats()` construction the parser tests make. Covered at 100%.

No, there is no unit-tested class below 100% that needs completing for Step 1.

### Feature integrity for Step 1

- **Existing feature behavior**: the affected, single and check commands get no `--durations` flags, so their command lines and output parsing are unchanged; `RunStats.durations` defaults empty and nothing downstream reads it yet, so no route or workflow is impaired.
- **Reporting or diagnostics**: the progress lines, closing line, failure block and coverage capture are untouched; the full-run output gains pytest's own `slowest durations` block, captured silently into the map — no visible report yet, which is Step 4's job.
- **Compatibility or rollout note**: the full command appends the two flags after `-v`; the alias-faithful test was updated to match that order. No behavior change reaches the affected, single or check paths.

No existing feature or reporting capability appears impaired by Step 1.

---

## Step 2. The true-outlier rule, the average and the report window

### Analysis of Step 2 implementation state

Yes. Step 2 has been fully implemented.

A new pure `durations.py` carries the auto floor (`k * median`), the two-condition
true-outlier rule (modified z-score at least 3.5 AND at or above the floor), the
MAD-zero fallback to the floor alone, and the average over the non-outlier calls; a
companion `durations_report.py` renders the bounded report window. Both import only
the standard library -- no IO and no import from `commands`, `reporting`, `floor` or
even `models` -- so the rule is judged in isolation. Their deterministic tests reach
100% of each module and the `ghog day` walk is green in one pass.

### Goal for Step 2

A pure `durations.py` carrying the median, the MAD, the modified z-score, the
`k * median` floor, the two-condition true-outlier rule, the average excluding
outliers and the bounded window line builders, with the MAD-zero fallback.

### Step 2 improvement expectations

- a tidy suite yields zero outliers; one order-of-magnitude freak is the one
  outlier; a two-to-three-times call is not.
- the average excludes outliers; the MAD-zero case stays defined.
- the window holds the flagged outliers, the marked floor, and bounded runners-up.

### What was implemented for Step 2

- **durations.py rule module (new)**: the constants `K_DEFAULT` (10.0), `MODZ_CUTOFF` (3.5), `_MODZ_SCALE` (0.6745) and `_RUNNERS_UP_MAX` (3); `auto_floor(durations)` returns `k * median`, or `0.0` for an empty map; `summarize(durations, floor)` applies the two-condition rule, drops the z-condition when the MAD is zero so the floor alone decides (Q50), builds the uncapped outlier list slowest-first, up to three runners-up, and the average over the calls left unflagged (Q37).
- **durations_report.py window builder (new)**: `window_lines(summary)` renders the bounded report window (Q47) -- a header, the outlier lines, the marked floor, then up to three runners-up; a single slowest-call line on a green run; a no-durations notice on an empty map. The window text lives here, split out of `durations.py` so the rule stays under its line budget and kept out of `reporting.py` so that module keeps its own.
- **value objects**: two frozen dataclasses in `durations.py`, `DurationCall` (node, seconds, ratio) and `DurationSummary` (average, outliers, runners_up, floor, median); the ratio is guarded to `0.0` when the median is zero, so a zero-median run never divides by zero.
- **Tests**: `test_groundhog_durations.py` holds nine deterministic rule vectors (empty-map summary, tidy suite, one freak with a spared ~2.7x call, average-excludes-outliers, MAD-zero floor-only, median-zero ratio guard, empty-map auto floor, odd and even median) reaching 100% of `durations.py`; `test_groundhog_durations_report.py` holds the three window shapes reaching 100% of `durations_report.py`; `test_groundhog_durations_pbt.py` adds two bounded hypothesis properties (the auto floor scales with the durations; a call below the floor is never flagged), capped at 50 examples and a 400 ms deadline so the property run stays tiny.
- **Validation evidence**: `ghog day` reports `exit=0`, `state=done`, `cov=100`, `fail=0` over 728 tests; `rg "K_DEFAULT|MODZ_CUTOFF|def summarize|def auto_floor" tools/groundhog/durations.py` finds the constants and both functions; `durations.py` (177 lines) and `durations_report.py` (87 lines) carry no IO and no import from `commands`, `reporting` or `floor`.

### New types or classes introduced for Step 2

- `DurationCall`: a frozen dataclass for one timed call -- `node`, `seconds`, and `ratio` (the seconds as a multiple of the run median).
- `DurationSummary`: a frozen dataclass for the run verdict -- `average`, `outliers`, `runners_up`, `floor`, and `median`.
- `auto_floor`, `summarize`: the public functions of the rule in `durations.py`, with the private helpers `_is_outlier`, `_call` and `_median`.
- `window_lines`: the public window builder in `durations_report.py`, with the private helpers `_green_line`, `_call_line` and `_floor_line`.

Neither module adds a class with behavior beyond the two value objects; both are pure functions, matching the function-style placement of `gate.py`.

### Architecture check for Step 2

- **durations.py (pure domain rule)**: the module imports only the standard library (`dataclasses`, `typing`, and `collections.abc` under `TYPE_CHECKING`); it holds no IO and no import from `commands`, `reporting`, `floor`, `runner`, `parser` or even `models`, so the rule is decoupled from the parsing adapter and the IO modules. Correct placement beside `gate.py`, the other pure helper.
- **boundary direction**: the rule defines its own value objects (`DurationCall`, `DurationSummary`) instead of reaching into `RunStats`, so the adapter's accumulator does not leak into the rule and the rule does not depend back on the adapter; `commands.py` will call these modules in Step 4, never the reverse.
- **split note**: the first draft of `durations.py` reached 242 lines, over the step's 230 target, so the window rendering moved to a new `durations_report.py` (87 lines), per the plan's split guidance; `durations.py` is now 177 lines. `durations_report.py` imports only the `DurationCall`/`DurationSummary` value objects (under `TYPE_CHECKING`) from `durations.py`, a one-way report-over-rule dependency with no cycle, and stays out of `reporting.py` so that module keeps its own budget.

No DDD-Hexagonal violation or adapter smell is visible in Step 2. No, there is nothing that needs to be addressed for Step 2.

### Performance check for Step 2

- **No new `O(n^2)` path**: `summarize` sorts at most three times -- the median of the values, the median of the deviations (the MAD), and the runners-up -- and scans the calls once; `auto_floor` sorts once for its median. Each sort is `O(n log n)` over the collected test count, the outlier scan `O(n)`.
- **Hot-path bound**: none -- the rule runs once at end of run, not per streamed line, so it adds nothing to the live parsing path.
- **Startup or background path**: none added; the rule is computed once per full run, on data the parent already parsed, with no file or directory access.
- **Plan-bound alignment**: the work is `O(n) to O(n log n) once per full run`, the band the plan's complexity clarification allows; no path is `O(n^2)`.

Step 2 stays inside the plan's complexity target. No, there is no performance issue that needs to be addressed for Step 2.

### Unit test coverage check for Step 2

- **`tools/groundhog/durations.py`**: the deterministic `test_groundhog_durations.py` reaches every statement -- `auto_floor` empty and non-empty, `summarize` empty-map early return and the populated path, `_is_outlier` (below the floor, MAD-zero floor-only, and the modified z-score branch), `_call` for a positive and a zero median, and `_median` odd and even counts. Covered at 100%.
- **`tools/groundhog/durations_report.py`**: `test_groundhog_durations_report.py` reaches `window_lines` in all three shapes (outliers with the marked floor and runners, the single green line, the empty-map notice), so `_green_line`, `_call_line` and `_floor_line` are all hit. Covered at 100%.

The `ghog day` walk reports `cov=100`. No, there is no unit-tested class below 100% that needs completing for Step 2.

### Feature integrity for Step 2

- **Existing feature behavior**: `durations.py` and `durations_report.py` are new and not yet called by any command -- `commands.py` wires them in at Step 4 -- so no run, route or output changes; `RunStats`, `parser.py`, `runner.py`, `reporting.py` and `commands.py` are untouched.
- **Reporting or diagnostics**: the progress lines, closing line, failure block and coverage capture are unchanged; no `avg=` or `outliers=` is emitted yet, which is Step 4's job.
- **Compatibility or rollout note**: a pure addition with no caller, so no behavior reaches the full, affected, single or check paths; the rule is exercised only by its own tests.

No existing feature or reporting capability appears impaired by Step 2.

---

## Step 3. The two-line floor file

### Analysis of Step 3 implementation state

Yes. Step 3 has been fully implemented.

A new pure-IO `floor.py` beside `gate.py`, `snapshot.py` and `status.py` reads the
user override from line 2 of the two-line `a.ghog.outliers`, resolves the active
floor (the override when set, else this run's freshly computed auto -- line 1 is
write-only and never read for gating, Q48), and writes both lines through the atomic
side-file replace the tool already uses. A missing, partial, malformed or binary file
falls back to the auto floor without crashing. Nine deterministic tests reach 100% of
the module and the `ghog day` walk is green in one pass.

### Goal for Step 3

A `floor.py` beside `gate.py` and `snapshot.py` that reads the user override from
line 2 of the two-line `a.ghog.outliers`, resolves the active floor (the override
when set, else this run's freshly computed auto `k * median` -- line 1 is write-only
and never read for gating, Q48), and writes line 1 from the run with line 2 preserved
(`-1` when none), using the atomic side-file replace.

### Step 3 improvement expectations

- a missing file resolves to this run's auto value, with no override read.
- a positive line 2 is the active floor; line 1 is never read for gating (Q48).
- the write is atomic and round-trips; a malformed or partial file falls back to the
  auto value, never crashing the run.

### What was implemented for Step 3

- **floor.py file helper (new)**: the constants `FLOOR_FILE` (`a.ghog.outliers`), `NO_OVERRIDE` (`-1.0`) and `_LINE_COUNT` (2); `floor_path(root)` returns the project-root path; `read_floor(root)` reads only line 2 and returns the override seconds when it parses to a number `>= 0`, else `None` for a missing, unreadable, partial, malformed or `-1`/negative file (Q48); `active_floor(override, auto)` returns the override when set (`>= 0`), else this run's auto floor (Q48); `write_floor(root, auto, override)` writes line 1 = auto and line 2 = override atomically through a `.tmp` side-file replace, logging an `OSError` instead of raising so a write failure cannot crash the run.
- **line-1 write-only rule (Q48)**: `read_floor` never reads line 1, so each run gates against its own freshly computed `k * median` and the convergence of Q43 never lags a run behind; this is the plan's Q48 refinement of the design's earlier "else line 1" wording, which the pre-filled goal text above now reflects.
- **atomic write reuse**: the side-file replace mirrors `snapshot.py` (`a.ghog.day.ok`) and `status.py` (`a.ghog.status`); `_read_text` suppresses `OSError`/`UnicodeDecodeError`, so an absent or binary file reads as "no override".
- **.gitignore coverage**: `a.ghog.outliers` and its `.tmp` side file are already ignored by the existing `a.*` pattern (`git check-ignore` reports `.gitignore:27:a.*`), matching the `a.ghog.*` family; no `.gitignore` change was needed.
- **Tests**: `test_groundhog_floor.py` holds nine deterministic cases -- missing-file no-override, `-1` resolving to the fresh auto with the stale line 1 ignored, a positive override replacing the auto, the two-line atomic round-trip with no side file left behind, a partial one-line file, a non-numeric line 2, a binary file, a negative override resolving to auto, and a write onto a non-directory root logged not raised -- reaching 100% of `floor.py`.
- **Validation evidence**: the implement step's `ghog day` walk reported `exit=0`, `state=done`, `cov=100`, `fail=0` over 728 tests; `floor.py` is 130 lines (target <= 130) and `test_groundhog_floor.py` is 94 lines (target <= 150).

### New types or classes introduced for Step 3

- No new production class or type. Step 3 is a function-style file helper, matching `gate.py`: the module constants `FLOOR_FILE`, `NO_OVERRIDE` and `_LINE_COUNT`; the public functions `floor_path`, `read_floor`, `active_floor` and `write_floor`; and the private helper `_read_text`. No dataclass or behavior-bearing class was added.

### Architecture check for Step 3

- **floor.py (IO helper)**: the module sits beside `gate.py`, `snapshot.py` and `status.py`, the project-root file helpers; it imports only the standard library (`contextlib`, `logging`, `typing`, and `pathlib.Path` under `TYPE_CHECKING`) and nothing from `commands`, `reporting`, `durations`, `runner`, `parser` or `models`. Correct placement: file IO, no rule.
- **boundary direction**: the true-outlier rule stays in the pure `durations.py`; `floor.py` carries only the file's own contract -- read line 2, resolve override-else-auto, write two lines -- so no median, MAD or z-score logic leaked into the IO module and the IO module does not reach back into the rule. `commands.py` calls both in Step 4, never the reverse.
- **split or size note**: `floor.py` is 130 lines, on the plan's `<= 130` target; the module is small and self-contained, so no split is needed.

No DDD-Hexagonal violation or adapter smell is visible in Step 3. No, there is nothing that needs to be addressed for Step 3.

### Performance check for Step 3

- **No new `O(n^2)` or `O(n log n)` path**: `read_floor` parses a two-line file (one `splitlines`, one `float`) and `write_floor` writes two lines; both are O(1), with no scan and no sort.
- **Hot-path bound**: none -- the floor is read once at run start and written once at run end, off the streamed-line path, so the live parsing loop is untouched.
- **Startup or background path**: the run-start read is a tiny index-read of a two-line file and the run-end write a single side-file replace; no directory scan is added on any path, matching the plan's file-IO classification.
- **Plan-bound alignment**: the plan states the floor read and write are two-line operations, not scans; the implementation holds to that.

Step 3 stays inside the plan's complexity target. No, there is no performance issue that needs to be addressed for Step 3.

### Unit test coverage check for Step 3

- **`tools/groundhog/floor.py`**: `test_groundhog_floor.py` reaches every statement -- `floor_path` (used throughout), `read_floor` in all five outcomes (absent/unreadable text, a sub-two-line file, a non-numeric line 2, a `>= 0` override, and a negative override), `active_floor` in its three branches (`None`, a non-negative override, a negative override), `write_floor` on both the success and the `OSError` paths, and `_read_text` on the success, the suppressed-error and the `None`-fallthrough paths. Covered at 100%, consistent with the walk's `cov=100`.

No, there is no unit-tested class below 100% that needs completing for Step 3.

### Feature integrity for Step 3

- **Existing feature behavior**: `floor.py` is new and not yet called by any command -- `commands.py` wires it in at Step 4 -- so no run, route or output changes; `RunStats`, `parser.py`, `runner.py`, `reporting.py`, `commands.py`, `durations.py` and `durations_report.py` are untouched.
- **Reporting or diagnostics**: the progress lines, closing line, failure block and coverage capture are unchanged; no `avg=` or `outliers=` is emitted yet and no run writes the floor file yet, which is Step 4's job.
- **Compatibility or rollout note**: a pure addition with no caller and no `.gitignore` change (the `a.*` pattern already covers the new file); the helper is exercised only by its own tests, so no behavior reaches the full, affected, single or check paths.

No existing feature or reporting capability appears impaired by Step 3.

---

## Step 4. Classification, progress output and report wiring

### Analysis of Step 4 implementation state

Yes. Step 4 has been fully implemented.

`EXIT_DURATION_OUTLIERS` (8) exists and is exported; `run_tests` reads the
override, persists the auto floor and judges the call durations only on a run
already green on tests and coverage; `classify` returns exit 8 last; the final
progress line, the closed bar and the closing line carry `avg=`/`outliers=`; and
the windowed list with its fix step and floor-override hint is emitted. The
`ghog day` walk is green in one pass (`exit=0`, `state=done`, `cov=100`,
`fail=0` over 767 tests), and the feature reads correctly on llm-shared's own
uniformly-fast suite (`avg=0.008s outliers=0`).

### Goal for Step 4

Add the exit-8 code, compute the summary for full runs, classify exit 8 when green
and coverage-clear with outliers remaining, add `avg=`/`outliers=` to the final
line, the bar and the closing line, emit the windowed report on exit 8, and write
the auto floor after the run -- keeping `commands.py` under its budget.

### Step 4 improvement expectations

- a green-but-slow full run exits 8 with the windowed list and the fix instruction.
- a tidy run exits 0 with `outliers=0`; a raised override exits 0.
- a failing or coverage-gap run keeps its own exit code (outliers judged last).
- the final progress line and bar postfix carry `avg=` and `outliers=` for full.

### What was implemented for Step 4

- **exit code (models, `__init__`)**: `EXIT_DURATION_OUTLIERS = 8`, placed with the run-classification codes (0, 2, 3, 4, 5, 8), apart from the Q32 lifecycle codes (6, 7); `__init__.py` exports it. The module docstring records that it is judged last so it never masks a failure or a coverage gap (Q34).
- **classification (commands.classify)**: a new `outlier_count` argument; the run returns exit 8 only when it is not crashed, not failing, coverage-clear and `outlier_count > 0`, so outliers are judged after failures and coverage (Q34).
- **run wiring (commands.run_tests)**: the coverage gate is read before the bar closes; the base code is computed, the durations judged (`durations_summary.judge`), the progress finished with the verdict, the run re-classified with the outlier count, and the report given the verdict.
- **progress output (reporting, commands._Progress)**: `progress_line` gains an optional summary and the `avg=`/`outliers=` suffix (`progress_suffix`); `_Progress.finish` emits exactly one final LLM line for a full run (Q52) and the closed user bar carries the same verdict, `postfix` gaining the summary (Q37).
- **closing line (reporting)**: a `ClosingMetrics` value object carries `cov=` and `outliers=`; `outliers_text` reads `skipped`/`withheld`/the count, mirroring `cov_text`; the five `closing_line` callers pass `ClosingMetrics`.
- **report (commands._report_run_context, reporting.next_after_full)**: every green full run emits the bounded window (`durations_report.window_lines`) -- the flagged outliers, the marked floor and the runners-up, or a single green slowest-call line; exit 8 adds `MSG_OUTLIERS` and the floor-override hint (`_override_hint`).
- **floor persistence (durations_summary, new)**: a green full run reads the override, recomputes and writes the auto floor (line 1 a write-only record, Q48) and resolves the active floor; a failure, a gap or a crash forms no verdict and writes nothing, so the timing verdict is withheld.
- **tidy-suite fix (durations._is_outlier, cross-step)**: the Step 4 integration walk exposed that a uniformly-fast suite (every call rounding to `0.00s`, so the median and the `k * median` floor are zero) flagged every call; the rule now spares every call when the floor is non-positive, so a tidy suite is green from the start (Q41), as the design promises.
- **pre-existing lint unblock**: two committed Step 2 test files were failing the strict gate after toolchain drift -- `test_groundhog_durations.py` used `pytest.approx` (strict pyright `reportUnknownMemberType`) and `test_groundhog_durations_pbt.py` tripped ruff `TC002`; both were fixed minimally (`math.isclose` like the property test; `SearchStrategy` moved to a `TYPE_CHECKING` block) so the walk could reach the test steps.
- **tests**: `test_groundhog_reporting.py` adds the progress suffix, `outliers_text`, `ClosingMetrics`, the closing-line grammar, the exit-8 next step with its override hint, and the Q30 restart rule; `test_groundhog_commands.py` (new) drives `cli.main` over a durations transcript for the green-but-slow exit-8 run (window, fix, floor seeded), the tidy exit-0 run, the raised-override exit-0 run, the failing withheld exit-2 run, the user-bar verdict and the bar-less no-tests run, plus the `classify` precedence and `postfix` verdict directly; `test_groundhog_durations.py` adds the zero-floor spares-every-call case.
- **validation evidence**: `ghog day` reports `exit=0`, `state=done`, `cov=100`, `fail=0` over 767 tests; the final line reads `avg=0.008s outliers=0` and the closing line `cov=100 outliers=0 exit=0`; `rg "EXIT_DURATION_OUTLIERS|outliers=" tools/groundhog` finds the code and the output keys.

### New types or classes introduced for Step 4

- `reporting.ClosingMetrics`: a frozen value object carrying the `cov=` and `outliers=` values of the closing line, so `closing_line` stays within the project's five-argument limit (PLR0913); the `outliers` field defaults to `skipped`, so the simple callers (check, init, day-noop, setup-error) pass only the coverage value.
- `tools/groundhog/durations_summary.py` (new module): the application seam between a run and the pure rule -- `measures_durations` (a `full` run only, Q39), `judge` (the gating: a `full` run already green, judged last) and the private `_judge_map` (read the override, persist the auto floor, resolve the active floor, summarize). It carries no behavior-bearing class; it is function-style like `gate.py` and `floor.py`.
- No other production class. The rest of the step is functions and constants: `EXIT_DURATION_OUTLIERS`, `MSG_OUTLIERS`, `OUTLIERS_SKIPPED`/`OUTLIERS_WITHHELD`, `progress_suffix`, `outliers_text`, `_override_hint`.

### Architecture check for Step 4

- **layering**: `commands.py`, the orchestration root, calls `durations_summary` (composition), `durations_report` (rendering) and `reporting` (text). `durations_summary` composes the pure rule (`durations`) and the IO helper (`floor`); `durations.py` stays pure -- no IO, no `floor` import. The dependencies run one way (`durations_summary` imports `durations`, `floor`, `runner`, `models`; nothing but `commands` imports it back), so there is no cycle.
- **boundary direction**: the report keeps its value objects (`ClosingMetrics`, `DurationSummary`); `commands` passes them down and never the reverse. The tidy-suite fix sits in the pure rule (`durations._is_outlier`), the correct home, with no IO leaked in.
- **placement of the split**: per the plan's split guidance, the full-run post-processing (read floor, judge, persist floor) was extracted to `durations_summary.py` rather than left in `commands.py` or pushed into the pure `durations.py`, so the orchestration layer and the rule each keep their concern.
- **girth**: `commands.py` is 647 lines and `reporting.py` 513, both under the project's hard 650-line gate (`PYTHON_BIG_FILE_LINE_LIMIT=650`) but over the plan's soft targets (<= 545, <= 395). Those targets were set from pre-Q32 baselines (499, 325) that intervening lifecycle work had already overshot (596, 401) before Step 4 began, so the soft numbers are stale; the hard gate holds. The `commands.py` margin is only three lines.

Yes -- `commands.py` sits three lines under the 650-line gate, a girth watch a later step should relieve by splitting the report-assembly helpers out before the next addition; there is no DDD-Hexagonal violation or adapter smell.

### Performance check for Step 4

- **no new `O(n^2)` path**: the verdict is computed once per full run, reusing the Step 2 single sort (`O(n log n)` over the collected test count); the floor read and write are two-line `O(1)` operations, `classify` is `O(1)`, and the report builds bounded strings (the window is capped at the outliers plus three runners-up).
- **hot-path bound**: the live per-line path is unchanged -- the governor still emits during the run; the `avg=`/`outliers=` verdict is an end-of-run value (Q37), so the streamed-line loop adds nothing.
- **startup or background path**: none added; the floor file is read once at run start and written once at run end, no directory scan, matching the plan's file-IO classification.
- **plan-bound alignment**: the work stays in the `O(n) to O(n log n) once per full run` band the plan allows.

No, there is no performance issue that needs to be addressed for Step 4.

### Unit test coverage check for Step 4

- **`tools/groundhog/reporting.py`**: `progress_suffix`, `outliers_text` (skipped, withheld, count), `ClosingMetrics`, the closing-line `outliers=` key, and the `next_after_full` exit-8 branch with `_override_hint` are reached by `test_groundhog_reporting.py`; the live progress and closing paths by the acceptance and cli suites. Covered at 100%.
- **`tools/groundhog/commands.py`**: the `finish` LLM and user verdict branches, the `run_tests` judging, the `classify` exit-8 branch, the `_report` window and `ClosingMetrics` wiring, and the bar-less no-tests early return are reached by `test_groundhog_commands.py` and the existing acceptance and cli tests. Covered at 100%.
- **`tools/groundhog/durations_summary.py`**: `measures_durations`, `judge` and `_judge_map` -- every branch (not a full run, not green, an empty map, an override set and an override absent) -- are reached by the `test_groundhog_commands.py` integration runs, the same way the orchestration layer (`commands.py`) is covered. Covered at 100%.
- **`tools/groundhog/durations.py`**: the new non-positive-floor branch of `_is_outlier` is reached by the added `test_zero_floor_spares_every_call`; the other branches by the existing vectors. Covered at 100%.

The `ghog day` walk reports `cov=100`. No, there is no unit-tested class below 100% that needs completing for Step 4.

### Feature integrity for Step 4

- **existing feature behavior**: a full run with no durations block (the legacy acceptance transcripts) forms no verdict, so the bar postfix, the cadence count and the LLM lines are unchanged; the only new closing-line text is `outliers=skipped`. The affected, single and check runs read `outliers=skipped` and are otherwise untouched, and a covered affected run keeps `cov=` with no durations.
- **reporting or diagnostics**: the new keys sit beside the existing ones (`cov=` then `outliers=` then `exit=`); the failure block, crash block and coverage-gap rows are unchanged. Failures and coverage keep priority -- outliers are judged last -- so a red run withholds the timing verdict (`outliers=withheld`).
- **the day walk**: a green-but-slow full step now returns exit 8 and withholds the green snapshot, so the loop re-enters until the slow call is trimmed or the floor override raised, the intended driver; a tidy suite stays green (`outliers=0`, exit 0) and records its snapshot as before.

No existing feature or reporting capability appears impaired by Step 4.

---

## Step 5. The skill instruction exit-8 branch and LLM fix playbook

### Analysis of Step 5 implementation state

Not started. Step 5 is not implemented because `instructions/groundhog.md` has no
exit-8 branch and no outlier fix playbook.

### Goal for Step 5

Add an exit-8 branch and the LLM fix playbook to `instructions/groundhog.md`, beside
the exit-2 and exit-3 guidance: fix above-floor outliers only, the per-cause
techniques, the override escape, confirm with `ghog single`, restart with
`ghog day`.

### Step 5 improvement expectations

- on exit 8 the loop reads a concrete fix playbook scoped to above-floor calls.
- the runners-up shown for tuning are explicitly not fix targets.
- the override is named as the alternative for a legitimately slow call.

### What was implemented for Step 5

(empty -- to be filled after the step is implemented.)

### New types or classes introduced for Step 5

(empty.)

### Architecture check for Step 5

(empty.)

### Performance check for Step 5

(empty.)

### Unit test coverage check for Step 5

(empty.)

### Feature integrity for Step 5

(empty.)

---

## Step 6. Acceptance tests for the green-but-slow run

### Analysis of Step 6 implementation state

Not started. Step 6 is not implemented because there is no end-to-end acceptance
module driving `cli.main` over a transcript with a durations block.

### Goal for Step 6

A new `test_groundhog_acceptance_durations.py` exercising the green-but-slow run and
its variants through the real parser, rule, floor, classification and report.

### Step 6 improvement expectations

- a green-but-slow transcript exits 8, prints the windowed list, writes
  `a.ghog.outliers`, and shows `avg=`/`outliers=`.
- a tidy transcript exits 0; a raised override exits 0; a missing file seeds the
  floor and still reports.
- a failing transcript with a durations block keeps exit 2 (outliers judged last).

### What was implemented for Step 6

(empty -- to be filled after the step is implemented.)

### New types or classes introduced for Step 6

(empty.)

### Architecture check for Step 6

(empty.)

### Performance check for Step 6

(empty.)

### Unit test coverage check for Step 6

(empty.)

### Feature integrity for Step 6

(empty.)
