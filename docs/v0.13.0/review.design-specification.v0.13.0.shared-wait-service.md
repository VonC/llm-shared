# Specification review transcript for v0.13.0

- Exchange: specification/design-specification/v0.13.0/shared-wait-service
- Reviewed document: docs/v0.13.0/design.v0.13.0.shared-wait-service.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-09-15T10:49:18+02:00
- Exchange: specification/design-specification/v0.13.0/shared-wait-service
- Umbrella: docs/v0.13.0/draft.v0.13.0.no_polling.md
- Reviewed document: docs/v0.13.0/design.v0.13.0.shared-wait-service.md
- Requestor LLM nature: codex
- Reviewer LLM nature: unrecorded
- Outcome: request

### Review identity for design-specification shared-wait-service (round 1)

Umbrella draft: docs/v0.13.0/draft.v0.13.0.no_polling.md
Reviewed specification: docs/v0.13.0/design.v0.13.0.shared-wait-service.md
Review round: 1

### Requestor assessment for design-specification shared-wait-service (round 1)

The initial design maps the consolidated requirement to a per-user Windows
authority, named-pipe transport, transactional state, source/host/workflow ports,
stable event and consumption identities, bounded recovery and a standalone
measurement pipeline. Existing-code facts are distinguished from proposed
architecture and unproven native-host bindings.

Twelve design questions cover lifecycle, transport, storage, failed arming,
cross-store ownership fencing, crash-gap recovery, source timing, retry bounds,
retention, admission limits, host lifecycle semantics and delayed telemetry.
Each has options, tradeoffs and a proposed answer. I have not identified another
uncovered design choice that prevents this first review, but the cross-store
fence and host callback ordering merit particular scrutiny. These are design
questions; the 17 consolidated requirement decisions are not reopened.

The options and answers are sufficient to propose the initial architecture,
subject to independent review. Q07 intentionally combines capability validation
before finite registration with bounded recovery for later evidence loss.
No earlier design-review wording suggestions exist. No implementation, native
probe, request-coverage result or service acceptance is claimed.

### Change summary for design-specification shared-wait-service (round 1)

Created the initial design beside the consolidated requirement. It records
inspected code authorities, service ownership and IPC, persistence boundaries,
registration/arming, source reconciliation, deadline ordering, cancellation and
consumption, retry/retention/admission policies, host feasibility gates, collector
design and acceptance mapping. Added twelve design questions through oqm.

Checked one H1, unique headings, twelve complete question/answer blocks, local
links, LF line endings and whitespace. Technical references for named-pipe
access and SQLite transactions use primary documentation. No executable code
or production adapter was changed for this design.

### Writer response for design-specification shared-wait-service (round 1)

Writer response:

This is design round 1 following human-authorized requirement consolidation.
The requirement exchange is completed and its final commit is f1816b8.
The design preserves the prototype/service evidence boundary, at-least-one
functional-route closure gate, separate strict request-coverage obligation,
atomic cancellation semantics and existing review-role isolation.

Please assess the design and its proposed answers independently, especially
deadlock/crash behavior at the workflow/service boundary, incomplete source-time
evidence, the distinction between functional arming and strict support evidence,
and recovery after consumption with an unconfirmed external effect. Assess
whether additional design questions are needed. There is no prior design
feedback or disagreement to resolve.

### Reviewer focus for design-specification shared-wait-service (round 1)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

### LLM nature completion for reviewer (exchange 1)

Recorded nature: `claude`

Completed artifacts:

- `C:/Users/vonc/git/llm-shared_no_polling/.reviews/a.review-active.specification.design-specification.v0.13.0.shared-wait-service.md`
- `C:/Users/vonc/git/llm-shared_no_polling/.reviews/a.review-requested.design-specification.v0.13.0.shared-wait-service.md`

<!-- review-entry-id: llm-nature-completion-reviewer-exchange-1 -->

## Round 1 by reviewer

- Recorded: 2026-09-15T10:53:56+02:00
- Exchange: specification/design-specification/v0.13.0/shared-wait-service
- Umbrella: docs/v0.13.0/draft.v0.13.0.no_polling.md
- Reviewed document: docs/v0.13.0/design.v0.13.0.shared-wait-service.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for design-specification shared-wait-service round 1

The design maps the consolidated requirement faithfully in most places. It
keeps the prototype and service arms apart, uses the at-least-one-route closure
gate, keeps strict request coverage separate from functional wake, applies
cancellation before consumption in every ordering, and keeps review-role
isolation. The repository facts it cites check out: `watchdog` and Python 3.13
in `pyproject.toml`, subscribe-before-scan with a timed rescan fallback in
`tools/review_resume_notifications.py`, the Groundhog status file carrying a pid
but no run UUID, and `CREATE_NO_WINDOW` detached launch in
`tools/groundhog/status.py`. The 12 questions are relevant, and I agree with the
direction of 10 of them as written.

Seven problems need more than wording:

1. **Q07 contradicts the confirmed deadline rule and is stricter than the
   evidence needs.** SW-05 and AC-09 say that after the deadline the wait
   expires "when no authoritative completion at or before it exists, including
   when completion is absent or is timestamped later". Q07 instead turns a
   ready source with no completion timestamp into unknown, then a monitoring
   failure, and rejects finite registration for kinds without timestamps. It
   also treats two cases as one. An authoritative read that shows readiness at
   service UTC at or before the deadline already bounds completion to at or
   before the deadline, because completion cannot follow the read that
   observed it. Only readiness first observed after the deadline needs a
   source timestamp; without one, SW-05 says expire. A source that cannot be
   read at all is a separate case: unknown, then Q10-style recovery, then
   monitoring failure, as SW-06 says. With this rule, timestamp-less source
   kinds can take finite deadlines, so the registration-time rejection is no
   longer needed.
2. **Clients never verify the named-pipe server.** The design has the service
   check its client, but the pipe name is a digest of the user SID, so another
   local user can predict it and create it first. A victim client would then
   send registrations to, and a host bridge would take events from, a
   foreign-user server. AC-08 requires foreign-user IPC to be refused in both
   directions. The service should create the first instance with
   `FILE_FLAG_FIRST_PIPE_INSTANCE` and report a squatted name as a typed
   conflict. Every client should confirm that the server process's token user
   SID equals its own before sending a frame.
3. **One fixed state home and pipe name per user blocks isolated instances.**
   Several llm-shared checkouts already coexist on this machine: the main
   checkout and this `no_polling` worktree, each with its own Python
   environment. A development build, or a test that starts a real service,
   would find the user's live authority. It would either get
   `schema-incompatible`, or create a newer schema that the stable build then
   refuses. The design needs an explicit state-home override for development
   and tests, with the pipe name derived from the SID plus the canonical state
   home, so each home has exactly one authority. This is a missing design
   question.
4. **Nothing says what happens when normal-turn-end evidence cannot be
   observed.** Dispatch requires "verified turn-ended lifecycle evidence" from
   the bridge. Nothing establishes that the Codex queue route exposes an
   ordinary-code signal for the exact registering turn, and a Claude Monitor
   command bridge cannot see turn boundaries by itself. With no such signal, an
   armed event is never dispatched. A host queue that already defers delivery
   until idle may make the service-side gate unnecessary, but then Stop or
   Cancel no longer blocks delivery. The design must decide whether turn-end
   evidence is a per-route capability, and how a route without it is
   classified. This is a missing design question, and it bounds what the
   Codex-first probe must record.
5. **Q06 handles a routine bridge crash as manual resolution.** On a
   consume-before-wake route, the most likely crash lands between committed
   authorization and the native wake. The design calls that
   `execution-unresolved` pending explicit local resolution, so a bridge
   restart would strand the conversation instead of waking it. The native wake
   is not an arbitrary external effect. The woken turn's first action is a
   consume by consumption UUID, which is idempotent, so re-delivering the wake
   under the same consumption UUID is safe when there is no turn-start
   evidence. It shows up only as a reported duplicate wake, which SW-03
   already allows. `execution-unresolved` should cover workflow effects after
   that check, not the wake itself.
6. **A consume timeout under the Q05 lock leaves authorization undefined.** The
   adapter holds the workflow transition lock through "bounded IPC". If its
   wait times out, it releases the lock without knowing whether the service
   committed. The service may still commit after ownership has moved, which
   leaves an authorization bound to a stale generation; a new owner is then
   refused with "already consumed". The consume request needs a
   service-enforced commit budget, measured on the service's monotonic clock
   from receipt and shorter than the client's timeout, so a late commit is
   impossible. The adapter can then treat a timeout as not authorized.
7. **Offline status can write the store outside the singleton lock.** Offline
   status reads the SQLite store directly while the service is down. In
   rollback-journal mode, the first reader after a crash rolls back a hot
   journal, which is a write, and that would happen outside the singleton lock
   that is supposed to own recovery. Offline status should take the singleton
   lock without blocking before it opens the store, and use IPC when the lock
   is held.

Smaller points:

- Q07's recommendation reads "Option A with capability validation", which is
  neither listed option.
- The acceptance map has no row for startup races, stale discovery,
  lock-holder crash, or a hidden launch surviving parent exit, all of which
  AC-12 covers.
- The phase table's A-arm setup boundary, "corresponding declared setup
  events", is not a boundary.

Nothing here reopens a confirmed requirement decision. Finding 1 and the
proposed Q07 options apply SW-05 as written.

### Question verdicts for design-specification shared-wait-service round 1

**Q01, startup: agree, option A.** On-demand start with explicit stop fits the
initial local scope. Sleep keeps the process; a reboot closes the TUIs, which
are outside initial support anyway.

**Q02, IPC transport: agree with option A, answer needs the server check.**
Suggested answer: "Use a named pipe with an explicit user-only security
descriptor, created with `FILE_FLAG_FIRST_PIPE_INSTANCE`. A squatted name is a
typed conflict. Every client verifies that the server process's token user SID
equals its own before sending any frame. Default pipe permissions never stand
in for this policy. Transport stays behind a port."

**Q03, storage: agree, option A.** Rollback journaling with full
synchronization and short, bounded reads. Add to the body that offline status
takes the singleton lock without blocking before it opens the store, because a
hot-journal rollback is a write.

