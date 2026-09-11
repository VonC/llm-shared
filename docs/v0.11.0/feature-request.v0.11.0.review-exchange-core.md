# Build the review exchange core

## Review-mode revision that introduces the exchange core

The review-mode workflow adds a dialogue between two LLM roles. A writer produces instructions for reviewing its work, and an independent reviewer evaluates those instructions and returns constructive feedback or improvement suggestions.

The shared transport, artifact naming, lifecycle, waiting, transcript, and termination behavior must live in one reusable review-exchange core. Specification-review and implementation-code-review integrations then reference that core while keeping their specialized requestor and reviewer behavior in separate requirements.

## User story for the review exchange core

As a workflow author, I want an opt-in and role-neutral review exchange protocol so that writer and reviewer skills can coordinate repeated review rounds consistently, preserve a versioned dialogue record, and escalate safely when automation cannot finish the review.

## Current behavior in v0.11.0

- The workflows do not have a shared protocol for exchanging review requests and answers between independent LLM roles.
- Writer skills reach their existing human-review stops without a reusable requestor role that can take over when review mode is enabled.
- Request, answer, and transcript paths are not governed by one artifact contract shared by specification and code review.
- No common lifecycle defines stale-artifact cleanup, exact-file waiting, transcript appends, repeated rounds, timeout outcomes, disagreement handling, or human escalation.
- Templates, scripts, and utility operations for the exchange are not provided as one canonical capability referenced by the LLM-specific wrappers.

## Expected review exchange behavior

1. Review mode is enabled only when `(project root)/a.review-mode` exists.
2. Review exchanges are coordinated through `pw` (`prompt-workflow`).
3. The writer side delegates the common exchange behavior to a complementary review-requestor role or skill instead of duplicating that behavior in each writer skill.
4. Every exchange is addressed by its review family, document type token, version, and slug so unrelated exchanges cannot consume each other's artifacts. Specification exchanges use their supported document type, while implementation-code exchanges use the fixed `code` token.
5. Transient request and answer files live at the project root and use the existing `.gitignore` coverage for `a.*` files.
6. A versioned review transcript lives beside the reviewed document and records every requestor and reviewer round.
7. Shared templates, scripts, and utilities implement the common artifact and lifecycle operations used by later specification and code review requirements.
8. Intermediate reviewer answers that request changes are applied and followed by another review round automatically, without a human wait.
9. The exchange reaches convergence only when the reviewer recommends the continuing action for its family. That recommendation is advisory, and the owning workflow proceeds only after explicit human confirmation.
10. At convergence, the core enters durable `awaiting-human-confirmation`; this state is distinct from timeout, abandonment, no-progress, disagreement, and inconsistent-state escalation.
11. Every reviewee-to-reviewer summary identifies its umbrella draft or `none`, its exact reviewed specification or implementation plan, its review round, and its implementation step for code review. Human-readable fields must match the machine-readable exchange identity.
12. The protocol stops and requests human intervention through the separate escalation path when its bounded wait or progress rules cannot produce a safe automated outcome.

## Review artifact contract

The core must support both artifact families without embedding the specialized feedback text that later requirements define.

| Review family | Reviewed document | Versioned transcript beside the document | Root request | Root answer |
| --- | --- | --- | --- | --- |
| Specification | `type.vX.Y.Z.slug.md` | `review.type.vX.Y.Z.slug.md` | `a.review-requested.type.vX.Y.Z.slug.md` | `a.review-answer.type.vX.Y.Z.slug.md` |
| Implementation code | `plan.vX.Y.Z.slug.md` | `review.code.vX.Y.Z.slug.md` | `a.review-requested.code.vX.Y.Z.slug.md` | `a.review-answer.code.vX.Y.Z.slug.md` |

Every Markdown artifact carrying machine-readable JSON starts with one `#`
title. Its first section is `## JSON`, containing the fenced JSON metadata.
Later role-authored top-level sections start at `##`, so no document jumps from
its H1 title directly to H3 content. The durable coordination record follows the
same title-then-JSON-section structure and has no authored trailing content.

For specification review, `type` is `feature-request`, `issue`, `design-specification`, or `plan`.

