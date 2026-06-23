# v0.8.0 git-history report implementation tracking and validation

No, it is not implemented.

This document tracks the v0.8.0 git-history report build, step by step, against `docs/plan.v0.8.0.git-history-report.md`. Nothing has been implemented yet: the aggregation has not moved to `aggregate.py`, there is no multi-repo CLI, no analysis files, no front-end filters, and no skill. Each step below holds an empty skeleton until an implementation check fills it.

> Initial-skeleton note: this first version (written by `write-plans`, before any
> implementation check) fills `Goal for Step N` and `Step N improvement
> expectations`, opens every `Analysis of Step N implementation state` with "Not
> started. Step N is not implemented because ...", and fills every other section
> with the literal placeholder `_(empty — no check has taken place yet.)_.`.
>
> Markdown lint note: never leave a space immediately inside an inline code span
> (MD038) -- write a needed space as the token `[space]`, as in `` `[space]${x}` ``.
> The empty placeholder ends in `)_.` so the line is not pure italic text (MD036).

---

## File-based IO cost clarification for v0.8.0 git-history report (implementation)

All implementation work must respect the IO classification established in `docs/plan.v0.8.0.git-history-report.md`. The key constraints carried forward from the plan are:

- One `git log` subprocess per repo; the `git_history.csv` scratch file stays git-ignored.
- `data.json` and `dashboard.html` are each written once per run; no directory scan and no per-commit file IO.
- `analysis.generated.md` is rewritten once per run; `analysis.notes.md` is read once and never overwritten.
- The rendered `dashboard.html` does zero IO at view time: the data is inlined and only Chart.js loads from the CDN.

---

## Complexity Bound Clarification for v0.8.0 (implementation)

The scaling target for all v0.8.0 code paths is:

- **O(1) amortized per commit**: tag, classify, and tally each commit in constant work.
- **O(n) total per phase**: one pass over commits to aggregate; the in-page filters sum pre-aggregated per-project series, O(projects x buckets), not O(commits).

Every implemented step should be reviewed against this bound in its Performance check section.

---

## Step 0. Perf gate and test scaffolding

### Analysis of Step 0 implementation state

Yes. Step 0 has been fully implemented.

The perf gate, the nested test subpackage, and the relocation of the flat build test are all in place, and one `ghog day` walk reports the objective (`fail=0 warn=0 xfail=1 cov=100 outliers=0 exit=0`). Step 0 adds no production code under `tools/`, so coverage stays at 100%; the single `xfail` is the owning-step perf gate, as designed.

### Goal for Step 0

Add a timeout-bound aggregation perf gate (marked `xfail` until Step 1.1) over a synthetic many-commit, several-repo fixture, create the `tests/unit/tools/git_history_dashboard/` subpackage and its test leaves with their `__init__.py` files, and relocate the existing flat build test into the subpackage as `test_build/test_build_tdd.py` (Q01).

### Step 0 improvement expectations

- A linear-time guard exists for the combined aggregation, failing as `xfail` until Step 1.1.
- The new per-module test packages import cleanly, and the relocated build test runs from its new path (Q01).
- `ghog day` is green with the gate counted as an expected failure.

### What was implemented for Step 0

- **Nested test subpackage**: created `tests/unit/tools/git_history_dashboard/__init__.py` and the `test_build/` and `test_aggregate/` leaves, each with a docstring `__init__.py` and `# eof`, adopting the per-test-folder convention (Q01).
- **Perf gate**: `test_aggregate/test_aggregate_perf_tdd.py` holds `TestCombinedAggregationPerf::test_combined_aggregation_stays_linear`, marked `@pytest.mark.timeout(8)` and `@pytest.mark.xfail(reason="combined aggregation lands in Step 1.1", strict=False)`. The future `aggregate` module is loaded with `importlib.import_module` behind a `try`/`except ImportError`, so the static type-checkers never resolve the not-yet-existing module and collection never errors; the gate xfails on the missing module today.
- **Relocation**: `tests/unit/tools/test_git_history_dashboard_build.py` moved verbatim to `test_build/test_build_tdd.py` (the docstring records the move; the absolute `from tools.git_history_dashboard import build` import is unchanged), and the flat original was deleted.
- **Outlier baselines**: the four real-git build tests whose node IDs changed in the move were re-accepted with `ghog exclude` at their measured times (4s, 4s, 3s, 3s), restoring the acceptance the old node IDs carried.
- **Validation evidence**: `ghog day` exit=0, `fail=0 warn=0 xfail=1 cov=100 outliers=0`.

