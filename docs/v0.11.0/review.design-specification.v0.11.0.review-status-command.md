# Specification review transcript for v0.11.0

- Exchange: specification/design-specification/v0.11.0/review-status-command
- Reviewed document: docs/v0.11.0/design.v0.11.0.review-status-command.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-08-27T22:25:06+02:00
- Exchange: specification/design-specification/v0.11.0/review-status-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/design.v0.11.0.review-status-command.md
- Outcome: request

### Review identity for design-specification review-status-command (round 1)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/design.v0.11.0.review-status-command.md
Review round: 1

### Requestor assessment for design-specification review-status-command (round 1)

The v0.11.0 design maps the consolidated review-status requirement onto the
existing exchange observer, state classifier, coordination model, canonical
path derivation, and caller-root precedent. It defines repository-wide
discovery, normalized human and JSON results, role and lease semantics,
artifact completeness, action identity, process outcomes, and a strict
read-only trust boundary.

Ten design questions cover the remaining choices: candidate filename scope,
healthy/damaged schema discrimination, portable path representation,
convergence human-turn role mapping, exact lease evidence, semantic next-action
identity, artifact record shape, deterministic ordering, numeric process
statuses, and consistency when files change during observation.

Each question stays at design level and includes three distinct options,
trade-offs, a recommendation, and an accepted answer. The reviewer should
check for conflicts between the state-aware requestor mapping and the normal
`expected_next_actor` rule, verify that damaged evidence remains visible
without becoming trusted identity, and identify any missing design choice that
would otherwise be left to implementation.

### Change summary for design-specification review-status-command (round 1)

- Added the v0.11.0 review-status design beside the settled requirement.
- Grounded the design in the existing observer, state classifier, coordination
  record, canonical path derivation, lease configuration, and root-resolution
  precedent.
- Defined discovery, normalized result, rendering, trustworthiness, and
  read-only boundaries.
- Added ten answered design questions covering the unresolved interfaces and
  data-flow choices.

### Writer response for design-specification review-status-command (round 1)

Writer response: This is the initial design-review round. There is no earlier reviewer feedback
to accept or dispute. The design preserves every settled requirement decision,
including explicit requestor/reviewer identity, exact umbrella visibility,
complete nonterminal state coverage, canonical paths, lease freshness,
caller-root resolution, and partial diagnostics.

Please identify missing design decisions, incompatible choices, weak option
trade-offs, or wording that crosses into file-by-file implementation planning.

### Reviewer focus for design-specification review-status-command (round 1)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

## Round 1 by human - escalation

- Recorded: 2026-08-28T08:42:30+02:00
- Exchange: specification/design-specification/v0.11.0/review-status-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/design.v0.11.0.review-status-command.md
- Outcome: escalation

wait timed out while answer was absent

<!-- review-entry-id: escalation-round-1 -->

## Round 1 by human - human-reclaim

- Recorded: 2026-08-28T10:17:30+02:00
- Exchange: specification/design-specification/v0.11.0/review-status-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/design.v0.11.0.review-status-command.md
- Outcome: human-reclaim

Human decision to resume design-specification round 1 after an overnight wait timeout.

The recorded escalation was a stopped handoff rather than a failure. The requestor published round 1 at 2026-08-27T22:25:06+02:00 and entered its bounded wait. No reviewer session was active overnight, so the wait reached the configured 18000-second timeout with the answer still absent and the protocol recorded an escalation with the diagnostic that the wait timed out while the answer was absent.

No review work was lost and no artifact was damaged. At the moment of this decision the request is present at 4704 bytes with an envelope naming round 1 and role requestor, the answer is absent because no reviewer answer was ever published, and the versioned transcript is present at 3884 bytes. That is the intact escalated shape the forced resume requires, and the artifact shape names the reviewer as the actor to resume.

The human reviewed this evidence and directed that the exchange resume in place at the same round rather than being resolved or archived. The reviewer then continues its normal round-one assessment and publishes the paired answer through the shared exchange.

This case is also a live example of the interruption class that umbrella requirements 9 and 10 exist to address. A returning agent had to reconstruct the exchange identity, round, and responsible role from durable files, which is what the review-status command is specified to report and what the review-resume command is specified to restore without a manual forced reclaim.

<!-- review-entry-id: human-reclaim-round-1 -->

## Round 1 by reviewer

- Recorded: 2026-08-28T10:22:06+02:00
- Exchange: specification/design-specification/v0.11.0/review-status-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/design.v0.11.0.review-status-command.md
- Outcome: answer

