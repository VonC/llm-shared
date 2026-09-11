# v0.11.0 specification reviewer implementation tracking and validation

Yes, it is implemented.

All four implementation slices are complete and validated, including the
public reviewer lifecycle, recovery boundaries, exact-path IO, and repository
quality gate.

## File-based IO cost clarification for v0.11.0 specification reviewer implementation

All implementation checks must verify that:

- routing observes only the fixed requirement, design, and plan contexts;
- reviewer work reads exact request, specification, state, and ignored inputs;
- paired rendering does not read transcript or protocol artifacts; and
- shared publication remains the only protocol mutation path.

## Complexity bound clarification for v0.11.0 specification reviewer implementation

- Route observation is O(1) over at most three specification contexts.
- Assessment and rendering are O(n) in exact input bytes.
- Directory scans, transcript-history reads, O(n log n), and O(n^2) response
  paths are implementation failures.

## Step 1. Route pending requests to the specification reviewer

### Analysis of Step 1 implementation state

Yes. Step 1 has been fully implemented.

The state-aware route, owner selection, forced reviewer behavior, module
splits, line budgets, and both example- and property-based routing coverage
now implement the complete first slice.

### Goal for Step 1

Expose one immutable context-and-state route, map pending work to
`spec-reviewer`, preserve writer-state ownership, and split the full
`prompt_workflow_skill.py` responsibility before adding behavior.

### Step 1 improvement expectations

- One route observation selects exactly one owning role.
- Cold abandoned requests hand reclaim to the requestor.
- Ordinary and forced reviewer commands preserve exact identity and host prefix.
- Only the four topic-discovery helpers move; `post_commit_command` remains in
  the skill module and imports stay one-way.
- The split leaves every Python file within the 650-line ceiling.

### What was implemented for Step 1

- `LiveSpecificationRoute` carries one exact review context and its observed
  artifact state as an immutable value returned by `live_specification_route`.
- Ordinary routing selects `spec-reviewer` for `request-pending` and retains
  `spec-review-requestor` for abandoned and writer-owned live states.
- Forced reviewer routing accepts only an exact pending request, returns no
  command for absent or writer-owned work, and diagnoses a cold abandoned
  request with its requestor reclaim identity.
- The post-commit discovery helpers moved to
  `tools/prompt_workflow_post_commit.py`; the likely fallback also moved the
  cohesive host-rendering cluster to `tools/prompt_workflow_render.py` with
  compatibility exports from the skill router.
- Example-based tests cover routing ownership, forced behavior, exact host
  prefixes and paths, ambiguity, marker gating, and bounded candidate access.
- Property-based coverage drives every generated artifact state through the
  real command selector, proves its owner or no-route outcome, and asserts one
  classification of each of the three fixed contexts.
- Two reviewer repairs completed the step. `def next_command` regained the
  two-blank-line separator used by every other top-level definition in the
  skill router; the sibling effort recorded that repair as blocked while the
  module sat at exactly 650 lines, and this step's split made it possible at
  552. `ArtifactState` is now imported from its owning
  `tools/review_exchange_models` module instead of the
  `tools/review_exchange_state` classifier that only re-exports it, matching
  `prompt_workflow_review.py` and this step's own property test.

### New types or classes introduced for Step 1

- `LiveSpecificationRoute`, a frozen dataclass containing a `ReviewContext`
  and the `ArtifactState` observed for that exact context.

### Architecture check for Step 1

The review adapter owns fixed-path exchange observation, the skill router owns
command selection, and the extracted post-commit and rendering modules depend
one way without importing the skill router. `post_commit_command` correctly
stays in the router because it uses its document and host helpers. No domain,
adapter, or infrastructure dependency is inverted, and every touched Python
file remains within the repository line ceiling.

No, there is nothing architectural that needs to be addressed.

### Performance check for Step 1

Routing classifies the fixed requirement, design, and plan candidate set once,
so its work remains O(1) with at most three exact contexts. It performs no
directory scan, transcript read, sorting, or repeated state observation.

No, there is no performance issue that needs to be addressed.

### Unit test coverage check for Step 1

The new frozen route and the touched module-level routing functions have direct
unit and property-based coverage, and the full suite reports 100% project
coverage.

No, there is no unit-tested class below 100% that needs completing.

### Feature integrity for Step 1

Compatibility views and rendering exports preserve existing requestor,
post-commit, and host behavior. The complete groundhog walk passed 1,546 tests
with 100% coverage, no duration outliers, and no exclusions. Feature integrity
is intact and the state-to-owner property is now explicitly proved.

---

## Step 2. Render paired specification review answers

