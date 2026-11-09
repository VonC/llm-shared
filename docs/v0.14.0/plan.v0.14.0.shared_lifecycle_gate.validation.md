# v0.14.0 shared lifecycle gate implementation tracking and validation

No, it is not implemented

Steps 1-4 of the seven-step
[implementation plan](plan.v0.14.0.shared_lifecycle_gate.md) have been checked,
including Step 4 on 2026-11-09. Steps 5-7 remain not started; their goals
describe later checks.

## Runtime context for validating the pytest plugin mechanism

The feature exposes lifecycle timing and process auditing as independently
selected pytest plugins. A plugin is a Python module registered with pytest
for execution hooks, so these checks can enforce test setup through teardown
in the consuming project's own interpreter without installing llm-shared.

Validate the complete route: project `senv.bat` selects the checks and calls
`bin/prepare_pytest_plugins.bat`, whose shell adapter uses the environment
builder; Windows transport applies only a complete successful
result to the calling shell; ordinary pytest starts its loader, validates the
selection and registers the checks before tests. The builder must not import
policies, and the loader must not run tests after failed selected preflight.

Groundhog, the shared test-loop tool, uses that same builder for every pytest
child and passes the environment directly, without shell serialization or
policy imports into groundhog. The [plan walkthrough](plan.v0.14.0.shared_lifecycle_gate.md#the-pytest-plugin-mechanism-this-plan-implements)
maps the runtime to Steps 1-7. Step 4 checks the shell-transfer boundary chosen
in Q02=B1; Step 5 checks the direct groundhog route. Neither route changes the
consumer's Python environment or substitutes llm-shared's interpreter.

## File-based IO cost clarification for v0.14.0 validation

Verify fixed-input preparation and source-hash bootstrap publication, no
per-event filesystem work, one session/worker record load and one controller
write per run. The compatibility declaration uses a named input, while every
required day/full invocation obtains fresh executable evidence. Inspect counted
operations and failure paths as well as elapsed time; never substitute cached
compatibility results or a recreated artifact home for the designed behavior.

## Complexity boundaries for v0.14.0 implementation checks

Check constant-time clock/authorization events, indexed collection validation
and linear record/report processing. Deterministic summary sorting stays out
of the hot path. Enforce the 650-line Python ceiling against fresh physical
counts; advisory estimates are not tighter gates. Require bounded external
worker/process cleanup and preserve process-free own-suite validation.

## Step 1. Standalone lifecycle policy and record continuity

### Analysis of Step 1 implementation state

Yes. Step 1 has been fully implemented.

The standalone gate, isolated contracts and static discovery configuration
are present. Existing timing/record assertions now import the canonical
module. The default day and subsequent full-speed review validation passed;
the legacy own-suite enforcer remains
in place until Step 3, as planned.

### Goal for Step 1

Extract the canonical stdlib/pytest-only gate while preserving all original
clock, report, configuration, proof, exception and record assertions.

### Step 1 improvement expectations

- Preserve schema 1, current-ceiling eligibility, diagnostics and controller writes.
- Keep strict behavior without a valid pre-existing artifact home.
- Add settings/record invariants without a consumer Hypothesis dependency.
- Apply Ruff py310 and Pyright 3.12 targets before the first standalone file.
- Share the isolated, explicit-plugin inline session helper within current limits.
- Expose a guarded literal contract version without preparing-process imports.

### What was implemented for Step 1

`tools/pytest_plugins/llm_shared_lifecycle_gate.py` contains the stdlib/pytest-only
policy, record model, measurement hooks and controller collector. Its Python
3.12 refusal precedes all imports except `sys` and `pytest`; the literal
`LOADER_CONTRACT_VERSION = 1` follows that guard. Strict artifact lookup copies
ConfigParser behavior, including DEFAULT inheritance, and requires an existing
contained directory with exact `b"*\n"` ignore bytes. It creates no home and
imports no shared artifact helper.

`pyproject.toml` exposes the dedicated module directory to pytest, Pyright and
ty, applies Ruff py310 and Pyright 3.12 targets, and retains coverage source
`tools` without plugin omissions. Original policy and CPU-band tests change
imports only; the new contract tests cover artifact failures, synthetic record
continuity, configuration precedence, guarded registration in both orders,
usage-error refusal, source syntax and dependencies, version refusal, proof
transitions and serialization properties.

`inline_session.py` shares the isolated explicit-plugin child session, restores
host state and removes newly imported project modules. Verification also required
the Testmon adapter to use its ordinary source/hash fallback instead of invoking
Git under the existing process audit; a focused regression retains source/hash
and missing-file behavior. Named lifecycle overruns in configuration properties,
duration properties, PNG output, resume selection and proof rendering were
shortened while retaining assertions and property domains. A review-document
list reflow changes no wording. The shipped-package contract derives its root
from its own package module, avoiding unrelated workflow fingerprints while
retaining real package validation and both assertions.

### New types or classes introduced for Step 1

The frozen `NodeState` carries proof, drift count, CPU and the CPU that earned
proof; `CpuException` carries accepted CPU, attempted improvement and reason;
`BandPolicy` validates settings and computes band ceilings. `LifecycleRecord`
contains nodes, accepted exceptions and rejected keys, and advances measured
proofs. `SaveOutcome` records persistence results and lost proofs.
`LifecycleGate` loads policy/record state, judges limits and saves updates.
`BandCollector` gathers teardown properties and performs controller persistence
and summary reporting. These are relocated policy types, not new consumer
dependencies.

### Architecture check for Step 1

The policy owns its minimal persistence adapter and depends only on stdlib and
pytest. It installs no audit hooks and imports neither suite packages nor
shared runtime helpers. The suite-only Hypothesis dependency stays in tests.
Importing the module alone does not register another collector. Legacy
`simulation_policy.py` and `lifecycle_cpu_record.py` remain unchanged.

Fresh physical counts are 602 for the gate, 53 for the inline helper, 263/54
for new contracts and 111/363 for redirected legacy tests. The package markers
are 1-4 lines; the Testmon adapter/regression are 59/24 lines. All other changed
Python tests are at most 360 lines, below the 650-line ceiling.

No architecture issue needs addressing.

### Performance check for Step 1

Clock samples and per-report state updates are constant time. Record parsing,
advancement and ordinary rendering are linear in their inputs. Deterministic
record-key, lost-proof and terminal-summary sorting retains the inherited
O(n log n) ordering outside the timing hot path; no new quadratic work appears.
The gate loads once per configured process and saves once on the controller.

`ghog day --whole-suite` finished at 2026-11-08T14:15:03+01:00 with
`state=done`, `exit=0`, `fail=0`, `warn=0`, `xfail=0`, `full=none`.
The preceding focused repair and affected run also passed. Timing repairs
avoid unused embedded-session work and repeated immutable observations while
retaining real proof/SQLite/render boundaries. No exclusion was added.

The subsequent required review walk, `ghog day --full=speed --whole-suite`,
finished at 2026-11-08T14:35:09+01:00 with `state=done`, `exit=0`, `fail=0`,
`warn=0`, `xfail=0`, `cov=100`, `outliers=0`, `excluded=0`, `proof=speed`.
It passed all 5,780 tests. A preceding package-contract wall overrun was
profiled; its unnecessary workflow dependency was removed, with assertions
and real package validation preserved. No accepted baseline was added or raised.

No performance issue needs addressing.

### Unit test coverage check for Step 1

The coverage configuration measures `tools`, including the standalone gate;
suite helpers under `tests` lie outside that source scope. This check is static:
no test or coverage command was run during implementation-check, and the
default day establishes no measured coverage percentage. Separately, the
subsequent required full-speed review walk measured 100% coverage over that
configured source scope; it ran outside implementation-check.

`test_lifecycle_policy.py` and `test_lifecycle_cpu_band.py` retain the tests
designed to cover the complete timing/record class file. They cover clock
windows, report properties/verdicts, configuration refusal, proof/drift,
exceptions, damaged/missing records, save failures, controller registration
and summary output. The dedicated `test_gate_contract` folder adds strict
artifact parsing/containment/IO, round-trip and current-ceiling contracts,
configuration and import boundaries, plus bounded property oracles. All
top-level gate symbols are reached through these tests or internal calls.

The Testmon regression references its source/hash adapter and live bindings;
its configure/protocol hooks are registered by the suite. The inline-session
helper and all added property-decoding helpers are referenced by their tests.
Static inspection identifies no unit-tested class requiring coverage completion.
No top-level symbol outside the coverage scope is unreferenced.

### Feature integrity for Step 1

Schema 1, unknown document fields, accepted exception evidence, proof eligibility
under the current ceiling, failure wording, wall aggregation, report-hook CPU,
teardown properties and controller-only writes are preserved. Existing legacy
assertions are unchanged. Synthetic record continuity is covered; Step 7 still
owns continuity against the real checkout record. No record was deleted or
migrated.

Executed evidence is Windows with Python 3.13. Python 3.10 syntax parsing,
the pre-refusal import test and static 3.12 targets do not claim an executable
Python 3.12 or cross-platform harness run. The independent audit, loader,
preparation and compatibility harness remain later steps. No Step 2 work is
included in this verdict.

## Step 2. Independent process sessions and fixture ownership

### Analysis of Step 2 implementation state

Yes. Step 2 has been fully implemented.

Round 1's four correctness findings are fixed with regression coverage. The
fresh whole-suite speed day passed after those fixes and the timing repair.

The standalone audit validates declarations before setup, enforces the preserved
process window and binds fixture ownership to live operations on their executing
thread. Focused ownership/declaration tests, the resolved day and the subsequent
covered day passed. Worker coordination and reporting remain Step 3 work.

### Goal for Step 2

Implement the approved process window, declarations, guarded dispatcher and
thread/token-bound fixture ownership without gate dependencies.

### Step 2 improvement expectations

- Preserve event rejection outside permissions and safe nested-session detach.
- Validate actual decorated fixture identities and original marker levels.
- Unwind ownership and restore only owned wrappers after the last detach.
- Declare the module-level literal contract after its Python-version guard.

### What was implemented for Step 2

`tools/pytest_plugins/llm_shared_process_audit.py` owns one sys-guarded lifetime
dispatcher and per-configuration audit state. Reloads and alias imports reuse
the hub; an active-session stack selects the innermost active test, including
the outer test during a child's collection. Detach restores the outer session.
The preserved nine process events are enforced throughout setup, call and
teardown, with carrying-test/event diagnostics.

Collection validates original class/module marker levels, named function and
parameter reasons, unused fixture declarations, actual decorated objects,
imported definitions, ambiguity and conflicting reasons. The registry is indexed
once. Definition identities retain relative source, qualified and declared names,
registration base and scope; parameter instances share one exercised record.
Sources on another Windows drive retain an absolute POSIX path. Failed
collectors are skipped without retrying their objects; all other declarations
are validated even with continued collection errors.

The bounded adapter checks fixture/conftest registries, unwrap and execution/finalization
capabilities. Execute masks requesting ownership during dependency/cache access;
the setup hook and finish adapter enter actual own work. Nested operations
replace and restore ownership; live thread-local tokens unwind on failure.
Only the final detach restores callables, and only while still adapter-owned.
Fixture permissions take precedence; unexempt function fixtures may use the
carrying test permission, while broader scopes cannot. Credit is exclusive.

The two new test packages use synthetic events and real in-process pytest
fixture definitions. The shared inline helper now leaves capture to the parent
session, avoiding redundant Windows console initialization with all output
assertions preserved. Package markers are present.

### New types or classes introduced for Step 2

- `Permission` records an exercised definition/test, reason and exclusive use.
- `AuditSession` holds declarations, active lifecycle, collectors and records.
- `_Operation` binds a fixture/session owner to a live thread-local token.
- `AuditHub` owns attachment, dispatch and bounded pytest instrumentation.
- `Fixture` and `FixtureCall` name the pytest definition and adapter signatures.

### Architecture check for Step 2

The standalone policy imports only stdlib and pytest. Its Python 3.12 refusal
precedes runtime imports and its literal loader contract follows the guard.
Session/declaration policy stays in `AuditSession`; technical pytest ownership
instrumentation stays in `AuditHub` and hook adapters. No timing settings,
CPU-band collector, gate records or shared runtime helper is imported.

Fresh physical counts are 395 for the audit, 353/293 for declaration/ownership
tests and 54 for the inline helper; package markers are below the 650-line limit.
No architecture issue needs addressing.

### Performance check for Step 2

Dispatch uses event membership, active-session/owner access and permission
dictionary lookups, with no filesystem IO or declaration scan. Collection
indexes fixture definitions once and traverses declaration sources/items
linearly. Ownership push/pop is constant time; detach traverses attached
sessions. No new quadratic or sorting path is introduced.

`ghog day --whole-suite` passed at 2026-11-08T17:54:02+01:00 with `exit=0`,
`fail=0`, `warn=0`, `xfail=0`. The subsequent
`ghog day --full=cov --whole-suite` passed at 2026-11-08T17:56:52+01:00 with
`exit=0`, `cov=100`, `proof=cov` and the same zero failure/warning/xfail counts.
These runs precede this static implementation check. Review preflight then
passed `ghog day --full=speed --whole-suite` at
2026-11-08T18:16:45+01:00: `exit=0`, `cov=100`, `proof=speed`, with zero
failures, warnings, xfails, outliers or exclusions.

After the four accepted round 1 fixes, 82 focused declaration/ownership cases
passed. The fresh `ghog day --full=speed --whole-suite` finished at
2026-11-08T18:58:13+01:00 with `exit=0`, `cov=100`, `proof=speed` and zero
failures, warnings, xfails, outliers or exclusions. Static checks passed.

An initial first-use lifecycle CPU overrun was profiled: redundant child
capture initialized Windows console/colorama support. Disabling only child
capture reduced diagnostic cold CPU from 0.312s to 0.172s; the affected repair
and both days passed afterward. Speed preflight also profiled redundant parent
pytest startup in the combined reload/alias/nesting test. Independent import
checks and reuse of the carrying pytest config preserve all assertions with
one real child session. The original combined case measured 0.125s CPU;
the passing covered speed walk measured 0.03125s for nesting and 0.015625s
each for reload and alias. No exclusion or budget change was added.
The strengthened nested test subsequently exceeded its lifecycle CPU band
at 0.28125s. Profiling identified child debugger/progress startup support;
disabling those two plugins only for that case preserves the reporter and
all ownership assertions. Diagnostic cold CPU fell from 0.171875s to 0.046875s;
the affected repair and fresh full speed day passed with unchanged budgets.
No performance issue needs addressing.

### Unit test coverage check for Step 2

The configured source is `tools`, including this audit without an omission;
the completed covered day measured 100% over that source scope. This check
runs no test command. Static review maps declaration, identity and adapter
capability paths to `test_audit_declarations`, and runtime ownership/credit,
all event phases, nesting, reload/alias, thread/context rejection, failure
unwind and callable restoration to `test_audit_ownership`. Together they
exercise the complete standalone class file. Finite parametrized matrices
cover the approved boundaries; a separate property suite is not required.

The helper under `tests` is outside measured source scope; its `run_inline`
symbol is referenced throughout both new packages and existing gate contracts.
Every audit top-level type/function is referenced by tests, internal calls or
pytest hook registration. No unit-tested class below 100% needs completing.
No top-level symbol outside the coverage scope is unreferenced.

### Feature integrity for Step 2

The existing suite enforcer and lifecycle gate remain unchanged. Process event
names/window and rejection attribution are preserved; fixture caching, setup
failure caching, yield teardown and registered finalizers remain pytest-owned.
Nested sessions restore outer state and later third-party wrappers are retained.
No existing feature or reporting capability appears impaired.

Evidence uses Windows/Python 3.13, synthetic process events and embedded pytest.
Source parsing and static targets do not claim executable Python 3.12 coverage.
Step 3 retains the all-worker barrier, aggregated summaries and suite migration;
Step 6 retains actual process/compatibility harness scenarios.

## Step 3. Worker barrier, summaries and own-suite migration

### Analysis of Step 3 implementation state

Yes. Step 3 has been fully implemented.

Workers validate before announcing collection, and the controller rejects
missing or inconsistent evidence and merges permission usage. Real Python
3.13 smoke evidence preceded migration to the canonical policies. The fresh
whole-suite speed walk passed with 100% tools coverage.

### Goal for Step 3

Stop scheduling after any invalid declaration, combine permission summaries
once, and load the two shared canonical policies after coverage starts.

### Step 3 improvement expectations

- Require validated worker announcements and stop on missing/error evidence.
- For Q01=A3, require actual Python 3.13 xdist smoke evidence before migrating
  the suite or deleting the legacy policy. Check invalid-worker announcements,
  no test starts on valid peers, controller exit 4, bounded cancellation and
  cleanup outside the audited suite. Record versions and outcomes separately
  from modeled unit evidence; this is no Python 3.12 compatibility claim.
- Verify Step 3 creates the shared harness runner/scenario/package markers and
  process-free compatibility tests, covers their code under the tools gate
  and assigns Ruff/Pyright Python 3.12 targets. Retain those files for Step 6
  extension; independent 3.12 manifest/provisioning stays in Step 6.
- Aggregate exercised permissions by stable identity with own-scope usage credit.
- Remove legacy policy sources without changing assertions or adding exemptions.
- Snapshot the existing record before first migrated execution and compare afterward.
- Preserve canonical imports and verify the existing shell selects neither policy.

### What was implemented for Step 3

- `llm_shared_process_audit.py` validates declarations in a first-priority
  collection-finish hook before xdist announces collection. Controller hooks
  count initial workers, reject inconsistent collections and early exits,
  and preserve identifying declaration errors with controller exit 4.
- The initial barrier stays complete after replacement announcements. Later
  crashes and keyboard interrupts retain xdist handling; crashes may omit
  records, while successful workers must send them. Any transported records
  are validated. Controller shutdown before the barrier, including collection
  failure with `--maxfail`, preserves the existing stop reason.
- Worker permission transport contains detached records. The controller
  validates definitions and reasons, merges usage with boolean OR, and emits
  separate test/fixture summaries once per stable identity. Unused exercised
  permissions produce warnings; unexercised declarations remain absent.
- The minimal `tools/lifecycle_compatibility/` runner generates isolated
  projects, bounds controller waits and cleans up remaining workers. Its
  process-free tests retain actual project construction and verdict logic.
  Ruff/Pyright target those harness files at Python 3.12.
- Real Windows smoke probes ran before migration using Python 3.13.9, pytest
  9.1.0 and xdist 3.8.0. Invalid declarations, early worker exit and mismatched
  collections each observed a valid peer announcement, no setup/body starts,
  controller exit 4 and both workers reaped. Refactored-runner probes repeated
  those outcomes. Private summaries remain in the step artifact home.
- `tests/conftest.py` now loads both canonical policies after coverage starts.
  Existing assertions passed against them before the two legacy sources were
  removed. Native-event assertions now expect the canonical audit diagnostic.
  Synthetic policy tests isolate their hub while the carrying dispatcher
  continues enforcing real events without permissions.
- The read-only pre-migration record snapshot and first migrated comparison
  remain private for Step 7. Exception content/meaning and other fields were
  preserved; all 5892 previously eligible proofs remained, with 9 added and
  no missing nodes or lost eligible proofs. Normal later timing drift remains
  live; the snapshot was never restored over the record.
- Source scans found no executable legacy-policy references, package-qualified
  policy imports or automatic policy selection in the unchanged `senv.bat`.

### New types or classes introduced for Step 3

No new production class was needed. `AuditSession` gained worker-announcement,
collection and merge state. Harness functions handle environment isolation,
project generation, bounded execution, cleanup and evidence aggregation.
The test transport uses a local `Child` double to observe process boundaries.

### Architecture check for Step 3

The standalone audit still imports only stdlib and pytest. Worker coordination
and reporting stay in its pytest adapter; executable compatibility orchestration
lives separately and is never imported by the policy. No DDD-Hexagonal layer
violation or extra standalone runtime dependency was found.

Physical Python line counts: audit 497; suite conftest 101; isolated-state
conftest 37; inline helper 62; worker tests 300; compatibility tests 248;
runner 132; scenarios 75; changed boundary/source-scan tests 89/83. Package
markers contain 1 to 4 lines. Every file remains within the 650-line ceiling.

No architecture or size issue needs addressing.

### Performance check for Step 3

Worker collection comparison, record transport/merging and summaries are linear
in their inputs; event ownership work remains constant time. No new quadratic
or sorting computation was introduced. A source scan now reads each file once
for all markers: actual-function profiles fell from 144 reads/0.115832 s to
36 reads/0.014754 s while retaining all checks.

Profiles of embedded pytest tests identified unused debugger/progress startup
and plugin registration. Generated sessions omit those plugins and unused
temporary-directory/legacy-path support, retaining real collection, fixtures,
warnings and terminal reports. The later gate profile measured CPU 0.125 s
both before and after; variable wall results do not establish an isolated
improvement for that case. Focused tests and the final integrated walk passed.

Round 2 review found 31 wall-limit overruns across 19 files without assertion
failures. Those files and the worker tests passed in focus. Profiling the
flagged process-event test identified embedded pytest startup as the largest
cost. Omitting the unused child assertion plugin retains plain Python
assertions and reduced that actual-function profile from CPU 0.171875 s /
wall 0.186358 s to CPU 0.078125 s / wall 0.101997 s. The complete shared
lifecycle focus and fresh integrated walk passed afterward with unchanged
budgets and no exclusions.

`ghog day --full=speed --whole-suite` completed on 2026-11-09 at
11:05:14+01:00 with fresh speed proof, no reused result, exit 0, no failures,
warnings, expected failures, outliers or exclusions. No budgets were raised.

No performance issue needs addressing.

### Unit test coverage check for Step 3

The configured coverage source remains `tools`, with a 100% gate and no new
omit. Static inspection ties each added audit branch to worker tests covering
announcement order, early exit, conflicting collections, invalid declarations,
detached transport, malformed records, reason conflicts and OR usage. Serial
summary assertions exercise both scopes, unused warnings and omitted work.
Regressions reject a normally finished, announced worker whose output omits
the permission-records key, and cover post-barrier crash output with and
without records,
replacement announcement/finish and mismatch, both keyboard-interrupt down
notifications before and after the barrier, and controller shutdown before
collection announcements. The module-entrypoint test fixes its platform to
the mocked Windows transport, preventing real POSIX signal probes.
Compatibility tests cover actual scenario generation, environment isolation,
each verdict condition, timeout/worker cleanup, Windows/POSIX boundaries and
CLI aggregation without starting processes. The completed walk reports 100%
for the measured tools scope; the real smoke is separate executable evidence.

Test files and helpers lie outside that coverage scope. Their top-level tests
are collected by pytest; fixtures are requested or automatic; `run_inline`,
transport helpers and existing AST/source helpers have explicit references in
their test packages, including fixture and module-level uses. No property test
was needed for the finite worker/transport/verdict matrices enumerated here.

No unit-tested production file below 100% needs completing. No top-level
symbol outside the coverage gate is unreferenced.

### Feature integrity for Step 3

Existing timing, record/proof semantics, event coverage and unrelated suite
plugins remain intact. The carrying audit received no process permission.
Audit-only summary tests create no lifecycle record or gate output. Migration
retains actual native-event rejection and all source-lock checks.
Distributed failures after validation retain their original xdist outcomes;
declaration failures and unexplained exits before the barrier remain exit 4.

Executable evidence covers Windows/Python 3.13 only. Independent Python 3.12
execution, recurring compatibility preflight and the broader harness remain
Step 6 work; shell preparation and early loading remain Step 4 work.

## Step 4. Immutable preparation and canonical early loading

### Analysis of Step 4 implementation state

Yes. Step 4 has been fully implemented.

The environment builder, immutable loader cache, separate Windows transfer
adapter and standalone early loader implement the settled activation boundary.
Focused tests and the resolved full speed day passed. Executable caller-shell
acceptance remains in Step 7 as planned; groundhog integration remains Step 5.

### Goal for Step 4

Implement the settled root-bound selection and immutable loader bootstrap,
with all-selected preflight before canonical policy registration. For Q02=B1,
verify that `tools/pytest_plugin_shell.py` owns Windows serialization, escaping
and transfer-output cleanup while consuming the same environment builder as
groundhog. Its focused package is
`tests/unit/tools/shared_lifecycle/test_shell_transport/`, containing
`__init__.py` and `test_shell_transport_tdd.py`; all three Python files have
zero-line baselines and the same 650-line ceiling.

### Step 4 improvement expectations

- Preserve unrelated environment entries and idempotent deselection.
- Reject stale, corrupt, mismatched or blocked selections before test execution.
- Preserve consumer packages and independently prepared checkout bindings.
- Verify source presence and literal contracts without importing selected policies.
- Check complete-result transfer, spaces and percent/exclamation/caret/ampersand/
  quote preservation, failure before application and transfer-output cleanup in
  focused process-free tests. Require actual calling-shell evidence from the
  Step 7 executable acceptance harness, without a second preparation algorithm.
- Cover both caller delayed-expansion states in focused tests and in the
  Step 7 executable evidence.

### What was implemented for Step 4

- `tools/pytest_plugin_environment.py` normalizes and deduplicates selection,
  rejects unknown tokens, recomputes owned paths/options, preserves unrelated
  environment entries and returns an independent complete environment.
- Preparation reads the loader and selected policy sources without importing
  their bodies. AST inspection requires one literal integer contract. Only
  the loader is published under its source SHA-256 in user-local storage
  outside both checkouts. Existing entries are verified without repair;
  same-parent publication handles races and removes interrupted scratch data.
- `tools/pytest_plugin_shell.py` calls that builder once, serializes every
  owned key, escapes delayed expansion when enabled, rejects unrepresentable
  records and encodes them in the caller's active console code page. Python
  exclusively creates each transfer file and discloses its name only after
  the complete write. A failed preparation removes only its own output.
  The batch launcher applies only an existing successful result, with no
  clock-seeded transfer names. Drive-root arguments have no trailing slash.
- `tools/pytest_plugins/llm_shared_pytest_loader.py` refuses old interpreters
  before later imports, validates every selected live source before importing
  policies, rejects missing/foreign modules and mismatched contracts, and
  converts selected import failures to identifying pytest usage errors.
- The initial-conftest hook checks project containment and every canonical
  identity before registration, rejects blocked selections, and reuses
  existing canonical modules. The loader imports only stdlib and pytest.
- Three focused test packages cover preparation, properties, transfer and
  startup. Existing memory-backed scratch routing includes these packages,
  retaining process-free own-suite scenarios.

### New types or classes introduced for Step 4

`PreparationError` is the builder/transport configuration exception. The
implementation otherwise uses functions, immutable selection tuples and
independent environment dictionaries; no new runtime service class is needed.

### Architecture check for Step 4

Selection and environment computation stay in the shared builder. Windows
encoding, publication and CLI handling stay in the shell adapter. The batch
launcher applies its result without duplicating selection. The standalone
loader has no shared-helper dependency and never exposes the shared repository
root or its `tools` package to consumers. Policies remain live and independent.
No domain-to-adapter dependency or DDD-Hexagonal violation was found.

Fresh physical counts are 226 lines for the builder, 112 for the shell adapter,
151 for the loader and 338 for the existing scratch router. The largest new
test file has 281 lines; every Python file remains below 650 lines.
No architecture or file-size issue needs addressing.

### Performance check for Step 4

Selection has two possible names. Path and option cleanup scan their input
once; source hashing and AST inspection are linear in named source bytes.
No new quadratic computation or input-size sorting was introduced. The counted
IO regression proves one read per required live source and cached loader on
both fresh and repeated preparation. Publication creates only a temporary
loader directory; preparation creates no consumer artifact home. Runtime
preflight is startup work and adds no per-test or per-event filesystem scan.

Property tests use bulk byte draws in 20 batches of five examples per property,
preserving 100 examples while keeping each measured lifecycle small. Focused
tests passed. `ghog day --whole-suite` finished with exit 0 on
2026-11-09 at 16:06:11 +01:00, with zero failures, warnings or expected failures.
Default day deliberately skipped full-suite coverage and duration reporting.
The final `ghog day --full=speed --whole-suite` finished with exit 0 at
16:08:38 +01:00 on the same date: 100% coverage, zero duration outliers,
zero exclusions and zero failures, warnings or expected failures.
This refreshed evidence includes all accepted round 1 transport and empty-path
repairs; no exclusion, process permission or budget was added.
No performance issue needs addressing.

### Unit test coverage check for Step 4

The configured line-coverage source is `tools`, using `sysmon`; all three new
production modules are inside that scope. The final full speed day measured
100% line coverage across that source scope. Static review finds dedicated tests for public entry
points and their helpers: invalid selection/contracts, deselection, repeated
preparation, preserved options, cache races/corruption/interruption, counted IO,
independent bindings, transport failures and both delayed-expansion states.
Transport regressions cover non-ASCII values under code pages 850 and 65001,
unrepresentable values and filenames, distinct outputs, failure isolation and
stdout failure cleanup. Selected preparation with an empty incoming
`PYTHONPATH` adds no empty entry.
The first full coverage report identified one uncovered empty-variable removal
branch. The owned-only deselection regression now verifies that no empty
activation variables remain, and the final full run covers that branch.
Loader tests cover selected imports, preflight order, missing checkout/cache,
usage errors, root containment, canonical identity conflicts, duplicate-safe
registration, the version guard and consumer package preservation.

The new exception class has no executable methods. No unit-tested class below
100% needs completing. The test/helper files outside the coverage source are
exercised by pytest collection or the existing scratch routing; no new top-level
symbol outside the coverage gate is unreferenced. Actual Windows execution
and a real Python 3.12 run remain their planned later acceptance checks.

### Feature integrity for Step 4

Empty selection leaves unrelated environments intact; deselection removes only
owned activation. Preparation never mutates the supplied environment or
imports policy bodies. Cache corruption fails without overwriting an entry.
Shell transfer preserves representable non-ASCII values and refuses the
complete result before application when its console code page cannot encode
it. Concurrent preparations own distinct transfer files; failure never deletes
another preparation's output. Step 7 retains the actual OEM code-page,
concurrency and drive-root executable checks.
Separate prepared environments retain their own checkout binding. Only-cache
removal uses the live loader; only-checkout removal still refuses selected
policies through the cached bootstrap. Explicit policy imports preserve
consumer `tools` and `tests` identities and do not change `sys.path`.
The environment-contract search contains only the three approved binding
variables, `PYTHONPATH` and `PYTEST_ADDOPTS`. Existing own-suite enforcement
and reporting passed the affected-test gate; no exemption or budget changed.

## Step 5. Prepared environments for every groundhog pytest child

### Analysis of Step 5 implementation state

Not started. Step 5 is not implemented because groundhog stages and collection
probes do not yet use the shared preparation contract.

### Goal for Step 5

Prepare every pytest child without changing the parent environment, consumer
interpreter, coverage overrides, worker caps or speed verdict.

### Step 5 improvement expectations

- Cover affected, single, timings, serial/xdist full and collection probes.
- Reject preparation errors before spawning and refresh stale project bindings.
- For Q05=E1, reject inherited bindings to a different project at invocation
  setup, before `check.bat`, the compatibility preflight and saved-proof reuse,
  comparing whole normalized roots with `invocation.root`, case-insensitively
  on Windows. Name bound root, target root and target environment setup. Cover
  nested projects and shared-prefix sibling roots beside same-project refresh.
  Cover every pytest stage and both collection probes, including fallback
  handling. Whole-day and direct-full tests assert zero spawns, unchanged
  sources and parent environment, and setup failure instead of saved-proof
  no-op. Include detached day before its launcher can spawn. Preserve
  no-binding no-selection behavior; commands that never start pytest retain
  their current behavior. Keep the loader's separate containment rule intact.
- Keep command-module growth within the 650-line ceiling through delegation.
- Remove owned environment entries for spawning and restore prior state on failure.
- Run self-hosted walks with the implementing checkout's groundhog launcher.

### What was implemented for Step 5

_(empty: no check has taken place yet.)_.

### New types or classes introduced for Step 5

_(empty: no check has taken place yet.)_.

### Architecture check for Step 5

_(empty: no check has taken place yet.)_.

### Performance check for Step 5

_(empty: no check has taken place yet.)_.

### Unit test coverage check for Step 5

_(empty: no check has taken place yet.)_.

### Feature integrity for Step 5

_(empty: no check has taken place yet.)_.

## Step 6. Fresh executable compatibility preflight

### Analysis of Step 6 implementation state

Not started. Step 6 is not implemented because the independent compatibility
harness, static entry checks and day/full preflight are pending.

### Goal for Step 6

Require verified real Python 3.12 executable evidence on each own-project
day/full invocation, including saved-proof paths, with no consumer prerequisite.
For Q03=C1, require the tracked `pyproject.toml` table
`[tool.llm-shared.lifecycle-compatibility]` with literal boolean `enabled = true`
and the fixed project-relative `bin/lifecycle_compatibility.bat` entrypoint.

### Step 6 improvement expectations

- Keep explicit provisioning separate from validation and reject missing prerequisites.
- For Q04=D1, resolve `venvs/python_3.12_lifecycle_compatibility/` from the
  project under test and provision explicitly from its independent manifest.
  Verify real version and dependencies against that manifest for both the
  default and absolute override; cover separate checkouts and differing pins.
  Check the directory name excludes `llm-shared`, sorts below the main runtime
  and leaves existing launchers selecting Python 3.13, including the root
  launchers `rvw_status.bat`, `markdown-check.bat` and `commit-plan-check.bat`,
  and `bin/mds.ps1`. Missing prerequisites
  must identify setup and override; validation never auto-provisions or changes
  a consumer environment.
- Validate real policy/process/fixture/xdist behavior outside the audited suite.
- Extend Step 3's runner/scenario and process-free coverage tests for real
  Python 3.12; retain its earlier 3.13 barrier evidence. Create the independent
  manifest/provisioning, static-entry checks and recurring preflight here,
  without duplicating the harness or weakening coverage/static targets.
- Preserve 100% tools coverage and statically inspect the Python 3.10 refusal path.
- Order Step 5's binding check, the preflight, then proof reuse or spawning;
  run preflight before no-op/upgrade reuse and once per day or direct full.
- Resolve the fixed harness entrypoint and policies from the project under test.
- Validate Q03=C1 missing table/key, false, invalid types and invalid table
  shape. Absence/false adds no preflight requirement; malformed explicit
  declarations fail before proof reuse or spawning, with an identifying setup
  diagnostic. Verify no command is executed from TOML.
- Reject missing declared entrypoints and PEP 701 syntax at the 3.10 boundary.
- Check the refusal structure separately and use supported targets for harness code.

### What was implemented for Step 6

_(empty: no check has taken place yet.)_.

### New types or classes introduced for Step 6

_(empty: no check has taken place yet.)_.

### Architecture check for Step 6

_(empty: no check has taken place yet.)_.

### Performance check for Step 6

_(empty: no check has taken place yet.)_.

### Unit test coverage check for Step 6

_(empty: no check has taken place yet.)_.

### Feature integrity for Step 6

_(empty: no check has taken place yet.)_.

## Step 7. Acceptance, transient trial and shared-use documentation

### Analysis of Step 7 implementation state

Not started. Step 7 is not implemented because complete acceptance evidence,
the anonymous two-context consumer trial and adoption documentation are pending.

### Goal for Step 7

Close every approved acceptance case with repeatable tests or executable/trial
evidence, then publish accurate adoption and compatibility documentation.

### Step 7 improvement expectations

- Obtain whole-suite full-speed exit 0 and 100% coverage including new modules.
- Verify checkout-record continuity and no own-suite process exemptions.
- Demonstrate both consumer activation contexts without file/persistent changes.
- Apply the shell result in callers with delayed expansion off and on.
- Document Windows/3.12/3.13 evidence and retain Linux/macOS as unvalidated.
- Use Q03=C1's exact compatibility table/boolean, applicability and malformed
  declaration rules in the adoption/validation documentation.
- Document Q04=D1's checkout-local default, explicit new-clone/worktree setup,
  verified absolute override and manifest/version/dependency checks, including
  missing-prerequisite diagnostics and the absence of automatic provisioning.
- Reuse Step 3's private record snapshot and validate with self-hosted groundhog.

### What was implemented for Step 7

_(empty: no check has taken place yet.)_.

### New types or classes introduced for Step 7

_(empty: no check has taken place yet.)_.

### Architecture check for Step 7

_(empty: no check has taken place yet.)_.

### Performance check for Step 7

_(empty: no check has taken place yet.)_.

### Unit test coverage check for Step 7

_(empty: no check has taken place yet.)_.

### Feature integrity for Step 7

_(empty: no check has taken place yet.)_.