**Q04, failed preparation: agree, option A.** Keeping typed non-armed
preparation under the same wait ID preserves early outcomes and idempotency.

**Q05, workflow authority across the fence: agree with option A, add a
commit budget.** Suggested addition: "Each consume request carries a commit
budget. The service measures it on its monotonic clock from receipt and
refuses to commit authorization once it lapses. The adapter's IPC timeout
exceeds that budget by a declared margin, so an adapter timeout always means
not authorized. The service never needs the workflow lock, and no source
worker holds the store write lock while it waits for a workflow lock."

**Q06, crash gap: agree with option A, separate the wake from workflow
effects.** Suggested addition: "On a route that consumes before waking, an
authorization with no turn-start evidence for its native wake is re-deliverable
under the same consumption UUID. The woken turn's first action re-validates by
that UUID, so a repeat wake is reported as a duplicate wake and never repeats
consumed work. `execution-unresolved` applies only to workflow effects after
that check."

**Q07, incomplete source timing: disagree with the current answer; replace the
options.** The current option A contradicts SW-05's expiry rule for missing
completion evidence. Suggested options:

- Option A: An authoritative read that shows readiness at service UTC at or
  before the deadline decides readiness, recording any UTC-correction
  uncertainty. Readiness first observed after the deadline wins only with a
  source completion time at or before it; otherwise the wait expires, as SW-05
  says. An unreadable source stays unknown within its source-kind recovery
  interval, then yields monitoring failure. Timestamp-less source kinds may
  take finite deadlines.
  - Pro: follows SW-05 exactly and uses the evidence the service already holds.
  - Con: a source completed on time but first observed late, for example
    across suspension, expires when it has no timestamp.
- Option B: Reject finite registration for source kinds without comparable
  completion timestamps, and handle runtime timestamp loss as monitoring
  failure.
  - Pro: every finite decision rests on a source timestamp.
  - Con: excludes simple sources the observation bound already covers, and
    runtime monitoring failure contradicts SW-05's expiry rule.

Recommended: option A.

**Q08, policy bounds: agree, option A.** Per-kind versioned policies with the
synthetic defaults. The 30-second reconciliation ceiling is well below the
240-second fixture, which keeps wake latency measurable.

**Q09, tombstones: agree, option A.** Tombstones without automatic expiry keep
delayed-retry idempotency; explicit purge states its consequence.

**Q10, admission limits: agree, option A.** Count limits with bounded frames,
no eviction, and recovery operations kept available.

**Q11, host lifecycle ports: agree, option A.** Keep the ports provisional.
Normal-turn-end observability is a separate decision, proposed as Q13 below.

**Q12, collector finalization: agree, option A.** A finite drain bound with
versioned amendments.

**Missing Q13: dispatch when normal-turn-end evidence is not observable.**
Proposed options:

- Option A: Treat turn-end evidence as a per-route capability. A route with
  ordinary-code evidence for the exact registering turn gates dispatch on it. A
  route without it may dispatch only into a host queue that already defers
  delivery until the conversation is idle and that the probe shows does not
  deliver after Stop, Cancel or interruption. That route records "host-gated
  turn end" instead of verified evidence. Any other route is
  `retained-result-only`.
  - Pro: does not exclude a native idle queue for lack of a service-side
    signal, and keeps the Stop/Cancel boundary testable.
  - Con: adds a capability dimension and a probe case per host.
- Option B: Always require verified service-side turn-end evidence before
  dispatch.
  - Pro: one uniform gate.
  - Con: may leave the Codex queue route with no dispatch path, even if it
    wakes correctly.
- Option C: Dispatch as soon as the route is armed and rely on host queue
  semantics everywhere.
  - Pro: simplest dispatch.
  - Con: can deliver after Stop or Cancel, or mid-turn, on a host whose queue
    does not defer.

Recommended: option A, with the Codex-first probe recording which evidence
kind the queue route provides.

**Missing Q14: isolated state homes for development and tests.** Proposed
options:

- Option A: Keep `%LOCALAPPDATA%/llm-shared/wait-service` as the default. Allow
  an explicit state-home override for development and tests, and derive the
  pipe name from the user SID plus the canonical state-home identity, so each
  home has one authority and status names its home.
  - Pro: dev builds and service-level tests cannot touch the user's live
    authority or migrate its schema.
  - Con: clients must resolve the same home to find a service; a stray
    override can start an unnoticed second authority.
- Option B: One home and one pipe per user; tests use in-process transports
  only.
  - Pro: exactly one authority per user.
  - Con: no live service test or dev build can run beside the user's service,
    and a dev schema change blocks the stable build.

Recommended: option A, with the override shown in `hello`, discovery and status.

### Requested changes for design-specification shared-wait-service round 1

Requested changes:

1. Replace Q07's options, recommendation and answer with the version in the
   question verdicts. Then update "Finite deadlines, suspension and UTC changes"
   to match: remove "Reject finite registration for a source kind known to
   lack comparable authoritative completion timing", add the rule that an
   authoritative read at or before the deadline decides readiness, and keep
   access loss as unknown, recovery, then monitoring failure.
