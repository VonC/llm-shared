# v0.11.0 commit-plan-check implementation plan -- read-only readiness evidence

Implement one typed, read-only commit-plan check and use it as the shared
mechanical readiness floor for commit grouping and code review.

- **Shared inventory parity**: checking and committing consume the same exact
  staged-path inventory.
- **One checker contract**: the batch launcher and Python module render one
  immutable result with stable statuses and diagnostics.
- **Review enforcement**: request publication fails closed, while reviewers
  independently rerun the same command before assessing readiness.

> Markdown lint note: never leave a space immediately inside an inline code
> span (MD038); when a snippet starts or ends with a space, write that space as
> the literal token `[space]`. End any line that would be only italic text with
> a period after the closing underscore (MD036).

## Plan goal for v0.11.0 commit-plan checking

Implement the complete contract from
`docs/v0.11.0/design.v0.11.0.commit-plan-check.md` and its related feature
request in four ordered implementation steps.

- **Step 1 goal**: extract one public staged-inventory boundary and preserve
  exact batch-workflow behavior.
- **Step 2 goal**: add the immutable checker service, human and JSON renderers,
  Python CLI, and focused root launcher.
- **Step 3 goal**: enforce checker success and stable index identity before
  code-review request artifacts can be rendered.
- **Step 4 goal**: wire the canonical reviewer and grouping instructions and
  prove launcher parity, failure taxonomy, and repository immutability with
  acceptance tests.

No Step 0 timeout gate is required. This feature has no model call, network
wait, event loop, or background timing target; its performance contract is
bounded exact-file and Git-index IO. Step 4 provides the larger acceptance
coverage needed to prove that contract without an artificial time-based
`xfail`.

---

## Scope anchors for the v0.11.0 commit-plan-check plan

This plan implements the design from
`docs/v0.11.0/design.v0.11.0.commit-plan-check.md` and the confirmed rules in
`docs/v0.11.0/feature-request.v0.11.0.commit-plan-check.md`, targeting these
outcomes:

1. One shared staged inventory preserves `--no-renames` and NUL-delimited path
   semantics for both checking and committing.
2. One immutable checker result carries readiness state, typed groups, exact
   staged paths, and deterministic diagnostics to both output formats.
3. Code-review request rendering cannot publish unchecked or index-drifting
   evidence, and reviewer/grouping instructions use the same command.

The following are explicitly **in scope**:

- `commit-plan-check.bat` and `python -m tools.commit_plan_check` over one
  service function.
- Distinct ready, non-ready, and operational outcomes using statuses `0`, `3`,
  and `2`.
- Human and JSON projections of the same typed result.
- Requestor-side enforcement, reviewer-side independent checking, and grouped
  commit workflow use.
- Unit and acceptance evidence for successful, invalid, missing, empty,
  rename, operational-failure, index-drift, and no-mutation cases.

The following remain deferred beyond this effort:

- Repairing or rewriting `a.commit` from checker diagnostics.
- Mutation or commit flags on the checker.
- Support for `--root-a-commit --dry-run` in the committing launcher.
- Active-review status and interrupted-review resumption.
- Reviewer-specific staged-path filtering or worktree readiness rules.

---

## Complexity bound clarification for v0.11.0 commit-plan checking

- **O(1) amortized per path or group insertion**: new orchestration stores and
  projects parsed groups, staged paths, and diagnostics without nested
  membership scans.
- **O(n) total outside the reused validator**: root-plan parsing, NUL-delimited
  inventory decoding, result projection, and rendering are linear in plan
  content plus staged membership.
- **Existing mismatch reporting remains bounded**: the public validator may
  sort path differences for deterministic diagnostics, producing its existing
  `O(n log n)` invalid-result path; the checker must not add another sort or a
  nested pass.

There is no request-response hot path. No new code path may introduce
quadratic work, per-path subprocesses, or repeated parsing of the same plan.

---

## File-based IO cost clarification for v0.11.0 commit-plan checking

- Root discovery performs only a bounded parent lookup.
- Each checker call reads exactly `<root>/a.commit` once and runs the single
  shared Git index inventory once.
- Parsing, validation, and human or JSON rendering reuse one in-memory result;
  neither renderer scans files or reloads metadata.
