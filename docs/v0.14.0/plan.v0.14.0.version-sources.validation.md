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

Yes. Step 1 has been fully implemented.

Every planned file, test and class change is present: operation tokens with
per-handler validators reach the context, status 3 is public at the four
sites with a cross-site test, `OperationLock.verify_held` binds a held lock to
the process, project root and artifact home, and the five typed Git release
observations exist with their simulation counterparts. Code review finding F1
is closed by the user's decision of 2026-11-08 to require Git 2.44 or later,
recorded in the design: from Git 2.44, `for-each-ref` peels a tag of a tag to
its commit in the one tag listing, also after the inner tag's ref is deleted,
so `TagRecord.commit` is always the commit without a second call and without
refusing valid tags. An older Git is refused when the context is created, and
the refusal states the floor, the reason and the remedy to upgrade. The two
new exceptions carry the repository's `Error` suffix
(`GitRevisionNotFoundError`, `GitCommandLineTooLongError`), and the plan uses
these names.

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
  output; a missing `--merged` revision raises `GitRevisionNotFoundError`,
  other failures stay `GitCommandError`; the simulations answer them from
  declared data.
- `independent_commits` measures its serialized command line in UTF-16 code
  units including the terminating NUL and refuses above 32,767 with status 1
  before starting Git, tested at the boundary with 40- and 64-character ids
  (plan decision Q13).
- One development-suite test checks that the four status sites accept the
  same statuses, `{0, 1, 2, 3}` (plan decision Q12).
- `SHIPPED_HANDLERS` is still empty.

### What was implemented for Step 1

- **Operation tokens**: `cli._parse` adds the `operation` positional
  (`nargs="*"`) and uses `parse_intermixed_args`, so options parse the same
  before, between and after the tokens. `cli.Handler.validate_arguments`
  receives the tokens in `_select`, before identity loading and context
  creation; without a validator, any token fails with
  `Release operation '<name>' takes no arguments: ...` (status 2). The tokens
  travel through `InvocationRequest.operation` to
  `InvocationContext.operation`, and the batch-character rule covers them.
- **Public status 3**: `results.render` and `bootstrap.main` accept
  `{0, 1, 2, 3}`; both launchers add
  `if "%_release_status%"=="3" goto cleanup` before the normalization line; 4
  and 23 still become 1 with the original value in the diagnostic.
- **Lock binding**: `OperationLock.verify_held(declaration)` rejects a handle
  that no longer holds the lock, an owner whose process is not the current
  one, another project root and a record outside the declared artifact home,
  then rereads the record under the transition mutex (`_require_owned`), which
  rejects a replaced or retained record; it returns the prepared artifacts.
- **Typed Git observations**: `TagRecord`, `tag_records` (one
  `for-each-ref` with six NUL-terminated fields, `%(*objecttype)` included,
  and an optional `--merged`), `independent_commits` (one
  `merge-base --independent` after the command-line guard), `tag_names`,
  `commit_count` and `listing`; `run` now shares its fixed options with the
  guard's measurement.
- **Peeled commit of a tag of a tag**: the release tooling now requires Git
  2.44 or later (`_MINIMUM_VERSION = (2, 44, 0)`), the first version whose
  `%(*objectname)` peels a tag fully, as `ref-filter.c` shows (v2.43.0 calls
  `get_tagged_oid` once, v2.44.0 calls `peel_iterated_oid`). An annotated
  tag's commit is therefore its dereferenced object, even when the inner
  tag's own ref was deleted; each record keeps its own annotation. A record
  still dereferenced to a tag object can only come from an older Git and is
  refused with the same reason. `GitExecutionContext.create` refuses an older
  Git before any operation: "Git version 2.43.9 at ... is older than required
  2.44.0: release range selection reads every tag with its commit in one
  `git for-each-ref` call, and only Git 2.44 or later peels a tag of a tag to
  its commit there (older Git stops at the inner tag). Upgrade Git to 2.44 or
  later." Git 2.56, installed here, peels a tag of a tag fully in a scratch
  repository probe.
