# Run one durable monitoring service

<!-- markdownlint-disable MD013 -->

- Type: feature-request
- Target version: v0.13.0
- Topic: `shared-wait-service`
- Status: requirement written; specification review pending
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
with an explicit pending/unavailable route state. Rebinding requires a
defined ownership and session-resume policy; it must not silently create a
replacement conversation or worker.

### SW-04: Preserve cancellation and review authority

Cancelling a wait suppresses future automatic continuation for that
registration. It must not cancel healthy underlying work or alter a review
exchange. Define deterministic ordering for cancellation, readiness and
expiry races, including events first discovered together during recovery.

Machine events provide information, not human approval or new permissions,
even when the host represents them as user messages. Validate the
registration before continuing an already authorized workflow.

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

When readiness, expiry and cancellation are first observed together, apply
the documented lifecycle ordering and retain available timestamps and
uncertainty. The resume timestamp alone does not establish causal order.
Keep stale routes pending, reconcile unacknowledged delivery by event
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
appropriate local user/session access control. Provide ordinary local status
tools for pending waits, failures and unsupported capabilities without model
inference. Do not store copies of conversation context in the service.

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
failed, capability unavailable or measurement inconclusive. Resolve a failed
route before depending on it; unavailable or inconclusive routes cannot
justify freezing unproven interface assumptions. Independent synthetic core
work may proceed. Probe evidence does not complete a production adapter item.

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
Repeat fresh matched A versus B-service trials when the core and relevant
host route are available. Never relabel prototype evidence as service
evidence; identify the actual service instance and registration/delivery
records for B-service. Item 8 reuses this methodology for the final comparison.

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
runs. Report auxiliary usage separately and unknown attribution explicitly.

Run sequentially with no unrelated work in the measured conversation.
Select telemetry by exact thread identity regardless of other repository
sessions. Keep the machine awake for baseline comparisons; retain and repeat
pairs affected by suspension or clock discontinuity. Resume tests provide
separate recovery evidence.

Create each unique run manifest in ordinary code after `READY` and before
the benchmark prompt. Record run/pair/arm identity, exact thread and storage,
seed hashes, configuration, source identity and pre-start counters/file
positions. Observe these distinct boundaries:

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
| AC-01 | A successful registration persists once and confirms an armed usable route; retries do not duplicate the logical wait. |
| AC-02 | A normally completed registering turn leaves no pending foreground wait; the supported ten-minute baseline has no wait-induced inference and automatically continues the same conversation on readiness. |
| AC-03 | Completion before registration, arming or turn end remains deliverable without another source event. |
| AC-04 | Duplicate/missed notifications and several subscribers use authoritative reconciliation and coalesced watches without cross-repository or cross-session delivery. |
| AC-05 | Outcomes survive restart and persist before delivery; lost acknowledgements retain event identity and do not repeat consumed workflow work. |
| AC-06 | Busy, interrupted, closed and stale host routes preserve recipient, ownership and pending-result state without a new worker or conversation. |
| AC-07 | Cancellation/readiness/expiry races follow documented ordering; cancelling monitoring leaves underlying authorized work intact. |
| AC-08 | Synthetic review ownership and provenance cases reject stale/ambiguous authority and never turn machine events into human approval or counterpart creation. |
| AC-09 | Sleep/resume with an unchanged indefinite wait remains quiet; completion or deadline expiry during suspension is reconciled without resetting the deadline. |
| AC-10 | Forward/backward UTC changes and restart honor persisted deadline semantics without reopening terminal waits or reusing raw monotonic timestamps. |
| AC-11 | Queued, consumed or cancelled events retain their state across resume; stale bindings and lost receipts are reconciled without repeated consumed work. |
| AC-12 | Local startup, discovery, access control, compatibility, reconnect, retention, cleanup and diagnostics satisfy the shared user-owned lifecycle without model health checks. |
| AC-13 | Capability failures are typed and fallbacks explicit; unavailable automatic delivery is never reported as an armed wake. |
| AC-14 | The Codex and available Claude probes retain exact version/session, timing, arming, delivery, consumption and request-coverage evidence with explicit outcomes and limitations. |
| AC-15 | A/B-prototype and subsequent A/B-service reports follow SW-09 through SW-11, retain unsuccessful/inconclusive trials and distinguish all phases and evidence sources. |
| AC-16 | Synthetic collector cases produce the known counts and expose missing/ambiguous evidence instead of reporting false zero usage. |

