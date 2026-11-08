# v0.14.0 version-sources implementation plan -- authoritative project versions

Add the version domain to the item 1 release engine: one anchor, registered
standard-library adapters, one recoverable transition and one shared tag range
selector, each delivered behind tests that start no process.

- **Foundation extensions**: operation tokens, public status 3, the version
  schema, a public lock ownership check and typed Git observations.
- **Source adapters**: the anchor, Python with uv, npm, Maven reactors and
  declared pattern sources, combined under one claim registry.
- **Transition and ranges**: the locked, evidence-backed `versions set`
  primitive, the stable tag classifier, the range selector and the
  release-version rule.

> Markdown lint note: never leave a space immediately inside an inline code span
> (MD038); when a snippet starts or ends with a space, write that space as the
> literal token `[space]`, as in `` `[space]${x}` ``. End any line that would be
> only italic text with a period after the closing `_` (MD036).

## Plan goal for v0.14.0 version-sources

Implement the approved [design](design.v0.14.0.version-sources.md) and
[requirement](feature-request.v0.14.0.version-sources.md), beside the
[focused draft](draft.v0.14.0.version-sources.md). This is item 2 of the
[sibling release tooling umbrella](draft.v0.14.0.sibling_release_tooling.md);
it builds on the item 1 foundation described in
[the item 1 plan](plan.v0.14.0.release-project-root.md).

- **Step 1 goal**: extend the item 1 foundation where the version domain needs
  it: operation tokens and argument validators, public status 3, the lock
  ownership check for lifecycle callers and typed Git observations.
- **Step 2 goal**: version tokens, forms, the read-only file view, the common
  source model and the `version.txt` anchor document.
- **Step 3 goal**: the version configuration schema, participating roots,
  pattern sources and the claim registry that combines every detector.
- **Step 4 goal**: the recoverable transition: locked planning, recovery
  evidence, ordered writes, verification, completion boundary, restoration and
  lifecycle reuse, with its restoration contract proven on the anchor and
  pattern sources.
- **Step 5 goal**: the Python and uv adapter with its TOML scanner, the
  recorded uv compatibility evidence that backs its registered lock schemas,
  and its restoration contract cases.
- **Step 6 goal**: the npm adapter with its JSON scanner, the recorded npm
  compatibility evidence for lock formats 2 and 3, and its restoration
  contract cases.
- **Step 7 goal**: the Maven reactor adapter, split into reactor discovery and
  reference rules, with its expat byte-offset scanner and its restoration
  contract cases.
- **Step 8 goal**: the stable and snapshot tag classifier, the range selector
  and the release-version rule.
- **Step 9 goal**: the shipped `version` and `versions` commands, the
  integrated acceptance matrix and the reference documentation.

No Step 0 is planned; see
[Performance-gate assessment for v0.14.0 version-sources](#performance-gate-assessment-for-v0140-version-sources).

---

## Scope anchors for v0.14.0 version-sources plan

This plan implements the design's five outcomes:

1. `version`, `versions list` and `versions check` run through item 1's
   dispatcher as read-only operations.
2. `versions set` is one locked, recoverable transition primitive, called by
   the CLI and reusable in process by item 5.
3. A registered adapter package covers the anchor, Python with uv, npm, Maven
   reactors and declared pattern sources.
4. The version domain of `.release.ini` declares form overrides, pattern
   sources and participating component roots.
5. One tag classifier and range selector, with persistent eligibility
   evidence, serves every release-range reader, with the read-only
   `versions range` command for instruction-driven readers.

The following are explicitly **in scope** for this plan:

- The foundation extensions of the design's "Foundation changes required by
  the version domain" table, with their item 1 test updates.
- `tools/release_workflow/sources/`, its explicit adapter tuple, the
  completeness test and per-adapter detection, read, expected-form, write and
  failure-restoration contract tests.
- Recorded tool compatibility evidence for every registered uv lock schema and
  npm lock format, checked by a test against the current adapter output.
- The in-process transition primitive, its restore handle for item 5 and the
  release-version rule function for items 5 and 7.
- Reference documentation for the shipped commands, statuses and
  configuration.

The following are explicitly **deferred** beyond this item:

- Release and next-snapshot commits, tags, the `Release tooling:` trailer
  writing, `[valid]` writing and lifecycle recovery (item 5); git-cliff range
  configuration (item 4); component setup (item 6); switching Step 12 and the
  range readers (item 7); llm-shared's own migration and retirement of
  `tools/dev_workflow` version scripts (item 8).
- npm and uv workspaces, Maven property forms beyond `${project.version}`,
  per-component versions and forms, lock regeneration, later formats and an
  automated recovery command for interrupted standalone evidence.

---

## Complexity Bound Clarification for v0.14.0

The scaling target for all v0.14.0 version-sources code paths is:

- **O(1) amortized per located field**: each claim is registered in a
  dictionary keyed by physical path and field; each Maven reference is resolved
  through a dictionary keyed by group and artifact identifiers; each tag name is
  classified once.
- **O(n) total per phase**: a phase reads each participating file once and
  scans its bytes once; detection is linear in participating roots, Maven
  modules and located fields; candidate filtering is linear in the one Git
  listing; the selector is linear in reachable tags, with ancestry decided by
  Git in a fixed number of calls.

The only sort is the per-file span list of the overlap check, bounded by the
handful of owned fields one file holds, and the deterministic write order over
participating files. No v0.14.0 code path may introduce a pairwise comparison
of all claims, of all tags or of all Maven modules. Any new path that breaks
this bound must be called out as a defect before merge.

---

## File-based IO cost clarification for v0.14.0 version-sources

| Path | Reads | Writes | Process starts |
| --- | --- | --- | --- |
| `version` | `version.txt` once; one non-recursive listing of the artifact home when it exists, for leftover evidence | none | none of its own |
| `versions check` | each participating source file once, through one file view; the same artifact-home listing | none | none of its own |
| `versions list` | as `check`, plus one Git listing and one read of each candidate manifest file | none | one Git call |
| `versions range` | the same artifact-home listing; no source file | none | at most four Git calls for one selection |
| `versions set` | one file view per phase: initial plan, locked plan, comparison before each replacement, final verification and, after a failure, the restoration check | evidence copies and manifest, then one atomic replacement per changed source, `version.txt` last | none of its own |

- Detection probes fixed file names at each participating root and the Maven
  modules declared from it; it never walks a directory tree. Only `list` asks
  Git for the tree, once.
- Every write goes through item 1's `managed_files` boundary: flushed
  same-parent temporary file, revalidation, atomic replacement.
- No version command starts uv, npm, Maven or git-cliff. The item 1 preflight
  (root validation, configuration, artifact declaration) and artifact
  preparation keep their own Git calls.
- Item 1's configuration loader still reads `.release.ini` once; the version
  validator works on the parsed mappings and reads no file.

---

## Confirmed technical facts for v0.14.0 plan viability

Inspection baseline: 2026-11-07, branch `version-sources` at `f053c2f`, before
implementation. The effort documents share `docs/v0.14.0/`; the two plans are
new. Counts use the gate metric
`sum(1 for _ in path.open(encoding="utf-8", errors="ignore"))`; the active
Python ceiling is 650 lines.

**Files over the 650-line repository limit** (must be split by responsibility):

- None among the files involved.

**Files in the 550-through-650 risk band** (avoid growth where practical):

- None among the files involved.

**Files below 550 and safe to extend** (current lines, expected additions):

| Existing file | Lines | Planned use |
| --- | --- | --- |
| `tools/release_workflow/cli.py` | 149 | Steps 1 and 9: operation tokens, validators, shipped handlers; advisory final 200 |
| `tools/release_workflow/invocation.py` | 192 | Step 1: carry operation tokens; advisory final 200 |
| `tools/release_workflow/results.py` | 51 | Step 1: public status 3; advisory final 55 |
| `tools/release_workflow/bootstrap.py` | 199 | Step 1: public status 3; advisory final 200 |
| `tools/release_workflow/operation_lock.py` | 233 | Step 1: public ownership check; advisory final 270 |
| `tools/release_workflow/git.py` | 185 | Step 1: typed observations; advisory final 290 |
| `tools/release_workflow/schemas.py` | 196 | Step 3: version schema; advisory final 220 |
| `tools/release_workflow/configuration.py` | 160 | Reference, unchanged |
| `tools/release_workflow/managed_files.py` | 137 | Reference, unchanged |
| `tools/release_workflow/artifacts.py` | 128 | Reference, unchanged |
| `tests/unit/tools/release_workflow/repository_simulation.py` | 148 | Step 1: declared release history; advisory final 260 |
| `tests/unit/tools/release_workflow/launcher_simulation.py` | 179 | Step 1: route the typed observations; advisory final 200 |
| `tests/unit/tools/release_workflow/conftest.py` | 132 | Reference, unchanged |
| `tests/unit/tools/release_workflow/test_cli/test_cli_tdd.py` | 123 | Step 1: token cases; advisory final 200 |
| `tests/unit/tools/release_workflow/test_invocation/test_invocation_tdd.py` | 177 | Step 1: tokens reach the context; advisory final 190 |
| `tests/unit/tools/release_workflow/test_results/test_results_tdd.py` | 40 | Step 1: status 3; advisory final 45 |
| `tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py` | 189 | Step 1: status 3; advisory final 195 |
| `tests/unit/tools/release_workflow/test_launchers/test_codepage_tdd.py` | 109 | Step 1: launcher source contract; advisory final 110 |
| `tests/unit/tools/release_workflow/test_release_transport/test_release_transport_tdd.py` | 104 | Step 1: status 3 transport case; advisory final 115 |
| `tests/unit/tools/release_workflow/test_operation_lock/test_operation_lock_tdd.py` | 285 | Step 1: ownership check; advisory final 350 |
| `tests/unit/tools/release_workflow/test_schemas/test_schemas_tdd.py` | 90 | Step 3: shipped tuple; advisory final 100 |
| `tests/unit/tools/release_workflow/test_release_acceptance/test_release_acceptance_tdd.py` | 206 | Step 9: shipped registry names; advisory final 210 |

Non-Python files involved, without the Python ceiling:

| Existing file | Lines | Planned use |
| --- | --- | --- |
| `bin/release_workflow.bat` | 78 | Step 1: pass status 3 |
| `bin/release_alias.bat` | 78 | Step 1: pass status 3 |
| `wiki/reference/automation-and-direct-invocation.md` | 177 | Step 9: availability boundary and status 3 |
| `wiki/reference/aliases-and-launchers.md` | 178 | Step 9: shipped operations |
| `wiki/README.md` | 267 | Step 9: link the new reference page |

**What does not exist yet (all new for v0.14.0 version-sources)**:

- `tools/release_workflow/sources/` and every module in it.
- `tools/release_workflow/version_evidence.py`,
  `tools/release_workflow/version_transition.py`,
  `tools/release_workflow/tags.py` and `tools/release_workflow/versions.py`.
- `tests/unit/tools/release_workflow/version_support.py`,
  `tests/unit/tools/release_workflow/lock_evidence_recorder.py` and every
  `test_version_*`, `test_*_sources` and `test_release_tags` test leaf.
- `wiki/reference/version-sources.md`.
- No `.release.ini` exists in this checkout.

**Other confirmed technical facts that affect plan shape**:

- **Standard library only**: `[dependency-groups] release = []`. `tomllib`,
  `json` and `xml.parsers.expat` give meaning and offsets; no release
  dependency is added. `tomllib` and `json.loads` reject a byte-order mark, so
  adapters decode with strict UTF-8, strip the mark for parsing and keep its
  length as a byte offset. Python 3.13 provides `PurePath.full_match` for
  workspace member patterns, so no filesystem glob is needed.
- **Schema import cycle**: `schemas.py` imports no domain code, and a version
  module that defines its schema must import `schemas.py`. The version schema's
  sections are therefore declared in `schemas.py`, and its validator is a
  small function there that imports `tools.release_workflow.sources.settings`
  when it runs, the deferred-import idiom `cli.py` and `artifacts.py` already
  use (`# noqa: PLC0415`).
- **Handler failures**: `cli._dispatch` turns any exception into status 1.
  Version handlers therefore convert their own preflight errors (status 2),
  lock contention (status 1) and transition outcomes (0, 1 or 3) into an
  `OperationResult` themselves.
- **Argument order**: the design's example `versions --project-root <root> set
  0.14.0` places options before the tokens; the parser uses
  `parse_intermixed_args` so options and tokens may interleave.
- **Status normalization sites**: a site here is one place in llm-shared's
  own code that holds the list of exit statuses passed through unchanged
  (today 0, 1 and 2; anything else becomes 1). There are four:
  `results.render`, `bootstrap.main` (which
  cannot import `results` before readiness) and both batch launchers each keep
  their own `0`, `1`, `2` list; all four change, with their source-contract
  tests.
- **Lock probe seam**: `OperationLock` binds its probe default at definition
  time, so the transition passes its explicit process-probe input to the
  chosen lock factory; tests supply declared process states through that seam.
  Existing foundation identity fixtures, such as `lock_facts`, may still
  replace `current_identity`.
- **Git adapter tests**: `test_git_tdd.py` checks typed methods by replacing
  `GitExecutionContext.run` with canned output; the new typed observations use
  the same pattern. Tag targets use full `refs/tags/<name>` revisions so a
  branch of the same name never shadows a tag.
- **Test boundary**: `tests/unit/tools/release_workflow/` runs on the memory
  scratch filesystem of `tests/memory_filesystem.py`, under the process audit
  of `tests/simulation_policy.py` and the 0.1-second CPU lifecycle limit of
  `pyproject.toml` (band factor 2.5 for proven tests). Coverage measures
  `tools` at 100% and omits `__init__.py` files and `tests`.
- **Existing evidence conventions**: the test tree holds no data fixture
  directory; item 1 kept its host probe outside pytest. The lock evidence is
  therefore one committed JSON data file read once by its test, produced by a
  recorder module started by hand.

### Lock compatibility facts from the planning probe

Terms used throughout this plan for the lock evidence: the "before" pair is a
manifest and its lock file as a project has them before `versions set` changes
the version, for example a `pyproject.toml` and its `uv.lock` both at
`0.13.0`. The edited pair is the same two files after the adapter's
version-only edit, both at `0.14.0` with every other byte unchanged. A tool
"accepts" a pair when its locked or frozen command (such as
`uv lock --locked --offline`) exits 0 and changes neither file. Each record
shows the tool accepting the "before" pair, then the edited pair; the first
acceptance proves the starting pair was valid, so the second proves the edit
kept it valid. The manifest-only control edits only the manifest, leaving the
lock at the old version, to check that the tool notices a missed lock field.

A planning probe on 2026-11-07, in a scratch directory outside the
repository, confirmed that the evidence the design prescribes can be produced
on this host. It is feasibility evidence for this plan, not the recorded
evidence of Steps 5 and 6.

| Tool and version | Lock schema | Layout | Frozen command | Observed |
| --- | --- | --- | --- | --- |
| uv 0.13.4 (x86_64-pc-windows-msvc), in this checkout's venv | `version = 1`, `revision = 5` (written by `uv lock --offline`) | virtual root (`[tool.uv] package = false`, `source = { virtual = "." }`) and editable root (hatchling `[build-system]`, `source = { editable = "." }`) | `uv lock --locked --offline --no-config --python <project interpreter>` | before pair and version-only edited pair: exit 0, both files unchanged; manifest-only edit: exit 1, "needs to be updated" |
| uv 0.13.4 | `version = 1`, `revision = 3` (same lock with the revision line set to 3; llm-shared's own `uv.lock` uses this pair) | virtual and editable roots | same | same outcomes |
| npm 10.8.3 on Node 22.9.0 (the host's Node 22 installation) | `lockfileVersion` 3, and 2 through `--lockfile-version 2` | root package, `private: true`, no dependencies | `npm ci --offline --ignore-scripts --no-audit --no-fund` | before and edited pairs: exit 0, both files unchanged; manifest-only edit also exit 0 |

uv 0.13.4 writes revision 5 for a fresh lock and accepts revision 3 locks
unchanged; both consumer revisions come from that uv version. npm's frozen
install does not compare the root version, so `npm ci` alone proves that the
tool still accepts the edited pair, not that it would detect a missed field.
Node 10 and 14 installations (npm 6) exist on the host but are not used: lock
format 1 is rejected.

A second npm probe the same day ran `npm install --package-lock-only --offline
--ignore-scripts --no-audit --no-fund` on the probe projects. On a consistent
pair it left `package-lock.json` unchanged; on the manifest-only control it
rewrote the lock with the new root version and kept its format (2 or 3). Per
plan decision Q05, the npm records therefore keep `npm ci` as the frozen-mode run
and add this lock-only check on the "before" pair, the edited pair and the
control. The adapter tests still carry the field-level proof.

---

## Current test-tree validation snapshot for v0.14.0 version-sources

Existing test packages that v0.14.0 version-sources must not break:

- `tests/unit/tools/release_workflow/` (71 tracked files): item 1's foundation
  suites. The schema, CLI, results, bootstrap, launcher-source, transport,
  operation-lock, invocation and acceptance leaves change as listed per step;
  every other leaf stays unchanged.
- `tests/acceptance/release_workflow/` (readiness acceptance): unchanged, since
  the release dependency group stays empty.
- `tests/unit/tools/prepare_release/` and `tools/dev_workflow`: unchanged;
  item 7 and item 8 switch them later.

New test leaf directories to create for v0.14.0 version-sources (each with an
`__init__.py` holding a one-line docstring and `# eof`):

- `tests/unit/tools/release_workflow/test_version_model/` (Step 2).
- `tests/unit/tools/release_workflow/test_version_anchor/` (Step 2).
- `tests/unit/tools/release_workflow/test_version_registry/` (Step 2).
- `tests/unit/tools/release_workflow/test_version_settings/` (Step 3).
- `tests/unit/tools/release_workflow/test_pattern_sources/` (Step 3).
- `tests/unit/tools/release_workflow/test_version_detection/` (Step 3).
- `tests/unit/tools/release_workflow/test_version_formats/` (Steps 5 to 7).
- `tests/unit/tools/release_workflow/test_python_sources/` (Step 5).
- `tests/unit/tools/release_workflow/test_version_lock_evidence/` (Steps 5 and 6).
- `tests/unit/tools/release_workflow/test_npm_sources/` (Step 6).
- `tests/unit/tools/release_workflow/test_maven_sources/` (Step 7).
- `tests/unit/tools/release_workflow/test_version_evidence/` (Step 4).
- `tests/unit/tools/release_workflow/test_version_transition/` (Step 4).
- `tests/unit/tools/release_workflow/test_release_tags/` (Step 8).
- `tests/unit/tools/release_workflow/test_version_commands/` (Step 9).
- `tests/unit/tools/release_workflow/test_version_acceptance/` (Step 9).

---

## Runtime file note for v0.14.0 version-sources plan

- `<artifact home>/a.release-operation.lock`: item 1's lock record, written
  only by `versions set` after its side-effect-free plan; the artifact home's
  `.gitignore` (`*`) already covers it.
- `<artifact home>/a.version-transition.<YYYYMMDDTHHMMSS+HHMM>-<pid>/`: the
  per-transition evidence directory, holding `original.<n>` copies and
  `manifest.json` (local time with offset; no `:` in the directory name). It
  is created exclusively; a name already taken gets a `-2`, `-3` and so on
  suffix, and an existing directory is never reused (Step 4).
  Covered by the same `.gitignore`; a standalone success deletes it.
- `tests/unit/tools/release_workflow/test_version_lock_evidence/lock_evidence.v1.json`:
  committed evidence data, not runtime output. It holds generic project names,
  argument lists with `<uv>`, `<npm>` and `<python>` placeholders, and no
  absolute path, user name or host name.
- The recorder's scratch projects live in a temporary directory outside the
  repository and are deleted when it ends.

---

## Shared execution command checklist for all v0.14.0 version-sources steps

Apply this checklist for every numbered step, filling in the step-specific
paths.

1. Start or resume the step journal with `pw step-journal <x>`; record the
   baseline line count of every file listed by the step, package initializers
   included.
2. Write the step's tests first and confirm through groundhog that they fail
   at the intended boundary; then implement that boundary.
3. Run the step's targeted tests through groundhog, with the named existing
   regressions.
4. Run the step's `rg` checks and read every match; a match is a lead, not
   automatically a fault.
5. Resolve and run the command printed by `pw scope day`; follow its printed
   repair and restart lines until it reports the requested objective
   (`exit=0`). Never freeze a selector.
6. Count lines after the edits and compare them with the step's line-budget
   checkpoint. A Python file above 650 lines stops the step until the split
   guidance is applied; an advisory estimate exceeded at or below 650 is
   recorded as variance, not missing work.
7. Record evidence and counts in the matching step of the
   [validation plan](plan.v0.14.0.version-sources.validation.md), with
   repository-relative paths only, then follow the normal implementation-check,
   review and authorized commit workflow.

---

## Ready-to-run command templates for all v0.14.0 version-sources steps

Follow [run-pw](../../instructions/run-pw.md),
[command execution](../../rules/run_commands.md) and
[groundhog](../../instructions/groundhog.md). Resolve `<LLM_SHARED_DIR>` from
the location of the canonical instruction; it is documentation notation, not an
environment variable.

- Line count before and after: the gate metric above with the project
  interpreter, or `[System.IO.File]::ReadAllLines($path).Count` in PowerShell
  for these UTF-8 files.
- Targeted tests: `& "<LLM_SHARED_DIR>\bin\ghog.bat" single <step test files>`
  (groundhog runs the tests; never a direct `pytest`).
- Grep checks: `rg -n '<step pattern>' tools/release_workflow tests/unit/tools/release_workflow`.
- Ready-to-run command and shared gate loop: run
  `& "<LLM_SHARED_DIR>\bin\prompt_workflow.bat" scope day` and execute the
  printed `ghog` command through the resolved `ghog.bat` launcher (on
  2026-11-07 it printed `ghog day --whole-suite`; resolve it again at execution
  time). Follow its repair and restart lines until `exit=0`. The default level
  runs `check.bat` plus affected tests and deliberately skips full.
- Final coverage proof (Step 9): `scope day --full=cov`, executed the same way.
- Recorder (Steps 5 and 6, outside pytest, from the project root):
  `& .\venvs\<project venv>\Scripts\python.exe -m tests.unit.tools.release_workflow.lock_evidence_recorder --uv <uv.exe> --python <project python.exe> --npm <npm.cmd> --node-dir <node 22 directory> --output tests\unit\tools\release_workflow\test_version_lock_evidence\lock_evidence.v1.json`.

No step schedules a direct `pytest` or `check.bat` call.

---

## Performance-gate assessment for v0.14.0 version-sources

No Step 0 timeout gate or `xfail` is warranted. The design sets operation
counts, not wall-clock targets: one read per file per phase, one Git listing
for `list`, at most four Git calls for one range selection, two for the
release-version rule and no process of their own for `version`, `check` and
`set`. Each owning step asserts those counts deterministically (a counting
file view, a recording Git observation), which is exact and repeatable where a
timing gate is not. Groundhog's lifecycle gate (0.1-second CPU, one-second
wall, setup and teardown included) applies to every new test, with no
duration exclusion.

