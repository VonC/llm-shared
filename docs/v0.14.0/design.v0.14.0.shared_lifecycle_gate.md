# Design v0.14.0 -- Shared lifecycle gate

Reference feature request:
[Every Suite Gets a Stopwatch](feature-request.v0.14.0.shared_lifecycle_gate.md).

## Context for v0.14.0 shared lifecycle enforcement

The lifecycle budget and process audit currently protect llm-shared's tests
through one suite-local plugin. Consumers run their own interpreters and have
colliding top-level package names, so exposing llm-shared's repository root or
installing its Python 3.13 project is unsuitable. This design separates the
policies and supplies prepared-environment activation without either dependency.

The requirement's Q01-Q16 decisions remain authoritative. Q01 to Q09 below
record the user's design decisions of 2026-11-06, and Q10 the decision of
2026-11-07.
The other interfaces below
are design choices within those decisions and the requirement.

## Scope for the v0.14.0 shared plugins

The design delivers independently selectable lifecycle and process policies,
one import route for prepared pytest and all groundhog test stages, compatible
checkout records, and recurring executable Python 3.12 verification.

Both policies support Python 3.12 and later and pytest 9.1 and later. Windows,
Python 3.12 and Python 3.13 are the release validation targets. Standard-library
APIs express portable intent; Linux and macOS remain unvalidated in this release.
Future supported versions are not described as already validated.

Persistent adoption or test conversion in consumers, changes to groundhog's
speed verdict, additional shared suite plugins and changes to llm-shared's own
Python requirement remain outside this effort. llm-shared uses both policies
without test or fixture process permissions.

## Confirmed technical facts for the v0.14.0 extraction

These facts were checked against the current source before drafting.

| Current source | Confirmed behavior and design consequence |
| --- | --- |
| `tests/simulation_policy.py` | Installs an audit hook at import, tracks active tests through `pytest_runtest_protocol`, and measures CPU from before setup through teardown. Separate plugins must each own their necessary lifecycle state. |
| `tests/lifecycle_cpu_record.py` | Implements the band, proof withdrawal, record schema 1, exception validation, node-ID normalization and controller collector. Its artifact lookup imports two `tools` modules, which cannot remain runtime dependencies. |
| `tools/review_artifact_configuration.py` | Reads a strict optional `[review-artifacts] home` declaration, checks repository containment and resolves the default `.reviews`. The current lifecycle caller substitutes a filesystem ignore check for Git subprocess use. |
| `tests/conftest.py` | Registers `tests.simulation_policy` alongside unrelated suite plugins. Those unrelated plugins retain their current ownership. |
| `pyproject.toml` | Declares Python `>=3.13,<3.14`, coverage source `tools`, fail-under 100, and Python 3.13 type checking. The consumer runtime therefore needs a separate compatibility boundary. |
| `senv.bat` | Adds llm-shared's `bin` to `PYTHONPATH` and creates pytest doskey shortcuts. Neither arrangement makes plain consumer pytest import the existing gate. |
| `tools/groundhog/commands.py` | Resolves the project's `pytest` through `PATH` and supplies spawn-only environment overrides through its runner. Activation belongs in that child environment, without switching interpreters. |
| `check.bat` | Aggregates static checks before the suite. It provides a project-local place to require the separate compatibility validation without adding it to consumer groundhog runs. |

## Current and target flows for prepared test runs

Today, llm-shared's conftest loads the combined suite policy, while consumer
pytest runs have neither policy. Groundhog executes the consumer's pytest;
its own interpreter does not determine the test interpreter.

The target flow is:

```text
project senv declares selection and calls shared preparation
    -> independent loader cache and dedicated policy directory on PYTHONPATH
    -> early pytest loader in PYTEST_ADDOPTS
    -> selected plugins preflighted and registered once
    -> project pytest collects and runs in its own interpreter

groundhog test stage
    -> same selection and preparation contract in child environment
    -> same project pytest and plugin identities
```

The loader carries no policy. Each selected policy supplies its own startup
validation, runtime hooks and reporting. Unselected policies are not imported.

## Import and activation boundary for v0.14.0 consumers

### Standalone modules and canonical import identities

Use a dedicated directory under `tools/pytest_plugins/`, exposing only these
top-level module names to the consumer:

| Module | Responsibility |
| --- | --- |
| `llm_shared_lifecycle_gate` | Lifecycle clocks, settings, record model, artifact lookup and CPU-band reporting. |
| `llm_shared_process_audit` | Process events, active lifecycle, permissions, declaration validation and exemption reporting. |
| `llm_shared_pytest_loader` | Prepared-run selection validation, import preflight and idempotent policy registration; preparation materializes this bootstrap independently of the shared checkout. |

Add only the dedicated policy directory and prepared bootstrap directory to
`PYTHONPATH`; do not add llm-shared's repository root or `tools` directory.
The consumer's `tools` and `tests` packages remain
importable. No distribution installation or entry-point auto-discovery is
required. Each policy module imports only stdlib and pytest; neither imports
the other policy, loader, record helper or any other llm-shared module.
The loader imports selected policies by their canonical names.

Keep each module within the repository's file-size policy. Internal classes
separate record handling, measurement and reporting without introducing a
consumer dependency on another llm-shared module.

### Opt-in and prepared-environment contract

Q02 confirmed `LLM_SHARED_PYTEST_PLUGINS`, containing a comma-separated selection of
`lifecycle` and `process`. Empty means neither. Unknown names are configuration
errors; repeated names normalize to one selection. A project's `senv.bat`
declares its selection and invokes a shared preparation launcher after choosing
its own interpreter. No pytest alias is required for activation.

Preparation captures the project root as `LLM_SHARED_PYTEST_ROOT`, exposes the
dedicated directory and the independent bootstrap, and prepends
`-p llm_shared_pytest_loader` to
`PYTEST_ADDOPTS`, preserving existing options and avoiding repeated entries.
The root binds selection to that project. Only preparation, in `senv` or in
groundhog's child environment, refreshes a binding. At pytest startup, before
registration, the bootstrap rejects a run whose pytest `rootpath` lies outside
`LLM_SHARED_PYTEST_ROOT`, with exit code 4 naming the bound root and the
selection; a rootdir inside the project stays accepted. A nested pytest process
for another directory, such as a generated temporary project, clears the
preparation variables first.
Re-preparation recomputes owned entries, so deselection removes activation
without deleting unrelated path entries or pytest options.

