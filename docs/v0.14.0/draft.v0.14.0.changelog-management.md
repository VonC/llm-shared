# Manage generated and curated changelogs

- Type: feature-request
- Test group: whole suite
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Target version: v0.14.0
- Documentation layout: docs/v0.14.0/
- Slug: changelog-management

## Selected umbrella entry for changelog management

| Order | Type | Key title | Slug | Status | Requirement | Validation plan |
| --- | --- | --- | --- | --- | --- | --- |
| 4 | Feature-request | Manage generated and curated changelogs | `changelog-management` | pending | - | - |

### Requirement detail inherited for changelog management

- Type: Feature-request
- Key title: Manage generated and curated changelogs
- Slug: `changelog-management`
- Regroups: default/project cliff config, header, stable ranges, exact-once notes,
  snapshot/release headings, groups/duplicates, generated/curated modes,
  built-in cleanups, declarative fixes/conversion and configurable archives.
- Boundary rationale: one owner manages content/range placement and preservation;
  item 5 owns release commits/tags and transaction recovery.
- Depends on: `release-project-root`, `version-sources`, `git-cliff-provisioning`.
- Ownership: renderer/validator, fix-rule runner and changelog/archive settings.
- Acceptance criteria:
  - Generated mode uses explicit project/default config, required header and
    stable-tag selection, injects anchor notes once, labels groups, preserves
    historical notes/dates and avoids duplicate target sections. Repeated runs
    on unchanged inputs produce identical output.
    Preserve existing released sections during ordinary rendering, including
    when fix rules change. Historical revisions require an explicit action;
    preserve editorial notes, report competing content sources and expose
    intentional revisions in the proposed changed set. Archive moves preserve
    section bodies.
  - Use hash-free `## [vX.Y.Z-SNAPSHOT unreleased] <title>` and dated
    `## [vX.Y.Z] - YYYY-MM-DD - <title>` headings, with the captured release date.
    No filter.changelog; snapshot tags never truncate commits or create a
    released section, including a snapshot marker on HEAD.
    Restrict git-cliff's release tags to the stable rule; never exclude a
    marker through `skip_tags`, which drops its commits. Replace the
    unfiltered readers of `update-changelog.sh` and `cliff.toml` listed in
    "Snapshot-tag readers still to migrate", tested on its histories.
  - Apply numeric recent/archive policy to root plus
    `docs/CHANGELOG.vA.B.C-vD.E.F.md`; validate bounds, destinations, overlap,
    coverage and links. Repartition complete sections when bounds change,
    including owned obsolete archive removal, without losing content.
    Added at the child-draft review (2026-11-23): before writing, prove a move
    by an identical set of released sections, each byte for byte unchanged,
    and keep sections sorted newest first in the root and every archive.
  - Curated mode validates exact supported headings (including `## X.Y.Z`),
    ranges and links while preserving every file byte; no automatic generation,
    archive movement, git-cliff, header or fix-rule prerequisite.
  - Apply built-in cleanups before TOML rules to content being generated,
    preserving existing released sections during ordinary rendering. Convert
    only supported Perl push pairs/legacy arrows; name unsupported lines or invalid regex rules
    and fail. TOML wins over legacy with a warning; dry-run gives match counts.
  - `uc`/`uvf` and preparation provision/check git-cliff before automatic fixes
    init/conversion. A direct release uses the in-memory transition reader,
    without making the tree dirty with a new untracked rules file.
  - Assemble/validate all output before writes; failures restore the complete
    affected changelog set. Use unique project artifacts and expose the exact
    write/delete set to preparation/release recovery. Compare legacy output
    with documented intentional differences, including the two llm-shared rules.

## Changelog sections, release notes and notices

Three words recur in this draft and in the documents that follow it.

A section is the part of a changelog file that starts at a level-two `## ...`
heading and runs over every line under it, up to the next level-two heading.
Most sections name a version; a curated file can also hold one that names
none, such as workspace-halo's `## Unreleased`, which the engine keeps as
written without treating it as a release. The lines at the top, before the
first section, belong to no section: in a generated root, the header and the
links to the archives; in a generated archive, a title naming its range and a
link back to the root. In llm-shared's generated
`CHANGELOG.md`, `## [v0.14.0] - 2026-11-12 - Groundhog Shares the Stopwatch`
opens the section of a released version, and
`## [v0.15.0-SNAPSHOT unreleased] <title>` would open the section of the
version in development. workspace-halo's hand-written file looks like this:

```text
# Changelog

## Unreleased

## 0.0.24

- Stop VS Code windows from taking turns coming to the front after a monitor
  unplug: ...

## 0.0.23
```

Its `## Unreleased` section is empty and names no version; the `0.0.24`
section holds the author's bullets. Sections matter because every changelog
rule works on them: the engine keeps released sections as written, moves
whole sections to archives, and, in curated mode, checks that the section of
each release exists. The bracketed groups of `.release.ini`, such as
`[changelog]`, are configuration sections, a different thing that this draft
always names with its bracketed name.

An archive is a file such as `docs/CHANGELOG.v0.1.0-v0.13.9.md` that holds the
released sections of one older version range, so the root `CHANGELOG.md`
keeps only the version in development and the recent releases. Each archive
is declared by a `[changelog-archive:...]` configuration section in
`.release.ini`. In generated mode the engine writes archives itself; in
curated mode the author writes them and the engine checks them. A file that an
earlier `.release.ini` declared and the current one no longer does is an
obsolete archive: the engine deletes it only when it can prove it managed it
and every section moved. An archive is not a Git archive, a zip file or a
GitHub release asset.

Release notes are the text a person writes about a release, as opposed to the
commit list git-cliff builds. In generated mode, they are the body of
`version.txt` below its first line, which the engine copies once into the
section of the version being prepared. In curated mode, they are what the
author writes under the release's heading, bullets or paragraphs, usually
shortly before the
release: workspace-halo's author added `## 0.0.24` the day before the commit
that prepared that release. Once released, a section keeps its release notes
as written; the acceptance criteria above call them historical or editorial
notes.

A notice is a message the engine prints for the person running it without
failing: the command still exits with status 0. A failure prints a message
and exits with a non-zero status, which stops a calling script or a release.
The requirement uses notices, for example when a curated changelog does not
have the section of the version in development yet.

## Context and scope of changelog management

dev_workflow renders and post-processes the changelog with these pieces, each
with its fate in the umbrella:

| Piece | Role today | Proposed fate |
| --- | --- | --- |
| `update-changelog.bat` + `.sh` | git-cliff run, sed clean-ups, `version.txt` body injected under the unreleased heading, header prepended, section labeling, `.changelog.fixes` | Engine `changelog` command, git-cliff kept, sed dropped |
| `cliff.toml` | Commit groups, skipped release chores | Moves to llm-shared as the default, a project `cliff.toml` overrides it |
| `changelog_duplicate_version_section_remover.awk`, `changelog_section_labeler.awk` | Changelog post-processing | Rewritten in Python, awk dropped |
| `update-changelog.fixes.tpl.pl` | Runs `.changelog.fixes` through Perl `s///gee` | Replaced by a Python rules runner, Perl dropped (see the fix-rules section below) |

`update-changelog.sh` line 10 runs `${PRGS}/git-cliffs/current/git-cliff.exe`
with `-c "${DEV_WORKFLOW_DIR}/cliff.toml" -w "${PRJ_DIR}" -s footer -o
"${PRJ_DIR}/CHANGELOG.tmp.md"`, then post-processes that file. After the
rewrite, the engine uses llm-shared's Python and Git, plus git-cliff only for
generated changelogs: no `bash`, `sed`, `awk`, `perl` or `cygpath`.

The three merged items supply what this one builds on:

- Item 1, `release-project-root`: the explicit validated project root,
  root-scoped Git, dispatch through the self-locating `bin/release_workflow.bat`
  and `bin/release_alias.bat`, the artifact home, the common managed-write
  functions (design decision Q06 A) and the common `.release.ini` reader, read
  with interpolation off, which composes explicitly registered domain schemas
  and validates every declared setting before mutation. Its shipped schemas are
  `tooling`, `version` and `git-cliff`: a `[changelog]` or
  `[changelog-archive:...]` section is reported as unknown until this item
  registers its schema. The command registry ships `version` and `versions`;
  `changelog` and `fixes` are new commands of this item.
