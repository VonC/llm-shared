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

Yes. Step 5 has been fully implemented.

`tools/release_workflow/sources/toml_scan.py` locates the single-line
`version` string of `[project]` or of the named `[[package]]` block, and
`tools/release_workflow/sources/python.py` registers the `python` adapter
between `anchor` and `pattern`. The adapter pairs `pyproject.toml` with its
`uv.lock`, lists tool-only files, and rejects dynamic or missing versions,
orphan and ambiguous locks, unregistered lock schemas, uv workspaces and
local links between participating components before any write. The
registered schemas `(1, 3)` and `(1, 5)` are exactly those of the five uv
0.13.4 records in the committed `lock_evidence.v1.json`, which the hand-run
recorder produced and a test checks against the current adapter edit. The
Python fixture sets joined the restoration matrix. Every planned test and
completion check is in place, and the command printed by `pw scope day`
reports `exit=0`.

Reviewer assessment for round 1: the staged implementation satisfies Step 5.
Commit readiness remains blocked: the required review command is
`ghog day --full=speed --whole-suite`, and both disclosed attempts failed
lifecycle timing gates, withholding coverage and duration-outlier verdicts.
The plain day pass and focused reruns do not replace that mandatory evidence.

Writer update for round 2: the radix-order overruns came from Hypothesis's
local-constants scan, which now runs once per worker after collection, in a
separate suite commit. The latest required walk still failed, only on wall
overruns with CPU within its limit, at high host load from other workloads;
the user directed to move on when CPU is under budget. Coverage and duration
verdicts remain withheld, so coverage is still assessed statically.

Reviewer assessment for round 2: Step 5 remains fully implemented; its 18
implementation, test and evidence paths are unchanged from round 1. The
collection hook performs Hypothesis's initial constants scan before the
garbage-collector freeze and measured tests, without changing budgets,
profiles or example counts. The latest log contains 30 wall-only lifecycle
errors, each within its applicable CPU limit, and no assertion failure.
Under the explicit human direction, "If CPU is under budget, do move on",
those errors no longer block this round's advisory commit-ready conclusion.
The command still exited 2: measured coverage and duration-outlier verdicts
remain unavailable, and no green speed walk or absence of outliers is claimed.
Static coverage review finds no Step 5 gap. The independently checked commit
plan is ready with three accurate groups; no implementation repair was made.

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

- **TOML scanner** (`sources/toml_scan.py`):
  - `locate(text, table, *, package=None)` reads the text line by line (LF
    or CRLF), tracking the current table header and each `[[array]]` block.
    A small lexer follows strings, comments and brackets, so a line inside a
    multi-line string, an open array or an inline table never reads as a
    header or an assignment, and a header it cannot read (a quoted key) ends
    the current table.
  - The owned field is the single-line `version = "..."` (basic or literal
    string, any spacing, optional comment) written directly in `[project]`,
    or directly in the one `[[package]]` block whose `name` is the requested
    package; sub-tables such as `[package.metadata]` are other tables.
    Dotted keys, inline tables and multi-line strings are not located and
    fail as unsupported layouts with the remedy to write the plain
    assignment; no or several matching blocks, and a doubled assignment,
    fail as ambiguous.
  - `byte_span(text, bom, table, value, *, package=None)` also requires the
    located text to equal the `tomllib` value (an escape fails) and maps the
    span to bytes through `model.to_byte_spans`.
