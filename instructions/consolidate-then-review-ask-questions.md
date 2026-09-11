# Consolidate then review and ask new questions

ultrathink: take the time to reason through the document deeply before drafting questions, so each question targets a real ambiguity rather than a surface-level prompt for elaboration.

Check your prompt for type (feature-request, issue, design or plan), vX.Y.Z and topic (for instance "design v9.3.0 sentinels").

Consolidate the exact `<document-path>` named in the prompt by integrating
answers given to existing questions in its "Open questions for the vX.Y.Z ..."
section. Read [`../rules/docs_layout.md`](../rules/docs_layout.md) and preserve
the document's effort directory. Before making any Markdown edit, read and
follow [`../rules/markdown.md`](../rules/markdown.md). Do not leave the
questions and their options; consolidation integrates the chosen answers into
the document.

## Pre-consolidation question snapshot

Before changing the document or running any `oqm` mode, commit the exact
`<document-path>` alone so Git retains the answered questions as they appeared
immediately before consolidation. This applies equally to a feature request,
issue, design, or implementation plan. Read
[`group-commits-msg.md`](group-commits-msg.md),
[`../templates/group-commits-msg.template.md`](../templates/group-commits-msg.template.md),
[`../rules/blacklist.md`](../rules/blacklist.md), and
[`../rules/run_commands.md`](../rules/run_commands.md) before creating the
snapshot.

Run this sequence from the project root:

Resolve `<LLM_SHARED_DIR>` as the absolute parent of the `instructions` folder
that contains this canonical file. Every shared launcher below uses that full
path; do not rely on an environment variable or a guessed sibling checkout.

1. Run plain `git reset` to clear the index without changing the working tree.
   Never use `--hard`, restore a file, or discard an unrelated change. Confirm
   that `git diff --cached --name-only` prints nothing.
2. Run `git add -A <document-path>` for the exact document only. Confirm that
   `git diff --cached --name-only` prints exactly `<document-path>` and no other
   path. The document must have a staged change; do not manufacture an empty
   snapshot commit when it is already identical to `HEAD`.
3. Replace the project-root `a.commit` with exactly one group following the
   group-commit template. Derive a required scope from the document identity:
   prefer its topic slug when the complete title remains within the 52-character
   limit; otherwise use the normalized document-type scope `feature`, `issue`,
   `design`, or `plan`. Use the conventional title
   `docs(<scope>): record pre-consolidation questions`. The `Why:` text must
   explain that consolidation will remove the answered question blocks; the
   `What:` list must name only `<document-path>` and state that its answered
   questions are recorded unchanged.
4. Run `& "<LLM_SHARED_DIR>\bin\wac.bat"` to format `a.commit`, then run
   `& "<LLM_SHARED_DIR>\bin\gcba.bat" --root-a-commit --non-interactive`.
   This one-file snapshot is part of the already-requested or durably authorized
   consolidation, so do not present another commit menu.
5. Confirm that the batch command succeeded, the new `HEAD` commit contains
   exactly `<document-path>`, and `git diff --cached --name-only` again prints
   nothing. Leave any unrelated working-tree changes unstaged.

If any check fails, stop before editing or stripping the questions. Report the
exact failure and keep the pre-consolidation document intact. Only a successful
one-file snapshot commit grants the next consolidation step.

You need to remove `Qxx:` sections and integrate their answers within the
document. Once every answer is integrated, remove the whole `## Open questions`
section with `& "<LLM_SHARED_DIR>\bin\oqm.bat" <document-path> --strip`
(see "Consolidating and placing questions with oqm" below).

Create a decision table in the document's decisions section, naming that section for the document type: "Design decisions" for a design, "Implementation decisions" for an implementation plan, or "Requirement clarifications" for a feature-request or an issue. Summarize all the choices that have been made, with their arguments and the alternatives that were rejected. Do reference the number of the question (Qxx) that led to each choice, as well as the section of the document where the choice is integrated. Keep the choices to the nature of the document: implementation decisions for a plan (file layout, step order, test and split strategy), design choices for a design, feature or issue clarifications for a requirement.

