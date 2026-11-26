# Manage generated and curated changelogs

- Type: feature-request
- Test group: whole suite
- Target version: v0.14.0
- Slug: changelog-management
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md

## Draft basis and user need for changelog management

As a maintainer who releases a project with the llm-shared release tooling, I
need its `CHANGELOG.md` kept the way that project keeps it: rebuilt from commit
messages when the project generates it, or left exactly as written when a
person curates it. A generated changelog must cover every commit since the
previous real release, apart from those its commit groups skip on purpose
(such as release chores), even when snapshot markers sit in between, must not
change for a commit hash alone, and must keep my older release notes as they
are. Older releases must move to archive files whose ranges I choose, without
losing or reordering a section. Every changelog run must either write a
complete, checked result or leave my files as they were.

The [focused draft](draft.v0.14.0.changelog-management.md) derives from item
4 of the [sibling release tooling umbrella](draft.v0.14.0.sibling_release_tooling.md)
and was approved on 2026-11-23, after a point-by-point review that added two
archive checks: completeness and newest-first order. It gathers the umbrella
contracts on the default and project `cliff.toml`, the header, stable ranges,
exactly-once release notes, snapshot and release headings, groups and
duplicates, the generated and curated modes, built-in cleanups, declarative
fix rules and their conversion, and configurable archives (umbrella decisions
2, 10, 22, 26, 27 and 38, confirmed answers Q2 A and Q3 A). This requirement
records those outcomes without choosing their implementation.

## Changelog sections, release notes and notices

Three words keep one meaning throughout this requirement and its questions:
section, release notes and notice. They are defined here with the files they
describe.

### Sections of a changelog file

A section is the part of a changelog file that starts at a level-two heading
line, such as `## 0.0.24`, and runs over every line under it, up to the next
level-two heading line or the end of the file. Most sections name a version;
a curated file can also hold a section whose heading names none, such as
`## Unreleased`. The lines before the first section belong to no section:
they form the preamble of the file, described below. Which lines count as
headings, including a `##` line inside a fenced code block, is set by Q04 in
generated mode and by Q09 in curated mode.

llm-shared's generated `CHANGELOG.md` today, shortened:

```text
# LLM-Shared workflow tools

Shared instructions, skills, scripts, and Python tools that drive an LLM ...

## [v0.14.0] - 2026-11-12 - Groundhog Shares the Stopwatch

Consumer pytest runs choose lifecycle budgets, process audits, or both.
...

## [v0.13.0] - 2026-10-06 - Groundhog Gets a Receipt
```

The title and its paragraph belong to no section. The `v0.14.0` section runs
from its heading to the line before `## [v0.13.0]`: its release notes, then
its commit list.

workspace-halo's curated `CHANGELOG.md` today, shortened:

```text
# Changelog

## Unreleased

## 0.0.24

- Stop VS Code windows from taking turns coming to the front after a monitor
  unplug: ...

## 0.0.23
```

The `## Unreleased` section is empty and names no version. The `0.0.24`
section holds the author's release notes, here bullets, up to `## 0.0.23`.

In curated mode, a level-two heading that names no version and does not look
versioned, such as `## Unreleased`, is still a section boundary. The engine
keeps that section byte for byte and leaves it out of the target, history,
duplicate-version and placement checks. A heading that looks versioned but
fits none of Q09's forms still fails.

| Kind of section | Generated example | Curated example |
| --- | --- | --- |
| Released: its heading names a released version | `## [v0.14.0] - 2026-11-12 - <title>` | `## 0.0.24` |
| Unreleased, also called the snapshot section: the version in development | `## [v0.15.0-SNAPSHOT unreleased] <title>`, or `## [v0.15.0 unreleased] <title>` for an untagged stable version (Q02) | `## 0.0.25`, written before its release |
| Naming no version | none: a heading outside Q04's forms stops a generated run | `## Unreleased` |

The target section is the section of the version a run works on: the
`version.txt` version in an ordinary run, or the version being released. A
section is missing when no heading of an accepted form names that version; a
`## Unreleased` section never stands for it.

A changelog file is either the root `CHANGELOG.md` or an archive file. An
archive file, or archive, is a Markdown file under `docs/`, named
`docs/CHANGELOG.vA.B.C-vD.E.F.md`, that holds the released sections of one
older version range, newest first, so the root stays short. Each archive is
declared in `.release.ini` by one `[changelog-archive:...]` configuration
section, whose `from` and `to` give its inclusive range and whose `file` gives
its path. The root keeps the snapshot section and the released sections from
`recent-from` upward, with a link to each archive of a declared range that
holds at least one release (Q13). For example, with
`[changelog-archive:0.1.0-0.13.9]` and `recent-from = 0.14.0`, llm-shared's
`docs/CHANGELOG.v0.1.0-v0.13.9.md` would hold the sections of `v0.13.0` down
to `v0.1.0`, and the root those of the version in development and `v0.14.0`.
In generated mode the engine writes the archives; in curated mode the author
writes them and the engine checks their placement and links. An obsolete
archive is a file that an earlier `.release.ini` declared and the current one
no longer declares: it is still an archive file, and Q12 decides whether a
repartition deletes it or keeps and reports it. An archive is never a Git
archive, a zip file or a GitHub release asset.

