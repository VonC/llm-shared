# The Release Desk Next Door

- Type: feature-request (several topics, see the candidate split at the end)

## Why this effort exists

Version and changelog management (`version.txt`, `CHANGELOG.md`, the
`-SNAPSHOT` to release switch, the annotated `vX.Y.Z` tag and its `[valid]`
marker) lives today in [`senv_dev_workflow`](https://github.com/VonC/senv_dev_workflow),
mounted as a `tools/dev_workflow` submodule in each project that wants `brel`.

That model has three costs:

- every consumer carries a pinned copy (llm-shared pins `f90bfc6`, my-project
  pins `5720c4b`: they already differ, only by the `uv`/`uver` alias rename);
- the submodule brings two nested submodules (`batcolors` on `legacy`,
  `shcolors` on `linux`), which my-project's Linux deployment then has to
  initialize on every host;
- a repository without the submodule gets nothing: workspace-halo has
  `version.txt`, `CHANGELOG.md` and `vX.Y.Z` tags, but its release commits say
  "this repository has no brel step" (`7ed242e chore(release): set version
  0.0.24`), so the `-SNAPSHOT` drop was done by hand.

Meanwhile every one of those repositories already expects `..\llm-shared` as a
sibling: my-project's `senv.bat` loads `..\llm-shared\senv.doskey`, and
workspace-halo's `senv.bat` resolves `..\llm-shared` for `pwiki`. llm-shared
already carries `tools/batcolors` as a submodule.

The goal: absorb the version and changelog features of `dev_workflow` into
llm-shared, so that `b` / `br` / `brel` work in any repository simply because
`..\llm-shared` sits beside it, with a clear warning when it does not. Then
remove the `tools/dev_workflow` submodule from llm-shared and my-project, and
give workspace-halo the same release flow without adding anything but a few
lines to its `build.bat`. Once the engine exists, `/prepare-release` can also
offer to tag the release itself, instead of always stopping before `brel`.

## Settled so far

- The engine is a Python rewrite behind a batch launcher, not a port of the
  batch and bash scripts (see "Engine in Python").
- `git-cliff` stays an external tool, installed by the global `senv` (not a
  project one) under `%PRGS%\git-cliffs\current`, reached through the
  `gcliff` alias and deliberately kept off `PATH`.
- Per-project settings live in a small `.release.ini` at the project root.
- Project fix rules move to `.changelog-fixes.toml`, created from an existing
  `.changelog.fixes` when missing, with a `convert` command and a transition
  reader.
- `/prepare-release` offers an optional `tag the release` step at the end of
  every mode when the project supports it, but never while an umbrella still
  has an unfinished topic. Feature mode keeps merging back to the integration
  branch without a tag, and offers three choices only after an exhausted
  umbrella or a standalone feature.
- Version-source formats are registered in an explicit tuple in
  `tools/release_workflow/sources/__init__.py`, with a test that fails when a
  module of the package is missing from it.
- The unreleased changelog heading carries no commit hash, and
  `filter.changelog` is dropped.
- `pyproject.toml` and `uv.lock` state plain `X.Y.Z` during the snapshot, as
  Step 12 does today.
- llm-shared is found as `%~dp0..\llm-shared` first, with a valid
  `LLM_SHARED_DIR` as fallback.
- The release tag message records the llm-shared `git describe`.
- my-project's `tools\batcolors` and `tools\shcolors` become junctions to the
  sibling, created by `senv`.
- This effort covers the llm-shared engine, the `/prepare-release`
  integration and llm-shared's own migration. my-project and workspace-halo
  are tracked as efforts in their own repositories; their sections below stay
  as input for those efforts.
- llm-shared's Diataxis pages document the migration. `senv_dev_workflow` is
  archived at the end of the my-project effort, with a short README pointing
  to those pages.

## What dev_workflow provides today

About 2,600 lines, most of it Windows batch calling Git Bash tools (`bash`,
`sed`, `awk`, `perl`, `cygpath`) and `git-cliff`.

| Piece | Role today | Proposed fate |
| --- | --- | --- |
| `init.bat` | Checks nested submodules, junctions `batcolors` into the parent `tools\`, requires `PRJ_DIR`, `PRJ_DIR_NAME` and `changelog-header.md`, sets `filter.changelog`, defines doskey aliases, exports path variables | Removed; each duty moves, see the next section |
| `get-version.bat` | Parses `version.txt` line 1 into `project_version`, `project_title`, `project_release_notes`; writes `0.1.0-SNAPSHOT` when the file is missing | Engine `version` command |
| `update-version.bat` (580 lines) | Snapshot/release state machine: git describe, dirty filter, next-snapshot prompt (fix/minor/major), title and description prompts, release commit, annotated tag | Engine core |
| `t_build.bat` | `:pre-processing` parses `rel`, `snap`, `rel_title...`, `prj_error` and calls update-version; `:post-processing` marks the tag `[valid]` or cancels the release (`reset @~1`, `tag -d`) | Engine `pre` and `post` commands |
| `update-changelog.bat` + `.sh` | git-cliff run, sed clean-ups, `version.txt` body injected under the unreleased heading, header prepended, section labeling, `.changelog.fixes` | Engine `changelog` command, git-cliff kept, sed dropped |
| `cliff.toml` | Commit groups, skipped release chores | Moves to llm-shared as the default, a project `cliff.toml` overrides it |
| `changelog_duplicate_version_section_remover.awk`, `changelog_section_labeler.awk` | Changelog post-processing | Rewritten in Python, awk dropped |
| `update-changelog.fixes.tpl.pl` | Runs `.changelog.fixes` through Perl `s///gee` | Replaced by a Python rules runner, Perl dropped (see "Changelog fixes without Perl") |
| `git/dirty-status-filter.pl`, `git/exempt-files.txt` | Dirty check that ignores release files plus a project `.exempt-files` | Rewritten in Python, Perl dropped |
| `t_build_maven.bat`, `mvn_get_version.ps1` | `pom.xml` get, set, check-snapshot | Maven version-source plugin |
| `t_build_npm.bat` | `package.json` get, set, check-snapshot | npm version-source plugin |
| `git/update-tag-message.*`, `git/release_reader.awk` | Rewrites a tag message from a file | Its `source "../../src/echos/echos"` does not resolve: port only if still used |
| `git/git_config.bat` | Adds a git config key if missing | Not called by anything in the three repositories: drop |
| `get_date.sh`, `get_day_index.ps1` | Date helpers | Not called: drop |
| `templates/*.tpl.*` | Project scaffolding (`senv`, `init`, `build`, `all`, `run`, `senv.local`, changelog header, fixes) | `init.tpl.bat` dropped; a new `build` snippet and the header template move to llm-shared `templates/` |
| `batcolors/`, `shcolors/` | Nested submodules for colored echos | llm-shared `tools/batcolors` (exists), plus a new `tools/shcolors` submodule on the `linux` branch of the same repository |

After the rewrite, the engine needs only `git` and `git-cliff`: no `bash`,
`sed`, `awk`, `perl` or `cygpath`.

## Where each init.bat duty goes

The aim is that no project needs an `init.bat` at all.

| Duty in `init.bat` | New home |
| --- | --- |
| `chcp 65001` | The llm-shared release launcher, around its own run |
| `batcolors` junction into the parent `tools\` | Gone: llm-shared scripts load `%LLM_SHARED_DIR%\tools\batcolors`; see my-project below for its own scripts |
| `PRJ_DIR` / `PRJ_DIR_NAME` required | The engine receives the project root as an argument from the project `build.bat` (`%~dp0`), and derives the name itself |
| `changelog-header.md` required | Checked only by the `changelog` command, and only in generated-changelog mode |
| `filter.changelog` git config | Written in all three repositories' `.git/config`, but no `.gitattributes` maps `CHANGELOG.md` to it: dead today. Dropped, since the heading it was meant to clean no longer carries a hash (see "No hash in the snapshot changelog heading") |
| Aliases `b`, `brel`, `br`, `crel`, `gv`, `uc`, `uver`, `uverr`, `uvf` | llm-shared `senv.doskey`, pointing at llm-shared launchers |
| Aliases `a`, `t`, `s`, `i`, `p`, `d`, `r`, `senv`, `lsenv`, `usenv`, `psenv`, `hsenv`, `hlsenv`, `psenve`, `cdp`, `fsenv` | Stay with each project `senv.bat` (workspace-halo already defines its own `i`, `cdp`, `fsenv`) |
| `VERSION_TXT_FILE`, `POM_FILE`, `PACKAGE_JSON_FILE`, `HEADER_CHANGELOG_FILE`, `DEV_WORKFLOW_DIR`, `PRJ_DIR_unix` | Computed inside the engine from the project root; no environment variable to export |
| `local_path` / `local_path_msg` | Computed and never read: drop |

### PRJ_DIR without init.bat

Every project `senv.bat` already sets `PRJ_DIR` and `PRJ_DIR_NAME` from its own
`%~dp0` (llm-shared, my-project and workspace-halo all do), so nothing is lost
when `init.bat` stops checking them.

The engine should still not trust `PRJ_DIR` as its source of truth. `PRJ_DIR` is
console-global, and the doskey aliases expand it when they run: after
`senv` in llm-shared, a `cd ..\workspace-halo` followed by `brel` runs
`llm-shared\build.bat rel` today. Two rules close that hole:

1. The project `build.bat` passes its own directory to the engine; the engine
   works on that root only, with every git call as `git -C <root>`.
2. The `brel` / `br` / `b` aliases call an llm-shared launcher that finds the
   project from the current directory (`git rev-parse --show-toplevel`), calls
   that project's `build.bat`, and warns when `PRJ_DIR` names another tree.

The same rule fixes `update-changelog.sh`, which runs some git commands in the
current directory instead of `PRJ_DIR` (`git show-ref`, `git cat-file`,
`git tag --sort` at lines 24 and 25, `git describe --exact-match` at line 49).
That only works today because the script is always started from inside the
project.

## Target shape in llm-shared

### Engine and launchers

- `tools/release_workflow/` (working name): the version, release and changelog
  logic, with tests under `tests/`, like the other llm-shared tools.
- `bin/release_workflow.bat`: the launcher. It locates llm-shared from its own
  path and uses the bundled venv Python, the way `bin/mds.ps1` already does for
  `pwiki`, so workspace-halo (a Node and Go project, no Python on `PATH`) can
  call it.
- Commands: `pre <root> [build args]`, `post <root> <build status>`,
  `version <root>`, `changelog <root> [latest|vX.Y.Z]`, `snapshot <root>`,
  `versions <root> list|set <version>|check`,
  `fixes <root> init|convert|dry-run`.
- Every command that can prompt (dirty tree, next snapshot, release title)
  also takes a non-interactive form that fails with a message instead of
  asking, so `/prepare-release` can drive it from its own menus.
- `pre` must hand variables back to the calling `build.bat` (`project_version`,
  `project_title`, `build_params`, `build_params_echos`, `build_must_fail`,
  `PRJ_REL_TITLE`). A Python process cannot set its parent's environment, so the
  engine writes `set` lines to `a.release.env.bat` in the project artifact home
  (`.reviews`), and the launcher calls then deletes it.

### Finding git-cliff

`git-cliff` is installed by the global `senv`, under
`%PRGS%\git-cliffs\current\git-cliff.exe`, and reached through the `gcliff`
alias (`gcliff=%PRGS%\git-cliffs\current\git-cliff.exe $*`). It is deliberately
not on `PATH`, and a doskey alias does not resolve from a Python subprocess, so
the engine looks for the executable itself, in this order:

1. a `GIT_CLIFF` environment variable naming the executable, for an unusual
   install;
2. `%PRGS%\git-cliffs\current\git-cliff.exe`;
3. `git-cliff` on `PATH`, for a machine without the global `senv`.

When none is found, the `changelog` command stops before writing anything, and
says what to run: `dwl gcliff` then `inst gcliff` in a global-`senv` console.
Commands that do not render a changelog (`version`, `versions`, `snapshot`,
and `pre` in curated-changelog mode) never look for it.

### Project build.bat contract

The whole integration a project needs, `%~dp0` being the project root. The
sibling `..\llm-shared` wins; an `LLM_SHARED_DIR` already set in the console
is used only when the sibling is missing and it holds the launcher:

```bat
set "release_workflow="
for %%i in ("%~dp0..\llm-shared") do (
  if exist "%%~fi\bin\release_workflow.bat" set "LLM_SHARED_DIR=%%~fi"
)
if exist "%LLM_SHARED_DIR%\bin\release_workflow.bat" (
  set "release_workflow=%LLM_SHARED_DIR%\bin\release_workflow.bat"
)
if not defined release_workflow (
  echo WARNING: no ..\llm-shared found: no version or changelog management.
  if /i "%~1"=="rel" ( echo FATAL: brel needs ..\llm-shared & exit /b 2 )
)
if defined release_workflow call "%release_workflow%" pre "%~dp0." %*
rem ... the project's own build (pytest, npm, mvn) ...
if defined release_workflow call "%release_workflow%" post "%~dp0." %build_status%
```

### Temporary files move out of the tooling tree

With one shared copy of the tooling, nothing may be written inside it: two
projects releasing at once would share the same files. Today:

- `update-version.bat` writes `dirty_files.tmp`, `dirty_ignored_files.tmp` and
  `run_filter.cmd` into `tools/dev_workflow/git/`;
- `t_build.bat` writes `temp_tag_message.txt` into `tools/dev_workflow/` (a
  leftover copy sits untracked in llm-shared's checkout right now);
- `update-changelog.sh` writes `CHANGELOG.tmp.md`, `CHANGELOG.new.md`,
  `CHANGELOG.cleaned.md`, `CHANGELOG.labeled.md`, `version.tmp.txt`,
  `.fixes_content.tmp` and `tmp_fixes.pl` at the project root.

The Python engine keeps most of those steps in memory. The files that remain
(the git-cliff output, the tag message, the `pre` handoff) go to the project
artifact home, following [`rules/artifact_files.md`](../rules/artifact_files.md).

### Per-project settings in .release.ini

Existing project files keep their meaning: `version.txt`, `CHANGELOG.md`,
`changelog-header.md`, `.exempt-files`. New ones, only where a project needs
to differ from the defaults:

- a project `cliff.toml` overriding llm-shared's default one;
- `.changelog-fixes.toml`, the fix rules (see "Changelog fixes without Perl");
- `.release.ini` at the project root, same idea as `.review-artifacts.ini`,
  for everything else. A project without it gets every default.

```ini
[changelog]
; generated (git-cliff, the default) or curated (never rewritten)
mode = curated

[source:npm]
; override the default form of a built-in format
form = release-only

[source:cicd-env]
; a project-specific file, one regex group holding the version
file = cicd/config/.env
pattern = ^APP_SERVICE_VERSION=(.+)$
form = snapshot
```

In `curated` mode the engine never rewrites `CHANGELOG.md`: it only checks that
a section for the release exists. The file is read with interpolation off, so
`%` and `$` in a pattern need no escaping.

### No hash in the snapshot changelog heading

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
`filter.changelog`, and the migration removes it from existing clones
(`git config --remove-section filter.changelog`). The parity run against
dev_workflow compares that heading without its hash suffix.

## Changelog fixes without Perl

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
  into a dash) become
  built-in Python rules, applied first;
- project rules move to `.changelog-fixes.toml`, a declarative file with one
  pattern and one replacement per rule:

cSpell: disable

  ```toml
  [[rule]]
  pattern = 'sumary'
  replace = 'summary'

  [[rule]]
  pattern = '\[v4\.1\.0\] -\s*?[\r\n]'
  replace = '[v4.1.0] - New doc created instead of rereading inputPDF\n'

  [[rule]]
  pattern = '(?<!`)__init__\.py'
  replace = '`__init__.py`'
  ```

cSpell: enable

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
  and lands in the prepare commit (Step 13 stages it with the other release
  files);
- `brel` never creates the file: a new untracked file would make the tree
  dirty mid-release, outside the release commit. When the TOML is missing,
  `brel` uses the transition reader instead, reading the same subset of
  `.changelog.fixes` in memory, and prints a one-line reminder to run
  `fixes init`;
- once `.changelog-fixes.toml` exists, it is the only rule file read; a
  `.changelog.fixes` still present beside it gets a one-line warning that it is
  ignored and can be deleted;
- `fixes <root> dry-run` lists, per rule, how many matches it made, replacing
  the `CHANGELOG_DBG` output of the Perl script.

A rule whose pattern does not compile in Python fails the run with the rule
number and the `re` error, instead of Perl's "some rules may have failed"
warning that lets the changelog through half-fixed.

`/prepare-release` Step 11 then reads "the fix rules" instead of "the Perl
find/replace rules", and `prepare_release_notes` needs no change beyond the
engine call.

## Version sources as plugins

A version lives in more places than `version.txt`. dev_workflow knows two
(`pom.xml`, `package.json`). `/prepare-release` Step 12 already describes more,
each in its own form: `pyproject.toml` and `uv.lock` without the suffix,
`package.json` and `package-lock.json` in the release form (a VS Code
extension version supports only `major.minor.patch` on the Marketplace), Maven
POMs and their module parents with `-SNAPSHOT`, and a `cicd/config/.env`
variable. my-project's `tools/set_version.py` and `tools/check_versions.py`
implement that list for one repository. The engine should implement it once,
for every repository, and leave room for formats nobody needs yet.

### One module per format

Each format is one module in the `tools/release_workflow/sources/` package
(`maven.py`, `npm.py`, `pyproject.py`, ...), exposing one object that follows
a small protocol:

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
  lists each format object in one explicit tuple. Adding a format is one module
  and one line in that tuple. The tuple order decides which format claims a
  file first, and pyright and vulture see every format in use. A test lists the
  modules of the package and fails when one is missing from the tuple, so a
  new format cannot be written and then silently left out;
- which files a project holds: each format's `detect` looks for its own files
  under the project root, automatically, so a project gains a format's support
  the day llm-shared ships it, with nothing to declare.

A project-local format (a Python file named in `.release.ini`) could later let
a repository add its own format without touching llm-shared, on top of the
tuple.

`versions <root> list` prints each detected file with its kind and current
value, so a user sees what a release will touch before it does.

Detection skips `node_modules`, `venvs`, `.venv`, `.git`, `.reviews` and
`target`, and a format can walk further from its root file: the Maven plugin
reads the `<modules>` of the root POM and updates each module's `<parent>`
version.

### Forms, and the anchor

`version.txt` is the anchor: every other source takes its value from the first
word of `version.txt`, never from its own current value. Each format then
chooses its form:

| Form | Snapshot `1.2.3-SNAPSHOT` becomes | Release `1.2.3` becomes | Used by default for |
| --- | --- | --- | --- |
| `snapshot` | `1.2.3-SNAPSHOT` | `1.2.3` | Maven POMs, the `.env` variable |
| `core` | `1.2.3` | `1.2.3` | `pyproject.toml`, `uv.lock` |
| `release-only` | `1.2.3` | `1.2.3` | `package.json`, `package-lock.json` |

`core` and `release-only` give the same strings. They differ in their
guard: a `release-only` source refuses a value lower than the one it states
already, since lowering a published extension version would rewind it, as Step
12 of `/prepare-release` already requires.

### First set, and the next ones

- First set, because the three repositories and Step 12 need them:
  `version.txt`, `pyproject.toml` (`[project].version`), `uv.lock` (the
  virtual root package), `package.json` with `package-lock.json` (the top-level
  `version` and `packages[""].version`, no dependency entry touched), Maven
  `pom.xml` with its module parents.
- A generic `pattern` source, declared by a project, for the one-off files:
  a path, a regular expression with one group, and a form. my-project's
  `cicd/config/.env` becomes one line of project configuration, instead of a
  case every repository's release carries.
- Later, as a repository needs them, each one module: `Cargo.toml`,
  `gradle.properties` and `build.gradle(.kts)`, `*.csproj` or
  `Directory.Build.props`, Helm `Chart.yaml` (`version` and `appVersion`),
  `composer.json`, `pubspec.yaml`, `mix.exs`, a `__version__` in a Python
  package `__init__.py`.

A format that also needs its own tool to regenerate a lock file (`uv lock`
after `pyproject.toml`) runs it only through its plugin, and only when the
tool is present; otherwise it edits the lock file entry directly and says so.

### What uses it

- `brel` (`pre`, release mode): drops the suffix from every source in its
  form, then includes each rewritten file in the release commit.
- The next-snapshot step after a release: raises every source to the chosen
  `X.Y.Z-SNAPSHOT` in its form, in the same commit as `version.txt`.
- `/prepare-release` Step 12: `versions <root> set X.Y.Z-SNAPSHOT` then
  `versions <root> check`, in place of the per-format instructions it carries
  today.
- A project `check.bat`: `versions <root> check`, in place of a project
  `check_versions.py`.

## Integration with /prepare-release

### What /prepare-release does today

Steps 9 to 13 set `version.txt` to `X.Y.Z-SNAPSHOT`, call
`prepare_release_notes` (which runs `tools\dev_workflow\update-changelog.bat`),
pause for review and regenerate the changelog with the same script (Step 11),
update the other version sources by hand or through `tools/set_version.py`
(Step 12), and make one `chore(release): prepare for vX.Y.Z release` commit
(Step 13). Step 14 checks the tree is clean, reports, and tells the user to
run `brel`. The instruction states it "never creates the git tag".

In feature mode, when the umbrella has another unfinished item, the run stops
after the merge with a `process-draft` handoff. When the umbrella is exhausted,
or the feature is standalone, it goes on through the full release path with no
choice.

### What changes in every run

- Step 10 and Step 11 call the engine `changelog` command instead of
  `tools\dev_workflow\update-changelog.bat`.
- Step 12 calls `versions set` and `versions check` (see above) instead of
  describing each format.
- Step 13 also stages `.changelog-fixes.toml` when Step 10 or Step 11 created
  or changed it.
- The "Boundary with brel" section names the llm-shared launcher instead of
  `tools\dev_workflow\update-version.bat`.

### A new optional release step

After the Step 14 clean-tree gate and report, the run can offer to tag the
release itself, as a last and optional step. "Tag" names what the user
cannot easily take back: the step builds too, but the annotated `vX.Y.Z` tag
is its lasting result.

- `Stop here`: today's end. The user reviews everything and runs `brel` when
  ready.
- `Go ahead, and tag the release`: run the project `build.bat rel` through
  the llm-shared launcher, in its non-interactive form. That drops `-SNAPSHOT`
  from `version.txt` and every version source, regenerates `CHANGELOG.md` with
  the dated release heading, makes the `chore(release): set new 'vX.Y.Z'`
  commit, creates the annotated `vX.Y.Z` tag from `version.txt`, runs the
  project build as the gate, then marks the tag `[valid]`. When the build
  fails, the engine's `post` step cancels the release (commit reset, tag
  deleted): the run reports that and stops, with the prepare commit still in
  place.

#### Where version.txt gets its content

The release step writes no release notes. By the time it runs, the same
`/prepare-release` run has already written them:

- Step 9 sets the first word to `X.Y.Z-SNAPSHOT`;
- Step 10 (`prepare_release_notes`) writes the summary (theme line, key
  changes, paragraphs), offers three title and subtitle pairs, and rewrites
  the first line to `X.Y.Z-SNAPSHOT -- <title>` once one is picked;
- Step 11 pauses for edits, regenerating the changelog when they change;
- Step 13 commits it in the prepare commit.

The release step then changes only the first word, `X.Y.Z-SNAPSHOT -- <title>`
becoming `X.Y.Z -- <title>`, and reuses the rest: the title goes into the
`## [vX.Y.Z] - <date> - <title>` changelog heading, the body goes under it,
and the whole file, with the date in place of the version, becomes the tag
message. No title prompt appears, since `version.txt` already carries one.
The next-snapshot prompts (fix, minor or major, new title, description) belong
to the next snapshot, after new commits, not to this step.

As a guard, the release refuses to start when the first line of `version.txt`
has no `--` separator followed by a title, or when no summary follows it,
which is what a `brel` run without `/prepare-release` first would otherwise
tag.

#### When the tag is never offered

The tag choice appears only when all of these hold:

- the run reached the prepare commit, which it never does while an umbrella
  collection still has an unfinished topic: those topics must first be
  implemented and merged back to the integration branch, and a tag at that
  point would name a release that is not complete;
- the project's `build.bat` carries the contract above, and `..\llm-shared`
  provides the launcher.

Otherwise the run ends as it does today. It never pushes the branch or the
tag. The "What this skill never
does" section changes from "never creates the git tag" to "never tags without
the explicit `tag the release` choice of the same run, and never pushes".

#### Recording the tooling version in the tag

A submodule pins the tooling commit; a sibling does not, so the release
records which llm-shared built it. The engine adds one trailer line to the
annotated tag message, after the `version.txt` content and before the
`[valid]` marker that `post` appends:

```text
Release tooling: llm-shared v0.13.0-4-gabc1234
```

The value is `git -C <llm-shared> describe --tags --long --dirty --always`.
It goes to the tag message only, never to `version.txt` or `CHANGELOG.md`, so
the release notes stay about the project.

Follow-up to remember: amend
`templates/prepare-release-notes.version-txt.template.txt` (and the
`prepare_release_notes` instruction that fills it) so the template shows where
that trailer sits in the final tag message, below the key changes, instead of
leaving it implicit in the engine.

### The feature-mode choice

Feature mode keeps its current merge-back behavior: merging a feature branch
back to its integration branch never needs, and never sets, a tag. The only
change is where the run used to continue on its own:

| Feature-mode situation | Today | Proposed |
| --- | --- | --- |
| Umbrella has another unfinished item | Merge back, `process-draft` handoff, stop | Unchanged: merge back to the umbrella integration branch, `process-draft` handoff, stop. No prepare choice and no tag choice is offered |
| Umbrella exhausted, or standalone feature | Merge back, then the full release path with no choice | Merge back, then a choice: `Stop after the merge` (no release artifacts, no tag), `Go ahead, and prepare the release` (through the prepare commit, stop before `brel`), or `Go ahead, prepare and tag the release` (the same, plus the release step above) |

On-main and integration modes have no merge-back to stop after, so they keep
today's path and only gain the optional release step at the end.

## When llm-shared is not beside the project

| Situation | `b` (build) | `brel` / `br` | `gv`, `uc`, `uver`, `uvf` |
| --- | --- | --- | --- |
| `..\llm-shared` present | Full flow | Full flow | Available |
| `..\llm-shared` missing | Builds, with one warning; the version shown is read from the first word of `version.txt` | Stops before any git change, with a warning naming the missing folder, non-zero exit | Not defined; `senv` says so once |
| `..\llm-shared` present but older than the project expects | Builds | Stops with both versions in the message | Available, with the same warning |
| `git-cliff` not found | Builds | Stops before the release commit when the changelog mode is `generated`, naming `dwl gcliff` / `inst gcliff` | `uc` fails with the same hint |

## Engine in Python

The Python rewrite was chosen over a straight port of the batch and bash: a
port would leave about 1,100 lines of untested batch outside llm-shared's
`ghog` coverage gate, bugs included. In Python, the snapshot and release state
machine becomes testable against temporary git repositories, Perl, awk, sed
and bash leave the dependency list, and the defects below get fixed instead of
copied.

The `dev_workflow` submodule stays in place until a parity run on llm-shared
itself produces the same `version.txt`, `CHANGELOG.md`, commit subjects and tag
message as the old scripts.

### Defects to fix rather than port

- `update-version.bat` lines 353 and 361, in `:restore-version`, use
  `%update_version_dir%` while the script defines `update-version_dir`: the
  POM and `package.json` restore calls resolve to `\t_build_maven.bat` and
  `\t_build_npm.bat` and never run.
- Lines 435 and 437 compare `"%git_tag%"==v"%version%"`: the quotes differ on
  each side, so the "already released" guards can never match, and both
  branches test the same condition.
- `t_build_npm.bat` line 89 rewrites every `"version": "..."` line of
  `package.json`, not only the top-level one, and leaves `package-lock.json`
  behind.
- The npm path requires `package.json` to carry `-SNAPSHOT` before a release
  (`check-snapshot`), the opposite of the release-only form a VS Code
  extension needs: workspace-halo's release would stop there.
- Every sub-script calls `"%PRJ_DIR%\senv.bat"` again (`t_build`,
  `update-version`, `update-changelog`, both adapters). The engine should never
  call the project `senv.bat`: the project `build.bat` already did.
- The `PRJ_DIR` and current-directory issues described above.

## Per-repository migration

### llm-shared itself

- `build.bat` switches from `tools\dev_workflow\t_build.bat` and
  `get-version.bat` to its own `bin\release_workflow.bat`. llm-shared is both
  the engine and a consumer: the release commit touches only `version.txt`,
  `CHANGELOG.md` and version sources, so a cancelled release (`reset @~1`)
  never rolls the engine back.
- `tools/init.bat` goes away; `senv.bat` exports the batcolors macros from
  `tools\batcolors` directly and stops clearing `INIT_DONE`.
- Add the `tools/shcolors` submodule (batcolors `linux` branch), remove the
  `tools/dev_workflow` submodule and its `.gitmodules` entry.
- Convert its `.changelog.fixes` (2 rules) with `fixes init`, and add a
  `.release.ini` only if a default does not fit.
- Update every reference to `tools\dev_workflow\update-changelog.bat`: the
  `prepare_release_notes` Step 5 in `instructions/prepare-release-notes.md` and
  its adapter copies, `instructions/prepare-release.md` (Steps 10 to 14 and the
  new release step), `DEVELOPMENT.md` (the "Dependency on the
  senv_dev_workflow build tooling" section), and the wiki pages that name it
  (`how-to/prepare-a-release.md`, `reference/aliases-and-launchers.md`,
  `reference/repository-layout.md`,
  `tutorials/05-prepare-a-release-from-develop.md`,
  `explanation/one-body-many-agents.md`).
- A new how-to page: "Give a sibling repository `brel`", with the
  `build.bat` snippet above.
- The migration itself, documented in the Diataxis wiki:
  - a how-to, "Move a project from the dev_workflow submodule to sibling
    llm-shared": the `build.bat` switch, `senv.bat` and `tools/init.bat`
    clean-up, junctions, `.changelog.fixes` conversion, `.release.ini`, then
    `git rm` of the submodule;
  - an explanation page on why a sibling replaced the submodule (pinning
    through the tag trailer, one copy of the tooling, no nested submodules);
  - the reference pages for the new launcher commands, `.release.ini` keys and
    `.changelog-fixes.toml` rules.
- The archive of
  [`senv_dev_workflow`](https://github.com/VonC/senv_dev_workflow) is not an
  llm-shared change: it closes the my-project effort, once my-project no
  longer uses the submodule. Its last README only points to the migration
  how-to above, then the repository gets the GitHub archive flag.

### my-project, for its own effort

- `build.bat`: same switch as llm-shared.
- `tools/init.bat` goes away, with the `INIT_DONE` handling in `senv.bat`
  (lines 51 to 62).
- `tools\batcolors` is today a junction into `tools\dev_workflow\batcolors`,
  and `senv.bat`, `build.bat`, `check.bat`, `run.bat` call
  `%PRJ_DIR%\tools\batcolors\echos.bat`. `senv` recreates it as a junction to
  `..\llm-shared\tools\batcolors`, and creates `tools\shcolors` the same way,
  to `..\llm-shared\tools\shcolors`: no script changes its path. `.gitignore`
  already holds `/tools/batcolors/` and gains `/tools/shcolors/`.
- The Linux side is the delicate part. `run`, `run_server`, `run_sentinel`,
  `kill_server` and `kill_sentinel` source
  `tools/dev_workflow/shcolors/echos`, and `.env` (lines 420 to 440) runs
  `git submodule update --init` for `tools/dev_workflow` and its nested
  submodules. Deployed hosts hold a my-project clone and no llm-shared, so no
  junction exists there. Those scripts source `tools/shcolors/echos` when the
  junction is present (a Windows development machine), and otherwise the
  tracked `tools/echos`, already an identical copy (same 67 lines). The `.env`
  bootstrap block goes away.
- `tools/deploy_pkgs.sh` documents a failure caused by the submodule recursion
  of `git status` on a host (`GIT_EXEC_PATH` workaround): that problem goes
  away with the submodule, the workaround can stay.
- Version sources: the built-in plugins cover `version.txt`, `pyproject.toml`,
  `uv.lock`, `pom.xml` and `PDF/pom.xml`; `cicd/config/.env` becomes one
  `pattern` source. `tools/set_version.py` and `tools/check_versions.py` can
  then retire, and `check.bat` calls `versions check`. Today only
  `version.txt` and `pom.xml` follow a `brel`, and `check.bat` catches the
  drift afterwards.
- Convert its `.changelog.fixes` (32 rules) with `fixes init`.
- Remove the `tools/dev_workflow` submodule.

### workspace-halo, for its own effort

It never had `dev_workflow`, so this is onboarding, not removal:

- `build.bat` gains the `pre` / `post` calls around its existing test gate and
  VSIX packaging; `senv.bat` loads llm-shared's `senv.doskey` (or only its
  release aliases) and warns when `..\llm-shared` is missing (today `pwiki`
  just fails).
- Its `CHANGELOG.md` is hand-written, marketplace style (`## 0.0.24` with
  user-facing bullets), and ships inside the VSIX. git-cliff output would
  replace it with commit subjects, so workspace-halo needs the `curated`
  changelog mode, with no `changelog-header.md`; it then never needs
  git-cliff either.
- `package.json` and `package-lock.json` use the `release-only` form: they
  stay at `0.0.24` while `version.txt` reads `0.0.25-SNAPSHOT`, and move to
  `0.0.25` at release.
- Its tags mix `0.0.21`, `0.0.22` and `v0.0.20`, `v0.0.23`, `v0.0.24`. The
  engine creates `vX.Y.Z`; the changelog range search must not trip on the
  older unprefixed tags.

## Decisions on the draft questions

Every question is settled; none remains open.

| # | Topic | Decision |
| --- | --- | --- |
| 1 | Per-project settings | `.release.ini` at the project root |
| 2 | Fix-rules file | `.changelog-fixes.toml`, `convert` command, transition reader, and `init` creating the TOML from `.changelog.fixes` when missing |
| 3 | Optional release step | Offered at the end of every mode when the project supports it, never while an umbrella has an unfinished topic |
| 4 | Feature-mode choice | Merge back without a tag always stays possible; after an exhausted umbrella or a standalone feature: `Stop after the merge`, `prepare the release`, `prepare and tag the release` |
| 5 | Format registration | Explicit tuple in `sources/__init__.py`, plus a test that fails when a module of the package is missing from it |
| 6 | `pyproject.toml` snapshot form | Plain `X.Y.Z`, as Step 12 does today |
| 7 | llm-shared discovery | `%~dp0..\llm-shared` first, a valid `LLM_SHARED_DIR` as fallback |
| 8 | Tooling pinning | llm-shared `git describe` as a tag-message trailer, plus the template follow-up |
| 9 | my-project color scripts | `tools\batcolors` and `tools\shcolors` junctions created by `senv` |
| 10 | Snapshot hash noise | No hash in the unreleased heading; `filter.changelog` dropped |
| 11 | Scope | llm-shared engine, `/prepare-release` integration, llm-shared migration; the other two repositories in their own efforts |
| 12 | `senv_dev_workflow` | llm-shared's Diataxis pages document the migration; the repository is archived at the end of the my-project effort, with a short README pointing to them |
| A | Word for the release choice | "tag": `Go ahead, and tag the release`, `Go ahead, prepare and tag the release` |

## Candidate split for split-and-define

Four items, in this order:

| # | Item | Needs |
| --- | --- | --- |
| 1 | `release-engine` | nothing |
| 2 | `version-sources` | 1 |
| 3 | `prepare-release-integration` | 1, 2 |
| 4 | `llm-shared-switch-over` | 1, 3 |

1. `release-engine`: `tools/release_workflow/`, `bin/release_workflow.bat`,
   the git-cliff lookup, the default `cliff.toml`, the hash-free unreleased
   heading, the `tools/shcolors` submodule, and the changelog fix rules (the
   built-in rules, `.changelog-fixes.toml`, the `init`, `convert` and
   `dry-run` commands, the transition reader), with tests and the parity run
   against `dev_workflow` on llm-shared. The fix rules belong here because the
   parity run cannot reproduce llm-shared's changelog without its 2 rules.
2. `version-sources`: the plugin protocol, the explicit format tuple and its
   completeness test, the first set of formats, the `pattern` source,
   `.release.ini` parsing, `versions list|set|check`. It stays separate: the
   parity run does not need it (dev_workflow never touches `pyproject.toml`),
   and its users are `/prepare-release` Step 12 and a project `check.bat`.
3. `prepare-release-integration`: engine calls in Steps 10 to 13, the
   optional tag step and the rules for when it is never offered, the
   feature-mode choice, the tag-message trailer, the `version.txt` template
   follow-up, and the adapter copies. It stays separate: it is an instruction
   change reviewed through contract tests, and it needs both items above.
4. `llm-shared-switch-over`: one cutover of llm-shared itself, so the aliases
   are never defined twice or not at all. `build.bat` and `senv.bat` on the
   engine, the `b`, `br`, `brel`, `crel`, `gv`, `uc`, `uver`, `uverr`, `uvf`
   aliases in `senv.doskey` (resolving the project from the current
   directory, with the missing-sibling warnings), `tools/init.bat` removal,
   `.changelog.fixes` conversion, `filter.changelog` removal, submodule
   removal, `DEVELOPMENT.md`, and the Diataxis pages: the "Give a sibling
   repository `brel`" and migration how-tos, the explanation page, the
   reference pages, and the `build.bat` template. It comes after item 3,
   because `/prepare-release` calls `tools\dev_workflow\update-changelog.bat`
   until item 3 lands.

Tracked outside this effort, in their own repositories: the my-project
migration and the workspace-halo onboarding. The `senv_dev_workflow` archive
is the last step of the my-project effort, since it can only happen once
my-project stops using the submodule. Its README then holds only a few lines
pointing to the llm-shared migration how-to written in item 4: the
documentation itself lives in llm-shared.
