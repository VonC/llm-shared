# v0.11.0 specification reviewer implementation plan -- independent response flow

Implement the responder as a state-aware route, a pure paired renderer, and a
thin reviewer role over the completed review exchange core.

- **Routing**: select reviewer work from one immutable context-and-state value.
- **Rendering**: produce one answer and one transcript summary from typed inputs.
- **Authority**: keep reviewer, requestor, and human transitions distinct.

## Plan goal for v0.11.0 specification reviewer

Implement the behavior settled in
`docs/v0.11.0/design.v0.11.0.spec-reviewer.md` in four ordered slices.

- **Step 1 goal**: add state-aware reviewer routing and split the full routing module.
- **Step 2 goal**: add the pure paired answer renderer and fixed-path CLI.
- **Step 3 goal**: add the canonical reviewer instruction, adapters, and requestor wait alignment.
- **Step 4 goal**: prove the complete reviewer lifecycle, recovery, authority, and IO bounds.

---

## Scope anchors for v0.11.0 specification reviewer plan

This plan implements the consolidated feature request and design beside this
document. It delivers:

1. ordinary and explicit routing to `spec-reviewer` for one exact pending request;
2. independent full-document assessment with typed disposition content;
3. paired answer and transcript-summary rendering;
4. shared publication, in-session reclaim, stopped-round retention, and recovery;
5. requestor-side full configured answer waiting; and
6. acceptance coverage for all supported specification identities.

The plan does not add code-review behavior, reviewer-authored specification
edits, human confirmation authority, new exchange state transitions, or review
mode user documentation reserved for later umbrella items.

## Complexity bound clarification for v0.11.0 specification reviewer

- **O(1) route observation per topic**: inspect at most the resolved requirement,
  design, and plan exchange contexts.
- **O(n) assessment and rendering per round**: read and render content once,
  where `n` is the combined exact input byte count.
- No response path may add documentation-tree scans, transcript-history reads,
  `O(n log n)`, or `O(n^2)` processing.

## File-based IO cost clarification for v0.11.0 specification reviewer

- Routing uses only the fixed document and exchange paths derived for one topic.
- The reviewer reads the exact request, current specification, coordination
  state, and ignored authored inputs a constant number of times.
- The renderer builds both Markdown outputs in memory and writes only the two
  explicit ignored output paths.
- The shared exchange command remains the sole publisher of the answer,
  consumed request, coordination state, and versioned transcript append.
- Recovery reads one exact retained manifest and removes it after successful
  republication; it never scans for nearby scratch files.

## Step 0 perf-gate decision for v0.11.0 specification reviewer

No Step 0 `xfail` performance gate is required. Existing review-exchange tests
already exercise bounded waits and exact-path IO. Step 1 adds state-mapping and
constant-candidate guards, while Step 4 adds end-to-end IO acceptance coverage.

## Confirmed technical facts for v0.11.0 plan viability

**Files at the 650-line repository ceiling**:

- `tools/prompt_workflow_skill.py`: 650 lines. Step 1 must split responsibility
  before adding reviewer routing; no further net growth is allowed in place.

**Files below 550 and safe to extend**:

- `tools/prompt_workflow_review.py`: 192 lines.
- `tools/spec_review_request.py`: 413 lines; retained as the requestor pattern,
  not extended for reviewer behavior.
- `tools/__init__.py`: 83 lines.
- `instructions/spec-review-requestor.md`: 162 lines.
- `test_prompt_workflow_review_tdd.py`: 298 lines.
- `test_prompt_workflow_skill_spec_review_tdd.py`: 128 lines.
- `test_spec_review_requestor_instruction_tdd.py`: 124 lines.
- `test_spec_review_requestor_adapters_tdd.py`: 121 lines.

**New production and test surfaces**:

- paired answer renderer and CLI modules, template, and launcher;
- canonical `spec-reviewer` instruction and four thin host adapters;
- focused answer-renderer, reviewer-instruction, and reviewer-acceptance tests.

**Repository facts affecting the steps**:

- `prompt_workflow_review._LiveRoute` is already frozen and carries context plus
  state, but public routing currently discards the state and returns only a path.
- `prompt_workflow_skill.forced_command` recognizes only
  `spec-review-requestor` for specification review.
