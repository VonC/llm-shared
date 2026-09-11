# v0.11.0 review-exchange-core implementation tracking and validation

Yes, it is implemented.

This validation records all five review-exchange-core implementation steps as complete, including integrated acceptance and rollout verification.

---

## File-based IO cost clarification for v0.11.0 review-exchange-core implementation

All implementation checks must verify the IO contract from `docs/v0.11.0/plan.v0.11.0.review-exchange-core.md`:

- Operations receive one exact reviewed-document path and derive a constant path set once.
- Status and waiting read only the expected transient and coordination paths.
- Waiting never scans, rereads the transcript, or renews a lease.
- Before append, idempotent transcript repair persists the pre-append byte offset and stable entry identifier; repair reads only from that offset, truncates a torn suffix when needed, and never loads transcript history.
- Recovery touches only the fixed artifacts for the selected identity.

---

## Complexity bound clarification for v0.11.0 implementation

- **O(1) per state operation and wait poll** over a constant exact path set.
- **O(k) serialization** only in the content currently read or written.
- **O(r) recovery** over the fixed artifacts for one identity.

Every step's performance check must reject project-tree scans, transcript-history reads, and quadratic round processing.

---

## Step 1. Typed identity, configuration, envelopes, and derived paths

### Analysis of Step 1 implementation state

Yes. Step 1 has been fully implemented.

The repository now contains the validated protocol model, coordination, envelope, configuration, path derivation, and Git-ignore activation primitives required by Step 1, with focused unit and property tests and a green global gate.

### Goal for Step 1

Create validated exchange identity, context, configuration, envelope, coordination-record, and exact derived-path primitives, including effective Git-ignore gating.

### Step 1 improvement expectations

- Every artifact and summary shares one complete, validated identity.
- Invalid configuration or identity fails before writes.
- Specification and intentional `code.code` paths are distinct and stable.
- Property tests cover identity/path round trips and collision resistance.

### What was implemented for Step 1

- **Typed identity and policy**: added immutable exchange identity, review context, family policy, actor, status, disposition, outcome, transition, archive, and artifact-state models with strict serialization and validation.
- **Configuration and timestamps**: added opt-in `a.review-mode` loading, the 1,800-second default, positive override validation, and local ISO-8601 timestamps with numeric offsets.
- **Coordination and envelopes**: split durable coordination state and fenced-JSON envelopes into focused modules, including impossible-state rejection and machine-to-human summary identity validation.
- **Derived paths and activation**: added constant exact path derivation, round-trip parsing, archive naming, intentional `code.code` support, repository validation, and one effective `git check-ignore` call covering every transient path.
- **Package surface**: exported the public protocol types from `tools/__init__.py` without exposing path-adapter internals.
- **Validation evidence**: focused model and path tests pass, the tree-scan grep finds no `rglob`, `glob`, or `iterdir` use in the four production modules, and `ghog day` completed with 1,300 passing tests, 100% coverage, zero outliers, zero exclusions, and `exit=0`.

### Step 1 implementation-to-plan variances

The protocol model was split preemptively into `tools/review_exchange_models.py`, `tools/review_exchange_models_coordination.py`, and `tools/review_exchange_models_envelope.py`. The latter two production modules make the line-budget split explicit rather than waiting for the combined model to approach the ceiling.

`tests/unit/tools/test_review_exchange_models/test_review_exchange_models_validation_tdd.py` was added as a separate validation-focused leaf so invalid field shapes and coordination invariants do not overload the primary model test module.

`tools/__init__.py` gained 36 export lines for the stable public protocol classes. This follows the repository's public-class export convention; the plan's earlier statement that the package needed no export growth was incorrect.

### Repository-wide supporting changes included with Step 1

- `.vscode/settings.json`: added spell-checker vocabulary used by the protocol and review documentation.
- `tools/open_questions_md.py` and `tests/unit/tools/test_open_questions_md.py`: kept open-question document lookup compatible with the versioned documentation layout and added the matching rejection coverage.
- `tests/unit/tools/test_prompt_workflow_docs/__init__.py` and `tests/unit/tools/test_prompt_workflow_docs/test_prompt_workflow_docs_document_lookup_tdd.py`: split document-lookup coverage into a focused test leaf.
- `tests/unit/tools/test_prompt_workflow_main.py`: preserved prompt-workflow missing-document coverage after the document-test split.
- `tests/unit/tools/test_instruction_structure/__init__.py`, `tests/unit/tools/test_instruction_structure/test_instruction_structure_tdd.py`, and `tests/unit/tools/test_instruction_structure/test_instruction_structure_prompt_workflow_tdd.py`: split instruction-structure coverage without changing its assertions.
- `tests/unit/tools/test_instruction_structure/test_codex_plugin_structure_tdd.py` and `tests/unit/tools/test_prompt_workflow_integration.py`: moved repeated repository setup out of measured calls while retaining the structural and integration assertions.
- `tests/unit/tools/sensitive_history/test_sensitive_commit_check.py` and `tests/unit/tools/sensitive_history/test_install_hooks.py`: moved repeated real-Git setup into fixtures while retaining the original checks.
- `tests/unit/tools/prepare_release/test_prepare_release_plan_workflow.py` and `tests/unit/tools/prepare_release/test_prepare_release_plan_git.py`: reused fixture-level repositories for the same release-plan and Git assertions.

