# Review staged implementation work without taking commit authority

## CDC revision that introduces the code reviewer

The review-mode umbrella separates implementation review into two roles. The completed `code-review-requestor` effort lets the implementation writer publish an identity-bearing review request after `group-commits-msg`. This feature adds the complementary `code-reviewer` responder, which independently assesses one staged implementation step, repairs missing work when appropriate, and reports whether another automated round is needed or the requestor may ask a human for commit authorization.

The code reviewer is advisory. It must never commit, authorize a commit, or replace the requestor's responsibility for continuing the implementation workflow.

## User story for independent implementation review

As an implementation writer using review mode, I want a separate LLM role to inspect my staged changes against the exact plan step and `implementation-check`, so that missing work can be repaired and reviewed through bounded automated rounds before a human decides whether the changes may be committed.

## Current behavior in v0.11.0

- The shared review exchange defines durable identities, request and answer artifacts, versioned transcripts, bounded waits, convergence gates, and escalation states.
- The implementation requestor can publish the derived code-family request artifact with the umbrella, exact plan, implementation step, and review round.
- No focused code-review responder currently owns waiting for that request, reviewing the staged implementation, publishing the corresponding answer, and relinquishing the request artifact atomically through the shared exchange.

## Gap to close for the code-review responder

1. Provide a `code-reviewer` role that accepts the plan document selected by `pw` and waits for the matching implementation-code review request.
2. Require the reviewer to validate that the human-readable umbrella, plan, step, and round agree with the machine-readable exchange identity before assessing any work.
3. Require review against the request, the exact implementation plan step, staged changes, `a.commit`, and the `implementation-check` criteria.
4. Allow the reviewer to repair missing implementation work and amend `a.commit` when necessary, while forbidding commits and any claim of commit authority.
5. Publish complete constructive findings that either request rework or recommend commit-readiness, append the paired substantive summary of those findings to the versioned sibling transcript, and remove the consumed request only when the answer is ready.
6. Provide the LLM-specific adapter, answer template, and generation script needed to expose the canonical reviewer behavior consistently.

## Expected review behavior and boundaries

- The reviewer resolves the exact exchange identity from the supplied plan and does not select a nearby plan, request, answer, or transcript by filename similarity.
- The reviewer waits through the shared bounded mechanism and follows the shared recovery or escalation result instead of implementing an unbounded polling loop.
- The reviewer reads the exact request returned for the active identity, validates its umbrella or `none`, plan, step, and positive round, and stops through the shared diagnostic path when those values are missing or inconsistent.
- The reviewer inspects the staged changes and applies the `implementation-check` criteria to determine whether the named plan step is fully implemented.
- When work is missing, the reviewer may repair it within the named step, stage only its own repairs, list every repair in the answer, and update `a.commit` so its grouped commit messages describe the resulting staged changes.
- A repair is in scope only when every file it touches is named by the reviewed plan step or already present in that step's staged set, it introduces no new design decision, and it changes no work belonging to another step or requirement. The reviewer returns anything else to the writer with the boundary-crossing reason.
- A reviewer-authored change to any tracked file is substantive, except `a.commit` and reviewed-step validation rows that record the reviewer's own `implementation-check` result. A substantive change forces a `changes-requested` intermediate outcome in that same round.
- Unrelated staged content is reliably separable only when it touches no file named by the reviewed plan step and `a.commit` places it in a distinct commit group. The reviewer reports all unrelated staged content and withholds commit-readiness whenever either condition fails.
- Applying the `implementation-check` criteria may update validation-plan rows for the reviewed step as an in-scope repair, but it never updates an umbrella status table during review.
- A round that stops without publishing leaves the working tree and index untouched and records every reviewer repair plus the assessed staged-tree identity in caller-owned ignored evidence. The assessed staged-tree identity is the Git tree object of the index at the moment the reviewer completed its assessment.
- The reviewer never commits, never calls the human-confirmation operation, and never treats its own recommendation as authorization.
- An intermediate outcome requests rework and another automated review round. A convergence outcome recommends commit-readiness and leaves the requestor to enter `awaiting-human-confirmation`.
- When mandatory evidence is unavailable, the reviewer requests rework the first time. It escalates when the same evidence remains unavailable in the next round, when the writer disputes that it is mandatory, or when the shared no-progress bound is reached. Missing or disputed mandatory evidence always blocks commit-readiness.
- Timeout, abandonment, repeated no-progress, disagreement, inconsistent artifacts, and interrupted transitions remain escalation or recovery concerns distinct from convergence.

## Commit-readiness evidence floor

The reviewer may recommend commit-readiness only when every applicable item below agrees:

1. The human-readable and machine-readable exchange identities match exactly.
2. The exact plan step is fully implemented under the `implementation-check` criteria.
3. Every mandatory validation command completes with a passing result under the project's own gate, including its coverage threshold.
4. The staged diff is attributable to the reviewed step under the accepted contamination rule.
5. No finding raised in this round, and no finding carried into the current request, remains unresolved.
6. `a.commit` accurately groups and describes the staged changes.

