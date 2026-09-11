# Request implementation code reviews before commit

## Review-mode revision that introduces the code-review requestor

The `implement-step` workflow currently finishes its implementation work, invokes `group-commits-msg`, and stops so a human can review the staged changes and the grouped commit message in `a.commit`.

Review mode changes that stopping point. When the project-root `a.review-mode` marker exists, implementation work must enter an automated writer-to-reviewer exchange before the human commit decision. The implementation writer remains responsible for the staged changes, its end-of-step report, `a.commit`, and the assessment of reviewer feedback. Shared artifact transport and lifecycle rules remain owned by `review-exchange-core`, while the independent responder remains outside this requirement.

As an implementation writer, I want `implement-step` to request and process an implementation-code review after commit-message grouping so that missing work can be found and corrected automatically while commit authority remains exclusively with the human.

## Current implementation workflow in v0.11.0

- `instructions/implement-step.md` reaches `group-commits-msg` after implementing and validating a plan step.
- The normal workflow then stops for human review of the staged implementation and `a.commit`.
- It does not condition that stopping point on the project-root `a.review-mode` marker.
- It does not create an identity-bearing `a.review-requested.code.vX.Y.Z.slug.md` request, append requestor feedback to a sibling code-review transcript, or consume a matching review answer.
- It does not automate intermediate rework rounds or distinguish reviewer-recommended commit readiness from human commit authorization.

## Gap to close for implementation-code review requests

1. Add a review-mode branch immediately after the existing `group-commits-msg` call in `implement-step`.
2. Keep the existing human-review stopping behavior when `a.review-mode` is absent.
3. When `a.review-mode` exists, delegate to the complementary code-review requestor role instead of duplicating that role's exchange process in `implement-step`.
4. Create or reuse the versioned code-review transcript beside the implementation plan, clear stale answer state, publish an identity-bearing request, and append the requestor entry to the transcript through the shared review-exchange facilities.
5. Continue intermediate review and rework rounds automatically, while reserving the commit-ready convergence point for explicit human confirmation.
6. Apply the shared timeout, abandonment, no-progress, disagreement, and artifact-consistency rules so an exchange that cannot safely continue enters `escalated` rather than waiting forever.

## Confirmed request identity and artifacts

- Review mode is enabled only by a project-root `a.review-mode` marker.
- The transient request is project-root `a.review-requested.code.vX.Y.Z.slug.md`.
- The transient answer is project-root `a.review-answer.code.vX.Y.Z.slug.md`.
- The versioned transcript is `review.code.vX.Y.Z.slug.md` beside `plan.vX.Y.Z.slug.md` in the effort's selected documentation layout.
- The transcript is initialized from the shared type-and-version template when absent, is append-only for agents, and is not reread as working context.
- Before publishing a new request, the requestor deletes a stale matching answer when the shared exchange rules permit it.
- Each request summary states the umbrella draft path or `Umbrella draft: none`, the exact implementation-plan path, the implementation step, and the round.
- The human-readable identity fields agree with the machine-readable exchange identity.
- The request includes the implementation writer's end-of-step report and tells the reviewer to use `implementation-check`, inspect the staged changes, refrain from committing, repair missing work, leave every reviewer repair staged, name the repaired paths in the answer, and amend `a.commit` when appropriate.
- Publishing the request also appends the same requestor feedback to the sibling versioned transcript.

## Automated rework and convergence behavior

For an intermediate response, the requestor reads the matching answer, inspects the staged changes and `a.commit`, applies or assesses the reviewer changes, makes any additional corrections, deletes the consumed answer, and publishes a replacement request with the updated round identity. When it reverts a reviewer repair, it records the reversal as an explicit disagreement in that replacement request so the shared disagreement rule bounds the dialogue. No human confirmation is required between intermediate rounds.

When the reviewer recommends commit readiness, the recommendation is advisory. The requestor retains the answer as decision evidence and enters `awaiting-human-confirmation`. It presents the human with the umbrella identity or `none`, exact plan, implementation step and round, reviewer recommendation, staged changes, `a.commit`, and its own assessment.

The human then chooses one of two actions:

- `Commit`: explicitly authorize the owning workflow to execute its existing commit step.
- `Rework and review again`: record the override and any human guidance, reset the no-progress counters, and publish another automated review round.

The requestor deletes the convergence answer only after applying the confirmed action. Neither a reviewer recommendation nor entry into `awaiting-human-confirmation` authorizes a commit.

## Termination and escalation rules

- `awaiting-human-confirmation` is a durable convergence state and is distinct from `escalated`.
- Timeout, abandonment, repeated no-progress, unresolved disagreement, and inconsistent identity or artifacts use the shared review-exchange termination criteria.
- An exchange that reaches a shared stop condition enters `escalated` and requests human intervention instead of creating unlimited automated rounds.
- A human choice of `Rework and review again` at convergence records the override, incorporates any supplied guidance into the replacement request summary, and resets the no-progress counters.

## Existing-skill and adapter boundaries