Use deterministic clocks and synthetic source/host fixtures for lifecycle
tests, including simulated suspension and clock correction, without network
inference or real sleeps. Use cheap commands rather than full check walks
to exercise completion. A bounded live Windows sleep/resume check is
required before claiming that recovery behavior is supported; retain it
separately from awake-machine A/B measurements.

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

## Open questions for the v0.13.0 shared-wait-service feature request

The answer lines below are proposed recommendations for review, not recorded
human decisions. This review clarifies behavior and acceptance; storage,
transport and wire-schema choices belong to the design stage.

### Q01: Completion boundary for umbrella item 1

SW-09 and AC-15 require later B-service evidence, but production host routes belong to items that depend on item 1. Which evidence is required to close this core item?

#### BBQ for Q01

A kitchen foundation can be accepted before every appliance is connected, but the later cooking check still needs an owner. In this picture: the foundation is the shared core, appliances are production host adapters, and the cooking check is the actual-service A/B comparison.

#### Options for Q01

- Option A: Close item 1 with its core fixtures, collector, prototype reports, explicit native-probe findings and live Windows core recovery check, subject to Q02 and Q17; make B-service comparisons item 8 acceptance evidence.
  - Pro: Avoids a circular dependency and keeps service evidence mandatory.
  - Con: Item 1 completion alone cannot mean full live service support.
- Option B: Require a usable actual-service host route and B-service comparison before item 1 closes.
  - Pro: Produces earlier integrated evidence.
  - Con: Pulls host work into item 1 and needs an explicit boundary change.

#### Recommended option for Q01

Option A: Use separate core and production-support gates. Item 1 includes a bounded live Windows sleep/resume check of the core with synthetic source and host fixtures; this does not require a production adapter. Item 8 owns the actual-service comparison. Q02 controls incomplete request coverage and Q17 controls closure when native routes are unproven.

#### Answer to Q01: option A

Option A: Subject to Q02 and Q17, item 1 closes with its synthetic core fixtures, validated collector, A versus B-prototype reports, explicit per-host native-probe findings, and a bounded live Windows sleep/resume check of the core service using synthetic source and host fixtures. A versus B-service trials become named acceptance evidence for item 8, run against the first available production host route. Item 1 validation lists that evidence as outstanding and never reports prototype results as service results. Consolidation edits SW-09 and AC-15 to this split and clarifies that the bounded live Windows sleep/resume check described after the acceptance table stays in item 1. Later adapter items retain their own host support obligations.

### Q02: Acceptance when request telemetry is incomplete

SW-08 permits an inconclusive measurement while AC-02 asks for verified zero wait-induced inference. What can be accepted when automatic continuation works but actual request coverage cannot be established?

#### BBQ for Q02

Seeing a barbecue finish does not prove how much fuel it used when the meter is broken. In this picture: cooking completion is the observed host wake, the fuel meter is request telemetry, and fuel use is quiet-wait inference.

#### Options for Q02

- Option A: Accept the observed wake finding and independent core fixtures only; leave strict no-inference validation and that support claim open.
  - Pro: Preserves useful evidence without making a false zero claim.
  - Con: A working route may remain only provisionally documented.
- Option B: Block completion of all core work until full request telemetry is available.
  - Pro: Gives one simple completion rule.
  - Con: Makes unrelated core acceptance depend on host observability.

#### Recommended option for Q02

Option A: Keep wake evidence separate from request-coverage evidence and identify the unresolved strict criterion explicitly. Useful core and functional wake evidence can be accepted without claiming verified zero inference.

#### Answer to Q02: option A

Option A: Keep wake evidence separate from request-coverage evidence. Consolidation rewrites AC-02 so a run with verified coverage must show no wait-induced inference, while a run with unverifiable coverage is recorded as "wake observed, coverage inconclusive". In the latter case the strict criterion and support claim stay open and are carried to item 8, without invalidating independent core fixtures. This does not weaken the no-inference requirement or turn an inconclusive result into a pass.

### Q03: Wake and duplicate-observation acceptance windows

The draft requires bounded, predeclared delivery and duplicate-observation windows but supplies no acceptance durations. How should a trial's timing contract be settled?

#### BBQ for Q03