The reviewed document and transcript may be directly under `docs`, under `docs/vX.Y`, or under `docs/vX.Y/vX.Y.Z`. Artifact derivation must preserve the reviewed document's actual parent folder rather than assuming one fixed documentation layout.

When a versioned transcript does not exist, the core initializes it from the template for the review family and version. Requestors and reviewers append their general feedback to it for documentation, but agents do not reread the transcript as working context. Every appended entry identifies its authoring role and completed round so a human can verify the dialogue order and no-progress decisions.

Different reviewed documents may have active exchanges concurrently, but one reviewed document may have only one active exchange. The current artifact identity gives concurrent exchanges for the same document identical file names, so supporting more than one would require a reviewer or exchange discriminator that is outside this contract.

## Review exchange lifecycle

1. Before publishing a new request, the requestor deletes any stale matching answer.
2. The requestor creates or overwrites the exact matching root request and appends the same general feedback to the versioned transcript.
3. The reviewer waits for the exact matching request, reads it, evaluates it, and prepares the matching answer.
4. When the answer is ready, the reviewer deletes the consumed request first, then writes the answer, in that order, and appends the same constructive feedback to the versioned transcript.
5. The requestor waits for the exact matching answer and reads it. When the reviewer requests changes, the requestor applies or assesses them, deletes the consumed answer, and automatically creates a replacement request for the next round.
6. When the reviewer recommends convergence, the requestor retains the answer as evidence, enters `awaiting-human-confirmation`, and presents the identity-bearing summary, reviewer recommendation, and requestor assessment to the human.
7. The human selects the family-specific choice mapped to the role-neutral outcome `another-round` or `continue-owning-workflow`. Another round records the override and optional human guidance, resets no-progress counters, includes any guidance in the replacement request summary, deletes the answer, and resumes automation. Continuing records confirmation, performs the owning action, and then deletes the answer.

The transition that publishes an answer must not leave the requestor with both a stale request and a fresh answer. If both matching files are present, the state is inconsistent: the core fails closed, preserves the conflicting evidence, and requests human intervention. Waiting must match the full expected artifact identity and must not accept an unrelated review file.

Two consecutive completed change-request rounds count as no meaningful progress when the reviewed work does not substantively change. A convergence recommendation always ends the automated loop at the human gate. When the requestor and reviewer explicitly disagree, they receive one dedicated clarification round and escalate to a human if the disagreement remains.

## Convergence gate and review-summary contract

A reviewer answer unambiguously declares either an intermediate change request or a convergence recommendation. The later specification and code requirements define their family-specific convergence signal and choice labels. The core models only `another-round` and `continue-owning-workflow`.

Every reviewee-to-reviewer request summary, and the presentation shown again at convergence, includes:

- `Umbrella draft: <path>` or `Umbrella draft: none`.
- `Reviewed specification: <path>` and `Review round: <n>` for specification review.
- `Implementation plan: <path>`, `Implementation step: <identifier>`, and `Review round: <n>` for implementation-code review.
- The reviewer recommendation and the requestor's assessment.

The core validates those values against machine-readable exchange context and fails closed on mismatch. The reviewer cannot select or trigger the human choice. The confirmation choice, role-neutral outcome, local timestamp with numeric UTC offset, and any human override are recorded in the durable coordination state and transcript.

`awaiting-human-confirmation` survives process exit. Automated lease expiry is suspended only in this state, and a later `pw` session re-presents the pending summary and choices rather than classifying the exchange as abandoned. Human cancellation is recorded through the escalation-resolution path.

## Templates, scripts, utilities, and adapters