---

## Shared test architecture for v0.14.0 version-sources

- **Where these tests run**: every test in this plan belongs to llm-shared's
  own development suite. Groundhog runs it while llm-shared is changed
  (`ghog single` for a step, the `pw scope day` gate for the whole suite). No
  version command, no `brel` and no consumer release runs it; a consumer's own
  release-time tests belong to umbrella item 5.
- **Simulation only**: no test starts Git, uv, npm, Maven, a shell or a child
  interpreter. Production parsers, detection, planning, the transition, the
  selector and rendering run in process. Git facts come from
  `RepositoryObservations`; the release history is declared data (commits with
  parents, tags with object type and annotation) from which the typed
  observations are answered, without interpreting Git arguments.
- **Shared builders**: `tests/unit/tools/release_workflow/version_support.py`
  (created in Step 2, extended by Steps 3 to 9) writes small byte templates for each
  ecosystem file (LF and CRLF variants, optional byte-order mark), builds a
  `VersionInputs` value from a `git_sandbox` project, and declares evidence
  directories and lock records as prerequisites instead of replaying a killed
  process.
- **One transition per test**: each test declares its prior state directly
  (files, evidence, lock record) and asserts one transition. The end-to-end
  journey keeps one test per command contract in Step 9.
- **Read and call counts**: `FileView` exposes the number of loads per path;
  the recording Git observation exposes its calls. Tests assert the design's
  bounds with them.
- **Property tests**: used where the input domain is large and the function
  pure (token grammar, span composition, scanners, CRLF mapping, annotation
  classification, linear histories). Strategies draw from cheap encodings
  (integer triples, short ASCII line lists) so each property stays inside the
  lifecycle budget without lowering its example budget. Finite domains, such as
  the failure position among N writes, use exhaustive parametrization instead.
- **Fault injection**: the transition takes one `TransitionPorts` value
  (plan decision Q07) carrying its replacement function (default
  `managed_files.replace_bytes`), file and directory removal, lock factory,
  process probe, clock and process id, each with its production default; tests
  inject a failure at a chosen write, removal, release or restoration index and
  fix the evidence name. No module-global patch replaces a production default
  silently.
- **Restoration contract per adapter** (plan decision Q01): Step 4 proves the
  transition's restoration on the anchor and pattern fixture sets; Steps 5, 6
  and 7 each add their own adapter's fixture set to the same exhaustive
  failure-position matrix, so every adapter step completes its AC3 contract
  set (detection, read, expected form, write and failure restoration).

---

## Numbered steps for v0.14.0 version-sources

### Step 1. Foundation extensions for the version domain

#### Step 1 -- analysis and intent for the foundation extensions

Issues to address:

- The item 1 parser rejects every token after the command, so `versions set
  0.14.0` cannot reach a handler.
- Four sites normalize every status other than 0, 1 and 2 to 1, so an
  incomplete restoration cannot be reported distinctly.
- `OperationLock` keeps its ownership check private, so item 5 cannot hand its
  held lock to the transition with a verifiable binding to this project.
- `GitExecutionContext` has no tag, ancestry, count or listing observation.

Fix intent:

- Collect trailing operation tokens, add a per-handler argument validator that
  runs right after parsing, and carry the tokens into the invocation context.
- Accept public status 3 at the renderer, the bootstrap and both launchers,
  still normalizing any other value to 1 with a diagnostic.
- Add a public `verify_held` check bound to the current process, the physical
  project root and the managed artifact home.
