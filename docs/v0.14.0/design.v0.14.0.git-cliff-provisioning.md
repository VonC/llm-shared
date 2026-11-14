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
exit-status numbers. The design decisions table at the end records its
eighteen choices.

## Scope and ownership of the v0.14.0 git-cliff provisioning design

The v0.14.0 outcomes of item 3 are:

1. A tested-pin manifest in llm-shared names every admitted git-cliff version
   with the published identity of its Windows x64 asset, and a `[git-cliff]`
   domain of the common reader admits only those versions.
2. One provisioning service returns an invocation object for a verified
   absolute `git-cliff.exe` of a pin, reusing a valid cache entry offline or
   downloading, verifying, extracting and publishing a new one under a bounded
   lock.
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
- Stage time budgets with the one download budget override, standard-error
  messages, statuses and diagnostics.
- The provisioning entry point and its invocation object, which items 4 and 5
  call.
- `bin/gcliff.bat`, its entry kind and the `gcliff` macro line, without an
  edit of the shared `senv.doskey`.
- The root `.gitignore` entry for the cache.
- The evidence harness as an internal comparison module with a developer entry
  point, the candidate lifecycle with the immutable 2.7.0 trust record, the
  exit-status audit and the committed evidence bundle that admits 2.14.2.

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
  -> budget policy: download budget D and own wait W = D + 60 s, read and
     validated once from the override variable (300/360 s when unset)
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
  -> the returned invocation object starts git-cliff as a contained child
     that inherits the guard, under the engine or passthrough environment
     policy, so the guard lasts as long as the child, even if the caller dies
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

The probe runs `git-cliff.exe --version` through the invocation object's
engine policy: standard input closed, output captured, the entry or staging
directory as working directory and an environment from which every
`GIT_CLIFF_*` variable is removed, so ambient git-cliff settings cannot affect
the check. The first output line must be
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
| Archive download D, both attempts together | 300 s, or the override value from 300 through 3600 s | One retry after 5 s for a connection error, a reset, or HTTP 429 or 5xx; none for another HTTP 4xx, a size overflow or a digest mismatch |
| Version probe | 15 s | None |
| Candidate metadata lookup, harness only, both attempts together | 60 s | One retry after 5 s under the same rules as the download, inside this budget |
| Waiting for another holder's lock, W | D + 60 s: 360 s by default, 3660 s at most | Not applicable |

The wait W is a finite contention policy for the caller's own D. It covers
that download budget, two probe budgets and about 30 s for extraction,
hashing, cleanup and publication, so a healthy holder with the same D normally
finishes first; a waiter still fails when the holder takes longer, including a
holder whose D is larger, and succeeds only when the holder completes within
the waiter's W (Q06, Q15). An expired budget reports the stage, deletes the
attempt's staging directory and releases the lock; the project is unchanged.
Every budget is an engine constant except the download budget, which one
documented environment variable can raise together with the caller's wait;
requirement Q07 excludes a mirror setting, not this override. The rendering
by git-cliff itself has no budget here; item 4 owns it.

### The download budget override

`LLM_SHARED_GIT_CLIFF_DOWNLOAD_TIMEOUT_SECONDS` sets D. It lies outside the
upstream `GIT_CLIFF_*` namespace, which the engine environment policy removes.

- Unset, D is 300 s. A set value is an ASCII decimal integer of seconds from
  300 through 3600 inclusive. An empty string, a sign, a fraction, a unit,
  whitespace or an out-of-range value is refused: it is never clamped and
  never replaced by the default. The 3600 s ceiling is an operational policy,
  not a bound the requirement derives.
- The caller's wait is W = D + 60 s: 300 and 360 s by default, 900 and 960 s
  for a 900 s value, 3600 and 3660 s at the ceiling.
- D and W apply to production provisioning and to evidence-candidate archive
  downloads and waits. The socket limit stays 30 s, every version probe 15 s
  and the harness metadata lookup 60 s.
