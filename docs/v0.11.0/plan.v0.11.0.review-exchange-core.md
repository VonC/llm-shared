# v0.11.0 review-exchange-core implementation plan -- durable review rounds with gated convergence

Implement the shared review transport as exact-path, crash-recoverable tooling whose specialized review roles remain deferred to later umbrella items.

- **Protocol foundation**: typed identity, configuration, envelopes, paths, coordination state, and timestamps.
- **Safe persistence**: atomic artifacts, short transition locks, append-only transcripts, tombstones, and archives.
- **Bounded lifecycle**: automated rounds, exact waits, recovery, escalation, and durable convergence confirmation.
- **Reusable surface**: one non-interactive launcher, canonical requestor instruction, thin adapters, templates, and acceptance coverage.

## Plan goal for v0.11.0 review-exchange-core

Implement umbrella item 1 from `docs/v0.11.0/draft.v0.11.0.review-mode.md` exactly as specified by `docs/v0.11.0/feature-request.v0.11.0.review-exchange-core.md` and `docs/v0.11.0/design.v0.11.0.review-exchange-core.md`.

- **Step 1 goal**: establish validated exchange identity, context, configuration, derived paths, envelopes, and coordination records.
- **Step 2 goal**: implement exact-path persistence, transcript, tombstone, archive, and short-lock primitives.
- **Step 3 goal**: implement the complete lifecycle, state classifier, bounded waiting, recovery, escalation, and convergence confirmation.
- **Step 4 goal**: expose the core through a thin CLI launcher, templates, canonical requestor instruction, and provider redirects.
- **Step 5 goal**: prove the integrated specification and code-family protocol through temporary-project acceptance tests.

No Step 0 performance gate is needed. The timing-sensitive wait logic uses injected monotonic clocks and poll functions, while the IO contract is enforced through exact-path tests and call-count assertions rather than wall-clock `xfail` tests.

---

## Scope anchors for v0.11.0 review-exchange-core plan

This plan delivers the core only:

1. Review-mode activation through `a.review-mode`, including the 1,800-second default and positive override.
2. Complete specification and code-family artifact identity, summary identity, and transient-ignore validation.
3. Durable lease coordination, atomic publication, append-only transcripts, recovery, and human escalation.
4. Fully automated intermediate rounds and a distinct, durable human gate only at convergence.
5. The canonical requestor instruction, its thin adapters, shared templates, launcher, and utilities.

The following are in scope:

- Family-neutral requestor/reviewer transport and metadata.
- The generic outcomes `another-round` and `continue-owning-workflow`.
- Registered family convergence signals and display labels.
- Exact status, wait, transition, reclaim, confirmation, resolution, archive, and completion operations.

The following remain deferred to later rows of `docs/v0.11.0/draft.v0.11.0.review-mode.md`:

- Specification-requestor feedback generation and the `Consolidate` owning action.
- Specification-reviewer evaluation behavior.
- Code-requestor implementation reporting and the `Commit` owning action.
- Code-reviewer implementation validation and repair behavior.
- User-facing review-mode documentation beyond the core instruction.

---

## Complexity bound clarification for v0.11.0

- **O(1) path and state work per operation**: each operation receives one exact reviewed-document identity and checks a constant derived path set.
- **O(1) work per waiting poll**: only the expected counterpart path and coordination record are checked; polls never scan or renew the lease.
- **O(k) current-entry suffix verification**: append repair seeks directly to the persisted pre-append offset and reads only the current entry's suffix, never transcript history.
- **O(k) serialization**: request, answer, coordination, and transcript-entry work is linear only in the content being written or parsed.
- **O(r) bounded recovery**: recovery handles the fixed number `r` of artifacts for one identity, never all project review files.

No response path may add project-tree discovery, transcript rereads, quadratic round history processing, or timestamp-based nearest-file selection.

---

## File-based IO cost clarification for v0.11.0 review-exchange-core

