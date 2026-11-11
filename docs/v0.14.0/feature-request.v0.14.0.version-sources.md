# Synchronize authoritative project versions

- Type: feature-request
- Test group: whole suite
- Target version: v0.14.0
- Slug: version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md

## Draft basis and user need for version sources

As a maintainer releasing projects that state their version in several files
and ecosystems, I need one shared engine to read the authoritative version from
`version.txt`, find every participating version source, give each the form its
ecosystem expects and change them all together, so no release publishes an
artifact under a version that another file of the same project does not name.

The [focused draft](draft.v0.14.0.version-sources.md) derives from item 2 of
the [sibling release tooling umbrella](draft.v0.14.0.sibling_release_tooling.md)
and was approved on 2026-11-03. It gathers the umbrella contracts on version
authority, adapters, detection, forms, locks, internal references, the
version-source settings, version notation and stable/snapshot tag
classification. This requirement records those outcomes without choosing their
implementation.

## Current behavior before the version-sources engine

- dev_workflow knows two secondary sources. `t_build_maven.bat` with
  `mvn_get_version.ps1` gets, sets and checks `pom.xml`; `t_build_npm.bat`
  does the same for `package.json`. `get-version.bat` parses the first line of
  `version.txt` and, when the file is missing, writes `0.1.0-SNAPSHOT` into it.
- `/prepare-release` Step 12 describes the other sources by hand, one format at
  a time: `pyproject.toml` and `package.json` at the release `X.Y.Z`, Maven
  POMs and module parents and `cicd/config/.env` at `X.Y.Z-SNAPSHOT`. It
  regenerates `uv.lock` with `uv sync` and updates `package-lock.json` through
  `npm version`, then relies on a project `tools/check_versions.py` when one
  exists.
- my-project implements that list for itself in `tools/set_version.py` and
  `tools/check_versions.py`. After a `brel`, only `version.txt` and `pom.xml`
  follow; its `check.bat` reports the remaining drift afterwards.
- workspace-halo has no `brel` step, so its `-SNAPSHOT` drop is done by hand.
  Its tags mix unprefixed `0.0.21`, `0.0.22` with `v0.0.20`, `v0.0.23`,
  `v0.0.24`.
- Item 1, `release-project-root`, is completed and merged. It supplies the
  explicit validated project root, root-scoped Git, the common `.release.ini`
  reader with its schema registry, guarded managed writes, the per-project
  operation lock and dispatch through `bin/release_workflow.bat`. It ships no
  release operation yet: every command, including `version` and `versions`,
  reports that it is unavailable in this tooling checkout, and the registry
  holds only the tooling settings domain.

## Scope and ownership boundaries of version sources

This item owns version reading, source detection and synchronization, form
mapping, the version-source settings, the reusable atomic transition and
restoration of the source set, and the shared stable/snapshot tag classifier
and range selector. It adds the version domain to the engine under
`tools/release_workflow/`, behind the dispatch and configuration boundaries
item 1 established.

It provides the transition and restoration primitive, not the commits or tags
around it. The neighboring behaviors stay with their items:

| Umbrella item | Behavior owned by that item |
| --- | --- |
| 3, git-cliff-provisioning | git-cliff download, cache and pin |
| 4, changelog-management | Changelog rendering, archives, fix rules and git-cliff range configuration |
| 5, build-release-lifecycle | Release and next-snapshot commits, tags, `[valid]`, build gate, recovery, and enforcement of the uniqueness rule in its preflight |
| 6, release-tooling-setup | Detecting and recording participating components in a consumer's setup |
| 7, prepare-release-integration | `/prepare-release` Step 12 adoption and switching release-notes and release-plan readers to the shared selector |
| 8, llm-shared-cutover | llm-shared's own migration |

Interfaces, module layout, detection algorithms, the persistent tag-eligibility
mechanism, the representation of lock ownership, the storage and retention of
recovery evidence, the lock-compatibility evidence, exact output formats and
exit-code numbers remain design work.

## Version notation for version sources

| Context | Form | Example |
| --- | --- | --- |
| `version.txt` first token, version-setting arguments, config bounds | `X.Y.Z` or `X.Y.Z-SNAPSHOT`, without `v` | `0.14.0-SNAPSHOT` |
| Python metadata/uv root and default npm manifest/lock | `X.Y.Z`, even during snapshots | `0.14.0` |
| Maven and configured snapshot sources | Same suffix state as the anchor, without `v` | `0.14.0-SNAPSHOT` |
| New release Git tag, generated release heading, release commit subject | `vX.Y.Z` | `v0.14.0` |
| Existing optional snapshot Git tag | `vX.Y.Z-SNAPSHOT`; also recognize legacy unprefixed spelling | `v0.14.0-SNAPSHOT` |
| Draft target labels, effort paths, archive filenames | `vX.Y.Z` | `docs/v0.14.0/`, `CHANGELOG.v0.1.0-v0.13.9.md` |

