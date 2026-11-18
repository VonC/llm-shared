# v0.14.0 git-cliff-provisioning implementation plan -- pinned git-cliff on demand

Add pinned git-cliff provisioning to the item 1 release engine: a tested-pin
manifest, contained Windows children, a guarded cache under a bounded lock, the
compatibility evidence that admits 2.14.2 and the `gcliff` launcher, each
delivered behind tests that start no process.

- **Pins and budgets**: the tested-pin manifest, the `[git-cliff]` domain of
  the common reader and the download budget policy read once per caller.
- **Contained execution and the cache**: suspended creation inside a
  parent-only kill-on-close job, the use guard, the entry record, the cache
  lock with owner-aware recovery, the download worker and single-member
  extraction.
- **Provisioning, evidence and launcher**: the provisioning service and its
  invocation object, the comparison harness and the reviewed bundle that
  admits 2.14.2, then the `gcliff` launcher and alias fragment.

> Markdown lint note: never leave a space immediately inside an inline code span
> (MD038); when a snippet starts or ends with a space, write that space as the
> literal token `[space]`, as in `` `[space]${x}` ``. End any line that would be
> only italic text with a period after the closing `_` (MD036).

## Plan goal for v0.14.0 git-cliff-provisioning

Implement the approved [design](design.v0.14.0.git-cliff-provisioning.md) and
[requirement](feature-request.v0.14.0.git-cliff-provisioning.md), beside the
[focused draft](draft.v0.14.0.git-cliff-provisioning.md). This is item 3 of
the [sibling release tooling umbrella](draft.v0.14.0.sibling_release_tooling.md);
it builds on the foundation of [the item 1 plan](plan.v0.14.0.release-project-root.md)
and the operations of [the item 2 plan](plan.v0.14.0.version-sources.md).

- **Step 1 goal**: the tested-pin manifest, the `[git-cliff]` configuration
  domain, the download budget policy and a shared strict record decoder.
- **Step 2 goal**: the native declarations, the Windows child lifecycle
  (platform baseline, parent-only kill-on-close job, suspended creation with
  a job list and a handle list, recording before resume, deadline
  termination), the use guard and the first committed native check record.
- **Step 3 goal**: the cache layout, the entry record and owner file, the
  lock-free reuse check, the cache lock with bounded waiting and owner-aware
  recovery, and the root `.gitignore` entry.
- **Step 4 goal**: the network client, the download worker started through
  the bootstrap, archive verification and single-member extraction, with the
  stalled-endpoint native check.
- **Step 5 goal**: the provisioning service, its invocation object with the
  engine and passthrough policies, messages, diagnostics and statuses, the
  entry point items 4 and 5 call, and the native checks through the service.
- **Step 6 goal**: the compatibility evidence harness: candidate identities
  and immutable trust records, the deterministic snapshot-tag fixture with
  Git's input stream, the controlled comparison and the compact bundle model
  with its review binding.
- **Step 7 goal**: the recorded evidence run and exit-path audit, the user's
  review recorded in the bundle, and the admission of 2.14.2 as the tested
  default.
- **Step 8 goal**: `bin/gcliff.bat`, the `gcliff-batch` entry kind, worktree
  pin selection, passthrough with status 69 for every failure before
  git-cliff starts, the alias fragment, integrated acceptance, the final
  native check run and the reference documentation.

No Step 0 is planned; see
[Performance-gate assessment for v0.14.0 git-cliff-provisioning](#performance-gate-assessment-for-v0140-git-cliff-provisioning).

---

## Scope anchors for v0.14.0 git-cliff-provisioning plan

This plan implements the design's four outcomes:

1. A tested-pin manifest names every admitted git-cliff version with the
   published identity of its Windows x64 asset, and the `[git-cliff]` domain
   admits only those versions.
2. One provisioning service returns an invocation object for a verified
   absolute `git-cliff.exe` of a pin, reusing a valid entry offline or
   downloading, verifying, extracting and publishing a new one under a bounded
   lock.
3. The `gcliff` launcher runs the provisioned git-cliff for the current
   worktree's pin and passes arguments, output and status through.
4. The compatibility harness compares raw git-cliff output of 2.7.0 and 2.14.2
   on recorded frozen inputs, and its committed bundle admits 2.14.2.

The following are explicitly **in scope** for this plan:

- Everything the design lists under "Delivered by item 3 in v0.14.0" and
  "Foundation changes required by git-cliff provisioning", with the item 1
  and item 2 test updates those changes need.
- `tools/release_workflow/git_cliff/`, the new Windows layer modules
  `windows_native.py`, `windows_child.py` and `windows_guard.py`, and the
  shared record decoder `lock_records.py`.
- `bin/gcliff.bat`, the alias fragment `bin/gcliff.doskey` and the root
  `.gitignore` entry `/.tools/git-cliff/`.
- The committed evidence bundle and trust records, the developer-run native
  check recorder with its committed evidence record, and the reference
  documentation.

The following are explicitly **deferred** beyond this item:

- Calling provisioning for rendering, `cliff.toml`, ranges, notes, fix rules,
  archives and the preflight ordering before `fixes init` (item 4); calling it
  from generated release `pre` (item 5); exposing the aliases to consumers and
  proposing newer pins (item 6); `/prepare-release` integration (item 7);
  adding `gcliff` to the shared `senv.doskey`, the cache ignore verification
  and the parity rehearsals (item 8).
- Other platforms, a mirror source, authenticated proxies, proxy
  auto-configuration scripts and automatic cache eviction.

---

## Complexity Bound Clarification for v0.14.0

The scaling target for all v0.14.0 git-cliff-provisioning code paths is:

- **O(1) amortized per call**: a pin lookup is one dictionary access in the
  manifest; the reuse check makes a constant number of operations (one guard,
  one record read, one hash pass, one probe), the hash pass itself being linear
  in the executable's bytes; a lock poll reads one record.
- **O(n) total per phase**: streaming, hashing and extraction are linear in
  archive and executable bytes; the lock wait is linear in its polls
  (W / 250 ms at most); leftover recovery is linear in the entries of one
  version directory, listed once without recursion; the harness is linear in
  ranges and output bytes.

The only path above linear is the harness's hunk computation for a range whose
outputs differ (`difflib`, worst case `O(n·m)` in output lines). It runs by
hand outside pytest, never during a release or a `gcliff` call. No other code
path may introduce a pairwise comparison of entries, records or ranges. Any
new path that breaks this bound must be called out as a defect before merge.

---

## File-based IO cost clarification for v0.14.0 git-cliff-provisioning

| Path | Reads | Writes | Process starts |
| --- | --- | --- | --- |
| Configuration load (every command) | `.release.ini` once, as today; the manifest is an in-memory table | none | none |
| `version`, `versions`, ordinary builds, curated validation | as today; the budget variable is never read | none | none of their own |
| Valid-entry reuse | one guard open on `git-cliff.exe`, one read of `entry.json`, one hash pass through the guard | none | one reuse probe |
| Lock wait | one lock record read per 250 ms poll | none | none |
| Provisioning under the lock | the lock record under the transition mutex; one non-recursive listing of the version directory for leftovers; the staged archive once for its digest | lock record, owner file, archive stream, one extracted member, `entry.json`, then renames for retirement and publication | download worker attempts (at most two), one staging probe |
| `gcliff` | `.release.ini` once through the reader, then reuse or provisioning | as provisioning, only when the entry is absent or invalid | Git discovery calls, then one git-cliff child |
| Evidence harness (by hand) | candidate trust records, the bundle, the bundle copy of `cliff.toml` | candidate cache entries, a temporary worktree and fixture repository outside the checkout, the bundle | metadata worker, download workers, probes, Git, one git-cliff run per range and candidate |

- No path scans a directory tree. The one directory listing is the version
  directory, under the lock, on the provisioning path only.
- Every record is complete before it is published: the lock record and entry
  record through non-replacing publication of a flushed file, the entry by one
  directory rename.
- Reuse writes nothing, so a read-only checkout with a valid entry renders.
- No document index, cache of metadata or new wall-clock target is added; the
  stage budgets are the design's deadlines, tested with a fake clock.

---

## Confirmed technical facts for v0.14.0 plan viability

Inspection baseline: 2026-11-15, branch `git-cliff-provisioning` at
`2b2cbab1`, before implementation. The effort documents share `docs/v0.14.0/`;
the two plans are new. Counts use the gate metric
`sum(1 for _ in path.open(encoding="utf-8", errors="ignore"))`; the active
Python ceiling is 650 lines.

**Files over the 650-line repository limit** (must be split by responsibility):

- None among the files involved.

**Files in the 550-through-650 risk band** (avoid growth where practical):

- `tests/unit/tools/release_workflow/version_support.py`: **552 lines** --
  reference only; no step adds to it. New git-cliff helpers go to
  `git_cliff_support.py`, `git_cliff_children_fake.py`,
  `git_cliff_harness_fake.py` and `native_kernel_fake.py`.

**Files below 550 and safe to extend** (current lines, expected additions):

| Existing file | Lines | Planned use |
| --- | --- | --- |
| `tools/release_workflow/schemas.py` | 220 | Step 1: git-cliff domain; advisory final 250 |
| `tools/release_workflow/operation_lock.py` | 261 | Step 1: use the shared record decoder; advisory final 235 |
| `tools/release_workflow/__init__.py` | 11 | Step 1: docstring names the `git_cliff` package |
| `tools/release_workflow/bootstrap.py` | 201 | Steps 4 and 8: worker and `gcliff-batch` entry kinds; advisory final 255 |
| `tools/release_workflow/invocation.py` | 199 | Step 8: `gcliff-batch` in `ENTRY_KINDS`; advisory final 201 |
| `tools/release_workflow/git.py` | 331 | Steps 6 and 8: optional input bytes, worktree-presence observation; advisory final 365 |
| `tools/release_workflow/paths.py` | 164 | Step 8: `find_worktree` for `gcliff`; advisory final 185 |
| `tools/release_workflow/windows_process.py` | 132 | Reference, reused unchanged |
| `tools/release_workflow/configuration.py` | 160 | Reference, unchanged |
| `tools/release_workflow/cli.py` | 176 | Reference, unchanged: no shipped handler is added |
| `tools/release_workflow/results.py` | 53 | Reference, unchanged |
| `tools/release_workflow/runtime_identity.py` | 162 | Reference, unchanged |
| `tests/unit/tools/release_workflow/launcher_simulation.py` | 210 | Step 8: route the `gcliff` entry; advisory final 260 |
| `tests/unit/tools/release_workflow/conftest.py` | 132 | Reference, unchanged |
| `tests/unit/tools/release_workflow/test_schemas/test_schemas_tdd.py` | 151 | Steps 1 and 7; advisory final 180 |
| `tests/unit/tools/release_workflow/test_configuration/test_configuration_tdd.py` | 256 | Steps 1 and 7; advisory final 290 |
| `tests/unit/tools/release_workflow/test_operation_lock/test_operation_lock_tdd.py` | 337 | Step 1 regression, unchanged |
| `tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py` | 212 | Steps 4 and 8; advisory final 300 |
| `tests/unit/tools/release_workflow/test_invocation/test_invocation_tdd.py` | 200 | Step 8; advisory final 212 |
| `tests/unit/tools/release_workflow/test_git/test_git_tdd.py` | 232 | Steps 6 and 8; advisory final 275 |
| `tests/unit/tools/release_workflow/test_paths/test_paths_tdd.py` | 174 | Step 8; advisory final 195 |
| `tests/unit/tools/release_workflow/test_launchers/test_codepage_tdd.py` | 161 | Steps 4 and 8 regression, unchanged |

Non-Python files involved, without the Python ceiling:

| Existing file | Lines | Planned use |
| --- | --- | --- |
| `.gitignore` | 121 | Step 3: add `/.tools/git-cliff/` |
| `bin/release_workflow.bat` | 79 | Reference for `bin/gcliff.bat`, unchanged |
| `senv.doskey` | 56 | Reference for the alias line shape, unchanged by this item |
| `wiki/reference/aliases-and-launchers.md` | 204 | Step 8: `gcliff` launcher and warm-up |
| `wiki/reference/automation-and-direct-invocation.md` | 180 | Step 8: statuses 2 and 69 for provisioning |
| `wiki/README.md` | 278 | Step 8: link the new reference page |

**What does not exist yet (all new for v0.14.0 git-cliff-provisioning)**:

- `tools/release_workflow/git_cliff/` and every module in it, including the
  committed bundle directory `tools/release_workflow/git_cliff/bundles/2.14.2/`.
- `tools/release_workflow/windows_native.py`,
  `tools/release_workflow/windows_child.py`,
  `tools/release_workflow/windows_guard.py` and
  `tools/release_workflow/lock_records.py`.
- `bin/gcliff.bat` and `bin/gcliff.doskey`.
- `tests/unit/tools/release_workflow/git_cliff_support.py`,
  `git_cliff_children_fake.py`, `git_cliff_harness_fake.py`,
  `native_kernel_fake.py`, `git_cliff_native_checks.py`, every
  `test_git_cliff_*`, `test_windows_native`, `test_windows_child`,
  `test_windows_guard` and `test_lock_records` test leaf, and
  `test_launchers/test_gcliff_source_tdd.py`.
- `wiki/reference/git-cliff-provisioning.md`.
- No `.tools/` directory and no `.release.ini` exist in this checkout.

**Other confirmed technical facts that affect plan shape**:

- **Standard library only**: `[dependency-groups] release = []`; Python
  `>=3.13, <3.14`. `urllib.request`, `ssl`, `hashlib`, `zipfile`, `json`,
  `difflib` and `ctypes` cover the design; `subprocess` is used only for
  `list2cmdline`. No release dependency is added.
- **Default and converter**: `configuration._value` applies a rule's textual
  default through the same `parse` converter as a supplied value, and fixed
  sections of every domain are materialized even when absent. The git-cliff
  rule therefore needs its default text at schema construction, so
  `schemas.py` imports the manifest module at load time; that module imports
  only `dataclasses` and `re`.
- **Empty manifest until admission**: the design admits a pin only by the
  reviewed manifest edit that follows its evidence. Steps 1 to 6 ship an
  empty admitted tuple: the rule has no default, any declared version is
  refused with `tested: none`, and provisioning without a pin raises the
  configuration-stage diagnostic. Unit tests and the native checks before
  admission build synthetic pin tables. Step 7 adds 2.14.2 as the default.
- **Status sites**: `test_codepage_tdd.py` evaluates the single set literal
  inside `bootstrap.main` and the status lines of the two release launchers.
  The new entry kinds keep that literal unique: their pass-through rule uses a
  module-level frozenset outside `main`, and `bin/gcliff.bat` has its own
  source contract instead of joining the release launcher tuple.
- **Process-free suite**: `tools/pytest_plugins/llm_shared_process_audit.py`
  fails a test that creates a process; `tmp_path` is routed to memory by
  `tests/memory_filesystem.py`, so native `CreateFileW` cannot see scenario
  files. Native code is tested through a fake kernel API object, as
  `test_windows_process_tdd.py` already patches `_kernel`; provisioning tests
  inject fake seams. Coverage measures `tools` at 100% and omits `__init__.py`
  files and `tests`.
- **Test class names**: pytest collects classes named `Test*`; the manifest
  record is therefore `AdmittedPin`, not `TestedPin`.
- **Git environment**: `GitExecutionContext` keeps configuration selectors
  (`GIT_CONFIG_GLOBAL`, `GIT_CONFIG_NOSYSTEM`) and removes routing variables;
  `run` has no input stream today. Its controlled environment sets `LC_ALL`,
  `LANG` and `LANGUAGE` to `C`, so Git diagnostics are untranslated.
  `rev-parse --is-inside-work-tree`, checked on 2026-11-15, prints `true` in a
  worktree or a nested folder of one, prints `false` with exit 0 in a bare
  repository or inside a `.git` directory, and exits 128 with `fatal: not a git
  repository` in a plain directory; `paths.discover_project` wraps every
  discovery failure as a generic `ProjectPathError`.
- **Alias files**: macros are single `name="%LLM_SHARED_DIR%\bin\<launcher>.bat" $*`
  lines; existing tests read `senv.doskey` as text and assert exact lines.
- **Legacy comparison inputs**: `tools/dev_workflow` is a submodule at
  `f90bfc6` with `cliff.toml` and `update-changelog.sh`.
- **Existing evidence conventions**: item 2 keeps a recorder module started by
  hand under `tests/unit/tools/release_workflow/` and one committed JSON
  record read by its test; the native check recorder follows that convention,
  created in Step 2 and extended in Steps 4, 5 and 8.

---

## Current test-tree validation snapshot for v0.14.0 git-cliff-provisioning

Existing test packages that v0.14.0 git-cliff-provisioning must not break:

- `tests/unit/tools/release_workflow/` (item 1 and item 2 suites). The schema,
  configuration, bootstrap, invocation, Git and path leaves change as listed
  per step; the operation lock, launcher source, transport, acceptance and
  every version leaf stay unchanged and run as regressions.
- `tests/acceptance/release_workflow/` (readiness acceptance): unchanged, the
  release dependency group stays empty.
- `tests/unit/tools/test_instruction_structure/`: unchanged; it asserts lines
  of `senv.doskey`, which this item does not edit.

New test leaf directories to create, one per production module with topic
files prefixed by the module name, all directly in
`tests/unit/tools/release_workflow/` beside the item 1 and item 2 leaves, with
no extra `git_cliff` level and no groundhog named group; the acceptance and
evidence leaves keep the item 2 naming style. Each has an `__init__.py`
holding a one-line docstring and `# eof`:

- `test_lock_records/` (Step 1).
- `test_git_cliff_manifest/` (Step 1).
- `test_git_cliff_budget/` (Step 1).
- `test_windows_native/` (Step 2).
- `test_windows_child/` (Step 2).
- `test_windows_guard/` (Step 2).
- `test_git_cliff_native_evidence/` (Step 2, extended in Steps 4, 5 and 8).
- `test_git_cliff_cache/` (Step 3).
- `test_git_cliff_cache_lock/` (Step 3).
- `test_git_cliff_network/` (Step 4).
- `test_git_cliff_download_worker/` (Step 4).
- `test_git_cliff_archive/` (Step 4).
- `test_git_cliff_messages/` (Step 5).
- `test_git_cliff_invocation/` (Step 5).
- `test_git_cliff_installation/` (Step 5).
- `test_git_cliff_provisioning/` (Step 5).
- `test_git_cliff_candidates/` (Step 6).
- `test_git_cliff_fixture/` (Step 6).
- `test_git_cliff_comparison/` (Step 6).
- `test_git_cliff_bundle/` (Step 6).
- `test_git_cliff_acceptance/` (Step 7, extended in Step 8).
- `test_git_cliff_launcher/` (Step 8).

---

## Runtime file note for v0.14.0 git-cliff-provisioning plan

- `<LLM_SHARED_DIR>/.tools/git-cliff/<pin>/<triple>/` with `git-cliff.exe`
  and `entry.json`, the lock record `<pin>/<triple>.lock`, and the attempt
  directories `.staging-<pid>-<created>-<rand>/` (holding `owner.json` until
  publication) and `.retired-<pid>-<created>-<rand>/`. The new root
  `.gitignore` entry `/.tools/git-cliff/` covers all of them (Step 3); the
  generic `*.exe`, `*.zip` and `*.lock` patterns already cover some.
- `<LLM_SHARED_DIR>/.tools/git-cliff/evidence/<candidate>/<triple>/` and its
  locks and attempts: the harness's candidate namespace, covered by the same
  entry.
- `tools/release_workflow/git_cliff/bundles/2.14.2/`: committed evidence data,
  not runtime output (`bundle.json` with its `files` and `review` members,
  `cliff.toml`, `trust.2.14.2.json`, `trust.2.7.0.json`). The trust records
  are written once by the harness and never rewritten.
- `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json`:
  committed evidence of the developer-run native checks, with no absolute
  path, user name or host name; first committed in Step 2, refreshed at the
  Step 4, Step 5 and final milestones and whenever a step edits a source file
  it covers.
- The harness's temporary worktree, fixture repository and empty home live in
  a temporary directory outside the repository and are removed when it ends;
  the temporary worktree is also unregistered from Git.

---

## Shared execution command checklist for all v0.14.0 git-cliff-provisioning steps

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
6. When the step edits a source file whose digest the committed native check
   record holds, rerun the recorder for the record's milestone (or the step's
   own milestone when it has one) and commit the refreshed record; the
   validator refuses a stale digest.
