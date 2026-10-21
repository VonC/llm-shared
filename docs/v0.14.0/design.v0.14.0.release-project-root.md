# Design v0.14.0: explicit release project identity

Reference feature request:
[feature-request.v0.14.0.release-project-root.md](feature-request.v0.14.0.release-project-root.md).

## Context for the release-project-root design

Shared release tooling must operate on one explicitly validated project while
executing code and Python from the selected llm-shared checkout. The approved
requirement separates those identities, caller initialization and artifact
ownership before version, changelog and release-lifecycle behavior is added.

This document proposes the foundation's responsibilities and interfaces.
Q01 A, Q02 C, Q03 A, Q04 A, Q05 A, Q06 A and Q07 A are approved with the
clarifications below:
Git subprocesses isolate inherited routing, each llm-shared checkout supplies
one authoritative setup-managed Python environment, and domain-owned schemas
provide common configuration validation with defaults that require no project
configuration when suitable. The batch launcher invokes that Python directly,
and one shared CLI renderer owns result streams and public exit statuses.
Common Python functions check destinations and perform managed writes within
that same release engine. A separate entrypoint for aliases discovers the
caller's worktree and passes its explicit root to the engine. Q08 A additionally
confirms a setup-produced runtime identity record and the narrow item 1 scope
amendment needed to produce it. Q09 A confirms that release startup checks only
llm-shared's release-engine dependencies in that environment, declared and
locked in llm-shared's own files. Q10 A confirms the caller transports and
replacement for inherited build-title arguments. Q10 P1 confirms explicit
path-variable selectors, with the build root freshly derived from its script
location rather than inherited `PRJ_DIR`. Q11 A confirms selection of an
existing `git.exe` through eligible absolute PATH entries, with minimum Git
2.31.0. Q12 A confirms the tooling-minimum check before strict domain
validation, including refusal of any declared minimum until item 6 supplies
comparison semantics. Q13 A confirms one shared project operation lock,
including ownership across build handoffs and conservative recovery. Q14 B
confirms non-interactive mode when explicitly requested or when stdin is not
a Windows console, preserved through the build handoff.

All questions remain recorded below until explicit consolidation. Independent
review round 1 proposed Q08 through Q14; their options were refined in rounds
2 to 4 with further Windows transport evidence. Q08 A through Q13 A and Q14 B
are now confirmed, including Q10's separate P1 path choice. Round 5 clarified
P1's per-caller variable lifetime and Q09's dependency-marker handling without
changing those answers. All recorded questions have human answers; this does
not authorize consolidation.
The requirement includes the setup producer scope amendment approved by Q08 A
and the caller/title transport amendment approved by Q10 A; the
[focused draft](draft.v0.14.0.release-project-root.md) remains its draft basis.

## Scope and ownership of the v0.14.0 foundation

The foundation supplies a common invocation context, root validation, explicit
Git execution, tooling/runtime location and validation, configuration parsing, artifact-path
validation and dispatch. Later domains receive that validated context rather
than rediscovering roots from the environment or working directory.

Version-source behavior, provisioning, changelog generation, release
transactions, installation, upgrades and migration remain with umbrella items
2 through 8. Their interfaces must fit this foundation, but this child does not
implement their commands, release-state model or installer. Unavailable domain
operations must fail clearly, never claim successful work through a stub.

## Confirmed codebase facts relevant to project identity

| Existing code | Observed behavior | Design implication |
| --- | --- | --- |
| `senv.bat` | Sets project identity before its guard; chooses a Python version from `PRGS` and calls the external `switchpy`, which names the environment `venvs\python_<version>_<checkout-name>` | Current setup leaves no authoritative runtime identity record; Q08 A removes the dependency cycle with item 6 |
| `build.bat` | Derives `build_dir` from its script and uses `call <NUL "%build_dir%\senv.bat"` before legacy preprocessing; this is the direct-call form that round 3 found fails for `%` and `^` directories | Preserve the script-derived root; items 5 and 8 apply the selected safe call form to the integration template |
| `bin/mds.ps1` | Derives the checkout from its own path, selects a venv directory by name and invokes Python by absolute path | Demonstrates self-location, but does not establish the new runtime-readiness policy |
| `bin/prompt_workflow.bat` | Keeps an inherited `LLM_SHARED_DIR` when present and selects a matching venv by modification time | Copying this launcher would violate the new checkout identity guarantee |
| `bin/ghog.bat` | Selects `python_3*` directories by name | Existing launchers do not share one selection rule |
| llm-shared's `pyproject.toml` and `uv.lock` | Require Python `>=3.13, <3.14`, use `package = false`, and declare one dev group with no release subset | Confirmed Q09 A defines a release group in these llm-shared files as the dependency scope for release readiness |
| `bin/review_exchange.bat` | Prepends tooling code to an inherited `PYTHONPATH` | The new release bootstrap must isolate imports instead of copying this pattern |
| `tools/git_command.py` | Accepts cwd, environment and stdin, but invokes bare `git`; Windows may search cwd when `NoDefaultCurrentDirectoryInExePath` is unset | Confirmed Q11 A selects an absolute `git.exe` through eligible PATH entries before checking its version or running operations |
| `tools/review_artifact_configuration.py` | Separates read-only `load` from `prepare_home` and accepts a tracking-check callback | Reuse configuration semantics without preparing artifacts during validation |
| `tools/artifact_home.py` | Convenience calls prepare the home and may move a legacy file | Do not use those convenience calls during preflight or read-only commands |
| Round 2 Windows PowerShell 5.1 forwarding probe | A space-free `C:\R&D\proj` passed to a forwarding `.bat` reached Python as `C:\R`; cmd tried to run `D\proj` | Q10 must route metacharacter paths through an explicit data channel; quoting behavior cannot be inferred from paths containing spaces |
| Round 2 redirected-stdin probe | Stdin from `NUL` returned `isatty() == True`, but `GetConsoleMode` reported no console | Confirmed Q14 B uses the Windows console API rather than `isatty()` |
| Round 3 launcher-location probes | Direct batch `call` failed in `%` and `^` directories; `pushd`, `call .\probe.bat`, `popd` worked for `%`, `^` and `!`. Windows PowerShell 5.1 reached batch files in `&`, `%` and `^` directories; Python `subprocess` with a space-free `&` batch path ran another command | Q10 A names the relative-call form for builds and retains native Python execution for automation; these probes establish those cases, not the whole transport contract |
| Round 5 reviewer P1 build probes | A scratch build using the confirmed `setlocal`, script-derived root, selector and relative-call form delivered exact roots, preserved status 7 and leaked neither its variable nor directory changes across 20 metacharacter and non-ASCII directory combinations | Supports the build route's path and cleanup rules; does not prove the real launcher, cancellation or every host |
| Round 5 reviewer P1 prompt and PowerShell probes | Windows PowerShell 5.1 delivered exact selector values in 9 combinations but retained the variable afterward; `setlocal` had no effect at a cmd prompt | P1 requires assignment for each launch and explicit lifetime rules for each caller; prompt assignments persist |

These facts describe current code, not changes already implemented for this
topic.

## Invocation flow and validation boundaries

The proposed flow is:

```text
caller supplies explicit root or requests current-worktree alias dispatch
  -> self-locating launcher locates its setup-managed runtime without changing cwd
  -> dependency-free Python bootstrap captures the original cwd
  -> bootstrap verifies platform and runtime readiness before engine imports
  -> dispatcher captures invocation data through the selected transport
  -> validate platform, project root and Git context
  -> load and validate project configuration and artifact declaration
  -> select a supported domain handler
  -> handler performs its own remaining preflight
  -> mutating operations acquire the shared project lock under confirmed Q13 A
  -> revalidate state that may have changed before lock acquisition
  -> authorized writes use explicit, revalidated project destinations
  -> result and diagnostics return through the launcher
```

This is a separation of responsibilities, not a file-by-file implementation
sequence. No artifact preparation occurs merely to construct or reject an
invocation. Domain preflight remains responsible for conditions introduced by
that domain before it requests writes.

The proposed invocation context carries:

| Context value | Purpose |
| --- | --- |
| Project root and derived project name | One authoritative worktree identity |
| Tooling root and authoritative runtime identity | The selected checkout's code and setup-managed interpreter actually executing |
| Invocation origin and original argument vector | Distinguish explicit-root calls from alias discovery without reparsing values as commands |
| Git execution context | Explicit target, controlled environment, linked-worktree metadata, and the absolute `git.exe` path/version selected under confirmed Q11 A |
| Validated configuration | Shared parsing plus validation by the owning domain |
| Artifact declaration | A validated destination, without eager creation |
| Interactive policy | Under confirmed Q14 B, select non-interactive mode on explicit request or non-console stdin and preserve it through the validated build handoff |

Keep this context fixed for one operation. An upgrade that selects another
checkout starts a new invocation there with the selected root and original
values. Confirmed Q10 A uses the selected checkout's designated Python directly
for that handoff, without re-entering a batch parsing boundary. The current
operation must not silently replace its tooling identity.

## Project paths and Git execution

Resolve the supplied root to its physical directory and compare it with Git's
worktree top-level under the controlled Git environment. Use filesystem-aware
identity checks for equivalent Windows spellings and links; textual prefix
comparison or unconditional lowercasing is insufficient. A supplied subfolder
is not an explicit root, even though alias discovery may start there.

Represent the worktree root separately from its Git directory and common Git
directory. Linked worktree metadata may legitimately live outside the worktree.
The containment rule applies to managed project files and artifacts; it must
not misclassify Git's own linked-worktree metadata as a managed project file.

Validate existing destinations and existing ancestors of future files against
the physical root. Check nested repository boundaries along the managed path.
Recheck the destination when a domain is about to write so a stale path result
does not authorize a changed link target. The managed-write section below
defines the guarantee and replacement discipline; implementation planning
must prove that contract.

Approved Q01 A makes the Git adapter responsible for a controlled environment
for every Git subprocess, including those used to validate the root. Later Git
operations require the validated context and an explicit working directory.
The adapter handles inherited inputs by class:

| Input class | Treatment |
| --- | --- |
| Repository routing, including worktree, index, common directory, objects, namespace, discovery limits, replace, graft and shallow overrides | Remove inherited overrides and diagnose conflicting targets |
| Command-scope configuration injection, including `GIT_CONFIG_PARAMETERS` and the counted key/value family | Remove inherited injection before validation |
| Configuration-file selection, including system/global selection and their disabling switches | Preserve selection, inspect effective configuration with origins and scopes, and reject routing keys supplied outside the selected repository's own configuration |
| Execution controls | Remove inherited executable-search and template overrides; preserve signing and credential helpers; always disable editors and pagers; disable terminal prompting when confirmed Q14 B selects non-interactive mode |
| Output and pathspec controls | Set explicit machine-readable formats, locale, quoting, color and literal-path behavior per parsed command; do not inherit output-shaping or pathspec overrides |
| Identity, signing and credentials | Preserve compatible author/committer identity, signing configuration and credential settings |

Inspect effective configuration before relying on Git's worktree result.
Included files retain their reported origin and scope for that check. Reject
an external-scope routing key such as `core.worktree` with its origin in the
diagnostic. Ordinary repository hooks and configured signing/credential helpers
remain trusted user code; this policy isolates targeting, not execution of
arbitrary trusted helpers. The parent shell is not changed.

In non-interactive mode, Git receives detached stdin and disabled terminal
prompts. A helper that cannot complete without interaction fails visibly.
Confirmed Q14 B selects that mode on explicit request or when stdin is not a
Windows console, and preserves it through the validated build handoff.

For example, after activating project A, the caller explicitly targets B.
Inherited `GIT_DIR`, `GIT_WORK_TREE` or `GIT_INDEX_FILE` may still name A;
`git -C B` alone does not override every such input. Isolation means controlling
what each Git subprocess inherits so validation and operations target B.
It does not create another checkout, container or sandbox.

This policy keeps explicit-root operations usable from stale shells and gives
every domain the same targeting guarantee. Implementation must enumerate and
verify the variables and routing keys within these design-level classes;
clearing only the three example variables is insufficient.

Round 1 demonstrated that a `git.exe` planted in the caller's directory can
win bare-name resolution. Confirmed Q11 A resolves the first eligible `git.exe`
from the current process's PATH in order, considering only absolute directories
and excluding cwd, empty entries and relative entries. It never runs `.cmd` or
`.bat` shims selected through `PATHEXT`. It records the absolute executable
path and version once per operation and uses that path for every Git call.
The confirmed minimum is Git 2.31.0 for the configuration facilities used by
this policy. No separate Git installation for llm-shared is required.

The existing Git execution helper may implement the final subprocess call.
It must not be treated as proof that environment routing or path identity was
validated.

## Launcher responsibilities and authoritative runtime

Use `bin/release_workflow.bat` as the public Windows entrypoint and keep its
responsibility limited to locating its own checkout and authoritative runtime,
starting the readiness bootstrap, preserving input values through the selected
transport and returning the public status.
Treat codepage changes as scoped to the launcher's run and restore the caller's
codepage on exit. Do not activate senv or modify the caller's PATH. Neither
public launcher changes directory before Python captures its own cwd.

Consumer discovery belongs before that entrypoint: the caller selects the
sibling checkout or valid fallback. The selected launcher's own location then
wins over inherited `LLM_SHARED_DIR`. An explicitly selected upgrade launcher
is invoked directly, and reports its actual checkout through diagnostics.