- `ReviewExchangeCore` already owns `wait-request`, `publish-answer`, `reclaim`,
  marker gating, atomic transitions, and artifact identity validation.
- The generic `templates/review-answer.template.md` contains only the shared
  Markdown envelope shape; reviewer-specific sections remain to be added.

## Current test-tree validation snapshot for v0.11.0 specification reviewer

Existing packages to extend without weakening their assertions:

- `tests/unit/tools/test_prompt_workflow_review/` for fixed candidate discovery
  and live-state classification;
- `tests/unit/tools/test_prompt_workflow_skill/` for command rendering and forced
  routing;
- `tests/unit/tools/test_spec_review_requestor_instruction/` for the requestor's
  complementary full-timeout wait contract;
- `tests/unit/tools/test_instruction_structure/` for thin adapter structure.

New test leaf directories:

- `tests/unit/tools/test_spec_review_answer/`;
- `tests/unit/tools/test_spec_reviewer_instruction/`;
- `tests/unit/tools/test_spec_reviewer_acceptance/`.

Property-based coverage is needed in Step 1 for the finite artifact-state to
owning-role mapping. Renderer, instruction, and lifecycle partitions are finite
scenario matrices and do not need additional property tests.

## Runtime file note for v0.11.0 specification reviewer plan

Reviewer assessments, instructions, guidance responses, paired renderer
outputs, and retained-context manifests remain project-root `a.*` files. They
must be UTF-8, regular files, effectively ignored by Git, and supplied by exact
path. The retained manifest is caller-owned scratch evidence, not a protocol
artifact, and is removed after successful republication.

## Shared execution command checklist for all v0.11.0 specification reviewer steps

1. Count physical lines before edits with `(Get-Content "<path>").Count`.
2. Add or update the step's tests before production behavior.
3. Run the listed `ghog single` command.
4. Run the listed `rg` contract checks.
5. Run `ghog day`, fixing and repeating until it reports `exit=0`.
6. Count lines after edits and record variance against the step checkpoint.
7. Stop and split any Python file above 650 lines before completion.
8. Treat advisory-estimate variance at or below 650 as evidence, not missing work.

## Ready-to-run command templates for all v0.11.0 specification reviewer steps

- Line count: `(Get-Content "<path>").Count`
- Targeted tests: `ghog single <step test files>`
- Contract checks: `rg --line-number "<tokens>" <step files>`
- Shared gate: `ghog day`, repeated until it reports the objective with `exit=0`

## Implementation decisions for v0.11.0 specification reviewer

| Question | Decision | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | Extract only the four post-commit topic-discovery helpers, retain `post_commit_command`, and plan the cohesive host-rendering fallback when needed. | Step 1 implementation and split guidance | Moving `post_commit_command` creates a cycle; adding without a split violates the ceiling. |
| Q02 | Separate the pure typed renderer from CLI and filesystem validation. | Step 2 files, tests, and split guidance | One module couples pure tests to IO; three modules fragment a small model prematurely. |
| Q03 | Retire the retained manifest in reviewer orchestration only after successful publication. | Step 3 behavior | Renderer cleanup is premature; core cleanup turns caller scratch into protocol state. |
| Q04 | Exercise scenario matrices through public Python entry points with one smoke test per launcher. | Step 4 tests and behavior | All-subprocess coverage is slow; Python-only coverage misses launcher wiring. |
| Q05 | Share acceptance builders through package-local `fixtures.py`. | Step 4 files and behavior | Duplicated builders drift; global pytest fixtures broaden narrow feature setup. |

## Numbered steps for v0.11.0 specification reviewer

### Step 1. Route pending requests to the specification reviewer

#### Step 1 -- analysis and intent for reviewer routing

Issues to address:

- Public review routing loses the observed artifact state.
- Ordinary and forced commands cannot select `spec-reviewer`.
- `prompt_workflow_skill.py` is already at the repository ceiling.

Fix intent:

- expose one immutable live-route value and map its state to one owning role;
- preserve requestor ownership for cold abandoned requests and all writer states;
- extract only `_resolve_post_commit_topic`, `_plan_topics`,
  `_topic_from_validation_plan`, and `_slug_key` before adding forced reviewer
  routing; keep `post_commit_command` in the public skill module.