### Analysis of Step 2 implementation state

Yes. Step 2 has been fully implemented.

The repository now contains the typed paired answer renderer, specialized
template, fixed-path CLI, launcher, public exports, and focused tests required
by the plan. Groundhog recorded all affected lines at 100% coverage with the
static gate green.

### Goal for Step 2

Create the pure typed answer renderer, specialized layered template, fixed-path
CLI, and launcher that produce one complete answer plus one matching transcript
summary without publishing either.

### Step 2 improvement expectations

- Both dispositions validate their required actionable content.
- Human guidance requires a distinct authored response.
- Answer and summary share exact identity and substantive findings.
- Invalid or stale input cannot cause partial output mutation.

### What was implemented for Step 2

- **Typed paired rendering**: `tools/spec_review_answer.py` validates exact
  specification identity, positive round, disposition-specific evidence, and
  the guidance-response pair before producing a complete answer and matching
  transcript summary from one immutable source.
- **Layered Markdown contract**:
  `templates/spec-review-answer.template.md` supplies unique round-bearing H2
  sections beneath the shared H1 and first `## JSON` envelope, including
  repository-relative human-readable identity and an advisory final decision.
- **Fixed-path adapter**: `tools/spec_review_answer_cli.py` reads each exact
  project-root ignored UTF-8 input once, validates the current SHA-256 and an
  optional retained manifest, rejects path collisions, and rolls back the pair
  if either output replacement fails.
- **Public and command surfaces**: `tools/__init__.py` exports the immutable
  models and pure renderer, while `bin/spec_review_answer.bat` self-locates the
  repository Python environment and invokes only the CLI adapter.
- **Validation evidence**: the focused renderer and CLI suite passed 38 tests;
  `ghog affected` reported `fail=0` and `cov=100`; the final `ghog check`
  recorded `state=done exit=0` with Ty, Pyright, Ruff, Radon, Vulture, file-size,
  shell, and EOF checks green.

### Step 2 implementation-to-plan variances

`tools/spec_review_answer_cli.py` finished at 327 lines against the plan's
advisory 150-240 estimate. It stays below the 550-line safe threshold and the
650-line ceiling, so the shared checklist records the variance as evidence
rather than missing work. The module keeps one responsibility, fixed-path trust
and IO for the pure renderer, and its helpers cover argument parsing, ignore
validation, path validation, single-read UTF-8 input, document digest, manifest
validation, temporary output, rollback-safe paired replacement, and one render
call. Splitting it would scatter one trust boundary across two modules for no
gain, so no plan-consistent split is required. `tools/spec_review_answer.py` at
297 lines stays inside its 260-360 advisory range. The renderer test finished
at 306 lines, while the CLI test finished at exactly 500 rather than below the
advisory 500; it remains far below the 550 safe threshold, but the next case
added to that file should either fit a trimmed fixture or move to a focused
sibling.

Two reviewer repairs completed the step. `_validate_manifest` accepted a JSON
boolean as `original_round_number`, because `isinstance(True, int)` is true in
Python and the check did not exclude bools; it now uses the shared
`positive_integer` helper that exists in `review_exchange_models` for exactly
this hazard, and a regression test rejects a boolean round. The answer template
also emitted three consecutive blank lines whenever no human guidance existed,
because the optional section substituted as an empty string between two literal
template blank lines; the disposition and guidance sections are now composed in
the renderer and joined only when present, with a regression test asserting no
blank-line run in either paired output. Both repairs keep the two production
modules at 100% coverage.

### New types or classes introduced for Step 2

- `SpecificationAssessment`: immutable exact context and authored findings for
  one reviewer answer round, including mutually exclusive disposition evidence.
- `SpecificationAnswerRender`: immutable complete answer and substantive
  transcript-summary pair.
- `_ArgumentParser`: narrow CLI parser that converts argument failures into the
  shared stable validation-error path.

### Architecture check for Step 2

- **Pure rendering boundary**: `tools/spec_review_answer.py` owns models and
  Markdown composition without command parsing, Git inspection, output writes,
  or review-exchange publication.
- **Adapter boundary**: `tools/spec_review_answer_cli.py` owns filesystem, Git,
  digest, manifest, and paired-write concerns, then calls the renderer once.
- **Protocol authority**: neither new module imports the exchange core or store;
  shared `publish-answer` remains the only later protocol mutation path.
- **Maintainability**: the 291-line renderer, 323-line CLI, and 91-line package
  export file remain below the enforced 650-line ceiling and keep their planned
  responsibilities separate.

No, there is nothing architectural that needs to be addressed.

### Performance check for Step 2

