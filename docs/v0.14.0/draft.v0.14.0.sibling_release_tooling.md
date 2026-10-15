# The Release Desk Next Door

- Type: collection (feature-requests and issues)
- Draft role: umbrella
- Target version: v0.14.0
- Documentation layout: docs/v0.14.0/
- Umbrella slug: sibling_release_tooling

## Why this effort exists

Version and changelog management (`version.txt`, `CHANGELOG.md`, the
`-SNAPSHOT` to release switch, the annotated `vX.Y.Z` tag and its `[valid]`
marker) lives today in [`senv_dev_workflow`](https://github.com/VonC/senv_dev_workflow),
mounted as a `tools/dev_workflow` submodule in each project that wants `brel`.

That model has three costs:

- every consumer carries a pinned copy (llm-shared pins `f90bfc6`, my-project
  pins `5720c4b`: they already differ, only by the `uv`/`uver` alias rename);
- the submodule brings two nested submodules (`batcolors` on `legacy`,
  `shcolors` on `linux`), which my-project's Linux deployment then has to
  initialize on every host;
- a repository without the submodule gets nothing: workspace-halo has
  `version.txt`, `CHANGELOG.md` and `vX.Y.Z` tags, but its release commits say
  "this repository has no brel step" (`7ed242e chore(release): set version
  0.0.24`), so the `-SNAPSHOT` drop was done by hand.

Meanwhile every one of those repositories already expects `..\llm-shared` as a
sibling: my-project's `senv.bat` loads `..\llm-shared\senv.doskey`, and
workspace-halo's `senv.bat` resolves `..\llm-shared` for `pwiki`. llm-shared
already carries `tools/batcolors` as a submodule.

The goal: absorb the version and changelog features of `dev_workflow` into
llm-shared, so that `b` / `br` / `brel` work in any repository simply because
`..\llm-shared` sits beside it, with a clear warning when it does not. Then
remove the `tools/dev_workflow` submodule from llm-shared and my-project, and
give workspace-halo the same release flow without adding anything but a few
lines to its `build.bat`, installed by a dedicated setup skill. Once the engine
exists, a confirmed merge to `main` can carry the release through its build
gate and annotated tag, instead of always stopping before `brel`.

## Settled so far

- The engine is a Python rewrite behind a batch launcher, not a port of the
  batch and bash scripts (see "Engine in Python").
- llm-shared downloads the pinned git-cliff release from GitHub automatically
  when needed and absent from its ignored internal cache. It calls that exact
  executable without PATH discovery or any senv dependency; `gcliff` is also
  exposed as an llm-shared convenience alias.
- `version.txt` is authoritative. Version transitions replace only its first
  token and preserve the title and release-notes body; all supported secondary
  sources are synchronized and checked according to their ecosystem form.
  Python and default npm sources retain `X.Y.Z` when the anchor has
  `X.Y.Z-SNAPSHOT`; one project can use several ecosystems at once.
- The engine always receives and validates an explicit consuming-project
  root. Build scripts derive it from their own directory; interactive aliases
  resolve the current Git worktree. Inherited `PRJ_DIR` is diagnostic context,
  never a fallback target, and `LLM_SHARED_DIR` identifies tooling only.
- `build.bat rel` is a transaction around the consuming project's own gate:
  preflight, release versions and changelog, commit, annotated tag, build,
  then `[valid]`. Recovery restores only state owned by that transaction.
- Per-project settings live in a small `.release.ini` at the project root.
- Project fix rules move to `.changelog-fixes.toml`, created from an existing
  `.changelog.fixes` automatically by `/prepare-release`. `convert` remains
  a maintenance command; ordinary preparation requires no manual conversion.
- Feature-to-umbrella merges never tag. Confirm umbrella-to-`develop` merges
  and allow several completed umbrellas to accumulate there. A separately
  confirmed merge to `main` automatically starts the release lifecycle after
  preparation and readiness checks; only `main` can receive a release tag.
- Version-source formats are registered in an explicit tuple in
  llm-shared's `tools/release_workflow/sources/__init__.py`, with a test that
  fails when a format module is missing from it. Consumers do not copy it;
  adding an adapter and its tests extends every consumer.
- The unreleased changelog heading carries no commit hash, and
  `filter.changelog` is dropped.
- `pyproject.toml` and `uv.lock` state plain `X.Y.Z` during the snapshot, as
  Step 12 does today.
- By default llm-shared is found as `%~dp0..\llm-shared` first, with a valid
  `LLM_SHARED_DIR` as fallback. An explicitly selected upgrade checkout must
  actually execute instead of being shadowed by that default discovery.
- The release tag message records the llm-shared revision actually used.
  An upgrade alias and preparation stage propose updating llm-shared before
  capturing that value; an outdated checkout gets an actionable update offer.
- Root `CHANGELOG.md` holds recent releases and the current snapshot; explicit
  version ranges in `.release.ini` assign older releases to
  `docs/CHANGELOG.vA.B.C-vD.E.F.md`. Authors can revise those ranges.
- Snapshot tags are development markers, never release boundaries or release
  cancellation targets. All new Python range readers share this distinction.
- my-project's `tools\batcolors` and `tools\shcolors` become junctions to the
  sibling, created by `senv`.
- This effort covers the llm-shared engine, reusable setup/upgrade tooling,
  the `/prepare-release` integration and llm-shared's own migration. my-project and workspace-halo
  are tracked as efforts in their own repositories; their sections below stay
  as input for those efforts.
- llm-shared's Diataxis pages document the migration. `senv_dev_workflow` is
  archived only after llm-shared and my-project have both migrated, with a short
  README pointing to those pages. llm-shared is the first consumer and its
  `v0.14.0` release is made by the new engine.

The 2026-10-15 review adds the behavioral contracts below to the existing
eight requirements. They specify outcomes and boundaries, not a storage
format, compatibility protocol, installation mechanism or synchronization
algorithm. The user confirmed Q1 A, Q2 A, Q3 A and Q4 A on 2026-10-15;
those policy choices are reflected throughout and recorded at the end.
Implementation details remain for each child's design.

## Version notation used throughout this draft

| Context | Form | Example |
| --- | --- | --- |
| `version.txt` first token, version-setting arguments, config bounds | `X.Y.Z` or `X.Y.Z-SNAPSHOT`, without `v` | `0.14.0-SNAPSHOT` |
| Python metadata/uv root and default npm manifest/lock | `X.Y.Z`, even during snapshots | `0.14.0` |
| Maven and configured snapshot sources | Same suffix state as the anchor, without `v` | `0.14.0-SNAPSHOT` |
| New release Git tag, generated release heading, release commit subject | `vX.Y.Z` | `v0.14.0` |
| Existing optional snapshot Git tag | `vX.Y.Z-SNAPSHOT`; also recognize legacy unprefixed spelling | `v0.14.0-SNAPSHOT` |
| Draft target labels, effort paths, archive filenames | `vX.Y.Z` | `docs/v0.14.0/`, `CHANGELOG.v0.1.0-v0.13.9.md` |
| git-cliff config pin / upstream GitHub tag | `X.Y.Z` / `vX.Y.Z` | `2.14.2` / `v2.14.2` |

Generated snapshot headings use `vX.Y.Z-SNAPSHOT` for display; that heading
does not imply a Git tag exists. Curated changelogs may retain their documented
unprefixed heading style. Legacy unprefixed stable tags remain readable;
new stable tags always have `v`. A CLI argument selecting a tag uses its actual
tag spelling; an argument setting a project version never includes `v`.

## What dev_workflow provides today

About 2,600 lines, most of it Windows batch calling Git Bash tools (`bash`,
`sed`, `awk`, `perl`, `cygpath`) and `git-cliff`.

| Piece | Role today | Proposed fate |
| --- | --- | --- |
| `init.bat` | Checks nested submodules, junctions `batcolors` into the parent `tools\`, requires `PRJ_DIR`, `PRJ_DIR_NAME` and `changelog-header.md`, sets `filter.changelog`, defines doskey aliases, exports path variables | Removed; each duty moves, see the next section |
| `get-version.bat` | Parses `version.txt` line 1 into `project_version`, `project_title`, `project_release_notes`; writes `0.1.0-SNAPSHOT` when the file is missing | Engine `version` command |
| `update-version.bat` (580 lines) | Snapshot/release state machine: git describe, dirty filter, next-snapshot prompt (fix/minor/major), title and description prompts, release commit, annotated tag | Engine core |
| `t_build.bat` | `:pre-processing` parses `rel`, `snap`, `rel_title...`, `prj_error` and calls update-version; `:post-processing` marks the tag `[valid]` or cancels the release (`reset @~1`, `tag -d`) | Engine `pre` and `post` commands |
| `update-changelog.bat` + `.sh` | git-cliff run, sed clean-ups, `version.txt` body injected under the unreleased heading, header prepended, section labeling, `.changelog.fixes` | Engine `changelog` command, git-cliff kept, sed dropped |
| `cliff.toml` | Commit groups, skipped release chores | Moves to llm-shared as the default, a project `cliff.toml` overrides it |
| `changelog_duplicate_version_section_remover.awk`, `changelog_section_labeler.awk` | Changelog post-processing | Rewritten in Python, awk dropped |
| `update-changelog.fixes.tpl.pl` | Runs `.changelog.fixes` through Perl `s///gee` | Replaced by a Python rules runner, Perl dropped (see "Changelog fixes without Perl") |
| `git/dirty-status-filter.pl`, `git/exempt-files.txt` | Dirty check that ignores release files plus a project `.exempt-files` | Rewritten in Python, Perl dropped |
| `t_build_maven.bat`, `mvn_get_version.ps1` | `pom.xml` get, set, check-snapshot | Maven version-source plugin |
| `t_build_npm.bat` | `package.json` get, set, check-snapshot | npm version-source plugin |
| `git/update-tag-message.*`, `git/release_reader.awk` | Rewrites a tag message from a file | Its `source "../../src/echos/echos"` does not resolve: port only if still used |
| `git/git_config.bat` | Adds a git config key if missing | Not called by anything in the three repositories: drop |
| `get_date.sh`, `get_day_index.ps1` | Date helpers | Not called: drop |
| `templates/*.tpl.*` | Project scaffolding (`senv`, `init`, `build`, `all`, `run`, `senv.local`, changelog header, fixes) | `init.tpl.bat` dropped; a new `build` snippet and the header template move to llm-shared `templates/` |
| `batcolors/`, `shcolors/` | Nested submodules for colored echos | llm-shared `tools/batcolors` (exists), plus a new `tools/shcolors` submodule on the `linux` branch of the same repository |

After the rewrite, the engine uses llm-shared's Python and Git, plus git-cliff
only for generated changelogs: no `bash`, `sed`, `awk`, `perl` or `cygpath`.

## Where each init.bat duty goes

The aim is that no project needs an `init.bat` at all.

| Duty in `init.bat` | New home |
| --- | --- |
| `chcp 65001` | The llm-shared release launcher, around its own run |
| `batcolors` junction into the parent `tools\` | Gone: llm-shared scripts load `%LLM_SHARED_DIR%\tools\batcolors`; see my-project below for its own scripts |
| `PRJ_DIR` / `PRJ_DIR_NAME` required | The engine receives the project root as an argument from the project `build.bat` (`%~dp0`), and derives the name itself |
| `changelog-header.md` required | Checked only by the `changelog` command, and only in generated-changelog mode |
| `filter.changelog` git config | Written in all three repositories' `.git/config`, but no `.gitattributes` maps `CHANGELOG.md` to it: dead today. Dropped, since the heading it was meant to clean no longer carries a hash (see "No hash in the snapshot changelog heading") |
| Aliases `b`, `brel`, `br`, `crel`, `gv`, `uc`, `uver`, `uverr`, `uvf` | llm-shared `senv.doskey`, pointing at llm-shared launchers |
| Aliases `a`, `t`, `s`, `i`, `p`, `d`, `r`, `senv`, `lsenv`, `usenv`, `psenv`, `hsenv`, `hlsenv`, `psenve`, `cdp`, `fsenv` | Stay with each project `senv.bat` (workspace-halo already defines its own `i`, `cdp`, `fsenv`) |
| `VERSION_TXT_FILE`, `POM_FILE`, `PACKAGE_JSON_FILE`, `HEADER_CHANGELOG_FILE`, `DEV_WORKFLOW_DIR`, `PRJ_DIR_unix` | Computed inside the engine from the project root; no environment variable to export |
| `local_path` / `local_path_msg` | Computed and never read: drop |

### PRJ_DIR without init.bat

The inspected llm-shared `senv.bat` lines 18 to 20 normalize its own `%~dp0`
into `PRJ_DIR` and derive `PRJ_DIR_NAME` from that directory's basename. These
assignments precede the `NO_MORE_SENV_%PRJ_DIR_NAME%` guard at line 34; even a
guarded call refreshes these identity values. The existing draft records the
same convention for my-project and workspace-halo; their migrations must
verify their own scripts. `build.bat` lines 39 to 43 derives `build_dir` from
its own script path, calls that project's `senv.bat`, then invokes release
preprocessing. The engine must not repeat that activation.

Environment values live in the process that sets them. Calling `senv.bat` in
an interactive cmd session updates that session; a child process inherits a
copy at launch and cannot update its parent. `cd` never refreshes identity.
New shells can inherit another project's values, and linked worktrees have
different roots even though they share Git objects and tags. Doskey macros
are per-console and are not a subprocess API. Calling a batch file from
PowerShell runs it in a child cmd process: its assignments do not update the
parent PowerShell environment. Independent tool calls cannot assume a prior
activation survived.

| Caller | Target selection | Missing or stale `PRJ_DIR` |
| --- | --- | --- |
| Engine and standalone launcher | Required explicit `<root>`; normalize it and require it to equal `git -C <root> rev-parse --show-toplevel` | Missing is allowed; stale is reported, but the validated explicit root wins. Missing or invalid explicit root fails without mutation; never infer a target from `PRJ_DIR` |
| `b`, `br`, `brel`, `crel`, `gv`, `uc`, `uver`, `uverr`, `uvf` aliases | Dispatch through a shared launcher, resolve the current directory's Git top-level, pass that root explicitly | Warn on mismatch, name both roots, then target the current worktree. Outside a Git worktree fail; never run the old environment's project |
| Project `build.bat` | Its own directory, validated as the worktree root, irrespective of caller directory | Call its own `senv.bat` once before preprocessing to refresh identity; pass the script-derived root anyway |

All project files, config, artifacts and Git operations resolve against that
root; every Git invocation supplies `-C <root>` or an equivalent explicit
working directory. Reject nested foreign repositories and paths outside the
selected worktree for managed files. Derive the project name from the root;
do not accept a stale `PRJ_DIR_NAME`. Keep `LLM_SHARED_DIR` separate: in
llm-shared itself both roots can coincide, but in a consumer they do not.
The shared launcher resolves its tooling root from its own location, rather
than trusting an inherited variable naming another checkout.

For interactive cmd use, initialize the chosen project's environment by
calling its root `senv.bat`. If inherited guards left required build tools
uninitialized, the caller clears that project's guard and activates it in
the same cmd process, following `rules/run_commands.md`. For PowerShell and
automation, invoke the full-path shared launcher with an explicit root, or
invoke the project's full-path `build.bat`, which owns its build environment.
The release engine itself never calls project or global `senv.bat`.

Alias semantics are explicit: `b` runs the ordinary consuming build; both
`br` and `brel` run its `rel` lifecycle (the inspected legacy aliases already
agree on that). `gv` reads the current version; `uc` and `uvf` refresh generated
changelog content or validate curated content; `uver` selects the separate
next-snapshot transition. `uverr` routes release intent through the consuming
build gate, rather than leaving a release permanently unvalidated. `crel`
routes to ownership-checked recovery of an active unvalidated transaction;
it must never port the legacy alias that resets/deletes the newest tag,
including an already valid release.

This also fixes the legacy `update-changelog.sh` Git calls that depend on the
current directory instead of `PRJ_DIR` (`show-ref`, `cat-file`, tag enumeration
and `describe`). Root validation and subprocess targeting must be covered for
directory changes, separate shells, subprocesses and linked worktrees.

## Target shape in llm-shared

### Engine and launchers

- `tools/release_workflow/` (working name): the version, release and changelog
  logic, with tests under `tests/`, like the other llm-shared tools.
- `bin/release_workflow.bat`: the launcher. It locates llm-shared from its own
  path and uses the bundled venv Python, the way `bin/mds.ps1` already does for
  `pwiki`, so workspace-halo (a Node and Go project, no Python on `PATH`) can
  call it.
- Commands: `pre <root> [build args]`, `post <root> <build status>`,
  `version <root>`, `changelog <root> [latest|vX.Y.Z]`, `snapshot <root>`,
  `versions <root> list|set <version>|check`,
  `fixes <root> init|convert|dry-run`, `recover <root>`.
- Every command that can prompt (dirty tree, next snapshot, release title)
  also takes a non-interactive form that fails with a message instead of
  asking, so `/prepare-release` can drive it from its own menus. Propagate the
  non-interactive option through dispatch, build, `pre` and `post`; do not
  reintroduce a batch `set /p` or a toolchain prompt downstream.
- `pre` must hand variables back to the calling `build.bat` (`project_version`,
  `project_title`, `build_params`, `build_params_echos`, `build_must_fail`,
  `PRJ_REL_TITLE`). A Python process cannot set its parent's environment, so the
  engine writes escaped `set` lines to a unique transaction-specific handoff
  batch file in the project artifact home (default `.reviews`, configurable).
  The launcher calls then deletes it. Values and arguments must survive spaces,
  quotes, `%`, `!`, `&` and other batch metacharacters without executing notes
  or titles as commands; failure produces no partially usable handoff.

### Supported platforms and runtime readiness

The v0.14.0 release tooling supports Windows x64 only initially, covering
launchers, the release lifecycle, git-cliff provisioning and setup/cutover.
Other operating systems and architectures require later scope. Existing Unix
deployment references do not extend this release-tooling support. Unsupported
platforms must receive a clear scope diagnostic before project mutation.

The selected llm-shared checkout must have a usable Python environment with
the dependencies required by its executing revision. Setup and upgrade must
check that readiness; the presence of a checkout or a Python executable alone
does not establish it. Setup and upgrade reuse llm-shared's setup process to
prepare or repair its own Python environment and required dependencies. An
accepted setup/upgrade must produce runnable tooling. Release operations use
the validated environment and stop before project mutation when it is unavailable. They
must not fall back to the consuming project's Python or require Python on
its PATH or repair their own environment mid-release. Runtime installation
details remain design work; the engine's existing prohibition on activating
project/global senv still applies.

### Automatic git-cliff provisioning

llm-shared owns downloading and caching git-cliff. The earlier external
installation/discovery proposal is superseded by the comments on this draft.
The observed global-senv binary is 2.7.0, but neither it nor global senv is a
runtime dependency. A release user does not need to know the dependency exists.

Read an exact `[git-cliff] version` from the consuming project's `.release.ini`,
or the tested llm-shared default when omitted. The proposed default is 2.14.2,
subject to the compatibility checks below. Never resolve a floating `latest`
during a release. The fixed location for that pin and platform is
`<LLM_SHARED_DIR>/.tools/git-cliff/<version>/<platform>/git-cliff.exe` on the
supported Windows x64 platform. Ignore the cache in llm-shared Git.
Versioned directories let consumers with different pins share one clone.

`GIT_CLIFF` is a launcher-local value computed from this internal path, not an
external override. No executable setting belongs in `.release.ini`; no PATH,
`PRGS`, global-senv, alias or machine installation discovery is performed.
Invoke the absolute executable directly and leave the parent's PATH and
environment unchanged. llm-shared supplies `bin/gcliff.bat` and the `gcliff`
alias in its alias set, both using this same resolver/downloader. The alias is
available to every user who loads llm-shared aliases, including without global
senv; scripts call the launcher directly, since doskey aliases do not expand
in subprocesses. Within a project the alias uses its pin; outside one it uses
the llm-shared default.

Before generated changelog work:

1. Check the selected cache path and executable version. Reuse a valid copy
   without network access.
2. If absent or invalid, obtain the matching OS/architecture release asset
   from `orhun/git-cliff` on GitHub, verify its published integrity information,
   and extract safely into a unique temporary cache directory. The supported
   platform contract must define the integrity check for each asset; do not
   assume every asset has a `.sha512` sidecar. For example, 2.14.2 lists those
   for tarballs but not Windows ZIPs; the inspected x86_64 MSVC ZIP has a SHA-256
   digest in GitHub's asset metadata. Verify that digest where available;
   missing verification data is an explicit setup failure.
3. Validate `--version`, then publish the cache entry atomically under a
   per-version/platform lock. Concurrent releases must not consume partial
   installs or replace a binary another release is using.
4. If the fixed binary still cannot be made available, stop with the requested
   version, internal path and download/verification/execution diagnostic.
   Explain the llm-shared setup, network or permission failure; do not ask the
   user to install git-cliff or configure PATH manually.

Provisioning occurs before any consuming-project managed-file, index, commit
or tag mutation. Cache writes are the explicit exception to keeping consumer
temporary state out of llm-shared. Generated mode means only that changelog
text is rendered from Git commits using git-cliff; it is not a separate version
or release lifecycle. Therefore `changelog` and generated release `pre` need
this dependency, while `version`, `versions list|set|check`, `snapshot`, ordinary
builds, curated validation and fix-rule conversion do not. `fixes dry-run`
uses existing text. A snapshot command does not regenerate a changelog.

#### 2.7.0 compared with the latest stable release

Upstream checked on 2026-10-09: the GitHub latest-release endpoint identifies
[2.14.2, published 2026-09-18](https://github.com/orhun/git-cliff/releases/tag/v2.14.2).
[2.7.0 was published 2024-11-20](https://github.com/orhun/git-cliff/releases/tag/v2.7.0).
The following changes matter to this engine; this is release-note and existing
`cliff.toml` inspection, not evidence of a completed binary parity run.

| Releases since 2.7.0 | Relevant changes | Consequence for llm-shared |
| --- | --- | --- |
| [2.8.0](https://github.com/orhun/git-cliff/releases/tag/v2.8.0), [2.9.0](https://github.com/orhun/git-cliff/releases/tag/v2.9.0) | Subdirectory/config discovery, monorepo include-path changes, worktree path fix, custom-range/submodule fixes, `require_conventional` | Exercise explicit roots, linked worktrees and nested repositories; keep config and range explicit |
| [2.10.0](https://github.com/orhun/git-cliff/releases/tag/v2.10.0) | Breaking change to empty default header/footer; include/exclude paths in config; skip-tag evaluation fix | Specify header/footer deliberately and compare generated bytes; skipping a tag must not accidentally discard its commits |
| [2.11.0](https://github.com/orhun/git-cliff/releases/tag/v2.11.0), [2.12.0](https://github.com/orhun/git-cliff/releases/tag/v2.12.0) | Unmatched-commit failure option, regex template filters, offline and `--skip-tags` CLI options; Azure DevOps template variable renamed | Useful controls, but opt in deliberately; audit any consumer remote templates and preserve the engine's own release-tag selection |
| [2.13.0](https://github.com/orhun/git-cliff/releases/tag/v2.13.0) | More config locations, configurable commit-processing order, per-commit statistics and offline environment support | Avoid ambient config/order changes; keep rendering local unless remote metadata is explicitly required |
| [2.14.1](https://github.com/orhun/git-cliff/releases/tag/v2.14.1) | Breaking config discovery, multi-value CLI parsing and remote PR-author field changes; graph-reachability release assignment, Windows path matching and nested annotated-tag fixes | Recheck command arguments, merge histories and custom templates; explicit config limits discovery surprises |
| [2.14.2](https://github.com/orhun/git-cliff/releases/tag/v2.14.2) | Multiple commit parsers can apply; all fields of a parser must match; `--workdir` include-path fix | Compare grouping, skip rules and security-body matches in the existing ordered parser list, not just successful execution |

| Pinning policy | Pros | Cons |
| --- | --- | --- |
| Exact `version = 2.14.2` in `.release.ini` (recommended for this cutover) | Reproducible binary, recent worktree/Windows/range fixes, automatic first-use install, reviewable upgrades | Newer parser/default behavior can change output; compatibility fixtures and a deliberate later pin update are required |
| Retain exact `2.7.0` temporarily | Closest comparison with the observed old tooling | Misses subsequent fixes/features; requires a second tested compatibility target if supported beyond migration evidence |
| Floating `latest` on each run | Gets new upstream changes without editing config | Output and CLI behavior can change without project review; network dependence and hard-to-reproduce releases; rejected |

Use 2.14.2 as the proposed initial pin and test the real llm-shared header,
template, parser/skip rules, snapshot-tag history and archive ranges against it.
Document intentional differences from 2.7.0 before cutover. Later setup/upgrade
checks can propose a newer tested exact pin with its diff; ordinary release
runs never silently move the pin. No binaries are installed by this draft edit.

### Project build.bat contract

The integration surrounds the project's own gate; it never replaces pytest,
npm, Maven or other project build/test commands with an engine-defined gate.
`%~dp0` identifies the consuming project, which calls its own `senv.bat` before
`pre`. A consumer defaults to `..\llm-shared`, with a validated `LLM_SHARED_DIR`
fallback; the explicit upgrade-selection contract below can select another
checkout. llm-shared's own build uses its own launcher. Compatibility is
checked before release mutation. The illustrative contract below shows the
required ordering; the implementation must preserve parameters and status:

```bat
set "project_root=%~dp0."
call "%~dp0senv.bat"
if errorlevel 1 exit /b 2
set "release_workflow="
for %%i in ("%~dp0..\llm-shared") do (
  if exist "%%~fi\bin\release_workflow.bat" set "LLM_SHARED_DIR=%%~fi"
)
if exist "%LLM_SHARED_DIR%\bin\release_workflow.bat" (
  set "release_workflow=%LLM_SHARED_DIR%\bin\release_workflow.bat"
)
if not defined release_workflow (
  echo WARNING: no ..\llm-shared found: no version or changelog management.
  if /i "%~1"=="rel" ( echo FATAL: brel needs ..\llm-shared & exit /b 2 )
)
if defined release_workflow (
  call "%release_workflow%" pre "%project_root%" %*
  if errorlevel 1 exit /b 2
)
rem ... the project's own build (pytest, npm, mvn) ...
rem Capture its exit code immediately as build_status.
if defined release_workflow (
  call "%release_workflow%" post "%project_root%" %build_status%
  if errorlevel 1 exit /b 2
)
exit /b %build_status%
```

Here "missing-tooling branch" means the `if not defined release_workflow`
conditional above, not a Git branch: the llm-shared launcher was not found.
That conditional must recognize release/snapshot requests among all
arguments, not just `%~1`; the shown first-argument check is illustrative only.
Missing tooling permits an ordinary build with one warning and a read-only
version display, but blocks any requested release or snapshot transition.
`pre` failure prevents the gate. Every gate outcome is passed to `post`;
successful gate plus failed postprocessing is still a failed release. Preserve
the original build failure code in diagnostics when recovery also fails.
`pre` and `post` must exchange a transaction identity through the launcher
handoff; `post <root> <status>` consumes only that root's active transaction,
never infers ownership from a matching version or the latest commit subject.

A dedicated `setup-release-tooling` skill and its repeatable helper install or
migrate this integration and generate `.release.ini` for the user. They inspect
the existing build and retain its gate, produce the real project-file changes,
and validate ordinary, failing and release argument paths. The illustrative
snippet is not a requirement for users to edit batch files manually. See
"Setup, migration and tooling upgrades" for the full adoption contract.

### Release readiness, lifecycle and recovery

These rules replace the legacy unqualified `reset @~1` cancellation behavior.
Release processing is a local transaction; it never pushes commits or tags.

1. **Preflight before project mutation.** Validate root, configuration, tooling
   compatibility, Git availability, commit/tag identity, the `main` branch,
   absence of an in-progress merge/rebase and competing release transaction,
   a valid `X.Y.Z-SNAPSHOT` token, a nonempty title after `--`, and nonempty
   notes in `version.txt`. Validate every detected source and its expected
   snapshot form, fix rules and changelog inputs. Check that neither `vX.Y.Z`
   nor legacy `X.Y.Z` exists, including valid or unvalidated tags: these spellings
   identify the same release version. Never create a second release of that
   version or replace an existing tag during preparation. Require the target
   version to be higher than every eligible reachable stable release on main.
   Lower maintenance releases require a later, separate policy. With no eligible
   stable release, retain the existing full-relevant-history behavior.
   Generated mode provisions/checks git-cliff and renders candidate output before project writes;
   curated mode checks its existing release section. Check all writable paths
   and report the exact files and version transitions.
2. **Preserve the baseline.** Default release readiness requires a clean tree
   apart from configured non-release artifacts. Retain `.exempt-files` as an
   explicit policy, with no blanket exemption for edited release inputs.
   Dirty managed release files or pre-existing staged changes to them fail
   before mutation; prepare and commit them first. An explicit dirty-policy
   opt-in may allow unrelated user changes, including staged ones, only when
   they can be preserved. Non-interactive mode never prompts or silently
   enables this opt-in. Capture the exact original branch/HEAD, managed-file
   bytes and existence, relevant index state, and tag absence in a durable
   transaction record before the first write. Unrelated changes are never
   staged into a release or discarded.
3. **Prepare the release.** Change only `version.txt`'s version token to
   `X.Y.Z`, synchronize the applicable sources and lock entries, and generate
   the dated release changelog or validate the curated section. Validate the
   resulting versions and output again. Commit only the enumerated release
   paths, including affected changelog archives, as
   `chore(release): set new 'vX.Y.Z'`. Create an annotated `vX.Y.Z`
   tag pointing to that exact commit, using the existing title and notes with
   the release date and tooling trailer. It has no `[valid]` marker yet.
4. **Run the consuming gate.** The project's build/test gate runs against the
   release-form files. No next snapshot is created during this phase. Record
   its actual result; a failed gate cannot yield a valid tag.
5. **Finalize success.** Only `post` for this transaction and a zero gate
   result may append a standalone `[valid]` line to its annotated tag. Confirm
   HEAD, managed files and the tag still identify the prepared release;
   unexpected gate edits to release files prevent validation. Retain the
   target commit and original annotation content. Finish the transaction
   only once validation is durable; repeated `post` is idempotent.
   Updating this transaction's exact unvalidated annotation to add `[valid]`
   is the sole tag-replacement exception. A changed, unrelated or already
   validated tag cannot be overwritten; observing the already completed owned
   finalization is an idempotent success, not another replacement.
6. **Recover failure.** For a version write, changelog write, commit, tag or
   gate failure, restore transaction-owned files (including every applicable
   lock entry) and index entries to their captured baseline. Remove a tag only
   when this transaction created it and its exact object still matches the
   recorded unvalidated tag. Return the branch to the captured HEAD only
   when it still points to this transaction's release commit. The prepare
   commit remains, so the restored `version.txt` is its original snapshot
   with the exact original title and notes. Preserve unrelated staged,
   unstaged, untracked and ignored user files, earlier commits and every
   previously valid release. No unconditional reset, clean or stash pop.
7. **Handle interruption or conflict.** Keep the transaction record when
   `post` is skipped or recovery/finalization fails. Add a non-interactive
   `recover <root>` path that performs the same ownership checks. If a user,
   concurrent process or gate changed HEAD, the tag, index entries or managed
   bytes since the engine wrote them, stop automatic recovery of conflicting
   state, preserve those changes and the record, and report precise manual
   recovery instructions. Never claim cancellation or success when cleanup
   is incomplete. A successfully validated tag is never deleted by later
   failed builds or recovery. If marker finalization fails after a green
   gate, report an unvalidated release and retain evidence for retry/recovery.

Serialize release mutations within a worktree and prevent races for shared
tag names across linked worktrees using their common Git identity. Different
projects may release concurrently; temporary handoffs and records must be
unique and project-local. Do not write consumer transaction state into the
tooling checkout; its managed git-cliff cache has separate provisioning locks.

The **current-version read** is read-only and returns the version, title and
notes from `version.txt`; missing or malformed files give an actionable error
rather than silently creating `0.1.0-SNAPSHOT`. The **next snapshot** is a
separate transition after a valid release, choosing patch/minor/major or an
explicit higher `X.Y.Z-SNAPSHOT`. It synchronizes sources in the same snapshot
commit, preserves title and notes unless explicitly replaced, and does not
alter the valid tag. Both direct `snapshot` and `uver` support explicit
non-interactive choices; omitted required choices fail without mutation.
Ordinary builds do not unexpectedly bump a version. Read, snapshot, release
and recovery all use the same version-source and project-root contracts.

### Snapshot tags are not releases

Recognize stable tags only by the complete `vX.Y.Z` or legacy `X.Y.Z` form.
Recognize `vX.Y.Z-SNAPSHOT` and `X.Y.Z-SNAPSHOT` separately as development
markers, including historical case variants of the suffix. Other prereleases
are not stable releases either. This effort supports existing snapshot tags;
it does not automatically create, move or delete them on snapshot transitions.

One shared tag classifier/range selector serves the engine, git-cliff input,
release-notes collection and release-plan/documentation ranges. Select a
reachable eligible stable release as the baseline, excluding snapshot tags
even when they point at HEAD. New engine tags require `[valid]` to become
release baselines; retain support for historical stable releases without that
marker, while excluding a tag recorded as an active unvalidated transaction.
The distinction between a historical release and a new unvalidated release
must remain available in another clone and when local transaction evidence
is absent. Missing evidence never promotes an unfinished new release into
a historical exception. Ambiguous validity must be reported and must not
silently establish a baseline. The persistent evidence and migration mechanism
are design decisions; local journals alone cannot define tag eligibility.
Use a documented deterministic ancestry rule, and report conflicting tags
rather than guessing. With no eligible stable tag, use the full relevant history.

Do not split `git describe` output on `-` to find a commit count: the snapshot
suffix is part of the version. Query the chosen ref and its commit distance
explicitly. Configure/filter git-cliff's release tags with the same complete
stable-tag rule and pass the selected range; ignoring a snapshot boundary must
retain commits on both sides, not skip their changelog content. Neither a
release-notes nor release-plan reader may use an unfiltered "last tag" query.

Example: after stable `v0.13.0`, commits A and B surround
`v0.14.0-SNAPSHOT`. Preparing `0.14.0` includes A and B from `v0.13.0..HEAD`,
even when HEAD itself has the snapshot tag. Release creates a distinct
`v0.14.0` on `main`; recovery/`crel` may remove only that transaction's
unvalidated stable tag, never the snapshot marker or a previously valid tag.
Publish/version-choice consumers in a later repository migration must also
exclude snapshot markers from release choices and require explicit snapshot
intent (including the `publish_pdf_nexus*.sh` follow-up in my-project).

### Temporary files move out of the tooling tree

With one shared copy of the tooling, consumer scratch files must not be written
inside it: two projects releasing at once would share those files. The ignored,
versioned git-cliff cache is the sole provisioning exception. Today:

- `update-version.bat` writes `dirty_files.tmp`, `dirty_ignored_files.tmp` and
  `run_filter.cmd` into `tools/dev_workflow/git/`;
- `t_build.bat` writes `temp_tag_message.txt` into `tools/dev_workflow/` (a
  leftover copy sits untracked in llm-shared's checkout right now);
- `update-changelog.sh` writes `CHANGELOG.tmp.md`, `CHANGELOG.new.md`,
  `CHANGELOG.cleaned.md`, `CHANGELOG.labeled.md`, `version.tmp.txt`,
  `.fixes_content.tmp` and `tmp_fixes.pl` at the project root.

The Python engine keeps most of those steps in memory. The files that remain
(the git-cliff output, the tag message, the `pre` handoff) go to the project
artifact home, following [`rules/artifact_files.md`](../../rules/artifact_files.md).

### Per-project settings in .release.ini

Existing project files keep their meaning: `version.txt`, `CHANGELOG.md`,
`changelog-header.md`, `.exempt-files`. New ones, only where a project needs
to differ from the defaults:

- a project `cliff.toml` overriding llm-shared's default one;
- `.changelog-fixes.toml`, the fix rules (see "Changelog fixes without Perl");
- `.release.ini` at the project root, same idea as `.review-artifacts.ini`,
  for everything else. A project without it gets every default.

```ini
[changelog]
; generated (git-cliff, the default) or curated (author-maintained)
mode = generated
; proposed archive policy syntax: numeric inclusive bounds, no v prefix
recent-from = 0.14.0

[changelog-archive:0.1.0-0.13.9]
from = 0.1.0
to = 0.13.9
file = docs/CHANGELOG.v0.1.0-v0.13.9.md

[git-cliff]
; exact version to download automatically into llm-shared's ignored cache
version = 2.14.2

[tooling]
; minimum compatible llm-shared release; no v prefix
minimum-version = 0.14.0

[source:npm]
; override the default form of a built-in format
form = release-only

[source:cicd-env]
; a project-specific file, one regex group holding the version
file = cicd/config/.env
pattern = ^APP_SERVICE_VERSION=(.+)$
form = snapshot
```

`generated` means commit-derived changelog text owned by the engine. `curated`
means author-maintained release notes, such as marketplace-facing bullets.
Neither mode changes the version-source forms or the consuming build gate.
In `curated` mode the engine never rewrites `CHANGELOG.md`: it only checks that
a section for the exact release exists (allow `## X.Y.Z` and the documented
`vX.Y.Z`/bracketed heading forms, never a substring match). It requires neither
git-cliff nor `changelog-header.md`, does not inject notes, dates or fix rules,
and preserves the curated file byte for byte. Archive movement also requires
author edits in this mode; the engine validates range placement and links.
The `.release.ini` config file is read with interpolation off, so
`%` and `$` in a pattern need no escaping.

