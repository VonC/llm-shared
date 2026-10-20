# Establish explicit release project identity

- Type: feature-request
- Test group: whole suite
- Target version: v0.14.0
- Slug: release-project-root
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md

## Draft basis and user need for release project identity

As a maintainer using shared release tooling across repositories and linked
worktrees, I need each command to identify its target project and executing
tooling checkout unambiguously, so inherited environment settings or a change
of directory cannot redirect the operation or mix project artifacts.

The [focused draft](draft.v0.14.0.release-project-root.md) derives from item 1
of the [sibling release tooling umbrella](draft.v0.14.0.sibling_release_tooling.md).
Its confirmed refinements cover inherited Git settings, actual path
destinations, failure reporting, invalid configuration, artifact side effects
and the existing missing-tooling build rule. This requirement records those
outcomes without choosing their implementation.

## Current behavior before the v0.14.0 tooling change

Version and changelog management lives in the `tools/dev_workflow` submodule.
Legacy `update-changelog.sh` Git operations, including `show-ref`, `cat-file`,
tag enumeration and `describe`, depend on the current directory. A stale
`PRJ_DIR` and a changed directory can therefore describe different projects.

The umbrella records that llm-shared's root `senv.bat` derives `PRJ_DIR` from
its own location and sets `PRJ_DIR_NAME` before the
`NO_MORE_SENV_%PRJ_DIR_NAME%` guard. Its `build.bat` derives its own root,
activates that project's environment, then runs release preprocessing. A child
process cannot refresh its parent's environment; changing directories also
does not refresh project identity.

Legacy scratch files are written under `tools/dev_workflow` and at the project
root. Moving release tooling into a shared checkout requires those writes to
remain associated with the consuming project when several projects run at once.

## Scope of the release-project-root foundation

This item owns the engine entrypoint, shared launcher, common configuration
reader and dispatcher. It establishes project selection, tooling selection,
runtime readiness and the boundaries for Git, files and artifacts.

The umbrella's working names are `tools/release_workflow/` and
`bin/release_workflow.bat`, with tests under `tests/`. These are inherited
context. Selection mechanisms, normalization algorithms, internal interfaces,
exact exit-code numbers and output formats remain design work.

The remaining ownership boundaries are:

| Umbrella item | Behavior owned by that item |
| --- | --- |
| 2, version-sources | Version authority, ecosystem participation, synchronization and checks |
| 3, git-cliff-provisioning | Managed binary download, cache and provisioning policy |
| 4, changelog-management | Generated/curated behavior, archives and fix rules |
| 5, build-release-lifecycle | Consuming build gate, release transactions, handoff and recovery |
| 6, release-tooling-setup | Installation, runtime preparation/repair, upgrades, compatibility and alias installation |
| 7, prepare-release-integration | Release preparation workflow integration |
| 8, llm-shared-cutover | Migration of llm-shared to its own tooling |

## Target selection for release callers

| Caller | Required target behavior |
| --- | --- |
| Engine and standalone launcher | Require an explicit root, normalize it and require the exact Git worktree top-level. Never infer a missing root from `PRJ_DIR` |
| Interactive aliases `b`, `br`, `brel`, `crel`, `gv`, `uc`, `uver`, `uverr`, `uvf` | Resolve the current directory's Git worktree top-level and pass it explicitly through the shared launcher. Fail outside a Git worktree |
| Project `build.bat` | Use its own directory, validated as the worktree root, regardless of the caller's directory. Call its own `senv.bat` once before preprocessing and pass the script-derived root |

An absent `PRJ_DIR` is allowed when an explicit root is valid. A stale value is
diagnostic context: report the mismatch and use the validated root. Alias
mismatch warnings name both roots. Derive the project name from the validated
root; `PRJ_DIR_NAME` cannot override it.

Every Git invocation supplies `-C <root>` or an equivalent explicit working
directory. Inherited Git settings, including `GIT_DIR`, `GIT_WORK_TREE` and
`GIT_INDEX_FILE`, must not redirect root validation or operations to another
repository, worktree or index. An explicit working directory alone does not
establish that guarantee.

