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
mechanism, exact output formats and exit-code numbers remain design work.

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

Detection follows the project's nature, not every matching file:

- Python: the project identified by its declared name and its local or virtual
  root entry in `uv.lock`.
- npm: the root manifest and its lock.
- Maven: the reactor reached through the root POM's declared modules.
- Never inside `node_modules`, `venvs`, `.venv`, `.git`, `.reviews` or
  `target`, vendor or sample projects, or nested Git repositories.

Independent workspace packages need explicit configuration rather than
accidental synchronization. Dynamic Python versions, ambiguous lock roots and
unsupported Maven property indirection fail with the exact source and the
configuration remedy; the engine never guesses.

## Version forms and their guards

| Form | Snapshot `1.2.3-SNAPSHOT` becomes | Release `1.2.3` becomes | Default for |
| --- | --- | --- | --- |
| `snapshot` | `1.2.3-SNAPSHOT` | `1.2.3` | Maven POMs, the configured `.env` variable |
| `core` | `1.2.3` | `1.2.3` | `pyproject.toml`, `uv.lock` |
| `release-only` | `1.2.3` | `1.2.3` | `package.json`, `package-lock.json` |

`core` and `release-only` produce the same strings and differ in their guard:
a `release-only` source refuses a value lower than the one it already states,
because lowering a published extension version would rewind it.

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
  expression with one capture group and a form. It must match exactly one
  version capture in its declared file. my-project's `cicd/config/.env` becomes
  one such declaration.

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
- Maven: the reactor's project versions and the `<parent>` version of each
  module declared in the root POM's `<modules>`. Inherited versions stay
  inherited; external parent, dependency and plugin versions stay unchanged.
  Supported reactor version properties are handled explicitly; others are
  rejected with an actionable error.

Each adapter validates its complete write set before changing any file, and
preserves unrelated content, formatting and line endings. No field named
`version` is replaced globally. Supported lock entries are edited directly for
a version-only change: `uv lock`, `uv sync` or npm dependency resolution never
run merely because a tool is present. If a supported format ever needs
regeneration, the engine requires its tool and limits and validates its
changes; when consistency cannot be kept safely, it fails before mutation
instead of producing a best-effort lock.

Synchronization also covers version references between participating
components (umbrella decision 39). Changing Maven module A while module B still
depends on A's old version is not a consistent reactor transition; the same
contract applies to supported participating workspace packages and their
manifests and locks. Within the supported boundary, internal references follow
the transition. Arrangements outside that boundary, or ambiguous ones, fail
before any write and name the affected components and the limitation. External
dependency versions remain unchanged. This requirement states the supported
boundary; its concrete extent is proposed in Q08 and remains a pending user
decision. The design chooses how references are identified and changed. No
successful transition may knowingly leave a stale internal reference inside
that boundary.

## Version commands and the atomic transition

| Command | Required behavior |
| --- | --- |
| `version <root>` | Read-only version, title and notes from the anchor |
| `versions <root> list` | Each detected file with its kind, form and current value, so a user sees what a transition will touch before it does |
| `versions <root> check` | Actual and expected value for each source; nonzero exit on any drift |
| `versions <root> set <version>` | Update the anchor token and every applicable source as one recoverable operation, with the argument as the proposed authoritative value |

When any write of a `set` fails, the engine restores the whole original set:
every source, the lock entries and the absence of files that did not exist
before. Files are written through item 1's managed-write boundary, inside the
validated project root. Item 5's release and next-snapshot transitions reuse
this same operation and add their commits and tags around it. `version`,
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
escaping. Forms, paths, patterns and unknown keys are validated before
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
rule; items 5 and 7 enforce it in their preflights.

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
| AC1 | `version <root>` returns version, title and notes without writing any file or preparing artifacts; a missing or malformed anchor fails with an actionable error and creates nothing |
| AC2 | A transition replaces only the anchor's first token; title, notes and every other byte, including line endings, are unchanged |
| AC3 | Adapters are registered only in llm-shared's explicit tuple; the completeness test fails for an unregistered adapter module; each adapter has detection, read, expected-form, write and failure-restoration contract tests; adding an adapter needs no consumer copy or release-lifecycle edit |
| AC4 | Detection finds the Python/uv local root, the npm root manifest and lock, the Maven reactor with its internal module parents and declared pattern sources; it excludes dependencies, the skipped directories, vendor and sample projects and nested foreign repositories |
| AC5 | All detectors run in one project: a Python plus npm root updates all four files; a declared nested component root participates, an undeclared nested manifest does not; conflicting claims on one file fail before any write |
| AC6 | Dynamic Python versions, ambiguous lock roots, unsupported Maven property indirection, unsupported form and format combinations, and pattern sources without exactly one capture fail before any write, naming the source and the remedy |
| AC7 | A snapshot anchor gives `X.Y.Z` to Python and default npm sources and keeps the suffix for Maven and configured snapshot sources; a release anchor gives `X.Y.Z` everywhere; `release-only` refuses a downgrade and never keeps the previous published core |
| AC8 | Writes touch only the owned version fields: uv local root and npm root lock entries, with lock schema, dependency, hash, URL and resolver data, external versions and inherited Maven versions unchanged; no global `version` replacement; no opportunistic lock regeneration or dependency resolution; unrelated content and formatting preserved |
| AC9 | Within the supported boundary this requirement states (proposed in Q08), internal references between participating components follow the transition; unsupported or ambiguous arrangements fail before any write, naming the components and the limitation |
| AC10 | `versions list` shows each source with kind, form and current value; `versions check` reports actual and expected values and exits nonzero on drift; a format without a registered adapter is never detected or synchronized |
| AC11 | `versions set` changes the anchor and every applicable source as one operation; an injected failure at any write restores the complete original set, including lock entries and previously absent files; version commands run without git-cliff |
| AC12 | Without `.release.ini` or its version sections, built-in detection and default forms apply; declared forms, paths, patterns and unknown keys are validated before mutation, including unused declarations; interpolation is off and configuration is never executed |
| AC13 | The shared classifier recognizes `vX.Y.Z` and legacy `X.Y.Z` as stable, snapshot markers in both spellings and case variants as non-releases; baseline selection excludes snapshot tags even at HEAD and new unvalidated tags even in another clone or without a journal, keeps historical stable tags without `[valid]`, reports ambiguous validity and conflicting tags, and falls back to full relevant history when no stable tag is eligible |
| AC14 | Commit distance comes from the chosen ref, never from splitting `git describe` output; the selector is exposed to changelog, release-notes and release-plan callers; mixed prefixed and unprefixed histories select the correct baseline |
| AC15 | `X.Y.Z` and `vX.Y.Z` reserve the same release version; the exposed rule rejects a target not higher than every eligible reachable stable release on `main`, and preserves the no-stable-release behavior |