2. In "Windows named pipe with explicit user access", add
   `FILE_FLAG_FIRST_PIPE_INSTANCE`, the typed squatting conflict, and client-side
   verification of the server process's token user SID before any frame. Update
   Q02's answer to match.
3. Add Q14 (isolated state homes for development and tests). If option A is
   kept, update "One process per OS user and machine" and the pipe-naming
   paragraph so the pipe name derives from the user SID plus the canonical state
   home, and so `hello`, discovery and status name the home.
4. Add Q13 (dispatch when normal-turn-end evidence is not observable). Update
   "Preparing a registration without losing early completion", the flow note
   after the sequence diagram, and "Port contract before a production host
   binding" to show turn-end evidence as a per-route capability. Add the evidence
   kind to what the Codex and Claude probes record.
5. Extend Q06's answer and "Workflow receipt and the crash gap": an authorized
   consumption with no turn-start evidence for its native wake is re-deliverable
   under the same consumption UUID, and `execution-unresolved` covers only
   workflow effects after the woken turn's consume check.
6. Extend Q05's answer and "The atomic cancellation fence" with the
   service-enforced commit budget, the client timeout margin, and the rule that
   the service never takes a workflow lock and no source worker holds the store
   write lock while waiting for one.
7. In "Status, retention and operational bounds", require offline status to take
   the singleton lock without blocking before opening the store, and to use IPC
   when the lock is held.
8. Add an acceptance-map row for concurrent start, stale discovery, lock-holder
   crash, pipe squatting and hidden launch surviving parent exit, mapped to
   AC-08 and AC-12.
9. In the phase table, define A's registration/setup boundary as benchmark
   prompt through A's first pending execution return.

### Writer instructions for design-specification shared-wait-service round 1

Revise the design and publish another automated round. Keep every answer a
proposal; do not consolidate.

Apply the requested changes in order. Item 1 matters most, because the current
Q07 answer contradicts the confirmed SW-05 expiry rule; check the new wording
against SW-05 and AC-09 before publishing. Add Q13 and Q14 after Q12 in the
existing question layout, generated through the same question tooling you used
for Q01 to Q12.

Where a requested body change depends on a new question's answer (Q13 and Q14),
write the body for the recommended option and say so, so the next round can
check them together. If you disagree with a verdict, keep your wording and
explain why in the writer response.

In the next change summary, mark each requested change as applied, applied
with a variation (and why), or declined (and why).

### Final reviewer decision for design-specification shared-wait-service round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-09-15T11:02:35+02:00
- Exchange: specification/design-specification/v0.13.0/shared-wait-service
- Umbrella: docs/v0.13.0/draft.v0.13.0.no_polling.md
- Reviewed document: docs/v0.13.0/design.v0.13.0.shared-wait-service.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: request

### Review identity for design-specification shared-wait-service (round 2)

Umbrella draft: docs/v0.13.0/draft.v0.13.0.no_polling.md
Reviewed specification: docs/v0.13.0/design.v0.13.0.shared-wait-service.md
Review round: 2

### Requestor assessment for design-specification shared-wait-service (round 2)

The revised design addresses the nine round-1 requested changes. Q13 and Q14
now cover the previously missing turn-end capability and explicit isolated
state-home choices. Fourteen complete questions have proposed answers; no
additional missing question was identified during this revision. Existing
options remain sufficient after Q05 and Q07 were rewritten, subject especially
to review of the revised cross-store intent/settlement contract.

Accepted wording is integrated in the body and answers. The timeout claim in
round-1 requested change 6 is explicitly disputed: a successful service commit
with a lost reply still yields a client timeout. The design therefore treats
timeout as unknown, uses a durable workflow intent to fence ownership across
adapter crash, and settles the exact service attempt before clearing that
intent. This is a substantive alternative for review, not a claim that time
budgets create an atomic cross-store boundary.

No requirement decision is reopened. No implementation, native probe, telemetry
coverage or acceptance result is claimed. All question recommendations remain
proposals pending the review and human consolidation gate.

### Change summary for design-specification shared-wait-service (round 2)

Round-1 requested changes:

1. Applied: rewrote Q07 and the deadline section. Comparable source timestamps
   take precedence; a valid pre-deadline authoritative readiness read supplies
   an upper bound without inventing a timestamp. First observed late without
   on-time evidence expires. Unreadable source state retains bounded recovery.
2. Applied: first-instance pipe creation, typed squatting conflict, server SID
   verification by every client and reciprocal client checks; Q02 matches.
3. Applied: Q14 and explicit development/test homes, SID-plus-home endpoint
   identity, physical alias resolution and visible home selection.
4. Applied: Q13 and direct/host-gated/unavailable normal-end evidence in the
   flow, arming, host port and both probes; operator markers are measurement
   evidence and cannot implement a production gate.
5. Applied: missing turn-start evidence permits bounded same-UUID native wake
   redelivery. Execution-unresolved applies to later uncertain workflow effects.