7. Count lines after the edits and compare them with the step's line-budget
   checkpoint. A Python file above 650 lines stops the step until the split
   guidance is applied; an advisory estimate exceeded at or below 650 is
   recorded as variance, not missing work.
8. Record evidence and counts in the matching step of the
   [validation plan](plan.v0.14.0.git-cliff-provisioning.validation.md), with
   repository-relative paths only, then follow the normal implementation-check,
   review and authorized commit workflow.

---

## Ready-to-run command templates for all v0.14.0 git-cliff-provisioning steps

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
- Grep checks: `rg -n '<step pattern>' tools/release_workflow tests/unit/tools/release_workflow bin`.
- Ready-to-run command and shared gate loop: run
  `& "<LLM_SHARED_DIR>\bin\prompt_workflow.bat" scope day` and execute the
  printed `ghog` command through the resolved `ghog.bat` launcher (the
  requirement's `- Test group: whole suite` gives `ghog day --whole-suite`
  today; resolve it again at execution time). Follow its repair and restart
  lines until `exit=0`. The default level runs `check.bat` plus affected tests
  and deliberately skips full.
- Final coverage proof (Step 8): `scope day --full=cov`, executed the same way.
- Evidence harness (Step 7, outside pytest, from the project root, network
  required): `& .\venvs\<project venv>\Scripts\python.exe -m tools.release_workflow.git_cliff.harness --bundle tools\release_workflow\git_cliff\bundles\2.14.2 --pin 2.14.2 --baseline 2.7.0`;
  after the user's decision, the same module with
  `--bundle tools\release_workflow\git_cliff\bundles\2.14.2 --review approved`
  (or `rejected`).
- Native check recorder (Steps 2, 4, 5 and 8, outside pytest, from the
  project root, with `step-2`, `step-4`, `step-5` or `final`):
  `& .\venvs\<project venv>\Scripts\python.exe -m tests.unit.tools.release_workflow.git_cliff_native_checks --milestone <milestone> --output tests\unit\tools\release_workflow\test_git_cliff_native_evidence\native_checks.v1.json`.

No step schedules a direct `pytest` or `check.bat` call.

---

## Performance-gate assessment for v0.14.0 git-cliff-provisioning

No Step 0 timeout gate or `xfail` is warranted. The design's budgets are stage
deadlines (30 s socket, D and W, 15 s probe, 60 s metadata), not
responsiveness targets, and the design requires that no test waits in real
time. Each owning step asserts them deterministically with a fake clock and
fake children: the deadline handed to a child, the termination and reap order
at expiry, the poll count of a wait and the budget shown in each message. The
reuse path's cost is fixed by construction (one guard, one record, one hash,
one probe) and is asserted by counting seam calls. Groundhog's lifecycle gate
(0.1-second CPU, one-second wall, setup and teardown included) applies to every
new test, with no duration exclusion.

---

## Shared test architecture for v0.14.0 git-cliff-provisioning

- **Where these tests run**: every test in this plan belongs to llm-shared's
  own development suite, run by groundhog while llm-shared is changed. No
  release, `gcliff` call or consumer build runs it.
- **Simulation only**: no test downloads, opens a socket, creates a job or a
  process, or runs git-cliff or Git. The native layer is exercised through
  `native_kernel_fake.py`, a fake kernel API object that records every call
  and its arguments and can fail at a chosen call; provisioning is exercised
  through injected seams.
- **Test leaves**: one leaf per production module, with topic files prefixed
  by the module name, all directly in `tests/unit/tools/release_workflow/`
  (see the test-tree snapshot above).
- **Shared builders**: three helper modules by concern, each created by the
  step that first needs it, all in `tests/unit/tools/release_workflow/`:
  - `git_cliff_support.py` (Step 3, extended in Step 4) holds a fake clock
    whose `sleep` advances time, declared process states keyed by
    `ProcessIdentity`, an uncontended transition mutex, a synthetic
    `AdmittedPin` for 2.14.2 built from a small generated archive (its real
    size and SHA-256 computed in the test), a fake guard opener over scenario
    files, a write-denying filesystem helper that makes every `mkdir`,
    `rename`, `replace`, `remove`, `rmdir` and write-mode `open` raise
    `PermissionError` and records the attempts, and (Step 4) a fake opener
    with canned bodies;
  - `git_cliff_children_fake.py` (Step 5) holds the fake child launcher that
    plays scripted outcomes (exit, never finishes, parent death at a named
    boundary, unconfirmed end);
  - `git_cliff_harness_fake.py` (Step 6) holds the fake metadata worker with
    canned release metadata, the fake Git runner and the comparison fakes;
  - the native fake kernel `native_kernel_fake.py` (Step 2) stays separate.
- **Parent death without a process**: the fake child launcher models creation
  as one step that yields either no child or a child already in its job, and
  raises a simulated parent death at each boundary the design lists; the test
  then runs a second caller against the left state and asserts what it
  recovers and what it preserves.
- **One scenario per test**: each test declares its cache state (entry, record,
  lock record, attempt directories, process states) directly and asserts one
  call.
- **Property tests**: used where the input domain is large and the function
  pure: pin and budget text grammars, attempt name round trips, record
  encoding round trips and archive member selection. Finite domains (stages,
  retry classes, lifecycle boundaries) use exhaustive parametrization.

---

## Numbered steps for v0.14.0 git-cliff-provisioning

### Step 1. Tested-pin manifest, git-cliff domain and download budget policy

#### Step 1 -- analysis and intent for pins and budgets

Issues to address:

- The common reader reports `[git-cliff]` as an unknown section, and nothing
  names an admitted git-cliff version or its asset identity.
- No code resolves the download budget override or its refused forms.
- Strict JSON record decoding lives privately in `operation_lock.py`, while
  this item adds four record kinds that need the same rules (cache lock
  record, owner file, entry record, trust record).

Fix intent:

- Ship `git_cliff/manifest.py` with frozen `AdmittedPin` records, an empty
  admitted tuple until Step 7, the pin converter and the derived download URL.
- Register the git-cliff domain in `schemas.py` after the version domain.
- Ship `git_cliff/budget.py`, read only when a caller enters provisioning or
  the harness starts.
- Move the strict decoding helpers to `lock_records.py` and import them from
  `operation_lock.py`, keeping its messages.

Expected outcome:

- `[git-cliff] version` parses exact `X.Y.Z` pins and admits only manifest
  versions; with the empty tuple every declared version is refused with
  `tested: none` and an omitted key yields no value.
- The budget policy returns D = 300 and W = 360 when unset, the exact raised
  values from 300 through 3600, and refuses every other form without clamping.
- `operation_lock.py` behavior and messages are unchanged.

Step framing:

- Design link: "The tested-pin manifest and pin resolution", "The download
  budget override", "Time budgets and retries", "Foundation changes required
  by git-cliff provisioning"; design decisions Q01, Q02, Q05, Q18; requirement
  clarifications Q01, Q02, Q11, Q16; plan decisions Q02, Q03, Q11.
- Execution checklist reference: [Shared execution command checklist for all
  v0.14.0 git-cliff-provisioning steps](#shared-execution-command-checklist-for-all-v0140-git-cliff-provisioning-steps).

#### Step 1 -- implementation for pins and budgets

**Files involved**:

- `tools/release_workflow/git_cliff/__init__.py` (new, to be created).
- `tools/release_workflow/git_cliff/manifest.py` (new, to be created).
- `tools/release_workflow/git_cliff/budget.py` (new, to be created).
- `tools/release_workflow/lock_records.py` (new, to be created).
- `tools/release_workflow/schemas.py` (existing, to be updated).
- `tools/release_workflow/operation_lock.py` (existing, to be updated).
- `tools/release_workflow/__init__.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_lock_records/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_lock_records/test_lock_records_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_manifest/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_manifest/test_git_cliff_manifest_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_manifest/test_git_cliff_manifest_pbt.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_budget/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_budget/test_git_cliff_budget_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_budget/test_git_cliff_budget_pbt.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_schemas/test_schemas_tdd.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_configuration/test_configuration_tdd.py` (existing, to be updated).

**Tests first**:

- Record decoder: duplicate keys refused with the caller's label (`Duplicate
  owner field: pid` for the operation lock), a non-object refused, positive
  integers only (booleans and numeric strings refused), present strings only,
  exact key sets. The existing `test_operation_lock` suites run unchanged.
- Manifest: a synthetic tuple with one default admits its version and gives it
  as default; `v2.14.2`, `2.14`, `2.14.2-rc.1`, `latest`, `[space]2.14.2` and
  an empty value are refused with the form message; a well-formed absent version
  is refused with `not a tested git-cliff pin; tested: <list>`; the shipped
  empty tuple refuses with `tested: none` and has no default; the invariant
  check refuses two defaults, a nonempty tuple without a default, a duplicate
  version, an asset or member name not derived from the version and triple, a
  digest that is not 64 lowercase hexadecimal characters, a zero size and an
  empty evidence reference; `download_url` keeps the `v` tag spelling.
- Manifest PBT: integer triples always format to admitted or refused versions
  consistently with the synthetic tuple; any text with a `v`, sign, letter or
  whitespace is refused.
- Budget: unset gives D 300, W 360 and the fixed 30, 15, 60 and 5 s values;
  `300`, `900`, `3600` and `0900` give their exact D and D + 60; empty, `-1`,
  `+600`, `300.5`, `600s`, `[space]600`, `600[space]`, `299`, `3601` and
  `300` written in non-ASCII digits (Arabic-Indic, for example) are refused
  with `BudgetSettingError` naming the variable and its
  range; the lookup is case-insensitive as Windows names are.
- Budget PBT: every integer from 300 through 3600 round-trips; every integer
  outside it and every string with a non-digit character is refused.
- Schemas: the shipped tuple is `(TOOLING_SCHEMA, VERSION_SCHEMA,
  GIT_CLIFF_SCHEMA)`; `git_cliff_domain(pins)` builds a domain whose rule
  carries the synthetic default; ownership of `[git-cliff]` conflicts with no
  family.
- Configuration: `[git-cliff]` is now a known section; `[git-cliff]
  executable=x.exe` and `[tooling] git-cliff=some.exe` are both unknown keys;
  with a synthetic registry, an omitted key yields a defaulted value with the
  source information of any other default and `version = 2.15.0` reports
  `.release.ini [git-cliff] version='2.15.0': not a tested git-cliff pin;
  tested: 2.14.2`; loading configuration imports
  `tools.release_workflow.git_cliff.manifest` and no other `git_cliff`
  module (checked in a fresh `sys.modules` snapshot).

**Classes and behavior**:

- `lock_records.decode_object(content: bytes, *, label: str) -> dict[str, object]`,
  `positive_integer(record, key, *, label)`, `text(record, key, *, label)`:
  the strict JSON rules `operation_lock` uses today. `operation_lock._record`,
  `_integer` and `_text` delegate to them with `label="owner"`.
- `manifest.AdmittedPin` (frozen): `version`, `default`, `triple`, `asset`,
  `size`, `sha256`, `member`, `evidence` (repository-relative bundle
  directory). `PLATFORM_TRIPLE = "x86_64-pc-windows-msvc"`.
  `ADMITTED_PINS: tuple[AdmittedPin, ...] = ()`, validated at import by
  `validate_pins`. `default_version(pins) -> str | None`,
  `admitted(version, pins) -> AdmittedPin`, `parse_pin(raw, *, pins) -> str`
  (`re.fullmatch(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)")` then
  admission), `download_url(pin)` returning
  `https://github.com/orhun/git-cliff/releases/download/v<version>/<asset>`.