Groundhog uses the same normalization and environment-building contract for
every pytest stage, including affected, focused, timings and full runs. It
passes the prepared selection to the project's pytest and its xdist workers.
Its parent environment is not mutated by child preparation. Project switching
cannot silently reuse another project's selection.

Carry the policy directory as `LLM_SHARED_PYTEST_POLICY_DIR` alongside the
project root and selection in the prepared environment. Cached bootstrap code
contains none of these bindings. Separate shells can therefore select different
shared checkouts for the same consumer without changing each other's loader.

Outside the prepared environment, nothing activates automatically. An operator
can expose the dedicated directory and use `-p llm_shared_lifecycle_gate` or
`-p llm_shared_process_audit`. Such explicit loading needs no selection variable.
Selecting neither leaves outcomes, records and both policy summaries unchanged.

### Early failure and duplicate loading

Preparation atomically materializes a self-contained copy of the loader in a
user-local cache outside both the consumer and shared checkout. Each entry is
content-addressed by the SHA-256 hash of the bootstrap source and contains only
the bootstrap module. Publish a new entry atomically once, verify any existing
entry against that hash, and never replace an entry used by a prepared shell.
An existing entry that fails verification stops preparation with a diagnostic
naming the entry and the documented cleanup. Preparation never rewrites it and
publishes no environment.
Changed source gets a new directory. Cleanup is an explicit, documented
operation, never an automatic step of preparation, because no record shows
which entries prepared shells still use. Removing an entry a shell still uses
leaves that shell on the policy directory's source loader, as described below.
This
bootstrap contains no policy and imports no shared helper. Its separate import
directory precedes the shared policy directory, whose loader source must not
shadow it. Preparation checks the bootstrap, the policy directory and every
selected module before exposing the environment. Groundhog repeats these
checks before spawning each selected stage. No package installation is needed.

The prepared bootstrap survives moving or removing the shared checkout. It
checks the bound shared policy path and preflights selected modules there,
without accepting an installed or cached policy as a fallback. A stale prepared
shell therefore still reports the selected policy, selection and exit code 4
if that checkout disappears, including `python -m pytest` and script entry
points. Re-preparation selects the matching immutable entry; a failure does not
publish a partly prepared environment. The cached bootstrap survives removal
of the shared checkout; the policy directory's source loader still serves if
only the cache is removed. Removing both copies removes every executable
bootstrap and leaves pytest's own import error before tests. Q08 confirmed the
user-local cache placement.
Preparation never creates the review artifact home for this cache; a missing
or invalid home still leaves the gate strict and record-free. Cache storage
does not change consumer project files, including during the transient trial.

Define one bootstrap-to-policy contract version, exposed by each standalone
policy and the loader. Preflight checks every selected policy's version before
registration. A stale bootstrap against a changed contract stops before tests
with exit code 4, naming the selection and asking to prepare the shell again.
Missing version declarations are mismatches. Live policy edits remain visible;
no cached policy or contract-mismatched registration substitutes for them.

pytest processes tracked `addopts` before `PYTEST_ADDOPTS`, then command-line
options. The bootstrap is first only among preparation's injected `-p` entries.
The opt-in guide must keep policy `-p` entries out of tracked `addopts`, where
they would import before the bootstrap. During its early import the bootstrap
validates selection and preflights every selected module before later
command-line `-p` options or collection can bypass a selected-policy error.
Convert selected import failures to `pytest.UsageError` naming the canonical
plugin, `LLM_SHARED_PYTEST_PLUGINS` and the project selection. Exit code is 4.
No tests run after partial preflight success.

Register the preflighted modules through pytest's canonical plugin-name
mechanism before initial conftest loading. An already registered canonical
module is reused; explicit loading before or after registration cannot install
a second gate, audit hook dispatcher or collector. Blocking a selected policy
with `-p no:...` is an identifying usage error rather than silent deselection.

The loader and each policy have a Python 3.10-parseable entry path. Check
`sys.version_info` before executing newer APIs or evaluating incompatible
definitions; below 3.12 raise a usage error identifying the module and minimum.
Use Python 3.10-compatible syntax throughout these standalone files to keep
that boundary inspectable. Before refusal, execute only `sys` and `pytest`
imports, the version comparison and the identifying usage-error raise. This
keeps the pre-refusal API boundary inspectable at 3.10 despite Pyright's 3.12
target for supported execution.
Repeatable parsing checks cover the entire entry
path; simulated-version tests exercise refusal. Neither replaces real 3.12
execution. Explicit loading receives the same version guard.

## Lifecycle policy and record continuity in v0.14.0

### Measurement, limits and proof states

The gate starts parent-process CPU measurement before setup and stops after
teardown, retaining the existing report-hook CPU inclusion. Wall time remains
the sum of setup, call and teardown report durations. Shared fixture work is
charged to the lifecycle that performs it. Child CPU and detached-child lifetime
are not measured; starts and waits performed inside a lifecycle remain charged.

Retain the four ini keys and `-o` / project / default precedence:

| Setting | Default | Accepted range |
| --- | --- | --- |
| `test_lifecycle_limit` | 0.1 seconds | Finite and greater than zero. |
| `test_lifecycle_wall_limit` | 1 second | Finite and greater than zero. |
| `test_lifecycle_cpu_band_factor` | 2.5 | Finite and at least 1. |
| `test_lifecycle_cpu_drift_runs` | 3 | Finite whole number at least 1. |

Invalid values name the key and stop startup with exit code 4. Selection applies
enforcement immediately; there is no off value, report-only mode or grace state.

For tracked lifecycle keys to remain usable without the gate, the project's
root `conftest.py` carries a plain-pytest `pytest_addoption` snippet registering
the four keys with `parser.addini`, as Q09 confirmed. This imports no shared
code. pytest keeps the last `addini` registration of a
key, and a root conftest registers after a `-p` plugin, so an unguarded snippet
replaces the gate's type and default. Q10 confirmed the guard: the snippet
takes `pytest_addoption(parser, pluginmanager)` and registers the keys only
when `pluginmanager.has_plugin("llm_shared_lifecycle_gate")` is false. The
gate's own registration then supplies the defaults, and `config.getini` keeps
the `-o`/project/default precedence without deprecated or private pytest
configuration access.

The current per-test ceiling, accepted measured CPU exceptions, eligible proof,
band-top pass and consecutive-drift withdrawal rules remain unchanged. Only a
passing call with no other phase failure contributes a measured observation.
Preserve report properties, failure text, both clocks, ceiling basis and the
documented `lifecycle CPU band` summary. Existing failures are not overwritten
by a second budget failure.

### Artifact-home lookup and persistence