### Reviewer assessment for design-specification review-status-command round 1

This is a strong design. It maps every settled requirement decision onto machinery that already exists, its confirmed technical facts are accurate, and nine of its ten questions are sound. One question contains a defect that would misreport the single situation this command is most likely to be run for, and that is the substance of this round.

I verified all five confirmed technical facts against the code rather than accepting them. The observer does read without mutation and delegate to the pure state table. `derive_artifact_paths` does return the six canonical paths from a validated context. The coordination record does carry the context, policy, `owner`, `expected_next_actor`, round, lease timestamp, confirmation fields, and incomplete-transition evidence. Lease expiry is `lease_renewed_at` plus `ReviewConfiguration.wait_timeout_seconds` against an injected wall clock. And the caller-root precedent is stated correctly, which matters because that precedent exists only because the equivalent launcher shipped the opposite behavior two requirements ago and had to be fixed in code review.

The requestor asked me specifically to check for conflicts between the state-aware requestor mapping and the normal next-actor rule. There is one, and it is not the one the question anticipates.

`Actor.HUMAN` is written to `expected_next_actor` in exactly two places in the protocol. One is the convergence gate, where the record becomes `AWAITING_HUMAN_CONFIRMATION` with `owner` set to reviewer and the lease cleared. The other is escalation, where the record becomes `ESCALATED` with the lease also cleared. Design Q04 accepts option D1 and describes the convergence gate as the only human-turn mapping, instructing that a human next actor in any unsupported state be treated as inconsistent. Applied to the protocol as implemented, that rule reports every escalated exchange as inconsistent with role `unknown`.

That contradicts the design's own text in two places. The active-state list includes escalated, and the next-action vocabulary already contains a value for resolving an escalation. So the design expects escalated exchanges to appear with a meaningful next action while its role resolver would refuse to identify them.

This exchange is itself the proof. This design review escalated last night when the requestor's bounded wait timed out with no reviewer answer present, and that escalation set a human next actor. Had `rvw_status` existed as designed, running it this morning to find out what had happened would have reported role `unknown` and an inconsistent exchange, rather than an escalated review awaiting human resolution. Diagnosing exactly that interruption is the reason umbrella row 9 exists.

Two smaller defects follow from the same area.

The design body and Q05 disagree about lease evidence. The lease-freshness section says the derived block reports the category "together with elapsed or overdue seconds when calculable", which is option E2's content. Q05 accepts option E1, whose stated con is that consumers calculate elapsed or overdue duration themselves. Both cannot stand, and an implementer reading the body would build something the accepted answer rejects.

The freshness category also conflates two unlike situations. Because the lease is deliberately cleared at both the convergence gate and escalation, a healthy human-turn exchange reports `missing` under E1's three-value vocabulary, indistinguishable from a damaged record whose lease evidence is genuinely absent. The requirement's Q11 exists to expose degree of staleness, and degree is undefined for states that legitimately hold no lease.

Two further points are worth recording without blocking.

The acceptance table has eleven scenarios and none of them exercises an escalated exchange. That absence is why the role-mapping defect survived the writer's own review, and adding the case is what would keep it fixed.

The convergence-gate row states the requestor continuing role but not what `owner` shows. The record sets `owner` to reviewer there, so status will display role requestor beside owner reviewer. That pairing is correct and surprising, and since the requirement mandates reporting owner separately, the design should say so rather than leave an implementer to discover it.

Everything else holds up well. Discovery, normalization, rendering, the read-only trust boundary, and the process-status mapping are all coherent, and Q09 adopts the repository's existing zero, three, and two convention rather than inventing another. Q01 through Q03 and Q06 through Q10 are well-formed with materially distinct options and honest trade-offs, and I accept each of their answers. No question crosses into file-by-file implementation planning, and none reopens a settled requirement decision.

### Question verdicts for design-specification review-status-command round 1

## Verdict on Q01 discovery filename scope

Agree with option A1, admit malformed coordination filenames as damaged candidates rather than filtering them out.

The reasoning is right and the con is honest. Filtering unparseable names would make a repository with unreadable review evidence look clean, which is the failure this command exists to prevent. It also pairs correctly with Q02's separation of damaged entries from trusted identity.

## Verdict on Q02 healthy and damaged entries in one schema

Agree with option B1, one ordered collection with damaged entries kept structurally distinct from trusted identity.

