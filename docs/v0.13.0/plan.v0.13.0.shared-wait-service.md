# v0.13.0 shared wait service implementation plan

Implement umbrella item 1 through measured native-wake prototypes, a durable
Windows service core and synthetic acceptance evidence.

- **Evidence first**: validate telemetry, then run native probes and A/B-prototype trials.
- **Durable core**: implement registration, monitoring, delivery and consumption recovery.
- **Explicit closure**: require live Windows recovery and retain later adapter obligations.

## Plan goal for v0.13.0 shared waits

Implement the [consolidated design](design.v0.13.0.shared-wait-service.md) and
[requirement](feature-request.v0.13.0.shared-wait-service.md) beside the
[focused draft](draft.v0.13.0.shared-wait-service.md), within
[umbrella item 1](draft.v0.13.0.no_polling.md). This plan is consolidated after review round 2;
no implementation, live probe, performance result or acceptance pass is claimed.

- **Step 1 goal**: Produce trustworthy exact-thread request and usage evidence before measuring a wake treatment.
- **Step 2 goal**: Record Codex-first and available Claude feasibility plus matched A/B-prototype evidence before substantial service implementation.
- **Step 3 goal**: Persist exact registrations, immutable outcomes/events and recovery state with transactional acknowledgements.
- **Step 4 goal**: Start one hidden process per canonical home and admit only compatible same-user peers.
- **Step 5 goal**: Arm durable waits without losing early completion and reconcile shared sources without inference.
- **Step 6 goal**: Keep one logical consumption decision through lost replies, crashes, cancellation and ownership changes.
- **Step 7 goal**: Provide ordinary local lifecycle commands, safe offline status and retention without evicting unconsumed outcomes.
- **Step 8 goal**: Prove the assembled Windows core and record exactly what item 1 establishes for later adapters.

## Scope anchors and rollout order for item 1

Steps 1 and 2 precede substantial service work. Steps 3 through 7 implement
the core through synthetic ports; Step 8 verifies the assembled result.
Step numbers here are local to item 1, not the umbrella's item numbers.

Steps 3 through 7 start after Step 2 records its live findings, including
failed/unavailable/inconclusive cases, or after the requirement's Q17 human
checkpoint records the scope allowed to proceed. A green harness alone does
not satisfy this ordering. When no route passes, recorded findings allow
independent synthetic core work with provisional ports under SW-08/Q17; the
human checkpoint still precedes interface freezing or item 1 closure.

- Deliver one Windows current-user authority per explicit canonical state home,
  exact durable registrations, typed source/host/authority ports, bounded local
  tooling, synthetic fixtures and standalone collection/probe/reporting tools.
- The service contracts implement the agreed design; concrete native host
  bindings remain provisional until the exact host/version probes support them.
- No functional native route means a human checkpoint before freezing host
  interfaces or closing item 1. Independent core and collector work may proceed;
  absence of request telemetry never proves strict zero-inference support.
- Production Groundhog/review sources are umbrella items 2 and 3. Their actual
  workflow ownership integration, including item 3's intent/settlement/human
  abandonment fence, remains mandatory later work.
- Production Codex/Claude/Copilot adapters are items 4 through 6, instruction
  migration is item 7, actual A/B-service evidence is item 8 and Gemini is item 9.
- Closed-TUI reopening, desktop hosts, WSL/remote execution and multiple machines
  remain outside initial support. Keep existing workflow execution paths intact.

## Complexity and file-based IO cost clarification for the plan

Use direct identity indexes for registration/event/attempt lookups and indexed
SQLite queries. Coalesce notification hints before reading a source; one source
watch serves its subscribers. Bound workers, protocol frames, result payloads,
status pages and diagnostic history. Never rescan all repositories or conversation
documents for each event, and never allocate a sleeping worker per registration.

Indexed database access and scheduler ordering may take logarithmic work in
indexed records; this plan does not impose an unsupported constant-time SQL
guarantee. Startup recovery is proportional to retained active state, not full
conversation history. Reconciliation cost follows dirty/due sources and their
subscribers, rather than all waits on each notification.

The normal registration/status path reads explicit identity/index records and
only required authoritative details. It never loads a model's conversation
context. Source reads and host I/O happen outside store transactions. Durable
SQLite commits and authoritative validation remain mandatory even when they
cost I/O; performance work cannot replace either with cached guesses.

The collector reads the manifest-selected telemetry streams incrementally from
recorded positions. Frozen seed loading is a separate benchmark phase. No cwd
search or newest-rollout heuristic participates in measured attribution.

## Confirmed code and test facts for plan viability

Inspection baseline: 2026-09-15, after design consolidation commit `ea3192c`.
Physical lines include blank lines, matching the file iteration metric in
[the big-file gate](../../bin/check_big_files.bat). The project
[senv setting](../../senv.bat) sets the Python ceiling to 650; the launcher's
700-line fallback is not this plan's execution limit.

| Existing reference | Physical lines | Planning consequence |
| --- | --- | --- |
| `tools/__init__.py` | 93 | Below 550; existing exports need no update for qualified new-package imports. |
| `tests/__init__.py` | 7 | Existing package marker; retain. |
| `tests/unit/__init__.py` | 6 | Existing package marker; retain. |
| `tests/unit/tools/__init__.py` | 6 | Existing package marker; retain. |
| `tools/review_exchange_wait.py` | 209 | Exact bounded wait remains a later production integration boundary. |
| `tools/review_resume_notifications.py` | 112 | Confirmed subscription-before-read and coalesced watchdog hints. |
| `tools/review_exchange_ownership_store.py` | 275 | Existing OS transition lock and digest-only authority remain independent. |
| `tools/review_artifact_configuration.py` | 184 | Callers resolve exact physical artifact homes. |
| `tools/groundhog/status.py` | 503 | Hidden survivor launch exists; no immutable run UUID is assumed for later sources. |
| `tools/groundhog/runner.py` | 225 | Existing execution and test lifecycle are preserved. |
| `pyproject.toml` | 256 | Python 3.13; tools run in place; watchdog, Hypothesis and pytest-timeout already declared. |
| `feature-request.v0.13.0.shared-wait-service.md` | 608 | Pre-plan baseline; only the matching I/O clarification is added during planning. |
| `design.v0.13.0.shared-wait-service.md` | 697 | Pre-plan baseline; same I/O clarification, with no reopened design decisions. |

All inspected Python references are below 550 and safe to extend under the
650-line ceiling, but this plan does not grow them. Neither new package
`tools/wait_service` / `tools/wait_evidence` nor its test counterpart exists
at this baseline. Every planned new file therefore has baseline 0.

The code tree already groups substantial tools into packages such as
`tools/groundhog` and `tools/markdown_check`. The test tree mixes older flat
tests with newer `tests/unit/tools/test_name/test_name_tdd.py` leaves. Follow
the newer leaf convention for all new tests and include package initializers.
There is no existing `tests/integration` root; acceptance scenarios use the
existing tools test hierarchy while remaining clearly identified as larger
integration tests, not evidence of unit-only coverage.

Existing review lifecycle, ownership, notification and Groundhog tests remain
part of the full regression gate. The project applies strict markers and a
100% tools coverage gate. No new dependency or coverage exclusion is planned:
use standard-library SQLite/ctypes and the existing watchdog dependency.

## Environment prerequisite before Step 1

Declared dependencies are not proof of an installed test environment. A direct
site-packages inventory on 2026-09-15 found no `watchdog`, `hypothesis` or
`pytest_timeout` package/module in this worktree's
`venvs/python_3.13.9_llm-shared_no_polling`. The canonical checkout's
`venvs/python_3.13.9_llm-shared` contained all three. This is an observed setup
gap, not a requested dependency change or a code-test failure.

