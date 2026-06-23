# Design v0.8.0 -- Commit and Tell git-history report

Reference feature-request: [feature-request.v0.8.0.git-history-report.md](feature-request.v0.8.0.git-history-report.md)

---

## Context for v0.8.0 git-history report

The feature-request settled nine points (Q01 to Q09). This design turns those
decisions into design areas. The `git_history_dashboard` tool already runs
against any single project; the v0.8.0 work wraps it in a skill, gives the data
a project dimension so one combined dashboard can cover several repos, adds
in-page filtering and a contributor leaderboard, splits the hand-written
analysis out of the template, and adds a theme toggle. No new behavior is
designed beyond what the feature-request lists.

## Scope for v0.8.0 git-history report

The v0.8.0 outcomes are:

1. A skill builds or updates one combined report for one or several projects in a single run, writes it to a chosen output folder, and opens it in the browser unless told not to.
2. The dashboard data carries a project dimension, and every chart recomputes under a date-range, a commit-type, and a project filter.
3. A single top-10 contributor leaderboard by author name, recomputed as the project filter changes.
4. The hand-written analysis leaves `template.html` for two markdown files the skill combines at build time: a generated-figures file refreshed each run, and a hand-written note file kept across runs.
5. A light/dark toggle that starts from the machine setting and remembers a manual choice.

Everything else is either supporting design context for those outcomes or explicitly deferred.

### In scope for v0.8.0 git-history report

- A project label on every commit, so the combined payload can break each series down per project.
- One combined dashboard page (charts, metrics, scopes, recent, contributors) summing the projects in the run, with the in-page project filter to narrow the view.
- A per-author tally added to the aggregation, feeding a filter-aware top-10 leaderboard.
- Two markdown analysis files, a generated-figures file (rewritten each run) and a hand-written note file (kept across runs), combined and converted to HTML at build time.
- A theme override layered on the existing `prefers-color-scheme` styling.
- Skill orchestration: target resolution, output destination, browser open with a suppress flag, per-phase error logging, and a run summary.

### Deferred from v0.8.0 git-history report to v0.9.0 and beyond

- Folding one contributor's several names or emails into a single identity (the feature-request kept name-based counting).
- Generation-time bounding of the report by window or type (the feature-request kept in-page filtering only).
- One dashboard per project, or a per-project narrative (the feature-request kept one combined page and one combined story).
- A contributor count that follows the date slider (design Q03 kept the leaderboard all-time; see Design Area 3).

---

## Confirmed Technical Facts for v0.8.0 git-history report

These facts were confirmed by inspecting the current codebase before writing this design.

**`build.py` is already project-generic**: it resolves the calling project through `find_project_root` (honoring `PRJ_DIR`), accepts `--git-dir`, `--csv`, `--out-dir`, and `--template`, has no third-party dependencies, and the rendered page pulls Chart.js from cdnjs at view time. The multi-project work extends this rather than replacing the targeting.

**The author is exported but dropped**: the export uses `%an`, and `iter_commits_from_csv` carries the author into the commit tuple, but `_record_commit` ignores it (the `_author` slot). The data needed for a contributor tally is already present; only the aggregation is missing.

**Rendering is placeholder substitution**: `render` replaces `__DATA__`, `__TOTAL_COMMITS__`, `__START__`, `__END__`, and the metric tokens in `template.html`. Adding an analysis slot and a title slot fits the same mechanism, so no new templating engine is needed.

**The payload is pre-aggregated and inlined**: `aggregate` builds one flat `DashboardData` (daily and weekly series, `by_type`, `by_scope`, `by_hour`, `by_weekday`, and a 10-row `recent`), serialized into `<script id="git-data">` and parsed at load. There is no project dimension, no per-author tally, and no per-commit rows beyond `recent`.

**Dark mode follows the OS but cannot be toggled**: the template defines light variables under `:root` and dark variables under `@media (prefers-color-scheme: dark)`, with `color-scheme: light dark`. There is no control to override the machine setting and nothing remembers a choice.

**Filtering is partial today**: a type-filter chip UI exists, but its handler only rebuilds the weekly timeline chart. The calendar heatmap, weekday chart, hour chart, scope pills, and metric cards read fixed arrays and do not react to it. Generalizing filtering to recompute every widget is new work.

