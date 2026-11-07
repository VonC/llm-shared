# Every Suite Gets a Stopwatch

- Type: feature-request
- Test group: whole suite
- Target version: v0.14.0
- Slug: shared_lifecycle_gate

## Draft basis and user need for the shared lifecycle gate

As the maintainer of a project that uses llm-shared, I want to turn on the
per-test lifecycle budget that llm-shared enforces on its own suite, so that the
budget the shared test-writing instruction asks for is checked by every
prepared test run instead of being left to each agent's care.

The [draft](draft.v0.14.0.shared_lifecycle_gate.md) records the need and the
import check of 2026-11-03. This requirement integrates the user decisions
reviewed through round 7. Packaging, import-route design, fixture-exemption
declaration mechanics and validation-step launch mechanics remain design work.

## Current behavior in v0.13.0 for the lifecycle gate

A pytest plugin is a Python module registered with pytest to receive its
execution hooks. Here, the lifecycle gate uses those hooks to measure setup
through teardown; the process audit uses lifecycle and fixture boundaries to
check process starts. Loading the plugins means activating these checks inside
the project's pytest process.

- llm-shared's own suite runs under a lifecycle gate. Each test lifecycle,
  setup through teardown, stays at or under a CPU ceiling
  (`test_lifecycle_limit`, default 0.1 s) and a wall limit
  (`test_lifecycle_wall_limit`, default 1 s). A test proven under its ceiling on
  this checkout passes up to its band top (`test_lifecycle_cpu_band_factor`,
  default 2.5), until `test_lifecycle_cpu_drift_runs` (default 3) consecutive
  measured runs above the ceiling cost its proof. Proofs and accepted
  exceptions live in the untracked per-checkout record
  `a.test-lifecycle-cpu.local.json` in the review artifact home, written once
  per run by the xdist controller, and every run ends with a
  `lifecycle CPU band` summary.
- A limit that is not finite and greater than 0, a band factor that is not
  finite and at least 1, or a drift count that is not a finite whole number
  of at least 1 stops pytest with a usage error naming the key, exit code 4.
- The same module installs a Python audit hook at import and rejects process
  creation during the active test's setup, call and teardown, fixture work
  included. The hook stays installed for the rest of the process; collection
  and worker startup are outside enforcement.
- Both live in llm-shared's `tests/` (`tests/simulation_policy.py` and
  `tests/lifecycle_cpu_record.py`), loaded through `pytest_plugins` in
  `tests/conftest.py`. The gate and process audit cannot be loaded apart.
- The record code imports `tools.review_artifact_configuration` and
  `tools.review_exchange_models` to find the review artifact home: the home
  `.review-artifacts.ini` names, else `.reviews`, used only when it exists and
  its `.gitignore` is exactly `*`.
- The coverage source is `tools` only, so the gate's own code sits outside
  llm-shared's 100% coverage gate.
- A consuming project gets neither plugin. llm-shared is never installed
  (`package = false`); groundhog runs from llm-shared's environment but spawns
  the project's own `pytest`, found on the `PATH` its `senv.bat` prepares.
  Tests run in that project's interpreter and import path. None of the seven
  consuming projects checked on 2026-11-03 has llm-shared on that path, and six
  have a top-level `tools` package, one a `tests` package, so adding
  llm-shared's root would not resolve package collisions.
- Those projects run pytest 9.1, one on Python 3.12 and six on 3.13; one has
  pytest-xdist and six have Hypothesis.
- `instructions/write-fast-python-tests.md` tells every project's agent to keep
  each lifecycle under the two limit keys, but consuming projects fail no
  over-budget lifecycle. groundhog's `speed` verdict judges call time only,
  flagging a call only when it is both a statistical outlier and above the
  project's duration floor.

## Gap to close in the implementation for the shared lifecycle gate

### End-to-end use of the shared pytest safeguards

The feature makes the existing own-suite safeguards available to an ordinary
consuming project with its own source, tests and Python environment:

