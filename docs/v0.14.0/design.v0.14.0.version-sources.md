# Design v0.14.0: authoritative project version sources

Reference feature request:
[feature-request.v0.14.0.version-sources.md](feature-request.v0.14.0.version-sources.md).

## Context for the version-sources design

Item 1 of the sibling release tooling umbrella shipped a release engine with
no operation: every command reports that it is unavailable. Item 2 adds the
first domain to that engine. It reads the authoritative version from
`version.txt`, finds every participating version source, gives each the form
its ecosystem expects and changes them all as one recoverable transition. It
also adds the shared stable and snapshot tag classifier and range selector that
items 4, 5 and 7 consume.

The requirement settles behavior through its fifteen requirement
clarifications. This design chooses the interfaces, the source model, the
write and restoration mechanism, the configuration syntax, the persistent tag
eligibility evidence and the ancestry rule that the requirement leaves to
design. It changes item 1's foundation only where a version command needs a
capability that item 1 does not yet expose.

## Scope and ownership of the v0.14.0 version-sources design

The v0.14.0 outcomes of item 2 are:

1. `version`, `versions list` and `versions check` run through item 1's
   dispatcher as read-only operations.
2. `versions set` is one locked, recoverable transition primitive, called by
   the CLI and reused in process by item 5.
3. A registered adapter package covers the anchor, Python with uv, npm,
   Maven reactors and declared pattern sources.
4. The version domain of `.release.ini` declares form overrides, pattern
   sources and participating component roots.
5. One tag classifier and range selector, with persistent eligibility
   evidence, serves every release-range reader.

### Delivered by item 2 in v0.14.0

- The `version` and `versions` handlers, their operation arguments and their
  output and status contract.
- The `tools/release_workflow/sources/` package, its explicit adapter tuple and
  the common source model.
- Detection, participation, lock pairing and the internal-reference boundary
  for the supported formats.
- The transition primitive: planning, locking, recovery evidence, ordered
  writes, verification and restoration.
- The version configuration schema and its cross-section validation.
- The tag classifier, the range selector with its `versions range` command,
  and the release-version rule exposed to items 5 and 7.