Legacy unprefixed stable tags remain readable; new stable tags always have `v`.
A CLI argument selecting a tag uses its actual tag spelling. An argument setting
a project version never includes `v`.

## The version.txt anchor and its read-only access

`version.txt` is authoritative (umbrella decision 13). Its first
whitespace-separated token is the project version; the rest of the first line,
after `--`, is the title, and the following lines are the release notes.

- The token is well formed only when it is exactly `X.Y.Z` or
  `X.Y.Z-SNAPSHOT`: non-negative integers without leading zeros, the uppercase
  `-SNAPSHOT` suffix and no `v` prefix. Any other token, such as `v0.14.0`,
  `0.14.0-snapshot`, `0.14.0-rc1` or `0.014.0`, is malformed. This rule covers
  the anchor only; recognizing historical tag spellings is the separate tag
  classification contract below.
- The title and notes may be empty for `version` and `versions`, so a fresh
  project holding only `0.1.0-SNAPSHOT` can run every version command. Item 5
  requires them for a release.
- The current-version read returns the version, title and notes and changes
  nothing. A missing or malformed `version.txt` gives an actionable error; it
  is never created or initialized, unlike dev_workflow's `0.1.0-SNAPSHOT`
  fallback. Like every read-only command, it prepares no project artifact.
- A version transition replaces only that first token and preserves the title,
  the release-notes body and every other byte. Synchronization never changes
  title or notes as a side effect.
- Every other source takes its value from the anchor's first token, never from
  its own current value.

## Registered version-source adapters

Each supported format is one adapter in llm-shared's
`tools/release_workflow/sources/` package. The umbrella sketches its protocol
as a name plus `detect`, `read`, `expected` and `write` operations, where
`write` changes only the version and leaves every other byte in place. That
sketch is inherited context; the design settles the actual interface.

Two separate questions are answered in two separate ways:

- Which formats the engine knows: `tools/release_workflow/sources/__init__.py`
  lists every adapter in one explicit tuple (umbrella decision 5). That tuple
  gives a deterministic detector order and keeps every format visible to
  pyright and vulture. A completeness test lists the package's modules and
  fails when one is missing from the tuple.
- Which files a project holds: each adapter detects its own files under the
  project root, so a project gains a format the day llm-shared ships it, with
  nothing to declare for an unambiguous project root. Independently nested
  components follow the explicit participation rule below.

The package and its tuple live only in llm-shared, never in a consumer. Adding a
format means adding its module, registering it and adding its detection, read,
expected-form, write and failure-restoration tests. It needs no change to
the release lifecycle code and no copied consumer code. Project-specific text
files use the declarative pattern source. Executable project-local plugins are
outside this effort and would need a separate contract.

## Participation and detection of ecosystems

Run every registered detector and combine their results (umbrella decision 14).
Selecting Python does not suppress npm or Maven: a project with root
`pyproject.toml`, `uv.lock`, `package.json` and `package-lock.json` updates all
four from one anchor.

A component in a nested directory, such as a Node application under
`frontend/`, participates only when `.release.ini` declares it as a
participating component root. Sample, example and package manifests elsewhere
in the tree are not the project's release. Item 6's setup detects candidate
component roots and records their participation, so later transitions need no
repeated choice; this item defines the declaration syntax in its design.
Conflicting claims on one file fail before any write rather than being resolved
by detector order.

An undeclared nested candidate, such as an undeclared `frontend/package.json`,
stays visible without participating: `versions list` reports it with its path
and a not-participating status, while `check` and `set` ignore it and do not
fail. Candidates obey the same exclusions as detection, so skipped directories,
vendor and sample projects and nested Git repositories are never reported.

The project has one version. Every participating component takes the anchor's
version in its form. An independently released package is simply not declared:
it is never touched, and references to it follow the external-version rule and
stay unchanged, without implying that they are valid. Per-component versions,
several anchors and fixed component versions are out of scope for v0.14.0.

Detection follows the project's nature, not every matching file:

- Python: the project identified by its declared name and its local or virtual
  root entry in `uv.lock`.
- npm: the root manifest and its lock.
- Maven: the reactor reached through the root POM's declared modules.
- Never inside `node_modules`, `venvs`, `.venv`, `.git`, `.reviews` or
  `target`, vendor or sample projects, or nested Git repositories.

A root manifest kept only for tool settings is not a version source: a
`pyproject.toml` without a `[project]` table, or a root `package.json` without
a `version` field. Its lock is excluded with it and never participates on its
own; `list` shows the pair as not participating, and `set` and `check` ignore
it. A `[project]` table with a dynamic or missing version still fails, and so
does a present manifest that cannot be parsed. Dynamic Python versions,
ambiguous lock roots and unsupported Maven property indirection fail with the
exact source and the configuration remedy; the engine never guesses.

