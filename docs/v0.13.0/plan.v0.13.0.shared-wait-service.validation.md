# v0.13.0 shared wait service implementation tracking and validation

No, it is not implemented

Track the eight steps in [the implementation plan](plan.v0.13.0.shared-wait-service.md).
Step 1 has been checked against its synthetic collector implementation and test
evidence. Steps 2 through 8 remain pending; this result does not establish native
wake feasibility or service implementation.

## File-based IO cost clarification for the validation record

Verify the plan's explicit identity/index reads, incremental exact-thread telemetry,
coalesced source reconciliation and bounded status output. No registration/status
operation should load conversation context. Source and host I/O stays outside
durable transactions; required validation and SQLite synchronization remain intact.

## Complexity checks for the shared wait implementation

Check direct/indexed lookup and dirty-source/subscriber work, bounded workers
and frames, and active-state recovery. Indexed SQL and scheduler operations may
be logarithmic; avoid per-event whole-repository or whole-history scans. Record
read counts and observed timings where checked, without claiming unit coverage
from live acceptance runs.

## Step 1. Validate standalone telemetry collection

### Analysis of Step 1 implementation state

Yes. Step 1 has been fully implemented.

The explicit-path synthetic collector, accounting rules, immutable snapshots
and paired summaries meet this step's AC-16 scope. Round 1 findings were fixed
with regression tests: stream continuity is checked against the manifest before
the first read, reset snapshots retain replacement content, and unknown request
intervals keep unknown phase costs. The final Groundhog walk on 2026-09-15 at
19:12:30 +02:00 passed 3,018 tests with 100% coverage of its configured source
scope. Native schemas and live wake evidence remain Step 2 work.

### Goal for Step 1

Produce trustworthy exact-thread request and usage evidence before measuring a wake treatment.

### Step 1 improvement expectations

- Known synthetic streams reproduce expected attempts, usage and phase totals; insufficient request evidence can never produce strict zero-inference support. Reports retain raw-evidence references without copying private rollouts.
- Verify bounded collector reads and timeout guards. In test_collector_tdd.py, smoke-test the absolute standalone script from the checkout and another cwd with the verified project interpreter, explicit paths and no manually prepared PYTHONPATH.
- Preserve the plan's scope, line budget and existing workflow behavior.
- Record the targeted Groundhog and full-walk result and the required evidence.

### What was implemented for Step 1

- `tools/wait_evidence/models.py` validates explicit identities, absolute paths,
  pre-start offsets/baselines, stream file identities and bounded fingerprints,
  frozen hashes, arm labels and finite bounds.
  Evidence retains original time, ingestion time and source references.
- `tools/wait_evidence/telemetry.py` normalizes the declared `synthetic-v1`
  schema with exact host/build/thread/profile/source matching. It resumes
  bounded reads, retains partial lines, checks manifest continuity before the
  first read and detects rotation/truncation. A reset freezes its snapshot
  budget against the open replacement file before yielding any records.
  Missing baseline identity and damaged evidence produce distinct gaps.
- `tools/wait_evidence/collector.py` deduplicates attempts and completions,
  reconciles compatible cumulative epochs, preserves unknown token fields,
  correlates nested tool ancestry and separates phase, seed and auxiliary costs.
  Unknown request ends retain unknown phase costs without inventing a crossing.
  Request and usage coverage remain independent. Fake-clock drain checks and
  versioned snapshots cover delayed evidence and clock discontinuities.
- `tools/wait_evidence/reports.py` publishes exclusive output versions and
  retains raw per-trial counts, paired deltas, context controls, medians/ranges
  and unsuccessful/repeated trials. Prototype and service labels stay distinct.
- `collect.shared-wait-service.py` bootstraps imports from its physical script
  location. Bounded subprocess tests exercise it from the checkout and another
  cwd with explicit manifest/output paths and no prepared `PYTHONPATH`.
- Test leaves under `tests/unit/tools/wait_evidence/` cover the planned
  accounting, identity, I/O, correlation and omission cases. Additional
  model/report leaves keep ownership by production module explicit.

