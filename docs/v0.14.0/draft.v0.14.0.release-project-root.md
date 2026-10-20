# Establish explicit release project identity

- Type: feature-request
- Test group: whole suite
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Target version: v0.14.0
- Documentation layout: docs/v0.14.0/
- Slug: release-project-root

## Selected umbrella entry

| Order | Type | Key title | Slug | Status | Requirement | Validation plan |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Feature-request | Establish explicit release project identity | `release-project-root` | pending | - | - |

### Requirement detail inherited from the umbrella

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
  - Keep Git targeting isolated from inherited routing and configuration
    injection, including during root validation. Diagnose ignored conflicts,
    preserve compatible user settings and leave the caller's shell unchanged.
  - Verify identity before senv guards, subprocess inheritance, PowerShell
    parent isolation, directory changes and linked worktrees. Engine never
    calls senv; document same-process caller initialization.
  - Self-locate tooling/Python; separate `LLM_SHARED_DIR` from consumer root,
    honor artifact home, reject managed paths outside the selected tree and
    keep consumer scratch files out of the tooling checkout. Item 3's managed
    binary cache is a distinct permitted write area.
  - Parse config without interpolation, validate unknown keys/paths and preserve
    quoted arguments/non-interactive options through dispatch.
  - Compose explicitly registered schemas and defaults owned by the shipped
    llm-shared domains; reject conflicting ownership and validate every declared
    setting before mutation, including settings unused by the current command.
  - Allow projects to omit `.release.ini` when defaults suit them, or version
    only needed overrides at their root. Projects need no schema or validator
    definitions; invalid declarations never silently fall back to defaults.
  - Support Windows x64 only initially and diagnose unsupported platforms before
    project mutation. Locate and validate the selected checkout's one
    setup-managed Python environment, without selecting older directories or
    consumer/global Python. Keep an explicitly selected upgrade checkout from
    being shadowed by default discovery.

## Context and scope

Version and changelog management currently lives in the `tools/dev_workflow`
submodule. The umbrella replaces that engine with shared Python tooling in
llm-shared. This first child establishes which project and tooling checkout
each call uses, before the later children supply version, changelog and release
behavior.

The umbrella already proposes `tools/release_workflow/` as a working name,
`bin/release_workflow.bat` as its launcher, and tests under `tests/`.
These inherited names are draft context. The policy clarifications below reflect
the user's approved design answers Q01 A, Q02 C, Q03 A and Q06 A; detailed
enforcement, runtime-location and schema-registration mechanisms remain in the
design.

## Project identity and caller contracts

| Caller | Target selection | Missing or stale `PRJ_DIR` |
| --- | --- | --- |
| Engine and standalone launcher | Required explicit `<root>`; normalize it and require it to equal `git -C <root> rev-parse --show-toplevel` | Missing is allowed; stale is reported, but the validated explicit root wins. Missing or invalid explicit root fails without mutation; never infer a target from `PRJ_DIR` |
| `b`, `br`, `brel`, `crel`, `gv`, `uc`, `uver`, `uverr`, `uvf` aliases | Dispatch through a shared launcher, resolve the current directory's Git top-level, pass that root explicitly | Warn on mismatch, name both roots, then target the current worktree. Outside a Git worktree fail; never run the old environment's project |
| Project `build.bat` | Its own directory, validated as the worktree root, irrespective of caller directory | Call its own `senv.bat` once before preprocessing to refresh identity; pass the script-derived root anyway |

All project files, config, artifacts and Git operations resolve against the
validated root. Every Git invocation supplies `-C <root>` or an equivalent
explicit working directory. Reject nested foreign repositories and paths
outside the selected worktree for managed files. Derive the project name
from the root; a stale `PRJ_DIR_NAME` is not authoritative.

Inherited Git settings, including `GIT_DIR`, `GIT_WORK_TREE` and
`GIT_INDEX_FILE`, must not redirect root validation or later operations to
another repository, worktree or index. An explicit working directory alone
does not establish that guarantee. For example, after activating A, an explicit
operation on B must still target B even when these inherited settings name A.

