# v0.14.0 release-project-root implementation plan

Establish the shared release engine's project identity, runtime readiness and
safe invocation foundation before adding release-domain behavior.

## Plan goal and scope for v0.14.0 release-project-root

Implement the approved [design](design.v0.14.0.release-project-root.md) and
[requirement](feature-request.v0.14.0.release-project-root.md), beside the
[focused draft](draft.v0.14.0.release-project-root.md). This is item 1 of the
[sibling release tooling umbrella](draft.v0.14.0.sibling_release_tooling.md).

1. Publish and validate the setup-owned runtime and its release dependencies.
2. Establish isolated Git execution and physical project/path identity.
3. Parse strict optional configuration through shipped domain schemas.
4. Provide read-only artifact resolution, managed writes and operation locking.
5. Wire context, transport, dispatch and the two real Windows launchers.
6. Prove the integrated foundation and document supported invocation routes.

Items 2–8 retain version sources, git-cliff, changelog processing, release
transactions/recovery, installation/upgrades, prepare-release integration and
consumer cutover. Item 1 includes only the approved narrow current-setup runtime
producer. Existing build/senv call migration, alias installation, actual build
execution and title acquisition belong to later owners. Missing domain handlers
must fail explicitly; this plan does not add successful placeholders.

The six steps are sequential. Their service APIs can be exercised before public
dispatch exists. Final acceptance uses a verified tooling copy with a generated
test handler and registry entry; production has no handler-injection surface.

## File-based IO cost clarification for v0.14.0 release-project-root

This synchronous CLI reads tooling dependency metadata and selected project
declarations once per invocation, retaining validated data in memory. The
launcher reads the runtime record to locate Python; bootstrap reads it again
to validate identity, so the record read bound is once per component.
It must not scan old environments, load unrelated consumer files or prepare
artifacts during readiness, preflight or read-only work. Git
identity/configuration probes and path-ancestor checks are necessary validation,
not reasons to scan the whole worktree. Revalidate managed paths immediately
before mutation; use same-parent temporary files and atomic replacement.
There is no document-index or event-loop requirement.

Readiness is linear in the relevant lock graph and parsed metadata; path checks
scale with path depth; configuration checks scale with declarations. Deduplicate
dependency visits and schema ownership checks. Do not add repeated whole-file
reads per key or enumerate all installed distributions when named lookups suffice.
These are operation-count expectations, not an invented wall-clock SLA.

## Confirmed source and test-tree facts

Inspection baseline: 2026-10-21, branch `release-project-root`, before implementation.
The effort documents share `docs/v0.14.0/`; the two plans are new.

- `senv.bat` initializes identity before its guard and calls external
  `switchpy`; it currently publishes no authoritative runtime identity.
- `pyproject.toml` requires Python `>=3.13,<3.14`, sets `package = false`,
  discovers tests below `tests`, and currently defines only a dev group.
- `tools/git_command.py` accepts cwd/env/stdin but executes bare Git. Keep it
  unchanged for existing consumers; the new adapter pins an absolute executable.
- `ReviewArtifactConfiguration.load` is read-only and accepts a tracking
  callback. Its preparation method and `tools/artifact_home.py` conveniences
  write or migrate files. Reuse only its parser/resolver during preflight.
- `tools/__init__.py` has eager public imports. The standalone readiness path
  must not import that package before metadata validation; test import ordering.
- Existing `tests/unit/tools` packages contain Git and artifact regression
  suites. Their autouse fixtures mock `os.fsync` and review-store persistence;
  child-process acceptance must exercise real filesystem boundaries.
- The existing `tests/acceptance` tree proves that subprocess acceptance is
  established. New test leaves below use the requested
  `tests/unit/.../test_name/test_name_tdd.py` convention, including a clearly
  identified integration leaf; its child processes are not mocked unit tests.
- No `tools/release_workflow`, corresponding test package, or release launcher
  currently exists. Existing package initializers need no export changes.

### Physical-line baseline and policy

Counts include blank lines, using the gate's
`sum(1 for _ in path.open(encoding="utf-8", errors="ignore"))` metric.
The active project ceiling is 650 Python lines, set by `senv.bat`; do not
substitute the standalone checker's fallback limit.

| Existing file | Lines | Planned use |
| --- | ---: | --- |
| `senv.bat` | 331 | Step 1 update |
| `pyproject.toml` | 256 | Step 1 update |
| `uv.lock` | 635 | Step 1 regenerate |
| `README.md` | 1126 | Step 6 update |
| `wiki/reference/aliases-and-launchers.md` | 130 | Step 6 update |
| `wiki/reference/automation-and-direct-invocation.md` | 69 | Step 6 update |
| `.gitignore` | 121 | Reference; already ignores `venvs/` |
| `tools/__init__.py` | 94 | Reference; safe, unchanged |
| `tools/git_command.py` | 102 | Reference; safe, unchanged |
| `tools/review_artifact_configuration.py` | 184 | Reuse unchanged; safe |
| `tools/artifact_home.py` | 101 | Reference; safe, unchanged |
| `tests/__init__.py` | 7 | Existing parent, unchanged; safe |
| `tests/unit/__init__.py` | 6 | Existing parent, unchanged; safe |
| `tests/unit/tools/__init__.py` | 6 | Existing parent, unchanged; safe |
| `tests/acceptance/__init__.py` | 4 | Reference, unchanged; safe |
| `tests/conftest.py` | 34 | Existing Hypothesis settings, unchanged; safe |
| `tests/unit/tools/conftest.py` | 78 | Existing mocks, unchanged; safe |
| `tests/unit/test_pyproject_metadata.py` | 44 | Regression suite, unchanged; safe |
| `tests/unit/tools/test_git_command.py` | 144 | Regression suite, unchanged; safe |
| `tests/unit/tools/test_review_artifact_home/test_review_artifact_configuration_tdd.py` | 218 | Regression suite, unchanged; safe |
| `docs/v0.14.0/feature-request.v0.14.0.release-project-root.md` | 353 | Pre-clarification planning baseline |
| `docs/v0.14.0/design.v0.14.0.release-project-root.md` | 706 | Pre-clarification planning baseline |