The final `ghog day` ran checks, 152 affected tests and the full suite. Its closing
verdict was `fail=0 warn=0 xfail=0 cov=100 outliers=skipped excluded=skipped exit=0`;
`ghog status` confirmed `state=done exit=0`. Static checks took 21.8s and the full
test phase took 2m 20.4s. Before that walk, 125 focused tests passed. The new
regressions first failed on all eight targeted cases before the fixes.
Local evidence is retained in `.reviews/a.step1-round2-final-ghog.log`,
`.reviews/a.step1-round2-tests-first.log`, `.reviews/a.step1-tests-first.log`
and `.reviews/a.step1-environment-result.md`.
Duration-outlier checks were reported as skipped; no outlier result is inferred.
The plan's coverage/arm contract search and affected source diff were inspected.

### New types or classes introduced for Step 1

- `Arm`, `Phase`, `StreamSpec`, `TrialManifest`, `EvidenceRecord`,
  `CoverageAssessment` and `TrialReport` define measurement contracts.
- `Telemetry` and its private `_Cursor` own parsing and bounded file state.
- `Collector`, `_Snapshot` and `_Drain` own accounting and elapsed drain state.
- `JsonValue`, `JsonObject` and `Usage` keep boundary data and unknown counters
  explicit in type checking.

### Architecture check for Step 1

Parsing/file access lives in `telemetry.py`; collection and phase accounting
consume normalized records without opening files. `reports.py` owns publication
and CLI wiring. The effort script only locates code and invokes that entry
point. No service authority, review workflow or host lifecycle dependency was
introduced into the accounting layer.

Physical lines were recounted, including blanks: models 312, telemetry 195,
collector 547, reports 183, package initializer 10 and effort CLI 15. All test
initializers have 3 lines. Collector test leaves have 221, 47, 259 and 133 lines;
telemetry leaves have 86 and 216; model/report leaves have 89 and 177. Every
file is below the 550 growth-assessment band and the mandatory 650 ceiling.
No architecture, responsibility or size issue needs fixing.

### Performance check for Step 1

Ingestion uses identity dictionaries. Snapshot accounting and tool ancestry
resolution use linear scans with cached owner results; pair grouping uses
direct keys. Median selection sorts only fixed groups of at most five elements,
so it does not introduce an input-sized O(n log n) sort or pairwise O(n²) work.
Snapshot reads consume a fixed initial byte budget with bounded chunks and
partial-line storage. Baseline verification hashes at most 4 KiB ending at the
recorded offset, with each read bounded by the configured chunk size.
Instrumented tests observe actual read sizes and resumed seek offsets.
Append-during-snapshot tests prove the budget stays fixed, including after a
rotation or truncation resets the cursor.

Tests use injected clock observations without real sleeps or model calls.
Subprocess smoke tests retain five-second subprocess bounds and ten-second
pytest guards; isolated Python startup avoids unrelated site initialization.
No performance issue needs addressing.

### Unit test coverage check for Step 1

`pyproject.toml` measures `source = ["tools"]` with a 100% gate, omitting tests,
initializers and the configured existing adapter exceptions. The four new
production modules are inside that scope. Their owning `test_models`,
`test_telemetry`, `test_collector` and `test_reports` folders exercise validation,
parsing, accounting, diagnostics, CLI errors and summary behavior. The full
walk reached 100%; static inspection finds no remaining uncovered class work.
Property tests permute duplicate arrivals and independently omit coverage.

The effort-side CLI is outside that percentage. It defines no new top-level
function or class, delegates to tested `reports.main`, and is exercised by the
two actual subprocess smoke cases. Initializers contain imports or docstrings.
No unit-tested class below 100% needs completing. No top-level symbol outside
the coverage gate is unreferenced.

### Feature integrity for Step 1

The new package is opt-in and changes no existing execution or review route.
Incomplete or conflicting evidence prevents a strict zero-inference claim;
seed/auxiliary costs and post-observation requests remain separate from the
primary measurement. Unknown native schemas remain explicit gaps.