Validation uses the selected whole suite. These criteria define expected
behavior; test organization and implementation mechanisms belong in the design
and plans.

The open questions below propose refinements that remain pending user
decisions. Once decided, each one refines these criteria:

| Question | Criteria it refines |
| --- | --- |
| Q01, Q02, Q04 | AC7, AC11 |
| Q03 | AC1, AC2 |
| Q05, Q07 | AC4, AC5, AC10 |
| Q06 | AC5, AC9 |
| Q08 | AC9 |
| Q09 | AC6, AC12 |
| Q10 | AC8 |
| Q11, Q12 | AC11 |
| Q13 | AC13, AC14 |
| Q14 | AC4, AC8, AC10 |
| Q15 | AC6, AC9 |

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

## Open questions for the v0.14.0 version-sources feature request

### Q01: Targets accepted by versions set

Question description: the requirement defines `versions <root> set <version>`
as the shared transition primitive, reused by item 5's release and next
snapshot, by Step 12 and by direct calls. It states the `release-only`
downgrade guard per source and the uniqueness and ordering rule that items 5
and 7 enforce, but not what the direct `set` command itself accepts: a lower
anchor, a release form `X.Y.Z`, or a version that an existing stable tag
already reserves.

#### BBQ for Q01

The pump at the gas station fills whatever amount you key in; the cashier is
the one who checks you paid. If the pump also starts checking receipts, every
other station that uses it inherits those checks, wanted or not. In this
picture: the pump is `versions set`, the amount keyed in is the target
version, the cashier is the release preflight of items 5 and 7, and the
receipts are the existing stable tags.

#### Options for Q01

- Option A: `set` accepts any valid `X.Y.Z` or `X.Y.Z-SNAPSHOT`; only the
  per-source guards apply (`release-only` downgrade, unsupported forms);
  ordering and uniqueness stay with the callers that release.
  - pro: one primitive serves release, next snapshot, Step 12 and manual
    corrections without special cases.
  - pro: matches the umbrella split: this item states and exposes the rule,
    items 5 and 7 enforce it.
  - con: a direct call can set a version that is already released, until a
    release preflight rejects it.
- Option B: `set` also refuses a target whose core is lower than the current
  anchor's core.
  - pro: prevents an accidental rewind of `version.txt`.
  - con: blocks a legitimate correction before any release, such as
    `0.15.0-SNAPSHOT` back to `0.14.1-SNAPSHOT` after a wrong bump.
- Option C: `set` applies the full uniqueness and ordering rule itself.
  - pro: no caller can forget the rule.
  - con: ties a file primitive to tag state on `main`, repeats the check items
    5 and 7 already make, and a snapshot target does not reserve a release.

#### Recommended option for Q01 (with arguments for this choice)

Option A: the direct command stays a version-file primitive with source-level
guards. The rule that protects published releases lives where a release is
actually made, and the requirement already exposes it to those callers.

Accepting a syntactically valid target is not permission to create a release.
Wherever versions are compared, in the `release-only` guard and in the exposed
ordering rule, the comparison is numeric per component, so `0.10.0` is higher
than `0.9.0`. (Clarified after review round 1.)

#### Answer to Q01: option A (with reason why it must be accepted as the answer)

Option A: it keeps one transition primitive for every caller, keeps item 2
inside its ownership boundary, and still blocks the one rewind that cannot be
undone (a published npm or extension version) through the `release-only`
guard.

User decision: confirmed - Option A, as recommended: `versions set` accepts any
valid `X.Y.Z` or `X.Y.Z-SNAPSHOT` with only the per-source guards; release
uniqueness and ordering stay with the releasing callers (items 5 and 7), and
version comparisons are numeric per component. Decided by the user on
2026-11-03 during the round 2 question explanation, with no further comment.

### Q02: Setting the version already in place

Question description: Step 12 must be safe to re-run, which is why it calls
`npm version` with `--allow-same-version` today. The requirement does not say
what `set` does when the anchor already holds the target: whether it rewrites
every source, only repairs drifted ones, or refuses. It also does not say
whether `set` stages anything in Git.

#### BBQ for Q02

When you ask a painter to paint a wall the color it already is, a good painter
touches up only the scratches and leaves the rest alone, and never signs off
the job for you. In this picture: the wall is the version-source set, the
color is the target version, the scratches are drifted sources, and signing
off is staging or committing in Git.

#### Options for Q02

- Option A: `set` with the version already in place rewrites only the sources
  that differ from their expected form; when nothing differs, it writes no
  version source and succeeds. It still validates the complete applicable set
  first, so a same-target run fails on an invalid source. Operation-lock
  bookkeeping may still happen; the no-op guarantee is that no version source
  is written. It never stages or commits.
  - pro: Step 12 re-runs are idempotent and a clean tree stays clean.
  - pro: item 5's "each changed file joins the commit" receives exactly the
    changed files.
  - con: needs a comparison before each write, a small cost.
- Option B: `set` always rewrites every source.
  - pro: simplest behavior to describe.
  - con: touches file timestamps and risks byte churn for no version change.
- Option C: `set` refuses when the anchor already holds the target; drift
  repair needs a separate command.
  - pro: makes repair explicit.
  - con: breaks idempotent re-runs and adds a command to the surface.

#### Recommended option for Q02 (with arguments for this choice)