- The requestor gate captures the index tree before and after the checker, then
  writes paired artifacts only after a ready result and identical trees.
- The checker itself performs no staging, reset, repair, evidence-file, or
  commit write.

The loading phase is therefore a tiny exact-plan and index-read operation, not
a documentation-tree or repository-file scan.

---

## Confirmed technical facts for v0.11.0 plan viability

Physical line counts include blank lines and use the same per-line iteration
metric as the repository big-file scan.

**Files over the 650-line repository planning limit**:

- None of the existing Python files planned for modification is over 650
  lines.

**Files in the 550-through-650 risk band**:

- `tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py`:
  **550 lines**. Limit changes to the shared source fixture and existing
  assertions; place checker-specific cases in a new focused test leaf.

**Files below 550 and safe to extend**:

- `tools/git_batch_commit_workflow.py`: **484 lines**; extracting inventory is
  expected to keep or reduce its size.
- `tests/unit/tools/test_git_batch_commit_workflow_process.py`: **353 lines**.
- `tools/code_review_request.py`: **497 lines**; keep checker orchestration and
  evidence wiring compact so the file remains below the 550 risk band when
  practical.
- `tests/unit/tools/test_code_reviewer_acceptance/fixtures.py`: **281 lines**.
- `tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_acceptance_tdd.py`:
  **362 lines**.
- `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py`:
  **479 lines**.
- `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py`:
  **281 lines**.
- `tests/unit/tools/test_code_reviewer_instruction/test_code_reviewer_instruction_tdd.py`:
  **118 lines**.
- `tests/unit/tools/test_group_commit_message_prompt_tdd.py`: **173 lines**.

**What does not exist yet**:

- `tools/commit_plan_support.py`.
- `tools/commit_plan_check.py`.
- `commit-plan-check.bat`.
- Focused unit leaves for commit-plan support, checker behavior, and
  code-review request checker integration.
- The commit-plan-check acceptance package and acceptance test leaf.

**Other confirmed facts affecting implementation**:

- `tools/git_batch_commit_validation.py` is 102 lines and already exports the
  side-effect-free `validate_commit_plan(blocks, staged_paths)` authority.
- `tools/git_batch_commit_models.py` is 151 lines and already owns immutable
  `CommitPlanGroup` and `CommitPlanValidation` values.
- `tools/git_batch_commit_git.py` is 479 lines and owns the cross-platform Git
  command wrapper used by the current inventory helper.
- `tools/git_batch_commit_workflow.py::_staged_paths` currently runs
  `git diff --cached --name-only --no-renames -z` but is not public.
- `tools/git_batch_commit_parsing.py::parse_clipboard_content` is public,
  exported in that module's `__all__`, and accepts content plus
  `interactive=False`; it is the parsing seam that preserves direct
  missing-file, empty-file, and unreadable-file classification in the checker.
- `tools/git_batch_commit_workflow.py::_read_and_parse_content` also accepts
  `interactive=False`, but it belongs to the committing workflow, includes
  clipboard and logging behavior, and collapses missing, empty, and read
  failures into `GitBatchCommitError`; it is not the read-only checker seam.
- `tools/code_review_request.py` already captures the request index tree and
  renders typed JSON and human evidence before writing paired artifacts.
- `markdown-check.bat` demonstrates the repository-root launcher pattern for a
  platform-neutral Python module.

---

## Current test-tree validation snapshot for v0.11.0 commit-plan checking

Existing test areas that must remain green:

- `tests/unit/tools/test_git_batch_commit_workflow_process.py` covers the
  current exact staged inventory and validator delegation.
- `tests/unit/tools/test_git_batch_commit_validation/` covers group ordering,
  conventional subjects, path normalization, duplicates, and exact membership.
- `tests/unit/tools/test_code_review_request/` covers typed code-review evidence
  and paired request rendering; its 550-line test file is already at risk.
- `tests/unit/tools/test_code_review_requestor_acceptance/` covers requestor
  rendering and publication-oriented IO boundaries.
- `tests/unit/tools/test_code_reviewer_acceptance/` covers the reviewer-facing
  request evidence flow.
- Canonical instruction contract tests cover `instructions/code-reviewer.md`
  and `instructions/group-commits-msg.md`.

