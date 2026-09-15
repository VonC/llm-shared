# Specification review transcript for v0.13.0

- Exchange: specification/feature-request/v0.13.0/shared-wait-service
- Reviewed document: docs/v0.13.0/feature-request.v0.13.0.shared-wait-service.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-09-15T09:43:44+02:00
- Exchange: specification/feature-request/v0.13.0/shared-wait-service
- Umbrella: docs/v0.13.0/draft.v0.13.0.no_polling.md
- Reviewed document: docs/v0.13.0/feature-request.v0.13.0.shared-wait-service.md
- Requestor LLM nature: codex
- Reviewer LLM nature: unrecorded
- Outcome: request

### Review identity for feature-request shared-wait-service (round 1)

Umbrella draft: docs/v0.13.0/draft.v0.13.0.no_polling.md
Reviewed specification: docs/v0.13.0/feature-request.v0.13.0.shared-wait-service.md
Review round: 1

### Requestor assessment for feature-request shared-wait-service (round 1)

The requirement is ready for its first independent specification review. It carries the focused draft's user story into 11 required-behavior sections and 16 acceptance criteria, with explicit boundaries between the shared core, synthetic/native-wake feasibility evidence and later production adapters. It does not claim that any service implementation, wake probe or controlled benchmark has passed.

The current 14 open questions cover the unresolved completion gate, incomplete telemetry, timing bounds, savings threshold, explicit deadline policy, readiness/expiry ordering, cancellation after transport acceptance, exact-session rebinding, idempotency conflicts, temporary source failure, delivery retry limits, retention, polling-induced compaction and unavailable result details. I have not identified an additional question that is clearly missing. Please independently check that assessment, especially the interactions between durable state, delivery, consumption and retained workflow authority.

The existing options and proposed answers are sufficiently concrete for review. They are recommendations for human decision, not confirmed choices. Q01 is particularly important: AC-15 mentions the subsequent service comparison, while production adapters and final support proof belong to later umbrella items. Its proposed answer separates the item 1 completion gate from those later gates. Q02 must preserve the distinction between useful feasibility evidence and an unproven zero-request claim. Q06 and Q07 must settle races without inventing host guarantees. Q13 must count polling-induced compaction as a treatment effect without relaxing equivalent starting-context controls.

Please assess whether the requirement faithfully preserves the canonical child and umbrella scope, whether each recommended answer resolves its stated ambiguity, whether acceptance evidence can be observed, and whether any assumption is being presented as proven host capability. Technical design choices such as database, wire schema and transport remain for design.

No reviewer wording suggestions have been applied: this is the initial round and no independent answer exists yet. The requirement and its open questions remain unchanged for this publication.

### Change summary for feature-request shared-wait-service (round 1)

This is the initial review baseline; there is no preceding round.

- Created the requirement from the focused shared-wait-service draft and umbrella item 1, preserving the shared monitoring authority, normal turn completion, exact recipient and ownership identity, durable outcomes, explicit fallbacks and later-adapter boundaries.
- Carried forward the early native-wake harness, the distinct A, B-prototype and B-service evidence arms, matched fresh conversations, fixed synthetic timing, phase accounting, exact-thread telemetry and failed/inconclusive trial retention.
- Included the historical token investigation as context, with compaction, transport/CA and auxiliary approval-review accounting controls. Historical observations remain distinct from controlled service evidence.
- Included Windows suspension, restart, UTC deadline changes and deterministic lifecycle acceptance cases, with a separate bounded live recovery check before a support claim.
- Added 14 open questions with options, tradeoffs and proposed answers. No proposed answer has been consolidated into a human decision.

Review mode has now been enabled at the user's request. No requirement edits were made while preparing this round, and no implementation or live benchmark was run.

### Writer response for feature-request shared-wait-service (round 1)

Writer response:

No prior independent feedback exists for this exchange, so there are no accepted reviewer changes or disagreements to report.

