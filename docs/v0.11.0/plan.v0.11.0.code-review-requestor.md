# v0.11.0 code-review-requestor implementation plan -- review before commit

Implement a bounded code-review requestor at the existing commit gate while preserving the shared exchange and the human-only commit decision.

- **Paired rendering**: produce one coherent code-review request and transcript summary from validated round inputs.
- **Focused orchestration**: add one canonical requestor role with redirect-only host adapters.
- **Durable routing**: carry exact plan-step context through `pw`, resume live exchanges, and continue an authorized commit without asking twice.
- **Acceptance proof**: validate opt-in behavior, staged repairs, repeated rounds, convergence overrides, and commit authorization end to end.

## Plan goal for v0.11.0 code-review-requestor

Implement the full feature described by `design.v0.11.0.code-review-requestor.md` and `feature-request.v0.11.0.code-review-requestor.md` in four ordered steps.

- **Step 1 goal**: add paired code-review request rendering.
- **Step 2 goal**: add the specialized requestor instruction and adapters.
- **Step 3 goal**: integrate `implement-step` and `pw` routing, step transport, live resumption, and authorized commit continuation.
- **Step 4 goal**: prove the complete workflow with acceptance coverage.

## Scope anchors for v0.11.0 code-review-requestor plan

This plan delivers marker-gated activation after `group-commits-msg`, exact plan-step-round identity, bounded staged repair assessment, automated intermediate rounds, and durable human-owned commit authorization.

In scope:

- The code-review request renderer and launcher.
- The canonical code-review requestor role and redirect adapters.
- Thin `implement-step` activation and `pw` command routing with an explicit step token.
- A dedicated post-confirmation continuation into existing commit mechanics.
- Focused unit, instruction-structure, routing, and repository-level acceptance tests.

Deferred:

- Independent `code-reviewer` implementation and answer generation.
- Review-mode Diataxis documentation assigned to the final umbrella item.
- Changes to shared exchange persistence, locking, or timeout semantics.

## Complexity bound clarification for v0.11.0

- **O(1) per routing or exchange operation**: operate on one resolved effort, plan, step, and constant artifact set.
- **O(n) per authored input or staged diff**: rendering and answer assessment scale linearly with the content being reviewed.
- No response path adds a documentation-tree scan, transcript-history read, `O(n log n)`, or `O(n^2)` operation.

## File-based IO cost clarification for v0.11.0 code-review-requestor

- Resolve the exact plan and step once at activation and carry both in the rendered command.
- Read each ignored authored input once and write paired renderer outputs once.
- Use shared atomic exact-path exchange operations; do not scan docs or reread transcripts.
- Read the staged diff, repaired-path inventory, validation evidence, and `a.commit` once per answer assessment.

## Step 0 perf-gate decision for v0.11.0 code-review-requestor

No Step 0 is required. The feature adds bounded synchronous CLI and Markdown workflows, not a timing-sensitive loop. Permanent IO acceptance assertions in Step 4 will reject directory scans and transcript reads; no `pytest.mark.timeout` xfail gate is needed.

## Confirmed technical facts for v0.11.0 plan viability

**Files in the 550-through-650 risk band**:

- `tools/prompt_workflow.py`: 572 lines -- keep parser wiring narrow and extract code-review routing behavior; ceiling 650.
- `tools/prompt_workflow_skill.py`: 552 lines -- keep only delegation and compatibility exports here; ceiling 650.
- `tools/review_exchange_core.py`: 558 lines -- no planned growth; use its public operations unchanged.

**Files below 550 and safe to extend**:

- `tools/prompt_workflow_review.py`: 201 lines -- preserve specification routing; no code-review responsibility added.
- `tools/prompt_workflow_render.py`: 47 lines -- add a narrow optional step-aware render helper; advisory final count 80.
- `tools/spec_review_request.py`: 413 lines -- reference its interface but do not extend it.
- `instructions/implement-step.md`: 77 lines -- add one bounded post-grouping delegation block.
- `instructions/review-requestor.md`: 120 lines -- shared role-neutral contract remains unchanged.
- `test_prompt_workflow_skill_rendering.py`: 69 lines -- add focused step-aware rendering cases; advisory final count 120.
- `test_prompt_workflow_skill_spec_review_tdd.py`: 137 lines -- preserve specification behavior unchanged.

**New files**:

- `tools/code_review_request.py`, `templates/code-review-request.template.md`, and `bin/code_review_request.bat`.
- `instructions/code-review-requestor.md` plus `.agent`, `.agents`, and `.claude` redirect adapters.
- `tools/prompt_workflow_code_review.py` for code-review routing and authorized continuation.
- Focused renderer, instruction, routing, integration, and acceptance test packages with their `__init__.py` files.

