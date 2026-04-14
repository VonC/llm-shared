---
name: consolidate-then-review-ask-questions
description: 'Consolidate answer to existing open questions (removing the open-ended questions section entirely), update a decision table, and  assert if new questions need to be asked. Review the amended document: If new questions need to be asked, create a new section for open questions, and ask as many questions as possible, with options and recommended choice, following the template provided in the prompt.'
user-invocable: true
metadata:
  - "This skill is used to consolidate answer to existing open questions (removing the open-ended questions section entirely), update a decision table, and  assert if new questions need to be asked. If new questions need to be asked, create a new section for open questions, and ask as many questions as possible, with options and recommended choice, following the template provided in the prompt."
  - "The argument hint for this skill is 'Provide the version and topic of the design document, for example "v9.3.0" and "sentinels".'"
argument-hint: 'Provide the version and topic of the design document, for example "v9.3.0" and "sentinels".'
---

Check your prompt for type (feature-request, issue, design or plan), vX.Y.Z and topic (for instance "design v9.3.0 sentinels")

Consolidate `docs\<type>.vX.Y.Z.<topic>.md` by integrating answers given to existing questions in the "Open questions for the vX.Y.Z design" section. Do not leave the question and their recommended options, "consolidate" means integrate the answers chosen into the document (with a summary of the question and its options).

You need to remove `Qxx:` sections and integrate their answers within the document. Make sure all the questions are removed and their decision integrated before adding any new question.

Be mindful of the type of the document you are reviewing: 

- a feature-request or an issue document should not include any design choice question, but only questions about clarifying the feature or the issue.
- a design document should not include any implementation detail, and should not include any question about implementation details, but only questions about design choices.
- an implementation plan document should not include any design choice question, but only questions about implementation details.

Once all the questions are removed and their decision integrated, you now have many questions already and previously answered: ask yourself, do you have enough to start the implementation plan document?

If you have no more questions, say so, and we will proceed with the implementation plan document.

Otherwise, review that `docs\<type>.vX.Y.Z.<topic>.md` document (see other `docs\<other_type>.vX.Y.Z.<topic>.md` documents in your context if provided), and leave your new questions directly edited in that document. Each question must comes with options (and their pros and cons), as well as a recommended choice (with arguments) from those options, as well as "Answer to Qxx: option Y" repeating the recommended option, but adding a reason why it must be accepted as the answer.

Follow the template:

```md
## Open questions for the vX.Y.Z design

### Qxx: <question title>

#### Options

- Option X1: (with pros and cons)
- Option X2: (with pros and cons)
- Option X3: (with pros and cons)

#### Recommended option (with arguments for this choice)

#### Answer to Qxx: option Y (with reason why it must be accepted as the answer)
```

Always ask as many questions as possible on different parts of the document. The only reason to ask only one question would be the impossibility to ask other questions without first answering that one question.

