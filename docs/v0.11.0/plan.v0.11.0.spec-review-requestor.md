# v0.11.0 specification review requestor implementation plan -- specialized writer orchestration

Implement the specification-writer side of review mode as a thin specialization
over the completed shared exchange.

- **Paired rendering**: generate coherent request content and transcript
  summaries from one validated round input.
- **Single orchestration role**: keep lifecycle commands in one specialized
  requestor with redirect-only host adapters.
- **Durable workflow routing**: resume exact live exchanges before ordinary
  document routing and delegate new-question triggers without duplication.

> Markdown lint note: never leave a space immediately inside an inline code span
> (MD038); when a snippet starts or ends with a space, write that space as the
> literal token `[space]`. End any line that would be only italic text with a
> period after the closing underscore (MD036).

## Plan goal for v0.11.0 specification review requestor

Implement the complete requestor integration described in
`design.v0.11.0.spec-review-requestor.md` and its linked feature request in four
ordered steps.

- **Step 1 goal**: add the validated paired request renderer and launcher.
- **Step 2 goal**: add the specialized orchestration instruction and host
  adapters.
- **Step 3 goal**: connect question workflows and durable `pw` routing.
- **Step 4 goal**: prove the complete opt-in, round, resume, and convergence
  behavior through acceptance tests.

---

## Scope anchors for v0.11.0 specification review requestor plan

This plan implements the consolidated design outcomes:

1. Writers delegate newly placed specification questions only when review mode
   is active and no direct hold applies.
2. One specialized role renders and coordinates every specification request
   while the shared exchange remains the state authority.
3. Exact live exchanges resume across sessions, and only durable human
   authorization permits consolidation.

In scope:

- Feature-request, issue, design-specification, and plan request identities.
- Paired request and transcript-summary generation.
- Canonical specification-requestor instruction plus workflow, Codex, and
  Claude adapters.
- Thin integration references in both existing question workflows.
- `pw` forced delegation and live-exchange precedence for the current effort.
- Focused unit, integration, and acceptance validation.

Deferred:

- Independent `spec-reviewer` behavior and answer generation.
- Implementation-code review requestor and reviewer behavior.
- End-user Diataxis documentation for the complete umbrella.
- Changes to shared exchange persistence, locking, waits, or recovery policy.

---

## Implementation decisions for v0.11.0 specification review requestor

| Question | Decision | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | Pass exact context and round as flags, authored content and optional guidance as ignored UTF-8 input files, and two explicit ignored output paths. | Step 1 tests and types and behavior | One JSON manifest duplicates context validation; standard-input and delimited-output handling makes paired output fragile. |
| Q02 | Fail closed when one topic has multiple live specification exchanges and report every exact identity. | Step 3 tests and behavior | Document-order and newest-lease selection both guess authority. |
| Q03 | After canonical consolidation, use live-exchange precedence to return to the requestor, verify the settled decision marker, complete the exchange, and rerun `pw skill`. | Step 2 and Step 3 behavior | General consolidation must not own exchange completion, and uninterrupted requestor-only consolidation is not replay-safe. |

---

## Complexity bound clarification for v0.11.0 specification review requestor

- **O(1) per render or protocol action**: identity derivation, request
  generation, exact coordination lookup, and state transitions operate on a
  constant set of paths and bounded content inputs.
- **O(n) per authored input**: request and summary rendering scale linearly with
  the supplied feedback and optional guidance text.
- **O(k) routing lookup with constant k**: `pw` checks only the bounded
  requirement, design, and plan candidates already resolved for one effort.

No response path may add a documentation-tree scan, transcript-history load,
or repeated parse of generated Markdown.

## File-based IO cost clarification for v0.11.0 specification review requestor

- Resolve the effort once and inspect only exact document and coordination
  paths.
- Read feedback and optional guidance once into one validated rendering input.
- Write the paired caller-owned outputs once, then publish them through the
  shared atomic exchange operation.
- Never use the sibling transcript as routing or working context.
- Keep reclaim and completion on the existing exact coordination path.

## Step 0 perf-gate decision for v0.11.0 specification review requestor

No separate Step 0 xfail performance gate is needed. The feature adds no new
unbounded model, loop, background worker, or async response path; the shared
exchange already owns exact-path performance gates. Step 3 unit tests will
assert bounded candidate lookup, and Step 4 acceptance tests will reject
directory scans and transcript reads in the specialized flow.

