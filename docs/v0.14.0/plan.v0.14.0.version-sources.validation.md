# v0.14.0 version-sources implementation tracking and validation

No, it is not implemented.

This document tracks the nine steps of the
[implementation plan](plan.v0.14.0.version-sources.md) for item 2 of the
sibling release tooling umbrella. No step has started: the foundation
extensions, the source adapters, the transition, the tag selector, the
commands and the recorded lock evidence are all still to be written.

> Initial-skeleton note: this first version was written by the `write-plans`
> skill, before any implementation check. It fills `Goal for Step N` and
> `Step N improvement expectations`, opens every `Analysis of Step N
> implementation state` with "Not started. Step N is not implemented because
> ...", and fills every other per-step section with the literal placeholder
> that an implementation check later replaces.
>
> Every test this document refers to belongs to llm-shared's own development
> suite, run while llm-shared is changed; no version command, no `brel` and
> no consumer release runs it.
>
> Markdown lint note: never leave a space immediately inside an inline code span
> (MD038); write a needed space as the token `[space]`, as in `` `[space]${x}` ``.
> The empty placeholder ends in `)_.` so the line is not pure italic text (MD036).

---

## File-based IO cost clarification for v0.14.0 version-sources (implementation)

All implementation work must respect the IO classification established in
[the plan](plan.v0.14.0.version-sources.md#file-based-io-cost-clarification-for-v0140-version-sources).
The key constraints carried forward from the plan are:

- `version`, `versions check` and `versions range` read each source file at
  most once, plus one non-recursive listing of the artifact home for leftover
  evidence; `versions list` adds one Git listing and one read per candidate
  manifest file.
- `versions set` reads through one fresh file view per phase (initial plan,
  locked plan, comparison before each replacement, final verification and
  restoration check) and writes evidence before the first overwrite.
- Detection probes fixed file names at participating roots and declared Maven
  modules; no command walks a directory tree.
- Every write goes through `managed_files` (flushed same-parent temporary,
  revalidation, atomic replacement); no version command starts uv, npm, Maven
  or git-cliff, and only `list` and `range` add Git calls of their own.

---

## Complexity Bound Clarification for v0.14.0 (implementation)

The scaling target for all v0.14.0 version-sources code paths is:

- **O(1) amortized per located field**: claims, Maven references and tag
  names go through dictionary lookups, each classified once.
- **O(n) total per phase**: one read and one scan per participating file;
  detection linear in roots, modules and fields; candidate filtering linear in
  the Git listing; selection linear in reachable tags with a fixed number of
  Git calls.

Every implemented step should be reviewed against this bound in its
Performance check section.

---

## Step 1. Foundation extensions for the version domain

### Analysis of Step 1 implementation state

Not started. Step 1 is not implemented because no implementation work has
begun: the parser still rejects operation tokens, status 3 is still
normalized to 1, the lock has no public ownership check and Git has no typed
tag, ancestry, count or listing observation.

### Goal for Step 1

Extend the item 1 foundation where the version domain needs it: trailing
operation tokens with per-handler argument validators carried into the
invocation context, public status 3 at the renderer, the bootstrap and both
launchers, a public `verify_held` lock check bound to the process, project
root and artifact home, and typed Git observations with their programmatic
simulation counterparts.

### Step 1 improvement expectations

- A validator failure, or a token sent to a handler without a validator,
  returns status 2 before any Git process or file read.
- Status 3 passes through every public boundary; any other unknown status is
  still reported and returned as 1.
- `verify_held` rejects a released handle, a handle for another project or
  home, a replaced or retained record and another process's owner.
- `tag_records`, `independent_commits`, `tag_names`, `commit_count` and
  `listing` each issue one Git call with the planned arguments and parse its
  output; a missing `--merged` revision raises `GitRevisionNotFound`, other
  failures stay `GitCommandError`; the simulations answer them from declared
  data.
- `independent_commits` measures its serialized command line in UTF-16 code
  units including the terminating NUL and refuses above 32,767 with status 1
  before starting Git, tested at the boundary with 40- and 64-character ids
  (plan decision Q13).
- One development-suite test checks that the four status sites accept the
  same statuses, `{0, 1, 2, 3}` (plan decision Q12).
- `SHIPPED_HANDLERS` is still empty.

### What was implemented for Step 1

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 1

_(empty — no check has taken place yet.)_.

### Architecture check for Step 1

_(empty — no check has taken place yet.)_.

### Performance check for Step 1

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 1

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 1

_(empty — no check has taken place yet.)_.

---

## Step 2. Version tokens, the anchor document and the source model

### Analysis of Step 2 implementation state

Not started. Step 2 is not implemented because `tools/release_workflow/sources/`
does not exist yet: there is no token grammar, form mapping, file view,
source model, anchor document or adapter tuple.

### Goal for Step 2

Create the shared version token grammar and numeric comparison, the forms with
their expected values and the release-only guard, the read-once file view, the
located-source and edit-composition model, the `version.txt` document parser
and the `anchor` adapter as the first entry of the explicit adapter tuple,
guarded by the completeness test.

### Step 2 improvement expectations

- Malformed tokens (`v0.14.0`, `0.14.0-snapshot`, `0.014.0`) fail with a
  remedy; `0.10.0` compares above `0.9.0`.
- Replacing the anchor token keeps the title, notes, byte-order mark and line
  endings byte for byte; a token followed by text without `--` is malformed.
- The file view loads each path once per phase; disjoint edits compose from
  one original and overlaps are rejected.
- Character spans map to byte spans in one linear walk, correct with accented
  and non-BMP text before and between owned fields.
- `VersionInputs`, `FileCapture`, `SourceChange`, `FileEdit`, `Inventory` and
  `Plan` exist in the model, so no later step's module is needed earlier.
- The completeness test fails for a missing or duplicated adapter module.

### What was implemented for Step 2

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 2

_(empty — no check has taken place yet.)_.

### Architecture check for Step 2

_(empty — no check has taken place yet.)_.

### Performance check for Step 2

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 2

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 2

_(empty — no check has taken place yet.)_.

---

## Step 3. Version configuration, participation, claims and pattern sources

### Analysis of Step 3 implementation state

Not started. Step 3 is not implemented because `.release.ini` still rejects
version sections, and no participating-root list, pattern adapter, claim
registry or candidate listing exists.

### Goal for Step 3

Declare the version schema in `schemas.py` with a deferred validator for the
per-instance rules, compute participating roots, run every adapter over them
in tuple order, register claims by physical path, field and byte span, compose
per-file edits, add the pattern adapter with its CRLF-to-LF view, and list
undeclared candidates from one Git listing.

### Step 3 improvement expectations

- Invalid forms, reserved names, unknown keys and missing pattern keys fail
  configuration for every command, even `version`.
- Duplicate or overlapping claims fail before any write and name both
  claimants; disjoint fields of one file compose.
- Pattern sources match exactly once on LF and CRLF files and keep line
  endings; zero, several or empty captures fail.
- Undeclared candidates are listed as `not-participating undeclared`, with the
  excluded directories and the artifact home skipped, using one Git call.

### What was implemented for Step 3

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 3

_(empty — no check has taken place yet.)_.

### Architecture check for Step 3

_(empty — no check has taken place yet.)_.

### Performance check for Step 3

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 3

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 3

_(empty — no check has taken place yet.)_.

---

## Step 4. Recoverable version transition

### Analysis of Step 4 implementation state

Not started. Step 4 is not implemented because no evidence module or
transition primitive exists yet.

### Goal for Step 4

Add the evidence module and the transition primitive: side-effect-free
planning, the lock (acquired standalone or verified for a lifecycle caller),
the evidence check before every success path, the authoritative locked plan,
evidence before the first overwrite, ordered writes with `version.txt` last,
verification, the completion marker, cleanup, restoration and the five
outcomes, with a restore handle for item 5.

### Step 4 improvement expectations

- Preflight failures leave no artifact home, lock or evidence; a held lock
  fails with status 1.
- An injected failure at any write position restores every replaced file
  (status 1) for the anchor and pattern fixture sets, through a fixture
  registry that Steps 5 to 7 extend (plan decision Q01); an incomplete
  restoration returns status 3 naming each source and its retained copy.
- `set_versions` takes one `TransitionPorts` value (replacement, file and
  directory removal, lock factory, process probe, clock, process id) with
  production defaults (plan decision Q07).
- A clean same-target run reports `unchanged` under the lock without writing a
  source; `writing` evidence stops the next `set`; complete standalone residue
  is removed with a warning.
- A lifecycle call never acquires or releases the supplied lock, keeps its
  `complete` evidence and receives a working restore handle.
- Evidence directories are created exclusively; a name collision takes the
  next suffix and never touches an existing directory, so an earlier restore
  handle stays valid.
- After the completion marker, removal and lock-release failures return
  status 1 with the new versions applied and the residue named; a release
  failure after an incomplete restoration keeps status 3 and every named
  original.

### What was implemented for Step 4

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 4

_(empty — no check has taken place yet.)_.

### Architecture check for Step 4

_(empty — no check has taken place yet.)_.

### Performance check for Step 4

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 4

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 4

_(empty — no check has taken place yet.)_.

---

## Step 5. Python and uv adapter with recorded uv evidence

### Analysis of Step 5 implementation state

Not started. Step 5 is not implemented because no TOML scanner, `python`
adapter, lock evidence recorder or recorded uv evidence exists yet.

### Goal for Step 5

Add the TOML line scanner and the `python` adapter with participation, uv lock
pairing by normalized name and local root source, the registered lock schemas
`(1, 3)` and `(1, 5)`, and the workspace and local-link rejections; record the
uv 0.13.4 compatibility evidence with the recorder outside pytest and check
that the adapter still reproduces each recorded edited pair. In this evidence,
the "before" pair is a `pyproject.toml` and its `uv.lock` as a project has
them before `versions set` changes the version (both at `0.13.0`), and the
edited pair is the same two files after the adapter's version-only edit (both
at `0.14.0`, every other byte unchanged).