| Operation | Reads | Writes | Prohibited work |
| --- | --- | --- | --- |
| Activation | Exact marker and one bounded `git check-ignore` input set | None on failure | Project or docs directory scan |
| State/status | Exact request, answer, tombstone, and coordination paths | None | Transcript read or neighboring artifact search |
| Wait poll | Exact expected artifact and coordination paths | None | Lease renewal, transcript read, or glob scan |
| Transition | Exact state plus prepared content; current suffix from the persisted pre-append offset only for idempotency | Atomic exact-path writes, optional torn-suffix truncation, and one append | Full transcript load, whole-tree discovery, or long-held lock |
| Recovery | Fixed artifacts for one selected identity | Exact archive/coordination/transcript paths | Global cleanup scan |

The CLI requires the exact reviewed-document path. It derives paths once and passes the resulting value object through the operation, keeping the loading phase to bounded exact-path reads.

---

## Confirmed technical facts for v0.11.0 plan viability

**Files over the 650-line planning limit**:

- None of the Python files modified or created by this plan currently exceed the limit.

**Files in the 550-through-650 risk band and deliberately left unchanged**:

- `tools/prompt_workflow.py`: 572 lines; the review core uses its own launcher instead of growing this hub.
- `tools/prompt_workflow_docs.py`: 613 lines; the core reuses `resolve_document` without modifying the module.
- `tools/prompt_workflow_skill.py`: 620 lines; later adapters consume the core without adding routing logic to this hub in item 1.
- `tools/coverage_gap_functions_mapping.py`: 563 lines; it is unrelated to review exchange and remains untouched.
- `tests/unit/tools/test_prompt_workflow_main.py`: 599 lines; CLI coverage goes into a new focused leaf.
- `tests/unit/tools/test_prompt_workflow_docs/test_prompt_workflow_docs_tdd.py`: 595 lines; document-resolution behavior is reused, not extended here.
- `tests/unit/tools/test_prompt_workflow_acceptance/test_prompt_workflow_acceptance_tdd.py`: 585 lines; review acceptance coverage gets its own leaf.

**Files below 550 and safe to extend**:

- `tools/prompt_workflow_git.py`: 198 lines; reused without edits for bounded Git calls.
- `tools/__init__.py`: 37 lines; the existing package already permits direct imports of the new modules and needs no export growth.
- `bin/prompt_workflow.bat`: 35 lines; used only as the launcher pattern and left unchanged.

**What does not exist yet**:

- All `tools/review_exchange_*.py` protocol modules.
- `bin/review_exchange.bat`.
- Review request, answer, and transcript templates.
- `instructions/review-requestor.md` and its provider redirects.
- Focused review-exchange unit, property, CLI, instruction, and acceptance test leaves.

**Other confirmed facts**:

- `.gitignore` contains `a.*`; activation must still verify the consuming repository's effective ignore behavior.
- `tools._models.find_project_root`, exported as `tools.find_project_root`, is the canonical project-root dependency.
- `docs_dirs_for_version` and `resolve_document` already support the repository's documentation layouts.
- Python 3.13, `pytest-timeout`, and Hypothesis are available.
- The generic Codex structure test requires every canonical instruction to have `.agents/llm-shared/instructions` and `.agents/llm-shared/skills` redirects.

---

## Current test-tree validation snapshot for v0.11.0 review-exchange-core

Existing suites that must remain green:

- `tests/unit/tools/test_prompt_workflow_docs/` for exact document resolution.
- `tests/unit/tools/test_prompt_workflow_skill/` and `test_prompt_workflow_main.py` for workflow routing stability.
- `tests/unit/tools/test_instruction_structure/` for canonical/adaptor separation and plugin completeness.
- The full groundhog suite and coverage gate.

New test leaf directories:

- `tests/unit/tools/test_review_exchange_models/`.
- `tests/unit/tools/test_review_exchange_paths/`.
- `tests/unit/tools/test_review_exchange_store/`.
- `tests/unit/tools/test_review_exchange_state/`.
- `tests/unit/tools/test_review_exchange_lifecycle/`.
- `tests/unit/tools/test_review_exchange_cli/`.
- `tests/unit/tools/test_review_requestor_instruction/`.
- `tests/unit/tools/test_review_exchange_acceptance/`.

Property-based coverage is required for identity/path round-tripping and state-shape classification because cross-identity contamination and unlisted artifact combinations are the highest combinatorial risks.

---

## Runtime file note for v0.11.0 review-exchange-core plan