Guests need to know when dinner is late before it starts, rather than after it arrives. In this picture: dinner is the delivered outcome, the promised serving window is the wake bound, and waiting after serving is the duplicate-observation window.

#### Options for Q03

- Option A: Declare finite bounds once per host and version comparison series, before its first trial; report misses as failed timing criteria and start a new series if bounds change.
  - Pro: Accommodates measured host behavior while preventing retrospective thresholds.
  - Con: Different host reports need their bounds shown to be comparable.
- Option B: Require one fixed pair of bounds for every host before any trial.
  - Pro: Makes results easy to compare.
  - Con: A universal bound may reject a usable native host route.
- Option C: Report timings without a pass/fail bound.
  - Pro: Avoids an arbitrary initial threshold.
  - Con: Does not establish bounded usable continuation.

#### Recommended option for Q03

Option A: Fix host-specific bounds before the first trial in the whole comparison series, so earlier pair results cannot influence later acceptance thresholds.

#### Answer to Q03: option A

Option A: Declare finite wake and duplicate-observation bounds once per host and version comparison series in its manifest, before its first trial. Changing a bound starts a new series; earlier trials and their misses are retained and reported. Consolidation makes this series boundary explicit in SW-10 and the comparative evidence accepted under AC-15.

### Q04: Required level of measured token savings

SW-09 through SW-11 require comparative costs, but no minimum end-to-end reduction is specified. Does a valid zero-polling route fail if setup makes a four-minute trial more expensive overall?

#### BBQ for Q04

A fuel-saving oven can cost extra to preheat for a short meal. In this picture: preheating is registration/setup, cooking is the wait, and total fuel is end-to-end input usage.

#### Options for Q04

- Option A: Require the quiet-wait behavior and successful continuation, and report end-to-end overhead without a minimum savings threshold.
  - Pro: Tests the requested behavior and exposes unfavorable results honestly.
  - Con: A passing implementation may not save tokens on every short task.
- Option B: Require lower median end-to-end input than classic polling in addition to functional criteria.
  - Pro: Makes a cost benefit part of acceptance.
  - Con: Can reject a correct mechanism for workloads dominated by setup.

#### Recommended option for Q04

Option A: The sources promise removal of wait-induced inference and measured cost reporting, not a guaranteed net saving for every duration.

#### Answer to Q04: option A

Option A: The sources promise removal of wait-induced inference and measured cost reporting, not a guaranteed net saving for every duration. An unfavorable end-to-end delta is a reported result, not a failed criterion.

### Q05: Wait policy when a caller omits a deadline

SW-02 requires a finite deadline or explicit indefinite policy, but does not specify whether callers may rely on a default. What should happen when neither is supplied?

#### BBQ for Q05

A cook must know whether to keep a meal warm until collection or discard it at closing time. In this picture: the meal is the wait, collection is source readiness, and closing time is its deadline.

#### Options for Q05

- Option A: Reject registration until the caller supplies a finite deadline or explicitly requests an indefinite wait.
  - Pro: Prevents accidental expiry and accidental endless monitoring.
  - Con: Callers must make one additional policy choice.
- Option B: Default an omitted deadline to an indefinite wait and report that choice.
  - Pro: Keeps registrations simple.
  - Con: An omission can create unwanted persistent waits.
- Option C: Use a documented finite service default.
  - Pro: Bounds unattended waits.
  - Con: A generic timeout may expire legitimate long work.

#### Recommended option for Q05

Option A: An explicit choice preserves the draft's distinction between finite and indefinite waits and makes expiry behavior reviewable.

#### Answer to Q05: option A

Option A: An explicit choice preserves the draft's distinction between finite and indefinite waits and makes expiry behavior reviewable.

Acceptance impact: Extend AC-01 to require that registration without a finite deadline or explicit indefinite policy returns a typed validation error and creates no wait record.

### Q06: Ordering readiness and expiry after suspension

SW-05 fixes UTC deadline semantics but leaves event precedence unresolved. If readiness and expiry are first observed together after resume, which terminal outcome wins?

#### BBQ for Q06

An order prepared before closing may still be collected later, while an order with no reliable preparation time is uncertain. In this picture: preparation is authoritative readiness, closing is the persisted deadline, and late collection is resume reconciliation.

#### Options for Q06

