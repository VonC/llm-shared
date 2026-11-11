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

## Round 1 by requestor - Step 4

- Recorded: 2026-11-09T16:37:30+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Implementation step: 4
- Outcome: request

### Review identity for step 4 version-sources (round 1)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.version-sources.md
Implementation step: 4
Review round: 1

### Code review evidence for step 4 version-sources (round 1)

request_index_tree: 0c3336dad7469ce5bd722d24b40f3e9375be8c2c
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.version-sources.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: docs(version-sources): fix transcript Markdown
group 1 path: docs/v0.14.0/review.code.v0.14.0.version-sources.md
group 2: feat(release): add the recoverable version transition
group 2 path: tools/release_workflow/version_evidence.py
group 2 path: tools/release_workflow/version_transition.py
group 2 path: tests/unit/tools/release_workflow/version_support.py
group 2 path: tests/unit/tools/release_workflow/test_version_evidence/__init__.py
group 2 path: tests/unit/tools/release_workflow/test_version_evidence/test_version_evidence_tdd.py
group 2 path: tests/unit/tools/release_workflow/test_version_transition/__init__.py
group 2 path: tests/unit/tools/release_workflow/test_version_transition/test_version_transition_tdd.py
group 2 path: tests/unit/tools/release_workflow/test_version_transition/test_version_restoration_tdd.py
group 2 path: tests/unit/tools/release_workflow/test_version_transition/test_version_lifecycle_tdd.py
group 3: docs(version-sources): record step 4 validation
group 3 path: docs/v0.14.0/plan.v0.14.0.version-sources.validation.md
group 3 path: .vscode/settings.json
staged path: .vscode/settings.json
staged path: docs/v0.14.0/plan.v0.14.0.version-sources.validation.md
staged path: docs/v0.14.0/review.code.v0.14.0.version-sources.md
staged path: tests/unit/tools/release_workflow/test_version_evidence/__init__.py
staged path: tests/unit/tools/release_workflow/test_version_evidence/test_version_evidence_tdd.py
staged path: tests/unit/tools/release_workflow/test_version_transition/__init__.py
staged path: tests/unit/tools/release_workflow/test_version_transition/test_version_lifecycle_tdd.py
staged path: tests/unit/tools/release_workflow/test_version_transition/test_version_restoration_tdd.py
staged path: tests/unit/tools/release_workflow/test_version_transition/test_version_transition_tdd.py
staged path: tests/unit/tools/release_workflow/version_support.py
staged path: tools/release_workflow/version_evidence.py
staged path: tools/release_workflow/version_transition.py
```

### Validation scope for step 4 version-sources (round 1)

Validation scope: the whole suite.

### Requestor assessment for step 4 version-sources (round 1)

Writer assessment for Step 4 of the version-sources plan, round 1: the step is
fully implemented, and its implementation check records
`Yes. Step 4 has been fully implemented.` in the staged validation plan.

Evidence, all on the staged tree:

- Tests first: `ghog single` on the two new test folders failed at collection
  (four `ModuleNotFoundError`s, exit 4), then passed after the implementation
  together with the Step 2 and 3 version and schema tests (168 tests), once
  two test-code defects were fixed (unescaped evidence names in `match=`, a
  declared home without its ignore file).
- `ghog day --whole-suite`, the command printed by `pw scope day`, exit 0. A
  first run failed only at check.bat (pyright, ruff, radon on one test, and
  MD050 on four bare `__init__.py` paths in the committed step 3 answer). A
  static coverage review then added three tests, and the walk passed again.
- `ghog day --full=speed --whole-suite`, the review validation default: exit
  0, no failure, coverage 100%, no duration outlier, no exclusion (check and
  affected reused by groundhog's proof), in a measured quiet window (no other
  checkout's pytest, load below 50% on three samples). An earlier speed walk
  started at a higher load failed on five unrelated tests with lifecycle wall
  overruns at near-zero CPU; those tests pass in focus. No budget was raised
  and no exclusion is accepted in this step.
- Completion checks: `rg -n 'os\.replace|write_bytes|unlink'` on both modules
  finds only `remove_managed`'s `unlink(missing_ok=True)` on
  `target.revalidate()`; the restoration registry holds the anchor, pattern
  and two-claim sets for Steps 5 to 7 to extend.
- Markdown lint and spell check of the staged validation plan and transcript:
  no finding; one word (`YYYYMMDDTHHMMSS`) added at the user's choice.
- Every file stays below 650 lines; `version_transition.py` is 384,
  `version_evidence.py` 326.

Architecture: the transition reaches item 1's boundaries only through
`TransitionPorts`; every write is a managed replacement or a revalidated
managed target; a lifecycle call never acquires, releases or deletes what it
does not own. Performance: one view per phase, each file read once per phase,
the only sorts over a handful of changed files and evidence directories.
Feature integrity: no existing tool module changes; nothing ships until
Step 9.

Please check in particular: the order of the locked phases and the evidence
check before every success path, the restoration boundary (what counts as
replaced, write-back and fresh-view verification), the secondary-failure rule
(status 1 after the marker, status 3 kept), the empty-directory residue
classification, the lifecycle rules (verification before any read, own
evidence accepted, kept evidence and the restore handle), and the fixture
registry Steps 5 to 7 will extend.

### Implementation report for step 4 version-sources (round 1)

Step 4, "Recoverable version transition", adds the recovery evidence module and
the transition primitive behind `versions set` and item 5. Nothing ships yet:
no handler calls them until Step 9.

Evidence (`tools/release_workflow/version_evidence.py`):

- `EvidenceManifest` (version 1, owner, target, state, created local time with
  offset, files with root-relative path, SHA-256, existence and copy name).
  `encode` writes indented UTF-8 JSON; `decode` rejects duplicate keys
  (`object_pairs_hook`), unknown or missing fields, wrong types (a JSON
  boolean is required for existence), another version and an empty owner, all
  as `ValueError("unreadable evidence manifest: ...")`.
- `allocate(prepared, now, pid, *, attempts=99)`: builds
  `a.version-transition.<now %Y%m%dT%H%M%S%z>-<pid>`, authorizes it in the
  prepared home and calls `mkdir(exist_ok=False)` on the revalidated target,
  then revalidates. `FileExistsError` moves to `-2`, `-3`, and so on; any
  other error, or exhausting the attempts, raises `EvidenceError` (status 1).
  Item 1's `prepare_directory` is not used, and `managed_files` is unchanged.
- `write_evidence(directory, manifest, captures, *, replace, remove)`: copies
  (`original.<n>` for each present capture) through the replace port, then the
  manifest. On failure it removes what it wrote (copies, manifest, directory)
  and raises `EvidenceError`, naming any residue when that cleanup fails too.
- `EvidenceDirectory.mark(state, replace)` replaces the manifest through the
  replace port; `delete(remove)` removes the copies, the manifest, then the
  directory, raising `EvidenceError` that names the residue: the directory
  with its copies and manifest, the manifest alone, or the empty directory.
- `find_evidence(declaration)`: one `iterdir` of the artifact home (sorted by
  name), directories with the prefix only, one manifest read each. Kinds:
  `RESIDUE` (standalone `complete`, or an empty directory), `INTERRUPTED`
  (standalone `writing` or `restoration-incomplete`), `UNREADABLE`,
  `LIFECYCLE` (any other owner). `EvidenceEntry.delete` removes residue
  whatever part of it a failed cleanup left.
- `remove_managed(target)`: `rmdir` for a directory, `unlink(missing_ok=True)`
  otherwise, both on `target.revalidate()`.

Transition (`tools/release_workflow/version_transition.py`):

- `TransitionOutcome` with statuses 0, 0, 1, 3, 1; `TransitionResult`
  (outcome, changes, diagnostics, optional `RestoreHandle`, `status`);
  `TransitionError` (status carried); `LifecycleOwnership(lock,
  transaction)`.
- `TransitionPorts` (plan decision Q07): `replace` (`replace_bytes`),
  `remove` (`remove_managed`), `lock_factory` (`OperationLock`), `probe`
  (`process_state`), `clock` (local time with offset), `pid` (`os.getpid`),
  and `view` (`FileView`), the factory of each phase's fresh view.
- `plan_transition(inputs, target, view)`: detect and `plan_edits`, no side
  effect.
- `set_versions(inputs, target, *, lifecycle=None, ports=DEFAULT_PORTS)`,
  standalone: unlocked plan; `prepare_artifacts`; lock acquisition
  (`OperationLockError` becomes `TransitionError` status 1 with the owner's
  record fields); then `_transition` inside `except BaseException:` that
  releases the lock (suppressing a release error) and re-raises; finally the
  release, whose failure only adds a diagnostic.
- `_transition`: `_check_evidence` (residue removed with a warning; anything
  but this call's own lifecycle evidence stops with status 2 naming the
  directory, owner and state); locked plan in a fresh view; `unchanged` for no
  edits; `allocate` and `write_evidence` with one clock reading; `_apply`.
- `_apply`: edits ordered by (is anchor, path); `_write` opens one comparison
  view, requires each file's current bytes to equal its capture, replaces it,
  and records the read bytes; `_verify` re-detects in a fresh view and
  requires every source's expected value; then `mark(COMPLETE)`. Any
  `SourceError`, `ManagedWriteError`, `OSError` or `EvidenceError` before the
  marker goes to `_restore`. After it: lifecycle returns `applied` with a
  `RestoreHandle`; standalone deletes the evidence, a failure turning the
  result into `applied with cleanup failed` with the residue named.
- `_restore`: writes back every replaced file (last first, errors suppressed),
  checks each in a fresh view (an unreadable file counts as unrestored). All
  back: `restored`, standalone evidence deleted (failure adds a diagnostic
  naming it), lifecycle evidence kept. Otherwise `restoration incomplete`
  naming each path and `copy_path`, and the evidence marked
  `restoration-incomplete` (failure adds a diagnostic).
- `_secondary`: an applied outcome becomes `applied with cleanup failed` with
  "the new versions are applied; ..."; any other outcome keeps its status and
  gains the diagnostic.
- Lifecycle: the transaction must be nonempty and not `standalone` (status 2);
  `verify_held(inputs.artifacts)` runs before any read (failure: status 1);
  no unlocked plan, since the lock is held; evidence owned by the transaction.

Tests: `test_version_evidence_tdd.py` (written evidence, failed writes with and
without cleanup, marking, deletion order and residue names, listing kinds,
missing home, strict decoding, allocation suffixes, other allocation failure,
attempt limit); `test_version_transition_tdd.py` (default ports, plan failures
with whole-tree snapshots, held lock, residue removal, unfinished evidence
stopping an empty plan, unchanged, unwritable evidence, ordered run and
changes, one view per phase and completion before cleanup);
`test_version_restoration_tdd.py` (the registry at every write position,
concurrent change, failed verification, failed marker, undeletable restored
evidence, incomplete restoration with no, release, marker or unreadable
secondary failure, `writing` evidence on a same-target rerun, three cleanup
faults then the next run, lock release failure after completion);
`test_version_lifecycle_tdd.py` (kept lock and handle, unbound or reserved
calls with no view opened, own and foreign evidence, two calls with disjoint
evidence). `version_support.py` adds the restoration registry, `Faults`,
`ViewLog`, `declare_evidence`, `source_bytes`, `version_project` and the fixed
clock, process id and names.

The commit plan also carries one documentation repair: the step 3 round 1
answer in the review transcript listed four `__init__.py` paths without code
spans, which check.bat's Markdown catalog reports as MD050 (the markdownlint
run at the step 3 gate did not).

Writer notes: `.reviews/a.version-sources.step4.journal.md` and
`.reviews/a.version-sources.step4.handoff.md`.

### Change summary for step 4 version-sources (round 1)

Staged paths (12), grouped in the root `a.commit` (three groups, checker
`ready: true`):

1. `docs(version-sources): fix transcript Markdown`:
   `docs/v0.14.0/review.code.v0.14.0.version-sources.md` (four `__init__.py`
   paths of the step 3 answer wrapped in code spans).
2. `feat(release): add the recoverable version transition`:
   `tools/release_workflow/version_evidence.py`,
   `tools/release_workflow/version_transition.py`,
   `tests/unit/tools/release_workflow/version_support.py`,
   `tests/unit/tools/release_workflow/test_version_evidence/__init__.py`,
   `tests/unit/tools/release_workflow/test_version_evidence/test_version_evidence_tdd.py`,
   `tests/unit/tools/release_workflow/test_version_transition/__init__.py`,
   `tests/unit/tools/release_workflow/test_version_transition/test_version_transition_tdd.py`,
   `tests/unit/tools/release_workflow/test_version_transition/test_version_restoration_tdd.py`,
   `tests/unit/tools/release_workflow/test_version_transition/test_version_lifecycle_tdd.py`.
3. `docs(version-sources): record step 4 validation`:
   `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md` (Step 4
   sections), `.vscode/settings.json` (`YYYYMMDDTHHMMSS` added to
   `cSpell.words` at the user's choice).

The evidence and transition modules share one group with their tests because
the shared test support imports the transition ports. Steps 1 to 3 are
committed (`a7c0d7c` to `83a31eb`) and are not part of this review.

### Writer response for step 4 version-sources (round 1)

Writer response:

This is the first round of the Step 4 code review; there is no earlier
reviewer feedback to answer.

Choices worth checking, all recorded in the validation plan or the step notes:

- `TransitionPorts` carries a seventh port, `view`, the factory of each
  phase's fresh `FileView`: tests count views (one per phase) and prove that a
  rejected lifecycle call opens none, without patching a module global.
- `allocate` takes `(prepared, now, pid)`: one clock reading names the
  directory and fills `created`, and the project comes from the prepared home.
- An empty evidence directory is classified as completed residue: a failed
  directory removal after the `complete` marker leaves exactly that, and the
  next `set` must remove it rather than stop on unreadable evidence. A
  directory holding copies but no manifest stays unreadable and stops `set`.
- `remove_managed` uses `unlink(missing_ok=True)`, so removing residue after a
  failed manifest deletion (copies already gone) is idempotent.
- A lifecycle call skips the unlocked plan (its lock is held), and rejects a
  `standalone` or empty transaction identity with status 2.
- Restoration writes back the bytes read in the comparison just before each
  replacement, suppresses a write-back failure and lets the fresh-view check
  decide; a lifecycle restoration (during the call or through the handle)
  keeps the transaction's evidence.
- A lock-release failure after `unchanged` or `restored` keeps that outcome and
  status and only adds a diagnostic; after `applied` it becomes `applied with
  cleanup failed`.

### Reviewer focus for step 4 version-sources (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-4-round-1 -->

## Round 1 by reviewer - Step 4

- Recorded: 2026-11-09T16:45:29+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 4
- Outcome: answer

### Assessed index identity for step 4 version-sources (exchange 1) (round 1)

Baseline index tree: 0c3336dad7469ce5bd722d24b40f3e9375be8c2c

Assessed index tree: 2ca227630aecb72eb9337a15cbeebc6acaf1f608

### Implementation check for step 4 version-sources (exchange 1) (round 1)

Result:

No. Step 4 has NOT been fully implemented.

The planned transition, durable completion boundary, restoration registry and lifecycle reuse are implemented, but three recovery and status defects remain. The exact Step 4 validation section now records the No verdict and a concrete missing-work list. Static review found no additional layering or performance issue; every changed production file is below the 650-line ceiling.

Readiness floor: identity passes; completeness fails; validation and coverage assessment identifies missing behavioral tests; staged attribution passes for the permitted validation metadata; unresolved findings fail; independent a.commit assessment passes.

Validation plan effects:

Updated only Step 4 in docs/v0.14.0/plan.v0.14.0.version-sources.validation.md: the No verdict, missing-work list, and matching architecture, unit-test and integrity assessments. The evidence launcher proved the patch attributable before it was staged. The umbrella is unchanged.

### Pre-repair mandatory checks and coverage for step 4 version-sources (exchange 1) (round 1)

Pre-repair validation blob: 94c359c1fa378f7fc40357c023e41e23754769e1. The writer's original Step 4 verdict was Yes. The original request, staged implementation and tests were reviewed independently; the transcript was not used as working context.

### Resolved validation set and sources for step 4 version-sources (exchange 1) (round 1)

Request and current resolver agree: ghog day --full=speed --whole-suite, source project. The bound round scope is the whole suite, fingerprint 686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6.

The writer reports 168 focused tests green, a green scoped day walk and a green speed/coverage walk on the staged implementation. Reviewer assessment was static; no ghog day, ghog full, coverage run, check or affected command was repeated. The coverage gate measures tools and excludes tests and initializers. Changed test-support definitions are exercised, but the three reported behaviors lack regression tests.

### Resolver drift and direction for step 4 version-sources (exchange 1) (round 1)

No drift. Both sets contain the project command ghog day --full=speed --whole-suite.

### Repository state around validation for step 4 version-sources (exchange 1) (round 1)

The live request-time tree matched 0c3336dad7469ce5bd722d24b40f3e9375be8c2c. After the attributable Step 4 metadata update, the assessed tree is 2ca227630aecb72eb9337a15cbeebc6acaf1f608.

The validation-state comparator reports acceptable=false because the validation plan and index changed. Independent classification confines both differences to the permitted, attributed Step 4 validation update. Every other tracked digest is identical; no untracked or ignored validation artifacts appeared. Umbrella digest comparison passes unchanged at 5abf0cb72800e9d07acba786dd90502fcb8879ff41cbcce55b961a95352aaa4c.

### Repair inventory for step 4 version-sources (exchange 1) (round 1)

Repairs made:

- Updated and staged only the exact Step 4 validation metadata. No implementation or test repair was authorized by a literal Human guidance block.

Paths staged:

- docs/v0.14.0/plan.v0.14.0.version-sources.validation.md: attributable reviewer metadata only. All other 11 staged paths retain the requestor's bytes.

### Commit plan assessment for step 4 version-sources (exchange 1) (round 1)

The independent commit-plan checker returned state=valid, ready=true, no diagnostics, and exactly 12 paths covered once. Its ordered groups are docs(version-sources): fix transcript Markdown; feat(release): add the recoverable version transition; docs(version-sources): record step 4 validation.

The order puts the pre-existing transcript lint correction before shared support imports the new modules, followed by validation metadata. Production code and tests form one coherent feature group. The editor dictionary addition is explicitly reported as the user's choice and grouped with metadata. Membership, scope and conventional subjects remain accurate; a.commit was not changed. This mechanical and semantic pass does not override the implementation findings.

### Findings and boundaries for step 4 version-sources (exchange 1) (round 1)

Unresolved findings:

- [P1] Constrain decoded copy destinations before residue cleanup (tools/release_workflow/version_evidence.py:201-205). _file accepts arbitrary copy strings, and _delete joins them to the evidence directory before authorizing them against the whole project. In a complete standalone manifest under .reviews/a.version-transition.example, copy="../../version.txt" resolves to the project's anchor and is deleted before the authoritative plan runs. Absolute in-project names are also accepted. Validate all copy metadata before any removal, require safe direct copy names and physical containment in the evidence directory, and classify invalid manifests as unreadable. Add set-level tests asserting status 2 and byte-identical sources and evidence for traversal and absolute destinations.
- [P2] Fail an unchanged run when releasing its lock fails (tools/release_workflow/version_transition.py:258-263). A same-target transition returns UNCHANGED, then a release error goes through _secondary's non-applied branch and retains status 0, although the operation lock remains. Raise or return status 1 with the lock-record diagnostic while preserving unchanged sources, and add a same-target test with the existing failing-release fixture.
- [P2] Classify a directory that cannot be enumerated as unreadable evidence (tools/release_workflow/version_evidence.py:318-323). When reading the manifest raises PermissionError, the exception handler calls path.iterdir() outside any error guard. If directory enumeration is also denied, that second error escapes _check_evidence as a raw OSError, without the required status-2 TransitionError naming the evidence directory. Conservatively retain an unreadable entry on enumeration failure; add an injected double-failure test asserting status 2, named evidence, unchanged sources and released standalone lock.

Boundary-crossing work: None.

### Writer instructions for step 4 version-sources (exchange 1) (round 1)

Fix all three findings within Step 4 and add the regression cases listed in its Missing work section. Reassess the validation plan, run the writer-owned resolved validation set green, refresh staged evidence and a.commit if necessary, and publish the next round through the existing requestor workflow.

### Decision rationale for step 4 version-sources (exchange 1) (round 1)

Changes requested. The implementation and broad writer validation establish the planned happy path and many injected faults, but do not make source-deleting residue cleanup or success after a failed lock release acceptable. The unreadable-directory fallback also violates the explicit evidence-stop contract. No commit-ready recommendation is made.

### Final reviewer decision for step 4 version-sources (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-4-round-1 -->

## Round 2 by requestor - Step 4

- Recorded: 2026-11-09T17:22:57+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 4
- Outcome: request

### Review identity for step 4 version-sources (round 2)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.version-sources.md
Implementation step: 4
Review round: 2

### Code review evidence for step 4 version-sources (round 2)

request_index_tree: 65f25de42b0d0df951209a95a076646cbe005b07
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.version-sources.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: docs(version-sources): fix transcript Markdown
group 1 path: docs/v0.14.0/review.code.v0.14.0.version-sources.md
group 2: feat(release): add the recoverable version transition
group 2 path: tools/release_workflow/version_evidence.py
group 2 path: tools/release_workflow/version_transition.py
group 2 path: tests/unit/tools/release_workflow/version_support.py
group 2 path: tests/unit/tools/release_workflow/test_version_evidence/__init__.py
group 2 path: tests/unit/tools/release_workflow/test_version_evidence/test_version_evidence_tdd.py
group 2 path: tests/unit/tools/release_workflow/test_version_transition/__init__.py
group 2 path: tests/unit/tools/release_workflow/test_version_transition/test_version_transition_tdd.py
group 2 path: tests/unit/tools/release_workflow/test_version_transition/test_version_restoration_tdd.py
group 2 path: tests/unit/tools/release_workflow/test_version_transition/test_version_lifecycle_tdd.py
group 3: docs(version-sources): record step 4 validation
group 3 path: docs/v0.14.0/plan.v0.14.0.version-sources.validation.md
group 3 path: .vscode/settings.json
staged path: .vscode/settings.json
staged path: docs/v0.14.0/plan.v0.14.0.version-sources.validation.md
staged path: docs/v0.14.0/review.code.v0.14.0.version-sources.md
staged path: tests/unit/tools/release_workflow/test_version_evidence/__init__.py
staged path: tests/unit/tools/release_workflow/test_version_evidence/test_version_evidence_tdd.py
staged path: tests/unit/tools/release_workflow/test_version_transition/__init__.py
staged path: tests/unit/tools/release_workflow/test_version_transition/test_version_lifecycle_tdd.py
staged path: tests/unit/tools/release_workflow/test_version_transition/test_version_restoration_tdd.py
staged path: tests/unit/tools/release_workflow/test_version_transition/test_version_transition_tdd.py
staged path: tests/unit/tools/release_workflow/version_support.py
staged path: tools/release_workflow/version_evidence.py
staged path: tools/release_workflow/version_transition.py
```

### Validation scope for step 4 version-sources (round 2)

Validation scope: the whole suite.

### Requestor assessment for step 4 version-sources (round 2)

Writer assessment for Step 4 of the version-sources plan, round 2: the step is
fully implemented. The three round 1 findings are repaired with regression
tests (see the writer response), and the staged validation plan records
`Yes. Step 4 has been fully implemented.` again, with the reviewer's Missing
work section removed because each item is done.

Evidence, all on the staged tree:

- `ghog single` on `test_version_evidence` and `test_version_transition` with
  the repairs and the new regression tests: exit 0.
- `ghog day --full=speed --whole-suite`, the review validation default: exit
  0, no failure, coverage 100%, no duration outlier, no exclusion, nothing
  reused (check, affected and full all ran). At the user's request it ran
  without waiting for a quiet window. A first run failed only at check.bat on
  MD032 in the rewritten validation text, which was fixed and staged.
- The commit plan is unchanged (three groups, 12 paths, checker ready). The
  transcript's index copy holds only the MD050 fix of group 1; this exchange's
  rounds stay unstaged for the residual commit.
- Every file stays below 650 lines; `version_evidence.py` is 357,
  `version_transition.py` 390.

Please check in particular: `_copy` and `_inside` (no recorded or resolved
path can leave the evidence directory, and an unsafe manifest is unreadable
before anything is removed), the status 1 `TransitionError` for a failed
release after `unchanged`, and `_empty` keeping an unlistable directory
unreadable.

### Implementation report for step 4 version-sources (round 2)

Step 4, "Recoverable version transition", adds the recovery evidence module and
the transition primitive behind `versions set` and item 5. Nothing ships yet:
no handler calls them until Step 9.

Evidence (`tools/release_workflow/version_evidence.py`):

- `EvidenceManifest` (version 1, owner, target, state, created local time with
  offset, files with root-relative path, SHA-256, existence and copy name).
  `encode` writes indented UTF-8 JSON; `decode` rejects duplicate keys
  (`object_pairs_hook`), unknown or missing fields, wrong types (a JSON
  boolean is required for existence), another version, an empty owner and,
  since round 1, any copy name other than `original.<n>` (`_copy`), all as
  `ValueError("unreadable evidence manifest: ...")`.
- `allocate(prepared, now, pid, *, attempts=99)`: builds
  `a.version-transition.<now %Y%m%dT%H%M%S%z>-<pid>`, authorizes it in the
  prepared home and calls `mkdir(exist_ok=False)` on the revalidated target,
  then revalidates. `FileExistsError` moves to `-2`, `-3`, and so on; any
  other error, or exhausting the attempts, raises `EvidenceError` (status 1).
  Item 1's `prepare_directory` is not used, and `managed_files` is unchanged.