The common config reader validates modes, forms, paths and unknown keys before
mutation. Version-source settings belong to version management; the git-cliff
pin belongs to internal provisioning; generation, archives and rules belong
to changelog management; the tooling minimum belongs to setup/upgrade checks.
No consumer runs code from project config. There is no git-cliff executable
key: llm-shared computes the fixed internal path.

### Changelog ranges and archives

Keep `CHANGELOG.md` at the repository root for the current snapshot and recent
stable releases. `.release.ini` defines the recent lower bound and any number
of inclusive archive ranges, each stored as
`docs/CHANGELOG.vA.B.C-vD.E.F.md`. Without ranges, the default remains a single
root file; setup proposes an initial split based on existing history. The
example above puts releases `0.1.0` through `0.13.9` in the named archive and
stable releases from `0.14.0` onward in the root file.

Compare version triples numerically, never as strings; do not infer ranges
from current file sizes or silently choose new boundaries. Each stable release
section must have exactly one destination. Reject overlapping ranges, reversed
bounds, an uncovered existing release, paths outside `docs/`, and filename
bounds inconsistent with config. Gaps containing no releases are allowed, but
become errors if a newly encountered release would have no destination. Snapshot
sections always stay in root. Add relative links to archives in root and links
back to root in archives, preserving release titles, dates and section content.