The key property is that an untrusted candidate never populates identity fields that a consumer would read as authoritative. B1 achieves that while still giving machine callers a single result to iterate, which is what `rvw_resume` will need.

## Verdict on Q03 portable paths and repository identity

Agree with option C1, repository-relative fields resolved against one reported root.

Correct, and the reason given is the important one: baking an absolute checkout location into exchange identity would make the result non-portable and would tie durable identity to one workstation. Reporting the resolved root once and everything else relative to it is the right shape, and it composes with Q12 of the requirement.

## Verdict on Q04 the convergence human turn

Agree with the direction of option D1 and with rejecting D2 and D3, but the answer as written is incomplete and must not be accepted unchanged.

D2 is correctly rejected because it would turn `owner` into an undocumented general fallback, and D3 correctly rejected because it would discard the confirmed requestor identity at convergence.

The defect is in the scope of the exception rather than the choice. The answer describes the convergence gate as the only human-turn mapping and directs that a human next actor in any unsupported state be treated as inconsistent. The protocol writes a human next actor in two places, not one: the convergence gate, and escalation. Every escalated exchange would therefore be reported as inconsistent with role `unknown`, even though the design's own active-state list includes escalated and its own next-action vocabulary already contains a value for resolving an escalation.

The correction is small and does not disturb the chosen option. Extend the state-aware resolver to cover both supported human-turn states, and say what each maps to. For the convergence gate, requestor, because the requestor resumes after the decision. For escalation, the agent the artifact shape names, which is a rule the protocol already implements when a human forcibly resumes a stopped handoff and hands the round back to the actor its artifacts identify. A human next actor in any state other than those two remains inconsistent, which preserves the guard the answer was reaching for.

The convergence-gate mapping should also record what `owner` shows, because the record sets it to reviewer while the role is requestor.

## Verdict on Q05 lease-freshness evidence

Agree with option E1, fixed timestamps plus the configured timeout and a category.

The parking-ticket analogy earns its place, and the reasoning is right that a per-second counter makes snapshots noisy while fixed timestamps let any consumer reproduce the decision. E3 is correctly rejected for hiding degree, which is exactly what the requirement's Q11 was added to expose.

Two things must be fixed around it.

The design body contradicts this answer. Its lease-freshness section says the derived block reports the category "together with elapsed or overdue seconds when calculable", which is option E2's content and precisely what E1's con says consumers compute themselves. Align the body to E1, or change the answer; they cannot both stand.

The category set needs to distinguish a deliberately cleared lease from missing evidence. The lease is set to none on purpose at both the convergence gate and escalation, so a healthy human-turn exchange currently reports `missing`, identical to a damaged record that lost its lease. Either add a distinct value for a state that legitimately holds no lease, or state explicitly that `missing` is the expected value in those two states and is only a defect elsewhere.

## Verdict on Q06 next-action identity

Agree with option F1, a closed semantic vocabulary independent of display text.

The reason given is the right one: the later resume feature needs a durable routing fact rather than a string tied to today's launcher names. This is the design-level counterpart of the requirement's Q09 and keeps the two representations from drifting.

## Verdict on Q07 artifact completeness shape

Agree with option G1, keyed records over a closed set of canonical artifact kinds.

Keyed access makes an expected-but-missing artifact unambiguous, which a positional or list shape would blur. It also composes with the requirement's Q06 rule that paths come from the protocol rather than from reconstructed names.

## Verdict on Q08 entry ordering

Agree with option H1, deterministic identity order.

Correct, and the reasoning is the part I would keep verbatim: ordering by identity avoids embedding a debatable urgency policy inside a diagnostic. Anything resembling severity ordering belongs to a consumer, not to discovery.

## Verdict on Q09 process-status mapping

Agree with option I1, zero for a trustworthy answer, three for completed but untrustworthy, two for inability to answer.

This adopts the convention already used by the commit-plan checker and the exchange launcher rather than inventing a third scheme, which is what I hoped for when I deliberately left exit codes out of the feature-level questions. The three-way split also matches the requirement's Q08 distinction between cardinality and trustworthiness.

## Verdict on Q10 files changing during a status read

Agree with option J1, detect a mixed snapshot and report it rather than retrying through a mutating path.

The important property is that the command cannot take the transition lock or otherwise mutate state to obtain a clean read, so surfacing the race as evidence is the only option consistent with the read-only boundary. The answer states that plainly.

## Verdict on overall question coverage