- Option A: Readiness wins if the source authority records completion at or before the persisted deadline; otherwise expiry wins once the deadline has passed. An already terminal state stays terminal.
  - Pro: Recognizes completion on time without inventing chronology.
  - Con: A real pre-deadline completion with insufficient evidence may expire.
- Option B: Always give an observed ready result priority over expiry.
  - Pro: Maximizes delivery of completed work.
  - Con: Can accept work that became ready after its deadline.
- Option C: Always expire when the service observes readiness after the deadline.
  - Pro: Provides a simple uniform rule.
  - Con: Rejects proven on-time completion that was only observed late.

#### Recommended option for Q06

Option A: Use the source authority's completion time, rather than service observation time, to recognize proven on-time completion. Apply the expiry rule when that evidence is unavailable and Q15 for cancellation precedence.

#### Answer to Q06: option A

Option A: Readiness wins when the source authority records a completion time at or before the persisted deadline. Expiry wins when the deadline has passed and the source authority records no completion time at or before it, including when it records no completion time at all. When a UTC correction occurred between readiness and observation, record the uncertainty with the outcome. An already terminal state stays terminal; this rule reconciles a still-pending wait. Precedence involving cancellation follows Q15. Consolidation makes the source timestamp, deadline equality and unknown-time cases explicit in SW-05 and AC-07, AC-09 and AC-10.

### Q07: Cancellation after transport acceptance

SW-04 suppresses future automatic continuation, but a host may already have accepted a queued event when cancellation succeeds. What guarantee applies before that event is consumed?

#### BBQ for Q07

Cancelling a meal after the waiter has left may not stop the knock at the door, but it can stop serving the meal. In this picture: the waiter is accepted host delivery, the knock is a model wake, and serving is authorized workflow continuation.

#### Options for Q07

- Option A: Cancellation prevents new service deliveries and continuation not yet consumed; an already accepted event may wake the host, but ordinary code rejects its consumption after cancellation.
  - Pro: Defines a guarantee compatible with hosts that cannot revoke queued events.
  - Con: A late wake can still consume some tokens.
- Option B: Guarantee no host wake after cancellation acknowledgement.
  - Pro: Gives the strongest user-visible cancellation promise.
  - Con: Requires revocation support that the candidate routes have not established.
- Option C: Let every transport-accepted event finish its continuation despite later cancellation.
  - Pro: Avoids a late-consumption race.
  - Con: Weakens the user's ability to cancel work that has not started.

#### Recommended option for Q07

Option A: Make cancellation effective through the ordinary-code consumption operation, with an atomic cancellation check, and report unavoidable accepted-event wakes separately.

#### Answer to Q07: option A

Option A: The consumption operation, in ordinary code, checks durable cancellation atomically with recording consumption and rejects a cancelled wait's event. It must not depend on the model interpreting event text correctly. A wake caused by an already accepted event is reported as a cancellation-induced wake. Once consumption has authorized continuation, later cancellation follows the existing workflow's execution semantics. Consolidation extends AC-07 and AC-11 with a cancellation-before-consumption case and a consumption-before-cancellation case, following Q15.

### Q08: Rebinding after a connection changes

SW-03 and SW-05 preserve results on stale routes and require an explicit rebinding policy. When can a restarted bridge or connection resume automatic delivery?

#### BBQ for Q08

A replacement waiter should serve the same verified table, not whichever table is nearest. In this picture: the waiter is the bridge connection, the table is the registered thread/session, and the table check is ownership validation.

#### Options for Q08

- Option A: Permit rearming for the same verified session/thread and still-valid ownership; require explicit authorized rebinding for a different or unverifiable recipient.
  - Pro: Supports routine reconnects without changing who owns the wait.
  - Con: Some recovered results remain pending until identity can be established.
- Option B: Require a human action after every connection-incarnation change.
  - Pro: Makes every rearm explicit.
  - Con: Turns ordinary bridge recovery into repeated manual work.
- Option C: Never rebind an existing registration; require cancellation and a new wait.
  - Pro: Simplifies the external lifecycle.
  - Con: Makes retained-result recovery cumbersome.

#### Recommended option for Q08

Option A: Preserve recipient and ownership identity while allowing routine recovery within the already authorized session.

#### Answer to Q08: option A