- The foundation extensions listed in
  [Foundation changes required by the version domain](#foundation-changes-required-by-the-version-domain).

### Left to later items or later versions

- Release and next-snapshot commits, tags, the `Release tooling:` trailer and
  `[valid]` writing, the consuming gate and lifecycle recovery: item 5.
- Changelog rendering and git-cliff range configuration: item 4, using this
  selector.
- Detecting candidate component roots during setup and recording their
  declarations: item 6, using this item's candidate listing and syntax.
- Switching `/prepare-release` Step 12 and the release-notes and release-plan
  readers: item 7.
- llm-shared's own migration and the retirement of the dev_workflow version
  scripts: item 8.
- npm and uv workspaces, Maven property forms beyond the requirement Q15
  exception, per-component versions and form overrides (design Q14), lower
  maintenance releases, and the later format candidates (`Cargo.toml`,
  Gradle, .NET, Helm, Composer, Dart, Mix, `__version__`).
- An automated recovery command for an interrupted standalone `set`; this
  version reports the retained evidence and stops.

## Confirmed codebase facts relevant to version sources

| Existing code or data | Observed behavior | Design implication |
| --- | --- | --- |
| `tools/release_workflow/cli.py` | `SHIPPED_HANDLERS` is an empty read-only mapping of `Handler(execute, requires_input)`. The parser accepts one `command` word plus root, input and text options and rejects any other argument | Handlers register in that source table; operation tokens such as `list` or `set 0.14.0` need a parser extension before dispatch |
| `tools/release_workflow/results.py` | `render` returns only 0, 1 or 2; any other status is reported and returned as 1. The item 1 design applies the same normalization at the launcher boundary | Requirement Q12's distinct incomplete-restoration status needs a fourth public status in the renderer and launcher contract |
| `tools/release_workflow/schemas.py` | `SHIPPED_SCHEMAS = (TOOLING_SCHEMA,)`. A family `SectionSchema` claims every `[prefix<instance>]` with one rule set; rules carry `required`, `default` and `path_role="managed"`; `DomainSchema.validate` sees all sections; the registry requires the complete shipped tuple | The version domain is one more shipped schema with `source:` and `component:` families; rules that differ between a built-in override and a pattern source belong in its validator |
| `tools/release_workflow/configuration.py` | Reads `.release.ini` once with interpolation off, rejects unknown sections and keys, validates every shipped domain even when a command does not use it, and creates nothing | AC12 follows from shipping the version schema; no separate validation pass is needed |
| `tools/release_workflow/managed_files.py` | `authorize_write` rechecks containment; `replace_bytes` replaces one file atomically through a flushed same-parent temporary; no multi-file transaction exists | The version transition owns ordering, capture and restoration across files, on top of per-file atomic replacement |
| `tools/release_workflow/operation_lock.py` | `OperationLock` needs `PreparedArtifacts`, publishes `a.release-operation.lock` in the artifact home, fails on a live owner, recovers a proven dead one, and offers `retain` and `transfer` for item 5. Its ownership check is private | A standalone `set` prepares artifacts and acquires the lock; reuse by a lifecycle caller needs a public check that a supplied handle owns the operation |
| `tools/release_workflow/artifacts.py` | Every context carries a read-only `ArtifactDeclaration`; `prepare_artifacts` is a separate mutation | Read commands use the declaration only; `set` prepares the home after preflight and keeps its recovery evidence there |
| `tools/release_workflow/git.py` and `tests/unit/tools/release_workflow/repository_simulation.py` | Every Git call goes through `GitExecutionContext` methods such as `index` and `metadata`; tests subclass it with programmatic observations and start no Git process | Tag, ancestry and listing queries become typed methods of that adapter, so the selector stays testable under the process audit and the 0.1 s lifecycle limit |
| llm-shared `pyproject.toml` and `tools/release_workflow/readiness.py` | `[dependency-groups] release = []`; readiness validates the locked release closure and reads `uv.lock` with `tomllib` | The engine runs on the standard library: `tomllib` reads but cannot write TOML, `json` and `xml.etree` drop formatting, `xml.parsers.expat` reports byte offsets. Writes are byte-span replacements; no release dependency is added |
| llm-shared `version.txt`, `pyproject.toml`, `uv.lock` | `0.13.0 -- Groundhog Gets a Receipt`; `[project] name = "LLM-Shared"`, `version = "0.13.0"`; `[[package]] name = "llm-shared"`, `version = "0.13.0"`, `source = { virtual = "." }` | The uv root is matched by the normalized project name and a local virtual or editable source |
| Tags of the three consumers | llm-shared: 12 annotated `vX.Y.Z` tags, the latest ending with `[valid]`. my-project: 99 tags (85 annotated, 14 lightweight), one `vX.Y.Z-SNAPSHOT`, 65 annotations ending with `[valid]`. workspace-halo: `v0.0.20`, `0.0.21`, `0.0.22`, `v0.0.23`, `v0.0.24`, all annotated. No annotation holds a `Release tooling:` line. Each history is one ancestry chain with increasing versions and one tag per commit | `[valid]` already appears on legacy tags, so it cannot separate engine tags from historical ones; the trailer can. A strict ancestry rule rejects none of these histories |
| Umbrella section "Recording the tooling version in the tag" | Engine annotations carry one `Release tooling: llm-shared <describe>` line after the `version.txt` content and before the `[valid]` line that `post` appends | Item 2 recognizes engine tags by that trailer; item 5 writes it |
| workspace-halo `package.json`, `package-lock.json` | `version` 0.0.24, no `workspaces`; lock format 3 with top-level `version` and `packages[""].version`; the lock uses CRLF line endings | The npm adapter edits two lock fields; byte-span edits keep CRLF untouched |
| my-project `pom.xml`, `PDF/pom.xml`, `cicd/config/.env` | Literal root `<version>`, one module `PDF` with a literal `<parent>` version; `${project.version}` appears only inside a plugin configuration value; plugin versions use properties; `.env` uses LF and defines `APP_SERVICE_VERSION=` on one line | The requirement Q15 boundary covers my-project as it is; the umbrella's anchored pattern matches exactly one line |
| `tools/prepare_release/prepare_release_plan_git.py`, `instructions/prepare-release.md`, `instructions/prepare-release-notes.md` | Use `git describe --tags --abbrev=0`, an unfiltered last-tag query | The readers item 7 switches are both Python code and instruction-driven shell commands, so the selector needs a Python interface and a read-only command |

These facts describe current code and data, not changes already made for this
topic.

## Target flow of the version commands

Read commands never prepare artifacts or take the lock. `set` plans without
side effects first, then repeats the plan under the lock before it writes:

```text
release_workflow.bat versions --project-root <root> set 0.14.0
  cli         parse the command and its operation tokens (bad tokens: 2)
  foundation  validate root and Git, load .release.ini, declare artifacts
  versions    read the anchor, detect sources, plan edits (no lock, no file)
  versions    prepare the artifact home, acquire the operation lock
  versions    recapture every source and plan again under the lock
  versions    write flushed recovery evidence into the artifact home
  versions    replace each changed source atomically, version.txt last
  versions    verify every source, durably mark the evidence complete
  versions    delete standalone evidence, release the lock
```

Three boundaries matter. A failure during the initial validation leaves the
project untouched: no artifact home, lock record or evidence. A failure after
the lock is taken but before the first source is replaced leaves every source
unchanged; the lock is released and any evidence already written is removed.
Failures after the first overwrite and before the completion boundary restore
the sources; after that boundary, cleanup failures report the applied versions
and remaining residue without restoration, as described in
[The recoverable version transition](#the-recoverable-version-transition).

## Command surface and operation arguments for version sources

### Commands and their arguments

| Command | Operation tokens | Effect |
| --- | --- | --- |
| `version` | none | Read version, title and notes |
| `versions` | `list` | List participating and visible non-participating sources |
| `versions` | `check` | Compare each participating source with its expected value |
| `versions` | `set <X.Y.Z or X.Y.Z-SNAPSHOT>` | Run the transition primitive |
| `versions` | `range` or `range <stable tag>` | Print the selected release range |

The root comes from item 1's explicit or alias surface, unchanged. Item 1's
parser gains a list of trailing operation tokens, and each `Handler` gains an
argument validator that runs right after parsing, before project validation.
A missing, extra or malformed token fails with status 2 before any Git process
or file read. The batch-character rule of item 1 still applies to these
tokens; version tokens and stable tag names contain none of the rejected
characters.

### Output contract on stdout

Command data goes to stdout in UTF-8 with LF; warnings and errors go to stderr,
as item 1's renderer already separates them.

- `version`: line 1 is the version token, line 2 the title (possibly empty),
  line 3 is empty, and the notes follow unchanged. A batch caller reads the
  version as the first line.
- `versions list`: a header line, then one tab-separated record per source:
  root-relative path with `/`, field, adapter, form, current value and status.
  The status is `participating`, `not-participating tool-only` or
  `not-participating undeclared`; a non-participating record shows `-` for
  form and value.
- `versions check`: one record per participating source: path, field, form,
  actual value, expected value and `ok` or `drift`.
- `versions set`: one record per changed source with its old and new value,
  or a single `unchanged` line for a clean same-target run.
- `versions range`: `key=value` lines `target`, `baseline` (a tag or `none`),
  `range` (a revision range Git accepts) and `commits`. A tag `target` keeps
  the caller's actual spelling. `baseline` and the left endpoint of `range`
  use the one name of the baseline boundary that the ancestry rule selects:
  its `vX.Y.Z` alias when it has one, otherwise its `X.Y.Z` alias.

### Public statuses of the version commands

| Status | Meaning for version commands |
| --- | --- |
| 0 | Success; `check` found no drift |
| 1 | Execution failure, including `check` drift, lock contention, a failed write whose restoration completed, and a completed transition whose cleanup failed (the diagnostic states that the new versions are applied) |
| 2 | Invalid input or failed preflight: tokens, malformed anchor, invalid configuration, unsupported or ambiguous arrangement, overlapping claim, release-only refusal, rejected range target, interrupted transition evidence |
| 3 | Restoration incomplete: at least one source could not be restored and its original is retained |

Status 3 is new to the foundation. Item 5 and every build adapter must treat it
as a stop that requires recovery, never as an ordinary failure to retry.

## Version tokens, the anchor and expected forms

### Version token grammar and comparison

A version token is `MAJOR.MINOR.PATCH` with an optional `-SNAPSHOT` suffix:
non-negative decimal integers without leading zeros, the uppercase suffix and
no `v`. The same parser serves the anchor, the `set` argument, configuration
bounds and the values read from sources. Comparison uses the integer triple of
the core, so `0.10.0` is higher than `0.9.0`; the suffix is not part of the
order used by the downgrade guard or the release-version rule.

### The version.txt document

The anchor is the project root's `version.txt`, decoded as strict UTF-8 with an
optional byte-order mark that is kept. Its first line holds the token,
optionally followed by whitespace, `--` and the title; anything else after the
token makes the anchor malformed. Following lines are the notes. A missing
file, invalid UTF-8 or a malformed first line fails with status 2 and a remedy,
and nothing is created.

The document records the byte span of the token. A transition replaces exactly
those bytes, so the title, the notes, the byte-order mark and every line ending
remain identical. Other `version.txt` files below the root are not sources;
a project that needs one declares a pattern source.

### Forms by adapter

| Adapter | Default form | Allowed forms | Reason |
| --- | --- | --- | --- |
| `python` (`pyproject.toml`, `uv.lock`) | `core` | `core` | Python versions cannot carry the Maven suffix (umbrella decision 6) |
| `npm` (`package.json`, lock) | `release-only` | `release-only`, `core`, `snapshot` | The requirement allows `snapshot` for packaging that accepts it |
| `maven` (reactor POMs) | `snapshot` | `snapshot` | A Maven build during a snapshot must not publish release coordinates |
| pattern sources | none, declared | `snapshot`, `core`, `release-only` | Each declaration states its form (requirement Q09) |

A configured form outside the allowed set fails configuration validation
before any command runs. The expected value of a source is the anchor token for
`snapshot`, and its core for `core` and `release-only`.

### The release-only guard

A `release-only` source whose current value is higher than its expected value
refuses the transition. The refusal happens while planning, before the lock and
before any write, and names the source, its value and the target. `check`
reports that source as `drift`. A current value that is not a well-formed
release token makes the source malformed, which also fails before any write.

## Adapter registry and the common source model

### The explicit adapter tuple

`tools/release_workflow/sources/__init__.py` declares one tuple of adapters in
detection order: `anchor`, `python`, `npm`, `maven`, then `pattern`. The
`anchor` adapter owns `version.txt` at the project root; it is the only source
whose value defines the others' expected values, and it accepts no form. A
completeness test lists the package's modules and fails when an adapter module
is missing from the tuple or appears twice.
Adding a format means adding a module, registering it in the tuple and adding
its contract tests; neither the release lifecycle nor a consumer changes.
These tests, like every test of this design, belong to llm-shared's own
development suite and run while llm-shared is changed; no version command and
no consumer release runs them.

### What an adapter provides

The umbrella's `detect`, `read`, `expected` and `write` sketch becomes this
interface:

- A name, a default form and its allowed forms. For `python`, `npm` and
  `maven`, the name is also the `[source:<name>]` instance that overrides the
  form.
- Detection for one participating root. It returns located sources and
  visible non-participating records, reading files through a read-only file
  view that loads each path at most once per phase. The transition opens a
  fresh view for each phase that must observe the disk again: the locked
  plan, the comparison before each replacement, the final verification and
  the verification of a restoration.
- A located source: physical path, field identifier, adapter, form, current
  value, the byte span or spans holding that value, its participating root and,
  for a lock, the manifest it pairs with.
- Rendering: the replacement bytes for a value in that field's syntax (a JSON
  string, a TOML string, XML text or the pattern's raw text).

Adapters never write files, take the lock or start a process. The transition
applies every edit, which keeps capture, ordering, verification and
restoration in one place and makes each adapter a pure function of file bytes
and configuration. AC3's failure-restoration contract tests therefore run the
common transition over each adapter's files, with a write failure injected at
each position.

### Combining all detectors

Every adapter runs over every participating root in tuple order. Each located
source claims the pair of its physical path and field, and the byte spans that
hold its value. Claims are then grouped by physical file. A second claim on the
same pair fails before any write, naming both claimants. So does any claim
whose span lies outside the file or overlaps another claim's span, even under a
different field identifier and even when both would write the same text. A
pattern source capturing the bytes of `[project].version`, or two pattern
sources capturing the same bytes, therefore fail. For example, a declared
component root that is also a module of the root Maven reactor fails, because
its `pom.xml` is claimed twice.

Disjoint fields in one file remain supported, such as the two version fields
of a `package-lock.json`. Their edits are composed into one new content from a
single captured original, using the spans measured in that original, so one
replacement never shifts the offsets of another.

### Locating values with the standard library

Each format is parsed for meaning with the standard library, and a
format-aware scanner identifies the owned syntactic field (its table and key,
its JSON path or its XML element path) and the byte span of its value. The
scanner, not a text search, identifies the field; the located text must then
also equal the parsed value, or the source fails as unsupported.

- TOML (`pyproject.toml`, `uv.lock`): `tomllib` gives the value. A line scanner
  finds the single-line `version = "..."` assignment, in a basic or literal
  string, inside the `[project]` table or the matching `[[package]]` block.
  Dotted `project.version` keys, inline tables and multi-line strings fail as
  unsupported layouts, with the remedy to use the plain assignment.
- JSON (`package.json`, npm locks): `json` gives the value. A path-tracking
  scanner returns the string spans of the top-level `version` and of
  `packages[""].version`. A duplicate key on either path is ambiguous, since
  `json` silently keeps the last one, and fails.
- XML (Maven POMs): `xml.parsers.expat` reports the byte offset of each event,
  which locates the text of each owned element. An owned element that holds a
  comment, CDATA, an entity reference or child markup fails as unsupported.
  A POM must be UTF-8 or declare UTF-8.
- Pattern sources: the compiled expression runs with `re.MULTILINE` over the
  decoded text in which each CRLF is presented as LF. The capture span is mapped
  back to the original bytes, so a `(.+)$` pattern on a CRLF file captures no
  carriage return and the file keeps its line endings.

Every file is decoded as strict UTF-8, keeping a byte-order mark when present.
An edit replaces only the located spans; everything else, including
formatting, ordering and line endings, stays byte for byte.

## Participation, detection and lock pairs

### Participating roots

The project root always participates. Each `[component:<id>]` declaration adds
one participating root. Every adapter detects only at a participating root (and
the modules a Maven reactor declares from it); no other directory is searched
during `check` or `set`. All participating components take the anchor's
version in their form; an undeclared package is never read for writing, and
references to it stay unchanged.

### Python with uv

- `pyproject.toml` without a `[project]` table is tool-only: it and its
  `uv.lock` are recorded as not participating.
- A `[project]` table whose `version` is missing or listed in `dynamic`, or a
  file `tomllib` cannot parse, fails with the source and the remedy.
- `uv.lock` pairs with a participating `pyproject.toml` in the same root. It
  must use a lock schema version this adapter supports, and contain exactly one
  `[[package]]` whose name equals the project's normalized name (lowercase,
  runs of `-`, `_` and `.` as one `-`) and whose source is `virtual = "."` or
  `editable = "."`. Zero or several matches fail as an ambiguous lock root.
- An absent `uv.lock` is not generated. A `uv.lock` without a participating
  `pyproject.toml` fails as an orphan lock.
- The supported lock schemas are registered in the adapter as explicit pairs
  of the lock's `version` and `revision` values, each backed by the
  compatibility evidence described below. The consumers use `version = 1` with
  revisions 3 and 5. Any unregistered pair fails as an unsupported lock schema.

uv workspaces and Python local links are rejected before any write, whether or
not a lock exists:

- A participating `pyproject.toml` that declares `[tool.uv.workspace]` fails
  as an unsupported uv workspace root.
- A `[tool.uv.workspace]` declared by the project root's `pyproject.toml`,
  even when that file is tool-only, fails when its `members` patterns, net of
  its `exclude` patterns, match a participating root. A tool-only workspace
  whose members include no participating root stays outside participation.
- A participating lock whose `[manifest]` table lists workspace members fails
  as an unsupported shared workspace lock.
- In a participating `pyproject.toml`, a `[tool.uv.sources]` entry with
  `workspace = true` fails as a workspace reference; it is never read as a
  path. An entry with `path` (editable or not), or a dependency written as a
  `file:` direct reference in `[project]` dependencies, optional dependencies
  or dependency groups, is resolved against the declaring root. When its
  physical destination is a participating root, it fails as an unsupported
  local link between participating components. Every other source, such as a
  Git, URL or index reference, or a path outside the participating roots, is
  external and stays unchanged.

### npm

- A root `package.json` without a `version` field is tool-only, together with
  its lock.
- A `workspaces` field fails as an unsupported npm workspace. A dependency
  specifier using `file:`, `link:` or `workspace:` that resolves into another
  participating root fails as an unsupported local link; one that resolves
  elsewhere is an external reference and stays unchanged.
- `package-lock.json` pairs with the manifest in the same root. Lock formats 2
  and 3 are supported: the top-level `version` where present and
  `packages[""].version`. A participating format 1 lock fails with status 2
  before any write, with the remedy to regenerate it with npm 7 or later.
  Another format, or a lock whose `packages[""]` names a different package,
  fails. Compatibility evidence covers the supported formats 2 and 3.
- `npm-shrinkwrap.json` takes precedence over `package-lock.json` in npm, so a
  participating root that has one fails as an unsupported lock rather than
  leaving it stale. Yarn and pnpm locks record no root version; they are not
  version sources and are not read.

### Maven reactors

- A root `pom.xml` starts the reactor; each `<module>` resolves relative to its
  declaring POM, recursively. Modules declared inside a `<profile>` make the
  reactor depend on activation and fail as ambiguous.
- A module's coordinates are its literal `artifactId` and its literal or
  inherited `groupId`. A module whose own coordinates use a property fails.
- A dependency or dependency-management entry is internal when its artifact
  and group identify a reactor module; the group may be literal or exactly
  `${project.groupId}`. An entry naming a reactor module's `artifactId` whose
  group cannot be determined this way fails as ambiguous.
- Owned fields: each module's own `<version>` when present (literal, or absent
  and inherited), each internal `<parent>` version (literal), and each internal
  dependency or dependency-management version (literal, absent and managed
  elsewhere, or exactly `${project.version}`, which stays unchanged).