- The value is read and validated once, when a caller enters provisioning or
  the evidence harness starts, before any reuse probe, child creation, network
  access or cache change; the resolved policy is passed to workers instead of
  being read again. An invalid value is a setup failure, status 2 for engine
  operations and 69 for `gcliff`, even when a valid cached entry exists.
  Operations that do not need git-cliff never read the variable.
- Every caller owns its finite W. A default 360 s waiter may time out behind a
  holder using D = 1800 s: its deadline is never reset or enlarged by a holder
  change, W = D + 60 s applies to the caller's own policy and not to the
  holder's environment, and a timeout never authorizes recovering a live or
  `UNKNOWN` owner.
- The retry count, its 5 s delay and the shared deadline stay inside D, and a
  `Retry-After` header extends nothing.

### Deadline enforcement

A `urllib` timeout bounds each blocking socket operation, not a whole
transfer, and does not cover name resolution, so a clock check between calls
cannot stop a call that never returns. Each download attempt therefore runs in
a worker process of the same runtime, started under the child lifecycle with
the URL, the attempt's staging file, the expected size and the remaining part
of the resolved budget D. The parent waits for the worker until the stage
deadline; on expiry it
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

The waiting line shows the caller's effective wait W, and every expiry
diagnostic shows the effective budget of its stage. Provisioning never writes
to standard output, so captured git-cliff output stays exactly git-cliff's
(Q08).

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
| Budget setting | Set `LLM_SHARED_GIT_CLIFF_DOWNLOAD_TIMEOUT_SECONDS` to a whole number of seconds from 300 through 3600, or unset it |
| Permission | Grant write access to the named directory of this llm-shared checkout |
| Lock wait | Another process holds the named lock; retry when it ends, or wait longer by raising `LLM_SHARED_GIT_CLIFF_DOWNLOAD_TIMEOUT_SECONDS` (300 through 3600 s) |
| Download | Check access to both hosts through the proxy variables; on a slow link, raise `LLM_SHARED_GIT_CLIFF_DOWNLOAD_TIMEOUT_SECONDS` (300 through 3600 s) |
| Verification | The asset does not match llm-shared's recorded digest; retry, and report a persistent mismatch |
| Extraction or probe | Delete the named staging or entry directory, then retry |
| In use | Another release runs the binary being replaced; retry when it ends |

No remedy asks the user to install git-cliff or change PATH, and the probe and
metadata remedies never suggest that the budget variable extends their
budgets.

### Statuses

| Path | Status on provisioning failure | Other statuses |
| --- | --- | --- |
| Engine operations | 2, the existing setup and configuration class | Unchanged |
| `gcliff` | 69, reserved for any failure before git-cliff starts: readiness, platform, configuration, budget setting, argument guard, provisioning or child containment | git-cliff's own status, unchanged |

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

The service is one call that takes the tooling root, the resolved pin, the
resolved budget policy and the injectable seams. It returns an invocation
object for the verified entry, or raises a provisioning error carrying the
stage, the path and the diagnostic.

The invocation object carries the verified executable path, its version and
the open use guard, and it is the only way a caller starts git-cliff. Each
start names one of two environment policies:

| Policy | Used by | Environment and streams |
| --- | --- | --- |
| Engine | Item 4 rendering, item 5 `pre`, the version probes, the harness comparison | Every `GIT_CLIFF_*` variable removed, standard input closed, output handled as the caller directs |
| Passthrough | `gcliff` | The user's environment, working directory and inherited standard streams |

Under either policy the object creates git-cliff under the child lifecycle,
inside the caller's kill-on-close job with the use guard in the child's
inherited-handle list, waits for it and returns its status. It closes its own
copy of the guard only after the child has exited, or at once when the
creation fails, since no child then exists. No caller can therefore forget
the environment rule, start an uncontained child or drop the guard. Item 4
keeps its rendering arguments, postprocessing and render timeout; the object
only owns how git-cliff is started.

Callers invoke the service after configuration validation and before their
first project write; the object's executable path is the launcher-local
`GIT_CLIFF` value of umbrella decision 20, never exported to a parent process.
The service creates no project file, takes no project lock and reads no
project state beyond the pin it receives.

