# Question explanation template

Render one question at a time. The instruction owns the fixed batch start and
percentage; the scanner supplies question identities and decision evidence.
Replace placeholders, and omit an analogy only when it would not clarify.

## Progress and context

**{question-id}/{last-question-id} {percentage}% — {question title}**

Status: awaiting your decision. Progress indicates position in this batch.

{Explain the concrete behavior being decided and why it matters.}

**Example**

{A realistic scenario showing the consequences of the choice.}

**BBQ explanation**

{A short analogy. Close with an explicit mapping from each analogy element
to the real concept; do not make the user infer the correspondence.}

| Option | Resulting behavior | Advantages | Drawbacks |
| --- | --- | --- | --- |
| A | {behavior} | {pros} | {cons} |
| B | {behavior} | {pros} | {cons} |

**Recommendation: {option}**

{Reasoning, assumptions, and relevant earlier decisions.}

**Effects on other questions**

{Affected decisions, conditional questions, and possible follow-up issues.}

## Decision prompt

{Ask for an option, an amendment, or further explanation. Never pre-record
the recommended option as a confirmed user choice.}
