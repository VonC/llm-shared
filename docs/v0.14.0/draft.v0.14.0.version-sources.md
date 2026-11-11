# Synchronize authoritative project versions

- Type: feature-request
- Test group: whole suite
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Target version: v0.14.0
- Documentation layout: docs/v0.14.0/
- Slug: version-sources

## Selected umbrella entry for version sources

| Order | Type | Key title | Slug | Status | Requirement | Validation plan |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | Feature-request | Synchronize authoritative project versions | `version-sources` | pending | - | - |

### Requirement detail inherited for version sources

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
    These are llm-shared's own development tests, run while llm-shared is
    changed; a consumer's `brel` or release never runs them, and release-time
    testing of a consumer stays with item 5.
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

## Context and scope of version sources

A version lives in more places than `version.txt`. dev_workflow knows two
(`pom.xml`, `package.json`). `/prepare-release` Step 12 already describes more,
each in its own form: `pyproject.toml` and `uv.lock` without the suffix,
`package.json` and `package-lock.json` in the release form (a VS Code
extension version supports only `major.minor.patch` on the Marketplace), Maven
POMs and their module parents with `-SNAPSHOT`, and a `cicd/config/.env`
variable. my-project's `tools/set_version.py` and `tools/check_versions.py`
implement that list for one repository. The engine should implement it once,
for every repository, and leave room for formats nobody needs yet.

Item 1, `release-project-root`, is completed and merged. It supplies the
foundation this item builds on: an explicit validated project root, root-scoped
Git, the common `.release.ini` reader with explicitly registered domain
schemas, guarded managed writes inside the selected worktree, the per-project
operation lock, and command dispatch through `bin/release_workflow.bat`. This
item adds the version domain to that engine under `tools/release_workflow/`.

This item owns version reading, source detection and synchronization, form
mapping, the version-source settings, the reusable atomic transition and
restoration of the source set, and the shared stable/snapshot tag classifier
and range selector. It does not own:

| Behavior outside version sources | Owning umbrella item |
| --- | --- |
| Changelog rendering, archives and fix rules | 4, `changelog-management` |
| git-cliff download, cache and pin | 3, `git-cliff-provisioning` |
| Release and next-snapshot commits, tags, `[valid]`, gate and recovery | 5, `build-release-lifecycle` |
| Detecting and recording participating components in a consumer's setup | 6, `release-tooling-setup` |
| `/prepare-release` Step 12 and range-reader adoption | 7, `prepare-release-integration` |
| llm-shared's own cutover | 8, `llm-shared-cutover` |

## Version notation used for version sources

| Context | Form | Example |
| --- | --- | --- |
| `version.txt` first token, version-setting arguments, config bounds | `X.Y.Z` or `X.Y.Z-SNAPSHOT`, without `v` | `0.14.0-SNAPSHOT` |
| Python metadata/uv root and default npm manifest/lock | `X.Y.Z`, even during snapshots | `0.14.0` |
| Maven and configured snapshot sources | Same suffix state as the anchor, without `v` | `0.14.0-SNAPSHOT` |
| New release Git tag, generated release heading, release commit subject | `vX.Y.Z` | `v0.14.0` |
| Existing optional snapshot Git tag | `vX.Y.Z-SNAPSHOT`; also recognize legacy unprefixed spelling | `v0.14.0-SNAPSHOT` |
| Draft target labels, effort paths, archive filenames | `vX.Y.Z` | `docs/v0.14.0/`, `CHANGELOG.v0.1.0-v0.13.9.md` |

Legacy unprefixed stable tags remain readable; new stable tags always have `v`.
A CLI argument selecting a tag uses its actual tag spelling; an argument setting
a project version never includes `v`.

## The version.txt anchor and the read command

`version.txt` is authoritative (umbrella decision 13). Its first
whitespace-separated token is the project version; the rest of the first line,
after `--`, is the title, and the following lines are the release notes.

- The **current-version read** is read-only and returns the version, title and
  notes from `version.txt`. A missing or malformed file gives an actionable
  error, rather than silently creating `0.1.0-SNAPSHOT` as dev_workflow's
  `get-version.bat` does today.
- A version transition replaces only the first token and preserves the title,
  the release-notes body and every other byte. Title and notes never change as
  a side effect of synchronization.
- Every other source takes its value from the anchor's first token, never from
  its own current value.