Its seams are the download worker launcher, an executable probe, a clock with
a sleep function, the process-state probe, the use-guard opener and the
environment the budget policy is read from. Production
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

After selecting the project and pin and provisioning the binary, the launcher
starts `git-cliff.exe` through the invocation object's passthrough policy,
under the child lifecycle, with the user's arguments, inherited standard
input, output and error, the use guard, the user's working directory and the
user's environment. While it waits, the launcher ignores the
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

The harness is an internal comparison module of the release engine with a
developer entry point, run by hand outside pytest, because it downloads and
runs binaries and runs Git. It defines no public engine command: item 6, which
later proposes newer tested pins with their differences on a consumer's
history, reuses the module and decides its public form. It uses the same
download worker, extraction, probe, use guard and resolved budget policy as
provisioning, through candidate records instead of the manifest, and starts
both versions through the invocation object's engine policy. Its result is a
committed evidence bundle; unit tests and item 4 read the bundle without
running git-cliff.

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

The bundle is compact. It stores:

- the input manifest: every controlled input listed above, with its digest or
  hash;
- for each range and candidate, the SHA-256 digest and the exit status of the
  raw output;
- for each range whose outputs differ, the differing hunks with their context;
- a classification table in which every difference is marked intentional,
  with its upstream release-note reason, or a defect;
- the exit-path audit and the corroborating observed statuses described under
  the statuses section.

Identical outputs are not stored. A rerun from the recorded inputs regenerates
any output on demand, and its digest proves that the rerun reproduces the
recorded output; a rerun whose digest differs fails. Admission of 2.14.2 into
the manifest requires a complete classification without an open defect and an
audit that excludes 69. The bundle covers raw git-cliff output only; the
postprocessing of `update-changelog.sh` is item 4's recheck and item 8's
parity.

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
- The download budget override is resolved from a fake environment and
  checked with the fake clock: the default, an exact raised value, the
  ceiling, every refused form (also with a valid cached entry), operations
  that never read it, retry and `Retry-After` inside D, unchanged probe and
  metadata budgets, candidate downloads using D, and a default waiter timing
  out behind a raised holder without recovering it. No test waits in real
  time.
- The invocation object is checked with a fake child launcher: the engine
  policy removes every `GIT_CLIFF_*` variable and closes standard input, the
  passthrough policy keeps the user's environment and streams, and both pass
  the use guard and the job to the creation call.
- The network client is tested against a fake opener that returns canned
  bytes, redirects, stalls and HTTP errors.
- The launcher's batch file is covered by the existing launcher acceptance
  style, which simulates the process boundary.
- The evidence harness itself runs only by hand; tests check the committed
  bundle's structure (input manifest, output digests and statuses, hunks,
  classification and audit) and that the manifest's admitted pins reference
  it.
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
- The provisioning entry point resolves the budget policy once from
  `LLM_SHARED_GIT_CLIFF_DOWNLOAD_TIMEOUT_SECONDS` and passes it to workers and
  to the lock wait; nothing else in the engine reads the variable.
- The provisioning service returns the invocation object, which owns the
  engine and passthrough environment policies, the contained creation and the
  guard transfer; the evidence comparison is an internal module with a
  developer entry point.

## Acceptance cases for the git-cliff provisioning design

