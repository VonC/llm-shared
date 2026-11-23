# git-cliff provisioning

<img src="../assets/logo-llm-shared-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

The release engine never asks you to install git-cliff or to put it on PATH.
It downloads one tested git-cliff for Windows x64 into the executing llm-shared
checkout, checks it before every use, and runs it contained in a job of its
own. The `gcliff` launcher runs that git-cliff for the current worktree, with
your arguments, output, status and environment passed through.

## Invocation model

In this version, a person or a script calls `bin\gcliff.bat` directly; no
workflow calls it on its own yet. Its first call in a checkout downloads the
pinned git-cliff, so run `bin\gcliff.bat --version` once as a warm-up before an
offline session. The changelog generation and release preparation of later
items call the same provisioning through the release engine, never through
`gcliff`. No Doskey alias is loaded yet: `bin\gcliff.doskey` holds the macro
line that a later item copies into `senv.doskey`.

## Tested pin and pin selection

The shipped manifest admits git-cliff 2.14.2, its default, because the user
approved its evidence bundle `tools/release_workflow/git_cliff/bundles/2.14.2/`
on 2026-11-21. A project selects a pin in its `.release.ini`:

```ini
[git-cliff]
version = 2.14.2
```

| Declared value | Result |
| --- | --- |
| no `[git-cliff]` section, or no `version` key | the manifest default, 2.14.2 |
| an admitted `X.Y.Z`, such as `2.14.2` | that pin |
| a well-formed version the manifest does not admit, such as `2.15.0` | configuration error `not a tested git-cliff pin; tested: 2.14.2` |
| `v2.14.2`, `latest` or a prerelease | configuration error on the form: an exact `X.Y.Z` is required |
| `2.7.0` | configuration error: the 2.7.0 baseline of the evidence bundle is evidence-only, never a pin |

| Caller | Project used for the pin | Without a pin |
| --- | --- | --- |
| Engine operations (changelog, generated `pre`) | the validated project root of the operation | manifest default |
| `gcliff` inside a Git worktree | the worktree containing the current directory | manifest default, after the whole `.release.ini` is validated |
| `gcliff` outside any worktree (a plain directory, a bare repository, a `.git` directory) | none | manifest default |

The whole `.release.ini` is validated, every section, even for `gcliff`: an
invalid unrelated section, such as a broken `[source:npm]`, stops the call.
git-cliff's own arguments never choose the project, so `--workdir` or
`--repository` naming another repository select no pin. A Git discovery
failure other than "not inside a worktree", such as a dubious ownership
refusal, stops the call instead of falling back to the default.

## Running gcliff

```text
bin\gcliff.bat --version
bin\gcliff.bat --unreleased --output CHANGELOG.md
```

`bin\gcliff.bat` self-locates its checkout, reads that checkout's runtime
record like the release launchers, switches the console to code page 65001
for the call and restores it afterwards. git-cliff then receives:

| What | How |
| --- | --- |
| arguments | unchanged, rebuilt with the standard Windows command-line rules git-cliff parses |
| working directory | your current directory |
| standard input, output and error | inherited from your console or redirection |
| environment | your environment unchanged, `GIT_CLIFF_*` variables included; the parent console's variables and PATH are never changed |
| Ctrl+C | delivered to git-cliff, which decides how it stops; the launcher ignores it while git-cliff runs |

cmd rewrites `%`, `^`, `!` and `"` before a batch file sees them, so an
argument that still holds one of them is refused with status 69 and the
diagnostic `gcliff: an argument holds %, ^, ! or ", which the batch launcher
cannot pass safely; put such values in cliff.toml`. The alias fragment, once
loaded, defines:

```text
gcliff="%LLM_SHARED_DIR%\bin\gcliff.bat" $*
```

## Cache layout and its ignore rule

```text
<llm-shared checkout>\.tools\git-cliff\
  2.14.2\
    x86_64-pc-windows-msvc\            published entry, never modified in place
      git-cliff.exe
      entry.json                       local integrity record
    x86_64-pc-windows-msvc.lock        provisioning lock record, while held
    .staging-<pid>-<created>-<rand>\   one staging directory per attempt
    .retired-<pid>-<created>-<rand>\   an invalid entry moved aside
  evidence\                            evidence harness candidates only
```

The cache belongs to the executing checkout; there is no per-user or shared
location. llm-shared's root `.gitignore` holds `/.tools/git-cliff/`, so a
fresh checkout's first download leaves `git status` clean.

Every use reuses a valid entry without a lock and without writing: it opens a
use guard on `git-cliff.exe` (a read handle that refuses any rename or
replacement while open), reads `entry.json`, hashes the executable through the
guard, then runs `git-cliff --version`. A truncated or replaced executable, or
a missing record, makes the entry invalid before it runs; the next call
provisions it again under the lock. A read-only checkout with a valid entry
works normally; only provisioning needs write access.