The preamble of a changelog file is every line before its first section. In
a generated root, it is the header from `changelog-header.md`, followed, when
at least one archive is linked, by the engine-owned link block of Q13: one
relative link per linked archive, newest range first. In a generated archive,
it is a one-line title naming the range, followed by a relative link back to
the root, without the project header. Any other preamble line in the root
stops a generated run before any write (Q04). An existing archive whose
preamble is missing, incomplete or different also stops a generated run
before any write, first render included (Q21): the engine leaves that
preamble in place, shows the two expected lines ready to type (the range
title and the link back, relative to the archive's own location), names each
line to insert, replace or remove, and says why it stopped. An archive whose
preamble passes still receives a missing historical section on a first
render (Q07). A curated file's
preamble belongs to its author: the engine reads it, like the rest of the
file, only for the links that Q13 and Q23 require.

Sections are the unit of every changelog rule. Generated mode rebuilds only
the target's unreleased section and keeps every released section byte for
byte. An archive move carries whole sections, and the completeness check
compares the set of released sections before and after the move. Curated
validation looks for the target section and for the section of every
eligible release (Q05, Q08).

A `.release.ini` file has sections too: its bracketed groups, such as
`[changelog]` and `[changelog-archive:0.1.0-0.13.9]`. This requirement always
names those with their bracketed name or calls them configuration sections;
"section" alone means a changelog section.

### Release notes written by a person

Release notes are the text a person writes about a release, as opposed to the
commit list git-cliff builds from commit messages.

- Generated mode: the release notes are the body of `version.txt`, below its
  first line. llm-shared's `version.txt` starts with
  `0.14.0 -- Groundhog Shares the Stopwatch`, which gives the version and the
  title, then a blank line and the body that opens the `v0.14.0` section
  above. The engine copies that body exactly once into the target section,
  directly under its heading.
- Curated mode: the release notes are what the author writes under the
  release's heading, bullets or paragraphs, such as the bullets of
  `## 0.0.24`; in workspace-halo, they are the whole section. The engine never
  writes, copies or changes those bytes: it only validates headings,
  historical coverage, placement, order and links.
- Once a version is released, its section keeps the release notes it holds,
  with any other text an author added there. This requirement calls that text
  historical or editorial notes: ordinary rendering keeps it byte for byte,
  and an explicit revision (Q01) must keep it.

### Notices that never fail a run

A notice is a message the engine prints on the console for the person running
it, after which the command still succeeds: the exit status stays 0 when
every check passed. A notice is never written into a changelog file and is
never release notes. Its opposite is a failure: a message with a non-zero
exit status, which stops a calling script, `/prepare-release` or the release
`pre` check. Examples:

- curated mode, `version.txt` at `0.0.25-SNAPSHOT` and no `## 0.0.25` yet: a
  notice that the section for `0.0.25` is still to write (Q08);
- curated mode, commits after the tag `v0.0.24` while `version.txt` still
  holds `0.0.24`: a notice pointing to `uver` (Q08);
- a declared archive range that holds no release yet (Q13);
- the report of each converted `=>` line, when the whole conversion succeeds
  (Q15);
- the warnings named below, such as the one-line warning for an ignored
  `.changelog.fixes`, and the message `brel` prints when it reads
  `.changelog.fixes` in memory.

These messages are notices when every check passes; a run that also meets a
failure keeps its non-zero exit status.

## Current behavior before changelog management

- dev_workflow's `uc` alias (`tools/dev_workflow/init.bat:138`) runs
  `update-changelog.bat`, which starts `bash` on `update-changelog.sh`. Its
  `uvf` alias (`init.bat:141`) sets `FORCE_UC=1` and runs
  `update-version.bat`. llm-shared's own `senv.doskey` defines neither alias.
- `update-changelog.sh:10` runs `${PRGS}/git-cliffs/current/git-cliff.exe`
  with dev_workflow's `cliff.toml`, `-w <PRJ_DIR> -s footer -o
  CHANGELOG.tmp.md`. Its one argument picks the part to regenerate (lines 14
  to 39): `latest` or nothing for the range since the nearest tag, a tag name
  for that release section, and the whole history when no `CHANGELOG.md`
  exists yet.
- sed calls then relabel two group headings, strip trailing blank lines and
  carriage returns, and drop version and date fragments (lines 41 to 46).
  When HEAD carries no tag, the `version.txt` body is injected under the
  unreleased heading, which becomes `## [vX.Y.Z-SNAPSHOT unreleased] <title> -
  <full commit hash>`, or `## [vX.Y.Z] - <today> - <title>` for a new release
  (lines 49 to 67).
- The script then removes duplicate sections of the target version with
  `changelog_duplicate_version_section_remover.awk`, prepends
  `changelog-header.md`, labels sections with
  `changelog_section_labeler.awk`, and runs `.changelog.fixes` through Perl
  `s///gee` (lines 95 to 246).
- Every intermediate file lands at the project root: `CHANGELOG.tmp.md`,
  `CHANGELOG.new.md`, `CHANGELOG.cleaned.md`, `CHANGELOG.labeled.md`,
  `version.tmp.txt`, `.fixes_content.tmp` and `tmp_fixes.pl`.
- Writes are not atomic. When a range is regenerated, `CHANGELOG.md` is cut in
  place (lines 76 or 89) before the duplicate remover runs, so a remover
  failure (line 116) leaves it with its top part removed. A labeler failure
  (line 142) stops after `CHANGELOG.md` already received the new sections
  without its header (line 126). A failing Perl run only warns
  `Some rules from .changelog.fixes may have failed to apply.`, discards the
  Perl output and writes the changelog with none of the rules applied (lines
  224 to 248).
- There is no mode: the script always runs git-cliff and always rewrites
  `CHANGELOG.md`, with no setting to leave a hand-written changelog alone.
- Four readers treat a snapshot marker tag as a release, as
  [the snapshot-marker defects](#snapshot-marker-defects-in-dev_workflows-range-readers)
  below show.
- The unreleased heading ends with the full commit hash. `init.bat` lines 78
  to 86 configure a `filter.changelog` clean filter meant to strip it, but no
  `.gitattributes` maps `CHANGELOG.md` to that filter, so it never runs and
  llm-shared's history holds the hashes (for example in `8142624`).
- There are no archives: llm-shared's root `CHANGELOG.md` holds every release
  (2034 lines today).
- Items 1 to 3 are completed and merged into the umbrella integration branch.
  The release engine's shipped schemas are `tooling`, `version` and
  `git-cliff`, so a `[changelog]` or `[changelog-archive:...]` section is
  reported as unknown. Its command registry ships only `version` and
  `versions`. No changelog reader calls item 2's range selector yet, and no
  renderer calls item 3's git-cliff provisioning and invocation yet.

## Scope and ownership boundaries of changelog management

This item owns the renderer and validator, the fix-rule runner and the
changelog and archive settings. It registers the `[changelog]` and
`[changelog-archive:...]` configuration sections with the common reader and
adds the `changelog` and `fixes` commands to the engine. Each dev_workflow
piece it replaces has a fate:

| Legacy piece | Role today | Fate in the engine |
| --- | --- | --- |
| `update-changelog.bat` + `.sh` | git-cliff run, sed clean-ups, `version.txt` body injected under the unreleased heading, header prepended, section labeling, `.changelog.fixes` | Engine `changelog` command, git-cliff kept, sed dropped |
| `cliff.toml` | Commit groups, skipped release chores | Moves to llm-shared as the default; a project `cliff.toml` overrides it |
| `changelog_duplicate_version_section_remover.awk`, `changelog_section_labeler.awk` | Changelog post-processing | Rewritten in Python, awk dropped |
| `update-changelog.fixes.tpl.pl` | Runs `.changelog.fixes` through Perl `s///gee` | Replaced by a Python rules runner, Perl dropped |

After the rewrite, the engine uses llm-shared's Python and Git, plus git-cliff
only for generated changelogs: no `bash`, `sed`, `awk`, `perl` or `cygpath`.

It builds on the three merged items:

- Item 1, `release-project-root`: the explicit validated project root,
  root-scoped Git, dispatch through the self-locating
  `bin/release_workflow.bat` and `bin/release_alias.bat`, the artifact home,
  the common managed-write functions (design decision Q06 A) and the common
  `.release.ini` reader, read with interpolation off, which composes
  explicitly registered domain schemas and validates every declared setting
  before mutation.
- Item 2, `version-sources`: the shared stable/snapshot tag classifier and
  range selector (`tools/release_workflow/tags.py`, exposed as
  `versions <root> range [<stable tag>]`), with the commit count read from
  `git rev-list --count` on the selected range. This item switches the
  changelog readers to that selector.
- Item 3, `git-cliff-provisioning`: the pinned git-cliff 2.14.2, downloaded
  into the executing checkout's ignored `.tools/git-cliff/` cache, checked
  before every use and started only through `GitCliffInvocation`. An engine
  caller that cannot get the binary receives a `ProvisioningError` (status 2)
  with the setup diagnostic. Its approved evidence bundle,
  `tools/release_workflow/git_cliff/bundles/2.14.2/`, compares raw git-cliff
  output of 2.7.0 and 2.14.2 on frozen inputs. Item 3 leaves to this item the
  decision of when rendering needs git-cliff.

The neighboring behaviors stay with their items:

| Behavior outside changelog management | Owning umbrella item |
| --- | --- |
| Pin admission, download, cache and invocation of git-cliff | 3, `git-cliff-provisioning` (completed) |
| The stable/snapshot tag classifier and range selector this item consumes | 2, `version-sources` (completed) |
| Release commit, annotated tag, transaction record and recovery of the affected changelog set; calling rendering or curated validation in release `pre` | 5, `build-release-lifecycle` |
| Proposing an initial archive split and generating `.release.ini` during setup; exposing `uc`/`uvf` to consumers not yet loading llm-shared's alias file | 6, `release-tooling-setup` |
| `/prepare-release` Steps 10 and 11 calling the changelog services, its Step 11 wording, Step 13 staging the rules file, `.release.ini` and archive set, and `prepare_release_notes` | 7, `prepare-release-integration` |
| llm-shared's own archive ranges and rule conversion, removing `filter.changelog` from existing clones, adding the aliases to the shared `senv.doskey`, removing `update-changelog.sh`, and the complete-pipeline parity rehearsals | 8, `llm-shared-cutover` |

The explicit action that revises a released section, the representation and
comparison of section content, and the regeneration mechanism remain design
work.

## Version notation in changelog headings and archives

| Context | Form | Example |
| --- | --- | --- |
| Generated snapshot heading | `vX.Y.Z-SNAPSHOT`, display only | `## [v0.14.0-SNAPSHOT unreleased] <title>` |
| Generated release heading | `vX.Y.Z` | `## [v0.14.0] - YYYY-MM-DD - <title>` |
| Archive bounds in `.release.ini` | `X.Y.Z`, without `v` | `recent-from = 0.14.0` |
| Archive filenames | `vX.Y.Z` | `docs/CHANGELOG.v0.1.0-v0.13.9.md` |
| New stable Git tag / legacy stable tag | `vX.Y.Z` / `X.Y.Z`, both readable | `v0.14.0` / `0.0.21` |

A generated snapshot heading does not imply that a Git tag exists. Curated
changelogs may keep their documented unprefixed heading style. Legacy
unprefixed stable tags remain readable; new stable tags always have `v`.

## Changelog commands and aliases of the engine

This item adds two commands to the engine:

- `changelog <root> [latest|vX.Y.Z]`, which renders a generated changelog or
  validates a curated one;
- `fixes <root> init|convert|dry-run`, which manages the project fix rules.

The `latest|vX.Y.Z` argument carries the choice dev_workflow's single
argument makes today (the latest range or one release section); it is not a
mode. Every command that can prompt also takes a non-interactive form that
fails with a message instead of asking, so `/prepare-release` can drive it
from its own menus.

The `uc` and `uvf` aliases refresh generated changelog content or validate
curated content. Interactive aliases resolve the current Git worktree and pass
that root explicitly; the engine never infers a target from `PRJ_DIR`.

## Per-project changelog settings and their defaults

Existing project files keep their meaning: `version.txt`, `CHANGELOG.md` and
`changelog-header.md`. New ones exist only where a project needs to differ
from the defaults:

- a project `cliff.toml`, overriding llm-shared's default one;
- `.changelog-fixes.toml`, the fix rules (see
  [the fix-rules section](#changelog-fix-rules-without-perl));
- the `[changelog]` and `[changelog-archive:...]` sections of `.release.ini`.

A project without `.release.ini` gets every default; invalid values are never
replaced silently with defaults. Approved release-project-root design decision
Q03 A keeps schemas and defaults beside their owning components: the changelog
component, for example, defines the accepted `generated` and `curated` modes.
The proposed archive policy syntax uses numeric inclusive bounds without `v`:

```ini
[changelog]
; generated (git-cliff, the default) or curated (author-maintained)
mode = generated
recent-from = 0.14.0

[changelog-archive:0.1.0-0.13.9]
from = 0.1.0
to = 0.13.9
file = docs/CHANGELOG.v0.1.0-v0.13.9.md
```

The common config reader validates modes, paths and unknown keys before
mutation, including declarations unused by the current command. Generation,
archives and rules belong to changelog management; the git-cliff pin belongs
to internal provisioning. No consumer runs code from project config.

## Generated and curated changelog modes

Projects keep their `CHANGELOG.md` in one of two ways:

- written by a tool from commit messages: llm-shared and my-project today,
  where dev_workflow runs git-cliff, which turns commits such as `feat: add X`
  and `fix: Y` into a list and rewrites the whole file on every run;
- written by a person: workspace-halo, whose author writes short user-facing
  notes for the VS Code Marketplace, such as `## 0.0.24` followed by bullets.
  A tool that rewrote that file from commit messages would lose those notes.

Each project declares its way with one line in `.release.ini`:

| Setting | Who writes `CHANGELOG.md` | What the engine does |
| --- | --- | --- |
| `mode = generated`, the default | The engine, from commit messages | Rebuilds the file with git-cliff, as dev_workflow does today |
| `mode = curated` | A person, by hand | Never touches the file; only checks that it has a section for the exact version, such as `## 0.0.25` when releasing `0.0.25` |

`generated` names what dev_workflow has always done. `curated` is new: the
effort's first draft introduced it for workspace-halo, which never had
dev_workflow. With these two modes, llm-shared and my-project keep a generated
changelog, while workspace-halo gets the release tooling with its hand-written
changelog left exactly as written: a missing section for the version being
released stops the release with a message, and git-cliff is never needed.

In precise terms, `generated` means commit-derived changelog text owned by the
engine, rendered from Git commits using git-cliff; it is not a separate version
or release lifecycle. `curated` means author-maintained release notes, such as
marketplace-facing bullets. Neither mode changes the version-source forms or
the consuming build gate.

### Curated mode checks without rewriting

In `curated` mode the engine never rewrites `CHANGELOG.md`: it only checks
that a section for the exact release exists. It accepts `## X.Y.Z` and the
documented `vX.Y.Z` and bracketed heading forms, and never a substring match.
It requires neither
git-cliff nor `changelog-header.md`, does not inject notes, dates or fix rules,
and preserves the curated file byte for byte.

`changelog-header.md` is checked only by the `changelog` command, and only in
generated mode.

## Generated changelog contract

Generated mode uses the project's `cliff.toml` or llm-shared's default,
requires `changelog-header.md`, and applies the built-in cleanups followed by
the project fix rules to content being generated. Ordinary rendering preserves
existing released sections; revising them requires the explicit action
described in
[the authority section](#authority-of-released-changelog-sections).

- Inject `version.txt`'s release-notes body exactly once under the target
  heading; rerunning on unchanged inputs gives identical output.
- During a snapshot, use the hash-free unreleased heading described below; at
  release, use `## [vX.Y.Z] - YYYY-MM-DD - <title>`.
- Capture the local release date once for the transaction and reuse it in the
  changelog and the tag annotation.
- Rebuild the target version's unreleased section as one section, replacing
  any earlier unreleased section of that version, and label groups without
  dropping historical entries.
- Never resolve competing released text automatically. When a version has two
  released sections, or the run would create a released section that differs
  from one already present for that version, the run stops before any write,
  names both places and keeps both texts. A present section identical to the
  one the run would create is kept as it is. Duplicate cleanup never selects a
  winner or discards distinct notes.
- Existing tagged releases keep their dates: a rerun never dates them with
  today's date.
- Handle older unprefixed `X.Y.Z` tags when resolving release ranges, while
  newly created tags always use `vX.Y.Z`.

### Recheck of the header and postprocessing against git-cliff 2.14.2

This item rechecks its own header, template and postprocessing against the
pinned git-cliff; item 8's parity rehearsals compare the complete pipelines
before cutover. These upstream changes since 2.7.0 bear on that recheck:

| Releases since 2.7.0 | Relevant changes | Consequence for llm-shared |
| --- | --- | --- |
| [2.10.0](https://github.com/orhun/git-cliff/releases/tag/v2.10.0) | Breaking change to empty default header/footer; include/exclude paths in config; skip-tag evaluation fix | Specify header/footer deliberately and compare generated bytes; skipping a tag must not accidentally discard its commits |
| [2.14.1](https://github.com/orhun/git-cliff/releases/tag/v2.14.1) | Breaking config discovery, multi-value CLI parsing and remote PR-author field changes; graph-reachability release assignment, Windows path matching and nested annotated-tag fixes | Recheck command arguments, merge histories and custom templates; explicit config limits discovery surprises |
| [2.14.2](https://github.com/orhun/git-cliff/releases/tag/v2.14.2) | Multiple commit parsers can apply; all fields of a parser must match; `--workdir` include-path fix | Compare grouping, skip rules and security-body matches in the existing ordered parser list, not just successful execution |

### Hash-free snapshot changelog heading

While a version is a snapshot, dev_workflow ends the generated heading with the
full hash of the commit it was built from:

```text
## [v0.12.0-SNAPSHOT unreleased] Resume Where You Filed It - 911e249c1afef827bd2ab37055e63e1d33b7b3ee
```

Every regeneration after a new commit (`uc`, `uvf`, Step 10 and Step 11 of
`/prepare-release`) changes that line, so `CHANGELOG.md` shows as modified for
a one-hash difference. The engine writes no hash: the unreleased heading ends
at the title.

```text
## [v0.12.0-SNAPSHOT unreleased] Resume Where You Filed It
```

A regeneration then changes `CHANGELOG.md` only when its content changes, with
no Git config or filter to install in each clone. The engine never sets
`filter.changelog`. The parity run against dev_workflow compares that heading
without its hash suffix. An unreleased section left by dev_workflow, with the
hash, is rebuilt with the hash-free heading on the first engine run.

## Stable-tag ranges and snapshot markers in changelogs

A release's changelog lists every commit since the previous real release.
dev_workflow finds that previous release by asking Git for a tag, and every
tag counts. But not every tag is a release: my-project also puts snapshot tags
such as `v0.14.0-SNAPSHOT` on its integration builds. Such a tag is a marker,
meaning "a build was made here", not "this version was released".

### Snapshot-marker defects in dev_workflow's range readers

Example history, oldest first:

```text
v0.13.0           real release
commit A
v0.14.0-SNAPSHOT  marker on an integration build
commit B
HEAD              0.14.0 is being prepared here
```

The `0.14.0` changelog must list A and B. dev_workflow gets it wrong in four
places, each reproduced on this history (Git default version sort, no
`versionsort.suffix` setting):

| Where | What it does | Effect on the example |
| --- | --- | --- |
| `tools/dev_workflow/update-changelog.sh:22` | `git describe --tags --abbrev=0` takes the nearest tag as the start of the range | Returns `v0.14.0-SNAPSHOT`: the range starts at the marker and commit A is silently dropped |
| `tools/dev_workflow/update-changelog.sh:25` | Regenerating one release section takes the tag listed just below it by `git tag --sort=-version:refname` | Git's version order puts `v0.14.0-SNAPSHOT` above `v0.14.0`. Once the history goes on with commit C, `v0.15.0-SNAPSHOT`, commit D and `v0.15.0`, the tag below `v0.15.0` is `v0.14.0-SNAPSHOT`: the `v0.15.0` section lists B again, although `v0.14.0` already released it |
| `tools/dev_workflow/update-changelog.sh:49` | `git describe --exact-match --tags HEAD` decides whether HEAD is already released | With a marker on HEAD, it succeeds: the script treats HEAD as released and skips both the `version.txt` notes and the unreleased heading |
| `tools/dev_workflow/cliff.toml:82` to `:86` | `tag_pattern` is commented out; `skip_tags` and `ignore_tags` are empty | git-cliff opens a release section for every tag, so `v0.14.0-SNAPSHOT` appears as if that version had shipped; even the commented pattern, `v[0-9].*`, would match the markers |

The umbrella's audit of 2026-11-12 assigns these readers: this item replaces
the three `update-changelog.sh` readers (item 8 removes the script) and the
`cliff.toml` tag settings.

### Range rule for snapshot markers in changelog readers

Snapshot tags are development markers, never release boundaries. A range ends
only at an eligible stable release, as item 2's shared selector decides
(umbrella decisions 26 and 34): a complete stable tag, `vX.Y.Z` or the legacy
`X.Y.Z`, reachable from the target, that is not an unvalidated engine release.
git-cliff's release boundaries consume that same decision rather than a
tag-name pattern, even when a project `cliff.toml` sets its own tag settings,
because a stable-name pattern alone also admits an unvalidated engine release.
A tag that is not an eligible release never opens a section, and its commits
stay in the range, on both sides of it. Never exclude such a tag through
`skip_tags`, which drops its commits. With no eligible stable tag, use the
full relevant history.

The range and the changelog entries are counted differently. The selected
range holds every commit since the baseline, and its count is
`git rev-list --count` of that range. The changelog can show fewer entries,
because the commit groups of `cliff.toml` skip some commits on purpose, such as
release chores. Only that commit-group policy removes entries; ignoring a tag
never does.

In the example, preparing `0.14.0` includes A and B from `v0.13.0..HEAD`, even
when HEAD itself has the snapshot tag, and no `v0.14.0-SNAPSHOT` section is
released. Later, the `v0.15.0` section starts at `v0.14.0` and lists C and D
only.

The same holds for an unvalidated engine release, a stable tag whose
annotation still waits for its `[valid]` line:

```text
A        eligible stable release
commit 1
B        stable tag of an unvalidated engine release
commit 2
HEAD
```

`latest` uses the range `A..HEAD`, which holds commits 1 and 2, and git-cliff's
output holds no released B section, even with a project `cliff.toml`. Item 2's
selector reports that it excluded B.

### Snapshot histories each switched reader is tested on

my-project gives the concrete shape: it sets `X.Y.Z-SNAPSHOT` in its sources,
then creates an annotated `vX.Y.Z-SNAPSHOT` tag on the final commit for its
integration build, and commits follow that marker. Every switched reader is
tested on these histories:

- a stable release, then a snapshot marker, then more commits (the marker below
  HEAD, the my-project shape);
- a snapshot marker on HEAD;
- snapshot markers only, and no tag at all;
- legacy snapshot spellings: unprefixed `X.Y.Z-SNAPSHOT` and other suffix cases.

Each must give the range since the last eligible stable release (or the full
history), a commit count equal to `git rev-list --count` of that range, and no
released section for a marker. Reuse the selector tests where they already
establish an outcome and add checks only for real gaps: at selector level, a
HEAD-target range with a marker below HEAD is covered only indirectly, through
a marker inside a tag-targeted range.

## Changelog ranges and archives

### Archive bounds and destinations

Keep `CHANGELOG.md` at the repository root for the current snapshot and recent
stable releases. `.release.ini` defines the recent lower bound and any number
of inclusive archive ranges, each stored as
`docs/CHANGELOG.vA.B.C-vD.E.F.md`. Without ranges, the default remains a single
root file. The settings example above puts releases `0.1.0` through `0.13.9`
in the named archive and stable releases from `0.14.0` onward in the root file.

Compare version triples numerically, never as strings; do not infer ranges
from current file sizes or silently choose new boundaries. Each stable release
section must have exactly one destination. Reject overlapping ranges, reversed
bounds, an uncovered existing release, paths outside `docs/`, and filename
bounds inconsistent with config. Snapshot sections always stay in root. Add
relative links to archives in root and links back to root in archives,
preserving release titles, dates and section content. In generated mode the
links sit in the preambles that "Sections of a changelog file" describes;
curated links may sit anywhere in the file (Q13, Q23).

### Repartition of sections after a bounds change

Authors can change the bounds whenever they choose. In generated mode, the next
`changelog` run previews the affected files and repartitions complete sections
according to the new config, preserving released section bodies and historical
notes. Apply each rule once to content being generated; existing released
sections remain unchanged during ordinary rendering. Assemble and validate the
whole result before replacing any file. Writes cover root, new or changed
archives, and any obsolete engine-owned archive removed after its sections and
links are moved; never remove unrelated files. Repeated runs with unchanged
inputs are identical.

The root is written whenever its link block changes, even when no section
enters or leaves it. For example, splitting `[changelog-archive:0.1.0-0.13.9]`
into `0.1.0-0.9.9` and `0.10.0-0.13.9` moves every section of
`docs/CHANGELOG.v0.1.0-v0.13.9.md` into the two new archives and deletes the
old one under Q12; the root keeps its sections, but its link block now holds
two links, so Q11's preview lists the root, both new archives and the
deletion. A run that renders nothing, such as a rerun on the release whose tag
is on HEAD (Q02, case 1), still runs a pending repartition with Q11's preview
and confirmation; with none pending, it writes nothing and exits 0. A file
kept under Q12 never stands in for a declared destination: when it holds the
only copy of an eligible release, that release is missing from its declared
destination and the run fails as Q05 says.

### Completeness and order checks for archive moves

Two more checks make every move provable (added at the child-draft review,
2026-11-23):

- completeness: every released section present before the run, heading
  included, appears exactly once after it, byte for byte unchanged, in its
  declared destination. The only other released sections are those the run
  explicitly creates, such as the target version's section at release, and
  the only changed ones are those an explicit historical revision targets; the
  proposed changed set lists both kinds apart from the moved sections.
  Otherwise no file is written. For example, when `0.15.0` is released with
  `recent-from = 0.14.0`, the root holds before the run the unreleased
  `0.15.0-SNAPSHOT` section and `[v0.14.0]`, and after it the created
  `[v0.15.0]` section and the unchanged `[v0.14.0]`, while every archive
  section stays unchanged in place;
- order: release sections stay sorted newest first, by numeric version, in the
  root file and in every archive. The order of the `[changelog-archive:...]`
  sections inside `.release.ini` does not matter.

### Gaps between archive ranges

Gaps are checked against existing releases, not against version numbers: no
version follows `0.13.9` directly, since `0.13.10` and later are valid
versions. With `to = 0.13.9` and `recent-from = 0.14.0`, the gap is accepted
while no such release exists, and the run stops naming the first release that
falls in it. A gap holding no release is allowed, but becomes an error once a
newly encountered release would have no destination. A new release cannot land
in an old gap, since a target version must be higher than every eligible
stable release (confirmed answer Q2 A).

### Archive ranges of a curated changelog

In curated mode the same range policy is checked, but files and links remain
author-maintained: archive movement needs author edits, and the engine
validates range placement and links. Report misplaced or duplicate sections
with their expected destination. Do not silently generate, rewrite or archive
curated prose. Q13 and Q23 set which links count, and Q22 the case of a kept
file at the path of a declared range that holds no release. A section naming
no version, such as `## Unreleased`, takes no part in placement.

### Authority of released changelog sections

Existing released sections are authoritative during ordinary generated-mode
rendering (confirmed answer Q3 A). Changed fix rules do not automatically
rewrite released history; historical revisions require an explicit action.
Moving a section between root and archives or between archives preserves its
body. Any intentional historical revision must keep editorial notes and be
visible in the proposed changed set. Conflicting sources must be reported
rather than silently resolved.

## Changelog fix rules without Perl

Today `.changelog.fixes` has two forms, both run by Perl:

- the `# PERL_CODE` form, a Perl fragment of `push @patterns, qr/.../;` and
  `push @replacements, '"..."';` pairs pasted into
  `update-changelog.fixes.tpl.pl`, then applied to the whole changelog with
  `s/$pattern/$replacement/gee`;
- a legacy `regex => replacement` line form, which the bash script turns into
  the same Perl pairs.

The three existing files (llm-shared, my-project, and the template) use only
the `push` pairs: 2 rules in llm-shared, 32 in my-project, covering typo
fixes, empty old release headings filled in, and backticks added around
identifiers. Their patterns use lookbehinds, `\S`, `[\r\n]`, `\s*?` and
non-capturing groups, all of which Python's `re` reads the same way. Their
replacements are Perl double-quoted strings holding `$1` or `\1` and `\n`,
which map to a Python `re.sub` template (`\1`, `\n`).

### Python fix-rule runner replacing Perl

A Python runner replaces Perl completely:

- the three built-in rules of the Perl template (wrap bare URLs in angle
  brackets, drop a single trailing space or tab, turn a leading asterisk list
  marker into a dash) become built-in Python rules, applied first;
- project rules move to `.changelog-fixes.toml`, a declarative file with one
  pattern and one replacement per rule, shown below with llm-shared's two
  rules and one heading fill shaped like my-project's;
- `fixes <root> convert` writes `.changelog-fixes.toml` from an existing
  `.changelog.fixes`, reading only the `push` pairs and the `=>` lines. Any
  other Perl statement stops the conversion and names its line, rather than
  guessing. A `push` pair converts to a rule that matches what the Perl rule
  matched (Q16). A `=>` line converts to what it says (Q15), within the
  pattern and replacement forms Q16 accepts, as an intentional change from
  the legacy effect: its left side is the author's regex, without the quotes
  and the backslash doubling `update-changelog.sh` added, and its right side
  is literal text with its group references. So `v1\.2 => version 1.2`
  matches a literal dot, in the converted rule and in the transition reader
  alike. When the whole file converts, each converted `=>` line gets a notice
  naming it as a behavior change; when any line is unsupported, the command
  fails, naming it, and writes nothing. When `.changelog-fixes.toml` already
  exists, `convert` fails before any write, naming it (Q20);
- `fixes <root> init` creates `.changelog-fixes.toml` when it is missing: by
  conversion when a `.changelog.fixes` exists, otherwise from a commented
  starter template in llm-shared `templates/` (replacing dev_workflow's
  `templates/.changelog.tpl.fixes`). Typed alone while the file exists, it
  changes nothing and exits 0;
- in generated mode, `uc`, `uvf` and `/prepare-release` Steps 10 and 11 run
  that `init` automatically before rendering, so the new file appears in the
  working tree and lands in the prepare commit; item 7 wires the
  `/prepare-release` steps and their Step 13 staging. Curated mode never runs
  the automatic `init`, since it applies no fix rule;
- `brel` never creates the file: a new untracked file would make the tree
  dirty mid-release, outside the release commit. When the TOML is missing,
  `brel` uses the transition reader instead, reading the same subset of
  `.changelog.fixes` in memory, and prints a notice that the next
  `/prepare-release` will convert it automatically;
- once `.changelog-fixes.toml` exists, it is the only rule file read; a
  `.changelog.fixes` still present beside it gets a one-line warning that it is
  ignored and can be deleted;
- `fixes <root> dry-run` replaces the `CHANGELOG_DBG` output of the Perl
  script (Q17). In generated mode it applies, in memory, the built-ins and
  then each project rule in run order to the complete existing root file and
  every existing declared archive, preambles included, and reports counts per
  rule and per file with each line a rule would change. It writes nothing,
  needs no git-cliff, and reads neither undeclared files nor the absent file
  of an empty declared range. Its report says that released sections change
  only through the explicit revision and that a zero count does not prove a
  rule unused. An invalid rule fails it before any report, as below. Q24
  decides what it does in curated mode.

```toml
[[rule]]
pattern = ' _main '
replace = ' `_main` '

[[rule]]
pattern = '(?<!`)draft\.vX\.Y\.Z\.<slug>\.md'
replace = '`draft.vX.Y.Z.<slug>.md`'

[[rule]]
pattern = '\[v4\.1\.0\] -\s*?[\r\n]'
replace = '[v4.1.0] - New doc created instead of rereading inputPDF\n'
```

A rule whose pattern does not compile in Python, or whose replacement uses an
invalid escape or a group the pattern does not define, fails the run with the
rule number and the reason, before any file is written, even when the rule
would match nothing. Today, a failing Perl run only warns, and
`update-changelog.sh` then writes the changelog with none of the rules
applied.

## Operations that need git-cliff for changelog work

In generated mode, `uc`/`uvf` and release-note preparation perform the
git-cliff preflight before automatic `fixes init`, so a missing tool cannot
leave a newly created rule file behind. In curated mode they run neither
git-cliff nor the automatic `fixes init`. Release preprocessing uses the
transition reader and never creates that file mid-release.

| Operation | Needs the provisioned binary |
| --- | --- |
| `changelog` in generated mode, including `uc` | Yes |
| Curated-mode validation | No |
| `fixes convert`, and `fixes dry-run`, which uses existing text | No |
| A snapshot command, which does not regenerate a changelog | No |

| Situation | Generated `uc` | Curated validation and version commands |
| --- | --- | --- |
| Pinned git-cliff absent from the internal cache | Downloads and verifies it automatically before writing | Need no binary |
| Internal git-cliff unavailable and download or verification fails | Fails with the internal path, version and setup or network diagnostic | Remain available |

## Writes and temporary files of changelog work

Render, inject, clean, label, fix and validate in memory or in unique artifact
files, then replace the root changelog and affected archives only after every
phase succeeds, together with any `.changelog-fixes.toml` the run's automatic
`init` converted or created (Q19). Missing headers, invalid config or rules,
git-cliff failure, a declined repartition and invalid output leave the
previous changelog intact and leave no new rules file; a failure during the
writes restores the files already written and removes that new rules file.
Expose the exact write and delete set, rules file included, so preparation
and release recovery (item 5) can restore it.

The Python engine keeps most of the legacy intermediate steps in memory; a
file that remains, such as the git-cliff output, goes to the project artifact
home, following [`rules/artifact_files.md`](../../rules/artifact_files.md).
Consumer scratch files never go into the tooling checkout.

Approved release-project-root design decision Q06 A uses common Python
functions to check destinations and perform managed writes: changelog
functions prepare content and ask those functions to check the destination and
write `CHANGELOG.md`. A junction can redirect a destination after initial
validation, so the common functions recheck physical containment and
repository boundaries before preparing artifacts or writing. Read-only
resolution creates no artifact directory.

## Umbrella decisions carried into changelog management

| # | Topic | Decision |
| --- | --- | --- |
| 2 | Fix-rules file | Preparation automatically converts legacy `.changelog.fixes` when TOML is missing; `convert` is an optional maintenance command; direct `brel` can use the in-memory transition reader |
| 10 | Snapshot hash noise | No hash in the unreleased heading; `filter.changelog` dropped |
| 22 | Changelog modes | Generated means commit-derived text with notes, date and fixes; curated means author-maintained bytes validated for exact headings and ranges, with no git-cliff or header dependency |
| 26 | Snapshot tags | Development markers, never stable release baselines, release menu choices or recovery targets; classification shared across engine, changelog, notes and release-plan readers |
| 27 | Changelog archives | Root holds recent releases and the current snapshot; explicit mutable numeric ranges assign older sections to `docs/CHANGELOG.vA.B.C-vD.E.F.md`; reject overlap, loss and duplicates; preserve curated prose |
| 38 | Historical changelog authority | Preserve existing released generated sections during ordinary rendering; changed rules do not rewrite history automatically. Revisions require an explicit action, preserve editorial notes and expose conflicts and changes; archive moves preserve bodies and curated bytes remain unchanged (Q3 A) |

## Consumer inputs shaping changelog management

These repositories shape the need. Their own migrations stay in their own
efforts; llm-shared's belongs to item 8.

- llm-shared: generated changelog with `changelog-header.md` and 2 fix rules;
  its cutover converts them and chooses archive ranges, such as `0.1.0` to
  `0.13.9` in `docs/CHANGELOG.v0.1.0-v0.13.9.md`.
- my-project: generated changelog with 32 fix rules, and the snapshot-marker
  history described above.
- workspace-halo: its `CHANGELOG.md` is hand-written, marketplace style
  (`## 0.0.24` with user-facing bullets), and ships inside the VSIX. git-cliff
  output would replace it with commit subjects, so it needs the `curated` mode,
  with no `changelog-header.md`; it then never needs git-cliff either. Its tags
  mix `0.0.21`, `0.0.22` and `v0.0.20`, `v0.0.23`, `v0.0.24`: the changelog
  range search must not trip on the older unprefixed tags. Its tags start at
  `v0.0.20`, while its file holds sections down to `## 0.0.1`. With an
  existing curated root, eligible tags starting at `v0.0.20` and a historical
  heading `## 0.0.1`, curated validation fails and names `0.0.1`, even when
  its archive path and both links are correct (Q05, Q08); an eligible
  reachable unprefixed tag such as `0.0.21` counts normally, and validation
  leaves every file intact. workspace-halo's own effort settles its untagged
  sections `0.0.1` to `0.0.19` before it adopts curated validation.

## Gap to close in the implementation for changelog management

1. Register the `[changelog]` and `[changelog-archive:...]` domain schemas
   with the common reader: `mode` (`generated` by default, or `curated`),
   `recent-from`, and each archive's `from`, `to` and `file`, validated before
   mutation, including declarations the current command does not use.
2. Add `changelog <root> [latest|vX.Y.Z]` and `fixes <root> init|convert|dry-run`
   to the command registry, with a non-interactive form for every command that
   can prompt, and let the `uc` and `uvf` aliases pass the current worktree
   root explicitly.
3. Ship llm-shared's default `cliff.toml`, honor a project `cliff.toml` that
   overrides it, and make git-cliff's release boundaries the eligible stable
   releases item 2's selector reports, whatever a project `cliff.toml` sets,
   never excluding a tag through `skip_tags`.
4. Render a generated changelog: select the range through item 2's selector,
   run git-cliff through item 3's provisioning and invocation, require
   `changelog-header.md`, inject the `version.txt` notes once, write the
   hash-free snapshot heading, its untagged stable form (Q02) or the dated
   release heading with the captured release date, rebuild the target's
   unreleased section once, stop on
   competing released sections while keeping both texts, label groups, and
   keep released sections and their dates.
5. Validate a curated changelog: exact supported headings, sections naming no
   version kept as boundaries, range placement and links (Q13, Q22, Q23),
   with the file preserved byte for byte and no git-cliff, header or
   fix-rule prerequisite.
6. Apply the archive policy: numeric bounds and destinations, repartition of
   complete sections when bounds change, the root and archive preambles with
   links in both directions (Q13, Q21), an existing file for an empty declared
   range (Q22), removal of obsolete engine-owned archives, and the
   completeness check (each
   pre-existing released section exactly once, byte for byte, with created and
   revised sections listed apart) and the newest-first order check before any
   write.
7. Keep released sections authoritative: revise them only through an explicit
   action that keeps editorial notes, reports competing content sources and
   shows each intentional revision in the proposed changed set.
8. Replace the Perl fix step with a Python runner: built-in cleanups first,
   then `.changelog-fixes.toml` rules on content being generated; `convert`
   (Q15, Q16, Q20), `init` and `dry-run` (Q17, Q24); the in-memory
   transition reader for `brel`; the
   warning for an ignored `.changelog.fixes`; and a failure naming the rule
   whose pattern or replacement is invalid, even when it matches nothing.
9. Run the git-cliff preflight in generated-mode `uc`, `uvf` and preparation
   before the automatic `fixes init`, and keep curated validation (which skips
   that `init`), conversion, dry runs and snapshot commands free of git-cliff.
10. Assemble and validate the complete output before any write, keep remaining
    intermediate files in the artifact home through the common managed-write
    functions, restore the complete affected changelog set on failure,
    including a rules file the automatic `init` converted or created (Q19),
    and expose the exact write and delete set to preparation and release
    recovery.
11. Compare the engine's output with dev_workflow's on the same frozen inputs
    (Q18) and document each intentional difference, including the hash-free
    heading, the snapshot-marker ranges and the effect of llm-shared's two fix
    rules. The comparison covers generated root-only output with no archive
    declared, since dev_workflow writes no archive and has no curated mode;
    archives and curated validation are tested against the engine's own
    expected results.

## Acceptance criteria for changelog management

- Generated mode uses the explicit project or default `cliff.toml`, the
  required header and stable-tag range selection, injects the release notes
  once, labels groups, preserves historical notes and dates, and leaves one
  section for the target version; competing released sections stop the run
  with both texts kept. Repeated runs on unchanged inputs produce
  identical output. Existing released sections are preserved during ordinary
  rendering, including when fix rules change. Historical revisions require an
  explicit action, preserve editorial notes, report competing content sources
  and appear in the proposed changed set. Archive moves preserve section
  bodies. The documentation points authors to `version.txt` for release notes
  and to fix rules for wording corrections (Q06).
- Headings are the hash-free `## [vX.Y.Z-SNAPSHOT unreleased] <title>`, its
  untagged stable form `## [vX.Y.Z unreleased] <title>` (Q02), and the dated
  `## [vX.Y.Z] - YYYY-MM-DD - <title>` with the captured release date.
  No `filter.changelog` is set. Snapshot tags never truncate commits or create
  a released section, including a snapshot marker on HEAD. git-cliff's release
  boundaries are the eligible stable releases of item 2's selector, so neither
  a snapshot marker nor an unvalidated engine release opens a section, even
  with a project `cliff.toml`; no tag is excluded through `skip_tags`, and
  only the commit groups remove entries from the selected range.
  The readers of `update-changelog.sh` and `cliff.toml` listed in
  [the snapshot-marker defects](#snapshot-marker-defects-in-dev_workflows-range-readers)
  are replaced and tested on the
  [snapshot histories](#snapshot-histories-each-switched-reader-is-tested-on).
- The numeric recent and archive policy applies to the root file and
  `docs/CHANGELOG.vA.B.C-vD.E.F.md` archives, validating bounds, destinations,
  overlap, coverage and links. A bounds change repartitions complete sections,
  including the removal of an owned obsolete archive, without losing content.
  Before writing, every pre-existing released section, heading included, is
  proven present exactly once and byte for byte unchanged, with explicitly
  created or revised sections listed apart, and sections stay sorted newest
  first in the root file and every archive. A generated root's preamble is its
  header and link block, newest range first, and a generated archive's is its
  range title and link back (Q13). A root whose link block alone changes is in
  the preview and the write set (Q11), and a rerun on the release whose tag is
  on HEAD still runs a pending repartition (Q02). An existing archive with an
  invalid preamble stops a generated run before any write, with a failure
  that shows the two expected lines ready to type, the edits needed and why
  (Q21).
- Curated mode validates exact supported headings (including `## X.Y.Z`),
  ranges and links while preserving every file byte, with no automatic
  generation, archive movement, git-cliff, header or fix-rule prerequisite.
  A section naming no version, such as `## Unreleased`, is kept and left out
  of the version checks, while a heading that looks versioned but fits no
  form fails. In a file holding both a fenced `## 0.0.25` example and the
  real `## 0.0.25` heading, only the real heading counts.
- Built-in cleanups apply before TOML rules to content being generated, and
  existing released sections are preserved during ordinary rendering.
  Conversion accepts only the supported Perl `push` pairs and legacy `=>`
  lines; an unsupported line, or a rule whose pattern or replacement is
  invalid, is named and fails the run, even when it would match nothing. TOML
  wins over the legacy file with a warning, and a dry run reports match counts
  per rule and per file with the lines it would change. A `=>` line such as
  `v1\.2 => version 1.2` matches a literal dot in the converted rule and in
  the transition reader alike, and is reported as an intentional change.
  `convert` fails over an existing `.changelog-fixes.toml`.
- In generated mode, `uc`, `uvf` and preparation provision and check git-cliff
  before the automatic `fixes init` or conversion; curated validation needs
  neither git-cliff nor that `init`. A direct release uses the in-memory
  transition reader and never leaves a new untracked rules file in the tree.
- All output is assembled and validated before any write, and a failure
  restores the complete affected changelog set, including a rules file the
  automatic `init` converted or created (Q19). Intermediate files are unique
  project artifacts, and the exact write and delete set is exposed to
  preparation and release recovery. Generated root-only output is compared
  with legacy output recorded once on frozen inputs (Q18), with the
  intentional differences documented, including the two llm-shared rules;
  archives and curated validation are tested against the engine's own
  expected results.

## Code references for changelog management

- `tools/dev_workflow/update-changelog.sh`: the legacy pipeline (git-cliff call
  at line 10, range readers at lines 22, 25 and 49, sed clean-ups at lines 41
  to 46, in-place cuts at lines 76 and 89, failures at lines 116 and 142, Perl
  fix step at lines 148 to 246, final move at line 248).
- `tools/dev_workflow/update-changelog.bat` and `tools/dev_workflow/init.bat`:
  the `uc` and `uvf` aliases (lines 138 and 141), the `changelog-header.md`
  check (lines 73 and 74) and the unused `filter.changelog` setup (lines 78 to
  86).
- `tools/dev_workflow/cliff.toml`: commit groups and the commented-out tag
  settings (lines 82 to 86); llm-shared's default `cliff.toml` replaces it.
- `tools/dev_workflow/changelog_duplicate_version_section_remover.awk` and
  `tools/dev_workflow/changelog_section_labeler.awk`: the duplicate remover
  and section labeler, rewritten in Python.
- `tools/dev_workflow/update-changelog.fixes.tpl.pl`: the Perl template with
  the three built-in rules and the `CHANGELOG_DBG` match counts.
- `tools/dev_workflow/templates/.changelog.tpl.fixes`: the starter rules
  template an llm-shared `templates/` file replaces.
- `.changelog.fixes`, `changelog-header.md`, `CHANGELOG.md` and `version.txt`
  at llm-shared's root: its two `push` rules, header, single root changelog
  and release-notes anchor.
- `tools/release_workflow/schemas.py`: `SHIPPED_SCHEMAS` holds the `tooling`,
  `version` and `git-cliff` domains; this item adds the changelog domain.
- `tools/release_workflow/configuration.py`: the common `.release.ini` reader,
  with interpolation off, that rejects unknown sections and keys before
  mutation.
- `tools/release_workflow/cli.py`: `SHIPPED_HANDLERS`, today only `version` and
  `versions`.
- `tools/release_workflow/tags.py`: `parse_name`, `classify` and
  `select_range`, the stable/snapshot classifier and range selector.
- `tools/release_workflow/git_cliff/provisioning.py`,
  `tools/release_workflow/git_cliff/invocation.py` and
  `tools/release_workflow/git_cliff/messages.py`: `provision`,
  `GitCliffInvocation` and `ProvisioningError`, the provisioning entry point,
  invocation and failure this item calls.
- `tools/release_workflow/managed_files.py`: `authorize_write`,
  `temporary_bytes` and `replace_bytes`, the common managed-write functions.
- `tools/release_workflow/artifacts.py`: `resolve_artifacts` and
  `prepare_artifacts`, the project artifact home.
- `bin/release_workflow.bat`, `bin/release_alias.bat` and `bin/gcliff.doskey`:
  the self-locating launchers and the alias fragment pattern the `uc` and
  `uvf` aliases can follow.

## Open questions for the v0.14.0 changelog-management feature request

### Q01: What `changelog <root> vX.Y.Z` does for a version already released

Question description: dev_workflow's tag argument (`update-changelog.sh`,
lines 24 to 36) regenerates the section of an existing annotated tag: it cuts
`CHANGELOG.md` above the previous tag's section, renders that range again and
puts it back. The requirement keeps that argument as
`changelog <root> [latest|vX.Y.Z]`, but it also makes existing released
sections authoritative: ordinary rendering never rewrites them, and a
historical revision needs an explicit action whose form remains design work.
It does not say whether naming an already released `vX.Y.Z` is that explicit
action, is refused, or names something else, such as the version about to be
released. Umbrella decision 38 accepts either an explicit revision through this
argument or a separately named action. The question concerns generated mode
only: in curated mode, every option below makes `changelog <root> vX.Y.Z` a
read-only lookup that checks the named version has one section, with an
accepted heading, in its declared destination, and checks the links. It never
rewrites notes and never needs git-cliff.

#### BBQ for Q01

A bakery keeps a ledger of past orders written in ink. The new order form has
a box for an order number. Writing an old number in that box could mean
"rewrite that old ledger page" or could be a mistake to refuse. If the form
silently rewrites the inked page, last year's notes in the margin disappear.
In this picture: the ledger is `CHANGELOG.md`, the inked pages are released
sections, the margin notes are the editorial notes Q3 A keeps, the
order-number box is the `vX.Y.Z` argument, and rewriting the page is a
historical revision.

#### Options for Q01

- Option A: `vX.Y.Z` names only a version with no stable tag yet: the version
  being prepared, which must match `version.txt`. Naming an already released
  version refuses before any write, with a message naming the separate
  revision action. `latest`, or no argument, renders the current range.
  - pro: one command cannot rewrite history, even after a confirmation, as
    Q3 A requires.
  - pro: the release flow (item 5) can name its target explicitly.
  - con: changes inherited behavior: regenerating one released section, the
    documented use of dev_workflow's tag argument, then needs the revision
    action, whose form is design work.
- Option B: naming a released `vX.Y.Z` is the explicit revision action: the
  run renders that section's range again and shows a preview of the proposed
  change, naming the file that holds the section (root or archive), keeping
  editorial notes and reporting conflicts. It writes only after confirmation,
  or with an explicit acceptance option in the non-interactive form; without
  it, nothing is written. Naming the target version (the `version.txt`
  version, with no stable tag yet) renders it as usual, and a version that is
  neither released nor the target is refused.
  - pro: keeps the documented single-release use of the legacy tag argument,
    now protected by a preview and an acceptance, as decision 38 permits.
  - pro: no second command to learn.
  - con: the same argument means "prepare" for the target and "revise" for an
    old version; only the preview and the acceptance stop a typo.
- Option C: drop the `vX.Y.Z` argument from this item: `changelog <root>`
  always renders the current range, snapshot or release target, and
  revisions get their own command later.
  - pro: smallest command surface.
  - con: contradicts the umbrella's listed form
    `changelog <root> [latest|vX.Y.Z]`.
  - con: item 5 then has no way to name the release target explicitly.

#### Recommended option for Q01 (with arguments for this choice)

Option B: it keeps the inherited meaning of the legacy tag argument and makes
it the explicit action decision 38 asks for: nothing is written without a
preview and an acceptance, so a typo shows a preview instead of rewriting
history. Option A is a workable change of that inherited behavior if the
human prefers a separately named action. (Round 1 of the independent review
moved this recommendation from A to B.)

#### Answer to Q01: option B (with reason why it must be accepted as the answer)

Option B: the single-release use authors know from dev_workflow keeps
working, released sections still change only through an explicit, previewed
and accepted action, and the target version renders as before. Curated mode
only looks the version up, without rewriting notes or needing git-cliff.

User decision: confirmed — option B: in generated mode, naming a released
`vX.Y.Z` is the explicit revision action, shown as a preview and written only
after acceptance (an explicit acceptance option in the non-interactive form);
the version being prepared renders as usual; in curated mode the argument is a
read-only lookup.

Decided by the user on 2026-11-24, during the question explanation after
review round 3, choosing the recommended option.

### Q02: Rendering when `version.txt` names a version that is already released

Question description: llm-shared's `version.txt` reads
`0.14.0 -- Groundhog Shares the Stopwatch` today; the tag `v0.14.0` exists and
many commits follow it. Tracing `update-changelog.sh` in that state (read, not
run): HEAD has no tag, so the `version.txt` notes go under
`## [v0.14.0 unreleased] ... - <hash>` (line 63); the duplicate remover then
deletes every `v0.14.0` section, since its pattern `^## \[v0.14.0[ \-\]]` also
matches the released `## [v0.14.0] - 2026-11-12 - ...` heading. The released
section and its commit list would be replaced by an unreleased section holding
only the newer commits. The legacy `uvf` avoided this by first offering the
next snapshot (`update-version.bat`, lines 207 to 216); in the umbrella, `uver`
owns that next-snapshot transition. The requirement defines the snapshot and
release headings, but not what a generated render does when `version.txt`
holds a stable `X.Y.Z` that a stable tag already reserves, nor which heading an
untagged stable `X.Y.Z` gets outside a release (item 2 accepts both `X.Y.Z` and
`X.Y.Z-SNAPSHOT` in the anchor). Item 2 separates two notions here. A version
is reserved by any stable tag that names it, `vX.Y.Z` or `X.Y.Z`, whatever its
state (validated, historical or an unvalidated engine release) and whether or
not HEAD reaches it. A range baseline is only an eligible stable release that
HEAD reaches. An unvalidated `v0.14.0` tag, for example, reserves `0.14.0` but
is no baseline. More cases are open: a repeated run right after a release,
when HEAD itself carries the tag; an unvalidated engine release on HEAD; a
missing root file; a run whose only work is a pending repartition after a
bounds change (Q11); and the order in which these checks apply, which Q08
reuses for curated validation.

#### BBQ for Q02

The scoreboard says "Round 14", round 14 is over, and new scores keep coming
in. The scorekeeper can write the new scores under "Round 14", wiping the
finished round, or stop and ask someone to turn the board to round 15. In
this picture: the scoreboard is `version.txt`, the finished round is the
released `v0.14.0` section, the new scores are the commits after the tag,
wiping is the duplicate remover's deletion, and turning the board is the
`uver` next-snapshot transition.

#### Options for Q02

- Option A: outside a release, an ordinary generated refresh (`uc`, `uvf`, or
  `changelog <root>` with `latest` or no argument) classifies the
  `version.txt` version in this order, and the first matching case decides:
  1. an eligible release of this history, as item 2 decides, whose tag is on
     HEAD, as in a repeated run right after a release. When the changelog
     files exist and pass Q05's check, there is nothing to render: the
     released section stays as it is and the run exits 0; a pending
     repartition alone may still run, with the preview and confirmation of
     Q11. When they fail that check, for example with no section for that
     release, the run stops as Q05 says. When the root file is missing, the
     first render of Q07 creates it, with that release's section;
  2. an eligible release of this history whose tag is below HEAD, with
     commits after it: the refresh refuses before any write, naming the tag
     and pointing to `uver`;
  3. a version reserved only by a tag that is not a release of this history:
     an unvalidated engine release, on HEAD or not, or a tag HEAD does not
     reach, such as one on another branch. The refresh refuses before any
     write, naming the tag and its state, and points to item 5's release
     recovery for an unvalidated release, or to `uver` for a version taken
     elsewhere;
  4. a version no stable tag reserves: the forthcoming target. The unreleased
     heading shows the token as written, `## [vX.Y.Z unreleased] <title>` for
     an untagged stable version and `## [vX.Y.Z-SNAPSHOT unreleased] <title>`
     for a snapshot, and the notation table documents both forms together.

  A refusal covers the whole refresh, so a pending repartition waits until its
  cause is fixed. It never applies to the explicit historical revision of
  Q01, which names its version and has its own preview and acceptance. The
  range baseline stays item 2's eligible stable release, which can differ from
  a reserving tag.
  - pro: no render can ever replace a released section, and the message says
    what to do next.
  - pro: the heading tells the truth about the anchor, and a run right after a
    release stays harmless.
  - con: two unreleased heading forms instead of one.
- Option B: the same four cases in the same order, but the unreleased heading
  always shows `vX.Y.Z-SNAPSHOT`, whatever suffix the token has.
  - pro: one unreleased heading form, as the notation table lists it.
  - con: the heading shows a suffix that `version.txt` does not hold.
- Option C: no refusal: render whatever `version.txt` says and leave a reused
  version to the release preflights (item 2's uniqueness rule, enforced by
  items 5 and 7).
  - pro: `uc` never blocks during development.
  - con: in llm-shared's current state, the render would repeat the `v0.14.0`
    notes or touch a released section, which the authority rule forbids.

#### Recommended option for Q02 (with arguments for this choice)

Option A: it closes the exact path through which a released section is lost
today, applies item 2's uniqueness rule early with a useful message, and
keeps the heading faithful to the anchor. The second heading form appears only
in the short window where a stable version is set but not yet tagged. Keeping
the reserved version apart from the range baseline follows item 2, so an
unvalidated tag blocks reuse of its version without becoming a baseline, and
the fixed order gives exactly one outcome for every anchor.

#### Answer to Q02: option A (with reason why it must be accepted as the answer)

Option A: the generated changelog must never trade a released section for an
unreleased one, and the person running `uc` learns at once that the next step
is `uver`. Showing the token as written avoids a heading that disagrees with
`version.txt`.

User decision: confirmed — option A: an ordinary generated refresh classifies
the `version.txt` version in four ordered cases (an eligible release of this
history on HEAD: nothing to render when the files pass Q05, first render when
the root is missing; an eligible release below HEAD: refusal pointing to
`uver`; a version reserved only by an unvalidated or unreachable tag: refusal
naming the tag; an unreserved version: the forthcoming target), and the
unreleased heading shows the token as written, `## [vX.Y.Z unreleased] <title>`
or `## [vX.Y.Z-SNAPSHOT unreleased] <title>`.

Decided by the user on 2026-11-24, during the question explanation after
review round 3, choosing the recommended option.

### Q03: What `uvf` does that `uc` does not

Question description: in dev_workflow, `uc` runs `update-changelog.bat`
directly, while `uvf` runs `update-version.bat` with `FORCE_UC=1`. That script
reads `version.txt`, offers to create the next snapshot when the current
stable version is tagged and commits follow it (lines 207 to 216, choice at
line 268), and forces the changelog regeneration it otherwise skips during a
snapshot (lines 534 to 547). The umbrella gives both aliases one meaning
("`uc` and `uvf` refresh generated changelog content or validate curated
content") and moves the next-snapshot choice to `uver`. The requirement does
not say what, if anything, still sets `uvf` apart.

#### BBQ for Q03

A grill has two buttons, "light" and "light, force". If both now do exactly
the same thing, the second one is a habit kept for old hands; if "force"
first checks the gas level, it earns its place. In this picture: the buttons
are `uc` and `uvf`, lighting is refreshing or validating the changelog, and
checking the gas is a read-only version check before the refresh.

#### Options for Q03

- Option A: `uvf` runs the same command as `uc`. It is kept so existing habits
  keep working, and it never prompts for a next snapshot (the Q02 refusal
  points to `uver`).
  - pro: matches the umbrella's single meaning for both aliases.
  - pro: nothing to specify or test beyond the alias itself.
  - con: two names for one action.
- Option B: `uvf` first runs item 2's read-only `versions check` and stops on
  drift, then refreshes the changelog like `uc`.
  - pro: gives `uvf` a distinct, read-only meaning close to its legacy name.
  - con: a version drift then blocks a changelog refresh that does not
    depend on it.
- Option C: `uvf` keeps the legacy behavior: when needed, it runs the
  next-snapshot transition before the refresh.
  - pro: closest to the legacy alias.
  - con: duplicates `uver`, which the umbrella makes the separate
    next-snapshot transition, and adds a version write to a changelog alias.

#### Recommended option for Q03 (with arguments for this choice)

Option A: the umbrella already states one meaning for both aliases, and the
only part of the legacy `uvf` that differed, the next-snapshot choice, now
belongs to `uver`. Keeping `uvf` as a plain alias costs nothing and avoids
breaking muscle memory.

#### Answer to Q03: option A (with reason why it must be accepted as the answer)

Option A: it follows the umbrella's alias semantics without inventing a new
check, and the next-snapshot step stays in one place, `uver`.

User decision: confirmed — option A: `uvf` runs the same command as `uc`,
kept so existing habits keep working; it never prompts for a next snapshot,
which `uver` owns.

Decided by the user on 2026-11-24, during the question explanation after
review round 3, choosing the recommended option.

### Q04: Which existing headings identify a released section, and what happens to other content

Question description: archive moves, the completeness check and the
authority rule all work on "released sections", but the requirement names only
the two headings the engine writes. llm-shared's `CHANGELOG.md` already holds a
second released form without a date: `## [v0.2.0] - Green is not the same as
done` and `## [v0.1.0] - Handoffs for the prompt-workflow cycle`, while later
ones read `## [v0.14.0] - 2026-11-12 - Groundhog Shares the Stopwatch`. The
legacy postprocessing strips dates from rendered release headings (line 46),
so other projects may hold date-less headings too, and the requirement accepts
legacy unprefixed `X.Y.Z` tags. A generated file can also contain text the
engine did not write: a preface below the header, or `## 0.0.24`-style
sections left by a project that switched from curated to generated. The
requirement does not say which heading forms count, whether an existing
heading is kept as it is, or what happens to content outside every recognized
section.

#### BBQ for Q04

A librarian moving books to the basement recognizes them by the spine label.
Some old books carry a label without a year; a few shelves hold loose leaflets
with no label at all. Moving only what is recognized and binning the leaflets
loses them; refusing to move anything until each one is labeled keeps them
safe. In this picture: the books are released sections, the spine labels are
their headings, labels without a year are the date-less
`## [v0.2.0] - <title>` headings, the leaflets are preface text or
curated-style sections, and the basement is the archive files.

#### Options for Q04

- Option A: recognize a fixed set of released headings: the dated
  `## [vX.Y.Z] - YYYY-MM-DD - <title>`, the date-less `## [vX.Y.Z] - <title>`,
  and the same two with an unprefixed `X.Y.Z`. Keep each existing heading byte
  for byte, with no date added to a date-less one. The unreleased headings are
  explicit exceptions: the engine owns them and rebuilds their section on each
  run. They are the hash-free forms (the snapshot form, plus the untagged
  stable form if Q02 A is chosen) and the same forms ending with a dash and
  the full commit hash, as dev_workflow wrote them. For example, the first
  run replaces a section headed
  `## [v0.12.0-SNAPSHOT unreleased] Resume Where You Filed It - 911e249c1afef827bd2ab37055e63e1d33b7b3ee`
  with one headed `## [v0.12.0-SNAPSHOT unreleased] Resume Where You Filed It`.
  A line inside a fenced code block is never a heading, so a
  `## [v0.1.0] - ...` line in an example stays part of the section that holds
  the block. Content before the first section other than the header and the
  archive links, or any other level-two heading, stops the run with its line
  named, and nothing is written.
  - pro: every byte has a known owner, so the completeness check can prove a
    move.
  - pro: llm-shared's current file passes unchanged.
  - con: a project with an unusual heading must fix it by hand before its
    first run.
- Option B: recognize any level-two heading that starts with `[` and a stable
  version; keep unrecognized content in place, attached to the section above
  it, with a warning.
  - pro: never blocks a run.
  - con: a stray paragraph silently travels with a section into an archive,
    and a warning in an automated run is easy to miss.
- Option C: normalize: rewrite recognized headings to the dated form, with a
  date taken from the tag, and drop unrecognized content.
  - pro: uniform output.
  - con: rewrites released sections, which Q3 A forbids, and loses content.

#### Recommended option for Q04 (with arguments for this choice)

Option A: the completeness check compares sets of released sections, so the
engine must know exactly where each one starts and ends. Accepting the
date-less form keeps llm-shared's history as it is, and stopping on unknown
content is the only behavior that neither loses nor silently moves it. Naming
the unreleased headings, including dev_workflow's hash-bearing ones, lets the
first engine run migrate them, and ignoring fenced examples keeps a quoted
heading from splitting a section.

#### Answer to Q04: option A (with reason why it must be accepted as the answer)

Option A: it covers the heading forms that exist today without rewriting any
of them, and it turns unknown content into a named, fixable stop instead of a
silent move, which keeps the "every move is provable" promise.

User decision: confirmed — option A: a fixed set of released headings (dated
and date-less, with `vX.Y.Z` or `X.Y.Z`) kept byte for byte; the unreleased
headings, including dev_workflow's hash-bearing ones, are rebuilt on each run;
lines inside fenced code blocks are never headings; any other content before
the first section or under an unrecognized level-two heading stops the run,
naming its line, before any write.

Decided by the user on 2026-11-24, during the question explanation after
review round 3, choosing the recommended option.

### Q05: Whether tags or sections define the existing releases

Question description: coverage ("an uncovered existing release"), the gap rule
("checked against existing releases") and the one-destination rule all count
existing releases. In generated mode, sections and stable tags usually agree:
llm-shared has 13 of each, and no `v0.11.0`, a gap that holds no release. They
can differ, though: a stable tag whose section was never rendered, or a
section with no tag, such as a curated `## 0.0.25` written before `0.0.25` is
released, a release section written during the release transaction before
its tag, or one left by a failed release. Not every stable tag is a release of
this history, either: item 2's selector counts only the eligible stable
releases that HEAD reaches, while any stable tag, in either spelling, reserves
its version (Q02). The requirement does not say which source is
authoritative, nor what a mismatch does, nor how the check differs between a
first render, where no section exists yet, and existing files, including an
archive that already holds sections while the root file is missing.

#### BBQ for Q05

A wine cellar has a register of bottles and the bottles on its racks. Placing
bottles by the register can reserve a rack for a bottle that is not there;
placing them by what stands on the racks can miss a registered one. In this
picture: the register is the list of stable Git tags, the bottles on the
racks are the released sections in the files, the racks are the root file and
the archives, and a bottle with no register entry is a section with no tag.

#### Options for Q05

- Option A: the sections in the files are what gets placed, and the releases
  of this history are checked against them:
  - the releases of this history are the eligible stable releases HEAD
    reaches, as item 2's selector defines them, with the `vX.Y.Z` and `X.Y.Z`
    tags of one version on one commit counted once; they are also the range
    baselines;
  - existing changelog (the root file exists): each release of this history
    needs exactly one section across the root and the archives, and each
    released section needs a release of this history, except the section of
    the version being prepared or released, which may exist before its tag.
    A release with no section, a section with no tag, and a section whose
    version only an unvalidated or unreachable tag names are reported by name
    and stop the run before any write;
  - first render (the root file is missing, whatever archives exist): nothing
    is checked before rendering. Sections already in an archive count as
    present and stay byte for byte. The render creates a section for each
    release of this history that no file holds, in its declared destination:
    the root, a new archive file, or an existing archive, where the new
    section is inserted in newest-first order and the file keeps all its
    existing bytes, in order (Q07). The assembled result then passes the same
    check before any write. For example, with no root file, a declared
    archive `docs/CHANGELOG.v1.0.0-v1.2.0.md` for `1.0.0` to `1.2.0` that
    holds only `1.0.0`, and an eligible annotated `v1.1.0` tag with no
    section, the first render inserts the `1.1.0` section into that archive
    above `1.0.0`, keeps every existing byte of the archive, and creates the
    root file.
  - pro: every placed byte exists, and no destination is reserved for a
    missing section.
  - pro: mismatches surface instead of moving silently, and a first render is
    never asked for sections that cannot exist yet.
  - con: a project with an old untagged section must decide what to do with
    it first.
- Option B: stable tags define the releases; a missing section is an error,
  and an extra section is ignored and stays where it is.
  - pro: Git is the single source of truth.
  - con: an ignored extra section can end up out of order or outside its
    range.
- Option C: the union of both: every tag and every section needs a
  destination, with no mismatch check.
  - pro: simplest rule.
  - con: a tag without a section and a section without a tag both pass
    silently.

#### Recommended option for Q05 (with arguments for this choice)

Option A: the archive rules move text, so the text is what must be counted;
the tags confirm it. The single exception covers the curated author who
writes notes before the release and the release transaction itself, the two
normal cases of a section ahead of its tag. Counting only the eligible
releases HEAD reaches uses item 2's decision, the same one that sets the range
baselines, and running the check on the assembled result lets a first render
create what it must.

#### Answer to Q05: option A (with reason why it must be accepted as the answer)

Option A: it gives one clear meaning to "existing release" for every archive
rule, reports the mismatches that would otherwise move or vanish silently, and
does not block the normal flow of preparing a release.

User decision: confirmed — option A: the sections in the files are placed and
checked against the eligible stable releases HEAD reaches. With an existing
root file, a release with no section, a section with no tag, or a section
whose version only an unvalidated or unreachable tag names stops the run
before any write, except the section of the version being prepared or
released. A first render (root file missing) checks nothing beforehand,
creates the missing sections in their destinations, inserting into an
existing archive while keeping all its bytes, and checks the assembled result
before any write. If Q07 is answered with option D, this example follows it.

Decided by the user on 2026-11-24, during the question explanation after
review round 3, choosing the recommended option.

### Q06: Hand edits inside the generated snapshot section

Question description: the authority rule protects released sections. The
snapshot section, `## [vX.Y.Z-SNAPSHOT unreleased] <title>`, is rebuilt on every
run from the commits since the last stable release and the `version.txt`
notes; dev_workflow rewrites it every time too. An author who edits a commit
line or adds a paragraph inside that section, instead of in `version.txt`,
loses the edit at the next `uc`, `uvf`, or `/prepare-release` Step 10 or 11.
The requirement does not say whether that loss is the expected behavior.

#### BBQ for Q06

A whiteboard menu is wiped and rewritten from the kitchen's order list every
morning. A note a waiter scribbles on the board is gone the next morning; a
note written in the order list stays. In this picture: the whiteboard is the
snapshot section, the morning rewrite is each `changelog` run, the order list
is the commits plus `version.txt`, and the waiter's note is a hand edit.

#### Options for Q06

- Option A: the snapshot section is engine-owned: each run rebuilds it from
  the commits and the `version.txt` notes, and hand edits there are replaced.
  Notes belong in `version.txt`, and the documentation says so. At release,
  the section becomes released and authoritative. If Q02 A is chosen, the
  same applies to the untagged stable form, `## [vX.Y.Z unreleased] <title>`.
  - pro: matches dev_workflow and keeps runs identical on unchanged inputs.
  - pro: one place for notes, `version.txt`, which item 2 already preserves.
  - con: an edit made in the wrong place is lost without warning.
- Option B: refuse to rebuild when the existing snapshot section differs from
  what the engine last wrote, naming the differing lines.
  - pro: no silent loss.
  - con: needs a record of the last render, and blocks every run after a
    harmless edit.
- Option C: keep the lines the engine does not recognize and merge them into
  the rebuilt section.
  - pro: edits survive.
  - con: guessing where a line belongs after new commits arrive makes the
    output depend on history rather than on the inputs.

#### Recommended option for Q06 (with arguments for this choice)

Option A: the snapshot section is a view of the commits and `version.txt`,
which is what makes repeated runs identical. `version.txt` already holds the
release notes and survives every version transition, so authors have a safe
place for prose.

#### Answer to Q06: option A (with reason why it must be accepted as the answer)

Option A: it keeps the generated section reproducible from its inputs and
matches what authors already experience with dev_workflow; the documentation
points them to `version.txt` for anything they want to keep.

User decision: confirmed — option A: the unreleased section, in both heading
forms of Q02, is engine-owned and rebuilt on each run from the commits and the
`version.txt` notes; hand edits there are replaced. The documentation points
authors to `version.txt` for notes and to `.changelog-fixes.toml` rules for
lasting wording corrections. At release the section becomes authoritative.

Decided by the user on 2026-11-24, during the question explanation after
review round 3, choosing the recommended option as presented with the
fix-rule pointer.

### Q07: Rendering a generated changelog when `CHANGELOG.md` does not exist

Question description: dev_workflow renders the whole history when no
`CHANGELOG.md` exists (line 18). Each release heading then comes from the
git-cliff template, `## [{{ version }}] - {{ timestamp }} - {{ message }}`,
with the annotated tag message as title, and line 46 strips the date, which
is consistent with llm-shared's two oldest headings having none. The
requirement keeps the dates of existing releases and never dates them with
today's date, but does not say whether a first render of the whole history
is in scope, nor which date and title a historical heading gets. A lightweight
tag has no message, and an annotated tag carries both a tagger date and the
date of its commit, each with the time-zone offset where it was recorded.
Item 2 counts a lightweight stable tag as an eligible historical release. The
requirement also does not say what happens to an archive that already exists
when the root file is missing, in particular one that lacks a section of its
range (Q05's example: an archive for `1.0.0` to `1.2.0` holding only `1.0.0`
while `v1.1.0` is an eligible release), nor when Q05's check for missing
sections runs.
All of llm-shared's thirteen release tags are annotated.

#### BBQ for Q07

Starting an album for twenty years of prints, each page needs a caption and
a date. The back of a print may show the day it was developed, the day it was
taken, or nothing. In this picture: the album is a first `CHANGELOG.md`, each
page is a historical release section, the caption is the title from the
annotated tag message, the two possible dates are the tagger date and the
commit date, and a print with nothing on the back is a lightweight tag.

#### Options for Q07

- Option A: supported for eligible annotated releases. A first render, run
  whenever the root file is missing, creates a section for each release of
  this history that no file holds yet, placed by the archive policy: in the
  root, in a new archive file, or in an existing archive, where the section is
  inserted in newest-first order and the file keeps all its existing bytes, in
  order. With no file at all, that is the whole history. In Q05's example, the
  missing `1.1.0` section goes into the existing `1.0.0` to `1.2.0` archive,
  above `1.0.0`. Each created historical heading uses the dated form, with the
  calendar date of its annotated tag's tagger date, taken in the offset
  recorded in the tag rather than the machine's time zone, and the first line
  of the tag message as title. An eligible release whose tag is lightweight
  stops the run, naming it. Q05's check runs on the assembled result, before
  any write.
  - pro: a new consumer gets a complete, uniform changelog in one run, with
    the same date its tag annotation shows, as new releases do.
  - pro: the same frozen history gives the same headings on every machine.
  - con: a lightweight release tag needs an author fix before the first
    render.
- Option B: supported, legacy style: historical headings take no date (the
  date-less form of Q04), with the tag message as title when there is one,
  and no title otherwise.
  - pro: never stops; matches the legacy output.
  - con: produces date-less headings, a second released form kept forever.
- Option C: out of scope: a missing `CHANGELOG.md` in generated mode is an
  error, and setup (item 6) creates the first file.
  - pro: smallest scope for this item.
  - con: moves history rendering to setup, which owns proposing archives,
    not rendering.
- Option D: as A, but an existing archive that lacks a section of its range
  stops the first render before any write, naming the archive and the
  missing release (in Q05's example, the archive and `1.1.0`); only new files
  are created.
  - pro: a first render never modifies a file that already exists.
  - con: the author must write that section by hand, or remove the archive,
    although the engine could render it from the tag.

#### Recommended option for Q07 (with arguments for this choice)

Option A: new releases already use one captured date in both the heading and
the tag annotation, so the tagger date gives historical headings the same
meaning, and reading it in the tag's own offset makes the output independent
of the machine. A stop on a lightweight tag is rare, names the tag, and avoids
inventing a title or a date. Inserting a missing section into an existing
archive, while keeping all its existing bytes, completes the history in one
run, and checking the assembled result protects what already exists without
asking for sections before they can exist. Option D is the stricter
alternative if the human prefers that a first render never touch an existing
file.

#### Answer to Q07: option A (with reason why it must be accepted as the answer)

Option A: it keeps one released heading form for everything the engine
writes, takes every value from the release's own tag, and never guesses a
missing one.

User decision: confirmed — option A: a first render, run whenever the root
file is missing, creates a section for each eligible annotated release no file
holds yet, inserting into an existing archive in newest-first order while the
archive keeps all its existing bytes; each created heading uses the dated
form with the calendar date of the tagger date in the tag's recorded offset
and the first line of the tag message as title; an eligible release whose tag
is lightweight stops the run, naming it; Q05's check runs on the assembled
result before any write. Q05's example stays as written.

Decided by the user on 2026-11-24, during the question explanation after
review round 3, choosing the recommended option.

### Q08: Curated validation outside a release, before the author writes the section

Question description: in curated mode the engine checks that a section for the
exact release exists. During development `version.txt` holds
`0.0.25-SNAPSHOT`, and a workspace-halo author usually writes `## 0.0.25`
close to the release. `uc` and `uvf` validate curated content at any time, and
release `pre` (item 5) calls the same validation, even when the release
started from a snapshot anchor that it turns into the stable version. The
requirement does not say whether a missing target section during a snapshot
fails `uc`, or only fails the release, nor what happens outside a release when
`version.txt` holds an untagged stable `0.0.25`, or a version a stable tag
already reserves. Such a tag may be an eligible release of this history,
whose section Q05 requires, or only reserve the number, as an unvalidated
engine release or a tag on another branch does (Q02).

#### BBQ for Q08

A wedding planner checks the list of speeches. A week before, a missing
best-man speech is a reminder; on the day, it stops the ceremony from
starting. In this picture: the list of speeches is the curated
`CHANGELOG.md`, the best-man speech is the `## 0.0.25` section, the week
before is a `uc` run during the snapshot, and the day itself is the release
`pre` check.

#### Options for Q08

- Option A: outside a release, run every other check first: headings,
  ranges, links, duplicates and Q05's historical check, under which a release
  of this history with no section fails even in an ordinary refresh (for
  example, an eligible `v1.2.3` tag on HEAD with no `## 1.2.3` section). Then
  classify the `version.txt` version in Q02's order:
  - an eligible release of this history needs its section like any other
    release, and a notice points to `uver` when commits follow its tag;
  - a version reserved only by an unvalidated engine release or by a tag HEAD
    does not reach fails, naming the tag and its state, since this history
    cannot release it;
  - a version no stable tag reserves is the forthcoming target, whatever its
    form (snapshot or untagged stable). Its missing section is a notice that
    never changes the exit status, which is 0 when every other check passed.

  Release validation requires the release version's section before any write,
  even when the release started from a snapshot anchor.
  - pro: `uc` stays useful during development, and a release still cannot
    ship without notes.
  - pro: a missing historical section or a version taken elsewhere is never
    reduced to a notice.
  - con: the same missing section gives two outcomes, depending on whether a
    release is running.
- Option B: a missing target section always fails, snapshot or release.
  - pro: one rule.
  - con: `uc` fails on every run until the author writes the notes, so
    authors stop running it.
- Option C: outside a release, skip the target check entirely; only the
  release checks it.
  - pro: quiet development runs.
  - con: no early reminder at all.

#### Recommended option for Q08 (with arguments for this choice)

Option A: the release gate is where the section is mandatory; before that, a
notice is the useful signal. Every other curated check still fails outside a
release, so a broken heading or link is caught early. Tying the notice to a
forthcoming version, in Q02's order, gives one answer for snapshot and
untagged stable anchors alike, while a historical release keeps Q05's
requirement.

#### Answer to Q08: option A (with reason why it must be accepted as the answer)

Option A: it matches how a curated author works, writing the notes last,
while keeping the release blocked until the exact section exists.

User decision: confirmed — option A: outside a release, curated validation
runs every other check first (headings, ranges, links, duplicates and Q05's
historical check), then classifies the `version.txt` version in Q02's order:
an eligible release of this history needs its section, with a notice pointing
to `uver` when commits follow its tag; a version reserved only by an
unvalidated engine release or by a tag HEAD does not reach fails, naming the
tag and its state; a version no stable tag reserves is the forthcoming
target, whose missing section is a notice that leaves the exit status at 0
when every other check passed. Release validation requires the release
version's section before any write, even when the release started from a
snapshot anchor. Qualification: the notions of section, release notes and
notice are detailed in the topic draft and in this requirement ("Changelog
sections, release notes and notices"), and the explanations and the review
of Q09 to Q20 apply them.

Decided by the user on 2026-11-25, during the question explanation after
review round 3, choosing the recommended option with that qualification.

### Q09: Curated heading forms that count as the section of a release

Question description: the requirement accepts `## X.Y.Z` "and the documented
`vX.Y.Z` and bracketed heading forms", never a substring match, but does not
list those forms, say what may follow the version on the heading line (a
date, a title), or say which heading level counts. workspace-halo writes
`## 0.0.24`; the generated form is `## [vX.Y.Z] - YYYY-MM-DD - <title>`.
Without a closed list, `## Version 0.0.25`, `### 0.0.25` or
`## [0.0.25] (2026-11-01)` could each be read either way.

#### BBQ for Q09

A doorman checks names against a guest list. He must know whether "Dr. Smith",
"Smith, J." and "SMITH" all count as "Smith", and that "Smithson" does not. In
this picture: the doorman is the curated validation, the name on the list is
the release version, the spellings are heading forms, and "Smithson" is a
substring match, such as `## 0.0.25` taken for the release `0.0.2`.

#### Options for Q09

- Option A: a closed list of level-two headings: `## X.Y.Z`, `## vX.Y.Z`,
  `## [X.Y.Z]` and `## [vX.Y.Z]`. The heading holds a complete version token,
  in brackets closed right after it when a bracket opens, then the end of the
  line or whitespace before optional free text, such as a date or a title.
  A heading that looks versioned but fits no form is reported. Neither a
  malformed bracket, such as `## [0.0.25 notes`, nor a `## 0.0.25` line
  inside a fenced code block can satisfy the release check.
  - pro: covers workspace-halo and the generated forms, and is predictable.
  - con: an author using another style must change it once.
- Option B: only `## X.Y.Z`, workspace-halo's form, and the generated dated
  form.
  - pro: smallest list.
  - con: refuses common styles such as `## v0.0.25`, which the requirement
    already calls documented.
- Option C: any heading, at any level, whose first version-looking token
  equals the release.
  - pro: accepts every style.
  - con: a sub-heading or `## Version 0.0.25 preview` can satisfy the check by
    accident.

#### Recommended option for Q09 (with arguments for this choice)

Option A: it names exactly what "documented" means, keeps free text after the
version for dates and titles, and the boundary rule rules out substring
matches. Reporting near misses tells the author why a section was not found.

#### Answer to Q09: option A (with reason why it must be accepted as the answer)

Option A: curated authors get a short, explicit list that includes their
current style, and the release check can never be satisfied by a heading
meant for another version.

User decision: confirmed — option A: a closed list of level-two headings,
`## X.Y.Z`, `## vX.Y.Z`, `## [X.Y.Z]` and `## [vX.Y.Z]`, each holding a
complete version token, in brackets closed right after it when a bracket
opens, then the end of the line or whitespace before optional free text, such
as a date or a title. A heading that looks versioned but fits no form is
reported as a failure, like every other curated heading check (Q08). Neither a
malformed bracket nor a `## 0.0.25` line inside a fenced code block can
satisfy the release check. The level-two section definition in "Changelog
sections, release notes and notices" stays as written.

Decided by the user on 2026-11-25, during the question explanation after
review round 3, choosing the recommended option. With this answer, the user
also directed that this effort define no `uv` alias, only `uver`; the
umbrella's alias row now says so.

### Q10: The recent lower bound when archives exist

Question description: `.release.ini` declares `recent-from` and archive ranges;
the requirement forbids inferring or silently choosing boundaries and rejects
an uncovered existing release. It does not say whether `recent-from` is
required once an archive is declared, what it means when omitted, or how it
must relate to the archives' `to` bounds.

#### BBQ for Q10

A closet has a "current season" rail and labeled storage boxes. Without a
sign on the rail saying from which season clothes hang there, someone must
guess where last year's coat goes. In this picture: the rail is the root
`CHANGELOG.md`, the sign is `recent-from`, the boxes are the archive files with
their `from` and `to`, and last year's coat is a release between the newest
archive and the root.

#### Options for Q10

- Option A: `recent-from` is required as soon as one archive range is declared,
  and must be higher than every archive `to`; without archives it is optional
  and the root holds every release. The space between the newest archive and
  `recent-from` follows the gap rule: accepted while it holds no release.
  - pro: no boundary is inferred, as the requirement asks.
  - pro: the gap rule keeps working unchanged, since confirmed answer Q2 A
    places every new release on `main` above the existing ones.
  - con: one more line to write when adding the first archive.
- Option B: when omitted, the root holds every release newer than the highest
  archive `to`.
  - pro: one less setting, with a well-defined rule.
  - con: the root's range then follows from the archives, a policy the author
    never declared, while the requirement forbids inferring boundaries.
- Option C: optional with archives too: the root holds every release that no
  archive covers, whatever its version.
  - pro: simplest.
  - con: a forgotten old release stays in the root, outside the policy, with
    no error.

#### Recommended option for Q10 (with arguments for this choice)

Option A: it applies the "no inferred boundary" rule to the root's own bound,
and reuses the gap rule already settled by Q2 A, so no new concept is needed.

#### Answer to Q10: option A (with reason why it must be accepted as the answer)

Option A: every release has a destination declared by the author, and a
missing or inconsistent bound is reported before any write instead of being
guessed.

User decision: confirmed — option A: `recent-from` is required as soon as one
archive range is declared, and must be higher than every archive `to`; without
archives it is optional and the root holds every release. The space between
the newest archive and `recent-from` follows the gap rule: accepted while it
holds no release. Every violation stops the run before any write, as a
failure, not a notice.

Decided by the user on 2026-11-25, during the question explanation after
review round 3, choosing the recommended option.

### Q11: Confirmation before a repartition is written

Question description: after an author changes archive bounds, "the next
`changelog` run previews the affected files and repartitions complete
sections". Every command that can prompt also has a non-interactive form that
fails instead of asking. The requirement does not say whether the preview
waits for a confirmation before the files are written, nor what the
non-interactive form does when a repartition is pending, for example during
`/prepare-release` Step 10.

#### BBQ for Q11

A mover shows the plan: "these twelve boxes go to the attic". He either waits
for a nod, or starts carrying while still talking. In this picture: the mover
is the `changelog` run, the plan is the preview of affected files, the boxes
are sections moving between the root and archives, and the nod is the
confirmation, or an explicit acceptance option in the non-interactive form.

#### Options for Q11

- Option A: an interactive run shows the preview and asks before writing; the
  non-interactive form fails with the preview unless an explicit acceptance
  option is passed. The preview names every affected file (the root and each
  archive written, created or deleted) and the sections moving between them.
  A run with no pending repartition asks nothing.
  - pro: a bounds change never moves files unseen, and `/prepare-release` can
    show the preview in its own menu.
  - con: one more prompt after each bounds change.
- Option B: the preview is printed and the files are written in the same run;
  Git's diff is the review.
  - pro: no prompt.
  - con: a typo in a bound moves many sections in an automated run before
    anyone reads the preview.
- Option C: ordinary runs never repartition; a separate explicit command moves
  the sections.
  - pro: ordinary renders stay small.
  - con: between the bounds change and that command, the files disagree with
    the config, and every run must report it.

#### Recommended option for Q11 (with arguments for this choice)

Option A: a repartition can touch every archive at once, so it deserves the
same confirm-or-fail pattern the requirement already sets for prompting
commands; ordinary renders stay prompt-free.

#### Answer to Q11: option A (with reason why it must be accepted as the answer)

Option A: it reuses the requirement's non-interactive rule, lets
`/prepare-release` present the preview in its own menu, and never moves
sections on a mistyped bound without someone seeing it.

User decision: confirmed — option A: an interactive run shows the preview and
asks before writing; the non-interactive form fails with the preview unless
an explicit acceptance option is passed. The preview names every affected
file (the root and each archive written, created or deleted) and the sections
moving between them. A run with no pending repartition asks nothing. A "no"
at the interactive prompt writes nothing and is a failure, since the files
still disagree with `.release.ini`; the next run asks again.

Decided by the user on 2026-11-25, during the question explanation after
review round 3, choosing the recommended option, with the reading of a
declined prompt shown in the choice.

### Q12: Which archive files a repartition may delete

Question description: a repartition may remove "any obsolete engine-owned
archive ... after its sections and links are moved", and must "never remove
unrelated files". Once an author edits `.release.ini`, the old range is no
longer declared, so the config alone cannot tell which file the engine owned.
The requirement does not say how a file qualifies as engine-owned. A matching
name, Git tracking and a clean working tree prove that a deletion could be
undone, not that the engine ever managed the file: an unrelated, tracked,
clean file named like an archive and holding no release section would even
pass an "every section moved" test, since it has none to move.

#### BBQ for Q12

After reorganizing the garage, the old labeled boxes are empty and can go. But
a box with the same label style might belong to a neighbor who stores things
there. In this picture: the old boxes are archive files whose range is no
longer declared, the label style is the `docs/CHANGELOG.vA.B.C-vD.E.F.md`
name, the neighbor's box is a file the author keeps for another reason, and
"empty" means every section was moved, as the completeness check proves.

#### Options for Q12

- Option A: delete an archive file that is no longer declared only with
  positive evidence that the engine managed it under an earlier config (how
  that evidence is kept is design work), and only when every section it held
  now appears, byte for byte, exactly once in a declared destination. Without
  that evidence, leave the file in place and report it, whatever its name,
  tracking state or content. A managed archive with local changes stops the
  run before any write, naming the file, so the author commits or discards the
  changes first. For example:
  - success: the bounds `[changelog-archive:0.1.0-0.9.9]` with
    `recent-from = 0.10.0` become `[changelog-archive:0.1.0-0.13.9]` with
    `recent-from = 0.14.0`. The sections of `docs/CHANGELOG.v0.1.0-v0.9.9.md`
    and the root's `0.10.0` to `0.13.0` sections move to the new
    `docs/CHANGELOG.v0.1.0-v0.13.9.md`. The old file, managed under the
    earlier config and emptied by that verified move, is deleted, and the
    exposed write and delete set lists it;
  - unrelated file: a tracked, clean `docs/CHANGELOG.v0.2.0-v0.3.0.md` that
    the author wrote for another purpose and never declared holds no release
    section. With no evidence of management, it stays and is reported;
  - last range removed: the author deletes the only `[changelog-archive:...]`
    section. Every release returns to the root, the managed archive is deleted
    once its sections are verified there, and the root's link to it goes;
  - local edits: the managed `docs/CHANGELOG.v0.1.0-v0.9.9.md` has an
    uncommitted change when its range is removed. The run stops before any
    write, naming it.
  - pro: only a file the engine provably managed can be deleted, and never
    with a lost section or a lost local edit.
  - con: an archive left from before the engine, or managed without that
    evidence, must be removed by hand.
- Option B: never delete: report obsolete archives and let the author remove
  them.
  - pro: no deletion risk at all.
  - con: a left-over archive duplicates every moved section, which the
    completeness and one-destination rules then flag on every run.
- Option C: delete every undeclared file that matches the archive name
  pattern after the move.
  - pro: simplest.
  - con: can delete a file with local edits, or one the author added on
    purpose.
- Option D (round 1 proposal, kept for reference): delete a file when its name
  matches `docs/CHANGELOG.vA.B.C-vD.E.F.md`, its range is no longer declared,
  Git tracks it with no local change, and every one of its sections now lives
  in a declared destination.
  - pro: needs no evidence beyond the disk and Git, and every deletion can be
    undone with Git.
  - con: proves recoverability, not ownership: the unrelated file of option
    A's example passes every condition, the last one with no section to move.

#### Recommended option for Q12 (with arguments for this choice)

Option A: positive evidence of earlier management is what separates an
engine-owned archive from a file that only looks like one, and the
byte-for-byte check proves nothing is lost. Anything ambiguous stays in place
and is reported, so "never remove unrelated files" holds even for a clean,
tracked file with the right name. (Round 1 of the independent review replaced
the earlier recommendation, now option D.)

#### Answer to Q12: option A (with reason why it must be accepted as the answer)

Option A: it keeps the requirement's promise to remove obsolete archives,
deletes only what the engine provably managed and fully moved, never touches a
locally edited archive, and leaves the evidence mechanism to the design.

User decision: confirmed — option A: delete an archive file that is no longer
declared only with positive evidence that the engine managed it under an
earlier config (how that evidence is kept is design work), and only when every
section it held now appears, byte for byte, exactly once in a declared
destination. Without that evidence, leave the file in place and report it: a
notice when it holds no released section, a failure when its sections also
exist in a declared destination. A managed archive with local changes stops
the run before any write, naming the file. Qualification: "archive" is defined
in the umbrella draft, the topic draft and this requirement (a file
`docs/CHANGELOG.vA.B.C-vD.E.F.md` holding the released sections of one older
range, declared by one `[changelog-archive:...]` configuration section), and
the explanations and the review of Q13 to Q20 apply it.

Decided by the user on 2026-11-25, during the question explanation after
review round 3, choosing the recommended option with that qualification and
the notice or failure reading shown in the choice.

### Q13: What an archive file holds besides its sections, and how the files link

Question description: generated mode adds relative links from the root to each
archive and back, and curated mode validates the links the author maintains.
The requirement does not say what precedes the sections in an archive (the
project header from `changelog-header.md`, a title naming the range, or
nothing), where the links sit, what the curated check accepts as a valid
link, or whether a declared range holding no release needs a file and links.

#### BBQ for Q13

A multi-volume encyclopedia: each volume needs a spine title such as "A to F",
and the first volume lists the others; a card slipped anywhere inside a
volume does not help a reader find the next one. In this picture: the volumes
are the archive files, the spine title is the archive's first line naming
its range, the list in the first volume is the root's links to the archives,
and a card slipped anywhere is a link at an arbitrary place in a curated
file.

#### Options for Q13

- Option A: generated mode writes an engine-owned link block in the root,
  right after the header, with one relative link per archive, newest range
  first. Each archive starts with a one-line title naming its range and a
  relative link back to the root, without the project header. Curated mode
  requires one relative link to each declared archive somewhere in the root,
  and one link back to the root somewhere in each archive, without imposing a
  position. A declared range that holds no existing release needs no archive
  file and no link: generated mode creates neither and reports a notice, and
  curated validation requires neither, checking the links of such a file only
  if the author keeps one.
  - pro: predictable generated output, and curated authors keep their
    layout.
  - con: generated and curated files place their links differently.
- Option B: archives repeat the project header from `changelog-header.md`,
  then the link back; curated mode requires the same block as generated mode.
  - pro: each archive reads like a full changelog, with one rule for both
    modes.
  - con: the header text may not fit an archive, and curated authors lose
    control of their layout.
- Option C: links only in the root; archives hold only their sections.
  - pro: the least content to own.
  - con: a reader who lands on an archive has no way back, which the
    requirement asks for.

#### Recommended option for Q13 (with arguments for this choice)

Option A: the generated files get a fixed, testable shape, and curated mode
checks only what the requirement asks, that the links exist, which respects
"files and links remain author-maintained".

#### Answer to Q13: option A (with reason why it must be accepted as the answer)

Option A: every archive says which releases it holds and how to get back,
the generated layout can be compared byte for byte, and curated authors keep
their own arrangement.

User decision: confirmed — option A: generated mode writes an engine-owned
link block in the root, right after the header, with one relative link per
archive, newest range first; each archive starts with a one-line title naming
its range and a relative link back to the root, without the project header.
Curated mode requires one relative link to each declared archive somewhere in
the root, and one link back to the root somewhere in each archive, without
imposing a position. A declared range that holds no existing release needs no
archive file and no link: generated mode creates neither and reports a notice
(exit 0), and curated validation requires neither, checking the links of such
a file only if the author keeps one.

Decided by the user on 2026-11-26, during the question explanation after
review round 3, choosing the recommended option.

### Q14: Whether the automatic `fixes init` creates a starter file in every generated project

Question description: `uc`, `uvf` and `/prepare-release` Steps 10 and 11 run
`fixes init` automatically; `init` converts an existing `.changelog.fixes`,
and otherwise creates `.changelog-fixes.toml` from a commented starter
template. Taken together, the first `uc` in a project that never had fix
rules adds a new file to its working tree and to the next prepare commit.
Umbrella decision 2 and the umbrella's overview speak only of converting an
existing `.changelog.fixes` automatically, but the umbrella's item 4 details,
carried into this requirement, also state that `init` creates the starter
when no legacy file exists and that `uc`, `uvf` and Steps 10 and 11 run
`init` automatically. Creating the starter automatically is therefore the
inherited behavior; skipping it would narrow it. Curated mode never runs the
automatic `init`, since it applies no fix rule.

#### BBQ for Q14

A hotel leaves a welcome basket in the rooms whose guests ordered one; leaving
an empty basket in every room makes every guest deal with it. In this
picture: the basket is `.changelog-fixes.toml`, guests who ordered one are
projects with a legacy `.changelog.fixes` to convert, the empty basket is the
commented starter file, and the rooms are generated and curated projects.

#### Options for Q14

- Option A: the automatic `init` only converts an existing `.changelog.fixes`;
  with none, it creates nothing and only the built-in cleanups run.
  `fixes <root> init` typed by hand still creates the starter. Curated mode
  never runs the automatic `init`.
  - pro: no new file appears in projects that need no rules.
  - con: changes inherited behavior, the umbrella's item 4 details, and needs
    the human's explicit choice.
  - con: an author must know about `fixes init` to start writing rules.
- Option B: as written: in generated mode the automatic `init` creates the
  starter when no file exists; curated mode never runs it.
  - pro: matches the umbrella's item 4 details, and the rules file is visible
    in every generated project.
  - con: every generated project gets a commented file it may never use, in a
    prepare commit.
- Option C: as B, in both modes.
  - pro: one behavior everywhere.
  - con: adds a rules file to curated projects, which never apply rules, and
    contradicts curated mode's freedom from fix rules.

#### Recommended option for Q14 (with arguments for this choice)

Option B: it is the behavior the umbrella states for item 4, and decision 2,
which summarizes the conversion, does not replace those details. Curated
projects stay untouched in both viable options. Option A is a reasonable
narrowing if the human prefers no starter file in projects without rules.
(Round 1 of the independent review moved this recommendation from A to B.)

#### Answer to Q14: option B (with reason why it must be accepted as the answer)

Option B: it keeps the inherited behavior, gives every generated project a
visible place to write rules, and leaves curated projects without a rules
file.

User decision: confirmed — option B: as written, in generated mode the
automatic `init` run by `uc`, `uvf` and `/prepare-release` Steps 10 and 11
converts an existing `.changelog.fixes`, or creates the commented starter
`.changelog-fixes.toml` when no rules file exists; curated mode never runs the
automatic `init`.

Decided by the user on 2026-11-26, during the question explanation after
review round 3, choosing the recommended option.

### Q15: Converting the legacy `regex => replacement` form, which never worked as written

Question description: the requirement has `fixes convert` and the `brel`
transition reader accept legacy `=>` lines. In `update-changelog.sh` (lines
173 to 197), such a line becomes `push @patterns, qr/"<regex>"/;` and
`push @replacements, "<replacement>";`: the pattern gains literal double
quotes, and `s///gee` evaluates the replacement text as Perl code under
`use strict`. A probe of that Perl code on 2026-11-24, with a one-word typo fix
written in this form, showed: the unquoted word was left alone, the same word
between double quotes matched, and it was replaced by nothing, quotes
included; Perl printed `Use of uninitialized value` and exited 0. That result
holds for the probed replacement only: since Perl evaluates the replacement
text as code, another replacement can give another result. No known file uses
this form: the three existing files use `push` pairs.

#### BBQ for Q15

An old recipe card says "add salt", but because of a printing error every
cook actually read it as "remove anything in quotation marks". Copying the
card to a new kitchen, one can copy what it says, copy the printing error, or
ask the cook to rewrite the card. In this picture: the card is a legacy `=>`
line, what it says is "replace the regex with the replacement", the printing
error is the added quotes plus the evaluation of the replacement as code
(which deleted the match in the probe), and the new kitchen is
`.changelog-fixes.toml`.

#### Options for Q15

- Option A: convert each `=>` line to what it says, within the subset of Q16:
  the pattern without the added quotes, and the replacement as literal text
  with its group references kept. The conversion report lists every converted
  `=>` line as a behavior change, and the `brel` transition reader, which
  reads these lines the same way, reports each one too whenever it uses it.
  A line outside the subset stops both, naming it.
  - pro: keeps the umbrella's support for legacy arrows, and gives each rule
    the effect its author wrote.
  - con: a project that relied on the broken effect, knowingly or not, sees
    different output, listed in the report.
- Option B: refuse `=>` lines: conversion and the transition reader stop,
  naming each line, and the author writes the rule in TOML.
  - pro: no silent change of meaning, and nothing known uses the form.
  - con: narrows the umbrella acceptance criterion, which lists legacy
    arrows.
- Option C: reproduce the legacy effect: match only the quoted text and
  evaluate the replacement as Perl code, as `s///gee` does.
  - pro: closest to the legacy output.
  - con: needs a Perl evaluator, which this item removes, and carries a defect
    into the new declarative file; no fixed replacement can stand for it,
    since the probe observed deletion for one replacement only.

#### Recommended option for Q15 (with arguments for this choice)

Option A: the legacy effect is a defect nobody would write on purpose, and the
report makes every changed meaning visible. It keeps the umbrella's promise to
convert legacy arrows without carrying the defect forward.

#### Answer to Q15: option A (with reason why it must be accepted as the answer)

Option A: the converted rule does what its line says, the change is reported
line by line, and the transition reader stays consistent with the converted
file.

User decision: confirmed — option A: convert each `=>` line to what it says,
within the subset of Q16: the pattern without the added quotes, and the
replacement as literal text with its group references kept. The conversion
report lists every converted `=>` line as a behavior change, and the `brel`
transition reader, which reads these lines the same way, reports each one too
whenever it uses it: both reports are notices (exit 0). A line outside the
subset stops both, naming it, as a failure.

Decided by the user on 2026-11-26, during the question explanation after
review round 3, choosing the recommended option, with the notice and failure
reading shown in the choice.

### Q16: Perl patterns and replacements that `fixes convert` accepts

Question description: a legacy `push` pair is Perl code. `qr/.../` may carry
flags (`i`, `m`, `s`, `x`) or other delimiters, and because `s///gee`
evaluates the replacement twice, `'"..."'` can hold any Perl expression,
including case modifiers (`\u$1`, `\L...\E`), other variables or function
calls. The known files use only plain `qr/.../` patterns with lookbehinds,
`\S`, `[\r\n]`, `\s*?` and non-capturing groups, and replacements made of
literal text, `$1`, `\1` and `\n`. The requirement says any other Perl
statement stops the conversion, but not which forms inside a `push` pair are
supported. Python's `re` also reads a few constructs differently from Perl:
`\Z`, for example, matches before a final newline in Perl and only at the very
end in Python, and `\v` means any vertical space in Perl but only a vertical
tab in Python. The template reads the changelog as bytes, with no encoding
layer, so for Perl `\w`, `\d`, `\s` and `\b` only see ASCII characters, while
Python's `re` on text also matches non-ASCII letters, digits and spaces, such
as a non-breaking space. A pattern that compiles in Python therefore does not
prove that it matches what the Perl rule matched. A replacement can also
refer to a group the pattern does not define; Perl only warns about it when a
match occurs.

#### BBQ for Q16

A translator converting old letters agrees to handle ordinary sentences and to
refuse idioms whose meaning would change in translation, rather than guess. In
this picture: the letters are `push` pairs, ordinary sentences are the subset
the known files use, idioms are Perl-only constructs such as `\u` or code in a
replacement, and guessing is converting a rule whose Python meaning differs.

#### Options for Q16

- Option A: a closed subset, defined by what it accepts rather than by what
  Python compiles: `qr/.../` with optional `i`, `m`, `s` and `x` flags,
  carried as inline flags; a replacement that is one double-quoted Perl string
  made of literal text, `$N`, `${N}` or `\N` group references, and the escapes
  `\n`, `\t`, `\\`, `\"`, `\$` and `\@`. The converted rule must match what
  the Perl rule matched on the same bytes, non-ASCII text included. Any other
  form, and any construct Python reads differently, stops the conversion,
  naming the line and the construct. Replacement escapes and group references
  are checked against the pattern when the rule is read, even if it would
  match nothing. Conversion and the `brel` transition reader accept the same
  subset and report the same unsupported construct before any write. For
  example:
  - accepted: llm-shared's
    ``push @patterns, qr/(?<!`)draft\.vX\.Y\.Z\.<slug>\.md/;`` with
    ``push @replacements, '"`draft.vX.Y.Z.<slug>.md`"';``, a pattern with the
    `i` flag, and a replacement such as `'"$1\n"'`;
  - refused, naming the construct: another delimiter such as `qr{...}`, the
    pattern escapes `\Z` and `\v`, a replacement with `\u$1` or `\L$1\E`, a
    variable other than a group reference, a function call, and `$3` when the
    pattern defines two groups.
  - pro: covers every known rule, and never produces a rule that behaves
    differently.
  - con: a project with an unusual rule must rewrite it by hand.
- Option B: as A, plus translating case modifiers and other common Perl
  features into equivalent Python behavior.
  - pro: converts more rules automatically.
  - con: the TOML format would need more than one pattern and one replacement
    per rule, or hidden semantics.
- Option C: only what the known files use: no flags, no `${N}`, and no escape
  other than `\n`.
  - pro: smallest surface.
  - con: refuses harmless forms, such as `qr/.../i`, that a project may have.

#### Recommended option for Q16 (with arguments for this choice)

Option A: it accepts every known rule plus the harmless variants a project is
likely to hold, and refuses, with a precise message, anything whose meaning
could shift, which is the "stop rather than guess" rule the requirement
already sets. Defining the subset by accepted constructs and examples, rather
than by what compiles, is what makes the conversion exact, and checking
replacements when a rule is read catches a broken rule before it ever
matches.

#### Answer to Q16: option A (with reason why it must be accepted as the answer)

Option A: the conversion stays exact for everything it accepts, keeps the
declarative file at one pattern and one replacement per rule, and tells the
author precisely which line needs a hand rewrite.

User decision: confirmed — option A: a closed subset, defined by what it
accepts rather than by what Python compiles: `qr/.../` with optional `i`, `m`,
`s` and `x` flags, carried as inline flags; a replacement that is one
double-quoted Perl string made of literal text, `$N`, `${N}` or `\N` group
references, and the escapes `\n`, `\t`, `\\`, `\"`, `\$` and `\@`. The
converted rule must match what the Perl rule matched on the same bytes,
non-ASCII text included. Any other form, and any construct Python reads
differently, stops the conversion as a failure, naming the line and the
construct. Replacement escapes and group references are checked against the
pattern when the rule is read, even if it would match nothing. Conversion and
the `brel` transition reader accept the same subset and report the same
unsupported construct before any write.

Decided by the user on 2026-11-26, during the question explanation after
review round 3, choosing the recommended option.

### Q17: What `fixes dry-run` measures

Question description: `fixes <root> dry-run` lists, per rule, how many matches
it made, "which uses existing text", and needs no git-cliff. Rules apply only
to content being generated, and ordinary rendering leaves released sections
unchanged, so counts over the whole existing file mostly measure text no
ordinary run will touch. The requirement does not say which text is measured
(the root file, the archives, or the snapshot section only), nor whether the
output shows the changed lines or only counts.

#### BBQ for Q17

Trying a new spice blend: tasting it on yesterday's whole buffet shows how it
would change every dish; tasting it only on today's soup shows what the next
customers will get. In this picture: the spice blend is the fix-rule set,
yesterday's buffet is the existing text including released sections and
archives, today's soup is the snapshot section, and the taste report is the
per-rule match counts.

#### Options for Q17

- Option A: a read-only diagnostic over existing text: apply, in memory, the
  built-ins and then each project rule in order, each on the result of the
  rules before it, as a run applies them, to the existing root file and every
  archive; report counts per rule and per file, plus each line a rule would
  change; write nothing. The report states that released sections change only
  through the explicit revision action, and that a zero count does not prove
  a rule unused: in generated text, the rule may already have done its work.
  - pro: shows what each rule would still change in existing text, and lets
    an author try a new rule on real text, with no binary needed.
  - con: counts over released text can be misread as what the next render
    changes.
- Option B: measure only the current snapshot section of the root file.
  - pro: matches what an ordinary run applies rules to.
  - con: right after a render the rules already ran there, so counts are near
    zero, and a new rule cannot be tried on older text.
- Option C: render the next content with git-cliff and measure there.
  - pro: an exact prediction of the next run.
  - con: needs the binary, which the requirement says dry-run does not.

#### Recommended option for Q17 (with arguments for this choice)

Option A: it serves both uses of the legacy debug output, checking what each
rule still matches and trying a new rule on real text, while staying
read-only and binary-free as the requirement asks. Counting in the order a
run applies the rules gives the numbers that run would see.

#### Answer to Q17: option A (with reason why it must be accepted as the answer)

Option A: the author sees exactly which lines each rule touches across all
changelog files, and the report says plainly that released sections only
change through the explicit revision action and that a zero count is not
proof of a dead rule.

User decision: confirmed — option A: a read-only diagnostic over existing
text: apply, in memory, the built-ins and then each project rule in order,
each on the result of the rules before it, as a run applies them, to the
existing root file and every archive; report counts per rule and per file,
plus each line a rule would change; write nothing. The report states that
released sections change only through the explicit revision action, and that
a zero count does not prove a rule unused: in generated text, the rule may
already have done its work.

Decided by the user on 2026-11-26, during the question explanation after
review round 3, choosing the recommended option.

### Q18: Comparison with dev_workflow's output that this item delivers

Question description: the requirement asks this item to compare its output with
dev_workflow's and document each intentional difference (the hash-free
heading, snapshot-marker ranges, the two llm-shared rules), while item 8 runs
the complete-pipeline parity rehearsals before cutover. It does not say on
which inputs this item compares, how the comparison is kept, nor how
my-project's 32 private rules are covered without copying them into
llm-shared. The legacy script needs `bash`, `sed`, `awk`, `perl` and the
git-cliff 2.7.0 binary that item 3 obtains only on an evidence-only path.

#### BBQ for Q18

Before switching bakeries, a café compares the new bread with the old: on a
fixed tray of test loaves, on the real morning orders, or not at all until
opening day. In this picture: the old bakery is dev_workflow's pipeline, the
new one is the engine, the test tray is frozen fixture histories, the morning
orders are a real repository, opening day is item 8's rehearsal, and a
private customer's order is my-project's rules.

#### Options for Q18

- Option A: frozen fixtures: synthetic histories, including the
  snapshot-marker shapes, and llm-shared's own inputs at a fixed commit
  (header, `cliff.toml`, its two rules). Their legacy outputs are recorded
  once with dev_workflow and kept as expected files; the tests compare the
  engine's output with them, and every byte difference is either removed or
  listed as intentional in the validation plan. my-project's rules are
  covered by conversion tests on synthetic rules using the same constructs,
  and the user can run the conversion privately on the real file. The real
  consumer migration and the complete-pipeline rehearsal keep their owners:
  my-project's own effort and item 8.
  - pro: repeatable, no private data in llm-shared, no legacy toolchain in
    each test run, and differences are reviewed before item 8.
  - con: the recording step is manual, and must be redone when a fixture
    changes.
- Option B: no legacy output: unit tests specify each behavior, and the
  intentional differences are listed in prose only.
  - pro: no legacy toolchain at all.
  - con: an unintended difference is only found at item 8.
- Option C: leave every comparison to item 8.
  - pro: smallest scope here.
  - con: contradicts the umbrella acceptance criterion assigned to this item.

#### Recommended option for Q18 (with arguments for this choice)

Option A: it delivers the comparison the acceptance criterion asks for, on
inputs anyone can rerun, without private content and without running bash
and Perl in every test. Item 8 then rehearses the complete pipelines on top
of an already reviewed difference list.

#### Answer to Q18: option A (with reason why it must be accepted as the answer)

Option A: the intentional differences are proven on frozen inputs and listed
before cutover, and my-project's rules are covered without copying them into
llm-shared.

User decision: confirmed — option A: frozen fixtures: synthetic histories,
including the snapshot-marker shapes, and llm-shared's own inputs at a fixed
commit (header, `cliff.toml`, its two rules). Their legacy outputs are
recorded once with dev_workflow and kept as expected files; the tests compare
the engine's output with them, and every byte difference is either removed or
listed as intentional in the validation plan. my-project's rules are covered
by conversion tests on synthetic rules using the same constructs, and the user
can run the conversion privately on the real file. The real consumer migration
and the complete-pipeline rehearsal keep their owners: my-project's own effort
and item 8.

Decided by the user on 2026-11-26, during the question explanation after
review round 3, choosing the recommended option.

### Q19: What remains when a changelog run fails after its automatic `fixes init`

Question description: in generated mode, `uc`, `uvf` and `/prepare-release`
Steps 10 and 11 run `fixes init` automatically before rendering, after the
git-cliff preflight, "so a missing tool cannot leave a newly created rule file
behind". That `init` converts an existing `.changelog.fixes` or, under Q14 B,
creates the starter file. The run can still fail after that `init` succeeded
in memory: a
missing `changelog-header.md`, a rendering failure, a declined repartition
(Q11), an invalid result, or a failure while writing the second of several
files. The user need asks every changelog run to write a complete, checked
result or leave the files as they were, and the requirement restores the
complete affected changelog set on failure, but it does not say whether a newly
created `.changelog-fixes.toml` belongs to that set. A standalone
`fixes <root> init` or `fixes <root> convert` writes only that file.

#### BBQ for Q19

A renovation crew is booked to replace the fuse box and repaint the kitchen in
one job. If the painting fails halfway and the job is called off, the owner
expects the house as it was; a new fuse box left behind from a cancelled job
is a surprise. A fuse box booked as a job of its own is another matter. In
this picture: the fuse box is the `.changelog-fixes.toml` converted from
`.changelog.fixes`, the painting is the render and its writes, the cancelled
job is a failed `uc` run, and the separate booking is a standalone
`fixes init` or `fixes convert`.

#### Options for Q19

- Option A: the automatic `init` joins the changelog's affected set: the new
  `.changelog-fixes.toml`, converted or created from the starter under Q14 B,
  is written together with the root file and the archives, only after every
  phase succeeds. A failure at any point leaves neither the new rules file nor
  any changelog change: a failure during a later write restores the files
  already written and removes the new rules file. The exposed write and delete
  set lists the rules file.
  A standalone `fixes init` or `fixes convert` writes its file as soon as it
  succeeds.
  - pro: one all-or-nothing rule for every changelog run, as the user need
    asks.
  - pro: preparation and release recovery see the rules file in the same
    exact set.
  - con: a conversion that succeeded is done again on the next run, at no real
    cost since it is deterministic.
- Option B: the automatic conversion writes the TOML as soon as it succeeds,
  and the file stays whatever happens to the render.
  - pro: the conversion result is visible even when the render fails.
  - con: a failed run leaves a new untracked file behind, the situation the
    preflight-before-`init` rule exists to avoid.
- Option C: the automatic conversion never writes: the run applies the
  converted rules in memory, and only a `fixes init` or `fixes convert` typed
  by hand writes the TOML.
  - pro: changelog runs touch only changelog files.
  - con: contradicts the umbrella's automatic conversion by
    `/prepare-release`, and the legacy file is never replaced.

#### Recommended option for Q19 (with arguments for this choice)

Option A: it extends the existing preflight rule to every failure, not just a
missing git-cliff, so a failed run never leaves a new file behind, and it
keeps the standalone maintenance commands independent.

#### Answer to Q19: option A (with reason why it must be accepted as the answer)

Option A: the person running `uc` either gets the complete, checked result,
rules file included, or finds the working tree as it was, and the exact write
set stays complete for preparation and recovery.

User decision: confirmed — option A: the automatic `init` joins the
changelog's affected set: the new `.changelog-fixes.toml`, converted or
created from the starter under Q14 B, is written together with the root file
and the archives, only after every phase succeeds. A failure at any point,
including a declined repartition (Q11), leaves neither the new rules file nor
any changelog change: a failure during a later write restores the files
already written and removes the new rules file. The exposed write and delete
set lists the rules file. A standalone `fixes init` or `fixes convert` writes
its file as soon as it succeeds.

Decided by the user on 2026-11-26, during the question explanation after
review round 3, choosing the recommended option, with the declined
repartition reading shown in the choice.

### Q20: What `fixes convert` does when `.changelog-fixes.toml` already exists

Question description: `fixes <root> init` creates `.changelog-fixes.toml` only
when it is missing, so it leaves an existing file alone. `fixes <root> convert`
"writes `.changelog-fixes.toml` from an existing `.changelog.fixes`" and stays
an optional maintenance command. Once the TOML exists, it is the only rules
file read, and its author may have edited it since the conversion. The
requirement does not say whether `convert` replaces an existing TOML, refuses,
or asks first.

#### BBQ for Q20

A translator is asked to translate an old letter again, but the earlier
translation on the desk carries the reader's handwritten corrections.
Translating over it erases them. In this picture: the old letter is
`.changelog.fixes`, the corrected translation is an edited
`.changelog-fixes.toml`, and translating again is `fixes convert`.

#### Options for Q20

- Option A: refuse before any write, naming the existing file and leaving both
  files unchanged; to convert again, the author removes or renames the TOML
  first.
  - pro: no single command can lose the author's edits, and `convert` behaves
    like `init` toward an existing file.
  - con: redoing a conversion takes one manual step.
- Option B: show what would change against the existing TOML (rules added,
  removed or changed) and replace the file only after confirmation, or with an
  explicit acceptance option in the non-interactive form; without it, nothing
  is written.
  - pro: follows the confirm-or-fail pattern of prompting commands, and
    redoing a conversion is one command.
  - con: one accepted prompt erases the edits, possibly in a TOML not yet
    committed.
- Option C: always replace the existing TOML.
  - pro: simplest.
  - con: silently loses the author's edits.

#### Recommended option for Q20 (with arguments for this choice)

Option A: a conversion is rare once the TOML exists, and the edited TOML is
the authoritative rules file, so protecting it outweighs saving one manual
step. It also gives `init` and `convert` the same rule: neither touches an
existing TOML.

#### Answer to Q20: option A (with reason why it must be accepted as the answer)

Option A: the authoritative rules file is never overwritten by a maintenance
command, and the refusal message tells the author exactly what to do to
convert again.

User decision: confirmed — option A: refuse before any write, naming the
existing file and leaving both files unchanged; the refusal is a failure
(non-zero exit). To convert again, the author removes or renames the TOML
first.

Decided by the user on 2026-11-26, during the question explanation after
review round 3, choosing the recommended option, with the failure reading
shown in the choice.

### Q21: What a generated run does with an existing archive whose preamble is missing or differs

Question description: Q13 A gives each generated archive a preamble: a
one-line title naming its range, then a relative link back to the root,
without the project header. Q04 A stops a generated run on unknown content
before the first section, but its wording names only the root's header and
archive links, and Q07 A keeps every byte of an existing archive when a first
render inserts a missing section. An archive written before the engine, or
edited by hand, can lack the title or the link back, or hold another line
before its first section. The requirement does not say whether such an
archive stops the run, is repaired, or is accepted, on a first render or on
an ordinary run. A valid archive that only lacks a historical section stays
Q07's successful insertion case. Q21 covers an archive serving a range that
holds at least one release; an existing file at an empty declared range
follows Q22 for its preamble and links. (Raised by review round 4.)

#### BBQ for Q21

A library receives donated volumes for a shelf it labels itself. Some arrive
with no spine label, or with a wrong one. The librarian can refuse to shelve
them until the donor fixes the label, relabel them, or shelve them as they
are. In this picture: the volumes are existing archive files, the spine label
is the archive's title and link back, relabeling is the engine rewriting the
preamble, and the donor is the author.

#### Options for Q21

- Option A: fail before any write, in every generated run, first render
  included, naming the archive path and the missing, extra or different
  preamble line; every byte of the archive stays as it was (Q07). For
  example, `docs/CHANGELOG.v0.1.0-v0.9.9.md` copied from an older layout
  starts with `# Old changelog` and has no link back: the run stops, naming
  line 1 and the missing link, and the author fixes both by hand once.
  - pro: no byte of an existing file changes without its author, and Q04's
    stop on unknown content applies to archives the same way.
  - con: one manual edit of a file that generated mode otherwise owns.
- Option B: rewrite the preamble to the engine's form, keeping every section
  byte for byte; the archive is listed in Q11's preview and the write set, and
  the run asks for confirmation as for a repartition.
  - pro: no manual step; the same command fixes the archive.
  - con: changes bytes that Q07 A keeps (lines outside every section), and
    adds a confirmation for a change that is not a repartition.
- Option C: accept any preamble in an existing archive and check only its
  sections.
  - pro: never blocks a run.
  - con: an archive can offer no way back to the root, which Q13 requires.

#### Recommended option for Q21 (with arguments for this choice)

Option A (reviewer proposal, round 4, pending the human decision): it keeps
Q07's promise that an existing archive's bytes never change during a first
render, extends Q04's named stop to the archive preamble, and tells the
author exactly which line to fix.

#### Answer to Q21: option A (with reason why it must be accepted as the answer)

Option A: an existing file never changes without its author, and the stop
names the path and the line to fix.

User decision: confirmed — option A: fail before any write, in every
generated run, first render included, naming the archive path and the
missing, extra or different preamble line; every byte of the archive stays as
it was (Q07). Qualification (user's words: "make sure the user knows what to
type and what to fix and why"): the failure message shows the exact
preamble lines expected, ready to type (the range title and the relative link
back to the root), says which lines to replace, insert or remove before the
first section, and says why: generated mode owns the archive preamble, the
link back is required so a reader can return to the root (Q13), and the
engine never rewrites an existing archive's bytes on its own (Q07).

Decided by the user on 2026-11-26, during the question explanation after
review round 5, choosing the recommended option with that qualification.

### Q22: An existing file at the path of a declared range that holds no release

Question description: Q13 A creates no file and no link for a declared range
holding no release, and prints a notice. Since the bounds are part of the
filename, a changed range normally gives a new path, and the old file becomes
an obsolete archive under Q12. A file can still sit at the declared path of
an empty range: for example `docs/CHANGELOG.v0.11.0-v0.11.9.md`, created by
hand before `[changelog-archive:0.11.0-0.11.9]` was declared, while
llm-shared never released `0.11.0`. The requirement does not say whether such
a file is kept, linked, rewritten or refused, nor, in curated mode, whether
both the root link to it and its link back are checked. Q12's deletion
authority covers only undeclared files. A file at that path that holds a
released section is not empty: that section still undergoes the coverage and
placement checks. (Raised by review round 4.)

#### BBQ for Q22

A shelf space is reserved for a volume that was never printed, yet someone
left an empty binder there. One can leave it, put it in the catalog, or ask
whoever left it to take it away. In this picture: the shelf space is the
declared range, the empty binder is the file at its path, the catalog is the
root's link block, and taking it away is a failure until the author removes
the file or changes the range.

#### Options for Q22

- Option A: keep the file unchanged and print a notice naming it, in both
  modes. Generated mode neither links it from the root nor rewrites it, and
  Q12's deletion authority does not extend to it. Curated validation checks a
  kept file's links in both directions, a working root link to it and its
  link back, as Q13 A's "checking the links of such a file" reads. For
  example, a zero-byte `docs/CHANGELOG.v0.11.0-v0.11.9.md` stays as it is,
  and a generated run prints a notice naming it.
  - pro: no file is deleted or rewritten without a rule that covers it.
  - con: a curated author who keeps the file must link it both ways.
- Option B: as A, but curated validation checks only the links that exist:
  a root link to the file or its link back must work, and neither is
  required.
  - pro: the least work for a curated author.
  - con: a kept file may stay unreachable from the root.
- Option C: treat the file as an archive in both modes: generated mode writes
  its preamble and links it from the root; curated validation requires both
  links.
  - pro: one behavior for every file at a declared path.
  - con: the root links to an archive that holds no release, which Q13 A
    avoids.
- Option D: fail before any write, naming the file, until the author deletes
  it or changes the range.
  - pro: no ambiguous file survives.
  - con: blocks every run for a harmless file.

#### Recommended option for Q22 (with arguments for this choice)

Option A (reviewer proposal, round 4, pending the human decision; the curated
link reading is the writer's): it keeps the file pending an explicit rule,
does not silently widen Q12's deletion authority, and keeps Q13's "no file,
no link" for generated output.

#### Answer to Q22: option A (with reason why it must be accepted as the answer)

Option A: a harmless file stays as it is, the notice names it, and curated
validation treats a kept file like any archive the author keeps.

User decision: confirmed — option A: keep the file unchanged and print a
notice naming it, in both modes. Generated mode neither links it from the
root nor rewrites it, and Q12's deletion authority does not extend to it.
Curated validation checks a kept file's links in both directions, a working
root link to it and its link back.

Decided by the user on 2026-11-26, during the question explanation after
review round 5, choosing the recommended option.

### Q23: Which links count in a curated changelog

Question description: Q13 A requires, in curated mode, one relative link from
the root to each declared archive and one link back to the root from each
archive, anywhere in the file. It does not say whether "one" means exactly
one or at least one, whether the link must resolve to the file, or whether a
link inside a fenced code block or an inline code span counts. In generated
mode, the engine-owned block holds exactly one link per linked archive (Q13
A). (Raised by review round 4.)

#### BBQ for Q23

A building inspector checks that every floor has a way to the exit. Several
signs on a floor are fine; a sign painted inside a framed picture of another
building is not a sign. In this picture: the floors are the curated files,
the signs are relative Markdown links, several signs are repeated links, and
the framed picture is a fenced code block or an inline code span.

#### Options for Q23

- Option A: at least one working relative Markdown link per destination: a
  link whose path, without any `#` fragment, resolves from the linking file to
  the declared archive or to the root `CHANGELOG.md`. Repeated links are
  accepted; links inside fenced code blocks or inline code spans do not
  count, nor does an absolute URL. For example, as a link check in isolation
  (that range holds untagged sections, which fail Q05's historical coverage),
  workspace-halo's root may link `docs/CHANGELOG.v0.0.1-v0.0.9.md` under
  `# Changelog` and again at the end of the file, while a `text` block quoting
  that link counts for nothing. A
  stale extra mention cannot satisfy the required link; one working link to
  the expected file satisfies the check, which is not a general broken-link
  audit.
  - pro: accepts any natural layout and refuses only a missing working link.
  - con: a stale extra link elsewhere in the file is not reported.
- Option B: exactly one working relative link per destination; a second one
  fails.
  - pro: one place to update when a range changes.
  - con: refuses a harmless second link.
- Option C: at least one mention of the destination's file name anywhere,
  code included, absolute URLs accepted.
  - pro: never blocks an author.
  - con: a quoted example or a link to another branch passes while the reader
    has no working way to the file.

#### Recommended option for Q23 (with arguments for this choice)

Option A (reviewer proposal, round 4, pending the human decision): it checks
what a reader needs, a link that works, and leaves the layout to the curated
author, as Q13 A intends; fenced examples follow Q09's rule that fenced lines
never count.

#### Answer to Q23: option A (with reason why it must be accepted as the answer)

Option A: every curated file has a working way to and from each archive,
whatever its layout, and a quoted example never stands in for a link.

User decision: confirmed — option A: at least one working relative Markdown
link per destination, a link whose path, without any `#` fragment, resolves
from the linking file to the declared archive or to the root `CHANGELOG.md`.
Repeated links are accepted; links inside fenced code blocks or inline code
spans do not count, nor does an absolute URL. A stale extra mention cannot
satisfy the required link; one working link to the expected file satisfies
the check, which is not a general broken-link audit.

Decided by the user on 2026-11-26, during the question explanation after
review round 5, choosing the recommended option.

### Q24: What `fixes dry-run` does in a curated project

Question description: Q17 A defines `fixes <root> dry-run` over existing
generated text. Curated mode applies no fix rule and never runs the automatic
`init`, but a curated project can still run `fixes <root> dry-run`, with or
without a `.changelog-fixes.toml`. Q08's curated validation rule does not
decide a standalone diagnostic, and the requirement does not say what it
does there. (Raised by review round 4.)

#### BBQ for Q24

A spice-blend taster asked to try the blend on a restaurant that serves only
raw dishes. They can say "nothing here gets seasoned" and leave, refuse the
visit, or taste anyway. In this picture: the restaurant is the curated
project, the blend is the rules file, and tasting anyway is measuring rules
that no run applies.

#### Options for Q24

- Option A: a successful no-op with an explanatory notice that the project is
  curated and applies no fix rule; no rules file or changelog file is read,
  and the command exits 0.
  - pro: a script or an author gets a clear answer without a failure.
  - con: a rules file left in a curated project is not checked.
- Option B: a failure naming the curated mode.
  - pro: says loudly that the command does not apply.
  - con: fails a harmless diagnostic, and a script must special-case curated
    projects.
- Option C: measure the rules anyway on the curated files, read-only, with a
  notice that curated mode never applies them.
  - pro: shows what a rules file would change after a switch to generated
    mode.
  - con: reports changes that no curated run will ever make.

#### Recommended option for Q24 (with arguments for this choice)

Option A (reviewer proposal, round 4, pending the human decision): it keeps
curated mode free of fix rules, as the requirement states, while giving the
person running the diagnostic a plain explanation and a successful exit.

#### Answer to Q24: option A (with reason why it must be accepted as the answer)

Option A: the diagnostic answers truthfully that curated mode applies no rule,
without failing and without measuring text no run will change.

User decision: confirmed — option A: a successful no-op with an explanatory
notice that the project is curated and applies no fix rule; no rules file or
changelog file is read, and the command exits 0.

Decided by the user on 2026-11-26, during the question explanation after
review round 5, choosing the recommended option.
