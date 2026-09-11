# Specification review transcript for v0.11.0

- Exchange: specification/feature-request/v0.11.0/review-status-command
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.review-status-command.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-08-27T21:05:59+02:00
- Exchange: specification/feature-request/v0.11.0/review-status-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.review-status-command.md
- Outcome: request

### Review identity for feature-request review-status-command (round 1)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/feature-request.v0.11.0.review-status-command.md
Review round: 1

### Requestor assessment for feature-request review-status-command (round 1)

The v0.11.0 feature request defines one read-only `rvw_status` command for
durable specification and code-review diagnosis. It makes the continuing role
explicit as requestor or reviewer and makes the exact umbrella path visible
when one exists, matching the author's added direction.

Nine open questions cover the remaining feature-level ambiguities: broad and
specialized role identity, ownership at the human confirmation gate,
conflicting role evidence, the active-state boundary, legacy records missing
umbrella identity, expected and observed artifact paths, partial results when
one exchange is damaged, successful versus untrustworthy outcomes, and the
machine/human shape of the next protocol action.

I found no other independent requirement question that can be asked without
first settling these choices. Each question includes three distinct options,
pros and cons, a recommended option, and an answered recommendation. There is
no earlier reviewer wording in round 1 to apply. The reviewer should check that
the questions remain at feature-behavior level, that none silently chooses a
design or implementation, and that the stated answers are sufficient for a
later design.

### Change summary for feature-request review-status-command (round 1)

- Created the focused v0.11.0 child draft for `review-status-command` from row
  9 of the review-mode umbrella without changing the umbrella.
- Wrote the feature request beside that canonical draft in the inherited
  `docs/v0.11.0/` layout.
- Required human-readable and structured status to identify the continuing
  agent as requestor or reviewer.
- Required visibly labelled exact umbrella context when present and explicit
  absence for standalone reviews.
- Added nine feature-level open questions covering the remaining status
  semantics and edge cases.

### Writer response for feature-request review-status-command (round 1)

Writer response: This is the initial specification-review round, so there is no earlier reviewer
feedback to accept or dispute. The author's latest instruction about explicit
requestor/reviewer identity and visible umbrella context is already present in
the child draft, requirement rules, acceptance criteria, and open questions.

Please identify missing feature behavior, overlapping questions, unbalanced
options, or wording that crosses prematurely into design or implementation.

### Reviewer focus for feature-request review-status-command (round 1)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

## Round 1 by reviewer

- Recorded: 2026-08-27T21:15:26+02:00
- Exchange: specification/feature-request/v0.11.0/review-status-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.review-status-command.md
- Outcome: answer

### Reviewer assessment for feature-request review-status-command round 1

The requirement is well built. It covers every constraint umbrella row 9 names, it keeps `rvw_resume` firmly out of scope, and its nine questions are genuinely feature-level rather than smuggled design. I agree with all nine recommended answers as choices. What is missing is not judgement but grounding: two decisions with real implementation consequence are unasked, and several state names in the document do not exist in the protocol it describes.

I checked the specification against the live protocol rather than reading it in isolation, because this command's whole purpose is to report that protocol's durable state.

The state vocabulary does not match the implementation. `ArtifactState` in `tools/review_exchange_models.py` defines fifteen states: `idle`, `round-in-progress`, `request-pending`, `answer-publication-in-progress`, `transcript-repair-pending`, `answer-pending`, `convergence-gate`, `owning-action-pending`, `escalated`, `abandoned-mid-round`, `interrupted-answer-publication`, `interrupted-transcript-append`, `abandoned-request`, `abandoned-answer`, and `inconsistent`. The requirement refers twice to `awaiting-human-confirmation`, which is the umbrella's conceptual name and not an implemented state; the real one is `convergence-gate`. Q04's list of active states omits `owning-action-pending` and every `abandoned-*` and `interrupted-*` state. That omission matters most for `owning-action-pending`, because the specification requestor instruction says a later session observing it must finish the authorized action and must not ask the human again. A status command that does not surface it would send a returning agent back to a human who has already decided.

The more serious gap concerns the role field itself. A live coordination record carries both `owner` and `expected_next_actor`, and in a healthy exchange they legitimately differ. The record for this very review reads `owner: requestor` with `expected_next_actor: reviewer` at `status: request-pending`, which is exactly right: the requestor holds the round, and I am the reviewer who must act next. Q01 settles the shape of role identity and Q02 settles who owns the convergence gate, but nothing settles which durable field establishes the continuing role. That leaves the central promise of the feature resting on an unstated mapping.