### New types or classes introduced for Step 1

- `ReviewExchangeError`: stable fail-closed validation error.
- `ReviewFamily`, `ReviewRole`, `CoordinationStatus`, `ReviewDisposition`, `ConfirmationOutcome`, `Actor`, `IncompleteTransitionKind`, `ArtifactState`, and `ArchiveKind`: closed protocol vocabularies.
- `ExchangeIdentity` and `ReviewContext`: canonical exchange identity and review-summary context.
- `FamilyPolicy`: immutable family convergence signal and confirmation-label mapping.
- `ReviewConfiguration`: marker-backed activation and bounded-wait configuration.
- `ArtifactPaths`: constant transcript and transient path set.
- `CoordinationRecord`: durable recovery, progress, escalation, and confirmation state.
- `Envelope`: machine-readable review artifact metadata.

### Architecture check for Step 1

- **Protocol model boundary**: `review_exchange_models.py` contains value types and standard-library validation only; it does not depend on persistence or workflow orchestration.
- **Focused model splits**: coordination and envelope modules depend on the protocol foundation, while the foundation does not import them, keeping dependency direction acyclic.
- **Adapter boundary**: `review_exchange_paths.py` owns filesystem naming and the injected Git command boundary; protocol types remain independent of Git subprocess details.
- **Package surface**: `tools/__init__.py` re-exports stable public models without moving adapter behavior into the package root.
- **Maintainability**: all new production modules stay below the plan's 550-line safe target after the coordination and envelope splits.

No, there is nothing that needs to be addressed for Step 1.

### Performance check for Step 1

- **No new `O(n^2)` or `O(n log n)` path**: identity checks, state validation, and path derivation operate over fixed fields and a constant path tuple.
- **Hot-path bound**: deriving or parsing one exchange path is `O(1)` in the number of artifacts and `O(k)` only in the bounded identity text being processed.
- **Activation bound**: Git repository validation and ignore coverage use bounded commands, with all transient paths supplied to one `git check-ignore` call.
- **Plan-bound alignment**: the required grep confirms the production path contains no project-tree scan.

No, there is no performance issue that needs to be addressed for Step 1.

### Unit test coverage check for Step 1

- **Protocol models**: test-driven and validation-focused suites cover valid round trips, every invalid field shape, impossible coordination states, configuration failures, timestamp constraints, and summary mismatches.
- **Identity properties**: Hypothesis tests cover exact JSON round trips and collision resistance across distinct identities.
- **Path adapter**: unit tests cover both families, intentional `code.code` names, archive kinds, parse-back behavior, non-Git failure, ignore gaps, bounded subprocess arguments, and Git diagnostic failures.
- **Coverage evidence**: focused affected coverage and the final full suite both report 100% coverage.

No, there is no unit-tested class below 100% that needs completing for Step 1.

### Feature integrity for Step 1

- **Existing workflow behavior**: focused regression tests preserve open-question document lookup and prompt-workflow missing-document handling after the small supporting refactor needed by the global gate.
- **Reporting and diagnostics**: invalid protocol input and Git activation failures produce stable diagnostics before any write.
- **Test-suite reliability**: slow structural and real-Git assertions were redesigned to keep the measured call phase deterministic while retaining repository setup and every assertion.
- **Compatibility**: review exchange behavior remains opt-in through `a.review-mode`; existing workflows are unchanged when the marker is absent.

No, no existing feature or reporting capability appears impaired by Step 1.

---

## Step 2. Atomic artifact store, transcript, tombstone, and archive primitives

### Analysis of Step 2 implementation state

Yes. Step 2 has been fully implemented.

The repository now contains exact-path persistence, short operating-system locks, atomic request and answer publication, consumed-request tombstones, append-only transcript initialization and repair, evidence archives, role-neutral templates, and complete focused test coverage.

### Goal for Step 2

Implement atomic exact-path storage, short transition locks, idempotent append-only transcripts, consumed-request tombstones, evidence archives, and role-neutral templates.

### Step 2 improvement expectations

- Partial publication and append failures remain recoverable.
- A torn transcript append is truncated to the persisted pre-append offset and regenerated exactly once.
- Request removal precedes answer visibility without destroying evidence.
- Agents append complete entries without reading transcript history.
- Family transcript templates initialize only missing transcripts.

