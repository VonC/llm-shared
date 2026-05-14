# Development workflow with IA

This workflow takes one raw topic from draft notes to reviewed documents,
implemented plan steps, and grouped commits. It uses the skills in
`.github\skills` together with the local helper scripts in `bin\` and `tools\`.

This is geared toward Python projects, but the general flow and some of the
helpers can be adapted to other languages and ecosystems.

Make sure the setting "Chat Permissions Default" is set to "Bypass Approval".  
And "chat.notifyWindowOnConfirmation" is set to "always".  
And "chat.notifyWindowOnResponseReceived" is set to "always".

## Goal: avoid vibe-coding

Vibe-coding is the shortcut some developers take with an AI assistant:
"I got an idea, here it is, now generate me some code for it, I will
figure out the details later." The code lands fast, runs against an
unspoken set of assumptions, and then breaks on the first real-world
case the author never wrote down.

This workflow keeps the creative spark — the draft is still raw natural
language, the author still picks the topic and direction — but spends
real time turning that spark into a defined requirement, a reviewed
design with explicit acceptance scenarios, and a plan that drives the
code in a known order. Each skill exists to do one of those jobs:

- **Capture and (optionally) split** the idea: write
  `docs\draft.vX.Y.Z.<topic>.md` in free form, then run
  `/split-and-define` only if the draft carries several items. A
  single-requirement draft skips straight to the next step.
- **Define each requirement** in its own document with
  `/write-requirement`.
- **Refine each document** through the review loop
  (`/review-ask-questions` then `/consolidate-then-review-ask-questions`),
  until no open question remains.
- **Design the solution**, including acceptance scenarios that describe
  what "done" looks like from the user side, with `/write-design`.
- **Plan the implementation** as a numbered list of steps with
  `/write-plans`. The plan starts with one or more gate-test steps that
  add failing tests against the target behavior, continues with steps
  that make those gate tests pass piece by piece, and ends with an
  acceptance-test step that closes the loop on the requirement.
- **Implement and check each step** in isolation with
  `/implement-step N` then `/implementation-check N`, updating the
  validation document and committing in small grouped commits.

What this workflow refuses to do:

- Skip the requirement document because "we both know what I mean".
- Skip the design document because "the code will tell us".
- Skip the gate tests because "I'll add them after".
- Skip the acceptance tests because "I tested it manually once".

What this workflow keeps:

- Natural-language drafts with no constraint on style.
- Author judgement on what is one requirement versus several.
- A short path when the draft is genuinely one self-contained
  requirement (see
  [Requirement breakdown from the draft](#requirement-breakdown-from-the-draft)).

The cost is up-front: a few extra documents before any code is written.
The payoff is that the code that does get written has a known target, a
written acceptance bar, and tests that already exist when the
implementation starts.

### Trail left by the workflow

A long-running benefit: every phase leaves an artifact, so the workflow
doubles as documentation of the development process itself.

What ends up in the repository:

- The original draft, with the author's raw framing.
- The requirement document(s), with the decision table that captures
  every resolved open question (the option that was picked and the
  alternatives that were rejected).
- The design document, with its own decision table and the acceptance
  scenarios.
- The plan, with one entry per numbered step, and the validation plan
  that records what each step actually shipped.
- One grouped commit per logical change, each with a conventional commit
  message written for the matching diff.
- A merge commit with a rewritten conventional message that points to
  the documents that landed with the branch.

This trail is useful to two kinds of future readers:

- A human reader (the original author six months later, or a new
  contributor) who needs to understand why a piece of code looks the
  way it does, not just what it does.
- An LLM that is asked to extend, debug, or refactor the code in a later
  session. The model gets context that is missing from the code alone:
  the question that was being answered, the alternatives that were ruled
  out, and the acceptance bar that was negotiated. The richer the
  history, the better the suggestions the model can produce.

Code without that trail forces every future reader — human or model —
to reverse-engineer the intent from the implementation. Code with the
trail short-circuits that reverse-engineering, which is the same reason
this workflow exists in the first place.

## Shell setup for the IA workflow

Before you use the aliases below, load the project shell with `senv.bat`.
That script switches to the project Python version, adds `bin\` to `PATH`,
and loads the Doskey macros declared in `senv.bat` and `senv.doskey`.

The rest of this document assumes those macros are available.

## Local command reference for this workflow

- `gcmp`: Doskey alias to `bin\gcmp.bat`. It runs
  `tools\group_commit_message_prompt.py`, reads the staged Git state, writes
  `a.diff`, clears `a.commit`, builds a `/group-commits-msg` prompt from the
  staged files, copies that prompt to the clipboard, and prints a ready line.
- `gcba`: Doskey alias to `bin\gcba.bat --root-a-commit`. It runs
  `tools\git_batch_commit.py --root-a-commit`, validates `a.commit`, and then
  replays the grouped commits when the file is valid. The aliases `gcb`,
  `gbc`, `gcbr`, `gbcr`, `gcab`, and `gbca` are the same family of helpers.
- `ruffc`: Doskey alias to `ruff check`. Use it right after code generation
  or manual edits.
- `pta`: Doskey alias to
  `pytest --testmon --cov-append --no-header --cov-report term-missing:skip-covered`.
  It reruns only the tests affected by the current changes and appends
  coverage data.
- `ptr`: Doskey alias to
  `del .testmondata 2>nul & pytest --testmon --no-header --cov-report term-missing:skip-covered`.
  It resets `testmon` state and then reruns the suite with coverage output,
  which is the wider safety check when `pta` is not enough.
- `covg`: alias to
  `python "tools\coverage_gap_functions.py" $*`.
  It maps uncovered coverage lines to the enclosing function or method, adds
  branch context when possible, logs the report, and copies a ready-to-paste
  test coverage prompt to the clipboard.

## Draft capture for a feature or fix

```txt
   +---------------------------------+
   | raw notes / discussion          |
   | missing or broken behavior      |
   | desired outcome                 |
   +-------+-------------------------+
           |
           |  capture
           v
   +---------------------------------+
   |                                 |----+
   |  docs\draft.vX.Y.Z.<topic>.md   |    |  edit + refine
   |                                 |<---+  in natural language
   +-------+-------------------------+
           |
           |  stable enough to split
           v
   +---------------------------------+
   |   draft ready for breakdown     |
   +---------------------------------+
