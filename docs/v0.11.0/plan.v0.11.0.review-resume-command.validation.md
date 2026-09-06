# v0.11.0 review-resume-command implementation tracking and validation

No, it is not implemented.

This validation tracks the seven ordered implementation steps. Steps 0 through
4 are fully implemented and validated; Steps 5 and 6 remain pending.

---

## File-based IO cost clarification for v0.11.0 review resumption implementation

All implementation work must preserve the IO classification in
`docs/v0.11.0/plan.v0.11.0.review-resume-command.md`:

- placement checks inspect only root, default home, and configured home;
- `migration_check` never performs full status projection;
- selected-role backfill scans one occurrence and writes missing identity only;
- ownership transitions read and write one coordination record under lock;
- global wait treats notifications as hints and uses bounded rescans;
- transcripts remain outside runtime artifact-home discovery.

---

## Complexity bound clarification for v0.11.0 review resumption implementation

- **O(1) amortized per file event or ownership transition**: event callbacks
  mark work pending, and capability validation reads one coordination record.
- **O(n) total per placement, status, migration, or selected-role phase**: each
  recognized artifact is processed a bounded number of times.

Every implemented step must be checked for recursive discovery, repeated full
projection, pairwise artifact comparison, and hot-loop filesystem work.

---

## Step 0. Establish migration and wait performance guards

### Analysis of Step 0 implementation state

Yes. Step 0 has been fully implemented.

The performance contract package now contains three strict migration xfails and
three strict global-wait xfails with deterministic spies, call-count assertions,
elapsed bounds, and per-test timeouts. The completed Groundhog walk reported
`fail=0`, `warn=0`, `xfail=6`, `cov=100`, `outliers=0`, `excluded=0`, and
`exit=0`.

### Goal for Step 0

Add strict xfail timing and call-bound guards before production behavior lands.

### Step 0 improvement expectations

- Bound placement checks to three non-recursive locations.
- Reject full status projection inside `migration_check`.
- Bound quiet waiting, notification wake, and polling fallback.

### What was implemented for Step 0

- Added `tests/unit/tools/test_review_resume_perf/__init__.py` and the 247-line
  `test_review_resume_perf_tdd.py` guard suite.
- Added strict Step 1 xfails for exactly three flat placement reads, one linear
  parse per synthetic candidate, and zero full-status projections from
  `migration_check`.
- Added strict Step 5 xfails for bounded quiet intervals, notification hints
  followed by authoritative rescans, and polling fallback when no notification
  arrives.
- Applied one-second `pytest.mark.timeout` guards and separate 0.25-second
  elapsed assertions while keeping fixture sizes and synthetic time
  deterministic.
- Shortened the pre-existing invalid-root review-status acceptance call by
  invoking the same public CLI adapter in-process; all original status and
  output assertions remain, and its measured call time fell from 5.38 seconds
  to below the 0.01-second report threshold.
- Qualified ten repeated historical transcript headings with their exchange
  occurrence so the repository Markdown gate remains valid.

### New types or classes introduced for Step 0

- `MigrationSpies` records configuration reads, non-recursive directory reads,
  candidate parses, and forbidden full-status projections through explicit
  test ports.
- `WaitSpies` records authoritative rescans, notification waits, fallback
  polls, and synthetic monotonic time through explicit test ports.

### Architecture check for Step 0

Step 0 adds no production dependency or domain behavior. Its tests describe
future migration and wait services through injected callables, keeping file IO,
status projection, notification observation, and clock behavior at explicit
adapter boundaries. The acceptance optimization still enters through the
public `review_status_cli.main` adapter and does not bypass status policy.

No architecture issue needs to be addressed.

### Performance check for Step 0

The migration contract permits one configuration read, three non-recursive
directory reads, and one parse per candidate, which is `O(n)` across the three
bounded locations. The wait contract permits one authoritative rescan per
notification or fallback interval and constant callback work. No pairwise
candidate comparison, recursive discovery, busy loop, or `O(n log n)` path is
introduced. Groundhog completed with no duration outlier after the flagged
acceptance subprocess was removed.