- **Simulation**: `repository_simulation.ReleaseHistory` declares commits
  with parents, `HEAD`, `main`, tags (including `nested_tag`, which carries
  its inner tag's commit) and listing names; `RepositoryObservations` answers
  the five methods by reachability, records each call and keeps the
  production guard; `launcher_simulation` routes the five methods through
  `_patch_release_observations`.
- **Validation evidence**: tests first, `ghog single` on the eight Step 1
  test files failed at collection on the missing API, then passed
  (2026-11-08T16:04 and 16:18). `ghog day --whole-suite`, the command printed
  by `pw scope day`, reported `exit=0` on 2026-11-08T16:20 (check and affected
  tests; the full stage is skipped at the default level). After the Git 2.44
  floor decision, `ghog single` on `test_git_releases_tdd.py`,
  `test_git_tdd.py`, `test_paths_faults_tdd.py` and
  `test_release_transport_tdd.py` passed (2026-11-08T17:33).
  `rg -n '"3"' bin/release_workflow.bat bin/release_alias.bat` shows line 68 in
  both launchers; `rg -n '0, 1, 2, 3'` shows `results.py:45` and
  `bootstrap.py:191`; the `subprocess|Popen` search over
  `tests/unit/tools/release_workflow/repository_simulation.py` matches only
  the import and a `CompletedProcess` data value, no process start;
  `cli.SHIPPED_HANDLERS` is empty. The cross-site status test passes, and its
  counter-test shows that a synthetic copy dropping status 3 at one site
  breaks the agreement.
- **Independent reviewer reassessment (round 3)**: F1 is resolved under the
  design's recorded Git 2.44 decision. Read-only inspection of Git v2.43.0
  and v2.44.0 `ref-filter.c` confirms the change from one-level dereference
  to full peeling. Context creation enforces the floor; the nested-tag and
  version tests cover the revised contract. The current resolver matches the
  request's `ghog day --full=speed --whole-suite` project validation set.
  The writer reports that walk green with 100% measured coverage; the
  reviewer assessed coverage statically and ran no tests or coverage walk.
  The independent commit-plan checker is ready with six ordered groups and
  no diagnostics. This reassessment changes review metadata only.
- **Line counts after the step**: `cli.py` 168, `invocation.py` 199,
  `results.py` 53, `bootstrap.py` 201, both launchers 79,
  `operation_lock.py` 261, `git.py` 331, `repository_simulation.py` 253,
  `launcher_simulation.py` 208, `test_cli_tdd.py` 200,
  `test_invocation_tdd.py` 200, `test_results_tdd.py` 46,
  `test_bootstrap_tdd.py` 212, `test_codepage_tdd.py` 161,
  `test_release_transport_tdd.py` 159, `test_operation_lock_tdd.py` 337,
  `test_git_releases_tdd.py` 288, `test_git_tdd.py` 232,
  `test_paths_faults_tdd.py` 91; every Python file stays below 650. Recorded
  variance above the advisory estimates: `git.py` +146 (+125, with the floor
  and its stated reason), `launcher_simulation.py` +29 (+20),
  `test_invocation_tdd.py` +23 (+12), `test_bootstrap_tdd.py` +23 (+6),
  `test_codepage_tdd.py` +52 (+25), `test_release_transport_tdd.py` +55 (+10,
  with the routing test of the five observations), `test_git_releases_tdd.py`
  288 (260).

### New types or classes introduced for Step 1

- `tools.release_workflow.git.TagRecord`: frozen tag ref data (name, object
  type, peeled commit, own annotation or `None` for a lightweight tag).
- `tools.release_workflow.git.GitRevisionNotFoundError`: a `GitCommandError`
  for a reachability filter naming no object, carrying the revision and
  `exit_code = 2`.
- `tools.release_workflow.git.GitCommandLineTooLongError`: a
  `GitPolicyError` carrying the measured UTF-16 units, the candidate count
  and `exit_code = 1`.
- `tests.unit.tools.release_workflow.repository_simulation.ReleaseHistory`:
  the declared release history behind the simulated observations.
- `tests/unit/tools/release_workflow/test_git/test_git_releases_tdd.py`: the
  typed observation, guard and simulation tests (`CannedRun` records the
  domain arguments of each `run` call).

### Architecture check for Step 1

- **Git adapter**: the five observations and `TagRecord` live in the existing
  Git adapter, keep `_execute` as the only process boundary and return plain
  data; tag classification and range rules stay out of it, for Step 8.
- **Entry boundary**: `cli` knows only an optional validator callable per
  handler; no version vocabulary enters the parser or the dispatcher, and
  validation runs before identity, Git and file access.
- **Lock**: `verify_held` adds a check without changing acquisition, release,
  retention or transfer; it depends on `ArtifactDeclaration` only for typing.
- **Status sites**: the four sites keep separate literals by design (the
  bootstrap may not import the tools package); the cross-site test is the
  single point that keeps them equal.

No, there is nothing that needs to be addressed: no DDD-Hexagonal violation or
adapter smell is visible in this step.

### Performance check for Step 1

- **No new `O(n^2)` or `O(n log n)` path**: tag records, tag names and the
  listing are split once, linear in the output, a tag of a tag included
  since Git 2.44 peels it in the listing; the guard joins the candidates once;
  token validation is linear in the tokens.
- **Hot-path bound**: each observation is one Git call; `verify_held` adds
  three comparisons and one record read under the existing mutex.
- **Startup or background path**: none added.
- **Plan-bound alignment**: the four-call selection ceiling and the linear
  bound of the plan are kept; the test-only simulation walks declared
  parents once per reachability query.

No, there is no performance issue that needs to be addressed.

### Unit test coverage check for Step 1

The coverage gate measures `tools` only (`[tool.coverage.run] source`), with
`*/tests/*` omitted.

- **`tools/release_workflow/cli.py`**: the validator call, the rejection of
  tokens without a validator and the intermixed parse are exercised by
  `test_cli/test_cli_tdd.py`; covered.
- **`tools/release_workflow/invocation.py`**: the new field and its copy are
  exercised by `test_invocation/test_invocation_tdd.py`; covered.
- **`tools/release_workflow/results.py`** and
  **`tools/release_workflow/bootstrap.py`**: both sides of the widened status
  check are exercised by `test_results_tdd.py` and `test_bootstrap_tdd.py`;
  covered.
- **`tools/release_workflow/operation_lock.py`**: every rejection branch of
  `verify_held` and its success are exercised by
  `test_operation_lock/test_operation_lock_tdd.py`; covered.
- **`tools/release_workflow/git.py`**: both exceptions, the record parser
  (valid and malformed output), every failure branch of `tag_records`, both
  sides of the guard and each new method are exercised by
  `test_git/test_git_releases_tdd.py`, including a tag of a tag peeled
  fully, with and without its inner tag's ref and with and without
  `--merged`, and a record still dereferenced to a tag refused with the
  floor's reason; `test_git/test_git_tdd.py` covers the floor (2.43.9 and
  2.31.0 refused, 2.44.0 accepted) and the stated reason; covered. The
  declared history covers a tag of a tag and its inner tag sharing one commit
  with distinct annotations, and the outer tag alone after the inner tag is
  deleted, with and without the reachability filter.
- **Files outside the gate**: `repository_simulation.py` (new
  `ReleaseHistory`, `_MISSING_STATUS`) and `launcher_simulation.py` (new
  `_patch_release_observations`) are referenced by tests and called by their
  own module; the five routed observations run in
  `test_release_transport_tdd.py`. Both launchers are covered by source
  contracts.

No, there is no unit-tested class below 100% that needs completing for Step 1.
No, none of the top-level symbols added outside the coverage gate is
unreferenced.

### Feature integrity for Step 1

- **Existing feature behavior**: a handler without a validator behaves as
  before when no token is given; the unavailable-operation message is
  unchanged; every existing CLI, invocation, lock and Git test passes in the
  day walk.
- **Reporting or diagnostics**: unknown statuses are still diagnosed with
  their original value; status 3 keeps the handler's diagnostics.
- **Compatibility or rollout note**: the parser now accepts trailing tokens,
  but only a handler with a validator takes them; `SHIPPED_HANDLERS` stays
  empty until Step 9.