6. Applied with a substantive variation: kept finite service work budgets and
   client margins, but rejected timeout-equals-not-authorized. Added a durable
   workflow intent, a unique attempt UUID and serialized service settlement.
   Ownership transitions resolve outstanding intents before advancing; adapter
   crash cannot remove the fence. Lock-order prohibitions are explicit.
7. Applied: offline status holds the singleton lock before opening SQLite and
   uses IPC when occupied; hot-journal recovery is cited.
8. Applied: acceptance rows cover startup races, stale discovery, lock-holder
   crash, pipe squatting, parent-exit survival, isolated homes and consume timeout.
9. Applied: A setup is benchmark prompt through first pending execution return.

Revalidated one H1, unique headings, fourteen complete questions/answers, local
links, LF and whitespace. No implementation or production adapter was changed.

### Writer response for design-specification shared-wait-service (round 2)

Writer response:

I accepted the round-1 findings and changes except the proposed inference that
a shorter service commit budget makes a client timeout mean not authorized.
Counterexample: the service commits within budget, its reply is lost, and the
client times out. A budget measured from service receipt also cannot bound
earlier IPC delay; disk commit completion can outlast a pre-commit clock check.
The design must not tell an adapter to treat that outcome as rejection.

The alternative Q05 answer uses a durable workflow intent under the existing
authority lock and a stable service attempt UUID. Generation-advancing workflow
transitions resolve the intent first, including after adapter crash. Service
settlement returns an already committed decision or records rejection before
any delayed consume can commit. Until settlement is definitive, no continuation
or ownership transfer is authorized. The service never takes workflow locks.
This adds a recovery obligation to later workflow adapters; item 1 tests it
synthetically. Please assess this explicit disagreement and the replacement
protocol, including failed receipt settlement and lost adapter processes.

Q07 now follows the requested expiry distinction and retains source completion
time where present. The pre-deadline observation is recorded as an upper bound,
not substituted into the source timestamp field. Q13 and Q14 and the remaining
requested edits are applied as detailed in the change summary. Keep all answers
as proposals; no consolidation has been performed.

### Reviewer focus for design-specification shared-wait-service (round 2)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-09-15T11:05:31+02:00
- Exchange: specification/design-specification/v0.13.0/shared-wait-service
- Umbrella: docs/v0.13.0/draft.v0.13.0.no_polling.md
- Reviewed document: docs/v0.13.0/design.v0.13.0.shared-wait-service.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for design-specification shared-wait-service round 2

All nine round 1 requested changes are handled, and I checked each against the
revised body and answers:

1. Q07 and the deadline section now separate an on-time observation, readiness
   first observed after the deadline, and an unreadable source. An observation
   spanning an unresolved clock discontinuity supplies no upper bound. The
   registration-time rejection is gone.
2. Pipe creation uses `FILE_FLAG_FIRST_PIPE_INSTANCE`, squatting is a typed
   conflict, and every client verifies the server's token user SID before
   sending a frame. Q02 matches.
3. Q14 adds explicit isolated homes, and the endpoint is derived from SID plus
   canonical home, visible in `hello`, discovery and status.
4. Q13 adds the `direct-turn-evidence`, `host-gated-turn-end` and `unavailable`
   evidence kinds. They appear in the flow note, arming, the host port and both
   probes, and an operator marker is excluded as a production gate.
5. Same-UUID native wake redelivery without turn-start evidence is in Q06 and
   the crash-gap section. `execution-unresolved` is limited to later workflow
   effects.
6. Applied with a variation that I accept (see below).
7. Offline status takes the singleton lock before opening SQLite and uses IPC
   when the lock is held.
8. The acceptance map now has rows for startup and server identity races and
   for consume timeout or adapter crash.
9. The A-arm setup boundary is defined.

**On the disputed round 1 change 6, the writer is right.** My claim that a
commit budget shorter than the client timeout makes a timeout mean "not
authorized" was wrong: the service can commit within budget and the reply can
still be lost. A budget measured from service receipt also cannot cover earlier
IPC delay. Treating a timeout as unknown is the correct contract.

The replacement protocol is sound where I checked it. It has a durable workflow
intent written under the transition lock and naming a unique attempt UUID, a
service `settle` serialized with `consume` for that attempt, and a rejected
tombstone that a delayed consume cannot override. Because the service is the
single writer and consume commits atomically, settle either sees the commit or
wins the race, and a later consume sees the tombstone. There is no lock cycle:
the service never takes a workflow lock, and no source worker waits on one while
holding the store write lock. A crashed adapter leaves the intent, and the next
generation-advancing transition settles it.

**One substantive gap remains: the intent fence has no way out when the
service stays unavailable.** A workflow transition that meets an unresolved
intent must settle it through the service first. If the service store is
corrupt, the design deliberately reports a concrete unavailable state and never
starts an empty replacement. A stuck service, or a user who simply stops using
it, has the same effect. In each case `consumption-resolution-pending` never
clears, and the review exchange that item 3 fences can never change owner
again, including through the human `resume` and claim path. Today that exchange
works with no wait service at all. The design needs an explicit local human
override that abandons the unsettled attempt and lets the generation advance.

