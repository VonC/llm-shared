# Respond to implementation code reviews

- Type: feature-request
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md

Create a focused `code-reviewer` role that independently reviews one staged implementation step, repairs missing work when appropriate, and reports whether the work needs another automated round or is ready for the requestor to ask a human for commit authorization.

## Review workflow context

The implementation writer creates or overwrites the project-root `a.review-requested.code.vX.Y.Z.slug.md` after `group-commits-msg`. The request contains an identity-bearing summary naming the umbrella draft (or `none`), the exact implementation plan, implementation step, and round. It directs the reviewer to use `implementation-check`, inspect staged changes, avoid committing, repair missing work, amend `a.commit` when needed, and either request rework or recommend commit-readiness.

Ordinary review rounds remain automated. A reviewer recommendation is advisory: it never authorizes a commit. A convergence point occurs only when the reviewer recommends commit-readiness. The requestor then enters `awaiting-human-confirmation`, where only the human may choose `Commit` or `Rework and review again`. Choosing another round records the override and guidance, resets the no-progress counters, and creates a replacement request. The distinct `escalated` state remains reserved for timeout, abandonment, no-progress, disagreement, and inconsistent artifacts.

## Code review responder

Add a `code-reviewer` skill that accepts the plan document name returned by `pw` and waits for the matching project-root `a.review-requested.code.vX.Y.Z.slug.md` file. It must:

- validate that the request's umbrella, plan, implementation step, round, and machine-readable exchange identity agree;
- follow the request and `implementation-check` to assess the staged implementation changes;
- inspect and repair missing implementation work when needed, without weakening the intended checks;
- amend `a.commit` when its grouped commit messages no longer describe the staged changes;
- never commit;
- provide constructive feedback that either requests rework and another automated review round or recommends commit-readiness;
- write that feedback to the matching project-root `a.review-answer.code.vX.Y.Z.slug.md`;
- append the same feedback to `review.code.vX.Y.Z.slug.md` beside the implementation plan; and
- delete the consumed request only when the answer is ready.

The versioned review transcript is append-only for agents and is not reread as working context. The transient request and answer files remain at the project root and rely on the existing `a.*` ignore rule.

## Skill adapter and generation support

Provide the LLM-specific skill wrapper or adapter that locates and follows the canonical shared `code-reviewer` instruction. Add a template and script for generating the review-answer content, reusing the shared exchange utilities and conventions established by `review-exchange-core` rather than duplicating their lifecycle or safety policy.

## Termination and intervention

The reviewer must follow the shared termination criteria for bounded waits, abandonment, repeated no-progress, disagreement, and inconsistent artifacts. When those criteria are met, stop the automated dialogue and request human intervention through the shared escalation mechanism. Do not confuse escalation with the convergence-only human confirmation gate.

## Dependencies and boundary

This feature depends on `review-exchange-core` and `code-review-requestor`. The shared exchange transport, file lifecycle, transcript initialization, convergence state, timeout policy, and requestor continuation decisions remain owned by those requirements. This effort owns only the focused code-review responder, its adapter, and its answer-generation support.
