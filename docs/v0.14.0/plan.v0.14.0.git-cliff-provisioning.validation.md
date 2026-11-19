# v0.14.0 git-cliff-provisioning implementation tracking and validation

No, it is not implemented.

This document tracks the eight steps of the
[implementation plan](plan.v0.14.0.git-cliff-provisioning.md) for item 3 of
the sibling release tooling umbrella. Steps 1 to 4 are implemented: the pin
manifest, the `[git-cliff]` domain, the download budget policy, the shared
record decoder, the contained Windows children with the use guard and their
native check record, the cache with its reuse check and its lock, and the
download worker with archive verification and extraction. The provisioning
service, the evidence harness, the reviewed admission of 2.14.2 and the
`gcliff` launcher are still to be written.

> Initial-skeleton note: this first version was written by the `write-plans`
> skill, before any implementation check. It fills `Goal for Step N` and
> `Step N improvement expectations`, opens every `Analysis of Step N
> implementation state` with "Not started. Step N is not implemented because
> ...", and fills every other per-step section with the literal placeholder
> that an implementation check later replaces.
>
> Every test this document refers to belongs to llm-shared's own development
> suite, run while llm-shared is changed; no release, no `gcliff` call and no
> consumer build runs it. The evidence harness and the native check recorder
> run by hand, outside pytest.
>
> Markdown lint note: never leave a space immediately inside an inline code span
> (MD038); write a needed space as the token `[space]`, as in `` `[space]${x}` ``.
> The empty placeholder ends in `)_.` so the line is not pure italic text (MD036).

---

## File-based IO cost clarification for v0.14.0 git-cliff-provisioning (implementation)

All implementation work must respect the IO classification established in
[the plan](plan.v0.14.0.git-cliff-provisioning.md#file-based-io-cost-clarification-for-v0140-git-cliff-provisioning).
The key constraints carried forward from the plan are:

- Configuration loading reads `.release.ini` once, as today; the manifest is
  an in-memory table, and operations that never need git-cliff import no other
  `git_cliff` module and never read the budget variable.
- Valid-entry reuse opens one guard, reads one `entry.json`, hashes the
  executable once through the guard (linear in its bytes) and runs one probe;
  it takes no lock and writes nothing.
- A lock wait reads one record per 250 ms poll; provisioning lists one version
  directory once, without recursion, and only under the lock.
- Every record is complete before non-replacing publication, and an entry is
  published by one directory rename; no path scans a directory tree.

---

## Complexity Bound Clarification for v0.14.0 (implementation)

The scaling target for all v0.14.0 git-cliff-provisioning code paths is:

- **O(1) amortized per call**: pin lookups go through the manifest table;
  reuse is a constant number of operations (one guard, one record, one hash
  pass, one probe), the hash pass being linear in the executable's bytes; a
  lock poll is one record read.
- **O(n) total per phase**: streaming, hashing and extraction are linear in
  bytes; waits are linear in polls; recovery is linear in the entries of one
  version directory; the harness is linear in ranges and output bytes, except
  its by-hand hunk computation for differing ranges.

Every implemented step should be reviewed against this bound in its
Performance check section.

---

## Step 1. Tested-pin manifest, git-cliff domain and download budget policy

### Analysis of Step 1 implementation state

Yes. Step 1 has been fully implemented.

The tested-pin manifest ships with its empty admitted tuple, the
`[git-cliff]` domain is registered last in the shipped schemas, the download
budget policy resolves every accepted value and refuses every other form the
plan lists, and the strict record helpers live in `lock_records.py`, used by
the operation lock with unchanged messages. Code review round 1 found that
warm manifest lookups hashed every pin through a cache key made of the table;
the cache is now keyed by the identity of the table it retains, and a
regression proves that warm lookups never hash, compare or visit a pin. Every
completion criterion holds: the command printed by `pw scope day` reports
`exit=0`, the three `rg` checks find only the expected matches, and the
import-freedom test passes.

### Goal for Step 1

Ship the tested-pin manifest with frozen `AdmittedPin` records and an empty
admitted tuple until Step 7, register the `[git-cliff]` domain whose `version`
rule parses exact pins and admits only manifest versions, ship the download
budget policy with its refused forms, and move the strict JSON record helpers
into `lock_records.py` for the operation lock and the new record kinds.

### Step 1 improvement expectations

- `[git-cliff] version` accepts only `X.Y.Z` and only admitted versions; with
  the empty tuple every declared version is refused with `tested: none`, and
  an omitted key yields no value.
- A synthetic manifest gives an omitted key a defaulted value with the same
  source information as any other default, and refuses `2.15.0` with the
  tested pins listed.
- The budget policy returns D 300 and W 360 when unset, exact values from 300
  through 3600 with W = D + 60, and refuses every other form without
  clamping.
- Loading configuration imports no `git_cliff` module other than `manifest`.
- `operation_lock.py` keeps its behavior and messages, and its suites run
  unchanged.

### What was implemented for Step 1

The current diff delivers the Step 1 file list of the plan, plus two
test-only changes outside it.

- **Shared record decoder**: `tools/release_workflow/lock_records.py` holds
  `decode_object`, `positive_integer` and `text`. Each message names the
  caller's label (`Duplicate owner field: pid`,
  `Owner record is not an object`, `Invalid owner pid`), duplicate keys are
  refused at every object level, and the decoded object keeps the exact keys
  of the document so each record kind compares them with the keys it expects.
  `operation_lock._record`, `_integer` and `_text` delegate to these helpers
  with `label="owner"`, and `json.loads` no longer appears in
  `operation_lock.py`.
- **Tested-pin manifest**: `tools/release_workflow/git_cliff/manifest.py`
  defines the frozen `AdmittedPin`, `PLATFORM_TRIPLE`,
  `ADMITTED_PINS = validate_pins(())`, `validate_pins`, `default_version`,
  `admitted`, `parse_pin` and `download_url`. `parse_pin` accepts only ASCII
  `X.Y.Z`, with the form message otherwise, then admission
  (`not a tested git-cliff pin; tested: <list>`, `tested: none` for the empty
  tuple). The invariant check refuses an invalid version, a triple other than
  the platform triple, an asset or member name not derived from the version
  and triple, a digest that is not 64 lowercase hexadecimal characters, a zero
  size, an empty evidence reference, a duplicate version and any number of
  defaults other than one in a nonempty table. Each table is validated and
  indexed on first use; the private cache is keyed by `id(pins)` and each
  entry keeps the table, so its identity cannot be reused while cached, and a
  warm lookup is one dictionary access on an integer that never hashes,
  compares or visits a pin. The module imports only `re` and `dataclasses`.
- **Download budget policy**: `tools/release_workflow/git_cliff/budget.py`
  defines `DOWNLOAD_BUDGET_VARIABLE`, the frozen keyword-only `BudgetPolicy`
  (`download`, `wait`, `socket` 30, `probe` 15, `metadata` 60, `retry_delay`
  5, `source`), `BudgetSettingError` (`exit_code = 2`) and
  `resolve_budget(environment)`. Unset gives D 300 and W 360; a value from 300
  through 3600 in ASCII digits, leading zeros allowed, gives exactly D and
  D + 60; every other form is refused with the variable name and its range,
  never clamped. The name matches whatever its case. The module reads no
  process environment itself: the caller hands it the mapping.
- **Git-cliff domain**: `schemas.git_cliff_domain(pins)` builds the
  `git-cliff` domain with one fixed `[git-cliff]` section and one `version`
  rule, whose converter is `partial(manifest.parse_pin, pins=pins)` and whose
  default is `manifest.default_version(pins)`. `GIT_CLIFF_SCHEMA` follows the
  version domain in `SHIPPED_SCHEMAS`. The schema module imports the manifest
  at load time, as the confirmed facts of the plan require.
- **Package surface**: `tools/release_workflow/git_cliff/__init__.py`
  documents the two modules and imports nothing; the docstring of
  `tools/release_workflow/__init__.py` names `lock_records` and the
  `git_cliff` package.
- **Tests**: new leaves `test_lock_records/`, `test_git_cliff_manifest/`
  (TDD and PBT) and `test_git_cliff_budget/` (TDD and PBT).
  `test_schemas_tdd.py` checks the three-domain shipped tuple, the fixed
  section and the synthetic default. `test_configuration_tdd.py` checks the
  known section, the unknown `executable` and other keys, the missing value
  and the `tested: none` refusal of the empty table, the synthetic default
  with its source information, the exact `2.15.0` message and the import
  freedom in a fresh `sys.modules` snapshot.
  `test_warm_lookups_never_hash_compare_or_visit_the_pins` passes a tuple
  subclass that records every `__iter__`, `__hash__`, `__eq__`, `__len__`
  and `__contains__` call, and asserts that warm `parse_pin`, `admitted` and
  `default_version` calls, hits and misses, record none.
- **Out-of-step test change**: the whole-suite walk measured a lifecycle CPU
  overrun (0.27 s against the 0.25 s band top) for one batch of
  `tests/unit/tools/test_scope_capture/test_scope_capture_pbt.py`, a test
  outside this step. Its names are now sampled from a precomputed pool of the
  same domain (one to four letters of a six-letter alphabet) instead of
  generated text filtered for uniqueness, and its three explicit limits run
  once in their own test instead of in each of the five batches. A
  side-by-side measurement gave 5.4 ms instead of 8.8 ms of CPU per batch
  call. No production code changes with it.
- **Second out-of-step test change**: the round 2 speed walk failed on the
  lifecycle CPU ceiling (0.109 s against 0.100 s, after the drift guard had
  dropped the proof of a case measured at 0.125 s in round 1) for
  `tests/unit/tools/shared_lifecycle/test_audit_declarations/test_audit_declarations_tdd.py::test_malformed_test_permission_prevents_setup[pytest.mark.process_allowed]`,
  one of seven embedded pytest sessions of about 25 ms each. One embedded
  session now proves that a malformed reason is a usage error before any
  setup, and `test_malformed_test_permission_forms_are_refused` checks the six
  distinct malformed forms directly against the mark validation of
  `AuditSession`, which every form reaches; the bare and empty-call spellings
  build the same mark. Every former assertion is still made, and no
  production code changes with it.
