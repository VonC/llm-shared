# Provision pinned git-cliff automatically

- Type: feature-request
- Test group: whole suite
- Target version: v0.14.0
- Slug: git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md

## Draft basis and user need for git-cliff provisioning

As a maintainer who renders a generated changelog or runs a generated release
with the llm-shared release tooling, I need the exact git-cliff version my
project expects to be available without installing it, finding it or even
knowing it is a dependency. A missing or unusable binary must stop generated
work with a precise setup diagnostic before anything in my project changes,
while every operation that does not render a changelog keeps working.

The [focused draft](draft.v0.14.0.git-cliff-provisioning.md) derives from item
3 of the [sibling release tooling umbrella](draft.v0.14.0.sibling_release_tooling.md)
and was approved on 2026-11-13. It gathers the umbrella contracts on the
internal cache and downloader, the exact pin, the compatibility research from
2.7.0 to 2.14.2, the fixed `GIT_CLIFF` value, the `gcliff` launcher and alias,
concurrency and integrity checks, and the dependency-specific preflight errors
(umbrella decisions 17 to 21 and confirmed answer Q1 A). This requirement
records those outcomes without choosing their implementation.

## Current behavior before git-cliff provisioning

- dev_workflow's `uc` alias (`tools/dev_workflow/init.bat`) runs
  `update-changelog.bat`, which starts `bash` on `update-changelog.sh`. That
  script invokes `${PRGS}/git-cliffs/current/git-cliff.exe` with
  `-c cliff.toml -w <PRJ_DIR> -s footer -o CHANGELOG.tmp.md`, first printing
  its version with `-V`. The output is then cleaned with sed, awk and Perl.
- That binary comes from global senv. The one observed here is
  `git-cliff-2.7.0-x86_64-pc-windows-msvc`, selected through a `current`
  directory. Nothing pins, checks or downloads a version: a missing binary
  fails inside `bash` at its first call, after the alias has started.
- Item 1, `release-project-root`, is completed and merged. It supplies the
  explicit validated project root, root-scoped Git, dispatch through the
  self-locating `bin/release_workflow.bat` and `bin/release_alias.bat`, the
  Windows x64 runtime check, and the common `.release.ini` reader, read with
  interpolation off, that composes explicitly registered domain schemas and
  validates every declared setting before mutation. It names this item's
  managed binary cache as the one distinct permitted write area inside the
  tooling checkout.
- Item 2, `version-sources`, is completed and merged. It ships the `version`
  and `versions` operations and the shared stable/snapshot tag classifier and
  range selector that git-cliff input will use. Configuring git-cliff with that
  selector is item 4's work.
- The release engine has no git-cliff code. Its shipped schemas are `tooling`
  and `version`, so a `[git-cliff]` section is reported today as an unknown
  configuration section, and a git-cliff executable key under `[tooling]` is
  rejected as an unknown key.
- llm-shared ships no `bin/gcliff.bat` launcher, and its alias set
  (`senv.doskey`) defines no `gcliff` alias.
- llm-shared's `.gitignore` has no entry for `.tools/git-cliff/`. Its generic
  `*.exe`, `*.zip` and `*.lock` patterns cover some of the files a cache would
  hold, but other files placed there, such as an extracted text file or a
  digest record, would appear as untracked.

## Scope and ownership boundaries of git-cliff provisioning

This item owns pin resolution, asset selection, download, integrity and version
checks, the cache and its locks, direct invocation, and the shared resolver
behind the `gcliff` launcher and alias. It registers the `[git-cliff]`
configuration section with the common reader.

The neighboring behaviors stay with their items:

| Umbrella item | Behavior owned by that item |
| --- | --- |
| 4, changelog-management | When rendering needs git-cliff, `cliff.toml`, header, ranges, fix rules and archives, and the preflight ordering before automatic `fixes init` |
| 5, build-release-lifecycle | Calling provisioning in generated release `pre` before project writes |
| 6, release-tooling-setup | Exposing the aliases in a consumer's setup; proposing a newer tested pin with its diff |
| 7, prepare-release-integration | `/prepare-release` Steps 10 and 11 calling the changelog services |
| 8, llm-shared-cutover | llm-shared's own `.release.ini` pin, exposed aliases and parity rehearsals |

The cache layout below the fixed path, the lock mechanism, the download client,
the archive extraction method, the digest source and the exact output formats
and exit-code numbers remain design work.

## Version notation for the git-cliff pin

| Context | Form | Example |
| --- | --- | --- |
| git-cliff pin in `.release.ini` and the cache directory | `X.Y.Z`, without `v` | `2.14.2` |
| Upstream GitHub release tag | `vX.Y.Z` | `v2.14.2` |

The pin follows the umbrella notation rule (decision 31): a value that sets a
version never includes `v`; an upstream tag keeps its actual spelling.

## Exact pin resolution from the project configuration

Read an exact `[git-cliff] version` from the consuming project's
`.release.ini`, or use the tested llm-shared default when it is omitted. The
proposed default is 2.14.2, subject to the compatibility checks below.

```ini
[git-cliff]
; exact version to download automatically into llm-shared's ignored cache
version = 2.14.2
```

- The pin belongs to internal provisioning. The common reader validates it with
  every other declared setting, before mutation, including for operations that
  never need git-cliff.
- No executable key exists in `.release.ini`: llm-shared computes the fixed
  internal path, and no consumer runs code from project configuration.
- Within a project, the pin comes from that project; outside one, the
  llm-shared default applies.
- Never resolve a floating `latest`. A later upgrade is a deliberate pin change
  with compatibility evidence (umbrella decision 19).

## Internal versioned cache for the git-cliff binary

The fixed location for one pin and platform is:

```text
<LLM_SHARED_DIR>/.tools/git-cliff/<version>/<platform>/git-cliff.exe
```

- The cache is ignored in llm-shared Git as a whole, so no provisioning file
  can appear as untracked or join a commit.
- Versioned directories let consumers with different pins share one llm-shared
  clone.
- Cache writes are the explicit exception to keeping consumer temporary state
  out of llm-shared. Consumer transaction state never goes into the tooling
  checkout.
- The cache has its own provisioning locks, separate from the per-project
  release operation lock. Linked-worktree Git metadata and this tooling cache
  keep distinct boundaries.

## Direct invocation through GIT_CLIFF and the gcliff launcher

- `GIT_CLIFF` is a launcher-local value computed from the internal path, not an
  external override. No PATH, `PRGS`, global-senv, alias or machine
  installation discovery is performed (umbrella decision 20).
- Invoke the absolute executable directly. Leave the parent's PATH and
  environment unchanged.
- llm-shared supplies `bin/gcliff.bat` and the `gcliff` alias in its alias set,
  both using the same resolver and downloader as the engine.
- The alias is available to every user who loads llm-shared aliases, including
  without global senv (umbrella decision 17). Scripts call the launcher
  directly, since doskey aliases do not expand in subprocesses.
- Within a project, the launcher and alias use its pin; outside one, they use
  the llm-shared default.

## Provisioning sequence before generated changelog work

1. Check the selected cache path and the executable's version. Reuse a valid
   copy without network access.
2. If it is absent or invalid, obtain the matching OS and architecture release
   asset from `orhun/git-cliff` on GitHub, verify its published integrity
   information, and extract it safely into a unique temporary cache directory.
3. Validate `--version`, then publish the cache entry atomically under a
   per-version and per-platform lock. Concurrent releases must not consume a
   partial install or replace a binary another release is using.
4. If the fixed binary still cannot be made available, stop with the requested
   version, the internal path and the download, verification or execution
   diagnostic. Explain the llm-shared setup, network or permission failure; do
   not ask the user to install git-cliff or change PATH.

An interrupted download leaves no entry that a later run accepts as valid. A
valid cached binary needs no network; a missing one with no network fails with
the step 4 diagnostic.

### Integrity data for each git-cliff release asset

