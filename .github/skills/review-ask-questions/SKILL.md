---
name: review-ask-questions
description: 'Review the <type>.vX.Y.Z.<topic>.md document, and add an "Open-ended questions" section at the end of the document, with all the open questions you have about the type (feature-request, issue, design or plan), based on your review of that document. Each question must include pros and cons for each option, as well as a recommended choice with arguments for that choice, and an answer.'
user-invocable: true
metadata:
  - "This skill is used to review a <type>.vX.Y.Z.<topic>.md document, and add an "Open-ended questions" section at the end of the document, with all the open questions you have about the type (feature-request, issue, design or plan), based on your review of that document."
argument-hint: 'Provide the type, version and topic of the document, for example "design v9.3.0 sentinels".'
model: claude-sonnet
---

Check your prompt for type (feature-request, issue, design or plan), vX.Y.Z and topic (for instance "design v9.3.0 sentinels")

Be mindful of the type of the document you are reviewing: 

- a feature-request or an issue document should not include any design choice question, but only questions about clarifying the feature or the issue.
- a design document should not include any implementation detail, and should not include any question about implementation details, but only questions about design choices.
- an implementation plan document should not include any design choice question, but only questions about implementation details.

Review that `docs\<type>.vX.Y.Z.<topic>.md` document (see other `docs\<other_type>.vX.Y.Z.<topic>.md` documents in your context if provided), and leave your new questions directly edited in that document. Each question must comes with options (and their pros and cons), as well as a recommended choice (with arguments) from those options, as well as "Answer to Qxx: option Y" repeating the recommended option, but adding a reason why it must be accepted as the answer.

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