Validation also repaired Markdown formatting in the validation/review documents
and supplied the existing effort-discovery explanation's required invocation
model section. Those documentation repairs are grouped separately from the
collector. No existing behavior or reporting capability was found impaired.

## Step 2. Run the minimal native-wake prototype and matched trials

### Analysis of Step 2 implementation state

Yes. Step 2 has been fully implemented.

The native-wake harness, host adapters and independent observers passed the
automated gates. Both available hosts have a retained controlled baseline and
three matched pairs, with all original failures and deviations preserved.
Codex B1/B2/B3 passed with B2 observer recovery retained. Claude B2/B3 passed
after the exact native-ancestry repair; Claude B1 remains failed without retry.
All Claude A trials passed functionally with the unavailable initial-yield
parameter recorded. The final Claude integrity audit and closure check passed.
Request accounting remains unknown; functional wake and lower observed usage
do not establish strict idle, quota savings or billing savings.

| Step 2 completion component | Checked state | Evidence |
| --- | --- | --- |
| Code complete | Yes | Exact B1 regression, 39 focused checks, 10 affected checks and 3,198 full tests at 100% configured coverage; final walk ended 2026-09-17 07:47:09 UTC, `state=done exit=0`; validated implementation and log hashes remain unchanged |
| Live evidence recorded | Yes, including failed and qualified cases | Both controlled baselines and three pairs per host audited; Claude baseline/A1/B2/A2/A3/B3 passed 25/26/37/29/29/37 independent checks; B1's failed audit remains retained; full observation windows verified for each passing case |
| Gate for Steps 3 through 7 | Functional route demonstrated and Step 2 evidence complete | Passing controlled Codex and Claude cases prove automatic useful continuation; no subsequent service work has started |

The human started and seeded each measured conversation and submitted each
benchmark prompt after observer readiness. Native normal completion gates the
B routes; no operator marker substitutes for native evidence. The original
Claude seeds and exact session identities survived resume unchanged. Pair
context differences are 3.891155%, 0.967780% and 0.583372%, within 5%.
The final audit verifies serial execution, original manifests, retained hashes,
one thread claim per run and no post-observation activity or invalidation.
All seven Claude tabs may now be closed. These are prototype results; host
interfaces need revalidation in their later production adapter items.

The independent Step 2 review confirmed implementation and live-evidence
completion, then requested transcript Markdown repairs, dependency documentation
and EOF sentinels in both docs-side Claude helpers. Those repairs are staged,
with the review transcript assigned its own commit group. A fresh forced
Groundhog walk passed all checks, affected tests and all 3,198 full tests at
100% configured coverage, with zero failures, warnings or xfails, ending
`2026-09-17T13:32:15+02:00`. Its retained log is
`.reviews/a.step2-r1-repair-ghog.log`, SHA-256
`9919dc025ad161de51f243622e5bc5666ee48b5934c8bb1f2d029f0923e45f73`.
The original live-series validation log and all frozen measurements remain
unchanged; the new walk validates the review repairs. Review convergence and
the human commit decision remain separate gates.

### Goal for Step 2

Record Codex-first and available Claude feasibility plus matched A/B-prototype evidence before substantial service implementation.

### Step 2 improvement expectations

- Commit reproducible commands, redacted manifests/configuration and compact A/B-prototype results, with all original failures and repeats. At least one functional route is required for item 1 closure. If no route passes, report that finding to the human; do not invent a replacement route.
- Verify the Step 2 extensions of tools/wait_evidence/telemetry.py and tests/unit/tools/wait_evidence/test_telemetry/test_telemetry_tdd.py against redacted installed-version fixtures, preserving unknown coverage for unsupported schemas.
- Check each initial host/version manifest's 60-second wake bound, 120-second duplicate window and separate 120-second telemetry drain. Wake latency ends at first useful continuation; changed bounds start a new series while retaining failures.
- In test_prototype_tdd.py, smoke-test the absolute probe script from the checkout and another cwd with the verified project interpreter and explicit paths, without a manually prepared PYTHONPATH.
- Preserve the plan's scope, line budget and existing workflow behavior.
- Record the targeted Groundhog and full-walk result and the required evidence.