Lock files are checked after this participation filtering, at the project root
and at each declared component root only. An absent optional lock does not
participate and is never generated. An existing lock must pair with an
identifiable participating manifest and use a supported, unambiguous schema;
otherwise `list`, `check` and `set` fail before any source write. An orphan or
unsupported lock inside an undeclared nested candidate does not count, since
the candidate does not participate.

## Version forms and their guards

| Form | Snapshot `1.2.3-SNAPSHOT` becomes | Release `1.2.3` becomes | Default for |
| --- | --- | --- | --- |
| `snapshot` | `1.2.3-SNAPSHOT` | `1.2.3` | Maven POMs, the configured `.env` variable |
| `core` | `1.2.3` | `1.2.3` | `pyproject.toml`, `uv.lock` |
| `release-only` | `1.2.3` | `1.2.3` | `package.json`, `package-lock.json` |

`core` and `release-only` produce the same strings and differ in their guard:
a `release-only` source refuses a value lower than the one it already states,
because lowering a published extension version would rewind it. That refusal
fails the whole transition before any write, naming the source, its value and
the target; no source is skipped. `versions check` reports a source ahead of
the anchor as drift, with a nonzero exit. There is no downgrade override in
v0.14.0: a deliberate downgrade needs a manual edit. Every version comparison,
in this guard and in the exposed ordering rule, is numeric per component, so
`0.10.0` is higher than `0.9.0`.

Both forms follow the current anchor's core during a snapshot and never keep
the previous published value (umbrella decision 15). With `version.txt` at
`0.0.25-SNAPSHOT`, npm sources already state `0.0.25`. Python cannot accept the
Maven-style suffix (umbrella decision 6), while Maven and configured snapshot
sources state `0.0.25-SNAPSHOT`. An npm project may select `snapshot` explicitly
when its packaging accepts that SemVer prerelease; VS Code Marketplace
consumers keep `release-only`. An unsupported form and format combination fails
before any write.

## Supported formats for v0.14.0 and later candidates

The supported first set, needed by the three repositories and Step 12:

- `version.txt`, the anchor.
- `pyproject.toml`, `[project].version`.
- `uv.lock`, the local virtual root package entry.
- `package.json` with `package-lock.json`: the top-level `version` and
  `packages[""].version`, with no external dependency entry touched.
- Maven `pom.xml` with its internal module parents.
- A generic `pattern` source declared by the project: a file path, a regular
  expression with one capture group and a form, all three required, with no
  default form. The declared file must exist and is never created. The pattern
  must produce exactly one successful match whose capture group holds a
  nonempty version: zero matches, several matches or an optional group with no
  value fail `list`, `check` and `set` before any write, with an actionable
  diagnostic. my-project's `cicd/config/.env` becomes one such declaration.

Later candidates, not promised in v0.14.0: `Cargo.toml`, `gradle.properties`
and `build.gradle(.kts)`, `*.csproj` or `Directory.Build.props`, Helm
`Chart.yaml` (`version` and `appVersion`), `composer.json`, `pubspec.yaml`,
`mix.exs` and a `__version__` in a Python package `__init__.py`. They remain
unsupported until their adapters are added.

## Version-only writes, locks and internal references

Each adapter changes only the version it owns:

- Python: `[project].version` and the corresponding local root package version
  in `uv.lock`. The lock schema `version`, dependency versions, hashes, URLs and
  resolver metadata stay unchanged.
- npm: the root manifest `version`, the lock's top-level `version` and
  `packages[""].version` where that lock format has them.
- Maven: the reactor's project versions, the internal `<parent>` version of
  each module and the literal version of each internal dependency or
  dependency-management entry, for the modules declared in the root POM's
  `<modules>` and, recursively, by participating modules. Project versions
  remain literal or inherited as applicable; explicit internal `<parent>`
  version fields remain literal. The one accepted property expression is
  `${project.version}` as the entire version of an internal dependency or
  dependency-management entry: it stays unchanged and follows the shared
  project version, since every participating module takes the same version.
  Any other expression in these fields, including `${revision}`, composite
  expressions and project-defined properties, and any version range, fails
  before any source write, naming the file, the field, the expression and the
  limitation. External parent, dependency and plugin versions and properties
  stay unchanged.

Each adapter validates its complete write set before changing any file, and
preserves unrelated content, formatting and line endings. No field named
`version` is replaced globally. Supported lock entries are edited directly for
a version-only change: `uv lock`, `uv sync` or npm dependency resolution never
run merely because a tool is present. If a supported format ever needs
regeneration, the engine requires its tool and limits and validates its
changes; when consistency cannot be kept safely, it fails before mutation
instead of producing a best-effort lock.