- **Validation evidence**:
  - Red first: `ghog single` on the seven Step 1 test files failed at
    collection on the missing modules (exit 4).
  - Targeted: `ghog single` on the Step 1 test files with
    `test_operation_lock_tdd.py` and `test_operation_lock_pbt.py`: exit 0,
    212 tests.
  - Gate: `ghog day --whole-suite`, the command printed by `pw scope day` at
    the default level, exit 0 at 2026-11-17T09:30:28+01:00, after repairs for
    ruff (`RUF043` and `RUF001` in new tests), the CPU overrun above and one
    pyright annotation; the affected stage of the second walk ran 7410 tests.
    The full stage is skipped at this level, so no coverage figure is
    measured here.
  - Code review round 1 repair: the new warm-lookup regression failed against
    the reviewed manifest with twelve recorded tuple hashes (`ghog single`,
    exit 2) and passes with the identity-keyed cache, together with the
    manifest property tests and the schema and configuration tests (exit 0).
  - `rg -n 'import' tools/release_workflow/git_cliff/manifest.py`:
    `__future__`, `re` and `dataclasses` only, plus one docstring line.
    `rg -n 'json.loads' tools/release_workflow/operation_lock.py`: no match.
    `rg -n 'getenv|environ' tools/release_workflow/git_cliff`: only the
    `environment` parameter of `budget.py`.
- **Line counts**: `git_cliff/manifest.py` 172 (advisory 110),
  `git_cliff/budget.py` 89 (advisory 80), `lock_records.py` 71 (advisory 70),
  `git_cliff/__init__.py` 18, `schemas.py` 245 (+25, as advised),
  `operation_lock.py` 244 (-17, advisory -25),
  `release_workflow/__init__.py` 14; new tests 87, 188, 66, 70 and 53
  (advisory 80, 180, 60, 130 and 50), initializers 3 each;
  `test_schemas_tdd.py` 189 (+38, advisory +20),
  `test_configuration_tdd.py` 327 (+71, advisory +30);
  `test_scope_capture_pbt.py` 22 to 46, `test_audit_declarations_tdd.py` 355
  to 379. Every Python file stays below 550;
  the split guidance was not needed.

### New types or classes introduced for Step 1

- `tools.release_workflow.lock_records`: `decode_object`, `positive_integer`
  and `text`.
- `tools.release_workflow.git_cliff.manifest`: `AdmittedPin`, `PinError`,
  `ManifestError`, `PLATFORM_TRIPLE`, `ADMITTED_PINS`, `validate_pins`,
  `default_version`, `admitted`, `parse_pin`, `download_url`, and the private
  per-table index `_Table`.
- `tools.release_workflow.git_cliff.budget`: `BudgetPolicy`,
  `BudgetSettingError`, `DOWNLOAD_BUDGET_VARIABLE`, the default, maximum and
  wait-margin constants, and `resolve_budget`.
- `tools.release_workflow.schemas`: `git_cliff_domain` and
  `GIT_CLIFF_SCHEMA`.
- Test folders `test_lock_records`, `test_git_cliff_manifest` and
  `test_git_cliff_budget`, with the instrumented `_CountingPins` table local
  to the manifest tests; no shared helper module, since the plan creates
  `git_cliff_support.py` in Step 3.

### Architecture check for Step 1

- **Domain table**: the manifest is pure data and pure functions, with no
  network, filesystem or process code and only standard-library imports. The
  budget policy is a pure function of the mapping its caller hands over, so
  the process environment is read at the provisioning boundary (Step 5), not
  inside the domain.
- **Composition point**: `schemas.py` is where the foundation declares the
  shipped domains; the git-cliff domain joins tooling and version there and
  imports only the manifest at load time, which the plan requires because the
  reader applies a default through the converter. The import-freedom test
  proves that loading configuration pulls no other `git_cliff` module.
- **Shared decoding**: `lock_records.py` depends on nothing in the engine;
  the operation lock depends on it, so the later cache lock never depends on
  the operation lock (plan decision Q02).
- **Module state**: the per-table index of the manifest is a private cache
  keyed by the identity of each validated table, which the entry keeps; it
  changes no result, only the cost of later lookups. The tables are the
  shipped tuple and the one each git-cliff domain captures, so the cache holds
  one entry in production.

No, there is nothing that needs to be addressed: no DDD-Hexagonal violation or
smell is visible in this step.

### Performance check for Step 1

- **No new `O(n^2)` or `O(n log n)` path**: validating a pin table is linear
  in its pins, with one set and one pass, and happens once per table. Every
  later `parse_pin`, `admitted` or `default_version` call is one dictionary
  access on `id(pins)`, an identity check, and one access by version in the
  cached index; no pin is hashed, compared or visited, which the warm-lookup
  regression asserts for hits and misses. Decoding a record is linear in its
  bytes. The budget lookup is one pass over the environment mapping of the
  caller, made once per caller, and the conversion of the value is bounded by
  stripping leading zeros and accepting at most four digits.
- **Hot-path bound**: configuration loading adds one fixed section and one
  rule; the empty table yields no value, and a declared pin costs one
  regular-expression match and the constant-time cached lookup.
- **Startup path**: importing the schemas also imports the manifest and
  validates the empty tuple once; configuration loading never imports the
  budget module.
- **Plan-bound alignment**: within the "O(1) amortized per call" bound of the
  plan for pin lookups, after the round 1 repair, and its single budget read
  per caller.

No, there is no performance issue that needs to be addressed.

### Unit test coverage check for Step 1

The coverage gate measures `tools` only (`[tool.coverage.run] source`), with
`*/tests/*` and `*/__init__.py` omitted, at `fail_under = 100`. The round 2
requestor reports 7414 passing tests and 100% coverage from
`ghog day --full=speed --whole-suite`, with no outliers or exclusions, and a
passing `ghog check` on the submitted tree after the documentation update.
The reviewer independently assessed the code and tests statically; no
reviewer test or coverage run was performed.

- **`tools/release_workflow/lock_records.py`**: `test_lock_records/` reaches
  the duplicate and unique paths of the pairs hook at the top level and in a
  nested object, the object and non-object results, malformed bytes, and both
  outcomes of `positive_integer` and `text`, missing keys included; covered.
- **`tools/release_workflow/git_cliff/manifest.py`**:
  `test_git_cliff_manifest/` reaches every invalid field, the duplicate
  version, both wrong default counts, the empty and synthetic tables, the
  cold and warm cache paths, both outcomes of `admitted` and `parse_pin`, and
  `download_url`; covered.
- **`tools/release_workflow/git_cliff/budget.py`**: `test_git_cliff_budget/`
  reaches the unset and set lookups, other cases of the name, similar names,
  the accepted values, and the non-digit, empty, out-of-range and long
  zero-padded refusals; covered.
- **`tools/release_workflow/schemas.py`**: `git_cliff_domain` runs at import
  and in `test_schemas_tdd.py` and `test_configuration_tdd.py`; the existing
  schema tests keep the rest covered.
- **`tools/release_workflow/operation_lock.py`**: the three delegating
  helpers run in the unchanged `test_operation_lock` suites, valid records and
  every refused field included; covered.

The lookup complexity is asserted by
`test_warm_lookups_never_hash_compare_or_visit_the_pins`, beside the count of
validations in `test_a_table_is_validated_and_indexed_once`.

Review round 2 confirms that the identity-keyed cache retains the tuple and
performs no warm traversal or tuple hash. The new regression detects the
round 1 defect. The audit test rework keeps one embedded-session assertion
that rejection precedes setup and checks every distinct malformed mark
directly through the same validator, preserving its identifying diagnostics.

No, there is no unit-tested class below 100% that needs completing for Step 1.

### Feature integrity for Step 1

- **Existing feature behavior**: the operation lock keeps its record format,
  refusals and messages, and its TDD and PBT suites pass unchanged. Every
  existing configuration test passes; `[tooling] git-cliff=...` stays an
  unknown key.
- **Reporting or diagnostics**: configuration errors keep their
  `<file> [section] key='<value>': <reason>` form, which the new pin refusals
  use; with a synthetic table, for example:
  `.release.ini [git-cliff] version='2.15.0': not a tested git-cliff pin; tested: 2.14.2`.
- **Compatibility or rollout note**: a project that declares `[git-cliff]`
  no longer gets "Unknown configuration section": an empty section loads, and
  any declared `version` is refused with `tested: none` until Step 7 admits
  2.14.2. The `version` and `versions` commands and builds never read the
  budget variable. The scope capture rework changes only how that property
  test generates and replays its cases, and the audit declaration rework only
  how many embedded sessions check the malformed marks.

No, there is no existing feature or reporting capability that appears
impaired.

---

## Step 2. Contained Windows children and the use guard

### Analysis of Step 2 implementation state

Yes. Step 2 has been fully implemented.

Reviewer round 3 independently inspected the staged changes and closes R1,
R2 and R4: failed handles remain owned through interruption, default SIGINT
delivery is deferred across native-call bookkeeping, outstanding resources
are retained even when an interrupt propagates, and release traversal is
linear. R3 remains resolved by the bounded native runners. The independent
commit-plan check is valid and ready for all six groups; no implementation
or test repair was made by the reviewer.

The three native modules exist with the plan's structure: `windows_native.py`
declares the structures, constants and kernel32 functions, `windows_child.py`
runs every child through the seven phases (no `subprocess` and no
create-then-assign path), and `windows_guard.py` holds the use guard. Code
review rounds 1 and 2 found gaps, now repaired. Cleanup dropped a handle
before its reset or close succeeded, or lost it when a failure and an
interrupt overlapped. An interrupt could escape the teardown or land between
a native call and its bookkeeping. The reset traversal was quadratic, and the
native recorder could not stop a stalled check. Every branch, each reviewer
sequence included, is exercised through the fake kernel and a fake loader.
The recorder, which bounds each check in its own contained runner, passed its
eight checks on a real kernel. The committed `native_checks.v1.json`, with its
stalled-runner demonstration, is accepted by its validator for the current
sources. One planned check changed by user decision: on Windows 11 build 26200
a job with UI limits did not refuse the nesting the design named, so the
refused creation is proven under a job limited to one active process, and the
design and plan now say so. Every completion criterion holds: the command
printed by `pw scope day` reports `exit=0` and the three `rg` checks find only
the expected matches.

### Goal for Step 2