The standalone gate owns a stdlib-only copy of the current lookup contract:
strict `.review-artifacts.ini`, one `[review-artifacts]` section and `home`
property, default `.reviews`, repository-relative spelling and resolved physical
containment. It starts no Git process. A usable home must already exist and
contain `.gitignore` with exactly the currently accepted catch-all bytes.
Invalid, unavailable or unsafe homes retain strict limits, write nothing and
produce the existing no-home summary. The gate never prepares the home.

Retain `a.test-lifecycle-cpu.local.json`, schema 1, node-key normalization and
the `nodes` / `exceptions` objects. Exceptions retain measured `cpu`,
`attempted` and `reason`, with no tracked numeric exception source. Proofs
remain eligible under unchanged current ceilings; lowering a ceiling can
invalidate a proof as it does today. Extraction needs no record migration.

Workers read the same initial policy and attach lifecycle observations to
reports. The controller merges observations and writes once per run; a serial
run performs that responsibility locally. Preserve accepted exception content
and existing valid records, including llm-shared's checkout record. Subsequent
contract changes must document compatibility or migration separately.

## Process permission boundaries for v0.14.0

### Independent audit state and declaration interfaces

The audit independently tracks setup, call and teardown. Its process-lifetime
audit hook observes the existing process-event set and rejects an unpermitted
start with the carrying test and event. Collection, conftest imports during
collection and worker startup stay outside enforcement. The hook dispatches
only to an active session, so embedded pytest sessions cannot retain stale
test identities or permissions after unconfiguration.

Install one audit dispatcher per process, using a process-wide guard that
survives module reload and import under another name. Module-local flags alone
are insufficient. Each session attaches and detaches its own active state.

Use a `process_allowed(reason="...")` pytest marker for named test
functions and individual parametrized cases. Consumers register the marker
independently in normal pytest configuration, including environments without
the audit. Class/module marks and empty or malformed reasons are invalid.

Q03 confirmed a plain module dictionary named `LLM_SHARED_PROCESS_FIXTURES` in a
conftest or collected test module. Keys are the actual decorated fixture objects;
values are non-empty reason strings. For example:

```python
@pytest.fixture(scope="session")
def service():
    ...

LLM_SHARED_PROCESS_FIXTURES = {service: "Exercises the real service protocol"}
```

This is ordinary Python data, requiring no llm-shared import, fixture mark or
pytest ini extension. It remains harmless with no audit, including gate-only
runs, strict configuration, strict markers, pytest strict mode and warnings as
errors. Exporting an imported fixture object in a declaration is allowed when
it resolves to an actual registered fixture definition. Invalid objects,
ambiguous resolution and conflicting reasons are identifying usage errors.

After collection and before any test setup, validate every declaration in
loaded conftests and collected test modules, including unused fixture entries.
Validate test markers and their original declaration level, not only the
effective inherited marker list. Serial and xdist runs both use exit code 4
for invalid declarations, without allowing tests to start on another worker.
Use xdist's existing `collection_is_completed` barrier, which counts the workers
that have announced their collection. Each worker validates in a
`pytest_collection_finish` implementation ordered before xdist's announcement.
After any declaration error, it withholds the announcement, leaves identifying
evidence for the controller and ends with a usage error, so the barrier never
completes. Validation never fails after the announcement: pytest still runs
`pytest_collection_finish` when `pytest_collection_modifyitems` raises, and xdist
then schedules the announced collection on the other workers. The controller
treats a worker that finishes before announcing its collection as a stop, never
as a wait. When that worker's evidence names a declaration error, the controller
stops the remaining workers and exits 4 with the identifying usage error. An
announced collection is the worker's validation evidence. Serial runs validate
at the same point.

### Fixture ownership and finalization

Use a narrow pytest compatibility adapter around fixture execution and
finalization to identify the active fixture definition, scope and own work.
Public setup hooks alone do not delimit every finalizer or identify all loaded
unused fixture declarations. The adapter may inspect pytest's fixture registry;
it must validate the expected capabilities at startup and stop with an
identifying usage error if a future pytest changes them incompatibly.

Nested requested fixtures replace the outer fixture's ownership while their
own setup or finalization runs, then restore it even after errors. Cached
fixture access grants no new permission. Finalization re-enters the finalized
fixture's own ownership, including yield teardown and registered finalizers;
dependency finalization switches to that dependency's owner.

Authorization follows the most specific active work:

| Active work | Applicable permission and usage credit |
| --- | --- |
| Explicitly exempt fixture's own work | That fixture only, irrespective of the consuming test. |
| Unexempt function fixture | The carrying test's permission, if any. |
| Unexempt broader-scoped fixture | None, even when the carrying test is exempt. |
| Test call | The test/case permission, if any. |
| Later background activity | Current lifecycle rules, without inheriting an expired fixture permission. |

Fixture ownership is bound to the thread executing that fixture operation and
its live execution token. A copied context or background thread cannot retain
the fixture's permission. A process start on any other thread is not that
fixture's own work, even while its setup or teardown is running, and is judged
under the active lifecycle. Helpers and pools that start processes on another
thread receive no fixture permission. All ownership stacks unwind on failure.
Install the fixture adapter once per process under the same process-wide guard
as the audit dispatcher. Each session attaches and detaches its own ownership
state. Restore pytest's original fixture callables only when the last attached
session detaches, and only while they still hold the adapter's wrappers.
The existing shared-fixture setup caching and teardown attribution remain
pytest's behavior. Neither kind of permission changes timing enforcement.

### Exercised permissions and xdist aggregation

Track test permissions by normalized node ID. Track fixture permissions by a
stable definition identity containing repository-relative source, qualified
name, declared fixture name, registration scope/base and fixture scope. The
same definition's parameter values and worker instances share one permission
identity; overridden definitions remain distinct.

Only an executed test or entered fixture instance is exercised. Each record
contains identity, reason and a used boolean. A permitted process event credits
exactly one applicable permission. Merge worker records by identity with boolean
OR for use and verify reason consistency. A test can therefore be unused when
all starts were credited to its exempt fixtures.

The controller emits one combined summary with separate test and fixture
groups; serial execution emits it locally. Flag exercised unused permissions
without failing, omit unexercised declarations, and list each fixture definition
once per run. Audit-only runs have this report and no gate settings, CPU-band
report or lifecycle record. No audit means no exemption report. llm-shared's
own suite declares and reports no permissions.

## Compatibility validation boundary for v0.14.0

### Process-free regressions and executable compatibility