The override is safe because the design already has a second fence. Q06 and the
crash-gap section require the resumed turn's first ordinary callback to validate
the consumption UUID and current workflow authority before any effect. A
consumption the service committed for the abandoned attempt is bound to the old
generation, so it cannot drive a dependent effect after the generation moves.
When the service recovers, it should settle the abandoned attempt and mark any
committed authorization superseded, so the event can be consumed again by the
current owner.

The rest is wording:

- Q07 relies on reading SW-05's "Use the source's completion time, not the
  service's observation time" as forbidding observation time as evidence of
  lateness, not as an upper bound proving on-time completion. That reading
  started with my round 1 suggestion. The answer should state it, so the human
  sees the interpretation at consolidation.
- Offline status now holds the singleton lock briefly. A service starter that
  finds the lock held has no endpoint to connect to and would report
  `startup-timeout`. It should retry acquiring the lock within its 15-second
  readiness bound.
- The "Native host feasibility and prototype trials" acceptance row does not
  mention the Q13 evidence kind or the Stop, Cancel and interruption suppression
  cases the probes now record.

### Question verdicts for design-specification shared-wait-service round 2

I would choose option A for all 14 questions. Q05 needs one addition; Q03 and
Q07 need small wording additions.

**Q01, startup: agree, option A.**

**Q02, IPC transport: agree, option A.** First-instance creation, typed
squatting conflict and client-side server SID verification close the
foreign-user gap.

**Q03, storage: agree, option A.** Suggested addition to the answer and the
startup section: "A starter that finds the singleton lock held with no reachable
endpoint retries acquisition within its readiness bound, because the holder may
be a brief offline status read."

**Q04, failed preparation: agree, option A.**

**Q05, uncertain consumption: agree with option A as revised, add the
unavailable-service override.** I accept the writer's disagreement with my
round 1 proposal: a timeout is unknown, not "not authorized". Suggested addition
to the answer: "If settlement cannot complete because the service is unavailable
or its store is unusable, an explicit local human action may abandon the
unsettled attempt. It records the attempt UUID and the reason, and lets the
workflow generation advance. The resumed turn's validation of the consumption
UUID against current workflow authority (Q06) stops any authorization committed
for the abandoned attempt from driving an effect. When the service recovers, it
settles the abandoned attempt and marks any committed authorization superseded,
so the current owner can consume the event again."

**Q06, crash gap: agree, option A.** Same-UUID wake redelivery with
resumed-turn validation is right, and that validation is what makes the Q05
override safe.

**Q07, incomplete source timing: agree, option A.** Suggested added sentence:
"Observation time is used only as an upper bound that proves on-time
completion, never to find completion late; this is how the design reads SW-05's
rule to use the source's completion time rather than the service's observation
time."

**Q08, policy bounds: agree, option A.**

**Q09, tombstones: agree, option A.**

**Q10, admission limits: agree, option A.**

**Q11, host lifecycle ports: agree, option A.**

**Q12, collector finalization: agree, option A.**

**Q13, turn-end evidence: agree, option A.** Suppression after Stop, Cancel and
interruption is the right proof obligation for `host-gated-turn-end`.

**Q14, isolated homes: agree, option A.**

No further question is missing. The Q05 override is an addition to an existing
answer, not a new decision area.

### Requested changes for design-specification shared-wait-service round 2

Requested changes:

1. Add the unavailable-service override to Q05's recommendation and answer,
   and to "The atomic cancellation fence". Specify:
   - an explicit local human action that abandons an unsettled attempt, recording
     its attempt UUID and reason;
   - that the workflow generation may then advance;
   - that the resumed turn's validation against current workflow authority stops
     any authorization committed for the abandoned attempt from driving an effect;
   - that on recovery the service settles the abandoned attempt, marks any
     committed authorization superseded, and lets the current owner consume the
     event.
   State that this override never runs automatically. Add it to the "Consume
   timeout or adapter crash" acceptance row.
2. Add to Q07's answer and the deadline section that observation time serves
   only as an upper bound proving on-time completion, never to find completion
   late, and that this is the design's reading of SW-05.
3. Add to Q03's answer and "One process per OS user, machine and explicit state
   home" that a starter finding the singleton lock held with no reachable
   endpoint retries acquisition within its 15-second readiness bound.
4. Extend the "Native host feasibility and prototype trials" acceptance row with
   the recorded Q13 evidence kind and the Stop, Cancel and interruption
   suppression cases.

### Writer instructions for design-specification shared-wait-service round 2

Revise the design and publish another automated round. Keep all answers as
proposals; do not consolidate.

Requested change 1 is the only substantive one. Check that the override text
leans on the existing Q06 resumed-turn validation, and does not add a second
authority path. Changes 2 to 4 are small additions; apply them in the same pass.

No other rework is needed, and the accepted round 1 variation on Q05 stays as
written. If you disagree with the override, explain in the writer response how
an exchange blocked by an unsettled intent recovers when the service store is
unusable.

In the next change summary, mark each requested change as applied, applied
with a variation (and why), or declined (and why).

### Final reviewer decision for design-specification shared-wait-service round 2

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-2 -->

## Round 3 by requestor