No involved existing Python file is in the 550–650 risk band or above 650.
Non-Python counts are recorded without imposing the Python ceiling on them.
Every proposed new file starts at zero. Below 550 is safe; 550–650 is at risk;
above 650 requires a responsibility split. Recount on each step because earlier
steps and concurrent changes can alter these baselines.

### Runtime files

`venvs/release-runtime.v1.txt` is an ignored, setup-produced identity record,
not a tracked fixture. Its versioned line format records the checkout-relative
environment directory; the producer measures the actual prepared interpreter
and prefix, and the bootstrap checks the selected executable/prefix against it.
Keep serialization and parsing in one tested contract. Reject extra/invalid
fields, unsupported versions and escape from the selected checkout's `venvs`.

Project-local lock state lives under the validated artifact home, for example
`.reviews/a.release-operation.lock`. It is runtime data created only after full
mutation preflight. Test records and payloads are generated under temporary
roots with generic names; no machine-specific paths, private terms, endpoints
or captured local configuration enter source or committed fixtures.

## Shared execution command checklist

Each step references this checklist and the command templates below.

1. Start/resume its journal using the step-journal workflow; record current
   baselines for every affected file, including package initializers.
2. Add the step's behavior tests first and confirm the intended failing boundary
   through groundhog. Implement that boundary without weakening coverage.
3. Run its targeted tests through groundhog, including named existing regressions.
4. Run its `rg` checks; inspect matches rather than treating all matches as faults.
5. Resolve and run the command printed by `pw scope day` for the current
   requirement. Follow its printed repair/restart instructions until the
   requested objective passes. Do not cache or freeze a scope selector.
6. Recount physical lines. Any Python file above 650 must be split before
   completion. For 550–650, avoid growth and use the step's split guidance.
   Exceeding an advisory estimate while remaining at or below 650 is recorded
   as variance, not missing work.
7. Record test/coverage evidence and file counts in the matching validation step.
   Check staged changes with configured sensitive-content protection before
   committing. Keep all published evidence paths repository-relative.

## Ready-to-run command templates

Follow [run-pw](../../instructions/run-pw.md),
[command execution](../../rules/run_commands.md) and
[groundhog](../../instructions/groundhog.md). Resolve the canonical shared
checkout from the instruction location; substitute it in the launcher paths
below. The placeholder is documentation, not an ambient environment assumption.

- Before/after counts: use the gate metric above with the selected project
  interpreter; a PowerShell `[System.IO.File]::ReadAllLines($path).Count`
  gives the same physical-line count for these UTF-8 files.
- Targeted tests: `& "<LLM_SHARED_DIR>\bin\ghog.bat" single <step-test-files>`.
- Search: `rg -n '<step-pattern>' tools/release_workflow <step-test-files>`.
- Scope resolution:
  `& "<LLM_SHARED_DIR>\bin\prompt_workflow.bat" scope day`.
  Execute its printed ghog command through the resolved `ghog.bat` launcher.
- If inherited `PRJ_DIR` names another checkout, scope it to the current
  project for these workflow calls and restore it afterward. Do not change
  parent-shell state or use activation to repair selector provenance.

The default day objective runs project checks plus affected tests and
deliberately skips full. Use the same resolver for all completion gates.
Where acceptance/coverage needs a broader groundhog level, request it through
`pw scope day --full=cov` and execute the printed command. No step schedules
direct `pytest` or `check.bat` execution.

## Performance-gate assessment

No Step 0 or speculative timeout/xfail performance gate is warranted: the
approved design defines no measured latency target or async responsiveness
requirement. Add deterministic read-count/scan-avoidance assertions with each
owning step. Bound subprocess tests to detect hangs and hidden prompts; those
test-harness safety timeouts are not product performance targets. Groundhog
owns duration measurement and any necessary slow-test repairs.

## Shared test architecture and coverage

In-process tests cover every new production Python line. `bootstrap.py` and
`cli.py` expose `main(argv, ...)` with injectable process state; use the existing
thin-launcher `# pragma: no cover - thin launcher boundary` or `runpy` pattern
for their guards only. Restore `sys.path`, `sys.modules` and
`sys.dont_write_bytecode` after bootstrap tests. pytest-cov 7 does not measure
the child processes here: subprocess/console acceptance proves behavior and
does not supply the 100% coverage gate.

Step 1 creates shared fixtures in `conftest.py` and `test_support.py` under
`tests/unit/tools/release_workflow`. Build repository A/B and linked/nested
templates once per session; materialize isolated case copies in fixture setup,
repairing absolute Git metadata pointers so a copy cannot address its template.
Create the tooling copy and its own `venv --without-pip` once per session.
Compare its manifest with the shipped tree: only the generated handler module
and explicit registry entry may differ in source; runtime data lives in ignored
`venvs`. No argument, environment variable, consumer file or import path can
register a production handler. Test that the unchanged checkout rejects the
same operation names.

Use one cmd or Windows PowerShell 5.1 process per caller-family case matrix
in a fixture, retain structured results, and assert each case in a fast test
call. Keep PBT in-process and spawned process counts small and fixed. Keep test
calls below groundhog's one-second outlier floor without `ghog exclude`; record
fixture/setup durations and total matrix cost too. Moving work into fixtures
does not itself prove a performance improvement. Reuse these helpers through
Step 6; production policy is exercised independently in-process.

Use directory junctions for real directory-link tests without elevation. Probe
file-symlink capability once. Without Developer Mode or elevation, report those
real cases as missing evidence, retain deterministic path-policy coverage, and
obtain the real evidence on a capable Windows host before claiming completeness.

## Step 1. Authoritative runtime production and readiness

### Step 1 analysis and intent