| Scenario | Expected outcome | Reason |
| --- | --- | --- |
| `.release.ini` without `[git-cliff]`, valid cached 2.14.2 | Invocation object returned, nothing printed, no lock, no network | Default pin and lock-free reuse |
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
| Parent dies during the creation of any child | Either no child exists, or the child is already a member of the job, which the parent's death closes and which ends it | No child ever exists outside its job (design Q17) |
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
| Harness rerun whose output digest differs from the bundle | Harness run fails | Compact, verifiable bundle |
| Engine start with `GIT_CLIFF_*` variables in the console | The engine policy removes them; `gcliff` passes them through | One place for the environment rule |
| Budget variable unset | D = 300 s, W = 360 s | Default budgets |
| Budget variable `900` | D = 900 s, W = 960 s | Exact raised budget |
| Budget variable `3600` | D = 3600 s, W = 3660 s | Ceiling |
| Budget variable empty, `-1`, `300.5`, `600s`, `600` with a leading space, `299` or `3601` | Setup failure naming the variable and its range; status 2, or 69 for `gcliff`; nothing provisioned | Refused, never clamped |
| Invalid budget variable with a valid cached entry | The same setup failure; the entry is not used | Validated before reuse |
| `version` command or ordinary build with an invalid budget variable | Unaffected; the variable is not read | Operations free of git-cliff |
| Budget `900`, first attempt reset, `Retry-After: 2000` | The 5 s delay and the retry stay inside 900 s; the header extends nothing | Retry inside D |
| Budget `3600`, a hung version probe or metadata lookup | Probe ends at 15 s, metadata at 60 s | Override limited to download and wait |
| Evidence harness with budget `900` | Candidate archive downloads use D = 900 s | Same policy for candidates |
| Default waiter behind a holder with D = 1800 s | The waiter fails at 360 s with the lock-wait diagnostic; the live holder's lock and staging are kept | Per-caller finite wait |

## Design decisions for git-cliff provisioning

The user decided each question after an explanation on 2026-11-14, and
independent review rounds 5 to 7 checked the decisions for consistency. The
question blocks, with their full options and arguments, are kept in the
commit `docs(design): record pre-consolidation questions`. In this table,
Qxx names a design question; elsewhere in this document, a bare Qxx in
parentheses names a requirement clarification.