Keep the existing gate assertions and add repeatable in-process isolation
coverage for both standalone policies, activation preparation and fixture
ownership. Simulated imports, environment construction and observed runner
dependencies cover integration branches without starting processes inside
llm-shared's suite. All shipped plugin and activation code remains under the
`tools` 100% coverage gate; the extraction adds no coverage omissions.

llm-shared's own prepared shell and groundhog child environments select neither
policy automatically. Its `tests/conftest.py` loads both canonical modules only
after pytest-cov has started coverage. Its tests import them only by canonical
names, never as `tools.pytest_plugins` modules. Early `-p` loading in its own
suite would execute module-level code before coverage and is therefore excluded.
This own-suite path still enables both policies without process permissions.

A separate compatibility harness runs outside that suite. It depends only on
stdlib, pytest and optional pytest-xdist, never llm-shared's Python 3.13 helpers
or root conftest. It exercises actual plugin loading, settings, budget failures,
process rejection and allowed starts, declarations, fixture teardown boundaries,
summaries and selected activation on Python 3.12. It also checks xdist behavior
with the optional dependency present and plugin independence without it.
Generated test projects and records belong to temporary directories.

Q06 confirmed a dedicated Python 3.12 virtual environment provisioned through a
standalone compatibility dependency manifest, outside llm-shared's project
dependency resolution. A machine-local absolute interpreter override may select
an equivalent prepared environment. Validate the executable's real version and
required dependencies; do not select whatever `python` happens to name.
Missing or unsuitable 3.12 is a validation failure, never a skip or automatic
consumer environment modification.

Set Ruff's main `per-file-target-version` to `py310` for
`tools/pytest_plugins/**`, preventing routine `ruff check --fix` from applying
the project's inferred Python 3.13 target there. Set a Pyright execution
environment for that directory to Python 3.12. `check.bat` runs static Python
3.12 checks and the Python 3.10 entry-path parse check, without the executable
harness.

Q07 confirmed an own-project whole-suite preflight running the executable harness
for every day walk and every direct `ghog full`, outside the audited test
window. Its applicability comes from an explicit declaration tracked in
llm-shared and read from the project under test, so every clone and linked
worktree of llm-shared runs it. Never derive it from a consumer name, an untracked
machine-local file or plugin selection. Each invocation obtains
fresh executable evidence; no harness-result reuse contract is needed.
The normal Python 3.13 suite and full-speed validation remain
required. Consumer groundhog runs gain no Python 3.12 prerequisite from this
harness. Plain pytest remains a suite run, without claiming completion of the
separate whole-suite validation contract.

### Temporary consumer trial and documentation

Acceptance also needs one real consuming environment trial using transient
shell selection and the supported import directory. Cover plain prepared-shell
pytest and an actual groundhog test stage. Leave project files and persistent
activation unchanged. A Python 3.12 trial may supply both evidence obligations,
but cannot replace recurring standalone regression checks.

Publish only anonymous commands, interpreter/platform versions, selected
policies, outcomes and cleanup evidence. Keep consumer identities, private
absolute paths and raw environment output out of tracked evidence.

Update the existing lifecycle reference and limit-setting guide and add
consumer adoption guidance for each policy. Explain the activation boundary,
exit-4 startup failures, bootstrap refresh and cleanup, tracked-key registration
with its plugin-manager guard,
independent marker registration, fixture dictionary, thread-specific permission
ownership and summaries. Explain pool/helper starts on other threads.
Cover temporary higher limits, gradual
reduction and full runs without selection or early stop to enumerate offenders.
Update `instructions/write-fast-python-tests.md` with the shared enforcement
contract. Present documentation categories in explanation, tutorials, how-to
guides, reference order; preserve each page's existing Diataxis purpose.

## Acceptance cases for the v0.14.0 shared lifecycle design

| Scenario | Expected outcome | Requirement basis |
| --- | --- | --- |
| Neither selected | No new enforcement, records or policy summaries. | Q01, Q11. |
| Gate only beside consumer `tools` and `tests` | Consumer packages import; limits and band work; process starts alone are permitted. | Independent loading and collision isolation. |
| Audit only | Unpermitted starts fail during setup/call/teardown; exemption report only. | Q04, Q05, Q14. |
| Prepared plus explicit selection | One canonical registration and one set of summaries. | Q01. |
| Missing selected module, blocked plugin or unsupported version | Identifying startup usage error, exit 4, before test execution. | Q11, Q15. |
| Shared checkout disappears after preparation | Independent bootstrap names the selected policy and selection, exit 4, including plain pytest and `python -m pytest`; no fallback policy. | Q11, K1. |
| Two shared checkouts prepare the same consumer | Immutable bootstrap entries and environment-carried paths preserve each live shell's original binding. | Supported import route and K1. |
| Live policy contract changes after preparation | Startup exits 4 before registration/tests and asks to prepare the shell again. | Q11, K1. |
| Exempt test triggers unexempt session fixture | Process start is rejected and fixture setup failure is cached normally. | Q12. |
| Exempt fixture requests unexempt fixture | Requested fixture has its own boundary; outer permission is not inherited. | Q12. |
| Exempt fixture and exempt consuming test | Fixture starts credit only the fixture; timing still applies. | Q12, Q14. |
| Invalid unused fixture declaration or module test mark | Pre-execution usage error in serial and xdist. | Q13. |
| Valid declarations with audit absent and strict settings | Normal collection and execution, no unknown config or fixture-mark warning. | Q13. |
| Tracked lifecycle keys with gate absent and strict settings | Root-conftest registration avoids warnings/errors; gate defaults and overrides stay unchanged when loaded. | Prepared opt-in and existing settings. |
| Exempt fixture starts work on another thread during setup | No fixture permission crosses threads; active lifecycle decides authorization. | Q12 ownership. |
| Fixture runs on multiple workers or for several parameters | One fixture summary entry; used if any own instance used permission. | Q14. |
| No safe pre-existing artifact home | Strict gate, no writes, explicit no-home summary. | Q06, Q09. |
| Existing valid checkout record | Exception meaning and eligible proofs survive; one controller write. | Q06, Q09. |
| llm-shared whole-suite validation without Python 3.12 | Validation fails before claiming compatibility success. | Q02, Q16. |
| Consumer validation without a separate Python 3.12 installation | No new interpreter prerequisite for that consumer. | Q16. |
| Anonymous real-environment trial | Both activation contexts evidenced, no project-file changes or persistent opt-in. | Q08. |
| One xdist worker finds an invalid declaration, the others are valid | No test starts on any worker; the controller exits 4 naming the declaration, stops the remaining workers and does not wait indefinitely. | Q13. |
| Embedded session loads and unconfigures the audit inside an audited run | The outer session keeps one dispatcher, its fixture ownership and its permissions. | Q12. |
| Prepared shell runs pytest with a rootpath outside the bound root | Exit 4 naming the bound root and the selection, before registration. | Q01, Q11. |
| Gate loaded with the documented key snippet, in either loading order | Gate defaults, tracked values and `-o` overrides keep their precedence. | Q07, Q10. |

