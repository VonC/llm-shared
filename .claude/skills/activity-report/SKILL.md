---
name: activity-report
description: 'In one invocation, build a.md (commit messages and Markdown diffs per git working tree over a date window, default end today) without reading the full codebase, analyze it, present the topics to select, ask for a few words of context, then write or update a French report a.activity-report.<start>-<end>.md in the review artifact home (.reviews) for review. With no file it creates that conventional name, or updates it (adding only new topics) when it already exists; pass an existing report file to update it. On the user go-ahead after review, it renders the report to HTML then PDF. Use when the user asks for an activity report across one or more working trees.'
user-invocable: true
argument-hint: 'Give the start date and the working trees, for example "activity-report --start 2026-05-29 . ../my-project". End date defaults to today (--end YYYY-MM-DD). Optionally pass an existing report file to update it; with no file the conventional a.activity-report.<start>-<end>.md is created, or updated when it already exists.'
---

[Instruction](../../../instructions/activity-report.md)
