# v0.11.0 review-resume-command implementation plan -- durable continuation

Implement configurable review evidence, role-specific LLM identity, and safe
continuation through ordered protocol slices.

- **Placement first**: centralize artifact discovery and complete legacy
  migration before changing exchange schemas.
- **One ownership contract**: add the generation and token-digest fence as its
  own cross-cutting step for ordinary and resumed actors.
- **Role-specific continuation**: finish with status integration, the LLM-only
  resume skill, persistent reviewer waiting, and full acceptance coverage.

## Plan goal for v0.11.0 review-resume-command

Implement the complete behavior from
`docs/v0.11.0/design.v0.11.0.review-resume-command.md` and its consolidated
feature request without reopening the settled choices.

- **Step 0 goal**: add time-bound and complexity guards before production work.
- **Step 1 goal**: implement the artifact-home declaration, registry, placement
  check, transactional migration, and locator adoption.
- **Step 2 goal**: add LLM-nature detection, strict two-role snapshots, legacy
  reconciliation, and missing-only backfill.
- **Step 3 goal**: implement uniform ownership capabilities and reject displaced
  or competing actors safely.
- **Step 4 goal**: advance review status to schema 2 with migration and role
  nature in human and machine output.
- **Step 5 goal**: add the LLM-only resume skill, automatic ownership pickup,
  role resolution, global reviewer wait, and requestor continuation from a
  bare `resume` request.
- **Step 6 goal**: prove the complete feature through real launchers, concurrent
  sessions, migration recovery, adapters, and documentation acceptance tests.

---

## Scope anchors for v0.11.0 review-resume-command plan

This plan implements these settled outcomes:

1. Every protocol-owned runtime artifact resolves through one repository-local
   home, defaulting to `.reviews`, and legacy layouts migrate all or none.
2. Every new exchange preserves requestor and reviewer LLM nature while legacy
   evidence remains readable and can be completed by its owning role.
3. A bare `resume` request resolves the role, automatically acquires or replaces
   the session capability, and continues immediately, while reviewers consume
   any future request and requestors progress only their owning task.
4. Every acting session uses the same generation and secret-token capability,
   with only the digest stored in coordination.

The following are in scope:

- `.review-artifacts.ini`, the explicit artifact registry, local ignore
  coverage, migration journal, recovery, and collision diagnostics;
- Claude, Codex, Gemini, and `unknown` host evidence;
- status schema 2 and the bounded status migration exception;
- request, answer, coordination, retained, consumed, transcript, wait, and
  continuation identity updates;
- an LLM skill with thin Claude, Codex, Gemini, and GitHub-compatible adapters;
- exact requestor continuation and identity-free reviewer waiting;
- existing specification, code-review, status, prompt-workflow, adapter, and
  documentation regression suites.

The following remain outside this plan:

- moving versioned review transcripts out of `docs`;
- a repository-root, batch, or shell `rvw_resume` command;
- automatic ordering of several available requests;
- replacing conflicting recorded LLM nature;
- reopening completed documents or umbrella status rows from earlier topics.

---

## Complexity bound clarification for v0.11.0 review resumption

- **O(1) amortized per file-system event**: directory notifications only mark
  the reviewer wait dirty; they never perform projection work in the callback.
- **O(n) per placement or status phase**: each recognized artifact in the three
  inspected locations is parsed, fingerprinted, or projected a bounded number
  of times.
- **O(n) per selected occurrence backfill**: selected-role evidence is scanned
  once before any rewrite and committed once after validation.
- **O(1) per transition**: ownership generation and token-digest checks operate
  on one coordination record under its transition lock.

No implementation may add pairwise artifact comparison, recursive repository
search, repeated full status projection inside `migration_check`, or event-loop
work with `O(n log n)` or `O(n^2)` cost.

---

## File-based IO cost clarification for v0.11.0 review resumption

| Flow | Reads | Writes | Bound |
| --- | --- | --- | --- |
| Artifact location | Optional root declaration and Git tracking evidence | None | One small configuration read per loaded workflow context; cache within one invocation. |
| Migration check | Root, default home, configured home, and registered candidate headers | None | Three non-recursive directory reads and one pass over recognized candidates; no status projection. |
| Migration | Validated source set and journal recovery state | Home ignore file, journal, atomic moves | One journaled transaction; no copy of unrelated files and no partial destination layout. |
| Status | Ready artifact home and active coordination candidates | Migration only when preflight requires it | One placement preflight followed by one ordinary read-only projection. |
| Role backfill | Selected occurrence and selected-role artifacts | Missing nature fields and one transcript completion entry | One pre-scan and one atomic missing-only commit; no repository-wide rewrite. |
| Ownership | One coordination record | One locked generation and digest transition | Constant work per actor claim or mutation. |
| Global reviewer wait | Request-artifact directory events and bounded rescans | Claim only after selection | Event hints plus bounded polling; full parse only for recognized request candidates. |

The runtime loading path must use the declaration and locator as a tiny index
read rather than repeatedly loading every artifact. Transcripts remain outside
the runtime artifact-home scan.

---

## Implementation decisions for v0.11.0 review resumption

| Question | Decision | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | Pass the ownership generation and token as paired CLI flags on each mutating call. The threat model is a displaced LLM session with repository access, not a hostile local user inspecting live process arguments; the displaced session cannot recover another session's arguments, while a file or environment copy would be reachable. | Step 3 ownership CLI, mutation tests, redaction checks, and completion grep. | Environment variables create a second reachable copy; a session-local capability file creates durable secret material and cleanup races. |
| Q02 | Declare `watchdog` as a direct runtime dependency behind a narrow notification adapter, retain bounded polling, and treat every event as a hint followed by an authoritative rescan. | Step 5 wait implementation, dependency files, notification tests, and Step 6 acceptance. | Hand-written platform watchers multiply platform code; polling alone does not provide the settled native-notification path. |
| Q03 | Put a schema-validated, non-secret `llm_nature` metadata field on each thin provider adapter while keeping every adapter body a canonical direct pointer. | Step 5 provider adapters, structure tests, role resolution, and Step 6 acceptance. | Body prose duplicates canonical rules; launcher environment injection adds public runtime machinery and omits direct skill invocation. |
| Q04 | Use one strict versioned JSON migration journal at a known path, atomically replacing the complete snapshot after every move or phase transition. | Step 1 migration service, recovery tests, and performance guards. | Append-only journals require partial-line recovery; multiple marker files make transaction state ambiguous. |
| Q05 | Expose typed `migration-check`, `migrate-artifacts`, `resume-inspect`, `claim`, and `wait-any-request` operations through `review_exchange.bat`; keep sequencing in the LLM skill and add no resume launcher. | Step 5 CLI support, canonical resume instruction, tests, and completion grep. | A generic action multiplexer weakens per-operation contracts; a second support launcher duplicates shared protocol safety. |
| Q06 | Add `tests/unit/tools/review_exchange_test_support.py` for canonical configured-home, role-nature, ownership, and schema builders while retaining local fixtures for scenario-specific behavior. | Step 6 affected suites, line budgets, and regression coverage. | Per-suite builders duplicate cross-cutting defaults; a global pytest plugin hides setup and increases unrelated coupling. |
| Q07 | Make the foreground `wait-any-request` command return exactly one typed terminal result for a claim, ambiguity, graceful cancellation, invalid input, or operational failure, without persisted wait state. | Step 5 wait CLI, instruction, and tests. | Idle progress; an LLM polling loop; a durable waiter manager. |