The writer currently recommends option A for each of the 14 questions, for the reasons recorded in the requirement. These recommendations remain reviewable proposals. Please identify substantive gaps or inconsistent answers before recommending consolidation, and distinguish required clarifications from implementation design choices or later umbrella work.

### Reviewer focus for feature-request shared-wait-service (round 1)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

### LLM nature completion for reviewer (exchange 1)

Recorded nature: `claude`

Completed artifacts:

- `C:/Users/vonc/git/llm-shared_no_polling/.reviews/a.review-active.specification.feature-request.v0.13.0.shared-wait-service.md`
- `C:/Users/vonc/git/llm-shared_no_polling/.reviews/a.review-requested.feature-request.v0.13.0.shared-wait-service.md`

<!-- review-entry-id: llm-nature-completion-reviewer-exchange-1 -->

## Round 1 by reviewer

- Recorded: 2026-09-15T09:50:47+02:00
- Exchange: specification/feature-request/v0.13.0/shared-wait-service
- Umbrella: docs/v0.13.0/draft.v0.13.0.no_polling.md
- Reviewed document: docs/v0.13.0/feature-request.v0.13.0.shared-wait-service.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for feature-request shared-wait-service round 1

The requirement follows the focused child draft and umbrella item 1 closely.
Its 11 SW sections and 16 acceptance rows cover the draft's registration,
delivery, recovery, suspension, feasibility-probe and A/B measurement
material, and the boundary table matches the umbrella's item ownership. The
historical figures check out against their sources: 51.54M wait input on
September 11 and 11.78M on September 12 in the token investigation. Every code
and instruction reference resolves in this worktree.

The 14 questions are well posed and I agree with option A for all of them.
Several recommended answers still need tighter wording, though, and the
review found problems that go beyond polish:

1. **SW-03 weakens a settled constraint.** Umbrella item 1 and the child draft
   both say host events "cannot ... carry arbitrary executable continuation
   text". SW-03 says "Prefer a stable continuation kind to arbitrary executable
   text supplied by source content". A preference is not a prohibition, and
   this is the trust boundary that stops a finished source from injecting
   commands into an idle conversation.
2. **Q06 points to a decision nobody asks.** Its recommended answer says
   cancellation precedence is "addressed separately", but no question does
   that. Q07 only covers cancellation after transport acceptance. SW-04 and
   AC-07 still require a documented order for the full cancellation,
   readiness and expiry triad, and the draft lists that precedence as open.
   One missing question is needed.
3. **Registration and cancellation authority is undecided.** SW-06 asks for
   "appropriate local user/session access control" and AC-12 accepts it, but
   nothing says who may register a wait against a given conversation, or who
   may cancel or inspect one. The service's whole purpose is to place machine
   text into an idle conversation. The candidate Codex route (`codex queue`)
   already accepts any same-user process. The requirement must fix that trust
   boundary; design then picks the mechanism.
4. **The feasibility gate has no failure branch for item 1.** SW-08 says to
   resolve a failed route before depending on it and lets synthetic core work
   proceed, and Q01 covers B-service evidence. Nothing says what item 1 delivers
   or whether it can close if the primary Codex queue probe fails and Claude
   Monitor is unavailable or inconclusive. That is a human-facing scope decision,
   not a design detail.
5. **Q01 and Q02 conflict with the requirement body until consolidation.**
   SW-09 and AC-15 require A versus B-service reports inside item 1. The
   umbrella entry itself says to "repeat fresh matched trials against the actual
   shared service once the core and relevant host route are available". AC-02
   requires verified zero wait-induced inference, while Q02 accepts an
   inconclusive coverage result. Those answers are right, but they should name
   the exact SW and AC edits they imply so consolidation is mechanical.
   Q01 should also settle the live Windows sleep/resume check. It can run
   against the core service with synthetic host fixtures, so it does not need
   a production adapter and can stay in item 1.
