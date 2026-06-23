# v0.8.0 git-history report implementation plan -- a skill, a project dimension, and a richer page

The build tool keeps its shape; the new work lands in new modules around it so no Python file grows past the line budget.

- **Aggregation moves out and grows up**: the per-day/type/scope/hour/weekday math leaves `build.py` for a new `aggregate.py`, then gains a project tag, an author tally, and a per-project breakdown.
- **Orchestration and analysis are new modules**: a multi-repo CLI and the markdown analysis files sit in their own files, so `build.py` stays a thin hub.
- **The page does the rest client-side**: the template gains a project filter, a contributor list, a theme toggle, and a recompute-all-widgets filter loop, fed by the richer payload.

> Markdown lint note: never leave a space immediately inside an inline code span
> (MD038); when a snippet starts or ends with a space, write that space as the
> literal token `[space]`, as in `` `[space]${x}` ``. End any line that would be
> only italic text with a period after the closing underscore (MD036).

## Plan goal for v0.8.0 git-history report

Implement the full v0.8.0 git-history report feature set as described in `docs/design.v0.8.0.git-history-report.md` and `docs/feature-request.v0.8.0.git-history-report.md`, targeting the confirmed outcomes in ordered implementation steps.

- **Step 0 goal**: a timeout-bound perf gate (xfail) for the combined multi-repo aggregation; create the nested `git_history_dashboard` test subpackage and relocate the existing flat build test into it (Q01).
- **Step 1 goal**: behavior-preserving extraction of the aggregation into `aggregate.py` and the render into `render.py`; tests move, the suite stays green, the Step 0 xfail stays (Q04, Q05).
- **Step 1.1 goal**: add the project tag (a `Commit` NamedTuple), the author tally, and the per-project breakdown; remove the Step 0 xfail (Q02, Q04).
- **Step 2 goal**: a native multi-repo CLI in a new orchestration module: target resolution, the `--out-dir` rule, browser open with a suppress flag, per-phase error logging, and a run summary.
- **Step 3 goal**: the analysis files and the template slots: a generated markdown file plus one hand-written notes file per project, the `uv --with markdown` conversion seam, and the project-neutral title and footer tokens (Q03, Q06).
- **Step 4 goal**: the dashboard front-end: a project filter, a contributor leaderboard, a theme toggle, and a recompute-every-widget filter loop.
- **Step 5 goal**: the user-facing skill, the README, and acceptance tests that build a real multi-repo report end to end.

---

## Scope anchors for v0.8.0 git-history report plan

This plan implements the design from `docs/design.v0.8.0.git-history-report.md` and the linked feature-request, targeting the following outcomes:

1. A skill builds or updates one combined report for one or several projects, writes it to a chosen output folder, and opens it unless suppressed.
2. The payload carries a project dimension and a per-author tally, so every widget recomputes under a date, type, and project filter.
3. One filter-aware top-10 contributor leaderboard by author name.
4. The analysis lives in two markdown files (generated, hand-written), converted to HTML at build time and injected into a template slot.
5. A two-state light/dark toggle that starts from the machine setting and remembers a manual flip.

The following are explicitly **in scope** for this plan:

- A project label on every commit, set at parse time in `build.py`'s multi-repo mode.
- A `projects` list and a `by_project` breakdown in the payload, plus a `by_author` tally.
- A project-neutral template (title, header, `sr-only` text, footer) and an `__ANALYSIS__` slot.
- The in-page recompute of every widget under the three filters.

The following are explicitly **deferred** to v0.9.0 and beyond:

- Contributor identity folding (name-based only here).
- Generation-time bounding of the report; a per-project narrative; a per-project dashboard.
- A contributor count that follows the date slider (the leaderboard stays all-time).
- A vendored pure-Python markdown converter (this plan uses the `uv --with markdown` step).

---

## Complexity Bound Clarification for v0.8.0

The scaling target for all v0.8.0 code paths is:

- **O(1) amortized per commit**: tagging, classifying, and tallying each commit (type, scope, hour, weekday, author, project) is constant work per commit.
- **O(n) total per phase**: one pass over the commits of all repos to aggregate; one pass over days for the gap-free calendar series; one pass over the payload to render.

No v0.8.0 code path should introduce `O(n^2)` or `O(n log n)` cost on the build path beyond the single unavoidable sort of days and weeks. The in-page filters recompute by summing pre-aggregated per-project series, which is O(projects x buckets), not O(commits). Any new path that breaks this bound must be called out as a defect before merge.

---

## File-based IO cost clarification for v0.8.0 git-history report

The report build is a one-shot offline operation, not a response path, so the IO rules are about keeping that one build lean and the rendered page IO-free.

- One `git log` subprocess per repo (O(repos) spawns), each writing the git-ignored `git_history.csv` scratch file, then read back once.
- The payload is built in memory and written once as `data.json` and once as `dashboard.html`; no directory scan, no per-commit file IO.
- The analysis conversion reads the two markdown files once and writes nothing extra; the generated markdown is written once per run.
- The rendered `dashboard.html` does zero IO at view time: the data is inlined, and only Chart.js loads from the CDN. Opening the report is a tiny static-file read, not a metadata-loading delay.

