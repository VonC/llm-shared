# v0.14.0 shared lifecycle gate implementation tracking and validation

No, it is not implemented

Step 1 of the seven-step
[implementation plan](plan.v0.14.0.shared_lifecycle_gate.md) was checked on
2026-11-08. Steps 2-7 remain not started; their goals describe later checks.

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

Not started. Step 2 is not implemented because the independent audit and its
declaration/ownership adapter have not been created.

### Goal for Step 2

Implement the approved process window, declarations, guarded dispatcher and
thread/token-bound fixture ownership without gate dependencies.

### Step 2 improvement expectations

- Preserve event rejection outside permissions and safe nested-session detach.
- Validate actual decorated fixture identities and original marker levels.
- Unwind ownership and restore only owned wrappers after the last detach.
- Declare the module-level literal contract after its Python-version guard.

### What was implemented for Step 2

_(empty: no check has taken place yet.)_.

### New types or classes introduced for Step 2

_(empty: no check has taken place yet.)_.

### Architecture check for Step 2

_(empty: no check has taken place yet.)_.

### Performance check for Step 2

_(empty: no check has taken place yet.)_.

### Unit test coverage check for Step 2

_(empty: no check has taken place yet.)_.

### Feature integrity for Step 2

_(empty: no check has taken place yet.)_.

## Step 3. Worker barrier, summaries and own-suite migration

### Analysis of Step 3 implementation state

Not started. Step 3 is not implemented because distributed declaration
validation/reporting and replacement of the suite-local policy are pending.

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

_(empty: no check has taken place yet.)_.

### New types or classes introduced for Step 3

_(empty: no check has taken place yet.)_.

### Architecture check for Step 3

_(empty: no check has taken place yet.)_.

### Performance check for Step 3

_(empty: no check has taken place yet.)_.

### Unit test coverage check for Step 3

_(empty: no check has taken place yet.)_.

### Feature integrity for Step 3

_(empty: no check has taken place yet.)_.

## Step 4. Immutable preparation and canonical early loading

### Analysis of Step 4 implementation state

Not started. Step 4 is not implemented because the loader, cache/environment
builder, Windows transport module and shell preparation launcher have not
been created.

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

_(empty: no check has taken place yet.)_.

### New types or classes introduced for Step 4

_(empty: no check has taken place yet.)_.

### Architecture check for Step 4

_(empty: no check has taken place yet.)_.

### Performance check for Step 4

_(empty: no check has taken place yet.)_.

### Unit test coverage check for Step 4

_(empty: no check has taken place yet.)_.

### Feature integrity for Step 4

_(empty: no check has taken place yet.)_.

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
