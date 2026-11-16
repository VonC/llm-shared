# v0.14.0 git-cliff-provisioning implementation tracking and validation

No, it is not implemented.

This document tracks the eight steps of the
[implementation plan](plan.v0.14.0.git-cliff-provisioning.md) for item 3 of
the sibling release tooling umbrella. No step has started: the pin manifest,
the contained Windows children with their native checks, the cache and its
lock, the download worker, the provisioning service, the evidence harness,
the reviewed admission of 2.14.2 and the `gcliff` launcher are all still to
be written.

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

Not started. Step 1 is not implemented because no implementation work has
begun: the common reader still reports `[git-cliff]` as an unknown section,
no manifest or budget module exists and the strict record helpers are still
private to `operation_lock.py`.

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

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 1

_(empty — no check has taken place yet.)_.

### Architecture check for Step 1

_(empty — no check has taken place yet.)_.

### Performance check for Step 1

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 1

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 1

_(empty — no check has taken place yet.)_.

---

## Step 2. Contained Windows children and the use guard

### Analysis of Step 2 implementation state

Not started. Step 2 is not implemented because no implementation work has
begun: the engine has no job object, no suspended creation with a job list and
a handle list, no deadline termination and no use guard.

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

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 2

_(empty — no check has taken place yet.)_.

### Architecture check for Step 2

_(empty — no check has taken place yet.)_.

### Performance check for Step 2

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 2

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 2

_(empty — no check has taken place yet.)_.

---

## Step 3. Cache layout, entry record, reuse check and the cache lock

### Analysis of Step 3 implementation state

Not started. Step 3 is not implemented because no implementation work has
begun: nothing computes the fixed cache path, records a published entry,
checks an entry before use or locks a version and platform, and the root
`.gitignore` has no `/.tools/git-cliff/` entry.

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

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 3

_(empty — no check has taken place yet.)_.

### Architecture check for Step 3

_(empty — no check has taken place yet.)_.

### Performance check for Step 3

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 3

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 3

_(empty — no check has taken place yet.)_.

---

## Step 4. Network client, download worker, verification and extraction

### Analysis of Step 4 implementation state

Not started. Step 4 is not implemented because no implementation work has
begun: no code downloads a release asset, no worker entry kind exists in the
bootstrap and nothing extracts a single member.

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

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 4

_(empty — no check has taken place yet.)_.

### Architecture check for Step 4

_(empty — no check has taken place yet.)_.

### Performance check for Step 4

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 4

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 4

_(empty — no check has taken place yet.)_.

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