The ten questions are the right ten, and I found no missing design decision. Nine answers are acceptable as written. Q04 needs its exception widened to the two states the protocol actually uses, and Q05 needs the body reconciled and its category set clarified. Neither requires a different option to be chosen.

### Requested changes for design-specification review-status-command round 1

Requested changes:

1. Widen Q04's state-aware resolver to cover both states in which the protocol writes a human next actor, keeping option D1: `convergence-gate` maps to `requestor`, `escalated` maps to the agent the artifact shape names, and any other human next actor remains inconsistent.
2. Update the Q04 description so it no longer implies the convergence gate is the only state recording a human next actor.
3. State in the Q04 answer and the convergence acceptance row that `owner` shows `reviewer` at that gate while the continuing role is `requestor`.
4. Reconcile the lease-freshness section of the design body with Q05's accepted option E1, removing the elapsed-or-overdue-seconds claim or changing the accepted answer.
5. Distinguish a deliberately cleared lease from missing lease evidence, either with a fourth category or by stating that `missing` is expected at `convergence-gate` and `escalated` and is a defect signal only elsewhere.
6. Add an escalated exchange to the acceptance table, reporting its state, artifact-shape continuing role, resolve-escalation next action, and lease category at overall status `3`.
7. Consider a second acceptance row for an exchange escalated by a timed-out wait, which is the shape this review itself produced.

### Writer instructions for design-specification review-status-command round 1

## Instruction to widen the human-turn mapping in Q04

Keep option D1 as the chosen option. Correct its scope so the state-aware resolver covers both states in which the protocol writes a human next actor, rather than only the convergence gate.

Rewrite the recommendation and answer so they say that agent-valued next actors map directly, and that a human next actor is valid in exactly two states. At `convergence-gate` the continuing role is `requestor`, because the requestor resumes by consuming the human decision. At `escalated` the continuing role is the agent the artifact shape names, which is the rule the protocol already applies when a human forcibly resumes a stopped handoff and returns the round to the actor its artifacts identify. A human next actor in any other state remains inconsistent, which keeps the guard the current answer was reaching for.

Record why this matters in the answer rather than only in the option text. An escalated exchange is the most likely reason a caller runs this command at all, and under the current wording every one of them would report role `unknown`.

Update the Q04 description too. It currently says the convergence gate "records a human next actor while the requirement says the continuing agent is the requestor", which reads as though that were the only such state.

## Instruction to state the convergence-gate owner value

Add to the Q04 answer, and to the convergence row of the acceptance table, that `owner` shows `reviewer` at that gate while the continuing role is `requestor`. The protocol sets ownership to the reviewer when it records the gate. The pairing is correct and counterintuitive, and since the requirement mandates reporting owner separately, an implementer should not have to discover it from a coordination record.

## Instruction to reconcile the lease body with Q05

The lease-freshness section of the design body says the derived block reports the category "together with elapsed or overdue seconds when calculable". That is option E2's content, and Q05 accepts option E1 whose con explicitly leaves that calculation to consumers.

Align the body to E1: report the renewal timestamp, the derived expiry timestamp, the evaluation timestamp, the configured timeout, and the category, and say that elapsed or overdue duration is derivable by consumers from those fixed values. If you prefer E2 instead, change the answer rather than leaving the two in conflict.

## Instruction to separate a cleared lease from missing lease evidence

The protocol deliberately clears `lease_renewed_at` at both the convergence gate and escalation, so under E1's three categories a healthy human-turn exchange reports `missing`, identical to a damaged record whose lease evidence is genuinely absent.

Either add a fourth category for a state that legitimately holds no lease, or state explicitly in Q05 and in the lease-freshness section that `missing` is the expected value at `convergence-gate` and `escalated`, and is a defect signal only in states that should hold a live lease. The first is cleaner for machine consumers; the second is a smaller change. Either resolves it.

## Instruction to add escalated acceptance coverage

The acceptance table has eleven scenarios and none of them exercises an escalated exchange, which is why the Q04 scope defect survived. Add at least one row: an escalated exchange reports its escalated state, the continuing role from the artifact shape, a resolve-escalation next action, and a lease category consistent with the cleared lease, at overall status `3`.

Consider adding a second row for an exchange escalated by a timed-out wait specifically, since that is the shape this very review produced last night and the one a returning caller is most likely to meet.

## Instruction on what to leave unchanged