Approved Q02 C means each selected llm-shared checkout has one authoritative,
setup-managed Python virtual environment for its tools, including release
tooling. Here, a Python environment is the interpreter and its installed
dependencies. It is distinct from the shell environment variables discussed
under Q01. There is no separate release environment or environment per consumer.
Consumer builds retain their own toolchains; consumer, other-project and global
Python are never candidates for the shared release engine.

Setup and upgrade own designation, preparation, replacement and repair of this
environment under umbrella item 6. This foundation locates that authoritative
environment independently of caller activation and checks interpreter, import
and dependency readiness against the executing revision. An executable's
presence or reported Python version alone does not establish readiness.
These checks must not repair the environment, run a release handler or write
consumer artifacts.

Older environment directories may remain on disk, but they are neither runtime
candidates nor grounds to reject a ready designated environment. If the
authoritative environment cannot be identified or is unusable, release tooling
fails before project mutation without selecting another environment or Python
from PATH. Runtime preparation and repair remain setup operations.

The approved ownership model replaces release-time discovery or ranking.
Current setup has no record identifying its chosen directory, and deriving one
from the newest machine-installed Python would reintroduce that ranking.
Item 1 cannot depend on a future item 6 implementation that itself depends on
item 1. Confirmed Q08 A assigns item 1 the identity record under ignored `venvs`
and its production by current setup after successful environment preparation.
The user explicitly approved this narrow feature-request scope amendment;
item 6 retains the full installation, upgrade and repair lifecycle.

A dependency-free bootstrap checks platform, the interpreter requirement and
the selected readiness contract before importing any engine third-party code.
Confirmed Q09 A requires a release dependency group in llm-shared's own
`pyproject.toml`, locked in its own `uv.lock` for the executing revision and
included by its existing dev group so current setup installs it. Release
startup checks only that group's applicable direct and transitive dependencies;
unrelated development packages and the consumer's lock are outside this check.
Failure returns status 2 and identifies setup repair as the remedy,
without attempting repair or creating consumer artifacts.

Launch Python with isolated imports and explicit UTF-8 mode (`-I -X utf8`).
The bootstrap derives the trusted tooling root from its own source location
and adds only that root for in-place engine imports; it must not trust the
consumer cwd, inherited `PYTHONPATH`, or user site-packages. Runtime packages
come from the designated environment. Disable bytecode writes during readiness
checks. Python streams are explicitly configured as UTF-8 with LF line endings;
codepage changes alone do not define stream encoding.

Round 1's scratch probes established failures, not merely a need for testing:
`%PATH%` expanded inside an automation argument, embedded quotes disappeared
through Windows PowerShell 5.1, a quoted ampersand value executed an extra
command through batch, and `build.bat`'s `call` layer changed `%` and `^`.
Q04 A still selects the minimal frontend structure, but its condition to
revisit transport is met. Confirmed Q10 A selects UTF-8 file/stdin transport for free text
and direct authoritative-Python invocation for Python automation and
cross-checkout execution. The value-preservation requirement remains intact.
Paths with metacharacters must also have a documented safe channel; labeling
all paths as safe batch tokens is insufficient. Confirmed Q10 A with P1 gives
each caller an explicit route, using named environment variables that the
caller assigns for each launch to carry project-root and input-file paths
without expanding them into batch arguments. Batch scripts limit their scope
with `setlocal`/`endlocal`; PowerShell scripts restore or remove the previous
value in `finally`. At a cmd or PowerShell prompt, assign the variable in the
launching command line; that value persists until reassigned or removed.
The build initializes its root from its own script location.
Batch grammar is a caller obligation: expansion before Python starts can
alter a value undetectably, so rejection of surviving unsafe characters is
not a guarantee that all unsafe invocations can be rejected. Implementation
approval waits for evidence for each supported caller.

## Common configuration with domain-owned validation

Use a strict UTF-8 INI reader with interpolation disabled and accept one
optional leading UTF-8 byte-order mark. Load only the selected root's
`.release.ini`; distinguish an absent file from read, encoding and
parsing errors. Duplicate or conflicting declarations must not silently choose
a value. No project-supplied code is imported or executed.

Approved Q03 A composes an explicit registry of domain-owned declarative
schemas. A schema defines allowed sections and keys, value types and forms,
defaults, validation rules and path roles. These definitions are versioned in
llm-shared's source beside the components that own the settings. For example,
the changelog component declares that its mode accepts `generated` or `curated`
and supplies the default; the common reader uses that declaration.

Each consuming project may keep its own versioned `.release.ini` at its root
to select values. When the supplied defaults suit the project, it can omit the
file entirely. A project that needs overrides declares only those settings;
omitted settings use their schema-defined defaults where available. Projects
do not need to copy, register or maintain schemas or validators. An incomplete
custom declaration still fails if it lacks a required value with no default.

Q03 concerns ownership of definitions inside llm-shared. The alternative B
would have put every domain's rules and defaults in one foundation-owned Python
module in that same repository. Both choices use the same optional per-project
configuration file; neither introduces a shared `.release.ini` for all projects.
A keeps the rules with their domain owners. Exact module names remain for
implementation planning.

The common reader owns parsing, file diagnostics, schema registration conflicts
and unknown-key detection. Schemas come only from shipped tooling code, and
the registry must reject duplicate ownership or conflicting declarations.
A schema owns fixed sections or an instance-named section family by prefix,
such as `source:` or `changelog-archive:`. Domain-owned validation functions
check parsed families and cross-section rules such as archive-range overlap.
An explicit registry tuple has a completeness check that fails when a shipped
schema is omitted. A missing schema cannot make its keys acceptable. This
permits source and changelog extensions without moving their behavior into the
foundation.

Confirmed Q12 A addresses configuration written for newer tooling. It
uses a stable `[tooling] minimum-version` bootstrap check before strict domain
validation. Before item 6 supplies comparison semantics, the foundation validates
the key's syntax and fails closed whenever a minimum is declared; item 1
does not invent a comparator. Generated configuration omits the key during
that interim. An absent key proceeds to strict domain validation. Once
comparison exists, incompatible tooling reports the update action first;
compatible tooling validates every declaration strictly. No newer configuration
may silently bypass validation.

Validate declared configuration before mutation, including settings outside
the command's immediate behavior. Defaults come from the owning schema; an
invalid declaration cannot be replaced with a default. A schema declaration
does not activate a domain handler or authorize provisioning.

Resolve project-relative managed paths using the same containment service as
other file operations. Keep the original setting and file location available
for diagnostics. Regex values such as `^APP_SERVICE_VERSION=(.+)$` remain data
and are passed unchanged to the version-source owner.

## Artifact reuse without eager side effects

Reuse `ReviewArtifactConfiguration.load` to interpret `.review-artifacts.ini`
and its default `.reviews` location. Supply a project-scoped tracking callback
using the controlled Git adapter, and apply the foundation's nested-repository
and physical-containment checks to the declaration and destination.

Keep artifact resolution and preparation as separate capabilities. Preflight
and read-only handlers may inspect a declaration but cannot obtain an operation
that creates the home, migrates legacy files or writes a handoff. A mutating
domain requests preparation only after its complete preflight succeeds.

Approved Q06 A puts managed destination checks and filesystem changes in
common Python functions inside the release engine. A module is a Python source
file containing related functions; version, changelog and release components
are code within that engine, all executed by the one llm-shared Python selected
in Q02. The shared write service is those common functions, called locally
through a shared interface: the functions and arguments available to callers.

For example, changelog code prepares content and asks the common functions to
write it to `CHANGELOG.md`; version code uses them for `version.txt`. The
functions recheck physical containment and repository boundaries before
artifact preparation or managed writes. File writes create a temporary file
inside the revalidated parent, revalidate the final physical target, then
replace atomically. Directory preparation revalidates the existing ancestors.
The guarantee covers ordinary changes between preflight and writing, including
edited paths and redirected junctions; it does not claim protection against a
hostile process racing each filesystem operation. Components retain their complete
preflight, transaction ordering and cleanup. Exact Python file names and
function signatures remain implementation-planning work.

This design reuses the existing artifact policy rather than copying its parser.
It does not modify review-exchange behavior. Per-operation temporary names,
cleanup and transaction ownership remain with the domains that generate them;
the shared git-cliff cache remains item 3's distinct write area.

Confirmed Q13 A gives the foundation one shared project operation lock for
version, changelog and release mutations. After complete preflight, prepare
the validated artifact home, acquire the lock atomically and revalidate state
that may have changed before acquisition. Retain ownership through mutation
and cleanup. Ownership belongs to the whole operation and survives validated
build handoffs, even while no engine process is running. Live contention fails
visibly; automatic stale recovery requires the exact process owner to be gone
and no retained handoff to own the operation. An abandoned or unverifiable
retained handoff requires explicit human recovery through an action item 5
provides.

The lock is separate from item 5's transaction and rollback rules. Read-only
commands and commands rejected during preflight still create nothing. Reads
take no lock and can observe an intermediate combination between atomic
replacements of different files; Q13 A supplies no multi-file snapshot.

## Dispatch and result interfaces

Use `bin/release_alias.bat` as the separate alias-only surface alongside the
explicit-root `bin/release_workflow.bat`. Only the alias surface selects
current-worktree discovery. Both leave cwd unchanged; Python captures it before
any domain work, without transporting `%CD%` through batch arguments.
The alias resolver uses the controlled Git adapter, then passes the discovered
root into ordinary explicit-root validation. Outside a worktree it fails.
The explicit-root surface rejects an absent root even inside a valid worktree.

The Python dispatcher owns command routing. Shell adapters provide
the invocation data and execute the selected project build when required; they
do not duplicate root validation or configuration semantics. Alias installation
and concrete consumer integration remain items 6 and 8.

Future domain handlers receive the fixed context and return a structured
outcome containing success/failure, result data and diagnostics. The public CLI
renders command data on stdout and warnings/errors on stderr. This allows a
stale-environment warning without corrupting a version result. Domains retain
ownership of their data format and of build/recovery detail.

Approved Q05 A defines public statuses: 0 for success, 1 for execution failure,
and 2 for invalid input or failed preflight. The launcher forwards those
statuses and the engine's streams unchanged. Before the renderer can run,
missing runtime, unsupported platform and failed readiness also return 2 with
a stderr diagnostic. An uncaught exception returns 1. An unexpected native
status outside 0 through 2, including console interruption when the launcher
can regain control, is reported on stderr and normalized to 1 at the outer
boundary. A terminated launcher cannot promise a final diagnostic; automation
must use the selected non-batch transport where batch termination could prompt.
The transport and cancellation evidence remain implementation proof
obligations under Q10 and Q14.
The shared CLI's stdout and stderr use UTF-8 and LF. Item 5 owns live child
output handling and retains the original build failure if postprocessing fails.

The missing-launcher exception is evaluated by the consuming build adapter:
ordinary build intent may proceed with its warning and read-only version
display; release or snapshot intent anywhere among arguments must fail.
An installed handler must not use this exception to hide an execution failure.
The actual lifecycle handling and build invocation belong to item 5.

Confirmed Q14 B selects non-interactive mode when explicitly requested or when
the Windows console API reports that stdin is not a console. Use
`GetConsoleMode` on the stdin handle; `isatty()` alone is insufficient.
Missing required input fails with an actionable diagnostic instead of prompting
or assuming consent. Piped callers must supply all required values. The chosen
policy survives both `pre` and `post` invocations through the validated item 5
handoff; an inherited variable cannot silently reverse it. This decision
provides no interactive override for redirected stdin. Native helpers and
batch cancellation still require validation for hidden prompts.

## Acceptance cases for the proposed foundation