An edited lock counts as consistent by the result consumers rely on. For a
supported format and tool version, and a manifest and lock pair that the tool
accepted as current before the transition, the version-only edit keeps that
acceptance, so a later locked install neither rewrites nor rejects the lock.
This does not promise to repair dependency drift that existed before, a
changed resolver environment or every future tool version. An ordinary `set`
never runs these tools to check its result; the design and plans choose the
compatibility evidence.

In this guarantee, the "before" pair is a manifest and its lock file as the
project has them before `versions set` changes the version: for example a
`pyproject.toml` and its `uv.lock`, both at `0.13.0`. The edited pair is the
same two files after the version-only edit, both at `0.14.0` with every other
byte unchanged. "Accepted as current" means the tool's locked or frozen check
(such as `uv lock --locked`) succeeds and changes neither file. The promise is
relative: when the "before" pair was accepted, the edited pair is accepted
too; a lock that was already stale before `set` is neither detected nor
repaired.

Synchronization also covers version references between participating
components (umbrella decision 39). Changing Maven module A while module B still
depends on A's old version is not a consistent reactor transition. This
requirement states the supported boundary for v0.14.0:

- Supported: unambiguous Maven reactor references, as listed for Maven above,
  including modules declared recursively by participating modules. They follow
  the transition, or, for an internal `${project.version}`, already resolve to
  it.
- Supported: independently declared components with their own locks and no
  internal references between them.
- Rejected before any write: every participating npm or uv workspace
  arrangement (workspace members, shared workspace locks and their member
  entries) and every local `file:`, `link:`, path or workspace link between
  participating components, including links that carry no version. An
  undeclared member does not make an otherwise participating shared workspace
  supported.
- Rejected before any source write: Maven property and range forms other than
  the one accepted above.

A rejected or ambiguous arrangement fails naming the affected components and
the limitation. External dependency versions remain unchanged. The design
chooses how references are identified and changed. No successful transition
may knowingly leave a stale internal reference inside that boundary.

## Version commands and the atomic transition

| Command | Required behavior |
| --- | --- |
| `version <root>` | Read-only version, title and notes from the anchor |
| `versions <root> list` | Each detected file with its kind, form and current value, so a user sees what a transition will touch before it does; tool-only manifest pairs and undeclared nested candidates appear with a not-participating status |
| `versions <root> check` | Actual and expected value for each source; nonzero exit on any drift |
| `versions <root> set <version>` | Update the anchor token and every applicable source as one recoverable operation, with the argument as the proposed authoritative value |

`set` accepts any well-formed `X.Y.Z` or `X.Y.Z-SNAPSHOT` target, lower or
higher than the current anchor; only the per-source guards apply, such as the
`release-only` downgrade refusal and unsupported forms. Accepting a target is
not permission to release it: release uniqueness and ordering stay with the
releasing callers of items 5 and 7. So one primitive serves the release, the
next snapshot, Step 12 and manual corrections.

A `set` to the version already in place still validates the complete
applicable set first, so it fails on an invalid source. It then rewrites only
the sources that differ from their expected form and, when nothing differs,
writes no version source and succeeds; operation-lock bookkeeping may still
occur. Re-running Step 12 is therefore safe, and item 5 receives exactly the
changed files. `set` never stages or commits.

A standalone `set` holds item 1's per-project operation lock across its whole
operation: capturing the originals, validating the complete set, writing and
any restoration. It fails when another operation holds the lock. A lifecycle
caller such as item 5 that already holds the lock runs the same primitive under
its existing ownership, without refusing itself or releasing the lock.
`version`, `list` and `check` take no lock and create no artifact. They may
observe a transition in progress, so their result is not isolated from it, and
a `check` during a transition is not a release-readiness guarantee.

When any write of a `set` fails, the engine restores the whole original set:
every source, the lock entries and the absence of files that did not exist
before. Before overwriting any source, the original bytes and existence of
every source in the set are recoverable; if that recovery evidence cannot be
prepared, no source is written. When restoration itself cannot complete, for
example because an editor holds a file open, the command fails with a status
distinct from an ordinary failure, names each source not restored and where its
retained original is, and never reports complete restoration. The evidence
lives in the consuming project's artifact home, never in the tooling checkout;
its interaction with item 5's encompassing transaction is design work. Files
are written through item 1's managed-write boundary, inside the validated
project root. Item 5's release and next-snapshot transitions reuse this same
operation and add their commits and tags around it. `version`,
`versions list|set|check` and `snapshot` need no git-cliff.

## Version-source configuration in .release.ini