### What was implemented for Step 2

- `pyproject.toml` adds development-only `wsproto>=1.3.2`; `uv.lock` records
  `wsproto 1.3.2` and its `h11 0.16.0` dependency. The Codex proxy needs
  WebSocket framing, which the standard library does not implement. Reusing
  the protocol library avoids maintaining a separate experimental frame
  parser. The service dependency and configured coverage scope are unchanged.
- `tools/wait_evidence/prototype.py` adds an isolated durable SQLite harness for
  exact source/wait/event/thread identities, readiness before normal end,
  interruption suppression, recipient checks, one delivery attempt, uncertain
  receipts without retry, and duplicate useful-consumption rejection. Host I/O
  runs outside the write transaction, with eligibility checked again before
  committing a send intent.
- `probe_driver.py` freezes both complete draft blobs from commit
  `3d4b5a4643d1fba65434877d965d2c051b65e1a3`, records hashes and controls,
  rejects reused or implementing threads and unrelated native files, preserves
  invalid attempts, and publishes each prompt after its manifest. Indexed
  reservations enforce ordering and the 5% pair-context gate.
- `probe_observer.py` combines filesystem notifications and ordinary timers
  with the Step 1 collector. It binds Codex normal completion to the exact
  registering turn and retains complete duplicate and separate drain windows.
  Restart replay preserves first completion times and journal entries.
- `probe_cli.py` and the thin `docs/v0.13.0/probe.shared-wait-service.py` entry
  point provide reproducible preparation, registration, observation, source,
  measurement, status, suppression and consumption operations. Physical paths
  resolve imports independently of the caller's working directory.
- `telemetry.py` and `telemetry_claude.py` normalize inspected Codex `0.154.0`
  and Claude `2.1.272`/`2.1.273` records through the common adapter. Native
  identity/build/home checks, stream roles, repeated usage, metadata, deferred
  tools and native normal-end ancestry retain unknown request completeness.
  `models.py` and `collector.py` preserve native versus synthetic evidence.
- `claude_monitor.py` and `claude_observer.py` implement exact schema/startup
  checks, gated Monitor delivery, exact native receipt, one consumption and
  independent full observation. The B1 repair accepts only the verified
  completed-task child of the ready notification, bound to the same task and
  Monitor call, without changing native turn UUIDs. Ambiguous or unrelated
  notices, duplicate completion notices and missing ancestry are rejected.
  Atomic readiness publication and parser-gap handling have regression coverage.
- The [results](probe-results.v0.13.0.shared-wait-service.md),
  [Codex export](probe-controlled.v0.13.0.shared-wait-service.json),
  [Claude export](probe-claude-controlled.v0.13.0.shared-wait-service.json) and
  [final Claude audit](probe-claude-series-audit.v0.13.0.shared-wait-service.json)
  retain reproducible commands, settings, seed evidence, all outcomes, timing
  gates and three pair comparisons per host. The separate Claude smoke and
  original failures remain available. Failed B1 has no successful consumption
  or final-window gate; elapsed failure observation is not relabelled a pass.
- Additive `monitor-completion-01` revision bindings preserve all original
  manifests, seed/configuration hashes and failed B1 evidence. Both arms in
  pairs 2 and 3 use that validated revision. The final audit verifies the
  current source and full-validation log hashes against it.

### New types or classes introduced for Step 2

- `Route` supplies explicit gate, recipient-status and send callbacks.
- `Prototype` owns the durable synthetic lifecycle; `CodexQueue` adapts the
  inspected app-server proxy and exact-thread queue command.
- `Experiment` owns a frozen series and indexed trial/thread reservations.
- `Observation` coordinates native evidence, prototype state and collection;
  `Changed` selects filesystem notifications for explicit streams.
