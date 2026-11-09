# Code review transcript for v0.14.0

- Exchange: code/code/v0.14.0/version-sources
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor - Step 1

- Recorded: 2026-11-08T16:27:40+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Implementation step: 1
- Outcome: request

### Review identity for step 1 version-sources (round 1)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.version-sources.md
Implementation step: 1
Review round: 1

### Code review evidence for step 1 version-sources (round 1)

request_index_tree: d5c639f56bcffc1e031cb22cdda59427ca816e43
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.version-sources.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(release): accept operation tokens per handler
group 1 path: tools/release_workflow/cli.py
group 1 path: tools/release_workflow/invocation.py
group 1 path: tests/unit/tools/release_workflow/test_cli/test_cli_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_invocation/test_invocation_tdd.py
group 2: feat(release): make status 3 a public status
group 2 path: tools/release_workflow/results.py
group 2 path: tools/release_workflow/bootstrap.py
group 2 path: bin/release_workflow.bat
group 2 path: bin/release_alias.bat
group 2 path: tests/unit/tools/release_workflow/test_results/test_results_tdd.py
group 2 path: tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py
group 2 path: tests/unit/tools/release_workflow/test_launchers/test_codepage_tdd.py
group 3: feat(release): verify a held operation lock
group 3 path: tools/release_workflow/operation_lock.py
group 3 path: tests/unit/tools/release_workflow/test_operation_lock/test_operation_lock_tdd.py
group 4: feat(release): add typed Git release observations
group 4 path: tools/release_workflow/git.py
group 4 path: tests/unit/tools/release_workflow/repository_simulation.py
group 4 path: tests/unit/tools/release_workflow/launcher_simulation.py
group 4 path: tests/unit/tools/release_workflow/test_git/test_git_releases_tdd.py
group 4 path: tests/unit/tools/release_workflow/test_release_transport/test_release_transport_tdd.py
group 5: docs(version-sources): record step 1 validation
group 5 path: docs/v0.14.0/plan.v0.14.0.version-sources.md
group 5 path: docs/v0.14.0/plan.v0.14.0.version-sources.validation.md
staged path: bin/release_alias.bat
staged path: bin/release_workflow.bat
staged path: docs/v0.14.0/plan.v0.14.0.version-sources.md
staged path: docs/v0.14.0/plan.v0.14.0.version-sources.validation.md
staged path: tests/unit/tools/release_workflow/launcher_simulation.py
staged path: tests/unit/tools/release_workflow/repository_simulation.py
staged path: tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py
staged path: tests/unit/tools/release_workflow/test_cli/test_cli_tdd.py
staged path: tests/unit/tools/release_workflow/test_git/test_git_releases_tdd.py
staged path: tests/unit/tools/release_workflow/test_invocation/test_invocation_tdd.py
staged path: tests/unit/tools/release_workflow/test_launchers/test_codepage_tdd.py
staged path: tests/unit/tools/release_workflow/test_operation_lock/test_operation_lock_tdd.py
staged path: tests/unit/tools/release_workflow/test_release_transport/test_release_transport_tdd.py
staged path: tests/unit/tools/release_workflow/test_results/test_results_tdd.py
staged path: tools/release_workflow/bootstrap.py
staged path: tools/release_workflow/cli.py
staged path: tools/release_workflow/git.py
staged path: tools/release_workflow/invocation.py
staged path: tools/release_workflow/operation_lock.py
staged path: tools/release_workflow/results.py
```

### Validation scope for step 1 version-sources (round 1)

Validation scope: the whole suite.

### Requestor assessment for step 1 version-sources (round 1)

Writer assessment for Step 1 of the version-sources plan, round 1: the step is
fully implemented, and its implementation check records
`Yes. Step 1 has been fully implemented.` in the staged validation plan.

Evidence, all on the staged tree:

- Tests first: the eight Step 1 test files failed at collection on the
  missing API (`ghog single`, exit 4), then passed (`ghog single`, exit 0).
- `ghog day --whole-suite`, the command printed by `pw scope day`, exit 0
  (check.bat: ty, pyright, ruff, radon, vulture, file size, Markdown,
  ShellCheck, end-of-file; affected tests green).
- `ghog day --full=speed --whole-suite`, the review validation default printed
  by `pw scope day --full=speed`, exit 0: full suite with no failure, coverage
  100%, no duration outlier and no exclusion. No exclusion is accepted in this
  step.
- Completion checks of the plan: both launchers carry the status 3 line;
  `results.py` and `bootstrap.py` carry `{0, 1, 2, 3}`; the cross-site status
  test and its counter-test pass; `cli.SHIPPED_HANDLERS` is empty; the
  `subprocess|Popen` search over the repository simulation matches only data
  (see the writer response).
- Every Python file stays below 650 lines; the largest is `git.py` at 307.

Architecture: the observations stay in the Git adapter behind `_execute`, the
parser knows only an optional validator per handler, and `verify_held` adds a
check without changing any lock transition. No DDD-Hexagonal violation is
visible. Performance: every new parse is linear in its output and each
observation is one Git call; the four-call selection ceiling is kept. Feature
integrity: a handler without a validator behaves as before when no token is
given, and the unavailable-operation message is unchanged.

Please check in particular: the intermixed parse with the validator order in
`_select`; the record format and parser of `tag_records` and its mapping of
exit 129; the exactness of the command-line measurement against what
`_execute` starts; the binding checks of `verify_held`; and whether the
simulation answers the five observations faithfully for Step 8.

### Implementation report for step 1 version-sources (round 1)

Step 1, "Foundation extensions for the version domain", extends item 1's
release foundation where the version domain needs it. No version command
ships yet: `cli.SHIPPED_HANDLERS` stays empty until Step 9.

Operation tokens (`tools/release_workflow/cli.py`, `invocation.py`):

- `_parse` adds an `operation` positional (`nargs="*"`) and parses with
  `parse_intermixed_args`, so options parse the same before, between and
  after the tokens.
- `Handler` gains `validate_arguments: Callable[[tuple[str, ...]], None] |
  None`. `_select` calls it with the tokens, or raises
  `Release operation '<name>' takes no arguments: ...` when it is `None` and
  tokens exist; `_select` runs before `RuntimeIdentity.load` and
  `create_context`, so a token error is status 2 with no Git process or file
  read.
- `InvocationRequest.operation` and `InvocationContext.operation` (trailing,
  default `()`); `create_context` copies it; the batch-character rule already
  covers every argv token.

Public status 3 (`results.py`, `bootstrap.py`, both launchers):

- `results.render` and `bootstrap.main` accept `{0, 1, 2, 3}`; both
  `bin/release_workflow.bat` and `bin/release_alias.bat` add
  `if "%_release_status%"=="3" goto cleanup` before the normalization line.
  Any other status is still diagnosed with its original value and returned as
  1.
- `test_codepage_tdd.py` adds the cross-site contract of plan decision Q12: it
  parses the set literal checked by `render` and `main` and the pass-through
  lines of both launchers as integers and requires one common set; a
  parametrized counter-test drops status 3 from one site in a synthetic copy
  and shows the agreement breaks.

Held-lock check (`operation_lock.py`):

- `OperationLock.verify_held(declaration) -> PreparedArtifacts` rejects a
  handle that no longer holds the lock, an owner whose process is not
  `current_identity()`, a declaration for another physical project root and
  a lock record not under the declared artifact home; it then calls
  `_require_owned()` inside `_transition()`, which rejects a replaced or
  retained record. Acquisition, release, retention and transfer are
  unchanged.

Typed Git release observations (`git.py`):

- `TagRecord` (frozen: name, object type, peeled commit, own annotation or
  `None` for a lightweight tag).
- `tag_records(*, cwd, merged=None)`: one `for-each-ref` over `refs/tags` with
  NUL-terminated fixed fields and an optional `--merged=<revision>`; exit 129
  whose stderr reports `malformed object name <revision>` raises
  `GitRevisionNotFoundError` (a `GitCommandError` carrying the revision,
  `exit_code = 2`); every other failure stays `GitCommandError`.
- `independent_commits(commits, *, cwd)`: one `merge-base --independent`.
  `_independent_arguments` measures the exact command line `_execute` would
  pass (`subprocess.list2cmdline` over the executable, the fixed `run`
  options, now one shared tuple, and the arguments) in UTF-16 code units plus
  the terminating NUL, and raises `GitCommandLineTooLongError`
  (`exit_code = 1`, naming the limit and the candidate count) above 32,767
  before any call (plan decision Q13).
- `tag_names`, `commit_count` (non-numeric output is a `GitPolicyError`) and
  `listing` (drops names ending with `/`, so an untracked nested repository
  goes and a tracked gitlink stays).
- The two exceptions take the repository's `Error` suffix (ruff N818; every
  exception in the package ends in `Error`); the plan now uses
  `GitRevisionNotFoundError` and `GitCommandLineTooLongError`.

Simulation (`tests/unit/tools/release_workflow/`):

- `repository_simulation.ReleaseHistory` declares commits with parents,
  `HEAD`, `main`, tags and listing names; `RepositoryObservations` answers the
  five methods by reachability over the declared parents, records each call
  and calls the production guard before the tips query. No process is
  started.
- `launcher_simulation._patch_release_observations` routes the five methods to
  the sandbox; `test_release_transport_tdd.py` proves the routing through the
  real bootstrap and also passes status 3 through every entry kind.

Tests first: the eight Step 1 test files failed at collection on the missing
API, then passed. New test file:
`tests/unit/tools/release_workflow/test_git/test_git_releases_tdd.py`.

Writer notes: `.reviews/a.version-sources.step1.journal.md` and
`.reviews/a.version-sources.step1.handoff.md`.

### Change summary for step 1 version-sources (round 1)

Staged paths (20), grouped in the root `a.commit` (five groups, checker
`ready: true`):

1. `feat(release): accept operation tokens per handler`:
   `tools/release_workflow/cli.py`, `tools/release_workflow/invocation.py`,
   `tests/unit/tools/release_workflow/test_cli/test_cli_tdd.py`,
   `tests/unit/tools/release_workflow/test_invocation/test_invocation_tdd.py`.
2. `feat(release): make status 3 a public status`:
   `tools/release_workflow/results.py`, `tools/release_workflow/bootstrap.py`,
   `bin/release_workflow.bat`, `bin/release_alias.bat`,
   `tests/unit/tools/release_workflow/test_results/test_results_tdd.py`,
   `tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py`,
   `tests/unit/tools/release_workflow/test_launchers/test_codepage_tdd.py`.
3. `feat(release): verify a held operation lock`:
   `tools/release_workflow/operation_lock.py`,
   `tests/unit/tools/release_workflow/test_operation_lock/test_operation_lock_tdd.py`.
4. `feat(release): add typed Git release observations`:
   `tools/release_workflow/git.py`,
   `tests/unit/tools/release_workflow/repository_simulation.py`,
   `tests/unit/tools/release_workflow/launcher_simulation.py`,
   `tests/unit/tools/release_workflow/test_git/test_git_releases_tdd.py` (new),
   `tests/unit/tools/release_workflow/test_release_transport/test_release_transport_tdd.py`.
5. `docs(version-sources): record step 1 validation`:
   `docs/v0.14.0/plan.v0.14.0.version-sources.md` (exception names),
   `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md` (Step 1
   sections).

Before this step, the branch committed the design clarification of plan
decision Q15 (design questions Q18 and Q19, consolidated) in `083ef50`,
`fd1c971` and `0edf3a9`; those commits are not part of this review.

### Writer response for step 1 version-sources (round 1)

Writer response:

This is the first round of the Step 1 code review; there is no earlier
reviewer feedback to answer.

Two deliberate differences from the plan's wording, both recorded in the
staged plan and validation plan:

- The plan named the exceptions `GitRevisionNotFound` and
  `GitCommandLineTooLong`. Ruff's N818 rule, enabled through `ALL`, requires
  an `Error` suffix, and every exception of `tools/release_workflow` already
  ends in `Error`; there is no N818 suppression anywhere in the repository.
  The code uses `GitRevisionNotFoundError` and `GitCommandLineTooLongError`,
  and the plan's Step 1 and Step 8 text now uses these names.
- The plan's completion check `rg -n 'subprocess|Popen'
  tests/unit/tools/release_workflow/repository_simulation.py` "finds no
  process start". It matches two lines: the `subprocess` import and a
  `subprocess.CompletedProcess` value that `ReleaseHistory.resolve` builds for
  `GitRevisionNotFoundError`, whose constructor takes the failed command. Both
  are data; no process is started.

The step also adds one test the plan did not list,
`test_release_observations_reach_the_declared_history`, so that the five
routers added to the launcher simulation run in this step instead of first in
Step 9.

### Reviewer focus for step 1 version-sources (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-1-round-1 -->

### LLM nature completion for reviewer (exchange 1)

Recorded nature: `codex`

Completed artifacts:

- `.reviews/a.review-active.code.code.v0.14.0.version-sources.md`
- `.reviews/a.review-requested.code.v0.14.0.version-sources.md`

<!-- review-entry-id: llm-nature-completion-reviewer-exchange-1 -->

## Round 1 by reviewer - Step 1

- Recorded: 2026-11-08T16:42:41+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 1
- Outcome: answer

### Assessed index identity for step 1 version-sources (exchange 1) (round 1)

Baseline index tree: d5c639f56bcffc1e031cb22cdda59427ca816e43

Assessed index tree: 461d06e7ab61f141119ad1866783269efc1449b9

### Implementation check for step 1 version-sources (exchange 1) (round 1)

Result:

No. Step 1 has NOT been fully implemented.

Operation tokens and early validators, invocation propagation, status 3 across all four sites, held-lock verification, the five typed observations, and their simulation wiring are present. The shipped registry remains empty. All changed Python files remain below 650 lines. No DDD-Hexagonal violation or new quadratic computation was found.

The tag observation does not meet its peeled-commit contract for nested annotated tags; see F1. The Step 1 validation plan now records the missing implementation and regression work.

Validation plan effects:

Only the reviewed Step 1 sections of docs/v0.14.0/plan.v0.14.0.version-sources.validation.md changed: the exact No verdict, its explanation, the Missing work section, semantic coverage assessment, and feature-integrity limitation. Other steps and the document-level status remain unchanged. The recorded pre-edit blob and attribute-reviewer-patch proved attribution; only that patch was staged. No implementation or test repair was made.

### Pre-repair mandatory checks and coverage for step 1 version-sources (exchange 1) (round 1)

The requestor reports ghog day --full=speed --whole-suite passed on the request tree, full suite and 100% coverage included, with no duration exclusions. These are writer results, not reviewer execution.

The reviewer did not repeat the walk or measure coverage. No ghog check or ghog affected execution was needed to identify the static adapter-contract defect. The bound round scope is whole, proof speed, fingerprint 686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6.

The gate measures tools and omits tests. Static review finds the added production paths exercised and the added simulation symbols referenced by unit/transport tests. The canned tag cases omit nested annotated tags, so reported measured coverage does not establish their commit semantics.

### Resolved validation set and sources for step 1 version-sources (exchange 1) (round 1)

Request and current resolver both require ghog day --full=speed --whole-suite, source project. The current project declaration is absent, so the resolver completes its built-in default with the whole-suite selector. No plan or request additions are carried. This set belongs to requestor validation and was not executed by the reviewer.

### Resolver drift and direction for step 1 version-sources (exchange 1) (round 1)

No drift: the current resolver helper returned {"commands": [{"command": "ghog day --full=speed --whole-suite", "sources": ["project"]}]}, matching the request.

### Repository state around validation for step 1 version-sources (exchange 1) (round 1)

Baseline/request tree d5c639f56bcffc1e031cb22cdda59427ca816e43 matched retained and current evidence before assessment. Final assessed tree is 461d06e7ab61f141119ad1866783269efc1449b9.

Umbrella digest remained 5abf0cb72800e9d07acba786dd90502fcb8879ff41cbcce55b961a95352aaa4c. The identical ordered validation-path set was captured before and after. The generic comparison reports acceptable=false for the validation plan and `<index>`; these changes are fully accounted for by the attributable, staged Step 1 metadata patch. There are no other tracked changes in that comparison, no untracked side effects, and no validation command side effects.

### Repair inventory for step 1 version-sources (exchange 1) (round 1)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 1 version-sources (exchange 1) (round 1)

Independent commit-plan-check.bat --format json returned exit 0, state valid, ready true, and no diagnostics before assessment; the post-metadata rerun agrees. All 20 staged paths are covered exactly once in five ordered groups:

1. feat(release): accept operation tokens per handler
2. feat(release): make status 3 a public status
3. feat(release): verify a held operation lock
4. feat(release): add typed Git release observations
5. docs(version-sources): record step 1 validation

The grouping, order, scopes and subjects describe the staged changes accurately. Full checker JSON is retained in the caller scratch commit-plan.json. Mechanical readiness does not resolve F1 or authorize a commit.

### Findings and boundaries for step 1 version-sources (exchange 1) (round 1)

Unresolved findings:

- F1 (P2), tools/release_workflow/git.py:40 and :144-147: preserve fully peeled commit identity for annotated tags pointing to annotated tags. For outer tag v1.0.0 -> inner annotated tag 1.0.0 -> commit C, Git's %(*objectname) yields the inner tag-object ID after one dereference. `_tag_records` puts that value directly in TagRecord.commit, while the direct inner record contains C. The API therefore returns different commit identities for tags on the same final commit. The approved design groups tags by version and peeled commit (design lines 715-720); this discrepancy would produce false conflicts or invalid independent-tip inputs. Existing canned tests cover direct annotated tags and lightweight commit tags, and assume the starred value is a commit. Reconcile the plan's prescribed one-call format with its peeled-commit contract, retain each outer tag's own annotation, and add a process-free nested-tag regression. If the query budget requires a contract or policy change, resolve it explicitly before implementation rather than silently introducing a new tag exclusion.

Boundary-crossing work: None.

### Writer instructions for step 1 version-sources (exchange 1) (round 1)

Resolve F1 and complete the two bullets under Missing work for Step 1 in the validation plan. Keep any necessary plan/design clarification explicit; this assessment does not authorize changing the approved query budget or tag eligibility policy. Add meaningful process-free nested-tag cases, then run the writer's required validation, refresh the exact Step 1 implementation check and commit plan, and submit a replacement request. No Human guidance block authorized reviewer repairs.

### Decision rationale for step 1 version-sources (exchange 1) (round 1)

Changes requested. The six readiness results are: exact identity passes; implementation completeness fails on F1; validation/coverage has green writer provenance but a semantic regression gap; staged attribution passes for the Step 1 metadata patch; absence of unresolved findings fails; independent commit-plan readiness passes. No substantive reviewer repair was made. The recommendation is advisory and does not authorize a commit.

### Final reviewer decision for step 1 version-sources (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-1-round-1 -->

## Round 2 by requestor - Step 1

- Recorded: 2026-11-08T16:59:01+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 1
- Outcome: request

### Review identity for step 1 version-sources (round 2)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.version-sources.md
Implementation step: 1
Review round: 2

### Code review evidence for step 1 version-sources (round 2)

request_index_tree: c6059047c28c757d21439750b93debdacbf8a19e
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.version-sources.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(release): accept operation tokens per handler
group 1 path: tools/release_workflow/cli.py
group 1 path: tools/release_workflow/invocation.py
group 1 path: tests/unit/tools/release_workflow/test_cli/test_cli_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_invocation/test_invocation_tdd.py
group 2: feat(release): make status 3 a public status
group 2 path: tools/release_workflow/results.py
group 2 path: tools/release_workflow/bootstrap.py
group 2 path: bin/release_workflow.bat
group 2 path: bin/release_alias.bat
group 2 path: tests/unit/tools/release_workflow/test_results/test_results_tdd.py
group 2 path: tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py
group 2 path: tests/unit/tools/release_workflow/test_launchers/test_codepage_tdd.py
group 3: feat(release): verify a held operation lock
group 3 path: tools/release_workflow/operation_lock.py
group 3 path: tests/unit/tools/release_workflow/test_operation_lock/test_operation_lock_tdd.py
group 4: feat(release): add typed Git release observations
group 4 path: tools/release_workflow/git.py
group 4 path: tests/unit/tools/release_workflow/repository_simulation.py
group 4 path: tests/unit/tools/release_workflow/launcher_simulation.py
group 4 path: tests/unit/tools/release_workflow/test_git/test_git_releases_tdd.py
group 4 path: tests/unit/tools/release_workflow/test_release_transport/test_release_transport_tdd.py
group 5: docs(version-sources): record step 1 validation
group 5 path: docs/v0.14.0/plan.v0.14.0.version-sources.md
group 5 path: docs/v0.14.0/plan.v0.14.0.version-sources.validation.md
staged path: bin/release_alias.bat
staged path: bin/release_workflow.bat
staged path: docs/v0.14.0/plan.v0.14.0.version-sources.md
staged path: docs/v0.14.0/plan.v0.14.0.version-sources.validation.md
staged path: tests/unit/tools/release_workflow/launcher_simulation.py
staged path: tests/unit/tools/release_workflow/repository_simulation.py
staged path: tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py
staged path: tests/unit/tools/release_workflow/test_cli/test_cli_tdd.py
staged path: tests/unit/tools/release_workflow/test_git/test_git_releases_tdd.py
staged path: tests/unit/tools/release_workflow/test_invocation/test_invocation_tdd.py
staged path: tests/unit/tools/release_workflow/test_launchers/test_codepage_tdd.py
staged path: tests/unit/tools/release_workflow/test_operation_lock/test_operation_lock_tdd.py
staged path: tests/unit/tools/release_workflow/test_release_transport/test_release_transport_tdd.py
staged path: tests/unit/tools/release_workflow/test_results/test_results_tdd.py
staged path: tools/release_workflow/bootstrap.py
staged path: tools/release_workflow/cli.py
staged path: tools/release_workflow/git.py
staged path: tools/release_workflow/invocation.py
staged path: tools/release_workflow/operation_lock.py
staged path: tools/release_workflow/results.py
```

