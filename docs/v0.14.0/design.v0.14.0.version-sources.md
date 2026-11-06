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
- npm and uv workspaces, Maven property forms beyond the Q15 exception,
  per-component versions and form overrides, lower maintenance releases, and
  the later format candidates (`Cargo.toml`, Gradle, .NET, Helm, Composer,
  Dart, Mix, `__version__`).
- An automated recovery command for an interrupted standalone `set`; this
  version reports the retained evidence and stops.

## Confirmed codebase facts relevant to version sources

| Existing code or data | Observed behavior | Design implication |
| --- | --- | --- |
| `tools/release_workflow/cli.py` | `SHIPPED_HANDLERS` is an empty read-only mapping of `Handler(execute, requires_input)`. The parser accepts one `command` word plus root, input and text options and rejects any other argument | Handlers register in that source table; operation tokens such as `list` or `set 0.14.0` need a parser extension before dispatch |
| `tools/release_workflow/results.py` | `render` returns only 0, 1 or 2; any other status is reported and returned as 1. The item 1 design applies the same normalization at the launcher boundary | Q12's distinct incomplete-restoration status needs a fourth public status in the renderer and launcher contract |
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
| my-project `pom.xml`, `PDF/pom.xml`, `cicd/config/.env` | Literal root `<version>`, one module `PDF` with a literal `<parent>` version; `${project.version}` appears only inside a plugin configuration value; plugin versions use properties; `.env` uses LF and defines `APP_SERVICE_VERSION=` on one line | The Q15 boundary covers my-project as it is; the umbrella's anchored pattern matches exactly one line |
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
  `range` (a revision range Git accepts) and `commits`.

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
| pattern sources | none, declared | `snapshot`, `core`, `release-only` | Each declaration states its form (Q09) |

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
- `package-lock.json` pairs with the manifest in the same root. Lock formats 1,
  2 and 3 are supported: the top-level `version` where present and, from
  format 2, `packages[""].version`. Another format, or a lock whose
  `packages[""]` names a different package, fails.
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

This section describes the boundary proposed in Q17. Once verification
succeeds, the transition atomically replaces the evidence manifest with one
whose state is `complete`, flushed before anything else happens. For a
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