### What was implemented for Step 2

- **Exact artifact store**: added `ReviewExchangeStore` for identity-checked UTF-8 reads, complete same-directory temporary writes, bounded atomic replacement, stale-answer cleanup, exact transient deletion, and coordination-record persistence.
- **Safe request and answer ordering**: request publication removes only a matching stale answer, while answer publication atomically renames the validated request to its identity-specific tombstone before exposing the answer.
- **Short transition locks**: added standard-library Windows and POSIX lock adapters against the exact ignored transition-lock path, with release guaranteed when a transition raises.
- **Transcript persistence**: added family-template initialization, role-and-round-labeled entries, stable entry footers, marker-first pre-append byte offsets, suffix-only verification, torn-suffix truncation, and idempotent complete-append repair.
- **Evidence recovery**: added exact archive moves for request, answer, consumed request, and coordination evidence with compact timestamped names and overwrite refusal.
- **Coordination templates**: added role-neutral request and answer templates plus separate specification and code transcript templates under `templates/`.
- **Focused validation**: added behavioral and failure-path test modules covering atomic replacement, transient sharing denial, identity mismatch, every publication window, torn append recovery, archive conflicts, malformed coordination, exact cleanup, and both lock adapters.
- **Global verification**: Groundhog completed with 1,337 passing tests, 100% coverage, zero warnings, zero xfails, zero outliers, zero exclusions, and `exit=0`.

### Step 2 implementation-to-plan variances

`TranscriptEntry` was introduced as a focused immutable value object so the append API remains below the repository's argument-count limit while carrying the stable entry identifier, role, outcome, timestamp, and authored content together.

The storage tests were split into behavioral and validation-focused modules. This keeps both test files below the line ceiling while preserving a single test package for the store.

Atomic replacement performs at most three immediate attempts with the same prepared file when the operating system reports a transient sharing denial. The bounded retry preserves atomic semantics and fixed complexity while preventing a verified Windows full-suite interaction from stranding coordination repair.

The global duration gate required two existing real-Git prepare-release tests to move unchanged setup and plan construction into fixtures. Their assertion calls now remain below the one-second floor without removing or weakening assertions.

### New types or classes introduced for Step 2

- `TranscriptEntry`: immutable validated current-round transcript content with a stable repair identifier.
- `ReviewExchangeStore`: exact-path persistence adapter for artifacts, coordination, locks, transcripts, tombstones, archives, and recoverable mutation windows.

### Architecture check for Step 2

- **Dependency direction**: the store depends on Step 1 protocol values and path derivation, while those model modules remain independent of persistence and lifecycle orchestration.
- **Adapter responsibility**: filesystem, atomic replacement, operating-system locks, templates, and archive moves remain in the persistence adapter; no lifecycle state classification, waiting, or specialized reviewer behavior leaked into Step 2.
- **Recoverability boundary**: coordination markers and transcript suffix repair are handled together because they form one persistence invariant, while callers retain ownership of transition scope and later lifecycle decisions.
- **File size**: `tools/review_exchange_store.py` is 548 lines, below the plan's 550-line safe target and 650-line ceiling. The two focused store test modules are 449 and 507 lines.

No, there is nothing that needs to be addressed for Step 2.

### Performance check for Step 2

- **No new `O(n^2)` or `O(n log n)` work**: all artifact operations use the fixed path set for one identity, and atomic replacement retries are bounded by a constant of three.
- **Transcript bound**: append repair seeks directly to the persisted byte offset and reads or truncates only the current suffix, making work `O(k)` in the current entry rather than transcript history.
- **Recovery bound**: tombstone cleanup and archive operations touch one selected exact artifact and never discover files through a directory scan.
- **Verification grep**: production storage code contains no `rglob`, `glob`, or `iterdir` call.

No, there is no performance issue that needs to be addressed for Step 2.

### Unit test coverage check for Step 2

- **Store behavior**: tests cover complete UTF-8 replacement, preservation on permanent failure, bounded transient-denial recovery, stale-answer cleanup, request-to-tombstone ordering, and exact cleanup.
- **Transcript behavior**: tests cover both family templates, preservation of existing transcripts, role and round labels, stable footers, marker persistence, torn suffix truncation, complete suffix recognition, and duplicate prevention.
- **Failure validation**: tests cover invalid entry metadata, wrong roles and identities, whole-transcript replacement rejection through generic publication, malformed coordination fences, unreadable and missing artifacts, stale markers, missing offsets, archive collisions, failed archive moves, preparation failures, and Windows and POSIX lock paths.
- **Coverage evidence**: the final full suite reports 100% coverage for `tools/review_exchange_store.py` and the repository.

No, there is no unit-tested class below 100% that needs completing for Step 2.