| Scenario | Expected outcome | Requirement |
| --- | --- | --- |
| Explicit project B with stale `PRJ_DIR` naming A | Validate and use B, diagnose the mismatch | AC1 |
| Alias from a subfolder of B after activating A | Resolve B's top-level and name both roots in the warning | AC2 |
| Full-path build for A launched from B | Pass A's script-derived root | AC2 |
| Inherited Git routing names A while target is B | Isolate validation and operations to B, diagnose ignored conflicts and leave the parent shell unchanged | AC3 |
| Environment-injected Git configuration could redirect target B | Remove the injection input under the controlled policy; no validation or operation targets another repository | AC3 |
| User identity, signing or credential settings coexist with target B | Preserve those settings while maintaining isolation | AC3 |
| Linked worktree B shares a common Git directory with A | B keeps its file/artifact root; shared metadata remains distinct | AC3 |
| Managed destination crosses an external junction or nested repository | Reject before a write to that destination | AC4 |
| Guarded activation or separate PowerShell calls | Do not assume identity/tool initialization was refreshed in the parent | AC5 |
| Explicit upgrade checkout differs from the default sibling | Execute and report the selected checkout | AC6 |
| Caller activated a consumer or another llm-shared checkout | Locate and validate the executing checkout's authoritative environment independently of activation | AC7 |
| Authoritative environment is ready and older environment directories remain | Use the authoritative environment; leftovers cause neither selection nor ambiguity | AC7 |
| Authoritative environment is unidentified or unusable, even if another Python runs | Fail before project mutation without fallback or repair | AC7 |
| Authoritative interpreter exists but required dependencies are unavailable | Fail readiness before project mutation; setup owns repair | AC7 |
| Configuration is missing versus malformed | Use defaults only for absence; diagnose malformed content | AC8 |
| Project accepts all supplied defaults | Omit `.release.ini` and use domain defaults without project schemas or validators | AC8 |
| Project overrides one setting and omits other defaulted settings | Validate the override and retain the owning schemas' defaults for omitted settings | AC8 |
| Invalid or unknown setting belongs to a domain unused by the command | Reject before mutation; do not ignore the setting or replace it with a default | AC8 |
| Registered schemas claim the same setting or conflict | Reject the schema composition before project mutation | AC8 |
| Current-version read or failed validation with no artifact home | Leave the artifact home absent and legacy scratch files untouched | AC9 |
| Quoted title includes batch metacharacters | Preserve its value without command execution | AC10 |
| A handler fails after producing diagnostics | Return failure and keep diagnostics out of successful command data | AC10 |
| Missing launcher and release intent is not the first argument | Reject the transition; item 5 owns the build-lifecycle behavior | AC11 |
| Explicit-root surface is called without a root inside a worktree | Fail with status 2; do not infer alias mode | AC1, AC2 |
| `release_alias.bat` is called outside Git | Fail discovery without creating artifacts | AC2, AC9 |
| A managed parent becomes an external junction after preflight | Reject before temporary-file creation or final replacement outside the root | AC4 |
| A non-repository configuration source sets `core.worktree` | Fail before operations, identifying the setting's origin and scope | AC3 |
| Caller cwd contains a planted `git.exe` | Never execute it; apply the executable-selection policy confirmed in Q11 A | AC3 |
| Python automation supplies `x"&echo INJECTED&"y` as a title | Preserve the exact value and execute no command through the Q10 transport | AC10 |
| A build handoff carries values containing `%`, `^`, `!`, `&` or embedded quotes | Preserve the bytes through the chosen channel, including each `call` boundary | AC10 |
| A project path contains spaces and batch metacharacters | Support it through a documented safe channel; do not silently narrow accepted paths | AC1, AC10 |
| A required release dependency is missing | Bootstrap returns 2 before engine third-party imports and creates no consumer artifacts | AC7, AC9 |
| A locked release dependency carries a marker the bootstrap cannot evaluate | Fail readiness with status 2 naming the package and marker | AC7 |
| Consumer cwd or inherited Python settings contain a shadow engine module | Import only the selected checkout and designated runtime packages | AC6, AC7 |
| A handler succeeds, fails, or rejects preflight | Return 0, 1, or 2 respectively; preserve stdout/stderr separation | AC10 |
| A child exits 7 or Python is interrupted with a native status | Report original failure and normalize to 1 when the outer boundary can run; verify cancellation behavior for each transport | AC10 |
| `.release.ini` declares newer required tooling once item 6 provides comparison | Apply confirmed Q12 A: report the update action before strict domain validation, without accepting unknown settings | AC8 |
| Two mutating operations target the same project | Under confirmed Q13 A, use the shared project operation lock and fail visibly on live contention; verify ownership and recovery rules | AC4, AC9 |
| UTF-8 configuration has a leading byte-order mark | Parse it as the same configuration as the unmarked file | AC8 |
| Non-ASCII result and diagnostic text is redirected | Emit UTF-8 with LF on the respective streams | AC10 |
| Windows PowerShell 5.1 supplies a space-free metacharacter root such as `C:\R&D\proj` | Preserve the root through Q10's selected path channel; never pass it through bare batch forwarding | AC1, AC10 |
| Stdin is redirected from `NUL` | Under confirmed Q14 B, the Windows console API selects non-interactive mode even when `isatty()` is true | AC10 |
| A non-interactive invocation lacks a required title or answer | Under confirmed Q14 B, fail with an actionable diagnostic rather than prompting or assuming consent | AC10 |
| A release handoff resumes after environment changes | Under confirmed Q14 B, preserve the selected policy through `pre`, build and `post`; do not silently re-enable prompts | AC10 |
| A `git.cmd` or `git.bat` shim appears earlier on PATH | Under Q11 A, never execute it; select an eligible `git.exe` or fail | AC3 |
| A minimum tooling version is declared before item 6 provides its comparator | Under Q12 A, validate syntax and fail closed with a compatibility-unavailable diagnostic | AC8 |
| A release operation spans `pre`, build and `post` without a live engine process in the gap | Under Q13 A, retain operation ownership through the validated handoff; absence of the `pre` process alone never makes the lock stale | AC4, AC9 |
| A fresh setup prepares the authoritative environment | Under Q08 A and Q09 A, install the release closure through the dev group's inclusion before publishing runtime identity | AC7 |
| A read overlaps a multi-file mutation | Under Q13 A, create no read lock and allow an intermediate combination of individually valid file versions; do not claim a transaction snapshot | AC4, AC9 |
| `build.bat` selects a tooling checkout under a `%` or `^` directory | Under Q10 A, enter the launcher's directory, use `call .\release_workflow.bat`, then restore cwd and the saved public status | AC6, AC10 |
| A build supplies a relative data path during the temporary launcher-directory change | Under Q10 A with P1, resolve it against the validated project root, never the tooling directory | AC1, AC10 |
| A PowerShell or cmd caller keeps a selector variable from an earlier launch | Scripts restore or remove it; prompt users assign it in the launching command line; diagnostics name the variable and its value | AC1, AC5 |
| A build runs in an interactive console containing an old selector-variable value | Under Q10 A with P1, assign the build's root inside `setlocal`/`endlocal`, restore the prior environment afterward, and identify the selector and supplied root in diagnostics; no later build-created value leaks | AC1, AC5 |

The approved whole-suite scope applies to later validation. Plans will assign
test files, implementation steps and rollout checks after design decisions are
settled.

## Open questions for the v0.14.0 release-project-root design

These questions concern design choices and explicitly identified requirement
amendments. Q01 A, Q02 C, Q03 A, Q04 A, Q05 A, Q06 A, Q07 A, Q08 A, Q09 A,
Q10 A with P1, Q11 A, Q12 A, Q13 A and Q14 B are confirmed with their
clarifications. Q08 A also approves the narrow setup producer addition to
item 1's requirement. Q10 A approves the caller
transport and build-title source amendment; P1 is now separately confirmed.
Q08 through Q14 were added from independent review round 1 and refined in
rounds 2 to 4. Round 5 clarified obligations within Q09 A and Q10 A with P1.
All recorded questions, including Q10's path sub-decision, now have human
answers. Answer recording does not authorize consolidation.
Recommendations retain the original review proposals, including Q02's
recommendation of A before the user chose C. All questions and options remain
here until explicit consolidation, after an intermediate question snapshot
commit preserves them in Git.

### Q01: How should the Git adapter isolate inherited routing settings?

The root must remain authoritative even when inherited Git settings redirect
the repository, worktree or index. The adapter must address environment-based
configuration injection as well as named routing variables. Ordinary signing,
identity and credential configuration should remain usable when it cannot
redirect the target. Which isolation policy should the foundation provide?

#### Clarifications for Q01

Here, the environment means the settings inherited by a Git subprocess.
Isolation controls those settings for each invocation, including root
validation; it requires no extra checkout, container, sandbox or Python virtual
environment. The parent shell remains unchanged.

For example, after activating project A, an explicit operation on B must target
B even if inherited `GIT_DIR`, `GIT_WORK_TREE` or `GIT_INDEX_FILE` still names A.
`git -C B` alone cannot guarantee that. Option A removes routing and
configuration-injection inputs, diagnoses ignored conflicts and preserves
compatible identity, signing and credential settings. The complete policy must
cover more than those three example variables.

#### BBQ for Q01

A barbecue delivery has a confirmed address but the driver's old route sheet
names another house. Replace that route sheet for this trip, or refuse the
delivery until the driver removes it. In this picture: the delivery address is
the validated worktree, the old route sheet is inherited Git routing, and the
driver is the Git subprocess.

#### Options for Q01

- Option A: Construct an operation-scoped Git environment, remove inherited
  routing and configuration-injection inputs, and bind operations to the
  validated Git/worktree identity. Preserve compatible non-routing settings
  and diagnose ignored conflicts without changing the parent shell.
  - Pro: Explicit-root operations remain usable from stale shells while their
    target stays fixed.
  - Con: The adapter must define and verify a complete routing-isolation policy;
    clearing only three familiar variables is insufficient.
- Option B: Reject inherited routing or configuration-injection inputs that
  cannot be proved consistent with the validated target, then use an explicitly
  targeted Git subprocess.
  - Pro: Ambiguous input produces a visible failure instead of being discarded.
  - Con: Otherwise valid commands may require callers to clean their shells;
    determining which settings are consistent still requires careful analysis.

#### Recommended option for Q01

Option A: Make the adapter responsible for isolation. This matches explicit
project selection and allows ordinary user signing configuration to keep
working. Configuration sources that cannot safely coexist with that isolation
must cause a clear failure rather than be trusted implicitly.

#### Answer to Q01: option A

Confirmed by the user on 2026-10-18: choose A. Every Git subprocess, including
root validation, receives controlled inherited settings. Remove routing and
configuration-injection inputs, diagnose ignored conflicts, and preserve
compatible identity, signing and credential settings. The parent shell stays
unchanged.

For example, after activating project A, an explicit operation on project B
must still target B despite inherited Git settings naming A. The complete
isolation policy must cover more than `GIT_DIR`, `GIT_WORK_TREE` and
`GIT_INDEX_FILE`. This gives every domain the same target guarantee without
requiring callers to repair their shells.

Round 1 wording completion: every subprocess uses the executable identity
subsequently confirmed in Q11 A and the input classes defined above. Preserve configuration-file
selection and compatible identity, signing and credentials, then inspect
effective configuration origins and scopes. A routing key outside the selected
repository's own configuration fails validation. Parsed commands select their
format and locale explicitly. Non-interactive Git has detached stdin and no
terminal prompts.

### Q02: How should the launcher identify and verify the setup-owned runtime?

The executing checkout's declared Python and dependency requirements determine
readiness. Existing launchers disagree on directory-name versus modification-
time selection. The new launcher must not use those heuristics as readiness
checks. The original question asked which candidate to select; the confirmed
C instead requires identification of the one setup-owned environment. The
original options and recommendation remain below as history. Q08 asks for the
identity mechanism and Q09 asks which dependencies establish readiness.

#### Clarifications for Q02

Here, the environment means a Python interpreter and its installed dependencies,
not the shell variables discussed in Q01. Each selected llm-shared checkout
provides one authoritative setup-managed environment for all its tools. Projects
using that checkout share this tooling environment; they need no release-only
or per-consumer environment. A consumer build still uses its own toolchain.

Setup and upgrade designate, prepare, replace and repair that environment.
Release tooling only locates it and checks readiness for the executing revision,
independently of caller activation. Leftover environment directories are not
ranked or counted as competing candidates; foreign and global Python are never
fallbacks. Release commands do not repair the runtime mid-operation.

The confirmed C requires a setup-owned authoritative identity. The original
option's selection record does not mandate a new file: an existing setup
identity mechanism can suffice. The original recommendation of A is retained
below as discussion history; the approved answer is C with this clarification.
Round 1 found no such identity record in current setup; confirmed Q08 A closes
that gap without silently falling back to candidate selection.

#### BBQ for Q02

Before grilling, choose a working grill belonging to this host. Use the only
ready grill, rank several ready grills, or require the host to label one in
advance. In this picture: the host is the selected tooling checkout, the grills
are its bundled environments, readiness is interpreter/dependency compatibility,
and the label is a setup-owned runtime selection record.

#### Options for Q02

- Option A: Discover checkout-local candidates, check readiness without repair,
  and require exactly one compatible ready environment. Fail clearly when none
  or several qualify, listing candidates in diagnostics.
  - Pro: Selection is deterministic without guessing precedence or requiring a
    new setup record before item 6 exists.
  - Con: Multiple usable environments require explicit cleanup or a later
    setup-managed selection mechanism.
- Option B: Discover and check candidates, then select one by a documented
  stable precedence rule when several are ready.
  - Pro: Existing multiple-environment installations can run unattended.
  - Con: A stable ordering can still select a runtime the maintainer did not
    intend, and becomes another compatibility rule to maintain.
- Option C: Require a setup-owned record selecting one checkout-local runtime,
  then independently verify its readiness on invocation.
  - Pro: Setup and upgrades make the runtime choice explicit and reproducible.
  - Con: Introduces a record lifecycle and a bootstrap dependency on item 6;
    existing installations need preparation before the launcher works.

#### Recommended option for Q02

Option A: Require one ready candidate for this foundation. It avoids accidental
selection while keeping runtime preparation and repair with item 6. Readiness
must cover the executing revision's dependencies and isolated import path,
not merely an executable's presence or reported Python version.

#### Answer to Q02: option C

Confirmed by the user on 2026-10-18: choose C with clarification. Each selected
llm-shared checkout has one authoritative setup-managed Python environment for
all its tools. Setup and upgrade own its designation, preparation, replacement
and repair; release tooling locates it independently of caller activation and
verifies readiness for the executing revision without repairing it mid-release.

There is no environment per consuming project, separate release environment,
foreign or global Python fallback, or ranking of leftover environment
directories. Older directories cannot make the authoritative environment
ambiguous. A consumer build keeps its own toolchain.

The original option mentions a setup-owned selection record. The confirmed
choice requires an authoritative setup-owned identity, not a new record file:
an existing setup identity mechanism may suffice. This confirmed C supersedes
the original recommendation of A above; the exact location mechanism remains
design work.

Round 1 clarification: Q08 and Q09 are pending choices within this confirmed
ownership model. They do not reopen the choice of llm-shared's one Python.
Subsequently, the user confirmed Q08 A and Q09 A on 2026-10-20.

### Q03: Who should own the common configuration schema?

The common reader must reject malformed, conflicting or unknown declarations
before mutation, while later items own version, changelog and setup behavior.
How should their settings become part of one complete validation pass?

#### Clarifications for Q03

