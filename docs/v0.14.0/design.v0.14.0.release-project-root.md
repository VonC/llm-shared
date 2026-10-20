# Design v0.14.0: explicit release project identity

Reference feature request:
[feature-request.v0.14.0.release-project-root.md](feature-request.v0.14.0.release-project-root.md).

## Context for the release-project-root design

Shared release tooling must operate on one explicitly validated project while
executing code and Python from the selected llm-shared checkout. The approved
requirement separates those identities, caller initialization and artifact
ownership before version, changelog and release-lifecycle behavior is added.

This document defines the foundation's approved responsibilities and interfaces.
Git subprocesses isolate inherited routing, each llm-shared checkout supplies
one authoritative setup-managed Python environment, and domain-owned schemas
provide common configuration validation with defaults that require no project
configuration when suitable. The batch launcher invokes that Python directly,
and one shared CLI renderer owns result streams and public exit statuses.
Common Python functions check destinations and perform managed writes within
that same release engine. A separate entrypoint for aliases discovers the
caller's worktree and passes its explicit root to the engine. The design
decisions table records all seven confirmed choices and their trade-offs.
The requirement and [focused draft](draft.v0.14.0.release-project-root.md)
retain their approved behavioral scope.

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
| `senv.bat` | Sets `PRJ_DIR`, `PRJ_DIR_NAME` and tooling variables before its guard | Caller initialization already owns identity; the engine must not reactivate it |
| `build.bat` | Derives `build_dir` from its script and calls its own senv before legacy preprocessing | Preserve the script-derived caller boundary; item 8 later replaces legacy integration |
| `bin/mds.ps1` | Derives the checkout from its own path, selects a venv directory by name and invokes Python by absolute path | Demonstrates self-location, but does not establish the new runtime-readiness policy |
| `bin/prompt_workflow.bat` | Keeps an inherited `LLM_SHARED_DIR` when present and selects a matching venv by modification time | Copying this launcher would violate the new checkout identity guarantee |
| `bin/ghog.bat` | Selects `python_3*` directories by name | Existing launchers do not share one selection rule |
| `pyproject.toml` | Currently requires Python `>=3.13, <3.14`; tooling runs in place with `package = false` | Validate against the executing revision's declared runtime; do not infer readiness from directory names |
| `tools/git_command.py` | Accepts explicit cwd, environment and stdin options; Windows executes Git without an intermediate shell | Provides an execution primitive, but does not itself validate project identity |
| `tools/review_artifact_configuration.py` | Separates read-only `load` from `prepare_home` and accepts a tracking-check callback | Reuse configuration semantics without preparing artifacts during validation |
| `tools/artifact_home.py` | Convenience calls prepare the home and may move a legacy file | Do not use those convenience calls during preflight or read-only commands |

These facts describe current code, not changes already implemented for this
topic.

## Invocation flow and validation boundaries

The invocation flow is:

```text
capture original caller directory and arguments before launcher movement
  -> self-locating launcher locates and verifies its setup-managed runtime
  -> direct call supplies a root, or alias entrypoint discovers one
  -> explicit-root Python dispatcher receives invocation data
  -> validate platform, project root and Git context
  -> load and validate project configuration and artifact declaration
  -> select a supported domain handler
  -> handler performs its own remaining preflight
  -> authorized writes use explicit project destinations
  -> result and diagnostics return through the launcher
```

This is a separation of responsibilities, not a file-by-file implementation
sequence. No artifact preparation occurs merely to construct or reject an
invocation. Domain preflight remains responsible for conditions introduced by
that domain before it requests writes.

The invocation context carries:

| Context value | Purpose |
| --- | --- |
| Project root and derived project name | One authoritative worktree identity |
| Tooling root and authoritative runtime identity | The selected checkout's code and setup-managed interpreter actually executing |
| Invocation origin and original argument vector | Distinguish explicit-root calls from alias discovery without reparsing values as commands |
| Git execution context | Explicit target, controlled subprocess environment and linked-worktree metadata |
| Validated configuration | Shared parsing plus validation by the owning domain |
| Artifact declaration | A validated destination, without eager creation |
| Interactive policy | Preserve non-interactive intent across the future build handoff |

Keep this context fixed for one operation. An upgrade that selects another
checkout starts execution there with the selected root and original arguments;
the current operation must not silently replace its tooling identity.

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
does not authorize a changed link target. Detailed filesystem operations belong
in implementation planning after this boundary is reviewed.