- `a.review-requested.*`, `a.review-answer.*`, `a.review-active.*`, `a.review-consumed.*`, transition-lock files, and `a.review-archive.*` are transient and must pass effective Git-ignore validation before activation.
- `review.<type>.vX.Y.Z.<slug>.md` and `review.code.vX.Y.Z.<slug>.md` are versioned transcripts beside the reviewed document.
- Same-directory temporary files are removed after successful atomic replacement and preserved only when required as recoverable evidence.

---

## Shared execution command checklist for all v0.11.0 review-exchange-core steps

1. Count every step file before editing with `@(Get-Content -LiteralPath <path>).Count`; use `0` for a new file.
2. Add the step's tests first, including the specified property test where applicable.
3. Run only the step's focused tests through `ghog single <test-paths>`.
4. Run the step's `rg` checks for prohibited scans, stale lock language, duplicated adapter bodies, and required operation names.
5. Run `ghog day`, fixing and repeating until it reports the objective with `exit=0`.
6. Count lines after editing and compare each Python file with the 650-line planning ceiling.
7. Split by the guidance below before completion if any Python file exceeds 650 lines.
8. Record advisory-estimate variance without failing a step when the actual file remains at or below 650.

## Ready-to-run command templates for all v0.11.0 review-exchange-core steps

- Line count: `@(Get-Content -LiteralPath <path>).Count`
- Focused tests: `ghog single <step-test-paths>`
- Grep verification: `rg -n "<required-or-prohibited-pattern>" <step-paths>`
- Shared gate: `ghog day`, repeated fix-and-walk until `exit=0`

---

## Numbered steps for v0.11.0 review-exchange-core

### Step 1. Typed identity, configuration, envelopes, and derived paths

#### Step 1 -- analysis and intent for protocol identity

Issues to address:

- Every artifact, summary, coordination record, and transcript entry must agree on one complete identity.
- Invalid markers, slugs, context paths, metadata blocks, or ignore coverage must fail before mutation.
- The code-family `code.code` identity and optional umbrella require explicit representation.

Fix intent:

- Introduce immutable protocol models and strict JSON serialization/validation.
- Derive the complete constant path set from an exact reviewed-document path.
- Validate review-mode configuration, Git presence, and effective ignore behavior.

Expected outcome:

- Identity mismatch and ambiguity are rejected before publication.
- Models represent active, awaiting-confirmation, owning-action-pending, and escalated coordination without textual inference.

Step framing:

- Design links: Identity and configuration design; derived path contract; review-content envelope; Q02, Q04, Q05, Q07, and Q11.
- Execution checklist: `Shared execution command checklist for all v0.11.0 review-exchange-core steps`.

#### Step 1 -- implementation for protocol identity

**Files involved**:

- `tools/review_exchange_models.py` (new, to be created).
- `tools/review_exchange_models_coordination.py` (new, line-budget split for durable state).
- `tools/review_exchange_models_envelope.py` (new, line-budget split for content metadata).
- `tools/review_exchange_paths.py` (new, to be created).
- `tools/__init__.py` (existing, export the new public protocol models).
- `tests/unit/tools/test_review_exchange_models/__init__.py` (new, to be created).
- `tests/unit/tools/test_review_exchange_models/test_review_exchange_models_tdd.py` (new, to be created).
- `tests/unit/tools/test_review_exchange_models/test_review_exchange_models_pbt.py` (new, to be created).
- `tests/unit/tools/test_review_exchange_models/test_review_exchange_models_validation_tdd.py` (new, validation-branch split).
- `tests/unit/tools/test_review_exchange_paths/__init__.py` (new, to be created).
- `tests/unit/tools/test_review_exchange_paths/test_review_exchange_paths_tdd.py` (new, to be created).

**Tests first**:

- Cover family/type/version/slug validation, optional umbrella validation, exact document and step context, local-offset timestamps, and JSON round trips.
- Property-test that valid identities produce distinct, stable path sets and parse back without cross-family or cross-slug collisions.
- Cover empty/positive/invalid marker content, non-Git activation, and every derived transient passed through one effective `git check-ignore` validation.
- Cover the required H1 title, first `## JSON` section parsing, H2 authored
  sections, and machine/human summary mismatch rejection.

**Classes and behavior**:

- `ExchangeIdentity`, `ReviewContext`, `ArtifactPaths`, `Envelope`, `CoordinationRecord`, `FamilyPolicy`, and enums for family, role, status, disposition, outcome, actor, marker, and artifact state.
- `FamilyPolicy` validates one convergence signal and two distinct display labels mapped to `another-round` and `continue-owning-workflow`; the start operation persists the immutable policy for every resumed process.
- `ReviewConfiguration` reads `a.review-mode`, applies 1,800 seconds by default, and accepts only a positive explicit override.
- Path derivation uses the actual document parent for transcripts and the project root for transients, including intentional `a.review-active.code.code...` names.

**Completion criteria**:

- `ghog single tests/unit/tools/test_review_exchange_models tests/unit/tools/test_review_exchange_paths` passes.
- `rg -n "rglob|glob|iterdir" tools/review_exchange_models.py tools/review_exchange_models_coordination.py tools/review_exchange_models_envelope.py tools/review_exchange_paths.py` finds no normal-path tree scan.
- Invalid configuration, context, identity, envelope, and ignore coverage produce stable fail-closed diagnostics without writes.
- `ghog day` reports `exit=0`.

#### Step 1 -- addendums for protocol identity

Line-budget checkpoint:

- `tools/review_exchange_models.py`: baseline 0; below-550 safe; ceiling 650; advisory estimate 430–520 lines after its focused splits.
- `tools/review_exchange_models_coordination.py`: baseline 0; below-550 safe; ceiling 650; advisory estimate 200–300 lines.
- `tools/review_exchange_models_envelope.py`: baseline 0; below-550 safe; ceiling 650; advisory estimate 160–240 lines.
- `tools/review_exchange_paths.py`: baseline 0; below-550 safe; ceiling 650; advisory estimate 220–320 lines.
- Each new Python test or `__init__.py`: baseline 0; below-550 safe; ceiling 650; keep each test leaf focused enough to remain below 550 when practical.

Split guidance:

- If models approach 650, keep durable coordination in `tools/review_exchange_models_coordination.py` and fenced-envelope handling in `tools/review_exchange_models_envelope.py`.
- If paths would exceed 650, extract marker and Git activation to `tools/review_exchange_activation.py`.

Full workflow timing run readiness:

- Focused model/path tests, then `ghog day`.

Time-gated status for Step 1:

- No wall-clock gate; property tests and bounded-call assertions own the risk.

### Step 2. Atomic artifact store, transcript, tombstone, and archive primitives

#### Step 2 -- analysis and intent for safe persistence

Issues to address:

- Partial artifact writes, torn transcript appends, long-held locks, transcript duplication, and delete-before-answer crashes can lose or contaminate review evidence.
- Agents must append entries without rereading transcript history.
- Recovery must preserve exact evidence under stable identity names.

Fix intent:

- Centralize exact-path reads, same-directory atomic publication, short OS locks, and idempotent transcript appends.
- Implement request tombstones and identity/timestamp archives.
- Materialize role-neutral request, answer, and family transcript templates.

Expected outcome:

- Storage operations are individually safe and directly reusable by the lifecycle service.
- Transcript initialization and append never fabricate or duplicate a review round.

Step framing:

- Design links: Safe publication transitions; transcript design; human escalation and fresh resumption; Q03, Q06, and Q08.
- Execution checklist: shared checklist above.

#### Step 2 -- implementation for safe persistence

**Files involved**:

- `tools/review_exchange_store.py` (new, to be created).
- `templates/review-request.template.md` (new, to be created).
- `templates/review-answer.template.md` (new, to be created).
- `templates/review-specification-transcript.template.md` (new, to be created).
- `templates/review-code-transcript.template.md` (new, to be created).
- `tests/unit/tools/test_review_exchange_store/__init__.py` (new, to be created).
- `tests/unit/tools/test_review_exchange_store/test_review_exchange_store_tdd.py` (new, to be created).

**Tests first**:

- Cover atomic create/overwrite, UTF-8 completeness, exact identity verification, stale-answer cleanup, and request-to-tombstone rename before answer visibility.
- Inject failures before and after each mutation and assert the recoverable artifact shape.
- Cover transcript initialization by family/version, append-only role/round entries, stable entry identifiers, and idempotent repair without transcript-history scans.
- Inject a torn transcript append after persisting the pre-append byte offset; verify repair reads only from that offset, truncates to it when the target footer is absent or incomplete, and re-appends one complete entry.
- Cover allowed archive kinds and compact local timestamp names.