Issues: release startup has no setup-owned runtime identity, and copying
existing newest-venv launchers would violate the approved runtime policy.
Fix intent: establish the record producer and a standard-library readiness
boundary before implementing consumers. Outcome: a fresh successful setup
produces one usable identity; unusable or unready identities fail without
fallback, repair or consumer writes.

Framing: design Q02, Q08 and Q09; AC6–AC7 and AC9. Dependency graph traversal
is linear with a visited set. Preserve existing setup, dev dependency
installation and public tools exports. Apply the shared execution checklist
and ready-to-run templates.

### Step 1 implementation

Files involved:

- `senv.bat` (existing, to be updated).
- `pyproject.toml` (existing, to be updated).
- `uv.lock` (existing, to be updated).
- `bin/release_runtime_record.bat` (new, to be created).
- `tools/release_workflow/__init__.py` (new, to be created).
- `tools/release_workflow/bootstrap.py` (new, to be created).
- `tools/release_workflow/runtime_identity.py` (new, to be created).
- `tools/release_workflow/readiness.py` (new, to be created).
- `tools/release_workflow/markers.py` (new, to be created).
- `tests/unit/tools/release_workflow/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/conftest.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_support.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_runtime/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_runtime/test_runtime_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_readiness/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_readiness/test_readiness_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_readiness/test_readiness_pbt.py` (new, to be created).

Tests first: measure actual interpreter/prefix publication after successful
preparation; reject failed `switchpy`/dependency preparation, missing or
malformed records, unsupported platform/architecture/Python, directory escapes,
moved/broken environments and foreign prefixes. Leftover environments must not
alter selection. Exercise absent/mismatched direct and transitive packages,
markers, dependency cycles, dev-only packages and engine import failure.
Use synthetic lock graphs for nonempty dependency closure and PBT for
marker parsing/graph traversal invariants; never evaluate marker text as Python code.
Retain the existing pyproject metadata tests.

Test the setup entry with a fake prepared environment and saved success/failure
statuses, independently of full machine setup or external `switchpy`. Assert
that `tools` is absent from `sys.modules` until readiness passes, including on
failure. After the gate, test that the complete engine import closure uses no
third-party distribution outside the locked release closure, including eager
imports from `tools/__init__.py`.

Classes and behavior:

- `RuntimeIdentity` and its producer measure `sys.executable` and
  `sys.prefix`; serialize the version and relative environment with Python,
  not batch echo. Publish atomically only after preparation succeeds. Preserve
  failure status before `popd` or macro restoration can replace it.
- In `senv.bat`, save `switchpy` status immediately and pass it to
  `bin/release_runtime_record.bat` before `popd` or macro restoration. The entry
  publishes nothing on a nonzero status; on success it runs the standalone
  producer through the prepared environment's absolute
  `%VIRTUAL_ENV%\Scripts\python.exe -I -X utf8`, never bare `python`.
  Verify the measured interpreter/prefix belongs to this checkout before
  publishing. Capture producer status before cleanup and propagate failures.
  Existing valid identity remains subject to readiness on every release call.
- Declare `release` and include it from `dev` using PEP 735. Declare only actual
  runtime third-party imports; a stdlib-only foundation may have an empty group.
  Test nonempty closures with fixtures regardless. Regenerate the lock through
  the project's uv workflow and preserve its public-URL clean filter.
- `bootstrap.py` is directly executable under `-I -X utf8`. Disable bytecode
  writes, derive sibling helper paths from `__file__`, and load
  `runtime_identity.py`, `markers.py` and `readiness.py` with
  `importlib.util.spec_from_file_location` under private module names. Wire
  their dependencies explicitly; no package-relative imports or search-path
  additions before readiness. After the gate, insert only the selected checkout
  root and import `tools.release_workflow.cli`. This enters the existing eager
  `tools/__init__.py` closure (26 modules today, stdlib only); test that closure
  rather than assuming it will remain free of undeclared dependencies.
  Pass only plain data (paths, strings and parsed record fields) across the
  gate; never rely on private-class instances matching package-module twins.
  Type loaded helper interfaces with small protocols or explicit casts in the
  bootstrap so pyright strict passes without suppressions.
- `readiness.py` reads that checkout's TOML/lock, resolves the applicable release
  closure and checks named installed distributions with `importlib.metadata`.
  `markers.py` uses a stdlib tokenizer/parser for the closed contract below;
  unknown/unevaluable markers fail with package and marker diagnostics.
- Bootstrap failures return 2 on stderr, never import a handler, and leave the
  consumer unchanged. After readiness, the engine import is itself checked;
  no import-name inference from distribution names.

Closed readiness input contract:

- Accept lock format `version = 1`; reject any other format, without keying on
  `revision`. Identify one root package by `source = { virtual = "." }` and
  the normalized project name; require its `metadata.requires-dev.release`.
  If that list is empty, absent `dev-dependencies.release` or an absent
  `dev-dependencies` table means an empty closure. A nonempty metadata list
  without locked release edges fails with 2. Test both empty shapes against
  uv-generated locks as well as nonempty/missing-edge failures.
  Traverse applicable dependency edges with a visited set. Resolve
  duplicate names by explicit edge `version` and source kind; treat registry
  URLs as opaque location data, not package identity. If candidates still tie,
  fail closed rather than select arbitrarily. Reject nonempty dependency
  `extra` lists with package/extra diagnostics; absent or empty lists are valid.
  Domain owners cannot declare a release dependency requiring extras until
  readiness supports them.
- Supported marker variables are `sys_platform`, `os_name`, `platform_system`,
  `platform_machine`, `implementation_name`, `python_version` and
  `python_full_version`. Support `==`, `!=`, `<`, `<=`, `>`, `>=`, `in`,
  `not in`, `and`, `or` and parentheses. Compare version variables as release
  tuples with trailing zero padding, other ordered strings lexically, and
  membership as string membership.
  Reject unsupported variables/operators, malformed versions and `extra`;
  never silently skip an unevaluable marker.
