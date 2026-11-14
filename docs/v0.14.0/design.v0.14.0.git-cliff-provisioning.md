# Design v0.14.0: pinned git-cliff provisioning

Reference feature request:
[feature-request.v0.14.0.git-cliff-provisioning.md](feature-request.v0.14.0.git-cliff-provisioning.md).

## Context for the git-cliff provisioning design

Item 3 of the sibling release tooling umbrella makes the exact git-cliff
version a project expects available without any manual installation. Items 1
and 2 shipped the release engine, its common `.release.ini` reader, the
operation lock and the `version` and `versions` operations; none of them knows
git-cliff. Items 4 and 5 will render changelogs and run generated releases on
top of the provisioning this item supplies.

The requirement settles behavior through sixteen requirement clarifications
(Q01 to Q16): only tested pins are admitted, each executing checkout keeps its
own ignored cache, a cached binary passes a local integrity check before its
version check, waits and network stages are bounded, `gcliff` passes git-cliff
through from the current worktree's pin, and item 3 delivers raw-output
compatibility evidence with 2.7.0 run only under a user-authorized
evidence-only exception. This design chooses what the requirement leaves to
design: the digest source, the cache layout below the fixed path, the local
integrity record, the lock mechanism and its recovery test, the download
client, the extraction method, the time budgets, the message formats and the
exit-status numbers.

## Scope and ownership of the v0.14.0 git-cliff provisioning design

The v0.14.0 outcomes of item 3 are:

1. A tested-pin manifest in llm-shared names every admitted git-cliff version
   with the published identity of its Windows x64 asset, and a `[git-cliff]`
   domain of the common reader admits only those versions.
2. One provisioning service returns a verified absolute `git-cliff.exe` path
   for a pin, reusing a valid cache entry offline or downloading, verifying,
   extracting and publishing a new one under a bounded lock.
3. A `gcliff` launcher runs the provisioned git-cliff for the current
   worktree's pin and passes arguments, output and status through.
4. A compatibility evidence harness compares raw git-cliff output of 2.7.0 and
   2.14.2 on recorded frozen inputs and commits its evidence bundle.

Everything else is supporting design context for those outcomes or deferred.

### Delivered by item 3 in v0.14.0

- The tested-pin manifest, the `[git-cliff]` schema and the default rule.
- The cache layout, the local integrity record and the lock-free reuse check.
- The download worker with its enforced deadline, archive verification,
  single-member extraction, the version probe, non-replacing publication and
  the use guard that protects an entry from validation until git-cliff exits.
- The provisioning lock with bounded waiting and dead-owner recovery.
- Stage time budgets, standard-error messages, statuses and diagnostics.
- The provisioning entry point that items 4 and 5 call.
- `bin/gcliff.bat`, its entry kind and the `gcliff` macro line, without an
  edit of the shared `senv.doskey`.
- The root `.gitignore` entry for the cache.
- The evidence harness, the candidate lifecycle with the immutable 2.7.0
  trust record, the exit-status audit and the committed evidence bundle that
  admits 2.14.2.

### Left to later items or later versions

- When rendering needs git-cliff, the `cliff.toml`, header, ranges, notes, fix
  rules and archives of the new renderer, the rendering environment and the
  preflight ordering before automatic `fixes init` (item 4).
- Calling provisioning from generated release `pre` (item 5).
- Exposing the aliases in a consumer's setup and proposing a newer tested pin
  (item 6); adding `gcliff` to the shared `senv.doskey`, verifying that the
  cache stays ignored and the full pipeline parity rehearsals (item 8).
- Other operating systems and architectures, a mirror source, authenticated
  proxies, proxy auto-configuration scripts and automatic cache eviction
  (later versions, each a separate decision).

## Confirmed codebase and upstream facts for git-cliff provisioning