### New types or classes introduced for Step 0

No production type was introduced; the step is test-only. The new code is one test class, `TestCombinedAggregationPerf`, and a module-level `_synthetic_commits` helper in the perf-gate file, plus three package `__init__.py` markers. No file under `tools/` was added or changed for this step.

### Architecture check for Step 0

- **Layer placement**: the change is confined to `tests/`; no production module or import changed, so no DDD-Hexagonal port or adapter boundary is touched.
- **Dependency direction**: the perf gate depends on the future `aggregate` module only through a dynamic, guarded import, so the test carries no hard dependency on code that does not exist yet and reaches no production internal beyond the public `build` surface the relocated test already used.
- **Test layout**: the perf gate sits in its own `test_aggregate` leaf (targeting the future `aggregate.py`) and the relocated build test in its own `test_build` leaf, one test folder per class file, matching the convention adopted in Q01.

No, there is nothing that needs to be addressed.

### Performance check for Step 0

- **No new `O(n^2)` or `O(n log n)` path**: the only added computation is `_synthetic_commits`, a single `O(n)` loop building `n` tuples; no production code path changed.
- **The gate is a guard, not a cost**: the perf test xfails today (a fast assert failure on the missing module) and, once the aggregation lands, bounds it at 8 seconds, which is the linear-time guard itself.
- **Startup or background path**: unchanged; the dashboard build is untouched.

No, there is no performance issue that needs to be addressed.

### Unit test coverage check for Step 0

- **`build.py`**: covered at 100%. Step 0 leaves `build.py` unchanged and moves its test verbatim to `test_build/test_build_tdd.py`, so the same assertions keep the class at 100%; the `ghog day` run measured `cov=100`.
- **No other production class file is impacted by Step 0**, so none drops below 100%. The perf-gate file is a test module with no production class to cover; its body xfails today.

No, there is no unit-tested class below 100% that needs completing for Step 0.

### Feature integrity for Step 0

- **Existing feature behavior**: no production code changed, so `build.py` and the dashboard tool behave exactly as before; the relocated test exercises the same `build` surface, preserving the export, parse, aggregate, render, and `__main__` coverage.
- **Reporting or diagnostics**: the suite gains one expected-failure (`xfail`) signal, the owning-step perf marker; no existing reporting was removed or changed.
- **Compatibility or rollout note**: removing the flat test changes the four real-git tests' node IDs, so their previously-accepted outlier baselines were re-applied at the new IDs; no runtime behavior changed.

No existing feature or reporting capability is impaired.

---

## Step 1. Behavior-preserving extraction of aggregation and render

### Analysis of Step 1 implementation state

Yes. Step 1 has been fully implemented.

The aggregation and the render are extracted into `aggregate.py` and `render.py`, `build.py` is a thin hub at 247 lines that re-exports the moved names, and the tests are redistributed with the suite green at 100 percent coverage. The only deviation from the plan's prediction is benign: the Step 0 perf gate now xpasses instead of staying `xfail`, because it calls the just-extracted `aggregate()`; the gate is retargeted and its marker removed in Step 1.1.

### Goal for Step 1

Move the aggregation into a new `aggregate.py` and the placeholder substitution into a new `render.py`, a behavior-preserving extraction; the tests move with them and the suite stays green, while the Step 0 `xfail` stays (Q04, Q05).

### Step 1 improvement expectations

- `build.py` drops below 360 lines and becomes a thin hub; `aggregate.py` and `render.py` own their pieces.
- No behavior or payload change; the suite stays green.
- The Step 0 perf gate stays `xfail` (the combined aggregation is added in Step 1.1).

### What was implemented for Step 1