A schema is the definition of accepted sections and keys, value types, defaults
and validation rules. For example, the changelog component defines that its mode
accepts `generated` or `curated`. A project's `.release.ini` supplies values to
those rules; projects do not write or maintain the schemas or validators.

A and B concern where those definitions live inside llm-shared's versioned
source. In A, each domain's definitions live beside its owning version, changelog
or setup component, and an explicit registry combines them for common
validation. In B, the central definition would be one foundation-owned Python
module containing every domain's schemas and defaults. Exact module names are
left to implementation planning.

Both options allow each consuming project to keep its own versioned
`.release.ini` at its root. B would not introduce one shared `.release.ini` for
all projects. Under the approved A, a project can omit the file entirely when
defaults suit it, or declare only the overrides it needs, without having to
understand or copy the default rules.

The common reader validates every declared setting before mutation, even when
the current command does not use it. Unknown keys, conflicting declarations and
invalid values fail. A custom declaration missing a required value without a
default also fails; defaults never conceal an invalid declaration.

#### BBQ for Q03

At a barbecue, one organizer checks the whole order, but the grill and dessert
stations know their own menus. Give the organizer each station's menu, or have
the organizer maintain a single master menu. In this picture: the organizer is
the common configuration reader, stations are domains, menus are schemas, and
the complete order is `.release.ini`.

#### Options for Q03

- Option A: Compose an explicit registry of domain-owned declarative schemas.
  The common reader controls parsing, duplicate schema ownership and unknown
  keys; schemas validate all declared settings before any domain may mutate.
  - Pro: Domain rules evolve with their owners while every command receives
    consistently validated configuration.
  - Con: Registration and cross-domain conflicts need a defined common contract;
    an omitted schema cannot be treated as permission to ignore its keys.
- Option B: Keep all domain schemas and defaults in one foundation-owned schema.
  Domain handlers consume the resulting validated values.
  - Pro: One place describes every accepted setting and its validation order.
  - Con: Each later domain change also modifies the foundation and can duplicate
    domain knowledge across owners.

#### Recommended option for Q03

Option A: Compose explicitly registered schemas supplied by shipped tooling
code, never by importing project configuration as code. Validate declared
settings even when the current command does not use them. A domain without a
shipped schema cannot silently accept unknown keys or execute a placeholder.

#### Answer to Q03: option A

Confirmed by the user on 2026-10-19: choose A, provided suitable defaults require
no project-specific configuration work. Version, changelog and setup components
own and ship their schemas in llm-shared's versioned code. A schema defines
accepted sections and keys, value types, defaults and validation rules; for
example, the changelog component defines `generated` and `curated` modes.

An explicit registry combines those schemas for one common validation pass.
Validate every declared setting before mutation, including settings unused by
the current command, and reject unknown keys and conflicting ownership or
declarations. Invalid values or incomplete declarations missing required values
without defaults must fail rather than silently fall back to defaults.

Each consuming project may have its own versioned `.release.ini` at its root.
It may omit the whole file when defaults suit it, or supply only the overrides
it needs. Projects do not need to copy, register or maintain schemas or
validators to use those defaults.

The alternative B's central definition would live in one foundation-owned
Python module in llm-shared, containing every domain's schemas and defaults.
Both A and B use optional per-project configuration; B does not mean one shared
`.release.ini` for all projects. A keeps definitions beside their domain owners
while retaining common validation.

Round 1 wording completion: schemas may own fixed sections or section families
by prefix, including `source:` and `changelog-archive:`. Their owners supply
validation functions for parsed families and cross-section constraints.
The explicit registry tuple has a completeness check for every shipped schema.
The reader accepts UTF-8 with an optional leading byte-order mark; subsequently
confirmed Q12 A checks the stable tooling minimum before strict domain
validation, with its stated interim refusal until comparison is available.

### Q04: Which launcher layer should own Windows argument transport?

The public batch entrypoint must preserve the argument values supplied under
the supported caller syntax, including spaces, quotes and metacharacters. The
design currently leaves the launch boundary between the shell and the Python
argument vector implicit. Which frontend structure should the design pursue?
Neither choice relaxes the argument-preservation requirement.

#### Clarifications for Q04

The selected Python is the authoritative setup-managed environment of the
llm-shared checkout being executed, as agreed in Q02. The batch launcher locates
and verifies that environment, then invokes its Python directly. It does not
select the consuming project's Python or a global interpreter from PATH.

PowerShell remains a supported calling shell under A. The choice means there
is no required PowerShell helper between the batch launcher and Python; it does
not restrict callers to cmd. Consumer builds keep their own toolchains.

The launcher forwards the shared CLI's stdout, stderr and public exit status unchanged.
As agreed in Q05, stdout carries requested results, stderr carries diagnostics,
and public statuses are 0 for success, 1 for execution failure and 2 for invalid
input or failed preflight. A native subprocess status can be normalized by the
shared CLI, with its original value preserved in diagnostics; the launcher does
not reinterpret that public status. Failures before the renderer and unexpected
native statuses follow the additional Q05 boundary rules. Q05 also details
the stream encoding and live output contract.

#### BBQ for Q04

A guest's written order can pass directly from the host to the cook, or through
a second coordinator who also checks the equipment. Every handoff must preserve
the order exactly. In this picture: the host is the batch entrypoint, the cook
is Python dispatch, the coordinator is a PowerShell bootstrap, and the written
order is the caller's argument values.

#### Options for Q04

- Option A: Keep the batch bootstrap minimal and invoke the selected Python
  entrypoint directly. Python owns validation and dispatch after argument
  capture; no additional shell command is built from caller values.
  - Pro: Fewer parsing boundaries and no extra shell dependency for consumers.
  - Con: Batch bootstrap and native argument forwarding remain delicate and
    need evidence for each supported caller, including embedded quotes.
- Option B: Have the batch entrypoint delegate bootstrap and native-process
  invocation to a PowerShell frontend before Python dispatch.
  - Pro: Bootstrap logic can use structured path and process APIs in a language
    already used by this repository.
  - Con: Adds another parsing boundary and a PowerShell compatibility contract;
    it does not automatically solve batch or native argument quoting.

#### Recommended option for Q04

Option A: Start with the smallest frontend. The implementation plan must prove
the supported cmd, PowerShell and automation invocations preserve values;
neither raw `%*` forwarding nor extra escaping is proof by itself. If that
boundary cannot meet the contract, revise this design before implementation
approval instead of silently restricting accepted values.

#### Answer to Q04: option A

Confirmed by the user on 2026-10-19: choose A. Keep the batch bootstrap minimal
and invoke the selected llm-shared checkout's authoritative Python directly,
using the setup-managed environment agreed in Q02. Python owns validation and
dispatch after argument capture, and the launcher returns the engine's status.

The implementation must demonstrate that supported cmd, PowerShell and
automation invocations preserve spaces, embedded quotes, `%`, `!` and `&` under
the documented caller syntax. If the direct boundary cannot meet that contract,
revisit the design before implementation approval; do not silently restrict
accepted values.

Round 1 evidence meets that revisit condition: plain batch forwarding changed
`%PATH%`, stripped embedded quotes through Windows PowerShell 5.1, allowed an
extra shell command from an automation value, and changed `%` and `^` through
`call`. Option A remains the chosen frontend structure. Subsequently confirmed
Q10 A completes the free-text and cross-checkout transport choices; separately
confirmed P1 completes the path channel. Preserving values remains mandatory.

### Q05: How should domains report results and failures?

The requirement separates machine-consumed results from diagnostics and keeps
failures visible through launchers. Should domains return a common outcome to
one renderer, or directly own their CLI streams and status?

#### Clarifications for Q05

A domain is a component such as version handling, changelog handling or release
execution. Under A, each returns structured result data, diagnostics and an
outcome category. The shared CLI renderer turns those into the public interface:

- stdout carries the requested result, for example the version `1.2.3`, so a
  script can capture it without mixing in explanatory messages.
- stderr carries warnings and errors, for example a diagnostic that inherited
  shell settings refer to another project.
- Exit status 0 means success, 1 means execution failure, and 2 means invalid
  input or failed preflight. The caller can check this status independently of
  either output stream; the batch launcher preserves it.

Native failure details remain visible. For example, if an underlying build
process exits with 7, the shared CLI can return public status 1 while its
diagnostic identifies the failed build and its original status 7. This example
does not assign a universal meaning to every tool's native status 7.

A does not require buffering live build output until completion. Build/release
design must provide the streaming interface while preserving the shared public
contract. Domain data formats, combined build/postprocessing failures and
recovery remain with their owners. B instead lets each component own its streams
and statuses behind common preflight: this preserves existing behavior more
directly but leaves callers with different conventions across components.

#### BBQ for Q05

Each barbecue station can send the host a completed order and a problem note,
or announce both directly to the guests. In this picture: stations are domain
handlers, the host is the dispatcher, completed orders are result data, problem
notes are diagnostics, and announcements are stdout/stderr and exit status.

#### Options for Q05

- Option A: Return structured outcomes with result data, diagnostics and a
  status category. One CLI renderer writes result data to stdout, diagnostics
  to stderr, and maps success to 0, execution failure to 1, and invalid input
  or failed preflight to 2. Preserve native failure details in diagnostics.
  - Pro: Consumers get one stable failure and stream contract across domains;
    a stale-root warning cannot contaminate a version result.
  - Con: Domains need to translate their failures into common categories, and
    long-running build output needs a separately defined streaming interface.
- Option B: Let each domain own stdout, stderr and its nonzero status, while the
  dispatcher enforces common preflight and passes those outputs through.
  - Pro: Existing tool statuses and streaming behavior can be preserved directly.
  - Con: Callers must understand several status vocabularies and each domain
    must independently maintain the result/diagnostic separation.

#### Recommended option for Q05

Option A: Centralize the small public result contract. Domain data formats and
item 5's live build output, combined build/postprocessing failures and recovery
remain with their owners. A normalized failure code must retain the original
failure's identity and status in diagnostics rather than erase it.

#### Answer to Q05: option A

Confirmed by the user on 2026-10-19: choose A. Domains return structured outcomes
with result data, diagnostics and a status category. The shared CLI renders
results to stdout and diagnostics to stderr, mapping success to 0, execution
failure to 1, and invalid input or failed preflight to 2. Preserve native failure
identity and status in diagnostics, and pass the public interface through the
launcher unchanged. This makes automation predictable while live build
streaming, domain data formats and transaction/recovery rules retain their
respective owners, as clarified above.

Round 1 wording completion: missing runtime, unsupported platform and failed
readiness return 2 even before the renderer starts. Uncaught exceptions
return status 1. An unexpected native status outside 0 through 2 is reported and normalized
to 1 when the launcher regains control, including interruption; hard termination
cannot promise a diagnostic. Python stdout and stderr use UTF-8 with LF.
Q10 and Q14 must cover cancellation and hidden batch prompts for automation.

### Q06: Where should managed writes be authorized and revalidated?

The design separates read-only configuration and artifact resolution from
preparation, and requires physical path checks again before writes. How should
domains receive that capability without treating the initial root check as
permanent authorization for any later destination?

#### Clarifications for Q06

The release engine uses the selected llm-shared checkout's one setup-managed
Python, as agreed in Q02. Here, a module means a Python source file containing
related functions. A domain or component means an area of that engine's code,
such as version handling, changelog handling or release coordination. All these
functions execute under that same Python.

A shared interface means common functions and their accepted arguments, reused
by those components. The managed-write service is local Python code called
through that interface. It requires no additional interpreter, environment,
server or user prompt.

For illustration, `changelog.py` could prepare the new changelog and ask a
function in `files.py` to check its destination and write `CHANGELOG.md`.
Functions in `versions.py` could use that same helper for `version.txt`.
These names illustrate code organization; they do not prescribe actual files.
The component decides what to change and when; the common functions check
where the change will happen and perform the filesystem operation.

In A, components use those common functions after completing their required
preliminary checks (preflight). In B, each component's own functions contain
the destination checks and instructions to open and write files. Both use the
same llm-shared Python; B duplicates the checking and writing code.

The checks must consider the destination at write time. For example, a command
targeting `C:\projects\B` may initially validate `B\docs\CHANGELOG.md`, then
`docs` may become a junction pointing into project A. The original path check
cannot authorize a later write into A. Read-only resolution also stays separate
from creating directories: reading a version must not create `.reviews`.

A centralizes destination enforcement while each component keeps complete
preflight, transaction ordering, recovery and cleanup. Git's linked-worktree
metadata and item 3's tooling cache retain their distinct boundaries. The
guarantee covers ordinary changes between preflight and writing, including
redirected junctions, but not a hostile process racing each operation. File
writes use a temporary file in the revalidated parent, revalidate the physical
final target, then replace atomically. Planning must prove that discipline;
a path recheck alone does not provide atomic protection against every race.

#### BBQ for Q06

The barbecue host approves a serving area, but tables can move before food is
carried out. One steward can check each delivery destination, or every station
can perform the same check itself. In this picture: the serving area is the
worktree, moving tables are changed path/link destinations, stations are domains,
and the steward is the common managed-write service.

#### Options for Q06

- Option A: Expose read-only resolution to all handlers and a separate managed-
  write service used only after domain preflight. The common service revalidates
  containment and repository boundaries before artifact preparation or writes.
  - Pro: One boundary covers ignored artifacts and ordinary managed files;
    domains cannot accidentally reuse an eager artifact helper during reads.
  - Con: Domains must route managed filesystem mutations through a shared
    interface, whose scope must remain separate from their transaction logic.
