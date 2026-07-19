# How to write an activity report

<img src="../assets/logo-llm-shared-trail-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

📊 Goal: produce a French activity report for IT managers from one or
several git working trees over a date window, without the agent reading
the codebase — commit messages and markdown diffs only.

## Invocation model

Ask the AI for an activity report; it normally gathers the history, offers the
topic selection, writes the report, and renders the deliverable. Run the helper
directly for a scheduled report, an integration test, or a deliberately
standalone conversion after the inputs are already settled.

## 📋 Steps from git history to PDF

1. Ask the agent for an activity report with a start date (end date
   defaults to today), naming the working trees:

   ```txt
   activity report from 2026-05-29 over ..\projA and ..\projB
   ```

2. The skill runs the collector from the project root:

   ```bash
   scripts/activity_report.sh --start 2026-05-29 ../projA ../projB
   ```

   It writes `a.md`: per tree, the commit messages of the window
   (`git log --reverse`) and the diff of the `*.md` files — nothing else
   is read.

3. The skill analyzes `a.md` and presents a numbered topic list grouped by
   tree. First pause: pick the topics worth reporting and give a few words
   of context.

4. It writes (or updates) the report,
   `a.activity-report.<start>-<end>.md`, following the French template:
   a `## En bref` section of standalone manager-ready lines, then one
   short titled section per selected topic. Passing an existing report
   file updates it, adding only new topics.

5. Second pause: review the markdown. On your go-ahead, the skill renders
   HTML then PDF with the same base name, through the pure-Python
   xhtml2pdf route (no browser involved):

   ```bash
   uv run --with markdown --with xhtml2pdf python a.md2pdf.py <in.md> <out.html> <out.pdf>
   ```

## 🙈 Why nothing is committed

Every produced file matches the `a.*` gitignore pattern: the report is a
deliverable to send, not repository content.

## ✅ Check the report

The `.md`, `.html` and `.pdf` share the same
`a.activity-report.<start>-<end>` base name, the report reads in French
with one `##` section per chosen topic, and re-running with the same
window updates rather than overwrites.

Related: [Build the git-history dashboard](build-the-git-history-dashboard.md),
[Document templates](../reference/templates.md).