### Feature integrity for Step 2

- **Opt-in isolation**: no existing writer workflow or prompt routing was changed; the Step 2 store remains an unused reusable core until later lifecycle and adapter steps wire it in.
- **Existing reporting**: Groundhog's complete check, affected, full-suite, coverage, and duration gates are green.
- **Prepare-release regression prevention**: two existing real-Git tests retain every assertion while moving expensive construction to fixtures, and their full test module passes in focus and globally.
- **Unrelated worktree state**: the pre-existing `.agents/llm-shared/.codex-plugin/plugin.json` edit was not changed during implementation or validation.

No, no existing feature or reporting capability appears impaired by Step 2.

---

## Step 3. Lifecycle state machine, bounded waits, repair, escalation, and confirmation

### Analysis of Step 3 implementation state

Yes. Step 3 has been fully implemented.

The repository now provides the complete fail-closed lifecycle classifier, marker-first transition service, monotonic bounded waits, automated round and escalation rules, durable convergence confirmation, and fresh-round human resolution required by the plan.

### Goal for Step 3

Implement every observable state and safe transition, bounded waiting and abandonment, automated round control, escalation, durable convergence confirmation, and idempotent owning-action authorization replay.

### Step 3 improvement expectations

- Every reachable state is classified or fails closed.
- Waiting is bounded and polls never renew a dead actor's lease.
- One in-process monotonic wait exposes periodic progress callbacks without persisted wall-time slices.
- Every transcript-appending transition repairs from its persisted pre-append offset and target entry identity.
- Intermediate rounds stay automated while convergence alone waits for a human.
- Interrupted human-authorized owning work resumes without asking the human twice.

### What was implemented for Step 3

- **Observable state classifier**: added immutable artifact snapshots and decisions covering idle, active, pending, repair, abandoned, convergence, owning-action, escalated, and inconsistent states, with identity and parse errors taking precedence over lease-time evaluation.
- **Lifecycle application service**: added start, request publication, answer publication and repair, answer consumption, round continuation, escalation, and completion transitions over the typed protocol models and exact-path store. A later `reclaim` transition renews an expired lease in place for an abandoned round with active coordination and intact evidence, stays idempotent on live rounds, and rejects escalated, confirming, interrupted, and inconsistent exchanges.
- **Marker-first recovery**: retained incomplete-transition markers through artifact mutation, transcript append, and post-append cleanup so request, answer, escalation, confirmation, and resolution retries remain identity-scoped and idempotent.
- **Bounded waiting**: added one-call monotonic deadlines, exact expected-state matching, periodic in-process progress callbacks, and terminal timeout, abandonment, inconsistency, escalation, and repair-required outcomes without lease renewal. A repair state whose marker is the counterpart's own in-flight publication of the expected artifact is polled through rather than treated as terminal, so an unlocked poll cannot abort a healthy publication.
- **Automated progress rules**: implemented escalation after two unchanged change-request rounds and after one unsuccessful clarification round, while substantive change resets the no-progress streak.
- **Durable human gate**: added role-neutral registered-choice validation, retained convergence evidence, another-round guidance and progress reset, replayable owning-action authorization, cancellation through escalation, and explicit completion after the owning action succeeds.
- **Fresh human resolution**: added clear-or-archive handling over the fixed evidence set, an idempotent human-resolution transcript entry, and a new active round and lease rather than resuming stopped authority.
- **Focused validation**: added table, property, lifecycle, confirmation, recovery, boundary, timeout, and fail-closed tests; the final `ghog day` exercised 1,398 tests and reported 100% coverage, zero outliers, zero exclusions, and `exit=0`.

### Step 3 implementation-to-plan variances

Pure state classification, exact-path observation, bounded waiting, and human transitions were extracted into `tools/review_exchange_state.py`, `tools/review_exchange_observer.py`, `tools/review_exchange_wait.py`, and `tools/review_exchange_human.py`. This keeps `ReviewExchangeCore` focused on application orchestration and every production file below the 650-line ceiling; `tools/review_exchange_core.py` remains within the plan's below-550 safe target at 529 lines.

Lifecycle tests were split into the planned lifecycle and state packages plus focused confirmation and boundary leaves. The split keeps every test file below the 650-line ceiling while making recovery and defensive branches deterministic rather than dependent on randomized property examples.

`ReviewExchangeStore.append_transcript_once` gained a backward-compatible `clear_marker` keyword whose default preserves Step 2 behavior. Step 3 uses `clear_marker=False` so a marker remains durable through lifecycle-owned cleanup and the final coordination write.