1. The project explicitly selects timing, process auditing or both in its
   `senv.bat`, which activates the project's own interpreter.
2. Shared preparation computes the selected checks' import paths and pytest
   startup settings. Preparation itself does not import the checks.
3. For an ordinary shell, the preparation launcher transfers only a complete
   successful result to that calling shell, preserving spaces and shell
   metacharacters in values and cleaning up its temporary transfer output.
   A child preparation process cannot directly change its parent shell.
4. The user runs ordinary pytest in that prepared shell. A loader runs inside
   the project's pytest process, checks the selected modules and registers the
   safeguards before tests. Missing selected enforcement stops startup.
5. The selected checks enforce test setup, execution and teardown and produce
   their existing reports and, where applicable, the per-checkout record.
6. Groundhog, the shared test-loop tool, prepares every pytest stage through
   the same contract. It passes the result directly as the child's environment
   and does not need Windows shell serialization.

This activates pytest extensions, without installing llm-shared into the
consumer or switching that consumer's interpreter. Selecting neither adds no
enforcement. The design's [activation boundary](design.v0.14.0.shared_lifecycle_gate.md#import-and-activation-boundary-for-v0140-consumers)
describes the modules and environment values used to meet this behavior.

### Required changes for independently selected safeguards

1. Provide two independently selected shared pytest plugins: the lifecycle
   gate and the process audit. A project declares its opt-in, and its prepared
   shell and every groundhog test stage load the selected plugins. Explicit
   loading with `-p` remains possible wherever the plugin is importable.
2. Each plugin works alone. The gate supplies both limits, CPU band and drift
   guard, per-checkout record and lifecycle summary. The audit tracks the
   active test independently and supplies the process policy and exemption
   summary. Both together retain current assertions, with the explicit
   consuming-project test and fixture permissions specified below.
3. Each plugin has its own import name, never `tools` or `tests`, and loads
   beside a project's packages with those names without hiding either side.
   Plugin files live under llm-shared's `tools/`.
4. At test time the plugins import only the standard library and pytest, with
   no other llm-shared module. The gate carries its artifact-home lookup and
   retains today's rule: the configured home, else `.reviews`, must already
   exist and have `.gitignore` containing exactly `*`. Otherwise every test
   stays strict, nothing is recorded and the summary says so.
5. Both plugins run in the consuming project's interpreter on Python 3.12 and
   later with pytest 9.1 and later, with or without pytest-xdist and without
   requiring Hypothesis. Validate Windows and Python 3.12 and 3.13 for this
   release; document portable-API intent and Linux/macOS as unvalidated.
6. Preserve the lifecycle settings, defaults, precedence, exit code 4 for
   invalid values, per-test CPU-ceiling selection, record name and schema,
   `nodes` and `exceptions` objects, one controller write per run, failure
   message and lifecycle summary lines documented in
   `wiki/reference/test-lifecycle-limits.md`. Existing valid records and
   eligible proofs survive the extraction under the current-ceiling rules.
7. llm-shared becomes the first user. `tests/conftest.py` loads both shared
   plugins instead of the existing modules; no second gate or audit remains
   under `tests/`. Preserve every assertion of the current gate tests and
   bring the plugin code under the 100% coverage gate. llm-shared's own suite
   declares neither test nor fixture process exemptions.
8. Document one supported import route for both prepared-shell pytest and
   every groundhog test stage. It must work in a consuming interpreter outside
   llm-shared's own declared range, currently `>=3.13,<3.14`, without installing
   llm-shared or anything bound by that declaration into the consumer. Design
   selects the route and opt-in declaration while respecting these boundaries.
9. Update the lifecycle documentation and `instructions/write-fast-python-tests.md`
   for shared use, including the opt-in, adoption, exemption and validation
   contracts below.
10. Keep consuming-project names out of the plugins, tests, documentation and
    published validation evidence.

### Activation scope and startup failures for the shared plugins

