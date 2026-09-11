# v0.11.0 commit-plan-check implementation tracking and validation

Yes, it is implemented.

This validation records the completed four-step implementation of read-only
commit-plan readiness evidence and its review-workflow adoption.

---

## File-based IO cost clarification for v0.11.0 commit-plan checking (implementation)

All implementation work must preserve the IO classification established in
`docs/v0.11.0/plan.v0.11.0.commit-plan-check.md`:

- read `<root>/a.commit` exactly once per checker call;
- obtain staged membership through one shared Git index command;
- reuse one in-memory typed result for validation and rendering; and
- perform no checker-owned repository writes or per-path file scans.

---

## Complexity bound clarification for v0.11.0 commit-plan checking (implementation)

- New orchestration remains linear in plan content and staged membership.
- Per-path and per-group accumulation remains `O(1)` amortized.
- The existing validator's deterministic mismatch sorting is not duplicated.
- No step introduces quadratic work, repeated parsing, or per-path
  subprocesses.

Every implemented step must be reviewed against these bounds in its
performance check.

---

## Step 1. Share exact staged-path inventory with the committing workflow

### Analysis of Step 1 implementation state

Yes. Step 1 has been fully implemented.

The exact staged-path inventory now has one public implementation, the batch
workflow preserves its private compatibility seam through delegation, and the
focused and global verification evidence covers the complete planned contract.

### Goal for Step 1

Extract the exact staged-path inventory into one public support boundary and
make the committing workflow delegate without changing its behavior.

### Step 1 improvement expectations

- One Git invocation owns `--cached --name-only --no-renames -z` semantics.
- Batch validation and the future checker receive the same ordered path tuple.
- Existing batch validation and commit execution remain unchanged.

### What was implemented for Step 1

- **Shared inventory boundary**: `tools/commit_plan_support.py` owns the exact
  `git diff --cached --name-only --no-renames -z` invocation and returns the
  ordered nonempty NUL-decoded path tuple.
- **Batch compatibility**: `git_batch_commit_workflow._staged_paths(root)` now
  delegates directly to `commit_plan_support.staged_paths(root)`, while
  `_validate_commit_plan_for_root` continues to pass that result to the
  unchanged public validator before mutation.
- **Focused verification**: the new support tests pin the Git arguments, root,
  capture and encoding options, whitespace preservation, deletion membership,
  both rename sides, order, and empty-segment handling. The updated workflow
  test proves the compatibility helper returns the public result unchanged.
- **Repository gate evidence**: the final forced `ghog day --force` bypassed
  the cached green no-op and completed with
  `fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0`.

### New types or classes introduced for Step 1

- `commit_plan_support.staged_paths(root)`: public read-only function for exact
  staged membership shared by committing and checking workflows.
- `test_commit_plan_support_tdd.py`: focused test suite for the subprocess and
  NUL-decoding boundary.

No new production class or domain type was needed; the step is a function
extraction with compatibility wiring.

### Architecture check for Step 1

- **Boundary direction**: the neutral support module depends only on the
  existing cross-platform Git command adapter. The committing workflow depends
  on that support boundary and no reverse dependency exists.
- **Responsibility placement**: Git inventory and decoding remain together;
  parser, validator, rendering, and commit execution responsibilities were not
  moved into the support module.
- **File girth**: the new support module is 38 lines, the workflow is 481 lines,
  the focused test is 135 lines, and the updated workflow test is 347 lines,
  all within their advisory budgets and the 650-line ceiling.

No, there is nothing that needs to be addressed for Step 1.

### Performance check for Step 1

`staged_paths(root)` performs exactly one Git subprocess call and one linear
split-and-filter pass over its NUL-delimited output. It adds no per-path file
probe, nested scan, sorting, O(n log n) work, or O(n^2) work.

No, there is no performance issue that needs to be addressed for Step 1.

### Unit test coverage check for Step 1

- **`commit_plan_support.staged_paths`**: focused tests execute the sole Git
  seam, nonempty and empty decoding branches, whitespace paths, deletions, and
  two-sided rename membership; the global coverage gate reports 100%.
- **Batch delegate and validator wiring**: existing and updated workflow tests
  cover delegation, successful validation input, diagnostics, and unchanged
  commit control flow.