---

## Confirmed technical facts for v0.11.0 plan viability

**Relevant Python files over the 650-line repository limit**:

- None. No currently relevant production Python file exceeds 650 physical
  lines.

**Relevant Python files in the 550-through-650 risk band**:

- `tools/review_exchange_store.py`: 633 lines. Add no new ownership or migration
  responsibility in place; extract storage helpers into new modules.
- `tools/review_exchange_cli.py`: 558 lines. Add no resume or capability branch
  in place; route those operations through a new CLI support module.
- `tools/review_exchange_models.py`: 555 lines. Keep new nature and ownership
  records in focused modules and reduce imports if this file would grow.
- `tests/unit/tools/test_review_exchange_cli/test_review_exchange_cli_tdd.py`:
  615 lines. Put new capability and resume CLI cases in new test leaves.
- `tests/unit/tools/test_review_exchange_acceptance/test_review_exchange_acceptance_tdd.py`:
  604 lines. Put the new end-to-end scenarios under `tests/acceptance/review_resume`.

**Relevant Python files below 550 and safe to extend**:

- `tools/review_exchange_core.py`: 462 lines.
- `tools/review_exchange_paths.py`: 231 lines.
- `tools/review_exchange_models_envelope.py`: 220 lines.
- `tools/review_exchange_models_coordination.py`: 238 lines.
- `tools/review_exchange_state.py`: 277 lines.
- `tools/review_exchange_wait.py`: 209 lines.
- `tools/review_exchange_observer.py`: 196 lines.
- `tools/review_exchange_cli_parser.py`: 132 lines.
- `tools/review_status.py`: 509 lines; prefer focused migration and role-nature
  helpers before this file enters the risk band.
- `tools/review_status_models.py`: 408 lines.
- `tools/review_status_render.py`: 119 lines.
- `tools/review_status_cli.py`: 103 lines.
- `tools/prompt_workflow_render.py`: 88 lines.

**New production modules for v0.11.0**:

- `tools/review_artifact_configuration.py`.
- `tools/review_artifact_registry.py`.
- `tools/review_artifact_migration.py`.
- `tools/llm_nature.py`.
- `tools/review_role_nature.py`.
- `tools/review_exchange_ownership.py`.
- `tools/review_exchange_ownership_store.py`.
- `tools/review_exchange_cli_ownership.py`.
- `tools/review_status_migration.py`.
- `tools/review_status_role_nature.py`.
- `tools/review_resume.py`.
- `tools/review_resume_wait.py`.
- `tools/review_exchange_cli_resume.py`.

**Other facts affecting the plan**:

- `rvw_status.bat` is the existing public status launcher; status remains the
  only command allowed to migrate as part of ordinary reporting.
- `bin/review_exchange.bat` is the shared protocol command surface; support
  operations may be added there, but no `rvw_resume` launcher may be created.
- Provider Markdown files are thin pointers to canonical instructions and must
  follow `rules/llm-specific-adapters.md`.
- Existing exact waits require a complete identity and bounded timeout; the
  global request watcher is a separate operation.
- Existing schemas are strict, so legacy and schema-2 parsing must be explicit
  rather than accepting unknown fields broadly.

---

## Current test-tree validation snapshot for v0.11.0 review resumption

Existing packages that must remain green:

- `tests/unit/tools/test_review_exchange_paths` for derivation and ignore
  validation.
- `tests/unit/tools/test_review_exchange_models` for strict envelope and
  coordination schemas.
- `tests/unit/tools/test_review_exchange_store` and
  `tests/unit/tools/test_review_exchange_lifecycle` for persistence, transition,
  recovery, and transcript behavior.
- `tests/unit/tools/test_review_exchange_cli` for command input and result
  contracts.
- `tests/unit/tools/test_review_status*` and `tests/acceptance/review_status` for
  status schema, projection, rendering, CLI, and launcher behavior.
- `tests/unit/tools/test_spec_review_requestor_acceptance`,
  `test_spec_reviewer_acceptance`, `test_code_review_requestor_acceptance`, and
  `test_code_reviewer_acceptance` for role workflows.
- `tests/unit/tools/test_prompt_workflow_skill` and
  `test_instruction_structure` for routing and thin adapters.
- `tests/unit/tools/test_review_mode_docs_acceptance` for documented public
  behavior.

New test leaves:

- `tests/unit/tools/test_review_resume_perf`.
- `tests/unit/tools/test_review_artifact_home`.
- `tests/unit/tools/test_llm_nature`.
- `tests/unit/tools/test_review_role_nature`.
- `tests/unit/tools/test_review_exchange_ownership`.
- `tests/unit/tools/test_review_status_migration`.
- `tests/unit/tools/test_review_resume`.
- `tests/unit/tools/test_review_resume_instruction`.
- `tests/acceptance/review_resume/test_review_resume_acceptance`.

Property tests are required for normalized repository-relative paths, artifact
registry round trips, role snapshot reconciliation, and monotonic ownership
generations. Time-bound examples are a better fit than property tests for file
notifications and process waits.

---

## Runtime file note for v0.11.0 review resumption

- `.review-artifacts.ini` is optional versioned configuration and is not a
  runtime artifact.
- `.reviews/.gitignore` is generated before first use and remains untracked
  under its own catch-all rule.
- `.reviews/*` contains only registered runtime artifacts, including the
  migration lock and journal.
- Caller-owned renderer inputs remain outside protocol artifact paths until all
  producing workflows are migrated through the shared locator.
- `docs/.../review.*.md` transcripts remain versioned beside reviewed documents.

---

## Shared execution command checklist for all v0.11.0 review-resume steps

Apply this checklist to every numbered step with its exact paths.

1. Count physical lines before edits for every involved file.
2. Add or update the step tests before production behavior.
3. Run `ghog single` with all focused test files for the step.
4. Run the step-specific `rg` checks for fields, operations, paths, instructions,
   adapters, and prohibited root assumptions.
5. Run `ghog day` repeatedly until it reports the objective with `exit=0`.
6. Count physical lines after edits and compare every Python file with its
   baseline, policy band, advisory estimate, and 650-line ceiling.
7. Stop and perform the stated responsibility split if a Python file exceeds
   650 lines.
8. Record advisory variance without marking the step incomplete when the file
   remains at or below 650.