New test leaf directories to create:

- `tests/unit/tools/test_commit_plan_support/`.
- `tests/unit/tools/test_commit_plan_check/`.
- `tests/unit/tools/test_code_review_request_commit_plan/`.
- `tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/`.

Property-based tests are not required. The feature has a finite failure
taxonomy and exact subprocess, path-order, status, and rendering contracts;
parameterized examples and real-repository acceptance fixtures provide the
stronger evidence. Existing validator tests continue to own path-rule breadth.

---

## Implementation decisions for v0.11.0 commit-plan checking

| Question | Decision | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | Start with one cohesive `tools/commit_plan_check.py`; split its CLI only if measured growth exceeds 650 lines | Step 2 file list and size addendum | Split service and CLI immediately; create a multi-module package |
| Q02 | Keep `git_batch_commit_workflow._staged_paths` as a thin delegate to the public staged inventory function | Step 1 compatibility and tests | Remove the seam immediately; retain separate Git calls |
| Q03 | Keep compact gate sequencing in `tools/code_review_request.py`, with render-path command ordering and `__post_init__` representability | Step 3 implementation and tests | Add a one-caller helper module; enforce only in the outer workflow |
| Q04 | Limit the existing 550-line rendering test to fixture and parity updates; put checker cases in the new leaf and supply the required result through the shared fixture | Step 3 test files and size guidance | Split the existing test first; add every checker case to it |
| Q05 | Keep acceptance helpers local until the file approaches 550 lines; if extracted, share them from `tests/acceptance/commit_plan_check/conftest.py` | Step 4 acceptance layout and split guidance | Create the shared fixture immediately; reuse unit fixtures |
| Q06 | Read exact `<root>/a.commit` in the checker and call public `git_batch_commit_parsing.parse_clipboard_content(content, interactive=False)` | Confirmed facts and Step 2 call order | Reuse the private workflow reader; move plan reading into staged-inventory support |
| Q07 | Require a typed checker result on `CodeReviewRoundInput` and reject non-ready evidence in `__post_init__` | Step 3 input contract and shared-fixture updates | Validate only in the outer render path; allow an optional result |

---

## Shared execution command checklist for all v0.11.0 commit-plan-check steps

Apply this checklist to every numbered step using its exact file list.

1. Count physical lines before edits for every step file.
2. Add or update the step's tests before production or instruction behavior.
3. Run `ghog single` on the exact affected test files.
4. Run the step-specific `rg` checks for public names, Git arguments, status
   mapping, evidence fields, or instruction wiring.
5. Run `ghog day` repeatedly until it reports the objective with `exit=0`.
6. Count physical lines after edits and compare every Python file with its
   baseline, policy band, advisory estimate, and 650-line ceiling.
7. If a Python file exceeds 650 lines, stop and apply the step's responsibility
   split before committing.
8. If a file exceeds only an advisory estimate while remaining at or below
   650, record the variance as evidence without failing the step.

## Ready-to-run commands for all v0.11.0 commit-plan-check steps

- Physical line count: `(Get-Content -LiteralPath '<path>').Count`
- Targeted tests: `ghog single <step-test-files>`
- Grep checks: `rg -n '<step-pattern>' <step-paths>`
- Shared gate loop: `ghog day`, repeated fix-and-walk until it reports the
  objective with `exit=0`

---

## Numbered implementation steps for v0.11.0 commit-plan checking

### Step 1. Share exact staged-path inventory with the committing workflow

#### Step 1 analysis and intent for staged inventory parity

Issues to address:

- Exact inventory is trapped in the private workflow helper
  `_staged_paths(root)`.
- A second implementation would risk diverging on NUL parsing, rename sides,
  deletions, whitespace, or path ordering.

Fix intent:

- Extract the existing Git invocation and decoding into one neutral public
  support function.
- Keep a compatibility delegate in the batch workflow where current imports
  and tests require it, while making both flows consume the public function.

Expected outcome:

- Batch validation and read-only checking receive identical repository-relative
  staged paths from the same implementation.
- The batch workflow's validation and commit behavior remains unchanged.

Step framing:

- Design link: “Shared staged inventory for commit-plan parity.”
- Complexity impact: one Git call and one linear NUL-delimited decode; no
  per-path filesystem checks.