---

## Confirmed technical facts for v0.8.0 plan viability

These facts were drawn from direct code inspection of the current repository tree.

**Files at or approaching the 550-line risk threshold** (must not grow in place):

- `tools/git_history_dashboard/build.py`: **518 lines** -- already near the line. The aggregation must move out to `aggregate.py` (Step 1) so this file shrinks before the multi-repo and analysis wiring is added; it must stay a thin hub.
- `tools/git_history_dashboard/template.html`: **542 lines** -- not a Python file, so the 650-line Python "big file" rule does not apply, but it will grow with the front-end. Keep the JS inline to preserve the single-static-file property; flag a future template-partials split as deferred, do not force it in this plan.

**Files safe to extend** (current lines, expected additions):

- `tools/git_history_dashboard/__init__.py`: 10 -- add exports for the new `aggregate`, `analysis`, and `cli` modules.
- `tools/git_history_dashboard/README.md`: 85 -- document the skill, the multi-repo run, the output rule, and the analysis files.
- `tests/unit/tools/test_git_history_dashboard_build.py`: 348 -- relocated to `test_build/test_build_tdd.py` in Step 0 (Q01); after its aggregation and render assertions move to the `test_aggregate` and `test_render` leaves in Step 1, it keeps the export and `__main__` coverage.

**What does not exist yet (all new for v0.8.0)**:

- `tools/git_history_dashboard/aggregate.py` (the extracted, then extended, aggregation).
- `tools/git_history_dashboard/render.py` (the extracted placeholder substitution and slot tokens, Q05).
- `tools/git_history_dashboard/cli.py` (multi-repo orchestration, output rule, open and summary).
- `tools/git_history_dashboard/analysis.py` (the generated markdown, the per-project notes files, the conversion seam, the slot injection).
- `.claude/skills/git-history-report/SKILL.md` and `instructions/git-history-report.md` (the user-facing skill).

**Other confirmed technical facts that affect plan shape**:

- **The author is already exported but dropped**: `%an` reaches the commit tuple; only `_record_commit` ignores it. The `by_author` tally is an add, not a re-export.
- **Rendering is placeholder substitution**: `render` swaps `__DATA__` and the metric tokens; `__ANALYSIS__` and `__TITLE__` slots fit the same mechanism with no templating engine.
- **A markdown-to-HTML path exists but pulls packages**: `a.md2pdf.py` uses the `markdown` package via `uv run --with markdown`. Step 3 reuses that pattern as a build-time uv step; `build.py` stays import-clean.
- **Dark mode follows the OS but cannot be toggled**: the template already has light and dark CSS variables under `prefers-color-scheme`; the toggle adds a `data-theme` override and persistence, not a new palette.

---

## Current test-tree validation snapshot for v0.8.0 git-history report

Existing test packages that v0.8.0 must not break:

- `tests/unit/tools/test_git_history_dashboard_build.py` -- 348 lines today; Step 0 relocates it into the new subpackage as `test_build/test_build_tdd.py` (Q01 adopts the nested convention and reorganizes the existing flat file). Its aggregation and render assertions then move to the `test_aggregate` and `test_render` leaves in Step 1; it keeps the export and `__main__` coverage.
- `tests/unit/tools/__init__.py` -- present; the parent package for the new `git_history_dashboard` test subpackage.

New test leaf directories to create for v0.8.0 (each with an `__init__.py`, nested per the adopted convention, Q01):

- `tests/unit/tools/git_history_dashboard/` (new subpackage root).
- `tests/unit/tools/git_history_dashboard/test_build/` (`test_build_tdd.py`, relocated from the flat file in Step 0).
- `tests/unit/tools/git_history_dashboard/test_aggregate/` (`test_aggregate_perf_tdd.py` in Step 0; `test_aggregate_tdd.py` in Step 1; `test_aggregate_pbt.py` in Step 1.1).
- `tests/unit/tools/git_history_dashboard/test_render/` (`test_render_tdd.py`, in Step 1).
- `tests/unit/tools/git_history_dashboard/test_cli/` (`test_cli_tdd.py`).
- `tests/unit/tools/git_history_dashboard/test_analysis/` (`test_analysis_tdd.py`).
- `tests/unit/tools/git_history_dashboard/test_report_acceptance/` (`test_report_acceptance_tdd.py`).

---

## Runtime file note for v0.8.0 git-history report plan

- `<out-dir>/git_history.csv` -- the git-ignored scratch export, already covered by `.gitignore`; unchanged.
- `<out-dir>/data.json` and `<out-dir>/dashboard.html` -- versioned report snapshots, as today.
- `<out-dir>/analysis.generated.md` -- rewritten each run from the figures; versioned as part of the report snapshot.
- `<out-dir>/analysis.notes.<project>.md` -- one hand-written notes file per project (Q06), created once if absent and never overwritten by a run; versioned. Each project's notes are editable in isolation; the build concatenates the generated file then the per-project notes in project order.

---

