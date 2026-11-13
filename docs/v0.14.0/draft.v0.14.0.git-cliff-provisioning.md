# Provision pinned git-cliff automatically

- Type: feature-request
- Test group: whole suite
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Target version: v0.14.0
- Documentation layout: docs/v0.14.0/
- Slug: git-cliff-provisioning

## Selected umbrella entry for git-cliff provisioning

| Order | Type | Key title | Slug | Status | Requirement | Validation plan |
| --- | --- | --- | --- | --- | --- | --- |
| 3 | Feature-request | Provision pinned git-cliff automatically | `git-cliff-provisioning` | pending | - | - |

### Requirement detail inherited for git-cliff provisioning

- Type: Feature-request
- Key title: Provision pinned git-cliff automatically
- Slug: `git-cliff-provisioning`
- Regroups: internal cache/downloader, exact pin, compatibility policy and the
  2.7.0-to-2.14.2 research, fixed `GIT_CLIFF`, `gcliff` launcher/alias contract,
  concurrency/integrity checks and dependency-specific preflight errors.
- Boundary rationale: rendering needs predictable availability without exposing
  an installation task to the consumer; no external binary discovery remains.
- Depends on: `release-project-root`.
- Ownership: asset selection/download/cache, direct invocation, version checks;
  setup/cutover expose the alias, while item 4 decides when rendering needs it.
- Acceptance criteria:
  - Read an exact project/default pin, compute its ignored internal
    version/platform path and reuse a valid cached binary without network.
    No executable override, PATH search/mutation, PRGS or senv dependency.
  - Automatically download the correct GitHub release asset if absent/invalid,
    verify integrity/version, safely extract and atomically publish under a
    cache lock; handle concurrent users, interrupted downloads and offline use.
    Support Windows x64 only initially and diagnose other platforms before
    project mutation.
  - Report internal path/pin and precise setup/network/verification failure
    when provisioning cannot supply the binary. Never require manual git-cliff
    installation. Do this before consuming-project managed-file/Git mutation.
  - Direct launcher and interactive `gcliff` share provisioning; scripts do not
    depend on doskey expansion. Inside a project use its pin, outside use the
    llm-shared default; leave the parent's environment unchanged.
  - Establish tested compatibility for the proposed exact 2.14.2 pin using
    real templates/parsers and histories. Record intentional differences from
    observed 2.7.0; no floating latest or silent pin upgrade at release time.
  - Version operations, ordinary builds, curated validation and fix conversion
    remain available without provisioning; cache state never joins a commit.

## Context and scope of git-cliff provisioning

dev_workflow's `update-changelog.bat` and `.sh` run git-cliff, then clean its
output with sed, awk and Perl. The engine keeps git-cliff and drops the rest:
after the rewrite, it uses llm-shared's Python and Git, plus git-cliff only for
generated changelogs, with no `bash`, `sed`, `awk`, `perl` or `cygpath`.

Today the binary comes from global senv: the observed one is 2.7.0. Neither
that binary nor global senv is a runtime dependency of the new tooling. The
earlier proposal to install git-cliff externally and discover it was superseded
by the comments on the umbrella draft: llm-shared owns downloading and caching
git-cliff, and a release user does not need to know the dependency exists
(umbrella decision 18).

Item 1, `release-project-root`, is completed and merged. It supplies what this
item builds on:

- an explicit validated project root, root-scoped Git, and command dispatch
  through the self-locating `bin/release_workflow.bat` and `bin/release_alias.bat`;
- the common `.release.ini` reader, read with interpolation off, which composes
  explicitly registered domain schemas and validates every declared setting
  before mutation. Its shipped schemas are `tooling` and `version`; the
  `[git-cliff]` section has no owner yet, and this item registers it. Item 1
  states that there is no git-cliff executable configuration key and that this
  item computes the internal path;
- the Windows x64 runtime check and the separation of `LLM_SHARED_DIR` from the
  consumer root. Item 1 keeps consumer scratch files out of the tooling
  checkout and names this item's managed binary cache as the one distinct
  permitted write area there.