- Feature preservation: existing root-plan validation, rename semantics, and
  commit execution stay intact.
- Execution checklist reference: “Shared execution command checklist for all
  v0.11.0 commit-plan-check steps” and its ready-to-run commands.

#### Step 1 implementation for staged inventory parity

**Files involved**:

- `tools/commit_plan_support.py` (new, to be created).
- `tools/git_batch_commit_workflow.py` (existing, to be updated).
- `tests/unit/tools/test_commit_plan_support/__init__.py` (new, to be created).
- `tests/unit/tools/test_commit_plan_support/test_commit_plan_support_tdd.py`
  (new, to be created).
- `tests/unit/tools/test_git_batch_commit_workflow_process.py` (existing, to be
  updated).

**Tests first**:

- Add focused tests that assert the exact Git argument tuple, repository root,
  capture/encoding options, NUL decoding, whitespace preservation, deletion
  membership, and two-path rename behavior.
- Update the workflow test to prove its compatibility helper delegates to the
  shared inventory and the public validator still receives that result.
- No PBT is needed; exact command and byte-decoding examples cover the bounded
  contract.

**Classes and behavior**:

- `staged_paths(root)`: run the existing cross-platform Git command exactly
  once and return the ordered nonempty path tuple.
- `git_batch_commit_workflow._staged_paths(root)`: remain a thin compatibility
  delegate with no inventory policy of its own.
- `_validate_commit_plan_for_root`: continue passing the shared inventory to
  the unchanged public validator before any mutation.

**Completion criteria**:

- `ghog day` reports the objective with `exit=0`.
- `rg -n "staged_paths|--no-renames|-z|validate_commit_plan" tools/commit_plan_support.py tools/git_batch_commit_workflow.py tests/unit/tools/test_commit_plan_support tests/unit/tools/test_git_batch_commit_workflow_process.py`
  shows one Git inventory implementation and explicit delegation coverage.
- Existing batch commit tests prove no commit-path behavior changed.

#### Step 1 addendums for staged inventory parity

Line-budget checkpoint:

- `tools/commit_plan_support.py`: before 0; below-550 safe; repository ceiling
  650; expected at or below 80 lines (advisory).
- `tools/git_batch_commit_workflow.py`: before 484; below-550 safe; repository
  ceiling 650; expected at or below 490 lines (advisory, with extraction
  expected to offset delegation changes).
- `tests/unit/tools/test_commit_plan_support/__init__.py`: before 0; below-550
  safe; repository ceiling 650; expected at or below 5 lines (advisory).
- `tests/unit/tools/test_commit_plan_support/test_commit_plan_support_tdd.py`:
  before 0; below-550 safe; repository ceiling 650; expected at or below 180
  lines (advisory).
- `tests/unit/tools/test_git_batch_commit_workflow_process.py`: before 353;
  below-550 safe; repository ceiling 650; expected at or below 370 lines
  (advisory).

Split guidance:

- If the new support module approaches the risk band, keep only Git inventory
  and decoding there; do not move parser, validator, renderer, or commit logic
  into it.
- If the workflow file would exceed 650, extract another existing workflow
  responsibility rather than growing the staged-inventory delegate.

Full workflow timing run readiness:

- `ghog single tests/unit/tools/test_commit_plan_support/test_commit_plan_support_tdd.py tests/unit/tools/test_git_batch_commit_workflow_process.py`
- `ghog day`

Time-gated status for Step 1:

- No Step 0 perf gate is affected; exact one-call inventory behavior is covered
  by focused assertions.

---

### Step 2. Expose one typed read-only checker through both entry points

#### Step 2 analysis and intent for checker evidence

Issues to address:

- No public command orchestrates exact root-plan parsing, shared staged
  inventory, and the existing validator without entering commit execution.
- Human reviewers and automation lack stable equivalent projections and the
  required `0`/`3`/`2` status taxonomy.

Fix intent:

- Add one immutable checker-specific result around the unchanged public
  validator result and input-state taxonomy.
- Run the service once per invocation, then select the human or JSON renderer.
- Add the root batch launcher and module CLI over the same `main` and service.

Expected outcome:

- Missing plan, empty plan, empty staged set, validator failures, and
  operational failures remain distinguishable.