The Step 3 code review repaired two gaps found against the staged work. First, the bounded wait returned `repair-required` whenever a poll observed a repair state, so an unlocked poll landing inside the counterpart's healthy in-flight publication aborted the wait; the wait now polls through the counterpart's own publication marker and reserves `repair-required` for foreign markers, with a deterministic regression test using the injected sleeper hook. Second, the design's step-qualified transcript round headings had been applied to the design and the recorded transcript but not to `_render_transcript_entry`; the renderer now appends a space followed by `- Step <identifier>` when the context carries an implementation step, and the store test pins the qualified heading.

### New types or classes introduced for Step 3

- `ReviewExchangeCore`: application facade coordinating exact-path lifecycle transitions, injected clocks, and repair ordering.
- `ArtifactSnapshot` and `StateDecision`: immutable inputs and outputs for pure observable-state classification.
- `ReviewExchangeObserver` and `ExchangeObservation`: read-only adapter that validates one fixed artifact set and evaluates lease currency.
- `WaitOutcome`, `WaitProgress`, and `WaitResult`: stable bounded-wait result and progress values.
- `ReviewExchangeHumanMixin`, `ConfirmationDecision`, and `ResolutionResult`: durable human-gate, owning-authorization, and escalation-resolution behavior.

### Architecture check for Step 3

- **Dependency direction**: the pure state module depends only on protocol values, while the observer and store adapters depend inward on those values; protocol models do not import persistence or application orchestration.
- **Application boundary**: `ReviewExchangeCore` owns transition ordering and coordinates the store, observer, and wait policy without moving filesystem mechanics into the lifecycle service.
- **Human transition cohesion**: confirmation and resolution are separated into an application-layer mixin but remain part of the public core facade; they use role-neutral outcomes and do not grant owning authority to the reviewer.
- **Adapter isolation**: wall time, monotonic time, sleeping, filesystem state, and locking remain injected or delegated, so tests exercise application policy without hidden waits or project-tree discovery.
- **Maintainability**: production files are 529, 324, 139, 275, and 188 lines for core, human, observer, state, and wait respectively, all below the 650-line ceiling and with the core below its 550-line safe target.

No, there is nothing that needs to be addressed for Step 3.

### Performance check for Step 3

- **No new `O(n^2)` or `O(n log n)` path**: state and transition decisions inspect a constant artifact tuple and fixed coordination fields; no operation sorts or scans project content.
- **Wait-loop bound**: each poll reads only the exact request, answer, tombstone, and coordination paths, computes one monotonic deadline comparison, and never rereads the transcript or renews a lease.
- **Recovery bound**: transcript repair delegates to the Step 2 persisted suffix offset, while escalation resolution iterates only the four supported live evidence paths.
- **Verification evidence**: production lifecycle modules contain no `rglob`, `glob`, or `iterdir` call, and the wait module contains no coordination write, lease renewal, wall clock, or persisted deadline.
- **Duration stability**: the generated-shape property's I/O-heavy examples are capped while the previously probabilistic fail-closed branches now have deterministic tests; its measured call phase fell from 5.58 seconds to 0.70 seconds without removing assertions.

No, there is no performance issue that needs to be addressed for Step 3.

### Unit test coverage check for Step 3

- **State classifier**: table and property tests cover every designed state, lease status, marker overlay, convergence recovery, and the fail-closed catch-all, with deterministic boundary tests for every defensive branch.
- **Lifecycle facade**: tests cover start, request, answer, consume, continue, escalation, confirmation, completion, resolution, invalid transition boundaries, and identity or round mismatch rejection.
- **Repair behavior**: fault-injection tests cover torn request entries, interrupted answer replacement, escalation append failure, confirmation cleanup interruption, replay mismatch, and exact visible-answer repair.
- **Wait behavior**: injected-clock tests cover periodic progress, monotonic timeout, abandonment attribution, already-escalated, inconsistent, and repair-required terminal states with no lease writes during polls.
- **Human behavior**: tests cover both convergence choices, persisted authorization replay, cancellation, guidance propagation, progress reset, clear and archive resolution, and rejection of unauthorized or incomplete actions.
- **Coverage evidence**: the final full Groundhog run reports 100% repository coverage across all Step 3 production modules.

No, there is no unit-tested class below 100% that needs completing for Step 3.

### Feature integrity for Step 3

- **Existing protocol and store behavior**: the Step 1 model contracts and Step 2 exact-path persistence tests remain green; the store extension defaults to its prior marker-clearing behavior for existing callers.
- **Opt-in compatibility**: lifecycle start rejects disabled review mode, so existing workflows remain inert until later adapters explicitly invoke the core under enabled configuration.
- **Evidence preservation**: timeout, abandonment, no-progress, disagreement, cancellation, and inconsistent shapes stop safely without deleting authoritative review evidence.
- **Reporting and diagnostics**: stable state diagnostics, transcript outcomes, wait results, expected-actor attribution, and human decision metadata extend reporting without changing existing workflow output surfaces.
- **Global regression evidence**: the final Groundhog walk passed quality checks, affected tests, the full 1,398-test suite, 100% coverage, and the duration gate.