The supported platform contract defines the integrity check for each asset; do
not assume every asset has a `.sha512` sidecar. For example, 2.14.2 lists those
for tarballs but not for Windows ZIPs; the inspected x86_64 MSVC ZIP has a
SHA-256 digest in GitHub's asset metadata. Verify that digest where it is
available. Missing verification data is an explicit setup failure, never a
reason to skip the check.

## Operations that need the provisioned binary

Provisioning occurs before any consuming-project managed-file, index, commit or
tag mutation. Generated mode means only that changelog text is rendered from
Git commits using git-cliff; it is not a separate version or release lifecycle.

| Operation | Needs the provisioned binary |
| --- | --- |
| `changelog` in generated mode, including `uc` | Yes |
| Generated release `pre` | Yes |
| The `gcliff` launcher and alias | Yes |
| `version`, `versions list`, `versions set`, `versions check` | No |
| `snapshot`, which does not regenerate a changelog | No |
| Ordinary builds | No |
| Curated-mode validation and curated release builds | No |
| Fix-rule conversion; `fixes dry-run`, which uses existing text | No |

`uc`, `uvf` and release-note preparation run the git-cliff preflight before
automatic `fixes init`, so a missing tool cannot leave a newly created rule file
behind. That ordering belongs to item 4; this item supplies the provisioning
those callers run first.

When llm-shared sits beside the project, the umbrella states:

| Situation | `b` (build) | `brel` / `br` | `gv`, `uc`, `uver`, `uvf` |
| --- | --- | --- | --- |
| Pinned git-cliff absent from the internal cache | Builds | Generated `br`/`brel` downloads and verifies it automatically before project mutation; curated release builds need none | Generated `uc` does the same; version and snapshot commands and curated validation need no binary |
| Internal git-cliff unavailable and download or verification fails | Builds | Generated release fails with the internal path, version and setup or network diagnostic; curated release builds work | Generated `uc` fails; version commands and curated validation remain available |

All release entries still require `main` and the readiness gates (item 5).

## Supported platform for git-cliff provisioning

The v0.14.0 release tooling supports Windows x64 only initially, covering
git-cliff provisioning among the other parts (confirmed answer Q1 A). Other
operating systems and architectures require later scope; existing Unix
deployment references do not extend this support. An unsupported platform
receives a clear scope diagnostic before project mutation.

## Failure when git-cliff provisioning cannot supply the binary

Attempt automatic provisioning first. If it cannot supply the binary, fail
generated work before project mutation with an internal setup or download
diagnostic naming the requested version and the internal path; other
operations remain usable (umbrella decision 21). Never require a manual
git-cliff installation or a PATH change.

## Compatibility of the 2.14.2 pin with the observed 2.7.0

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

### Pinning policy options for git-cliff

| Pinning policy | Pros | Cons |
| --- | --- | --- |
| Exact `version = 2.14.2` in `.release.ini` (recommended for this cutover) | Reproducible binary, recent worktree/Windows/range fixes, automatic first-use install, reviewable upgrades | Newer parser/default behavior can change output; compatibility fixtures and a deliberate later pin update are required |
| Retain exact `2.7.0` temporarily | Closest comparison with the observed old tooling | Misses subsequent fixes/features; requires a second tested compatibility target if supported beyond migration evidence |
| Floating `latest` on each run | Gets new upstream changes without editing config | Output and CLI behavior can change without project review; network dependence and hard-to-reproduce releases; rejected |

Use 2.14.2 as the proposed initial pin and test the real llm-shared header,
template, parser and skip rules, snapshot-tag history and archive ranges
against it. Document intentional differences from 2.7.0 before cutover. Later
setup and upgrade checks (item 6) can propose a newer tested exact pin with its
diff; ordinary release runs never silently move the pin. The 2.14.2 pin is a
researched recommendation, not a claim that binary compatibility has been
validated, and the upstream check above dates from 2026-10-09.

## Consumer inputs shaping git-cliff provisioning

These repositories shape the need. Their own migrations stay in their own
efforts; llm-shared's belongs to item 8.

- llm-shared: generated changelog with 2 fix rules. Its cutover creates
  `.release.ini` with the exact git-cliff pin, ignores the internal
  `.tools/git-cliff/` cache, and exposes `gcliff` with the other aliases.
  Parity rehearsals against dev_workflow accept approved git-cliff output fixes
  as documented intentional differences.
- my-project: generated changelog with 32 fix rules, so it needs the
  provisioned binary for `uc` and generated releases.
- workspace-halo: its hand-written, marketplace-style `CHANGELOG.md` uses the
  `curated` mode, so it never needs git-cliff.

## Gap to close in the implementation for git-cliff provisioning

1. Register a `[git-cliff]` domain schema with the common reader: an exact
   `version` in `X.Y.Z` form, validated before mutation, with the tested
   llm-shared default when it is omitted. Keep rejecting any executable key.
2. Compute the fixed internal path for the resolved pin and the supported
   platform, and ignore `.tools/git-cliff/` in llm-shared Git as a whole.
3. Reuse a valid cached binary offline; otherwise select, download, verify,
   extract and atomically publish the matching release asset under a
   per-version and per-platform lock that tolerates concurrent users and
   interrupted downloads.
4. Report the requested version, the internal path and the precise setup,
   network, verification or execution failure when provisioning cannot supply
   the binary, before any consuming-project mutation.
5. Diagnose unsupported operating systems and architectures before project
   mutation.
6. Ship `bin/gcliff.bat` and the `gcliff` alias on the shared resolver, using
   the project pin inside a project and the llm-shared default outside one,
   without changing the parent environment.
7. Expose the provisioning entry point that items 4 and 5 call before
   generated changelog work, while keeping every operation that does not need
   git-cliff free of it.
8. Establish tested compatibility for the 2.14.2 pin with real templates,
   parsers and histories, and record the intentional differences from 2.7.0.

## Acceptance criteria for git-cliff provisioning

- Read an exact project or default pin, compute its ignored internal version
  and platform path, and reuse a valid cached binary without network. No
  executable override, PATH search or mutation, `PRGS` or senv dependency.
- Automatically download the correct GitHub release asset when it is absent or
  invalid, verify its integrity and version, extract it safely and publish it
  atomically under a cache lock; handle concurrent users, interrupted downloads
  and offline use. Support Windows x64 only initially and diagnose other
  platforms before project mutation.
- Report the internal path and pin, and the precise setup, network or
  verification failure, when provisioning cannot supply the binary. Never
  require a manual git-cliff installation. Do this before any consuming-project
  managed-file or Git mutation.
- The direct launcher and the interactive `gcliff` alias share provisioning;
  scripts do not depend on doskey expansion. Inside a project use its pin,
  outside use the llm-shared default; leave the parent's environment
  unchanged.
- Establish tested compatibility for the proposed exact 2.14.2 pin using real
  templates, parsers and histories. Record the intentional differences from the
  observed 2.7.0; no floating latest and no silent pin upgrade at release time.
- Version operations, ordinary builds, curated validation and fix conversion
  remain available without provisioning; cache state never joins a commit.

## Code references for git-cliff provisioning

- `tools/release_workflow/schemas.py`: `SHIPPED_SCHEMAS` holds the `tooling`
  and `version` domains; this item adds the git-cliff domain to that explicit
  manifest.
- `tools/release_workflow/configuration.py`: the common `.release.ini` reader,
  with interpolation off, that rejects unknown sections and keys before
  mutation.
- `tools/release_workflow/bootstrap.py`: the Windows x64 runtime check item 1
  ships.
- `tools/release_workflow/cli.py`: `SHIPPED_HANDLERS`, today only `version` and
  `versions`.
- `bin/release_workflow.bat` and `bin/release_alias.bat`: the self-locating
  launchers a `bin/gcliff.bat` sits beside.
- `senv.doskey`: llm-shared's alias set, loaded with `doskey /MACROFILE`,
  where the `gcliff` alias belongs.
- `.gitignore`: generic `*.exe`, `*.zip` and `*.lock` patterns, no
  `.tools/git-cliff/` entry yet.
- `tests/unit/tools/release_workflow/test_configuration/test_configuration_tdd.py`:
  already rejects a git-cliff executable key under `[tooling]`.
