# v0.14.0 git-cliff-provisioning implementation plan -- pinned git-cliff on demand

Add pinned git-cliff provisioning to the item 1 release engine: a tested-pin
manifest, contained Windows children, a guarded cache under a bounded lock, the
`gcliff` launcher and the compatibility evidence that admits 2.14.2, each
delivered behind tests that start no process.

- **Pins and budgets**: the tested-pin manifest, the `[git-cliff]` domain of
  the common reader and the download budget policy read once per caller.
- **Contained execution and the cache**: suspended creation inside a
  parent-only kill-on-close job, the use guard, the entry record, the cache
  lock with owner-aware recovery, the download worker and single-member
  extraction.
- **Provisioning, launcher and evidence**: the provisioning service and its
  invocation object, the `gcliff` launcher and alias fragment, the comparison
  harness and the bundle that admits 2.14.2.

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
- **Step 2 goal**: the Windows child lifecycle (platform baseline,
  parent-only kill-on-close job, suspended creation with a job list and a
  handle list, recording before resume, deadline termination) and the use
  guard.
- **Step 3 goal**: the cache layout, the entry record and owner file, the
  lock-free reuse check, the cache lock with bounded waiting and owner-aware
  recovery, and the root `.gitignore` entry.
- **Step 4 goal**: the network client, the download worker started through
  the bootstrap, archive verification and single-member extraction.
- **Step 5 goal**: the provisioning service, its invocation object with the
  engine and passthrough policies, messages, diagnostics and statuses, and the
  entry point items 4 and 5 call.
- **Step 6 goal**: `bin/gcliff.bat`, the `gcliff-batch` entry kind, worktree
  pin selection, passthrough with status 69 for every failure before
  git-cliff starts, and the alias fragment.
- **Step 7 goal**: the compatibility evidence harness: candidate identities
  and immutable trust records, the deterministic snapshot-tag fixture, the
  controlled comparison and the compact bundle model.
- **Step 8 goal**: the recorded evidence run and exit-path audit, the reviewed
  admission of 2.14.2 as the tested default, integrated acceptance, the
  developer-run native checks and the reference documentation.

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
  `windows_child.py` and `windows_guard.py`, and the shared record decoder
  `lock_records.py`.
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
  `git_cliff_support.py` and `native_kernel_fake.py`.

**Files below 550 and safe to extend** (current lines, expected additions):

| Existing file | Lines | Planned use |
| --- | --- | --- |
| `tools/release_workflow/schemas.py` | 220 | Step 1: git-cliff domain; advisory final 250 |
| `tools/release_workflow/operation_lock.py` | 261 | Step 1: use the shared record decoder; advisory final 235 |
| `tools/release_workflow/__init__.py` | 11 | Step 1: docstring names the `git_cliff` package |
| `tools/release_workflow/bootstrap.py` | 201 | Steps 4 and 6: worker and `gcliff-batch` entry kinds; advisory final 255 |
| `tools/release_workflow/invocation.py` | 199 | Step 6: `gcliff-batch` in `ENTRY_KINDS`; advisory final 201 |
| `tools/release_workflow/git.py` | 331 | Steps 6 and 7: worktree-presence observation, optional input bytes; advisory final 365 |
| `tools/release_workflow/paths.py` | 164 | Step 6: `find_worktree` for `gcliff`; advisory final 185 |
| `tools/release_workflow/windows_process.py` | 132 | Reference, reused unchanged |
| `tools/release_workflow/configuration.py` | 160 | Reference, unchanged |
| `tools/release_workflow/cli.py` | 176 | Reference, unchanged: no shipped handler is added |
| `tools/release_workflow/results.py` | 53 | Reference, unchanged |
| `tools/release_workflow/runtime_identity.py` | 162 | Reference, unchanged |
| `tests/unit/tools/release_workflow/launcher_simulation.py` | 210 | Step 6: route the `gcliff` entry; advisory final 260 |
| `tests/unit/tools/release_workflow/conftest.py` | 132 | Reference, unchanged |
| `tests/unit/tools/release_workflow/test_schemas/test_schemas_tdd.py` | 151 | Steps 1 and 8; advisory final 180 |
| `tests/unit/tools/release_workflow/test_configuration/test_configuration_tdd.py` | 256 | Steps 1 and 8; advisory final 290 |
| `tests/unit/tools/release_workflow/test_operation_lock/test_operation_lock_tdd.py` | 337 | Step 1 regression, unchanged |
| `tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py` | 212 | Steps 4 and 6; advisory final 300 |
| `tests/unit/tools/release_workflow/test_invocation/test_invocation_tdd.py` | 200 | Step 6; advisory final 212 |
| `tests/unit/tools/release_workflow/test_git/test_git_tdd.py` | 232 | Steps 6 and 7; advisory final 275 |
| `tests/unit/tools/release_workflow/test_paths/test_paths_tdd.py` | 174 | Step 6; advisory final 195 |
| `tests/unit/tools/release_workflow/test_launchers/test_codepage_tdd.py` | 161 | Steps 4 and 6 regression, unchanged |

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
- `tools/release_workflow/windows_child.py`,
  `tools/release_workflow/windows_guard.py` and
  `tools/release_workflow/lock_records.py`.
- `bin/gcliff.bat` and `bin/gcliff.doskey`.
- `tests/unit/tools/release_workflow/git_cliff_support.py`,
  `native_kernel_fake.py`, `git_cliff_native_checks.py` and every
  `test_git_cliff_*`, `test_gcliff_*`, `test_windows_child`,
  `test_windows_guard` and `test_lock_records` test leaf.
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
  reviewed manifest edit that follows its evidence. Steps 1 to 7 ship an
  empty admitted tuple: the rule has no default, any declared version is
  refused with `tested: none`, and provisioning without a pin raises the
  configuration-stage diagnostic. Unit tests build synthetic pin tables. Step 8
  adds 2.14.2 as the default.
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
  record read by its test; the native check recorder follows that convention.

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

New test leaf directories to create (each with an `__init__.py` holding a
one-line docstring and `# eof`):

- `tests/unit/tools/release_workflow/test_lock_records/` (Step 1).
- `tests/unit/tools/release_workflow/test_git_cliff_manifest/` (Step 1).
- `tests/unit/tools/release_workflow/test_git_cliff_budget/` (Step 1).
- `tests/unit/tools/release_workflow/test_windows_child/` (Step 2).
- `tests/unit/tools/release_workflow/test_windows_guard/` (Step 2).
- `tests/unit/tools/release_workflow/test_git_cliff_cache/` (Step 3).
- `tests/unit/tools/release_workflow/test_git_cliff_lock/` (Step 3).
- `tests/unit/tools/release_workflow/test_git_cliff_network/` (Step 4).
- `tests/unit/tools/release_workflow/test_git_cliff_worker/` (Step 4).
- `tests/unit/tools/release_workflow/test_git_cliff_archive/` (Step 4).
- `tests/unit/tools/release_workflow/test_git_cliff_messages/` (Step 5).
- `tests/unit/tools/release_workflow/test_git_cliff_invocation/` (Step 5).
- `tests/unit/tools/release_workflow/test_git_cliff_provisioning/` (Step 5).
- `tests/unit/tools/release_workflow/test_git_cliff_lifecycle/` (Step 5).
- `tests/unit/tools/release_workflow/test_gcliff_launcher/` (Step 6).
- `tests/unit/tools/release_workflow/test_git_cliff_candidates/` (Step 7).
- `tests/unit/tools/release_workflow/test_git_cliff_fixture/` (Step 7).
- `tests/unit/tools/release_workflow/test_git_cliff_comparison/` (Step 7).
- `tests/unit/tools/release_workflow/test_git_cliff_bundle/` (Step 7).
- `tests/unit/tools/release_workflow/test_git_cliff_acceptance/` (Step 8).
- `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/` (Step 8).

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
  not runtime output (`bundle.json`, `cliff.toml`, `trust.2.14.2.json`,
  `trust.2.7.0.json`). The trust records are written once by the harness and
  never rewritten.
- `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json`:
  committed evidence of the developer-run native checks, with no absolute
  path, user name or host name.
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
6. Count lines after the edits and compare them with the step's line-budget
   checkpoint. A Python file above 650 lines stops the step until the split
   guidance is applied; an advisory estimate exceeded at or below 650 is
   recorded as variance, not missing work.
7. Record evidence and counts in the matching step of the
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
- Evidence harness (Step 8, outside pytest, from the project root, network
  required): `& .\venvs\<project venv>\Scripts\python.exe -m tools.release_workflow.git_cliff.harness --bundle tools\release_workflow\git_cliff\bundles\2.14.2 --pin 2.14.2 --baseline 2.7.0`.
- Native check recorder (Step 8, outside pytest, from the project root):
  `& .\venvs\<project venv>\Scripts\python.exe -m tests.unit.tools.release_workflow.git_cliff_native_checks --output tests\unit\tools\release_workflow\test_git_cliff_native_evidence\native_checks.v1.json`.

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
- **Shared builders**: `tests/unit/tools/release_workflow/git_cliff_support.py`
  (created in Step 3, extended by Steps 4 to 8) holds a fake clock whose
  `sleep` advances time, declared process states keyed by `ProcessIdentity`,
  an uncontended transition mutex, a synthetic `AdmittedPin` for 2.14.2 built
  from a small generated archive (its real size and SHA-256 computed in the
  test), a fake guard opener over scenario files, a fake child launcher that
  plays scripted outcomes (exit, never finishes, parent death at a named
  boundary), and a write-denying filesystem helper that makes every
  `mkdir`, `rename`, `replace`, `remove`, `rmdir` and write-mode `open` raise
  `PermissionError` and records the attempts.
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
  admitted tuple until Step 8, the pin converter and the derived download URL.
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
  clarifications Q01, Q02, Q11, Q16.
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

Expected outcome:

- No code path creates a child outside its job or falls back to
  `subprocess` or to create-then-assign; every failure before resume leaves
  no running child.
- No path blocks on the output pipes before every job member has ended, so a
  descendant holding a pipe write end cannot defeat a deadline.
- A returned outcome always means a confirmed end; an unconfirmed end raises a
  distinct error after which no caller cleans up.
- Every branch of the native layer is covered through the fake kernel.

Step framing:

- Design link: "Child process lifecycle", "Deadline enforcement", "Reuse check
  and the use guard", "Foundation changes required by git-cliff
  provisioning"; design decisions Q07, Q10, Q17; the confirmed facts on job
  objects, process attributes, nested jobs and `subprocess`.
