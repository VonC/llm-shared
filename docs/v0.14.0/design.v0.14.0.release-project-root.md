# Design v0.14.0: explicit release project identity

Reference feature request:
[feature-request.v0.14.0.release-project-root.md](feature-request.v0.14.0.release-project-root.md).

## Context for the release-project-root design

Shared release tooling must operate on one explicitly validated project while
executing code and Python from the selected llm-shared checkout. The approved
requirement separates those identities, caller initialization and artifact
ownership before version, changelog and release-lifecycle behavior is added.

This document proposes the foundation's responsibilities and interfaces.
Q01 A, Q02 C and Q03 A are approved with the clarifications recorded below:
Git subprocesses isolate inherited routing, each llm-shared checkout supplies
one authoritative setup-managed Python environment, and domain-owned schemas
provide common configuration validation with defaults that require no project
configuration when suitable. Q04 through Q07 remain unanswered; their proposed
mechanisms are still subject to design review.
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

The proposed flow is:

```text
caller supplies explicit root or requests current-worktree alias dispatch
  -> self-locating launcher locates and verifies its setup-managed runtime
  -> Python dispatcher captures invocation data without preparing artifacts
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

The proposed invocation context carries:

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
verifying readiness, preserving the caller's arguments and returning the engine status.
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

The approved ownership model replaces the earlier proposal to discover or rank
ready environments at release time. The mechanism for locating setup's
authoritative environment remains design work coordinated with item 6;
choosing C does not prescribe a new selection-record file. Setup must expose
the authoritative identity so release tooling can locate and validate it.

Inherited Python import settings must not load a consumer's module in place of
the selected release engine. Startup and dependency checks must also preserve
the prohibition on writes to the consumer during failed preflight.

The exact Windows argument transport needs proof with spaces, quotes, `%`,
`!` and `&`. Do not treat a raw `%*` expansion, delayed expansion or an extra
`call` layer as proof of preservation. Python dispatch works with an argument
vector after capture; values are never interpolated into executable command
text. The later transaction handoff remains item 5's design responsibility.

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

Q03 concerns ownership of definitions inside llm-shared. The alternative B
would have put every domain's rules and defaults in one foundation-owned Python
module in that same repository. Both choices use the same optional per-project
configuration file; neither introduces a shared `.release.ini` for all projects.
A keeps the rules with their domain owners. Exact module names remain for
implementation planning.

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

This design reuses the existing artifact policy rather than copying its parser.
It does not modify review-exchange behavior. Per-operation temporary names,
cleanup and transaction ownership remain with the domains that generate them;
the shared git-cliff cache remains item 3's distinct write area.

## Dispatch and result interfaces

The proposed Python dispatcher owns command routing and the distinction between
explicit-root calls and current-worktree alias requests. Shell adapters provide
the invocation data and execute the selected project build when required; they
do not duplicate root validation or configuration semantics. Alias installation
and concrete consumer integration remain items 6 and 8.

Future domain handlers receive the fixed context and return a structured
outcome containing success/failure, result data and diagnostics. The public CLI
renders command data on stdout and warnings/errors on stderr. This allows a
stale-environment warning without corrupting a version result. Domains retain
ownership of their data format and of build/recovery detail.

The alternative is to preserve domain CLI streams and status directly behind
the common preflight. Review must settle the outcome interface and exit-status
categories before implementation. Failure must never become success under
either approach, and item 5 must retain the original build failure in
diagnostics if postprocessing also fails.

The missing-launcher exception is evaluated by the consuming build adapter:
ordinary build intent may proceed with its warning and read-only version
display; release or snapshot intent anywhere among arguments must fail.
An installed handler must not use this exception to hide an execution failure.
The actual lifecycle handling and build invocation belong to item 5.

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

The approved whole-suite scope applies to later validation. Plans will assign
test files, implementation steps and rollout checks after design decisions are
settled.

## Open questions for the v0.14.0 release-project-root design

These questions concern design choices only. The requirement remains settled.
Q01 A, Q02 C and Q03 A are confirmed with the clarifications in their answers.
Q04 through Q07 remain unanswered; their answer lines are proposals, not human
approval. Recommendations retain the original review proposals, including Q02's
recommendation of A before the user chose C. All questions and options remain
here until explicit consolidation, after an intermediate question snapshot
commit preserves them in Git.

### Q01: How should the Git adapter isolate inherited routing settings?

The root must remain authoritative even when inherited Git settings redirect
the repository, worktree or index. The adapter must address environment-based
configuration injection as well as named routing variables. Ordinary signing,
identity and credential configuration should remain usable when it cannot
redirect the target. Which isolation policy should the foundation provide?

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

### Q02: How should the launcher select a ready bundled runtime?

The executing checkout's declared Python and dependency requirements determine
readiness. Existing launchers disagree on directory-name versus modification-
time selection. The new launcher must not use those heuristics as readiness
checks. Which rule should select among this checkout's candidate environments?

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

### Q03: Who should own the common configuration schema?

The common reader must reject malformed, conflicting or unknown declarations
before mutation, while later items own version, changelog and setup behavior.
How should their settings become part of one complete validation pass?

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

### Q04: Which launcher layer should own Windows argument transport?

The public batch entrypoint must preserve the argument values supplied under
the supported caller syntax, including spaces, quotes and metacharacters. The
design currently leaves the launch boundary between the shell and the Python
argument vector implicit. Which frontend structure should the design pursue?
Neither choice relaxes the argument-preservation requirement.

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

Proposed answer: accept a minimal direct bootstrap because it minimizes places
where values can become command text. Acceptance remains conditional on the
required argument-preservation evidence, not confidence in batch syntax.

### Q05: How should domains report results and failures?

The requirement separates machine-consumed results from diagnostics and keeps
failures visible through launchers. Should domains return a common outcome to
one renderer, or directly own their CLI streams and status?

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

Proposed answer: accept structured outcomes and the three common status values
because they make launcher behavior predictable without choosing later domains'
data formats or transaction rules.

### Q06: Where should managed writes be authorized and revalidated?

The design separates read-only configuration and artifact resolution from
preparation, and requires physical path checks again before writes. How should
domains receive that capability without treating the initial root check as
permanent authorization for any later destination?

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

Proposed answer: accept the separate managed-write capability because it makes
the approved no-artifact-side-effects rule easier to preserve across domains.
The plan must establish the guarantees of its filesystem operations rather than
claiming a path recheck alone provides atomic protection against every race.

### Q07: Where should current-directory alias resolution live?

Aliases discover the current worktree and pass an explicit root; engine and
standalone commands must never infer a missing root. The proposed dispatcher
mentions both invocation origins without defining the boundary. How should the
foundation share alias discovery while keeping its engine API explicit?

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

Proposed answer: accept the separate facade because it centralizes discovery
without weakening the approved explicit-root contract or moving installation
work into this child.