- An absent project version is supported only when it is inherited through a
  chain of internal parents that ends in a reactor module with its own literal
  version, which the transition updates. A participating POM without its own
  version whose parent is external, such as a root POM inheriting from
  `spring-boot-starter-parent`, fails before any write with the remedy to
  declare a literal project version. External parent versions are never
  edited.
- Any other expression or a version range in an owned field fails, naming the
  file, field, expression and limitation. External parents, external
  dependencies, plugins and `<properties>` are never written.

### Pattern sources

A pattern source belongs to the project, not to a component. Its declared file
must exist and is never created. Its expression must produce exactly one
successful match whose capture holds a nonempty, well-formed value in its form;
zero matches, several matches or an empty optional group fail `list`, `check`
and `set` before any write.

### Lock pairs after participation filtering

Lock rules apply only at participating roots. A tool-only manifest and its lock
are excluded together. A lock inside an undeclared nested directory is never
inspected, because that directory does not participate.

### Undeclared nested candidates

Only `versions list` and item 6's setup look for candidates. One Git listing
of tracked files and of untracked files that no ignore rule matches (the
existing `GitExecutionContext` with a typed listing method) finds
`pyproject.toml`, `package.json` and `pom.xml` files outside the participating
roots and the reactor modules. A tracked file stays visible even when an
ignore rule matches it later; an ignored untracked file is not listed. A
directory whose manifest file carries a project version is a candidate,
reported with its path and `not-participating undeclared`; `check` and `set`
never compute candidates. The listing skips nested repositories, and
candidates exclude any path under a directory named `node_modules`, `venvs`,
`.venv`, `.git`, `target`, `vendor`, `sample`, `samples`, `example` or
`examples`, or under the configured artifact home. Changing that list is a
change to llm-shared, not a project setting.