### Validation scope for step 1 version-sources (round 2)

Validation scope: the whole suite.

### Requestor assessment for step 1 version-sources (round 2)

Writer assessment for Step 1 of the version-sources plan, round 2: the step is
fully implemented. Round 1 finding F1 (a tag of a tag exposing its inner tag
object as the commit) is fixed within the one-call budget and the existing
tag policy, and the refreshed implementation check in the staged validation
plan reads `Yes. Step 1 has been fully implemented.`

Evidence on the replacement tree:

- `ghog single` on `test_git_releases_tdd.py` and
  `test_release_transport_tdd.py` with the nested-tag cases: exit 0.
- `ghog day --full=speed --whole-suite`, the review validation default:
  exit 0, run in full (check, affected and full stages, nothing reused), no
  failure, coverage 100%, no duration outlier, no exclusion. No exclusion is
  accepted in this step.
- Markdown check exit 0, including the versioned review transcript;
  `commit-plan-check` ready with no diagnostics; 20 staged paths in the same
  five groups.
- Every Python file stays below 650 lines; `git.py` is now 344.

Architecture, performance and feature integrity are unchanged from round 1,
with one addition: the nested-tag walk is linear in the listing because each
tag object is followed once. No DDD-Hexagonal violation is visible.

Please check in particular: whether following the inner tag object through
the same listing is sound for every supported Git version and for the
`--merged` filter, whether failing closed on an inner tag object without its
own ref is an acceptable reading of the existing fail-closed rule for
untrusted Git output (it excludes no tag and adds no call), and whether the
new tests and the refreshed validation plan fully discharge the round 1
missing work.

### Implementation report for step 1 version-sources (round 2)

Step 1, "Foundation extensions for the version domain", extends item 1's
release foundation where the version domain needs it. No version command
ships yet: `cli.SHIPPED_HANDLERS` stays empty until Step 9.

Operation tokens (`tools/release_workflow/cli.py`, `invocation.py`):

- `_parse` adds an `operation` positional (`nargs="*"`) and parses with
  `parse_intermixed_args`, so options parse the same before, between and
  after the tokens.
- `Handler` gains `validate_arguments: Callable[[tuple[str, ...]], None] |
  None`. `_select` calls it with the tokens, or raises
  `Release operation '<name>' takes no arguments: ...` when it is `None` and
  tokens exist; `_select` runs before `RuntimeIdentity.load` and
  `create_context`, so a token error is status 2 with no Git process or file
  read.
- `InvocationRequest.operation` and `InvocationContext.operation` (trailing,
  default `()`); `create_context` copies it; the batch-character rule already
  covers every argv token.

Public status 3 (`results.py`, `bootstrap.py`, both launchers):

- `results.render` and `bootstrap.main` accept `{0, 1, 2, 3}`; both
  `bin/release_workflow.bat` and `bin/release_alias.bat` add
  `if "%_release_status%"=="3" goto cleanup` before the normalization line.
  Any other status is still diagnosed with its original value and returned as
  1.
- `test_codepage_tdd.py` adds the cross-site contract of plan decision Q12: it
  parses the set literal checked by `render` and `main` and the pass-through
  lines of both launchers as integers and requires one common set; a
  parametrized counter-test drops status 3 from one site in a synthetic copy
  and shows the agreement breaks.