Authors can change the bounds whenever they choose. In generated mode, the next
`changelog` run previews the affected files and repartitions complete sections
according to the new config, preserving released section bodies and historical
notes. Apply each rule once to content being generated; existing released
sections remain unchanged during ordinary rendering. Assemble and validate
the whole result before replacing any file. Writes and release recovery cover
root, new/changed archives, and any obsolete engine-owned archive removed after
its sections and links are moved;
never remove unrelated files. Repeated runs with unchanged inputs are identical.
Preparation stages this exact changed set and `.release.ini` when policy was
edited; the release commit includes any files changed by final rendering.

Existing released sections are authoritative during ordinary generated-mode
rendering. Changed fix rules do not automatically rewrite released history;
historical revisions require an explicit action. Moving a section between root
and archives or between archives preserves its body. Any intentional historical
revision must retain editorial notes and be visible in the proposed changed
set. Conflicting sources must be reported rather than silently resolved. The
explicit revision action, content representation, comparison and regeneration
mechanisms remain design work.

In curated mode the same range policy is checked but files and links remain
author-maintained. Report misplaced or duplicate sections with their expected
destination. Do not silently generate, rewrite or archive curated prose.

### Generated changelog contract

Generated mode uses the project's `cliff.toml` or llm-shared's default, requires
`changelog-header.md`, and applies the built-in cleanups followed by project
fix rules to content being generated. Ordinary rendering preserves existing
released sections; revising them requires the explicit action described above.
Inject `version.txt`'s release-notes body exactly once under the
target heading; rerunning on unchanged inputs is idempotent. During a snapshot
use the hash-free unreleased heading below; at release use
`## [vX.Y.Z] - YYYY-MM-DD - <title>`. Capture the local release date once for
the transaction and reuse it in the changelog and annotation. Remove duplicate
target-version sections and label groups without dropping historical entries.
Existing tagged releases retain their dates; rerunning must not date them
with today's date. Handle older unprefixed `X.Y.Z` tags when resolving release
ranges, while newly created tags always use `vX.Y.Z`.