- Both entry points emit identical ordered evidence without changing Git or
  repository files.

Step framing:

- Design links: “Read-only checker model for commit plans” and “Output
  contracts for commit-plan evidence.”
- Complexity impact: one exact plan read, one inventory call, one parse, one
  validation, and one projection per invocation.
- Feature preservation: the public validator model and committing launcher's
  incompatible root-plan dry-run behavior remain unchanged.
- Execution checklist reference: the shared execution checklist and
  ready-to-run commands in this document.

#### Step 2 implementation for checker evidence

**Files involved**:

- `tools/commit_plan_check.py` (new, to be created).
- `commit-plan-check.bat` (new, to be created).
- `tests/unit/tools/test_commit_plan_check/__init__.py` (new, to be created).
- `tests/unit/tools/test_commit_plan_check/test_commit_plan_check_tdd.py` (new,
  to be created).

**Tests first**:

- Parameterize ready, missing-plan, empty-plan, empty-staged-set, invalid-plan,
  unreadable-plan, Git failure, invalid argument, and unexpected-error cases.
- Assert `interactive=False`, exact use of `staged_paths` and
  `validate_commit_plan`, preservation of ordered typed groups and all
  diagnostics, deterministic human and JSON projections, stdout/stderr
  separation, and statuses `0`, `3`, and `2`.
- Assert the exact structured key set from the design: `schema_version` equal
  to `1`, `state`, `ready`, `staged_paths`, `groups` with `position`, `subject`,
  and `paths`, and `diagnostics`; expected non-readiness must emit this complete
  object to stdout before returning status `3`.
- Exercise `--root`, upward root discovery, default human format,
  `--format human|json`, module-main behavior, and root-launcher delegation.
- No PBT is needed; the finite state matrix is fully parameterized.

**Classes and behavior**:

- `CommitPlanCheckState`: enumerate the stable ready, expected non-ready, and
  operational states confirmed by the design.
- `CommitPlanCheckResult`: immutable groups, diagnostics, staged paths, state,
  and derived readiness with a structured payload projection.
- `check_commit_plan(root)`: resolve `<root>/a.commit`; return `missing-plan`
  when it is absent; read it exactly once and return `empty-plan` when content
  is empty or whitespace; otherwise parse through public
  `parse_clipboard_content(content, interactive=False)`, inventory once, call
  the public validator once, and return typed evidence without writing.
- Human and JSON renderers: project the same result deterministically and keep
  expected non-readiness on stdout.
- `main(argv)`: validate arguments, resolve the root, map result or operational
  failure to the documented stream and status contract.
- `commit-plan-check.bat`: resolve the llm-shared Python environment, run
  `python -m tools.commit_plan_check`, and preserve its exit status.

**Completion criteria**:

- `ghog day` reports the objective with `exit=0`.
- `rg -n "CommitPlanCheck|check_commit_plan|interactive=False|--format|schema_version|return 3|return 2" tools/commit_plan_check.py commit-plan-check.bat tests/unit/tools/test_commit_plan_check`
  confirms the service, projections, and adapter mappings.
- Focused tests prove the service never calls reset, add, rm, commit, or a file
  writer.

#### Step 2 addendums for checker evidence

Line-budget checkpoint:

- `tools/commit_plan_check.py`: before 0; below-550 safe; repository ceiling
  650; expected at or below 360 lines (advisory). The exact plan read and
  missing/empty/unreadable discrimination may exceed this advisory estimate;
  record the variance as evidence rather than treating it as a defect while
  the measured file remains at or below 650.
- `commit-plan-check.bat`: before 0; non-Python launcher; Python ceiling not
  applicable; expected at or below 35 physical lines (advisory).
- `tests/unit/tools/test_commit_plan_check/__init__.py`: before 0; below-550
  safe; repository ceiling 650; expected at or below 5 lines (advisory).
- `tests/unit/tools/test_commit_plan_check/test_commit_plan_check_tdd.py`:
  before 0; below-550 safe; repository ceiling 650; expected at or below 420
  lines (advisory).

Split guidance:

- If `tools/commit_plan_check.py` would exceed 650, split CLI parsing and stream
  rendering into `tools/commit_plan_check_cli.py`, leaving states, result, and
  service orchestration in the original module.