Expected outcome:

- pending requests route to the exact reviewer document with one observation;
- ambiguous candidates fail closed with every identity;
- cold abandoned requests produce an actionable requestor reclaim handoff.

Step framing:

- Design link: state-aware routing and explicit specification reviewer route.
- Execution checklist: shared execution command checklist in this plan.

#### Step 1 -- implementation for reviewer routing

**Files involved**:

- `tools/prompt_workflow_review.py` (existing, to be updated).
- `tools/prompt_workflow_skill.py` (existing, to be updated and split).
- `tools/prompt_workflow_post_commit.py` (new, to be created).
- `tests/unit/tools/test_prompt_workflow_review/test_prompt_workflow_review_spec_reviewer_tdd.py` (new, to be created).
- `tests/unit/tools/test_prompt_workflow_review/test_prompt_workflow_review_spec_reviewer_pbt.py` (new, to be created).
- `tests/unit/tools/test_prompt_workflow_skill/test_prompt_workflow_skill_spec_reviewer_tdd.py` (new, to be created).

**Tests first**:

- cover every live artifact state, marker suspension, one and multiple contexts,
  ordinary reviewer selection, writer-state routing, and no transcript reads;
- cover explicit `spec-reviewer`, cold abandoned-request diagnostics, absent or
  mismatched requests, host prefixes, and exact repository-relative documents;
- property-test that each generated supported state maps to exactly one role or
  the defined no-route outcome without a second classification.

**Types and behavior**:

- `LiveSpecificationRoute`: frozen exact context plus observed state.
- `live_specification_route`: returns the sole route without discarding state.
- `forced_command`: recognizes `spec-reviewer` only for an exact pending request.
- `prompt_workflow_post_commit`: owns `_resolve_post_commit_topic`,
  `_plan_topics`, `_topic_from_validation_plan`, and `_slug_key`. These helpers
  depend only on documentation discovery, shared workflow models, and suffix
  constants, so the skill router imports them one way.
- `post_commit_command`: remains in `prompt_workflow_skill.py` because it calls
  that module's `host_prefix` and `_document`; moving it would create the
  circular import the split is intended to avoid.

**Completion criteria**:

- `ghog single tests/unit/tools/test_prompt_workflow_review/test_prompt_workflow_review_spec_reviewer_tdd.py tests/unit/tools/test_prompt_workflow_review/test_prompt_workflow_review_spec_reviewer_pbt.py tests/unit/tools/test_prompt_workflow_skill/test_prompt_workflow_skill_spec_reviewer_tdd.py` passes.
- `rg --line-number "LiveSpecificationRoute|spec-reviewer|abandoned-request" tools/prompt_workflow_review.py tools/prompt_workflow_skill.py` finds the routing contract.
- `ghog day` reports `exit=0`.

#### Step 1 -- addendums for reviewer routing

Line-budget checkpoint:

- `tools/prompt_workflow_review.py`: baseline 192; below-550 safe; ceiling 650;
  advisory final count 250-330.
- `tools/prompt_workflow_skill.py`: baseline 650; 550-through-650 risk; ceiling
  650; expected count about 581 measured immediately after extracting the four
  discovery helpers; mandatory final target at or below 610 because splitting
  this full file is an explicit Step 1 goal.
- `tools/prompt_workflow_post_commit.py`: baseline 0; below-550 safe; ceiling 650;
  advisory final count 80-130.
- each new routing test file: baseline 0; below-550 safe; ceiling 650; advisory
  final count below 300.

Split guidance:

- Move only `_resolve_post_commit_topic`, `_plan_topics`,
  `_topic_from_validation_plan`, and `_slug_key`; keep `post_commit_command` in
  place and preserve one-way imports.
- The roughly 29-line margin from the immediate post-extraction count to the
  610 target makes a second split likely. Plan to move `detect_host`,
  `host_prefix`, and `render_command` together to
  `tools/prompt_workflow_render.py` when the reviewer-routing additions consume
  that margin, re-exporting them from the skill module for compatibility. Do
  not defer the count until step end or improvise a mixed-responsibility split.

Full workflow timing run readiness:

- focused routing tests, then `ghog day`.

Time-gated status for Step 1:

- No new wall-clock timeout; constant-candidate and no-rescan assertions are the gate.