- **`aggregate.py` (new)**: the data model (`Commit`, `DashboardData`, `Highlights`) and the aggregation (`classify`, `_build_daily_series`, `_aggregate_weeks`, `_CommitTallies`, `_empty_tallies`, `_parse_commit_clock`, `_record_commit`, `_build_dashboard_payload`, `aggregate`, `compute_highlights`), moved verbatim from `build.py`.
- **`render.py` (new)**: `render` and its placeholder-token table, importing `compute_highlights` from `aggregate`.
- **`build.py` (247 lines, was 518)**: keeps the export, the CSV parse, `run_build`, the CLI and `__main__`; imports the moved names from `aggregate` and `render` and re-exports them through `__all__`, so `build.<name>` callers are unaffected.
- **`__init__.py`**: docstring updated for the three-module split.
- **Tests redistributed**: the classifier and aggregation assertions to `test_aggregate/test_aggregate_tdd.py`, the render assertion to `test_render/test_render_tdd.py`; `test_build/test_build_tdd.py` keeps the export, the CSV parse, `run_build`, `main` and `__main__`. No test was dropped.
- **Validation evidence**: one `ghog day` walk reports the objective, `fail=0 cov=100 outliers=0 exit=0`; `build.py` at 247, `aggregate.py` at 312, `render.py` at 52 lines, all under the 550 risk threshold.

### New types or classes introduced for Step 1

No new production type was introduced. The step is a behavior-preserving move: `Commit`, `DashboardData`, `Highlights` and `_CommitTallies` existed already and only changed module. The new files `aggregate.py` and `render.py` are modules, not types.

### Architecture check for Step 1

- **Module boundaries**: the new modules form a clean one-way chain — `render` imports `aggregate`, `build` imports both, `aggregate` imports nothing from the package. No import cycle.
- **Layer placement**: each module has one responsibility — `aggregate` the data and the math, `render` the HTML substitution, `build` the export, parse, orchestration and CLI. The hub no longer mixes aggregation and rendering with the IO.
- **Re-export surface**: `build.__all__` lists the moved names so `build.<name>` stays valid; the imports are used through that export, not dead.

No, there is nothing that needs to be addressed.

### Performance check for Step 1

- **No new `O(n^2)` or `O(n log n)` path**: the code is moved unchanged; the aggregation keeps its single O(n) pass over commits and the one sort of days and weeks.
- **The perf gate now runs for real**: it aggregates 6000 synthetic commits within the 8-second bound (an xpass), confirming the extracted `aggregate` stays linear.
- **Startup or background path**: unchanged; import adds two small modules.

No, there is no performance issue that needs to be addressed.

### Unit test coverage check for Step 1

- **`aggregate.py`**: covered at 100% by `test_aggregate_tdd.py` plus the `run_build` / `main` / `__main__` tests in `test_build_tdd.py` that drive it; the `ghog day` run measured `cov=100`.
- **`render.py`**: covered at 100% by `test_render_tdd.py` plus the end-to-end tests that render through `run_build`.
- **`build.py`**: covered at 100% by the export, parse, `run_build`, `main` and `__main__` tests in `test_build_tdd.py`.

No, there is no unit-tested class below 100% that needs completing for Step 1.

### Feature integrity for Step 1

- **Existing feature behavior**: the dashboard build is unchanged — same `data.json` payload and same rendered `dashboard.html`; the `__main__` test renders end to end and the export and parse tests still pass. `build.<name>` re-exports keep the public surface intact.
- **Reporting or diagnostics**: the `LOGGER` messages in `run_build` and `main` are unchanged. The Step 0 perf gate flips from `xfail` to a green xpass because `aggregate()` now exists; this is benign under `strict=False` and is finalized in Step 1.1 when the gate is retargeted at the `by_project` path and its marker removed.
- **Compatibility or rollout note**: no behavior change; only the module a name lives in changed, with re-exports preserving the old access.

No existing feature or reporting capability is impaired.

---

## Step 1.1. Data model: project tag, author tally, and per-project breakdown

### Analysis of Step 1.1 implementation state

Yes. Step 1.1 has been fully implemented.

`Commit` is now a `NamedTuple` with a `project` field, `aggregate` builds the `projects` list, the `by_project` per-project sub-aggregates (which sum back to the top-level series), and the `by_author` tally, and the perf gate is retargeted at the project-tagged path with its `xfail` removed. One `ghog day` walk reports the objective at 100 percent coverage, and a hypothesis property test checks the per-project sum invariant.