Option A: it gives the expected result of re-running a preparation step, makes
`set` a natural drift repair after `check` reports a problem, and keeps commits
and staging with the callers that own them. (Validation and lock wording
clarified after review round 1.)

#### Answer to Q02: option A (with reason why it must be accepted as the answer)

Option A: idempotent re-runs are already part of today's Step 12 contract, and
writing only changed files is what item 5 needs to build its commit.

User decision: confirmed - Option A, as recommended: a same-target `set`
validates the complete applicable set, rewrites only drifted sources, writes no
version source when nothing differs, and never stages or commits;
operation-lock bookkeeping may still occur. Decided by the user on 2026-11-03
during the round 2 question explanation, with no further comment.

### Q03: What makes the version.txt anchor well formed

Question description: the requirement says a missing or malformed anchor fails,
but does not define malformed. Open points: whether the token must be exactly
`X.Y.Z` or `X.Y.Z-SNAPSHOT` (no `v`, no lowercase suffix, no other
prerelease, no leading zeros), and whether the title after `--` and the notes
are required for `version` and `versions`, or only for item 5's release
preflight. A fresh project may hold only `0.1.0-SNAPSHOT`.

#### BBQ for Q03

A bouncer can check only that your ticket is genuine, or also that you wear a
tie. Checking the tie at the front door turns away people who only came to look
at the menu. In this picture: the ticket is the version token, the tie is a
nonempty title and notes, the front door is the read and `versions` commands,
and the dinner itself is item 5's release.

#### Options for Q03

- Option A: the token must be exactly `X.Y.Z` or `X.Y.Z-SNAPSHOT`, with
  non-negative integers without leading zeros and the uppercase suffix; title
  and notes may be empty for `version` and `versions`; item 5 requires them
  for a release.
  - pro: a strict token prevents malformed tags and ecosystem values later.
  - pro: a fresh project can run `versions list` and `check` at once.
  - con: an older file with a lowercase suffix fails until fixed (with a
    remedy message).
- Option B: also accept a `v` prefix and suffix case variants, normalizing them
  on the next write.
  - pro: tolerant of legacy spellings.
  - con: rewrites bytes the author wrote and contradicts the notation table.
- Option C: require a nonempty title and notes for every command.
  - pro: a single rule for all commands.
  - con: blocks `check` on a fresh project and duplicates item 5's preflight.

#### Recommended option for Q03 (with arguments for this choice)

Option A: the token is what every source and tag is derived from, so it gets
the strict rule; title and notes are release content, so their presence is
checked by the release lifecycle that uses them. This rule covers the anchor
only: recognizing historical tag spellings is the separate tag classification
contract. (Scope note added after review round 1.)

#### Answer to Q03: option A (with reason why it must be accepted as the answer)

Option A: it follows the notation table exactly, keeps read and check usable on
any valid project, and leaves release-content checks with item 5.

User decision: confirmed - Option A, as recommended: the anchor token must be
exactly `X.Y.Z` or `X.Y.Z-SNAPSHOT` (non-negative integers without leading
zeros, uppercase suffix, no `v`); title and notes may be empty for `version`
and `versions`, and item 5 requires them for a release; historical tag
spellings keep their separate classification contract. Decided by the user on
2026-11-03 during the round 2 question explanation, with no further comment.

### Q04: How the release-only downgrade refusal behaves

Question description: a `release-only` source refuses a value lower than the
one it states. The requirement does not say whether that refusal stops the
whole transition, skips that one source, or can be overridden, nor how `check`
reports a source that is ahead of the anchor.

#### BBQ for Q04

When one passenger refuses to board, the coach either waits at the stop or
leaves without them. Leaving without them means the group arrives split up.
In this picture: the passenger is a `release-only` source already ahead of the
target, the coach is the atomic `set`, and arriving split up is a source set
with mixed versions.

#### Options for Q04

- Option A: the whole transition fails before any write, naming the source, its
  value and the target; `check` reports that source as drift with a nonzero
  exit; no override in v0.14.0.
  - pro: keeps the atomic contract; matches Step 12's "stop and report".
  - con: a deliberate downgrade needs a manual edit.
- Option B: skip that source, update the others and warn.
  - pro: the transition goes through.
  - con: leaves exactly the inconsistent set this item exists to prevent.
- Option C: fail by default, with an explicit downgrade override.
  - pro: offers an escape hatch.
  - con: a published Marketplace version cannot be rewound anyway; the
    override invites misuse and adds a choice to every non-interactive caller.

#### Recommended option for Q04 (with arguments for this choice)

Option A: the guard protects something that cannot be undone, so it must stop
the transition rather than weaken it, and the atomic rule already forbids a
partial set.

#### Answer to Q04: option A (with reason why it must be accepted as the answer)

Option A: it combines the existing Step 12 behavior with the atomic contract and
needs no new flag.

User decision: confirmed - Option A, as recommended: a `release-only` downgrade
refusal fails the whole transition before any write, naming the source, its
value and the target; `check` reports that source as drift with a nonzero exit;
no override in v0.14.0. Decided by the user on 2026-11-03 during the round 2
question explanation, with no further comment.

### Q05: Root manifests that carry no project version

Question description: many repositories keep a root `pyproject.toml` only for
tool settings (ruff, pyright) or a private `package.json` only for development
tools, with no version. The requirement rejects dynamic Python versions, but
does not say whether such tool-only manifests are version sources that fail, or
are not version sources at all.

#### BBQ for Q05

Not every box in the garage holds tools for sale; some just hold the
lawnmower's spare blades. A stock-take that fails because a box has no price
tag stops the whole shop for nothing. In this picture: the boxes are root
manifests, the price tag is a static version field, and the stock-take is
`versions check`.

#### Options for Q05

- Option A: a `pyproject.toml` without a `[project]` table, or a root
  `package.json` without a `version` field, is tool-only and not a version
  source. Its lock is excluded with it and never participates on its own.
  `list` shows the pair as not participating, and `set` and `check` ignore it.
  A `[project]` table with a dynamic or missing version still fails, and a
  present manifest that cannot be parsed fails rather than being treated as
  tool-only.
  - pro: tool-only manifests keep working with no configuration.
  - pro: the dynamic-version rejection keeps its meaning for real projects.
  - con: a project that forgot its version field is not synchronized, though
    `list` shows it.