Item 2, `version-sources`, is also merged. It owns the shared stable/snapshot
tag classifier and range selector that git-cliff input will use; configuring
git-cliff with it is item 4's work.

This item owns pin resolution, asset selection, download, integrity and version
checks, the cache and its locks, direct invocation and the shared resolver
behind the `gcliff` launcher and alias. It does not own:

| Behavior outside git-cliff provisioning | Owning umbrella item |
| --- | --- |
| When rendering needs git-cliff, `cliff.toml`, header, ranges, fix rules and archives | 4, `changelog-management` |
| Calling provisioning in generated release `pre` before project writes | 5, `build-release-lifecycle` |
| Exposing the aliases in a consumer's setup; proposing a newer tested pin with its diff | 6, `release-tooling-setup` |
| `/prepare-release` Steps 10 and 11 calling the changelog services | 7, `prepare-release-integration` |
| llm-shared's own `.release.ini` pin, exposed aliases and parity rehearsals | 8, `llm-shared-cutover` |

## Version notation for the git-cliff pin

| Context | Form | Example |
| --- | --- | --- |
| git-cliff pin in `.release.ini` and the cache directory | `X.Y.Z`, without `v` | `2.14.2` |
| Upstream GitHub release tag | `vX.Y.Z` | `v2.14.2` |

The pin follows the umbrella's notation rule: a value that sets a version
never includes `v`; an upstream tag keeps its actual spelling.

## The exact pin and where it comes from

Read an exact `[git-cliff] version` from the consuming project's `.release.ini`,
or the tested llm-shared default when it is omitted. The proposed default is
2.14.2, subject to the compatibility checks below. Never resolve a floating
`latest` during a release.

```ini
[git-cliff]
; exact version to download automatically into llm-shared's ignored cache
version = 2.14.2
```

The git-cliff pin belongs to internal provisioning: the common reader validates
it with every other declared setting, before mutation. There is no executable
key in `.release.ini`: llm-shared computes the fixed internal path. No consumer
runs code from project config.

Within a project, the pin comes from that project; outside one, the
llm-shared default applies. Later
upgrades are deliberate pin changes with compatibility evidence, never a
floating latest (umbrella decision 19).

## The internal cache location

The fixed location for one pin and platform is:

```text
<LLM_SHARED_DIR>/.tools/git-cliff/<version>/<platform>/git-cliff.exe
```

on the supported Windows x64 platform. The cache is ignored in llm-shared Git.
Versioned directories let consumers with different pins share one clone.

Cache writes are the explicit exception to keeping consumer temporary state
out of llm-shared. Consumer transaction state never goes into the tooling
checkout; the managed git-cliff cache has its own provisioning locks, separate
from the release transaction serialization. Linked-worktree Git metadata and
this tooling cache keep distinct boundaries.

## Direct invocation, GIT_CLIFF and the gcliff launcher

`GIT_CLIFF` is a launcher-local value computed from the internal path, not an
external override. No PATH, `PRGS`, global-senv, alias or machine installation
discovery is performed. Invoke the absolute executable directly and leave the
parent's PATH and environment unchanged (umbrella decision 20).

llm-shared supplies `bin/gcliff.bat` and the `gcliff` alias in its alias set,
both using this same resolver and downloader. The alias is available to every
user who loads llm-shared aliases, including without global senv. Scripts call
the launcher directly, since doskey aliases do not expand in subprocesses.
Within a project the alias uses its pin; outside one it uses the llm-shared
default.

## Provisioning steps before generated changelog work

1. Check the selected cache path and executable version. Reuse a valid copy
   without network access.
2. If absent or invalid, obtain the matching OS/architecture release asset
   from `orhun/git-cliff` on GitHub, verify its published integrity information,
   and extract safely into a unique temporary cache directory.
3. Validate `--version`, then publish the cache entry atomically under a
   per-version/platform lock. Concurrent releases must not consume partial
   installs or replace a binary another release is using.
4. If the fixed binary still cannot be made available, stop with the requested
   version, internal path and download, verification or execution diagnostic.
   Explain the llm-shared setup, network or permission failure; do not ask the
   user to install git-cliff or configure PATH manually.

