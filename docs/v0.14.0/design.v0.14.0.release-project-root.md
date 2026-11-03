# Design v0.14.0: explicit release project identity

Reference feature request:
[feature-request.v0.14.0.release-project-root.md](feature-request.v0.14.0.release-project-root.md).

## Context for the release-project-root design

Shared release tooling must operate on one explicitly validated project while
executing code and Python from the selected llm-shared checkout. The approved
requirement separates those identities, caller initialization and artifact
ownership before version, changelog and release-lifecycle behavior is added.

This design defines the foundation's responsibilities and interfaces. Git
subprocesses isolate inherited routing; each llm-shared checkout supplies one
setup-managed Python environment; domain-owned schemas provide common
configuration validation and defaults. A minimal batch entrypoint invokes
that Python, while explicit path selectors and data channels preserve caller
values. Common functions enforce managed destinations and one project operation
lock coordinates mutations. A separate alias entrypoint discovers the caller's
worktree, and one renderer defines result streams and public statuses.

The 14 confirmed decisions are consolidated below after independent review.
The requirement includes Q08's narrow setup producer scope amendment and
Q10's caller/title transport amendment; the
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
  -> validate project root and Git context
  -> parse configuration and check the stable tooling minimum
  -> strictly validate domain configuration and artifact declaration
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

Here, cwd means the engine process's directory at Git selection. A build using
the temporary tooling-directory call described below selects Git from that
directory. This is not a blanket exclusion of the supplied project root.
For an engine running in `C:\projects\my-app`, the selection behaves as follows:

| PATH entry | Example contents | Selection behavior |
| --- | --- | --- |
| Empty, `.` or `tools` | No absolute directory | Skip |
| `C:\projects\my-app` | Project-local `git.exe` | Skip: the engine's current directory |
| `C:\helper-wrappers` | Only `git.cmd` | Skip: no eligible `git.exe` |
| `C:\Program Files\Git\cmd` | Installed `git.exe` | Select and check its version |

Selection precedes any version invocation. If no eligible executable exists,
its version cannot be established, or it is older than 2.31.0, preflight fails
with status 2 and a diagnostic. Release invocation does not install or upgrade
Git. The retained absolute path serves root validation, configuration inspection,
artifact tracking checks and later operations; changing a subprocess's cwd
never triggers a bare-name search. Each new invocation resolves its own Git.

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

### Setup-produced runtime identity

The record is local to ignored `venvs`, has a format version, and names a
checkout-relative environment directory. Its filename and serialization remain
implementation details. For example, a record in `C:\projects\llm-shared`
may name `venvs\python_3.13.9_llm-shared`; the launcher then invokes that
directory's `Scripts\python.exe`. Reject an unsupported record format, missing
target, escape from the selected checkout's `venvs`, or unusable interpreter.

Current setup publishes the record only after `switchpy` and dependency
preparation succeed. Record the environment `switchpy` actually prepared,
for example the activated interpreter's prefix, rather than reconstructing
its directory-naming rules. Write paths as data without batch `echo` of path
text. Existing checkouts need successful setup once to produce the record.

Consumer discovery first checks the sibling `%PRJ_DIR%\..\llm-shared`, then a
valid `LLM_SHARED_DIR` fallback. The selected launcher's location fixes the
checkout; inherited `LLM_SHARED_DIR` does not select its internal environment.
Likewise, `PYTHON_HOME` names a base installation, `PYTHON_VERSION` describes
the activation's choice, and `VIRTUAL_ENV` can name the consumer's environment.
None establishes this runtime identity. Directly invoking the recorded venv's
Python uses its executable location and `pyvenv.cfg` without activation.

### Release dependency readiness

A dependency-free bootstrap checks platform, the interpreter requirement and
the selected readiness contract before importing any engine third-party code.
Confirmed Q09 A requires a release dependency group in llm-shared's own
`pyproject.toml`, locked in its own `uv.lock` for the executing revision and
included by its existing `dev` group through PEP 735 `include-group` so current
setup installs it in the same environment. Release
startup checks only that group's applicable direct and transitive dependencies;
unrelated development packages and the consumer's lock are outside this check.
Failure returns status 2 and identifies setup repair as the remedy,
without attempting repair or creating consumer artifacts.