- Option B: any root manifest without a static version fails until
  `.release.ini` declares it non-participating.
  - pro: every exclusion is explicit.
  - con: one configuration line per tool-only file in many repositories.
- Option C: ignore such manifests silently, not even listed.
  - pro: quiet output.
  - con: the user cannot see why a manifest was left out.

#### Recommended option for Q05 (with arguments for this choice)

Option A: it separates "no project here" from "a project whose version cannot
be read", fails only the second, and keeps the first visible in `list`.
(Paired-lock and malformed-manifest rules added after review round 1; Q14
covers the remaining manifest and lock pairs.)

#### Answer to Q05: option A (with reason why it must be accepted as the answer)

Option A: it avoids false failures in common repository layouts while keeping
the never-guess rule for actual Python and npm projects.

User decision: confirmed - Option A, as recommended: a `pyproject.toml` without
a `[project]` table, or a root `package.json` without a `version` field, is
tool-only and not a version source; its lock is excluded with it, `list` shows
the pair as not participating, and `set` and `check` ignore it, while a
`[project]` table with a dynamic or missing version, or a present manifest that
cannot be parsed, still fails. Decided by the user on 2026-11-04 during the
round 2 question explanation, with no further comment.

### Q06: One version for every participating component

Question description: the requirement synchronizes every participating source
from one anchor and says independent workspace packages need explicit
configuration. It does not say whether a declared component can carry its own
version, or whether every participating component always takes the project
version while independently released packages are simply not declared.

#### BBQ for Q06

A choir sings in one key; a soloist who wants a different key does not join the
choir for that song. Letting each singer choose their own key inside the choir
turns one song into several. In this picture: the choir is the set of
participating components, the key is the anchor version, the soloist is an
independently released package, and several songs are several release
versions in one release.

#### Options for Q06

- Option A: one project version: every participating component takes the
  anchor's version in its form; an independently released package is not
  declared and never touched. Not declaring it only excludes it from
  synchronization: references to it follow the existing external-version rule
  and stay unchanged, without implying that they are valid. Per-component
  versions are out of scope for v0.14.0.
  - pro: follows "version.txt is authoritative" and one release version per
    release (umbrella decision 35).
  - pro: keeps detection, check and tags simple.
  - con: a repository with independently versioned packages cannot release
    those packages through this engine yet.
- Option B: each declared component may have its own anchor and version.
  - pro: covers independently versioned monorepos.
  - con: several versions and tags per release, against the umbrella's one
    release version; much larger scope.
- Option C: a component may declare a fixed version that `check` verifies but
  `set` never changes.
  - pro: covers a pinned sub-package.
  - con: adds a second version rule and a new configuration concept for no
    current consumer.

#### Recommended option for Q06 (with arguments for this choice)

Option A: none of the three repositories needs per-component versions, and the
umbrella already settles one release version per release. (External-reference
wording clarified after review round 1.)

#### Answer to Q06: option A (with reason why it must be accepted as the answer)

Option A: it states the existing umbrella intent explicitly and gives the
"explicit configuration" of independent packages a clear meaning: they are not
declared.

User decision: confirmed - Option A, as recommended: one project version, where
every participating component takes the anchor's version in its form, an
independently released package is not declared and never touched, references
to it follow the existing external-version rule and stay unchanged without
implying that they are valid, and per-component versions are out of scope for
v0.14.0. Decided by the user on 2026-11-04 during the round 2 question
explanation, with no further comment.

### Q07: Visibility of undeclared nested component candidates

Question description: a nested component participates only when
`.release.ini` declares it. The requirement does not say what `list`, `check`
and `set` do with a nested manifest that looks like a component root (for
example `frontend/package.json`) but is not declared.

#### BBQ for Q07

A gate guard who silently waves away an unknown visitor never tells the host
someone came. One who refuses everyone without an invitation blocks the
delivery driver. In this picture: the visitor is an undeclared nested manifest,
the host is the user reading `versions list`, and the invitation is a
participating component-root declaration.

#### Options for Q07

- Option A: `list` reports each undeclared candidate with its path and a
  not-participating status; `check` and `set` ignore it and do not fail.
  Candidates obey the same exclusions as detection: skipped directories,
  vendor and sample projects and nested Git repositories are never reported.
  - pro: the user sees what setup could declare, with no false failure.
  - pro: `list` still states precisely which files `set` touches.
  - con: longer `list` output in repositories with several nested application
    manifests.
- Option B: ignore undeclared candidates silently.
  - pro: quiet output.
  - con: a forgotten application component stays at an old version unnoticed.
- Option C: `check` fails until each candidate is declared participating or
  excluded.
  - pro: forces an explicit decision.
  - con: every nested application manifest must be classified, and an
    exclusion syntax becomes mandatory.

#### Recommended option for Q07 (with arguments for this choice)

Option A: it keeps the participation rule strict for writes while making the
undeclared candidates visible, which is what item 6's setup and a human
reviewing `list` need. (Eligibility limit and status reporting added after
review round 1.)

#### Answer to Q07: option A (with reason why it must be accepted as the answer)

Option A: it applies the same "visible but not participating" treatment as Q05
and does not turn nested manifests into release failures.

User decision: confirmed - Option A, as recommended: `list` reports each
undeclared nested candidate with its path and a not-participating status,
`check` and `set` ignore it and do not fail, and candidates obey the same
exclusions as detection, so skipped directories, vendor and sample projects and
nested Git repositories are never reported. Decided by the user on 2026-11-04
during the round 2 question explanation, with no further comment.

### Q08: Supported internal-reference boundary in v0.14.0