## One module per version format

Each format is one module in llm-shared's `tools/release_workflow/sources/`
package (`maven.py`, `npm.py`, `pyproject.py`, ...), exposing one object that
follows a small protocol. The umbrella's sketch, for illustration only (the
design settles the actual interface):

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
  lists each format object in one explicit tuple (umbrella decision 5). Adding
  a format is one module and one line in that tuple. The tuple gives a
  deterministic detector order, and pyright and vulture see every format in
  use. A test lists the modules of the package and fails when one is missing
  from the tuple, so a new format cannot be written and then silently left out;
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

## Detecting every participating ecosystem

Run every registered detector and combine their results; selecting Python does
not suppress npm or Maven (umbrella decision 14). A project with root
`pyproject.toml`, `uv.lock`, `package.json` and `package-lock.json` updates all
four from one anchor. A Node component under `frontend/` is included when
declared as a participating component root in `.release.ini`; do not mistake
every sample/package manifest for the project's release. Setup (item 6)
detects candidate component roots and records their participation, so later
version transitions need no repeated choices. This item's design must settle
the declaration syntax. Conflicting claims on one file fail before writes rather
than being silently resolved by detector order.

Detection follows project nature, not every matching file in the tree:
identify the Python project by its declared name and local/virtual source in
`uv.lock`, the npm root by its manifest, and the Maven reactor through its
root POM's declared modules. Detection skips `node_modules`, `venvs`, `.venv`,
`.git`, `.reviews` and `target`, and excludes vendor/sample projects and
nested Git repositories. Independent workspace packages need explicit
configuration rather than accidental synchronization. Dynamic Python versions,
ambiguous lock roots or unsupported Maven property indirection fail with the
exact source and configuration remedy; never guess.

## Version forms per format

| Form | Snapshot `1.2.3-SNAPSHOT` becomes | Release `1.2.3` becomes | Used by default for |
| --- | --- | --- | --- |
| `snapshot` | `1.2.3-SNAPSHOT` | `1.2.3` | Maven POMs, the `.env` variable |
| `core` | `1.2.3` | `1.2.3` | `pyproject.toml`, `uv.lock` |
| `release-only` | `1.2.3` | `1.2.3` | `package.json`, `package-lock.json`; no prerelease suffix by default |

`core` and `release-only` give the same strings. They differ in their guard: a
`release-only` source refuses a value lower than the one it states already,
since lowering a published extension version would rewind it, as Step 12 of
`/prepare-release` already requires.

Both forms synchronize to the current anchor's core during a snapshot. They do
not retain the previous published value: with `version.txt` at
`0.0.25-SNAPSHOT`, npm sources become `0.0.25` already (umbrella decision 15).
Maven and the configured `.env` source use `0.0.25-SNAPSHOT`; Python cannot
accept that Maven-style suffix (umbrella decision 6). An npm project can
explicitly select `snapshot` when its packaging accepts that SemVer prerelease,
but VS Code Marketplace consumers use `release-only`. Unsupported form/format
combinations fail before writes.

## Supported formats in v0.14.0 and later candidates

- Explicitly supported first set, because the three repositories and Step 12
  need them: `version.txt`, `pyproject.toml` (`[project].version`), `uv.lock`
  (the virtual root package), `package.json` with `package-lock.json` (the
  top-level `version` and `packages[""].version`, no external dependency entry
  touched), Maven `pom.xml` with its module parents.
- A generic `pattern` source, declared by a project, for the one-off files: a
  path, a regular expression with one group, and a form. my-project's
  `cicd/config/.env` becomes one line of project configuration, instead of a
  case every repository's release carries. A configured pattern source must
  match exactly one version capture in its declared file.
- Future candidates only, not promised support in v0.14.0: `Cargo.toml`,
  `gradle.properties` and `build.gradle(.kts)`, `*.csproj` or
  `Directory.Build.props`, Helm `Chart.yaml` (`version` and `appVersion`),
  `composer.json`, `pubspec.yaml`, `mix.exs`, a `__version__` in a Python
  package `__init__.py`.

## Writing only the version, including locks