For example, an operation explicitly targeting B after the shell was initialized
for A must use B even if inherited Git settings still name A. Approved design
answer Q01 A isolates those settings for each Git subprocess, including root
validation. It removes inherited routing and configuration-injection inputs,
diagnoses ignored conflicts and preserves compatible identity, signing and
credential settings. The parent shell stays unchanged; no extra checkout,
container or sandbox is required. The design owns the complete isolation policy.

Treat equivalent path spellings consistently. Managed project files and
artifact paths must remain inside the selected worktree and outside nested
foreign repositories, including their actual destinations through symbolic
links or Windows junctions. Linked worktrees retain distinct project roots
even when Git objects and tags are shared.

Project files, configuration and artifacts resolve against that root. Compute
the legacy locations represented by `VERSION_TXT_FILE`, `POM_FILE`,
`PACKAGE_JSON_FILE`, `HEADER_CHANGELOG_FILE`, `DEV_WORKFLOW_DIR` and
`PRJ_DIR_unix` inside the engine without exporting those environment variables.
Only the generated changelog command checks `changelog-header.md`; its
changelog behavior belongs to item 4.

## Environment lifetime and tooling identity

Keep the selected project root distinct from `LLM_SHARED_DIR`. They may coincide
when llm-shared releases itself. The shared launcher resolves its tooling root
from its own location instead of trusting an inherited variable naming another
checkout, and uses that checkout's bundled venv Python. Consumers need no
Python executable on their PATH and must never supply a fallback interpreter.

For ordinary consumer discovery, use the settled sibling location
`%~dp0..\llm-shared` first, then a valid `LLM_SHARED_DIR` fallback. llm-shared's
own build uses its own launcher. Once an upgrade explicitly selects a checkout,
that checkout must execute and its actual path must be reported; default
discovery must not redirect the operation to an older checkout.

Environment activation belongs to callers. Interactive cmd callers initialize
the chosen project's root `senv.bat`; when a guard left build tools
uninitialized, they clear that project's guard and activate in the same cmd
process, following [the shell policy](../../rules/run_commands.md). PowerShell
and automation callers use the full-path shared launcher with an explicit root,
or the project's full-path `build.bat`, which owns its build environment.
The engine never calls project or global `senv.bat`.

This contract covers identity assignment before guards, directory changes,
subprocess inheritance and separate shells. Doskey macros are per-console,
not a subprocess API. A batch file called from PowerShell cannot update the
parent PowerShell environment; independent calls cannot assume earlier
activation survived. External consumers verify their own build and environment
scripts during their migrations.

The launcher owns `chcp 65001` around its own run. Shared scripts use
`%LLM_SHARED_DIR%\tools\batcolors`, as recorded in the draft.

## Platform support and runtime readiness

The initial v0.14.0 scope is Windows x64. Other operating systems and
architectures receive a clear unsupported-platform diagnostic before project
mutation. Existing Unix deployment references do not extend this scope.

The selected tooling checkout has one authoritative, setup-managed Python
virtual environment: the interpreter and installed dependencies used by
llm-shared's tools, including the release engine. This is distinct from inherited
shell environment variables. No separate release environment or environment
per consumer is needed. A consumer build retains its own toolchain, but consumer,
other-project and global Python never participate in release-engine selection.

Approved design answer Q02 C requires the launcher to locate that authoritative
environment independently of caller activation and verify its readiness for the
executing revision. A checkout or interpreter alone does not prove readiness.
Older environment directories, if present, have no role in runtime selection
and cannot make a ready authoritative environment ambiguous. Release operations
stop before project mutation if that environment cannot be identified or is
unusable, with no consumer-PATH requirement, fallback or mid-release repair.

Setup and upgrade own designation, preparation, replacement and repair through
llm-shared's setup process. An accepted upgrade must be runnable and actually
invoke the selected checkout. This item supplies runtime location and readiness;
item 6 owns installation, upgrade and compatibility policy. The location
mechanism remains design work; a new selection-record file is not required by C.

## Configuration behavior at the selected root

Read `.release.ini` from the validated root. If it is absent, use the defaults.
If it exists but is unreadable, malformed or ambiguous, fail before mutation;
do not silently replace it with defaults. Diagnostics identify the file and
offending setting where possible.

