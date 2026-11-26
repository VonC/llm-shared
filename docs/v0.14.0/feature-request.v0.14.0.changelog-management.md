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
headings is set by the released headings of "Generated changelog contract"
(Q04) and by the curated heading forms of "Curated mode checks without
rewriting" (Q09); a `##` line inside a fenced code block is never a heading.

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
no longer declares: it is still an archive file, which a repartition deletes
or keeps and reports as "Repartition of sections after a bounds change" says
(Q12). An archive is never a Git
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
| Generated untagged stable heading | `vX.Y.Z`, display only | `## [v0.15.0 unreleased] <title>` |
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

Naming a version selects what the command does with it. The version being
prepared renders as usual. In generated mode, a released `vX.Y.Z` is the
explicit revision action of
[the authority section](#authority-of-released-changelog-sections): the run
renders that section's range again and shows a preview of the proposed
change, naming the file that holds the section, keeping editorial notes and
reporting conflicts, and writes only after confirmation, or with an explicit
acceptance option in the non-interactive form; without it, nothing is
written. In curated mode the argument is a read-only lookup of that version's
section (Q01).

The `uc` and `uvf` aliases refresh generated changelog content or validate
curated content. Interactive aliases resolve the current Git worktree and pass
that root explicitly; the engine never infers a target from `PRJ_DIR`. `uvf`
runs the same command as `uc`: it is kept so existing habits keep working,
and it never prompts for a next snapshot, which `uver` owns (Q03). This
effort defines no alias named `uv` or `uvr`, only `uver` (Q09).

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
that a section for the exact release exists. A release section has one of a
closed list of level-two headings: `## X.Y.Z`, `## vX.Y.Z`, `## [X.Y.Z]` and
`## [vX.Y.Z]`, holding a complete version token, in brackets closed right
after it when a bracket opens, then the end of the line or whitespace before
optional free text, such as a date or a title; a substring never matches. A
heading that looks versioned but fits no form fails, and neither a malformed
bracket, such as `## [0.0.25 notes`, nor a `## 0.0.25` line inside a fenced
code block satisfies the release check (Q09). It requires neither
git-cliff nor `changelog-header.md`, does not inject notes, dates or fix rules,
and preserves the curated file byte for byte.

Outside a release, curated validation runs every other check first: headings,
ranges, links, duplicates and the historical check of "Releases and sections
must agree". It then classifies the `version.txt` version in the order of
"Classification of the `version.txt` version": an eligible release of this
history needs its section, with a notice pointing to `uver` when commits
follow its tag; a version reserved only by an unvalidated engine release or by
a tag HEAD does not reach fails, naming the tag and its state; a version no
stable tag reserves is the forthcoming target, whose missing section is a
notice that leaves the exit status at 0 when every other check passed.
Release validation requires the release version's section before any write,
even when the release started from a snapshot anchor (Q08).

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

### Classification of the `version.txt` version

Outside a release, an ordinary generated refresh (`uc`, `uvf`, or
`changelog <root>` with `latest` or no argument) classifies the `version.txt`
version in this order, and the first matching case decides (Q02):

1. an eligible release of this history, as item 2 decides, whose tag is on
   HEAD, as in a repeated run right after a release. When the changelog files
   exist and pass the check of "Releases and sections must agree", there is
   nothing to render: the released section stays as it is and the run exits
   0, while a pending repartition still runs, with the preview and
   confirmation of "Repartition of sections after a bounds change". When they
   fail that check, for example with no section for that release, the run
   stops as that check says. When the root file is missing, the first render
   below creates it, with that release's section;
2. an eligible release of this history whose tag is below HEAD, with commits
   after it: the refresh refuses before any write, naming the tag and pointing
   to `uver`;
3. a version reserved only by a tag that is not a release of this history: an
   unvalidated engine release, on HEAD or not, or a tag HEAD does not reach,
   such as one on another branch. The refresh refuses before any write,
   naming the tag and its state, and points to item 5's release recovery for
   an unvalidated release, or to `uver` for a version taken elsewhere;
4. a version no stable tag reserves: the forthcoming target. The unreleased
   heading shows the token as written, `## [vX.Y.Z unreleased] <title>` for an
   untagged stable version and `## [vX.Y.Z-SNAPSHOT unreleased] <title>` for a
   snapshot.

A refusal covers the whole refresh, so a pending repartition waits until its
cause is fixed. It never applies to the explicit historical revision (Q01),
which names its version and has its own preview and acceptance. The range
baseline stays item 2's eligible stable release, which can differ from a
reserving tag.

### Released headings and other content of a generated file

A generated file recognizes a fixed set of released headings: the dated
`## [vX.Y.Z] - YYYY-MM-DD - <title>`, the date-less `## [vX.Y.Z] - <title>`,
which llm-shared's `## [v0.2.0] - Green is not the same as done` already
uses, and the same two with an unprefixed `X.Y.Z`. Each existing heading is
kept byte for byte, with no date added to a date-less one. The unreleased
headings are explicit exceptions that the engine owns and rebuilds on each
run: the two forms of the classification above, and the same forms ending
with a dash and the full commit hash, as dev_workflow wrote them, which the
first run replaces as "Hash-free snapshot changelog heading" shows. A line
inside a fenced code block is never a heading. Any line before the first
section other than the preamble that "Sections of a changelog file"
describes, and any other level-two heading, stops the run before any write,
naming its line (Q04).

### Ownership of the unreleased section

The unreleased section, in both heading forms, is engine-owned: each run
rebuilds it from the commits and the `version.txt` release notes, and hand
edits there are replaced. The documentation points authors to `version.txt`
for release notes and to `.changelog-fixes.toml` rules for lasting wording
corrections. At release, the section becomes released and authoritative
(Q06).

### Releases and sections must agree

The sections in the changelog files are what gets placed, and they are
checked against the eligible stable releases HEAD reaches, as item 2's
selector decides. With an existing root file, a release with no section, a
section with no tag, or a section whose version only an unvalidated or
unreachable tag names stops the run before any write, except the section of
the version being prepared or released. A first render checks nothing
beforehand and checks the assembled result before any write (Q05). Curated
validation applies the same check (Q08).

### First render when CHANGELOG.md is missing

A first render runs whenever the root file is missing, whatever archives
exist. It creates a section for each eligible annotated release of this
history that no file holds yet, placed by the archive policy: in the root, in
a new archive file, or in an existing archive whose preamble passes, where the
section is inserted in newest-first order and the file keeps all its existing
bytes, in order. Each created heading uses the dated form, with the calendar
date of the tagger date in the tag's recorded offset and the first line of the
tag message as title. An eligible release whose tag is lightweight stops the
run, naming it. The check of "Releases and sections must agree" then runs on
the assembled result before any write (Q07). For example, with no root, an
archive for `1.0.0` to `1.2.0` holding only `1.0.0`, and an eligible annotated
`v1.1.0` with no section, the first render inserts the `1.1.0` section into
that archive above `1.0.0`, keeps every existing byte of the archive, and
creates the root.

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
`recent-from` is required as soon as one archive range is declared, and must
be higher than every archive `to`; without archives it is optional and the
root holds every release. The space between the newest archive and
`recent-from` follows the gap rule below. Every violation stops the run before
any write, as a failure (Q10).

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

An interactive run shows that preview and asks before writing; the
non-interactive form fails with the preview unless an explicit acceptance
option is passed. The preview names every affected file, the root and each
archive written, created or deleted, and the sections moving between them. A
run with no pending repartition asks nothing. A "no" at the prompt writes
nothing and is a failure, since the files still disagree with `.release.ini`;
the next run asks again (Q11).

A repartition deletes an archive file that is no longer declared only with
positive evidence that the engine managed it under an earlier config, and
only when every section it held now appears, byte for byte, exactly once in a
declared destination; how that evidence is kept is design work. Without that
evidence, the file stays in place and is reported: a notice when it holds no
released section, a failure when its sections also exist in a declared
destination. A managed archive with local changes stops the run before any
write, naming the file (Q12).

A declared range that holds no existing release needs no archive file and no
link: generated mode creates neither and prints a notice (Q13). A file already
present at the path of such a range is kept unchanged, with a notice naming
it: generated mode neither links it from the root nor rewrites it, and the
deletion rule above does not extend to it. A file there that holds a released
section is not empty: that section undergoes the coverage and placement
checks (Q22).

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
curated prose. A section naming no version, such as `## Unreleased`, takes no
part in placement.

The root needs at least one working relative Markdown link to each declared
archive, and each archive at least one working link back to the root
`CHANGELOG.md`, anywhere in the file: a link whose path, without any `#`
fragment, resolves from the linking file to the expected file. Repeated links
are accepted; links inside fenced code blocks or inline code spans do not
count, nor does an absolute URL. A stale extra mention cannot satisfy the
required link, and one working link to the expected file satisfies the check,
which is not a general broken-link audit (Q13, Q23). A declared range that
holds no release needs no file and no link; a file the author keeps there is
checked in both directions, a working root link to it and its link back
(Q22).

### Authority of released changelog sections

Existing released sections are authoritative during ordinary generated-mode
rendering (confirmed answer Q3 A). Changed fix rules do not automatically
rewrite released history; historical revisions require an explicit action,
`changelog <root> vX.Y.Z` naming a released version in generated mode (Q01).
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
  guessing. A `push` pair converts only within a closed subset, defined by
  what it accepts rather than by what Python compiles: `qr/.../` with
  optional `i`, `m`, `s` and `x` flags, carried as inline flags, and a
  replacement that is one double-quoted Perl string made of literal text,
  `$N`, `${N}` or `\N` group references and the escapes `\n`, `\t`, `\\`,
  `\"`, `\$` and `\@`. The converted rule must match what the Perl rule
  matched on the same bytes, non-ASCII text included. Any other form, and any
  construct Python reads differently, such as `\Z`, `\v`, `\u$1` or another
  delimiter, fails the conversion, naming the line and the construct;
  replacement escapes and group references are checked against the pattern
  when the rule is read, even if it would match nothing, and the transition
  reader accepts the same subset (Q16). A `=>` line converts to what it says
  (Q15), within the
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
  rule unused. An invalid rule fails it before any report, as below. In
  curated mode it is a successful no-op: it prints a notice that the project
  is curated and applies no fix rule, reads no rules file or changelog file,
  and exits 0 (Q24).

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
    (Q18): synthetic histories with the snapshot-marker shapes, and
    llm-shared's own inputs at a fixed commit, whose legacy outputs are
    recorded once with dev_workflow and kept as expected files. Remove each
    byte difference or list it as intentional in the validation plan,
    including the hash-free heading, the snapshot-marker ranges and the effect
    of llm-shared's two fix rules. The comparison covers generated root-only
    output with no archive declared, since dev_workflow writes no archive and
    has no curated mode; archives and curated validation are tested against
    the engine's own expected results. my-project's 32 rules are covered by
    conversion tests on synthetic rules using the same constructs.

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

## Requirement clarifications for changelog management

The user decided Q01 to Q20 after explanations from 2026-11-24 to 2026-11-26,
and independent review rounds 4 and 5 checked those decisions. Review round 4
raised Q21 to Q24, which the user decided on 2026-11-26 and round 6 checked.
Every choice is the recommended option. The question blocks, with their full
options and arguments, are kept in the commit
`docs(feature): record pre-consolidation questions`.

| Question | Decision and reason | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | In generated mode, naming a released `vX.Y.Z` is the explicit revision action: a preview, written only after acceptance or an explicit acceptance option; the version being prepared renders as usual; in curated mode a read-only lookup. Gives the authority rule its one entry point | Changelog commands and aliases; Authority of released changelog sections | Refusing every released version (no revision entry point); dropping the argument until a later command |
| Q02 | An ordinary refresh classifies the `version.txt` version in four ordered cases, refusing a released or reserved version, and the unreleased heading shows the token as written, snapshot or untagged stable. No render replaces a released section, and each refusal says what to do | Classification of the `version.txt` version; Version notation; acceptance criteria | Always a `-SNAPSHOT` heading (hides the anchor); no refusal, leaving reuse to the release preflights |
| Q03 | `uvf` runs the same command as `uc`, kept for existing habits; it never prompts for a next snapshot, which `uver` owns | Changelog commands and aliases | `uvf` running `versions check` first; the legacy next-snapshot transition |
| Q04 | A fixed set of released headings (dated and date-less, `vX.Y.Z` or `X.Y.Z`) kept byte for byte; unreleased headings, hash-bearing ones included, rebuilt; fenced lines never headings; any other preamble line or level-two heading stops the run. Every byte has a known owner, so a move is provable | Released headings and other content of a generated file; Sections of a changelog file | Any bracketed heading with stray content attached and a warning (silent moves); normalizing headings and dropping content (rewrites history) |
| Q05 | Sections are placed and checked against the eligible stable releases HEAD reaches; with an existing root, a release without section, a section without tag or one named only by an unvalidated or unreachable tag stops the run, except the target; a first render checks the assembled result | Releases and sections must agree; Consumer inputs (workspace-halo); Completeness and order checks | Tags alone defining releases, extra sections ignored; the union of both with no mismatch check |
| Q06 | The unreleased section, in both heading forms, is engine-owned and rebuilt on each run; the documentation points to `version.txt` for release notes and to fix rules for lasting wording corrections; it becomes authoritative at release | Ownership of the unreleased section; acceptance criteria | Refusing to rebuild after hand edits; merging unrecognized lines into the rebuilt section |
| Q07 | A first render, whenever the root is missing, creates a section for each eligible annotated release no file holds, inserting into existing archives newest first while keeping their bytes; dated heading from the tagger date in its offset, title from the tag message's first line; a lightweight eligible tag stops the run | First render when CHANGELOG.md is missing | Legacy date-less headings; out of scope until setup creates the file; refusing an incomplete existing archive (option D) |
| Q08 | Outside a release, curated validation runs every other check first, then the classification order: a released version needs its section (a notice pointing to `uver` when commits follow its tag), a version reserved elsewhere fails, a forthcoming target's missing section is a notice; release validation requires the section. Qualification: section, release notes and notice are defined in the topic draft and here, and inform every later question | Curated mode checks without rewriting; Changelog sections, release notes and notices | A missing target section always failing; skipping the target check outside a release |
| Q09 | A closed list of curated level-two forms, `## X.Y.Z`, `## vX.Y.Z`, `## [X.Y.Z]` and `## [vX.Y.Z]`, with optional free text; near misses fail; malformed brackets and fenced lines never count; a heading naming no version is a section boundary. Direction: no alias named `uv` or `uvr`, only `uver` | Curated mode checks without rewriting; Sections of a changelog file; Changelog commands and aliases; umbrella alias row | Only `## X.Y.Z` and the generated dated form; any heading at any level whose first version token matches |
| Q10 | `recent-from` is required once an archive is declared and must exceed every archive `to`; optional without archives; the space between follows the gap rule; violations are failures before any write. No boundary is inferred | Archive bounds and destinations | Inferring the root's bound from the highest archive `to`; an optional bound with uncovered releases left in the root |
| Q11 | A repartition shows its preview and asks; the non-interactive form fails unless accepted; the preview names every file written, created or deleted and the moving sections; a "no" writes nothing and is a failure | Repartition of sections after a bounds change | Writing in the same run as the preview; a separate command, leaving files and config in disagreement |
| Q12 | An undeclared archive is deleted only with positive evidence of earlier engine management and after every section is verified exactly once in a declared destination; otherwise kept and reported, a notice without released sections, a failure with duplicated ones; a managed archive with local changes stops the run. Qualification: archive is defined in all three documents | Repartition of sections after a bounds change; Sections of a changelog file; topic draft; umbrella | Never deleting (duplicates on every run); deleting every matching name; deleting any clean tracked file (proves recoverability, not ownership) |
| Q13 | Generated mode writes an engine-owned link block after the root header, newest range first, and each archive opens with a range title and a link back, without the project header; curated mode needs the links anywhere; a declared range holding no release gets no file, no link and a notice | Sections of a changelog file (preamble); Archive bounds and destinations; Repartition of sections after a bounds change; Archive ranges of a curated changelog | Repeating the project header in archives and imposing it on curated files; links only in the root (no way back) |
| Q14 | In generated mode the automatic `init` converts a legacy `.changelog.fixes` or creates the commented starter; curated mode never runs it. Keeps the umbrella's item 4 details | Python fix-rule runner replacing Perl | Converting only, with no starter; the starter in curated projects too |
| Q15 | A `=>` line converts to what it says, within the accepted subset: the author's regex without the added quotes or backslash doubling, a literal replacement with group references; each converted line gets a notice when the whole file converts; an unsupported line fails | Python fix-rule runner replacing Perl; Notices that never fail a run; acceptance criteria | Refusing every `=>` line; reproducing the broken Perl effect, which needs a Perl evaluator |
| Q16 | A closed subset of Perl patterns and replacements; the converted rule must match what Perl matched on the same bytes, non-ASCII included; anything else fails, naming the line and construct; replacements checked when read; the transition reader accepts the same subset | Python fix-rule runner replacing Perl | Translating case modifiers and other Perl features (hidden semantics); only the forms the known files use |
| Q17 | `fixes dry-run` applies the rules in run order, in memory, to the existing root and every declared archive, reporting counts per rule and per file with each changed line, and writes nothing; the report says released sections change only by explicit revision and a zero count is no proof of an unused rule | Python fix-rule runner replacing Perl | Measuring only the snapshot section; rendering with git-cliff first (needs the binary) |
| Q18 | Frozen fixtures, synthetic marker histories and llm-shared's inputs at a fixed commit, with legacy outputs recorded once as expected files; every byte difference removed or listed in the validation plan; my-project covered by synthetic conversion tests and a private run | Gap item 11; acceptance criteria | Unit tests and prose only (differences found at item 8); leaving every comparison to item 8 |
| Q19 | A rules file the automatic `init` converts or creates joins the atomic write set: written with the changelog files only after every phase succeeds, removed on any failure, a declined repartition included; standalone `init` and `convert` write at once | Writes and temporary files of changelog work; acceptance criteria | Writing the TOML as soon as it converts (an untracked leftover); never writing it from a run |
| Q20 | `fixes convert` refuses before any write when `.changelog-fixes.toml` exists, naming it, as a failure; to convert again the author removes or renames the TOML | Python fix-rule runner replacing Perl | A diff and confirmation (one "yes" erases edits); always replacing it |
| Q21 | An existing generated archive with a missing, extra or different preamble line stops every generated run before any write, first render included, keeping its bytes. Qualification: the failure shows the two expected lines ready to type, the edits needed and why | Sections of a changelog file (preamble); acceptance criteria | Rewriting the preamble after confirmation (changes bytes Q07 keeps); accepting any preamble (no way back) |
| Q22 | A file at the path of a declared range holding no release is kept unchanged with a notice; generated mode neither links nor rewrites it, and deletion does not extend to it; curated validation checks a kept file's links both ways | Repartition of sections after a bounds change; Archive ranges of a curated changelog | Checking only existing curated links; treating it as a linked archive; failing until it is removed |
| Q23 | Curated mode needs at least one working relative Markdown link per destination; repeats are accepted; fenced code, inline code and absolute URLs do not count; it is not a broken-link audit | Archive ranges of a curated changelog | Exactly one link per destination; any mention of the file name, code and URLs included |
| Q24 | In a curated project, `fixes dry-run` is a successful no-op with a notice that curated mode applies no fix rule, reading no rules or changelog file | Python fix-rule runner replacing Perl | A failure naming the curated mode; measuring rules no curated run applies |
