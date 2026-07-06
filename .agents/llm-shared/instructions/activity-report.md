# Activity report

Produce an activity report for IT managers from one or more git working
trees over a date window, without reading the full codebase. The skill
runs end to end on a single invocation: it gathers the activity
elements, analyzes them, presents choices for the user to pick the topics and
add a few words of context, then writes the report for review.

The only inputs the skill reads are the commit messages and the diff of
the Markdown files over the window. The report is written for a human
reviewer, in French by default (the audience is French-speaking IT
managers).

## Inputs for the activity-report skill

- A start date `YYYY-MM-DD`, inclusive (required).
- An end date `YYYY-MM-DD`, inclusive (optional, default: today).
- One or more git working trees (paths). When none is given, the
  current directory is used. Paths may be relative to the calling
  project, for example `.` and `../my-project`.
- An optional existing report file to update. When a report file is named,
  the skill updates that file. When none is named, the target is the
  naming convention `a.activity-report.<start>-<end>.md` at the calling
  project root: the skill creates it when it does not exist, and updates it
  (never overwrites it) when it already does. Updating means adding only
  the topics the report does not cover yet, and refreshing the summary, not
  rewriting what is there.

## Outputs of the activity-report skill

- `<CALLING_PRJ_DIR>/a.md` — the scratch elements document (git log and
  the `*.md` diff per working tree). A throwaway, regenerated each run.
  See [`activity-elements.template.md`](../templates/activity-elements.template.md).
- `<CALLING_PRJ_DIR>/a.activity-report.<start>-<end>.md` — the report
  itself, in French, for the user to review (or the report file named on
  input, when updating).
- The HTML and PDF renders of that report, sharing its base name
  (`a.activity-report.<start>-<end>.html` and `.pdf`), generated after the
  review go-ahead. The `a.*` line in each project
  `.gitignore` keeps all of these files out of git by default.

## Mutualized resources for activity-report

- This instruction lives in [`../instructions`](.).
- The elements script is
  [`activity_report.sh`](../scripts/activity_report.sh) under
  [`../scripts`](../scripts).
- The render helper is
  [`md_to_pdf.py.template`](../templates/md_to_pdf.py.template) under
  [`../templates`](../templates); it turns the report Markdown into HTML
  and then a PDF with the pure-Python `xhtml2pdf` engine, no browser. It is
  a `.py.template`, not a `.py`, so the project linters skip it; it is run
  directly with `python`.
- The elements (a.md) structure is
  [`activity-elements.template.md`](../templates/activity-elements.template.md).
- The report structure is
  [`activity-report.french.template.md`](../templates/activity-report.french.template.md).
- Writing rules: [`markdown.md`](../rules/markdown.md) and
  [`blacklist.md`](../rules/blacklist.md) under `../rules`.

## Workflow for activity-report

Run all steps in one go. The user invokes the skill once; do not pause
between steps 1 and 2. There are two pauses: step 3 collects the topic
selection and context, and step 5 waits for the go-ahead after the report
review, before the HTML and the PDF are rendered in step 6. Read
[`../rules/interactive_menu.md`](../rules/interactive_menu.md) before both
pauses.

### Step 1 — Generate the activity elements with the script

Run the mutualized `activity_report.sh` from the calling project root
(so `a.md` lands at that root). Pass the start date and the working
trees; the end date defaults to today.

```bash
bash ../llm-shared/scripts/activity_report.sh --start 2026-05-29 . ../my-project
```

To set an explicit end date or output file:

```bash
bash ../llm-shared/scripts/activity_report.sh \
  --start 2026-05-29 --end 2026-06-21 --out a.md . ../my-project
```

The script writes, per working tree, the output of these two git
commands (documented here so the window logic is reviewable):

- Commit messages, oldest first, over the inclusive window:

  ```bash
  git -C <worktree> log --reverse \
    --since="<start> 00:00:00" --until="<end> 23:59:59" \
    --date=short --format='- %ad %h %s%n%w(0,2,2)%b'
  ```

- Markdown diff, from the last commit strictly before the start day to
  the last commit at or before the end day, limited to `*.md`:

  ```bash
  START_REV=$(git -C <worktree> rev-list -1 --before="<start> 00:00:00" HEAD)
  END_REV=$(git -C <worktree> rev-list -1 --before="<end> 23:59:59" HEAD)
  git -C <worktree> diff "$START_REV" "$END_REV" -- '*.md'
  ```

  When `START_REV` is empty (the working tree has no commit before the
  start day), the script uses the empty tree as the base.