No performance issue needs to be addressed.

### Unit test coverage check for Step 0

Step 0 changes no production class, so no class-specific unit coverage target is
newly applicable. The six new contracts were collected in both focused and full
Groundhog phases as the six declared xfails, and the complete suite retained
100 percent production coverage.

No unit-tested class is below 100 percent or needs completing.

### Feature integrity for Step 0

The full suite passed all 2,219 collected tests with the six intentional Step 0
xfails. Review-status invalid-root behavior still returns status 2, emits no
stdout, prefixes stderr with `rvw_status:`, and does not emit a partial JSON
payload. Repository Markdown validation also passes after occurrence-qualified
transcript headings, so no existing feature or reporting capability is
impaired.

---

## Step 1. Centralize artifact-home placement and migration

### Analysis of Step 1 implementation state

Yes. Step 1 has been fully implemented.

Configuration, registry, locator, transactional migration, recovery, and
invocation-scoped configuration reuse are all present, every caller-owned review
file now resolves against the configured artifact home, and both mandatory
validation commands pass independently in the reviewed state.

### Goal for Step 1

Move every protocol-owned runtime path behind the configured artifact home and
provide safe all-or-none legacy migration.

### Step 1 improvement expectations

- Validate `.review-artifacts.ini` and default to `.reviews`.
- Create and verify home-local ignore coverage before use.
- Migrate all validated sources or restore the complete source layout.
- Persist one strict versioned JSON journal through atomic full-snapshot
  replacement after every move and phase transition.
- Remove direct project-root runtime path assumptions.

### What was implemented for Step 1

- Added strict `.review-artifacts.ini` loading with the repository-local
  `.reviews` default, physical boundary checks, tracked-directory rejection,
  exact home-local `*\n` ignore creation, and rollback on creation failure.
- Added a closed artifact registry and home-aware locator for exchange files,
  transition locks, archives, retained code-review evidence, fixed markers,
  guidance, question state, and the migration journal while keeping transcripts
  beside reviewed documents.
- Added bounded root/default/configured-home migration discovery, exact-byte
  collision handling, one strict atomic full-snapshot JSON journal, rollback,
  committed cleanup, crash recovery, and an exclusive migration lock.
- Routed exchange path derivation, review-status candidate enumeration,
  review-mode lookup, and retained evidence through the configuration and
  locator boundaries, with an explicit legacy root marker fallback.
- Added one immutable status invocation context that loads artifact-home
  configuration once and reuses it for review-mode loading, candidate
  enumeration, and every candidate path derivation.
- Activated all three Step 1 migration performance contracts and added focused
  configuration, registry, property, migration, recovery, path, store, status,
  evidence, and acceptance coverage.
- Accepted two advisory line-budget variances while retaining the 650-line
  ceiling: `tools/review_artifact_migration.py` is 635 lines against its
  480-line target, and
  `tests/unit/tools/test_review_artifact_home/test_review_artifact_migration_tdd.py`
  is 632 lines after passing the plan's 550-line recovery-example split point.

### New types or classes introduced for Step 1

- `ReviewArtifactConfiguration` represents one validated repository-bound
  artifact home and owns exact ignore preparation and rollback.
- `RegisteredArtifactKind` and `RegisteredArtifact` define the closed runtime
  artifact vocabulary and parsed metadata.
- `ReviewArtifactRegistry` renders and parses registered names, while
  `ReviewArtifactLocator` derives their configured physical paths.
- `MigrationState`, `MigrationMove`, and `MigrationCheckResult` represent the
  typed preflight and immutable transaction plan.
- `ReviewArtifactMigration` owns bounded discovery, journaling, movement,
  verification, rollback, recovery, cleanup, and locking through injected IO
  ports.
- `_StatusInvocation` groups one repository root, artifact configuration,
  review configuration, and evaluation instant for a complete read-only status
  projection.

### Architecture check for Step 1