### Step 5 improvement expectations

- Tool-only `pyproject.toml` files and their locks are listed as not
  participating; dynamic or missing versions, orphan and ambiguous locks and
  unregistered schemas fail before any write.
- uv workspaces, workspace references and `path` or `file:` links between
  participating components fail naming both; external references stay
  unchanged.
- Only the owned version strings change in `pyproject.toml` and `uv.lock`.
- Every registered pair and layout has a recorded record in which uv's locked
  mode accepted the "before" pair (old version in both files) and then the
  edited pair (new version in both) without changing either file.
- The Python fixture sets join the Step 4 restoration matrix, and a failure at
  every write position restores both files byte for byte (plan decision Q01).

### What was implemented for Step 5

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 5

_(empty — no check has taken place yet.)_.

### Architecture check for Step 5

_(empty — no check has taken place yet.)_.

### Performance check for Step 5

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 5

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 5

_(empty — no check has taken place yet.)_.

---

## Step 6. npm adapter with recorded npm evidence

### Analysis of Step 6 implementation state

Not started. Step 6 is not implemented because no JSON scanner, `npm` adapter
or recorded npm evidence exists yet.

### Goal for Step 6

Add the path-tracking JSON scanner and the `npm` adapter with its three forms,
the `release-only` default, lock formats 2 and 3, the format 1 remedy and the
workspace, local-link and shrinkwrap rejections; add the npm 10.8.3 records to
the evidence file and check them against the adapter.

