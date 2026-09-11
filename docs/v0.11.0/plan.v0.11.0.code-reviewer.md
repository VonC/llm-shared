# v0.11.0 code-reviewer implementation plan -- staged review responder

Implement the responder in six dependency-ordered slices, with each extension to a completed surface carrying its own focused tests.

- **Immutable request evidence**: publish the exact index tree and resolved validation set.
- **Safe assessment primitives**: record and compare executable evidence, validate `a.commit`, and then bound `implementation-check` writes through that evidence boundary.
- **Independent responder**: render typed answers, route the reviewer, and prove recovery through acceptance tests.

## Plan goal for v0.11.0 code-reviewer

Implement the full responder described in `design.v0.11.0.code-reviewer.md` and `feature-request.v0.11.0.code-reviewer.md` without granting commit or exchange-owner authority.

- **Step 1 goal**: extend code-review requests with immutable staged-state and validation-set evidence.
- **Step 2 goal**: add the executable Git evidence, manifest, and shared commit-plan validation boundary.
- **Step 3 goal**: enforce reviewer-mode `implementation-check` through the Step 2 evidence boundary.
- **Step 4 goal**: add the discriminated code-review answer renderer and its paired-output launcher.
- **Step 5 goal**: expose the canonical reviewer role and exact pending-request routing.
- **Step 6 goal**: prove repair, early rejection, recovery, publication, and authority boundaries in acceptance tests.

No Step 0 performance gate is required. The responder is a bounded local workflow, and the owning steps test exact-path access, no directory enumeration, and linear work over explicit files.

---

## Implementation decisions for v0.11.0 code-reviewer

| Question | Decision | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | Expose the evidence library through a typed CLI and `bin/code_review_evidence.bat`. | New production surfaces and Steps 1, 2, and 6 | Library-only access or Git command prose in the reviewer instruction |
| Q02 | Validate parsed `CommitBlock` values with explicit staged paths through `validate_commit_plan(blocks, staged_paths)`. | Step 2 commit validation | Hidden Git IO in validation or subprocess-only validation |
| Q03 | Render one fenced JSON object under `## Code review evidence` and derive its summary from the same typed object. | Step 1 request evidence | Free-form Markdown fields or a separate retained evidence artifact |
| Q04 | Resolve a typed `CodeReviewActor` once and require `CodeReviewRoute.actor` to agree with classified state. | Step 5 routing | Repeated state switches or parallel route dataclasses |
| Q05 | Use six focused steps, separating evidence and commit validation from reviewer-mode `implementation-check`. | Plan goals, numbered steps, and validation plan | One broad assessment step or moving reviewer mode into routing |
| Q06 | Test public Python entry points over real temporary Git repositories, with one smoke invocation per launcher. | Step 6 acceptance | Launcher subprocesses for every case or fully mocked repository state |
| Q07 | Put capture, comparison, attribution, and retained-manifest operations behind one typed evidence boundary. | Steps 2, 3, and 5 | Prose-managed checks or several helpers with separate state models |
| Q08 | Create capture-only `code_review_evidence.py` in Step 1, then extend the same module in Step 2. | Steps 1 and 2 file ownership and line budgets | Duplicate capture implementations or step renumbering |
| Q09 | Declare each validation command and its artifact paths in one tab-separated project, plan, or request entry; carry merged paths as `artifacts`, and report omissions as declaration defects. | Step 1 validation resolution and Step 3 validation scope | An entry-only artifact field without declaration ownership, or repository-wide artifact discovery |
| Q10 | Let the reviewer retire retained evidence only after answer publication; bind retained evidence to its round and exchange occurrence and refuse stale reads. | Step 2 retained evidence and Steps 4–6 publication recovery | Retirement during implementation-check or by the requestor after answer consumption |
| Q11 | Test instruction structure with identifiers read from the registered Step 2 CLI subcommands and reuse Step 2 behavior tests plus Step 6 acceptance journeys. | Step 3 reviewer-mode tests and Step 6 acceptance | A test-only prose interpreter or a new production assessment service |
| Q12 | Compare the complete staged set from the immutable request-time index and use `Files involved` only for attribution. | Step 3 validation path-set construction | Bounding scope to `Files involved` or carrying a second authored staged inventory |

---

## Scope anchors for v0.11.0 code-reviewer plan

This plan implements the consolidated design beside this document. It targets:

1. one exact reviewer route for one pending code-family request;
2. bounded repair and validation of the staged plan step;
3. separately validated early-rejection and assessment answers;
4. advisory `changes-requested` or `commit-ready` publication without commit authority.

In scope:

- request payload changes in the completed requestor renderer, template, and instruction;
- shared validation resolution, index evidence, manifest recovery, and `a.commit` validation;
- reviewer assessment mode in `implementation-check`;
- code-review answer model, CLI, template, launcher, canonical instruction, host adapters, and routing;
- unit, property-oriented boundary, and temporary-repository acceptance tests.