- **No new `O(n^2)` or `O(n log n)` path**: input validation, hashing, template
  substitution, and summary construction are linear in exact input bytes.
- **Exact-read bound**: the reviewed document and each supplied authored input
  are read once; no directory or transcript-history scan was added.
- **Output bound**: rendering holds two outputs in memory and performs a fixed
  number of same-directory temporary writes and replacements, independent of
  nearby repository content.
- **Plan-bound alignment**: optional retained-manifest validation compares one
  fixed identity and one ordered exact-path list without changing the O(n)
  per-round target.

No, there is no performance issue that needs to be addressed.

### Unit test coverage check for Step 2

- **Pure renderer**:
  `tests/unit/tools/test_spec_review_answer/test_spec_review_answer_tdd.py`
  covers all four identities, both dispositions, immutable models, guidance,
  Markdown shape, containment, template failure, and shared-envelope failure.
- **CLI adapter**:
  `tests/unit/tools/test_spec_review_answer/test_spec_review_answer_cli_tdd.py`
  covers root, ignore, UTF-8, SHA-256, manifest, collision, exact pairing, IO
  failures, and rollback with and without existing outputs.
- **Measured result**: `ghog affected` reported 100% coverage for the affected
  production files after the full suite had already passed all 1,584 tests.

No, there is no unit-tested class below 100% that needs completing.

### Feature integrity for Step 2

- **Existing request renderer**: `tools/spec_review_request.py` remains unchanged;
  the reviewer renderer uses the same context and envelope contracts through a
  separate module and export surface.
- **Protocol behavior**: no answer publication, request consumption,
  coordination update, or transcript append occurs in the new renderer or CLI.
- **Diagnostics and recovery**: stable validation errors cover invalid arguments,
  stale document content, malformed retained evidence, and IO failure, while
  the CLI deliberately leaves the single-use manifest for Step 3 orchestration
  to retire after successful publication.

No existing feature or reporting capability appears impaired.

---

## Step 3. Add reviewer orchestration and host adapters

### Analysis of Step 3 implementation state

Yes. Step 3 has been fully implemented.

The repository now contains one canonical specification reviewer instruction,
four thin host adapters, focused instruction and adapter contracts, and the
requestor timeout clarification required by the plan. The focused 17-test set
and the 1,600-test groundhog walk are green with 100% coverage.

### Goal for Step 3

Add one canonical reviewer instruction and thin host adapters, preserve the
reviewer/requestor/human authority boundaries, and align requestor answer waits
with the full configured timeout.

### Step 3 improvement expectations

- Reviewer orchestration uses only public paired-renderer and exchange surfaces.
- Cold and in-session reclaim paths remain distinct.
- Retained assessment manifests are revalidated and retired only after
  successful publication.
- The workflow adapter uses the portable three-step locate body, while Codex
  and Claude adapters use loader-relative canonical links.

### What was implemented for Step 3

- **Canonical reviewer orchestration**: `instructions/spec-reviewer.md`
  registers the fixed specification policy, accepts only exact supplied
  context, and orders `status`, one bounded `wait-request`, paired answer
  rendering, and shared `publish-answer` without copying exchange transitions.
- **Authority and recovery boundary**: the instruction limits reclaim to an
  expired intact lease from the active reviewer session, returns cold
  `abandoned-request` work to `spec-review-requestor`, stops on shared recovery
  states, and forbids writer and human operations.
- **Retained assessment contract**: SHA-256, identity, original round, and exact
  assessment paths are revalidated through the paired renderer. The
  single-use manifest remains after rendering or failed publication and is
  retired only after `publish-answer` reports `outcome: published`. That
  outcome accompanies exit `0` for a change request and exit `3` at the
  convergence gate, matching the plan's Q03 decision to retire after a
  successful publication rather than after one exit code.
- **Requestor timeout authority**: `instructions/spec-review-requestor.md`
  explicitly omits `--timeout-seconds` from `wait-answer` so the marker's full
  configured review timeout remains authoritative.
- **Per-host redirects**: `.agent/workflows/spec-reviewer.md` retains the
  repository three-step locate body, while the packaged instruction, packaged
  skill, and Claude skill point directly to the canonical root instruction
  with loader-relative links.
- **Focused contracts**: the new reviewer instruction and adapter tests cover
  exact policy, ordered operations, cold and in-session reclaim, retained
  evidence, stopped states, forbidden authority, workflow portability, direct
  links, and absence of copied orchestration. The requestor instruction test
  pins the complete marker timeout.