No, there is no unit-tested class below 100% that needs completing for Step 1.

### Feature integrity for Step 1

- **Existing batch behavior**: the public validator still receives the same
  ordered tuple through `_staged_paths`, and commit execution remains unchanged.
- **Rename and deletion reporting**: `--no-renames` continues to expose both
  rename sides, while deleted worktree paths remain exact staged members.
- **Regression evidence**: all 2,010 full-suite tests pass with no warning,
  expected failure, coverage gap, or duration outlier.

No existing feature or reporting capability appears impaired by Step 1.

---

## Step 2. Expose one typed read-only checker through both entry points

### Analysis of Step 2 implementation state

Yes. Step 2 has been fully implemented.

The checker now exposes one immutable service result through deterministic
human and JSON projections, a platform-neutral module CLI, and a focused root
launcher while preserving the required read-only and status contracts.

### Goal for Step 2

Add the immutable checker service, equivalent human and JSON evidence, stable
status mapping, Python CLI, and focused root launcher without repository
mutation.

### Step 2 improvement expectations

- One service call distinguishes ready, expected non-ready, and operational
  outcomes.
- Human and JSON output preserve the same groups, paths, and diagnostics.
- Both entry points share one service and return statuses `0`, `3`, and `2`.

### What was implemented for Step 2

- **Typed checker service**: `tools/commit_plan_check.py` defines the six stable
  result states and one immutable result carrying ordered groups, staged paths,
  diagnostics, and derived readiness.
- **Shared orchestration**: `check_commit_plan(root)` reads only the canonical
  root `a.commit`, parses with `interactive=False`, inventories staged paths
  through `commit_plan_support.staged_paths`, and delegates exact membership
  rules to `validate_commit_plan`.
- **Equivalent evidence**: the human and compact JSON renderers project the
  same in-memory result, including the exact versioned structured key set,
  ordered groups, ordered paths, and complete diagnostics.
- **Command boundaries**: `main(argv)` supports upward root discovery,
  `--root`, and `--format human|json`, with statuses `0`, `3`, and `2` mapped to
  the required stdout and stderr contracts. `commit-plan-check.bat` runs the
  same module without changing the caller's working directory and preserves
  its status, including status `2` for launcher bootstrap failure.
- **Focused verification**: 21 parameterized and boundary tests cover ready,
  missing, empty, empty-staged, malformed, invalid, unreadable, Git failure,
  invalid invocation, unexpected failure, both projections, module execution,
  root discovery, and executable module-to-launcher parity from a foreign Git
  working directory.
- **Repository gate evidence**: the final detached `ghog day` completed with
  all 2,039 tests passing and
  `fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0`.

### New types or classes introduced for Step 2

- `CommitPlanCheckState`: string enumeration for `valid`, `missing-plan`,
  `empty-plan`, `empty-staged-set`, `invalid-plan`, and
  `operational-failure`.
- `CommitPlanCheckResult`: frozen evidence value containing the state, ordered
  typed groups, ordered diagnostics, and exact staged paths, with derived
  readiness and the versioned structured projection.
- `_ArgumentParser` and `_InvocationError`: narrow command-adapter types that
  convert invalid arguments into the stable status-two contract without
  terminating imported callers.

### Architecture check for Step 2

- **Dependency direction**: the command adapter depends on the neutral staged
  inventory boundary, existing parser, existing validation API, and shared root
  discovery. None of those boundaries depends back on the checker.
- **Responsibility separation**: the service returns data without writing
  streams; renderers only project the result; the CLI alone owns stream and
  status mapping; the batch launcher only selects Python and delegates.
- **Mutation boundary**: production imports and service calls contain no Git
  reset, add, remove, commit, or file-writing operation. The only repository
  file access is the exact root plan read and the shared read-only index query.
- **File girth**: the Python checker is 247 lines, the batch launcher is 27
  lines, the package marker is 2 lines, the focused service test is 453 lines,
  and the split adapter test is 131 lines. The service test exceeds its
  420-line advisory estimate by 33 lines; this recorded variance remains below
  the 550-line split-risk threshold and the 650-line repository ceiling, while
  executable adapter coverage has been extracted into its own conventional
  test leaf.

No, there is nothing that needs to be addressed for Step 2.

### Performance check for Step 2