An opted-in project's plain `pytest` run in its prepared `senv.bat` shell and
every groundhog test stage automatically load the selected plugins. Runs
outside that prepared environment receive no automatic activation; they may
explicitly load an importable plugin. A project selecting neither plugin has
no changed outcome, lifecycle summary, exemption summary or lifecycle record.

Selecting the same plugin through prepared activation and explicit loading
loads it once, without duplicate registration, enforcement or summaries.
If any selected plugin cannot be imported in an opted-in prepared run, stop
before any test runs with usage-error exit code 4. Name both the unavailable
plugin and the opt-in that selected it. Do not continue with missing or partial
selected enforcement.

### Python and platform compatibility for the shared plugins

Python 3.12 support is mandatory because a current consumer requires it;
llm-shared itself may keep its Python 3.13 environment. Loading either plugin
below Python 3.12 stops pytest before tests run with a usage error naming the
plugin and required version. This check also applies to explicit loading
outside the prepared scope. Runs loading neither plugin are unaffected.

The refusal must run before syntax or imports that an older interpreter
cannot handle. Require a repeatable Python 3.10 validity check of the code
reached before that refusal, without promising Python 3.10 runtime support.
Simulating an unsupported version checks the refusal logic; it cannot replace
executable evidence of plugin loading and behavior on supported Python 3.12.

Document Python 3.12 and 3.13 as validated for this release, Windows as
validated, portable-API intent, and Linux/macOS as unvalidated. No validation
on another platform is required for acceptance.

### Lifecycle settings and record compatibility for consuming projects

Opting in applies enforcement immediately, with no report-only mode or
automatic grace period. All four settings remain configurable, with a pytest
`-o` override taking precedence over project pytest configuration, then the
plugin default. No value switches enforcement off.

| Setting | Plugin default | Valid values |
| --- | --- | --- |
| `test_lifecycle_limit` | 0.1 seconds | Finite seconds greater than zero |
| `test_lifecycle_wall_limit` | 1 second | Finite seconds greater than zero |
| `test_lifecycle_cpu_band_factor` | 2.5 | Finite factor at least 1 |
| `test_lifecycle_cpu_drift_runs` | 3 | Finite whole number at least 1 |

A project may adopt with temporarily higher CPU and wall limits and lower
them later. Only a full run without selection or early-stop options can list
every offender. The gate retains current band passes, drift-based proof
withdrawal, failure diagnostics and summary semantics.

Accepted CPU exceptions stay in the ignored per-checkout record with their
existing measured `cpu`, `attempted` and `reason` fields. Do not distribute
numeric exceptions through tracked configuration or add a second source.
Existing valid records remain readable, exceptions keep their meaning and
proofs remain eligible under unchanged current-ceiling rules. Validate
continuity of llm-shared's existing record across the move. Later changes to
configuration keys, defaults or schema document compatibility or migration
behavior; no indefinite schema promise or proof above a lowered ceiling is
required.

CPU measures only the test process, excluding child-process CPU even in
gate-only runs. Wall time covers elapsed setup through teardown, including
process starts and waits within that lifecycle. It does not bound the lifetime
of a child left running afterward. Process permissions grant no CPU or wall
exception. Shared-fixture wall work stays attributed to the carrying test and
can affect a different test's wall verdict after reordering or redistribution.

### Process audit boundaries and permissions for consuming projects

The audit enforces during each test's setup, call and teardown, including
shared-fixture work attributed to that lifecycle. Collection, `conftest.py`
imports during collection and worker startup are outside enforcement, even
though the Python audit hook remains installed for the process lifetime.

A consuming project may declare either permission with its own non-empty
reason:

| Permission | Process starts it covers | Work it does not exempt |
| --- | --- | --- |
| Named test function or parametrized case | The test's call and its function-scoped fixture work | Broader-scoped fixtures |
| Explicitly identified fixture, including shared fixtures | That fixture's own setup, teardown and finalizers | Requested fixtures, consuming tests and later background starts |