| Existing code or data | Observed behavior | Design implication |
| --- | --- | --- |
| `tools/release_workflow/schemas.py` | `SHIPPED_SCHEMAS = (TOOLING_SCHEMA, VERSION_SCHEMA)`. A `ValueRule` carries a trusted `parse` converter, a textual `default` and `required`; a domain may add a whole-configuration `validate`; the version domain imports its adapter package only when a version section exists | The git-cliff domain is one more shipped schema whose `version` rule parses and admits a pin against the manifest; nothing else is imported for a configuration without a `[git-cliff]` section |
| `tools/release_workflow/configuration.py` | Reads `.release.ini` once with interpolation off, rejects unknown sections and keys and validates every shipped domain for every command | Whole-file validation for `gcliff` (Q11) follows from using the same reader |
| `tools/release_workflow/cli.py` and `bootstrap.py` | `SHIPPED_HANDLERS` maps `version` and `versions`; `engine.main` receives `entry_kind`, `original_cwd`, `tooling_root` and the runtime identity; entry kinds are `explicit-batch`, `alias-batch` and `explicit-native` | The engine already knows the executing checkout (`tooling_root`); `gcliff` needs a fourth entry kind rather than a new runtime |
| `tools/release_workflow/invocation.py` | Batch entry kinds reject arguments containing `%`, `^`, `!` or `"`, which batch expansion would corrupt | The `gcliff` batch entry keeps the same guard and reports it as a launcher failure |
| `bin/release_workflow.bat` | Self-locates, reads `venvs/release-runtime.v1.txt`, runs `python -I -X utf8 bootstrap.py`, and maps every status outside 0 to 3 to 1 | `gcliff` needs its own launcher that returns git-cliff's status unchanged |
| `tools/release_workflow/results.py` | `render` writes data to stdout and diagnostics to stderr and normalizes any status outside 0 to 3 to 1; configuration and readiness failures use 2 | Engine operations report a provisioning failure as 2; the `gcliff` path bypasses this normalization |
| `tools/release_workflow/windows_process.py` and `operation_lock.py` | `ProcessIdentity` is a PID plus the kernel creation FILETIME; `process_state` returns `ALIVE`, `DEAD` or `UNKNOWN`, and only `DEAD` proves an owner gone; `transition_mutex` serializes record transitions with a kernel mutex that the kernel releases if its holder crashes; `OperationLock` publishes its owner record without replacement and recovers only a `DEAD` owner | The cache lock reuses these primitives; it adds a bounded wait, which the project operation lock does not have, and stays separate from the per-project lock |
| Windows kernel mutexes ([Mutex Objects](https://learn.microsoft.com/en-us/windows/win32/sync/mutex-objects)) | A mutex is owned by a thread; an abandoned mutex means its owning thread ended without releasing it, not that its process ended | Mutex acquisition, normal or abandoned, never authorizes recovery or cleanup; only a `DEAD` owner identity does |
| Windows file sharing ([CreateFileW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew)) | While a handle opened without `FILE_SHARE_DELETE` or `FILE_SHARE_WRITE` is open, another open requesting delete or write access fails with a sharing violation; renaming a file requires delete access | A read handle that denies write and delete sharing protects an executable from replacement for as long as it stays open |
| Windows process termination ([Terminating a Process](https://learn.microsoft.com/en-us/windows/win32/procthread/terminating-a-process)) | Terminating a process does not terminate its child processes, and a process's handles close when it ends | A worker or git-cliff child can outlive a dead parent, and a parent-held guard does not cover it; parent death alone proves nothing about a child |
| Windows job objects ([Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)) | With `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`, closing the last handle to a job terminates every process associated with it; nested jobs are supported | A parent that alone holds a non-inheritable job handle bounds the life of every child associated with the job, even if the parent dies; completion of that termination is still observed per child |
| Job assignment after creation ([AssignProcessToJobObject](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-assignprocesstojobobject)) | Associates an existing process with a job only when it is called | A child created first and assigned later is outside the job until that call; a parent that dies in between leaves it uncontained, suspended or not, for as long as it lives |
| Process attributes ([UpdateProcThreadAttribute](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute)) | `PROC_THREAD_ATTRIBUTE_JOB_LIST` lists job handles assigned to the child process, supported in Windows 10 and newer and Windows Server 2016 and newer; `PROC_THREAD_ATTRIBUTE_HANDLE_LIST` lists the only handles the child inherits, which must be inheritable, with `bInheritHandles` true | One `STARTUPINFOEX` carrying both attributes gives a child its job and its handles as part of its creation; the provisioning platform baseline is Windows 10 or Windows Server 2016, x64 |
| Nested jobs ([Nested Jobs](https://learn.microsoft.com/en-us/windows/win32/procthread/nested-jobs)) | A process already in a job joins another job only if a valid hierarchy forms and neither job sets UI limits; a child created by a process in a job belongs to every job of its parent's chain | A parent running inside a job, such as a terminal, an editor or a CI agent, nests the new job under it; a refused nesting is a creation failure, never a reason to create the child outside the job |
| CPython `subprocess.Popen` on Windows | `_execute_child` closes the new process's primary thread handle at once, and `STARTUPINFO.lpAttributeList` supports only `handle_list` | Creating a child suspended inside a job and resuming it after recording its identity needs the engine's Windows layer, not `subprocess` |
| Python `urllib.request.urlopen` ([documentation](https://docs.python.org/3/library/urllib.request.html#urllib.request.urlopen)) | Its `timeout` applies to blocking socket operations, not to a whole transfer, and name resolution is not covered by it | A wall-clock stage budget needs an actor that can be stopped and reaped; clock checks between blocking calls are not enough |
| `tools/release_workflow/git.py` | Owns the only Git subprocess boundary; tests replace it with programmatic observations | Running `git-cliff.exe` and downloading get their own injectable boundaries |
| `tools/pytest_plugins/llm_shared_process_audit.py`, `tests/memory_filesystem.py` | The suite fails any test that creates a process; scenario files can live in memory; each test lifecycle has a 0.1 s CPU budget | Unit tests drive provisioning through a fake download worker, a fake probe, a fake clock and in-memory or temporary files; no test downloads or runs git-cliff |
| llm-shared `pyproject.toml` | `requires-python = ">=3.13, <3.14"`; the release dependency group is empty | The design uses only the standard library: `urllib.request`, `ssl`, `hashlib`, `zipfile`, `json`, `ctypes` for the contained Windows child launcher, and `subprocess` only for its command-line quoting helper |
| `.gitignore`, `senv.doskey` | No `.tools/` entry; macros are `name="%LLM_SHARED_DIR%\bin\<launcher>.bat" $*` lines | Item 3 adds `/.tools/git-cliff/` to the root `.gitignore`; the `gcliff` macro follows the same line shape |
| GitHub release v2.14.2, checked 2026-11-13 | `git-cliff-2.14.2-x86_64-pc-windows-msvc.zip`, 7,428,304 bytes, published digest `sha256:6ece2112b3f4af462190ecbea4aeb1315fff6af415629b597f84319073c31131`, which the downloaded bytes match. The download URL answers 302 to `release-assets.githubusercontent.com`. The archive holds `git-cliff-2.14.2/git-cliff.exe` (15,245,824 bytes) beside `git-cliff-completions.exe`, `git-cliff-mangen.exe`, completions, a man page, licenses, `README.md` and `CHANGELOG.md` | Provisioning needs only the archive URL and a recorded digest; it extracts one named member |
| GitHub release v2.7.0, checked 2026-11-13 | No asset digest on any asset; `.sha512` sidecars exist for tarballs only | 2.7.0 can only be an evidence-only candidate (Q16) |
| This workstation's network | `HTTPS_PROXY` and `NO_PROXY` are set without credentials; the Windows proxy setting uses an auto-configuration URL. `urllib.request.getproxies()` returns the environment proxies, and `ssl.create_default_context()` loads 83 certificates from the Windows store. A standard-library `HEAD` request through that proxy follows the redirect and reports status 200 and length 7,428,304 | The standard library reaches the asset through the documented environment proxy and the operating system's certificates without a new dependency |

These facts describe current code and data, not changes already made for this
topic.

## Target flow of git-cliff provisioning

```txt
caller (item 4 renderer, item 5 pre, gcliff launcher)
  -> common reader: [git-cliff] version admitted by the manifest, or default
  -> resolve: <tooling_root>/.tools/git-cliff/<pin>/<triple>/git-cliff.exe
  -> open the use guard on git-cliff.exe (read; deny write and delete)
  -> reuse check through that handle, no lock, no write:
       entry record present, executable digest matches, probe reports pin
       (the probe is a contained, record-free child inheriting the guard)
       -> return the guarded entry (silent)
  -> otherwise close the guard and acquire the version/platform lock
     (bounded wait)
       -> recheck the entry under a new guard (another caller may have
          published it)
       -> recover records and staging directories whose owner and every
          recorded child are DEAD
       -> run the download worker as a contained, recorded child; terminate
          and reap it at the deadline
       -> verify size and SHA-256 against the manifest
       -> extract the single git-cliff.exe member
       -> probe --version in staging, write the entry record
       -> retire an invalid old entry: rename its executable first, which
          fails while any use guard is open, then move the directory aside
       -> publish staging by directory rename, release the lock
       -> open the use guard on the new entry, announce "ready" on stderr
  -> the caller starts git-cliff as a contained child that inherits the
     guard, so the guard lasts as long as the child, even if the caller dies
  -> any failure: diagnostic with pin, path and stage; no project mutation
```

Callers run this flow after configuration validation and before any project
mutation. A caller that never needs git-cliff never imports the provisioning
service.

## The tested-pin manifest and pin resolution

### Manifest content and admission

The manifest is a shipped, read-only Python table in the release engine. Each
admitted version records:

| Field | Meaning | Example for 2.14.2 |
| --- | --- | --- |
| `version` | Exact pin in `X.Y.Z` form | `2.14.2` |
| `default` | Whether this pin is the tested default; exactly one entry is | yes |
| `triple` | Supported platform, a Rust target name | `x86_64-pc-windows-msvc` |
| `asset` | Upstream archive file name | `git-cliff-2.14.2-x86_64-pc-windows-msvc.zip` |
| `size` | Archive size in bytes | `7428304` |
| `sha256` | Upstream published digest, copied when the pin was admitted | `6ece2112...c31131` |
| `member` | Archive member to extract | `git-cliff-2.14.2/git-cliff.exe` |
| `evidence` | Committed evidence bundle that admitted the pin | the item 3 bundle |

A version enters the manifest only with its evidence bundle (Q01). The digest
source is the asset digest GitHub publishes, copied into the manifest at
admission and checked again by the evidence harness. Provisioning at release
time therefore makes no call to the GitHub API: it needs neither
`api.github.com` nor the unauthenticated API quota of 60 requests per hour per
address, which a corporate proxy shares across its users. A release asset
replaced upstream after admission is detected as a digest mismatch rather than
silently accepted.

The manifest's download URL is derived, not stored:
`https://github.com/orhun/git-cliff/releases/download/v<version>/<asset>`,
which keeps the upstream tag spelling `vX.Y.Z` (decision 31).

### The git-cliff domain of the common reader

The shipped schemas gain a `git-cliff` domain with one fixed section,
`[git-cliff]`, and one key, `version`. Its `parse` converter accepts only
`X.Y.Z` (no `v`, no prerelease, no `latest`) and then admission: a well-formed
version absent from the manifest is a configuration error listing the tested
pins, for example
`.release.ini [git-cliff] version = 2.15.0: not a tested git-cliff pin; tested: 2.14.2`.
The rule's textual default is the manifest's default version, so an omitted
key yields a defaulted value with the same source information as any other
default (Q02). Like every domain, it is validated for every command, and the
reader's unknown-key rule keeps rejecting an executable key.

The converter imports only the manifest, a small table without network,
filesystem or process code, so an ordinary build or `version` command pays no
provisioning cost.

### Selecting the project and the pin

| Caller | Project used for the pin | Without a pin |
| --- | --- | --- |
| Engine operations (`changelog`, generated `pre`) | The validated project root of the operation | Manifest default |
| `gcliff` inside a Git worktree | The worktree containing the current directory, through the existing alias discovery | Manifest default, after whole-file validation |
| `gcliff` outside any worktree | None | Manifest default |

`gcliff` never reads its git-cliff arguments to choose a project (Q10). A
discovery failure other than "not inside a worktree" is a launcher failure,
not a silent fallback to the default.

## Cache layout and the local integrity record

### Layout below the fixed path

```text
<LLM_SHARED_DIR>/.tools/git-cliff/
  2.14.2/
    x86_64-pc-windows-msvc/          published entry, never modified in place
      git-cliff.exe
      entry.json                     local integrity record
    x86_64-pc-windows-msvc.lock      provisioning lock record, while held
    .staging-<pid>-<created>-<rand>/ one staging directory per attempt
    .retired-<pid>-<created>-<rand>/ an invalid entry moved aside
  evidence/
    2.7.0/x86_64-pc-windows-msvc/    evidence-only candidate (Q16)
```

`<LLM_SHARED_DIR>` is the executing checkout's `tooling_root`; there is no
cross-checkout or per-user location (Q04). Staging and retired directory names
carry the owner's PID and creation time, so recovery can test their owner. The
`evidence/` subtree is never a valid `X.Y.Z` directory name, and resolution
reads only `<pin>/<triple>/` for a manifest pin, so production provisioning
cannot reach an evidence candidate.

### Ignore rule

Item 3 adds `/.tools/git-cliff/` to llm-shared's tracked root `.gitignore` in
the same change that adds the downloader (Q05). Any checkout that contains the
provisioning code therefore contains the rule before its first cache write, in
every worktree. A unit test reads the root `.gitignore` and asserts the entry;
item 8 only verifies it in llm-shared's cutover.

### Entry record

`entry.json` is written in staging before publication and never edited
afterwards:

| Field | Purpose |
| --- | --- |
| `schema` | Record format version, `1` |
| `version`, `triple` | Must equal the directory names and the requested pin |
| `asset`, `asset_sha256` | The verified archive identity, for diagnostics |
| `executable_sha256`, `executable_size` | The local integrity data checked before every use |
| `provisioned` | Local time with offset, for diagnostics |

The record detects divergence from what was published, such as a truncated or
replaced executable. It does not defeat a coordinated replacement of both the
record and the binary (Q03); the cache is not a security boundary against a
local writer.

### Reuse check and the use guard

Every use of an entry holds a use guard from validation until the git-cliff
process it starts exits. The guard is a handle on `git-cliff.exe` opened for
reading with `FILE_SHARE_READ` only: other readers and the loader's own image
open stay compatible, while any open that requests write or delete access,
including the rename a replacement needs, fails with a sharing violation for
as long as the guard is open. Reuse runs in this order and stops at the first
failure (Q03):

1. Open the use guard; a missing executable makes the entry absent.
2. Read `entry.json`; it must parse and name the requested version and triple.
3. Hash `git-cliff.exe` through the guard handle; its size and SHA-256 must
   equal the record.
4. Run the version probe; it must report the pin. The probe is a record-free
   child under the child lifecycle below: it receives the guard in its
   inherited-handle list and writes no lock record or owner file.

A missing or mismatching record makes the entry invalid before it runs. The
guard is held from step 1, so no replacement can slip between validation and
the start of the caller's git-cliff process. Every execution of the cached
executable, the reuse probe as well as the caller's git-cliff run, starts
under the child lifecycle below with the guard in its explicit
inherited-handle list: the child holds its own copy from creation, so the
protection lasts for that child's actual lifetime even if the caller dies,
and the caller's kill-on-close job, which the child belongs to from creation,
bounds that orphan. If the caller dies before the child exists, its guard
closes with it and there is no child to protect. Reuse, its probe included,
takes no lock and writes nothing, and a read handle needs no write access, so
a read-only checkout with a valid entry renders normally; only provisioning
needs write access (Q04).
Hashing a 15 MB executable costs a few milliseconds compared with rendering a
changelog.

## Download, verification and extraction

### Network path

The download worker uses `urllib.request` with an opener built from
`urllib.request.getproxies()` and `ssl.create_default_context()`:

- Proxies come from `HTTPS_PROXY`, `HTTP_PROXY` and `NO_PROXY`, or from the
  static Windows proxy setting when no environment proxy exists. These are the
  documented standard proxy configuration (Q07).
- Certificates come from the Windows certificate store through the default
  context, so a corporate inspecting root that Windows trusts is accepted.
  Verification is never disabled, and no setting turns it off.
- Redirects from `github.com` to `release-assets.githubusercontent.com` are
  followed; both hosts must be reachable through the proxy.
- Not supported in v0.14.0: proxies that require authentication, proxy
  auto-configuration scripts, and a mirror source. Each fails with the network
  diagnostic, which names the two hosts and the proxy variables.

### Archive verification

The archive streams into a file in the attempt's staging directory while its
SHA-256 is computed. Provisioning checks the received size against the
manifest during the stream, stopping at the first byte beyond it, and checks
the digest at the end. A mismatch deletes the staging directory and reports a
verification failure; it is never retried, because a repeated download from
the same source would not change a wrong asset.

### Single-member extraction

Only the manifest's `member` is read, with `zipfile`, and written under the
fixed name `git-cliff.exe` in staging. Its uncompressed size must match the
archive directory entry, and the written bytes are hashed for the entry record.
No other member, such as `git-cliff-mangen.exe` or `git-cliff-completions.exe`,
is extracted, and no member path from the archive becomes a filesystem path,
so traversal entries cannot write outside staging.

### Version probe

The probe runs `git-cliff.exe --version` with standard input closed, output
captured, the entry or staging directory as working directory and an
environment from which every `GIT_CLIFF_*` variable is removed, so ambient
git-cliff settings cannot affect the check. The first output line must be
`git-cliff <pin>`. The probe has its own time budget; on expiry the process is
terminated and the probe fails. The same probe serves the reuse check and the
staging check, in two roles of the child lifecycle: the reuse probe is
record-free and inherits the entry's use guard, while the staging probe
belongs to the writable attempt and is recorded before it resumes.

### Publication

Under the lock, publication renames the staging directory to `<triple>/`. A
directory rename on the same volume either completes or leaves the old state,
and Windows does not replace an existing target, so two publishers can never
merge files. When an existing entry was found invalid, the holder first
renames its `git-cliff.exe` inside the entry to a `.retired-...` name. That
rename needs delete access, so it fails while any caller holds a use guard on
the file; provisioning then reports the in-use diagnostic instead of replacing
a binary another release is validating or running (Q14). Only after that
rename succeeds is the entry directory moved to a `.retired-...` directory and
staging published. A reader arriving after the rename finds no executable,
treats the entry as absent and waits for the lock. Nothing ever evicts a valid
complete entry. A developer-run acceptance check outside pytest confirms the
refusal on Windows, both with a guard held by a running child and with a guard
held between validation and child start.

## Provisioning lock, contention and recovery

### Lock record and transition mutex

Each version and platform has one lock record,
`<version>/<triple>.lock`, holding the owner's PID, creation time, start time
and caller kind. All reads, publications and removals of that record happen
inside a kernel transition mutex named from the cache directory's file identity
and the version and triple, like `OperationLock` does for a project. The
record is published without replacement, so two callers cannot both believe
they hold it. The cache lock is separate from the per-project operation lock;
a release holds its project lock while it waits for or holds a cache lock.

The transition mutex only serializes brief record changes. A mutex is owned by
a thread, so its abandonment proves only that a thread ended; neither a normal
nor an abandoned acquisition ever authorizes removing a record or a directory.
Only a `DEAD` owner identity does.

The supported topology is a cache on a local disk of the machine that runs the
release. The transition mutex lives in the `Global\` namespace, shared by every
session on that machine, and the PID probe sees only local processes. A cache
on a network share used from several machines is not supported: neither the
mutex nor the probe coordinates across machines, and the design makes no claim
for that case.

### Bounded wait with a message

A caller that finds a live owner prints one waiting line on standard error and
polls the record every 250 ms until the lock frees or the wait budget expires.
On expiry it fails with the lock path, the owner's PID and start time, and the
remedy. When the lock frees, the caller rechecks the entry first: in the common
case of two simultaneous first uses, the second caller reuses what the first
published and downloads nothing (Q06).

### Recovery of a dead holder and its partial state

A lock is removed inside the mutex, and the caller proceeds, only when its
owner and every child recorded in it are `DEAD`. An owner or child reported
`ALIVE` or `UNKNOWN` is never recovered, however old the record, even when the
owner's thread abandoned the transition mutex (Q06). While holding the lock, a
caller removes a `.staging-` or `.retired-` directory of that version only when
its owner, read from the PID and creation time in the directory name, and
every child listed in the directory's owner file are `DEAD`. A child whose
kill-on-close termination is still pending reports `ALIVE`, so its directory
waits for a later provisioning; a live caller's temporary installation
survives.

### Child process lifecycle

Every child process the engine starts for git-cliff provisioning, evidence or
rendering follows one protocol through the engine's Windows layer. The
children fall into two classes, which differ only in what is recorded:

| Class | Children | Records before resume |
| --- | --- | --- |
| Cache-writing | The download worker of a provisioning or candidate attempt, and the staging probe of that attempt | PID and creation time in the attempt's lock record, under the transition mutex, and in its staging directory's owner file |
| Record-free | The valid-entry reuse probe of an entry or a candidate, the harness metadata worker, and every git-cliff run (`gcliff`, item 4 rendering, harness comparison) | None: such a child needs no attempt record and writes no cache state |

A cache-writing child belongs to an attempt that already holds the lock and
owns staging. A record-free child needs no attempt record and makes no cache
writes; it may also be used by the entry recheck after a provisioning caller
acquires the lock. The reuse probe is the probe of the reuse check, which is
lock-free and read-only on its own; the metadata worker returns the release
metadata on its standard output and writes no file; and a git-cliff run writes
only what its caller directs, never into the cache. Every child that executes
a cached entry's executable, the reuse probe and every git-cliff run, inherits
that entry's use guard.

1. The parent creates one job object per attempt or run, with
   `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`, through a non-inheritable handle it
   alone holds. A failure to create or configure the job fails the stage before
   any child exists.
2. It creates the child with `CreateProcessW`, `CREATE_SUSPENDED` and
   `EXTENDED_STARTUPINFO_PRESENT`, through a `STARTUPINFOEX` whose attribute
   list carries two attributes. `PROC_THREAD_ATTRIBUTE_JOB_LIST` names that
   job, so Windows associates the child with it as part of its creation.
   `PROC_THREAD_ATTRIBUTE_HANDLE_LIST` names the only inherited handles: the
   standard handles and, for a child that executes a cached entry, that
   entry's use guard. The listed handles are made inheritable only for this
   creation call.
3. If the attribute list, the job association or the creation fails, for
   example because Windows refuses to nest the job under a job of the parent's
   chain that sets UI limits, `CreateProcessW` returns no child and the stage
   fails with a containment diagnostic. There is no fallback to creating the
   child first and assigning it to a job afterwards, and no fallback to
   `subprocess`.
4. For a cache-writing child, it records the child's PID and creation time in
   the lock record, under the transition mutex, and in the staging directory's
   owner file. A failure terminates the suspended child, waits for its exit and
   fails the stage. A record-free child skips this step.
5. It resumes the child, waits for it within the stage deadline, and on expiry
   terminates it and waits for its exit.

The supported baseline is Windows 10 or Windows Server 2016, x64, the first
releases that document `PROC_THREAD_ATTRIBUTE_JOB_LIST`. The platform check
rejects an older Windows before any download or child, and an attribute
Windows rejects at run time is a stage failure under step 3, never a reason to
start a child outside a job.

Because job membership is part of the creation call, no child ever exists
outside its job. If the parent dies before `CreateProcessW` completes, either
no child exists or the child is already a member; when the parent dies, its
job handle closes and Windows terminates every member, suspended or running.
A cache-writing child that was not yet recorded is still suspended, so it
never ran and wrote nothing; its staging directory holds nothing of it and is
recoverable once the parent is `DEAD`. A recorded child that is terminating
stays `ALIVE` until it has ended, and recovery waits for it. A record-free
child holds no lock and leaves nothing to recover, while its inherited guard
keeps the entry it executes from being renamed until the child has actually
ended. Neither a `DEAD` parent nor an abandoned mutex ever stands in for a
child's own `DEAD` state. An interrupted download thus leaves at most a
staging directory that the next provisioning of that version cleans (Q14).

## Time budgets and retries

| Stage | Budget | Retries |
| --- | --- | --- |
| Socket connect or inactivity, per network operation | 30 s | Counted in the download budget |
| Archive download, both attempts together | 300 s | One retry after 5 s for a connection error, a reset, or HTTP 429 or 5xx; none for another HTTP 4xx, a size overflow or a digest mismatch |
| Version probe | 15 s | None |
| Candidate metadata lookup, harness only, both attempts together | 60 s | One retry after 5 s under the same rules as the download, inside this budget |
| Waiting for another holder's lock | 360 s | Not applicable |

The 360 s wait is a finite contention policy. It covers a holder's download
budget, two probe budgets and about 30 s for extraction, hashing, cleanup and
publication, so a healthy holder normally finishes first; a waiter still fails
when the holder takes longer, and succeeds only when the holder completes
within that budget (Q15). An expired budget reports the stage, deletes the
attempt's staging directory and releases the lock; the project is unchanged.
The budgets are constants of the engine, not configuration; requirement Q07
excludes a mirror setting, not a budget override, and Q05 and Q18 decide the
one override. The rendering by git-cliff itself has no budget here;
item 4 owns it.

### Deadline enforcement

A `urllib` timeout bounds each blocking socket operation, not a whole
transfer, and does not cover name resolution, so a clock check between calls
cannot stop a call that never returns. Each download attempt therefore runs in
a worker process of the same runtime, started under the child lifecycle with
the URL, the attempt's staging file, the expected size and the remaining stage
budget. The parent waits for the worker until the stage deadline; on expiry it
terminates the worker and waits for its exit before it deletes staging or
releases the lock, so no orphaned actor can still write into a removed
directory. If the parent itself dies, the kill-on-close job ends the worker,
and the worker's recorded identity keeps its staging directory until it is
`DEAD`. The retry delay and the second attempt draw on the same deadline, and
a `Retry-After` header never extends it. The harness's candidate metadata
lookup uses the same worker code with its own 60 s budget, as a record-free
child that returns the metadata on its standard output and writes nothing; if
the harness dies, the job ends it and nothing is left to recover.

The version probe follows the same rule: on expiry the probe process is
terminated and reaped before the stage reports its failure. Unit tests replace
the Windows layer, the worker and the probe with fakes; developer-run
acceptance checks outside pytest exercise real termination against a local
endpoint that accepts a connection and never answers, and real kill-on-close
termination after the parent is killed, including while the child is still
suspended.

## Messages, statuses and the failure contract

### Standard-error messages

| Event | Message |
| --- | --- |
| Download starts | `git-cliff 2.14.2: downloading git-cliff-2.14.2-x86_64-pc-windows-msvc.zip (7.1 MiB) from GitHub` |
| Entry published | `git-cliff 2.14.2: ready at <path>` |
| Waiting for a holder | `git-cliff 2.14.2: waiting for provisioning by process 4812 since 14:02:31+01:00 (up to 360 s)` |
| Valid entry reused | nothing |

Provisioning never writes to standard output, so captured git-cliff output
stays exactly git-cliff's (Q08).

### Failure diagnostics

Every failure names the pin, the internal path, the failed stage and a remedy,
for example:

```text
git-cliff 2.14.2 unavailable at C:\...\llm-shared\.tools\git-cliff\2.14.2\x86_64-pc-windows-msvc:
download failed after 2 attempts (connection timed out). Check access to
github.com and release-assets.githubusercontent.com through HTTPS_PROXY.
```

| Stage | Remedy given |
| --- | --- |
| Platform | Windows 10 or Windows Server 2016 and later, x64 only, in v0.14.0 |
| Containment | Windows refused to create the child inside its job, for example under a host job that sets UI limits; run from a console outside such a job |
| Permission | Grant write access to the named directory of this llm-shared checkout |
| Lock wait | Another process holds the named lock; retry when it ends |
| Download | Check access to both hosts through the proxy variables |
| Verification | The asset does not match llm-shared's recorded digest; retry, and report a persistent mismatch |
| Extraction or probe | Delete the named staging or entry directory, then retry |
| In use | Another release runs the binary being replaced; retry when it ends |

No remedy asks the user to install git-cliff or change PATH.

### Statuses

| Path | Status on provisioning failure | Other statuses |
| --- | --- | --- |
| Engine operations | 2, the existing setup and configuration class | Unchanged |
| `gcliff` | 69, reserved for any failure before git-cliff starts: readiness, platform, configuration, argument guard, provisioning or child containment | git-cliff's own status, unchanged |

69 is the conventional "service unavailable" value. It is a proposal that
holds only with admission evidence (Q08). For each admitted version, the
evidence bundle records an audit of git-cliff's exit paths at that version's
source tag: its error return, argument-parsing errors, propagated helper
statuses, panics and abnormal termination, with the audited revision. Observed
statuses for success, a usage error, a failing render and any panic path that
can be reached corroborate the audit; the observations alone do not prove the
exclusion. If a version can return 69, admission stops and the conflict goes
back to the user rather than weakening the requirement.

## The provisioning entry point for items 4 and 5

The service is one call that takes the tooling root, the resolved pin and the
injectable seams, and returns the verified executable path, its version and
the open use guard, or raises a provisioning error carrying the stage, the
path and the diagnostic. The caller starts git-cliff under the child lifecycle
with the guard in the child's inherited-handle list and closes its own copy
only after the child has exited, or at once when the start fails, since no
child then exists.
Callers invoke it after configuration validation and before their first
project write; the returned path is the launcher-local `GIT_CLIFF` value of
umbrella decision 20, never exported to a parent process. The service creates
no project file, takes no project lock and reads no project state beyond the
pin it receives.

Its seams are the download worker launcher, an executable probe, a clock with
a sleep function, the process-state probe and the use-guard opener. Production
supplies the download worker, contained Windows child launcher, process-state
probe and use-guard implementation; tests supply fakes.

## The gcliff launcher

### Launcher and entry kind

`bin/gcliff.bat` self-locates like `bin/release_workflow.bat`, reads the same
runtime record and runs the bootstrap with a new `gcliff-batch` entry kind.
Unlike the release launcher, it returns any status unchanged, because a
git-cliff status is not a release status. A missing or invalid runtime record
returns 69 with the existing "run this checkout's setup" message.

### Running git-cliff

After selecting the project and pin and provisioning the binary, the engine
starts `git-cliff.exe` under the child lifecycle with the user's arguments,
inherited standard input, output and error, the use guard, the user's working
directory and the user's environment. While it waits, the launcher ignores the
console's Ctrl+C so that git-cliff, which receives the same event, decides how
to stop, and the launcher then returns git-cliff's status. If the launcher
itself dies, its kill-on-close job ends the git-cliff run.
Arguments are rebuilt with the standard Windows command-line rules that
git-cliff also uses to parse them. The batch entry keeps the guard that rejects
`%`, `^`, `!` and `"` in arguments; such values belong in `cliff.toml`. The
launcher holds the entry's use guard until git-cliff exits and returns its
status unchanged. The parent console's environment and PATH are never changed
(Q10).

### Alias definition

Item 3 ships the macro line
`gcliff="%LLM_SHARED_DIR%\bin\gcliff.bat" $*` as a single-line alias fragment
beside the launcher, loaded in tests with the same parsing as `senv.doskey`. It
does not edit the shared `senv.doskey`; item 8 copies the line there, and item
6 brings it to consumers that do not load that file (Q12). Until then,
`bin\gcliff.bat` works directly, including as the warm-up
`bin\gcliff.bat --version` (Q09).

## Compatibility evidence harness and bundle

### The harness

The harness is a developer-run command of the release engine, outside pytest,
because it downloads and runs binaries and runs Git. It uses the same download
worker, extraction, probe and use guard as provisioning, through candidate
records instead of the manifest. Its result is a committed evidence bundle;
unit tests and item 4 read the bundle without running git-cliff.

### Candidate lifecycle and admission order

A candidate becomes a pin in four ordered steps; nothing is admitted
provisionally:

1. Acquire the candidate's identity independently of the manifest. For 2.14.2,
   the harness reads the asset name, size and published digest from the GitHub
   release metadata, through the record-free metadata worker. For 2.7.0, the
   first authorized download over certificate-verified HTTPS records the asset
   name, size and SHA-256.
2. Download and verify the asset against that identity, then extract and
   probe it in the candidate cache.
3. Run the comparison and classify every difference in the bundle.
4. Admit the pin by a reviewed manifest edit that copies the same identity and
   digest with the bundle reference. The harness never writes the manifest,
   so this route cannot admit a production pin by itself.

| Candidate | Trust | Where it is extracted |
| --- | --- | --- |
| 2.14.2 | Upstream published digest from the release metadata | `.tools/git-cliff/evidence/2.14.2/<triple>/` |
| 2.7.0 | Evidence-only exception authorized by the user on 2026-11-13; the recorded digest identifies the bytes but does not authenticate the first download | `.tools/git-cliff/evidence/2.7.0/<triple>/` |

Each candidate has a trust record committed with the evidence bundle. It is
written once, at the candidate's first acquisition, and never rewritten: a
later run compares the downloaded archive with it and fails on a difference
instead of recording the new bytes. The 2.7.0 record never enters the manifest,
so `.release.ini` can never admit it and production provisioning keeps failing
for any version without upstream integrity data (Q16). No further authorization
is asked for a repetition. The harness reads release metadata only for
candidates, never during a release.

### Candidate cache

The `evidence/` subtree uses the provisioning primitives parameterized by a
candidate namespace: its own lock names, staging directories, atomic
publication, entry record, use guard and reuse check. Before a cached candidate
runs, the reuse check compares its entry record with the candidate trust
record's archive digest, then the executable digest with the entry record,
then the version probe, in the production order. A recorded executable hash in
a new report is not a reuse check by itself. The production resolver reads
only `<pin>/<triple>/` for a manifest pin and cannot reach this namespace.

### Frozen inputs and the coverage matrix

The bundle records every input so anyone can repeat the run, and both
versions receive identical inputs:

- llm-shared's commit, frozen by its full hash; the comparison runs in a
  temporary worktree checked out at that commit, the same working directory for
  both versions;
- each range: the full history, every consecutive `vA..vB` release range and
  `<last tag>..HEAD`;
- the exact `cliff.toml` bytes, copied into the bundle with their source path
  and dev_workflow submodule commit, so the input survives dev_workflow's
  removal;
- the flags `-c <bundle copy of cliff.toml> -w <worktree> -s footer`, the form
  `update-changelog.sh` uses;
- one explicit environment for both versions: `SystemRoot`, `TEMP` and `TMP`,
  and `HOME` and `USERPROFILE` pointing at an empty directory so no global Git
  configuration applies, with no `GIT_CLIFF_*` or other `GIT_*` variable;
- each candidate's asset identity and executable SHA-256.

The matrix covers commit parsers and skip rules, snapshot-tag history and
archive ranges (Q13). llm-shared has no snapshot tag, so the harness builds a
fixture history from a committed script with stable and `-SNAPSHOT` tags. The
script fixes every object-producing input: each tree's file names and bytes,
parent order, commit messages, author and committer names, emails and dates
with time zones, annotated tag names, tagger identities, dates and messages,
the SHA-1 object format, and Git configuration given on the command line with
no global or system configuration, no hooks, no signing and no line-ending
conversion. The bundle records the resulting commit and tag object hashes, and
a regeneration that does not reproduce them fails the run. Any matrix case
llm-shared's history lacks gets the same treatment.

### Outputs and classification

For each range and candidate, the bundle stores the raw output and the exit
status, then a difference listing and a classification table in which every
difference is marked intentional, with its upstream release-note reason, or a
defect. It also records the exit-path audit and the corroborating observed
statuses described under the statuses section. Admission of 2.14.2 into the
manifest requires a complete classification without an open defect and an
audit that excludes 69. The bundle covers raw git-cliff output
only; the postprocessing of `update-changelog.sh` is item 4's recheck and item
8's parity.

## Testing approach under the process-free policy

- Provisioning tests drive the service through the worker, probe, clock,
  process-state and use-guard seams, with cache files in the in-memory
  scenario filesystem or a temporary directory, so no test creates a process
  or opens a socket.
- Fake workers and probes that never finish check that the parent terminates
  and reaps them before it removes staging or releases the lock.
- A fake Windows layer models creation as one step that yields either no
  child or a child already in its job, and simulates parent death at each
  lifecycle boundary (during creation, after creation before recording, during
  a write, during a staging probe, during a reuse probe, between validation and
  child start, and while a git-cliff run executes), pending kill-on-close
  termination, `ALIVE` and `UNKNOWN` children, job creation, attribute,
  nesting and recording failures, and a Windows release below the baseline, so
  containment, recovery and guard behavior are checked without a process.
- A read-only reuse of a valid entry, run against a scenario filesystem that
  rejects every write, asserts that the reuse probe is created with the guard
  in its handle list and that no lock record, staging directory or owner file
  is written.
- Contention, dead-owner recovery and expiry are simulated with the fake clock
  and process states, not real waits, keeping each lifecycle under its CPU
  budget.
- The network client is tested against a fake opener that returns canned
  bytes, redirects, stalls and HTTP errors.
- The launcher's batch file is covered by the existing launcher acceptance
  style, which simulates the process boundary.
- The evidence harness itself runs only by hand; tests check the committed
  bundle's structure and that the manifest's admitted pins reference it.
- Developer-run acceptance checks, outside pytest, exercise what fakes cannot:
  real worker termination against a stalled local endpoint; a child created
  through the job list reporting membership with `IsProcessInJob` before it
  resumes, and ending when its parent is killed while the child is still
  suspended; a creation refused, with no child process left, when the parent
  runs inside a job that sets UI limits; real kill-on-close termination of a
  worker and of a git-cliff child after the parent is killed; the inherited use
  guard refusing an executable rename while a child runs, including after its
  launcher was killed, while a reuse probe runs after its caller was killed,
  and while a guard is held between validation and child start; and the
  abandoned transition mutex of a live process leaving its lock record in
  place. Each check bounds its own run with a timeout and ends every process
  it started. The design specifies the evidence these checks must produce;
  none has run yet.

## Foundation changes required by git-cliff provisioning

- The schema registry ships the git-cliff domain; the registry's completeness
  check already requires the shipped tuple to grow with it.
- Bootstrap and invocation accept the `gcliff-batch` entry kind, which selects
  the launcher path instead of the command dispatcher and skips status
  normalization.
- The Windows process and transition-mutex primitives are reused as they are;
  the lock-record helpers may move to a shared place when the plan finds the
  duplication worth removing.
- The Windows layer gains the use guard, a `CreateFileW` read handle with
  `FILE_SHARE_READ` only, and child creation through `CreateProcessW`:
  suspended, with a `STARTUPINFOEX` attribute list that carries
  `PROC_THREAD_ATTRIBUTE_JOB_LIST`, for membership from creation in a
  kill-on-close job held only by the parent, and
  `PROC_THREAD_ATTRIBUTE_HANDLE_LIST`, then resumed after any required
  recording, with terminate and wait for expiry and failure paths. It has no
  create-then-assign path.
- The platform check requires Windows 10 or Windows Server 2016 and later, x64.
- The engine gains a worker entry point that the bootstrap can start with the
  same runtime for a download attempt.

## Acceptance cases for the git-cliff provisioning design

| Scenario | Expected outcome | Reason |
| --- | --- | --- |
| `.release.ini` without `[git-cliff]`, valid cached 2.14.2 | Path returned, nothing printed, no lock, no network | Default pin and lock-free reuse |
| `version = 2.15.0` | Configuration error listing `2.14.2`, before any other work | Only tested pins (Q01) |
| `version = v2.14.2` or `latest` | Configuration error on the form | Notation and no floating pin |
| Cached executable truncated | Entry invalid without running it; provisioned again online, or a diagnostic offline | Integrity before probe (Q03) |
| `entry.json` missing | Entry invalid; provisioned again | Missing record invalidates |
| Two first uses together | One download; the second prints the waiting line and reuses the entry | Bounded wait and recheck (Q06) |
| Lock left by a crashed process | Recovered after `DEAD`; its staging directory removed | Owner-aware recovery (Q06, Q14) |
| Lock owner `UNKNOWN` for longer than the wait budget | Lock-wait failure naming the owner; nothing removed | Age never proves death |
| Download stalls in name resolution or trickles slowly | Worker terminated at the deadline and reaped before staging removal and lock release | Enforced stage budgets (Q15) |
| Version probe never exits | Probe terminated at 15 s and reaped; probe stage reported | Probe budget (Q15) |
| Transition mutex abandoned by a thread whose process is still `ALIVE` | Lock record kept; the waiter fails at its budget | Mutex ownership is per thread (Q06) |
| Staging directory of an `ALIVE` or `UNKNOWN` owner | Preserved | Owner-aware cleanup (Q14) |
| Parent dies during the creation of any child | Either no child exists, or the child is already a member of the job, which the parent's death closes and which ends it | No child ever exists outside its job (Q17) |
| Parent dies after creating a suspended worker, before recording it | The worker, a job member since creation, ends with the job without ever running; staging, with nothing written, is recoverable once the parent is `DEAD` | No unrecorded child ever runs |
| Parent dies while its recorded worker writes | Kill-on-close ends the worker; staging kept while the worker reports `ALIVE`, removed once it is `DEAD` | Every writer `DEAD` before cleanup |
| Parent dies during a staging probe | Same as a writing worker, with the probe's recorded identity | Probe children are recorded too |
| Child `ALIVE` or `UNKNOWN` after its parent is `DEAD` | Lock and staging preserved; a waiter fails at its budget | Parent death proves nothing about children |
| Job creation, attribute list or creation-time job association fails, including a nesting refused under a host job with UI limits | `CreateProcessW` returns no child; containment diagnostic; nothing written; no create-then-assign or `subprocess` fallback | Fail closed on containment |
| Windows older than Windows 10 or Windows Server 2016 | Platform diagnostic before any download or child | Supported baseline of the job list |
| Identity recording fails for a suspended cache-writing child | Child terminated and reaped; stage fails; nothing written | Recording before any work |
| Valid-entry reuse, writable or read-only checkout | The reuse probe is created in its job with the entry's guard in its handle list; no lock, lock record, staging directory or owner file is written | Record-free reuse probe |
| Caller dies while its reuse probe runs | The probe keeps its inherited guard, so an executable rename is refused until the job's termination has ended it; nothing to recover | Guard covers every execution of a cached binary |
| Harness dies while its metadata worker runs | The job ends the worker; it wrote nothing, so nothing is recovered | Record-free metadata worker |
| Launcher dies while its git-cliff child runs | Child keeps its inherited guard, so an executable rename is refused until the job ends the child | Guard covers the child's actual lifetime |
| Launcher dies between validation and child start | Its guard closes; no child exists, so nothing needs protection | No orphan to protect |
| Archive digest differs | Verification failure, no retry, staging removed | Manifest digest |
| Checkout not writable, entry absent | Permission diagnostic naming the directory | No fallback (Q04) |
| Checkout not writable, entry valid | Renders normally | Reuse writes nothing |
| Invalid entry while another release holds its use guard | Executable rename refused; in-use diagnostic; running binary untouched | No replacement in use (Q14) |
| Repair attempt between a caller's validation and its child start | Refused, since the guard is held from validation | No validation-to-start window |
| `gcliff --version` in a nested folder of a pinned worktree | That worktree's pin provisioned and run | Current worktree (Q10) |
| `gcliff` with an invalid `[source:npm]` section | Reader diagnostic, status 69, git-cliff not started | Whole-file validation (Q11) |
| `gcliff` with a bad git-cliff argument | git-cliff's own error and status | Passthrough (Q08) |
| `uc` or `brel` when provisioning fails | Status 2 with the stage diagnostic, project unchanged | Failure before mutation |
| `version`, ordinary build, curated validation | No provisioning module imported | Operations free of git-cliff |
| Fresh checkout after item 3 | `git status` clean after the first download | Ignore before first write (Q05) |
| `.release.ini` with `version = 2.7.0` | Configuration error; the evidence candidate is not a pin | Evidence-only exception (Q16) |
| Cached 2.7.0 candidate whose archive differs from its trust record | Harness run fails; the trust record is unchanged | Immutable candidate record |
| Fixture regeneration that does not reproduce the recorded hashes | Harness run fails | Deterministic fixture |
| Comparison run of 2.7.0 and 2.14.2 | Same worktree, ranges, `cliff.toml` bytes, flags and environment for both | Controlled comparison inputs |

## Open questions for the v0.14.0 git-cliff-provisioning design

### Q01: Source of the expected digest during provisioning

Question description: the design copies each admitted asset's published
SHA-256 into the tested-pin manifest and verifies downloads against that copy,
so a release never calls the GitHub API. The requirement asks to "verify its
published integrity information" and lists the digest source as design work.
Reading the digest live from the release metadata at each provisioning is the
other natural source.

#### BBQ for Q01

The butcher's label says how much the brisket weighed when it left the shop.
The cook can write that weight in the recipe book once, when the cut was first
chosen, or phone the shop before every barbecue to ask again. Phoning needs the
shop to answer, and the shop limits how many calls it takes from one street. In
this picture: the label is GitHub's published asset digest, the recipe book is
the tested-pin manifest, phoning the shop is a GitHub API call at provisioning
time, and the call limit is the unauthenticated API quota of 60 requests per
hour that a corporate proxy shares across its users.

#### Options for Q01

- Option A: the manifest records the published digest at admission; provisioning
  compares the download with it and never calls the API.
  - pro: provisioning needs only the two download hosts, with no API host and
    no rate limit.
  - pro: an asset replaced upstream after admission is caught as a mismatch.
  - con: correcting a wrong recorded digest needs an llm-shared change.
- Option B: provisioning reads the asset digest from the release metadata on
  every download.
  - pro: always the digest GitHub publishes now.
  - con: adds `api.github.com`, its quota and a metadata stage to every first
    use, and accepts a silently replaced asset.
- Option C: the manifest digest is authoritative, and provisioning also checks
  the live metadata when the API answers, warning on a difference.
  - pro: detects upstream changes early.
  - con: two sources and a warning path for a rare event, plus the API
    dependency whenever it is reachable.

#### Recommended option for Q01 (with arguments for this choice)

Option A: only tested pins are admitted (requirement Q01), so the manifest
already lists every version provisioning may download; recording the digest
there costs nothing and removes a network dependency and a quota from every
release. The order is candidate first: the harness reads the published digest
independently, verifies the download against it and classifies the evidence,
and only then does a reviewed manifest edit admit that same digest. Every
download is still checked against the recorded digest.

#### Answer to Q01: option A (with reason why it must be accepted as the answer)

Option A: it verifies the published integrity information with the fewest
moving parts at release time and turns an upstream asset replacement into a
detected failure instead of a silent change.

User decision: confirmed: option A, the manifest records the published digest
at admission and provisioning never calls the GitHub API, selected by the user
on 2026-11-14 without amendment. Releases need only the two download hosts,
and an asset replaced upstream after admission fails as a digest mismatch.

### Q02: Form of the tested-pin manifest

Question description: the design describes the manifest as a shipped,
read-only Python table in the release engine. Item 6 later proposes newer
tested pins, and admitting a pin means adding an entry with its digest and
evidence reference. The design does not compare that form with a data file.

#### BBQ for Q02

The list of approved charcoal brands can be printed inside the grill's manual,
or kept on a card clipped to the grill. The manual is checked when it is
printed; the card is easy to swap but needs its own check that it is still
readable. In this picture: the manual is a Python table compiled with the
engine, the card is a TOML or JSON data file, and checking the card is parsing
and validating that file at run time.

#### Options for Q02

- Option A: a Python table of frozen records in the engine.
  - pro: type-checked and linted with the code; no parsing step at run time.
  - pro: matches the shipped schema and adapter registries of items 1 and 2.
  - con: admitting a pin is a code change rather than a data change.
- Option B: a TOML file read with `tomllib` and validated on load.
  - pro: a pin admission reads as data, and item 6 tooling can rewrite it.
  - con: a parsing and validation path, with its own failure diagnostics, on
    every configuration read.
- Option C: a JSON file generated from the evidence bundle.
  - pro: the manifest cannot drift from the evidence.
  - con: a generation step and a second artifact to keep in sync.

#### Recommended option for Q02 (with arguments for this choice)

Option A: pins change rarely, always with reviewed evidence, so a code change
is the right weight; it keeps the configuration reader free of a new file
format and follows the explicit shipped tables of items 1 and 2.

#### Answer to Q02: option A (with reason why it must be accepted as the answer)

Option A: it gives the smallest validated surface and keeps admission a
reviewed code change, which is what a tested-pin rule wants.

User decision: confirmed: option A, the manifest is a table of frozen Python
records in the release engine, selected by the user on 2026-11-14 without
amendment. Admitting a pin is a reviewed code change, and the configuration
reader parses no new file format.

### Q03: Lock mechanism for one version and platform

Question description: the design mirrors the project operation lock: a lock
record published without replacement, a short kernel transition mutex around
record changes, polling every 250 ms, and recovery only when
`process_state` reports the owner `DEAD`. The cache lock has no handoff between
processes, unlike the operation lock. A kernel mutex held for the whole
provisioning would let waiters block in the kernel instead of polling, but a
mutex belongs to a thread: its abandonment proves that the owning thread
ended, not that its process did. Whatever serializes the work, the requirement
still demands a `DEAD` process identity before recovering a lock or removing
a partial download. The supported topology is a cache on a local disk of one
machine; neither a mutex nor the PID probe coordinates across machines.

#### BBQ for Q03

The shared grill can carry a paper sign with the user's name, checked by
asking the neighbors whether that person has gone home, or a key that drops
back on its hook when the hand holding it lets go. A dropped key says the hand
let go, not that its owner went home: the owner may still be in the garden with
a half-cooked steak on a side table. In this picture: the paper sign is the
lock record, asking the neighbors is `process_state`, the key is a kernel mutex
held for the whole provisioning, the hand is the thread that owns the mutex,
the owner going home is the process ending, and the half-cooked steak is a
staging directory a live process still owns.

#### Options for Q03

- Option A: lock record plus short transition mutex plus liveness probe, with
  polling, as the design states.
  - pro: the same mechanism and diagnostics as the operation lock; recovery
    and cleanup rest on the `DEAD` process identity the requirement names.
  - con: an owner reported `UNKNOWN`, such as another user's process, blocks
    recovery until the wait expires; waiters poll every 250 ms.
- Option B: a named kernel mutex held for the whole provisioning, waited on
  with the wait budget, plus the same owner records and `DEAD`-only recovery
  and cleanup.
  - pro: waiters block in the kernel with a timeout and wake as soon as the
    holder releases, with no polling.
  - con: two mechanisms instead of one: acquiring the mutex, even an abandoned
    one, still needs the record and probe before removing anything.
  - con: the whole provisioning must run on the thread that owns the mutex.
- Option C: a lock file opened with exclusive sharing for the whole
  provisioning, closed by Windows when the holding process ends.
  - pro: release on process end, and visible in the cache.
  - con: an antivirus or indexing tool that opens the file can make the
    exclusive open fail, which looks like real contention; cleanup of staging
    still needs owner identities.

#### Recommended option for Q03 (with arguments for this choice)

Option A: every option needs the owner record and the `DEAD` check to satisfy
the requirement, so option B adds a second primitive only to save polling, and
a 250 ms poll is negligible next to a download. Option A reuses the operation
lock's tested pattern. The record also lists every cache-writing child the
holder started, its download workers and staging probes, and recovery
requires the owner and each recorded child to be `DEAD` (Q17). A valid-entry
reuse probe holds no lock and is recorded nowhere, so reuse stays lock-free
and read-only.
The design states the supported local-disk topology and makes no
cross-machine claim.

#### Answer to Q03: option A (with reason why it must be accepted as the answer)

Option A: it meets the owner-death condition of the requirement with one
mechanism the engine already uses, while the topology limit is stated rather
than assumed away.

User decision: confirmed: option A, a lock record with a short transition
mutex and the liveness probe, waiters polling every 250 ms, selected by the
user on 2026-11-14 without amendment. Recovery and cleanup require the owner
and every recorded cache-writing child to be `DEAD`, on a local-disk cache.

### Q04: Lock granularity

Question description: the design takes one lock per version and platform, so
provisioning 2.14.2 and an evidence candidate, or two pins of two projects, can
proceed in parallel. One lock for the whole cache would be simpler but
serializes unrelated downloads.

#### BBQ for Q04

A barbecue can have one tongs for every grill, or one tongs per grill. One
tongs is easy to find, but the burger cook waits while the fish cook turns the
salmon. In this picture: the tongs is the provisioning lock, each grill is one
version and platform entry, and the waiting cook is a download of another pin
blocked by an unrelated one.

#### Options for Q04

- Option A: one lock per version and platform.
  - pro: independent pins never wait for each other.
  - con: one lock name per entry to derive and test.
- Option B: one lock for the whole cache.
  - pro: one name; simplest reasoning.
  - con: a slow download of one pin delays every other pin, including a fast
    reuse that found its entry invalid.

#### Recommended option for Q04 (with arguments for this choice)

Option A: entries never share files, so nothing needs a cache-wide lock, and
projects with different pins share one checkout by design. Evidence candidates
use lock names of their own namespace, so a candidate and a production entry of
the same version never share a lock.

#### Answer to Q04: option A (with reason why it must be accepted as the answer)

Option A: it serializes exactly the callers that would write the same entry
and no others.

User decision: confirmed: option A, one lock per version and platform, with
evidence candidates in their own lock namespace, selected by the user on
2026-11-14 without amendment. Independent pins and candidates never wait for
each other.

### Q05: Fixed or adjustable time budgets

Question description: the design fixes the budgets as engine constants: 30 s
per socket operation, 300 s for the download including its retry, 15 s for the
version probe and 360 s for waiting on a holder. Requirement Q07 excludes a
mirror setting; Q05 B permits one finite provisioning-budget override. A very
slow link could need more than 300 s for a 7.4 MB
archive (about 25 KB/s). This question concerns the values only; how a budget
is enforced against a call that never returns is Q17.

#### BBQ for Q05

The recipe says to give up on the charcoal delivery after five minutes. That
suits most streets, but a farm at the end of a dirt road needs longer. The
recipe can keep five minutes, let the cook write another number, or scale the
wait with the size of the order. In this picture: five minutes is the fixed
download budget, the farm is a slow corporate link, writing another number is
an environment override, and scaling with the order is a budget derived from
the manifest's asset size.

#### Options for Q05

- Option A: fixed constants, reviewed when a pin is admitted.
  - pro: no new setting to document or validate.
  - con: a slower link fails until a code change raises the constant.
- Option B: the constants plus one documented environment variable that
  raises the download and wait budgets.
  - pro: a slow site adapts without a code change.
  - con: a new setting to document and validate; requirement Q07 excludes a
    mirror setting, not this override.
- Option C: budgets derived from the manifest size at a documented minimum
  throughput, with a fixed floor.
  - pro: a larger future asset gets a proportional budget automatically.
  - con: one more rule to explain in diagnostics.

#### Recommended option for Q05 (with arguments for this choice)

Option A: the asset size is known per pin and changes only with an admission,
which already reviews the numbers; a fixed, documented budget keeps
diagnostics simple and adds no setting.

#### Answer to Q05: option A (with reason why it must be accepted as the answer)

Option A: it meets requirement Q15's finite budgets with the least surface, and
the admission review is the natural place to revisit them.

User decision: confirmed: option B, the fixed constants plus one documented
environment variable that raises the download and wait budgets, selected by
the user on 2026-11-14 instead of the recommended option A (first picked A,
then corrected to B). Requirement Q07 excludes a mirror setting, not this
budget override; requirement Q15 still requires every budget, raised or not,
to stay documented and finite. Consolidation defines the variable's name, its
form, its accepted range and the refusal of an invalid value, defines the
caller's finite wait budget in Q18 (it need not outlast a differently
configured holder), names the variable in the expiry remedy, and replaces the
body's statement that the budgets are not configuration.

### Q06: Retry policy for the download

Question description: the design allows one retry after 5 s for a connection
error or a reset, within the 300 s budget: HTTP 429 or 5xx is retryable; other
HTTP 4xx, size overflow and digest mismatch are not.

#### BBQ for Q06

When the delivery van breaks down, the shop can send another van once, keep
sending vans until the party ends, or not send another one. Sending vans
forever means the guests wait without knowing why. In this picture: the van
breaking down is a transient network failure, another van is a retry, and the
party ending is the download budget.

#### Options for Q06

- Option A: one retry for transient failures, inside the budget.
  - pro: absorbs a dropped connection, the most common proxy hiccup.
  - con: a second attempt doubles the time before a real outage is reported.
- Option B: no retry.
  - pro: simplest; the failure is reported at once.
  - con: a single reset fails a release that would have succeeded.
- Option C: up to three retries with growing delays, inside the budget.
  - pro: rides out a short outage.
  - con: more states to test, and the budget, not the retry count, ends most
    real outages anyway.

#### Recommended option for Q06 (with arguments for this choice)

Option A: one retry covers the usual transient reset without hiding a real
outage, and the shared budget keeps the worst case bounded for waiters. The
delay and the second attempt draw on the same deadline, a `Retry-After` header
never extends it, and an integrity failure is never retried.

#### Answer to Q06: option A (with reason why it must be accepted as the answer)

Option A: it is the smallest policy that survives a transient failure while
keeping the reported failure time predictable.

User decision: confirmed: option A, one retry after 5 s for a transient
failure inside the download budget (HTTP 429 or 5xx is retryable; other HTTP
4xx, size overflow and digest mismatch are not), selected by the user on
2026-11-14 without amendment. The
retry draws on the same budget, raised or not (Q05 B), and a `Retry-After`
header never extends it.

### Q07: Replacing an entry found invalid

Question description: when a published entry fails the reuse check, it must be
replaced without ever replacing a binary that another caller is validating or
running (requirement Q14). The first version of this design relied on Windows
refusing to move a directory whose executable runs, which no documented
guarantee supports, and left a window between a caller's validation and the
start of its git-cliff process. The revised body uses a use guard: every
caller holds a read handle on `git-cliff.exe` that denies write and delete
sharing, from validation until its git-cliff process exits, and a replacement
starts by renaming that executable, which needs delete access and fails while
any guard is open. Windows documents that sharing rule for `CreateFileW`.

#### BBQ for Q07

A jar of spoiled sauce sits in the shared fridge. Each cook who takes sauce
puts a clothes peg on the jar's lid while using it, and nobody may take a
pegged jar off the shelf. The cook who spots the spoiled jar replaces it only
when no peg is on it. The alternatives are refusing to cook until someone
throws the jar away, or never moving any jar and putting each new jar on a new
numbered shelf. In this picture: the spoiled jar is an invalid entry, the peg
is the use guard held from validation until git-cliff exits, taking the jar off
the shelf is renaming its executable, refusing to cook is a diagnostic asking
the user to delete the entry, and numbered shelves are generation directories.

#### Options for Q07

- Option A: the use guard, plus a replacement that renames the executable
  first, under the provisioning lock, and reports in-use when the rename is
  refused. Every execution of the cached executable, the reuse probe as well
  as the git-cliff run, inherits the guard through an explicit
  inherited-handle list and belongs to the caller's kill-on-close job from its
  creation, so the protection lasts for that child's actual lifetime even if
  its caller dies, and no such child ever runs outside the job (Q17).
  - pro: self-healing in the usual case, with no manual step.
  - pro: rests on documented file-sharing semantics and closes the
    validation-to-start window; a read handle keeps read-only reuse working.
  - con: a Windows handle per use, opened through `CreateFileW` and passed to
    each child that executes the entry, and developer-run acceptance checks
    for the running, launcher-killed, probe-orphaned and validation-to-start
    cases.
- Option B: never replace automatically; report the invalid entry and ask the
  user to delete it.
  - pro: no automatic removal at all.
  - con: a manual repair, which the requirement avoids, for a corrupted file.
- Option C: immutable generation directories under each entry, selected by a
  pointer file replaced atomically, with no automatic removal of an old
  generation.
  - pro: nothing in use is ever moved, so no guard is needed.
  - con: a pointer to read on every reuse, and every corrupted generation stays
    on disk until removed by hand.

#### Recommended option for Q07 (with arguments for this choice)

Option A: it keeps one directory per pin, repairs corruption automatically,
and its protection follows from the documented rule that a file cannot be
renamed while another handle denies delete sharing. Holding the guard from
validation covers the race between validation and child start as well as the
running child, and passing it to the reuse probe too keeps an orphaned probe
from outliving the only guard. Its parent-death guarantee depends on the
creation-time containment of Q17 option A.

#### Answer to Q07: option A (with reason why it must be accepted as the answer)

Option A: it repairs an invalid entry automatically and makes "never replace a
binary in use" a property of an open handle instead of an undocumented
assumption.

User decision: confirmed: option A, the use guard held from validation until
the git-cliff process exits and inherited by every child that executes the
entry, with a rename-first replacement under the provisioning lock that
reports in-use when refused, selected by the user on 2026-11-14 without
amendment. Its parent-death guarantee relies on the creation-time containment
of Q17 option A.

### Q08: Proxy resolution

Question description: the design resolves proxies with
`urllib.request.getproxies()`, which reads `HTTPS_PROXY`, `HTTP_PROXY` and
`NO_PROXY`, or the static Windows proxy setting. On this workstation the
environment variables are set and the Windows setting uses a proxy
auto-configuration script, which `urllib` does not evaluate. Windows' own HTTP
stack (WinHTTP) can resolve such scripts and is reachable from Python through
`ctypes`.

#### BBQ for Q08

The delivery driver can follow the street signs the town put up, or call the
town hall's switchboard, which knows the route to every house but answers only
on the town's own phone line. In this picture: the street signs are the proxy
environment variables and the static Windows setting, the switchboard is the
proxy auto-configuration script, and the town's phone line is WinHTTP called
through `ctypes`.

#### Options for Q08

- Option A: `urllib.request.getproxies()` only; an auto-configuration script
  without environment variables fails with the network diagnostic naming
  `HTTPS_PROXY`.
  - pro: standard library only, already verified on this workstation.
  - con: a machine configured only by a script needs `HTTPS_PROXY` set.
- Option B: ask WinHTTP for the proxy of each URL, including scripts and
  automatic discovery, then download through it with `urllib`.
  - pro: follows the Windows configuration exactly.
  - con: Windows API code through `ctypes`, a new failure surface, and two
    proxy sources to explain.
- Option C: environment variables only, ignoring the Windows setting.
  - pro: one documented source.
  - con: a static Windows proxy without environment variables stops working.

#### Recommended option for Q08 (with arguments for this choice)

Option A: it is what requirement Q07 calls the documented standard proxy
configuration, and its diagnostic tells a script-only machine exactly which
variable to set. The workstation check supports it but does not prove every
proxy works: machines configured only by an auto-configuration script, and
proxies that require authentication, are outside v0.14.0 and are stated as
such. Script support can be a later, separate decision.

#### Answer to Q08: option A (with reason why it must be accepted as the answer)

Option A: it delivers the selected network scope with the standard library and
a precise remedy for the unsupported case.

User decision: confirmed: option A, `urllib.request.getproxies()` only, the
proxy environment variables or else the static Windows proxy setting, selected
by the user on 2026-11-14 without amendment. A machine configured only by an
auto-configuration script gets the network diagnostic naming `HTTPS_PROXY`;
scripts and authenticated proxies stay outside v0.14.0.

### Q09: What the provisioning entry point returns

Question description: the design's entry point returns the verified path, and
item 4 owns how git-cliff is invoked for rendering. git-cliff reads its
`GIT_CLIFF_*` environment variables, including whole-configuration overrides,
so a caller that forgets to remove them renders with ambient settings. The
version probe already removes them.

#### BBQ for Q09

The shop can hand over the knife alone, or the knife in a sheath with a guard
that every cook uses the same way. A cook who takes the bare knife may forget
the guard. In this picture: the knife is the verified `git-cliff.exe` path, the
sheath is an invocation object that runs git-cliff with a fixed environment
policy, and forgetting the guard is a renderer that inherits `GIT_CLIFF_*`
variables from the user's console.

#### Options for Q09

- Option A: return the path; items 4 and 5 and the launcher each build their
  own invocation.
  - pro: the smallest interface for item 3.
  - con: the environment rule is repeated, and a caller can omit it.
- Option B: return an invocation object that runs git-cliff with a caller
  chosen policy: a scrubbed environment and closed input for the engine, or
  full passthrough for `gcliff`.
  - pro: one place knows git-cliff's environment surface, shared by the probe,
    the engine and the launcher.
  - con: item 3 defines an interface that item 4 must accept.
- Option C: return the path and a ready-made scrubbed environment mapping.
  - pro: shares the rule without owning process execution.
  - con: callers can still pass the wrong mapping.

#### Recommended option for Q09 (with arguments for this choice)

Option B: the engine and the launcher must treat git-cliff's environment
differently, and keeping both policies next to the probe that already applies
one removes a class of rendering surprises without taking rendering decisions
away from item 4. The scrubbed policy also serves the evidence comparison, and
the object owns, in one place, the environment policy, the creation-time
containment and the guard transfer of the child lifecycle (Q17): it starts
git-cliff, and the reuse probe through the same path, inside the job and with
the guard inherited, so the protection does not depend on the object or its
process staying alive, and no caller can forget the guard or start an
uncontained child. Item 4 keeps its rendering arguments, postprocessing and
timeouts.

#### Answer to Q09: option B (with reason why it must be accepted as the answer)

Option B: it shares the one fragile rule, the `GIT_CLIFF_*` environment
surface, across every caller while item 4 keeps its own arguments and
timeouts.

User decision: confirmed: option B, the entry point returns an invocation
object with a caller-chosen policy, a scrubbed environment and closed input
for the engine or full passthrough for `gcliff`, which starts git-cliff and the
reuse probe inside the job with the guard inherited, selected by the user on
2026-11-14 without amendment. Consolidation replaces the body's path-return
formulation; item 4 keeps its rendering arguments, postprocessing and
timeouts.

### Q10: How gcliff starts git-cliff

Question description: the design starts git-cliff as a child of the Python
launcher process, with inherited standard streams, arguments rebuilt by the
Windows command-line rules and the batch guard against `%`, `^`, `!` and `"`.
The batch file could instead run the path Python resolves, passing its raw
`%*`.

#### BBQ for Q10

The waiter can carry the guest's order to the kitchen in his own words, or
hand the kitchen the guest's handwritten note. His words are reliable for
ordinary orders; the note keeps every odd spelling but needs a second trip to
report back whether the dish worked. In this picture: the waiter is the Python
launcher, his own words are arguments rebuilt by the standard Windows rules,
the handwritten note is the batch file's raw `%*`, and the second trip is
passing the provisioning status back from Python to the batch file before it
runs git-cliff.

#### Options for Q10

- Option A: Python runs git-cliff as a child with inherited streams and
  returns its status; the batch guard stays.
  - pro: one status path, no temporary file, Ctrl+C reaches both processes.
  - con: one extra process stays alive during the run; quoted characters the
    guard rejects need `cliff.toml`.
- Option B: Python provisions and writes the path for the batch file, which
  runs git-cliff with `%*`.
  - pro: raw argument fidelity, including characters the guard rejects.
  - con: a two-step protocol to carry both the path and the reserved status
    from Python to the batch file.
- Option C: Python replaces itself with git-cliff through `os.execv`.
  - pro: no lingering parent in principle.
  - con: on Windows it starts a new process and returns at once, losing the
    status the caller waits for.

#### Recommended option for Q10 (with arguments for this choice)

Option A: git-cliff parses its command line with the same Windows rules Python
uses to rebuild it, the guard already protects the batch entry kinds, and a
single status path is what requirement Q08's passthrough needs. The child is
created through the engine's Windows layer rather than `subprocess`,
suspended, a member of a kill-on-close job from its creation and holding the
inherited use guard (Q17); a containment failure stops before git-cliff
starts, with status 69, instead of creating the child and assigning it later.
The launcher ignores Ctrl+C while it waits, returns the child's status without
the release launcher's normalization, and its own death ends the git-cliff
run.

#### Answer to Q10: option A (with reason why it must be accepted as the answer)

Option A: it passes arguments, streams and status through with the fewest
moving parts and reuses the existing batch-argument guard.

User decision: confirmed: option A, the Python launcher starts git-cliff as a
contained child with inherited streams and the use guard and returns its
status unchanged, keeping the batch-argument guard, selected by the user on
2026-11-14 without amendment. It uses the passthrough policy of the Q09
invocation object.

### Q11: The reserved gcliff failure status

Question description: the design proposes 69 for any `gcliff` failure before
git-cliff starts. 69 is the conventional "service unavailable" value. A few
observed statuses cannot prove that an admitted version never returns it, so
the proposal holds only with admission evidence: an audit of each version's
exit paths at its source tag (error return, argument errors, propagated helper
statuses, panics and abnormal termination), corroborated by observed success,
usage-error, failing-render and reachable panic statuses. If a version can
return 69, admission stops and the conflict returns to the user. This question
chooses the number; the audit applies to whichever number is chosen.

#### BBQ for Q11

The kitchen uses bell signals: one ring for "order ready", two for "order
problem". The grill master needs a signal for "no charcoal at all" that no cook
already uses. In this picture: the bell signals are exit statuses, the cooks'
signals are git-cliff's own statuses, and "no charcoal" is the reserved status
for a provisioning failure.

#### Options for Q11

- Option A: 69.
  - pro: a recognized meaning, "service unavailable", far from git-cliff's
    small statuses.
  - con: rarely seen on Windows, so it needs its documentation line.
- Option B: 3, next to the release launcher's statuses.
  - pro: familiar to readers of the release launcher.
  - con: 3 already means incomplete restoration for release operations, a
    different meaning.
- Option C: 255.
  - pro: clearly out of band.
  - con: also what many tools return for a generic fatal error, so it says
    less.

#### Recommended option for Q11 (with arguments for this choice)

Option A: it carries the intended meaning and does not overload a release
status; the per-version exit-path audit, not the sampled statuses, is what
shows that no admitted version returns it.

#### Answer to Q11: option A (with reason why it must be accepted as the answer)

Option A: it gives scripts a "tool unavailable" value with a recognized
meaning, whose exclusion from git-cliff's own statuses is established version
by version at admission.

User decision: confirmed: option A, status 69 for any `gcliff` failure before
git-cliff starts, selected by the user on 2026-11-14 without amendment. It
holds only with each admitted version's exit-path audit; a version that can
return 69 stops admission and returns the conflict to the user.

### Q12: Where evidence candidates are extracted

Question description: the design extracts evidence candidates, including the
2.7.0 binary, under `.tools/git-cliff/evidence/<version>/<triple>/`, a subtree
production resolution never reads and the same ignore rule covers. A separate
tree or a temporary directory per run would keep them physically apart from
production entries.

#### BBQ for Q12

The tasting samples can sit on a labeled shelf in the same pantry, in a
separate cupboard with its own lock, or be bought fresh for every tasting and
thrown away. The shared pantry is convenient; the cupboard needs its own key;
buying fresh costs a trip each time. In this picture: the pantry is
`.tools/git-cliff/`, the labeled shelf is its `evidence/` subtree, the separate
cupboard is a `.tools/git-cliff-evidence/` tree with its own ignore entry, and
buying fresh is a temporary directory downloaded again on every harness run.

#### Options for Q12

- Option A: the `evidence/` subtree of the cache.
  - pro: one ignore rule; repeated runs reuse the recorded bytes offline.
  - con: evidence binaries share a tree with production entries.
- Option B: a sibling `.tools/git-cliff-evidence/` tree.
  - pro: physical separation from production.
  - con: a second ignore entry and a second location to explain.
- Option C: a temporary directory per run.
  - pro: nothing kept between runs.
  - con: every repetition downloads again, and 2.7.0 relies on HTTPS each
    time while the recorded digest still has to match.

#### Recommended option for Q12 (with arguments for this choice)

Option A: resolution reads only `<pin>/<triple>/` for a manifest pin and
`evidence` is never a valid version, so sharing the tree cannot leak a
candidate into production, while one ignore rule and offline repetition stay
simple. The location alone does not make reuse safe: the candidate cache has
its own locks, staging, atomic publication, entry record and use guard, and a
cached candidate runs only after its entry matches the immutable candidate
trust record and its executable matches the entry, in the production order.
Its children follow the production lifecycle and classes (Q17): download
workers and staging probes are cache-writing children recorded in the
candidate attempt, while the metadata worker, reuse probes and comparison runs
are record-free; every one of them is created inside its job.

#### Answer to Q12: option A (with reason why it must be accepted as the answer)

Option A: it keeps the evidence-only binary unreachable by production
provisioning without a second location or a download per repetition.

User decision: confirmed: option A, the `evidence/` subtree of the cache with
its own namespace, selected by the user on 2026-11-14 without amendment. A
cached candidate runs only after its entry matches the immutable trust record
and its executable matches the entry, and production resolution never reads
the subtree.

### Q13: What the committed evidence bundle contains

Question description: the design commits raw outputs per range and candidate,
a difference listing and the classification table. llm-shared's changelog is
about 89 KB, so raw outputs for the full history, 13 tag ranges and the
unreleased range come to roughly 400 KB of text for two versions. Digests of
the outputs with only the differing hunks would be much smaller but would need
a rerun to show an identical output.

#### BBQ for Q13

After the taste test, the cook can keep a full plate of every dish from both
brands in the freezer, keep a photo of each plate plus samples of the dishes
that tasted different, or keep only the written verdict. In this picture: the
full plates are the raw outputs, the photos are output digests, the samples
are the differing hunks, and the written verdict is the classification table.

#### Options for Q13

- Option A: raw outputs, differences and classification.
  - pro: complete and readable without rerunning anything.
  - con: about 400 KB of generated text in the repository, growing with each
    admitted pin.
- Option B: input manifest, output digests, differing hunks with context, and
  classification.
  - pro: small, and still verifies that a rerun reproduces the same outputs.
  - con: reading an unchanged output needs a rerun.
- Option C: classification table only.
  - pro: smallest.
  - con: nothing to verify a classification against without rerunning both
    versions.

#### Recommended option for Q13 (with arguments for this choice)

Option B: the classification needs the differing hunks, and reproducibility
needs the digests; identical outputs carry no information worth 400 KB, and
the harness can regenerate them when someone needs to read one. Regeneration
relies on the controlled harness inputs: the committed `cliff.toml` bytes, the
frozen commit, the fixed flags, working directory and environment, and the
deterministic fixture.

#### Answer to Q13: option B (with reason why it must be accepted as the answer)

Option B: it keeps every classified difference reviewable and every output
verifiable while keeping generated text out of the repository.

User decision: confirmed: option B, the input manifest, output digests,
differing hunks with context and the classification, selected by the user on
2026-11-14 without amendment. Consolidation replaces the body's raw-output
formulation; identical outputs are regenerated from the controlled inputs
when needed.

### Q14: Fixture history for snapshot-tag cases

Question description: llm-shared has no snapshot tag, so the design has the
harness build a small scripted repository with stable and `-SNAPSHOT` tags and
record its script and resulting commit hashes. A committed `git bundle` of that
repository would pin the exact objects instead of regenerating them.

#### BBQ for Q14

The test recipe can be written down so anyone can cook the same dish again, or
the cooked dish can be vacuum-sealed and stored. The recipe is readable but only
reproduces the dish if every step is exact; the sealed dish is exact but
opaque. In this picture: the recipe is the committed fixture script with fixed
author and dates, cooking it again is regenerating the repository, and the
sealed dish is a committed `git bundle` file.

#### Options for Q14

- Option A: a committed script with fixed author, committer and dates; the
  bundle records the resulting hashes.
  - pro: readable and reviewable; the recorded hashes prove the regeneration.
  - con: depends on Git producing the same objects from the same inputs.
- Option B: a committed `git bundle` of the fixture repository.
  - pro: exact objects, no regeneration.
  - con: a binary file in the repository, unreadable in review.
- Option C: no fixture; snapshot-tag cases wait for item 4.
  - pro: less work in item 3.
  - con: leaves part of the evidence matrix of requirement Q13 uncovered.

#### Recommended option for Q14 (with arguments for this choice)

Option A: Git objects are a pure function of their content, so a script that
fixes every object-producing input regenerates the same hashes: each tree's
file names and bytes, parent order, messages, author and committer names,
emails and dates with time zones, annotated tag names, tagger identities,
dates and messages, the SHA-1 object format, and command-line Git
configuration with no global or system configuration, hooks, signing or
line-ending conversion. The recorded hashes turn any drift into a failed run.

#### Answer to Q14: option A (with reason why it must be accepted as the answer)

Option A: it covers the snapshot-tag cases with a reviewable fixture whose
exactness is checked rather than assumed.

User decision: confirmed: option A, a committed script that fixes every
object-producing input, with the resulting commit and tag hashes recorded in
the bundle, selected by the user on 2026-11-14 without amendment, after a
plain-language restatement of the question. A regeneration that does not
reproduce the recorded hashes fails the harness run.

### Q15: Surface of the evidence harness

Question description: the design makes the harness a developer-run command,
outside pytest. Item 6 later proposes newer tested pins "with its diff", which
needs the same download, run and comparison logic for a consumer's history.
The harness could stay a script, become a public engine command now, or be an
internal comparison module with a developer entry point.

#### BBQ for Q15

The tasting setup can be a one-off folding table, a permanent counter in the
shop window, or a sturdy table kept in the back room that the shop can roll out
later. The window counter invites customers before the shop is ready to serve
them. In this picture: the folding table is a throwaway script, the window
counter is a public engine command, and the back-room table is an internal
comparison module with a developer entry point that item 6 can reuse.

#### Options for Q15

- Option A: a developer-only script.
  - pro: no public contract in item 3.
  - con: item 6 must extract or rewrite the logic later.
- Option B: a public engine command in item 3.
  - pro: item 6 and consumers can call it at once.
  - con: a public command, output and statuses designed before item 6
    defines its needs.
- Option C: an internal comparison module with a developer entry point; item 6
  decides its public form.
  - pro: reusable logic without committing to a public interface.
  - con: an internal interface to keep stable for item 6.

#### Recommended option for Q15 (with arguments for this choice)

Option C: item 6's "newer tested pin with its diff" is the same comparison on
another history, so the logic should be reusable, but its public form belongs
to item 6's design.

#### Answer to Q15: option C (with reason why it must be accepted as the answer)

Option C: it serves item 3's evidence now and leaves item 6 a tested module
instead of a script or a premature command.

User decision: confirmed: option C, an internal comparison module with a
developer entry point, item 6 deciding its public form, selected by the user
on 2026-11-14 without amendment.

### Q16: Where the gcliff alias definition lives

Question description: the design ships the macro line
`gcliff="%LLM_SHARED_DIR%\bin\gcliff.bat" $*` as a single-line alias fragment
beside the launcher, which item 8 copies into the shared `senv.doskey`. The
line could instead live only in documentation, or in a separate macro file that
item 8 starts loading.

#### BBQ for Q16

The new grill comes with its handle in a separate bag. The bag can sit next to
the grill until the installer fits it, the handle can be described in the
manual for the installer to make, or the grill can get a second hook where the
handle will hang once someone switches it on. In this picture: the handle is
the `gcliff` macro line, the bag next to the grill is an alias fragment beside
the launcher, the manual is documentation only, the second hook is a separate
macro file loaded later, and the installer is item 8.

#### Options for Q16

- Option A: a tested single-line fragment beside the launcher; item 8 copies
  it into `senv.doskey`.
  - pro: the exact line is tested in item 3 and copied, not retyped.
  - con: a fragment file whose only consumer is item 8.
- Option B: the line in documentation only.
  - pro: no extra file.
  - con: untested until item 8, and easy to mistype.
- Option C: a separate release macro file that item 8 makes `senv.bat` load.
  - pro: item 8 changes one load line instead of copying macros.
  - con: a second macro file for consumers to load, against the one shared
    alias set of the umbrella.

#### Recommended option for Q16 (with arguments for this choice)

Option A: requirement Q12 has item 3 ship and test the definition without
editing `senv.doskey`; a fragment loaded by the same macro parsing is the
smallest way to test exactly what item 8 will add.

#### Answer to Q16: option A (with reason why it must be accepted as the answer)

Option A: it lets item 3 test the definition it ships while keeping the shared
alias file untouched until the cutover.

User decision: confirmed: option A, a tested single-line alias fragment beside
the launcher that item 8 copies into `senv.doskey`, selected by the user on
2026-11-14 without amendment.

### Q17: How stage deadlines are enforced against a call that never returns

Question description: requirement Q15 demands finite budgets for every network
stage and version probe. Python documents the `urllib` timeout as applying to
each blocking socket operation, not to a whole transfer, and name resolution
is not covered; a slow trickle of bytes also restarts the inactivity timer.
Checking a clock between calls cannot stop a call that never returns, so the
body runs each network attempt in a worker process. A worker alone is not
enough: Windows does not end a child when its parent dies, so a parent that
crashes leaves its worker, probe or git-cliff run alive, still able to write
staging or run an entry its dead parent no longer guards. The revised body
answers both with one child lifecycle: every child is created suspended through
the engine's Windows layer, with an explicit inherited-handle list and
membership, from its creation, in a kill-on-close job that only the parent
holds. Cache-writing children, download workers and staging probes, are
recorded in their attempt's owner records before they resume; record-free
children, reuse probes, the metadata worker and git-cliff runs, take no lock
and write no record, and those that execute a cached entry inherit its use
guard. Recovery needs every recorded process `DEAD`. Assigning a child to the
job after creating it is not enough: a parent that dies between the two calls
leaves a suspended child outside any job, holding its inherited handles for as
long as it lives. This question is separate from Q05, which only sets the
values.

#### BBQ for Q17

The cook sends helpers to fetch charcoal and wants them back within the hour.
Checking a watch between shops does not help a helper stuck in a queue that
never moves, and a helper keeps shopping even if the cook faints. The cook can
hire every helper with a radio already clipped to the helper's belt, which
sends them all home when the cook's own radio goes silent, and write on the
kitchen board, before they leave, the names of those who will handle the
stock; give each helper a personal alarm that sends the helper home at a set
hour and have the helper sign the board; hire a courier firm that promises to
cancel any trip at a given hour; or trust the watch. A radio handed over at
the door, after hiring, does not help: a cook who faints in between leaves a
helper with no radio at all. In this picture: the helpers are the download
worker, the metadata worker, the probes and the git-cliff runs; the cook
fainting is the parent process dying; the radio clipped at hiring is
membership, from creation, in a kill-on-close job held only by the parent;
the radio handed over at the door is a job assignment after creation; the
board is the owner records that recovery checks for cache-writing children;
the personal alarm is a worker's own watchdog deadline; the courier firm is a
third-party transport with a cancellable deadline; and the watch is socket
timeouts plus clock checks.

#### Options for Q17

- Option A: the contained child lifecycle. Create each child suspended with
  an explicit inherited-handle list and creation-time membership in the
  parent-only kill-on-close job (`PROC_THREAD_ATTRIBUTE_JOB_LIST`, Windows 10
  or Windows Server 2016 and later). A creation or containment failure yields
  no uncontained child. Publish cache-writing attempt identities before
  resume; lock-free reuse probes publish no cache records and inherit their
  executable's guard. Terminate and wait at the deadline; recover writable
  attempts only after all recorded actors are `DEAD`.
  - pro: stops any blocking call, and the job bounds every child from the
    moment it exists, including a hung probe or a git-cliff run whose launcher
    died, with no third-party code.
  - pro: no child ever exists outside its job, and a cache-writing child that
    was never recorded never ran, so a parent crash during or after creation
    leaves no uncontained process and no unrecorded writer; reuse stays
    lock-free and read-only.
  - con: process creation moves from `subprocess` into the Windows layer
    (`CreateProcessW`, attribute lists, job objects); the platform baseline
    rises to Windows 10 or Windows Server 2016 with no fallback, and a host
    job that refuses nesting, such as one with UI limits, makes the stage fail;
    developer-run checks of real containment, kill-on-close and guard
    inheritance run outside the process-free suite.
- Option B: self-limiting workers started through `subprocess`: each worker
  records its own identity in staging before writing anything and carries an
  absolute deadline enforced by an internal watchdog thread that ends its
  process; the parent still terminates it on expiry.
  - pro: pure standard-library Python, no job objects.
  - con: a git-cliff probe or run cannot carry a watchdog, so an orphaned hung
    probe or a launcher-less run is unbounded; recovery may then wait forever.
  - con: between start and self-recording a worker is unrecorded, so it must
    write nothing before its record, and recovery must tolerate an attempt
    whose worker never appears.
- Option C: an in-process transport with a documented end-to-end cancellable
  deadline.
  - pro: no extra process for downloads.
  - con: the standard library has none, the release dependency group is empty,
    and probes and git-cliff runs still need a lifecycle of their own.
- Option D: socket timeouts plus clock checks between blocking operations.
  - pro: simplest, all in one process.
  - con: name resolution and some handshakes are not covered, so a stage can
    outlive its budget; this does not meet requirement Q15.

#### Recommended option for Q17 (with arguments for this choice)

Option A: it is the only option that bounds every child, workers, probes and
git-cliff runs alike, from its creation and whatever happens to the parent,
and it makes "every writer is `DEAD` before cleanup" checkable from the owner
records while reuse writes nothing. Containment is part of the creation call
rather than a later parent action, because no parent-only cleanup can reach a
child that a crash left outside the job. The cost is one new Windows-layer
creation path beside the engine's existing `ctypes` process primitives and a
Windows 10 or Windows Server 2016 baseline, and a process start is negligible
next to a first-use download.

#### Answer to Q17: option A (with reason why it must be accepted as the answer)

Option A: it turns the finite stage budgets of requirement Q15 and the
owner-aware cleanup of requirement Q14 into enforced properties that survive a
parent crash at any point, creation included, with unit seams for the
process-free suite and real checks outside it.

User decision: confirmed: option A, the contained child lifecycle with
creation-time membership in a parent-only kill-on-close job, suspended
creation, identity publication for cache-writing children before resume,
record-free guarded reuse probes, termination at the deadline and recovery
only after every recorded actor is `DEAD`, selected by the user on 2026-11-14
without amendment. It accepts the Windows 10 or Windows Server 2016 baseline
and the fail-closed stage failure under a host job that refuses nesting.

### Q18: What contract does the Q05 budget override expose?

Question description: Q05 B is confirmed: the budgets stay fixed constants,
plus one documented environment variable that raises the download and wait
budgets. That decision does not say which stages the variable affects beyond
the download and the wait, what values it accepts, or how two callers with
different values behave when one waits for the other's lock. Those choices
change behavior: whether a hung probe or metadata lookup may run longer, how
long a user may wait, and whether one caller can extend another's deadline.
The requirement keeps every budget documented and finite (requirement Q15),
and it lets a waiter fail when the holder does not finish within that
waiter's own budget (requirement Q06). Q05 B names the download and wait
budgets; Q18 defines their representation, bounds and caller semantics, and
option C would additionally expand the affected stages. It does not reopen
whether an override exists.

#### BBQ for Q18

The recipe now lets the cook wait longer for the charcoal van. The cook can
write the exact number of minutes on the order slip, choose a multiple of the
standard wait, or turn one dial that stretches every timer in the kitchen,
including the one for checking the oven thermometer. Each cook waiting for the
shared grill keeps a personal timer: a cook with the standard timer may give
up while a neighbor's slow delivery is still on its way, but never throws the
neighbor's half-unpacked order away. In this picture: the van wait is the
archive download budget, the order slip is a value in seconds, the multiple is
a multiplier, the dial for every timer is a multiplier applied to all stages,
the oven thermometer is the version probe, the shared grill is the
provisioning lock, and throwing the order away is recovering a live owner's
lock.

#### Options for Q18

- Option A: an exact download budget in seconds, coupled to the wait.
  - Name: `LLM_SHARED_GIT_CLIFF_DOWNLOAD_TIMEOUT_SECONDS`, outside the
    upstream `GIT_CLIFF_*` namespace that the invocation object scrubs (Q09).
  - Unset, it means the existing 300 s download budget. A set value is an
    ASCII decimal integer of seconds from 300 through 3600 inclusive. An empty
    string, a sign, a fraction, a unit, whitespace or an out-of-range value is
    refused, never clamped and never replaced by the default. The 3600 s
    limit is a proposed operational policy, not a bound the requirement
    derives.
  - With D the caller's validated download budget, its lock wait is
    W = D + 60 s: 300 and 360 s by default, 900 and 960 s for a 900 s value,
    3600 and 3660 s at the limit. The 60 s keep the two 15 s probe allowances
    and the existing 30 s processing allowance; W is a contention policy, not
    a promise that all filesystem work ends within 30 s.
  - D and W apply to production provisioning and to evidence-candidate archive
    downloads. Socket connect or inactivity stays 30 s, every version probe
    15 s and the harness metadata lookup 60 s; rendering stays item 4's.
  - The value is read and validated once, when a caller enters provisioning or
    starts the evidence harness, before any reuse probe, child creation,
    network access or cache change, and the resolved policy is passed to
    workers instead of being read again. An invalid value is a setup failure,
    status 2 for engine operations and 69 for `gcliff`, even when a valid
    cached entry exists. Operations that do not need git-cliff never read it.
  - Every caller owns its finite W. A default 360 s waiter may time out
    behind a holder using D = 1800 s; its deadline is never reset or enlarged
    by a holder change, and W = D + 60 s applies to the caller's own policy,
    not to the holder's environment. A timeout never authorizes recovering a
    live or `UNKNOWN` owner (Q03).
  - Q06's retry count, 5 s delay and shared deadline stay unchanged inside D.
    The waiting line and expiry diagnostics show the effective budgets;
    download and wait remedies name the variable and its range, while probe
    and metadata remedies never suggest that it extends their budgets.
  - pro: an exact duration for the slow archive transfer, with the two
    affected budgets coupled and bounded; one setting, a narrow scope, and a
    hung local probe stays quick to diagnose.
  - con: a slow metadata service or a socket inactivity timeout is not cured
    by raising the archive budget, and differently configured callers can
    still time out on contention.
- Option B: an integer multiplier m from 1 through 12 for the download and
  wait only: D = 300 s × m and W = D + 60 s, with the same fixed other stages,
  single validation and per-caller behavior as option A.
  - pro: a simple relative scale with unchanged defaults.
  - con: coarse 300 s steps, and the effective duration moves if a base
    constant later changes.
- Option C: an integer multiplier m from 1 through 12 that scales the
  download, socket, probe, metadata and wait budgets together.
  - pro: one knob also helps slow probe and metadata environments, with a
    finite upper bound.
  - con: it widens the scope Q05 B chose (download and wait) and delays
    unrelated failure detection: at 12, a version probe may take 180 s and the
    metadata lookup 720 s.

Acceptance examples for the chosen contract, checked with a fake clock and no
real long wait (stated here for option A):

| Scenario | Expected outcome |
| --- | --- |
| Variable unset | D = 300 s, W = 360 s |
| Value `900` | D = 900 s, W = 960 s |
| Value `3600` | D = 3600 s, W = 3660 s |
| Value empty, `-1`, `300.5`, `600s`, `600` with a leading space, `299` or `3601` | Setup failure naming the variable and its range; status 2, or 69 for `gcliff`; nothing provisioned |
| Invalid value with a valid cached entry | The same setup failure; the entry is not used |
| `version` command or ordinary build with an invalid value | Unaffected; the variable is not read |
| Value `900`, first attempt reset, `Retry-After: 2000` | The 5 s delay and the retry stay inside 900 s; the header extends nothing |
| Value `3600`, a hung version probe or metadata lookup | Probe ends at 15 s, metadata at 60 s |
| Evidence harness with value `900` | Candidate archive downloads use D = 900 s |
| Default waiter behind a holder with D = 1800 s | The waiter fails at 360 s with the lock-wait diagnostic; the live holder's lock and staging are kept |

#### Recommended option for Q18 (with arguments for this choice)

Option A: it gives a user the exact duration a slow link needs, keeps the two
budgets Q05 B named coupled and finite, and leaves the probe, socket and
metadata budgets short enough to report a hang quickly. Reading the value once
and keeping every waiter's own deadline turn mixed configurations into an
ordinary, diagnosed lock-wait failure instead of an unbounded wait. Option C
would need a new explicit choice, since it widens Q05 B's scope.

#### Answer to Q18: option A (with reason why it must be accepted as the answer)

Option A: it implements the confirmed Q05 B with one exact, bounded and
validated value, without slowing the detection of any other hung stage.

User decision: confirmed: option A, `LLM_SHARED_GIT_CLIFF_DOWNLOAD_TIMEOUT_SECONDS`
as an exact download budget D from 300 through 3600 seconds with the caller's
own wait W = D + 60 s, other stage budgets unchanged, the value validated once
and refused when malformed or out of range, and each caller keeping its own
finite wait, selected by the user on 2026-11-14 without amendment. The 3600 s
ceiling is accepted as the operational limit, and a default waiter may expire
behind a raised holder without ever recovering it.