Keep the confirmed technical facts, which I verified against the code and found accurate. Keep the discovery and normalization boundaries, the read-only trust boundary, the human report structure, and the process-status mapping. Keep every one of the existing answers to Q01, Q02, Q03, Q06, Q07, Q08, Q09, and Q10, which this review accepts as written. Keep Q09's adoption of the repository's existing zero, three, and two convention rather than introducing a new one.

### Final reviewer decision for design-specification review-status-command round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-08-28T10:31:19+02:00
- Exchange: specification/design-specification/v0.11.0/review-status-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/design.v0.11.0.review-status-command.md
- Outcome: request

### Review identity for design-specification review-status-command (round 2)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/design.v0.11.0.review-status-command.md
Review round: 2

### Requestor assessment for design-specification review-status-command (round 2)

Round one accepted nine questions and found one connected defect around valid
human turns and deliberately cleared leases. The design now recognizes both
`convergence-gate` and `escalated` as valid human-next-actor states. Convergence
reports requestor as continuing role beside reviewer as owner; escalation uses
the agent named by the artifact shape.

Lease evidence now follows Q05 option E1 consistently: renewal, expiry, and
evaluation timestamps plus the configured timeout and a four-way category.
`not-held` represents the protocol's deliberate lease clearing at human turns,
while `missing` remains damaged evidence where a lease should exist. No elapsed
or overdue counter is reported.

The acceptance table now covers convergence ownership, a general escalation,
and the timed-out-wait escalation exercised by this review. Round two should
verify that these changes resolve every requested correction without altering
the nine already accepted design answers.

### Change summary for design-specification review-status-command (round 2)

- Widened Q04 and the role resolver to both valid human-next-actor states.
- Defined convergence as continuing requestor with reviewer owner, and
  escalation as the artifact-shape agent awaiting human resolution.
- Reconciled the lease body with Q05 option E1 and added `not-held` to separate
  deliberate lease clearing from missing evidence.
- Added acceptance coverage for convergence ownership, escalation, and a wait
  timeout escalation.
- Left Q01 through Q03 and Q06 through Q10 unchanged as requested.

### Human guidance and writer response for design-specification review-status-command (round 2)

Human guidance:

Human decision to resume design-specification round 1 after an overnight wait timeout.

The recorded escalation was a stopped handoff rather than a failure. The requestor published round 1 at 2026-08-27T22:25:06+02:00 and entered its bounded wait. No reviewer session was active overnight, so the wait reached the configured 18000-second timeout with the answer still absent and the protocol recorded an escalation with the diagnostic that the wait timed out while the answer was absent.

No review work was lost and no artifact was damaged. At the moment of this decision the request is present at 4704 bytes with an envelope naming round 1 and role requestor, the answer is absent because no reviewer answer was ever published, and the versioned transcript is present at 3884 bytes. That is the intact escalated shape the forced resume requires, and the artifact shape names the reviewer as the actor to resume.

The human reviewed this evidence and directed that the exchange resume in place at the same round rather than being resolved or archived. The reviewer then continues its normal round-one assessment and publishes the paired answer through the shared exchange.

This case is also a live example of the interruption class that umbrella requirements 9 and 10 exist to address. A returning agent had to reconstruct the exchange identity, round, and responsible role from durable files, which is what the review-status command is specified to report and what the review-resume command is specified to restore without a manual forced reclaim.

Writer response: I accept every round-one finding. Q04 now covers convergence and escalation as
the two valid human-next-actor states and records the convergence owner/role
pair. Q05 and the design body now use fixed timestamps and a distinct
`not-held` category, with no elapsed counter. The acceptance cases exercise
both escalation generally and the timed-out-wait shape from this exchange.

There is no disagreement. Please assess the revised design for consolidation
readiness.

### Reviewer focus for design-specification review-status-command (round 2)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-08-28T10:35:40+02:00
- Exchange: specification/design-specification/v0.11.0/review-status-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/design.v0.11.0.review-status-command.md
- Outcome: answer

### Reviewer assessment for design-specification review-status-command round 2

Every round-one correction is applied, and applied at the root rather than patched over. I verified each against the current document.

The human-turn mapping now covers both states the protocol actually uses. The continuing-agent section names `convergence-gate` and `escalated` as the two intentional human-next-actor states, maps the first to `requestor` with owner `reviewer`, maps the second to the agent named by the artifact shape with a human escalation-resolution next action, and retains the guard that a human next actor in any other state is inconsistent. The Q04 answer carries the same rule and states the reason plainly: reporting `unknown` at `escalated` would hide the interruption this command exists to diagnose.

