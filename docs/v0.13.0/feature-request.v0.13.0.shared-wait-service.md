# Run one durable monitoring service

<!-- markdownlint-disable MD013 -->

- Type: feature-request
- Target version: v0.13.0
- Topic: `shared-wait-service`
- Status: consolidated after specification review round 2; ready for design
- Canonical draft: [Shared wait service](draft.v0.13.0.shared-wait-service.md)
- Umbrella: [Wake Me When It Matters](draft.v0.13.0.no_polling.md), item 1

## Specification revision introducing shared waits

The [historical wait analysis](../draft_codex_wait.md) and
[expanded token/quota investigation](../draft.v0.13.0.codex_token_investigation.md)
describe repeated model requests that carry substantial conversation context
while external work remains unchanged. The later investigation reports
51.54 million wait-related input tokens on September 11 and 11.78 million on
September 12. These are historical observations under different workloads
and conditions, not controlled service measurements or promised savings.

Umbrella item 1 introduces a common durable monitoring authority. The focused
draft adds early native-wake probes and a controlled comparison before
substantial implementation. Its latest revision aligns the copied umbrella
entry, records compaction, transport/CA and approval-review conditions, and
defines Windows suspension, resume and clock-change behavior.

This requirement carries those behaviors into the v0.13.0 core effort. It
does not establish that the service, collector, host probes or benchmarks
have already been implemented or passed.

## User story for an idle conversation

As a user running authorized work in an existing terminal conversation, I
want the agent to register an exact wait and finish its turn normally, so
ordinary code can monitor the work and the same conversation can continue
automatically when an actionable result is ready.

An unchanged wait must make no model requests or repeated context
submissions. Registration and useful continuation may consume tokens. The
application remains open and available for other user work while waiting.

## Current behavior before the v0.13.0 shared service

- Groundhog guidance uses detached execution where needed and subsequent
  `ghog status` checks. Longer intervals reduce model re-entry without
  removing it. Its status authority distinguishes a live run from a lost
  or completed run; log growth does not establish completion.
- Exact review-exchange waits already keep checks inside a bounded Python
  call. A host can nevertheless yield that call and repeatedly return the
  model to status-only work. Progress output can also become an unwanted
  host wake signal.
- Review-request discovery already provides authoritative rescanning,
  native notification hints and a polling fallback. Its existing waiter
  does not provide durable subscriptions and delivery to idle hosts.
- The associated drafts contain host research and proposed experiments,
  not an implemented common monitoring service or verified host support.

## Boundary of the shared-wait-service effort

| Included in item 1 | Owned by later umbrella items |
| --- | --- |
| Durable registration, source and host interfaces, result persistence and delivery bookkeeping | Production Groundhog/check readers in item 2 and review sources in item 3 |
| Local IPC, instance discovery, user-owned lifecycle, diagnostics and recovery | Production Codex, Claude and Copilot adapters in items 4 through 6 |
| Synthetic source/host fixtures and limited Codex/Claude feasibility probes | Canonical and generated guidance migration in item 7 |
| Initial controlled A/B methodology, collector requirements and prototype evidence | Common final service comparison and support proof in item 8 |
| Core contracts reusable by the eventual Gemini route | Production Gemini integration and its live evidence in item 9 |

The initial deployment target is the user's local Windows environment.
Preserve ordinary `codex.exe` and `claude.exe` terminal conversations.
Desktop applications, automatic reopening of a closed TUI, remote/WSL
boundaries and multi-machine routing are outside the initial support claim.

The core must handle concurrent repositories, worktrees, conversations,
review roles and wait types. Synthetic fixtures establish the core contract;
they do not substitute for later production source and host validation.
Current role-wait instructions remain authoritative until item 7 migrates
them to a supported register-and-idle workflow.

## Recommended service direction and bounded alternatives

Use one shared monitoring authority with separate source and host adapters.
The authority owns registrations, source watches, results and delivery state.
A bridge per session or wait may be necessary for a host, but remains a
transport client and must not create a second source-monitoring authority.

| Choice carried from the draft | Benefit | Constraint or tradeoff |
| --- | --- | --- |
| On-demand service owned by the current user, one authority per user and machine | Reuses monitoring across consuming repositories with little startup work for users | Requires reliable discovery, singleton enforcement and background lifetime |
| Explicit startup of the same user-owned service | Makes service readiness and lifecycle visible | Requires a startup action before registration |
| Named pipes or authenticated loopback IPC | Provides a local client/service boundary | Access control, compatibility and reconnect behavior need a concrete design |