---

## Confirmed technical facts for v0.11.0 plan viability

**Files in the 550-through-650 risk band**:

- `tools/prompt_workflow_skill.py`: 631 lines -- keep specification routing in
  a new focused module and limit this file to a narrow delegation call; do not
  exceed the repository ceiling of 650.
- `tests/unit/tools/test_prompt_workflow_skill/test_prompt_workflow_skill_tdd.py`:
  596 lines -- add specification-routing cases in a new sibling test module.
- `tests/unit/tools/test_prompt_workflow_acceptance/test_prompt_workflow_acceptance_tdd.py`:
  585 lines -- add the new feature acceptance suite in its own package.

**Files below 550 and safe to extend**:

- `tools/__init__.py`: 73 lines -- export only the public specialized render
  value objects if the launcher contract needs them; advisory final count 85.
- `tools/prompt_workflow_steps.py`: 266 lines -- no planned change.
- `instructions/review-ask-questions.md`: 82 lines -- add one bounded review-mode
  delegation block.
- `instructions/consolidate-then-review-ask-questions.md`: 121 lines -- add the
  same delegation boundary after new questions are placed.
- `tests/unit/tools/test_instruction_structure/test_codex_plugin_structure_tdd.py`:
  173 lines -- no growth; adapter checks go in a new sibling test file.
- `tests/unit/tools/test_review_requestor_instruction/test_review_requestor_instruction_tdd.py`:
  56 lines -- preserve shared role-neutral coverage unchanged.

**New files**:

- `tools/spec_review_request.py` and `bin/spec_review_request.bat`.
- `templates/spec-review-request.template.md`.
- `instructions/spec-review-requestor.md` and its host adapters.
- `tools/prompt_workflow_review.py`.
- Focused renderer, instruction, routing, and acceptance test packages.

**Other facts**:

- The shared CLI maps `design.*` to `design-specification` and validates the
  family policy, envelope, human-readable identity, and literal guided-override
  summary.
- `prompt_workflow.py` already accepts an arbitrary forced skill name; the
  applicability and target document are resolved in `prompt_workflow_skill.py`.
- Current host adapters are redirect-only Markdown and must remain so under
  `rules/llm-specific-adapters.md`.
- The existing `a.*` ignore convention covers renderer inputs and transient
  exchange artifacts.

---

## Current test-tree validation snapshot for v0.11.0 specification review requestor

Existing packages to preserve:

- `tests/unit/tools/test_review_exchange_*` -- shared identity, lifecycle,
  storage, wait, recovery, and acceptance coverage; specialized tests reference
  these contracts instead of duplicating core internals.
- `tests/unit/tools/test_prompt_workflow_skill/` -- current routing and rendering
  coverage; its primary file is already in the risk band.
- `tests/unit/tools/test_prompt_workflow_acceptance/` -- existing workflow
  acceptance coverage; its current file is in the risk band.
- `tests/unit/tools/test_instruction_structure/` -- canonical/adaptor structure
  and plan-shape checks.

New leaf packages:

- `tests/unit/tools/test_spec_review_request/`.
- `tests/unit/tools/test_spec_review_requestor_instruction/`.
- `tests/unit/tools/test_prompt_workflow_review/`.
- `tests/unit/tools/test_spec_review_requestor_acceptance/`.

Property-based testing is not added for the specialized renderer: identity,
timestamps, envelopes, and lifecycle transitions already have shared core PBT
coverage, while this feature's finite label and section composition is better
covered by exact example and boundary tests.

## Runtime file note for v0.11.0 specification review requestor plan

- `a.review-requested.<type>.vX.Y.Z.<slug>.md` and matching answer,
  coordination, lock, and tombstone files remain ignored shared runtime state.
- Caller-owned renderer content, summary, and optional guidance inputs use
  ignored root `a.*` names and are removed by the caller after publication.
- `review.<type>.vX.Y.Z.<slug>.md` is the only versioned aggregation artifact.

---

## Shared execution command checklist for all v0.11.0 specification review requestor steps

For each step:

1. Count each step file with `@(Get-Content -LiteralPath <path>).Count`; use `0`
   for a new file.