Option A: Preserve recipient and ownership identity while allowing routine recovery within the already authorized session. A rearm comes from the host side: a bridge reconnecting under the same verified session, or a later turn in that session. The service never wakes a conversation only to ask it to rearm. Explicit rebinding to a different recipient is a local user action through status tooling, still subject to existing workflow authority; an unverifiable recipient remains pending. Consolidation makes host-initiated rearm explicit in SW-03, SW-05 and AC-06/AC-11.

### Q09: Conflicting reuse of a registration idempotency key

SW-02 says retries create one logical wait. What happens if a caller reuses the same key with a different source, recipient, deadline or permitted continuation?

#### BBQ for Q09

An order number should not silently switch from one customer's meal to another. In this picture: the order number is the idempotency key, the meal is the source condition, and the customer is the registered recipient.

#### Options for Q09

- Option A: Reject the conflicting registration and preserve the original wait; a changed intent requires a new registration or an explicitly supported lifecycle action.
  - Pro: Prevents accidental retargeting under the appearance of a retry.
  - Con: Callers must distinguish retries from changed requests.
- Option B: Return the existing wait without accepting any changed fields.
  - Pro: Keeps retry handling simple and preserves existing state.
  - Con: Can hide a caller error unless the conflict is also reported.
- Option C: Replace the original wait's fields.
  - Pro: Allows convenient correction.
  - Con: Can redirect pending delivery or erase the original authorization.

#### Recommended option for Q09

Option A: A retry must mean the same logical request; explicit rejection protects the original registration and exposes mismatched intent.

#### Answer to Q09: option A

Option A: An identical retry returns the existing wait and its acknowledgement state. A retry that reuses the key with a different source, recipient, deadline or continuation is rejected with a typed conflict naming the existing wait, and nothing changes. A changed intent requires a new registration or an explicitly supported lifecycle action.

Acceptance impact: Extend AC-01 with identical-retry and conflicting-key cases, checking the returned identity and acknowledgement state, typed conflict, and unchanged original registration.

### Q10: Temporary loss of authoritative source access

The core treats notifications as hints and preserves typed outcomes, but source reads may temporarily fail after registration. When does that become an operational outcome?

#### BBQ for Q10

A closed kitchen hatch does not prove the food is ready or ruined. In this picture: the hatch is source access, the food is underlying work, and asking again is code-only reconciliation.

#### Options for Q10

- Option A: Keep source readiness unknown during a bounded declared recovery interval; then record a typed monitoring failure if access is not restored, without declaring underlying work failed.
  - Pro: Tolerates transient faults while bounding an unusable monitor.
  - Con: Outcome delivery can be delayed by the recovery interval.
- Option B: Immediately terminate the wait with a monitoring failure on the first unavailable read.
  - Pro: Reports loss of monitoring promptly.
  - Con: Turns brief filesystem or connection issues into failed waits.
- Option C: Retry indefinitely whenever the wait has no deadline.
  - Pro: May recover after arbitrarily long outages.
  - Con: Can leave a broken registration appearing usable indefinitely.

#### Recommended option for Q10

Option A: Distinguish monitoring failure from work failure and make recovery bounded and observable without model-driven retries.

#### Answer to Q10: option A

Option A: Distinguish monitoring failure from work failure and make recovery bounded and observable without model-driven retries. The recovery interval is declared per source kind, before any wait of that kind is registered. If access remains unavailable when it lapses, record one typed monitoring-failure outcome and deliver it like any other actionable outcome, subject to Q11. Never report the underlying work as failed from this monitoring failure.

Acceptance impact: Extend AC-04 and AC-13 with transient recovery and exhausted-recovery fixtures that check the declared bound, one monitoring-failure outcome, normal delivery handling, and no false work-failure report.

### Q11: Automatic retries after a persistent delivery failure

SW-03 and SW-07 retain unavailable delivery and forbid polling loops, but do not state when repeated automatic attempts should stop or how recovery re-enables them.

#### BBQ for Q11

Repeatedly ringing a broken doorbell does not deliver dinner. In this picture: the doorbell is the host route, ringing is a delivery attempt, and a repaired connection is a validated capability change.

#### Options for Q11

- Option A: Bound automatic attempts for the same unchanged failure, retain the result and route diagnostic, and resume attempts only after explicit retry or a validated recovery event.
  - Pro: Avoids endless retries and recurring failure wakes while preserving results.
  - Con: Some waits require a later recovery trigger or manual retry.