- `ClaudeTelemetry` holds Claude native ancestry and usage normalization state.
- `ClaudeObservation` specializes the common observer for native Monitor
  registration, gating, continuation and audit evidence.
- `Watch` owns filesystem notification startup, readiness and bounded waiting
  for the ordinary Claude bridge and observer processes.

### Architecture check for Step 2

The experiment remains separate from the later shared service. `Route` injects
host callbacks; native invocation belongs to the Codex and Claude adapters.
Claude normalization uses the common telemetry entry point and shared evidence
models. `ClaudeObservation` composes collection and lifecycle behavior through
the existing observer. No production workflow imports the probe, and no
review counterpart creation or messaging path was added.

All 30 changed Python files are within the 650-line ceiling. The prototype is
248 lines, driver 233, common observer 200, CLI 141, telemetry entry point 347,
Claude telemetry 179, Claude observer 388 and Monitor adapter 173. The existing
collector remains 548 lines. Changed tool modules retain `# eof` sentinels.
Host-status and delivery calls remain outside write transactions; cancellation
during a status call is reread before sending.

No architecture issue needs to be addressed.

### Performance check for Step 2

Native reads advance captured offsets and normalize each new record once.
Parent and continuation identities use keyed state; no pairwise history scan
was introduced by the ancestry repair. Filesystem notifications select exact
paths, with ordinary timers for source and final-window deadlines. Journal
replay is linear at restart. Indexed SQLite reservations and ordinal lookup
avoid rescanning retained trials; the existing 6,000-trial regression retains
its bounded instruction budget. Full seed verification runs once per series.
RPC waits retain their wall-clock bound without holding a SQLite write lock.

No performance issue needs to be addressed.

### Unit test coverage check for Step 2

The final `ghog day` ended at `2026-09-17T09:47:09+02:00`, exit `0`: all static
checks, 10 affected tests and 3,198 full-suite tests passed with 100% configured
coverage and zero failures, warnings or xfails. The exact failure was first
reproduced, then 39 focused checks passed before that full walk. `ghog status`
confirmed `state=done exit=0`; the final audit verified the unchanged validated
source and log hashes. This implementation check uses those results and static
test inspection without rerunning tests.

Unit tests under `tests/unit/tools/wait_evidence/test_prototype/` cover
prototype state, driver validation, native transports and both observers with
fake clocks and transports. Cases include replay, cancellation, lost receipt,
noisy transport deadlines, exact startup/schema, full duplicate/drain windows,
atomic publication, parser gaps and consumption binding. The ten cases in
`test_claude_continuation_tdd.py` exercise the observed adjacent-notification
chain and reject mismatched task/call/status/parent, human origin, duplicate
tags, notices before readiness, duplicate notices and missing turn identity.
Unit telemetry tests cover supported native schemas, metadata, usage deduplication,
normal-end ancestry and unknown completeness. Existing collector/model tests
cover their extensions. No new PBT is needed beyond Step 1 accounting properties.

The coverage gate measures `tools`; tests, initializers, protocols and the
other explicit `pyproject.toml` omissions are excluded. No percentage is claimed
for `docs` probe helpers or excluded initialization code. Static inspection of
every top-level definition in the changed `docs` helpers found a reference
within its own module or from its companion entry point. In particular, all
five helpers in `claude-probe-state.shared-wait-service.py` are referenced by
`claude-probe.shared-wait-service.py`. The thin common probe calls the package
CLI and its bounded smoke exercises checkout and alternate working directories.
The modified package initializer exports types used by the test suite.

No unit-tested class below 100% needs completing. No top-level symbol outside
the configured gate is unreferenced.

### Feature integrity for Step 2

Existing collector reports, accounting properties and workflow behavior remain
covered by the full suite. Probe artifacts use explicit ignored run paths;
provider, permission, approval and telemetry settings remain unchanged. Queue
acceptance alone never certifies useful wake, and operator markers cannot
certify native normal end or complete request coverage. The contract search
and affected diff were inspected. Claude replay covers the seven original
seed transcripts and separate smoke without parser gaps.