Each nonempty checker call performs one exact plan read, one parser pass, one
shared staged-inventory subprocess, one validator call, and one selected
projection. Accumulation is linear in groups and paths; it adds no per-path
file probes, repeated scans, duplicated sorting, O(n log n) work, or O(n^2)
work beyond the unchanged validator behavior.

No, there is no performance issue that needs to be addressed for Step 2.

### Unit test coverage check for Step 2

- **Checker states and service seams**: focused unit tests cover every stable
  state, exact collaborator arguments and call counts, ordered evidence, parser
  failure, operational boundaries, and derived readiness.
- **Renderers and CLI**: focused unit tests cover the exact structured schema,
  deterministic human evidence, both format paths, every status/stream class,
  invalid arguments, explicit and discovered roots, unexpected failure, and
  the module main guard.
- **Launcher**: the focused adapter test executes both entry points from the
  same temporary Git repository, with `PRJ_DIR` cleared, and proves identical
  JSON evidence and status while the launcher preserves the caller's working
  directory.
- **Coverage evidence**: the repository Groundhog gate reports 100% coverage
  for all affected production statements.

No, there is no unit-tested class below 100% that needs completing for Step 2.

### Feature integrity for Step 2

- **Existing validator authority**: group, subject, command, duplicate, and
  membership rules remain in `validate_commit_plan`; the checker wraps its
  typed result without changing it.
- **Existing commit execution**: the committing launcher and its incompatible
  root-plan dry-run behavior are unchanged, and no commit-side API is imported
  by the checker.
- **Evidence parity**: expected non-readiness emits complete evidence on stdout
  before status `3`, while operational inability emits a stable diagnostic on
  stderr with status `2`.
- **Regression evidence**: the complete suite passes with no warning, expected
  failure, coverage gap, or duration outlier.

No existing feature or reporting capability appears impaired by Step 2.

---

## Step 3. Enforce commit-plan readiness before code-review request rendering

### Analysis of Step 3 implementation state

Yes. Step 3 has been fully implemented.

The specialized renderer now requires ready typed commit-plan evidence, binds
it to one stable index tree, and rejects every planned failure class before
writing either request artifact. Focused tests and the complete repository gate
cover the new contract.

### Goal for Step 3

Require a ready checker result and identical before/after index trees before
the specialized code-review renderer writes paired request artifacts.

### Step 3 improvement expectations

- Non-ready, operational, and index-drift outcomes produce no request outputs.
- The request carries the full structured checker result beside the stable
  request index tree and validation set.
- Human and JSON evidence derive from the same typed source.

### What was implemented for Step 3

- **Typed request input**: `CodeReviewRoundInput` now requires one
  `CommitPlanCheckResult` and rejects untyped or non-ready evidence in its
  representability invariant.
- **Paired evidence**: `_CodeReviewEvidence` carries the full versioned
  structured checker payload beside `request_index_tree` and
  `resolved_validation_set`; its human summary projects the same in-memory
  result through the shared human renderer inside a Markdown-safe text fence.
- **Publication gate**: `_render_from_arguments` captures tree A, calls
  `check_commit_plan(root)` exactly once, rejects non-ready or operational
  results, captures tree B, rejects drift, and only then renders and writes the
  paired outputs.
- **Compatibility wiring**: existing renderer, reviewer acceptance, and
  requestor acceptance builders now supply typed ready evidence without
  changing their exchange behavior.
- **Focused verification**: the new commit-plan request leaf covers direct
  typed-boundary rejection, exact call order, one checker invocation, complete
  JSON and human evidence, non-readiness, operational failure, index drift,
  preservation of both pre-existing outputs on every rejected path, and
  literal dunder paths inside the human evidence fence.
- **Repository gate evidence**: the final detached `ghog day` completed with
  `fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0`.

### New types or classes introduced for Step 3

No new production class was introduced. Step 3 extends the existing frozen
`CodeReviewRoundInput` and `_CodeReviewEvidence` types, and adds three focused
helpers:

- `_validate_authored_inputs`: keeps authored-field checks outside the input
  type's branch count.
- `_validate_request_evidence`: owns exact tree, validation-set, and ready
  checker-result invariants used by `CodeReviewRoundInput.__post_init__`.