- Option B: Continue code-only retries indefinitely at a bounded cadence.
  - Pro: Can recover without an explicit trigger.
  - Con: Sustains background activity and can repeatedly exercise a broken route.
- Option C: Treat the first delivery failure as permanent and require a new wait.
  - Pro: Provides simple failure semantics.
  - Con: Loses convenient recovery of transient host failures.

#### Recommended option for Q11

Option A: Bound recovery for one unchanged failure and preserve the durable event so a validated route recovery can continue the same logical wait.

#### Answer to Q11: option A

Option A: Declare the automatic-attempt bound per host route kind. Bound automatic attempts for one unchanged failure and preserve the durable event and route diagnostic, so validated route recovery can continue the same logical wait. A validated recovery event includes a same-session rearm under Q08. An explicit retry is a local tool action, never a model-driven loop.

Acceptance impact: Extend AC-05 and AC-13 to verify that attempts stop at the declared bound for an unchanged failure, the result remains available, and an explicit retry or verified recovery resumes delivery with the same event identity.

### Q12: Retention of unconsumed outcomes

SW-06 requires retention and cleanup without specifying which records may expire automatically. Can a cleanup policy remove an active wait or a ready outcome that its recipient has not consumed?

#### BBQ for Q12

Clearing empty plates is different from throwing away a meal still awaiting collection. In this picture: empty plates are consumed terminal records, the waiting meal is an unconsumed result, and clearing is retention cleanup.

#### Options for Q12

- Option A: Exclude active waits and ready unconsumed outcomes from automatic terminal-record cleanup; remove them only through an explicit cancellation/expiry or other documented lifecycle action.
  - Pro: Protects the durable recovery promise.
  - Con: Long-abandoned waits may retain data until explicitly resolved.
- Option B: Apply a disclosed retention age to all records, including pending and unconsumed waits.
  - Pro: Bounds storage even for abandoned registrations.
  - Con: Can remove a result before the promised recipient resumes.
- Option C: Retain all records indefinitely.
  - Pro: Maximizes historical recovery.
  - Con: Leaves storage and data lifetime unbounded.

#### Recommended option for Q12

Option A: Separate lifecycle changes from housekeeping and document retention of consumed/cancelled terminal records without silently deleting deliverable outcomes.

#### Answer to Q12: option A

Option A: Exclude active waits and ready unconsumed outcomes from automatic terminal-record cleanup. Separate lifecycle changes from housekeeping and document retention of consumed/cancelled terminal records without silently deleting deliverable outcomes. Local status tooling lists retained pending and unconsumed records with their age, so long-abandoned waits can be resolved explicitly. Cancellation retains any ready outcome as evidence under Q15, subject to the documented terminal-record retention policy.

Acceptance impact: Extend AC-12 with aged active, ready-unconsumed and consumed/cancelled fixtures, verifying housekeeping exclusions, age visibility, and cleanup only when the documented lifecycle and retention conditions permit it.

### Q13: Compaction caused by the measured polling arm

SW-10 records compaction and repeats materially unmatched pairs. If A's natural extra context causes compaction after equivalent seeding, is that a protocol deviation or part of its measured cost?

#### BBQ for Q13

A crowded kitchen may need an extra cleanup because one recipe uses more dishes. In this picture: dishes are accumulated context, cleanup is compaction, and the recipe is the polling mechanism.

#### Options for Q13

- Option A: Retain and count post-seed compaction caused by the arm as measured behavior when attribution remains valid; repeat for seed mismatch, configuration drift or unusable telemetry.
  - Pro: Preserves the cost of A's natural context growth.
  - Con: Reports must distinguish valid treatment effects from invalid comparisons.
- Option B: Exclude and repeat every pair with any compaction.
  - Pro: Produces a simpler comparison without compaction effects.
  - Con: Can selectively remove a real cost of repeated polling.
- Option C: Prevent compaction by changing settings during affected trials.
  - Pro: Avoids interrupted accounting.
  - Con: Breaks the matched configuration and changes the workload.

#### Recommended option for Q13

Option A: The protocol explicitly retains A's natural context growth; its attributable compaction belongs in the result unless a genuine matching or evidence failure invalidates the pair.

#### Answer to Q13: option A