2. Add or update the step tests before production behavior.
3. Run the step's `ghog single` command.
4. Run the step grep checks.
5. Repeat `ghog day` and fixes until the objective reports `exit=0`.
6. Count every step file again and compare with its line-budget checkpoint.
7. Split any Python file above 650 lines before the step is complete.
8. Record advisory-estimate variance without failing a file that remains at or
   below 650 lines.

## Ready-to-run command templates for all v0.11.0 specification review requestor steps

- Line count: `@(Get-Content -LiteralPath <path>).Count`
- Targeted tests: `ghog single <step test files>`
- Grep checks: `rg --line-number <pattern> <step paths>`
- Shared gate loop: `ghog day`, repeated until `exit=0`
- Final line count: `@(Get-Content -LiteralPath <path>).Count`

---

## Numbered steps for v0.11.0 specification review requestor

### Step 1. Add paired specification request rendering

#### Step 1 -- analysis and intent for paired rendering

Issues to address:

- Specialized request and transcript-summary content has no dedicated validated
  input or renderer.
- Independently authored outputs can disagree or leak fixed conclusion text
  into the transcript.

Fix intent:

- Introduce one immutable round input and paired render result.
- Reuse shared envelope and Markdown validation while keeping specification
  assessment and conclusion wording specialized.
- Preserve literal `Human guidance: <text>` when override guidance exists.

Expected outcome:

- One launcher call produces UTF-8 request-content and transcript-summary files
  with matching round context.
- Design sources map through the core to `design-specification`.

Step framing:

- Design links: Request composition and identity; Q02 and Q05.
- Execution checklist: Shared execution command checklist in this plan.

#### Step 1 -- implementation for paired rendering

**Files involved**:

- `tools/spec_review_request.py` (new, to be created).
- `tools/__init__.py` (existing, to be updated only for public exports).
- `templates/spec-review-request.template.md` (new, to be created).
- `bin/spec_review_request.bat` (new, to be created).
- `tests/unit/tools/test_spec_review_request/__init__.py` (new, to be created).
- `tests/unit/tools/test_spec_review_request/test_spec_review_request_tdd.py`
  (new, to be created).

**Tests first**:

- Cover feature-request, issue, design, and plan inputs, exact umbrella or
  `none`, positive rounds, required H1/JSON/H2 shape, paired identity, and
  exclusion of fixed conclusion boilerplate from the summary.
- Cover invalid paths, unsupported types, wrong rounds, non-root or tracked
  output paths, malformed UTF-8 feedback, and missing input.
- Cover exact context and round flags, separate ignored UTF-8 files for
  assessment, change summary, writer response, and optional guidance, and two
  explicit ignored root output paths.
- Cover guided overrides with the exact `Human guidance:` label plus a separate
  writer response.

**Types and behavior**:

- `SpecificationRoundInput`: exact context, round, authored assessment,
  change summary, and optional human guidance.
- `SpecificationRequestRender`: complete request and substantive summary.
- Renderer CLI: receives exact context and round as flags; reads assessment,
  change summary, writer response, and optional guidance from separate ignored
  UTF-8 root files; validates two explicit ignored root output paths; renders
  and writes both outputs once. Publication remains out of scope.

**Completion criteria**:

- `ghog single tests/unit/tools/test_spec_review_request/test_spec_review_request_tdd.py`
  passes.
- `rg --line-number "Human guidance:|## JSON|Reviewed specification|Review round" tools/spec_review_request.py templates/spec-review-request.template.md`
  finds the specialized contract.
- `ghog day` reports `exit=0`.

#### Step 1 -- addendums for paired rendering

Line-budget checkpoint:

- `tools/spec_review_request.py`: baseline 0; below-550 safe; ceiling 650;
  advisory final count 240-340.
- `tools/__init__.py`: baseline 73; below-550 safe; ceiling 650; advisory final
  count 85.
- `test_spec_review_request_tdd.py`: baseline 0; below-550 safe; ceiling 650;
  advisory final count 300-420.

Split guidance:

- If the renderer approaches 650 lines, extract argument parsing and filesystem
  output validation into `tools/spec_review_request_cli.py`; keep the immutable
  inputs and pure rendering in `tools/spec_review_request.py`.

Full workflow timing run readiness:

- Focused renderer tests; `ghog day`.