### Step 6 improvement expectations

- The release-only default keeps the core for a snapshot anchor and refuses a
  downgrade before any write; `check` reports it as drift.
- Formats 2 and 3 change only the top-level `version` where present and
  `packages[""].version`, keeping CRLF; format 1 fails with the npm 7 remedy.
- `workspaces`, local links into participating roots and
  `npm-shrinkwrap.json` fail before any write; Yarn and pnpm locks are never
  read.
- Recorded npm evidence covers formats 2 and 3: npm accepted the "before"
  pair (`package.json` and `package-lock.json` at the old version, as found
  before `versions set`) and the edited pair (both at the new version), and
  the record states that the frozen install does not compare the root version.
- Each npm record also holds the lock-only check: `npm install
  --package-lock-only --offline --ignore-scripts --no-audit --no-fund` left
  the lock of both pairs unchanged and rewrote the manifest-only control's
  root version fields, keeping the lock format, with actual exit codes and
  hashes (plan decision Q05).
- The npm fixture sets join the restoration matrix (plan decision Q01).

### What was implemented for Step 6

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 6

_(empty — no check has taken place yet.)_.

### Architecture check for Step 6

_(empty — no check has taken place yet.)_.

### Performance check for Step 6

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 6

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 6

_(empty — no check has taken place yet.)_.

---

## Step 7. Maven reactor adapter