Approved Q01 A makes the Git adapter responsible for a controlled environment
for every Git subprocess, including those used to validate the root. Later Git
operations require the validated context and an explicit working directory.
The adapter removes inherited routing and configuration-injection inputs that
could redirect the repository, worktree or index. It diagnoses ignored conflicts
and preserves ordinary identity, signing and credential settings when they can
coexist with the target guarantee. The parent shell is not changed.

For example, after activating project A, the caller explicitly targets B.
Inherited `GIT_DIR`, `GIT_WORK_TREE` or `GIT_INDEX_FILE` may still name A;
`git -C B` alone does not override every such input. Isolation means controlling
what each Git subprocess inherits so validation and operations target B.
It does not create another checkout, container or sandbox.

This policy keeps explicit-root operations usable from stale shells and gives
every domain the same targeting guarantee. Its implementation must define and
verify the complete routing and configuration-injection policy; clearing only
the three example variables is insufficient. Configuration sources that cannot
safely coexist with that guarantee must produce a clear failure.

The existing Git execution helper may implement the final subprocess call.
It must not be treated as proof that environment routing or path identity was
validated.

## Launcher responsibilities and authoritative runtime

Use `bin/release_workflow.bat` as the public Windows entrypoint and keep its
responsibility limited to locating its own checkout and authoritative runtime,
verifying readiness, preserving the caller's arguments and returning the engine
status. The minimal batch bootstrap invokes that Python directly; Python owns
validation and dispatch after argument capture. PowerShell remains a supported
calling shell without becoming a required intermediary. Forward the shared
CLI's stdout, stderr and public exit status unchanged.
Treat codepage changes as scoped to the launcher's run and restore the caller's
codepage on exit. Do not activate senv or modify the caller's PATH.

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

Setup must expose the authoritative identity so release tooling can locate and
validate it. An existing setup identity mechanism may satisfy this contract;
the decision does not require a new selection-record file. The concrete
location mechanism must be coordinated with item 6 before runtime integration.
Discovery or ranking of leftover environments cannot substitute for that
setup-owned identity.

Inherited Python import settings must not load a consumer's module in place of
the selected release engine. Startup and dependency checks must also preserve
the prohibition on writes to the consumer during failed preflight.

The exact Windows argument transport needs proof with spaces, quotes, `%`,
`!` and `&`. Do not treat a raw `%*` expansion, delayed expansion or an extra
`call` layer as proof of preservation. Python dispatch works with an argument
vector after capture; values are never interpolated into executable command
text. Demonstrate preservation for cmd, PowerShell and automation using the
documented caller syntax. If the direct boundary cannot meet this contract,
revisit the design before implementation approval; do not silently narrow the
accepted values. The later transaction handoff remains item 5's responsibility.

## Common configuration with domain-owned validation

Use a strict INI reader with interpolation disabled. Load only the selected
root's `.release.ini`; distinguish an absent file from read, encoding and
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

Definition ownership stays inside llm-shared, beside the owning components.
The optional `.release.ini` remains per project; there is no shared
configuration file for all consuming projects. Exact Python file names remain
for implementation planning.

The common reader owns parsing, file diagnostics, schema registration conflicts
and unknown-key detection. Schemas come only from shipped tooling code, and
the registry must reject duplicate ownership or conflicting declarations.
A missing schema cannot make its keys acceptable. This permits source and
changelog extensions without moving their behavior into the foundation.

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
These are ordinary local calls, requiring no additional interpreter,
environment, server or user prompt.

For example, changelog code prepares content and asks the common functions to
write it to `CHANGELOG.md`; version code uses them for `version.txt`. The
functions recheck physical containment and repository boundaries before
artifact preparation or managed writes. Components retain their complete
preflight, transaction ordering, recovery and cleanup; the common functions do
not become a general transaction engine. Exact Python file names and function
signatures remain implementation-planning work.

For example, a command may validate `C:\projects\B\docs\CHANGELOG.md`, then
`docs` may become a junction into project A. Its earlier path check cannot
authorize a write into A. The plan must establish the guarantees of the chosen
filesystem operations: rechecking a path alone does not establish atomic
protection against every race. Read-only version lookup creates no `.reviews`.

This design reuses the existing artifact policy rather than copying its parser.
It does not modify review-exchange behavior. Per-operation temporary names,
cleanup and transaction ownership remain with the domains that generate them;
the shared git-cliff cache remains item 3's distinct write area.

## Dispatch and result interfaces

The Python dispatcher requires an explicit root for engine and standalone
commands. A direct command missing its root fails even inside a valid worktree.
A separate alias entrypoint, sometimes called a facade, captures the caller's
original directory before any launcher movement. Its common Python functions
use the controlled Git adapter to discover that directory's worktree, then
pass the resulting explicit root through ordinary engine validation.