Deferred:

- requestor round continuation, human confirmation, and batch commit execution;
- shared exchange naming, locking, timeout, transcript append, and escalation mechanics;
- general review-mode user documentation assigned to the later umbrella item.

---

## Complexity bound for v0.11.0 code-reviewer

- **O(1) path derivation per round**: derive every protocol and retained-evidence path from the exact exchange identity and step.
- **O(n) per assessment phase**: process only explicit request bytes, staged paths, repair paths, validation commands, and `a.commit` groups.
- **No repository-wide selection scan**: routing and recovery never enumerate nearby request, answer, transcript, or manifest files.
- **No nested comparison over the repository**: overlap and validation-state checks compare explicit path sets and content snapshots.

Any implementation that adds directory discovery or repeated full-file reads on the response path is incomplete.

---

## File-based IO cost clarification for v0.11.0 code-reviewer

- Read the exact request, plan, validation plan, `a.commit`, and retained manifest by derived path.
- Read caller-authored answer inputs once and write the answer and transcript summary as one validated pair.
- Record pre-repair content only for files the reviewer may touch; compare validation state only for explicit tracked and ignored differences.
- Write one stable ignored manifest atomically and retire it only after `publish-answer` reports `outcome: published`.
- Do not scan the project root for `a.*` artifacts or nearby plans.

---

## Confirmed technical facts for v0.11.0 plan viability

Existing production Python files below 550 lines and safe to extend:

- `tools/code_review_request.py`: 382 lines; repository ceiling 650.
- `tools/prompt_workflow_code_review.py`: 246 lines; repository ceiling 650.
- `tools/git_batch_commit_models.py`: 127 lines; repository ceiling 650.
- `tools/git_batch_commit_workflow.py`: 462 lines; repository ceiling 650.

Existing production Python files in the 550-through-650 risk band:

- `tools/prompt_workflow_skill.py`: 583 lines; keep code-family decisions in `prompt_workflow_code_review.py` and add only the dispatcher constant and forced-route branch here.

Existing tests below 550 lines:

- `tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py`: 437 lines.
- `tests/unit/tools/test_code_review_requestor_instruction/test_code_review_requestor_instruction_tdd.py`: 151 lines.
- `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py`: 426 lines.
- `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py`: 254 lines.
- `tests/unit/tools/test_git_batch_commit_workflow_process.py`: 259 lines.
- `tests/unit/tools/test_prompt_workflow_code_review/test_prompt_workflow_code_review_tdd.py`: 383 lines.
- `tests/unit/tools/test_instruction_structure/test_instruction_structure_tdd.py`: 543 lines; add a new code-reviewer adapter test file instead of growing this file.

Existing tests in the 550-through-650 risk band:

- `tests/unit/tools/test_prompt_workflow_skill/test_prompt_workflow_skill_tdd.py`: 614 lines; add a dedicated code-reviewer route test file and do not grow this file.

Existing non-Python surfaces and physical line counts:

- `instructions/code-review-requestor.md`: 147 lines.
- `instructions/implementation-check.md`: 103 lines.
- `templates/code-review-request.template.md`: 38 lines.

New production surfaces, all with baseline 0 lines:

- `tools/code_review_validation.py`.
- `tools/code_review_evidence.py`.
- `tools/code_review_evidence_cli.py` and `bin/code_review_evidence.bat`.
- `tools/git_batch_commit_validation.py`.
- `tools/code_review_answer.py` and `tools/code_review_answer_cli.py`.
- `templates/code-review-answer.template.md` and `bin/code_review_answer.bat`.
- `instructions/code-reviewer.md` and the `.agent`, `.agents`, and `.claude` adapters.

The typed parser already exists in `tools/git_batch_commit_parsing.py` at 438 lines and remains the parser source; the new validator lives beside it rather than growing the parser.

---

## Current test-tree validation snapshot for v0.11.0 code-reviewer

Existing packages to preserve:

- `tests/unit/tools/test_code_review_request/` covers typed request rendering and CLI IO.
- `tests/unit/tools/test_code_review_requestor_acceptance/` covers requestor publication and shared transition behavior.
- `tests/unit/tools/test_prompt_workflow_code_review/` covers exact plan-step routing and authorized commit continuation.
- `tests/unit/tools/test_git_batch_commit_*` covers parser and batch execution behavior.
- `tests/unit/tools/test_spec_review_answer/` and `test_spec_reviewer_acceptance/` provide the paired-answer reference behavior.

New test leaf directories:

- `tests/unit/tools/test_code_review_validation/`.
- `tests/unit/tools/test_code_review_evidence/`.
- `tests/unit/tools/test_git_batch_commit_validation/`.
- `tests/unit/tools/test_implementation_check_reviewer_mode/`.
- `tests/unit/tools/test_code_review_answer/`.
- `tests/unit/tools/test_code_reviewer_instruction/`.
- `tests/unit/tools/test_code_reviewer_acceptance/`.