- Option B: Give handlers validated paths and require each domain to repeat
  containment checks and defer preparation before its own direct writes.
  - Pro: Domains retain full control over filesystem operations.
  - Con: Enforcement is duplicated and easier to omit when adding a write path
    or handling a failure; a validated path can become stale.

#### Recommended option for Q06

Option A: Centralize managed-destination enforcement while domains own complete
preflight, transaction ordering and cleanup. This service is not a general
transaction engine. Git's linked-worktree metadata and item 3's explicitly owned
tool cache keep their distinct boundaries.

#### Answer to Q06: option A

Confirmed by the user on 2026-10-20: choose A with the clarifications above.
Within the release engine running under the one llm-shared Python, components
route managed filesystem changes through common functions that revalidate
physical containment and repository boundaries before preparing artifacts or
writing. Read-only resolution remains separate and creates no artifacts.

This choice centralizes destination checks instead of duplicating them in each
Python component. Components retain complete preflight, transaction ordering,
recovery and cleanup; the common functions do not become a general transaction
engine. Round 1 completes the guarantee as described above: handle ordinary
changed destinations, revalidate before temporary-file creation and final
atomic replacement, and make no hostile-race protection claim. Subsequently
confirmed Q13 A serializes cooperating same-project mutating commands through
one shared project operation lock, with the ownership and recovery rules below.

### Q07: Where should current-directory alias resolution live?

Aliases discover the current worktree and pass an explicit root; engine and
standalone commands must never infer a missing root. The proposed dispatcher
mentions both invocation origins without defining the boundary. How should the
foundation share alias discovery while keeping its engine API explicit?

#### Clarifications for Q07

An alias is a shortcut such as `gv`. Running it from `C:\projects\B\src` must
discover `C:\projects\B` as the worktree root and pass that explicit path to
the release engine. If inherited shell settings still name project A, report
both roots and target B. Outside a Git worktree, discovery fails.

In A, the alias-resolution facade is a dedicated entrypoint for shortcuts in
llm-shared. Common Python functions use the controlled Git adapter to discover
the worktree, then invoke the ordinary explicit-root engine path. They run
under the same llm-shared Python agreed in Q02. Shell adapters pass the invocation
data; they do not each implement their own project discovery. In B, each shell
adapter, such as cmd or PowerShell, contains that discovery logic.

Capture the caller's original directory before any launcher changes directories.
Keep the shortcut entrypoint distinct from commands requiring an explicit root:
a direct command missing its root still fails, even inside a valid worktree.
Alias installation remains item 6's responsibility, with consuming-build
integration in items 5 and 8.

#### BBQ for Q07

Guests may ask the host which barbecue they have reached, but the cook accepts
only orders carrying an address. One host desk can answer that question for all
guests, or each entrance can keep its own map. In this picture: guests are alias
callers, the host desk is a shared alias resolver, entrances are shell adapters,
the address is the explicit root, and the cook is the engine dispatcher.

#### Options for Q07

- Option A: Provide a separate alias-resolution facade using the common Git
  adapter. It captures the caller's directory, resolves its worktree and passes
  an explicit root into the same engine path as standalone callers.
  - Pro: Discovery and mismatch diagnostics stay consistent; missing-root
    inference cannot leak into the explicit engine interface.
  - Con: The invocation surface must distinguish the facade from explicit-root
    commands, and preserve the original directory before any launcher movement.
- Option B: Require each shell alias adapter to discover the worktree and pass
  the explicit root, leaving the engine with no alias-specific facade.
  - Pro: The engine exposes only one explicit-root invocation form.
  - Con: Git isolation, failure behavior and caller-directory capture are
    duplicated across shell adapters or require another shared resolver anyway.

#### Recommended option for Q07

Option A: Share discovery behind a distinct alias-only facade, followed by the
ordinary explicit-root validation path. Keep alias installation with item 6
and consuming-build integration with items 5 and 8. Calling an explicit-root
command without its root must still fail, even from a valid worktree.

#### Answer to Q07: option A

Confirmed by the user on 2026-10-20: choose A. Provide a dedicated entrypoint
for aliases using common discovery functions and the controlled Git adapter
under the same llm-shared Python. Capture the caller's original directory,
resolve its worktree, and pass the resulting explicit root through the ordinary
engine validation path. Diagnose stale-root mismatches and fail outside Git.

This centralizes discovery and diagnostics across shell shortcuts while keeping
direct engine and standalone calls explicit: a missing root remains an error.
Alias installation and consuming-build integration retain their existing
owners, as clarified above.

Round 1 wording completion: the alias-only surface is
`bin/release_alias.bat`; the explicit-root surface is
`bin/release_workflow.bat`. Neither changes directory before Python captures
cwd. No `%CD%` argument is reparsed by batch, and a missing explicit root
never selects alias discovery.

### Q08: How does setup expose its runtime identity before item 6 exists?

Q02 C fixes the owner and rejects runtime ranking. Current setup creates a
version-named environment through `switchpy`, but records no authoritative
directory. Item 1 needs that identity before item 6, while item 6 depends on
item 1. Which producer and contract remove this ordering cycle?

#### Clarifications for Q08

The identity names the one environment already owned by llm-shared setup.
It neither creates another Python nor selects a consumer interpreter.
llm-shared's own `senv.bat`, through `switchpy`, remains the authority that
prepares this environment. Q08 asks how a later release invocation obtains
that setup decision without running setup again.

`LLM_SHARED_DIR` names the tooling checkout, not its environment directory.
Ordinary consumer discovery first checks the sibling
`%PRJ_DIR%\..\llm-shared`, then a valid `LLM_SHARED_DIR` fallback; the selected
launcher's own location fixes the executing checkout. Finding that checkout
does not distinguish environment directories inside its `venvs`.

The shell variables describe the current activation:

| Variable | Meaning in the current setup |
| --- | --- |
| `PYTHON_HOME` | Base Python installation selected by `switchpy`, outside the venv |
| `PYTHON_VERSION` | Python version selected by `switchpy` |
| `VIRTUAL_ENV` | Environment directory set by its activation script |

Activating a consumer can replace those values, and a fresh automation shell
may have none. Invoking the designated venv's `Scripts\python.exe` directly
uses that environment's installed libraries without setting `VIRTUAL_ENV`.
Python identifies the venv through the executable location and `pyvenv.cfg`;
activation mainly makes that executable available as plain `python` on PATH.
The isolated invocation described above also excludes inherited Python import
settings.

Current shared launchers do not all call llm-shared's `senv.bat`:
`prompt_workflow.bat` and `review_exchange.bat` locate a venv directly;
`ghog.bat` initializes the consuming project and separately invokes llm-shared's
Python. Calling llm-shared's `senv.bat` on every release is another possible
contract, but its `NO_MORE_SENV_...` guard can skip reactivation, and a full
initialization can synchronize dependencies and perform other setup work.
Option A preserves the agreed separation between setup and release invocation.

Having exactly one directory under `venvs` would make location straightforward.
Current `switchpy` uses version-dependent directory names and does not remove
older environments on a Python version change. Q02 permits such leftovers
without changing the authoritative runtime. The record exposes setup's choice
without ranking directories or requiring their removal.

Under A, the record is local to ignored `venvs`, has a format version, and
contains a checkout-relative environment directory. It is not committed to Git.
Its exact filename and serialization remain implementation details. For example,
the following illustrates its meaning, not a prescribed file format:

```text
Selected checkout: C:\projects\llm-shared
Directory recorded by setup: venvs\python_3.13.9_llm-shared
Python invoked: C:\projects\llm-shared\venvs\python_3.13.9_llm-shared\Scripts\python.exe
```

Even if the shell's `VIRTUAL_ENV` names `C:\projects\my-project\venvs\...`,
the release launcher reads the selected checkout's record and invokes the
recorded Python. Validation rejects an unsupported record format, missing
target, escape from that checkout's `venvs`, or unusable interpreter. Setup
publishes the record only after successful preparation; release commands read
it, verify readiness and never repair it or run setup. Confirmed Q09 A defines
which dependencies establish that readiness.

For the setup producer, record the environment `switchpy` actually prepared,
for example the activated interpreter's prefix, rather than reconstructing
its directory-naming rules. Write that path as data without batch `echo` of
path text. This is implementation guidance within Q08 A's existing contract.

Item 1 is the release foundation and needs this handoff immediately. Item 6 is
the later setup and upgrade work, which depends on that foundation. A therefore
includes the narrow producer addition in item 1 while leaving the full
installation, upgrade and repair lifecycle with item 6.

#### BBQ for Q08

The cook needs to know which grill the host prepared before a later equipment
service is built. The host can leave a label today or the event can wait for
that service. In this picture: the cook is item 1, the grill is llm-shared's
environment, the label is runtime identity, and the later service is item 6.

#### Options for Q08

- Option A: Item 1 defines the local identity record and adds its production
  to current setup after `switchpy` and dependency preparation succeed.
  Choosing A also approves amending the feature request's item 1 scope to
  include that setup producer step. Item 6 later owns installation, upgrade
  and repair of the same contract.
  - Pro: Deterministic and testable within item 1 without ranking environments.
  - Con: Existing checkouts need setup to run once, and a new record is added.
- Option B: Derive a single directory from a versioned exact Python patch
  version and checkout name, with no record.
  - Pro: Avoids a separate identity file.
  - Con: Couples the public contract to external `switchpy` naming and pins a
    patch version for every checkout.
- Option C: Move item 6's runtime-identity work ahead of item 1.
  - Pro: Keeps all identity production inside the setup item.
  - Con: Changes the approved umbrella order and delays the foundation.
- Option D: Call llm-shared's `senv.bat` within each release tool invocation,
  ensure activation occurs, and use the resulting environment.
  - Pro: Uses setup directly as the runtime authority without a separate record.
  - Con: Changes the no-setup-at-release contract, can synchronize dependencies
    at startup, and requires guard handling and protection of the consuming
    project's identity and caller environment.
- Option E: Require setup to leave exactly one environment directory under
  the selected checkout's `venvs`, then locate and validate that environment.
  - Pro: Needs neither an identity record nor activation during release.
  - Con: Requires setup to enforce uniqueness and changes Q02's allowance for
    leftover environments that cannot affect runtime selection.

#### Recommended option for Q08

Option A, as recommended in round 1. It keeps setup as the producer and makes
item 1 independently usable. The narrow setup addition and record contract
must be explicit in item 1's accepted scope before implementation.

#### Answer to Q08: option A

Confirmed by the user on 2026-10-20: choose A with the clarifications above.
Item 1 defines the local runtime identity record under ignored `venvs` and adds
its production to current llm-shared setup after `switchpy` and dependency
preparation succeed. This explicitly approves the corresponding narrow
feature-request scope amendment. Item 6 retains ownership of the full
installation, upgrade and repair lifecycle; the umbrella order does not change.

Setup remains the authority over llm-shared's one environment. Release tooling
reads setup's recorded choice and validates it independently of caller
activation, without ranking leftover directories, running `senv.bat`, repairing
the environment or choosing another Python. Existing checkouts need successful
setup to produce the record. Subsequently confirmed Q09 A defines the dependency
checks in this same llm-shared environment.
The user explicitly requested retaining this question and its options:
recording this answer does not authorize consolidation.

### Q09: Which llm-shared dependencies must be ready before a release starts?

Q08 identifies the one Python environment prepared by llm-shared's setup.
Before starting its release engine, which installed packages in that environment
must llm-shared verify: only the packages needed by the release engine, or every
package used to develop and test llm-shared? The alternative is to forbid
third-party packages in the release engine entirely.

This question concerns llm-shared's own dependencies, declarations and lock file.
It does not ask the consuming project to declare or install llm-shared packages.

#### Clarifications for Q09

**The project being released and the tooling that releases it have separate
dependencies.** For example, suppose `C:\projects\my-app` calls release tooling
from `C:\projects\llm-shared`. The proposed ownership is:

| Location | Role in this example |
| --- | --- |
| `C:\projects\llm-shared\pyproject.toml` | Declares the packages llm-shared's release engine needs, in a group named `release` |
| `C:\projects\llm-shared\uv.lock` | Records the resolved versions of those packages and their dependencies for this llm-shared revision |
| `C:\projects\llm-shared\venvs\<environment-directory>` | Holds llm-shared's one setup-managed Python environment, whose installed packages release startup checks |
| `C:\projects\my-app\pyproject.toml` and `uv.lock`, if present | Describe my-app's own dependencies; Q09 adds no llm-shared dependencies here |
| my-app's own environment, if it has one | Serves my-app's build and tests; it does not supply llm-shared's release-engine packages |

The consumer may not even be a Python project or have a `uv.lock`. Its own
build gate still checks whatever it needs to build and test. That is separate
from checking whether llm-shared can start its release engine.

**A dependency group is a named list, not another Python environment.**
Under option A, llm-shared adds a `release` group to its own `pyproject.toml`
and updates its own `uv.lock`. Its existing `dev` group includes `release`
through PEP 735 `include-group`. Thus the usual llm-shared setup installs both
release packages and development tools into the same environment already
selected under Q02 and Q08. There is no second release-only environment and
no per-consumer copy of these dependencies.

The inclusion is one-way: installing `dev` also installs `release`, but checking
`release` does not check everything in `dev`. A test runner, profiler or analysis
tool that only serves llm-shared development must not prevent the release engine
from starting. If a package also serves the release engine, it belongs in the
release check regardless of its development use.

**"Only release-engine dependencies" includes the packages those dependencies
need.** A direct dependency is a package the release engine itself requires.
A transitive dependency is a package needed by one of those packages, possibly
through several levels. Both must be available for the engine to work. The
check covers the applicable dependencies for the supported Windows platform
and selected interpreter, using the executing llm-shared revision's lock.
It does not check every unrelated package that happens to appear in that lock.
The interpreter must also satisfy llm-shared's declared Python requirement.