No existing feature or reporting capability appears impaired. The Git floor
moves from 2.31.0 to 2.44.0 by the user's decision: a machine with Git 2.31
to 2.43 is now refused for every release command, with the reason and the
remedy to upgrade, instead of producing a wrong commit for a tag of a tag.

---

## Step 2. Version tokens, the anchor document and the source model

### Analysis of Step 2 implementation state

Yes. Step 2 has been fully implemented.

`tools/release_workflow/sources/` now holds the token grammar with numeric
ordering, the three forms with their expected values and the release-only
guard, the read-once `FileView`, the located-source, composition and
character-to-byte span model, the shared types of plan decision Q16, the
`version.txt` document parser, the `anchor` adapter and the adapter tuple
with its completeness test. Every planned test, property test and completion
check is in place, and the command printed by `pw scope day` reports
`exit=0`.

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

- **Tokens and forms**: `VersionToken.parse` accepts `MAJOR.MINOR.PATCH` with
  an optional uppercase `-SNAPSHOT`, without leading zeros or `v`, and fails
  with `VersionError` (status 2) whose remedy states that grammar; `key` is
  the integer triple, so `0.10.0` orders above `0.9.0` and the suffix plays no
  part. `Form` (`snapshot`, `core`, `release-only`) parses configured names
  and maps the anchor to each source's expected value; `check_release_only`
  refuses a release-only value above the target's core, naming source, value
  and target, and fails a value that is not a release token as malformed.
- **File view**: `FileView.read` loads each path at most once per view and
  records absence as `None`; `text` decodes strict UTF-8 through
  `decode_utf8`, keeping the byte-order mark apart, and a decoding failure
  names the file; `loads` counts loads per path.
- **Composition and spans**: `compose` builds one content from one original,
  rejecting a span past the end or overlapping another; `to_byte_spans` maps
  character spans to byte spans in one walk, encoding each segment once.
- **Shared model** (plan decision Q16): `Span`, `LocatedSource`,
  `VisibleRecord`, `Detection`, `SourceError`, the `AdapterSettings` and
  `Adapter` protocols, `VersionInputs.from_context`, `FileCapture.of`,
  `SourceChange`, `FileEdit` (refusing an unchanged content), `Claim`,
  `Inventory` and `Plan`. `model.py` imports only the standard library at run
  time; foundation types are imported for type checking only.
- **Anchor**: `parse_document` reads the token, optionally followed by
  whitespace, `--` and the title, as the whole first line; anything else is
  malformed with a remedy. Notes, title, byte-order mark and line endings are
  kept, and the token's byte span is recorded. `ADAPTER` locates only the
  project root's `version.txt` (other roots return no source), wraps every
  failure with the file path (status 2), reads the file once and renders the
  raw token.
- **Registry**: `sources/__init__.py` declares `ADAPTERS = (anchor.ADAPTER,)`
  and `SUPPORT_MODULES = frozenset({"model"})`; the registry test lists the
  package's modules and requires each adapter module's `ADAPTER` exactly once,
  and a synthetic listing with an unregistered module, a duplicate entry or an
  entry without a module is reported.
- **Test support**: `version_support.py` builds `version.txt` documents (LF,
  CRLF, byte-order mark), writes them at a root, declares `RootSettings` and
  reports load counts.
- **Validation evidence**: tests first, with the `sources` package moved
  aside, `ghog single` on the three Step 2 test folders failed at collection
  (`ImportError`, five modules; 2026-11-08T19:58), then passed after the
  implementation (20:00). `ghog day --whole-suite`, the command printed by
  `pw scope day`, reported `exit=0` on 2026-11-08T20:08 (check and affected
  tests; the full stage is skipped at the default level).
  `rg -n 'open\(|write_bytes|write_text' tools/release_workflow/sources` finds
  nothing.
- **Line counts**: `sources/__init__.py` 22, `sources/model.py` 390,
  `sources/anchor.py` 106, `version_support.py` 48,
  `test_version_model_tdd.py` 236, `test_version_model_pbt.py` 60,
  `test_version_anchor_tdd.py` 128, `test_version_anchor_pbt.py` 35,
  `test_version_registry_tdd.py` 66, initializers 3 each; every file stays
  below 650. Variance above the advisory estimates: `model.py` 390 (360),
  `test_version_model_tdd.py` 236 (200).
- **Independent reviewer assessment** (round 1): the staged implementation
  and unit tests satisfy Step 2, including root-only anchor detection, strict
  token and first-line parsing, byte-preserving composition and the shared
  model for later steps. The validation resolver agrees with the request's
  whole-suite speed command; the writer reports that command green with 100%
  measured coverage and no exclusions or duration outliers. The reviewer ran
  no tests or coverage, assessed coverage statically within the gate's scope,
  and independently confirmed that the three-group commit plan is ready.

### New types or classes introduced for Step 2

- `tools.release_workflow.sources.model.VersionToken`, `VersionError`,
  `Form`, `Span`, `LocatedSource`, `VisibleRecord`, `Detection`,
  `SourceError`, `FileView`, `AdapterSettings`, `Adapter`, `VersionInputs`,
  `FileCapture`, `SourceChange`, `FileEdit`, `Claim`, `Inventory`, `Plan`, and
  the functions `check_release_only`, `decode_utf8`, `compose` and
  `to_byte_spans`.
- `tools.release_workflow.sources.anchor.VersionDocument`, `AnchorAdapter`,
  `parse_document` and `ADAPTER`.