Optional tweaks, only when the user asks: add `--author=<name>` to the
log to keep one author, or drop merge commits with `--no-merges`. By
default both are kept, since merge commit messages can carry topic
information.

### Step 2 — Settle the target file, analyze a.md, present the topic list

First settle the target report file. When the prompt named an existing
report file, that file is the target and the run is an update. Otherwise
the target is `a.activity-report.<start>-<end>.md` at the calling project
root: a new file when it does not exist, an update when it does. When the
target already exists, read it now, so the topic list can mark what it
already covers.

Then read `a.md` and work from it alone — do not open the source files.
From the commit messages and the Markdown diffs, build a topic list and
present it to the user without being asked:

- Group by working tree first.
- Within a tree, group related commits and Markdown changes into a small
  number of topics (a feature, a fix family, a doc effort, a tooling
  change). Merge commits that belong to the same effort.
- Number every topic so the user can refer to it.
- For each topic give: a short title, a one-line summary of what changed
  and why it matters to an IT manager, and the supporting evidence
  (commit short hashes and changed Markdown files).
- When the target is an update, compare each candidate topic against what
  the report already covers and present only the topics that are new; the
  existing content stays.

Keep the list concise and factual: concrete changes, no generalities,
and none of the words from [`blacklist.md`](../rules/blacklist.md).

### Step 3 — Select topics and add context

Pause once, here, and present the topic selection:

- When the host has a multi-select menu, use it for the numbered topics.
- After the topics are selected, present a separate text-entry prompt for a few
  words of context to guide the redaction: the audience angle, what to stress,
  the tone, or anything the commits do not show.
- When the host has no multi-select menu, use the chat fallback described in
  [`../rules/interactive_menu.md`](../rules/interactive_menu.md).

Do not write the report before the user has selected topics and given context.

### Step 4 — Write or update the report

Write the target report file settled in step 2, following
[`activity-report.french.template.md`](../templates/activity-report.french.template.md):

- A new report: a main title with the period, an `## En bref` section a
  manager can read on its own, then one `##` section per selected topic in
  the user's order, each woven with the user's context.
- An update: integrate only the selected new topics into the existing
  report, in place. Add or extend the relevant `##` sections, and refresh
  the `## En bref` where a new topic changes the headline. Do not rewrite
  or drop what is already there, and do not overwrite the file with a fresh
  report.

Write in French by default. If the user asked for another language,
adapt the headings and prose to that language but keep the same shape.
Use concrete terms, the user's context, and none of the blacklisted
words. Do not put commit hashes in the report prose; they belong in
`a.md`.

### Step 5 — Pause for review and a go-ahead

Tell the user the report was written (or updated) at its path, and that it
is gitignored by the `a.*` rule. Ask them to review it, then present the
go-ahead choices from [`../rules/interactive_menu.md`](../rules/interactive_menu.md):

- `Go ahead` — render the HTML and PDF.

Render the HTML and the PDF only after a go-ahead entry is selected. Do not
render before that selection.

### Step 6 — Render the HTML, then the PDF

On a go-ahead selection, render the report to HTML and then to PDF, in that
order, over the matching names (the report base name with `.html` and
`.pdf`). Use the mutualized render helper, which needs no browser: the
headless-browser route hangs on Windows, so this uses the pure-Python
`xhtml2pdf` engine, provided on the fly by uv. From the calling project
root:

```bash
uv run --with markdown --with xhtml2pdf python \
  <LLM_SHARED_DIR>/templates/md_to_pdf.py.template \
  a.activity-report.<start>-<end>.md \
  a.activity-report.<start>-<end>.html \
  a.activity-report.<start>-<end>.pdf
```

Use the report's real name (the named file when updating, or the
conventional name otherwise) for all three paths. The helper writes the
HTML first, then the PDF, and overwrites both. When the PDF path is locked
(open in a viewer), it cannot be overwritten: tell the user to close the
viewer, then re-run this step.

### Step 7 — Confirm and hand back

Confirm the report, its HTML, and its PDF were written (or updated) at the
project root, all gitignored by the `a.*` rule, and invite the user to
review them. Offer to adjust topics, length, or tone, then re-render on
request.