- Item 2, `version-sources`: the shared stable/snapshot tag classifier and
  range selector (`tools/release_workflow/tags.py`, exposed as
  `versions <root> range [<stable tag>]`), with the commit count read from
  `git rev-list --count` on the selected range. No existing reader calls the
  selector yet; this item switches the changelog readers to it.
- Item 3, `git-cliff-provisioning`: the pinned git-cliff 2.14.2, downloaded
  into the executing checkout's ignored `.tools/git-cliff/` cache, checked
  before every use and started only through `GitCliffInvocation`. An engine
  caller that cannot get the binary receives a `ProvisioningError` (status 2)
  with the setup diagnostic. Its approved evidence bundle,
  `tools/release_workflow/git_cliff/bundles/2.14.2/`, compares raw git-cliff
  output of 2.7.0 and 2.14.2 on frozen inputs. Item 3 leaves to this item the
  decision of when rendering needs git-cliff.

This item owns the renderer and validator, the fix-rule runner and the
changelog and archive settings. It does not own:

| Behavior outside changelog management | Owning umbrella item |
| --- | --- |
| Pin admission, download, cache and invocation of git-cliff | 3, `git-cliff-provisioning` (completed) |
| The stable/snapshot tag classifier and range selector this item consumes | 2, `version-sources` (completed) |
| Release commit, annotated tag, transaction record and recovery of the affected changelog set; calling rendering or curated validation in release `pre` | 5, `build-release-lifecycle` |
| Proposing an initial archive split and generating `.release.ini` during setup; exposing `uc`/`uvf` to consumers not yet loading llm-shared's alias file | 6, `release-tooling-setup` |
| `/prepare-release` Steps 10 and 11 calling the changelog services, its Step 11 wording, Step 13 staging the rules file, `.release.ini` and archive set, and `prepare_release_notes` | 7, `prepare-release-integration` |
| llm-shared's own archive ranges and rule conversion, removing `filter.changelog` from existing clones, adding the aliases to the shared `senv.doskey`, removing `update-changelog.sh`, and the complete-pipeline parity rehearsals | 8, `llm-shared-cutover` |

## Version notation in changelog headings and archives

| Context | Form | Example |
| --- | --- | --- |
| Generated snapshot heading | `vX.Y.Z-SNAPSHOT`, display only | `## [v0.14.0-SNAPSHOT unreleased] <title>` |
| Generated release heading | `vX.Y.Z` | `## [v0.14.0] - YYYY-MM-DD - <title>` |
| Archive bounds in `.release.ini` | `X.Y.Z`, without `v` | `recent-from = 0.14.0` |
| Archive filenames | `vX.Y.Z` | `docs/CHANGELOG.v0.1.0-v0.13.9.md` |
| New stable Git tag / legacy stable tag | `vX.Y.Z` / `X.Y.Z`, both readable | `v0.14.0` / `0.0.21` |

A generated snapshot heading does not imply that a Git tag exists. Curated
changelogs may retain their documented unprefixed heading style. Legacy
unprefixed stable tags remain readable; new stable tags always have `v`.

## Engine commands for changelog management

The umbrella lists these commands among the engine's:

- `changelog <root> [latest|vX.Y.Z]`;
- `fixes <root> init|convert|dry-run`.

Every command that can prompt also takes a non-interactive form that fails
with a message instead of asking, so `/prepare-release` can drive it from its
own menus.

The `uc` and `uvf` aliases refresh generated changelog content or validate
curated content. Interactive aliases resolve the current Git worktree and pass
that root explicitly; the engine never infers a target from `PRJ_DIR`.

## Per-project changelog settings

Existing project files keep their meaning: `version.txt`, `CHANGELOG.md`,
`changelog-header.md`. New ones, only where a project needs to differ from the
defaults:

- a project `cliff.toml` overriding llm-shared's default one;
- `.changelog-fixes.toml`, the fix rules (see the fix-rules section below);
- the `[changelog]` and `[changelog-archive:...]` sections of `.release.ini`.

A project without `.release.ini` gets every default; invalid values are never
replaced silently with defaults. Approved release-project-root design decision
Q03 A keeps schemas and defaults beside their owning components: the changelog
component, for example, defines the accepted `generated` and `curated` modes.