The bootstrap uses only the standard library: `tomllib` reads the tooling's
declarations and lock, and `importlib.metadata` checks installed distributions
against applicable locked versions. Evaluate locked environment markers with
standard-library code against the running interpreter and platform. An unknown
or unevaluable marker fails readiness with status 2, naming the package and
marker; never silently skip it or assume it applies. After metadata checks,
import the release engine's own modules; do not infer import names from
distribution names. Matching versions alone cannot prove imports work.

For illustration, suppose hypothetical `release-format-lib` 2.4 requires
`format-helper` 1.7, and `dev-profiler` serves only development:

| State in llm-shared's designated environment | Readiness result |
| --- | --- |
| Both release packages have locked versions and engine modules import | Pass if the interpreter requirement also passes |
| Either release package is missing or has a different version | Fail, including the transitive dependency |
| Release packages are ready but `dev-profiler` is missing or broken | Pass: development-only packages are outside this check |
| Required packages exist only in the consumer's environment | Fail: they are absent from the executing environment |
| Installed versions match but an engine module fails to import | Fail: metadata alone is insufficient |

The consumer may have no Python environment or lock at all. Its build gate
checks its own dependencies separately. This startup policy neither narrows
setup to release-only installation nor selects future third-party libraries;
the `release` group must stay complete as domains grow. Package readiness
does not replace project configuration, Git or build validation.

Launch Python with isolated imports and explicit UTF-8 mode (`-I -X utf8`).
The bootstrap derives the trusted tooling root from its own source location
and adds only that root for in-place engine imports; it must not trust the
consumer cwd, inherited `PYTHONPATH`, or user site-packages. Runtime packages
come from the designated environment. Disable bytecode writes during readiness
checks. Python streams are explicitly configured as UTF-8 with LF line endings;
codepage changes alone do not define stream encoding.

## Caller channels and value preservation

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
alter a value undetectable, so rejection of surviving unsafe characters is
not a guarantee that all unsafe invocations can be rejected. Implementation
approval waits for evidence for each supported caller.

### Explicit path selectors and their lifetime

An explicit selector names the variable whose value Python reads as data:

```text
Environment value: RELEASE_INPUT_PROJECT_ROOT = C:\R&D\proj
Command arguments: --project-root-env RELEASE_INPUT_PROJECT_ROOT
Python reads:      C:\R&D\proj
```

Only the variable name enters the batch selector arguments. No missing root
implicitly consults `PRJ_DIR`. A deliberately initialized and preserved
`PRJ_DIR` may be explicitly selected, but an inherited value alone does not
satisfy the build's root-source contract. Missing, empty or conflicting
selectors and conflicting explicit root inputs fail with status 2. Every
diagnostic consuming a selector identifies the variable and supplied root or
path; ordinary physical-root and destination validation still applies.

For example, when `PRJ_DIR=C:\projects\A` but the caller invokes
`C:\projects\B\build.bat`, the build assigns B from its own directory to a
dedicated selector variable. Inside `setlocal`/`endlocal`, with delayed expansion
off, it uses `set "RELEASE_INPUT_PROJECT_ROOT=%~dp0"` and preserves that value
across `pre`, build and `post`. The previous environment is restored afterward.
The variable is not immutable: the caller must control it until Python
captures the root. A stale selector naming valid A cannot reveal that B was
intended; validation cannot infer caller intent from a valid repository.

PowerShell scripts assign immediately before launch and restore the previous
value, or remove a newly introduced variable, in `finally`. At a cmd or
PowerShell prompt, assign each selector in the launching command line using
that shell's supported path-data syntax. Prompt assignments persist until
reassigned or removed; `setlocal` does not scope interactive cmd commands.
Passing a selector again without fresh assignment can reuse another project.

`--input-file-env RELEASE_INPUT_FILE` carries a UTF-8 payload's locator by
the same explicit mechanism. Relative locators resolve against the validated
project root, even during a temporary tooling-directory call. No variable is
consulted implicitly. A selector does not replace stdin or itself change the
interactive policy; the file's contents carry free text, not its path variable.