## Open questions for the v0.14.0 shared lifecycle gate design

### Q01: Import route and early loader

Question description: Should consumers expose the dedicated
`tools/pytest_plugins` directory and use the early loader, or receive a
separately installable plugin distribution? Both must preserve Python 3.12,
unique module names, canonical registration and selected-import exit code 4
without installing llm-shared itself.

#### BBQ for Q01

A workshop can lend a small toolbox from its shelf or ship the tools in their
own case. In this picture: the shelf is the dedicated import directory, the
case is an independent distribution, and the check-in desk is the early pytest
loader.

#### Options for Q01

- Option A1: Dedicated import directory plus early loader.
  - pro: Uses the current shared checkout without package resolution against
    llm-shared's Python range; makes one import identity available to both
    activation contexts.
  - con: Preparation must maintain `PYTHONPATH` and option ordering, the
    independent bootstrap cache needs refresh and cleanup.
- Option A2: Independent installable plugin distribution with its own Python
  3.12 metadata and equivalent startup guard.
  - pro: Provides normal package import discovery and isolates runtime
    dependencies through distribution metadata.
  - con: Adds a build/install lifecycle and synchronization of installed code
    with the shared checkout, without per-consumer pinning.

#### Recommended option for Q01 (with arguments for this choice)

Option A1: The dedicated directory fits the existing shared-checkout workflow
and avoids a new distribution lifecycle. Its bootstrap must preflight selected
policies before command-line `-p` options, preserve unrelated options and
report missing infrastructure clearly. Tracked `addopts` precede the bootstrap
and must not contain policy `-p` entries.

#### Answer to Q01: option A1 (with reason why it must be accepted as the answer)

Option A1: The dedicated directory fits the existing shared-checkout workflow
and avoids a new distribution lifecycle. Its bootstrap must preflight selected
policies before command-line `-p` options, preserve unrelated options and
report missing infrastructure clearly. Tracked `addopts` precede the bootstrap
and must not contain policy `-p` entries.

User decision: confirmed — A1, dedicated import directory plus early loader.
Confirmed on 2026-11-06 by the user's explicit selection of option 1 (A1).
The shared-checkout workflow and avoidance of a separate distribution lifecycle
are the accepted rationale; Python 3.12+ compatibility, unique module names,
canonical registration and selected-import exit code 4 remain required.

### Q02: Selection declaration and project binding

Question description: Should selection be declared in the prepared shell and
bound to its project root, or read from a dedicated project file with a
transient override? Automatic activation remains limited to prepared pytest
and groundhog; this does not change that requirement.

#### BBQ for Q02

A room can display today's attendance list on a board or keep a standing
roster in a folder. In this picture: the board is shell selection, the folder
is a tracked selection file, and the room label is the bound project root.

#### Options for Q02

- Option B1: `LLM_SHARED_PYTEST_PLUGINS` in `senv`, with
  `LLM_SHARED_PYTEST_ROOT` captured by preparation.
  - pro: Makes temporary trials file-free and keeps opt-in with the
    environment that actually prepares the project interpreter.
  - con: Persistent choices are less discoverable to editors, and project
    switching needs careful environment refresh and root validation.
- Option B2: A dedicated repository selection file, read only during prepared
  activation, with an explicit transient override.
  - pro: Makes selection reviewable as project data and easy for both
    activation paths to resolve.
  - con: Adds another configuration parser, precedence contract and
    project-root discovery path; transient trials still require an override.

#### Recommended option for Q02 (with arguments for this choice)

Option B1: Shell selection matches the requested prepared-environment boundary
and existing `senv` ownership. Preparation should replace only its own
entries, bind selection to the project and refuse stale cross-project
activation.

#### Answer to Q02: option B1 (with reason why it must be accepted as the answer)

Option B1: Shell selection matches the requested prepared-environment boundary
and existing `senv` ownership. Preparation should replace only its own
entries, bind selection to the project and refuse stale cross-project
activation.

User decision: confirmed — B1, `LLM_SHARED_PYTEST_PLUGINS` in `senv`,
with `LLM_SHARED_PYTEST_ROOT` captured by preparation.
Confirmed on 2026-11-06 by the user's explicit selection of option 1 (B1).
The accepted rationale is alignment with prepared-environment activation and
existing `senv` ownership, including file-free temporary trials. Preparation
must preserve unrelated entries and reject or refresh stale project bindings.

### Q03: Harmless fixture-permission declaration

Question description: Should explicitly identified fixtures be declared by a
plain module dictionary keyed by decorated fixture objects, or by a custom
attribute on their underlying Python functions? Either route must need no
llm-shared import, no fixture mark and no unknown pytest config key.

#### BBQ for Q03

Equipment can carry a label or appear in a signed inventory. In this picture:
equipment is a fixture definition, its label is a Python attribute, the
inventory is `LLM_SHARED_PROCESS_FIXTURES`, and the signature is the required
reason.

#### Options for Q03

- Option C1: `LLM_SHARED_PROCESS_FIXTURES` maps registered decorated fixture
  objects to reasons.
  - pro: Centralizes visible declarations, distinguishes renamed/imported
    fixture objects and remains inert without the audit under strict pytest
    settings.
  - con: Needs explicit object-to-definition resolution and clear conflict
    rules for repeated declarations or overrides.
- Option C2: A documented custom attribute on each fixture's underlying
  Python function.
  - pro: Keeps permission next to the fixture body and avoids a separate
    registry variable.
  - con: Exposes decorator unwrapping details to users and makes invalid or
    misspelled attributes harder to validate before execution.

#### Recommended option for Q03 (with arguments for this choice)

Option C1: The module dictionary offers a consumer interface made entirely of
ordinary Python data. Require resolvable registered fixture objects, non-empty
reasons and rejection of conflicting declarations; keep usage identity tied to
fixture definitions.

#### Answer to Q03: option C1 (with reason why it must be accepted as the answer)

