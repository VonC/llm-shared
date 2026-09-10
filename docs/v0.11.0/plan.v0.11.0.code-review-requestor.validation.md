# v0.11.0 code-review-requestor implementation tracking and validation

Yes, it is implemented.

All four steps are validated. The implementation review requestor is opt-in,
bounded, resumable, and guarded by durable human commit authority.

## File-based IO cost clarification for v0.11.0 code-review-requestor (implementation)

- Resolve one exact plan and implementation step.
- Use constant exact-path exchange operations and atomic writes.
- Never scan documentation directories or reread transcripts as working context.
- Read current staged evidence once per answer assessment.

## Complexity bound clarification for v0.11.0 (implementation)

- **O(1) per routing or exchange operation** on one exact context.
- **O(n) per authored input or staged diff**.
- No new `O(n log n)` or `O(n^2)` response path.

## Step 1. Add paired code-review request rendering

### Analysis of Step 1 implementation state

Yes. Step 1 has been fully implemented.

The exact code-family plan, step, round, umbrella, authored inputs, request content, and transcript summary now share one validated rendering path. The focused suite, repository checks, all 1,641 tests, coverage gate, and duration gate pass.

### Goal for Step 1

Add validated paired request and transcript-summary rendering for exact code-review rounds.

### Step 1 improvement expectations

- Exact plan, step, round, and umbrella identity.
- Separate ignored authored inputs and paired UTF-8 outputs.
- Code-review-specific instructions without transcript boilerplate leakage.

### What was implemented for Step 1

- Added a pure code-review renderer that derives fixed `code` identity from an exact plan and implementation step.
- Added a canonical request template covering implementation-check evidence, staged repairs, repaired-path reporting, `a.commit` assessment, and advisory commit readiness.
- Added a self-locating launcher and an exact ignored UTF-8 CLI boundary with one read per authored input and one write per paired output.
- Added focused unit coverage for valid rendering, optional guidance, invalid identity, malformed input, unsafe paths, Git-ignore failures, template failures, and envelope mismatches.
- Moved expensive setup for two duration-gated tests into fixtures while keeping real Git setup and all assertions.

### New types or classes introduced for Step 1

- `CodeReviewRoundInput`: frozen, validated identity and authored input for one code-review round.
- `CodeReviewRequestRender`: frozen paired request-content and substantive-summary result.
- `_ArgumentParser`: CLI adapter that converts argument errors to the renderer's stable failure contract.

### Architecture check for Step 1

Rendering remains a deterministic transformation over immutable inputs. Git and filesystem concerns stay at the command adapter boundary, while the launcher contains no business rules. Shared exchange models and envelope validation are reused without importing requestor coordination or persistence responsibilities. No DDD-Hexagonal violation or layer inversion is present.

No architecture issue needs to be addressed.

### Performance check for Step 1

The renderer performs constant exact-path validation, linear template substitution, and one linear read or write per caller-owned file. It adds no directory scan, transcript reread, sorting, nested input traversal, `O(n log n)`, or `O(n^2)` path. The renderer is 382 lines against the step's advisory 280-380 band, and its tests are 437 lines against the advisory 300-430 band. Both exceed their advisory upper bound by a small margin and both stay far below the 650-line ceiling, so the shared execution checklist records the variance as evidence rather than missing work. No split is required: the module keeps one responsibility, and the step's split guidance reserves the `code_review_request_cli.py` extraction for a renderer approaching the ceiling. Groundhog's duration gate passes after two setup-heavy calls were reduced below the one-second call floor.

No performance issue needs to be addressed.

### Unit test coverage check for Step 1

The focused `tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py` package covers the complete `tools/code_review_request.py` module, including defensive error paths. The repository full run reports 100% coverage. This repository does not use the `src/<package>/tests/unit` layout named by the generic instruction; the colocated unit-test convention is followed here.

No unit-tested class below 100% needs completing.

### Feature integrity for Step 1

Existing specification rendering and exchange behavior are unchanged. The new launcher and files are additive, all 1,641 tests pass, and the duration fixes preserve real Git setup and every assertion while moving setup outside measured call time. No existing feature or reporting capability is impaired.

## Step 2. Add the specialized code-review requestor role

### Analysis of Step 2 implementation state

Yes. Step 2 has been fully implemented.

The canonical code-review requestor role now fixes the code-family policy, delegates the shared exchange lifecycle, assesses staged repairs and commit grouping, and exposes redirect-only adapters for every supported host. Its focused contract suite and the full repository gate pass.