Both controlled series retain native evidence independently of deterministic
tests. Codex's B2 recovery, Claude's failed B1, all Claude A protocol deviations,
preparation variation and unknown configuration/accounting fields remain
explicit. All seven Claude observation processes exited and final hashes were
verified before permitting tab closure. No service implementation or umbrella
completion follows from this Step 2 check; Steps 3 through 8 remain unstarted.

## Step 3. Create the durable service model and store

### Analysis of Step 3 implementation state

Not started. Step 3 is not implemented because its planned files, behavior
and acceptance evidence have not yet been delivered or checked.

### Goal for Step 3

Persist exact registrations, immutable outcomes/events and recovery state with transactional acknowledgements.

### Step 3 improvement expectations

- Reopened stores preserve acknowledged registration, outcome and event identities, and injected storage failures return typed unavailable results without resetting the database.
- Preserve the plan's scope, line budget and existing workflow behavior.
- Record the targeted Groundhog and full-walk result and the required evidence.

### What was implemented for Step 3

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 3

_(empty — no check has taken place yet.)_.

### Architecture check for Step 3

_(empty — no check has taken place yet.)_.

### Performance check for Step 3

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 3

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 3

_(empty — no check has taken place yet.)_.

## Step 4. Implement the Windows authority and authenticated pipe

### Analysis of Step 4 implementation state

Not started. Step 4 is not implemented because its planned files, behavior
and acceptance evidence have not yet been delivered or checked.

### Goal for Step 4

Start one hidden process per canonical home and admit only compatible same-user peers.

### Step 4 improvement expectations

- Synthetic peers cannot reach a request handler before identity and compatibility checks; concurrent startup selects one durable authority and honors explicit isolated homes.
- Verify `tests/unit/tools/wait_service/test_windows_ipc/__init__.py` and `test_windows_ipc_tdd.py` exist. Direct native-call error, SID/ACL and handle-cleanup cases must exercise the ctypes adapter within unit coverage; live Windows evidence stays separate.
- Before rollout, omitted/default/aliased-default homes return explicit-home-required before discovery or resource creation. Check bounded startup/pipe resources with deterministic clocks and finite timeout guards.
- Preserve the plan's scope, line budget and existing workflow behavior.
- Record the targeted Groundhog and full-walk result and the required evidence.

### What was implemented for Step 4

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 4

_(empty — no check has taken place yet.)_.

### Architecture check for Step 4

_(empty — no check has taken place yet.)_.

### Performance check for Step 4

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 4

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 4

_(empty — no check has taken place yet.)_.

## Step 5. Wire registration, monitoring and deadline recovery

### Analysis of Step 5 implementation state

Not started. Step 5 is not implemented because its planned files, behavior
and acceptance evidence have not yet been delivered or checked.

### Goal for Step 5

Arm durable waits without losing early completion and reconcile shared sources without inference.

### Step 5 improvement expectations

- Every early-result race retains one outcome, shared watches remain per-source while permissions remain per-wait, and simulated sleep/clock changes obey AC-09/AC-10 without model calls.
- Verify coalesced source-read counts, worker limits and finite timeout guards in the owning tests; no Step 0 or xfail placeholder defers these resource assertions.
- Preserve the plan's scope, line budget and existing workflow behavior.
- Record the targeted Groundhog and full-walk result and the required evidence.

### What was implemented for Step 5

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 5

_(empty — no check has taken place yet.)_.

### Architecture check for Step 5

_(empty — no check has taken place yet.)_.

### Performance check for Step 5

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 5

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 5

_(empty — no check has taken place yet.)_.

## Step 6. Implement delivery, cancellation and consumption settlement

### Analysis of Step 6 implementation state

Not started. Step 6 is not implemented because its planned files, behavior
and acceptance evidence have not yet been delivered or checked.

### Goal for Step 6

Keep one logical consumption decision through lost replies, crashes, cancellation and ownership changes.

### Step 6 improvement expectations

