# Step {x} handoff for {slug}

Private, git-ignored resume note. Rewrite the state and next-action sections
whenever they change; the journal stays the authoritative, append-only log.

- Journal: `{artifact-home}/a.{slug}.step{x}.journal.md`
- Updated: {YYYY-MM-DDTHH:MM:SS+HH:MM}

## Step {x} at a glance

{one paragraph: the goal from the journal, and where the step stands now}

## Step {x} verified state

- Branch and head: `{branch}` at `{short sha}` ({clean, or: n files changed, staged or not})
- Last gate: {`ghog day` exit code and date, or: not run yet}
- Review: {no review, or: round n and state, as `pw progress` reports it}
- {any other fact checked on disk, with how it was checked}

## Step {x} next actions

1. {the very next action, concrete enough to run without rereading the plan}
2. {the action after it}

## Step {x} decisions

- {decision, reason, and date; append, never rewrite}

## Step {x} record tables

{only when the step needs one: a Markdown table of runs, probes, or builds,
with the revision, command, result, and evidence folder of each row}

## Step {x} private references

- {private paths the step relies on: earlier handoffs, evidence folders,
  `a.{slug}.step{x}.tmp.*` files, local notes outside the repository}