The recommended direction is the on-demand user-owned service. These are
design candidates, not a selected wire schema, database or transport.
Administrator rights and a Windows service installation must not be assumed
necessary. Direct localhost WebSocket delivery to Claude is not implied by
any internal transport choice.

## Required registration and quiet-wait behavior

### SW-01: Finish the registering turn normally

1. Start or identify authorized work and register its exact condition.
2. Acknowledge success only after the registration is durable and a usable
   host route is armed.
3. Let the agent acknowledge briefly and finish its turn normally with the
   application open and no foreground wait tool left pending.
4. Monitor the unchanged source entirely in ordinary code.
5. Persist a validated actionable outcome, deliver it to the registered
   conversation and resume only its permitted continuation.

Normal turn completion differs from Stop/Cancel, an interrupted tool or
application closure. Those actions can invalidate a host route.

During an unchanged wait, prohibit wait-induced model requests, status-only
reasoning, progress narration and repeated tool polling, including polling
delegated to another LLM. Native file notifications, blocking IPC, local host
queue checks and bounded service reconciliation are compatible with this
contract. Keep service health checks, retries and progress in local
diagnostics, away from host channels that invoke the model on output.

### SW-02: Bind durable registrations to exact identities

The registration contract must represent:

- A wait identity and idempotency key so retrying one registration creates
  one logical wait.
- Source kind, canonical repository/worktree or artifact home, and exact
  run or exchange identity, including applicable round and generation.
- Host kind, exact session/thread and connection incarnation.
- Subscription provenance, applicable review role and permitted continuation.
- Capability state and the armed route.
- A finite deadline or explicit indefinite-wait policy.
- Durable result and acknowledgement state.

These are required meanings, not fixed field names. Do not resolve recipients
from cwd, the newest transcript, the active editor tab or a fuzzy session
name; do not identify a run from a reused PID alone.

Reconcile source completion before registration, before arming and before
normal turn completion. Retain and deliver an existing result without
requiring another source notification. Failure to persist or arm must be
reported immediately rather than presented as successful automatic wake.

Reject registration without either a finite deadline or an explicit
indefinite-wait policy with a typed validation error and no wait record.

An identical idempotent retry returns the existing wait and acknowledgement
state. Reusing its key with a different source, recipient, deadline policy
or continuation returns a typed conflict naming the existing wait without
changing it. Changed intent requires a new registration or an explicit
lifecycle action.

For the initial Windows deployment, trust processes running as the current
OS user at the local IPC boundary and deny foreign-user access. Those
processes may register an exact session, cancel waits and inspect status.
Record when the registrant differs from the recipient and expose that
provenance to SW-04 validation. OS-user access does not grant workflow
authority or relax exact recipient and review-role restrictions. A
per-session secret is possible later hardening, subject to host feasibility.

### SW-03: Keep source, delivery and consumption state separate

Persist the outcome before delivery. Represent cancellation, expiry,
invalidation and operational failure distinctly from source success.
Separate source readiness, a delivery attempt, transport acceptance and
workflow consumption.

Use a stable event identity, wait identity, source identity, typed outcome,
bounded result data and an authoritative result reference. Use a stable
continuation kind. Events must not carry arbitrary executable continuation
text, whether it comes from source content or from the registrant.

Reconcile crashes between sending and recording delivery, including a lost
acknowledgement. Preserve event identity on retries and use idempotent
consumption. One normal actionable event should produce one logical
continuation, which may contain several useful model requests. Report
duplicate wakes separately from repeated consumption; do not claim arbitrary
exactly-once execution across crashes.

Queue for a busy host using its supported behavior while preserving the
recipient and ordering. For a closed or unavailable host, retain the result
with an explicit pending/unavailable route state. A reconnecting bridge or
later turn may rearm the same verified thread/session on the host side when
ownership remains valid. The service must not wake the model merely to ask
it to rearm. A different recipient requires explicit local user action
through status tooling and the existing workflow authority. Unverifiable
bindings stay pending; never create a replacement conversation or worker.

If a persisted outcome survives but required result details are missing,
replaced or belong to another source generation, retain that outcome and
report a typed unavailable or invalid result. Suppress continuation that
depends on those details until validation or explicit resolution. Do not
substitute another source or automatically rerun the underlying work.

### SW-04: Preserve cancellation and review authority