Render, inject, clean, label, fix and validate in memory or unique artifact
files, then replace the root changelog and affected archives only after every
phase succeeds. Missing
headers, invalid config or rules, git-cliff failure and invalid output leave
the previous changelog intact; during a release the transaction restores any
earlier version edits as well. `uc`/`uvf` and release-note preparation perform
git-cliff preflight before automatic `fixes init`, so a missing tool cannot
leave a newly created rule file behind. Release preprocessing uses the
transition reader and never creates that file mid-release.

### No hash in the snapshot changelog heading

While a version is a snapshot, dev_workflow ends the generated heading with the
full hash of the commit it was built from:

```text
## [v0.12.0-SNAPSHOT unreleased] Resume Where You Filed It - 911e249c1afef827bd2ab37055e63e1d33b7b3ee
```

Every regeneration after a new commit (`uc`, `uvf`, Step 10 and Step 11 of
`/prepare-release`) changes that line, so `CHANGELOG.md` shows as modified for
a one-hash difference. `init.bat` configures a `filter.changelog` clean filter
meant to strip the hash when the file is staged, but no `.gitattributes` maps
`CHANGELOG.md` to it, so it never runs: llm-shared's history holds the hashes
(for example in `8142624`).

The engine writes no hash: the unreleased heading ends at the title.

```text
## [v0.12.0-SNAPSHOT unreleased] Resume Where You Filed It
```

A regeneration then changes `CHANGELOG.md` only when its content changes, with
no git config or filter to install in each clone. The engine never sets
`filter.changelog`, and the migration removes it from existing clones
(`git config --remove-section filter.changelog`). The parity run against
dev_workflow compares that heading without its hash suffix.

## Changelog fixes without Perl

Today `.changelog.fixes` has two forms, both run by Perl:

- the `# PERL_CODE` form, a Perl fragment of `push @patterns, qr/.../;` and
  `push @replacements, '"..."';` pairs pasted into
  `update-changelog.fixes.tpl.pl`, then applied to the whole changelog with
  `s/$pattern/$replacement/gee`;
- a legacy `regex => replacement` line form, which the bash script turns into
  the same Perl pairs.

The three existing files (llm-shared, my-project, and the template) use only
the `push` pairs: 2 rules in llm-shared, 32 in my-project, typo fixes, empty
old release headings filled in, and backticks added around identifiers. Their
patterns use lookbehinds, `\S`, `[\r\n]`, `\s*?` and non-capturing groups,
all of which Python's `re` reads the same way. Their replacements are Perl
double-quoted strings holding `$1` or `\1` and `\n`, which map to a Python
`re.sub` template (`\1`, `\n`).

So a Python runner can replace Perl completely:

- the three built-in rules of the Perl template (wrap bare URLs in angle
  brackets, drop a single trailing space, turn a leading asterisk list marker
  into a dash) become
  built-in Python rules, applied first;
- project rules move to `.changelog-fixes.toml`, a declarative file with one
  pattern and one replacement per rule:

cSpell: disable

  ```toml
  [[rule]]
  pattern = 'sumary'
  replace = 'summary'

  [[rule]]
  pattern = '\[v4\.1\.0\] -\s*?[\r\n]'
  replace = '[v4.1.0] - New doc created instead of rereading inputPDF\n'

  [[rule]]
  pattern = '(?<!`)__init__\.py'
  replace = '`__init__.py`'
  ```

cSpell: enable

- `fixes <root> convert` writes `.changelog-fixes.toml` from an existing
  `.changelog.fixes`, reading only the `push` pairs and the `=>` lines. Any
  other Perl statement stops the conversion and names its line, rather than
  guessing;
- `fixes <root> init` creates `.changelog-fixes.toml` when it is missing: by
  conversion when a `.changelog.fixes` exists, otherwise from a commented
  starter template in llm-shared `templates/` (replacing dev_workflow's
  `templates/.changelog.tpl.fixes`);
- `uc`, `uvf` and `/prepare-release` Steps 10 and 11 run that `init`
  automatically before rendering, so the new file appears in the working tree
  and lands in the prepare commit (Step 13 stages it with the other release
  files);
- `brel` never creates the file: a new untracked file would make the tree
  dirty mid-release, outside the release commit. When the TOML is missing,
  `brel` uses the transition reader instead, reading the same subset of
  `.changelog.fixes` in memory, and notes that the next `/prepare-release`
  will convert it automatically;
- once `.changelog-fixes.toml` exists, it is the only rule file read; a
  `.changelog.fixes` still present beside it gets a one-line warning that it is
  ignored and can be deleted;
- `fixes <root> dry-run` lists, per rule, how many matches it made, replacing
  the `CHANGELOG_DBG` output of the Perl script.

A rule whose pattern does not compile in Python fails the run with the rule
number and the `re` error, instead of Perl's "some rules may have failed"
warning that lets the changelog through half-fixed.

`/prepare-release` Step 11 then reads "the fix rules" instead of "the Perl
find/replace rules", and `prepare_release_notes` needs no change beyond the
engine call.

## Version sources as plugins

A version lives in more places than `version.txt`. dev_workflow knows two
(`pom.xml`, `package.json`). `/prepare-release` Step 12 already describes more,
each in its own form: `pyproject.toml` and `uv.lock` without the suffix,
`package.json` and `package-lock.json` in the release form (a VS Code
extension version supports only `major.minor.patch` on the Marketplace), Maven
POMs and their module parents with `-SNAPSHOT`, and a `cicd/config/.env`
variable. my-project's `tools/set_version.py` and `tools/check_versions.py`
implement that list for one repository. The engine should implement it once,
for every repository, and leave room for formats nobody needs yet.

### One module per format

Each format is one module in llm-shared's `tools/release_workflow/sources/` package
(`maven.py`, `npm.py`, `pyproject.py`, ...), exposing one object that follows
a small protocol:

```python
class VersionSource(Protocol):
    """One kind of file that states the project version."""

    name: str  # "maven", "npm", "pyproject", ...

    def detect(self, root: Path) -> tuple[Path, ...]:
        """Return the files of this kind under root, empty when none."""

    def read(self, path: Path) -> str:
        """Return the version the file states today."""

    def expected(self, version: ProjectVersion) -> str:
        """Return the form this kind states for one version.txt version."""

    def write(self, path: Path, version: ProjectVersion) -> None:
        """Rewrite only the version, leaving every other byte in place."""
```

Two different things are found here, in two different ways:

- which formats the engine knows: `tools/release_workflow/sources/__init__.py`
  lists each format object in one explicit tuple. Adding a format is one module
  and one line in that tuple. The tuple gives a deterministic detector order,
  and pyright and vulture see every format in use. A test lists the
  modules of the package and fails when one is missing from the tuple, so a
  new format cannot be written and then silently left out;
- which files a project holds: each format's `detect` looks for its own files
  under the project root, automatically, so a project gains a format's support
  the day llm-shared ships it, with nothing to declare for unambiguous project
  roots. Independently nested components follow the explicit participation rule.

This package and its registration tuple live only in llm-shared, never in each
consumer. Extension means adding the module, registering its object, and adding
detect/read/expected/write and failure-restoration tests; no release-orchestration
changes or copied consumer code are needed. Project-specific text files use
the declarative pattern source. Executable project-local plugins are outside
this effort and would need a separate contract.

Run every registered detector and combine their results; selecting Python does
not suppress npm or Maven. A project with root `pyproject.toml`, `uv.lock`,
`package.json` and `package-lock.json` updates all four from one anchor. A Node
component under `frontend/` is included when declared as a participating
component root in `.release.ini`; do not mistake every sample/package manifest
for the project's release. Setup detects candidate component roots and records
their participation, so later version transitions need no repeated choices.
The design must settle the declaration syntax. Conflicting claims on one file
fail before writes rather than being silently resolved by detector order.

`versions <root> list` prints each detected file with its kind and current
value, so a user sees what a release will touch before it does.

Detection skips `node_modules`, `venvs`, `.venv`, `.git`, `.reviews` and
`target`, and a format can walk further from its root file: the Maven plugin
reads the `<modules>` of the root POM and updates each module's `<parent>`
version.

### Forms, and the anchor

`version.txt` is the anchor: every other source takes its value from the first
word of `version.txt`, never from its own current value. Each format then
chooses its form:

| Form | Snapshot `1.2.3-SNAPSHOT` becomes | Release `1.2.3` becomes | Used by default for |
| --- | --- | --- | --- |
| `snapshot` | `1.2.3-SNAPSHOT` | `1.2.3` | Maven POMs, the `.env` variable |
| `core` | `1.2.3` | `1.2.3` | `pyproject.toml`, `uv.lock` |
| `release-only` | `1.2.3` | `1.2.3` | `package.json`, `package-lock.json`; no prerelease suffix by default |

`core` and `release-only` give the same strings. They differ in their
guard: a `release-only` source refuses a value lower than the one it states
already, since lowering a published extension version would rewind it, as Step
12 of `/prepare-release` already requires.

Both forms synchronize to the current anchor's core during a snapshot. They
do not retain the previous published value: with `version.txt` at
`0.0.25-SNAPSHOT`, npm sources become `0.0.25` already. This resolves the
contradictory workspace-halo example below. Maven and the configured `.env`
source use `0.0.25-SNAPSHOT`; Python cannot accept that Maven-style suffix.
An npm project can explicitly select `snapshot` when its packaging accepts
that SemVer prerelease, but VS Code Marketplace consumers use `release-only`.
Unsupported form/format combinations fail before writes.

### First set, and the next ones

- Explicitly supported first set, because the three repositories and Step 12
  need them:
  `version.txt`, `pyproject.toml` (`[project].version`), `uv.lock` (the
  virtual root package), `package.json` with `package-lock.json` (the top-level
  `version` and `packages[""].version`, no external dependency entry touched),
  Maven `pom.xml` with its module parents.
- A generic `pattern` source, declared by a project, for the one-off files:
  a path, a regular expression with one group, and a form. my-project's
  `cicd/config/.env` becomes one line of project configuration, instead of a
  case every repository's release carries.
- Future candidates only, not promised support in v0.14.0: `Cargo.toml`,
  `gradle.properties` and `build.gradle(.kts)`, `*.csproj` or
  `Directory.Build.props`, Helm `Chart.yaml` (`version` and `appVersion`),
  `composer.json`, `pubspec.yaml`, `mix.exs`, a `__version__` in a Python
  package `__init__.py`.

Detection follows project nature, not every matching file in the tree:
identify the Python project by its declared name and local/virtual source in
`uv.lock`, the npm root by its manifest, and the Maven reactor through its
root POM's declared modules. Exclude vendor/sample projects and nested Git
repositories as well as the directories already listed. Independent workspace
packages need explicit configuration rather than accidental synchronization.
Dynamic Python versions, ambiguous lock roots or unsupported Maven property
indirection fail with the exact source and configuration remedy; never guess.

For a single-component Python project, update `[project].version` and only
the corresponding local root package version in `uv.lock`, leaving lock schema
`version`, dependency versions, hashes, URLs and resolver metadata unchanged.
For a single-component npm project, update only the root manifest `version`,
lock top-level `version` and `packages[""].version` where present for that lock
format. Maven updates the reactor's project
versions and internal module-parent references; inherited versions remain
inherited and external parent/dependency/plugin versions stay unchanged.
Handle supported reactor version properties explicitly or reject them with
an actionable error. A configured pattern source must match exactly one
version capture in its declared file. Each adapter validates its complete
write set before changing any file and preserves unrelated content, formatting
and line endings; no global replacement of every field named `version`.

Synchronization must also account for version references between participating
components. For example, changing Maven module A's version while module B
still depends on its old version is not a consistent reactor transition.
The same contract applies to supported participating workspace packages and
their manifests/locks. Update internal references supported by the adapter;
reject unsupported or ambiguous arrangements before any writes, naming the
affected components and the limitation. External dependency versions remain
unchanged. This does not promise every workspace format: child requirements
must state the supported boundary and designs choose how references are
identified and changed. No successful transition may knowingly leave stale
internal references within that supported boundary.

The supported lock entries can be edited directly for a version-only change;
do not run `uv lock` or npm dependency resolution opportunistically merely
because a tool is present. If an explicitly supported format needs regeneration,
require its tool and limit/validate its changes; if consistency cannot be
maintained safely, fail before mutation rather than produce a best-effort lock.
`versions list` reports detection and forms, `versions check` reports actual
and expected values and exits nonzero on drift, and `versions set <version>`
updates the anchor token and all applicable sources as one recoverable
operation, with the target as its proposed authoritative value. Snapshot and
release transitions reuse this operation. Title and notes never change as a
side effect of synchronization; failed writes restore the whole original set.

### What uses the version-source engine

The shared detection, form mapping and atomic synchronization operations above
are reused by these callers; each receives the full set of participating sources.

- `brel` (`pre`, release mode): changes the anchor to `X.Y.Z` and maps each
  source to its release form. Python/default npm already have that core;
  snapshot-form sources lose the suffix. Include each changed file in the commit.
- The next-snapshot step after a release: raises every source to the chosen
  `X.Y.Z-SNAPSHOT` in its form, in the same commit as `version.txt`.
- `/prepare-release` Step 12: `versions <root> set X.Y.Z-SNAPSHOT` then
  `versions <root> check`, in place of the per-format instructions it carries
  today.
- A project `check.bat`: `versions <root> check`, in place of a project
  `check_versions.py`.

## Integration with /prepare-release

### What /prepare-release does today

Steps 9 to 13 set `version.txt` to `X.Y.Z-SNAPSHOT`, call
`prepare_release_notes` (which runs `tools\dev_workflow\update-changelog.bat`),
pause for review and regenerate the changelog with the same script (Step 11),
update the other version sources by hand or through `tools/set_version.py`
(Step 12), and make one `chore(release): prepare for vX.Y.Z release` commit
(Step 13). Step 14 checks the tree is clean, reports, and tells the user to
run `brel`. The instruction states it "never creates the git tag".

This paragraph describes existing behavior, which the new flow below changes.
In feature mode, when the umbrella has another unfinished item, the run stops
after the merge with a `process-draft` handoff. When the umbrella is exhausted,
or the feature is standalone, it goes on through the full release path with no
choice.

### What changes in every run

- Step 10 and Step 11 call the engine `changelog` command instead of
  `tools\dev_workflow\update-changelog.bat`. Generated mode provisions its
  pinned binary, automatically converts missing TOML fixes from the legacy
  file, and applies the configured root/archive policy.
- Step 12 calls `versions set` and `versions check` (see above) instead of
  describing each format.
- Step 13 also stages new/changed `.changelog-fixes.toml`, `.release.ini` and
  the exact affected archive set, including owned archive removals.
- Release-notes, release-plan and documentation range selection use the shared
  stable-tag selector; snapshot markers never truncate the reviewed history.
- Before preparation, check the llm-shared minimum/latest stable version and
  offer the upgrade action described below; complete it before engine execution.
- The "Boundary with brel" section names the llm-shared launcher instead of
  `tools\dev_workflow\update-version.bat`.

### Release after a confirmed merge to main

Completing one umbrella does not mean all work for the next release is ready.
The user can confirm integrating it into `develop`, then continue integrating
other umbrellas there without preparing or tagging a release. A separate
confirmation covers the complete proposed integration-to-`main` range and
states that this merge starts release preparation, the build gate and tagging.
Approval for an umbrella merge does not authorize that later merge to `main`.

Once the confirmed merge to `main` succeeds, the workflow continues through
preparation and its existing title/edit/readiness gates. After the prepare
commit and Step 14 clean-tree gate, it automatically invokes the supported
project `build.bat rel` in non-interactive form. No second tag-only choice is
needed: the main-merge confirmation included the release. This is workflow
orchestration, not a Git hook that tags arbitrary manual merges. A failed or
cancelled preparation stops without a tag and can be resumed on `main`.

The engine changes `version.txt` from `X.Y.Z-SNAPSHOT` to `X.Y.Z`, synchronizes
every secondary source to its release form (Python/default npm already contain
`X.Y.Z`), renders the dated changelog and affected archives or validates curated
content, commits `chore(release): set new 'vX.Y.Z'`, creates annotated `vX.Y.Z`,
runs the consuming gate and only then marks the tag `[valid]`. Recovery retains
the confirmed merge and prepare commit and restores only transaction-owned
release changes. Conflicts retain evidence and report incomplete recovery.

For a run starting on `main` without an already authorized merge-and-release
continuation, keep an explicit final choice: `Stop here` or `Go ahead, and tag
the release`. A direct user invocation of `brel` on `main` also expresses release
intent. On every other branch, `br`/`brel` refuse release mutation; snapshot and
ordinary build operations remain available. No flow pushes commits or tags.

#### Where version.txt gets its content

The release step writes no release notes. By the time it runs, the same
`/prepare-release` run has already written them:

- Step 9 sets the first word to `X.Y.Z-SNAPSHOT`;
- Step 10 (`prepare_release_notes`) writes the summary (theme line, key
  changes, paragraphs), offers three title and subtitle pairs, and rewrites
  the first line to `X.Y.Z-SNAPSHOT -- <title>` once one is picked;
- Step 11 pauses for edits, regenerating the changelog when they change;
- Step 13 commits it in the prepare commit.

The release step then changes only the first word, `X.Y.Z-SNAPSHOT -- <title>`
becoming `X.Y.Z -- <title>`, and reuses the rest: the title goes into the
`## [vX.Y.Z] - <date> - <title>` changelog heading, the body goes under it,
and the whole file, with the date in place of the version, becomes the tag
message. No title prompt appears, since `version.txt` already carries one.
The next-snapshot prompts (fix, minor or major, new title, description) belong
to the next snapshot, after new commits, not to this step.

