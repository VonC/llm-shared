# Design v0.11.0 -- Read-only commit-plan checking

Reference feature request:
[feature-request.v0.11.0.commit-plan-check.md](feature-request.v0.11.0.commit-plan-check.md)

---

## Context for v0.11.0 commit-plan checking

The batch commit workflow already parses `a.commit`, inventories staged paths,
and calls the side-effect-free `validate_commit_plan` API before it changes Git
state. Review-mode roles need that same decision without entering the batch
workflow that can reset the index and create commits.

This design adds a read-only application boundary over the existing parser,
staged inventory, and validator. It keeps commit execution in the batch
workflow and makes validation usable by humans, automation, and the code-review
requestor and reviewer roles.

## Scope for v0.11.0 commit-plan checking

The v0.11.0 outcomes are:

1. One typed checker result represents the parsed groups, staged membership,
   input-state failures, and validator diagnostics.
2. `commit-plan-check.bat` and
   `python -m tools.commit_plan_check` expose that result without changing the
   repository.
3. Code-review publication and reviewer assessment use the same checker as a
   shared mechanical readiness floor.

Everything else supports those outcomes or stays in the committing workflow.

### In scope for v0.11.0 commit-plan checking

- Project-root discovery and exact root `a.commit` resolution.
- Non-interactive parsing through the existing commit-plan parser.
- Exact staged-path inventory with `--no-renames` semantics.
- Stable human-readable and structured renderings of one typed result.
- Exit statuses zero, three, and two for success, expected non-readiness, and
  operational failure respectively.
- Enforced requestor-side validation and independent reviewer-side validation.
- State-preservation checks for successful and failing calls.

### Deferred beyond v0.11.0 commit-plan checking

- Repairing or rewriting `a.commit` from checker diagnostics.
- Adding commit actions or mutation flags to the checker.
- Changing the root batch workflow to accept
  `--root-a-commit --dry-run`.
- Active-review status and interrupted-review resumption, which are separate
  review-mode umbrella items.
- Reviewer-specific staged-path filtering or Git status classification.

---

## Confirmed technical facts for v0.11.0 commit-plan checking

These facts come from the current repository code.

**The validator is already side-effect free**:
`tools/git_batch_commit_validation.py` exports only
`validate_commit_plan(blocks, staged_paths)`. It returns immutable ordered
`CommitPlanGroup` values and diagnostic strings inside
`CommitPlanValidation`.

**The root parser path is reusable but private**:
`tools/git_batch_commit_workflow.py::_read_and_parse_content` accepts
`interactive=False` and returns the existing `CommitBlock` objects. It is in
that module's `__all__`, despite its private name.

**The staged inventory is private and unexported**:
`_staged_paths(root)` runs
`git diff --cached --name-only --no-renames -z`. Its result includes both sides
of a rename as distinct paths, but `_staged_paths` is absent from `__all__`.

**The current root command cannot be used safely by a reviewer**:
`--root-a-commit` rejects `--dry-run` and calls the commit phase after
validation succeeds.

**Code-review rendering already captures index identity**:
`tools/code_review_request.py` captures the request-time index tree and renders
it into the typed code-review evidence before publication.

**The paired-entry-point pattern already exists**:
`markdown-check.bat` delegates to a platform-neutral Python module and leaves
policy evaluation in shared Python code.

## Current behavior before read-only commit-plan checking

```txt
root a.commit
    -> _read_and_parse_content(interactive=False)
    -> _validate_missing_files_for_blocks
    -> _staged_paths(root)
    -> validate_commit_plan(blocks, staged_paths)
    -> git reset
    -> git add and git commit for each group
```

The reusable validation calls sit inside a command whose successful root-plan
path proceeds to mutation. Instructions can ask a reviewer to inspect the same
properties, but they cannot name a shipped read-only evidence command.

## Target behavior for read-only commit-plan checking