Disable configuration interpolation so `%` and `$` in patterns need no escaping.
Validate modes, forms, paths and unknown keys before mutation. Treat project
configuration as data, never executable code. There is no git-cliff executable
configuration key; item 3 computes that internal path.

Existing files retain their meanings: `version.txt`, `CHANGELOG.md`,
`changelog-header.md` and `.exempt-files`. A project `cliff.toml` may override
the shared default; fix rules use `.changelog-fixes.toml`. The common reader
preserves settings while their owning items supply domain behavior:

| Configuration area | Owning item |
| --- | --- |
| Version-source settings, including forms and configured file/pattern pairs | 2 |
| Exact git-cliff pin | 3 |
| Generated/curated mode, archives and fix rules | 4 |
| Tooling minimum and compatibility | 6 |

For example, the draft's `file = cicd/config/.env` and
`pattern = ^APP_SERVICE_VERSION=(.+)$` values must reach their owner intact.
Its `form = release-only` for npm and `form = snapshot` for that configured
source remain domain settings, not behavior implemented by this foundation.

## Project artifacts and operations without mutation

Consumer scratch files must not be written into the shared tooling checkout.
The ignored, versioned git-cliff cache owned by item 3 is the distinct permitted
provisioning write area. Different projects may operate concurrently without
mixing their scratch files.

The draft identifies legacy `dirty_files.tmp`, `dirty_ignored_files.tmp` and
`run_filter.cmd` under `tools/dev_workflow/git/`, and `temp_tag_message.txt`
under `tools/dev_workflow/`. It also identifies project-root scratch files
`CHANGELOG.tmp.md`, `CHANGELOG.new.md`, `CHANGELOG.cleaned.md`,
`CHANGELOG.labeled.md`, `version.tmp.txt`, `.fixes_content.tmp` and
`tmp_fixes.pl`.

The umbrella expects most processing to remain in memory. Remaining output,
including git-cliff output, tag messages and the `pre` handoff, belongs in the
selected project's artifact home, default `.reviews`, according to the existing
[artifact rules](../../rules/artifact_files.md). The later items own the
operations that generate those artifacts.

Failure before project mutation includes ignored and untracked artifacts.
Invalid root/configuration and unavailable-runtime failures must not first
create the artifact home, move legacy scratch files or write a handoff.
Reading the current version and other read-only commands must not initialize
or migrate project artifacts.

Approved design answer Q06 A (2026-10-20) applies these destination and artifact
rules through common Python functions inside the release engine. A module is a
Python source file containing related functions; version, changelog and release
components are code executed by the one llm-shared Python selected in Q02.
The shared interface is the common functions and their accepted arguments.
The managed-write service is local code, requiring no additional interpreter,
environment, server or user prompt.

For example, changelog code prepares content and calls the common functions to
check the destination and write `CHANGELOG.md`; version code uses them for
`version.txt`. The alternative would repeat the checks and file-writing
instructions inside each component, using the same Python. A previously valid
destination can change through a redirected junction, so the common functions
recheck physical containment and repository boundaries before artifact
preparation or writes.

Each component completes its preflight before requesting changes and retains
transaction ordering, recovery and cleanup. Read-only resolution stays separate
from preparation. Linked-worktree Git metadata and the tooling cache keep their
distinct boundaries. The design and plan own the exact functions and filesystem
guarantees; a path recheck alone does not establish atomic protection against
every race.

## Dispatch, arguments and caller-visible results

The inherited command surface supplies dispatch context:

| Command form | Behavior owner beyond this foundation |
| --- | --- |
| `pre <root> [build args]`, `post <root> <build status>`, `recover <root>` | Item 5 |
| `version <root>`, `versions <root> list\|set <version>\|check` | Item 2, consumed by item 5 |
| `snapshot <root>` | Item 5 using item 2's source contracts |
| `changelog <root> [latest\|vX.Y.Z]`, `fixes <root> init\|convert\|dry-run` | Item 4 |

`b` routes an ordinary consuming build; `br` and `brel` route its `rel`
lifecycle. `gv` reads the version. `uc` and `uvf` refresh generated changelog
content or validate curated content. `uver` selects the separate next-snapshot
transition; `uverr` routes release intent through the consuming build gate.
`crel` routes ownership-checked recovery of an active unvalidated transaction;
it must not reproduce newest-tag reset/deletion against a valid release.