A fixture's own permission applies whichever test triggers it. A test's
permission alone never grants permission to a broader-scoped fixture, so
shared-fixture process permission does not depend on test order or xdist
distribution. An unpermitted shared-fixture setup failure is cached for tests
using that fixture; a teardown failure belongs to the lifecycle carrying that
teardown. These rules do not change lifecycle timing attribution.

A process started later by a thread or pool left running by an exempt fixture
does not inherit that fixture permission; it belongs to the lifecycle running
then, under the audit's enforcement window. Requested fixtures have their own
permission boundary. If a function-scoped fixture and its consuming test are
both exempt, credit starts within the fixture to its own permission only. A
function-scoped fixture without its own exemption remains covered by, and
credited to, the exempt test's permission.

With the audit loaded, reject blanket class- or module-level test exemptions,
invalid fixture declarations, and missing or empty reasons before tests run.
Use an identifying usage error with exit code 4, with or without xdist.
Document independent project registration of the test marker so strict-marker
runs work without loading the audit.

Fixture declarations must preserve collection and execution when the audit is
absent, including gate-only runs and environments where llm-shared is not
importable. Consumer tests and conftest files need no llm-shared import for a
fixture declaration, and it introduces no pytest configuration key reported
as unknown without the plugin. This applies under strict markers, strict
configuration, pytest's strict setting and warnings-as-errors. The supported
mechanism remains design work; ordinary pytest marks on fixtures cannot be
assumed to provide it. Without the audit, process permissions have no effect.

### Exemption reporting for the process audit

With the audit loaded, the end-of-run summary reports exercised exempt tests
and fixtures separately, each with its own identity, reason and whether its
permission was used to start a process in its own scope. Flag an exercised
but unused permission without failing the run. Do not list unexercised
fixtures or tests that did not run.

Report each exercised fixture permission once per run, even if instances run
across several modules, classes or workers. Mark it used if any exercised
instance on any worker started a process in that fixture's own work. Credit
each start to the permission covering its scope; a test permission may be
unused when all starts were credited to exempt fixtures.

Under xdist the controller emits one combined summary; otherwise the single
process emits it. Runs without the audit show no exemption summary. Audit-only
runs may show this summary but have no lifecycle limits, lifecycle CPU band
summary or lifecycle record. llm-shared's own suite declares and reports no
test or fixture exemptions.

### Validation evidence for the shared lifecycle gate

Require repeatable in-process isolation tests in llm-shared's suite and a
temporary trial in one real consuming environment. Isolation evidence covers
the import route alongside a project's own `tools` and `tests` packages,
prepared-shell and groundhog activation, no automatic activation outside
that scope, single loading when selected twice, and startup refusal under K1.
These checks remain under the `tools` coverage gate and may not start processes
from llm-shared's process-free suite.

The real-environment trial covers both a prepared-shell plain pytest run and
a groundhog test stage. It changes no consuming-project files, leaves neither
plugin persistently selected, and is recorded without naming the project.
Suitable Python 3.12 evidence and this trial may share a run; both activation
contexts remain required.

In llm-shared's regular whole-suite validation, run static checks targeting
Python 3.12 for the plugin modules and executable plugin tests under Python
3.12, alongside Python 3.13 validation. The Python 3.12 tests use a harness
independent of llm-shared's Python 3.13-only helpers and run as a separate step
outside its process-free suite. Every machine running llm-shared's own
whole-suite validation must provide Python 3.12; otherwise validation fails
rather than skipping that step. The launch mechanism and interpreter provision
remain design work. This adds no Python 3.12 requirement to a consuming
project's validation, including groundhog runs of its own suite.

### Documentation deliverables for the shared plugins

Update the lifecycle reference and how-to pages, provide a consuming-project
opt-in how-to for each plugin, and update `instructions/write-fast-python-tests.md`
to state where the budget is enforced and how a project opts in. Cover the
prepared-environment boundary, supported import route, startup failures,
independent marker registration, test and fixture permission boundaries,
reporting, and timing that remains charged to shared-fixture lifecycles.