For each supported combination of tool version, lock schema (the uv
`version`/`revision` pair, or the npm lock format) and root layout (a uv
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

## Range selection and the release-version rule

### The deterministic ancestry rule

The selector takes a target, HEAD or a stable release tag, and applies one
rule:

1. Resolve the target. A tag target must be a stable, eligible release; a
   missing tag, a snapshot or other prerelease, or an ineligible or ambiguous
   tag fails with status 2.
2. Read every stable tag reachable from the target commit, the target's own
   tags included, with its object type, peeled commit and annotation, and
   classify each one.
3. Group those tags by version and commit, whatever their eligibility. Tags
   of the same version on the same commit form one boundary. The same version
   on different commits, or different versions on one commit, are conflicting
   tags and fail, naming them. This check runs before anything is excluded, so
   `1.0.0` on commit A and `v1.0.0` on a later commit B fail even for
   `range v1.0.0`.
4. For a tag target, remove the target's boundary as a whole, every alias of
   its version on the target commit together. The remaining eligible
   boundaries are the candidates. For HEAD, a release tagged on HEAD itself
   stays a candidate.
5. The baseline is the single candidate that is not an ancestor of another
   candidate; every other candidate is then an ancestor of it. Several such
   candidates, from merged parallel histories, are a conflict and fail. So does
   a baseline whose version is lower than another candidate's.
6. Classify the remaining tags against the baseline with the tags reachable
   from the target but not from the baseline. An ambiguous tag among them
   fails the selection rather than being skipped. An unvalidated engine tag
   among them is excluded with a warning.
7. With no candidate, the range is the full history through the target.

For HEAD, a release on HEAD itself makes the range just after a release empty.
The selector never splits `git describe` output: it reports the revision range
and asks Git for that range's commit count explicitly.

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
The release-version rule adds one listing of all tags and one listing of the
tags reachable from `main`. Tests supply each observation programmatically, as
they already do for indexes and configuration.

### The release-version rule for items 5 and 7

A second function exposes umbrella decision 33 without enforcing it in `set`
(Q01). A target release version is rejected when any existing stable tag, in
either spelling and whatever its eligibility, already names that version. It is
also rejected unless it is higher, comparing numerically, than every eligible
stable release reachable from `main`. With no eligible release, any well-formed
target passes. Items 5 and 7 call it in their preflights.

### Exposure to every range reader

Items 4, 5 and 7 call the selector and the release-version rule in process.
Instruction-driven readers, which today run `git describe --tags --abbrev=0`,
call the read-only `versions range` command instead. Item 7 switches those
readers; item 2 only provides both entries.

## Foundation changes required by the version domain

Five deliberate extensions change item 1's code. Two of them change a
documented item 1 contract, and their tests change with them; the others add
capabilities without altering existing behavior:

| Change | Item 1 contract affected | Test impact |
| --- | --- | --- |
| `cli.py` collects trailing operation tokens, `Handler` gains an argument validator, and `version` and `versions` join `SHIPPED_HANDLERS` | The parser no longer rejects every token after the command; a handler without a validator still rejects any extra token | Parser tests gain operation-token cases; the "every operation is unavailable" expectation now excludes the two shipped commands |
| `results.py` and the launcher boundary accept status 3 | The public statuses become 0, 1, 2 and 3; any other status is still reported and returned as 1 | Renderer and launcher status tests add 3 and keep the normalization of other values |
| `schemas.py` adds the version schema to `SHIPPED_SCHEMAS` | None: the registry was built for more domains | Registry composition tests include the version domain |
| `operation_lock.py` exposes a public ownership check bound to the current project's artifact home | None: acquisition, release, retention and transfer are unchanged | New tests for the check, including a handle from another project |
| `git.py` adds typed observations for tags, independent tips, commit counts and the candidate listing | None: existing methods and Git isolation are unchanged | The repository simulation gains matching programmatic observations |

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

## Open questions for the v0.14.0 version-sources design

### Q01: Evidence that separates engine tags from historical tags

Question description: umbrella decision 34 leaves the persistent tag
eligibility mechanism to this design. The design reads it from the tag object:
an annotated tag with a `Release tooling:` line is an engine tag, eligible only
with a standalone `[valid]` line after that trailer; every other stable tag is
historical and eligible. `[valid]` alone cannot decide, because legacy
dev_workflow tags already end with it (65 of my-project's annotations, the
latest llm-shared tag). The question is whether the umbrella's diagnostic
tooling trailer should also carry eligibility, or whether another marker
should.

#### BBQ for Q01

A wine shop sells old bottles bought from estates and new bottles from its own
cellar. Its own bottles go on sale only once the cellar master signs the label.
To tell them apart, the shop can look for its own cellar stamp, add a separate
"house bottle" sticker, or keep a list in the back office that a branch shop
never sees. In this picture: the estate bottles are historical tags, the house
bottles are engine tags, the signature is `[valid]`, the cellar stamp is the
`Release tooling:` trailer, the sticker is a dedicated marker line, and the
back-office list is evidence outside the tag, such as Git notes or a local
journal.

#### Options for Q01

- Option A: the `Release tooling:` trailer identifies an engine tag; a
  standalone `[valid]` line after it validates the tag (current design).
  - pro: uses exactly the annotation content the umbrella already specifies
    for item 5; no new contract.
  - pro: travels with the tag to every clone; none of the three consumers has
    the trailer today, so no migration.
  - con: a diagnostic line now also decides eligibility; a hand-written tag
    copying the trailer becomes ineligible until it gets `[valid]`.
- Option B: item 5 writes an additional dedicated line, such as
  `Release-Engine: 1`, and only that line identifies engine tags.
  - pro: separates provenance text from the eligibility contract, with room for
    a format version.
  - con: a second marker for item 5 to write and keep consistent, with no
    present need for versioning.
- Option C: record validity outside the annotation, in Git notes or a
  dedicated ref namespace.
  - pro: no change to the annotation text.
  - con: notes and extra refs are not fetched by default, so another clone
    would lose the evidence, which decision 34 forbids.

#### Recommended option for Q01 (with arguments for this choice)

Option A: the trailer is already a required part of every engine annotation
and is placed before the point where `post` appends `[valid]`, so reading both
from the tag needs no new writer obligation and works in any clone. The only
failure mode is conservative: a tag that imitates the trailer is excluded until
validated, never promoted. Matching uses whole lines at the umbrella's
position (the trailer as the last nonempty line, or followed only by
`[valid]`), never a substring found in the notes; a trailer line elsewhere
makes the tag ambiguous. (Matching rule added after review round 1.)

#### Answer to Q01: option A (with reason why it must be accepted as the answer)

Option A: it meets decision 34 with evidence that every clone already
receives, adds nothing for item 5 to write, and errs only toward excluding a
tag.

User decision: confirmed - Option A, as recommended: an annotated tag whose
whole-line `Release tooling:` trailer sits at the umbrella's position is an
engine tag, eligible only when a standalone `[valid]` line follows that
trailer; other stable tags are historical and eligible; a misplaced or repeated
trailer makes the tag ambiguous and never a baseline. Decided by the user on
2026-11-05 during the explanation that followed the design review round 2
convergence, with no further comment.

### Q02: How strictly the ancestry rule treats conflicting histories

Question description: the requirement asks for a documented deterministic
ancestry rule and for conflicting tags to be reported rather than guessed. The
design fails when the reachable eligible releases have several independent
tips (merged parallel histories), or when the nearest release has a lower
version than an older one. The question is whether those cases fail or
resolve to a chosen baseline with a warning.

#### BBQ for Q02

A hiker follows trail markers back to the last shelter. If two trails merge and
each has its own nearest shelter, or if the nearest shelter claims to be older
than one further back, the hiker can stop and ask, or pick one and walk on. In
this picture: the trail is the commit ancestry, the shelters are eligible
release tags, the two merged trails are parallel tagged histories, the
misnumbered shelter is a version inversion, and picking one is choosing a
baseline with a warning.

#### Options for Q02

- Option A: fail on several independent tips and on a version inversion,
  naming the tags (current design).
  - pro: never guesses a range that changes a changelog or release notes.
  - pro: the histories of llm-shared, my-project and workspace-halo are single
    increasing chains, so nothing they do today fails.
  - con: a project that merged a tagged side branch must clean up or wait for
    the later maintenance-release policy.
- Option B: choose the independent tip with the highest version and report the
  others as warnings.
  - pro: always produces a range.
  - con: a merged maintenance release can silently drop from or duplicate in
    the generated notes.
- Option C: choose the tip with the latest commit date.
  - pro: simple to explain.
  - con: dates are not ancestry and can be rewritten; the result depends on
    clocks, not on the graph.

#### Recommended option for Q02 (with arguments for this choice)

Option A: the selector feeds changelogs and release notes, where a wrong
baseline is a silent content error. Releases only happen on `main`, by
umbrella decision 23, and lower maintenance releases need a later policy, by
decision 33. So the failing shapes come only from legacy history, which
deserves a report.

#### Answer to Q02: option A (with reason why it must be accepted as the answer)

Option A: it reports every case the rule cannot decide, costs nothing for the
known consumers, and leaves maintenance branches to their own later policy.

User decision: confirmed - Option A, as recommended: the selection fails with
status 2, naming the tags, when the reachable eligible releases have several
independent tips or when the nearest release has a lower version than an older
candidate; no baseline is chosen by highest version or by date. Decided by the
user on 2026-11-05 during the explanation that followed the design review
round 2 convergence, with no further comment.

### Q03: How instruction-driven readers reach the range selector

Question description: today `prepare-release` and `prepare-release-notes`
instructions, and `tools/prepare_release/prepare_release_plan_git.py`, run
`git describe --tags --abbrev=0`. Python callers can import the selector, but
an agent following an instruction needs a command. The design adds a read-only
`versions range [<tag>]` operation printing `target`, `baseline`, `range` and
`commits`. The question is where that command lives.

#### BBQ for Q03

A library adds a new catalogue. Staff can query it from their desks, but
visitors need a public terminal. The terminal can sit at the version-sources
desk, get its own kiosk, or wait until the reading room is renovated. In this
picture: the catalogue is the range selector, the staff desks are in-process
callers (items 4, 5 and 7), the visitors are instruction-driven readers, the
version-sources desk is the `versions` command, the kiosk is a separate
top-level command, and the renovation is item 7's adoption.

#### Options for Q03

- Option A: a `versions range [<tag>]` operation of the existing `versions`
  handler (current design).
  - pro: one handler and one help surface for version and tag questions.
  - pro: item 7 can switch instructions to a command that already exists.
  - con: `versions` grows beyond the four operations the requirement lists.
- Option B: a separate top-level `range` command.
  - pro: keeps `versions` limited to source synchronization.
  - con: another handler and argument contract for one read.
- Option C: Python interface only; item 7 adds whatever command it needs.
  - pro: the smallest item 2 surface.
  - con: item 7 would design a second entry around the same rule, and the
    unfiltered `describe` query stays in instructions longer.

#### Recommended option for Q03 (with arguments for this choice)

Option A: the requirement makes this item expose the selector to release-notes
and release-plan callers, and some of those callers are instructions. A read
operation under `versions` reuses the handler, its argument validation and its
output contract.

#### Answer to Q03: option A (with reason why it must be accepted as the answer)

Option A: it gives every reader, Python or instruction, the same rule now, at
the cost of one more read-only operation on an existing handler.

User decision: confirmed - Option A, as recommended: the read-only
`versions range [<stable tag>]` operation of the `versions` handler prints the
`target`, `baseline`, `range` and `commits` lines from the shared selector;
item 7 switches the instruction-driven readers to it. Decided by the user on
2026-11-05 during the explanation that followed the design review round 2
convergence, with no further comment.

### Q04: The public status for an incomplete restoration

Question description: Q12 of the requirement asks that a restoration that
cannot complete fails with a status distinct from an ordinary failure. Item 1's
renderer and launchers expose only 0, 1 and 2 and turn any other status into 1.
The design adds a public status 3. The question is whether to extend the
foundation's status contract or to signal the case another way.

#### BBQ for Q04

A fire panel has three lights: normal, fault and wrong input. A fourth
situation, "the sprinklers ran and some rooms are still wet", can get its own
red light, or share the fault light with a printed note underneath. In this
picture: the panel is item 1's public status contract, the lights are statuses
0, 1 and 2, the wet rooms are sources left unrestored, the red light is status
3, and the printed note is a stable diagnostic line on stderr.

#### Options for Q04

- Option A: add public status 3 in the renderer and launchers (current design).
  - pro: a build adapter or item 5 can branch on the exit code alone.
  - pro: matches the requirement's wording of a distinct status.
  - con: changes item 1's documented contract and its tests; every caller must
    treat 3 as a recovery stop.
- Option B: keep status 1 and print a stable `Restoration incomplete:` line
  on stderr.
  - pro: no foundation change.
  - con: does not meet the requirement's distinct public status; callers must
    parse stderr, and batch scripts usually check only the exit code.
- Option C: status 3 only in the in-process interface; the CLI returns 1 with
  the diagnostic.
  - pro: item 5 gets the distinction without changing the launchers.
  - con: does not meet the requirement for the command itself; a person or
    script running it cannot tell the two failures apart by status.

#### Recommended option for Q04 (with arguments for this choice)

Option A: it is the only option that gives both the command and in-process
callers the distinct status the requirement asks for. The case is the one where
a user must act before anything else runs, and an exit code is the signal every
caller reads. The foundation change is local to the renderer and the launcher
boundary, and its contract and tests are updated explicitly. (B and C labeled
as not meeting the requirement after review round 1.)

#### Answer to Q04: option A (with reason why it must be accepted as the answer)

Option A: it satisfies the requirement literally and gives every caller a
signal it cannot miss.

User decision: confirmed - Option A, as recommended: item 1's renderer and
launcher boundary accept public status 3 for an incomplete restoration, for
both the command and in-process callers; other unknown statuses still become
1, and item 1's contract and tests change explicitly. Decided by the user on
2026-11-05 during the explanation that followed the design review round 2
convergence, with no further comment.

### Q05: When `set` takes the lock relative to its validation

Question description: requirement Q11 makes a standalone `set` hold the
operation lock from capture to restoration. Taking the lock needs a prepared
artifact home. The design plans once without the lock, so an invalid target or
an unsupported arrangement fails without creating the home or a lock record,
then plans again under the lock, and takes the lock even when the first plan
is empty. The question is whether to keep that double plan.

#### BBQ for Q05

A locksmith can check your paperwork at the counter before opening the
workshop, then check the door again inside; or open the workshop first and
check everything there once. Checking only at the counter and skipping the
inside check saves time but misses a door someone else just changed. In this
picture: the counter check is the plan without the lock, opening the workshop
is preparing the artifact home and taking the lock, the inside check is the
plan under the lock, and the changed door is a source edited by another
transition.

#### Options for Q05

- Option A: plan without side effects, then lock and plan again; always lock
  for `set`, even when the first plan is empty (current design).
  - pro: a well-formed target that fails source validation, such as an
    unsupported workspace or a release-only refusal, leaves no artifact home
    or lock record.
  - pro: the authoritative plan sees the files as they are once the lock is
    held, and a clean result is never reported during another transition.
  - con: reads every source in one more phase.
- Option B: lock first, then plan once.
  - pro: one plan phase fewer.
  - con: a well-formed target that fails source validation prepares the
    artifact home and writes a lock record before failing. A malformed target
    is rejected by the argument validator under either option.
- Option C: as option A, but return `unchanged` without the lock when the first
  plan is empty.
  - pro: no bookkeeping for the common Step 12 re-run.
  - con: can report a clean state while another `set` is half-way through.

#### Recommended option for Q05 (with arguments for this choice)

Option A: source validation failures, the most likely rejections of a valid
command line, leave the project untouched, and the extra plan costs little
against the files involved. The authoritative capture and plan still happen
under the lock, as requirement Q11 asks, and always locking keeps the meaning
of a clean `set` exact. (Comparison with B corrected after review round 1.)

#### Answer to Q05: option A (with reason why it must be accepted as the answer)

Option A: it keeps source-validation failures artifact-free and makes every
`set` result reflect a state no other transition is changing.

User decision: confirmed - Option A, as recommended: `set` first plans without
a lock or artifact, then always prepares the artifact home and takes the lock,
even after an empty first plan, checks for transition evidence and plans again;
only the plan under the lock is authoritative. Decided by the user on
2026-11-05 during the explanation that followed the design review round 2
convergence, with no further comment.

### Q06: What happens after a `set` process is killed mid-transition

Question description: a killed process leaves its lock record and its recovery
evidence directory. Item 1's lock recovers a proven dead owner, but the
sources may be half-written. The design stops the next `set` with status 2,
naming the evidence, and leaves restoration to a person; read commands warn.
The question is whether this item should restore automatically or provide a
recovery command.

#### BBQ for Q06

A power cut stops a painter half-way through relabeling the shelves, with the
old labels kept in a box. The next painter can refuse to start until someone
sorts the box, put the old labels back automatically, or follow a printed
procedure for sorting it. In this picture: the power cut is a killed process,
the box of old labels is the recovery evidence, refusing to start is the status
2 stop, putting labels back automatically is an automatic restore, and the
printed procedure is a `versions recover` command.

#### Options for Q06

- Option A: stop the next `set` until a person handles the evidence; read
  commands warn (current design).
  - pro: nothing guesses which state the user wants after an interruption.
  - pro: no new command or automatic write in this item.
  - con: the user restores or deletes the evidence by hand.
- Option B: the next `set` restores the evidence automatically when every
  written file still matches what the dead transition wrote, then continues.
  - pro: the common case recovers without a person.
  - con: decides for the user that the old state is wanted, and adds a write
    path that runs at the start of an unrelated transition.
- Option C: add a `versions recover` operation that restores the evidence
  after the same checks, and point the stop diagnostic at it.
  - pro: an explicit, repeatable recovery with the same verification.
  - con: one more mutating operation to design and test now, while item 5 will
    design lifecycle recovery for the same evidence.

#### Recommended option for Q06 (with arguments for this choice)

Option A: an interrupted standalone `set` is rare, the evidence keeps every
original byte, and item 5 designs lifecycle recovery next. Stopping with a
precise diagnostic is safe now and leaves room for one shared recovery command
later.

#### Answer to Q06: option A (with reason why it must be accepted as the answer)

Option A: it never loses or overwrites the user's files after an interruption
and avoids designing recovery twice.

User decision: confirmed - Option A, as recommended: interrupted or unreadable
transition evidence stops the next `set` with status 2, naming the evidence
directory, and read commands warn; a person restores or removes it by hand; no
automatic restore and no recovery command in this item. Decided by the user on
2026-11-05 during the explanation that followed the design review round 2
convergence, with no further comment.

### Q07: Who keeps the recovery evidence when item 5 calls the primitive

Question description: requirement Q12 leaves to this design how recovery
evidence interacts with item 5's encompassing transaction. Item 5 must capture
managed-file bytes before its first write and may need to undo the version
change after later steps fail. The design lets item 5 pass its held lock,
checked against the current project, and its transaction identity; the
primitive writes its evidence in this project's artifact home under that
owner, keeps it after success and returns a handle that restores the sources
later. The question is how the two transactions share that evidence.

#### BBQ for Q07

A contractor renovating a kitchen hires a plumber. The plumber photographs the
old pipes before starting. The plumber can file the photos on the site's
shelf under the contractor's job number, throw them away when done, or take
none because the contractor already photographed everything. In this picture:
the contractor is item 5's release transaction, the plumber is the version
primitive, the photos are recovery evidence, the site's shelf is this
project's artifact home, and the job number is item 5's transaction identity.

#### Options for Q07

- Option A: item 5 supplies its held lock and transaction identity; the
  primitive writes evidence in this project's artifact home owned by that
  identity, keeps it on success and returns a restore handle (current design).
  - pro: one capture serves both the primitive's own restoration and item 5's
    later rollback.
  - pro: one restoration routine for both cases.
  - con: item 5 must manage that evidence's lifetime.
- Option B: the primitive always deletes its evidence on success; item 5
  captures the same files separately before calling it.
  - pro: no lifetime shared across items.
  - con: two captures of the same files and two restoration routines that can
    diverge.
- Option C: when item 5 calls it, the primitive writes no evidence and relies on
  item 5's record.
  - pro: one capture.
  - con: the primitive's own restoration would depend on a record it does not
    own, and the standalone and lifecycle paths would behave differently.

#### Recommended option for Q07 (with arguments for this choice)

Option A: item 5 needs exactly the evidence this primitive already produces,
and sharing it avoids a second capture and a second restoration routine. Item 5
keeps control of retention, as the requirement leaves it. Binding the lock and
the evidence to the current project's artifact home, and recording the owner in
the evidence, keeps an abandoned transaction from passing as the current one.
(Project binding and evidence ownership added after review round 1.)

#### Answer to Q07: option A (with reason why it must be accepted as the answer)

Option A: it gives both transactions one source of truth for the original
bytes, with retention decided by the caller that owns the release.

User decision: confirmed - Option A, as recommended: item 5 supplies its held
lock, checked against this process and project, and its transaction identity;
the primitive writes evidence owned by that identity in this project's
artifact home, keeps it on success, returns a restore handle, and never
removes lifecycle-owned evidence; item 5 deletes it when its transaction ends.
Decided by the user on 2026-11-05 during the explanation that followed the
design review round 2 convergence, with no further comment.

### Q08: How adapters locate and rewrite owned values

Question description: the release dependency group is empty, so the engine
runs on the standard library. `tomllib` reads TOML but cannot write it; `json`
and `xml.etree` lose formatting. The design parses each file with the standard
library for meaning, locates the owned values as byte spans with small
format-aware scanners (and `expat` byte offsets for XML), checks that the span
holds the parsed value, and replaces only those bytes. The question is whether
to keep that approach or add format-preserving libraries.

#### BBQ for Q08

To correct one number on a printed form, you can use correction tape on that
number only, retype the whole form in a new program, or search the page for
anything that looks like the old number. In this picture: the printed form is
a manifest or lock file, the number is the version field, correction tape is a
byte-span replacement checked against a parser, retyping is a
format-preserving library that rewrites the file, and searching the page is a
plain regular expression per format.

#### Options for Q08

- Option A: standard-library parsing plus byte-span replacement, cross-checked
  against the parsed value (current design).
  - pro: no release dependency; readiness and setup stay unchanged.
  - pro: every byte outside the owned spans is unchanged by construction,
    including line endings.
  - con: rare spellings (dotted TOML keys, inline tables, comments inside an
    XML element) fail as unsupported instead of being handled.
- Option B: add format-preserving libraries such as `tomlkit` to the `release`
  group.
  - pro: handles more TOML spellings.
  - con: a new dependency in every consumer's release runtime and readiness
    closure; round-trip fidelity is still the library's promise, not a byte
    guarantee; no equivalent exists in the standard library for XML.
- Option C: one regular expression per format, without parsing.
  - pro: the smallest code.
  - con: cannot tell the root `version` from a dependency's `version`, the very
    defect the requirement lists for `t_build_npm.bat`.

#### Recommended option for Q08 (with arguments for this choice)

Option A: it gives the byte-for-byte guarantee the acceptance criteria ask for
without changing the release runtime, and every unsupported spelling fails
before any write with a remedy.

#### Answer to Q08: option A (with reason why it must be accepted as the answer)

Option A: the parser decides meaning, the span decides bytes, and no
dependency is added to any consumer.

User decision: confirmed - Option A, as recommended: each format is parsed with
the standard library for meaning, a format-aware scanner (with `expat` byte
offsets for XML) locates the owned field's byte span, the span must equal the
parsed value, and only those bytes change; unsupported spellings fail before
any write with a remedy; no release dependency is added. Decided by the user on
2026-11-05 during the explanation that followed the design review round 2
convergence, with no further comment.

### Q09: How pattern sources match files with CRLF line endings

Question description: pattern sources compile with `re.MULTILINE`. On a file
with CRLF line endings, a pattern such as the umbrella's
`^APP_SERVICE_VERSION=(.+)$` captures the carriage return, because `.` matches
it and `$` stops before LF. The design matches against the decoded text with
each CRLF presented as LF and maps the capture span back to the original
bytes. The question is whether to keep that or make users write CRLF-aware
patterns.

#### BBQ for Q09

A clerk copies a reference number from a typed card; some typewriters leave an
invisible mark after every line. The clerk can ignore the mark while reading,
ask every form author to describe the mark in their instructions, or refuse
cards from those typewriters. In this picture: the clerk is the pattern
matcher, the invisible mark is the carriage return, ignoring it while reading
is presenting CRLF as LF, the form author's instructions are the declared
pattern, and refusing cards is rejecting CRLF files.

#### Options for Q09

- Option A: match on a view where CRLF reads as LF and map spans back (current
  design).
  - pro: the umbrella's example pattern works on both line endings.
  - pro: the file keeps its CRLF bytes.
  - con: a pattern that deliberately matches `\r` behaves differently.
- Option B: match the raw text; a capture containing `\r` is not a valid
  version and fails with a hint to use `([^\r\n]+)`.
  - pro: no transformation of the text.
  - con: patterns copied from the umbrella fail on Windows files.
- Option C: reject pattern files with CRLF line endings.
  - pro: simple.
  - con: Windows repositories commonly keep CRLF files.

#### Recommended option for Q09 (with arguments for this choice)

Option A: pattern sources mostly serve Windows projects, and the common
`(.+)$` shape should work there; the remapping is local to pattern matching and
leaves the file's bytes untouched.

#### Answer to Q09: option A (with reason why it must be accepted as the answer)

Option A: one pattern works on either line ending, and nothing is written but
the captured version.

User decision: confirmed - Option A, as recommended: pattern sources match a
view of the decoded text in which each CRLF reads as LF, the capture span is
mapped back to the original bytes, and only the captured version is replaced,
so the file keeps its line endings. Decided by the user on 2026-11-05 during
the explanation that followed the design review round 2 convergence, with no
further comment.

### Q10: Which forms each built-in adapter allows

Question description: the requirement fixes the default forms and says an
unsupported form and format combination fails before any write, but leaves the
combinations to design. The design allows only `core` for Python, all three
forms for npm, only `snapshot` for Maven, and any form for a pattern source.
The question is whether Maven should also accept `core` or `release-only`.

#### BBQ for Q10

A bakery labels loaves either "tomorrow's batch" or with the final price. Some
shelves can show the batch label, some cannot, and one shelf could show either
if the manager allows it. In this picture: the batch label is the `-SNAPSHOT`
form, the final price is the release core, the shelves are the adapters, the
Python shelf cannot show batch labels, and the manager's permission is a
configured form override.

#### Options for Q10

- Option A: Python `core` only, npm all three, Maven `snapshot` only, pattern
  sources any form (current design).
  - pro: a Maven snapshot build can never publish release coordinates.
  - pro: matches every default and the requirement's explicit npm exception.
  - con: a Maven project that never deploys snapshots cannot drop the suffix.
- Option B: as option A, but Maven also accepts `core`.
  - pro: flexibility for Maven projects that only build releases.
  - con: a snapshot build would produce artifacts named like the release.
- Option C: every adapter except Python accepts every form.
  - pro: uniform configuration.
  - con: opens the release-coordinate risk for Maven with no consumer asking.

#### Recommended option for Q10 (with arguments for this choice)

Option A: each restriction reflects a format rule or a publication risk, and
none blocks a known consumer; a Maven need for `core` can be added later with
its own justification.

#### Answer to Q10: option A (with reason why it must be accepted as the answer)

Option A: it keeps every allowed combination safe to publish and matches the
requirement's defaults and its single npm exception.

User decision: confirmed - Option A, as recommended: Python allows only `core`;
npm allows `release-only`, `core` and `snapshot`; Maven allows only `snapshot`;
a pattern source takes its declared form; any other configured form fails
configuration validation before a command runs. Decided by the user on
2026-11-05 during the explanation that followed the design review round 2
convergence, with no further comment.

### Q11: Which `package-lock.json` formats the npm adapter supports

Question description: the design currently supports lock formats 1, 2 and 3.
Format 1 comes from npm 6 and older; workspace-halo uses format 3. Requirement
Q10 makes the compatibility guarantee rest on evidence captured with each
supported tool version, which for format 1 means fixtures produced with an
obsolete npm. Reviewing the design, the writer finds format 1 support costly
for no known consumer. The question is which formats to support.

#### BBQ for Q11

A garage services three generations of one car model. The oldest needs special
tools nobody in the shop still owns, and no customer drives one. The garage can
keep the old tools anyway, or tell owners of the oldest model to upgrade first.
In this picture: the generations are lock formats 1, 2 and 3, the special
tools are fixtures captured with npm 6, the customers are the consumers, and
upgrading first is regenerating the lock with a current npm.

#### Options for Q11

- Option A: support formats 1, 2 and 3 (current design text).
  - pro: works on very old projects.
  - con: requires compatibility fixtures from npm 6 and tests for a format no
    consumer uses.
- Option B: support formats 2 and 3; format 1 fails before any write with the
  remedy to regenerate the lock with npm 7 or later.
  - pro: evidence comes from npm 7 and later, the versions that write formats
    2 and 3.
  - pro: every known consumer is covered.
  - con: a project still on npm 6 must regenerate its lock first.
- Option C: support format 3 only.
  - pro: the smallest surface.
  - con: format 2 locks from npm 7 and 8 are still common and were written to
    stay readable by both old and new npm.

#### Recommended option for Q11 (with arguments for this choice)

Option B: it covers every npm that writes formats 2 or 3, with evidence that
can still be produced, and the failure for format 1 is explicit and fixable.
Choosing it amends the design's npm section at consolidation.

#### Answer to Q11: option B (with reason why it must be accepted as the answer)

Option B: every supported format can be backed by real tool evidence, and the
only excluded format belongs to an npm generation no consumer uses.

User decision: confirmed - Option B, as recommended: the npm adapter supports
lock formats 2 and 3; a format 1 lock fails before any write, with the remedy
to regenerate it with npm 7 or later. Consolidation changes the npm section
from formats 1, 2 and 3 to formats 2 and 3 and adds an acceptance row for a
format 1 lock rejected before any write. Decided by the user on 2026-11-06
during the explanation that followed the design review round 2 convergence,
with no further comment.

### Q12: How Maven internal dependencies are identified

Question description: identifying internal references is design work. The
design treats a dependency or dependency-management entry as internal when its
`artifactId` and group match a reactor module, accepting a literal group or
exactly `${project.groupId}`; an entry naming a module's `artifactId` with any
other group expression fails as ambiguous. Module coordinates themselves must
be literal or inherited. The question is how far identification resolves
properties.

#### BBQ for Q12

A mail room delivers internal mail by department name. Some envelopes say "our
own department" instead of its name, some use a code from a lookup sheet. The
clerk can accept the name and "our own department", read every lookup sheet,
or treat anything but the printed name as outside mail. In this picture: the
department name is a literal `groupId`, "our own department" is
`${project.groupId}`, the lookup sheet is a project-defined property, and
outside mail is an external dependency.

#### Options for Q12

- Option A: literal groups and exactly `${project.groupId}`; a property group
  on an entry naming a module's `artifactId` fails as ambiguous (current
  design).
  - pro: covers the common Maven idiom without a property model.
  - pro: never misses an internal reference silently.
  - con: a reactor using a custom group property must write the group
    literally.
