# Activity report

Produce an activity report for IT managers from one or more git working
trees over a date window, without reading the full codebase. The skill
runs end to end on a single invocation: it gathers the activity
elements, analyzes them, asks the user to pick the topics and add a few
words of context, then writes the report for review.

The only inputs the skill reads are the commit messages and the diff of
the Markdown files over the window. The report is written for a human
reviewer, in French by default (the audience is French-speaking IT
managers).

## Inputs for the activity-report skill

- A start date `YYYY-MM-DD`, inclusive (required).
- An end date `YYYY-MM-DD`, inclusive (optional, default: today).
- One or more git working trees (paths). When none is given, the
  current directory is used. Paths may be relative to the calling
  project, for example `.` and `../pdfsplitter`.

## Outputs of the activity-report skill

- `<CALLING_PRJ_DIR>/a.md` — the scratch elements document (git log and
  the `*.md` diff per working tree). A throwaway, regenerated each run.
  See [`activity-elements.template.md`](../templates/activity-elements.template.md).
- `<CALLING_PRJ_DIR>/a.activity-report.<start>-<end>.md` — the report
  itself, in French, for the user to review. The `a.*` line in each
  project `.gitignore` keeps both files out of git by default.

## Mutualized resources for activity-report

- This instruction lives in [`../instructions`](.).
- The script is
  [`activity_report.sh`](../scripts/activity_report.sh) under
  [`../scripts`](../scripts).
- The elements (a.md) structure is
  [`activity-elements.template.md`](../templates/activity-elements.template.md).
- The report structure is
  [`activity-report.french.template.md`](../templates/activity-report.french.template.md).
- Writing rules: [`markdown.md`](../rules/markdown.md) and
  [`blacklist.md`](../rules/blacklist.md) under `../rules`.

## Workflow for activity-report

Run all steps in one go. The user invokes the skill once; do not pause
between steps 1 and 2. The only pause is step 3, to collect the user's
topic selection and context.

### Step 1 — Generate the activity elements with the script

Run the mutualized `activity_report.sh` from the calling project root
(so `a.md` lands at that root). Pass the start date and the working
trees; the end date defaults to today.

```bash
bash ../llm-shared/scripts/activity_report.sh --start 2026-05-29 . ../pdfsplitter
```

To set an explicit end date or output file:

```bash
bash ../llm-shared/scripts/activity_report.sh \
  --start 2026-05-29 --end 2026-06-21 --out a.md . ../pdfsplitter
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

### Step 2 — Analyze a.md and present the topic list

Right after the script finishes, read `a.md` and work from it alone — do
not open the source files. From the commit messages and the Markdown
diffs, build a topic list and present it to the user without being asked:

- Group by working tree first.
- Within a tree, group related commits and Markdown changes into a small
  number of topics (a feature, a fix family, a doc effort, a tooling
  change). Merge commits that belong to the same effort.
- Number every topic so the user can refer to it.
- For each topic give: a short title, a one-line summary of what changed
  and why it matters to an IT manager, and the supporting evidence
  (commit short hashes and changed Markdown files).

Keep the list concise and factual: concrete changes, no generalities,
and none of the words from [`blacklist.md`](../rules/blacklist.md).

### Step 3 — Ask the user to select topics and add context

Pause once, here, and ask the user two things together:

1. Which numbered topics to keep in the report (and their order if it
   matters).
2. A few words of context to guide the redaction: the audience angle,
   what to stress, the tone, or anything the commits do not show.

When the topics are few, a multi-select prompt is convenient; otherwise
present the numbered list and ask the user to reply with the kept
numbers and the context line. Do not write the report before the user
has selected topics and given context.

### Step 4 — Write the report for review

Write `<CALLING_PRJ_DIR>/a.activity-report.<start>-<end>.md`, for
example `a.activity-report.2026-05-29-2026-06-21.md`, following
[`activity-report.french.template.md`](../templates/activity-report.french.template.md):

- A main title with the period.
- An `## En bref` section a manager can read on its own.
- One `##` section per selected topic, in the user's order, each woven
  with the user's context.

Write in French by default. If the user asked for another language,
adapt the headings and prose to that language but keep the same shape.
Use concrete terms, the user's context, and none of the blacklisted
words. Do not put commit hashes in the report prose; they belong in
`a.md`.

### Step 5 — Confirm and hand back

Tell the user the report was written to
`a.activity-report.<start>-<end>.md` at the project root, that it is
gitignored by the `a.*` rule, and invite them to review it. Offer to
adjust topics, length, or tone on request.