## Ready-to-run commands for all v0.11.0 review-resume steps

- Physical line count: `(Get-Content -LiteralPath '<path>').Count`
- Targeted tests: `ghog single <step-test-files>`
- Grep checks: `rg -n '<step-pattern>' <step-paths>`
- Shared gate loop: `ghog day`, repeated until it reports `exit=0`
- Physical line recount: `(Get-Content -LiteralPath '<path>').Count`

---

## Numbered implementation steps for v0.11.0 review resumption

### Step 0. Establish migration and wait performance guards

#### Step 0 analysis and intent for bounded preflight behavior

Issues to address:

- `migration_check` must remain materially cheaper than full status collection.
- The open-ended reviewer wait must not busy-loop or depend solely on native
  events.
- No test currently guards the three-location scan or quiet-wait cost.

Fix intent:

- Add strict xfail performance and call-bound tests before production modules
  exist.
- Assign every gate to the step that removes its xfail marker.

Expected outcome:

- Migration tests fail if status projection is called or discovery becomes
  recursive.
- Wait tests fail if a quiet interval performs unbounded rescans or misses the
  polling fallback.

Step framing:

- Design link: Complexity bound and file-based IO cost clarifications.
- Execution checklist reference: Shared execution command checklist for all
  v0.11.0 review-resume steps.

#### Step 0 implementation for performance guards

**Files involved**:

- `tests/unit/tools/test_review_resume_perf/__init__.py` (new, to be created).
- `tests/unit/tools/test_review_resume_perf/test_review_resume_perf_tdd.py` (new,
  to be created).

**Tests first**:

- Mark strict xfail tests with `pytest.mark.timeout` for three non-recursive
  placement reads, linear candidate parsing, quiet global waiting, notification
  wake, polling fallback, and no full status call from migration check.
- Keep synthetic fixture sizes deterministic and assert call counts as well as
  elapsed bounds.

**Classes and behavior**:

- Test-only spies model configuration reads, directory enumeration, candidate
  parsing, status projection, notification hints, and fallback polls.

**Completion criteria**:

- `ghog single tests/unit/tools/test_review_resume_perf/test_review_resume_perf_tdd.py`
  passes with only the declared strict xfails.
- `rg -n "xfail|timeout|migration|notification|poll" tests/unit/tools/test_review_resume_perf`
  lists every gate and owning step.
- `ghog day` reports `exit=0`.

#### Step 0 addendums for performance guards

Line-budget checkpoint:

- `tests/unit/tools/test_review_resume_perf/__init__.py`: before 0; below-550
  safe; ceiling 650; expected at or below 5 lines (advisory).
- `tests/unit/tools/test_review_resume_perf/test_review_resume_perf_tdd.py`:
  before 0; below-550 safe; ceiling 650; expected at or below 260 lines
  (advisory).

Split guidance:

- Split notification timing into a sibling conventional test leaf if the test
  file approaches 550 lines; do not loosen timeouts to hide repeated IO.

Full workflow timing run readiness:

- `tests/unit/tools/test_review_resume_perf/test_review_resume_perf_tdd.py`;
  `ghog day`.

Time-gated status for Step 0:

- Strict xfails remain until Step 1 owns migration gates and Step 5 owns global
  wait gates.

---

### Step 1. Centralize artifact-home placement and migration

#### Step 1 analysis and intent for one runtime evidence home

Issues to address:

- Runtime paths are derived at the project root and status enumerates root-level
  coordination files.
- There is no strict versioned declaration, kind registry, home-local ignore
  coverage, or all-or-none migration recovery.
- The 633-line store module cannot absorb migration responsibility.

Fix intent:

- Add focused configuration, registry, and migration modules and route all
  exchange path derivation through them.
- Keep journal, rollback, collision checks, and home creation outside the store.
- Remove Step 0 migration xfails.

Expected outcome:

- Default and configured homes produce identical canonical runtime paths.
- Root/default/configured evidence migrates in one recoverable transaction or
  remains wholly at source.

Step framing:

- Design link: Versioned artifact-home declaration through transactional
  migration.
- Execution checklist reference: Shared execution command checklist for all
  v0.11.0 review-resume steps.

#### Step 1 implementation for artifact placement

**Files involved**:

- `tools/review_artifact_configuration.py` (new, to be created).
- `tools/review_artifact_registry.py` (new, to be created).
- `tools/review_artifact_migration.py` (new, to be created).
- `tools/review_exchange_paths.py` (existing, to be updated).
- `tools/review_exchange_core.py` (existing, to be updated).
- `tools/review_exchange_store.py` (existing, to be updated only for delegation).
- `tools/review_exchange_observer.py` (existing, to be updated).
- `tests/unit/tools/test_review_artifact_home/__init__.py` (new, to be created).
- `tests/unit/tools/test_review_artifact_home/test_review_artifact_configuration_tdd.py`
  (new, to be created).
- `tests/unit/tools/test_review_artifact_home/test_review_artifact_registry_tdd.py`
  (new, to be created).
- `tests/unit/tools/test_review_artifact_home/test_review_artifact_registry_pbt.py`
  (new, to be created).
- `tests/unit/tools/test_review_artifact_home/test_review_artifact_migration_tdd.py`
  (new, to be created).
- `tests/unit/tools/test_review_exchange_paths/test_review_exchange_paths_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_review_exchange_store/test_review_exchange_store_validation_tdd.py`
  (existing, to be updated).

**Tests first**:

- Cover absent and valid declaration, every invalid path class, symlink escape,
  tracked-directory rejection, duplicate keys, and portable relative output.
- Cover every registered artifact kind, role attribution, identity parser,
  transcript exclusion, and unrelated `a.*` rejection; property-test registry
  render/parse round trips.
- Cover new-home ignore creation and Git verification, existing uncovered home,
  multi-source merge, collision, byte mismatch, journal rollback, committed
  cleanup, repeated check, and repeated migration.
- Cover a single known-path, strict versioned JSON journal whose complete
  snapshot is atomically replaced after every move and phase transition;
  malformed, truncated, or unsupported snapshots must block recovery.
- Update path and store tests so no runtime artifact assumes `PRJ_DIR` directly.
- Remove the Step 0 migration xfails without changing their bounds.

**Classes and behavior**:

- `ReviewArtifactConfiguration`: strict `.review-artifacts.ini` parsing and
  repository-boundary validation.
- `ReviewArtifactRegistry`: closed artifact-kind metadata and name parsing.
- `ReviewArtifactLocator`: home-aware derivation replacing direct root joins.
- `MigrationCheckResult` and `ReviewArtifactMigration`: ready,
  migration-required, blocked, journaling, rollback, and recovery.
- `ReviewArtifactMigration` owns one atomic JSON snapshot journal rather than
  append-only records or per-phase marker files.

**Completion criteria**:

- `ghog single tests/unit/tools/test_review_resume_perf/test_review_resume_perf_tdd.py tests/unit/tools/test_review_artifact_home tests/unit/tools/test_review_exchange_paths tests/unit/tools/test_review_exchange_store/test_review_exchange_store_validation_tdd.py`
  passes.
- `rg -n "project_root /.*review|glob\(.*review-active" tools/review_exchange_* tools/review_status.py`
  finds no runtime path bypass outside the registry implementation.
- `ghog day` reports `exit=0`.

#### Step 1 addendums for artifact placement

Line-budget checkpoint:

- New production modules: before 0; below-550 safe; ceiling 650; configuration
  target 220, registry 320, migration 480 lines (advisory).
- `tools/review_exchange_paths.py`: before 231; below-550 safe; ceiling 650;
  expected at or below 300 lines (advisory).
- `tools/review_exchange_core.py`: before 462; below-550 safe; ceiling 650;
  expected at or below 500 lines (advisory).
- `tools/review_exchange_store.py`: before 633; risk band; ceiling 650; target at
  or below 620 only because migration-related path logic is extracted.
- `tools/review_exchange_observer.py`: before 196; below-550 safe; ceiling 650;
  expected at or below 230 lines (advisory).
- New artifact-home tests: before 0; each below-550 safe; ceiling 650; each
  expected at or below 450 lines (advisory).
- Existing path test: before 350; below-550 safe; ceiling 650; expected at or
  below 470 lines (advisory).

Split guidance:

- Do not grow `review_exchange_store.py`; move all journal and migration IO into
  `review_artifact_migration.py` and storage seams into focused helpers.
- Split migration recovery tests from ordinary migration examples before either
  test file reaches 550 lines.

Full workflow timing run readiness:

- Step 1 focused tests listed above; `ghog day`.

Time-gated status for Step 1:

- Migration-check performance gates are active and no longer xfailed.

---

### Step 2. Add role-specific LLM nature and legacy completion

#### Step 2 analysis and intent for host identity evidence

Issues to address:

- Host detection silently defaults to Claude and has no Gemini or `unknown`.
- Strict envelopes and coordination records carry roles but no role-nature map.
- Legacy evidence needs complete selected-role scanning and atomic missing-only
  completion without changing counterpart evidence or conflicts.

Fix intent:

- Add focused detector and reconciliation modules, then extend strict schemas
  and transcript publication with two-role snapshots.
- Keep legacy parsing explicit and append transcript completion entries with
  unique role and occurrence headings.

Expected outcome:

- New exchanges preserve both role natures as they become known.
- Legacy selected-role evidence is classified and completed exactly once, while
  conflicts and `unknown` follow the settled rules.

Step framing:

- Design link: LLM-nature detection through legacy role evidence and backfill.
- Execution checklist reference: Shared execution command checklist for all
  v0.11.0 review-resume steps.

#### Step 2 implementation for role identity

**Files involved**:

- `tools/llm_nature.py` (new, to be created).
- `tools/review_role_nature.py` (new, to be created).
- `tools/review_exchange_models_envelope.py` (existing, to be updated).
- `tools/review_exchange_models_coordination.py` (existing, to be updated).
- `tools/review_exchange_publication.py` (existing, to be updated).
- `tools/review_exchange_transcript_identity.py` (existing, to be updated).
- `tools/prompt_workflow_render.py` (existing, to be updated).
- `tests/unit/tools/test_llm_nature/__init__.py` (new, to be created).
- `tests/unit/tools/test_llm_nature/test_llm_nature_tdd.py` (new, to be created).
- `tests/unit/tools/test_review_role_nature/__init__.py` (new, to be created).
- `tests/unit/tools/test_review_role_nature/test_review_role_nature_tdd.py` (new,
  to be created).
- `tests/unit/tools/test_review_role_nature/test_review_role_nature_pbt.py` (new,
  to be created).
- `tests/unit/tools/test_review_exchange_models/test_review_exchange_models_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_review_exchange_models/test_review_exchange_models_validation_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_transcript_identity_tdd.py`
  (existing, to be updated).

**Tests first**:

- Cover trusted host hint precedence, Claude, Codex, Gemini, no evidence,
  conflicting evidence, and non-persistence of secret environment values.
- Cover legacy absent field, `null`, all supported enums, unknown, strict unknown
  values, requestor-first and reviewer-later snapshots, and preservation across
  transitions.
- Property-test reconciliation ordering and complete conflict collection.
- Cover current-role missing-only backfill, counterpart omission, conflict
  Override and Stop, unknown no-backfill, atomic failure, unique transcript
  completion headings, and idempotent repeats.

**Classes and behavior**:

- `LlmNature` and `LlmNatureDetector`: closed nature and evidence result.
- `RoleNatureSnapshot`: strict requestor/reviewer map with legacy parser.
- `RoleNatureReconciler` and `RoleNatureBackfill`: selected-occurrence scan,
  conflict result, atomic mutable upgrades, and transcript completion.

**Completion criteria**:

- `ghog single tests/unit/tools/test_llm_nature tests/unit/tools/test_review_role_nature tests/unit/tools/test_review_exchange_models tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_transcript_identity_tdd.py`
  passes.
- `rg -n "default.*claude|CLAUDECODE|CODEX_THREAD_ID|role_natures" tools instructions`
  shows centralized detection and schema use without a silent Claude fallback.
- `ghog day` reports `exit=0`.

#### Step 2 addendums for role identity

Line-budget checkpoint:

- New detector and role modules: before 0; below-550 safe; ceiling 650; expected
  at or below 180 and 420 lines respectively (advisory).
- Envelope model: before 220; below-550 safe; ceiling 650; expected at or below
  300 lines (advisory).
- Coordination model: before 238; below-550 safe; ceiling 650; expected at or
  below 330 lines (advisory).
- Publication: before 358; below-550 safe; ceiling 650; expected at or below 430
  lines (advisory).
- Transcript identity: before 46; below-550 safe; ceiling 650; expected at or
  below 110 lines (advisory).
- Prompt renderer: before 88; below-550 safe; ceiling 650; expected at or below
  120 lines (advisory).
- New tests: before 0; each below-550 safe; ceiling 650; expected at or below 450
  lines (advisory).
- Existing model test: before 470; below-550 safe; ceiling 650; expected at or
  below 540 lines (advisory); put new validation cases in its existing 359-line
  sibling before crossing the risk band.

Split guidance:

- Keep backfill transaction IO separate from pure reconciliation.
- Add a new schema-v2 test leaf rather than growing any existing test beyond
  650 lines.

Full workflow timing run readiness:

- Step 2 focused tests listed above; `ghog day`.

Time-gated status for Step 2:

- No Step 0 time gate changes; identity work is bounded by artifact count.

---

### Step 3. Fence every acting session with ownership capabilities

#### Step 3 analysis and intent for safe transition ownership

Issues to address:

- Fresh-lease pickup can displace a live session without a mechanical fence.
- Ordinary and resumed actors need one claim contract, and plaintext tokens must
  never be recoverable from coordination.
- CLI and store files are already in the risk band.

Fix intent:

- Add focused ownership, ownership-store, and CLI support modules.
- Claim on start, reclaim, actor wake, and selected global request; require the
  generation and secret on every mutation and store only the digest.
- Keep all new branches outside risk-band files except narrow delegation.

Expected outcome:

- Stale, missing, or invalid capabilities fail before mutation.
- Direct resume advances ownership while ordinary workflows still claim and
  complete normally.

Step framing:

- Design link: Lease-independent pickup and displaced sessions, Q05.
- Execution checklist reference: Shared execution command checklist for all
  v0.11.0 review-resume steps.

#### Step 3 implementation for ownership fencing

**Files involved**:

- `tools/review_exchange_ownership.py` (new, to be created).
- `tools/review_exchange_ownership_store.py` (new, to be created).
- `tools/review_exchange_cli_ownership.py` (new, to be created).
- `tools/review_exchange_models_coordination.py` (existing, to be updated).
- `tools/review_exchange_state.py` (existing, to be updated).
- `tools/review_exchange_core.py` (existing, to be updated).
- `tools/review_exchange_store.py` (existing, to be reduced to delegation).
- `tools/review_exchange_wait.py` (existing, to be updated).
- `tools/review_exchange_cli_parser.py` (existing, to be updated).
- `tools/review_exchange_cli.py` (existing, to be reduced to delegation).
- `tests/unit/tools/test_review_exchange_ownership/__init__.py` (new, to be
  created).
- `tests/unit/tools/test_review_exchange_ownership/test_review_exchange_ownership_tdd.py`
  (new, to be created).
- `tests/unit/tools/test_review_exchange_ownership/test_review_exchange_ownership_pbt.py`
  (new, to be created).
- `tests/unit/tools/test_review_exchange_ownership/test_review_exchange_ownership_cli_tdd.py`
  (new, to be created).
- `tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_lifecycle_recovery_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_review_exchange_cli/test_review_exchange_cli_boundaries_tdd.py`
  (existing, to be updated).

**Tests first**:

- Cover ordinary claim and mutation, actor handoff, digest-only coordination,
  wrong secret, stale generation, missing capability, duplicate claim,
  lease-independent pickup, lost secret pickup, convergence-gate pickup, and
  typed `ownership-superseded`.
- Cover generation and token flags as one required pair, including omitted,
  empty, malformed, duplicated, and mismatched values plus secret redaction from
  diagnostics and transcript output.
- Pass both values only as CLI flags for the current mutating call. Do not place
  the token in an environment variable or session capability file; this follows
  the displaced-session threat model recorded in Q01.
- Property-test strict generation increase and rejection of every earlier
  generation.
- Cover crash boundaries before and after capability persistence and require the
  transition lock for every compare-and-swap.
- Prove human rendering and transcripts never contain the secret.

**Classes and behavior**:

- `OwnershipCapability`, `OwnershipClaim`, and `OwnershipFailure` typed records.
- `OwnershipService`: token generation, digest comparison, ordinary claim,
  forced pickup, validation, and handoff invalidation.
- Ownership CLI support parses capability inputs and removes those branches from
  `review_exchange_cli.py`.
- Every mutating operation accepts the paired ownership generation and token
  flags, validates them before mutation, and redacts the token from all output.

**Completion criteria**:

- `ghog single tests/unit/tools/test_review_exchange_ownership tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_lifecycle_recovery_tdd.py tests/unit/tools/test_review_exchange_cli/test_review_exchange_cli_boundaries_tdd.py`
  passes.
- `rg -n "ownership[-_](generation|token|digest)|ownership-superseded" tools tests/unit/tools/test_review_exchange_ownership`
  shows digest storage and typed fencing at every mutation seam.
- `ghog day` reports `exit=0`.

#### Step 3 addendums for ownership fencing

Line-budget checkpoint:

- New ownership modules: before 0; below-550 safe; ceiling 650; service target
  360, store target 260, CLI support target 220 lines (advisory).
- Coordination model: before the recorded Step 2 final count; use Step 2's
  below-550 or risk-band classification; ceiling 650; expected at or below 380
  lines after Step 3 (advisory).
- State: before 277; below-550 safe; ceiling 650; expected at or below 340 lines
  (advisory).
- Core: before the recorded Step 1 final count; use Step 1's recorded policy
  band; ceiling 650; expected at or below 540 lines (advisory).
- Store: before the recorded Step 1 final count; use Step 1's recorded risk band;
  mandatory target at or below 600 because ownership storage is explicitly
  extracted.
- Wait: before 209; below-550 safe; ceiling 650; expected at or below 290 lines
  (advisory).
- CLI parser: before 132; below-550 safe; ceiling 650; expected at or below 190
  lines (advisory).
- CLI: before 558; risk band; mandatory target at or below 540 because ownership
  dispatch is explicitly extracted.
- New ownership tests: before 0; each below-550 safe; ceiling 650; expected at or
  below 480 lines (advisory).
- Lifecycle recovery test: before 498; below-550 safe; ceiling 650; expected at
  or below 560 lines (advisory).

Split guidance:

- The store and CLI extraction targets are mandatory goals of this step; do not
  leave either risk-band file larger after adding ownership.
- Keep token cryptography and compare-and-swap storage in separate modules so
  neither new module approaches 550 lines.

Full workflow timing run readiness:

- Step 3 focused tests listed above; `ghog day`.

Time-gated status for Step 3:

- Add bounded concurrent-claim tests; no wall-clock wait longer than the focused
  test timeout.

---

### Step 4. Project migration and role nature through status schema 2

#### Step 4 analysis and intent for migration-aware diagnosis

Issues to address:

- Status schema 1 has no migration record or LLM nature and discovers only
  root-level coordination.
- `rvw_status` is documented as strictly read-only although safe migration is
  now its required bounded exception.
- The 509-line projection service should not absorb migration orchestration.

Fix intent:

- Add focused status migration and role-nature projection helpers.
- Advance machine output to schema 2 and update human rendering, exit mapping,
  canonical instruction, adapters, and acceptance fixtures.

Expected outcome:

- Status reports unnecessary or completed migration and both role natures.
- Blocked migration returns operational failure before ordinary projection;
  ready projection remains read-only.

Step framing:

- Design link: Status model and migration-aware reporting.
- Execution checklist reference: Shared execution command checklist for all
  v0.11.0 review-resume steps.

#### Step 4 implementation for schema-2 status

**Files involved**:

- `tools/review_status_migration.py` (new, to be created).
- `tools/review_status_role_nature.py` (new, to be created).
- `tools/review_status_models.py` (existing, to be updated).
- `tools/review_status.py` (existing, to be updated by delegation).
- `tools/review_status_render.py` (existing, to be updated).
- `tools/review_status_cli.py` (existing, to be updated).
- `rvw_status.bat` (existing, to be verified and updated only if arguments
  change).