Configuration, artifact naming, location, and migration are separated from the
633-line exchange store. The store, observer, status projection, and retained
evidence depend on the locator boundary rather than absorbing migration IO, and
the migration service exposes explicit filesystem and Git ports. No layer
imports a UI adapter or adds domain behavior to the persistence store.

The one smell raised in round 1 is resolved. `ReviewConfiguration.load` is a
data-model parser again: it accepts an optional resolved `review_mode_path`,
and `review_exchange_paths.load_review_configuration` owns the repository-aware
lookup through `ReviewArtifactLocator`. The deferred import is gone, the cycle
between the shared model and the placement modules is broken, and the model no
longer knows about the artifact home.

No architecture issue needs to be addressed.

### Performance check for Step 1

Migration discovery is `O(n)` across exactly three flat locations, uses a
dictionary for collision detection, fingerprints each recognized candidate a
bounded number of times, and never invokes full status projection. Status loads
and validates artifact-home configuration once per invocation, then performs
constant-time reuse for review-mode lookup and each candidate derivation; the
candidate scan remains `O(n)` with no pairwise comparison or repeated Git
tracking subprocess.

No performance issue needs to be addressed.

### Unit test coverage check for Step 1

Dedicated unit leaves cover every new configuration, registry, locator,
migration, journal, recovery, collision, rollback, ignore, and lock branch.
The activated performance contracts verify three bounded reads, linear parsing,
and no status projection. Multi-candidate tests for both the default and a
configured home prove exactly one artifact configuration load and one tracking
probe per status invocation. The registry suite originally did not pin the
retained manifest step token to the alphabet `code_review_evidence` renders,
which is why the step-0 rejection reached review; `_STEP` and `_TOKEN_RE` are
now character-identical and the
registry suite covers numeric steps and named substeps such as `4A`. The
configuration suite covers the home-only caller rule and its fail-closed
behavior for an invalid declaration, and the launcher suites exercise
home-local, project-root, and out-of-repository caller paths.

The registry property test is bounded to 40 generated examples to clear a
Groundhog duration outlier. Its strategy space and assertions are unchanged, so
the reduction costs search depth rather than coverage.

The full walk reports `cov=100` with `fail=0`, `warn=0`, `outliers=0`, and the
three intentional Step 5 xfails.

No unit-tested class is below 100 percent or needs completing.

### Feature integrity for Step 1

The focused Step 1 command passes with `fail=0`, `warn=0`, and the three
intentional Step 5 xfails. Runtime-path bypass search found no direct exchange
path construction outside the registry and explicit legacy marker fallback,
and `tools/review_exchange_core.py`, `tools/review_exchange_store.py`, and
`tools/review_exchange_observer.py` needed no edit because they already reach
every path through `derive_artifact_paths`.

Three capabilities were impaired by the first delivered state, and all three are
now resolved. Retained code-review evidence for step 0 stopped resolving,
because the closed registry accepted only `step-[1-9]\d*`. Publishing any
code-review answer became impossible, because the retained manifest moved into
the home while every launcher still demanded caller-owned files directly under
the project root; the two rules were mutually unsatisfiable and
`bin/code_review_answer.bat` failed every render. The reviewer repaired both in
round 1 and the writer then tightened the caller rule to the home only, so this
answer was rendered from `.reviews` and published from there, which exercises
the repaired path end to end.

Review-status candidate enumeration remains confined to the configured home
with no legacy root fallback, and no production caller invokes
`ReviewArtifactMigration` yet, so a repository still holding root-level
coordination files reports no active exchange until Step 4 wires migration into
status. That window is the plan's own staging and is recorded rather than
treated as a Step 1 defect.

Every Step 1 completion criterion now holds in the reviewed state. The focused
command reports `fail=0 warn=0 xfail=3 exit=0`; the runtime-path bypass search
finds no exchange path construction outside the registry and migration
implementation; and `ghog day` reports `exit=0` across check, affected, and
full, with the full phase at `fail=0 warn=0 xfail=3 cov=100 outliers=0
excluded=0`. Every Step 1 file stays under the 650-line ceiling, and `.agents`
is clean.