**Classes and behavior**:

- `ReviewExchangeStore` owns exact artifact IO and never discovers identities by scanning.
- `transition_lock` uses standard-library `msvcrt.locking` on Windows and `fcntl.flock` elsewhere against the effectively ignored `a.review-lock.<family>.<type-token>.vX.Y.Z.<slug>.lock` path. It is held only across one read/validate/write transition and is released by the operating system before counterpart waits or LLM work, including process exit.
- `publish_atomic`, `append_transcript_once`, `consume_request_to_tombstone`, `archive_evidence`, and exact cleanup operations preserve evidence and ordering. Before appending, `append_transcript_once` persists the transcript's pre-append byte length and stable entry identifier in the incomplete-transition marker. Repair reads only from that offset: a complete target footer clears the marker; any other suffix is truncated to the recorded length and regenerated content is appended once.

**Completion criteria**:

- `ghog single tests/unit/tools/test_review_exchange_store` passes.
- Failure injection demonstrates every publication and append window, including a torn transcript write, is recoverable.
- Grep and focused tests show no full transcript load or directory discovery on normal operations and enforce offset-based suffix verification and truncation.
- `ghog day` reports `exit=0`.

#### Step 2 -- addendums for safe persistence

Line-budget checkpoint:

- `tools/review_exchange_store.py`: baseline 0; below-550 safe; ceiling 650; advisory estimate 420–540 lines.
- Store test files and initializers: baseline 0; below-550 safe; ceiling 650; advisory test estimate 420–540 lines.
- Markdown templates: baseline 0; not subject to the Python ceiling; keep them coordination-only.

Split guidance:

- If the store exceeds 650, extract transcript initialization/append to `tools/review_exchange_transcript.py`; keep atomic artifact and lock primitives in the store.

Full workflow timing run readiness:

- Focused store tests with injected failures, then `ghog day`.

Time-gated status for Step 2:

- No perf gate; exact-call assertions ensure bounded IO.

### Step 3. Lifecycle state machine, bounded waits, repair, escalation, and confirmation

#### Step 3 -- analysis and intent for lifecycle control

Issues to address:

- All reachable artifact/lease shapes need one observable outcome, including owning action pending.
- Waiting polls must remain bounded without extending dead actors' leases.
- Automated rounds, no-progress, clarification, escalation, and convergence confirmation require durable cross-process state.

Fix intent:

- Implement one classifier and transition service over the typed models and store.
- Make every transcript-appending transition marker-first and idempotently repairable.
- Persist and re-report human authorization without asking twice after an interrupted owning action.

Expected outcome:

- Intermediate rounds continue automatically; convergence alone enters a durable human gate.
- Timeout, abandonment, inconsistency, no-progress, and disagreement preserve evidence and stop safely.

Step framing:

- Design links: Observable exchange states; safe publication transitions; waiting and no-progress; convergence confirmation; acceptance cases; Q01, Q06, Q09, and Q10.
- Execution checklist: shared checklist above.

#### Step 3 -- implementation for lifecycle control

**Files involved**:

- `tools/review_exchange_core.py` (new, to be created).
- `tests/unit/tools/test_review_exchange_state/__init__.py` (new, to be created).
- `tests/unit/tools/test_review_exchange_state/test_review_exchange_state_tdd.py` (new, to be created).
- `tests/unit/tools/test_review_exchange_state/test_review_exchange_state_pbt.py` (new, to be created).
- `tests/unit/tools/test_review_exchange_lifecycle/__init__.py` (new, to be created).
- `tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_lifecycle_tdd.py` (new, to be created).

**Tests first**:

- Table-test every listed state and property-test that all remaining artifact/status/lease shapes fail closed as inconsistent.
- Cover current and expired coordination-only states, marker overlays, request-publication regeneration, envelope-authoritative convergence recovery, and identity-scoped transcript repair from the marker's pre-append offset.
- Cover transitions start, request, answer, consume, continue, reclaim, escalate, confirm/resolve, archive, and complete with failures at each boundary.
- Use injected monotonic time to cover timeout versus abandonment, TTL renewal only on state change, no renewal on poll, suspension only at the gate, and periodic progress callbacks within one bounded in-process wait.
- Verify request, answer, escalation, and human-entry repairs reconstruct the target content, truncate a torn suffix to the persisted offset, and append exactly one complete footer-bearing entry.
- Cover two unchanged change-request rounds, one clarification round, human override guidance/reset, cancellation, escalation idempotence, and owning-action authorization replay.

**Classes and behavior**:

- `ReviewExchangeCore.classify` returns the complete observable state without consulting timestamps when identity evidence conflicts.
- State-changing operations renew the effective-limit lease; `wait_for_exact` runs once against one monotonic deadline, never renews, and exposes periodic progress callbacks without converting the wait into host-managed slices.
- `confirm` validates registered labels and stores their generic outcome; persisted `continue-owning-workflow` is re-reported until `complete` succeeds.
- `resolve_escalation` archives or clears stopped evidence, records human resolution, and starts a fresh lease rather than resuming the failed transition.
- `reclaim` renews an expired lease in place for an abandoned round with active coordination and intact evidence, changes no artifact or transcript content, stays idempotent on live rounds, and rejects escalated, confirming, interrupted, and inconsistent exchanges.

**Completion criteria**:

- `ghog single tests/unit/tools/test_review_exchange_state tests/unit/tools/test_review_exchange_lifecycle` passes.
- The property test covers every generated combination through a listed state or the fail-closed catch-all.
- Grep confirms waiting code contains no lease write or wall-time deadline persistence, and confirmation replay contains no choice re-presentation.
- `ghog day` reports `exit=0`.

#### Step 3 -- addendums for lifecycle control

Line-budget checkpoint:

- `tools/review_exchange_core.py`: baseline 0; below-550 safe; ceiling 650; advisory estimate 500–620 lines.
- Each state/lifecycle test file and initializer: baseline 0; below-550 safe; ceiling 650; keep generated-shape coverage separate from transition scenarios.

Split guidance:

- If the core exceeds 650, extract pure state classification to `tools/review_exchange_state.py`; keep transitions and orchestration in `review_exchange_core.py`.
- If lifecycle tests approach the ceiling, split confirmation/recovery scenarios into a new matching test leaf rather than growing one test hub.

Full workflow timing run readiness:

- Focused state and lifecycle tests, then `ghog day`.

Time-gated status for Step 3:

- Injected clocks replace real sleeps; no timeout marker is added.

### Step 4. Non-interactive utility, templates, and canonical requestor adapters

#### Step 4 -- analysis and intent for reusable surfaces

Issues to address:

- Later requestor and reviewer items need a stable script instead of duplicating filesystem protocol rules.
- The core must ship one canonical requestor instruction while provider Markdown remains redirect-only.
- Human-readable summaries and machine envelopes must carry the same umbrella/document/step/round identity.

Fix intent:

- Add a thin self-locating launcher and subcommand-based Python CLI over core operations.
- Write the canonical coordination instruction and all repository-required redirects.
- Keep family-specific analysis and owning actions out of the core.

Expected outcome:

- Any later adapter can call the same status, lifecycle, wait, confirmation, and recovery interface.
- Instruction-structure tests prove there is one canonical body.

Step framing:

- Design links: Core-owned surfaces; later adapter responsibilities; content envelope; convergence confirmation.
- Execution checklist: shared checklist above.

#### Step 4 -- implementation for reusable surfaces

**Files involved**:

- `tools/review_exchange_cli.py` (new, to be created).
- `bin/review_exchange.bat` (new, to be created).
- `instructions/review-requestor.md` (new, to be created).
- `.agent/workflows/review-requestor.md` (new, to be created).
- `.agents/llm-shared/instructions/review-requestor.md` (new, to be created).
- `.agents/llm-shared/skills/review-requestor/SKILL.md` (new, to be created).
- `tests/unit/tools/test_review_exchange_cli/__init__.py` (new, to be created).
- `tests/unit/tools/test_review_exchange_cli/test_review_exchange_cli_tdd.py` (new, to be created).
- `tests/unit/tools/test_review_requestor_instruction/__init__.py` (new, to be created).
- `tests/unit/tools/test_review_requestor_instruction/test_review_requestor_instruction_tdd.py` (new, to be created).

