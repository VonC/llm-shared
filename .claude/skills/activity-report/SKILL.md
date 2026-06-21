---
name: activity-report
description: 'In one invocation, build a.md (commit messages and Markdown diffs per git working tree over a date window, default end today) without reading the full codebase, then analyze it, present the topics for the user to select, ask for a few words of context, and write a French report a.activity-report.<start>-<end>.md at the project root for review. Use when the user asks for an activity report across one or more working trees.'
user-invocable: true
argument-hint: 'Give the start date and the working trees, for example "activity-report --start 2026-05-29 . ../pdfsplitter". End date defaults to today; override with --end YYYY-MM-DD.'
---

[Instruction](../../../instructions/activity-report.md)

Implementation is mutualized across the shared directories:

- [`../instructions/activity-report.md`](../../../instructions/activity-report.md)
  — the full end-to-end workflow.
- [`../templates/activity-elements.template.md`](../../../templates/activity-elements.template.md)
  — the structure of the generated `a.md` elements document.
- [`../templates/activity-report.french.template.md`](../../../templates/activity-report.french.template.md)
  — the structure of the French report.
- [`../scripts/activity_report.sh`](../../../scripts/activity_report.sh)
  — the git log / git diff script, run from the calling project root.

Inputs: a start date, an optional end date (default today), and one or
more git working trees. The skill runs end to end: it writes `a.md` at
the calling project root, presents the topics for selection, asks for a
few words of context, then writes `a.activity-report.<start>-<end>.md`
at the same root for review. Both files match the `a.*` gitignore rule.