- `tools.release_workflow.sources.ADAPTERS` and `SUPPORT_MODULES`.
- Two additions the plan's list implies: `AdapterSettings`, a protocol
  exposing `project_root`, so the anchor (and Step 3's pattern adapter) emit
  only at the project root, which Step 3's `VersionSettings` satisfies
  structurally; and `Claim` (path, field, adapter, spans), the element of
  `Inventory.claims` that Step 3 registers.
- Test support: `tests.unit.tools.release_workflow.version_support` and the
  `test_version_model`, `test_version_anchor` and `test_version_registry`
  test folders.

### Architecture check for Step 2

- **Domain model**: `model.py` holds plain values and pure functions over
  bytes and text; its only file access is the read-only `FileView`, which the
  plan places there and which adapters receive injected, so detection stays a
  pure function of the view's bytes and the settings.
- **Adapters**: `anchor.py` depends only on the model; it never writes, takes
  the lock or starts a process. Rendering returns bytes for the transition.
- **Boundary direction**: foundation types (`ProjectIdentity`,
  `Configuration`, `ArtifactDeclaration`, `GitExecutionContext`,
  `InvocationContext`) are imported for type checking only; no foundation
  module imports `sources`, and no Step 2 module imports a later one.

No, there is nothing that needs to be addressed: no DDD-Hexagonal violation or
adapter smell is visible in this step.

### Performance check for Step 2

- **No new `O(n^2)` or `O(n log n)` path over a file**: `FileView` caches
  each path, `to_byte_spans` encodes the text once and `compose` joins slices
  of the original once. The only sorts are over the span offsets or edits of a
  single file, a handful of owned fields, as the plan prescribes; they never
  grow with file size.
- **Hot-path bound**: each file is loaded once per phase, decoded once and
  scanned once; token parsing is one regular-expression match.
- **Startup or background path**: none added; importing the package builds one
  frozen adapter.
- **Plan-bound alignment**: one read and one scan per file per phase, linear
  in the file.

No, there is no performance issue that needs to be addressed.

### Unit test coverage check for Step 2

The coverage gate measures `tools` only (`[tool.coverage.run] source`), with
`*/tests/*` and `*/__init__.py` omitted.

- **`tools/release_workflow/sources/model.py`**: every branch is exercised by
  `test_version_model/test_version_model_tdd.py` and its property tests:
  accepted and rejected tokens, `core`, `key`, both form parses, every form's
  expected value, every release-only outcome (other form, accepted, above the
  target, unparsable, snapshot), present, absent and undecodable reads,
  composition with adjacent, outside and overlapping spans, invalid spans,
  span mapping with and without a byte-order mark and past the text, and each
  shared type; covered.
- **`tools/release_workflow/sources/anchor.py`**: every first-line form,
  malformed lines, invalid tokens, notes with and without a terminator, LF,
  CRLF and byte-order-mark replacement, project-root and other-root
  detection, and the missing, undecodable, malformed and invalid-token
  failures are exercised by `test_version_anchor/`; covered.
- **`tools/release_workflow/sources/__init__.py`**: omitted by the gate; its
  two declarations are read by `test_version_registry`.
- **Files outside the gate**: `version_support.py` defines `BOM`,
  `RootSettings`, `version_txt`, `write_version_txt` and `load_counts`, each
  referenced by the Step 2 tests.

No, there is no unit-tested class below 100% that needs completing for Step 2.
No, none of the top-level symbols added outside the coverage gate is
unreferenced.

### Feature integrity for Step 2

- **Existing feature behavior**: no existing module changes; the new package
  is not imported by any shipped handler, and `SHIPPED_HANDLERS` stays empty.
- **Reporting or diagnostics**: every new failure is a `ValueError` subclass
  carrying `exit_code = 2` and a remedy naming the file or grammar.
- **Compatibility or rollout note**: Step 3 builds settings, participation and
  claims on these types, and the adapter tuple grows from `("anchor",)`.

No existing feature or reporting capability appears impaired.

---

## Step 3. Version configuration, participation, claims and pattern sources

### Analysis of Step 3 implementation state

Yes. Step 3 has been fully implemented.

`.release.ini` now accepts the version domain, `[source:<name>]` and
`[component:<id>]`, validated for every command by a deferred validator that
loads the source settings only when a version section exists. The pattern
adapter matches once on a CRLF-to-LF view and maps its capture back to the
original bytes. Detection runs every adapter over every participating root,
registers claims by path, field and byte span, composes per-file edits from
one original and lists undeclared candidates from one Git listing. Every
planned test, the property test and the completion checks are in place, and
the command printed by `pw scope day` reports `exit=0`.

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

- **Version schema** (plan decision Q02): `schemas.VERSION_SCHEMA` declares
  the `source:` family (`form`, managed `file`, `pattern`) and the
  `component:` family (required managed `root`); `SHIPPED_SCHEMAS` is
  `(TOOLING_SCHEMA, VERSION_SCHEMA)`. `_validate_version` returns at once when
  no `source:` or `component:` section is declared, otherwise imports
  `sources.settings` and calls `validate_settings`, so loading a configuration
  without version sections imports no `tools.release_workflow.sources` module.
- **Settings**: `validate_settings(sections, adapters=ADAPTERS)` applies the
  per-instance rules of "Sections and keys". A registered adapter other than
  the reserved `anchor` and `pattern` names a built-in section that takes only
  `form`, within that adapter's `forms` (design decision Q10). `anchor` and
  `pattern` cannot be declared. Every other name is a pattern source that
  needs `file`, `pattern` (compiled with `re.MULTILINE`, exactly one capture
  group) and `form`. A component root must lie below the project root, not
  under a name of `EXCLUDED_DIRECTORIES` (compared with the filesystem's case
  rules), and must not repeat another declaration's directory. Each failure
  names the section and key, and the loader reports it as a
  `ConfigurationError` (status 2). `read_settings(configuration, adapters)`
  returns `VersionSettings` (project root, form overrides by adapter name,
  pattern declarations, components by id, all in declaration order); the
  project root is the directory of the `.release.ini` the loader read, the
  only root the validator's mappings carry.
- **Pattern sources** (design decision Q09): `pattern.lf_view` reads each CRLF
  as LF in one pass and records where each such line feed lands, and
  `LfView.original_offset` maps a view offset back to the original text. The
  `pattern` adapter, with no default form and every form allowed, locates the
  declared sources only at the project root. It requires the file to exist
  (never created) and to be UTF-8. Its expression must match exactly once,
  with a nonempty capture that is a version token, without `-SNAPSHOT` unless
  the form is `snapshot`. The capture is mapped to a byte span through
  `to_byte_spans`, so a replacement keeps every line ending; each failure
  names `[source:<name>]` and the file (status 2).
- **Detection**: `participating_roots(settings)` returns the project root then
  each component root, failing when a component root is missing or not a
  directory. `detect(inputs, view, adapters=ADAPTERS)` runs every adapter over
  every root in tuple order. It refuses a second claim on one path and field,
  a span outside its file and any overlapping spans of one file, naming both
  claimants with their adapter, field and root, and captures each
  participating file once from the same view. `plan_edits(inventory, anchor,
  adapters=ADAPTERS)` runs the release-only guard for every source, then
  composes one `FileEdit` per changed file from its captured original through
  `model.compose`, with its `SourceChange` records.
  `candidates(inputs, inventory, view, adapters=ADAPTERS)` makes one
  `git.listing` call. It skips names under an excluded directory, the
  artifact home, a participating root or the directory of a located manifest
  file (a Maven module), and reads each remaining manifest file once to keep
  those with a project version as `not-participating undeclared`.
- **Registry**: `ADAPTERS = (anchor.ADAPTER, pattern.ADAPTER)` and
  `SUPPORT_MODULES = frozenset({"model", "settings", "detection"})`.
- **Model extension**: `model.PatternDeclaration` (name, path, compiled
  expression, form) and `AdapterSettings.patterns`. The pattern adapter reads
  its declarations through the same `detect` signature as every adapter, and
  pyright strict refuses a narrower settings parameter in the registered
  tuple. `model.py` is a Step 2 file outside this step's file list.
- **Tests**: `test_schemas_tdd.py` checks the shipped tuple, the absence of any
  source module import without version sections (the entries are removed from
  `sys.modules` for the test first) and the delegation to the settings
  validator. `test_version_settings_tdd.py` covers each accepted and rejected
  declaration of the plan through `load_configuration`; until Steps 5 to 7
  register `python`, `npm` and `maven`, synthetic adapters with the design's
  forms stand in for them through a test registry.
  `test_pattern_sources_tdd.py` covers the umbrella pattern on LF and CRLF,
  the byte-order mark, accented and non-BMP text, two sources composing in one
  file, and each failure. `test_pattern_sources_pbt.py` checks the view and
  offset map over generated line lists. `test_version_detection_tdd.py` covers
  claims, overlaps, root order, read counts, composition, the release-only
  guard, component roots and candidates. `test_version_registry_tdd.py` checks
  the new order. `version_support.py` adds pattern declarations to
  `RootSettings` and adds line files, file and `.release.ini` writers, a
  `VersionInputs` builder and a logging `SyntheticAdapter`.
- **Validation evidence**: tests first, `ghog single` on the Step 3 test
  folders with the schema and registry tests failed at collection (exit 4, six
  `ImportError`s; 2026-11-09T09:59). After the implementation, the focused set
  with `test_configuration`, `test_version_anchor` and `test_version_model`
  passed except the property test's lifecycle CPU (0.234 s); redrawn from one
  integer, it passed (10:15). `ghog day --whole-suite`, the command printed by
  `pw scope day`, failed once at check.bat (an unused import, a test constant
  named like a token, a dataclass call default, a lost `noqa` and radon grade
  C on `candidates`), then reported `exit=0` on 2026-11-09T10:31 (check and
  298 affected tests; the full stage is skipped at the default level).
  `rg -n 'import tools.release_workflow.sources|from tools.release_workflow.sources' tools/release_workflow/schemas.py`
  shows only the deferred import inside `_validate_version`, and the item 1
  configuration tests pass unchanged.
- **Line counts**: `schemas.py` 220, `sources/__init__.py` 23,
  `sources/model.py` 410, `sources/settings.py` 175, `sources/pattern.py`
  148, `sources/detection.py` 180, `version_support.py` 150,
  `test_schemas_tdd.py` 151, `test_version_registry_tdd.py` 69,
  `test_version_settings_tdd.py` 139, `test_pattern_sources_tdd.py` 131,
  `test_pattern_sources_pbt.py` 54, `test_version_detection_tdd.py` 198,
  initializers 3 each; every file stays below 650. Variance above the
  advisory estimates: `pattern.py` 148 (130), `version_support.py` +102
  (+60), `test_schemas_tdd.py` +61 (+8).

- **Independent reviewer assessment (round 1)**: the staged implementation
  satisfies Step 3. Configuration validation, CRLF offsets, duplicate and
  overlapping claims, adapter-major order, per-file composition and candidate
  filtering agree with the plan and their unit tests. The model extension
  carries the pattern declarations through the existing adapter protocol and
  stays within this step's behavior. Coverage was assessed statically against
  the `tools` gate; the writer reports the whole-suite speed walk green with
  100% measured coverage. The reviewer ran no test or coverage walk. The
  current validation resolver matches the request, and the independent commit
  checker is ready with four ordered groups and no diagnostics. No unresolved
  finding or substantive reviewer repair remains.

### New types or classes introduced for Step 3

- `tools.release_workflow.schemas.VERSION_SCHEMA` and `_validate_version`.
- `tools.release_workflow.sources.settings.VersionSettings`, `SettingsError`,
  `EXCLUDED_DIRECTORIES`, `excluded_directory`, `validate_settings` and
  `read_settings`.
- `tools.release_workflow.sources.pattern.LfView`, `lf_view`,
  `PatternAdapter` and `ADAPTER`.
- `tools.release_workflow.sources.detection.participating_roots`, `detect`,
  `plan_edits` and `candidates`.
- `tools.release_workflow.sources.model.PatternDeclaration` and the
  `AdapterSettings.patterns` property.
- Test support: `version_support.SyntheticAdapter`, `lines_file`,
  `write_file`, `write_release_ini`, `declare_pattern`, `project_identity`,
  `version_inputs` and `UMBRELLA_PATTERN`, and the `test_version_settings`,
  `test_pattern_sources` and `test_version_detection` test folders.

### Architecture check for Step 3

- **Foundation boundary**: `schemas.py` keeps importing no domain code at load
  time; its one deferred import runs only for a declared version section, the
  idiom `cli.py` and `artifacts.py` already use. `configuration.py` is
  unchanged.
- **Domain modules**: `settings.py` works on the loader's immutable mappings
  and reads no file; `pattern.py` depends only on the model and never writes;
  `detection.py` depends on the model, settings and the adapter tuple, reads
  through the injected `FileView`, and reaches Git only through the
  `GitExecutionContext` carried by `VersionInputs`. Foundation types are
  imported for type checking only.
- **Dependency direction**: the package initializer imports only the adapters;
  `settings` and `detection` import the initializer's tuple, and no adapter
  imports a support module, so there is no import cycle. Adapters never write,
  lock or start a process; edits are composed for the Step 4 transition.

No, there is nothing that needs to be addressed: no DDD-Hexagonal violation or
smell is visible in this step.

### Performance check for Step 3

- **No new `O(n^2)` or `O(n log n)` path**: claims are indexed by path and
  field in a dictionary; the only sort is over the spans of one file, a handful
  of owned fields, as the plan prescribes. Candidate filtering is one pass
  over the Git listing with set lookups, and each remaining manifest file is
  read once.
- **Pattern sources**: the CRLF-to-LF view is built in one pass; mapping the
  two capture offsets costs one binary search each over the collapsed line
  feeds; the match stops after a second occurrence.
- **Configuration**: validation is one pass over the sections; a configuration
  without version sections pays one scan of its section names and no import.
- **Plan-bound alignment**: detection reads each file once per phase through
  the view, and `list` adds exactly one Git call.

No, there is no performance issue that needs to be addressed.

### Unit test coverage check for Step 3

The coverage gate measures `tools` only (`[tool.coverage.run] source`), with
`*/tests/*` and `*/__init__.py` omitted.

- **`tools/release_workflow/schemas.py`**: `_validate_version`'s early return
  and its delegation are exercised by `test_schemas/test_schemas_tdd.py`; the
  rest of the module keeps its item 1 tests; covered.
- **`tools/release_workflow/sources/settings.py`**: every rule of
  `_form`, `_pattern_source`, `_source` and `_component`, the accepted
  override, pattern and component paths, and `read_settings` without version
  sections are exercised by `test_version_settings/`; covered.
- **`tools/release_workflow/sources/pattern.py`**: the view and offset map,
  project and other roots, the missing and undecodable file, zero, several and
  empty matches, both malformed values, rendering and the candidate answer are
  exercised by `test_pattern_sources/`; covered.
- **`tools/release_workflow/sources/detection.py`**: missing and file
  component roots, the root order, duplicate, outside and overlapping claims,
  captures, composition, the release-only guard, an absent capture, and every
  candidate filter (non-manifest, excluded, artifact home, participating,
  missing file, without version) are exercised by `test_version_detection/`;
  covered.
- **`tools/release_workflow/sources/model.py`**: the new `PatternDeclaration`
  is built by the settings and pattern tests.
- **`tools/release_workflow/sources/__init__.py`**: omitted by the gate; its
  declarations are read by `test_version_registry`.
- **Files outside the gate**: every new `version_support.py` symbol
  (`SyntheticAdapter`, `lines_file`, `write_file`, `write_release_ini`,
  `declare_pattern`, `project_identity`, `version_inputs`, `UMBRELLA_PATTERN`)
  is referenced by the Step 3 tests or inside the module.

No, there is no unit-tested class below 100% that needs completing for Step 3.
No, none of the top-level symbols added outside the coverage gate is
unreferenced.

### Feature integrity for Step 3

- **Existing feature behavior**: a configuration without version sections
  loads as before, imports no source module, and still rejects unknown
  sections and keys; the item 1 configuration and schema tests pass, the
  schema test updated only for the shipped tuple. No shipped handler uses the
  new modules yet.
- **Reporting or diagnostics**: every new failure carries status 2 and names
  its section and key, its `[source:<name>]` and file, or both claimants.
- **Compatibility or rollout note**: until Steps 5 to 7 register `python`,
  `npm` and `maven`, a `[source:npm]` section is read as a pattern source and
  needs all three keys; the design's override semantics apply once each
  adapter is registered. Step 4 consumes `detect` and `plan_edits`, and Step 9
  `candidates`.

No existing feature or reporting capability appears impaired.

---

## Step 4. Recoverable version transition

### Analysis of Step 4 implementation state

Yes. Step 4 has been fully implemented.

`tools/release_workflow/version_evidence.py` writes, marks, deletes, lists
and allocates the per-transition evidence, and
`tools/release_workflow/version_transition.py` runs the recoverable
transition, reporting one of five outcomes, with a restore handle for item 5.
The three defects found by the round 1 code review are repaired with
regression tests:

- a manifest copy name can no longer lead residue cleanup out of its evidence
  directory;
- an `unchanged` run whose lock release fails now stops with status 1;
- an evidence directory that can be neither read nor listed is unreadable
  (status 2).

Every planned test and completion check is in place, and the command printed
by `pw scope day` reports `exit=0`.

Independent reviewer assessment (code review round 2): the three carried
findings are resolved by the staged implementation and regression tests.
Static review finds no remaining Step 4 implementation or unit coverage gap.
The current validation resolver matches the request's whole-suite command;
the writer owns the reported green walk and coverage result, which the
reviewer has not rerun.

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

- **Evidence** (`version_evidence.py`):
  - `EvidenceManifest` records version 1, the owner (`standalone` or a
    lifecycle transaction), the target, the state (`writing`, `complete` or
    `restoration-incomplete`), the creation time with its offset, and each
    file's root-relative path, SHA-256, existence and copy name. It encodes
    as indented UTF-8 JSON. Decoding rejects duplicate keys, unknown or
    missing fields, wrong types, another version, an empty owner and any
    copy name other than `original.<n>` (no traversal, absolute,
    drive-qualified, nested or manifest name), so such a manifest is
    unreadable evidence.
  - `allocate(prepared, now, pid, attempts=99)` creates
    `a.version-transition.<YYYYMMDDTHHMMSS+HHMM>-<pid>` with
    `mkdir(exist_ok=False)` on a revalidated managed target. A taken name
    moves to the next `-2`, `-3` suffix, and an existing directory is never
    entered (plan decision Q17). Any other failure, or the attempt limit,
    fails with status 1.
  - `write_evidence` writes one copy per present file through the managed
    replacement, then the manifest. On failure it removes the partial
    directory, or names what remains.
  - `EvidenceDirectory.mark` replaces the manifest atomically. `delete`
    removes the copies, then the manifest, each authorized and required to
    resolve directly inside the evidence directory, then the directory; a
    failure or a destination outside the directory names the residue and
    removes nothing further.
  - `find_evidence` lists only the artifact home and reads each manifest
    once. It classifies completed standalone residue (including an empty
    directory left by a failed cleanup), interrupted, unreadable (including a
    directory that cannot be read or listed) and lifecycle-owned evidence.
  - `remove_managed` removes a revalidated file, if present, or an empty
    directory.
- **Transition** (`version_transition.py`):
  - `TransitionOutcome` (`applied` 0, `unchanged` 0, `restored` 1,
    `restoration incomplete` 3, `applied with cleanup failed` 1),
    `TransitionResult`, `TransitionError`, `LifecycleOwnership`,
    `RestoreHandle.restore` and `discard`.
  - `TransitionPorts` (plan decision Q07): replacement, removal, lock
    factory, process probe, local clock and process id, plus the file-view
    factory that opens each phase's fresh view, all with production defaults.
  - `plan_transition` and `set_versions` follow "Ownership and the
    authoritative plan" through "Restoration and its distinct failure".
  - A standalone call:
    - plans without side effects (status 2 leaves no artifact home, lock or
      evidence), then prepares the home and acquires the lock (a held lock:
      status 1 naming its owner);
    - removes completed standalone residue with a warning, and stops with
      status 2 on any other evidence it does not own, before every success
      path;
    - replans in a fresh view and reports `unchanged` for an empty plan;
    - writes evidence (failure: status 1, no source written);
    - compares each file with its captured bytes just before replacing it,
      replaces the files in path order with `version.txt` last, verifies
      every source's expected value in a fresh view, and marks the evidence
      `complete`.
  - Before that marker, any failure restores the replaced files and verifies
    them in a fresh view:
    - when every file is back, the standalone evidence is deleted and the
      status is 1;
    - otherwise the evidence becomes `restoration-incomplete`, and status 3
      names each unrestored source and its retained copy.
  - After the marker, a cleanup or lock-release failure keeps the new
    versions and returns `applied with cleanup failed` (status 1), naming the
    residue. The primary outcome is fixed first, and secondary failures only
    add diagnostics, except that an `unchanged` run whose lock release fails
    raises `TransitionError` with status 1 naming the remaining lock record.
    The lock is released on every path after acquisition, including an
    exception.
  - A lifecycle call validates its transaction identity (not `standalone`:
    status 2) and verifies the supplied lock before any read (status 1). It
    never acquires or releases that lock, accepts its own earlier evidence,
    keeps its evidence `complete`, and returns a `RestoreHandle` that
    restores with the same routine.
- **Test support** (`version_support.py`): the fixed clock and process id, the
  `RESTORATION_FIXTURES` registry (anchor, pattern, and one file with two
  disjoint claims) that Steps 5 to 7 extend (plan decision Q01), `Faults`
  (recording and failing managed replacement and removal, with tampering and
  a concurrent writer hook), `ViewLog`, `declare_evidence`, `source_bytes` and
  `version_project`.
- **Tests**:
  - `test_version_evidence_tdd.py`: copies and manifest, failed writes with
    and without a successful cleanup, marking, deletion order and residue
    names, a copy resolving outside the directory refused, listing
    classification (nested and non-evidence entries ignored, a missing home
    included), strict decoding including unsafe copy names, allocation
    suffixes, an allocation failure and the attempt limit.
  - `test_version_transition_tdd.py`: plan failures with whole-tree
    snapshots, a held lock, residue removal, residue with a traversal or
    absolute copy name stopping with every byte kept, evidence that can be
    neither read nor listed stopping with the lock released, unfinished
    evidence stopping an empty plan, `unchanged`, unwritable evidence, write
    order, changes, one view per phase, marker before cleanup, and the
    default ports.
  - `test_version_restoration_tdd.py`: every registry set at every write
    position, a concurrent change, a failed verification, a failed marker, a
    restoration whose evidence cannot be deleted, an incomplete restoration
    alone and with a lock-release failure, a marker failure or an unreadable
    file, `writing` evidence stopping a same-target rerun, the three cleanup
    faults followed by the next run removing their residue, and a lock-release
    failure after an `unchanged` run (status 1) or after completion.
  - `test_version_lifecycle_tdd.py`: a kept lock and a working handle, a
    released handle, another project's lock and the reserved name failing
    with no view opened, own versus foreign evidence, and two calls with
    disjoint evidence whose first handle still restores.
  - No property test: the failure-position domain is finite and parametrized
    exhaustively.
- **Validation evidence**:
  - Tests first: `ghog single` on the two new test folders failed at
    collection (four `ModuleNotFoundError`s; 2026-11-09T14:46). After the
    implementation and two test-code defects (unescaped evidence names in
    `match=`, and a declared home without its ignore file), 168 focused
    tests passed.
  - `ghog day --whole-suite`, the command printed by `pw scope day`, first
    failed at check.bat: pyright, ruff, radon on one test, and MD050 on four
    bare `__init__.py` paths in the committed step 3 review answer, which
    the earlier markdownlint run had not reported. Once these were fixed, it
    reported `exit=0` (15:09). Three tests added after a static coverage
    review then passed in another `exit=0` walk (2026-11-09T15:16).
  - `rg -n 'os\.replace|write_bytes|unlink'` on both modules finds only
    `remove_managed`'s `unlink(missing_ok=True)` on `target.revalidate()`.
  - Code review round 1 (changes requested) found three defects: unsafe copy
    names, status 0 after a failed release of an `unchanged` run, and an
    unguarded directory listing. The writer repaired all three with
    regression tests; the Step 4 test folders pass, and the walks are rerun
    before round 2.
- **Line counts** (after the round 1 repairs): `version_evidence.py` 357,
  `version_transition.py` 390, `version_support.py` 290,
  `test_version_evidence_tdd.py` 289, `test_version_transition_tdd.py` 253,
  `test_version_restoration_tdd.py` 282, `test_version_lifecycle_tdd.py` 168,
  initializers 3 each; every file stays below 650. Variance:
  `version_evidence.py` 357 (advisory 300), `version_support.py` +140
  (advisory +60); the transition test files stay under their estimates.

### New types or classes introduced for Step 4

- `tools.release_workflow.version_evidence`: `EvidenceError`,
  `EvidenceState`, `EvidenceKind`, `EvidenceFile`, `EvidenceManifest`,
  `EvidenceDirectory`, `EvidenceEntry`, `allocate`, `write_evidence`,
  `evidence_files`, `find_evidence`, `remove_managed`, `STANDALONE`,
  `EVIDENCE_PREFIX`, `MANIFEST_NAME` and `ATTEMPT_LIMIT`.
- `tools.release_workflow.version_transition`: `TransitionOutcome`,
  `TransitionResult`, `TransitionError`, `TransitionLock`, `LockFactory`,
  `TransitionPorts`, `DEFAULT_PORTS`, `LifecycleOwnership`, `RestoreHandle`,
  `plan_transition` and `set_versions`.
- Additions beyond the plan's list: the `view` port (a fresh file view per
  phase, so tests count views and prove that a failing lifecycle call opens
  none); `allocate` taking the clock reading and the prepared home (the
  project comes from it); `remove_managed` tolerating an already-missing file,
  so removing residue after a failed manifest deletion is idempotent.
