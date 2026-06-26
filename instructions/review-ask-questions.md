# Review and ask open questions

ultrathink: take the time to reason through the document deeply before drafting questions, so each question targets a real ambiguity rather than a surface-level prompt for elaboration.

Check your prompt for type (feature-request, issue, design or plan), vX.Y.Z and topic (for instance "design v9.3.0 sentinels").

Be mindful of the type of the document you are reviewing, because the kind of question you may ask changes with it. A question that fits one type is out of place in another:

- a feature-request or an issue document takes only questions that clarify the feature or the issue itself: scope, expected behaviour, acceptance criteria, edge cases. No design choice, no implementation detail.
- a design document takes only questions about design choices: structure, data flow, trade-offs, interfaces, target behaviour. No implementation detail, and nothing that re-opens the feature or the issue.
- an implementation plan document takes only questions about implementation details: which files to create or change, the order of the steps, the gate-test and acceptance-test strategy, the line budget and split decisions, the per-step command checklist. No design choice, and nothing that re-opens the feature, the issue or the design.

Never carry a question across types: a plan review does not re-ask a design question the design already settled, and it does not re-clarify the feature or the issue. If the right place for a question is an earlier document, say so instead of asking it here.

Review that `docs\<type>.vX.Y.Z.<topic>.md` document (see other `docs\<other_type>.vX.Y.Z.<topic>.md` documents in your context if provided), and write your new questions into the companion scratch file `a.<base>.open.questions.md`, following the template, then let `oqm` place them into the document as described below. Each question must comes with options (and their pros and cons), as well as a recommended choice (with arguments) from those options, as well as "Answer to Qxx: option Y" repeating the recommended option, but adding a reason why it must be accepted as the answer.

Follow the template defined in [`open-question.template.md`](../templates/open-question.template.md).

Always ask as many questions as possible on different parts of the document. The only reason to ask only one question would be the impossibility to ask other questions without first answering that one question.

## Placing the new questions with oqm

Before running `oqm`, read [`../rules/run_commands.md`](../rules/run_commands.md).

Do not edit the `## Open questions` section of the document by hand. Use the
`oqm` wrapper ([`oqm.bat`](../bin/oqm.bat), which runs
[`open_questions_md.py`](../tools/open_questions_md.py) through the consuming
project environment) to manage that section. It finds the project root,
resolves the document under `docs\` or `docs\vX.Y.Z\`, and works through the
companion scratch file `a.<base>.open.questions.md` kept at the project root,
where `<base>` is the document name without its `.md` suffix.

The companion scratch file `a.<base>.open.questions.md` is the one file you author by hand: write the new open questions there, starting with the `## Open questions for the vX.Y.Z ...` line and following [`open-question.template.md`](../templates/open-question.template.md). `oqm` then removes any older `## Open questions` section from the document and appends the new section taken from `a.<base>.open.questions.md`, so the questions you wrote in the companion become the document's only `## Open questions` section.

The tool has three modes, each taking the document file name:

- `cmd /d /v:on /c "..\llm-shared\bin\oqm.bat <type>.vX.Y.Z.<topic>.md --create"`: write an empty `a.<base>.open.questions.md` companion at the project root (truncating it when it already exists).
- `cmd /d /v:on /c "..\llm-shared\bin\oqm.bat <type>.vX.Y.Z.<topic>.md --strip"`: drop the `## Open questions` line and every line after it from the document (a no-op when there is none).
- `cmd /d /v:on /c "..\llm-shared\bin\oqm.bat <type>.vX.Y.Z.<topic>.md --append"`: add the `## Open questions` section of `a.<base>.open.questions.md` to the document, with one empty line before it.

Run these steps for the document you are reviewing:

1. `cmd /d /v:on /c "..\llm-shared\bin\oqm.bat <type>.vX.Y.Z.<topic>.md --strip"` to drop any prior `## Open questions` section from the document.
2. `cmd /d /v:on /c "..\llm-shared\bin\oqm.bat <type>.vX.Y.Z.<topic>.md --create"` to start an empty `a.<base>.open.questions.md` companion.
3. Write your new questions into `a.<base>.open.questions.md`, starting with the `## Open questions for the vX.Y.Z ...` line and following the template.
4. `cmd /d /v:on /c "..\llm-shared\bin\oqm.bat <type>.vX.Y.Z.<topic>.md --append"` to move the questions from `a.<base>.open.questions.md` into the document.
5. Present the placed questions in your reply as the mandatory three-column table described in "Presenting the review questions" below — never as a bulleted list.


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

The review is a stop, not an automatic chain: a human answers the questions before the consolidation. Leave the next step in two forms rather than running the next skill: the "Next step" command — `<command-prefix>consolidate-then-review-ask-questions on docs/<doc type>.vX.Y.Z.<slug>.md` you just reviewed, carrying the reviewed document name so it is ready to run once the answers are in — and, in addition, a hint: where the host can render a gray, Tab-completable prompt, show that same command as the ghost prompt the human can accept with a keystroke rather than retype (the reliable trigger is still to be studied).

When the review round raises no question at all, do not leave the document with no section: write a one-row decisions table — the consolidate step's `Requirement clarifications`, `Design decisions`, or `Implementation decisions` section, with a single row such as "No open questions, all decisions made" — so the on-disk state reads as settled. From that settled state `pw skill` advances straight to the next phase, skipping a consolidate round.
