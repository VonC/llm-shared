# Specification review transcript for v0.11.0

- Exchange: specification/plan/v0.11.0/spec-review-requestor
- Reviewed document: docs/v0.11.0/plan.v0.11.0.spec-review-requestor.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-08-06T21:16:34+02:00
- Exchange: specification/plan/v0.11.0/spec-review-requestor
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.spec-review-requestor.md
- Outcome: request

### Review scope for spec-review-requestor plan round 1

Review the implementation plan and its three open questions as implementation
content. Check the step order, exact file ownership, tests-first work, line
budgets, split guidance, command checklists, IO constraints, and final
acceptance coverage against the consolidated requirement and design. Keep the
review at implementation level: do not reopen feature scope or design choices.

The sibling validation skeleton mirrors Steps 1 through 4 and may be checked
only for alignment with the numbered plan; the reviewed specification and
question source remains the plain implementation plan.

### Requestor assessment for spec-review-requestor plan round 1

The plan uses four implementation slices:

1. Add a paired specification request renderer, specialized template, launcher,
   and focused unit tests.
2. Add the canonical specialized requestor instruction with redirect-only
   Codex and Claude adapters.
3. Add bounded exact-path review routing, forced requestor delegation, and thin
   integration references in both question workflows while keeping the
   631-line `prompt_workflow_skill.py` below the 650-line ceiling.
4. Add lifecycle and IO acceptance coverage for every registered specification
   type, repeated rounds, reclaim, convergence, canonical consolidation, and
   completion.

The three questions settle implementation contracts needed before Step 1:

- Q01 recommends explicit exchange context flags, ignored UTF-8 authored-input
  files, and two explicit ignored output paths for the paired renderer.
- Q02 recommends failing closed with every exact identity when more than one
  live specification exchange exists for the resolved topic.
- Q03 recommends using normal `pw` live-exchange precedence as the
  post-consolidation handback: the requestor verifies the settled document,
  completes the exchange, then resolves the ordinary next phase.

Check whether the proposed file splits are sufficient, whether any production
or test file is missing from a step, whether the validation skeleton needs
realignment, and whether each recommended answer is the most reliable
implementation choice.

### Reviewer instructions for spec-review-requestor plan round 1

For each existing question, state agreement or disagreement with its options,
recommendation, and proposed answer. Identify exact plan or validation-skeleton
edits when needed. Add a question only for an unresolved implementation detail
that blocks coding; do not add requirement or design questions.

<!-- review-entry-id: request-round-1 -->

## Round 1 by reviewer

- Recorded: 2026-08-06T22:08:18+02:00
- Exchange: specification/plan/v0.11.0/spec-review-requestor
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.spec-review-requestor.md
- Outcome: answer

### Reviewer assessment for specification reviewer plan round 1

The step order, tests-first structure, line budgets, split guidance, command
checklists, and IO constraints follow the repository plan norms. Every
verifiable confirmed fact is exact: all eight quoted line counts match the
working tree, the forced-skill routing fact matches `prompt_workflow.py` and
`prompt_workflow_skill.py`, and the validation skeleton mirrors Steps 1
through 4 and needs no realignment. Step 2 behavior and Step 4 coverage
correctly include the shared `reclaim` operation.

All three recommended answers are accepted. Q01-A mirrors the shared launcher
contract with context flags, ignored UTF-8 authored inputs, and two explicit
ignored output paths. Q02-A fails closed with every exact identity because
multiple live exchanges are ambiguous authority, not a precedence case. Q03-A
uses `pw` live-exchange precedence as the replay-safe completion handback that
keeps canonical consolidation unaware of exchange state. No further
implementation question blocks coding.

### Requested changes for specification reviewer plan round 1

1. Add `.agent/workflows/spec-review-requestor.md` (redirect adapter) to the
   Step 2 files list and to the adapters-test coverage: every `pw`-invocable
   workflow instruction ships that host surface, including both question
   workflows and the shared `review-requestor` role. If the omission is
   deliberate, state the excluded host surface and the reason in the plan.
2. Optional wording: anchor the Step 3 transcript-dependency grep to the
   artifact shape, for example
   `review\.(feature-request|issue|design-specification|plan)`, so module
   prose cannot false-positive the must-find-nothing check.

Disposition: changes-requested. Apply the requested changes, realign the
validation skeleton's Step 2 expectations if they name adapter files, and
start another automated review round; no consolidation on this round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-08-06T23:34:32+02:00
- Exchange: specification/plan/v0.11.0/spec-review-requestor
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.spec-review-requestor.md
- Outcome: request

### Review identity for spec-review-requestor plan round 2

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/plan.v0.11.0.spec-review-requestor.md
Review round: 2

### Review scope for spec-review-requestor plan round 2

Review the revised implementation plan and its three open questions as
implementation content. Check the step order, exact file ownership,
tests-first work, line budgets, split guidance, command checklists, IO
constraints, and final acceptance coverage against the consolidated
requirement and design. Keep the review at implementation level: do not reopen
feature scope or design choices.

### Requestor update for spec-review-requestor plan round 2

- Step 2 now owns the missing
  `.agent/workflows/spec-review-requestor.md` redirect adapter.
- Step 2 adapter tests explicitly cover the `.agent/workflows`,
  `.agents/llm-shared/instructions`, `.agents/llm-shared/skills`, and
  `.claude/skills` surfaces as redirect-only Markdown.
- The Step 2 validation expectation names the same four adapter surfaces.
- The optional Step 3 completion grep now targets only the exact
  `review\.(feature-request|issue|design-specification|plan)` transcript
  artifact forms.
- Q01 through Q03 and their selected answers are unchanged. The round 1
  reviewer agreed with all three and identified no additional implementation
  question.

### Reviewer instructions for spec-review-requestor plan round 2

Confirm that the requested adapter ownership and coverage correction is
complete and that the tightened completion check remains executable. Report
any remaining implementation-level question or plan defect. Treat wording-only
polish as convergence-ready; otherwise request the concrete changes required
for another automated review round.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-08-06T23:53:15+02:00
- Exchange: specification/plan/v0.11.0/spec-review-requestor
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.spec-review-requestor.md
- Outcome: answer

### Reviewer assessment for specification reviewer plan round 2

Both round 1 corrections are applied and verified against the working tree:
Step 2 owns the `.agent/workflows/spec-review-requestor.md` redirect adapter
alongside the other three host surfaces, the adapters test asserts all four
surfaces are redirect-only, the validation-skeleton Step 2 expectation names
the same four surfaces, and the Step 3 completion grep is anchored to the
exact `review\.(feature-request|issue|design-specification|plan)` transcript
artifact forms while remaining a single executable command.

Q01 through Q03 keep their selected answers with the round 1 agreement
standing. No implementation-level question is missing and no plan defect
remains; file ownership, budgets, split guidance, and acceptance coverage are
coherent for coding to begin.

### Remaining edits for specification reviewer plan round 2

None.

Disposition: convergence-recommended. Retain this answer as evidence, enter
human confirmation, and present the `Consolidate` and
`Revise and review again` choices. This recommendation is advisory and does
not authorize consolidation.

<!-- review-entry-id: answer-round-2 -->

## Round 2 by human

- Recorded: 2026-08-07T00:01:40+02:00
- Exchange: specification/plan/v0.11.0/spec-review-requestor
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.spec-review-requestor.md
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->