- Option B: literal groups only; any property group is treated as external.
  - pro: the simplest rule.
  - con: a `${project.groupId}` sibling dependency would keep an old version
    silently, the stale reference AC9 forbids.
- Option C: resolve properties declared in the reactor's POMs for coordinates.
  - pro: covers custom group properties.
  - con: brings in the property resolution the requirement kept out of scope,
    including profiles and inheritance order.

#### Recommended option for Q12 (with arguments for this choice)

Option A: it recognizes the one group expression that always names the
declaring project, fails loudly on everything else that could be internal, and
keeps property resolution out of the engine.

#### Answer to Q12: option A (with reason why it must be accepted as the answer)

Option A: it finds every internal dependency that common reactors write and
refuses the rest instead of leaving a stale version.

User decision: confirmed - Option A, as recommended: a dependency or
dependency-management entry is internal when its `artifactId` and its literal
group, or exactly `${project.groupId}`, identify a reactor module; an entry
naming a module's `artifactId` with any other group expression fails as
ambiguous; property resolution stays out of the engine. Decided by the user on
2026-11-06 during the explanation that followed the design review round 2
convergence, with no further comment.

### Q13: Syntax that declares participating component roots

Question description: the requirement leaves the component-root declaration
syntax to this design; item 6 writes it and item 2 reads it. The design uses a
`[component:<id>]` family with a required `root` managed path, so the id names
the component in diagnostics and the path goes through item 1's managed-path
validation. The question is which syntax item 6 should write.

