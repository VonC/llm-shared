# Question explanation template

Render one question at a time. The instruction owns the fixed batch start and
percentage; the scanner supplies question identities and decision evidence.
Replace placeholders, and omit an analogy only when it would not clarify.

## Where this question sits

Open every explanation with this table, filled from the continuation note, so
the user sees what is being decided before the question itself. Write
`not resolved` for a value the context step could not establish; never guess.

| Context | Value |
| --- | --- |
| Umbrella | {`<umbrella-slug>`, item {x}/{N}: {key title} ({completed}/{N} items completed), umbrella draft `<path>`; or `none, standalone topic`} |
| Topic | {version and slug, as the `topic` line of `pw progress`} |
| Phase | {phase and position, such as `requirement (2/5)`} |
| Draft | {path of the topic's own draft} |
| Document | {path of the document holding these questions, and its type} |
| Questions | {question {k} of {B} in this batch, {first-id} to {last-id}; {U} of {Q} questions in the document still undecided} |
| Review | {live exchange, round and gate, or no live exchange} |

## Progress and explanation

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