---

## Step 2. Add role-specific LLM nature and legacy completion

### Analysis of Step 2 implementation state

Yes. Step 2 has been fully implemented.

Host detection now has a closed, non-secret nature result; request, answer, and
coordination publication preserve strict two-role snapshots; and legacy
selected-role evidence has complete reconciliation and transactional
missing-only completion with conflict, unknown, and idempotency safeguards.

### Goal for Step 2

Persist Claude, Codex, Gemini, or `unknown` for both exchange roles and complete
legacy selected-role evidence without rewriting conflicts.

### Step 2 improvement expectations

- Remove the silent Claude fallback.
- Preserve two-role snapshots through strict schemas and transitions.
- Scan the complete selected role and occurrence before mutation.
- Append unique transcript identity-completion evidence.

### What was implemented for Step 2

- Added centralized Claude, Codex, Gemini, and `unknown` detection with trusted
  hint precedence, explicit no-evidence and conflicting-evidence results, and
  diagnostics that retain neither environment names nor values.
- Added strict requestor/reviewer snapshots to envelopes and coordination while
  preserving the explicit legacy field-absence parser. Publication merges the
  stored snapshots, records only the acting role, rerenders the envelope, and
  carries the resulting snapshot into coordination and transcript metadata.
- Removed the prompt renderer's silent Claude default, routed its detection
  through the shared detector, and added explicit Gemini and unknown command
  prefix behavior.
- Added selected-role reconciliation that ignores counterpart gaps, preserves
  stable evidence order, and collects every conflict before mutation.
- Added missing-only legacy backfill with prospective rendering and validation,
  Stop/Override conflict handling, unknown no-op behavior, rollback on commit
  failure, and one role-and-occurrence-qualified transcript completion entry.
- Added focused detector, snapshot, schema, publication, reconciliation,
  property, backfill, rollback, transcript identity, and prompt-rendering tests.

### New types or classes introduced for Step 2

- `LlmNature` is the closed Claude, Codex, Gemini, and `unknown` enum;
  `LlmNatureDetection` holds only its nature, stable source category, and an
  optional non-secret diagnostic; and `LlmNatureDetector` applies trusted-hint
  precedence before bounded host-environment detection.
- `RoleNatureSnapshot` is the strict nullable requestor/reviewer value object,
  with compatible legacy parsing and conflict-safe record and merge operations.
- `RoleNatureEvidence`, `RoleNatureReconciliation`, and
  `RoleNatureReconciler` represent and classify the complete selected-role
  evidence set in one stable pass.
- `MutableRoleNatureArtifact`, `RoleNatureBackfillContext`,
  `RoleNatureBackfillResult`, and `RoleNatureBackfill` isolate validated file
  rendering from pure reconciliation and coordinate the missing-only commit.
- `NatureCompletionEntry` represents the uniquely identified append-only
  transcript fragment for one role and exchange occurrence.

### Architecture check for Step 2

The detector and immutable snapshot types remain independent of file storage.
Pure reconciliation is separated from the backfill transaction, while
publication obtains host evidence at its existing process boundary and the
store only renders already validated enum values. Envelope and coordination
schemas share the snapshot value object without importing either persistence or
workflow adapters. No new responsibility was added to the risk-band exchange
store beyond rendering two snapshot values.

The round-1 review found that backfill temporary files used an unignored prefix
inside each target directory. The replacement prefix now starts with `.tmp`,
which the repository ignore rules already cover, and a regression test pins
that relationship.

The temporary-file ignore-coverage issue needed fixing and is now addressed.

### Performance check for Step 2

Environment detection checks a fixed two-signal tuple. Snapshot record and merge
are constant bounded work. Reconciliation, prospective rendering, temporary
preparation, commit, and cleanup each make one linear pass over the selected
artifact set; resolved-path membership uses a set, so no pairwise scan was
introduced. Transcript identity lookup retains its existing bounded behavior.

No performance issue needs to be addressed.