Cancelling a wait durably before consumption suppresses automatic
continuation for that registration, regardless of when source readiness
occurred or was observed. It must not cancel healthy underlying work, alter
a review exchange or rewrite the source outcome. Retain an already ready
result as evidence; cancellation does not reopen an expired terminal wait.

At consumption, ordinary code must atomically check durable cancellation
while recording authorization to consume the event. A cancelled event must
be rejected without relying on model interpretation. Transport acceptance
alone does not authorize continuation. An event already queued at the host
may still wake it after cancellation; report that as a cancellation-induced
wake. Once consumption authorizes continuation, later cancellation follows
the existing execution semantics and does not retroactively undo work.

Apply SW-05 to readiness versus expiry, including events discovered together
after restart or suspension. Cancellation before consumption suppresses
continuation in every ordering without changing the recorded source outcome.

Machine events provide information, not human approval or new permissions,
even when the host represents them as user messages. Validate the
registration and any registrant-other-than-recipient provenance before
continuing an already authorized workflow. Render delivered text from fixed
templates, typed fields and the stable continuation kind. Source and
registrant text must not supply executable instructions.

A requestor and reviewer subscribe independently through the existing
protocol. Neither may register, create, invoke or directly wake its
counterpart. Preserve exact exchange/round matching, ambiguity handling,
atomic claims, ownership generation and session-only capabilities. A source
notification is not an ownership claim. Keep capabilities out of ordinary
logs and user-facing events.

At convergence or another human gate, present the durable outcome and await
the existing human decision. An event cannot supply `confirm`.

### SW-05: Recover after Windows suspension and clock changes

Preserve waits, outcomes, events and delivery-attempt identities across
sleep, hibernation and restart. Monitoring and delivery are not expected
during machine suspension. On resume, reconcile authoritative source,
cancellation, ownership, deadline and host-route state in ordinary code
before automatic delivery. Recover missed events without a further change.

Persist finite deadlines as absolute UTC instants set at registration.
Suspended time counts toward expiry; resume and restart do not reset the
deadline. Indefinite waits remain indefinite. Use monotonic time for local
scheduling and duration measurements with explicit handling of its suspension
behavior. A raw monotonic timestamp must not be reused across process restart.

Re-evaluate pending deadlines after resume or a detected UTC correction.
Forward corrections can expire a pending wait; backward corrections can
delay its expiry. Neither can invent source completion, reopen a terminal
wait or repeat consumed work.

For a still-pending wait, authoritative source completion at or before the
persisted UTC deadline wins over expiry. After that deadline, expire the wait
when no authoritative completion at or before it exists, including when
completion is absent or is timestamped later. Use the source's completion
time, not the service's observation time. Record uncertainty when a UTC
correction separates completion from observation; the resume timestamp alone
does not establish causal order. An already terminal wait stays terminal.

Cancellation before consumption suppresses continuation under SW-04 even
when the source completed earlier. Keep stale routes pending, reconcile
unacknowledged delivery by event
identity and avoid replacement workers or a wake for each missed check.
An unchanged, unexpired, uncancelled wait remains pending without inference.

### SW-06: Operate the shared authority through local tooling

Coalesce identical source watches while preserving each subscription's
recipient and authorization. Treat native notifications as hints to read
authoritative state. Any fallback reconciliation cadence must be bounded,
justified and executed by the service.

Use llm-shared launcher and Python-environment conventions. A consuming
repository supplies resolved context; startup must not depend on its cwd,
an interactive alias or another project's Python. Background launch must
remain hidden on Windows and survive the initiating shell call returning.

Define discovery, singleton enforcement, readiness, reconnect behavior,
protocol compatibility, durable storage, retention and cleanup. Apply
the current-OS-user access boundary and workflow restrictions in SW-02 and
SW-04. Provide ordinary local status tools for pending waits, failures and
unsupported capabilities without model inference. Do not store copies of
conversation context in the service.

Treat temporary source-access loss as unknown readiness during a bounded
recovery interval fixed for each source kind before any wait of that kind is
registered. If access is not restored within that interval, persist one typed
monitoring-failure outcome and deliver it as actionable under SW-07. It does
not mean that the underlying work failed.

Exclude active waits and ready-but-unconsumed results from automatic terminal
cleanup. Removing them requires an explicit documented lifecycle action.
Retain source evidence for cancelled ready waits under the documented
terminal-retention policy. Status tooling must expose pending or unconsumed
state and age so retained records remain manageable.

### SW-07: Report capability failures and explicit fallbacks

Distinguish at least these outcomes:

| Capability outcome | Required user-visible behavior |
| --- | --- |
| Strict idle continuation supported for this session and wait type | Report durable registration and armed route |
| Result retention available but automatic continuation unavailable | Retain the result and identify manual resumption |
| Direct pending-tool wait available | Identify its finite timeout and pending-turn behavior separately |
| Unsupported or misconfigured source/host route | Report the concrete failure; make no automatic-wake claim |

Do not silently fall back to periodic LLM checks, disguise a timeout as work
completion or recreate a short polling cycle after it. Preserve the user's
model, approval, telemetry and provider settings during capability probes.

Bound delivery attempts for an unchanged failure condition by host route
kind. On exhaustion, retain the event, result and diagnostic without further
automatic attempts. Resume delivery only after explicit local retry through
ordinary tooling or validated recovery, such as same-session rearming.
Neither source recovery nor delivery retry may become model-driven polling.

## Required feasibility evidence before substantial implementation

### SW-08: Prove the native wake routes with a small harness

Prove the Codex wake primitive first, then attempt Claude in an independently
available session. Before substantial service implementation fixes the host
interface, use a small ordinary-code harness with one persisted synthetic
registration, result and delivery record. Record exact recipient, wait/event
identity, due condition, result reference and attempt/consumption state.
The harness and collector must outlive their initiating tool call.

For each available host, establish a ten-minute unchanged-source interval
after verified normal turn completion. Obtain that boundary from host
lifecycle evidence or an independent operator marker. Predeclare bounded
delivery and duplicate-observation windows. Demonstrate automatic useful
continuation in the same conversation without a new prompt, Enter key,
manual resume or replacement session.

For Codex, validate the resolved executable, exact thread UUID, actual
storage/profile and `CODEX_THREAD_ID` binding. Test the draft's native queue
candidate in an ordinary idle TUI. A successful queue exit or context left
for a future human prompt does not pass. Record retry behavior without
assuming fresh CLI client IDs are idempotent. An optional App Server route
must bind the relevant owning backend/thread; an unrelated server, context
injection or active-turn steering is insufficient evidence.

For Claude, verify the exposed Monitor capability and actual schema in that
session, Windows command launch, silent subscription survival after normal
turn completion, same-conversation delivery, cancellation and bridge exit.
Use the command bridge candidate with local IPC, subject to actual capability.
Do not change provider, permissions or telemetry settings to enable Monitor,
or infer Claude support from Codex results.