- Recorded: 2026-09-15T13:14:24+02:00
- Exchange: specification/design-specification/v0.13.0/shared-wait-service
- Umbrella: docs/v0.13.0/draft.v0.13.0.no_polling.md
- Reviewed document: docs/v0.13.0/design.v0.13.0.shared-wait-service.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: request

### Review identity for design-specification shared-wait-service (round 3)

Umbrella draft: docs/v0.13.0/draft.v0.13.0.no_polling.md
Reviewed specification: docs/v0.13.0/design.v0.13.0.shared-wait-service.md
Review round: 3

### Requestor assessment for design-specification shared-wait-service (round 3)

The revised design answers all fourteen design questions with explicit options,
trade-offs and proposed answers. No additional decision area is missing.
The remaining round-2 recovery gap is addressed inside Q05, using the existing
workflow authority and Q06 resumed-turn validation. All reviewer wording
suggestions are applied. Answers remain proposals for human consolidation.

The recovery action records abandonment before allowing the existing ownership
transition, persists reconciliation evidence and never runs automatically.
A recovered service supersedes old authorization without bypassing cancellation,
recipient, result or current-authority checks. Completed and uncertain effects
remain governed by Q06; abandonment is not permission to replay them.

### Change summary for design-specification shared-wait-service (round 3)

Round-2 requested changes:

1. Applied: Q05 recommendation/answer and the atomic cancellation fence now
   permit explicit local human abandonment when the service cannot settle.
   The durable record names attempt UUID, event, recipient, old generation,
   reason and pending reconciliation. Existing authorized ownership may advance;
   no second authority path or automatic override is introduced. Q06 rejects
   stale-generation effects. Recovery settles the old attempt, supersedes its
   committed authorization and permits eligible current-owner consumption.
   The acceptance row covers this path. Completed or uncertain effects keep
   their receipt/recovery gates, and rebinding wording now matches this rule.
2. Applied: the deadline section and Q07 explicitly state the reading of SW-05:
   observation time supplies only an on-time upper bound, never lateness proof.
3. Applied: startup and Q03 retry singleton acquisition within the 15-second
   readiness bound when a brief offline status reader holds it without IPC.
   The startup acceptance row includes that race.
4. Applied: the native feasibility acceptance row records the Q13 evidence kind
   and Stop, Cancel and interruption suppression cases.

No new question was added. Fourteen complete questions and proposed answers
remain, with one H1, unique headings, checked local links and clean whitespace.

### Writer response for design-specification shared-wait-service (round 3)

Writer response:

I accept all four round-2 requested changes. The human recovery path closes the
permanent service-unavailability deadlock without changing who may claim a
workflow or approve its actions. The abandonment record survives clearing the
in-flight intent, and failed service reconciliation does not reverse the
ownership transition.

I made explicit two consequences of the existing Q06 contract: superseding an
old authorization cannot replay an already completed effect, and an effect
that began before abandonment keeps its unresolved-receipt gate. This clarifies
recovery without weakening the accepted timeout-as-unknown settlement design.

There is no remaining disagreement. Please assess the revised design and all
fourteen proposed answers for consolidation readiness.

### Reviewer focus for design-specification shared-wait-service (round 3)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-3 -->

## Round 3 by reviewer

- Recorded: 2026-09-15T13:16:39+02:00
- Exchange: specification/design-specification/v0.13.0/shared-wait-service
- Umbrella: docs/v0.13.0/draft.v0.13.0.no_polling.md
- Reviewed document: docs/v0.13.0/design.v0.13.0.shared-wait-service.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for design-specification shared-wait-service round 3

All four round 2 requested changes are applied. I reread the full design to
check them in context:

1. **Service-unavailable abandonment.** It appears in Q05's recommendation and
   answer and in "The atomic cancellation fence".
   - It runs only as an explicit local human action under the existing workflow
     transition lock.
   - It durably records the attempt UUID, event, recipient, old generation,
     reason and pending reconciliation, and that record outlives the cleared
     intent.
   - It never runs automatically and grants no claim, approval or continuation
     authority.
   - It leans on Q06's resumed-turn validation instead of adding a second
     authority path.
   - On recovery, the service settles the abandoned attempt and supersedes any
     committed authorization, and delayed requests cannot restore it.
   - Completed effects are not replayed. An effect that began before abandonment
     keeps its Q06 receipt gate. A failed reconciliation keeps the evidence
     without undoing the ownership change.
   - The rebinding paragraph and the "Consume timeout or adapter crash"
     acceptance row match.
2. **Observation time.** Q07 and the deadline section state that observation
   time only proves on-time completion, and that this is the design's reading of
   SW-05.
3. **Starter retry.** A starter that finds the singleton lock held with no
   reachable endpoint now retries within the 15-second bound. The startup
   acceptance row includes that race.
4. **Probe acceptance row.** The native feasibility row records the Q13 evidence
   kind and the Stop, Cancel and interruption suppression cases.

Across the whole document, the 14 answers are consistent with each other and
with the confirmed requirement:

- Q05 settlement or abandonment and Q06 resumed-turn validation form one fence.
- Q07 applies SW-05's expiry rule.
- Q13's evidence kinds feed both probes and the capability classification.
- Q14's per-home endpoint matches the Q02 pipe identity and the Q03 singleton
  lock.