Version-source settings belong to the version domain of item 1's schema
registry. A project without `.release.ini`, or without these sections, gets
the built-in detection and default forms. The umbrella's examples:

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
escaping. A pattern source requires `file`, `pattern` and `form`. Forms,
paths, patterns, missing required keys and unknown keys are validated before
mutation, including declarations the current command does not use. Project
configuration is data: no consumer code runs from it. The participating
component-root declaration is part of this domain; its syntax is design work.

## Stable and snapshot tag classification

- Stable releases are recognized only by the complete `vX.Y.Z` form or the
  legacy `X.Y.Z` form. `vX.Y.Z-SNAPSHOT` and `X.Y.Z-SNAPSHOT`, including
  historical case variants of the suffix, are development markers. Other
  prereleases are not stable releases either.
- This effort reads existing snapshot tags; it does not create, move or delete
  them on snapshot transitions.
- One shared classifier and range selector serves the engine, git-cliff input,
  release-notes collection and release-plan and documentation ranges (umbrella
  decision 26).
- The baseline is a reachable eligible stable release, excluding snapshot tags
  even when they point at HEAD. New engine tags become baselines only with
  `[valid]`. Historical stable releases without that marker stay eligible; a
  tag recorded as an active unvalidated transaction does not.
- The distinction between a historical release and a new unvalidated release
  holds in another clone and without local transaction evidence (umbrella
  decision 34). Missing evidence never turns an unfinished new release into a
  historical exception, and local journals alone cannot define eligibility.
  The persistent evidence and its migration are design decisions.
- Ambiguous validity is reported and never silently establishes a baseline.
  A documented deterministic ancestry rule selects among tags, and conflicting
  tags are reported rather than guessed. With no eligible stable tag, the full
  relevant history applies.
- The selector takes a target, HEAD or a stable release tag, with the same
  rules, so item 4's per-release changelog and item 7's readers share it. For
  HEAD, the baseline is the nearest eligible stable release, which may be a
  release at HEAD itself. A release-tag target must itself be an eligible
  stable release: a missing tag, a snapshot or other prerelease, or an
  ineligible tag such as an unvalidated one fails with a diagnostic. The target
  is never its own predecessor, and with no eligible predecessor the range is
  the full history through the target. `X.Y.Z` and `vX.Y.Z` on the same commit
  are one release boundary; on different commits they are conflicting tags and
  fail. The ancestry rule and the persistent eligibility evidence are design
  work.
- `git describe` output is never split on `-` to find a commit count, since the
  snapshot suffix is part of the version: the chosen ref and its commit
  distance are queried explicitly. No release-notes or release-plan reader may
  use an unfiltered "last tag" query once it adopts this selector.

For example, after stable `v0.13.0`, commits A and B surround
`v0.14.0-SNAPSHOT`. Preparing `0.14.0` selects `v0.13.0..HEAD` and includes
both A and B, even when HEAD itself carries the snapshot tag. Creating the
distinct `v0.14.0` tag and any recovery that may remove only its own
unvalidated tag belong to item 5.

## Release version uniqueness and ordering rule

Existing `X.Y.Z` and `vX.Y.Z` tags both reserve the same release version
(umbrella decision 33). A target must be higher than every eligible reachable
stable release on `main` (confirmed answer Q2 A). Lower maintenance releases
need a later, separate policy. With no eligible stable release, the existing
full-relevant-history behavior is preserved. This item defines and exposes the
rule, comparing versions numerically per component; items 5 and 7 enforce it in
their preflights. `versions set` does not apply it.

## Callers adopting the version-source operations

Each caller receives the full set of participating sources through the same
detection, form mapping and atomic synchronization:

| Caller | Use of version sources | Adoption owner |
| --- | --- | --- |
| `brel` (`pre`, release mode) | Anchor to `X.Y.Z`; each source to its release form; snapshot-form sources lose the suffix; each changed file joins the release commit | Item 5 |
| Next snapshot after a release | Every source to the chosen `X.Y.Z-SNAPSHOT` in its form, in the same commit as `version.txt` | Item 5 |
| `/prepare-release` Step 12 | `versions <root> set X.Y.Z-SNAPSHOT` then `versions <root> check`, replacing its per-format instructions | Item 7 |
| A project `check.bat` | `versions <root> check`, replacing a project `check_versions.py` | Consumer migrations |
| Changelog, notes and release-plan readers | The shared stable/snapshot range selector | Items 4 and 7 |

## dev_workflow version defects not carried forward

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
- `update-version.bat` lines 435 and 437 compare `"%git_tag%"==v"%version%"`.
  The quotes differ on each side, so the "already released" guards never match.
  This item supplies the uniqueness rule; item 5 applies it.

## Consumer inputs shaping the supported set

These repositories shape the supported formats. Their migrations stay in their
own efforts; llm-shared's belongs to item 8.