As a guard, the release refuses to start when the first line of `version.txt`
has no `--` separator followed by a title, or when no summary follows it,
which is what a `brel` run without `/prepare-release` first would otherwise
tag.

#### When release tagging is prohibited

No tag is offered or created on a feature, umbrella or generic integration
branch, while any included umbrella has unfinished topics, before the prepare
commit/readiness gates, or without a supported consuming build contract and
compatible launcher. Checking out `main` alone does not authorize a release.
The workflow's boundary becomes: only tag on `main` following an explicit
release choice or the confirmed merge-and-release continuation; never push.

#### Recording the tooling version in the tag

A submodule pins the tooling commit; a sibling does not, so the release
records which llm-shared built it. The engine adds one trailer line to the
annotated tag message, after the `version.txt` content and before the
`[valid]` marker that `post` appends:

```text
Release tooling: llm-shared v0.13.0-4-gabc1234
```

The value is the executing llm-shared checkout's
`git -C <llm-shared> describe --tags --long --dirty --always`, captured after
any approved tooling upgrade and before the release transaction. Unlike a
release-range query, this is a diagnostic string, not a parsed commit count
or stable-release selector. Also retain the exact tooling commit in transaction
evidence. Keep the executing tooling unchanged for the run; a change during
the gate prevents validation. For llm-shared's own release, distinguish the
captured preparation commit from the transaction-owned release commit.
That expected HEAD transition and its enumerated release-file changes are
allowed; the engine source and all other tooling content must stay unchanged.
The trailer still identifies the tooling that executed the transaction, and
the release evidence must account for the owned commit transition. An
unrelated HEAD movement or source edit is never covered by this exception.
How the implementation proves that identity remains a design decision.
It goes to the tag message only, never to `version.txt` or `CHANGELOG.md`, so
the release notes stay about the project.

Follow-up to remember: amend
`templates/prepare-release-notes.version-txt.template.txt` (and the
`prepare_release_notes` instruction that fills it) so the template shows where
that trailer sits in the final tag message, below the key changes, instead of
leaving it implicit in the engine.

### The feature-mode choice

Feature-to-umbrella merges remain untagged. The distinct confirmation points
below prevent finishing one umbrella from releasing other integrated work early.

| Feature-mode situation | Today | Proposed |
| --- | --- | --- |
| Umbrella has another unfinished item | Merge back, `process-draft` handoff, stop | Unchanged: merge back to the umbrella integration branch, `process-draft` handoff, stop. No prepare choice and no tag choice is offered |
| Umbrella exhausted | Continue toward release | Confirm its exact merge into generic integration such as `develop`, or stop; after integration, stop without tagging so more umbrellas can join |
| Standalone feature | Continue toward release after merge-back | Confirm the merge into generic integration, then allow stopping there without tagging |
| Generic integration ready for release | Prepare and stop before brel | Confirm the complete merge to `main` and its release consequence; successful merge continues automatically through preparation, gate and tag |
| Already on main | Prepare and stop before brel | Resume a previously confirmed release continuation, or offer the explicit final tag choice for a fresh on-main run |

No implicit permission carries from feature completion or umbrella integration
to the separate merge to `main`. Existing merge review requirements still apply.

### One release across umbrellas and interrupted preparation

A release continuation must identify the repository, the complete confirmed
integration range, every included umbrella/standalone effort, and one target
release version. Check completion for all included umbrellas; checking only
the currently selected one is insufficient. Unrelated drafts outside the
release scope do not block it. Release notes cover the whole included range.
Conflicting effort target versions require an explicit user choice before
confirming the main merge; do not silently choose a version from whichever
umbrella happened to be selected. This adds no automatic version-bump rule.

The confirmed release intent and preparation progress must survive an
interruption. A resumed run must establish that it continues that same
authorized release, account for its owned merge/preparation commits and
completed gates, and avoid repeating completed release actions. A changed
included range or target version requires a new decision for the changed
scope; the old confirmation does not cover it. Existing title/edit gates
remain applicable, including edits they explicitly allow. Checking out main,
finding a prepare commit, or losing continuation evidence cannot manufacture
authorization. When authorization cannot be established, use the existing
fresh-on-main release choice. Cancellation must not silently become automatic
resumption. The representation and storage of continuation evidence, and its
relationship to the engine transaction record, remain design decisions.

### Setup, migration and tooling upgrades

Add a dedicated `setup-release-tooling` skill backed by a repeatable helper for
new consumers and migrations. It inspects the real project before editing,
adds pre/post integration around the existing gate, generates or merges
`.release.ini`, registers participating ecosystems, exposes llm-shared aliases,
and converts legacy fixes automatically. It preserves project-specific commands,
comments and settings and produces a concrete diff; rerunning makes no duplicate
blocks. Report unrecognized build layouts with proposed changes rather than
blindly replacing a script. Provide preview and non-interactive application
forms with explicit choices. The helper handles llm-shared's self-hosted launcher
path as well as sibling discovery in other projects.

The skill also drives migration checks for legacy init/color references,
submodule consumers and Git filter cleanup. Apply relevant steps to llm-shared
first. Remove a legacy dependency only after all local callers have replacements
and parity/recovery checks pass. External repository changes remain in their
own efforts; the helper and documentation are delivered here.

Provide a tooling-update launcher and an `llmup` alias (proposed name), reused
by a stage before release preparation. Check the project's minimum compatible
llm-shared release against the installed revision and the latest stable upstream
release. Propose a concrete target, old/new versions and affected checkout.
When too old, offer to update to the latest compatible stable release satisfying
the minimum; declining blocks release work but not an ordinary build. When
already compatible, a newer stable release is optional. A successful update
restarts/revalidates with the new launcher before preparation, and the tag's
`Release tooling:` value then reflects the code actually used.

Updating an llm-shared clone is separate from automatically filling its git-cliff
cache. Fetch/check first; apply an explicitly selected update only when it will
not overwrite local edits, divergent development history or another active
release's tooling revision. No reset, stash or forced branch switch. Report a
development checkout as such and offer an appropriate separate stable checkout
when an in-place update is unsuitable. During llm-shared's own cutover, use its
candidate implementation; do not replace it with the older published tool.
Allow offline use of a compatible installed revision; report the latest check
as unavailable, never as proof it is current. Non-interactive callers supply an
update policy or receive the required action without a hidden prompt.

Compatibility must be established for the consumer's configuration and required
release operations, not inferred solely from an installed version being above
`minimum-version`. State which combinations are supported; unknown or
incompatible combinations block release with a concrete remedy. The policy
must cover the candidate engine during llm-shared's own cutover without
pretending it is an already published stable release. A compatibility protocol,
config schema strategy and version-range notation are left to design.

Setup and upgrade reuse llm-shared's setup process to prepare or repair its own
Python environment. An accepted tooling update is usable only after its
runtime/dependencies are ready and the consumer demonstrably invokes that
selected checkout. When a separate stable checkout is selected, ordinary
sibling discovery must not
silently redirect the resumed run to the old development checkout. Preserve
the sibling-first default for unselected runs and report the actual selected
tooling path. The selection mechanism remains design work. Failed update or
readiness checks must not be reported as a completed upgrade or allow release
to proceed on an unintended revision; preserve the prior usable setup and
the existing protection for local work and active releases.

## When llm-shared is not beside the project