The round 2 variation on timeout semantics (a timeout is unknown, not "not
authorized") stays correct and is described the same way in the body, Q05 and
the acceptance map. I found no missing decision area.

One wording gap remains, and it changes no behavior. The recovery paragraph
orders abandonment reconciliation before current-owner consumption only
implicitly, through sentence order. If the current owner's consume reached the
recovered service before the abandonment evidence, it would meet the old
committed authorization and be refused as already consumed. That is safe, but
confusing. Saying the order explicitly removes the ambiguity for the later
review adapter.

### Question verdicts for design-specification shared-wait-service round 3

I would choose option A for all 14 questions. Each option set is materially
distinct, each con is stated honestly, and each recommendation follows from the
confirmed requirement and the inspected code.

**Q01, startup: agree, option A.** On-demand start with explicit stop; offline
status exposes retained work.

**Q02, IPC transport: agree, option A.** A user-restricted named pipe,
first-instance creation, typed squatting conflict and mutual SID verification.

**Q03, storage: agree, option A.** Rollback journaling with full
synchronization, offline status under the singleton lock, and starter retry
within the readiness bound.

**Q04, failed preparation: agree, option A.** Typed non-armed preparation under
the same wait ID.

**Q05, uncertain consumption: agree, option A.** Durable intent, same-attempt
settlement, timeout treated as unknown, and explicit human abandonment when the
service cannot settle. Wording polish only, listed below.

**Q06, crash gap: agree, option A.** Receipt reconciliation for workflow
effects, and same-UUID wake redelivery with resumed-turn validation.

**Q07, incomplete source timing: agree, option A.** The observation upper bound
applies to on-time proof only; readiness first observed late expires without
on-time evidence.

**Q08, policy bounds: agree, option A.** Per-kind versioned policies with the
synthetic defaults.

**Q09, tombstones: agree, option A.** Seven-day details, compact tombstones
until explicit purge.

**Q10, admission limits: agree, option A.** Count limits without eviction.

**Q11, host lifecycle ports: agree, option A.** Provisional semantic ports with
functional and coverage evidence kept separate.

**Q12, collector finalization: agree, option A.** A finite drain bound with
versioned amendments.

**Q13, turn-end evidence: agree, option A.** Direct or proven host-gated turn
end, otherwise retained-result-only.

**Q14, isolated homes: agree, option A.** Explicit, visible overrides with one
authority per canonical home.

### Convergence evidence for design-specification shared-wait-service round 3

Covered wording:

1. "The atomic cancellation fence", the paragraph starting "The resumed turn's
   Q06 validation". Replace "Once the service recovers, the adapter submits the
   durable abandonment evidence under current workflow authority." with "Once
   the service recovers, and before the current owner consumes that event, the
   adapter submits the durable abandonment evidence under current workflow
   authority."
2. Q05 recommendation and answer. Replace "On recovery, settle the abandoned
   attempt, supersede any committed authorization and permit current-owner
   consumption through the ordinary gates." with "On recovery, settle the
   abandoned attempt and supersede any committed authorization before permitting
   current-owner consumption through the ordinary gates."
3. At consolidation, update the status line "revised for specification review
   round 3" to reflect the consolidated state.

Convergence rationale:

Every in-scope design decision for umbrella item 1 is expressed as one of 14
questions with distinct options and a recommendation. Those recommendations are
now written into the body, the acceptance map and the answers consistently.

Three rounds closed these gaps:

- the deadline rule that conflicted with SW-05;
- foreign-user pipe squatting;
- shared state homes for development and tests;
- missing turn-end evidence;
- wake redelivery after a bridge crash;
- uncertain consumption after a timeout, adapter crash or permanently
  unavailable service;
- offline hot-journal recovery.

The one round 2 disagreement was resolved in the writer's favor, and the result
is described the same way throughout.

What remains is wording: two sentences that make the abandonment-reconciliation
order explicit, and a status-line update at consolidation. Neither changes a
choice, adds behavior, or moves scope between umbrella items.

This recommendation is advisory. Consolidation needs the human's choice.

### Writer instructions for design-specification shared-wait-service round 3

No further automated review round is needed. Present this convergence
recommendation to the human and wait for their choice.

If the human chooses to consolidate, apply the covered wording first. Then
record the 14 option A answers as design decisions, and update the status line.
The later review adapter (item 3) inherits the Q05 intent, settlement and
abandonment obligations. Keep them visible as its integration requirements, not
as work done in item 1.

If the human asks for another round, publish it with the reason and any
guidance, and keep the answers as proposals.

### Final reviewer decision for design-specification shared-wait-service round 3

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-3 -->

## Round 3 by human - human-confirmation

- Recorded: 2026-09-15T13:34:57+02:00
- Exchange: specification/design-specification/v0.13.0/shared-wait-service
- Umbrella: docs/v0.13.0/draft.v0.13.0.no_polling.md
- Reviewed document: docs/v0.13.0/design.v0.13.0.shared-wait-service.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-3 -->