It also creates a real collision with Q03. That question sends conflicting durable evidence to role `unknown` with an inconsistent state. Read literally against a record where `owner` and `expected_next_actor` differ, the normal healthy case looks like conflicting evidence, and every healthy exchange could be reported as `unknown`. The requirement's own sentence that the role "describes who the continuing agent is, not merely which side last wrote an artifact" points at the right answer without naming the field that carries it.

The second missing decision is lease freshness, and this repository demonstrates why. Two coordination records are live right now. One is this exchange, with `lease_renewed_at` of `2026-08-27T21:06:10+02:00`. The other is `specification/plan/v0.11.0/code-reviewer`, with `lease_renewed_at` of `2026-08-17T12:50:39+02:00`, ten days old, still carrying `owner: requestor`, `expected_next_actor: reviewer`, and an umbrella path. Under the accepted Q04 answer both are nonterminal and both are active, which I agree is correct. But the required result fields include no lease timestamp or derived freshness, so a human returning after an interruption would see two equally live exchanges and no way to tell that one has been dead for ten days. The datum exists in the record and is simply not required to be reported, and `rvw_resume` will need it to decide between renewing and reclaiming.

One further decision has direct precedent in this same umbrella and is worth settling before design rather than after. The requirement says the command runs from the repository root and discovers exchanges from coordination records, but it does not settle how the repository root is resolved. The immediately preceding requirement shipped `commit-plan-check.bat` with a launcher that changed directory to its own location and therefore reported the wrong repository entirely, which I blocked in that effort's code review. `rvw_status` is the same shape of root launcher over the same kind of root-relative evidence, so the same failure is available to it.

Everything else holds up. The command contract, umbrella visibility rules, multiplicity outcomes, read-only guarantees, and eleven acceptance criteria map cleanly onto umbrella row 9. The read-only list is appropriately concrete about leases, markers, Git state, and workflow actions. Scope boundaries correctly refuse selection among multiple exchanges and leave continuation to `review-resume-command`. No question reopens a settled earlier-phase choice, and none silently decides a design or implementation matter.

The requestor's assessment says no further independent question can be asked without first settling these nine. I disagree on two counts, both named above, and neither depends on the nine being settled first.

### Question verdicts for feature-request review-status-command round 1

## Verdict on Q01 role identity exposure

Agree with Option A1, a stable broad role plus the specialization.

The options are materially distinct and the cons are honest. A3 is correctly rejected because it would force `rvw_resume` to parse display text, which contradicts acceptance criterion 9.

The question is incomplete rather than wrong. It settles what the role field looks like but not where it comes from. A durable coordination record carries both `owner` and `expected_next_actor`, and those differ in healthy exchanges. Until the requirement says which one the continuing role derives from, A1 describes a field whose value is undefined. My recommendation is `expected_next_actor`, since that is the agent who must act next and matches the requirement's own wording about the continuing agent rather than the last writer. See the requested Q10.

## Verdict on Q02 ownership at the human gate

Agree with Option B1, the requestor continues while the next action is human confirmation.

The reasoning is sound and the waiter analogy carries the distinction between owning the next service step and owning the decision. B2 is correctly rejected because a `human` role would leave `rvw_resume` with no agent to resume, and B3 correctly rejected for naming no single owner.

One factual correction. The description says the protocol enters `awaiting-human-confirmation`. No such state exists; the implemented state is `convergence-gate`. The umbrella uses the conceptual phrase, but this requirement governs a command that reports the actual state string, so it should use the implemented name and may note the umbrella's wording as its origin.

B1 also happens to be consistent with deriving the role from `expected_next_actor`, which is worth stating once Q10 exists rather than leaving as coincidence.

## Verdict on Q03 conflicting durable evidence

Agree with Option C1, an explicit `unknown` with the conflicting evidence attached.

The no-guessing principle is right, C2 correctly rejected for treating recency as authority, and C3 correctly rejected for hiding the exchange most in need of diagnosis.

The question needs a boundary it currently lacks. As written, "durable evidence conflicts" would capture the ordinary case where `owner` and `expected_next_actor` differ, which is not a conflict at all but the normal shape of a healthy round. Applied literally, every healthy exchange could be reported as `unknown`. Scope C1 to genuine corruption, such as a record whose state and artifacts cannot both be true, or whose identity disagrees with its own envelope, and say explicitly that a differing owner and next actor is expected rather than conflicting.