Before implementation, run the project's normal environment setup from this
worktree and synchronize the existing lockfile through the project's
`tools/uv_run.py sync` route if necessary. Follow the environment-wrapper rules
in [run_commands.md](../../rules/run_commands.md), including clearing the
project-specific activation guard. Do not substitute an unrelated environment,
change dependency declarations, or weaken TLS/permission settings to hide a
setup failure. Record setup failures separately and resolve them before tests.

Verify and record the actual project Python executable, version, distribution
versions and successful imports of `watchdog`, `hypothesis` and `pytest_timeout`
in the environment Groundhog uses for its test child. Check that `tools`
resolves to this worktree. Use that verified project interpreter for the
standalone script smoke tests and live drivers; also verify the canonical
launcher interpreter separately. Repeat this prerequisite if either environment
or launcher-root selection changes. No installation or import-success result
is claimed by this plan.

## Runtime files and evidence ownership for shared waits

- Default service state: `%LOCALAPPDATA%/llm-shared/wait-service`, outside Git.
  Live tests explicitly select their own canonical isolated home.
- Local raw probe, manifest, seed, trace and temporary service fixtures:
  `a.shared-wait-service/<series>/<run>/`, covered by the existing `a.*` rule.
  Evidence must retain exact paths and hashes locally; do not commit full rollouts
  or credentials.
- Versioned scripts and compact reports are listed in their owning steps below.
  They live beside the effort docs; reusable tested logic lives under `tools/`.
  These scripts are standalone entry points, so `docs/` needs no Python
  package initializer.
- The final verifier only cleans resources it created after validating their
  resolved paths and run identity. It must retain reports and never target
  production workflow files or another running service.

## Shared execution command checklist for all eight steps

1. Recount every listed step file before edits, including package initializers;
   absent files start at 0. Record the actual count rather than a prior estimate.
2. Implement the step's behavioral tests first and observe meaningful failure.
   Use deterministic clocks and injected resources for long intervals.
3. Run targeted tests through Groundhog. Its `single` command accepts the
   concrete `test_*_tdd.py` and `test_*_pbt.py` paths listed for that step.
4. Run the step's `rg` check and inspect results for contract coverage; a string
   match alone is not proof of behavior. Review the diff for unintended workflow
   integration or private evidence.
5. Run one `ghog day` walk and follow its reported fixing loop until objective
   reached: checks, affected tests and full coverage are owned by Groundhog.
   Do not add direct `check.bat` or `pytest` calls to the checklist.
6. Recount all touched Python files after edits. Below 550 is safe to extend;
   550 through 650 is at risk; over 650 requires a responsibility split. The
   sole mandatory size bound is 650 unless a later step explicitly owns shrinking.
7. Apply each step's split guidance when needed. Advisory count variance below
   the ceiling is evidence, not missing implementation.
8. Record timings, real evidence and gate results in the matching validation
   section only after the implementation check. Keep an unperformed live gate
   explicitly incomplete.

## Ready-to-run command forms for shared wait steps