- Compare installed distribution names and versions, never registry URLs.
  Verify identical readiness decisions for clean committed and filter-rewritten
  working-tree locks using synthetic generic registry locations only.
- Read `pyproject.toml` for interpreter requirements, existence of `release`
  and inclusion by `dev`; obtain the release dependency graph from the lock.
  Accept `requires-python` as comma-separated `==`, `!=`, `<`, `<=`, `>` and
  `>=` clauses on release versions, using the same release-tuple comparison.
  Reject `~=`, `===`, wildcards, prereleases and local versions with status 2
  naming the unsupported specifier; test the current `>=3.13, <3.14` form.
  A repository test proves `package.metadata.requires-dev.release` agrees with
  `[dependency-groups].release`; runtime does not implement PEP 508 parsing.

Completion: producer and readiness tests plus metadata regressions pass;
`rg -n 'VIRTUAL_ENV|PYTHONPATH|glob|rglob|import_module' tools/release_workflow`
confirms no ambient fallback or old-environment scan. Run the command printed
by `pw scope day` to its requested objective. Record one fresh successful setup
run and its measured record in private evidence, publishing only generic
results and repository-relative paths. Public launcher proof is Step 5.

### Step 1 addendums

Line-budget checkpoint:

- [ ] Existing non-Python baselines: senv 331, pyproject 256, lock 635; recount.
- [ ] New setup batch entry: baseline 0; keep minimal and record final count.
- [ ] Every new Python file above: baseline 0, safe band, ceiling 650.
  Advisory: 150–400 per behavior module, 250–500 per TDD/PBT file, under 30
  per initializer. No mandatory shrink target.
- [ ] New fixture/support modules: baseline 0, ceiling 650, advisory 200–400;
  split repository builders, tooling-copy setup and result storage if needed.
- [ ] Split readiness tests by runtime identity, closure and marker grammar
  before any file exceeds 650; retain shared graph builders in a small helper.

Full-workflow timing readiness: targeted runtime/readiness tests and existing
metadata regression, followed by the shared resolved day gate. No Step 1
time-gated xfails; capture normal duration evidence.

## Step 2. Controlled Git and physical project boundaries

### Step 2 analysis and intent

Issues: bare Git and ambient routing can target another repository; textual
path containment misses junctions and linked/nested worktrees. Fix intent:
select one Git executable, sanitize a copied environment, inspect effective
configuration and construct physical project identity. Outcome: explicit B
remains B even when caller state names A; aliases can later discover B safely.

Framing: Q01/Q11, AC1–AC4. Probe only required Git metadata and managed-path
ancestors. Preserve compatible user identity, signing, credentials and config
file selection, and preserve the old Git helper's behavior for other tools.
Apply the shared checklist and ready-to-run templates.

### Step 2 implementation

Files involved:

- `tools/release_workflow/git_environment.py` (new, to be created).
- `tools/release_workflow/git.py` (new, to be created).
- `tools/release_workflow/paths.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git/test_git_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_paths/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_paths/test_paths_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_paths/test_paths_pbt.py` (new, to be created).

Tests first: two repositories and a linked worktree; explicit missing,
nonexistent and subfolder roots; equivalent physical spellings; external and
internal junctions; nonexistent destination ancestors; nested repositories.
Use PBT for path-segment/normalization cases and deterministic Windows tests
for physical links. Reject planted cwd Git, shims, relative/empty PATH entries,
unknown or old Git versions; retain the first eligible absolute executable.

Enumerate environment classes in a table-driven test: worktree/index/common
directory, object/alternate/namespace/discovery, replace/graft/shallow routing;
counted and parameter configuration injection; executable/template controls;
output/pathspec shaping. Include actual Git-supported variable spellings.
Exercise selected global/system files and includes, rejecting external routing
keys with origin/scope before relying on the worktree result. Preserve benign
identity/helpers and never mutate the input environment.

Classes and behavior:

- `GitExecutionContext` retains executable path/version, controlled environment
  and explicit cwd policy. Select from absolute PATH directories excluding the
  engine's captured cwd; never consult PATHEXT shims. Require Git 2.31.0.
- `git_environment.py` owns the enumerated removal/override policy and
  ignored-conflict diagnostics. Preserve config-file selection and compatible
  settings; inspect routing-key origins/scopes using the pinned executable.
  The closed routing-key set is `core.worktree`, `core.bare` and
  `extensions.worktreeConfig` (case-insensitive). Accept these only in `local`
  or `worktree` scope; reject external scopes with key/origin/scope diagnostics.
  Reject every surviving `command`-scope entry after environment cleanup.
  Test each key/scope combination, including benign non-routing settings.
  Configure machine-readable output, literal paths, disabled pagers/editors,
  and detached stdin/disabled prompts for non-interactive use.
- `git.py` runs native argument lists only and requires explicit cwd for every
  subprocess, including config inspection, root discovery and tracking checks.
  Keep original child status/stderr available to the result boundary.
- `ProjectIdentity` separates physical worktree root, Git directory and common
  directory. Explicit root must equal Git's physical top-level. Alias discovery
  accepts a starting subfolder but passes its result through the same validator.
- `authorize_path` in `paths.py` validates existing targets/ancestors and nested
  repository boundaries; linked Git metadata outside the worktree is distinct
  from managed project destinations. Preserve original values for diagnostics.

Completion: focused suites and existing Git-helper regression pass; all planned
environment classes have positive and negative assertions. Inspect
`rg -n 'subprocess|cwd=|shell=|GIT_' tools/release_workflow` for pinned
executables, explicit cwd and complete policy. Run the resolved day gate.

### Step 2 addendums

Line-budget checkpoint:

- [ ] All new Python files: baseline 0, safe band, ceiling 650; advisory 200–450
  per source and 300–500 per test file, under 30 per initializer.
- [ ] Existing referenced Git helper 102 and its test 144 remain unchanged.
- [ ] If tests enter 550–650, split executable selection, environment policy and
  real-repository identity by responsibility; do not grow any file above 650.