- The complementary review-requestor role or skill includes a template and script for generating review-requested content.
- Shared utilities may cover artifact-name derivation, transcript initialization, transcript append, stale-artifact cleanup, exact-file waiting, and request/answer transitions.
- The core ships the canonical review-requestor instruction and its own LLM-specific wrapper using the established canonical-instruction reference pattern.
- The functional adapters for `review-ask-questions`, `consolidate-then-review-ask-questions`, `implement-step`, `spec-reviewer`, and `code-reviewer` belong to later umbrella requirements. They reference the core rather than copy its common lifecycle.
- The core provides the mandatory identity-bearing request-summary shape and role-neutral convergence outcomes; specialized requestor requirements register their displayed human choices and convergence signals.
- Fixed request and answer conclusion templates are coordination boilerplate. Role-authored analysis, decisions, recommendations, and response summaries are substantive feedback and are copied completely into the transcript.
- Specialized request conclusions, reviewer answer content, writer-specific continuation decisions, and code-fix behavior remain assigned to the later specification-review and implementation-code-review requirements.

## Termination and human intervention

Every review dialogue must have explicit, observable termination criteria. The exchange must stop and request human intervention when any of these conditions applies:

- the matching request or answer is not produced within the defined timely-wait policy;
- the requestor and reviewer cannot resolve a disagreement;
- repeated rounds make no meaningful progress;
- artifact state is inconsistent and the protocol cannot recover without risking loss or applying feedback to the wrong review.

The content of `a.review-mode` holds the per-project wait override; when it does not provide one, the documented default applies. A wait is timed out when the current bounded wait exceeds that effective limit while the counterpart artifact is still absent. An exchange is abandoned when matching transient artifacts or an unresolved escalation record exist but no active round is progressing them, including state discovered after an interrupted session, except while the exchange is in `awaiting-human-confirmation`.

A round abandoned only by lease expiry, with intact matching evidence and no recorded escalation, can be reclaimed in place by the returning expected actor; reclaiming renews the durable lease and changes no artifact or transcript content. On timeout or abandonment, the core preserves the current matching transient artifacts and appends an escalation record to the transcript. After human intervention, the human resolves the preserved evidence and clears or archives the stopped transient state. Automation resumes with a fresh review round whose response summary and human resolution are appended to the transcript escalation record.

## File-based IO cost clarification

The core receives an exact reviewed-document path and derives a constant set of exact transcript and transient paths once per exchange. Normal activation, state inspection, waiting, publication, and confirmation must not scan documentation directories or load versioned transcript history; each waiting poll checks only the exact counterpart and coordination paths. Idempotent append or repair may inspect only a bounded transcript tail for its stable entry identifier. Git-ignore validation checks only the constant derived transient set, and recovery touches only the artifacts for the selected exchange identity.

## Requirement clarifications for the review exchange core

| Question | Accepted clarification | Arguments | Integrated in | Rejected alternatives |
| --- | --- | --- | --- | --- |
| Q01 | Allow concurrent exchanges for different documents, with only one active exchange per reviewed document. | The artifact identity already gives same-document exchanges identical names; this preserves useful parallelism without ambiguous ownership. | Review artifact contract | One project-wide exchange; multiple concurrent exchanges for one document |
| Q02 | Use a documented default wait limit with a per-project override in `a.review-mode`. | Every wait remains bounded while projects can adapt the limit through the marker that already gates the feature. | Termination and human intervention | One fixed limit; indefinite wait |
| Q03 | Declare no progress after two consecutive completed change-request rounds do not substantively change the reviewed work; convergence always exits the automated loop to the gate. | The rule targets observable stagnation without introducing a decision signal that does not exist between automated rounds. | Review exchange lifecycle | Fixed total round cap; role-declared stagnation only |
| Q04 | Allow one dedicated clarification round after an explicit disagreement, then escalate if disagreement remains. | One round can correct a misunderstanding while keeping conflict strictly bounded. | Review exchange lifecycle | Immediate escalation; unlimited automated debate |
| Q05 | Fail closed, preserve conflicting evidence, and request human intervention for inconsistent artifact state. | Guessing from timestamps or transcripts can apply feedback to the wrong work. | Review exchange lifecycle | Trust newest artifact; reconstruct automatically from transcript |
| Q06 | Append complete substantive role-authored feedback while excluding fixed coordination boilerplate. | Templates make the boundary observable and preserve review reasoning without repetitive control text. | Templates, scripts, utilities, and adapters | Append complete artifacts; append summaries only |
| Q07 | Preserve matching transient artifacts and append an escalation record on timeout or abandonment. | Human recovery is safer when unresolved evidence remains available and the stop is versioned. | Termination and human intervention | Delete all transients; preserve only the newest artifact |
| Q08 | After human resolution, clear or archive stopped state and start a fresh round with the resolution summary in the transcript. | A fresh authoritative boundary prevents ambiguous state from silently regaining control. | Termination and human intervention | Resume from existing artifact; unrecorded operator choice |