Ship `windows_native.py` (the ctypes structures, constants and kernel loader
shared by the two other native modules) and `windows_child.py`, which checks
the Windows 10 or Windows Server 2016 x64 baseline and runs each child
through the design's lifecycle (a
parent-only kill-on-close job, suspended `CreateProcessW` with a
`STARTUPINFOEX` carrying the job list and the handle list, an optional
recording callback before resume, a deadline wait, then a job-wide teardown
confirmed before the output pipes are joined), plus the launcher's console
interrupt filter; ship `windows_guard.py`, the use guard opened with
`FILE_SHARE_READ` only and hashed through a duplicated handle; and create the
developer-run native check recorder with its Step 2 due set, its committed
record and the test that validates it.

### Step 2 improvement expectations

- No code path creates a child outside its job, assigns a job after creation
  or falls back to `subprocess`; every failure before resume leaves no running
  child.
- A failing identity lookup, recording callback or `ResumeThread` tears the
  job down and confirms the end before the error propagates.
- On a normal exit and on expiry, `TerminateJobObject`, the root wait and a
  zero `ActiveProcesses` count come before the reader join, so a descendant
  holding a pipe write end cannot block the call; the root's status is kept.
- A failing termination, wait or count query raises `UnconfirmedEndError`,
  joins no reader, and moves the job, process, thread and pipe handles to the
  process-lifetime owner `RETAINED`, which no `finally`, context manager or
  `close()` path releases.
- Readers are daemon threads over native pipe handles and private buffers, so
  a pipe-holding descendant cannot hold interpreter shutdown; the native
  teardown-failure exit check shows the parent exiting and its descendant
  ended by kill-on-close.
- A failed identity lookup followed by a failed teardown raises the error with
  `identity=None`; the child stays suspended and unrecorded.
- `UseGuard.retain()` makes `close()` a no-op for a guard registered in
  `RETAINED`.
- The handle list holds only the standard handles and, when requested, the
  guard; listed handles are inheritable only around the creation call.
- The console filter is a handler routine, kept referenced while registered
  and removed on success and on errors, never the inherited null routine.
- The three native modules reach 100% coverage through the fake kernel and a
  fake loader, and no declaration test calls the operating system.
- The native check record holds milestone `step-2`, and every due check
  `passed` on temporary paths and stand-in children against the current
  sources; the validator refuses a missing, failed, timed-out, skipped or
  stale check.

### What was implemented for Step 2

The current diff delivers the Step 2 file list of the plan, a docstring line
in `tools/release_workflow/__init__.py`, the design and plan corrections for
the refused creation, and one formatting fix outside the step.

- **Native declarations**: `tools/release_workflow/windows_native.py` defines
  the x64 structures `STARTUPINFOW`, `STARTUPINFOEXW`, `PROCESS_INFORMATION`,
  `JOBOBJECT_BASIC_LIMIT_INFORMATION`, `IO_COUNTERS`,
  `JOBOBJECT_EXTENDED_LIMIT_INFORMATION` and
  `JOBOBJECT_BASIC_ACCOUNTING_INFORMATION`, the creation, job, file, wait,
  console and error constants, the `PHANDLER_ROUTINE` callback type and
  `kernel(loader=None)`. It gives each of the 23 functions the layer calls its
  argument types, result type and error check, then caches the declared
  library per loader. Every error check raises `NativeCallError` (an
  `OSError` carrying the call name and the Windows error) on a failed result:
  a zero BOOL, a NULL or invalid handle, `WAIT_FAILED` or a failed resume.
  Only the sizing call of the attribute list may answer with an insufficient
  buffer. Pointer arguments take the ctypes instances themselves.
- **Contained children**: `tools/release_workflow/windows_child.py` defines
  `require_supported_platform` (platform version 10 or later on an x64
  machine, otherwise `PlatformError` with the baseline remedy), the frozen
  `ChildRequest` (stream modes and environment entries checked when built,
  `list2cmdline` command line, environment block sorted case-insensitively),
  the frozen `ChildOutcome`, and `run_contained(request, *, api=None,
  sleep=time.sleep)` in the seven phases of the plan. Setup creates the
  kill-on-close job, the `NUL` handle or the parent's standard handles, the
  capture pipes and an attribute list holding exactly the job list and the
  handle list (standard handles listed once, then the guard handles).
  Creation makes only the not yet inheritable listed handles inheritable,
  calls `CreateProcessW` suspended, then restores inheritance, deletes the
  list and closes the parent's write ends and `NUL`. Pre-resume reads the
  identity, calls the recording callback and resumes. The wait starts two
  daemon readers over the native read handles and waits within the deadline.
  The teardown terminates the job, reaps the root and polls the accounting
  count to 0 through the injected sleep. Only then does the drain read the
  root's status, join the readers and close every handle. Any failure before
  the teardown, an interrupt included, settles the attempt: a created child is
  ended and its end confirmed, every resource released, then a native or other
  error raises `ContainmentError` and an interrupt propagates as is. A failing
  termination, reap wait or accounting query, or any other error while
  polling, moves the job, process, thread and read handles with the readers
  into `RETAINED` and raises `UnconfirmedEndError`, which names the PID, the
  identity (`None` when it was never read) and the call. `is_process_in_job`
  and the `ignore_console_interrupts` handler routine complete the module.
- **Code review repairs, rounds 1 and 2**: the handle bookkeeping is a set of
  ordered dictionaries, so every release is linear. A handle is registered
  before the call that makes it inheritable, the process and thread handles
  are adopted from the filled process information, and each close takes its
  handle out of the set first and puts it back if the close fails. A failed
  reset or close keeps its handle and failure, every other handle is still
  released, and settling retries what remains. Whatever still remains goes to
  `RETAINED` on every exit path, named in `ContainmentError.cleanup` or, when an
  interrupt propagates, in a note on it (a caller's guard left inheritable
  among them). On the main thread, with Python's default handler, the run
  replaces the SIGINT handler with one that records a Ctrl+C; the run raises
  it at safe points where every handle is accounted for (after setup, before
  resuming, after the wait) or once it is settled. A launcher's console filter
  still swallows Ctrl+C before Python sees it. A `KeyboardInterrupt` raised
  while the run is ended or released is held back the same way: the action
  runs again to its end, and a successful termination is not repeated. An
  `UnconfirmedEndError` still wins, so its caller keeps every resource. The
  recorder runs each check in its own runner process, started through
  `run_contained` with the check's bound as deadline. On expiry the job-wide
  termination ends the runner and its whole helper tree and the check is
  recorded `timed-out`; production reap semantics are unchanged.
- **Use guard**: `tools/release_workflow/windows_guard.py` defines `UseGuard`
  and `open_guard`. The guard is a `CreateFileW` handle with `GENERIC_READ`,
  `FILE_SHARE_READ` only, `OPEN_EXISTING` and no security attributes. A
  missing file or folder raises `FileNotFoundError` and any other refusal an
  `OSError` carrying the Windows error and the path. `sha256_and_size()`
  duplicates the handle, rewinds the shared position, hashes to the end and
  closes only the duplicate. `close()` is idempotent, the context manager
  closes, and `retain()` registers the guard in `RETAINED`, after which no path
  closes it.
- **Fake kernel and tests**: `tests/unit/tools/release_workflow/native_kernel_fake.py`
  logs every call, fails a chosen occurrence of a function as its error check
  would or interrupts it once it ran, plays a declared child (status, output,
  still running at its deadline, a descendant holding stdout until
  termination) and blocks pipe
  reads until data or the last write-end holder ends, with a safety bound and
  a logged end of file. The new leaves `test_windows_native/`,
  `test_windows_child/` (lifecycle and faults) and `test_windows_guard/`
  cover the plan's test list.
- **Native check recorder and record**:
  `tests/unit/tools/release_workflow/git_cliff_native_checks.py`, started by
  hand and never imported by a test, runs the cumulative due set of a
  milestone on stand-in children and temporary paths, each check in its own
  bounded runner process, restarting itself as helper parents, and writes
  `native_checks.v1.json` (sorted keys, LF, no host path). The record's
  `recorder_timeout` entry shows a deliberately stalled runner ended at its
  3 s bound, its helper child alive then and ended after it. The Step 2 set: job membership before resume; a suspended child
  ending with its killed parent; a creation refused by the job of a helper
  limited to one active process; kill-on-close of a running child; a root
  exiting while its descendant holds stdout; a helper exiting normally after
  its termination call was made to fail, its descendant then ended by
  kill-on-close; the guard refusing a rename before any child and while a
  child runs with the inherited copy only. The two descendant checks also
  observe the descendant alive at the decisive moment.
  `test_git_cliff_native_evidence_tdd.py` validates the record against its own
  catalog (outcome, expected and observed observation, bound and
  LF-normalized source digests, commit and host facts, the timeout
  demonstration, no host path or user or host name) and refuses each
  defective record built in memory.
- **Deviation decided by the user (2026-11-18)**: the planned check "a refused
  creation under a job with UI limits" could not pass, since on Windows 11
  build 26200 a helper inside a job with UI restrictions (0x1, 0x20, 0x40,
  0xff) created the job-list child normally. Two real refusals were found: a
  job limited to one active process (`CreateProcessW` error 1816, the job
  counting only the helper) and a job list holding a query-only job handle
  (error 5). The user chose the first. The design facts row, lifecycle step 3,
  the Containment remedy, the testing approach and the acceptance row, and the
  plan's Step 2 recorder text, now name it.
- **Out-of-step test change**: the round 3 request walk measured 0.109 s of
  lifecycle CPU, above the 0.100 s ceiling and not proven here, for
  `tests/unit/tools/shared_lifecycle/test_audit_declarations/test_audit_declarations_tdd.py::test_inherited_permissions_are_invalid[module]`,
  whose cost is one embedded pytest session. As Step 1 did for the same file,
  the class-level case keeps its embedded session, and the module-level case
  calls the plugin's collector check directly on a module collector carrying
  the mark, the check both levels reach. No production code changes with it.
- **Out-of-step formatting fix**: line 419 of
  `docs/v0.14.0/review.code.v0.14.0.git-cliff-provisioning.md`, committed with
  Step 1, held a bare `AdmittedPin.__hash__` from the reviewer's answer, which
  fails Markdown rule MD050 at `HEAD`. Its identifiers are now code spans; no
  word changed.