No, no existing feature or reporting capability appears impaired by Step 3.

---

## Step 4. Non-interactive utility, templates, and canonical requestor adapters

### Analysis of Step 4 implementation state

Yes. Step 4 has been fully implemented.

The repository now exposes the lifecycle core through one exact-document CLI and self-locating launcher, one canonical requestor instruction, redirect-only provider adapters, and focused command and instruction tests.

### Goal for Step 4

Expose all core operations through one stable non-interactive launcher and one canonical requestor instruction with provider-specific redirect-only adapters.

### Step 4 improvement expectations

- Later roles call one shared utility instead of reproducing protocol mechanics.
- CLI status and exit codes are stable and machine-readable.
- Wait progress is emitted only on standard error and exactly one final JSON result is emitted on standard output.
- Caller-owned substantive input files are accepted only under the effectively ignored project-root `a.*` convention.
- Every request summary validates umbrella, exact document or plan/step, and round.
- Provider Markdown contains no copy of the canonical instruction body.

### What was implemented for Step 4

- **Non-interactive CLI**: added exact document-name identity inference, typed runtime construction, configuration loading, activation checks, and dispatch for activate, status, start, request and answer publication, request and answer waits, answer consumption, automated continuation, abandoned-round reclaim, escalation, confirmation, cancellation, clear-or-archive resolution, and completion.
- **Stable result contract**: every handled invocation emits one final sorted UTF-8 JSON object with operation, identity, state, outcome, round, paths, and diagnostic data; expected protocol stops use exit `3`, invalid or fatal input uses exit `2`, and completed operations use exit `0`.
- **Caller-owned input boundary**: substantive content, summaries, and guidance must be exact UTF-8 files directly under the project root with `a.*` names and effective Git-ignore coverage; each file is read once and never deleted by the CLI.
- **Bounded wait reporting**: wait operations remain one core-owned monotonic call, emit periodic JSON only on standard error, and leave standard output for the one final result.
- **Self-locating launcher**: added `bin/review_exchange.bat` using the established newest llm-shared virtual-environment interpreter pattern without project activation.
- **Canonical requestor guidance**: added one root instruction that defines authored input, identity-summary, automated-round, convergence, escalation, recovery, and exit handling while delegating every protocol mutation to the launcher.
- **Redirect-only provider surfaces**: added the `.agent` workflow locator plus packaged instruction and skill redirects without copying the canonical body.
- **Focused verification**: added command, boundary, entry-point, canonical-body, and redirect tests; the final Groundhog walk passed the quality gate, 7 affected tests, all 1,438 tests, 100% coverage, and the duration gate with zero outliers or exclusions.

### Step 4 implementation-to-plan variances

CLI boundary coverage was extracted to `test_review_exchange_cli_boundaries_tdd.py` so the primary parameterized command test remains below the 650-line test ceiling. Both leaves target the same command adapter and remain in the planned test package.

`tools/review_exchange_cli.py` is 575 lines, which is above the advisory 550-line safe target but below the 650-line ceiling. Operation dispatch is split into small typed handlers, and the project complexity gate reports no violation; the plan requires a production split only if the file exceeds 650 lines.

The Step 4 code review repaired one contract gap found against the staged work: the expected-stop exit mapping omitted the owning-action-pending state that the consolidated Q05 answer lists among exit-3 protocol stops. The stop set, the parametrized stop-state test, and the canonical instruction's exit-3 enumeration now all include the pending human-authorized owning action.

### New types or classes introduced for Step 4

- `CorePort`: structural application port listing only the lifecycle operations used by the command adapter.
- `Runtime`: immutable bundle of project root, validated context, derived paths, configuration, and lifecycle port.
- `OperationResult`: immutable delegated outcome with optional observation, exit override, and operation-specific fields.
- `JsonArgumentParser`: parser adapter that converts argument failures into the mandatory JSON fatal-result path.

### Architecture check for Step 4

- **Dependency direction**: the CLI imports and calls the application-facing `ReviewExchangeCore`; the core does not import the CLI, launcher, instruction, or provider adapters.
- **Thin adapter boundary**: command handlers validate transport inputs and translate typed results but contain no lifecycle state table, transition ordering, lease renewal, transcript repair, or confirmation policy.
- **Filesystem isolation**: exact caller-input reads and one fixed Git ignore probe stay in the outer command adapter, while protocol artifact persistence remains in the existing store adapter.
- **Instruction ownership**: reusable coordination prose exists only under `instructions/`; `.agent` and `.agents` files retain discovery metadata and direct canonical redirects.
- **Cohesion and size**: dispatch is split by operation family, all production and test files stay below the 650-line ceiling, and the quality gate reports no complexity violation.