---

### Step 2. Render paired specification review answers

#### Step 2 -- analysis and intent for answer rendering

Issues to address:

- no specialized typed answer renderer or reviewer template exists;
- generic answer structure does not enforce disposition-specific content;
- caller-owned file validation must remain separate from pure rendering.

Fix intent:

- add a pure typed renderer and a narrow fixed-path CLI;
- layer reviewer sections on the generic answer contract;
- produce answer and transcript summary from the same in-memory source.

Expected outcome:

- both dispositions produce valid paired Markdown with exact identity;
- guidance acknowledgment is conditionally required and separately authored;
- malformed, tracked, misplaced, or stale inputs fail before output mutation.

Step framing:

- Design link: paired answer design, disposition boundary, and trust boundaries.
- Execution checklist: shared execution command checklist in this plan.

#### Step 2 -- implementation for answer rendering

**Files involved**:

- `tools/spec_review_answer.py` (new, to be created).
- `tools/spec_review_answer_cli.py` (new, to be created).
- `tools/__init__.py` (existing, to be updated only for public exports).
- `templates/spec-review-answer.template.md` (new, to be created).
- `bin/spec_review_answer.bat` (new, to be created).
- `tests/unit/tools/test_spec_review_answer/__init__.py` (new, to be created).
- `tests/unit/tools/test_spec_review_answer/test_spec_review_answer_tdd.py` (new, to be created).
- `tests/unit/tools/test_spec_review_answer/test_spec_review_answer_cli_tdd.py` (new, to be created).

**Tests first**:

- cover feature-request, issue, design-specification, and plan identities;
- cover required H1 then `## JSON`, unique round-bearing headings, paired
  substantive content, and repository-relative human-readable identity;
- require requested changes for `changes-requested`, and covered wording plus
  convergence rationale for `convergence-recommended`;
- require a separate guidance-response input only when human guidance exists;
- cover invalid disposition, round, UTF-8, root location, ignore status, input
  drift, and output collision without partial writes.

**Types and behavior**:

- immutable typed assessment and disposition models validate conditional fields;
- pure renderer returns complete answer and transcript summary strings;
- CLI reads each exact caller input once, validates the current document digest
  and retained manifest when supplied, and writes the two ignored outputs;
- publication and protocol artifact mutation remain outside both modules.

**Completion criteria**:

- `ghog single tests/unit/tools/test_spec_review_answer/test_spec_review_answer_tdd.py tests/unit/tools/test_spec_review_answer/test_spec_review_answer_cli_tdd.py` passes.
- `rg --line-number "## JSON|changes-requested|convergence-recommended|guidance" tools/spec_review_answer.py templates/spec-review-answer.template.md` finds the contract.
- `ghog day` reports `exit=0`.

#### Step 2 -- addendums for answer rendering

Line-budget checkpoint:

- `tools/spec_review_answer.py`: baseline 0; below-550 safe; ceiling 650;
  advisory final count 260-360.
- `tools/spec_review_answer_cli.py`: baseline 0; below-550 safe; ceiling 650;
  advisory final count 150-240.
- `tools/__init__.py`: baseline 83; below-550 safe; ceiling 650; advisory final count 95.
- each new renderer test file: baseline 0; below-550 safe; ceiling 650; advisory
  final count below 500.

Split guidance:

- Keep path/encoding/ignore validation in the CLI module and pure models plus
  rendering in the renderer; split tests by pure content and filesystem IO.

Full workflow timing run readiness:

- focused renderer and CLI tests, then `ghog day`.

Time-gated status for Step 2:

- No new timeout; tests assert bounded exact-path reads and atomic output behavior.

---

### Step 3. Add reviewer orchestration and host adapters

#### Step 3 -- analysis and intent for reviewer orchestration

Issues to address:

- no canonical reviewer role or host adapters exist;
- reviewer and requestor reclaim entry paths must remain distinct;
- the requestor must use the marker's full answer wait without a shorter override.

Fix intent:

- encode the exact shared policy and reviewer operation sequence once;
- add thin redirect adapters for supported hosts;
- make retained assessment, manifest retirement, and authority stops explicit.

Expected outcome:

- the role waits for one exact request, assesses, renders, and publishes once;
- cold abandoned requests return to the requestor, while an active reviewer may
  reclaim its own expired intact lease;