Each new leaf contains `__init__.py` and a matching `test_*_tdd.py`; the evidence and answer leaves each add a second `test_*_cli_tdd.py` for their CLI-heavy cases. Property-oriented cases belong beside the unit tests only when generated path-set or shape combinations add coverage beyond explicit examples.

---

## Shared execution command checklist for all v0.11.0 code-reviewer steps

Apply this checklist to every numbered step.

1. Count physical lines for every existing and new step file before edits.
2. Add or update the step's tests first.
3. Run `ghog single` for the affected test files.
4. Run the step-specific `rg` checks.
5. Run `ghog day` repeatedly until it reports the project objective.
6. Count physical lines after edits and compare each Python file with the 650-line ceiling.
7. Split a Python file before commit if it exceeds 650 lines.
8. Record advisory estimate variance without failing a file that remains at or below 650 lines.

## Ready-to-run command templates for all v0.11.0 code-reviewer steps

- Line count: `[System.IO.File]::ReadAllLines((Resolve-Path -LiteralPath '<path>')).Count`
- Focused tests: `ghog single <step test files>`
- Grep checks: `rg -n '<step invariant>' <step files>`
- Shared gate: `ghog day`, repeated fix-and-walk until `exit=0`

---

## Numbered steps for v0.11.0 code-reviewer

### Step 1. Publish immutable request evidence

#### Step 1 -- analysis and intent for request evidence

Issues to address:

- Code-family requests do not carry the request-time index tree.
- Requestor and reviewer do not share one typed resolved validation set with
  command sources and declared artifact paths.

Fix intent:

- Add one resolver for project defaults plus plan and request additions. Parse
  every non-comment declaration as tab-separated command and
  repository-relative artifact-path fields, merge artifact paths with source
  labels, and reject malformed or escaping paths.
- Capture the Git index tree at publication and render both evidence fields in the complete request and paired summary.
- Put the authored evidence object under a distinct `## Code review evidence` heading so it cannot be confused with the shared envelope's `## JSON` section.

Expected outcome:

- A code-family request from v0.11.0 cannot be rendered without the exact tree and validation-set evidence.
- Existing requestor publication tests cover the completed surface being extended.

Step framing:

- Design links: design Q01 authoritative snapshot and design Q04 validation-set resolution.
- Execution checklist: shared execution command checklist in this plan.

#### Step 1 -- implementation for request evidence

Files involved:

- `tools/code_review_evidence.py` (new, to be created with index-tree capture only).
- `tools/code_review_validation.py` (new, to be created).
- `tools/code_review_request.py` (existing, to be updated).
- `templates/code-review-request.template.md` (existing, to be updated).
- `instructions/code-review-requestor.md` (existing, to be updated).
- `tests/unit/tools/test_code_review_validation/__init__.py` (new, to be created).
- `tests/unit/tools/test_code_review_validation/test_code_review_validation_tdd.py` (new, to be created).
- `tests/unit/tools/test_code_review_evidence/__init__.py` (new, to be created).
- `tests/unit/tools/test_code_review_evidence/test_code_review_evidence_tdd.py` (new, to be created with index-tree capture cases).
- `tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py` (existing, to be updated).
- `tests/unit/tools/test_code_review_requestor_instruction/test_code_review_requestor_instruction_tdd.py` (existing, to be updated).
- `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py` (existing, to be updated).
- `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py` (existing, to be updated).

Tests first:

- Use small temporary Git repositories to prove the shared helper captures the Git tree object of the index without inspecting the worktree.
- Cover default preservation, additive plan/request checks, tab-separated
  declaration parsing, repository-relative artifact validation, source labels,
  deterministic command-and-artifact ordering, and resolver drift inputs.
- Reject a missing or malformed tree object and require both new fields in request and summary.
- Round-trip a request carrying both `## JSON` and `## Code review evidence` through the shared envelope parser unchanged.
- Prove each caller input is read once and output pairing remains atomic.

Classes and behavior:

- `capture_index_tree`: the single requestor-and-reviewer implementation of Git index-tree capture, introduced before the first request publication consumer.
- `ResolvedValidationSet`: immutable commands plus their project, plan, or
  request sources and the merged `artifacts` list for each command.
- `resolve_code_review_validation`: combine tab-separated project, plan, and
  request declarations without allowing a default removal; keep the first-seen
  ordered union of repository-relative artifact paths.
- `CodeReviewRoundInput`: receive `request_index_tree` from `capture_index_tree` rather than computing it, require the tree and `resolved_validation_set`, render their canonical fenced JSON object under `## Code review evidence`, derive the human-readable summary from the same object, and preserve the shared envelope unchanged.

Completion criteria:

- `ghog day` reports `exit=0`.
- `rg -n 'capture_index_tree|Code review evidence|request_index_tree|resolved_validation_set|artifacts' tools/code_review_evidence.py tools/code_review_validation.py tools/code_review_request.py templates/code-review-request.template.md instructions/code-review-requestor.md` finds the single capture helper, distinct authored heading, both evidence fields, and the declared artifact payload.
- Requestor acceptance tests publish the exact evidence without changing shared exchange mechanics.

#### Step 1 -- addendums for request evidence

Line-budget checkpoint:

- `tools/code_review_request.py`: before 382; below-550 safe; ceiling 650; expected final count below 470 (advisory).
- `tools/code_review_evidence.py`: before 0; below-550 safe; ceiling 650; expected Step 1 final count below 80 (advisory).
- `tools/code_review_validation.py`: before 0; below-550 safe; ceiling 650; expected final count below 220 after the Q09 declaration-parse and payload additions (advisory).
- `test_code_review_request_tdd.py`: before 437; below-550 safe; ceiling 650; expected final count below 525 (advisory).
- Other Step 1 Python tests: before 151, 426, and 254; below-550 safe; ceiling 650; keep focused additions in place and move broad combinations to the new validation leaf.

Split guidance:

- If request rendering approaches 650 lines, extract CLI path validation from `tools/code_review_request.py`; keep the typed renderer and CLI entry stable.

Full workflow timing run readiness:

- `ghog single tests/unit/tools/test_code_review_evidence/test_code_review_evidence_tdd.py tests/unit/tools/test_code_review_validation tests/unit/tools/test_code_review_request tests/unit/tools/test_code_review_requestor_acceptance`; then `ghog day`.

Time-gated status for Step 1:

- No timeout gate; exact-path and read-once assertions are deterministic.

---

### Step 2. Add executable Git evidence and commit validation

#### Step 2 -- analysis and intent for executable assessment evidence

Issues to address:

- Reviewer-only repair patches need recorded pre-repair content and retained assessed-tree identity.
- Umbrella and validation-state comparisons must be executable checks rather than prose instructions.
- `a.commit` has a parser but no side-effect-free validator shared with batch execution.

Fix intent:

- Add exact-path Git evidence, comparison, attribution, and stable manifest helpers behind one non-interactive launcher. Retain the writing round number and exchange occurrence and refuse a manifest that does not match the current request.
- Add a typed commit-plan validator and call it from the existing batch workflow.
- Make every evidence operation callable by the later canonical reviewer instruction without composing Git commands in Markdown.

Expected outcome:

- Index snapshots, recovery, patch attribution, umbrella mutation, validation side effects, and manifest lifecycle are machine-checkable through `bin/code_review_evidence.bat`.
- Commit-plan decisions are side-effect-free and shared by the reviewer and batch execution.

Step framing:

- Design links: design Q02 repair attribution, design Q03 umbrella-digest enforcement mechanism, design Q05 retained evidence, design Q07 `a.commit` validation interface, and design Q08 validation side effects.
- Plan decision links: Q01 option A2, Q02 option B2, and Q07 option G2.
- Execution checklist: shared execution command checklist in this plan.

#### Step 2 -- implementation for executable assessment evidence

Files involved:

- `tools/code_review_evidence.py` (existing after Step 1, to be extended).
- `tools/code_review_evidence_cli.py` (new, to be created).
- `bin/code_review_evidence.bat` (new, to be created).
- `tools/git_batch_commit_validation.py` (new, to be created).
- `tools/git_batch_commit_models.py` (existing, to be updated).
- `tools/git_batch_commit_workflow.py` (existing, to be updated).
- `tests/unit/tools/test_code_review_evidence/__init__.py` (existing after Step 1).
- `tests/unit/tools/test_code_review_evidence/test_code_review_evidence_tdd.py` (existing after Step 1, to be extended).
- `tests/unit/tools/test_code_review_evidence/test_code_review_evidence_cli_tdd.py` (new, to be created).
- `tests/unit/tools/test_git_batch_commit_validation/__init__.py` (new, to be created).
- `tests/unit/tools/test_git_batch_commit_validation/test_git_batch_commit_validation_tdd.py` (new, to be created).
- `tests/unit/tools/test_git_batch_commit_workflow_process.py` (existing, to be updated).

Tests first:

- Use temporary Git repositories to extend the Step 1 capture cases with pre-repair blobs, created and writer-deleted files, reviewer-only patch attribution, drift, stable manifest write/read/retirement, stale round or exchange refusal, and next-round overwrite.
- Execute `umbrella_digest` capture and comparison for unchanged and changed pass/fail workflow outcomes, including the explicit not-applicable result for `Umbrella draft: none`.
- Execute validation-state capture and comparison around ignored-only and tracked-file differences without reverting or laundering command artifacts into reviewer repairs.
- Validate staged membership, group order, and conventional subjects from `CommitBlock` values through `validate_commit_plan(blocks, staged_paths)` after `interactive=False` parsing.
- Prove batch execution calls the same validator and the CLI rejects mixed identities, unsafe paths, or malformed retained evidence.