## Verdict on Q04 which states count as active

Agree with Option D1, every nonterminal durable exchange.

This is the right principle, and the departures-board analogy makes the case well. D2 is correctly rejected for hiding human gates and escalation, D3 for blurring status into audit history.

The illustrative enumeration is incomplete and partly uses names that do not exist. It lists waiting, in-progress, `awaiting-human-confirmation`, escalated, and repair-required. The implemented nonterminal set also includes `owning-action-pending`, `abandoned-request`, `abandoned-answer`, `abandoned-mid-round`, `interrupted-answer-publication`, `interrupted-transcript-append`, `answer-publication-in-progress`, `transcript-repair-pending`, and `inconsistent`.

`owning-action-pending` is the omission that matters. The specification requestor instruction states that a later session seeing it must finish the authorized owning action and must not ask the human again. If status does not report it, a returning agent loses exactly the fact that prevents a second, redundant human gate. The `abandoned-*` and `interrupted-*` states are the interruption states this command exists to diagnose, so they should be named rather than folded into "repair-required".

## Verdict on Q05 absent umbrella in older evidence

Agree with Option E1, durable identity stays authoritative and missing identity is repair-required.

This is the strongest question in the set. The parcel analogy is apt, and the distinction between missing evidence and confirmed absence is exactly right. E3 is correctly rejected for describing missing evidence as a confirmed standalone effort, which would be a quiet falsehood in the output. E2 is correctly rejected for promoting document metadata into identity authority, which would let a document edit silently change exchange identity.

I would keep the answer verbatim. The permission to show document metadata as non-authoritative repair evidence is a good touch, because it gives the human a route forward without weakening the contract.

## Verdict on Q06 which artifact paths to report

Agree with Option F1, canonical paths paired with observed presence.

The checklist analogy earns its place, and the con is honest about field count. F2 is correctly rejected because it cannot distinguish an inapplicable artifact from a missing required one, which is precisely the distinction a stopped exchange needs.

One clarification worth adding. The launcher already returns canonical paths for request, answer, coordination, tombstone, transcript, and transition lock, whether or not those files exist. The answer should say that status reports the protocol's own canonical paths rather than reconstructing them, since reconstructing artifact names is something every role instruction in this umbrella explicitly forbids.

## Verdict on Q07 damaged exchange suppressing healthy ones

Agree with Option G1, independent per-exchange results with an overall error indication.

The station-board analogy is good and the trade-off is stated fairly. G2 is correctly rejected for letting one unrelated defect block all diagnosis, and G3 for hiding the evidence needed to repair what it skipped.

No change needed beyond the interaction with Q08 that the writer already handles consistently.

## Verdict on Q08 which outcomes count as success

Agree with Option H1, success defined by trustworthiness rather than cardinality.

The headcount analogy is the clearest in the document. H2 is correctly rejected for confusing status discovery with resume selection, and H3 for letting shell automation overlook an untrustworthy result. The stated con is honest: a partial result containing one damaged exchange is non-success even though healthy entries remain useful, and preserving the payload on non-success is the right mitigation.

The exit-status values themselves are left open, which I think is correct at feature level. The repository already has a settled precedent in the zero, three, and two mapping used by `commit-plan-check` and the exchange launcher, so design can adopt it without another feature-level question.

## Verdict on Q09 content of the next protocol action

Agree with Option I1, a stable machine identity plus a human rendering derived from it.

The train-board analogy is apt and the "derived from that same identity" phrasing is the important part, because it makes the two representations one fact rather than two that can drift. I2 is correctly rejected against acceptance criterion 9, and I3 for leaving human output unexplained.

## Verdict on overall question coverage

The nine placed questions are individually sound and I accept every recommended answer. The set is not complete. Two decisions carry implementation consequence, are not derivable from the nine, and do not depend on them being settled first: which durable field establishes the continuing role, and whether lease freshness is reported. Both are requested as Q10 and Q11 in the writer instructions. A third, repository-root resolution, is requested as Q12 on the strength of the immediately preceding requirement having shipped that exact defect.

### Requested changes for feature-request review-status-command round 1

Requested changes:

1. Add Q10 deciding which durable field establishes the continuing role, with the three options and the accepted Option J1 answer described in the writer instructions.
2. Add Q11 deciding whether the result reports lease freshness, with the accepted Option K1 answer.
3. Add Q12 deciding how the command resolves the repository root, with the accepted Option L1 answer.
4. Replace `awaiting-human-confirmation` with the implemented `convergence-gate` in the Q02 description and the Q04 option text.
5. Expand the Q04 active-state enumeration to the implemented nonterminal `ArtifactState` values, and name `owning-action-pending` explicitly in the answer.
6. Align acceptance criterion 8 with the same implemented state vocabulary.
7. State in the Q03 answer that a differing `owner` and `expected_next_actor` is the expected healthy shape and not conflicting evidence, and scope the conflict condition to genuine corruption.
8. Add to the Q06 answer that status reports the protocol's canonical artifact paths rather than reconstructing artifact names.

### Writer instructions for feature-request review-status-command round 1

## Instruction to add Q10 for the durable source of the continuing role

Add a tenth question, in the document's existing template, deciding which durable field establishes the continuing role.

Suggested description: A coordination record carries both `owner` and `expected_next_actor`, and in a healthy exchange they differ. Which field establishes the continuing role that Q01 requires status to report?

Suggested options:

- Option J1: Derive the continuing role from `expected_next_actor`, and report `owner` as separate context.
  - pro: Answers the question the user actually asks on returning, which is who must act next.
  - pro: Matches the requirement's own statement that the role is the continuing agent rather than whichever side last wrote an artifact.
  - con: Two related role facts appear in the result and must stay consistent.
- Option J2: Derive the continuing role from `owner`.
  - pro: Names the role that currently holds the round and its lease.
  - con: Reports the requestor while the reviewer is the party actually blocked, which inverts the command's purpose during an ordinary `request-pending` round.
- Option J3: Report both without designating either as the continuing role.
  - pro: Exposes all durable evidence without interpretation.
  - con: Leaves the requirement's central promise unmet, since no single continuing role is stated.

Recommended and accepted answer: Option J1. The live record for this very review reads `owner: requestor` with `expected_next_actor: reviewer` at `status: request-pending`, and the agent who must act is the reviewer. Under J2 the same record would report `requestor`, telling a returning reviewer that someone else is blocked.

## Instruction to add Q11 for lease freshness in the reported result

Add an eleventh question deciding whether the result carries lease information.

Suggested description: Q04 makes every nonterminal exchange active, which includes exchanges whose lease expired long ago. Must the result report lease freshness, and in what form?

Suggested options:

- Option K1: Report the durable `lease_renewed_at` timestamp and a derived freshness indication against the configured wait timeout.
  - pro: Distinguishes a live exchange from a long-abandoned one that is equally nonterminal.
  - pro: Supplies the fact `rvw_resume` needs to choose between renewing and reclaiming a lease.
  - con: The derived indication depends on a configured timeout that may change.
- Option K2: Report the raw `lease_renewed_at` timestamp only.
  - pro: Reports durable evidence without interpretation.
  - con: Makes every caller reimplement the freshness comparison.
- Option K3: Report no lease information.
  - pro: Keeps the result focused on identity and next action.
  - con: A ten-day-dead exchange and a live one are indistinguishable in the output.

Recommended and accepted answer: Option K1. This repository currently holds two live coordination records: this exchange at `2026-08-27T21:06:10+02:00`, and `specification/plan/v0.11.0/code-reviewer` at `2026-08-17T12:50:39+02:00`. Both are nonterminal, both are therefore active under Q04, and nothing in the current required fields would tell a returning human that one has been dead for ten days.

## Instruction to add Q12 for repository-root resolution

Add a twelfth question deciding how the command resolves which repository it inspects.

Suggested description: The command runs from the repository root and discovers exchanges from root-level coordination records. How is that root resolved, and what happens when the caller's working directory is elsewhere?

Suggested options:

- Option L1: Discover the root from the caller's working directory by default and accept an explicit override, requiring both entry points to report the same repository from the same working directory.
  - pro: Reports the repository the caller is actually standing in.
  - pro: Makes the parity requirement testable rather than assumed.
  - con: Requires the launcher to preserve the caller's working directory rather than changing to its own.
- Option L2: Always resolve the root from the command's own installed location.
  - pro: Behaves identically no matter where it is invoked from.
  - con: Reports the tooling repository rather than the caller's when the two differ.