The question id must be the **first** column of every decision row. `pw skill`
routes on `has_consolidated_decisions`, which requires a row opening with
`| Qxx` (or the `No open questions` settled row) so that a table seeded when the
document was first written is not mistaken for a consolidated one. A table that
carries the question id in a later column is not recognized, and `pw skill`
routes back to another review round instead of forward to the next phase. Use
this normative shape, adding columns after the first as the document needs:

```md
| Question | Decision | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | ... | ... | ... |
```

The design-decisions table shown in [`process-draft.md`](process-draft.md),
which places `Question` in a later column, is a seeded design record written
with that instruction rather than a consolidation output, so it is deliberately
not the routing shape and must not be copied here.

Be mindful of the type of the document you are reviewing, because the kind of question you may consolidate or ask changes with it. A question that fits one type is out of place in another:

- a feature-request or an issue document takes only questions that clarify the feature or the issue itself: scope, expected behaviour, acceptance criteria, edge cases. No design choice, no implementation detail.
- a design document takes only questions about design choices: structure, data flow, trade-offs, interfaces, target behaviour. No implementation detail, and nothing that re-opens the feature or the issue.
- an implementation plan document takes only questions about implementation details: which files to create or change, the order of the steps, the gate-test and acceptance-test strategy, the line budget and split decisions, the per-step command checklist. No design choice, and nothing that re-opens the feature, the issue or the design.

Never carry a question across types: a plan review does not re-ask a design question the design already settled, and it does not re-clarify the feature or the issue. If the right place for a question is an earlier document, say so instead of asking it here.

Once all the questions are removed and their decision integrated, you now have many questions already and previously answered: ask yourself, do you have enough to start the next phase? That next phase is the design after a feature-request or an issue, the implementation plan after a design, and the coding itself after an implementation plan.

If you have no more questions, say so, and we will proceed to that next phase.

Do not try to ask too many questions, but ask as many as you can, as long as they are relevant and not redundant with already answered questions. The only reason to add new questions is that you think you cannot start the next step (the design, the implementation plan, or the coding) without having answers to those questions, and that those questions are not already answered in the document. Keep any new question within the nature of the current document: an implementation plan asks only implementation-detail questions, never design or feature questions. If you think you have enough information to start the next step, say so, and do not ask any new question.

Otherwise, review the exact document again, using related documents beside it
when provided. Write new questions into `a.<base>.open.questions.md`, then let
`oqm` place them as described below. Each question must come with options and
their pros and cons, a recommended choice with arguments, and an "Answer to
Qxx: option Y" line with the acceptance reason.

Follow the template defined in [`open-question.template.md`](../templates/open-question.template.md).

Always ask as many questions as possible on different parts of the document. The only reason to ask only one question would be the impossibility to ask other questions without first answering that one question.

## Consolidating and placing questions with oqm

Before running `oqm`, read [`../rules/run_commands.md`](../rules/run_commands.md).

Resolve `<LLM_SHARED_DIR>` as the absolute parent of the `instructions` folder
that contains this canonical file. Invoke `oqm.bat` by that full path from
PowerShell; do not guess a sibling `..\llm-shared` folder. The wrapper
self-locates llm-shared and loads the consuming project environment itself.

Do not edit the `## Open questions` section of the document by hand. Use the
`oqm` wrapper ([`oqm.bat`](../bin/oqm.bat), which runs
[`open_questions_md.py`](../tools/open_questions_md.py) through the consuming
project environment) to manage that section. It finds the project root,
resolves the exact path in any supported docs layout, and works through the
companion scratch file `a.<base>.open.questions.md` kept at the project root,
where `<base>` is the document name without its `.md` suffix.

The companion scratch file `a.<base>.open.questions.md` is the one file you author by hand: write the new open questions there, starting with the `## Open questions for the vX.Y.Z ...` line and following [`open-question.template.md`](../templates/open-question.template.md). `oqm` then removes any older `## Open questions` section from the document and appends the new section taken from `a.<base>.open.questions.md`, so the questions you wrote in the companion become the document's only `## Open questions` section.