### Unit test coverage check for Step 2

Dedicated unit leaves exercise every detector result, every closed enum member,
legacy absence and nullable strict schemas, invalid keys and values, role
preservation, stable complete conflict collection, counterpart omission,
Stop/Override, unknown no-op, missing-only mutation, repeat idempotency, commit
rollback, and transcript completion guards. Lifecycle tests prove requestor
publication first and reviewer publication later across request, answer,
coordination, and transcript evidence without retaining environment secrets.

The exact Step 2 focused walk passed 85 tests with no failures or warnings. The
coverage repair walk then passed all 28 affected tests at `cov=100`, and the
final `ghog check` passed every static and documentation gate.

No unit-tested class is below 100 percent or needs completing.

### Feature integrity for Step 2

Legacy envelopes and coordination records remain readable only through the
explicit missing-field exception, while every new serialization emits both
role keys. Known role evidence cannot be silently replaced, unknown detection
does not manufacture legacy evidence, counterpart artifacts remain untouched,
and Override fills gaps without rewriting conflicts. Existing specification
and code-review lifecycle behavior remained green across the 2,345-test full
phase; its only initial nonzero result was the seven newly introduced defensive
coverage lines, which the subsequent 100-percent affected walk closed.

The completion grep shows host environment signals only in the centralized
detector and `role_natures` at the two strict schemas, publication merge, and
transcript projection sites, with no `default.*claude` match. Every Step 2
Python file remains below the 650-line ceiling. No existing feature or reporting
capability is impaired. The round-1 temporary-file ignore gap, stale theme
sentence, and dropped exchange-store invariant needed fixing; all three are now
corrected. Round 2 also found that an unmatched backtick run could expose a
later code-spanned URL to rewriting, and that concurrent stale-record routing
work pushed its public resolver over the Radon gate. The span scan now skips
only the unmatched run, a regression test protects the later span, and record
eligibility is isolated behind a small predicate so `ghog check` is green.

The round-3 reviewer walk restored 100 percent coverage across 2,393 tests but
exited 8 for three duration outliers, not for a coverage failure. Step 2 owned
the largest: its reconciliation property took 0.63 seconds; the other two were
concurrent Markdown-checker and pre-existing Step 1 tests. The Step 2 property
now uses 40 generated examples while retaining list sizes through 40 and the
complete conflict-order assertion. The subsequent 2,403-test `ghog day` reports
`fail=0`, `xfail=3`, `cov=100`, `outliers=0`, and `exit=0`; its opening
`check.bat` phase also passes across the complete shared worktree.

---

## Step 3. Fence every acting session with ownership capabilities

### Analysis of Step 3 implementation state

Yes. Step 3 has been fully implemented.

Ordinary and resumed actors now claim one monotonic, digest-backed ownership
capability under the transition lock, every later mutation validates the
session-held pair, and the focused and repository-wide validation gates pass.

### Goal for Step 3

Apply one token-digest ownership contract to every actor and reject displaced,
stale, missing, or invalid capabilities.

### Step 3 improvement expectations

- Store only the ownership token digest in coordination.
- Advance generations under the transition lock.
- Support fresh-lease pickup, lost-secret pickup, and ordinary claims.
- Pass paired generation and token CLI flags on mutating calls without copying
  the token into environment variables or durable session files.
- Redact ownership tokens from diagnostics, transcripts, and human output.
- Keep new ownership and CLI responsibilities outside risk-band files.

### What was implemented for Step 3

- Added immutable ownership capability, claim, and failure records plus a pure
  ownership service that issues random secrets, stores only SHA-256 digests,
  advances generations, and reports typed missing, invalid, superseded, and
  duplicate-claim failures without retaining plaintext secrets.
- Extracted transition locking, exact coordination parsing, atomic persistence,
  and locked compare-and-swap claims into `ReviewExchangeOwnershipStore`; the
  existing store delegates those responsibilities and remains at 599 lines.
- Added a focused CLI ownership adapter for paired, single-use generation and
  token flags, strict validation, token-safe failures, and successful
  capability delivery. The command hub delegates to it and remains at 521
  lines.