**The template is my-project-specific in more than the observations**: the `<title>`, the header `<h1>`, the `sr-only` description, the hand-written `observations` section, and the footer command are all hardcoded for my-project. Making the report project-neutral covers all of these, not only the observations block.

**A markdown-to-HTML path already exists, but it pulls third-party packages**: `a.md2pdf.py` converts Markdown with the `markdown` package and renders with `xhtml2pdf`, both brought in on the fly through `uv run --with ...` rather than vendored. The repo has a working markdown conversion, but it is a build-time dependency, which bears on how the analysis markdown becomes HTML (design Q07).

---

## Current Behavior for v0.8.0 git-history report

A single-repository run today:

```txt
export_git_history_csv(repo) -> git_history.csv
  -> iter_commits_from_csv -> aggregate (one flat payload, author dropped)
  -> render(payload, template.html)  [placeholder substitution]
  -> write data.json + dashboard.html into <project>/docs/git_history_dashboard/
```

The page parses the inlined payload and draws fixed charts; only the weekly
timeline reacts to the type chips.

## Target Behavior for v0.8.0 git-history report

A run over one or several repositories:

```txt
skill: resolve targets (none -> current project; one -> that repo; several -> combined, --out-dir required)
build.py multi-repo mode:
  for each repo: export -> parse -> tag every commit with its project
  -> one combined aggregate (top-level series for the default view + a by_project breakdown)
  -> write the generated analysis markdown from the figures; leave the hand-written analysis markdown untouched
  -> convert both analysis files to HTML, fill the data, title, and analysis slots
  -> write data.json + dashboard.html into the output folder
skill: open dashboard.html in the browser unless suppressed; log per-phase errors; print a run summary
```

In the page, the default view sums all projects across the full date range and
all types -- one combined story. The date-range, commit-type, and project
filters narrow that view and recompute every widget.

---

## File-based IO cost clarification for v0.8.0 git-history report

The report build is a one-shot offline operation, and the rendered page is
static, so IO stays bounded and off any response path.

- One `git log` per repo, writing the git-ignored scratch CSV, read back once; no directory scan.
- `data.json` and `dashboard.html` are written once each; the analysis markdown is read once and the generated file written once.
- Loading the report is a tiny static-file read: the data is inlined and only Chart.js loads from the CDN, so there is no metadata-loading delay at view time.

---

## Design Area 1 for v0.8.0 git-history report: project-tagged data model

### Commit-level project tag

Every commit gains a project label, set to the project the export came from. A
single-repo run tags all commits with that one project; a combined run tags each
commit with its own repo. This label is the key the page filters on. `build.py`
gains a native multi-repo mode that takes the run's repos, applies this tag as it
parses each one, and aggregates them into the one combined payload; the skill
orchestrates and does not re-sum per-repo output (design Q01).

### Combined payload with a per-project breakdown

The payload keeps its current top-level series as the all-projects default view,
so the first paint needs no client computation. It adds:

- `projects`: the ordered list of project names in the run.
- `by_project`: a map from project name to that project's own sub-aggregate (daily totals and `by_type_day`, the weekly series, `by_type`, `by_scope`, `by_hour`, `by_weekday`, a new `by_author`, and its `recent` rows).

The page derives any filtered view by summing the `by_project` entries for the
selected projects. The top-level series equal the sum over all projects, so the
unfiltered page matches `by_project` summed across everything. A single-project
run has one entry in `projects` and one in `by_project`, and behaves as today.

### Size trade-off for the per-project breakdown

The payload grows roughly linearly with the project count, since each project
carries its own series. For the handful of repos a portfolio run covers this is
acceptable, and it keeps every filter client-side. Shipping per-commit rows
instead was rejected: it bloats `data.json` on large repos and duplicates what
the aggregates already summarize.

## Design Area 2 for v0.8.0 git-history report: in-page filtering across all widgets

### Three filters over one visible slice