Approved design answer Q01 A isolates each Git subprocess's inherited settings,
including during root validation. It removes routing and configuration-injection
inputs, preserves compatible identity, signing and credential settings, and
diagnoses ignored conflicts without changing the parent shell. This is Git
targeting isolation; it requires no new checkout, container or sandbox. The
design must define a complete policy beyond the three example variables.

Root identity must treat equivalent path spellings consistently. Containment
of managed project files and artifact paths applies to their actual
destinations, including paths through symbolic links or Windows junctions.
A path written beneath the root must not permit access to managed files
outside the selected worktree or inside a nested foreign repository. Path
normalization and containment mechanisms remain design work.

Legacy file-location variables (`VERSION_TXT_FILE`, `POM_FILE`,
`PACKAGE_JSON_FILE`, `HEADER_CHANGELOG_FILE`, `DEV_WORKFLOW_DIR` and
`PRJ_DIR_unix`) are computed inside the engine from the project root,
without exporting those environment variables. `changelog-header.md` is
checked only by the changelog command, and only in generated mode.

Keep `LLM_SHARED_DIR` separate from project identity. In llm-shared itself
the roots can coincide; in a consumer they do not. The shared launcher resolves
its tooling root from its own location instead of trusting an inherited
variable naming another checkout.

The legacy `update-changelog.sh` calls to `show-ref`, `cat-file`, tag
enumeration and `describe` depend on the current directory rather than
`PRJ_DIR`. Root validation and subprocess targeting must cover directory
changes, separate shells, subprocesses and linked worktrees.

## Environment timing and process lifetime

The umbrella records that llm-shared's `senv.bat` normalizes its own
`%~dp0` into `PRJ_DIR` and derives `PRJ_DIR_NAME` before the
`NO_MORE_SENV_%PRJ_DIR_NAME%` guard. Even a guarded call refreshes identity.
Its `build.bat` derives `build_dir` from its own script path, calls that
project's `senv.bat`, then invokes release preprocessing. The release engine
must not repeat that activation. External consumers verify their own scripts
during their separate migrations.

Environment values belong to the process that sets them. Calling `senv.bat`
in an interactive cmd session updates that session. A child inherits a copy
at launch and cannot update its parent. Changing directories does not refresh
identity; new shells can inherit another project's values. Linked worktrees
have different roots even when Git objects and tags are shared.

Doskey macros are per-console, not a subprocess API. Calling a batch file from
PowerShell runs it in a child cmd process whose assignments do not update the
parent PowerShell environment. Independent tool calls cannot assume an earlier
activation survived.

Interactive cmd callers initialize the chosen project's root `senv.bat`.
If inherited guards left build tools uninitialized, the caller clears that
project's guard and activates its environment in the same cmd process,
following [the shell policy](../../rules/run_commands.md). PowerShell and
automation callers use the full-path shared launcher with an explicit root,
or the project's full-path `build.bat`, which owns its build environment.
The engine never calls project or global `senv.bat`.

## Launcher, platform and selected runtime

The launcher locates llm-shared from its own path and uses llm-shared's bundled
venv Python, as the umbrella's `bin/mds.ps1` example already does for
`pwiki`. A consumer such as workspace-halo must not need Python on its PATH.
The launcher owns `chcp 65001` around its own run. Shared scripts use
`%LLM_SHARED_DIR%\tools\batcolors`.

For ordinary consumer discovery, the settled default is
`%~dp0..\llm-shared` first, then a valid `LLM_SHARED_DIR` fallback;
llm-shared itself uses its own launcher. Once an upgrade has explicitly
selected a checkout, that checkout must execute and its actual path must be
reported. Default sibling discovery must not redirect the resumed operation
to an older development checkout. Selection mechanics remain design work.

The confirmed initial v0.14.0 platform is Windows x64 (Q1 A). Other operating
systems and architectures receive a clear scope diagnostic before project
mutation. Existing Unix deployment references do not extend this scope.

The selected checkout has one authoritative Python virtual environment: its
interpreter and installed dependencies for llm-shared tools, including release
operations. This differs from inherited shell environment variables. There is
no separate release environment or environment per consumer. Consumer builds
retain their own toolchains, but consumer, other-project and global Python are
never candidates for the shared release engine.