- **Validation evidence**:
  - Red first: `ghog single` on the five Step 2 test files failed at
    collection on the missing `windows_native` module (exit 4).
  - Targeted: `ghog single` on the five Step 2 test files with
    `test_windows_process_tdd.py`: exit 0, 91 tests.
  - Gate: `ghog day --whole-suite`, the command printed by `pw scope day` at
    the default level, exit 0 at 2026-11-18T09:49:42+01:00, after one walk
    that failed at check (typing, lint, complexity and the MD050 line above).
  - Round 1 repairs, red first: the thirteen new fault cases run against the
    reviewed `windows_child.py`: `ghog single` exit 4, 10 failed (cleanup
    stopping early, a failed reset lost, raw interrupts escaping the end).
    Green with the repaired module: the four kernel-based files with
    `test_windows_process_tdd.py`, exit 0, 91 tests; then every Step 2 test
    file with it, 107 tests, after `ghog check` passed.
  - Round 2 repairs, red first: the nine new sequences run against the
    round 2 reviewed `windows_child.py`: `ghog single` exit 2, 9 failed.
    Green with the repaired module: 100 tests with the other kernel-based
    files and `test_windows_process_tdd.py`, then every Step 2 test file, 116
    tests, after `ghog check` passed.
  - Native record, after the last source change: the recorder with
    `--milestone step-2` passed 8 of 8 checks through their runners (0.38 s
    to 1.03 s each), and the stalled runner timed out at its 3 s bound in
    3.08 s with its helper tree ended; the validator accepts the record.
  - `rg -n 'subprocess\.(Popen|run|call)|AssignProcessToJobObject'` on the
    three modules: no match. `rg -n 'SetConsoleCtrlHandler'
    tools/release_workflow`: the registration and removal in
    `windows_child.py` and the declaration in `windows_native.py`.
    `rg -n 'TerminateJobObject|\.join\(' tools/release_workflow/windows_child.py`:
    the termination in `_teardown`, then the single reader join in
    `_release`, which runs only after a confirmed end (the drain and the
    settling both call the teardown first).
- **Line counts**: `windows_native.py` 286 (advisory 180),
  `windows_child.py` 594 (advisory 360), `windows_guard.py` 120 (advisory
  120), `native_kernel_fake.py` 456 (advisory 310),
  `git_cliff_native_checks.py` 598 (advisory 190); tests 165, 234, 474, 104
  and 212 (advisory 90, 280, 380, 140 and 130), initializers 3 each;
  `release_workflow/__init__.py` 17 (+3); `native_checks.v1.json` 213. Every
  Python file stays below the 650 ceiling; the advisory overruns are variance.
  `windows_child.py` and the recorder sit in the 550 to 650 band.
  `windows_child.py` grew with the review repairs, and no later step plans to
  extend it. The plan adds about 190 lines to the recorder in Steps 4, 5 and
  8, so Step 4 meets the split guidance of shared checklist item 7 before it
  adds its check.

### New types or classes introduced for Step 2

- `tools.release_workflow.windows_native`: the seven structures above,
  `PHANDLER_ROUTINE`, `NativeCallError`, the `Kernel` protocol and `kernel`.
- `tools.release_workflow.windows_child`: `PlatformError`,
  `ContainmentError` (with `call`, `error` and `cleanup`),
  `UnconfirmedEndError`, `RetainedChild`, `RETAINED` (the private `_Retained`
  owner), `require_supported_platform`, `ChildRequest`, `ChildOutcome`,
  `run_contained` (with the private `_Run` phases, its settling and
  interrupt-deferring helpers, and `_Reader` threads), `is_process_in_job` and
  `ignore_console_interrupts`.
- `tools.release_workflow.windows_guard`: `UseGuard` and `open_guard`.
- Test support: `FakeKernel` (with `fail` and `interrupt`), `FakeChild` and
  `Creation` in `native_kernel_fake.py`; the recorder with its `_Check`
  catalog, runner mode and timeout demonstration; the validator catalog `_Due`
  in the evidence test.

### Architecture check for Step 2

- **Infrastructure placement**: the three modules are the engine's Windows
  adapter layer, beside `windows_process.py`; they import only the standard
  library, `windows_process.ProcessIdentity` and each other, never a domain or
  configuration module, and nothing outside the recorder imports them yet.
- **Dependency direction**: `windows_guard` depends on `windows_child` for
  `RETAINED` and both depend on `windows_native`; `windows_child` never
  imports the guard and receives guard handles as plain integers in
  `ChildRequest.inherited`, so there is no cycle.
- **Kernel seam**: every native call goes through the declared `Kernel`
  object passed as `api`, the real library only when `api` is `None` (plan
  decision Q05); no test patches a module attribute to reach it.
- **Process-lifetime state**: `RETAINED` is append-only by design: it owns
  what an unconfirmed end forbids closing, and the operating system closes it
  with the process. The declaration cache holds the declared library per
  loader.

No, there is nothing that needs to be addressed: no DDD-Hexagonal violation or
smell is visible in this step.

### Performance check for Step 2

- **One required `O(n log n)` sort**: building the
  environment block sorts the environment entries, because `CreateProcessW`
  requires a sorted block and the plan names that order; it runs once per
  child over the environment's tens of entries. Setup, creation and teardown
  make a constant number of kernel calls plus one inheritance query per
  listed handle (at most three standard handles and the guards). The readers
  and the guard hash are linear in the bytes read, in 64 KiB and 1 MiB
  chunks.
- **Hot-path bound**: none of this runs during configuration loading or any
  existing command; the accounting poll sleeps 10 ms between reads and only
  after a successful termination, which the design leaves unbudgeted.
- **Startup path**: importing the modules declares nothing; the kernel is
  loaded and declared on first use, once per process.
- **Plan-bound alignment**: within the "O(n) total per phase" bound for child
  runs and the one hash pass the reuse check allows. Since round 2 the
  bookkeeping is ordered dictionaries: each reset, close, retry and adoption
  is a constant-time membership change, so a release is linear in the
  inherited handles (round 1 had a quadratic `list.remove` traversal). A
  resumed teardown repeats a constant number of kernel calls, and the
  developer-run recorder bounds each whole check from outside the production
  lifecycle, whose reap stays unbudgeted as designed.

No, there is no performance issue that needs to be addressed.

### Unit test coverage check for Step 2

The coverage gate measures `tools` only (`[tool.coverage.run] source`), with
`*/tests/*` and `*/__init__.py` omitted, at `fail_under = 100`. This check
reasons from the code and the tests. The writer reports a whole-suite speed
walk of 7,519 tests with 100% measured coverage, zero outliers and zero
exclusions on the round 3 request tree. The reviewer did not rerun that walk
or measure coverage independently.

- **`tools/release_workflow/windows_native.py`**: `test_windows_native/`
  checks the layouts and constants, declares the 23 functions through a fake
  loader (cached per loader) and reaches the failing and passing result of
  every error check, both sizing answers included; covered.
- **`tools/release_workflow/windows_child.py`**: `test_windows_child/`
  reaches both platform outcomes, every request refusal, the environment
  block with entries, empty and inherited, both stdin and output modes with a
  guard, the inheritance skip and set, the deadline conversions, expiry, the
  descendant cases, the accounting poll, membership and the console filter.
  The faults file reaches every setup and creation failure, a missing
  standard handle, the three pre-resume failures, the interrupt, a failed
  deadline wait, status read and pipe read, the three unconfirmed ends and the
  identity failure with an unconfirmed teardown. Since round 1 it also
  reaches a reset failure retried while settling and one left retained, close
  failures before and after the end, a refused creation with both cleanup
  failures, an interrupt during setup, right after creation, while polling
  and repeatedly during recovery, a pending interrupt replacing a containment
  error, an error while polling and an unconfirmed end winning over an
  interrupt; ten of these failed on the round 1 module. Round 2 adds the
  reviewer's sequences: a failed close then a Ctrl+C, a failed close left by
  an interrupt from the callback (retained and noted), and a Ctrl+C right
  after a guard's inheritance is enabled, after `CreateProcessW`, and after
  the job, `NUL`, a pipe or the attribute list is acquired. It also checks
  where the Ctrl+C deferral applies (main thread, default handler) and that
  no handle is ever closed twice; the nine new cases failed on the round 2
  module. Covered.
- **`tools/release_workflow/windows_guard.py`**: `test_windows_guard/`
  reaches the open, both missing-file errors, the sharing violation, hashing
  twice through duplicates, the closed guard, the idempotent close and the
  retained guard; covered.
- **Files outside the gate**: `native_kernel_fake.py` and
  `git_cliff_native_checks.py` live under `tests` and are not measured.
  Every top-level symbol of the fake is used by the Step 2 tests or inside
  the fake itself; every
  top-level function and class of the recorder is reached from its `main`,
  its runner or helper dispatch or its check catalog, and the record proves
  the run.

No, there is no unit-tested class below 100% that needs completing for Step 2.
No, none of the top-level symbols of the files outside the gate is
unreferenced.

### Feature integrity for Step 2

- **Existing feature behavior**: no existing module changes behavior;
  `windows_process.py` is reused unchanged and its tests pass, and the only
  edit to an existing source file is the package docstring.
- **Reporting or diagnostics**: the new errors carry the stage name the Step 5
  messages module will map (`platform`, `containment`, `unconfirmed-end`), the
  failing call and, for a release that left handles, the failed cleanup calls;
  an interrupt never replaces an unconfirmed end. Nothing is printed yet.
- **Compatibility or rollout note**: nothing calls the layer before Step 3.
  The design's containment example and remedy now name a host job that
  limits its processes instead of UI limits; the transcript fix only adds code
  spans.

No, there is no existing feature or reporting capability that appears
impaired.

---

## Step 3. Cache layout, entry record, reuse check and the cache lock

### Analysis of Step 3 implementation state

Yes. Step 3 has been fully implemented.