When the shared launcher cannot be found, the umbrella permits an ordinary
build with one warning and a read-only version display. It blocks any requested
release or snapshot transition, wherever the request appears among arguments.
This missing-launcher exception does not relax release runtime requirements.
Item 5 owns the build-lifecycle behavior; setup and cutover install it.

Every prompting operation must have a non-interactive form that fails with a
message when required input is missing. Preserve that choice through dispatch,
build, `pre` and `post`, without hidden batch `set /p` or downstream prompts.

Preserve quoted arguments and values containing spaces, quotes, `%`, `!`, `&`
and other batch metacharacters without executing notes or titles as commands.
The inherited build handoff names `project_version`, `project_title`,
`build_params`, `build_params_echos`, `build_must_fail` and `PRJ_REL_TITLE`.
Item 5 owns the transaction and handoff, including failure without a partially
usable result; this item owns safe dispatch.

Preserve failure status through launchers and dispatch so failure cannot appear
successful to the caller. Keep warnings and diagnostics, including stale-root
warnings, separate from command results consumed by callers, such as a version.
Exact exit-code numbers and output formats remain design decisions. Item 5
owns build-gate and postprocessing outcome rules.

## Acceptance criteria for the project identity foundation

| ID | Observable acceptance criterion |
| --- | --- |
| AC1 | Engine and standalone calls reject missing, invalid or non-top-level roots before mutation; a valid explicit root wins over stale or absent project environment values |
| AC2 | Aliases from a subfolder target its Git worktree and warn with both roots on an environment mismatch; outside Git they fail; a full-path build targets its own root |
| AC3 | Inherited routing and configuration injection cannot redirect root validation, repository operations or index operations; diagnose ignored conflicts, preserve compatible user settings and leave the parent shell unchanged; linked worktrees retain their own project identity |
| AC4 | Equivalent root spellings are treated consistently; managed-file and artifact destinations cannot escape the selected worktree or cross into nested foreign repositories through links or junctions |
| AC5 | Caller initialization and process-lifetime rules hold across guards, directory changes, subprocesses and PowerShell; the engine never activates senv |
| AC6 | The launcher uses its own tooling checkout and runtime, keeps consumer and tooling roots distinct and honors an explicitly selected upgrade checkout without default-discovery redirection |
| AC7 | Locate and validate the selected checkout's one setup-managed environment independently of caller activation; older environment directories do not affect selection. Unsupported platforms and an unidentified or unusable authoritative runtime fail before project mutation; no consumer, other-project or global Python fallback or mid-release runtime repair occurs |
| AC8 | Missing configuration uses defaults; unreadable, malformed or ambiguous configuration fails; interpolation is disabled, invalid settings are diagnosed and configuration is never executed |
| AC9 | Consumer artifacts stay in the selected project's configured artifact home; invalid-root/configuration/runtime failures and read-only operations do not create or migrate project artifacts |
| AC10 | Dispatch preserves quoted/metacharacter-containing values and non-interactive intent, propagates failure and keeps diagnostics separate from command results |
| AC11 | The missing-launcher boundary permits an ordinary build with one warning and read-only version display, while rejecting release/snapshot intent anywhere among the arguments; item 5 retains lifecycle ownership |

Validation uses the already selected whole suite. These criteria define
expected behavior; test organization and implementation mechanisms belong in
the design and plans.

## Existing references for the release-project-root requirement

- `senv.bat`: project identity before its guard, as recorded by the umbrella.
- `build.bat`: script-derived project root and caller-owned build environment.
- `tools/dev_workflow/update-changelog.sh`: legacy directory-sensitive Git
  operations identified in the draft.
- `bin/mds.ps1`: existing bundled-Python launcher example named by the umbrella.
- [Focused draft](draft.v0.14.0.release-project-root.md): approved scope and
  contract refinements.
- [Umbrella](draft.v0.14.0.sibling_release_tooling.md): shared contracts and
  ownership of items 2 through 8.

## Requirement clarifications

| Review outcome | Basis |
| --- | --- |
| No open questions, all requirement decisions made | The approved child draft and its contract refinements settle scope and expected behavior. Remaining mechanisms and interfaces belong to design; later umbrella items retain their domain behavior |