## Shared execution command checklist for all v0.8.0 git-history report steps

Apply this checklist for every numbered step, filling in the step-specific paths.

1. Count lines before edits on all step files with the shared line-count command below.
2. Apply tests-first changes as described under the step implementation section.
3. Run the step-targeted test command with `ghog single`.
4. Run the step grep checks.
5. Run the shared gate loop (`ghog day`) until both the focused tests and the repo gate pass in the same cycle.
6. Count lines after edits and compare with the step line-budget checkpoint.
7. If any Python file exceeds 650 lines after edits, stop and apply the step split guidance before committing.

---

## Ready-to-run command templates for all v0.8.0 git-history report steps

Use these template forms in each step, substituting actual paths. Groundhog owns check and tests; never call `check.bat` or `pytest` directly.

- Line count (reliable, encoding-safe): `python -c "import sys;print(sum(1 for _ in open(sys.argv[1],encoding='utf-8')))" <file>`
- Targeted tests: `ghog single <step test files>`
- Grep checks: `rg -n "<pattern>" tools/git_history_dashboard tests/unit/tools/git_history_dashboard`
- Shared gate loop: `ghog day`, repeated fix-and-walk until it reports the objective (`exit=0`): `check.bat`, the affected tests, then the full suite with coverage, in order, stopping at the first non-green step.
- Line count after: the same line-count command on each step file.

---

## Shared timeout target policy for v0.8.0 git-history report perf-complexity gates

- Add one focused responsiveness gate on the combined aggregation, with a generous timeout and a synthetic many-commit, several-repo fixture, so a future O(n^2) regression in the per-project breakdown trips it.
- Mark the Step 0 gate `xfail` with explicit owning-step text while the multi-repo aggregation is still pending.
- Remove the `xfail` in Step 1.1 when `aggregate.py` lands the combined aggregation.

Gate-to-step ownership for v0.8.0:

- `test_aggregate_perf_tdd::test_combined_aggregation_stays_linear` -> remove `xfail` in Step 1.1.

---

## Numbered steps for v0.8.0 git-history report

### Step 0. Perf gate and test scaffolding

#### Step 0 -- analysis and intent for the aggregation perf gate

Issues to address:

- There is no guard that the new per-project breakdown keeps the aggregation linear in the commit count.
- The new per-module test leaves and their `__init__.py` files do not exist yet.
- The existing dashboard test sits flat under `tests/unit/tools`, out of step with the nested convention adopted in Q01.

Fix intent:

- Add a timeout-bound aggregation test over a synthetic many-commit, several-repo fixture, marked `xfail` until the combined aggregation exists.
- Create the `tests/unit/tools/git_history_dashboard/` subpackage and the test leaves with their `__init__.py` files.
- Relocate `tests/unit/tools/test_git_history_dashboard_build.py` into the subpackage as `test_build/test_build_tdd.py`, a pure move that keeps the suite green (Q01).

Expected outcome:

- `ghog day` is green with the gate present and `xfail` (an expected failure, not a hard failure).
- The new test packages import cleanly.

Step framing:

- Design link: Complexity Bound Clarification; Design Area 1 (per-project breakdown).
- Execution checklist reference: Shared execution command checklist for all v0.8.0 git-history report steps.

#### Step 0 -- implementation for the aggregation perf gate

**Files involved**:

- `tests/unit/tools/git_history_dashboard/__init__.py` (new, to be created).
- `tests/unit/tools/git_history_dashboard/test_build/__init__.py` (new, to be created).
- `tests/unit/tools/git_history_dashboard/test_build/test_build_tdd.py` (new, relocated from `tests/unit/tools/test_git_history_dashboard_build.py`).
- `tests/unit/tools/test_git_history_dashboard_build.py` (existing, to be deleted after the move).
- `tests/unit/tools/git_history_dashboard/test_aggregate/__init__.py` (new, to be created).
- `tests/unit/tools/git_history_dashboard/test_aggregate/test_aggregate_perf_tdd.py` (new, to be created).

**Tests first**:

- `test_combined_aggregation_stays_linear`: build a synthetic list of N commits spread over M repos, call the combined aggregation entry, and assert it returns within a `@pytest.mark.timeout(...)` bound. Mark `@pytest.mark.xfail(reason="combined aggregation lands in Step 1.1", strict=False)` with the owning-step text.
- Relocate the existing build test verbatim into `test_build/test_build_tdd.py`; its assertions are unchanged, only the path moves.

**Classes and behavior**:

- No production code in this step; the test imports the future `aggregate` entry behind a guard so the `xfail` is an import-or-assert failure, not a collection error.

**Completion criteria**:

- `ghog day` reports the objective (`exit=0`) with the gate counted as `xfail`.
- `rg -n "xfail" tests/unit/tools/git_history_dashboard` shows the one owned gate.
- The new packages are importable.

#### Step 0 -- addendums for the aggregation perf gate

Line-budget checkpoint:

- `test_aggregate_perf_tdd.py`: before 0 -> target <= 120.

Split guidance:

- None; test-only step.

Full workflow timing run readiness:

- `ghog single tests/unit/tools/git_history_dashboard/test_aggregate/test_aggregate_perf_tdd.py`

Time-gated status for Step 0:

- The gate is `xfail` here; Step 1.1 removes the `xfail`.

---

### Step 1. Behavior-preserving extraction of aggregation and render

#### Step 1 -- analysis and intent for the extraction

Issues to address:

- The aggregation and the render both live inside the 518-line `build.py`, which has no room to grow.

Fix intent:

- Move the aggregation (`classify`, the daily and weekly builders, `aggregate`, `compute_highlights`, the tally dataclass) into a new `aggregate.py`, and the placeholder substitution (`render`) into a new `render.py`; `build.py` imports both (Q04, Q05). No behavior change and no payload change this step.

Expected outcome:

- `build.py` drops well below 360 lines and becomes a thin hub; `aggregate.py` and `render.py` own their pieces; the suite stays green and the Step 0 perf gate stays `xfail`.

Step framing:

- Design link: Design Area 1; plan decisions Q04 (extract first) and Q05 (`render.py`).
- Execution checklist reference: Shared execution command checklist for all v0.8.0 git-history report steps.

#### Step 1 -- implementation for the extraction

**Files involved**:

- `tools/git_history_dashboard/aggregate.py` (new, to be created) -- the moved aggregation, verbatim.
- `tools/git_history_dashboard/render.py` (new, to be created) -- the moved `render` and its slot-token table, verbatim.
- `tools/git_history_dashboard/build.py` (existing, to be updated) -- import from `aggregate` and `render`; keep the export, the CLI, and `__main__`.
- `tools/git_history_dashboard/__init__.py` (existing, to be updated) -- export the `aggregate` and `render` surfaces.
- `tests/unit/tools/git_history_dashboard/test_aggregate/test_aggregate_tdd.py` (new, to be created) -- the moved aggregation assertions.
- `tests/unit/tools/git_history_dashboard/test_render/__init__.py` and `test_render/test_render_tdd.py` (new, to be created) -- the moved render assertions.
- `tests/unit/tools/git_history_dashboard/test_build/test_build_tdd.py` (existing in the subpackage from Step 0, to be updated) -- drop the moved assertions, keep export and `__main__`.

**Tests first**:

- Move the aggregation assertions into `test_aggregate_tdd.py` and the render assertions into `test_render_tdd.py`, unchanged in meaning; `test_build_tdd.py` keeps the export and `__main__` coverage. The Step 0 perf `xfail` stays (the combined aggregation is not added yet).

**Classes and behavior**:

- `aggregate.py`: the same functions and signatures, moved verbatim.
- `render.py`: `render` and the placeholder-token table, moved verbatim.
- `build.py`: imports and re-exports the moved names so external callers are unaffected.

**Completion criteria**:

- `ghog day` reports the objective (`exit=0`); the perf gate is still `xfail`.
- `rg -n "from .aggregate|from .render|import aggregate|import render" tools/git_history_dashboard/build.py` shows the imports.
- `python -c "import sys;print(sum(1 for _ in open(sys.argv[1],encoding='utf-8')))" tools/git_history_dashboard/build.py` is below 360.

#### Step 1 -- addendums for the extraction

Line-budget checkpoint:

- `tools/git_history_dashboard/build.py`: before 518 -> target <= 360 (aggregation and render removed).
- `tools/git_history_dashboard/aggregate.py`: before 0 -> target <= 300.
- `tools/git_history_dashboard/render.py`: before 0 -> target <= 120.

Split guidance:

- None this step; it is a move. If `aggregate.py` grows later, split the series builders into `aggregate_series.py`.

Full workflow timing run readiness:

- `ghog single tools/git_history_dashboard/aggregate.py tools/git_history_dashboard/render.py tests/unit/tools/git_history_dashboard/test_aggregate tests/unit/tools/git_history_dashboard/test_render`

Time-gated status for Step 1:

- The Step 0 `xfail` stays; Step 1.1 removes it.

---

### Step 1.1. Data model: project tag, author tally, and per-project breakdown

#### Step 1.1 -- analysis and intent for the data model

Issues to address:

- `aggregate.py` still drops the author and has no project dimension, so there is no `by_author`, no `projects`, and no `by_project`.

Fix intent:

- Introduce a `Commit` NamedTuple with a `project` field (Q02), set at parse time. Add a `by_author` Counter and build a `projects` list and a `by_project` map of per-project sub-aggregates, with the top-level series equal to the all-projects sum. Remove the Step 0 `xfail` (Q04).

Expected outcome:

- The payload carries `projects`, `by_project`, and `by_author`; a single-project run matches the prior output plus the new keys; the perf gate is now a real green.

Step framing:

- Design link: Design Area 1 (project-tagged data model, design Q01, Q02), Design Area 3 (`by_author` for design Q05); plan decision Q02 (`Commit` NamedTuple).
- Execution checklist reference: Shared execution command checklist for all v0.8.0 git-history report steps.

#### Step 1.1 -- implementation for the data model

**Files involved**:

- `tools/git_history_dashboard/aggregate.py` (existing, to be updated) -- the `Commit` NamedTuple, `by_author`, `projects`, `by_project`.
- `tools/git_history_dashboard/build.py` (existing, to be updated) -- the parser sets the project on each `Commit`.
- `tests/unit/tools/git_history_dashboard/test_aggregate/test_aggregate_tdd.py` (existing, to be updated).
- `tests/unit/tools/git_history_dashboard/test_aggregate/test_aggregate_pbt.py` (new, to be created) -- the by_project sum invariant with `hypothesis`.
- `tests/unit/tools/git_history_dashboard/test_aggregate/test_aggregate_perf_tdd.py` (existing, to be updated) -- remove the `xfail`.

**Tests first**:

- `test_aggregate_tdd.py`: a `Commit` carries its project; `by_author` counts by display name; `projects` lists the run's projects; a single-project run keeps the prior shape plus the new keys.
- `test_aggregate_pbt.py`: over random tagged commit lists, the sum of `by_project` equals each top-level series (the combine invariant), using `hypothesis` like `test_groundhog_durations_pbt.py`.
- Remove the `xfail` from `test_aggregate_perf_tdd.py` so the perf gate is a real green.

**Classes and behavior**:

- `Commit` (NamedTuple): `sha`, `iso_date`, `author`, `subject`, `project`.
- `aggregate(commits)`: one pass, O(n), builds the top-level series, the `by_project` map, and `by_author`.
- `build_combined_payload`: assembles `projects`, `by_project`, `by_author` into the `DashboardData` shape.

**Completion criteria**:

- `ghog day` reports the objective (`exit=0`); the perf gate is green (no longer `xfail`).
- `rg -n "by_project|by_author|class Commit" tools/git_history_dashboard/aggregate.py` shows the new shape.

#### Step 1.1 -- addendums for the data model

Line-budget checkpoint:

- `tools/git_history_dashboard/aggregate.py`: before <=300 -> target <= 420 (project and author math added).
- `test_aggregate_tdd.py`: target <= 320.
- `test_aggregate_pbt.py`: before 0 -> target <= 150.

Split guidance:

- If `aggregate.py` exceeds 550, split the series builders into `aggregate_series.py`, keeping the payload assembler in `aggregate.py`.

Full workflow timing run readiness:

- `ghog single tools/git_history_dashboard/aggregate.py tests/unit/tools/git_history_dashboard/test_aggregate`

Time-gated status for Step 1.1:

- Removes the Step 0 `xfail`; the perf gate stays as a permanent linear-time guard.

---

### Step 2. Multi-repo CLI: targeting, the output rule, browser open, and the run summary

#### Step 2 -- analysis and intent for orchestration

Issues to address:

- `build.py` targets one repo per call, always writes under that repo's docs folder, never opens the page, and has no run summary or per-repo error handling.

Fix intent:

- Add a `cli.py` orchestration module: resolve zero, one, or several repo targets; require `--out-dir` for a multi-repo run; keep the single-repo default; tag each repo's commits; call the combined aggregation; open `dashboard.html` unless `--no-open`; log per-phase errors and skip a failing repo; print a run summary.
- Keep `build.py` as the thin hub that wires `cli.py`, `aggregate.py`, and `render.py`.

Expected outcome:

- `python build.py repoA repoB --out-dir X` writes one combined report to `X`; a bad repo is skipped and named in the summary; `--no-open` keeps the browser shut.

Step framing:

- Design link: Design Area 6 (skill orchestration), design Q01, Q07 output rule; Q02 (browser suppress); the v0.7.0 Windows browser-hang lesson.
- Execution checklist reference: Shared execution command checklist for all v0.8.0 git-history report steps.

#### Step 2 -- implementation for orchestration

**Files involved**:

- `tools/git_history_dashboard/cli.py` (new, to be created).
- `tools/git_history_dashboard/build.py` (existing, to be updated) -- delegate argument handling and the run loop to `cli.py`.
- `tools/git_history_dashboard/__init__.py` (existing, to be updated) -- export the `cli` surface.
- `tests/unit/tools/git_history_dashboard/test_cli/__init__.py` (new, to be created).
- `tests/unit/tools/git_history_dashboard/test_cli/test_cli_tdd.py` (new, to be created).
- `tests/unit/tools/git_history_dashboard/test_build/test_build_tdd.py` (existing, to be updated) -- point the `__main__` test at the delegated flow.

**Tests first**:

- `test_cli_tdd.py`: no path resolves to the current project; one path keeps the default out-dir; two paths without `--out-dir` exit with the output-folder error; two paths with `--out-dir` write one combined report; `--no-open` suppresses the browser call (monkeypatch the opener); a failing repo export is logged, skipped, and listed in the summary; the summary names projects, counts, and the output path.

**Classes and behavior**:

- `resolve_targets(args)`: returns the ordered repo list and the resolved out-dir, raising the output-folder error for a multi-repo run with no `--out-dir`.
- `run(args)`: per-repo export and tag, combined aggregate, render, write, open-unless-suppressed, summary; a per-repo failure is caught, logged, and skipped.
- `open_in_browser(path, *, suppressed)`: the single seam tests monkeypatch, so no real browser opens under test.