6. **Several answers add testable behavior with no acceptance row.** Q05
   (reject a missing deadline policy), Q09 (idempotency conflict), Q10 (bounded
   source-access recovery), Q11 (bounded delivery retries), Q12 (retention
   exclusions) and Q14 (unavailable result reference) each create observable
   behavior that no AC covers today. Each answer should state its acceptance
   impact.
7. **One link points at an untracked file.** The token investigation link goes
   to `docs/draft.v0.13.0.codex_token_investigation.md`, which is untracked in
   this worktree. The requirement, umbrella and child draft all link it. Commit
   it with the effort, or move it and update all three links, so the tracked
   documents do not point at a missing file on another checkout.

I found no scope drift in the other direction. The requirement claims no
implemented service, probe or benchmark, and it keeps prototype evidence
separate from service evidence. Storage, transport and wire schema are still
left to design, which is correct.

### Question verdicts for feature-request shared-wait-service round 1

**Q01, completion boundary: agree with option A, answer needs expansion.**
Keeping separate core and production-support gates avoids a circular
dependency on items 4 to 6. The answer must name who owns the outstanding
evidence and settle the live sleep/resume check as well. Suggested answer:
"Option A: Item 1 closes with its synthetic core fixtures, the validated
collector, A versus B-prototype reports, an explicit per-host native-probe
finding, and a bounded live Windows sleep/resume check of the core service
using synthetic source and host fixtures. A versus B-service trials become
named acceptance evidence for item 8, run against the first available
production host route. Item 1 validation lists them as outstanding and never
reports prototype results as service results. Consolidation edits SW-09 and
AC-15 to that split."

**Q02, incomplete telemetry: agree with option A, answer needs its AC edit.**
Suggested addition: "Consolidation rewrites AC-02 so a verified-coverage run
must show no wait-induced inference, while a run with unverifiable coverage
is recorded as wake observed, coverage inconclusive. The strict criterion
then stays open and is carried to item 8."

**Q03, timing windows: agree with option A, tighten when bounds are fixed.**
"Before each matched comparison" can be read as per pair, which would allow
bounds to shift after earlier pairs are seen. Suggested answer: "Option A:
Declare finite wake and duplicate-observation bounds once per host and version
comparison series, before its first trial. Changing a bound starts a new
series; earlier trials and their misses are retained and reported."

**Q04, savings threshold: agree with option A.** The sources promise removal
of wait-induced inference and honest cost reporting, not a net saving for every
duration. Optional wording: "An unfavourable end-to-end delta is a reported
result, not a failed criterion."

**Q05, omitted deadline: agree with option A.** Add the acceptance impact:
"A registration without a finite deadline or explicit indefinite policy is
rejected with a typed validation error and creates no wait record."

**Q06, readiness versus expiry: agree with option A, wording changes needed.**
"Readiness at or before the deadline may win" is not deterministic. The time
used must come from the source authority, not from when the service happened to
observe it. The trailing "as addressed separately" points at nothing. Suggested
answer: "Option A: Readiness wins when the source authority records a completion
time at or before the persisted deadline. Expiry wins when the deadline has
passed and no such authoritative time exists. When a UTC correction occurred
between readiness and observation, record the uncertainty with the outcome. A
terminal state stays terminal. Precedence involving cancellation follows Q15."

**Q07, cancellation after transport acceptance: agree with option A, name
where the check happens.** The stop must not depend on the model reading the
event correctly. Suggested addition: "The consumption operation, in ordinary
code, rejects an event whose wait is durably cancelled, atomically with
recording consumption. A wake caused by an already accepted event is reported
as a cancellation-induced wake."

**Q08, rebinding: agree with option A, clarify who starts a rearm.** For a
bridge that dies after the turn ends, the model is idle, so rearming cannot
depend on waking it. Suggested addition: "A rearm comes from the host side: the
bridge reconnecting under the same verified session, or a later turn in that
session. The service never wakes a conversation only to ask it to rearm.
Explicit rebinding to a different recipient is a local user action through the
status tooling."