Question description: umbrella decision 39 and its contract say child
requirements must state the supported boundary for internal references, while
designs choose how references are identified and changed. The body now states
that this requirement owns the boundary and points to this question for its
concrete extent: which references between participating components follow a
transition, and which arrangements fail before any write. Unbounded cases
include Maven property and range forms, npm and uv workspaces with their shared
locks, and local path or workspace links between components.

#### BBQ for Q08

A moving company lists which items it carries: furniture yes, the piano only
with notice, the aquarium never. Without that list, you find out on moving day.
In this picture: the moving company is the version-source engine, the listed
items are the supported internal references, the refused ones are arrangements
that fail before any write, and moving day is a release.

#### Options for Q08

- Option A (proposed boundary): support unambiguous Maven reactor references:
  the project versions of the reactor, each module's internal `<parent>`
  version and the literal version of a dependency or dependency-management
  entry whose group and artifact are a reactor module, including modules
  declared recursively by participating modules. External parents and external
  dependencies stay unchanged. Internal references written through properties
  or version ranges that the requirement does not support are rejected before
  any source write. Any participating npm or uv workspace arrangement is
  rejected before any write in v0.14.0: workspace members, shared workspace
  locks and their member entries, and local `file:`, `link:`, path or
  workspace links between participating components. Independently declared
  components with their own locks and no internal references remain supported.
  - pro: covers the known needs (my-project's `pom.xml` and `PDF/pom.xml`).
  - pro: a bounded promise; everything else fails loudly with the limitation,
    including links that carry no version.
  - con: npm and uv workspaces wait for a later item.
- Option B: Maven reactor plus npm workspaces (lock `packages["<path>"]` entries
  and dependents' exact versions) plus uv workspace members.
  - pro: broader coverage at once.
  - con: no current consumer needs it; npm ranges such as `^1.2.3` make the
    expected update ambiguous.
- Option C: Maven `<parent>` references only; any other internal reference
  fails.
  - pro: the smallest boundary.
  - con: a reactor where one module depends on another by literal version, a
    common Maven layout, would fail.

#### Recommended option for Q08 (with arguments for this choice)

Option A: it covers the real reactor layouts the consumers have, keeps the
requirement consistent with decision 39, and bounds every workspace and local
link arrangement explicitly instead of only those that carry a version.
Identification and change mechanisms stay with the design, as the umbrella
intends. (Option A completed after review round 1: recursive modules, property
and range forms, workspace locks and local links.)

#### Answer to Q08: option A (with reason why it must be accepted as the answer)

Option A: the requirement must state a boundary, and this is the smallest one
that does not break a common Maven reactor while staying explicit about every
workspace arrangement it does not support.

User decision: confirmed - Option A, as recommended: unambiguous Maven reactor
references follow the transition (the reactor's project versions, each
module's internal `<parent>` version and the literal version of a dependency or
dependency-management entry whose group and artifact are a reactor module,
including recursively declared modules), external parents and dependencies stay
unchanged, unsupported property or range forms are rejected before any source
write, every participating npm or uv workspace arrangement and every local
`file:`, `link:`, path or workspace link between participating components is
rejected before any write in v0.14.0, and independently declared components
with their own locks and no internal references remain supported. Decided by
the user on 2026-11-04 during the round 2 question explanation, with no further
comment.

### Q09: Required keys and missing files for pattern sources

Question description: a pattern source has a file, a one-group regular
expression and a form, and must match exactly one capture. The requirement
does not say whether `form` has a default, nor what happens when the declared
file does not exist in the checkout.

#### BBQ for Q09

A packing list item that says "the blue folder" is useful only if someone
notices when the blue folder is not on the shelf. Skipping it quietly means the
meeting starts without it. In this picture: the packing list is `.release.ini`,
the blue folder is the declared pattern file, the shelf is the checkout, and the
meeting is the release using that file.

#### Options for Q09

- Option A: `file`, `pattern` and `form` are all required. The declared file
  must exist and is never created. The pattern must produce exactly one
  successful match whose capture group holds a nonempty version: having one
  group in the expression is not enough, so zero matches, several matches or
  an optional group with no value fail `list`, `check` and `set` before any
  write, with an actionable diagnostic.
  - pro: no hidden default; a renamed or moved file is caught at once.
  - con: one more line per declaration.
- Option B: `form` defaults to `snapshot`; a missing file is skipped with a
  warning.
  - pro: shorter declarations.
  - con: a renamed `.env` silently stops following releases, the drift that
    exists today.
- Option C: `form` is required; a missing file is skipped with a warning.
  - pro: explicit form.
  - con: the same silent drift as option B.

#### Recommended option for Q09 (with arguments for this choice)

Option A: a project declares a pattern source precisely because that file must
follow the version, so its absence is an error, and item 1's rule that custom
declarations supply values without defaults already fits a required form.
(Capture rule and no-creation rule clarified after review round 1.)

#### Answer to Q09: option A (with reason why it must be accepted as the answer)

Option A: it turns the most likely failure, a moved file, into an immediate
diagnostic instead of a silent drift.

User decision: confirmed - Option A, as recommended: `file`, `pattern` and
`form` are all required; the declared file must exist and is never created; the
pattern must produce exactly one successful match whose capture group holds a
nonempty version, so zero matches, several matches or an optional group with no
value fail `list`, `check` and `set` before any write, with an actionable
diagnostic. Decided by the user on 2026-11-04 during the round 2 question
explanation, with no further comment.

### Q10: When an edited lock counts as consistent

Question description: the engine edits `uv.lock` and `package-lock.json`
directly and does not run the ecosystem tools during an ordinary `set`. The
requirement lists which fields change, but does not define the observable
result: whether the edited lock must also be accepted as current by the
ecosystem tool, so a later `uv sync --locked` or `npm ci` neither rewrites nor
rejects it.

#### BBQ for Q10

Changing the date on a train ticket by hand is fine only if the conductor's
scanner still accepts it. Saying "I changed only the date" does not get you on
the train. In this picture: the ticket is the lock file, the date is the root
version entry, the conductor's scanner is the ecosystem tool's lock check, and
the train is a later locked install or build.

#### Options for Q10

- Option A: for a supported format and tool version, and a manifest and lock
  pair that the tool accepted as current before the transition, the
  version-only edit keeps that acceptance (`uv lock --check`, npm lock and
  manifest agreement). It does not promise to repair unrelated dependency
  drift that existed before, a changed resolver environment, or every future
  tool version. An ordinary `set` never runs these tools opportunistically;
  the requirement's explicitly supported regeneration exception (tool
  required, changes limited and validated) still applies. The design and plans
  choose the compatibility evidence.
  - pro: defines "consistent" by the result consumers rely on.
  - pro: catches an edit to the wrong entry or a missed derived field.
  - con: evidence must follow supported tool versions over time.
- Option B: a field-level guarantee only: exactly the named fields change.
  - pro: simple to test.
  - con: no promise that the tool agrees with the result.
- Option C: the engine runs the tool's check after writing when the tool is
  present.
  - pro: live proof on every run.
  - con: adds a tool dependency and PATH discovery the umbrella avoids, and
    makes the result depend on the installed tool version.

#### Recommended option for Q10 (with arguments for this choice)

Option A: it states the outcome that matters to the consumers, limited to what
a version-only edit can honestly preserve, without bringing back the
opportunistic tool runs the requirement forbids. (Guarantee qualified and
regeneration exception preserved after review round 1.)

#### Answer to Q10: option A (with reason why it must be accepted as the answer)

Option A: a lock that the tool rejects after a version-only change of a
previously accepted pair is not a successful transition, and the requirement
should say so while leaving the evidence method to design and plans.

User decision: confirmed - Option A, as recommended: for a supported format and
tool version, and a manifest and lock pair that the tool accepted as current
before the transition, the version-only edit keeps that acceptance, without
promising to repair earlier dependency drift, a changed resolver environment or
every future tool version; an ordinary `set` never runs these tools
opportunistically, the explicitly supported regeneration exception still
applies, and the design and plans choose the compatibility evidence. Decided by
the user on 2026-11-04 during the round 2 question explanation, with no further
comment.

### Q11: Locking and concurrent version transitions

Question description: item 1 supplies a per-project operation lock. The
requirement does not say whether `versions set` holds it, over which span, how
a lifecycle caller that already holds it reuses the primitive, or whether the
read-only commands take it. Two concurrent `set` calls, or a `set` during item
5's release transaction, could interleave captures, writes and restorations.

#### BBQ for Q11

Two cooks seasoning the same pot at once each think they ruined it and each
pours some back out. Anyone can still taste from the pot while one cook works.
In this picture: the pot is the version-source set, seasoning is `versions set`
with its restoration, the cooks are concurrent transitions, and tasting is
`version`, `list` and `check`.

#### Options for Q11

- Option A: a standalone `set` holds the per-project operation lock across its
  whole operation: reading and capturing the originals, validating the
  complete set, writing and any restoration. It fails when another operation
  holds the lock. A lifecycle caller such as item 5 that already holds the lock
  runs the same primitive under its existing ownership, without refusing
  itself or releasing the lock. `version`, `list` and `check` take no lock and
  create no artifact; they may observe a transition in progress, so their
  result is not snapshot-isolated, and a `check` during a transition is not a
  release-readiness guarantee. Interfaces and the representation of ownership
  are design work.
  - pro: concurrent transitions cannot capture a stale baseline or undo each
    other's writes.
  - pro: item 5 reuses the primitive inside its own transaction.
  - pro: reads stay available during a long build or release.
  - con: a stale lock blocks `set` until item 1's stale-lock handling clears it.
- Option B: every command, reads included, takes the lock.
  - pro: reads never see a transition halfway.
  - con: blocks `gv` and `check` during a release, when they are most useful.
- Option C: no lock in this item; item 5 adds one.
  - pro: less work now.
  - con: Step 12 and a parallel `uver` can race, and one restoration can erase
    the other's writes.

#### Recommended option for Q11 (with arguments for this choice)

Option A: the lock already exists, the restoration contract is only sound when
one transition owns the files from capture to restoration, and read-only
commands gain nothing from waiting as long as their limits are stated.
(Lock span, owned-caller reuse and read limits added after review round 1.)

#### Answer to Q11: option A (with reason why it must be accepted as the answer)

Option A: it reuses item 1's foundation exactly where mutation happens, lets
item 5 call the primitive inside its own lock, and keeps read-only commands
free of side effects.

User decision: confirmed - Option A, as recommended: a standalone `set` holds
the per-project operation lock across its whole operation (capture,
validation, writes and any restoration) and fails when another operation holds
it; a lifecycle caller such as item 5 that already holds the lock runs the same
primitive under its existing ownership; `version`, `list` and `check` take no
lock and create no artifact, may observe a transition in progress, and a
`check` during a transition is not a release-readiness guarantee; interfaces
and the representation of ownership are design work. Decided by the user on
2026-11-04 during the round 2 question explanation, with no further comment.

### Q12: When restoring the original sources fails

Question description: a failed `set` restores the whole original set. The
requirement does not say what must be in place before the first overwrite so
that restoration is possible, nor what the user sees when the restoration
itself cannot complete, for example when an editor holds a file open on
Windows.

#### BBQ for Q12

When a removal van drops a box and cannot put it back on the shelf, a good crew
leaves a note saying which box is where and keeps the contents safe. Driving
off with "all done" on the clipboard is the worst outcome. In this picture: the
dropped box is a source the restoration could not rewrite, the note is the
failure report, the kept contents are copies of the original bytes, and "all
done" is a success status.

#### Options for Q12

- Option A: before overwriting any source, the original bytes and existence of
  every source in the set are recoverable; if that recovery evidence cannot be
  prepared, no source is written. When restoration cannot complete, the
  command fails with a status distinct from an ordinary failure, names each
  source not restored and where its retained original is, and never reports
  complete restoration. Evidence lives in the consuming project's artifact
  home, never in the tooling checkout. Storage, retention and interaction with
  item 5's encompassing transaction are design work.
  - pro: no silent half-state, and the original bytes survive.
  - pro: a failure to prepare evidence stops the transition before damage.
  - con: recovery evidence must exist before the first write, not only on the
    rare failure path.
- Option B: report the unrestored files only, without copies.
  - pro: no artifact.
  - con: the original bytes are lost when a partial write already replaced
    them.
- Option C: retry the restoration until it succeeds or a timeout expires.
  - pro: often recovers from a brief file lock.
  - con: can hang a non-interactive caller and still needs option A or B as
    its final outcome.

#### Recommended option for Q12 (with arguments for this choice)

Option A: the requirement promises restoration, so it must be possible before
anything is overwritten, and its failure must be visible and recoverable; the
artifact home is the existing place for such project files. (Evidence before
overwrite added after review round 1.)

#### Answer to Q12: option A (with reason why it must be accepted as the answer)

Option A: it is the only option that keeps the user's original content when
the promise of restoration cannot be kept.

User decision: confirmed - Option A, as recommended: before overwriting any
source, the original bytes and existence of every source in the set are
recoverable, and no source is written if that recovery evidence cannot be
prepared; when restoration cannot complete, the command fails with a status
distinct from an ordinary failure, names each source not restored and where its
retained original is, and never reports complete restoration; the evidence
lives in the consuming project's artifact home, never in the tooling checkout,
and storage, retention and interaction with item 5's encompassing transaction
are design work. Decided by the user on 2026-11-04 during the round 2 question
explanation, with no further comment.

### Q13: Targets supported by the shared range selector

Question description: the requirement describes the selector for preparing the
next release from HEAD. Item 4's `changelog <root> vX.Y.Z` and the release-notes
readers also need the range of an existing release, from the previous eligible
stable release to that tag. The requirement does not say whether this item's
selector covers that target, which targets are valid, what a first release
gives, whether a target can be its own predecessor, or how prefixed and
unprefixed spellings of one version are treated.

#### BBQ for Q13

A ruler that measures only from today back to the last birthday cannot tell you
how long a past year was. Handing out a second ruler for past years means two
rulers that may disagree. In this picture: the ruler is the shared range
selector, today is HEAD, a past year is the range of an existing stable
release, and the second ruler is a separate range rule inside item 4.

#### Options for Q13

- Option A: the selector takes a target, HEAD or a stable release tag, with the
  same rules. For HEAD, the baseline is the nearest eligible stable release,
  which may be a release at HEAD itself. For a release tag, the target must
  itself be an eligible stable release: a missing tag, a snapshot or other
  prerelease, or an ineligible tag such as an unvalidated one fails with a
  diagnostic. The target is never its own predecessor, and with no eligible
  predecessor the range is the full history through the target. `X.Y.Z` and
  `vX.Y.Z` on the same commit are one release boundary; on different commits
  they are conflicting tags and fail. The deterministic ancestry rule and the
  persistent eligibility evidence stay design work.
  - pro: one rule for item 4's per-release changelog and item 7's readers
    (umbrella decision 26).
  - pro: a historical range can never be built from an unvalidated release.
  - con: more cases to cover now, such as the first release and alias tags.
- Option B: HEAD only in this item; item 4 adds per-release ranges.
  - pro: smaller scope for item 2.
  - con: two range rules that can diverge, against the single shared selector.
- Option C: return the ordered list of eligible stable releases and let callers
  pick.
  - pro: flexible.
  - con: each caller re-implements "previous baseline" and its ancestry rule.
- Option D: as option A, but also accept an unvalidated stable tag as the
  target when it belongs to the caller's own active release transaction.
  - pro: lets the owning transaction regenerate notes for its own tag.
  - con: item 5 generates the release changelog before creating its tag, so no
    current caller needs it, and it mixes owned-transaction generation with
    historical range selection.

#### Recommended option for Q13 (with arguments for this choice)

Option A: the umbrella makes this item the single owner of tag classification
and range selection, and a per-release range is the same rule applied to a
different target, with the target's own eligibility checked. (Target
validation, first release, self-predecessor and alias rules, and option D,
added after review round 1.)