Option C1: The module dictionary offers a consumer interface made entirely of
ordinary Python data. Require resolvable registered fixture objects, non-empty
reasons and rejection of conflicting declarations; keep usage identity tied to
fixture definitions.

User decision: confirmed — C1, `LLM_SHARED_PROCESS_FIXTURES` maps registered
decorated fixture objects to non-empty reason strings.
Confirmed on 2026-11-06 by the user's explicit selection of option 1 (C1).
The accepted rationale is a visible declaration using ordinary Python data,
harmless without the audit and independent of llm-shared imports or fixture
marks. Require unambiguous registered-definition resolution, reject conflicting
declarations and keep usage identity tied to fixture definitions.

### Q04: Fixture execution and finalizer ownership

Question description: Should the audit use a narrow compatibility adapter
around pytest fixture execution/finalization, or public setup hooks plus
wrapping each registered finalizer? The design must identify requested-fixture
boundaries and yield/manual teardown without inheriting outer permissions.

#### BBQ for Q04

A supervisor can track entry and exit at each workshop door or tag every
cleanup task individually. In this picture: doors are fixture
execution/finalization boundaries, cleanup tasks are finalizers, and the
supervisor is the process audit.

#### Options for Q04

- Option D1: A bounded adapter over fixture execution, finalization and
  registry capabilities.
  - pro: Provides one ownership model for setup, dependencies, cached
    fixtures, yield teardown and finalizers; also supports preflight
    declaration resolution.
  - con: Uses pytest internals and needs capability checks, focused
    compatibility coverage and a clear startup error for incompatible future
    changes.
- Option D2: Public fixture setup hooks plus individual finalizer wrapping.
  - pro: Keeps more interaction on published hooks and can isolate ordinary
    setup ownership.
  - con: Has more interception paths for nested finalizers and requested
    dependencies; complete attribution is harder to establish without still
    inspecting internals.

#### Recommended option for Q04 (with arguments for this choice)

Option D1: A small explicit adapter makes the unavoidable compatibility
boundary visible. It must unwind on failures, restore instrumentation on
unconfigure and bind fixture permissions to a live executing thread/token so
background work cannot inherit them. Starts on another thread receive no
fixture permission even during fixture setup or teardown.

#### Answer to Q04: option D1 (with reason why it must be accepted as the answer)

Option D1: A small explicit adapter makes the unavoidable compatibility
boundary visible. It must unwind on failures, restore instrumentation on
unconfigure and bind fixture permissions to a live executing thread/token so
background work cannot inherit them. Starts on another thread receive no
fixture permission even during fixture setup or teardown.

User decision: confirmed — D1, a bounded adapter over pytest fixture execution,
finalization and registry capabilities.
Confirmed on 2026-11-06 by the user's explicit selection of option 1 (D1).
The accepted rationale is one explicit ownership model across setup,
dependencies and cleanup, with a visible compatibility boundary. Require
startup capability checks, restoration on unconfigure, failure-safe ownership
unwinding and permission bound to the executing thread and live token.

### Q05: Xdist declaration-validation barrier

Question description: How should invalid declarations on any worker prevent
every worker from starting tests? The current draft requires a controller
barrier but must choose where collection evidence is obtained.

#### BBQ for Q05

A convoy can wait for every driver to finish inspection or send a separate
inspector along the route first. In this picture: drivers are workers,
inspection is declaration validation during collection, the convoy signal is
controller scheduling, and the separate inspector is extra controller
collection.

#### Options for Q05

- Option E1: Workers validate before reporting successful collection, using
  xdist's existing `collection_is_completed` barrier; controller schedules
  nothing until every worker succeeds.
  - pro: Uses each worker's actual imports and collected definitions and
    avoids an extra controller collection with different side effects.
  - con: Requires explicit worker-to-controller evidence, cancellation and
    exit-4 translation rather than relying only on a worker's normal
    collection failure.
- Option E2: Controller performs an additional collection/validation pass
  before starting worker execution.
  - pro: Gives a single upfront authority for declaration errors and
    simplifies the initial scheduling decision.
  - con: Duplicates collection and imports and can differ from worker-only
    fixtures or configuration; it still needs worker consistency checks.

#### Recommended option for Q05 (with arguments for this choice)

Option E1: The existing all-worker collection barrier validates the
definitions that will execute. Invalid declarations fail collection; the
controller translates their identifying evidence to exit 4. Any declaration
error, missing validation evidence or inconsistent collection must prevent
scheduling; invalid declarations specifically retain the required identifying
exit code 4.

#### Answer to Q05: option E1 (with reason why it must be accepted as the answer)

Option E1: The existing all-worker collection barrier validates the
definitions that will execute. Invalid declarations fail collection; the
controller translates their identifying evidence to exit 4. Any declaration
error, missing validation evidence or inconsistent collection must prevent
scheduling; invalid declarations specifically retain the required identifying
exit code 4.

User decision: confirmed — E1, worker validation before successful collection
using xdist's existing all-worker collection barrier.
Confirmed on 2026-11-06 by the user's explicit selection of option E1.
The accepted rationale is validation of each worker's actual imported fixture
definitions without an extra controller collection pass. Require explicit
worker-to-controller validation evidence, cancellation handling and translation
of invalid declarations to identifying errors and controller exit 4. Declaration
errors, missing evidence or inconsistent collection must prevent all scheduling.

### Q06: Provisioning the recurring Python 3.12 environment

Question description: Should llm-shared provide a separate managed
compatibility environment and dependency manifest, or require each machine to
supply its own prepared Python 3.12 environment? Both fail validation if
Python 3.12 or required dependencies are missing.

#### BBQ for Q06

A measuring station can supply a calibrated instrument or accept one brought
by its operator after checking it. In this picture: the station is whole-suite
validation, the instrument is Python 3.12 plus harness dependencies, and
calibration is version/dependency verification.

#### Options for Q06

- Option F1: A dedicated managed environment from an independent
  compatibility manifest, with a verified absolute-path override.
  - pro: Makes dependency provisioning repeatable without resolving
    llm-shared's Python 3.13 project into Python 3.12.
  - con: Adds one environment and manifest to maintain and needs documented
    explicit setup before unattended validation.
- Option F2: Only an operator-provided absolute Python 3.12 environment with
  documented dependencies.
  - pro: Keeps interpreter provisioning outside repository tooling and can
    fit an existing machine-management policy.
  - con: Allows more machine-to-machine dependency drift and makes setup
    harder to reproduce without a shared manifest.

#### Recommended option for Q06 (with arguments for this choice)