### Supported caller and free-text routes

Batch command-line data is limited to command tokens and quoted paths free
of `%`, `^`, `!` and `"`. This grammar is a caller obligation. Reject those
characters when they survive in batch-only arguments, without claiming to
detect corruption or command splitting that occurred before Python started.
P1 selectors supply the separate channel for project-root and input-file paths.

| Caller | Command and path channel | Free-text channel |
| --- | --- | --- |
| Interactive cmd | Supported tokens and quoted paths in the grammar; other project/input-file paths use an explicit variable assigned in the launching command line, with prompt persistence understood | User-authored UTF-8 file or Python-side console prompt; stdin data selects non-interactive mode |
| Doskey alias | Alias entrypoint captures cwd in Python; other paths follow the cmd rule | Same file or Python-side prompt; the macro never echoes text into a payload |
| `build.bat` | Script-derived root in a dedicated variable, scoped across `pre`, build and `post` with delayed expansion off; relative launcher call as described below | Python reads an existing file, `version.txt` or its console; arbitrary build-argument text is not forwarded or serialized by batch |
| Windows PowerShell 5.1 | Assign through the environment API and pass selectors to batch; scripts restore/remove in `finally`, prompt users assign in the launching command line | UTF-8 file or stdin, with no embedded-quote argument dependency |
| Python automation | Read the selected checkout's identity record and invoke its designated Python and trusted bootstrap through a native argument list | Native argument values, UTF-8 file or stdin; no intermediate batch parsing |
| Cross-checkout execution | Invoke the explicitly selected checkout's designated Python and trusted bootstrap through a native argument list | Original values as data without re-entering a batch file |

Every native route runs the same platform, readiness and project validation.
It never chooses another Python or skips the bootstrap. The approved requirement
amendment recognizes these routes and replaces arbitrary `build.bat rel_title...`
forwarding. Item 5 obtains titles and notes on the Python side from its console,
`version.txt`, or a user-authored UTF-8 file and preserves them in its validated
handoff. Batch cannot safely manufacture arbitrary text from its own arguments
into a file, pipe or variable.

For example, Python reads `Ready %PATH% & more` from UTF-8 file contents or its
console without batch echo or command substitution. Python automation can
instead supply native argument data. Piping a payload replaces console stdin,
so an interactive build uses a file or Python prompt when it needs to retain
the console. Invalid UTF-8 and stdin ownership remain transport proof cases.

### Launcher location, cleanup and transport evidence