Resolve the canonical shared root from the loaded workflow instructions as
specified in [run_commands.md](../../rules/run_commands.md). Read
[Groundhog's workflow](../../instructions/groundhog.md) before running its loop.
Shared workflow launchers resolve from the canonical instruction root,
currently `C:/Users/vonc/git/llm-shared`. The new service code, its
`bin/wait_service.bat`, and the effort-side Python scripts belong to
`C:/Users/vonc/git/llm-shared_no_polling` until merge. Invoke those new
entry points from their absolute worktree paths with the verified project
environment, not as if the canonical checkout already contained them.

Launchers honor an inherited `LLM_SHARED_DIR`; even a full-path launcher call
can select a different interpreter when that variable is stale. Check that
selection before the call. When necessary, use a caller-owned PowerShell
script to set `LLM_SHARED_DIR` to the resolved canonical root for shared
workflow commands only, as documented by the launcher workaround. Keep the
project root and test-child environment bound to this worktree. A wrapper or
setup error is a prerequisite failure, never evidence against service code.

For line counts, put this small script in an ignored `a.*.ps1` file and invoke
it with the step's exact paths. This counts physical lines including blanks.

```powershell
param([string[]]$Paths)
foreach ($stepPath in $Paths) {
  $count = 0
  if (Test-Path -LiteralPath $stepPath -PathType Leaf) {
    foreach ($line in [IO.File]::ReadLines((Resolve-Path -LiteralPath $stepPath).Path)) {
      $count++
    }
  }
  [PSCustomObject]@{ Path = $stepPath; Lines = $count }
}
```

Groundhog command forms, substituting concrete test files from the step:

```text
& "<LLM_SHARED_DIR>/bin/ghog.bat" single <step test file paths>
& "<LLM_SHARED_DIR>/bin/ghog.bat" day
```

Use a detached walk and its documented status mechanism when execution lifetime
requires it. Wait on the existing healthy process; do not restart a walk from
log growth or repeatedly poll it for progress. Setup errors are not green tests
and do not authorize changing dependencies or coverage gates to manufacture a pass.

## Timeout gates and the Step 0 assessment

No separate Step 0 or expected-failure performance suite is needed: this is a
new isolated package, and there is no existing measured hot-path regression to
capture before implementation. Each owning step adds passing timeout guards and
deterministic read-count/worker-bound tests with its behavior. Use
`pytest.mark.timeout` for deadlock/runaway protection, not a substitute for
the 15-second startup or other contractual durations, which fake clocks verify.

There are no planned `xfail` placeholders. The ten-minute native baseline,
240-second comparisons and real sleep/resume check are explicit evidence runs
outside the fast unit suite. They cannot be marked passed by synthetic time.

Steps 1, 4, 5, 7 and 8 own their resource assertions and timeout guards:
incremental collector reads, bounded startup/pipe work, coalesced source reads
and worker limits, bounded status pages, and composed acceptance resources.
Do not defer these checks to a separate performance step or weaken the gates.

## Numbered implementation steps for v0.13.0 shared waits

### Step 1. Validate standalone telemetry collection

#### Step 1 analysis and intent

Current evidence is not a reusable exact-thread collector. Establish typed manifests, normalized events and independent request/usage coverage, then prove counts from synthetic streams. Keep telemetry parsing separate from accounting and reporting so installing another host schema does not alter measured phase rules.

Expected outcome: Produce trustworthy exact-thread request and usage evidence before measuring a wake treatment.

Step framing: [settled design section](design.v0.13.0.shared-wait-service.md#collector-ports-normalized-records-and-coverage);
requirement coverage: AC-16; SW-10 and SW-11. Apply the
[shared execution checklist](#shared-execution-command-checklist-for-all-eight-steps)
and [command forms](#ready-to-run-command-forms-for-shared-wait-steps).
Keep changes inside the listed responsibilities and preserve existing workflows.

#### Step 1 implementation

Files involved, with the measured current baseline:

| File and state | Physical baseline | Python policy |
| --- | --- | --- |
| `tools/wait_evidence/__init__.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tools/wait_evidence/models.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tools/wait_evidence/telemetry.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tools/wait_evidence/collector.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tools/wait_evidence/reports.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `docs/v0.13.0/collect.shared-wait-service.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tests/unit/tools/wait_evidence/__init__.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tests/unit/tools/wait_evidence/test_collector/__init__.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tests/unit/tools/wait_evidence/test_collector/test_collector_tdd.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tests/unit/tools/wait_evidence/test_collector/test_collector_pbt.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tests/unit/tools/wait_evidence/test_telemetry/__init__.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tests/unit/tools/wait_evidence/test_telemetry/test_telemetry_tdd.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |

Tests first:

- Start with repeated pre-start cumulative records, request retries, duplicate completions, mixed per-request/cumulative usage and counter resets; assert exact expected totals and unknown fields.
- Cover delayed/partial/malformed JSONL, compaction, rotation, wrong-thread records, nested execution/tool IDs, poll commands with other names, cross-phase requests and absent attempt evidence.
- Use Hypothesis to permute duplicate and delayed ingestion order without changing deduplicated totals; independent omissions must lower coverage confidence rather than yield false zero.
- Instrument reads: resume at stored offsets, read bounded chunks, never discover a thread by cwd or newest file, and retain enough boundary state for split JSONL records.
- In test_collector_tdd.py, run bounded subprocess smoke cases against the absolute collector script path from the checkout and another cwd, using the verified project interpreter and explicit input/output paths. No manually prepared PYTHONPATH is required.

Classes and behavior:

- models.py defines TrialManifest, EvidenceRecord, CoverageAssessment and phase identities, preserving original and ingestion time and source location.
- telemetry.py validates actual host/version/profile/schema against the manifest and normalizes records; unknown schema fails coverage explicitly. Test schemas are labeled synthetic until local installation inspection supplies real fixtures.
- collector.py owns baseline epochs, deduplication, tool correlation and drain state. reports.py writes immutable report versions, per-pair counts/deltas, median/range and failed/invalid/inconclusive totals. Report seed and auxiliary usage separately.
- The effort-side collector script is a thin explicit-path CLI into these modules. The driver requires finite series wake/duplicate/drain bounds and an arm enum; B-service remains a reserved later-item label. The 120-second drain ends early only on authoritative completeness.
- Bootstrap module discovery from the script's own resolved physical location. This only locates code; repository, home and telemetry attribution still use explicit identities and never the caller's cwd.

Completion criteria:

- Known synthetic streams reproduce expected attempts, usage and phase totals; insufficient request evidence can never produce strict zero-inference support. Reports retain raw-evidence references without copying private rollouts.
- Targeted tests and the shared `ghog day` walk pass with recorded evidence.
- Inspect this contract search and the affected diff:

```text
rg -n 'CoverageAssessment|request_coverage|usage_coverage|B-prototype|B-service' tools/wait_evidence
```

#### Step 1 addendums

Line-budget checkpoint:

- [ ] Recount each listed file at execution time; all current baselines are 0,
  with later-step extensions inheriting their actual earlier-step counts.
- [ ] Every listed Python file starts in the below-550 safe band; the mandatory
  ceiling is 650, including tests and initializers. No tighter target is imposed.
- [ ] At 550 through 650, assess growth and apply the split guidance if the
  ceiling would be crossed; above 650, split before step completion.

Split guidance: Separate telemetry schemas into per-host parser modules if telemetry.py would exceed 650; split collector tests by accounting versus correlation before either leaf grows beyond the ceiling.

Complexity and feature preservation: use the
[shared complexity/I/O rules](#complexity-and-file-based-io-cost-clarification-for-the-plan);
do not add per-event repository scans, context loading or workflow authority paths.

Full workflow timing run readiness: the listed test leaves identify the focused
Groundhog inputs; record that run and the shared `ghog day` result after code
exists. No timing or full-coverage result has been measured for this step yet.

Time-gated status for Step 1: Use fake clocks for drain and late-arrival tests. Apply finite pytest timeout guards to parser/collector cases; no wall-clock sleep or inference in tests.

### Step 2. Run the minimal native-wake prototype and matched trials

#### Step 2 analysis and intent

An exposed queue operation is not proof of an idle TUI wake. Build only the synthetic durable registration/source/outcome/receipt harness and reuse Step 1 accounting. Native route details remain provisional until the exact open conversation resumes automatically.

Expected outcome: Record Codex-first and available Claude feasibility plus matched A/B-prototype evidence before substantial service implementation.

Step framing: [settled design section](design.v0.13.0.shared-wait-service.md#codex-first-and-independent-claude-probes);
requirement coverage: AC-02, AC-14, AC-15; SW-08 through SW-11. Apply the
[shared execution checklist](#shared-execution-command-checklist-for-all-eight-steps)
and [command forms](#ready-to-run-command-forms-for-shared-wait-steps).
Keep changes inside the listed responsibilities and preserve existing workflows.

#### Step 2 implementation

Files involved, with the measured current baseline:

| File and state | Physical baseline | Python policy |
| --- | --- | --- |
| `tools/wait_evidence/prototype.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tools/wait_evidence/telemetry.py` (created in Step 1, extended here) | Step 1 count | Recount: below 550 safe; 550 through 650 at risk; ceiling 650 |
| `docs/v0.13.0/probe.shared-wait-service.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `docs/v0.13.0/probe-results.v0.13.0.shared-wait-service.md` (new, to be created) | 0 | Non-Python, no Python ceiling |
| `tests/unit/tools/wait_evidence/test_prototype/__init__.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tests/unit/tools/wait_evidence/test_prototype/test_prototype_tdd.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tests/unit/tools/wait_evidence/test_telemetry/test_telemetry_tdd.py` (created in Step 1, extended here) | Step 1 count | Recount: below 550 safe; 550 through 650 at risk; ceiling 650 |

Tests first:

- Test timer release and durable identities with fake clocks/host callbacks before live probing, including early completion and restart before send.
- Exercise direct normal-end and host-gated normal-end variants, unavailable gating, Stop/Cancel/interruption suppression, busy/closed/stale recipients, lost receipt and duplicate useful-continuation rejection.
- Test driver validation of fresh run/thread IDs, full frozen/hash-recorded seeds, READY-before-manifest-before-prompt ordering, 5% context matching, fixed configuration and retained invalid trials. No PBT is needed beyond Step 1 accounting properties.
- Extend test_telemetry_tdd.py with redacted fixtures from each inspected installed host/version and unknown-schema coverage failures. Keep one normalization path in telemetry.py rather than duplicating parsing in the prototype.
- In test_prototype_tdd.py, invoke the absolute probe script in bounded subprocess smoke cases from both the checkout and another cwd, using the verified project interpreter and explicit input/output paths. Resolve imports from the script's physical location, never from cwd or a manually prepared PYTHONPATH.

Classes and behavior:

- prototype.py persists only harness state under an explicit ignored run directory; it does not import or masquerade as the shared service. The thin probe CLI accepts exact host/thread/profile and synthetic source settings.
- At implementation time inspect installed Codex help/backend and actual Claude Monitor schema. Capture executable/build, configuration and evidence capability without changing provider, permissions, approval or telemetry settings. The harness does not start reviewer/requestor counterparts.
- Extend Step 1 telemetry.py for those inspected schemas; prototype.py owns host invocation and harness state. Preserve unknown request/usage coverage when the installed schema cannot prove completeness.
- Freeze the full docs/v0.13.0/draft.v0.13.0.no_polling.md and docs/v0.13.0/draft.v0.13.0.shared-wait-service.md from one recorded commit, following SW-10 and the focused draft's READY prompt. Put that commit ID, exact source paths and each frozen copy's SHA-256 in every manifest. Both arms read identical frozen bytes; later source edits start a new seed revision/series. Preserve full reads, retained context, compaction configuration and redacted proxy/CA/transport evidence.
- Run Codex first and available Claude separately. Each initial host/version series records a 60-second wake bound and 120-second post-completion duplicate window in its manifest before the first trial; wake latency ends at the first useful continuation, not transport acceptance. Keep these bounds fixed within the series; a change starts a new series and retains earlier failures. The telemetry drain has its separate 120-second bound from Step 1. Run at least ten minutes of unchanged source after normal turn end, then at least three fresh trials per arm in A/B, B/A, A/B order. The 240-second source interval is distinct from actual quiet time.
- A uses initial 1,000 ms yield where supported, otherwise the minimum, followed by 60,000 ms waits as the documented benchmark-only exception. B ends normally and receives useful WAIT_TEST_DONE automatically. Collection and source timers run outside measured conversations.
- Record pass/fail/unavailable/inconclusive per host and case. No passing native route triggers the design's human checkpoint before host-interface freezing or item 1 closure; independent core/collector work may continue with provisional ports. Adequate coverage is separately required for strict-idle-supported.

Live operator procedure for Step 2:

1. The human operator starts each fresh Codex TUI conversation and each available
   Claude conversation; the implementing session prepares the driver, commands
   and frozen seed but is never itself a measured conversation. Repeat for each
   unchanged-source baseline and each A/B trial; never recycle a measured thread.
2. The operator delivers the protocol's seed prompt through the normal TUI input,
   naming the frozen copies of the two specified drafts. Verify complete reads
   and retained context after READY. An independent ordinary-code driver then
   writes the manifest, exact thread binding and pre-start telemetry positions.
3. The driver prepares the exact arm's benchmark prompt; the operator submits it
   only after the manifest is durable. Preserve that prompt with the run. The
   source timer and collector stay in independent ordinary processes.
4. Prefer proven native normal-end evidence. If measurement needs an operator
   marker, the operator invokes the driver's explicit mark-normal-end action
   only after observing normal TUI turn completion. This writes a timestamped
   marker outside the conversation; it never sends another user turn or arms a
   route. An operator marker cannot substitute for a proven normal-end host gate.
5. Observe the automatic useful continuation without nudging the measured TUI.
   Record its first useful continuation, not merely queue/transport acceptance,
   then complete the finite duplicate window and telemetry drain. Retain misses,
   interruptions and unmatched pairs before repeating them in fresh threads.
6. Record an unavailable Claude installation/Monitor route with the inspected
   build/schema or the concrete missing capability and attempted check. Do not
   invent a Claude trial, substitute another host, or count it as a passing arm.

Step 2 completion states, recorded separately:

- **Code complete**: harness/collector integration and deterministic driver
  tests pass targeted Groundhog and the full walk; commands and operator
  procedure are ready. This alone leaves Step 2 incomplete.
- **Live evidence recorded**: required available-host baselines and matched
  trials have retained manifests/reports; every unavailable or failed route has
  a concrete finding. A recorded failure does not become a functional pass.
  Apply the [Step 2 start gate](#scope-anchors-and-rollout-order-for-item-1)
  before service work, and retain the functional route gate for item 1 closure.

Completion criteria:

- Commit reproducible commands, redacted manifests/configuration and compact A/B-prototype results, with all original failures and repeats. At least one functional route is required for item 1 closure. If no route passes, report that finding to the human; do not invent a replacement route.
- Targeted tests and the shared `ghog day` walk pass with recorded evidence.
- Inspect this contract search and the affected diff:

```text
rg -n 'normal.end|WAIT_TEST_DONE|B-prototype|inconclusive' tools/wait_evidence docs/v0.13.0/probe-results.v0.13.0.shared-wait-service.md
```

#### Step 2 addendums

Line-budget checkpoint:

- [ ] Recount each listed file at execution time; all current baselines are 0,
  with later-step extensions inheriting their actual earlier-step counts.
- [ ] Every listed Python file starts in the below-550 safe band; the mandatory
  ceiling is 650, including tests and initializers. No tighter target is imposed.
- [ ] At 550 through 650, assess growth and apply the split guidance if the
  ceiling would be crossed; above 650, split before step completion.

Split guidance: Keep installed-host invocation details in prototype.py only while it fits 650 lines; extract each host invocation adapter when that responsibility needs more space. Keep prototype state independent of the later store.

Complexity and feature preservation: use the
[shared complexity/I/O rules](#complexity-and-file-based-io-cost-clarification-for-the-plan);
do not add per-event repository scans, context loading or workflow authority paths.

Full workflow timing run readiness: the listed test leaves identify the focused
Groundhog inputs; record that run and the shared `ghog day` result after code
exists. No timing or full-coverage result has been measured for this step yet.

Time-gated status for Step 2: Real ten-minute and 240-second runs are explicit live experiments outside the fast unit suite. Record actual idle/source durations and finite wake/duplicate/drain boundaries; unit timer cases use fake time.

### Step 3. Create the durable service model and store

#### Step 3 analysis and intent

There is no shared durable wait authority today. Implement the settled domain and SQLite contracts independently of native host APIs; keep source/host I/O outside store transactions and retain typed failure evidence.

Expected outcome: Persist exact registrations, immutable outcomes/events and recovery state with transactional acknowledgements.

Step framing: [settled design section](design.v0.13.0.shared-wait-service.md#durable-records-and-transaction-boundaries);
requirement coverage: AC-01, AC-03, AC-05, AC-12, AC-13. Apply the
[shared execution checklist](#shared-execution-command-checklist-for-all-eight-steps)
and [command forms](#ready-to-run-command-forms-for-shared-wait-steps).
Keep changes inside the listed responsibilities and preserve existing workflows.

#### Step 3 implementation

Files involved, with the measured current baseline:

| File and state | Physical baseline | Python policy |
| --- | --- | --- |
| `tools/wait_service/__init__.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tools/wait_service/models.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tools/wait_service/ports.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tools/wait_service/store.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tests/unit/tools/wait_service/__init__.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tests/unit/tools/wait_service/test_store/__init__.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tests/unit/tools/wait_service/test_store/test_store_tdd.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tests/unit/tools/wait_service/test_store/test_store_pbt.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |

Tests first:

- Use temporary real SQLite stores to test reopen, successful/failed commit boundaries, disk-full/corrupt/unknown-schema refusal, durable acknowledgement and immutable outcome/event creation.
- Test canonical idempotency equality versus conflict, explicit finite-or-indefinite validation, preparing/armed retry, stable IDs and physical source/recipient isolation.
- Add property tests for retry/outcome/cancellation sequences: unchanged intent cannot create another wait, terminal outcomes cannot reopen, failed commits cannot acknowledge success.

Classes and behavior:

- models.py owns typed identities, policies, bounded outcomes and errors; ports.py declares source, host, authority, clock and I/O seams without importing production workflow adapters.
- store.py creates schema version 1 only for an absent store, uses rollback journaling and full synchronization, and exposes explicit transactions and indexed exact-key lookups. Persist all entities in the design's record table, including attempt settlement and abandonment evidence fields needed by Step 6.
- Retain source and route policy versions, access-loss start, delivery epochs, next eligible UTC and deduplication facts. Only versioned known schemas open; maintenance migration is added in Step 7.
- Use small package initializers, with imports under tools.wait_service rather than adding wait-service exports to `tools/__init__.py`. No review or Groundhog implementation is modified.

Completion criteria:

- Reopened stores preserve acknowledged registration, outcome and event identities, and injected storage failures return typed unavailable results without resetting the database.
- Targeted tests and the shared `ghog day` walk pass with recorded evidence.
- Inspect this contract search and the affected diff:

```text
rg -n 'preparing|armed|idempotency|synchronous|journal_mode' tools/wait_service
```

#### Step 3 addendums

Line-budget checkpoint:

- [ ] Recount each listed file at execution time; all current baselines are 0,
  with later-step extensions inheriting their actual earlier-step counts.
- [ ] Every listed Python file starts in the below-550 safe band; the mandatory
  ceiling is 650, including tests and initializers. No tighter target is imposed.
- [ ] At 550 through 650, assess growth and apply the split guidance if the
  ceiling would be crossed; above 650, split before step completion.

Split guidance: Keep base persistence and schema in store.py; consumption transactions land separately in store_consumption.py in Step 6. Extract queries or schema definitions by responsibility only if a module would exceed 650.

Complexity and feature preservation: use the
[shared complexity/I/O rules](#complexity-and-file-based-io-cost-clarification-for-the-plan);
do not add per-event repository scans, context loading or workflow authority paths.

Full workflow timing run readiness: the listed test leaves identify the focused
Groundhog inputs; record that run and the shared `ghog day` result after code
exists. No timing or full-coverage result has been measured for this step yet.

Time-gated status for Step 3: Real SQLite tests use temporary storage and bounded operations, no simulated time via sleep. Timeout guards catch deadlocks; PBT uses small operation sequences.

### Step 4. Implement the Windows authority and authenticated pipe

#### Step 4 analysis and intent

A PID and predictable pipe name cannot establish service ownership or peer identity. Implement the chosen OS singleton and mutual user checks with a mockable Win32 adapter, leaving policy independent of the platform calls.

Expected outcome: Start one hidden process per canonical home and admit only compatible same-user peers.

Step framing: [settled design section](design.v0.13.0.shared-wait-service.md#service-ownership-discovery-and-local-ipc);
requirement coverage: AC-08, AC-12, AC-13. Apply the
[shared execution checklist](#shared-execution-command-checklist-for-all-eight-steps)
and [command forms](#ready-to-run-command-forms-for-shared-wait-steps).
Keep changes inside the listed responsibilities and preserve existing workflows.

#### Step 4 implementation

Files involved, with the measured current baseline:

| File and state | Physical baseline | Python policy |
| --- | --- | --- |
| `tools/wait_service/runtime.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tools/wait_service/windows_ipc.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tools/wait_service/protocol.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tests/unit/tools/wait_service/test_runtime/__init__.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tests/unit/tools/wait_service/test_runtime/test_runtime_tdd.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tests/unit/tools/wait_service/test_protocol/__init__.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tests/unit/tools/wait_service/test_protocol/test_protocol_tdd.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tests/unit/tools/wait_service/test_windows_ipc/__init__.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tests/unit/tools/wait_service/test_windows_ipc/test_windows_ipc_tdd.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |

Tests first:

- First test simultaneous starters, stale discovery, hidden child surviving parent exit, offline-reader lock contention and the 15-second startup bound with injected process/clock/lock APIs.
- Test explicit canonical home aliases and separate isolated homes, no cwd/default fallback, squatted pipe conflicts, foreign/remote peers and verification failure before any application frame.
- Test refusal before file/pipe creation when no explicit isolated home is supplied or the resolved home is the default home. Return typed explicit-home-required; aliases cannot bypass the pre-rollout guard.
- Test length framing at 64 KiB, 8 KiB inline results, truncated/invalid JSON, unknown operation/required feature and protocol-major/schema incompatibility. Use parameterized framing boundaries rather than another PBT suite.
- Use the dedicated test_windows_ipc_tdd.py leaf for direct ctypes adapter return/error paths, SID/ACL handling and handle cleanup through an explicit native-call seam. Keep adapter code in the unit coverage gate; Step 8 live Windows results remain separate evidence.

Classes and behavior:

- runtime.py resolves user/home identity and owns singleton lifetime, hidden survivor startup, discovery hints, hello/readiness and orderly shutdown. Startup retries lock acquisition within 15 seconds when an offline reader holds it; never kill a healthy owner.
- Until the Step 8 rollout patch, runtime.py requires an explicit nondefault isolated home before startup or discovery. Neither an omitted argument nor a default-home alias may create a development authority. Keep this temporary guard separate from the settled home canonicalization contract.
- windows_ipc.py confines ctypes Win32 calls, handle cleanup, explicit user ACLs on pipe/state, remote rejection, first-instance creation and reciprocal token-user SID verification before frames. Platform imports must remain safe on non-Windows test collection.
- protocol.py validates bounded typed frames and compatibility. Bind endpoint identity to SID and physical state home and expose protocol/build/schema/instance/feature identity.
- Use the existing shared launcher resolution pattern without coupling to Groundhog's status file. The service owns no automatic logon task or idle-exit policy. Unit tests fake OS APIs; real Windows coverage is owned by Step 8.

Completion criteria:

- Synthetic peers cannot reach a request handler before identity and compatibility checks; concurrent startup selects one durable authority and honors explicit isolated homes.
- Targeted tests and the shared `ghog day` walk pass with recorded evidence.
- Inspect this contract search and the affected diff:

```text
rg -n 'FIRST_PIPE_INSTANCE|PIPE_REJECT_REMOTE_CLIENTS|startup-timeout|hello' tools/wait_service
```

#### Step 4 addendums

Line-budget checkpoint:

- [ ] Recount each listed file at execution time; all current baselines are 0,
  with later-step extensions inheriting their actual earlier-step counts.
- [ ] Every listed Python file starts in the below-550 safe band; the mandatory
  ceiling is 650, including tests and initializers. No tighter target is imposed.
- [ ] At 550 through 650, assess growth and apply the split guidance if the
  ceiling would be crossed; above 650, split before step completion.

Split guidance: Extract Win32 security/handle utilities from windows_ipc.py if it would exceed 650; keep wire validation in protocol.py and process lifecycle in runtime.py. Split native identity tests from framing tests.

Complexity and feature preservation: use the
[shared complexity/I/O rules](#complexity-and-file-based-io-cost-clarification-for-the-plan);
do not add per-event repository scans, context loading or workflow authority paths.

Full workflow timing run readiness: the listed test leaves identify the focused
Groundhog inputs; record that run and the shared `ghog day` result after code
exists. No timing or full-coverage result has been measured for this step yet.

Time-gated status for Step 4: Simulate the 15-second startup deadline without real waiting. Include finite timeout guards on lock and pipe fixture tests; defer survivor-process timing to live acceptance.

### Step 5. Wire registration, monitoring and deadline recovery

#### Step 5 analysis and intent

Source changes can race registration and clocks can jump during suspension. Connect subscriptions, preparation and arming to the durable store, with one scheduler and bounded workers instead of a sleeping worker per wait.

Expected outcome: Arm durable waits without losing early completion and reconcile shared sources without inference.

Step framing: [settled design section](design.v0.13.0.shared-wait-service.md#source-monitoring-and-recovery-scheduling);
requirement coverage: AC-01, AC-03, AC-04, AC-09, AC-10. Apply the
[shared execution checklist](#shared-execution-command-checklist-for-all-eight-steps)
and [command forms](#ready-to-run-command-forms-for-shared-wait-steps).
Keep changes inside the listed responsibilities and preserve existing workflows.

#### Step 5 implementation

Files involved, with the measured current baseline:

| File and state | Physical baseline | Python policy |
| --- | --- | --- |
| `tools/wait_service/registration.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tools/wait_service/monitoring.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tools/wait_service/synthetic.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tests/unit/tools/wait_service/test_monitoring/__init__.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tests/unit/tools/wait_service/test_monitoring/test_monitoring_tdd.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tests/unit/tools/wait_service/test_monitoring/test_monitoring_pbt.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |

Tests first:

- Subscribe before first read; inject completion before registration, between subscription/read and before arming/turn end. Failed arming retains preparing state and early outcomes for identical retry.
- Test shared sources with distinct recipients, deadlines, roles and cancellation, notification storms, missed notifications, observer startup failure and workers that exceed their declared observation budget.
- Use fake UTC and monotonic clocks for predeadline/equal/late readiness, timestamp-less on-time upper bounds, unreadable sources, restart, suspend/resume and forward/backward corrections.
- Add PBT for event/clock orderings: terminal states stay terminal, uncertainty never supplies a false on-time bound, indefinite waits do not expire and subscribers never inherit another registration's authority.

Classes and behavior:

- registration.py validates exact identity and policy, persists preparation, shares a watch, reconciles source and negotiates the route; armed acknowledgement follows the durable usable-route result.
- monitoring.py coalesces dirty-source hints, deadlines and retries into one schedule and bounds blocking work. Synthetic policy versions use a 30-second reconciliation ceiling and 60-second durable access-loss interval; invalid identity never becomes readiness.
- synthetic.py provides controllable source and host ports and deterministic clock fixtures for core acceptance, independent of review/Groundhog artifacts. It will gain a separate durable synthetic workflow authority in Step 6.
- Persist absolute UTC deadlines; source completion timestamp or reliable predeadline readiness observation decides readiness versus expiry for pending waits. Unreadable sources follow access-loss recovery. Coalesce missed timers on resume and do not persist/reuse raw monotonic deadlines.

Completion criteria:

- Every early-result race retains one outcome, shared watches remain per-source while permissions remain per-wait, and simulated sleep/clock changes obey AC-09/AC-10 without model calls.
- Targeted tests and the shared `ghog day` walk pass with recorded evidence.
- Inspect this contract search and the affected diff:

```text
rg -n 'unknown|monitoring-failure|deadline|preparing|armed' tools/wait_service
```

#### Step 5 addendums

Line-budget checkpoint:

- [ ] Recount each listed file at execution time; all current baselines are 0,
  with later-step extensions inheriting their actual earlier-step counts.
- [ ] Every listed Python file starts in the below-550 safe band; the mandatory
  ceiling is 650, including tests and initializers. No tighter target is imposed.
- [ ] At 550 through 650, assess growth and apply the split guidance if the
  ceiling would be crossed; above 650, split before step completion.

Split guidance: If monitoring.py would exceed 650, separate deadline decisions from scheduler/notification ownership. Keep registration arming separate from reconciliation; split test cases at that same boundary.

Complexity and feature preservation: use the
[shared complexity/I/O rules](#complexity-and-file-based-io-cost-clarification-for-the-plan);
do not add per-event repository scans, context loading or workflow authority paths.

Full workflow timing run readiness: the listed test leaves identify the focused
Groundhog inputs; record that run and the shared `ghog day` result after code
exists. No timing or full-coverage result has been measured for this step yet.

Time-gated status for Step 5: Thirty/sixty-second policies and suspension intervals use fake clocks. Assert source reads are coalesced and scheduler worker count stays bounded; do not xfail correctness gates.

### Step 6. Implement delivery, cancellation and consumption settlement

#### Step 6 analysis and intent

Transport acceptance is not workflow consumption, and a timed-out consume may have committed. Implement the settled event/attempt/receipt boundary and prove the cross-store fence with a separate synthetic workflow authority before production integration.

Expected outcome: Keep one logical consumption decision through lost replies, crashes, cancellation and ownership changes.

Step framing: [settled design section](design.v0.13.0.shared-wait-service.md#the-atomic-cancellation-fence);
requirement coverage: AC-05, AC-06, AC-07, AC-08, AC-11, AC-13. Apply the
[shared execution checklist](#shared-execution-command-checklist-for-all-eight-steps)
and [command forms](#ready-to-run-command-forms-for-shared-wait-steps).
Keep changes inside the listed responsibilities and preserve existing workflows.

#### Step 6 implementation

Files involved, with the measured current baseline:

| File and state | Physical baseline | Python policy |
| --- | --- | --- |
| `tools/wait_service/delivery.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tools/wait_service/store_consumption.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tools/wait_service/synthetic.py` (created in Step 5, extended here) | Step 5 count | Recount: below 550 safe; 550 through 650 at risk; ceiling 650 |
| `tests/unit/tools/wait_service/test_delivery/__init__.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tests/unit/tools/wait_service/test_delivery/test_delivery_tdd.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tests/unit/tools/wait_service/test_delivery/test_delivery_pbt.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tests/unit/tools/wait_service/test_settlement/__init__.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tests/unit/tools/wait_service/test_settlement/test_settlement_tdd.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |

Tests first:

- Inject crashes at outcome commit, send, acceptance, consume commit, lost reply, native wake, first ordinary callback and workflow receipt. Assert stable event/consumption IDs and no duplicate useful effect.
- Enumerate cancellation before and after readiness/expiry/queue/receipt/consume, stale recipients/generations and wrong roles. Queued cancellation-induced wakes must be counted but cannot authorize dependent work.
- In a second durable synthetic workflow store, test intent under its transition lock, crash releasing that lock, consume/settle races, rejected tombstones, delayed old requests and lost settlement replies.
- In test_settlement_tdd.py, use a small bounded subprocess matrix with explicit barriers after durable workflow intent, service consume commit and settlement. Terminate only the fixture child without cleanup handlers (TerminateProcess on Windows), reopen both stores, and prove the durable intent fence survives OS lock release. Keep exhaustive permutations in the in-process state-machine property tests.
- Test explicit human abandonment during service failure, generation advance under existing authority, rejection of stale resumed callbacks and reconciliation/supersession before current-owner consumption. Preserve completed receipts and unresolved effects.
- Add state-machine PBT for duplicate/reordered consume, settle, cancel and receipt operations; isolate result-detail tampering, command/prompt injection and required-detail failures as deterministic cases.

Classes and behavior:

- delivery.py renders allowlisted typed events, checks normal-end/recipient eligibility and manages three attempts with 1/5-second delays, durable attempt epochs and ordinary-code receipt reconciliation. Unchanged recovery hints cannot reset exhausted retries.
- store_consumption.py owns atomic cancellation/consume decisions and same-attempt settle tombstones, consumption UUID lookup, abandonment reconciliation and supersession. Service code never takes a workflow transition lock.
- Extend synthetic.py with a separate durable authority store and lock for in-flight intents, human abandonment and workflow receipts. It must exercise real persisted fences, not substitute the service transaction or an in-memory flag for workflow authority.
- The first resumed ordinary callback validates consumption UUID and current authority before dependent effects. Missing turn-start evidence permits bounded native-wake redelivery under the same UUID; execution-unresolved applies only to an uncertain later effect.
- Validate required details by exact reference/generation/digest; retain unavailable/invalid outcomes without rerunning sources. Same-session rearm creates a new incarnation, while changing recipient requires explicit human action and existing workflow authority.

Completion criteria:

- Lost replies never imply no commit, settled/rejected attempts reject delayed consumes, pre-consume cancellation blocks effects, and abandonment recovery cannot restore obsolete authority or repeat useful work.
- Targeted tests and the shared `ghog day` walk pass with recorded evidence.
- Inspect this contract search and the affected diff:

```text
rg -n 'consumption-resolution-pending|execution-unresolved|settle|superseded|cancellation-induced-wake' tools/wait_service
```

#### Step 6 addendums

Line-budget checkpoint:

- [ ] Recount each listed file at execution time; all current baselines are 0,
  with later-step extensions inheriting their actual earlier-step counts.
- [ ] Every listed Python file starts in the below-550 safe band; the mandatory
  ceiling is 650, including tests and initializers. No tighter target is imposed.
- [ ] At 550 through 650, assess growth and apply the split guidance if the
  ceiling would be crossed; above 650, split before step completion.

Split guidance: Split synthetic authority persistence from source/host fixtures into synthetic_authority.py if synthetic.py would exceed 650. Keep settlement tests separate from delivery tests; extract store transaction helpers only along those boundaries.

Complexity and feature preservation: use the
[shared complexity/I/O rules](#complexity-and-file-based-io-cost-clarification-for-the-plan);
do not add per-event repository scans, context loading or workflow authority paths.

Full workflow timing run readiness: the listed test leaves identify the focused
Groundhog inputs; record that run and the shared `ghog day` result after code
exists. No timing or full-coverage result has been measured for this step yet.

Time-gated status for Step 6: Retry delays and admission budgets use deterministic time. Crash tests use bounded subprocesses only where restart persistence is under test; no real 1/5-second sleeps.

### Step 7. Expose status, recovery and bounded lifecycle operations

#### Step 7 analysis and intent

A durable service needs inspectable failure and recovery states without model health checks. Add the local command surface and composition root after policy and persistence have executable coverage.

Expected outcome: Provide ordinary local lifecycle commands, safe offline status and retention without evicting unconsumed outcomes.

Step framing: [settled design section](design.v0.13.0.shared-wait-service.md#status-retention-and-operational-bounds);
requirement coverage: AC-06, AC-12, AC-13. Apply the
[shared execution checklist](#shared-execution-command-checklist-for-all-eight-steps)
and [command forms](#ready-to-run-command-forms-for-shared-wait-steps).
Keep changes inside the listed responsibilities and preserve existing workflows.

#### Step 7 implementation

Files involved, with the measured current baseline:

| File and state | Physical baseline | Python policy |
| --- | --- | --- |
| `tools/wait_service/operations.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tools/wait_service/cli.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tools/wait_service/runtime.py` (created in Step 4, extended here) | Step 4 count | Recount: below 550 safe; 550 through 650 at risk; ceiling 650 |
| `bin/wait_service.bat` (new, to be created) | 0 | Non-Python, no Python ceiling |
| `tests/unit/tools/wait_service/test_operations/__init__.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tests/unit/tools/wait_service/test_operations/test_operations_tdd.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |

Tests first:

- Test status pagination and explicit identities, offline singleton acquisition before opening SQLite including hot-journal recovery, busy/unavailable/misconfigured cases, stop/restart and store/schema failure.
- Test seven-day detail cleanup while excluding preparing/active/unconsumed/unresolved outcomes, preserved deduplication tombstones, cancellation evidence, explicit purge and no source-artifact deletion.
- Test the 10,000 live/unconsumed wait and 1,000 active-source limits, typed admission refusal and continued status/cancel access; keep fixtures small by injecting test policies without changing production defaults.
- Test explicit retry/rearm/rebind validation, same-user provenance display, safe command arguments and state-home override failures. Test absent-store creation and explicit maintenance backup/migration failure without schema reset. No separate PBT is needed.
- Test the launcher and CLI with an omitted home, a canonical default-home alias and an explicit isolated home; rejected invocations leave the default home untouched.

Classes and behavior:

- operations.py provides status/cancel/retry/rearm/rebind/stop/restart and terminal cleanup/purge actions through existing service decisions; manual retained-result behavior stays explicitly labeled.
- cli.py composes store, scheduler, transport and synthetic ports and dispatches bounded commands with typed diagnostics; runtime.py gains this composition without import cycles. Client commands use explicit resolved repository/artifact/host identity.
- bin/wait_service.bat follows shared-root/Python resolution and hidden-launch rules; startup/status never needs a model call. Offline status owns the singleton through database recovery/snapshot, never migrating it.
- Carry the temporary explicit-home-required guard through launcher, CLI and runtime. Every development/manual command supplies an isolated home until Step 8's recorded rollout patch; documentation alone is not the guard.
- Expose schema-maintenance action with explicit local request and recoverable backup; do not invent an upgrade path from an unknown schema. Tombstone purge discloses loss of deduplication history and affects only service-owned history.

Completion criteria:

- Local diagnostics and cancellation remain usable at capacity, no offline reader opens a locked store, and cleanup cannot delete work still awaiting handling.
- Targeted tests and the shared `ghog day` walk pass with recorded evidence.
- Inspect this contract search and the affected diff:

```text
rg -n 'capacity-exceeded|schema-incompatible|retained-result-only|purge|offline' tools/wait_service
```

#### Step 7 addendums

Line-budget checkpoint:

- [ ] Recount each listed file at execution time; all current baselines are 0,
  with later-step extensions inheriting their actual earlier-step counts.
- [ ] Every listed Python file starts in the below-550 safe band; the mandatory
  ceiling is 650, including tests and initializers. No tighter target is imposed.
- [ ] At 550 through 650, assess growth and apply the split guidance if the
  ceiling would be crossed; above 650, split before step completion.

Split guidance: Keep CLI parsing/composition under 650 by leaving lifecycle and retention in operations.py; split operations into retention versus recovery only when responsibility/ceiling requires it.

Complexity and feature preservation: use the
[shared complexity/I/O rules](#complexity-and-file-based-io-cost-clarification-for-the-plan);
do not add per-event repository scans, context loading or workflow authority paths.

Full workflow timing run readiness: the listed test leaves identify the focused
Groundhog inputs; record that run and the shared `ghog day` result after code
exists. No timing or full-coverage result has been measured for this step yet.

Time-gated status for Step 7: Retention ages and capacity thresholds use injected fixtures. Count status reads and page bounds; startup readiness retains the 15-second contract. No live sleeps in unit tests.

### Step 8. Validate integrated core and publish item 1 evidence

#### Step 8 analysis and intent

Unit fixtures cannot prove Windows process survival, ACL enforcement or real recovery after suspension. Exercise the real composed service with synthetic sources/hosts and keep those results separate from native-prototype and future production-service measurements.

Expected outcome: Prove the assembled Windows core and record exactly what item 1 establishes for later adapters.

Step framing: [settled design section](design.v0.13.0.shared-wait-service.md#acceptance-evidence-and-closure-boundaries);
requirement coverage: AC-01 through AC-16; item 1 closure, with strict/service evidence carried to item 8. Apply the
[shared execution checklist](#shared-execution-command-checklist-for-all-eight-steps)
and [command forms](#ready-to-run-command-forms-for-shared-wait-steps).
Keep changes inside the listed responsibilities and preserve existing workflows.

#### Step 8 implementation

Files involved, with the measured current baseline:

| File and state | Physical baseline | Python policy |
| --- | --- | --- |
| `tests/unit/tools/wait_service/test_acceptance/__init__.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `tests/unit/tools/wait_service/test_acceptance/test_acceptance_tdd.py` (new, to be created) | 0 | Below 550, safe to extend; ceiling 650 |
| `docs/v0.13.0/verify.shared-wait-service.ps1` (new, to be created) | 0 | Non-Python, no Python ceiling |
| `docs/v0.13.0/acceptance.v0.13.0.shared-wait-service.md` (new, to be created) | 0 | Non-Python, no Python ceiling |
| `docs/v0.13.0/usage.v0.13.0.shared-wait-service.md` (new, to be created) | 0 | Non-Python, no Python ceiling |
| `docs/v0.13.0/probe-results.v0.13.0.shared-wait-service.md` (created in Step 2, extended here) | Step 2 count | Non-Python, no Python ceiling |
| `tools/wait_service/runtime.py` (created in Step 4, extended here) | Step 4/7 count | Recount: below 550 safe; 550 through 650 at risk; ceiling 650 |
| `tests/unit/tools/wait_service/test_runtime/test_runtime_tdd.py` (created in Step 4, extended here) | Step 4 count | Recount: below 550 safe; 550 through 650 at risk; ceiling 650 |
| `tools/wait_service/cli.py` (created in Step 7, extended here) | Step 7 count | Recount: below 550 safe; 550 through 650 at risk; ceiling 650 |
| `bin/wait_service.bat` (created in Step 7, extended here) | Step 7 count | Non-Python, no Python ceiling |
| `tests/unit/tools/wait_service/test_operations/test_operations_tdd.py` (created in Step 7, extended here) | Step 7 count | Recount: below 550 safe; 550 through 650 at risk; ceiling 650 |

Tests first:

- Add integration-size scenarios in the established tests/unit/tools/.../test_acceptance/test_acceptance_tdd.py layout: real temporary SQLite plus composed runtime/ports, several repositories/recipients, event storms, restart and consumed/cancelled outcomes. Treat this suite as acceptance evidence, not a unit coverage claim.
- Use the standalone Windows verifier for real named-pipe peer/ACL and startup races, hidden child survival after parent exit, explicit isolated homes, store reopen/hot-journal locking and cleanup of only that run's owned resources.
- Run bounded real Windows sleep/resume with synthetic source/host, covering unchanged indefinite, completed/expired, queued/cancelled/consumed states and retained IDs. Record requested/actual suspension, UTC/monotonic evidence and finite recovery bounds separately from awake baseline trials.
- Keep crash-boundary/PBT tests in their owning steps; acceptance combines those behaviors through actual public entry points. Synthetic foreign-user cases remain required even if a second-user live fixture is unavailable, which must be reported.

Classes and behavior:

- verify.shared-wait-service.ps1 orchestrates only explicit isolated-home runs and writes local raw logs; it validates resolved ownership before cleaning its own fixtures and never targets the default service home or workflow artifacts.
- usage...md documents start/register/status/stop/restart, same-session recovery, explicit rebind/retry/purge, compatibility and typed fallbacks using exact installed invocations. No instruction migration or production adapter is added.
- acceptance...md records AC-by-AC evidence, commands, builds, timings and limitations; probe-results...md remains explicitly A/B-prototype. Preserve the validated collector and replay it against captured fixtures.
- Before item 1 closure require core fixtures, collector, native prototype reports, per-host findings, live synthetic Windows recovery and at least one passing functional route. Carry incomplete request coverage/strict support and actual A/B-service to item 8; revalidate provisional host assumptions in later items.
- Roll out first to an explicit isolated home. Exercise default-home discovery only through an explicit local action and after checking existing compatible authority. Leave current review/Groundhog paths in operation until their later umbrella items.
- After isolated live acceptance, record the local rollout action and existing-authority compatibility check, then remove the temporary default-home guard in runtime.py, cli.py and bin/wait_service.bat. Update runtime/operations tests to cover released default discovery with an injected default-home location; automated tests never use the user's real home. Rerun affected Groundhog gates after this patch. Refuse incompatible authority; do not replace it or migrate unknown schemas.

Live operator procedure for Step 8:

1. The operator selects a Windows machine and explicit isolated state home and
   starts the verifier's synthetic source/host fixture. This core recovery run
   does not require or measure an LLM conversation. Any native-host evidence
   rerun uses Step 2's separate fresh-conversation procedure.
2. The verifier records run identity, pre-suspension states, UTC/monotonic
   evidence, requested duration and finite recovery bounds. It also records the
   commit and build identity of the service under test, so evidence gathered
   before the Q07 rollout patch stays attributable. The operator
   initiates and ends real Windows suspension through the documented local
   procedure, independently of the implementing conversation. The verifier
   records actual suspension/resume and validates retained states afterward.
3. Run second-user pipe-access checks only with an available independently
   configured account fixture. If unavailable, record that exact limitation and
   retain mandatory synthetic foreign-user rejection cases; never label those
   synthetic cases as observed live multi-user enforcement.
4. Retain the report and clean only fixture-owned resources using resolved
   identity/path checks. Keep awake A/B, live core recovery and later production
   adapter recovery evidence separately labeled.

Step 8 completion states, recorded separately:

- **Code complete**: composed acceptance tests, verifier and usage/report
  structure pass Groundhog; the rollout patch is separately tracked.
- **Live evidence recorded**: actual bounded Windows recovery and other live
  cases have results and limitations, plus Step 2's functional route finding.
  Missing required live recovery keeps Step 8 incomplete even with green code.
- **Rollout recorded**: after the isolated evidence gate, the Q07
  guard-removal patch, compatibility check and post-patch tests have evidence.
  The patch changes only the temporary guard; its diff is retained with the
  rollout record.
  No default-home use is authorized merely by a code-complete finding.

Completion criteria:

- A green Groundhog walk plus retained, bounded live Windows recovery evidence and functional route gate support the stated item 1 result. Missing live evidence remains an explicit incomplete gate; do not mark this step or umbrella completed from unit fixtures alone.
- Targeted tests and the shared `ghog day` walk pass with recorded evidence.
- Inspect this contract search and the affected diff:

```text
rg -n 'AC-0|AC-1|B-prototype|B-service|sleep|inconclusive' docs/v0.13.0/acceptance.v0.13.0.shared-wait-service.md docs/v0.13.0/probe-results.v0.13.0.shared-wait-service.md
```

#### Step 8 addendums

Line-budget checkpoint:

- [ ] Recount each listed file at execution time; all current baselines are 0,
  with later-step extensions inheriting their actual earlier-step counts.
- [ ] Every listed Python file starts in the below-550 safe band; the mandatory
  ceiling is 650, including tests and initializers. No tighter target is imposed.
- [ ] At 550 through 650, assess growth and apply the split guidance if the
  ceiling would be crossed; above 650, split before step completion.

Split guidance: Split acceptance cases by Windows lifecycle versus end-to-end delivery if the acceptance test file approaches 650. Keep the PowerShell driver thin and reusable logic in tested modules.

Complexity and feature preservation: use the
[shared complexity/I/O rules](#complexity-and-file-based-io-cost-clarification-for-the-plan);
do not add per-event repository scans, context loading or workflow authority paths.

Full workflow timing run readiness: the listed test leaves identify the focused
Groundhog inputs; record that run and the shared `ghog day` result after code
exists. No timing or full-coverage result has been measured for this step yet.

Time-gated status for Step 8: Fast acceptance fixtures use fake time. Live suspension, ten-minute feasibility and matched trials stay outside ghog and have predeclared finite observation bounds; never weaken unit timeout/outlier gates to accommodate them.

## Evidence handoff after Step 8

The validation document follows these same eight step numbers. Its initial
status stays unimplemented until checks replace the placeholders. If plan review
changes the step sequence, update both documents together.

Later item 3 must take the durable intent/settlement/human-abandonment obligations
into the real review ownership and pickup paths. Later host items must re-prove
their native normal-end gate, exact-recipient wake and recovery behavior. Item 8
must reuse the first item's manifest, phase, context and coverage methodology
against the actual service and first available production route. Retain all
prototype evidence under its original label.

Do not mark the umbrella row complete during planning or from a partial test
pass. The final implementation-check workflow owns that update after the
recorded closure gates are satisfied.

## Implementation decisions for the shared wait service

Review round 2 and the human consolidation choice settle all seven answers as
option A. No further question blocks implementation; the environment prerequisite
and each step's evidence gates still apply.

| Question | Decision | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | Extend Step 1 telemetry.py and its tests for inspected host schemas, keeping one normalization path and explicit unknown coverage. | [Step 2 files and behavior](#step-2-implementation) | Requiring real parsers and fixtures in Step 1 would move installed-host investigation ahead of its owning step and delay the feasibility probe. |
| Q02 | Predeclare the initial 60-second wake bound and 120-second duplicate window per host/version series; first useful continuation ends wake latency, with a separate 120-second telemetry drain. Changed bounds start a new series and retain earlier failures. These classify evidence, not service policy or guaranteed host latency. | [Step 2 manifest and operator procedure](#step-2-implementation) | Initial 120-second wake and 300-second duplicate bounds add several minutes per run and set a less demanding wake criterion. |
| Q03 | Add the test_windows_ipc leaf and initializer, exercising native-call errors, SID/ACL handling and cleanup without removing the adapter from unit coverage. | [Step 4 files and tests](#step-4-implementation) | Keeping native cases inside runtime/protocol leaves makes direct adapter coverage harder to establish and can hide cleanup gaps. |
| Q04 | Use a small bounded subprocess crash matrix with durable barriers, forced termination without cleanup and reopening both stores; keep exhaustive permutations in-process. | [Step 6 crash tests](#step-6-implementation) | In-process exceptions with real process death deferred to Step 8 would leave OS lock-release assumptions unproved in Step 6. |
| Q05 | Keep resource assertions and timeout guards in Steps 1, 4, 5, 7 and 8, with fake time for contractual intervals and separate live evidence runs. | [Timeout gates and Step 0 assessment](#timeout-gates-and-the-step-0-assessment) | A separate Step 0 or xfail suite has no existing measured regression to capture and would defer required checks. |
| Q06 | Smoke-test each absolute standalone script from the checkout and another cwd with the verified project interpreter and explicit paths; locate imports from the script itself. | [Step 1 entry point](#step-1-implementation) and [Step 2 entry point](#step-2-implementation) | Project-root-only checks would hide import/bootstrap dependencies on cwd or PYTHONPATH. |
| Q07 | Require an explicit nondefault isolated home before discovery or resource creation until Step 8 records isolated acceptance, compatibility and a guard-only rollout patch with post-patch tests. | [Step 4 runtime](#step-4-implementation), [Step 7 commands](#step-7-implementation) and [Step 8 rollout](#step-8-implementation) | Allowing default-home startup in development would rely on operators always remembering an override. |