```ini
[changelog]
; generated (git-cliff, the default) or curated (author-maintained)
mode = generated
; proposed archive policy syntax: numeric inclusive bounds, no v prefix
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

dev_workflow knows only the first way: `update-changelog.sh` always runs
git-cliff and always rewrites `CHANGELOG.md`, with no setting to turn that
off. Its only option selects which part to regenerate (`latest`, a tag name,
or the whole history when no `CHANGELOG.md` exists yet); that option becomes
the `changelog <root> [latest|vX.Y.Z]` argument, not a mode. So each project
declares its way with one line in `.release.ini`:

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

In `curated` mode the engine never rewrites `CHANGELOG.md`: it only checks
that a section for the exact release exists (allow `## X.Y.Z` and the
documented `vX.Y.Z`/bracketed heading forms, never a substring match). It
requires neither git-cliff nor `changelog-header.md`, does not inject notes,
dates or fix rules, and preserves the curated file byte for byte. Archive
movement also requires author edits in this mode; the engine validates range
placement and links.

`changelog-header.md` is checked only by the `changelog` command, and only in
generated mode.

## Generated changelog contract

Generated mode uses the project's `cliff.toml` or llm-shared's default,
requires `changelog-header.md`, and applies the built-in cleanups followed by
project fix rules to content being generated. Ordinary rendering preserves
existing released sections; revising them requires the explicit action
described in the archive section. Inject `version.txt`'s release-notes body
exactly once under the target heading; rerunning on unchanged inputs is
idempotent. During a snapshot use the hash-free unreleased heading below; at
release use `## [vX.Y.Z] - YYYY-MM-DD - <title>`. Capture the local release
date once for the transaction and reuse it in the changelog and annotation.
Remove duplicate target-version sections and label groups without dropping
historical entries. Existing tagged releases retain their dates; rerunning
must not date them with today's date. Handle older unprefixed `X.Y.Z` tags
when resolving release ranges, while newly created tags always use `vX.Y.Z`.

Item 4 rechecks its own header, template and postprocessing against the
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
a one-hash difference. `init.bat` configures a `filter.changelog` clean filter
meant to strip the hash when the file is staged, but no `.gitattributes` maps
`CHANGELOG.md` to it, so it never runs: llm-shared's history holds the hashes
(for example in `8142624`).

The engine writes no hash: the unreleased heading ends at the title.

```text
## [v0.12.0-SNAPSHOT unreleased] Resume Where You Filed It
```

A regeneration then changes `CHANGELOG.md` only when its content changes, with
no git config or filter to install in each clone. The engine never sets
`filter.changelog`. The parity run against dev_workflow compares that heading
without its hash suffix.

## Stable-tag ranges and snapshot markers in changelogs

### The snapshot-marker problem in dev_workflow

A release's changelog lists every commit since the previous real release.
dev_workflow finds that previous release by asking Git for a tag, and every
tag counts. But not every tag is a release: my-project also puts snapshot tags
such as `v0.14.0-SNAPSHOT` on its integration builds. Such a tag is a marker,
meaning "a build was made here", not "this version was released".

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

### How changelog ranges treat snapshot markers

Snapshot tags are development markers, never release boundaries. Only a
complete stable tag, `vX.Y.Z` or the legacy `X.Y.Z`, ends a range, following
the shared selector of item 2. Configure git-cliff's release tags with that
complete stable-tag rule and pass the selected range; ignoring a snapshot
boundary must retain commits on both sides, not skip their changelog content.
Never exclude a marker through `skip_tags`, which drops its commits. With no
eligible stable tag, use the full relevant history.

In the example, preparing `0.14.0` includes A and B from `v0.13.0..HEAD`, even
when HEAD itself has the snapshot tag, and no `v0.14.0-SNAPSHOT` section is
released. Later, the `v0.15.0` section starts at `v0.14.0` and lists C and D
only.

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

Keep `CHANGELOG.md` at the repository root for the current snapshot and recent
stable releases. `.release.ini` defines the recent lower bound and any number
of inclusive archive ranges, each stored as
`docs/CHANGELOG.vA.B.C-vD.E.F.md`. Without ranges, the default remains a single
root file. The example above puts releases `0.1.0` through `0.13.9` in the
named archive and stable releases from `0.14.0` onward in the root file.