- Option L3: Require an explicit repository argument.
  - pro: Removes all ambiguity about which repository is meant.
  - con: Contradicts the requirement that the command need no remembered arguments.

Recommended and accepted answer: Option L1. This is not hypothetical for this umbrella. The immediately preceding requirement shipped `commit-plan-check.bat` with a launcher that changed directory to its own location, so it reported the tooling repository's readiness rather than the caller's, and its delegation test could not detect the divergence because it only matched text in the batch file. `rvw_status` is the same shape of root launcher over the same kind of root-relative evidence.

## Instruction to correct the state vocabulary

Replace `awaiting-human-confirmation` with the implemented `convergence-gate` in the Q02 description and the Q04 option text. The umbrella's conceptual phrase can be mentioned once as its origin, but this requirement governs a command that reports the actual state string.

Expand the Q04 active-state enumeration to name the implemented nonterminal states rather than a partial paraphrase. `ArtifactState` defines `round-in-progress`, `request-pending`, `answer-publication-in-progress`, `transcript-repair-pending`, `answer-pending`, `convergence-gate`, `owning-action-pending`, `escalated`, `abandoned-mid-round`, `interrupted-answer-publication`, `interrupted-transcript-append`, `abandoned-request`, `abandoned-answer`, and `inconsistent`, with `idle` as the only non-active value.

Name `owning-action-pending` explicitly in the answer. The specification requestor instruction requires a later session observing that state to finish the authorized owning action without asking the human again, so a status result that omits it costs the returning agent the one fact that prevents a duplicate human gate.

Align acceptance criterion 8 with the same vocabulary, since it currently mixes conceptual and implemented names.

## Instruction to scope the conflicting-evidence rule in Q03

State in the Q03 answer that a differing `owner` and `expected_next_actor` is the expected shape of a healthy round and is not conflicting evidence. As written, the rule would send ordinary healthy exchanges to role `unknown`. Scope the conflict condition to genuine corruption, such as a state and artifact set that cannot both be true, or a record whose identity disagrees with its own envelope.

## Instruction to reference canonical paths in Q06

Add to the Q06 answer that status reports the protocol's own canonical artifact paths rather than reconstructing artifact names. The launcher already returns request, answer, coordination, tombstone, transcript, and transition-lock paths whether or not the files exist, and every role instruction in this umbrella forbids reconstructing nearby names.

## Instruction on what to leave unchanged

Keep the command contract, umbrella visibility rules, multiplicity outcomes, read-only guarantees, scope boundaries, and all eleven acceptance criteria. Keep every one of the nine existing recommended answers, which this review accepts as written apart from the corrections above. Do not add an exit-status question; the repository's settled zero, three, and two mapping is available to design without another feature-level decision.

### Final reviewer decision for feature-request review-status-command round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-08-27T21:28:40+02:00
- Exchange: specification/feature-request/v0.11.0/review-status-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.review-status-command.md
- Outcome: request

### Review identity for feature-request review-status-command (round 2)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/feature-request.v0.11.0.review-status-command.md
Review round: 2

### Requestor assessment for feature-request review-status-command (round 2)

Round one identified three missing feature decisions and four vocabulary or
evidence corrections. The requirement now derives the continuing role from
`expected_next_actor`, reports `owner` separately, reports lease timestamp and
freshness, and resolves the caller repository rather than the launcher's
installed location.

The active-state contract now enumerates every implemented nonterminal state,
including `convergence-gate` and `owning-action-pending`, with `idle` as the only
inactive value. Healthy differences between `owner` and `expected_next_actor`
are no longer described as conflicting evidence. Artifact reporting now uses
the protocol's canonical paths and records expected, present, missing, or
not-applicable status.

The twelve questions remain feature-level decisions with distinct options,
trade-offs, accepted recommendations, and answers. Round two should verify that
these changes fully resolve the reviewer instructions without introducing a
new ambiguity or prematurely prescribing implementation structure.

### Change summary for feature-request review-status-command (round 2)

- Added Q10 and accepted J1: continuing role comes from
  `expected_next_actor`; `owner` is reported separately.
- Added Q11 and accepted K1: expose `lease_renewed_at` plus freshness against
  the configured wait timeout.
- Added Q12 and accepted L1: resolve the repository from the caller's working
  directory by default, allow an explicit override, and require entry-point
  parity.
- Replaced the conceptual `awaiting-human-confirmation` term with the actual
  `convergence-gate` state.
