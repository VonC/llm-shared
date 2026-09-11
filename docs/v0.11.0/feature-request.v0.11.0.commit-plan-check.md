# Validate commit plans without committing

## Review-mode need for read-only commit-plan validation

As an implementation reviewer or requestor, I want one repository command to
validate the root `a.commit` against the exact staged file set without changing
Git state, so both roles can use the batch workflow's real readiness floor
without entering its committing path.

This requirement belongs to the `commit-plan-check` item in the review-mode
umbrella. It adds a read-only entry point over existing commit-plan behavior;
it does not create a second validator or move commit-plan ownership into a
review role.

## Current commit-plan behavior in v0.11.0

- `tools/git_batch_commit_validation.py` exposes the public,
  side-effect-free `validate_commit_plan(blocks, staged_paths)` API.
- The API validates ordered groups, conventional subjects, supported `git add`
  commands, duplicate membership, and exact agreement with the staged paths.
- `tools/git_batch_commit_workflow.py` parses the root `a.commit` with
  `interactive=False` and calls the public validator before its commit phase.
- The shipped root-plan entry point rejects `--root-a-commit` together with
  `--dry-run`, so its successful path proceeds beyond validation to committing.
- Reviewer instructions currently describe how to assess `a.commit`, but do
  not name a safe command that produces the validator's typed evidence.

## Gap to close for commit-plan checking

The repository has the validation API but no command that exposes it for the
root plan as an explicitly read-only operation. A reviewer must therefore
inspect the plan manually or create an ad hoc import, even though batch
execution already relies on the authoritative rules.

The missing entry point must make the following behavior directly usable:

1. Read the project-root `a.commit` non-interactively.
2. Read the exact staged path set without changing it.
3. Pass the parsed blocks and staged paths to `validate_commit_plan`.
4. Report every typed group and diagnostic in a stable, quotable form.
5. Return without staging, unstaging, resetting, rewriting files, or committing.

## Required read-only command contract

The focused repository-root command is named `commit-plan-check.bat`. It must
run from a repository context and resolve the same project root, plan file,
parser, staged-path inventory, and public validator used by the batch workflow.
It must not weaken, reinterpret, or duplicate validation rules in a
launcher-specific implementation. The same shared function must also be
reachable through the platform-neutral `python -m tools.commit_plan_check`
entry point. The two adapters must not implement separate validation behavior.

### Commit-plan inputs for the read-only command

- Plan source: the project-root `a.commit`.
- Parser mode: `interactive=False`.
- Membership source: the exact paths currently staged in Git.
- Validation call: `validate_commit_plan(blocks, staged_paths)`.

Malformed plan content and mismatches between planned and staged paths remain
validator diagnostics. The adapter must preserve their association with the
affected group, path, or rule.

A missing plan, an empty plan, an empty staged set, and a membership mismatch
must each produce a distinct fail-closed diagnostic. None of those states is
commit-ready. The adapter may enforce the missing and empty input preconditions
before it returns the public validator's typed groups and diagnostics for
nonempty inputs.

### Repository-state guarantee for the read-only command

The command must not run `git reset`, `git add`, `git rm`, or `git commit`, and
must not rewrite `a.commit` or another repository file. Repeated calls with
unchanged inputs must leave the index and working tree unchanged.

Tests must compare the relevant Git state before and after successful and
failing validation calls. A failure is evidence about the plan, not authority
to repair or commit it automatically.

The command itself writes nothing under the repository root. A caller may
explicitly redirect its human or structured output into an ignored root `a.*`
evidence file; that caller-owned redirection does not weaken the command's
no-write guarantee.

### Validation evidence emitted by the command

The report must include the ordered typed groups returned by the public API and
every diagnostic it produces. Human-readable output is the default, and a
stable structured mode must contain the same groups and diagnostics from the
same validation result. A code reviewer can quote the default output as
readiness-floor evidence, while requestor automation does not need to scrape
unrelated log prose.

Exit statuses follow the repository convention already used by
`bin/review_exchange.bat`: zero means validation completed successfully, three
means the expected stop of an invalid or non-ready plan, and two means invalid
invocation or an unexpected operational failure.

## Entry-point direction for commit-plan checking

The feature must ship both `commit-plan-check.bat` and
`python -m tools.commit_plan_check` over one shared read-only function. The
focused root launcher makes the no-commit promise explicit for local Windows
roles. The module entry point supplies the same evidence contract to
platform-neutral automation without requiring callers to import private
implementation details.

The existing batch launcher's `--root-a-commit --dry-run` combination remains
unsupported. Root-plan mode there continues to mean validate and commit, so a
flag combination inside that interface is not the public read-only boundary.

## File-based IO cost clarification for commit-plan checking

- Plan loading is one exact read of `<root>/a.commit`; it must not scan the
  documentation tree or preload repository metadata.
- Staged membership comes from one exact Git index inventory using
  `git diff --cached --name-only --no-renames -z`, not from per-path worktree
  probes.
- One checker call parses and projects the plan and inventory in memory after
  those bounded reads. Human and structured output reuse the same result.
- The requestor gate may capture the index tree before and after checking, but
  it must not add directory traversal or command-owned repository writes.

## Shared review evidence for commit-plan checking