- Test support: `version_support.RestorationFixture`, `RESTORATION_FIXTURES`,
  `Faults`, `ViewLog`, `declare_evidence`, `source_bytes`, `version_project`,
  `FIXED_NOW`, `TRANSITION_PID`, `EVIDENCE_NAME`, `TARGET`, `PATTERN_INI`, and
  the `test_version_evidence` and `test_version_transition` test folders.

### Architecture check for Step 4

- **Layering**: the transition is an application service. It drives the
  domain (`sources.detection`, the model) and item 1's infrastructure
  boundaries (`prepare_artifacts`, `managed_files`, `OperationLock`,
  `windows_process.process_state`) only through `TransitionPorts`, whose
  defaults are those boundaries. No domain module imports the transition or
  the evidence module, and neither imports a later step's module.
- **Writes**: every file change goes through the managed replacement or a
  revalidated managed target; evidence allocation uses the managed target's
  revalidated path and never item 1's `prepare_directory`. `managed_files` is
  unchanged.
- **Ownership**: a lifecycle call verifies, but never acquires or releases,
  the supplied lock, and never deletes evidence owned by a transaction; only
  `RestoreHandle.discard` does, on item 5's request.
- **Evidence cleanup boundary**: project-level managed authorization alone
  did not prove that a decoded copy belongs to its evidence directory (round
  1 finding). Decoding now accepts only `original.<n>` copy names, and
  removal requires each copy and the manifest to resolve directly inside the
  directory.