`git_cliff/cache.py` places every pin at its fixed path, with a separate
evidence namespace that no production version can reach. It decodes the entry
record and the owner file strictly. Its reuse check opens the guard, reads the
record, hashes and probes in that order, stopping at the first failure.
`git_cliff/cache_lock.py` publishes a complete lock record without
replacement under a transition mutex named from the cache root's file
identity, namespace, version and triple. A waiter gets one callback for a live
holder, then polls every 250 ms until its own deadline, which a holder change
never resets. Recovery of a record or of an attempt directory needs its owner
and every recorded child `DEAD`. The root `.gitignore` holds
`/.tools/git-cliff/`. Code review round 1 found that the wait could still
publish after its deadline when a sleep woke late, or when entering the mutex
or proving a dead holder ran past W (R1). A poll now reads the clock inside
the mutex after those steps and publishes or replaces nothing once the
deadline has passed. Regressions cover a late wake-up and liveness queries
crossing W; both failed on the reviewed module. Every behavior of the plan's
test list is exercised with a fake clock, declared process states, an
uncontended mutex, fake guards and a write-denying helper, without a process
or a real wait. The command printed by `pw scope day` reports `exit=0`, and
the three `rg` checks find only the expected match. The interface differs
from the plan's sketch in a few details, listed below with their reasons.

The independent round 2 review confirms that R1 is resolved: the fixed
deadline is checked inside the transition after record reading and liveness
queries, before authorizing acquisition. The late-wake and slow-probe cases
preserve absence or the dead record, respectively; the last holder remains
available for diagnostics and the waiting callback remains single. The
review assessed the staged implementation and tests without rerunning tests
or measuring coverage.

### Goal for Step 3

Ship `git_cliff/cache.py` (the layout with production and evidence
namespaces, attempt names carrying their owner, the entry record, the owner
file and the lock-free reuse check) and `git_cliff/cache_lock.py` (the lock
record under a transition mutex, the bounded wait with its message, child
recording and owner-aware recovery of the record and of attempt directories),
and add `/.tools/git-cliff/` to the root `.gitignore`.

### Step 3 improvement expectations

- Reuse runs guard, record, hash and probe in that order, stops at the first
  failure, closes the guard on an ordinary failure and writes nothing; a probe
  raising `UnconfirmedEndError` retains the guard before the error
  propagates, and caller cleanup leaves it open.
- `retain_record()` makes a later `release()` leave the lock record, and
  recovery still needs the owner and every recorded child `DEAD`.
- A waiter prints one waiting line, polls every 250 ms of fake time and fails
  at its own W with the lock path, the owner and the remedy.
- Recovery requires the owner and every recorded child to be `DEAD`; `ALIVE`
  and `UNKNOWN` actors keep the record and their attempt directories, and an
  abandoned mutex authorizes nothing.
- No production layout resolves into the evidence namespace.
- The ignore-rule test finds `/.tools/git-cliff/` in the root `.gitignore`.

### What was implemented for Step 3

The current diff delivers the Step 3 file list of the plan and a docstring
update in `tools/release_workflow/git_cliff/__init__.py`, which now names the
two new modules.

- **Cache layout**: `CacheLayout(tooling_root, namespace="production")` is a
  frozen value whose `root` is `<tooling_root>/.tools/git-cliff`, or its
  `evidence` folder for the evidence namespace; any other namespace is
  refused. `version_dir`, `entry_dir`, `executable`, `record` and `lock_path`
  give `<pin>/`, `<pin>/<triple>/`, `git-cliff.exe`, `entry.json` and
  `<pin>/<triple>.lock`. A version directory name must be three dot-separated
  digit runs and a triple a dashed lowercase name. So `evidence`, `..`, a
  `v` prefix or a path separator never becomes a directory, and no
  production pin resolves into `evidence/`. `attempt_dir(pin, kind, owner,
  token)` builds `.staging-<pid>-<created>-<token>` or `.retired-...` only
  for a positive PID and creation time and a lowercase hexadecimal token.
  `parse_attempt(name)` gives back an `Attempt` (kind, owner, token) for a
  canonical name and `None` for anything else, leading zeros and suffixes
  included.
- **Records**: `EntryRecord` (schema 1, eight fields in a fixed order) checks
  its own values when built: schema 1, non-empty names, two lowercase
  SHA-256 digests, a positive size and a `provisioned` time with its offset.
  `decode` goes through `lock_records` with the `entry` label, so an extra,
  missing, duplicate or mistyped field and a foreign schema are refused.
  `OwnerFile` (owner and children, schema 1) decodes the same way with the
  `owner file` label. Its children, and those of the lock record, are objects
  holding exactly a positive `pid` and `created`.
- **Reuse check**: `check_entry(layout, pin, *, open_guard, probe)` returns a
  `ValidEntry` holding the open guard and the record, or an `UnusableEntry`
  with `absent` and a reason. A missing executable is absent, and nothing else
  is read. A missing, unparsable or foreign `entry.json` is invalid before any
  hash. A size or digest mismatch is invalid before the probe. A probe that
  timed out, exited with a status other than 0, or whose first line is not
  `git-cliff <pin>` is invalid. Each of these closes the guard. An
  `UnconfirmedEndError` from the probe retains the guard first, so the
  caller's cleanup leaves it open. Any other exception closes the guard and
  propagates, as does a guard open failure other than a missing file, so its
  real cause is reported.
- **Cache lock**: `CacheLock(layout, pin, *, caller, seams)` builds nothing on
  disk until its first transition. That transition creates the version
  directory with its parents and names the mutex
  `Global\llm-shared-git-cliff-<dev>-<ino>-<namespace>-<version>-<triple>`
  from `stat` of the namespace root. Each poll enters the mutex and reads the
  record. With no record, or with one whose owner and every child are `DEAD`,
  it writes this caller's complete record (owner, start time with offset,
  caller kind, no child) to a flushed temporary beside it. It then publishes
  by a non-replacing rename, or replaces a proven-dead record in the same
  transition, and the temporary never stays. `acquire(wait_seconds, on_wait)`
  fixes its deadline once and calls `on_wait(holder, W)` once for the first
  live holder. It then sleeps `min(0.25, remaining)` between polls and raises
  `LockWaitError` at W. The error carries the lock path, the last live
  holder's PID and start time and the design's lock-wait remedy
  (`LOCK_WAIT_REMEDY`, built from the budget variable and its bounds). An
  unverifiable record raises
  `LockRecordError` at once and stays in place. `record_child` appends one
  identity under the mutex. `release` removes the record only while it is
  still this caller's. After `retain_record()`, `release` removes nothing, and
  `record_child` and `recover_attempts` are refused.
- **Code review round 1 repair (R1)**: `_poll` receives the fixed deadline and
  reads the clock inside the mutex, after entering it, reading the record and
  probing the actors. Past the deadline it publishes nothing and replaces no
  dead record. `acquire` then raises `LockWaitError` naming the last live
  holder seen; `owner` and `started` are `None` only when no live holder was
  ever seen, as when proving a dead holder itself ran past W. A lock freed by
  the poll at exactly W is still taken.
- **Attempt recovery**: `recover_attempts()`, refused unless the lock is held,
  lists the version directory once without recursion. It keeps only
  directories with a canonical attempt name, then removes one only when its
  name owner is `DEAD` and every child of its `owner.json` is `DEAD`. The
  owner file must name the same owner; a missing file means no child was ever
  recorded. An unreadable or invalid owner file, a live or `UNKNOWN` actor and
  a refused removal keep the directory. The call returns the names it
  removed.
- **Ignore rule**: the root `.gitignore` ends with a comment and
  `/.tools/git-cliff/`.
- **Test support and tests**: `tests/unit/tools/release_workflow/git_cliff_support.py`
  holds the fake clock (with an optional oversleep for a late wake-up),
  declared process states, the uncontended mutex that can declare its entries
  abandoned, and the `LockWorld` scenario builder, whose liveness queries can
  each take fake time. It
  also holds the synthetic 2.14.2 pin built from a generated archive, the
  entry installer, the fake guard opener and probe, and the write-denying
  helper. That helper refuses and records `mkdir`, `rename`, `replace`,
  `remove`, `unlink`, `rmdir`, a write-mode `open` and a writing `os.open`.
  The new leaves `test_git_cliff_cache/` (tdd and pbt) and
  `test_git_cliff_cache_lock/` (lock and recovery) cover the plan's test
  list.
- **Interface details that differ from the plan's sketch**:
  - `CacheLock` takes its seams as one frozen `LockSeams` (clock, sleep, then
    `probe=process_state`, `current=current_identity`,
    `mutex=transition_mutex` and a local-time `now`) instead of six keywords,
    because the repository's lint allows five arguments.
  - `recover_attempts()` takes no pin, since a lock already serves one
    version and platform.
  - A pin is any value with a `version` and a `triple` (the `CachePin`
    protocol), so an evidence candidate fits too.
  - The probe seam returns a `ChildOutcome`, whose status and time-out the
    check reads beside the first line.
  - `EntryCheck` is the union of `ValidEntry` and `UnusableEntry`.
  - An unverifiable lock record fails at once with `LockRecordError` instead
    of being waited on, because it cannot prove an owner and waiting cannot
    change it.
- **Validation evidence**:
  - Red first: `ghog single` on the four Step 3 test files, with `cache.py`
    and `cache_lock.py` held aside, failed at collection on the missing
    `git_cliff.cache` module (exit 4).
  - Targeted: `ghog single` on the four test files, exit 0.
  - Gate: `ghog day --whole-suite`, the command printed by `pw scope day` at
    the default level, exit 0 at 2026-11-18T21:02:24+01:00. One earlier walk
    failed at check on typing in the test support and on lint (a function with
    eight returns, now split into three helpers, and a docstring with a
    backslash, now raw).
  - Round 1 repair, red first: the three new deadline cases run against the
    reviewed `cache_lock.py`: `ghog single` exit 2, the late wake-up and the
    liveness queries crossing W both failed with `DID NOT RAISE
    LockWaitError`. Green with the repaired module: the four Step 3 test
    files, exit 0.
  - `rg -n '\.tools/git-cliff/' .gitignore`: line 124.
    `rg -n 'getmtime|st_mtime|age' tools/release_workflow/git_cliff/cache_lock.py`:
    no match. `rg -n 'subprocess|Popen'
    tests/unit/tools/release_workflow/git_cliff_support.py`: no match.
- **Line counts**: `cache.py` 395 (advisory 260), `cache_lock.py` 377
  (advisory 290), `git_cliff_support.py` 327 (advisory 230); tests 289, 49,
  255 and 175 (advisory 230, 60, 250 and 220), initializers 3 each;
  `git_cliff/__init__.py` 24 (+6); `.gitignore` 124 (+3, advisory +2). Every
  Python file stays below 550; the advisory overruns are variance.

