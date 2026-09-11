# Specification review transcript for v0.11.0

- Exchange: specification/plan/v0.11.0/spec-reviewer
- Reviewed document: docs/v0.11.0/plan.v0.11.0.spec-reviewer.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-08-10T11:09:43+02:00
- Exchange: specification/plan/v0.11.0/spec-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.spec-reviewer.md
- Outcome: request

### Review identity for plan spec-reviewer round 1

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/plan.v0.11.0.spec-reviewer.md
Review round: 1

### Requestor assessment for plan spec-reviewer round 1

The implementation plan is aligned with the consolidated requirement and
design. It defines four ordered slices, lists every production and test file,
uses tests first, carries shared execution commands, and aligns the validation
skeleton one-for-one with the numbered steps.

The measured 650-line `prompt_workflow_skill.py` baseline makes its Step 1
split mandatory. The five open questions cover the remaining implementation
choices: split boundary, renderer/CLI module boundary, retained-manifest cleanup
owner, public-launcher acceptance strategy, and shared fixture placement. Each
has distinct options, trade-offs, a recommendation, and an answer. No design or
requirement decision is reopened, and no additional plan-level question is
apparent.

This is the first plan review round, so no earlier reviewer wording exists to
apply or reject.

### Change summary for plan spec-reviewer round 1

Created the four-step implementation plan and aligned validation skeleton from
the consolidated design. Added measured line budgets, the mandatory workflow
router split, exact test packages and commands, IO and complexity constraints,
acceptance coverage, and five implementation-level open questions.

### Writer response for plan spec-reviewer round 1

Writer response: This is the first plan review round. Please assess the complete implementation
and validation plans, verify file existence and measured baselines, and review
all five implementation decisions without reopening the settled feature or
design. Identify any missing file, unsafe step ordering, test gap, line-budget
problem, or wording change required before implementation can begin.

### Reviewer focus for plan spec-reviewer round 1

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

## Round 1 by reviewer

- Recorded: 2026-08-11T07:41:37+02:00
- Exchange: specification/plan/v0.11.0/spec-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.spec-reviewer.md
- Outcome: answer

### Reviewer assessment for plan spec-reviewer round 1

The plan is sound and implementable: four ordered slices, tests before
behavior, exact file lists, measured budgets, shared command checklists, IO and
complexity bounds, and a validation skeleton aligned with the steps. It
implements the consolidated design without reopening it.

Every measured baseline was verified against the working tree rather than
accepted, and all nine are exact: `prompt_workflow_skill.py` 650,
`prompt_workflow_review.py` 192, `spec_review_request.py` 413,
`tools/__init__.py` 83, `spec-review-requestor.md` 162, and the four test files
at 298, 128, 124, and 121. The repository facts hold too: `_LiveRoute` is
frozen with context and state while public routing returns only a path,
`forced_command` recognizes only `spec-review-requestor`, and the generic
answer template carries just the shared envelope shape.

All five recommended answers are the ones I would choose. Q03 is right for the
reason its option B is wrong: retiring the manifest at render time destroys
recovery evidence exactly when publication later fails. Q04 matches what the
sibling acceptance suite showed about subprocess cost. Q01 is correct as a
decision; its execution needs the detail below.

### Requested changes for plan spec-reviewer round 1

1. Name the exact functions Step 1 extracts and what stays. The module name
   invites moving `post_commit_command`, which is the one move that creates the
   forbidden cycle: it calls `host_prefix` and `_document` from the module
   being split, while `run_skill` calls it. The safe extraction is the four
   topic-discovery helpers only, `_resolve_post_commit_topic`, `_plan_topics`,
   `_topic_from_validation_plan`, and `_slug_key`, which depend only on `docs`
   and shared models so the import stays one-way.
2. Correct the Step 3 adapter contract before it becomes a test. "Every adapter
   is metadata plus a canonical redirect only" is the formulation that produced
   a defect in the sibling effort and had to be repaired at code review. All 26
   `.agent/workflows/` files use the repository locate-steps body, which
   resolves when the folder is junctioned into a consuming project. State that
   the workflow wrapper uses that form while Codex and Claude hosts use
   loader-relative links, and that the adapter test checks each host in its own
   form, modelled on the repaired requestor adapters test and its
   workflow-wrapper regression guard.
3. Recommended: record the expected post-extraction count. Removing the four
   helpers takes 650 to roughly 581, leaving about 29 lines under the mandatory
   610 target for Step 1's own additions. It fits, but this module shipped at
   exactly 650 with no headroom last time, so a stated baseline and one
   fallback extraction candidate would prevent an emergency second split.