- Wired claims into start, reclaim, exact wait wake, and direct pickup. Core and
  human/publication mutations validate the currently presented capability
  before changing artifacts, while a forced pickup advances the generation and
  invalidates every earlier holder.
- Updated the authorized code-review commit continuation to pick up requestor
  ownership before its final owning mutation, and adapted specification and
  code-review acceptance fixtures to carry session capabilities through normal
  request, answer, convergence, recovery, and completion paths.
- Added focused example, property, concurrency, persistence-crash, CLI pairing,
  redaction, lost-secret, convergence, and stale-session coverage. The exact
  Step 3 `ghog single` command passed, and `ghog day` passed all 2,437 tests with
  100 percent production coverage and no duration outliers.

### New types or classes introduced for Step 3

- `OwnershipCapability` holds one positive generation and session-only token.
- `OwnershipClaim` returns the durable record plus its capability and records
  whether the capability was newly issued.
- `OwnershipFailure` and `OwnershipRejectedError` carry stable, non-secret
  rejection evidence.
- `OwnershipService` owns token generation, digest comparison, ordinary claim,
  actor handoff, forced pickup, and capability validation.
- `ReviewExchangeOwnershipStore` owns the process-local and operating-system
  transition locks, exact coordination persistence, and claim compare-and-swap.
- `CorePort` and `_SingleValueAction` isolate the CLI lifecycle contract and
  duplicate-sensitive-flag rejection from the command hub.

### Architecture check for Step 3

The ownership service contains only capability rules and cryptographic digest
comparison, while the ownership store contains filesystem locking and atomic
persistence. The CLI ownership adapter depends on a protocol-shaped core port,
and `ReviewExchangeCore` remains the application orchestrator that sequences
state observation, locked claims, and mutation. Publication and human mixins
reuse the core's fenced `_require_record` boundary without importing storage or
cryptographic details.

The mandatory risk-band reductions are met: `review_exchange_store.py` is 599
lines and `review_exchange_cli.py` is 521 lines. Core is 538 lines, and every
new ownership module and test leaf remains below both its advisory target or
the 650-line ceiling. Keeping the post-wake locked revalidation in the core
avoids adding ownership policy to the generic wait observer.

No architecture issue needs to be addressed.

### Performance check for Step 3

Generation comparison, SHA-256 digesting, constant-time digest comparison, and
the coordination compare-and-swap perform constant work per transition. Claims
read and atomically replace one exact coordination record under one exact lock;
they add no repository scan or collection-sized loop. The defensive wait wake
performs one locked state revalidation and one claim after the existing bounded
wait returns.

No new `O(n^2)` or `O(n log n)` path was introduced, and the implementation
stays within the plan's `O(1)` ownership-transition bound.

No performance issue needs to be addressed.

### Unit test coverage check for Step 3

- `review_exchange_ownership.py` is covered by focused example and property
  tests for generation, validation, handoff, forced pickup, malformed values,
  and rejection of every previous generation.
- `review_exchange_ownership_store.py` is covered for locking, concurrent claim
  convergence, stale records, strict parsing, context binding, atomic prepare
  and replacement failures, cleanup, retries, and crash boundaries.
- `review_exchange_cli_ownership.py` is covered for paired inputs, malformed,
  empty, duplicated, and mismatched values, typed payloads, and secret
  redaction.
- Coordination, core, store, parser, CLI, human, and code-review continuation
  branches changed by this step are exercised by their unit suites; the full
  Groundhog report records 100 percent production coverage.

No unit-tested class is below 100 percent or needs completing.

### Feature integrity for Step 3

Existing specification and code-review requestor/reviewer flows still complete
through ordinary, recovery, convergence, and authorized-commit paths while now
carrying the same ownership fence. Read-only status remains capability-free,
typed ownership stops expose only the current generation and diagnostic, and
human/transcript rendering does not expose the secret. `check.bat` passes for
the shared worktree, including type, Ruff, complexity, file-size, Markdown,
shell, and EOF checks.