- Enumerated all implemented nonterminal states and explicitly retained
  `owning-action-pending` as active.
- Scoped inconsistent-role handling to genuine corruption, not the healthy
  difference between owner and expected next actor.
- Required protocol-canonical artifact paths rather than reconstructed names.
- Aligned the command contract and all eleven acceptance criteria with those
  decisions.

### Writer response for feature-request review-status-command (round 2)

Writer response: I accept every round-one finding and applied each requested change. Q10, Q11,
and Q12 use the reviewer's accepted J1, K1, and L1 answers. Q02 and Q04 now use
the implemented state vocabulary; Q04 contains the complete nonterminal state
set and calls out `owning-action-pending`. Q03 explicitly treats differing
`owner` and `expected_next_actor` values as healthy. Q06 uses paths supplied by
the protocol itself. The main requirement and acceptance criteria carry the
same decisions.

There is no disagreement. Please assess the revised requirement for
consolidation readiness.

### Reviewer focus for feature-request review-status-command (round 2)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-08-27T21:33:13+02:00
- Exchange: specification/feature-request/v0.11.0/review-status-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.review-status-command.md
- Outcome: answer

### Reviewer assessment for feature-request review-status-command round 2

Every round-one item is applied, and applied correctly rather than nominally. I verified each against the current document, and I verified the one technical claim underlying my own request against the implementation rather than assuming it.

Confirmed applied:

- Q10 exists and accepts J1, deriving the continuing role from `expected_next_actor`, with reasoning that names the exact case I raised: a healthy `request-pending` exchange owned by the requestor while the reviewer must act next.
- Q11 exists and accepts K1, exposing `lease_renewed_at` with freshness against the configured wait timeout.
- Q12 exists and accepts L1, resolving the caller's repository with an explicit override and required entry-point parity.
- `awaiting-human-confirmation` is gone from the document entirely, with `convergence-gate` used throughout.
- The active-state contract now names every implemented nonterminal state, and `owning-action-pending` appears throughout rather than being folded into a paraphrase.
- Q03 now states that a healthy difference between `owner` and `expected_next_actor` does not trigger the inconsistent-role exception.
- Q06 now requires the protocol's canonical artifact paths rather than reconstructed names.
- The command contract and all eleven acceptance criteria carry the same decisions, including criterion 2's explicit refusal to resolve the repository from the launcher's installed location.

All three new questions follow the document's template: three materially distinct options each, honest pros and cons, a recommendation, and an accepted answer. All twelve questions have a BBQ section and an answer.

I checked the one thing in my own round-one request that could have been wrong. Q11's answer pins freshness to "the configured wait timeout", and I wanted to know whether lease expiry actually uses that value rather than a separate constant. It does: `_lease_is_current` in `tools/review_exchange_observer.py` computes expiry as `lease_renewed_at` plus `wait_timeout_seconds` from the configuration and compares it against the wall clock. The phrasing is exactly right.

That same reading corrects something in my round-one assessment, and I would rather fix it than let it stand. I wrote that a returning human would see two equally live exchanges with no way to tell one had been dead for ten days. That was too strong. Because lease currency feeds the classifier, an expired lease already changes the reported state, so the ten-day-old `specification/plan/v0.11.0/code-reviewer` record would surface as `abandoned-request` rather than `request-pending`. What the state does not convey is the degree of staleness, and that is what matters when choosing between reclaiming an exchange someone stepped away from minutes ago and treating one abandoned for ten days as recoverable. Q11 is still the right decision; my justification for it was imprecise.

The requirement now settles every decision an implementer needs. Twelve questions carry complete options, consequences, recommendations, and accepted answers. The body, the umbrella visibility rules, multiplicity outcomes, read-only guarantees, and acceptance criteria agree with those answers and with each other. Nothing reopens a settled earlier-phase choice, and nothing prescribes design or implementation structure: the questions decide what status must report and which durable evidence is authoritative, leaving module shape, output rendering, and status codes to design.

I ran the repository Markdown gate, which reports no finding for this requirement, its child draft, or the review transcript.

What remains is optional wording only, listed separately and carrying no implementation consequence. There is no disagreement between the roles in this exchange.

### Question verdicts for feature-request review-status-command round 2

## Round two verdict on Q01 through Q09

Unchanged and agreed. The round-one answers stand, and the two corrections I asked for inside them are present without altering any selected option.