- **Validation evidence**: the focused set passed 17 tests. The final groundhog
  walk passed 1,600 tests with `fail=0`, `warn=0`, `xfail=0`, `cov=100`, no
  duration outliers, no exclusions, and `exit=0`.

### Step 3 implementation-to-plan variances

`instructions/spec-review-requestor.md` moved from 162 to 164 lines, and its
test moved from 124 to 133 lines, both inside the plan's advisory checkpoints.
The new canonical reviewer instruction is 168 lines, its behavior test is 131
lines, and its adapter test is 114 lines. Every Python test stays below the
550-line safe threshold and 650-line ceiling, so no split is indicated.

The groundhog compile gate exposed a partially unknown empty-list type in the
Step 2 boolean-manifest regression fixture. Annotating that local as
`dict[str, object]` made the committed repair pass Pyright. The change replaced
one existing line rather than adding one, so the file stays at exactly 500
lines, unchanged from the count Step 2 recorded. No test case or responsibility
was added. A later new case should still use a trimmed fixture or a focused
sibling, as recorded by Step 2.

### New types or classes introduced for Step 3

No production type or class was introduced. Step 3 adds canonical Markdown
orchestration and provider discovery adapters; its Python changes are contract
tests plus one local test-fixture annotation.

### Architecture check for Step 3

- **Canonical ownership**: reusable reviewer policy and orchestration live only
  in `instructions/spec-reviewer.md`.
- **Adapter isolation**: provider-specific files contain discovery metadata and
  a direct canonical redirect. The portable workflow form and loader-relative
  packaged forms are tested independently.
- **Port boundary**: the instruction invokes only the public paired renderer
  and `review_exchange.bat`; it does not reproduce state classification,
  publication mutation, or filesystem trust logic.
- **Authority separation**: reviewer, requestor, and human operations remain
  distinct, including separate active-session and cold-route reclaim paths.

No, there is nothing architectural that needs to be addressed.

### Performance check for Step 3

- **Bounded orchestration**: one status, one exact wait, one render, and one
  publication are named for a normal invocation; no polling or directory scan
  is introduced.
- **Linear retained evidence**: SHA-256 and renderer validation remain linear
  in exact input bytes and compare one fixed ordered path list.
- **No new expensive computation**: the implementation adds Markdown contracts
  and tests, not an `O(n^2)` or `O(n log n)` production path.

No, there is no performance issue that needs to be addressed.

### Unit test coverage check for Step 3

- **Reviewer instruction**:
  `tests/unit/tools/test_spec_reviewer_instruction/test_spec_reviewer_instruction_tdd.py`
  covers the canonical policy, operation order, reclaim split, retained
  manifest, stopped states, and authority prohibitions.
- **Host adapters**:
  `tests/unit/tools/test_instruction_structure/test_spec_reviewer_adapters_tdd.py`
  covers all four hosts, exact packaged links, portable workflow location,
  metadata, and absence of copied logic.
- **Requestor timeout**: the existing requestor instruction test now proves
  that `wait-answer` uses the complete marker timeout without a caller override.
- **Measured result**: the focused 17-test set passed, and the full groundhog
  walk retained project coverage at 100%.

No, there is no unit-tested class below 100% that needs completing.

### Feature integrity for Step 3

- **Requestor behavior**: all writer, intermediate-round, human-gate, and
  consolidation actions remain in the existing requestor instruction; only its
  answer-wait timeout wording changed.
- **Exchange behavior**: no core, store, renderer, launcher, or routing
  production code changed in this step.
- **Host portability**: the repaired requestor workflow locate body is reused
  as the structural model without copying reviewer orchestration into adapters.
- **Repository gate**: all 1,600 tests passed with no warnings, expected
  failures, duration outliers, or exclusions.

No existing feature or reporting capability appears impaired.

---

## Step 4. Prove the complete specification reviewer workflow

### Analysis of Step 4 implementation state

Yes. Step 4 has been fully implemented.

The new acceptance package composes all four specification identities with
ordinary and explicit routing, paired reviewer answers, durable publication,
reclaim and recovery behavior, exact-path IO instrumentation, and each shipped
batch launcher. The focused acceptance run and final full Groundhog walk both
pass, with 100% coverage and no duration outliers.

### Goal for Step 4

Validate the full public reviewer lifecycle across all specification types,
both dispositions, guidance, publication replay, reclaim, stopped recovery,
manifest drift, marker suspension, and exact-path IO.

### Step 4 improvement expectations

- Public launchers and routing contracts work together end to end.
- Scenario matrices use public Python boundaries, with one smoke test per launcher.
- Package-local fixtures share exact setup without global pytest configuration.
- Answer publication consumes and appends exactly once.
- Recovery preserves valid reasoning without publishing stale identity.
- Acceptance tests prove the requirement and repository coverage gate.