For illustration only, suppose the release engine needs a package called
`release-format-lib` at locked version `2.4`, that package needs
`format-helper` at locked version `1.7`, and llm-shared developers separately
use a profiler called `dev-profiler`. These are hypothetical package names,
not a decision to adopt particular libraries:

| State in llm-shared's selected environment | Result of the Q09 A dependency check |
| --- | --- |
| Both release packages have the required versions and the release engine's modules import | Pass, provided the interpreter requirement also passes |
| `release-format-lib` is missing or has the wrong version | Fail: a direct release dependency is not ready |
| `format-helper` is missing or has the wrong version | Fail: a transitive release dependency is not ready |
| Both release packages are ready, but `dev-profiler` is missing or broken | Pass: this development-only package is outside the release check |
| The required packages exist only in my-app's environment | Fail: they are missing from the llm-shared environment actually running the engine |
| Installed versions match, but importing a release engine module fails | Fail: matching metadata alone does not establish readiness |

Passing this check establishes package readiness, not success of the entire
release. Project configuration, Git and the consumer's build still have their
own checks.

**Setup installs; release startup verifies.** These are different moments:

1. During llm-shared setup, its own `senv.bat` and setup tools prepare the
   authoritative environment and synchronize its declared dependencies.
   Including `release` from `dev` ensures this preparation installs the release
   packages. Setup checks that preparation succeeded before publishing the
   Q08 runtime identity record.
2. During a later release invocation, the launcher uses that record to invoke
   llm-shared's designated Python. A small bootstrap, meaning the initial
   startup code, checks the interpreter and release dependencies before loading
   the engine's third-party code.
3. If the check fails, startup returns status 2 with setup-repair guidance.
   It does not run setup, install packages, select another environment or
   create consumer artifacts. Repair belongs to llm-shared setup.

The proposed bootstrap itself uses only Python's standard library: `tomllib`
reads llm-shared's TOML declarations and lock, and `importlib.metadata` inspects
the distributions installed in the designated environment. It checks applicable
locked versions before importing the release engine's own modules. This lets
it diagnose a missing prerequisite before a normal engine import fails.
Reading a lock file verifies the expected versions; it does not install them.

Applicability comes from each locked dependency's environment marker,
evaluated with standard-library code against the running interpreter and
platform. A marker the bootstrap cannot evaluate fails readiness with status
2, naming the package and the marker; it is never skipped or assumed to apply.

Q09 A limits the release-startup check. It does not narrow the existing setup
process to installing only release packages, and it does not decide which
third-party libraries future release features will need. The `release` group
must stay complete as those features are implemented.

#### BBQ for Q09

Before cooking, check the supplies needed for this meal rather than the whole
party warehouse. In this picture: meal supplies are release dependencies,
the warehouse is the full dev group, and the advance check is the bootstrap.

#### Options for Q09

- Option A: Declare a release dependency group in llm-shared's own
  `pyproject.toml`, lock it in llm-shared's own `uv.lock`, and include it from
  llm-shared's existing dev group. At release startup, verify only its applicable
  direct and transitive dependencies in llm-shared's designated environment,
  plus the interpreter requirement.
  - Pro: Readiness covers release needs without unrelated dev-tool failures.
  - Con: Adds a dependency group whose contents must stay complete.
- Option B: Require llm-shared's complete locked dev dependency set in that
  same llm-shared environment.
  - Pro: Uses the existing group and one shared-tooling readiness rule.
  - Con: An unrelated test or analysis package can block release operations.
- Option C: Require a standard-library-only llm-shared release engine and an
  isolated engine import.
  - Pro: Keeps dependency readiness simple.
  - Con: Constrains later domains, including formats without a standard-library
    writer, and may duplicate existing library behavior.

#### Recommended option for Q09

Option A, with the dependency-free bootstrap. It gives readiness a declared,
checkable scope and preserves status 2 for missing prerequisites.

#### Answer to Q09: option A

Confirmed by the user on 2026-10-20: choose A with the clarifications above.
Declare and lock the `release` group in llm-shared's own `pyproject.toml` and
`uv.lock`, and include it from its existing `dev` group so setup installs the
packages in llm-shared's one authoritative environment. The consuming project's
dependency declarations, lock and environment are not used for this check.

Release startup verifies only the release group's applicable direct and
transitive dependencies and locked versions, plus the Python requirement,
before importing the release engine's own modules. Marker evaluation follows
the clarification above and fails with status 2 if applicability cannot be
determined. Unrelated development packages cannot block that check. The
standard-library bootstrap returns status 2 with setup-repair guidance when
prerequisites fail; it does not install or repair anything.

The user explicitly requested retaining this question and its options:
recording this answer does not authorize consolidation.

### Q10: How can launchers pass project paths, titles and notes to Python unchanged?

The caller already knows which project it wants to release. How should its
paths and free text reach llm-shared's release engine without a shell changing
them or interpreting part of a value as another command? Q04 A retains a small
batch frontend; Q10 decides which values that frontend can forward and which
must travel through another channel.

#### Clarifications for Q10

**Knowing the root and transporting it are separate concerns.** In the usual
project build, the project's own `senv.bat` sets `PRJ_DIR` before calling
llm-shared. This supplies a possible source of the path, but writing
`%PRJ_DIR%` on a batch `call` line expands the value into command text.
The confirmed P1 channel instead passes the variable's name, allowing Python
to read its contents from the inherited environment without putting that path
through the batch argument parser.

For example, these illustrate the data and selector, not a complete command:

```text
Environment value: RELEASE_INPUT_PROJECT_ROOT = C:\R&D\proj
Command arguments: --project-root-env RELEASE_INPUT_PROJECT_ROOT
Python reads:      C:\R&D\proj
```

`--project-root-env PRJ_DIR` could use the existing variable in exactly the
same way when the caller deliberately initializes it to the intended root.
A new variable name is not intrinsically required by this transport.
The selector is explicit: a missing root does not make the engine silently
consult `PRJ_DIR`. The engine still validates the supplied root and uses it
throughout the operation.

**`PRJ_DIR` is mutable and may be inaccurate.** The user specifically raised
this concern while considering P1. Another setup invocation or a manual
assignment can replace it, and an inherited value may name a different project.
Checking that it names a valid Git worktree cannot establish that the caller
intended that worktree. A stale value naming another valid repository would
pass that structural check.

For that reason, the confirmed build integration derives the root from
`build.bat`'s own directory, independently of ambient `PRJ_DIR`, and places it
in a dedicated variable for the invocation. Under P1, it does so inside
`setlocal`/`endlocal`, with delayed expansion off, spanning `pre`, build and
`post`. A reused `PRJ_DIR` would need the same deliberate initialization from
the script-derived root and protection against intervening replacement.
Using a dedicated variable makes that obligation easier to keep visible.
Neither variable is immutable; the caller must control its value until Python
captures the explicit root.

For a standalone invocation, the caller supplies its intended root explicitly.
That root wins over an unrelated or stale `PRJ_DIR`, with a mismatch diagnostic
as already required. Conflicting explicit root inputs are rejected rather than
silently choosing between them. Aliases retain Q07's separate current-worktree
discovery. A full-path project build retains its own script-derived root.
Thus the value-passing mechanism does not change who chooses the target.
The user separately confirmed P1 on 2026-10-20 with this root-source rule.

For example, if the shell still has `PRJ_DIR=C:\projects\A` and the user invokes
`C:\projects\B\build.bat`, the build must target B. Under confirmed P1, it assigns
B to its dedicated root variable from its own script location. Merely selecting
the inherited `PRJ_DIR` would explicitly supply A, which could be a valid but
unintended worktree. P1's selector mechanism alone does not prevent that error;
the caller's script-derived assignment does.

The same example separates the stale value from the actual input supplied to
the release engine:

```text
Inherited shell value: PRJ_DIR = C:\projects\A
Invoked build script:  C:\projects\B\build.bat
Fresh scoped value:    RELEASE_INPUT_PROJECT_ROOT = C:\projects\B
Command arguments:    --project-root-env RELEASE_INPUT_PROJECT_ROOT
Python reads:         C:\projects\B
```

Only the variable name appears in the selector arguments. Python reads the
path as environment data, so characters such as `&` in `C:\R&D\proj` do not
become shell operators through expansion on that argument line. The build
uses `setlocal`/`endlocal` with delayed expansion off, covering `pre`, build
and `post`, and restores the previous environment afterward. It must preserve
the intended value until Python captures it; a dedicated variable is not
inherently immutable. Missing, empty or conflicting selectors fail with
status 2. Diagnostics consuming a selector identify both the variable and the supplied
root or path, and ordinary root/path validation still applies.

**Each caller assigns selector variables for each launch.** Batch scripts
limit their lifetime with `setlocal`/`endlocal`, as the build example does.
PowerShell scripts assign immediately before the call and restore a previous
value, or remove a newly introduced variable, in `finally`. At a cmd or
PowerShell prompt there is no automatic launch scope: `setlocal` does not
scope interactive cmd commands, and PowerShell environment assignments remain
in the session. Prompt users assign each selected variable in the same command
line as the launch, using that shell's supported path-data syntax; the value
persists until reassigned or removed. Passing a selector again without a fresh
assignment can reuse an earlier project's path. Root validation cannot infer
that the caller intended a different valid checkout.

**P1 also covers locating an input file and preserves console stdin.**
`--input-file-env RELEASE_INPUT_FILE` lets Python read a UTF-8 payload's path
from an explicitly selected variable. The file's contents carry arbitrary
text; the environment selector carries only its locator. Relative locators
resolve against the validated project root, including while the launcher runs
from a temporary tooling directory. No variable is consulted implicitly.
Unlike piping the payload, passing these selectors does not replace stdin,
so it does not itself select non-interactive mode under Q14 B. An explicit
non-interactive request or non-console stdin still selects that mode.

P2 and P3 remain below as alternatives considered. P2 restricts the batch path
grammar and requires a native route outside it. P3 carries paths in a UTF-8
payload but still needs a safe way to locate that payload or consumes stdin.
The selected P1 supplies an explicit channel for the build's script-derived
root without those restrictions. It does not make arbitrary free text safe
for batch forwarding or prove the safety of the launcher-location mechanism;
those retain their separate contracts and required validation below.

**Free text has the same parsing problem but different sources.** A release
title containing literal `%PATH%` may be expanded, and `&` can separate commands
when it reaches an unsafe shell parsing boundary. By the time Python starts,
the original text may already be lost. Choosing the correct llm-shared Python
under Q08 and checking its packages under Q09 cannot repair that loss.
Round 1 demonstrated corruption through `%*`, Windows PowerShell 5.1 and batch
`call`, including an automation value that executed an additional command.

Free text includes release titles and notes. Project and tooling paths may
also contain shell metacharacters, so merely calling an argument a path does
not make it safe. Round 2 additionally showed Windows PowerShell 5.1 passing
the space-free path `C:\R&D\proj` unquoted to a forwarding batch file: Python
received `C:\R`, and cmd attempted to execute `D\proj`. These probes demonstrate
failures, not correctness of a proposed replacement.

Under A, batch command-line data is limited to command tokens and quoted paths
free of `%`, `^`, `!` and `"`. This grammar is a caller obligation. The engine
rejects those characters if they survive in a batch-only argument, but cannot
detect expansion, quote loss or command splitting that already occurred before
it started. It must not promise rejection of every unsafe invocation.
Structured UTF-8 files and stdin carry arbitrary text; the separately confirmed
P1 channel carries project-root and input-file paths. P1 through P3 remain
below with their original tradeoffs.

An interactive build cannot pipe a payload without replacing console stdin
and selecting non-interactive mode under Q14 B. `build.bat` cannot safely
author arbitrary text from its own arguments into a file, pipe or variable.
Inherited title arguments such as `rel_title...` are therefore not a supported
free-text source under A. Item 5 obtains titles and notes on the Python side
from a console prompt, `version.txt`, or a user-authored UTF-8 file. The same
exact values can then travel in its validated handoff.

For example, a title such as `Ready %PATH% & more` can be read as UTF-8 file
content by Python. It is never echoed by batch into a file or substituted into
a command. An interactive Python prompt can obtain the same text directly.
For automation, a native Python argument list or UTF-8 file/stdin carries the
value without an intermediate `.bat`. These are supported sources of exact
text; they are not escaping recipes for arbitrary `build.bat` arguments.
If the input file's path contains shell metacharacters, confirmed P1 also
applies to locating that file.

The confirmed channels under A with path choice P1 are:

| Caller | Command and path channel | Free-text channel |
| --- | --- | --- |
| Interactive cmd | Supported batch tokens and quoted paths in the grammar; other project/input-file paths use an explicitly selected variable assigned in the same command line as the launch. `setlocal` has no effect at the prompt, so the value stays in the console until reassigned or removed | User-authored UTF-8 file, or a Python-side console prompt; stdin data selects non-interactive mode |
| Doskey alias | Alias entrypoint captures cwd in Python without passing that path through an argument; other paths follow the cmd rule | Same file or Python-side prompt as cmd; the macro does not echo text into a payload |
| `build.bat` | Inside `setlocal` spanning `pre`, build and `post`, with delayed expansion off, assign `set "RELEASE_INPUT_PROJECT_ROOT=%~dp0"`. Use `pushd` to the launcher's directory, `call .\release_workflow.bat` with tokens and the variable selector, then `popd`. Relative data paths resolve against the validated project root | Python reads an existing file, `version.txt` or its console; arbitrary build-argument text is not forwarded or serialized by batch |
| Windows PowerShell 5.1 | Assign path data through PowerShell's environment API immediately before the call and pass only selectors to batch. Scripts restore or remove the previous value in `finally`; prompt users assign it in the launching command line. Never forward an unsafe metacharacter path as a batch argument | UTF-8 file or stdin, with no embedded-quote argument dependency |
| Python automation | Read the selected checkout's identity record and invoke its designated Python and trusted bootstrap script through a native argument list | Native argument values, UTF-8 file or stdin; no intermediate batch parsing |
| Cross-checkout execution | Invoke the target checkout's designated Python and trusted bootstrap through a native argument list after selecting that checkout explicitly | Original values as data, without re-entering a `.bat` |