Option F1: A separate manifest and environment make the compatibility promise
repeatable while the override supports managed machines. Validation verifies
the actual version and dependencies, fails instead of skipping, and does not
install into consumer environments.

#### Answer to Q06: option F1 (with reason why it must be accepted as the answer)

Option F1: A separate manifest and environment make the compatibility promise
repeatable while the override supports managed machines. Validation verifies
the actual version and dependencies, fails instead of skipping, and does not
install into consumer environments.

User decision: confirmed — F1, a dedicated managed compatibility environment
from an independent dependency manifest, with a verified absolute-path override.
Confirmed on 2026-11-06 by the user's explicit selection of option F1.
The accepted rationale is repeatable Python 3.12 provisioning separate from
llm-shared's Python 3.13 project, while supporting externally managed machines.
Require explicit documented setup, verification of the actual interpreter
version and dependencies, failure rather than skipping when prerequisites are
missing, and no installation into consumer environments.

### Q07: Compatibility evidence for direct full validation

Question description: A day walk reaches `check.bat`, but direct `ghog full`
bypasses that check today. The executable harness should run independently of
the static-check stage. Which design ensures llm-shared's regular whole-suite
validation always includes the separate 3.12 checks without giving consumers
that obligation?

#### BBQ for Q07

A shipment can require an inspection ticket at every exit or leave through one
designated inspection lane. In this picture: shipments are whole-suite
validations, the ticket is fresh compatibility evidence, exits are day/full
entry paths, and the designated lane is a single documented wrapper.

#### Options for Q07

- Option G1: An explicitly declared own-project executable preflight covering
  every day and direct full invocation; `check.bat` keeps only static 3.12 and
  3.10 parse checks.
  - pro: Preserves direct-full validation while preventing accidental
    compatibility omission and keeps processes outside the audited suite.
  - con: Adds an opt-in validation extension to groundhog and needs strict
    project applicability.
- Option G2: A single dedicated llm-shared whole-suite validation wrapper;
  bare full remains partial evidence until that wrapper completes.
  - pro: Keeps groundhog generic and puts all compatibility orchestration in
    project-local tooling.
  - con: Changes which command establishes the complete validation contract
    and relies on clear routing so users do not mistake bare full success for
    completion.

#### Recommended option for Q07 (with arguments for this choice)

Option G1: An explicit own-project preflight preserves existing day/full usage
and closes the bypass. Its declaration must be independent of shared plugin
selection, invoke fresh executable compatibility checks, keep `check.bat` to
static checks, fail when 3.12 is missing, and never run for ordinary
consumers.

#### Answer to Q07: option G1 (with reason why it must be accepted as the answer)

Option G1: An explicit own-project preflight preserves existing day/full usage
and closes the bypass. Its declaration must be independent of shared plugin
selection, invoke fresh executable compatibility checks, keep `check.bat` to
static checks, fail when 3.12 is missing, and never run for ordinary
consumers.

User decision: confirmed — G1, an explicitly declared own-project executable
preflight for every day and direct full invocation.
Confirmed on 2026-11-06 by the user's explicit selection of option 1 (G1).
The accepted rationale is preserving existing day/full commands while closing
the direct-full compatibility-check bypass. Require fresh executable evidence,
project applicability independent of shared plugin selection, execution outside
the audited test window, and failure when Python 3.12 is missing. Keep
`check.bat` to static and parse checks; ordinary consumers gain no preflight
or separate Python 3.12 prerequisite.

### Q08: Bootstrap storage independent of the shared checkout

Question description: K1 already requires identifying startup exit code 4
when a selected policy cannot be imported. A loader imported only from the
shared checkout disappears with that checkout, leaving pytest's own exit
code 1. Where should preparation materialize an independent, self-contained
bootstrap so the confirmed K1 behavior still holds in a stale prepared shell?
Both options use immutable, content-addressed entries containing only the loader,
with project root, policy directory and selection carried in the environment.
A bootstrap-to-policy contract check refuses mismatches with exit code 4 and
asks to prepare the shell again. Neither option caches policy code.

#### BBQ for Q08

A cookout attendant keeps a checklist separate from the supplier's toolbox.
If the toolbox vanishes, the attendant can still name the missing thermometer
and stop cooking. The checklist can stay in the attendant's usual office or
another office chosen by the organizer. In this picture: the checklist is
the bootstrap, the toolbox is the shared checkout, the usual office is a
user-local cache, and the chosen office is an explicit external cache location.

#### Options for Q08

- Option H1: Atomically publish the bootstrap in a user-local cache, in an
  immutable directory named by the SHA-256 hash of its source. Bind project,
  policy path and selection through the prepared environment.
  - pro: Preserves K1 after shared-checkout removal without changing consumer
    files, installing a distribution or requiring a review artifact home.
  - con: Adds cache validation and cleanup rules; old entries stay until the
    user runs the documented cleanup.
- Option H2: Require an explicitly configured writable external cache directory
  separate from both checkouts and from the review artifact home, with the
  same immutable content-addressed layout and environment-carried binding.
  - pro: Preserves K1 with storage controlled by an operator's environment
    policy and no consumer-file or lifecycle-record side effects.
  - con: Adds mandatory machine configuration, path validation and cleanup
    instructions instead of a conventional cache default.

#### Recommended option for Q08 (with arguments for this choice)

Option H1: A content-addressed user-local cache preserves the no-project-file
trial and leaves missing artifact homes untouched. The cached bootstrap
contains no policy and imports only stdlib and pytest. It preflights the
bound shared path, refuses fallback policy copies and reports missing selected
policies with exit code 4. The cache precedes the shared policy directory on
`PYTHONPATH`. Re-preparation selects the correct source-hash directory without
replacing one a live shell uses. Cleanup is an explicit documented user
operation, never an automatic preparation step.
The loader checks the selected policies' bootstrap contract before registration
and refuses mismatches with exit code 4 and a re-preparation diagnostic.

#### Answer to Q08: option H1 (with reason why it must be accepted as the answer)

Option H1: An independent user-local bootstrap preserves the confirmed K1
contract even when the whole shared checkout disappears after preparation.
Acceptance covers plain `pytest`, `python -m pytest` and script entry points
in that stale environment. A failed preparation publishes no partial
activation. Multiple shared checkouts cannot overwrite a live shell's loader
or policy-path binding. Contract mismatches ask for re-preparation before tests.