Q02 now uses `convergence-gate` in place of a state name that does not exist, while keeping option B1 and its reasoning intact.

Q03 keeps option C1 and adds the boundary it needed: a healthy difference between `owner` and `expected_next_actor` does not trigger the exception. That sentence is what stops the rule from marking every healthy exchange `unknown`.

Q04 keeps option D1 and now enumerates the implemented nonterminal states rather than a partial paraphrase, with `owning-action-pending` named explicitly. That was the omission that would have cost a returning agent the one fact preventing a duplicate human gate.

Q06 keeps option F1 and now says status reports the protocol's canonical paths rather than reconstructing artifact names, which aligns it with every role instruction in this umbrella.

Q05, Q07, Q08 and Q09 are unchanged and remain correct. Q05 is still the strongest question in the set for distinguishing missing evidence from confirmed absence.

## Round two verdict on the new Q10

Agree with option J1 as accepted.

The question is correctly framed as a choice about which durable field is authoritative rather than about output shape, which keeps it at feature level. The options are genuinely distinct and the cons are accurate rather than strawmen: J2's con names the real failure, that an ordinary `request-pending` round would report the requestor while the reviewer is the blocked party.

The accepted answer's reasoning matches the live evidence I cited in round one, where a healthy record carries `owner: requestor` with `expected_next_actor: reviewer`. Reporting `owner` separately rather than discarding it is the right call, since it remains the field that governs lease ownership and reclaim eligibility.

## Round two verdict on the new Q11

Agree with option K1 as accepted.

I verified the technical basis rather than accepting the phrasing. `_lease_is_current` computes expiry as `lease_renewed_at` plus the configuration's `wait_timeout_seconds`, so "freshness against the configured wait timeout" names the real comparison rather than an approximation.

The option set is honest. K1's con correctly notes that the derived indication depends on a configured timeout that may change, which is a real cost and the reason for reporting the raw timestamp alongside it. K3's con is accurate as far as the raw output goes.

One nuance the answer could carry, and my round-one framing got slightly wrong. Because lease currency feeds the state classifier, an expired lease already shows up as an `abandoned-*` or `interrupted-*` state, so staleness is not entirely invisible today. What K1 adds is the degree of staleness, which is what separates an exchange someone stepped away from minutes ago from one abandoned for ten days. That distinction drives the reclaim decision in the following requirement, and it is a better justification than the one I originally gave.

## Round two verdict on the new Q12

Agree with option L1 as accepted.

The question settles root resolution without prescribing the mechanism, which is the correct altitude for a feature request: it requires the caller's repository, an explicit override, and entry-point parity, and leaves how the launcher achieves that to design.

L2's con is precise about the failure mode, and acceptance criterion 2 now states the same refusal in the requirement body rather than only inside the question. That pairing is what makes the decision testable rather than aspirational, which is exactly what was missing when the equivalent launcher shipped in the preceding requirement.

## Round two verdict on remaining question coverage

The set is complete. I looked specifically for decisions still left to implementer discretion and found none with implementation consequence. Role source, lease visibility, root resolution, active-state membership, artifact-path authority, umbrella authority, multiplicity, success semantics, and next-action shape are all settled with reasons recorded.

No question is missing, redundant, unclear, or outside scope, and none silently chooses a design or implementation structure.

### Convergence evidence for feature-request review-status-command round 2

Covered wording: These are optional and carry no implementation consequence. The requirement is implementable exactly as written if none is applied. I list them only because the round asks for better phrasing where it exists.

1. Q11's accepted answer justifies lease freshness by saying nonterminal status alone does not establish liveness. That is true but understates the case, because an expired lease already changes the reported state to an `abandoned-*` or `interrupted-*` value. The sharper justification is that the state says whether the lease has expired while the timestamp says by how much, and the reclaim decision in `review-resume-command` depends on the difference between minutes and days. Consider: "Accept this because the state alone says only that a lease has expired, while the timestamp and derived freshness say by how much, which is what separates a momentary interruption from long-abandoned work."

2. Acceptance criterion 8 now carries the cardinality rule and the complete active-state vocabulary in a single sentence, which is dense. Splitting it into two criteria, one for zero, one, and multiple without silent selection, and one for the active-state membership rule, would make each independently checkable during implementation review. The content is correct either way.

3. The contract bullet for artifact paths lists six path kinds and four presence values in one sentence. Naming the presence values as a short nested list under the bullet would make the completeness model easier to read without changing it.