#### Answer to Q13: option A (with reason why it must be accepted as the answer)

Option A: it keeps one selector for every reader, as decision 26 requires,
saves item 4 from defining its own range rule, and never lets an unvalidated
release define a historical range.

User decision: confirmed - Option A, as recommended: the selector takes a
target, HEAD or a stable release tag, with the same rules; for HEAD the
baseline is the nearest eligible stable release, possibly at HEAD itself; a
release-tag target must itself be an eligible stable release, so a missing tag,
a snapshot or other prerelease, or an ineligible tag such as an unvalidated one
fails with a diagnostic; the target is never its own predecessor, and with no
eligible predecessor the range is the full history through the target; `X.Y.Z`
and `vX.Y.Z` on the same commit are one release boundary and on different
commits are conflicting tags that fail; the ancestry rule and persistent
eligibility evidence stay design work. Decided by the user on 2026-11-04 during
the round 2 question explanation, with no further comment.

### Q14: Built-in manifest and lock pairs that are absent or unsupported

Question description: the requirement lists the supported built-in pairs
(`pyproject.toml` with `uv.lock`, `package.json` with `package-lock.json`) and
restores previously absent files after a failure, but does not promise an
outcome when part of a pair is missing or unusable: a manifest without a lock,
an orphan lock without its participating manifest, or an existing lock in an
unsupported schema. It does not say whether `set` creates a lock, skips it or
refuses. Added after review round 1.