- `write_evidence(directory, manifest, captures, *, replace, remove)`: copies
  (`original.<n>` for each present capture) through the replace port, then the
  manifest. On failure it removes what it wrote (copies, manifest, directory)
  and raises `EvidenceError`, naming any residue when that cleanup fails too.
- `EvidenceDirectory.mark(state, replace)` replaces the manifest through the
  replace port; `delete(remove)` removes the copies, the manifest, then the
  directory, raising `EvidenceError` that names the residue: the directory
  with its copies and manifest, the manifest alone, or the empty directory.
  Since round 1, each copy and the manifest is authorized through `_inside`,
  which requires the resolved path's parent to be the evidence directory.
- `find_evidence(declaration)`: one `iterdir` of the artifact home (sorted by
  name), directories with the prefix only, one manifest read each. Kinds:
  `RESIDUE` (standalone `complete`, or a provably empty directory),
  `INTERRUPTED` (standalone `writing` or `restoration-incomplete`),
  `UNREADABLE` (including, since round 1, a directory `_empty` cannot list),
  `LIFECYCLE` (any other owner). `EvidenceEntry.delete` removes residue
  whatever part of it a failed cleanup left.
- `remove_managed(target)`: `rmdir` for a directory, `unlink(missing_ok=True)`
  otherwise, both on `target.revalidate()`.

Transition (`tools/release_workflow/version_transition.py`):

- `TransitionOutcome` with statuses 0, 0, 1, 3, 1; `TransitionResult`
  (outcome, changes, diagnostics, optional `RestoreHandle`, `status`);
  `TransitionError` (status carried); `LifecycleOwnership(lock,
  transaction)`.
- `TransitionPorts` (plan decision Q07): `replace` (`replace_bytes`),
  `remove` (`remove_managed`), `lock_factory` (`OperationLock`), `probe`
  (`process_state`), `clock` (local time with offset), `pid` (`os.getpid`),
  and `view` (`FileView`), the factory of each phase's fresh view.
- `plan_transition(inputs, target, view)`: detect and `plan_edits`, no side
  effect.
- `set_versions(inputs, target, *, lifecycle=None, ports=DEFAULT_PORTS)`,
  standalone: unlocked plan; `prepare_artifacts`; lock acquisition
  (`OperationLockError` becomes `TransitionError` status 1 with the owner's
  record fields); then `_transition` inside `except BaseException:` that
  releases the lock (suppressing a release error) and re-raises; finally the
  release, whose failure only adds a diagnostic, except after `unchanged`,
  where it raises `TransitionError` with status 1 (since round 1).
- `_transition`: `_check_evidence` (residue removed with a warning; anything
  but this call's own lifecycle evidence stops with status 2 naming the
  directory, owner and state); locked plan in a fresh view; `unchanged` for no
  edits; `allocate` and `write_evidence` with one clock reading; `_apply`.
- `_apply`: edits ordered by (is anchor, path); `_write` opens one comparison
  view, requires each file's current bytes to equal its capture, replaces it,
  and records the read bytes; `_verify` re-detects in a fresh view and
  requires every source's expected value; then `mark(COMPLETE)`. Any
  `SourceError`, `ManagedWriteError`, `OSError` or `EvidenceError` before the
  marker goes to `_restore`. After it: lifecycle returns `applied` with a
  `RestoreHandle`; standalone deletes the evidence, a failure turning the
  result into `applied with cleanup failed` with the residue named.
- `_restore`: writes back every replaced file (last first, errors suppressed),
  checks each in a fresh view (an unreadable file counts as unrestored). All
  back: `restored`, standalone evidence deleted (failure adds a diagnostic
  naming it), lifecycle evidence kept. Otherwise `restoration incomplete`
  naming each path and `copy_path`, and the evidence marked
  `restoration-incomplete` (failure adds a diagnostic).
- `_secondary`: an applied outcome becomes `applied with cleanup failed` with
  "the new versions are applied; ..."; any other outcome keeps its status and
  gains the diagnostic.
- Lifecycle: the transaction must be nonempty and not `standalone` (status 2);
  `verify_held(inputs.artifacts)` runs before any read (failure: status 1);
  no unlocked plan, since the lock is held; evidence owned by the transaction.

Tests: `test_version_evidence_tdd.py` (written evidence, failed writes with and
without cleanup, marking, deletion order and residue names, deletion refusing
a copy outside its directory, listing kinds, missing home, strict decoding
with unsafe copy names, allocation suffixes, other allocation failure, attempt
limit); `test_version_transition_tdd.py` (default ports, plan failures with
whole-tree snapshots, held lock, residue removal, residue with a traversal or
absolute copy name, evidence that can be neither read nor listed, unfinished
evidence stopping an empty plan, unchanged, unwritable evidence, ordered run
and changes, one view per phase and completion before cleanup);
`test_version_restoration_tdd.py` (the registry at every write position,
concurrent change, failed verification, failed marker, undeletable restored
evidence, incomplete restoration with no, release, marker or unreadable
secondary failure, `writing` evidence on a same-target rerun, three cleanup
faults then the next run, lock release failure after an `unchanged` run and
after completion);
`test_version_lifecycle_tdd.py` (kept lock and handle, unbound or reserved
calls with no view opened, own and foreign evidence, two calls with disjoint
evidence). `version_support.py` adds the restoration registry, `Faults`,
`ViewLog`, `declare_evidence`, `source_bytes`, `version_project` and the fixed
clock, process id and names.

The commit plan also carries one documentation repair: the step 3 round 1
answer in the review transcript listed four `__init__.py` paths without code
spans, which check.bat's Markdown catalog reports as MD050 (the markdownlint
run at the step 3 gate did not).

Writer notes: `.reviews/a.version-sources.step4.journal.md` and
`.reviews/a.version-sources.step4.handoff.md`.

### Change summary for step 4 version-sources (round 2)

Staged paths (12), grouped in the root `a.commit` (three groups, checker
`ready: true`):

1. `docs(version-sources): fix transcript Markdown`:
   `docs/v0.14.0/review.code.v0.14.0.version-sources.md` (four `__init__.py`
   paths of the step 3 answer wrapped in code spans).
2. `feat(release): add the recoverable version transition`:
   `tools/release_workflow/version_evidence.py`,
   `tools/release_workflow/version_transition.py`,
   `tests/unit/tools/release_workflow/version_support.py`,
   `tests/unit/tools/release_workflow/test_version_evidence/__init__.py`,
   `tests/unit/tools/release_workflow/test_version_evidence/test_version_evidence_tdd.py`,
   `tests/unit/tools/release_workflow/test_version_transition/__init__.py`,
   `tests/unit/tools/release_workflow/test_version_transition/test_version_transition_tdd.py`,
   `tests/unit/tools/release_workflow/test_version_transition/test_version_restoration_tdd.py`,
   `tests/unit/tools/release_workflow/test_version_transition/test_version_lifecycle_tdd.py`.