```

1. Start with `docs\draft.vX.Y.Z.<topic>.md`.
2. Keep `X.Y.Z` as the working version for the current effort, even if the
  final merge target changes later.
3. Keep `<topic>` short, stable, and descriptive.
4. Write the draft in natural language, preferably English. Cover the desired
  behavior, missing behavior, broken behavior, constraints, examples, and the
  expected outcome.

## Requirement breakdown from the draft

```txt
                +---------------------------------+
                |  docs\draft.vX.Y.Z.<topic>.md   |
                +----------------+----------------+
                                 |
                  +--------------+--------------+
                  |                             |
        single requirement?            multiple items?
        skip /split-and-define         /split-and-define
                  |                             |
                  |                             v
                  |             +---------------------------------+
                  |             |  draft + appended section:      |
                  |             |  "List of feature-requests      |
                  |             |   and issues to create"         |
                  |             |   - item 1   [topic-slug]       |
                  |             |   - item 2   [topic-slug]       |
                  |             |   - ...                         |
                  |             |   - item N   [topic-slug]       |
                  |             +----------------+----------------+
                  |                              |
                  |                  /write-requirement
                  |                  <type> vX.Y.Z <topic>
                  |                  (one call per item)
                  |                              |
                  +--------------+---------------+
                                 |
                /write-requirement <type> vX.Y.Z <topic>
                (single call, author picks the type)
                                 v
                +---------------------------------+
                | docs\feature-request.vX.Y.Z.    |
                |       <topic-slug>.md           |
                |  or                             |
                | docs\issue.vX.Y.Z.              |
                |       <topic-slug>.md           |
                +---------------------------------+