### Goal for Step 2

Add the canonical specialized requestor instruction and redirect-only adapters over shared coordination.

### Step 2 improvement expectations

- Fixed code-review family policy and exact state handling.
- Staged-repair, disagreement, convergence, and authorization assessment rules.
- Thin canonical redirects for every supported host.

### What was implemented for Step 2

- Added `instructions/code-review-requestor.md` with the fixed `code` / `commit-ready` policy, exact plan-step identity, complete exchange-state routing, paired request rendering, exact answer-path consumption, repair and `a.commit` assessment, convergence handling, and durable commit continuation.
- Added workflow, Codex instruction, Codex skill, and Claude skill adapters that redirect directly to the canonical role without copying lifecycle policy.
- Added token-and-order contract tests for the role plus structural tests proving adapter metadata and direct canonical redirects.

### New types or classes introduced for Step 2

No production types or classes were introduced. Step 2 adds Markdown role contracts and their structural tests only.

### Architecture check for Step 2

The canonical instruction owns only code-review-specific policy and delegates all coordination transitions to `instructions/review-requestor.md`, request construction to `bin/code_review_request.bat`, and exchange commands to `bin/review_exchange.bat`. Each host adapter is a direct redirect, so policy is not duplicated across integration surfaces. This preserves the intended ports-and-adapters boundary and introduces no cross-layer dependency or misplaced behavior.

No architecture issue needs to be addressed.

### Performance check for Step 2

The implementation is static Markdown with constant-path redirects and no new runtime computation, traversal, or I/O loop. The two test modules are 151 and 107 lines respectively, below the repository ceiling; they are also below their advisory bands, which reflects concise token/order and redirect assertions rather than omitted coverage.

No performance issue needs to be addressed.

### Unit test coverage check for Step 2

Thirteen focused instruction and adapter tests pass. They verify required tokens and their ordering rather than pinning full prose, and they prove every adapter contains the required metadata plus a direct canonical redirect without copied lifecycle logic. Step 2 introduces no production class file requiring a class-specific unit coverage target. The full repository walk also completed with 100% coverage, zero failures, warnings, outliers, or exclusions.

No unit-tested class is below 100% or needs completing.

### Feature integrity for Step 2

Existing shared requestor behavior remains canonical and unchanged; the new role narrows policy through delegation instead of modifying shared transitions. The complete repository gate reports `exit=0`, so no existing feature or reporting capability is impaired.

## Step 3. Integrate commit-gate activation and durable pw routing

### Analysis of Step 3 implementation state

Yes. Step 3 has been fully implemented.

The post-grouping marker sample, exact plan-step handoff, durable exchange
routing, and authorized commit continuation are implemented and validated.

### Goal for Step 3

Connect post-grouping activation, explicit step transport, live exchange routing, and authorized commit continuation.

### Step 3 improvement expectations

- Marker absence preserves the existing gate.
- Marker presence yields a self-contained plan-and-step requestor command.
- Durable commit authorization executes existing commit mechanics once without another choice.

### What was implemented for Step 3

- Added an exact-path code-review routing adapter with the settled family
  policy, marker-gated cold entry, live-state precedence, and fail-closed
  identity validation.
- Added step-aware command rendering using a literal space followed by the
  `step <id>` suffix
  while preserving ordinary rendering byte-for-byte.
- Integrated the specialized requestor route and `code-review-commit` command
  into `pw`, delegating successful authorization to the existing strict batch
  commit boundary and retaining pending authorization after failure.
- Updated implementation and grouping instructions so the marker is sampled
  after grouping and the printed requestor command is run verbatim.
- Added focused routing, rendering, CLI, continuation, and instruction contract
  tests, plus duration-only fixture-boundary repairs required by Groundhog.

### New types or classes introduced for Step 3

- `CodeReviewRoute` is an immutable value carrying one exact review context and
  its observed artifact state.
- `CodeReviewRoutingError` reports absent or inconsistent specialized routes.

### Architecture check for Step 3

The new module is a focused workflow adapter: it derives one fixed context,
delegates protocol state to `ReviewExchangeCore`, rendering to the shared
renderer, and side effects to the existing batch-commit subprocess boundary.
That boundary resolves `gcba.bat` from `steps.llm_shared_dir()` while retaining
the reviewed project as its working directory, so root, submodule, and sibling
llm-shared deployments execute the same installed launcher against the correct
staged tree.
The skill and CLI layers remain thin and do not absorb exchange-domain logic.
No architecture issue needs to be addressed.