- `tools/dev_workflow/update-changelog.sh`, `update-changelog.bat`, `init.bat`
  and `cliff.toml`: the legacy invocation through `PRGS` and the `uc` alias
  this item's provisioning replaces.

## Open questions for the v0.14.0 git-cliff-provisioning feature request

### Q01: Pins a project may declare in .release.ini

Question description: the requirement accepts an exact `[git-cliff] version`
in `X.Y.Z` form and states that the 2.14.2 default must have tested
compatibility. It does not say whether a project may declare an exact version
that llm-shared never tested, such as `2.10.0` or a later `2.15.0`, nor what
happens when it does. The pinning-policy table also mentions keeping `2.7.0`
temporarily, which "requires a second tested compatibility target". Checked on
2026-11-13, the 2.7.0 Windows x64 ZIP has neither a GitHub asset digest nor a
`.sha512` sidecar, so the integrity rule alone already keeps 2.7.0 from being
a production pin. Obtaining a version only to gather evidence (the 2.7.0
comparison target, or 2.14.2 before its evidence is recorded) is a separate
step from admitting it as a pin; Q13 and Q16 cover it.

#### BBQ for Q01

A grill shop sells propane regulators. It can fit any regulator the customer
names, or only the models it has pressure-tested on its own grills. Fitting
anything is flexible, but the first leak shows up at the customer's barbecue,
not in the shop. In this picture: the grill shop is llm-shared, the customer's
named regulator is a project's `[git-cliff] version`, the pressure-tested models
are the pins with recorded compatibility evidence, and the leak is changed
changelog output discovered during a release.

#### Options for Q01

- Option A: accept any exact `X.Y.Z` that has a supported-platform release
  asset; verify it like the default, with no compatibility guarantee.
  - pro: a project can try a newer git-cliff without waiting for an
    llm-shared release.
  - con: generated releases can run with an untested renderer whose output
    differences nobody reviewed.
  - con: each untested pin still needs integrity data the platform contract
    defines, so "any version" can fail late, at first download.
- Option B: accept only the pins llm-shared records as tested (the default and
  any other version with recorded evidence); refuse another pin before
  mutation with a diagnostic listing the tested pins. Candidates used to
  gather that evidence are obtained the same way and are not admitted as pins
  until their evidence is recorded; they are verified the same way too,
  except for the evidence-only exception Q16 proposes for 2.7.0.
  - pro: every generated changelog comes from a renderer whose differences
    were reviewed. This is stricter than decision 19, which asks for evidence
    before cutover and deliberate upgrades but does not itself restrict
    project pins.
  - pro: gathering evidence for a candidate never requires that evidence to
    exist already.
  - pro: matches item 6's role of proposing "a newer tested exact pin with its
    diff" instead of letting projects drift.
  - con: trying a new git-cliff version requires an llm-shared change first.
- Option C: accept any exact pin, but warn on each run when it is outside the
  tested set.
  - pro: flexible and still visible.
  - con: warnings in automated `/prepare-release` runs are easily ignored, and
    the release still uses unreviewed output.

#### Recommended option for Q01 (with arguments for this choice)

Option B: the pin exists to make generated releases reproducible and reviewed.
Restricting it to tested versions keeps that promise for every consumer, and
item 6 already provides the deliberate path for adding a newer tested pin. The
`gcliff` launcher applies the same rule, since it shares the resolver. This is
a proposed restriction, not one decision 19 already mandates, and it leaves
evidence runs free to obtain an untested candidate.

#### Answer to Q01: option B (with reason why it must be accepted as the answer)

