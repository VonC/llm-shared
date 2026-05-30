# Consolidate then review and ask new questions

ultrathink: take the time to reason through the document deeply before drafting questions, so each question targets a real ambiguity rather than a surface-level prompt for elaboration.

Check your prompt for type (feature-request, issue, design or plan), vX.Y.Z and topic (for instance "design v9.3.0 sentinels").

Consolidate `docs\<type>.vX.Y.Z.<topic>.md` by integrating answers given to existing questions in the "Open questions for the vX.Y.Z design" section. Do not leave the question and their recommended options; "consolidate" means integrate the answers chosen into the document (with a summary of the question and its options).

You need to remove `Qxx:` sections and integrate their answers within the document. Make sure all the questions are removed and their decision integrated before adding any new question. Once every answer is integrated into the document body, remove the whole `## Open questions` section with `oqm <type>.vX.Y.Z.<topic>.md --strip` (see "Consolidating and placing questions with oqm" below).

Create a decision table in the "Design decisions" section of the document, summarizing all the design choices that have been made, with their arguments and the alternatives that were rejected. Do reference the number of the question (Qxx) that led to each design choice, as well as the section of the document where the design choice is integrated.

Be mindful of the type of the document you are reviewing:

- a feature-request or an issue document should not include any design choice question, but only questions about clarifying the feature or the issue.
- a design document should not include any implementation detail, and should not include any question about implementation details, but only questions about design choices.
- an implementation plan document should not include any design choice question, but only questions about implementation details.

Once all the questions are removed and their decision integrated, you now have many questions already and previously answered: ask yourself, do you have enough to start the implementation plan document?

If you have no more questions, say so, and we will proceed with the implementation plan document.

Do not try to ask too many questions, but ask as many as you can, as long as they are relevant and not redundant with already answered questions. The only reason to add new questions is that you think you cannot start the next step (design or implementation) without having answers to those questions, and that those questions are not already answered in the document. If you think you have enough information to start the next step, say so, and do not ask any new question.

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