Classes and behavior:

- `CodeReviewEvidence`: baseline and assessed index tree objects, recorded blobs, repair paths, validation state, round number, exchange occurrence, and identity-derived manifest serialization.
- `CodeReviewEvidenceCli`: typed subcommands for index-tree capture, pre-repair blob recording, reviewer-only patch attribution, `umbrella_digest` capture/compare, validation-state capture/compare, and manifest write/read/retire; `read-manifest` receives the current round and exchange occurrence and refuses a mismatch.
- `CommitPlanValidation`: typed groups and diagnostics without staging or commit side effects; `validate_commit_plan(blocks, staged_paths)` is the public validation API.

Completion criteria:

- `ghog day` reports `exit=0`.
- `rg -n 'interactive=False|umbrella_digest|validation_state|round_number|exchange_occurrence|retire_manifest' tools/code_review_evidence.py tools/code_review_evidence_cli.py tools/git_batch_commit_validation.py tests/unit/tools/test_code_review_evidence tests/unit/tools/test_git_batch_commit_validation` finds executable implementations, retained request identity, and tests rather than documentation-only phrases.
- Existing batch commit tests still pass with the shared validator in the commit path.
- The launcher works from a repository root without environment setup.

#### Step 2 -- addendums for executable assessment evidence

Line-budget checkpoint:

- `tools/code_review_evidence.py`: before the recorded Step 1 final count (expected below 80); below-550 safe; ceiling 650; expected Step 2 final count below 360 (advisory).
- `tools/code_review_evidence_cli.py`: before 0; below-550 safe; ceiling 650; expected final count below 280 (advisory).
- `bin/code_review_evidence.bat`: before 0; non-Python launcher kept thin and delegated to the CLI.
- `tools/git_batch_commit_validation.py`: before 0; below-550 safe; ceiling 650; expected final count below 220 (advisory).
- `tools/git_batch_commit_models.py`: before 127; below-550 safe; ceiling 650; small typed-result addition expected.
- `tools/git_batch_commit_workflow.py`: before 462; below-550 safe; ceiling 650; expected final count below 500 (advisory).
- `test_git_batch_commit_workflow_process.py`: before 259; below-550 safe; ceiling 650.
- New test modules: before 0; below-550 safe; ceiling 650; split fixture support if either evidence test module approaches 550.

Split guidance:

- Keep typed snapshots, comparisons, attribution, and manifests in `code_review_evidence.py`; keep argument and path validation in `code_review_evidence_cli.py`; keep batch-plan rules in `git_batch_commit_validation.py`. Do not grow the 438-line parser with validator behavior.

Full workflow timing run readiness:

- `ghog single tests/unit/tools/test_code_review_evidence tests/unit/tools/test_git_batch_commit_validation tests/unit/tools/test_git_batch_commit_workflow_process.py`; then `ghog day`.

Time-gated status for Step 2:

- No timeout gate; temporary-repository cases must remain bounded to explicit small fixtures.

---

### Step 3. Enforce reviewer-mode implementation checks

#### Step 3 -- analysis and intent for reviewer-mode checks

Issues to address:

- The canonical implementation check currently owns umbrella completion writes that an advisory reviewer must not perform.
- A Markdown instruction can require calls to an executable boundary, but it cannot itself prove umbrella or validation-state comparisons.

Fix intent:

- Add an explicit reviewer assessment mode to the canonical implementation-check instruction.
- Require that mode to call the Step 2 evidence launcher before and after either the criteria pass or fail path.
- Require each validation-state capture to name the complete staged set from
  the immutable request-time index plus every declared validation-artifact
  path, so tracked differences cannot fall outside the compared scope. Use the
  plan step's `Files involved` list only to explain attribution.
- Permit writes only to validation-plan rows for the reviewed step and treat any detected umbrella mutation as a `changes-requested` finding that leaves the changed file in place.

Expected outcome:

- Reviewer mode delegates every machine comparison to named evidence commands and never marks the umbrella effort complete.
- `Umbrella draft: none` records the digest check as not applicable instead of inventing a path.

Step framing:

- Design links: design Q03 enforceable reviewer mode, design Q08 validation side effects, and the umbrella-status acceptance case.
- Plan decision link: Q07 option G2.
- Execution checklist: shared execution command checklist in this plan.

#### Step 3 -- implementation for reviewer-mode checks

Files involved:

- `instructions/implementation-check.md` (existing, to be updated).
- `tests/unit/tools/test_implementation_check_reviewer_mode/__init__.py` (new, to be created).
- `tests/unit/tools/test_implementation_check_reviewer_mode/test_implementation_check_reviewer_mode_tdd.py` (new, to be created).

Tests first:

- Assert the canonical instruction names the evidence launcher's `umbrella-digest` capture/compare operations on both criteria result paths.
- Assert it names validation-state capture/compare, pre-repair blob capture, patch attribution, and manifest lifecycle commands rather than describing equivalent shell operations.
- Assert both result paths build the validation-state scope from the complete
  request-time staged set and every declared validation-artifact path before
  capture.
- Cover the reviewed-step validation-row exemption, forbidden umbrella completion writes, changed-file retention, and `Umbrella draft: none` handling.
- Reuse Step 2 executable tests as the proof that pass-path and fail-path mutation and validation side effects are actually detected.

Classes and behavior:

- Reviewer assessment mode: an explicit canonical mode that delegates executable evidence work to `bin/code_review_evidence.bat`, permits only reviewed-step validation-row writes, and reports any other tracked difference.
- Canonical command contract: instruction tests take command identifiers such as `umbrella-digest` and `validation-state` from the Step 2 CLI's registered subcommand names, require the complete request-time staged set plus the declared validation-artifact paths, treat `Files involved` as attribution only, and use helper tests to prove command behavior.

Completion criteria:

- `ghog day` reports `exit=0`.
- `rg -n 'code_review_evidence.bat|umbrella-digest|validation-state' instructions/implementation-check.md tests/unit/tools/test_implementation_check_reviewer_mode` finds the exact delegation boundary and both result paths.
- Existing implementation-check behavior outside reviewer assessment mode remains unchanged.

#### Step 3 -- addendums for reviewer-mode checks

Line-budget checkpoint:

- `instructions/implementation-check.md`: before 103; non-Python instruction remains canonical and concise.
- New reviewer-mode test module: before 0; below-550 safe; ceiling 650.

Split guidance:

- Keep executable Git and filesystem evidence in Step 2 modules; do not duplicate evidence algorithms in the instruction or its structure tests.

Full workflow timing run readiness:

- `ghog single tests/unit/tools/test_implementation_check_reviewer_mode tests/unit/tools/test_code_review_evidence`; then `ghog day`.

Time-gated status for Step 3:

- No timeout gate; instruction and helper boundary checks are deterministic.

---

### Step 4. Build paired code-review answers

#### Step 4 -- analysis and intent for answer rendering

Issues to address:

- No code-family answer model, template, CLI, or launcher exists.
- Early rejection and full assessment require different mandatory evidence shapes.

Fix intent:

- Compose the shared envelope and IO checks with a code-specific discriminated union.
- Produce complete answer content and transcript summary from one validated source.

Expected outcome:

- Mixed early-rejection and assessment evidence fails before rendering.
- Paired outputs carry exact identity, repair, validation, guidance, and advisory decision content.

Step framing:

- Design links: design Q06 paired renderer and the two typed answer shapes.
- Execution checklist: shared execution command checklist in this plan.

#### Step 4 -- implementation for answer rendering

Files involved:

- `tools/code_review_answer.py` (new, to be created).
- `tools/code_review_answer_cli.py` (new, to be created).
- `templates/code-review-answer.template.md` (new, to be created).
- `bin/code_review_answer.bat` (new, to be created).
- `tests/unit/tools/test_code_review_answer/__init__.py` (new, to be created).
- `tests/unit/tools/test_code_review_answer/test_code_review_answer_tdd.py` (new, to be created).
- `tests/unit/tools/test_code_review_answer/test_code_review_answer_cli_tdd.py` (new, to be created).

Tests first:

- Cover valid early-rejection and assessment inputs plus every prohibited mixture and missing mandatory field.
- Cover identity fields exactly once, human guidance pairing, pre-repair validation labels, repair inventory, resolver drift, and final advisory disposition.
- Cover ignored-root input validation, single reads, distinct paths, paired writes, partial-write cleanup, and stable fatal exit 2.

Classes and behavior:

- `EarlyRejectionAssessment` and `ImplementationAssessment`: the two validated input variants.
- `CodeReviewAnswerRender`: complete answer plus substantive transcript summary.
- CLI: validate the live manifest and assessed index when assessment evidence is supplied; retire the manifest only after publication, as directed by the reviewer workflow rather than during rendering.

Completion criteria:

- `ghog day` reports `exit=0`.
- `rg -n 'EarlyRejection|ImplementationAssessment|answer_content|transcript_summary' tools/code_review_answer.py tools/code_review_answer_cli.py` finds the typed pair.
- The launcher works from a repository root without environment setup.

#### Step 4 -- addendums for answer rendering

Line-budget checkpoint:

- `tools/code_review_answer.py`: before 0; below-550 safe; ceiling 650; expected final count below 380 (advisory).
- `tools/code_review_answer_cli.py`: before 0; below-550 safe; ceiling 650; expected final count below 380 (advisory).
- Each new answer test module: before 0; below-550 safe; ceiling 650; keep model and CLI tests separate.