- llm-shared: `version.txt`, `pyproject.toml` and `uv.lock`, with plain `X.Y.Z`
  in `pyproject.toml` and `uv.lock` during the snapshot, as Step 12 does today.
- my-project: the built-in adapters cover `version.txt`, `pyproject.toml`,
  `uv.lock`, `pom.xml` and `PDF/pom.xml`; `cicd/config/.env` becomes one
  `pattern` source. `tools/set_version.py` and `tools/check_versions.py` can
  then retire, and `check.bat` calls `versions check`. Its
  `publish_pdf_nexus*.sh` version menus must exclude snapshot tags, with this
  item's tag policy as their contract.
- workspace-halo: `package.json` and `package-lock.json` use `release-only`,
  stating `0.0.25` while `version.txt` reads `0.0.25-SNAPSHOT` and staying
  `0.0.25` at release; `-SNAPSHOT` never enters the VSIX version. Range
  selection handles its mixed prefixed and unprefixed tags.

## Acceptance criteria for version sources

| ID | Observable acceptance criterion |
| --- | --- |
| AC1 | `version <root>` returns version, title and notes without writing any file or preparing artifacts; a missing anchor, or a token other than exactly `X.Y.Z` or `X.Y.Z-SNAPSHOT` (no leading zeros, uppercase suffix, no `v`), fails with an actionable error and creates nothing; an empty title or empty notes are accepted by `version` and `versions` |
| AC2 | A transition replaces only the anchor's first token; title, notes and every other byte, including line endings, are unchanged |
| AC3 | Adapters are registered only in llm-shared's explicit tuple; the completeness test fails for an unregistered adapter module; each adapter has detection, read, expected-form, write and failure-restoration contract tests; adding an adapter needs no consumer copy or release-lifecycle edit |
| AC4 | Detection finds the Python/uv local root, the npm root manifest and lock, the Maven reactor with its recursively declared modules and declared pattern sources; it excludes dependencies, the skipped directories, vendor and sample projects and nested foreign repositories; a tool-only `pyproject.toml` or `package.json` and its lock are excluded together; at the root and declared component roots, an absent optional lock is not generated, and an orphan lock or a lock in an unsupported or ambiguous schema fails `list`, `check` and `set` before any source write |
| AC5 | All detectors run in one project: a Python plus npm root updates all four files; every participating component takes the anchor's version in its form; a declared nested component root participates; an undeclared nested candidate does not participate and makes neither `check` nor `set` fail; conflicting claims on one file fail before any write |
| AC6 | Dynamic or missing Python project versions, unparsable manifest files, ambiguous lock roots, unsupported form and format combinations, pattern sources with a missing key, a missing file, or zero, several or empty captures, and Maven property expressions or ranges in project, internal parent or internal dependency version fields (except a whole-value internal dependency or dependency-management `${project.version}`) fail before any write, naming the source and the remedy |
| AC7 | A snapshot anchor gives `X.Y.Z` to Python and default npm sources and keeps the suffix for Maven and configured snapshot sources; a release anchor gives `X.Y.Z` everywhere; a `release-only` source that would be lowered fails the whole transition before any write, naming the source, its value and the target, with no override; `check` reports a source ahead of the anchor as drift; comparisons are numeric per component; the previous published core is never kept |
| AC8 | Writes touch only the owned version fields: uv local root and npm root lock entries, with lock schema, dependency, hash, URL and resolver data, external versions and inherited Maven versions unchanged; no global `version` replacement; no opportunistic lock regeneration, dependency resolution or tool check; a supported pair the tool accepted as current before the transition is still accepted after it |
| AC9 | Maven reactor references (project, internal parent and literal internal dependency and dependency-management versions, recursively) follow the transition, and a whole-value internal `${project.version}` stays unchanged; independently declared components with their own locks are supported; every participating npm or uv workspace arrangement and every local `file:`, `link:`, path or workspace link between participating components, and any other unsupported or ambiguous arrangement, fail before any write, naming the components and the limitation |
| AC10 | `versions list` shows each source with kind, form and current value, and each tool-only pair and undeclared nested candidate with its path and a not-participating status; `versions check` reports actual and expected values and exits nonzero on drift; a format without a registered adapter is never detected or synchronized |
| AC11 | `versions set` accepts any well-formed target and changes the anchor and every applicable source as one operation under the per-project operation lock, failing when another operation holds it and reusing a lifecycle caller's ownership; a same-target run validates the whole set, rewrites only drifted sources, writes none when clean and never stages or commits; recovery evidence of every source exists before the first overwrite, or nothing is written; an injected failure at any write restores the complete original set, including lock entries and previously absent files; a restoration that cannot complete fails with a distinct status naming each unrestored source and its retained original in the project's artifact home; `version`, `list` and `check` take no lock and create no artifact; version commands run without git-cliff |
| AC12 | Without `.release.ini` or its version sections, built-in detection and default forms apply; declared forms, paths, patterns, missing required pattern keys and unknown keys are validated before mutation, including unused declarations; interpolation is off and configuration is never executed |
| AC13 | The shared classifier recognizes `vX.Y.Z` and legacy `X.Y.Z` as stable, snapshot markers in both spellings and case variants as non-releases; baseline selection excludes snapshot tags even at HEAD and new unvalidated tags even in another clone or without a journal, keeps historical stable tags without `[valid]`, reports ambiguous validity and conflicting tags, and falls back to full relevant history when no stable tag is eligible |
| AC14 | Commit distance comes from the chosen ref, never from splitting `git describe` output; the selector is exposed to changelog, release-notes and release-plan callers; it accepts HEAD, whose baseline may be a release at HEAD, or an eligible stable release tag, rejecting a missing, prerelease or ineligible tag; a target is never its own predecessor; a first release gives the full history through the target; same-commit `X.Y.Z` and `vX.Y.Z` are one boundary and different-commit ones fail as conflicting; mixed prefixed and unprefixed histories select the correct baseline |
| AC15 | `X.Y.Z` and `vX.Y.Z` reserve the same release version; the exposed rule, comparing numerically per component, rejects a target not higher than every eligible reachable stable release on `main`, and preserves the no-stable-release behavior; `versions set` itself does not apply it |