```txt
commit-plan-check.bat                     python -m tools.commit_plan_check
              \                           /
               -> command adapter and rendering
               -> check_commit_plan(root)
                    -> resolve root a.commit
                    -> parse with interactive=False
                    -> inventory exact staged paths
                    -> validate_commit_plan(blocks, staged_paths)
                    -> return one immutable checker result
               -> render human text or structured output
               -> return 0, 3, or 2

code-review requestor -> run checker -> render and publish only on status 0
code reviewer          -> rerun checker -> quote result as readiness evidence
```

Neither entry point calls the root batch workflow. Both call the same checker
service, so the launcher name and operating system cannot change validation
policy.

---

## Read-only checker model for commit plans

The checker service owns input orchestration, while
`validate_commit_plan` remains the authority for group and membership rules.
The service returns data and does not write output streams itself. The CLI
adapter is the only component that renders stdout and stderr.

### Root and plan input resolution for the checker

The adapter discovers the project root upward from the current directory by
default. An optional `--root <path>` overrides that discovery for tests and
automation; either route resolves and validates one canonical repository root
before calling the service. The service resolves only `<root>/a.commit`; it
does not accept an alternate plan path because the public feature is
specifically the root commit-plan readiness check.

Input handling distinguishes:

- missing `a.commit`;
- unreadable `a.commit`;
- an empty plan file or a parse with no commit blocks;
- a nonempty plan with an empty staged set;
- parsed and staged inputs passed to the public validator.

Missing and empty readiness inputs return typed non-ready diagnostics. An I/O
or Git execution problem that prevents a trustworthy decision is an
operational failure rather than an invalid plan.

### Typed result boundary for the checker

The checker uses an immutable result that wraps, rather than changes,
`CommitPlanValidation`. It carries:

- a stable result state such as `valid`, `missing-plan`, `empty-plan`,
  `empty-staged-set`, `invalid-plan`, or `operational-failure`;
- the ordered `CommitPlanGroup` values when parsing succeeds;
- every diagnostic in deterministic order;
- the exact staged paths used for the decision; and
- a boolean readiness property derived from the state and diagnostics.

Keeping an orchestration result outside `CommitPlanValidation` preserves the
public validator's narrow contract. Batch execution can continue consuming the
existing validator result, while the checker adds input-state meaning required
by a command boundary.

### Failure taxonomy for plan checking

Expected non-readiness includes malformed plan content, unsupported plan
commands, missing or empty readiness inputs, duplicate planned paths, and
planned-versus-staged membership differences. These conditions produce status
three because the command ran and found a plan that cannot proceed.

Invalid command arguments, repository discovery failure, unreadable inputs,
Git subprocess failure, encoding failure, or an unexpected exception produce
status two. They do not claim that the plan itself is invalid because the
checker could not complete its decision.

## Shared staged inventory for commit-plan parity

The checker and batch execution must call one staged-inventory function. No
adapter may recreate its Git command or filter its result.

### Public inventory boundary for staged paths

The preferred design extracts the inventory operation from the committing
workflow into a small shared commit-plan support boundary. That boundary owns
the cross-platform Git call and returns the existing tuple of repository-
relative paths.

Batch execution and read-only checking then depend on the shared boundary. A
private compatibility wrapper may remain in the batch module if existing tests
or imports require it, but it must delegate without changing the result.

### Rename and deletion semantics for staged membership

The inventory command remains exactly
`git diff --cached --name-only --no-renames -z`. The NUL delimiter preserves
paths containing whitespace, and `--no-renames` makes a rename appear as a
deleted source path plus an added destination path. Both paths must be named by
the commit plan.

Deletions remain staged paths even when the worktree file no longer exists.
The batch workflow's `_check_missing_files` already tolerates a staged deletion
of a committed file: it flags an absent worktree path only when that path is
also untracked and absent from `HEAD`. The read-only checker still does not use
that separate precondition, because its authority is exact index membership and
the public validator rather than worktree and `HEAD` state.

### Repository-state proof around checker calls

Acceptance tests capture `HEAD`, the index tree, staged-path inventory, tracked
worktree diff, root `a.commit` bytes, and relevant ignored-root inventory before
and after both valid and invalid calls. Equality proves the command did not
stage, unstage, reset, rewrite, or commit.