Held-lock check (`operation_lock.py`):

- `OperationLock.verify_held(declaration) -> PreparedArtifacts` rejects a
  handle that no longer holds the lock, an owner whose process is not
  `current_identity()`, a declaration for another physical project root and
  a lock record not under the declared artifact home; it then calls
  `_require_owned()` inside `_transition()`, which rejects a replaced or
  retained record. Acquisition, release, retention and transfer are
  unchanged.

Typed Git release observations (`git.py`):

- `TagRecord` (frozen: name, object type, peeled commit, own annotation or
  `None` for a lightweight tag).
- `tag_records(*, cwd, merged=None)`: one `for-each-ref` over `refs/tags` with
  six NUL-terminated fixed fields (`%(*objecttype)` included) and an optional
  `--merged=<revision>`; exit 129 whose stderr reports
  `malformed object name <revision>` raises `GitRevisionNotFoundError` (a
  `GitCommandError` carrying the revision, `exit_code = 2`); every other
  failure stays `GitCommandError`. An annotated tag's commit is its
  dereferenced object; when Git dereferences a tag of a tag one level only,
  `_peeled` follows the inner tag object through the same listing, once per
  tag object, and an inner tag object without its own ref raises
  `GitPolicyError` (round 1 finding F1).
- `independent_commits(commits, *, cwd)`: one `merge-base --independent`.
  `_independent_arguments` measures the exact command line `_execute` would
  pass (`subprocess.list2cmdline` over the executable, the fixed `run`
  options, now one shared tuple, and the arguments) in UTF-16 code units plus
  the terminating NUL, and raises `GitCommandLineTooLongError`
  (`exit_code = 1`, naming the limit and the candidate count) above 32,767
  before any call (plan decision Q13).
- `tag_names`, `commit_count` (non-numeric output is a `GitPolicyError`) and
  `listing` (drops names ending with `/`, so an untracked nested repository
  goes and a tracked gitlink stays).
- The two exceptions take the repository's `Error` suffix (ruff N818; every
  exception in the package ends in `Error`); the plan now uses
  `GitRevisionNotFoundError` and `GitCommandLineTooLongError`.

Simulation (`tests/unit/tools/release_workflow/`):

- `repository_simulation.ReleaseHistory` declares commits with parents,
  `HEAD`, `main`, tags (`nested_tag` carries its inner tag's commit) and
  listing names; `RepositoryObservations` answers the
  five methods by reachability over the declared parents, records each call
  and calls the production guard before the tips query. No process is
  started.
- `launcher_simulation._patch_release_observations` routes the five methods to
  the sandbox; `test_release_transport_tdd.py` proves the routing through the
  real bootstrap and also passes status 3 through every entry kind.

Tests first: the eight Step 1 test files failed at collection on the missing
API, then passed. New test file:
`tests/unit/tools/release_workflow/test_git/test_git_releases_tdd.py`.

Writer notes: `.reviews/a.version-sources.step1.journal.md` and
`.reviews/a.version-sources.step1.handoff.md`.

### Change summary for step 1 version-sources (round 2)

Staged paths (20), grouped in the root `a.commit` (five groups, checker
`ready: true`):

1. `feat(release): accept operation tokens per handler`:
   `tools/release_workflow/cli.py`, `tools/release_workflow/invocation.py`,
   `tests/unit/tools/release_workflow/test_cli/test_cli_tdd.py`,
   `tests/unit/tools/release_workflow/test_invocation/test_invocation_tdd.py`.
2. `feat(release): make status 3 a public status`:
   `tools/release_workflow/results.py`, `tools/release_workflow/bootstrap.py`,
   `bin/release_workflow.bat`, `bin/release_alias.bat`,
   `tests/unit/tools/release_workflow/test_results/test_results_tdd.py`,
   `tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py`,
   `tests/unit/tools/release_workflow/test_launchers/test_codepage_tdd.py`.
3. `feat(release): verify a held operation lock`:
   `tools/release_workflow/operation_lock.py`,
   `tests/unit/tools/release_workflow/test_operation_lock/test_operation_lock_tdd.py`.
4. `feat(release): add typed Git release observations`:
   `tools/release_workflow/git.py`,
   `tests/unit/tools/release_workflow/repository_simulation.py`,
   `tests/unit/tools/release_workflow/launcher_simulation.py`,
   `tests/unit/tools/release_workflow/test_git/test_git_releases_tdd.py` (new),
   `tests/unit/tools/release_workflow/test_release_transport/test_release_transport_tdd.py`.
5. `docs(version-sources): record step 1 validation`:
   `docs/v0.14.0/plan.v0.14.0.version-sources.md` (exception names),
   `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md` (Step 1
   sections).

Changes since round 1 (F1): `tools/release_workflow/git.py` (six-field tag
format, `_peeled` within the listing),
`tests/unit/tools/release_workflow/test_git/test_git_releases_tdd.py`
(nested-tag cases, explicit `%(*objecttype)` in every canned record),
`tests/unit/tools/release_workflow/repository_simulation.py` (`nested_tag`),
`docs/v0.14.0/plan.v0.14.0.version-sources.md` (Step 1 format and rule),
`docs/v0.14.0/plan.v0.14.0.version-sources.validation.md` (Step 1 check
refreshed to Yes after the round 1 No) and the bodies of `a.commit` groups 4
and 5. Unstaged: the versioned review transcript, with two formatting-only
Markdown fixes in the round 1 answer.

Before this step, the branch committed the design clarification of plan
decision Q15 (design questions Q18 and Q19, consolidated) in `083ef50`,
`fd1c971` and `0edf3a9`; those commits are not part of this review.

### Writer response for step 1 version-sources (round 2)

Writer response:

F1 is accepted and fixed. The reviewer's validation-plan edit (No verdict,
Missing work, coverage and feature-integrity notes) was the correct state for
round 1; after the fix, the writer refreshed the Step 1 implementation check
to Yes and removed the Missing work section, since both bullets are done.

How F1 is fixed, within the approved query budget and tag policy:

- `tag_records` still makes one `for-each-ref` call. The format gains
  `%(*objecttype)` (six NUL-terminated fields).
- An annotated tag's commit is its dereferenced object. Git versions that
  dereference `%(*...)` one level only report the dereferenced type `tag` for
  a tag of a tag; the parser then follows that inner tag object through the
  other records of the same listing, in any record order. A tag on the same
  commit is always in that listing, with or without `--merged`, because it is
  reachable exactly when the outer tag is.
- The walk remembers the final commit of every tag object it visits, so each
  tag object is followed once and the parse stays linear in the listing.
- An inner tag object with no ref of its own leaves no trustworthy commit in
  the output; that case raises `GitPolicyError` naming the tag, like other
  untrusted Git output. No tag is excluded and no second call is made, so
  neither the four-call ceiling nor the eligibility policy changes.
- Each record keeps its own annotation.

A probe in a scratch repository with the installed Git 2.56 shows that it
already peels a tag of a tag fully (`%(*objecttype)` is `commit`), while the
repository's floor is Git 2.31; both forms are tested.

Regression coverage, all process-free:

- `test_tag_records_peel_a_tag_of_a_tag`, parametrized over full and
  one-level peeling: the outer and inner tags report the same commit, each
  with its own annotation.
- `test_tag_records_peel_a_chain_listed_out_of_order`: three tags of tags,
  outer first, all resolve to the commit.
- `test_tag_records_fail_closed_on_an_unlisted_inner_tag`.
- `test_release_history_nested_and_direct_tags_share_a_commit`: the declared
  history's new `nested_tag` carries its inner tag's commit; both appear in
  `tag_records` and `tag_names` with their own annotations.
- The existing canned records now carry an explicit `%(*objecttype)`, so no
  test assumes the starred object is a commit.

The plan's Step 1 now states the six-field format, the peeling within the
same call and the fail-closed case, and lists the nested-tag tests. `a.commit`
membership and subjects are unchanged; the bodies of groups 4 and 5 describe
the fix.

Formatting-only edits to the versioned review transcript, which stays out of
the staged set for its residual commit: the `<index>` placeholder of the
round 1 answer is quoted as code, and a blank line was added before its
numbered list, because the repository-wide Markdown check of `check.bat`
reported MD033 and MD032 there.

No disagreement with the round 1 answer.

### Reviewer focus for step 1 version-sources (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-1-round-2 -->

## Round 2 by reviewer - Step 1

- Recorded: 2026-11-08T17:04:49+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 1
- Outcome: answer

### Assessed index identity for step 1 version-sources (exchange 1) (round 2)

Baseline index tree: c6059047c28c757d21439750b93debdacbf8a19e

Assessed index tree: ea2197122ff0c14de4479c7aef03b0570c93a73a

### Implementation check for step 1 version-sources (exchange 1) (round 2)

Result:

No. Step 1 has NOT been fully implemented.

The foundation work from round 1 remains present. The new six-field parser correctly follows listed inner tag objects, preserves each annotation, and memoizes successful chains in linear time. The new simulation helper and nested-tag cases are exercised. All changed Python files remain below 650 lines. No DDD-Hexagonal violation was identified.

F1 remains open for valid nested tags whose inner object has no ref. The plan's newly added fail-closed clause changes compatibility rather than resolving that case. Only the reviewed Step 1 validation sections were updated with a No verdict and concrete missing work.

Validation plan effects:

Updated only Step 1 in docs/v0.14.0/plan.v0.14.0.version-sources.validation.md: exact No verdict, summary, Missing work, residual compatibility limitation and test assessment. Pre-edit content was recorded and attribute-reviewer-patch proved attribution before that metadata patch was staged. Other steps and the document-level status are unchanged. No implementation or test repair was made.

### Pre-repair mandatory checks and coverage for step 1 version-sources (exchange 1) (round 2)

The requestor reports a fresh ghog day --full=speed --whole-suite with all stages run, exit 0, full suite and 100% coverage, no duration outlier or exclusion. Focused writer tests also passed. Those are writer results.

The reviewer did not repeat the walk, measure coverage or run ghog check/affected: the unresolved compatibility case is statically visible. The gate measures tools and omits tests. The new _peeled function is exercised by the canned nested cases; the added simulation method is referenced by its unit test. The new unlisted-inner test expects the behavior under dispute, so its passing does not establish the approved commit contract. Bound scope remains whole, proof speed, fingerprint 686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6.

### Resolved validation set and sources for step 1 version-sources (exchange 1) (round 2)

Request and current resolver both require ghog day --full=speed --whole-suite, source project. The exact .review-validation path was sampled as absent; the current helper completed the built-in project default with the whole-suite selector and returned the same set. No plan/request additions are carried. This is requestor validation, not a reviewer command to run.

### Resolver drift and direction for step 1 version-sources (exchange 1) (round 2)

None. The current helper returned {"commands": [{"command": "ghog day --full=speed --whole-suite", "sources": ["project"]}]}, identical to the request.

### Repository state around validation for step 1 version-sources (exchange 1) (round 2)

The live baseline tree matched request tree c6059047c28c757d21439750b93debdacbf8a19e. Final assessed tree is ea2197122ff0c14de4479c7aef03b0570c93a73a.

The umbrella digest is unchanged at 5abf0cb72800e9d07acba786dd90502fcb8879ff41cbcce55b961a95352aaa4c. Before/after snapshots use the identical ordered path set. Generic comparison reports acceptable=false for the reviewed validation plan and the code placeholder `<index>`; attribution accounts for both as the staged Step 1 metadata patch. No other tracked difference or untracked side effect was found in that comparison. The pre-existing unstaged transcript formatting work described by the request was not touched.

### Repair inventory for step 1 version-sources (exchange 1) (round 2)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 1 version-sources (exchange 1) (round 2)

Independent commit-plan-check.bat --format json returned exit 0, state valid, ready true, 20 staged paths and no diagnostics. Its ordered subjects are:

1. feat(release): accept operation tokens per handler
2. feat(release): make status 3 a public status
3. feat(release): verify a held operation lock
4. feat(release): add typed Git release observations
5. docs(version-sources): record step 1 validation

Membership, order, scopes and subjects remain appropriate. No a.commit edit was made. Group 5's body still says the implementation check is Yes; the writer must refresh that explanatory body against the final verdict when resolving F1. Mechanical readiness does not establish semantic completeness or authorize a commit. Full independent JSON is retained in the round-2 commit-plan.json scratch evidence.

### Findings and boundaries for step 1 version-sources (exchange 1) (round 2)

Unresolved findings:

- F1 (P2, carried), tools/release_workflow/git.py:150-152: do not reject valid nested tags solely because the inner tag object has no ref. On the supported Git 2.31, create an annotated inner tag on commit C, create outer annotated tag v1.0.0 on that tag, then delete only the inner ref. The outer tag and all its objects remain valid and reachable. Starred fields return type tag plus the inner object ID, but for-each-ref has no row for that inner object, so `_peeled` now raises GitPolicyError and aborts the entire tag observation. This is valid Git output, not corruption. It can also occur with an irrelevant nested tag because the adapter parses every tag before domain classification. The new test at test_git_releases_tdd.py:138 encodes the rejection rather than proving the promised peeled commit. The approved design does not require every inner object to retain its own ref; adding that failure to the implementation plan alone does not establish such a restriction.

Boundary-crossing work:

- A change to the one-call budget, supported Git floor or accepted tag policy requires explicit design clarification if needed to handle F1; the reviewer has made none of those changes.

### Writer instructions for step 1 version-sources (exchange 1) (round 2)

Keep the successful listed-chain peeling and annotation regression cases. Resolve the valid unreferenced-inner-object case on all supported Git versions, and add process-free cases with and without --merged against the resulting contract. If the current constraints cannot all be satisfied, obtain an explicit design decision before implementing a budget, minimum-version or tag-policy change; do not classify a valid chain as untrusted output solely to preserve one call.

Refresh the plan, Step 1 validation and a.commit explanation, run the writer's required validation, and submit a replacement request. Generic repair wording is not a literal Human guidance block, so no implementation repairs were authorized for this reviewer.

### Decision rationale for step 1 version-sources (exchange 1) (round 2)

Changes requested. Exact identity passes. Completeness and absence of unresolved findings fail on the remaining F1 case. Writer validation is green but its regression expectation does not resolve that contract gap. Step 1 metadata staging is attributable. Mechanical commit-plan readiness passes, with the explanatory body refresh noted above. No substantive reviewer repair was made.