User decision: confirmed — H1, an atomically published user-local bootstrap
cache with immutable entries named by the source SHA-256 hash.
Confirmed on 2026-11-06 by the user's explicit selection of option H1.
The accepted rationale is preserving identifying startup exit 4 after shared
checkout removal without mandatory cache configuration or consumer-file changes.
Cache only the self-contained loader, carry bindings in the environment, verify
existing entries and reject policy-contract mismatches with exit 4 and a request
to prepare the shell again. Failed preparation publishes no partial activation;
cleanup remains an explicit documented user operation. Do not create a review
artifact home or cache policy code.

### Q09: Lifecycle settings where the gate is not loaded

Question description: Tracked `test_lifecycle_*` settings are unknown to
pytest when the gate is absent, including unprepared and audit-only runs.
They warn normally and fail under warnings-as-errors or strict configuration.
How should the adoption interface keep tracked limits usable across selections
without importing shared code in those runs?

#### BBQ for Q09

A club keeps preferred grill temperatures on a card in every picnic basket.
Guests without the club's thermometer still need a legend to understand the
card. The legend is plain-pytest key registration, the card is tracked
configuration, and the thermometer is the gate. Alternatively, temperatures
can be handed out only to guests using that thermometer.

#### Options for Q09

- Option I1: Provide a plain-pytest root-conftest `pytest_addoption` snippet
  registering the four keys with `parser.addini`; the gate resolves its own
  defaults independently of registration defaults.
  - pro: Tracked settings work without shared imports in unprepared and
    audit-only runs, including strict configuration and warnings-as-errors.
  - con: Projects maintaining non-default tracked limits also maintain a short
    registration snippet whose key names must match the gate.
- Option I2: Supply settings only as prepared-run `-o` overrides and keep
  those keys out of tracked pytest configuration.
  - pro: Runs without the gate never see unknown keys.
  - con: Moves reviewed project settings into shell preparation and adds a
    precedence interface to maintain.
- Option I3: Document the unknown-key limitation and require strict projects
  to use defaults or prepared `-o` overrides.
  - pro: Adds no registration mechanism.
  - con: Tracked limits warn without the gate and fail strict runs, reducing
    usability of the confirmed project-configuration interface.

#### Recommended option for Q09 (with arguments for this choice)

Option I1: Plain-pytest registration preserves tracked settings across policy
selections. The gate reads configuration presence and `-o` overrides
explicitly, keeping its documented defaults even if a later root-conftest
registration supplies different registration defaults.

#### Answer to Q09: option I1 (with reason why it must be accepted as the answer)

Option I1: Document the root-conftest registration, keep default resolution
owned by the gate, and verify tracked settings with the gate absent under
strict configuration and warnings-as-errors. Also verify default and override
precedence with the gate loaded.

User decision: confirmed — I1, a plain-pytest root-conftest snippet registering
the four lifecycle keys with `parser.addini`, with defaults owned by the gate.
Confirmed on 2026-11-06 by the user's explicit selection of option I1.
The accepted rationale is preserving tracked project settings across policy
selections without shared imports or activation when the gate is absent.
Verify unprepared and audit-only runs under strict configuration and
warnings-as-errors, and verify explicit configuration, gate-owned defaults and
`-o` override precedence when the gate is loaded.

### Q10: Gate defaults beside the key-registration snippet

Question description: The confirmed I1 snippet and the gate both register the
four `test_lifecycle_*` keys with `parser.addini`. pytest 9.1 keeps the last
registration's type and default, and a root conftest registers after a `-p`
plugin, so an unguarded snippet replaces the gate's defaults. Telling an absent
key from an explicit one would need `config.inicfg`, deprecated in pytest 9.1
and an error under warnings-as-errors, or pytest's private configuration store.
How should the gate keep its own defaults and the `-o`/project/default
precedence? Q09's recommendation describes reading presence explicitly, which
is J2's mechanism; J1 or J3 keeps I1 and replaces that sentence at consolidation.

#### BBQ for Q10

Two people write a grill temperature card for the same grill. When the club's
thermometer is there, the club's card must be the one in use. In this picture:
the cards are the two `addini` registrations, the club's card is the gate's
registration, and looking for the thermometer is the plugin-manager guard.

#### Options for Q10

- Option J1: The documented snippet takes
  `pytest_addoption(parser, pluginmanager)` and registers the keys only when
  `pluginmanager.has_plugin("llm_shared_lifecycle_gate")` is false. The gate's
  own registration then supplies the defaults, and `config.getini` keeps
  today's precedence.
  - pro: Uses only public pytest API, keeps the current settings reader and
    works in both loading orders, under strict configuration and
    warnings-as-errors.
  - con: An outdated snippet copy without the guard silently replaces the
    gate's defaults when the gate loads first; public API cannot detect it.
- Option J2: The gate reads raw presence and `-o` origin from pytest's private
  configuration store behind a startup capability check, with exit code 4
  when the store changes.
  - pro: Stays correct whatever defaults a snippet registers.
  - con: Adds a second private pytest surface beside the fixture adapter, in
    an area pytest 9.1 is already moving to `getini`.
- Option J3: Prescribe a snippet registering string keys with `default=None`;
  the gate treats `None` as absent and applies its own defaults.
  - pro: Uses only public API, and the gate default applies in either loading
    order.
  - con: A snippet with any other default silently becomes project
    configuration, so consumers must copy exact defaults rather than one guard.

#### Recommended option for Q10 (with arguments for this choice)

Option J1: The guard keeps the gate's registration authoritative through a
documented hook argument, adds no pytest internals and keeps the current
settings reader. Document the guard as part of the snippet. Verify both loading
orders, an absent key, a tracked value and an `-o` override with the gate loaded,
and tracked keys with the gate absent under strict configuration and
warnings-as-errors.

#### Answer to Q10: option J1 (with reason why it must be accepted as the answer)

Option J1: It meets Q09's gate-owned defaults with public pytest API in every
loading order the design supports.

User decision: confirmed — J1, the plain-pytest snippet registers lifecycle
keys only when `pluginmanager.has_plugin("llm_shared_lifecycle_gate")` is false.
Confirmed on 2026-11-07 by the user's explicit selection of option 1 (J1).
The accepted rationale is preserving gate-owned defaults through public pytest
API while retaining `config.getini` and explicit project/`-o` precedence.
Document the guard as part of the required snippet; an outdated unguarded copy
can silently replace gate defaults. Verify both loading orders, absent keys,
tracked values and `-o` overrides with the gate loaded, and strict configuration
and warnings-as-errors with it absent. Q09's I1 remains confirmed; its historical
presence-reading recommendation is replaced by J1 only during authorized
consolidation. This decision requires independent follow-up review and does
not authorize consolidation.