Approved design answer Q02 C reuses this setup-managed environment. The launcher
locates it independently of caller activation and verifies readiness against
the executing revision. Older environment directories, if present, are not
ranked, selected or counted as ambiguity when the authoritative environment is
ready. A checkout or Python executable alone does not establish readiness.
Release operations stop before project mutation if the authoritative runtime
cannot be identified or is unusable. They require no Python on the consumer
PATH and perform no fallback or runtime repair mid-release.

The umbrella's Q4 A assigns runtime preparation and repair to setup/upgrade,
reusing llm-shared's setup process. Design Q02 C also makes setup responsible
for the authoritative environment's designation and replacement. This child
supplies the location and readiness boundary;
item 6 owns installation, upgrades and compatibility policy for the actual
configuration and operations. An accepted upgrade must be runnable and invoke
the selected checkout. The location mechanism remains design work; choosing C
does not require a new selection-record file.

## Common configuration

Read `.release.ini` from the validated project root. A project without it
gets the defaults. Each project can keep its own versioned file for overrides;
it need not create the file when the defaults suit it, and omitted settings
retain their schema-defined defaults where available. Projects need not copy
or maintain the validation rules. Existing files keep their meanings: `version.txt`,
`CHANGELOG.md`, `changelog-header.md` and `.exempt-files`. A project
`cliff.toml` can override the shared default, while fix rules use
`.changelog-fixes.toml`; their behavior belongs to later children.

Approved design answer Q03 A, confirmed on 2026-10-19, places each schema beside
its owning component in llm-shared's versioned source. A schema describes allowed
sections and keys, value types, defaults and validation rules. For example, the
changelog component defines the accepted `generated` and `curated` modes. An
explicit registry combines these domain declarations for the common reader,
which rejects duplicate ownership and conflicts and validates all declared
settings, including those unused by the current command. Schemas come only from
shipped llm-shared code; a missing schema does not permit unknown settings.

The choice concerns the location of validation definitions inside llm-shared.
Alternative B would put all definitions in one foundation-owned Python module
in that repository. Both choices keep the same optional per-project
`.release.ini`; neither means one shared configuration file for every project.
A keeps rules and defaults with their owners while projects supply only values.

An existing `.release.ini` that is unreadable, malformed or ambiguous is an
error before mutation; it must not be treated as absent or silently replaced
by defaults. An incomplete custom declaration with a required value lacking a
default also fails. Diagnostics identify the configuration file and the offending
setting where possible. Parsing and diagnostic implementation remain design
work.

Read configuration with interpolation disabled so `%` and `$` in patterns
need no escaping. Validate modes, forms, paths and unknown keys before
mutation. No consumer runs code from project configuration. There is no
git-cliff executable configuration key; provisioning computes its internal
path.

These existing umbrella examples illustrate values the common reader must
preserve; their domain behavior remains with the owning children:

```ini
[changelog]
mode = generated

[tooling]
minimum-version = 0.14.0

[source:npm]
form = release-only

[source:cicd-env]
file = cicd/config/.env
pattern = ^APP_SERVICE_VERSION=(.+)$
form = snapshot
```

Version-source settings belong to item 2, the git-cliff pin to item 3,
generation/archive/fix rules to item 4, and the tooling minimum to item 6.
Shared parsing must support those boundaries without assigning their behavior
to this first child.

## Project artifact isolation

Consumer scratch files must not be written into the shared tooling checkout:
two projects may release concurrently. The ignored, versioned git-cliff cache
owned by item 3 is the distinct provisioning exception.

The umbrella identifies these legacy scratch writes:

- `dirty_files.tmp`, `dirty_ignored_files.tmp` and `run_filter.cmd`
  under `tools/dev_workflow/git/`;
- `temp_tag_message.txt` under `tools/dev_workflow/`;
- `CHANGELOG.tmp.md`, `CHANGELOG.new.md`, `CHANGELOG.cleaned.md`,
  `CHANGELOG.labeled.md`, `version.tmp.txt`, `.fixes_content.tmp`
  and `tmp_fixes.pl` at the project root.