3. `docs(version-sources): record step 4 validation`:
   `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md` (Step 4
   sections), `.vscode/settings.json` (`YYYYMMDDTHHMMSS` added to
   `cSpell.words` at the user's choice).

The evidence and transition modules share one group with their tests because
the shared test support imports the transition ports. Steps 1 to 3 are
committed (`a7c0d7c` to `83a31eb`) and are not part of this review.

### Writer response for step 4 version-sources (round 2)

Writer response:

Round 1 requested changes with three findings. The writer accepts all three,
with no disagreement, and repaired them with regression tests.

- [P1] Unsafe manifest copy names. `_copy` now accepts a copy name only when
  it fully matches `original\.[1-9][0-9]*`, so a traversal (`../../version.txt`),
  absolute (`C:/project/version.txt`), nested (`sub/original.1`), reserved
  (`manifest.json`) or `original.0` name makes the manifest unreadable, and
  `set` stops with status 2 before removing anything. As a second guard,
  removal now authorizes each copy and the manifest through `_inside`, which
  requires the resolved path to sit directly in the evidence directory; a
  destination outside it raises `EvidenceError` before anything is removed.
  Tests: five unsafe names in `test_manifest_decoding_is_strict`;
  `test_deletion_never_leaves_the_evidence_directory` (a constructed manifest
  with `../version.txt`: refused, outside file and manifest kept);
  `test_residue_with_an_unsafe_copy_name_stops_and_deletes_nothing` (traversal
  and absolute names through `set`: status 2, whole-tree snapshot unchanged).
- [P2] `unchanged` after a failed lock release. `set_versions` now raises
  `TransitionError` with status 1 ("no source changed; releasing the operation
  lock failed and its record remains ...") when the release fails after an
  empty authoritative plan; `restored` and `restoration incomplete` keep their
  statuses 1 and 3. Test:
  `test_lock_release_failure_after_an_unchanged_run_fails_with_status_1`
  (same-target run with the failing-release fixture: status 1, lock record
  named, sources unchanged, no evidence).
- [P2] Unguarded listing after an unreadable manifest. `_entry` now asks
  `_empty`, which treats a directory it cannot list as not empty, so the entry
  is `unreadable` and `set` stops with the named status 2 diagnostic. Test:
  `test_evidence_that_cannot_be_read_or_listed_stops_the_transition` (manifest
  read and directory listing both denied: status 2, directory named, sources
  unchanged, lock released).

The reviewer's validation-plan metadata (No verdict and Missing work) is
superseded by the writer's renewed check: the Step 4 analysis is back to
`Yes. Step 4 has been fully implemented.`, the Missing work section is removed
because each item is done, and the architecture, coverage and integrity
sections record the round 1 findings as repaired.

### Reviewer focus for step 4 version-sources (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-4-round-2 -->

## Round 2 by reviewer - Step 4

- Recorded: 2026-11-09T17:29:30+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 4
- Outcome: answer

### Assessed index identity for step 4 version-sources (exchange 1) (round 2)

Baseline index tree: 65f25de42b0d0df951209a95a076646cbe005b07

Assessed index tree: bb76d4cd846fe86baa40b7d91f087d6e46da6a7e

### Implementation check for step 4 version-sources (exchange 1) (round 2)

Result:

Yes. Step 4 has been fully implemented.

The evidence and transition services satisfy the exact Step 4 plan: exclusive recovery directories, evidence before writes, a fresh locked plan, ordered replacement with the anchor last, verification and durable completion, restoration and status 3 evidence, and lifecycle lock/restore-handle reuse. No remaining layering, performance, line-budget or static unit coverage gap was found.

All three carried findings are resolved: strict copy-name decoding plus resolved-directory containment prevents cleanup from escaping its evidence directory; a failed lock release after unchanged raises status 1; failed manifest reading and directory enumeration produce the named unreadable-evidence status 2 stop. Regression tests check preserved source bytes, the unsafe manifest's unchanged tree, and lock release on the unreadable-directory path.

Readiness floor: exact identity passes; implementation completeness passes; requestor validation and static coverage assessment pass; staged attribution passes; no unresolved findings remain; independent commit-plan assessment passes.

Validation plan effects:

Added one independent reviewer confirmation paragraph only in the exact Step 4 analysis section of `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md`. The exact Yes verdict remains. No other step or umbrella row changed. Markdown lint reports zero issues.

### Pre-repair mandatory checks and coverage for step 4 version-sources (exchange 1) (round 2)

Before reviewer metadata changes, the request-time and live index trees matched `65f25de42b0d0df951209a95a076646cbe005b07`. The validation plan's pre-repair blob is `8bb44ba5ff88d3e5dedb52e545ff64f2c3ed5630`. No reviewer implementation or test repair was authorized or made. The request reports a fresh green whole-suite speed walk, nothing reused, 100% coverage, no outlier and no exclusion. The reviewer checked the implementation and regressions statically and did not rerun groundhog or measure coverage. The gate measures `tools`, omitting tests and initializers; the new support symbols outside it are referenced.

### Resolved validation set and sources for step 4 version-sources (exchange 1) (round 2)

The published request and current resolver both select `ghog day --full=speed --whole-suite`, source `project`. This is requestor-owned validation. The core-bound scope is whole-suite with fingerprint `686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6`.

### Resolver drift and direction for step 4 version-sources (exchange 1) (round 2)

None. Command, scope and source agree with the current resolver.

### Repository state around validation for step 4 version-sources (exchange 1) (round 2)

Baseline tree: `65f25de42b0d0df951209a95a076646cbe005b07`. Assessed tree: `bb76d4cd846fe86baa40b7d91f087d6e46da6a7e`.

The validation-state comparator reports `acceptable=false` solely for the validation plan and index. Independent classification confines these changes to the attributed Step 4 reviewer metadata paragraph. All other tracked digests match, including the pre-existing unstaged transcript content. No untracked or ignored validation artifacts appeared. Umbrella digest is unchanged at `5abf0cb72800e9d07acba786dd90502fcb8879ff41cbcce55b961a95352aaa4c`. Attribution returned true before staging the exact validation path.

### Repair inventory for step 4 version-sources (exchange 1) (round 2)

Repairs made:

- Polishing-only review metadata: `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md`, independent Step 4 confirmation. No substantive repair.

Paths staged:

- `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md`

### Commit plan assessment for step 4 version-sources (exchange 1) (round 2)

The independent checker reports `state=valid`, `ready=true`, no diagnostics, and all 12 staged paths covered exactly once. `a.commit` remains accurate and unchanged.

1. `docs(version-sources): fix transcript Markdown` contains only the staged code-span correction.
2. `feat(release): add the recoverable version transition` contains both services and their dependent tests/support.
3. `docs(version-sources): record step 4 validation` contains validation metadata and the user-selected editor dictionary word.

Order, subjects and dependencies remain appropriate after the permitted metadata update. The existing unstaged exchange transcript remains unstaged.

### Findings and boundaries for step 4 version-sources (exchange 1) (round 2)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 4 version-sources (exchange 1) (round 2)

No further Step 4 repair is requested. This advisory recommendation leaves the convergence choice and any commit to the human/requestor workflow.

### Decision rationale for step 4 version-sources (exchange 1) (round 2)

Recommend `commit-ready`. All three previous findings are resolved with behavioral regression tests, all six readiness results pass, and this round made only attributable review metadata changes. No literal `Human guidance:` block was supplied. This recommendation does not authorize a commit.

### Final reviewer decision for step 4 version-sources (exchange 1) (round 2)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-4-round-2 -->

## Round 2 by human - Step 4 - human-confirmation

- Recorded: 2026-11-09T17:34:23+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 4
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->

## Round 1 by requestor - Step 5

- Recorded: 2026-11-10T08:56:47+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Implementation step: 5
- Outcome: request

### Review identity for step 5 version-sources (round 1)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.version-sources.md
Implementation step: 5
Review round: 1

### Code review evidence for step 5 version-sources (round 1)

request_index_tree: 536e54b05b5dd4daa7fa7ad2c39595d52beb0c6e
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)
- `rg -n 'subprocess' tools/release_workflow/sources` (sources: plan)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "none", "requirement": "docs/v0.14.0/feature-request.v0.14.0.version-sources.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(release): add the python and uv version adapter
group 1 path: tools/release_workflow/sources/toml_scan.py
group 1 path: tools/release_workflow/sources/python.py
group 1 path: tools/release_workflow/sources/__init__.py
group 1 path: tools/release_workflow/sources/model.py
group 1 path: tools/release_workflow/sources/settings.py
group 1 path: tests/unit/tools/release_workflow/version_support.py
group 1 path: tests/unit/tools/release_workflow/lock_evidence_recorder.py
group 1 path: tests/unit/tools/release_workflow/test_version_formats/__init__.py
group 1 path: tests/unit/tools/release_workflow/test_version_formats/test_toml_scan_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_version_formats/test_version_formats_pbt.py
group 1 path: tests/unit/tools/release_workflow/test_python_sources/__init__.py
group 1 path: tests/unit/tools/release_workflow/test_python_sources/test_python_sources_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_python_sources/test_python_links_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_version_lock_evidence/__init__.py
group 1 path: tests/unit/tools/release_workflow/test_version_lock_evidence/lock_evidence.v1.json
group 1 path: tests/unit/tools/release_workflow/test_version_lock_evidence/test_version_lock_evidence_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_version_registry/test_version_registry_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_version_transition/test_version_restoration_tdd.py
group 2: docs(version-sources): record step 5 validation
group 2 path: docs/v0.14.0/plan.v0.14.0.version-sources.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.version-sources.validation.md
staged path: tests/unit/tools/release_workflow/lock_evidence_recorder.py
staged path: tests/unit/tools/release_workflow/test_python_sources/__init__.py
staged path: tests/unit/tools/release_workflow/test_python_sources/test_python_links_tdd.py
staged path: tests/unit/tools/release_workflow/test_python_sources/test_python_sources_tdd.py
staged path: tests/unit/tools/release_workflow/test_version_formats/__init__.py
staged path: tests/unit/tools/release_workflow/test_version_formats/test_toml_scan_tdd.py
staged path: tests/unit/tools/release_workflow/test_version_formats/test_version_formats_pbt.py
staged path: tests/unit/tools/release_workflow/test_version_lock_evidence/__init__.py
staged path: tests/unit/tools/release_workflow/test_version_lock_evidence/lock_evidence.v1.json
staged path: tests/unit/tools/release_workflow/test_version_lock_evidence/test_version_lock_evidence_tdd.py
staged path: tests/unit/tools/release_workflow/test_version_registry/test_version_registry_tdd.py
staged path: tests/unit/tools/release_workflow/test_version_transition/test_version_restoration_tdd.py
staged path: tests/unit/tools/release_workflow/version_support.py
staged path: tools/release_workflow/sources/__init__.py
staged path: tools/release_workflow/sources/model.py
staged path: tools/release_workflow/sources/python.py
staged path: tools/release_workflow/sources/settings.py
staged path: tools/release_workflow/sources/toml_scan.py
```

### Validation scope for step 5 version-sources (round 1)

Validation scope: the whole suite.

### Requestor assessment for step 5 version-sources (round 1)

Writer assessment for Step 5 of the version-sources plan, round 1: the step is
fully implemented, and its implementation check records
`Yes. Step 5 has been fully implemented.` in the staged validation plan.

Evidence, all on the staged tree:

- Tests first: `ghog single` on the new and registry leaves failed at
  collection (six errors, `ImportError: cannot import name 'python'`, exit
  4). After the implementation only the two scanner properties exceeded the
  0.1 s CPU lifecycle limit; drawing an integer triple and one bit field per
  example fixed them with the same 25-example budget. The Step 5 leaves and
  the settings, pattern and detection leaves then passed.
- Recorder run by hand with the project venv's uv 0.13.4 and Python 3.13.9:
  five records written, each with both accepted runs unchanged and the
  control refused; the recorder found no host path to refuse.
- `ghog day --whole-suite`, the command printed by `pw scope day`, exit 0. A
  first run failed only at check.bat (pyright: an unknown list type; ruff:
  magic values, two six-argument functions, an S105 false positive on a lexer
  variable named `token`); those fixes, a constant-time participant lookup and
  two added tests preceded the green walk.
- `rg -n 'subprocess' tools/release_workflow/sources` finds nothing.
- Markdown check and cSpell on the staged validation plan: no finding, no
  unknown word. Every Python file stays below 650 lines.

Review validation, `ghog day --full=speed --whole-suite` (the built-in
default; no `.review-validation`), is NOT green. Published at the user's
explicit choice, with the failures disclosed:

- Run 1 (08:42): one failure of 6014, a lifecycle CPU overrun (0.141 s,
  limit 0.100 s, not yet proven) in
  `tests/unit/tools/release_workflow/test_version_anchor/test_version_anchor_pbt.py::test_replacement_changes_only_the_token`
  (Step 2, untouched here). It passed in focus and is now recorded as proven
  at 0.094 s, so the CPU band applies to it.
- Run 2 (08:49): that test passed; seven lifecycle wall overruns (1.04 to
  1.85 s, limit 1 s) with CPU within its limit (0.00 to 0.19 s): four
  `test_instruction_structure/test_codex_plugin_structure_tdd.py` cases,
  `test_linear_order/test_linear_order_tdd.py::test_radix_order[0]` and two
  `test_spec_review_requestor_acceptance/test_spec_review_requestor_acceptance_activation_tdd.py`
  cases. None touches the version domain.
- Focused reruns: the codex plugin and spec-review cases pass in focus;
  `test_radix_order` overran wall in focus too, alone and at 17 % host load
  (1.07 s and 2.55 s wall against 0.13 to 0.14 s CPU, a different parameter
  each run), so its time is spent waiting, not computing.
- Consequence: groundhog withheld the coverage and duration-outlier verdicts
  of both walks (`cov=withheld outliers=withheld`). Coverage of the new
  modules is asserted only statically in the validation plan, not measured.
  No budget was changed and no exclusion is accepted in this step.

Architecture: the scanner and the adapter are pure domain code of the
`sources` package (standard library and `sources.model` only), reading
through the `FileView` and learning the participating roots through the
`AdapterSettings` protocol; the process-starting recorder stays in the test
tree and is never imported by a test. Performance: each file is read once per
view, the scanner visits each line once, and each local-link destination is
one lookup in an index built once per settings value. Feature integrity:
nothing ships until Step 9; registering `python` adds detection at
participating roots, and the earlier version tests pass unchanged.

Please check in particular: the scanner's lexer and header handling (what
counts as a statement line, the fail-closed cases), the lock pairing and
schema rules, the workspace and local-link rules against the design's "Python
with uv" section, the settings seam added to `model.py` and `settings.py`
outside the plan's file list, and whether the evidence record and its test
prove what plan decisions Q03, Q04 and Q06 require.

### Implementation report for step 5 version-sources (round 1)

Step 5, "Python and uv adapter with recorded uv evidence", adds the TOML
scanner, the `python` adapter and the recorded uv lock evidence that backs its
registered lock schemas. Nothing ships yet: no handler calls the version
domain until Step 9.

TOML scanner (`tools/release_workflow/sources/toml_scan.py`):

- `locate(text, table, *, package=None) -> Span` splits the text on LF (a
  trailing CR is ignored when matching) and tracks the current header. A
  small lexer, driven by one regular expression per state, follows basic,
  literal and multi-line strings (with escapes), comments and `[`/`{`
  nesting, so only lines that start a statement are read as a header or an
  assignment. A line starting with `[` at statement start is a header; one
  the header patterns cannot read (a quoted key) ends the current table.
- It keeps the `name` and `version` single-line string assignments written
  directly in each occurrence of the target table: `[project]`, or each
  `[[package]]` block, whose sub-tables (`[package.metadata]`) are other
  tables. With `package`, exactly one block must have that one `name`; zero or
  several fail. Exactly one `version` assignment must remain: none fails as an
  unsupported layout (dotted keys, inline tables, multi-line strings) with
  the remedy to write `version = "X.Y.Z"` on its own line; several fail as
  ambiguous.
- `byte_span(text, bom, table, value, *, package=None)` requires the located
  text to equal the `tomllib` value (an escape sequence fails) and maps it to
  bytes through `model.to_byte_spans`.

Python adapter (`tools/release_workflow/sources/python.py`):

- `PythonAdapter`: name `python`, forms `{core}`, default `core`, candidate
  name `pyproject.toml`. `detect` reads `pyproject.toml` and `uv.lock` once
  each through the view.
- No manifest: no lock gives nothing, a lock fails as an orphan. A manifest
  is decoded strictly (mark kept apart) and parsed with `tomllib`; failures
  name the file and the remedy.
- No `[project]` table: `not-participating tool-only` records for the
  manifest and, when present, the lock (never parsed). At the project root
  only, a `[tool.uv.workspace]` whose `members`, net of `exclude`, match a
  declared component root fails (`PurePosixPath.full_match`, relative to the
  project root, case-insensitive where the filesystem is).
- A participating manifest: `[tool.uv.workspace]` fails; then each
  `[tool.uv.sources]` entry (table or list of tables) with `workspace = true`
  fails, and each `path`, and each `name @ file:...` requirement in
  `[project] dependencies`, `[project.optional-dependencies]` or
  `[dependency-groups]` (with `${PROJECT_ROOT}` expanded), is resolved
  against the declaring root; a destination that is a participating root
  fails naming both. A `version` listed in `dynamic`, or not a string, fails
  with the remedy. The value's span comes from `byte_span`.
- A lock: the `(version, revision)` pair must be in
  `REGISTERED_LOCK_SCHEMAS = frozenset({(1, 3), (1, 5)})` (integers only, so
  `version = true` is refused), and a `[manifest]` listing members fails as a
  shared workspace lock. The project needs a `name`; exactly one package must
  have its normalized name (lowercase, `[-_.]+` as `-`) and a source equal to
  `{virtual = "."}` or `{editable = "."}`; that package needs a version
  string. The lock source records the manifest it pairs with.
- `render` returns the value's bytes (the content between the quotes);
  `has_project_version` is true only for a static version string and false
  for an undecodable or unparsable candidate.

Registry and settings seam:

- `sources/__init__.py`: `ADAPTERS = (anchor, python, pattern)`;
  `SUPPORT_MODULES` adds `toml_scan`.
- `sources/model.py`: `AdapterSettings` gains `components` and
  `participant(path)`; `participant_names(project_root, components)` builds
  the case-normalized physical-path index. `sources/settings.py`:
  `VersionSettings` keeps that index in a `cached_property`, so each lookup is
  constant time and a detection pass stays linear in the roots. Neither file
  is in the plan's Step 5 list; both changes are recorded as variance.

Lock evidence (plan decisions Q03, Q04, Q06):

- `tests/unit/tools/release_workflow/lock_evidence_recorder.py`: started by
  hand with `--uv`, `--python` and `--output`, never imported by a test. Each
  of five scenarios runs in a new temporary directory outside the
  repository, with every `UV_*` variable removed: write the manifest at
  `0.13.0`, `uv lock --offline --no-config --python <python>` (revision 5),
  derive revision 3 by setting the revision line, convert to CRLF for the
  CRLF variant, then run `uv lock --locked --offline --no-config --python
  <python>` on the "before" pair, on `version_support.python_pair_edit`
  (the production detection and `plan_edits` for `0.14.0`), and on the
  manifest-only control. Each run records its exit code, its `error:` lines
  and both files' SHA-256 before and after. The JSON is written with sorted
  keys and LF endings, placeholders for the tools, and refused if it still
  holds a host path.
- `test_version_lock_evidence/lock_evidence.v1.json`: five uv 0.13.4 records
  (`uv-0.13.4-v1r5-virtual`, `-v1r5-editable`, `-v1r3-virtual`,
  `-v1r3-editable`, `-v1r3-virtual-crlf`). Every "before" and edited run
  exited 0 with both files unchanged; every control exited 1 ("needs to be
  updated") with both files unchanged.

Tests:

- `test_version_formats/test_toml_scan_tdd.py` and
  `test_version_formats_pbt.py` (properties: generated manifests and locks
  with decoys; an integer triple and one bit field per example keep the
  25-example budget inside the CPU limit).
- `test_python_sources/test_python_sources_tdd.py` (adapter) and
  `test_python_links_tdd.py` (workspaces and links, including one link
  between `.release.ini` components through `detection.detect`).
- `test_version_lock_evidence/test_version_lock_evidence_tdd.py` (the JSON is
  read once per session through the `evidence` fixture).
- `test_version_registry_tdd.py` (order and support modules) and
  `test_version_restoration_tdd.py`, whose matrix now runs the
  `python-virtual` (LF, revision 3, registry package first) and
  `python-editable` (CRLF, snapshot anchor) sets at all three write
  positions.

Writer notes: `.reviews/a.version-sources.step5.journal.md` and
`.reviews/a.version-sources.step5.handoff.md`.

### Change summary for step 5 version-sources (round 1)

Staged paths (19), grouped in the root `a.commit` (two groups, checker
`ready: true`):

1. `feat(release): add the python and uv version adapter`:
   `tools/release_workflow/sources/toml_scan.py`,
   `tools/release_workflow/sources/python.py`,
   `tools/release_workflow/sources/__init__.py`,
   `tools/release_workflow/sources/model.py`,
   `tools/release_workflow/sources/settings.py`,
   `tests/unit/tools/release_workflow/version_support.py`,
   `tests/unit/tools/release_workflow/lock_evidence_recorder.py`,
   `tests/unit/tools/release_workflow/test_version_formats/__init__.py`,
   `tests/unit/tools/release_workflow/test_version_formats/test_toml_scan_tdd.py`,
   `tests/unit/tools/release_workflow/test_version_formats/test_version_formats_pbt.py`,
   `tests/unit/tools/release_workflow/test_python_sources/__init__.py`,
   `tests/unit/tools/release_workflow/test_python_sources/test_python_sources_tdd.py`,
   `tests/unit/tools/release_workflow/test_python_sources/test_python_links_tdd.py`,
   `tests/unit/tools/release_workflow/test_version_lock_evidence/__init__.py`,
   `tests/unit/tools/release_workflow/test_version_lock_evidence/lock_evidence.v1.json`,
   `tests/unit/tools/release_workflow/test_version_lock_evidence/test_version_lock_evidence_tdd.py`,
   `tests/unit/tools/release_workflow/test_version_registry/test_version_registry_tdd.py`,
   `tests/unit/tools/release_workflow/test_version_transition/test_version_restoration_tdd.py`.
2. `docs(version-sources): record step 5 validation`:
   `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md` (Step 5
   sections).

The adapter, its registration and its evidence share one group: plan
decision Q06 forbids registering a lock schema without its record, and the
registry test needs `toml_scan` and `python` registered together. Steps 1 to
4 are committed (`a7c0d7c` to `3a88905`) and are not part of this review.

### Writer response for step 5 version-sources (round 1)

Writer response:

This is the first round of the Step 5 code review; there is no earlier
reviewer feedback to answer.

Choices worth checking, all recorded in the validation plan or the step notes:

- The settings seam: `AdapterSettings` gains `components` (for workspace
  members) and `participant(path)` (for local links), and `VersionSettings`
  indexes the roots once. A first version built that name map at every
  detected root, which is quadratic in the roots; `model.py` and
  `settings.py` are outside the plan's Step 5 file list.
- A local link fails only when its resolved destination is exactly a
  participating root; a path into a file or subdirectory of a component
  (such as a built wheel) is external, as the design's "physical destination
  is a participating root" reads.
- The tool-only workspace rule is applied at the project root only, as the
  design states; a tool-only workspace at a component root stays listed.
- `has_project_version` returns false for an undecodable or unparsable
  candidate, so a broken nested manifest never fails `versions list`.
- The scanner fails closed: an unread header ends the table, and a doubled
  `version` assignment in the target (only possible through a scanning
  mistake, since TOML forbids duplicate keys) fails as ambiguous rather than
  editing either one.
- The `[source:python] form = core` override is accepted by settings and
  changes nothing, since `core` is the adapter's only form; the adapter does
  not read `settings.forms`.
- The recorder drops `UV_*` variables and records only `error:` lines, so no
  user configuration or host path reaches the committed JSON.

### Reviewer focus for step 5 version-sources (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-5-round-1 -->

## Round 1 by reviewer - Step 5

- Recorded: 2026-11-10T09:08:57+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 5
- Outcome: answer

### Assessed index identity for step 5 version-sources (exchange 1) (round 1)

Baseline index tree: 536e54b05b5dd4daa7fa7ad2c39595d52beb0c6e

Assessed index tree: c1f0cc08edc7f030e62b902a9126c54b906090c3

### Implementation check for step 5 version-sources (exchange 1) (round 1)

Result:

Yes. Step 5 has been fully implemented.

The reviewed code implements the planned TOML scanner, Python adapter, registry integration, workspace and local-link checks, and the five recorded uv evidence scenarios. The scanner tracks multiline strings and brackets and fails closed for unsupported owned layouts. Lock pairing checks normalized names, local root sources, integer schema pairs and ambiguity. Evidence tests compare both accepted pairs and the refused manifest-only control using hashes and reproduce the adapter's byte edits. Both Python fixture sets join restoration at every write position.

The AdapterSettings components/participant seam in model.py and settings.py is justified by the planned checks and is already inside the staged step. Its cached physical-path map avoids rebuilding the component index per local link. No DDD-Hexagonal violation or new quadratic path was identified; all Python files remain below 650 lines.

Static unit-test assessment: the gate measures tools, omitting tests and `__init__.py`. Added production functions are reached by the scanner, Python, evidence, registry, restoration and component-detection tests, or internal package calls. Test-support and recorder symbols have test or module-level/internal references. No missing exercise was identified; this is not a measured percentage. Required speed walks withheld coverage.

Functional step completeness and review readiness differ here: mandatory validation remains unsuccessful.

Validation plan effects:

Updated only Step 5 in docs/v0.14.0/plan.v0.14.0.version-sources.validation.md. Retained the exact Yes verdict for implementation, added the failed mandatory speed evidence and clarified the static coverage assessment. No other step, document-level status or umbrella row changed. The launcher attributed the patch; git apply --cached staged only that patch. This is review metadata, with no substantive repair.

### Pre-repair mandatory checks and coverage for step 5 version-sources (exchange 1) (round 1)

The request-time index 536e54b05b5dd4daa7fa7ad2c39595d52beb0c6e matched the independently captured baseline. Writer evidence reports ghog day --whole-suite exit 0 and the Step 5 leaves passing. However, mandatory ghog day --full=speed --whole-suite failed twice: first the unchanged anchor property CPU limit, then seven wall-time gates in other leaves. Both withheld coverage and duration verdicts. Focused passes do not replace the required walk. No reviewer ghog check or affected command was necessary to decide this evidence-only blocker; no day/full or coverage command was run by the reviewer.

### Resolved validation set and sources for step 5 version-sources (exchange 1) (round 1)

- ghog day --full=speed --whole-suite (source: project; built-in ghog day --full=speed default, bound whole-suite scope).
- rg -n 'subprocess' tools/release_workflow/sources (source: plan; expected no matches).

The request records the first as failed and the second as no matches.

### Resolver drift and direction for step 5 version-sources (exchange 1) (round 1)

No drift identified. The current .review-validation path was sampled and is absent, so the current resolver's project default is ghog day --full=speed. The bound scope is whole-suite (fingerprint 686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6). Step 5 adds the subprocess search; there are no request additions. These reproduce the embedded command order and project/plan source labels.

### Repository state around validation for step 5 version-sources (exchange 1) (round 1)

The umbrella comparison reports changed=false with digest 5abf0cb72800e9d07acba786dd90502fcb8879ff41cbcce55b961a95352aaa4c before and after. The same ordered 19-path validation comparison reports only the reviewed Step 5 validation-plan metadata changed, with no ignored or untracked changes. The generic comparator marks that tracked difference unacceptable; inspection and patch attribution establish the explicit reviewed-step metadata exception. No implementation or test file changed during review. Assessed index after staging the attributable metadata is c1f0cc08edc7f030e62b902a9126c54b906090c3.

### Repair inventory for step 5 version-sources (exchange 1) (round 1)

Repairs made:

- docs/v0.14.0/plan.v0.14.0.version-sources.validation.md: polishing-only review metadata recording mandatory validation failure and static coverage limits; staged as an attributable patch. No substantive repair.

Paths staged:

- docs/v0.14.0/plan.v0.14.0.version-sources.validation.md
- tests/unit/tools/release_workflow/lock_evidence_recorder.py
- `tests/unit/tools/release_workflow/test_python_sources/__init__.py`
- tests/unit/tools/release_workflow/test_python_sources/test_python_links_tdd.py
- tests/unit/tools/release_workflow/test_python_sources/test_python_sources_tdd.py
- `tests/unit/tools/release_workflow/test_version_formats/__init__.py`
- tests/unit/tools/release_workflow/test_version_formats/test_toml_scan_tdd.py
- tests/unit/tools/release_workflow/test_version_formats/test_version_formats_pbt.py
- `tests/unit/tools/release_workflow/test_version_lock_evidence/__init__.py`
- tests/unit/tools/release_workflow/test_version_lock_evidence/lock_evidence.v1.json
- tests/unit/tools/release_workflow/test_version_lock_evidence/test_version_lock_evidence_tdd.py
- tests/unit/tools/release_workflow/test_version_registry/test_version_registry_tdd.py
- tests/unit/tools/release_workflow/test_version_transition/test_version_restoration_tdd.py
- tests/unit/tools/release_workflow/version_support.py
- `tools/release_workflow/sources/__init__.py`
- tools/release_workflow/sources/model.py
- tools/release_workflow/sources/python.py
- tools/release_workflow/sources/settings.py
- tools/release_workflow/sources/toml_scan.py

### Commit plan assessment for step 5 version-sources (exchange 1) (round 1)

The reviewer independently ran the canonical commit-plan-check.bat --format json once before assessment: exit 0, schema_version 1, state valid, ready true, diagnostics empty. Its 19 staged paths and two ordered groups matched the request. Group 1, feat(release): add the python and uv version adapter, includes the 18 adapter/registry/settings/test/evidence files; keeping schema registration and its evidence together is appropriate. Group 2, docs(version-sources): record step 5 validation, includes only the validation plan. The later metadata patch changes neither membership, order nor subjects. a.commit remains accurate; no amendment was needed.

### Findings and boundaries for step 5 version-sources (exchange 1) (round 1)

Unresolved findings:

- P1: Mandatory review validation has no green result. Both required ghog day --full=speed --whole-suite attempts failed timing gates and reported cov=withheld outliers=withheld. Publishing at the user's explicit choice permits review but does not satisfy the readiness floor. The plain day pass and static test inspection cannot establish the withheld gate verdicts. Writer action: resolve or diagnose the timing failures through the owning workflow, preserve the configured gates and scope, and publish a replacement request with a successful required walk, including coverage and duration verdicts.

Boundary-crossing work:

- The disclosed failures are in unchanged anchor, instruction-structure, radix-order and specification-review tests. Any fixes outside Step 5 need the owning workflow's scope handling. The reviewer made no such changes.

### Writer instructions for step 5 version-sources (exchange 1) (round 1)

Retain the staged Step 5 reviewer metadata. Establish a green ghog day --full=speed --whole-suite with the same required scope, coverage gate and timing limits; investigate the repeated radix-order wall failures and any remaining lifecycle failure without weakening budgets or excluding cases. Handle any out-of-step fixes through the owning workflow. Refresh validation evidence and the request-time index and publish another review round. No Step 5 implementation defect was identified in this assessment.

### Decision rationale for step 5 version-sources (exchange 1) (round 1)

Changes requested because the validation and coverage floor is not satisfied.

- Identity: pass; exact plan, step 5, round 1, occurrence 1 and request-time index agree.
- Completeness: pass; planned implementation and tests are present.
- Validation and coverage: fail; required speed walks failed and withheld verdicts; static coverage review found no missing exercise.
- Staged attribution: pass; only attributed Step 5 validation metadata was added by the reviewer.
- Unresolved findings: fail; the mandatory validation evidence gap remains open.
- a.commit: pass; independently checked mechanical plan and grouping remain accurate.

No literal Human guidance: block is present. The generic request to make safe repairs does not authorize implementation/test edits under the reviewer instruction; none were made. This advisory disposition does not authorize a commit.

### Final reviewer decision for step 5 version-sources (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-5-round-1 -->

## Round 2 by requestor - Step 5

- Recorded: 2026-11-10T10:24:51+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 5
- Outcome: request

### Review identity for step 5 version-sources (round 2)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.version-sources.md
Implementation step: 5
Review round: 2

### Code review evidence for step 5 version-sources (round 2)

request_index_tree: f05e6db7c3e3161c9973b19e9add3d52ca244631
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)
- `rg -n 'subprocess' tools/release_workflow/sources` (sources: plan)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "none", "requirement": "docs/v0.14.0/feature-request.v0.14.0.version-sources.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: perf(tests): scan Hypothesis constants at collection
group 1 path: tests/conftest.py
group 2: feat(release): add the python and uv version adapter
group 2 path: tools/release_workflow/sources/toml_scan.py
group 2 path: tools/release_workflow/sources/python.py
group 2 path: tools/release_workflow/sources/__init__.py
group 2 path: tools/release_workflow/sources/model.py
group 2 path: tools/release_workflow/sources/settings.py
group 2 path: tests/unit/tools/release_workflow/version_support.py
group 2 path: tests/unit/tools/release_workflow/lock_evidence_recorder.py
group 2 path: tests/unit/tools/release_workflow/test_version_formats/__init__.py
group 2 path: tests/unit/tools/release_workflow/test_version_formats/test_toml_scan_tdd.py
group 2 path: tests/unit/tools/release_workflow/test_version_formats/test_version_formats_pbt.py
group 2 path: tests/unit/tools/release_workflow/test_python_sources/__init__.py
group 2 path: tests/unit/tools/release_workflow/test_python_sources/test_python_sources_tdd.py
group 2 path: tests/unit/tools/release_workflow/test_python_sources/test_python_links_tdd.py
group 2 path: tests/unit/tools/release_workflow/test_version_lock_evidence/__init__.py
group 2 path: tests/unit/tools/release_workflow/test_version_lock_evidence/lock_evidence.v1.json
group 2 path: tests/unit/tools/release_workflow/test_version_lock_evidence/test_version_lock_evidence_tdd.py
group 2 path: tests/unit/tools/release_workflow/test_version_registry/test_version_registry_tdd.py
group 2 path: tests/unit/tools/release_workflow/test_version_transition/test_version_restoration_tdd.py
group 3: docs(version-sources): record step 5 validation
group 3 path: docs/v0.14.0/plan.v0.14.0.version-sources.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.version-sources.validation.md
staged path: tests/conftest.py
staged path: tests/unit/tools/release_workflow/lock_evidence_recorder.py
staged path: tests/unit/tools/release_workflow/test_python_sources/__init__.py
staged path: tests/unit/tools/release_workflow/test_python_sources/test_python_links_tdd.py
staged path: tests/unit/tools/release_workflow/test_python_sources/test_python_sources_tdd.py
staged path: tests/unit/tools/release_workflow/test_version_formats/__init__.py
staged path: tests/unit/tools/release_workflow/test_version_formats/test_toml_scan_tdd.py
staged path: tests/unit/tools/release_workflow/test_version_formats/test_version_formats_pbt.py
staged path: tests/unit/tools/release_workflow/test_version_lock_evidence/__init__.py
staged path: tests/unit/tools/release_workflow/test_version_lock_evidence/lock_evidence.v1.json
staged path: tests/unit/tools/release_workflow/test_version_lock_evidence/test_version_lock_evidence_tdd.py
staged path: tests/unit/tools/release_workflow/test_version_registry/test_version_registry_tdd.py
staged path: tests/unit/tools/release_workflow/test_version_transition/test_version_restoration_tdd.py
staged path: tests/unit/tools/release_workflow/version_support.py
staged path: tools/release_workflow/sources/__init__.py
staged path: tools/release_workflow/sources/model.py
staged path: tools/release_workflow/sources/python.py
staged path: tools/release_workflow/sources/settings.py
staged path: tools/release_workflow/sources/toml_scan.py
```

### Validation scope for step 5 version-sources (round 2)

Validation scope: the whole suite.

### Requestor assessment for step 5 version-sources (round 2)

Writer assessment for Step 5 of the version-sources plan, round 2: the step is
fully implemented (implementation check `Yes. Step 5 has been fully
implemented.`), and round 1 found no Step 5 defect. Its one finding, P1 (no
green required walk), was investigated as the writer instructions asked.

Diagnosis of the timing failures:

- Each radix batch takes 10 to 35 ms on its own (measured outside pytest).
- Hypothesis 6.152.7 scans every newly loaded local module for constants
  before the next generated input. Its site-packages shortcut tests for
  `/site-packages/`, which a Windows path never contains, so every loaded
  module pays a physical path lookup: 0.19 to 0.53 s wall and 0.16 s CPU for
  440 modules in a bare interpreter, more in a pytest worker. The scan landed
  inside the first property test of a worker: the radix overruns and the
  anchor property's CPU overrun of round 1.
- Fix (out of step, at the user's explicit choice, its own `perf(tests)`
  group first in `a.commit`): `tests/conftest.py` runs that scan once per
  worker in `pytest_collection_finish`, outside every measured lifecycle,
  through a guarded import and lookup.
- After the fix, `ghog single` on the radix and anchor property leaves at
  `--full=speed` exit 0, no overrun and no band use, at 92 % host load
  (before it, the radix leaf overran alone at 17 %).

Required walk, `ghog day --full=speed --whole-suite`, 2026-11-10T09:30:
check.bat and the affected tests green; the full stage failed only on 30
lifecycle wall overruns (1.0 to 3.5 s wall, limit 1 s) whose CPU stayed
within its limit (at most 0.19 s), with no assertion failure, at 78 % host
load from other workloads. They are spread over unrelated leaves (question
decisions, review exchange models, ownership and paths, role nature, prompt
workflow, review resume, the radix leaf once at 1.03 s). Groundhog therefore
withheld the coverage and duration-outlier verdicts again; coverage of the
new modules is still assessed statically. The user then directed to move on
when CPU is under budget (see the human guidance); no budget was changed and
no exclusion is accepted.

Other evidence, unchanged from round 1 and still valid: tests first (red at
collection, then green), the recorded uv 0.13.4 evidence, `ghog day
--whole-suite` exit 0, `rg -n 'subprocess' tools/release_workflow/sources`
empty, every Python file below 650 lines. This round also wrapped five bare
`__init__.py` paths of the round 1 answer in code spans in the transcript
(MD050) and replaced one unknown word there at the user's choice; the
transcript stays unstaged for its residual commit. Markdown check and cSpell
on the staged validation plan and the transcript: clean; commit-plan-check:
ready, three groups.

Please check in particular: the conftest warm-up (placement before the
garbage-collector freeze, the guarded lookup, that it changes no budget and
measures nothing), whether the wall-only failures under the human guidance
now satisfy the readiness floor, and the refreshed Step 5 validation entry.

### Implementation report for step 5 version-sources (round 2)

Step 5, "Python and uv adapter with recorded uv evidence", adds the TOML
scanner, the `python` adapter and the recorded uv lock evidence that backs its
registered lock schemas. Nothing ships yet: no handler calls the version
domain until Step 9. The Step 5 code is unchanged since round 1; round 2
adds one out-of-step suite change, described first.

Suite change in round 2 (`tests/conftest.py`, own `perf(tests)` group):

- `_scan_hypothesis_constants()` imports
  `hypothesis.internal.conjecture.providers` and, when it still defines
  `_get_local_constants`, calls it once; an `ImportError` or a missing name
  leaves the suite as before. `pytest_collection_finish` calls it before
  `gc.collect()` and `gc.freeze()`, so the scan of every collected module
  happens once per worker, outside every measured lifecycle; a later lazy
  import makes the next generated input scan only its own new modules.
- The module docstring gains a `Fix:` paragraph with the cause: the scan's
  site-packages shortcut never matches a Windows path, so each loaded module
  paid a physical path lookup inside the first property test of a worker.
- No budget, scope, coverage gate, Hypothesis profile setting or exclusion
  changes.

TOML scanner (`tools/release_workflow/sources/toml_scan.py`):

- `locate(text, table, *, package=None) -> Span` splits the text on LF (a
  trailing CR is ignored when matching) and tracks the current header. A
  small lexer, driven by one regular expression per state, follows basic,
  literal and multi-line strings (with escapes), comments and `[`/`{`
  nesting, so only lines that start a statement are read as a header or an
  assignment. A line starting with `[` at statement start is a header; one
  the header patterns cannot read (a quoted key) ends the current table.
- It keeps the `name` and `version` single-line string assignments written
  directly in each occurrence of the target table: `[project]`, or each
  `[[package]]` block, whose sub-tables (`[package.metadata]`) are other
  tables. With `package`, exactly one block must have that one `name`; zero or
  several fail. Exactly one `version` assignment must remain: none fails as an
  unsupported layout (dotted keys, inline tables, multi-line strings) with
  the remedy to write `version = "X.Y.Z"` on its own line; several fail as
  ambiguous.
- `byte_span(text, bom, table, value, *, package=None)` requires the located
  text to equal the `tomllib` value (an escape sequence fails) and maps it to
  bytes through `model.to_byte_spans`.

Python adapter (`tools/release_workflow/sources/python.py`):

- `PythonAdapter`: name `python`, forms `{core}`, default `core`, candidate
  name `pyproject.toml`. `detect` reads `pyproject.toml` and `uv.lock` once
  each through the view.
- No manifest: no lock gives nothing, a lock fails as an orphan. A manifest
  is decoded strictly (mark kept apart) and parsed with `tomllib`; failures
  name the file and the remedy.
- No `[project]` table: `not-participating tool-only` records for the
  manifest and, when present, the lock (never parsed). At the project root
  only, a `[tool.uv.workspace]` whose `members`, net of `exclude`, match a
  declared component root fails (`PurePosixPath.full_match`, relative to the
  project root, case-insensitive where the filesystem is).
- A participating manifest: `[tool.uv.workspace]` fails; then each
  `[tool.uv.sources]` entry (table or list of tables) with `workspace = true`
  fails, and each `path`, and each `name @ file:...` requirement in
  `[project] dependencies`, `[project.optional-dependencies]` or
  `[dependency-groups]` (with `${PROJECT_ROOT}` expanded), is resolved
  against the declaring root; a destination that is a participating root
  fails naming both. A `version` listed in `dynamic`, or not a string, fails
  with the remedy. The value's span comes from `byte_span`.
- A lock: the `(version, revision)` pair must be in
  `REGISTERED_LOCK_SCHEMAS = frozenset({(1, 3), (1, 5)})` (integers only, so
  `version = true` is refused), and a `[manifest]` listing members fails as a
  shared workspace lock. The project needs a `name`; exactly one package must
  have its normalized name (lowercase, `[-_.]+` as `-`) and a source equal to
  `{virtual = "."}` or `{editable = "."}`; that package needs a version
  string. The lock source records the manifest it pairs with.
- `render` returns the value's bytes (the content between the quotes);
  `has_project_version` is true only for a static version string and false
  for an undecodable or unparsable candidate.

Registry and settings seam:

- `sources/__init__.py`: `ADAPTERS = (anchor, python, pattern)`;
  `SUPPORT_MODULES` adds `toml_scan`.
- `sources/model.py`: `AdapterSettings` gains `components` and
  `participant(path)`; `participant_names(project_root, components)` builds
  the case-normalized physical-path index. `sources/settings.py`:
  `VersionSettings` keeps that index in a `cached_property`, so each lookup is
  constant time and a detection pass stays linear in the roots. Neither file
  is in the plan's Step 5 list; both changes are recorded as variance.

Lock evidence (plan decisions Q03, Q04, Q06):

- `tests/unit/tools/release_workflow/lock_evidence_recorder.py`: started by
  hand with `--uv`, `--python` and `--output`, never imported by a test. Each
  of five scenarios runs in a new temporary directory outside the
  repository, with every `UV_*` variable removed: write the manifest at
  `0.13.0`, `uv lock --offline --no-config --python <python>` (revision 5),
  derive revision 3 by setting the revision line, convert to CRLF for the
  CRLF variant, then run `uv lock --locked --offline --no-config --python
  <python>` on the "before" pair, on `version_support.python_pair_edit`
  (the production detection and `plan_edits` for `0.14.0`), and on the
  manifest-only control. Each run records its exit code, its `error:` lines
  and both files' SHA-256 before and after. The JSON is written with sorted
  keys and LF endings, placeholders for the tools, and refused if it still
  holds a host path.
- `test_version_lock_evidence/lock_evidence.v1.json`: five uv 0.13.4 records
  (`uv-0.13.4-v1r5-virtual`, `-v1r5-editable`, `-v1r3-virtual`,
  `-v1r3-editable`, `-v1r3-virtual-crlf`). Every "before" and edited run
  exited 0 with both files unchanged; every control exited 1 ("needs to be
  updated") with both files unchanged.

Tests:

- `test_version_formats/test_toml_scan_tdd.py` and
  `test_version_formats_pbt.py` (properties: generated manifests and locks
  with decoys; an integer triple and one bit field per example keep the
  25-example budget inside the CPU limit).
- `test_python_sources/test_python_sources_tdd.py` (adapter) and
  `test_python_links_tdd.py` (workspaces and links, including one link
  between `.release.ini` components through `detection.detect`).
- `test_version_lock_evidence/test_version_lock_evidence_tdd.py` (the JSON is
  read once per session through the `evidence` fixture).
- `test_version_registry_tdd.py` (order and support modules) and
  `test_version_restoration_tdd.py`, whose matrix now runs the
  `python-virtual` (LF, revision 3, registry package first) and
  `python-editable` (CRLF, snapshot anchor) sets at all three write
  positions.

Writer notes: `.reviews/a.version-sources.step5.journal.md` and
`.reviews/a.version-sources.step5.handoff.md`.

### Change summary for step 5 version-sources (round 2)

Staged paths (20), grouped in the root `a.commit` (three groups, checker
`ready: true`):

1. `perf(tests): scan Hypothesis constants at collection`:
   `tests/conftest.py` (new in round 2, out of step at the user's choice).
2. `feat(release): add the python and uv version adapter`: unchanged since
   round 1, the 18 adapter, registry, settings, test and evidence paths.
3. `docs(version-sources): record step 5 validation`:
   `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md` (the reviewer's
   round 1 metadata kept; writer round 2 paragraph in the analysis and a
   round 2 validation-evidence bullet added).

Changes since round 1: `tests/conftest.py` added to the index and the plan's
first group; the Step 5 validation entry refreshed. Unstaged, for the
residual commit: the transcript, where round 1's five bare `__init__.py`
paths are now code spans and one unknown word became `case-normalized`. The
bound scope (whole suite) and the requirement are unchanged.

### Human guidance and writer response for step 5 version-sources (round 2)

Human guidance:

User direction of 2026-11-10, given after the latest required speed walk
failed only on wall overruns with CPU under budget at 78 % host load from
other workloads: "If CPU is under budget, do move on".

The writer reads it as: lifecycle wall-time overruns whose CPU stays within
its limit, and that come with no assertion failure, no CPU overrun and no
duration outlier, do not block this review. No budget is changed and no test
is excluded.

Writer response:

Response to the round 1 answer (changes requested; no Step 5 implementation
defect found).

- Accepted: the reviewer's metadata patch to the Step 5 validation entry is
  kept. The writer refreshed that entry with the round 2 validation result
  below; the reviewer's round 1 paragraph stays as the record of that round.
- P1 (no green mandatory walk): accepted and addressed by diagnosis, not by a
  budget change or an exclusion. As the writer instructions asked, the
  repeated `test_radix_order` wall failures were investigated first.
  - Outside pytest, each radix batch takes 10 to 35 ms. Hypothesis 6.152.7's
    local-constants scan (`hypothesis.internal.conjecture.providers._get_local_constants`)
    takes 0.19 to 0.53 s of wall time and 0.16 s of CPU for 440 modules. It
    runs before the next generated input whenever `sys.modules` has grown,
    and its site-packages shortcut tests for `/site-packages/`, which a
    Windows path never contains, so every loaded module pays a physical path
    lookup. In a pytest worker the scan landed inside the first property test
    that saw new modules: the radix overruns, and the anchor property's CPU
    overrun of round 1.
  - Fix, at the user's explicit choice (out of step, own commit group, first
    in `a.commit`): `tests/conftest.py` runs that scan once per worker in
    `pytest_collection_finish`, outside every measured lifecycle, through a
    guarded import. No budget, scope, coverage gate or exclusion changed.
  - Boundary: the change is suite infrastructure, not Step 5 scope; it is
    disclosed here and in the assessment, and committed as its own
    `perf(tests)` group so it can be reviewed and reverted on its own.
- No disagreement with the round 1 answer.

### Reviewer focus for step 5 version-sources (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-5-round-2 -->

## Round 2 by reviewer - Step 5

- Recorded: 2026-11-10T10:35:52+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 5
- Outcome: answer

### Assessed index identity for step 5 version-sources (exchange 1) (round 2)

Baseline index tree: f05e6db7c3e3161c9973b19e9add3d52ca244631

Assessed index tree: 136f2f2f026346954c413583a8d714b42cb7cd08

### Implementation check for step 5 version-sources (exchange 1) (round 2)

Result:

Yes. Step 5 has been fully implemented.

The round 1 implementation assessment still applies: comparison against its assessed index tree shows that all 18 adapter, registry, settings, test and recorded-evidence paths are unchanged. The scanner, Python adapter, workspace and local-link refusals, registered uv schemas, five evidence scenarios and restoration cases fulfill the named step. No implementation defect was found.

The newly staged suite hook calls the installed Hypothesis constants scanner once at collection finish, before gc.collect and gc.freeze. Inspection of Hypothesis's provider confirms that it caches seen modules and scans only newly loaded modules thereafter. Its guarded import and missing-name fallback preserve compatibility if that internal entry point disappears. It changes no lifecycle limit, profile, example budget or exclusion. The helper is referenced by the existing pytest hook; no unreferenced top-level symbol was added outside the coverage gate.

Static coverage assessment finds no gap in the unchanged Step 5 production functions, support symbols or recorded-evidence checks. No measured coverage percentage is claimed. No architecture, complexity, file-size or feature-integrity regression was identified.

The suite hook is outside Step 5 but was explicitly user-authorized and separately grouped by the writer according to the request. This boundary variance is reviewed and resolved; no additional boundary-crossing work is requested.

Validation plan effects:

Only the exact Step 5 analysis was amended with the round 2 reviewer assessment, the explicit CPU guidance, the unchanged implementation and the unavailable measured verdicts. The Yes verdict remains; no other step or umbrella status changed. This metadata-only patch was proven attributable and staged separately from any writer work.

### Pre-repair mandatory checks and coverage for step 5 version-sources (exchange 1) (round 2)

No reviewer implementation repair or test execution occurred. The writer's saved speed-walk output and the matching current log tail show check exit 0, affected exit 0 (zero selected tests under testmon), and full/day exit 2 with 30 lifecycle errors. Every error is wall-only: CPU is at most 0.187500 s against the applicable 0.250 s band limit; no assertion failure or traceback appears in the error report. Coverage, outlier and exclusion verdicts are withheld. The log also records radix CPU proof being lost after this run; the guidance accepts this run's applicable CPU limits and does not create proof for a future run.

The earlier plain-day pass, focused passes, recorded uv evidence and subprocess search remain supporting evidence, without being relabeled as a green speed walk. Reviewer verification consisted of static inspection, an independent commit-plan check and retained boundary captures; no full walk or coverage measurement was repeated.

### Resolved validation set and sources for step 5 version-sources (exchange 1) (round 2)

- `ghog day --full=speed --whole-suite` (source: project; built-in default completed with the bound whole-suite scope). Executed by the writer, exit 2; accepted for this round under the explicit CPU guidance, with withheld verdicts disclosed.
- `rg -n 'subprocess' tools/release_workflow/sources` (source: plan; expected no matches). Writer result: no matches; unchanged implementation since round 1.

### Resolver drift and direction for step 5 version-sources (exchange 1) (round 2)

No drift. The current .review-validation path was sampled and is absent. The built-in project default remains ghog day --full=speed; the bound whole-suite fingerprint is 686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6. The exact plan adds the subprocess search, and there are no request additions. Command order and source labels match the request. The human exception does not alter the resolver or repository budgets.

### Repository state around validation for step 5 version-sources (exchange 1) (round 2)

The request-time and baseline index both equal f05e6db7c3e3161c9973b19e9add3d52ca244631. The assessed index is 136f2f2f026346954c413583a8d714b42cb7cd08, differing only by the attributable Step 5 assessment patch. Relative to the round 1 assessed tree, the writer changed only tests/conftest.py and the Step 5 validation metadata.

The applicable umbrella digest is unchanged (5abf0cb72800e9d07acba786dd90502fcb8879ff41cbcce55b961a95352aaa4c). The same ordered 20-path validation capture found only the intended validation-plan change; the generic comparator reports acceptable=false for that tracked path, which inspection confines to permitted Step 5 reviewer metadata. No other captured tracked or untracked path changed. No tracked command side effect or substantive reviewer repair occurred. The writer's unstaged transcript work was neither read as review context nor modified or staged.

### Repair inventory for step 5 version-sources (exchange 1) (round 2)

Repairs made:

- `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md`: polishing-only review metadata in Step 5; no implementation, test or acceptance behavior changed. Attribution succeeded; only the returned patch was staged.

Paths staged:

- `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md`
- `tests/conftest.py`
- `tests/unit/tools/release_workflow/lock_evidence_recorder.py`
- `tests/unit/tools/release_workflow/test_python_sources/__init__.py`
- `tests/unit/tools/release_workflow/test_python_sources/test_python_links_tdd.py`
- `tests/unit/tools/release_workflow/test_python_sources/test_python_sources_tdd.py`
- `tests/unit/tools/release_workflow/test_version_formats/__init__.py`
- `tests/unit/tools/release_workflow/test_version_formats/test_toml_scan_tdd.py`
- `tests/unit/tools/release_workflow/test_version_formats/test_version_formats_pbt.py`
- `tests/unit/tools/release_workflow/test_version_lock_evidence/__init__.py`
- `tests/unit/tools/release_workflow/test_version_lock_evidence/lock_evidence.v1.json`
- `tests/unit/tools/release_workflow/test_version_lock_evidence/test_version_lock_evidence_tdd.py`
- `tests/unit/tools/release_workflow/test_version_registry/test_version_registry_tdd.py`
- `tests/unit/tools/release_workflow/test_version_transition/test_version_restoration_tdd.py`
- `tests/unit/tools/release_workflow/version_support.py`
- `tools/release_workflow/sources/__init__.py`
- `tools/release_workflow/sources/model.py`
- `tools/release_workflow/sources/python.py`
- `tools/release_workflow/sources/settings.py`
- `tools/release_workflow/sources/toml_scan.py`

### Commit plan assessment for step 5 version-sources (exchange 1) (round 2)

The independent checker returned state=valid, ready=true, diagnostics=[] and the same ordered 20 staged paths as the request. Its three groups are accurate: perf(tests): scan Hypothesis constants at collection (tests/conftest.py); feat(release): add the python and uv version adapter (18 paths); docs(version-sources): record step 5 validation (one path). The reviewer metadata fits the existing third group; a.commit was unchanged. Mechanical readiness does not authorize a commit.

### Findings and boundaries for step 5 version-sources (exchange 1) (round 2)

Unresolved findings: None.

Boundary-crossing work: None.

### Human guidance response for step 5 version-sources (exchange 1) (round 2)

Human guidance:

Human guidance:

User direction of 2026-11-10: "If CPU is under budget, do move on".

The request places this direction after the latest required speed walk failed on wall overruns with CPU under its applicable limits at high host load.

Guidance response:

Accepted for this round. Independent log inspection confirms all 30 lifecycle errors stayed within their applicable CPU limits, with no assertion error or traceback in the full-stage error report. The writer diagnosed the previous initial Hypothesis scan cost and staged a separately grouped collection-time warm-up. No test was excluded or limit relaxed.

The explicit user instruction takes precedence over the skill's default requirement for another green mandatory walk. This exception is applied transparently to the actual exit-2 result, including its withheld measured verdicts. The writer's phrase "no duration outlier" cannot be established from a withheld outlier verdict: absence of outliers is not claimed. Static coverage finds no Step 5 gap; measured coverage and outlier results remain unknown. Identity, scope, attribution and implementation requirements were independently checked and remain satisfied. No code repair was authorized or performed by the reviewer.

### Writer instructions for step 5 version-sources (exchange 1) (round 2)

No implementation rework is requested. Preserve the explicit validation exception and unavailable measured verdicts in the handoff. Follow the requestor's human convergence gate; this recommendation does not authorize a commit or any owning-workflow action.

### Decision rationale for step 5 version-sources (exchange 1) (round 2)

Advisory commit-ready under the explicit human CPU direction. Identity: pass, exact round 2/occurrence 1 and request-time tree. Completeness: pass, unchanged Step 5 implementation and reviewed collection hook. Validation and coverage: accepted with the user-directed exception for the verified wall-only errors; checks are green, no CPU/assertion failure is reported, and static coverage finds no gap. The speed command remains exit 2 and its measured coverage/outlier verdicts remain unavailable. Attribution: pass, only exact Step 5 reviewer metadata staged. Findings: none unresolved under that exception. a.commit: pass, independent checker ready and all three groups accurate. This round made no substantive reviewer repair.

### Final reviewer decision for step 5 version-sources (exchange 1) (round 2)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-5-round-2 -->

## Round 2 by human - Step 5 - human-confirmation

- Recorded: 2026-11-10T10:53:30+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 5
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->

## Round 1 by requestor - Step 6

- Recorded: 2026-11-10T15:13:43+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Implementation step: 6
- Outcome: request

### Review identity for step 6 version-sources (round 1)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.version-sources.md
Implementation step: 6
Review round: 1

### Code review evidence for step 6 version-sources (round 1)

request_index_tree: ee21c5fa76c50c6b2a62a43482898da83148faaa
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.version-sources.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(release): add the npm version adapter
group 1 path: tools/release_workflow/sources/json_scan.py
group 1 path: tools/release_workflow/sources/npm.py
group 1 path: tools/release_workflow/sources/__init__.py
group 1 path: tools/release_workflow/sources/model.py
group 1 path: tests/unit/tools/release_workflow/version_support.py
group 1 path: tests/unit/tools/release_workflow/lock_evidence_recorder.py
group 1 path: tests/unit/tools/release_workflow/test_version_lock_evidence/lock_evidence.v1.json
group 1 path: tests/unit/tools/release_workflow/test_version_lock_evidence/test_version_lock_evidence_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_npm_sources/__init__.py
group 1 path: tests/unit/tools/release_workflow/test_npm_sources/test_npm_sources_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_version_formats/test_json_scan_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_version_formats/test_version_formats_pbt.py
group 1 path: tests/unit/tools/release_workflow/test_version_model/test_version_model_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_version_registry/test_version_registry_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_version_transition/test_version_restoration_tdd.py
group 2: docs(version-sources): record step 6 validation
group 2 path: docs/v0.14.0/plan.v0.14.0.version-sources.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.version-sources.validation.md
staged path: tests/unit/tools/release_workflow/lock_evidence_recorder.py
staged path: tests/unit/tools/release_workflow/test_npm_sources/__init__.py
staged path: tests/unit/tools/release_workflow/test_npm_sources/test_npm_sources_tdd.py
staged path: tests/unit/tools/release_workflow/test_version_formats/test_json_scan_tdd.py
staged path: tests/unit/tools/release_workflow/test_version_formats/test_version_formats_pbt.py
staged path: tests/unit/tools/release_workflow/test_version_lock_evidence/lock_evidence.v1.json
staged path: tests/unit/tools/release_workflow/test_version_lock_evidence/test_version_lock_evidence_tdd.py
staged path: tests/unit/tools/release_workflow/test_version_model/test_version_model_tdd.py
staged path: tests/unit/tools/release_workflow/test_version_registry/test_version_registry_tdd.py
staged path: tests/unit/tools/release_workflow/test_version_transition/test_version_restoration_tdd.py
staged path: tests/unit/tools/release_workflow/version_support.py
staged path: tools/release_workflow/sources/__init__.py
staged path: tools/release_workflow/sources/json_scan.py
staged path: tools/release_workflow/sources/model.py
staged path: tools/release_workflow/sources/npm.py
```

### Validation scope for step 6 version-sources (round 1)

Validation scope: the whole suite.

### Requestor assessment for step 6 version-sources (round 1)

Writer assessment for Step 6 of the version-sources plan, round 1: the step is
fully implemented, and its implementation check records
`Yes. Step 6 has been fully implemented.` in the staged validation plan.

Evidence, all on the staged tree:

- Tests first: `ghog single` on the new and changed leaves failed at
  collection (five errors, `ImportError: cannot import name 'npm'`, exit 4).
  After the implementation only the three npm evidence tests failed, pending
  the recording; every scanner, adapter, registry, model and restoration test
  passed.
- Recorder run by hand with the project venv's uv 0.13.4 and Python 3.13.9
  and with npm 10.8.3 on Node 22.9.0: eight records written with no host
  path; the five uv records are byte-identical to the committed ones. In
  every npm record, `npm ci` and the lock-only check exit 0 with both files
  unchanged on the "before" and edited pairs, and the lock-only check on the
  manifest-only control exits 0 and rewrites the lock to root versions
  `0.0.25` in the same format. A second recording added the note that `npm ci`
  ignores the root version, which the implementation check found missing.
- `ghog day --whole-suite`, the command printed by `pw scope day`, exit 0 on
  the final tree. Earlier runs failed only at check.bat: ty and pyright on
  tuple literals typed as `JsonPath` keys and an untyped empty set in tests,
  then radon grade C on the npm records test, fixed by a helper.
- Review validation, `ghog day --full=speed --whole-suite` (the built-in
  default; no `.review-validation`): exit 0 with `cov=100 outliers=0
  excluded=0 proof=speed`, on index tree
  `ee21c5fa76c50c6b2a62a43482898da83148faaa`. The first attempt failed on one
  lifecycle wall overrun at teardown of
  `tests/unit/tools/test_codex_plugin_package/test_codex_plugin_package_tdd.py::test_repository_package_is_valid`
  (1.65 s wall, 0.06 s CPU within its limit; unrelated to the version
  domain), which passed in focus; the restarted walk was green. No budget was
  changed and no exclusion is accepted.
- `rg -n 'lockfileVersion' tools/release_workflow/sources/npm.py` shows the
  format check and the format 1 remedy; `rg -n 'subprocess'
  tools/release_workflow/sources` finds nothing. Every Python file stays below
  650 lines.
- Markdown check and cSpell on the staged validation plan: no finding, no
  unknown word.

Architecture: the scanner and the adapter are pure domain code of the
`sources` package (standard library, `sources.model` and `sources.json_scan`
only), reading through the `FileView` and learning the configured form and
participating roots through the `AdapterSettings` protocol; the cross-root
name index lives in the phase's view, so the adapter keeps no state. The
process-starting recorder stays in the test tree and is never imported by a
test. Performance: each file is read once per view, the scanner matches each
character once, each specifier costs one lookup, and the name index is built
at most once per view. Feature integrity: nothing ships until Step 9;
registering `npm` adds detection at participating roots, and the earlier
version tests pass unchanged.

Please check in particular: the scanner's frame tracking and its duplicate
and root rules, the lock pairing and format rules against the design's "npm"
section, the readings listed in the writer response (workspaces in a
tool-only manifest, the unnamed-manifest name rule, `workspace:` matching),
the `AdapterSettings.forms` and `FileView.derived` seam added to `model.py`
outside the plan's file list, and whether the npm records and their test prove
what plan decisions Q05 and Q06 require.

### Implementation report for step 6 version-sources (round 1)

Step 6, "npm adapter with recorded npm evidence", adds the JSON scanner, the
`npm` adapter and the recorded npm lock evidence that backs its supported lock
formats. Nothing ships yet: no handler calls the version domain until Step 9.

JSON scanner (`tools/release_workflow/sources/json_scan.py`):

- `locate(text, paths) -> dict[JsonPath, Span]` matches one token expression
  (string, `{`/`[`, `}`/`]`, comma, colon, scalar) from position to position
  over the decoded text. A `_Scanner` keeps a stack of `_Frame` values: each
  open object or array, the key path reaching it (tracked only while it is a
  prefix of an owned path, `None` below an array), its last key (decoded with
  `json.loads` only when it holds a backslash) and, when the container itself
  is an owned value, its start offset.
- A value whose key path is owned is recorded: a string's content between
  the quotes, a scalar's token, or a container's whole text at its close. A
  second value on the same owned path fails as ambiguous (`json` keeps the
  last one silently); duplicates elsewhere are ignored. The first token must
  open the root object and nothing may follow its close; otherwise, or when
  the text ends inside it, the text "is not one JSON object". Token handlers
  are dispatched through a table to keep each function below radon's C grade.
- `byte_spans(text, bom, paths, values)` locates every owned path (so a
  duplicate `lockfileVersion` fails even though it is not edited), requires
  each string to edit to read exactly as its parsed value (an escape, or a
  value the text does not hold, fails), and maps all spans to bytes in one
  `model.to_byte_spans` walk, so both lock edits compose from one original.
  `spell(path)` writes `packages[""].version` for diagnostics and fields.

npm adapter (`tools/release_workflow/sources/npm.py`):

- `NpmAdapter`: name `npm`, forms `{release-only, core, snapshot}`, default
  `release-only`, candidate name `package.json`. Every owned field of a root
  takes `settings.forms.get("npm", Form.RELEASE_ONLY)`.
- `detect` reads `package.json` and `package-lock.json` once each. No manifest:
  no lock gives nothing, a lock fails as an orphan. A manifest is decoded
  strictly (mark kept apart) and must parse as one JSON object.
- A `workspaces` field fails at once, whether or not the manifest has a
  version. A manifest without `version` gives `not-participating tool-only`
  records for it and, when present, its lock (field `packages[""].version`,
  never parsed).
- A participating manifest: an `npm-shrinkwrap.json` at the root fails; then
  each string specifier of `dependencies`, `devDependencies`,
  `optionalDependencies` and `peerDependencies` is checked. `file:` and
  `link:` destinations (`url2pathname(urlsplit(spec).path)`, relative to the
  declaring root, resolved) that are a participating root fail through one
  `settings.participant` lookup, naming both roots. A `workspace:` specifier
  fails when its dependency name is the name of a participating npm manifest
  (a root manifest with a string name and version), looked up in an index
  built once per view through `FileView.derived`. A non-string version
  fails with the remedy; the version's span comes from `byte_spans`.
- A lock: `lockfileVersion` 1 fails with the remedy to regenerate the lock
  with npm 7 or later; any other value outside
  `SUPPORTED_LOCK_FORMATS = frozenset({2, 3})` (integers only, so `"3"` and
  `true` are refused) fails. `packages[""].name`, when the manifest has a
  name, must equal it; `packages[""].version` must be a string; a top-level
  `version` must be a string where present. Each owned string becomes one
  source (`version`, then `packages[""].version`) recording its manifest.
- `render` returns the value's bytes; `has_project_version` is true only for
  a manifest with its own version string and false for an unreadable one.

Registry and model seam:

- `sources/__init__.py`: `ADAPTERS = (anchor, python, npm, pattern)`;
  `SUPPORT_MODULES` adds `json_scan`.
- `sources/model.py` (outside the plan's Step 6 list, recorded as variance):
  `AdapterSettings.forms`, already held by `VersionSettings`, which no
  adapter read before; `FileView.derived(key, compute)`, a value computed
  once per key for the view's phase. Without it, each root's `workspace:`
  check would scan every root's manifest, quadratic in the roots.

Lock evidence (plan decisions Q05 and Q06):

- `lock_evidence_recorder.py` gains `--npm` and `--node-dir` (all five
  arguments are required and the whole file is rewritten); its uv classes
  are renamed `UvScenario` and `UvTools` beside `NpmScenario` and `NpmTools`.
  Each npm scenario runs in a new temporary directory: write a `private:
  true` `package.json` at `0.0.24`, `npm install --package-lock-only
  --offline --lockfile-version <2|3> --ignore-scripts --no-audit --no-fund`,
  convert both files to CRLF for the format 3 variant, then run `npm ci
  --offline --ignore-scripts --no-audit --no-fund` and the lock-only check
  `npm install --package-lock-only --offline --ignore-scripts --no-audit
  --no-fund` on the "before" pair and on `version_support.pair_edit(npm.ADAPTER,
  ...)` for `0.0.25`, then the lock-only check on the manifest-only control.
  `node_modules` is removed before each run; the Node directory is prepended
  to the child `PATH` only, `npm_config_*` variables are removed, and the
  cache and user configuration point into the scratch directory. Each run
  records its exit code, `npm error` lines, both files' SHA-256 before and
  after, and the lock's format and root versions after it.
- `lock_evidence.v1.json`: the five uv records are byte-identical to the
  committed ones; three npm records (`npm-10.8.3-lock2-root`,
  `npm-10.8.3-lock3-root`, `npm-10.8.3-lock3-root-crlf`, npm 10.8.3 on Node
  v22.9.0) each carry a note that `npm ci` does not compare the root
  version.

Test support and tests:

- `version_support.py`: `RootSettings.forms`; `package_json` and
  `package_lock` (two-space JSON, LF, as npm writes them); the `npm-lock2`
  and `npm-lock3-crlf` restoration sets (three writes each); Step 5's
  `python_pair_edit` generalized to `pair_edit(adapter, root, target)`.
- New: `test_version_formats/test_json_scan_tdd.py`,
  `test_npm_sources/__init__.py`, `test_npm_sources/test_npm_sources_tdd.py`.
  Extended: the formats property file (JSON property), the evidence test (npm
  records), the model test (`FileView.derived`), the registry test (order and
  support modules) and the restoration test docstring (the npm sets run
  through the existing matrix).

Writer notes: `.reviews/a.version-sources.step6.journal.md` and
`.reviews/a.version-sources.step6.handoff.md`.

### Change summary for step 6 version-sources (round 1)

Staged paths (16), grouped in the root `a.commit` (two groups, checker
`ready: true`):

1. `feat(release): add the npm version adapter`:
   `tools/release_workflow/sources/json_scan.py`,
   `tools/release_workflow/sources/npm.py`,
   `tools/release_workflow/sources/__init__.py`,
   `tools/release_workflow/sources/model.py`,
   `tests/unit/tools/release_workflow/version_support.py`,
   `tests/unit/tools/release_workflow/lock_evidence_recorder.py`,
   `tests/unit/tools/release_workflow/test_version_lock_evidence/lock_evidence.v1.json`,
   `tests/unit/tools/release_workflow/test_version_lock_evidence/test_version_lock_evidence_tdd.py`,
   `tests/unit/tools/release_workflow/test_npm_sources/__init__.py`,
   `tests/unit/tools/release_workflow/test_npm_sources/test_npm_sources_tdd.py`,
   `tests/unit/tools/release_workflow/test_version_formats/test_json_scan_tdd.py`,
   `tests/unit/tools/release_workflow/test_version_formats/test_version_formats_pbt.py`,
   `tests/unit/tools/release_workflow/test_version_model/test_version_model_tdd.py`,
   `tests/unit/tools/release_workflow/test_version_registry/test_version_registry_tdd.py`,
   `tests/unit/tools/release_workflow/test_version_transition/test_version_restoration_tdd.py`.
2. `docs(version-sources): record step 6 validation`:
   `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md` (Step 6
   sections).

The adapter, its registration and its evidence share one group: plan
decision Q06 forbids supporting a lock format without its record, and the
registry and restoration tests need `json_scan` and `npm` registered
together. Steps 1 to 5 are committed and pushed (`a7c0d7c` to `b8e03a5`) and
are not part of this review.

### Writer response for step 6 version-sources (round 1)

Writer response:

This is the first round of the Step 6 code review; there is no earlier
reviewer feedback to answer.

Choices worth checking, all recorded in the validation plan or the step notes:

- The model seam: `AdapterSettings.forms` (npm is the first adapter to apply
  a configured form) and `FileView.derived`, which holds the participating
  npm package-name index once per view. `model.py` and
  `test_version_model_tdd.py` are outside the plan's Step 6 file list.
- A `workspaces` field fails even in a manifest without `version`: the
  design's npm section states the rule without the tool-only exception the
  Python section spells out, and npm workspaces are deferred as a whole.
  Links, the shrinkwrap check and every lock check apply to participating
  manifests only, as for Python.
- `packages[""].name` is compared only when the manifest has a name: npm
  writes the folder name there for an unnamed package, so comparing would
  refuse a valid lock.
- `workspace:` (plan decision Q15) matches the dependency key against the
  names of participating manifests that carry a version; a tool-only or
  unreadable manifest is not a participating package, and its name is
  external.
- The scanner relies on the caller having parsed the text with `json`
  first: it checks only the one-object root it depends on, not bracket
  matching or escape validity.
- The release-only refusal is proven through `set_versions` (status 2, no
  source or evidence write). `check` reporting drift is a Step 9 command; this
  step asserts the differing expected value it will report.
- The evidence: the npm fixture runs from `0.0.24` to `0.0.25` as the plan
  states (uv stays `0.13.0` to `0.14.0`); re-recording kept the uv records
  byte-identical. The control runs only the lock-only check, as plan decision
  Q05 lists, and each npm record notes that `npm ci` ignores the root version.
- Step 5's validation entry still names `python_pair_edit`, renamed
  `pair_edit` here; the Step 6 feature-integrity note records the rename
  rather than editing the Step 5 record.

### Reviewer focus for step 6 version-sources (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-6-round-1 -->

## Round 1 by reviewer - Step 6

- Recorded: 2026-11-10T15:25:29+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 6
- Outcome: answer

### Assessed index identity for step 6 version-sources (exchange 1) (round 1)

Baseline index tree: ee21c5fa76c50c6b2a62a43482898da83148faaa

Assessed index tree: 32708897e9cf81050f140fb30f5a1850a33327c6

### Implementation check for step 6 version-sources (exchange 1) (round 1)

Result:

Yes. Step 6 has been fully implemented.

Reviewed the exact Step 6 plan and design, all 16 staged paths, the scanner and adapter, the model and registry changes, the recorder, recorded evidence, unit tests and restoration matrix. Scanner paths and spans distinguish nested and array decoys, reject duplicate owned values and escaped version text, and map UTF-8/BOM offsets in one pass. The npm adapter implements the configured forms, tool-only reporting, workspace and participating-link refusals, shrinkwrap and orphan rejection, formats 2 and 3, the format 1 remedy and root identity/version checks. Tests exercise the required failures, paired edits, byte preservation and restoration at every write position.

The two writer-authored files outside the Step 6 plan list, `sources/model.py` and its model test, supply the existing configured forms through the protocol and compute the npm name index once per view. This is a justified Step 6 dependency with unit coverage, rather than outstanding work for another step. Architecture stays within the source domain; no production subprocess or new quadratic scan was introduced. The workspaces rule also applies to tool-only manifests as the npm design states. The unnamed-manifest rule accommodates npm's folder-derived name.

Static coverage assessment: the configured gate measures `tools`, omitting test files and initializers. The scanner, adapter and model unit tests exercise their new behavior. Registry and support symbols outside the gate are referenced by tests; recorder symbols are reached within its own module, with output checked as data rather than importing the process launcher into pytest. No uncovered unit-tested class or unreferenced added top-level symbol was identified. Step 9 still owns command-level `check` reporting.

Validation plan effects:

Added only the independent round 1 assessment under Analysis of Step 6 implementation state in `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md`. The Yes result remains justified. Other steps, document-level status and umbrella rows were not edited. This is polishing-only review metadata.

### Pre-repair mandatory checks and coverage for step 6 version-sources (exchange 1) (round 1)

The request-time and captured baseline index trees both equal `ee21c5fa76c50c6b2a62a43482898da83148faaa`. The retained final writer speed log ends at 2026-11-10T15:10:47+01:00 with `exit=0 cov=100 outliers=0 excluded=0 proof=speed`, whole suite, after 6101 tests. The saved day proof and core-owned scope capture have matching fingerprint `686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6`. The earlier unrelated wall overrun passed in focus and the restarted full walk was green; no timing exception is used in this assessment.

Independently matched the npm accepted-pair SHA-256 values to the UTF-8 fixture bytes for all three records, inspected all five checks per record and their manifest-only lock rewrite, and compared the five unchanged uv records against HEAD. The recorder and replay tests support the format registry and CRLF variant. No reviewer test command or coverage measurement was performed; reported coverage is writer evidence, supplemented by static review.

### Resolved validation set and sources for step 6 version-sources (exchange 1) (round 1)

`ghog day --full=speed --whole-suite` (source: project). It is mandatory writer evidence, not a reviewer command.

### Resolver drift and direction for step 6 version-sources (exchange 1) (round 1)

None. The project declaration `.review-validation` is absent. An independent call to the current resolver with the bound whole-suite selector returns exactly the request's one project command; no plan or request additions are declared.

### Repository state around validation for step 6 version-sources (exchange 1) (round 1)

Umbrella digest comparison reports unchanged (`5abf0cb72800e9d07acba786dd90502fcb8879ff41cbcce55b961a95352aaa4c`). The ordered validation set includes all 16 staged paths and the validation plan. Its final comparison reports `acceptable: false`, with exactly the validation-plan path and `<index>` changed, and no untracked paths. This is the explicitly permitted Step 6 review-metadata exception, not a generic clean-state result. Attribution reports `attributable: true`; only that patch was staged with `git apply --cached`. The assessed tree is `32708897e9cf81050f140fb30f5a1850a33327c6`. No production/test repair, other tracked validation side effect or umbrella change occurred.

### Repair inventory for step 6 version-sources (exchange 1) (round 1)

Repairs made:

- `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md`: polishing-only; independent Step 6 round 1 assessment metadata.

Paths staged:

- `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md`

### Commit plan assessment for step 6 version-sources (exchange 1) (round 1)

Independently ran `commit-plan-check.bat --format json` once before assessment: `state=valid`, `ready=true`, no diagnostics, 16 staged paths. Ordered groups: (1) `feat(release): add the npm version adapter`, the 15 source/test/evidence paths; (2) `docs(version-sources): record step 6 validation`, the validation plan. Membership, dependency order and conventional subjects match the diff. Scanner, adapter, registration and evidence correctly ship together because the supported formats require their records. The reviewer metadata patch preserves group membership and subjects; `a.commit` remains accurate without amendment. The complete checker JSON is retained in the ignored round evidence.

### Findings and boundaries for step 6 version-sources (exchange 1) (round 1)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 6 version-sources (exchange 1) (round 1)

Consume this advisory commit-ready answer through the exchange and continue the requestor workflow to the human convergence gate. The reviewer has not authorized or performed any commit. No implementation rework is requested.

### Decision rationale for step 6 version-sources (exchange 1) (round 1)

All six readiness-floor results pass: exact identity and request tree; Step 6 completeness; green mandatory writer validation and sufficient static coverage; an attributable metadata-only reviewer patch; no unresolved finding or boundary work; and accurate `a.commit`. Recommend commit-ready. There is no substantive reviewer repair and no claim of reviewer-run coverage.

### Final reviewer decision for step 6 version-sources (exchange 1) (round 1)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-6-round-1 -->

## Round 1 by human - Step 6 - human-confirmation

- Recorded: 2026-11-10T17:23:43+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 6
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-1 -->

## Round 1 by requestor - Step 7

- Recorded: 2026-11-10T18:13:22+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Implementation step: 7
- Outcome: request

### Review identity for step 7 version-sources (round 1)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.version-sources.md
Implementation step: 7
Review round: 1

### Code review evidence for step 7 version-sources (round 1)

request_index_tree: 2680926ba2ad1fa9b5144dd37d9b6594b2ee5627
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.version-sources.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(release): add the maven version adapter
group 1 path: tools/release_workflow/sources/xml_scan.py
group 1 path: tools/release_workflow/sources/maven_references.py
group 1 path: tools/release_workflow/sources/maven.py
group 1 path: tools/release_workflow/sources/__init__.py
group 1 path: tests/unit/tools/release_workflow/version_support.py
group 1 path: tests/unit/tools/release_workflow/test_version_formats/test_xml_scan_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_version_formats/test_version_formats_pbt.py
group 1 path: tests/unit/tools/release_workflow/test_maven_sources/__init__.py
group 1 path: tests/unit/tools/release_workflow/test_maven_sources/test_maven_sources_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_maven_sources/test_maven_references_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_version_registry/test_version_registry_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_version_transition/test_version_restoration_tdd.py
group 2: docs(version-sources): record step 7 validation
group 2 path: docs/v0.14.0/plan.v0.14.0.version-sources.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.version-sources.validation.md
staged path: tests/unit/tools/release_workflow/test_maven_sources/__init__.py
staged path: tests/unit/tools/release_workflow/test_maven_sources/test_maven_references_tdd.py
staged path: tests/unit/tools/release_workflow/test_maven_sources/test_maven_sources_tdd.py
staged path: tests/unit/tools/release_workflow/test_version_formats/test_version_formats_pbt.py
staged path: tests/unit/tools/release_workflow/test_version_formats/test_xml_scan_tdd.py
staged path: tests/unit/tools/release_workflow/test_version_registry/test_version_registry_tdd.py
staged path: tests/unit/tools/release_workflow/test_version_transition/test_version_restoration_tdd.py
staged path: tests/unit/tools/release_workflow/version_support.py
staged path: tools/release_workflow/sources/__init__.py
staged path: tools/release_workflow/sources/maven.py
staged path: tools/release_workflow/sources/maven_references.py
staged path: tools/release_workflow/sources/xml_scan.py
```

### Validation scope for step 7 version-sources (round 1)

Validation scope: the whole suite.

### Requestor assessment for step 7 version-sources (round 1)

Writer assessment for Step 7 of the version-sources plan, round 1: the step is
fully implemented, and its implementation check records
`Yes. Step 7 has been fully implemented.` in the staged validation plan.

Evidence, all on the staged tree:

- Tests first: `ghog single` on the new and changed leaves failed at
  collection (five errors, `ImportError: cannot import name 'maven'`, exit 4).
  After the implementation, the Step 7 leaves with the restoration, detection,
  settings, npm, Python and lock evidence leaves passed (311 tests, exit 0).
- `ghog day --whole-suite`, the command printed by `pw scope day`, exit 0. A
  first run failed only at check.bat (pyright on a `Literal`-keyed dict in the
  XML property test; ruff rewrapped three imports).
- Review validation, `ghog day --full=speed --whole-suite` (the built-in
  default; no `.review-validation`): exit 0 with `cov=100 outliers=0
  excluded=0 proof=speed`, on index tree
  `2680926ba2ad1fa9b5144dd37d9b6594b2ee5627`, first attempt. No budget was
  changed and no exclusion is accepted.
- `rg -n 'xml.etree' tools/release_workflow/sources` and
  `rg -n 'subprocess' tools/release_workflow/sources` find nothing; the
  registry test pins `("anchor", "python", "npm", "maven", "pattern")`. Every
  Python file stays below 650 lines.
- Markdown check and cSpell on the staged validation plan: no finding; one
  unknown word of my own wording was rephrased before staging.

Architecture: the scanner, the adapter and the reference rules are pure
domain code of the `sources` package (standard library `xml.parsers.expat`,
`sources.model` and the scanner only), reading through the `FileView`; the
dependency runs one way, from `maven` to `maven_references`, as plan decision
Q10 splits them. A component that is also a reactor module is refused by the
existing claim registry. Performance: each POM is parsed once, each module
visited once, dependencies resolved through dictionaries and a set of module
artifacts, and each inheritance chain resolved once. Feature integrity:
nothing ships until Step 9; registering `maven` adds reactor detection at
participating roots, and the earlier version tests pass unchanged.

Please check in particular: the scanner's span rule (first character data to
the end tag, whitespace trimmed on raw bytes) and its problem-instead-of-fail
choice; the reference rules against the design's "Maven reactors" section
and design decision Q12 (`${project.groupId}`, ambiguous groups, the two
supported sections); inheritance through internal parents and its failures;
and the readings listed in the writer response (plugins unread, required
internal parent version, `pair_edit` keyed by relative path).

### Implementation report for step 7 version-sources (round 1)

Step 7, "Maven reactor adapter", adds the expat scanner, the `maven` adapter
(reactor discovery) and its reference rules, completes the adapter registry
and the restoration matrix. Nothing ships yet: no handler calls the version
domain until Step 9.

XML scanner (`tools/release_workflow/sources/xml_scan.py`):

- `scan(content, name, wanted) -> PomDocument` checks strict UTF-8 with
  `decode_utf8`, then parses the bytes once with `xml.parsers.expat` (no
  namespace processing, so Maven's default namespace leaves names plain). A
  `_Scan` keeps a stack of `_Open` elements named by slash-joined paths; the
  first element is the document root.
- For each element whose path `wanted` fully matches, character data is
  collected and the first `CurrentByteIndex` remembered; at its end tag the
  span runs from there to the end tag's index, moved inward past XML
  whitespace (raw bytes, so CRLF and a byte-order mark keep offsets right).
  The value records the parent element's start offset, which groups one
  `<dependency>`'s fields.
- A comment, CDATA section, processing instruction or child element inside a
  wanted element, or span bytes that do not decode to the parsed text (an
  entity or character reference), become the value's `problem` instead of an
  immediate failure: the text stays readable for coordinates, and
  `XmlValue.owned(name)` refuses the span of such a field. The scanner cannot
  know which dependency versions are owned before the reactor index exists.
- A declared encoding other than UTF-8 (`XmlDeclHandler`), invalid UTF-8 and
  any `ExpatError` fail. `PomDocument.first` and `every` use a path index
  built once (`cached_property`).

Reactor discovery (`tools/release_workflow/sources/maven.py`):

- `MavenAdapter`: name `maven`, forms `{snapshot}`, default `snapshot`,
  candidate name `pom.xml`. `detect` reads the root's `pom.xml`; none gives
  nothing.
- `reactor` walks modules breadth first: each `<module>` is normalized against
  its declaring POM's directory (`os.path.normpath`, no disk access), as a POM
  file when it ends in `.xml`, otherwise the directory's `pom.xml`. A module
  declared twice (set of declared paths) or missing fails; any
  `project/profiles/profile/modules/module` fails as ambiguous; a root element
  other than `<project>` fails.
- Coordinates: literal `artifactId`, literal own or `<parent>` `groupId`; a
  property, an empty or missing value fails.
- The wanted paths: own and parent coordinates and version, modules (also in
  profiles), and `groupId`, `artifactId` and `version` of every `dependency`
  element at any depth. Plugins and `<properties>` are not read.

Reference rules (`tools/release_workflow/sources/maven_references.py`):

- `index` maps `(groupId, artifactId)` to `PomModule`; duplicates fail.
- `_Rules.own`: an own `<version>` is owned. When absent,
  `_check_inherited` follows internal parents until a module with its own
  version, remembering resolved modules in a set; an external parent, no
  parent or a loop fails with the remedy to declare a literal version.
- `_Rules.parent`: an internal parent (literal coordinates in the index) has
  its version owned and required; an external parent is skipped.
- `_Rules.dependencies`: `_dependencies` groups a document's dependency fields
  by parent offset in one pass. An entry is considered only when its
  `artifactId` is a module's (a set). Its group is literal or exactly
  `${project.groupId}` (the declaring module's group); then it is internal if
  the pair is in the index, otherwise external; any other group, or none,
  fails as ambiguous. An internal entry outside `project/dependencies` and
  `project/dependencyManagement/dependencies` fails (plan decision Q15). In
  those sections an absent version and exactly `${project.version}` stay;
  other versions are owned as `<section>/dependency[<group>:<artifact>]/version`
  (`#2` and on for repeated owned entries of one module).
- `_literal_version` refuses empty values, `${` expressions and ranges (any of
  `[](),`), naming the POM, field and expression. Every owned field takes
  `Form.SNAPSHOT` and its span from `XmlValue.owned`.

Registry, test support and tests:

- `sources/__init__.py`: `ADAPTERS = (anchor, python, npm, maven, pattern)`;
  `SUPPORT_MODULES` adds `xml_scan` and `maven_references`.
- `version_support.py`: `DEMO_GROUP`, `gav`, `pom_xml`, `reactor_poms`
  (my-project's shape); `pair_edit` now keys by path relative to the root; the
  `maven-reactor` (CRLF), `maven-inherited` (byte-order mark, four writes) and
  `combined` (five files, five writes) restoration sets.
- New: `test_version_formats/test_xml_scan_tdd.py`,
  `test_maven_sources/__init__.py`, `test_maven_sources/test_maven_sources_tdd.py`,
  `test_maven_sources/test_maven_references_tdd.py`. Extended: the formats
  property file (XML property), the registry test (final order) and the
  restoration test docstring (the new sets run through the existing matrix).

Writer notes: `.reviews/a.version-sources.step7.journal.md` and
`.reviews/a.version-sources.step7.handoff.md`.

### Change summary for step 7 version-sources (round 1)

Staged paths (13), grouped in the root `a.commit` (two groups, checker
`ready: true`):

1. `feat(release): add the maven version adapter`:
   `tools/release_workflow/sources/xml_scan.py`,
   `tools/release_workflow/sources/maven_references.py`,
   `tools/release_workflow/sources/maven.py`,
   `tools/release_workflow/sources/__init__.py`,
   `tests/unit/tools/release_workflow/version_support.py`,
   `tests/unit/tools/release_workflow/test_version_formats/test_xml_scan_tdd.py`,
   `tests/unit/tools/release_workflow/test_version_formats/test_version_formats_pbt.py`,
   `tests/unit/tools/release_workflow/test_maven_sources/__init__.py`,
   `tests/unit/tools/release_workflow/test_maven_sources/test_maven_sources_tdd.py`,
   `tests/unit/tools/release_workflow/test_maven_sources/test_maven_references_tdd.py`,
   `tests/unit/tools/release_workflow/test_version_registry/test_version_registry_tdd.py`,
   `tests/unit/tools/release_workflow/test_version_transition/test_version_restoration_tdd.py`.
2. `docs(version-sources): record step 7 validation`:
   `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md` (Step 7
   sections).

The scanner, the adapter, the reference rules and the registration share one
group: the registry test needs all three modules registered or declared
together, and the restoration matrix needs the adapter. Steps 1 to 6 are
committed and pushed (`a7c0d7c` to `b217b23`) and are not part of this review.

### Writer response for step 7 version-sources (round 1)

Writer response:

This is the first round of the Step 7 code review; there is no earlier
reviewer feedback to answer.

Choices worth checking, all recorded in the validation plan or the step notes:

- The scanner records markup inside a wanted element as a `problem` rather
  than failing at once. Only an owned field (`XmlValue.owned`) fails, so a
  comment inside an external dependency's version never breaks a POM. The
  plan wording "rejecting comments ... inside owned elements" is met at the
  point ownership is known.
- `scan(content, name, wanted)` takes a name for diagnostics beside the plan's
  `scan(content, wanted_paths)`, and `wanted` is a compiled expression, so
  `dependency` fields at any depth can be recorded without listing every
  Maven location.
- Only `dependency` elements are references. Plugin declarations are never
  read, as the design's "external parents, external dependencies, plugins and
  `<properties>` are never written" states; a reactor module used as a plugin
  is therefore outside the model. An internal dependency of a plugin or a
  profile fails (plan decision Q15).
- `${project.groupId}` resolves to the declaring module's own or inherited
  literal group; with that group the entry is internal only when the pair is
  a module, as for a literal group.
- An internal `<parent>` version is required and must be literal; an
  absent one fails rather than relying on Maven 4 inference.
- `pair_edit` now keys its result by path relative to the root (a reactor has
  several `pom.xml`); the uv and npm callers keep their keys because their
  files sit at the root.
- The restoration test gains no new code: the three new sets run through the
  existing parametrized matrix, so its +40 advisory was not needed.

### Reviewer focus for step 7 version-sources (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-7-round-1 -->

## Round 1 by reviewer - Step 7

- Recorded: 2026-11-10T18:24:32+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 7
- Outcome: answer

### Assessed index identity for step 7 version-sources (exchange 1) (round 1)

Baseline index tree: 2680926ba2ad1fa9b5144dd37d9b6594b2ee5627

Assessed index tree: e58cbc01159204836ed46504ecc35bb479b59e7d

### Implementation check for step 7 version-sources (exchange 1) (round 1)

Result:

No. Step 7 has NOT been fully implemented.

The expat scanner, Maven reference rules, registry order and restoration fixtures implement the ordinary reactor behavior. Physical module identity is missing at the discovery boundary, so the required component/reactor conflict can be bypassed through a junction alias. The implementation has a concrete missing path-policy and regression-test obligation. No other architecture or performance issue was identified.

Validation plan effects:

Updated only Step 7 in `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md`: exact No verdict, concrete missing-work section, and consistent architecture, coverage and integrity assessments. The attributable metadata patch was staged separately from the writer's existing staged changes. Other steps and the umbrella were untouched.

### Pre-repair mandatory checks and coverage for step 7 version-sources (exchange 1) (round 1)

No implementation repair was authorized or made; no literal Human guidance block was present. The writer's successful full speed walk ended 2026-11-10T18:12:24+01:00 with 6186 whole-suite tests, exit=0, cov=100, outliers=0, excluded=0, proof=speed and reused=none. Its check and 83-test affected phase were green, and the bound scope fingerprint matches the request. The reviewer relied on static code/test assessment and did not rerun tests or coverage. The measured source scope is `tools`, with tests and initializers omitted; the new test-support symbols are referenced. Green measured coverage does not cover the absent alias/boundary behaviors.

### Resolved validation set and sources for step 7 version-sources (exchange 1) (round 1)

Both the request and current resolver require `ghog day --full=speed --whole-suite`, source `project`. No declared `.review-validation` set exists. This command is writer-owned validation evidence and was not run by the reviewer.

### Resolver drift and direction for step 7 version-sources (exchange 1) (round 1)

None: the requested and current validation commands and sources match.

### Repository state around validation for step 7 version-sources (exchange 1) (round 1)

The baseline index matched the request tree `2680926ba2ad1fa9b5144dd37d9b6594b2ee5627`. After staging the attributable Step 7 metadata patch, the assessed tree is `e58cbc01159204836ed46504ecc35bb479b59e7d`. Umbrella digest comparison reports changed=false. Validation-state comparison reports acceptable=false for exactly the validation-plan path and `<index>`; this is the permitted reviewed-step metadata exception, not a validation side effect. All other tracked paths in the 13-path validation set are unchanged; no untracked path was introduced. Attribution reports attributable=true against the saved pre-edit blob.

### Repair inventory for step 7 version-sources (exchange 1) (round 1)

Repairs made:

- Review metadata only: corrected the Step 7 assessment and missing-work list in `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md`; no production or test repairs.

Paths staged:

- `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md` (reviewer-authored Step 7 metadata patch only)

### Commit plan assessment for step 7 version-sources (exchange 1) (round 1)

Independent canonical commit-plan checker: state=valid, ready=true, diagnostics empty, 13 staged paths. The unchanged a.commit remains accurate after the metadata patch. Ordered groups:

Group 1: feat(release): add the maven version adapter

- `tools/release_workflow/sources/xml_scan.py`
- `tools/release_workflow/sources/maven_references.py`
- `tools/release_workflow/sources/maven.py`
- `tools/release_workflow/sources/__init__.py`
- `tests/unit/tools/release_workflow/version_support.py`
- `tests/unit/tools/release_workflow/test_version_formats/test_xml_scan_tdd.py`
- `tests/unit/tools/release_workflow/test_version_formats/test_version_formats_pbt.py`
- `tests/unit/tools/release_workflow/test_maven_sources/__init__.py`
- `tests/unit/tools/release_workflow/test_maven_sources/test_maven_sources_tdd.py`
- `tests/unit/tools/release_workflow/test_maven_sources/test_maven_references_tdd.py`
- `tests/unit/tools/release_workflow/test_version_registry/test_version_registry_tdd.py`
- `tests/unit/tools/release_workflow/test_version_transition/test_version_restoration_tdd.py`

Group 2: docs(version-sources): record step 7 validation

- `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md`

### Findings and boundaries for step 7 version-sources (exchange 1) (round 1)

Unresolved findings:

- [P2] Authorize and canonicalize discovered module POMs before reads and claims — `tools/release_workflow/sources/maven.py:49-52,91-101`. `_module_path` uses only `normpath`, and `reactor` passes that lexical path through `FileView`, `PomModule` and `LocatedSource`. The claim registry keys `(source.path, source.field)` without resolving it. For a root reactor declaring `<module>alias</module>`, an in-project junction `alias -> real`, and a declared component rooted at `real` whose POM has a literal own version, the same physical project/version field is registered as both `alias/pom.xml` and `real/pom.xml`. The reactors' separate coordinate indexes do not detect that duplication, so detection accepts ownership that the design explicitly requires it to reject before writes. The same missing project path policy allows module discovery outside the physical project root or into a nested repository; downstream evidence or write authorization handles it too late. Apply the existing physical project path policy at module discovery, retain correct declaring-POM-relative resolution, and add alias/component conflict and project-boundary regression tests. This is a static finding; no implementation probe or test was run by the reviewer.

Boundary-crossing work: None.

### Writer instructions for step 7 version-sources (exchange 1) (round 1)

Implement the Step 7 missing-work list in the validation plan. Authorize discovered POMs against the overall physical project before reading or registering them, and use canonical physical identities for module/claim tracking. Preserve supported relative modules inside the project, including siblings of component roots. Add tests for aliased component/module conflicts, two module aliases, external paths, nested repository paths and linked boundary escapes, with rejection before mutation. Run the writer-owned validation set green, refresh Step 7 evidence, and publish a replacement review request.

### Decision rationale for step 7 version-sources (exchange 1) (round 1)

Changes requested. Identity passes; completeness fails on the physical module identity/path-policy finding. Writer validation is green and resolver drift is absent, but static test review identifies the missing path regressions. Staged attribution passes for the permitted Step 7 metadata exception, one finding remains unresolved, and the independent commit-plan assessment is mechanically ready. No substantive reviewer repairs were made. This assessment does not authorize a commit.

### Final reviewer decision for step 7 version-sources (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-7-round-1 -->

## Round 2 by requestor - Step 7

- Recorded: 2026-11-10T18:41:13+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 7
- Outcome: request

### Review identity for step 7 version-sources (round 2)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.version-sources.md
Implementation step: 7
Review round: 2

### Code review evidence for step 7 version-sources (round 2)

request_index_tree: cfe584ce8b5b8c3cdd6ba2ca6e549525b56bdc1f
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.version-sources.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(release): add the maven version adapter
group 1 path: tools/release_workflow/paths.py
group 1 path: tools/release_workflow/sources/model.py
group 1 path: tools/release_workflow/sources/settings.py
group 1 path: tools/release_workflow/sources/xml_scan.py
group 1 path: tools/release_workflow/sources/maven_references.py
group 1 path: tools/release_workflow/sources/maven.py
group 1 path: tools/release_workflow/sources/__init__.py
group 1 path: tests/unit/tools/release_workflow/version_support.py
group 1 path: tests/unit/tools/release_workflow/test_version_formats/test_xml_scan_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_version_formats/test_version_formats_pbt.py
group 1 path: tests/unit/tools/release_workflow/test_maven_sources/__init__.py
group 1 path: tests/unit/tools/release_workflow/test_maven_sources/test_maven_sources_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_maven_sources/test_maven_references_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_version_registry/test_version_registry_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_version_transition/test_version_restoration_tdd.py
group 2: docs(version-sources): record step 7 validation
group 2 path: docs/v0.14.0/plan.v0.14.0.version-sources.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.version-sources.validation.md
staged path: tests/unit/tools/release_workflow/test_maven_sources/__init__.py
staged path: tests/unit/tools/release_workflow/test_maven_sources/test_maven_references_tdd.py
staged path: tests/unit/tools/release_workflow/test_maven_sources/test_maven_sources_tdd.py
staged path: tests/unit/tools/release_workflow/test_version_formats/test_version_formats_pbt.py
staged path: tests/unit/tools/release_workflow/test_version_formats/test_xml_scan_tdd.py
staged path: tests/unit/tools/release_workflow/test_version_registry/test_version_registry_tdd.py
staged path: tests/unit/tools/release_workflow/test_version_transition/test_version_restoration_tdd.py
staged path: tests/unit/tools/release_workflow/version_support.py
staged path: tools/release_workflow/paths.py
staged path: tools/release_workflow/sources/__init__.py
staged path: tools/release_workflow/sources/maven.py
staged path: tools/release_workflow/sources/maven_references.py
staged path: tools/release_workflow/sources/model.py
staged path: tools/release_workflow/sources/settings.py
staged path: tools/release_workflow/sources/xml_scan.py
```

### Validation scope for step 7 version-sources (round 2)

Validation scope: the whole suite.

### Requestor assessment for step 7 version-sources (round 2)

Writer assessment for Step 7 of the version-sources plan, round 2: the step is
fully implemented after the round 1 repair, and the staged validation plan
records `Yes. Step 7 has been fully implemented.` again, with the reviewer's
round 1 assessment kept and the round 2 repair described.

Round 1 finding [P2], module POM paths only normalized lexically: repaired.
Every POM the Maven adapter reads, the root one included, goes through the
project's physical path policy first (`AdapterSettings.authorize`, backed by
`paths.authorize_in`, the body `authorize_path` already had), and the physical
path names the module, its sources and their claims.

Evidence, all on the staged tree:

- The six new path regressions in `test_maven_sources_tdd.py` run through
  `detection.detect` with `.release.ini` settings: the aliased component
  conflict is refused by `set_versions` as a field claimed twice, with no
  source or evidence write and the files unchanged; two links to one POM fail
  as one module declared twice; modules outside the project and in a nested
  repository, directly and through junctions, fail naming the declaring POM,
  the module and the policy's reason, with the files unchanged; a linked
  module and a component's `../shared` sibling stay supported under their
  physical paths.
- `ghog single` on the Maven, paths, managed-files, settings, detection,
  restoration, Python and npm leaves: exit 0 (304 tests). A first run failed in
  the fixture only (the memory filesystem keeps `.git` as a directory).
- Review validation, `ghog day --full=speed --whole-suite`: exit 0 with
  `cov=100 outliers=0 excluded=0 proof=speed`, on index tree
  `cfe584ce8b5b8c3cdd6ba2ca6e549525b56bdc1f` (ruff only sorted one import in
  `version_support.py` during the walk's check, restaged before this request).
  No budget was changed and no exclusion is accepted.
- `rg -n 'xml.etree' tools/release_workflow/sources` and
  `rg -n 'subprocess' tools/release_workflow/sources` still find nothing. Every
  Python file stays below 650 lines.
- Markdown check and cSpell on the staged validation plan and the transcript:
  no finding, after two polishing fixes in the transcript (a code span for the
  reviewer's `<index>`, and the removal of an unknown word I had quoted).
- `commit-plan-check`: ready, two groups, 16 paths; `paths.py`, `model.py`
  and `settings.py` joined the feature group.

Architecture: the domain reaches the path policy only through the
`AdapterSettings.authorize` port; the policy itself stays in `paths.py`, once.
Performance: one authorization per discovered POM, a fixed number of
filesystem probes on its ancestors, no tree scan. Feature integrity:
`authorize_path` behaves as before.

Please check in particular: whether authorizing the root POM as well as the
modules is the right boundary, the wording of the refusal, the six
regressions against your round 1 instructions, and the validation-plan
treatment of your round 1 metadata.

### Implementation report for step 7 version-sources (round 2)

Step 7, "Maven reactor adapter", adds the expat scanner, the `maven` adapter
(reactor discovery) and its reference rules, completes the adapter registry
and the restoration matrix. Nothing ships yet: no handler calls the version
domain until Step 9.

XML scanner (`tools/release_workflow/sources/xml_scan.py`):

- `scan(content, name, wanted) -> PomDocument` checks strict UTF-8 with
  `decode_utf8`, then parses the bytes once with `xml.parsers.expat` (no
  namespace processing, so Maven's default namespace leaves names plain). A
  `_Scan` keeps a stack of `_Open` elements named by slash-joined paths; the
  first element is the document root.
- For each element whose path `wanted` fully matches, character data is
  collected and the first `CurrentByteIndex` remembered; at its end tag the
  span runs from there to the end tag's index, moved inward past XML
  whitespace (raw bytes, so CRLF and a byte-order mark keep offsets right).
  The value records the parent element's start offset, which groups one
  `<dependency>`'s fields.
- A comment, CDATA section, processing instruction or child element inside a
  wanted element, or span bytes that do not decode to the parsed text (an
  entity or character reference), become the value's `problem` instead of an
  immediate failure: the text stays readable for coordinates, and
  `XmlValue.owned(name)` refuses the span of such a field. The scanner cannot
  know which dependency versions are owned before the reactor index exists.
- A declared encoding other than UTF-8 (`XmlDeclHandler`), invalid UTF-8 and
  any `ExpatError` fail. `PomDocument.first` and `every` use a path index
  built once (`cached_property`).

Reactor discovery (`tools/release_workflow/sources/maven.py`):

- `MavenAdapter`: name `maven`, forms `{snapshot}`, default `snapshot`,
  candidate name `pom.xml`. `detect` reads the root's `pom.xml`; none gives
  nothing.
- `reactor` walks modules breadth first: each `<module>` is normalized against
  its declaring POM's directory (`os.path.normpath`), as a POM file when it
  ends in `.xml`, otherwise the directory's `pom.xml`. Round 2: that path then
  goes through `settings.authorize` (the project's physical path policy) before
  it is read; a refusal names the declaring POM and the module, and the
  returned physical path identifies the module, its sources and claims.
  `detect` authorizes the root POM the same way. A module declared twice (set
  of declared physical paths, so two links to one POM collide) or missing
  fails; any `project/profiles/profile/modules/module` fails as ambiguous; a
  root element other than `<project>` fails.

Path policy seam (round 2):

- `tools/release_workflow/paths.py`: `authorize_in(root, supplied)` holds the
  existing check of existing ancestors and of the resolved path (escape,
  project Git metadata, nested repositories, non-directory ancestors);
  `authorize_path(identity, supplied)` delegates to it unchanged.
- `tools/release_workflow/sources/model.py`: `AdapterSettings.authorize(path)`.
- `tools/release_workflow/sources/settings.py`: `authorize_source(project_root,
  path)` wraps `authorize_in` and turns `ProjectPathError` into `SourceError`;
  `VersionSettings.authorize` uses it from the physical project root.
- `version_support.RootSettings.authorize` applies the same function.
- Coordinates: literal `artifactId`, literal own or `<parent>` `groupId`; a
  property, an empty or missing value fails.
- The wanted paths: own and parent coordinates and version, modules (also in
  profiles), and `groupId`, `artifactId` and `version` of every `dependency`
  element at any depth. Plugins and `<properties>` are not read.

Reference rules (`tools/release_workflow/sources/maven_references.py`):

- `index` maps `(groupId, artifactId)` to `PomModule`; duplicates fail.
- `_Rules.own`: an own `<version>` is owned. When absent,
  `_check_inherited` follows internal parents until a module with its own
  version, remembering resolved modules in a set; an external parent, no
  parent or a loop fails with the remedy to declare a literal version.
- `_Rules.parent`: an internal parent (literal coordinates in the index) has
  its version owned and required; an external parent is skipped.
- `_Rules.dependencies`: `_dependencies` groups a document's dependency fields
  by parent offset in one pass. An entry is considered only when its
  `artifactId` is a module's (a set). Its group is literal or exactly
  `${project.groupId}` (the declaring module's group); then it is internal if
  the pair is in the index, otherwise external; any other group, or none,
  fails as ambiguous. An internal entry outside `project/dependencies` and
  `project/dependencyManagement/dependencies` fails (plan decision Q15). In
  those sections an absent version and exactly `${project.version}` stay;
  other versions are owned as `<section>/dependency[<group>:<artifact>]/version`
  (`#2` and on for repeated owned entries of one module).
- `_literal_version` refuses empty values, `${` expressions and ranges (any of
  `[](),`), naming the POM, field and expression. Every owned field takes
  `Form.SNAPSHOT` and its span from `XmlValue.owned`.

Registry, test support and tests:

- `sources/__init__.py`: `ADAPTERS = (anchor, python, npm, maven, pattern)`;
  `SUPPORT_MODULES` adds `xml_scan` and `maven_references`.
- `version_support.py`: `DEMO_GROUP`, `gav`, `pom_xml`, `reactor_poms`
  (my-project's shape); `pair_edit` now keys by path relative to the root; the
  `maven-reactor` (CRLF), `maven-inherited` (byte-order mark, four writes) and
  `combined` (five files, five writes) restoration sets.
- New: `test_version_formats/test_xml_scan_tdd.py`,
  `test_maven_sources/__init__.py`, `test_maven_sources/test_maven_sources_tdd.py`
  (with the round 2 path-policy regressions),
  `test_maven_sources/test_maven_references_tdd.py`. Extended: the formats
  property file (XML property), the registry test (final order) and the
  restoration test docstring (the new sets run through the existing matrix).

Writer notes: `.reviews/a.version-sources.step7.journal.md` and
`.reviews/a.version-sources.step7.handoff.md`.

### Change summary for step 7 version-sources (round 2)

Round 2 changes since round 1 (all staged):

- `tools/release_workflow/paths.py`: `authorize_in(root, supplied)` holds the
  physical path policy; `authorize_path` delegates to it, docstring kept.
- `tools/release_workflow/sources/model.py`: `AdapterSettings.authorize(path)`
  port; module docstring.
- `tools/release_workflow/sources/settings.py`: `authorize_source` and
  `VersionSettings.authorize`; docstrings.
- `tools/release_workflow/sources/maven.py`: `_authorized`; `reactor` takes the
  settings and authorizes each module POM; `detect` authorizes the root POM;
  docstring.
- `tests/unit/tools/release_workflow/version_support.py`:
  `RootSettings.authorize`.
- `tests/unit/tools/release_workflow/test_maven_sources/test_maven_sources_tdd.py`:
  the six path-policy regressions and the `_modules` helper.
- `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md`: Step 7 back to
  Yes with the round 1 assessment kept and the round 2 repair recorded.

Staged paths (16), grouped in the root `a.commit` (two groups, checker
`ready: true`):

1. `feat(release): add the maven version adapter` (15 paths):
   `tools/release_workflow/paths.py`,
   `tools/release_workflow/sources/model.py`,
   `tools/release_workflow/sources/settings.py`,
   `tools/release_workflow/sources/xml_scan.py`,
   `tools/release_workflow/sources/maven_references.py`,
   `tools/release_workflow/sources/maven.py`,
   `tools/release_workflow/sources/__init__.py`,
   `tests/unit/tools/release_workflow/version_support.py`,
   `tests/unit/tools/release_workflow/test_version_formats/test_xml_scan_tdd.py`,
   `tests/unit/tools/release_workflow/test_version_formats/test_version_formats_pbt.py`,
   `tests/unit/tools/release_workflow/test_maven_sources/__init__.py`,
   `tests/unit/tools/release_workflow/test_maven_sources/test_maven_sources_tdd.py`,
   `tests/unit/tools/release_workflow/test_maven_sources/test_maven_references_tdd.py`,
   `tests/unit/tools/release_workflow/test_version_registry/test_version_registry_tdd.py`,
   `tests/unit/tools/release_workflow/test_version_transition/test_version_restoration_tdd.py`.
2. `docs(version-sources): record step 7 validation`:
   `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md`.

The review transcript stays unstaged for the residual commit.

### Writer response for step 7 version-sources (round 2)

Writer response:

Round 1 finding accepted and repaired; no disagreement.

- [P2] Authorize and canonicalize discovered module POMs before reads and
  claims: accepted. The Maven adapter now passes the root POM and every
  module POM through the project's physical path policy before reading it,
  and keeps the physical path for the module, its sources and their claims.
  - The policy is the existing one: `paths.authorize_in(root, supplied)` is
    the body `authorize_path(identity, supplied)` already had, which now
    delegates to it unchanged, so managed destinations and discovered POMs
    share one implementation.
  - Adapters reach it through a new port, `AdapterSettings.authorize(path)`.
    `VersionSettings.authorize` applies it from the physical project root
    through `settings.authorize_source`, which turns a `ProjectPathError` into
    a status 2 `SourceError`; `RootSettings` in test support does the same.
    The adapter imports no foundation path code.
  - Resolution stays relative to the declaring POM (`_module_path`), then
    authorization returns the physical path; modules elsewhere inside the
    project, such as a component's `../shared` module, stay supported.
  - Regressions, through `detection.detect` with `.release.ini` settings so
    `VersionSettings.authorize` runs: a module reached through an in-project
    junction that is also a declared component (refused by `set_versions` as
    a field claimed twice, with no source or evidence write and the files
    unchanged); two links to one module POM (declared twice); modules outside
    the project directly and through a junction, and inside a nested
    repository directly and through a junction (each refused with the files
    unchanged); and a supported linked module and component sibling, named by
    their physical paths.
- The reviewer's validation-plan metadata (No verdict and missing-work list)
  was the right record for round 1. After the repair, the Step 7 entry is back
  to `Yes`, the round 1 assessment is kept as its own paragraph, a writer
  round 2 paragraph describes the repair, and the completed missing-work
  section is removed, as the implementation-check instruction requires.
- `paths.py`, `sources/model.py` and `sources/settings.py` join the feature
  group of `a.commit` (outside the plan's Step 7 file list, recorded as
  variance in the validation plan).
- Transcript polishing only: the reviewer's bare `<index>` became a code span
  (MD033), and an unknown word quoted in my round 1 assessment was removed.

### Reviewer focus for step 7 version-sources (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-7-round-2 -->

## Round 2 by reviewer - Step 7

- Recorded: 2026-11-10T18:48:26+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 7
- Outcome: answer

### Assessed index identity for step 7 version-sources (exchange 1) (round 2)

Baseline index tree: cfe584ce8b5b8c3cdd6ba2ca6e549525b56bdc1f

Assessed index tree: 6f8935f035e0ede9d83eb8a8b0698b1791c58a43

### Implementation check for step 7 version-sources (exchange 1) (round 2)

Result:

Yes. Step 7 has been fully implemented.

The round 1 physical-path finding is resolved. Root and module POMs pass through the existing project authorization policy before reads and registration. Claims now use physical paths, so a linked reactor module and a separately configured component cannot silently claim the same field. The settings port preserves the adapter boundary and existing managed-path behavior.

The Maven reactor, references, namespace-aware span scanner, byte-preserving writes, and transactional conflict handling satisfy the named step. The new regressions cover alias/component conflicts before source or evidence writes, duplicate module aliases, external and nested-repository module refusals (direct and linked), valid linked modules, and sibling module paths.

Validation plan effects:

Updated only the Step 7 assessment in `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md`: recorded resolution of the earlier finding, the physical authorization boundary, architecture and performance assessment, and the writer's round 2 evidence. Kept the exact Yes result. No other step or umbrella status was edited.

### Pre-repair mandatory checks and coverage for step 7 version-sources (exchange 1) (round 2)

The writer's bound round 2 speed walk completed on 2026-11-10 at 18:40:00+01:00: check green; affected 717/6193 green; full 6193 tests green; exit=0, cov=100, outliers=0, excluded=0, proof=speed, reused=none. Its fingerprint `686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6` matches the bound round scope.

The reviewer assessed this evidence and source/tests statically. No reviewer test execution, coverage measurement, `ghog check`, or `ghog affected` was needed or performed. Added support symbols are exercised, and the tests cover the new path decisions without subprocess or native lifecycle overhead. No static coverage gap was found. Authorization cost is proportional to POM ancestor depth, with no repository scan or Git subprocess.

### Resolved validation set and sources for step 7 version-sources (exchange 1) (round 2)

Request-time and independently resolved current set agree:

- `ghog day --full=speed --whole-suite` (source: project; declared=false).

This is writer validation evidence; the reviewer did not rerun the command.

### Resolver drift and direction for step 7 version-sources (exchange 1) (round 2)

None. Request-time and current resolved commands and sources agree.

### Repository state around validation for step 7 version-sources (exchange 1) (round 2)

The request-time index and captured baseline agree at `cfe584ce8b5b8c3cdd6ba2ca6e549525b56bdc1f`. After the attributable Step 7 validation metadata patch was staged, the assessed tree is `6f8935f035e0ede9d83eb8a8b0698b1791c58a43`.

The final validation-state comparison reports `acceptable=false`, with tracked changes limited to the Step 7 validation file and `<index>`. This is the explicitly permitted reviewed-step metadata/index exception, not a validation side effect or an unconditional acceptable=true result. All other tracked validation paths are unchanged, and there are no new untracked paths. Attribution returned `attributable=true` before staging only the reviewer patch.

The applicable umbrella digest is unchanged: `5abf0cb72800e9d07acba786dd90502fcb8879ff41cbcce55b961a95352aaa4c` before and after.

### Repair inventory for step 7 version-sources (exchange 1) (round 2)

Repairs made:

- Review metadata only: recorded the Step 7 round 2 assessment and clarified architecture/performance evidence in `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md`; no production or test repairs.

Paths staged:

- `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md` (attributable reviewer metadata patch only).

### Commit plan assessment for step 7 version-sources (exchange 1) (round 2)

Independent `commit-plan-check.bat --format json` result: `state=valid`, `ready=true`; 16 staged paths; diagnostics empty. The check ran against the received state. The subsequent reviewer patch changes only the already-listed Step 7 validation file, so group membership and subjects remain accurate. `a.commit` was unchanged.

Group 1: `feat(release): add the maven version adapter`

- `tools/release_workflow/paths.py`
- `tools/release_workflow/sources/model.py`
- `tools/release_workflow/sources/settings.py`
- `tools/release_workflow/sources/xml_scan.py`
- `tools/release_workflow/sources/maven_references.py`
- `tools/release_workflow/sources/maven.py`
- `tools/release_workflow/sources/__init__.py`
- `tests/unit/tools/release_workflow/version_support.py`
- `tests/unit/tools/release_workflow/test_version_formats/test_xml_scan_tdd.py`
- `tests/unit/tools/release_workflow/test_version_formats/test_version_formats_pbt.py`
- `tests/unit/tools/release_workflow/test_maven_sources/__init__.py`
- `tests/unit/tools/release_workflow/test_maven_sources/test_maven_sources_tdd.py`
- `tests/unit/tools/release_workflow/test_maven_sources/test_maven_references_tdd.py`
- `tests/unit/tools/release_workflow/test_version_registry/test_version_registry_tdd.py`
- `tests/unit/tools/release_workflow/test_version_transition/test_version_restoration_tdd.py`

Group 2: `docs(version-sources): record step 7 validation`

- `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md`

### Findings and boundaries for step 7 version-sources (exchange 1) (round 2)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 7 version-sources (exchange 1) (round 2)

No implementation rework is requested. The existing requestor owns consumption of this answer and presentation of the human convergence gate. This advisory recommendation grants no commit authority; the human owns the Commit choice.

### Decision rationale for step 7 version-sources (exchange 1) (round 2)

Recommend `commit-ready` for Step 7, round 2, occurrence 1. All six readiness-floor assessments pass: exact identity and baseline, complete implementation, sufficient writer validation and static coverage evidence, attributable staged scope with the explicit Step 7 metadata exception, no unresolved current or carried findings, and an accurate independently checked commit plan. No substantive reviewer repair was made. The additional shared path-policy files are necessary for the writer's documented Step 7 repair and preserve existing behavior.

### Final reviewer decision for step 7 version-sources (exchange 1) (round 2)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-7-round-2 -->

## Round 2 by human - Step 7 - human-confirmation

- Recorded: 2026-11-10T19:14:16+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 7
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->

## Round 1 by requestor - Step 8

- Recorded: 2026-11-10T20:18:58+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Implementation step: 8
- Outcome: request

### Review identity for step 8 version-sources (round 1)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.version-sources.md
Implementation step: 8
Review round: 1

### Code review evidence for step 8 version-sources (round 1)

request_index_tree: 5e2a187477a360bd6a7bfb76b9cd220dfa04618a
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.version-sources.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(release): select release ranges from classified tags
group 1 path: tools/release_workflow/tags.py
group 1 path: tests/unit/tools/release_workflow/version_support.py
group 1 path: tests/unit/tools/release_workflow/test_release_tags/__init__.py
group 1 path: tests/unit/tools/release_workflow/test_release_tags/test_release_tags_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_release_tags/test_release_ranges_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_release_tags/test_release_tags_pbt.py
group 2: docs(version-sources): record step 8 validation
group 2 path: docs/v0.14.0/plan.v0.14.0.version-sources.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.version-sources.validation.md
staged path: tests/unit/tools/release_workflow/test_release_tags/__init__.py
staged path: tests/unit/tools/release_workflow/test_release_tags/test_release_ranges_tdd.py
staged path: tests/unit/tools/release_workflow/test_release_tags/test_release_tags_pbt.py
staged path: tests/unit/tools/release_workflow/test_release_tags/test_release_tags_tdd.py
staged path: tests/unit/tools/release_workflow/version_support.py
staged path: tools/release_workflow/tags.py
```

### Validation scope for step 8 version-sources (round 1)

Validation scope: the whole suite.

### Requestor assessment for step 8 version-sources (round 1)

Writer assessment for Step 8 of the version-sources plan, round 1: the step is
fully implemented, and its implementation check records
`Yes. Step 8 has been fully implemented.` in the staged validation plan.

Evidence, all on the staged tree:

- Tests first: `ghog single` on `test_release_tags` failed at collection
  (three errors, `ImportError: cannot import name 'tags'`, exit 4). After the
  implementation, `test_release_tags` and `test_git` passed (152 tests).
- Every selection test asserts its recorded Git calls against the plan's
  call table: no call for a refused target name; records only for a missing
  target, a conflict, an ineligible or ambiguous target boundary and an
  oversized tips query; records and count without a candidate; records,
  tags between and count for one candidate; records, tips, tags between and
  count for several. The release-version rule always records two calls.
- The aliased-boundary cases of design decisions Q18 and Q19 listed in the
  plan are written and pass, as do every AC13, AC14 and AC15 row of the
  design and the three consumer-shaped histories.
- `ghog day --whole-suite`, the command printed by `pw scope day`, exit 0. A
  first run failed only at check.bat: typings in two test files, PLR0913 on
  one parametrized test, and radon grade C on `eligibility`, `boundaries`,
  `check_release_version` and the test's reference predicate, each split
  into helpers.
- Review validation, `ghog day --full=speed --whole-suite` (the built-in
  default; no `.review-validation`): exit 0 with `cov=100 outliers=0
  excluded=0 proof=speed`, on index tree
  `5e2a187477a360bd6a7bfb76b9cd220dfa04618a`, first attempt. No budget was
  changed and no exclusion is accepted.
- `rg -n 'describe' tools/release_workflow/tags.py` finds nothing; every
  Python file stays below 650 lines (`tags.py` 342).
- Markdown check and cSpell on the staged validation plan: clean, after one
  MD038 fix in my own text (a code span with a trailing space, now written
  with the plan's `[space]` token).

Architecture: `tags.py` is release-domain code that reads Git only through
the Step 1 typed observations and the token grammar of `sources.model`; it
starts no process of its own and holds no state. Performance: dictionaries
and sets keyed by version, commit and name make each selection linear in the
reachable tags, with at most four Git calls (two for the rule). Feature
integrity: nothing calls it yet; Step 9 adds `versions range`, and the
existing readers keep their query until item 7.

Please check in particular: the trailer and `[valid]` line rules against
design decision Q01 and the eligibility table; the boundary class and name
(Q18, Q19); the seven steps and the call table, including my reading of the
no-candidate case; and the release-version rule's two calls and its bound.

### Implementation report for step 8 version-sources (round 1)

Step 8, "Tag classification, range selection and the release-version rule",
adds `tools/release_workflow/tags.py`: the one classifier, range selector and
release-version rule every range reader will share. Nothing calls it yet:
Step 9 adds `versions range`, and item 7 switches the existing readers.

Names and eligibility:

- `parse_name(name)`: one regular expression, `v?` then the token grammar's
  three numbers (no leading zeros), then an optional `-SNAPSHOT` matched case
  insensitively. With the suffix it is a `SnapshotName`, without a
  `StableName`; anything else, other prereleases included, is `None`.
- `eligibility(annotation)`: `None` (a lightweight tag) and an annotation
  without a trailer line are `HISTORICAL`. Lines are the nonblank lines of
  `splitlines()` (so CRLF and trailing blank lines do not matter). A trailer
  line starts with exactly `Release tooling:[space]` and has a value that is not
  blank; `[valid]` must equal the whole line. `_engine` then requires one
  trailer, no `[valid]` before it, and after it nothing (`UNVALIDATED`) or
  exactly `[valid]` (`VALIDATED`); anything else is `AMBIGUOUS`.
- `classify(record)` returns `ClassifiedTag(record, name, eligibility)` for a
  stable name and `None` otherwise, so callers drop snapshot markers and
  other tags in one pass (the plan's signature reads `-> ClassifiedTag`).

Boundaries:

- `boundaries(tags)` fills two dictionaries in one pass, by version key and
  by commit, then `_one_commit_per_version` and `_one_version_per_commit`
  refuse a version on several commits or a commit with several versions,
  naming the tags, before anything is excluded.
- `Boundary(version, commit, aliases)`: `status` (`BoundaryClass`) is
  ambiguous when any alias is, otherwise ineligible when any alias is
  unvalidated, otherwise eligible (design decision Q18); `name` is the
  `vX.Y.Z` alias when present, otherwise the first `X.Y.Z` alias (Q19);
  `spelled` joins the sorted alias names for diagnostics.

Range selection, `select_range(git, *, cwd, target=None) -> RangeSelection`:

1. `_target`: HEAD, or a stable name as `refs/tags/<name>`; anything else is
   a `RangeError` before any call.
2. `_boundaries`: one `tag_records(merged=revision)` call;
   `GitRevisionNotFoundError` becomes `RangeError` ("tag X does not exist")
   chained from it; other Git errors propagate (status 1).
3. Grouping as above.
4. `_without_target`: a tag target's boundary must be eligible (ambiguous or
   not eligible fails naming the aliases) and is removed whole; HEAD keeps
   every boundary, so a release on HEAD stays a candidate.
5. `_baseline`: one candidate is the baseline; several go through one
   `independent_commits` call (its command-line guard raises
   `GitCommandLineTooLongError` first), and anything but one tip, or a
   candidate of a higher version than the tip, fails.
6. `_checked` with one `tag_names(merged=revision, not_merged=refs/tags/<baseline>)`
   call: an ambiguous boundary among those names fails naming its aliases,
   an ineligible one gives a warning naming them.
7. Without a candidate, `_checked` runs over every remaining boundary ("before
   the target") and the range is the target alone, counted by
   `commit_count(revision)`; otherwise `commit_count(refs/tags/<baseline>..revision)`
   and the printed range `<baseline>..<target>` with plain names.

Release-version rule, `check_release_version(git, *, cwd, version)`:
`VersionToken.parse` (status 2 `VersionError`) and a snapshot refusal come
first, then exactly two calls, `tag_records()` and `tag_records(merged="main")`.
A version any stable tag names is reserved; otherwise it must be above the
highest eligible boundary on `main`, grouped by `boundaries`.

Tests and support: `version_support` gains `ENGINE_TRAILER`, `annotation`,
`chain` and `tagged_history`. `test_release_tags/` holds the classification
tests, the selection and rule tests on declared histories (every selection
asserts its recorded calls against the plan's call table, including the
600-candidate command-line case), and the properties.

Writer notes: `.reviews/a.version-sources.step8.journal.md` and
`.reviews/a.version-sources.step8.handoff.md`.

### Change summary for step 8 version-sources (round 1)

Staged paths (7), grouped in the root `a.commit` (two groups, checker
`ready: true`):

1. `feat(release): select release ranges from classified tags`:
   `tools/release_workflow/tags.py`,
   `tests/unit/tools/release_workflow/version_support.py`,
   `tests/unit/tools/release_workflow/test_release_tags/__init__.py`,
   `tests/unit/tools/release_workflow/test_release_tags/test_release_tags_tdd.py`,
   `tests/unit/tools/release_workflow/test_release_tags/test_release_ranges_tdd.py`,
   `tests/unit/tools/release_workflow/test_release_tags/test_release_tags_pbt.py`.
2. `docs(version-sources): record step 8 validation`:
   `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md` (Step 8
   sections).

Steps 1 to 7 are committed and pushed (`a7c0d7c` to `3bdd5ec`) and are not
part of this review.

### Writer response for step 8 version-sources (round 1)

Writer response:

This is the first round of the Step 8 code review; there is no earlier
reviewer feedback to answer.

Choices worth checking, all recorded in the validation plan or the step notes:

- `classify` returns `None` for names that are not stable releases; the plan
  wrote `-> ClassifiedTag`.
- A missing tag target is reported as `RangeError` (status 2, "tag X does not
  exist") chained from the `GitRevisionNotFoundError` the one records call
  raises, rather than the raw Git error; the status is the same and the
  message names the tag.
- Without a candidate, the remaining boundaries are still checked as step 6
  does after a baseline: an ambiguous one fails, an unvalidated one is
  warned about ("before" the target), from the records already read, so no
  extra call is made. The design's step 7 says only that the range is the
  full history; failing on an ambiguous release inside that history follows
  the same rule as inside a baselined range.
- Ambiguous or unvalidated boundaries that are ancestors of the baseline are
  neither warned about nor fatal: step 6 classifies only the tags between the
  baseline and the target.
- A trailer value must not be blank (`Release tooling:` followed by spaces is
  no trailer), and `[valid]` must match the whole line (`[valid]` with a
  trailing space after the trailer makes the tag ambiguous).
- The release-version rule always makes both calls before deciding, so its
  call count is fixed at two; it refuses a malformed or snapshot version
  before any call. The `main` branch name is fixed, as the design states.

### Reviewer focus for step 8 version-sources (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-8-round-1 -->

## Round 1 by reviewer - Step 8

- Recorded: 2026-11-10T20:30:58+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 8
- Outcome: answer

### Assessed index identity for step 8 version-sources (exchange 1) (round 1)

Baseline index tree: 5e2a187477a360bd6a7bfb76b9cd220dfa04618a

Assessed index tree: 0ab463d15f46a415d65f0b554a1d7b5bcc3dff64

### Implementation check for step 8 version-sources (exchange 1) (round 1)

Result:

No. Step 8 has NOT been fully implemented.

The staged domain implementation matches the name grammar, whole-line annotation rules, restrictive alias boundaries, ancestry selection and release-version rule. Static review found no production defect, architecture violation, or impaired existing reader. The documented no-candidate ambiguity check is consistent with refusing ambiguous releases inside a selected history; widening `classify` to return `None` for nonstable tags is appropriate.

The explicit completion criterion at `plan.v0.14.0.version-sources.md:1811` is not met: several selection tests do not assert their complete recorded Git-call sequence. See finding R1. File sizes remain below 650 lines. Normal classification/grouping is linear; sorting a conflicting group's diagnostic can cost `O(k log k)`. Static source and branch review supports the writer's coverage evidence for `tools`; test helpers and initializers are outside the gate and their added symbols are referenced.

Validation plan effects:

Updated only Step 8 in `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md`. The exact verdict is No; `Missing work for Step 8` lists the unasserted call contracts. Corrected the universal call-assertion claim and distinguished linear normal execution from diagnostic sorting. The umbrella and other steps were not edited.

### Pre-repair mandatory checks and coverage for step 8 version-sources (exchange 1) (round 1)

Writer evidence on request tree `5e2a187477a360bd6a7bfb76b9cd220dfa04618a`: `ghog day --full=speed --whole-suite` ended 2026-11-10 at 20:13:50 +01:00 with `exit=0 cov=100 outliers=0 excluded=0 proof=speed`, 6284 tests; no budget or exclusion changes. The retained speed log agrees with the request. The round's core-owned whole-suite scope has fingerprint `686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6`.

The reviewer ran no tests, coverage command, `ghog day` or `ghog full`. Static review establishes the missing assertions directly; additional execution would not resolve that omission. No production or test repair was made.

### Resolved validation set and sources for step 8 version-sources (exchange 1) (round 1)

The current resolver reports `declared=false` and one command: `ghog day --full=speed --whole-suite`, source `project`. This exactly matches the request's resolved validation set. Resolution used the current canonical validation resolver without executing that command.

### Resolver drift and direction for step 8 version-sources (exchange 1) (round 1)

None. Request and current command, scope and source agree.

### Repository state around validation for step 8 version-sources (exchange 1) (round 1)

Request/baseline tree: `5e2a187477a360bd6a7bfb76b9cd220dfa04618a`. Retained manifest reread and live tree matched before continuing assessment. Assessed tree after staging reviewer metadata: `0ab463d15f46a415d65f0b554a1d7b5bcc3dff64`.

The identical ordered seven-path validation set was captured before and after. Canonical comparison returned `acceptable=false`, with tracked differences only at the validation plan and `<index>`; there are no ignored or untracked differences. Inspection of the attributable patch confirms these are the permitted reviewed-Step-8 metadata exception, not a validation side effect. All six implementation/test paths retain their original digests. The applicable umbrella digest remained `5abf0cb72800e9d07acba786dd90502fcb8879ff41cbcce55b961a95352aaa4c` (`changed=false`).

The evidence launcher proved the metadata patch attributable to the pre-edit blob `c6f18022657479271dd803620532f4e2e607ee6b`; only that patch was staged.

### Repair inventory for step 8 version-sources (exchange 1) (round 1)

Repairs made:

- Review metadata only, polishing: corrected the Step 8 validation verdict, recorded missing call assertions and clarified complexity. No substantive repair; no implementation or test changes.

Paths staged:

- `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md` (reviewer-authored Step 8 metadata patch only).

### Commit plan assessment for step 8 version-sources (exchange 1) (round 1)

Independent checker: `state=valid`, `ready=true`, seven staged paths, no diagnostics. Its ordered groups are:

1. `feat(release): select release ranges from classified tags` — `tools/release_workflow/tags.py`, `tests/unit/tools/release_workflow/version_support.py`, and `test_release_tags/{__init__.py,test_release_tags_tdd.py,test_release_ranges_tdd.py,test_release_tags_pbt.py}` under `tests/unit/tools/release_workflow/`.
2. `docs(version-sources): record step 8 validation` — the exact validation plan.

Membership, dependency order, conventional subjects and scope remain accurate after the metadata-only patch. `a.commit` was not changed. Mechanical readiness does not establish implementation completeness or authorize committing.

### Findings and boundaries for step 8 version-sources (exchange 1) (round 1)

Unresolved findings:

- R1 (medium, test completeness): `tests/unit/tools/release_workflow/test_release_tags/test_release_ranges_tdd.py:232` and other cases omit the full Git-call assertion required explicitly by `docs/v0.14.0/plan.v0.14.0.version-sources.md:1811`. The ambiguous aliased boundary and ambiguous target discard the history; the eligible aliased baseline checks only the last count call. All three consumer-shaped tests omit call checks for their multiple selections. The canned failure does not record/assert the attempted query. `test_release_tags_pbt.py:75` likewise makes generated selections without asserting the call sequence. The boundary-class and no-eligible release-version tests also omit their required two-call checks. Extra or repeated observations could therefore pass these cases, despite the request and validation plan claiming every selection checks them. Add complete ordered call assertions per invocation (including generated zero/one/several-candidate branches and recorded failure), assert the two records calls in those rule tests, then refresh validation evidence. This is an unmet explicit test contract, not an observed production bug.

Boundary-crossing work: None.

### Writer instructions for step 8 version-sources (exchange 1) (round 1)

Complete R1 using the exact `Missing work for Step 8` list. Assert the public observation sequence, count and ordering from the plan's call table; use existing recorded histories and keep generated cases bounded. For tests with several selections/rule calls, assert each call segment separately. Record the failed query in the canned failure test rather than asserting an empty recorder.

Rerun the writer-owned validation for the changed tests, update Step 8's validation evidence truthfully, verify `a.commit`, and publish the replacement request. The request contains no literal `Human guidance:` block authorizing reviewer code/test repairs; its generic repair boilerplate was not treated as such authorization.

### Decision rationale for step 8 version-sources (exchange 1) (round 1)

Changes requested. Readiness floor: identity passes; implementation completeness fails R1; writer validation/coverage evidence and static coverage assessment pass for the measured scope; staged attribution passes with the documented Step 8 metadata exception; absence of unresolved findings fails R1; commit-plan accuracy passes. No substantive reviewer repair occurred. A green suite cannot substitute for the plan's missing call assertions. The recommendation is advisory and grants no commit or convergence authority.

### Final reviewer decision for step 8 version-sources (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-8-round-1 -->

## Round 2 by requestor - Step 8

- Recorded: 2026-11-10T20:55:25+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 8
- Outcome: request

### Review identity for step 8 version-sources (round 2)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.version-sources.md
Implementation step: 8
Review round: 2

### Code review evidence for step 8 version-sources (round 2)

request_index_tree: ef91da8f835d41a40a16cbfab878bbc63ccaed74
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.version-sources.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(release): select release ranges from classified tags
group 1 path: tools/release_workflow/tags.py
group 1 path: tests/unit/tools/release_workflow/version_support.py
group 1 path: tests/unit/tools/release_workflow/test_release_tags/__init__.py
group 1 path: tests/unit/tools/release_workflow/test_release_tags/test_release_tags_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_release_tags/test_release_ranges_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_release_tags/test_release_tags_pbt.py
group 2: docs(version-sources): record step 8 validation
group 2 path: docs/v0.14.0/plan.v0.14.0.version-sources.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.version-sources.validation.md
staged path: tests/unit/tools/release_workflow/test_release_tags/__init__.py
staged path: tests/unit/tools/release_workflow/test_release_tags/test_release_ranges_tdd.py
staged path: tests/unit/tools/release_workflow/test_release_tags/test_release_tags_pbt.py
staged path: tests/unit/tools/release_workflow/test_release_tags/test_release_tags_tdd.py
staged path: tests/unit/tools/release_workflow/version_support.py
staged path: tools/release_workflow/tags.py
```

### Validation scope for step 8 version-sources (round 2)

Validation scope: the whole suite.

### Requestor assessment for step 8 version-sources (round 2)

Writer assessment for Step 8 of the version-sources plan, round 2: the step is
fully implemented after the round 1 repair, and the staged validation plan
records `Yes. Step 8 has been fully implemented.` again, with the reviewer's
round 1 assessment kept and the round 2 repair described.

Round 1 finding R1, incomplete recorded-call assertions: repaired in the
tests only; `tools/release_workflow/tags.py` is unchanged. Every case listed
in the round 1 missing-work section now asserts its complete ordered calls,
arguments included, one invocation at a time, and the property test asserts
the call-table sequence of every generated selection.

Evidence, all on the staged tree:

- `ghog single` on `test_release_tags`: exit 0 (91 tests) with the new
  assertions.
- Review validation, `ghog day --full=speed --whole-suite`: exit 0 with
  `cov=100 outliers=0 excluded=0 proof=speed`, on index tree
  `ef91da8f835d41a40a16cbfab878bbc63ccaed74`. The first attempt passed check
  and the affected tests, then failed on one wall-only lifecycle overrun at
  the teardown of
  `tests/unit/tools/test_groundhog_no_machine_queue.py::test_groundhog_source_takes_no_cross_process_lock`
  (1.07 s wall against 1 s, CPU 0.09 s within its band; unrelated to this
  step). It passed in focus, and the restarted walk was green. No budget was
  changed and no exclusion is accepted.
- Markdown check and cSpell on the staged validation plan and the
  transcript: clean, after polishing my own round 1 text in the transcript
  (a `[space]` token for a code span ending in a space, and two bare
  `<target>` placeholders reworded).
- `commit-plan-check`: ready, two groups, 7 paths, unchanged membership.

Please check in particular that the new assertions match the call table for
each case, including the candidate lists of the independent-tips calls in
the consumer-shaped histories, and the validation-plan treatment of your
round 1 metadata.

### Implementation report for step 8 version-sources (round 2)

Step 8, "Tag classification, range selection and the release-version rule",
adds `tools/release_workflow/tags.py`: the one classifier, range selector and
release-version rule every range reader will share. Nothing calls it yet:
Step 9 adds `versions range`, and item 7 switches the existing readers.

Names and eligibility:

- `parse_name(name)`: one regular expression, `v?` then the token grammar's
  three numbers (no leading zeros), then an optional `-SNAPSHOT` matched case
  insensitively. With the suffix it is a `SnapshotName`, without a
  `StableName`; anything else, other prereleases included, is `None`.
- `eligibility(annotation)`: `None` (a lightweight tag) and an annotation
  without a trailer line are `HISTORICAL`. Lines are the nonblank lines of
  `splitlines()` (so CRLF and trailing blank lines do not matter). A trailer
  line starts with exactly `Release tooling:[space]` and has a value that is not
  blank; `[valid]` must equal the whole line. `_engine` then requires one
  trailer, no `[valid]` before it, and after it nothing (`UNVALIDATED`) or
  exactly `[valid]` (`VALIDATED`); anything else is `AMBIGUOUS`.
- `classify(record)` returns `ClassifiedTag(record, name, eligibility)` for a
  stable name and `None` otherwise, so callers drop snapshot markers and
  other tags in one pass (the plan's signature reads `-> ClassifiedTag`).

Boundaries:

- `boundaries(tags)` fills two dictionaries in one pass, by version key and
  by commit, then `_one_commit_per_version` and `_one_version_per_commit`
  refuse a version on several commits or a commit with several versions,
  naming the tags, before anything is excluded.
- `Boundary(version, commit, aliases)`: `status` (`BoundaryClass`) is
  ambiguous when any alias is, otherwise ineligible when any alias is
  unvalidated, otherwise eligible (design decision Q18); `name` is the
  `vX.Y.Z` alias when present, otherwise the first `X.Y.Z` alias (Q19);
  `spelled` joins the sorted alias names for diagnostics.

Range selection, `select_range(git, *, cwd, target=None) -> RangeSelection`:

1. `_target`: HEAD, or a stable name as `refs/tags/<name>`; anything else is
   a `RangeError` before any call.
2. `_boundaries`: one `tag_records(merged=revision)` call;
   `GitRevisionNotFoundError` becomes `RangeError` ("tag X does not exist")
   chained from it; other Git errors propagate (status 1).
3. Grouping as above.
4. `_without_target`: a tag target's boundary must be eligible (ambiguous or
   not eligible fails naming the aliases) and is removed whole; HEAD keeps
   every boundary, so a release on HEAD stays a candidate.
5. `_baseline`: one candidate is the baseline; several go through one
   `independent_commits` call (its command-line guard raises
   `GitCommandLineTooLongError` first), and anything but one tip, or a
   candidate of a higher version than the tip, fails.
6. `_checked` with one `tag_names(merged=revision, not_merged=refs/tags/<baseline>)`
   call: an ambiguous boundary among those names fails naming its aliases,
   an ineligible one gives a warning naming them.
7. Without a candidate, `_checked` runs over every remaining boundary (before
   the target) and the range is the target alone, counted by
   `commit_count(revision)`; otherwise `commit_count(refs/tags/<baseline>..revision)`
   and the printed range `<baseline>..<target>` with plain names.

Release-version rule, `check_release_version(git, *, cwd, version)`:
`VersionToken.parse` (status 2 `VersionError`) and a snapshot refusal come
first, then exactly two calls, `tag_records()` and `tag_records(merged="main")`.
A version any stable tag names is reserved; otherwise it must be above the
highest eligible boundary on `main`, grouped by `boundaries`.

Tests and support (round 2: complete ordered call assertions per invocation, see the writer response): `version_support` gains `ENGINE_TRAILER`, `annotation`,
`chain` and `tagged_history`. `test_release_tags/` holds the classification
tests, the selection and rule tests on declared histories (every selection
asserts its recorded calls against the plan's call table, including the
600-candidate command-line case), and the properties.

Writer notes: `.reviews/a.version-sources.step8.journal.md` and
`.reviews/a.version-sources.step8.handoff.md`.

### Change summary for step 8 version-sources (round 2)

Round 2 changes since round 1 (all staged):

- `tests/unit/tools/release_workflow/test_release_tags/test_release_ranges_tdd.py`:
  `_take` and `_selection_calls` helpers; complete ordered call assertions in
  the ambiguous aliased boundary, eligible aliased baseline, ambiguous target,
  canned failure (which now records its query), consumer-shaped histories and
  both release-version cases; docstring.
- `tests/unit/tools/release_workflow/test_release_tags/test_release_tags_pbt.py`:
  the call sequence of every generated selection; docstring.
- `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md`: Step 8 back to
  Yes with the round 1 assessment kept and the round 2 repair recorded.

`tools/release_workflow/tags.py` and `version_support.py` are unchanged since
round 1.

Staged paths (7), grouped in the root `a.commit` (two groups, checker
`ready: true`):

1. `feat(release): select release ranges from classified tags`:
   `tools/release_workflow/tags.py`,
   `tests/unit/tools/release_workflow/version_support.py`,
   `tests/unit/tools/release_workflow/test_release_tags/__init__.py`,
   `tests/unit/tools/release_workflow/test_release_tags/test_release_tags_tdd.py`,
   `tests/unit/tools/release_workflow/test_release_tags/test_release_ranges_tdd.py`,
   `tests/unit/tools/release_workflow/test_release_tags/test_release_tags_pbt.py`.
2. `docs(version-sources): record step 8 validation`:
   `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md`.

The review transcript stays unstaged for the residual commit.

### Writer response for step 8 version-sources (round 2)

Writer response:

Round 1 finding accepted and repaired; no disagreement.

- R1 (medium, test completeness): accepted. Every case you listed now
  asserts its complete ordered calls, arguments included:
  - `_take(history)` returns and clears the calls of one invocation, so tests
    that select or check several times assert each invocation alone;
    `_selection_calls(revision, candidates, baseline)` builds the call
    table's sequence for a selection with a baseline (records, tips only for
    several candidates, tags between, count).
  - The ambiguous aliased boundary asserts records then tags between; the
    eligible aliased baseline its three calls; the ambiguous target its one
    records call.
  - The canned records failure now records the attempted
    `("tag_records", "HEAD")` before raising, and the test asserts it.
  - The three consumer-shaped histories assert every selection's sequence,
    including the full candidate list of the independent-tips call (twelve,
    98 and five commits for HEAD; the earlier candidates for each tag
    target).
  - `test_the_bound_uses_boundary_classes` asserts the two records calls of
    each of its two invocations, and
    `test_without_an_eligible_release_any_target_passes` its two calls.
  - The property test asserts, for every generated selection, records and
    count without a candidate (before its early return), and records, tips
    (several candidates only), tags between and count otherwise.
- The validation plan: your round 1 assessment is kept as its own paragraph,
  a writer round 2 paragraph records the repair, the completed missing-work
  section is removed, and your performance wording (`O(k log k)` only for a
  conflict's message) is kept as accurate.
- Transcript polishing only, in my own round 1 text: a code span with a
  trailing space now uses the plan's `[space]` token (MD038), and two bare
  `<target>` placeholders were reworded (MD033).
- No production change: `tools/release_workflow/tags.py` is the reviewed
  file, unchanged.

### Reviewer focus for step 8 version-sources (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-8-round-2 -->

## Round 2 by reviewer - Step 8

- Recorded: 2026-11-10T21:01:43+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 8
- Outcome: answer

### Assessed index identity for step 8 version-sources (exchange 1) (round 2)

Baseline index tree: ef91da8f835d41a40a16cbfab878bbc63ccaed74

Assessed index tree: 0fc042a04fc97abcd5d0fd598d6f0d09ce3b363f

### Implementation check for step 8 version-sources (exchange 1) (round 2)

Result:

Yes. Step 8 has been fully implemented.

R1 from round 1 is resolved. Each formerly unchecked selection now asserts its ordered observations. The canned failure records its attempted query; the aliased cases assert their complete sequences; each consumer-history selection checks its own segment, including independent-tip candidates; both rule cases assert their two records calls per invocation. The generated chain checks zero-candidate calls before its early return and checks one/several-candidate sequences otherwise. The candidate lists match the declared histories: twelve releases, 98 stable tags excluding the snapshot, and the five-release mixed-spelling chain, with the selected target removed.

The production classifier, restrictive alias boundaries, ancestry selection and release-version rule retain the reviewed round 1 digest. No production defect, architecture violation, performance issue or unit-coverage gap remains. Normal work is linear; conflict-message sorting can cost `O(k log k)`. Static assessment respects the gate's `tools` scope and its test/initializer omissions; added test helper symbols are referenced. Sizes remain below 650 lines. No existing reader is switched by this step.

Validation plan effects:

Retained the exact Yes verdict in `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md` and added an independent round 2 reassessment only within Step 8. The writer retained the historical round 1 finding, documented the repair and removed the completed missing-work list. No other step or umbrella row was edited by the reviewer.

### Pre-repair mandatory checks and coverage for step 8 version-sources (exchange 1) (round 2)

Writer evidence on request tree `ef91da8f835d41a40a16cbfab878bbc63ccaed74`: focused Step 8 tests passed (91 tests); `ghog day --full=speed --whole-suite` ended at 2026-11-10T20:53:49+01:00 with `exit=0 cov=100 outliers=0 excluded=0 proof=speed`, 6284 tests. The retained round 2 speed log agrees. The request discloses a preceding unrelated wall-only lifecycle overrun, its passing focused run, and the subsequent green walk; no budget or exclusion was changed.

The core-owned bound scope is whole-suite, fingerprint `686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6`. The reviewer ran no tests or coverage walk; static examination resolves the missing-assertion finding without repeating writer validation.

### Resolved validation set and sources for step 8 version-sources (exchange 1) (round 2)

The current resolver reports `declared=false` and one command: `ghog day --full=speed --whole-suite`, source `project`. This exactly matches the request's resolved validation set. Resolution used the current canonical validation resolver without executing that command.

### Resolver drift and direction for step 8 version-sources (exchange 1) (round 2)

None. Request and current command, scope and source agree.

### Repository state around validation for step 8 version-sources (exchange 1) (round 2)

The request and captured baseline index matched at `ef91da8f835d41a40a16cbfab878bbc63ccaed74`. Assessed tree after staging the reviewer metadata: `0fc042a04fc97abcd5d0fd598d6f0d09ce3b363f`.

Before/after captures use the same ordered seven staged Step 8 paths. Canonical comparison reports `acceptable=false` solely for the exact validation plan and `<index>`, with no ignored or untracked differences. The attributable patch contains only the round 2 Step 8 assessment, so these changes satisfy the permitted reviewed-step metadata exception. All six implementation/test paths retain their round 2 baseline digests. The umbrella digest remains `5abf0cb72800e9d07acba786dd90502fcb8879ff41cbcce55b961a95352aaa4c` (`changed=false`).

The evidence launcher proved attribution against validation blob `9ecb6a6315014c80d0ef7649a4645063caaf095d`; only that patch was staged. The retained manifest records the new assessed tree.

### Repair inventory for step 8 version-sources (exchange 1) (round 2)

Repairs made:

- Review metadata only, polishing: added the independent round 2 reassessment and R1 resolution to the exact Step 8 validation section. No substantive repair or implementation/test change.

Paths staged:

- `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md` (reviewer-authored Step 8 metadata patch only).

### Commit plan assessment for step 8 version-sources (exchange 1) (round 2)

Independent checker: `state=valid`, `ready=true`, seven staged paths, no diagnostics. Its ordered groups are:

1. `feat(release): select release ranges from classified tags` — `tools/release_workflow/tags.py`, `tests/unit/tools/release_workflow/version_support.py`, and `test_release_tags/{__init__.py,test_release_tags_tdd.py,test_release_ranges_tdd.py,test_release_tags_pbt.py}` under `tests/unit/tools/release_workflow/`.
2. `docs(version-sources): record step 8 validation` — the exact validation plan.

Membership, dependency order, conventional subjects and scope remain accurate after the metadata-only patch. `a.commit` was not changed. Mechanical readiness does not establish implementation completeness or authorize committing.

### Findings and boundaries for step 8 version-sources (exchange 1) (round 2)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 8 version-sources (exchange 1) (round 2)

The review is advisory commit-ready. Preserve the Step 8 reassessment and use the existing requestor workflow to present the human convergence choice. No code or test repair is requested.

The request has no literal `Human guidance:` block authorizing reviewer implementation repairs; its generic repair boilerplate was not treated as such authorization. The reviewer made only permitted validation metadata changes.

### Decision rationale for step 8 version-sources (exchange 1) (round 2)

Advisory commit-ready. All six readiness-floor results pass: exact identity; complete implementation including R1; writer validation/coverage evidence with static coverage assessment; attributable staged scope under the explicit reviewed-step metadata exception; no unresolved current or carried findings; and accurate `a.commit` membership, order, scope and subjects. No substantive reviewer repair occurred. This recommendation does not authorize a commit or confirm convergence.

### Final reviewer decision for step 8 version-sources (exchange 1) (round 2)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-8-round-2 -->

## Round 2 by human - Step 8 - human-confirmation

- Recorded: 2026-11-10T21:07:25+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 8
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->

## Round 1 by requestor - Step 9

- Recorded: 2026-11-11T14:42:22+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Implementation step: 9
- Outcome: request

### Review identity for step 9 version-sources (round 1)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.version-sources.md
Implementation step: 9
Review round: 1

### Code review evidence for step 9 version-sources (round 1)

request_index_tree: 109d4e200b886b36d7a4272254bf978dde2fc534
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.version-sources.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(release): ship version and versions commands
group 1 path: tools/release_workflow/versions.py
group 1 path: tools/release_workflow/cli.py
group 1 path: tools/release_workflow/sources/anchor.py
group 1 path: tests/unit/tools/release_workflow/launcher_simulation.py
group 1 path: tests/unit/tools/release_workflow/version_support.py
group 1 path: tests/unit/tools/release_workflow/test_cli/test_cli_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_release_acceptance/test_release_acceptance_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_version_commands/__init__.py
group 1 path: tests/unit/tools/release_workflow/test_version_commands/test_version_commands_tdd.py
group 2: test(release): run version acceptance end to end
group 2 path: tests/unit/tools/release_workflow/test_version_acceptance/__init__.py
group 2 path: tests/unit/tools/release_workflow/test_version_acceptance/test_version_acceptance_tdd.py
group 2 path: tests/unit/tools/release_workflow/test_version_acceptance/test_version_range_acceptance_tdd.py
group 3: docs(wiki): document the version commands
group 3 path: wiki/reference/version-sources.md
group 3 path: wiki/reference/automation-and-direct-invocation.md
group 3 path: wiki/reference/aliases-and-launchers.md
group 3 path: wiki/README.md
group 4: docs(version-sources): record step 9 validation
group 4 path: docs/v0.14.0/plan.v0.14.0.version-sources.validation.md
group 4 path: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
staged path: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
staged path: docs/v0.14.0/plan.v0.14.0.version-sources.validation.md
staged path: tests/unit/tools/release_workflow/launcher_simulation.py
staged path: tests/unit/tools/release_workflow/test_cli/test_cli_tdd.py
staged path: tests/unit/tools/release_workflow/test_release_acceptance/test_release_acceptance_tdd.py
staged path: tests/unit/tools/release_workflow/test_version_acceptance/__init__.py
staged path: tests/unit/tools/release_workflow/test_version_acceptance/test_version_acceptance_tdd.py
staged path: tests/unit/tools/release_workflow/test_version_acceptance/test_version_range_acceptance_tdd.py
staged path: tests/unit/tools/release_workflow/test_version_commands/__init__.py
staged path: tests/unit/tools/release_workflow/test_version_commands/test_version_commands_tdd.py
staged path: tests/unit/tools/release_workflow/version_support.py
staged path: tools/release_workflow/cli.py
staged path: tools/release_workflow/sources/anchor.py
staged path: tools/release_workflow/versions.py
staged path: wiki/README.md
staged path: wiki/reference/aliases-and-launchers.md
staged path: wiki/reference/automation-and-direct-invocation.md
staged path: wiki/reference/version-sources.md
```

### Validation scope for step 9 version-sources (round 1)

Validation scope: the whole suite.

### Requestor assessment for step 9 version-sources (round 1)

Writer assessment for Step 9 of the version-sources plan, round 1: the step is
fully implemented, and its implementation check records
`Yes. Step 9 has been fully implemented.` in the staged validation plan, which
now reads `Yes, it is implemented.`; the umbrella row of `version-sources` is
completed with its requirement and validation plan paths.

Evidence, all on the staged tree:

- Tests first: with the production changes set aside, `ghog single` on the
  step 9 leaves failed at collection (`ModuleNotFoundError:
  tools.release_workflow.versions`, exit 4). After the implementation they
  passed (295 tests with the affected leaves).
- `ghog day --whole-suite`, the command printed by `pw scope day`, exit 0
  after check.bat findings on deferred imports (rewrapped by `ruff --fix`).
- `ghog day --full=cov --whole-suite`, the completion criterion, exit 0 with
  `cov=100` (6442 tests), after adding the page's `## Invocation model`
  section and reshaping two CRLF `set` rows that exceeded the lifecycle CPU
  budget. One unrelated flake, `test_lifecycle_cpu_band.py::
  test_the_gate_records_proofs_and_the_drift_guard_drops_them`, failed in one
  full run and passed in focus and in the next runs.
- Review validation, `ghog day --full=speed --whole-suite` (the built-in
  default; no `.review-validation`): exit 0 with `cov=100 outliers=0
  excluded=0 proof=speed` (6444 tests), on index tree
  `109d4e200b886b36d7a4272254bf978dde2fc534`. No budget was changed and no
  exclusion is accepted.
- `rg -n 'cliff' tools/release_workflow` finds nothing; the two existing
  reference pages keep `unavailable in this tooling checkout` only for any
  other operation name. Every Python file stays below 650 lines
  (`versions.py` 223, the largest test file 484).
- Markdown check and cSpell on the six staged Markdown files: clean.

Architecture: `versions.py` is the command layer over the domain modules; it
never imports `cli`, which only wires the two handlers, and the transition's
side effects stay behind `TransitionPorts`. Performance: each read command
reads each source once and lists the artifact home once; `list` adds one Git
listing and `range` keeps the selector's four calls. Feature integrity: every
other operation name stays unavailable, and no existing caller is switched.

Please check in particular: the token validator and the CLI's refusal before
any Git context; the status each error keeps (`exit_code`, 1 otherwise); the
stdout formats against the design's output contract; whether the acceptance
covers every design row, including the replay of the recorded lock evidence;
the handler-location deviation; and the reference page against the code.

### Implementation report for step 9 version-sources (round 1)

Step 9, "Version commands, integrated acceptance and documentation", ships
the `version` and `versions` commands over the domain of steps 1 to 8, runs
the design's acceptance matrix end to end and documents the commands. It is
the last step of the plan.

Commands, `tools/release_workflow/versions.py`:

- `validate_versions(tokens)`: a `match` on the trailing tokens accepts
  `list`, `check`, `range`, `set <token>` (parsed by `VersionToken.parse`)
  and `range <tag>` (a `tags.StableName`); anything else raises `ValueError`
  with the expected forms. The CLI runs it right after parsing, so a refused
  token is status 2 before any identity load, Git context or file read.
- `show_version(context)`: lists the artifact home for leftover evidence,
  then `anchor.read_document(root, FileView())` and prints
  `token\ntitle\n\nnotes`.
- `VersionsCommand(ports=None)`: `__call__` copies `VersionInputs` from the
  context; `set` calls `version_transition.set_versions` with these ports
  (the production `DEFAULT_PORTS` when `None`) and prints
  `path field old new` per change, `version.txt` last, or `unchanged`; a
  nonzero outcome adds `versions set <t> failed: <outcome>`. The read
  operations (`_list`, `_check`, `_range`) get the leftover-evidence
  warnings first; `list` prints a header, the participating sources, the
  tool-only records and the undeclared candidates from one view and one Git
  listing; `check` derives each expected value from the anchor source's
  token and returns 1 with a diagnostic on drift; `range` prints the four
  `key=value` lines and passes the selector's warnings to stderr.
- `_failed`: a refused command keeps the status of its error's `exit_code`
  (every domain error is a `ValueError`), 1 when it carries none.
- `leftover_warnings`: one `find_evidence` listing, one warning per directory
  with its kind and remedy.
- Imports: only `results` at module level; each function imports the domain
  modules it uses, one line each (check.bat's `ruff --fix` rewraps import
  lines over 88 characters, so they import modules, not names).

Registry, `tools/release_workflow/cli.py`: `SHIPPED_HANDLERS` maps `version`
to `Handler(versions.show_version)` and `versions` to
`Handler(versions.VersionsCommand(), validate_arguments=versions.validate_versions)`.
The plan placed `VERSION_HANDLER` and `VERSIONS_HANDLER` in `versions`; that
module would then import `cli` while `cli` imports it, a cycle that fails when
`versions` is imported first. The deviation is recorded in the validation
plan, and a test pins the shipped values.

`sources/anchor.py`: `read_document(root, view)` holds the read the adapter
already did, so `version` and the adapter share the missing and malformed
messages.

Tests and support:

- `launcher_simulation._patch_git` is now public `patch_git`.
- `version_support`: `run_command` runs one command through `cli.main` for
  repository A with that simulated Git and captured streams;
  `command_project` writes the files and `.release.ini` without loading them
  and declares the listing; `version_registry(ports)` is the shipped registry
  with `VersionsCommand(ports)`, the plan decision Q07 seam.
- `test_version_commands/`: each command's exact output, status and Git
  calls; ten refused token lists with identity and Git context creation
  patched to fail; warnings for each read command and each evidence kind;
  refusals, an evidence write failure and status 3.
- `test_version_acceptance/test_version_acceptance_tdd.py`: AC1 to AC12 with
  whole-tree snapshots for read commands, refusals and failures; the
  recorded uv and npm evidence replayed through `versions set`; seven
  launcher cases through `ToolingSimulation.run` covering each command and
  statuses 0 to 3.
- `test_version_acceptance/test_version_range_acceptance_tdd.py`: AC13 to
  AC15 through `versions range`, the release-version rule and `set` not
  applying it.
- `test_release_acceptance_tdd.py`, `test_cli_tdd.py`: the shipped registry is
  exactly the version pair.

Docs: the new `wiki/reference/version-sources.md`, the shipped pair and status
3 in `automation-and-direct-invocation.md` and `aliases-and-launchers.md`, and
a link in `wiki/README.md`. The validation plan records Step 9 and flips to
`Yes, it is implemented.`; the umbrella row of `version-sources` is completed.

Writer notes: `.reviews/a.version-sources.step9.journal.md` and
`.reviews/a.version-sources.step9.handoff.md`.

### Change summary for step 9 version-sources (round 1)

Staged paths (18), grouped in the root `a.commit` (four groups, checker
`ready: true`):

1. `feat(release): ship version and versions commands`:
   `tools/release_workflow/versions.py`, `tools/release_workflow/cli.py`,
   `tools/release_workflow/sources/anchor.py`,
   `tests/unit/tools/release_workflow/launcher_simulation.py`,
   `tests/unit/tools/release_workflow/version_support.py`,
   `tests/unit/tools/release_workflow/test_cli/test_cli_tdd.py`,
   `tests/unit/tools/release_workflow/test_release_acceptance/test_release_acceptance_tdd.py`,
   `tests/unit/tools/release_workflow/test_version_commands/__init__.py`,
   `tests/unit/tools/release_workflow/test_version_commands/test_version_commands_tdd.py`.
2. `test(release): run version acceptance end to end`:
   `tests/unit/tools/release_workflow/test_version_acceptance/__init__.py`,
   `tests/unit/tools/release_workflow/test_version_acceptance/test_version_acceptance_tdd.py`,
   `tests/unit/tools/release_workflow/test_version_acceptance/test_version_range_acceptance_tdd.py`.
3. `docs(wiki): document the version commands`:
   `wiki/reference/version-sources.md`,
   `wiki/reference/automation-and-direct-invocation.md`,
   `wiki/reference/aliases-and-launchers.md`, `wiki/README.md`.
4. `docs(version-sources): record step 9 validation`:
   `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md` (Step 9
   sections, document status), `docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md`
   (umbrella row 2 completed).

Steps 1 to 8 are committed and pushed (`a7c0d7c` to `79d9a75`) and are not
part of this review.

### Writer response for step 9 version-sources (round 1)

Writer response:

This is the first round of the Step 9 code review; there is no earlier
reviewer feedback to answer.

Choices worth checking, all recorded in the validation plan or the step notes:

- The two `Handler` values are built in `cli.py`, not exported by `versions`
  as the plan wrote, to avoid an import cycle; `test_version_commands` pins
  them.
- Fault injection through the CLI uses `VersionsCommand(ports)` in an
  explicit registry (plan decision Q07). Lock contention needs it too: the
  production probe would recover the declared fake owner as dead.
- `check` prints no header (the design names one for `list` only); `set`
  prints `path field old new`; a failed `set` ends with
  `versions set <t> failed: <outcome>`; the leftover warning names the
  evidence kind and its remedy; `range` warnings stay as the selector words
  them.
- An error without `exit_code` (a lock error, a Git policy error) is status 1;
  an `OSError` escapes to the dispatcher's status 1 as before.
- The lifecycle row (a lock of another project) is tested in process,
  because only item 5 reaches the primitive with a lifecycle lock.
- Two CRLF `set` rows check each source byte for byte and the artifact home
  listing instead of whole trees, to stay inside the 0.1 second lifecycle
  CPU budget: a five-file `set` costs about that much, mostly in the
  foundation's path authorization of managed writes. The every-adapter
  project uses a pattern source on a POM property, which also composes two
  adapters' fields in one file.
- `version` on a project without `version.txt` through an installed launcher
  now returns status 2 for the missing anchor; the reference caller test
  keeps its expectation (status 2 propagates without fallback).

### Reviewer focus for step 9 version-sources (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-9-round-1 -->

## Round 1 by reviewer - Step 9

- Recorded: 2026-11-11T14:52:10+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 9
- Outcome: answer

### Assessed index identity for step 9 version-sources (exchange 1) (round 1)

Baseline index tree: 109d4e200b886b36d7a4272254bf978dde2fc534

Assessed index tree: 37d706b26ae0676f28f547a1e207715535de281f

### Implementation check for step 9 version-sources (exchange 1) (round 1)

Result:

Yes. Step 9 has been fully implemented.

The staged handlers expose `version`, `versions list`, `check`, `set` and
`range` through the production dispatcher. The argument validator runs before
runtime identity and Git context creation. Output matches the design's token,
tab-separated record and key/value contracts; domain statuses and transition
status 3 survive rendering. Read commands warn about retained evidence and use
the read-only artifact declaration.

The new `VersionsCommand` delegates mutations to `set_versions` through
`TransitionPorts`; `show_version` shares `anchor.read_document` with detection.
Constructing the two `Handler` values in `cli.py` avoids an import cycle and
preserves the planned registry contract. No DDD-Hexagonal violation or
architecture correction was found.

The command tests exercise malformed arguments, exact outputs, drift,
same-target writes, refusals, evidence warnings and error propagation. The
acceptance tests cover the design rows across source arrangements, recorded
uv/npm pairs, restoration, incomplete restoration, contention, interruption,
cleanup and tag eligibility. Launcher cases carry every command and statuses
0 through 3 through bootstrap and rendering. Existing adapter completeness
and recorded tool evidence remain owned by their earlier test packages.

Coverage assessment is static: the gate measures `tools`, omitting tests,
initializers and ports. The changed production paths have corresponding unit
tests, and every added test-support symbol has references. No untested branch
or unreferenced top-level helper was identified. The reported whole-suite
100% result is writer evidence, not an independently rerun percentage.

Rendering and inventory processing are linear; discovery and range queries
retain their bounded domain calls. No performance issue or impaired existing
feature was found. The reference pages describe the shipped commands, formats,
statuses, configuration, supported layouts and recovery limits accurately.

Validation plan effects:

Added only an independent round-1 assessment paragraph beneath the exact
`Yes. Step 9 has been fully implemented.` sentence. The rest of the validation
plan and its document-level status were preserved. The writer's staged
umbrella completion was assessed read-only; the reviewer changed no umbrella
row. No missing-work section is required for this Yes result.

### Pre-repair mandatory checks and coverage for step 9 version-sources (exchange 1) (round 1)

Baseline index matched request tree
`109d4e200b886b36d7a4272254bf978dde2fc534`. The bound scope fingerprint is
`686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6`
(whole suite). Independent commit-plan-check was valid and ready with all 18
staged paths and no diagnostics. The validation plan's pre-edit blob is
`3bafc3309c9a0dcb8fc7985e64ae534604e0e583`.

The request records successful whole-suite speed validation on that exact
index: 6444 tests, cov=100, outliers=0, excluded=0. The reviewer did not run
ghog day, ghog full, coverage, or additional focused tests; static assessment
was sufficient for this round.

### Resolved validation set and sources for step 9 version-sources (exchange 1) (round 1)

Request and current resolver: `ghog day --full=speed --whole-suite`, source
`project`. Sampled `.review-validation` as absent. The built-in default
`ghog day --full=speed` is completed with the whole-suite selector, as defined
by `complete_project_default`; no plan or request additions were declared.
These commands are requestor-owned validation evidence and were not rerun.

### Resolver drift and direction for step 9 version-sources (exchange 1) (round 1)

None. Request and current resolver commands, order, scope and source agree;
neither additions nor removals were found.

### Repository state around validation for step 9 version-sources (exchange 1) (round 1)

The umbrella digest comparison reports changed=false. The validation-state
comparison names only the reviewed validation plan and `<index>` as changed;
both are explained by staging the attributable eight-line Step 9 review
paragraph. No other tracked, untracked or ignored validation side effect was
reported. The generic comparison's acceptable=false reflects those expected
metadata changes, which are permitted by reviewer assessment mode.

The attribution helper reports attributable=true against the retained blob;
only its patch was applied to the index. The retained manifest now records
the resulting assessed index and validation-after state. No implementation,
test, umbrella or commit grouping change was made by the reviewer.

### Repair inventory for step 9 version-sources (exchange 1) (round 1)

Repairs made:

- Polishing-only review metadata: added the independent assessment paragraph
  to `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md`. No substantive
  repair was made.

Paths staged:

- `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md` (only the attributable
  Step 9 reviewer paragraph; existing writer staging was preserved).

### Commit plan assessment for step 9 version-sources (exchange 1) (round 1)

Independent commit-plan-check reports state=valid, ready=true, 18 staged paths
and diagnostics=[]. It remains valid after staging the review metadata.
The four ordered groups remain accurate:

1. `feat(release): ship version and versions commands`
2. `test(release): run version acceptance end to end`
3. `docs(wiki): document the version commands`
4. `docs(version-sources): record step 9 validation`

The production, test-support and unit-test changes form the first group;
integrated acceptance, reference documentation and validation/umbrella
evidence follow. All staged paths belong to the reviewed step. `a.commit`
was not changed.

### Findings and boundaries for step 9 version-sources (exchange 1) (round 1)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 9 version-sources (exchange 1) (round 1)

No rework is requested. The requestor may consume this advisory answer and
present the durable human Commit gate. This answer authorizes no commit.

### Decision rationale for step 9 version-sources (exchange 1) (round 1)

All six readiness-floor results pass: exact request identity and baseline;
complete Step 9 implementation; matching requestor validation evidence and
static coverage assessment; attributable staged scope; no unresolved findings;
and accurate, mechanically valid `a.commit` grouping. The only reviewer edit
is permitted review metadata. Recommend commit-ready, subject to the human
gate; no commit has been performed or authorized by this reviewer.

### Final reviewer decision for step 9 version-sources (exchange 1) (round 1)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-9-round-1 -->

## Round 1 by human - Step 9 - human-confirmation

- Recorded: 2026-11-11T16:19:34+01:00
- Exchange: code/code/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 9
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-1 -->