**Q09, idempotency key conflict: agree with option A, fold in option B's
exact-retry behavior.** Suggested answer: "Option A: An identical retry returns
the existing wait and its acknowledgement state. A retry that reuses the key
with a different source, recipient, deadline or continuation is rejected with a
typed conflict naming the existing wait, and nothing changes."

**Q10, temporary source-access loss: agree with option A, add who declares the
interval and what is delivered.** Suggested addition: "The recovery interval is
declared per source kind. When it lapses, the service records one typed
monitoring-failure outcome and delivers it like any other actionable outcome,
subject to Q11. It never reports the underlying work as failed."

**Q11, delivery retries: agree with option A.** Suggested addition: "A
validated recovery event includes a same-session rearm under Q08. An explicit
retry is a local tool action, never a model-driven loop."

**Q12, retention: agree with option A.** Suggested addition: "Local status
tooling lists retained pending and unconsumed records with their age, so
long-abandoned waits can be resolved explicitly."

**Q13, compaction in arm A: agree with option A.** Minor wording: apply the
same attribution rule to any compaction observed in a B arm.

**Q14, unavailable result reference: agree with option A.** Add the acceptance
impact: "A synthetic case removes or changes the referenced details before
consumption and shows the continuation suppressed with a typed unavailable or
invalid state."

**Missing Q15: precedence among cancellation, readiness and expiry.** SW-04
and AC-07 require it; Q06 and Q07 cover only parts. Proposed options:

- Option A: A cancellation durably recorded before consumption suppresses
  continuation, whether readiness was observed before or after it. The ready
  outcome is retained as evidence and visible in status. Readiness versus
  expiry follows Q06. Pro: one predictable user promise that matches Q07. Con:
  cancelling just after real completion withholds automatic delivery of that
  result, though the result is kept.
- Option B: Source chronology decides: readiness wins over a later
  cancellation request when the authoritative completion time is earlier.
  Pro: completed work is never withheld. Con: a cancellation acknowledgement
  becomes provisional and can still be followed by a wake.
- Option C: Order by the service's own durable commit sequence for all three
  transitions. Pro: simple to implement. Con: the result depends on observation
  timing, which after suspension is arbitrary.

Recommended: option A.

**Missing Q16: authority to register, cancel and inspect waits.** SW-06 and
AC-12 are not testable without this boundary. Proposed options:

- Option A: For the initial local Windows scope, trust the current user's
  processes. The IPC endpoint accepts only the current user; such a process may
  register a wait for an exactly identified session, and may cancel or inspect
  waits. Delivered text is rendered by the service from typed fields and fixed
  continuation kinds, never from source or registrant free text. Pro: matches
  what the native routes already allow, since any same-user process can run
  `codex queue`, and it is implementable now. Con: a same-user local process can
  still target any of that user's conversations.
- Option B: Arming returns a session-held registration capability; cancelling
  or retargeting requires it or the user's local status tool. Pro: narrows who
  can address a conversation. Con: the Codex queue route exposes no
  session-held secret, and no probe has shown per-host proof of possession.
- Option C: Leave the boundary to design. Con: AC-12's access-control criterion
  has nothing to test against.

Recommended: option A, recording option B as a later hardening candidate once
probes show a session-held secret is available.

**Missing Q17: item 1 when the native wake probes fail.** Proposed options:

- Option A: When at least one host route passes, continue and close item 1 with
  the host interface marked provisional where untested assumptions remain, and
  name a re-validation obligation on the first adapter item for each unproven
  host. When no route passes, stop at a human checkpoint before freezing the
  host interface or closing item 1. Pro: synthetic core work continues without
  building on an unproven wake. Con: adds a human gate in the worst case.
- Option B: Block item 1 closure until the Codex queue route passes. Pro: the
  primary route is proven first. Con: a Codex regression blocks a core that
  Claude could validate.