Disposition: changes-requested. Changes 1 and 2 alter which definitions move
and which contract a test encodes. Apply them and start another automated
round; no consolidation on this round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-08-11T07:53:17+02:00
- Exchange: specification/plan/v0.11.0/spec-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.spec-reviewer.md
- Outcome: request

### Review identity for plan spec-reviewer round 2

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/plan.v0.11.0.spec-reviewer.md
Review round: 2

### Requestor assessment for plan spec-reviewer round 2

All round-1 findings were accepted with no disagreement. Step 1 now names the
four helpers that move, states that `post_commit_command` remains because it
depends on skill-module rendering and document helpers, and requires one-way
imports. Its budget records the expected post-extraction count of about 581,
the mandatory final target at or below 610, and a named host-rendering fallback
extraction if that headroom proves insufficient.

Step 3 now distinguishes the workflow host's portable three-step locate body
from the loader-relative Codex and Claude adapters. Its tests explicitly reuse
the repaired requestor adapter regression model and check each host form
independently. The validation skeleton carries both clarifications.

All five implementation questions remain sufficient and retain their supported
recommended answers. No additional plan-level question or design conflict is
apparent after these changes.

### Change summary for plan spec-reviewer round 2

Named the exact four Step 1 discovery helpers, kept `post_commit_command` in
place, documented one-way dependencies, added the expected 581-line extraction
baseline and a host-rendering fallback split. Replaced the uniform Step 3
adapter assertion with the workflow locate-steps contract and loader-relative
Codex/Claude contracts, and aligned the validation skeleton.

### Writer response for plan spec-reviewer round 2

Writer response: Accepted both required changes and the line-budget recommendation. The plan now
prevents the circular-import split, names a measurable fallback, and models
each host adapter on its actual deployment form. There is no disagreement.
Please verify those implementation instructions and reassess the five plan
answers for convergence.

### Reviewer focus for plan spec-reviewer round 2

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-08-11T08:55:34+02:00
- Exchange: specification/plan/v0.11.0/spec-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.spec-reviewer.md
- Outcome: answer

### Reviewer assessment for plan spec-reviewer round 2

Both required changes and the line-budget recommendation are applied, each in
every place it needed to land rather than only where it was raised.

Step 1 names the exact four helpers to move in its fix intent, types and
behavior, split guidance, and Q01's option A and recommendation, and it states
that `post_commit_command` remains because it calls the skill module's
`host_prefix` and `_document`, so moving it would create the circular import
the split exists to avoid. That is the correct boundary: the four discovery
helpers depend only on documentation discovery, shared models, and suffix
constants, so the import stays one way.

The budget records the expected count of about 581 after extraction alongside
the mandatory 610 target, and the split guidance names a concrete fallback,
moving `detect_host`, `host_prefix`, and `render_command` to
`tools/prompt_workflow_render.py` with re-export. That fallback is well chosen:
those three are the host-rendering cluster, and the new module would import
nothing from the skill router, so the one-way rule holds for it too.

Step 3 replaced the uniform adapter assertion with per-host contracts. The
workflow wrapper must use the repository three-step locate body for workspace,
sibling-clone, and submodule deployment; the packaged Codex instruction, Codex
skill, and Claude skill must use loader-relative canonical links; and the tests
reuse the repaired requestor assertions, naming
`test_workflow_wrapper_reuses_the_repository_locate_steps` as the regression
model while checking each host independently. The behavior list and split
guidance carry the same distinction, so the contract cannot drift back to the
formulation that caused the earlier defect.

The validation skeleton keeps one section per numbered step and carries both
clarifications in its Step 1 and Step 3 expectations. All five recommended
answers remain the ones I would choose, no plan-level question is missing, and
implementation can begin.

### Wording edit covered by this convergence recommendation

The split guidance introduces the render-module fallback with "If reviewer
routing cannot remain at or below 610 after that extraction". On the plan's own
numbers the margin is about one line: roughly 581 after extraction plus close
to 28 lines for the state-to-role mapping, the `spec-reviewer` forced branch,
and its constant. State that the fallback should be treated as likely rather
than exceptional, and that the count is taken immediately after the extraction
rather than at step end, so the second split is planned instead of a late
rescue.

Disposition: convergence-recommended. Apply the edit before the human gate,
state that it is applied in the convergence summary, and present the
`Consolidate` and `Revise and review again` choices. This recommendation is
advisory and does not authorize consolidation.

<!-- review-entry-id: answer-round-2 -->

## Round 2 by human

- Recorded: 2026-08-11T10:06:34+02:00
- Exchange: specification/plan/v0.11.0/spec-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.spec-reviewer.md
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->