The native routes run the same platform/readiness bootstrap; they never choose
another Python or skip runtime validation. Confirmed Q10 A approves the
requirement's caller wording amendment to recognize those routes and replace
inherited build-title argument syntax with the supported text sources above.
The feature request records that amendment. The user separately confirmed
the P1-specific path behavior in the table on 2026-10-20.

The launcher location is distinct from project-root or input-file data.
Round 3 probes showed that `call "<dir>\x.bat"` fails when `<dir>` contains
`%` or `^`, while `pushd "<dir>"`, `call .\x.bat` and `popd` reached it for
`%`, `^` and `!`. Windows PowerShell 5.1 reached batch files in `&`, `%` and
`^` directories directly. A selects that `pushd` form for `build.bat`;
validation must cover the required tooling locations. The `.\` prefix is
required because some hosts set `NoDefaultCurrentDirectoryInExePath`, which
stops cmd from resolving a bare name from the current directory.
The caller must stop if `pushd` fails, restore its directory on normal and
handled-error returns, and retain the release command's status across cleanup.

The alias surface is never reached through `pushd`, because it needs the
original caller directory. Under confirmed P1, explicit build calls carry their
root through the selected variable;
relative data paths, including an input-file locator, resolve against that
validated root instead of the temporary launcher directory.
The existing `call <NUL "%build_dir%\senv.bat"` also uses the failing direct
form. Under A, items 5 and 8 apply the same `pushd` form to that environment
call in the build integration template; this is not an item 1 implementation
change. Cancellation, UTF-8 decoding errors and stdin ownership remain
required transport proof cases. The probes support the named mechanism but
do not prove the complete release transport.

#### BBQ for Q10

A spoken order can lose punctuation at each relay. Put the exact order on a
card and pass the card to the cook. In this picture: relays are shell parsing
boundaries, the order is input values, the card is UTF-8 file/stdin data, and
the cook is the Python entrypoint.

#### Options for Q10

- Option A: Keep batch for supported cmd/build invocations, carry free text
  through UTF-8 file/stdin, and call authoritative Python directly from Python
  automation and cross-checkout execution. Use the per-caller channels above
  and choose the path sub-option below explicitly.
  - Pro: Removes free-text shell interpretation and repeated batch parsing from
    automation while retaining Q04 A.
  - Con: Changes inherited release-title argument syntax and requires item 5
    to adopt the data channel and each shell to document its invocation form.
- Option B: Keep all values on command lines with caller-specific escaping.
  - Pro: Retains the existing argument-shaped interface.
  - Con: The observed quote, percent and `call` failures show that a universal
    escaping recipe cannot be assumed; every caller needs separate proof.
- Option C: Replace the public batch boundary with a native executable shim.
  - Pro: Offers a native argument vector without an initial batch parser.
  - Con: Adds a binary build/signing/distribution responsibility outside the
    accepted v0.14.0 scope.

#### Path-channel sub-decision for Q10 option A

Selecting A alone did not select a path channel. The user subsequently chose
P1 explicitly on 2026-10-20. The earlier concern that `PRJ_DIR` can be
overridden or inaccurate is addressed by the script-derived root and scoped
assignment described above. This choice does not authorize trusting ambient
`PRJ_DIR`. All three options remain recorded for review.

- P1: Use path variables assigned for each launch and selected by explicit
  command options.
  For example, `--project-root-env RELEASE_INPUT_PROJECT_ROOT` reads that
  variable as the supplied root, and `--input-file-env RELEASE_INPUT_FILE`
  reads a UTF-8 payload's filename. Missing, empty or conflicting selectors
  fail with status 2. No variable is consulted implicitly. The caller assigns
  the variable for each launch and limits its lifetime: batch callers use
  `setlocal` and `endlocal`, and PowerShell scripts restore or remove the
  previous value in `finally`. At a cmd or PowerShell prompt no automatic
  launch scope exists, so the user assigns the variable in the same command
  line as the launch; the value persists until reassigned or removed.
  Ordinary root/path validation still applies.
  `build.bat` assigns the variable inside `setlocal` and `endlocal`, spanning
  `pre`, build and `post`, so its value cannot leak into the user's console.
  Its source is the build script's own directory, independent of ambient
  `PRJ_DIR`. The selector may name `PRJ_DIR` only when the caller deliberately
  initializes and preserves it for this invocation; an inherited value alone
  does not satisfy the build's root-source contract.
  Every diagnostic that consumes a selector names the variable and the root
  or path it supplied, making a stale manually assigned value visible.
  - Pro: A build can pass `%~dp0` as data with delayed expansion off, and
    PowerShell can assign a metacharacter path without passing it through cmd.
    Input-file locators receive the same channel.
  - Con: Callers must set and scope the value deliberately. This is a path
    channel, not a way for batch to serialize arbitrary free text or a proof
    that the launcher invocation itself is safe.
- P2: Restrict batch path values to the documented grammar and require a
  native Python route for values outside it.
  - Pro: Keeps batch data arguments simple and makes the limitation explicit.
  - Con: A build rooted outside the grammar needs another supported caller
    route; accepting a restriction would require an explicit requirement
    change, not merely an implementation diagnostic.
- P3: Put paths in a user-authored UTF-8 payload at a filename that itself
  satisfies the batch grammar, or provide that payload on stdin.
  - Pro: Uses the same data format for paths and free text.
  - Con: Does not let batch manufacture an arbitrary payload or encode its
    script-derived root safely, and stdin payloads replace the console.
    An interactive build needs an additional explicit root mechanism.

#### Recommended option for Q10

Option A plus P1, completing the round 1 recommendation with an explicit
data-path channel. It keeps arbitrary text out of command parsing and carries
a build's script-derived root without placing that value on the `call` line.
The user has confirmed both the overall A approach and the separate P1 choice.
Implementation must still prove the full caller and cancellation contract.
Q04 A alone did not settle Q10.

#### Answer to Q10: option A with path choice P1

Confirmed by the user on 2026-10-20: choose A with the clarifications above.
Keep batch for supported cmd/build calls, obtain arbitrary titles and notes
through UTF-8 file/stdin or the defined Python-side sources, and invoke the
designated llm-shared Python directly for Python automation and cross-checkout
execution. Every route retains the same runtime and project validation.
Build integration uses the selected relative `call` form from the launcher's
directory, restores cwd and preserves the command's status.

This answer also approves the explicitly described requirement amendment:
recognize the native Python routes and replace inherited arbitrary build-title
arguments with the supported text sources. It does not weaken value preservation.

Separately confirmed by the user on 2026-10-20: choose P1 with the
clarifications above. Pass explicit variable-name selectors for project-root
and input-file paths. The build derives its root from its own script location,
assigns a dedicated launch-scoped variable with delayed expansion off, and
preserves that value across `pre`, build and `post` inside `setlocal`/`endlocal`.
Python reads the selected variable directly; the path value is not expanded
into the batch selector arguments. This avoids relying on stale `PRJ_DIR`.

Other callers also assign the selected variable for each launch. PowerShell
scripts restore its previous state in `finally`; cmd and PowerShell prompt
users assign it in the launching command line and account for its persistence
afterward. P1 does not supply automatic scope at a prompt.

Missing, empty or conflicting selectors fail with status 2; diagnostics
identify the selected variable and its supplied value. Validate the resulting
root/path normally and resolve relative input-file locators against the
validated project root. The selector mechanism leaves stdin available and
does not itself enable or disable prompting. Explicitly selecting `PRJ_DIR`
is valid only with deliberate initialization and preservation of the intended
root; the engine never infers a missing root from that variable.

The user explicitly requested retaining this question and its options:
recording this answer does not authorize consolidation.

### Q11: Which installed Git should the engine run, and what version is required?

The caller normally already has Git on PATH. How should llm-shared find that
executable and make sure every Git operation uses the same one, instead of
letting a file in the current directory replace it? Which minimum Git version
must that executable satisfy for the design's configuration checks?

#### Clarifications for Q11

**Option A uses Git already on the current process's PATH.** It does not
require a separate Git installation inside llm-shared, ask setup to record a
Git identity, or choose the newest installed Git. The caller's PATH order
remains the preference order. The release engine resolves the first eligible
`git.exe`, then checks its version and retains its full executable path.

An eligible PATH entry is an absolute directory other than the current working
directory. Empty entries, relative entries and the current directory are
excluded. Only an actual `git.exe` is a candidate; a directory containing
`git.cmd` or `git.bat` alone supplies no candidate. The engine does not use
`PATHEXT` to select one of those batch wrappers, because doing so would put
Git arguments such as commit and tag messages through cmd parsing again.

For example, suppose the current directory is `C:\projects\my-app`, and the
following PATH entries are encountered in this order:

| PATH entry | Example contents | Q11 A behavior |
| --- | --- | --- |
| An empty entry | No absolute directory specified | Skip |
| `.` | The current project directory | Skip: relative and current-directory lookup |
| `tools` | A directory relative to the current directory | Skip: not absolute |
| `C:\projects\my-app` | A project-local `git.exe` | Skip: still the current directory even though the entry is absolute |
| `C:\helper-wrappers` | Only `git.cmd` | Skip: no eligible `git.exe` |
| `C:\Program Files\Git\cmd` | Installed `git.exe` | Select this executable and check its version |

The excluded directory is the engine process's working directory when Git
is selected. On the `build.bat` route that is the tooling directory, so the
example's skip of `C:\projects\my-app` applies when the engine runs from
that directory. No route performs a bare-name search.

In this example the executable retained for the operation is:

```text
C:\Program Files\Git\cmd\git.exe
```

The same absolute path is used for root validation, configuration inspection,
artifact tracking checks and subsequent Git operations. Changing a subprocess's
working directory does not trigger another bare-name search. A later release
invocation resolves its own Git from the PATH it receives.

**The problem is executable selection, separately from repository selection.**
Passing a project root to Git and controlling variables such as `GIT_DIR`
govern an operation only after a Git executable has started. They do not ensure
that the intended executable starts. Round 1 demonstrated this by placing a
`git.exe` in the caller's working directory and observing bare-name resolution
run it. Q11 A avoids that lookup while retaining the caller's installed Git.

**The minimum version is Git 2.31.0.** This is the version floor proposed for
the configuration facilities cited in round 1 and accepted with option A.
Executable selection comes first; only then may the engine run the selected
executable to read its version. If no eligible executable exists, its version
cannot be established, or it is below the minimum, prerequisite validation
fails with a diagnostic. Release invocation does not install or upgrade Git.

Configured user helper programs remain a separate trusted-code boundary.

#### BBQ for Q11

Before asking a guide for directions, identify the hired guide rather than
whoever stands closest to the gate. In this picture: the guide is Git, the
gate is cwd, and the verified appointment is the absolute path and version.

#### Options for Q11

- Option A: Use the first eligible `git.exe` from the current process's PATH
  in order, considering only absolute directories and excluding cwd, empty or
  relative entries and batch shims. Require Git 2.31.0 or newer and retain the
  executable's absolute path for the operation.
  - Pro: Prevents cwd substitution without tying Git installation to llm-shared.
  - Con: Machines with older Git or only a relative PATH entry need correction.
- Option B: Let setup designate an absolute Git executable beside runtime identity.
  - Pro: Makes the Git choice explicit and repeatable across invocations.
  - Con: Adds setup coupling and another identity to maintain on each machine.
- Option C: Retain bare-name resolution.
  - Pro: Reuses the existing subprocess helper without a resolver.
  - Con: Permits the planted-executable behavior observed in round 1.

#### Recommended option for Q11

Option A with minimum Git 2.31.0. It closes the observed cwd substitution and
gives the configuration policy a versioned prerequisite.

#### Answer to Q11: option A

Confirmed by the user on 2026-10-20: choose A with the clarifications above,
including the stated minimum Git 2.31.0. Use Git already available through the
current process's PATH; no separate llm-shared Git installation is required.
Resolve the first eligible `git.exe` in PATH order, excluding cwd, empty or
relative entries and `.bat`/`.cmd` wrappers. Check its version only after
selection, retain its absolute path and version once per operation, and use
that path for all Git calls, including the initial validation checks.

The user explicitly requested retaining this question and its options:
recording this answer does not authorize consolidation.

### Q12: Should the required llm-shared version be checked before unfamiliar configuration settings?

A consuming project's `.release.ini` can require a newer llm-shared version
and contain settings that an older checkout does not understand. Should the
tool first explain that llm-shared needs updating, or first reject those
unfamiliar settings? What should happen while item 1 can read the required
version but item 6 has not yet supplied the version-comparison rules?

#### Clarifications for Q12

**The minimum is a required llm-shared tooling version.** It is not the
consuming project's release version, its Python version, or its Git version.
The declaration belongs to the consumer's `.release.ini` because that file
describes what its release tooling must understand. For example:

```ini
[tooling]
minimum-version = 0.15.0
```

Suppose the executing llm-shared checkout is version `0.14.0`, and the same
configuration contains settings introduced in `0.15.0`. Once version
comparison is available, option A first reports that this configuration
requires llm-shared `0.15.0` or newer and that the selected tooling needs
updating. It stops before trying to validate those domain settings. An
unknown-setting error alone would obscure the action the user needs to take.
This compatibility check reports that action; it does not itself upgrade
llm-shared.

The foundation first parses the INI and reads the stable
`[tooling] minimum-version` schema without executing project code. Malformed
INI and syntactically invalid minimum values still fail. Once the executing
tooling satisfies the minimum, every declaration undergoes strict validation:
the minimum is never permission to ignore unknown settings or invalid values.
If the key is absent, ordinary strict domain validation proceeds.

**Option A includes an interim restriction before item 6 is available.**
Item 1 defines the stable key, its syntax and the bootstrap contract, but
does not invent version ordering. Until item 6 supplies comparison semantics,
any declared minimum makes the command stop with status 2 and a diagnostic
that compatibility evaluation is not yet available. This includes a minimum
that looks older than the executing tooling: without the agreed comparator,
item 1 cannot assume that it is satisfied. Generated configuration therefore
omits the key during this interim.

| Configuration case | Before item 6 supplies comparison | Once item 6 supplies comparison |
| --- | --- | --- |
| No minimum declared | Proceed to strict domain validation | Proceed to strict domain validation |
| Valid minimum declared | Stop with status 2: compatibility evaluation unavailable | Compare versions before strict domain validation |
| Executing `0.14.0`, required `0.15.0` | Same interim refusal; do not claim a comparison occurred | Stop with an update diagnostic before rejecting unfamiliar domain settings |
| Executing tooling satisfies the minimum | Same interim refusal; do not assume compatibility | Validate every declaration strictly |
| Malformed INI or invalid minimum syntax | Reject invalid configuration | Reject invalid configuration |

Item 6 owns the comparison, including how snapshot and candidate versions
such as `0.14.0-SNAPSHOT` relate to `0.14.0`. Item 1 makes no ordering claim
about those versions. Item 6 supplies that evaluation without changing the
key's meaning or weakening strict domain validation.

#### BBQ for Q12

Read the recipe's required oven model before rejecting unfamiliar oven settings.
In this picture: the recipe is `.release.ini`, the model is the tooling minimum,
and the settings are domain keys.

#### Options for Q12

- Option A: Check the stable tooling-minimum schema before strict domain validation.
  Until item 6 supplies comparison semantics, validate syntax and fail closed
  when a minimum is declared, with a compatibility-unavailable diagnostic.
  - Pro: Reports the update action first while retaining strict validation for
    compatible tooling.
  - Con: Requires a stable bootstrap key; configurations declaring it cannot
    be used until item 6 supplies comparison semantics.
- Option B: Validate strictly first and add the minimum-version update hint
  to unknown-key diagnostics.
  - Pro: Preserves one strict validation order.
  - Con: Reports unsupported keys before explaining that the tooling is too old.
- Option C: Tolerate unknown keys when the minimum is newer.
  - Pro: May permit a command that happens not to use the new settings.
  - Con: Weakens AC8 and can silently ignore important behavior.

#### Recommended option for Q12

Option A, as recommended in round 1. It stops incompatible execution with a
useful remedy and never treats newer configuration as permission to ignore keys.

#### Answer to Q12: option A

Confirmed by the user on 2026-10-20: choose A with the clarifications above.
Check the stable tooling-minimum schema before strict domain validation.
Until item 6 supplies comparison semantics, validate syntax and stop with
status 2 whenever any minimum is declared, explaining that compatibility
evaluation is unavailable; generated configuration omits the key. An absent
key proceeds to strict domain validation.

Once comparison is available, incompatible tooling reports the update action
before domain validation, while compatible tooling validates every declaration
strictly. The check does not perform the upgrade. Item 6 owns version ordering,
including snapshot and candidate versions.

The user explicitly requested retaining this question and its options:
recording this answer does not authorize consolidation.

### Q13: What prevents two commands from modifying the same project simultaneously?

Two terminals can run release, version or changelog commands against the same
project. How should the tools prevent those operations from interleaving their
changes, and who owns the lock and its recovery if an operation stops?
Version and changelog commands can also run outside item 5's full release
transaction, so protecting only that transaction would leave other commands
uncoordinated.

#### Clarifications for Q13

**Writing each file correctly does not make several file changes one operation.**
Atomic replacement means a reader sees a complete old or new file rather than
a partially written file. It does not stop another command from changing a
different managed file between two replacements. For example, without a shared
lock:

| Step | Terminal 1: release command | Terminal 2: version command |
| --- | --- | --- |
| 1 | Updates `version.txt` for its release | Has not started |
| 2 | Continues using its previously checked project state | Updates `pom.xml` for a different version |
| 3 | Continues the release assuming the files still describe its intended version | Continues its own updates |

Every individual write can succeed while the files describe different intended
versions or one operation overwrites the other's changes. A version-only lock
and a separate release-only lock would still allow these two commands to
overlap. Under A, the foundation supplies one shared lock used by all cooperating
version, changelog and release commands that modify the same project. A second
operation fails visibly while another operation owns it. This coordinates
llm-shared commands; it is not protection against arbitrary external writers.

**The lock is acquired after complete preflight and retained through cleanup.**
The mutating command follows this order:

1. Complete its validation without creating artifacts or changing managed files.
2. Prepare the validated artifact home and acquire the project operation lock
   atomically, so two operations cannot both become its owner.
3. Revalidate state that could have changed between preflight and acquisition.
4. Perform its managed changes while retaining ownership.
5. Complete cleanup and release ownership.

Checks before acquisition alone are insufficient: another operation might
finish changing the project just before this command obtains the lock.

**The owner is the whole operation, not just its current Python process.**
For a release spanning `pre`, build and `post`, the Python process running
`pre` can exit while the build continues. A validated handoff retains operation
ownership during that gap, even when no release-engine Python process exists.
The `post` invocation continues the same operation through that handoff.
Item 5 defines the handoff's validation and transfer against this foundation
contract; unrelated commands cannot adopt its operation identity.

While a process owns the lock, its identity includes both its process id and
creation time, because an id can be reused. Neither the exited `pre` process
nor the user's long-lived cmd process defines the whole operation's lifetime.

**Recovery requires evidence that ownership has ended.** Automatic stale-lock
recovery is allowed only when the exact process owner is gone and no retained
handoff owns the operation. Elapsed time alone is insufficient, and the absence
of an engine process during a build does not make its lock stale. A retained
but abandoned or unverifiable handoff requires explicit human recovery through
an action item 5 provides, rather than automatic lock removal. Live contention
always fails visibly.

**Reads remain unlocked, and locking does not provide rollback.** Read-only
commands take no lock and create nothing. They may observe an intermediate
combination while one operation replaces several files, such as a new
`version.txt` alongside an old `pom.xml`. Each file replacement is atomic;
the pair is not one atomic snapshot. A domain needing transaction-consistent
reads must explicitly design that later capability. If an operation fails
after changing files, the lock itself does not undo those changes: item 5
retains ownership of release transactions and rollback.

#### BBQ for Q13

Two cooks must not rewrite the same serving order at once. One shared sign
marks who currently owns it, even when a cook changes stations. In this picture:
cooks are mutating commands, the order is project state, the sign is the
operation lock, and changing stations is item 5's handoff.

#### Options for Q13

- Option A: Give the foundation a project-wide operation lock after complete
  preflight, with operation ownership across handoffs and the conservative
  recovery and read-consistency rules above.
  - Pro: Coordinates version, changelog and release commands under one boundary.
  - Con: Requires recovery and cross-process ownership design.
- Option B: Let each domain serialize its own writes.
  - Pro: Keeps locking near the domain's transaction logic.
  - Con: Different domains can still interleave changes to the same project.
- Option C: Document one mutating operation at a time without enforcement.
  - Pro: Adds no lock state or recovery mechanism.
  - Con: A second shell can violate the rule and corrupt shared state silently.

#### Recommended option for Q13

Option A with conservative ownership-based recovery. It gives all mutating
domains one exclusion contract while preserving artifact-free reads.

#### Answer to Q13: option A

Confirmed by the user on 2026-10-20: choose A with the clarifications above.
The foundation owns one shared project operation lock covering version,
changelog and release mutations. Acquire it atomically after complete
preflight, revalidate state that could have changed, and retain ownership
through managed mutation and cleanup. A competing live operation fails visibly.

Ownership belongs to the whole operation and persists across validated
`pre`, build and `post` handoffs. Automatic stale recovery requires the exact
process owner to be gone and no retained handoff to own the operation; an
abandoned or unverifiable retained handoff requires explicit human recovery
through an action item 5 provides.
Read-only commands remain unlocked and artifact-free, with no multi-file
snapshot guarantee. The lock does not provide rollback.

The user explicitly requested retaining this question and its options:
recording this answer does not authorize consolidation.

### Q14: How does a command decide whether it may ask the user for input?

A release command may need a title or another answer that the caller has not
supplied. In an interactive console it can ask the user, but an automated job
could remain stuck waiting for someone who cannot answer. How should the
command select non-interactive mode, and how should that decision survive
the separate `pre`, build and `post` stages?

#### Clarifications for Q14

**Option B combines an explicit caller choice with detection of non-console
input.** Standard input, or stdin, is the input stream from which a command
reads. It can be connected to the user's console, a pipe, a file or `NUL`.
The command selects non-interactive mode when the caller explicitly requests
it, or when Windows reports that stdin is not a console. An ordinary console
invocation may prompt unless the caller requested non-interactive mode.

For example, suppose a release requires a title that has not been supplied:

| Invocation | Mode under B | Behavior when the required title is missing |
| --- | --- | --- |
| Console stdin, no explicit non-interactive request | Interactive | Python may ask the user to enter the title |
| Console stdin, explicit non-interactive request | Non-interactive | Fail and explain how to supply the title |
| A Q10 data payload is piped into stdin | Non-interactive | Fail and explain how to supply the title; do not try to ask through the pipe |
| Stdin comes from a file or `NUL` | Non-interactive | Fail and explain how to supply the title; do not wait for a console answer |

When all required inputs are supplied, non-interactive execution can proceed
under the command's normal validation and authorization rules. **Non-interactive
mode does not mean automatically answering yes.** It disables questions; it
does not invent missing values or consent. Missing required information causes
a visible, actionable failure. Automation that has a console attached should
still explicitly request non-interactive mode: console detection establishes
the input channel, not whether a person is actually available to answer.

**The Windows console check must identify a real console.** Use
`GetConsoleMode` on the stdin handle. Python's `isatty()` alone is insufficient:
in round 2's probe, input redirected from `NUL` returned `isatty() == True`
while the Windows API reported no console. Relying on `isatty()` would therefore
select the wrong mode for that case.

Piping a Q10 payload replaces console stdin and selects non-interactive mode.
Such callers must supply all required values through the supported input
channels. This decision provides no override that re-enables questions while
stdin is redirected. Any future interactive override would need a separately
designed console channel.

**The selected policy belongs to the whole operation.** Item 5 records it in
the validated handoff and applies it to both `pre` and `post`. For example,
if `pre` selected non-interactive mode, `post` must not start asking questions
because an inherited variable changed or its immediate input environment
looks different. An inherited environment variable is not the authority that
can silently reverse the recorded choice.

**Disabling Python questions alone is insufficient.** In non-interactive mode,
Git receives detached stdin and disabled terminal prompting. A helper that
cannot finish without interaction must fail visibly. Native helpers and batch
cancellation also need validation for hidden prompts; changing the engine's
message renderer does not control those programs or the shell. The selected
Q10 non-batch automation route remains required where batch termination could
otherwise prompt.

#### BBQ for Q14

Before asking guests to choose a side dish, check whether anyone is at the
table to answer. In this picture: guests are a console user, the table is
stdin, the choice is a required prompt, and a completed order is explicit input.

#### Options for Q14

- Option A: Use an explicit non-interactive option only.
  - Pro: Gives callers a simple intentional switch.
  - Con: A forgotten switch can leave automation waiting for a prompt.
- Option B: Combine that option with non-interactive mode when stdin is not
  a console according to the Windows console API, and preserve the result in
  the build handoff.
  - Pro: Redirected and automated calls cannot silently fall into engine prompts.
  - Con: Piped callers must provide required values instead of answering later.
- Option C: Use an inherited environment variable as the policy source.
  - Pro: Propagates easily to subprocesses.
  - Con: Reintroduces stale environment state and can lose intent across shells.

#### Recommended option for Q14

Option B, as recommended in round 1, with the redirected-input clarification
above. It makes missing input fail visibly and carries one policy across the
operation.

#### Answer to Q14: option B

Confirmed by the user on 2026-10-20: choose B with the clarifications above.
Select non-interactive mode when explicitly requested or when the Windows
console API reports that stdin is not a console. Use `GetConsoleMode` on the
stdin handle rather than relying on `isatty()`. Missing required input fails
with an actionable diagnostic; it does not trigger a prompt or automatic
consent. Piped callers supply all required values, with no interactive override
for redirected stdin under this decision.

Preserve the selected policy through item 5's validated `pre`, build and `post`
handoff. In non-interactive mode, detach Git's stdin and disable its terminal
prompts; validate native helpers and batch cancellation for hidden prompts.
An inherited environment variable cannot silently reverse the policy.

The user explicitly requested retaining this question and its options:
recording this answer does not authorize consolidation.