#### BBQ for Q14

A car and its spare key travel together. A car without a spare key still
drives; a spare key without its car means someone lost track of a car; and a
key cut for another model does not fit, however you push. In this picture: the
car is a participating manifest, the spare key is its lock, the missing car is
an orphan lock, and the key for another model is a lock in an unsupported
schema.

#### Options for Q14

- Option A: an absent optional lock does not participate and is never
  generated. An existing lock must pair with an identifiable participating
  manifest and use a supported, unambiguous schema; otherwise `list`, `check`
  and `set` fail before any source write. A tool-only manifest and its lock,
  excluded under Q05, stay excluded together. Q10's consistency guarantee
  applies only to supported pairs.
  - pro: supports projects without a lock file, with no dependency resolution.
  - pro: an existing release lock can never be silently left stale.
  - con: an orphan or unsupported lock needs correction before a transition.
- Option B: require a lock for every participating manifest.
  - pro: uniform, lock-backed releases.
  - con: rejects legitimate projects without a lock file and adds a requirement the
    umbrella does not state.
- Option C: skip any unusable lock with a warning.
  - pro: tolerant of unusual layouts.
  - con: can report a successful transition while an existing release lock
    keeps the old version.

#### Recommended option for Q14 (with arguments for this choice)

Option A: it follows the umbrella's rules that only the supported lock entries
are edited and that no lock is regenerated opportunistically, while keeping the
atomic promise for every lock that actually exists.