The Python engine keeps most of those steps in memory. Remaining files, such
as git-cliff output, tag messages and the `pre` handoff, use the selected
project's artifact home: default `.reviews`, configurable through the
existing [artifact rules](../../rules/artifact_files.md). Their generating
operations remain owned by the later children.

The requirement to fail before project mutation includes ignored and
untracked artifacts. Rejecting a root, configuration or unavailable runtime
must not first create the artifact home, move legacy scratch files or write a
handoff. Read-only commands, including reading the current version, must not
initialize or migrate project artifacts. Artifact preparation and migration
must respect those outcomes.

Approved design answer Q06 A, confirmed on 2026-10-20, centralizes destination
checks and managed writes in common Python functions inside the release engine.
A module is a Python source file containing related functions; version,
changelog and release components are areas of code executed by the same
llm-shared Python selected in Q02. A shared interface is the common functions
and arguments they reuse. The managed-write service is local code within this
engine, requiring no additional Python, environment, server or user prompt.

For example, changelog functions prepare content and call the common functions
to check the destination and write `CHANGELOG.md`; version functions use them
for `version.txt`. The alternative would repeat destination checks and direct
file-writing instructions inside each component, still under the same Python.
Physical destinations can change after initial validation, for example when a
junction is redirected, so the common functions recheck containment and
repository boundaries before preparation or writes.

Components request changes only after complete preflight and retain transaction
ordering, recovery and cleanup. Read-only path resolution creates no artifacts.
Linked-worktree Git metadata and item 3's tooling cache keep distinct boundaries.
Exact functions and filesystem guarantees remain design and planning work;
rechecking a path alone does not establish atomic protection against every race.

## Dispatch and argument preservation

The umbrella's command surface provides dispatch context:

- `pre <root> [build args]` and `post <root> <build status>`;
- `version <root>` and `snapshot <root>`;
- `changelog <root> [latest|vX.Y.Z]`;
- `versions <root> list|set <version>|check`;
- `fixes <root> init|convert|dry-run`;
- `recover <root>`.

`b` routes the ordinary consuming build; `br` and `brel` both route its
`rel` lifecycle. `gv` reads the version; `uc` and `uvf` refresh
generated changelog content or validate curated content. `uver` selects the
separate next-snapshot transition. `uverr` routes release intent through the
consuming build gate. `crel` routes ownership-checked recovery of an active
unvalidated transaction; it must never reproduce the legacy newest-tag
reset/delete behavior against a valid release.

The umbrella's missing-tooling rule remains applicable: when the shared
launcher cannot be found, an ordinary consuming build may continue with one
warning and a read-only version display. Any requested release or snapshot
transition is blocked, wherever that request appears among the arguments.
This inherited exception concerns a missing launcher; it does not relax the
runtime requirements for release operations. Item 5 owns the build-lifecycle
behavior; setup and cutover install its integration. This child preserves
that boundary in dispatch.

Every prompting operation also has a non-interactive form that fails with a
message instead of asking. Preserve that option through dispatch, build,
`pre` and `post`, with no hidden batch `set /p` or downstream toolchain
prompt.

Preserve failure status through launcher and dispatch layers so a failed
operation cannot appear successful to its caller. Warnings and diagnostics,
including stale-environment warnings, must remain separate from command
results consumed by callers, such as the current version. Exact exit-code
numbers and output formats remain design decisions; item 5 retains ownership
of build-gate and postprocessing outcome rules.

Preserve quoted arguments and values containing spaces, quotes, `%`, `!`,
`&` and other batch metacharacters without executing notes or titles as
commands. The umbrella names `project_version`, `project_title`,
`build_params`, `build_params_echos`, `build_must_fail` and
`PRJ_REL_TITLE` at the build handoff boundary. Item 5 owns that transaction
and its handoff, including failure without a partially usable result; this
child owns safe dispatch to it.

Installing aliases and adapting consumer build scripts belong to setup and
cutover. Version synchronization, changelog rendering, binary provisioning,
release state/recovery, preparation workflow and migration remain with
umbrella items 2 through 8. Their implementation designs are not inferred
by this focused draft.