The lease evidence is now internally consistent. The body no longer claims to report elapsed or overdue seconds; it reports the renewal, expiry, and evaluation timestamps with the configured timeout, and says consumers derive duration from those fixed values. That matches Q05 option E1 exactly, and the two remaining mentions of elapsed or overdue duration are inside the option text where they belong.

The category conflation is resolved with the cleaner of the two routes I offered. A fourth value, `not-held`, now represents the protocol's deliberate lease clearing at the two human-turn states, while `missing` is reserved for a state that should carry lease evidence and does not. That distinction is worth keeping precisely because it is invisible until someone reads the code that clears the lease.

Acceptance coverage now exercises the gap that let the defect through. Three rows were added: convergence with its requestor role beside reviewer owner and a `not-held` lease, a general escalated exchange at overall status three, and a wait-timeout escalation whose expected outcome is the original request retained with an artifact-shape reviewer role. That last row is this exchange's own shape, which is the right thing to encode as a permanent test rather than a one-time anecdote.

The nine previously accepted answers are unchanged, and all ten questions still carry a BBQ section and an answer.

One observation belongs in this round even though it is not a defect in the reviewed design, because it is red right now and the writer will meet it.

The repository Markdown gate reports no finding against this design document, but it does fail on a different file: `docs/v0.11.0/review.feature-request.v0.11.0.review-status-command.md` at line 186, MD032, a list block needing a blank line before it. The cause is the label-inlining renderer defect deferred through the whole commit-plan-check effort. My round-one requested-changes input for the feature request was a properly formed ordered list, and `tools/spec_review_answer.py` inlined it after its `Requested changes: ` label so the first item landed on the label line. That file is committed and clean in the working tree, so the gate is red on committed history.

This is the recurrence I predicted when the defect was recorded rather than fixed, and it is the second transcript it has damaged. It is outside this design's scope and outside my authority to repair, and it does not affect whether this design is ready to consolidate. It does mean the next `ghog day` will fail at its check phase until someone either repairs that line or fixes the four renderer call sites, and umbrella rows 9 and 10 are no longer blocked by any collision that justified deferring it.

Everything else holds. The design settles every decision an implementer needs, its confirmed technical facts remain accurate against the code, and nothing crosses into file-by-file implementation planning. What remains on this document is two optional wording items, listed separately, neither of which changes a decision.

There is no disagreement between the roles in this exchange.

### Question verdicts for design-specification review-status-command round 2

## Round two verdict on Q01 through Q03 and Q06 through Q10

Unchanged and agreed. These eight answers were accepted in round one, I asked for no change to them, and none was made.

Q09's adoption of the repository's existing zero, three, and two convention remains the right call, and the escalation rows added this round exercise the status-three branch with a concrete case rather than leaving it theoretical.

## Round two verdict on Q04 the human-turn mapping

Agree with option D1 as now written. The scope defect is fixed.

The answer now names both states the protocol writes a human next actor into, maps each explicitly, and keeps the inconsistency guard for every other state. The convergence mapping records the counterintuitive pairing of continuing role `requestor` beside owner `reviewer`, which is what the coordination record actually holds and what an implementer would otherwise have had to discover for themselves.

The escalation mapping is the part I care most about, and its reasoning is right: the artifact shape identifies who resumes after human resolution, which is the same rule the protocol already applies when a human forcibly resumes a stopped handoff. Reporting `unknown` there would have hidden exactly the interruption this command exists to surface.

Two residues of the single-state version survive in the option text. The BBQ analogy still explains only the convergence case, ending with the paused match as `convergence-gate`, and option D2's con still refers to "the one confirmed state" although there are now two. Neither changes the decision; both are listed as optional wording.

## Round two verdict on Q05 lease-freshness evidence

Agree with option E1 as now written, with the added fourth category.

The body and the answer no longer contradict each other. The design reports fixed timestamps and the configured timeout and leaves duration to consumers, which is E1's contract rather than E2's.

Adding `not-held` was the better of the two routes I offered, and I want to record why rather than just endorsing it. A three-value vocabulary would have forced a healthy convergence or escalated exchange to report `missing`, the same value a corrupt record produces, so the one field a consumer would use to judge trustworthiness would have been ambiguous exactly where trust matters. The four-value set keeps deliberate clearing and absent evidence separable without adding a counter that changes every second.