Full-workflow timing readiness: focused Git/path tests and the shared gate.
Bound real Git subprocesses against hangs; no product timeout/xfail gate.

## Step 3. Strict configuration and domain schema registration

### Step 3 analysis and intent

Issues: optional configuration must distinguish defaults from invalid input,
and future domains must own their validation without executing consumer code.
Fix intent: build the strict common parser and explicit shipped schema registry.
Outcome: all supplied declarations are validated before mutation, including
those unrelated to a selected command.

Framing: Q03/Q12, AC8–AC9. Parse each declaration once and index schema ownership
in memory. Preserve the separate review-artifact format and behavior.
Apply the shared checklist and command templates.

### Step 3 implementation

Files involved:

- `tools/release_workflow/configuration.py` (new, to be created).
- `tools/release_workflow/schemas.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_configuration/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_configuration/test_configuration_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_configuration/test_configuration_pbt.py` (new, to be created).

Tests first: absent file/defaults, read errors, invalid UTF-8, optional leading
BOM, malformed INI, duplicates/conflicts, unknown keys/sections, required values
without defaults and literal regex/interpolation-looking data. Exercise fixed
sections, prefix families, duplicate ownership, omitted shipped schemas and
cross-section validation with test schemas. PBT covers literal value preservation
and duplicate/unknown ownership rejection, not future-domain semantics.

Classes and behavior:

- `DomainSchema` describes fixed sections/families, keys, value rules, defaults
  and path roles. `SchemaRegistry` composes an explicit tuple and checks
  completeness against shipped declarations without runtime filesystem scanning.
  Each future domain supplies its schema with its own implementation.
- Foundation ships only its `tooling` declaration; synthetic domain schemas
  test extension points. Do not accept hypothetical version/changelog options
  without their shipped owner or implement those domains here.
- `load_configuration` uses strict UTF-8 INI parsing with interpolation disabled
  and one optional BOM. Keep source file/key/value provenance for errors.
  Missing file permits defaults; malformed or invalid input never does.
- Parse the stable `[tooling] minimum-version` field before strict domain
  validation. Accept a release version `MAJOR.MINOR.PATCH` without a `v`
  prefix, as in the umbrella's `[tooling]` example; anything else is malformed.
  Fail closed with status 2 whenever it is declared until item 6 supplies
  comparison. Do not invent snapshot/candidate ordering, accept unknown keys
  or run an upgrade.
- Resolve schema-managed paths through Step 2 and run every registered domain's
  validation irrespective of the immediate command.

Completion: focused tests pass and config failures create no artifacts. Inspect
`rg -n 'ConfigParser|interpolation|minimum-version|importlib|exec\(' tools/release_workflow`
for strict data-only loading. Run the resolved day objective.

### Step 3 addendums

Line-budget checkpoint:

- [ ] New Python files: baseline 0, safe band, ceiling 650; advisory 200–400
  per source, 250–450 per test, under 30 for initializer.
- [ ] If either source approaches 550–650, separate schema descriptors/ownership
  from parsing/diagnostics; split tests along the same boundaries above 650.

Full-workflow timing readiness: focused configuration tests and shared gate.
Assert bounded declaration reads; no Step 3 time-gated xfail.

## Step 4. Managed writes, artifact capabilities and operation ownership

### Step 4 analysis and intent

Issues: artifact conveniences create files too early, path authorization can go
stale, and independent domain locks permit cross-domain mutation interleaving.
Fix intent: expose separate resolution/write capabilities and a shared operation
lock with process identity. Outcome: no-op/failure paths remain unchanged;
cooperating mutations revalidate destinations and serialize per project.

Framing: Q06/Q13, AC4/AC9. Recheck only affected ancestors/targets at mutation
boundaries. Preserve review-exchange behavior, domain-owned transaction order
and cleanup; do not claim hostile-race protection or multi-file read snapshots.
Apply the shared checklist and ready-to-run templates.

### Step 4 implementation

Files involved:

- `tools/release_workflow/artifacts.py` (new, to be created).
- `tools/release_workflow/managed_files.py` (new, to be created).
- `tools/release_workflow/operation_lock.py` (new, to be created).
- `tools/release_workflow/windows_process.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_managed_files/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_managed_files/test_managed_files_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_operation_lock/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_operation_lock/test_operation_lock_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_operation_lock/test_operation_lock_pbt.py` (new, to be created).

Tests first: default/custom artifact homes, tracked or foreign destinations,
unchanged legacy scratch, config symlink escape and nested repositories.
Repoint a junction between authorization and preparation/replacement; inject
temporary-write and replace errors; verify original data and owned cleanup.
Test live contention, PID reuse, exact dead owner, unreadable identity,
retained handoff, absent engine during handoff and different-project concurrency.
Test a crash leaving only a temporary owner file, non-replacing publication
contention, a malformed owner record and an unknown record version.
Use a lock-state PBT for ownership/retention transitions; real contention is
also tested in Step 6 subprocesses.

Classes and behavior:

- `resolve_artifacts` calls `ReviewArtifactConfiguration.load` with Step 2's
  tracking callback, checking the declaration and destination physically.
  It exposes a read-only declaration, not eager `artifact_home` preparation.
- `prepare_artifacts` is available only after complete mutation preflight;
  the managed service revalidates existing home ancestors, then delegates to
  `ReviewArtifactConfiguration.prepare_home()`. Revalidate the prepared home
  physically before lock creation. Keep exact `*` ignore bytes, existing-home
  checks and rollback single-sourced in that helper; no convenience migration
  or copied preparation/parser. `ReviewExchangeError` during read-only loading
  returns status 2; preparation errors after mutation authorization return 1,
  with stderr diagnostics and the helper's owned rollback.
- `authorize_write`, `prepare_directory` and `replace_bytes` share Step 2's
  path policy. Revalidate existing ancestors before creation; create a temporary
  file in the checked parent, revalidate the final physical target, replace
  atomically, and clean only owned temporary data on failure.