### Goal for Step 1.1

Introduce a `Commit` NamedTuple with a `project` field (Q02), add a `by_author` tally, a `projects` list, and a `by_project` breakdown whose per-project series sum to the top-level series, and remove the Step 0 `xfail` (Q04).

### Step 1.1 improvement expectations

- The payload carries `projects`, `by_project`, and `by_author`.
- A single-project run keeps the prior output plus the new keys.
- The perf gate is now a real green (no longer `xfail`).

### What was implemented for Step 1.1

- **`Commit` NamedTuple**: `aggregate.py` defines `Commit(sha, iso_date, author, subject, project)`; `_record_commit` reads it by attribute and tags each `recent` row with the project.
- **Per-project and author aggregation**: `aggregate` makes one O(n) pass into a global tally and a per-project tally; `_build_combined_payload` assembles `projects`, `by_project` (per-project slices aligned to the global span so they sum to the top-level), and `by_author`, with `_project_data` building each slice.
- **Project tagging in the hub**: `iter_commits_from_csv` still yields raw rows (the CSV-parse tests are untouched); `run_build` gains a `project` argument and tags each row into a `Commit`; `main` derives the project name from the source repo (or the project root for `--csv`).
- **Perf gate**: `test_aggregate_perf_tdd.py` drops the `xfail` and the `importlib` guard, builds `Commit` records across five projects, and bounds the run at 8 seconds.
- **Property test**: `test_aggregate_pbt.py` (hypothesis) asserts the per-project list and mapping series sum back to the top-level.
- **Validation evidence**: `ghog day` reports the objective, `fail=0 xfail=0 cov=100 outliers=0 exit=0`.

### New types or classes introduced for Step 1.1

- **`Commit`** (`NamedTuple`): the parsed commit tagged with its project, replacing the former 4-tuple alias.
- **`ProjectData`** (`TypedDict`): one project's slice of the series, aligned to the global span and listed in `aggregate.__all__`.

No other new production type; the rest is functions and the extended `DashboardData` keys.

### Architecture check for Step 1.1

- **Single-pass aggregation**: `aggregate` fills the global and per-project tallies in one O(n) loop; the per-project slices reuse `_build_daily_series` and `_aggregate_weeks` over the global span, so there is no second scan of the commits.
- **Boundary direction**: the project dimension lives in `aggregate.py`; `build.py` only tags rows into `Commit` records at `run_build` and derives the project name in `main`; `render` is untouched, and there is no import cycle.
- **Re-export surface**: `aggregate.__all__` adds `ProjectData`; `build.py` re-exports the data model unchanged.

No, there is nothing that needs to be addressed.

### Performance check for Step 1.1

- **No new `O(n^2)` or `O(n log n)` path**: one O(n) pass tags every commit into two tallies; assembling the per-project payload is O(projects x buckets), and the day and week sort is the one unavoidable sort, as before.
- **The perf gate proves it**: 6000 commits across five projects aggregate within the 8-second bound.
- **Page recompute stays cheap**: the per-project slices align to the global span, so summing them is O(projects x buckets), not O(commits).

No, there is no performance issue that needs to be addressed.

### Unit test coverage check for Step 1.1

- **`aggregate.py`**: covered at 100% by `test_aggregate_tdd.py` (the project tag, the author tally, the single- and multi-project split, the skip and empty edges) and `test_aggregate_pbt.py` (the sum invariant), plus the `run_build` / `main` / `__main__` tests that drive it; `ghog day` measured `cov=100`.
- **`build.py`**: covered at 100% by the export, the parse, `run_build` (now with a project) and the `main` / `__main__` tests.

No, there is no unit-tested class below 100% that needs completing for Step 1.1.

### Feature integrity for Step 1.1

- **Existing feature behavior**: a single-repo run keeps the prior `data.json` series and adds the new `projects`, `by_project` and `by_author` keys; the rendered `dashboard.html` is unchanged because `render` ignores the new keys and the template reads the same tokens.
- **Reporting or diagnostics**: the `LOGGER` messages are unchanged; `recent` rows gain a `project` field the page can later filter on, which the current template ignores.
- **Compatibility or rollout note**: `iter_commits_from_csv` still yields raw rows, so its parsing tests and any external caller are unaffected; `run_build` gains a required `project` argument, the one signature change, consumed only inside the tool.