- Add typed Git observations and their programmatic counterparts in the
  repository and launcher simulations.

Expected outcome:

- A handler without a validator still rejects any extra token with status 2;
  a validator failure returns status 2 before any Git process or file read.
- Status 3 passes through every public boundary unchanged; status 4 and 23
  still become 1 with the original value in a diagnostic.
- `SHIPPED_HANDLERS` stays empty until Step 9.

Step framing:

- Design link: "Foundation changes required by the version domain",
  "Commands and their arguments", "Public statuses of the version commands",
  "Reuse by a lifecycle caller", "Git queries of the selector", "Undeclared
  nested candidates"; design decisions Q04, Q07, Q15.
- Execution checklist reference: [Shared execution command checklist for all
  v0.14.0 version-sources steps](#shared-execution-command-checklist-for-all-v0140-version-sources-steps).

#### Step 1 -- implementation for the foundation extensions

**Files involved**:

- `tools/release_workflow/cli.py` (existing, to be updated).
- `tools/release_workflow/invocation.py` (existing, to be updated).
- `tools/release_workflow/results.py` (existing, to be updated).
- `tools/release_workflow/bootstrap.py` (existing, to be updated).
- `bin/release_workflow.bat` (existing, to be updated).
- `bin/release_alias.bat` (existing, to be updated).
- `tools/release_workflow/operation_lock.py` (existing, to be updated).
- `tools/release_workflow/git.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/repository_simulation.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/launcher_simulation.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_cli/test_cli_tdd.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_invocation/test_invocation_tdd.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_results/test_results_tdd.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_launchers/test_codepage_tdd.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_release_transport/test_release_transport_tdd.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_operation_lock/test_operation_lock_tdd.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_git/test_git_releases_tdd.py` (new, to be created).

**Tests first**:

- CLI: a test registry with a validator receives `("set", "0.14.0")`; options
  before, between and after tokens parse the same; a handler without a
  validator rejects `extra` with status 2; a validator error returns status 2
  while a replaced `GitExecutionContext.create` and `RuntimeIdentity.load`
  record no call; the unavailable-operation message is unchanged.
- Invocation: `create_context` copies `InvocationRequest.operation` into
  `InvocationContext.operation`; the batch-character rule still rejects a
  token holding `%`, `^`, `!` or `"`.
- Results and bootstrap: parametrize 0, 1, 2 and 3 as pass-through, 4 and 23
  as normalized to 1 with the original value in the diagnostic.
- Launchers: extend the source-contract block of `test_codepage_tdd.py` with
  the `"3"` line for both launchers. Transport: a test handler returning 3 with
  a diagnostic passes through `launcher_tooling.run` with status 3.
- Status consistency (plan decision Q12): one test in `test_codepage_tdd.py`
  compares the statuses accepted by the four sites (`results.render`,
  `bootstrap.main` and both launchers, read through the existing
  source-contract mechanism) and requires the same set, `{0, 1, 2, 3}`; it
  compares accepted values, not one textual spelling. Like every test of this
  plan, it runs only in llm-shared's development suite.
- Lock: `verify_held` returns the prepared artifacts for the current holder;
  it fails for a released handle, a handle taken for another project root, a
  declaration whose home differs, a record replaced by another owner, a
  retained (handed-off) record and an owner whose process identity is not the
  current one.
- Git: each typed method's exact argument vector and parsing from canned
  `run` output: zero, one and several tag records, an annotation with blank
  lines and trailing newline, a lightweight tag, merged and not-merged filters,
  independent tips, a count, a listing with an embedded repository entry
  (`nested/`) dropped and a tracked gitlink kept as a name; a nonzero Git
  status keeps raising `GitCommandError`, except the canned exit 129 with
  `malformed object name refs/tags/<name>` for `--merged`, which raises
  `GitRevisionNotFound`; an exit 129 with other stderr stays a
  `GitCommandError`.
- Command-line guard (plan decision Q13): `independent_commits` refuses, before
  any process start, a candidate list whose serialized command line would
  exceed 32,767 UTF-16 code units including the terminating NUL; boundary
  cases just below, at and just above the limit, each with 40- and
  64-character object ids and a long executable path, assert the refusal
  (`GitCommandLineTooLong`, status 1, naming the limit and the candidate
  count) and that the recording `run` saw no call.
- PBT: not needed in this step; the token and status domains are finite and
  parametrized exhaustively.

**Classes and behavior**:

- `cli._parse`: add `parser.add_argument("operation", nargs="*")` and use
  `parse_intermixed_args`; return the tokens as a tuple.
- `cli.Handler`: add `validate_arguments: Callable[[tuple[str, ...]], None] |
  None = None`. `_select` calls it with the tokens, or raises
  `ValueError("Release operation '<name>' takes no arguments: ...")` when it
  is `None` and tokens exist. Both run before identity loading and context
  creation.
- `invocation.InvocationRequest` and `InvocationContext`: add a trailing
  `operation: tuple[str, ...] = ()` field; `create_context` passes it through.
- `results.render` and `bootstrap.main`: public statuses `{0, 1, 2, 3}`; the
  module docstrings record the change. Both launchers add
  `if "%_release_status%"=="3" goto cleanup` before the normalization line.
- `OperationLock.verify_held(declaration: ArtifactDeclaration) ->
  PreparedArtifacts`: compare the held owner's process with
  `current_identity()`, the physical project root and the lock target derived
  from `declaration.home` with this handle's own, then call `_require_owned()`
  inside `_transition()`. Acquisition, release, retention and transfer stay
  unchanged.
- `git.TagRecord` (frozen): `name`, `object_type`, `commit` (peeled),
  `annotation: str | None` (`None` for a lightweight tag).
- `GitExecutionContext.tag_records(*, cwd, merged=None)`: one
  `for-each-ref` over `refs/tags` with NUL-separated fixed fields
  (`%(refname:strip=2)`, `%(objecttype)`, `%(objectname)`,
  `%(*objectname)`, `%(contents)`) and an optional `--merged=<revision>`.
  When that single call exits 129 and its stderr reports `malformed object
  name` for the supplied `--merged` revision, it raises
  `GitRevisionNotFound` (a `GitCommandError` subclass carrying the revision),
  so a missing tag target becomes status 2 in Step 8 without a second query;
  every other failure stays a plain `GitCommandError` (status 1).
- `GitExecutionContext.independent_commits(commits, *, cwd)`: one
  `merge-base --independent`. Before starting it, the method builds the exact
  command line the call would use (`subprocess.list2cmdline` over the selected
  executable, the fixed `run` prefix options and the arguments), measures it in
  UTF-16 code units including the terminating NUL, and raises
  `GitCommandLineTooLong` (execution failure, status 1) above 32,767, naming
  the limit and the candidate count (plan decision Q13). The four-call ceiling of a
  selection stays.
- `GitExecutionContext.tag_names(*, cwd, merged, not_merged)`: one
  `for-each-ref --merged=<target> --no-merged=<baseline>` over `refs/tags`.
- `GitExecutionContext.commit_count(revision_range, *, cwd)`: one
  `rev-list --count`.
- `GitExecutionContext.listing(*, cwd)`: one `ls-files -z --cached --others
  --exclude-standard`, dropping entries that end with `/`.
- `repository_simulation.ReleaseHistory`: declared commits with parents,
  `HEAD`, `main`, tags (`TagRecord` data) and listing names;
  `RepositoryObservations` answers the five methods from it by reachability
  over the declared parents and records each call. `launcher_simulation._patch_git`
  routes the five methods to the sandbox's observations.

**Completion criteria**:

- The command printed by `pw scope day` reports the objective (`exit=0`) in
  the current effort scope.
- `rg -n '"3"' bin/release_workflow.bat bin/release_alias.bat` shows the new
  pass-through line in both launchers;
  `rg -n '0, 1, 2, 3' tools/release_workflow/results.py tools/release_workflow/bootstrap.py`
  shows both public lists.
- The cross-site status test passes and fails when one site's list is changed
  in a synthetic copy (plan decision Q12).
- `rg -n 'subprocess|Popen' tests/unit/tools/release_workflow/repository_simulation.py`
  finds no process start.
- `cli.SHIPPED_HANDLERS` is still empty.

#### Step 1 -- addendums for the foundation extensions

Line-budget checkpoint:

- [ ] `tools/release_workflow/cli.py`: before 149; below-550 safe; repository ceiling <= 650; expected +35 (advisory).
- [ ] `tools/release_workflow/invocation.py`: before 192; below-550 safe; ceiling <= 650; expected +5 (advisory).
- [ ] `tools/release_workflow/results.py`: before 51; below-550 safe; ceiling <= 650; expected +2 (advisory).
- [ ] `tools/release_workflow/bootstrap.py`: before 199; below-550 safe; ceiling <= 650; expected +1 (advisory).
- [ ] `tools/release_workflow/operation_lock.py`: before 233; below-550 safe; ceiling <= 650; expected +35 (advisory).
- [ ] `tools/release_workflow/git.py`: before 185; below-550 safe; ceiling <= 650; expected +125 with the command-line guard (advisory).
- [ ] `tests/unit/tools/release_workflow/repository_simulation.py`: before 148; below-550 safe; ceiling <= 650; expected +110 (advisory).
- [ ] `tests/unit/tools/release_workflow/launcher_simulation.py`: before 179; below-550 safe; ceiling <= 650; expected +20 (advisory).
- [ ] Updated test files: before 123, 177, 40, 189, 109, 104 and 285; below-550 safe; ceiling <= 650; expected +80, +12, +5, +6, +25 (with the cross-site status test), +10 and +65 (advisory).
- [ ] `tests/unit/tools/release_workflow/test_git/test_git_releases_tdd.py`: before 0; ceiling <= 650; expected 260 with the guard's boundary cases (advisory).
- [ ] Both launchers: 78 lines each; non-Python, no Python ceiling.

Split guidance:

- If `git.py` would pass 650, move `TagRecord` and the five typed observations
  into `tools/release_workflow/git_releases.py` as functions taking the
  context, keeping `_execute` the only process boundary.
- If `repository_simulation.py` would pass 650, move `ReleaseHistory` into
  `tests/unit/tools/release_workflow/release_history.py`.

Full workflow timing run readiness:

- `ghog single` on the Step 1 test files, then the command printed by `pw scope day`.

Time-gated status for Step 1:

- No perf gate is affected; the lifecycle gate applies to the new tests.

---

### Step 2. Version tokens, the anchor document and the source model

#### Step 2 -- analysis and intent for tokens, anchor and model

Issues to address:

- No shared token grammar, form mapping or numeric comparison exists for the
  anchor, the `set` argument, configuration and source values.
- No representation exists for a located field, its byte spans, its form or
  the read-once file view the design requires.

Fix intent:

- One `VersionToken` parser and comparison, one `Form` enumeration with its
  expected-value rule and the release-only guard.
- A `FileView` that loads each path at most once per phase and counts loads.
- The located-source, visible-record, adapter protocol and edit-composition
  types every adapter shares.
- The `version.txt` document parser and the `anchor` adapter, registered as the
  first entry of the adapter tuple, with the completeness test.

Expected outcome:

- `0.10.0` compares above `0.9.0`; `v0.14.0`, `0.14.0-snapshot` and
  `0.014.0` are rejected with a remedy.
- Replacing the anchor token keeps the title, notes, byte-order mark and every
  line ending byte for byte.
- An adapter module missing from the tuple, or listed twice, fails the
  completeness test.

Step framing:

- Design link: "Version token grammar and comparison", "The version.txt
  document", "Forms by adapter", "The release-only guard", "The explicit
  adapter tuple", "What an adapter provides"; design decision Q16; AC1, AC2, AC3, AC7.
- Execution checklist reference: [Shared execution command checklist for all
  v0.14.0 version-sources steps](#shared-execution-command-checklist-for-all-v0140-version-sources-steps).

#### Step 2 -- implementation for tokens, anchor and model

**Files involved**:

- `tools/release_workflow/sources/__init__.py` (new, to be created).
- `tools/release_workflow/sources/model.py` (new, to be created).
- `tools/release_workflow/sources/anchor.py` (new, to be created).
- `tests/unit/tools/release_workflow/version_support.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_version_model/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_version_model/test_version_model_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_version_model/test_version_model_pbt.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_version_anchor/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_version_anchor/test_version_anchor_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_version_anchor/test_version_anchor_pbt.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_version_registry/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_version_registry/test_version_registry_tdd.py` (new, to be created).

**Tests first**:

- Tokens: accepted `0.0.0`, `0.14.0`, `10.0.0-SNAPSHOT`; rejected `v0.14.0`,
  `0.14.0-snapshot`, `0.014.0`, `01.0.0`, `1.0`, `1.0.0.0`, empty and padded
  text, each with a remedy naming the expected grammar; numeric ordering of
  cores; the suffix ignored by the ordering.
- Forms: `snapshot`, `core` and `release-only` expected values for a release
  and a snapshot anchor; the release-only guard refuses a current core above
  the expected core and names source, value and target; a malformed current
  value fails as malformed.
- `FileView`: one load per path, absence recorded as `None`, a fresh view
  loads again, strict UTF-8 failure names the path.
- Composition: several disjoint spans in one original produce one content;
  a span outside the content or two overlapping spans raise.
- Offsets: `to_byte_spans` maps character spans to byte spans for fixed
  texts holding accented letters and a non-BMP character (such as U+1F600)
  before and between several owned fields, with and without a byte-order
  mark; composing replacements at the mapped spans keeps every other byte;
  the mapping encodes each text segment once (asserted by counting encoded
  characters against the text length).
- Shared types: `VersionInputs.from_context` copies project, configuration,
  artifacts and Git from an `InvocationContext`; `FileCapture` records absence
  as `None` bytes and the SHA-256 of present bytes; `FileEdit` rejects new
  bytes equal to the original.
- Anchor: `0.14.0`, `0.14.0 -- Title`, `0.14.0   --   Title` and an empty
  title; `0.14.0 Title` and `0.14.0 -SNAPSHOT` malformed; missing file,
  invalid UTF-8 and malformed first line fail with status 2 and a remedy and
  create nothing; notes after the first line are returned unchanged; LF, CRLF
  and byte-order-mark documents keep every byte except the token.
- Registry: the modules of `tools/release_workflow/sources/`, minus a declared
  set of support modules, each contribute exactly one entry to `ADAPTERS`; a
  synthetic package listing with an extra or a duplicated adapter fails; the
  current order is `("anchor",)`.
- PBT (needed): token round trip over integer triples with and without the
  suffix, ordering equal to tuple ordering; composition of random disjoint
  spans equals right-to-left sequential replacement; anchor replacement over
  generated titles, notes and line endings changes only the token bytes.

**Classes and behavior**:

- `model.VersionToken`: `parse(text) -> VersionToken`, `core`, `snapshot`,
  `key` (integer triple), `__str__`; `VersionError(ValueError)` with
  `exit_code = 2`.
- `model.Form`: `SNAPSHOT`, `CORE`, `RELEASE_ONLY` with `parse(text)` and
  `expected(anchor) -> str`; `check_release_only(source, anchor)`.
- `model.Span`, `model.LocatedSource` (path, field, adapter, form, value,
  spans, root, paired manifest), `model.VisibleRecord` (path, field, adapter,
  status `not-participating tool-only` or `not-participating undeclared`),
  `model.Detection` (sources and visible records), `model.SourceError(ValueError)`
  with `exit_code = 2`.
- `model.FileView`: `read(path) -> bytes | None`, `text(path) -> (str, bom)`
  with strict UTF-8, `loads` counter per path.
- `model.Adapter` protocol: `name`, `default_form`, `forms`,
  `detect(root, view, settings) -> Detection`, `render(source, value) -> bytes`,
  `manifest_names` and `has_project_version(name, content) -> bool` for
  candidates.
- `model.compose(original, edits) -> bytes`: sort the file's spans, reject
  out-of-bounds and overlapping spans, build the new content from the one
  original.
- `model.to_byte_spans(text, bom_length, spans) -> tuple[Span, ...]`: the
  one character-to-byte mapping used by the TOML scanner, the JSON scanner and
  pattern sources. It sorts the requested character offsets and walks the text
  once, encoding each segment between consecutive offsets exactly once, so the
  cost is linear in the text and independent of the number of fields; the
  pattern adapter first maps its LF-view offsets back to original character
  offsets in the same walk. Expat already reports byte indexes and does not
  use it.
- Shared types for every later step (plan decision Q16): `VersionInputs`
  (project, configuration, artifacts, Git) with `from_context(context)`, the
  context type imported for type checking only; `FileCapture` (path, original
  bytes or `None` when absent, SHA-256); `SourceChange` (path, field, adapter,
  old value, new value); `FileEdit` (capture, new bytes, changes);
  `Inventory` (located sources, visible records, claims, captures) and `Plan`
  (target, inventory, edits). `model.py` imports only the standard library,
  `sources` modules and foundation types; no Step 2 or Step 3 module imports a
  later transition module.
- `anchor.VersionDocument` (token, title, notes, token span, byte-order mark)
  and `anchor.parse_document(content)`; `anchor.ADAPTER` locates
  `version.txt` at the project root only and renders the raw token.
- `sources/__init__.py`: `ADAPTERS = (anchor.ADAPTER,)` in detection order;
  later steps insert `python`, `npm` and `maven` before `pattern`, which
  Step 3 appends.
- `version_support.py`: byte builders for `version.txt` (LF, CRLF,
  byte-order mark) and a counting-view helper; later steps extend it.

**Completion criteria**:

- The command printed by `pw scope day` reports the objective (`exit=0`) in
  the current effort scope.
- `rg -n 'open\(|write_bytes|write_text' tools/release_workflow/sources`
  finds no write in an adapter module.
- The completeness test fails when a temporary adapter module is listed
  without a tuple entry (asserted through the synthetic listing).

#### Step 2 -- addendums for tokens, anchor and model

Line-budget checkpoint:

- [ ] `tools/release_workflow/sources/__init__.py`: before 0; ceiling <= 650; expected 25 (advisory).
- [ ] `tools/release_workflow/sources/model.py`: before 0; below-550 safe; ceiling <= 650; expected 360 (advisory).
- [ ] `tools/release_workflow/sources/anchor.py`: before 0; ceiling <= 650; expected 110 (advisory).
- [ ] `tests/unit/tools/release_workflow/version_support.py`: before 0; ceiling <= 650; expected 80 at this step (advisory).
- [ ] New test files: before 0; ceiling <= 650; expected 200, 90, 160, 70 and 80 (advisory); initializers 3 lines each.

Split guidance:

- If `model.py` would pass 650, move `VersionToken` and `Form` into
  `sources/tokens.py`; the located-source, shared input, plan and composition
  types stay in `model.py`.

Full workflow timing run readiness:

- `ghog single` on the Step 2 test files, then the command printed by `pw scope day`.

Time-gated status for Step 2:

- No perf gate is affected; the property tests use integer and short ASCII
  encodings to stay inside the lifecycle budget.

---

### Step 3. Version configuration, participation, claims and pattern sources

#### Step 3 -- analysis and intent for configuration and claims

Issues to address:

- `.release.ini` rejects `[source:<name>]` and `[component:<id>]` because no
  shipped schema claims them.
- No participating-root list, pattern source, claim registry or candidate
  listing exists.

Fix intent:

- Declare the version schema in `schemas.py` with a deferred validator that
  applies the per-instance rules.
- Compute participating roots, run the adapters in tuple order over them,
  register claims by physical path, field and span, and compose per-file edits.
- Add the pattern adapter with the CRLF-to-LF view and the span mapping back
  to the original bytes.
- List undeclared candidates for `versions list` from one Git listing.

Expected outcome:

- An invalid form, a reserved name, an unknown key or a missing pattern key
  fails configuration for every command, even `version`.
- A second claim on one path and field, or any overlapping span, fails before
  any write and names both claimants; disjoint fields in one file compose.
- A pattern matching zero or several times, or with an empty optional group,
  fails `list`, `check` and `set`.

Step framing:

- Design link: "Configuration of the version domain in .release.ini",
  "Combining all detectors", "Participating roots", "Pattern sources",
  "Undeclared nested candidates"; design decisions Q09, Q10, Q13, Q14, Q15; AC4, AC5,
  AC6, AC10, AC12.
- Execution checklist reference: [Shared execution command checklist for all
  v0.14.0 version-sources steps](#shared-execution-command-checklist-for-all-v0140-version-sources-steps).

#### Step 3 -- implementation for configuration and claims

**Files involved**:

- `tools/release_workflow/schemas.py` (existing, to be updated).
- `tools/release_workflow/sources/__init__.py` (existing, to be updated).
- `tools/release_workflow/sources/settings.py` (new, to be created).
- `tools/release_workflow/sources/pattern.py` (new, to be created).
- `tools/release_workflow/sources/detection.py` (new, to be created).
- `tests/unit/tools/release_workflow/version_support.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_schemas/test_schemas_tdd.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_version_registry/test_version_registry_tdd.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_version_settings/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_version_settings/test_version_settings_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_pattern_sources/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_pattern_sources/test_pattern_sources_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_pattern_sources/test_pattern_sources_pbt.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_version_detection/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_version_detection/test_version_detection_tdd.py` (new, to be created).

**Tests first**:

- Schemas: `test_foundation_ships_only_tooling` becomes a check that the
  shipped tuple is exactly `(TOOLING_SCHEMA, VERSION_SCHEMA)`; a configuration
  without version sections imports no `tools.release_workflow.sources` module:
  the test removes those entries from a monkeypatched copy of `sys.modules`
  first, so the result does not depend on what earlier tests loaded.
- Settings, through `load_configuration`: `[source:npm] form = snapshot`
  accepted; `[source:python] form = snapshot`, `[source:maven] form = core`,
  `[source:npm] file = x`, `[source:npm]` with an unknown key, `[source:anchor]`,
  `[source:pattern]`, a pattern source missing `file`, `pattern` or `form`, a
  pattern that does not compile or holds zero or two groups, a component whose
  root is the project root, under `node_modules` or `samples`, or declared
  twice for one physical directory: each fails as `ConfigurationError` naming
  the section and key.
- Pattern sources: the umbrella's `^APP_SERVICE_VERSION=(.+)$` on LF and CRLF
  files captures no carriage return and the file keeps its line endings; zero
  matches, two matches, an empty optional group, a missing file and a value
  malformed for its form fail with status 2; a byte-order mark, accented
  letters and a non-BMP character before the match shift the mapped byte span
  correctly on LF and CRLF files, and two pattern sources in one file compose
  from one original.
- Detection: two synthetic adapters claiming one path and field, overlapping
  spans under different fields, two pattern sources capturing the same bytes
  and a pattern capturing a span claimed by another adapter all fail before
  any write and name both claimants; two disjoint fields of one file compose
  from one original; a declared component root that is missing or not a
  directory fails; every adapter runs over every participating root in tuple
  order; the file view loads each file once.
- Candidates: from a declared listing, `frontend/package.json` with a version
  is `not-participating undeclared`; files under each excluded directory name
  and under the artifact home are skipped; a manifest without a project version
  is not a candidate; the root's own files and declared component roots are not
  candidates; exactly one Git listing call.
- PBT (needed): the CRLF view and offset map over generated LF/CRLF line lists
  map every LF-view span back to the same characters in the original bytes.

**Classes and behavior**:

- `schemas.VERSION_SCHEMA`: `DomainSchema("version", (SectionSchema("source:",
  (ValueRule("form"), ValueRule("file", path_role="managed"),
  ValueRule("pattern")), family=True), SectionSchema("component:",
  (ValueRule("root", required=True, path_role="managed"),), family=True)),
  validate=_validate_version)`; `SHIPPED_SCHEMAS = (TOOLING_SCHEMA,
  VERSION_SCHEMA)`. `_validate_version` returns at once when no `source:` or
  `component:` section is declared, otherwise imports and calls
  `sources.settings.validate_settings`.
- `settings.validate_settings(sections)`: per-instance rules of "Sections and
  keys", with forms read from the registered adapters' `forms`.
  `settings.read_settings(configuration) -> VersionSettings` (form overrides by
  adapter name, pattern declarations, components by id).
  `settings.EXCLUDED_DIRECTORIES` holds the fixed directory names shared by the
  validator and candidate filtering.
- `pattern.ADAPTER`: name `pattern`, no default form; emits declared pattern
  sources only for the project root, reading each declared file through the
  view, matching with `re.MULTILINE` on the LF view and mapping the capture back.
- `detection.participating_roots(project, settings)`, `detection.detect(inputs:
  model.VersionInputs, view) -> model.Inventory` (located sources, visible
  records, claims, one `FileCapture` per participating file) and
  `detection.plan_edits(inventory, anchor) -> tuple[model.FileEdit, ...]` (one
  new content per changed file, through `model.compose`, with its
  `SourceChange` records). Every type comes from the Step 2 model.
- `detection.candidates(inputs, inventory) -> tuple[VisibleRecord, ...]`: one
  `git.listing`, filter by manifest name, exclusions, artifact home and
  participation, then `has_project_version` on each remaining file read once.
- `ADAPTERS = (anchor.ADAPTER, pattern.ADAPTER)` at this step.

**Completion criteria**:

- The command printed by `pw scope day` reports the objective (`exit=0`) in
  the current effort scope.
- `rg -n 'import tools.release_workflow.sources|from tools.release_workflow.sources' tools/release_workflow/schemas.py`
  shows only the deferred import inside `_validate_version`.
- The configuration tests of item 1 pass unchanged.

#### Step 3 -- addendums for configuration and claims

Line-budget checkpoint:

- [ ] `tools/release_workflow/schemas.py`: before 196; below-550 safe; ceiling <= 650; expected +22 (advisory).
- [ ] `tools/release_workflow/sources/settings.py`: before 0; ceiling <= 650; expected 170 (advisory).
- [ ] `tools/release_workflow/sources/pattern.py`: before 0; ceiling <= 650; expected 130 (advisory).
- [ ] `tools/release_workflow/sources/detection.py`: before 0; below-550 safe; ceiling <= 650; expected 300 (advisory).
- [ ] `tests/unit/tools/release_workflow/version_support.py`: recount at entry; ceiling <= 650; expected +60 (advisory).
- [ ] Test files: `test_schemas_tdd.py` before 90, expected +8; new files expected 220, 170, 60 and 300 (advisory).

Split guidance:

- If `detection.py` would pass 650, move candidate listing into
  `sources/candidates.py`; the claim registry and edit planning stay together.

Full workflow timing run readiness:

- `ghog single` on the Step 3 test files and the item 1 configuration and
  schema tests, then the command printed by `pw scope day`.

Time-gated status for Step 3:

- No perf gate is affected.

---

### Step 4. Recoverable version transition

#### Step 4 -- analysis and intent for the transition

Issues to address:

- Item 1 replaces one file atomically but has no multi-file transaction,
  evidence, verification or restoration.
- Item 5 needs the same primitive with its own lock and transaction identity.

Fix intent:

- An evidence module that writes, reads, marks and deletes the
  per-transition directory, and classifies leftover evidence.
- A transition module that plans without side effects, then under the lock
  checks evidence, replans, writes evidence, replaces files in order with
  `version.txt` last, verifies, marks completion, cleans up or restores, and
  reports one of five outcomes.

Expected outcome:

- A failure before the first overwrite leaves sources unchanged and no
  evidence; a failure after it restores every replaced file (status 1) or
  reports each unrestored source and its retained copy (status 3).
- A same-target clean run takes and releases the lock and reports `unchanged`
  without writing a source; `writing` evidence stops the next `set` even for
  the same target.
- A lifecycle call keeps its `complete` evidence and receives a restore handle.

Step framing:

- Design link: "Target flow of the version commands", "The recoverable version
  transition" and its subsections; design decisions Q04, Q05, Q06, Q07, Q17; AC3,
  AC11.
- Execution checklist reference: [Shared execution command checklist for all
  v0.14.0 version-sources steps](#shared-execution-command-checklist-for-all-v0140-version-sources-steps).

#### Step 4 -- implementation for the transition

**Files involved**:

- `tools/release_workflow/version_evidence.py` (new, to be created).
- `tools/release_workflow/version_transition.py` (new, to be created).
- `tests/unit/tools/release_workflow/version_support.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_version_evidence/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_version_evidence/test_version_evidence_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_version_transition/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_version_transition/test_version_transition_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_version_transition/test_version_restoration_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_version_transition/test_version_lifecycle_tdd.py` (new, to be created).

**Tests first**:

- Evidence: a written directory holds one copy per participating file and a
  manifest with owner, paths, SHA-256, existence, target and state `writing`;
  a failure while writing removes the partial directory; marking `complete` and
  `restoration-incomplete` replaces the manifest atomically; deletion removes
  copies first and the manifest last; listing classifies standalone complete
  residue, interrupted, unreadable (including duplicate JSON keys) and
  lifecycle-owned evidence; the listing reads only the artifact home, not
  recursively.
- Evidence allocation (plan decision Q17): two allocations with the
  same injected clock and process id get distinct directories, the second
  with the next sequence suffix; a declared pre-existing directory of that
  name, complete or partial (no manifest, or copies only), is skipped and its
  bytes stay identical; reaching the attempt limit fails before any source
  write with status 1 and no partial evidence; an existing evidence directory
  is never written into.
- Transition: a side-effect-free plan failure (unsupported arrangement,
  overlapping claim, release-only refusal) leaves no artifact home, lock or
  evidence; a held lock fails with status 1 naming the owner; standalone
  complete residue is removed with a warning before the plan; interrupted,
  unreadable and foreign lifecycle evidence stop with status 2 naming the
  directory, even when the locked plan is empty; an empty locked plan reports
  `unchanged`; a successful run writes in path order with `version.txt` last,
  verifies in a fresh view, marks complete, deletes the evidence and releases
  the lock; the changes list carries old and new values.
- Restoration (`test_version_restoration_tdd.py`): for the anchor and pattern
  fixture sets available at this step, and a synthetic file with two disjoint
  claims, a failure injected at every write position (exhaustive
  parametrization) restores the replaced files, verifies them, deletes the
  evidence and returns status 1; the parametrization is a registry of fixture
  sets that Steps 5, 6 and 7 extend with their adapters (plan decision Q01), and
  Step 7 adds the combined five-file project once every adapter exists; a concurrent change detected
  before a replacement, a verification failure and a marker failure restore;
  a failure while restoring returns status 3 with each unrestored source and
  its retained copy, state `restoration-incomplete`; declared `writing`
  evidence after the last replacement stops the same-target rerun.
- Completion-boundary faults (same file): after the durable `complete`
  marker, a failure deleting an original copy, deleting the manifest or
  removing the directory, and a failure of the standalone
  `OperationLock.release()`, each return `applied with cleanup failed`,
  status 1, with the new source bytes in place, no restoration attempted and a
  diagnostic naming the actual residue (directory, manifest or lock record);
  the next `set` removes complete standalone residue. An incomplete
  restoration followed by a lock-release failure still returns status 3 and
  names every unrestored path and its retained original; the secondary error
  is added as a diagnostic and never replaces the primary result.
- Lifecycle (`test_version_lifecycle_tdd.py`): a supplied held lock is
  verified, neither acquired nor released; a released handle or one for
  another project fails before any source read (counting view at zero loads);
  evidence owned by the transaction is kept `complete` and the restore handle
  restores the sources with the same routine; the transaction's own earlier
  evidence is accepted and any other unfinished evidence stops the call; two
  calls under one lifecycle lock with identical injected clock and process id
  keep two disjoint evidence directories, and the first restore handle still
  restores the first call's originals afterwards.
- PBT: not needed; the failure-position domain is finite and parametrized
  exhaustively.

**Classes and behavior**:

- `version_evidence.EvidenceManifest` (version 1, owner, target, state,
  created local timestamp with offset, files with path, SHA-256, existence and
  copy name), strict decoding that rejects duplicate keys.
- `version_evidence.allocate(prepared, project, clock, pid) -> ManagedTarget`:
  authorizes `a.version-transition.<timestamp>-<pid>` in the prepared home and
  creates it exclusively (`Path.mkdir(exist_ok=False)` on the revalidated
  target, then revalidation); on `FileExistsError` it tries
  `<timestamp>-<pid>-2`, `-3` and so on up to a fixed attempt limit, never
  entering an existing directory. Item 1's `prepare_directory`
  (`exist_ok=True`) is not used for evidence, and `managed_files` is
  unchanged.
- `version_evidence.write_evidence(directory, owner, target, captures) ->
  EvidenceDirectory` writes copies through `authorize_write` and
  `replace_bytes`, manifest last; `EvidenceDirectory.mark(state)` and
  `delete()`; `find_evidence(declaration) -> tuple[EvidenceEntry, ...]`.
- `VersionInputs`, `FileCapture`, `FileEdit`, `Inventory` and `Plan` come from
  the Step 2 model (plan decision Q16); this step adds no second definition.
- `version_transition.TransitionOutcome`: `APPLIED`, `UNCHANGED`, `RESTORED`,
  `RESTORATION_INCOMPLETE`, `APPLIED_CLEANUP_FAILED`, with statuses 0, 0, 1, 3
  and 1.
- `version_transition.TransitionResult` (outcome, changes, diagnostics,
  `restore: RestoreHandle | None`); `LifecycleOwnership` (held lock,
  transaction identity); `RestoreHandle.restore()` and `discard()` for item 5.
- `version_transition.TransitionPorts` (frozen dataclass, plan decision Q07):
  `replace` (default `managed_files.replace_bytes`), `remove` (managed file
  and directory removal), `lock_factory` (default `OperationLock`), `probe`
  (default `process_state`), `clock` (local time with offset) and `pid`
  (default `os.getpid`).
- `version_transition.plan_transition(inputs, target) -> Plan` and
  `set_versions(inputs, target, *, lifecycle=None, ports=TransitionPorts())
  -> TransitionResult`, following "Ownership and the authoritative plan"
  through "Restoration and its distinct failure" in order. A standalone run
  releases its lock on every path after acquisition; a lifecycle run never
  releases the supplied lock. The primary outcome is fixed before cleanup and
  release run; their failures only add diagnostics (status 1 after the
  completion marker, status 3 kept after an incomplete restoration).

**Completion criteria**:

- The command printed by `pw scope day` reports the objective (`exit=0`) in
  the current effort scope.
- `rg -n 'os\.replace|write_bytes|unlink' tools/release_workflow/version_transition.py tools/release_workflow/version_evidence.py`
  shows file changes only through `managed_files` targets.
- The anchor and pattern contract sets include failure restoration (AC3), and
  the restoration fixture registry is ready for Steps 5 to 7 to extend.

#### Step 4 -- addendums for the transition

Line-budget checkpoint:

- [ ] `tools/release_workflow/version_evidence.py`: before 0; below-550 safe; ceiling <= 650; expected 300 (advisory).
- [ ] `tools/release_workflow/version_transition.py`: before 0; below-550 safe; ceiling <= 650; expected 450 (advisory).
- [ ] `tests/unit/tools/release_workflow/version_support.py`: recount at entry; ceiling <= 650; expected +60 (advisory).
- [ ] New test files: expected 300, 320, 460 and 240 (advisory); split `test_version_restoration_tdd.py` into a completion-boundary file if it would pass 650.

Split guidance:

- If `version_transition.py` would pass 650, move restoration and cleanup into
  `tools/release_workflow/version_restoration.py`; planning, ownership and
  ordered writes stay in `version_transition.py`.
- If `version_support.py` would pass 650, move the ecosystem byte builders into
  `version_project_support.py`.

Full workflow timing run readiness:

- `ghog single` on the Step 4 test files, then the command printed by `pw scope day`.

Time-gated status for Step 4:

- No perf gate is affected; each parametrized failure case runs one
  transition over at most five small files.

---

### Step 5. Python and uv adapter with recorded uv evidence

#### Step 5 -- analysis and intent for the Python and uv adapter

Issues to address:

- No adapter reads or writes `pyproject.toml` or `uv.lock`, and nothing rejects
  uv workspaces or local links between participating components.
- No recorded evidence backs any uv lock schema yet, and the design forbids
  claiming support without it.

Fix intent:

- A TOML line scanner for the single-line `version = "..."` assignment in
  `[project]` and in the matching `[[package]]` block.
- The `python` adapter with participation, lock pairing, registered schemas
  and the workspace and local-link rejections.
- A recorder that produces the uv evidence with the real tool outside pytest,
  and a test that checks the adapter still reproduces each recorded edited pair.

Expected outcome:

- A tool-only `pyproject.toml` and its lock are listed as not participating;
  a dynamic or missing version, an orphan lock, an ambiguous lock root, an
  unregistered `version`/`revision` pair, a workspace and a local link fail
  before any write.
- Registered pairs are exactly those with recorded evidence: `(1, 3)` and
  `(1, 5)` for uv 0.13.4, virtual and editable roots.

Step framing:

- Design link: "Python with uv", "Locating values with the standard library",
  "Lock compatibility evidence for supported tools"; design decision Q08; AC4, AC6,
  AC8, AC9.
- Execution checklist reference: [Shared execution command checklist for all
  v0.14.0 version-sources steps](#shared-execution-command-checklist-for-all-v0140-version-sources-steps).

#### Step 5 -- implementation for the Python and uv adapter

**Files involved**:

- `tools/release_workflow/sources/toml_scan.py` (new, to be created).
- `tools/release_workflow/sources/python.py` (new, to be created).
- `tools/release_workflow/sources/__init__.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/version_support.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/lock_evidence_recorder.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_version_registry/test_version_registry_tdd.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_version_formats/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_version_formats/test_toml_scan_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_version_formats/test_version_formats_pbt.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_python_sources/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_python_sources/test_python_sources_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_python_sources/test_python_links_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_version_lock_evidence/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_version_lock_evidence/test_version_lock_evidence_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_version_lock_evidence/lock_evidence.v1.json` (new, to be created).
- `tests/unit/tools/release_workflow/test_version_transition/test_version_restoration_tdd.py` (existing, to be updated).

**Tests first**:

- Restoration contract (plan decision Q01): the Python fixture sets (virtual and
  editable roots with their `uv.lock`) join the Step 4 restoration matrix, so
  a failure at every write position restores `pyproject.toml` and `uv.lock`
  byte for byte.
- Scanner: basic and literal strings, comments and spacing around `=`, a
  `version` key in another table ignored, the matching `[[package]]` block
  among several; dotted `project.version`, an inline `project` table and a
  multi-line string fail as unsupported layouts with the remedy; a located text
  that differs from the `tomllib` value (an escape) fails; a description with
  accented letters and a non-BMP character before `[project].version`, and a
  `uv.lock` with such text in an earlier `[[package]]` block, map to the right
  byte spans through `model.to_byte_spans`, and the edit keeps every other
  byte.
- Adapter: llm-shared's shape (`name = "LLM-Shared"`, lock package
  `llm-shared`, `source = { virtual = "." }`) pairs by normalized name; an
  editable root pairs; zero or two matching packages fail as ambiguous; a lock
  without a participating `pyproject.toml` fails as orphan; an absent lock is
  not generated; `[project]` missing gives two tool-only records; dynamic and
  missing versions fail with the remedy; an unparsable file fails; a
  snapshot anchor gives `core` values.
- Links (`test_python_links_tdd.py`): `[tool.uv.workspace]` in a participating
  file, with or without a lock; a tool-only root whose `members` net of
  `exclude` match a declared component; a tool-only root whose members match
  none (stays outside participation); a lock `[manifest]` with members;
  `workspace = true`; a `path` source and a `file:` reference in dependencies,
  optional dependencies and dependency groups resolving into another
  participating root (fail naming both components) or elsewhere (external,
  unchanged); Git and URL sources unchanged.
- Evidence: the JSON holds a record for every registered pair and layout;
  each record names tool, version, schema, layout, line endings, command and
  outcomes, with SHA-256 of both files before and after each tool run; tool
  runs left both files unchanged; the adapter's edit of the recorded before
  pair equals the recorded edited pair byte for byte; a pair outside the
  registry fails detection.
- PBT (needed): the TOML scanner over generated spacing, comment and quote
  variants locates a span whose text equals the parsed value, and replacing it
  leaves every other byte unchanged.

**Classes and behavior**:

- `toml_scan.locate(text, table, *, package=None) -> Span`: line-oriented
  table tracking with array-of-tables blocks; returns the string content span.
- `python.ADAPTER`: name `python`, forms `{core}`, default `core`; detects at
  each participating root; normalizes names (lowercase, runs of `-`, `_`, `.`
  as one `-`); `REGISTERED_LOCK_SCHEMAS = frozenset({(1, 3), (1, 5)})`, each
  pair documented next to its evidence record; workspace members matched with
  `PurePosixPath.full_match` against participating roots relative to the
  project root; `path` and `file:` destinations resolved against the declaring
  root and compared physically.
- `ADAPTERS = (anchor, python, pattern)` at this step.
- `lock_evidence_recorder.py` (started by hand, never imported by a test):
  creates each scenario in a new temporary directory outside the repository;
  writes the virtual and editable `pyproject.toml` fixtures with version
  `0.13.0`; generates the revision 5 lock with `uv lock --offline --no-config
  --python <python>`; derives the revision 3 lock by setting its revision line,
  recording that provenance; runs `uv lock --locked --offline --no-config
  --python <python>` on the before pair; applies the production adapter's
  planned edit to `0.14.0`; runs the frozen command again; records the
  manifest-only control; adds an LF-to-CRLF variant of the virtual revision 3
  pair; writes `lock_evidence.v1.json` with sorted keys, LF endings and
  placeholders instead of absolute paths.

**Completion criteria**:

- The command printed by `pw scope day` reports the objective (`exit=0`) in
  the current effort scope.
- `lock_evidence.v1.json` was produced by the recorder with uv 0.13.4 and is
  committed with the step; the evidence test passes.
- `rg -n 'subprocess' tools/release_workflow/sources` finds nothing.

#### Step 5 -- addendums for the Python and uv adapter

Line-budget checkpoint:

- [ ] `tools/release_workflow/sources/toml_scan.py`: before 0; ceiling <= 650; expected 170 (advisory).
- [ ] `tools/release_workflow/sources/python.py`: before 0; below-550 safe; ceiling <= 650; expected 430 (advisory).
- [ ] `tests/unit/tools/release_workflow/lock_evidence_recorder.py`: before 0; ceiling <= 650; expected 220 at this step (advisory).
- [ ] `tests/unit/tools/release_workflow/version_support.py`: recount at entry; ceiling <= 650; expected +50 (advisory).
- [ ] New test files: expected 200, 120, 280, 260 and 140 (advisory); the JSON file has no Python ceiling.

Split guidance:

- If `python.py` would pass 650, move the workspace and local-link rejections
  into `sources/python_links.py`, keeping detection and lock pairing in
  `python.py`.

Full workflow timing run readiness:

- `ghog single` on the Step 5 test files, then the command printed by `pw scope day`.

Time-gated status for Step 5:

- No perf gate is affected; the evidence test reads its JSON file once per
  session through one replaceable loader.

---

### Step 6. npm adapter with recorded npm evidence

#### Step 6 -- analysis and intent for the npm adapter

Issues to address:

- No adapter reads or writes `package.json` and its lock, and nothing rejects
  npm workspaces, local links, shrinkwrap files or format 1 locks.
- No recorded evidence backs lock formats 2 and 3 yet.

Fix intent:

- A path-tracking JSON scanner for the top-level `version`,
  `packages[""].version` and `lockfileVersion`, rejecting duplicate keys on
  those paths.
- The `npm` adapter with its three forms, the release-only default and the
  lock pairing rules.
- npm records added to the evidence file by the recorder.

Expected outcome:

- workspace-halo's shape (format 3, CRLF lock) changes only the two lock
  version strings and the manifest version.
- A format 1 lock fails with the remedy to regenerate it with npm 7 or later;
  a shrinkwrap file, a `workspaces` field and a local link into another
  participating root fail before any write.

Step framing:

- Design link: "npm", "Locating values with the standard library", "Lock
  compatibility evidence for supported tools"; design decisions Q10, Q11; AC4, AC7,
  AC8, AC9.
- Execution checklist reference: [Shared execution command checklist for all
  v0.14.0 version-sources steps](#shared-execution-command-checklist-for-all-v0140-version-sources-steps).

#### Step 6 -- implementation for the npm adapter

**Files involved**:

- `tools/release_workflow/sources/json_scan.py` (new, to be created).
- `tools/release_workflow/sources/npm.py` (new, to be created).
- `tools/release_workflow/sources/__init__.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/version_support.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/lock_evidence_recorder.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_version_registry/test_version_registry_tdd.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_version_formats/test_json_scan_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_version_formats/test_version_formats_pbt.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_npm_sources/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_npm_sources/test_npm_sources_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_version_lock_evidence/test_version_lock_evidence_tdd.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_version_lock_evidence/lock_evidence.v1.json` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_version_transition/test_version_restoration_tdd.py` (existing, to be updated).

**Tests first**:

- Restoration contract (plan decision Q01): the npm fixture sets (formats 2 and 3,
  LF and CRLF, with the two lock fields composed in one file) join the
  restoration matrix; a failure at every write position restores
  `package.json` and `package-lock.json` byte for byte.
- Scanner: string spans of the two owned paths among nested objects and
  arrays; a duplicate key on an owned path fails as ambiguous; duplicates
  elsewhere ignored; an escape inside an owned value fails; non-object roots
  fail; a `description` with accented letters and a non-BMP character before
  the top-level `version`, and both owned lock fields after such text, map to
  the right byte spans through `model.to_byte_spans`, composing both lock
  edits from one original.
- Adapter: default `release-only` keeps `0.0.25` for anchor `0.0.25-SNAPSHOT`;
  `[source:npm] form = snapshot` gives the suffix; a release-only source at
  `0.0.25` refuses `set 0.0.24` before any write and `check` reports drift; a
  manifest without `version` gives two tool-only records; `workspaces` fails;
  `file:` and `link:` into another participating root fail naming both, and
  elsewhere stay unchanged; `workspace:` naming a participating package fails;
  `npm-shrinkwrap.json` fails; formats 2 and 3 locate the top-level `version`
  where present and `packages[""].version`; format 1 fails with the remedy;
  another format, a `packages[""].name` naming another package, a missing
  `packages[""].version` and an orphan lock fail; Yarn and pnpm locks are never
  read (the view records no load).
- Evidence: npm records exist for formats 2 and 3 and the CRLF format 3
  variant, with tool runs unchanged and the adapter reproducing each edited
  pair; each record holds the frozen `npm ci` runs on the "before" pair and the
  edited pair, plus the lock-only check of plan decision Q05: `npm install
  --package-lock-only --offline --ignore-scripts --no-audit --no-fund` leaves
  the lock of the "before" pair and of the edited pair unchanged and rewrites
  the lock of the manifest-only control, whose root version fields must
  actually change for the check to count; the lock format stays the selected
  one, and actual exit codes and hashes are recorded.
- PBT (needed): the JSON scanner over generated objects and whitespace
  locates spans whose text equals the `json` value.

**Classes and behavior**:

- `json_scan.locate(text, paths) -> dict[path, Span]`: one pass over the
  decoded text with a key-path stack; reports duplicates only on owned paths.
- `npm.ADAPTER`: name `npm`, forms `{release-only, core, snapshot}`, default
  `release-only`; dependency sections `dependencies`, `devDependencies`,
  `optionalDependencies` and `peerDependencies`; `file:` and `link:` resolved
  against the declaring root; `workspace:` matched by package name against the
  participating npm manifest files.
- `ADAPTERS = (anchor, python, npm, pattern)` at this step.
- Recorder: Node 22.9.0 directory prepended to the child `PATH` only;
  `npm_config_cache` and `npm_config_userconfig` pointed into the scratch
  directory; lock generated with `npm install --package-lock-only --offline
  --lockfile-version <2|3> --ignore-scripts --no-audit --no-fund` for a root
  package `private: true` at `0.0.24`; frozen command `npm ci --offline
  --ignore-scripts --no-audit --no-fund`; lock-only check `npm install
  --package-lock-only --offline --ignore-scripts --no-audit --no-fund` on the
  "before" pair, the edited pair and a scratch copy of the manifest-only
  control (plan decision Q05); edit to `0.0.25` through the adapter; CRLF variant of
  format 3; `node_modules` removed before each run.

**Completion criteria**:

- The command printed by `pw scope day` reports the objective (`exit=0`) in
  the current effort scope.
- The evidence file holds the npm records produced by the recorder with npm
  10.8.3; the evidence test passes.
- `rg -n 'lockfileVersion' tools/release_workflow/sources/npm.py` shows the
  format check and the format 1 remedy.

#### Step 6 -- addendums for the npm adapter

Line-budget checkpoint:

- [ ] `tools/release_workflow/sources/json_scan.py`: before 0; ceiling <= 650; expected 220 (advisory).
- [ ] `tools/release_workflow/sources/npm.py`: before 0; below-550 safe; ceiling <= 650; expected 270 (advisory).
- [ ] `tests/unit/tools/release_workflow/lock_evidence_recorder.py`: recount at entry; ceiling <= 650; expected +110 (advisory).
- [ ] `tests/unit/tools/release_workflow/version_support.py`: recount at entry; ceiling <= 650; expected +40 (advisory).
- [ ] Test files: new 160 and 320; updated pbt +40 and evidence test +30 (advisory).

Split guidance:

- If the recorder would pass 650, split it into `lock_evidence_uv.py` and
  `lock_evidence_npm.py` beside a small common writer.

Full workflow timing run readiness:

- `ghog single` on the Step 6 test files, then the command printed by `pw scope day`.

Time-gated status for Step 6:

- No perf gate is affected.

---

### Step 7. Maven reactor adapter

#### Step 7 -- analysis and intent for the Maven adapter

Issues to address:

- No adapter reads a Maven reactor, its modules, internal parents or internal
  dependency versions.
- `xml.etree` drops formatting and offsets, so a byte-exact edit needs expat
  byte indexes.

Fix intent:

- An expat scanner that records, for the element paths Maven needs, their text
  and the byte span of that text, rejecting comments, CDATA, entity references
  and child markup inside owned elements, and any encoding other than UTF-8.
- The `maven` adapter: recursive modules, coordinates, the internal index,
  owned fields, inheritance through internal parents and the property
  boundary.

Expected outcome:

- my-project's shape (literal root version, module `PDF` with a literal
  internal parent version, `${project.version}` only in a plugin
  configuration) changes the root version and the module's parent version.
- `${revision}` in an owned field, a version range, modules inside a profile,
  a property in a module's own coordinates and a root POM without its own
  version under an external parent fail before any write.

Step framing:

- Design link: "Maven reactors", "Locating values with the standard library",
  "Combining all detectors"; design decisions Q08, Q10, Q12; AC5, AC6, AC9.
- Execution checklist reference: [Shared execution command checklist for all
  v0.14.0 version-sources steps](#shared-execution-command-checklist-for-all-v0140-version-sources-steps).

#### Step 7 -- implementation for the Maven adapter

**Files involved**:

- `tools/release_workflow/sources/xml_scan.py` (new, to be created).
- `tools/release_workflow/sources/maven.py` (new, to be created).
- `tools/release_workflow/sources/maven_references.py` (new, to be created).
- `tools/release_workflow/sources/__init__.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/version_support.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_version_registry/test_version_registry_tdd.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_version_transition/test_version_restoration_tdd.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_version_formats/test_xml_scan_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_version_formats/test_version_formats_pbt.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_maven_sources/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_maven_sources/test_maven_sources_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_maven_sources/test_maven_references_tdd.py` (new, to be created).

**Tests first**:

- Restoration contract (plan decision Q01): the Maven fixture sets (root with one
  module, inherited versions, internal dependencies) join the restoration
  matrix, and the combined five-file project (`version.txt`, Python, npm,
  Maven and a pattern source) is added now that every adapter exists; a
  failure at every write position restores every replaced file byte for byte.
- Scanner: element text spans for nested paths; whitespace and attributes
  around owned elements; a comment, CDATA, entity reference or child element
  inside an owned element fails; a non-UTF-8 declaration fails; a byte-order
  mark shifts offsets correctly; LF and CRLF files.
- Reactor (`test_maven_sources_tdd.py`): recursive modules relative to the
  declaring POM; a missing module POM fails; modules inside a profile fail as
  ambiguous; module coordinates with an inherited literal `groupId`; a
  property in own coordinates fails; the snapshot form keeps the suffix; a
  release anchor gives the core; a configured `core` form is rejected by
  configuration.
- References (`test_maven_references_tdd.py`): internal dependency and
  dependency-management versions, literal (owned) or absent (managed
  elsewhere); `${project.version}` kept; `${project.groupId}` identifies an
  internal entry; another group expression naming a module's `artifactId`
  fails as ambiguous; `${revision}` and ranges fail naming file, field and
  expression; an inherited version through an internal parent chain changes
  the ancestor's literal version and the `<parent>` versions; an external
  parent without an own version fails with the remedy; external parents,
  external dependencies, plugins and `<properties>` never change; an internal
  reference in a profile or a plugin dependency fails as unsupported; a
  declared component that is also a reactor module fails as a conflicting
  claim on its `pom.xml`.
- PBT (needed): the XML scanner over generated indentation, attribute and
  line-ending variants locates spans whose text equals the parsed element text.

**Classes and behavior**:

- `xml_scan.scan(content, wanted_paths) -> PomDocument`: expat with
  `CurrentByteIndex`; a text span starts at the first character-data event of
  an owned element and ends at the byte index of its end tag; the located bytes
  must decode to the parsed text.
- `maven.ADAPTER` in `sources/maven.py` (reactor discovery, plan decision Q10):
  name `maven`, forms `{snapshot}`, default `snapshot`; starts at each
  participating root's `pom.xml`; builds the module list recursively and the
  module coordinates, rejecting profile modules and properties in own
  coordinates; then asks `maven_references` for the owned fields.
- `sources/maven_references.py` (reference rules, plan decision Q10): the
  dictionary keyed by `(groupId, artifactId)`; owned fields per the design's
  "Owned fields" rule; inheritance through internal parents; the
  `${project.version}` and `${project.groupId}` boundary; internal references
  outside `project/dependencies` and
  `project/dependencyManagement/dependencies` fail as an unsupported
  arrangement (FR AC9). It contributes no adapter and is listed in the
  registry test's support-module set.
- `ADAPTERS = (anchor, python, npm, maven, pattern)`, the final order the
  registry test now pins.

**Completion criteria**:

- The command printed by `pw scope day` reports the objective (`exit=0`) in
  the current effort scope.
- `rg -n 'xml.etree' tools/release_workflow/sources` finds nothing.
- The registry test pins `("anchor", "python", "npm", "maven", "pattern")`.

#### Step 7 -- addendums for the Maven adapter

Line-budget checkpoint:

- [ ] `tools/release_workflow/sources/xml_scan.py`: before 0; ceiling <= 650; expected 220 (advisory).
- [ ] `tools/release_workflow/sources/maven.py`: before 0; below-550 safe; ceiling <= 650; expected 220 (advisory).
- [ ] `tools/release_workflow/sources/maven_references.py`: before 0; below-550 safe; ceiling <= 650; expected 280 (advisory).
- [ ] `tests/unit/tools/release_workflow/version_support.py`: recount at entry; ceiling <= 650; expected +50 (advisory).
- [ ] Test files: new 180, 260 and 320; updated pbt +40; restoration test +40 (advisory).

Split guidance:

- The reactor and reference responsibilities are already separate (decision
  Q10). If `maven_references.py` would still pass 650, move inheritance
  resolution into `sources/maven_inheritance.py`.

Full workflow timing run readiness:

- `ghog single` on the Step 7 test files, then the command printed by `pw scope day`.

Time-gated status for Step 7:

- No perf gate is affected.

---

### Step 8. Tag classification, range selection and the release-version rule

#### Step 8 -- analysis and intent for tags and ranges

Issues to address:

- Range readers use `git describe --tags --abbrev=0`, an unfiltered last-tag
  query that cannot tell stable, snapshot, engine and validated tags apart.
- Nothing exposes umbrella decision 33 to items 5 and 7.

Fix intent:

- Classify tag names and annotations by whole lines, group stable tags into
  boundaries, and apply the seven-step ancestry rule with at most four Git
  calls.
- Expose the release-version rule as a separate function using two tag
  listings.

Expected outcome:

- A snapshot at HEAD after `v0.13.0` gives `v0.13.0..HEAD`; an unvalidated
  engine tag is never a baseline; `range v0.13.0` never selects `v0.13.0`;
  conflicting aliases and versions fail with status 2 naming them.
- `0.13.0` is reserved when `v0.13.0` exists; a target must be higher than
  every eligible release reachable from `main`.

Prerequisite for aliased boundaries:

- The design does not yet say when a boundary holding several same-version,
  same-commit tags is eligible, nor which actual tag spelling the output
  prints for it. By plan decision Q15, both are settled in a design clarification
  that needs its own authorization (the Q15 choice does not grant it) and must
  be reviewed before this step's aliased-boundary tests are written. Until then the step implements and tests every other rule (single
  tags, conflicts, ancestry, counts, the release-version rule), and the cases
  that depend on the clarification stay blocked: a historical `0.13.0` with an
  unvalidated `v0.13.0` on one commit; a validated and an unvalidated alias on
  one commit; an ambiguous alias beside an eligible one; and the printed
  spelling of any boundary with two eligible aliases. The existing conflict
  rules (same version on different commits, different versions on one
  commit) are not part of that dependency and are tested now.

Step framing:

- Design link: "Stable and snapshot tag classification", "Range selection and
  the release-version rule"; design decisions Q01, Q02, Q03; AC13, AC14, AC15.
- Execution checklist reference: [Shared execution command checklist for all
  v0.14.0 version-sources steps](#shared-execution-command-checklist-for-all-v0140-version-sources-steps).

#### Step 8 -- implementation for tags and ranges

**Files involved**:

- `tools/release_workflow/tags.py` (new, to be created).
- `tests/unit/tools/release_workflow/version_support.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_release_tags/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_release_tags/test_release_tags_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_release_tags/test_release_ranges_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_release_tags/test_release_tags_pbt.py` (new, to be created).

**Tests first**:

- Classification: every row of the design's eligibility table; a trailer as
  substring of a notes line is not a trailer; `Release tooling:` without a
  value is not a trailer; `[valid]` before the trailer and two trailers are
  ambiguous; snapshot markers in both spellings and suffix cases; other
  prereleases ignored.
- Selection (`test_release_ranges_tdd.py`), on declared histories: every
  AC13 and AC14 acceptance row of the design; HEAD on a release gives an empty
  range after it; no candidate gives the full history; independent candidate
  tips fail; a version inversion fails; an ambiguous tag between baseline and
  target fails; an unvalidated engine tag there is excluded with a warning;
  the recorded Git calls follow the call table below in every case; the count
  is nonzero for a baseline several commits behind HEAD, zero for a release at
  HEAD, and the full-history count when no boundary is eligible; a
  syntactically valid missing tag target returns status 2 through
  `GitRevisionNotFound` from the one records call, while a canned Git
  execution failure of that call returns status 1.
- Release-version rule: reserved in either spelling whatever its eligibility;
  not higher than an eligible release on `main` rejected; numeric comparison;
  no eligible release accepts any well-formed target; two recorded calls.
- Consumer-shaped histories declared with generic names: twelve annotated
  `vX.Y.Z` tags with `[valid]`; 99 tags mixing annotated and lightweight with
  one snapshot; the mixed `v0.0.20`, `0.0.21`, `0.0.22`, `v0.0.23`, `v0.0.24`
  chain.
- PBT (needed): annotation classification over generated line sequences
  matches a reference predicate; on generated linear chains, the baseline is
  the nearest eligible ancestor boundary and the commit count equals the
  distance.

**Classes and behavior**:

- `tags.parse_name(name) -> StableName | SnapshotName | None`;
  `tags.Eligibility` (`HISTORICAL`, `VALIDATED`, `UNVALIDATED`, `AMBIGUOUS`);
  `tags.classify(record) -> ClassifiedTag`.
- `tags.select_range(git, *, cwd, target=None) -> RangeSelection` (target,
  baseline or `None`, range text, commit count, warnings); Git revisions use
  `HEAD` or `refs/tags/<name>`, the printed range uses plain names.
- `tags.check_release_version(git, *, cwd, version) -> None`, raising
  `RangeError(ValueError)` with `exit_code = 2`.
- A boundary is the set of stable tags with one version on one commit. A
  boundary of one tag takes that tag's eligibility and prints its name; the
  eligibility and printed spelling of a boundary with several tags wait for
  the prerequisite above.

Git calls of one selection, by case:

| Case | Calls | Result |
| --- | --- | --- |
| Malformed name, snapshot or other prerelease target | none | status 2 |
| Missing tag target | records (raises `GitRevisionNotFound`) | status 2 |
| Ineligible or ambiguous target, or conflicting tags | records | status 2 |
| No eligible candidate | records, count of the target | full history |
| One candidate | records, tags between baseline and target, count | baseline and range |
| Several candidates | records, independent tips, tags between, count | baseline and range, or status 2 for several tips or an inversion |
| Several candidates whose independent-tips command line would pass the Windows limit | records only; `GitCommandLineTooLong` before the tips call starts (plan decision Q13) | status 1 naming the limit and the candidate count |

The release-version rule uses two calls: all tag records and the records
merged into `main`.

**Completion criteria**:

- The command printed by `pw scope day` reports the objective (`exit=0`) in
  the current effort scope.
- `rg -n 'describe' tools/release_workflow/tags.py` finds no `git describe`.
- The recorded Git calls match the call table in every selection test.
- The aliased-boundary cases of the prerequisite are written and pass against
  the reviewed design clarification; until then Step 8 stays incomplete,
  while the earlier steps and the rest of Step 8 can proceed.

#### Step 8 -- addendums for tags and ranges

Line-budget checkpoint:

- [ ] `tools/release_workflow/tags.py`: before 0; below-550 safe; ceiling <= 650; expected 380 (advisory).
- [ ] `tests/unit/tools/release_workflow/version_support.py`: recount at entry; ceiling <= 650; expected +40 (advisory).
- [ ] New test files: expected 220, 380 and 120 (advisory).

Split guidance:

- If `tags.py` would pass 650, move the selector and the release-version rule
  into `tools/release_workflow/tag_ranges.py`; classification stays in
  `tags.py`.

Full workflow timing run readiness:

- `ghog single` on the Step 8 test files, then the command printed by `pw scope day`.

Time-gated status for Step 8:

- No perf gate is affected; generated chains stay under twenty commits so each
  example costs a few dictionary lookups.

---

### Step 9. Version commands, integrated acceptance and documentation

#### Step 9 -- analysis and intent for commands and rollout

Issues to address:

- No shipped handler exposes the domain; every operation is still unavailable.
- No end-to-end test runs the design's acceptance matrix through production
  bootstrap, dispatch and rendering.
- The reference pages still state that no operation is shipped and list only
  statuses 0, 1 and 2.

Fix intent:

- Register `version` and `versions` with their argument validators and
  output contracts.
- Run the design's acceptance matrix through the launcher simulation with
  whole-tree snapshots.
- Document the commands, statuses, configuration and limits.

Expected outcome:

- The five commands print the design's stdout formats and return its
  statuses; read commands warn about leftover evidence and create nothing.
- The integrated acceptance passes in the whole-suite coverage walk.

Step framing:

- Design link: "Command surface and operation arguments for version sources",
  "Read-only commands and their limits", "Acceptance cases for the
  version-sources design"; all FR acceptance criteria AC1 to AC15.
- Execution checklist reference: [Shared execution command checklist for all
  v0.14.0 version-sources steps](#shared-execution-command-checklist-for-all-v0140-version-sources-steps).

#### Step 9 -- implementation for commands and rollout

**Files involved**:

- `tools/release_workflow/versions.py` (new, to be created).
- `tools/release_workflow/cli.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/version_support.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_version_commands/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_version_commands/test_version_commands_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_version_acceptance/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_version_acceptance/test_version_acceptance_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_version_acceptance/test_version_range_acceptance_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_release_acceptance/test_release_acceptance_tdd.py` (existing, to be updated).
- `wiki/reference/version-sources.md` (new, to be created).
- `wiki/reference/automation-and-direct-invocation.md` (existing, to be updated).
- `wiki/reference/aliases-and-launchers.md` (existing, to be updated).
- `wiki/README.md` (existing, to be updated).

**Tests first**:

- Commands, through `cli.main` with the shipped registry: `version` prints
  token, title, empty line and notes; `versions list` prints the header and
  tab-separated records with `/` paths and `-` for non-participating form and
  value; `versions check` prints records and returns 1 on drift; `versions set`
  prints old and new values or `unchanged`; `versions range` prints the four
  `key=value` lines; missing, extra and malformed tokens return status 2 before
  any Git call; leftover evidence produces a stderr warning on read commands;
  status 3 reaches the caller.
- Acceptance (`test_version_acceptance_tdd.py`), through `cli.main` with the
  shipped registry and whole-tree snapshots (plan decision Q09): the source rows of
  the design's acceptance table (AC1 to AC12), including a combined Python,
  npm, Maven and pattern project with CRLF files, the release-only refusal,
  the injected third-of-five failure, an incomplete restoration (status 3),
  lock contention, leftover `writing` evidence, configuration failures that
  stop even `version`, and read commands that create no file or artifact. No
  restoration or no-write assertion is weaker than through the launcher.
- Launcher cases (same file, plan decision Q09): one `launcher_tooling.run` case
  per command (`version`, `versions list`, `check`, `set`, `range`) and per
  public status (0, 1, 2 and 3), proving that production bootstrap, readiness
  and rendering carry each contract.
- Acceptance (`test_version_range_acceptance_tdd.py`): the range rows (AC13 to
  AC15) through `versions range` via `cli.main`, plus the release-version rule
  on the same declared histories.
- `test_release_acceptance_tdd.py`: the shipped registry is exactly
  `{"version", "versions"}`; the acceptance handler names stay unavailable.
- PBT: not needed at this level; properties are owned by Steps 2 to 8.

**Classes and behavior**:

- `versions.VERSION_HANDLER` and `versions.VERSIONS_HANDLER`: `cli.Handler`
  values with validators (`version`: no token; `versions`: `list`, `check`,
  `set <token>`, `range`, `range <stable tag>`); heavy modules imported inside
  the execute functions so importing `cli` stays cheap.
- Output builders for the five formats; `SourceError`, `VersionError`,
  `RangeError` and `ConfigurationError` mapped to status 2,
  `OperationLockError` and `ArtifactError` mapped to their own status,
  `TransitionOutcome` mapped through its status.
- `cli.SHIPPED_HANDLERS = MappingProxyType({"version": ..., "versions": ...})`.
- `wiki/reference/version-sources.md` (reference only): commands and their
  stdout, statuses 0 to 3, `.release.ini` version sections, supported formats,
  forms and limits, the evidence directory and what a person does with
  interrupted evidence, `versions range` for instruction-driven readers, the
  recorded tool versions. The two existing reference pages replace "no
  operation is shipped" with the shipped pair and add the status 3 row;
  `wiki/README.md` links the new page in its reference list.

**Completion criteria**:

- The command printed by `pw scope day` reports the objective (`exit=0`), and
  `scope day --full=cov` reports full coverage for the whole suite.
- `rg -n 'cliff' tools/release_workflow` finds nothing.
- `rg -n 'unavailable in this tooling checkout|status 2' wiki/reference/automation-and-direct-invocation.md wiki/reference/aliases-and-launchers.md`
  shows no remaining claim that every operation is unavailable.
- The Markdown check passes on the new and updated pages.

#### Step 9 -- addendums for commands and rollout

Line-budget checkpoint:

- [ ] `tools/release_workflow/versions.py`: before 0; below-550 safe; ceiling <= 650; expected 290 (advisory).
- [ ] `tools/release_workflow/cli.py`: recount at entry (about 184 after Step 1); ceiling <= 650; expected +10 (advisory).
- [ ] `tests/unit/tools/release_workflow/version_support.py`: recount at entry; ceiling <= 650; expected +30 (advisory).
- [ ] New test files: expected 320, 420 and 220 (advisory); `test_release_acceptance_tdd.py` before 206, expected +4.
- [ ] Reference pages: 177, 178 and 267 lines before; the new page about 150; non-Python, no Python ceiling.

Split guidance:

- If `test_version_acceptance_tdd.py` would pass 650, split it by command
  family (`list` and `check` against `set`).

Full workflow timing run readiness:

- `ghog single` on the Step 9 test files, then the command printed by `pw scope day`, then `scope day --full=cov`.

Time-gated status for Step 9:

- No perf gate is affected; each acceptance case is one launcher-simulation
  call with a small project tree.

---

## Acceptance ownership map for v0.14.0 version-sources

| Design acceptance rows | Requirement | Unit proof | End-to-end proof |
| --- | --- | --- | --- |
| `version` output, malformed anchors, CRLF anchor write | AC1, AC2 | Step 2 anchor and model tests | Step 9 acceptance |
| Adapter missing from the tuple | AC3 | Step 2 registry test, extended to the final order in Step 7 | n/a |
| Failure restoration for every adapter | AC3, AC11 | Step 4 matrix on anchor and pattern sources, extended by Steps 5, 6 and 7 with each adapter's fixtures and the combined project | Step 9 acceptance |
| Root Python and npm files, tool-only pairs, undeclared candidates, conflicting component claim, overlapping pattern claims | AC4, AC5, AC10 | Steps 3 to 7 detection and adapter tests | Step 9 acceptance |
| Dynamic version, pattern match counts, Maven expressions, external parent | AC6, AC9 | Steps 3, 5 and 7 | Step 9 acceptance |
| Forms and release-only refusal | AC7 | Steps 2 and 6 | Step 9 acceptance |
| uv and npm lock edits, format 1 lock, unregistered uv pair, recorded evidence | AC4, AC8 | Steps 5 and 6 adapter and evidence tests | Step 9 acceptance |
| uv workspaces, Python and npm local links, npm workspaces, inherited Maven versions | AC9 | Steps 5, 6 and 7 | Step 9 acceptance |
| Injected failures, restoration, unchanged, contention, leftover evidence, cleanup failure, lifecycle lock binding | AC11 | Step 4 transition tests | Step 9 acceptance |
| Configuration failures for every command | AC12 | Step 3 settings tests | Step 9 acceptance |
| Snapshot at HEAD, unvalidated engine tag, ambiguous tag, conflicting aliases and versions, mixed prefixes | AC13, AC14 | Step 8 classification and range tests | Step 9 range acceptance |
| Reserved release version | AC15 | Step 8 rule tests | Step 9 range acceptance |

---

## Planning risk pass and rollout order for v0.14.0 version-sources

The steps are sequential: the transition (Step 4) consumes only the Step 2
shared types and the Step 3 planned-edit interface; each adapter step (Steps 5
to 7) plugs into the Step 3 claim registry and extends the Step 4 restoration
matrix with its own fixtures; the commands depend on the transition and the
selector. Steps 5, 6 and 7 can be reordered among themselves; the registry
test pins the final order once the last adapter lands. Every step passes its
own gate without a placeholder module for a later step.

Implementation risks found by the second pass:

- **Import cost on every call**: the version validator runs on every
  configuration load; its early return when no version section exists keeps
  item 1 commands and tests from importing the adapter package.
- **Windows command-line length**: `merge-base --independent` takes candidate
  commits as arguments, and `CreateProcess` accepts at most 32,767 UTF-16 code
  units including the terminating NUL. `independent_commits` measures the
  serialized command line (executable, Git prefix options, quoting, 40- or
  64-character object ids) and refuses with status 1 before starting Git
  (plan decision Q13). The consumers have at most 99 tags.
- **Evidence provenance**: the uv revision 3 fixture is a uv 0.13.4 lock with
  its revision line set to 3, which uv 0.13.4 accepts unchanged; the record
  states this and claims nothing about older tools or other revision 3 syntax
  (plan decision Q04). `npm ci` ignores the root version, so the npm records add
  the sensitive lock-only check (plan decision Q05). Recomputed hashes and edits
  check the records' consistency, not that the commands ran; the recorded
  outcomes and provenance carry that.
- **Readings of design-silent cases** (plan decision Q15): four follow from the
  requirement's "any other unsupported or ambiguous arrangement fails" rule or
  from an implementation mechanism, and the plan implements them as tested
  behavior:
  - an internal Maven reference outside `project/dependencies` and
    `project/dependencyManagement/dependencies` (a profile or a plugin
    dependency) fails rather than staying stale;
  - a `workspace:` npm specifier is matched by package name against the
    participating npm manifest files;
  - a declared component root that is missing fails detection, while one
    without any detected source yields no record;
  - an incomplete standalone restoration still releases the lock, since its
    retained `restoration-incomplete` evidence stops the next `set`.
- **Unresolved design dependency** (plan decision Q15): the eligibility of a
  boundary holding several aliases and the printed spelling of such a boundary
  are not settled by the design, and the plan does not settle them. Step 8's
  aliased-boundary cases wait for a design clarification that needs its own
  authorization (the Q15 choice does not grant it) and its own review; every
  other step, and the rest of Step 8, proceed without it.

Roll out by keeping every legacy path unchanged: `tools/dev_workflow` and
`prepare-release` keep their own version and range logic until items 7 and 8
switch them. The shipped commands are new entries of the release engine and
change no existing caller, and no version command runs tests: the umbrella
records the user's rule that `brel` never triggers the application test suite
(item 5). No private path or sensitive term is needed by any planned file or
fixture.

---

## Implementation decisions for v0.14.0 version-sources

The user decided each question after an explanation (Q01 and Q02 on
2026-11-07 afternoon, Q03 to Q08 on 2026-11-07 evening, Q09 to Q17 on
2026-11-08), always choosing the recommended option. Independent review round
3 checked the seventeen decisions for consistency with each other and with
the requirement, design and drafts, and found no missing question. The
question blocks are kept in the commit
`docs(plan): record pre-consolidation questions`.

| Question | Decision | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | B: the transition is Step 4, right after configuration and claims; Python, npm and Maven are Steps 5, 6 and 7, each adding its fixture set to the restoration matrix, so every adapter step completes its AC3 contract set | Plan goal; Steps 4 to 7; Shared test architecture ("Restoration contract per adapter"); acceptance ownership map; validation plan | A: adapters before the transition (restoration debt paid in one late step); C: transition split in two steps (one more review cycle for an interface with no caller until item 5) |
| Q02 | A: the version sections are declared in `schemas.py`, whose validator imports `sources.settings` only when a version section exists | Step 3 | B: schema in `sources/settings.py` imported at the end of `schemas.py` (import-order hazard); C: new `schema_types.py` (item 1 layout change) |
| Q03 | A: lock evidence is one committed JSON file beside its test, produced by a hand-run recorder in the test tree; the engine starts no process and coverage rules are unchanged | Steps 5 and 6; Runtime file note | B: generated Python module of byte constants (lint burden, poor diffs); C: recorder under `tools/` (process starts in the engine, new coverage omission) |
| Q04 | A: the uv revision 3 "before" lock is the uv 0.13.4 revision 5 lock with its revision line set to 3, provenance recorded; the claim covers uv 0.13.4 only | Lock compatibility facts; Step 5 | B: also install an older uv (download, second tool, guessed version); C: reduce llm-shared's real lock (rewritten anyway, needs cached metadata) |
| Q05 | B: the npm records keep `npm ci` and add `npm install --package-lock-only --offline --ignore-scripts --no-audit --no-fund` on the "before" pair, the edited pair and the manifest-only control | Lock compatibility facts; Step 6 | A: `npm ci` only (cannot detect a missed lock field); C: lock-only check instead (no frozen-mode record) |
| Q06 | A: uv evidence is recorded in the uv step and npm evidence in the npm step, so no registered schema ships without its record | Steps 5 and 6 | B: a dedicated evidence step after the adapters; C: recording in the final step (both leave support claimed without proof) |
| Q07 | B: one `TransitionPorts` value carries replacement, file and directory removal, lock factory, process probe, clock and process id, with production defaults | Step 4; Shared test architecture ("Fault injection") | A: six explicit keywords (wider signature); C: monkeypatching module globals (ruled out; definition-time defaults ignore it) |
| Q08 | A: tests declare commits, parents, `HEAD`, `main` and tags in `repository_simulation.py`, which answers the typed observations by reachability without interpreting Git arguments | Step 1; Step 8 | B: hand-written answers per query (can disagree); C: separate `release_history.py` from the start (kept as split guidance) |
| Q09 | B: acceptance rows run through `cli.main` with the shipped registry and whole-tree snapshots, plus one launcher case per command and per public status (0 to 3) | Step 9 | A: every row through the launcher (repeated bootstrap work against the budget); C: `cli.main` only (status 3 and new commands unproven through bootstrap) |
| Q10 | C: the Maven step creates `sources/maven.py` (reactor discovery) and `sources/maven_references.py` (references, parents, inheritance) from the start; `python.py` keeps its on-demand split guidance | Step 7; Step 5 split guidance | A: split only past 650 lines (forced split during review); B: pre-split Python too (extra module for about 120 lines) |
| Q11 | A: sixteen test leaves, one per production module or concern, following the item 1 `test_<name>/test_<name>_tdd.py` convention | Current test-tree validation snapshot; every step's files | B: about five subsystem leaves (breaks the convention, larger files) |
| Q12 | B: one development-suite test compares the statuses accepted by the four sites (`results.render`, `bootstrap.main`, both launchers) through the source-contract mechanism | Step 1 | A: per-site tests only (a later status can miss one site); C: shared Python constant (batch files still separate) |
| Q13 | B: `independent_commits` measures the serialized command line in UTF-16 code units including the terminating NUL and refuses with status 1 before starting Git | Step 1; Step 8 call table; risk pass | A: let Git fail (opaque launch error); C: chunked calls (break the four-call ceiling) |
| Q14 | A: Step 9 adds `wiki/reference/version-sources.md`, corrects the two existing reference pages and links the new page; the umbrella's final audit may still reorganize it | Step 9 | B: defer to the umbrella's final audit (false statements stay published); C: correct the old pages only (commands undocumented) |
| Q15 | B: the plan keeps four mechanism readings; aliased-boundary eligibility and printed spelling go to a separately authorized, reviewed design clarification before Step 8's alias tests | Step 8 prerequisite and completion criteria; risk pass | A: all five readings in the plan (a baseline rule set without design review); C: all five in the design (reopens settled mechanisms) |
| Q16 | A: `VersionInputs`, `FileCapture`, `SourceChange`, `FileEdit`, `Inventory` and `Plan` are defined in the Step 2 source model | Step 2; Steps 3 and 4 | B: separate `sources/inputs.py` (one more module); C: the transition module (Step 3 depends on Step 4, import cycle) |
| Q17 | A: the recovery evidence directory is created exclusively; a taken name gets the next `-2`, `-3` suffix up to a fixed limit, and an existing directory is never entered | Step 4; Runtime file note | B: stop on a collision (repeated lifecycle calls fail by timing); C: finer timestamp only (no protection of earlier evidence) |

User comments taken into account during the explanations: the "before" pair
of the lock evidence, a status normalization "site" and the scope of this
item's tests (llm-shared's development suite only) are now defined in every
effort document that relies on them; the user's rule that `brel` never
triggers the application test suite is recorded in the umbrella for item 5.