The checker does not create evidence files. Shell redirection remains a caller
action, including redirection to an ignored root `a.*` file.

## Output contracts for commit-plan evidence

Human and structured output are projections of the same checker result. The
adapter runs the service once per invocation, then selects one renderer. Both
entry points accept `--format human|json`, with `human` as the default.

### Human-readable commit-plan report

The default report begins with the result state, then lists groups in declared
order with their conventional subject and ordered paths. Diagnostics follow in
their deterministic service order. Each line is independently quotable and no
debug logging is mixed into stdout.

A valid report still lists every group and path so reviewer evidence proves
what was checked. An invalid report preserves all groups that parsed
successfully and prints every diagnostic rather than stopping at the first
membership error.

### Structured commit-plan report

The structured form is one JSON object produced from the same result. Its
proposed fields are:

```json
{
  "schema_version": 1,
  "state": "valid",
  "ready": true,
  "staged_paths": ["path/in/index"],
  "groups": [
    {
      "position": 1,
      "subject": "feat(scope): example",
      "paths": ["path/in/index"]
    }
  ],
  "diagnostics": []
}
```

The adapter uses deterministic key and list ordering. Structured output goes to
stdout even for expected non-readiness so automation can parse the evidence
before observing status three. Operational diagnostics go to stderr and status
two when no trustworthy checker result exists.

### Exit status mapping for checker adapters

| Checker outcome | Exit status | Stream contract |
| --- | --- | --- |
| Ready plan | `0` | Complete human or structured result on stdout |
| Expected invalid or non-ready plan | `3` | Complete human or structured result on stdout |
| Invalid invocation or operational failure | `2` | Stable diagnostic on stderr |

The root batch launcher's current status behavior is unchanged. These statuses
belong to the new read-only command boundary only.

## File-based IO cost clarification for v0.11.0 commit-plan checking

The checker keeps repository loading to a tiny exact-input phase:

- root discovery performs only the bounded parent lookup needed to identify
  one repository root;
- the service reads `<root>/a.commit` once and obtains staged membership with
  one shared Git index command;
- parsing, validation, and both renderers operate on the resulting in-memory
  blocks, paths, and typed result without rescanning files; and
- request rendering surrounds the checker with the two required index-tree
  captures, then writes paired artifacts only after readiness and tree
  stability are established.

The operation is linear in plan content and staged-path inventory outside the
existing validator's deterministic mismatch sorting. It introduces no
per-path file reads, documentation-tree scan, or command-owned write.

## Code-review integration for commit-plan evidence

The checker is mechanical evidence. Requestors and reviewers still own their
role-specific assessment, exchange transitions, and human authority boundaries.

### Enforced requestor publication gate

The specialized code-review request renderer is the enforcement boundary. It
runs the shared checker against the current project root before it writes the
paired request artifacts. A non-ready or operational result prevents artifact
rendering, so the canonical requestor sequence cannot reach `publish-request`
with an unchecked plan.

To bind the check to the request evidence, the renderer captures the index tree
before validation, runs the checker, captures the index tree again, and requires
both tree identities to match. The stable tree becomes the existing
`request_index_tree`. A changed tree rejects rendering and requires a fresh
request attempt.

The request content carries the structured checker result beside the existing
index tree and resolved validation set. The reviewer can then compare its rerun
with the plan and exact staged state received for that round.

This enforcement covers the canonical renderer-to-publication path, not every
possible direct protocol call. Shared `publish-request` validates the role,
identity, document, umbrella, implementation step, and round through
`_validate_envelope`; it does not prove that content came from the specialized
renderer. A caller that hand-authors a matching request envelope can therefore
bypass the checker gate. The design accepts that residual because closing it
would couple the role-neutral exchange core to `a.commit` and staged Git state.

### Independent reviewer readiness check

The code-reviewer instruction names `commit-plan-check.bat` in the readiness
floor. The reviewer reruns it before assessing grouping, ordering, scope, and
subjects, and records the result state, groups, diagnostics, and staged paths in
its evidence inputs.