Time-gated status for Step 1:

- No new perf gate; linear authored-input rendering and one-write-per-output are
  asserted by focused tests.

---

### Step 2. Add the specialized requestor instruction and adapters

#### Step 2 -- analysis and intent for requestor orchestration

Issues to address:

- The shared requestor instruction is deliberately role-neutral and cannot own
  specification assessment, edits, or consolidation.
- No discoverable specialized role joins the renderer to the shared lifecycle.

Fix intent:

- Add one canonical specialized instruction that registers the fixed family
  policy and delegates every state transition to the shared instruction.
- Add redirect-only workflow, Codex, and Claude adapters.

Expected outcome:

- The role handles disabled, idle, active, answer-pending, abandoned,
  convergence, and owning-action-pending states without manual artifact edits.
- Intermediate changes and convergence wording are owned by the writer.

Step framing:

- Design links: Activation and role boundaries; Repeated rounds and
  convergence; Q03 and Q04.
- Execution checklist: Shared execution command checklist in this plan.

#### Step 2 -- implementation for requestor orchestration

**Files involved**:

- `instructions/spec-review-requestor.md` (new, to be created).
- `.agent/workflows/spec-review-requestor.md` (new, redirect adapter to be
  created).
- `.agents/llm-shared/instructions/spec-review-requestor.md` (new, redirect
  adapter to be created).
- `.agents/llm-shared/skills/spec-review-requestor/SKILL.md` (new, redirect
  adapter to be created).
- `.claude/skills/spec-review-requestor/SKILL.md` (new, redirect adapter to be
  created).
- `tests/unit/tools/test_spec_review_requestor_instruction/__init__.py` (new,
  to be created).
- `tests/unit/tools/test_spec_review_requestor_instruction/test_spec_review_requestor_instruction_tdd.py`
  (new, to be created).
- `tests/unit/tools/test_instruction_structure/test_spec_review_requestor_adapters_tdd.py`
  (new, to be created).

**Tests first**:

- Assert the exact family policy, status/activate/start/publish/wait/consume/
  continue/confirm/reclaim/complete sequence, exact answer-path reading, and no
  transcript reread.
- Assert wording-edit-before-gate behavior, exact choices, durable replay, and
  canonical consolidation only after authorization.
- Assert the `.agent/workflows`, `.agents/llm-shared/instructions`,
  `.agents/llm-shared/skills`, and `.claude/skills` adapters contain only
  metadata plus a direct canonical redirect, with no copied instruction body.

**Behavior**:

- Canonical role invokes the paired renderer for each request and the shared
  requestor for coordination.
- An expired intact active round uses `reclaim`; escalated state stops for human
  resolution.
- `Consolidate` delegates the exact document to canonical consolidation. The
  resulting `pw skill` live-exchange precedence returns the settled document
  to this role, which verifies the consolidated decision marker, calls
  `complete`, and reruns `pw skill` for ordinary next-phase routing.

**Completion criteria**:

- `ghog single tests/unit/tools/test_spec_review_requestor_instruction/test_spec_review_requestor_instruction_tdd.py tests/unit/tools/test_instruction_structure/test_spec_review_requestor_adapters_tdd.py`
  passes.
- `rg --line-number "consolidation-ready|Revise and review again|Consolidate|reclaim|Human guidance:" instructions/spec-review-requestor.md`
  finds every specialized contract token.
- `ghog day` reports `exit=0`.

#### Step 2 -- addendums for requestor orchestration

Line-budget checkpoint:

- `test_spec_review_requestor_instruction_tdd.py`: baseline 0; below-550 safe;
  ceiling 650; advisory final count 240-340.
- `test_spec_review_requestor_adapters_tdd.py`: baseline 0; below-550 safe;
  ceiling 650; advisory final count 120-190.

Split guidance:

- Keep lifecycle details referenced from `instructions/review-requestor.md`;
  split no canonical prose into adapters.

Full workflow timing run readiness:

- Focused instruction and adapter tests; `ghog day`.

Time-gated status for Step 2:

- No perf gates are affected; this step adds Markdown adapters and orchestration
  contracts only.

---

### Step 3. Route new questions and resume live exchanges through pw

#### Step 3 -- analysis and intent for workflow routing

Issues to address:

- Both question workflows currently stop for human review when questions
  remain, even when `a.review-mode` is active.
- Normal `pw skill` routing can bypass a live specification exchange after a
  session boundary.
- `tools/prompt_workflow_skill.py` is already in the 550-through-650 risk band.

Fix intent:

- Add one focused review-routing module with constant exact-path candidate
  checks and no transcript access.
- Add forced `spec-review-requestor` targeting for the current open-question
  document and live-exchange precedence for ordinary `pw skill`.
- Add identical thin delegation references to both canonical question
  workflows while honoring `stop here` before exchange status.

Expected outcome:

- Marker absence preserves current behavior; marker presence delegates new
  questions automatically.
- A matching live exchange wins over ordinary document routing, including
  reclaimable and owning-action-pending states.

Step framing:

- Design links: Question-present activation boundary; Q01 and Q03.
- Execution checklist: Shared execution command checklist in this plan.

#### Step 3 -- implementation for workflow routing

**Files involved**:

- `tools/prompt_workflow_review.py` (new, to be created).
- `tools/prompt_workflow_skill.py` (existing, to be updated narrowly).
- `instructions/review-ask-questions.md` (existing, to be updated).
- `instructions/consolidate-then-review-ask-questions.md` (existing, to be
  updated).
- `tests/unit/tools/test_prompt_workflow_review/__init__.py` (new, to be
  created).
- `tests/unit/tools/test_prompt_workflow_review/test_prompt_workflow_review_tdd.py`
  (new, to be created).
- `tests/unit/tools/test_prompt_workflow_skill/test_prompt_workflow_skill_spec_review_tdd.py`
  (new, to be created).
- `tests/unit/tools/test_spec_review_requestor_instruction/test_spec_review_question_workflow_integration_tdd.py`
  (new, to be created).

**Tests first**:

- Cover requirement, design, and plan selection, registered design type mapping,
  constant candidate count, no glob/rglob/iterdir, and no transcript read.
- Cover forced delegation, normal live-exchange precedence, marker absence,
  no-question passes, explicit holds, current and expired leases, escalation,
  and owning-action replay.
- Cover multiple live specification exchanges for one topic failing closed and
  reporting every exact family, type, version, slug, and document identity.
- Cover both canonical question instructions naming the specialized role once
  and preserving their existing non-review handoffs.

**Behavior**:

- `prompt_workflow_review` derives exact candidate contexts from the resolved
  topic state and returns the applicable reviewed document and live state.
- `prompt_workflow_skill` delegates special forced/current routing without
  embedding exchange parsing.
- More than one live specification exchange for the resolved topic is an
  ambiguity: routing selects none, fails closed, and reports every exact
  identity.
- A settled document in `owning-action-pending` state routes back to the
  specialized requestor so it can verify the decision marker, complete the
  exchange, and rerun ordinary routing.
- Question instructions call the `pw`-resolved specialized role only after they
  placed questions and review mode is active.

**Completion criteria**:

- `ghog single tests/unit/tools/test_prompt_workflow_review/test_prompt_workflow_review_tdd.py tests/unit/tools/test_prompt_workflow_skill/test_prompt_workflow_skill_spec_review_tdd.py tests/unit/tools/test_spec_review_requestor_instruction/test_spec_review_question_workflow_integration_tdd.py`
  passes.
- `rg --line-number "rglob|glob|iterdir|review\.(feature-request|issue|design-specification|plan)" tools/prompt_workflow_review.py`
  finds no directory scan or exact transcript artifact dependency.
- `rg --line-number "spec-review-requestor" instructions/review-ask-questions.md instructions/consolidate-then-review-ask-questions.md tools/prompt_workflow_skill.py`
  finds the thin integration points.
- `ghog day` reports `exit=0`.

#### Step 3 -- addendums for workflow routing

Line-budget checkpoint:

- `tools/prompt_workflow_review.py`: baseline 0; below-550 safe; ceiling 650;
  advisory final count 180-280.
- `tools/prompt_workflow_skill.py`: baseline 631; 550-through-650 risk; ceiling
  650; advisory final count at or below 645.
- `test_prompt_workflow_review_tdd.py`: baseline 0; below-550 safe; ceiling 650;
  advisory final count 260-380.