### New types or classes introduced for Step 3

- `tools.release_workflow.git_cliff.cache`: the `CachePin` and `Guard`
  protocols, `Attempt`, `CacheLayout`, `EntryRecord`, `OwnerFile`,
  `ValidEntry`, `UnusableEntry`, the `EntryCheck` alias, `check_entry`, the
  record helpers `local_time`, `identity_fields` and `decode_children`, and the
  names `SCHEMA`, `EXECUTABLE`, `ENTRY_RECORD`, `OWNER_FILE`, `NAMESPACES` and
  `ATTEMPT_KINDS`.
- `tools.release_workflow.git_cliff.cache_lock`: `LockRecord`,
  `LockRecordError`, `LockWaitError`, `LockSeams`, `CacheLock` and
  `LOCK_WAIT_REMEDY`.
- Test support: `FakeClock`, `ProcessStates`, `UncontendedMutex`,
  `LockWorld`, `synthetic_archive`, `synthetic_pin`, `entry_record`,
  `install_entry`, `FakeGuard`, `FakeGuardOpener`, `FakeProbe`, `WriteDenial`
  and `deny_writes` in `git_cliff_support.py`.

### Architecture check for Step 3

- **Ports at the consumer**: the reuse check depends on two protocols it
  defines, `Guard` and `CachePin`, and on two injected callables, the guard
  opener and the probe. The production adapters, `windows_guard.open_guard`
  and the Step 5 invocation's contained probe, are passed in; the cache
  imports no native module beyond the error and outcome types of
  `windows_child`.
- **Lock seams**: the cache lock reaches the kernel only through `LockSeams`,
  whose defaults are the item 1 `windows_process` primitives, reused
  unchanged. The lock stays separate from the per-project `OperationLock`, as
  the design requires, and shares only the strict decoder of `lock_records`
  with it (plan decision Q02).
- **Dependency direction**: `cache_lock` depends on `cache` (layout, owner
  file, record helpers) and on the `budget` constants for its remedy text;
  `cache` never imports `cache_lock`, and neither imports configuration,
  dispatch or the operation lock. `LOCK_WAIT_REMEDY` is the single source of
  the lock-wait remedy wording.
- **Records and paths**: persisted records decode through the shared strict
  decoder before reuse or recovery. `EntryRecord` also validates construction;
  `OwnerFile` and `LockRecord` rely on typed caller inputs when constructed.

No, there is nothing that needs to be addressed: no DDD-Hexagonal violation or
smell is visible in this step.

### Performance check for Step 3

- **Reuse**: one guard, one record read, one hash pass through the guard
  (linear in the executable's bytes) and one probe; the probe output is
  decoded once and only its first line is compared. Nothing is written.
- **Lock wait**: each poll is one mutex entry, one record read and the
  liveness probe of the owner, then of its children only when the owner is
  `DEAD`, so the wait is linear in its polls (W / 250 ms at most). The mutex
  name is computed once per lock. Since the round 1 repair the deadline is
  enforced at publication too: a poll reads the clock inside the mutex after
  its entry and the probes, so no oversleep or slow transition acquires or
  recovers after W.
- **Child recording**: `record_child` rewrites the complete record, linear in
  its children, as the design publishes only complete records; an attempt
  records at most three children (two download attempts and the staging
  probe), so the rewrites stay constant per attempt.
- **Recovery**: one non-recursive listing of one version directory; per
  attempt directory one owner probe, at most one owner file read, the probes
  of its children and a removal linear in the directory's files. No sort, no
  pairwise comparison and no tree scan.
- **Plan-bound alignment**: within "O(1) amortized per call" for reuse and a
  poll, and "O(n) total per phase" for the wait and recovery.

No, there is no performance issue that needs to be addressed.

### Unit test coverage check for Step 3

The coverage gate measures `tools` only (`[tool.coverage.run] source`), with
`*/tests/*` and `*/__init__.py` omitted, at `fail_under = 100`. This check
reasons from the code and the tests. The writer reports each review request's
whole-suite speed walk, `ghog day --full=speed --whole-suite`, with 100%
measured coverage, no outlier and no exclusion on that request's tree (round
1: 7636 tests; round 2: 7639 tests on index tree
`78c002416187a2ba1488ea1915eb4099d7b5ed3a`). The reviewers assessed code and
tests statically and ran no test or coverage measurement. The bound scope is
whole, with speed proof, and the built-in default command has no
`.review-validation` override.

- **`tools/release_workflow/git_cliff/cache.py`**: `test_git_cliff_cache/`
  reaches both namespaces and the refused one, every path method, the refused
  version and triple names, valid and refused attempt parts, canonical and
  malformed attempt names, the entry record round trip and thirteen invalid
  records, the owner file round trip, a malformed child and refused fields or
  schema. It also reaches every reuse outcome: absent, missing, unparsable and
  foreign records, size and digest mismatches, the four probe failures, a
  valid entry under the write-denying helper, an unconfirmed probe end and
  another probe failure. The children decoder is also reached through the
  lock record cases; covered.
- **`tools/release_workflow/git_cliff/cache_lock.py`**: `test_git_cliff_cache_lock/`
  reaches the publication, the mutex name in both namespaces, a live holder
  until W, a holder that releases mid-wait, a holder change, child
  recording, release, a record replaced by hand, retention, an unheld or
  doubly acquired lock, an empty caller kind and the default seams with the
  local clock. Eleven unverifiable records are covered, along with recovery
  of a dead owner and dead children, a live or `UNKNOWN` child, an `UNKNOWN`
  owner and an abandoned mutex. The attempt cases run for both kinds and
  eight verdicts each: a file or unknown name ignored, an unreadable owner
  file, a non-holder and a refused removal. Since round 1 it also reaches the
  deadline at publication: a lock freed at exactly W is taken, a late wake-up
  finding the lock freed fails without publishing, and liveness queries
  running past W leave a dead record in place with no holder named; the last
  two failed on the reviewed module. Covered.
- **Files outside the gate**: `git_cliff_support.py` lives under `tests` and
  is not measured. Each of its top-level symbols is used by the Step 3 tests
  or inside the module (`synthetic_archive` by `synthetic_pin`,
  `_alive_current` and `_no_actions` as default factories, `_denied` by
  `deny_writes`).

No, there is no unit-tested class below 100% that needs completing for Step 3.
No, none of the top-level symbols of the files outside the gate is
unreferenced.

### Feature integrity for Step 3

- **Existing feature behavior**: no existing module changes behavior;
  `windows_process`, `lock_records`, `manifest` and `budget` are only
  imported, and the only edit to an existing source file is the package
  docstring.
- **Reporting or diagnostics**: `LockWaitError` and `LockRecordError` name the
  lock path, and the former the last live holder seen and the remedy;
  `UnusableEntry` reasons
  name the failing check. Nothing is printed: the waiting line itself is left
  to the caller's `on_wait`, which Step 5 formats.
- **Compatibility or rollout note**: the new ignore rule covers only
  `/.tools/git-cliff/` at the repository root; the existing generic patterns
  are unchanged. Nothing calls the cache or its lock before Step 5.

No, there is no existing feature or reporting capability that appears
impaired.

---

## Step 4. Network client, download worker, verification and extraction

### Analysis of Step 4 implementation state

Yes. Step 4 has been fully implemented.

`git_cliff/network.py` builds its opener from the standard proxies and the
default certificate context without touching verification. It streams an
archive with its SHA-256, reading at most one byte past the expected size,
reads release metadata within a limit, and classifies each failure as
retryable or fatal without reading any response header.
`git_cliff/download_worker.py` runs one archive attempt or metadata lookup,
started through the new internal `git-cliff-worker` entry kind of
`bootstrap.py`, and writes one JSON outcome line with its internal status 0,
75 or 65, which the bootstrap returns unchanged. `git_cliff/archive.py`
recomputes the staged digest and extracts only the manifest member as
`git-cliff.exe`. Before adding the Step 4 check, the native check recorder
was split, as the Step 2 validation planned: its check bodies and helper
parents moved to the new `git_cliff_native_probes.py`. The recorder then
recorded milestone `step-4`: the Step 2 set and a real worker, started
through the bootstrap and recorded in a disposable staging directory, ended
job-wide at its deadline while a local endpoint never answered; its validator
accepts the record for the current sources. The command printed by
`pw scope day` reports `exit=0`, and the three `rg` checks find no match.

### Goal for Step 4

Ship `git_cliff/network.py` (the opener from the standard proxy settings and
the default certificate context, size-capped streaming with SHA-256, the
metadata fetch and the retry classification), `git_cliff/download_worker.py`
(one attempt or one metadata lookup per run, started through the internal
`git-cliff-worker` entry kind of the bootstrap) and `git_cliff/archive.py`
(the digest check from the staged file and the single-member extraction).

### Step 4 improvement expectations

- Certificate verification is never turned off, and redirects to the asset
  host are followed.
- A body longer than the expected size stops at the first extra byte.
- Connection errors, resets, HTTP 429 and 5xx are retryable; other HTTP 4xx
  and a size overflow are fatal; `Retry-After` is ignored.
- The worker kind passes readiness and returns its status unchanged, while the
  release kinds keep `{0, 1, 2, 3}` and the cross-site status contract passes.
- Only the manifest member is extracted, as `git-cliff.exe`, with its size
  checked; traversal names in the archive create nothing.
- The native check record holds milestone `step-4`, with the stalled-endpoint
  worker termination `passed`.

### What was implemented for Step 4

The current diff delivers the Step 4 file list of the plan, a docstring
update in `tools/release_workflow/git_cliff/__init__.py`, and one file outside
that list, `tests/unit/tools/release_workflow/git_cliff_native_probes.py`,
from the recorder split described below.

