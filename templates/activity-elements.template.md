# Activity elements scratch document template

This template describes the structure of `a.md`, the throwaway document
the `activity-report` skill writes at the root of the calling project.
It holds the activity elements to analyze: per working tree, the commit
messages and the Markdown diff over the date window. It is the input
material, not the report; the report is written afterwards from the
topics the user selects out of this document.

The `activity_report.sh` script produces `a.md` with the shape below.
One `##` section per working tree; under each, the commit messages and
the Markdown diff for the date window.

## Generated a.md layout

The fenced block shows the exact layout, with `{...}` placeholders. The
real `a.md` repeats the working-tree block once per tree. The outer
fence uses four backticks so the inner `diff` fences stay visible.

````md
# Activity report to be analyzed

Period: from {start} to {end} (both dates included).

## {working tree 1 name}

Path: {absolute path of working tree 1}

### Commit messages

- {YYYY-MM-DD} {short-hash} {commit subject}
  {commit body, indented by two spaces, may span several lines}
- {YYYY-MM-DD} {short-hash} {commit subject}

### Md diff

```diff
{git diff of *.md over the window, unified diff format}
```

## {working tree 2 name}

Path: {absolute path of working tree 2}

### Commit messages

- {YYYY-MM-DD} {short-hash} {commit subject}

### Md diff

```diff
{git diff of *.md over the window}
```
````

## Notes on the generated sections

- `Period` records the inclusive start and end dates used for both the
  log and the diff, so any later reader knows the window at a glance.
- `Commit messages` is `git log --reverse` output (oldest first) over
  the window: one list item per commit with date, short hash, subject,
  and the indented body.
- `Md diff` is the cumulative `git diff` of `*.md` files between the
  commit just before the start day and the last commit of the end day.
  An empty section means no Markdown changed in the window.
- A working tree that is not a git repository, or that has no commit in
  the window, gets a short note instead of the two sections.