A valid checker result does not prove implementation completeness, test
results, repair attribution, or commit authority. Any failure blocks a
commit-ready recommendation, but success satisfies only the mechanical
`a.commit` part of the six-part readiness floor.

### Grouping workflow use of the checker

The grouped-commit workflow runs the read-only checker after `a.commit` is
formatted and the intended set is staged. A status-three result returns the
diagnostics for plan repair. Status zero permits the existing commit menu or
authorized batch continuation; it does not itself approve a commit.

The final batch command still runs its own validator before mutation. The
read-only check is an earlier shared gate, not a replacement for defensive
validation inside commit execution.

## Acceptance cases for v0.11.0 commit-plan checking

| Scenario | Expected outcome | Reason |
| --- | --- | --- |
| Valid root plan and matching staged set | Both entry points report identical ordered groups and return `0` | One service owns validation and both renderers use its result |
| Planned path missing from the index | All parsed groups and the missing-membership diagnostic are reported with status `3` | Expected non-readiness must fail closed without hiding evidence |
| Empty `a.commit` and empty staged set | The result is `empty-plan` with status `3` | Empty set equality is not commit readiness |
| Nonempty plan and empty staged set | The result is `empty-staged-set` with status `3` | The caller receives a distinct recovery action |
| Missing root `a.commit` | The result is `missing-plan` with status `3` | Missing planning is expected non-readiness |
| Unreadable plan or failed Git inventory | A stable stderr diagnostic is returned with status `2` | The command cannot make a trustworthy plan decision |
| Staged rename | Source and destination paths both participate in membership | The checker matches `--no-renames` batch semantics |
| Caller redirects stdout to ignored `a.*` | The checker remains read-only and the caller owns the evidence file | Redirection is outside command behavior |
| Requestor plan is invalid | Code-review request rendering produces no paired outputs | Publication cannot proceed without status zero |
| Index changes during request rendering | Rendering stops before publication | Checker evidence and request index identity must describe one state |
| Reviewer rerun is valid | The result is recorded as mechanical readiness evidence only | Success does not grant commit authority |

## Design constraints for later implementation planning

- Preserve `validate_commit_plan` as the single authority for group and exact
  membership rules.
- Keep Git inventory in one shared boundary used by checking and committing.
- Keep rendering outside the checker service and run the service once per CLI
  invocation.
- Keep the checker free of staging, reset, repair, evidence-file, and commit
  operations.
- Keep code-review exchange coordination in its existing requestor and reviewer
  workflows.
- Keep root batch execution and its `--root-a-commit --dry-run` rejection
  unchanged.

## Design decisions for v0.11.0 commit-plan checking

| Question | Decision | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | Extract staged inventory into a neutral public commit-plan support boundary used by checking and committing. | Shared staged inventory for commit-plan parity | Exporting the batch-private helper or duplicating the Git call |
| Q02 | Wrap the unchanged public validator result in an immutable checker-specific result. | Typed result boundary for the checker | Expanding the validator with orchestration states or using exceptions and renderer-specific values |
| Q03 | Select output with `--format human\|json`, defaulting to `human`. | Output contracts for commit-plan evidence | A `--json` boolean or a separate structured-output command |
| Q04 | Enforce the requestor gate in the specialized code-review renderer and accept the documented direct-publication bypass. | Enforced requestor publication gate | Coupling shared `publish-request` to commit plans or relying on instructions alone |
| Q05 | Exclude the batch missing-file precheck and decide readiness from parsing plus exact staged membership. | Rename and deletion semantics for staged membership | Advisory reuse or readiness-gate reuse of worktree and `HEAD` checks |
| Q06 | Embed the full structured checker result in the code-review request. | Enforced requestor publication gate | A validity marker only or no durable checker evidence |
| Q07 | Discover the root from the current directory by default and accept optional `--root <path>`. | Root and plan input resolution for the checker | Discovery only or a mandatory repository argument |