Compare version triples numerically, never as strings; do not infer ranges
from current file sizes or silently choose new boundaries. Each stable release
section must have exactly one destination. Reject overlapping ranges, reversed
bounds, an uncovered existing release, paths outside `docs/`, and filename
bounds inconsistent with config. Gaps containing no releases are allowed, but
become errors if a newly encountered release would have no destination.
Snapshot sections always stay in root. Add relative links to archives in root
and links back to root in archives, preserving release titles, dates and
section content.

Authors can change the bounds whenever they choose. In generated mode, the next
`changelog` run previews the affected files and repartitions complete sections
according to the new config, preserving released section bodies and historical
notes. Apply each rule once to content being generated; existing released
sections remain unchanged during ordinary rendering. Assemble and validate
the whole result before replacing any file. Writes cover root, new or changed
archives, and any obsolete engine-owned archive removed after its sections and
links are moved; never remove unrelated files. Repeated runs with unchanged
inputs are identical.

Two more checks make every move provable (added at the child-draft review,
2026-11-23):

- completeness: after any move, the set of released sections across the root
  file and every archive equals the set before the move, each section byte
  for byte identical, apart from an explicit historical revision; otherwise no
  file is written;
- order: release sections stay sorted newest first, by numeric version, in the
  root file and in every archive. The order of the `[changelog-archive:...]`
  sections inside `.release.ini` does not matter.

Gaps are checked against existing releases, not against version numbers: no
version follows `0.13.9` directly, since `0.13.10` and later are valid
versions. With `to = 0.13.9` and `recent-from = 0.14.0`, the gap is accepted
while no such release exists, and the run stops naming the first release that
falls in it. A new release cannot land in an old gap, since a target version
must be higher than every eligible stable release (confirmed answer Q2 A).

In curated mode the same range policy is checked but files and links remain
author-maintained. Report misplaced or duplicate sections with their expected
destination. Do not silently generate, rewrite or archive curated prose.

### Authority of released changelog sections

Existing released sections are authoritative during ordinary generated-mode
rendering (confirmed answer Q3 A). Changed fix rules do not automatically
rewrite released history; historical revisions require an explicit action.
Moving a section between root and archives or between archives preserves its
body. Any intentional historical revision must retain editorial notes and be
visible in the proposed changed set. Conflicting sources must be reported
rather than silently resolved. The explicit revision action, content
representation, comparison and regeneration mechanisms remain design work.

## Changelog fix rules without Perl

Today `.changelog.fixes` has two forms, both run by Perl:

- the `# PERL_CODE` form, a Perl fragment of `push @patterns, qr/.../;` and
  `push @replacements, '"..."';` pairs pasted into
  `update-changelog.fixes.tpl.pl`, then applied to the whole changelog with
  `s/$pattern/$replacement/gee`;
- a legacy `regex => replacement` line form, which the bash script turns into
  the same Perl pairs.

The three existing files (llm-shared, my-project, and the template) use only
the `push` pairs: 2 rules in llm-shared, 32 in my-project, typo fixes, empty
old release headings filled in, and backticks added around identifiers. Their
patterns use lookbehinds, `\S`, `[\r\n]`, `\s*?` and non-capturing groups,
all of which Python's `re` reads the same way. Their replacements are Perl
double-quoted strings holding `$1` or `\1` and `\n`, which map to a Python
`re.sub` template (`\1`, `\n`).

So a Python runner can replace Perl completely:

- the three built-in rules of the Perl template (wrap bare URLs in angle
  brackets, drop a single trailing space, turn a leading asterisk list marker
  into a dash) become built-in Python rules, applied first;