- `instructions/implement-step.md` contains only the integration trigger and a direct reference to the complementary canonical requestor role.
- That integration reference makes clear that review mode replaces the normal immediate human-review stop and that requestor feedback is appended to the versioned transcript.
- The requestor workflow, templates, scripts, and supporting utilities remain in their shared role or skill rather than being copied into `implement-step`.
- LLM-specific Markdown registrations remain thin adapters that point directly to the canonical root instruction, following `rules/llm-specific-adapters.md`.
- The implementation-code reviewer role and its answer-generation behavior belong to the separate `code-reviewer` effort.

## Acceptance criteria for `code-review-requestor`

1. With no root `a.review-mode`, `implement-step` retains its existing post-`group-commits-msg` human-review behavior.
2. With root `a.review-mode`, `implement-step` invokes the complementary code-review requestor flow immediately after `group-commits-msg` and does not stop at the old review point.
3. The requestor uses the shared exchange facilities to initialize or reuse the sibling transcript, remove permitted stale answer state, write the matching root request, and append the requestor feedback to the transcript.
4. Every request carries the exact umbrella-or-none, plan, step, and round identity, and rejects or escalates inconsistent identity or artifacts.
5. The reviewer instructions require `implementation-check`, staged-change inspection, no commit, missing-work repair, conditional `a.commit` amendment, a fix summary, and either an intermediate rework request or an advisory commit-readiness recommendation.
6. A reviewer answer that changed code, tests, acceptance behavior, or commit grouping triggers another automated round; a reviewer answer whose only changes are wording, formatting, or equivalent metadata that leave the proposed commit boundaries unchanged may recommend commit readiness in the same round.
7. Every reviewer repair is left staged, and the reviewer answer names every repaired path so the requestor can assess the work against the single staged review subject.
8. When the requestor reverts a reviewer repair, the replacement request records that reversal as an explicit disagreement; the existing shared disagreement rule bounds any revert-and-restore loop while the requestor retains final authority over its staged work.
9. Intermediate answers trigger an automated assess-correct-request cycle without a human wait.
10. A commit-readiness recommendation enters `awaiting-human-confirmation` and exposes the required identity, evidence, recommendation, staged changes, `a.commit`, and requestor assessment.
11. The existing commit step runs only after the human explicitly chooses `Commit`.
12. Choosing `Rework and review again` records the override and guidance, resets no-progress counters, and begins another automated round.
13. Shared termination criteria bound waiting and repeated dialogue; timeout, abandonment, no-progress, disagreement, and inconsistent artifacts escalate for human intervention.
14. The `implement-step` integration references rather than duplicates the canonical requestor process, and any LLM-specific adapter remains a redirect to canonical root content.

## Requirement clarifications

| Question | Decision | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | The reviewer repairs every omission it can correct safely and unambiguously within the reviewed plan step; work beyond that boundary is returned as feedback. | Confirmed request identity and artifacts; acceptance criterion 5 | Discretionary repair; feedback-only review |
| Q02 | Code, test, acceptance-behavior, or commit-grouping changes require another automated round; polishing-only changes may converge in the same round. | Automated rework and convergence behavior; acceptance criterion 6 | Re-review every edit; let the reviewer approve its own substantive repairs |
| Q03 | The reviewer amends `a.commit` only when staged membership, grouping, order, scope, or conventional-subject accuracy changes. | Confirmed request identity and artifacts; acceptance criterion 5 | Amend after every edit; reserve every amendment for the requestor |
| Q04 | Sample `a.review-mode` once immediately after successful `group-commits-msg`; after exchange start, durable coordination state governs later continuation. | Gap to close; acceptance criteria 1 and 2 | Sample at step start; monitor continuously |
| Q05 | Every reviewer repair is staged and every repaired path is named in the answer. | Confirmed request identity and artifacts; acceptance criterion 7 | Requestor stages repairs; unspecified staging with path inventory only |
| Q06 | A requestor may revert a reviewer repair, but the replacement request records the reversal as an explicit disagreement governed by the shared bound. | Automated rework and convergence behavior; acceptance criterion 8 | Prohibit reversal and escalate immediately; permit an unmarked first reversal |

## Direct implementation references

- `instructions/implement-step.md`: integrate the review-mode trigger immediately after the existing `group-commits-msg` handoff point.
- `instructions/implementation-check.md`: supply the implementation-validation behavior named in each code-review request.
- `instructions/group-commits-msg.md`: preserve the grouped `a.commit` preparation that occurs before review starts.
- `rules/llm-specific-adapters.md`: constrain provider-specific registrations to direct canonical redirects.
- `docs/v0.11.0/feature-request.v0.11.0.review-exchange-core.md`: provide the shared artifact lifecycle, state, convergence, and termination contract on which this requestor depends.

## File-based IO cost clarification

- Review activation resolves one exact plan and implementation step rather than searching the documentation tree.
- Request and answer handling use the shared exchange's bounded exact artifact set and atomic transitions.
- The staged diff and `a.commit` are read only when assessing the current answer; the transcript is never loaded as working context.