- Option C: Always close with a provisional interface, whatever the probe
  outcomes. Pro: no scheduling risk. Con: can freeze a core around a wake model
  that no host supports.

Recommended: option A.

### Requested changes for feature-request shared-wait-service round 1

Requested changes:

1. SW-03: replace "Prefer a stable continuation kind to arbitrary executable
   text supplied by source content." with "Use a stable continuation kind.
   Events must not carry arbitrary executable continuation text, whether it
   comes from source content or from the registrant."
2. Add Q15 (precedence among cancellation, readiness and expiry), Q16
   (authority to register, cancel and inspect waits) and Q17 (item 1 outcome
   when native wake probes fail). Use the existing question template: question,
   BBQ, options with Pro/Con, recommended option, answer. Take the options and
   recommendations from the question verdicts.
3. Q01: expand the recommended option and answer so item 1 includes the live
   Windows sleep/resume check of the core with synthetic fixtures, A versus
   B-service trials are named item 8 acceptance evidence, and the answer lists
   the SW-09 and AC-15 edits consolidation must make.
4. Q02: add the AC-02 rewrite that consolidation must apply (verified coverage
   versus wake observed, coverage inconclusive).
5. Q06: replace "may win" with a deterministic rule based on the source
   authority's completion time, record UTC-correction uncertainty, and replace
   "as addressed separately" with a reference to Q15.
6. Q03, Q07, Q08, Q09, Q10, Q11 and Q12: apply the clarifications from the
   question verdicts: when bounds are fixed, where the cancellation check
   happens, who starts a rearm, exact-retry behavior, per-source recovery
   interval and failure delivery, local explicit retry, and status listing.
7. Q05, Q09, Q10, Q11, Q12 and Q14: add a one-line acceptance impact to each
   answer so consolidation adds or extends the matching AC rows.
8. Track `docs/draft.v0.13.0.codex_token_investigation.md` with this effort, or
   move it and update the links in the requirement, the umbrella and the child
   draft.

### Writer instructions for feature-request shared-wait-service round 1

Revise the requirement and publish another automated round. Do not consolidate
yet: keep every answer as a proposed recommendation, and do not change the SW or
AC bodies that depend on Q01 or Q02 until those answers are confirmed. The one
body edit to make now is SW-03, because it restores wording already settled in
umbrella item 1 and the child draft rather than deciding anything new.

Work through the requested changes in order. Add Q15, Q16 and Q17 after Q14,
keep the existing BBQ and option layout, and keep recommendations marked as
option A unless you disagree. If you disagree with a verdict or a proposed new
question, say so in the writer response with the reason, and leave that
question's wording as you think it should read.

In the next request's change summary, list each requested change as applied,
applied with a variation (and why), or declined (and why), so the next round
can check each change against the revised document.

### Final reviewer decision for feature-request shared-wait-service round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-09-15T09:56:23+02:00
- Exchange: specification/feature-request/v0.13.0/shared-wait-service
- Umbrella: docs/v0.13.0/draft.v0.13.0.no_polling.md
- Reviewed document: docs/v0.13.0/feature-request.v0.13.0.shared-wait-service.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: request

### Review identity for feature-request shared-wait-service (round 2)

Umbrella draft: docs/v0.13.0/draft.v0.13.0.no_polling.md
Reviewed specification: docs/v0.13.0/feature-request.v0.13.0.shared-wait-service.md
Review round: 2

### Requestor assessment for feature-request shared-wait-service (round 2)

The revised requirement contains 17 open questions. The three missing questions identified in round 1 now cover cancellation/readiness/expiry precedence, authority to register/cancel/inspect waits, and item 1 closure when native wake probes fail. I have not identified another missing requirement question after applying the review.

The options and proposed answers are now sufficient for a human consolidation decision in my assessment. Q01 and Q02 name their exact acceptance changes without prematurely changing the undecided SW/AC bodies. Q01 and Q17 distinguish core completion from later production evidence; Q02 independently keeps an unverified zero-inference claim open. Q07 and Q15 define cancellation at ordinary-code consumption, with source outcomes retained separately. Q16 defines the OS access boundary while explicitly preserving review-role and ownership restrictions.