The opt-in how-to explains adoption with temporarily higher CPU and wall
limits, gradual reduction, and why only a full run without selection or
early-stop options can list every offender. Document validated interpreter and
platform versions and unvalidated platforms as stated above. Keep consumer
identities and private paths out of all public evidence and documentation.

## File-based IO cost clarification for the shared lifecycle requirement

Activation must use the declared environment and named bootstrap/policy inputs,
without scanning project documentation. Keep per-test measurement and process
authorization in memory. Preserve one controller record write per run and the
strict, record-free outcome when no valid artifact home already exists. These
clarifications preserve the accepted contracts; they add no new timing limit.

## Acceptance criteria for the shared lifecycle gate

- A project selecting neither plugin has unchanged outcomes and summaries,
  with no lifecycle record or exemption summary introduced.
- Opted-in prepared-shell pytest and every groundhog test stage load exactly
  the selected plugins. Outside runs receive no automatic activation.
  Explicit loading remains possible, and combined prepared and explicit
  selection causes one registration and one set of summaries.
- A selected-plugin import failure in a prepared run stops before tests with
  exit code 4 and names both the plugin and selecting opt-in.
- With the gate only, an over-ceiling lifecycle fails with today's message,
  both clocks and the ceiling basis. A proven test within its band top passes
  as a band pass; drift and proof withdrawal stay unchanged. Starting a
  process alone does not fail a gate-only run.
- With the audit only, unpermitted process creation during setup, call or
  teardown fails and names the carrying test and process event. Collection
  and worker startup stay outside enforcement. No lifecycle limits, lifecycle
  CPU band summary or lifecycle record appear; exemption reporting remains.
- Test and fixture permissions obey their separate boundaries with required
  reasons. Shared-fixture process permission is stable under test order and
  xdist distribution. Timing stays enforced, including shared-fixture starts
  and waits, while child CPU and detached-child lifetime stay outside the
  stated measurements.
- Invalid permission declarations fail before tests with an identifying
  usage error, exit code 4, with or without xdist. Valid declarations remain
  harmless without the audit under all stated strict settings, with no
  required consumer import of llm-shared or unknown ini key.
- Audit summaries identify exercised exempt tests and fixtures, own-scope use
  and reasons, flag unused permissions without failure, exclude unexercised
  work, aggregate fixture permissions once per run and appear once on the
  controller under xdist. Without the audit, no exemption summary appears.
- With the gate and no existing valid ignored artifact home, every test is
  strict, nothing is recorded and the lifecycle summary says so. With a valid
  home, the controller writes once per run, or the single process without
  xdist does so. Existing valid records, exception meanings and eligible
  proofs, including llm-shared's current record, survive the extraction.
- Each setting retains its specified default, valid range and
  `-o`/project/default precedence. Invalid values stop pytest with exit code 4
  and name the key; there is no report-only or grace mode.
- Both plugins load beside a project's own top-level `tools` and `tests`
  packages, which remain importable. At test time they import no llm-shared
  module other than the plugin itself and require only stdlib and pytest.
  The route works on Python 3.12 without installing llm-shared into it.
- Executable tests demonstrate loading and behavior on real Python 3.12 and
  3.13 on Windows. llm-shared's regular whole-suite validation includes the
  repeated static and executable Python 3.12 checks described above; missing
  Python 3.12 fails that validation. Static checks or a simulated version alone
  do not meet supported-runtime evidence requirements.
- Loading either plugin below Python 3.12, including explicit outside-scope
  loading, produces the identifying startup usage error. Simulated-version
  tests cover refusal, and a repeatable Python 3.10 validity check covers code
  before refusal, without adding support for that interpreter.
- Repeatable isolation evidence and a temporary real-consuming-environment
  trial cover both activation contexts; trial evidence names no consumer,
  changes no consumer files and leaves no persistent activation.