## Acceptance criteria for the review exchange core

1. With no root `a.review-mode` marker, existing writer workflows keep their normal non-review-mode behavior and do not create review exchange artifacts.
2. With the marker present, a writer integration can invoke the core's canonical review-requestor instruction through its own wrapper and `pw` rather than implement the common exchange itself.
3. The core derives all four artifacts for a specification review from a supported document type, `vX.Y.Z`, slug, and the reviewed document's real parent folder.
4. The core derives all four artifacts for an implementation-code review from its plan version, slug, and real parent folder.
5. Root request and answer artifacts use the exact `a.review-requested.*` and `a.review-answer.*` naming rules and remain covered by the existing `a.*` ignore behavior.
6. Transcript initialization uses the correct review-family and version template when the sibling `review.*` file is absent and preserves an existing transcript when it is present.
7. Requestor and reviewer feedback is appended to the transcript with its authoring role and completed round, without requiring the agent to read previous transcript content.
8. Publishing a new request removes a stale matching answer before the request becomes available.
9. Publishing an answer deletes the matching request before exposing the matching answer; both matching files being present is treated as an inconsistent state and fails closed.
10. Consuming an answer removes it, and a later round can create a replacement request containing the requestor's response summary.
11. Exact-file waiting cannot be satisfied by an artifact with a different review family, document type token, version, or slug.
12. The shared request-generation template and script, plus any supporting utilities, are available through the core's canonical instruction and wrapper; the five functional skill adapters remain assigned to later umbrella requirements.
13. A bounded wait uses the documented default or the `a.review-mode` per-project override and reports whether the exchange is active, timed out, or abandoned using the definitions in this requirement.
14. Two consecutive completed change-request rounds with no substantive change to the reviewed work, disagreement remaining after one clarification round, and unrecoverable artifact inconsistency stop automation and request human intervention; convergence recommendations exit to the confirmation gate instead.
15. On timeout or abandonment, matching transient artifacts remain available and the transcript records the escalation, authoring role, and round.
16. After human intervention, automation resumes only through a fresh round after the stopped state is resolved and cleared or archived, and the human resolution is recorded in the transcript.
17. Different documents can be reviewed concurrently, but a second active exchange for the same reviewed document is rejected by the core contract.
18. Request, answer, tombstone, archive, and coordination Markdown starts with
    an H1 title followed by a first `## JSON` section; later authored top-level
    request or answer sections use H2 headings.
18. The core does not implement the specialized specification request text, specification reviewer decisions, implementation report text, code fixes, or owning-workflow continuation decisions assigned to later umbrella items.
19. An intermediate change-request answer is consumed and followed by another automated round without entering a human-wait state.
20. A convergence recommendation enters `awaiting-human-confirmation`, retains the answer as evidence, and cannot continue the owning workflow without an explicit human choice.
21. Specification consolidation cannot occur before the human confirms the family choice mapped to `continue-owning-workflow`.
22. Implementation commit cannot occur before the human confirms the family choice mapped to `continue-owning-workflow`.
23. Choosing another round at convergence records the human override and any optional guidance, resets no-progress counters, includes the guidance in the replacement request summary, and returns to automated review.
24. `awaiting-human-confirmation` survives process exit, suspends automated lease expiry, and is re-presented by a later workflow session.
25. Every requestor summary names its umbrella or `none`, exact reviewed specification or plan, round, and code step when applicable.
26. A mismatch between summary identity and machine-readable exchange identity fails closed before the request is published.
27. Reclaiming an abandoned round with intact evidence and active coordination restores its pending state in place by lease renewal without changing artifacts or the transcript; reclaim is rejected once the exchange is escalated, awaiting confirmation, interrupted, or inconsistent.