**Other confirmed facts**:

- `render_command` currently emits only `<skill> on <document>`; Step 3 adds explicit implementation-step transport without changing ordinary commands.
- `_implementation_command` already derives the next uncommitted plan step from the validation plan and commit history.
- `group-commits-msg` owns `a.commit` validation and batch commit mechanics; the new continuation must reuse that ownership.
- Existing `a.*` ignore coverage applies to renderer inputs and exchange artifacts.

## Current test-tree validation snapshot

Preserve existing review-exchange, specification-requestor, workflow-routing, instruction-structure, and commit-cycle suites. Add new leaf packages instead of growing risk-band suites:

- `tests/unit/tools/test_code_review_request/`.
- `tests/unit/tools/test_code_review_requestor_instruction/`.
- `tests/unit/tools/test_prompt_workflow_code_review/`.
- `tests/unit/tools/test_code_review_requestor_acceptance/`.

Property-based coverage is not required for authored Markdown rendering. Existing exchange model property tests continue to own identity/state invariants; focused examples cover every code-review command shape and disposition.

## Runtime file note

- Root `a.review-requested.code.*`, `a.review-answer.code.*`, coordination, lock, tombstone, and caller-authored renderer files remain ignored.
- `review.code.vX.Y.Z.<slug>.md` beside the plan is the only versioned code-review exchange artifact.
- Reviewer manifests remain owned by the later `code-reviewer` effort.

## Shared execution command checklist for all steps

1. Count physical lines before edits with `(Get-Content -LiteralPath <path>).Count`.
2. Add or update tests first.
3. Run focused tests through `ghog single <test paths>`.
4. Run the step-specific `rg` checks.
5. Run `ghog day` repeatedly until it reports the objective with `exit=0`.
6. Count lines after edits and compare with each line-budget checkpoint.
7. Split any Python file above 650 lines before completion; record advisory-estimate variance at or below 650 without failing the step.

## Ready-to-run command templates for all steps

- Line count: `(Get-Content -LiteralPath <path>).Count`
- Targeted tests: `ghog single <step test files>`
- Grep checks: `rg --line-number <pattern> <step paths>`
- Shared gate loop: `ghog day`, repeated until `exit=0`

## Numbered steps for v0.11.0 code-review-requestor

### Step 1. Add paired code-review request rendering

#### Step 1 -- analysis and intent

Issues to address:

- No specialized renderer composes code-review request content and its transcript summary from one validated round input.
- Code requests need exact plan, step, round, umbrella, implementation report, writer response, change summary, and optional guidance.

Fix intent:

- Add an immutable code-round input and paired render result.
- Reuse shared envelope/Markdown validation while keeping code-review findings and conclusion wording specialized.

Expected outcome:

- One launcher call writes matching UTF-8 request-content and substantive-summary outputs under ignored root paths.

Step framing:

- Design links: Implementation-specific request body; Q02.
- Execution checklist: Shared execution command checklist for all steps.

#### Step 1 -- implementation

**Files involved**:

- `tools/code_review_request.py` (new, to be created).
- `templates/code-review-request.template.md` (new, to be created).
- `bin/code_review_request.bat` (new, to be created).
- `tests/unit/tools/test_code_review_request/__init__.py` (new, to be created).
- `tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py` (new, to be created).

**Tests first**:

- Cover exact plan, step, round, umbrella-or-none, fixed `code` identity, H1/JSON/H2 structure, paired output identity, repaired-path and staged-state instructions, and optional guidance.
- Reject invalid plans, empty steps, nonpositive rounds, tracked or non-root scratch paths, invalid UTF-8, and independently inconsistent outputs.

**Classes and behavior**:

- `CodeReviewRoundInput`: validated identity and separate authored inputs.
- `CodeReviewRequestRender`: complete request and substantive transcript summary.
- CLI: read ignored UTF-8 assessment, report, change summary, writer response, and optional guidance once; write two validated ignored outputs once.

**Completion criteria**:

- `ghog single tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py` passes.
- `rg --line-number "Implementation plan:|Implementation step:|Review round:|## JSON" tools/code_review_request.py templates/code-review-request.template.md` finds the contract.
- `ghog day` reports `exit=0`.

#### Step 1 -- addendums

Line-budget checkpoint:

- `tools/code_review_request.py`: baseline 0; below-550 safe; ceiling 650; advisory final count 280-380.
- `test_code_review_request_tdd.py`: baseline 0; below-550 safe; ceiling 650; advisory final count 300-430.