- Execution checklist reference: [Shared execution command checklist for all
  v0.14.0 git-cliff-provisioning steps](#shared-execution-command-checklist-for-all-v0140-git-cliff-provisioning-steps).

#### Step 2 -- implementation for the Windows layer

**Files involved**:

- `tools/release_workflow/windows_child.py` (new, to be created).
- `tools/release_workflow/windows_guard.py` (new, to be created).
- `tests/unit/tools/release_workflow/native_kernel_fake.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_windows_child/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_windows_child/test_windows_child_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_windows_child/test_windows_child_faults_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_windows_guard/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_windows_guard/test_windows_guard_tdd.py` (new, to be created).

**Tests first**:

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
  routine (whose ignore flag children would inherit), and removes it on exit.
- Guard: `open_guard` calls `CreateFileW` with `GENERIC_READ`,
  `FILE_SHARE_READ`, `OPEN_EXISTING` and no security attributes; a missing
  file raises `FileNotFoundError`; a sharing violation raises `OSError` with
  the Windows error; `sha256_and_size()` reads through a duplicated handle and
  closes only that duplicate; `close()` is idempotent.
- PBT: not needed in this step; the native call sequences are finite and
  parametrized exhaustively.

**Classes and behavior**:

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

**Completion criteria**:

- The command printed by `pw scope day` reports the objective (`exit=0`) in
  the current effort scope.
- `rg -n 'subprocess\.(Popen|run|call)|AssignProcessToJobObject' tools/release_workflow/windows_child.py tools/release_workflow/windows_guard.py`
  finds no match.
- `rg -n 'SetConsoleCtrlHandler' tools/release_workflow` shows only the
  handler-routine registration and removal.
- `rg -n 'TerminateJobObject|\.join\(' tools/release_workflow/windows_child.py`
  shows the reader join only after the teardown helper.
- Coverage of both modules is 100% through the fake kernel.

#### Step 2 -- addendums for the Windows layer

Line-budget checkpoint:

- [ ] `tools/release_workflow/windows_child.py`: before 0; below-550 safe; repository ceiling <= 650; expected 530 with the teardown, pre-resume and retention paths (advisory; close to the risk band, which Q04 option B would avoid).
- [ ] `tools/release_workflow/windows_guard.py`: before 0; below-550 safe; ceiling <= 650; expected 130 (advisory).
- [ ] `tests/unit/tools/release_workflow/native_kernel_fake.py`: before 0; ceiling <= 650; expected 310 with declared descendants and pipes (advisory).
- [ ] New test files: before 0; ceiling <= 650; expected 280, 380 and 140 (advisory).

Split guidance:

- If `windows_child.py` would pass 650, move the ctypes structure and
  signature declarations (`STARTUPINFOEXW`, `PROCESS_INFORMATION`,
  `JOBOBJECT_EXTENDED_LIMIT_INFORMATION` and the `_kernel` loader) into
  `windows_native.py`, keeping `run_contained` and its steps in place.

Full workflow timing run readiness:

- `ghog single` on the Step 2 test files and `test_windows_process`, then the
  command printed by `pw scope day`.

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
  Q07, Q12; requirement clarifications Q03, Q04, Q05, Q06, Q14.
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
- `tests/unit/tools/release_workflow/test_git_cliff_lock/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_lock/test_git_cliff_lock_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_lock/test_git_cliff_recovery_tdd.py` (new, to be created).

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

Expected outcome:

- One attempt reports `ok`, `retryable` (connection error, reset, HTTP 429 or
  5xx) or `fatal` (another HTTP 4xx, size overflow), and a `Retry-After`
  header changes nothing.
- Extraction writes only `git-cliff.exe` in staging, from the manifest member,
  with its uncompressed size checked and its bytes hashed.

Step framing:

- Design link: "Download, verification and extraction", "Deadline
  enforcement", "Time budgets and retries"; design decisions Q01, Q06, Q08;
  requirement clarifications Q07, Q15.
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
- `tests/unit/tools/release_workflow/test_git_cliff_worker/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_worker/test_git_cliff_worker_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_archive/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_archive/test_git_cliff_archive_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_archive/test_git_cliff_archive_pbt.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py` (existing, to be updated).

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

**Completion criteria**:

- The command printed by `pw scope day` reports the objective (`exit=0`) in
  the current effort scope.
- `rg -n 'CERT_NONE|check_hostname|_create_unverified_context|Retry-After' tools/release_workflow/git_cliff`
  shows no verification bypass and no header use.
- `rg -n 'extractall|extract\(' tools/release_workflow/git_cliff/archive.py`
  finds no whole-archive extraction.
- `rg -n 'api.github.com' tools/release_workflow/git_cliff/network.py tools/release_workflow/git_cliff/download_worker.py`
  finds nothing outside the metadata mode's caller-supplied URL.

#### Step 4 -- addendums for the download

Line-budget checkpoint:

- [ ] `tools/release_workflow/git_cliff/network.py`: before 0; below-550 safe; repository ceiling <= 650; expected 190 (advisory).
- [ ] `tools/release_workflow/git_cliff/download_worker.py`: before 0; below-550 safe; ceiling <= 650; expected 150 (advisory).
- [ ] `tools/release_workflow/git_cliff/archive.py`: before 0; below-550 safe; ceiling <= 650; expected 80 (advisory).
- [ ] `tools/release_workflow/bootstrap.py`: before 201; below-550 safe; ceiling <= 650; expected +25 (advisory).
- [ ] `tests/unit/tools/release_workflow/git_cliff_support.py`: before about 230; ceiling <= 650; expected +60 (advisory).
- [ ] New test files: before 0; ceiling <= 650; expected 220, 170, 160 and 50 (advisory).
- [ ] `tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py`: before 212; ceiling <= 650; expected +35 (advisory).

Split guidance:

- None expected.

Full workflow timing run readiness:

- `ghog single` on the Step 4 test files and `test_launchers`, then the
  command printed by `pw scope day`.

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
  clarifications Q03, Q06, Q08, Q14, Q15.
- Execution checklist reference: [Shared execution command checklist for all
  v0.14.0 git-cliff-provisioning steps](#shared-execution-command-checklist-for-all-v0140-git-cliff-provisioning-steps).

#### Step 5 -- implementation for provisioning

**Files involved**:

- `tools/release_workflow/git_cliff/messages.py` (new, to be created).
- `tools/release_workflow/git_cliff/invocation.py` (new, to be created).
- `tools/release_workflow/git_cliff/installation.py` (new, to be created).
- `tools/release_workflow/git_cliff/provisioning.py` (new, to be created).
- `tests/unit/tools/release_workflow/git_cliff_support.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_git_cliff_messages/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_messages/test_git_cliff_messages_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_invocation/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_invocation/test_git_cliff_invocation_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_provisioning/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_reuse_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_installation_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_contention_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_budget_flow_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_lifecycle/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_lifecycle/test_git_cliff_lifecycle_tdd.py` (new, to be created).

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
- Reuse (`test_git_cliff_reuse_tdd.py`): a valid entry returns an invocation
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
- Contention (`test_git_cliff_contention_tdd.py`): two first uses produce one
  download, the second caller prints the waiting line and reuses the entry
  after its recheck; a lock left by a `DEAD` owner with `DEAD` children is
  recovered and its staging removed; `UNKNOWN` and `ALIVE` owners and children
  are preserved and the waiter fails at W; a repair attempt between a caller's
  validation and its child start is refused by the guard.
- Budget flow (`test_git_cliff_budget_flow_tdd.py`): unset, `900` and `3600`
  give the D and W the worker deadline and the waiting line show; each
  refused form fails before any guard, probe, child, network or cache access,
  also with a valid entry; `900` with a reset and `Retry-After: 2000` keeps
  the delay and the retry inside 900 s; `3600` keeps the probe at 15 s; a
  default waiter behind a holder declared with D = 1800 fails at 360 s and
  keeps the holder's lock and staging.
- Lifecycle (`test_git_cliff_lifecycle_tdd.py`), one case per boundary of the
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

#### Step 5 -- addendums for provisioning

Line-budget checkpoint:

- [ ] `tools/release_workflow/git_cliff/messages.py`: before 0; below-550 safe; repository ceiling <= 650; expected 160 (advisory).
- [ ] `tools/release_workflow/git_cliff/invocation.py`: before 0; below-550 safe; ceiling <= 650; expected 140 (advisory).
- [ ] `tools/release_workflow/git_cliff/installation.py`: before 0; below-550 safe; ceiling <= 650; expected 320 with the retirement states and unconfirmed-end handling (advisory).
- [ ] `tools/release_workflow/git_cliff/provisioning.py`: before 0; below-550 safe; ceiling <= 650; expected 240 (advisory).
- [ ] `tests/unit/tools/release_workflow/git_cliff_support.py`: before about 290; ceiling <= 650; expected +150 (advisory).
- [ ] New test files: before 0; ceiling <= 650; expected 130, 170, 200, 300, 260, 230 and 320 (advisory).

Split guidance:

- If `git_cliff_support.py` would pass 650, move the fake child launcher and
  its boundary script into `git_cliff_children_fake.py`.
- If `installation.py` would pass 650, move retirement and publication into
  `git_cliff/publication.py`.

Full workflow timing run readiness:

- `ghog single` on the Step 5 test files, then the command printed by
  `pw scope day`.

Time-gated status for Step 5:

- No perf gate is affected; every budget is asserted against the fake clock.

---

### Step 6. The gcliff launcher, its entry kind and the alias fragment

#### Step 6 -- analysis and intent for gcliff

Issues to address:

- No launcher runs git-cliff for the current worktree's pin, and the release
  launcher maps every status outside 0 to 3 to 1.
- Discovery cannot tell "no worktree here" (a plain directory, a bare
  repository, a `.git` directory) from a genuine discovery failure.
- No tested alias line exists for `gcliff`.

Fix intent:

- Ship `bin/gcliff.bat` and the `gcliff-batch` entry kind, which selects
  `git_cliff/launcher.py`, reports readiness and argument failures as 69 and
  returns git-cliff's status unchanged.
- Add a typed worktree-presence observation to `git.py` and a
  `paths.find_worktree` used only by `gcliff`; `discover_project` and its
  other callers keep their behavior.
- Ship `bin/gcliff.doskey`, the single-line alias fragment.

Expected outcome:

- `gcliff` in a nested folder of a pinned worktree runs that pin; outside a
  worktree, or without a pin, the default applies after whole-file validation;
  arguments, output, status and environment pass through.
- Every failure before git-cliff starts returns 69 with its diagnostic.

Step framing:

- Design link: "The gcliff launcher", "Selecting the project and the pin",
  "Statuses"; design decisions Q09, Q10, Q11, Q16; requirement clarifications
  Q08, Q09, Q10, Q11, Q12.
- Execution checklist reference: [Shared execution command checklist for all
  v0.14.0 git-cliff-provisioning steps](#shared-execution-command-checklist-for-all-v0140-git-cliff-provisioning-steps).

#### Step 6 -- implementation for gcliff

**Files involved**:

- `bin/gcliff.bat` (new, to be created).
- `bin/gcliff.doskey` (new, to be created).
- `tools/release_workflow/git_cliff/launcher.py` (new, to be created).
- `tools/release_workflow/bootstrap.py` (existing, to be updated).
- `tools/release_workflow/invocation.py` (existing, to be updated).
- `tools/release_workflow/git.py` (existing, to be updated).
- `tools/release_workflow/paths.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/launcher_simulation.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_gcliff_launcher/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_gcliff_launcher/test_gcliff_launcher_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_launchers/test_gcliff_source_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_invocation/test_invocation_tdd.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_git/test_git_tdd.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_paths/test_paths_tdd.py` (existing, to be updated).

**Tests first**:

- Launcher, through the launcher simulation with a fake provisioning seam
  and a fake child launcher: `gcliff --version` in a nested folder of a
  worktree with `[git-cliff] version = 2.14.2` (synthetic manifest) provisions
  and runs that pin; in a plain directory, a bare repository, a `.git`
  directory and a worktree without a pin the default is used after
  validation; an invalid `[source:npm]` section returns
  69 with the reader diagnostic and starts no child; a git-cliff status of 1,
  2 or 3 returns unchanged; `--workdir <other repository>` does not change the
  selected pin; a `%`, `^`, `!` or `"` argument returns 69; an invalid budget
  value returns 69 even with a valid entry; `GIT_CLIFF_*` variables reach the
  child; the console filter is active only while the child runs; a genuine
  discovery failure (exit 128 with another diagnostic, such as a dubious
  ownership refusal, or a rejected configuration) returns 69.
- Bootstrap: `gcliff-batch` readiness failure returns 69 with the "run this
  checkout's setup" message; a reserved `--entry-kind` in its arguments
  returns 69; its status is returned unchanged for 0, 1, 2, 3, 69 and 101.
- Batch source contract (`test_gcliff_source_tdd.py`): `bin/gcliff.bat` keeps
  the self-location, codepage save and restore and runtime record blocks of
  the release launchers, sets `_release_status=69` before the record checks,
  runs `-I -X utf8 "%_release_root%\tools\release_workflow\bootstrap.py"
  --entry-kind gcliff-batch -- %*`, and has no status normalization line.
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

**Classes and behavior**:

- `launcher.main(arguments, *, original_cwd, tooling_root, runtime,
  environment=None, seams=None) -> int`: validates the arguments with the
  batch guard, creates the Git context, finds the worktree with
  `paths.find_worktree` (or none), loads the configuration, takes `configured_pin` or
  the manifest default, resolves the budget, provisions, then runs the
  passthrough policy inside `ignore_console_interrupts()` and returns the
  child's status. Every failure before the child starts writes its diagnostic
  and returns 69 (`GCLIFF_UNAVAILABLE = 69`).
- `bootstrap`: `entry` accepts `gcliff-batch`; `_ENGINES` maps it to
  `tools.release_workflow.git_cliff.launcher`; `_UNNORMALIZED_KINDS` includes
  it; a `_FAILURE_STATUS` table gives 69 for its readiness and invocation
  failures and 2 for the release kinds.
- `invocation.ENTRY_KINDS` gains `gcliff-batch`.
- `git.WorktreePresence` (enum: `INSIDE`, `NO_WORKTREE`, `NO_REPOSITORY`) and
  `GitExecutionContext.worktree_presence(*, cwd)`: one
  `rev-parse --is-inside-work-tree` call through `run` with `check=False`,
  classified on its exit code, stdout and untranslated stderr.
  `paths.find_worktree(start, git) -> ProjectIdentity | None`.
- `bin/gcliff.bat`: the release launcher's self-location, codepage handling
  and runtime record reading, status 69 for every pre-Python failure, then
  `exit /b %_release_status%` with git-cliff's status.

**Completion criteria**:

- The command printed by `pw scope day` reports the objective (`exit=0`) in
  the current effort scope.
- `rg -n 'gcliff' senv.doskey` finds no match.
- `rg -n 'returning 1' bin/gcliff.bat` finds no normalization.
- The cross-site status contract of `test_codepage_tdd.py` still passes
  unchanged.

#### Step 6 -- addendums for gcliff

Line-budget checkpoint:

- [ ] `tools/release_workflow/git_cliff/launcher.py`: before 0; below-550 safe; repository ceiling <= 650; expected 150 (advisory).
- [ ] `tools/release_workflow/bootstrap.py`: before about 226; below-550 safe; ceiling <= 650; expected +30 (advisory).
- [ ] `tools/release_workflow/invocation.py`: before 199; below-550 safe; ceiling <= 650; expected +1 (advisory).
- [ ] `tools/release_workflow/git.py`: before 331; below-550 safe; ceiling <= 650; expected +12 (advisory).
- [ ] `tools/release_workflow/paths.py`: before 164; below-550 safe; ceiling <= 650; expected +12 (advisory).
- [ ] `tests/unit/tools/release_workflow/launcher_simulation.py`: before 210; below-550 safe; ceiling <= 650; expected +45 (advisory).
- [ ] New test files: before 0; ceiling <= 650; expected 300 and 90 (advisory).
- [ ] Updated test files: before about 247, 200, 232 and 174; ceiling <= 650; expected +40, +5, +20 and +15 (advisory).
- [ ] `bin/gcliff.bat` and `bin/gcliff.doskey`: non-Python, about 75 lines and 1 line.

Split guidance:

- If `test_gcliff_launcher_tdd.py` would pass 650, move the failure-status
  cases into `test_gcliff_failures_tdd.py`.

Full workflow timing run readiness:

- `ghog single` on the Step 6 test files, `test_launchers` and
  `test_release_acceptance`, then the command printed by `pw scope day`.

Time-gated status for Step 6:

- No perf gate is affected.

---

### Step 7. Compatibility evidence harness

#### Step 7 -- analysis and intent for the harness

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
  certificate-verified release metadata, as Q19 recommends while it is
  pending), trust records written once and compared later, and candidate
  provisioning through the evidence namespace of the Step 3 to 5 primitives.
- Ship `git_cliff/fixture_history.py`: the committed script building the
  snapshot-tag fixture through one `git fast-import` stream that fixes every
  object-producing input.
- Ship `git_cliff/comparison.py`: frozen inputs, the temporary worktree, the
  range list, the runs through the engine policy with one explicit
  environment, digests, statuses and hunks.
- Ship `git_cliff/bundle.py`: the bundle model, its strict reader and writer,
  and its completeness checks; and `git_cliff/harness.py`, the developer
  entry point.
- Add an optional `input` to `GitExecutionContext.run`.

Expected outcome:

- The harness never writes the manifest, never reaches the production
  namespace and fails on a changed trust record, a changed fixture hash or a
  changed rerun digest.
- Its pure logic is covered by unit tests with fakes; only the real run is by
  hand.

Step framing:

- Design link: "Compatibility evidence harness and bundle", "Statuses";
  design decisions Q11, Q12, Q13, Q14, Q15; requirement clarifications Q13,
  Q16.
- Execution checklist reference: [Shared execution command checklist for all
  v0.14.0 git-cliff-provisioning steps](#shared-execution-command-checklist-for-all-v0140-git-cliff-provisioning-steps).

#### Step 7 -- implementation for the harness

**Files involved**:

- `tools/release_workflow/git_cliff/candidates.py` (new, to be created).
- `tools/release_workflow/git_cliff/fixture_history.py` (new, to be created).
- `tools/release_workflow/git_cliff/comparison.py` (new, to be created).
- `tools/release_workflow/git_cliff/bundle.py` (new, to be created).
- `tools/release_workflow/git_cliff/harness.py` (new, to be created).
- `tools/release_workflow/git.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/git_cliff_support.py` (existing, to be updated).
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
  `audit`, `observed_statuses`; `read(path)`, `write(path)`,
  `require_admissible(bundle)`.
- `harness.main(arguments) -> int`: `--bundle`, `--pin`, `--baseline`;
  resolves the budget once, acquires or compares candidates, builds or checks
  the fixture, runs the comparison and writes the bundle, keeping existing
  classification and audit entries by hunk identity. Its
  `if __name__ == "__main__":` line is the only `# pragma: no cover` line.
- `git.GitExecutionContext.run(..., input: bytes | None = None)`.

**Completion criteria**:

- The command printed by `pw scope day` reports the objective (`exit=0`) in
  the current effort scope.
- `rg -n 'manifest' tools/release_workflow/git_cliff/harness.py tools/release_workflow/git_cliff/comparison.py tools/release_workflow/git_cliff/candidates.py`
  shows reads of the manifest only, no write.
- `rg -n 'pragma: no cover' tools/release_workflow/git_cliff` shows only the
  harness entry line.

#### Step 7 -- addendums for the harness

Line-budget checkpoint:

- [ ] `tools/release_workflow/git_cliff/candidates.py`: before 0; below-550 safe; repository ceiling <= 650; expected 260 with the acquisition path (advisory).
- [ ] `tools/release_workflow/git_cliff/fixture_history.py`: before 0; below-550 safe; ceiling <= 650; expected 200 (advisory).
- [ ] `tools/release_workflow/git_cliff/comparison.py`: before 0; below-550 safe; ceiling <= 650; expected 260 (advisory).
- [ ] `tools/release_workflow/git_cliff/bundle.py`: before 0; below-550 safe; ceiling <= 650; expected 190 (advisory).
- [ ] `tools/release_workflow/git_cliff/harness.py`: before 0; below-550 safe; ceiling <= 650; expected 110 (advisory).
- [ ] `tools/release_workflow/git.py`: before about 343; below-550 safe; ceiling <= 650; expected +6 (advisory).
- [ ] `tests/unit/tools/release_workflow/git_cliff_support.py`: before about 440; below-550 safe; ceiling <= 650; expected +50 (advisory).
- [ ] New test files: before 0; ceiling <= 650; expected 280, 170, 260 and 180 (advisory).

Split guidance:

- `git_cliff_support.py` approaches the risk band here: put harness fakes in
  `git_cliff_harness_fake.py` instead if the file would reach 550.

Full workflow timing run readiness:

- `ghog single` on the Step 7 test files and `test_git`, then the command
  printed by `pw scope day`.

Time-gated status for Step 7:

- No perf gate is affected; the harness itself runs only by hand.

---

### Step 8. Evidence run, admission of 2.14.2, acceptance and documentation

#### Step 8 -- analysis and intent for admission and rollout

Issues to address:

- No evidence has been recorded, so the manifest admits nothing and an
  omitted pin has no default.
- The design's developer-run native checks have never run.
- No end-to-end test walks the shipped paths together, and no reference page
  documents the launcher, the cache, the budget variable or the statuses.

Fix intent:

- Run the harness by hand (network required; the 2.7.0 download runs under
  the evidence-only exception the user authorized on 2026-11-13); audit
  git-cliff's exit paths at the `v2.14.2` source tag; classify every hunk;
  present the bundle for the user's review; then admit 2.14.2 as the default
  by a manifest edit that copies the bundle's identity and reference.
- Run the native check recorder by hand and commit its record.
- Add the integrated acceptance tests and the reference documentation.

Expected outcome:

- The manifest holds exactly 2.14.2, default, with the design's identity, and
  the admission test ties it to the committed bundle.
- Every design acceptance row has its unit or acceptance proof, and every
  native row has a recorded check that passed against the current sources.

Step framing:

- Design link: "Candidate lifecycle and admission order", "Outputs and
  classification", "Statuses", "Acceptance cases for the git-cliff
  provisioning design", "Testing approach under the process-free policy";
  design decisions Q01, Q11, Q13, Q17; requirement clarifications Q01, Q13,
  Q16 and the requirement's acceptance criteria.
- Execution checklist reference: [Shared execution command checklist for all
  v0.14.0 git-cliff-provisioning steps](#shared-execution-command-checklist-for-all-v0140-git-cliff-provisioning-steps).

#### Step 8 -- implementation for admission and rollout

**Files involved**:

- `tools/release_workflow/git_cliff/bundles/2.14.2/bundle.json` (new, to be created).
- `tools/release_workflow/git_cliff/bundles/2.14.2/cliff.toml` (new, to be created).
- `tools/release_workflow/git_cliff/bundles/2.14.2/trust.2.14.2.json` (new, to be created).
- `tools/release_workflow/git_cliff/bundles/2.14.2/trust.2.7.0.json` (new, to be created).
- `tools/release_workflow/git_cliff/manifest.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/git_cliff_native_checks.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_acceptance/__init__.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_acceptance/test_git_cliff_admission_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_acceptance/test_git_cliff_acceptance_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_git_cliff_acceptance/test_gcliff_acceptance_tdd.py` (new, to be created).
- `tests/unit/tools/release_workflow/test_schemas/test_schemas_tdd.py` (existing, to be updated).
- `tests/unit/tools/release_workflow/test_configuration/test_configuration_tdd.py` (existing, to be updated).
- `wiki/reference/git-cliff-provisioning.md` (new, to be created).
- `wiki/reference/aliases-and-launchers.md` (existing, to be updated).
- `wiki/reference/automation-and-direct-invocation.md` (existing, to be updated).
- `wiki/README.md` (existing, to be updated).

**Tests first**:

- Admission: the shipped manifest holds one pin, `2.14.2`, default, with
  `git-cliff-2.14.2-x86_64-pc-windows-msvc.zip`, 7,428,304 bytes, digest
  `6ece2112b3f4af462190ecbea4aeb1315fff6af415629b597f84319073c31131` and
  member `git-cliff-2.14.2/git-cliff.exe`; its evidence reference names
  `tools/release_workflow/git_cliff/bundles/2.14.2`; the bundle passes
  `require_admissible`; its 2.14.2 candidate identity equals the manifest
  entry; `trust.2.7.0.json` never appears in the manifest and `version =
  2.7.0` stays a configuration error.
- Native evidence: a validator in the test module requires, for every check
  of the required set (the design's developer-run list plus the descendant
  teardown and teardown-failure exit checks), outcome `passed`, an
  observation equal to its expected
  observation, a duration within its bound, the recorded commit, and source
  digests equal to the current SHA-256 of every repository file the check
  exercises; host facts (Windows build, architecture) are present and no
  absolute path, user or host name appears. Negative records built in memory
  are each refused: a missing check, `failed`, `timed-out` and `skipped`
  outcomes, an observation differing from its expectation, a duration over
  its bound and a stale source digest.
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
- Schemas and configuration: the shipped default is now `2.14.2`; an omitted
  key yields that defaulted value.

**Classes and behavior**:

- Evidence run, by hand: the harness command of the ready-to-run templates;
  then the exit-path audit of git-cliff at `v2.14.2` (its error return,
  argument-parsing errors, propagated helper statuses, panics and abnormal
  termination, with the audited commit), recorded in `bundle.json` with the
  observed statuses of success, a usage error, a failing render and any
  reachable panic path; then the classification of every hunk as intentional
  with its upstream release-note reason, or as a defect.
- Human gate: present the bundle's classification table and audit to the
  user and wait for their review before the manifest edit. An open defect or
  a version able to return 69 stops admission and goes back to the user.
- `manifest.ADMITTED_PINS`: the one `AdmittedPin` above, after the review.
- `git_cliff_native_checks.py`: started by hand, never imported by a test;
  each check bounds its own run with a timeout, ends every process it
  started and writes its identifier, outcome, expected and observed
  observations, bound, duration, the commit and the SHA-256 of each source
  file it exercises: worker termination against a local endpoint that accepts
  and never answers; `IsProcessInJob` before resume; a suspended child ending
  when its parent is killed; a refused creation under a job with UI limits
  leaving no process; kill-on-close of a worker and of a git-cliff child after
  the parent is killed; a root that exits while a descendant keeps its stdout
  open, returning within the check's bound with the descendant ended; a helper
  parent whose `TerminateJobObject` call is made to fail (through an injected
  `api` wrapper around the real kernel and a real kill-on-close job) while a
  descendant holds its captured pipe, which must still exit normally, after
  which its descendant ends through kill-on-close (the recorder runs the
  helper inside its own bounded job and ends it if it hangs); the
  inherited guard refusing an executable rename while a child runs, after its
  launcher was killed, while a reuse probe runs after its caller was killed
  and while a guard is held between validation and child start; and an
  abandoned transition mutex of a live process leaving its lock record. A
  check that fails, times out or cannot run is recorded as such, and the
  validator then refuses the record, which blocks the step.
- Documentation: `wiki/reference/git-cliff-provisioning.md` covers the pin,
  the tested set, the cache path and ignore rule, the warm-up, the proxy and
  certificate rules, the budget variable, the messages, the statuses and the
  evidence bundle; the two existing pages add `gcliff` and statuses 2 and 69;
  `wiki/README.md` links the new page.

**Completion criteria**:

- The command printed by `pw scope day --full=cov` reports the objective
  (`exit=0`, coverage 100) in the current effort scope.
- `rg -n '2\.14\.2' tools/release_workflow/git_cliff/manifest.py` shows the
  one admitted pin.
- The user's review of the bundle is recorded in the step journal with its
  date before the manifest edit is committed.
- Every row of the
  [acceptance ownership map](#acceptance-ownership-map-for-v0140-git-cliff-provisioning)
  names a passing test or a native check the validator accepts as passed for
  the current sources.

#### Step 8 -- addendums for admission and rollout

Line-budget checkpoint:

- [ ] `tools/release_workflow/git_cliff/manifest.py`: before about 110; below-550 safe; repository ceiling <= 650; expected +12 (advisory).
- [ ] `tests/unit/tools/release_workflow/git_cliff_native_checks.py`: before 0; ceiling <= 650; expected 380 (advisory).
- [ ] New test files: before 0; ceiling <= 650; expected 120, 90, 300 and 220 (advisory).
- [ ] Updated test files: before about 171 and 286; ceiling <= 650; expected +5 and +10 (advisory).
- [ ] Bundle data and wiki pages: non-Python, no Python ceiling.

Split guidance:

- If `git_cliff_native_checks.py` would pass 650, move the guard and mutex
  checks into `git_cliff_native_guard_checks.py`, started by the same entry.

Full workflow timing run readiness:

- `ghog single` on the Step 8 test files, then the command printed by
  `pw scope day`, then `pw scope day --full=cov`.

Time-gated status for Step 8:

- No perf gate is affected; the harness and the native checks run outside
  pytest with their own bounds.

---

## Acceptance ownership map for v0.14.0 git-cliff-provisioning

AC1 to AC6 number the six bullets of the requirement's "Acceptance criteria
for git-cliff provisioning" in their order: pin and reuse (AC1), download,
concurrency, budgets and platform (AC2), failure reporting (AC3), launcher and
alias (AC4), compatibility evidence (AC5), and operations free of git-cliff
with the ignored cache (AC6).

| Design acceptance rows | Requirement | Unit proof | End-to-end or passing native proof |
| --- | --- | --- | --- |
| Default pin with valid cache; `2.15.0`; `v2.14.2` or `latest`; `2.7.0` | AC1, AC5 | Step 1 manifest and configuration tests | Step 8 acceptance |
| Truncated executable; missing `entry.json`; read-only checkout with a valid entry | AC1, AC2 | Step 3 reuse check, Step 5 reuse tests | Step 8 acceptance |
| Two first uses; crashed holder; `UNKNOWN` owner; abandoned mutex with `ALIVE` owner; staging of a live owner | AC2 | Step 3 lock tests, Step 5 contention tests | Native check (abandoned mutex) |
| Stalled download; hung probe | AC2 | Step 2 deadline, descendant and unconfirmed-end tests, Step 5 lifecycle tests | Native checks (stalled endpoint, descendant teardown, teardown-failure exit) |
| Parent death at each boundary; recording failure; child `ALIVE` or `UNKNOWN` after parent death; containment and nesting failures | AC2 | Step 2 fault tests, Step 5 lifecycle tests | Native checks (job membership, suspended child, refused nesting, kill-on-close) |
| Older Windows | AC2 | Step 2 platform tests | Step 8 acceptance |
| Valid-entry reuse probe; caller, harness or launcher death during a child; launcher death before child start | AC2 | Step 5 lifecycle tests | Native checks (inherited guard) |
| Digest mismatch; checkout not writable; invalid entry in use; repair between validation and start | AC2, AC3 | Step 4 archive tests, Step 5 installation and contention tests | Native check (guard between validation and start) |
| `gcliff --version` nested; invalid `[source:npm]`; bad git-cliff argument | AC4 | Step 6 launcher tests | Step 8 `gcliff` acceptance |
| `uc` or `brel` provisioning failure (engine caller) | AC3 | Step 5 messages and provisioning tests | Step 8 acceptance with a test-only handler |
| `version`, ordinary build, curated validation free of provisioning; budget variable not read | AC6 | Step 1 import-freedom test | Step 8 acceptance |
| Fresh checkout `git status` clean | AC6 | Step 3 ignore-rule test | Step 8 acceptance |
| Changed candidate archive; fixture regeneration; controlled inputs; rerun digest | AC5 | Step 7 candidate, fixture and comparison tests | Step 8 evidence run |
| Engine and passthrough environments | AC4 | Step 5 invocation tests, Step 6 launcher tests | Step 8 acceptance |
| Budget unset, `900`, `3600`, refused forms, valid entry with invalid budget, unaffected operations, retry inside D, probe and metadata limits, harness downloads, default waiter behind a 1800 s holder | AC2, AC3 | Step 1 budget tests, Step 5 budget flow tests, Step 7 candidate tests | Step 8 acceptance |

---

## Planning risk pass and rollout order for v0.14.0 git-cliff-provisioning

The steps are sequential: Steps 3 to 5 compose the Step 1 manifest and budget
with the Step 2 native layer; the launcher (Step 6) and the harness (Step 7)
both call the Step 5 service; Step 8 admits the pin only after the harness
exists. Steps 6 and 7 can be swapped. Every step passes its own gate without a
placeholder module for a later step.

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
- **Empty manifest interval**: from Step 1 to Step 8 the item branch admits no
  pin. Nothing outside this item calls provisioning yet, and the umbrella
  reaches `main` only after all eight items, so no consumer sees it.
- **Readings of design-silent cases**, implemented as tested behavior unless
  the plan review decides otherwise:
  - the root `.gitignore` entry lands in Step 3, the first step whose code
    writes under `.tools/git-cliff/`, one step before the downloader, so the
    rule still precedes every cache write in every checkout (requirement
    Q05);
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
    prints the ready line only once the invocation is usable (Q18);
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
    the trust record is written once after extraction and probe (pending
    Q19);
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

## Open questions for the v0.14.0 git-cliff-provisioning implementation plan

### Q01: Which step adds the root .gitignore entry

Question description: the design asks for `/.tools/git-cliff/` "in the same
change that adds the downloader" (requirement Q05: the rule precedes the first
cache write in every checkout). The plan adds it in Step 3, with the cache lock,
because the lock code is the first code that writes under `.tools/git-cliff/`;
the downloader itself arrives in Step 4. Each step is reviewed and committed on
its own, so the step that carries the line decides which commit holds it.
Revised after review round 1: whichever step carries it must precede every
cache-writing operation, including the by-hand native checks of Q06; with Q06
option B, the Step 2 checks use temporary paths outside `.tools/git-cliff/`.

#### BBQ for Q01

The "keep the smoke away from the neighbors" screen must be up before the first
coal is lit. It can go up with the lighter (the first thing that makes smoke),
with the bag of charcoal (what the instructions name), or on day one, before
anything arrives. In this picture: the screen is the `.gitignore` entry, the
lighter is the Step 3 lock code (first writer of the cache), the bag of charcoal
is the Step 4 downloader, and day one is Step 1.

#### Options for Q01

- Option A: Step 3, with the first code that writes under `.tools/git-cliff/`.
  - pro: no commit of the item branch contains cache-writing code without the
    rule, which is the purpose of requirement Q05.
  - pro: the ignore-rule test sits beside the cache layout it protects.
  - con: one step earlier than the design's literal "same change as the
    downloader".
- Option B: Step 4, with the downloader, as the design words it.
  - pro: literal match with the design sentence.
  - con: Step 3's lock records and attempt directories, written by its own
    code paths, would exist one commit before the rule.
- Option C: Step 1, before any cache code.
  - pro: the rule precedes every later commit of the item.
  - con: an ignore entry for a path no code of that commit knows yet; its test
    has no layout to refer to.

#### Recommended option for Q01 (with arguments for this choice)

Option A: requirement Q05 is about the rule existing before the first write,
and Step 3 is the first commit whose code can write there; the design's
"downloader" wording described the item as one change, while the plan splits
it into reviewed steps.

#### Answer to Q01: option A (with reason why it must be accepted as the answer)

Option A: it keeps the intent of requirement Q05 exact for every commit of the
item branch, adds no early unexplained entry, and lets the ignore-rule test sit
with the layout code it guards.

User decision: confirmed: option A, Step 3 carries the `/.tools/git-cliff/`
line with the first cache-writing code; any earlier by-hand native check uses
temporary paths. Chosen by the user on 2026-11-15 after the explanation, as
recommended, with no amendment.

### Q02: Shared strict record decoder or duplicated helpers

Question description: `operation_lock.py` keeps private strict JSON helpers
(duplicate-key rejection, object check, positive integers, present strings).
Item 3 adds four records needing the same rules: the cache lock record, the
staging owner file, `entry.json` and the candidate trust record. The design lets
the plan decide whether the helpers move to a shared place. The plan moves them
to `tools/release_workflow/lock_records.py` in Step 1 and makes
`operation_lock.py` call them with its existing messages.

#### BBQ for Q02

Two grills need the same thermometer. You can buy one thermometer and hang it
between them, or keep a second one at the new grill so the old grill is never
touched. In this picture: the thermometer is the strict record decoder, the old
grill is `operation_lock.py`, the new grill is the git-cliff cache code, and
hanging it between them is the shared `lock_records.py` module.

#### Options for Q02

- Option A: extract `lock_records.py` in Step 1; `operation_lock.py` delegates
  with `label="owner"` so its messages stay the same.
  - pro: one implementation of the strict rules for five record kinds.
  - pro: `operation_lock.py` shrinks by about 25 lines.
  - con: touches an item 1 module whose tests must stay green unchanged.
- Option B: copy the helpers into `git_cliff/cache.py` and leave
  `operation_lock.py` untouched.
  - pro: no change to an item 1 file.
  - con: two copies of the same security-relevant parsing rules that can drift.
- Option C: import the private helpers from `operation_lock.py` directly.
  - pro: no new file and no copy.
  - con: the git-cliff package would depend on private names of the project
    operation lock, which the cache lock must stay separate from.

#### Recommended option for Q02 (with arguments for this choice)

Option A: the four new record kinds and the existing one share exactly the same
rules, the refactor is small and covered by the unchanged operation lock suites,
and it keeps the cache lock independent of the project lock module.

#### Answer to Q02: option A (with reason why it must be accepted as the answer)

Option A: one strict decoder avoids drift between five record kinds, its
behavior is pinned by existing tests, and the dependency points from both locks
to a neutral helper rather than from one lock into the other.

User decision: confirmed: option A, a shared `lock_records.py` used by the
operation lock (messages and tests unchanged) and the four git-cliff records.
Chosen by the user on 2026-11-15 after the explanation, as recommended, with no
amendment.

### Q03: When 2.14.2 is admitted and where the launcher step sits

Question description: the manifest admits a pin only after its evidence is
recorded and reviewed. In the plan, the harness is written in Step 7 and the
evidence run, review and admission happen in Step 8, after the launcher
(Step 6). Until Step 8 the item branch admits no pin, so `bin\gcliff.bat` cannot
be tried by hand against a real pin before the last step, and the last step
also carries the evidence review gate, acceptance, native checks and
documentation.

#### BBQ for Q03

You can build the serving counter before the head cook tastes the new sauce, or
let the cook taste and approve the sauce first, then build the counter and
serve a real plate on it at once. In this picture: the serving counter is the
`gcliff` launcher, tasting and approving the sauce is the evidence run, the
user's review and the admission of 2.14.2, and serving a real plate is running
`bin\gcliff.bat --version` against the admitted pin.

#### Options for Q03

- Option A: keep the order: launcher in Step 6, harness in Step 7, evidence
  run and admission in Step 8.
  - pro: no renumbering; the launcher lands early.
  - con: the launcher can only be exercised with synthetic pins until the final
    step, and the final step is the heaviest of the plan.
- Option B: harness in Step 6, evidence run, audit, user review and admission in
  Step 7, then the launcher with integrated acceptance, native checks and
  documentation in Step 8.
  - pro: the launcher can be tried by hand against the admitted pin as soon as
    it lands, and the evidence review gate is no longer at the very end.
  - pro: spreads the work: the final step no longer holds the evidence run.
  - con: renumbers Steps 6 to 8: both plans, the dependency order, the
    acceptance owners, the commands and the cumulative line baselines change
    together, and the Git input change moves with the harness.
- Option C: run the evidence and admit right after Step 5, before writing the
  harness as engine code, with a throwaway script.
  - pro: earliest admission.
  - con: requires a design change rather than being an equally compliant
    route: the approved harness is an internal module reused by item 6
    (design Q15), and the throwaway script would not be reviewed code.

#### Recommended option for Q03 (with arguments for this choice)

Option B: both the harness and the launcher depend only on the Step 5 service,
so the swap is free of new dependencies, and it gives the launcher a real pin
for manual checks while moving the human evidence gate away from the final
acceptance step.

#### Answer to Q03: option B (with reason why it must be accepted as the answer)

Option B: it keeps every design rule (nothing admitted before reviewed
evidence), balances the last two steps, and makes the final step's acceptance
run against the shipped manifest rather than a synthetic one.

User decision: confirmed: option B, new order Step 6 harness, Step 7 evidence
run with the user's review and the admission of 2.14.2, Step 8 launcher with
integrated acceptance, native checks and documentation; both plans, file
lists, commands, ownership maps and line baselines are renumbered together at
consolidation, and the Git input change moves with the harness. Chosen by the
user on 2026-11-15 after the explanation, as recommended, with no amendment.

### Q04: How the native Windows layer is split into modules

Question description: the plan puts the child lifecycle (ctypes declarations,
job, attribute list, creation, recording callback, deadline, console filter) in
`windows_child.py`, estimated at 430 lines, and the use guard in
`windows_guard.py` (130 lines), with split guidance to move the declarations
into `windows_native.py` only if `windows_child.py` would pass 650.

#### BBQ for Q04

The grill's gas parts can live in one cabinet, with the valve chart taped on the
door, or the chart can get its own small box from the start so the cabinet never
fills up. In this picture: the cabinet is `windows_child.py`, the valve chart is
the ctypes structure and signature declarations, and the small box is a
separate `windows_native.py`.

#### Options for Q04

- Option A: two modules (`windows_child.py`, `windows_guard.py`), declarations
  moved out only if the 650 ceiling would be crossed.
  - pro: fewer files; the split happens only when needed.
  - con: `windows_child.py` reaches about 530 lines, close to the risk band,
    and may need a split later in the middle of a step (revised after review
    round 4).
- Option B: three modules from the start: `windows_native.py` (structures,
  constants, the kernel loader with signatures), `windows_child.py`
  (lifecycle) and `windows_guard.py` (guard).
  - pro: each module stays small and single-purpose; the lifecycle reads
    without ctypes noise.
  - pro: the fake kernel replaces one loader used by both modules.
  - con: one more file to read and review; the new module and its loader join
    Step 2's file list, tests and line budgets.
- Option C: one `windows_child.py` holding the guard too.
  - pro: one place for all new native code.
  - con: about 660 lines at once, above the 650-line repository ceiling
    (revised after review round 4).

#### Recommended option for Q04 (with arguments for this choice)

Option B: the declarations are a different responsibility from the lifecycle,
both modules need them, and separating them up front keeps every native module
well below the risk band without a mid-step split.

#### Answer to Q04: option B (with reason why it must be accepted as the answer)

Option B: it gives one shared loader, replaceable in tests, for the child and guard modules,
keeps the lifecycle readable, and removes the planned-for-later split.

User decision: confirmed: option B, three modules from Step 2:
`windows_native.py` (ctypes structures, constants and the kernel loader),
`windows_child.py` (lifecycle) and `windows_guard.py` (guard), with the new
module and its loader in Step 2's file list, tests and line budgets. Chosen by
the user on 2026-11-15 after the explanation, as recommended, with no
amendment. Clarification at the decision: after review rounds 1 and 2 the
single-module estimate of option C grew to about 660 lines, over the 650
ceiling, and option A's `windows_child.py` to about 530.

### Q05: How the native layer reaches 100% coverage without a process

Question description: coverage of `tools` must be 100%, and the suite fails any
test that creates a process. The plan passes an `api` object to
`run_contained` and `open_guard` (default: the real kernel loader) and tests
them with `native_kernel_fake.py`, which records every call and fails at a
chosen one. The existing `test_windows_process_tdd.py` instead monkeypatches the
module's `_kernel` function.

#### BBQ for Q05

To test a grill's ignition without gas, you can plug a dummy gas line into the
grill's inlet, swap the grill's internal pipe during the test, or leave the
ignition untested at home and only try it at the park. In this picture: the
dummy gas line is the injected fake kernel `api`, swapping the internal pipe is
monkeypatching `_kernel`, and trying it at the park is covering native code only
with developer-run checks outside pytest.

#### Options for Q05

- Option A: an explicit `api` parameter with the fake kernel object. The
  production default loader is covered through a fake loader, the signature
  declarations without any OS call, and the fault cases include the
  post-creation failures of Step 2 (revised after review round 1) and its
  retention and shutdown cases: the retained owner, daemon readers and the
  pre-identity unconfirmed end (revised after review round 2).
  - pro: no module-global patch; call order is asserted from one log.
  - pro: same injected-seam style as item 2's ports.
  - con: production signatures carry a parameter only tests use.
- Option B: monkeypatch `_kernel` (or the new loader) as the existing Windows
  process tests do.
  - pro: matches the existing native tests exactly.
  - con: a global patch per test; a forgotten patch reaches the real kernel.
- Option C: omit the native wrappers from coverage and rely on the native
  checks.
  - pro: no fake kernel to maintain.
  - con: noncompliant with the 100% coverage gate, since it omits code with
    many failure branches, which the native checks cannot all trigger.

#### Recommended option for Q05 (with arguments for this choice)

Option A: the lifecycle makes a long ordered sequence of calls whose order is
the contract (job before creation, recording before resume, reap before
cleanup); one injected fake recording them is the most direct proof, and it
never risks a real kernel call.

#### Answer to Q05: option A (with reason why it must be accepted as the answer)

Option A: it proves the ordered lifecycle branch by branch at 100% coverage,
keeps tests free of global patches, and leaves real behavior to the
developer-run native checks.

User decision: confirmed: option A, an explicit `api` parameter taking the fake
kernel object, the production default loader covered through a fake loader and
the declarations without any OS call, including the post-creation failure,
retention, daemon-reader and pre-identity cases. Chosen by the user on
2026-11-15 after the explanation, as recommended, with no amendment.

### Q06: When the developer-run native checks run

Question description: the design lists native behaviors fakes cannot prove
(job membership before resume, a suspended child ending with its killed
parent, a refused nesting, kill-on-close, worker termination against a stalled
endpoint, guard refusals, an abandoned mutex). The plan writes and runs the
recorder only in the final step, so a native defect found there would send
work back to Steps 2 to 5.

#### BBQ for Q06

You can check that the gas valve really shuts off right after fitting it, or
wait for the full party before lighting anything. In this picture: fitting the
valve is Step 2's native layer (and Step 5's guard use), checking it at once is
running the matching native checks in that step, and the full party is the
final step's integrated acceptance.

#### Options for Q06

- Option A: write and run every native check in the final step.
  - pro: one recorder written once, against the finished code.
  - con: a native surprise (for example a nesting refusal behaving differently)
    is found after four steps were built on the layer.
- Option B: create the recorder in Step 2 with the native-layer checks, extend
  it in Step 4 (stalled endpoint) and Step 5 (guard and mutex checks), commit
  the record each time, and rerun it in full in the final step. Each record
  declares its milestone and due checks, and the Step 8 validator rules apply
  to them (revised after review round 1). The Step 2 due set runs on temporary
  paths and stand-in children, never the cache: job membership before resume,
  a suspended child ending with its killed parent, a refused nesting under a
  job with UI limits, kill-on-close of a running child, descendant teardown,
  the teardown-failure exit, and the inherited guard refusing a rename while
  a child runs and while it is held between open and child start. The Step 4
  due set adds worker termination against a stalled local endpoint, with a
  disposable recorded staging directory. The Step 5 due set adds kill-on-close
  of a worker and of a git-cliff run through the service, a reuse probe and a
  stand-in caller in place of the launcher (delivered in Step 8 under
  confirmed Q03 B; revised after review round 4) killed
  while their child holds the guard, and an abandoned mutex of a live owner
  keeping its record. The final step reruns the full set against the final
  sources, with the production `gcliff` launcher instead of the stand-in
  (teardown-failure check and stand-in caller revised after review round 2).
  A failed, timed-out, skipped or missing due check blocks its step.
  - pro: each native assumption is proven in the step that relies on it.
  - con: the record changes in several commits; each step gains a by-hand run.
- Option C: incremental runs as in B, but commit the record only in the final
  step.
  - pro: early feedback with a single committed record.
  - con: intermediate results live only in private notes.

#### Recommended option for Q06 (with arguments for this choice)

Option B: the whole design rests on creation-time job membership and the
inherited guard, which only a real process proves; checking them in the step
that introduces them is the cheapest moment to find a wrong assumption, and the
committed record shows what each step relied on.

#### Answer to Q06: option B (with reason why it must be accepted as the answer)

Option B: early native proof protects Steps 3 to 8 from rework, and the final
full rerun still produces the one complete record the design asks for.

User decision: confirmed: option B, the recorder created in Step 2 and extended
in Steps 4 and 5, each milestone's due checks committed and validated as
passing for the current sources, a stand-in caller in Step 5 since the
launcher arrives in Step 8 (Q03 B), and the full set rerun against the final
sources with the production launcher in the final step. Chosen by the user on
2026-11-15 after the explanation, as recommended, with no amendment.

### Q07: Where the native check recorder and its record live

Question description: the plan follows item 2's lock evidence convention: a
recorder module started by hand under `tests/unit/tools/release_workflow/`
(outside coverage, never imported by a test) and a committed JSON record read by
a test leaf that checks its passing outcomes and source provenance (wording
revised after review round 2).

#### BBQ for Q07

The thermometer readings from a test cook can be noted in the test kitchen's
logbook, printed on a card shipped with every grill, or just told to the head
cook. In this picture: the test kitchen's logbook is the recorder and record
under `tests/`, the card shipped with every grill is a recorder module inside
the engine under `tools/`, and telling the head cook is pasting results into
the validation plan only.

#### Options for Q07

- Option A: recorder in `tests/unit/tools/release_workflow/git_cliff_native_checks.py`,
  record in `test_git_cliff_native_evidence/native_checks.v1.json`, checked by
  a test.
  - pro: same shape as item 2's `lock_evidence_recorder.py`; no coverage
    burden for process-starting code.
  - con: the recorder is not shipped for consumers to rerun.
- Option B: recorder as an engine module under `tools/release_workflow/git_cliff/`.
  - pro: item 8 or a consumer could rerun it from the engine.
  - con: also testable, but its process-starting code would add production
    coverage obligations through fakes, which prove nothing about the real
    checks.
- Option C: no committed record; results go into the validation plan text.
  - pro: no data file.
  - con: nothing a test can check, and no stable evidence for review.

#### Recommended option for Q07 (with arguments for this choice)

Option A: it reuses a convention already reviewed in item 2, keeps real-process
code out of the coverage-measured engine, and gives reviewers a committed
record whose test proves passing checks and their source provenance, not only
its structure (revised after review round 1).

#### Answer to Q07: option A (with reason why it must be accepted as the answer)

Option A: it is the established pattern for by-hand evidence in this engine,
its committed record is validated for success and provenance, and it avoids
fake-only production coverage of process-starting code.

User decision: confirmed: option A, the recorder
`tests/unit/tools/release_workflow/git_cliff_native_checks.py` started by
hand, and the record `test_git_cliff_native_evidence/native_checks.v1.json`
validated by its test for passing outcomes, expected observations, bounds and
current source digests. Chosen by the user on 2026-11-15 after the
explanation, as recommended, with no amendment.

### Q08: Where the committed evidence bundle lives

Question description: the manifest's `evidence` field must name the committed
bundle, which unit tests and item 4 read. The plan places it in the engine
package at `tools/release_workflow/git_cliff/bundles/2.14.2/` (`bundle.json`,
`cliff.toml`, `trust.2.14.2.json`, `trust.2.7.0.json`).

#### BBQ for Q08

The tasting notes that approved a sauce can be stapled to the recipe binder in
the kitchen, filed with the party planning papers, or kept in the test
kitchen's drawer. In this picture: the recipe binder is the engine package that
holds the manifest, the party planning papers are the `docs/v0.14.0/` effort
documents, and the test kitchen's drawer is a test data directory.

#### Options for Q08

- Option A: `tools/release_workflow/git_cliff/bundles/2.14.2/`.
  - pro: the manifest and the bundle it references ship together; item 4 reads
    engine data, not docs.
  - con: data files inside a Python package directory.
- Option B: `docs/v0.14.0/evidence/git-cliff-2.14.2/`.
  - pro: beside the effort documents that justify it.
  - con: engine code and item 4 would read from the docs tree, and a later
    effort's documents move to another version directory.
- Option C: a test data leaf such as `tests/unit/tools/release_workflow/test_git_cliff_bundle/`.
  - pro: same place as item 2's lock evidence.
  - con: the shipped manifest would reference a test directory.

#### Recommended option for Q08 (with arguments for this choice)

Option A: the bundle is part of what admits a production pin, so it belongs
with the manifest it backs, in a stable path that items 4 and 6 can rely on.

#### Answer to Q08: option A (with reason why it must be accepted as the answer)

Option A: shipped evidence stays next to the shipped table that cites it, and
neither engine code nor item 4 depends on the docs or test trees.

User decision: confirmed: option A, the bundle in
`tools/release_workflow/git_cliff/bundles/2.14.2/` (`bundle.json`,
`cliff.toml`, `trust.2.14.2.json`, `trust.2.7.0.json`), cited by the
manifest's `evidence` field. Chosen by the user on 2026-11-15 after the
explanation, as recommended, with no amendment.

### Q09: How the fixture history script creates its objects

Question description: the fixture script must fix every object-producing input
(trees, parents, messages, identities and dates with zones, annotated tags,
SHA-1 format, command-line configuration, no hooks, no signing, no line-ending
conversion). The plan builds it from one `git fast-import` stream, which needs
Git's standard input, so `GitExecutionContext.run` gains an optional `input`.

#### BBQ for Q09

A practice cook for the judges can be replayed from one written script read
aloud to the kitchen, or by giving each cook a separate note with their own
timing for every dish. In this picture: the script read aloud is the
`git fast-import` stream fed through Git's input, and the separate notes are
plumbing commands that each need their own author and committer environment.

#### Options for Q09

- Option A: one `git fast-import` stream through `run(..., input=...)`, which
  passes the bytes with `input=` without also setting `stdin` and keeps the
  current stdin rule when no input is given; both branches are tested without
  a process (revised after review round 1).
  - pro: every object input sits in one byte-stable text the test compares.
  - pro: one Git call builds the whole history.
  - con: adds an input parameter to the item 1 Git boundary.
- Option B: plumbing commands (`hash-object`, `mktree`, `commit-tree`, `tag`)
  with a per-call environment for dates and identities.
  - pro: each object is created by a familiar command.
  - con: needs a per-call environment override on `GitExecutionContext` and
    still needs input for `mktree`; many calls to keep in order.
- Option C: let the harness start Git through its own subprocess call.
  - pro: no change to `git.py`.
  - con: breaks the rule that `git.py` owns the only Git subprocess boundary.

#### Recommended option for Q09 (with arguments for this choice)

Option A: the stream is the most direct way to pin every object input, it is
easy to compare byte for byte, and the boundary change is a small optional
argument with its own test.

#### Answer to Q09: option A (with reason why it must be accepted as the answer)

Option A: it makes the fixture reproducible from one reviewed text, keeps Git
behind its single boundary, and costs one tested parameter.

User decision: confirmed: option A, one `git fast-import` stream fed through
`GitExecutionContext.run(..., input=...)`, which passes the bytes without also
setting stdin and keeps today's stdin rule when no input is given; the change
moves with the harness step (Q03 B). Chosen by the user on 2026-11-15 after
the explanation, as recommended, with no amendment.

### Q10: Who computes the digest checked against the manifest

Question description: the worker streams the archive while computing its
SHA-256 and stops at the first byte beyond the expected size. The plan has the
parent recompute the digest from the staged file before extraction instead of
trusting the worker's reported value.

#### BBQ for Q10

The helper who carries the meat in tells you its weight; you can trust the
number, or put the package on your own scale before cooking. In this picture:
the helper is the download worker, the number it tells is its reported digest,
and your own scale is the parent hashing the staged archive itself.

#### Options for Q10

- Option A: the parent recomputes the digest from the staged file.
  - pro: the check that admits bytes runs in the process that publishes them,
    on the bytes actually on disk.
  - con: one more read of about 7 MB, a few milliseconds.
- Option B: the parent trusts the worker's reported digest and size.
  - pro: no second read.
  - con: a worker defect or a file changed after the worker exited would pass.
- Option C: the parent recomputes and also compares with the worker's report,
  failing on disagreement.
  - pro: detects a worker that misreports.
  - con: a second failure path that adds nothing once the parent's own digest
    decides.

#### Recommended option for Q10 (with arguments for this choice)

Option A: verification is the security-relevant step, so it belongs to the
publishing process and to the bytes it will extract, at a negligible cost.

#### Answer to Q10: option A (with reason why it must be accepted as the answer)

Option A: it verifies exactly what is extracted, independent of the worker's
correctness, for a cost far below one probe.

User decision: confirmed: option A, the parent recomputes the SHA-256 of the
staged archive and compares it with the manifest before extraction, without
relying on the worker's report. Chosen by the user on 2026-11-15 after the
explanation, as recommended, with no amendment.

### Q11: How the new test leaves are named

Question description: the plan convention is
`tests\unit\...\test_<module>\test_<module>_tdd.py`, and existing leaves such as
`test_paths` add topic files named `test_paths_faults_tdd.py`. Some planned
leaves do not follow it: `test_git_cliff_provisioning/` holds
`test_git_cliff_reuse_tdd.py`, `test_git_cliff_installation_tdd.py`,
`test_git_cliff_contention_tdd.py` and `test_git_cliff_budget_flow_tdd.py`;
`test_git_cliff_lifecycle/` matches no module; `test_git_cliff_lock/` tests
`cache_lock.py`, `test_git_cliff_worker/` tests `download_worker.py`, and
`test_gcliff_launcher/` tests `git_cliff/launcher.py`.

#### BBQ for Q11

Spice jars can carry the name of the dish they serve, or the name of whatever
the cook had in mind that day. Labels named after the dish let anyone find the
right jar. In this picture: the dish is the production module, the jar is the
test leaf, and the label is the leaf and file name.

#### Options for Q11

- Option A: keep the planned leaf names.
  - pro: topic names read well for a reviewer.
  - con: breaks the module-to-leaf convention, so the tests of a module are
    harder to find.
- Option B: one leaf per production module, with topic files prefixed by the
  module name: `test_git_cliff_installation/`, `test_git_cliff_provisioning/`
  with `test_git_cliff_provisioning_tdd.py` (reuse),
  `test_git_cliff_provisioning_contention_tdd.py`,
  `test_git_cliff_provisioning_budget_tdd.py` and
  `test_git_cliff_provisioning_lifecycle_tdd.py`; `test_git_cliff_cache_lock/`
  with `test_git_cliff_cache_lock_recovery_tdd.py`;
  `test_git_cliff_download_worker/`; `test_git_cliff_launcher/`. Acceptance and
  evidence leaves keep their item 2 style names. After the decision, the file
  lists, commands, validation references and maps are renamed together; the
  proof obligations do not change (revised after review round 1).
  - pro: follows the convention and the existing topic-file practice.
  - pro: groundhog's affected-test selection and a reader map module to tests
    directly.
  - con: longer file names.
- Option C: one leaf per production module with a single test file each.
  - pro: strictest form of the convention.
  - con: the provisioning tests would exceed the 650-line ceiling in one file.

#### Recommended option for Q11 (with arguments for this choice)

Option B: it applies the repository convention with the topic-file practice
already used by `test_paths`, without forcing oversized files.

#### Answer to Q11: option B (with reason why it must be accepted as the answer)

Option B: every module's tests sit in its own leaf, topic files keep each file
small, and the plan's file lists and validation sections only rename paths.

User decision: confirmed: option B, one leaf per production module with topic
files prefixed by the module name (acceptance and evidence leaves keep their
item 2 style names), with the user's amendment that everything release
related stays grouped inside one overall group above any module. The user
clarified that this group is the existing release folder
`tests/unit/tools/release_workflow/`: every new git-cliff leaf goes directly
in it, beside the item 1 and item 2 leaves, with no other location and no
extra `git_cliff` level or groundhog named group. Chosen by the user on
2026-11-15 after the explanation and a clarifying question.

### Q12: How the shared git-cliff test fakes are organized

Question description: the plan grows one `git_cliff_support.py` from Step 3 to
Step 7 (clock, process states, synthetic pin and archive, guard opener,
write-denying filesystem, fake child launcher, harness fakes), reaching about
490 lines by Step 7 with split guidance toward the risk band. The native fake
kernel is already separate.

#### BBQ for Q12

All the grilling tools can go into one drawer that slowly fills, or into three
labeled drawers from the start: basic tools, fire tools and tasting tools. In
this picture: the one drawer is a single `git_cliff_support.py`, the basic tools
are the clock, process states, pins and filesystem helpers, the fire tools are
the fake child launcher and its parent-death boundaries, and the tasting tools
are the harness fakes.

#### Options for Q12

- Option A: one `git_cliff_support.py`, split only if it nears 550 lines.
  - pro: one import for every git-cliff test.
  - con: predicted to approach the risk band; a split in Step 7 would touch
    earlier tests' imports.
- Option B: three modules by concern from their first step:
  `git_cliff_support.py` (Step 3), `git_cliff_children_fake.py` (Step 5) and
  `git_cliff_harness_fake.py` (Step 6 under confirmed Q03 B, with the
  cumulative budgets and imports updated accordingly; revised after review
  round 4).
  - pro: each stays well below 550; later steps never rewrite earlier imports.
  - con: tests import from up to three helper modules.
- Option C: put fakes in each leaf's `conftest.py`.
  - pro: fakes sit next to their tests.
  - con: the child launcher and process-state fakes are shared by several
    leaves and would be duplicated.

#### Recommended option for Q12 (with arguments for this choice)

Option B: the three groups have different users and lifetimes, and splitting at
creation avoids a known late split that would rewrite imports in reviewed
steps.

#### Answer to Q12: option B (with reason why it must be accepted as the answer)

Option B: it keeps every helper module small, gives each step one helper module
of its own, and removes a predicted risk-band split.

User decision: confirmed: option B, three helper modules from their first
step: `git_cliff_support.py` (Step 3), `git_cliff_children_fake.py` (Step 5)
and `git_cliff_harness_fake.py` (the harness step, Step 6 under Q03 B), all in
`tests/unit/tools/release_workflow/` (Q11 amendment), with the native kernel
fake kept separate. Chosen by the user on 2026-11-15 after the explanation, as
recommended, with no amendment.

### Q13: Whether bin\gcliff.bat switches the console codepage

Question description: the release launchers switch the console to codepage
65001 and restore it at exit. They need it because `for /f` decodes the runtime
record with the console codepage, and a checkout path with non-ASCII
characters is stored there as UTF-8. The plan has `bin\gcliff.bat` keep the same
switch and restore. git-cliff's own output is not the reason for the switch,
which costs two short `chcp` runs.

#### BBQ for Q13

To read a recipe card written in another alphabet, you can put on the reading
glasses for the moment you read it and take them off afterwards, or try to read
it without them and hope the card has no foreign letters. In this picture: the
recipe card is the runtime record, the foreign letters are non-ASCII
characters in the checkout path, the reading glasses are codepage 65001, and
taking them off is restoring the console's codepage at exit.

#### Options for Q13

- Option A: the same switch and restore as the release launchers, with source
  and simulation checks that the codepage is restored after a readiness error
  and after a normal child return (revised after review round 1).
  - pro: a checkout path with non-ASCII characters is read correctly, as for
    `release_workflow.bat`; the source contract can share the release
    launchers' expectations.
  - pro: the console codepage is unchanged once `gcliff` returns.
  - con: two `chcp` process starts per call.
- Option B: no codepage handling.
  - pro: no extra process start; the console is never touched.
  - con: the runtime record of a checkout under a non-ASCII path is misread,
    and `gcliff` fails with status 69 where the release launcher works.
- Option C: switch only when the record contains a non-ASCII byte.
  - pro: no `chcp` in the common case.
  - con: batch cannot test bytes before decoding them; the check itself needs
    the codepage it wants to avoid.

#### Recommended option for Q13 (with arguments for this choice)

Option A: the launcher must read the same record the same way as the release
launchers, and restoring the codepage keeps the console unchanged after the
call.

#### Answer to Q13: option A (with reason why it must be accepted as the answer)

Option A: it gives `gcliff` the same path support as the release launchers for a
small fixed cost, with no lasting console change.

User decision: confirmed: option A, `bin\gcliff.bat` saves the console code
page, switches to 65001 like the release launchers and restores it at exit,
with source and simulation checks for restoration after a readiness error and
after a normal child return. Chosen by the user on 2026-11-15 after the
explanation, as recommended, with no amendment.

### Q14: How the launcher ignores Ctrl+C while git-cliff runs

Question description: while it waits, the launcher must ignore the console's
Ctrl+C so git-cliff decides how to stop. `SetConsoleCtrlHandler(NULL, TRUE)` is
inherited by children, so it would also make git-cliff ignore Ctrl+C. The plan
registers a ctypes handler routine that returns true for `CTRL_C_EVENT` and
`CTRL_BREAK_EVENT`, which children do not inherit, and removes it after the
wait.

#### BBQ for Q14

When the smoke alarm rings, you want the grill master to decide whether to stop
cooking, while you, the helper, keep holding the tray. You can wear earplugs
you put in yourself, ask the house rules to "ignore alarms" (which the grill
master would then follow too), or rely on a house habit that happens to make
helpers ignore alarms. In this picture: the alarm is Ctrl+C, the grill master
is git-cliff, the helper is the launcher, the earplugs are a handler routine,
the house rule is the inherited null handler, and the house habit is the C
runtime treating an ignored `SIGINT` as handled.

#### Options for Q14

- Option A: a ctypes handler routine returning true, registered for the wait
  and then removed; the callback object stays referenced while registered,
  and its removal is tested on errors as well as on success (revised after
  review round 1).
  - pro: documented Win32 behavior: a handler returning true stops the event
    for this process only, and handler routines are not inherited.
  - pro: tested through the Step 2 fake kernel.
  - con: the ctypes callback must stay referenced while registered.
- Option B: `signal.signal(SIGINT, SIG_IGN)` and `SIGBREAK` for the wait, then
  the previous handlers restored.
  - pro: two standard-library calls, no ctypes.
  - con: relies on the C runtime's console handler answering "handled" for an
    ignored signal, an internal behavior that only a native check would prove.
- Option C: keep Python's handler and catch `KeyboardInterrupt` around a wait
  loop with short timeouts, then keep waiting.
  - pro: no handler change at all.
  - con: a polling wait instead of one blocking wait, and a second Ctrl+C
    during the handling window could still end the launcher.

#### Recommended option for Q14 (with arguments for this choice)

Option A: it states the required behavior directly in Win32 terms, cannot leak
into git-cliff, and fits the fake-kernel tests the native layer already has.

#### Answer to Q14: option A (with reason why it must be accepted as the answer)

Option A: it is the only option whose correctness follows from documented
console semantics rather than runtime internals or polling.

User decision: confirmed: option A, a ctypes handler routine returning true for
`CTRL_C_EVENT` and `CTRL_BREAK_EVENT`, registered only while the launcher waits
for git-cliff, kept referenced while registered and removed on success and on
errors; never the inherited null routine. Chosen by the user on 2026-11-15
after the explanation, as recommended, with no amendment.

### Q15: How the bootstrap gains the worker and gcliff entry kinds

Question description: the bootstrap gains `git-cliff-worker` (Step 4) and
`gcliff-batch` (Step 6). Both skip the release status normalization, and
`gcliff-batch` reports readiness and invocation failures as 69. The cross-site
status test parses exactly one set literal inside `bootstrap.main`. The plan
adds module-level tables (`_ENGINES`, `_UNNORMALIZED_KINDS`, `_FAILURE_STATUS`)
and keeps that literal unique.

#### BBQ for Q15

One front door with a small sign saying which guest goes to which room, or a
second door built for the new guests next to the first one. In this picture:
the front door is `bootstrap.py`, the sign is the module-level kind tables, and
the second door is a separate bootstrap script for the worker and `gcliff`.

#### Options for Q15

- Option A: one bootstrap with module-level kind tables; the worker and
  `gcliff` pass-through statuses are tested independently of the release
  kinds (revised after review round 1).
  - pro: one readiness gate and one private helper loader for every entry.
  - pro: the cross-site status contract keeps reading one literal.
  - con: `bootstrap.py` grows by about 55 lines and serves three behaviors.
- Option B: separate thin scripts (`gcliff_bootstrap.py`,
  `worker_bootstrap.py`) loading `bootstrap.py` as a sibling helper for
  `check` and `configure_streams`.
  - pro: `bootstrap.main` stays exactly as today.
  - con: two more isolated entry scripts with their own import-path handling to
    test and keep in step.
- Option C: route `gcliff` through `cli.main` as a handler.
  - pro: no bootstrap change for `gcliff`.
  - con: `cli` and `results` normalize statuses and render diagnostics, which
    contradicts passthrough.

#### Recommended option for Q15 (with arguments for this choice)

Option A: the readiness gate and helper loading are the reason the bootstrap
exists; sharing them through a small table is less code than two new entry
scripts, and the status contract stays intact.

#### Answer to Q15: option A (with reason why it must be accepted as the answer)

Option A: one tested entry boundary serves all kinds, the status literal stays
unique, and no second isolated script has to repeat its setup.

User decision: confirmed: option A, one `bootstrap.py` with module-level
tables (`_ENGINES`, `_UNNORMALIZED_KINDS`, `_FAILURE_STATUS`) for the
`git-cliff-worker` and `gcliff-batch` kinds, keeping the single set literal in
`bootstrap.main`, with the worker and `gcliff` pass-through statuses tested
independently of the release kinds. Chosen by the user on 2026-11-15 after the
explanation, as recommended, with no amendment.

### Q16: Where the user's review of the evidence is recorded

Question description: the requirement makes reviewing the evidence a separate
acceptance step, and the plan's Step 8 waits for the user's review before the
manifest edit. The plan records that review only in the private, ignored step
journal, so the committed repository would show an admitted pin with no record
of its review.

#### BBQ for Q16

The head cook approves the new sauce; that approval can be written in your own
pocket notebook, or signed on the recipe card itself, where the next cook sees
it. In this picture: the pocket notebook is the private step journal, the recipe
card is the committed `bundle.json`, and the signature is a `review` entry with
its date and decision that the admission test checks.

#### Options for Q16

- Option A: step journal only.
  - pro: no new bundle field.
  - con: the committed admission has no trace of the required review.
- Option B: a `review` object in `bundle.json`, written after the user's
  review and required by `require_admissible`; the step journal records it
  too, as usual. Its binding, revised after review round 1:
  - the covered projection is `bundle.json` without its `review` member,
    serialized as canonical JSON (keys sorted, `separators=(",", ":")`,
    `ensure_ascii=True`, UTF-8), and a `files` member of the bundle lists the
    SHA-256 of `cliff.toml`, `trust.2.14.2.json` and `trust.2.7.0.json`, which
    the reader verifies against the files on every read;
  - the review holds `decision` (`approved` or `rejected`), `reviewer`
    (`user`), `date` (ISO local date) and `covered_sha256`, the digest of that
    projection;
  - `require_admissible` refuses an absent review, a decision other than
    `approved`, a reviewer other than `user`, a malformed date, a
    `covered_sha256` different from the recomputed projection and any listed
    file whose digest differs;
  - a harness rerun that changes any covered content (inputs, outputs, hunks,
    classification, audit, listed files) leaves the review in place but stale,
    so admission is refused until a new review; a byte-identical projection
    keeps the approval;
  - tests reject an absent, rejected and stale review, a tampered listed file
    and a content change after approval.
  - pro: the committed evidence shows the review that admitted the pin, and a
    test refuses admission without it.
  - con: one more bundle member, its projection rule and its checks.
- Option C: a separate review document beside the bundle.
  - pro: free-form notes from the review.
  - con: a second artifact to keep in step with the bundle; it could bind a
    digest too, but adds coordination between two files for the same fact.

#### Recommended option for Q16 (with arguments for this choice)

Option B: the review is part of what admits a production pin, so it belongs in
the committed evidence, bound to the bundle it covers and enforced by the
admission test.

#### Answer to Q16: option B (with reason why it must be accepted as the answer)

Option B: it makes the separate acceptance step visible and enforced in the
repository instead of in a private note.

User decision: confirmed: option B as revised after review round 1, a `review`
member in `bundle.json` (decision, reviewer `user`, date, `covered_sha256` of
the canonical projection without `review`), a `files` member binding
`cliff.toml` and both trust records by SHA-256, and `require_admissible`
refusing an absent, rejected, malformed or stale review and any tampered
listed file; the step journal records it too. Chosen by the user on 2026-11-15
after the explanation, as recommended, with no amendment.

### Q17: How the exit-path audit is produced

Question description: status 69 holds only if the evidence bundle records an
audit of git-cliff's exit paths at the `v2.14.2` source tag (error return,
argument-parsing errors, propagated helper statuses, panics, abnormal
termination) with the audited revision. The plan leaves it as a by-hand reading
recorded in `bundle.json`, without saying how the source is obtained or what is
read.

#### BBQ for Q17

To be sure a recipe never calls for peanuts, you can read the whole recipe book
yourself with a checklist of where peanuts usually hide, or have a helper
scan the book for the word "peanut" and hand you only those pages. In this
picture: the recipe book is git-cliff's source at `v2.14.2`, peanuts are a
possible exit status 69, the checklist is the audit's list of exit-path
categories, and the helper's scan is a pattern search by the harness.

#### Options for Q17

- Option A: by-hand audit with a written checklist: a shallow clone of the tag
  into a temporary directory outside the repository, the files and call sites
  to read for each category, and the commands and commit recorded in the
  bundle, with the dependency versions and source references wherever they
  affect helper, parser or panic exits (revised after review round 1).
  - pro: a person reads every path, including statuses set inside dependencies.
  - pro: no network or parsing code added to the harness.
  - con: repeating it for item 6's next pin is manual work.
- Option B: harness-assisted: the harness clones the tag and lists candidate
  exit sites by pattern, and the person classifies the list.
  - pro: repeatable candidate list for later pins.
  - con: more harness code and coverage, and a pattern list can miss a path, so
    the reading is still needed.
- Option C: observed statuses only.
  - pro: no source reading.
  - con: noncompliant with the design, which says observations corroborate
    but do not prove the exclusion.

#### Recommended option for Q17 (with arguments for this choice)

Option A: the audit's value comes from a complete reading, which no pattern
search replaces, and a checklist with recorded commands makes it repeatable
enough until item 6 decides how pins are proposed.

#### Answer to Q17: option A (with reason why it must be accepted as the answer)

Option A: it satisfies the design's audit requirement with the least new code
and records exactly what was read and at which commit.

User decision: confirmed: option A, a by-hand audit with a written checklist
(shallow clone of `v2.14.2` into a temporary directory outside the
repository, the files and call sites read per exit-path category, dependency
versions and source references where they affect exits), with the commands
and the audited commit recorded in `bundle.json`; observed statuses only
corroborate. Chosen by the user on 2026-11-15 after the explanation, as
recommended, with no amendment.

### Q18: What provisioning does when the new entry cannot be guarded

Question description: after publication the design releases the lock, then
opens the use guard on the new entry. If the guard cannot be opened in between
(the entry was removed by hand, repaired by another caller after finding it
invalid, or changed by other external interference), the plan reports the
extraction-or-probe stage with its remedy and does not loop. Revised after
review round 1: the diagnostic names the actual cause and path, and the ready
line is printed only once a usable invocation exists.

#### BBQ for Q18

You place the finished plate on the pass and step back to wash your hands; when
you turn around to carry it, someone has taken it away. You can tell the guest
that their plate is gone and they can order again, or cook it once more
yourself before giving up. In this picture: the pass is the published cache
entry, stepping back is releasing the lock, carrying it is opening the use
guard, and cooking it once more is one rerun of the provisioning flow.

#### Options for Q18

- Option A: fail with the extraction-or-probe stage diagnostic and its remedy.
  - pro: simplest behavior; no loop and no second download within one call.
  - con: a rare race turns into a failure the user retries by hand.
- Option B: rerun the flow once from the reuse check, then fail.
  - pro: absorbs the race without user action.
  - con: one call could download twice and hold its caller for twice the
    budgets.

#### Recommended option for Q18 (with arguments for this choice)

Option A: the case needs another process to remove or replace the entry within
a window of milliseconds; a diagnostic naming the actual cause is enough, and
it keeps each call bounded by one download.

#### Answer to Q18: option A (with reason why it must be accepted as the answer)

Option A: it keeps the call's time bound and code simple for a case that only
outside interference produces, and reports what actually happened.

User decision: confirmed: option A, one failure under the extraction-or-probe
stage whose diagnostic names the actual cause and path, no rerun of the flow,
and the ready line printed only once a usable invocation exists. Chosen by
the user on 2026-11-15 after the explanation, as recommended, with no
amendment.

### Q19: How the first 2.7.0 acquisition is bounded before its identity exists

Question description: added after review round 1. The design lets the first
authorized download of 2.7.0, over certificate-verified HTTPS, record the
asset name, size and SHA-256 (requirement Q16 exception). The ordinary worker
streams only with an `expected_size` and stops at the first byte beyond it,
but 2.7.0 has no recorded size before that first download. The plan body
follows option A while this question is pending.

#### BBQ for Q19

Picking up a cake from a new bakery whose recipe you have never tasted, you
can call the bakery first to ask the box size, so the van carries exactly that
box, or bring the biggest box the van holds and measure what comes back. In
this picture: the bakery is GitHub's 2.7.0 release, the phone call is the
certificate-verified release metadata lookup, the box size is the asset size,
the van is the size-bounded download worker, and the biggest box is a fixed
size cap chosen for the evidence-only mode.

#### Options for Q19

- Option A: read the asset name and size from the certificate-verified release
  metadata through the record-free metadata worker (60 s, one retry), then use
  the ordinary recorded worker with that exact size under D with one retry;
  the parent computes the digest, extracts, probes, and writes the immutable
  trust record once, only after that; a failure anywhere before writes no trust
  record and leaves staging to the ordinary recovery rules.
  - pro: reuses the metadata worker the harness needs for 2.14.2 and the
    exact-size guard of production downloads; no new worker mode or limit.
  - pro: the recorded size matches both the metadata and the received bytes.
  - con: the first acquisition also needs the API host and its quota, which
    the later reruns (comparing with the trust record) do not.
- Option B: a separate evidence-only worker mode with a fixed size cap,
  recording the actual size and digest after the download completes.
  - pro: no dependency on the release metadata for 2.7.0.
  - con: a new cap value and worker mode that the design does not define, so
    it needs a design clarification before implementation.

Neither option authenticates the first digest independently or widens the
exception beyond 2.7.0.

#### Recommended option for Q19 (with arguments for this choice)

Option A: it bounds the first download with an exact size taken from the same
certificate-verified source the harness already uses for 2.14.2, adds no new
limit to the design, and records the trust record only for a candidate that
extracted and probed successfully.

#### Answer to Q19: option A (with reason why it must be accepted as the answer)

Option A: it gives the evidence-only acquisition an implementable, exact bound
with existing mechanisms, and keeps the user's 2026-11-13 exception unchanged.

User decision: confirmed: option A, the asset name and exact size read from
the certificate-verified release metadata through the record-free metadata
worker, the ordinary recorded size-bounded download under D with one retry,
the digest computed by the parent, and the trust record written once only
after extraction and probe succeed; the exception stays limited to 2.7.0.
Chosen by the user on 2026-11-15 after the explanation, as recommended, with
no amendment; the user then asked to print the next step and hold.