- `test_prompt_workflow_skill_spec_review_tdd.py`: baseline 0; below-550 safe;
  ceiling 650; advisory final count 180-280.

Split guidance:

- Do not add exchange parsing to `prompt_workflow_skill.py`. If its narrow
  delegation would exceed 650 lines, move existing forced-skill resolution into
  `tools/prompt_workflow_review.py` or a responsibility-focused sibling before
  completing the step.
- Keep all new routing tests out of the existing 596-line primary skill test.

Full workflow timing run readiness:

- Focused routing and workflow-instruction tests; `ghog day`.

Time-gated status for Step 3:

- No xfail perf gate; focused tests assert bounded exact-path lookup and reject
  scan APIs.

---

### Step 4. Prove the full specification requestor workflow

#### Step 4 -- analysis and intent for acceptance coverage

Issues to address:

- Unit slices do not prove that marker detection, `pw`, paired rendering, shared
  publication, transcript aggregation, repeated rounds, reclaim, and
  convergence compose correctly.
- Later reviewer work must be able to rely on the requestor artifacts without
  specialized transport exceptions.

Fix intent:

- Add repository-level acceptance fixtures that drive the specialized writer
  against the real shared exchange surface while simulating counterpart answers.
- Verify all supported specification types and exact human-gate behavior.

Expected outcome:

- Review mode is opt-in, round identities remain coherent, aggregation is
  append-only, and no protocol artifact is hand-mutated by the requestor.
- The feature is ready for the independent `spec-reviewer` umbrella item.

Step framing:

- Design links: all acceptance cases and Q01-Q05.
- Execution checklist: Shared execution command checklist in this plan.

#### Step 4 -- implementation for acceptance coverage

**Files involved**:

- `tests/unit/tools/test_spec_review_requestor_acceptance/__init__.py` (new, to
  be created).
- `tests/unit/tools/test_spec_review_requestor_acceptance/test_spec_review_requestor_acceptance_tdd.py`
  (new, to be created).
- `tests/unit/tools/test_spec_review_requestor_acceptance/test_spec_review_requestor_io_acceptance_tdd.py`
  (new, to be created).

**Tests first**:

- Marker absent, explicit hold, no-question pass, and marker-present activation.
- Feature-request, issue, design-specification, and plan artifact identities.
- Round 1 publication, transcript initialization, substantive append, change
  answer consumption, replacement round, literal guided override, reclaim,
  convergence retention, durable `Consolidate`, canonical owning action, and
  completion cleanup.
- Failure cases for mismatched identity, escalation, unsupported type, tracked
  root inputs, duplicate live document exchange, and transcript-read attempts.
- IO acceptance proving a constant exact-path set and no documentation-tree or
  transcript-history read.

**Behavior**:

- Acceptance fixtures invoke public launchers and canonical routing contracts;
  they do not reach into core private state to manufacture success.
- Counterpart answer publication may use the shared core directly because the
  independent reviewer role remains deferred.

**Completion criteria**:

- `ghog single tests/unit/tools/test_spec_review_requestor_acceptance/test_spec_review_requestor_acceptance_tdd.py tests/unit/tools/test_spec_review_requestor_acceptance/test_spec_review_requestor_io_acceptance_tdd.py`
  passes.
- `rg --line-number "feature-request|issue|design-specification|plan|consolidation-ready|Human guidance:" tests/unit/tools/test_spec_review_requestor_acceptance`
  finds complete family and gate coverage.
- `ghog day` reports `exit=0` with full project coverage at the repository gate.

#### Step 4 -- addendums for acceptance coverage

Line-budget checkpoint:

- `test_spec_review_requestor_acceptance_tdd.py`: baseline 0; below-550 safe;
  ceiling 650; advisory final count 360-480.
- `test_spec_review_requestor_io_acceptance_tdd.py`: baseline 0; below-550 safe;
  ceiling 650; advisory final count 160-240.

Split guidance:

- Keep IO/failure instrumentation separate from lifecycle scenarios; if either
  test file approaches 650 lines, split by activation, repeated-round, and
  convergence responsibilities without growing the existing 585-line workflow
  acceptance test.

Full workflow timing run readiness:

- Full requestor acceptance suite; `ghog day`.

Time-gated status for Step 4:

- Acceptance IO assertions remain permanent regression gates; no xfail marker
  remains.
