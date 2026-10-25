# Question decision scanner

`tools/question_decisions.py` reads a Markdown specification and reports
explicit human decisions. It uses only the Python standard library and never
edits the document, creates artifacts, or persists explanation progress.

## Invocation model

The explanation skill runs this scanner before selecting questions and after
recording answers. Invoke the launcher directly for a read-only status check.

## Command

Resolve the absolute llm-shared directory, then run from the consuming project:

```powershell
& "<LLM_SHARED_DIR>\bin\question_decisions.bat" docs/v1.4.0/feature-request.v1.4.0.route-warnings.md
& "<LLM_SHARED_DIR>\bin\question_decisions.bat" docs/v1.4.0/feature-request.v1.4.0.route-warnings.md --after Q59
```

The launcher uses llm-shared's Python environment. Relative document paths are
resolved from the caller's current directory. Output is JSON. Exit `0` means a
successful scan, including when questions remain undecided. Exit `2` means
invalid input or ambiguous/conflicting decision records; never interpret it as
completion. Launcher setup failures return exit `1`.

## Recognized structure and evidence

The document contains at most one level-two `Open questions` or
`Open-ended questions` section. Each question has a `### Qxx: Title` heading
and its own `#### Answer to Qxx` section. Numeric IDs are positive, normalized
to at least two digits, and unique. Gaps are allowed; `position` is the ordinal
document position, independent of the numeric ID.

Only these explicit records in the answer body count as confirmed:

```text
User decision: confirmed — Option A, including the agreed clarification.
Confirmed by the user: Option A.
Confirmed by the user on 2026-10-21: Option A, with the examples above.
```

The canonical marker also accepts an en dash, colon, or hyphen separator.
Recognition is case-insensitive. The dated legacy form uses `YYYY-MM-DD`.
The choice must start on the marker line; subsequent lines may qualify it.

`Proposed`, `Awaiting user confirmation`, and `User decision:` followed by
`pending`, `deferred`, `undecided`, or `reopened` remain undecided. Missing
answers, recommendations, and filled proposed answer headings do not constitute
a user decision. A record in another section, a Markdown fence, a blockquote,
or an HTML comment is not active evidence. The answer body ends at the next
heading of level four or higher in the document hierarchy.

Conflicting records, multiple confirmations, and unrecognized decision markers
produce diagnostics and exit `2`. Move superseded records into a quoted
historical note when recording a new explicit decision. Duplicate/malformed
question headings, duplicate or mismatched answer headings, multiple question
sections, unclosed fences, empty files, unreadable files, and invalid UTF-8
also fail. A valid document without any questions returns an empty result;
question headings without an open-questions section are an error.

## JSON fields

| Field | Meaning |
| --- | --- |
| `document`, `document_sha256` | Absolute input path and digest of its original bytes |
| `question_count`, `last_question` | Number of questions and final question ID, or null |
| `undecided_count`, `first_undecided`, `last_undecided` | Full-document unresolved count and endpoints, or null endpoints |
| `next_undecided` | First undecided ID strictly after `--after`, or first undecided without a cursor; null at the end |
| `questions` | Ordered entries: `id`, `position`, `title`, `line`, `status`, `reason`, `decision_line` |
| `diagnostics` | Ambiguous or conflicting record messages requiring reconciliation |
| `error` | Input failure message instead of a report |

`status` is `confirmed` or `undecided`. `decision_line` is the one-based source
line for explicit confirmation, otherwise null. `--after` requires an existing
question ID. It changes only `next_undecided`; it never hides earlier unresolved
questions from the count or endpoints. A null next cursor is not proof that
every question is decided: perform a full scan before completing discussion.

## Explanation progress and continuation

The [skill](../../instructions/explain-undecided-questions.md), not this utility,
saves the initial first-undecided position `I`, total question count `Total`,
their IDs, and ordered batch IDs. For current position `x`, it displays
`Qx/QTotal` with the actual IDs and this percentage:

```text
round(100 * (x - I + 1) / (Total - I + 1))
```

For Q59–Q73, `I=59`, `Total=73`: Q59 displays 7%, Q60 13%, Q73 100%.
A single question displays 100% while awaiting its answer; an empty batch has
no percentage. Already confirmed questions can be skipped without resetting
`I`. Removed or reordered IDs require reconciliation.

The private continuation note follows
[question-explanation-state.template.md](../../templates/question-explanation-state.template.md).
Its phases are `explaining`, `awaiting-user-decision`,
`follow-up-review-required`, `follow-up-review-in-progress`, and `reviewed`.
The review protocol retains its existing state schema and confirmation labels.