```

`/split-and-define` is optional. The choice depends on the draft:

- Run `/split-and-define` first when the draft mixes several distinct
  items, when those items have a non-trivial dependency order, or when
  the author wants the skill to propose a `[topic-slug]` per item and
  decide which item is a `feature-request` and which is an `issue`.
- Skip `/split-and-define` and call `/write-requirement` directly when
  the draft already describes a single, self-contained requirement and
  the author already knows the type (`feature-request` or `issue`),
  version, and topic. This shorter path keeps the focus on writing one
  clear requirement instead of running a split that would return only
  one item.

When `/split-and-define` is used:

1. Run `/split-and-define` with the draft document in context.
2. That skill updates the draft itself by appending a
  `List of feature-requests and issues to create` section.
3. The generated list groups related draft items, gives each item a key title
  plus a short `[topic-slug]`, and orders the items from the most independent
  one to the most dependent one.
4. For each item in that list, run `/write-requirement` with the draft and the
  selected item in context.
5. Use the actual skill name `/write-requirement` and pass the type, version,
  and topic, for example `issue v9.3.0 sentinels`.
6. The skill writes `docs\<type>.vX.Y.Z.<topic>.md`.

When `/split-and-define` is skipped:

1. Decide the type directly: `feature-request` for new behavior, `issue`
  for a bug or missing behavior already present in the draft.
2. Run `/write-requirement <type> vX.Y.Z <topic>` with the draft in
  context, picking a stable `<topic>` slug yourself.
3. The skill writes the same `docs\<type>.vX.Y.Z.<topic>.md` file and
  the next phase (review loop) is identical.

You can decide if you need to isolate each identified features or issues in their
own development branch (`git switch -c <topic-slug>`) or if you can keep multiple
related items in the

## Review loop for each requirement document

The same loop is used later on the design document and, if needed, on the plan
document. Only the input document changes.

```txt
   +---------------------------------+
   |  document under review          |
   |  (requirement, design, or plan) |
   +-------+-------------------------+
           |
           |  /review-ask-questions
           |  (appends Qxx blocks: options,
           |   pros, cons, recommended choice)
           v
   +---------------------------------+
   |  doc with open questions        |
   +-------+-------------------------+
           |
           |  user picks one answer per Qxx
           v
   +---------------------------------+
   |  answered doc                   |
   +-------+-------------------------+
           |
           |  /consolidate-then-review-ask-questions
           |  (folds answers into a decision table,
           |   removes resolved Qxx,
           |   appends new Qxx only if needed)
           v
   +---------------------------------+
   |  consolidated doc               |----+  new open questions?
   |                                 |    |  yes -> /review-ask-questions
   |                                 |<---+  (loop)
   +-------+-------------------------+
           |
           |  no more open questions
           v
   +---------------------------------+
   |  doc approved for next phase    |
   +---------------------------------+
```

1. Run `/review-ask-questions` on the requirement document, with the related
  markdown files in context.
2. That skill appends open questions with options, pros and cons, a
  recommended choice, and an explicit answer format.
3. Once answers are settled, run `/consolidate-then-review-ask-questions`.
4. That skill folds resolved questions back into the document, removes old
  question blocks, and asks new questions only when more clarification is
  still needed.
5. Repeat the two skills until the requirement is clear enough to design and
  plan.

## Design and planning flow for each approved requirement

```txt
   +---------------------------------+
   |  approved requirement doc       |
   +-------+-------------------------+
           |
           |  /write-design
           v
   +---------------------------------+
   |                                 |----+
   |  docs\design.vX.Y.Z.<topic>.md  |    |  /review-ask-questions
   |  (scope, constraints, target    |    |  /consolidate-then-review-...
   |   behavior, design areas)       |<---+  (loop until stable)
   +-------+-------------------------+
           |
           |  /write-plans
           v
   +---------------------------------+
   |  docs\plan.vX.Y.Z.<topic>.md    |
   |    (execution plan)             |----+
   |  docs\plan.vX.Y.Z.<topic>.      |    |  /review-ask-questions
   |       validation.md             |    |  /consolidate-then-review-...
   |    (validation template)        |<---+  (optional, if open Qs remain)
   +-------+-------------------------+
           |
           |  plan ready for step-by-step execution
           v
   +---------------------------------+
   |  ready to /implement-step       |
   +---------------------------------+
```

1. Run `/write-design` with the requirement document in context.
2. The skill writes `docs\design.vX.Y.Z.<topic>.md` and keeps the output at
  design level: scope, constraints, confirmed facts, target behavior, and
  major design areas, not file-by-file implementation steps.
3. Run `/review-ask-questions` on the design document.
4. Run `/consolidate-then-review-ask-questions` after the design answers are
  chosen.
5. Repeat that review loop until the design is stable.
6. Run `/write-plans` with the design document in context.
7. That skill creates `docs\plan.vX.Y.Z.<topic>.md`, which is the execution
  plan: step order, file lists, rollout notes, line-budget checkpoints,
  command checklists, and acceptance-test expectations.
8. The same skill also creates
  `docs\plan.vX.Y.Z.<topic>.validation.md`, which is the implementation
  validation document updated later by the execution and checking steps.
9. If the plan still has open implementation questions, run the same
  review-and-consolidation loop on the plan document before coding.

## Grouped commit loop for documents and code

```txt
   +---------------------------------+
   |  staged files (current slice)   |
   +-------+-------------------------+
           |
           |  gcmp
           v
   +---------------------------------+
   |  a.diff (snapshot of the diff)  |
   |  clipboard:                     |
   |    /group-commits-msg           |
   |    ... Context: <topic>         |
   +-------+-------------------------+
           |
           |  paste the prompt into Copilot / Claude
           v
   +---------------------------------+
   |  a.commit                       |----+  edit if grouping
   |  (groups + messages,            |    |  or wording is off
   |   one block per group)          |<---+  (rerun /group-commits-msg
   +-------+-------------------------+       only if needed)
           |
           |  approved a.commit
           |  gcba
           v
   +---------------------------------+
   |  commits replayed, from least   |
   |  dependent group to most        |
   |  dependent group                |
   +---------------------------------+
