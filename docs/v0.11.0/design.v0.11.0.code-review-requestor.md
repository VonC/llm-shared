# Design v0.11.0 -- Implementation Code Review Requestor

Reference feature request:
[feature-request.v0.11.0.code-review-requestor.md](feature-request.v0.11.0.code-review-requestor.md)

---

## Context for v0.11.0 implementation code review requests

The shared review exchange already supplies exact artifact identity, durable round state, transcript persistence, bounded recovery, convergence authorization, and escalation. This design connects the implementation writer's existing post-`group-commits-msg` commit gate to that exchange when review mode is active, while preserving the ordinary human gate when it is not.

The requestor remains the owner of the staged implementation, `a.commit`, its assessment of reviewer repairs, and any eventual commit action. The code reviewer may make only bounded repairs and can recommend commit readiness, but cannot authorize or perform a commit.

## Scope for v0.11.0 implementation code review requests

The v0.11.0 outcomes are:

1. Select ordinary human review or automated code review at the existing commit-gate boundary.
2. Compose implementation-specific review requests and drive repeated requestor rounds through the shared exchange.
3. Preserve a human-only decision before the existing commit action can run.

Everything else is supporting design context for those outcomes or explicitly deferred.

### In scope for v0.11.0 implementation code review requests

- Review-mode activation immediately after successful commit-message grouping.
- Code-review request identity for the exact plan, implementation step, round, and umbrella-or-none context.
- Requestor assessment of staged reviewer repairs and `a.commit` amendments.
- Automated intermediate rounds, explicit repair disagreements, and convergence presentation.
- Canonical and host-specific instruction surfaces for the complementary code-review requestor role.

### Deferred from v0.11.0 implementation code review requests to later umbrella topics

- The independent `code-reviewer` role and its answer-generation implementation.
- End-user documentation for the complete review-mode workflow.
- Changes to shared exchange transport, persistence, timeout, recovery, or escalation semantics.
- Any implementation-specific file list, task order, or test commands, which belong in the implementation plan.

---

## Confirmed technical facts for v0.11.0 implementation code review requests

**The current implementation cycle has one commit gate**: `instructions/implement-step.md` requires the chain to continue through implementation check, after-check routing, `group-commits-msg`, and preparation of `a.commit`; only then does it stop for review before the actual commit.

**Shared requestor coordination is already canonical**: `instructions/review-requestor.md` assigns status, activation, request publication, exact-file waiting, answer consumption, continuation, confirmation, escalation, recovery, and completion to `bin/review_exchange.bat`.

**The exchange core already recognizes implementation-code identity**: code reviews use the fixed `code` family token, derive version and slug from the exact plan, require an implementation-step identifier, and place the versioned transcript beside the plan.

**Commit grouping is staged-state based**: the implementation cycle prepares staged changes and `a.commit` before the review boundary, so the Git index is the stable review subject shared by the requestor, reviewer, and eventual commit workflow.

**Canonical host adapters are redirects**: provider-specific instruction and skill registrations point directly to canonical root instructions under the repository's LLM-specific adapter rule.

---

## Current behavior for v0.11.0 implementation review

The implementation workflow reaches one unconditional human review stop after `a.commit` is prepared.

```txt
implement-step
  -> implementation-check
  -> after-check routing
  -> group-commits-msg
  -> staged changes + a.commit
  -> human commit gate
```

It does not sample `a.review-mode` at that boundary, delegate to an implementation-specific requestor, publish code-review artifacts, or distinguish intermediate rework from reviewer-recommended commit readiness.

## Target behavior for v0.11.0 implementation review

The writer samples the root marker exactly once after `group-commits-msg` succeeds and before either review path creates state.

```txt
group-commits-msg completes
  -> sample project-root a.review-mode once
       -> absent: preserve existing human commit gate
       -> present: delegate through pw to code-review requestor
            -> publish exact plan + step + round request
            -> reviewer inspects and may repair staged work
            -> requestor assesses staged repairs and a.commit
                 -> changes requested: consume and publish another automated round
                 -> substantive repair plus commit-ready recommendation: human gate, override recommended
                 -> polishing-only repair plus commit-ready recommendation: human gate
            -> Commit: run the existing authorized commit action
            -> Rework and review again: record override and publish another round
```

Once an exchange starts, its durable coordination state governs continuation. Removing or changing the marker cannot silently abandon or reroute that live exchange.

---

## Activation and role boundaries for v0.11.0 implementation review requests

### Commit-gate activation boundary

`implement-step` retains ownership of reaching a valid, reviewable staged state and `a.commit`. Immediately after successful grouping, it selects the ordinary or review-mode path from one marker sample. The integration contains only this trigger and a direct delegation to the specialized code-review requestor; it does not reproduce request construction or lifecycle transitions. That delegation asks `pw` to render a self-contained specialized command carrying both the exact plan document and an explicit implementation-step token, then runs the printed command verbatim.

The code-review family policy is stable for the exchange:

- family: `code`;
- convergence signal: `commit-ready`;
- another-round label: `Rework and review again`;
- continue-owning-workflow label: `Commit`.

### Specialized writer and shared requestor ownership

The specialized code-review requestor owns the implementation report, reviewer-repair assessment, writer corrections, disagreement assessment, `a.commit` assessment, convergence summary, and any human-authorized continuation. The shared requestor owns every durable protocol transition and artifact lifecycle operation.

The independent reviewer owns its assessment and any repair it can make safely and unambiguously within the reviewed plan step. Work outside that objective boundary is returned as feedback. The reviewer never commits and never calls the human-confirmation transition.

## Request identity and content for v0.11.0 implementation review requests

### Exact plan and step identity

The requestor receives the exact plan path and implementation-step identifier from the self-contained command rendered by `pw`. The host-prefixed handoff extends the usual `on <document>` form with an explicit step token rather than requiring the requestor to re-derive the step from workflow state or read a side-channel context file. The plan filename supplies the version and slug, and the effort context supplies the exact umbrella path or `none`. The machine envelope and authored summary each carry that same plan, step, round, and umbrella identity; any mismatch fails closed before publication.

All shared operations use the fixed code-review policy and exact context. The requestor uses paths returned by the launcher and never constructs or mutates request, answer, coordination, tombstone, or transcript artifacts by hand.

### Implementation-specific request body

The specialized renderer produces the complete request and substantive transcript summary from one validated round input. The request includes the end-of-step implementation report and directs the reviewer to:

- apply `implementation-check` to the exact plan step;
- inspect the staged changes as the review subject;
- make every safe, unambiguous repair that remains inside the reviewed step;
- leave each repair staged and name every repaired path in the answer;
- inspect and amend `a.commit` only when file membership, grouping, order, scope, or conventional-subject accuracy changed;
- avoid committing;
- publish either a rework request or an advisory commit-ready recommendation.

The transcript summary contains the requestor's substantive feedback without coordination boilerplate. The exchange appends it under the correct role and round; neither writer nor reviewer uses the transcript as working context.

## Repair assessment and repeated rounds for v0.11.0

### One staged review subject

Reviewer repairs are staged before the answer becomes available, and the answer names their paths. The requestor therefore assesses one observable index state rather than combining staged and unstaged changes. It compares that state with the exact plan step, answer, and `a.commit`, then makes any further writer-owned corrections before continuing.

When the requestor rejects and reverts a reviewer repair, its replacement request records the reversal as an explicit disagreement. The shared clarification-and-escalation bound then prevents a reviewer restore/requestor revert cycle from masquerading as progress. This preserves final writer authority without adding a second no-progress counter.

### Round classification after repairs

A reviewer answer that changes code, tests, acceptance behavior, or commit grouping cannot validly finish the workflow in that round. When the answer requests changes, the requestor assesses the result and publishes another automated round for the substantive change. When the answer instead recommends commit readiness, the exchange has already reached its human gate, so the requestor presents the substantive evidence with a recommendation to choose `Rework and review again` rather than starting a round it cannot start. Wording, formatting, and equivalent metadata polishing that leaves proposed commit boundaries unchanged may accompany a same-round commit-ready recommendation.

Intermediate answers never enter a human gate. The requestor truthfully records whether reviewed work changed and whether explicit disagreement exists, consumes the answer, advances the durable round, publishes the updated writer response, and waits again. Shared timeout, abandonment, no-progress, disagreement, and inconsistent-artifact outcomes stop automation through the established escalation path.

## Convergence and human-owned commit authority for v0.11.0

At a commit-ready recommendation, the answer remains as evidence and the exchange enters `awaiting-human-confirmation`. The requestor presents the exact umbrella or `none`, plan, step, round, reviewer recommendation, staged changes, `a.commit`, and writer assessment.

When that recommendation follows a substantive reviewer repair, the gate remains legitimate rather than becoming an artifact inconsistency. The writer assessment explicitly identifies the substantive evidence and recommends `Rework and review again`. Only the human override can leave the gate for another round; the requestor neither consumes the convergence answer as intermediate feedback nor escalates a recoverable policy disagreement.

`Rework and review again` records the human override and optional guidance, resets the shared no-progress counters, and publishes a replacement round. Guidance remains distinct from the writer response and resulting changes.

`Commit` durably authorizes only the existing owning commit action. The requestor verifies `owning_action_authorized: true`, invokes the canonical commit continuation, and completes the exchange only after that action succeeds. A later session seeing `owning-action-pending` resumes the already authorized action without asking again. Reviewer recommendation alone never authorizes a commit.

---

## Requirement decisions carried into the v0.11.0 code review requestor design

The identifiers below are the consolidated feature request's decision identifiers. This design's own open questions use their own sequence and are recorded separately once they are consolidated.