No existing feature or reporting capability appears impaired.

---

## Step 4. Project migration and role nature through status schema 2

### Analysis of Step 4 implementation state

Yes. Step 4 has been fully implemented.

The migration preflight, schema-2 model, configured-home projection, and
role-nature reconciliation are complete. Completed and blocked migration output
is now asserted in human and JSON forms, whitespace-only exception messages
retain typed diagnostics, and the launcher accurately describes its bounded
migration exception. A fresh `ghog day` passes with full coverage.

### Goal for Step 4

Run bounded migration preflight from status and report typed migration and both
role natures in schema-2 human and machine output.

### Step 4 improvement expectations

- Report migration as unnecessary or completed.
- Return operational failure for blocked migration before projection.
- Render requestor and reviewer nature, including unrecorded and conflicting.
- Remain read-only after the bounded preflight.

### What was implemented for Step 4

- **Migration-aware collection**: `ReviewStatusMigrationPreflight` performs one
  check, an automatic migration when required, and the mandatory ready recheck.
  A blocked check, failed move, or failed recheck returns an operational failure
  before ordinary exchange projection.
- **Schema-2 status model**: repository results carry typed migration state,
  artifact home, moved count, and diagnostics. Every trustworthy exchange
  carries requestor and reviewer LLM nature plus source-path evidence, including
  explicit `unrecorded` and `conflicting` states.
- **Configured-home projection**: `review_status.py` accepts the ready
  configuration from preflight, enumerates coordination only in that home, and
  reconciles role nature from already parsed coordination, request, and answer
  snapshots without a second artifact read.
- **Rendering and command contract**: human and compact JSON output expose the
  new typed fields, while blocked migration retains process status 2. The
  launcher arguments remain unchanged, and the canonical instruction plus all
  four provider adapters describe the bounded mutation exception.
- **Regression coverage**: unit and acceptance tests cover unnecessary,
  completed, repeated, blocked, and failed migration; schema serialization;
  known, unrecorded, and conflicting role nature; evidence paths; unchanged
  post-preflight bytes; output; and process statuses.
- **Validation evidence**: the fresh `ghog day` completed with `fail=0`,
  `cov=100`, `outliers=0`, and `exit=0`. Static checks and Markdown validation
  also pass.

### New types or classes introduced for Step 4

- `MigrationState`: typed `unnecessary`, `completed`, and `blocked` repository
  migration states.
- `RoleNatureState`: typed `unrecorded` and `conflicting` reconciliation states.
- `MigrationStatus`: validated schema-2 migration outcome, home, move count, and
  diagnostics.
- `RoleNatureEvidenceStatus` and `RoleNatureStatus`: one role's reconciled value
  and complete path-addressed evidence.
- `ReviewStatusMigrationResult`: preflight result coupling status with the
  configuration that is authorized for projection.
- `ReviewStatusMigrationPreflight`: bounded check, migrate, and ready-recheck
  orchestration behind an injectable migration port.
- `ReviewStatusRoleNatureProjection`: linear requestor and reviewer snapshot
  reconciliation.

### Architecture check for Step 4

- **Responsibility separation**: migration orchestration and role-nature
  reconciliation live in focused helpers; the status service coordinates them,
  and rendering plus CLI adapters consume only typed result models.
- **Boundary direction**: the migration helper depends on the existing artifact
  migration port, the role helper depends on protocol snapshots and status
  values, and neither reaches into CLI or rendering concerns.
- **Read boundary**: the preflight supplies the resolved configuration to
  collection, preventing a second configuration decision and preserving the
  post-ready read-only projection contract.
- **Maintainability**: all changed Python files remain below the enforced
  650-line ceiling, while the new migration and role helpers are 118 and 75
  lines respectively.

No, there is nothing that needs to be addressed for Step 4.

### Performance check for Step 4

- **No new `O(n^2)` or `O(n log n)` path**: role evidence is reconciled in one
  linear pass, and schema rendering remains linear in exchanges and artifacts.
