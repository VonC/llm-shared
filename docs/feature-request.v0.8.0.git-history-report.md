# Commit and Tell: a git-history report skill for any project

- Type: feature-request
- Version: v0.8.0
- Topic: git-history-report

## CDC revision that introduces the git-history report skill

Today the `git_history_dashboard` tool already runs against the calling
project. `build.py` resolves that project's root, exports the commit log,
aggregates it, and writes a standalone `dashboard.html` next to a raw
`data.json`. What is missing is a skill that drives this tool end to end for any
project, a clean split between the generated data and the hand-written analysis,
and a few report features (a theme toggle, date and type filtering, a
contributor summary).

The request: a skill that creates or updates the git-history report for one or
several projects in a single run, by running `build.py` for each and writing one
combined dashboard the reader can filter by project. It refreshes a separate
analysis file with the latest observations, and opens the result in the default
browser unless told not to. The analysis text must leave `template.html` and live
in its own file the skill rewrites after each run, so the template keeps only the
shell and a slot that pulls in the current analysis.

## Current behavior of the dashboard tool in v0.8.0

- `build.py` resolves the calling project root through `find_project_root` (which prefers the `PRJ_DIR` variable each project's `senv.bat` exports), runs `git log --all --pretty=format:%H|%ai|%an|%s --date-order`, and writes a git-ignored `git_history.csv` under `<project>/docs/git_history_dashboard/`.
- It aggregates commits by day, week, type, scope, weekday, and hour, then renders `dashboard.html` and `data.json` into the same folder. It already accepts `--git-dir`, `--csv`, `--out-dir`, and `--template`, has no third-party dependencies, and pulls Chart.js from cdnjs at view time.
- The author field is parsed but dropped (the `_author` slot in `_record_commit`), so there is no per-author tally and no contributor summary in the payload.
- `template.html` holds the static HTML shell, the placeholder tokens that `render` fills (`__DATA__`, `__TOTAL_COMMITS__`, `__START__`, and the rest), and a hand-written observations block that `build.py` never generates. That block currently describes my-project's numbers.
- Each invocation targets a single repository (`--git-dir`, or the calling project); there is no multi-project run and no per-commit project label.
- Nothing drives the run as a skill, nothing opens the dashboard after a build, the page ships a single light theme, and `data.json` is not filtered by date range or commit type.

## Gap to close for the git-history report skill

1. A new skill that creates or updates the report for one or several projects in a single run (Q01): it takes one or more project paths, defaults to the current project when none is given, runs the export and build for each, and writes one combined dashboard. A multi-project run names its output folder with `--out-dir`; a single-project run keeps the current `<project>/docs/git_history_dashboard/` default (Q07). It logs any error during export, build, or render, and prints a summary of the actions it took.
2. Move the analysis out of `template.html` into a separate analysis file (Q03). The template keeps the shell and a slot that includes the latest analysis; the skill rewrites that file after each run, refreshing the computed figures while keeping a marked hand-written section across runs. Across a multi-project run the charts and the computed figures combine into one story for the whole run, and the in-page project filter lets the reader focus on one or more repos; only the hand-written section keeps a per-project note (Q08).
3. Refresh the observations from the new data (Q03, Q08): extend the time narrative through the day it runs, correct the commit-type story, check the busiest hour and weekday, and refresh the top scopes, computed across all projects in the run. The numbers in the draft are illustrative; each run computes them from the target projects.
4. A white/dark mode toggle on `dashboard.html` that follows the machine setting on first load and remembers a manual flip (Q06).
5. In-page filtering of the rendered report by date range, by commit type (feat, fix, docs, test, refactor, chore), and by project (Q04, Q01), so the reader can hide one or more projects without a re-run.
6. A top-contributors summary that counts by author name, all-time, top 10 (Q05), as one combined leaderboard that re-counts as the in-page project filter hides or shows repos (Q09). This needs `build.py` to aggregate the author field it drops today.
7. The skill opens `dashboard.html` in the default browser after the report is created or updated, unless a suppress flag is passed (Q02).

## Acceptance checks for the git-history report skill

- Running the skill with one or more project paths, or none for the current project, writes `dashboard.html` and `data.json` and opens `dashboard.html` in the default browser unless suppressed.
- A multi-project run writes the combined report to the `--out-dir` it was given; a single-project run keeps the `<project>/docs/git_history_dashboard/` default.
- The charts and the computed figures combine every project in the run into one story; the in-page project filter narrows the view to one or more repos.
- `template.html` no longer carries project-specific analysis text; the analysis lives in its own file the skill rewrites on each run, keeping a marked hand-written section with a per-project note.
- The dashboard offers a light/dark toggle that starts from the machine setting and remembers a manual flip.
- The rendered report can be filtered by date range, by commit type, and by project.
- The skill produces a single top-contributors list by author name, all-time, top 10, that re-counts with the project filter.
- Errors during export, build, or render are logged, and the run ends with a summary of the actions taken.

## Code references for the git-history report skill

- `tools/git_history_dashboard/build.py`: exports the git log, aggregates by day/week/type/scope/weekday/hour, and renders `dashboard.html` plus `data.json`; already project-generic; drops the author field today.
- `tools/git_history_dashboard/template.html`: the HTML shell, the `__...__` placeholder tokens, and the hand-written observations block to move out.
- `tools/git_history_dashboard/README.md`: the tool's current usage notes, to update for the skill and the split analysis file.
- `tools/__init__.py` (`find_project_root`): resolves the calling project root from `PRJ_DIR`, the seam the skill reuses to target any project.

## File-based IO cost for the git-history report skill

The skill is a one-shot build, not a service, so its file work stays small and predictable.

- One git-history export per project, into the git-ignored scratch file, read back once.
- The report files (`dashboard.html`, `data.json`) and the analysis file are each written once per run.
- Opening the report is a plain static-file read; the page does no work at view time beyond loading Chart.js from the CDN.

## Requirement clarifications for the git-history report skill

The review settled nine points (Q01 to Q09). Each row names the question, the choice made, why it won, the alternatives turned down, and where it lands in this document.

| Question | Choice | Why | Rejected | Integrated in |
| --- | --- | --- | --- | --- |
| Q01 | One or several project paths in one run; default to the current project; one combined dashboard with a per-project filter | Widest "any project" reach, sweeps a portfolio in one command, keeps a current-project default | A1 current project only; A2 single path only | Gap item 1; acceptance checks |
| Q02 | Open the dashboard by default, with a flag to keep it shut | Keeps the interactive default without the Windows browser-hang in scripts and CI | B1 always open; B3 never open | Gap item 7; acceptance checks |
| Q03 | Refresh the computed figures, keep a marked hand-written section across runs | The numbers stay current while a maintainer's notes survive a re-run | C1 full rewrite each run; C3 a new dated file each run | Gap items 2 and 3; acceptance checks |
| Q04 | In-page filtering by date range, commit type, and project | Matches where the draft puts the filter, with no extra build step | D2 generation-time bound; D3 both | Gap item 5; acceptance checks |
| Q05 | Top contributors by author name, all-time, top 10 | Uses the author field the export already carries, a short readable list | E2 folded identity; E3 the full raw list | Gap item 6; acceptance checks |
| Q06 | Theme follows the machine setting on first load and remembers a manual flip | Opens in the reader's usual mode and keeps their choice | F1 light only; F3 dark only | Gap item 4; acceptance checks |
| Q07 | A multi-project run names its output folder with `--out-dir`; a single project keeps the current default | An explicit home for a combined report, out of any one repo, reusing the existing flag | G2 the first project's folder; G3 a fixed working-directory folder | Gap item 1; acceptance checks |
| Q08 | Combine the charts and computed figures into one story for the whole run; keep only a per-project hand-written note | The project filter already lets the reader focus, so one combined story reads better than blended-or-split prose | H1 a narrative per project; H3 a combined headline plus per-project notes | Gap items 2 and 3; acceptance checks |
| Q09 | One combined top-10 leaderboard that re-counts as the project filter changes | Keeps the leaderboard in step with the in-page filter and still gives one overall list | I2 a frozen combined list; I3 a list per project | Gap item 6; acceptance checks |

The three follow-up points the multi-project choice opened (Q07 to Q09) are settled in the rows above: a combined run names its output folder, the charts and figures combine into one story the project filter can narrow, and the contributor list is one filter-aware leaderboard.