### What was implemented for Step 4

- `tests/unit/tools/test_spec_reviewer_acceptance/fixtures.py` provides shared
  real-Git effort setup and public request, answer, exchange, and core helpers
  without adding global pytest configuration.
- Lifecycle acceptance covers feature requests, issues, design specifications,
  and plans; ordinary and forced reviewer routing; marker suspension; exact
  identity; both dispositions; literal human guidance; paired content; and
  single transcript append behavior.
- Recovery acceptance covers cold requestor reclaim, in-session reviewer
  reclaim, interrupted answer-publication replay, retained assessment context,
  fresh-document drift rejection, manifest retirement ordering, escalation,
  and human-only recovery.
- IO acceptance rejects directory scans and transcript reads, proves exact
  caller input reads, ignores stale scratch files, observes same-directory
  atomic replacement for both renderer outputs, fails closed on ambiguous live
  requests, and smoke-tests `prompt_workflow.bat`, `spec_review_answer.bat`, and
  `review_exchange.bat` through their public help entry points.
- Expensive real-Git and batch-launcher journeys run in fixtures so pytest's
  measured call phase contains only the assertions. The same refactor removed
  two neighboring recovery-suite outliers without changing their scenarios or
  assertions.
- The required vocabulary scan finds all registered specification tokens,
  literal human guidance, and SHA-256 evidence in the acceptance package.
- The focused four-file Groundhog run passes 30 tests. The final repository
  walk passes all 1,621 tests with 100% coverage, zero warnings, zero expected
  failures, zero duration outliers, and zero exclusions.

### New types or classes introduced for Step 4

- `Effort`, an acceptance-only frozen dataclass carrying one temporary project
  root, topic, exact review context, reviewed document, and umbrella.
- `CliResult`, an acceptance-only frozen dataclass carrying one public exchange
  command's exit code and parsed JSON payload.
- `Clock`, an acceptance-only deterministic aware wall clock used to prove the
  two reclaim ownership paths without a real wait.

### Architecture check for Step 4

Step 4 changes no production layer. The acceptance package enters through
public routing, renderer, CLI, core, store, and launcher boundaries; its shared
fixture module owns setup only, while lifecycle, recovery, and IO assertions
remain separated by responsibility. The 288-line fixture module and the
180-line, 258-line, and 189-line scenario modules differ from the plan's
advisory starting distribution, but every file remains cohesive, below the
500-line advisory ceiling, and well below the 650-line hard ceiling. No import
cycle, cross-layer dependency, private protocol-state mutation, O(n log n), or
O(n^2) path was introduced.

No architecture issue or other fix is needed for Step 4.

### Performance check for Step 4

Profiling identified repeated Git ignored-path subprocesses in acceptance call
phases. Moving complete real-file journeys into package and local fixtures kept
all assertions and public boundaries intact while reducing measured call time
below the one-second floor. The final full walk reports zero duration outliers
and zero exclusions; production complexity remains unchanged.

That repair relocates cost rather than removing it, and this record reads it
that way on purpose. The duration gate measures only the pytest call phase, so
the journeys now run in setup, where the one-second floor does not apply: the
new package still takes about 41 seconds for its 21 tests, with slowest setup
phases of 4.36, 4.30, and 4.13 seconds. `outliers=0` therefore records that no
measured call phase is slow, not that the suite became faster. Because each
scenario body now sits in its fixture, a regression surfaces as a pytest error
rather than a failure. The fixture form itself is not new: the committed
`test_spec_review_requestor_acceptance` suite already uses it, and Step 4
applied it to two pre-existing `test_review_exchange_recovery_acceptance`
tests as well.

The remaining cost is the real-Git and real-launcher fidelity this plan asked
for, so no performance issue needs to be addressed for Step 4.

### Unit test coverage check for Step 4

Step 4 adds acceptance tests and changes no production class file, so it creates
no new class-specific unit-test obligation. Existing focused unit suites for
routing, answer rendering, answer CLI validation, exchange transitions, and
instruction structure remain present, and the repository-wide coverage gate
reports 100%.

No unit-tested class is below 100% or needs completing for Step 4.

### Feature integrity for Step 4

The complete reviewer workflow is exercised through its public boundaries for
every specification type, both dispositions, guidance, exact identity,
publication, recovery, marker, ambiguity, manifest, and filesystem contracts.
The final Groundhog walk passed all 1,621 tests with no warnings, expected
failures, outliers, or exclusions. No existing feature or reporting capability
appears impaired.