- `OperationLock` acquires atomically inside the prepared artifact home after
  complete preflight. Write and flush the complete versioned owner record to a
  same-directory temporary file, then publish with non-replacing `os.rename`
  (Windows rejects an existing destination). Never create the final lock and
  fill it afterward. Clean only this invocation's temporary file; leftover
  temporary records confer no ownership. Revalidate mutable operation state
  after acquisition. Record PID and Windows creation time via
  `windows_process.py`; hold ownership through mutation and cleanup, with
  retain/transfer interfaces for item 5.
- Recovery of a dead process is permitted only when exact ownership is proven
  gone and no retained handoff owns the operation. Unknown identity or an
  abandoned/unverifiable retained handoff fails conservatively and points to
  item 5's future explicit recovery; do not implement recovery CLI here.
  Until then, diagnostics identify the lock's project-relative path, record
  version and available owner fields so a human can decide on deliberate
  removal. Unknown versions are unverifiable, never evidence of a dead owner.
- Reads and rejected preflights never prepare the home or acquire a lock.
  Different project roots use different locks; read operations can observe
  intermediate combinations across multiple atomic writes.

Completion: focused suites and existing artifact-configuration regressions pass;
`rg -n 'prepare_home|artifact_home|write_|replace|mkdir|unlink' tools/release_workflow`
shows consumer writes only behind managed operations (setup record is distinct).
Run the resolved day objective.

### Step 4 addendums

Line-budget checkpoint:

- [ ] New Python files: baseline 0, safe band, ceiling 650; advisory 150–400
  per source and 300–500 per test, under 30 per initializer.
- [ ] Reused artifact configuration 184 and regression test 218 stay unchanged.
- [ ] Split lock state transitions from process interrogation, and managed-write
  tests from artifact-policy tests if any file would exceed 650.

Full-workflow timing readiness: focused tests plus shared gate; acceptance uses
child processes so inherited fsync mocks cannot stand in for real IO.
No Step 4 timing xfails or age-based lock expiry.

## Step 5. Invocation context, dispatch and actual launchers

### Step 5 analysis and intent

Issues: Python APIs alone do not prove batch path preservation, alias origin,
stdin policy or status propagation. Fix intent: compose the completed services
behind explicit-root and alias surfaces and execute the real launchers.
Outcome: one fixed context reaches handlers; supported values survive the
chosen transport and failures stay failures.

Framing: Q04/Q05/Q07/Q10/Q14, AC1–AC2/AC5–AC7/AC10.
Capture inputs once and keep result/diagnostic data in memory. Preserve caller
cwd, environment, codepage and consumer build ownership. Apply the shared
checklist and command templates.

### Step 5 implementation

Files involved:

- `tools/release_workflow/bootstrap.py` (existing, to be updated).
- `tools/release_workflow/invocation.py` (new, to be created).
- `tools/release_workflow/cli.py` (new, to be created).
- `tools/release_workflow/results.py` (new, to be created).
- `bin/release_workflow.bat` (new, to be created).
- `bin/release_alias.bat` (new, to be created).
- `tests/unit/tools/release_workflow/conftest.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_support.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/console_support.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_invocation/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_invocation/test_invocation_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_invocation/test_invocation_pbt.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_launchers/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_launchers/test_launchers_tdd.py` (new, to be created).

Tests first: selectors missing/empty/conflicting, implicit PRJ_DIR forbidden,
standalone missing root inside Git, alias from subfolder/outside Git, stale-root
diagnostics naming both roots, and relative input locators rooted at the project.
Test stdin pipe/file/NUL/console with and without explicit non-interactive mode
using Windows `GetConsoleMode`, not only `isatty`. Missing required input
must fail with no prompt/consent. PBT covers Unicode/free-text preservation
through native arguments and UTF-8 data paths; batch grammar uses concrete
shell cases because pre-Python corruption cannot be detected reliably.

Classes and behavior:

- `InvocationContext` freezes project/runtime/Git/configuration/artifact
  identities, invocation origin/original arguments and interaction policy.
  `invocation.py` captures cwd before work, reads explicitly named variables
  as data and constructs context through Steps 1–4. Selector diagnostics name
  the variable and supplied value. Relative input files use the validated root.
  Expose root Windows/POSIX forms and project name derived from that root,
  plus root-relative `version.txt`, `pom.xml`, `package.json`,
  `changelog-header.md` and `tools/dev_workflow`, matching the locations behind
  `VERSION_TXT_FILE`, `POM_FILE`, `PACKAGE_JSON_FILE`, `HEADER_CHANGELOG_FILE`,
  `DEV_WORKFLOW_DIR` and `PRJ_DIR_unix`. Do not export/set those variables in
  child environments. Test that inherited values and `PRJ_DIR_NAME` alter no
  computed result. Later domains own their use, not the identity computation.
- `cli.py` owns argument parsing, explicit versus alias mode, supported
  file/stdin/native free-text inputs, non-interactive decisions and a shipped
  handler registry. Reject unavailable later-domain operations clearly.
  Unit tests inject handlers in-process; real launchers use the shared verified
  tooling copy. No production plugin/config import or registration override.
- `OperationResult` in `results.py` carries result data and diagnostics.
  Render UTF-8/LF stdout for data and stderr for warnings/errors. Public statuses
  are 0 success, 1 execution failure, 2 invalid input/preflight. Preserve original
  child failure detail; uncaught exceptions/interruption normalize to 1 where
  the outer boundary regains control.
- Both ASCII-only launchers self-locate regardless of inherited tooling
  variables, read the runtime record as data and invoke its Python directly
  with `-I -X utf8`. A missing/unreadable record or missing interpreter prints
  a stderr diagnostic and returns 2 before Python; never try another Python.
  Disable delayed expansion, avoid senv/PATH changes and capture native status
  before cleanup. No directory change before Python captures cwd.
