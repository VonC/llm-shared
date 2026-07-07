# How to build the git-history dashboard

<img src="../assets/logo-llm-shared-trail-transparent.png" alt="" height="90" align="right">

<!-- markdownlint-disable MD013 -->

📊 Goal: produce one standalone HTML dashboard of the commit history of
one or several repositories, with in-page filters and per-project analysis
notes.

## 📋 Steps to generate the dashboard

1. Pick the targets:

   - no path — the current project, output in
     `<project>/docs/git_history_dashboard/`,
   - one path — that repository, same per-repo output folder,
   - several paths — a combined report; `--out-dir` is then required.

2. Run the builder (or ask the agent for a "git-history report"):

   ```cmd
   ghd.bat <targets> [--out-dir <folder>] [--no-open] [--csv]
   ```

3. The tool exports each repo with `git log`, tags every commit with its
   project, aggregates by day, week, conventional-commit type, scope,
   weekday, hour, author and project, then writes the output folder and
   opens the dashboard in the browser (unless `--no-open`). `--csv`
   rebuilds from a pre-exported pipe-separated history.

## 📁 What lands in the output folder

| File | Role |
| --- | --- |
| `dashboard.html` | self-contained page: project, type and date filters, contributor leaderboard, light/dark toggle |
| `data.json` | the aggregated data the page reads |
| `analysis.generated.md` | regenerated on every run — never hand-edit |
| `analysis.notes.<project>.md` | one hand-editable file per project, created once, never overwritten |
| `git_history.csv` | scratch export, gitignored |

## 🗒️ Keeping your own notes

The generated analysis is rewritten each run; your reading of the history
belongs in `analysis.notes.<project>.md`, which the builder creates once
and then leaves alone. Commit the output folder: the dashboard is meant to
be shared.

## ✅ Check the dashboard

`dashboard.html` opens with the filters live and the leaderboard filled;
re-running the command refreshes `analysis.generated.md` but leaves your
notes file untouched.

Related: [Write an activity report](write-an-activity-report.md),
[skills catalog](../reference/skills-catalog.md).