- **Network client**: `build_opener(*, proxies=None, context=None)` passes
  `urllib.request.getproxies()` (or the declared proxies) to a
  `ProxyHandler` and `ssl.create_default_context()` (or the declared context)
  to an `HTTPSHandler`, unchanged, so certificate and host name verification
  stay on; the standard redirect handler follows GitHub's 302 to
  `release-assets.githubusercontent.com`. `stream_archive(opener, url,
  target, *, expected_size, socket_timeout) -> Received` opens the URL with
  the socket timeout, creates the target only once the response arrived,
  and reads chunks of at most `expected_size - size + 1` bytes. A chunk that
  would pass the expected size raises `SizeOverflowError` before it is
  written, so exactly one extra byte is read and none is written. A shorter
  body is returned with its size and SHA-256 for the parent's check.
  `fetch_metadata` reads the body whole within `METADATA_LIMIT` (4 MiB),
  beyond which it is a size overflow. `classify` returns `retryable` for HTTP
  429 and 500 to 599, for a URL error (connection refused, name resolution),
  a reset, a timeout, an `http.client` protocol error and a TLS error, and
  `fatal` for every other HTTP status, a certificate verification failure, a
  size overflow and any local error. No response header is read.
- **Download worker**: `WorkerRequest` (frozen, keyword-only: `mode`, `url`,
  `target`, `expected_size`, `remaining`) refuses an unknown mode, a URL
  other than HTTPS, a remaining time that is not finite and positive, an
  archive request without target and size or a metadata request with them,
  and a size below 1. `worker_arguments` and `parse_request` are inverse;
  `parse_request` refuses a missing value, an unknown or repeated option, a
  missing required option and a size that is not ASCII digits.
  `worker_command(runtime, tooling_root, request)` returns the runtime and
  `-I -X utf8 <tooling_root>\tools\release_workflow\bootstrap.py --entry-kind
  git-cliff-worker -- <arguments>`. `main(arguments, *, opener=None)` uses a
  socket timeout of `min(30, remaining)`, writes exactly one JSON line on
  standard output (`ok` with `size` and `sha256`, `ok` with `metadata`, or the
  failure class with its error) and nothing on standard error, and returns
  `STATUSES` 0, 75 or 65. Invalid arguments are a fatal outcome; any failure
  of the attempt is reported with its class, never raised.
- **Bootstrap entry kind**: `bootstrap.py` gains the module-level `_ENGINES`
  mapping (the three release kinds to `tools.release_workflow.cli`,
  `git-cliff-worker` to `tools.release_workflow.git_cliff.download_worker`)
  and `_UNNORMALIZED_KINDS`. `entry` accepts the kinds of `_ENGINES`, its
  message still naming only the public ones. After the unchanged readiness
  gate, `main` imports the module of the kind; for the worker it calls
  `main(arguments)` and returns that status unchanged, for the release kinds
  it keeps the single set literal `{0, 1, 2, 3}`, and `_normalized` diagnoses
  any other status as 1. The `Worker` protocol types the worker call.
- **Archive**: `verify_archive(path, pin)` hashes the staged file in 1 MiB
  chunks and raises `VerificationError` naming the size or the SHA-256 that
  differs. `extract_member(path, pin, target_dir)` opens the archive with
  `zipfile`, reads only `getinfo(pin.member)`, writes it exclusively as
  `git-cliff.exe`, and returns the SHA-256 and size of the written bytes. A
  missing member, a file that is not a readable ZIP archive, a failed CRC or
  a written size other than the directory entry raises `ExtractionError`. A
  pin is any value with `size`, `sha256` and `member` (the `ArchivePin`
  protocol), so the Step 6 candidates fit too.
- **Test support**: `git_cliff_support.py` gains `Canned` and `CannedWeb`:
  canned HTTPS answers by URL (status and body, redirect, stalled read or an
  exception), served by a real `urllib` opener through its redirect and error
  handlers with no socket and no certificate loading, recording each open
  with its timeout and each read size.
- **Recorder split and Step 4 check**: the recorder had reached 598 lines,
  in the 550 to 650 band, and the Step 2 validation recorded that Step 4 would
  split it before adding its check. Its kernel helpers, check bodies and
  helper parents moved unchanged to `git_cliff_native_probes.py`; the
  recorder keeps the catalog, the bounded runner, the record and the command
  line, and dispatches `--helper` to the probes module. Every check's sources
  now include the probes module. The new `worker-ends-at-deadline` check
  records the real worker in the owner file of a staging directory under a
  temporary tooling root. The worker is started through `worker_command` and
  the bootstrap, with `NO_PROXY=127.0.0.1` so that a declared proxy is
  bypassed. It connects to a loopback endpoint that accepts and never answers
  (the TLS handshake stalls), and is ended job-wide at its 10 s deadline. It
  wrote no outcome and is gone afterwards. Milestone `step-4` is the Step 2
  set plus this check.
- **Evidence validator**: `test_git_cliff_native_evidence_tdd.py` knows
  milestone `step-4`, the worker check with its sources (bootstrap, worker,
  network and cache modules beside the Step 2 ones), the probes module in
  every check's sources, and refuses a `step-4` record without the worker
  check. The committed record holds milestone `step-4`.
- **Validation evidence**:
  - Red first: `ghog single` on the four new test files and the bootstrap
    test failed at collection on the missing `network`, `download_worker` and
    `archive` modules (exit 4); the bootstrap test alone then failed its five
    worker-kind cases (exit 2).
  - Targeted: `ghog single` on the Step 4 test files, the bootstrap test,
    `test_codepage_tdd.py` and the evidence test, exit 0.
  - A by-hand run of the real worker through the bootstrap against a closed
    loopback port printed one `retryable` line and exited 75.
  - Native record: the recorder with `--milestone step-4`, after the last
    source change, passed 9 of 9 checks (0.50 s to 1.23 s, the worker check
    10.57 s for its 10 s deadline); the stalled runner timed out at its 3 s
    bound in 3.08 s with its helper tree ended.
  - Gate: `ghog day --whole-suite`, the command printed by `pw scope day` at
    the default level, exit 0 at 2026-11-18T22:45:10+01:00. Two earlier walks
    failed: the first at check (typing of the canned handler and of test
    helpers, a function with seven returns in `bootstrap.main`, a grade C
    argument parser now split), the second only on the record's digests,
    stale after those edits, before the rerun above.
  - `rg -n 'CERT_NONE|check_hostname|_create_unverified_context|Retry-After'
    tools/release_workflow/git_cliff`, `rg -n 'extractall|extract\('
    tools/release_workflow/git_cliff/archive.py` and `rg -n 'api.github.com'`
    on `network.py` and `download_worker.py`: no match.
- **Line counts**: `network.py` 120 (advisory 190), `download_worker.py` 155
  (advisory 150), `archive.py` 100 (advisory 80), `bootstrap.py` 227 (+26,
  advisory +25), `git_cliff/__init__.py` 33; `git_cliff_support.py` 401 (+74,
  advisory +60); new tests 175, 143, 121 and 55 (advisory 220, 170, 160 and
  50), initializers 3 each; `test_bootstrap_tdd.py` 261 (+49, advisory +35);
  `git_cliff_native_checks.py` 278 (598 before the split),
  `git_cliff_native_probes.py` 470 (new), `test_git_cliff_native_evidence_tdd.py`
  231 (+19, advisory +5), `native_checks.v1.json` 253. Every Python file stays
  below 550; the advisory overruns are variance.

### New types or classes introduced for Step 4

- `tools.release_workflow.git_cliff.network`: `SizeOverflowError`,
  `Received`, `build_opener`, `stream_archive`, `fetch_metadata`, `classify`
  and `METADATA_LIMIT`.
- `tools.release_workflow.git_cliff.download_worker`: `WorkerRequest`,
  `worker_arguments`, `parse_request`, `worker_command`, `main`, `STATUSES`,
  `SOCKET_SECONDS` and `ENTRY_KIND`.
- `tools.release_workflow.git_cliff.archive`: `VerificationError`,
  `ExtractionError`, the `ArchivePin` protocol, `verify_archive` and
  `extract_member`.
- `tools.release_workflow.bootstrap`: the `Worker` protocol, `_ENGINES`,
  `_UNNORMALIZED_KINDS` and `_normalized`.
- Test support: `Canned` and `CannedWeb` in `git_cliff_support.py`; in
  `git_cliff_native_probes.py`, the moved `Kernel32`, `KERNEL`, `Observed`,
  check functions and helper parents, plus `check_worker_deadline` with its
  silent loopback endpoint.

### Architecture check for Step 4

- **Network adapter**: `network.py` is the only module that touches
  `urllib`, `ssl` and `http.client`; it imports nothing else of the engine.
  The opener and the context are injectable, and tests reach it through a
  real opener over canned answers, never a monkeypatched transport.
- **Worker boundary**: `download_worker.py` depends only on `network`; its
  outcome line and internal statuses are a private contract with the Step 5
  parent, kept apart from the public engine statuses by the bootstrap's
  module-level tables, as plan decision Q15 requires. The worker is reached
  only through the bootstrap, after the same readiness gate as every engine
  entry.
- **Archive and cache**: `archive.py` depends on `cache.EXECUTABLE` for the
  fixed name and on the `ArchivePin` protocol, not on the manifest, and holds
  no network or process code.
- **Developer-run evidence**: the recorder and the probes module stay under
  `tests`, are never imported by a test, and depend on the engine, never the
  reverse.

No, there is nothing that needs to be addressed: no DDD-Hexagonal violation or
smell is visible in this step.

### Performance check for Step 4

- **Streaming and hashing**: linear in the archive's bytes, in 64 KiB reads,
  with at most one extra byte read; the staged digest and the extraction are
  linear in the archive and member bytes, in 1 MiB chunks.
- **Metadata**: one bounded read of at most 4 MiB plus one byte.
- **Worker and bootstrap**: one argument pass and one JSON line per attempt;
  the bootstrap's kind lookup is one dictionary access. No sort, no pairwise
  comparison and no directory scan.
- **Hot-path bound**: none of this runs during configuration loading or any
  existing command; the bootstrap's release kinds only gain a dictionary
  lookup.
- **Plan-bound alignment**: within "O(n) total per phase" for streaming,
  hashing and extraction.

No, there is no performance issue that needs to be addressed.

### Unit test coverage check for Step 4

The coverage gate measures `tools` only (`[tool.coverage.run] source`), with
`*/tests/*` and `*/__init__.py` omitted, at `fail_under = 100`. The Step 4
round 1 request records the writer's `ghog day --full=speed --whole-suite`
result: 7,719 passing tests, `cov=100 outliers=0 excluded=0 proof=speed`, for
index tree `ad2afb2d6d3ae846f798808026913665bfcc5307`. The independent reviewer
assessed the code and tests statically and found no coverage gap; no reviewer
test run or coverage measurement was performed. This measured result applies
to the configured production scope, not the helpers and recorder under `tests`.