No, there is nothing that needs to be addressed for Step 4.

### Performance check for Step 4

- **No new `O(n^2)` or `O(n log n)` path**: identity parsing uses one fixed regular expression, output rendering walks one constant path set, and dispatch selects one operation from a fixed dictionary.
- **Input cost**: each operation validates only its explicit root input paths, performs one Git ignore probe per input, and reads each UTF-8 file exactly once without scanning project content.
- **Wait cost**: the CLI delegates one bounded call to the core and adds only constant-time progress serialization; it does not create repeated short waits or persisted wall-time deadlines.
- **Test timing**: CLI tests inject the application port and clocks, perform no real waits, and the final Groundhog duration gate reports zero outliers.

No, there is no performance issue that needs to be addressed for Step 4.

### Unit test coverage check for Step 4

- **Command operations**: parameterized tests cover every registered operation, typed argument propagation, common JSON fields, exact found states, caller-input retention, stderr progress, and exit `0`, `2`, and `3` behavior.
- **Command boundaries**: focused tests cover numeric validation, family/document mismatch, real runtime construction, Git ignore outcomes, missing and invalid UTF-8 inputs, disabled status, defensive dispatch, and direct script execution.
- **Instruction structure**: tests require launcher and core delegation, caller-input flags, output-channel guidance, direct provider redirects, and absence of a copied lifecycle table or canonical body.
- **Coverage evidence**: Groundhog reports 100% repository coverage with all branches in `tools/review_exchange_cli.py` exercised.

No, there is no unit-tested class below 100% that needs completing for Step 4.

### Feature integrity for Step 4

- **Opt-in behavior**: disabled configuration returns the documented expected stop without calling a lifecycle mutation, preserving existing writer behavior until later integrations opt in.
- **Protocol reuse**: all artifact state and transition authority remains in the Step 3 core; the new surface adds transport and reporting without changing existing model, store, lifecycle, or transcript contracts.
- **Caller evidence**: rejected or consumed caller-owned input files remain untouched, and fatal command input produces a diagnostic without manual artifact cleanup.
- **Adapter integrity**: existing instruction-structure checks pass with the new canonical instruction, packaged redirect, skill redirect, and workflow locator.
- **Global regression evidence**: the final walk passed the quality gate and all 1,438 tests with no warnings, expected failures, outliers, or exclusions.

No, no existing feature or reporting capability appears impaired by Step 4.

---

## Step 5. Integrated acceptance and rollout verification

### Analysis of Step 5 implementation state

Yes. Step 5 has been fully implemented.

The repository now proves the public review-exchange boundary across real temporary Git repositories, process boundaries, both artifact families, recovery and escalation paths, convergence outcomes, identity isolation, and deterministic bounded waits.

### Goal for Step 5

Validate the public core boundary across real Git repositories, both artifact families, subprocess interruption and repair, automated rounds, escalation, and both convergence outcomes.

### Step 5 improvement expectations

- Opt-in activation and effective-ignore failure behave correctly in consuming repositories.
- Cross-document isolation and same-document exclusion hold across process boundaries.
- Crash windows repair or escalate without losing evidence.
- Torn transcript appends truncate to the persisted offset and re-append exactly one complete entry across the acceptance boundary.
- Long waits expose periodic standard-error progress while producing one final standard-output JSON result under one monotonic deadline.
- Convergence confirmation, override guidance, and continuing authorization survive session interruption.

### What was implemented for Step 5

- **Real CLI and Git acceptance**: added subprocess journeys in effectively ignored temporary repositories for absent-marker inertness, ignore refusal, concurrent specification and code identities, same-document exclusion, and independent transcripts.
- **Multi-round convergence**: exercised code-family continuation, convergence retention, cross-session gate re-presentation, continuing Commit authorization, owning-action completion, and ordered local-offset transcript evidence.
- **Human override and resumption**: exercised specification-family another-round guidance, escalation archival, artifact cleanup, and a fresh round after human resolution.
- **Wait reporting**: verified injected-clock progress emits multiple standard-error diagnostics, one final standard-output JSON result, and one monotonic deadline without a real wait.
- **Crash recovery**: added fault-injected acceptance coverage for request publication, answer rename and visible append, torn transcript suffixes, answer consumption, escalation append, and owning-action completion.
- **Bounded automation**: verified attributed abandonment, no-progress escalation, persistent disagreement escalation, and exact wait isolation from unrelated identities.
- **Windows Git boundary**: changed effective-ignore validation to NUL-delimited `git check-ignore -z --stdin`, preventing text-mode carriage returns from becoming part of transient paths across Windows subprocess boundaries, with focused unit coverage.
- **Duration-gate repair**: moved real-Git setup for the new recovery journeys and eight existing prepare-release scenarios into fixtures while preserving their behavioral assertions.
- **Global verification**: the final Groundhog walk passed all 1,451 tests, 100% coverage, and the duration gate with zero failures, warnings, expected failures, outliers, or exclusions.