**Completion criteria**:

- `ghog day` reports the objective (`exit=0`).
- `rg -n "no-open|out-dir|skipped" tools/git_history_dashboard/cli.py` shows the flags and the skip path.
- A throwaway two-repo run in the test writes one `dashboard.html` and one `data.json` to the chosen folder.

#### Step 2 -- addendums for orchestration

Line-budget checkpoint:

- `tools/git_history_dashboard/cli.py`: before 0 -> target <= 320.
- `tools/git_history_dashboard/build.py`: before <=430 -> target <= 430 (delegation, not growth).
- `test_cli_tdd.py`: before 0 -> target <= 320.

Split guidance:

- If `cli.py` nears 550, move target resolution and the output rule into `cli_targets.py`, keeping the run loop in `cli.py`.

Full workflow timing run readiness:

- `ghog single tools/git_history_dashboard/cli.py tests/unit/tools/git_history_dashboard/test_cli`

Time-gated status for Step 2:

- No perf gate affected.

---

### Step 3. Analysis files, conversion, and the project-neutral template slots

#### Step 3 -- analysis and intent for the analysis and template

Issues to address:

- The analysis is hand-written inside `template.html` and my-project-specific; there is no slot, no generated-figures file, and no markdown conversion.

Fix intent:

- Add `analysis.py`: write `analysis.generated.md` from the combined figures; create one `analysis.notes.<project>.md` per project if absent and never overwrite any (Q06); concatenate the generated file then the per-project notes in project order and convert to HTML through a `uv run --with markdown` seam that `analysis.py` shells out to and the unit tests monkeypatch (Q03); inject the HTML into a new `__ANALYSIS__` slot.
- Parameterize the template: replace the hardcoded title, header, `sr-only` text, and footer command with `__TITLE__` and the existing-style tokens; the title names the project, or the project count for a combined run. The two new tokens live in `render.py` (from Step 1).

Expected outcome:

- A run writes the generated markdown, keeps every per-project notes file, and fills the analysis and title slots; re-running refreshes the figures and leaves each notes file verbatim.

Step framing:

- Design link: Design Area 4 (analysis files and slot) and Design Area 7 (project-neutral template), design Q04, Q05, Q07; plan decisions Q03 (uv seam) and Q06 (per-project notes).
- Execution checklist reference: Shared execution command checklist for all v0.8.0 git-history report steps.

#### Step 3 -- implementation for the analysis and template

**Files involved**:

- `tools/git_history_dashboard/analysis.py` (new, to be created).
- `tools/git_history_dashboard/template.html` (existing, to be updated) -- add `__ANALYSIS__` and `__TITLE__` slots; drop the hardcoded my-project strings and the inline observations content.
- `tools/git_history_dashboard/render.py` (existing from Step 1, to be updated) -- add the `__ANALYSIS__` and `__TITLE__` tokens to the substitution table.
- `tools/git_history_dashboard/build.py` (existing, to be updated) -- write the analysis, build the title, and pass the analysis HTML and title through to `render`.
- `tools/git_history_dashboard/__init__.py` (existing, to be updated) -- export the `analysis` surface.
- `tests/unit/tools/git_history_dashboard/test_analysis/__init__.py` (new, to be created).
- `tests/unit/tools/git_history_dashboard/test_analysis/test_analysis_tdd.py` (new, to be created).
- `tests/unit/tools/git_history_dashboard/test_render/test_render_tdd.py` (existing from Step 1, to be updated) -- assert the two new tokens fill.

**Tests first**:

- `test_analysis_tdd.py`: the generated file is rewritten from the figures on each run; a pre-existing `analysis.notes.<project>.md` is left byte-for-byte unchanged; a missing per-project notes file is created once with a stub; the concatenation order is generated then per-project notes in project order; the conversion seam is monkeypatched so the unit test needs no `markdown` package.
- `test_render_tdd.py` (update): `render` fills `__ANALYSIS__` and `__TITLE__`; the rendered HTML carries no my-project string; a single project yields its name as the title, several yield the project-count label.

**Classes and behavior**:

- `write_generated_analysis(payload, path)`: the one-story figures (narrative through the run day, type leader, hour and weekday peaks, top scopes) as markdown.
- `ensure_notes(project, dir)`: create `analysis.notes.<project>.md` once if absent with a stub; never overwrite an existing one.
- `analysis_html(generated_path, notes_paths)`: concatenate the generated file then the per-project notes in project order, then convert through the uv-backed `markdown` seam.
- `convert_markdown(md)`: the single seam that shells to `uv run --with markdown python -c ...`; monkeypatched in tests (Q03).
- `render.py` tokens: `__ANALYSIS__` and `__TITLE__` join the substitution table.

**Completion criteria**:

- `ghog day` reports the objective (`exit=0`).
- `rg -n "my-project" tools/git_history_dashboard/template.html` returns nothing.
- `rg -n "__ANALYSIS__|__TITLE__" tools/git_history_dashboard/template.html tools/git_history_dashboard/render.py` shows the slots and their tokens.

