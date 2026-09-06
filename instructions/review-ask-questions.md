# Review and ask open questions

ultrathink: take the time to reason through the document deeply before drafting questions, so each question targets a real ambiguity rather than a surface-level prompt for elaboration.

Check your prompt for type (feature-request, issue, design or plan), vX.Y.Z and topic (for instance "design v9.3.0 sentinels").

Be mindful of the type of the document you are reviewing, because the kind of question you may ask changes with it. A question that fits one type is out of place in another:

- a feature-request or an issue document takes only questions that clarify the feature or the issue itself: scope, expected behaviour, acceptance criteria, edge cases. No design choice, no implementation detail.
- a design document takes only questions about design choices: structure, data flow, trade-offs, interfaces, target behaviour. No implementation detail, and nothing that re-opens the feature or the issue.
- an implementation plan document takes only questions about implementation details: which files to create or change, the order of the steps, the gate-test and acceptance-test strategy, the line budget and split decisions, the per-step command checklist. No design choice, and nothing that re-opens the feature, the issue or the design.

Never carry a question across types: a plan review does not re-ask a design question the design already settled, and it does not re-clarify the feature or the issue. If the right place for a question is an earlier document, say so instead of asking it here.

Review the exact `<effort-dir>\<type>.vX.Y.Z.<topic>.md` document named in the
prompt (see other documents beside it when provided), and write your new
questions into the companion scratch file `a.<base>.open.questions.md`,
following the template, then let `oqm` place them into the document as described
below. Read [`../rules/docs_layout.md`](../rules/docs_layout.md) and preserve the
document's selected effort directory. Each question must come with options and
their pros and cons, a recommended choice with arguments, and an "Answer to
Qxx: option Y" line that repeats the recommendation and gives the acceptance
reason.

Follow the template defined in [`open-question.template.md`](../templates/open-question.template.md).

Always ask as many questions as possible on different parts of the document. The only reason to ask only one question would be the impossibility to ask other questions without first answering that one question.

## Placing the new questions with oqm

Before running `oqm`, read [`../rules/run_commands.md`](../rules/run_commands.md).

Resolve `<LLM_SHARED_DIR>` as the absolute parent of the `instructions` folder
that contains this canonical file. Invoke `oqm.bat` by that full path from
PowerShell; do not guess a sibling `..\llm-shared` folder. The wrapper
self-locates llm-shared and loads the consuming project environment itself.

Do not edit the `## Open questions` section of the document by hand. Use the
`oqm` wrapper ([`oqm.bat`](../bin/oqm.bat), which runs
[`open_questions_md.py`](../tools/open_questions_md.py) through the consuming
project environment) to manage that section. It finds the project root,
resolves the exact repository-relative path in any supported docs layout, and works through the
companion scratch file `a.<base>.open.questions.md` kept at the project root,
where `<base>` is the document name without its `.md` suffix.

The companion scratch file `a.<base>.open.questions.md` is the one file you author by hand: write the new open questions there, starting with the `## Open questions for the vX.Y.Z ...` line and following [`open-question.template.md`](../templates/open-question.template.md). `oqm` then removes any older `## Open questions` section from the document and appends the new section taken from `a.<base>.open.questions.md`, so the questions you wrote in the companion become the document's only `## Open questions` section.

The tool has three modes, each taking the exact repository-relative document path:

- `& "<LLM_SHARED_DIR>\bin\oqm.bat" <document-path> --create`: write an empty `a.<base>.open.questions.md` companion at the project root (truncating it when it already exists).
- `& "<LLM_SHARED_DIR>\bin\oqm.bat" <document-path> --strip`: drop the `## Open questions` line and every line after it from the document (a no-op when there is none).
- `& "<LLM_SHARED_DIR>\bin\oqm.bat" <document-path> --append`: add the `## Open questions` section of `a.<base>.open.questions.md` to the document, with one empty line before it.

Run these steps for the document you are reviewing:

1. `& "<LLM_SHARED_DIR>\bin\oqm.bat" <document-path> --strip` to drop any prior `## Open questions` section from the document.
2. `& "<LLM_SHARED_DIR>\bin\oqm.bat" <document-path> --create` to start an empty `a.<base>.open.questions.md` companion.
3. Write your new questions into `a.<base>.open.questions.md`, starting with the `## Open questions for the vX.Y.Z ...` line and following the template.
4. `& "<LLM_SHARED_DIR>\bin\oqm.bat" <document-path> --append` to move the questions from `a.<base>.open.questions.md` into the document.
5. Present the placed questions in your reply as the mandatory three-column table described in "Presenting the review questions" below — never as a bulleted list.

## Review-mode delegation after placing questions

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
coordination here. A no-question pass skips this block and retains its existing
settled-document handoff.

## Presenting the review questions

This step is mandatory, not optional: every time you post open questions, present them in your reply as a compact three-column table — one row per question, never a bulleted list — so the human reads them at a glance:

| Q0x | Title | Recommended Answer |
| --- | --- | --- |
| Q01 | Short title of the question | The recommended option, in a few words |
| Q02 | ... | ... |

The full options, their pros and cons, and the `Answer to Qxx` line stay in the document and its companion (the [`open-question.template.md`](../templates/open-question.template.md) shape); the table is the at-a-glance summary, not a replacement. Use the compact table form of [`../rules/markdown.md`](../rules/markdown.md): one space around each cell, exactly three dashes in each header separator.

## Handoff

Before using or showing a host-prefixed workflow command, read
[`../rules/command_prefix_char.md`](../rules/command_prefix_char.md) and use its
prefix rule.

The review is a stop, not an automatic chain: a human answers the questions
before consolidation. Leave the next step in two forms rather than running it:
the "Next step" command
`<command-prefix>consolidate-then-review-ask-questions on <document-path>` using
the exact path just reviewed, plus the same command as a gray, Tab-completable
hint where the host supports one.

When the review round raises no question at all, do not leave the document with no section: write a one-row decisions table — the consolidate step's `Requirement clarifications`, `Design decisions`, or `Implementation decisions` section, with a single row such as "No open questions, all decisions made" — so the on-disk state reads as settled. Keep the words "No open questions" verbatim in that row: the `pw` routing reads that row (or a `| Qxx` row) as the consolidated signal, and a decisions heading without one still routes to a review. From that settled state, run `pw skill` and run the printed command straight away, the same settled handoff as the consolidate skill: from a plan that command is `<command-prefix>implement-step` on the plan's first step (its id read from the validation plan, not always 1). The same explicit hold applies here: with `stop here` in the invocation argument, or a human instruction not to start the next phase, present the printed line as the "Next step" command and stop instead of running it.