4. Q12's description asks how the root is resolved "and what happens when the caller's working directory is elsewhere". The second clause is really the same question as the first, since L1, L2 and L3 differ precisely in that case. Trimming it to the first clause would tighten the question without losing anything.

None of these changes a decision, an option, an answer, a required field, or an acceptance criterion.

Convergence rationale: I recommend convergence because the three missing decisions from round one are settled at feature level with reasons recorded, the vocabulary now matches the protocol the command will report, and I could not find a new gap.

The round-one blockers were decisions an implementer would otherwise have made silently. Q10 settles which durable field establishes the continuing role, which was the requirement's central promise resting on an unstated mapping, and it settles it the way the live evidence demands. Q11 settles lease visibility, which is what separates a momentary interruption from long-abandoned work and what the following requirement needs to choose between renewing and reclaiming. Q12 settles root resolution, which the immediately preceding requirement got wrong in shipped code.

The corrections matter as much as the additions. A requirement that governs a command reporting protocol state cannot name states the protocol does not have, and it now names all fifteen implemented values with `idle` as the only inactive one. `owning-action-pending` is called out rather than absorbed into a paraphrase, which preserves the fact that stops a returning agent from re-asking a human who has already decided. Q03's new boundary prevents the no-guessing rule from firing on the ordinary healthy shape of a round.

I did three independent checks rather than confirming my own asks. I read `_lease_is_current` and confirmed lease expiry really is `lease_renewed_at` plus the configured `wait_timeout_seconds`, so Q11's phrasing names the actual comparison. I checked all three new questions for template compliance and found three distinct options, honest pros and cons, a recommendation, and an accepted answer in each. I ran the repository Markdown gate over the requirement, its child draft, and the transcript, which reports no finding.

That reading also corrected my own round-one reasoning, which I would rather record than quietly drop. I had claimed a returning human could not tell a ten-day-dead exchange from a live one. In fact the expired lease already changes the reported state, so the difference is visible in kind though not in degree. Q11 remains the right decision on the stronger justification, and the weaker one is noted in the covered wording.

What remains is four optional phrasing suggestions, none of which changes a decision, option, answer, required field, or acceptance criterion. That is wording-only by this exchange's standard, so another automated round would not improve the specification.

This recommendation is advisory. It does not authorize consolidation, and the human remains the only party who may choose `Consolidate` or `Revise and review again`.

### Writer instructions for feature-request review-status-command round 2

No substantive change is required. Do not open another revision cycle on my account.

If the human selects `Consolidate`, proceed with the canonical `consolidate-then-review-ask-questions` workflow on `docs/v0.11.0/feature-request.v0.11.0.review-status-command.md`. When consolidating:

- Carry every accepted answer for Q01 through Q12 into the decision record with its reason. Several reasons rest on facts about the running protocol that will not be re-derivable from the consolidated prose alone, in particular that the continuing role comes from `expected_next_actor` because a healthy `request-pending` round is owned by the requestor while the reviewer must act, and that lease expiry is `lease_renewed_at` plus the configured `wait_timeout_seconds`.
- Keep the complete implemented state vocabulary rather than compressing it back to a paraphrase, and keep `owning-action-pending` named. Its presence is what prevents a returning agent from re-asking a human who has already authorized the owning action.
- Keep Q03's sentence that a healthy difference between `owner` and `expected_next_actor` is not conflicting evidence. Without it the inconsistent-role rule fires on the ordinary case.
- Keep acceptance criterion 2's explicit refusal to resolve the repository from the launcher's installed location. That sentence is the testable half of Q12 and the direct lesson from the preceding requirement's shipped defect.

The four phrasing suggestions in the covered-wording input are optional. Apply any, all, or none before consolidation; none alters a decision.

If the human instead selects `Revise and review again`, treat the covered wording as the full scope of that round unless the human supplies guidance that adds to it.

One item to carry into design rather than act on now. Q08 deliberately leaves exit-status values open, and the repository already has a settled zero, three, and two mapping in `commit-plan-check` and the exchange launcher. Design can adopt it directly without reopening a feature-level question.

### Final reviewer decision for feature-request review-status-command round 2

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-2 -->

## Round 2 by human - human-confirmation

- Recorded: 2026-08-27T22:06:26+02:00
- Exchange: specification/feature-request/v0.11.0/review-status-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.review-status-command.md
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->
