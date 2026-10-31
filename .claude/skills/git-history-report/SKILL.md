---
name: git-history-report
description: 'Build one standalone HTML commit-history dashboard for one or several project working trees. It exports each repo with git log, aggregates by day, week, type, scope, weekday, hour, author and project, and writes one data.json plus a self-contained dashboard.html with in-page project, type and date filters, a contributor leaderboard, and a light/dark toggle. It also writes a regenerated analysis.generated.md and one hand-editable analysis.notes.<project>.md per project (created once, never overwritten). With no path it reports the current project into <project>/docs/git_history_dashboard/; several paths require --out-dir and produce one combined report. Use when the user asks for a git-history report or a commit dashboard across one or more repos.'
user-invocable: true
argument-hint: 'Give the repo paths and an output folder, for example "git-history-report ../alpha ../beta --out-dir /tmp/report". With no path it reports the current project; several paths require --out-dir. Pass --no-open to keep the browser shut.'
---

[Instruction](../../../instructions/git-history-report.md)
