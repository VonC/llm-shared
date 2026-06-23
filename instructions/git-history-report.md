# git-history-report instruction

Build one standalone HTML commit-history dashboard for one or several project
working trees, then follow the keep-the-notes analysis workflow. This is the
full workflow behind the `git-history-report` skill.

## Goal for the git-history report

From the repo paths the user gives (or the current project when none), produce a
single self-contained `dashboard.html` plus its `data.json`, with the commit
history aggregated by day, week, conventional-commit type, scope, weekday, hour,
author and project. The page carries in-page project, type and date-range
filters, a contributor leaderboard, and a remembered light/dark toggle.

## Resolve the targets

The number of repo paths decides the run:

| Paths given | Targets | Output folder |
| --- | --- | --- |
| none | the current project (via `PRJ_DIR`) | `<project>/docs/git_history_dashboard/` |
| one | that repo | that repo's `docs/git_history_dashboard/` |
| several | a combined run over all of them | the required `--out-dir` |

A multi-project run without `--out-dir` is rejected, so the combined report never
lands inside one of the repos.

## Run the build

Call `build.py` with the resolved targets. It delegates to `cli.py`, which
exports each repo with `git log`, tags every commit with its project, aggregates
the combined history, writes the analysis files, renders the dashboard, and opens
it in the browser unless `--no-open` is passed.

For one or several repositories, naming the output folder:

```text
python <llm-shared>/tools/git_history_dashboard/build.py ../alpha ../beta --out-dir /tmp/report
```

For the current project, into its default folder:

```text
python <llm-shared>/tools/git_history_dashboard/build.py
```

Pass `--no-open` for a script or CI run so it never blocks on a browser, and
`--csv` to rebuild from a pre-exported pipe-separated history without re-running
`git log`.

## Keep-the-notes analysis workflow

Each run writes two kinds of analysis file into the output folder:

- `analysis.generated.md` is rewritten from the figures on every run. Never hand
  edit it; the next build overwrites it.
- `analysis.notes.<project>.md` is created once per project with a stub, then
  left alone. A rebuild never overwrites it, so this is where hand-written
  commentary lives. Edit it to add context for that project.

The dashboard's analysis block is the generated file followed by each
per-project notes file, in project order, converted to HTML. The conversion
shells to `uv run --with markdown`, so `uv` is needed at build time.

## Output files for the report

| Output | Versioned? | Why |
| --- | --- | --- |
| `dashboard.html` | yes | the rendered, self-contained dashboard |
| `data.json` | yes | the aggregated payload the page reads |
| `analysis.generated.md` | yes | the auto-generated observations, rewritten each run |
| `analysis.notes.<project>.md` | yes | hand-written commentary, kept across runs |
| `git_history.csv` | no (git-ignored) | the scratch `git log` export |

## What the rendered page offers

- A project-chip filter, a type-chip filter, and a date-range control; changing
  any of them recomputes every widget and the metric cards by summing the visible
  per-project series.
- A top-10 contributor leaderboard from the author tally, recomputed with the
  project filter (all-time, not date-bound).
- A light/dark toggle that writes `data-theme` to storage and is read before the
  first paint, falling back to the OS `prefers-color-scheme`.

## Hand-off note for the report

The rendered `dashboard.html`, `data.json`, and the analysis files are meant to
be committed in the output folder so the project's history snapshots are recorded
over time. The `git_history.csv` export is scratch and matches the git-ignore
rule.