No, there is nothing that needs to be addressed: no DDD-Hexagonal violation or
smell is visible in this step.

### Performance check for Step 4

- **No new `O(n^2)` or `O(n log n)` path**: each phase opens one view and
  reads each participating file once. The only sorts are the write order over
  the changed files and the listing of evidence directories in the home, both
  a handful of entries. Evidence is classified in one pass, and restoration
  touches each replaced file once.
- **Bounded side effects**: allocation tries at most 99 names, each one
  `mkdir`; evidence writes one copy per participating file and one manifest
  per state change.
- **Plan-bound alignment**: one file view per phase (initial plan, locked
  plan, comparison, verification, restoration check), as the IO table states.

No, there is no performance issue that needs to be addressed.

### Unit test coverage check for Step 4

The coverage gate measures `tools` only (`[tool.coverage.run] source`), with
`*/tests/*` and `*/__init__.py` omitted.

- **`tools/release_workflow/version_evidence.py`**: `test_version_evidence/`
  exercises every branch, including every strict decoding rule, both
  `remove_managed` branches, each residue name, the write cleanup that fails,
  the allocation failure, the attempt limit and every listing kind. The
  transition tests add residue deletion of a manifest-less empty directory;
  covered.
- **`tools/release_workflow/version_transition.py`**: the transition,
  restoration and lifecycle tests reach every outcome and every secondary
  failure:
  - before any side effect: plan failures, the held lock, unwritable
    evidence, the evidence stop with the lock released through the exception
    path;
  - during writes: a write, comparison, verification or marker failure, and
    an unreadable file during the restoration check;
  - after an outcome: deletion and release failures;
  - lifecycle: an unbound lock, the reserved name, own evidence and the
    handle's `restore` and `discard`;
  - `test_default_ports_are_the_production_boundaries` reaches the default
    clock.
  Covered.