Project data and the launcher's own location have separate contracts. Builds
use `pushd` to the selected launcher's directory, `call .\release_workflow.bat`
with command tokens and selectors, then `popd`. Stop if `pushd` fails; restore
cwd on normal and handled-error returns and preserve the command's saved public
status across cleanup. The `.\` prefix remains required when a host sets
`NoDefaultCurrentDirectoryInExePath`. Relative input-file paths resolve against
the validated project root, never this temporary tooling directory.

The alias surface never uses this `pushd` route because it needs the original
caller directory. Items 5 and 8 also apply the relative-call form to the build
template's existing `call <NUL "%build_dir%\senv.bat"`; that integration change
is outside item 1. The public launchers themselves do not change cwd before
Python captures it.

Scratch probes reached launcher locations containing `%`, `^` and `!` through
the relative-call form, where direct `call "<dir>\x.bat"` failed for `%` and
`^`. Windows PowerShell 5.1 reached batch locations containing `&`, `%` and
`^`. Later build probes preserved roots, status 7, environment and cwd across
20 metacharacter and non-ASCII combinations; 9 PowerShell combinations
preserved values but retained the selector variable. These are scratch-probe
results, not proof of the real launcher, all hosts, cancellation or the whole
release transport. Implementation must prove each supported caller, required
tooling location, decoding failure, stdin policy and hidden cancellation prompt.

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

Definitions stay with their domain owners inside llm-shared; this is not one
shared `.release.ini` for all projects. Exact module names remain for
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

For example, `[tooling] minimum-version = 0.15.0` in a consumer's `.release.ini`
requires llm-shared 0.15.0, not that consumer's release, Python or Git version.
Once comparison exists, an executing 0.14.0 checkout reports the update action
before rejecting settings introduced in 0.15.0. The check does not upgrade
tooling. During the interim, even an apparently older minimum returns status 2
with a compatibility-unavailable diagnostic. Malformed INI or invalid minimum
syntax always fails. Item 6 owns snapshot and candidate ordering, including
how `0.14.0-SNAPSHOT` relates to `0.14.0`; item 1 assumes no such ordering.

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

### Shared project operation lock

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

Process identity includes the process id and creation time to detect id reuse.
Elapsed time, the exited `pre` process, or the user's long-lived cmd process
alone cannot establish the operation's end. Item 5 validates handoff and transfer
under this contract; unrelated commands cannot adopt its operation identity.
This lock coordinates cooperating llm-shared commands, not arbitrary external
writers. Without it, a release updating `version.txt` and a version command
updating `pom.xml` could interleave despite every individual replacement being
atomic; separate domain locks would leave that same gap.

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

For example, `gv` from `C:\projects\B\src` discovers `C:\projects\B` and
passes that explicit root through validation. If inherited settings still
name A, the diagnostic identifies both roots while the operation targets B.

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

With console stdin and no explicit non-interactive request, Python may prompt.
With console stdin plus that request, a pipe, a file or `NUL`, missing required
input fails instead. All supplied inputs remain subject to normal validation
and authorization. Automation attached to a console should explicitly request
non-interactive mode: console detection identifies the channel, not whether a
person is available to answer. Non-interactive execution never invents consent.

## Acceptance cases for the release foundation

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
| Title includes batch metacharacters | Preserve its value through a supported free-text channel without command execution | AC10 |
| A handler fails after producing diagnostics | Return failure and keep diagnostics out of successful command data | AC10 |
| Missing launcher and release intent is not the first argument | Reject the transition; item 5 owns the build-lifecycle behavior | AC11 |
| Explicit-root surface is called without a root inside a worktree | Fail with status 2; do not infer alias mode | AC1, AC2 |
| `release_alias.bat` is called outside Git | Fail discovery without creating artifacts | AC2, AC9 |
| A managed parent becomes an external junction after preflight | Reject before temporary-file creation or final replacement outside the root | AC4 |
| A non-repository configuration source sets `core.worktree` | Fail before operations, identifying the setting's origin and scope | AC3 |
| Engine cwd at Git selection contains a planted `git.exe` | Never execute it; apply the executable-selection policy confirmed in Q11 A | AC3 |
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
test files, implementation steps and rollout checks from these settled decisions.
This consolidation supplies no implementation or full-suite validation evidence.

## File-based IO cost clarification for release-project-root

Read the selected runtime identity, tooling dependency metadata and project
declarations once per synchronous invocation and retain their validated forms in
memory. Do not scan old environments or unrelated consumer files, or prepare
artifacts during readiness, preflight or read-only work. Git identity/configuration
probes and managed-path ancestor checks are necessary validation; revalidate paths
at mutation boundaries and use same-parent temporary files for atomic replacement.
No document-index or event-loop mechanism is introduced, and no new wall-clock
target is implied. The implementation plan assigns read-count and scan-avoidance
checks to the owning steps.

## Design decisions

All recorded answers are integrated. No new blocking design question remains.
The question IDs preserve traceability to the pre-consolidation snapshot.

| Question | Decision and rationale | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | A: isolate inherited Git routing and command-scope injection for every subprocess while preserving compatible identity, signing and credentials; explicit-root calls remain usable from stale shells | [Project paths and Git execution](#project-paths-and-git-execution) | B: reject inherited inputs instead of isolating them, requiring callers to repair otherwise usable shells |
| Q02 | C: one setup-owned authoritative Python environment per llm-shared checkout, verified without release-time repair; setup's identity remains deterministic despite leftover environments | [Launcher and runtime](#launcher-responsibilities-and-authoritative-runtime) | A: require one ready candidate; B: rank ready candidates; both substitute discovery for setup's authority |
| Q03 | A: explicitly compose shipped domain-owned schemas and defaults, validating every declaration; projects may omit configuration when defaults suffice | [Common configuration](#common-configuration-with-domain-owned-validation) | B: one foundation-owned schema for all domains, coupling later domain changes to central definitions |
| Q04 | A: minimal batch frontend directly invokes designated Python; Q10's selected caller channels address the observed forwarding failures without an extra mandatory shell and still require implementation proof | [Launcher and runtime](#launcher-responsibilities-and-authoritative-runtime), [Caller channels](#caller-channels-and-value-preservation) | B: mandatory PowerShell intermediary, adding a parsing boundary and compatibility burden without solving transport by itself |
| Q05 | A: structured domain outcomes and one renderer for stdout results, stderr diagnostics and public statuses 0/1/2; preserve native failure identity and status | [Dispatch and results](#dispatch-and-result-interfaces) | B: domain-specific streams and status conventions, making callers handle inconsistent failure contracts |
| Q06 | A: common local Python functions authorize and revalidate managed writes after preflight; domains retain transactions and cleanup, with no hostile-race guarantee | [Artifact reuse and managed writes](#artifact-reuse-without-eager-side-effects) | B: repeated direct-write enforcement in each domain, risking omissions and stale path authorization |
| Q07 | A: separate alias entrypoint captures cwd and discovers the worktree through common Git handling, then passes an explicit root; standalone missing-root calls still fail | [Dispatch and results](#dispatch-and-result-interfaces) | B: discovery in each shell adapter, duplicating isolation and diagnostics |
| Q08 | A: setup publishes a versioned local runtime identity under ignored `venvs` after successful preparation; item 1 includes this narrow producer so it is independently usable | [Runtime identity](#setup-produced-runtime-identity) | B: reconstruct version/name rules; C: reorder item 6; D: run setup during release; E: require unique venv directories; these add coupling or change confirmed ownership and lifecycle rules |
| Q09 | A: declare and lock a release dependency group in llm-shared, included by dev; the standard-library bootstrap checks applicable direct/transitive versions and engine imports, failing unknown markers | [Dependency readiness](#release-dependency-readiness) | B: check all dev packages, allowing unrelated failures to block release; C: forbid third-party engine packages, constraining later domains |
| Q10 | A plus P1: explicit per-launch variable-name selectors carry paths; builds derive the root from their script; UTF-8 data and Python-side/native routes preserve free text and caller intent without repeated batch parsing | [Caller channels](#caller-channels-and-value-preservation) | B: universal escaping despite demonstrated failures; C: native binary shim outside scope; P2: restrict accepted paths; P3: payload-only paths leave locator and interactive build-root transport unresolved |
| Q11 | A: first eligible absolute PATH `git.exe`, excluding engine cwd, empty/relative entries and batch shims, with minimum 2.31.0 and one retained executable per operation | [Project paths and Git execution](#project-paths-and-git-execution) | B: setup-owned Git identity adds installation coupling; C: bare-name lookup permits the observed cwd substitution |
| Q12 | A: stable tooling minimum before strict domain validation gives the update remedy first; until item 6 supplies comparison, any declared minimum fails with status 2 | [Common configuration](#common-configuration-with-domain-owned-validation) | B: strict validation first obscures the update action; C: tolerate unknown keys, weakening validation |
| Q13 | A: one project operation lock across version, changelog and release mutations, held through handoffs and cleanup; conservative ownership-based recovery prevents cooperating commands from interleaving | [Project operation lock](#shared-project-operation-lock) | B: separate domain locks leave cross-domain overlap; C: an unenforced one-operation rule permits conflicting writes |
| Q14 | B: explicit non-interactive request or non-console stdin detected by `GetConsoleMode`, preserved in the validated handoff; missing input fails without prompts or assumed consent | [Dispatch and results](#dispatch-and-result-interfaces) | A: explicit flag only can hang redirected callers; C: inherited policy variable can carry stale intent across shells |
