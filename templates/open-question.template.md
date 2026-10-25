# Template for open questions about a feature request, issue, design or implementation plan

Only include the `## Open questions` section and below, do not include the title and this introduction.

Keep every question within the nature of its document, because the kind of question changes with the type: a feature-request or issue asks only to clarify the feature or the issue, a design asks only about design choices, and an implementation plan asks only about implementation details. A question that fits one type is out of place in another.

## Open questions for the vX.Y.Z feature request, issue, design or implementation plan

### Qxx: {question title}

Question description: a clear and concise description of the question, including the context, the problem statement, and any relevant information that can help to understand the question and its implications.

#### BBQ for Qxx

Short section reformulating the question description in BBQ-style, to clarify the stakes and the impact of the question, and to make it easier to understand why the question matters and what are the implications of each option.

Always close the BBQ with an explicit mapping that names, for each element of the analogy, the concrete concept it stands for, so the reader never has to guess the correspondence. Write it as one "In this picture: ..." sentence or a short list, for example: "In this picture: the badge reader is the session dependency, the locked corridor is the `/api/admin` prefix, and the end-of-job inspection is the acceptance test suite." An analogy element with no named concept is a gap to fix before publishing the question.

#### Options for Qxx

- Option X1: (with pros and cons: you can list multiple pros and cons for each option, but at least one pro and one con for each option)
  - pro:
  - con:
- Option X2: (with pros and cons)
  - pro:
  - con:
- Option X3: (with pros and cons)
  - pro:
  - con:

#### Recommended option for Qxx (with arguments for this choice)

Option XY: Do list the arguments for the recommended option, and explain why it is the best choice among the options, taking into account the pros and cons of each option, as well as the overall goals and constraints of the feature request, issue, design or implementation plan.

#### Answer to Qxx: option XY (with reason why it must be accepted as the answer)

Option XY: Do not leave empty, but explain why the user should consider the recommended option as the answer to the question, and why it should be accepted as the answer, taking into account the arguments for the recommended option, as well as the overall goals and constraints of the feature request, issue, design or implementation plan.

User decision: pending

The answer above is a proposal until the user explicitly chooses. On that
choice, replace the active pending line with
`User decision: confirmed — <choice and agreed qualifications>` and record the
reason, relevant comments, and date in this answer section. Do not generate a
confirmed record from the recommendation or reviewer agreement. A deferral
uses `User decision: deferred` and remains undecided. Preserve existing
`Confirmed by the user: ...` records; do not rewrite older questions merely
to adopt this format. Quote superseded status text when retaining history so
it cannot be mistaken for a second active decision.