| Question | Decision and reason | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | The manifest records each admitted asset's published SHA-256 at admission; provisioning compares downloads with it and never calls the GitHub API. Releases need only the two download hosts, and an asset replaced upstream fails as a mismatch | Manifest content and admission; Archive verification; Candidate lifecycle | Live digest from release metadata on every download (API host, quota, accepts a replaced asset); manifest plus live check with a warning (two sources, API dependency) |
| Q02 | The manifest is a table of frozen Python records in the release engine; admitting a pin is a reviewed code change and the reader parses no new file format | Manifest content and admission; The git-cliff domain of the common reader | TOML file validated on every configuration read; JSON generated from the evidence bundle (generation step, second artifact) |
| Q03 | A lock record published without replacement, a short transition mutex and the liveness probe, waiters polling every 250 ms; recovery and cleanup need the owner and every recorded cache-writing child `DEAD`, on a local-disk cache | Lock record and transition mutex; Recovery of a dead holder; Child process lifecycle | Kernel mutex held for the whole provisioning (second mechanism, abandonment proves only a thread ended); exclusive lock file (antivirus false contention) |
| Q04 | One lock per version and platform, with evidence candidates in their own lock namespace | Lock record and transition mutex; Candidate cache | One lock for the whole cache (unrelated downloads serialize) |
| Q05 | The budgets stay engine constants, plus one documented environment variable that raises the download and wait budgets; chosen by the user over the recommended fixed-only option. Requirement Q07 excludes a mirror setting, not this override, and every budget stays documented and finite | Time budgets and retries; The download budget override; Failure diagnostics | Fixed constants only (a slower link fails until a code change); budgets derived from the asset size (one more rule to explain) |
| Q06 | One retry after 5 s for a connection error, a reset, HTTP 429 or 5xx, inside the download budget; none for another HTTP 4xx, a size overflow or a digest mismatch; `Retry-After` never extends the deadline | Time budgets and retries; Deadline enforcement; Archive verification | No retry (one reset fails a release); up to three growing retries (more states, the budget ends outages anyway) |
| Q07 | A use guard, a read handle denying write and delete sharing, held from validation until git-cliff exits and inherited by every child that executes the entry; an invalid entry is replaced by renaming its executable first under the lock, with an in-use diagnostic when refused | Reuse check and the use guard; Publication; Child process lifecycle | Manual deletion only (a manual repair); immutable generation directories with a pointer file (every corrupted generation kept) |
| Q08 | `urllib.request.getproxies()` only: proxy environment variables, else the static Windows proxy; a script-configured machine gets the diagnostic naming `HTTPS_PROXY` | Network path; Failure diagnostics | WinHTTP through `ctypes` with auto-configuration scripts (new failure surface); environment variables only (static Windows proxy breaks) |
| Q09 | The entry point returns an invocation object with the engine policy (`GIT_CLIFF_*` removed, input closed) or the passthrough policy of `gcliff`; it owns the contained creation and the guard transfer, while item 4 keeps rendering arguments, postprocessing and timeouts | Target flow; Version probe; The provisioning entry point for items 4 and 5; Running git-cliff | Path only, each caller building its own start (the rule can be omitted); path plus a scrubbed environment mapping (wrong mapping still possible) |
| Q10 | The Python launcher starts git-cliff as a contained child with inherited streams and the use guard and returns its status unchanged; the batch-argument guard stays | Launcher and entry kind; Running git-cliff | Batch file running the resolved path with raw `%*` (two-step status protocol); `os.execv` (loses the status on Windows) |
| Q11 | Status 69 for any `gcliff` failure before git-cliff starts, holding only with each admitted version's exit-path audit; a version able to return 69 stops admission | Statuses; Outputs and classification | 3 (already incomplete restoration for releases); 255 (a generic fatal status) |
| Q12 | Evidence candidates live in the `evidence/` subtree of the cache with their own namespace; a cached candidate runs only after its entry matches the immutable trust record and its executable matches the entry | Layout below the fixed path; Candidate cache | A sibling evidence tree (second ignore entry); a temporary directory per run (downloads every time) |
| Q13 | The bundle stores the input manifest, output digests and statuses, differing hunks with context, the classification and the exit-path audit; identical outputs are regenerated from the controlled inputs | Outputs and classification; Testing approach | Every raw output (about 400 KB, growing per pin); the classification table only (nothing to verify against) |
| Q14 | A committed script fixes every object-producing input of the snapshot-tag fixture, and the bundle records the resulting commit and tag hashes; a regeneration that differs fails the run | Frozen inputs and the coverage matrix | A committed `git bundle` (binary, unreadable in review); no fixture (contradicts requirement Q13) |
| Q15 | The harness is an internal comparison module with a developer entry point; item 6 decides its public form | The harness; Foundation changes | A developer-only script (item 6 rewrites it); a public engine command now (contract before item 6's needs) |
| Q16 | A tested single-line alias fragment beside the launcher; item 8 copies it into `senv.doskey` | Alias definition | Documentation only (untested, easy to mistype); a separate macro file loaded later (second alias file for consumers) |
| Q17 | Every child is created suspended with an explicit inherited-handle list and creation-time membership in a parent-only kill-on-close job; cache-writing children are recorded before resume, reuse probes are record-free and guarded, children end at their deadline, and recovery waits for every recorded actor to be `DEAD`. Windows 10 or Windows Server 2016 is the baseline, and a refused nesting fails closed | Child process lifecycle; Deadline enforcement; Foundation changes; Testing approach | Self-limiting workers through `subprocess` (a hung probe or run can outlive its parent); a third-party cancellable transport (new dependency); socket timeouts with clock checks (name resolution not covered) |
| Q18 | `LLM_SHARED_GIT_CLIFF_DOWNLOAD_TIMEOUT_SECONDS` sets an exact download budget D from 300 through 3600 s, refused when malformed or out of range; the caller's wait is D + 60 s; socket, probe and metadata budgets stay fixed; the value is validated once before any work, and each caller keeps its own finite wait | The download budget override; Time budgets and retries; Failure diagnostics; Statuses; Acceptance cases | A 1 to 12 multiplier for download and wait (coarse steps that move with the base); a 1 to 12 multiplier for every stage (widens Q05, slows unrelated hang detection) |