#### Step 3 -- addendums for the analysis and template

Line-budget checkpoint:

- `tools/git_history_dashboard/analysis.py`: before 0 -> target <= 320.
- `tools/git_history_dashboard/render.py`: before <=120 -> target <= 160 (two tokens added).
- `tools/git_history_dashboard/build.py`: before <=360 -> target <= 420 (analysis write and title wiring).
- `tools/git_history_dashboard/template.html`: before 542 -> watch; the observations content leaves and the slots are small, so the net change is near flat (not a Python budget item).
- `test_analysis_tdd.py`: before 0 -> target <= 300. `test_render_tdd.py`: target <= 240.

Split guidance:

- If `analysis.py` nears 550, move the figures-to-markdown text builder into `analysis_text.py`, keeping the file IO and the conversion seam in `analysis.py`.

Full workflow timing run readiness:

- `ghog single tools/git_history_dashboard/analysis.py tools/git_history_dashboard/render.py tests/unit/tools/git_history_dashboard/test_analysis tests/unit/tools/git_history_dashboard/test_render`

Time-gated status for Step 3:

- No perf gate affected.

---

### Step 4. Dashboard front-end: project filter, contributor leaderboard, theme toggle, recompute-all filtering

#### Step 4 -- analysis and intent for the front-end

Issues to address:

- The page reads fixed top-level arrays; only the weekly chart reacts to the type chips. There is no project filter, no contributor list, and no theme toggle.

Fix intent:

- Generalize the client logic to a single recompute that, on any filter change (date range, type set, project set), sums the visible `by_project` slices and redraws every widget and the metric cards.
- Add a project-chip filter mirroring the type chips; a date-range control; a top-10 contributor list from `by_author`, recomputed with the project filter; a two-state light/dark toggle with a `data-theme` override read from storage before first paint, falling back to `prefers-color-scheme`.

Expected outcome:

- Hiding a project recomputes every widget and the leaderboard; narrowing the date range recomputes the charts and metrics while the leaderboard stays all-time; the theme toggle flips and is remembered.

Step framing:

- Design link: Design Area 2 (in-page filtering), Design Area 3 (leaderboard), Design Area 5 (theme), design Q02, Q03, Q06, Q09.
- Execution checklist reference: Shared execution command checklist for all v0.8.0 git-history report steps.

#### Step 4 -- implementation for the front-end

**Files involved**:

- `tools/git_history_dashboard/template.html` (existing, to be updated) -- the filter controls, the leaderboard section, the toggle, and the recompute loop in the inline script.
- `tests/unit/tools/git_history_dashboard/test_render/test_render_tdd.py` (existing, to be updated) -- assert the new markup is present and wired to the payload keys.

**Tests first**:

- Extend `test_render_tdd.py`: the rendered HTML contains the project-filter container, the contributor list container, the date-range control, and the theme-toggle control; the inline script references `by_project`, `by_author`, and a `data-theme` override; a single-project payload still renders the project filter with one entry.
- Note: the recompute logic is client-side JavaScript with no Python harness in this repo; its behavior is validated by the markup-and-wiring assertions here and by the acceptance step's rendered-output checks. State this limit plainly rather than implying JS unit coverage.

**Classes and behavior**:

- `applyFilters()`: sum the visible `by_project` series across the selected projects, types, and date window; redraw the timeline, calendar, weekday, hour, scope, recent, metric, and contributor widgets.
- The project chips and the date-range control call `applyFilters()`; the contributor list recomputes from `by_author` for the visible projects (all-time, not date-bound).
- The theme toggle writes `data-theme` to storage and flips the attribute; first paint reads storage, else the media query.

**Completion criteria**:

- `ghog day` reports the objective (`exit=0`).
- `rg -n "applyFilters|data-theme|by_author" tools/git_history_dashboard/template.html` shows the recompute, the theme override, and the leaderboard wiring.
- A rendered sample page (from the test) contains all four new controls and sections.

#### Step 4 -- addendums for the front-end

Line-budget checkpoint:

- `tools/git_history_dashboard/template.html`: before ~542 -> expected well over 650 after the front-end. This is an HTML file, not a Python file, so it does not trip the Python big-file rule. Record the size; do not split the JS out (it would break the single-static-file property). A future template-partials assembly is the deferred split, not part of this plan.
- `test_render_tdd.py`: keep <= 360 after the additions.

Split guidance:

- Deferred: a later phase can assemble `template.html` from partials at build time. Do not force it here.

Full workflow timing run readiness:

- `ghog single tools/git_history_dashboard/template.html tests/unit/tools/git_history_dashboard/test_render`

Time-gated status for Step 4:

- No perf gate affected; the client recompute is O(projects x buckets), not O(commits).

---

### Step 5. The skill, the README, and acceptance tests

#### Step 5 -- analysis and intent for the skill and acceptance

Issues to address:

- There is no user-facing skill, the README still describes the single-repo tool, and nothing validates the whole flow end to end.

Fix intent:

- Add `.claude/skills/git-history-report/SKILL.md` and `instructions/git-history-report.md`: resolve targets, call `build.py` with the right flags, and describe the keep-the-notes analysis workflow.
- Update the README for the multi-repo run, the `--out-dir` rule, the analysis files, and the in-page filters.
- Add acceptance tests that build a real multi-repo report from throwaway repos and assert the whole chain.

Expected outcome:

- The skill drives a combined report; the acceptance tests prove the payload shape, the filled slots, the analysis round-trip, the suppress flag, and the project-neutral title.

Step framing:

- Design link: all design areas; the feature-request outcomes 1 to 5.
- Execution checklist reference: Shared execution command checklist for all v0.8.0 git-history report steps.

#### Step 5 -- implementation for the skill and acceptance

**Files involved**:

- `.claude/skills/git-history-report/SKILL.md` (new, to be created).
- `instructions/git-history-report.md` (new, to be created).
- `tools/git_history_dashboard/README.md` (existing, to be updated).
- `tests/unit/tools/git_history_dashboard/test_report_acceptance/__init__.py` (new, to be created).
- `tests/unit/tools/git_history_dashboard/test_report_acceptance/test_report_acceptance_tdd.py` (new, to be created).

**Tests first**:

- `test_report_acceptance_tdd.py` (larger than unit; builds throwaway git repos under `tmp_path` with real `git`): a two-repo `--out-dir` run writes one `data.json` whose payload has `projects` (both), `by_project` (summing to the top-level series), and `by_author`; the `dashboard.html` has the filled `__ANALYSIS__` and `__TITLE__` slots and no my-project string; `analysis.notes.md` survives a second run unchanged while `analysis.generated.md` refreshes; `--no-open` writes the report without calling the opener.

**Classes and behavior**:

- `SKILL.md` and `instructions/git-history-report.md`: the user-facing entry; resolve targets, invoke `build.py`, and run the analysis keep-the-notes workflow; no new Python behavior.
- The acceptance test reuses the throwaway-repo helper pattern already in `test_git_history_dashboard_build.py`.

**Completion criteria**:

- `ghog day` reports the objective (`exit=0`).
- `rg -n "git-history-report" .claude/skills instructions` shows the skill and its instruction.
- The acceptance test builds, asserts the payload and the slots, and proves the analysis round-trip and the suppress flag.

#### Step 5 -- addendums for the skill and acceptance

Line-budget checkpoint:

- `instructions/git-history-report.md`: before 0 -> target <= 200.
- `tools/git_history_dashboard/README.md`: before 85 -> target <= 180.
- `test_report_acceptance_tdd.py`: before 0 -> target <= 320.

Split guidance:

- If the acceptance file nears 320, move the throwaway-repo builder into a shared `conftest.py` under the new test subpackage.

Full workflow timing run readiness:

- `ghog single tests/unit/tools/git_history_dashboard/test_report_acceptance`

Time-gated status for Step 5:

- No perf gate affected; the Step 0 gate remains green from Step 1.

---

## Implementation decisions for v0.8.0 git-history report

The plan review settled six points (plan Q01 to Q06). Each row names the question, the choice, why it won, the alternatives turned down, and where it lands. These are implementation choices; the design and the feature scope are fixed in the upstream documents.

| Question | Choice | Why | Rejected | Integrated in |
| --- | --- | --- | --- | --- |
| Q01 | Adopt the nested `test_<name>/test_<name>_tdd.py` convention and relocate the existing flat build test into the subpackage | One consistent test layout; the dashboard tests sit together under the convention | A1 flat files; A3 a flat subpackage | Step 0; test-tree snapshot |
| Q02 | A `Commit` NamedTuple with a `project` field | Named access reads clearly in the mixed-repo aggregation | B1 a five-slot tuple; B3 a parallel per-repo value | Step 1.1 |
| Q03 | A `convert_markdown` seam in `analysis.py` that shells to `uv run --with markdown` | Keeps `build.py` runnable as bare `python build.py`; confines the dependency; a clean test seam | C2 run the whole build under uv; C3 a separate helper script | Step 3 |
| Q04 | Split Step 1 into a pure extraction (Step 1) and the data-model extension (Step 1.1) | The risky project and author math is isolated in its own diff after a green move | D1 one combined step | Steps 1 and 1.1 |
| Q05 | Extract `render` into a `render.py` module | `build.py` stays a thin hub; the render test leaf names a `render.py` | E1 keep `render` in `build.py` | Step 1; Step 3 |
| Q06 | One hand-written notes file per project (`analysis.notes.<project>.md`) | Each project's notes are editable in isolation, no in-file section merge | F1 one file with per-project headings; F3 a single blank stub | Step 3; runtime file note |

These decisions reshaped the step list (the new Step 1.1, the `render.py` module, and the per-project notes), and the validation skeleton was realigned so each `Analysis of Step N` section still matches a plan step.

This plan stays at implementation level only: files, tests, commands, budgets, rollout order, and completion checks. The design choices are fixed in `docs/design.v0.8.0.git-history-report.md`; this document does not reopen them.