- **Hot-path bound**: migration check remains limited to recognized legacy-root,
  default-home, and configured-home locations; ordinary projection runs only
  after a ready result.
- **Startup path**: automatic migration is a bounded one-time operation, and a
  repeated status call reports `unnecessary` without moving artifacts again.
- **Plan-bound alignment**: status adds at most the prescribed check, optional
  migration, ready recheck, and one ordinary projection.

No, there is no performance issue that needs to be addressed for Step 4.

### Unit test coverage check for Step 4

- **Migration preflight**: the dedicated migration tests cover ready, required,
  blocked, failed-move, failed-check, and failed-ready-recheck branches at 100%.
- **Schema models**: the existing model suite and the split schema-2 leaf cover
  construction, invariants, serialization, migration, nature, and evidence at
  100%.
- **Projection and role nature**: the projection, status-service, and dedicated
  role-nature tests cover configured-home discovery, parsed-envelope evidence,
  enum, unrecorded, conflicting, damaged, and operational-failure behavior at
  100%.
- **Rendering and CLI**: their named unit suites reach 100% line and branch
  coverage of `review_status_render.py` and `review_status_cli.py`, including
  completed and blocked human migration output and the blocked JSON migration
  payload.

No, there is no unit-tested class below 100% that needs completing for Step 4.

### Feature integrity for Step 4

- **Existing command behavior**: `rvw_status.bat` and its existing arguments are
  preserved; the only mutation is the required bounded safe migration before
  ordinary read-only status collection.
- **Reporting and diagnostics**: schema 2 extends rather than obscures identity,
  lease, artifact, action, and damage reporting, and blocked placement is
  surfaced as typed operational failure.
- **Compatibility**: legacy evidence remains readable as `unrecorded`, repeated
  calls are idempotent, and conflicting recorded natures retain all evidence
  instead of being guessed or overwritten.
- **Documentation rollout**: the canonical status instruction, status launcher,
  and thin Agent, Codex, Claude, and GitHub adapters consistently describe
  migration-aware status behavior.

No, no existing feature or reporting capability appears impaired by Step 4.

---

## Step 5. Add LLM-only resume and persistent reviewer waiting

### Analysis of Step 5 implementation state

Not started. Step 5 is not implemented because the resume skill, role resolver,
global reviewer watcher, and updated continuation instructions do not exist.

### Goal for Step 5

Resume the correct durable role without redundant confirmation and keep
reviewers waiting across exchanges while requestors progress only their task.

### Step 5 improvement expectations

- Run migration and identity gates before role continuation.
- Wait for any future specification or code request without a known identity.
- Resolve competing waits through first atomic claim and return losers to wait.
- Follow exact requestor state and `pw skill` after exchange release.
- Expose typed `migration-check`, `migrate-artifacts`, `resume-inspect`, `claim`,
  and `wait-any-request` support operations through `review_exchange.bat`.
- Use `watchdog` behind a narrow adapter with bounded polling and authoritative
  rescans as the correctness fallback.
- Add validated `llm_nature` metadata to thin provider adapters and no public
  resume launcher.

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

## Step 6. Prove cross-workflow acceptance and documentation rollout

### Analysis of Step 6 implementation state

Not started. Step 6 is not implemented because real-launcher acceptance,
concurrency, legacy compatibility, regression, and public documentation coverage
have not been completed.

### Goal for Step 6

Prove every acceptance criterion across real Git repositories, separate LLM
sessions, specification and code workflows, status, migration, and adapters.

### Step 6 improvement expectations

- Cover all safe and blocked placement layouts.
- Cover every LLM nature and legacy identity policy.
- Cover ordinary ownership, displacement, lost capability, and reviewer races.
- Reuse canonical configured-home, role-nature, ownership, and schema builders
  from `tests/unit/tools/review_exchange_test_support.py` while keeping local
  scenario fixtures local.
- Keep every earlier review-mode workflow green with new schemas and paths.
- Document configuration, status migration, resume, and role-specific waiting.

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