| Situation | `b` (build) | `brel` / `br` | `gv`, `uc`, `uver`, `uvf` |
| --- | --- | --- | --- |
| `..\llm-shared` present | Full flow | Full flow | Available |
| `..\llm-shared` missing and no valid fallback | Builds, with one warning; the version shown is read from the first word of `version.txt` | Stops before any git change, with a warning naming the missing folder, non-zero exit | Not defined; `senv` says so once |
| `..\llm-shared` present but older than the project expects | Builds | Offers the concrete tooling update, resumes after a successful approved update/recheck, otherwise stops before release mutation | Available compatible commands warn and expose the same update action |
| Pinned git-cliff absent from internal cache | Builds | Generated `br`/`brel` downloads and verifies it automatically before project mutation; curated release builds need none | Generated `uc` does the same; version/snapshot commands and curated validation need no binary |
| Internal git-cliff unavailable and download/verification fails | Builds | Generated release fails with internal path/version and setup/network diagnostic; curated release builds work | Generated `uc` fails; version commands and curated validation remain available |

All release entries in this table still require `main` and the readiness gates.

## Engine in Python

The Python rewrite was chosen over a straight port of the batch and bash: a
port would leave about 1,100 lines of untested batch outside llm-shared's
`ghog` coverage gate, bugs included. In Python, the snapshot and release state
machine becomes testable against temporary git repositories, Perl, awk, sed
and bash leave the dependency list, and the defects below get fixed instead of
copied.

The `dev_workflow` submodule stays in place until isolated parity runs on
llm-shared history compare `version.txt`, version sources, changelog sections,
commit subjects and annotations against the old scripts. Allow documented
intentional differences: corrected versions/locks, hash-free headings, archive
placement, the tooling trailer, snapshot-tag filtering and approved git-cliff
output fixes. Preserve all other content; investigate unexplained differences.
These are rehearsals, not competing real release tags. The actual `v0.14.0`
release/tag on `main` must be produced by the new engine after cutover.

### Defects to fix rather than port

- `update-version.bat` lines 353 and 361, in `:restore-version`, use
  `%update_version_dir%` while the script defines `update-version_dir`: the
  POM and `package.json` restore calls resolve to `\t_build_maven.bat` and
  `\t_build_npm.bat` and never run.
- Lines 435 and 437 compare `"%git_tag%"==v"%version%"`: the quotes differ on
  each side, so the "already released" guards can never match, and both
  branches test the same condition.
- `t_build_npm.bat` line 89 rewrites every `"version": "..."` line of
  `package.json`, not only the top-level one, and leaves `package-lock.json`
  behind.
- The npm path requires `package.json` to carry `-SNAPSHOT` before a release
  (`check-snapshot`), the opposite of the release-only form a VS Code
  extension needs: workspace-halo's release would stop there.
- Every sub-script calls `"%PRJ_DIR%\senv.bat"` again (`t_build`,
  `update-version`, `update-changelog`, both adapters). The engine should never
  call the project `senv.bat`: the project `build.bat` already did.
- The `PRJ_DIR` and current-directory issues described above.

## Per-repository migration

### llm-shared itself

- llm-shared is the first consumer of the setup/migration helper, including
  the applicable init, color, version-source and reference cleanup described
  for my-project below. Its own development checkout provides the new engine;
  its release is not delegated to the still-published older tooling.
- `build.bat` switches from `tools\dev_workflow\t_build.bat` and
  `get-version.bat` to its own `bin\release_workflow.bat`. llm-shared is both
  the engine and a consumer: the release commit touches only `version.txt`,
  `CHANGELOG.md`, affected archives and version sources, so transaction recovery
  never rolls the engine back. Keep llm-shared's existing consuming build gate; do not
  misdescribe its current dummy/last-failed pytest gate as the full ghog suite.
- `tools/init.bat` goes away; `senv.bat` exports the batcolors macros from
  `tools\batcolors` directly and stops clearing `INIT_DONE`.
- Add the `tools/shcolors` submodule (batcolors `linux` branch), remove the
  `tools/dev_workflow` submodule and its `.gitmodules` entry.
- Let setup/preparation convert its `.changelog.fixes` (2 rules), and create
  `.release.ini` with the proposed exact git-cliff pin and chosen archive ranges.
  Ignore the internal `.tools/git-cliff/` cache and expose `gcliff` and the
  tooling-update alias along with the existing release aliases.