- With both plugins, llm-shared's current gate and audit tests pass unchanged
  in what they assert. Its whole-suite `ghog day --full=speed` passes with
  100% coverage including the plugin modules and with neither test nor fixture
  exemptions declared or reported.
- Documentation covers the specified adoption and permission contracts and
  states Python 3.12/3.13 and Windows validation, portable-API intent and
  Linux/macOS as unvalidated in this release.

## Out of scope for the shared lifecycle gate

- Persistent activation in a consuming project or conversion of its tests;
  the temporary acceptance trial is limited to the evidence contract above.
- Changes to the groundhog `speed` verdict or its duration floor.
- Process-starting tests or fixture exemptions in llm-shared's own suite.
- Changing llm-shared's own Python requirement, indefinite record-schema
  support, plugin version pinning per consumer, or Linux/macOS acceptance runs.
- llm-shared's other suite plugins (`tests.memory_filesystem`,
  `tests.scenario_cli`, `tests.scenario_generation`,
  `tests.testmon_monitoring`) and the rest of `tests/conftest.py`, which stay
  llm-shared's own.

## Code references for the shared lifecycle gate

- `tests/simulation_policy.py`: process audit hook, lifecycle CPU and wall
  measurement, ini key declarations and failure message.
- `tests/lifecycle_cpu_record.py`: band policy, record parsing and writing,
  artifact-home lookup, `LifecycleGate`, controller-side `BandCollector` and
  end-of-run summary.
- `tests/conftest.py`: loads both modules through `pytest_plugins` with the
  other suite plugins.
- `tests/unit/tools/test_lifecycle_policy.py` and
  `tests/unit/tools/test_lifecycle_cpu_band.py`: the gate's current tests.
- `pyproject.toml`: project `test_lifecycle_*` values, `addopts` and coverage
  source `tools`.
- `tools/review_artifact_configuration.py` and `tools/review_exchange_models.py`:
  the artifact-home lookup the record uses today.
- `tools/groundhog/commands.py` and `tools/groundhog/runner.py`: find the
  project's `pytest` on `PATH` and spawn it with spawn-only environment
  overrides.
- `senv.bat`: puts llm-shared's `bin` on `PYTHONPATH`, not its root.
- `wiki/reference/test-lifecycle-limits.md`,
  `wiki/how-to/set-test-lifecycle-limits.md`,
  `wiki/explanation/why-fast-tests-keep-the-work-they-assert.md` and
  `instructions/write-fast-python-tests.md`: the gate's documentation.

## Requirement clarifications

The following decisions were confirmed by the user on 2026-11-04 and
2026-11-05 and independently reviewed through round 7. Q02's Python 3.12
amendment supersedes the earlier B3 choice; Q15 uses that revised minimum.
The pre-consolidation commit retains all question blocks and review history.