- `_ready_commit_plan`: maps the shared checker result to stable request-gate
  rejection diagnostics.
- `test_code_review_request_commit_plan_tdd.py`: a dedicated Step 3 test leaf
  for commit-plan gate sequencing and failure boundaries.

### Architecture check for Step 3

- **Dependency direction**: the specialized code-review adapter depends on the
  read-only checker service and shared evidence types. The checker and
  role-neutral exchange core do not depend back on request rendering.
- **Responsibility boundary**: `check_commit_plan` retains parsing, inventory,
  and validation policy. The request adapter only orders the check around index
  identity and projects the returned typed value.
- **Write boundary**: all plan and tree checks finish before the existing two
  `_write_utf8` calls. Direct role-neutral publication remains unchanged, so
  the design's documented specialized-renderer boundary is preserved.
- **File girth**: `tools/code_review_request.py` is 559 lines, 14 above its
  545-line advisory and below the 650-line split trigger. The existing renderer
  test is 568 lines, eight above its 560-line advisory and below the same
  ceiling; checker-specific cases stay in the 241-line dedicated leaf. All
  other touched test files remain inside their Step 3 advisory estimates.

No, there is nothing that needs to be addressed for Step 3.

### Performance check for Step 3

Each command call adds two constant-count index-tree captures around exactly one
checker call. The checker remains linear in plan content and staged membership,
and both evidence renderings traverse the already-built typed groups, paths,
commands, and diagnostics once. No per-path subprocess, repeated parse,
duplicated sort, O(n log n) path, or O(n^2) path was added.

No, there is no performance issue that needs to be addressed for Step 3.

### Unit test coverage check for Step 3

- **Typed input and evidence projections**: unit tests cover typed and ready
  invariants plus exact full-payload parity between request JSON and the human
  transcript summary.
- **Command gate**: focused unit tests cover matching captures, exactly one
  checker call, successful paired writes, status-three non-readiness,
  operational failure, index drift, and unchanged outputs on rejection.
- **Existing rendering and IO**: the prior unit leaf continues to cover exact
  envelope identity, validation-set resolution, distinct ignored paths,
  one-read/one-write behavior, malformed inputs, and stable fatal errors.
- **Coverage evidence**: the complete Groundhog gate reports 100% coverage for
  all affected production statements.

No, there is no unit-tested class below 100% that needs completing for Step 3.

### Feature integrity for Step 3

- **Existing exchange behavior**: shared publication, envelope validation,
  transcript rendering, and durable exchange transitions remain unchanged.
- **Validation evidence**: the existing project, plan, and request validation
  command set remains present beside the new complete commit-plan payload.
- **Failure behavior**: invalid plans, operational failures, and staged-tree
  drift fail before either paired output changes, while a stable ready result
  retains the previous successful rendering path.
- **Regression evidence**: the complete suite passes with no warning, expected
  failure, coverage gap, or duration outlier.

No existing feature or reporting capability appears impaired by Step 3.

---

## Step 4. Roll out shared review guidance and acceptance evidence

### Analysis of Step 4 implementation state

Yes. Step 4 has been fully implemented.

The canonical reviewer and grouping instructions now use the read-only checker
without transferring commit authority. Real-repository acceptance coverage
proves adapter parity, failure taxonomy, rename semantics, caller-owned
redirection, request rejection, and repository-state preservation.

### Goal for Step 4

Make grouped-commit and reviewer instructions use the shared read-only command
and prove entry-point parity plus exact repository immutability in acceptance
tests.

### Step 4 improvement expectations

- Requestors and reviewers independently establish the same mechanical
  readiness floor without transferring commit authority.
- Grouped-commit preparation repairs non-ready plans before commit choices.
- Real-repository tests cover the failure taxonomy, renames, both adapters, and
  complete before/after state equality.

### What was implemented for Step 4

- **Independent reviewer gate**: `instructions/code-reviewer.md` runs
  `commit-plan-check.bat --format json` before broader assessment, records the
  complete mechanical result, blocks on statuses `2` and `3`, and states that
  status `0` neither proves the other readiness-floor results nor authorizes a
  commit.
- **Grouping readiness gate**: `instructions/group-commits-msg.md` runs the
  focused checker after formatting and staging. Non-ready diagnostics return
  to plan repair, operational failure stops the flow, and the final batch still
  validates again before mutation.