- project rules move to `.changelog-fixes.toml`, a declarative file with one
  pattern and one replacement per rule:

  ```toml
  [[rule]]
  pattern = ' _main '
  replace = ' `_main` '

  [[rule]]
  pattern = '\[v4\.1\.0\] -\s*?[\r\n]'
  replace = '[v4.1.0] - New doc created instead of rereading inputPDF\n'

  [[rule]]
  pattern = '(?<!`)__init__\.py'
  replace = '`__init__.py`'
  ```

- `fixes <root> convert` writes `.changelog-fixes.toml` from an existing
  `.changelog.fixes`, reading only the `push` pairs and the `=>` lines. Any
  other Perl statement stops the conversion and names its line, rather than
  guessing;
- `fixes <root> init` creates `.changelog-fixes.toml` when it is missing: by
  conversion when a `.changelog.fixes` exists, otherwise from a commented
  starter template in llm-shared `templates/` (replacing dev_workflow's
  `templates/.changelog.tpl.fixes`);
- `uc`, `uvf` and `/prepare-release` Steps 10 and 11 run that `init`
  automatically before rendering, so the new file appears in the working tree
  and lands in the prepare commit; item 7 wires the `/prepare-release` steps
  and their Step 13 staging;
- `brel` never creates the file: a new untracked file would make the tree
  dirty mid-release, outside the release commit. When the TOML is missing,
  `brel` uses the transition reader instead, reading the same subset of
  `.changelog.fixes` in memory, and prints a notice that the next
  `/prepare-release` will convert it automatically;
- once `.changelog-fixes.toml` exists, it is the only rule file read; a
  `.changelog.fixes` still present beside it gets a one-line warning that it is
  ignored and can be deleted;
- `fixes <root> dry-run` lists, per rule, how many matches it made, replacing
  the `CHANGELOG_DBG` output of the Perl script.

A rule whose pattern does not compile in Python fails the run with the rule
number and the `re` error. Today, a failing Perl run only prints "some rules
may have failed": `update-changelog.sh` then discards the Perl output and still
writes the changelog with none of the rules applied (lines 224 to 248).

## Operations that need git-cliff for changelog work

`uc`/`uvf` and release-note preparation perform the git-cliff preflight before
automatic `fixes init`, so a missing tool cannot leave a newly created rule
file behind. Release preprocessing uses the transition reader and never
creates that file mid-release.

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

Render, inject, clean, label, fix and validate in memory or unique artifact
files, then replace the root changelog and affected archives only after every
phase succeeds. Missing headers, invalid config or rules, git-cliff failure
and invalid output leave the previous changelog intact. Expose the exact
write and delete set, so preparation and release recovery (item 5) can restore
it.

Today `update-changelog.sh` writes `CHANGELOG.tmp.md`, `CHANGELOG.new.md`,
`CHANGELOG.cleaned.md`, `CHANGELOG.labeled.md`, `version.tmp.txt`,
`.fixes_content.tmp` and `tmp_fixes.pl` at the project root. The Python engine
keeps most of those steps in memory; a file that remains, such as the git-cliff
output, goes to the project artifact home, following
[`rules/artifact_files.md`](../../rules/artifact_files.md). Consumer scratch
files never go into the tooling checkout.

Approved release-project-root design decision Q06 A uses common Python
functions to check destinations and perform managed writes: changelog
functions prepare content and ask those functions to check the destination and
write `CHANGELOG.md`. A junction can redirect a destination after initial
validation, so the common functions recheck physical containment and
repository boundaries before preparing artifacts or writing. Read-only
resolution creates no artifact directory.

## Decisions inherited for changelog management

| # | Topic | Decision |
| --- | --- | --- |
| 2 | Fix-rules file | Preparation automatically converts legacy `.changelog.fixes` when TOML is missing; `convert` is an optional maintenance command; direct brel can use the in-memory transition reader |
| 10 | Snapshot hash noise | No hash in the unreleased heading; `filter.changelog` dropped |
| 22 | Changelog modes | Generated means commit-derived text with notes/date/fixes; curated means author-maintained bytes validated for exact headings/ranges, with no git-cliff/header dependency |
| 26 | Snapshot tags | Development markers, never stable release baselines, release menu choices or recovery targets; share classification across engine, changelog, notes and release-plan readers |
| 27 | Changelog archives | Root holds recent releases/current snapshot; explicit mutable numeric ranges assign older sections to `docs/CHANGELOG.vA.B.C-vD.E.F.md`; reject overlap/loss/duplicates; preserve curated prose |
| 38 | Historical changelog authority | Preserve existing released generated sections during ordinary rendering; changed rules do not rewrite history automatically. Revisions require an explicit action, preserve editorial notes and expose conflicts/changes; archive moves preserve bodies and curated bytes remain unchanged (Q3 A) |

## Consumer inputs for changelog management

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
  range search must not trip on the older unprefixed tags.