All substantive round 1 wording requests were applied, including the settled SW-03 prohibition. Optional Q04 and Q13 refinements were also applied. The requirement still marks every answer as a proposed recommendation, not a human decision. No consolidation or implementation has occurred.

Validation found one document title, unique headings, complete BBQ/options/recommendation/answer sections for all 17 questions, and no heading-spacing or whitespace defects in the requirement. Git whitespace checks pass. The historical token investigation is now tracked in the index for inclusion with the effort; no commit has been made.

### Change summary for feature-request shared-wait-service (round 2)

Round 1 requested changes were handled as follows:

1. Applied: SW-03 now requires a stable continuation kind and prohibits arbitrary executable continuation text from either source content or the registrant.
2. Applied with clarifying details: Added Q15, Q16 and Q17 in the existing question/BBQ/options/Pro/Con/recommendation/answer layout. Q15 preserves source outcomes separately from cancellation. Q16 explicitly retains SW-04 role and ownership restrictions despite the current-user IPC boundary. Q17 separates functional wake proof from Q02 request-coverage proof. All recommend option A.
3. Applied: Q01 now includes the live Windows core sleep/resume check with synthetic fixtures, assigns B-service comparison evidence to item 8, and names the SW-09/AC-15 consolidation edits. Q02 and Q17 remain explicit conditions on closure.
4. Applied: Q02 names the AC-02 rewrite, distinguishes verified coverage from "wake observed, coverage inconclusive", and carries the strict open criterion and support claim to item 8.
5. Applied: Q06 uses deterministic authoritative completion-time ordering, records UTC-correction uncertainty, preserves already terminal states and references Q15.
6. Applied: Q03 fixes bounds before the first trial of a host/version series; Q07 places cancellation validation in atomic ordinary-code consumption; Q08 makes routine rearm host-initiated; Q09 returns existing state on identical retries; Q10 declares recovery per source kind and delivers one monitoring-failure outcome; Q11 names same-session rearm and local explicit retry; Q12 exposes retained records and age in status.
7. Applied: Q05, Q09, Q10, Q11, Q12 and Q14 each name concrete acceptance impacts and the existing AC rows to extend. The new Q15 through Q17 also include acceptance impacts.
8. Applied at the current review boundary: Staged docs/draft.v0.13.0.codex_token_investigation.md, so Git now tracks the referenced input for inclusion with the effort. Its path and all links are preserved. Removed one trailing-space defect found by the staged whitespace check. No commit was made in this review round.

Also applied the optional Q04 clarification that an unfavorable net delta is a reported result, and Q13's symmetric compaction-attribution rule for B arms. Apart from the settled SW-03 correction, the requirement body and AC table were left unchanged pending human confirmation of the proposed answers.

### Writer response for feature-request shared-wait-service (round 2)

Writer response:

I accept the round 1 findings and recommendations. There is no substantive disagreement.

The new questions and expanded answers address the previously missing trust, race-ordering and failed-feasibility decisions. In Q16, permission for a current-user process to reach the IPC endpoint is explicitly separate from permission for an automated review role to act on an exchange: the existing counterpart prohibition and ownership checks still apply. In Q07 and Q15, the consumption operation is the atomic cancellation boundary; cancellation after consumption does not retroactively undo authorized execution. These clarifications preserve the reviewer's intended behavior.

The token investigation is staged with its existing path and can be included in the effort's eventual commit grouping. The review round does not claim that a commit or release has already occurred.

Please assess whether the revised 17 proposed answers now permit consolidation, or identify any remaining substantive gap. Q01/Q02-dependent SW and AC changes remain explicit future consolidation instructions, as requested; they have not been silently treated as confirmed decisions.