- `instructions/review-status-command.md` (existing, to be updated).
- `.agent/workflows/review-status-command.md` (existing, to be updated).
- `.agents/llm-shared/skills/review-status-command/SKILL.md` (existing, to be
  updated).
- `.claude/skills/review-status-command/SKILL.md` (existing, to be updated).
- `.github/skills/review-status-command/SKILL.md` (existing, to be updated).
- `tests/unit/tools/test_review_status_migration/__init__.py` (new, to be
  created).
- `tests/unit/tools/test_review_status_migration/test_review_status_migration_tdd.py`
  (new, to be created).
- `tests/unit/tools/test_review_status_models/test_review_status_models_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_review_status_projection/test_review_status_projection_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_review_status_render/test_review_status_render_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_review_status_cli/test_review_status_cli_tdd.py`
  (existing, to be updated).
- `tests/acceptance/review_status/test_review_status_acceptance/test_review_status_acceptance_tdd.py`
  (existing, to be updated).

**Tests first**:

- Cover schema 2 serialization, unnecessary/completed migration, moved count,
  relative home, requestor/reviewer nature, unrecorded, conflicting evidence,
  and evidence paths.
- Cover check, migrate, ready recheck ordering and no projection on blocked or
  failed migration.
- Update human and JSON snapshots plus status codes for normal, completed, and
  operational-failure cases.
- Prove status bytes are unchanged after the bounded preflight and repeated
  calls do not migrate twice.

**Classes and behavior**:

- `MigrationStatus`, schema-2 repository result fields, and role-nature status
  fields.
- `ReviewStatusMigrationPreflight`: shared check/migrate/recheck adapter.
- `ReviewStatusRoleNatureProjection`: reconcile snapshots into enum,
  `unrecorded`, or `conflicting` plus evidence.

**Completion criteria**:

- `ghog single tests/unit/tools/test_review_status_migration tests/unit/tools/test_review_status_models tests/unit/tools/test_review_status_projection tests/unit/tools/test_review_status_render tests/unit/tools/test_review_status_cli tests/acceptance/review_status/test_review_status_acceptance/test_review_status_acceptance_tdd.py`
  passes.
- `rg -n "schema_version.*2|migration|requestor_llm_nature|reviewer_llm_nature|strictly read-only" tools/review_status* instructions/review-status-command.md`
  shows schema-2 fields and no obsolete absolute read-only claim.
- `ghog day` reports `exit=0`.

#### Step 4 addendums for schema-2 status

Line-budget checkpoint:

- New status helpers: before 0; below-550 safe; ceiling 650; expected at or below
  240 lines each (advisory).
- Status models: before 408; below-550 safe; ceiling 650; expected at or below
  520 lines (advisory).
- Status service: before 509; below-550 safe; ceiling 650; expected at or below
  540 lines because helpers own all new projection and migration logic.
- Status render and CLI: before 119 and 103; below-550 safe; ceiling 650;
  expected at or below 180 and 150 lines (advisory).
- Status instruction and adapters: before 38 and 6-7 lines; non-Python; expected
  instruction at or below 90 and adapters at or below 10 lines (advisory).
- New migration test: before 0; below-550 safe; ceiling 650; expected at or below
  420 lines (advisory).
- Existing status tests: before 455, 155, 230, 330, and 291 lines; below-550 safe;
  ceiling 650; put schema-2 overflow in the new migration leaf before any file
  crosses 650.

Split guidance:

- Keep `review_status.py` below 550 if practical by delegating both new concerns.
- Split schema serialization tests before growing the 455-line models test into
  the risk band.

Full workflow timing run readiness:

- Step 4 focused tests listed above; `ghog day`.

Time-gated status for Step 4:

- Reuse the active migration-check bounds; status may add only one ordinary
  projection after a ready preflight.

---

### Step 5. Add LLM-only resume and persistent reviewer waiting

#### Step 5 analysis and intent for role-specific continuation

Issues to address:

- There is no public resume skill, role resolver, identity-free request wait, or
  several-reviewer race handling.
- Existing reviewer instructions stop at convergence and exact replacement
  waits, while the settled behavior is persistent across exchanges.
- Requestor resume must stay bound to its task and follow `pw skill` only after
  exchange release.
- A new process can be misrouted to `reclaim` or lease waiting when its durable
  exchange is still live but its prior plaintext capability is unavailable.

Fix intent:

- Add focused resume services and CLI support operations without adding a
  public resume launcher.
- Add one canonical resume instruction and thin adapters.
- Update all role instructions to carry nature, capability, global reviewer
  waiting, and exact requestor continuation.
- Make global reviewer waiting one quiet foreground script operation; do not
  stream idle progress into an LLM session or add an LLM polling loop.
- Treat a graceful host or console interruption as `cancelled`, with one typed
  terminal result and fixed exit mapping; do not create durable waiter state.
- Treat the bare user request `resume` as authorization for automatic
  lease-independent pickup after role resolution and before role dispatch. Do
  not require the user to mention a new session, pickup, generation, token,
  reclaim, force, or lease expiry.
- Remove Step 0 global-wait xfails.

Expected outcome:

- A bare `resume` detects or asks for role once, applies migration and identity
  gates, automatically picks up ownership, then acts or waits without an
  ownership-recovery explanation or another confirmation. Only a genuine role
  or request ambiguity, identity conflict, cancellation, or existing human
  convergence decision may still require human input.
- Reviewers answer one request or wait for any future request; requestors never
  consume arbitrary requests.

Step framing:

- Design link: Resume skill orchestration through requestor continuation, Q06
  and Q07.
- Execution checklist reference: Shared execution command checklist for all
  v0.11.0 review-resume steps.

#### Step 5 implementation for resume workflows

**Files involved**:

- `tools/review_resume.py` (new, to be created).
- `tools/review_resume_wait.py` (new, to be created).
- `tools/review_exchange_cli_resume.py` (new, to be created).
- `tools/review_exchange_cli_parser.py` (existing, to be updated).
- `tools/review_exchange_cli.py` (existing, to be reduced to delegation).
- `tools/review_exchange_wait.py` (existing, to be updated).
- `tools/prompt_workflow_skill_review.py` (existing, to be updated).
- `pyproject.toml` (existing, to be updated).
- `uv.lock` (existing, to be updated).
- `instructions/review-resume.md` (new, to be created).
- `.agent/workflows/review-resume.md` (new, to be created).
- `.agents/llm-shared/skills/review-resume/SKILL.md` (new, to be created).
- `.claude/skills/review-resume/SKILL.md` (new, to be created).
- `.github/skills/review-resume/SKILL.md` (new, to be created).
- `instructions/review-requestor.md` (existing, to be updated).
- `instructions/spec-review-requestor.md` (existing, to be updated).
- `instructions/code-review-requestor.md` (existing, to be updated).
- `instructions/spec-reviewer.md` (existing, to be updated).
- `instructions/code-reviewer.md` (existing, to be updated).
- `tests/unit/tools/test_review_resume/__init__.py` (new, to be created).
- `tests/unit/tools/test_review_resume/test_review_resume_tdd.py` (new, to be
  created).