| Question | Decision | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| FR-Q01 | Give the reviewer bounded repair authority inside the exact plan step; unsafe, ambiguous, or product-changing work is feedback-only. | Activation and role boundaries; Implementation-specific request body | Reviewer discretion; feedback-only review |
| FR-Q02 | Require a new round after code, test, acceptance-behavior, or commit-grouping changes; permit same-round convergence for polishing-only changes. | Repair assessment and repeated rounds / Round classification after repairs | Re-review every edit; same-round approval of substantive repairs |
| FR-Q03 | Amend `a.commit` only when its membership, grouping, order, scope, or subject accuracy no longer matches staged work. | Request identity and content / Implementation-specific request body | Amend after every repair; reserve all amendments for the writer |
| FR-Q04 | Sample review mode once immediately after successful grouping and use durable coordination thereafter. | Activation and role boundaries / Commit-gate activation boundary | Sample at step start; monitor continuously |
| FR-Q05 | Leave every reviewer repair staged and inventory repaired paths in the answer. | Repair assessment and repeated rounds / One staged review subject | Requestor stages repairs; unspecified staging |
| FR-Q06 | Treat a requestor reversal as explicit disagreement governed by the shared bound. | Repair assessment and repeated rounds / One staged review subject | Immediate escalation without reversal; an unmarked first reversal |

## Design decisions for v0.11.0 implementation code review requests

| Question | Decision | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | `implement-step` asks `pw` for the specialized code-review requestor command and executes the rendered handoff verbatim. | Activation and role boundaries / Commit-gate activation boundary | Direct requestor invocation; router-owned orchestration |
| Q02 | A specialized renderer accepts exact context plus separate ignored authored inputs and emits paired request and transcript-summary outputs in one run. | Request identity and content / Implementation-specific request body | One mixed JSON input; parse the transcript summary from rendered Markdown |
| Q03 | A dedicated `pw` continuation resumes existing commit execution from durable authorization without presenting the commit choice again. | Convergence and human-owned commit authority | Re-enter the ordinary gate; commit directly from the requestor |
| Q04 | Assess repair scope against the exact plan step, repaired-path inventory, staged diff, and relevant `implementation-check` result. | Repair assessment and repeated rounds / One staged review subject | Treat the check alone as sufficient; use unconstrained contextual judgment |
| Q05 | Extend the rendered requestor handoff with an explicit implementation-step token so plan and step are self-contained, inspectable, and resumable. | Activation and role boundaries / Commit-gate activation boundary; Request identity and content / Exact plan and step identity | Re-derive the step from workflow state; pass it through a side-channel file |
| Q06 | If substantive repairs accompany a commit-ready recommendation, retain the legitimate human gate and recommend `Rework and review again`. | Repair assessment and repeated rounds / Round classification after repairs; Convergence and human-owned commit authority | Escalate valid state as inconsistent; use an unavailable intermediate disagreement transition |

## Acceptance cases for v0.11.0 implementation code review requests

| Scenario | Expected outcome | Reason |
| --- | --- | --- |
| Marker absent after successful grouping | Preserve the existing human commit gate and create no exchange artifacts. | Review mode remains opt-in. |
| Marker present after successful grouping | Delegate exact plan and step context to the code-review requestor. | The commit-gate boundary is the settled activation point. |
| Marker changes after exchange start | Resume from durable coordination state without rerouting the live exchange. | Artifact ownership must remain consistent. |
| Reviewer finds a safe in-step omission | Repair and stage it, name its path, and assess `a.commit`. | Both roles must observe one staged review subject. |
| Repair exceeds the plan step or needs a product decision | Return feedback without editing that work. | Reviewer authority has an objective scope boundary. |
| Reviewer changes code, tests, acceptance behavior, or grouping and requests changes | Consume the intermediate answer and publish another automated round after requestor assessment. | One actor cannot write and approve substantive work in the same round. |
| Reviewer changes code, tests, acceptance behavior, or grouping and recommends commit readiness | Present the human gate with the substantive evidence and recommend `Rework and review again`; do not consume the convergence answer or start a round directly. | One actor cannot write and approve substantive work in the same round. |
| Reviewer changes only wording or equivalent metadata | May recommend commit readiness in the same round when boundaries remain unchanged. | A mechanical extra round cannot change correctness. |
| Requestor reverts a reviewer repair | Record explicit disagreement in the replacement request. | The shared disagreement bound stops restore-and-revert loops. |
| Reviewer recommends commit readiness | Retain the answer and present both human choices with staged evidence. | The recommendation is advisory. |
| Human selects `Rework and review again` | Record override and guidance, reset counters, and publish another bounded round. | Human authority can override convergence. |
| Human selects `Commit` | Durably authorize and run only the existing commit continuation, then complete the exchange. | Commit authority remains exclusively human. |

## File-based IO cost clarification for v0.11.0 implementation code review requests

- `pw` resolves the effort and implementation step once, then renders one self-contained handoff without a documentation-tree scan.
- Each request render reads its small ignored authored inputs once and writes paired outputs once.
- Shared exchange operations remain constant exact-path reads and atomic writes; neither role reads transcript history as working context.
- Repair assessment reads the staged diff, repaired-path inventory, exact plan step, relevant validation result, and `a.commit` once per answer.