No existing feature or reporting capability is impaired.

---

## Step 2. Multi-repo CLI: targeting, the output rule, browser open, and the run summary

### Analysis of Step 2 implementation state

Not started. Step 2 is not implemented because `build.py` still targets one repo, never opens the page, and has no run summary or per-repo error handling.

### Goal for Step 2

Add a `cli.py` orchestration module: resolve zero, one, or several repo targets; require `--out-dir` for a multi-repo run; keep the single-repo default; open `dashboard.html` unless `--no-open`; log per-phase errors and skip a failing repo; print a run summary. Keep `build.py` a thin hub.

### Step 2 improvement expectations

- A multi-repo run writes one combined report to the named `--out-dir`.
- A bad repo is logged, skipped, and named in the summary; `--no-open` keeps the browser shut.
- The single-repo default folder is unchanged.

### What was implemented for Step 2

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 2

_(empty — no check has taken place yet.)_.

### Architecture check for Step 2

_(empty — no check has taken place yet.)_.

### Performance check for Step 2

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 2

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 2

_(empty — no check has taken place yet.)_.

---

## Step 3. Analysis files, conversion, and the project-neutral template slots

### Analysis of Step 3 implementation state

Not started. Step 3 is not implemented because the analysis is still hardcoded in `template.html`, with no slot, no generated-figures file, and no markdown conversion.

### Goal for Step 3

Add `analysis.py` to write `analysis.generated.md` from the figures, keep one `analysis.notes.<project>.md` per project untouched (Q06), concatenate the generated file then the per-project notes and convert to HTML through a `uv --with markdown` seam `analysis.py` shells to and the tests monkeypatch (Q03), and inject it into a new `__ANALYSIS__` slot; add the `__ANALYSIS__` and `__TITLE__` tokens to `render.py` and parameterize the template title, header, `sr-only` text, and footer, removing the pdfsplitter strings.

### Step 3 improvement expectations

- A run writes the generated markdown and fills the analysis and title slots.
- A second run refreshes the figures and leaves every per-project notes file byte-for-byte unchanged.
- The rendered HTML carries no pdfsplitter string.

### What was implemented for Step 3

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 3

_(empty — no check has taken place yet.)_.

### Architecture check for Step 3

_(empty — no check has taken place yet.)_.

### Performance check for Step 3

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 3

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 3

_(empty — no check has taken place yet.)_.

---

## Step 4. Dashboard front-end: project filter, contributor leaderboard, theme toggle, recompute-all filtering

### Analysis of Step 4 implementation state

Not started. Step 4 is not implemented because the page still reads fixed top-level arrays, has no project filter, no contributor list, and no theme toggle.

### Goal for Step 4

Generalize the client logic to recompute every widget and the metric cards on any filter change by summing the visible `by_project` slices; add a project-chip filter, a date-range control, a `by_author` top-10 leaderboard recomputed with the project filter, and a two-state light/dark toggle with a remembered `data-theme` override.

### Step 4 improvement expectations

- Hiding a project recomputes every widget and the leaderboard.
- Narrowing the date range recomputes the charts and metrics while the leaderboard stays all-time.
- The theme toggle flips and is remembered across visits.

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

## Step 5. The skill, the README, and acceptance tests

### Analysis of Step 5 implementation state

Not started. Step 5 is not implemented because there is no user-facing skill, the README still describes the single-repo tool, and nothing validates the whole flow end to end.

### Goal for Step 5

Add `.claude/skills/git-history-report/SKILL.md` and `instructions/git-history-report.md`, update the README for the multi-repo run and the analysis files, and add acceptance tests that build a real multi-repo report from throwaway repos and assert the payload shape, the filled slots, the analysis round-trip, and the suppress flag.

### Step 5 improvement expectations

- The skill drives a combined report end to end.
- The acceptance tests prove `projects`, `by_project`, and `by_author` in the payload, the filled `__ANALYSIS__` and `__TITLE__` slots, the notes-preserving re-run, and `--no-open`.
- The README documents the multi-repo run and the analysis files.

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