## Configuration of the version domain in .release.ini

### Sections and keys

The version domain ships one schema with two families:

```ini
[source:npm]
; built-in override: only the form
form = snapshot

[source:cicd-env]
; pattern source: all three keys
file = cicd/config/.env
pattern = ^APP_SERVICE_VERSION=(.+)$
form = snapshot

[component:frontend]
; one participating component root
root = frontend
```

- `[source:<name>]` has optional `form`, `file` (a managed path) and `pattern`
  rules. The domain validator applies the per-instance rules: when `<name>` is
  `python`, `npm` or `maven`, only `form` is allowed and it must be one of that
  adapter's forms; `anchor` and `pattern` are reserved and cannot be declared;
  any other name is a pattern source, and `file`, `pattern` and `form` are all
  required. The pattern compiles with `re.MULTILINE` and must have exactly one
  capture group.
- `[component:<id>]` requires `root`, a managed path to a directory below the
  project root. The validator rejects the project root itself, two
  declarations of the same physical directory, and roots under the excluded
  directory names. The id names the component in diagnostics.
- A built-in form override applies to that adapter at every participating
  root.

Item 1's loader already reads the file once with interpolation off, rejects
unknown sections and keys, and validates every declaration whether or not the
current command uses it. Existence of a pattern file is checked by detection,
since the requirement attaches that failure to `list`, `check` and `set`.
Item 6 writes component declarations with this syntax; item 2 only reads them.

## The recoverable version transition

### Planning without side effects

`set` first validates its token, reads the anchor, detects every participating
source, applies forms and guards, and computes the edits. This plan uses no
lock and prepares no artifact. A well-formed target that then fails source
validation, such as an unsupported arrangement, an overlapping claim or a
release-only refusal, fails with status 2 and leaves no artifact home, lock
record or evidence. A malformed target never gets this far: the argument
validator rejects it first. A plan with no edit still continues under the
lock, so a clean result is never reported while another transition is writing.

### Ownership and the authoritative plan

A standalone `set` then prepares the artifact home and acquires item 1's
operation lock; a held lock fails with status 1. Under the lock, in this order:

1. Look for version-transition evidence in this project's artifact home.
   Standalone evidence whose manifest records a completed transition is
   residue: it is removed with a warning, and the command continues. Evidence
   owned by the lifecycle transaction supplying the current call is that
   caller's and is left alone. Any other evidence, interrupted, unreadable or
   owned by another lifecycle transaction, stops `set` with status 2, naming
   the directory. This check precedes every success path, including
   `unchanged`.
2. Read every participating file again in a fresh view, capture each file's
   bytes and existence, and compute the plan again; only this second plan is
   authoritative.
3. When this plan is empty, release the lock and report `unchanged` with
   status 0, without writing a source.

A human handles interrupted evidence: inspect it, restore what is needed and
remove it. This version provides no automated recovery command.

### Recovery evidence before the first overwrite

Before the first replacement, the transition writes a per-transition directory
in this project's artifact home, named
`a.version-transition.<timestamp>-<pid>`. It holds one copy of the original
bytes of every participating source file and a manifest recording the owner
(`standalone` or the lifecycle transaction identity), each path, its SHA-256,
its existence, the target and the state (`writing` at this point). Every file
is flushed before the first source is replaced. If the evidence cannot be
written completely, the partial evidence is removed, the lock is released and
`set` fails with status 1; no source has been written.

### Ordered writes and verification

Edits apply one file at a time through item 1's managed-write boundary, in a
deterministic order with `version.txt` last. The anchor therefore changes only
after every other source holds the new value. Before replacing a file, the
transition compares its current bytes with the captured original; a change by
another writer stops the transition and starts restoration. After the last
write, every participating source is read again in a fresh view and must hold
its expected value.

### Completion boundary and cleanup failures