For a single-component Python project, update `[project].version` and only the
corresponding local root package version in `uv.lock`, leaving lock schema
`version`, dependency versions, hashes, URLs and resolver metadata unchanged.
For a single-component npm project, update only the root manifest `version`,
lock top-level `version` and `packages[""].version` where present for that lock
format. Maven updates the reactor's project versions and internal module-parent
references (the plugin reads the `<modules>` of the root POM and updates each
module's `<parent>` version); inherited versions remain inherited and external
parent/dependency/plugin versions stay unchanged. Handle supported reactor
version properties explicitly or reject them with an actionable error. Each
adapter validates its complete write set before changing any file and preserves
unrelated content, formatting and line endings; no global replacement of every
field named `version`.

The supported lock entries can be edited directly for a version-only change; do
not run `uv lock` or npm dependency resolution opportunistically merely because
a tool is present. If an explicitly supported format needs regeneration,
require its tool and limit/validate its changes; if consistency cannot be
maintained safely, fail before mutation rather than produce a best-effort lock.

Lock consistency is judged by comparing two states of the same manifest and
lock pair. The "before" pair is the two files as the project has them before
`versions set` changes the version, for example `pyproject.toml` and `uv.lock`
both at `0.13.0`; the edited pair is the same files after the version-only
edit, both at `0.14.0` with every other byte unchanged. When the tool's locked
check (such as `uv lock --locked`) accepted the "before" pair without changing
it, it must accept the edited pair the same way. A lock that was already stale
before `set` is neither detected nor repaired (feature-request clarification
Q10).

## Internal references between participating components

Synchronization must also account for version references between participating
components (umbrella decision 39). For example, changing Maven module A's
version while module B still depends on its old version is not a consistent
reactor transition. The same contract applies to supported participating
workspace packages and their manifests/locks. Update internal references
supported by the adapter; reject unsupported or ambiguous arrangements before
any writes, naming the affected components and the limitation. External
dependency versions remain unchanged. This does not promise every workspace
format: the requirement must state the supported boundary and the design
chooses how references are identified and changed. No successful transition
may knowingly leave stale internal references within that supported boundary.

## The versions list, check and set commands

- `versions <root> list` prints each detected file with its kind, form and
  current value, so a user sees what a release will touch before it does.
- `versions <root> check` reports actual and expected values and exits nonzero
  on drift.
- `versions <root> set <version>` updates the anchor token and all applicable
  sources as one recoverable operation, with the target as its proposed
  authoritative value. Failed writes restore the whole original set, including
  lock entries and the absence of files that did not exist before.

Snapshot and release transitions (item 5) reuse this same operation; this item
provides the transition and restoration primitive, not the commit or tag around
it. `version`, `versions list|set|check` and `snapshot` need no git-cliff.

## Version-source settings in .release.ini

Version-source settings belong to version management (item 1's schema
registry gives each domain its own section ownership). A project without
`.release.ini`, or without these sections, gets the built-in detection and
default forms. The umbrella's examples:

```ini
[source:npm]
; override the default form of a built-in format
form = release-only

[source:cicd-env]
; a project-specific file, one regex group holding the version
file = cicd/config/.env
pattern = ^APP_SERVICE_VERSION=(.+)$
form = snapshot
```

The file is read with interpolation off, so `%` and `$` in a pattern need no
escaping. The common reader validates forms, paths and unknown keys before
mutation, including declarations unused by the current command. No consumer
runs code from project config. The participating component-root declaration
syntax is this item's design work.

## Stable and snapshot tag classification

Recognize stable tags only by the complete `vX.Y.Z` or legacy `X.Y.Z` form.
Recognize `vX.Y.Z-SNAPSHOT` and `X.Y.Z-SNAPSHOT` separately as development
markers, including historical case variants of the suffix. Other prereleases
are not stable releases either. This effort supports existing snapshot tags;
it does not automatically create, move or delete them on snapshot transitions.

One shared tag classifier/range selector serves the engine, git-cliff input,
release-notes collection and release-plan/documentation ranges (umbrella
decision 26). Select a reachable eligible stable release as the baseline,
excluding snapshot tags even when they point at HEAD. New engine tags require
`[valid]` to become release baselines; retain support for historical stable
releases without that marker, while excluding a tag recorded as an active
unvalidated transaction. The distinction between a historical release and a
new unvalidated release must remain available in another clone and when local
transaction evidence is absent (umbrella decision 34). Missing evidence never
promotes an unfinished new release into a historical exception. Ambiguous
validity must be reported and must not silently establish a baseline. The
persistent evidence and migration mechanism are design decisions; local
journals alone cannot define tag eligibility. Use a documented deterministic
ancestry rule, and report conflicting tags rather than guessing. With no
eligible stable tag, use the full relevant history.

Do not split `git describe` output on `-` to find a commit count: the snapshot
suffix is part of the version. Query the chosen ref and its commit distance
explicitly. Neither a release-notes nor a release-plan reader may use an
unfiltered "last tag" query; item 4 configures git-cliff with this selector and
item 7 switches those readers to it.

Example: after stable `v0.13.0`, commits A and B surround `v0.14.0-SNAPSHOT`.
Preparing `0.14.0` includes A and B from `v0.13.0..HEAD`, even when HEAD itself
has the snapshot tag. The release that creates a distinct `v0.14.0`, and the
recovery that may remove only its own unvalidated tag, belong to item 5.

## Release version uniqueness and order

Existing `X.Y.Z` and `vX.Y.Z` tags both reserve the same release version
(umbrella decision 33). The target version must be higher than every eligible
reachable stable release on main (confirmed answer Q2 A). Lower maintenance
releases require a later, separate policy. With no eligible stable release,
retain the existing full-relevant-history behavior. This item states and exposes
that rule; the release lifecycle (item 5) and preparation (item 7) enforce it
in their preflights.

## Callers of the version-source operations

These callers reuse the shared detection, form mapping and atomic
synchronization; each receives the full set of participating sources. Their
adoption belongs to the named items.

- `brel` (`pre`, release mode, item 5): changes the anchor to `X.Y.Z` and maps
  each source to its release form. Python/default npm already have that core;
  snapshot-form sources lose the suffix. Each changed file joins the commit.
- The next-snapshot step after a release (item 5): raises every source to the
  chosen `X.Y.Z-SNAPSHOT` in its form, in the same commit as `version.txt`.
- `/prepare-release` Step 12 (item 7): `versions <root> set X.Y.Z-SNAPSHOT`
  then `versions <root> check`, in place of the per-format instructions it
  carries today.
- A project `check.bat`: `versions <root> check`, in place of a project
  `check_versions.py`.

## dev_workflow version defects to fix rather than port

- `update-version.bat` lines 353 and 361, in `:restore-version`, use
  `%update_version_dir%` while the script defines `update-version_dir`: the POM
  and `package.json` restore calls resolve to `\t_build_maven.bat` and
  `\t_build_npm.bat` and never run. The new restoration covers the complete
  source set.
- `t_build_npm.bat` line 89 rewrites every `"version": "..."` line of
  `package.json`, not only the top-level one, and leaves `package-lock.json`
  behind.
- The npm path requires `package.json` to carry `-SNAPSHOT` before a release
  (`check-snapshot`), the opposite of the release-only form a VS Code extension
  needs: workspace-halo's release would stop there.
- Lines 435 and 437 of `update-version.bat` compare `"%git_tag%"==v"%version%"`:
  the quotes differ on each side, so the "already released" guards can never
  match. This item supplies the uniqueness rule above; item 5 applies it.

## Consumer inputs for version sources

These repositories shape the supported set. Their own migrations stay in their
own efforts; llm-shared's belongs to item 8.

- llm-shared: `version.txt`, `pyproject.toml` and `uv.lock`, plain `X.Y.Z`
  during the snapshot, as Step 12 does today.
- my-project: the built-in plugins cover `version.txt`, `pyproject.toml`,
  `uv.lock`, `pom.xml` and `PDF/pom.xml`; `cicd/config/.env` becomes one
  `pattern` source. `tools/set_version.py` and `tools/check_versions.py` can
  then retire, and `check.bat` calls `versions check`. Today only
  `version.txt` and `pom.xml` follow a `brel`, and `check.bat` catches the
  drift afterwards. Its `publish_pdf_nexus*.sh` version menus must exclude
  snapshot tags, using this item's shared tag policy as their contract.
- workspace-halo: `package.json` and `package-lock.json` use the `release-only`
  form, synchronizing to `0.0.25` while `version.txt` reads `0.0.25-SNAPSHOT`
  and remaining `0.0.25` at release. Never insert `-SNAPSHOT` into the VSIX
  version. Its tags mix `0.0.21`, `0.0.22` and `v0.0.20`, `v0.0.23`, `v0.0.24`;
  range selection must not trip on the older unprefixed tags.