Split guidance:

- If the renderer approaches 650 lines, extract CLI/path validation into `tools/code_review_request_cli.py` and keep pure rendering in `code_review_request.py`.

Full workflow timing run readiness: focused renderer tests; `ghog day`.

Time-gated status: no perf gate; permanent tests assert one-read/one-write paired rendering.

### Step 2. Add the specialized code-review requestor role

#### Step 2 -- analysis and intent

Issues to address:

- The shared requestor is intentionally role-neutral and cannot assess staged repairs, `a.commit`, or implementation evidence.
- No discoverable canonical role registers the code family policy and human choice labels.

Fix intent:

- Add one canonical instruction that uses `review-requestor.md` for every transition and the Step 1 renderer for authored output.
- Add redirect-only workflow, Codex, and Claude adapters.

Expected outcome:

- The role handles disabled, idle, request/answer pending, abandoned, convergence, owning-action pending, and escalation states without manual protocol edits.

Step framing:

- Design links: Specialized writer and shared requestor ownership; Repair assessment; Q04 and Q06.
- Execution checklist: Shared execution command checklist for all steps.

#### Step 2 -- implementation

**Files involved**:

- `instructions/code-review-requestor.md` (new, to be created).
- `.agent/workflows/code-review-requestor.md` (new, redirect adapter to be created).
- `.agents/llm-shared/instructions/code-review-requestor.md` (new, redirect adapter to be created).
- `.agents/llm-shared/skills/code-review-requestor/SKILL.md` (new, redirect adapter to be created).
- `.claude/skills/code-review-requestor/SKILL.md` (new, redirect adapter to be created).
- `tests/unit/tools/test_code_review_requestor_instruction/__init__.py` (new, to be created).
- `tests/unit/tools/test_code_review_requestor_instruction/test_code_review_requestor_instruction_tdd.py` (new, to be created).
- `tests/unit/tools/test_instruction_structure/test_code_review_requestor_adapters_tdd.py` (new, to be created).

**Tests first**:

- Assert `code`, `commit-ready`, `Rework and review again`, and `Commit`; exact plan/step identity; status through completion; exact answer-path reading; no transcript reread.
- Assert staged repair inventory, four-part scope evidence, `a.commit` assessment, explicit repair-reversal disagreement, substantive-change classification, and convergence override recommendation.
- Assert all adapters contain metadata plus direct canonical redirects only.

Instruction assertions check required tokens and their required ordering rather than whole sentences, so a wording change does not fail the suite and a rule change does.

**Classes and behavior**:

- Canonical role invokes the paired renderer and shared requestor commands.
- Intermediate answers can be consumed; convergence answers remain evidence and use only the human gate.
- Durable `Commit` authorization delegates to the owning continuation and completes only after success.

**Completion criteria**:

- `ghog single tests/unit/tools/test_code_review_requestor_instruction/test_code_review_requestor_instruction_tdd.py tests/unit/tools/test_instruction_structure/test_code_review_requestor_adapters_tdd.py` passes.
- `rg --line-number "commit-ready|Rework and review again|Commit|reviewed-work-changed|disagreement" instructions/code-review-requestor.md` finds the policy.
- `ghog day` reports `exit=0`.

#### Step 2 -- addendums

Line-budget checkpoint:

- `test_code_review_requestor_instruction_tdd.py`: baseline 0; below-550 safe; ceiling 650; advisory final count 260-380.
- `test_code_review_requestor_adapters_tdd.py`: baseline 0; below-550 safe; ceiling 650; advisory final count 120-190.

Split guidance: keep lifecycle details in `review-requestor.md`; never copy canonical prose into adapters.

Full workflow timing run readiness: focused instruction/adapter tests; `ghog day`.

Time-gated status: no perf gate; Markdown contract only.

### Step 3. Integrate commit-gate activation and durable pw routing

#### Step 3 -- analysis and intent

Issues to address:

- `implement-step` always reaches the ordinary human commit gate after grouping.
- Ordinary rendered commands cannot carry an implementation step.
- Live code exchanges and authorized commits need exact resumable routing without growing risk-band router modules beyond 650 lines.

Fix intent:

- Add focused code-review route resolution and step-aware rendering in a new module.
- Add a narrow `implement-step` delegation after successful grouping.
- Add forced/live requestor routing and a dedicated authorized commit continuation that reuses existing commit mechanics without another choice.

Expected outcome:

- Marker absence is unchanged; marker presence emits a self-contained plan-and-step requestor command; live state wins over ordinary routing; durable commit authorization resumes once.

Step framing:

- Design links: Commit-gate activation; Exact plan and step identity; Convergence; Q01, Q03, and Q05.
- Execution checklist: Shared execution command checklist for all steps.

#### Step 3 -- implementation

**Files involved**:

- `tools/prompt_workflow_code_review.py` (new, to be created).
- `tools/prompt_workflow_render.py` (existing, to be updated).
- `tools/prompt_workflow_skill.py` (existing, narrow delegation update).
- `tools/prompt_workflow.py` (existing, narrow CLI wiring update).
- `instructions/implement-step.md` (existing, to be updated).
- `instructions/group-commits-msg.md` (existing, to be updated for authorized continuation entry only).
- `tests/unit/tools/test_prompt_workflow_code_review/__init__.py` (new, to be created).
- `tests/unit/tools/test_prompt_workflow_code_review/test_prompt_workflow_code_review_tdd.py` (new, to be created).
- `tests/unit/tools/test_prompt_workflow_skill/test_prompt_workflow_skill_rendering.py` (existing, to be updated).
- `tests/unit/tools/test_code_review_requestor_instruction/test_implement_step_integration_tdd.py` (new, to be created).

**Tests first**:

- Cover step-aware Codex and Claude rendering while ordinary document-only rendering remains byte-compatible.
- Cover marker sampling exactly after grouping, no artifacts when absent, explicit plan and step when present, live requestor precedence, abandoned reclaim routing, convergence, and owning-action replay.
- Cover dedicated authorized continuation invoking existing batch-commit validation/execution exactly once without displaying a second commit choice.
- Reject missing/unknown steps, mismatched plan context, duplicate live code exchanges, and authorization absent or for another identity.

**Classes and behavior**:

- `prompt_workflow_code_review`: derive exact plan-step context, inspect only exact code-exchange paths, and render/resume specialized routes.
- `render_step_command`: append a literal space followed by `step <id>` after the ordinary `<skill> on <document>` command, preserving the ordinary command as a byte-identical strict prefix.
- CLI/skill modules: delegate parser and route work to the focused module.
- Writer instructions: sample marker once after grouping and run the exact `pw` output.

**Completion criteria**:

- `ghog single tests/unit/tools/test_prompt_workflow_code_review/test_prompt_workflow_code_review_tdd.py tests/unit/tools/test_prompt_workflow_skill/test_prompt_workflow_skill_rendering.py tests/unit/tools/test_code_review_requestor_instruction/test_implement_step_integration_tdd.py` passes.
- `rg --line-number "glob|rglob|iterdir|transcript" tools/prompt_workflow_code_review.py` confirms no scan/transcript dependency.
- `rg --line-number "code-review-requestor|a.review-mode|implementation-step" instructions/implement-step.md tools/prompt_workflow_code_review.py tools/prompt_workflow_skill.py` finds the thin integration.
- `rg --line-number " step " tools/prompt_workflow_render.py tests/unit/tools/test_prompt_workflow_skill/test_prompt_workflow_skill_rendering.py` finds the literal step-token contract in both the renderer and its test.
- `ghog day` reports `exit=0`.

#### Step 3 -- addendums

Line-budget checkpoint:

- `tools/prompt_workflow_code_review.py`: baseline 0; below-550 safe; ceiling 650; advisory final count 220-340.
- `tools/prompt_workflow_render.py`: baseline 47; below-550 safe; ceiling 650; advisory final count 80.
- `tools/prompt_workflow_skill.py`: baseline 552; 550-through-650 risk; ceiling 650; advisory final count at or below 590.
- `tools/prompt_workflow.py`: baseline 572; 550-through-650 risk; ceiling 650; advisory final count at or below 600.
- `instructions/implement-step.md`: baseline 77; non-Python; keep the added delegation concise.
- `test_prompt_workflow_skill_rendering.py`: baseline 69; below-550 safe; ceiling 650; advisory final count 120.
- `test_prompt_workflow_code_review_tdd.py`: baseline 0; below-550 safe; ceiling 650; advisory final count 260-380.
- `test_implement_step_integration_tdd.py`: baseline 0; below-550 safe; ceiling 650; advisory final count 120-200.

Split guidance:

- Put all code-review classification and continuation behavior in `prompt_workflow_code_review.py`; if either risk-band router would exceed 650, move existing CLI or forced-route responsibility to a cohesive sibling before completion.

Full workflow timing run readiness: focused routing/instruction tests; `ghog day`.