The code-reviewer instruction must name the resulting command where it
currently asks for a prose assessment of `a.commit`. Its result becomes the
readiness-floor evidence; it does not replace the reviewer's broader judgment
or grant commit authority.

The requestor-side command is an enforced publication precondition rather than
an advisory instruction. `group-commits-msg` and the code-review requestor must
use the same validation result, and publication must refuse to proceed while
the plan is invalid or non-ready. The reviewer reruns the command against the
received state so both roles independently establish the same readiness floor.

The staged inventory must preserve exact batch-workflow semantics. Its current
source is the private `_staged_paths(root)` helper in
`tools/git_batch_commit_workflow.py`; reuse therefore requires exporting that
helper or extracting it into a shared module. It invokes
`git diff --cached --name-only --no-renames -z`, so both sides of a rename are
separate inventory paths and both must appear in a matching plan.

## Requirement clarifications for commit-plan checking

| Question | Decision | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | Ship the focused `commit-plan-check.bat` launcher. | Required command contract and entry-point direction | Extending only the committing launcher hides the safety boundary; supporting both batch surfaces adds compatibility work. |
| Q02 | Default to human-readable output and provide a stable structured mode over the same result. | Validation evidence and acceptance criteria | Human-only output forces prose parsing; structured-only output is poor review evidence. |
| Q03 | Return zero for success, three for an invalid or non-ready plan, and two for invalid invocation or unexpected failure. | Validation evidence and acceptance criteria | Always-zero is unsafe for shell gates; one failure status cannot guide recovery. |
| Q04 | Block request publication until requestor validation succeeds, then require an independent reviewer rerun. | Shared review evidence and acceptance criteria | Reviewer-only or advisory checks allow preventable invalid requests. |
| Q05 | Permit no command-owned repository writes; caller-owned redirection to an ignored root `a.*` file remains valid. | Repository-state guarantee and acceptance criteria | Ignored writes leave side effects; an output-file flag weakens the unconditional boundary. |
| Q06 | Report missing plan, empty plan, empty staged set, and membership mismatch distinctly; none is commit-ready. | Commit-plan inputs | Empty equality is not review readiness; one generic failure hides the required recovery. |
| Q07 | Reuse or extract the exact batch inventory, including two paths for renames under `--no-renames`. | Shared review evidence, acceptance criteria, and code references | Reviewer-specific filtering can make validation disagree with the committing path. |
| Q08 | Ship the root batch launcher and platform-neutral Python module over one shared function. | Required command contract and entry-point direction | Batch-only excludes portable automation; Python-only breaks the root-launcher convention. |

## Acceptance criteria for commit-plan checking

1. The shipped repository-root `commit-plan-check.bat` command validates the
   root `a.commit` against the exact staged paths without entering a commit
   workflow.
2. The command parses with `interactive=False` and calls the existing public
   `validate_commit_plan(blocks, staged_paths)` API.
3. The command reports ordered typed groups and all validator diagnostics in a
   stable human-readable form and a stable structured form suitable for review
   evidence and automation.
4. Successful and failing calls leave the index, working tree, `a.commit`, and
   `HEAD` unchanged.
5. Automated tests prove the no-mutation contract and exact reuse of the public
   parser, staged-path inventory, and validator.
6. The code-reviewer instructions name the command and explain how its output
   contributes to the readiness floor without authorizing a commit.
7. The chosen entry point explicitly resolves the current incompatibility
   between root-plan mode and `--dry-run`.
8. Invalid or non-ready plans use exit status three, successful validation uses
   zero, and invalid invocation or unexpected failure uses two.
9. Code-review request publication is blocked until requestor-side validation
   succeeds, and the reviewer independently reruns the same command.
10. Inventory semantics match `_staged_paths(root)`, including separate paths
    for both sides of a rename under `--no-renames`.
11. The command writes nothing under the repository root, while callers may
    explicitly redirect output into ignored `a.*` evidence files.
12. A missing plan, an empty plan, an empty staged set, and a membership
    mismatch produce distinct diagnostics and none is commit-ready.
13. Both `commit-plan-check.bat` and
    `python -m tools.commit_plan_check` call one shared read-only function.

## Scope boundaries for commit-plan checking

- Do not reimplement or fork the public commit-plan validation rules.
- Do not add staging, reset, file-rewrite, or commit side effects.
- Do not make the command responsible for repairing `a.commit`.
- Do not fold the tool into the code-reviewer assessment role.
- Do not include active-review status or interrupted-review resumption; those
  remain the next separate review-mode umbrella items.

## Code references for commit-plan checking

- `tools/git_batch_commit_validation.py`: defines the typed public validator
  and its group, subject, command, duplicate, and staged-membership checks.
- `tools/git_batch_commit_workflow.py`: parses root `a.commit`, inventories the
  staged paths, invokes validation, rejects root-plan dry-run, and owns commit
  execution after validation.
- `tools/git_batch_commit_workflow.py::_staged_paths`: currently private and
  unexported; obtains exact staged membership with
  `git diff --cached --name-only --no-renames -z`, counting both rename sides.
- `tools/prompt_workflow_code_review.py`: invokes the committing root-plan path
  only after durable human commit authorization.
- `instructions/code-reviewer.md`: defines the current prose readiness-floor
  assessment that must name the read-only command.
- `instructions/group-commits-msg.md`: defines requestor-side grouping and is
  the decision point for optional pre-publication use of the same command.
