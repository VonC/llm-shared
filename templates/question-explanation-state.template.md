# Question explanation continuation: {exact document}

Private requestor-owned note in the configured artifact home. This is not a
review protocol artifact. Replace all placeholders; never save capabilities.

- Document: {absolute path}
- Document type: {feature-request / issue / design / plan}
- Topic and phase: {version and slug; phase and position, such as `requirement (2/5)`}
- Umbrella: {slug, item x/N: key title, completed/N items completed, umbrella draft path; or none, standalone topic}
- Topic draft: {path, or not resolved}
- Context source and refresh: {`pw progress` or drafts, with timestamp}
- Last observed document SHA-256: {scanner digest}
- Updated: {timestamp with timezone}
- Review identity and role: {exact exchange, requestor, or no live exchange}
- Converged round at batch entry: {round or none}
- Phase: {explaining / awaiting-user-decision / follow-up-review-required / follow-up-review-in-progress / reviewed}
- Batch identity: {document plus entry round and timestamp}
- Fixed starting position I and question ID: {position, ID}
- Fixed endpoint Total and last question ID: {position, ID}
- Ordered batch question IDs: {IDs from I to Total}
- Current question: {ID or none}
- Explanation delivered: {yes / no}
- Explicit decision recorded for current question: {yes / no, document line}
- Next and last undecided: {IDs or none, from latest full scan}
- Follow-up review authority: {user selection/invocation and date, exact scope}
- User hold: {none or exact stop instruction}
- Follow-up round/publication: {none or round, outcome, evidence}
- Reviewed batch evidence: {none or convergence round and document identity}
- Next action: {one concrete action and its prerequisite}

## Big picture shown before each question

Composed once per batch, as the instruction's "Compose the big picture shown
before every question" describes; recomposed after a resume or a decision that
changes the flow. Write `not resolved` for a part no source establishes.

- Sources and refresh: {umbrella draft, topic draft and effort documents read, with timestamp}
- Purpose: {umbrella goal and this item's place, then the topic's purpose and implementation state}
- Walkthrough steps: {numbered end-to-end steps on an ordinary concrete case}
- Step of each batch question: {question ID, then the walkthrough step or component it concerns}

## Notions explained to the user

One entry per notion the user asked about, as the instruction's "Explain a
notion the user asks about" describes. Every later question that involves one
explains it again, in more detail.

- {notion}: {short definition}; raised at {question ID}; introduced in {each document path and section updated}

## Decisions and comments to include in the review

{Question IDs, user decisions, rationale, comments, dependencies and possible
inconsistencies. Link to the document's full records; do not infer decisions.}

## Reconciliation notes

{Changes since the previous snapshot, reconciled question identities, unresolved
discrepancies, and actions already completed that must not be repeated.}