**Tests first**:

- Cover CLI argument validation and stable machine-readable output for activate, status, start, publish/wait/consume, reclaim, escalate, confirm, resolve, archive, and complete operations.
- Cover exit codes for disabled mode, timeout, abandoned, inconsistent, repair-required, awaiting-confirmation, and fatal input.
- Cover a wait that emits periodic progress diagnostics only to standard error and exactly one final JSON object to standard output.
- Assert all summary fields are required and validated before request publication.
- Assert substantive caller-owned input files use effectively ignored project-root `a.*` names before the CLI reads them.
- Assert provider files only redirect to the canonical instruction and the canonical instruction delegates state mutations to the launcher.

**Classes and behavior**:

- `review_exchange_cli.main` resolves the project root through `tools.find_project_root`, requires an exact document path, constructs the core, dispatches one operation, and emits parseable status/result data. Substantive Markdown enters through operation-specific exact `--content-file`, `--summary-file`, and `--guidance-file` arguments under the effectively ignored project-root `a.*` convention; the CLI reads UTF-8 once and never deletes caller-owned input.
- Every invocation emits one final UTF-8 JSON object with the applicable `operation`, `identity`, `state`, `outcome`, `round`, `paths`, and `diagnostic` fields. Exit `0` means completed, `3` means an expected protocol stop, and `2` means invalid input or an unexpected fatal error. A wait remains one bounded in-process call, reports progress periodically on standard error, and emits exactly one final JSON result on standard output. Re-invoked short wait slices are prohibited because they would require a persisted wall-time overall deadline instead of the approved monotonic deadline.
- `bin/review_exchange.bat` follows `prompt_workflow.bat`'s self-locating llm-shared-venv pattern without project activation.
- `instructions/review-requestor.md` explains when and how an LLM supplies authored content and identity-bearing summaries; it does not duplicate the state table.
- Provider-specific Markdown contains only discovery metadata and a direct canonical redirect.

**Completion criteria**:

- `ghog single tests/unit/tools/test_review_exchange_cli tests/unit/tools/test_review_requestor_instruction tests/unit/tools/test_instruction_structure` passes.
- `rg -n "ReviewExchangeCore|review_exchange.bat" instructions/review-requestor.md tools/review_exchange_cli.py` confirms delegation.
- Adapter-copy checks find no canonical body under `.agent/` or `.agents/`.
- `ghog day` reports `exit=0`.

#### Step 4 -- addendums for reusable surfaces

Line-budget checkpoint:

- `tools/review_exchange_cli.py`: baseline 0; below-550 safe; ceiling 650; advisory estimate 260–380 lines.
- Each new CLI/instruction Python test and initializer: baseline 0; below-550 safe; ceiling 650; advisory test estimate below 500.
- Launcher, instruction, adapters, and templates: baseline 0; not subject to the Python ceiling; adapters must remain thin.

Split guidance:

- If CLI parsing exceeds 650, extract result rendering to `tools/review_exchange_cli_output.py`; do not move lifecycle logic into the CLI.

Full workflow timing run readiness:

- Focused CLI and instruction tests, then `ghog day`.

Time-gated status for Step 4:

- No perf gate; CLI tests inject the core and do not wait in real time.

### Step 5. Integrated acceptance and rollout verification

#### Step 5 -- analysis and intent for end-to-end proof

Issues to address:

- Unit-level safety does not prove that real Git ignore checks, exact files, separate processes, and crash recovery compose correctly.
- Both artifact families and both human outcomes must work without implementing the later specialized roles.

Fix intent:

- Exercise the public CLI against temporary Git repositories with real files and subprocess boundaries.
- Cover the highest-risk recovery, escalation, convergence, and identity-isolation journeys.

Expected outcome:

- The core satisfies every acceptance criterion and leaves later umbrella items only their specialized behavior.
- Rollout remains opt-in and inert when `a.review-mode` is absent.

Step framing:

- Design links: Acceptance cases; target behavior; adapter boundary.
- Execution checklist: shared checklist above.

#### Step 5 -- implementation for end-to-end proof