Validation uses the selected whole suite. These criteria define expected
behavior; test organization and implementation mechanisms belong in the design
and plans. That suite is llm-shared's own development test suite, run while
llm-shared is changed: no version command, no `brel` and no consumer release
runs it, and release-time testing of a consumer belongs to umbrella item 5.

## Existing references for the version-sources requirement

- `tools/release_workflow/cli.py`: `SHIPPED_HANDLERS` is empty, so every
  release operation reports that it is unavailable.
- `tools/release_workflow/schemas.py`: `SHIPPED_SCHEMAS` registers only the
  tooling domain; this item adds the version domain.
- `tools/release_workflow/configuration.py`: the common `.release.ini` reader.
- `tools/release_workflow/managed_files.py`: guarded managed writes inside the
  validated root.
- `tools/release_workflow/invocation.py`: engine-computed legacy locations,
  including the version, POM and `package.json` files.
- `bin/release_workflow.bat`: the shared launcher dispatching `version` and
  `versions`.
- `tools/dev_workflow/get-version.bat`: the `0.1.0-SNAPSHOT` fallback written
  when `version.txt` is missing.
- `tools/dev_workflow/update-version.bat`, `t_build_maven.bat`,
  `mvn_get_version.ps1`, `t_build_npm.bat`: the legacy version handling and the
  defects listed above.
- `instructions/prepare-release.md`, Step 12: today's per-format version
  instructions.
- `version.txt`, `pyproject.toml`, `uv.lock`: llm-shared's own version sources.
- [Focused draft](draft.v0.14.0.version-sources.md): approved scope for item 2.
- [Umbrella](draft.v0.14.0.sibling_release_tooling.md): shared contracts,
  decisions 5, 6, 13, 14, 15, 26, 33, 34 and 39, and ownership of items 3
  through 8.

## File-based IO cost clarification for version sources

Version commands are synchronous and read only what they act on: the anchor
and the participating version sources, each once per read command, plus the
artifact home to report leftover recovery evidence. `versions set` reads its
sources again only where the transition must observe the disk, writes its
recovery evidence before the first overwrite and replaces each changed file
atomically. Only `versions list` asks Git for the project's file tree, to show
undeclared candidates. No version command runs git-cliff, uv, npm or Maven, and
none adds a document index or a new wall-clock target.

## Requirement clarifications for version sources

The user decided each question after an explanation (Q01 to Q04 on
2026-11-03, Q05 to Q14 on 2026-11-04, Q15 on 2026-11-05), and independent
review rounds 3 to 5 checked the decisions for consistency. The question
blocks, with their full options and arguments, are kept in the commit
`docs(feature): record pre-consolidation questions`.