Split guidance:

- Keep rendering/model validation in `code_review_answer.py` and filesystem/CLI validation in `code_review_answer_cli.py`; extract shared review-answer IO only if both specification and code responders can adopt it without role-invalid optional fields.

Full workflow timing run readiness:

- `ghog single tests/unit/tools/test_code_review_answer`; then `ghog day`.

Time-gated status for Step 4:

- No timeout gate; atomic failure cases use deterministic local files.

---

### Step 5. Route and instruct the independent reviewer

#### Step 5 -- analysis and intent for reviewer orchestration

Issues to address:

- `pw` routes every live code exchange to the requestor and has no forced reviewer role.
- No canonical reviewer instruction or host adapter exposes the allowed responder operations and recovery rules.

Fix intent:

- Route one exact `request-pending` code exchange or its intact `abandoned-request` form to `code-reviewer`; keep writer-owned and stopped states requestor-owned.
- Add the canonical instruction and thin host adapters after request, evidence, validator, and answer surfaces exist.

Expected outcome:

- Ordinary and forced routing agree, including cold abandoned-request behavior.
- The reviewer can wait, assess, repair, render, and publish, but cannot consume, continue, confirm, complete, escalate, cancel, or commit.

Step framing:

- Design links: exact routing, fixed policy, human guidance, publication, and recovery sections.
- Execution checklist: shared execution command checklist in this plan.

#### Step 5 -- implementation for reviewer orchestration

Files involved:

- `tools/prompt_workflow_code_review.py` (existing, to be updated).
- `tools/prompt_workflow_skill.py` (existing, to be updated).
- `instructions/code-reviewer.md` (new, to be created).
- `.agent/workflows/code-reviewer.md` (new, to be created).
- `.agents/llm-shared/instructions/code-reviewer.md` (new, to be created).
- `.agents/llm-shared/skills/code-reviewer/SKILL.md` (new, to be created).
- `.claude/skills/code-reviewer/SKILL.md` (new, to be created).
- `tests/unit/tools/test_code_reviewer_instruction/__init__.py` (new, to be created).
- `tests/unit/tools/test_code_reviewer_instruction/test_code_reviewer_instruction_tdd.py` (new, to be created).
- `tests/unit/tools/test_prompt_workflow_code_review/test_prompt_workflow_code_review_tdd.py` (existing, to be updated).
- `tests/unit/tools/test_prompt_workflow_skill/test_prompt_workflow_skill_code_reviewer_tdd.py` (new, to be created).
- `tests/unit/tools/test_instruction_structure/test_code_reviewer_adapters_tdd.py` (new, to be created).

Tests first:

- Cover `request-pending` and `abandoned-request` reviewer routing, requestor routing for every writer-owned or stopped state, forced-role identity checks, and one guarded cold abandoned-request reclaim.
- Cover typed actor resolution once from state and reject any `CodeReviewRoute` whose actor and classified state disagree.
- In `test_code_reviewer_instruction_tdd.py`, assert the canonical reviewer instruction names `bin/code_review_evidence.bat` for baseline capture, pre-repair blobs, patch attribution, validation-state comparison, and manifest write/read/retire, and names `bin/code_review_answer.bat` for paired rendering instead of describing equivalent Git or filesystem operations.
- Cover canonical policy, exact answer-path reads, one bounded wait, manifest lifecycle, early rejection, repair staging, validation side effects, publication exits 0 and 3, and forbidden operations.
- Prove every host adapter links only to the canonical instruction and copies no policy.

Classes and behavior:

- `CODE_REVIEWER`: role constant used for exact pending and intact abandoned request states.
- `CodeReviewActor`: typed reviewer-or-requestor actor resolved once from the classified state.
- `CodeReviewRoute.actor`: required typed field with a construction-time consistency check against the route state.
- `command_for_route`: consume the resolved actor without repeating the state partition or scanning.
- Canonical instruction: a thin ordered caller that delegates executable evidence to `bin/code_review_evidence.bat`, paired rendering to `bin/code_review_answer.bat`, and protocol operations to `bin/review_exchange.bat`; it owns only sequence, recovery, guidance, and publication decisions.

Completion criteria:

- `ghog day` reports `exit=0`.
- `rg -n 'code-reviewer|REQUEST_PENDING|ABANDONED_REQUEST|CODE_REVIEWER' tools/prompt_workflow_code_review.py tools/prompt_workflow_skill.py instructions/code-reviewer.md` finds routing and canonical ownership.
- `rg -n 'code_review_evidence.bat|code_review_answer.bat|review_exchange.bat' instructions/code-reviewer.md` finds the delegated evidence, rendering, and protocol boundaries.
- Forced and ordinary Codex/Claude commands render the expected host prefix and exact plan step.

#### Step 5 -- addendums for reviewer orchestration

Line-budget checkpoint:

- `tools/prompt_workflow_code_review.py`: before 246; below-550 safe; ceiling 650; expected final count below 310 (advisory).
- `tools/prompt_workflow_skill.py`: before 583; 550-through-650 risk; ceiling 650; add only constant and dispatcher branch, expected final count below 600 (advisory).
- Existing route test: before 383; below-550 safe; ceiling 650; expected final count below 500 (advisory).
- New canonical-instruction test module: before 0; below-550 safe; ceiling 650; keep content assertions separate from adapter-linkage assertions.
- New skill-route and adapter test files: before 0; below-550 safe; ceiling 650.

Split guidance:

- If `prompt_workflow_skill.py` would exceed 650, move forced code-review role selection into `prompt_workflow_code_review.py`; do not add another family-specific branch cluster to the dispatcher.

Full workflow timing run readiness:

- `ghog single tests/unit/tools/test_code_reviewer_instruction tests/unit/tools/test_prompt_workflow_code_review tests/unit/tools/test_prompt_workflow_skill/test_prompt_workflow_skill_code_reviewer_tdd.py tests/unit/tools/test_instruction_structure/test_code_reviewer_adapters_tdd.py`; then `ghog day`.

Time-gated status for Step 5:

- No timeout gate; routing tests classify fixture states synchronously.

---

### Step 6. Prove responder acceptance and recovery

#### Step 6 -- analysis and intent for end-to-end acceptance

Issues to address:

- Unit slices do not by themselves prove that request, assessment, repair, answer, publication, recovery, and authority boundaries compose.
- The final step must cover real Git index behavior and both answer publication exits.

Fix intent:

- Add temporary-repository acceptance fixtures that call the real renderers, evidence helpers, shared exchange CLI, and Git validator.
- Cover all sixteen design acceptance cases and the requirement's eight acceptance criteria.

Expected outcome:

- A pending request can reach `changes-requested` or `convergence-gate` with exact transcript and artifact behavior.
- Repair, drift, missing evidence, guidance, recovery, and forbidden authority are checked through observable repository state.

Step framing:

- Design links: acceptance cases and publication/recovery sections.
- Execution checklist: shared execution command checklist in this plan.

#### Step 6 -- implementation for end-to-end acceptance

Files involved:

- `tests/unit/tools/test_code_reviewer_acceptance/__init__.py` (new, to be created).
- `tests/unit/tools/test_code_reviewer_acceptance/fixtures.py` (new, to be created).
- `tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_acceptance_tdd.py` (new, to be created).
- `tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_recovery_tdd.py` (new, to be created).
- `tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_io_acceptance_tdd.py` (new, to be created).
- `tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_launcher_smoke_tdd.py` (new, to be created).
- Steps 1 through 5 production files (existing after prior steps, to be updated only for acceptance defects).

Tests first:

- Build small real Git repositories with staged, unstaged, ignored, repaired, and validation-generated files.
- Smoke `bin/code_review_request.bat`, `bin/code_review_evidence.bat`, and `bin/code_review_answer.bat` once each to catch launcher argument drift while keeping scenario coverage on public Python APIs.
- Cover four early-rejection triggers, safe and unsafe repair attribution, umbrella digest mutation, validation union/drift, ignored versus tracked command artifacts, repeated missing evidence, guidance, manifest reclaim, interrupted publication replay, and exit-3 retirement.
- Assert the reviewer never calls or gains consume, continue, confirm, complete, escalate, cancel, batch commit, or umbrella completion authority.

Classes and behavior:

- Acceptance fixtures create exact plans, validation plans, requests, manifests, and staged trees without scanning test roots.
- Tests use real `ReviewExchangeCore` transitions at public launcher seams and mock only external command duration where needed.

Completion criteria:

- `ghog day` reports `exit=0` with the project coverage gate.
- Acceptance journeys assert both answer paths and the durable publication outcomes: convergence-gate advisory state, a published outcome, and CLI exit 3.
- Every design acceptance case has a named test or parametrized case id.

#### Step 6 -- addendums for end-to-end acceptance

Line-budget checkpoint:

- `fixtures.py`: before 0; below-550 safe; ceiling 650; expected final count below 320 (advisory).
- Each acceptance test module: before 0; below-550 safe; ceiling 650; split by assessment, recovery, and IO responsibility from the outset.
- Launcher smoke test: before 0; below-550 safe; ceiling 650; keep it to one invocation per launcher.
- Any production file reopened for an acceptance defect keeps its earlier step ceiling and split guidance.

Split guidance:

- Keep reusable repository construction in `fixtures.py`; do not combine acceptance, recovery, and IO cases into one large test module.

Full workflow timing run readiness:

- `ghog single tests/unit/tools/test_code_reviewer_acceptance`; then `ghog day`.

Time-gated status for Step 6:

- No persistent timeout marker; bounded-wait cases use configured short fixture deadlines and deterministic state transitions.