The acceptance criteria add interrupted downloads and offline use: a valid
cached binary needs no network, and a missing one with no network fails with
the step 4 diagnostic.

### Integrity data per release asset

The supported platform contract must define the integrity check for each
asset; do not assume every asset has a `.sha512` sidecar. For example, 2.14.2
lists those for tarballs but not for Windows ZIPs; the inspected x86_64 MSVC
ZIP has a SHA-256 digest in GitHub's asset metadata. Verify that digest where
available; missing verification data is an explicit setup failure.

## Operations that need git-cliff and those that never do

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
automatic `fixes init`, so a missing tool cannot leave a newly created rule
file behind. That ordering belongs to item 4; this item supplies the
provisioning those callers run first.

When llm-shared is beside the project, the umbrella states:

| Situation | `b` (build) | `brel` / `br` | `gv`, `uc`, `uver`, `uvf` |
| --- | --- | --- | --- |
| Pinned git-cliff absent from internal cache | Builds | Generated `br`/`brel` downloads and verifies it automatically before project mutation; curated release builds need none | Generated `uc` does the same; version/snapshot commands and curated validation need no binary |
| Internal git-cliff unavailable and download/verification fails | Builds | Generated release fails with internal path/version and setup/network diagnostic; curated release builds work | Generated `uc` fails; version commands and curated validation remain available |

All release entries still require `main` and the readiness gates (item 5).

## Supported platform for git-cliff provisioning

The v0.14.0 release tooling supports Windows x64 only initially, covering
git-cliff provisioning among the other parts (confirmed answer Q1 A). Other
operating systems and architectures require later scope; existing Unix
deployment references do not extend this support. An unsupported platform
receives a clear scope diagnostic before project mutation.

## Failure when provisioning cannot supply the binary

Attempt automatic provisioning first. If it cannot supply the binary, fail
generated work before project mutation with an internal setup or download
diagnostic naming the requested version and internal path; other operations
remain usable (umbrella decision 21). Never require a manual git-cliff
installation or a PATH change.

## git-cliff 2.7.0 compared with 2.14.2

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

### Pinning policy for git-cliff

| Pinning policy | Pros | Cons |
| --- | --- | --- |
| Exact `version = 2.14.2` in `.release.ini` (recommended for this cutover) | Reproducible binary, recent worktree/Windows/range fixes, automatic first-use install, reviewable upgrades | Newer parser/default behavior can change output; compatibility fixtures and a deliberate later pin update are required |
| Retain exact `2.7.0` temporarily | Closest comparison with the observed old tooling | Misses subsequent fixes/features; requires a second tested compatibility target if supported beyond migration evidence |
| Floating `latest` on each run | Gets new upstream changes without editing config | Output and CLI behavior can change without project review; network dependence and hard-to-reproduce releases; rejected |

Use 2.14.2 as the proposed initial pin and test the real llm-shared header,
template, parser/skip rules, snapshot-tag history and archive ranges against it.
Document intentional differences from 2.7.0 before cutover. Later setup/upgrade
checks (item 6) can propose a newer tested exact pin with its diff; ordinary
release runs never silently move the pin. The 2.14.2 pin is a researched
recommendation, not a claim that binary compatibility has been validated, and
the upstream check above dates from 2026-10-09.

## Consumer inputs for git-cliff provisioning

These repositories shape the need. Their own migrations stay in their own
efforts; llm-shared's belongs to item 8.

- llm-shared: generated changelog with 2 fix rules; its cutover creates
  `.release.ini` with the exact git-cliff pin, ignores the internal
  `.tools/git-cliff/` cache, and exposes `gcliff` with the other aliases.
  Parity rehearsals against dev_workflow accept approved git-cliff output fixes
  as documented intentional differences.
- my-project: generated changelog with 32 fix rules, so it needs the
  provisioned binary for `uc` and generated releases.
- workspace-halo: its hand-written, marketplace-style `CHANGELOG.md` uses the
  `curated` mode, so it never needs git-cliff.