Option A: The protocol explicitly retains A's natural context growth; its attributable compaction belongs in the result unless a genuine matching or evidence failure invalidates the pair. Apply the same attribution rule to any compaction in a B arm. Consolidation clarifies SW-10 without changing the equivalent starting-context controls.

### Q14: A ready result reference becomes unavailable

SW-03 persists bounded outcomes and a reference to authoritative details. What must happen if those details disappear or no longer validate the registered source generation before consumption?

#### BBQ for Q14

A collection ticket cannot authorize serving a different meal when the original has gone missing. In this picture: the ticket is the event and result reference, the meal is the authoritative source outcome, and collection is workflow consumption.

#### Options for Q14

- Option A: Retain the recorded outcome but report unavailable or invalid details; suppress dependent continuation until the registered result can be validated or the wait is explicitly resolved.
  - Pro: Prevents acting on replacement or unverifiable source content.
  - Con: A source-complete wait may still need manual resolution.
- Option B: Proceed using only the persisted summary even when the permitted continuation requires missing details.
  - Pro: Keeps automatic continuation moving.
  - Con: May execute work without the evidence the workflow requires.
- Option C: Automatically rerun underlying work to recreate the result.
  - Pro: Can recover a readable artifact.
  - Con: Risks duplicate work and exceeds monitoring authority.

#### Recommended option for Q14

Option A: Durable notification must preserve exact source identity and existing workflow validation; it cannot authorize a substitute result or a new underlying run.

#### Answer to Q14: option A

Option A: Durable notification must preserve exact source identity and existing workflow validation; it cannot authorize a substitute result or a new underlying run.

Acceptance impact: Extend AC-05 and AC-13 with a synthetic case that removes or changes the referenced details before consumption; retain the outcome, report a typed unavailable or invalid state, and suppress dependent continuation until validation or explicit resolution.

### Q15: Precedence among cancellation, readiness and expiry

SW-04 and AC-07 require an ordering for the full cancellation, readiness and expiry race. Q06 resolves readiness versus expiry and Q07 covers an accepted event. Which rule controls a cancellation recorded before workflow consumption?

#### BBQ for Q15

A cancelled meal can remain on the kitchen record without being served. In this picture: preparation is source readiness, the cancellation record is durable cancellation, and serving is workflow consumption.

#### Options for Q15

- Option A: A cancellation durably recorded before consumption suppresses continuation, whether readiness was observed before or after it; retain any ready outcome as evidence. Readiness versus expiry follows Q06.
  - Pro: Gives a predictable cancellation promise that matches Q07.
  - Con: Cancelling just after completion withholds automatic continuation even though the result exists.
- Option B: Let authoritative source chronology decide, with readiness winning over a later cancellation request.
  - Pro: Completed work is not withheld by a later cancellation.
  - Con: A cancellation acknowledgement becomes provisional and can still lead to continuation.
- Option C: Order all three transitions by the service's durable commit sequence.
  - Pro: Gives the service one simple ordering mechanism.
  - Con: Readiness versus expiry can depend on arbitrary observation timing after suspension.

#### Recommended option for Q15

Option A: Make cancellation before consumption decisive for continuation, while preserving source evidence separately and using Q06 for readiness versus expiry.

#### Answer to Q15: option A

Option A: A cancellation durably recorded before consumption suppresses continuation regardless of when readiness was observed. Retain the ready outcome, if any, as evidence visible in status; cancellation does not rewrite source success or reopen an expired/terminal source outcome. Readiness versus expiry follows Q06. The ordinary-code consumption operation orders cancellation against consumption atomically as described in Q07. Cancellation after consumption does not retroactively undo authorized work and follows the existing workflow's execution semantics.

Acceptance impact: Extend SW-04, AC-07 and AC-11 with cancellation before/after readiness, before/after consumption, and readiness/expiry discovered together after suspension. Assert suppression, retained source evidence and the same deterministic ordering after restart.

### Q16: Authority to register, cancel and inspect waits

SW-06 requires local user/session access control, but AC-12 cannot test it without a defined trust boundary. Which local callers may register, cancel, inspect or explicitly rebind a wait addressed to a conversation?

#### BBQ for Q16

Access to the kitchen lets a household member place an order, but does not let a waiter invent the cook's instructions. In this picture: the household is the current OS user, orders are typed registrations, and the cook's instructions are existing workflow authority.