The page holds three filters: a date range, a set of enabled commit types, and a
set of visible projects. The visible slice is their intersection. Every widget
-- the metric cards, the weekly timeline, the calendar heatmap, the weekday and
hour charts, the scope pills, the recent list, and the contributor leaderboard
-- redraws from that slice. This generalizes today's behavior, where only the
weekly timeline reacts to the type chips.

### Combined-by-default, narrowed on demand

With no filter touched, the slice is all projects, all types, and the full date
range: the single combined story chosen in Q08. Hiding a project subtracts its
series from every widget; the project filter is what lets a reader focus, which
is why the figures stay combined rather than split per project.

### Date-range filtering over the daily grain

The date filter works on the daily series (and the day-keyed `by_type_day`),
which already exist per project. The weekly chart and the metric cards recompute
from the days inside the window. The commit-type filter selects type series; the
project filter selects `by_project` entries. All three compose without a re-run.

## Design Area 3 for v0.8.0 git-history report: contributor leaderboard

### One filter-aware list

The aggregation stops dropping the author and builds a per-project `by_author`
count. The page shows one top-10 list by author display name, summed across the
visible projects, recomputed when the project filter changes (Q09). Name-based
counting is the chosen rule; folding several names into one identity is deferred.

### Leaderboard window rule

Q05 fixed the leaderboard as all-time and Q09 made it follow the project filter.
To hold both without shipping per-day author data, the leaderboard follows the
project filter but not the date slider: it counts every commit of the visible
projects across the whole history. This keeps the per-author data to a small
per-project total and matches "all-time, recomputed by project". A
date-windowed leaderboard is listed as deferred.

## Design Area 4 for v0.8.0 git-history report: analysis files and template slot

### Splitting the analysis out of the template

The hand-written `observations` content leaves `template.html`. The template
keeps the section shell and an analysis slot (a placeholder the render step
fills, in the same style as the existing tokens). The analysis lives outside the
template and is fed into the slot at render time, so the template no longer
carries any project text.

### Two markdown files, one refreshed and one kept

The analysis lives in two markdown files (design Q04, Q05):

- a generated file, rewritten on every run from the latest combined data: the time narrative through the run day, the commit-type leader, the busiest hour and weekday, and the top scopes, all computed across the projects in the run.
- a hand-written file, never opened by the refresh, holding a per-project note for any commentary a maintainer adds.

At render the two files are concatenated, generated first then hand-written,
converted to HTML, and dropped into the analysis slot. Because the refresh
overwrites only the generated file and never touches the hand-written file, a
maintainer's notes cannot be lost while the figures stay current (Q03, Q08).
Keeping the two in separate files, rather than two regions of one file, means
there is no marker for a careless edit to break (design Q05).

### Converting the markdown without a viewer dependency

The rendered `dashboard.html` stays static and free of any third-party
dependency: the markdown becomes HTML at build time, not in the browser (design
Q04). That conversion reuses the `uv run --with markdown` pattern already used by
`a.md2pdf.py`, so it runs as its own uv-backed build step with full markdown, and
the directly-run `build.py` stays import-clean. A vendored pure-Python converter
is the fallback only if the no-dependency property must be strict (design Q07).

## Design Area 5 for v0.8.0 git-history report: theme toggle

### An override on top of the machine setting

The styling keeps its `prefers-color-scheme` defaults. The design adds an
explicit theme override carried on the root element and a visible toggle. The CSS
variables apply for either an override value or, when no override is set, the
media query. First load reads a stored choice if present, otherwise it falls
through to the machine setting (Q06).

### Remembering the choice

A manual flip writes the chosen theme to browser storage; the next visit reads it
back before first paint, so the report opens in the reader's last choice. With no
stored choice, the machine setting still wins, so a first-time reader sees their
usual mode.

## Design Area 6 for v0.8.0 git-history report: skill orchestration

### Target resolution and output destination

The skill resolves its targets from the paths it is given: none means the current
project (via `PRJ_DIR`), one means that repo, and several mean a combined run. A
single-project run keeps the current `<project>/docs/git_history_dashboard/`
default output folder; a multi-project run names its output folder with
`--out-dir`, so the combined report does not land inside any one repo (Q01, Q07).

### Browser open and the suppress flag