- The bootstrap entry protocol starts with exactly one reserved
  `--entry-kind explicit-batch`, `--entry-kind alias-batch` or
  `--entry-kind explicit-native`, followed by `--` and the original arguments.
  Each batch file supplies its own literal kind; native callers must supply
  `explicit-native`. Missing/duplicate kinds fail with 2, and user arguments
  cannot override the prefix. Only `alias-batch` enables discovery; missing
  roots in explicit modes always fail. Apply batch grammar checks only to
  batch-origin arguments, preserving native argument values.
- Capture the prior code page as the digits after the last colon in localized
  `chcp` output, run `chcp 65001`, and restore the captured value on paths where
  cleanup regains control. A failed `chcp` (including no console) is not an
  error and must not replace the saved operation status. Any colored output
  uses `tools/batcolors` from the launcher's own checkout, never inherited
  `LLM_SHARED_DIR`. Test non-English output and redirected/no-console routes.
- Accept only the approved batch token/path grammar; selectors carry other
  paths. Reject surviving forbidden batch characters without claiming to
  detect corruption before process entry. Automation and cross-checkout
  callers invoke designated Python/bootstrap with native argument lists.
- Test the build-adapter contract with a disposable script: derive its root
  from its own location inside `setlocal` with delayed expansion off; retain
  selectors through synthetic pre/build/post; `pushd` to selected launcher,
  stop on failure, `call .\release_workflow.bat`, preserve status and `popd`.
  Do not migrate the real consumer build or its existing senv call here.
- PowerShell 5.1 fixtures use environment API assignment and `finally`
  restoration/removal. Prompt examples assign fresh per launch and explain
  persistence. An existing valid stale selector cannot reveal another intent.
  Alias fixtures never use the build's temporary-directory route.

`console_support.py` uses Windows `CreatePseudoConsole` through stdlib ctypes
to host cmd, submit real doskey input and deliver Ctrl+C. Keep its resources
bounded and close handles/processes in fixture teardown. Capture each route's
actual cancellation outcome: batch routes show `Terminate batch job (Y/N)?`
(or the localized equivalent); use the localized yes and no answers, reading
their keys from the captured prompt. Yes terminates without a promised final
diagnostic; no lets the launcher return 1 with stderr diagnostics. Native
execution returns 1 with diagnostics. Redirected stdin must never prompt.
Verify environment, cwd and codepage restoration wherever cleanup can run;
capture terminal-abort behavior explicitly rather than claiming cleanup after
termination.

Completion: real launcher tests exercise Windows cmd, doskey expansion,
PowerShell 5.1, Python native automation and explicit alternate checkout.
Include project and tooling paths containing spaces, Unicode, percent, caret,
bang and ampersand; free text also includes quotes and literal environment-like
text. Inspect
`rg -n 'senv|PYTHONPATH|set /p|shell=True|pushd|GetConsoleMode' tools/release_workflow bin/release*.bat`
for forbidden activation, hidden prompting and adapter leakage; a runtime-record
read is distinct from an interactive `set /p` prompt. Run the resolved day gate.
Step 5 cannot be complete while any supported caller lacks real transport or
cancellation evidence; an unavailable console harness is missing work.

### Step 5 addendums

Line-budget checkpoint:

- [ ] Bootstrap's planning baseline is 0 (created by Step 1); measure its actual
  Step 5 entry count, classify safe/risk/split-required, enforce ceiling 650.
- [ ] Every other new Python file: baseline 0, safe band, ceiling 650; advisory
  200–450 source, 300–500 tests and under 30 initializers.
- [ ] Both new batch files start at 0; keep them minimal and record final counts.
- [ ] Existing fixture/support modules were created in Step 1; measure their
  Step 5 entry counts and enforce 650. New console support starts at 0,
  advisory 200–400, ceiling 650; split Win32 lifetime handling from scenarios.
- [ ] Split launcher tests by caller family and context tests from result
  rendering if needed; never move core policy into batch to reduce Python size.

Full-workflow timing readiness: focused real-launcher matrix and shared gate.
Bound cancellation/hidden-prompt probes; missing real-console evidence remains
an explicit validation gap, never a passing skip. No Step 5 xfail perf gate.

## Step 6. Integrated acceptance and foundation rollout

### Step 6 analysis and intent

Issues: isolated green tests cannot prove cross-project safety, real lock
contention or transport cancellation. Fix intent: validate the assembled
foundation with temporary consumer/tooling roots and publish usable invocation
guidance. Outcome: the item 1 contract is demonstrated and later domain owners
receive working interfaces and explicit remaining ownership.

Framing: all foundation ACs and the approved design acceptance matrix.
Use a small reusable temporary-repository harness, in-memory payloads where
possible and targeted before/after filesystem snapshots in tests only.
Preserve legacy workflows while the new foundation remains opt-in.
Apply the shared checklist and ready-to-run templates.

### Step 6 implementation

Files involved:

- `tests/unit/tools/release_workflow/acceptance_support.py` (new, to be created).
- `tests/unit/tools/release_workflow/conftest.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_support.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/console_support.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_release_acceptance/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_release_acceptance/test_release_acceptance_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_release_transport/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_release_transport/test_release_transport_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_release_locking/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_release_locking/test_release_locking_tdd.py` (new, to be created).
- `README.md` (existing, to be updated).
- `wiki/reference/aliases-and-launchers.md` (existing, to be updated).
- `wiki/reference/automation-and-direct-invocation.md` (existing, to be updated).

Tests first and acceptance behavior:

- Launch actual production bootstrap/launchers against temporary Git projects
  A and B, linked and nested worktrees, selected tooling copies and runtime
  identities. Use the session tooling copy and its manifest-verified generated
  handler/registry delta to prove read/mutation/results. Reuse the shared matrix
  fixtures and assert case results separately. Also prove the unmodified
  production launcher rejects those names; no public foundation command is added.
- Cover stale project/Git/Python/tooling environment, current-directory
  executable/module shadowing, selected alternate tooling checkout, setup
  record publication and readiness failures. Verify no changes to either
  consumer or tooling artifacts on failed/read-only calls, including ignored
  files and legacy scratch.