| Question | Decision and reason | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | A2: automatic activation in prepared-shell pytest and all groundhog test stages keeps the documented workflows covered without requiring llm-shared everywhere. | [Activation scope](#activation-scope-and-startup-failures-for-the-shared-plugins) | A1 everywhere; A3 warning with unenforced runs. |
| Q02 | Mandatory Python 3.12 and later support, with real 3.12 loading and behavior evidence independent of 3.13-only helpers, serves the current consumer constraint. llm-shared may remain on 3.13. | [Compatibility](#python-and-platform-compatibility-for-the-shared-plugins), [validation](#validation-evidence-for-the-shared-lifecycle-gate) | Static-only evidence; superseded B3 dropping 3.12 support. |
| Q03 | C3: validate Windows, state portable-API intent and mark Linux/macOS unvalidated so the promise matches the evidence. | [Compatibility](#python-and-platform-compatibility-for-the-shared-plugins) | C1 excluding other platforms; C2 requiring validation on all three. |
| Q04 | D1: enforce during setup, call and teardown, with attributed shared-fixture work, preserving the existing window and timing alignment. | [Audit boundaries](#process-audit-boundaries-and-permissions-for-consuming-projects) | D2 collection enforcement; D3 a configurable extra window. |
| Q05 | E2: reasoned per-test permissions permit incremental audit adoption and stay visible; timing remains enforced and llm-shared's own suite has no exemptions. | [Audit boundaries](#process-audit-boundaries-and-permissions-for-consuming-projects), [reporting](#exemption-reporting-for-the-process-audit) | E1 no consumer exemptions; E3 broad path exemptions. |
| Q06 | F1: accepted CPU exceptions remain measured, ignored and local to each checkout, retaining their existing fields and meaning. | [Settings and records](#lifecycle-settings-and-record-compatibility-for-consuming-projects) | F2 tracked numeric exceptions; F3 tracked and local sources. |
| Q07 | G1: immediate enforcement with all four settings configurable under `-o`/project/default precedence avoids an off switch or hidden grace state. | [Settings and records](#lifecycle-settings-and-record-compatibility-for-consuming-projects) | G2 report-only mode; G3 automatic grace. |
| Q08 | H3: repeatable isolation tests plus a temporary real-environment trial provide both regression coverage and practical import/activation evidence without consumer-file changes or persistent activation. | [Validation](#validation-evidence-for-the-shared-lifecycle-gate) | H1 isolation only; H2 trial only. |
| Q09 | I1: preserve valid records, exception meaning and eligible proofs for this extraction, and document compatibility or migration for later contract changes. | [Settings and records](#lifecycle-settings-and-record-compatibility-for-consuming-projects) | I2 no compatibility promise; I3 per-project plugin pinning. |
| Q10 | J1: keep defaults of 0.1 s CPU, 1 s wall, factor 2.5 and drift count 3, matching the existing instruction and allowing explicit overrides. | [Settings and records](#lifecycle-settings-and-record-compatibility-for-consuming-projects) | J2 looser defaults; J3 mandatory explicit values without defaults. |
| Q11 | K1, with separately confirmed exit code 4: stop before tests on selected-plugin import failure, naming the plugin and opt-in, so selected enforcement cannot disappear. | [Startup failures](#activation-scope-and-startup-failures-for-the-shared-plugins) | K2 continue without selected policies; K3 partial enforcement. |
| Q12 | L3: a test permission covers its call and function fixtures; separate reasoned fixture permission covers only its own work, making shared-fixture process permission independent of the triggering test. Timing is unchanged. | [Audit boundaries](#process-audit-boundaries-and-permissions-for-consuming-projects) | L1 no shared-fixture permission; L2 permission inherited from the carrying test. |
| Q13 | M1 adapted to L3: allow named tests/cases and identified fixtures, reject invalid declarations before tests with exit code 4, and preserve strict runs without audit. This prevents blanket or accidental permission. | [Audit boundaries](#process-audit-boundaries-and-permissions-for-consuming-projects) | M2 blanket class/module test marks; M3 warning-only invalid declarations. |
| Q14 | N2 adapted to L3: report exercised test and fixture permissions with identity, reason and own-scope use, flagging unused permissions without failure and aggregating once under xdist. | [Reporting](#exemption-reporting-for-the-process-audit) | N1 omit usage; N3 fail unused permissions. |
| Q15 | O2 amended to 3.12: refuse older interpreters before incompatible code with an identifying startup usage error; accept and runtime-validate 3.12. Check pre-refusal validity at 3.10 without promising its support. | [Compatibility](#python-and-platform-compatibility-for-the-shared-plugins), [acceptance](#acceptance-criteria-for-the-shared-lifecycle-gate) | O1 documented floor without enforcement; the superseded 3.13 refusal threshold. |
| Q16 | P3: recurring static 3.12 checks and executable 3.12 plugin tests in llm-shared's own whole-suite validation keep the compatibility promise checked after changes. Missing 3.12 fails; consumer validation gains no interpreter requirement. | [Validation](#validation-evidence-for-the-shared-lifecycle-gate) | P1 one-off runtime evidence; P2 recurring static checks without recurring runtime evidence. |