The option text for E1 still lists three categories, since the fourth was introduced after the options were written. That is a wording point rather than a conflict, because the answer and body agree on four; it is listed as optional wording.

## Round two verdict on remaining question coverage

The set remains the right ten and is complete. I looked again for a design decision left to implementation and found none. Discovery scope, schema discrimination, path portability, role mapping, lease evidence, action identity, artifact shape, ordering, process status, and snapshot consistency are all settled with reasons recorded.

No question is missing, redundant, unclear, or outside scope, and none prescribes file-by-file implementation structure.

### Convergence evidence for design-specification review-status-command round 2

Covered wording: These are optional and carry no implementation consequence. The design is implementable exactly as written if none is applied.

1. Q04's BBQ analogy still explains only the convergence case, ending with the paused match as `convergence-gate`, although the question now covers two states. Extending it would keep the analogy carrying the whole decision, for example by adding that an abandoned match also has a designated official who resumes once the dispute is settled.

2. Q04's option D2 con still says ownership would become a fallback "beyond the one confirmed state". There are now two confirmed states, so "beyond the two confirmed states" matches the answer.

3. Q05's option E1 text still lists three categories, because `not-held` was introduced after the options were written. The answer and the design body both use four. Listing all four in the option keeps the option and its answer describing the same contract.

4. The Q04 description opens by saying most continuing roles come from `expected_next_actor` "but both `convergence-gate` and `escalated` record a human next actor while the requirement says the continuing agent is the requestor". The final clause is now only true of convergence, since escalation maps to the artifact-shape agent rather than to the requestor. Splitting it would remove the remaining ambiguity.

None of these changes a decision, an option choice, an answer, an acceptance case, or a required field.

Convergence rationale: I recommend convergence because the round-one defect is fixed at its cause, the two consequences that followed from it are resolved, and the gap that let it survive is now closed by a permanent test rather than by a promise.

The blocker was a scope error rather than a wrong choice, and it was corrected without changing the chosen option. The role resolver now covers both states in which the protocol writes a human next actor, maps each explicitly, and keeps the guard for every other state. The escalated mapping in particular now says what happens instead of refusing to answer, and the answer records why: reporting `unknown` there would hide the interruption the command exists to diagnose.

The lease work is better than the minimum I asked for. The body was reconciled to the accepted option rather than the answer being loosened to match the body, and the conflation between a deliberately cleared lease and absent evidence was resolved with a distinct `not-held` value rather than a footnote. That keeps the field a consumer uses to judge trustworthiness unambiguous in exactly the states where trust is hardest.

Acceptance coverage is what turns this from a fix into a guarantee. The table now exercises convergence ownership, a general escalation, and the wait-timeout escalation this exchange itself produced. Encoding that last shape as a test is the difference between having survived one interruption and being able to diagnose the next one.

I verified rather than accepted. I re-read the continuing-agent mapping, the lease section, the Q04 and Q05 answers, and the acceptance table against the current document; confirmed the elapsed-or-overdue claim survives only inside option text where it belongs; confirmed all ten questions still carry a BBQ section and an answer; and confirmed the eight untouched answers were left alone as requested. I also ran the repository Markdown gate, which reports no finding against this design document.

That gate did surface one failure elsewhere, and I reported it in the assessment rather than letting it pass. A committed feature-request transcript now fails MD032 because the label-inlining renderer defect flattened my round-one requested-changes list onto its label line. It is outside this design's scope and outside my authority to repair, it does not bear on whether this design is ready, and it is the recurrence I predicted when that defect was deferred rather than fixed. The human should know the repository gate is red from it before the next implementation round begins.

What remains on this document is four optional phrasing items, all residues of the single-state version of Q04 and Q05, none of which changes a decision, option, answer, acceptance case, or required field. That is wording-only by this exchange's standard, so another automated round would not improve the design.

This recommendation is advisory. It does not authorize consolidation, and the human remains the only party who may choose `Consolidate` or `Revise and review again`.

### Human guidance response for design-specification review-status-command round 2

Human guidance: Human decision to resume design-specification round 1 after an overnight wait timeout.

The recorded escalation was a stopped handoff rather than a failure. The requestor published round 1 at 2026-08-27T22:25:06+02:00 and entered its bounded wait. No reviewer session was active overnight, so the wait reached the configured 18000-second timeout with the answer still absent and the protocol recorded an escalation with the diagnostic that the wait timed out while the answer was absent.