- `tests/unit/tools/test_review_resume/test_review_resume_wait_tdd.py` (new, to
  be created).
- `tests/unit/tools/test_review_resume/test_review_resume_role_tdd.py` (new, to
  be created).
- `tests/unit/tools/test_review_resume_instruction/__init__.py` (new, to be
  created).
- `tests/unit/tools/test_review_resume_instruction/test_review_resume_instruction_tdd.py`
  (new, to be created).
- `tests/unit/tools/test_instruction_structure/test_spec_reviewer_adapters_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_instruction_structure/test_code_reviewer_adapters_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_review_requestor_instruction/test_review_requestor_instruction_tdd.py`
  (existing, to be updated).

**Tests first**:

- Cover inferred requestor, inferred reviewer, legacy no-nature prompt, explicit
  role, forced mismatch confirmation, two matching roles, unknown host, selected
  role conflict, counterpart omission, migration-first ordering, and no second
  confirmation.
- Cover the exact argument-free user request `resume` for an active reviewer
  request, requestor answer, convergence gate, and authorized owning action.
  Assert each path runs `resume-inspect` and automatic `claim` before its first
  role-owned mutation without asking for ownership terminology.
- Cover missing and stale session capabilities while the lease remains fresh.
  Assert resume performs lease-independent pickup, never `reclaim --force`, and
  never waits for lease expiry; an abandoned request may use ordinary `reclaim`
  only after the automatic pickup returns the fresh capability.
- Cover reviewer wait before any exchange, after conclusion, after intermediate
  answer, at convergence, and during requestor ownership; same and new exchange
  wakes; unrelated artifact ignore; human cancellation.
- Cover native notification through a narrow `watchdog` adapter, bounded polling
  fallback, event coalescing, and an authoritative rescan after every hint.
- Cover non-mutating candidate discovery separately from the foreground claim,
  plus a quiet `wait-any-request` with no idle standard-output or standard-error
  progress and one final machine result. Inject graceful host and console
  cancellation through a test seam; assert one `cancelled` result, no claim or
  ownership capability, and no persisted waiter artifact. Assert the result
  fields and exit mapping for `found`, `ambiguous`, `cancelled`, invalid input,
  and operational failure.
- Cover several requests for one reviewer and one request for several reviewers,
  including first claim, typed loser, and return to wait.
- Cover requestor exact-answer wait, owned action, convergence pickup, lost
  secret pickup, exchange release, and immediate `pw skill` continuation.
- Assert the resume instruction and every provider adapter accept bare `resume`
  and never ask the user to supply an ownership generation, token, pickup
  directive, new-session declaration, or reclaim choice.
- Assert there is no `rvw_resume.bat` and every provider adapter remains a thin
  direct pointer with a schema-validated, non-secret `llm_nature` metadata field.
- Cover the typed `migration-check`, `migrate-artifacts`, `resume-inspect`,
  `claim`, and `wait-any-request` operations exposed by `review_exchange.bat`.
- Remove Step 0 wait xfails without changing timeout bounds.

**Classes and behavior**:

- `ResumeContext`, `ResumeRoleResolution`, and `ReviewResumeService` implement
  preflight, role selection, evidence gate, ownership claim, and typed next
  action.
- `ReviewResumeService` invokes the internal `claim` operation automatically
  for every selected concrete live exchange. In direct-resume mode, `claim`
  delegates to lease-independent pickup when the current process has no valid
  capability, advances the generation, retains the returned secret only in the
  running session, and supplies the pair to later fenced operations.
- The canonical resume skill and thin provider adapters recognize the bare
  prompt `resume`; ownership recovery is internal orchestration, not a user
  prompt or public launcher argument.
- `GlobalReviewRequestDiscovery` uses notification hints, bounded polling, and
  authoritative rescans without claiming. `GlobalReviewerWait` selects one
  candidate, performs the normal first-claim-wins operation, and remains quiet
  until its one final machine result. `wait-any-request` catches graceful host
  and console interruption as `cancelled` and emits `operation`, `outcome`,
  `identity`, `candidates`, and `diagnostic`; only `found` includes the
  session-only ownership capability. It exits 0 for `found`, 3 for `ambiguous`
  or `cancelled`, and 2 for invalid input or operational failure.
- A narrow notification adapter uses the direct `watchdog` runtime dependency
  when available and retains bounded polling as the correctness fallback.
- Resume support operations are exposed through `review_exchange.bat` as
  `migration-check`, `migrate-artifacts`, `resume-inspect`, `claim`, and
  `wait-any-request`; the LLM instruction remains the only public resume entry
  point.
- Provider adapters carry validated `llm_nature` metadata and keep their bodies
  as canonical direct pointers.

**Completion criteria**:

- `ghog single tests/unit/tools/test_review_resume_perf/test_review_resume_perf_tdd.py tests/unit/tools/test_review_resume tests/unit/tools/test_review_resume_instruction tests/unit/tools/test_instruction_structure/test_spec_reviewer_adapters_tdd.py tests/unit/tools/test_instruction_structure/test_code_reviewer_adapters_tdd.py tests/unit/tools/test_review_requestor_instruction`
  passes.
- `rg -n "rvw_resume|bare.*resume|automatic.*(claim|pickup)|wait globally|pw skill|already-claimed|review-resume" bin tools instructions .agent .agents .claude .github`
  shows no public resume launcher and the settled role split.
- `ghog day` reports `exit=0`.

#### Step 5 addendums for resume workflows

Line-budget checkpoint:

- New resume modules: before 0; below-550 safe; ceiling 650; service target 430,
  wait target 360, CLI support target 220 lines (advisory).
- CLI parser: before the recorded Step 3 final count; use Step 3's recorded
  policy band; ceiling 650; expected at or below 230 lines after Step 5
  (advisory).
- CLI: before the recorded Step 3 final count; use Step 3's recorded policy
  band; mandatory target at or below 520 because resume dispatch joins the Step
  3 extraction.
- Wait module: before the recorded Step 3 final count; use Step 3's recorded
  policy band; ceiling 650; expected at or below 360 lines (advisory).
- Prompt review routing: before 208; below-550 safe; ceiling 650; expected at or
  below 250 lines (advisory).
- `pyproject.toml` and `uv.lock`: existing non-Python dependency declarations;
  no Python line ceiling; add `watchdog` as a direct runtime dependency.
- Canonical instructions: before 235, 166, 183, 233, and 238 lines; non-Python;
  keep role rules centralized and adapters at 10 lines or fewer (advisory).