```

1. Stage only the files that belong to the current slice. Use `git add .` only
  if the worktree contains nothing unrelated.
2. Run `gcmp`.
3. Paste the generated clipboard prompt into Copilot. The prompt already
  starts with `/group-commits-msg ...` and ends with `Context:`. Add the
  topic at the end of that `Context:` line.
4. Review the generated `a.commit` file. `a.diff` is the staged diff snapshot
  used to justify the groups, and `a.commit` is the grouped commit plan that
  will be replayed later.
5. If the grouping or wording is off, edit `a.commit`.
  Rerun the `gcmp` -> `/group-commits-msg` generation pass only if you need
  Copilot to regroup files or rewrite the commit messages again. If your
  manual edits are enough, do not rerun that pass; go straight to `gcba`.
6. When `a.commit` is ready, either say `go ahead` in the same chat flow or
  run `gcba` directly.
7. `gcba` validates `a.commit` and creates the commits from the least
  dependent group to the most dependent group.

Use this commit loop once after the documents are ready, then again after each
fully completed implementation step.

## Step execution loop from the plan

```txt
   +---------------------------------+
   |  docs\plan.vX.Y.Z.<topic>.md    |
   |  pick next unchecked step N     |
   +-------+-------------------------+
           |
           |  /implement-step N
           v
   +---------------------------------+
   |  code + tests for step N        |
   +-------+-------------------------+
           |
           |  ruffc                  (lint pass)
           |  pta                    (affected tests)
           |  covg + extra tests     (only if gaps)
           |  ptr                    (wider reset pass)
           v
   +---------------------------------+
   |  step N green                   |
   +-------+-------------------------+
           |
           |  /implementation-check N
           |  (updates ...validation.md,
           |   flags smells, dep issues,
           |   hot-path risks)
           v
   +---------------------------------+
   |  step N validated               |
   +-------+-------------------------+
           |
           |  grouped commit loop
           |  gp (git push)
           v
   +---------------------------------+
   |  step N committed and pushed    |----+  more steps?
   |                                 |    |  yes -> /implement-step
   |                                 |<---+  (loop)
   +-------+-------------------------+
           |
           |  last step done
           v
   +---------------------------------+
   |  branch ready to merge          |
   +---------------------------------+