- **`tools/release_workflow/git_cliff/network.py`**: `test_git_cliff_network/`
  reaches both opener branches, streaming with a full, longer, shorter and
  stalled body, a redirect, six HTTP error statuses, the metadata read within
  and beyond its limit, and every branch of `classify` (HTTP statuses, URL
  errors with a connection or a certificate cause, connection, protocol,
  timeout, TLS, size and local errors); covered.
- **`tools/release_workflow/git_cliff/download_worker.py`**:
  `test_git_cliff_download_worker/` reaches both argument round trips, the
  command, thirteen invalid argument vectors, an archive and a metadata
  attempt, four classified failures, the status table and the production
  opener; covered.
- **`tools/release_workflow/git_cliff/archive.py`**: `test_git_cliff_archive/`
  reaches a matching, truncated and altered archive, the extraction, hostile
  member names, a missing member, a file that is not a ZIP archive and both
  directions of a wrong directory size (a CRC failure and a short member);
  the property test checks generated member lists; covered.
- **`tools/release_workflow/bootstrap.py`**: `test_bootstrap/` adds the module
  of each kind, the worker status passed unchanged (0, 2, 65 and 75) and the
  release kinds turning 65 and 75 into 1, beside its existing cases; covered.
- **Files outside the gate**: `git_cliff_support.py`,
  `git_cliff_native_checks.py` and `git_cliff_native_probes.py` live under
  `tests` and are not measured. `Canned` and `CannedWeb` are used by the
  network and worker tests. Every top-level function and class of the probes
  module is reached from the recorder's catalog, its runner or helper
  dispatch, or inside the module (`_Place` and `_SilentEndpoint` by
  `check_worker_deadline`, `_FailingTerminate` by a helper parent), and the
  record proves the run.

No, there is no unit-tested class below 100% that needs completing for Step 4.
No, none of the top-level symbols of the files outside the gate is
unreferenced.

### Feature integrity for Step 4

- **Existing feature behavior**: the release entry kinds keep their gate,
  their dispatcher and their public statuses; `test_codepage_tdd.py` still
  finds one status set in `bootstrap.main`, equal to the launchers' and the
  renderer's. No other existing module changes behavior.
- **Reporting or diagnostics**: the worker's outcome line carries the error
  type and text for the Step 5 diagnostics; nothing is printed on a release
  command's output.
- **Compatibility or rollout note**: nothing starts the worker before Step 5.
  The recorder's command line is unchanged except for the new milestone, and
  its record is refreshed for the moved sources.

No, there is no existing feature or reporting capability that appears
impaired.

---

## Step 5. Provisioning service, invocation object and failure contract

### Analysis of Step 5 implementation state

Not started. Step 5 is not implemented because no implementation work has
begun: the primitives are not composed into the target flow, and no
invocation object, message, diagnostic or engine entry point exists.

### Goal for Step 5

Ship `git_cliff/messages.py` (stages, remedies, `ProvisioningError` with
status 2 and the three standard-error lines), `git_cliff/invocation.py`
(`GitCliffInvocation` with the engine and passthrough policies, owning the
contained creation and the guard transfer), `git_cliff/installation.py` (the
lock-held installation) and `git_cliff/provisioning.py` (the seams, the outer
flow and `configured_pin`).

### Step 5 improvement expectations

- A valid entry is reused silently, without lock or network, and with the
  reuse probe created holding the guard, also on a write-denying filesystem.
- Two first uses download once; the second caller waits, rechecks and
  reuses.
- A digest mismatch is never retried; a retryable failure retries once after
  5 s inside D; an invalid entry in use gives the in-use diagnostic and stays.
- Retirement leaves only the states the plan lists: a refused executable
  rename changes nothing, a refused directory rename or a parent death between
  the renames leaves the entry directory without its executable, and the next
  caller under the lock resumes at the directory rename; a failed publication
  after retirement leaves no entry, and the next caller provisions afresh.
- An unconfirmed child end keeps staging, the lock record
  (`retain_record()`) and the guard (retained by `check_entry` for a reuse
  probe, by the invocation for a git-cliff run); a later caller recovers them
  only once the owner and every recorded child are `DEAD`, and a pre-identity
  end records nothing for the never-run child.
- Every lifecycle boundary of the fake child launcher leaves the state the
  design's acceptance rows describe, and staging is removed only after every
  recorded child has exited.
- The budget override cases hold, including the refusal before any work with
  a valid entry and the default waiter failing at 360 s behind a 1800 s
  holder.
- The engine policy removes every `GIT_CLIFF_*` variable and closes stdin;
  the passthrough policy keeps the environment and streams; both pass the
  guard and close it only after the child exits.
- Provisioning never writes to standard output.
- The native check record holds milestone `step-5`: kill-on-close of a worker
  and of a git-cliff run, the inherited guard during a reuse probe and a
  killed stand-in caller, and the abandoned mutex of a live owner each
  `passed`, on a synthetic pin since no pin is admitted yet.

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

---

## Step 6. Compatibility evidence harness

### Analysis of Step 6 implementation state

Not started. Step 6 is not implemented because no implementation work has
begun: no candidate identity, trust record, fixture history, comparison or
bundle model exists, and `GitExecutionContext.run` takes no input.

### Goal for Step 6

Ship the internal comparison modules of the evidence harness:
`git_cliff/candidates.py` (identities acquired independently of the manifest,
trust records written once, candidate provisioning in the evidence
namespace), `git_cliff/fixture_history.py` (one `git fast-import` stream that
fixes every object-producing input), `git_cliff/comparison.py` (frozen inputs,
the temporary worktree, the ranges and the controlled runs),
`git_cliff/bundle.py` (the compact bundle, its completeness checks and the
binding of the user's review to the exact evidence) and `git_cliff/harness.py`
(the developer entry point, which also records the review), with the optional
`input` of `GitExecutionContext.run` and the harness test fakes in
`git_cliff_harness_fake.py`.

### Step 6 improvement expectations

- 2.14.2's identity comes from the release metadata; 2.7.0's comes from its
  first authorized download, bounded by the metadata's asset size, with the
  digest computed by the parent; the trust record is written once, only after
  extraction and probe succeed, and a later different archive fails without
  changing it; evidence-only trust is refused for any version other than
  2.7.0.
- The fixture stream is byte-identical across builds, and a regeneration that
  does not reproduce the recorded hashes fails.
- Both candidates receive the same worktree, ranges, `cliff.toml` bytes,
  flags and environment; identical outputs keep only digests and statuses.
- The bundle checks refuse an unclassified hunk, a defect, an audit without
  its revision or that does not exclude 69, and a missing input.
- `require_admissible` refuses an absent, rejected, malformed or stale review
  and any listed file whose SHA-256 differs; a rerun that changes covered
  content leaves the review stale, and a byte-identical projection keeps it.
- The harness never writes the manifest or reaches the production namespace.

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

---

## Step 7. Evidence run, user review and admission of 2.14.2

### Analysis of Step 7 implementation state

Not started. Step 7 is not implemented because no implementation work has
begun: no evidence bundle, trust record, recorded review or admitted pin
exists.

### Goal for Step 7

Run the harness by hand under the evidence-only exception for 2.7.0, record
the exit-path audit at `v2.14.2` with its written checklist and the
classification of every hunk, present the bundle for the user's review and
record the decision in its `review` member and in the step journal, then
admit 2.14.2 as the tested default by the reviewed manifest edit.

### Step 7 improvement expectations

- The manifest holds exactly 2.14.2, default, with the design's asset name,
  size, digest and member, and its evidence reference names the committed
  bundle, which passes `require_admissible` with an approved review covering
  its committed projection.
- `version = 2.7.0` stays a configuration error, and the 2.7.0 trust record
  never enters the manifest.
- The audit records its clone commands, the audited commit and the files and
  call sites read per exit-path category.
- The user's review is recorded in `bundle.json` and in the step journal
  before the admission commit.

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

---

## Step 8. The gcliff launcher, integrated acceptance, final native checks and documentation

### Analysis of Step 8 implementation state

Not started. Step 8 is not implemented because no implementation work has
begun: no `bin/gcliff.bat`, `gcliff-batch` entry kind, launcher module or
alias fragment exists, discovery cannot tell "no worktree here" (a plain
directory, a bare repository, a `.git` directory) from a genuine failure, and
no integrated acceptance test, final native record or reference page exists.

### Goal for Step 8

Ship `bin/gcliff.bat`, the `gcliff-batch` entry kind and
`git_cliff/launcher.py`, which select the pin from the worktree containing the
current directory, validate the whole `.release.ini`, provision, run git-cliff
through the passthrough policy and return its status unchanged, with status 69
for every failure before git-cliff starts; add the typed worktree-presence
observation and `paths.find_worktree`, used only by `gcliff`; ship the
single-line alias fragment `bin/gcliff.doskey` without editing `senv.doskey`;
add the integrated acceptance tests against the shipped manifest; rerun the
full native check set with the production launcher; and write the reference
documentation.

### Step 8 improvement expectations

- A nested folder of a pinned worktree selects that pin; a plain directory, a
  bare repository, a `.git` directory or a worktree without a pin gets the
  default after whole-file validation; a genuine discovery failure returns 69;
  `discover_project` keeps its behavior for every other caller.
- An invalid unrelated section, an unsafe batch argument, an invalid budget
  value, a readiness failure and a provisioning failure each return 69 and
  start no git-cliff child.
- git-cliff's arguments, output, status and environment pass through; a
  target argument never selects another repository's pin.
- `bin/gcliff.bat` keeps the release launchers' self-location, code page save,
  switch and restore, and runtime record blocks, uses 69 for pre-Python
  failures and normalizes no status; the code page is restored after a
  readiness error and after a normal child return.
- The console handler routine is registered only while the child runs and is
  removed after a normal return and after an error.
- `senv.doskey` has no `gcliff` line, and the cross-site status contract is
  unchanged.
- The native check record holds milestone `final`: every check of Steps 2, 4
  and 5 `passed` against the final sources, with the inherited-guard check
  after a killed launcher run through the production `bin\gcliff.bat`.
- Every row of the plan's acceptance ownership map names a passing test or a
  native check the validator accepts.
- `pw scope day --full=cov` reports `exit=0` with coverage 100.

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