#### BBQ for Q13

A building directory can list each company on its own plaque with a name and a
floor, write all floors on one plaque, or use the floor itself as the plaque
title. In this picture: the directory is `.release.ini`, a plaque per company is
a `[component:<id>]` section, the floor is the `root` path, the single plaque is
one list-valued key, and the floor as title is a section named by its path.

#### Options for Q13

- Option A: `[component:<id>]` with `root = <relative path>` (current design).
  - pro: each root is a managed-path value, validated like every other path.
  - pro: a stable id for diagnostics and for item 6 to update one entry.
  - con: two lines per component.
- Option B: one `[components]` section with `roots = frontend, backend`.
  - pro: compact.
  - con: a list inside one value needs its own splitting and quoting rules, and
    paths with commas or spaces become fragile.
- Option C: the path as the section instance, `[component:frontend]`, with no
  key.
  - pro: one line per component.
  - con: section names cannot hold `]` or surrounding spaces, and the path
    escapes item 1's managed-path rule.

#### Recommended option for Q13 (with arguments for this choice)

Option A: it reuses the schema registry's family and managed-path features
unchanged, keeps paths as ordinary validated values, and gives item 6 a stable
key per component.

#### Answer to Q13: option A (with reason why it must be accepted as the answer)

Option A: it needs no new parsing rule and validates every root with the same
boundary as every other configured path.