```

1. Pick the next unchecked step from `docs\plan.vX.Y.Z.<topic>.md`.
2. Run `/implement-step <step-number>` with the plan, design, and related
  requirement documents in context.
3. Run `ruffc`.
4. Run `pta` on the touched tests first.
5. If `pta` shows a small number of uncovered lines, copy the uncovered
  coverage lines and run `covg`. That helper maps the missing lines to the
  enclosing functions or methods, then prepares a clipboard prompt you can
  paste back into Copilot to ask for the smallest missing tests.
6. If `pta` is not enough, or if `testmon` state looks stale, run `ptr` for a
  wider rerun after resetting `.testmondata`.
7. Once the code and tests are green, run `/implementation-check` with the
  step number, version, topic, relevant markdown docs, and `a.diff` when
  available.
8. That skill updates `docs\plan.vX.Y.Z.<topic>.validation.md` and checks
  whether the step is actually complete, including architecture smells,
  dependency issues, and hot-path performance risks.
9. If a file is getting too large or is doing too many unrelated things, use
  `/split-large-file` before the next step grows it further.
10. Stage the finished slice and reuse the grouped commit loop.
11. Do not start the next step until the current one is implemented, tested,
  checked, and committed. And pushed. (use `gp` for `git push`)

## Decision rule for architecture and performance findings

- If `/implementation-check` finds an architecture smell (or violation, or
  girth too big, or anything else), ask for the pros
  and cons of fixing it now versus documenting an exemption and creating a
  follow-up issue. Fix it immediately when the change stays small and within
  the current step scope.
- If it finds a hot-path performance issue, fix it before moving on. Do not
  defer it to a later step unless the current fix is blocked by missing design
  work.

Repeat this sequence until every planned step is committed in your branch.

## Merge your development branch

```txt
   +---------------------------------+
   |  development branch             |
   |  (all steps committed)          |
   +-------+-------------------------+
           |
           |  git fetch
           |  git rebase origin/main
           |  c (python_check) + pta + ptr
           v
   +---------------------------------+
   |  branch rebased and green       |
   +-------+-------------------------+
           |
           |  git switch main
           |  git pull
           |  git merge --no-ff <branch>
           v
   +---------------------------------+
   |  merge commit on main           |
   |  (default Git message)          |
   +-------+-------------------------+
           |
           |  /update-merge-commit-msg
           |    (git-extract-merge-docs.sh
           |     -> a.docs;
           |     skill -> a.commit)
           |  grmc
           |    (rewrites the merge commit)
           v
   +---------------------------------+
   |  merge commit with              |
   |  conventional message           |
   +-------+-------------------------+
           |
           |  gp / git push
           v
   +---------------------------------+
   |                                 |----+  next requirement?
   |  main published                 |    |  yes -> new branch,
   |                                 |<---+  back to /implement-step
   +-------+-------------------------+
           |
           |  after several merges
           |  /write-release-notes-summary
           |  git tag vX.Y.Z
           v
   +---------------------------------+
   |  release                        |
   +---------------------------------+
```

### Rebase your branch on top of main

Do this while you are still on your development branch. The goal is to replay
your work on top of the latest `origin/main`, resolve conflicts before the
merge commit exists, and rerun the same checks you used during step execution.

1. Run `git fetch` to refresh your remote references.
2. Run `git rebase origin/main` and resolve any conflict before continuing.
3. Run `c`, which is the local Doskey alias to `bin\python_check.bat`.
4. Run `pta` and then `ptr` so both the affected-test pass and the wider
  reset pass are green before you merge.

### Create the merge commit on main

Switch back to `main` only after your rebased branch is clean. This keeps the
merge commit focused on a branch that already passed checks on top of the
current main line.

1. Run `git switch main`.
2. Run `git pull` to make sure your local `main` matches the remote branch.
3. Run `git merge --no-ff <your-branch>` so Git creates an explicit merge
  commit for the branch.

### Reword the merge commit from the branch docs

Do not keep the default merge message. At this point the merge commit exists,
so you can derive a proper conventional commit message from the documents that
landed with the branch.

1. Run `/update-merge-commit-msg`.
2. That skill calls the merge-doc extraction script, writes the merged branch
  documents to `a.docs`, then writes one conventional commit message to
  `a.commit` for you to review and edit if needed.
3. Once `a.commit` is ready, run `grmc`, which is the local Doskey alias to
  `scripts\update-merge-commit-msg\git-reword-merge.sh`.
4. `grmc` rewrites the current merge commit so its message matches the final
  content of `a.commit`.

### Push the updated main branch

Publish only after the merge commit message has been rewritten.

1. Run `gp` if your shell defines it as your `git push` shortcut.
2. If `gp` is not defined in your shell, run `git push` directly to update
  `main`.

## Release notes and version tag

```txt
   main with several merge commits
                |
                | /write-release-notes-summary
                | (reads merge commit subjects and docs\plan.*.md files)
                v
   release notes draft
   +-- summary bullets grouped by topic
   +-- three witty title / subtitle pairs to pick from
                |
                | pick one title pair, finalize the notes
                v
   release notes ready to publish
                |
                | git tag vX.Y.Z
                | git push --tags
                v
   tagged release on main
```

1. After several merges have landed on `main`, run
  `/write-release-notes-summary` so the skill reads the recent merge commit
  subjects and any `docs\plan.*.md` files in context.
2. Review the generated bullet summary and pick one of the three proposed
  title / subtitle pairs.
3. Edit the notes if needed, then publish them through the project's usual
  release channel.
4. Run `git tag vX.Y.Z` on the latest commit of `main`, where `vX.Y.Z`
  matches the working version used for the recent draft, design, and plan
  documents.
5. Run `git push --tags` to publish the tag.