### Performance check for Step 3

Routing examines only the derived request, answer, coordination, tombstone, and
lock paths, so it is constant with repository size and performs no directory or
transcript scan. Production files remain within their advisory bands: the
router is 246 lines, renderer 57, skill router 583, and CLI 579. The focused
routing test is 383 lines, three lines above its 260–380 advisory band, because
it keeps all route, continuation, and external-boundary cases together; the
instruction integration test is 48 lines, below its 120–200 band because token
and ordering assertions cover the contract concisely. All remain below the
hard 650-line ceiling. No performance issue needs to be addressed.

### Unit test coverage check for Step 3

The dedicated router suite covers disabled, cold, live, inconsistent,
mismatched-step, rendering, authorization, subprocess-success, and
subprocess-failure paths. Skill rendering and CLI suites cover the new routing
and command surfaces, and the instruction integration test pins required tokens
and ordering. Groundhog completed 1,671 tests with 100% coverage, no failures,
warnings, xfails, or duration outliers. No unit-tested class below 100% needs
completing.

### Feature integrity for Step 3

Marker absence keeps ordinary workflow routing unchanged, while durable exact
exchange evidence remains resumable after marker removal. The full repository
gate reports `state=done exit=0`, so no existing feature or reporting capability
is impaired.

## Step 4. Prove the full code-review requestor workflow

### Analysis of Step 4 implementation state

Yes. Step 4 has been fully implemented.

Repository-level acceptance coverage now proves the complete requestor
lifecycle, its bounded repair paths, exact IO constraints, human gate, and
single authorized commit continuation.

### Goal for Step 4

Validate the complete opt-in requestor lifecycle, bounded repair paths, human gate, and single authorized commit.

### Step 4 improvement expectations

- Public-launcher acceptance coverage for normal, recovery, and failure paths.
- Constant exact-path IO with no transcript or directory scans.
- Full repository gate and coverage objective passing.

### What was implemented for Step 4

- Added a test-local code-answer builder that emits strict code-family envelopes
  for the exact plan, step, round, umbrella, disposition, repaired paths, and
  recommendation without pulling forward the deferred reviewer renderer.
- Added lifecycle acceptance journeys for opt-in routing, step transport,
  staged repair inventory, `a.commit` assessment, substantive re-review,
  explicit disagreement, polishing convergence, human override, reclaim,
  durable Commit replay, one batch execution, and cleanup.
- Added IO and failure acceptance for plan, step, round, and umbrella mismatch;
  tracked scratch inputs; unrelated staged paths; duplicate exchanges;
  escalation; directory scans; and transcript reads.
- Moved real Git setup for duration-gated acceptance and legacy preview tests
  into fixtures while retaining every behavioral assertion.

### New types or classes introduced for Step 4

- `CodeAnswer` is an immutable test value carrying one complete deferred
  reviewer answer and its substantive transcript summary.
- `Effort` is an immutable acceptance fixture value carrying one temporary
  reviewed project, workflow state, memory, and exact review context.

### Architecture check for Step 4

The new code is test-only and composes public production ports: the specialized
renderer and router, shared exchange core and store, Git staging boundary, and
the injected final batch subprocess seam. Reviewer simulation is isolated in a
test-local builder rather than leaking deferred reviewer behavior into
production. No architecture issue needs to be addressed.

### Performance check for Step 4

Acceptance routing asserts fixed-path behavior and fails any documentation-tree
scan or versioned-transcript read. Each journey operates on one exact context;
staged inventory is linear in staged paths, with no new `O(n log n)` or
`O(n^2)` work. The builder is 76 lines, lifecycle suite 426, and IO suite 254;
the builder is below its 150–260 advisory band because shared envelope rendering
keeps it compact, while both suites remain within their advisory bands and all
files are below 650. No performance issue needs to be addressed.

### Unit test coverage check for Step 4

Ten focused acceptance tests cover all planned normal, recovery, convergence,
authorization, and failure surfaces. Groundhog completed 1,681 tests with 100%
coverage, no failures, warnings, xfails, or duration outliers. The new builder
is exercised through every answer-publication journey. No unit-tested class
below 100% needs completing.

### Feature integrity for Step 4

Marker-off behavior retains the ordinary gate; marker-on and live-state paths
carry exact identity; invalid inputs fail closed; and only durable `Commit`
authority reaches the existing batch continuation once. The full repository
gate reports `state=done exit=0`, so no existing feature or reporting capability
is impaired.