User decision: confirmed - Option A, as recommended: item 6 writes and item 2
reads one `[component:<id>]` section per participating component root, with a
required `root` managed path; the id names the component in diagnostics.
Decided by the user on 2026-11-06 during the explanation that followed the
design review round 2 convergence, with no further comment.

### Q14: Scope of a built-in form override

Question description: `[source:npm] form = snapshot` overrides the npm form.
With declared components, a project could have npm sources at several roots.
The design applies a built-in override to that adapter at every participating
root and defers per-component overrides. The question is whether v0.14.0 needs
per-component forms.

#### BBQ for Q14

A school sets one dress code per sport. A team could ask for its own kit, which
means one rule per team instead of per sport. In this picture: the sport is an
adapter such as npm, the dress code is the form, a team is a component root,
and its own kit is a per-component form override.

#### Options for Q14

- Option A: one override per adapter, applied at every participating root
  (current design).
  - pro: one rule to read; no consumer has two npm roots needing different
    forms.
  - con: a future project mixing a Marketplace extension and a snapshot-tolerant
    package in one repository must wait.
- Option B: also allow a form key in `[component:<id>]` per adapter, overriding
  the project-wide one.
  - pro: covers mixed repositories now.
  - con: more configuration and validation for a case no consumer has.
- Option C: per-component forms only, no project-wide override.
  - pro: explicit everywhere.
  - con: repeats the same form at every root of a simple project.