Run early-event, busy-host, harness restart, lost-acknowledgement,
cancellation, interrupted/closed TUI and bridge-failure cases from the
[draft's PoC procedures](draft.v0.13.0.shared-wait-service.md#initial-codex-and-claude-proofs-of-concept).
Use synthetic outcomes and independently authorized sessions, never an
automated review counterpart.

Close the checkpoint with a per-host finding: passed for measured cases,
failed, capability unavailable or measurement inconclusive. Item 1 may close
under SW-09 when at least one route proves functional arming, normal turn
completion, an actual quiet interval and automatic continuation in the same
conversation. Keep unproven host-interface assumptions provisional and
revalidate them in the first production adapter item for each host. Probe
evidence does not complete a production adapter item.

When no route proves that sequence, independent synthetic core and collector
work may proceed, but require a human checkpoint before freezing the host
interface or closing item 1. Retain failed, unavailable and inconclusive
evidence; do not substitute manual resumption or another conversation.

Functional wake evidence and request coverage are separate findings. With
incomplete coverage, record "wake observed, coverage inconclusive"; leave the
strict no-inference criterion and support claim open for item 8. Core
fixtures and functional wake evidence may be accepted separately, but missing
telemetry never establishes zero inference.

## Controlled comparison required for the shared wait

### SW-09: Preserve prototype and service evidence separately

Use the [controlled A/B protocol](draft.v0.13.0.shared-wait-service.md#controlled-ab-measurement)
as the shared methodology, including its seed and benchmark prompts.

| Arm | Mechanism | Evidence scope |
| --- | --- | --- |
| A | Foreground synthetic work with model-driven polling | Controlled classic-polling cost |
| B-prototype | Small harness plus native wake primitive | Wake feasibility and preliminary cost |
| B-service | Actual shared monitoring service, durable registration and armed route | Observed behavior and cost of the service |

Run matched A versus B-prototype trials before substantial implementation.
Item 1 closes with synthetic core fixtures, a validated collector,
A/B-prototype reports, explicit per-host probe findings under SW-08 and the
bounded live Windows core sleep/resume check specified after the acceptance
table. Incomplete request coverage follows SW-08 and AC-02.

Fresh matched A versus B-service trials are item 8 acceptance using the first
available production host route. Record that obligation as outstanding in
item 1 validation. Reuse this methodology and identify the actual service
instance and registration/delivery records for B-service. Never relabel
prototype evidence as service evidence.

Require quiet-wait behavior and useful continuation, and report registration
and delivery overhead. There is no minimum net token-savings threshold: an
unfavorable end-to-end delta is a measured result, not by itself a failure of
acceptance.

Use a nominal 240-second synthetic source condition, not a real Groundhog
walk or review. Arm A requests an initial 1000 ms yield if supported, otherwise
the shortest supported yield, followed by 60000 ms waits on the same execution.
Record actual supported durations and return counts. This deliberate polling
exception applies only inside the controlled benchmark.

B acknowledges durable registration and arming, ends normally, and resumes
to validate and consume the result once. Both arms end with the assistant's
`WAIT_TEST_DONE` response after success. A missing automatic wake or unavailable
route is not a passing B trial even if quiet-time usage is zero.

### SW-10: Match context, environment and timing

Use fresh conversations for every trial and at least three fresh trials per
arm for each comparison. Counterbalance pair order, for example `A B`,
`B A`, `A B`. Keep host build, selected model, reasoning, context/compaction
configuration, repository/worktree, instructions, permissions and tool
inventory equivalent except for the recorded wait integration.

Freeze and hash both source drafts. Seed every conversation with their full
contents using the protocol's `READY` prompt. Verify complete reads and
retained-context size rather than trusting `READY`. Predeclare a context
matching tolerance, such as the draft's 5% example; flag and repeat
materially unmatched pairs. Keep seeds within the context window, report
seeding separately and retain A's natural context growth during polling.

Record effective compaction threshold/policy, approval policy,
`approvals_reviewer`, redacted proxy/CA configuration, actual transport and
fallbacks, certificate errors, retries, compaction attempts/failures and
attributable auxiliary approval-review usage. Match configuration across
paired arms; preserve failures and deviations rather than selecting clean
runs. Attributable post-seed compaction in either arm is a measured treatment
effect: retain it and count its cost. Repeat a pair for an actual seed or
configuration mismatch or invalid telemetry, not merely because compaction
occurred. Report auxiliary usage separately and unknown attribution explicitly.

Run sequentially with no unrelated work in the measured conversation.
Select telemetry by exact thread identity regardless of other repository
sessions. Keep the machine awake for baseline comparisons; retain and repeat
pairs affected by suspension or clock discontinuity. Resume tests provide
separate recovery evidence.

Create each unique run manifest in ordinary code after `READY` and before
the benchmark prompt. Record run/pair/arm identity, exact thread and storage,
seed hashes, configuration, source identity and pre-start counters/file
positions. Fix finite wake-latency and duplicate-observation bounds once per
host-and-version comparison series before its first trial, and record them
in each run manifest. Changing either bound starts a new series; retain all
earlier trials and bound misses. Observe these distinct boundaries:

| Measurement | Required boundary |
| --- | --- |
| End-to-end task | Benchmark prompt to final assistant `WAIT_TEST_DONE` turn completion |
| Synthetic source runtime | Source start to authoritative readiness, nominally 240 seconds |
| A's polling interval | First pending execution return to source readiness |
| B's quiet interval | Normal registering-turn completion to source readiness |
| Wake latency | Source readiness to first useful continuation |
| Duplicate observation | Final turn completion to predeclared observation-window end |

Report registration/setup, actual quiet-wait, useful continuation and
end-to-end costs separately. A timer starting at registration does not imply
240 idle seconds. The ten-minute feasibility baseline remains separate.
Any equal-quiet-duration variant must declare its changed source-release
rule before testing. Record UTC correlation timestamps and monotonic elapsed
durations, and correlate buffered evidence to original request times.

### SW-11: Collect reliable request and usage evidence

Implement the standalone collector specified by the draft using explicit
manifest and output paths and the repository's command rules. Do all
collection, timer handling and analysis outside the measured conversation.

The collector must:

- Verify exact thread/profile metadata and installed telemetry schema.
- Establish cumulative baselines and event identity before the start marker,
  so repeated pre-start usage is not counted as benchmark work.
- Distinguish request attempts from usage-bearing completions. Use request
  identity where available; never label usage reports as complete request
  coverage without supporting evidence.
- Deduplicate usage reports and reconcile compatible per-request/cumulative
  counts without counting both representations. Handle counter resets,
  compaction, retries, rotation, delayed writes and partial/malformed JSONL.
- Preserve unknown values, verify cached-input semantics before deriving
  uncached usage, and avoid double counting reasoning and output.
- Correlate requests, tool call IDs/results, host turns and source readiness,
  including nested/orchestrated calls and polling under other tool names.
- Separate unchanged-work polling from useful terminal-result processing;
  flag requests crossing phase boundaries or otherwise ambiguous attribution.
- Detect missing evidence, unexpected threads, unrelated inference and
  compaction. Retain local raw evidence and publish bounded redacted reports.

Validate the collector with known synthetic records covering repeated
pre-start usage, duplicates, missing request records, resets/compaction,
delayed reports, nested calls and unrelated threads. No model call or real
sleep is required for those checks.

Report exact counts for attempts/completions; wait-induced requests/input;
diagnostic wait/non-wait totals; input, cached/uncached input, output and
available reasoning usage; each phase's cost; source/quiet durations; wake
latency; logical wakes and consumption; retries, compactions and gaps.
Publish per-pair raw counts, context comparisons and cost deltas, followed
by median and range and counts of tested, valid, passed, failed and
inconclusive trials. Keep failures and repeat invalid pairs without silently
dropping their evidence. Observed cache state is not guaranteed by fresh
sessions; duration normalization is supplemental only.

Claim zero quiet-wait requests only with adequate coverage and correct
automatic continuation. Zero wait-tool calls, unchanged usage counters or
a quiet UI alone are insufficient. Do not infer billing or quota savings
from token counts. Apply the methodology separately to Claude if its Monitor
and telemetry permit it, using that host's actual schema and keeping its
results separate from Codex.

## Acceptance criteria for the shared core

All criteria concern this core and its evidence boundary. Later production
adapter and instruction-migration work remains outside item 1.

| ID | Acceptance evidence |
| --- | --- |
| AC-01 | A successful registration persists once and confirms an armed usable route. An identical retry returns its wait and acknowledgement state; a conflicting key returns a typed conflict without mutation. Omitting both a finite deadline and an explicit indefinite policy returns a typed validation error and creates no wait. |
| AC-02 | A normally completed registering turn leaves no pending foreground wait and automatically continues the same conversation after the ten-minute unchanged-source baseline. Verified request coverage must show zero wait-induced inference. Incomplete coverage is recorded as "wake observed, coverage inconclusive"; the strict criterion and support claim remain open for item 8 while core fixtures and functional wake evidence may be accepted separately. |
| AC-03 | Completion before registration, arming or turn end remains deliverable without another source event. |
| AC-04 | Duplicate/missed notifications and several subscribers use authoritative reconciliation and coalesced watches without cross-repository or cross-session delivery. Source-access loss stays unknown within the predeclared source-kind recovery interval, then produces one typed monitoring failure without declaring underlying work failed. |
| AC-05 | Outcomes survive restart and persist before delivery; lost acknowledgements retain event identity and do not repeat consumed workflow work. Unchanged delivery failures exhaust the route-kind attempt bound and retain the result until explicit local retry or validated recovery. Missing, replaced or wrong-generation required details preserve the outcome and suppress dependent continuation pending validation or explicit resolution. |
| AC-06 | Busy, interrupted, closed and stale routes preserve recipient, ownership and pending results. Host-side rearming requires the same verified session and valid ownership; a different recipient requires explicit local user action and existing workflow authority. Unverifiable bindings stay pending without replacement or a model wake to request rearming. |
| AC-07 | Readiness/expiry follows authoritative completion time versus the persisted deadline for pending waits. Durable cancellation before consumption suppresses continuation in every ordering, including restart and suspension recovery, while preserving source outcomes and underlying work; terminal waits remain terminal. |
| AC-08 | Synthetic foreign-user IPC, exact-recipient, registrant provenance, review-role and instruction-injection cases enforce SW-02/SW-04. Stale or ambiguous authority is rejected; OS-user access and machine events never grant workflow permission, human approval or counterpart creation. |
| AC-09 | Sleep/resume with an unchanged indefinite wait remains quiet. Pending completion at or before the deadline wins; absent or later completion expires after the deadline. Recovery uses source timestamps, records clock uncertainty and never resets the deadline. |
| AC-10 | Forward/backward UTC changes and restart honor persisted deadline and authoritative completion semantics without reopening terminal waits or reusing raw monotonic timestamps. |
| AC-11 | Queued, consumed or cancelled events retain their state across resume. Ordinary-code consumption atomically checks durable cancellation; accepted-but-cancelled queued events may cause a reported cancellation-induced wake but cannot authorize continuation. Cancellation after consumption follows existing execution semantics. Same-session rearming and lost-receipt recovery do not repeat consumed work. |
| AC-12 | Local startup, discovery, current-OS-user access control, compatibility, reconnect and diagnostics satisfy the shared user-owned lifecycle without model health checks. Automatic terminal cleanup excludes active waits and ready-but-unconsumed results; status shows their state and age. Explicit lifecycle actions and cancelled-result retention are documented. |
| AC-13 | Capability, monitoring, delivery and required-result-detail failures are typed and fallbacks explicit. Source recovery and delivery attempts obey their bounds; retained outcomes are not silently replaced or rerun, and unavailable automatic delivery is never reported as an armed wake. |
| AC-14 | The Codex and available Claude probes retain exact version/session, timing, arming, delivery, consumption and request-coverage evidence with explicit outcomes. At least one functional route must pass for item 1 closure; otherwise a human checkpoint precedes interface freezing or closure. Unproven host assumptions remain provisional for revalidation in each later host adapter item, and functional wake does not prove zero inference. |
| AC-15 | Item 1 A/B-prototype reports follow SW-09 through SW-11 with declared series bounds, separate phases and all failed/inconclusive trials. A/B-service remains an explicit item 8 acceptance obligation using the first available production host route. Report overhead and deltas without requiring minimum net token savings or relabelling prototype results as service evidence. |
| AC-16 | Synthetic collector cases produce the known counts and expose missing/ambiguous evidence instead of reporting false zero usage. |

Use deterministic clocks and synthetic source/host fixtures for lifecycle
tests, including simulated suspension and clock correction, without network
inference or real sleeps. Use cheap commands rather than full check walks
to exercise completion. Item 1 also requires a bounded live Windows core
sleep/resume check with a synthetic source and host before claiming core
recovery support. Retain it separately from awake-machine A/B measurements;
later adapter items remain responsible for their host-specific recovery
support evidence.

Keep harness/collector scripts, exact invocations, relevant redacted
configuration and compact reports beside the effort documents. Reference
local raw evidence without publishing full rollouts or credentials. Record
registration, arming, normal turn end, source readiness, send/receipt and
consumption timestamps and report unknown request coverage explicitly.

## Existing code and workflow references for shared waits

These references come from the associated drafts. They identify existing
authorities and constraints, not a file-by-file implementation plan.

- [Groundhog lifecycle authority](../../tools/groundhog/status.py): the
  existing run-state and lost-run semantics for the later check source.
- [Groundhog worker](../../tools/groundhog/runner.py): ordinary process
  waiting and worker completion.
- [Exact exchange waiter](../../tools/review_exchange_wait.py) and
  [review CLI parser](../../tools/review_exchange_cli_parser.py): bounded
  waits, internal checks and progress behavior to preserve at the boundary.
- [Review-request waiter](../../tools/review_resume_wait.py) and
  [notification helper](../../tools/review_resume_notifications.py):
  authoritative rescans, subscription-before-scan and notification fallback.
- [Review workflow authority](../../instructions/review-requestor.md):
  independent roles, ownership and human gates.
- [Groundhog instructions](../../instructions/groundhog.md),
  [generated initialization guidance](../../tools/groundhog/init_files.py)
  and [reporting guidance](../../tools/groundhog/reporting.py): later item 7
  must migrate emitted polling instructions consistently.
- [Command execution rules](../../rules/run_commands.md): shared launchers,
  Python environment resolution and standalone PowerShell scripts.

## Requirement clarifications

The user confirmed consolidation after specification review round 2. These
17 decisions are integrated above; no requirement question remains open.
Concrete storage, IPC transport, wire schema and bound values belong to
design within these confirmed constraints.

| Question | Decision | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | Close item 1 with core fixtures, collector, prototype reports, per-host findings and a live synthetic Windows recovery check; reserve A/B-service for item 8 to avoid dependence on later adapters. | SW-08, SW-09, AC-14, AC-15 and live recovery evidence | Gating item 1 on a production adapter or service comparison creates a circular dependency. |
| Q02 | Accept functional wake and core evidence separately when coverage is inconclusive; retain the strict zero-inference criterion and support claim as open item 8 obligations to avoid false passes. | SW-08, SW-11 and AC-02 | Blocking all core work on complete telemetry; treating missing coverage as proof of zero inference. |
| Q03 | Predeclare finite wake and duplicate-observation bounds for each host/version series; changed bounds start a new series with earlier results retained, making pass/fail interpretation reproducible. | SW-10 and AC-15 | One universal bound for all hosts; reporting timings without declared acceptance bounds. |
| Q04 | Require quiet behavior and useful continuation and report all overhead; no minimum net token savings is promised because measured end-to-end results may be unfavorable. | SW-09 and AC-15 | A required median net reduction would confuse the behavioral contract with a cost prediction. |
| Q05 | Reject registration unless it specifies either a finite deadline or an explicit indefinite policy, creating no wait on rejection, so lifetime is intentional. | SW-02 and AC-01 | Implicit indefinite waits or an undocumented default finite deadline. |
| Q06 | For a pending wait, source completion at/before the UTC deadline wins; absent or later completion expires after it. Record clock uncertainty and preserve terminal state to make recovery independent of observation order. | SW-05 and AC-07, AC-09, AC-10 | Readiness always wins; expiry determined only by service observation time. |
| Q07 | Atomically check durable cancellation when consuming in ordinary code; classify unavoidable queued cancellation-induced wakes and preserve existing semantics after consumption. | SW-04 and AC-07, AC-11 | Promising to revoke every accepted wake; allowing queued events to authorize continuation despite cancellation. |
| Q08 | Permit host-side rearming for the same verified session and valid ownership; require explicit local user action and workflow authority for a different recipient, keeping unverifiable bindings pending. | SW-03, SW-05 and AC-06, AC-11 | Human intervention on every reconnect; prohibiting all rebinding or silently replacing a conversation. |
| Q09 | Identical retries return the existing wait and acknowledgement state; conflicting idempotency-key reuse returns a typed conflict without mutation, preventing silent intent changes. | SW-02 and AC-01 | Silently returning an unrelated existing wait or replacing it with the conflicting request. |
| Q10 | Use a bounded recovery interval fixed per source kind before registration; unresolved access loss yields one typed monitoring failure while underlying work remains independent. | SW-06, SW-07 and AC-04, AC-13 | Immediate termination for every access failure; indefinite source retries. |
| Q11 | Bound attempts for unchanged failures per host route kind; retain events and resume only after explicit local retry or validated recovery, limiting repeated failed delivery. | SW-03, SW-07 and AC-05, AC-13 | Endless retry cadence; discarding the result or requiring a new wait after the first failure. |
| Q12 | Exclude active and ready-but-unconsumed records from automatic terminal cleanup; expose state and age and require explicit lifecycle actions, preserving undelivered work without keeping all terminal records forever. | SW-06 and AC-12 | Age-based deletion of all records; permanent retention of every record. |
| Q13 | Keep and count attributable post-seed compaction in either arm as an observed treatment effect; repeat only actual seed/configuration mismatch or invalid telemetry, retaining all evidence. | SW-10, SW-11 and AC-15, AC-16 | Excluding all compaction trials or changing configuration mid-series to hide their cost. |
| Q14 | Retain the outcome but report missing, replaced or wrong-generation required details as typed unavailable/invalid; suppress dependent continuation pending validation or explicit resolution. | SW-03 and AC-05, AC-13 | Continuing from a summary when authoritative details are required; automatically rerunning the underlying work. |
| Q15 | Cancellation durable before consumption suppresses continuation regardless of source chronology; preserve source evidence and terminal state, with SW-05 resolving readiness versus expiry. | SW-04, SW-05 and AC-07, AC-11 | Earlier source readiness overriding cancellation; service observation/commit order deciding readiness versus deadline after recovery. |
| Q16 | Use current-OS-user local IPC authority, recorded registrant provenance, exact workflow validation and fixed-template typed events for the initial Windows scope; deny foreign users. | SW-02, SW-04, SW-06 and AC-08, AC-12 | Requiring an unproven per-session capability now; leaving the local trust boundary unspecified until design. |
| Q17 | Allow item 1 closure with at least one functionally proven wake route, provisional assumptions for unproven hosts and later per-host revalidation. If none passes, require a human checkpoint before interface freezing or closure while independent core/collector work proceeds. | SW-08, SW-09 and AC-02, AC-14, AC-15 | Requiring Codex alone to pass; unconditionally closing item 1 with entirely provisional wake support. |