The tool has three modes, each taking the exact repository-relative document path:

- `& "<LLM_SHARED_DIR>\bin\oqm.bat" <document-path> --create`: write an empty `a.<base>.open.questions.md` companion at the project root (truncating it when it already exists).
- `& "<LLM_SHARED_DIR>\bin\oqm.bat" <document-path> --strip`: drop the `## Open questions` line and every line after it from the document (a no-op when there is none).
- `& "<LLM_SHARED_DIR>\bin\oqm.bat" <document-path> --append`: add the `## Open questions` section of `a.<base>.open.questions.md` to the document, with one empty line before it.

Run these steps, in order:

1. `& "<LLM_SHARED_DIR>\bin\oqm.bat" <document-path> --strip` once you have integrated every existing answer into the document body and the decision table, to remove the consolidated `## Open questions` section.
2. Stop here when you have no new question to ask, and say you are ready for the next step.
3. `& "<LLM_SHARED_DIR>\bin\oqm.bat" <document-path> --create` to start an empty `a.<base>.open.questions.md` companion when you do have new questions.
4. Write your new questions into `a.<base>.open.questions.md`, starting with the `## Open questions for the vX.Y.Z ...` line and following the template.
5. `& "<LLM_SHARED_DIR>\bin\oqm.bat" <document-path> --append` to move the questions from `a.<base>.open.questions.md` into the document.
6. Present the placed questions in your reply as the mandatory three-column table described in "Presenting any follow-up questions" below — never as a bulleted list.

## Review-mode delegation after placing follow-up questions

Apply this block only when the workflow placed one or more new questions.
Honor an invocation containing `stop here` before checking exchange state: keep
the existing human-review stop and create no review artifact. Sample review
mode here rather than recalling an earlier listing: the marker sits in a dotted
directory a plain `ls` does not show, and the `a.*` ignore rule keeps it out of
`git status`. Prefer the status command,
`& "<LLM_SHARED_DIR>\rvw_status.bat"`, which resolves the artifact home itself;
falling back to a file test means checking `<artifact-home>/a.review-mode`
first, where `<artifact-home>` is `.reviews` unless a versioned
`.review-artifacts.ini` declares another `home` under `[review-artifacts]`, and
only then the project-root `a.review-mode` the loader keeps as its legacy
fallback. When review mode is absent because neither marker exists, keep that
same existing stop.

When the marker is present, run `pw skill spec-review-requestor` through the
launcher described in [`run-pw.md`](run-pw.md), then run the exact specialized
role command it prints for the reviewed document. Do not duplicate round
coordination here. A no-question pass skips this block and retains the existing
settled-document handoff below.

## Presenting any follow-up questions

This step is mandatory, not optional: when a consolidation round raises new questions, present them in your reply as a compact three-column table — one row per question, never a bulleted list — the same way the review skill does, so the human reads them at a glance:

| Q0x | Title | Recommended Answer |
| --- | --- | --- |
| Q01 | Short title of the question | The recommended option, in a few words |
| Q02 | ... | ... |

The full options, their pros and cons, and the `Answer to Qxx` line stay in the document and its companion (the [`open-question.template.md`](../templates/open-question.template.md) shape); the table is the at-a-glance summary, not a replacement. Use the compact table form of [`../rules/markdown.md`](../rules/markdown.md): one space around each cell, exactly three dashes in each header separator.

## Post-consolidation grouped commits and clean-tree gate

Apply this gate only when consolidation settles the document: every existing
answer is integrated, the decision table is present, the `## Open questions`
section is stripped, and no follow-up question remains. It runs after the
one-file pre-consolidation snapshot and after every consolidation edit, but
before any `pw skill`, review-exchange completion, or next-phase command.