The version-specific assessment is supported by Git v2.31.0 ref-filter.c: lines 1838-1846 use get_tagged_oid once and explicitly say the operation dereferences only once (<https://github.com/git/git/blob/v2.31.0/ref-filter.c#L1838>). The writer's installed Git 2.56 probe does not establish the behavior of the supported floor. This is an advisory review, not commit authorization.

### Final reviewer decision for step 1 version-sources (exchange 1) (round 2)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-1-round-2 -->

## Round 3 by requestor - Step 1

- Recorded: 2026-11-08T18:41:37+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 1
- Outcome: request

### Review identity for step 1 version-sources (round 3)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.version-sources.md
Implementation step: 1
Review round: 3

### Code review evidence for step 1 version-sources (round 3)

request_index_tree: 37e471f91472c617379838f191c92a8582d5ddf8
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.version-sources.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(release): accept operation tokens per handler
group 1 path: tools/release_workflow/cli.py
group 1 path: tools/release_workflow/invocation.py
group 1 path: tests/unit/tools/release_workflow/test_cli/test_cli_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_invocation/test_invocation_tdd.py
group 2: feat(release): make status 3 a public status
group 2 path: tools/release_workflow/results.py
group 2 path: tools/release_workflow/bootstrap.py
group 2 path: bin/release_workflow.bat
group 2 path: bin/release_alias.bat
group 2 path: tests/unit/tools/release_workflow/test_results/test_results_tdd.py
group 2 path: tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py
group 2 path: tests/unit/tools/release_workflow/test_launchers/test_codepage_tdd.py
group 3: feat(release): verify a held operation lock
group 3 path: tools/release_workflow/operation_lock.py
group 3 path: tests/unit/tools/release_workflow/test_operation_lock/test_operation_lock_tdd.py
group 4: docs(version-sources): require Git 2.44 for tag peeling
group 4 path: docs/v0.14.0/design.v0.14.0.version-sources.md
group 5: feat(release): add typed Git release observations
group 5 path: tools/release_workflow/git.py
group 5 path: tests/unit/tools/release_workflow/repository_simulation.py
group 5 path: tests/unit/tools/release_workflow/launcher_simulation.py
group 5 path: tests/unit/tools/release_workflow/test_git/test_git_releases_tdd.py
group 5 path: tests/unit/tools/release_workflow/test_git/test_git_tdd.py
group 5 path: tests/unit/tools/release_workflow/test_paths/test_paths_faults_tdd.py
group 5 path: tests/unit/tools/release_workflow/test_release_transport/test_release_transport_tdd.py
group 6: docs(version-sources): record step 1 validation
group 6 path: docs/v0.14.0/plan.v0.14.0.version-sources.md
group 6 path: docs/v0.14.0/plan.v0.14.0.version-sources.validation.md
staged path: bin/release_alias.bat
staged path: bin/release_workflow.bat
staged path: docs/v0.14.0/design.v0.14.0.version-sources.md
staged path: docs/v0.14.0/plan.v0.14.0.version-sources.md
staged path: docs/v0.14.0/plan.v0.14.0.version-sources.validation.md
staged path: tests/unit/tools/release_workflow/launcher_simulation.py
staged path: tests/unit/tools/release_workflow/repository_simulation.py
staged path: tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py
staged path: tests/unit/tools/release_workflow/test_cli/test_cli_tdd.py
staged path: tests/unit/tools/release_workflow/test_git/test_git_releases_tdd.py
staged path: tests/unit/tools/release_workflow/test_git/test_git_tdd.py
staged path: tests/unit/tools/release_workflow/test_invocation/test_invocation_tdd.py
staged path: tests/unit/tools/release_workflow/test_launchers/test_codepage_tdd.py
staged path: tests/unit/tools/release_workflow/test_operation_lock/test_operation_lock_tdd.py
staged path: tests/unit/tools/release_workflow/test_paths/test_paths_faults_tdd.py
staged path: tests/unit/tools/release_workflow/test_release_transport/test_release_transport_tdd.py
staged path: tests/unit/tools/release_workflow/test_results/test_results_tdd.py
staged path: tools/release_workflow/bootstrap.py
staged path: tools/release_workflow/cli.py
staged path: tools/release_workflow/git.py
staged path: tools/release_workflow/invocation.py
staged path: tools/release_workflow/operation_lock.py
staged path: tools/release_workflow/results.py
```

### Validation scope for step 1 version-sources (round 3)

Validation scope: the whole suite.

### Requestor assessment for step 1 version-sources (round 3)

Writer assessment for Step 1 of the version-sources plan, round 3: the step is
fully implemented. Finding F1 is resolved by the user's explicit decision to
raise the release tooling's Git floor to 2.44, now recorded in the design, so
the one tag listing names the commit of every tag, a tag of a tag whose inner
ref was deleted included. The refreshed implementation check in the staged
validation plan reads `Yes. Step 1 has been fully implemented.`

Evidence on the replacement tree:

- `ghog single` on `test_git_releases_tdd.py`, `test_git_tdd.py`,
  `test_paths_faults_tdd.py` and `test_release_transport_tdd.py`: exit 0.
- `ghog day --full=speed --whole-suite`, the review validation default:
  exit 0, no failure, coverage 100%, no duration outlier, no exclusion
  (check and affected reused by groundhog's own proof). No exclusion is
  accepted in this step.
- Two earlier walks of this round failed only on lifecycle wall-time budgets
  (wall 1.2 to 2.9 s with CPU 0.00 to 0.16 s), each time on different,
  unchanged tests, all green in focus, while another worktree's pytest suite
  kept the machine at 69 to 95% CPU load. The green walk ran in a measured
  quiet window (no foreign pytest, load below 50% on three samples). No
  budget was raised and no test was excluded.
- Markdown check exit 0; `commit-plan-check` ready with no diagnostics; 23
  staged paths in six groups.
- Every Python file stays below 650 lines; `git.py` is 331.

Architecture: the floor stays in the Git adapter's existing version check, and
`tag_records` keeps one call and plain data. Performance: the record parse is
a single linear pass again. Feature integrity: every release command now
refuses Git 2.31 to 2.43 with the reason and the remedy to upgrade; this
behavior change is the user's decision and is recorded as a foundation change
in the design.

Please check in particular: that the floor is enforced for every release
operation through `GitExecutionContext.create`; that the refusal message
explains the requirement; that the design records the decision and the
foundation change adequately; and that the new tests cover a tag of a tag
with and without its inner ref and with and without `--merged`.

### Implementation report for step 1 version-sources (round 3)

Step 1, "Foundation extensions for the version domain", extends item 1's
release foundation where the version domain needs it. No version command
ships yet: `cli.SHIPPED_HANDLERS` stays empty until Step 9.

Operation tokens (`tools/release_workflow/cli.py`, `invocation.py`):

- `_parse` adds an `operation` positional (`nargs="*"`) and parses with
  `parse_intermixed_args`, so options parse the same before, between and
  after the tokens.
- `Handler` gains `validate_arguments: Callable[[tuple[str, ...]], None] |
  None`. `_select` calls it with the tokens, or raises
  `Release operation '<name>' takes no arguments: ...` when it is `None` and
  tokens exist; `_select` runs before `RuntimeIdentity.load` and
  `create_context`, so a token error is status 2 with no Git process or file
  read.
- `InvocationRequest.operation` and `InvocationContext.operation` (trailing,
  default `()`); `create_context` copies it; the batch-character rule already
  covers every argv token.

Public status 3 (`results.py`, `bootstrap.py`, both launchers):

- `results.render` and `bootstrap.main` accept `{0, 1, 2, 3}`; both
  `bin/release_workflow.bat` and `bin/release_alias.bat` add
  `if "%_release_status%"=="3" goto cleanup` before the normalization line.
  Any other status is still diagnosed with its original value and returned as
  1.
- `test_codepage_tdd.py` adds the cross-site contract of plan decision Q12: it
  parses the set literal checked by `render` and `main` and the pass-through
  lines of both launchers as integers and requires one common set; a
  parametrized counter-test drops status 3 from one site in a synthetic copy
  and shows the agreement breaks.

Held-lock check (`operation_lock.py`):

- `OperationLock.verify_held(declaration) -> PreparedArtifacts` rejects a
  handle that no longer holds the lock, an owner whose process is not
  `current_identity()`, a declaration for another physical project root and
  a lock record not under the declared artifact home; it then calls
  `_require_owned()` inside `_transition()`, which rejects a replaced or
  retained record. Acquisition, release, retention and transfer are
  unchanged.

Typed Git release observations (`git.py`):

- `TagRecord` (frozen: name, object type, peeled commit, own annotation or
  `None` for a lightweight tag).
- `tag_records(*, cwd, merged=None)`: one `for-each-ref` over `refs/tags` with
  six NUL-terminated fixed fields (`%(*objecttype)` included) and an optional
  `--merged=<revision>`; exit 129 whose stderr reports
  `malformed object name <revision>` raises `GitRevisionNotFoundError` (a
  `GitCommandError` carrying the revision, `exit_code = 2`); every other
  failure stays `GitCommandError`. An annotated tag's commit is its
  dereferenced object, which Git 2.44 or later peels fully, a tag of a tag
  included, even when the inner ref was deleted; a record still dereferenced
  to a tag object can only come from an older Git and is refused with the
  floor's reason (findings F1 of rounds 1 and 2).
- Git floor: `_MINIMUM_VERSION` is `(2, 44, 0)` (user decision of
  2026-11-08, recorded in the design). `GitExecutionContext.create` refuses
  an older Git before any operation, stating the floor, the reason (only Git
  2.44 or later peels a tag of a tag to its commit in the one tag listing)
  and the remedy to upgrade.
- `independent_commits(commits, *, cwd)`: one `merge-base --independent`.
  `_independent_arguments` measures the exact command line `_execute` would
  pass (`subprocess.list2cmdline` over the executable, the fixed `run`
  options, now one shared tuple, and the arguments) in UTF-16 code units plus
  the terminating NUL, and raises `GitCommandLineTooLongError`
  (`exit_code = 1`, naming the limit and the candidate count) above 32,767
  before any call (plan decision Q13).
- `tag_names`, `commit_count` (non-numeric output is a `GitPolicyError`) and
  `listing` (drops names ending with `/`, so an untracked nested repository
  goes and a tracked gitlink stays).
- The two exceptions take the repository's `Error` suffix (ruff N818; every
  exception in the package ends in `Error`); the plan now uses
  `GitRevisionNotFoundError` and `GitCommandLineTooLongError`.

Simulation (`tests/unit/tools/release_workflow/`):

- `repository_simulation.ReleaseHistory` declares commits with parents,
  `HEAD`, `main`, tags (`nested_tag` carries its inner tag's commit) and
  listing names; `RepositoryObservations` answers the
  five methods by reachability over the declared parents, records each call
  and calls the production guard before the tips query. No process is
  started.
- `launcher_simulation._patch_release_observations` routes the five methods to
  the sandbox; `test_release_transport_tdd.py` proves the routing through the
  real bootstrap and also passes status 3 through every entry kind.

Tests first: the eight Step 1 test files failed at collection on the missing
API, then passed. New test file:
`tests/unit/tools/release_workflow/test_git/test_git_releases_tdd.py`.

Writer notes: `.reviews/a.version-sources.step1.journal.md` and
`.reviews/a.version-sources.step1.handoff.md`.

### Change summary for step 1 version-sources (round 3)

Staged paths (23), grouped in the root `a.commit` (six groups, checker
`ready: true`):

1. `feat(release): accept operation tokens per handler`:
   `tools/release_workflow/cli.py`, `tools/release_workflow/invocation.py`,
   `tests/unit/tools/release_workflow/test_cli/test_cli_tdd.py`,
   `tests/unit/tools/release_workflow/test_invocation/test_invocation_tdd.py`.
2. `feat(release): make status 3 a public status`:
   `tools/release_workflow/results.py`, `tools/release_workflow/bootstrap.py`,
   `bin/release_workflow.bat`, `bin/release_alias.bat`,
   `tests/unit/tools/release_workflow/test_results/test_results_tdd.py`,
   `tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py`,
   `tests/unit/tools/release_workflow/test_launchers/test_codepage_tdd.py`.
3. `feat(release): verify a held operation lock`:
   `tools/release_workflow/operation_lock.py`,
   `tests/unit/tools/release_workflow/test_operation_lock/test_operation_lock_tdd.py`.
4. `docs(version-sources): require Git 2.44 for tag peeling`:
   `docs/v0.14.0/design.v0.14.0.version-sources.md` (new in this round).
5. `feat(release): add typed Git release observations`:
   `tools/release_workflow/git.py`,
   `tests/unit/tools/release_workflow/repository_simulation.py`,
   `tests/unit/tools/release_workflow/launcher_simulation.py`,
   `tests/unit/tools/release_workflow/test_git/test_git_releases_tdd.py` (new),
   `tests/unit/tools/release_workflow/test_git/test_git_tdd.py` (new in this
   round), `tests/unit/tools/release_workflow/test_paths/test_paths_faults_tdd.py`
   (new in this round),
   `tests/unit/tools/release_workflow/test_release_transport/test_release_transport_tdd.py`.
6. `docs(version-sources): record step 1 validation`:
   `docs/v0.14.0/plan.v0.14.0.version-sources.md`,
   `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md`.

Changes since round 2 (F1 carried, resolved by the user's Git 2.44 floor
decision): `tools/release_workflow/git.py` (floor 2.44.0 with an explained
refusal, record dereferenced to a tag refused with the same reason, `_peeled`
removed), `test_git_releases_tdd.py` (tag of a tag with and without its inner
ref and `--merged`, one-level dereference refused, one-level and chain cases
removed), `test_git_tdd.py` (floor and stated reason),
`test_paths_faults_tdd.py` (contexts at the new floor), the design (decision
and foundation change), plan Step 1, validation plan Step 1 (refreshed to Yes
after the round 2 No) and `a.commit` (new group 4, group 5 membership and
body, group 6 body). Unstaged: the versioned review transcript, with the
formatting-only Markdown fixes described in round 2.

Before this step, the branch committed the design clarification of plan
decision Q15 (design questions Q18 and Q19, consolidated) in `083ef50`,
`fd1c971` and `0edf3a9`; those commits are not part of this review.

### Writer response for step 1 version-sources (round 3)

Writer response:

F1 (carried) is accepted, and it is resolved by an explicit decision, as round
2 required. The writer verified the version boundary in Git's sources:
`ref-filter.c` at v2.43.0 dereferences `%(*...)` once (`get_tagged_oid`, with a
NEEDSWORK comment on nested tags), and v2.44.0 peels fully
(`peel_iterated_oid`). The user was offered three options (a second call only
when needed, raising the Git floor to 2.44, or making the failure a stated
policy) and chose to raise the floor to 2.44, asking that the refusal explain
why 2.44 is mandatory and that it be enforced.

Resulting contract and implementation:

- `_MINIMUM_VERSION` is `(2, 44, 0)`. `GitExecutionContext.create`, through
  which every release operation selects its Git, refuses an older Git before
  any operation with the floor, the reason and the remedy, for example:
  "Git version 2.43.9 at ... is older than required 2.44.0: release range
  selection reads every tag with its commit in one `git for-each-ref` call,
  and only Git 2.44 or later peels a tag of a tag to its commit there (older
  Git stops at the inner tag). Upgrade Git to 2.44 or later."
- `tag_records` keeps one call and the six-field format. With the floor, the
  dereferenced object is always the commit, including for a tag of a tag
  whose inner ref was deleted; no valid tag is refused and no call is added.
  A record still reporting the dereferenced type `tag` can only come from an
  older Git, so it is refused with the same reason (a guard behind the floor,
  not a tag policy).
- The listing walk of round 2 (`_peeled`) is removed.
- The decision is recorded in the design: "Git queries of the selector"
  explains why the tag listing needs Git 2.44 and how an older Git is refused,
  and the foundation changes table lists the raised minimum (item 1's 2.31.0,
  its decision Q11, becomes 2.44.0). Item 1's own documents stay as its
  historical record, as for the earlier status 3 foundation change. The
  plan's Step 1 and the validation plan follow.

Regression coverage replaces the disputed expectation:

- `test_tag_records_peel_a_tag_of_a_tag`: a tag of a tag with and without its
  inner tag's row (inner ref deleted), each with and without `--merged`; the
  outer record reports the commit with its own annotation, and the call
  vector carries the filter.
- `test_tag_records_reject_a_one_level_dereference`: the floor's reason.
- `test_git_before_2_44_is_refused_with_its_reason`, and the version tests
  now use 2.44.0 as the floor (2.43.9 and 2.31.0 refused).
- `test_release_history_nested_and_direct_tags_share_a_commit` also deletes
  the inner tag and checks the outer tag with and without the filter.
- `test_paths_faults_tdd.py` builds its contexts at the new floor.

`a.commit` gains a group for the design decision before the Git group, and
the Git group gains the two version-test files; group 6's body now describes
the floor rather than a Yes verdict made before the fix.

No disagreement with the round 2 answer.

### Reviewer focus for step 1 version-sources (round 3)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-1-round-3 -->

## Round 3 by reviewer - Step 1

- Recorded: 2026-11-08T18:48:47+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 1
- Outcome: answer

### Assessed index identity for step 1 version-sources (exchange 1) (round 3)

Baseline index tree: 37e471f91472c617379838f191c92a8582d5ddf8

Assessed index tree: 89552c548fc09df80b7d79ee459ef04277330186

### Implementation check for step 1 version-sources (exchange 1) (round 3)

Result:

Yes. Step 1 has been fully implemented.

F1 is resolved under the explicit Git 2.44 decision recorded in the design. Git v2.43.0 dereferences one tag layer; v2.44.0 uses `peel_iterated_oid`. The adapter enforces `(2, 44, 0)` in `GitExecutionContext.create` before root inspection and handler execution. Its refusal names the detected version, required version, nested-tag reason and upgrade remedy. The parser now reads the fully peeled object in one linear pass, without requiring an inner ref.

The revised unit tests cover nested tags with and without their inner ref, each with and without `--merged`, annotation ownership, the defensive one-level-output refusal, and acceptance/refusal at the version boundary. Prior-round foundation coverage remains applicable: only the seven declared implementation/document paths changed from the round 2 request tree. The operation tokens, public status 3, held-lock verification and simulated observations remain present. No architecture, complexity, file-size or static test-coverage blocker remains.

Validation plan effects:

Updated only the reviewed Step 1 `What was implemented` section of `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md` with the independent round 3 reassessment. Retained the exact Yes verdict and the other steps unchanged. No missing-work section remains for Step 1. The umbrella digest is unchanged. The attributable metadata patch is staged; it is polishing-only review metadata, with no code, test, acceptance or grouping change.

### Pre-repair mandatory checks and coverage for step 1 version-sources (exchange 1) (round 3)

No implementation or test repair was authorized or made; the request has no literal `Human guidance:` block. No reviewer test or coverage command was needed or run. The requestor reports `ghog day --full=speed --whole-suite` green on the replacement tree with 100% measured coverage and no exclusions or duration outliers. Earlier timing-only failures and the final quiet-window run are disclosed in the current request.

Static review confirms the coverage gate measures `tools` and omits tests. The changed production branches have unit-test references; the simulation helpers outside that gate are exercised by the declared-history and transport tests. The request's whole-suite speed scope is bound at `.reviews/a.review-scope.code.v0.14.0.version-sources.json`, fingerprint `686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6`.

### Resolved validation set and sources for step 1 version-sources (exchange 1) (round 3)

The request and the current resolver both return `ghog day --full=speed --whole-suite`, source `project`. The exact `.review-validation` marker was sampled absent. This set is requestor-owned and was not executed by the reviewer.

### Resolver drift and direction for step 1 version-sources (exchange 1) (round 3)

None. The current resolver command and source exactly match the request's resolved validation set.

### Repository state around validation for step 1 version-sources (exchange 1) (round 3)

The request-time tree and fresh baseline both equal `37e471f91472c617379838f191c92a8582d5ddf8`. The ordered validation-state comparison reports only the validation plan and `<index>` changed, explained by the attributed Step 1 metadata patch. No other tracked or untracked path in the compared set changed. The unchanged umbrella SHA-256 is `5abf0cb72800e9d07acba786dd90502fcb8879ff41cbcce55b961a95352aaa4c`. Pre-existing transcript work was left alone and was not used as assessment context.

### Repair inventory for step 1 version-sources (exchange 1) (round 3)

Repairs made:

- Polishing-only: added the independent reassessment note to the exact Step 1 validation metadata. No implementation, test, acceptance behavior or commit grouping changed.

Paths staged:

- `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md`

### Commit plan assessment for step 1 version-sources (exchange 1) (round 3)

Independent `commit-plan-check.bat --format json`: exit 0, state `valid`, `ready: true`, 23 staged paths and no diagnostics. Six ordered groups:

1. `feat(release): accept operation tokens per handler`
2. `feat(release): make status 3 a public status`
3. `feat(release): verify a held operation lock`
4. `docs(version-sources): require Git 2.44 for tag peeling`
5. `feat(release): add typed Git release observations`
6. `docs(version-sources): record step 1 validation`

Membership, dependencies and conventional subjects match the staged work. The design decision precedes its implementation, and the final documentation group follows both. The refreshed bodies describe the current floor and Yes result accurately. The attributable reviewer note adds no path or group, so `a.commit` remains accurate and was not edited.

### Findings and boundaries for step 1 version-sources (exchange 1) (round 3)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 1 version-sources (exchange 1) (round 3)

No rework requested for this step. The commit-ready recommendation is advisory; only the requestor's human convergence gate can authorize a commit. The reviewer does not confirm, commit or continue the writer workflow.

### Decision rationale for step 1 version-sources (exchange 1) (round 3)

Advisory commit-ready. All six readiness results pass: exact identity and request-tree match; Step 1 complete under the recorded decision; writer green validation and static coverage assessment with no gap; attributable metadata-only staging; no unresolved current or carried finding; accurate independent commit-plan result. No substantive reviewer repair was made.

The version boundary was independently checked against [Git v2.43.0 source](https://github.com/git/git/blob/v2.43.0/ref-filter.c) and [Git v2.44.0 source](https://github.com/git/git/blob/v2.44.0/ref-filter.c). The old source calls `get_tagged_oid` once and contains the one-level NEEDSWORK comment; the new source calls `peel_iterated_oid`. This recommendation never authorizes a commit.

### Final reviewer decision for step 1 version-sources (exchange 1) (round 3)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-1-round-3 -->

## Round 3 by human - Step 1 - human-confirmation

- Recorded: 2026-11-08T19:35:56+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 1
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-3 -->

## Round 1 by requestor - Step 2

- Recorded: 2026-11-08T21:54:34+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Implementation step: 2
- Outcome: request

### Review identity for step 2 version-sources (round 1)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.version-sources.md
Implementation step: 2
Review round: 1

### Code review evidence for step 2 version-sources (round 1)

request_index_tree: 4d5a54318ed1e5a62f4737436e3a4af30cf5c395
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.version-sources.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(release): add the version source model
group 1 path: tools/release_workflow/sources/model.py
group 1 path: tests/unit/tools/release_workflow/version_support.py
group 1 path: tests/unit/tools/release_workflow/test_version_model/__init__.py
group 1 path: tests/unit/tools/release_workflow/test_version_model/test_version_model_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_version_model/test_version_model_pbt.py
group 2: feat(release): add the version.txt anchor adapter
group 2 path: tools/release_workflow/sources/anchor.py
group 2 path: tools/release_workflow/sources/__init__.py
group 2 path: tests/unit/tools/release_workflow/test_version_anchor/__init__.py
group 2 path: tests/unit/tools/release_workflow/test_version_anchor/test_version_anchor_tdd.py
group 2 path: tests/unit/tools/release_workflow/test_version_anchor/test_version_anchor_pbt.py
group 2 path: tests/unit/tools/release_workflow/test_version_registry/__init__.py
group 2 path: tests/unit/tools/release_workflow/test_version_registry/test_version_registry_tdd.py
group 3: docs(version-sources): record step 2 validation
group 3 path: docs/v0.14.0/plan.v0.14.0.version-sources.validation.md
group 3 path: .vscode/settings.json
staged path: .vscode/settings.json
staged path: docs/v0.14.0/plan.v0.14.0.version-sources.validation.md
staged path: tests/unit/tools/release_workflow/test_version_anchor/__init__.py
staged path: tests/unit/tools/release_workflow/test_version_anchor/test_version_anchor_pbt.py
staged path: tests/unit/tools/release_workflow/test_version_anchor/test_version_anchor_tdd.py
staged path: tests/unit/tools/release_workflow/test_version_model/__init__.py
staged path: tests/unit/tools/release_workflow/test_version_model/test_version_model_pbt.py
staged path: tests/unit/tools/release_workflow/test_version_model/test_version_model_tdd.py
staged path: tests/unit/tools/release_workflow/test_version_registry/__init__.py
staged path: tests/unit/tools/release_workflow/test_version_registry/test_version_registry_tdd.py
staged path: tests/unit/tools/release_workflow/version_support.py
staged path: tools/release_workflow/sources/__init__.py
staged path: tools/release_workflow/sources/anchor.py
staged path: tools/release_workflow/sources/model.py
```

### Validation scope for step 2 version-sources (round 1)

Validation scope: the whole suite.

### Requestor assessment for step 2 version-sources (round 1)

Writer assessment for Step 2 of the version-sources plan, round 1: the step is
fully implemented, and its implementation check records
`Yes. Step 2 has been fully implemented.` in the staged validation plan.

Evidence, all on the staged tree:

- Tests first: with `tools/release_workflow/sources` moved aside, `ghog
  single` on the three Step 2 test folders failed at collection (five
  modules, `ImportError`, exit 4), then passed after the implementation.
- `ghog day --whole-suite`, the command printed by `pw scope day`, exit 0
  (check.bat: ty, pyright, ruff, radon, vulture, file size, Markdown,
  ShellCheck, end-of-file; affected tests green). A first run failed only on
  ruff RUF043 in two test `match=` patterns, made raw and escaped.
- `ghog day --full=speed --whole-suite`, the review validation default:
  exit 0, no failure, coverage 100%, no duration outlier, no exclusion (check
  and affected reused by groundhog's proof); it ran in a measured quiet
  window (no other checkout's pytest, load below 50% on three samples). No
  exclusion is accepted in this step.
- Completion checks: `rg -n 'open\(|write_bytes|write_text'
  tools/release_workflow/sources` finds nothing; the synthetic-listing test
  reports an unregistered adapter module.
- Spell check of the 14 staged files: one unknown word (`nargs`), added to
  `.vscode/settings.json` at the user's choice; rechecked, none left.
- Every file stays below 650 lines; `model.py` is 390.

Architecture: the model is plain values and pure functions plus the
read-only `FileView` the plan places there; the anchor depends only on the
model and never writes; foundation types are imported for type checking
only. Performance: one load, decode and scan per file per phase; the only
sorts are over one file's few owned spans. Feature integrity: no existing
module changes and nothing ships.

Please check in particular: the token grammar and its remedy, the anchor's
first-line rule (token, optionally whitespace, `--` and a title; anything
else malformed, trailing whitespace alone included), the root-only anchor
detection through `AdapterSettings.project_root`, `compose` and
`to_byte_spans` exactness, and whether the Q16 shared types are what Steps 3
and 4 need.

### Implementation report for step 2 version-sources (round 1)

Step 2, "Version tokens, the anchor document and the source model", creates
the `tools/release_workflow/sources` package. Nothing ships yet:
`cli.SHIPPED_HANDLERS` stays empty and no existing module imports the package.

Model (`sources/model.py`, standard library only at run time):

- `VersionToken.parse` accepts `MAJOR.MINOR.PATCH` with an optional uppercase
  `-SNAPSHOT`, no leading zeros, no `v`; `VersionError` (status 2) names the
  grammar. `core`, `key` (integer triple, the only order) and `__str__`.
- `Form` (`StrEnum`: `snapshot`, `core`, `release-only`) with `parse` and
  `expected(anchor)`; `check_release_only(source, anchor)` refuses a
  release-only value above the target's core, naming source, value and
  target, and fails a value that is not a release token as malformed; other
  forms are not guarded there.
- `Span` (half-open, validated), `LocatedSource` (path, field, adapter, form,
  value, spans, root, paired manifest), `VisibleRecord` (status
  `not-participating tool-only` or `not-participating undeclared`),
  `Detection`, `SourceError` (status 2).
- `decode_utf8` (strict UTF-8, byte-order mark returned apart) and `FileView`
  (`read` caches each path once, absence as `None`; `text` decodes and names
  the file on failure; `loads` counts loads per path).
- `AdapterSettings` (a protocol exposing `project_root`) and `Adapter` (name,
  default form, forms, manifest names, `detect(root, view, settings)`,
  `render(source, value)`, `has_project_version(name, content)`).
- `compose(original, edits)` sorts one file's edits, rejects a span past the
  end or overlapping another, and joins slices of the one original.
- `to_byte_spans(text, bom_length, spans)` sorts the distinct offsets once and
  encodes each segment between consecutive offsets once.
- Plan decision Q16 types: `VersionInputs.from_context`, `FileCapture.of`
  (SHA-256 of present bytes, `None` when absent), `SourceChange`, `FileEdit`
  (refuses unchanged bytes), `Claim`, `Inventory`, `Plan`. Foundation types
  are imported for type checking only.

Anchor (`sources/anchor.py`):

- `parse_document(content)` decodes, splits the first line (CR removed only
  from a CRLF terminator), and requires the token optionally followed by
  whitespace, `--` and a title; anything else is malformed with a remedy. The
  title is stripped; the notes are everything after the first terminator,
  unchanged; the token's byte span starts after the byte-order mark.
- `ADAPTER` (`AnchorAdapter`, frozen): name `anchor`, located form
  `snapshot`, no configurable form, no candidate names. `detect` returns
  nothing for a root other than `settings.project_root`, fails a missing file
  with a remedy, wraps every parse failure with the path (status 2), reads the
  file once and returns one `LocatedSource`. `render` returns the raw token.

Registry (`sources/__init__.py`): `ADAPTERS = (anchor.ADAPTER,)` and
`SUPPORT_MODULES = frozenset({"model"})`. The registry test lists the
package's modules and requires each adapter module's `ADAPTER` exactly once;
a synthetic listing with an unregistered module, a duplicate or an entry
without a module is reported.

Two additions the plan's list implies, recorded in the validation plan:
`AdapterSettings`, so root-only adapters (the anchor now, Step 3's pattern
adapter) know the project root, which Step 3's `VersionSettings` satisfies
structurally; and `Claim`, the element of `Inventory.claims`.

Tests first: with the package moved aside, the three Step 2 test folders
failed at collection, then passed after the implementation. Property tests
(25 examples each): token round trip and order, composition against
right-to-left replacement, anchor token replacement over generated titles,
notes, line endings and byte-order marks.

Spell check: one unknown word, `nargs` (the argparse parameter named in the
validation plan's Step 1 text); the user chose to add it to
`.vscode/settings.json`.

Writer notes: `.reviews/a.version-sources.step2.journal.md` and
`.reviews/a.version-sources.step2.handoff.md`.

### Change summary for step 2 version-sources (round 1)

Staged paths (14), grouped in the root `a.commit` (three groups, checker
`ready: true`):

1. `feat(release): add the version source model`:
   `tools/release_workflow/sources/model.py`,
   `tests/unit/tools/release_workflow/version_support.py`,
   `tests/unit/tools/release_workflow/test_version_model/__init__.py`,
   `tests/unit/tools/release_workflow/test_version_model/test_version_model_tdd.py`,
   `tests/unit/tools/release_workflow/test_version_model/test_version_model_pbt.py`.
2. `feat(release): add the version.txt anchor adapter`:
   `tools/release_workflow/sources/anchor.py`,
   `tools/release_workflow/sources/__init__.py`,
   `tests/unit/tools/release_workflow/test_version_anchor/__init__.py`,
   `tests/unit/tools/release_workflow/test_version_anchor/test_version_anchor_tdd.py`,
   `tests/unit/tools/release_workflow/test_version_anchor/test_version_anchor_pbt.py`,
   `tests/unit/tools/release_workflow/test_version_registry/__init__.py`,
   `tests/unit/tools/release_workflow/test_version_registry/test_version_registry_tdd.py`.
3. `docs(version-sources): record step 2 validation`:
   `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md` (Step 2
   sections), `.vscode/settings.json` (`nargs` added to `cSpell.words`).

Group 1 is importable on its own: without `__init__.py`, `sources` is a
namespace package. Every file except the validation plan and the settings is
new. Before this step, the branch committed Step 1 (`a7c0d7c` to `c609947`),
which is not part of this review.

### Writer response for step 2 version-sources (round 1)

Writer response:

This is the first round of the Step 2 code review; there is no earlier
reviewer feedback to answer.

Choices worth checking, all within the plan:

- The anchor's `LocatedSource.form` is `snapshot`, because its expected value
  is the whole target token; its configurable `forms` set is empty, so no
  `[source:anchor]` override can be valid.
- A first line with only trailing whitespace after the token (`0.14.0[space]`) is
  malformed: the design allows "whitespace, `--` and the title" together, and
  anything else after the token is malformed.
- `compose` and `to_byte_spans` sort per-file spans or offsets, a handful of
  owned fields, as the plan prescribes; nothing sorts or rescans file content.
- `check_release_only` returns for forms other than `release-only`; drift of
  a `core` or `snapshot` source is the transition's and `check`'s concern in
  later steps.

### Reviewer focus for step 2 version-sources (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-2-round-1 -->

## Round 1 by reviewer - Step 2

- Recorded: 2026-11-08T22:00:53+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 2
- Outcome: answer

### Assessed index identity for step 2 version-sources (exchange 1) (round 1)

Baseline index tree: 4d5a54318ed1e5a62f4737436e3a4af30cf5c395

Assessed index tree: f6d10cd6a193ecb0440d651cd910c6329ccfdb76

### Implementation check for step 2 version-sources (exchange 1) (round 1)

Result:

Yes. Step 2 has been fully implemented.

The staged model, anchor adapter and registry implement the exact plan step. Token parsing enforces the decimal triple, uppercase optional suffix, leading-zero rule and complete-input match; comparison uses the numeric core key. Forms and the release-only guard implement the expected mappings and refusals. The anchor rejects trailing text or whitespace without the separator, accepts empty titles, detects only the configured project root, and retains the token's byte span, BOM, notes and line endings. Composition rejects outside and overlapping spans; character-to-byte mapping handles accented and non-BMP text without repeatedly encoding prefixes.

The new values and protocols are VersionToken, Form, Span, LocatedSource, VisibleRecord, Detection, FileView, AdapterSettings, Adapter, VersionInputs, FileCapture, SourceChange, FileEdit, Claim, Inventory, Plan, VersionDocument and AnchorAdapter, with VersionError and SourceError. The Q16 types provide Steps 3 and 4 with shared inputs, claims, captures and edits without a dependency on the later transition.

Architecture: the anchor depends on the common model and reads through the injected view; foundation imports are for type checking only. No adapter writes, takes a lock or starts a process. No architecture issue needs addressing.

Performance: each view caches present and absent bytes; span mapping encodes disjoint segments and composition joins original slices. Sorting is confined to one file's spans or offsets as planned. No performance issue needs addressing.

Unit coverage was assessed statically from the named model, anchor and registry tests and property tests. The gate measures `tools`, omitting tests and initializers. Test support's top-level helpers are all referenced; the omitted registry declarations are exercised explicitly. No coverage gap or unreferenced top-level symbol was identified. The writer reports 100% measured coverage; the reviewer did not measure it.

Feature integrity: the new package remains unshipped, with no existing production module modified. No existing feature or reporting capability appears impaired.

Validation plan effects:

Updated only Step 2's "What was implemented" section in `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md` with this independent assessment and the distinction between writer-executed evidence and static reviewer coverage assessment. The exact Yes verdict remains. Other steps, document-level status and umbrella remain unchanged. Markdown validation passed.

### Pre-repair mandatory checks and coverage for step 2 version-sources (exchange 1) (round 1)

The request reports tests first failing at collection without the package, then passing with it; `ghog day --whole-suite` green; and the required `ghog day --full=speed --whole-suite` green with 100% measured coverage, no exclusions and no duration outliers. The earlier ruff pattern failure was corrected before publication. These are writer reports on the staged tree, not reviewer-executed tests.

Reviewer commands: no tests, coverage, ghog check or affected run. Static code and test assessment supplied the needed review evidence.

### Resolved validation set and sources for step 2 version-sources (exchange 1) (round 1)

Current resolver: `ghog day --full=speed --whole-suite`, source `project`. This exactly matches the request's resolved set. Bound scope is the core-owned `.reviews/a.review-scope.code.v0.14.0.version-sources.json`, whole suite, speed proof, fingerprint `686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6`. The request identity and envelope agree, including plan, umbrella, step 2 and round 1.

### Resolver drift and direction for step 2 version-sources (exchange 1) (round 1)

No drift. No added, removed or changed commands or source labels. The `.review-validation` marker was sampled absent.

### Repository state around validation for step 2 version-sources (exchange 1) (round 1)

Request-time and baseline index trees match: `4d5a54318ed1e5a62f4737436e3a4af30cf5c395`. Assessed index tree: `f6d10cd6a193ecb0440d651cd910c6329ccfdb76`.

The evidence comparison reports tracked differences only for the reviewed validation plan and `<index>`, with no untracked or ignored differences in the captured path set. Its raw `acceptable: false` reflects the explicitly staged reviewer metadata patch; attribution proves that patch cleanly attributable, and inspection confines it to Step 2's assessment note. No implementation or test change was made. The umbrella digest is unchanged: `5abf0cb72800e9d07acba786dd90502fcb8879ff41cbcce55b961a95352aaa4c`.

### Repair inventory for step 2 version-sources (exchange 1) (round 1)

Repairs made:

- Polishing-only review metadata: added the independent assessment note to Step 2 of `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md`; no substantive repair.

Paths staged:

- `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md`: staged only the exact patch returned by the evidence attribution operation.

### Commit plan assessment for step 2 version-sources (exchange 1) (round 1)

Independent `commit-plan-check.bat --format json` returned exit 0, `state: valid`, `ready: true`, 14 staged paths and no diagnostics. Its ordered groups match the received `a.commit`:

1. `feat(release): add the version source model` (5 paths).
2. `feat(release): add the version.txt anchor adapter` (7 paths).
3. `docs(version-sources): record step 2 validation` (2 paths, including the user-approved dictionary word).

Membership, dependency order, scope and subjects remain accurate after the validation metadata note. No `a.commit` edit was needed.

### Findings and boundaries for step 2 version-sources (exchange 1) (round 1)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 2 version-sources (exchange 1) (round 1)

No implementation rework requested. Process this advisory answer through the existing requestor convergence gate. Commit authorization remains the human's decision.

### Decision rationale for step 2 version-sources (exchange 1) (round 1)

All six readiness-floor results pass: exact identity; complete Step 2 implementation; writer-reported validation and static coverage assessment; attributable staged scope; no unresolved findings; and accurate, independently checked commit grouping. The reviewer made only a polishing metadata update. Recommend commit-ready; this is advisory and does not authorize a commit.

The current request has no literal Human guidance block authorizing implementation or test repair. None was performed.

### Final reviewer decision for step 2 version-sources (exchange 1) (round 1)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-2-round-1 -->

## Round 1 by human - Step 2 - human-confirmation

- Recorded: 2026-11-08T23:40:07+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 2
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-1 -->

## Round 1 by requestor - Step 3

- Recorded: 2026-11-09T11:18:36+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Implementation step: 3
- Outcome: request

### Review identity for step 3 version-sources (round 1)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.version-sources.md
Implementation step: 3
Review round: 1

### Code review evidence for step 3 version-sources (round 1)

request_index_tree: 6767623c8a6ed2f73a75f6c3e4e56a4ad3b3475e
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.version-sources.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(release): add declared pattern sources
group 1 path: tools/release_workflow/sources/model.py
group 1 path: tools/release_workflow/sources/pattern.py
group 1 path: tools/release_workflow/sources/__init__.py
group 1 path: tests/unit/tools/release_workflow/version_support.py
group 1 path: tests/unit/tools/release_workflow/test_pattern_sources/__init__.py
group 1 path: tests/unit/tools/release_workflow/test_pattern_sources/test_pattern_sources_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_pattern_sources/test_pattern_sources_pbt.py
group 1 path: tests/unit/tools/release_workflow/test_version_registry/test_version_registry_tdd.py
group 2: feat(release): validate version configuration
group 2 path: tools/release_workflow/sources/settings.py
group 2 path: tools/release_workflow/schemas.py
group 2 path: tests/unit/tools/release_workflow/test_version_settings/__init__.py
group 2 path: tests/unit/tools/release_workflow/test_version_settings/test_version_settings_tdd.py
group 2 path: tests/unit/tools/release_workflow/test_schemas/test_schemas_tdd.py
group 3: feat(release): combine detectors and claims
group 3 path: tools/release_workflow/sources/detection.py
group 3 path: tests/unit/tools/release_workflow/test_version_detection/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_version_detection/test_version_detection_tdd.py
group 4: docs(version-sources): record step 3 validation
group 4 path: docs/v0.14.0/plan.v0.14.0.version-sources.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.version-sources.validation.md
staged path: tests/unit/tools/release_workflow/test_pattern_sources/__init__.py
staged path: tests/unit/tools/release_workflow/test_pattern_sources/test_pattern_sources_pbt.py
staged path: tests/unit/tools/release_workflow/test_pattern_sources/test_pattern_sources_tdd.py
staged path: tests/unit/tools/release_workflow/test_schemas/test_schemas_tdd.py
staged path: tests/unit/tools/release_workflow/test_version_detection/__init__.py
staged path: tests/unit/tools/release_workflow/test_version_detection/test_version_detection_tdd.py
staged path: tests/unit/tools/release_workflow/test_version_registry/test_version_registry_tdd.py
staged path: tests/unit/tools/release_workflow/test_version_settings/__init__.py
staged path: tests/unit/tools/release_workflow/test_version_settings/test_version_settings_tdd.py
staged path: tests/unit/tools/release_workflow/version_support.py
staged path: tools/release_workflow/schemas.py
staged path: tools/release_workflow/sources/__init__.py
staged path: tools/release_workflow/sources/detection.py
staged path: tools/release_workflow/sources/model.py
staged path: tools/release_workflow/sources/pattern.py
staged path: tools/release_workflow/sources/settings.py
```

### Validation scope for step 3 version-sources (round 1)

Validation scope: the whole suite.

### Requestor assessment for step 3 version-sources (round 1)

Writer assessment for Step 3 of the version-sources plan, round 1: the step is
fully implemented, and its implementation check records
`Yes. Step 3 has been fully implemented.` in the staged validation plan.

Evidence, all on the staged tree:

- Tests first: `ghog single` on the three new Step 3 test folders with the
  updated schema and registry tests failed at collection (six `ImportError`s,
  exit 4), then passed after the implementation, together with the item 1
  configuration tests and the Step 2 anchor and model tests. The property test
  first exceeded the 0.1 s CPU lifecycle budget (0.234 s) and was redrawn from
  one integer, the cheapest encoding, keeping 25 examples.
- `ghog day --whole-suite`, the command printed by `pw scope day`, exit 0
  (check.bat and 298 affected tests). A first run failed only at check.bat:
  an unused test import, a test constant named like a token (S105), a dataclass
  call default (RUF009), a `noqa` lost when ruff rewrapped the deferred import,
  and radon grade C on `candidates`, split into two helpers.
- `ghog day --full=speed --whole-suite`, the review validation default: exit
  0, no failure, coverage 100%, no duration outlier, no exclusion (check and
  affected reused by groundhog's proof); it ran in a measured quiet window (no
  other checkout's pytest, load below 50% on three samples). No exclusion is
  accepted in this step.
- Completion checks: `rg -n 'import tools.release_workflow.sources|from
  tools.release_workflow.sources' tools/release_workflow/schemas.py` shows
  only the deferred import inside `_validate_version`; the item 1
  configuration tests pass unchanged.
- Markdown lint and spell check of the staged validation plan: no finding, no
  unknown word.
- Every file stays below 650 lines; `detection.py` is 180, `model.py` 410.

Architecture: `schemas.py` keeps no load-time domain import; settings works on
the loader's mappings and reads no file; the pattern adapter depends only on
the model and never writes; detection reads through the injected view and
reaches Git only through `VersionInputs.git`. Performance: claims are indexed
by path and field, only one file's few spans are sorted, the CRLF view is one
pass, candidates make one listing call and read each remaining file once.
Feature integrity: a configuration without version sections loads as before
and imports no source module; nothing ships.

Please check in particular: the per-instance configuration rules and their
messages, the CRLF-to-LF offset mapping, the claim registry (duplicate,
outside and overlapping spans, both claimants named), adapter-major detection
order, `plan_edits` composition and the release-only guard, candidate
filtering, and the `model.py` extension (`PatternDeclaration`,
`AdapterSettings.patterns`) made outside the plan's file list.

### Implementation report for step 3 version-sources (round 1)

Step 3, "Version configuration, participation, claims and pattern sources",
adds the version domain of `.release.ini`, the `pattern` adapter, and the
detection layer that combines every adapter. Nothing ships yet:
`cli.SHIPPED_HANDLERS` stays empty, and only the configuration loader reaches
the new code, through the deferred validator.

Schema (`tools/release_workflow/schemas.py`, plan decision Q02):

- `VERSION_SCHEMA`: the `source:` family (`form`, managed `file`, `pattern`)
  and the `component:` family (required managed `root`);
  `SHIPPED_SCHEMAS = (TOOLING_SCHEMA, VERSION_SCHEMA)`.
- `_validate_version(sections)` returns at once when no section name starts
  with `source:` or `component:`; otherwise it imports
  `tools.release_workflow.sources.settings` (the only import of the package in
  `schemas.py`, `# noqa: PLC0415`) and calls `validate_settings(sections)`.

Settings (`sources/settings.py`):

- `validate_settings(sections, adapters=ADAPTERS)` walks the sections once.
  Built-in names are the registered adapters other than the reserved `anchor`
  and `pattern`; such a section accepts only `form`, within the adapter's
  `forms`. A reserved name fails. Any other name is a pattern source that
  needs `file`, `pattern` and `form`; the pattern compiles with
  `re.MULTILINE` and must have exactly one capture group. A component root
  must differ from the project root, lie under no name of
  `EXCLUDED_DIRECTORIES` (compared with `os.path.normcase`), and not repeat
  another component's directory. Errors are `SettingsError` (status 2)
  naming `[section] key=value`; the loader wraps them as `ConfigurationError`.
- `read_settings(configuration, adapters=ADAPTERS) -> VersionSettings`
  (project root, form overrides by adapter name, pattern declarations,
  components by id, read-only mappings in declaration order).
- The project root is `configuration.source.parent`, the directory of the
  `.release.ini` the loader read: the validator only receives the section
  mappings, whose `ConfigValue.source` is that file, so both functions use the
  same root.

Pattern sources (`sources/pattern.py`, design decision Q09):

- `lf_view(text)` reads each CRLF as LF in one pass, recording the view offset
  of each collapsed line feed; `LfView.original_offset` adds one per
  collapsed line feed before an offset (binary search), so an offset at a
  line end maps to the carriage return.
- `PatternAdapter` (`ADAPTER`): name `pattern`, no default form, every form
  allowed, no candidate names. `detect` returns nothing for a root other than
  the project root; for each declaration it requires the file (never
  created), decodes strict UTF-8, matches on the LF view, stops after a second
  match, requires a nonempty group 1 that is a version token (no `-SNAPSHOT`
  unless the form is `snapshot`), and maps the capture to a byte span through
  `to_byte_spans`. The field is `source:<name>`. Every failure names
  `[source:<name>]` and the file (status 2). `render` returns the raw text.

Detection (`sources/detection.py`):

- `participating_roots(settings)`: the project root, then each component root
  in declaration order; a missing or non-directory component root fails.
- `detect(inputs, view, *, adapters=ADAPTERS) -> Inventory`: adapter-major
  ("every adapter runs over every participating root in tuple order"). Claims
  are registered in a dictionary keyed by path and field; a second claim, a
  span past the end of the file, or overlapping spans of one file (sorted per
  file, consecutive comparison) fail, naming both claimants as
  `<adapter> <field> at root <root>`. One `FileCapture` per participating
  file comes from the same view, so nothing is read twice.
- `plan_edits(inventory, anchor, *, adapters=ADAPTERS)`: runs
  `check_release_only` for every source, then builds one `FileEdit` per file
  whose values differ from `form.expected(anchor)`, composed from the captured
  original with each adapter's `render`; an absent capture fails.
- `candidates(inputs, inventory, view, *, adapters=ADAPTERS)`: one
  `git.listing`; names whose file name is an adapter's manifest name are kept
  unless under an excluded directory, the artifact home, a participating root
  or the directory of a located manifest file (Maven modules later); each
  remaining file is read once and kept when `has_project_version` holds, as
  `VisibleRecord(path, "version", adapter, "not-participating undeclared")`.

Registry: `ADAPTERS = (anchor.ADAPTER, pattern.ADAPTER)`,
`SUPPORT_MODULES = frozenset({"model", "settings", "detection"})`.

One file outside the plan's Step 3 list changes: `sources/model.py` gains
`PatternDeclaration` (name, path, compiled expression, form) and the
`AdapterSettings.patterns` property. The pattern adapter reads its
declarations through the common `detect(root, view, settings)` signature, and
pyright strict rejects an adapter whose `detect` takes a narrower settings type
inside the `tuple[Adapter, ...]`. `version_support.RootSettings` gains
`patterns=()` accordingly. The validation plan records this.

Tests:

- `test_schemas_tdd.py`: the shipped tuple and family owners; with the
  `tools.release_workflow.sources*` entries removed from `sys.modules` through
  `monkeypatch.delitem`, loading no file or a `[tooling]`-only file imports no
  source module; a `[component:app]` section reaches
  `settings.validate_settings` once (replaced in place, never reloaded, so no
  duplicate classes leak into later tests).
- `test_version_settings_tdd.py`: through `load_configuration`, each accepted
  and rejected declaration of the plan, each asserting status 2, the section
  and key in the message and nothing written. Built-in cases use a test
  registry whose version validator is
  `partial(validate_settings, adapters=...)` with synthetic `python`
  (`core`), `npm` (all three) and `maven` (`snapshot`) adapters, until Steps
  5 to 7 register the real ones; reserved names, pattern keys and component
  roots use the shipped registry.
- `test_pattern_sources_tdd.py` and `_pbt.py`: the umbrella pattern on LF and
  CRLF; byte-order mark, accented and non-BMP text before the match on both
  endings; two pattern sources of one file composing from one original read
  once; zero, two and empty matches, a malformed value, a snapshot value in
  `core` form, a missing and a non-UTF-8 file; other roots. The property
  checks the view and offset map over one integer decoded into six lines with
  mixed endings and stray carriage returns (25 examples, the cheapest encoding
  under the 0.1 s CPU lifecycle budget).
- `test_version_detection_tdd.py`: duplicate path and field, overlapping
  fields, two pattern sources on the same bytes, a pattern on the anchor's
  token, a span outside its file, missing and file component roots,
  adapter-major order over three roots, one load per file with three claims
  and two captures, two disjoint fields composed in one edit (and only the
  anchor edited for an older target), the release-only refusal, an absent
  capture, and candidates with one listing call (excluded names, artifact
  home, participating root, component root, Maven-module directory, missing
  file, manifest without a version).
- `test_version_registry_tdd.py`: the order `("anchor", "pattern")` and the
  support modules.

Writer notes: `.reviews/a.version-sources.step3.journal.md` and
`.reviews/a.version-sources.step3.handoff.md`.

### Change summary for step 3 version-sources (round 1)

Staged paths (17), grouped in the root `a.commit` (four groups, checker
`ready: true`):

1. `feat(release): add declared pattern sources`:
   `tools/release_workflow/sources/model.py`,
   `tools/release_workflow/sources/pattern.py`,
   `tools/release_workflow/sources/__init__.py`,
   `tests/unit/tools/release_workflow/version_support.py`,
   `tests/unit/tools/release_workflow/test_pattern_sources/__init__.py`,
   `tests/unit/tools/release_workflow/test_pattern_sources/test_pattern_sources_tdd.py`,
   `tests/unit/tools/release_workflow/test_pattern_sources/test_pattern_sources_pbt.py`,
   `tests/unit/tools/release_workflow/test_version_registry/test_version_registry_tdd.py`.
2. `feat(release): validate version configuration`:
   `tools/release_workflow/sources/settings.py`,
   `tools/release_workflow/schemas.py`,
   `tests/unit/tools/release_workflow/test_version_settings/__init__.py`,
   `tests/unit/tools/release_workflow/test_version_settings/test_version_settings_tdd.py`,
   `tests/unit/tools/release_workflow/test_schemas/test_schemas_tdd.py`.
3. `feat(release): combine detectors and claims`:
   `tools/release_workflow/sources/detection.py`,
   `tests/unit/tools/release_workflow/test_version_detection/__init__.py`,
   `tests/unit/tools/release_workflow/test_version_detection/test_version_detection_tdd.py`.
4. `docs(version-sources): record step 3 validation`:
   `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md` (Step 3
   sections).

Group 1 declares the `settings` and `detection` support modules before they
exist; the registry check subtracts support modules from the listed ones, so
it holds at every group. Steps 1 and 2 are committed (`a7c0d7c` to `115105c`)
and are not part of this review.

### Writer response for step 3 version-sources (round 1)

Writer response:

This is the first round of the Step 3 code review; there is no earlier
reviewer feedback to answer.

Choices worth checking, all within the plan or recorded in the validation plan:

- Built-in form names come from the registered adapters, the plan's "forms
  read from the registered adapters' `forms`". Until Steps 5 to 7 register
  `python`, `npm` and `maven`, `[source:npm]` is therefore read as a pattern
  source and needs all three keys; the settings tests exercise the override
  rules with synthetic adapters carrying the design's forms.
- `read_settings` and the validator take the project root from the
  `.release.ini` location, so `participating_roots` takes the settings alone
  rather than the plan's `(project, settings)` pair.
- `detect`, `plan_edits` and `candidates` take a keyword `adapters`
  defaulting to `ADAPTERS`, and `candidates` also takes the phase's
  `FileView`, so tests inject synthetic adapters and count reads without any
  module-global patch.
- `plan_edits` runs the release-only guard for every source before building
  any edit, so a refusal leaves no partial plan.
- Candidate exclusion treats the directory of a located manifest file as
  participating (Maven reactor modules), but not the directory of a pattern
  source's file.
- A pattern capture must be a version token, without `-SNAPSHOT` unless the
  form is `snapshot`; a snapshot-form source may hold a release token.

### Reviewer focus for step 3 version-sources (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-3-round-1 -->

## Round 1 by reviewer - Step 3

- Recorded: 2026-11-09T11:31:54+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 3
- Outcome: answer

### Assessed index identity for step 3 version-sources (exchange 1) (round 1)

Baseline index tree: 6767623c8a6ed2f73a75f6c3e4e56a4ad3b3475e

Assessed index tree: 7eaec9757b3ed0a76f0417a7c51c7ccd8c310807

### Implementation check for step 3 version-sources (exchange 1) (round 1)

Result:

Yes. Step 3 has been fully implemented.

The schema and deferred validator implement the per-instance source and component rules. Pattern detection enforces one nonempty version capture and maps LF-view offsets back through CRLF and UTF-8 bytes. The claim registry rejects duplicate fields, out-of-file spans and overlaps; detection is adapter-major, and planning composes disjoint fields from one original after the release-only guard. Candidate filtering uses one Git listing and one cached read per remaining file.

The tests cover the planned failures, declaration order, read counts, BOM and multi-byte offsets, composition and candidate exclusions. The property test exercises mixed line endings and boundary offsets. The model extension is required by the common adapter settings protocol and implements this step's pattern declaration behavior. No architecture, performance, feature-integrity or static coverage gap was found. The tools coverage gate excludes tests and initializers; their new symbols are referenced by tests or their own package.

Validation plan effects:

Added and staged one independent assessment paragraph in the Step 3 rows of docs/v0.14.0/plan.v0.14.0.version-sources.validation.md. The existing Yes verdict remains correct. No other step, document-level completion status or umbrella row was changed. The evidence launcher proved the patch attributable before it was applied to the index.

### Pre-repair mandatory checks and coverage for step 3 version-sources (exchange 1) (round 1)

The request reports green focused tests, ghog day --whole-suite and ghog day --full=speed --whole-suite, including 100% measured tools coverage, with no exclusions or duration outliers. The bound whole-suite scope capture is present. I assessed coverage statically against the implementation and unit tests; no reviewer test execution or coverage walk was needed or run. The mechanical commit-plan checker ran independently and passed.

### Resolved validation set and sources for step 3 version-sources (exchange 1) (round 1)

The current resolver returns ghog day --full=speed --whole-suite, with sources [project], matching the request. No plan or request additions apply. This command remains requestor-side validation and was not rerun by the reviewer.

### Resolver drift and direction for step 3 version-sources (exchange 1) (round 1)

No validation-set drift: the current scope-aware resolver and the request have the same command, order and source.

### Repository state around validation for step 3 version-sources (exchange 1) (round 1)

Request and baseline index: 6767623c8a6ed2f73a75f6c3e4e56a4ad3b3475e. Assessed index: 7eaec9757b3ed0a76f0417a7c51c7ccd8c310807.

The umbrella comparison reports changed=false. Validation-state comparison reports acceptable=false because the validation plan and index changed; inspection and patch attribution show that both changes are confined to the permitted Step 3 review-metadata paragraph. No implementation, test, other tracked path or untracked validation side effect changed. No implementation repair was authorized or performed. The request's general repair prose is not a literal Human guidance block.

### Repair inventory for step 3 version-sources (exchange 1) (round 1)

Repairs made:

- docs/v0.14.0/plan.v0.14.0.version-sources.validation.md: polishing-only review metadata; added the independent Step 3 assessment. No substantive repair.

Paths staged:

- docs/v0.14.0/plan.v0.14.0.version-sources.validation.md
- `tests/unit/tools/release_workflow/test_pattern_sources/__init__.py`
- tests/unit/tools/release_workflow/test_pattern_sources/test_pattern_sources_pbt.py
- tests/unit/tools/release_workflow/test_pattern_sources/test_pattern_sources_tdd.py
- tests/unit/tools/release_workflow/test_schemas/test_schemas_tdd.py
- `tests/unit/tools/release_workflow/test_version_detection/__init__.py`
- tests/unit/tools/release_workflow/test_version_detection/test_version_detection_tdd.py
- tests/unit/tools/release_workflow/test_version_registry/test_version_registry_tdd.py
- `tests/unit/tools/release_workflow/test_version_settings/__init__.py`
- tests/unit/tools/release_workflow/test_version_settings/test_version_settings_tdd.py
- tests/unit/tools/release_workflow/version_support.py
- tools/release_workflow/schemas.py
- `tools/release_workflow/sources/__init__.py`
- tools/release_workflow/sources/detection.py
- tools/release_workflow/sources/model.py
- tools/release_workflow/sources/pattern.py
- tools/release_workflow/sources/settings.py

### Commit plan assessment for step 3 version-sources (exchange 1) (round 1)

Independent checker: state=valid, ready=true, no diagnostics, all 17 staged paths covered exactly once. The four groups are ordered as declared pattern sources, version configuration, detector composition and claims, then Step 3 validation. Their conventional subjects accurately describe the changes. The model extension belongs with the pattern adapter that requires it. The support-module declarations may precede those modules because the completeness check subtracts support names from discovered files. The reviewer metadata remains in the existing validation group, so a.commit requires no amendment.

### Findings and boundaries for step 3 version-sources (exchange 1) (round 1)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 3 version-sources (exchange 1) (round 1)

No rework is required. Present the advisory commit-ready recommendation at the existing human convergence gate. Commit authorization belongs to that gate.

### Decision rationale for step 3 version-sources (exchange 1) (round 1)

Recommend commit-ready. All six readiness results pass: exact identity, complete Step 3 implementation, sufficient writer validation and static coverage evidence, attributable staged scope, no unresolved findings and accurate commit grouping. Only review metadata changed in this round; no substantive repair was made. This recommendation does not authorize a commit.

### Final reviewer decision for step 3 version-sources (exchange 1) (round 1)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-3-round-1 -->

## Round 1 by human - Step 3 - human-confirmation

- Recorded: 2026-11-09T12:28:41+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 3
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-1 -->