The project's validation entry point and coverage gate supply the default mandatory verification set. The plan step or review request may add stricter evidence but may not remove an item from that default set.

## File-based IO cost clarification for the code reviewer

The reviewer resolves exact request, plan, validation-plan, manifest, and answer paths from the exchange identity. It does not scan directories to discover nearby artifacts. Each explicit input is read once per assessment phase, retained evidence uses one stable ignored path, and paired answer outputs are written together before publication.

## Review artifacts and transcript rules

- The shared `review-exchange-core` derives the exact request, answer, and transcript names from the exchange identity, and every artifact must agree with that identity.
- The answer carries the complete reviewer findings, while the transcript entry carries the paired substantive summary of the same findings.
- The transcript is append-only for agents and is not reread as working context.
- Publishing the ready answer consumes the matching request through the shared exchange lifecycle.
- The root artifacts continue to rely on the existing `a.*` ignore rule.

## Acceptance criteria for the code reviewer

1. Given review mode is active and a valid code-review request is pending, invoking `code-reviewer` with the exact plan selected by `pw` waits for and reads only that request.
2. A request whose umbrella, plan, step, or round disagrees with its exchange identity, or whose step identifier is not defined by the referenced plan, is rejected without reviewing or mutating the staged implementation.
3. A valid review applies the `implementation-check` criteria to the named plan step, staged changes, and `a.commit` without creating a commit or updating an umbrella status table.
4. When the implementation is incomplete, the reviewer can make bounded in-scope repairs, stage only those repairs, list them in the answer, amend `a.commit` when needed, and publish an intermediate answer requesting another round.
5. The reviewer recommends commit-readiness only when it made no substantive staged change in that round and every applicable item in the commit-readiness evidence floor passes; the recommendation never authorizes or performs a commit.
6. Publishing an answer appends the paired substantive summary of the same findings to the sibling versioned transcript and removes the consumed request only after the answer is ready.
7. Disabled review mode, bounded-wait expiry, abandonment, no-progress, disagreement, inconsistent identity, and interrupted state follow the shared diagnostic, recovery, or human-escalation behavior.
8. The responder is exposed through the canonical shared `code-reviewer` instruction, its LLM-specific skill wrapper, a review-answer template beside the existing review-request template, and an answer-generation launcher matching the existing `bin/code_review_request` entry point, without duplicating the shared exchange state machine.

## Requirement clarifications for the code reviewer

| Question | Decision | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | Allow only bounded repairs whose files and behavior remain inside the reviewed plan step, and list every repair in the answer. | Expected review behavior and boundaries; acceptance criterion 4 | Report-only review; unrestricted repair authority |
| Q02 | Require another round after substantive tracked-file changes, while exempting `a.commit`, ignored caller files, review artifacts, and reviewed-step validation rows that record the reviewer's own check. | Expected review behavior and boundaries; acceptance criterion 5 | Same-round approval of substantive repairs; another round after every mutation |
| Q03 | Review only the named step, report unrelated staged work, and withhold readiness when file overlap or `a.commit` grouping prevents reliable separation. | Expected review behavior and boundaries; commit-readiness evidence floor | Review every staged change; reject every contaminated index |
| Q04 | Require all six applicable readiness evidence items to agree before recommending commit-readiness. | Commit-readiness evidence floor; acceptance criterion 5 | `implementation-check` alone; a per-request threshold |
| Q05 | Request rework on the first unavailable mandatory check, then escalate on repeated absence, dispute, or the shared no-progress bound. | Expected review behavior and boundaries; acceptance criterion 7 | Always rework; immediate escalation |
| Q06 | Take project validation and coverage gates as mandatory defaults, allowing only additive plan-step or request evidence. | Commit-readiness evidence floor | Plan-only checks; request-only checks |
| Q07 | Permit reviewed-step validation-row updates but forbid umbrella status updates during review. | Expected review behavior and boundaries; acceptance criterion 3 | Run all `implementation-check` writes; make the check wholly read-only |
| Q08 | Preserve the tree and index on an interrupted round and retain repair provenance plus the assessed Git index tree object. | Expected review behavior and boundaries; acceptance criterion 7 | Revert repairs; defer provenance to the next request |
| Q09 | Stage only reviewer-authored repairs and report, but never stage, pre-existing unstaged work. | Expected review behavior and boundaries; acceptance criterion 4 | Stage all in-scope work; leave reviewer repairs unstaged |

## Dependencies for the code reviewer

This feature depends on the completed `review-exchange-core` and `code-review-requestor` efforts. Those efforts continue to own transport, artifact lifecycle, transcript initialization, durable state, timeout and escalation policy, requestor continuation, and human confirmation. This feature owns the focused responder assessment, permitted repairs, advisory recommendation, adapter, and answer-generation support.
