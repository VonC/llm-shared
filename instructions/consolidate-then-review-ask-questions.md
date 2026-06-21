# Consolidate then review and ask new questions

ultrathink: take the time to reason through the document deeply before drafting questions, so each question targets a real ambiguity rather than a surface-level prompt for elaboration.

Check your prompt for type (feature-request, issue, design or plan), vX.Y.Z and topic (for instance "design v9.3.0 sentinels").

Consolidate `docs\<type>.vX.Y.Z.<topic>.md` by integrating answers given to existing questions in its "Open questions for the vX.Y.Z ..." section (the section names the document type: feature request, issue, design or implementation plan). Do not leave the question and their recommended options; "consolidate" means integrate the answers chosen into the document (with a summary of the question and its options).

You need to remove `Qxx:` sections and integrate their answers within the document. Make sure all the questions are removed and their decision integrated before adding any new question. Once every answer is integrated into the document body, remove the whole `## Open questions` section with `oqm <type>.vX.Y.Z.<topic>.md --strip` (see "Consolidating and placing questions with oqm" below).

Create a decision table in the document's decisions section, naming that section for the document type: "Design decisions" for a design, "Implementation decisions" for an implementation plan, or "Requirement clarifications" for a feature-request or an issue. Summarize all the choices that have been made, with their arguments and the alternatives that were rejected. Do reference the number of the question (Qxx) that led to each choice, as well as the section of the document where the choice is integrated. Keep the choices to the nature of the document: implementation decisions for a plan (file layout, step order, test and split strategy), design choices for a design, feature or issue clarifications for a requirement.

Be mindful of the type of the document you are reviewing, because the kind of question you may consolidate or ask changes with it. A question that fits one type is out of place in another:

- a feature-request or an issue document takes only questions that clarify the feature or the issue itself: scope, expected behaviour, acceptance criteria, edge cases. No design choice, no implementation detail.
- a design document takes only questions about design choices: structure, data flow, trade-offs, interfaces, target behaviour. No implementation detail, and nothing that re-opens the feature or the issue.
- an implementation plan document takes only questions about implementation details: which files to create or change, the order of the steps, the gate-test and acceptance-test strategy, the line budget and split decisions, the per-step command checklist. No design choice, and nothing that re-opens the feature, the issue or the design.

Never carry a question across types: a plan review does not re-ask a design question the design already settled, and it does not re-clarify the feature or the issue. If the right place for a question is an earlier document, say so instead of asking it here.

Once all the questions are removed and their decision integrated, you now have many questions already and previously answered: ask yourself, do you have enough to start the next phase? That next phase is the design after a feature-request or an issue, the implementation plan after a design, and the coding itself after an implementation plan.

If you have no more questions, say so, and we will proceed to that next phase.

Do not try to ask too many questions, but ask as many as you can, as long as they are relevant and not redundant with already answered questions. The only reason to add new questions is that you think you cannot start the next step (the design, the implementation plan, or the coding) without having answers to those questions, and that those questions are not already answered in the document. Keep any new question within the nature of the current document: an implementation plan asks only implementation-detail questions, never design or feature questions. If you think you have enough information to start the next step, say so, and do not ask any new question.

Otherwise, review that `docs\<type>.vX.Y.Z.<topic>.md` document (see other `docs\<other_type>.vX.Y.Z.<topic>.md` documents in your context if provided), and write your new questions into the companion scratch file `a.<base>.open.questions.md`, following the template, then let `oqm` place them into the document as described below. Each question must comes with options (and their pros and cons), as well as a recommended choice (with arguments) from those options, as well as "Answer to Qxx: option Y" repeating the recommended option, but adding a reason why it must be accepted as the answer.

Follow the template defined in [`open-question.template.md`](../templates/open-question.template.md).

Always ask as many questions as possible on different parts of the document. The only reason to ask only one question would be the impossibility to ask other questions without first answering that one question.

## Consolidating and placing questions with oqm

Do not edit the `## Open questions` section of the document by hand. Use the `oqm` tool ([`open_questions_md.py`](../tools/open_questions_md.py), alias `oqm`) to manage that section. It finds the project root, resolves the document under `docs\` or `docs\vX.Y.Z\`, and works through the companion scratch file `a.<base>.open.questions.md` kept at the project root, where `<base>` is the document name without its `.md` suffix.

The companion scratch file `a.<base>.open.questions.md` is the one file you author by hand: write the new open questions there, starting with the `## Open questions for the vX.Y.Z ...` line and following [`open-question.template.md`](../templates/open-question.template.md). `oqm` then removes any older `## Open questions` section from the document and appends the new section taken from `a.<base>.open.questions.md`, so the questions you wrote in the companion become the document's only `## Open questions` section.

The tool has three modes, each taking the document file name:

- `oqm <type>.vX.Y.Z.<topic>.md --create`: write an empty `a.<base>.open.questions.md` companion at the project root (truncating it when it already exists).
- `oqm <type>.vX.Y.Z.<topic>.md --strip`: drop the `## Open questions` line and every line after it from the document (a no-op when there is none).
- `oqm <type>.vX.Y.Z.<topic>.md --append`: add the `## Open questions` section of `a.<base>.open.questions.md` to the document, with one empty line before it.

Run these steps, in order:

1. `oqm <type>.vX.Y.Z.<topic>.md --strip` once you have integrated every existing answer into the document body and the decision table, to remove the consolidated `## Open questions` section.
2. Stop here when you have no new question to ask, and say you are ready for the next step.
3. `oqm <type>.vX.Y.Z.<topic>.md --create` to start an empty `a.<base>.open.questions.md` companion when you do have new questions.
4. Write your new questions into `a.<base>.open.questions.md`, starting with the `## Open questions for the vX.Y.Z ...` line and following the template.
5. `oqm <type>.vX.Y.Z.<topic>.md --append` to move the questions from `a.<base>.open.questions.md` into the document.

If the `oqm` alias is not available in your shell, call the script directly with `python <LLM_SHARED_DIR>\tools\open_questions_md.py <type>.vX.Y.Z.<topic>.md <mode>`.