## Network, proxy and certificates

The download comes from the GitHub release of the pin, which redirects to
`release-assets.githubusercontent.com`; both hosts must be reachable.

- Proxies come from `HTTPS_PROXY`, `HTTP_PROXY` and `NO_PROXY`, or from the
  static Windows proxy setting when no proxy variable is set.
- Certificates come from the Windows certificate store, so a corporate
  inspecting root that Windows trusts is accepted. Verification is never
  turned off.
- Not supported in this version: proxies that require authentication, proxy
  auto-configuration scripts and mirrors.

The archive must have the size and SHA-256 the manifest records; it is never
retried on a digest mismatch.

## Download budget variable

`LLM_SHARED_GIT_CLIFF_DOWNLOAD_TIMEOUT_SECONDS` sets the download budget D,
both attempts together. Unset, D is 300 s. A set value is a whole number of
seconds from 300 through 3600; an empty value, a sign, a fraction, a unit,
spaces or an out-of-range value is refused, never clamped, even when a valid
entry is cached. The wait for another caller's lock is W = D + 60 s.

| Value | D | W |
| --- | --- | --- |
| unset | 300 s | 360 s |
| `900` | 900 s | 960 s |
| `3600` | 3600 s | 3660 s |

One retry after 5 s follows a connection error, a reset, HTTP 429 or 5xx,
inside D; a `Retry-After` header extends nothing. The variable changes no
other budget: each socket operation keeps 30 s and each version probe 15 s.
Commands that need no git-cliff, such as `version` or `versions check`, never
read it.

## Messages on standard error

| Event | Message |
| --- | --- |
| download starts | `git-cliff 2.14.2: downloading git-cliff-2.14.2-x86_64-pc-windows-msvc.zip (7.1 MiB) from GitHub` |
| entry published | `git-cliff 2.14.2: ready at <entry directory>` |
| waiting for another caller | `git-cliff 2.14.2: waiting for provisioning by process <pid> since <time> (up to 360 s)` |
| valid entry reused | nothing |

Provisioning never writes to standard output, so git-cliff's output stays
exactly git-cliff's. A failure names the pin, the internal path, the stage and
its remedy, for example
`git-cliff 2.14.2 unavailable at <entry directory> (download stage): ...`.

| Stage | Remedy given |
| --- | --- |
| platform | Windows 10 or Windows Server 2016 and later, x64 only |
| containment | Windows refused to create the child inside its job; run from a console outside a host job that limits its processes |
| budget-setting | set the budget variable to a whole number of seconds from 300 through 3600, or unset it |
| configuration | use an llm-shared release whose manifest admits a tested pin |
| permission | grant write access to the named directory of the llm-shared checkout |
| lock-wait | another process holds the named lock; retry when it ends, or raise the budget variable |
| download | check access to both hosts through the proxy variables; on a slow link, raise the budget variable |
| verification | the asset does not match the recorded digest; retry, and report a persistent mismatch |
| extraction, probe | delete the named staging or entry directory, then retry |
| in-use | another release runs the binary being replaced; retry when it ends |
| reporting | the calling command's standard error could not be written; check its console or redirection |

## Statuses of gcliff and of the engine callers

| Caller | Status |
| --- | --- |
| `gcliff` | git-cliff's own status, unchanged (0 success, 1 a failing render, 2 a usage error, 101 a panic, or any other); `69` for any failure before git-cliff starts: readiness, configuration, argument guard, budget setting, platform, provisioning or a child Windows refused to create |
| engine operations | `2`, the setup and configuration class, when provisioning fails; the project is unchanged |

69 is the conventional "service unavailable" status. The evidence bundle's
audit of git-cliff 2.14.2's exit paths, at its `v2.14.2` source tag, shows that
git-cliff itself never returns 69, so a 69 from `gcliff` always means that
git-cliff did not start. A missing or invalid runtime record makes
`bin\gcliff.bat` print `Release readiness failed: ... Run this checkout's
setup` and return 69.

## Evidence bundle and its review

A version enters the manifest only with a committed evidence bundle that the
user approved. The bundle for 2.14.2 compares git-cliff 2.14.2 with the 2.7.0
baseline on llm-shared's own history and on a snapshot-tag fixture history,
with identical inputs for both versions: the frozen commit, the ranges, the
exact `cliff.toml` bytes, the flags and the environment. It records each
output's digest and status, the differing hunks with their classification
(intentional, with the upstream release-note reason, or a defect), the
exit-path audit and the user's review, which covers the digest of everything
the review saw. A unit test ties the manifest entry to that approved bundle.
The harness that builds a bundle runs by hand, outside the test suite.

Related: [Aliases and launchers](aliases-and-launchers.md#git-cliff-launcher),
[Automation and direct invocation](automation-and-direct-invocation.md#statuses-and-streams),
[Version sources](version-sources.md).
