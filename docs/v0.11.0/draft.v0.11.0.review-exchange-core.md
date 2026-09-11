# Build the review exchange core

- Type: feature-request
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md

## Selected umbrella entry

| Order | Type | Key title | Slug | Status | Requirement | Validation plan |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Feature-request | Build the review exchange core | `review-exchange-core` | pending | - | - |

## Requirement detail inherited from the umbrella

- Regroups: the project-root `a.review-mode` opt-in marker; the request, answer, and versioned review-transcript artifact conventions; the shared requestor role or skill; reusable templates, scripts, and utility tools; safe create, overwrite, append, wait, and delete operations; the convergence-only human-confirmation state; mandatory review-summary identity; and the termination and human-intervention rules shared by specification and code review.
- Boundary rationale: the transport, naming, lifecycle, and safety policy must be settled once so every requestor and reviewer role can exchange files consistently without duplicating the protocol.
- Depends on: none.

## Shared review-mode behavior

Review mode is an opt-in, dialogue-based workflow between two LLM roles. The writer creates review instructions for its work, and an independent reviewer evaluates those instructions and returns constructive feedback and suggestions for improvement. The workflow is active only when `(project root)/a.review-mode` exists and is coordinated through `pw` (`prompt-workflow`).

The shared protocol must be implemented as its own complementary review-requestor role or skill. Existing writer skills reference that role instead of duplicating the requestor process. Specification-review and implementation-code-review integrations, and their two specialized reviewer roles, remain separate umbrella items.

Ordinary change-request rounds remain automated. A human gate appears only at convergence, when the reviewer recommends consolidation or commit-readiness. The reviewer recommendation is advisory: the requestor enters `awaiting-human-confirmation`, and only the human chooses whether to continue the owning workflow or start another review round. Timeout, abandonment, no-progress, disagreement, and inconsistent-state escalation remain a separate human entry path.

## Artifact model

Every exchange is identified by its review family, document type token, version, and slug. The shared tooling must support the two artifact families that later requirements specialize:

- Specification artifacts use `type.vX.Y.Z.slug.md`, `review.type.vX.Y.Z.slug.md`, `a.review-requested.type.vX.Y.Z.slug.md`, and `a.review-answer.type.vX.Y.Z.slug.md`, where `type` is `feature-request`, `issue`, `design-specification`, or `plan`.
- Implementation-code artifacts use `plan.vX.Y.Z.slug.md`, `review.code.vX.Y.Z.slug.md`, `a.review-requested.code.vX.Y.Z.slug.md`, and `a.review-answer.code.vX.Y.Z.slug.md`.

Transient request and answer files always live at the project root and rely on the existing `.gitignore` rule for `a.*` files. A versioned review transcript lives in the same folder as the reviewed document. That folder may be `docs`, `docs/vX.Y`, or `docs/vX.Y/vX.Y.Z`; the protocol must preserve the reviewed document's actual folder instead of assuming one fixed layout.

When the transcript does not exist, initialize it from an appropriate review-kind and version template. Agents append their general feedback for every request and answer round. The transcript exists only to document the dialogue: agents append to it but do not reread it as working context.

Every reviewee-to-reviewer summary includes a human-readable identity header. It states the umbrella draft path or `none`; specification summaries state the exact reviewed specification and round; implementation-code summaries state the exact plan, step, and round. The header must match the machine-readable exchange identity.

## Exchange lifecycle

The shared requestor and reviewer utilities must support this lifecycle safely:

1. Before a new request, the requestor deletes any stale matching answer.
2. The requestor creates or overwrites the matching root request and appends the same general feedback to the versioned transcript.
3. The reviewer waits for and reads the matching request, evaluates it, and prepares the matching answer.
4. When the answer is ready, the reviewer deletes the consumed request first, then writes the answer, in that order, and appends the same constructive feedback to the versioned transcript.
5. The requestor waits for and reads the answer. For an intermediate change request, it applies or assesses the recommendations, deletes the consumed answer, and automatically continues with a replacement request and the next round.
6. For a convergence recommendation, the requestor retains the answer as evidence, enters durable `awaiting-human-confirmation`, and presents the human with the identity-bearing summary, recommendation, and its assessment.
7. The human selects the family-specific label mapped to `another-round` or `continue-owning-workflow`. Another round records the override and optional human guidance, resets no-progress counters, includes any guidance in the replacement request summary, deletes the answer, and resumes automation. Continuing records confirmation, applies the owning action, and then deletes the answer.

File transitions must avoid leaving a requestor with both a stale request and a fresh answer. Waiting must identify the exact expected artifact rather than accepting an unrelated review file.

## Templates, scripts, and utilities

The review-requestor role or skill must include a template and script for generating review-requested content. Shared utilities may be added where needed for artifact-name derivation, transcript initialization and append, stale-artifact cleanup, exact-file waiting, and request/answer transitions. Specialized specification and code requirements supply their role-specific request conclusions and reviewer answer content.

The shared request summary template requires umbrella and reviewed-document context plus the review round. The core models role-neutral convergence outcomes as `another-round` and `continue-owning-workflow`; specialized requirements provide the displayed choice labels and convergence signal for their family.

The shared instruction must be reachable from the repository's LLM-specific wrappers using the established canonical-instruction reference pattern. The functional adapters for `review-ask-questions`, `consolidate-then-review-ask-questions`, `implement-step`, `spec-reviewer`, and `code-reviewer` are assigned to later umbrella items.

## Termination and human intervention

The protocol must define explicit termination criteria for every review dialogue. It must not wait forever or cycle indefinitely. It must stop and request human intervention when a review is not completed within the defined timely-wait policy, when the requestor and reviewer cannot resolve a disagreement, when repeated rounds make no meaningful progress, or when artifact state is inconsistent and cannot be recovered safely.

The normal convergence gate is not an escalation. While `awaiting-human-confirmation`, automated lease expiry is suspended and the durable state is re-presented by a later workflow session until the human confirms or cancels. Cancellation is recorded through the escalation-resolution path.

The eventual feature request and design must make those criteria observable and give clear recovery guidance. They must distinguish a normal reviewer wait from a timed-out or abandoned review and preserve enough transient or transcript evidence for a human to decide how to continue.
