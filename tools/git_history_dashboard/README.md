# git_history_dashboard

A standalone, single-file HTML dashboard of commit history: weekly activity
stacked by conventional commit type, a GitHub-style daily heatmap, weekday and
hour-of-day distributions, a contributor leaderboard, top scopes, and the most
recent commits — with in-page project, type and date-range filters and a
light/dark toggle.

This tool is **shared**: it lives in `llm-shared` but builds the dashboard for
the **calling** project (or for whichever repos you point it at). With no path
it resolves the current project's root through the shared `find_project_root`
helper, which prefers the `PRJ_DIR` environment variable each project's
`senv.bat` exports — the same mechanism `git_batch_commit` uses. So it can be run
from any project, from any working directory.

## Modules of git_history_dashboard

| File | Role |
| --- | --- |
| `build.py` | Entry point and hub: the `git log` export, the CSV parse, `write_dashboard`, and `run_build`; `main` delegates to `cli.py`. |
| `cli.py` | Resolves one or several repo targets, runs the combined build, opens the page unless `--no-open`, and prints a run summary. |
| `aggregate.py` | The data model (`Commit`, `DashboardData`, `ProjectData`) and the per-day/week/type/scope/hour/weekday/author/project aggregation. |
| `render.py` | Substitutes the payload, the headline numbers, the title, and the analysis HTML into the `template.html` slots. |
| `analysis.py` | Writes `analysis.generated.md`, keeps each `analysis.notes.<project>.md`, and converts the combined analysis to HTML. |
| `template.html` | The project-neutral HTML template with `__TOKEN__` slots and the inline filter/recompute script. |
| `__init__.py` | Makes the folder an importable package for the test suite. |

## Where the report output goes

A single-project run writes into `<project>/docs/git_history_dashboard/`; a
multi-project run writes into the folder named by `--out-dir`:

| Output | Versioned? | Why |
| --- | --- | --- |
| `dashboard.html` | Yes | The rendered, self-contained dashboard. |
| `data.json` | Yes | The aggregated payload the page reads. |
| `analysis.generated.md` | Yes | The auto-generated observations, rewritten each run. |
| `analysis.notes.<project>.md` | Yes | Hand-written commentary, created once and kept across runs. |
| `git_history.csv` | No (git-ignored) | Pipe-separated `git log` export; a scratch artifact. |

## Run the report

The simplest single-project way is the `ghd` alias (defined in
`llm-shared/senv.doskey`, loaded by every project's `senv.bat`). It refreshes the
history export, rebuilds the dashboard, and opens it in the browser:

```text
ghd
```

Or call `build.py` directly. With no arguments it reports the current project:

```text
python <llm-shared>/tools/git_history_dashboard/build.py
```

Against one or several repositories, writing one combined report:

```text
python build.py /path/to/repo-a /path/to/repo-b --out-dir /tmp/report
```

From a pre-exported CSV (skips the `git log` call):

```text
python build.py --csv git_history.csv
```

A multi-project run must name `--out-dir`. Pass `--no-open` to keep the browser
shut (for scripts and CI), and `--template` to use a different HTML template.

## What the dashboard shows

- **Header metrics** — total commits, active-day ratio, peak day, peak week;
  these recompute as you filter.
- **Project / type / date filters** — chips for each project and each commit
  type, plus a week-indexed date range. Changing any of them recomputes every
  widget by summing the visible per-project series.
- **Weekly commit activity** — stacked bars per ISO week (Monday-anchored), one
  stack per commit type.
- **Daily activity** — a GitHub-style heatmap with five intensity buckets
  (0 / 1–3 / 4–7 / 8–15 / 16+).
- **By weekday / By hour of day** — twin distribution panels.
- **Top contributors** — a top-10 leaderboard from the author tally, recomputed
  with the project filter (all-time, not date-bound).
- **Top focus areas** — the 15 most-used conventional-commit scopes.
- **Most recent commits** — last 10 entries, type-coloured.
- **Light/dark toggle** — flips the theme and remembers it across visits via a
  `data-theme` override, falling back to the OS `prefers-color-scheme`.

## Analysis files of the report

The observations block is assembled, not hand-written in the template:

- `analysis.generated.md` is rewritten from the figures on every run — do not
  hand edit it.
- `analysis.notes.<project>.md` is created once per project with a stub and then
  left alone; a rebuild never overwrites it, so this is where hand-written
  commentary lives.

The two are concatenated (generated first, then each project's notes in order)
and converted to HTML for the page's analysis slot.

## Dependencies of the report

- **Build time:** Python 3.13 standard library plus the shared
  `tools.find_project_root` helper. The analysis conversion shells to
  `uv run --with markdown`, so `uv` is needed at build time; nothing else is.
- **View time:** any modern browser. Chart.js 4.4.1 is loaded from
  `cdnjs.cloudflare.com` at view time; everything else (data, layout, calendar
  heatmap, filters) is inlined into `dashboard.html`.

## How the commit data is parsed

Each commit subject is matched against the conventional-commit pattern
`<type>(<scope>)!: <subject>` to extract its type and scope. Unrecognised types
collapse into `other`. Each commit is tagged with the project it was exported
from, so every series can be broken down per project. The aggregation produces:

- a contiguous daily series (zero-filled), and a Monday-anchored weekly rollup
  keyed by ISO week start;
- per-type totals across the whole history and per day/week;
- top-15 scopes ranked by frequency;
- 24 hour-of-day buckets and 7 weekday buckets (Mon=0);
- the author tally and the per-project slices that sum back to the top level;
- the 10 most recent commits as `{sha, date, type, scope, msg, project}`.

If you change the type or scope conventions, edit `KNOWN_TYPES` and the regex
constants at the top of `aggregate.py`.