#### Recommended option for Q14 (with arguments for this choice)

Option A: it covers all three consumers with the simplest rule, and option B
can be added later without changing option A's syntax.

#### Answer to Q14: option A (with reason why it must be accepted as the answer)

Option A: it keeps configuration minimal now and leaves a compatible extension
for a real mixed repository later.

User decision: confirmed - Option A, as recommended: a built-in form override
such as `[source:npm] form = snapshot` applies to that adapter at every
participating root; per-component forms are deferred until a real mixed
repository needs them. Decided by the user on 2026-11-06 during the
explanation that followed the design review round 2 convergence, with no
further comment.

### Q15: How `versions list` finds undeclared nested candidates

Question description: requirement Q07 has `list` report undeclared nested
component candidates under the same exclusions as detection. The design uses
one Git listing of tracked files plus untracked files that no ignore rule
matches, finds manifest files outside the participating roots and reactor
modules, and skips nested
repositories and a fixed list of excluded directory names. The question is
which file inventory candidate discovery uses.

#### BBQ for Q15

An inspector counts the rooms of a building from the owner's floor plan, from
walking every corridor, or from the floor plan plus any rooms built since. In
this picture: the floor plan is Git's index, walking every corridor is a
filesystem walk, the rooms built since are untracked files, and the rooms the
owner sealed off are ignored directories.