Once verification succeeds, the transition atomically replaces the evidence
manifest with one whose state is `complete`, flushed before anything else
happens. For a
standalone transition, that write is the completion boundary: the new versions
are the result, and subsequent cleanup or lock-release failures do not trigger
restoration. A lifecycle owner retains the explicit later restoration ability
described in
[Reuse by a lifecycle caller](#reuse-by-a-lifecycle-caller).

- Before the boundary, any failure (a write, a comparison, the verification or
  the marker itself) restores the sources from the complete originals.
- After the boundary, the standalone transition deletes the original copies,
  then the manifest last, then releases the lock. A failure in that cleanup or
  in the lock release triggers no rollback. `set` fails with status 1 and a
  diagnostic stating that the new versions are applied and naming the residue
  left behind, the evidence directory or the lock record. The next `set` removes
  standalone residue whose manifest says `complete`; a lock record left by a
  failed release becomes recoverable once its process has ended.
- Status 3 stays reserved for an incomplete restoration. The in-process
  interface reports distinct outcomes: applied, unchanged, restored,
  restoration incomplete, and applied with cleanup failed.

### Restoration and its distinct failure

On any failure before the completion boundary and after the first
replacement, the transition restores every file it replaced from the evidence
and reads each one back in a fresh view. When every file matches its captured
original, the evidence is deleted (original copies first, manifest last), the
lock is released and `set` fails with status 1. When any file cannot be
restored, for example because an editor holds it open, the evidence stays
complete, its manifest state becomes `restoration-incomplete`, and `set` fails
with status 3. Its diagnostics name each unrestored source and the path of its
retained original, and never report a complete restoration.

A process killed mid-transition leaves the lock record and the evidence, in
state `writing` or `complete` depending on when it stopped. Item 1's lock
recovers a proven dead owner on the next acquisition; the next `set` then
removes `complete` residue and stops on `writing` evidence, as described
above. A process killed after its last replacement but before the completion
marker leaves fully synchronized sources with `writing` evidence; that evidence
still stops the next `set`, even when the target is the same, because nothing
proved the transition finished. Read commands report any leftover evidence as a
warning on stderr.

### Reuse by a lifecycle caller

The CLI handler and item 5 call the same in-process primitive. Item 5 passes
the operation lock it already holds and its transaction identity.

- A new public method of the lock checks that the handle is held by the
  current process and that its lock record is the one in this invocation's
  managed artifact home, for the same physical project root. A released handle,
  or one taken for another project, fails before any read. The primitive
  neither acquires nor releases a supplied lock.
- The evidence is written in this project's artifact home with the
  transaction identity as its owner. On success it is marked `complete` and
  kept, and the primitive returns a handle that item 5 can use to restore the
  version sources later with the same restoration routine. Item 5 deletes the
  evidence when its transaction ends; the primitive never removes evidence
  owned by a lifecycle transaction.
- The evidence check of step 1 accepts the supplied transaction's own evidence
  and stops on any other unfinished evidence, so an earlier abandoned
  transaction is never mistaken for the current one.

## Read-only commands and their limits

`version`, `versions list`, `versions check` and `versions range` take no lock,
prepare no artifact and write nothing. They read the artifact declaration only
to find leftover evidence and to exclude the artifact home from candidates.
They may observe a transition in progress, since item 1's per-file
replacements give no multi-file snapshot; a `check` during a transition is not
a release-readiness guarantee.

Each read command reads each source file once. `set` reads them once per phase
that must observe the disk: the initial plan, the locked plan, the comparison
before each replacement, the final verification and, after a failure, the
restoration check. Detection probes only the participating roots and their
Maven modules; only `list` lists the tree, with one Git call. `version`,
`check` and `set` start no Git process of their own. `range` uses a fixed
number of Git calls whatever the number of tags. No version command loads
git-cliff.

## Lock compatibility evidence for supported tools

No supported format needs lock regeneration in v0.14.0, so the requirement's
regeneration exception has no user in this version; `set` never runs `uv` or
`npm`. The compatibility guarantee rests on evidence recorded when fixtures
are generated, never on tool runs during `set`.

The evidence compares two states of one manifest and lock pair. The "before"
pair is the two files as a project has them before `versions set` changes the
version: for example a `pyproject.toml` and its `uv.lock`, both at `0.13.0`,
which the tool accepts as current. The edited pair is the same two files after
the adapter's version-only edit, both at `0.14.0` with every other byte
unchanged. "Accepted as current" means the tool's locked or frozen command
exits successfully and changes neither file. Recording the "before" acceptance
proves the starting pair was valid, so the acceptance after the edit shows that
the edit kept it valid; without the starting-pair acceptance, success afterwards
would not establish preservation from an accepted starting pair, and a failure
could come from a lock that was already stale, which `set` does not repair.

For each supported combination of tool version, lock schema (the uv
`version`/`revision` pair, or npm lock format 2 or 3) and root layout (a uv
virtual or editable root, an npm root package), the evidence records:

1. The real tool accepting the "before" manifest and lock pair in its locked
   or frozen mode, without changing either file.
2. The adapter's version-only edit of that pair.
3. The same tool accepting the edited pair in the same mode, again without
   changing the manifest or the lock.

Each record names the tool and its version, the schema, the layout, the
command and its outcome, and the SHA-256 of both files before and after each
step. A test checks that the adapter still produces the recorded edited pair
from the recorded "before" pair. A combination without such a record is not
supported: its schema or layout fails before any write. Supporting a new tool
version, schema or layout means recording new evidence; the plans name the
exact tools, versions, commands and fixture locations.

## Stable and snapshot tag classification

### Classifying tag names

- `vX.Y.Z` and the legacy `X.Y.Z` are stable release names, with the token
  grammar above.
- `vX.Y.Z-SNAPSHOT` and `X.Y.Z-SNAPSHOT`, in any case of the suffix, are
  development markers. They never become baselines, targets or recovery
  targets, even at HEAD.
- Every other tag name, including other prereleases, is not a release and is
  ignored.

### Persistent eligibility evidence

Eligibility is read from the tag object itself, so it is the same in every
clone and needs no local journal (umbrella decision 34). Matching is by whole
lines, never by a substring found in the notes. A trailer line is a line that
starts with exactly `Release tooling:`, one space and a nonempty value, and a
validation line is exactly `[valid]`. Following the umbrella's placement, the
trailer must be the last nonempty line of the annotation, or the last but one
when only `[valid]` follows it:

| Stable tag | Classification | Baseline eligibility |
| --- | --- | --- |
| Lightweight, or annotated with no trailer line anywhere | Historical release | Eligible, with or without `[valid]` |
| Annotated, ending with one trailer line then `[valid]` | Validated engine release | Eligible |
| Annotated, ending with one trailer line | Unvalidated engine release, including an active transaction | Not eligible |
| Annotated with a trailer line anywhere else, several trailer lines, or `[valid]` before the trailer | Ambiguous | Never a baseline; reported |

Item 5 writes the trailer when it creates a tag and appends `[valid]` after a
successful gate, as the umbrella specifies; this classifier only reads them.
Missing evidence never promotes a tag: an engine tag without `[valid]` stays
ineligible, whatever local state exists. Existing tags need no migration,
because none of the three consumers has an annotation with the trailer. A legacy
dev_workflow release interrupted before its own post-processing has no trailer
and remains a historical release; item 8's cutover checks for such tags.

This table classifies single tags. A release can carry several tags of one
version on one commit, its aliases, such as a historical `0.13.0` and a
validated `v0.13.0`. The ancestry rule below groups them into one boundary
and derives the boundary's class from its aliases (design decision Q18).
Selection and the release-version rule use that boundary class, never the
class of one alias alone.

## Range selection and the release-version rule

### The deterministic ancestry rule

The selector takes a target, HEAD or a stable release tag, and applies one
rule:

1. Resolve the target: HEAD, or the caller's actual stable tag name resolved
   to its commit. A missing tag, or a snapshot or other prerelease name,
   fails with status 2. A tag target's eligibility is decided in step 4,
   from its whole boundary.
2. Read every stable tag reachable from the target commit, the target's own
   tags included, with its object type, peeled commit and annotation, and
   classify each one.
3. Group those tags by version and commit, whatever their eligibility. Tags
   of the same version on the same commit form one boundary. The same version
   on different commits, or different versions on one commit, are conflicting
   tags and fail, naming them. This check runs before anything is excluded, so
   `1.0.0` on commit A and `v1.0.0` on a later commit B fail even for
   `range v1.0.0`. Each boundary then takes the most restrictive class of
   its aliases: it is ambiguous when any alias is ambiguous; otherwise it is
   not eligible when any alias is an unvalidated engine tag; otherwise it is
   eligible. A boundary of one tag keeps that tag's class. The later steps
   use the boundary's class only.
4. For a tag target, its boundary must be eligible: an ambiguous or
   ineligible target boundary fails with status 2 naming its aliases, even
   when the named alias is eligible on its own. Remove the target's boundary
   as a whole, every alias of its version on the target commit together.
   The remaining eligible boundaries are the candidates. For HEAD, an
   eligible boundary on HEAD itself stays a candidate.
5. The baseline is the single candidate that is not an ancestor of another
   candidate; every other candidate is then an ancestor of it. Several such
   candidates, from merged parallel histories, are a conflict and fail. So does
   a baseline whose version is lower than another candidate's.
6. Classify the remaining boundaries against the baseline with the tags
   reachable from the target but not from the baseline. An ambiguous
   boundary among them fails the selection, naming its aliases, rather than
   being skipped. An ineligible boundary among them is excluded with a
   warning naming its aliases.
7. With no candidate, the range is the full history through the target.

For HEAD, a release on HEAD itself makes the range just after a release empty.
The selector never splits `git describe` output: it reports the revision range
and asks Git for that range's commit count explicitly.

The selected baseline boundary supplies one name: its `vX.Y.Z` alias when it
has one, otherwise its `X.Y.Z` alias (design decision Q19). Every alias of an
eligible boundary is eligible, so that name is always an eligible actual tag.
The in-process result returns it, and the output prints it as `baseline` and
as the left endpoint of `range`. All aliases name one commit, so the choice
changes neither the selected commits nor their count, and a tag target keeps
the caller's actual spelling.

### Git queries of the selector

The selector uses typed methods added to `GitExecutionContext`, each returning
the information one step of the rule uses:

| Query | Used by |
| --- | --- |
| Stable tag records reachable from the target: name, object type, peeled commit, annotation | Steps 1 to 4 |
| Independent tips among the candidate commits | Step 5 |
| Tag names reachable from the target and not from the baseline | Step 6 |
| Commit count of the selected range | Output |

That is at most four Git calls for one selection, whatever the number of tags.
The peeled commit of a tag of a tag comes from that same listing: from Git
2.44, the `%(*...)` fields of `for-each-ref` peel a tag fully to its commit,
while older Git stops at the inner tag object, which no listing row explains
once the inner tag's own ref is deleted. Rather than add a call or fail on
such valid tags, the release tooling requires Git 2.44 or later (user
decision of 2026-11-08, during the Step 1 code review). An older Git is
refused when the operation selects its executable, with this reason and the
remedy to upgrade; a tag record still dereferenced to a tag object is refused
with the same reason.
The release-version rule adds one listing of all tags and one listing of the
tags reachable from `main`. Tests supply each observation programmatically, as
they already do for indexes and configuration.

### The release-version rule for items 5 and 7

A second function exposes umbrella decision 33 without enforcing it in `set`
(requirement Q01). A target release version is rejected when any existing
stable tag, in either spelling and whatever its own or its boundary's
eligibility, already names that version. It is also rejected unless it is
higher, comparing numerically, than every eligible boundary reachable from
`main`: the stable tags reachable from `main` are grouped into boundaries and
classified as step 3 of the ancestry rule does. With no eligible boundary,
any well-formed target passes. Items 5 and 7 call it in their preflights.

### Exposure to every range reader

Items 4, 5 and 7 call the selector and the release-version rule in process.
Instruction-driven readers, which today run `git describe --tags --abbrev=0`,
call the read-only `versions range` command instead. Item 7 switches those
readers; item 2 only provides both entries.

## Foundation changes required by the version domain

Six deliberate extensions change item 1's code. Three of them change a
documented item 1 contract, and their tests change with them; the others add
capabilities without altering existing behavior:

| Change | Item 1 contract affected | Test impact |
| --- | --- | --- |
| `cli.py` collects trailing operation tokens, `Handler` gains an argument validator, and `version` and `versions` join `SHIPPED_HANDLERS` | The parser no longer rejects every token after the command; a handler without a validator still rejects any extra token | Parser tests gain operation-token cases; the "every operation is unavailable" expectation now excludes the two shipped commands |
| `results.py` and the launcher boundary accept status 3 | The public statuses become 0, 1, 2 and 3; any other status is still reported and returned as 1 | Renderer and launcher status tests add 3 and keep the normalization of other values |
| `schemas.py` adds the version schema to `SHIPPED_SCHEMAS` | None: the registry was built for more domains | Registry composition tests include the version domain |
| `operation_lock.py` exposes a public ownership check bound to the current project's artifact home | None: acquisition, release, retention and transfer are unchanged | New tests for the check, including a handle from another project |
| `git.py` adds typed observations for tags, independent tips, commit counts and the candidate listing | None: existing methods and Git isolation are unchanged | The repository simulation gains matching programmatic observations |
| `git.py` raises the minimum Git version from 2.31.0 to 2.44.0, the first whose `for-each-ref` peels a tag of a tag to its commit | Item 1's minimum Git 2.31.0 (its decision Q11) becomes 2.44.0; the refusal states why and asks for an upgrade | Version tests use 2.44.0 as the floor and check the stated reason |

Every other foundation guarantee stays as it is: root validation, Git
isolation, managed-write revalidation, artifact preparation and the lock's
recovery rules.

## Acceptance cases for the version-sources design

| Scenario | Expected outcome | Requirement |
| --- | --- | --- |
| `version` on `0.14.0-SNAPSHOT -- Title` with notes | Prints token, title, empty line, notes; no file or artifact is created | AC1 |
| Anchor `v0.14.0`, `0.14.0-snapshot` or `0.014.0` | Status 2 with the remedy; nothing created | AC1 |
| `set 0.14.0` on a CRLF `version.txt` | Only the token bytes change; title, notes and CRLF identical | AC2 |
| An adapter module missing from the tuple | Completeness test fails | AC3 |
| Root `pyproject.toml`, `uv.lock`, `package.json`, `package-lock.json` | All four participate and change in one `set` | AC4, AC5 |
| `pyproject.toml` with only `[tool.ruff]` and a `uv.lock` | Both listed `not-participating tool-only`; `check` and `set` ignore them | AC4, AC10 |
| Undeclared `frontend/package.json` with a version | Listed `not-participating undeclared`; `check` and `set` succeed without it | AC5, AC10 |
| `frontend` declared as a component and also a reactor module | Conflicting claim on `frontend/pom.xml`; status 2 before any write | AC5 |
| `[project]` with `dynamic = ["version"]` | Status 2 naming the source and remedy | AC6 |
| Pattern matching twice, or not at all, or an empty optional group | Status 2 for `list`, `check` and `set` | AC6 |
| Internal dependency version `${revision}` | Status 2 naming file, field and expression | AC6, AC9 |
| Internal dependency version `${project.version}` | Left unchanged; reactor versions and parents change | AC9 |
| `package.json` with `workspaces` | Status 2 naming the limitation | AC9 |
| Anchor `0.0.25-SNAPSHOT`, npm at `0.0.25` | npm expected and kept at `0.0.25`; Maven gets `0.0.25-SNAPSHOT` | AC7 |
| `set 0.0.24` with npm `release-only` at `0.0.25` | Status 2 before any write, naming source, value and target; `check` reports drift | AC7 |
| `set` on uv and npm locks | Only the owned version strings change; other bytes, including CRLF, identical; tool fixtures agree | AC8 |
| Participating `package-lock.json` with `lockfileVersion` 1 | Status 2 before any write; remedy: regenerate the lock with npm 7 or later | AC4, AC8 |
| Injected failure at the third of five writes | First two restored and verified; evidence deleted; status 1 | AC11 |
| Injected failure while restoring | Status 3 naming each unrestored source and its retained copy | AC11 |
| `set` to the version already in place, no drift | Lock taken and released, `unchanged`, no source written | AC11 |
| `set` while another operation holds the lock | Status 1 naming the owner; nothing written | AC11 |
| Leftover `writing` evidence from a killed `set` | Next `set` stops with status 2 naming it; `check` warns | AC11 |
| `[source:python]` with `form = snapshot`, or `[source:npm]` with an unknown key | Configuration failure for every command, even `version` | AC12 |
| `v0.14.0-SNAPSHOT` at HEAD after stable `v0.13.0` | Baseline `v0.13.0`, range `v0.13.0..HEAD` | AC13 |
| Engine tag `v0.14.0` with trailer, no `[valid]`, in a fresh clone | Not eligible; baseline stays the previous release | AC13 |
| `range v0.13.0` where `v0.12.0` precedes it | Baseline `v0.12.0`, never `v0.13.0` itself | AC14 |
| workspace-halo's mixed `0.0.22` and `v0.0.23` history at HEAD `v0.0.24` | Baseline at HEAD: `v0.0.24`; `range v0.0.24` gives `v0.0.23..v0.0.24` | AC14 |
| `0.13.0` and `v0.13.0` on different commits | Conflicting tags; status 2 | AC14 |
| Release-version rule for `0.13.0` with `v0.13.0` tagged | Rejected as reserved | AC15 |
| `1.0.0` on commit A, `v1.0.0` on a later commit B, then `range v1.0.0` | Conflicting tags, status 2 naming both; A never becomes the predecessor | AC14 |
| `v1.0.0` and `v1.1.0` on the same commit, then `range v1.1.0` | Conflicting tags, status 2 | AC14 |
| An ambiguous engine tag between baseline `v0.13.0` and HEAD | Selection fails with status 2 naming the tag | AC13 |
| Historical `0.13.0` and unvalidated engine `v0.13.0` on one commit, after `v0.12.0` | Boundary not eligible; at HEAD, baseline `v0.12.0` with a warning naming both aliases | AC13, AC14 |
| Validated `v0.13.0` and unvalidated engine `0.13.0` on one commit, after `v0.12.0` | Boundary not eligible; at HEAD, baseline `v0.12.0` with a warning naming both aliases | AC13, AC14 |
| Validated `v0.13.0` and ambiguous `0.13.0` on one commit, after `v0.12.0` | At HEAD, selection fails with status 2 naming both aliases | AC13 |
| Two unvalidated engine aliases, or two ambiguous aliases, on one commit | The boundary is not eligible, or ambiguous, as a single tag of that class | AC13 |
| Historical `0.13.0` and validated `v0.13.0` on one commit, HEAD after it | Baseline `v0.13.0`, range `v0.13.0..HEAD` | AC14 |
| `range 0.13.0` or `range v0.13.0` when that commit carries historical `0.13.0` and unvalidated `v0.13.0` | Status 2 naming both aliases, although `0.13.0` alone is eligible | AC14 |
| Eligible `0.14.0` and `v0.14.0` on HEAD, after `v0.13.0` | At HEAD: baseline `v0.14.0`, empty range; `range 0.14.0` or `range v0.14.0`: both aliases removed, baseline `v0.13.0` | AC14 |
| Release-version rule for `0.12.5` when `main` holds `v0.12.0`, then historical `0.13.0` with unvalidated `v0.13.0` on one commit | Accepted: that boundary is not eligible, so `v0.12.0` is the bound; `0.13.0` itself stays reserved | AC15 |
| Participating `pyproject.toml` with `[tool.uv.workspace]` and no `uv.lock` | Status 2 naming the workspace | AC9 |
| Declared Python components `api` and `cli`, with `cli` declaring `[tool.uv.sources] api = { path = "../api" }` | Status 2 naming both components and the link | AC9 |
| Tool-only root `pyproject.toml` whose uv workspace members include a declared component | Status 2 naming the workspace and the component | AC9 |
| A pattern source capturing the `version` value of `pyproject.toml` | Overlapping claim, status 2 naming both claimants | AC5 |
| Two pattern sources capturing the same bytes, even with the same replacement | Overlapping claim, status 2 | AC5 |
| Process killed after its last replacement, before the completion marker, then `set` to the same target | Stops with status 2 naming the `writing` evidence; never reports `unchanged` | AC11 |
| Deleting the original copies fails after the completion marker | Status 1: new versions applied, residue named, no rollback; the next `set` removes the residue | AC11 |
| Lifecycle call with a lock handle taken for another project | Fails before any read | AC11 |
| Module inheriting its version from an internal parent with a literal version | The parent's version and the module's `<parent>` version change; the module stays inherited | AC9 |
| Root POM with an external parent and no `<version>` of its own | Status 2 with the remedy to declare a literal version | AC6, AC9 |
| `uv.lock` with an unregistered `version` and `revision` pair | Status 2 naming the unsupported schema | AC8 |
| Recorded evidence for a supported uv layout or npm lock format | The tool's locked mode accepts the before and edited pairs without changing either file | AC8 |

## File-based IO cost clarification for version sources

The read bounds of
[Read-only commands and their limits](#read-only-commands-and-their-limits)
are the whole IO contract: each read command reads each source file once, and
`set` once per phase that must observe the disk. Detection probes fixed file
names at participating roots and declared Maven modules, never a directory
walk; only `list` lists the tree, with one Git call, and `range` uses at most
four. Read commands list the artifact home once, without recursion, for
leftover evidence. Writes are the recovery evidence, then one atomic
replacement per changed source through item 1's managed-write boundary. No
version command runs a build or lock tool, and no document index or wall-clock
target is added.

## Design decisions for the v0.14.0 version-sources design

The user decided each question after an explanation (Q01 to Q10 on
2026-11-05, Q11 to Q17 on 2026-11-06), and independent review round 3 checked
the decisions for consistency with each other, with this design and with the
feature request. Q18 and Q19 settle the aliased-boundary clarification that
plan decision Q15 reserved: the user authorized it, decided both on 2026-11-08
after an explanation, and independent review (exchange 2, round 1) found them
consistent with Q01 to Q17, the feature request and the umbrella. The question
blocks, with their full options and arguments, are kept in the commits
`docs(design): record pre-consolidation questions` (`ec6e967` for Q01 to Q17,
`083ef50` for Q18 and Q19).

| Question | Decision and reason | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | An annotated tag whose whole-line `Release tooling:` trailer sits at the umbrella's position is an engine tag, eligible only with a standalone `[valid]` line after that trailer; other stable tags are historical and eligible; a misplaced or repeated trailer makes the tag ambiguous. The evidence travels with the tag to every clone and adds nothing for item 5 to write | Persistent eligibility evidence; AC13 | A dedicated `Release-Engine:` marker line (a second marker to keep consistent); Git notes or a ref namespace (not fetched by default, so other clones lose the evidence) |
| Q02 | Selection fails with status 2, naming the tags, on several independent eligible tips or a version inversion; no baseline is guessed, since a wrong baseline silently changes changelogs and release notes, and the three consumers' histories are single increasing chains | The deterministic ancestry rule; AC14 | The highest-version tip with warnings (a merged maintenance release can drop from or duplicate in the notes); the latest commit date (clocks, not ancestry) |
| Q03 | A read-only `versions range [<stable tag>]` operation of the `versions` handler prints `target`, `baseline`, `range` and `commits` from the shared selector; item 7 switches the instruction-driven readers to it | Commands and their arguments; Exposure to every range reader | A separate top-level `range` command (another handler for one read); a Python interface only (item 7 would design a second entry) |
| Q04 | Item 1's renderer and launcher boundary accept public status 3 for an incomplete restoration, for the command and in-process callers; other unknown statuses still become 1; item 1's contract and tests change explicitly | Public statuses of the version commands; Foundation changes required by the version domain; AC11 | Status 1 with a stable stderr line (no distinct public status); status 3 only in process (the command cannot tell the two failures apart) |
| Q05 | `set` plans first without a lock or artifact, then always prepares the artifact home and takes the lock, even after an empty first plan, checks for transition evidence and plans again; only the locked plan is authoritative. Source-validation failures stay artifact-free, and a clean result never overlaps another transition | Target flow of the version commands; Planning without side effects; Ownership and the authoritative plan; AC11 | Locking first and planning once (a failed validation leaves an artifact home and a lock record); an unlocked `unchanged` (can report a clean state during another `set`) |
| Q06 | Interrupted or unreadable `writing` evidence stops the next `set` with status 2 naming the evidence directory, and read commands warn; a person restores or removes it; no automatic restore and no recovery command in this item, since item 5 designs lifecycle recovery next | Ownership and the authoritative plan; Restoration and its distinct failure; Left to later items or later versions; AC11 | An automatic restore by the next `set` (decides for the user and adds a write path); a `versions recover` operation (recovery designed twice with item 5) |
| Q07 | Item 5 supplies its held lock, checked against this process and project, and its transaction identity; the primitive writes evidence owned by that identity in this project's artifact home, keeps it on success, returns a restore handle and never removes lifecycle-owned evidence; item 5 deletes it when its transaction ends | Reuse by a lifecycle caller; AC11 | Always deleting the evidence, with a separate item 5 capture (two captures and two restoration routines); no primitive evidence under item 5 (its restoration would depend on a record it does not own) |
| Q08 | Each format is parsed with the standard library for meaning; a format-aware scanner, with `expat` byte offsets for XML, locates the owned byte span, which must equal the parsed value, and only those bytes change; unsupported spellings fail before any write; no release dependency is added | Locating values with the standard library; Combining all detectors; AC2, AC8 | Format-preserving libraries such as `tomlkit` (a new release dependency, no byte guarantee, nothing for XML); one regular expression per format (cannot tell the root version from a dependency's) |
| Q09 | Pattern sources match a view of the decoded text in which each CRLF reads as LF, and the capture span maps back to the original bytes, so the umbrella's `(.+)$` pattern works on either line ending and the file keeps its CRLF | Locating values with the standard library; Pattern sources | Raw-text matching with a `([^\r\n]+)` hint (copied patterns fail on Windows files); rejecting CRLF files (common in Windows repositories) |
| Q10 | Python allows only `core`; npm allows `release-only`, `core` and `snapshot`; Maven allows only `snapshot`; a pattern source takes its declared form; any other configured form fails configuration validation before a command runs | Forms by adapter; Sections and keys; AC7, AC12 | Maven also accepting `core` (a snapshot build would carry release coordinates); every form for every adapter but Python (the same risk, with no consumer asking) |
| Q11 | The npm adapter supports lock formats 2 and 3; a participating format 1 lock fails with status 2 before any write, with the remedy to regenerate it with npm 7 or later. Every supported format has tool evidence that can still be produced, and no consumer uses format 1 | npm; Lock compatibility evidence for supported tools; AC4, AC8 | Formats 1, 2 and 3 (npm 6 fixtures on an end-of-life Node, for no consumer); format 3 only (format 2 locks from npm 7 and 8 stay common) |
| Q12 | A dependency or dependency-management entry is internal when its `artifactId` and its literal group, or exactly `${project.groupId}`, identify a reactor module; an entry naming a module's `artifactId` with another group expression fails as ambiguous; no property resolution | Maven reactors; AC9 | Literal groups only (a `${project.groupId}` sibling dependency silently stays stale); resolving reactor properties (reopens the property resolution the requirement left out) |
| Q13 | Item 6 writes and item 2 reads one `[component:<id>]` section per participating component root, with a required `root` managed path; the id names the component in diagnostics, and item 6 updates one entry by it | Participating roots; Sections and keys; AC5 | One `[components]` list (its own splitting and quoting rules); the path as the section name (escapes managed-path validation, no id) |
| Q14 | A built-in form override such as `[source:npm] form = snapshot` applies to that adapter at every participating root; per-component forms are deferred and can later become a key of `[component:<id>]` | Sections and keys; Left to later items or later versions | Per-component form keys now (configuration and validation for a case no consumer has); per-component forms only (repeats the same form at every root) |
| Q15 | Candidate discovery uses one Git listing of tracked files plus untracked files that no ignore rule matches, skips nested repositories, and excludes the fixed directory names and the artifact home; a tracked file stays listed even when an ignore rule matches it later | Undeclared nested candidates; AC5, AC10 | Tracked files only (a new component stays invisible to setup until added); a filesystem walk (walks ignored trees and reports deliberately ignored projects) |
| Q16 | The anchor's first line holds the token, optionally followed by whitespace, `--` and the title; anything else after the token makes the anchor malformed, with status 2 and a remedy before any write, so a version typo never becomes a silent title | The version.txt document; AC1 | Reading any trailing text as the title (`0.14.0 -SNAPSHOT` silently becomes `0.14.0`); ignoring text without `--` (drops the intended title, with the same typo risk) |
| Q17 | After verification, the transition durably records a `complete` state in the evidence manifest. Before it, any failure restores from complete originals; after it, cleanup deletes the originals and then the manifest, and a cleanup or lock-release failure returns status 1, stating that the new versions are applied and naming the residue, without rollback. The next `set` removes standalone `complete` residue and still stops on `writing` evidence | Target flow of the version commands; Completion boundary and cleanup failures; Public statuses of the version commands; AC11 | Keeping the evidence until an explicit cleanup (copies left after every success, a new routine or command); status 0 with a warning (residue goes unnoticed, and the next run cannot tell it from an interruption) |
| Q18 | A boundary of same-version, same-commit tags takes the most restrictive class of its aliases: ambiguous when any alias is ambiguous, otherwise not eligible when any alias is an unvalidated engine tag, otherwise eligible. That class decides a tag target, the candidates, the boundaries after the baseline and the release-version rule's bound. No alias, with or without evidence, makes a release whose gate did not pass a baseline, and the single-tag behavior applies unchanged | Persistent eligibility evidence; The deterministic ancestry rule; The release-version rule for items 5 and 7; AC13, AC14, AC15 | One eligible alias is enough (a lightweight alias promotes a failed release); validated evidence decides (a precedence order for an arrangement the tooling never creates); disagreement fails (a stray alias stops every range reader) |
| Q19 | The baseline boundary is named by its eligible `vX.Y.Z` alias when it has one, otherwise by its `X.Y.Z` alias, in `baseline`, in the left endpoint of `range` and in the in-process result. The name depends on the tags alone, matches the spelling of new releases and changes neither the commits nor their count | The deterministic ancestry rule; Output contract on stdout; AC14 | Follow the target's spelling (the output depends on the argument); print every eligible alias (breaks the one-tag `baseline` line and moves the choice to each reader) |