- `schemas.git_cliff_domain(pins) -> DomainSchema`: one fixed section
  `git-cliff` with `ValueRule("version", parse=partial(manifest.parse_pin,
  pins=pins), default=manifest.default_version(pins))`.
  `GIT_CLIFF_SCHEMA = git_cliff_domain(manifest.ADMITTED_PINS)`, appended to
  `SHIPPED_SCHEMAS`. The module docstring records the manifest import.
- `budget.BudgetPolicy` (frozen): `download`, `wait`, `socket = 30`,
  `probe = 15`, `metadata = 60`, `retry_delay = 5`, `source` (for messages).
  `DOWNLOAD_BUDGET_VARIABLE = "LLM_SHARED_GIT_CLIFF_DOWNLOAD_TIMEOUT_SECONDS"`.
  `resolve_budget(environment: Mapping[str, str]) -> BudgetPolicy` accepts
  `value.isascii() and value.isdigit()` within 300 through 3600, else raises
  `BudgetSettingError` (`exit_code = 2`).
- `git_cliff/__init__.py`: docstring listing the modules; imports nothing.

**Completion criteria**:

- The command printed by `pw scope day` reports the objective (`exit=0`) in
  the current effort scope.
- `rg -n 'import' tools/release_workflow/git_cliff/manifest.py` shows only
  standard-library imports.
- `rg -n 'json.loads' tools/release_workflow/operation_lock.py` finds no match
  (decoding moved to `lock_records.py`).
- `rg -n 'getenv|environ' tools/release_workflow/git_cliff` finds no read of
  the budget variable outside `budget.py`.
- The import-freedom test passes.

#### Step 1 -- addendums for pins and budgets

Line-budget checkpoint:

- [ ] `tools/release_workflow/git_cliff/manifest.py`: before 0; below-550 safe; repository ceiling <= 650; expected 110 (advisory).
- [ ] `tools/release_workflow/git_cliff/budget.py`: before 0; below-550 safe; ceiling <= 650; expected 80 (advisory).
- [ ] `tools/release_workflow/lock_records.py`: before 0; below-550 safe; ceiling <= 650; expected 70 (advisory).
- [ ] `tools/release_workflow/schemas.py`: before 220; below-550 safe; ceiling <= 650; expected +25 (advisory).
- [ ] `tools/release_workflow/operation_lock.py`: before 261; below-550 safe; ceiling <= 650; expected -25 (advisory).
- [ ] New test files: before 0; ceiling <= 650; expected 80, 180, 60, 130 and 50 (advisory).
- [ ] Updated test files: before 151 and 256; below-550 safe; ceiling <= 650; expected +20 and +30 (advisory).

Split guidance:

- None expected. If the manifest test file passes 650, move the invariant
  cases into `test_git_cliff_manifest_invariants_tdd.py`.

Full workflow timing run readiness:

- `ghog single` on the Step 1 test files and `test_operation_lock`, then the
  command printed by `pw scope day`.

Time-gated status for Step 1:

- No perf gate is affected; the lifecycle gate applies to the new tests.

---

### Step 2. Contained Windows children and the use guard

#### Step 2 -- analysis and intent for the Windows layer

Issues to address:

- The engine can probe process identities and serialize transitions, but it
  cannot create a child inside a job from its creation, list the only handles
  the child inherits, record it before it runs or end it at a deadline.
- Nothing holds an executable against replacement while a child runs.
- `subprocess.Popen` closes the primary thread handle at once and supports only
  `handle_list`, so it cannot provide the lifecycle.

Fix intent:

- Ship `windows_native.py`: the ctypes structures, constants and the kernel
  loader with its signatures, shared by the child and guard modules.
- Ship `windows_child.py`: the platform baseline check, a parent-only
  kill-on-close job per attempt or run, creation through `CreateProcessW` with
  `CREATE_SUSPENDED`, `EXTENDED_STARTUPINFO_PRESENT` and a `STARTUPINFOEX`
  carrying `PROC_THREAD_ATTRIBUTE_JOB_LIST` and
  `PROC_THREAD_ATTRIBUTE_HANDLE_LIST`, an optional recording callback before
  `ResumeThread`, a deadline wait, a job-wide teardown whose end is confirmed
  before the output pipes are joined, and the console interrupt filter of the
  launcher.
- Ship `windows_guard.py`: the use guard (`CreateFileW` with `GENERIC_READ`
  and `FILE_SHARE_READ` only) with hashing through a duplicated handle.
- Create the developer-run native check recorder with the Step 2 due set,
  commit its first record and the test that validates it.

Expected outcome:

- No code path creates a child outside its job or falls back to
  `subprocess` or to create-then-assign; every failure before resume leaves
  no running child.
- No path blocks on the output pipes before every job member has ended, so a
  descendant holding a pipe write end cannot defeat a deadline.
- A returned outcome always means a confirmed end; an unconfirmed end raises a
  distinct error after which no caller cleans up.
- Every branch of the native layer is covered through the fake kernel.
- The committed native record passes the Step 2 due set against the current
  sources, so Steps 3 to 8 build on a native layer proven on a real kernel.

Step framing:

- Design link: "Child process lifecycle", "Deadline enforcement", "Reuse check
  and the use guard", "Foundation changes required by git-cliff
  provisioning", "Testing approach under the process-free policy"; design
  decisions Q07, Q10, Q17; the confirmed facts on job objects, process
  attributes, nested jobs and `subprocess`; plan decisions Q01, Q04, Q05,
  Q06, Q07, Q14.
