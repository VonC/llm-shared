# Version sources

<img src="../assets/logo-llm-shared-trail-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

The release engine's `version` and `versions` commands read a project's
authoritative version, keep every participating version source in step with
it, and select release ranges from classified stable tags. They run through
the release launchers of
[Aliases and launchers](aliases-and-launchers.md#-release-foundation-launchers);
the statuses, streams and selector rules every release operation shares are in
[Automation and direct invocation](automation-and-direct-invocation.md#release-foundation-invocation).

## Invocation model

In this version, a person or a script calls these commands directly through a
release launcher; no workflow calls them on its own yet. The read commands are
safe at any time: they take no lock and write nothing. `versions set` changes
the project's version files, so call it only when you mean to change the
version, and review its result before committing. The build release lifecycle
and the release preparation of later items will call the same commands and the
same transition themselves.

## Commands

| Command | Effect | Lock, writes and Git |
| --- | --- | --- |
| `version` | prints the anchor's version, title and notes | no lock, no write, no Git call |
| `versions list` | lists each participating source, then each visible non-participating file | no lock, no write, one Git listing |
| `versions check` | compares each participating source with its expected value | no lock, no write, no Git call |
| `versions set <X.Y.Z or X.Y.Z-SNAPSHOT>` | updates the anchor and every participating source as one transition | the project operation lock, recovery evidence, one atomic replacement per changed file, no Git call |
| `versions range [<stable tag>]` | prints the release range ending at `HEAD` or at that tag | no lock, no write, at most four Git calls |

The operation tokens follow the command; the launcher options may sit before,
between or after them:

```text
release_workflow.bat versions set 0.14.0 --project-root C:\work\app
```

A missing, extra or malformed token fails with status 2 before any Git process
or file read. The read commands list the artifact home once and report every
leftover version-transition evidence directory as a warning on standard error.
No version command runs a build or lock tool, or git-cliff.

## Output on standard output

Data is UTF-8 with LF line endings; a record separates its fields with a tab.
Warnings and errors go to standard error.

| Command | Output |
| --- | --- |
| `version` | line 1 the version token, line 2 the title (possibly empty), line 3 empty, then the notes; a batch caller reads the version as the first line |
| `versions list` | the header `path field adapter form value status`, then one record per source: root-relative path with `/`, field, adapter, form, current value and status (`participating`, `not-participating tool-only` or `not-participating undeclared`); a non-participating record shows `-` for form and value |
| `versions check` | one record per participating source: path, field, form, actual value, expected value, `ok` or `drift` |
| `versions set` | one record per changed field: path, field, old value, new value, `version.txt` last; or the single line `unchanged` |
| `versions range` | the lines `target=`, `baseline=` (a tag or `none`), `range=` (a revision range Git accepts) and `commits=` |

A `range` reader runs `git log <range>`. A tag target keeps the caller's
spelling; the baseline is named by its `vX.Y.Z` alias when it has one.

## Statuses of the version commands

| Status | Meaning |
| --- | --- |
| `0` | success; `check` found no drift |
| `1` | execution failure: `check` drift, a lock held by another operation, recovery evidence that cannot be written, a failed write whose restoration completed, or a completed transition whose cleanup failed (the diagnostic states that the new versions are applied and names the residue) |
| `2` | invalid input or failed preflight: tokens, malformed anchor, invalid configuration, unsupported or ambiguous arrangement, overlapping claim, release-only refusal, rejected range target, conflicting or ambiguous tags, interrupted transition evidence |
| `3` | restoration incomplete: at least one source could not be restored; each one and the path of its retained original are named |

Status 3 is a stop that requires recovery, never an ordinary failure to retry.

## The anchor document

The project root's `version.txt` is the anchor. It is strict UTF-8; a
byte-order mark is kept. Its first line holds the version token, optionally
followed by whitespace, `--` and the title; the following lines are the notes.
A token is `MAJOR.MINOR.PATCH` with an optional uppercase `-SNAPSHOT`, decimal
numbers without leading zeros and no `v`. Versions compare by their numeric
core. `versions set` replaces only the token's bytes: the title, the notes,
the byte-order mark and every line ending stay. Other `version.txt` files are
not sources.

## Sources, forms and limits

| Adapter | Owned fields | Default form | Allowed forms |
| --- | --- | --- | --- |
| `anchor` | the project root's `version.txt` | `snapshot` | none to configure |
| `python` | `pyproject.toml` `[project] version`, and the root package version of its `uv.lock` | `core` | `core` |
| `npm` | `package.json` `version`, and the top-level `version` and `packages[""].version` of its `package-lock.json` | `release-only` | `release-only`, `core`, `snapshot` |
| `maven` | the reactor's project, internal parent, and literal internal dependency and dependency-management versions, through every declared module | `snapshot` | `snapshot` |
| pattern source | the one capture of a declared expression in a declared file | declared | `snapshot`, `core`, `release-only` |

A `snapshot` source expects the anchor token; a `core` or `release-only`
source expects its core, so `0.14.0-SNAPSHOT` gives `0.14.0`. A `release-only`
source whose value is higher than its expected value refuses `versions set`
and is `drift` for `versions check`.

Detection runs every adapter at the project root and at each declared
component root, probing fixed file names only. A `pyproject.toml` or
`package.json` without its own version is tool-only: it and its lock are listed
and never participate. An undeclared manifest file below the project with its
own version is listed as `not-participating undeclared` and never makes
`check` or `set` fail. Directories named `node_modules`, `venvs`, `.venv`,
`.git`, `target`, `vendor`, `sample`, `samples`, `example` or `examples`, and
nested repositories, are never candidates.

These arrangements fail every `list`, `check` and `set` with status 2 before
any write, naming the file and the remedy:

- a dynamic or missing Python project version, a `uv.lock` schema other than
  `version = 1` with `revision = 3` or `5`, a uv workspace, a shared workspace
  lock or a workspace reference;
- a `package-lock.json` format other than 2 or 3 (format 1: regenerate it with
  npm 7 or later), a `workspaces` field or an `npm-shrinkwrap.json`;
- a local link between participating components (`file:`, `link:`, a path or a
  `workspace:` specifier);
- a Maven property expression or range in a version field, except a whole
  internal dependency `${project.version}`, which stays unchanged, and a root
  POM with an external parent and no version of its own;
- a pattern that matches nothing, more than once or an empty value, and two
  claims on the same bytes, whoever makes them.

`versions set` never regenerates a lock or resolves dependencies.

## Configuration in .release.ini

```ini
[source:npm]
form = core

[source:cicd-env]
file = cicd/config/.env
pattern = ^APP_SERVICE_VERSION=(.+)$
form = snapshot

[component:api]
root = api
```

| Section | Keys | Rule |
| --- | --- | --- |
| `[source:python]`, `[source:npm]`, `[source:maven]` | `form` only | overrides that adapter's form at every participating root, within its allowed forms |
| `[source:<name>]`, any other name | `file`, `pattern` and `form`, all required | a pattern source: a file inside the project, an expression with exactly one capture group (compiled in multiline mode) and a form |
| `[component:<id>]` | `root`, required | a participating root: an existing directory below the project root, not the root itself, not under an excluded directory name, declared once |

`anchor` and `pattern` are reserved source names. An unknown section or key, an
invalid form or a missing required key fails every command, even `version`,
with status 2. Interpolation is off and the file is never executed. Without
version sections, built-in detection and default forms apply.

## Recovery evidence

Before its first overwrite, `versions set` writes a directory
`a.version-transition.<YYYYMMDDTHHMMSS+HHMM>-<pid>` (a taken name gets a `-2`,
`-3` suffix) in the project's artifact home, `.reviews` by default. It holds an
`original.<n>` copy of every participating file and a `manifest.json` with the
owner, the target, the state and each file's path and SHA-256. A successful
standalone transition deletes it.

| Evidence found | Next `versions set` | What a person does |
| --- | --- | --- |
| state `complete`, standalone | removes it with a warning | nothing |
| state `writing` (a stopped transition) | stops with status 2, naming it | compare each source with its copy, restore what is needed, then remove the directory |
| state `restoration-incomplete` | stops with status 2, naming it | restore each source the status 3 diagnostic named from its `original.<n>` copy, then remove the directory |
| unreadable manifest | stops with status 2, naming it | inspect the directory, restore what is needed, then remove it |
| owned by a release lifecycle | stops with status 2, naming it | leave it to that lifecycle |

This version has no automated recovery command.

## Release ranges for instruction-driven readers

`versions range` is the one release-range selector for changelog, release
notes and release-plan readers.

- `vX.Y.Z` and `X.Y.Z` are stable releases; a `-SNAPSHOT` tag in any case is a
  development marker, never a boundary or a target; other names are ignored.
- A lightweight tag, or an annotation without a `Release tooling: <value>`
  line, is a historical release and is eligible. That trailer as the last
  nonempty line marks an unvalidated engine release: it is excluded, with a
  warning, until a `[valid]` line follows it. Any other trailer arrangement is
  ambiguous and fails with status 2 when it lies in the selected range.
- `X.Y.Z` and `vX.Y.Z` on one commit are one release, judged by its most
  restrictive alias. One version on two commits, or two versions on one
  commit, are conflicting tags: status 2.
- The baseline is the latest eligible release reachable from the target. At
  `HEAD` it may be a release on `HEAD` itself, which gives an empty range; a
  tag target is never its own predecessor and must be an eligible stable tag.
  Without any eligible release, `baseline=none` and `range` is the target, the
  full history.

## Recorded tool versions

Each supported lock schema rests on evidence recorded with the real tool:
uv 0.13.4 for the `uv.lock` schemas `(1, 3)` and `(1, 5)` with virtual and
editable roots, and npm 10.8.3 on Node 22.9.0 for lock formats 2 and 3. The
records are in
`tests/unit/tools/release_workflow/test_version_lock_evidence/lock_evidence.v1.json`;
a test checks that the adapters still produce each recorded edited pair.
Another tool version, schema or layout is supported only once its evidence is
recorded.

Related: [Automation and direct invocation](automation-and-direct-invocation.md),
[Aliases and launchers](aliases-and-launchers.md).