| Question | Decision and reason | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | `set` accepts any well-formed target with only per-source guards; release uniqueness and ordering stay with items 5 and 7; comparisons are numeric per component. One primitive serves every caller, inside item 2's ownership | Version commands and the atomic transition; Version forms and their guards; Release version uniqueness and ordering rule; AC7, AC11, AC15 | Refusing a lower core (blocks legitimate corrections); applying the full uniqueness rule in `set` (ties a file primitive to tag state, duplicates items 5 and 7) |
| Q02 | A same-target `set` validates the whole set, rewrites only drifted sources, writes none when clean and never stages or commits; lock bookkeeping may occur. Step 12 re-runs stay safe and item 5 gets exactly the changed files | Version commands and the atomic transition; AC11 | Always rewriting every source (byte churn); refusing a same-target `set` (breaks idempotent re-runs) |
| Q03 | The anchor token is exactly `X.Y.Z` or `X.Y.Z-SNAPSHOT` (no leading zeros, uppercase suffix, no `v`); title and notes may be empty for version commands and are required by item 5 for a release | The version.txt anchor and its read-only access; AC1 | Accepting and normalizing `v` and case variants (rewrites author bytes); requiring title and notes everywhere (blocks fresh projects) |
| Q04 | A `release-only` downgrade refusal fails the whole transition before any write, naming source, value and target; `check` reports it as drift; no override in v0.14.0. It keeps the atomic contract | Version forms and their guards; AC7 | Skipping the source (inconsistent set); a downgrade override (a published version cannot be rewound, invites misuse) |
| Q05 | A `pyproject.toml` without `[project]` or a root `package.json` without `version` is tool-only: it and its lock are excluded together and listed as not participating; dynamic or missing Python versions and unparsable manifest files still fail | Participation and detection of ecosystems; AC4, AC6, AC10 | Failing until declared non-participating (one setting per tool-only file); silently ignoring them (user cannot see why) |
| Q06 | One project version: every participating component takes the anchor's version in its form; independently released packages are not declared, never touched, and references to them stay unchanged without implying validity; per-component versions out of scope | Participation and detection of ecosystems; AC5 | Per-component anchors (several versions per release, larger scope); fixed component versions (new rule, no consumer) |
| Q07 | Undeclared nested candidates are listed with path and a not-participating status, ignored by `check` and `set`, under the detection exclusions | Participation and detection of ecosystems; Version commands and the atomic transition; AC5, AC10 | Silent exclusion (forgotten components unnoticed); failing until classified (mandatory exclusion syntax) |
| Q08 | Supported boundary: Maven reactor project, internal parent and literal internal dependency and dependency-management versions, recursively; independently declared components with their own locks. Rejected before any write: participating npm or uv workspace arrangements and local links between participating components | Version-only writes, locks and internal references; AC9 | Adding npm and uv workspaces (no consumer, ambiguous ranges); Maven parents only (common reactors would fail) |
| Q09 | Pattern sources require `file`, `pattern` and `form`; the file must exist and is never created; exactly one successful nonempty capture, otherwise `list`, `check` and `set` fail before any write | Supported formats for v0.14.0 and later candidates; Version-source configuration in .release.ini; AC6, AC12 | A default form or skipping a missing file with a warning (silent drift after a rename) |
| Q10 | For a supported format and tool version, a pair the tool accepted before the transition is still accepted after the version-only edit; no repair of earlier drift or future-tool promise; no opportunistic tool run; design chooses the evidence | Version-only writes, locks and internal references; AC8 | A field-level guarantee only (tool may disagree); running the tool after each write (tool dependency, version-dependent result) |
| Q11 | A standalone `set` holds the operation lock from capture to restoration and fails when it is held; a lifecycle caller reuses its ownership; reads take no lock, create no artifact and are not release-readiness guarantees during a transition | Version commands and the atomic transition; AC11 | Locking reads too (blocks reads during a release); no lock in this item (racing restorations) |
| Q12 | Recovery evidence of every source exists before the first overwrite, or nothing is written; an incomplete restoration fails with a distinct status naming each unrestored source and its retained original in the consuming project's artifact home | Version commands and the atomic transition; AC11 | Reporting paths only (original bytes lost); retrying until a timeout (can hang, still needs a final outcome) |
| Q13 | The shared selector takes HEAD or an eligible stable release tag with the same rules; a target is never its own predecessor; first release gives full history; same-commit aliases are one boundary, different-commit ones conflict | Stable and snapshot tag classification; AC14 | HEAD only (two diverging range rules); a list of releases for callers (each re-implements the predecessor rule); accepting an owned unvalidated tag (no current caller) |
| Q14 | After participation filtering, an absent optional lock is not generated; an existing lock needs an identifiable participating manifest and a supported unambiguous schema, otherwise failure before any source write; Q05 tool-only pairs stay excluded together | Participation and detection of ecosystems; AC4, AC8 | Requiring a lock everywhere (rejects lock-free projects); skipping unusable locks with a warning (stale release lock) |
| Q15 | Maven project versions are literal or inherited and internal parent versions literal; only `${project.version}` as the entire internal dependency or dependency-management version is accepted, unchanged, since it resolves to the shared version; every other expression fails before any source write | Version-only writes, locks and internal references; AC6, AC9 | Literal values only (rejects an always-consistent idiom); adding root-POM `${revision}` (no consumer, needs further boundary decisions) |