### Analysis of Step 7 implementation state

Not started. Step 7 is not implemented because no expat scanner or `maven`
adapter exists yet.

### Goal for Step 7

Add the expat byte-offset scanner and the `maven` adapter, split from the
start into `sources/maven.py` (recursive modules, literal or inherited
coordinates) and `sources/maven_references.py` (the internal reference index,
owned project, parent and internal dependency versions, inheritance through
internal parents and the `${project.version}` boundary); add the Maven and
combined five-file fixture sets to the restoration matrix; pin the final
adapter order.

### Step 7 improvement expectations

- Reactor versions and internal parents change; `${project.version}`
  references stay unchanged; external parents, dependencies, plugins and
  properties never change.
- `${revision}`, ranges, profile modules, properties in own coordinates and an
  external-parent POM without its own version fail before any write.
- A declared component that is also a reactor module fails as a conflicting
  claim.
- The registry order is `anchor`, `python`, `npm`, `maven`, `pattern`, and
  `maven_references` is listed as a support module (plan decision Q10).
- The Maven fixture sets and the combined five-file project join the
  restoration matrix (plan decision Q01).

### What was implemented for Step 7

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 7

_(empty — no check has taken place yet.)_.

### Architecture check for Step 7

_(empty — no check has taken place yet.)_.

### Performance check for Step 7

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 7

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 7

_(empty — no check has taken place yet.)_.

---

## Step 8. Tag classification, range selection and the release-version rule

### Analysis of Step 8 implementation state

Not started. Step 8 is not implemented because `tools/release_workflow/tags.py`
does not exist yet.

### Goal for Step 8

Classify stable, snapshot and other tag names, read eligibility from whole
annotation lines, group stable tags into version boundaries, apply the
seven-step ancestry rule with at most four Git calls, and expose the
release-version rule for items 5 and 7.

### Step 8 improvement expectations

- Snapshot markers and unvalidated engine tags never become baselines;
  historical tags without `[valid]` stay eligible.
- A tag target is never its own predecessor; a first release gives the full
  history; conflicting aliases or versions, independent tips, version
  inversions and ambiguous tags after the baseline fail with status 2.
- The release-version rule rejects reserved versions in either spelling and
  targets not higher than every eligible release reachable from `main`.
- Recorded Git calls follow the plan's call table: a missing tag target
  returns status 2 from the one records call, a Git execution failure
  status 1.
- Aliased boundaries follow design decisions Q18 and Q19: a boundary takes
  the most restrictive class of its aliases for a tag target, the
  candidates, the boundaries after the baseline and the release-version
  bound, and the baseline boundary is named by its `vX.Y.Z` alias when it
  has one, otherwise by its `X.Y.Z` alias.

### What was implemented for Step 8

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 8

_(empty — no check has taken place yet.)_.

### Architecture check for Step 8

_(empty — no check has taken place yet.)_.

### Performance check for Step 8

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 8

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 8

_(empty — no check has taken place yet.)_.

---

## Step 9. Version commands, integrated acceptance and documentation

### Analysis of Step 9 implementation state

Not started. Step 9 is not implemented because no `version` or `versions`
handler is shipped, no integrated acceptance runs the design's matrix and the
reference pages still describe a foundation without operations.

### Goal for Step 9

Register the `version` and `versions` handlers with their validators, output
formats and status mapping, run the design's acceptance matrix end to end
through `cli.main` with the shipped registry, prove each command and public
status once through the launcher simulation, and document the commands,
statuses, configuration and limits in the reference pages.

### Step 9 improvement expectations

- The five commands print the design's stdout formats and return its statuses;
  read commands warn about leftover evidence and create nothing.
- Every row of the design's acceptance table passes through `cli.main`
  (parsing, preflight, dispatch, rendering) with whole-tree snapshots, and one
  launcher-simulation case per command and per public status (0, 1, 2 and 3)
  passes through production bootstrap (plan decision Q09).
- The whole-suite coverage walk reports 100% coverage with no duration
  exclusion.
- The reference pages describe the shipped pair, status 3 and the version
  configuration; the Markdown check passes.

### What was implemented for Step 9

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 9

_(empty — no check has taken place yet.)_.

### Architecture check for Step 9

_(empty — no check has taken place yet.)_.

### Performance check for Step 9

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 9

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 9

_(empty — no check has taken place yet.)_.