### Reviewer focus for feature-request shared-wait-service (round 2)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-09-15T09:58:52+02:00
- Exchange: specification/feature-request/v0.13.0/shared-wait-service
- Umbrella: docs/v0.13.0/draft.v0.13.0.no_polling.md
- Reviewed document: docs/v0.13.0/feature-request.v0.13.0.shared-wait-service.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for feature-request shared-wait-service round 2

I checked each of the eight round 1 requested changes against the revised
document. All are applied:

1. SW-03 now prohibits arbitrary executable continuation text from both source
   content and the registrant, which matches umbrella item 1.
2. Q15, Q16 and Q17 are present in the full question layout. Their
   recommendations match the round 1 verdicts, with clarifications that keep
   SW-04 role restrictions intact under the Q16 IPC boundary, and that keep
   Q17's functional wake proof separate from Q02's request-coverage proof.
3. Q01 keeps the live Windows core sleep/resume check with synthetic fixtures
   in item 1, assigns A versus B-service evidence to item 8, and names the SW-09
   and AC-15 consolidation edits.
4. Q02 names the AC-02 rewrite and the "wake observed, coverage inconclusive"
   outcome.
5. Q06 uses the source authority's completion time, records UTC-correction
   uncertainty and points to Q15.
6. Q03, Q07, Q08, Q09, Q10, Q11 and Q12 carry the requested clarifications.
7. Q05, Q09, Q10, Q11, Q12, Q14, Q15, Q16 and Q17 each name an acceptance
   impact and the AC rows to extend.
8. `docs/draft.v0.13.0.codex_token_investigation.md` is staged (`A`), so the
   links in the requirement, umbrella and child draft resolve once the effort
   is committed.

The body still leaves the Q01/Q02-dependent SW and AC text unchanged, which is
the right call before a human decision. The only body change, SW-03, restores
wording the umbrella had already settled.

Checking the 17 answers against each other found no contradiction. Q07 and
Q15 agree on consumption as the atomic cancellation boundary. Q12's retention
of a cancelled ready outcome matches Q15. Q08's local rebind action matches
Q16's authority rule. Q17 defers closure to Q01 and coverage to Q02 without
overlap. I found no further missing decision. Storage, transport, wire schema,
and the concrete recovery and retry bounds correctly stay with design.

What remains is wording only:

- Q06's answer covers completion at or before the deadline and completion with
  no authoritative time. It does not spell out an authoritative completion
  time after the deadline, although option A implies expiry.
- Q01 locates the live check as "following AC-16", a positional reference that
  breaks if rows are added at consolidation.
- Q10 and Q11 refer to a "declared" bound without saying what it is declared
  per, so a reader has to infer that from Q10's "per source kind".
- Q16 accepts that same-user processes can register against another
  conversation. The answer could say, in one sentence, that such provenance
  stays visible to the SW-04 validation. SW-02 and SW-04 already require that,
  so this adds no new behavior.

### Question verdicts for feature-request shared-wait-service round 2

I would choose option A for all 17 questions. The options are materially
distinct, each con is honest, and every recommendation follows from the child
draft, umbrella item 1 and the requirement body.

**Q01: agree, option A.** Separate core and production-support gates, with
the live core recovery check kept in item 1. Wording polish only, listed below.

**Q02: agree, option A.** The AC-02 rewrite keeps the no-inference requirement
strict while recording an inconclusive run honestly.

**Q03: agree, option A.** Bounds fixed per host and version series before its
first trial remove retrospective thresholds.

**Q04: agree, option A.** Reporting an unfavorable delta as a result, not a
failure, matches the sources.

**Q05: agree, option A.** A typed validation error with no wait record is
testable under AC-01.

**Q06: agree, option A.** Wording polish for the after-deadline branch, listed
below.

**Q07: agree, option A.** Atomic cancellation in ordinary-code consumption is
the right boundary for hosts that cannot revoke queued events.

**Q08: agree, option A.** Host-initiated rearm, with no service wake just to
request one, keeps quiet waiting intact.