### Step 5 implementation-to-plan variances

The acceptance coverage exceeded one safe leaf, so recovery and fault-injection journeys were extracted to `tests/unit/tools/test_review_exchange_recovery_acceptance/test_review_exchange_recovery_acceptance_tdd.py` exactly as the plan's split guidance permits. The primary acceptance leaf remains below the 650-line ceiling.

Real CLI subprocess coverage exposed Windows text-mode newline translation in the existing Git ignore probe. The outer path adapter and its focused unit test were updated to use Git's NUL-delimited protocol; no lifecycle or persistence contract changed.

The global duration gate initially reported repository setup inside four new recovery calls and eight existing prepare-release calls. Heavy real-Git setup now occurs in fixtures, leaving measured calls to assert the same results; both affected files and the final full walk pass.

The Step 5 code review repaired three malformed identity paths in the versioned review transcript: the Step 4 and Step 5 requestor entries wrote a slash instead of a dot inside the umbrella name, and the Step 5 entry did the same inside the reviewed-document name. These hand-authored lines are exactly the machine-versus-human identity mismatch the core's summary validation rejects; once the specialized adapters drive the outer dogfood loop through the core, such lines fail closed before publication.

### New types or classes introduced for Step 5

- `CliResult`: immutable test result for one real CLI subprocess invocation.
- `IsolationJourney`: immutable fixture result for opt-in and identity-isolation evidence.
- `CodeJourney`: immutable fixture result for multi-round code convergence and authorization evidence.
- `ResolutionJourney`: immutable fixture result for human override, archive, and fresh-round evidence.
- `FakeTime`: deterministic acceptance clock that advances waits without sleeping.

No new production type or class was introduced in Step 5.

### Architecture check for Step 5

- **Public boundary**: end-to-end journeys invoke the command adapter as a subprocess and inspect only result JSON and observable artifacts.
- **Fault boundary**: recovery tests inject faults through the public lifecycle core and store seam so they can target atomic crash windows deterministically without duplicating protocol behavior.
- **Dependency direction**: the Windows ignore repair remains in the outer path-validation adapter; domain models, lifecycle policy, and persistence do not import Git or command concerns.
- **Identity isolation**: each journey supplies one exact reviewed document and observes only its derived fixed path set, preserving the established ports-and-adapters boundary.
- **Cohesion and size**: the plan-authorized recovery leaf keeps both acceptance files below the 650-line ceiling, and the quality gate reports no complexity violation.

No, there is nothing that needs to be addressed for Step 5.

### Performance check for Step 5

- **No new asymptotic growth**: activation adds one NUL-delimited Git ignore probe over the constant transient-path set; state operations still derive and touch only fixed identity paths.
- **No scans**: acceptance verifies exact-path isolation, and production review-exchange code introduces no project-tree traversal or transcript-history scan.
- **Deterministic waits**: injected clocks advance the one monotonic deadline without `sleep`, repeated short waits, or persisted wall-time deadlines.
- **Measured duration**: real-Git construction is fixture setup rather than assertion-call work; the final duration report contains zero outliers and zero exclusions.

No, there is no performance issue that needs to be addressed for Step 5.

### Unit test coverage check for Step 5

- **Production classes**: Step 5 introduces no production class requiring a new class-named unit-test leaf.
- **Path adapter change**: the focused path suite asserts the `-z` Git invocation and NUL-delimited input and output handling, alongside existing activation and ignore-failure branches.
- **Acceptance support types**: the new immutable journey results and fake clock are test-only scaffolding exercised by their owning acceptance leaves.
- **Coverage evidence**: the final Groundhog walk reports 100% repository coverage across all 1,451 tests.

No, there is no unit-tested class below 100% that needs completing for Step 5.

### Feature integrity for Step 5

- **Opt-in rollout**: an absent marker remains inert, and non-ignored transients or a non-repository root fail before artifact mutation.
- **Artifact families**: specification and code exchanges both complete through shared core behavior without introducing later specialized requestor or reviewer roles.
- **Recovery evidence**: every planned publication, append, consumption, escalation, and owning-completion interruption either repairs once or preserves an attributed escalation.
- **Convergence outcomes**: both confirmation and another-round guidance survive process interruption, and continuing authorization replays without a second human question.
- **Isolation and ordering**: different identities progress concurrently, the same document is excluded, exact waits ignore unrelated artifacts, and transcripts retain ordered local-offset evidence.
- **Regression evidence**: the quality gate, full suite, coverage gate, and duration gate all pass with no existing feature or reporting regression detected.

No, no existing feature or reporting capability appears impaired by Step 5.