Time-gated status: no xfail perf gate; permanent tests prohibit scans and duplicate commit execution.

### Step 4. Prove the full code-review requestor workflow

#### Step 4 -- analysis and intent

Issues to address:

- Unit slices do not prove that grouping, marker activation, step transport, rendering, staged repairs, exchange rounds, human override, and authorized commit continuation compose.

Fix intent:

- Add repository-level acceptance fixtures through public launchers and shared exchange operations.
- Cover all feature acceptance cases and IO constraints, with the reviewer simulated through the shared answer surface because `code-reviewer` is deferred.

Expected outcome:

- The requestor is demonstrably opt-in, bounded, resumable, and unable to commit without durable human authorization.

Step framing:

- Design links: all acceptance cases and Q01-Q06.
- Execution checklist: Shared execution command checklist for all steps.

#### Step 4 -- implementation

**Files involved**:

- `tests/unit/tools/test_code_review_requestor_acceptance/__init__.py` (new, to be created).
- `tests/unit/tools/test_code_review_requestor_acceptance/code_answer_builder.py` (new, test-local builder to be created).
- `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py` (new, to be created).
- `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py` (new, to be created).

**Tests first**:

- Cover marker absent/present, exact step handoff, round 1 publication, staged repair inventory, `a.commit` amendment, changes-requested continuation, explicit reversal disagreement, reclaim, and escalation.
- Cover polishing-only convergence, substantive-repair convergence with override recommendation, durable `Rework and review again`, durable `Commit`, later-session owning-action replay, one batch commit, and completion cleanup.
- Cover mismatched plan/step/round/umbrella, unrelated staged paths, duplicate live exchanges, tracked scratch inputs, directory-scan attempts, transcript reads, and second commit attempts.

**Classes and behavior**:

- Acceptance fixtures exercise launchers and public routing contracts.
- `code_answer_builder.py` composes one valid code-family answer envelope and authored body for the exact plan, step, round, umbrella, disposition, repaired paths, and recommendation used by each scenario.
- Shared exchange answer publication simulates the deferred reviewer without bypassing requestor state rules.

**Completion criteria**:

- `ghog single tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py` passes.
- `rg --line-number "commit-ready|Rework and review again|owning_action_authorized|implementation-step|a.commit" tests/unit/tools/test_code_review_requestor_acceptance` finds complete gate coverage.
- `ghog day` reports `exit=0` with the full coverage objective.

#### Step 4 -- addendums

Line-budget checkpoint:

- `code_answer_builder.py`: baseline 0; below-550 safe; ceiling 650; advisory final count 150-260.
- `test_code_review_requestor_acceptance_tdd.py`: baseline 0; below-550 safe; ceiling 650; advisory final count 400-540.
- `test_code_review_requestor_io_acceptance_tdd.py`: baseline 0; below-550 safe; ceiling 650; advisory final count 170-260.

Split guidance: keep IO/failure instrumentation separate from lifecycle cases; split acceptance tests by activation, rounds, and convergence before either file exceeds 650.

Full workflow timing run readiness: full requestor acceptance suite; `ghog day`.

Time-gated status: permanent IO and single-commit assertions remain; no xfail marker.

## Implementation decisions for v0.11.0 code-review-requestor

| Question | Decision | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | Keep step-aware rendering and CLI parsing in Step 3 with the routing that consumes them. | Step 3 implementation | Move command rendering into Step 1; add a routing-prerequisite step |
| Q02 | Test authorized commit continuation in temporary Git repositories and intercept only the final batch-commit subprocess boundary. | Step 3 tests; Step 4 acceptance coverage | Mock all Git/exchange behavior; commit in the shared workspace |
| Q03 | Protect repair-scope policy with token/order instruction tests in Step 2 and executable staged-diff scenarios in Step 4. | Step 2 tests; Step 4 tests | Instruction-only coverage; acceptance-only coverage |
| Q04 | Permit narrow risk-band delegation at or below 650 lines and split only when measured post-edit size crosses the process ceiling. | Step 3 line-budget checkpoint and split guidance | Mandatory pre-edit split; allow growth beyond 650 |
| Q05 | Render the exact visible handoff as `<skill> on <document> step <id>`, leaving the ordinary command as a strict prefix. | Step 3 classes, tests, and grep criteria | Flag-style suffix; compact document qualifier |
| Q06 | Use `tests/unit/tools/test_code_review_requestor_acceptance/code_answer_builder.py` to build valid code-family answers for requestor acceptance scenarios. | Step 4 files and behavior | Repeat hand-authored answer Markdown; pull forward the deferred reviewer renderer |