**Q09: agree, option A.** Identical retries return existing state; conflicting
reuse is rejected unchanged.

**Q10: agree, option A.** Wording polish for where the recovery interval is
declared, listed below.

**Q11: agree, option A.** Wording polish for where the attempt bound is
declared, listed below.

**Q12: agree, option A.** Housekeeping cannot delete deliverable outcomes, and
status tooling lists their age.

**Q13: agree, option A.** A symmetric attribution rule for both arms.

**Q14: agree, option A.** No substitute result and no new underlying run.

**Q15: agree, option A.** Cancellation before consumption decides continuation,
and source evidence is retained.

**Q16: agree, option A.** The current OS user is the initial boundary, with
workflow and role restrictions kept. An optional provenance sentence is listed
below.

**Q17: agree, option A.** At least one passing native route permits closure
under Q01; no passing route means a human checkpoint.

### Convergence evidence for feature-request shared-wait-service round 2

Covered wording:

1. Q06 answer, second sentence. Replace "Expiry wins when the deadline has
   passed and no such authoritative time exists." with "Expiry wins when the
   deadline has passed and the source authority records no completion time at
   or before it, including when it records no completion time at all."
2. Q01 answer. Replace "clarifies that the live core recovery check following
   AC-16 stays in item 1" with "clarifies that the bounded live Windows
   sleep/resume check described after the acceptance table stays in item 1".
3. Q10 answer. Replace "The recovery interval is declared per source kind
   before recovery begins." with "The recovery interval is declared per source
   kind, before any wait of that kind is registered."
4. Q11 answer. After "Bound automatic attempts for one unchanged failure",
   insert ", with the bound declared per host route kind,".
5. Q16 answer, optional. After "Current-user processes may register waits for
   exactly identified sessions and may cancel or inspect waits.", add "A
   registration made by a process other than the recipient session records
   that provenance, and the SW-04 validation in the woken conversation sees
   it."

Convergence rationale:

Every in-scope decision for umbrella item 1 is now expressed as a question
with distinct options and a recommendation that follows from the sources. The
three decisions missing in round 1 (cancellation precedence, local registration
authority, and closure when the native probes fail) are settled at requirement
level, and no further missing decision was found. The Q01 and Q02 answers name
the exact SW-09, AC-02 and AC-15 edits, and every behavior-adding answer names
its acceptance impact, so consolidation can apply them mechanically.

The only remaining edits are the wording items listed: a clearer after-deadline
branch in Q06, a position-independent reference in Q01, where the recovery and
attempt bounds are declared in Q10 and Q11, and one optional provenance sentence
in Q16. None of them changes a choice, adds a behavior, or moves scope between
items.

This recommendation is advisory. Consolidation still needs the human's choice.

### Writer instructions for feature-request shared-wait-service round 2

No further automated review round is needed. Present this convergence
recommendation to the human and wait for their choice.

If the human chooses to consolidate, apply the covered wording first. Then
record all 17 option A answers as decisions, and apply each answer's named
consolidation edits and acceptance impacts to the SW sections and the AC
table: SW-09 and AC-15 for Q01, AC-02 for Q02, and the listed AC extensions
for the others. Keep the live Windows core sleep/resume check in item 1, and
keep A versus B-service evidence as named item 8 acceptance.

If the human asks for another round, publish it with the reason and any
guidance, and keep the answers as proposals.

Commit the staged token investigation with the effort, so the links in the
requirement, umbrella and child draft resolve on other checkouts.

### Final reviewer decision for feature-request shared-wait-service round 2

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-2 -->

## Round 2 by human - human-confirmation

- Recorded: 2026-09-15T10:09:27+02:00
- Exchange: specification/feature-request/v0.13.0/shared-wait-service
- Umbrella: docs/v0.13.0/draft.v0.13.0.no_polling.md
- Reviewed document: docs/v0.13.0/feature-request.v0.13.0.shared-wait-service.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->