#### Options for Q16

- Option A: In the initial local Windows scope, trust current-user processes at the IPC boundary; allow them to register exactly identified recipients and cancel or inspect waits, while retaining workflow and role restrictions. Render events from typed fields and fixed continuation kinds.
  - Pro: Establishes a concrete local boundary without assuming an unproven per-host session secret.
  - Con: A same-user process can address another conversation owned by that user; this boundary does not isolate mutually untrusted same-user processes.
- Option B: Require a session-held capability issued by arming for registration, cancellation or retargeting, with a local user recovery path.
  - Pro: Narrows who can address an individual conversation.
  - Con: Depends on a host proof-of-possession mechanism that the probes have not established.
- Option C: Leave the trust boundary to design.
  - Pro: Allows design to select the boundary after investigating hosts.
  - Con: Leaves the access-control acceptance criterion undefined.

#### Recommended option for Q16

Option A: Specify the current OS user as the initial IPC trust boundary and record option B as later hardening if host probes establish a suitable session-held capability. This chooses the boundary, not an IPC mechanism.

#### Answer to Q16: option A

Option A: The IPC endpoint accepts only the current user. Current-user processes may register waits for exactly identified sessions and may cancel or inspect waits. A registration made by a process other than the recipient session records that provenance, and the SW-04 validation in the woken conversation sees it. A different-recipient rebind requires the explicit local user action in Q08. This OS access boundary does not grant workflow permission: exact ownership validation and the prohibition on a requestor or reviewer registering, creating or directly waking its counterpart in SW-04 still apply. Events are rendered by the service from typed fields and fixed continuation kinds, never from source or registrant free text. Per-session capabilities remain a later hardening candidate if probes establish support; no such support is claimed now.

Acceptance impact: Extend SW-02, SW-06 and AC-08/AC-12 with current-user access, rejected foreign-user access, exact-recipient validation, prohibited counterpart action, and rejection of arbitrary continuation text. Keep existing workflow capability and human-decision checks intact.

### Q17: Item 1 outcome when native wake probes fail

SW-08 permits useful synthetic work while a route is unresolved, but does not define item 1 closure if the primary Codex route fails and Claude is unavailable or inconclusive. What evidence must exist before freezing the host interface or closing this core item?

#### BBQ for Q17

A kitchen can test its order book before a waiter is hired, but should not finalize a serving hatch that no waiter can use. In this picture: the order book is the core, the hatch is the host interface, and a working waiter is an observed native wake route.

#### Options for Q17

- Option A: Continue with at least one passing native wake route and explicit revalidation obligations for unproven hosts; if none passes, stop at a human checkpoint before freezing the host interface or closing item 1.
  - Pro: Preserves useful synthetic progress without settling an interface around a wholly unproven wake model.
  - Con: Requires a human scope decision when no route can be established.
- Option B: Block item 1 closure until the primary Codex route passes.
  - Pro: Proves the primary intended route before closure.
  - Con: A Codex-specific failure blocks a core that another supported host could validate.
- Option C: Always close with a provisional host interface, regardless of probe results.
  - Pro: Avoids a host-dependent closure delay.
  - Con: Can settle a core around a wake model no host supports.

#### Recommended option for Q17

Option A: Require at least one observed usable native wake route for automatic closure, preserving provisional assumptions and named host-specific revalidation. With no passing route, leave a human checkpoint before the interface or item is declared settled.

#### Answer to Q17: option A

Option A: When at least one native route proves the functional sequence of arming, normal turn completion, quiet waiting and automatic same-conversation continuation, item 1 may proceed toward closure under Q01. Unproven host assumptions remain provisional and require revalidation in the first adapter item for each host. Q02 independently governs request-coverage proof: a functional wake pass is not a verified zero-inference claim. If no route passes, useful synthetic core and collector work may proceed without depending on the failed route, but stop at a human checkpoint before freezing the host interface or closing item 1. Record every failed, unavailable or inconclusive route and the unresolved feasibility decision; do not silently substitute manual wake or a new conversation.

Acceptance impact: Extend SW-08 and AC-14 to distinguish at-least-one-route-passes and no-route-passes outcomes, reference the Q01/Q02 evidence split, and name each outstanding obligation under the matching host adapter item. The no-route case leaves item 1 closure open pending a human scope decision.