- Use real subprocesses for managed-write/junction revalidation, competing
  mutations, exact dead-owner recovery, retained handoff no-process gaps,
  unverifiable ownership and independent-project concurrency. Assert no
  multi-file snapshot guarantee for unlocked reads.
- Execute the complete Step 5 transport matrix using the real launcher,
  including relative payload location during build-directory changes,
  invalid UTF-8, redirected stdin, codepage/environment/cwd restoration,
  public 0/1/2, child status 7, non-ASCII streams and cancellation. For cmd
  console/doskey and Ctrl+C behavior use Step 5's `CreatePseudoConsole` harness
  and exact route outcomes. Record any host limitation as missing evidence to
  be resolved; Step 6 cannot complete with a supported caller unproved.
- Verify the missing-launcher caller contract in the disposable build fixture:
  ordinary intent warns and reads its local version, while release/snapshot
  anywhere in arguments fails. Detect missing tooling by launcher file absence
  before calling it; an installed launcher returning 1 or 2 must propagate
  failure and never take the fallback. Exercise those cases against the shipped
  launcher. The fixture's intent scan is a reference for items 5/8, not proof
  of their unimplemented production argument handling or integration.
- PBT is already owned by earlier steps; use deterministic multi-process
  acceptance for operating-system sequencing and cancellation.
- Put detailed alias/explicit-entry syntax and safe path/free-text channels in
  `wiki/reference/aliases-and-launchers.md`; put runtime repair requirements,
  PowerShell selector lifetime, native automation, statuses/streams and the
  foundation availability boundary in
  `wiki/reference/automation-and-direct-invocation.md`. Keep both reference-only;
  README receives a short pointer. Use generic examples and repository-relative
  references. Preserve category ordering: explanation, tutorials, how-to guides,
  reference, in any category links touched.

Acceptance ownership map:

| Acceptance | Foundation proof | Later owner boundary |
| --- | --- | --- |
| AC1–AC4 | Steps 2/5/6 roots, Git, linked/nested worktrees and managed writes | Domain-specific managed paths arrive with their owner |
| Project-name and legacy-location requirements | Steps 5/6 derive root/name and all six legacy location representations without exporting variables; stale inherited values change no result | Domain use remains items 2–4 |
| AC5 | Steps 1/5/6 setup producer, process scoping and disposable build caller | Real build/senv migration remains items 5/8 |
| AC6–AC7 | Steps 1/5/6 runtime, isolated imports and selected checkout | Full setup/upgrade lifecycle remains item 6 |
| AC8 | Steps 3/6 strict configuration and interim minimum-version failure | Version comparison remains item 6; schemas arrive with domains |
| AC9 | Steps 4/6 read-only artifacts, mutation service and lock | Domain transactions/cleanup remain their owners |
| AC10 | Steps 5/6 supported transport, interaction, streams/status and cancellation | Actual title acquisition/live build output and validated lifecycle handoff remain item 5 |
| AC11 | Step 6 reference adapter distinguishes launcher file absence from actual shipped-launcher failures | Production AC11 behavior remains unproven until item 5; consumer cutover remains item 8 |

Completion: focused acceptance passes on supported Windows x64 with real
filesystem/process/console evidence. Resolve `pw scope day` and, for final
whole-scope coverage proof, `pw scope day --full=cov`; run their printed
commands to the requested objectives. Do not substitute fixture success for
production migration claims. Inspect
`rg -n 'release_workflow|release_alias|project-root-env|input-file-env' README.md wiki/reference/aliases-and-launchers.md wiki/reference/automation-and-direct-invocation.md tools/release_workflow bin tests/unit/tools/release_workflow`.
Record evidence and line counts in validation, then use the normal
implementation-check/review/authorized commit workflow. This planning invocation
does not implement, commit or release the feature.

### Step 6 addendums

Line-budget checkpoint:

- [ ] New Python files: baseline 0, safe band, ceiling 650; advisory 200–400
  support and 300–500 per acceptance file, under 30 for initializer.
- [ ] README baseline 1126; non-Python, no Python line ceiling.
- [ ] Reference-page baselines 130 and 69; non-Python, no Python line ceiling.
- [ ] Reused fixture/support/console files: recount on Step 6 entry, ceiling
  650; keep reusable setup, operating-system support and assertions separate.
- [ ] Keep transport and locking acceptance separated as listed. Split further
  by caller family or ownership transition if a file would exceed 650.
  Any source correction follows its owning step's measured budget.

Full-workflow timing readiness: focused acceptance, resolved day objective and
final resolved coverage objective. Groundhog owns durations; investigate actual
outliers without weakening assertions. No timing xfails may mask acceptance.

## Planning risk pass and rollout order

The current tree supports the paths above. Implement runtime production before
the launcher consumes it; bootstrap must not depend on a future setup item.
Keep readiness imports separate from eager package imports. Validate actual
`switchpy` outcomes instead of reconstructing environment naming. Track
lockfile graph/marker completeness and reject unknown cases before dispatch.

Perform Git config-scope inspection before trusting root discovery, and keep
one executable across later cwd changes. Separate artifact parsing from
preparation, and make write-time checks and retained lock ownership explicit.
Include real Windows caller/cancellation evidence before approving transport;
scratch probe counts and mocked console APIs are insufficient.

Roll out the foundation and narrow runtime producer first. Keep legacy domain
commands operational until their owning items migrate them. The final evidence
must distinguish working foundation services, caller-contract fixtures and
deferred production integration. No private path or sensitive term is required
by any planned implementation or fixture.

## Plan writer assessment

| Review outcome | Basis |
| --- | --- |
| No open questions from the plan writer | Independent round 3 recommends convergence: all substantive findings are resolved, and the two covered reflow edits are applied. The requirement, design and six-step order are unchanged by the review revisions. The writer agrees that the plan is ready for the human consolidation choice; implementation and consolidation are not yet authorized by this review |