- **Files outside the gate**: every new `version_support.py` symbol is
  referenced by the Step 4 tests.
- **Behavioral contracts beyond line coverage** (round 1 finding):
  - unsafe copy names are tested at decoding, at deletion and through `set`
    (status 2, every byte kept);
  - a failed release after `unchanged` is tested (status 1, sources kept);
  - a manifest read and a directory listing both denied is tested through
    `set` (status 2, named directory, sources kept, lock released).

No, there is no unit-tested class below 100% that needs completing for Step 4.
No, none of the top-level symbols added outside the coverage gate is
unreferenced.

### Feature integrity for Step 4

- **Existing feature behavior**: no existing tool module changes. The new
  modules are not wired to a shipped handler until Step 9, and the item 1
  lock, managed-file and artifact tests are unchanged.
- **Reporting or diagnostics**: preflight and evidence stops raise with
  status 2, lock and evidence-writing failures with status 1, and outcomes
  carry their status and diagnostics. No diagnostic of an incomplete
  restoration claims a complete one.
- **Compatibility or rollout note**: Steps 5 to 7 add their adapters'
  fixture sets to `RESTORATION_FIXTURES`. Step 9's handlers turn
  `TransitionError`, `EvidenceError` and the outcomes into an
  `OperationResult`.

No existing feature or reporting capability appears impaired; the cleanup and
failure-reporting contracts that round 1 found impaired are repaired and
tested.

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