For example, `gv` invoked from `C:\projects\B\src` discovers `C:\projects\B`.
If inherited shell settings name A, diagnose the mismatch with both roots and
target B. Outside a Git worktree, discovery fails. The alias entrypoint runs
under the same llm-shared Python; shell adapters pass invocation data instead
of each implementing discovery and its diagnostics.

Shell adapters execute the selected project build when required and do not
duplicate root validation or configuration semantics. Alias installation
belongs to item 6; consuming-build integration remains with items 5 and 8.

Domain handlers receive the fixed context and return structured outcomes with
result data, diagnostics and an outcome category. One shared CLI renderer
writes requested data to stdout and warnings/errors to stderr. This allows a
stale-environment warning without corrupting a version result.

| Public exit status | Meaning |
| --- | --- |
| 0 | Success |
| 1 | Execution failure |
| 2 | Invalid input or failed preflight |

The batch launcher forwards this public interface unchanged. Preserve native
failure identity and status in diagnostics: a build exiting with 7 may produce
public status 1 while the diagnostic identifies the build and its native 7.
This example does not assign a universal meaning to native status 7. Failure
must never become success.

Structured outcomes do not require buffering live build output until completion.
Item 5 owns the streaming interface and combined build/postprocessing failure
rules under this public contract. It must retain the original build failure
when postprocessing also fails. Domain data formats and transaction/recovery
rules remain with their owners.

The missing-launcher exception is evaluated by the consuming build adapter:
ordinary build intent may proceed with its warning and read-only version
display; release or snapshot intent anywhere among arguments must fail.
An installed handler must not use this exception to hide an execution failure.
The actual lifecycle handling and build invocation belong to item 5.

## Acceptance cases for the approved foundation

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
| Direct command omits its root inside a valid worktree | Fail with status 2; alias discovery is a distinct entrypoint | AC1 |
| Alias starts outside Git or launcher later changes directory | Fail outside Git; otherwise discover from the captured original directory | AC2 |
| A managed destination changes to a junction into A after preflight | Revalidate before mutation and reject the changed destination | AC4 |
| Supported cmd, PowerShell and automation arguments contain spaces, quotes, `%`, `!` or `&` | Prove preserved values under documented caller syntax without executing them | AC10 |
| Handler succeeds, fails execution or rejects preflight | Return 0, 1 or 2 respectively; keep diagnostics on stderr | AC10 |
| Native subprocess fails with status 7 | Preserve native identity/status in diagnostics and return public status 1 through the launcher | AC10 |
| Missing launcher and release intent is not the first argument | Reject the transition; item 5 owns the build-lifecycle behavior | AC11 |

The approved whole-suite scope applies to later validation. Plans will assign
test files, implementation steps and rollout checks from these settled design
decisions.

## Design decisions

| Question | Decision and reason | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | A: control inherited settings for every Git subprocess so a stale shell cannot redirect the validated target; retain compatible identity, signing and credentials without changing the parent | Project paths and Git execution | B: require callers to clean conflicting settings; unsafe configuration still fails under A |
| Q02 | C: one setup-managed Python environment per selected checkout, shared by its tools; release verifies readiness without fallback, ranking or repair | Launcher responsibilities and authoritative runtime | A: require exactly one ready candidate; B: rank candidates. C supersedes the earlier A recommendation and requires setup identity, not necessarily a new record file |
| Q03 | A: compose shipped domain-owned schemas in an explicit registry so complete validation and optional per-project overrides keep defaults beside their owners | Common configuration with domain-owned validation | B: centralize every domain's schema in one foundation-owned Python file, increasing coupling |
| Q04 | A: minimal batch bootstrap directly invokes that checkout's Python, reducing parsing boundaries while retaining cmd, PowerShell and automation callers | Launcher responsibilities and authoritative runtime | B: require an intermediary PowerShell bootstrap; neither option relaxes argument preservation |
| Q05 | A: structured outcomes and one renderer provide stdout results, stderr diagnostics and public statuses 0/1/2; native failure details remain visible | Dispatch and result interfaces | B: separate domain stream/status conventions, requiring callers to understand each; live streaming remains domain-owned |
| Q06 | A: common local Python functions revalidate and perform managed mutations after complete component preflight; reads create no artifacts | Artifact reuse without eager side effects; Project paths and Git execution | B: duplicate checks and writes in each component. Common functions do not take transaction ownership or make path rechecks atomic |
| Q07 | A: dedicated alias entrypoint captures the original directory and uses controlled Git discovery before explicit-root engine validation | Invocation flow and validation boundaries; Dispatch and result interfaces | B: duplicate discovery in shell adapters; direct commands still reject a missing root |