- Update every reference to `tools\dev_workflow\update-changelog.bat`: the
  `prepare_release_notes` Step 5 in `instructions/prepare-release-notes.md` and
  its adapter copies, `instructions/prepare-release.md` (Steps 10 to 14 and the
  new release step), `DEVELOPMENT.md` (the "Dependency on the
  senv_dev_workflow build tooling" section), and the wiki pages that name it
  (`how-to/prepare-a-release.md`, `reference/aliases-and-launchers.md`,
  `reference/repository-layout.md`,
  `tutorials/05-prepare-a-release-from-develop.md`,
  `explanation/one-body-many-agents.md`).
- A new how-to page: "Give a sibling repository `brel`", using the setup skill
  and helper to create the integration and `.release.ini`. Keep the build
  snippet as reference for the generated changes, not the primary manual task.
- The migration itself, documented in the Diataxis wiki:
  - an explanation page on why a sibling replaced the submodule (pinning
    through the tag trailer, one copy of the tooling, no nested submodules);
  - a tutorial following setup, first preparation, confirmed integration to
    `main`, release gate and tag, including llm-shared's first-use example;
  - a how-to, "Move a project from the dev_workflow submodule to sibling
    llm-shared": run the migration skill/helper, inspect its build/init/color
    and fix-rule changes, choose archive ranges, validate parity, then remove
    the submodule. Include repeat runs and the tooling upgrade action;
  - the reference pages for the new launcher commands, `.release.ini` keys and
    `.changelog-fixes.toml` rules, internal automatic provisioning and aliases.
- The archive of
  [`senv_dev_workflow`](https://github.com/VonC/senv_dev_workflow) is not an
  llm-shared change: it closes the my-project effort, only once both llm-shared
  and my-project no longer use the submodule. Its last README points to the migration
  how-to above, then the repository gets the GitHub archive flag.
- Cutover evidence must show the real `v0.14.0` annotated tag created by the
  new engine on `main`, its consuming-gate result and `[valid]`, and the actual
  `Release tooling:` value. A parity rehearsal alone does not satisfy that
  release outcome; do not mark it validated before the authorized release runs.
  Record this at release closeout, separately from implementation validation:
  the cutover row can complete once the engine is installed and its rehearsals
  pass, making the umbrella eligible to release. Requiring the real tag before
  completing that row would deadlock the unfinished-umbrella release guard.

### my-project, for its own effort

- Use the same setup/migration skill; `build.bat` makes the same switch as
  llm-shared, retaining this project's gate and deployment responsibilities.
- `tools/init.bat` goes away, with the `INIT_DONE` handling in `senv.bat`
  (lines 51 to 62).
- `tools\batcolors` is today a junction into `tools\dev_workflow\batcolors`,
  and `senv.bat`, `build.bat`, `check.bat`, `run.bat` call
  `%PRJ_DIR%\tools\batcolors\echos.bat`. `senv` recreates it as a junction to
  `..\llm-shared\tools\batcolors`, and creates `tools\shcolors` the same way,
  to `..\llm-shared\tools\shcolors`: no script changes its path. `.gitignore`
  already holds `/tools/batcolors/` and gains `/tools/shcolors/`.
- The Linux side is the delicate part. `run`, `run_server`, `run_sentinel`,
  `kill_server` and `kill_sentinel` source
  `tools/dev_workflow/shcolors/echos`, and `.env` (lines 420 to 440) runs
  `git submodule update --init` for `tools/dev_workflow` and its nested
  submodules. Deployed hosts hold a my-project clone and no llm-shared, so no
  junction exists there. Those scripts source `tools/shcolors/echos` when the
  junction is present (a Windows development machine), and otherwise the
  tracked `tools/echos`, already an identical copy (same 67 lines). The `.env`
  bootstrap block goes away.
- `tools/deploy_pkgs.sh` documents a failure caused by the submodule recursion
  of `git status` on a host (`GIT_EXEC_PATH` workaround): that problem goes
  away with the submodule, the workaround can stay.
- Version sources: the built-in plugins cover `version.txt`, `pyproject.toml`,
  `uv.lock`, `pom.xml` and `PDF/pom.xml`; `cicd/config/.env` becomes one
  `pattern` source. `tools/set_version.py` and `tools/check_versions.py` can
  then retire, and `check.bat` calls `versions check`. Today only
  `version.txt` and `pom.xml` follow a `brel`, and `check.bat` catches the
  drift afterwards.
- Convert its `.changelog.fixes` (32 rules) with `fixes init`.
- Remove the `tools/dev_workflow` submodule.
- Audit `publish_pdf_nexus*.sh` and other version menus so snapshot tags are
  excluded from release choices unless snapshot intent is explicit. Keep this
  external-script work in the my-project effort, with the shared tag policy as
  its contract.

### workspace-halo, for its own effort

It never had `dev_workflow`, so this is onboarding, not removal:

- `build.bat` gains the `pre` / `post` calls around its existing test gate and
  VSIX packaging; `senv.bat` loads llm-shared's `senv.doskey` (or only its
  release aliases) and warns when `..\llm-shared` is missing (today `pwiki`
  just fails).
- Its `CHANGELOG.md` is hand-written, marketplace style (`## 0.0.24` with
  user-facing bullets), and ships inside the VSIX. git-cliff output would
  replace it with commit subjects, so workspace-halo needs the `curated`
  changelog mode, with no `changelog-header.md`; it then never needs
  git-cliff either.
- `package.json` and `package-lock.json` use the `release-only` form: they
  synchronize to `0.0.25` while `version.txt` reads `0.0.25-SNAPSHOT`, and
  remain `0.0.25` at release. Never insert `-SNAPSHOT` into the VSIX version.
- Its tags mix `0.0.21`, `0.0.22` and `v0.0.20`, `v0.0.23`, `v0.0.24`. The
  engine creates `vX.Y.Z`; the changelog range search must not trip on the
  older unprefixed tags.

## Decisions on the draft questions

Reconciled with `a.comments.on.draft.v0.14.0.sibling_release_tooling.md`
on 2026-10-09 and extended with draft contracts on 2026-10-15. These decisions
supersede the external git-cliff installation and tag-from-any-mode proposals.
The 2.14.2 pin is a researched recommendation,
not a claim that binary compatibility or implementation has been validated.

| # | Topic | Decision |
| --- | --- | --- |
| 1 | Per-project settings | `.release.ini` at the project root; setup generates/merges it and supplies explicit version, tooling and archive policy |
| 2 | Fix-rules file | Preparation automatically converts legacy `.changelog.fixes` when TOML is missing; `convert` is an optional maintenance command; direct brel can use the in-memory transition reader |
| 3 | Release trigger | A confirmed workflow merge to `main` includes automatic release continuation after preparation/readiness gates; a fresh on-main run keeps an explicit final tag choice |
| 4 | Integration confirmation | Feature-to-umbrella merges remain untagged; confirm umbrella-to-develop integration separately, allow multiple umbrellas there, then separately confirm the complete merge-and-release to main |
| 5 | Format registration | Explicit tuple only in llm-shared's `tools/release_workflow/sources/__init__.py`; adapter completeness/contract tests; all participating ecosystems run in one project |
| 6 | Python snapshot form | `pyproject.toml` and the uv root use plain `X.Y.Z` while `version.txt` can use `X.Y.Z-SNAPSHOT` |
| 7 | llm-shared discovery | `%~dp0..\llm-shared` first, a valid `LLM_SHARED_DIR` as fallback; llm-shared itself uses its own launcher. An explicitly selected upgrade checkout must actually execute, without silently reverting to the default sibling |
| 8 | Tooling provenance and updates | Capture the executing revision after any approved upgrade in `Release tooling:`; an alias and preparation stage check/propose latest compatible stable tooling |
| 9 | my-project color scripts | `tools\batcolors` and `tools\shcolors` junctions created by project senv; apply relevant color cleanup to llm-shared too |
| 10 | Snapshot hash noise | No hash in the unreleased heading; `filter.changelog` dropped |
| 11 | Scope | llm-shared engine, preparation integration, reusable setup/upgrade tooling and first-consumer migration; external consumers keep separate efforts |
| 12 | `senv_dev_workflow` | Archive in the my-project effort only after both llm-shared and my-project have migrated; README links to llm-shared migration docs |
| 13 | Version authority | `version.txt` first token is authoritative; read is read-only; synchronization preserves title, notes and unrelated content |
| 14 | Detection and locks | Combine every participating ecosystem; detect roots/reactors, explicitly register nested components, update only local lock/internal-parent versions; reject ambiguity |
| 15 | npm snapshot consistency | Default release-only uses the current anchor's core, never the previous published version; refuse downgrades |
| 16 | Project identity | Project senv sets identity before its guard; child calls cannot refresh parents. Engine validates an explicit root, aliases use the current worktree, build uses its own root; stale environment is diagnostic |
| 17 | Environment ownership | Caller/build initializes project senv once if needed; engine never reactivates it; release tooling and git-cliff provisioning need no global senv |
| 18 | git-cliff installation | llm-shared automatically downloads/verifies the exact pinned GitHub asset into an ignored internal version/platform cache when absent or invalid; reuse offline when valid |
| 19 | git-cliff pin | Recommend exact `2.14.2` after the documented comparison with 2.7.0; prove compatibility before cutover; later upgrades are deliberate pin changes, never floating latest |
| 20 | git-cliff invocation | Fixed internal absolute path and launcher-local `GIT_CLIFF`; no executable config or PATH discovery/mutation; provide shared `gcliff` alias and direct launcher |
| 21 | Missing git-cliff | Attempt automatic provisioning first; if unavailable, fail generated work before project mutation with an internal setup/download diagnostic; other operations remain usable |
| 22 | Changelog modes | Generated means commit-derived text with notes/date/fixes; curated means author-maintained bytes validated for exact headings/ranges, with no git-cliff/header dependency |
| 23 | Release gate and validity | Only main may release; pre creates release files/commit/unvalidated annotated tag; consuming gate owns success; post adds `[valid]` after identity checks; no push |
| 24 | Failure recovery | Restore only transaction-owned files, archive set, index, commit and tag with conflict checks; preserve merge/prepare commits, user changes and valid releases |
| 25 | Next snapshot and automation | Separate higher snapshot transition with consistent source forms and no tag change; explicit non-interactive choices, no hidden prompts |
| 26 | Snapshot tags | Development markers, never stable release baselines, release menu choices or recovery targets; share classification across engine, changelog, notes and release-plan readers |
| 27 | Changelog archives | Root holds recent releases/current snapshot; explicit mutable numeric ranges assign older sections to `docs/CHANGELOG.vA.B.C-vD.E.F.md`; reject overlap/loss/duplicates; preserve curated prose |
| 28 | Setup and migration | Dedicated `setup-release-tooling` skill/helper installs the real build contract/config/aliases, converts fixes and drives applicable legacy cleanup; idempotent and reviewable |
| 29 | Outdated llm-shared | Show installed/required/target versions and offer the concrete update; preserve development checkouts/local edits; restart/recheck before release, not midway through a transaction |
| 30 | First release with new engine | llm-shared is first consumer; isolated parity precedes removal, but actual `v0.14.0` on main must use the new engine and record gate/tag evidence |
| 31 | Version notation | Bare `X.Y.Z[-SNAPSHOT]` for anchor/config/version arguments and ecosystem forms; `vX.Y.Z` for new stable tags, generated headings and effort/archive filenames |
| 32 | Self-release identity and finalization | Allow only the owned preparation-to-release commit transition and enumerated release-file changes; keep engine content unchanged and provenance truthful. Finalization may replace only the exact owned unvalidated annotation to add `[valid]` |
| 33 | Release-version uniqueness and order | Existing `X.Y.Z` and `vX.Y.Z` both reserve the same release version. Target must be higher than every eligible reachable stable release on main; lower maintenance releases require a later, separate policy (Q2 A) |
| 34 | Persistent tag eligibility | New unvalidated releases stay ineligible without a local journal, including in another clone; historical exceptions need distinguishable evidence. Mechanism deferred to design |
| 35 | Release scope and continuation | Identify all included efforts, confirmed range and one release version; resolve target conflicts explicitly. Preserve scoped intent/progress across interruptions, recheck completion and renew decisions when scope changes |
| 36 | Compatibility and usable upgrades | Establish support for actual config/operations and runtime readiness; numeric minimum alone is insufficient. Execute the selected checkout, preserve prior usable setup on failure; mechanism deferred to design |
| 37 | Platform and runtime scope | Windows x64 only initially for v0.14.0 (Q1 A). Setup/upgrade reuses llm-shared's setup process to prepare or repair its own Python environment and required dependencies; accepted setup/upgrade produces runnable tooling (Q4 A). No consumer Python fallback or mid-release repair |
| 38 | Historical changelog authority | Preserve existing released generated sections during ordinary rendering; changed rules do not rewrite history automatically. Revisions require an explicit action, preserve editorial notes and expose conflicts/changes; archive moves preserve bodies and curated bytes remain unchanged (Q3 A) |
| 39 | Internal component references | Supported transitions keep participating components' internal references consistent; unsupported/ambiguous arrangements fail before writes. External dependencies stay unchanged; supported formats are bounded in child requirements |
| A | Release choice wording | Main merge confirmation names its release/tag consequence; fresh on-main run offers `Stop here` or `Go ahead, and tag the release` |

The ordered list grows from seven to eight items: add setup/migration/upgrades
before workflow integration and cutover. Existing slugs are retained; item 3's
title and contract now describe automatic internal provisioning. Archive policy
belongs to changelog management, shared tag classification to version sources,
and the callers adopt it in preparation integration. All work remains pending.
The 2026-10-15 contracts fit these same eight items. The user confirmed
Q1 A, Q2 A, Q3 A and Q4 A; these choices settle policy and scope while leaving
implementation mechanisms to the child designs.

## List of feature-requests and issues to create

| Order | Type | Key title | Slug | Status | Requirement | Validation plan |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Feature-request | Establish explicit release project identity | `release-project-root` | pending | - | - |
| 2 | Feature-request | Synchronize authoritative project versions | `version-sources` | pending | - | - |
| 3 | Feature-request | Provision pinned git-cliff automatically | `git-cliff-provisioning` | pending | - | - |
| 4 | Feature-request | Manage generated and curated changelogs | `changelog-management` | pending | - | - |
| 5 | Feature-request | Complete the guarded build release lifecycle | `build-release-lifecycle` | pending | - | - |
| 6 | Feature-request | Set up and upgrade sibling release tooling | `release-tooling-setup` | pending | - | - |
| 7 | Feature-request | Integrate release preparation with the engine | `prepare-release-integration` | pending | - | - |
| 8 | Feature-request | Migrate llm-shared to sibling release tooling | `llm-shared-cutover` | pending | - | - |

### Requirement details for the umbrella

#### 1. Establish explicit release project identity

- Type: Feature-request
- Key title: Establish explicit release project identity
- Slug: `release-project-root`
- Regroups: project identity timing/process lifetime, explicit root validation,
  root-scoped Git/file/artifact operations, Python engine and self-locating
  launcher foundation, common `.release.ini` parsing and worktree dispatch.
- Boundary rationale: one target-selection contract precedes every operation;
  this supplies shared plumbing, while setup and cutover activate consumers.
- Depends on: none.
- Ownership: engine entrypoint, shared launcher, common config reader and
  dispatcher; neither ecosystem synchronization nor release state.
- Acceptance criteria:
  - Require a normalized exact Git worktree top-level. Missing/invalid root
    fails before mutation; derive project name there and target every Git call.
  - Stale/absent `PRJ_DIR` cannot redirect calls. Alias dispatch from subfolders
    uses that worktree, warns with both roots on mismatch and fails outside Git;
    full-path build calls use their own root.
  - Verify identity before senv guards, subprocess inheritance, PowerShell
    parent isolation, directory changes and linked worktrees. Engine never
    calls senv; document same-process caller initialization.
  - Self-locate tooling/Python; separate `LLM_SHARED_DIR` from consumer root,
    honor artifact home, reject managed paths outside the selected tree and
    keep consumer scratch files out of the tooling checkout. Item 3's managed
    binary cache is a distinct permitted write area.
  - Parse config without interpolation, validate unknown keys/paths and preserve
    quoted arguments/non-interactive options through dispatch.
  - Support Windows x64 only initially and diagnose unsupported platforms before
    project mutation. Validate the selected tooling's Python/runtime readiness.
    Never substitute consumer Python; keep an explicitly selected upgrade
    checkout from being shadowed by default discovery.

#### 2. Synchronize authoritative project versions

- Type: Feature-request
- Key title: Synchronize authoritative project versions
- Slug: `version-sources`
- Regroups: anchor parsing/token-only writes, read/list/set/check, shared adapter
  protocol/registration, all participating ecosystems, form mapping, locks,
  pattern sources, version notation and snapshot/stable tag classification.
- Boundary rationale: independent version authority and release-range semantics
  must be available before generation/lifecycle callers. This item owns the
  reusable atomic source transition/restoration primitive, not commits or tags.
- Depends on: `release-project-root`.
- Ownership: adapters, detection/config/write contracts, shared tag classifier
  and range selector; item 5 consumes them for the release state machine.
- Acceptance criteria:
  - Read version/title/notes without creating a file; missing/malformed anchor
    fails. Set changes only its token and synchronizes every participating
    source; preserve unrelated bytes/formatting and restore the complete set
    after failure, including locks and pre-existing file absence.
  - Detect Python/uv local root, npm root manifest/lock, Maven reactor/internal
    parents and declared single-capture pattern sources. Exclude dependencies,
    vendor/examples and nested foreign repositories; reject ambiguous, dynamic
    or unsupported forms with a remedy.
  - Run all detectors: Python plus Node in one project updates both sets.
    Include declared nested component roots; report conflicting file claims.
    Keep adapter registration only in llm-shared, with completeness and contract
    tests so a new ecosystem needs no consumer copies or orchestration edits.
  - Map snapshot `1.2.3-SNAPSHOT` to `1.2.3` for Python/default npm and retain
    the suffix for Maven/configured sources. Release maps all to `1.2.3`;
    npm release-only refuses downgrades and never keeps the old published core.
  - Update uv local-root/npm root lock fields only; preserve schema/dependency
    metadata for external dependencies and external/inherited Maven versions.
    No opportunistic dependency resolution or global replacement of fields
    named version.
    Define the supported internal component-reference boundary and maintain
    consistency within it; unsupported or ambiguous arrangements fail before
    any source writes, rather than leaving sibling references on an old version.
  - List each file/form; check reports actual/expected drift with nonzero exit.
    Future formats remain unsupported until their adapters are added.
  - Recognize complete stable tags and snapshot markers separately. Exclude
    snapshots and known unvalidated releases from baseline selection, support
    legacy stable tags, no-stable-tag histories and ambiguous-tag diagnostics.
    Never parse a snapshot suffix as a git-describe commit count. Expose this
    selector to changelog, notes and release-plan callers.
    Eligibility must remain correct in another clone or without a local journal;
    missing evidence cannot turn a new unvalidated tag into a legacy release.
    Treat prefixed/unprefixed stable spellings as one release version. Require
    a target higher than every eligible reachable stable release on main and
    expose this rule to lifecycle callers. Lower maintenance releases require
    a later, separate policy; preserve the existing no-stable-release behavior.

#### 3. Provision pinned git-cliff automatically

- Type: Feature-request
- Key title: Provision pinned git-cliff automatically
- Slug: `git-cliff-provisioning`
- Regroups: internal cache/downloader, exact pin, compatibility policy and the
  2.7.0-to-2.14.2 research, fixed `GIT_CLIFF`, `gcliff` launcher/alias contract,
  concurrency/integrity checks and dependency-specific preflight errors.
- Boundary rationale: rendering needs predictable availability without exposing
  an installation task to the consumer; no external binary discovery remains.
- Depends on: `release-project-root`.
- Ownership: asset selection/download/cache, direct invocation, version checks;
  setup/cutover expose the alias, while item 4 decides when rendering needs it.
- Acceptance criteria:
  - Read an exact project/default pin, compute its ignored internal
    version/platform path and reuse a valid cached binary without network.
    No executable override, PATH search/mutation, PRGS or senv dependency.
  - Automatically download the correct GitHub release asset if absent/invalid,
    verify integrity/version, safely extract and atomically publish under a
    cache lock; handle concurrent users, interrupted downloads and offline use.
    Support Windows x64 only initially and diagnose other platforms before
    project mutation.
  - Report internal path/pin and precise setup/network/verification failure
    when provisioning cannot supply the binary. Never require manual git-cliff
    installation. Do this before consuming-project managed-file/Git mutation.
  - Direct launcher and interactive `gcliff` share provisioning; scripts do not
    depend on doskey expansion. Inside a project use its pin, outside use the
    llm-shared default; leave the parent's environment unchanged.
  - Establish tested compatibility for the proposed exact 2.14.2 pin using
    real templates/parsers and histories. Record intentional differences from
    observed 2.7.0; no floating latest or silent pin upgrade at release time.
  - Version operations, ordinary builds, curated validation and fix conversion
    remain available without provisioning; cache state never joins a commit.

#### 4. Manage generated and curated changelogs

- Type: Feature-request
- Key title: Manage generated and curated changelogs
- Slug: `changelog-management`
- Regroups: default/project cliff config, header, stable ranges, exact-once notes,
  snapshot/release headings, groups/duplicates, generated/curated modes,
  built-in cleanups, declarative fixes/conversion and configurable archives.
- Boundary rationale: one owner manages content/range placement and preservation;
  item 5 owns release commits/tags and transaction recovery.
- Depends on: `release-project-root`, `version-sources`, `git-cliff-provisioning`.
- Ownership: renderer/validator, fix-rule runner and changelog/archive settings.
- Acceptance criteria:
  - Generated mode uses explicit project/default config, required header and
    stable-tag selection, injects anchor notes once, labels groups, preserves
    historical notes/dates and avoids duplicate target sections. Repeated runs
    on unchanged inputs produce identical output.
    Preserve existing released sections during ordinary rendering, including
    when fix rules change. Historical revisions require an explicit action;
    preserve editorial notes, report competing content sources and expose
    intentional revisions in the proposed changed set. Archive moves preserve
    section bodies.
  - Use hash-free `## [vX.Y.Z-SNAPSHOT unreleased] <title>` and dated
    `## [vX.Y.Z] - YYYY-MM-DD - <title>` headings, with the captured release date.
    No filter.changelog; snapshot tags never truncate commits or create a
    released section, including a snapshot marker on HEAD.
  - Apply numeric recent/archive policy to root plus
    `docs/CHANGELOG.vA.B.C-vD.E.F.md`; validate bounds, destinations, overlap,
    coverage and links. Repartition complete sections when bounds change,
    including owned obsolete archive removal, without losing content.
  - Curated mode validates exact supported headings (including `## X.Y.Z`),
    ranges and links while preserving every file byte; no automatic generation,
    archive movement, git-cliff, header or fix-rule prerequisite.
  - Apply built-in cleanups before TOML rules to content being generated,
    preserving existing released sections during ordinary rendering. Convert
    only supported Perl push pairs/legacy arrows; name unsupported lines or invalid regex rules
    and fail. TOML wins over legacy with a warning; dry-run gives match counts.
  - `uc`/`uvf` and preparation provision/check git-cliff before automatic fixes
    init/conversion. A direct release uses the in-memory transition reader,
    without making the tree dirty with a new untracked rules file.
  - Assemble/validate all output before writes; failures restore the complete
    affected changelog set. Use unique project artifacts and expose the exact
    write/delete set to preparation/release recovery. Compare legacy output
    with documented intentional differences, including the two llm-shared rules.

#### 5. Complete the guarded build release lifecycle

- Type: Feature-request
- Key title: Complete the guarded build release lifecycle
- Slug: `build-release-lifecycle`
- Regroups: pre/post and build contract, main-only release readiness, dirty
  policy, transaction evidence/environment handoff, release annotation/trailer,
  consuming gate, validity, recovery and separate next-snapshot transition.
- Boundary rationale: source/changelog contracts precede one owner of all
  release state; never infer parity from version.txt alone or port cancellation
  that blindly resets HEAD/deletes the newest tag.
- Depends on: `release-project-root`, `version-sources`,
  `git-cliff-provisioning`, `changelog-management`.
- Ownership: release/snapshot state machine, recovery and generic build contract;
  the consumer retains its real gate, setup later installs the integration.
- Acceptance criteria:
  - Preflight main branch, clean/readiness policy, prepared title/notes, sources,
    configuration and absence of both prefixed and legacy tags for the target
    version. Require a target higher than every eligible reachable stable
    release on main; lower maintenance releases require a later, separate
    policy. Preserve the existing no-stable-release behavior.
    Provision generated-mode git-cliff before project writes; other branches
    reject release mutation. Dirty managed files fail; unrelated dirty opt-in
    preserves user worktree/index state.
  - Synchronize release forms/locks and render or validate the complete
    changelog set before a narrowly scoped release commit and annotated
    `vX.Y.Z`. Reuse title/notes/date; record the executing tooling revision.
    Snapshot tags remain untouched and cannot stand in for release tags.
  - Pre failure skips the gate; every gate outcome reaches post with root and
    transaction identity. Only a successful owned gate adds `[valid]`; check
    source/tooling identity with the documented self-release exception, including
    the owned HEAD transition while engine content stays unchanged. Failed
    post fails the release even after a green gate; never push. Replace only
    this transaction's exact unvalidated annotation during finalization; preserve
    the target and existing content, and never overwrite a conflicting/valid tag.
  - Exercise failures before/between writes, rendering, commit, tag creation,
    gate and finalization. Restore only owned baseline state, preserving user
    edits/index, merge/prepare commits and valid releases. Include new/deleted
    archives and file absence; no blanket reset, clean or stash restoration.
  - Recover skipped post/interruption with conflict checks and durable evidence;
    repeat post/recover safely. Never let crel remove an unrelated snapshot tag
    or valid release; report incomplete recovery truthfully.
  - Serialize same-root/shared-tag mutations across worktrees, allow independent
    projects, escape/clean unique handoffs and keep consumer scratch state local.
  - Keep br equivalent to brel. Ordinary builds do not bump; next snapshot is
    a separate higher-version commit with consistent forms and unchanged tags.
    Preserve notes unless replaced; explicit automation choices never prompt.

#### 6. Set up and upgrade sibling release tooling

- Type: Feature-request
- Key title: Set up and upgrade sibling release tooling
- Slug: `release-tooling-setup`
- Regroups: dedicated setup skill/helper, build/config/alias installation,
  reusable migration checks, minimum/latest tooling checks and update alias.
- Boundary rationale: adoption and subsequent upgrades share ownership of the
  consumer's tooling integration. This delivers reusable machinery; item 8
  applies it to llm-shared and external consumers migrate in their own efforts.
- Depends on: `release-project-root`, `version-sources`,
  `git-cliff-provisioning`, `changelog-management`, `build-release-lifecycle`.
- Ownership: setup/migration/update helper, skill and LLM adapters, config/build
  templates, direct launchers and proposed llmup alias. Follow adapter rules.
- Acceptance criteria:
  - Inspect the consuming build, preserve its gate/arguments/status and install
    correct pre/post calls, including all-argument missing-tooling handling.
    Generate/merge .release.ini with pin, minimum, mode/archive policy and
    participating roots; preserve existing project settings/comments.
  - Produce reviewable files, preview/non-interactive forms and idempotent
    repeat runs; report unsupported layouts without replacing arbitrary code.
    Support both sibling discovery and llm-shared's own launcher.
  - Expose release aliases plus gcliff/update aliases without global senv;
    automatically convert fixes and identify init/color/filter/submodule
    callers requiring migration. Never remove legacy tooling before checks pass.
  - Check installed/required/latest compatible stable versions and offer a
    concrete update in the resolved tooling checkout. Distinguish required
    upgrades from optional newer releases; compatible offline use remains valid.
    Establish compatibility for actual configuration/required operations, rather
    than just a numeric minimum; cover the self-development candidate explicitly.
  - Preserve dirty/divergent/development checkouts and active release revisions;
    no destructive update. After an approved update restart/revalidate before
    preparation. Explicit non-interactive policy replaces hidden prompts.
  - Keep llm-shared self-development on its candidate engine; offer a separate
    stable checkout when appropriate, never overwrite cutover work. Pin updates
    for git-cliff are separate deliberate config edits with compatibility evidence.
  - Support Windows x64 only initially. Reuse llm-shared's setup process to
    prepare or repair its own Python environment and required dependencies;
    accepted setup/upgrade produces runnable tooling. Verify readiness after
    setup/update, and demonstrate that the consumer executes the selected
    checkout even when a default sibling still exists.
    Failed upgrades retain the prior usable setup and block unintended release
    continuation; do not report a checkout change alone as a usable upgrade.

#### 7. Integrate release preparation with the engine

- Type: Feature-request
- Key title: Integrate release preparation with the engine
- Slug: `prepare-release-integration`
- Regroups: preparation/notes/planner callers, steps 10 to 14, automatic fixes,
  archives/source staging, tooling upgrade stage, branch confirmations/release
  continuation, trailer template and synchronized LLM-specific adapters.
- Boundary rationale: workflow consumes complete reusable engine/setup services;
  it must switch every caller before legacy removal in item 8.
- Depends on: all six earlier items.
- Ownership: canonical preparation/notes instructions and supporting range-reader
  code, templates and adapters; no duplicated source writers or recovery logic.
- Acceptance criteria:
  - Steps 10/11 call explicit-root changelog services with automatic provisioning
    and fixes conversion; Step 12 uses versions set/check; Step 13 stages the
    exact source/fix/config/archive set. Preserve title/notes and human editing.
  - Replace unfiltered last-tag queries in notes, release planning and documentation
    scope with the shared stable selector. Test stable then snapshot tags,
    snapshot at HEAD and histories containing only snapshot markers.
  - Run the tooling upgrade check before preparation, offering the helper's
    concrete action and revalidating after update. Record the executing revision
    in the final trailer, never a recommended-but-unused version.
  - Unfinished umbrellas merge items back and hand off the next pending item,
    with no tag. Exhausted umbrella/standalone integration requires the exact
    proposed merge confirmation; allow stopping on develop for other umbrellas.
  - Confirm the complete merge to main and its release consequence separately.
    After that merge, automatically continue through preparation/readiness and
    the consuming release gate/tag. A fresh on-main run keeps explicit tag intent;
    checking out main or merely completing an umbrella supplies none.
  - Identify all included efforts and one target version; require completion
    of included umbrellas and explicit resolution of conflicting targets before
    the main-merge confirmation. Apply the shared rule requiring a target higher
    than every eligible reachable stable release on main. Notes cover the
    complete confirmed range.
    Persist enough intent/progress to resume the same release after interruption
    without duplicating completed actions. Account for owned preparation changes;
    a changed range/version needs a new decision, missing evidence confers no
    authorization, and cancellation does not silently resume a release.
  - Missing build contract/compatible tooling blocks release continuation; do
    not tag on integration branches. Propagate non-interactive intent, never
    push, and report actual recovered/conflicted/unvalidated outcomes.
  - Update boundaries/template for token-only changes, ecosystem forms, date,
    provenance and separate snapshot. Synchronize adapters according to
    rules/llm-specific-adapters.md and validate workflow contracts.

#### 8. Migrate llm-shared to sibling release tooling

- Type: Feature-request
- Key title: Migrate llm-shared to sibling release tooling
- Slug: `llm-shared-cutover`
- Regroups: first-consumer setup, build/senv/aliases, colors/init removal,
  ignored binary cache, rules/config/archives, legacy submodule/filter removal,
  docs and a separate actual v0.14.0 release-closeout record.
- Boundary rationale: apply the reusable machinery only after engine and callers
  exist. External consumer edits/archival stay outside this repository effort.
- Depends on: all seven earlier items.
- Ownership: llm-shared consumer cutover, migration docs and release evidence;
  release execution still follows its explicit integration/main authorization.
- Acceptance criteria:
  - Use setup on llm-shared itself; switch build/version calls to its own launcher,
    keep its real gate and script-derived root, refresh identity before guards,
    expose shared aliases once and remove duplicate legacy initialization.
  - Convert its two fix rules automatically; add explicit config/pin/archive
    policy and cache ignore; use direct colors/add shcolors on linux branch.
    Remove dev_workflow/.gitmodules and only the obsolete Git filter after
    callers and parity/recovery checks pass.
  - Rehearse on isolated histories using legacy scripts for comparison, with
    documented intentional version/lock/changelog/trailer/snapshot differences.
    Include validity and failure recovery; retain evidence before removal.
    Include llm-shared's owned HEAD transition with unchanged engine content,
    legacy spelling collisions and tag eligibility without a local journal.
  - Implementation completion requires the installed engine, passing rehearsals
    and a documented release-closeout evidence checklist. After the authorized
    main release, record the real `v0.14.0` tag/commit created by the new engine,
    executing tooling trailer, consuming gate and `[valid]`. Keep this release
    outcome pending separately until then; it must not block completion of the
    implementation row that makes the umbrella eligible to release.
  - Update DEVELOPMENT and all named wiki/instruction references. Document
    setup/migration helper usage, generated config, automatic git-cliff caching,
    archive changes, snapshot tags and tooling upgrades, with concrete examples.
  - Present/link Diataxis in order: explanation, tutorials, how-to guides,
    reference. Each page serves one purpose; onboarding/migration how-tos use
    the delivered skill/helper, and reference explains their generated contract.
  - Preserve my-project/workspace-halo inputs as external follow-ups, including
    snapshot-aware publishing menus. Archive dev_workflow only after both
    llm-shared and my-project migrated, from the latter effort, with README links.

All rows remain `pending`; requirement and validation-plan paths stay `-` until
later workflows create and complete them. The ordering respects dependencies.
This is refinement of the canonical umbrella under `docs/v0.14.0/`; it creates
no child requirements, implementation branches, commits or release tags.

## Confirmed answers on the 2026-10-15 contracts

The user confirmed Q1 A, Q2 A, Q3 A and Q4 A on 2026-10-15. These policy/scope
choices are incorporated in the contracts, decision table and acceptance
criteria above. Storage formats, compatibility protocols, checkout selection,
runtime versions and installation mechanisms, and adapter algorithms remain
child-design work.

### Q1. Supported platforms for v0.14.0

- **Confirmed answer: A — Windows x64 only initially.** Covers launchers,
  release lifecycle, git-cliff provisioning and setup/cutover. Other operating
  systems and architectures require later scope; unsupported platforms receive
  a clear diagnostic before project mutation.
- Applies to items 1, 3, 5, 6 and their cutover validation.

### Q2. Previously unused lower release versions on main

- **Confirmed answer: A — Require a version higher than every eligible
  reachable stable release on main.** Lower maintenance releases require a
  later, separate policy. Existing `X.Y.Z` or `vX.Y.Z` always prevents another
  release of that version. The existing no-eligible-stable-release behavior
  remains unchanged.
- Applies to items 2, 5 and 7.

### Q3. Authority of released generated-changelog sections

- **Confirmed answer: A — Preserve existing released sections during ordinary
  rendering; require an explicit action to revise them.** Changed fix rules do
  not update released history automatically. Moving sections between archives
  preserves their bodies. Intentional revisions preserve editorial notes and
  expose changes and conflicts. Curated mode remains byte-preserving.
- Applies to item 4 and its preparation/cutover callers. The explicit revision
  action and content representation remain design work.

### Q4. Responsibility for an absent or outdated tooling runtime

- **Confirmed answer: A — Setup/upgrade reuses llm-shared's setup process to
  prepare or repair its own Python environment.** An accepted setup/upgrade
  produces runnable tooling with the required dependencies. The release engine
  does not activate project/global senv, repair itself mid-release or fall back
  to the consuming project's Python.
- Applies to items 1 and 6, with readiness enforced by 5 and exercised by 8.
  Runtime versions and installation mechanisms remain design work.