#### Options for Q15

- Option A: one Git listing of tracked files plus untracked files that no
  ignore rule matches, with the fixed excluded names (current design).
  - pro: one process, no tree walk; `.gitignore` already hides
    `node_modules`, virtual environments and build output.
  - pro: shows a new component before it is committed.
  - con: an ignored untracked nested project is never reported, while a
    tracked file stays listed even if an ignore rule matches it later.
- Option B: tracked files only.
  - pro: reports only what the repository already contains.
  - con: a new, not yet committed component stays invisible to setup.
- Option C: a filesystem walk with the excluded names.
  - pro: independent of Git state.
  - con: walks large ignored trees unless the list is complete, and reports
    ignored projects the user deliberately keeps out.

#### Recommended option for Q15 (with arguments for this choice)

Option A: it is bounded by one Git call, follows the user's own ignore rules,
and still shows candidates that setup should offer before their first commit.

#### Answer to Q15: option A (with reason why it must be accepted as the answer)

Option A: it finds what a person would expect to see, with a fixed cost, and
respects what the repository deliberately ignores.

User decision: confirmed - Option A, as recommended: candidate discovery uses
one Git listing of tracked files plus untracked files that no ignore rule
matches, skips nested repositories, and excludes the fixed directory names and
the artifact home. Decided by the user on 2026-11-06 during the explanation
that followed the design review round 2 convergence, with no further comment.