- **Instruction contracts**: focused unit tests pin the independent rerun,
  status handling, authority boundary, ordering before the human menu, and the
  updated seven-step authorized residual and consolidation continuations.
- **Adapter and taxonomy acceptance**: a real-Git parametrized fixture covers
  valid, missing-plan, empty-plan, empty-staged-set, and membership-mismatch
  states through both human and JSON formats on the module and root launcher.
- **Repository immutability**: every parametrized ready or non-ready call
  compares `HEAD`, index tree, staged paths, tracked worktree diff, exact
  `a.commit` bytes, and ignored root inventory before and after.
- **Boundary acceptance**: focused scenarios cover both paths of a staged
  rename, failed Git inventory with stable status `2`, caller-owned redirected
  evidence as the only observable change, and requestor rejection of invalid
  checker evidence and index drift without paired outputs.
- **Repository gate evidence**: the final detached `ghog day` completed with
  `fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0`.

### New types or classes introduced for Step 4

No production type was introduced. Acceptance coverage adds the frozen
`_RepositoryState` snapshot type plus local repository, adapter, evidence, and
request-input fixtures. These test-only helpers keep setup deterministic and
leave checker and requestor production boundaries unchanged.

### Architecture check for Step 4

- **Canonical source boundary**: workflow behavior remains in root
  `instructions/` files; no provider-specific adapter copies were added or
  changed.
- **Responsibility boundary**: instructions call the shipped checker and react
  to its stable statuses without copying parser, inventory, or validation
  logic into Markdown.
- **Authority boundary**: checker success remains mechanical evidence only.
  Human or durable authorization still controls every committing batch, and
  the batch retains its final defensive validation.
- **Dependency direction**: acceptance code calls the public module and root
  launcher against temporary repositories. No production dependency points
  from commit-plan services into reviewer or grouping workflows.
- **File girth**: `instructions/code-reviewer.md` is 223 lines, inside its
  225-line advisory. `instructions/group-commits-msg.md` is 169 lines, 34 above
  its 135-line advisory after earlier continuation growth. The acceptance leaf
  is 418 lines, 38 above its 380-line advisory and below the 550-line helper
  extraction point. Both focused instruction test files remain inside their
  advisories, and every Python file remains below the 650-line ceiling.

No, there is nothing that needs to be addressed for Step 4.

### Performance check for Step 4

Checker and snapshot work is linear over exact plan, path, and evidence sets;
no nested per-path scan or sort was added. The initial request-rejection test
call measured 4.69 seconds because required repository setup and Git subprocess
boundaries ran in its assertion phase. Profiling placed 3.47 seconds in
caller-path ignore checks, so the full rejection exercise moved to fixture
setup without dropping an assertion. The isolated result reports 5.21 seconds
of setup while the measured call stays below the 0.50-second floor, and the
final full run reports zero outliers.

No, there is no performance issue that needs to be addressed for Step 4.

### Unit test coverage check for Step 4

- **Instruction contracts**: unit tests cover the independent reviewer rerun,
  mechanical-only result, statuses `2` and `3`, grouping order, final batch
  validation, and authorized continuation renumbering.
- **Production classes**: Step 4 changes no production Python class, so no new
  class-specific unit-test leaf is required.
- **Acceptance boundary**: real-repository tests are acceptance coverage and do
  not carry a class-level unit coverage target.
- **Coverage evidence**: the complete Groundhog gate reports 100% coverage for
  all affected production statements.

No, there is no unit-tested class below 100% that needs completing for Step 4.

### Feature integrity for Step 4

- **Reviewer behavior**: the six-part readiness floor, repair ownership,
  reciprocal waits, and advisory-only convergence decision remain present.
- **Grouping behavior**: normal menus, authorized review cleanup,
  consolidation cleanup, batch parsing, and clean-tree postconditions remain
  intact around the new read-only precheck.
- **Checker behavior**: acceptance results match across entry points and
  formats for every planned readiness state without entering commit execution.
- **Requestor behavior**: invalid plans and index drift still fail before either
  caller-owned request artifact is created.
- **Regression evidence**: the complete suite passes with no warning, expected
  failure, coverage gap, or duration outlier.

No existing feature or reporting capability appears impaired by Step 4.