Option B: it extends decision 19 ("prove compatibility before cutover; later
upgrades are deliberate pin changes") into a checked rule for every project
pin, a restriction the decision itself does not impose. The refusal happens
before mutation, with the list of accepted pins in the diagnostic.

User decision: confirmed: option B, only tested pins are accepted, selected by
the user on 2026-11-13 without amendment. A pin outside the tested set is
refused before mutation with the tested pins listed; evidence candidates (Q13,
Q16) are obtained outside that admission.

### Q02: Omitted pin when the llm-shared default changes

Question description: a project that omits `[git-cliff] version` uses the
llm-shared default. When a later llm-shared release changes that default, the
project's git-cliff version changes with the tooling update, without any edit
to the project. The requirement says "no silent pin upgrade at release time"
but does not say whether this inherited change counts as one.

#### BBQ for Q02

A restaurant serves the "house wine" unless the guest orders a specific bottle.
When the restaurant changes its house wine, regulars who never ordered by name
get a different wine. Whether that is acceptable depends on whether the menu
announced the change. In this picture: the house wine is llm-shared's default
pin, the specific bottle is an explicit `[git-cliff] version`, the regulars are
projects that omit the pin, and the menu announcement is the tooling upgrade
that brings the new default.

#### Options for Q02

- Option A: an omitted pin follows the tested default of the executing
  llm-shared checkout, while an explicit pin survives a tooling update as long
  as it stays in the tested set (Q01). Changing the default is itself a
  reviewed llm-shared change with its compatibility evidence, and item 6's
  upgrade workflow reports a changed default when the user upgrades through it.
  - pro: keeps decision 1: a project omits settings whose defaults suit it,
    and a release user need not know git-cliff exists.
  - pro: the version never moves during a release; it moves only when the
    executing checkout changes.
  - con: an ordinary checkout update, such as a `git pull` in llm-shared, does
    not necessarily pass through item 6's workflow, so the next release can
    render differently without a report.
  - con: the project's own history does not record which git-cliff version
    rendered each release.
- Option B: generated mode requires an explicit pin in `.release.ini`; the
  default applies only to `gcliff` outside a project.
  - pro: each project records its renderer version in its own history.
  - con: contradicts decision 1 and the goal that a release user need not know
    the dependency exists; every generated-mode project needs setup edits.
- Option C: the first generated run records the resolved default into the
  project's `.release.ini`.
  - pro: records the version without asking the user.
  - con: a release command that edits project configuration on its own is a
    hidden mutation, which the umbrella rules out.

#### Recommended option for Q02 (with arguments for this choice)

Option A: the version moves only when the executing llm-shared checkout
changes, never in the middle of a release. Item 6's upgrade workflow shows that
change when the user upgrades through it, but an ordinary checkout update is
not guaranteed to go through that workflow. Projects that want a fixed renderer
across tooling updates declare the pin explicitly, as llm-shared itself will at
cutover.

#### Answer to Q02: option A (with reason why it must be accepted as the answer)

Option A: it keeps the zero-configuration default the umbrella promises, ties
a default change to a reviewed llm-shared change rather than to a release run,
and leaves projects that need stability a one-line explicit pin.

User decision: confirmed: option A, an omitted pin follows the executing
checkout's tested default, selected by the user on 2026-11-13 without
amendment. An explicit pin survives tooling updates while it stays in the
tested set (Q01 B); a plain checkout update can change the default without an
item 6 report.

### Q03: What makes a cached git-cliff binary valid for reuse

Question description: provisioning reuses "a valid copy without network
access" and replaces one that is "absent or invalid". The requirement checks
the executable's version, but does not say whether a copy that reports the
right version yet differs from the verified download (corrupted, replaced or
edited after publication) counts as valid, nor in which order the checks run.
Two kinds of integrity data are involved: the archive digest, checked against
upstream data once at download time, and an integrity record of the extracted
executable, kept locally when the cache entry is published.

#### BBQ for Q03

A pantry jar labeled "smoked paprika" is reused for every barbecue. Checking the
label is quick; checking that the contents still match what was bought takes
a sniff each time. A label alone cannot tell that someone refilled the jar with
chili powder. In this picture: the jar is the cached `git-cliff.exe`, the label
is its `--version` output, the sniff is comparing the binary with the integrity
data recorded at publication, and the refill is a modified or corrupted binary.

#### Options for Q03

- Option A: first verify the cached executable against its locally recorded
  integrity data, and only then run its `--version`, which must report the
  pin. A missing or mismatching local record makes the entry invalid.
  - pro: detects corruption and replacement, not only a wrong version, and
    never runs a changed executable, even for the version check.
  - pro: the check stays offline, since it uses data recorded at publication.
  - con: hashing the binary costs a little time on each use.
- Option B: valid means `--version` reports the pin.
  - pro: simplest and fastest check.
  - con: a modified binary that still prints the right version is reused
    silently, and a changed executable runs before anything can reject it,
    which undermines the download-time verification.
- Option C: valid means the file exists.
  - pro: no process launch at all.
  - con: a truncated or wrong binary fails later, inside rendering, with a
    worse diagnostic.

#### Recommended option for Q03 (with arguments for this choice)

Option A: the requirement verifies the archive at download time, and only
option A keeps that guarantee for every later use. The order matters: the
version check runs the executable, so a changed copy must be rejected before it
runs. The cost is one hash of a single binary per provisioning check, which is
small next to rendering a changelog. How the local record is stored and which
hash it uses remain design work. The local record detects divergence from what
was published; it does not defeat a coordinated replacement of both the record
and the binary.

#### Answer to Q03: option A (with reason why it must be accepted as the answer)

Option A: it makes "valid" mean "the binary that was verified", so an invalid
copy is replaced (or reported offline) before it ever runs, instead of
rendering a release with an unknown executable.

User decision: confirmed: option A, verify the local integrity record first,
then require `--version` to report the pin, selected by the user on 2026-11-13
without amendment. A missing or mismatching local record invalidates the entry
before it runs.

### Q04: Cache scope across llm-shared checkouts and unwritable checkouts

Question description: the cache path is `<LLM_SHARED_DIR>/.tools/git-cliff/...`.
A user can have several llm-shared checkouts or linked worktrees (for example a
main checkout and a feature worktree), and an llm-shared checkout can be
read-only for the current user. The requirement does not say whether each
checkout keeps its own cache, or what happens when the cache cannot be written.

#### BBQ for Q04

Each grill in a backyard has its own small charcoal bin. Sharing one central
bin saves charcoal, but then every grill depends on that one bin being open and
stocked. And a grill whose bin is locked cannot cook unless it may borrow from
the neighbor's. In this picture: each grill is an llm-shared checkout or
worktree, its charcoal bin is its `.tools/git-cliff/` cache, the central bin is
a shared cache outside the checkout, and the locked bin is a checkout the user
cannot write to.

#### Options for Q04

- Option A: each executing checkout uses only its own `.tools/git-cliff/`
  cache, with no cross-checkout or per-user fallback; when a write that
  provisioning needs is denied, the setup diagnostic names the path and the
  permission failure.
  - pro: matches the fixed internal path and decision 7 (the selected checkout
    actually executes, self-contained).
  - pro: no cross-checkout locks or shared state to reason about.
  - con: each worktree downloads the same binary once.
- Option B: linked worktrees share the main checkout's cache.
  - pro: one download per clone.
  - con: a worktree then writes into another checkout, against the item 1
    boundary between linked-worktree metadata and the tooling cache.
- Option C: fall back to a per-user cache (such as under the user profile)
  when the checkout is unwritable.
  - pro: works for a read-only shared llm-shared installation.
  - con: introduces a second location, contradicting the single fixed path of
    decision 20, and splits diagnostics between two places.

#### Recommended option for Q04 (with arguments for this choice)

Option A: the cost is one extra download per checkout, while the gain is a
single, predictable location per executing checkout. A denied write fails with
a diagnostic that names the path needing write access. This requirement does
not promise that a read-only checkout either works or fails as a whole: that
depends on which lock or validation writes reusing an existing entry needs,
which the design decides.

#### Answer to Q04: option A (with reason why it must be accepted as the answer)

Option A: it keeps decisions 7 and 20 intact (one fixed path inside the
executing checkout) and turns a denied write into the step 4 setup diagnostic
instead of a hidden fallback.

User decision: confirmed: option A, each executing checkout uses only its own
`.tools/git-cliff/` cache with no cross-checkout or per-user fallback, selected
by the user on 2026-11-13 without amendment. A denied required write fails with
the setup diagnostic naming the path; read-only reuse is left to the design.

### Q05: Which item makes the git-cliff cache ignored

Question description: the gap list asks this item to ignore
`.tools/git-cliff/` in llm-shared Git, while the consumer input for llm-shared
says its cutover (item 8) "ignores the internal `.tools/git-cliff/` cache".
Today only the generic `*.exe`, `*.zip` and `*.lock` patterns cover part of it.
Once this item's downloader exists, any developer or test run can populate the
cache before item 8 lands.

#### BBQ for Q05

The new smoker arrives before the shed is built. If the shed comes months
later, the smoker sits in the driveway in the meantime, where everyone trips
over it. In this picture: the smoker is the git-cliff cache, the shed is the
ignore rule, the driveway is `git status` showing untracked cache files, and
"months later" is the time between item 3 and the item 8 cutover.

#### Options for Q05

- Option A: item 3 guarantees the cache is ignored from its first write, in
  every llm-shared checkout; item 8 only verifies it.
  - pro: no window in which cache files show as untracked or can be staged.
  - pro: satisfies the acceptance criterion "cache state never joins a commit"
    within the item that creates the state.
  - con: the umbrella's consumer-input wording for item 8 needs an
    authorized correction.
- Option B: item 8 adds the ignore rule at cutover.
  - pro: groups llm-shared's own configuration changes in one place.
  - con: until then, development and test runs leave untracked files that a
    broad `git add` can commit.

#### Recommended option for Q05 (with arguments for this choice)

Option A: the item that writes the cache owns keeping it out of Git. The
mechanism (a root `.gitignore` entry or a self-ignoring cache directory)
remains design work. The requirement keeps its recorded source wording for
now; the umbrella's llm-shared consumer bullet, which gives the ignore rule to
the cutover, is flagged for reconciliation once the user decides, and is not
edited without that authorization.

#### Answer to Q05: option A (with reason why it must be accepted as the answer)

Option A: it closes the window between this item and the cutover, and it makes
the existing acceptance criterion testable in this item.

User decision: confirmed: option A, item 3 guarantees the cache is ignored from
its first write in every checkout and item 8 only verifies it, selected by the
user on 2026-11-13 without amendment, after a worked example (untracked cache
files, `git add -A` and clean-tree checks between items 3 and 8). The umbrella
llm-shared consumer bullet is flagged for authorized reconciliation.

User comment (2026-11-13): umbrella items land on `sibling_release_tooling`,
and main receives the umbrella only after all items are developed, so the
untracked-cache window concerns the umbrella branch and its worktrees; any
change reaching main before then is unlikely. The decision stands.

### Q06: Waiting on a held provisioning lock and recovering a stale one

Question description: publication happens "under a per-version/platform
lock", and the acceptance criteria require handling "concurrent users,
interrupted downloads". The requirement does not say what a second caller
does while another one downloads (wait, and for how long, or fail at once),
nor what happens when the lock holder died, leaving the lock behind.

#### BBQ for Q06

Two neighbors want the one shared grill. The second can wait for the first to
finish, leave immediately, or wait forever. And if the first neighbor went home
and left the lid down with a "busy" sign, someone must decide when the sign no
longer counts. In this picture: the grill is the cache entry for one pin and
platform, the "busy" sign is the provisioning lock, the second neighbor is a
concurrent `uc`, release or `gcliff` call, and the neighbor who went home is a
crashed or interrupted provisioning process.

#### Options for Q06

- Option A: a second caller waits for the holder, reporting that it waits,
  up to a bounded time, then fails with a diagnostic naming the lock and its
  holder. A lock is recovered automatically, and its partial download
  discarded, only once its holder is established to be no longer running; the
  lock's age alone never proves that, and recovery never removes a temporary
  installation that a live caller still owns.
  - pro: two releases started together both succeed after one download,
    provided it completes within the waiting caller's budget.
  - pro: a crash never requires manual cleanup.
  - con: a bounded wait needs a documented limit that suits slow networks.
  - con: this bounds only the waiting caller; the holder's own download or
    version check needs its own bound (Q15).
- Option B: a second caller fails at once while the lock is held.
  - pro: simple, never hangs.
  - con: two parallel projects on one llm-shared clone fail spuriously on
    first use; the user must rerun.
- Option C: wait without limit; stale locks need manual removal.
  - pro: no timeout to choose.
  - con: a crashed holder blocks every generated release until someone finds
    and removes the lock by hand, a manual repair the requirement otherwise
    avoids.

#### Recommended option for Q06 (with arguments for this choice)

Option A: concurrent first use is the expected case once several projects share
one llm-shared clone, and recovery from an interrupted download is already an
acceptance criterion. The wait message is the contention report Q08 allows on
standard error. The exact limit and the stale-owner test remain design work.

#### Answer to Q06: option A (with reason why it must be accepted as the answer)

Option A: it makes the concurrency and interruption criteria observable
behaviors: one download serves all waiting callers, a crash heals itself, and
a stuck holder ends in a precise diagnostic instead of a hang.

User decision: confirmed: option A, a second caller waits with a message up to
a bounded time, then fails naming the lock and its holder; a lock is recovered
only once its holder is established to be gone, never on age alone, selected
by the user on 2026-11-13 without amendment.

### Q07: Network environments the download must support

Question description: provisioning obtains the asset "from `orhun/git-cliff` on
GitHub". The requirement does not say whether the download must work behind a
corporate HTTPS proxy or with a corporate certificate authority, nor whether a
mirror or internal artifact repository can replace GitHub.

#### BBQ for Q07

The butcher delivers to the house, but this house sits behind a gated
community with a guard who inspects every package. The delivery can follow the
gate's rules, or the household can name a different shop. In this picture: the
butcher is GitHub's release download, the gated community is a corporate
network, the guard is the HTTPS proxy and its certificate authority, and the
different shop is a mirror or internal artifact repository.

#### Options for Q07

- Option A: download from GitHub only, through the documented standard proxy
  configuration and the operating system's trusted certificates, always with
  certificate verification; no mirror setting in v0.14.0.
  - pro: intended to work in corporate networks that allow GitHub through a
    standard proxy, without new configuration.
  - pro: one source keeps the integrity contract simple.
  - con: a network that blocks GitHub entirely cannot provision.
- Option B: also accept an llm-shared-level mirror base URL (never a project
  setting), with the same integrity verification.
  - pro: supports networks that only reach an internal repository.
  - con: a new setting and trust decision outside the umbrella's contract.
- Option C: GitHub only, with a direct connection and Python's own
  certificate bundle.
  - pro: simplest.
  - con: fails behind a proxy or a certificate-inspecting network, setups
    that llm-shared users can have.

#### Recommended option for Q07 (with arguments for this choice)

Option A: it targets networks that reach GitHub directly or through a standard
proxy, without adding a configuration surface; there is no evidence yet that
it covers every current installation. A network without GitHub access gets the
step 4 diagnostic; a mirror can be a later, separately decided scope. How long
a stalled connection may take before it fails is Q15; the download client and
trust-store integration remain design work.

#### Answer to Q07: option A (with reason why it must be accepted as the answer)

Option A: it keeps a single trusted source while making the download work
through the proxy and certificate configuration the user's system already has.

User decision: confirmed: option A, download from GitHub only, through the
documented standard proxy configuration and the operating system's trusted
certificates, always with certificate verification and no mirror setting,
selected by the user on 2026-11-13 without amendment.

### Q08: What provisioning reports, and on which output channel

Question description: a first download may happen in the middle of `uc`, a
generated release or a `gcliff` call whose output a script captures. The
requirement says the user need not know the dependency exists, but does not
say whether a download is announced, where messages go, or how a provisioning
failure is distinguished from a git-cliff failure in the exit status.

#### BBQ for Q08

The grill master steps away to buy charcoal mid-cookout. Guests can be told
"back in five minutes", or not told at all. Shouting it over the plates being
served would mix the announcement into the food. In this picture: the charcoal
run is a first download, the "back in five minutes" note is the provisioning
message, the plates are git-cliff's own standard output that a script captures,
and the side table where the note goes is standard error.

#### Options for Q08

- Option A: announce a download and its result in one or two lines on
  standard error, plus the lock-wait message of Q06 when a caller waits;
  reuse of a valid cache prints nothing; git-cliff's own standard output and
  exit status pass through `gcliff` unchanged; a provisioning failure uses an
  exit status that the admitted git-cliff versions do not use.
  - pro: a long first call is explained, and captured standard output stays
    exactly git-cliff's.
  - pro: scripts can tell "tool unavailable" from "git-cliff reported an
    error".
  - con: needs a documented provisioning exit status, and the design must
    verify that each admitted git-cliff version never returns it.
- Option B: silent unless provisioning fails.
  - pro: the dependency stays invisible.
  - con: a first `brel` that pauses for a download looks hung.
- Option C: show a progress display on standard output.
  - pro: most informative interactively.
  - con: corrupts captured output and logs of non-interactive runs.

#### Recommended option for Q08 (with arguments for this choice)

Option A: "need not know the dependency exists" means no manual step, not an
unexplained pause. Keeping the announcement on standard error preserves
git-cliff's output for scripts, and a distinct exit status lets callers report
the step 4 diagnostic precisely. That status is promised only for the admitted
versions, whose own exit codes the design checks.

#### Answer to Q08: option A (with reason why it must be accepted as the answer)

Option A: it explains the only visible effect of provisioning (a first-use
delay) without disturbing any caller that reads git-cliff's output, and the
exact message text and status numbers remain design work.

User decision: confirmed: option A, one or two standard-error lines per
download plus the Q06 wait message, silent reuse, git-cliff's standard output
and exit status passed through unchanged, and a provisioning failure status
that the admitted versions never return, selected by the user on 2026-11-13
without amendment.

### Q09: When provisioning runs, and whether it can be done ahead of time

Question description: provisioning happens at first need: generated `uc`,
generated release `pre` or `gcliff`. The requirement does not say whether a
user can provision ahead of time, for example before working offline, or
whether setup (item 6) downloads the binary when it configures a project.

#### BBQ for Q09

Charcoal can be bought on the way to the barbecue, or stocked the day before.
Buying on the way is simplest until the shop is closed on the day of the
cookout. In this picture: buying on the way is first-use provisioning during
`uc` or a release, stocking the day before is provisioning ahead of time, and
the closed shop is having no network at release time.

#### Options for Q09

- Option A: provisioning happens only at first need; a launcher call such as
  `bin\gcliff.bat --version` is the documented way to provision ahead of time.
  It works before the alias is exposed, and the alias form does the same once
  exposed.
  - pro: no extra command; the shared resolver already does the work.
  - pro: setup stays free of mandatory network downloads.
  - con: relies on users knowing that a `--version` call warms the cache.
- Option B: add a dedicated release-workflow operation that provisions the
  project's pin and reports the result.
  - pro: explicit and scriptable, with a project-scoped report.
  - con: a new command for something `gcliff` already does.
- Option C: setup (item 6) provisions the pin as part of configuring a
  project.
  - pro: the first release never waits for a download.
  - con: setup gains a network dependency, and the pin can change after setup.

#### Recommended option for Q09 (with arguments for this choice)

Option A: the launcher already runs the shared resolver, so a documented
`--version` call provisions the exact pin the project will use. Item 6 can
still recommend that call in its setup report without gaining a mandatory
download.

#### Answer to Q09: option A (with reason why it must be accepted as the answer)

Option A: it gives users an explicit, offline-preparation path without a new
command or a network dependency in setup.

User decision: confirmed: option A, provisioning happens at first need, and
`bin\gcliff.bat --version` (or the alias form once exposed) is the documented
way to provision ahead of time, selected by the user on 2026-11-13 without
amendment. Setup may recommend that call but gains no mandatory download.

### Q10: Which project's pin gcliff uses

Question description: "Within a project the alias uses its pin; outside one it
uses the llm-shared default." The requirement does not say how `gcliff` decides
it is within a project, nor which pin applies when its arguments point
git-cliff at another repository (git-cliff's own `--workdir` or `--repository`
options) than the current directory.

#### BBQ for Q10

A cook grabs the spice rack of the kitchen they stand in. If the recipe card
says "for the house next door", the cook can still use this kitchen's rack, or
walk next door to use theirs. In this picture: the kitchen the cook stands in
is the current directory's worktree, the spice rack is that project's
`[git-cliff] version`, and the recipe card naming the house next door is a
git-cliff `--workdir` or `--repository` argument.

#### Options for Q10

- Option A: the worktree containing the current directory, including from a
  nested directory, selects the project and its configuration (the umbrella
  rule that aliases use the current worktree, decision 16); git-cliff
  arguments pass through unread. Outside a worktree, or in one without a
  `[git-cliff]` pin, the default applies, after the whole-file validation of
  Q11. A target argument pointing at another repository does not select that
  repository's pin.
  - pro: consistent with the other aliases and simple to predict.
  - pro: `gcliff` passes every git-cliff argument through unchanged.
  - con: `gcliff --workdir <other>` renders with the current project's pin.
- Option B: the launcher takes an explicit project root as its first
  argument, and the alias passes the current worktree.
  - pro: scripts select a project explicitly.
  - con: `gcliff` no longer accepts plain git-cliff arguments, unlike the
    global-senv alias it replaces.
- Option C: inspect git-cliff's `--workdir` and `--repository` arguments to
  choose the project.
  - pro: follows the target repository.
  - con: couples the launcher to git-cliff's argument parsing, which changed
    in 2.14.1.

#### Recommended option for Q10 (with arguments for this choice)

Option A: it applies the existing alias rule unchanged and keeps the launcher
free of git-cliff argument parsing. A script that targets another project runs
`gcliff` from that project's directory.

#### Answer to Q10: option A (with reason why it must be accepted as the answer)

Option A: it is the umbrella's alias rule, it keeps `gcliff` an argument
passthrough to the pinned git-cliff, and it avoids depending on argument
syntax that git-cliff has already changed once.

User decision: confirmed: option A, the worktree containing the current
directory, including from a nested directory, selects the pin; git-cliff
arguments pass through unread, and a target argument never selects another
repository's pin, selected by the user on 2026-11-13 without amendment.

### Q11: gcliff in a project whose .release.ini is invalid

Question description: the common reader validates every declared setting
"including declarations unused by the current command". The requirement does
not say whether that rule applies to the `gcliff` launcher: a malformed
`[source:npm]` section unrelated to git-cliff would then block `gcliff` in that
project.

#### BBQ for Q11

The grill's ignition checks the whole gas line before lighting, even the hose
that feeds the patio heater. A leak in that hose keeps the grill off too, even
though the grill only needs its own valve. In this picture: the ignition check
is the common `.release.ini` validation, the patio heater hose is an unrelated
section such as `[source:npm]`, the grill's own valve is `[git-cliff] version`,
and lighting the grill is running `gcliff`.

#### Options for Q11

- Option A: `gcliff` validates the whole `.release.ini` like every release
  operation, and reports any invalid declaration with the reader's
  diagnostic, without falling back to another pin.
  - pro: one configuration rule for every entry point; no command can run on
    a configuration that others reject.
  - con: an unrelated error blocks an interactive `gcliff` call until fixed.
- Option B: `gcliff` reads and validates only the `[git-cliff]` section.
  - pro: unrelated errors do not get in the way.
  - con: changes the established item 1 reader contract by adding a second,
    partial reading mode.
- Option C: on any configuration error, fall back to the default pin with a
  warning.
  - pro: `gcliff` always runs.
  - con: undermines exact pinning: it runs a different version than the
    project declared, the exact drift the pin prevents.

#### Recommended option for Q11 (with arguments for this choice)

Option A: the diagnostic names the file and the offending setting, so the fix
is immediate, and keeping one reading rule avoids a special case in the
foundation item 1 established.

#### Answer to Q11: option A (with reason why it must be accepted as the answer)

Option A: it keeps the item 1 contract ("validates every declared setting")
for every entry point, and never lets `gcliff` run a version the project did
not declare.

User decision: confirmed: option A, `gcliff` validates the whole `.release.ini`
like every release operation and reports any invalid declaration without
falling back to another pin, selected by the user on 2026-11-13 without
amendment.

### Q12: When gcliff joins llm-shared's alias set, given the global gcliff

Question description: the requirement says llm-shared supplies the `gcliff`
alias in its alias set, while the umbrella item entry says "setup/cutover
expose the alias". That alias set is one shared file: llm-shared's `senv.bat`
loads `%LLM_SHARED_DIR%\senv.doskey` with `doskey /MACROFILE`, and
my-project's `senv.bat` loads `..\llm-shared\senv.doskey` too. Global senv
already defines a `gcliff` macro that runs the `PRGS` 2.7.0 binary. Whenever
`gcliff` enters the shared file, every console that loads it afterwards gets
the provisioned `gcliff`, which replaces a global-senv `gcliff` loaded earlier,
including consumers whose `uc` still renders with 2.7.0 through dev_workflow
until their own migration. No timing of that single edit can follow each
project's changelog migration.

#### BBQ for Q12

A new thermometer is hung on the shared hook of a community kitchen. Every cook
who uses that kitchen gets the new one the same day, including cooks whose oven
still runs on the old settings, so their readings disagree for a while. Hanging
it later does not help one cook in particular; only a hook at each station
would. In this picture: the shared hook is the `gcliff` name in llm-shared's
shared `senv.doskey`, the community kitchen is every console that loads that
file, the old thermometer is the global-senv `gcliff` (2.7.0), the new one is
the provisioned pin (initially proposed as 2.14.2), each cook's oven is that
project's `uc`, which keeps 2.7.0 until its own migration, and a hook at each
station is per-project activation of the alias.

#### Options for Q12

- Option A: this item ships and tests `bin/gcliff.bat` and the alias
  definition without adding it to the shared `senv.doskey`. Item 8 adds it to
  that file at llm-shared's cutover, as a shared exposure that reaches every
  console loading the file, and item 6 setup brings it to consumers that do
  not load the file yet. Consumers still on the legacy `uc` then go through a
  mixed-version interval: `gcliff` runs the project's admitted pin or the
  executing checkout's default, initially proposed as 2.14.2, while their
  `uc` renders with 2.7.0, until their own migration.
  - pro: follows the umbrella ownership line ("setup/cutover expose the
    alias") and the shared-file model the other release aliases already use.
  - pro: this item stays inside its scope, the resolver and the launcher
    behind the alias; its tests use the launcher directly.
  - con: the mixed-version interval is real for consumers such as my-project;
    it is recorded, not avoided.
  - con: interactive `gcliff` stays on the global 2.7.0 until the cutover.
- Option B: this item adds `gcliff` to the shared `senv.doskey` at once.
  - pro: users get the provisioned binary immediately.
  - con: the same shared exposure and mixed-version interval, starting
    earlier and for llm-shared too, while its own `uc` still renders with
    2.7.0.
- Option C: ship the alias under a new name to avoid replacing the global
  `gcliff`.
  - pro: no collision, and no mixed-version interval under one name.
  - con: two names for one tool, and the umbrella names the alias `gcliff`.
- Option D: per-project activation: `gcliff` stays out of the shared file,
  and each project's own setup defines it when that project's changelog flow
  moves (item 6 for consumers, item 8 for llm-shared).
  - pro: a project's `gcliff` and `uc` switch together, with no mixed-version
    interval.
  - con: departs from decision 17 (the alias is available to every user who
    loads llm-shared aliases) and adds a per-project alias mechanism to item
    6, which needs an authorized umbrella change.

#### Recommended option for Q12 (with arguments for this choice)

Option A: it keeps item 3 inside its ownership and states the real consequence
of the shared alias file, instead of promising a per-project switch that one
shared file cannot give. The mixed-version interval is recorded for each
consumer's own migration effort. If a per-project guarantee matters more,
option D is the explicit alternative, with its scope cost.

#### Answer to Q12: option A (with reason why it must be accepted as the answer)

Option A: it resolves the contradiction in favor of the umbrella's ownership
entry, keeps the confirmed alias name and the fixed resolver, and makes the
shared exposure, with its mixed-version interval, an explicit cutover step
instead of a side effect of updating llm-shared.

User decision: confirmed: option A, item 3 ships and tests `bin/gcliff.bat` and
the alias definition; item 8 adds the macro to the shared `senv.doskey` as a
shared exposure, and item 6 brings it to consumers that do not load that file
yet; the mixed-version interval for consumers still on the legacy `uc` is
recorded, selected by the user on 2026-11-13 without amendment.

User comment (2026-11-13): umbrella items land on `sibling_release_tooling`,
and main receives the umbrella only after all items are developed, so
consumers such as my-project see the shared `gcliff` when the umbrella merges
to main, with the same mixed-version interval; any earlier change reaching
main is unlikely. The decision stands.

### Q13: Compatibility evidence this item must deliver

Question description: the acceptance criteria require "tested compatibility
for the proposed exact 2.14.2 pin using real templates/parsers and histories",
with the differences from 2.7.0 recorded, and the pinning policy asks to test
"the real llm-shared header, template, parser and skip rules, snapshot-tag
history and archive ranges". In dev_workflow, `update-changelog.sh` runs
git-cliff first, with `-c cliff.toml -w <PRJ_DIR> -s footer` and a computed
range, and only then cleans its output with sed, injects the `version.txt`
notes, attaches `changelog-header.md`, labels the sections and applies the
`.changelog.fixes` Perl rules. Running git-cliff alone exercises none of those
later stages. Item 4 owns `cliff.toml`, the header, ranges and fix rules, item
8 owns the parity rehearsals, and item 4's rendering does not exist yet when
this item is implemented. The requirement does not say which comparison this
item's evidence covers, which inputs make it reproducible, or how the compared
binaries are obtained, given that Q01 may admit only tested pins.

#### BBQ for Q13

Before switching charcoal brands, the cook grills the same cuts with both
brands, unseasoned, and tastes the difference. Seasoning and plating come
later, and the full dinner rehearsal checks them. In this picture: the brands
are git-cliff 2.7.0 and 2.14.2, the same cuts are llm-shared's frozen history,
ranges and `cliff.toml`, unseasoned means raw git-cliff output before the
`update-changelog.sh` postprocessing, seasoning and plating are the header,
notes, section labels and fix rules that item 4 renders, and the dinner
rehearsal is item 8's parity run.

#### Options for Q13

- Option A: this item compares raw git-cliff output only. Both versions run
  with identical, recorded inputs: llm-shared's history frozen at a recorded
  commit, the same explicit ranges, the dev_workflow `cliff.toml` and the
  same command-line flags as `update-changelog.sh`. The evidence matrix keeps
  the coverage the compatibility section names: commit parsers and skip
  rules, snapshot-tag history and archive ranges, with a recorded fixture
  history for any case llm-shared's own history lacks. Every difference is
  classified as intentional or a defect. Header attachment, note injection,
  section labels and fix rules are not covered: item 4 re-checks its new
  renderer, and item 8's parity rehearsal compares the complete legacy and
  new pipelines. The compared binaries are evidence candidates that are not
  admitted as pins: 2.14.2 is obtained through this item's download and
  upstream integrity verification and joins Q01's tested set once this
  evidence is recorded; 2.7.0 runs only under the evidence-only policy of
  Q16.
  - pro: proves the renderer change before any later item depends on it, with
    the configuration that exists today.
  - pro: reproducible: anyone can rerun the comparison from the recorded
    commit, ranges and flags.
  - pro: separates renderer differences from postprocessing, so each later
    item knows what it still owes.
  - con: the 2.7.0 Windows ZIP has no upstream integrity data, so the 2.7.0
    run stays blocked until the user decides Q16.
  - con: item 4's new configuration needs its own re-check later.
- Option B: this item proves only provisioning (download, verification,
  `--version`); all output compatibility moves to items 4 and 8.
  - pro: smaller scope, and no 2.7.0 binary needed.
  - con: contradicts this item's acceptance criterion and leaves the pin
    unproven while items 4 and 5 build on it.
- Option C: also cover my-project's history and its 32 fix rules.
  - pro: broader evidence.
  - con: my-project's migration is its own effort (umbrella decision 11).
- Option D: compare the complete legacy pipeline, git-cliff plus the
  `update-changelog.sh` postprocessing, with each version.
  - pro: also covers the header, notes, section labels and fix rules.
  - con: runs dev_workflow's bash pipeline and its `PRGS` path inside this
    item, and duplicates item 8's parity rehearsal.

#### Recommended option for Q13 (with arguments for this choice)

Option A: it delivers the renderer evidence the acceptance criterion asks for,
with the templates and parsers that exist today, states exactly what it does
not cover, and leaves the header, notes, fix rules and final parity with items
4 and 8. Neither binary comes from global senv; how the 2.7.0 binary is
trusted is Q16.

#### Answer to Q13: option A (with reason why it must be accepted as the answer)

Option A: it gives the pin real, reproducible evidence before item 4 depends
on it and keeps the work within the umbrella's ownership split. It keeps
upstream verification mandatory for production pins; an evidence-only 2.7.0
run is blocked until the explicit Q16 trust-policy decision authorizes its
narrowly stated exception.

User decision: confirmed: option A, item 3 compares raw git-cliff output of
both versions on recorded frozen inputs with the parser, skip-rule,
snapshot-tag and archive-range matrix; postprocessing and final parity stay
with items 4 and 8, and the 2.7.0 side runs only under Q16, selected by the
user on 2026-11-13 without amendment.

### Q14: Cache entries for pins no longer used

Question description: versioned directories let several pins coexist in one
llm-shared clone. The requirement does not say whether anything removes
entries for versions no project uses any more, or partial entries left by an
interrupted download.

#### BBQ for Q14

Every time the house switches charcoal brands, the old bag stays in the
garage. A few bags take little room, but nobody knows which ones are still
needed by the neighbor who borrows the grill. In this picture: each bag is a
cache entry for one git-cliff version, the garage is
`.tools/git-cliff/`, the brand switch is a pin change, and the neighbor is
another project sharing the same llm-shared clone with an older pin.

#### Options for Q14

- Option A: complete entries stay until a user deliberately removes them
  while no caller uses them; provisioning never evicts a complete valid entry
  and never replaces a binary another release is using. Removing an entry
  loses offline availability for that version until a later provisioning
  succeeds. Leftovers of an interrupted download are cleaned by a later
  provisioning of that version, only once their owner is established to be no
  longer running (Q06).
  - pro: never removes a binary another project or a running release uses.
  - pro: no new command in v0.14.0.
  - con: unused versions accumulate (a few megabytes each).
  - con: a manual removal is the user's responsibility; nothing protects a
    release that uses the entry at that moment.
- Option B: provisioning removes other versions it considers unused.
  - pro: no accumulation.
  - con: one clone cannot know every project's pin, so it may remove a
    version another project needs, or one in use.
- Option C: add an explicit clean command.
  - pro: deliberate and visible cleanup.
  - con: extra scope for a small disk cost.

#### Recommended option for Q14 (with arguments for this choice)

Option A: the cost of keeping an old version is a few megabytes, while
removing one automatically could break another project's offline release.
Manual removal stays possible but is not guaranteed safe: the user removes an
entry only when no caller uses it, and offline use of that version waits for
the next successful provisioning. Partial downloads are already part of the
interruption criterion and are cleaned under Q06's ownership check.

#### Answer to Q14: option A (with reason why it must be accepted as the answer)

Option A: it avoids any automatic eviction, keeps the contract that no binary
in use is replaced, and limits automatic cleanup to abandoned partial state
whose owner is established to be gone.

User decision: confirmed: option A, complete entries stay until a user removes
one while nothing uses it; provisioning never evicts a complete valid entry or
replaces a binary in use, and partial leftovers are cleaned only under the Q06
ownership check, selected by the user on 2026-11-13 without amendment.

### Q15: Bounded failure of network operations and version probes

Question description: Q06 bounds how long a second caller waits for a lock,
but not the lock holder's own work. Provisioning looks up release metadata,
downloads an asset and runs the executable's `--version`; a server that stalls
or a probe that never exits would hold the lock indefinitely, and every
generated release on that pin would wait behind it until Q06's wait expires.
The requirement does not say whether those stages have finite limits, or what
an expired limit leaves behind.

#### BBQ for Q15

The neighbor using the shared grill has gone to fetch charcoal from a shop that
never answers the door. A limit on how long others wait in line does not bring
the neighbor back; only a time limit on the errand itself does. In this
picture: the neighbor is the provisioning call holding the lock, the errand is
the metadata lookup, the asset download or the `--version` probe, the shop that
never answers is a stalled server or a hung process, and the waiting line is
Q06's bounded wait.

#### Options for Q15

- Option A: every provisioning-controlled network operation and version probe
  has a documented finite time budget, with bounded retries if any. An expired
  budget reports the pin, the internal path and the failed stage, leaves no
  entry that a later run accepts, and releases recoverable lock state, without
  changing the project.
  - pro: no generated release or `gcliff` call can hang on provisioning.
  - pro: the diagnostic names the failed stage, so a network problem reads
    differently from a broken executable.
  - con: a very slow but working network can exceed a budget, so the limits
    need documented values that suit slow links.
- Option B: bound lock acquisition only, and let network operations and probes
  wait indefinitely.
  - pro: simpler, with no limit to choose for each stage.
  - con: a caller holding the lock can hang every first-use release, despite
    Q06's bounded waiting for the others.
- Option C: require manual cancellation and recovery for a stalled holder.
  - pro: no automatic decision about when a slow operation has failed.
  - con: adds an operator dependency, contrary to automatic first-use
    provisioning.

#### Recommended option for Q15 (with arguments for this choice)

Option A: it specifies the observable availability contract, so Q06's bounded
wait has a matching bound for the holder. The design selects the values, the
retry policy and the mechanisms; this question chooses no client, timeout
number or lock mechanism.

#### Answer to Q15: option A (with reason why it must be accepted as the answer)

Option A: it makes "fail with a precise diagnostic, never hang" true for every
stage of provisioning, not only for the lock wait, and keeps a failure from
leaving state that a later run would trust. The rendering by git-cliff itself
stays outside this guarantee.

User decision: confirmed: option A, every provisioning-controlled network
operation and version probe has a documented finite time budget with bounded
retries if any, and an expired budget reports the pin, the internal path and
the failed stage without leaving an accepted entry or changing the project,
selected by the user on 2026-11-13 without amendment.

### Q16: Trusting the 2.7.0 comparison binary without upstream integrity data

Question description: the integrity rule makes missing verification data an
explicit setup failure, never a reason to skip the check, and the umbrella's
automatic provisioning sequence says the same. Checked on 2026-11-13 through
GitHub's release API, the 2.7.0 `git-cliff-2.7.0-x86_64-pc-windows-msvc.zip`
asset has no asset digest, and 2.7.0 publishes `.sha512` sidecars for its
tarballs only, not for its Windows ZIPs; the 2.14.2 Windows ZIP does have an
asset digest. Q13 compares 2.14.2 with 2.7.0, so the 2.7.0 binary cannot be
verified against independent upstream data. Running it for evidence needs
either an explicit, narrowly scoped exception to that rule or a different
evidence policy. A digest computed after the download identifies the
downloaded bytes and lets a later run check that they did not change; it does
not authenticate the first download. The requirement says neither which policy
applies nor whether it must be authorized before the binary first runs.

#### BBQ for Q16

A taste test compares new charcoal with an old brand whose bags no longer carry
a factory seal. The cook can decide in advance to buy one bag from the usual
shop, accepting that only the shop vouches for it, and write its lot number in
the tasting notes so a repeated test uses the very same bag. The cook can also
compare that bag with an old one in the garage, or skip the old brand. The lot
number proves that later tests use the same bag, not that the first bag was
genuine. In this picture: the old brand is git-cliff 2.7.0, the missing factory
seal is the absent upstream integrity data, the usual shop is the upstream
GitHub release reached over certificate-verified HTTPS, deciding in advance is
the user authorizing the evidence-only policy before the first run, the lot
number is the SHA-256 digest recorded in the evidence, the bag in the garage
is the global-senv 2.7.0 binary, and skipping is dropping the 2.7.0 run.

#### Options for Q16

- Option A: a proposed evidence-only exception to upstream verification.
  Only after the user explicitly authorizes this evidence-only trust policy,
  obtain the 2.7.0 Windows ZIP from the named upstream GitHub release over
  certificate-verified HTTPS, record its exact asset identity and SHA-256
  digest, and run it solely for the frozen-input comparison of Q13. HTTPS is
  the initial trust anchor; the recorded digest identifies the downloaded
  bytes and is rechecked when the comparison is repeated, but does not
  independently authenticate the initial archive. The evidence candidate is
  never admitted as a project pin or published as an entry that normal
  provisioning accepts, and missing upstream verification data remains a setup
  failure for every production pin. The user's explicit selection of this
  fully stated policy is the authorization, with no extra prompt for each run;
  reviewing the resulting evidence is a separate acceptance step.
  - pro: the exception is disclosed, narrow, and decided by the user before
    anything runs.
  - pro: production provisioning stays fail-closed, nothing from global senv
    is needed, and every repetition checks the same recorded bytes.
  - con: the first download is trusted on certificate-verified HTTPS alone.
  - con: it departs from the umbrella's unconditional integrity wording, so
    selecting it flags that wording for authorized reconciliation as an
    evidence-only exception.
- Option B: option A, plus recording whether the downloaded executable is
  byte-identical to the global-senv 2.7.0 binary.
  - pro: links the comparison to the binary that has rendered llm-shared's
    changelogs so far.
  - con: corroboration only, not independent authentication, since both copies
    may come from the same unverified source.
  - con: reads a machine-specific installation that this item otherwise never
    touches, and the corroboration cannot be repeated on a machine without it.
- Option C: drop the 2.7.0 run, and compare 2.14.2's output with the
  changelogs the legacy pipeline already committed.
  - pro: no binary lacking upstream verification ever runs.
  - con: committed changelogs include the postprocessing, so renderer
    differences cannot be isolated, and the comparison moves in practice to
    item 8's parity work.
  - con: changes Q13's evidence scope and the acceptance criterion's
    "differences from the observed 2.7.0", which need a matching
    reconciliation.

#### Recommended option for Q16 (with arguments for this choice)

Option A: it is the simplest option that keeps raw 2.7.0 evidence while stating
plainly that this is an exception: disclosed, narrow, authorized before the
first execution, and never reaching production provisioning. If the user
selects it, the umbrella's integrity wording is flagged for reconciliation
through the authorized post-decision workflow, as Q05 does for its own
wording. If the user rejects the exception, the 2.7.0 comparison stays blocked
until a different evidence policy and its scope consequences are explicitly
settled. Option B's corroboration can still be added to the evidence by hand,
without becoming part of the contract.

#### Answer to Q16: option A (with reason why it must be accepted as the answer)

Option A: it avoids an undisclosed exception. It names exactly what is trusted
(the upstream release over certificate-verified HTTPS), what the recorded
digest proves (that later runs use the same bytes) and what it does not
(independent authentication of the first download), and it keeps upstream
verification mandatory for every production pin.

User decision: confirmed: option A, the user authorizes the evidence-only trust
policy before the 2.7.0 binary first runs: download it from the upstream
GitHub release over certificate-verified HTTPS, record its asset identity and
SHA-256, and run it solely for the Q13 comparison; it is never a pin or an
accepted cache entry, and production pins stay fail-closed. Selected by the
user on 2026-11-13 without amendment; the umbrella integrity wording is flagged
for authorized reconciliation as an evidence-only exception.