**Files involved**:

- `tests/unit/tools/test_review_exchange_acceptance/__init__.py` (new, to be created).
- `tests/unit/tools/test_review_exchange_acceptance/test_review_exchange_acceptance_tdd.py` (new, to be created).

**Tests first**:

- Run specification and code-family multi-round exchanges in temporary Git repositories, including `code.code` coordination and sibling transcripts.
- Verify absent marker inertness, effective-ignore refusal, concurrent different identities, same-document exclusion, and exact-wait isolation.
- Interrupt request publication, answer publication, transcript append including a torn partial write, answer consumption, escalation append, and owning action completion; verify deterministic repair or preserved escalation.
- Verify a long bounded wait emits multiple standard-error progress diagnostics but only one final standard-output JSON result and uses one monotonic deadline.
- Verify intermediate automation, no-progress and clarification stops, convergence answer retention, cross-session gate re-presentation, another-round guidance, and continuing-authorization replay without a second human question.
- Verify archives, local-offset timestamps, transcript order, and fresh-round resumption after human resolution.

**Classes and behavior**:

- The acceptance suite invokes only the public CLI/core boundary and inspects observable artifacts and results.
- Temporary repositories configure an effective ignore rule explicitly and never depend on the llm-shared working tree's ambient state.

**Completion criteria**:

- `ghog single tests/unit/tools/test_review_exchange_acceptance` passes.
- All feature-request acceptance criteria and design acceptance cases have a named acceptance or focused unit test.
- `rg -n "sleep\(|rglob|iterdir" tools/review_exchange_*.py` finds no real-time test dependency or normal-path tree scan.
- `ghog day` reports `exit=0` with the repository coverage gate satisfied.

#### Step 5 -- addendums for end-to-end proof

Line-budget checkpoint:

- Acceptance initializer and test: baseline 0; below-550 safe; ceiling 650; advisory test estimate 480–600 lines.

Split guidance:

- If acceptance coverage exceeds 650, keep the main exchange journey in this leaf and extract recovery journeys into `tests/unit/tools/test_review_exchange_recovery_acceptance/test_review_exchange_recovery_acceptance_tdd.py` with its own initializer.

Full workflow timing run readiness:

- Acceptance suite, then the final `ghog day` objective.

Time-gated status for Step 5:

- No real bounded wait is allowed in tests; injected clocks and subprocess completion limits keep the suite deterministic.

## Implementation decisions for v0.11.0 review-exchange-core

| Question | Accepted implementation | Arguments | Integrated in | Rejected alternatives |
| --- | --- | --- | --- | --- |
| Q01 | Pass substantive Markdown through exact UTF-8 caller-owned files under effectively ignored project-root `a.*` paths. | This avoids quoting and command-length defects while preventing substantive feedback from becoming commit-visible; the CLI never deletes caller-owned input. | Step 4 CLI tests and behavior | Standard input; command-line Markdown options |
| Q02 | Use standard-library `msvcrt.locking` on Windows and `fcntl.flock` elsewhere against the identity-specific ignored transition-lock path. | Operating-system ownership is released on process exit without another dependency or stale lock-file protocol. | Step 2 store behavior and activation coverage | Third-party lock dependency; exclusive-created lock file |
| Q03 | Persist the pre-append transcript byte offset and target entry identity, finish entries with a reserved stable footer, and truncate a torn suffix before deterministic re-append. | This distinguishes no append, torn append, and complete append without scanning transcript history or adding another mutable artifact. | Steps 2, 3, and 5; validation IO and expectations | Fixed 4 KiB footer search; full transcript scan; separate entry index |
| Q04 | Validate and persist an immutable `FamilyPolicy` at exchange start. | Every resumed process uses the same convergence signal and two label-to-outcome mappings while the core remains role-neutral. | Step 1 models and Step 3 confirmation flow | Hard-coded family vocabulary; rediscover policy on every operation |
| Q05 | Emit exactly one final JSON result, use exit codes `0`, `3`, and `2`, and send periodic in-process wait progress only to standard error. | Callers receive a stable success/expected-stop/fatal shell contract and precise JSON state without replacing the monotonic wait with wall-time host slices. | Steps 3, 4, and 5 | One exit code per state; prose-only zero-exit output |