- New resume tests: before 0; each below-550 safe; ceiling 650; expected at or
  below 500 lines (advisory).
- Existing instruction tests: before 66-143 lines; below-550 safe; ceiling 650;
  expected below 220 lines each (advisory).

Split guidance:

- Keep observation mechanics separate from role and workflow decisions.
- Do not copy continuation rules into adapters or `prompt_workflow_skill_review.py`.
- Complete the CLI extraction if the main CLI remains above 550 after Step 3.

Full workflow timing run readiness:

- Step 5 focused tests listed above; `ghog day`.

Time-gated status for Step 5:

- Notification and polling gates are active and no longer xfailed; concurrency
  tests use bounded synthetic waits.

---

### Step 6. Prove cross-workflow acceptance and documentation rollout

#### Step 6 analysis and intent for complete feature acceptance

Issues to address:

- Unit seams cannot prove migration, strict schemas, ownership, status,
  adapters, separate LLM sessions, and workflow continuation together.
- Completed review-mode topics have broad tests that still encode root paths,
  no nature, old status schema, exact-only waits, and convergence stops.
- Public documentation must describe the artifact home and role-specific resume
  behavior without reopening completed topic documents.

Fix intent:

- Add real temporary-repository acceptance coverage and update affected shipped
  suites together.
- Exercise launchers and canonical instructions across specification and code
  exchanges, legacy and new evidence, three LLM natures, status migration,
  displacement, reviewer races, and requestor `pw skill` release.
- Update current public documentation and keep earlier completed effort records
  unchanged.

Expected outcome:

- Every feature-request acceptance criterion has a named executable scenario.
- All earlier review workflows pass with configured-home, nature, and ownership
  behavior.

Step framing:

- Design link: Acceptance cases for v0.11.0 review resumption.
- Execution checklist reference: Shared execution command checklist for all
  v0.11.0 review-resume steps.

#### Step 6 implementation for acceptance and rollout

**Files involved**:

- `tests/acceptance/review_resume/__init__.py` (new, to be created).
- `tests/acceptance/review_resume/conftest.py` (new, to be created).
- `tests/acceptance/review_resume/test_review_resume_acceptance/__init__.py`
  (new, to be created).
- `tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_acceptance_tdd.py`
  (new, to be created).
- `tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_concurrency_tdd.py`
  (new, to be created).
- `tests/unit/tools/review_exchange_test_support.py` (new, to be created).
- `tests/unit/tools/test_review_exchange_acceptance/test_review_exchange_acceptance_tdd.py`
  (existing, to be updated only for shared fixtures and schema expectations).
- `tests/unit/tools/test_spec_review_requestor_acceptance/test_spec_review_requestor_acceptance_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_spec_reviewer_acceptance/test_spec_reviewer_acceptance_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_acceptance_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_prompt_workflow_skill/test_prompt_workflow_skill_spec_reviewer_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_prompt_workflow_skill/test_prompt_workflow_skill_code_reviewer_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_review_mode_docs_acceptance/test_review_mode_docs_final_acceptance_tdd.py`
  (existing, to be updated).
- `README.md` (existing, to be updated).

**Tests first**:

- Build real Git repositories for default, configured, legacy root, former
  default, collision, damaged journal, uncovered home, and repeated migration.
- Run status, specification requestor/reviewer, code requestor/reviewer, and
  resume flows through public launchers and separate simulated LLM sessions.
- Cover Claude, Codex, Gemini, unknown, legacy completion, conflict Override and
  Stop, counterpart omission, fresh-lease displacement, lost capability,
  convergence pickup, same/new exchange reviewer wake, simultaneous requests,
  competing reviewers, and requestor workflow release.
- Start the fresh-lease reviewer, convergence-gate requestor, and lost-capability
  scenarios with only the user text `resume`; assert automatic pickup precedes
  continuation and no ownership-recovery question is emitted.
- Compare artifact bytes, transcript headings, Git ignore evidence, ownership
  generations, secret absence, schema-2 JSON, human reports, process statuses,
  and clean Git state.
- Map each feature acceptance criterion to at least one test name.

**Classes and behavior**:

- Acceptance fixtures create configured repositories, session host evidence,
  protocol artifacts, concurrent waiters, and deterministic notifications.
- `review_exchange_test_support.py` provides canonical configured-home,
  role-nature, ownership, and schema builders; scenario-specific fixtures remain
  local to their test package.
- README documents `.review-artifacts.ini`, migration-aware `rvw_status`, bare
  `resume`, automatic pickup, role detection, reviewer waiting, and requestor
  continuation.

**Completion criteria**:

- `ghog single tests/acceptance/review_resume tests/acceptance/review_status tests/unit/tools/test_spec_review_requestor_acceptance tests/unit/tools/test_spec_reviewer_acceptance tests/unit/tools/test_code_review_requestor_acceptance tests/unit/tools/test_code_reviewer_acceptance tests/unit/tools/test_prompt_workflow_skill tests/unit/tools/test_review_mode_docs_acceptance`
  passes.
- `rg -n "\.reviews|\.review-artifacts\.ini|review-resume|requestor_llm_nature|reviewer_llm_nature|already-claimed" README.md instructions tools tests`
  shows public documentation and acceptance evidence.
- `rg --files | rg "rvw_resume\.bat$"` returns no path.
- `ghog day` reports `exit=0`.

#### Step 6 addendums for acceptance and rollout

Line-budget checkpoint:

- New acceptance package and init files: before 0; below-550 safe; ceiling 650;
  each init target 5 lines, conftest target 420 lines, scenario files target 500
  lines each (advisory).
- Shared review-exchange test support: before 0; below-550 safe; ceiling 650;
  expected at or below 450 lines (advisory).
- Existing review-exchange acceptance test: before 604; risk band; ceiling 650;
  no growth beyond fixture/schema edits; put every new scenario in the new
  acceptance package.
- Existing status acceptance test: before the recorded Step 4 final count; use
  Step 4's recorded policy band; ceiling 650; expected at or below 380 lines
  after Step 6 (advisory).
- Existing role acceptance and prompt tests: count before edits; below-550 files
  may grow to the 650 ceiling, while any risk-band file receives only fixture or
  expectation replacements and no new scenario block.
- README: before 1068; non-Python; no Python ceiling; keep additions focused and
  link canonical instructions rather than copying them.

Split guidance:

- Keep repository/session builders in `conftest.py`, sequential scenarios in the
  main acceptance file, and race/timing scenarios in the concurrency file.
- Split any existing test already in the risk band before adding a new behavior
  section to it.

Full workflow timing run readiness:

- Step 6 focused acceptance and regression suites listed above; `ghog day`.

Time-gated status for Step 6:

- Run notification, polling, migration, and competing-reviewer gates under the
  final public launcher fixtures with their Step 0 bounds unchanged.