### Q16: What the anchor's first line may hold after the token

Question description: the requirement says the rest of the first line, after
`--`, is the title. It does not say what happens when text follows the token
without `--`, such as `0.1.0-SNAPSHOT Initial`. The design treats that as a
malformed anchor. The question is whether to reject it, read it as a title or
ignore it.

#### BBQ for Q16

A shipping label has a tracking number, then "--", then the recipient. A label
with a name right after the number, without the dash, can be refused at the
counter, read as the recipient anyway, or have the name ignored. In this
picture: the tracking number is the version token, the "--" is the title
separator, the recipient is the title, and the counter is the anchor parser.

#### Options for Q16

- Option A: anything after the token other than whitespace, `--` and a title
  makes the anchor malformed (current design).
  - pro: one unambiguous shape that item 5 can rely on for titles.
  - con: an existing file using another separator fails until edited.
- Option B: treat any text after the token as the title, with or without
  `--`.
  - pro: lenient with hand-written files.
  - con: a typo such as `0.14.0 -SNAPSHOT` silently becomes version `0.14.0`
    with a title.
- Option C: ignore text after the token unless it starts with `--`.
  - pro: never fails on the first line.
  - con: silently drops what the author meant as a title.

#### Recommended option for Q16 (with arguments for this choice)

Option A: the anchor is authoritative, so a first line the parser cannot read
in exactly one way should fail with a remedy; the three consumers already use
`<token> -- <title>`.

#### Answer to Q16: option A (with reason why it must be accepted as the answer)

Option A: it turns a possible version typo into a visible error instead of a
silent release under the wrong number.

User decision: confirmed - Option A, as recommended: the anchor's first line
holds the token, optionally followed by whitespace, `--` and the title;
anything else after the token makes the anchor malformed, which fails with
status 2 and a remedy before any write. Decided by the user on 2026-11-06
during the explanation that followed the design review round 2 convergence,
with no further comment.

### Q17: When a verified version transition is complete, and what a cleanup failure reports

Question description: after a `set` verifies the new versions, it removes its
recovery evidence and releases the lock. If removing the evidence fails half
way, some originals are already gone, so a rollback can no longer be
promised; the same holds when releasing the lock fails afterwards. The design
needs a point after which the transition counts as done, and a defined result
when cleanup after that point fails. Status 3 stays reserved for an incomplete
restoration. Added after review round 1.

#### BBQ for Q17

A mover finishes unloading, checks every room, and then throws away the
inventory list and returns the keys. If the bin bag tears or the key box is
jammed, the move itself is still done. The crew can sign a "move complete"
sheet before cleaning up, keep the inventory until the customer clears it,
or simply say "all fine" and ignore the torn bag. In this picture: the rooms
are the version sources, the inventory list is the recovery evidence, the keys
are the operation lock, the signed sheet is a durable completion marker, and
"all fine" is a success status that hides the residue.

#### Options for Q17

- Option A: after verification, durably record a `complete` state in the
  evidence manifest; before that point any failure restores from the complete
  originals; after it, cleanup deletes the originals and then the manifest, and
  a cleanup or lock-release failure returns status 1 stating that the new
  versions are applied and naming the residue, with no rollback. The next
  `set` removes standalone residue marked `complete` and still stops on
  `writing` evidence (current design).
  - pro: a rollback is only ever attempted with complete originals.
  - pro: the next invocation can tell finished residue from an interrupted
    transition.
  - con: one more flushed write per transition, and a nonzero status for a
    transition whose versions were applied.
- Option B: keep the complete evidence after every successful transition until
  an explicit cleanup, by the next `set` or a dedicated action.
  - pro: the originals of the last transition remain available for manual
    comparison.
  - con: every success leaves a copy of every source in the artifact home, and
    the cleanup action becomes part of the user's routine or a new command.
- Option C: after verification, report success with status 0 and only warn on
  stderr when cleanup or lock release fails.
  - pro: callers see success whenever the versions were applied.
  - con: residue and a possibly unreleased lock go unnoticed by callers that
    read only the exit code, and without a marker the next invocation cannot
    tell residue from an interrupted transition.

#### Recommended option for Q17 (with arguments for this choice)

Option A: it draws the line where the originals stop being needed, keeps every
rollback backed by complete evidence, and makes leftovers self-describing for
the next run. A nonzero status after applied versions is honest: the caller
learns that something remains to clean, and the diagnostic says the versions
themselves are in place.

#### Answer to Q17: option A (with reason why it must be accepted as the answer)

Option A: it never promises a rollback it cannot perform, never hides residue,
and lets the next `set` recover automatically from a finished transition while
still stopping on an interrupted one.

User decision: confirmed - Option A, as recommended: after verification, the
transition durably records a `complete` state in the evidence manifest; before
that boundary any failure restores from the complete originals; after it,
cleanup deletes the originals and then the manifest, and a cleanup or
lock-release failure returns status 1 stating that the new versions are
applied and naming the residue, with no rollback; the next `set` removes
standalone residue marked `complete` and still stops on `writing` evidence.
Decided by the user on 2026-11-06 during the explanation that followed the
design review round 2 convergence, with no further comment.