- **Python adapter** (`sources/python.py`, `python.ADAPTER`): name `python`,
  forms `{core}`, default `core`, candidate file `pyproject.toml`.
  - A manifest without `[project]` gives `not-participating tool-only`
    records for it and its lock. A version listed in `dynamic`, missing or
    not a string, and a file that is not UTF-8 or TOML, fail naming the file
    and the remedy.
  - `uv.lock` must carry a registered `(version, revision)` schema,
    `REGISTERED_LOCK_SCHEMAS = frozenset({(1, 3), (1, 5)})`, documented next
    to the evidence record identifiers, and exactly one `[[package]]` with
    the project's normalized name (`normalize`: lowercase, runs of `-`, `_`
    and `.` as one `-`) and a `virtual = "."` or `editable = "."` source. A
    missing project name, zero or several such packages, and a root package
    without a version string fail before any write. An absent lock is not
    generated; a lock without a manifest fails as an orphan. The lock source
    names its manifest.
  - Rejections before any write: a participating manifest declaring
    `[tool.uv.workspace]`, with or without a lock; a tool-only project root
    whose workspace `members`, net of `exclude`, match a component root
    (`PurePosixPath.full_match` relative to the project root, by the
    filesystem's case rules); a lock whose `[manifest]` lists members; a
    `workspace = true` source; a `[tool.uv.sources]` `path` (table or list
    form) or a `file:` direct reference in dependencies, optional
    dependencies or dependency groups (`${PROJECT_ROOT}` expanded) whose
    destination, resolved against the declaring root, is a participating
    root, named with both components. Git, URL, index and outside paths stay
    external and unchanged.
  - Rendering returns the bytes between the quotes; `has_project_version`
    reports a candidate only for a static project version string.
- **Registry** (`sources/__init__.py`): `ADAPTERS = (anchor, python,
  pattern)`; `toml_scan` joins `SUPPORT_MODULES`.
- **Settings seam** (`sources/model.py`, `sources/settings.py`):
  `AdapterSettings` gains `components` (the declared component roots by id)
  and `participant(path)`, which names the participating root a physical
  path is. `model.participant_names` builds the index that
  `VersionSettings` keeps once per settings value, so each local-link lookup
  is constant time.
- **Lock evidence** (plan decisions Q03, Q04 and Q06):
  - `tests/unit/tools/release_workflow/lock_evidence_recorder.py`, started by
    hand and never imported by a test, records each scenario in a new
    temporary directory outside the repository, without any `UV_*`
    variable. It writes the virtual or editable manifest at `0.13.0`, lets uv
    write the revision 5 lock (`uv lock --offline --no-config --python
    <python>`), derives revision 3 by setting the revision line (provenance
    recorded) and the CRLF variant of the virtual revision 3 pair. It runs
    `uv lock --locked --offline --no-config --python <python>` on the
    "before" pair, on the pair the production adapter plans for `0.14.0`
    (`version_support.python_pair_edit`) and on the manifest-only control,
    and writes the JSON with sorted keys, LF endings and `<uv>` and
    `<python>` placeholders, refusing any host path.
  - `test_version_lock_evidence/lock_evidence.v1.json` holds five uv 0.13.4
    records (`v1r5` virtual and editable, `v1r3` virtual, editable and
    virtual CRLF). In each, the "before" and edited runs exit 0 with both
    files unchanged, and the manifest-only control exits 1 ("needs to be
    updated") with both files unchanged.
- **Test support** (`version_support.py`): `RootSettings.components` and
  `participant`; `pyproject_toml` and `uv_lock` builders for virtual and
  editable roots, `crlf`, `REGISTRY_PACKAGE`; the `python-virtual` and
  `python-editable` restoration sets (three writes each, the editable one
  CRLF with a snapshot anchor); `python_pair_edit`.
- **Tests**:
  - `test_version_formats/test_toml_scan_tdd.py`: quotes, spacing and
    comments; other tables and sub-tables ignored; the named block among
    several; lines inside strings, arrays and inline tables; the dotted,
    inline and multi-line layouts; unread headers, missing or doubled blocks
    and assignments; an escape; a mark, accented and non-BMP text before the
    value in a manifest and in an earlier lock block, LF and CRLF.
  - `test_version_formats/test_version_formats_pbt.py` (property test
    needed): generated manifests and locks with decoys locate the parsed
    value, and replacing it keeps every other character. Each example draws
    an integer triple and one bit field decoded into the layout, so the
    25-example budget stays inside the lifecycle limit.
  - `test_python_sources/test_python_sources_tdd.py`: llm-shared's shape, an
    editable CRLF root, zero or two lock roots, orphan, absent lock, tool-only
    with and without lock, dynamic, missing, non-string and escaped
    versions, unparsable TOML and UTF-8, unregistered schemas (revision 4,
    `version = true`, no revision), no project name, no root version, a
    snapshot anchor giving `core` edits through detection, candidates and
    rendering.
  - `test_python_sources/test_python_links_tdd.py`: every workspace and link
    case above, including one link between `.release.ini` components through
    `detection.detect`, a tool-only workspace below the project root, and
    the external references.
  - `test_version_lock_evidence/test_version_lock_evidence_tdd.py`: records
    for every registered pair and layout; tool, version, schema, layout, line
    endings, command and provenance; both accepted runs unchanged and the
    control refused; the adapter reproducing each recorded edited pair; a
    pair outside the registry failing detection; no host path. The JSON is
    read once per session through the `evidence` fixture.
  - `test_version_registry_tdd.py`: the order `("anchor", "python",
    "pattern")` and the support modules; `test_version_restoration_tdd.py`:
    the Python sets at every write position through the registry.
- **Validation evidence**:
  - Tests first: `ghog single` on the new and registry leaves failed at
    collection (six errors, `ImportError: cannot import name 'python'`;
    2026-11-10T07:46).
  - After the implementation, only the two properties exceeded the 0.1 s CPU
    lifecycle limit (0.109 s and 0.141 s); the cheaper encoding fixed them
    without lowering the example budget.
  - Recorder run by hand on 2026-11-10 with the project venv's uv 0.13.4 and
    Python 3.13.9: five records, written with no host path.
  - `ghog day --whole-suite`, the command printed by `pw scope day`, first
    failed at check.bat (pyright: an unknown list type; ruff: magic values,
    two six-argument functions, an S105 false positive on a lexer variable).
    After the fixes, and a constant-time participant lookup found by self
    review, it reported `exit=0` (2026-11-10T08:29).
  - `rg -n 'subprocess' tools/release_workflow/sources` finds nothing.
  - Reviewer round 1: the request discloses two failed required
    `ghog day --full=speed --whole-suite` attempts (an anchor property CPU
    overrun, then seven wall overruns in other leaves). Both reported
    `cov=withheld outliers=withheld`. No full walk or coverage measurement
    was repeated by the reviewer. The writer must establish a green required
    walk, with coverage and duration verdicts, before commit readiness.
  - Two focused runs at 66 % and 96 % host CPU load reported wall-time
    overruns in unchanged Step 4 tests (CPU inside its limit); they passed at
    35 % load. No budget was changed and nothing was excluded.
  - Round 2 (writer): each radix batch takes 10 to 35 ms on its own, but
    Hypothesis's local-constants scan looks up the path of every loaded
    module on Windows and landed inside the first property test of each
    worker. `tests/conftest.py` now runs that scan once per worker after
    collection, in its own `perf(tests)` commit; the radix and anchor property
    leaves then passed at 92 % host load. The whole-suite speed walk of
    2026-11-10T09:30 passed check.bat and the affected tests; its full stage
    failed only on 30 wall overruns (1.0 to 3.5 s) with CPU within its limit
    (at most 0.19 s), at 78 % host load from other workloads, so coverage and
    duration verdicts were withheld again. The user directed to move on when
    CPU is under budget. No budget was changed and nothing was excluded.
- **Line counts**: `toml_scan.py` 164 (advisory 170), `python.py` 307
  (advisory 430), `lock_evidence_recorder.py` 209 (advisory 220),
  `version_support.py` 356 (+66, advisory +50), test files 132, 100, 202,
  142 and 131 (advisory 200, 120, 280, 260 and 140), initializers 3 each,
  `lock_evidence.v1.json` 431 (no Python ceiling). Two files outside the
  plan's list changed for the settings seam: `sources/model.py` 410 to 437
  and `sources/settings.py` 175 to 193. Every Python file stays below 650;
  the split guidance for `python.py` was not needed.

### New types or classes introduced for Step 5

- `tools.release_workflow.sources.toml_scan`: `locate` and `byte_span`.
- `tools.release_workflow.sources.python`: `PythonAdapter`, `ADAPTER`,
  `REGISTERED_LOCK_SCHEMAS` and `normalize`.
- `tools.release_workflow.sources.model`: `AdapterSettings.components`,
  `AdapterSettings.participant` and `participant_names`.
- `tools.release_workflow.sources.settings`: `VersionSettings.participant`.
- Test support: `version_support.pyproject_toml`, `uv_lock`, `crlf`,
  `python_pair_edit`, `REGISTRY_PACKAGE`, `DEMO`, `RootSettings.components`
  and `participant`; the recorder's `Scenario`, `Tools`, `record` and `main`;
  the `test_version_formats`, `test_python_sources` and
  `test_version_lock_evidence` test folders.

### Architecture check for Step 5

- **Layering**: the scanner and the adapter are domain code of the
  `sources` package, a pure function of file bytes and settings. They read
  only through the `FileView`, resolve declared link destinations with
  `Path.resolve` (the plan's physical comparison), and never write, take the
  lock or start a process: `rg -n 'subprocess' tools/release_workflow/sources`
  finds nothing. They import only the standard library and `sources.model`.
- **Ports**: the adapter learns the participating roots through the
  `AdapterSettings` protocol (`components`, `participant`), not through the
  settings module or the configuration loader, so the domain keeps one
  inward-facing seam.
- **Evidence boundary**: the process-starting recorder lives in the test
  tree, is never imported by a test and is not part of the engine (plan
  decision Q03); production code holds only the registered schema pairs.

No, there is nothing that needs to be addressed: no DDD-Hexagonal violation or
smell is visible in this step.

### Performance check for Step 5

- **No new `O(n^2)` or `O(n log n)` path**: the scanner visits each line once
  and jumps between lexer tokens with regular expressions; block selection
  and the version list are linear in the located assignments. The adapter
  reads each of its two files once per view, scans the lock's packages once,
  and answers each local-link destination with one lookup in an index built
  once per settings value. Workspace members are matched once per component,
  at the project root only.
- **Bounded side effects**: none; detection probes two fixed file names per
  participating root, and the only filesystem query besides those reads is
  resolving each declared local destination.

No, there is no performance issue that needs to be addressed.

### Unit test coverage check for Step 5

The coverage gate measures `tools` only (`[tool.coverage.run] source`), with
`*/tests/*` and `*/__init__.py` omitted.

- **`tools/release_workflow/sources/toml_scan.py`**: `test_version_formats/`
  reaches every lexer branch (escape, comment, triple and single quotes,
  brackets), both header kinds and the unread header, both block failures,
  both assignment failures and the escape refusal; covered.
- **`tools/release_workflow/sources/python.py`**: `test_python_sources/` and
  the evidence test reach every failure and both lock outcomes, the tool-only
  records with and without a lock, every workspace and link rule, the
  external references, rendering and the candidate cases; covered.
- **`sources/model.py`** (`participant_names`) and **`sources/settings.py`**
  (`VersionSettings.participant`): reached through `RootSettings` and
  through the link test that runs `detection.detect` with `.release.ini`
  components; covered.
- **Files outside the gate**: every new `version_support.py` symbol is
  referenced by the Step 5 tests. The recorder's top-level symbols are
  referenced inside its own module from `main`; by design (plan decision
  Q03) no test imports it, and its output is checked through the committed
  JSON.

No, there is no unit-tested class below 100% that needs completing for Step 5.
No, none of the top-level symbols added outside the coverage gate is
unreferenced.

Reviewer round 1: static inspection found no missing exercise of the added
production functions or test-support symbols. This is a static assessment,
not a measured coverage percentage; the required speed walks withheld their
coverage verdicts. The recorder's symbols are connected through its module
entry point and the committed output is checked without starting uv in tests.

### Feature integrity for Step 5

- **Existing feature behavior**: no shipped command uses the version domain
  before Step 9. Registering `python` adds detection of `pyproject.toml` and
  `uv.lock` at every participating root; the Step 2 to 4 version tests, which
  use the shipped tuple, pass unchanged, and the readiness metadata checks
  keep their own parser.
- **Reporting or diagnostics**: every refusal is a status 2 `SourceError`
  naming the file and the remedy, and a local link names both components.
- **Compatibility or rollout note**: `[source:python] form = core` remains
  the only accepted override. Step 6 adds the npm records to the same
  evidence file and the `--npm` and `--node-dir` recorder arguments.

No existing feature or reporting capability appears impaired.

---

## Step 6. npm adapter with recorded npm evidence

### Analysis of Step 6 implementation state

Yes. Step 6 has been fully implemented.

Independent reviewer assessment, round 1: the received index tree
`ee21c5fa76c50c6b2a62a43482898da83148faaa` matches the request. Static review
of the scanner, adapter, registry, model seam, tests and recorder found no
blocking implementation, architecture, performance or coverage gap. The
retained whole-suite speed-walk log reports `exit=0 cov=100 outliers=0
excluded=0 proof=speed`, and its scope fingerprint matches the bound review
scope. No reviewer test or coverage run was needed. The npm accepted-pair
hashes independently match the recorded fixture bytes; the five uv records
are unchanged. The staged model and model-test additions are justified by
Step 6's configured forms and once-per-view name index. The independent
commit-plan checker reports `state=valid`, `ready=true`, two ordered groups,
16 staged paths and no diagnostics; `a.commit` remains accurate. The only
reviewer edit is this Step 6 validation assessment; the umbrella and other
steps remain outside the reviewer edit boundary.

`tools/release_workflow/sources/json_scan.py` locates owned JSON values by key
path in one pass and refuses duplicate keys on those paths, and
`tools/release_workflow/sources/npm.py` registers the `npm` adapter between
`python` and `pattern`. The adapter applies the `release-only` default or the
configured form and pairs `package.json` with its format 2 or 3
`package-lock.json`, whose top-level `version` (where present) and
`packages[""].version` compose from one original. It lists tool-only files
and, before any write, rejects workspaces, local links into participating
roots, shrinkwrap files, format 1 and other formats, foreign or versionless
root entries and orphan locks. The three npm 10.8.3 records in
`lock_evidence.v1.json` were produced by the recorder; the evidence test
checks them against the adapter. The npm fixture sets joined the restoration
matrix. Every planned test and completion check is in place, and the command
printed by `pw scope day` reports `exit=0`.

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

- **JSON scanner** (`sources/json_scan.py`):
  - `locate(text, paths)` matches one token expression over the decoded text
    and keeps a stack of open objects and arrays, each object holding the
    key path that reaches it (tracked only while it can lead to an owned
    path) and its last key, compared after decoding its escapes. It returns
    the span of each owned path's value: a string's content between the
    quotes, or the whole text of a number, literal, object or array, so the
    caller checks the parsed type. A second value on an owned path fails as
    ambiguous, since `json` keeps the last one silently; duplicates elsewhere
    are ignored. A root that is not one object (an array, a scalar, trailing
    text, an unterminated object or string, empty text) fails.
  - `byte_spans(text, bom, paths, values)` locates every owned path (so a
    duplicate `lockfileVersion` fails too), requires each string to edit to
    read as its parsed value (an escape fails), and maps the spans to bytes
    through one `model.to_byte_spans` walk, so both lock edits compose from
    one original. `spell` writes a path as `packages[""].version` in
    diagnostics and field identifiers.
- **npm adapter** (`sources/npm.py`, `npm.ADAPTER`): name `npm`, forms
  `{release-only, core, snapshot}`, default `release-only`, candidate file
  `package.json`; the `[source:npm] form` override applies to every owned
  field at every participating root.
  - A manifest without `version` gives `not-participating tool-only` records
    for it and its lock, which is never parsed. A `version` that is not a
    string, a duplicate or escaped version, and a file that is not UTF-8 or
    one JSON object fail naming the file and the remedy.
  - Rejections before any write: a `workspaces` field, with or without a
    version (npm workspaces are deferred); an `npm-shrinkwrap.json` beside a
    participating manifest; in `dependencies`, `devDependencies`,
    `optionalDependencies` and `peerDependencies`, a `file:` or `link:`
    specifier (relative, `file:///` URL, any case on Windows) whose
    destination, resolved against the declaring root, is a participating
    root, and a `workspace:` specifier whose package name is a participating
    npm manifest's name (plan decision Q15), each naming both roots.
    Registry ranges, tarballs, outside paths, Git and URL specifiers, and
    `workspace:` names of tool-only or unknown packages stay external.
  - `package-lock.json` pairs with the participating manifest. Its
    `lockfileVersion` must be in `SUPPORTED_LOCK_FORMATS = frozenset({2,
    3})`, documented next to the evidence record identifiers: format 1 fails
    with the remedy to regenerate the lock with npm 7 or later, and another
    format, a string or a boolean fails. `packages[""]` must not name
    another package (compared only when the manifest has a name, since npm
    names the root entry after the folder otherwise) and must carry a
    version string; the top-level `version` must be a string where present.
    The lock gives one source per owned field (`version`, then
    `packages[""].version`), each naming its manifest. A lock without a
    manifest fails as an orphan; Yarn and pnpm locks are never read.
  - Rendering returns the bytes between the quotes; `has_project_version`
    reports a candidate only for a manifest with its own version string.
- **Registry** (`sources/__init__.py`): `ADAPTERS = (anchor, python, npm,
  pattern)`; `json_scan` joins `SUPPORT_MODULES`.
- **Model seam** (`sources/model.py`, outside the plan's file list):
  `AdapterSettings` gains `forms`, which `VersionSettings` already held and
  the npm adapter is the first to read; `FileView.derived(key, compute)`
  computes a value once per key and view, used for the npm index of
  participating package names.
- **Lock evidence** (plan decisions Q05 and Q06):
  - The recorder now takes `--npm` and `--node-dir` beside `--uv` and
    `--python` and rewrites the whole evidence file. For each npm scenario it
    writes a `private: true` root `package.json` at `0.0.24`, lets npm write
    the format 2 or 3 lock (`npm install --package-lock-only --offline
    --lockfile-version <2|3> --ignore-scripts --no-audit --no-fund`), and
    converts both files to CRLF for the format 3 variant. It runs `npm ci
    --offline --ignore-scripts --no-audit --no-fund` on the "before" pair and
    on the pair the production adapter plans for `0.0.25`, and the lock-only
    check `npm install --package-lock-only --offline --ignore-scripts
    --no-audit --no-fund` on both pairs and on the manifest-only control,
    removing `node_modules` before each run. The Node directory is prepended
    to the child `PATH` only, `npm_config_*` variables are removed, and the
    npm cache and user configuration live in the scratch directory.
  - `lock_evidence.v1.json` holds the five uv records, unchanged by the new
    recording, and three npm records (`npm-10.8.3-lock2-root`,
    `npm-10.8.3-lock3-root`, `npm-10.8.3-lock3-root-crlf`, npm 10.8.3 on
    Node v22.9.0). Each states that `npm ci` does not compare the root
    version. In each, the four runs on the "before" and edited pairs exit 0
    with both files unchanged; the control's lock-only check exits 0, keeps
    the manifest and rewrites the lock, whose format stays the recorded one
    and whose two root version fields move to `0.0.25`.
- **Test support** (`version_support.py`): `RootSettings.forms`;
  `package_json` and `package_lock` builders formatted as npm writes them;
  the `npm-lock2` (LF) and `npm-lock3-crlf` (CRLF, accented description,
  a dependency entry) restoration sets, three writes each with two lock
  fields in one file; Step 5's `python_pair_edit` generalized to
  `pair_edit(adapter, root, target)` for both recorders and the evidence
  test.
- **Tests**:
  - `test_version_formats/test_json_scan_tdd.py`: owned paths among nested
    objects and arrays with decoy `version` keys; spans of non-string
    values; duplicates on each owned path (escaped key included) and
    duplicates elsewhere; nine texts that are not one object; the escape and
    the unlocated value; accented and non-BMP text before each owned value,
    with and without a byte-order mark, composing both lock edits; path
    spelling.
  - `test_version_formats/test_version_formats_pbt.py` (property test
    needed): generated lock-like objects with escaped decoys, nested
    `version` keys, whitespace, member order, an optional top-level version
    and byte-order mark; the byte spans hold the parsed values and
    replacing them changes only those values. One integer triple and one
    13-bit field per example, 25 examples.
  - `test_npm_sources/test_npm_sources_tdd.py`: workspace-halo's shape (CRLF
    format 3 lock, a dependency entry, snapshot anchor) changing only the
    three strings with one load per file and none of `yarn.lock` and
    `pnpm-lock.yaml`; the three forms through `.release.ini`; the
    release-only refusal of `set 0.0.24` through `set_versions` with no
    source or evidence write; tool-only with and without lock; workspaces;
    shrinkwrap; formats 2 and 3 with and without the top-level version;
    format 1, other formats, foreign and versionless root entries,
    duplicates, an escape and unparsable locks; an unnamed manifest; the
    orphan lock; unusable manifests; every link kind and the external
    references; a link through `detection.detect`; the name index read once
    per file across three roots; candidates and rendering.
  - `test_version_lock_evidence_tdd.py`: the npm records for every supported
    format and the CRLF variant, their fields and note, the four accepted
    runs, the control's rewrite and lock fields, the adapter reproducing each
    edited pair, and format 4 failing detection.
  - `test_version_model_tdd.py`: `FileView.derived` computes once per key and
    view. `test_version_registry_tdd.py`: the order `("anchor", "python",
    "npm", "pattern")` and the support modules.
    `test_version_restoration_tdd.py`: the npm sets at every write position.
- **Validation evidence**:
  - A planning probe in the scratch directory confirmed the shape npm 10.8.3
    writes for a root package without dependencies (two-space JSON, LF,
    top-level name and version, `packages[""]` name and version).
  - Tests first: `ghog single` on the new and changed leaves failed at
    collection (five errors, `ImportError: cannot import name 'npm'`;
    2026-11-10T14:13).
  - After the implementation, only the three npm evidence tests failed,
    pending the recording (2026-11-10T14:20).
  - The recorder ran by hand on 2026-11-10 with the project venv's uv 0.13.4
    and Python 3.13.9 and with npm 10.8.3 on Node 22.9.0 (the explicit 22.9.0
    directory; the host's `node22` link now points to a later 22.x). It
    wrote eight records with no host path; the uv records are identical to
    the committed ones.
  - `ghog day --whole-suite`, the command printed by `pw scope day`, first
    failed at check.bat (ty and pyright: tuple literals as `JsonPath` keys in
    two test files and one untyped empty set). After annotating them it
    reported `exit=0` (2026-11-10T14:33).
  - The implementation check found that the npm records did not yet state
    that the frozen install ignores the root version: the recorder now adds
    that note to each npm record, and the evidence was recorded again (uv
    records unchanged). The next walk failed at radon (grade C for the
    records test); with its per-record checks moved to a helper,
    `ghog day --whole-suite` reported `exit=0` on the final tree
    (2026-11-10T14:48).
  - `rg -n 'lockfileVersion' tools/release_workflow/sources/npm.py` shows the
    format check and the format 1 remedy;
    `rg -n 'subprocess' tools/release_workflow/sources` finds nothing.
- **Line counts**: `json_scan.py` 172 (advisory 220), `npm.py` 277 (advisory
  270), `lock_evidence_recorder.py` 344 (+135, advisory +110),
  `version_support.py` 397 (+41, advisory +40), new test files 118 and 304
  (advisory 160 and 320), `test_version_formats_pbt.py` +60 (advisory +40),
  `test_version_lock_evidence_tdd.py` +81 (advisory +30), registry +2,
  restoration +3, initializer 3, `lock_evidence.v1.json` 431 to 875 (no
  Python ceiling). Outside the plan's list:
  `sources/model.py` 437 to 456 and `test_version_model_tdd.py` 236 to 253.
  Every Python file stays below 650; the recorder split guidance was not
  needed.

### New types or classes introduced for Step 6

- `tools.release_workflow.sources.json_scan`: `JsonPath`, `locate`,
  `byte_spans` and `spell` (private `_Frame` and `_Scanner`).
- `tools.release_workflow.sources.npm`: `NpmAdapter`, `ADAPTER` and
  `SUPPORTED_LOCK_FORMATS`.
- `tools.release_workflow.sources.model`: `AdapterSettings.forms` and
  `FileView.derived`.
- Test support: `version_support.package_json`, `package_lock`, `pair_edit`
  (replacing `python_pair_edit`) and `RootSettings.forms`; the recorder's
  `NpmScenario`, `NpmTools` and `record_npm`, its uv classes renamed
  `UvScenario` and `UvTools`; the `test_npm_sources` test folder.

### Architecture check for Step 6

- **Layering**: the scanner and the adapter are domain code of the `sources`
  package, a pure function of file bytes and settings. They read only through
  the `FileView`, resolve declared link destinations with `Path.resolve`, and
  never write, take the lock or start a process. They import only the
  standard library and the `sources` model and scanner.
- **Ports**: the configured form reaches the adapter through the
  `AdapterSettings` protocol (`forms`), not through the settings module, and
  the cross-root name index lives in the phase's `FileView`, so no adapter
  keeps state between calls.
- **Evidence boundary**: the process-starting recorder stays in the test tree
  and is never imported by a test (plan decision Q03); production code holds
  only the supported formats.

No, there is nothing that needs to be addressed: no DDD-Hexagonal violation or
smell is visible in this step.

### Performance check for Step 6

- **No new `O(n^2)` or `O(n log n)` path**: the scanner matches each
  character once and keeps constant work per token (a key's escapes are
  decoded once); `byte_spans` measures all spans in one walk. The adapter
  reads each of its files once per view, visits each dependency specifier
  once with one settings lookup, and builds the participating-name index at
  most once per view, on the first `workspace:` specifier, reading manifests
  the same view already loads: detection stays linear in roots and
  specifiers.
- **Bounded side effects**: none; detection probes three fixed file names
  per participating root, and the only other filesystem query is resolving
  each declared local destination.

No, there is no performance issue that needs to be addressed.

### Unit test coverage check for Step 6

The coverage gate measures `tools` only (`[tool.coverage.run] source`), with
`*/tests/*` and `*/__init__.py` omitted.

- **`tools/release_workflow/sources/json_scan.py`**: `test_version_formats/`
  reaches every token kind, the tracked and untracked paths, string,
  scalar and container values on owned paths, the duplicate refusal, both
  "not one object" failures, the escape and unlocated-value refusal and
  `spell`; covered.
- **`tools/release_workflow/sources/npm.py`**: `test_npm_sources/` and the
  evidence test reach every failure, both tool-only outcomes, both lock
  outcomes with and without the top-level version, the unnamed manifest,
  every link kind and the external cases (including an unreadable component
  manifest and a non-string specifier), rendering and candidates; covered.
- **`sources/model.py`** (`FileView.derived`, `AdapterSettings.forms`):
  `test_version_model_tdd.py` and the form tests through `.release.ini`;
  covered.
- **Files outside the gate**: every new `version_support.py` symbol is
  referenced by the Step 6 tests. The recorder's top-level symbols are
  referenced inside its own module from `main`; by design no test imports it,
  and its output is checked through the committed JSON.

No, there is no unit-tested class below 100% that needs completing for Step 6.
No, none of the top-level symbols added outside the coverage gate is
unreferenced.

### Feature integrity for Step 6

- **Existing feature behavior**: no shipped command uses the version domain
  before Step 9. Registering `npm` adds detection of `package.json` and
  `package-lock.json` at every participating root; the Step 2 to 5 version
  tests pass unchanged, and the uv evidence records are byte-identical
  after re-recording.
- **Reporting or diagnostics**: every refusal is a status 2 `SourceError`
  naming the file and the remedy; a local link names both roots, and the
  release-only refusal names the source, its value and the target.
- **Compatibility or rollout note**: `[source:npm] form` accepts
  `release-only`, `core` and `snapshot`. `check` reporting drift for a
  release-only value above the target arrives with the commands in Step 9;
  this step proves the planned refusal and the differing expected value it
  will report. The Step 5 entry above names `python_pair_edit`, renamed
  `pair_edit` in this step.

No existing feature or reporting capability appears impaired.

---

## Step 7. Maven reactor adapter

### Analysis of Step 7 implementation state

Yes. Step 7 has been fully implemented.

`tools/release_workflow/sources/xml_scan.py` records wanted element text with
its expat byte span, and the `maven` adapter, split between
`tools/release_workflow/sources/maven.py` (reactor discovery) and
`tools/release_workflow/sources/maven_references.py` (reference rules), sits
between `npm` and `pattern`, completing the design's order. It keeps each
module's own version, each internal parent version and each literal internal
dependency or dependency-management version on the snapshot form, leaves
`${project.version}`, absent managed versions, external parents,
dependencies, plugins and properties unchanged, and refuses properties,
ranges, profile modules, unresolvable groups, out-of-section internal
references and versions inherited from outside the reactor before any write.
Every POM it reads goes through the project's physical path policy first, so
modules, sources and claims use physical paths. The Maven fixture sets and the
combined five-file project joined the restoration matrix. Every planned test
and completion check is in place, and the command printed by `pw scope day`
reports `exit=0`.

Reviewer assessment for round 1: No. Module POM paths were only normalized
lexically, so a junction alias could bypass the physical file claim conflict
with a declared component, and discovery did not apply the project path
boundary before returning module sources.

Writer update for round 2: `paths.authorize_in` now holds the physical path
policy that `authorize_path` applies, `AdapterSettings.authorize` exposes it to
adapters, and the Maven adapter authorizes the root POM and every module POM
before reading it, keeping the physical path for modules, sources and claims.
Regressions cover the aliased component conflict (refused by `versions set`
before any write), two links to one module, modules outside the project and in
a nested repository, directly and through junctions, and supported in-project
links and component siblings.

Reviewer assessment for round 2: the round 1 finding is resolved. Root and
module POM authorization precedes reads, physical paths reach the existing
claim registry, and the path regressions exercise the production settings
policy. Authorizing the root POM also closes a linked-file entry point; the
module refusal identifies its declaring POM, declaration and policy reason.
The shared path-policy extraction preserves `authorize_path` behavior. The
writer's full speed walk ended 2026-11-10T18:40:00+01:00 with 6,193 tests,
`exit=0 cov=100 outliers=0 excluded=0 proof=speed reused=none`. Static review
finds no remaining implementation or unit coverage gap; the reviewer did not
rerun tests or coverage. The validation resolver matches the request.

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

- **XML scanner** (`sources/xml_scan.py`):
  - `scan(content, name, wanted)` checks strict UTF-8, then parses the bytes
    once with `xml.parsers.expat`, without namespace processing, keeping a
    stack of open elements named by their slash-joined path. Each element
    whose path the caller's expression fully matches becomes an `XmlValue`:
    its text without the surrounding XML whitespace, the byte span of that
    text (from the first character-data `CurrentByteIndex` to the end tag's,
    moved inward past whitespace, so a byte-order mark and CRLF bytes count),
    and its parent's start offset, which groups one `<dependency>`'s fields.
  - A comment, CDATA section, processing instruction or child element inside
    a wanted element, or span bytes that do not read as the parsed text (an
    entity or character reference), become the value's `problem`. The text
    stays readable for coordinates; `XmlValue.owned` refuses the span of such
    a field, naming the file, the path and the markup.
  - A declared encoding other than UTF-8, invalid UTF-8 and malformed XML fail.
    `PomDocument` gives `first` and `every` through a path index built once.
- **Reactor discovery** (`sources/maven.py`, `maven.ADAPTER`): name `maven`,
  forms `{snapshot}`, default `snapshot`, candidate file `pom.xml`.
  - The root `pom.xml` of each participating root starts a breadth-first
    walk. Each `<module>` resolves against its declaring POM's directory, as
    a POM file (`.xml`) or a directory's `pom.xml`, normalized. A missing
    module POM and a module declared twice fail; modules inside a
    `<profile>` fail as ambiguous.
  - Round 2: the root POM and every module POM go through
    `AdapterSettings.authorize` before they are read. A path outside the
    physical project root or entering a nested repository, directly or
    through a link, fails naming the declaring POM and the module; otherwise
    the physical path identifies the module, its sources and their claims, so
    two links to one POM are one module declared twice and a linked module
    that is also a component is claimed twice.
- **Path policy seam** (round 2, outside the plan's file list):
  `paths.authorize_in(root, supplied)` holds the existing physical policy,
  which `authorize_path(identity, supplied)` now delegates to unchanged;
  `AdapterSettings.authorize(path)` in `sources/model.py`;
  `settings.authorize_source` and `VersionSettings.authorize` apply it from
  the physical project root and turn its refusal into a `SourceError`.
  - Coordinates: the literal `artifactId` and the literal own or `<parent>`
    `groupId`; a property, a missing value, a root element other than
    `<project>` and an unreadable file fail.
  - Rendering returns the text bytes; `has_project_version` reports a
    candidate only for a POM with its own version text.
- **Reference rules** (`sources/maven_references.py`, plan decision Q10):
  - `PomModule` and `index`, the `(groupId, artifactId)` map; duplicate
    coordinates fail.
  - Own version: owned when present. When absent, the `<parent>` chain must
    stay inside the reactor and end in a module with its own version, each
    module's chain resolved once; an external parent, no parent and a loop
    fail with the remedy to declare a literal version.
  - Internal `<parent>` (literal coordinates naming a module): its version is
    owned and required; an external parent is never edited.
  - Each `<dependency>`, wherever it appears, is grouped from its recorded
    fields. One naming a module's `artifactId` is internal with a literal
    group or exactly `${project.groupId}` resolving to a module; another
    literal group is external; any other group, or none, fails as ambiguous
    (design decision Q12). An internal entry outside `project/dependencies`
    and `project/dependencyManagement/dependencies` fails (plan decision
    Q15). In those sections an absent version and exactly `${project.version}`
    stay; other versions are owned as
    `<section>/dependency[<group>:<artifact>]/version`, with `#2` and on for
    repeated entries.
  - Owned values must be literal: empty values, property expressions and
    ranges fail naming file, field and expression. Plugins and `<properties>`
    are never read.
- **Registry** (`sources/__init__.py`): `ADAPTERS = (anchor, python, npm,
  maven, pattern)`, the final order; `xml_scan` and `maven_references` join
  `SUPPORT_MODULES`.
- **Test support** (`version_support.py`): `gav`, `pom_xml`, `DEMO_GROUP` and
  `reactor_poms` (my-project's shape); `pair_edit` now keys its result by
  path relative to the root, so a reactor's several `pom.xml` stay apart; the
  `maven-reactor` (CRLF, external parent, plugin `${project.version}`),
  `maven-inherited` (byte-order mark, inherited versions, internal managed
  and `${project.version}` dependencies, four writes) and `combined`
  (`version.txt`, Python, npm, Maven and a pattern source, five writes)
  restoration sets.
- **Tests**:
  - `test_version_formats/test_xml_scan_tdd.py`: wanted paths among decoys,
    in LF, CRLF and behind a byte-order mark, with parent grouping; lookups;
    whitespace and attributes around an owned element; empty, self-closing
    and blank elements; the six kinds of markup inside an owned element;
    accepted and refused encodings, invalid UTF-8, malformed and empty input;
    byte offsets after multi-byte text.
  - `test_version_formats/test_version_formats_pbt.py` (property test
    needed): generated POMs with inner whitespace, attributes, indentation,
    decoys, line endings and an optional byte-order mark; the three owned
    spans hold their values and replacing them changes only those values.
  - `test_maven_sources/test_maven_sources_tdd.py`: my-project's shape
    through `detection.detect` with one load per POM; the release core;
    recursive, relative and file modules; missing, repeated and profile
    modules; the inherited group; coordinate failures; non-POM files; no
    POM; the `core` form refused by configuration; candidates and rendering.
  - `test_maven_sources/test_maven_references_tdd.py`: owned literal entries,
    managed and `${project.version}` entries, the inheritance chain,
    ambiguous and external groups, expressions and ranges in dependency,
    project and parent versions, POMs without a version under an external
    parent or without a parent, internal parent failures, untouched external parents,
    dependencies, plugins and properties, out-of-section internal references
    and ignored external ones, repeated entries, duplicate coordinates, a
    loop, markup in an owned field, and the component that is also a module.
  - `test_version_registry_tdd.py`: the final order and support modules;
    `test_version_restoration_tdd.py`: the three new sets at every write
    position.
- **Validation evidence**:
  - An expat probe in the scratch directory confirmed that
    `CurrentByteIndex` counts the byte-order mark and raw CRLF bytes, that
    references arrive as separate decoded character events and that CDATA
    has its own event.
  - Tests first: `ghog single` on the new and changed leaves failed at
    collection (five errors, `ImportError: cannot import name 'maven'`;
    2026-11-10T17:56).
  - After the implementation, the step 7 leaves with the restoration,
    detection, settings, npm, Python and evidence leaves passed (311 tests).
  - `ghog day --whole-suite`, the command printed by `pw scope day`, first
    failed at check.bat (pyright: a `Literal`-keyed dict in the property
    test); after the annotation it reported `exit=0` (2026-11-10T18:04).
  - `rg -n 'xml.etree' tools/release_workflow/sources` and
    `rg -n 'subprocess' tools/release_workflow/sources` find nothing; the
    registry test pins `("anchor", "python", "npm", "maven", "pattern")`.
  - Round 1 review validation: `ghog day --full=speed --whole-suite` exit 0,
    `cov=100 outliers=0 excluded=0` (2026-11-10T18:12). The reviewer found the
    lexical module paths (P2) by static review.
  - Round 2: the path tests in `test_maven_sources_tdd.py` (aliased
    component conflict through `set_versions` with no source or evidence
    write, two links to one module, outside, linked outside, nested and
    linked nested modules with the files unchanged, supported linked and
    sibling modules) and the Maven, paths, managed-files, settings,
    detection, restoration, Python and npm leaves passed (304 tests). A first
    run wrote the nested repository marker as a file, which the memory
    filesystem keeps as a directory; the fixture now writes `.git/HEAD`.
- **Line counts** (after round 2): `xml_scan.py` 191 (advisory 220),
  `maven.py` 158 (advisory 220), `maven_references.py` 243 (advisory 280),
  `version_support.py` 464 (+67, advisory +50), new test files 149, 281 and
  236 (advisory 180, 260 and 320), `test_version_formats_pbt.py` +48
  (advisory +40), `test_version_restoration_tdd.py` +2 (advisory +40: the
  new sets run through the existing parametrized matrix, so only its
  docstring changed), registry +2, initializer 3. Outside the plan's list,
  for the round 2 path policy: `paths.py` 152 to 164, `sources/model.py` 456
  to 469, `sources/settings.py` 193 to 210. Every Python file stays below
  650; the split guidance was not needed.

### New types or classes introduced for Step 7

- `tools.release_workflow.sources.xml_scan`: `XmlValue`, `PomDocument` and
  `scan` (private `_Open` and `_Scan`).
- `tools.release_workflow.sources.maven`: `MavenAdapter`, `ADAPTER` and
  `reactor`.
- `tools.release_workflow.sources.maven_references`: `PomModule`,
  `Coordinates`, `index`, `literal_coordinate` and `owned_sources` (private
  `_Dependency` and `_Rules`).
- Test support: `version_support.gav`, `pom_xml`, `reactor_poms` and
  `DEMO_GROUP`; the `test_maven_sources` test folder.
- Round 2 path policy: `tools.release_workflow.paths.authorize_in`;
  `AdapterSettings.authorize`; `VersionSettings.authorize` and
  `settings.authorize_source`; `RootSettings.authorize` in test support.

### Architecture check for Step 7

- **Layering**: the scanner, the adapter and the reference rules are domain
  code of the `sources` package. Source bytes come through `FileView`, and
  path authorization comes through the settings port. They never write, take
  the lock or start a process.
  They import only the standard library (`xml.parsers.expat`, no element
  tree) and the `sources` model and scanner.
- **Module split** (plan decision Q10): `maven.py` owns discovery and
  coordinates; `maven_references.py` owns the index and the owned-field
  rules and declares no adapter; the dependency runs one way, from `maven` to
  `maven_references`.
- **Claims and path boundary** (round 2): the adapter reaches the project's
  physical path policy through the `AdapterSettings.authorize` port, which
  `VersionSettings` implements with `paths.authorize_in`, the same policy
  `authorize_path` applies to managed destinations, so the domain imports no
  foundation path code and the policy lives once. Discovered POMs are keyed by
  their physical path, and the existing claim registry refuses one physical
  field claimed through a junction alias and a component root.

No, there is nothing that needs to be addressed: no DDD-Hexagonal violation or
smell is visible in this step.

### Performance check for Step 7

- **No new `O(n^2)` or `O(n log n)` path**: expat parses each POM once and
  each wanted value is measured once; the path index of a document is built
  once. Discovery visits each module once through a breadth-first queue and
  a set of declared paths. The reference rules use the coordinates
  dictionary and a set of module `artifactId`s for each dependency, group a
  document's dependency fields in one pass, and resolve each module's
  inheritance chain once, remembering the modules already resolved, so
  the work stays linear in modules and dependencies.
- **Bounded side effects**: none; detection reads the root `pom.xml` of each
  participating root and the module POMs it declares, each once per view.
- **Path policy**: one authorization per discovered POM checks its spelling
  and resolved ancestors, with work proportional to path depth. It performs
  no directory-tree scan or Git subprocess.

No, there is no performance issue that needs to be addressed.

### Unit test coverage check for Step 7

The coverage gate measures `tools` only (`[tool.coverage.run] source`), with
`*/tests/*` and `*/__init__.py` omitted.

- **`tools/release_workflow/sources/xml_scan.py`**: `test_version_formats/`
  reaches every handler (declaration, start, characters, comment, CDATA,
  processing instruction, end), the problem and reference paths, empty
  elements, `owned`, the lookups and every failure; covered.
- **`tools/release_workflow/sources/maven.py`**: `test_maven_sources_tdd.py`
  reaches discovery, file and directory modules, every failure, the
  authorization failure of a module outside the project or in a nested
  repository (directly and through junctions), linked and sibling modules,
  the no-POM root, rendering and candidates; covered.
- **`tools/release_workflow/sources/settings.py`** (`authorize`,
  `authorize_source`) and **`tools/release_workflow/paths.py`**
  (`authorize_in`): reached through `detection.detect` in the path tests,
  success and refusal; `authorize_path` keeps its existing tests; covered.
- **`tools/release_workflow/sources/maven_references.py`**: the two Maven
  test files reach every owned field, every inheritance branch (own version,
  internal chain, external parent, no parent, loop), every dependency branch
  (external, ambiguous, out of section, kept, managed, repeated) and every
  literal-value failure; covered.
- **Files outside the gate**: every new `version_support.py` symbol is
  referenced by the Step 7 tests and the restoration registry.

No, there is no unit-tested class below 100% that needs completing for Step 7.
No, none of the top-level symbols added outside the coverage gate is
unreferenced.

### Feature integrity for Step 7

- **Existing feature behavior**: no shipped command uses the version domain
  before Step 9. Registering `maven` adds reactor detection at every
  participating root; the Step 2 to 6 version tests pass unchanged, and
  `pair_edit` callers keep their keys because their files sit at the root.
- **Reporting or diagnostics**: every refusal is a status 2 `SourceError`
  naming the POM, the element or field and the remedy; a module outside the
  project or in a nested repository is refused at detection, naming the
  declaring POM, the module and the path policy's reason.
- **Compatibility or rollout note**: `[source:maven] form` accepts only
  `snapshot`. Internal plugin declarations are outside the reference model,
  as the design's "plugins are never written" states; an internal dependency
  of a plugin or a profile fails. `paths.authorize_path` keeps its behavior;
  it now delegates to `authorize_in`.

No existing feature or reporting capability appears impaired.

---

## Step 8. Tag classification, range selection and the release-version rule

### Analysis of Step 8 implementation state

Yes. Step 8 has been fully implemented.

`tools/release_workflow/tags.py` classifies stable, snapshot and other tag
names, reads eligibility from whole annotation lines, groups stable tags into
release boundaries that take the most restrictive class of their aliases and
the `vX.Y.Z` name when they have one (design decisions Q18 and Q19), and
fails on conflicting tags. `select_range` applies the seven-step ancestry
rule over the step 1 typed Git observations with at most four calls, and
`check_release_version` applies umbrella decision 33 with two. Every AC13,
AC14 and AC15 row of the design, the aliased-boundary cases and the
consumer-shaped histories are tested on declared histories, and every
selection and rule invocation asserts its recorded Git calls against the
plan's call table. `rg -n 'describe' tools/release_workflow/tags.py` finds
nothing, and the command printed by `pw scope day` reports `exit=0`.

Reviewer assessment for round 1: No. Several selection tests omitted the
complete recorded-call assertions the plan's completion criteria require (an
ambiguous aliased boundary, the eligible aliased baseline, an ambiguous
target, the canned records failure, the three consumer-shaped histories and
the generated chains), and two release-version cases did not assert their two
calls. No production defect was found.

Writer update for round 2: those tests now assert their complete ordered
calls, arguments included, one invocation at a time (`_take`) against the call
table's sequence (`_selection_calls`); the canned failure records the query it
refuses; the property test asserts the call sequence of every generated
selection, the no-candidate branch included; and both release-version cases
assert their two calls per invocation.

Independent reviewer reassessment for round 2: R1 is resolved. The formerly
unchecked cases now assert each invocation's ordered Git observations; the
consumer histories' candidate lists match their declared ancestry, and the
generated no-candidate branch asserts its calls before returning. Production
code and test-support digests match round 1. Static review finds no remaining
implementation, architecture or unit-coverage gap. The writer's speed-walk
evidence ended at 20:53:49 +01:00 with all 6284 tests passing,
`cov=100 outliers=0 excluded=0`; the reviewer ran no tests or coverage walk.
Only this Step 8 review metadata was edited by the reviewer in round 2.

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

- **Names** (`tools/release_workflow/tags.py`): `parse_name` reads `vX.Y.Z`
  and `X.Y.Z` as `StableName` with the token grammar, `-SNAPSHOT` in any case
  as `SnapshotName`, and returns `None` for every other name, other
  prereleases, `V`-prefixed, leading-zero and partial versions included.
- **Eligibility**: `eligibility(annotation)` works on nonblank lines. A
  trailer line starts with exactly `Release tooling:`, one space and a value
  that is not blank, and `[valid]` must match the whole line. No trailer
  (or a lightweight tag) is `HISTORICAL`; one trailer as the last line is
  `UNVALIDATED`, followed only by `[valid]` `VALIDATED`; several trailers,
  `[valid]` before the trailer, or anything else after it is `AMBIGUOUS`.
  `classify(record)` returns a `ClassifiedTag` for a stable name and `None`
  for snapshot markers and other names (the plan's `-> ClassifiedTag`
  signature widened so callers drop them in one pass).
- **Boundaries**: `boundaries(tags)` groups by version and by commit in one
  pass; a version on several commits, or a commit with several versions,
  raises `RangeError` naming the tags, before anything is excluded. A
  `Boundary` exposes its alias names, its `status` (`BoundaryClass`:
  ambiguous when any alias is, otherwise ineligible when any alias is an
  unvalidated engine tag, otherwise eligible), its `name` (the `vX.Y.Z`
  alias, otherwise the `X.Y.Z` alias) and its `spelled` aliases for
  diagnostics.
- **Range selection**: `select_range(git, *, cwd, target=None)` returns a
  `RangeSelection` (target, baseline or `None`, printed range, commit count,
  warnings).
  - A target that is not a stable name fails before any call; Git revisions
    are `HEAD` or `refs/tags/<name>` and the printed range uses plain names.
  - One `tag_records` call; a missing tag target becomes `RangeError` (status
    2) chained from `GitRevisionNotFoundError`, and any other Git failure
    propagates as `GitCommandError` (status 1).
  - A tag target's whole boundary must be eligible and is removed; HEAD keeps
    a boundary on HEAD as candidate.
  - One candidate is the baseline; several go through `independent_commits`
    (its command-line guard raising `GitCommandLineTooLongError`, status 1,
    before the call starts), and several tips or a version inversion fail.
  - `tag_names` between the baseline and the target: an ambiguous boundary
    there fails naming its aliases, an unvalidated one is excluded with a
    warning naming them; then `commit_count` of `baseline..target`.
  - Without a candidate, the range is the full history: the same checks run
    on the remaining boundaries from the records, then `commit_count` of the
    target.
- **Release-version rule**: `check_release_version(git, *, cwd, version)`
  refuses a malformed token (`VersionError`) or a snapshot (`RangeError`)
  before any call, then makes its two calls (all tag records, records merged
  into `main`): a version any stable tag names, in either spelling and
  whatever its class, is reserved; otherwise it must be numerically higher
  than the highest eligible boundary on `main`, grouped as the selector
  groups them. `RangeError(ValueError)` carries `exit_code = 2`.
- **Test support** (`version_support.py`): `ENGINE_TRAILER`, `annotation`
  (notes, trailer, `[valid]`), `chain` (a linear declared history) and
  `tagged_history` (a chain with tags by position over the sandbox's
  recording Git observations).
- **Tests**:
  - `test_release_tags/test_release_tags_tdd.py`: stable and snapshot names in
    both spellings and suffix cases, ignored names, every eligibility row
    (trailer inside a notes line, `Release tooling:` without a value, CRLF,
    trailing blank lines, `[valid][space]` with a trailing space), classification, the
    eight boundary class and name combinations, ordering and both conflicts.
  - `test_release_tags/test_release_ranges_tdd.py`: every AC13, AC14 and AC15
    row of the design; HEAD on a release; no candidate (none, snapshot and
    other tags only, a first tag target, an unvalidated tag only); several
    candidates; independent tips; inversion; the three conflicts; an
    ambiguous tag after the baseline; non-stable targets with no call; a
    missing target; a Git failure of the records call; 600 candidates over
    the command-line limit; the aliased cases of design decisions Q18 and
    Q19; the release-version rule (reserved, numeric bound with an unmerged
    higher tag, boundary classes, no eligible release, unusable versions);
    the three consumer-shaped histories. Every selection and rule invocation
    asserts its recorded calls against the call table, one invocation at a
    time where a test makes several (round 2).
  - `test_release_tags/test_release_tags_pbt.py` (property test needed):
    annotation classification against a reference predicate written another
    way, and linear chains of up to fifteen commits where the baseline is the
    nearest eligible tagged ancestor, the count its distance, each later
    unvalidated release warned about and the call sequence the call table
    gives for zero, one or several candidates (round 2).
- **Validation evidence**:
  - Tests first: `ghog single` on `test_release_tags` failed at collection
    (three errors, `ImportError: cannot import name 'tags'`;
    2026-11-10T19:43).
  - After the implementation, `test_release_tags` and `test_git` passed
    (152 tests).
  - `ghog day --whole-suite`, the command printed by `pw scope day`, first
    failed at check.bat (ty and pyright on two test typings, ruff PLR0913 on
    one parametrized test, radon grade C on three functions and the test
    reference predicate, each split into helpers); it then reported `exit=0`
    (2026-11-10T19:57).
  - `rg -n 'describe' tools/release_workflow/tags.py` finds nothing.
  - Round 1 review validation: `ghog day --full=speed --whole-suite` exit 0,
    `cov=100 outliers=0 excluded=0` (2026-11-10T20:13). The reviewer found
    the missing call assertions (R1) by static review; no production defect.
  - Round 2: with the complete call assertions, `ghog single` on
    `test_release_tags` passed (91 tests, 2026-11-10T20:36).
- **Line counts** (after round 2): `tags.py` 342 (advisory 380),
  `version_support.py` 497 (+33, advisory +40), new test files 126, 398 and
  111 (advisory 220, 380 and 120), initializer 3. Every Python file stays
  below 650; the split guidance was not needed.

### New types or classes introduced for Step 8

- `tools.release_workflow.tags`: `RangeError`, `StableName`, `SnapshotName`,
  `parse_name`, `Eligibility`, `eligibility`, `ClassifiedTag`, `classify`,
  `BoundaryClass`, `Boundary`, `boundaries`, `RangeSelection`,
  `select_range` and `check_release_version`.
- Test support: `version_support.ENGINE_TRAILER`, `annotation`, `chain` and
  `tagged_history`; the `test_release_tags` test folder.

### Architecture check for Step 8

- **Layering**: `tags.py` is release-domain code. It reads Git only through
  the typed `GitExecutionContext` observations added in Step 1 and the token
  grammar of `sources.model`; it starts no process of its own, writes
  nothing and holds no state between calls.
- **Ports**: tests answer the same four observations from the declared
  `ReleaseHistory`, so the selector is exercised without Git, and the calls
  it makes are the boundary the call table specifies.
- **Shared rule**: classification and boundary grouping are one code path
  for the selector and the release-version rule, so their classes cannot
  drift apart.

No, there is nothing that needs to be addressed: no DDD-Hexagonal violation or
smell is visible in this step.

### Performance check for Step 8

- **Linear normal path**: classification reads each
  annotation's lines once; grouping uses dictionaries by version and commit
  and sorts names or commits of a conflicting group for its error message
  (`O(k log k)` for a conflict involving `k` records); candidates, tips,
  the names between baseline and target
  and boundary aliases are compared through sets; the highest eligible
  boundary is one `max`. Normal selection is linear in the reachable tags.
- **Bounded side effects**: at most four Git calls per selection (records,
  tips, tags between, count) and two for the release-version rule, as the
  call table states; none when the target name is refused.

No, there is no performance issue that needs to be addressed.

### Unit test coverage check for Step 8

The coverage gate measures `tools` only (`[tool.coverage.run] source`), with
`*/tests/*` and `*/__init__.py` omitted.

- **`tools/release_workflow/tags.py`**: `test_release_tags/` reaches every
  name form, every eligibility branch, each boundary class and name rule,
  both conflicts, every target refusal, the missing-target conversion, the
  one-candidate, several-candidate, tips, inversion and no-candidate paths,
  the ambiguous and ineligible checks after the baseline and before the
  target, and every release-version outcome; covered.
- **Files outside the gate**: every new `version_support.py` symbol is
  referenced by the Step 8 tests.

No, there is no unit-tested class below 100% that needs completing for Step 8.
No, none of the top-level symbols added outside the coverage gate is
unreferenced.

The Git-call budget is a separate contract from branch coverage: after round
2, every selection and rule invocation asserts its complete recorded calls,
so an extra or repeated observation fails a test.

### Feature integrity for Step 8

- **Existing feature behavior**: no existing reader is switched; the range
  readers of `prepare-release` and the instructions keep their own query
  until item 7. Nothing calls `tags.py` yet; Step 9 adds `versions range`.
- **Reporting or diagnostics**: refusals are `RangeError` (status 2) naming
  the target, the conflicting tags, the tips, the inversion or the aliases;
  a missing tag target names the tag; Git execution failures and an
  oversized tips query keep their status 1 errors.
- **Compatibility or rollout note**: existing tags need no migration: none
  of the consumers' annotations holds a trailer, so their tags stay
  historical and eligible, and mixed `vX.Y.Z` and `X.Y.Z` histories select
  as before.

No existing feature or reporting capability appears impaired.

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
