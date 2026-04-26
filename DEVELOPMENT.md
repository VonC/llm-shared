# Development workflow with IA

This workflow takes one raw topic from draft notes to reviewed documents,
implemented plan steps, and grouped commits. It uses the skills in
`.github\skills` together with the local helper scripts in `bin\` and `tools\`.

This is geared toward Python projects, but the general flow and some of the
helpers can be adapted to other languages and ecosystems.

Make sure the setting "Chat Permissions Default" is set to "Bypass Approval".  
And "chat.notifyWindowOnConfirmation" is set to "always".  
And "chat.notifyWindowOnResponseReceived" is set to "always".

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

1. Start with `docs\draft.vX.Y.Z.<topic>.md`.
2. Keep `X.Y.Z` as the working version for the current effort, even if the
  final merge target changes later.
3. Keep `<topic>` short, stable, and descriptive.
4. Write the draft in natural language, preferably English. Cover the desired
  behavior, missing behavior, broken behavior, constraints, examples, and the
  expected outcome.

## Requirement breakdown from the draft

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

You can decide if you need to isolate each identified features or issues in their
own development branch (`git switch -c <topic-slug>`) or if you can keep multiple
related items in the

## Review loop for each requirement document

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
  `docs\plan.vX.Y.Z.<topic>.implementation.md`, which is the implementation
  review journal updated later by the execution and checking steps.
9. If the plan still has open implementation questions, run the same
  review-and-consolidation loop on the plan document before coding.

## Grouped commit loop for documents and code

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
8. That skill updates `docs\plan.vX.Y.Z.<topic>.implementation.md` and checks
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
  `.github\skills\update-merge-commit-msg\git-reword-merge.sh`.
4. `grmc` rewrites the current merge commit so its message matches the final
  content of `a.commit`.

### Push the updated main branch

Publish only after the merge commit message has been rewritten.

1. Run `gp` if your shell defines it as your `git push` shortcut.
2. If `gp` is not defined in your shell, run `git push` directly to update
  `main`.