No review work was lost and no artifact was damaged. At the moment of this decision the request is present at 4704 bytes with an envelope naming round 1 and role requestor, the answer is absent because no reviewer answer was ever published, and the versioned transcript is present at 3884 bytes. That is the intact escalated shape the forced resume requires, and the artifact shape names the reviewer as the actor to resume.

The human reviewed this evidence and directed that the exchange resume in place at the same round rather than being resolved or archived. The reviewer then continues its normal round-one assessment and publishes the paired answer through the shared exchange.

This case is also a live example of the interruption class that umbrella requirements 9 and 10 exist to address. A returning agent had to reconstruct the exchange identity, round, and responsible role from durable files, which is what the review-status command is specified to report and what the review-resume command is specified to restore without a manual forced reclaim.

Guidance response: The guidance carried into this round is the summary recorded when the human authorized the forced resume of round one, and it is accurate as evidence.

It informed this review in one specific way. It confirmed that the escalation was a stopped handoff rather than a failure, that no artifact was damaged, and that the artifact shape named the reviewer as the actor to resume. That let me pick up round one as an ordinary round rather than treating the exchange as unsafe, and I assessed the design on its merits without giving the interruption any weight it had not earned.

It did not override anything, and I want to be explicit that it could not have. Guidance cannot change exchange identity, the current document's authority, or the disposition rules, and nothing in it asked to. The reclaim restored the same round and the same identity, and the digest I assessed is the current document's own bytes.

One part of the guidance turned out to be directly useful to the review rather than only to the recovery. It observed that a returning agent had to reconstruct the exchange identity, round, and responsible role from durable files, which is what this very command is specified to report. That made the escalated-state role mapping a concrete question rather than an abstract one, and it is why round one could show that the original Q04 rule would have reported this exchange as inconsistent with role `unknown` at the exact moment someone ran the command to understand what had happened.

The writer has since encoded that shape as a permanent acceptance case rather than leaving it as an anecdote, which is the right outcome. The guidance also anticipated that the resume command should make a manual forced reclaim unnecessary in this situation, and nothing in this design contradicts that; the status result it defines carries the state, artifact-shape role, resolve-escalation action, and lease category that such a resume would need.

### Writer instructions for design-specification review-status-command round 2

No substantive change is required. Do not open another revision cycle on my account.

If the human selects `Consolidate`, proceed with the canonical `consolidate-then-review-ask-questions` workflow on `docs/v0.11.0/design.v0.11.0.review-status-command.md`. When consolidating:

- Carry every accepted answer for Q01 through Q10 into the decision record with its reason. Two reasons rest on facts about the running protocol that will not be re-derivable from consolidated prose: that `expected_next_actor` is written as `human` in exactly two places, the convergence gate and escalation, and that the lease is deliberately cleared in both.
- Keep the continuing-agent mapping's full sentence naming both human-turn states. Compressing it back to the convergence case would reintroduce the round-one defect, which would then report every escalated exchange as inconsistent.
- Keep the `not-held` category and its definition. Without it, a healthy convergence or escalated exchange reports the same lease value as a corrupt record.
- Keep the three added acceptance rows, especially the wait-timeout escalation. It encodes a real interruption this effort actually experienced, and it is what would catch a future regression in the role mapping.

The four phrasing suggestions in the covered-wording input are optional residues of the single-state version of Q04 and Q05. Apply any, all, or none before consolidation; none alters a decision.

One item to hand on rather than act on inside this effort. The repository Markdown gate is currently failing on `docs/v0.11.0/review.feature-request.v0.11.0.review-status-command.md` at line 186, MD032, because the label-inlining renderer defect flattened an ordered list onto its `Requested changes: ` label line. That file is committed, so the next `ghog day` will stop at its check phase. The cause is the four call sites in `tools/spec_review_answer.py`, `tools/spec_review_request.py`, `tools/code_review_request.py`, and `tools/code_review_answer.py`, with the correct idiom already present at `tools/code_review_answer.py:288`. This is the second transcript that defect has damaged, and nothing in the current umbrella schedule now collides with fixing it.

If the human instead selects `Revise and review again`, treat the covered wording as the full scope of that round unless the human supplies guidance that adds to it.

### Final reviewer decision for design-specification review-status-command round 2

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-2 -->

## Round 2 by human - human-confirmation

- Recorded: 2026-08-28T23:31:55+02:00
- Exchange: specification/design-specification/v0.11.0/review-status-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/design.v0.11.0.review-status-command.md
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->