#### Answer to Q14: option A (with reason why it must be accepted as the answer)

Option A: it treats a missing lock as a normal project layout and every
unusable existing lock as an error, which is the only way no participating
lock is left behind.

User decision: confirmed - Option A, as recommended: an absent optional lock
does not participate and is never generated; an existing lock must pair with an
identifiable participating manifest and use a supported, unambiguous schema,
otherwise `list`, `check` and `set` fail before any source write; a tool-only
manifest and its lock, excluded under Q05, stay excluded together; and Q10's
consistency guarantee applies only to supported pairs. Decided by the user on
2026-11-04 during the round 2 question explanation, with no further comment.

### Q15: Maven version property forms supported in v0.14.0

Question description: the Q08 decision makes literal internal dependency and
dependency-management versions follow the transition and rejects "unsupported
property or range forms", but names no supported property form. The body says
"Supported reactor version properties are handled explicitly; others are
rejected", and AC6 rejects "unsupported Maven property indirection". A reactor
whose project version is `${revision}`, or whose internal dependency version is
`${project.version}`, therefore has no defined outcome. This question settles
which property expressions, if any, may appear in participating project
versions, internal `<parent>` versions and internal dependency or
dependency-management versions in v0.14.0. Q08's other boundaries stay as
decided: inherited project versions stay inherited, version ranges stay
rejected, and external versions and properties stay unchanged. How expressions
are identified is design work. The known Maven consumer, my-project, states
literal values in its project and `<parent>` version fields; its
`${project.version}` appears only inside a plugin configuration value, which is
not a version field this question covers. Added after review round 3.

#### BBQ for Q15

Before a street is renumbered, a painter renews the number on every door. Most
doors carry a painted number, which the painter repaints. Some carry a plate
reading "same number as the street sign": they never need paint and always
match. A few carry a plate reading "see the note in the hall": the painter must
find that note and change it, and may miss one. In this picture: the painter is
the version-source engine, a painted number is a literal Maven version, the
"same as the street sign" plate is `${project.version}` in an internal
dependency, and the note in the hall is a property such as `${revision}`
defined elsewhere.

#### Options for Q15

- Option A: literal versions only. Every participating project version
  (unless inherited), internal `<parent>` version and internal dependency or
  dependency-management version must be a literal value. A property expression
  in any of these fields fails before any source write, naming the file, the
  field, the expression and the limitation. No property form joins the
  supported boundary in v0.14.0.
  - pro: the smallest boundary, with no property handling at all.
  - pro: covers my-project, whose version fields are literal.
  - con: a reactor whose internal dependencies use `${project.version}`, a
    common Maven idiom that already stays in step, must convert them to
    literals, which the engine then rewrites at every transition.
  - con: `${revision}` reactors need manual conversion or a later item.
- Option B: literal versions, plus `${project.version}` accepted only as the
  entire internal dependency or dependency-management version in a supported
  reactor. It stays unchanged and follows the owning project's effective Maven
  version, which under the Q06 decision is the same expected Maven version as
  the participating target module: it follows the transition with no write.
  All participating project and internal `<parent>` version fields remain
  literal or inherited as applicable. Every other expression in the covered
  fields fails before any source write as in option A, including
  `${project.version}` as a project or `<parent>` version, `${revision}`,
  composite expressions and project-defined properties.
  - pro: accepts the common sibling-reference idiom without editing it and
    without resolving any property.
  - pro: covers my-project, and still rejects every property the engine would
    have to rewrite.
  - con: one more accepted case for detection to recognize and tests to cover.
  - con: `${revision}` reactors still need manual conversion or a later item.
- Option C: option B plus Maven CI-friendly versions: a `${revision}` project
  and `<parent>` version, optionally combined with `${sha1}` and
  `${changelist}`, defined once as a property in the root POM, which the
  engine rewrites; any other definition location or expression fails before
  any source write.
  - pro: supports CI-friendly reactors without conversion.
  - con: no current consumer needs it; definitions in `.mvn/maven.config`,
    profiles or command lines make the expected write ambiguous, and published
    POMs then depend on flattening, which this item does not own.
  - con: needs further boundary decisions before design can start.

#### Recommended option for Q15 (with arguments for this choice)

Option B: the engine still writes only literal versions and resolves no
property, as Q08 decided, while accepting the one expression that cannot go
stale under the Q06 single version. Option A would fail reactors that are
already consistent and replace a self-maintaining reference with literals the
engine must rewrite. Option C adds decisions no consumer has asked for. The
round 3 reviewer proposed option A; option B differs from it only for
`${project.version}` in internal dependency and dependency-management
versions.

#### Answer to Q15: option B (with reason why it must be accepted as the answer)

Option B: every property the engine would need to rewrite is still rejected,
and the only accepted expression is one that Maven itself resolves to the
transition's version.

User decision: confirmed - Option B, as recommended: participating project
versions and internal `<parent>` versions are literal or inherited;
`${project.version}` is accepted only as the entire internal dependency or
dependency-management version in a supported reactor, stays unchanged and
follows the shared version under Q06; every other expression in these fields,
including `${revision}`, composite expressions and project-defined properties,
fails before any source write; ranges stay rejected and external versions and
properties stay unchanged, as Q08 decided. Decided by the user on 2026-11-05
during the round 4 question explanation, with no further comment.