- escalation stops for human recovery and convergence remains advisory.

Step framing:

- Design link: reviewer orchestration, authority matrix, and recovery design.
- Execution checklist: shared execution command checklist in this plan.

#### Step 3 -- implementation for reviewer orchestration

**Files involved**:

- `instructions/spec-reviewer.md` (new, to be created).
- `instructions/spec-review-requestor.md` (existing, to be updated).
- `.agent/workflows/spec-reviewer.md` (new, to be created).
- `.agents/llm-shared/instructions/spec-reviewer.md` (new, to be created).
- `.agents/llm-shared/skills/spec-reviewer/SKILL.md` (new, to be created).
- `.claude/skills/spec-reviewer/SKILL.md` (new, to be created).
- `tests/unit/tools/test_spec_reviewer_instruction/__init__.py` (new, to be created).
- `tests/unit/tools/test_spec_reviewer_instruction/test_spec_reviewer_instruction_tdd.py` (new, to be created).
- `tests/unit/tools/test_instruction_structure/test_spec_reviewer_adapters_tdd.py` (new, to be created).
- `tests/unit/tools/test_spec_review_requestor_instruction/test_spec_review_requestor_instruction_tdd.py` (existing, to be updated).

**Tests first**:

- assert status, wait-request, in-session reclaim, renderer, publish-answer, and
  stopped-state handling with exact policy and paths;
- assert no specification edit, consume, continue, confirm, complete, cancel,
  resolve, archive, transcript read, or cold-route reclaim authority;
- assert retained SHA-256 context revalidation and manifest removal only after
  successful republication;
- assert `.agent/workflows/spec-reviewer.md` uses the repository three-step
  locate body for workspace, sibling-clone, and submodule deployment;
- assert `.agents/llm-shared/instructions/spec-reviewer.md`,
  `.agents/llm-shared/skills/spec-reviewer/SKILL.md`, and
  `.claude/skills/spec-reviewer/SKILL.md` use their loader-relative canonical
  links rather than the workflow-host locate body;
- reuse the repaired requestor adapter assertions, including
  `test_workflow_wrapper_reuses_the_repository_locate_steps`, as the regression
  model while checking each host form independently;
- assert requestor `wait-answer` omits `--timeout-seconds`.

**Behavior**:

- canonical instruction owns orchestration and invokes the paired renderer plus
  shared exchange launchers;
- reviewer orchestration removes the retained-context manifest only after a
  successful shared `publish-answer` result; rendering or failed publication
  leaves the recovery evidence intact;
- the workflow wrapper owns only portable repository location, while Codex and
  Claude adapters own only loader-relative canonical links;
- convergence answers recommend but never confirm consolidation;
- the requestor retains all writer actions and full configured wait authority.

**Completion criteria**:

- `ghog single tests/unit/tools/test_spec_reviewer_instruction/test_spec_reviewer_instruction_tdd.py tests/unit/tools/test_instruction_structure/test_spec_reviewer_adapters_tdd.py tests/unit/tools/test_spec_review_requestor_instruction/test_spec_review_requestor_instruction_tdd.py` passes.
- `rg --line-number "wait-request|publish-answer|reclaim|convergence-recommended|timeout-seconds" instructions/spec-reviewer.md instructions/spec-review-requestor.md` confirms the boundary.
- `ghog day` reports `exit=0`.

#### Step 3 -- addendums for reviewer orchestration

Line-budget checkpoint:

- `instructions/spec-review-requestor.md`: baseline 162; non-Python; keep the
  timeout clarification narrow.
- `test_spec_review_requestor_instruction_tdd.py`: baseline 124; below-550 safe;
  ceiling 650; advisory final count 145.
- each new instruction or adapter test: baseline 0; below-550 safe; ceiling 650;
  advisory final count below 350.

Split guidance:

- Host adapters contain no copied orchestration. The workflow wrapper keeps its
  established three-step locate body; packaged Codex and Claude adapters keep
  their loader-relative form. If instruction tests approach the ceiling, split
  behavior and adapter structure by responsibility.

Full workflow timing run readiness:

- focused instruction and adapter tests, then `ghog day`.

Time-gated status for Step 3:

- The requestor uses the configured 1,800-second default when no marker override
  exists; focused tests must not perform that real wait.

---

### Step 4. Prove the complete specification reviewer workflow

#### Step 4 -- analysis and intent for reviewer acceptance

Issues to address:

- unit slices do not prove the public launchers and durable transitions together;
- recovery must reject stale retained content and retire current manifests;
- acceptance must demonstrate constant exact-path IO and every supported type.

Fix intent:

- drive routing, reviewer orchestration, rendering, and publication through
  public surfaces;
- separate lifecycle, recovery, and IO instrumentation into focused files;
- preserve all completed requestor and exchange-core behavior.

Expected outcome:

- round 1 and replacement rounds publish exactly once with matching transcripts;
- change requests return to the requestor and convergence reaches only its gate;
- interruption, reclaim, escalation, recovery, drift, and marker suspension are
  deterministic and evidence preserving.

Step framing:

- Design link: acceptance cases and publication/recovery design.
- Execution checklist: shared execution command checklist in this plan.

#### Step 4 -- implementation for reviewer acceptance

**Files involved**:

- `tests/unit/tools/test_spec_reviewer_acceptance/__init__.py` (new, to be created).
- `tests/unit/tools/test_spec_reviewer_acceptance/fixtures.py` (new, to be created).
- `tests/unit/tools/test_spec_reviewer_acceptance/test_spec_reviewer_acceptance_tdd.py` (new, to be created).
- `tests/unit/tools/test_spec_reviewer_acceptance/test_spec_reviewer_recovery_tdd.py` (new, to be created).
- `tests/unit/tools/test_spec_reviewer_acceptance/test_spec_reviewer_io_acceptance_tdd.py` (new, to be created).

**Tests first**:

- cover all four specification types, ordinary and explicit routing, marker
  suspension, ambiguous candidates, exact identity, both dispositions, human
  guidance, paired content, and transcript append;
- cover cold requestor reclaim, in-session reviewer reclaim, interrupted
  publication replay, stopped assessment retention, fresh-round drift, manifest
  retirement, escalation, and human-only recovery;
- instrument filesystem access to reject directory scans, transcript reads,
  stale scratch discovery, repeated input reads, and non-atomic publication.
- drive scenario matrices through public Python entry points and add one focused
  smoke test per `.bat` launcher rather than spawning a process per scenario.

**Behavior**:

- acceptance fixtures invoke `prompt_workflow.bat`, `spec_review_answer.bat`,
  and `review_exchange.bat` once each as adapter smoke coverage; scenario
  matrices use their public Python boundaries;
- package-local `fixtures.py` owns shared exact contexts, ignored inputs, and
  exchange setup without broadening repository-wide pytest configuration;
- no test mutates private exchange state merely to manufacture success;
- the final suite proves the feature request's acceptance criteria end to end.

**Completion criteria**:

- `ghog single tests/unit/tools/test_spec_reviewer_acceptance/test_spec_reviewer_acceptance_tdd.py tests/unit/tools/test_spec_reviewer_acceptance/test_spec_reviewer_recovery_tdd.py tests/unit/tools/test_spec_reviewer_acceptance/test_spec_reviewer_io_acceptance_tdd.py` passes.
- `rg --line-number "feature-request|issue|design-specification|plan|Human guidance:|SHA-256" tests/unit/tools/test_spec_reviewer_acceptance` finds the required scenario evidence.
- `ghog day` reports `exit=0` with the repository coverage gate satisfied.

#### Step 4 -- addendums for reviewer acceptance

Line-budget checkpoint:

- each new acceptance file: baseline 0; below-550 safe; ceiling 650;
  advisory final counts of 420-520 for lifecycle, 260-360 for recovery, and
  180-280 for IO instrumentation.
- `fixtures.py`: baseline 0; below-550 safe; ceiling 650; advisory final count
  120-220.

Split guidance:

- Keep lifecycle, recovery, and IO assertions separate. If any file approaches
  650 lines, split by disposition or recovery phase without duplicating fixtures.

Full workflow timing run readiness:

- focused acceptance files, then `ghog day` until the recorded objective is green.

Time-gated status for Step 4:

- Use short explicit test timeouts only in focused fixtures; production
  requestor behavior continues to use the full configured wait.