The human's `Consolidate` choice, or a direct human invocation of this skill,
authorizes both the pre-consolidation snapshot commit and these final grouped
commits. Do not present another commit menu or ask for another go-ahead. Apply
the canonical [`group-commits-msg.md`](group-commits-msg.md) process through
its authorized consolidation continuation.

Run this sequence from the project root:

1. Run `git status --porcelain` to inventory every remaining non-ignored
   working-tree change. If it prints nothing, the repository already satisfies
   the clean-tree gate; continue to the final verification below.
2. When changes remain, run `git add -A` with no path restriction. This scope
   is intentional: every tracked, untracked, concurrent, or outside-origin
   non-ignored change must be included so consolidation cannot leave a dirty
   working tree. Confirm that `git diff --cached --name-only` is nonempty,
   while `git diff --name-only` and
   `git ls-files --others --exclude-standard` both print nothing. Never omit,
   restore, discard, or unstage a path merely to make the gate pass.
3. Run the `group-commits-msg` skill for the complete staged set (in Codex,
   `$llm-shared:group-commits-msg for all staged changes`). It must inspect and
   group every path from `git diff --cached --name-only`, write and format the
   project-root `a.commit`, and preserve the canonical dependency ordering and
   commit-message rules.
4. Because consolidation already has durable human authority, skip the normal
   group-commit menu. Run `& "<LLM_SHARED_DIR>\bin\gcba.bat" --root-a-commit --non-interactive`.
   Do not manually replay, combine, or amend the generated groups.
5. Confirm that the batch command succeeded and
   `git diff --cached --name-only` prints nothing. Then run
   `git status --porcelain`; it must print nothing.
6. If the final porcelain check reports a remaining path, do not run
   `pw skill`. Stage every remaining non-ignored change and repeat the same
   `group-commits-msg` plus non-interactive batch process once as a recovery
   pass. If `git status --porcelain` is still nonempty afterward, stop and
   report every remaining status entry. Never claim consolidation complete,
   complete a live review exchange, or enter the next phase with a dirty tree.

Only a successful grouped-commit pass followed by an empty
`git status --porcelain` grants the handoff below. Do not make another
non-ignored working-tree change between that clean check and `pw skill`.

## Handoff

Before using or showing a host-prefixed workflow command, read
[`../rules/command_prefix_char.md`](../rules/command_prefix_char.md) and use its
prefix rule.

When the consolidation settles the document — every open question answered, no new one raised, the `## Open questions` section stripped (step 1 above), the decisions table in place, all remaining changes committed through `group-commits-msg`, and `git status --porcelain` empty — hand the cycle on to the next phase, with no menu and no go-ahead. From the project root, in a PowerShell shell, run `pw skill` through its launcher (see [`run-pw.md`](run-pw.md) for the non-interactive invocation; the bare `pw` alias does not resolve in a tool shell):

- `pw skill`

`pw skill` reads the settled document on disk and prints the next-step command: `<command-prefix>write-design` from a feature-request or issue, `<command-prefix>write-plans` from a design, or `<command-prefix>implement-step` from a plan, carrying the plan's first step id read from the validation plan (not always `step 1`: a plan may open on a step 0 or any other first number), with the prefix selected by `command_prefix_char.md`. Read that line and run it straight away: the handoff is the go-ahead to perform the next step now, so do not stop to ask whether to proceed, and do not compose the next prompt yourself.

The settled handoff has one explicit hold: when the invocation argument contains the literal phrase `stop here`, or the human has explicitly asked not to start the next phase (for a plan, not to start the implementation), do not run the printed command. Still settle the document, still run `pw skill`, then present its printed line as the "Next step" command with the Tab-completable hint, and stop. The hold changes only who launches the next phase, never the on-disk state; without such an explicit instruction the default above stands and the next phase starts now.

When new open questions remain, append them with `oqm`, present them in the
three-column table, and stop for another review round. Leave the next step as
`<command-prefix>consolidate-then-review-ask-questions on <document-path>`, using
the same exact path, plus the gray Tab-completable hint where supported. Do not
run that handoff.