After writing the report the skill opens `dashboard.html` in the default browser.
A suppress flag keeps it shut for a script, a hook, or CI, which avoids the
Windows browser-hang the v0.7.0 activity-report work already chose to avoid
(Q02).

### Error logging and run summary

Each phase -- export, build, render, and open -- is logged. When one repo's
export or parse fails, the skill reports it, skips that repo, and notes the skip
in the summary rather than aborting the whole run. The run ends with a summary:
the projects processed, the commit counts, the output path, and whether the
browser was opened or suppressed.

## Design Area 7 for v0.8.0 git-history report: a project-neutral template

### Parameterizing the my-project strings

The hardcoded my-project strings (the `<title>`, the header `<h1>`, the
`sr-only` description, and the footer command) become slots the render step
fills. The header names the subject of the report: the single project name for a
one-repo run, or a combined label such as the project count for a portfolio run.
This removes the last project-specific text from the template, alongside the
observations moved out in Design Area 4.

---

## Acceptance Cases for v0.8.0 git-history report

| Scenario | Expected outcome | Reason |
| --- | --- | --- |
| `skill` with no path | builds the current project's report in its default folder and opens it | default targeting (Q01) |
| `skill repoA repoB --out-dir X` | one combined report in `X`; the project filter lists both repos | combined multi-project run (Q01, Q07) |
| `skill repoA repoB` with no `--out-dir` | the run stops and asks for an output folder | a combined report must not land in one repo (Q07) |
| `--no-open` in a non-interactive run | the report is written, no browser opens | safe for scripts and CI (Q02) |
| hide one project on the page | every widget and the leaderboard recompute without that repo | combined, project-filtered view (Q08, Q09) |
| narrow the date range | charts and metric cards recompute; the leaderboard stays all-time | in-page date filter; leaderboard window rule (Q04, Q05) |
| re-run after editing the hand-written notes | the figures region refreshes; the notes are kept | analysis refresh contract (Q03, Q08) |
| toggle to dark, then revisit | the report opens in dark | remembered theme choice (Q06) |
| open with no stored theme on a dark machine | the report opens in dark | machine-setting default (Q06) |

---

## Design decisions for v0.8.0 git-history report

The design review settled seven points (design Q01 to Q07). Each row names the question, the choice, why it won, the alternatives turned down, and the design area where it lands. These are design choices; the feature scope is fixed by the feature-request, and the file-by-file work belongs to the later implementation plan.

| Question | Choice | Why | Rejected | Integrated in |
| --- | --- | --- | --- | --- |
| Q01 | `build.py` gains a native multi-repo mode; the skill is a thin orchestrator | One path produces the combined payload, with the project tag set at parse time | A2 merge per-repo JSON in the skill; A3 a shared module after a refactor | Design Area 1; Design Area 6 |
| Q02 | Per-project pre-aggregates plus the combined top-level series | Every filter is a sum of selected series; the payload stays small; fast first paint | B2 per-commit rows; B3 a hybrid index | Design Area 1; Design Area 2 |
| Q03 | The leaderboard follows the project filter, all-time over the date range | Honors both all-time and project-aware with the smallest data | C2 follow the date slider too; C3 a fixed board | Design Area 3 |
| Q04 | Markdown analysis files converted to HTML at build time | Notes stay editable in markdown while the rendered dashboard keeps no viewer dependency | D1 an HTML fragment; D3 a structured data block | Design Area 4 |
| Q05 | Two files: a generated file overwritten each run, a hand-written file never touched | The refresh never opens the notes file, so notes cannot be lost | E1 markers in one file; E3 a labelled-heading split | Design Area 4 |
| Q06 | A two-state light/dark toggle, the machine setting as the default | The lightest control, matching the feature answer | F2 a three-state light/dark/system control | Design Area 5 |
| Q07 | The build-time markdown-to-HTML conversion reuses the `uv --with markdown` pattern from `a.md2pdf.py` | Full markdown and a static dashboard, with the dependency confined to a uv build step | G2 a vendored pure-Python converter; G3 an inline regex subset | Design Area 4; confirmed facts |

With Q07 settled, the design carries no open question; the file-by-file work passes to the implementation plan.
