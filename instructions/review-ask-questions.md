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
companion scratch file `a.<base>.open.questions.md` kept in the review artifact
home (`.reviews` unless `.review-artifacts.ini` declares another home, see
[`../rules/artifact_files.md`](../rules/artifact_files.md)), where `<base>` is
the document name without its `.md` suffix. `oqm` moves a companion left at the
project root by an older run into the artifact home on first use; never create
the companion at the project root.

The companion scratch file `a.<base>.open.questions.md` is the one file you author by hand: write the new open questions there, starting with the `## Open questions for the vX.Y.Z ...` line and following [`open-question.template.md`](../templates/open-question.template.md). `oqm` then removes any older `## Open questions` section from the document and appends the new section taken from `a.<base>.open.questions.md`, so the questions you wrote in the companion become the document's only `## Open questions` section.

The tool has three modes, each taking the exact repository-relative document path:

- `& "<LLM_SHARED_DIR>\bin\oqm.bat" <document-path> --create`: write an empty `a.<base>.open.questions.md` companion in the artifact home (truncating it when it already exists) and print its full path.
- `& "<LLM_SHARED_DIR>\bin\oqm.bat" <document-path> --strip`: drop the `## Open questions` line and every line after it from the document (a no-op when there is none).
- `& "<LLM_SHARED_DIR>\bin\oqm.bat" <document-path> --append`: add the `## Open questions` section of `a.<base>.open.questions.md` to the document, with one empty line before it.

Review never authorizes consolidation. Preserve existing question IDs,
options, recommendations, explanations, and recorded answers. Removing
answered question blocks or replacing them with decision rows requires the
express human intent gate in
[`consolidate-then-review-ask-questions.md`](consolidate-then-review-ask-questions.md).
A bare combined-skill invocation with a document path does not pass that gate.

Run these steps only when adding or amending questions:

1. Read and retain the complete existing `## Open questions` section before
   creating a companion. Do not run `--strip` during review.
2. `& "<LLM_SHARED_DIR>\bin\oqm.bat" <document-path> --create` to start an empty
   companion, then copy every existing question and answer into it unchanged.
   When there are no existing questions, start with the required section heading.
3. Add new questions with unused IDs or apply accepted wording edits in the
   companion. Verify that all prior question IDs, options, and human answers
   remain present before replacing the document's section.
4. `& "<LLM_SHARED_DIR>\bin\oqm.bat" <document-path> --append` to replace the
   section with that complete preserved-and-amended set.
5. Present newly placed questions in the mandatory three-column table below.
   If there are no question changes, leave the section and companion untouched.

## Independent review gate after the writer assessment

Read and follow [the independent specification review gate](../rules/specification-review-gate.md).
Apply it to every assessment, including a no-question pass. Honor `stop here`,
preserve existing live exchanges, and freshly sample review mode. The gate
defines the disabled-mode stop and the only explicit human waiver; author
decisions are not evidence of independent review.

When the gate requires publication, run `pw skill spec-review-requestor` through the
launcher described in [`run-pw.md`](run-pw.md), then run the exact specialized
role command only if it targets the exact document being reviewed. If the topic
resolver names another existing specification, invoke the specialized requestor
on this exact document and its umbrella instead. Do not manufacture questions,
duplicate coordination, or advance because routing produced no command.

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
and separately expresses intent before consolidation. Leave the next step in two forms rather than running it:
the "Next step" command
`<command-prefix>consolidate-then-review-ask-questions on <document-path> consolidate the answered questions` using
the exact path just reviewed, plus the same command as a gray, Tab-completable
hint where the host supports one.

When the document has no existing questions and the writer raises none, record that assessment in the document's
appropriate decisions section with a row containing "No open questions".
Preserve any existing decision rows. This marks the author's assessment as
settled; it does not record independent review or authorize advancement.
Apply the independent review gate above before invoking the ordinary next-phase
handoff. After an explicit human waiver, follow the consolidation handoff and
any human hold. Never start planning or implementation solely because the
writer found no questions.

When existing question blocks are present and no new question is needed, keep
those blocks and answers intact and report only that no additional questions
were found. Do not replace them with a settled decision marker.