- If the unit test approaches 550, extract launcher and adapter cases into a
  sibling conventional test leaf before adding more cases.

Full workflow timing run readiness:

- `ghog single tests/unit/tools/test_commit_plan_check/test_commit_plan_check_tdd.py`
- `ghog day`

Time-gated status for Step 2:

- No timeout `xfail` is introduced. Focused tests assert bounded call counts;
  Step 4 measures behavior in real temporary repositories.

---

### Step 3. Enforce commit-plan readiness before code-review request rendering

#### Step 3 analysis and intent for requestor publication enforcement

Issues to address:

- Request rendering captures index identity but does not run the authoritative
  commit-plan checker.
- The request evidence cannot prove that its groups and diagnostics describe
  the same index tree that the request publishes.

Fix intent:

- Capture the index tree, run the shared checker, capture the tree again, and
  reject non-ready results or tree drift before rendering or writes.
- Carry the complete structured checker result in the typed code-review
  evidence and derive the human summary from the same value.

Expected outcome:

- Canonical requestor rendering creates neither paired artifact when the plan
  is non-ready, the checker fails operationally, or the index changes.
- Ready request content binds checker evidence, validation commands, and one
  stable request index tree.

Step framing:

- Design link: “Enforced requestor publication gate.”
- Complexity impact: two index-tree captures around one checker invocation;
  rendering remains one in-memory projection.
- Feature preservation: shared exchange publication stays role-neutral, direct
  protocol bypass remains documented, and existing paired-write validation is
  retained.
- Execution checklist reference: the shared execution checklist and
  ready-to-run commands in this document.

#### Step 3 implementation for requestor publication enforcement

**Files involved**:

- `tools/code_review_request.py` (existing, to be updated).
- `tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_code_review_request_commit_plan/__init__.py` (new, to
  be created).
- `tests/unit/tools/test_code_review_request_commit_plan/test_code_review_request_commit_plan_tdd.py`
  (new, to be created).
- `tests/unit/tools/test_code_reviewer_acceptance/fixtures.py` (existing, to be
  updated).
- `tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_acceptance_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py`
  (existing, to be updated).

**Tests first**:

- Extend shared request builders with one typed valid checker result and assert
  its full payload and human summary are paired.
- Supply the new required result through the shared fixture used by the six
  existing keyword-based `CodeReviewRoundInput(` construction sites, limiting
  the 550-line rendering test to one fixture-level compatibility change.
- Add focused tests for status-three non-readiness, operational failure,
  before/after index drift, exactly one checker call, complete evidence, and no
  output creation on every rejected path.
- Retain existing tests for distinct inputs and outputs, validation-set
  resolution, envelope identity, and successful paired writes.
- No PBT is needed; typed boundary and failure-order cases are finite.

**Classes and behavior**:

- `CodeReviewRoundInput`: require one typed commit-plan result alongside the
  stable request index tree and resolved validation set; `__post_init__` must
  reject a non-ready result so the public renderer cannot construct request
  content with invalid checker evidence.
- `_CodeReviewEvidence`: include the full structured checker payload and
  derive a quotable summary without reparsing JSON.
- `_render_from_arguments`: capture tree A, run `check_commit_plan`, require a
  ready result, capture tree B, require A equals B, build typed input, render,
  and only then write both outputs. This render path owns command order;
  `CodeReviewRoundInput.__post_init__` owns the separate representability
  invariant for direct public renderer use.
- Existing `render_code_review_request`: continue validating the envelope and
  paired content from a single typed source.

**Completion criteria**:

- `ghog day` reports the objective with `exit=0`.
- `rg -n "commit_plan|check_commit_plan|request_index_tree|capture_index_tree|ready" tools/code_review_request.py tests/unit/tools/test_code_review_request tests/unit/tools/test_code_review_request_commit_plan tests/unit/tools/test_code_reviewer_acceptance tests/unit/tools/test_code_review_requestor_acceptance`
  shows typed evidence, enforcement order, and rejection coverage.
- Every non-ready, operational, or drift case proves that neither output file
  exists or changes.

#### Step 3 addendums for requestor publication enforcement

Line-budget checkpoint:

- `tools/code_review_request.py`: before 497; below-550 safe; repository ceiling
  650; expected at or below 545 lines (advisory). If it enters the risk band,
  avoid further growth and keep checker policy in `tools/commit_plan_check.py`.
- `tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py`:
  before 550; 550-through-650 risk; repository ceiling 650; expected at or
  below 560 lines (advisory). Add only shared fixture/evidence alignment here.
- `tests/unit/tools/test_code_review_request_commit_plan/__init__.py`: before 0;
  below-550 safe; repository ceiling 650; expected at or below 5 lines
  (advisory).
- `tests/unit/tools/test_code_review_request_commit_plan/test_code_review_request_commit_plan_tdd.py`:
  before 0; below-550 safe; repository ceiling 650; expected at or below 260
  lines (advisory).
- `tests/unit/tools/test_code_reviewer_acceptance/fixtures.py`: before 281;
  below-550 safe; repository ceiling 650; expected at or below 290 lines
  (advisory).
- `tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_acceptance_tdd.py`:
  before 362; below-550 safe; repository ceiling 650; expected at or below 375
  lines (advisory).
- `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py`:
  before 479; below-550 safe; repository ceiling 650; expected at or below 500
  lines (advisory).
- `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py`:
  before 281; below-550 safe; repository ceiling 650; expected at or below 300
  lines (advisory).

Split guidance:

- Keep new checker-specific request tests in their dedicated leaf. Do not grow
  the existing 550-line rendering test beyond shared fixture compatibility and
  evidence-parity assertions.
- If `tools/code_review_request.py` exceeds 650, extract only commit-plan gate
  sequencing and typed evidence conversion to a focused requestor helper;
  leave envelope and paired rendering in the existing module.

Full workflow timing run readiness:

- `ghog single tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py tests/unit/tools/test_code_review_request_commit_plan/test_code_review_request_commit_plan_tdd.py tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_acceptance_tdd.py tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py`
- `ghog day`

Time-gated status for Step 3:

- No timeout gate is affected. Call-order tests prove bounded index capture and
  checker use before any writes.

---

### Step 4. Roll out shared review guidance and acceptance evidence

#### Step 4 analysis and intent for repository-wide adoption

Issues to address:

- Reviewer instructions currently assess `a.commit` without naming the shipped
  read-only command.
- Grouped-commit guidance reaches the committing batch path without an earlier
  shared read-only readiness result.
- Unit isolation alone cannot prove launcher parity and full Git-state
  immutability in real repositories.

Fix intent:

- Require the code reviewer to rerun the checker and record its mechanical
  evidence without treating success as commit authority.
- Require grouped-commit preparation to run the checker after formatting and
  staging, repairing status-three diagnostics before presenting commit choices.
- Add real-repository acceptance tests for both entry points, all important
  readiness states, rename membership, requestor rejection, and before/after
  state equality.

Expected outcome:

- Requestors, reviewers, and grouped-commit execution share one readiness floor
  while preserving their distinct authority boundaries.
- Successful and failing checker calls demonstrably leave `HEAD`, index,
  worktree, `a.commit`, and ignored-root inventory unchanged.

Step framing:

- Design links: “Independent reviewer readiness check,” “Grouping workflow use
  of the checker,” and “Acceptance cases.”
- Complexity impact: acceptance fixtures use bounded temporary repositories;
  production guidance adds one explicit checker call, not a scan or poll loop.
- Feature preservation: a ready result never authorizes a commit, and the final
  batch workflow still validates again before mutation.
- Execution checklist reference: the shared execution checklist and
  ready-to-run commands in this document.

#### Step 4 implementation for repository-wide adoption

**Files involved**:

- `instructions/code-reviewer.md` (existing, to be updated).
- `instructions/group-commits-msg.md` (existing, to be updated).
- `tests/unit/tools/test_code_reviewer_instruction/test_code_reviewer_instruction_tdd.py`
  (existing, to be updated).
- `tests/unit/tools/test_group_commit_message_prompt_tdd.py` (existing, to be
  updated).
- `tests/acceptance/commit_plan_check/__init__.py` (new, to be created).
- `tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/__init__.py`
  (new, to be created).
- `tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_acceptance_tdd.py`
  (new, to be created).

**Tests first**:

- Extend instruction contract tests to require the focused launcher, its
  readiness-only meaning, status-three repair behavior, independent reviewer
  rerun, and the prohibition on deriving commit authority from status zero.
- Build temporary Git repositories that run the batch and module entry points
  against valid, missing-plan, empty-plan, empty-staged-set, mismatched, and
  renamed inputs and compare human/JSON evidence and statuses.
- Cover an unreadable plan or failed Git inventory as an operational failure
  with a stable stderr diagnostic and status `2` across both entry points.
- Redirect stdout into a caller-owned ignored root `a.*` evidence file and
  prove the checker remains read-only while the caller owns that write.
- Capture `HEAD`, index tree, staged paths, tracked worktree diff,
  `a.commit` bytes, and ignored root `a.*` inventory before and after valid and
  invalid calls.
- Exercise requestor rendering with invalid checker evidence and index drift to
  confirm no paired artifacts are written.
- No PBT is needed; these are cross-boundary acceptance scenarios with exact
  expected state snapshots.

**Classes and behavior**:

- `instructions/code-reviewer.md`: place `commit-plan-check.bat` in the six-part
  readiness floor, require an independent rerun, and distinguish mechanical
  success from assessment and commit authority.
- `instructions/group-commits-msg.md`: run the read-only checker after canonical
  formatting and staging, repair non-ready diagnostics, then retain the
  authorized committing batch path as the final defensive validation.
- Acceptance fixtures: create deterministic temporary repositories and compare
  complete before/after state snapshots around both adapters.

**Completion criteria**:

- `ghog day` reports the objective with `exit=0`.
- `rg -n "commit-plan-check|status|readiness|never authorizes|independent" instructions/code-reviewer.md instructions/group-commits-msg.md tests/unit/tools/test_code_reviewer_instruction tests/unit/tools/test_group_commit_message_prompt_tdd.py tests/acceptance/commit_plan_check`
  confirms the shared command and authority wording.
- Acceptance tests prove identical service evidence across entry points and
  exact repository-state preservation for successful and failing calls.
- The full feature request acceptance criteria are covered by unit or
  acceptance evidence without invoking commit execution.

#### Step 4 addendums for repository-wide adoption

Line-budget checkpoint:

- `instructions/code-reviewer.md`: before 209; non-Python Markdown; Python
  ceiling not applicable; expected at or below 225 physical lines (advisory).
- `instructions/group-commits-msg.md`: before 119; non-Python Markdown; Python
  ceiling not applicable; expected at or below 135 physical lines (advisory).
- `tests/unit/tools/test_code_reviewer_instruction/test_code_reviewer_instruction_tdd.py`:
  before 118; below-550 safe; repository ceiling 650; expected at or below 145
  lines (advisory).
- `tests/unit/tools/test_group_commit_message_prompt_tdd.py`: before 173;
  below-550 safe; repository ceiling 650; expected at or below 205 lines
  (advisory).
- `tests/acceptance/commit_plan_check/__init__.py`: before 0; below-550 safe;
  repository ceiling 650; expected at or below 5 lines (advisory).
- `tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/__init__.py`:
  before 0; below-550 safe; repository ceiling 650; expected at or below 5
  lines (advisory).
- `tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_acceptance_tdd.py`:
  before 0; below-550 safe; repository ceiling 650; expected at or below 380
  lines (advisory).

Split guidance:

- If the acceptance test approaches 550 lines, extract repository-state setup
  and snapshot helpers into `tests/acceptance/commit_plan_check/conftest.py`,
  leaving scenarios in the conventional test leaf. The parent-package
  placement is deliberate so later sibling acceptance leaves can share the
  helpers, even though current repository conftests are leaf-level.
- Keep instruction changes limited to command use and authority boundaries;
  do not copy checker implementation details into Markdown.

Full workflow timing run readiness:

- `ghog single tests/unit/tools/test_code_reviewer_instruction/test_code_reviewer_instruction_tdd.py tests/unit/tools/test_group_commit_message_prompt_tdd.py tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_acceptance_tdd.py`
- `ghog day`

Time-gated status for Step 4:

- No timeout `xfail` is removed. Acceptance evidence records bounded command
  completion through groundhog and proves IO call counts and state equality.