- Execution checklist reference: [Shared execution command checklist for all
  v0.14.0 git-cliff-provisioning steps](#shared-execution-command-checklist-for-all-v0140-git-cliff-provisioning-steps).

#### Step 2 -- implementation for the Windows layer

**Files involved**:

- `tools/release_workflow/windows_native.py` (new, to be created).
- `tools/release_workflow/windows_child.py` (new, to be created).
- `tools/release_workflow/windows_guard.py` (new, to be created).
- `tests/unit/tools/release_workflow/native_kernel_fake.py` (new, to be created).
- `tests/unit/tools/release_workflow/git_cliff_native_checks.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_windows_native/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_windows_native/test_windows_native_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_windows_child/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_windows_child/test_windows_child_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_windows_child/test_windows_child_faults_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_windows_guard/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_windows_guard/test_windows_guard_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py` (new, to be created).

**Tests first**:

- Native declarations (`test_windows_native_tdd.py`): the x64 field layouts
  and sizes of the declared structures, the constants, and the default kernel
  loader called through a fake loader that records the `argtypes`, `restype`
  and `errcheck` of every declared function; no test calls the operating
  system.

- Platform: Windows 10 and Windows Server 2016 (`platform_version` 10.0) on
  x64 pass; 6.3 (Windows 8.1 or Server 2012 R2) and a 32-bit or ARM machine
  raise `PlatformError` with the baseline remedy, before any job or child.
- Creation order, read from the fake kernel's call log: job created and
  configured with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` and a non-inheritable
  handle; attribute list sized, initialized and updated with exactly the job
  list and the handle list; listed handles made inheritable just before
  `CreateProcessW` and reset just after it; `CreateProcessW` called with
  `bInheritHandles` true and both flags; the recording callback called with
  the child's PID and creation time before `ResumeThread`; the attribute list
  deleted on every path.
- Handle list contents: standard handles only, or standard handles plus the
  guard handle when the request carries one; engine stdin is a `NUL` handle;
  captured streams are pipe write ends; passthrough streams are the parent's
  standard handles.
- Setup and creation faults (one test per failing call, each asserting that no
  `ResumeThread` happened, that no other creation path ran and that every
  handle created so far is closed): job creation, job configuration, pipe
  creation, attribute list sizing, initialization, each update, and
  `CreateProcessW` returning 0 (including `ERROR_ACCESS_DENIED` for a refused
  nesting) raise `ContainmentError`.
- Pre-resume faults: a failing `GetProcessTimes`, a recording callback that
  raises and a failing `ResumeThread` each tear the job down, confirm the end
  and only then raise `ContainmentError`; the call log shows no resume before
  the failure.
- Normal exit and deadline: an exit within the deadline returns the root's own
  status and the captured bytes; expiry returns a timed-out outcome; both
  paths call `TerminateJobObject`, wait on the root and read an
  `ActiveProcesses` count of 0 before the reader threads are joined.
- Descendant holding a pipe: the fake kernel declares a descendant that keeps
  the stdout write end and whose pipe reaches end of file only when the job is
  terminated; after a normal root exit and after expiry, the call returns, the
  call log orders `TerminateJobObject` before the join, and the root's status
  is kept. The parent closes its own copies of the pipe write ends right after
  `CreateProcessW`.
- Unconfirmed end: a failing `TerminateJobObject` while a declared descendant
  still holds a captured pipe, a `WAIT_FAILED` root wait and a failing
  accounting query each raise `UnconfirmedEndError` promptly with the child
  identity and the failing call. The test asserts that the readers are daemon
  threads reading native handles into private buffers, that no join and no
  `CloseHandle` of the job, process, thread or pipe handles happened, and that
  those handles now belong to the process-lifetime owner `RETAINED`. A failing
  `GetProcessTimes` followed by a failing teardown raises it with
  `identity=None` and the PID from `CreateProcessW`, after no `ResumeThread`
  and no recording callback. The fake pipe's blocking read waits on an event
  the test sets at teardown, so no reader outlives its test.
- Retained guard: `UseGuard.retain()` hands the guard to `RETAINED`, after
  which `close()` and the context manager's exit leave the handle open.
- Console filter: `ignore_console_interrupts()` registers a handler routine
  that returns true for `CTRL_C_EVENT` and `CTRL_BREAK_EVENT`, never the null
  routine (whose ignore flag children would inherit), keeps the ctypes
  callback referenced while it is registered, and removes it on a normal exit
  and when the guarded block raises.
- Guard: `open_guard` calls `CreateFileW` with `GENERIC_READ`,
  `FILE_SHARE_READ`, `OPEN_EXISTING` and no security attributes; a missing
  file raises `FileNotFoundError`; a sharing violation raises `OSError` with
  the Windows error; `sha256_and_size()` reads through a duplicated handle and
  closes only that duplicate; `close()` is idempotent.
- Native evidence validator (`test_git_cliff_native_evidence_tdd.py`): the
  record names its milestone (`step-2`, `step-4`, `step-5` or `final`), and
  for every check due at that milestone (the due sets are cumulative) it
  requires outcome `passed`, an observation equal to its expected
  observation, a duration within its bound, the recorded commit, and source
  digests equal to the current SHA-256 of every repository file the check
  exercises; host facts (Windows build, architecture) are present and no
  absolute path, user or host name appears. Negative records built in memory
  are each refused: an unknown milestone, a missing due check, `failed`,
  `timed-out` and `skipped` outcomes, an observation differing from its
  expectation, a duration over its bound and a stale source digest.
- PBT: not needed in this step; the native call sequences are finite and
  parametrized exhaustively.

**Classes and behavior**:

- `windows_native`: `STARTUPINFOEXW`, `PROCESS_INFORMATION`,
  `JOBOBJECT_EXTENDED_LIMIT_INFORMATION`,
  `JOBOBJECT_BASIC_ACCOUNTING_INFORMATION` and the constants the lifecycle
  and the guard use; `kernel(loader=None)` returns the declared `kernel32`
  functions and caches them. `windows_child` and `windows_guard` call it when
  their `api` argument is `None`; tests pass the fake kernel instead.

- `windows_child.require_supported_platform(version=sys.getwindowsversion(),
  machine=platform.machine())`: major `platform_version` 10 or later and an
  x64 machine, else `PlatformError`.
- `windows_child.ChildRequest` (frozen): `executable`, `arguments`, `cwd`,
  `environment` (`None` inherits), `stdin` (`"closed"` or `"inherit"`),
  `output` (`"capture"` or `"inherit"`), `inherited` (guard handles),
  `deadline` (seconds or `None`), `record` (`Callable[[ProcessIdentity], None]
  | None`). The command line is `subprocess.list2cmdline([executable,
  *arguments])`; the environment block is built in sorted, case-insensitive
  order.
- `windows_child.ChildOutcome` (frozen): `status`, `stdout`, `stderr`,
  `timed_out`, `identity`. A returned outcome always means that every member of
  the child's job has ended.
- `windows_child.run_contained(request, *, api=None) -> ChildOutcome`: the
  design lifecycle, expanded into the following seven implementation phases,
  in this order on every path:
  1. Setup: create the job with a non-inheritable handle and
     `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`, the capture pipes (read ends never
     inheritable), the `NUL` handle for a closed stdin and the attribute list.
     A failure closes what was created and raises `ContainmentError`; no child
     exists.
  2. Creation: make the listed handles inheritable, call `CreateProcessW`
     suspended with the attribute list, reset inheritance, delete the
     attribute list, then close the parent's copies of the pipe write ends and
     of the `NUL` handle. `CreateProcessW` returning 0 closes the job and
     raises `ContainmentError`; no child exists.
  3. Pre-resume: read the child's identity, call the recording callback when
     the request has one, then `ResumeThread`. A failure in any of the three
     runs the teardown of step 5 and raises `ContainmentError` once the end is
     confirmed; the child never ran. If that teardown is itself unconfirmed,
     step 7 applies; when the identity lookup was the failing call, the error
     carries `identity=None`, the child stays suspended, unrecorded and never
     resumed, and nothing records it as recoverable.
  4. Wait: `WaitForSingleObject` on the root within the deadline, while two
     daemon reader threads drain the native pipe read handles with `ReadFile`
     into private byte buffers (no Python file object wraps a pipe); a
     signaled root gives its status through `GetExitCodeProcess`, expiry marks
     the outcome timed out. The readers are not joined here.
  5. Job-wide teardown on every path after creation: `TerminateJobObject` ends
     every remaining member (the root on expiry, a descendant left behind
     after a normal root exit), then the parent waits on the root handle and
     polls `JobObjectBasicAccountingInformation` through the injected sleep
     until `ActiveProcesses` is 0. A successful termination call followed by
     that zero count confirms the end. As the design orders, this reap has no
     budget of its own once termination has succeeded.
  6. Drain: after the confirmed end, join the readers (every write end holder
     has ended, so both pipes reach end of file), close the job, process and
     thread handles and return the outcome with the root's status.
  7. Unconfirmed end: a failing `TerminateJobObject`, root wait or accounting
     query moves the job, process, thread and pipe read handles into
     `RETAINED` and raises `UnconfirmedEndError`. No reader is joined and none
     of those handles is closed by any `finally`, context manager or `close()`
     path. The daemon readers cannot hold interpreter shutdown, so the parent
     process can still end normally; its end closes the retained job handle,
     and kill-on-close then terminates the members. No caller removes
     staging, releases a lock record or closes a guard on this error (Steps 3
     and 5).
- `windows_child.RETAINED`: the process-lifetime owner of unresolved native
  resources, a module-level registry that only appends handles and guards and
  never closes them; the operating system closes them when the process ends.
  The guarantee does not depend on the exception object staying reachable.
- `windows_child.ContainmentError(OSError)`, its subclass
  `UnconfirmedEndError` (carrying `pid`, `identity: ProcessIdentity | None`
  and the failing call) and `PlatformError(OSError)`, each with the stage name
  the messages module maps to a remedy.
- `windows_child.is_process_in_job(process_handle) -> bool`, used only by the
  native check recorder.
- `windows_guard.UseGuard`: `path`, `handle`, `sha256_and_size()`, `close()`,
  `retain()`, context manager; a retained guard is registered in `RETAINED`
  and its `close()` is a no-op. `open_guard(path, *, api=None) -> UseGuard`.
- `git_cliff_native_checks.py`: started by hand, never imported by a test;
  `--milestone` selects the cumulative due set and `--output` the record.
  Each check bounds its own run with a timeout, ends every process it started
  and writes its identifier, outcome, expected and observed observations,
  bound, duration, the commit and the SHA-256 of each source file it
  exercises. The Step 2 due set runs on temporary paths outside
  `.tools/git-cliff/` and on stand-in children, never on the cache:
  `IsProcessInJob` before resume; a suspended child ending when its parent is
  killed; a creation refused by the job of a helper parent limited to one
  active process, leaving no process (on Windows 11 build 26200 a job with UI
  limits did not refuse the nesting, so the user chose this refusal on
  2026-11-18);
  kill-on-close of a running child after its parent is killed; a root that
  exits while a descendant keeps its stdout open, returning within the
  check's bound with the descendant ended; a helper parent whose
  `TerminateJobObject` call is made to fail (through an injected `api`
  wrapper around the real kernel and a real kill-on-close job) while a
  descendant holds its captured pipe, which must still exit normally, after
  which its descendant ends through kill-on-close (the recorder runs the
  helper inside its own bounded job and ends it if it hangs); and the
  inherited guard refusing a rename while a child runs and while the guard is
  held between its opening and the child start. A check that fails, times out
  or cannot run is recorded as such, and the validator then refuses the
  record, which blocks the step.

**Completion criteria**:

- The command printed by `pw scope day` reports the objective (`exit=0`) in
  the current effort scope.
- `rg -n 'subprocess\.(Popen|run|call)|AssignProcessToJobObject' tools/release_workflow/windows_native.py tools/release_workflow/windows_child.py tools/release_workflow/windows_guard.py`
  finds no match.
- `rg -n 'SetConsoleCtrlHandler' tools/release_workflow` shows only the
  handler-routine registration and removal.
- `rg -n 'TerminateJobObject|\.join\(' tools/release_workflow/windows_child.py`
  shows the reader join only after the teardown helper.
- Coverage of the three modules is 100% through the fake kernel and the fake
  loader.
- `native_checks.v1.json` holds milestone `step-2`, and its validator accepts
  it for the current sources.

#### Step 2 -- addendums for the Windows layer

Line-budget checkpoint:

- [ ] `tools/release_workflow/windows_native.py`: before 0; below-550 safe; repository ceiling <= 650; expected 180 (advisory).
- [ ] `tools/release_workflow/windows_child.py`: before 0; below-550 safe; ceiling <= 650; expected 360 with the teardown, pre-resume and retention paths (advisory).
- [ ] `tools/release_workflow/windows_guard.py`: before 0; below-550 safe; ceiling <= 650; expected 120 (advisory).
- [ ] `tests/unit/tools/release_workflow/native_kernel_fake.py`: before 0; ceiling <= 650; expected 310 with declared descendants and pipes (advisory).
- [ ] `tests/unit/tools/release_workflow/git_cliff_native_checks.py`: before 0; ceiling <= 650; expected 190 with the Step 2 due set (advisory).
- [ ] New test files: before 0; ceiling <= 650; expected 90 (native), 280, 380 and 140 (child and guard) and 130 (evidence validator) (advisory).
- [ ] `native_checks.v1.json`: non-Python data, no Python ceiling.

Split guidance:

- None expected: the declarations live in `windows_native.py` from the
  start, so `windows_child.py` stays below the risk band.

Full workflow timing run readiness:

- `ghog single` on the Step 2 test files and `test_windows_process`, then the
  native check recorder by hand with `--milestone step-2`, then the command
  printed by `pw scope day`.

Time-gated status for Step 2:

- No perf gate is affected; deadlines are asserted through the fake kernel's
  wait results, not real time.

---

### Step 3. Cache layout, entry record, reuse check and the cache lock

#### Step 3 -- analysis and intent for the cache

Issues to address:

- Nothing computes the fixed path of a pin, records what was published or
  checks an entry before use.
- No lock serializes provisioning of one version and platform, waits for a
  holder with a bound, or recovers a holder proven gone.
- `.tools/git-cliff/` is not ignored.

Fix intent:

- Ship `git_cliff/cache.py`: the layout below `<tooling_root>/.tools/git-cliff/`
  with production and evidence namespaces, attempt directory names carrying
  the owner's PID, creation time and a random token, the entry record and the
  owner file, and the lock-free reuse check taking a guard opener and a probe.
- Ship `git_cliff/cache_lock.py`: the lock record under a transition mutex
  named from the cache directory's file identity, namespace, version and
  triple; the bounded wait; child recording; owner-aware recovery of the
  record and of attempt directories.
- Add `/.tools/git-cliff/` to the root `.gitignore`, in the first step whose
  code writes under that path.

Expected outcome:

- Reuse stops at the first failing check, writes nothing and takes no lock.
- A lock is recovered only when its owner and every recorded child are
  `DEAD`; an `ALIVE` or `UNKNOWN` actor keeps the record and its attempt
  directory however long the wait lasts, and an abandoned mutex authorizes
  nothing.

Step framing:

- Design link: "Cache layout and the local integrity record", "Provisioning
  lock, contention and recovery", "Ignore rule"; design decisions Q03, Q04,
  Q07, Q12; requirement clarifications Q03, Q04, Q05, Q06, Q14; plan
  decisions Q01, Q02, Q11, Q12.
- Execution checklist reference: [Shared execution command checklist for all
  v0.14.0 git-cliff-provisioning steps](#shared-execution-command-checklist-for-all-v0140-git-cliff-provisioning-steps).

#### Step 3 -- implementation for the cache

**Files involved**:

- `tools/release_workflow/git_cliff/cache.py` (new, to be created).
- `tools/release_workflow/git_cliff/cache_lock.py` (new, to be created).
- `.gitignore` (existing, to be updated).
- `tests/unit/tools/release_workflow/git_cliff_support.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_cache/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_cache/test_git_cliff_cache_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_cache/test_git_cliff_cache_pbt.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_cache_lock/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_cache_lock/test_git_cliff_cache_lock_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_cache_lock/test_git_cliff_cache_lock_recovery_tdd.py` (new, to be created).

**Tests first**:

- Layout: the production entry path is
  `<root>/.tools/git-cliff/2.14.2/x86_64-pc-windows-msvc/git-cliff.exe`; the
  evidence namespace lives under `evidence/`; a production layout never
  resolves into `evidence/` for any admitted version; attempt names parse
  back to their owner and refuse a malformed name.
- Ignore rule: the root `.gitignore` holds the exact line `/.tools/git-cliff/`.
- Entry record: encoding and strict decoding of schema 1 with every field;
  a record naming another version or triple, an extra or missing field, or a
  duplicate key is invalid.
- Reuse check, in order: a missing executable makes the entry absent; a
  missing or unparsable `entry.json` is invalid without hashing or probing; a
  size or digest mismatch is invalid without probing; a probe whose first
  line is not `git-cliff <pin>` is invalid; a valid entry returns the open
  guard. Each ordinary failure closes the guard. A probe raising
  `UnconfirmedEndError` instead retains the guard (`UseGuard.retain()`) before
  the error propagates, so no invocation needs to exist for the guard to stay
  open; the test asserts that the caller's cleanup leaves the handle open and
  that no write happened. Under the write-denying helper a valid reuse
  succeeds with no recorded write attempt.
- Cache PBT: attempt names round-trip for positive PIDs, creation times and
  tokens; entry records round-trip for generated digests and sizes.
- Lock: acquisition publishes a complete record without replacement; a live
  holder makes the caller print one waiting line with the holder's PID, start
  time and the caller's W, poll every 250 ms of fake time and fail at W with
  `LockWaitError` naming the lock path, the owner and the remedy; a holder that
  releases mid-wait lets the caller acquire; `record_child` appends an identity
  under the mutex; `release` removes only this caller's record, and after
  `retain_record()` removes nothing.
- Recovery: an owner `DEAD` with every child `DEAD` is recovered inside the
  mutex; an owner `DEAD` with one child `ALIVE` or `UNKNOWN` is kept; an owner
  `UNKNOWN` beyond W is kept and the waiter fails; a mutex acquired abandoned
  while the owner is `ALIVE` keeps the record; `.staging-` and `.retired-`
  directories are removed only when their name owner and every child of their
  owner file are `DEAD`, and only by a lock holder; a waiter's deadline is
  never reset by a holder change.

**Classes and behavior**:

- `cache.CacheLayout(tooling_root, namespace="production")`: `root`,
  `version_dir(pin)`, `entry_dir(pin)`, `executable(pin)`, `record(pin)`,
  `lock_path(pin)`, `attempt_dir(pin, kind, identity, token)` and
  `parse_attempt(name) -> Attempt | None` for `staging` and `retired`.
- `cache.EntryRecord` (frozen): `schema`, `version`, `triple`, `asset`,
  `asset_sha256`, `executable_sha256`, `executable_size`, `provisioned`;
  `encode()` and `decode(content)` through `lock_records`.
- `cache.OwnerFile` (frozen): `owner` and `children`; written as
  `owner.json` in a staging directory and removed before publication.
- `cache.check_entry(layout, pin, *, open_guard, probe) -> EntryCheck`, where
  `EntryCheck` is either a valid entry holding the guard and the record or an
  invalid or absent result with its reason. On `UnconfirmedEndError` from the
  probe it calls `guard.retain()` and lets the error propagate.
- `cache_lock.CacheLock(layout, pin, *, caller, probe=process_state,
  current=current_identity, mutex=transition_mutex, clock, sleep)`:
  `acquire(wait_seconds, on_wait) -> CacheLock`, `record_child(identity)`,
  `release()`, `retain_record()`, `recover_attempts(pin)`. After
  `retain_record()`, used only on an unconfirmed end, `release()` leaves the
  record in place, so a `finally` path cannot remove it. Recovery keeps its
  rule: the owner and every recorded child must be `DEAD`. The mutex name is
  `Global\llm-shared-git-cliff-<dev>-<ino>-<namespace>-<version>-<triple>`
  from `os.stat` of the cache root, created with its parents on first
  provisioning.
- `cache_lock.LockWaitError(OSError)` carrying the lock path, the owner
  identity and start time.

**Completion criteria**:

- The command printed by `pw scope day` reports the objective (`exit=0`) in
  the current effort scope.
- `rg -n '\.tools/git-cliff/' .gitignore` shows the entry.
- `rg -n 'getmtime|st_mtime|age' tools/release_workflow/git_cliff/cache_lock.py`
  finds no age-based recovery.
- `rg -n 'subprocess|Popen' tests/unit/tools/release_workflow/git_cliff_support.py`
  finds no process start.

#### Step 3 -- addendums for the cache

Line-budget checkpoint:

- [ ] `tools/release_workflow/git_cliff/cache.py`: before 0; below-550 safe; repository ceiling <= 650; expected 260 (advisory).
- [ ] `tools/release_workflow/git_cliff/cache_lock.py`: before 0; below-550 safe; ceiling <= 650; expected 290 (advisory).
- [ ] `tests/unit/tools/release_workflow/git_cliff_support.py`: before 0; ceiling <= 650; expected 230 (advisory).
- [ ] New test files: before 0; ceiling <= 650; expected 230, 60, 250 and 220 (advisory).
- [ ] `.gitignore`: 121 lines; non-Python, +2.

Split guidance:

- If `cache.py` would pass 650, move `check_entry` and `EntryCheck` into
  `git_cliff/reuse.py`.

Full workflow timing run readiness:

- `ghog single` on the Step 3 test files, then the command printed by
  `pw scope day`.

Time-gated status for Step 3:

- No perf gate is affected; the wait is asserted in fake-clock polls.

---

### Step 4. Network client, download worker, verification and extraction

#### Step 4 -- analysis and intent for the download

Issues to address:

- Nothing downloads a release asset through the standard proxy and the
  Windows certificate store, or stops at the first byte beyond the expected
  size.
- A `urllib` timeout bounds only one socket operation, so the download must
  run in a worker process the parent can end at the deadline, started with
  the same runtime.
- Nothing extracts one named member under a fixed name.

Fix intent:

- Ship `git_cliff/network.py`: the opener from `getproxies()` and
  `ssl.create_default_context()`, archive streaming with a size cap and
  SHA-256, the release metadata fetch, and the retry classification.
- Ship `git_cliff/download_worker.py`: the worker main for one archive attempt
  or one metadata lookup, its argument vector builder, and its one-line JSON
  outcome on its own standard output (a pipe the parent reads).
- Add the internal `git-cliff-worker` entry kind to the bootstrap.
- Ship `git_cliff/archive.py`: the digest check from the staged file and the
  single-member extraction.
- Extend the native check recorder with the Step 4 due set and commit the
  refreshed record.

Expected outcome:

- One attempt reports `ok`, `retryable` (connection error, reset, HTTP 429 or
  5xx) or `fatal` (another HTTP 4xx, size overflow), and a `Retry-After`
  header changes nothing.
- Extraction writes only `git-cliff.exe` in staging, from the manifest member,
  with its uncompressed size checked and its bytes hashed.

Step framing:

- Design link: "Download, verification and extraction", "Deadline
  enforcement", "Time budgets and retries"; design decisions Q01, Q06, Q08;
  requirement clarifications Q07, Q15; plan decisions Q06, Q10, Q11, Q15.
- Execution checklist reference: [Shared execution command checklist for all
  v0.14.0 git-cliff-provisioning steps](#shared-execution-command-checklist-for-all-v0140-git-cliff-provisioning-steps).

#### Step 4 -- implementation for the download

**Files involved**:

- `tools/release_workflow/git_cliff/network.py` (new, to be created).
- `tools/release_workflow/git_cliff/download_worker.py` (new, to be created).
- `tools/release_workflow/git_cliff/archive.py` (new, to be created).
- `tools/release_workflow/bootstrap.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/git_cliff_support.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_git_cliff_network/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_network/test_git_cliff_network_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_download_worker/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_download_worker/test_git_cliff_download_worker_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_archive/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_archive/test_git_cliff_archive_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_archive/test_git_cliff_archive_pbt.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/git_cliff_native_checks.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py` (existing, to be updated).

**Tests first**:

- Opener: built from a declared `getproxies()` result and a declared default
  context; certificate verification is never turned off (no `CERT_NONE`, no
  `check_hostname = False`).
- Streaming, against a fake opener: canned bytes give the right size and
  digest; a redirect to `release-assets.githubusercontent.com` is followed; a
  body longer than the expected size stops at the first extra byte with
  `SizeOverflowError` and writes no more; a short body is reported for the
  digest check; a stalled read raises the socket timeout; connection errors,
  resets, 429 and 500 to 599 classify as retryable, 403, 404 and 410 as fatal.
- Worker: argument parsing for both modes; one JSON line on its stdout with
  the outcome, received size and digest, nothing on stderr for success;
  metadata mode writes no file; the socket timeout is
  `min(30, remaining budget)`; internal statuses 0, 75 and 65 map to `ok`,
  `retryable` and `fatal`.
- Bootstrap: `--entry-kind git-cliff-worker` passes readiness, imports
  `tools.release_workflow.git_cliff.download_worker` and returns its status
  unchanged; the release kinds keep `{0, 1, 2, 3}`; the cross-site status
  contract of `test_codepage_tdd.py` still passes.
- Archive: the staged digest is recomputed from the file and compared with the
  pin; a mismatch raises the verification error; only the manifest member is
  read and written as `git-cliff.exe`; an uncompressed size different from the
  directory entry, a missing member and an archive that is not a ZIP raise
  the extraction error; archives with `../`, absolute and drive-letter member
  names beside the member never create those paths.
- Archive PBT: for generated member name lists that include the manifest
  member, only `git-cliff.exe` appears in staging.
- Native evidence: the `step-4` milestone requires the Step 2 due set plus
  the stalled-endpoint check.

**Classes and behavior**:

- `network.build_opener(*, proxies=None, context=None)`;
  `network.stream_archive(opener, url, target, *, expected_size,
  socket_timeout) -> Received` (`size`, `sha256`);
  `network.fetch_metadata(opener, url, *, socket_timeout) -> bytes`;
  `network.classify(error) -> Literal["retryable", "fatal"]`.
- `download_worker.WorkerRequest` (frozen): `mode`, `url`, `target`,
  `expected_size`, `remaining`. `worker_arguments(request) -> list[str]` and
  `worker_command(runtime, tooling_root, request) -> tuple[Path, list[str]]`
  (`-I -X utf8 <tooling_root>\tools\release_workflow\bootstrap.py
  --entry-kind git-cliff-worker -- ...`). `main(arguments) -> int`.
- `bootstrap`: `entry` accepts `git-cliff-worker`; a module-level
  `_ENGINES` mapping selects the module per kind and a module-level
  `_UNNORMALIZED_KINDS` frozenset lets the worker status pass unchanged, so
  `main` keeps its single set literal.
- `archive.verify_archive(path, pin) -> None` and
  `archive.extract_member(path, pin, target_dir) -> tuple[str, int]`.
- `git_cliff_native_checks.py --milestone step-4` adds worker termination at
  its deadline against a local endpoint that accepts and never answers, with
  a disposable recorded staging directory under a temporary tooling root.

**Completion criteria**:

- The command printed by `pw scope day` reports the objective (`exit=0`) in
  the current effort scope.
- `rg -n 'CERT_NONE|check_hostname|_create_unverified_context|Retry-After' tools/release_workflow/git_cliff`
  shows no verification bypass and no header use.
- `rg -n 'extractall|extract\(' tools/release_workflow/git_cliff/archive.py`
  finds no whole-archive extraction.
- `rg -n 'api.github.com' tools/release_workflow/git_cliff/network.py tools/release_workflow/git_cliff/download_worker.py`
  finds nothing outside the metadata mode's caller-supplied URL.
- `native_checks.v1.json` holds milestone `step-4`, and its validator accepts
  it for the current sources.

#### Step 4 -- addendums for the download

Line-budget checkpoint:

- [ ] `tools/release_workflow/git_cliff/network.py`: before 0; below-550 safe; repository ceiling <= 650; expected 190 (advisory).
- [ ] `tools/release_workflow/git_cliff/download_worker.py`: before 0; below-550 safe; ceiling <= 650; expected 150 (advisory).
- [ ] `tools/release_workflow/git_cliff/archive.py`: before 0; below-550 safe; ceiling <= 650; expected 80 (advisory).
- [ ] `tools/release_workflow/bootstrap.py`: before 201; below-550 safe; ceiling <= 650; expected +25 (advisory).
- [ ] `tests/unit/tools/release_workflow/git_cliff_support.py`: before about 230; ceiling <= 650; expected +60 (advisory).
- [ ] New test files: before 0; ceiling <= 650; expected 220, 170, 160 and 50 (advisory).
- [ ] `tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py`: before 212; ceiling <= 650; expected +35 (advisory).
- [ ] `tests/unit/tools/release_workflow/git_cliff_native_checks.py`: before about 190; ceiling <= 650; expected +40 (advisory).
- [ ] `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py`: before about 130; ceiling <= 650; expected +5 (advisory).

Split guidance:

- None expected.

Full workflow timing run readiness:

- `ghog single` on the Step 4 test files and `test_launchers`, then the
  native check recorder by hand with `--milestone step-4`, then the command
  printed by `pw scope day`.

Time-gated status for Step 4:

- No perf gate is affected; stalls are fake reads raising the socket timeout.

---

### Step 5. Provisioning service, invocation object and failure contract

#### Step 5 -- analysis and intent for provisioning

Issues to address:

- The primitives of Steps 1 to 4 are not composed into the design's target
  flow, and no object starts git-cliff under one environment policy with the
  guard and the job.
- No message, diagnostic or remedy exists, and engine callers have no entry
  point or status.

Fix intent:

- Ship `git_cliff/messages.py`: the stages, remedies, `ProvisioningError`
  (status 2 for engine callers) and the three standard-error lines.
- Ship `git_cliff/invocation.py`: `GitCliffInvocation` with the engine and
  passthrough policies.
- Ship `git_cliff/installation.py`: the lock-held installation (attempts with
  one retry inside D, digest check, extraction, recorded staging probe, entry
  record, retirement of an invalid entry, publication).
- Ship `git_cliff/provisioning.py`: the seams, the outer flow (budget, platform,
  guard, reuse, lock, recheck, recovery, installation, release, new guard,
  `ready`) and `configured_pin(configuration)`.
- Extend the native check recorder with the Step 5 due set, through the
  service and a stand-in caller, and commit the refreshed record.

Expected outcome:

- Every design acceptance row about reuse, contention, recovery, deadlines,
  parent death, the guard, the budget override and the engine environment
  holds under fakes.
- Provisioning never writes to standard output; a valid reuse prints nothing.

Step framing:

- Design link: "Target flow of git-cliff provisioning", "Publication",
  "Messages, statuses and the failure contract", "The provisioning entry point
  for items 4 and 5", "Testing approach under the process-free policy";
  design decisions Q03, Q05, Q06, Q07, Q09, Q17, Q18; requirement
  clarifications Q03, Q06, Q08, Q14, Q15; plan decisions Q06, Q10, Q11, Q12,
  Q18.
- Execution checklist reference: [Shared execution command checklist for all
  v0.14.0 git-cliff-provisioning steps](#shared-execution-command-checklist-for-all-v0140-git-cliff-provisioning-steps).

#### Step 5 -- implementation for provisioning

**Files involved**:

- `tools/release_workflow/git_cliff/messages.py` (new, to be created).
- `tools/release_workflow/git_cliff/invocation.py` (new, to be created).
- `tools/release_workflow/git_cliff/installation.py` (new, to be created).
- `tools/release_workflow/git_cliff/provisioning.py` (new, to be created).
- `tests/unit/tools/release_workflow/git_cliff_children_fake.py` (new, to be created).
- `tests/unit/tools/release_workflow/git_cliff_native_checks.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_git_cliff_messages/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_messages/test_git_cliff_messages_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_invocation/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_invocation/test_git_cliff_invocation_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_installation/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_installation/test_git_cliff_installation_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_provisioning/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_contention_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_budget_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_lifecycle_tdd.py` (new, to be created).

**Tests first**:

- Messages: the download line reads
  `git-cliff 2.14.2: downloading git-cliff-2.14.2-x86_64-pc-windows-msvc.zip (7.1 MiB) from GitHub`
  for 7,428,304 bytes; the ready and waiting lines follow the design table
  with local time and offset; every stage diagnostic names the pin, the path,
  the stage and its remedy; no remedy mentions installing git-cliff or PATH;
  the probe and metadata remedies never mention the budget variable.
- Invocation: the engine policy removes every `GIT_CLIFF_*` name in any case,
  closes stdin and captures or inherits output as asked; the passthrough
  policy keeps the given environment, working directory and inherited
  streams; both put the guard handle in the request's inherited list and
  close the object's own guard only after the child exits, or at once when
  creation fails.
- Reuse (`test_git_cliff_provisioning_tdd.py`): a valid entry returns an invocation
  with nothing on stdout or stderr, no lock, no network and one probe created
  with the guard; under the write-denying helper the same call succeeds with
  no write attempt; a truncated executable or a missing `entry.json` leads to
  provisioning online and to the download diagnostic offline.
- Installation (`test_git_cliff_installation_tdd.py`): a first download
  prints the download and ready lines, publishes by one directory rename and
  leaves no owner file in the entry; a digest mismatch removes staging without
  a retry; a reset then success retries once after 5 s of fake time; two
  retryable failures report `download failed after 2 attempts`; a denied write
  gives the permission diagnostic naming the directory.
- Retirement and publication faults (`test_git_cliff_installation_tdd.py`),
  each followed by a second caller under the lock: an executable rename
  refused by a held guard gives the in-use diagnostic, leaves `<triple>/` with
  its executable and lets the next caller find the same state; a refused
  directory rename gives the in-use diagnostic and leaves `<triple>/` without
  `git-cliff.exe`, and the next caller skips the executable rename and moves
  the directory; a parent death between the two renames leaves the same state,
  repaired by the next caller once the parent is `DEAD`; an entry whose
  executable was already absent is moved without a first rename; a failed
  publication after retirement leaves no `<triple>/`, and the next caller
  provisions afresh. No case deletes or renames a guarded executable.
- Contention (`test_git_cliff_provisioning_contention_tdd.py`): two first uses produce one
  download, the second caller prints the waiting line and reuses the entry
  after its recheck; a lock left by a `DEAD` owner with `DEAD` children is
  recovered and its staging removed; `UNKNOWN` and `ALIVE` owners and children
  are preserved and the waiter fails at W; a repair attempt between a caller's
  validation and its child start is refused by the guard.
- Budget flow (`test_git_cliff_provisioning_budget_tdd.py`): unset, `900` and `3600`
  give the D and W the worker deadline and the waiting line show; each
  refused form fails before any guard, probe, child, network or cache access,
  also with a valid entry; `900` with a reset and `Retry-After: 2000` keeps
  the delay and the retry inside 900 s; `3600` keeps the probe at 15 s; a
  default waiter behind a holder declared with D = 1800 fails at 360 s and
  keeps the holder's lock and staging.
- Lifecycle (`test_git_cliff_provisioning_lifecycle_tdd.py`), one case per boundary of the
  fake child launcher: parent death during creation leaves no child or a job
  member that ends; death after creating a suspended worker before recording
  leaves an empty staging directory recovered once the parent is `DEAD`;
  death while a recorded worker writes, or during a staging probe, keeps
  staging while the child is `ALIVE` and removes it once `DEAD`; a recording
  failure terminates and reaps the suspended child and writes nothing; a
  worker or probe that never finishes is terminated and reaped before staging
  removal and lock release; death during a reuse probe or a git-cliff run
  keeps the inherited guard until the child ends; death between validation
  and child start leaves nothing to protect; a containment failure writes
  nothing; a Windows release below the baseline fails before any download or
  child. An `UnconfirmedEndError` from a worker or a staging probe raises the
  containment stage, removes no staging and leaves the lock record in place
  (`retain_record()`, so the `finally` path removes nothing), the state a dead
  parent leaves, and a later caller recovers them only once the owner and
  every recorded child are `DEAD`. From a reuse probe, `check_entry` has
  retained the guard before any invocation exists, and the provisioning
  caller's cleanup leaves it open; from a git-cliff run, the invocation
  retains its guard copy. A pre-identity unconfirmed end (`identity=None`)
  records nothing for that child, which never ran, so its staging stays
  recoverable once the owner is `DEAD`.
- Native evidence: the `step-5` milestone requires the Step 4 due set plus
  the Step 5 checks below.

**Classes and behavior**:

- `messages.Stage` (enum): `platform`, `containment`, `budget-setting`,
  `configuration`, `permission`, `lock-wait`, `download`, `verification`,
  `extraction`, `probe`, `in-use`. `messages.REMEDIES` maps each stage to the
  design's remedy text. `messages.ProvisioningError(ValueError)` with
  `exit_code = 2`, `stage`, `version`, `path`, `detail` and `diagnostic()`.
  `downloading_line`, `ready_line` and `waiting_line` format the design's
  lines.
- `invocation.Policy` (enum): `ENGINE`, `PASSTHROUGH`.
  `invocation.GitCliffInvocation(executable, version, guard, *, launch)`:
  `run(arguments, *, policy, cwd, environment=None, output="capture",
  deadline=None) -> ChildOutcome` and `close()`. `executable` is the
  launcher-local `GIT_CLIFF` value; it is never exported. On
  `UnconfirmedEndError` it retains its guard copy (`guard.retain()`), so its
  own `close()` and any caller cleanup leave the handle open.
- `installation.install(layout, pin, budget, seams, lock) -> None`: creates the
  staging directory and its owner file, runs at most two recorded worker
  attempts inside the deadline D (the 5 s delay drawn from it), verifies,
  extracts, runs the recorded staging probe within 15 s, writes `entry.json`,
  removes `owner.json`, retires an invalid or executable-less entry and
  publishes. On a failure whose children all ended it removes staging and
  releases the lock; on `UnconfirmedEndError` it calls `lock.retain_record()`,
  keeps staging and raises the containment stage.
- `installation.retire_entry(layout, pin, attempt)`, under the lock, starts
  from the state it finds and leaves these states:
  - no `<triple>/`: nothing to retire;
  - `<triple>/` with `git-cliff.exe`: rename the executable to
    `<triple>/.retired-<pid>-<created>-<rand>.exe`; a refusal (an open guard)
    is the in-use stage and changes nothing;
  - `<triple>/` without `git-cliff.exe` (after the first rename, a refused
    second rename, a parent death between the two, or a hand removal): rename
    the directory to `<pin>/.retired-<pid>-<created>-<rand>/`; a refusal (any
    other open handle inside) is the in-use stage and leaves `<triple>/`
    without its executable, which readers treat as absent;
  - after the directory rename, the retired directory is recovered once its
    name owner is `DEAD`;
  - publication then renames staging to `<triple>/`; a failure there leaves no
    `<triple>/`, and the next caller provisions afresh.
- `provisioning.ProvisioningSeams` (frozen): `launch` (child launcher),
  `open_guard`, `process_state`, `current_identity`, `mutex`, `clock`,
  `sleep`, `stderr`, `runtime` (worker interpreter) and `platform_check`;
  `production_seams(runtime)` builds the real ones.
- `provisioning.provision(tooling_root, pin, budget, *, seams, caller) ->
  GitCliffInvocation`: runs the target flow and raises `ProvisioningError`
  for every failure; `pin is None` raises the configuration stage.
- `provisioning.configured_pin(configuration) -> str | None`: the validated
  `[git-cliff] version` value, or its default.
- `git_cliff_native_checks.py --milestone step-5` adds, through the service:
  kill-on-close of a worker and of a git-cliff run after their parent is
  killed; the inherited guard refusing an executable rename while a reuse
  probe runs after its caller was killed and while a stand-in caller of the
  service is killed during its git-cliff run; and an abandoned transition
  mutex of a live process leaving its lock record. No pin is admitted before
  Step 7, so these checks use a temporary tooling root, a synthetic pin and an
  entry whose executable is a stand-in that prints `git-cliff <pin>` and then
  waits; the stand-in caller takes the place of the launcher, which arrives in
  Step 8.

**Completion criteria**:

- The command printed by `pw scope day` reports the objective (`exit=0`) in
  the current effort scope.
- `rg -n 'sys\.stdout|print\(' tools/release_workflow/git_cliff` finds no
  write to standard output outside the worker's own outcome line.
- `rg -n 'GIT_CLIFF_' tools/release_workflow/git_cliff` shows the removal
  rule only in `invocation.py`.
- Every design acceptance row assigned to Step 5 in the
  [acceptance ownership map](#acceptance-ownership-map-for-v0140-git-cliff-provisioning)
  has its named test.
- `native_checks.v1.json` holds milestone `step-5`, and its validator accepts
  it for the current sources.

#### Step 5 -- addendums for provisioning

Line-budget checkpoint:

- [ ] `tools/release_workflow/git_cliff/messages.py`: before 0; below-550 safe; repository ceiling <= 650; expected 160 (advisory).
- [ ] `tools/release_workflow/git_cliff/invocation.py`: before 0; below-550 safe; ceiling <= 650; expected 140 (advisory).
- [ ] `tools/release_workflow/git_cliff/installation.py`: before 0; below-550 safe; ceiling <= 650; expected 320 with the retirement states and unconfirmed-end handling (advisory).
- [ ] `tools/release_workflow/git_cliff/provisioning.py`: before 0; below-550 safe; ceiling <= 650; expected 240 (advisory).
- [ ] `tests/unit/tools/release_workflow/git_cliff_children_fake.py`: before 0; ceiling <= 650; expected 150 (advisory).
- [ ] `tests/unit/tools/release_workflow/git_cliff_native_checks.py`: before about 230; ceiling <= 650; expected +110 (advisory).
- [ ] `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py`: before about 135; ceiling <= 650; expected +5 (advisory).
- [ ] New test files: before 0; ceiling <= 650; expected 130 (messages), 170 (invocation), 300 (installation), 200 (provisioning), 260 (contention), 230 (budget) and 320 (lifecycle) (advisory).

Split guidance:

- If `installation.py` would pass 650, move retirement and publication into
  `git_cliff/publication.py`.

Full workflow timing run readiness:

- `ghog single` on the Step 5 test files, then the native check recorder by
  hand with `--milestone step-5`, then the command printed by `pw scope day`.

Time-gated status for Step 5:

- No perf gate is affected; every budget is asserted against the fake clock.

---

### Step 6. Compatibility evidence harness

#### Step 6 -- analysis and intent for the harness

Issues to address:

- No code acquires a candidate's identity independently of the manifest,
  keeps an immutable trust record, or runs two versions on identical inputs.
- llm-shared has no snapshot tag, so the matrix needs a deterministic
  fixture history whose object hashes are recorded.
- `GitExecutionContext.run` cannot feed an input stream to Git.

Fix intent:

- Ship `git_cliff/candidates.py`: candidate identities (2.14.2 from release
  metadata through the record-free metadata worker, 2.7.0 from its first
  authorized download, bounded by the asset size read from the same
  certificate-verified release metadata, as plan Q19 decided), trust records
  written once and compared later, and candidate
  provisioning through the evidence namespace of the Step 3 to 5 primitives.
- Ship `git_cliff/fixture_history.py`: the committed script building the
  snapshot-tag fixture through one `git fast-import` stream that fixes every
  object-producing input.
- Ship `git_cliff/comparison.py`: frozen inputs, the temporary worktree, the
  range list, the runs through the engine policy with one explicit
  environment, digests, statuses and hunks.
- Ship `git_cliff/bundle.py`: the bundle model, its strict reader and writer,
  its completeness checks and the binding of the user's review to the exact
  evidence (a `review` member over the canonical projection and a `files`
  member with the digests of the bundle's other files); and
  `git_cliff/harness.py`, the developer entry point, which also records the
  user's review.
- Add an optional `input` to `GitExecutionContext.run`, which moves here with
  the harness.

Expected outcome:

- The harness never writes the manifest, never reaches the production
  namespace and fails on a changed trust record, a changed fixture hash or a
  changed rerun digest.
- Its pure logic is covered by unit tests with fakes; only the real run is by
  hand.

Step framing:

- Design link: "Compatibility evidence harness and bundle", "Statuses";
  design decisions Q11, Q12, Q13, Q14, Q15; requirement clarifications Q13,
  Q16; plan decisions Q03, Q09, Q12, Q16, Q19.
- Execution checklist reference: [Shared execution command checklist for all
  v0.14.0 git-cliff-provisioning steps](#shared-execution-command-checklist-for-all-v0140-git-cliff-provisioning-steps).

#### Step 6 -- implementation for the harness

**Files involved**:

- `tools/release_workflow/git_cliff/candidates.py` (new, to be created).
- `tools/release_workflow/git_cliff/fixture_history.py` (new, to be created).
- `tools/release_workflow/git_cliff/comparison.py` (new, to be created).
- `tools/release_workflow/git_cliff/bundle.py` (new, to be created).
- `tools/release_workflow/git_cliff/harness.py` (new, to be created).
- `tools/release_workflow/git.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/git_cliff_harness_fake.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_candidates/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_candidates/test_git_cliff_candidates_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_fixture/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_fixture/test_git_cliff_fixture_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_comparison/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_comparison/test_git_cliff_comparison_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_bundle/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_bundle/test_git_cliff_bundle_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git/test_git_tdd.py` (existing, to be updated).

**Tests first**:

- Candidates: the 2.14.2 identity comes from canned release metadata (asset
  name, size and `sha256:` digest) returned by a fake metadata worker; for
  2.7.0 the metadata gives the asset name and size without a digest, the
  recorded worker download is bounded by that size, and the parent computes
  the digest; the trust record is written once, only after the staged
  candidate is extracted and its probe reports the version; a metadata
  failure, a size overflow, a short body, two retryable download failures, an
  extraction or probe failure, an unconfirmed child end and a parent death
  before that point each leave no trust record and staging recoverable by the
  ordinary rules; evidence-only trust for any version other than 2.7.0 is
  refused before any download; a later different archive fails and leaves the
  record byte for byte; the candidate reuse check compares the entry record's
  archive digest with the trust record, then the executable with the entry,
  then the probe; candidate layouts never resolve to a production path; the
  harness resolves the budget once and candidate downloads use D.
- Fixture: the fast-import stream is byte-identical across two builds; it
  sets every tree, parent order, message, author and committer identity and
  date with zone, annotated tag name, tagger and message, with stable and
  `-SNAPSHOT` tags; the Git calls (recorded by a fake runner) use
  `--object-format=sha1`, command-line configuration only, an empty
  `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_NOSYSTEM=1`, no hooks, no signing and no
  line-ending conversion; recorded object hashes that differ from the
  regenerated ones fail.
- Comparison: both candidates receive the same worktree, ranges, `cliff.toml`
  bytes, flags (`-c <bundle copy> -w <worktree> -s footer`) and environment
  (`SystemRoot`, `TEMP`, `TMP`, `HOME` and `USERPROFILE` on an empty
  directory, no `GIT_*`); the ranges are the full history, each consecutive
  `vA..vB` and `<last tag>..HEAD`; identical outputs store only digests and
  statuses; a differing range stores its hunks with three lines of context; a
  rerun digest different from the bundle fails; the temporary worktree is
  removed and pruned on success and failure.
- Bundle: strict read and write of schema 1; the checks refuse a missing
  input, an unclassified hunk, a `defect` entry, an audit that does not
  exclude 69 or lacks its revision, and a bundle whose pin is admitted without
  a manifest reference.
- Bundle review binding: the covered projection is `bundle.json` without its
  `review` member, serialized as canonical JSON (keys sorted,
  `separators=(",", ":")`, `ensure_ascii=True`, UTF-8); the `files` member
  lists the SHA-256 of `cliff.toml`, `trust.2.14.2.json` and
  `trust.2.7.0.json`, verified against the files on every read; the `review`
  member holds `decision` (`approved` or `rejected`), `reviewer` (`user`),
  `date` (ISO local date) and `covered_sha256`. `require_admissible` refuses
  an absent review, a rejected one, a reviewer other than `user`, a malformed
  date, a `covered_sha256` different from the recomputed projection, a
  tampered listed file and a content change after approval; a harness rerun
  that changes any covered content keeps the review member but leaves it
  stale, and a byte-identical projection keeps the approval.
- Git: `run(arguments, cwd=..., input=b"...")` passes the bytes through
  `subprocess.run(input=...)` without also setting `stdin`; without `input`
  the existing stdin rule is unchanged; both branches are tested without a
  process.

**Classes and behavior**:

- `candidates.AssetListing` (frozen): `version`, `asset`, `size` and
  `published_sha256` (`None` when the release publishes no digest), parsed
  from the metadata worker's output.
- `candidates.Candidate` (frozen): `version`, `asset`, `size`, `sha256`,
  `trust` (`upstream-digest` or `evidence-only-https`), `source`, `acquired`.
  `TrustRecord.write_once(path, candidate)` (non-replacing publication of a
  flushed file) and `TrustRecord.compare(path, received)`.
- `candidates.EVIDENCE_ONLY_VERSIONS = frozenset({"2.7.0"})`, the scope of the
  user's authorization of 2026-11-13.
- `candidates.acquire_candidate(tooling_root, version, budget, seams, *,
  trust_path) -> GitCliffInvocation`, under the candidate lock:
  1. With an existing trust record, use its identity; otherwise read the
     listing through the metadata worker (60 s, one retry). An
     `upstream-digest` candidate needs `published_sha256`; an
     `evidence-only-https` candidate is allowed only for a version in
     `EVIDENCE_ONLY_VERSIONS`.
  2. Download through the ordinary recorded worker with
     `expected_size = listing.size`, under D with one retry, into candidate
     staging; the parent computes the SHA-256 of the staged file.
  3. Compare with the trust record or, without one, with the listing's
     published digest when it has one; then extract and run the recorded
     staging probe.
  4. Without a trust record, write it once from the listing and the computed
     digest, then publish the candidate entry; a failure at any earlier point
     writes no trust record.
  `provision_candidate` is its reuse path through
  `CacheLayout(namespace="evidence")`.
- `fixture_history.stream() -> bytes`, `build(git, directory) ->
  FixtureHashes`, `verify(recorded, built)`.
- `comparison.FrozenInputs` (frozen): llm-shared commit, `cliff.toml` source
  path, bytes digest and dev_workflow commit, flags, environment names,
  ranges, candidate identities. `run_comparison(inputs, invocations, git)
  -> ComparisonResult`.
- `bundle.Bundle` (frozen) with `inputs`, `outputs`, `classification`,
  `audit`, `observed_statuses`, `files` and `review` (`None` until the user's
  decision); `read(path)` (which verifies the `files` digests), `write(path)`,
  `canonical_projection(bundle) -> bytes`, `with_review(bundle, decision,
  date) -> Bundle` and `require_admissible(bundle)`.
- `harness.main(arguments) -> int`: `--bundle`, `--pin`, `--baseline`;
  resolves the budget once, acquires or compares candidates, builds or checks
  the fixture, runs the comparison and writes the bundle, keeping existing
  classification, audit and review entries (a kept review whose projection
  changed is stale). `--review approved` or `--review rejected` with
  `--bundle` only writes the user's decision over the current projection,
  with today's local date, and changes nothing else. Its
  `if __name__ == "__main__":` line is the only `# pragma: no cover` line.
- `git.GitExecutionContext.run(..., input: bytes | None = None)`.

**Completion criteria**:

- The command printed by `pw scope day` reports the objective (`exit=0`) in
  the current effort scope.
- `rg -n 'manifest' tools/release_workflow/git_cliff/harness.py tools/release_workflow/git_cliff/comparison.py tools/release_workflow/git_cliff/candidates.py`
  shows reads of the manifest only, no write.
- `rg -n 'pragma: no cover' tools/release_workflow/git_cliff` shows only the
  harness entry line.

#### Step 6 -- addendums for the harness

Line-budget checkpoint:

- [ ] `tools/release_workflow/git_cliff/candidates.py`: before 0; below-550 safe; repository ceiling <= 650; expected 260 with the acquisition path (advisory).
- [ ] `tools/release_workflow/git_cliff/fixture_history.py`: before 0; below-550 safe; ceiling <= 650; expected 200 (advisory).
- [ ] `tools/release_workflow/git_cliff/comparison.py`: before 0; below-550 safe; ceiling <= 650; expected 260 (advisory).
- [ ] `tools/release_workflow/git_cliff/bundle.py`: before 0; below-550 safe; ceiling <= 650; expected 250 with the review binding (advisory).
- [ ] `tools/release_workflow/git_cliff/harness.py`: before 0; below-550 safe; ceiling <= 650; expected 130 with the review mode (advisory).
- [ ] `tools/release_workflow/git.py`: before 331; below-550 safe; ceiling <= 650; expected +6 (advisory).
- [ ] `tests/unit/tools/release_workflow/git_cliff_harness_fake.py`: before 0; ceiling <= 650; expected 90 (advisory).
- [ ] New test files: before 0; ceiling <= 650; expected 280, 170, 260 and 260 (advisory).
- [ ] `tests/unit/tools/release_workflow/test_git/test_git_tdd.py`: before 232; ceiling <= 650; expected +15 (advisory).

Split guidance:

- If `test_git_cliff_bundle_tdd.py` would pass 650, move the review binding
  cases into `test_git_cliff_bundle_review_tdd.py`.

Full workflow timing run readiness:

- `ghog single` on the Step 6 test files and `test_git`, then the command
  printed by `pw scope day`.

Time-gated status for Step 6:

- No perf gate is affected; the harness itself runs only by hand.

---

### Step 7. Evidence run, user review and admission of 2.14.2

#### Step 7 -- analysis and intent for admission

Issues to address:

- No evidence has been recorded, so the manifest admits nothing and an
  omitted pin has no default.
- The requirement makes the user's review of the evidence a separate
  acceptance step, and nothing committed records that review yet.

Fix intent:

- Run the Step 6 harness by hand (network required; the 2.7.0 download runs
  under the evidence-only exception the user authorized on 2026-11-13), audit
  git-cliff's exit paths at the `v2.14.2` source tag and classify every hunk.
- Present the bundle for the user's review and record the decision in its
  `review` member through the harness, then in the step journal.
- Admit 2.14.2 as the default by a manifest edit that copies the bundle's
  identity and reference, with the admission, schema and configuration tests.

Expected outcome:

- The manifest holds exactly 2.14.2, default, with the design's identity, and
  the admission test ties it to the committed bundle and its approved review.
- Step 8 builds the launcher and the integrated acceptance on the shipped
  manifest, and `bin\gcliff.bat` can be tried by hand against the admitted pin
  as soon as it lands.

Step framing:

- Design link: "Candidate lifecycle and admission order", "Outputs and
  classification", "Statuses"; design decisions Q01, Q11, Q13, Q17;
  requirement clarifications Q01, Q13, Q16; plan decisions Q03, Q08, Q16,
  Q17.
- Execution checklist reference: [Shared execution command checklist for all
  v0.14.0 git-cliff-provisioning steps](#shared-execution-command-checklist-for-all-v0140-git-cliff-provisioning-steps).

#### Step 7 -- implementation for admission

**Files involved**:

- `tools/release_workflow/git_cliff/bundles/2.14.2/bundle.json` (new, to be created).
- `tools/release_workflow/git_cliff/bundles/2.14.2/cliff.toml` (new, to be created).
- `tools/release_workflow/git_cliff/bundles/2.14.2/trust.2.14.2.json` (new, to be created).
- `tools/release_workflow/git_cliff/bundles/2.14.2/trust.2.7.0.json` (new, to be created).
- `tools/release_workflow/git_cliff/manifest.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_git_cliff_acceptance/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_acceptance/test_git_cliff_admission_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_schemas/test_schemas_tdd.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_configuration/test_configuration_tdd.py` (existing, to be updated).

**Tests first**:

- Admission: the shipped manifest holds one pin, `2.14.2`, default, with
  `git-cliff-2.14.2-x86_64-pc-windows-msvc.zip`, 7,428,304 bytes, digest
  `6ece2112b3f4af462190ecbea4aeb1315fff6af415629b597f84319073c31131` and
  member `git-cliff-2.14.2/git-cliff.exe`; its evidence reference names
  `tools/release_workflow/git_cliff/bundles/2.14.2`; the committed bundle
  passes `require_admissible`, so its `review` member reads decision
  `approved`, reviewer `user` and a valid date, its `covered_sha256` equals
  the recomputed projection and the listed digests of `cliff.toml` and both
  trust records equal the committed files; its 2.14.2 candidate identity
  equals the manifest entry; `trust.2.7.0.json` never appears in the manifest
  and `version = 2.7.0` stays a configuration error.
- Schemas and configuration: the shipped default is now `2.14.2`; an omitted
  key yields that defaulted value; `version = 2.15.0` reports
  `tested: 2.14.2`.

**Classes and behavior**:

- Evidence run, by hand: the harness command of the ready-to-run templates.
- Exit-path audit, by hand, with a written checklist: a shallow clone of the
  `v2.14.2` tag into a temporary directory outside the repository; for each
  category (error return, argument-parsing errors, propagated helper
  statuses, panics and abnormal termination) the files and call sites read,
  with the dependency versions and source references wherever they affect
  helper, parser or panic exits; the clone commands and the audited commit
  recorded in `bundle.json` with the observed statuses of success, a usage
  error, a failing render and any reachable panic path. Observed statuses
  corroborate the reading; they do not prove the exclusion of 69.
- Classification of every hunk as intentional with its upstream release-note
  reason, or as a defect.
- Human gate: present the bundle's classification table, audit and listed
  files to the user and wait for their decision. The harness then writes it
  with `--review approved` or `--review rejected` (Step 6) over the current
  projection, and the step journal records the same decision with its date. A
  rejection, an open defect or a version able to return 69 stops admission and
  goes back to the user.
- `manifest.ADMITTED_PINS`: the one `AdmittedPin` above, written only after an
  approved review.

**Completion criteria**:

- The command printed by `pw scope day` reports the objective (`exit=0`) in
  the current effort scope.
- `rg -n '2\.14\.2' tools/release_workflow/git_cliff/manifest.py` shows the
  one admitted pin.
- The committed `bundle.json` holds the user's approved `review` covering its
  committed projection, and the step journal records that review with its
  date before the manifest edit is committed.
- The native check record still passes its validator: when this step edits a
  source file the record covers, the affected checks are rerun first (shared
  checklist).

#### Step 7 -- addendums for admission

Line-budget checkpoint:

- [ ] `tools/release_workflow/git_cliff/manifest.py`: before about 110; below-550 safe; repository ceiling <= 650; expected +12 (advisory).
- [ ] New test file `test_git_cliff_admission_tdd.py`: before 0; ceiling <= 650; expected 120 (advisory).
- [ ] Updated test files: before about 171 and 286; ceiling <= 650; expected +5 and +10 (advisory).
- [ ] Bundle data: non-Python, no Python ceiling.

Split guidance:

- None expected.

Full workflow timing run readiness:

- `ghog single` on the Step 7 test files, then the command printed by
  `pw scope day`.

Time-gated status for Step 7:

- No perf gate is affected; the harness runs outside pytest with its own
  bounds.

---

### Step 8. The gcliff launcher, integrated acceptance, final native checks and documentation

#### Step 8 -- analysis and intent for gcliff and rollout

Issues to address:

- No launcher runs git-cliff for the current worktree's pin, and the release
  launcher maps every status outside 0 to 3 to 1.
- Discovery cannot tell "no worktree here" (a plain directory, a bare
  repository, a `.git` directory) from a genuine discovery failure.
- No tested alias line exists for `gcliff`.
- No end-to-end test walks the shipped paths together, the native checks have
  not run against the final sources and the production launcher, and no
  reference page documents the launcher, the cache, the budget variable or the
  statuses.

Fix intent:

- Ship `bin/gcliff.bat` and the `gcliff-batch` entry kind, which selects
  `git_cliff/launcher.py`, reports readiness and argument failures as 69 and
  returns git-cliff's status unchanged.
- Add a typed worktree-presence observation to `git.py` and a
  `paths.find_worktree` used only by `gcliff`; `discover_project` and its
  other callers keep their behavior.
- Ship `bin/gcliff.doskey`, the single-line alias fragment.
- Add the integrated acceptance tests, run against the shipped manifest.
- Rerun the full native check set against the final sources, with the
  production `gcliff` launcher in place of the Step 5 stand-in caller, and
  commit the final record.
- Write the reference documentation.

Expected outcome:

- `gcliff` in a nested folder of a pinned worktree runs that pin; outside a
  worktree, or without a pin, the default applies after whole-file validation;
  arguments, output, status and environment pass through.
- Every failure before git-cliff starts returns 69 with its diagnostic.
- Every design acceptance row has its unit or acceptance proof, and every
  native row has a recorded check that passed against the final sources.

Step framing:

- Design link: "The gcliff launcher", "Selecting the project and the pin",
  "Statuses", "Acceptance cases for the git-cliff provisioning design",
  "Testing approach under the process-free policy"; design decisions Q09,
  Q10, Q11, Q16, Q17; requirement clarifications Q08, Q09, Q10, Q11, Q12 and
  the requirement's acceptance criteria; plan decisions Q03, Q06, Q07, Q13,
  Q14, Q15.
- Execution checklist reference: [Shared execution command checklist for all
  v0.14.0 git-cliff-provisioning steps](#shared-execution-command-checklist-for-all-v0140-git-cliff-provisioning-steps).

#### Step 8 -- implementation for gcliff and rollout

**Files involved**:

- `bin/gcliff.bat` (new, to be created).
- `bin/gcliff.doskey` (new, to be created).
- `tools/release_workflow/git_cliff/launcher.py` (new, to be created).
- `tools/release_workflow/bootstrap.py` (existing, to be updated).
- `tools/release_workflow/invocation.py` (existing, to be updated).
- `tools/release_workflow/git.py` (existing, to be updated).
- `tools/release_workflow/paths.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/launcher_simulation.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/git_cliff_native_checks.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_git_cliff_launcher/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_launcher/test_git_cliff_launcher_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_launchers/test_gcliff_source_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_acceptance/test_git_cliff_acceptance_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_acceptance/test_gcliff_acceptance_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_invocation/test_invocation_tdd.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_git/test_git_tdd.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_paths/test_paths_tdd.py` (existing, to be updated).
- `wiki/reference/git-cliff-provisioning.md` (new, to be created).
- `wiki/reference/aliases-and-launchers.md` (existing, to be updated).
- `wiki/reference/automation-and-direct-invocation.md` (existing, to be updated).
- `wiki/README.md` (existing, to be updated).

**Tests first**:

- Launcher (`test_git_cliff_launcher_tdd.py`), through the launcher
  simulation with a fake provisioning seam and a fake child launcher:
  `gcliff --version` in a nested folder of a worktree with
  `[git-cliff] version = 2.14.2` (shipped manifest) provisions and runs that
  pin; in a plain directory, a bare repository, a `.git` directory and a
  worktree without a pin the default is used after validation; an invalid
  `[source:npm]` section returns 69 with the reader diagnostic and starts no
  child; a git-cliff status of 1, 2 or 3 returns unchanged;
  `--workdir <other repository>` does not change the selected pin; a `%`,
  `^`, `!` or `"` argument returns 69; an invalid budget value returns 69 even
  with a valid entry; `GIT_CLIFF_*` variables reach the child; the console
  handler routine is registered only while the child runs, stays referenced
  while registered and is removed after a normal return and after a child
  error; a genuine discovery failure (exit 128 with another diagnostic, such
  as a dubious ownership refusal, or a rejected configuration) returns 69.
- Bootstrap: `gcliff-batch` readiness failure returns 69 with the "run this
  checkout's setup" message; a reserved `--entry-kind` in its arguments
  returns 69; its status is returned unchanged for 0, 1, 2, 3, 69 and 101,
  tested independently of the release kinds.
- Batch source contract (`test_gcliff_source_tdd.py`): `bin/gcliff.bat` keeps
  the self-location, codepage save and restore and runtime record blocks of
  the release launchers, sets `_release_status=69` before the record checks,
  runs `-I -X utf8 "%_release_root%\tools\release_workflow\bootstrap.py"
  --entry-kind gcliff-batch -- %*`, and has no status normalization line; the
  source and the launcher simulation show the saved codepage restored after a
  readiness error and after a normal child return.
- Alias fragment: `bin/gcliff.doskey` is exactly one line,
  `gcliff="%LLM_SHARED_DIR%\bin\gcliff.bat" $*`, parsed with the
  `name=definition` rule of `senv.doskey`; `senv.doskey` has no `gcliff`
  line.
- Invocation: `validate_arguments("gcliff-batch", ...)` applies the batch
  guard.
- Git and paths: `worktree_presence` maps `true` to `INSIDE`, `false` (bare
  repository or `.git` directory) to `NO_WORKTREE`, and exit 128 whose stderr
  starts with `fatal: not a git repository` to `NO_REPOSITORY`; any other
  failure raises `GitCommandError`. `find_worktree` returns `None` for the two
  absent cases, runs the existing configuration inspection first, and for
  `INSIDE` returns what `discover_project` returns; the existing
  `discover_project` tests stay unchanged.
- Native evidence: the validator's `final` milestone requires the full set of
  Steps 2, 4 and 5, with the inherited-guard check after a killed launcher
  run through the production `bin\gcliff.bat` and the admitted 2.14.2; the
  negative records of Step 2 still apply.
- Acceptance, through the launcher simulation and fake native seams: every
  design acceptance row assigned to Step 8 in the ownership map, including
  `.release.ini` without `[git-cliff]` reusing a valid default entry
  silently; `version`, `versions check` and an ordinary configuration load
  importing no `git_cliff` module other than `manifest` and never reading the
  budget variable; an engine caller (a test-only handler calling
  `provision`) returning status 2 with the stage diagnostic and leaving the
  project unchanged; `bin\gcliff.bat --version` as the warm-up path; a
  fresh checkout's first provisioning leaving `git status` clean, asserted on
  the ignore rule and the produced paths.

**Classes and behavior**:

- `launcher.main(arguments, *, original_cwd, tooling_root, runtime,
  environment=None, seams=None) -> int`: validates the arguments with the
  batch guard, creates the Git context, finds the worktree with
  `paths.find_worktree` (or none), loads the configuration, takes
  `configured_pin` or the manifest default, resolves the budget, provisions,
  then runs the passthrough policy inside `ignore_console_interrupts()` and
  returns the child's status. Every failure before the child starts writes its
  diagnostic and returns 69 (`GCLIFF_UNAVAILABLE = 69`).
- `bootstrap`: `entry` accepts `gcliff-batch`; `_ENGINES` maps it to
  `tools.release_workflow.git_cliff.launcher`; `_UNNORMALIZED_KINDS` includes
  it; a `_FAILURE_STATUS` table gives 69 for its readiness and invocation
  failures and 2 for the release kinds; `main` keeps its single set literal.
- `invocation.ENTRY_KINDS` gains `gcliff-batch`.
- `git.WorktreePresence` (enum: `INSIDE`, `NO_WORKTREE`, `NO_REPOSITORY`) and
  `GitExecutionContext.worktree_presence(*, cwd)`: one
  `rev-parse --is-inside-work-tree` call through `run` with `check=False`,
  classified on its exit code, stdout and untranslated stderr.
  `paths.find_worktree(start, git) -> ProjectIdentity | None`.
- `bin/gcliff.bat`: the release launcher's self-location, codepage save,
  switch to 65001 and restore, and runtime record reading, status 69 for
  every pre-Python failure, then `exit /b %_release_status%` with git-cliff's
  status.
- `git_cliff_native_checks.py --milestone final`: reruns every check of
  Steps 2, 4 and 5 against the final sources; the inherited-guard check after
  a killed launcher now starts `bin\gcliff.bat` with the admitted 2.14.2
  instead of the stand-in caller. A check that fails, times out or cannot run
  is recorded as such, and the validator then refuses the record, which
  blocks the step.
- Documentation: `wiki/reference/git-cliff-provisioning.md` covers the pin,
  the tested set, the cache path and ignore rule, the warm-up, the proxy and
  certificate rules, the budget variable, the messages, the statuses and the
  evidence bundle with its review; the two existing pages add `gcliff` and
  statuses 2 and 69; `wiki/README.md` links the new page.

**Completion criteria**:

- The command printed by `pw scope day --full=cov` reports the objective
  (`exit=0`, coverage 100) in the current effort scope.
- `rg -n 'gcliff' senv.doskey` finds no match.
- `rg -n 'returning 1' bin/gcliff.bat` finds no normalization.
- The cross-site status contract of `test_codepage_tdd.py` still passes
  unchanged.
- `native_checks.v1.json` holds milestone `final`, and its validator accepts
  it for the current sources.
- Every row of the
  [acceptance ownership map](#acceptance-ownership-map-for-v0140-git-cliff-provisioning)
  names a passing test or a native check the validator accepts as passed for
  the current sources.

#### Step 8 -- addendums for gcliff and rollout

Line-budget checkpoint:

- [ ] `tools/release_workflow/git_cliff/launcher.py`: before 0; below-550 safe; repository ceiling <= 650; expected 150 (advisory).
- [ ] `tools/release_workflow/bootstrap.py`: before about 226; below-550 safe; ceiling <= 650; expected +30 (advisory).
- [ ] `tools/release_workflow/invocation.py`: before 199; below-550 safe; ceiling <= 650; expected +1 (advisory).
- [ ] `tools/release_workflow/git.py`: before about 337; below-550 safe; ceiling <= 650; expected +12 (advisory).
- [ ] `tools/release_workflow/paths.py`: before 164; below-550 safe; ceiling <= 650; expected +12 (advisory).
- [ ] `tests/unit/tools/release_workflow/launcher_simulation.py`: before 210; below-550 safe; ceiling <= 650; expected +45 (advisory).
- [ ] `tests/unit/tools/release_workflow/git_cliff_native_checks.py`: before about 340; ceiling <= 650; expected +40 (advisory).
- [ ] New test files: before 0; ceiling <= 650; expected 300 (launcher), 90 (source contract), 300 and 220 (acceptance) (advisory).
- [ ] Updated test files: before about 247, 200, 247, 174 and 140; ceiling <= 650; expected +40, +5, +20, +15 and +10 (advisory).
- [ ] `bin/gcliff.bat`, `bin/gcliff.doskey`, the record and the wiki pages: non-Python, no Python ceiling (about 75 lines and 1 line for the two launcher files).

Split guidance:

- If `test_git_cliff_launcher_tdd.py` would pass 650, move the failure-status
  cases into `test_git_cliff_launcher_failures_tdd.py`.
- If `git_cliff_native_checks.py` would pass 650, move the guard and mutex
  checks into `git_cliff_native_guard_checks.py`, started by the same entry.

Full workflow timing run readiness:

- `ghog single` on the Step 8 test files, `test_launchers` and
  `test_release_acceptance`, then the command printed by `pw scope day`, then
  `pw scope day --full=cov`.

Time-gated status for Step 8:

- No perf gate is affected; the native checks run outside pytest with their
  own bounds.

---

## Acceptance ownership map for v0.14.0 git-cliff-provisioning

AC1 to AC6 number the six bullets of the requirement's "Acceptance criteria
for git-cliff provisioning" in their order: pin and reuse (AC1), download,
concurrency, budgets and platform (AC2), failure reporting (AC3), launcher and
alias (AC4), compatibility evidence (AC5), and operations free of git-cliff
with the ignored cache (AC6).

| Design acceptance rows | Requirement | Unit proof | End-to-end or passing native proof |
| --- | --- | --- | --- |
| Default pin with valid cache; `2.15.0`; `v2.14.2` or `latest`; `2.7.0` | AC1, AC5 | Step 1 manifest and configuration tests, Step 7 admission tests | Step 8 acceptance |
| Truncated executable; missing `entry.json`; read-only checkout with a valid entry | AC1, AC2 | Step 3 reuse check, Step 5 reuse tests | Step 8 acceptance |
| Two first uses; crashed holder; `UNKNOWN` owner; abandoned mutex with `ALIVE` owner; staging of a live owner | AC2 | Step 3 lock tests, Step 5 contention tests | Native check (abandoned mutex) |
| Stalled download; hung probe | AC2 | Step 2 deadline, descendant and unconfirmed-end tests, Step 5 lifecycle tests | Native checks (stalled endpoint, descendant teardown, teardown-failure exit) |
| Parent death at each boundary; recording failure; child `ALIVE` or `UNKNOWN` after parent death; containment and nesting failures | AC2 | Step 2 fault tests, Step 5 lifecycle tests | Native checks (job membership, suspended child, refused nesting, kill-on-close) |
| Older Windows | AC2 | Step 2 platform tests | Step 8 acceptance |
| Valid-entry reuse probe; caller, harness or launcher death during a child; launcher death before child start | AC2 | Step 5 lifecycle tests | Native checks (inherited guard) |
| Digest mismatch; checkout not writable; invalid entry in use; repair between validation and start | AC2, AC3 | Step 4 archive tests, Step 5 installation and contention tests | Native check (guard between validation and start) |
| `gcliff --version` nested; invalid `[source:npm]`; bad git-cliff argument | AC4 | Step 8 launcher tests | Step 8 `gcliff` acceptance |
| `uc` or `brel` provisioning failure (engine caller) | AC3 | Step 5 messages and provisioning tests | Step 8 acceptance with a test-only handler |
| `version`, ordinary build, curated validation free of provisioning; budget variable not read | AC6 | Step 1 import-freedom test | Step 8 acceptance |
| Fresh checkout `git status` clean | AC6 | Step 3 ignore-rule test | Step 8 acceptance |
| Changed candidate archive; fixture regeneration; controlled inputs; rerun digest; reviewed evidence | AC5 | Step 6 candidate, fixture, comparison and bundle review tests | Step 7 evidence run and recorded review |
| Engine and passthrough environments | AC4 | Step 5 invocation tests, Step 8 launcher tests | Step 8 acceptance |
| Budget unset, `900`, `3600`, refused forms, valid entry with invalid budget, unaffected operations, retry inside D, probe and metadata limits, harness downloads, default waiter behind a 1800 s holder | AC2, AC3 | Step 1 budget tests, Step 5 budget flow tests, Step 6 candidate tests | Step 8 acceptance |

Each native check first passes in the step that introduces the behavior it
proves (Step 2, 4 or 5) and passes again in the final Step 8 rerun against
the final sources.

---

## Planning risk pass and rollout order for v0.14.0 git-cliff-provisioning

The steps are sequential: Steps 3 to 5 compose the Step 1 manifest and budget
with the Step 2 native layer; the harness (Step 6) and the launcher (Step 8)
both call the Step 5 service, not each other; Step 7 admits the pin only after
the harness exists and the user approved its bundle; Step 8 then builds the
launcher and the integrated acceptance on the shipped manifest. The native
checks are recorded at the Step 2, Step 4 and Step 5 milestones and rerun in
full in Step 8. Every step passes its own gate without a placeholder module
for a later step.

Implementation risks found by the second pass:

- **Status contract**: `test_codepage_tdd.py` reads exactly one set literal in
  `bootstrap.main`. The new kinds keep their pass-through and failure rules in
  module-level tables, never in a second literal inside `main`.
- **Inherited console filter**: `SetConsoleCtrlHandler(NULL, TRUE)` is
  inherited by children, which would stop git-cliff from receiving Ctrl+C; the
  launcher registers a handler routine instead, which children do not
  inherit.
- **Memory filesystem and native calls**: `tmp_path` lives in memory, so any
  test reaching real `CreateFileW` would miss its files; every native call in
  tests goes through the fake kernel or a fake guard opener.
- **Handle inheritance window**: the guard and pipe ends become inheritable
  only around `CreateProcessW`. Concurrent `subprocess` starts in the same
  process (Git) use their own handle lists, so they cannot pick the guard up.
- **Directory rename with open files**: retiring an entry renames its
  executable first (refused by any guard), then its directory; a directory
  rename refused for another open handle (an antivirus scan, for example) is
  reported as the in-use stage as well. The directory then stays without its
  executable, which readers treat as absent, and the next caller under the
  lock resumes at the directory rename (Step 5 `retire_entry`).
- **Descendants holding output pipes**: a descendant that inherits a pipe write
  end keeps the pipe open after its parent ends, so reader threads are joined
  only after the job-wide teardown has confirmed that every member ended.
- **Shutdown after an unconfirmed end**: a non-daemon reader blocked on such a
  pipe would hold CPython's shutdown and keep the job handle open forever.
  Readers are therefore daemon threads over native handles and private
  buffers, and every unresolved handle and guard moves to the process-lifetime
  owner `RETAINED`, so normal unwinding and interpreter exit end the process
  and let kill-on-close terminate the members.
- **Empty manifest interval**: from Step 1 to Step 6 the item branch admits no
  pin. Nothing outside this item calls provisioning yet, and the umbrella
  reaches `main` only after all eight items, so no consumer sees it.
- **Stale native evidence**: the record holds the digest of every source file
  each check exercises, so a later step that edits one of them must rerun the
  affected checks before its gate passes (shared checklist item 6).
- **Readings of design-silent cases**, implemented as tested behavior and
  confirmed by the plan review (see
  [Implementation decisions](#implementation-decisions-for-v0140-git-cliff-provisioning)):
  - the root `.gitignore` entry lands in Step 3, the first step whose code
    writes under `.tools/git-cliff/`, one step before the downloader, so the
    rule still precedes every cache write in every checkout (requirement
    Q05, plan Q01); the Step 2 native checks use temporary paths;
  - `bin/gcliff.bat` reuses the release launchers' UTF-8 codepage switch and
    restores the console's codepage before it exits, so the console is
    unchanged afterwards;
  - termination is job-wide (`TerminateJobObject`) and confirmed by the root
    wait and a zero `ActiveProcesses` count before any join or cleanup; once
    the termination call has succeeded, that reap has no budget of its own, as
    the design orders the reap before cleanup without bounding it; a failing
    termination, wait or count query is an unconfirmed end that keeps
    staging, the lock record and the guard copy, the state the design already
    defines for a dead parent;
  - each download attempt is one worker run; the parent owns the retry, its
    5 s delay and the shared deadline D, and recomputes the archive digest from
    the staged file instead of trusting the worker's report;
  - the owner file `owner.json` is removed from staging after every recorded
    child has exited and before publication, so the entry holds only
    `git-cliff.exe` and `entry.json`;
  - if the guard cannot be opened on the entry just published (removed or
    repaired by another process in between), provisioning reports the actual
    cause and path under the extraction-or-probe stage instead of looping, and
    prints the ready line only once the invocation is usable (plan Q18);
  - the budget value accepts any ASCII digit string in range, leading zeros
    included (`0900` is 900 s);
  - the fixture history is one `git fast-import` stream, which is why
    `GitExecutionContext.run` gains an `input`;
  - "outside a worktree" covers a plain directory (`rev-parse
    --is-inside-work-tree` exits 128 with `fatal: not a git repository`), a
    bare repository and a `.git` directory (it prints `false`); every other
    discovery failure is a launcher failure (69), and `discover_project` keeps
    its behavior for every other caller;
  - the first 2.7.0 download is bounded by the asset size from its
    certificate-verified release metadata, the parent computes its digest, and
    the trust record is written once after extraction and probe (plan Q19);
  - the platform check reads `sys.getwindowsversion().platform_version`, since
    Windows 10 and Windows Server 2016 both report 10.0;
  - the committed bundle lives at `tools/release_workflow/git_cliff/bundles/2.14.2/`,
    the location the manifest's `evidence` field names;
  - the worker's statuses 0, 75 and 65 are internal to the parent and worker
    pair and never reach a caller.
- **Evidence provenance**: the 2.7.0 trust record states the evidence-only
  authorization of 2026-11-13 and that HTTPS, not an upstream digest, anchors
  its first download; the audit names the commit it read.

Roll out by keeping every legacy path unchanged: `uc` and
`update-changelog.sh` keep the global 2.7.0 binary until item 4 and the
consumer migrations switch them, and `senv.doskey` stays unedited until item 8.
No version command, build or curated path imports provisioning. No private
path or sensitive term is needed by any planned file, fixture or evidence
record.

---

## Implementation decisions for v0.14.0 git-cliff-provisioning

The user decided each question after an explanation on 2026-11-15, always
choosing the recommended option; Q11 carries the user's amendment on the test
folder. Independent review round 4 checked the nineteen decisions for
consistency with each other and with the requirement, the design and the
umbrella, and found no missing question. The question blocks are kept in the
commit `docs(plan): record pre-consolidation questions`.

| Question | Decision | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | A: Step 3 adds `/.tools/git-cliff/` to the root `.gitignore` with the first code that writes under it (the cache lock); the Step 2 native checks use temporary paths | Step 3; Step 2 native checks; Runtime file note; risk pass | B: Step 4 with the downloader (lock records written one commit before the rule); C: Step 1 (an entry for a path no code of that commit knows) |
| Q02 | A: the strict JSON record helpers move to `lock_records.py`, used by the operation lock with unchanged messages and by the four git-cliff records | Steps 1 and 3 | B: copies in `git_cliff/cache.py` (two copies can drift); C: importing the private `operation_lock` helpers (couples the cache lock to the project lock) |
| Q03 | B: the harness and the Git input change in Step 6; the evidence run, audit, user review and admission of 2.14.2 in Step 7; the launcher, alias, integrated acceptance, final native run and documentation in Step 8 | Plan goal; Steps 6 to 8; confirmed facts; acceptance ownership map; risk pass; validation plan | A: launcher in Step 6 before the harness (launcher tried only on synthetic pins, heaviest final step); C: a throwaway admission script after Step 5 (needs a design change) |
| Q04 | B: three native modules from Step 2: `windows_native.py` (structures, constants, kernel loader), `windows_child.py` (lifecycle) and `windows_guard.py` (guard) | Step 2; scope anchors; confirmed facts | A: two modules split only past 650 lines (the child module reaches about 530 lines, near the risk band); C: one module (about 660 lines, over the ceiling) |
| Q05 | A: an explicit `api` parameter takes the fake kernel; the default loader is covered through a fake loader and the declarations without operating-system calls, including the post-creation, retention, daemon-reader and pre-identity cases | Step 2 | B: monkeypatching `_kernel` (a forgotten patch reaches the real kernel); C: native wrappers omitted from coverage (breaks the 100% gate) |
| Q06 | B: the native check recorder is created in Step 2 and extended in Steps 4 and 5; each milestone's due checks are committed and validated as passing for the current sources; Step 5 uses a synthetic pin and a stand-in caller; Step 8 reruns the full set with the production launcher | Steps 2, 4, 5 and 8; shared checklist item 6; command templates; acceptance ownership map; risk pass | A: every native check only in the final step (a native surprise found after four steps); C: incremental runs with one final committed record (intermediate results only in private notes) |
| Q07 | A: the recorder `tests/unit/tools/release_workflow/git_cliff_native_checks.py` is started by hand; the record `test_git_cliff_native_evidence/native_checks.v1.json` is validated for passing outcomes, expected observations, bounds and current source digests | Step 2; Runtime file note | B: recorder as an engine module (fake-only production coverage of process-starting code); C: results in the validation plan only (nothing a test can check) |
| Q08 | A: the bundle lives in `tools/release_workflow/git_cliff/bundles/2.14.2/`, cited by the manifest's `evidence` field | Steps 6 and 7; Runtime file note | B: `docs/v0.14.0/evidence/` (engine and item 4 read the docs tree); C: a test data leaf (the shipped manifest cites a test directory) |
| Q09 | A: one `git fast-import` stream through `GitExecutionContext.run(..., input=...)`, which passes the bytes without also setting stdin and keeps today's stdin rule otherwise | Step 6 | B: plumbing commands with per-call environments (many ordered calls, still needs input); C: a harness-owned subprocess call (breaks the single Git boundary) |
| Q10 | A: the parent recomputes the SHA-256 of the staged archive before extraction instead of trusting the worker's report | Step 4; Step 6 candidates | B: trusting the worker's report (a worker defect would pass); C: recomputing and comparing with the report (a second failure path that adds nothing) |
| Q11 | B with the user's amendment: one leaf per production module with topic files prefixed by the module name, all directly in `tests/unit/tools/release_workflow/`, with no `git_cliff` level and no groundhog named group; acceptance and evidence leaves keep the item 2 naming | Test-tree snapshot; shared test architecture; Steps 2 to 8 file lists | A: the topic-named leaves (tests of a module harder to find); C: one file per module (the provisioning file over 650 lines) |
| Q12 | B: three helper modules by concern: `git_cliff_support.py` (Step 3), `git_cliff_children_fake.py` (Step 5) and `git_cliff_harness_fake.py` (Step 6); `native_kernel_fake.py` stays separate | Shared test architecture; Steps 3 to 6 | A: one support module split near 550 lines (a late split rewrites reviewed imports); C: fakes in each leaf's `conftest.py` (shared fakes duplicated) |
| Q13 | A: `bin\gcliff.bat` saves the console code page, switches to 65001 and restores it, checked after a readiness error and after a normal child return | Step 8 | B: no code page handling (a non-ASCII checkout path is misread and `gcliff` returns 69); C: switching only for non-ASCII records (batch cannot test bytes before decoding them) |
| Q14 | A: a ctypes handler routine returning true for `CTRL_C_EVENT` and `CTRL_BREAK_EVENT`, registered only while the launcher waits, kept referenced and removed on success and on errors; never the inherited null routine | Step 2; Step 8; risk pass | B: ignoring `SIGINT` and `SIGBREAK` (relies on C runtime internals); C: catching `KeyboardInterrupt` in a polling wait (a second Ctrl+C can end the launcher) |
| Q15 | A: one `bootstrap.py` with module-level `_ENGINES`, `_UNNORMALIZED_KINDS` and `_FAILURE_STATUS` tables, keeping the single set literal in `main`; worker and `gcliff` statuses tested independently of the release kinds | Steps 4 and 8 | B: separate bootstrap scripts (two more entry scripts to keep in step); C: routing `gcliff` through `cli.main` (normalizes statuses) |
| Q16 | B as revised in review round 1: a `review` member in `bundle.json` (decision, reviewer `user`, date, `covered_sha256` of the canonical projection without `review`) and a `files` member with the SHA-256 of `cliff.toml` and both trust records; `require_admissible` refuses an absent, rejected, malformed or stale review and any tampered listed file; the step journal records the review too | Step 6 (bundle and harness); Step 7 (human gate and admission test); Runtime file note | A: step journal only (no committed trace of the review); C: a separate review document (two files for one fact) |
| Q17 | A: a by-hand audit with a written checklist (shallow clone of `v2.14.2` outside the repository, files and call sites per exit-path category, dependency versions and source references), with the commands and the audited commit recorded in `bundle.json`; observed statuses only corroborate | Step 7 | B: a harness-assisted pattern list (can miss a path, so the reading is still needed); C: observed statuses only (does not prove the exclusion of 69) |
| Q18 | A: a newly published entry that cannot be guarded fails once under the extraction-or-probe stage, naming the actual cause and path, with no rerun; the ready line is printed only for a usable invocation | Step 5; risk pass | B: rerunning the flow once (two downloads and doubled budgets in one call) |
| Q19 | A: 2.7.0's first acquisition reads the asset name and exact size from certificate-verified release metadata, downloads through the ordinary recorded worker under D with one retry, lets the parent compute the digest and writes the trust record once after extraction and probe; the exception stays limited to 2.7.0 | Step 6 (`candidates.acquire_candidate`); risk pass | B: an evidence-only worker mode with a fixed size cap (a limit the design does not define) |