- Lost replies never imply no commit, settled/rejected attempts reject delayed consumes, pre-consume cancellation blocks effects, and abandonment recovery cannot restore obsolete authority or repeat useful work.
- In test_settlement_tdd.py, retain bounded subprocess evidence at durable intent, consume-commit and settlement barriers: terminate the fixture child without cleanup, reopen both stores and prove intent survives OS lock release. Keep exhaustive permutations in the in-process property tests.
- Preserve the plan's scope, line budget and existing workflow behavior.
- Record the targeted Groundhog and full-walk result and the required evidence.

### What was implemented for Step 6

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 6

_(empty — no check has taken place yet.)_.

### Architecture check for Step 6

_(empty — no check has taken place yet.)_.

### Performance check for Step 6

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 6

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 6

_(empty — no check has taken place yet.)_.

## Step 7. Expose status, recovery and bounded lifecycle operations

### Analysis of Step 7 implementation state

Not started. Step 7 is not implemented because its planned files, behavior
and acceptance evidence have not yet been delivered or checked.

### Goal for Step 7

Provide ordinary local lifecycle commands, safe offline status and retention without evicting unconsumed outcomes.

### Step 7 improvement expectations

- Local diagnostics and cancellation remain usable at capacity, no offline reader opens a locked store, and cleanup cannot delete work still awaiting handling.
- Check status read/page bounds and timeout guards. Launcher, CLI and runtime must preserve explicit-home-required rejection of omitted/default-home aliases until the recorded Step 8 rollout action.
- Preserve the plan's scope, line budget and existing workflow behavior.
- Record the targeted Groundhog and full-walk result and the required evidence.

### What was implemented for Step 7

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 7

_(empty — no check has taken place yet.)_.

### Architecture check for Step 7

_(empty — no check has taken place yet.)_.

### Performance check for Step 7

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 7

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 7

_(empty — no check has taken place yet.)_.

## Step 8. Validate integrated core and publish item 1 evidence

### Analysis of Step 8 implementation state

Not started. Step 8 is not implemented because its planned files, behavior
and acceptance evidence have not yet been delivered or checked.

| Step 8 completion component | Initial state | Evidence needed before recording completion |
| --- | --- | --- |
| Code complete | Not started | Composed acceptance tests, verifier, usage/report structure and Groundhog results |
| Live evidence recorded | Not started | Real bounded Windows sleep/resume with isolated synthetic fixtures, retained IDs/states, timings and limitations; Step 2 functional-route finding |
| Rollout recorded | Not started | Q07 guard-removal patch after isolated acceptance, explicit local rollout/compatibility check and post-patch tests |

Record the operator's suspension/resume action and requested/actual timing.
Retain the tested service commit/build identity and the guard-only rollout diff
so the pre-patch live evidence and post-patch checks remain attributable.
The core sleep fixture does not measure an LLM conversation. Any unavailable
second-user fixture stays an explicit limitation; synthetic rejection cases do
not prove live multi-user enforcement. Missing mandatory recovery evidence
keeps Step 8 incomplete even when code checks pass. The default home stays
guarded until the rollout component is recorded.

### Goal for Step 8

Prove the assembled Windows core and record exactly what item 1 establishes for later adapters.

### Step 8 improvement expectations

- A green Groundhog walk plus retained, bounded live Windows recovery evidence and functional route gate support the stated item 1 result. Missing live evidence remains an explicit incomplete gate; do not mark this step or umbrella completed from unit fixtures alone.
- Verify composed resource assertions and timeout guards. After isolated live acceptance and compatibility checks, retain the guard-only runtime/CLI/launcher patch and post-patch Groundhog results; runtime/operations tests exercise default discovery only through an injected default location.
- Preserve the plan's scope, line budget and existing workflow behavior.
- Record the targeted Groundhog and full-walk result and the required evidence.

### What was implemented for Step 8

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 8

_(empty — no check has taken place yet.)_.

### Architecture check for Step 8

_(empty — no check has taken place yet.)_.

### Performance check for Step 8

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 8

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 8

_(empty — no check has taken place yet.)_.
