# Code review transcript for v0.14.0

- Exchange: code/code/v0.14.0/release-project-root
- Reviewed document: docs/v0.14.0/plan.v0.14.0.release-project-root.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor - Step 1

- Recorded: 2026-10-22T11:49:00+02:00
- Exchange: code/code/v0.14.0/release-project-root
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.release-project-root.md
- Requestor LLM nature: codex
- Reviewer LLM nature: unrecorded
- Implementation step: 1
- Outcome: request

### Review identity for step 1 release-project-root (round 1)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.release-project-root.md
Implementation step: 1
Review round: 1

### Code review evidence for step 1 release-project-root (round 1)

request_index_tree: 84ab1f27a0d6c8fa4f617790cb258caeec85789a
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project, request)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.release-project-root.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: docs(review): qualify duplicate headings
group 1 path: docs/v0.14.0/review.design-specification.v0.14.0.release-project-root.md
group 2: perf(tests): reuse review CLI initialization
group 2 path: tests/acceptance/commit_plan_check/commit_plan_check_support.py
group 2 path: tests/acceptance/review_resume/__init__.py
group 2 path: tests/acceptance/review_resume/cli_support.py
group 2 path: tests/acceptance/review_resume/conftest.py
group 2 path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_identity_tdd.py
group 2 path: tests/acceptance/review_status/conftest.py
group 2 path: tests/unit/tools/git_test_double.py
group 2 path: tests/unit/tools/test_code_reviewer_acceptance/fixtures.py
group 3: feat(release): validate setup-owned runtime
group 3 path: bin/release_runtime_record.bat
group 3 path: pyproject.toml
group 3 path: senv.bat
group 3 path: tests/acceptance/release_workflow/__init__.py
group 3 path: tests/acceptance/release_workflow/conftest.py
group 3 path: tests/acceptance/release_workflow/process_support.py
group 3 path: tests/acceptance/release_workflow/test_release_readiness_tdd.py
group 3 path: tests/acceptance/release_workflow/test_uv_readiness_tdd.py
group 3 path: tests/unit/tools/release_workflow/__init__.py
group 3 path: tests/unit/tools/release_workflow/conftest.py
group 3 path: tests/unit/tools/release_workflow/test_bootstrap/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_markers/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_markers/test_markers_pbt.py
group 3 path: tests/unit/tools/release_workflow/test_markers/test_markers_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_readiness/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_readiness/test_faults_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_readiness/test_metadata_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_readiness/test_readiness_pbt.py
group 3 path: tests/unit/tools/release_workflow/test_readiness/test_readiness_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_runtime/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_runtime/test_runtime_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_support.py
group 3 path: tools/release_workflow/__init__.py
group 3 path: tools/release_workflow/bootstrap.py
group 3 path: tools/release_workflow/markers.py
group 3 path: tools/release_workflow/readiness.py
group 3 path: tools/release_workflow/runtime_identity.py
group 3 path: uv.lock
group 4: docs(release-project-root): record step 1 validation
group 4 path: docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md
staged path: bin/release_runtime_record.bat
staged path: docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md
staged path: docs/v0.14.0/review.design-specification.v0.14.0.release-project-root.md
staged path: pyproject.toml
staged path: senv.bat
staged path: tests/acceptance/commit_plan_check/commit_plan_check_support.py
staged path: tests/acceptance/release_workflow/__init__.py
staged path: tests/acceptance/release_workflow/conftest.py
staged path: tests/acceptance/release_workflow/process_support.py
staged path: tests/acceptance/release_workflow/test_release_readiness_tdd.py
staged path: tests/acceptance/release_workflow/test_uv_readiness_tdd.py
staged path: tests/acceptance/review_resume/__init__.py
staged path: tests/acceptance/review_resume/cli_support.py
staged path: tests/acceptance/review_resume/conftest.py
staged path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_identity_tdd.py
staged path: tests/acceptance/review_status/conftest.py
staged path: tests/unit/tools/git_test_double.py
staged path: tests/unit/tools/release_workflow/__init__.py
staged path: tests/unit/tools/release_workflow/conftest.py
staged path: tests/unit/tools/release_workflow/test_bootstrap/__init__.py
staged path: tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py
staged path: tests/unit/tools/release_workflow/test_markers/__init__.py
staged path: tests/unit/tools/release_workflow/test_markers/test_markers_pbt.py
staged path: tests/unit/tools/release_workflow/test_markers/test_markers_tdd.py
staged path: tests/unit/tools/release_workflow/test_readiness/__init__.py
staged path: tests/unit/tools/release_workflow/test_readiness/test_faults_tdd.py
staged path: tests/unit/tools/release_workflow/test_readiness/test_metadata_tdd.py
staged path: tests/unit/tools/release_workflow/test_readiness/test_readiness_pbt.py
staged path: tests/unit/tools/release_workflow/test_readiness/test_readiness_tdd.py
staged path: tests/unit/tools/release_workflow/test_runtime/__init__.py
staged path: tests/unit/tools/release_workflow/test_runtime/test_runtime_tdd.py
staged path: tests/unit/tools/release_workflow/test_support.py
staged path: tests/unit/tools/test_code_reviewer_acceptance/fixtures.py
staged path: tools/release_workflow/__init__.py
staged path: tools/release_workflow/bootstrap.py
staged path: tools/release_workflow/markers.py
staged path: tools/release_workflow/readiness.py
staged path: tools/release_workflow/runtime_identity.py
staged path: uv.lock
```

### Validation scope for step 1 release-project-root (round 1)

Validation scope: the whole suite.

### Requestor assessment for step 1 release-project-root (round 1)

Step 1 is fully implemented. The validation plan records its file-level and
behavioral evidence; Steps 2-6 remain pending.

The final `ghog day --full=speed --whole-suite` completed on 2026-10-22 with
exit 0: compile/type/lint checks passed, 90 affected tests passed, the full
stage reached 100% tools coverage, and sequential timing of 3,687 tests passed
with no failures, warnings, xfails, outliers or exclusions. The final timing
stage's `cov=skipped` does not replace the preceding full stage's `cov=100`.
Evidence is in `a.ghog.log` and the private preserved final-gate log.

Production modules remain below the 650-line ceiling. Dependency candidates
are indexed once and traversed with a visited set. Bootstrap imports exact
sibling helpers before readiness and inserts the checkout path only after
readiness succeeds. Runtime publication is atomic and follows successful
preparation. Tests cover failures, marker and graph invariants, isolated
processes, physical junction boundaries, real batch entry, eager stdlib
closure, and offline uv-generated empty-lock shapes.

The user-requested fixture refactor retains all assertions and reduces the
eight provider-identity tests from 71.86s to 8.78s including setup (87.8%).
Complete CODE/SPECIFICATION lifecycles and concurrent waiters retain real
process boundaries; migration tests retain real Git. Review the fixture
isolation and retained process coverage alongside the runtime foundation.

### Implementation report for step 1 release-project-root (round 1)

Successful setup now records its measured checkout-owned runtime in ignored
`venvs/release-runtime.json`. The batch producer uses the prepared absolute
interpreter with isolation and UTF-8, and setup preserves preparation and
producer failures through cleanup. Runtime identity rejects lexical and
physical escapes, foreign prefixes and unusable environments.

The standalone bootstrap loads exact sibling helpers under private names,
checks runtime and locked dependency readiness, then imports the engine.
The release dependency group is empty because the foundation uses only the
standard library; dev includes release and the lock was regenerated without
upgrades. The closed marker grammar validates even inactive boolean branches.
The production CLI is intentionally deferred to Step 5; Step 1 tests supply
a disposable engine and separately verify missing-engine failure.

Fresh setup and isolated capture succeeded: empty release closure,
tools_imported=false, isolated=1 and utf8=1. Setup evidence stays private.

The shared acceptance harness reuses CLI imports with a fresh runtime per
invocation and restores cwd, environment and streams. Provider-only identity
variants reuse the existing Git double, which now handles absolute executables
and leading -C. Tracked seed bytes are captured once. Synthetic seed commits
disable signing only for the command. Real CODE/SPECIFICATION journeys,
concurrent waiters and migration Git behavior retain their process boundaries.

Measured identical eight-test module including fixtures: baseline 71.86s;
in-process CLI with real Git 47.73s; provider-only Git double 8.78s. All
assertions retained. Profiles and raw logs are in the writer's private notes.
Accepted duration exclusions: none. Raised baselines: none.

The final whole-suite speed gate passed, including full 100% tools coverage.
No production or test code changed afterward; the validation record was then
completed. Two duplicate headings in the existing design review transcript
were qualified to satisfy Markdown checks without changing their content.

Writer notes: `.reviews/a.release-project-root.step1.journal.md` and
`.reviews/a.release-project-root.step1.handoff.md`.

### Change summary for step 1 release-project-root (round 1)

The staged work contains 39 paths, assigned exactly once to four groups in root a.commit. The canonical commit-plan-check reports ready=true with no diagnostics.

#### Staged paths for step 1 release-project-root (round 1)

- bin/release_runtime_record.bat
- docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md
- docs/v0.14.0/review.design-specification.v0.14.0.release-project-root.md
- pyproject.toml
- senv.bat
- tests/acceptance/commit_plan_check/commit_plan_check_support.py
- tests/acceptance/release_workflow/**init**.py
- tests/acceptance/release_workflow/conftest.py
- tests/acceptance/release_workflow/process_support.py
- tests/acceptance/release_workflow/test_release_readiness_tdd.py
- tests/acceptance/release_workflow/test_uv_readiness_tdd.py
- tests/acceptance/review_resume/**init**.py
- tests/acceptance/review_resume/cli_support.py
- tests/acceptance/review_resume/conftest.py
- tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_identity_tdd.py
- tests/acceptance/review_status/conftest.py
- tests/unit/tools/git_test_double.py
- tests/unit/tools/release_workflow/**init**.py
- tests/unit/tools/release_workflow/conftest.py
- tests/unit/tools/release_workflow/test_bootstrap/**init**.py
- tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py
- tests/unit/tools/release_workflow/test_markers/**init**.py
- tests/unit/tools/release_workflow/test_markers/test_markers_pbt.py
- tests/unit/tools/release_workflow/test_markers/test_markers_tdd.py
- tests/unit/tools/release_workflow/test_readiness/**init**.py
- tests/unit/tools/release_workflow/test_readiness/test_faults_tdd.py
- tests/unit/tools/release_workflow/test_readiness/test_metadata_tdd.py
- tests/unit/tools/release_workflow/test_readiness/test_readiness_pbt.py
- tests/unit/tools/release_workflow/test_readiness/test_readiness_tdd.py
- tests/unit/tools/release_workflow/test_runtime/**init**.py
- tests/unit/tools/release_workflow/test_runtime/test_runtime_tdd.py
- tests/unit/tools/release_workflow/test_support.py
- tests/unit/tools/test_code_reviewer_acceptance/fixtures.py
- tools/release_workflow/**init**.py
- tools/release_workflow/bootstrap.py
- tools/release_workflow/markers.py
- tools/release_workflow/readiness.py
- tools/release_workflow/runtime_identity.py
- uv.lock

##### Prepared commit groups for step 1 release-project-root (round 1)

#### Grouping commits by topic for step 1 release-project-root (round 1)

##### Group 1: Review transcript heading cleanup for step 1 release-project-root (round 1)

git add -A docs/v0.14.0/review.design-specification.v0.14.0.release-project-root.md

```log
docs(review): qualify duplicate headings

Why:

Repeated guidance headings made the design review transcript fail the Markdown
gate.

Each original entry now has a distinct heading while its review content remains
intact.

What:

- Qualify the two initial guidance entries in rounds 2 and 3.
```

##### Group 2: Shorter shared test initialization for step 1 release-project-root (round 1)

git add -A tests/acceptance/commit_plan_check/commit_plan_check_support.py
git add -A tests/acceptance/review_resume/**init**.py
git add -A tests/acceptance/review_resume/cli_support.py
git add -A tests/acceptance/review_resume/conftest.py
git add -A tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_identity_tdd.py
git add -A tests/acceptance/review_status/conftest.py
git add -A tests/unit/tools/git_test_double.py
git add -A tests/unit/tools/test_code_reviewer_acceptance/fixtures.py

```log
perf(tests): reuse review CLI initialization

Why:

Repeated Python and Git process startup dominated provider identity fixture
setup. Host signing rules also rejected synthetic fixture identities.

The eight-test identity module now completes in `8.78` seconds instead of
`71.86` seconds, including setup, with every assertion retained.

What:

- Reuse CLI imports and restore cwd, environment and captured streams.
- Use the existing Git double for provider-only identity variants.
- Recognize absolute Git executables and leading `-C` repository paths.
- Keep complete lifecycle journeys and concurrent waiters in real processes.
- Disable signing only on synthetic fixture seed commits.
```

##### Group 3: Setup-owned release runtime and readiness for step 1 release-project-root (round 1)

git add -A bin/release_runtime_record.bat
git add -A pyproject.toml
git add -A senv.bat
git add -A tests/acceptance/release_workflow/**init**.py
git add -A tests/acceptance/release_workflow/conftest.py
git add -A tests/acceptance/release_workflow/process_support.py
git add -A tests/acceptance/release_workflow/test_release_readiness_tdd.py
git add -A tests/acceptance/release_workflow/test_uv_readiness_tdd.py
git add -A tests/unit/tools/release_workflow/**init**.py
git add -A tests/unit/tools/release_workflow/conftest.py
git add -A tests/unit/tools/release_workflow/test_bootstrap/**init**.py
git add -A tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py
git add -A tests/unit/tools/release_workflow/test_markers/**init**.py
git add -A tests/unit/tools/release_workflow/test_markers/test_markers_pbt.py
git add -A tests/unit/tools/release_workflow/test_markers/test_markers_tdd.py
git add -A tests/unit/tools/release_workflow/test_readiness/**init**.py
git add -A tests/unit/tools/release_workflow/test_readiness/test_faults_tdd.py
git add -A tests/unit/tools/release_workflow/test_readiness/test_metadata_tdd.py
git add -A tests/unit/tools/release_workflow/test_readiness/test_readiness_pbt.py
git add -A tests/unit/tools/release_workflow/test_readiness/test_readiness_tdd.py
git add -A tests/unit/tools/release_workflow/test_runtime/**init**.py
git add -A tests/unit/tools/release_workflow/test_runtime/test_runtime_tdd.py
git add -A tests/unit/tools/release_workflow/test_support.py
git add -A tools/release_workflow/**init**.py
git add -A tools/release_workflow/bootstrap.py
git add -A tools/release_workflow/markers.py
git add -A tools/release_workflow/readiness.py
git add -A tools/release_workflow/runtime_identity.py
git add -A uv.lock

```log
feat(release): validate setup-owned runtime

Why:

Release startup needs one setup-owned runtime identity before it can check
interpreter and locked dependency readiness without ambient fallback.

Successful setup now records its measured environment. The isolated bootstrap
validates that record and release metadata before importing the engine.

What:

- Preserve setup status and atomically publish the measured runtime record.
- Declare the stdlib-only release group and include it from dev.
- Check physical containment, interpreter clauses and locked dependency graphs.
- Parse the closed marker grammar and load helpers before package imports.
- Cover failures and invariants with unit and property-based tests.
- Exercise real batch setup, isolated processes, junctions and offline uv locks.
- Pass the whole-suite speed gate with 100 percent tools coverage.
```

##### Group 4: Step 1 validation for step 1 release-project-root (round 1)

git add -A docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md

```log
docs(release-project-root): record step 1 validation

Why:

The runtime foundation and its validation evidence now satisfy Step 1. The
remaining five plan steps still require implementation.

The validation plan records the completed contract, architecture, coverage and
measured fixture improvement without claiming later-step completion.

What:

- Record runtime, dependency, import and fresh-setup evidence.
- Record 100 percent tools coverage and the green whole-suite speed gate.
- Record the `87.8` percent fixture reduction and retained process boundaries.
- Keep Steps 2 through 6 pending.
```

### Human guidance and writer response for step 1 release-project-root (round 1)

Human guidance:

The user requested drastic test-time reduction through fixture and shared
initialization refactoring. Keep the work to Step 1 and its test optimization.
All assertions and meaningful process boundaries must remain. Do not infer
authorization to commit or implement Step 2 from review convergence.

Writer response:

Initial implementation review; no earlier code-review feedback to accept or
dispute. The prior specification review and consolidation are complete.
The current request includes the user's subsequent test-fixture optimization.

### Reviewer focus for step 1 release-project-root (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-1-round-1 -->

### LLM nature completion for reviewer (exchange 1)

Recorded nature: `claude`

Completed artifacts:

- `C:/Users/vonc/git/llm-shared_sibling_release_tooling/.reviews/a.review-active.code.code.v0.14.0.release-project-root.md`
- `C:/Users/vonc/git/llm-shared_sibling_release_tooling/.reviews/a.review-requested.code.v0.14.0.release-project-root.md`

<!-- review-entry-id: llm-nature-completion-reviewer-exchange-1 -->

## Round 1 by reviewer - Step 1

- Recorded: 2026-10-22T13:43:03+02:00
- Exchange: code/code/v0.14.0/release-project-root
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.release-project-root.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 1
- Outcome: answer

### Assessed index identity for step 1 release-project-root (exchange 1) (round 1)

Baseline index tree: 84ab1f27a0d6c8fa4f617790cb258caeec85789a

Assessed index tree: 481412fdbabc139271585139c112ca6a5779b78a

### Implementation check for step 1 release-project-root (exchange 1) (round 1)

Result:

Result:

No. Step 1 has NOT been fully implemented.

The runtime producer, the isolated bootstrap, the closed marker grammar, the
lock-graph readiness check and their unit, property-based and process tests are
in place, and the focused suite passes. Two gaps keep Step 1 open. The
published record does not follow the plan's runtime-file contract (R1), and
`senv.bat` now aborts setup when `switchpy` prepares no checkout-local
environment, so existing setup is not preserved (R2). The exact Step 1
validation rows now say No and list this work under *Missing work for Step 1*.

Plan conformance checked item by item: saved `switchpy` status passed before
`popd`; the producer runs through `%VIRTUAL_ENV%\Scripts\python.exe -I -X utf8`;
measured executable and prefix are checked against the checkout before an
atomic same-directory replace; the empty `release` group is included by `dev`
and mirrored in `uv.lock`; helpers load by exact sibling path under private
names with bytecode writes disabled; the checkout root is inserted only after
readiness; failures return 2 on stderr. Lock format 1, the unique virtual root,
both uv empty-group shapes, version and source-kind disambiguation, fail-closed
ties, extra rejection, the seven marker variables, the eight operators, padded
release tuples and the `requires-python` clause grammar all match the closed
contract. The plan's `rg -n 'VIRTUAL_ENV|PYTHONPATH|glob|rglob|import_module'
tools/release_workflow` scan, run read-only, finds only the intended post-gate
`import_module` in `bootstrap.py:128`.

Architecture: marker parsing and graph traversal take injected lookups and
plain data; filesystem publication, distribution lookup and the engine import
stay at explicit boundaries. Bootstrap types the loaded helpers with protocols
and casts, and no package twin crosses the gate. No layer violation or file over
the 650-line ceiling (largest new module: `readiness.py`, 195 lines).

Performance: index construction is linear with four fixed keys per candidate,
traversal is bounded by a visited set, each metadata file is read once (a unit
test asserts the two reads and forbids directory iteration), and marker parsing
is a single pass. No quadratic or sort-based work was found.

Static coverage: `[tool.coverage.run] source = ["tools"]` measures the four new
behavior modules; `__init__.py` is omitted. Walking every raise and return
branch of `runtime_identity.py`, `bootstrap.py`, `readiness.py` and
`markers.py` against the new tests found each one exercised, consistent with the
requestor's reported 100%. Test support lives outside the gate; its top-level
helpers are all referenced.

Feature integrity: with a checkout-local environment, setup, development
dependency installation and public tools exports are unchanged. Under the other
two `switchpy` choices, setup now stops early (R2). The fixture refactor keeps
every assertion; complete lifecycle journeys, the competing-waiter race and
migration keep their real process and Git boundaries.

Validation plan effects:

Changed only Step 1 rows in
`docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md`: the exact No
sentence and its short rationale under *Analysis of Step 1 implementation
state*, a new *Missing work for Step 1* section placed after *What was
implemented for Step 1* (R1, R2 and R3 as concrete bullets), and the *Feature
integrity for Step 1* conclusion, which now records the `senv.bat` impairment.

The document-level opening line stays `No, it is not implemented`. The header
sentence "Step 1 is implemented and validated." is outside the Step 1 rows and
was left for the writer to refresh. Other steps, the plan, the umbrella,
implementation, tests and `a.commit` were not edited.

The evidence launcher attributed the patch from pre-edit blob
`3875c211de676b7f93c51fa7c1fbb561c514f2d6` (attributable, not created); only
that patch was staged. The project Markdown check passes after the edit. This
is review metadata, not a substantive repair.

### Pre-repair mandatory checks and coverage for step 1 release-project-root (exchange 1) (round 1)

Requestor evidence: `ghog day --full=speed --whole-suite` completed on
2026-10-22 with exit 0, `proof=speed`, full-stage `cov=100`, 3,687 timed
tests, and no failures, warnings, xfails, outliers or exclusions. This is
reported evidence and was not repeated.

Reviewer evidence, each command run once from the project root through the
shared `ghog.bat` launcher with the log-freshness proof:

- `ghog check`: unavailable as evidence. This review's shell inherits
  `SWITCHPY_CHOICE=No venv`, so `switchpy` prepared no environment, and the
  base Python carries none of the check tools (`ty`, `pyright`, `ruff`,
  `radon`, `vulture`), which all reported 9009. The same run is what exposed
  R2: the senv preamble shows `Release runtime setup failed: no prepared
  environment.` and no `Environment initialized` line. This is missing
  evidence, not a pass and not a code defect.
- `ghog affected --no-cov --scope-file=.reviews/a.review-scope.code.v0.14.0.release-project-root.json`,
  run with `SWITCHPY_CHOICE=local` scoped to that one process: exit 0, scope
  whole, 3,687 tests, `fail=0 warn=0 xfail=0`. The senv preamble shows the
  existing checkout venv activated, dependencies synced and `Environment
  initialized`; the runtime record content was unchanged.

The reviewer did not run `ghog day`, `ghog full` or any coverage measurement.
Coverage was assessed statically.

### Resolved validation set and sources for step 1 release-project-root (exchange 1) (round 1)

The request and the current resolver produce the same ordered set:

1. `ghog day --full=speed --whole-suite`: sources project and request.

No `.review-validation` file exists, so the project default is the built-in
`ghog day --full=speed`, completed with the bound `--whole-suite` selector for
scope `whole`. The request adds the same command, which only adds the request
source label. No plan additions were passed. This comparison used the current
resolver code and the exact request; the reviewer did not run the command.

### Resolver drift and direction for step 1 release-project-root (exchange 1) (round 1)

None in resolver output: ordered commands and source labels agree.

Direction note for the requestor: the plan's Step 1 completion names
`rg -n 'VIRTUAL_ENV|PYTHONPATH|glob|rglob|import_module' tools/release_workflow`,
but the request carried it as prose rather than as a plan validation command.
Pass it with `--plan-validation-command` on the next request so it appears in
the resolved set with its plan source.

### Repository state around validation for step 1 release-project-root (exchange 1) (round 1)

Request-time and reviewer baseline index tree:
`84ab1f27a0d6c8fa4f617790cb258caeec85789a` (identical). Final assessed index
tree after the reviewer metadata patch: `481412fdbabc139271585139c112ca6a5779b78a`.

The same ordered 41-path validation set (the 39 staged paths plus the ignored
`a.ghog.log` and `a.ghog.status`) was captured before and after assessment. The
comparison reports tracked differences only for
`docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md` and `<index>`,
ignored differences only for the two ghog files written by the reviewer's
evidence commands, and no untracked differences. The raw `acceptable=false`
reflects the intentional Step 1 metadata edit; the attribution proves every
changed line belongs to the Step 1 rows. No tracked validation side effect and
no overlap with writer work.

Umbrella `docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md`: applicable,
digest `ca6fe473…0ec992` before and after, unchanged. No umbrella row was
modified.

Retained evidence: `.reviews/a.code-review-evidence.v0.14.0.release-project-root.step-1.json`,
with the inputs under `.reviews/a.release-project-root.step1.tmp.r1.*`.

### Repair inventory for step 1 release-project-root (exchange 1) (round 1)

Repairs made:

- Review metadata only: changed the Step 1 validation rows to No, added
  *Missing work for Step 1* (R1 to R3) and qualified the feature-integrity
  conclusion. No implementation, test, plan or `a.commit` repair.

Paths staged:

- docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md (reviewer metadata patch only)

### Commit plan assessment for step 1 release-project-root (exchange 1) (round 1)

Ran `commit-plan-check.bat --format json` independently before assessment and
again after staging the Step 1 metadata. Both returned exit 0, `state=valid`,
`ready=true`, four ordered groups, 39 staged paths and no diagnostics. The
initial JSON is retained in
`.reviews/a.release-project-root.step1.tmp.r1.commit-plan.json`.

Ordered groups:

1. `docs(review): qualify duplicate headings` (1 path)
2. `perf(tests): reuse review CLI initialization` (8 paths)
3. `feat(release): validate setup-owned runtime` (29 paths)
4. `docs(release-project-root): record step 1 validation` (1 path)

Membership, order (transcript fix, test speed-up, feature, validation record)
and conventional subjects match the staged work, so the reviewer did not amend
`a.commit`. One body is now stale: group 4 says the runtime foundation
satisfies Step 1, which the staged validation rows no longer claim. The writer
should rewrite that body together with the R1 to R3 fixes. Mechanical
readiness does not resolve the findings and does not authorize a commit.

### Findings and boundaries for step 1 release-project-root (exchange 1) (round 1)

Unresolved findings:

- R1 (P2): follow the plan's runtime-record contract. The design leaves the
  filename and serialization to implementation, but the plan's *Runtime files*
  section then fixes them: `venvs/release-runtime.v1.txt`, in a versioned line
  format that records the checkout-relative environment directory.
  `tools/release_workflow/runtime_identity.py:17` and `:117` publish
  `venvs/release-runtime.json` as a JSON object instead, and the validation
  plan records no variance. The choice matters for Step 5: its ASCII-only
  batch launchers must read the record as data and start its Python before any
  Python runs. A JSON object is hard to parse in batch. Also, `json.dumps`
  defaults to `ensure_ascii=True`, so a non-ASCII environment name (`switchpy`
  names it `python_<version>_<checkout-name>`) is written as `\uXXXX`
  escapes, which a batch reader cannot turn back into a path. Publish the
  planned line format under the planned name, through one tested
  serialize/parse contract. Add unit cases for a non-ASCII name, extra or
  missing lines, and an unsupported version line. Keeping JSON needs human
  approval and a plan amendment first.
- R2 (P2): let `senv.bat` finish when `switchpy` prepares no checkout-local
  environment. `switchpy` honours `SWITCHPY_CHOICE` (`no` or `No venv`,
  `global`, `local`) and otherwise prompts. With `No venv` it returns 0 and
  leaves `VIRTUAL_ENV` undefined, so `bin/release_runtime_record.bat:6-8`
  returns 2. With `global`, the venv sits under `%PYTHON_ROOT%\venvs`, so
  `RuntimeIdentity.measure` rejects it as outside the checkout, and the entry
  again returns 2. `senv.bat:279` then runs `exit /b 2`. That skips
  sensitive-hook installation, the `%PRJ_DIR%\bin` PATH entry, the
  `NO_MORE_SENV_<name>` guard and the `fsenv` alias. Before this change, senv
  finished under all three choices. Observed in this review: the shell
  inherits `SWITCHPY_CHOICE=No venv`, and the `ghog check` preamble
  (`.reviews/a.ghog.senv.txt`) shows `No virtual environment will be used.`,
  then `Release runtime setup failed: no prepared environment.`, and no
  `Environment initialized` line. Recommended fix, pending the decision listed
  under boundary-crossing work: when `switchpy` succeeds without a
  checkout-local environment, publish nothing, print a warning that names the
  missing release runtime, and let senv finish. Keep the hard failure for a
  producer failure on a checkout-local environment. Cover both non-local cases
  in the batch entry's acceptance matrix; the current `foreign_python` case
  expects exit 2 and would change with this decision.
- R3 (P3): `senv.bat:273` and `:275` leave `RELEASE_SETUP_STATUS` and
  `RELEASE_RUNTIME_STATUS` set in the caller's console. senv already clears
  its other temporaries (`UV_LOCK_DIRTY`, `SENSITIVE_SHARED_RULES`,
  `SENSITIVE_CURRENT_REPO`). Clear both after use and keep the exit status.
- R4 (P3): the two re-qualified headings in
  `docs/v0.14.0/review.design-specification.v0.14.0.release-project-root.md:928`
  and `:1438` now end with `(round 2, initial entry)` and
  `(round 3, initial entry)`. The heading rule in
  `instructions/review-requestor.md` says a round heading ends with
  `(round N)`. Put the discriminator before the suffix, for example
  `#### Initial human-authorized continuation of ... (round 2)`.
- R5 (P3): `test_faults_tdd.py:10`, `test_metadata_tdd.py:9`,
  `test_markers_tdd.py:7` and the acceptance module
  `test_uv_readiness_tdd.py:7` import `ENV` from the test module
  `test_readiness/test_readiness_tdd.py`. Move `ENV` into
  `tests/unit/tools/release_workflow/test_support.py` so that no test module
  depends on another test module.

Boundary-crossing work:

- R2 needs a human decision the plan does not cover: whether llm-shared setup must still finish under the `No venv` and `global` switchpy choices (recommended), or must now require a checkout-local environment. Record the decision in the plan before implementing it.
- Keeping the JSON record instead of the planned line format (R1) would amend the approved plan; that also needs human approval rather than a writer or reviewer choice.

### Human guidance response for step 1 release-project-root (exchange 1) (round 1)

Human guidance:

The user requested drastic test-time reduction through fixture and shared
initialization refactoring. Keep the work to Step 1 and its test optimization.
All assertions and meaningful process boundaries must remain. Do not infer
authorization to commit or implement Step 2 from review convergence.

Guidance response:

The guidance was applied as review scope. It does not instruct a repair, so the
reviewer changed no implementation or test file. The request's general
"make every safe repair" wording does not override that rule.

Test optimization: no assertion was removed. `run_inline` restores cwd,
environment and streams for each call, and the CLI parser reports errors as
JSON rather than exiting, so in-process variants still get a result for every
call. Both complete CODE and SPECIFICATION lifecycles pass `processes=True`.
The competing-reviewer race still starts two real waiter processes, migration
still uses real Git, and the Git double is limited to the provider-identity
module. The scope stayed within Step 1 and its test optimization; nothing from
Step 2 was implemented. This answer does not authorize a commit.

### Writer instructions for step 1 release-project-root (exchange 1) (round 1)

Get the human's answer on the R2 behavior, and on R1 only if you want to keep
JSON. Then fix R1 to R5 within Step 1 and add the listed tests. Rewrite the
Step 1 validation rows after the fixes: remove *Missing work for Step 1* only
when every bullet is done, and restore the Yes sentence only then. Also refresh
the document header sentence "Step 1 is implemented and validated." and the
`a.commit` group 4 body, which the reviewer did not touch.

Run the requestor-owned resolved set (`ghog day --full=speed --whole-suite`).
Pass the plan's `rg` scan as a plan validation command on the next request.
Update `a.commit` only if staged membership changes, then publish the
replacement request through the normal requestor workflow.

The reviewer repaired no implementation or test file. Its only staged change is
the attributable Step 1 validation-row patch.

### Decision rationale for step 1 release-project-root (exchange 1) (round 1)

Recommend changes-requested. The six readiness-floor results are:

1. Identity: PASS. Exact plan, step 1, round 1, occurrence 1, code identity,
   umbrella and request-time index tree agree with the live exchange.
2. Implementation completeness: FAIL. R1 (record contract) and R2 (setup no
   longer preserved under non-local `switchpy` choices) remain.
3. Validation and coverage: INCOMPLETE. Requestor speed and coverage evidence
   is green, the reviewer's focused `ghog affected --no-cov` run is green
   (3,687 tests), and the static coverage walk finds no gap. The reviewer's
   `ghog check` could not produce evidence in this shell (no checkout venv
   under the inherited `SWITCHPY_CHOICE=No venv`), so that result is missing,
   not passed.
4. Staged attribution: PASS. The sole reviewer change is the attributable
   Step 1 validation metadata; no substantive repair and no unrelated staged
   work.
5. Unresolved findings: FAIL. R1 to R5 remain open, R1 and R2 at P2.
6. `a.commit`: PASS mechanically. The independent checker reports exit 0,
   valid, ready, with all 39 paths in four accurate groups. The group 4 body
   needs a refresh after the fixes.

The implementation and unresolved-findings failures block commit-readiness,
even though the reported walks are green and the commit plan is valid.

### Final reviewer decision for step 1 release-project-root (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-1-round-1 -->

## Round 2 by requestor - Step 1

- Recorded: 2026-10-22T15:01:20+02:00
- Exchange: code/code/v0.14.0/release-project-root
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.release-project-root.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 1
- Outcome: request

### Review identity for step 1 release-project-root (round 2)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.release-project-root.md
Implementation step: 1
Review round: 2

### Code review evidence for step 1 release-project-root (round 2)

request_index_tree: 86fd35f216a40b8fbf83ead68d7ebe88468905c1
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)
- `rg -n 'VIRTUAL_ENV|PYTHONPATH|glob|rglob|import_module' tools/release_workflow` (sources: plan)
- `ghog check` (sources: request)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.release-project-root.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: docs(review): qualify duplicate headings
group 1 path: docs/v0.14.0/review.design-specification.v0.14.0.release-project-root.md
group 2: perf(tests): reuse CLI and repository initialization
group 2 path: tests/acceptance/commit_plan_check/__init__.py
group 2 path: tests/acceptance/commit_plan_check/commit_plan_check_support.py
group 2 path: tests/acceptance/commit_plan_check/conftest.py
group 2 path: tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_acceptance_tdd.py
group 2 path: tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_contracts_tdd.py
group 2 path: tests/acceptance/review_resume/__init__.py
group 2 path: tests/acceptance/review_resume/cli_support.py
group 2 path: tests/acceptance/review_resume/conftest.py
group 2 path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_acceptance_tdd.py
group 2 path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_concurrency_tdd.py
group 2 path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_identity_tdd.py
group 2 path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_parked_wait_tdd.py
group 2 path: tests/acceptance/review_status/conftest.py
group 2 path: tests/unit/tools/git_test_double.py
group 2 path: tests/unit/tools/test_code_reviewer_acceptance/fixtures.py
group 3: feat(release): validate setup-owned runtime
group 3 path: bin/release_runtime_record.bat
group 3 path: docs/v0.14.0/plan.v0.14.0.release-project-root.md
group 3 path: pyproject.toml
group 3 path: senv.bat
group 3 path: tests/acceptance/release_workflow/__init__.py
group 3 path: tests/acceptance/release_workflow/conftest.py
group 3 path: tests/acceptance/release_workflow/process_support.py
group 3 path: tests/acceptance/release_workflow/test_release_readiness_tdd.py
group 3 path: tests/acceptance/release_workflow/test_uv_readiness_tdd.py
group 3 path: tests/unit/tools/release_workflow/__init__.py
group 3 path: tests/unit/tools/release_workflow/conftest.py
group 3 path: tests/unit/tools/release_workflow/test_bootstrap/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_markers/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_markers/test_markers_pbt.py
group 3 path: tests/unit/tools/release_workflow/test_markers/test_markers_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_readiness/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_readiness/test_faults_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_readiness/test_metadata_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_readiness/test_readiness_pbt.py
group 3 path: tests/unit/tools/release_workflow/test_readiness/test_readiness_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_runtime/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_runtime/test_runtime_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_support.py
group 3 path: tools/release_workflow/__init__.py
group 3 path: tools/release_workflow/bootstrap.py
group 3 path: tools/release_workflow/markers.py
group 3 path: tools/release_workflow/readiness.py
group 3 path: tools/release_workflow/runtime_identity.py
group 3 path: uv.lock
group 4: docs(release-project-root): record step 1 validation
group 4 path: docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md
staged path: bin/release_runtime_record.bat
staged path: docs/v0.14.0/plan.v0.14.0.release-project-root.md
staged path: docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md
staged path: docs/v0.14.0/review.design-specification.v0.14.0.release-project-root.md
staged path: pyproject.toml
staged path: senv.bat
staged path: tests/acceptance/commit_plan_check/__init__.py
staged path: tests/acceptance/commit_plan_check/commit_plan_check_support.py
staged path: tests/acceptance/commit_plan_check/conftest.py
staged path: tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_acceptance_tdd.py
staged path: tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_contracts_tdd.py
staged path: tests/acceptance/release_workflow/__init__.py
staged path: tests/acceptance/release_workflow/conftest.py
staged path: tests/acceptance/release_workflow/process_support.py
staged path: tests/acceptance/release_workflow/test_release_readiness_tdd.py
staged path: tests/acceptance/release_workflow/test_uv_readiness_tdd.py
staged path: tests/acceptance/review_resume/__init__.py
staged path: tests/acceptance/review_resume/cli_support.py
staged path: tests/acceptance/review_resume/conftest.py
staged path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_acceptance_tdd.py
staged path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_concurrency_tdd.py
staged path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_identity_tdd.py
staged path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_parked_wait_tdd.py
staged path: tests/acceptance/review_status/conftest.py
staged path: tests/unit/tools/git_test_double.py
staged path: tests/unit/tools/release_workflow/__init__.py
staged path: tests/unit/tools/release_workflow/conftest.py
staged path: tests/unit/tools/release_workflow/test_bootstrap/__init__.py
staged path: tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py
staged path: tests/unit/tools/release_workflow/test_markers/__init__.py
staged path: tests/unit/tools/release_workflow/test_markers/test_markers_pbt.py
staged path: tests/unit/tools/release_workflow/test_markers/test_markers_tdd.py
staged path: tests/unit/tools/release_workflow/test_readiness/__init__.py
staged path: tests/unit/tools/release_workflow/test_readiness/test_faults_tdd.py
staged path: tests/unit/tools/release_workflow/test_readiness/test_metadata_tdd.py
staged path: tests/unit/tools/release_workflow/test_readiness/test_readiness_pbt.py
staged path: tests/unit/tools/release_workflow/test_readiness/test_readiness_tdd.py
staged path: tests/unit/tools/release_workflow/test_runtime/__init__.py
staged path: tests/unit/tools/release_workflow/test_runtime/test_runtime_tdd.py
staged path: tests/unit/tools/release_workflow/test_support.py
staged path: tests/unit/tools/test_code_reviewer_acceptance/fixtures.py
staged path: tools/release_workflow/__init__.py
staged path: tools/release_workflow/bootstrap.py
staged path: tools/release_workflow/markers.py
staged path: tools/release_workflow/readiness.py
staged path: tools/release_workflow/runtime_identity.py
staged path: uv.lock
```

### Validation scope for step 1 release-project-root (round 2)

Validation scope: the whole suite.

### Requestor assessment for step 1 release-project-root (round 2)

Step 1 is implemented against the approved plan. R1-R5 from round 1 are
accepted and repaired. Steps 2-6 remain unimplemented and outside this request.

The post-refactoring whole-suite speed day passed 3,696 tests, strict static
checks and 100% tools coverage on 2026-10-22 at 14:53:51 +02:00. The exact plan
source scan and fresh isolated setup/readiness capture also pass. After final
document edits, day reused saved speed proof and a fresh ghog check passed.
Production
modules remain within the 650-line ceiling, with explicit infrastructure
boundaries and linear lock/declaration processing. Existing setup behavior,
failure isolation and consumer immutability remain covered.

The user-requested one-second total-duration ceiling is configured and all
offenders are listed, but the ceiling is not achieved: 52 tests exceed it.
Whole-suite measured phase time fell 20.0%; focused lifecycle, parked-wait and
competing-reviewer runs fell substantially. All assertions are retained, with
real ownership pickup, public launchers, independent waiters, migration Git,
and commit-plan adapters/snapshots still exercised. Parent CLI orchestration
and repository initialization are reused. The request does not present green
call-only proof as proof of the stricter audit.

No exclusions or raised baselines were accepted. The validation document and
implementation report record the remaining performance work explicitly.
Review the repaired contracts and fixture boundaries before recommending a
human commit decision. No Step 1 commit has been authorized.

### Implementation report for step 1 release-project-root (round 2)

Successful checkout-local setup publishes the measured runtime under
`venvs/release-runtime.v1.txt`: literal UTF-8 version and relative-path lines.
One tested parse/serialize contract rejects unsupported versions, malformed
line counts and unsafe paths. Publication uses a same-directory temporary and
atomic replacement, after executable/prefix verification. Successful no-env
or global setup warns and preserves any existing record without publication.
Actual local producer failures remain failures. Both setup status temporaries
are cleared; acceptance executes the actual batch block to prove exit status
and environment cleanup.

The standalone bootstrap loads exact sibling helpers under private names,
checks the measured runtime and locked release dependencies, then imports the
engine. The release group remains empty and included from dev. Metadata,
marker grammar, graph traversal, physical containment and import-isolation
coverage remain as described in the approved Step 1. The production CLI is
assigned to Step 5; tests supply a disposable engine for the success boundary.

R1-R5 are addressed, including historical review-heading suffixes and shared
ENV test data. The plan clarification records preservation of existing setup,
already required by the approved Step 1; it does not impose local-only setup.

Fixture refactoring reuses CLI imports with a fresh runtime and restored cwd,
environment and streams. Provider identity and parent exchange orchestration
use bounded Git answers. Lifecycle ownership takeover, status/workflow launchers
and independent waiters retain real processes; migration retains real Git.
Commit-plan tests copy a real session-owned Git seed but keep real adapter
processes, Git queries and before/after immutability snapshots. All assertions
remain. Synthetic fixture commits disable signing only for that command.

Measured profile runs, including fixtures: provider identities 71.86s -> 8.78s
(earlier work); lifecycle 90.99s -> 30.17s; commit-plan parity 47.19s -> 35.71s;
parked waits 39.15s -> 8.09s; competing reviewers 16.75s -> 6.61s. These timings
do not claim individual setup phases are below one second.

The private strict 1.0s audit includes setup + call + teardown, charges shared
fixtures where they actually execute, excludes collection/interpreter startup,
and uses no exclusions. The original inventory had 49 breaches among 3687
passing tests, with 86.1% of measured phase time in setup. Groundhog's built-in
speed gate remains call-only and statistical.

Post-refactoring validation completed at 2026-10-22T14:53:51+02:00:
`ghog day --full=speed --whole-suite` exited 0, all 3,696 tests passed,
tools coverage was 100%, and no warnings, xfails, call outliers or exclusions
were reported. The separate strict audit reports 52 breaches (ceiling verdict
8); the outer PowerShell command returned 1. Total measured phases fell from
435.4594s to 348.5239s (20.0%), with setup falling from 375.0891s to 286.0789s.
Calls total 60.8390s and teardown 1.6061s. Setup still accounts for 82.1%.
This is not a claim that the one-second total-duration target is achieved.

Current full inventory and raw measurements:
`.reviews/a.release-project-root.step1.tmp.timing/above-one-second.md` and
`.reviews/a.release-project-root.step1.tmp.timing/durations.json`.
The same folder preserves baseline reports and the complete groundhog log.
The largest remaining costs are migration (19.20s/16.48s), review-status setup
(11.85s), lifecycle setup (10.57s/9.24s), and real commit-plan scenarios
(up to 9.36s). No slow setup was shifted outside measured fixture phases.

Fresh guard-clearing senv plus isolated UTF-8 readiness capture exited 0:
the two-line record names the measured checkout-local environment, the release
closure is empty, tools_imported is false, and isolated/UTF-8 flags are both 1.
Evidence: `.reviews/a.release-project-root.step1.tmp.r2.setup-evidence.txt`.
The plan source scan finds only the intended post-gate engine import and the
word global in a setup comment; neither indicates ambient runtime selection.

After final documentation edits, the exact speed day reused saved speed proof
on unchanged code/test sources. A separate fresh `ghog check` passed all
static and Markdown checks. Evidence is retained as `.tmp.r2.final-gate.log`
and `.tmp.r2.final-check.log` under the same step prefix in `.reviews`.

Accepted duration exclusions: none. Raised baselines: none.

Writer notes: `.reviews/a.release-project-root.step1.journal.md` and
`.reviews/a.release-project-root.step1.handoff.md`.

### Change summary for step 1 release-project-root (round 2)

The staged work has four ordered a.commit groups:

1. docs(review): qualify duplicate headings
2. perf(tests): reuse CLI and repository initialization
3. feat(release): validate setup-owned runtime
4. docs(release-project-root): record step 1 validation

Canonical wac formatted the plan; commit-plan-check reports ready=true,
47 staged paths, and no diagnostics. Both staged and worktree whitespace
checks pass with CRLF-aware settings. The lock clean filter was retained.

Current staged paths:

- `bin/release_runtime_record.bat`
- `docs/v0.14.0/plan.v0.14.0.release-project-root.md`
- `docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md`
- `docs/v0.14.0/review.design-specification.v0.14.0.release-project-root.md`
- `pyproject.toml`
- `senv.bat`
- `tests/acceptance/commit_plan_check/__init__.py`
- `tests/acceptance/commit_plan_check/commit_plan_check_support.py`
- `tests/acceptance/commit_plan_check/conftest.py`
- `tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_acceptance_tdd.py`
- `tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_contracts_tdd.py`
- `tests/acceptance/release_workflow/__init__.py`
- `tests/acceptance/release_workflow/conftest.py`
- `tests/acceptance/release_workflow/process_support.py`
- `tests/acceptance/release_workflow/test_release_readiness_tdd.py`
- `tests/acceptance/release_workflow/test_uv_readiness_tdd.py`
- `tests/acceptance/review_resume/__init__.py`
- `tests/acceptance/review_resume/cli_support.py`
- `tests/acceptance/review_resume/conftest.py`
- `tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_acceptance_tdd.py`
- `tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_concurrency_tdd.py`
- `tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_identity_tdd.py`
- `tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_parked_wait_tdd.py`
- `tests/acceptance/review_status/conftest.py`
- `tests/unit/tools/git_test_double.py`
- `tests/unit/tools/release_workflow/__init__.py`
- `tests/unit/tools/release_workflow/conftest.py`
- `tests/unit/tools/release_workflow/test_bootstrap/__init__.py`
- `tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py`
- `tests/unit/tools/release_workflow/test_markers/__init__.py`
- `tests/unit/tools/release_workflow/test_markers/test_markers_pbt.py`
- `tests/unit/tools/release_workflow/test_markers/test_markers_tdd.py`
- `tests/unit/tools/release_workflow/test_readiness/__init__.py`
- `tests/unit/tools/release_workflow/test_readiness/test_faults_tdd.py`
- `tests/unit/tools/release_workflow/test_readiness/test_metadata_tdd.py`
- `tests/unit/tools/release_workflow/test_readiness/test_readiness_pbt.py`
- `tests/unit/tools/release_workflow/test_readiness/test_readiness_tdd.py`
- `tests/unit/tools/release_workflow/test_runtime/__init__.py`
- `tests/unit/tools/release_workflow/test_runtime/test_runtime_tdd.py`
- `tests/unit/tools/release_workflow/test_support.py`
- `tests/unit/tools/test_code_reviewer_acceptance/fixtures.py`
- `tools/release_workflow/__init__.py`
- `tools/release_workflow/bootstrap.py`
- `tools/release_workflow/markers.py`
- `tools/release_workflow/readiness.py`
- `tools/release_workflow/runtime_identity.py`
- `uv.lock`

Round 2 includes all accepted R1-R5 repairs and further fixture optimization.
The generated code-review transcript evolves through exchange publication and
remains outside this prepared index; the authorized residual workflow owns it.
No commit has been performed or authorized.

### Human guidance and writer response for step 1 release-project-root (round 2)

Human guidance:

Implement and review Step 1 only. Preserve the approved setup behavior and
the runtime-file contract. Do not advance to Step 2 or commit without the
human's final choice.

The user asked to configure a one-second ceiling and list tests exceeding it.
The private audit uses setup + call + teardown, strict greater-than 1.0,
no exclusions, sequential execution and no coverage. The baseline listed
49 breaches; the refreshed inventory has 52 among 3,696 passing tests, while
total measured phase time fell 20.0%. Assess the timing evidence with that scope;
the existing groundhog speed gate remains a call-only statistical gate.

Retain test assertions and necessary real process/Git boundary coverage.
Lifecycle pickup and public launchers, independent waiters, migration Git and
commit-plan adapter/snapshot behavior must remain meaningful. Do not read a
green call-only groundhog result as proof that the total-duration ceiling passes.

Writer response:

All five round 1 findings are accepted; no reviewer repair was reversed.

- R1: Replace the JSON record with `venvs/release-runtime.v1.txt`. Its two
  UTF-8 lines are version `1` and the checkout-relative environment path.
  Parsing and serialization share one tested contract, including literal
  Unicode, CRLF input, malformed line counts and unsupported versions.
- R2: Preserve successful no-environment and global-environment setup with a
  warning and no publication. The approved plan already requires preservation
  of existing setup; its Step 1 prose now makes these cases explicit. Actual
  local producer failures still fail setup. Existing designation bytes remain
  unchanged when publication is skipped.
- R3: Clear both setup status variables after use while preserving setup and
  producer failures. The acceptance fixture executes the actual setup block
  with small collaborators and asserts success, failure status and cleanup.
- R4: Keep the historical design-review heading discriminator before the
  final `(round N)` suffix, without changing review content.
- R5: Move shared `ENV` data to `test_support.py` and update its consumers.

The reviewer's staged validation metadata was accepted. The writer refreshes
it only after validating the repairs. The request's executable validation set
now includes the plan's source scan.

The latest human steering adds a one-second total-duration audit. It measured
49 breaches among 3,687 passing tests; setup accounts for 86.1% of phase time.
This private audit is separate from the existing groundhog call-only gate.
Its inventory does not claim that all suite fixture costs have been fixed.

Further measured fixture work preserves every assertion:

| Target | Before | After | Retained boundaries |
| --- | ---: | ---: | --- |
| Lifecycle module, 12 tests | 90.99s | 30.17s | Fresh-process ownership pickup and real status/workflow launchers |
| Commit-plan parity, 5 tests | 47.19s | 35.71s | All real module/launcher adapters and Git snapshots |
| Parked waits, 2 tests | 39.15s | 8.09s | Independent waiter with real Git and filesystem |
| Competing reviewers, 1 test | 16.75s | 6.61s | Two independent real CLI/Git processes and ownership race |

These are whole pytest runs under the same profiling setup, including fixtures.
Lifecycle setup itself fell from 83.18s combined to 21.19s; commit-plan setup
fell from 38.17s to 35.44s. Real Git snapshot and adapter costs still dominate
the latter. Process startup and cleanup also contribute to whole-run time.
No assertion was removed, no threshold raised and no exclusion introduced.
The fresh full-suite inventory supersedes the baseline: 3,696 tests pass with
100% tools coverage, but 52 exceed the total-duration ceiling. Measured phases
fall from 435.46s to 348.52s; setup falls from 375.09s to 286.08s. The complete
list is `.reviews/a.release-project-root.step1.tmp.timing/above-one-second.md`.
The groundhog speed proof passes; the separate one-second audit fails. Further
optimization remains visible rather than treated as an accepted exclusion.

### Reviewer focus for step 1 release-project-root (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-1-round-2 -->

## Round 2 by reviewer - Step 1

- Recorded: 2026-10-22T15:23:22+02:00
- Exchange: code/code/v0.14.0/release-project-root
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.release-project-root.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 1
- Outcome: answer

### Assessed index identity for step 1 release-project-root (exchange 1) (round 2)

Baseline index tree: 86fd35f216a40b8fbf83ead68d7ebe88468905c1

Assessed index tree: 505add891ebfef119dd009dc5c725c7d0565c6f0

### Implementation check for step 1 release-project-root (exchange 1) (round 2)

Result:

Result:

No. Step 1 has NOT been fully implemented.

The five round 1 findings are fixed. The producer writes the planned two-line
`venvs/release-runtime.v1.txt` through one parse/serialize contract.
Successful no-environment and global setup finish with a warning and publish
nothing. `senv.bat` clears both status temporaries. The historical headings end
with `(round N)`, and `ENV` lives in `test_support.py`. Two gaps keep Step 1
open. The new checkout-local test in the producer mixes path forms (R6), and two
of Step 1's own acceptance tests exceed the user's one-second total-duration
ceiling (R7). The exact Step 1 validation rows now say No and list this work
under *Missing work for Step 1*.

R1 to R5 checked against the round 2 diff from the round 1 assessed tree
`481412fd…` to `86fd35f2…`:

- R1: `RECORD_NAME = "release-runtime.v1.txt"`. `serialize()` writes
  `1\n<relative>\n` with literal UTF-8, and `publish()` writes with
  `newline="\n"`. `parse()` accepts CRLF and rejects wrong line counts, a
  version other than `1`, and unsafe paths. The new unit cases include
  `préparé 日本`, CRLF input, `True` and `1.0` version lines, and extra or
  missing lines. The checkout's own record holds two lines naming its venv.
- R2: `bin/release_runtime_record.bat` warns and returns 0 when `VIRTUAL_ENV`
  is undefined. `main()` warns and returns 0 when `sys.prefix` is not under
  `<root>\venvs`, and a nonzero setup status still propagates. The plan's
  Step 1 framing now states this. That matches the round 2 guidance to
  preserve the approved setup behavior, and it is the behavior recommended in
  round 1. This review's `ghog check` preamble shows senv finishing with
  `Environment initialized` and the hook check.
- R3: both variables are cleared on the success and failure paths. Inside the
  parenthesized block, `exit /b %RELEASE_RUNTIME_STATUS%` is expanded when the
  block is parsed, so the status survives the earlier `set`. The new acceptance
  test runs the real senv block and covers success, setup failure and producer
  failure.
- R4: both headings end with `(round 2)` and `(round 3)`, and the Markdown
  gate passes.
- R5: four consumers now import `ENV` from `test_support.py`.

R6: `tools/release_workflow/runtime_identity.py:143-148` compares
`Path(sys.prefix).absolute()` with `Path(arguments[0]).resolve() / "venvs"`.
One side is resolved and the other is not. `sys.prefix` keeps the path form
used to start the interpreter, so on a checkout reached through an 8.3 name,
a directory junction or a `subst` drive, the checkout's own venv fails the
test. `main()` prints "no checkout-local environment prepared", returns 0 and
publishes nothing. That contradicts the plan's new Step 1 sentence that a
producer failure for a checkout-local environment still fails setup. It also
breaks the Step 1 outcome that a fresh successful setup produces one usable
identity. I reproduced it read-only by starting this checkout's venv Python
through the 8.3 short form of its path. `sys.prefix` kept the short form,
the current test returned `False`, and a test with both paths in the same
lexical form returned `True`. `measure()` already resolves both paths for the
physical containment checks, so a lexical-to-lexical first test keeps the
junction-escape failure intact.

R7: the human guidance asks for timing evidence assessed against the
one-second total-duration ceiling. The private audit lists 52 breaches. Two
are Step 1 tests:

- `test_setup_entry[success-0]`: 4.09s, all in the module-scoped `processes`
  fixture. It was 2.80s in the baseline; the round 2 setup-cleanup scenarios
  joined the same fixture.
- `test_uv_generated_empty_shapes`: 2.94s.

The other 50 are in suites outside Step 1 and are listed under
boundary-crossing work.

Plan conformance, unchanged since round 1 and rechecked where touched:

- saved `switchpy` status is passed before `popd`;
- the producer runs `%VIRTUAL_ENV%\Scripts\python.exe -I -X utf8`, never bare
  `python`;
- publication is atomic in the same directory;
- the empty `release` group is included by `dev`;
- helpers load by exact sibling path, and the root is inserted only after
  readiness;
- the closed lock and marker contracts are unchanged.

The plan's
`rg -n 'VIRTUAL_ENV|PYTHONPATH|glob|rglob|import_module' tools/release_workflow`
scan is now in the resolved set as a plan command. Only the requestor ran it,
and the requestor reports only the intended post-gate `import_module` and the
word `global` in a comment.

Architecture: no change since round 1 apart from the producer's new
non-local branch, which stays in the infrastructure entry point. Largest new
module: `readiness.py`, 195 lines. No layer violation and no file over 650
lines.

Performance: production code is unchanged in complexity. The test-side issue is
R7.

Static coverage: `[tool.coverage.run] source = ["tools"]` measures the
changed `runtime_identity.py`. The new `parse`, `serialize` and non-local
`main()` branch are exercised by `test_non_ascii_environment_roundtrip`,
`test_invalid_records_fail` and `test_global_setup_preserves_record`. That is
consistent with the requestor's reported 100%. No test covers either side of
the R6 rule.

Feature integrity: setup under all three `switchpy` choices finishes again,
except in the R6 layouts. The fixture refactor removes no assertion, test or
marker. The staged diff of the 15 group 2 files adds or removes no `assert`
line, and no `skip`, `xfail` or exclusion was added.

Validation plan effects:

Changed only Step 1 rows in
`docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md`:

- *Analysis of Step 1 implementation state* now opens with the exact No
  sentence and a short rationale. The writer's `Yes, Step 1 is implemented.`
  was not one of the two permitted sentences.
- *Missing work for Step 1* now lists R6 and the R7 tests as concrete bullets,
  replacing a "no gap" note that contradicted the open audit.
- *What was implemented for Step 1* gains one sentence with the reviewer's
  round 2 evidence.
- *Performance check for Step 1* now ends with its Yes phrase for the
  total-duration ceiling.
- *Feature integrity for Step 1* records the R6 layout impairment.

The document-level opening line stays `No, it is not implemented`. The header
sentences are outside the Step 1 rows and were left for the writer. Other
steps, the plan, the umbrella, implementation, tests and `a.commit` were not
edited.

The evidence launcher attributed the patch against the pre-edit blob
`cd7bd22a790798a42f3d6cc2a0cf7ffa3e4c99c4` (attributable, not created). Only
that patch was staged. The project Markdown check passes after the edit. This
is review metadata, not a substantive repair.

### Pre-repair mandatory checks and coverage for step 1 release-project-root (exchange 1) (round 2)

Requestor evidence: `ghog day --full=speed --whole-suite` completed on
2026-10-22 at 14:53:51 +02:00 with exit 0, `proof=speed`, full-stage
`cov=100`, 3,696 timed tests, and no failures, warnings, xfails, outliers or
exclusions. A later run reused the saved speed proof after documentation edits,
and a fresh `ghog check` passed. The requestor's separate strict
total-duration audit reports 52 tests above 1.0s. This is reported evidence
and was not repeated.

Reviewer evidence, each command run once from the project root through the
shared `ghog.bat` launcher, with the log-freshness proof and
`SWITCHPY_CHOICE=local` set for that process only:

- `ghog check`: exit 0. All static, EOF and Markdown checks passed. The senv
  preamble shows the checkout venv activated, `Environment initialized`, and
  the sensitive-hook check.
- `ghog affected --no-cov --scope-file=.reviews/a.review-scope.code.v0.14.0.release-project-root.json`:
  exit 0, scope whole, 3,696 tests, `fail=0 warn=0 xfail=0`.

The reviewer did not run `ghog day`, `ghog full`, the strict audit or any
coverage measurement. Coverage was assessed statically. These green runs say
nothing about the total-duration ceiling.

### Resolved validation set and sources for step 1 release-project-root (exchange 1) (round 2)

The request and the current resolver produce the same ordered set:

1. `ghog day --full=speed --whole-suite`: source project.
2. `rg -n 'VIRTUAL_ENV|PYTHONPATH|glob|rglob|import_module' tools/release_workflow`:
   source plan.
3. `ghog check`: source request.

No `.review-validation` file exists, so the project default is the built-in
`ghog day --full=speed`, completed with the bound `--whole-suite` selector for
scope `whole`. The plan scan now arrives as a plan command, as round 1 asked.
The comparison ran `resolve_code_review_validation` from the current
`tools/code_review_validation.py` with those inputs. The reviewer did not run
the resolved set; its own `ghog check` run is reviewer evidence, listed below.

### Resolver drift and direction for step 1 release-project-root (exchange 1) (round 2)

None: ordered commands and source labels agree with the current resolver.

### Repository state around validation for step 1 release-project-root (exchange 1) (round 2)

Request-time and reviewer baseline index tree:
`86fd35f216a40b8fbf83ead68d7ebe88468905c1` (identical). Final assessed index
tree after the reviewer metadata patch: `505add891ebfef119dd009dc5c725c7d0565c6f0`.

The same ordered 49-path validation set was captured before and after
assessment: the 47 staged paths plus the ignored `a.ghog.log` and
`a.ghog.status`. Tracked differences appear only for
`docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md` and `<index>`.
Ignored differences appear only for the two ghog files written by the
reviewer's evidence commands, and there are no untracked differences. The raw
`acceptable=false` reflects the intentional Step 1 metadata edit; the
attribution shows that every changed hunk lies in the Step 1 rows. There is no
tracked validation side effect and no overlap with writer work. The only other
working-tree entry is the untracked exchange transcript, which the protocol
owns.

Umbrella `docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md`: applicable,
digest `ca6fe473…0ec992` before and after, unchanged. No umbrella row was
modified.

Retained evidence: `.reviews/a.code-review-evidence.v0.14.0.release-project-root.step-1.json`,
with the inputs under `.reviews/a.release-project-root.step1.tmp.r2.*`.

### Repair inventory for step 1 release-project-root (exchange 1) (round 2)

Repairs made:

- Review metadata only: rewrote the Step 1 validation rows to the exact No
  sentence, replaced *Missing work for Step 1* with R6 and R7 bullets, and
  added the performance and feature-integrity conclusions. No implementation,
  test, plan or `a.commit` repair.

Paths staged:

- docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md (reviewer metadata patch only)

### Commit plan assessment for step 1 release-project-root (exchange 1) (round 2)

Ran `commit-plan-check.bat --format json` independently before assessment and
again after staging the Step 1 metadata. Both returned exit 0, `state=valid`,
`ready=true`, four ordered groups, 47 staged paths and no diagnostics. The JSON
is retained in `.reviews/a.release-project-root.step1.tmp.r2.review-commit-plan.json`
and `.reviews/a.release-project-root.step1.tmp.r2.review-commit-plan-after.json`.

Ordered groups:

1. `docs(review): qualify duplicate headings` (1 path)
2. `perf(tests): reuse CLI and repository initialization` (15 paths)
3. `feat(release): validate setup-owned runtime` (30 paths)
4. `docs(release-project-root): record step 1 validation` (1 path)

Membership, order and conventional subjects match the staged work, so the
reviewer did not amend `a.commit`. Group 3 carries the plan clarification with
the feature it describes, which fits. One body is now stale: group 4 says "The
runtime foundation and its validation evidence now satisfy Step 1", which the
staged validation rows no longer claim. The writer should rewrite it together
with the R6 and R7 fixes. Mechanical readiness does not resolve the findings
and does not authorize a commit.

### Findings and boundaries for step 1 release-project-root (exchange 1) (round 2)

Unresolved findings:

- R6 (P3): classify a checkout-local environment with both paths in the same
  form. `tools/release_workflow/runtime_identity.py:143-148` tests
  `Path(sys.prefix).absolute().is_relative_to(Path(arguments[0]).resolve() / "venvs")`.
  `sys.prefix` keeps the path form the interpreter was started with, but the
  root is resolved. On a checkout reached through an 8.3 name, a directory
  junction or a `subst` drive, the checkout's own venv fails the test. Setup
  then warns "no checkout-local environment prepared", returns 0 and never
  publishes a record. That contradicts the plan's new Step 1 sentence ("A
  producer failure for a checkout-local environment still fails setup") and
  the Step 1 outcome. Reproduced read-only through this checkout's 8.3 short
  path: `False` with the current test, `True` with both sides lexical. Compare
  `Path(sys.prefix).absolute()` with `Path(arguments[0]).absolute() / "venvs"`
  and leave the physical checks to `measure()`, which resolves both paths.
  Add two producer tests. In the first, the same checkout given through
  another lexical form, such as a junction or a patched `resolve` alias,
  publishes the record. In the second, a prefix lexically under `venvs` that
  physically escapes through a junction returns 2 and publishes nothing. That
  second case backs the code comment's claim, which no producer-level test
  covers today.
- R7 (P3): bring Step 1's own acceptance tests under the user's one-second
  total-duration ceiling (setup + call + teardown). The private audit charges
  `tests/acceptance/release_workflow/test_release_readiness_tdd.py::test_setup_entry[success-0]`
  4.09s, all module-fixture setup. It was 2.80s in the baseline audit; the
  round 2 setup-cleanup scenarios were added to the same `processes` fixture.
  It also charges
  `tests/acceptance/release_workflow/test_uv_readiness_tdd.py::test_uv_generated_empty_shapes`
  2.94s. Split the process matrix into smaller fixtures per scenario group, so
  that no single test is charged every launch. Keep each real `cmd`, Python,
  junction and uv process and every assertion. Measure each uv shape
  separately. If one real `uv lock` run alone stays above one second, report
  that number for the human's decision instead of excluding the test.

Boundary-crossing work:

- The other 50 total-duration breaches are in suites outside Step 1:
  review-resume migration (19.20s and 16.48s), review-status setup (11.85s),
  review lifecycle (10.57s and 9.24s), commit-plan contracts (up to 9.36s),
  and the blocked-layout, markdown, prompt-workflow and code-review evidence
  modules. The human decides whether the one-second ceiling must pass for the
  whole suite before the Step 1 commit, or moves to a separate effort. The
  reviewer did not treat them as Step 1 missing work.

### Human guidance response for step 1 release-project-root (exchange 1) (round 2)

Human guidance:

Implement and review Step 1 only. Preserve the approved setup behavior and
the runtime-file contract. Do not advance to Step 2 or commit without the
human's final choice.

The user asked to configure a one-second ceiling and list tests exceeding it.
The private audit uses setup + call + teardown, strict greater-than 1.0,
no exclusions, sequential execution and no coverage. The baseline listed
49 breaches; the refreshed inventory has 52 among 3,696 passing tests, while
total measured phase time fell 20.0%. Assess the timing evidence with that scope;
the existing groundhog speed gate remains a call-only statistical gate.

Retain test assertions and necessary real process/Git boundary coverage.
Lifecycle pickup and public launchers, independent waiters, migration Git and
commit-plan adapter/snapshot behavior must remain meaningful. Do not read a
green call-only groundhog result as proof that the total-duration ceiling passes.

Guidance response:

The guidance sets review scope and does not instruct a reviewer repair, so the
reviewer changed no implementation, test or plan file. The request's general
"make every safe repair" wording does not override that rule.

Scope: the staged work stays within Step 1 and the requested test
optimization. Nothing from Step 2 was found. This answer authorizes no commit.

Setup behavior and the runtime-file contract: R1 now follows the plan's
`venvs/release-runtime.v1.txt` line contract. R2 preserves successful
no-environment and global setup, as the guidance asks, and the plan sentence
states it. R6 is the remaining gap in that preservation work. The new local
test misclassifies a checkout reached through another path form.

Timing evidence, assessed as total duration: the audit inventory lists 52
tests above 1.0s among 3,696 passing tests, and its method matches the
guidance. The reviewer did not take the green call-only speed gate, or its own
green `ghog affected` run, as proof that the ceiling passes. Two breaches
belong to Step 1's own fixtures (R7), and one of them grew this round. The
other 50 are listed as boundary-crossing work for the human.

Boundaries and assertions:

- The 15 group 2 files add or remove no `assert` line.
- No test function was removed, and no `skip`, `xfail` or exclusion was added.
- Lifecycle ownership pickup runs in a fresh process.
- `rvw_status.bat` and `prompt_workflow.bat` still run through their batch
  launchers.
- The competing-reviewer race and the parked wait keep independent real CLI
  processes with real Git.
- Migration keeps real Git.
- Commit-plan scenarios copy a real committed seed per test and keep the real
  adapters and Git snapshots.

One narrowing to note: the rest of the lifecycle orchestration now runs in
process with the bounded Git double, where round 1 ran all of it in separate
processes. The guidance names exactly the boundaries that remain, so the
reviewer accepts this.

### Writer instructions for step 1 release-project-root (exchange 1) (round 2)

Fix R6 and R7 within Step 1 and add the listed tests. Ask the human about
the 50 breaches outside Step 1 listed under boundary-crossing work.

Rewrite the Step 1 validation rows after the fixes. The *Analysis* section
must open with one of the two exact sentences, `Yes. Step 1 has been fully
implemented.` or `No. Step 1 has NOT been fully implemented.`. Round 2's
`Yes, Step 1 is implemented.` is not an accepted form. A Yes result removes
*Missing work for Step 1*; do not keep that section with a "no gap" note.
Also refresh three texts the reviewer did not touch:

- the document header sentences;
- the `a.commit` group 4 body, which still says the runtime foundation
  satisfies Step 1;
- the group 3 body, if the R7 split changes what it describes.

Run the requestor-owned resolved set: `ghog day --full=speed --whole-suite`,
the plan's `rg` scan and `ghog check`. Re-run the strict total-duration audit
and report its new count. Update `a.commit` only if staged membership changes,
then publish the replacement request through the normal requestor workflow.

The reviewer repaired no implementation or test file. Its only staged change is
the attributable Step 1 validation-row patch.

### Decision rationale for step 1 release-project-root (exchange 1) (round 2)

Recommend changes-requested. The six readiness-floor results are:

1. Identity: PASS. The exact plan, step 1, round 2, occurrence 1, code
   identity, umbrella and request-time index tree agree with the live exchange.
2. Implementation completeness: FAIL. R6 (checkout-local classification) and
   R7 (Step 1 tests above the total-duration ceiling) remain.
3. Validation and coverage: FAIL on the user's total-duration ceiling only.
   The requestor's speed day and 100% coverage, the reviewer's `ghog check`
   and the reviewer's `ghog affected --no-cov` run (3,696 tests) are all green,
   and the static coverage walk finds no gap in the changed module. The strict
   audit the guidance asks to assess is red: 52 breaches, two of them in
   Step 1.
4. Staged attribution: PASS. The sole reviewer change is the attributable
   Step 1 validation metadata. There is no substantive repair and no unrelated
   staged work.
5. Unresolved findings: FAIL. R6 and R7 remain open, both P3. R1 to R5 are
   resolved.
6. `a.commit`: PASS mechanically. The independent checker reports exit 0,
   valid, ready, with all 47 paths in four accurate groups. The group 4 body
   needs a refresh.

Completeness and the open findings block commit-readiness, even though every
groundhog walk is green and the commit plan is valid. Round 2 made real
progress. Both remaining items are small and stay within Step 1, apart from
the 50 breaches outside it, which the human decides on.

### Final reviewer decision for step 1 release-project-root (exchange 1) (round 2)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-1-round-2 -->

## Round 3 by requestor - Step 1

- Recorded: 2026-10-22T20:53:17+02:00
- Exchange: code/code/v0.14.0/release-project-root
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.release-project-root.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 1
- Outcome: request

### Review identity for step 1 release-project-root (round 3)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.release-project-root.md
Implementation step: 1
Review round: 3

### Code review evidence for step 1 release-project-root (round 3)

request_index_tree: d16ed32710fc19d830135f98a2c29ac8d5eaff20
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)
- `rg -n 'VIRTUAL_ENV|PYTHONPATH|glob|rglob|import_module' tools/release_workflow` (sources: plan)
- `ghog check` (sources: request)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.release-project-root.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: docs(review): qualify duplicate headings
group 1 path: docs/v0.14.0/review.design-specification.v0.14.0.release-project-root.md
group 2: perf(tests): reuse CLI and repository initialization
group 2 path: tests/acceptance/commit_plan_check/__init__.py
group 2 path: tests/acceptance/commit_plan_check/commit_plan_check_support.py
group 2 path: tests/acceptance/commit_plan_check/conftest.py
group 2 path: tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_acceptance_tdd.py
group 2 path: tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_contracts_tdd.py
group 2 path: tests/acceptance/review_resume/__init__.py
group 2 path: tests/acceptance/review_resume/cli_support.py
group 2 path: tests/acceptance/review_resume/conftest.py
group 2 path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_acceptance_tdd.py
group 2 path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_concurrency_tdd.py
group 2 path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_identity_tdd.py
group 2 path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_parked_wait_tdd.py
group 2 path: tests/acceptance/review_status/conftest.py
group 2 path: tests/unit/tools/git_test_double.py
group 2 path: tests/unit/tools/test_code_reviewer_acceptance/fixtures.py
group 3: feat(release): validate setup-owned runtime
group 3 path: bin/release_runtime_record.bat
group 3 path: docs/v0.14.0/plan.v0.14.0.release-project-root.md
group 3 path: pyproject.toml
group 3 path: senv.bat
group 3 path: tests/acceptance/release_workflow/__init__.py
group 3 path: tests/acceptance/release_workflow/conftest.py
group 3 path: tests/acceptance/release_workflow/process_support.py
group 3 path: tests/acceptance/release_workflow/test_release_readiness_tdd.py
group 3 path: tests/acceptance/release_workflow/test_uv_readiness_tdd.py
group 3 path: tests/unit/tools/release_workflow/__init__.py
group 3 path: tests/unit/tools/release_workflow/conftest.py
group 3 path: tests/unit/tools/release_workflow/test_bootstrap/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_markers/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_markers/test_markers_pbt.py
group 3 path: tests/unit/tools/release_workflow/test_markers/test_markers_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_readiness/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_readiness/test_faults_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_readiness/test_metadata_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_readiness/test_readiness_pbt.py
group 3 path: tests/unit/tools/release_workflow/test_readiness/test_readiness_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_runtime/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_runtime/test_runtime_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_support.py
group 3 path: tools/release_workflow/__init__.py
group 3 path: tools/release_workflow/bootstrap.py
group 3 path: tools/release_workflow/markers.py
group 3 path: tools/release_workflow/readiness.py
group 3 path: tools/release_workflow/runtime_identity.py
group 3 path: uv.lock
group 4: docs(release-project-root): record step 1 validation
group 4 path: docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md
staged path: bin/release_runtime_record.bat
staged path: docs/v0.14.0/plan.v0.14.0.release-project-root.md
staged path: docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md
staged path: docs/v0.14.0/review.design-specification.v0.14.0.release-project-root.md
staged path: pyproject.toml
staged path: senv.bat
staged path: tests/acceptance/commit_plan_check/__init__.py
staged path: tests/acceptance/commit_plan_check/commit_plan_check_support.py
staged path: tests/acceptance/commit_plan_check/conftest.py
staged path: tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_acceptance_tdd.py
staged path: tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_contracts_tdd.py
staged path: tests/acceptance/release_workflow/__init__.py
staged path: tests/acceptance/release_workflow/conftest.py
staged path: tests/acceptance/release_workflow/process_support.py
staged path: tests/acceptance/release_workflow/test_release_readiness_tdd.py
staged path: tests/acceptance/release_workflow/test_uv_readiness_tdd.py
staged path: tests/acceptance/review_resume/__init__.py
staged path: tests/acceptance/review_resume/cli_support.py
staged path: tests/acceptance/review_resume/conftest.py
staged path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_acceptance_tdd.py
staged path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_concurrency_tdd.py
staged path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_identity_tdd.py
staged path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_parked_wait_tdd.py
staged path: tests/acceptance/review_status/conftest.py
staged path: tests/unit/tools/git_test_double.py
staged path: tests/unit/tools/release_workflow/__init__.py
staged path: tests/unit/tools/release_workflow/conftest.py
staged path: tests/unit/tools/release_workflow/test_bootstrap/__init__.py
staged path: tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py
staged path: tests/unit/tools/release_workflow/test_markers/__init__.py
staged path: tests/unit/tools/release_workflow/test_markers/test_markers_pbt.py
staged path: tests/unit/tools/release_workflow/test_markers/test_markers_tdd.py
staged path: tests/unit/tools/release_workflow/test_readiness/__init__.py
staged path: tests/unit/tools/release_workflow/test_readiness/test_faults_tdd.py
staged path: tests/unit/tools/release_workflow/test_readiness/test_metadata_tdd.py
staged path: tests/unit/tools/release_workflow/test_readiness/test_readiness_pbt.py
staged path: tests/unit/tools/release_workflow/test_readiness/test_readiness_tdd.py
staged path: tests/unit/tools/release_workflow/test_runtime/__init__.py
staged path: tests/unit/tools/release_workflow/test_runtime/test_runtime_tdd.py
staged path: tests/unit/tools/release_workflow/test_support.py
staged path: tests/unit/tools/test_code_reviewer_acceptance/fixtures.py
staged path: tools/release_workflow/__init__.py
staged path: tools/release_workflow/bootstrap.py
staged path: tools/release_workflow/markers.py
staged path: tools/release_workflow/readiness.py
staged path: tools/release_workflow/runtime_identity.py
staged path: uv.lock
```

### Validation scope for step 1 release-project-root (round 3)

Validation scope: the whole suite.

### Requestor assessment for step 1 release-project-root (round 3)

No. Step 1 has NOT been fully implemented.

The runtime behavior and R6 producer correction are implemented. R1-R5 remain
resolved. R7's process matrix is split into complete per-scenario fixtures,
and each actual offline UV lock shape now has its own test. Assertions and
required real processes remain intact. The final full audit lists two Step 1
tests above the unchanged one-second total-duration ceiling: the real UV lock
shapes at 1.8040s and 1.9385s. All process scenarios fall below 0.630s,
including missing engine at 0.5580s. The human authorized further optimization
and Round 3 publication. Additional startup experiments found no sub-second
solution; this assessment does not accept an exception or claim R7 resolved.

Functional evidence: the final full speed day passed 3,699 tests, strict
checks and 100% tools coverage with no failures, warnings, xfails, call
outliers or exclusions. Fresh setup explicitly exited 0 and captured the
measured local runtime, valid two-line record, empty closure and isolated
UTF-8 flags with tools absent before the gate. Focused tests after the
interpreter hard-link change and its fresh whole-suite coverage/speed run pass.
The plan source scan and CRLF-aware whitespace checks pass. A fresh ghog check
passed after final tracked documentation changes. Canonical wac and
commit-plan-check pass with ready=true, 47 staged paths and no diagnostics.

Architecture and feature integrity: the lexical producer classification still
delegates physical containment to RuntimeIdentity.measure; no production layer,
dependency, complexity or import-boundary change was introduced. All new
production files remain within the line budget. No assertion, process boundary,
skip, xfail or duration exclusion was removed or added to hide costs.

The human authorized separate tracking of breaches outside Step 1. Those
remain in the complete inventory but do not block this step. That decision
does not authorize an exception for its own UV tests. No commit or Step 2
work is authorized. The final audit lists 50 breaches in total, with 48
outside Step 1, and 371.5959s total phases. No exclusion is configured.

### Implementation report for step 1 release-project-root (round 3)

Step 1 produces an authoritative setup-owned runtime identity and validates
the runtime, interpreter requirements and locked release closure before engine
import. The record remains two literal UTF-8 lines (version and relative
environment path). Publication is atomic, physical containment is enforced,
and successful no-environment/global setup preserves any prior record without
publishing. Local producer failures propagate and setup temporaries are cleared.

Round 3 corrects the producer's early locality classification: the checkout
root and prefix are compared in the same lexical form, with physical checks
still owned by RuntimeIdentity.measure. Producer regressions cover alias
success and a lexically local prefix that physically escapes and fails closed.

Bootstrap still loads fixed helper files before any package import, then checks
the release lock closure using the approved marker/version grammar. The
stdlib-only release group is included by dev. The production CLI remains Step
5 work; acceptance uses its disposable engine probe and proves missing-engine
failure. No new production dependency or Step 2 work was introduced.

The process fixture now prepares and launches only the scenario requested by
each test. Successful production starts without a record; consumers and failure
paths seed prior record data. Setup-cleanup cases still execute the actual
senv preparation block. Real cmd/Python launches, the junction escape, isolated
import checks, unchanged consumer snapshots and every assertion remain.

Profiling the old shared matrix charged 4.34s setup to the first success test.
The new success setup measured 0.59s; the maximum scenario setup was 0.79s.
The complete 13-test readiness module passed in 5.89s. The earlier 4.91s run
selected one test but executed the whole shared matrix; these whole-run totals
are not an aggregate before/after comparison.

The latest completed full audit subsequently measured missing-engine setup
at 5.5625s. Its isolated profile measured 0.86s setup with 0.7850s in the
child process. A child trace measured 0.5651s total process time and 0.2750s
inside imports/bootstrap, with only 0.0165s fixture preparation. The fixture
now links the immutable interpreter redirector instead of copying it anew,
falling back to copying across unsupported volumes. The separate real
isolated process and all checks remain. Isolated setup after the change was
0.77s; focused groundhog passes. The final full audit totals 0.5580s for
missing engine, 0.5741s for the producer, and below 0.630s for every process
scenario. The earlier 5.5625s observation remains in the retained snapshot.

The two offline UV lock shapes now have independent parametrized fixtures and
tests. Both retain actual UV invocation, generated metadata-shape checks and
empty-release readiness assertions. Combined setup was 2.69s; independent
shapes measured 1.33s and 1.39s. Explicit interpreter selection was slower and
was reverted. Trace evidence placed UV's first output at 1.545s, resolution at
5ms and process exit at 1.565s; smaller worker pools did not improve startup.
No initialization moved outside measured fixtures and no host settings changed.

The user then authorized another optimization attempt and Round 3 publication.
The executable is native UV, not a Python shim. A `uv --version` diagnostic
measured 0.9121s in subprocess creation and 0.0570s executing the child.
Suppressing the console measured 0.9329s creation plus 0.1314s execution.
A fixture-local hard link to the same executable measured 0.9083s creation
plus 0.0511s execution; its own setup cost was 0.0003s. A cmd launch merely
moved the wait into the child (0.0319s creation plus 1.0392s execution).
Removing inherited UV settings did not improve the version probe (0.9660s
versus 0.9546s total). A real no-dev-edge lock with isolated UV/certificate
settings still took 1.7952s, including interpreter discovery. These are
diagnostic subprocess measurements, not fresh pytest totals. None justified
a production fixture change. The retained full audit remains authoritative;
no repeated unchanged suite run was used to gamble away a timing failure.

Earlier fixture improvements remain: provider identities 71.86s to 8.78s,
lifecycle 90.99s to 30.17s, commit-plan parity 47.19s to 35.71s, parked waits
39.15s to 8.09s and competing reviewers 16.75s to 6.61s. Parent orchestration
reuses imports and bounded Git answers. Real ownership pickup, public launchers,
independent waiters, migration Git and commit-plan adapters/snapshots remain.

The strict private audit measures setup + call + teardown sequentially without
coverage, with every total greater than 1.0s listed and no exclusions. It charges
shared fixture costs where they execute; collection and pytest startup are
outside individual tests, while child-process startup inside fixtures counts.
The final audit measured 50 breaches among 3,699 passing tests:
371.5959s phase total (302.4019s setup, 67.1606s calls, 2.0334s teardown).
Two belong to Step 1: UV shapes 1.8040s/1.9385s. The other 48 are separately
tracked under the human's scope decision. The UV timing gap remains open;
authorization to attempt a fix and publish does not accept a timing exception.

The full speed day completed at 17:50:24 +02:00 on 2026-10-22, with
proof=speed/reused=none, 100% tools coverage and no failures, warnings,
xfails, call outliers or exclusions. Its final state is done/exit=0. The
independent total-duration audit verdict remains 8; the outer PowerShell
process returned 1. Functional success does not establish ceiling compliance.

Fresh setup explicitly captured exit 0 and the expected local two-line runtime
record, empty release closure, tools_imported=false, isolated=1 and utf8=1.

Full inventory: .reviews/a.release-project-root.step1.tmp.timing/above-one-second.md.
Raw phases: .reviews/a.release-project-root.step1.tmp.timing/durations.json.
Original baseline, round 2 and round 3 snapshots remain in that same directory.

Accepted duration exclusions: none. Raised baselines: none.

Writer notes: `.reviews/a.release-project-root.step1.journal.md` and
`.reviews/a.release-project-root.step1.handoff.md`.

### Change summary for step 1 release-project-root (round 3)

The staged work has four ordered a.commit groups:

1. docs(review): qualify duplicate headings
2. perf(tests): reuse CLI and repository initialization
3. feat(release): validate setup-owned runtime
4. docs(release-project-root): record step 1 validation

Fresh canonical wac and commit-plan-check verification passed: ready=true,
47 staged paths, and no diagnostics. Both staged and worktree whitespace
checks pass with CRLF-aware settings. The lock clean filter was retained.

Current staged paths:

- `bin/release_runtime_record.bat`
- `docs/v0.14.0/plan.v0.14.0.release-project-root.md`
- `docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md`
- `docs/v0.14.0/review.design-specification.v0.14.0.release-project-root.md`
- `pyproject.toml`
- `senv.bat`
- `tests/acceptance/commit_plan_check/__init__.py`
- `tests/acceptance/commit_plan_check/commit_plan_check_support.py`
- `tests/acceptance/commit_plan_check/conftest.py`
- `tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_acceptance_tdd.py`
- `tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_contracts_tdd.py`
- `tests/acceptance/release_workflow/__init__.py`
- `tests/acceptance/release_workflow/conftest.py`
- `tests/acceptance/release_workflow/process_support.py`
- `tests/acceptance/release_workflow/test_release_readiness_tdd.py`
- `tests/acceptance/release_workflow/test_uv_readiness_tdd.py`
- `tests/acceptance/review_resume/__init__.py`
- `tests/acceptance/review_resume/cli_support.py`
- `tests/acceptance/review_resume/conftest.py`
- `tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_acceptance_tdd.py`
- `tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_concurrency_tdd.py`
- `tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_identity_tdd.py`
- `tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_parked_wait_tdd.py`
- `tests/acceptance/review_status/conftest.py`
- `tests/unit/tools/git_test_double.py`
- `tests/unit/tools/release_workflow/__init__.py`
- `tests/unit/tools/release_workflow/conftest.py`
- `tests/unit/tools/release_workflow/test_bootstrap/__init__.py`
- `tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py`
- `tests/unit/tools/release_workflow/test_markers/__init__.py`
- `tests/unit/tools/release_workflow/test_markers/test_markers_pbt.py`
- `tests/unit/tools/release_workflow/test_markers/test_markers_tdd.py`
- `tests/unit/tools/release_workflow/test_readiness/__init__.py`
- `tests/unit/tools/release_workflow/test_readiness/test_faults_tdd.py`
- `tests/unit/tools/release_workflow/test_readiness/test_metadata_tdd.py`
- `tests/unit/tools/release_workflow/test_readiness/test_readiness_pbt.py`
- `tests/unit/tools/release_workflow/test_readiness/test_readiness_tdd.py`
- `tests/unit/tools/release_workflow/test_runtime/__init__.py`
- `tests/unit/tools/release_workflow/test_runtime/test_runtime_tdd.py`
- `tests/unit/tools/release_workflow/test_support.py`
- `tests/unit/tools/test_code_reviewer_acceptance/fixtures.py`
- `tools/release_workflow/__init__.py`
- `tools/release_workflow/bootstrap.py`
- `tools/release_workflow/markers.py`
- `tools/release_workflow/readiness.py`
- `tools/release_workflow/runtime_identity.py`
- `uv.lock`

Round 3 retains R1-R5 repairs and adds the R6 lexical-path fix and producer regressions, plus R7 per-scenario process and per-shape UV fixtures. Commit group membership and order remain unchanged; group 3 and 4 bodies now describe these changes and the recorded timing work.
The generated code-review transcript evolves through exchange publication and
remains outside this prepared index; the authorized residual workflow owns it.
No commit has been performed or authorized.

### Human guidance and writer response for step 1 release-project-root (round 3)

Human guidance:

Implement and review Step 1 only. Do not advance to Step 2 or commit without
the human's final choice. R1-R5 were resolved by round 2; assess the R6 producer
path-form fix and the R7 process/UV fixture changes in this round.

The ceiling is strict greater-than 1.0 second for setup + call + teardown,
without coverage or parallel execution. Shared costs remain charged where
they execute. The built-in groundhog speed gate remains call-only and does
not establish compliance with this ceiling.

The user answered: "Track separately; finish Step 1 first" for breaches
outside Step 1. Those remain listed for later optimization and do not block
Step 1. The user then asked: "Do you think we can fix the test now, and then
you publish round 3?" This authorizes further optimization and publication,
not an exception to the ceiling. Additional UV startup diagnostics did not
clear the gap. The latest test totals remain 1.8040s and 1.9385s; assess this
open R7 finding explicitly. All other Step 1 scenarios are below the ceiling;
the final full audit lists 48 breaches outside Step 1.

Preserve every assertion and real process/Git boundary described in the
report. Do not interpret a green validation command as acceptance of an
unanswered timing exception. No duration exclusion was configured.

Writer response:

The writer accepts R6 and R7 from round 2. R1-R5 remain resolved. No reviewer
repair was reversed. The reviewer changed only the Step 1 validation metadata;
the writer is refreshing those rows against the repaired implementation.

- R6: The producer compares the absolute lexical checkout root and prefix
  before calling RuntimeIdentity.measure, which retains physical containment
  checks. New producer tests cover an alias of the checkout that publishes a
  valid record and a lexically local prefix that physically escapes, returns
  status 2 and publishes nothing.
- R7 process fixtures: Each scenario now owns its measured setup and real
  launch. The successful producer starts without a record and proves actual
  publication. Readiness/failure cases seed their required existing record as
  fixture data. All batch, Python and junction processes and assertions remain.
  Success setup fell from 4.34s to 0.59s; the maximum scenario setup measured
  0.79s. No initialization was moved outside measured fixture phases.
  The subsequent whole-suite audit exposed a missing-engine total of 5.5625s.
  Linking the immutable interpreter redirector reduced isolated setup from
  0.86s to 0.77s while preserving the real process; the final full audit totals
  0.5580s for this case and below 0.630s for every process scenario.
- R7 UV fixtures: Both real offline UV lock shapes have independent tests and
  fixtures, retaining generated-shape and readiness assertions. The old
  combined setup was 2.69s; separate shapes measured 1.33s and 1.39s.
  Explicit interpreter selection did not help (1.67s/1.53s) and was reverted.
  Diagnostic tracing placed UV's first log at 1.545s, dependency resolution
  at 5ms and process exit at 1.565s; reducing worker pools did not improve it.
  No host/security settings changed, no threshold was raised, and no test was
  excluded or replaced with a synthetic lock. The final whole-suite audit
  measured these two shapes at 1.8040s and 1.9385s.

The human explicitly chose to track breaches outside Step 1 separately
and finish Step 1 first, then authorized further attempts to fix the UV tests
and publish Round 3. Those attempts did not clear the ceiling: native process
creation alone costs about 0.91s. Removing inherited settings, suppressing
the console, linking the executable and using cmd did not provide a solution.
The implementation report retains exact measurements and their limits.
No new source change was justified by these experiments. R7 remains open for
the two UV tests. The strict audit continues to list every breach against 1.0 seconds
for setup + call + teardown. Groundhog's call-only speed proof is distinct.

Fresh full-suite evidence: 3,699 passed, 100% tools coverage, no failures,
warnings, xfails, call outliers or exclusions. The strict audit lists 50
breaches, with the 48 outside Step 1 separately tracked. Publication is
authorized; no timing exception or commit is authorized.

### Reviewer focus for step 1 release-project-root (round 3)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-1-round-3 -->

## Round 3 by reviewer - Step 1

- Recorded: 2026-10-22T21:08:14+02:00
- Exchange: code/code/v0.14.0/release-project-root
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.release-project-root.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 1
- Outcome: answer

### Assessed index identity for step 1 release-project-root (exchange 1) (round 3)

Baseline index tree: d16ed32710fc19d830135f98a2c29ac8d5eaff20

Assessed index tree: a54b309ab1d06c59ac11a6e08221315b79ef1190

### Implementation check for step 1 release-project-root (exchange 1) (round 3)

Result:

Result:

No. Step 1 has NOT been fully implemented.

R6 is fixed, and the process-scenario half of R7 is fixed. Two items are
open:

- The two real `uv lock` tests exceed the user's one-second total-duration
  ceiling (R7). The writer cannot close this without a human decision.
- The reviewer's `ghog affected` run failed once in the parked-wait journey
  from the staged test optimization (R8). This is a race the writer can fix.

The writer's refreshed Step 1 rows already open with the exact No sentence and
list R7 under *Missing work for Step 1*. The reviewer added one bullet there
for R8 and changed nothing else.

Changes checked against the diff from the round 2 assessed tree `505add89…`
to `d16ed327…`. Six files changed: the validation plan, `runtime_identity.py`,
`test_runtime_tdd.py`, and the release acceptance `conftest.py`,
`process_support.py` and `test_uv_readiness_tdd.py`.

- R6: `tools/release_workflow/runtime_identity.py:143` now builds the root
  with `Path(arguments[0]).absolute()`, so the checkout-local test compares two
  paths in the same lexical form. `RuntimeIdentity.measure()` still resolves
  both paths and owns physical containment. Two new producer tests cover both
  sides. `test_producer_through_checkout_alias` runs the producer through an
  alias of the checkout and gets a published record for the real root.
  `test_producer_rejects_physical_escape` resolves a lexically local prefix
  outside the checkout and gets status 2, no record and the "outside the
  tooling checkout" diagnostic. The alias is simulated with a patched
  `resolve`, which is adequate for this unit rule. The 8.3 reproduction from
  round 2 now takes the publishing path.
- R7 process scenarios: the module-scoped matrix became a function-scoped
  `processes(tmp_path, scenario)` fixture, so each test builds and launches
  only its own scenario. `test_release_readiness_tdd.py` is unchanged, so
  every assertion is kept. Real `cmd`, Python and `mklink /J` launches remain.
  Record-consuming scenarios seed the prior record as fixture bytes. The
  successful producer starts without a record, so its assertion now proves
  publication rather than preservation. The disposable checkout hard-links the
  interpreter redirector and falls back to a copy across volumes. No fixture
  writes to that linked file; the only interpreter-shaped write is a separate
  new file under `outside`. The final audit puts every process scenario below
  0.63s.
- R7 uv shapes: one parametrized test and fixture per shape, each with a real
  `uv lock --offline --no-config` and the same shape and readiness assertions.
  The final audit lists them at 1.9385s (`with-dev-edges`) and 1.8040s
  (`no-dev-edges`); isolated runs measured 1.39s and 1.33s. The writer's
  diagnostics put about 0.91s in creating the native `uv.exe` process even for
  `uv --version`. Lock resolution takes milliseconds. Neither settings
  isolation, console suppression, a hard link nor a `cmd` launch helped. No
  host or security setting was changed, and nothing was excluded.

R1 to R5 stay resolved; their files are unchanged since round 2. The plan is
unchanged since round 2.

Architecture: the only production change is one line in the producer entry
point. No layer or dependency change. The largest new production module is
`readiness.py` at 195 lines, and `process_support.py` is 195 lines.

Performance: production code is unchanged in complexity. The open test-side
item is the uv timing.

Static coverage: both branches of the producer's local test are exercised: the
alias test publishes, `test_global_setup_preserves_record` warns, and the
escape test fails through `measure()`. That is consistent with the requestor's
reported 100% `tools` coverage.

Feature integrity: setup finishes under all three `switchpy` choices,
including a checkout reached through another path form, and local producer
failures still fail. No assertion, test, process boundary or marker was
removed. No `skip`, `xfail` or exclusion was added.

R8 is a test-reliability defect. In this round's reviewer `ghog affected` run,
the independent waiter in the `concluded` parked-wait journey exited 2 at
startup with "global wait requires ready migration and trustworthy status". The
fixture is unchanged since round 2, when it passed, so the failure is
intermittent. The only synchronization is two 0.15s silence checks, and the
round 2 in-process parent mutates the exchange almost at once after them. The
details and the fix direction are in the findings.

Validation plan effects:

The writer's refreshed Step 1 rows were accurate. They open with the exact No
sentence, record R6 and the process half of R7 as fixed, and keep the uv timing
under *Missing work for Step 1*. The reviewer added one bullet to that section
for R8, the parked-wait failure observed in this round's `ghog affected` run,
and changed nothing else.

The document-level opening line stays `No, it is not implemented`. Other
steps, the plan, the umbrella, implementation, tests and `a.commit` were not
edited.

The evidence launcher attributed the patch against the pre-edit blob
`d3429f4085df0a4d595d87f4b475fd83913ddf27` (attributable, not created). Only
that patch was staged. The project Markdown check passes after the edit. This
is review metadata, not a substantive repair.

### Pre-repair mandatory checks and coverage for step 1 release-project-root (exchange 1) (round 3)

Requestor evidence: `ghog day --full=speed --whole-suite` completed on
2026-10-22 at 17:50:24 +02:00 with exit 0, `proof=speed`, `reused=none`, full
stage `cov=100` and 3,699 tests, with no failures, warnings, xfails, call
outliers or exclusions. A fresh `ghog check` passed after the final document
edits. The requestor's strict total-duration audit lists 50 tests above 1.0s:
two in Step 1 and 48 outside it. This is reported evidence and was not
repeated.

Reviewer evidence, each command run once from the project root through the
shared `ghog.bat` launcher, with the log-freshness proof and
`SWITCHPY_CHOICE=local` set for that process only:

- `ghog check`: exit 0. All static, EOF and Markdown checks passed. The senv
  preamble shows the checkout venv activated and senv finishing.
- `ghog affected --no-cov --scope-file=.reviews/a.review-scope.code.v0.14.0.release-project-root.json`:
  exit 2, scope whole, 3,699 tests, `fail=1 warn=0 xfail=0`. The one failure is
  a setup error in
  `test_review_resume_parked_wait_tdd.py::test_wait_survives_convergence_and_conclusion_then_wakes[concluded]`,
  where the independent waiter returned exit 2 with "global wait requires
  ready migration and trustworthy status" (R8). Every other test passed.

The reviewer did not re-run the failing test or the walk: each reviewer
command runs once per round, and the fixing loop belongs to the writer. The
reviewer did not run `ghog day`, `ghog full`, the strict audit or any coverage
measurement. Coverage was assessed statically.

### Resolved validation set and sources for step 1 release-project-root (exchange 1) (round 3)

The request and the current resolver produce the same ordered set as in
round 2:

1. `ghog day --full=speed --whole-suite`: source project.
2. `rg -n 'VIRTUAL_ENV|PYTHONPATH|glob|rglob|import_module' tools/release_workflow`:
   source plan.
3. `ghog check`: source request.

No `.review-validation` file exists. Re-running `resolve_code_review_validation`
from the current `tools/code_review_validation.py` this round reproduced this
exact set. The reviewer did not run the resolved set; its own `ghog check` run
is reviewer evidence.

### Resolver drift and direction for step 1 release-project-root (exchange 1) (round 3)

None: ordered commands and source labels agree with the current resolver.

### Repository state around validation for step 1 release-project-root (exchange 1) (round 3)

Request-time and reviewer baseline index tree:
`d16ed32710fc19d830135f98a2c29ac8d5eaff20` (identical). Final assessed index
tree after the reviewer metadata patch: `a54b309ab1d06c59ac11a6e08221315b79ef1190`.

The same ordered 49-path validation set was captured before and after
assessment: the 47 staged paths plus the ignored `a.ghog.log` and
`a.ghog.status`. Tracked differences appear only for
`docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md` and `<index>`.
Ignored differences appear only for the two ghog files written by the
reviewer's evidence commands, and there are no untracked differences. The
raw `acceptable=false` reflects the intentional Step 1 metadata edit; its
single hunk lies in *Missing work for Step 1*. The failed `ghog affected` run
left no tracked side effect. There is no overlap with writer work, and the
only other working-tree entry is the untracked exchange transcript, which the
protocol owns.

Umbrella `docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md`: applicable,
digest `ca6fe473…0ec992` before and after, unchanged. No umbrella row was
modified.

Retained evidence: `.reviews/a.code-review-evidence.v0.14.0.release-project-root.step-1.json`,
with the inputs under `.reviews/a.release-project-root.step1.tmp.r3.*`.

### Repair inventory for step 1 release-project-root (exchange 1) (round 3)

Repairs made:

- Review metadata only: added one *Missing work for Step 1* bullet for the
  nondeterministic parked-wait journey (R8). The writer's other Step 1 rows
  already matched this assessment and were left unchanged. No implementation,
  test, plan or `a.commit` repair.

Paths staged:

- docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md (reviewer metadata patch only)

### Commit plan assessment for step 1 release-project-root (exchange 1) (round 3)

Ran `commit-plan-check.bat --format json` independently before assessment and
again after staging the Step 1 metadata. Both returned exit 0, `state=valid`,
`ready=true`, four ordered groups, 47 staged paths and no diagnostics. The JSON
is retained in `.reviews/a.release-project-root.step1.tmp.r3.review-commit-plan.json`
and `.reviews/a.release-project-root.step1.tmp.r3.review-commit-plan-after.json`.

Ordered groups:

1. `docs(review): qualify duplicate headings` (1 path)
2. `perf(tests): reuse CLI and repository initialization` (15 paths)
3. `feat(release): validate setup-owned runtime` (30 paths)
4. `docs(release-project-root): record step 1 validation` (1 path)

Membership, order and conventional subjects match the staged work. The
round 2 stale body is fixed: group 4 now says the timing work is recorded
against Step 1 rather than claiming Step 1 is satisfied. Group 3 lists the
lexical path comparison and the per-scenario and per-shape fixtures. The
reviewer did not amend `a.commit`. When the writer fixes R8, a group 2 body
line should mention the waiter synchronization. Mechanical readiness does not
resolve R7 or R8 and does not authorize a commit.

### Findings and boundaries for step 1 release-project-root (exchange 1) (round 3)

Unresolved findings:

- R8 (P2): the parked-wait journey is nondeterministic. The reviewer's one
  `ghog affected --no-cov` run this round failed with `fail=1`, at setup of
  `tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_parked_wait_tdd.py::test_wait_survives_convergence_and_conclusion_then_wakes[concluded]`.
  The independent waiter exited 2 with
  `"global wait requires ready migration and trustworthy status"`,
  `operational-failure`. That is the startup gate in
  `tools/review_exchange_cli_resume.py:325-328`. The fixture is unchanged since
  round 2, when the same test passed in the reviewer's run and in the
  requestor's runs, so the failure is intermittent. Likely cause: the fixture's
  only synchronization is `assert_still_quiet`, two 0.15s silence checks. A
  fresh waiter process needs longer than that to import the CLI and finish its
  first real-Git status scan, especially under xdist load. Since round 2 the
  parent runs in process with the Git double (`fast_git=True`), so its next
  mutation lands within milliseconds after the quiet window. That mutation is
  `start_request` for the later specification family, or `confirm` and
  `publish` at the gate. The waiter's startup scan can then observe a
  half-finished transition. Silence does not prove the waiter has parked.
  Before the parent mutates, wait for a signal the test can observe showing
  the waiter has passed its startup status check; do not use a longer sleep.
  Keep the independent real waiter process, real Git and every assertion.
  Check the `gate` variant and the competing-reviewer journey for the same
  pattern, since both pair `fast_git=True` parents with real waiters.
- R7 (P3, carried and narrowed): the two real `uv lock` tests still exceed
  the user's one-second total-duration ceiling.
  `tests/acceptance/release_workflow/test_uv_readiness_tdd.py::test_uv_generated_empty_shapes[with-dev-edges]`
  measured 1.9385s and `[no-dev-edges]` 1.8040s in the final full audit
  (1.39s and 1.33s isolated). The process-scenario half of R7 is resolved, and
  R6 is resolved. The writer's diagnostics place most of the time in starting
  the native `uv.exe`, about 0.91s of process creation even for
  `uv --version`, while lock resolution takes milliseconds. No change tried
  inside the repository clears it. The writer cannot close this without the
  human decision listed under boundary-crossing work. Once the human decides,
  implement the chosen option, re-run the strict audit, and refresh the Step 1
  rows.

Boundary-crossing work:

- R7 needs a human decision on the two real uv tests. Option 1, recommended:
  commit the two lock files that `uv lock --offline --no-config` produces for
  the synthetic metadata as generic test data, and test readiness against them
  in process, in milliseconds. This follows the user's standing preference to
  stub a slow process boundary rather than keep a slow test. It still drops
  the live uv run, which the round 3 guidance lists among the real boundaries
  to preserve. It also reads the plan's "uv-generated locks" as generated once
  rather than on every run, so it needs explicit approval, and the files must
  be regenerated when uv's lock format changes. Option 2: keep the live uv
  runs and record a named timing exception for these two tests. The user's
  standing rule rejects exceptions, so only the user can grant it. The 0.91s
  process-creation cost looks host-specific, and its cause was not
  established; changing host security settings is outside this repository and
  is not recommended.

### Human guidance response for step 1 release-project-root (exchange 1) (round 3)

Human guidance:

Implement and review Step 1 only. Do not advance to Step 2 or commit without
the human's final choice. R1-R5 were resolved by round 2; assess the R6 producer
path-form fix and the R7 process/UV fixture changes in this round.

The ceiling is strict greater-than 1.0 second for setup + call + teardown,
without coverage or parallel execution. Shared costs remain charged where
they execute. The built-in groundhog speed gate remains call-only and does
not establish compliance with this ceiling.

The user answered: "Track separately; finish Step 1 first" for breaches
outside Step 1. Those remain listed for later optimization and do not block
Step 1. The user then asked: "Do you think we can fix the test now, and then
you publish round 3?" This authorizes further optimization and publication,
not an exception to the ceiling. Additional UV startup diagnostics did not
clear the gap. The latest test totals remain 1.8040s and 1.9385s; assess this
open R7 finding explicitly. All other Step 1 scenarios are below the ceiling;
the final full audit lists 48 breaches outside Step 1.

Preserve every assertion and real process/Git boundary described in the
report. Do not interpret a green validation command as acceptance of an
unanswered timing exception. No duration exclusion was configured.

Guidance response:

The guidance sets review scope and does not instruct a reviewer repair, so the
reviewer changed no implementation, test or plan file. Its only change is one
Step 1 missing-work bullet. The request's general "make every safe repair"
wording does not override that rule.

Scope: the staged work stays within Step 1. Nothing from Step 2 was found.
This answer authorizes no commit.

R6 is fixed. The producer compares lexical paths, and `measure()` keeps the
physical checks. The alias and escape tests cover both sides.

R7, assessed explicitly against the total-duration ceiling:

- The process scenarios now pass the ceiling: every one is below 0.63s in the
  final audit.
- The two real uv tests do not, at 1.8040s and 1.9385s. The reviewer treats
  that as open.
- The authorization to try again and publish is not an exception. The green
  speed day, `ghog check` and `ghog affected` runs say nothing about the
  ceiling.
- A disposition the writer can act on is listed under boundary-crossing work.

Breaches outside Step 1: following the user's answer "Track separately; finish
Step 1 first", the reviewer no longer counts the 48 other breaches against
Step 1. They stay in the inventory.

Boundaries and assertions:

- `test_release_readiness_tdd.py` is unchanged, so every assertion remains.
- Each process scenario still launches real `cmd` and Python, and the escape
  case still creates a real junction.
- Both uv tests still run real uv with their shape and readiness assertions.
- The hard-linked interpreter redirector is never written to.
- Group 2 and the review-resume, commit-plan and migration boundaries are
  unchanged since round 2.

One of those boundaries does not hold reliably. The independent waiter in the
parked-wait journey failed at startup in this round's `ghog affected` run
(R8). The likely cause is that the in-process parent now mutates the exchange
before the real waiter has parked. The waiter must stay a real independent
process; the fix is synchronization, not removing it.

### Writer instructions for step 1 release-project-root (exchange 1) (round 3)

Fix R8 first. It needs no decision: synchronize the parked-wait journey on a
signal the test can observe showing the waiter has parked, check the `gate`
variant and the competing-reviewer journey for the same pattern, and keep
every real waiter process and assertion. Add a group 2 body line in `a.commit`
for it.

Present the R7 decision under boundary-crossing work to the human, and
implement the option chosen within Step 1. With option 1, add the two
uv-generated lock files as generic test data with no machine paths. Note how to
regenerate them, keep the shape and readiness assertions, and update the group
3 body. With option 2, record the human's named exception for exactly these
two tests in the Step 1 validation rows and the journal.

Then re-run the strict total-duration audit and the requestor-owned resolved
set: `ghog day --full=speed --whole-suite`, the plan's `rg` scan and
`ghog check`. Refresh the Step 1 rows. Open with `Yes. Step 1 has been fully
implemented.` and remove *Missing work for Step 1* only when R8 is fixed and
the two uv tests either pass the ceiling or have the human's exception
recorded. Update `a.commit` if staged membership changes, then publish the
replacement request through the normal requestor workflow.

The reviewer's only staged change is the attributable R8 missing-work bullet
in the Step 1 validation rows.

### Decision rationale for step 1 release-project-root (exchange 1) (round 3)

Recommend changes-requested. The six readiness-floor results are:

1. Identity: PASS. The exact plan, step 1, round 3, occurrence 1, code
   identity, umbrella and request-time index tree agree with the live exchange.
2. Implementation completeness: FAIL. R7 (the two real uv tests above the
   ceiling) and R8 (the nondeterministic parked-wait journey) remain.
3. Validation and coverage: FAIL. The reviewer's `ghog affected --no-cov` run
   failed one test (R8), and the user's total-duration audit still lists the
   two Step 1 uv tests (R7). The requestor's speed day with 100% coverage and
   the reviewer's `ghog check` are green, and the static coverage walk finds no
   gap.
4. Staged attribution: PASS. The sole reviewer change is the attributable
   Step 1 missing-work bullet. There is no substantive repair and no unrelated
   staged work.
5. Unresolved findings: FAIL. R8 (P2) and R7 (P3) remain. R1 to R6 are
   resolved.
6. `a.commit`: PASS mechanically. The independent checker reports exit 0,
   valid, ready, with all 47 paths in four accurate groups.

R6 and the process half of R7 are done well. R8 is a writer fix inside the
staged test work. R7 cannot move without the human decision listed under
boundary-crossing work.

### Final reviewer decision for step 1 release-project-root (exchange 1) (round 3)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-1-round-3 -->

## Round 4 by requestor - Step 1

- Recorded: 2026-10-22T22:10:30+02:00
- Exchange: code/code/v0.14.0/release-project-root
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.release-project-root.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 1
- Outcome: request

### Review identity for step 1 release-project-root (round 4)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.release-project-root.md
Implementation step: 1
Review round: 4

### Code review evidence for step 1 release-project-root (round 4)

request_index_tree: dfc7d5de4f536615b9eb3859abdfc15f7b64f011
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)
- `rg -n 'VIRTUAL_ENV|PYTHONPATH|glob|rglob|import_module' tools/release_workflow` (sources: plan)
- `ghog check` (sources: request)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "missing", "requirement": "docs/v0.14.0/feature-request.v0.14.0.release-project-root.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: docs(review): qualify duplicate headings
group 1 path: docs/v0.14.0/review.design-specification.v0.14.0.release-project-root.md
group 2: perf(tests): reuse CLI and repository initialization
group 2 path: tests/acceptance/commit_plan_check/__init__.py
group 2 path: tests/acceptance/commit_plan_check/commit_plan_check_support.py
group 2 path: tests/acceptance/commit_plan_check/conftest.py
group 2 path: tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_acceptance_tdd.py
group 2 path: tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_contracts_tdd.py
group 2 path: tests/acceptance/review_resume/__init__.py
group 2 path: tests/acceptance/review_resume/cli_support.py
group 2 path: tests/acceptance/review_resume/conftest.py
group 2 path: tests/acceptance/review_resume/waiter_driver.py
group 2 path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_acceptance_tdd.py
group 2 path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_concurrency_tdd.py
group 2 path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_identity_tdd.py
group 2 path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_parked_wait_tdd.py
group 2 path: tests/acceptance/review_status/conftest.py
group 2 path: tests/unit/tools/git_test_double.py
group 2 path: tests/unit/tools/test_code_reviewer_acceptance/fixtures.py
group 3: feat(release): validate setup-owned runtime
group 3 path: bin/release_runtime_record.bat
group 3 path: docs/v0.14.0/plan.v0.14.0.release-project-root.md
group 3 path: pyproject.toml
group 3 path: senv.bat
group 3 path: tests/acceptance/release_workflow/__init__.py
group 3 path: tests/acceptance/release_workflow/conftest.py
group 3 path: tests/acceptance/release_workflow/process_support.py
group 3 path: tests/acceptance/release_workflow/test_release_readiness_tdd.py
group 3 path: tests/acceptance/release_workflow/test_uv_readiness_tdd.py
group 3 path: tests/unit/tools/release_workflow/__init__.py
group 3 path: tests/unit/tools/release_workflow/conftest.py
group 3 path: tests/unit/tools/release_workflow/test_bootstrap/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_markers/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_markers/test_markers_pbt.py
group 3 path: tests/unit/tools/release_workflow/test_markers/test_markers_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_readiness/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_readiness/test_faults_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_readiness/test_metadata_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_readiness/test_readiness_pbt.py
group 3 path: tests/unit/tools/release_workflow/test_readiness/test_readiness_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_runtime/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_runtime/test_runtime_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_support.py
group 3 path: tools/release_workflow/__init__.py
group 3 path: tools/release_workflow/bootstrap.py
group 3 path: tools/release_workflow/markers.py
group 3 path: tools/release_workflow/readiness.py
group 3 path: tools/release_workflow/runtime_identity.py
group 3 path: uv.lock
group 4: docs(release-project-root): record step 1 validation
group 4 path: docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md
staged path: bin/release_runtime_record.bat
staged path: docs/v0.14.0/plan.v0.14.0.release-project-root.md
staged path: docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md
staged path: docs/v0.14.0/review.design-specification.v0.14.0.release-project-root.md
staged path: pyproject.toml
staged path: senv.bat
staged path: tests/acceptance/commit_plan_check/__init__.py
staged path: tests/acceptance/commit_plan_check/commit_plan_check_support.py
staged path: tests/acceptance/commit_plan_check/conftest.py
staged path: tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_acceptance_tdd.py
staged path: tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_contracts_tdd.py
staged path: tests/acceptance/release_workflow/__init__.py
staged path: tests/acceptance/release_workflow/conftest.py
staged path: tests/acceptance/release_workflow/process_support.py
staged path: tests/acceptance/release_workflow/test_release_readiness_tdd.py
staged path: tests/acceptance/release_workflow/test_uv_readiness_tdd.py
staged path: tests/acceptance/review_resume/__init__.py
staged path: tests/acceptance/review_resume/cli_support.py
staged path: tests/acceptance/review_resume/conftest.py
staged path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_acceptance_tdd.py
staged path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_concurrency_tdd.py
staged path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_identity_tdd.py
staged path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_parked_wait_tdd.py
staged path: tests/acceptance/review_resume/waiter_driver.py
staged path: tests/acceptance/review_status/conftest.py
staged path: tests/unit/tools/git_test_double.py
staged path: tests/unit/tools/release_workflow/__init__.py
staged path: tests/unit/tools/release_workflow/conftest.py
staged path: tests/unit/tools/release_workflow/test_bootstrap/__init__.py
staged path: tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py
staged path: tests/unit/tools/release_workflow/test_markers/__init__.py
staged path: tests/unit/tools/release_workflow/test_markers/test_markers_pbt.py
staged path: tests/unit/tools/release_workflow/test_markers/test_markers_tdd.py
staged path: tests/unit/tools/release_workflow/test_readiness/__init__.py
staged path: tests/unit/tools/release_workflow/test_readiness/test_faults_tdd.py
staged path: tests/unit/tools/release_workflow/test_readiness/test_metadata_tdd.py
staged path: tests/unit/tools/release_workflow/test_readiness/test_readiness_pbt.py
staged path: tests/unit/tools/release_workflow/test_readiness/test_readiness_tdd.py
staged path: tests/unit/tools/release_workflow/test_runtime/__init__.py
staged path: tests/unit/tools/release_workflow/test_runtime/test_runtime_tdd.py
staged path: tests/unit/tools/release_workflow/test_support.py
staged path: tests/unit/tools/test_code_reviewer_acceptance/fixtures.py
staged path: tools/release_workflow/__init__.py
staged path: tools/release_workflow/bootstrap.py
staged path: tools/release_workflow/markers.py
staged path: tools/release_workflow/readiness.py
staged path: tools/release_workflow/runtime_identity.py
staged path: uv.lock
```

### Validation scope for step 1 release-project-root (round 4)

Validation scope: the whole suite.

### Requestor assessment for step 1 release-project-root (round 4)

No. Step 1 has NOT been fully implemented.

R1-R6 and the process-scenario half of R7 remain resolved. The human chose
"Keep live UV generation, publish round 4" after the coverage/timing tradeoff
and the unresolved identity-fixture failure were explained. This round is
published on that explicit instruction, with incomplete validation disclosed;
it does not claim the normal all-green publication prerequisite was met.

R7: retain both real offline UV lock invocations and all shape/readiness
assertions. The human's choice accepts named total-duration exceptions for
test_uv_generated_empty_shapes[no-dev-edges] at 1.8040s and [with-dev-edges]
at 1.9385s, under tests/acceptance/release_workflow/test_uv_readiness_tdd.py.
The general one-second ceiling stays unchanged. The raw inventory continues
to list both costs. No call-only groundhog exclusion or raised floor is used.

R8: the real independent waiter signals its first notification-wait boundary,
after startup status and initial discovery. The parent waits for that signal
before mutation. The parked-wait and competing-reviewer focused tests pass;
all real CLI, Git, notification and claim behavior and assertions remain.

Current verification limitation: the post-R8 whole-suite speed day passed
check, all 3,699 affected tests and 100% tools coverage, then exited 2 during
sequential timings. Two setup errors share the Gemini identity fixture: the
first resume did not yield an ownership capability. The new assertion exposes
the first operation/outcome/diagnostic instead of a downstream missing key.
It is diagnostic improvement, not a root-cause fix. Identity-only and surrounding
review-resume focused runs pass, as did an 80-journey diagnostic; none resolves
the failed full walk. No current speed proof or full-duration compliance is
claimed. An unchanged full walk was not repeated to gamble for green.

Architecture and production behavior are unchanged since Round 3. The latest
edits are test synchronization, diagnostic reporting and validation/guidance
updates. The code remains within Step 1. The reviewer should assess R8 and
the unresolved identity failure explicitly. No commit or Step 2 is authorized.

### Implementation report for step 1 release-project-root (round 4)

Step 1 produces a setup-owned two-line runtime identity, validates physical
containment, interpreter requirements and the locked release closure, and
delays engine imports until readiness succeeds. R1-R6 repairs remain intact.
The release group stays stdlib-only and is included by dev. The production
CLI remains Step 5 work; Step 1 uses a disposable engine probe and checks
missing-engine failure. No production code changed after Round 3.

R8 changes start_wait and adds waiter_driver.py. The child calls the real
review-exchange CLI in its own process and observes the first
WatchdogNotificationAdapter.wait call. That boundary follows the startup
status guard and initial request discovery. It touches one fixture-owned
marker outside the repository, then delegates to the original wait method.
The parent waits for this marker with a bounded startup guard and child-exit
check. Failure kills and collects the child; cleanup removes the marker.
Gate, concluded and competing-reviewer scenarios use the same synchronization.
Every existing assertion, including silence and terminal-result checks, stays.

The first post-R8 day passed check, 3,699 affected tests and 100% tools coverage.
Its sequential timings failed with two setup errors from one Gemini identity
fixture at 21:35:19 +02:00 on 2026-10-22. The fixture had used the first resume
result as a capability without checking its exit code. The new early assertion
reports operation, outcome and diagnostic without including ownership tokens.
No production cause has been established. Focused identity and review-resume
runs and 80 diagnostic journeys did not reproduce the failure. This is an open
functional finding, not a timing exception or a proven fix.

Evidence:

- .reviews/a.release-project-root.step1.tmp.r4.waiters.log: parked/concurrent
  focused groundhog, exit 0.
- .reviews/a.release-project-root.step1.tmp.timing/round4-first-groundhog.log:
  whole-suite speed day, exit 2 after successful affected/coverage stages.
- .reviews/a.release-project-root.step1.tmp.r4.identity.log and
  .reviews/a.release-project-root.step1.tmp.r4.resume.log: focused passes.
- .reviews/a.release-project-root.step1.tmp.r4.identity-probe.log:
  20 cycles across four providers, no reproduction.
- .reviews/a.release-project-root.step1.tmp.r4.check.log: latest static checks.

R7 keeps two live offline UV invocations, shape checks and readiness assertions.
The human selected retaining live generation and publishing this round after
the stored-fixture alternative was explained. Record named timing exceptions:
tests/acceptance/release_workflow/test_uv_readiness_tdd.py::test_uv_generated_empty_shapes[no-dev-edges]
at 1.8040s, and the same test's [with-dev-edges] case at 1.9385s. These are
setup + call + teardown totals from the last successful full audit, not fresh
measurements. The general ceiling remains 1.0s and the raw inventory lists both.

Attempted improvements: split the original 2.69s combined fixture into one
fixture per shape (isolated 1.33s/1.39s). Explicit interpreter selection,
reduced workers, isolated UV settings, console suppression and executable
linking did not clear the ceiling. Native UV process creation alone measured
about 0.91s; useful resolution took milliseconds. No host settings changed.
The reason for accepting these two costs is the human's choice to preserve
live integration coverage. No stored locks, call-only groundhog exclusions,
raised global floor, skipped tests or weakened assertions were introduced.

Historical pre-R8 proof: 3,699 tests, 100% tools coverage, speed proof completed
2026-10-22 17:50:24 +02:00. Its independent total-phase audit measured 50
breaches and 371.5959s summed phases: setup 302.4019s, call 67.1606s, teardown
2.0334s. Every Step 1 process scenario was below 0.630s. The other 48 breaches
remain separately tracked as authorized. This evidence predates R8 and does
not prove the current tree. Snapshots: .reviews/a.release-project-root.step1.tmp.timing/round3-final-*.

Writer notes: `.reviews/a.release-project-root.step1.journal.md` and
`.reviews/a.release-project-root.step1.handoff.md`.

### Change summary for step 1 release-project-root (round 4)

The staged work has four ordered a.commit groups:

1. docs(review): qualify duplicate headings
2. perf(tests): reuse CLI and repository initialization
3. feat(release): validate setup-owned runtime
4. docs(release-project-root): record step 1 validation

Fresh canonical wac and commit-plan-check verification passed: ready=true,
48 staged paths, and no diagnostics. Both staged and worktree whitespace
checks pass with CRLF-aware settings. The lock clean filter was retained.

Current staged paths:

- `bin/release_runtime_record.bat`
- `docs/v0.14.0/plan.v0.14.0.release-project-root.md`
- `docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md`
- `docs/v0.14.0/review.design-specification.v0.14.0.release-project-root.md`
- `pyproject.toml`
- `senv.bat`
- `tests/acceptance/commit_plan_check/__init__.py`
- `tests/acceptance/commit_plan_check/commit_plan_check_support.py`
- `tests/acceptance/commit_plan_check/conftest.py`
- `tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_acceptance_tdd.py`
- `tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_contracts_tdd.py`
- `tests/acceptance/release_workflow/__init__.py`
- `tests/acceptance/release_workflow/conftest.py`
- `tests/acceptance/release_workflow/process_support.py`
- `tests/acceptance/release_workflow/test_release_readiness_tdd.py`
- `tests/acceptance/release_workflow/test_uv_readiness_tdd.py`
- `tests/acceptance/review_resume/__init__.py`
- `tests/acceptance/review_resume/cli_support.py`
- `tests/acceptance/review_resume/conftest.py`
- `tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_acceptance_tdd.py`
- `tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_concurrency_tdd.py`
- `tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_identity_tdd.py`
- `tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_parked_wait_tdd.py`
- `tests/acceptance/review_resume/waiter_driver.py`
- `tests/acceptance/review_status/conftest.py`
- `tests/unit/tools/git_test_double.py`
- `tests/unit/tools/release_workflow/__init__.py`
- `tests/unit/tools/release_workflow/conftest.py`
- `tests/unit/tools/release_workflow/test_bootstrap/__init__.py`
- `tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py`
- `tests/unit/tools/release_workflow/test_markers/__init__.py`
- `tests/unit/tools/release_workflow/test_markers/test_markers_pbt.py`
- `tests/unit/tools/release_workflow/test_markers/test_markers_tdd.py`
- `tests/unit/tools/release_workflow/test_readiness/__init__.py`
- `tests/unit/tools/release_workflow/test_readiness/test_faults_tdd.py`
- `tests/unit/tools/release_workflow/test_readiness/test_metadata_tdd.py`
- `tests/unit/tools/release_workflow/test_readiness/test_readiness_pbt.py`
- `tests/unit/tools/release_workflow/test_readiness/test_readiness_tdd.py`
- `tests/unit/tools/release_workflow/test_runtime/__init__.py`
- `tests/unit/tools/release_workflow/test_runtime/test_runtime_tdd.py`
- `tests/unit/tools/release_workflow/test_support.py`
- `tests/unit/tools/test_code_reviewer_acceptance/fixtures.py`
- `tools/release_workflow/__init__.py`
- `tools/release_workflow/bootstrap.py`
- `tools/release_workflow/markers.py`
- `tools/release_workflow/readiness.py`
- `tools/release_workflow/runtime_identity.py`
- `uv.lock`

Round 4 adds the R8 child waiter signal and parent synchronization, plus the
identity fixture's early diagnostic assertion. Group 2 includes the new
waiter_driver.py and preserves all assertions. The validation document and
group 4 record the human's two live-UV timing exceptions and the unresolved
whole-suite identity failure. Production code is unchanged since Round 3.
All earlier repairs remain accepted; no repair was reversed.

The generated code-review transcript evolves through exchange publication and
remains outside this prepared index. No commit is authorized or performed.

### Human guidance and writer response for step 1 release-project-root (round 4)

Human guidance:

The user's latest instruction is: "Keep live UV generation, publish round 4."

It follows an explanation that stored lock fixtures preserve readiness
assertions but remove live generation coverage, whereas retaining live UV
needs timing exceptions for these two tests. Preserve live UV generation and
all assertions. Record exactly those two measured integration costs as named
exceptions: test_uv_generated_empty_shapes[no-dev-edges] at 1.8040s and
[with-dev-edges] at 1.9385s, in
tests/acceptance/release_workflow/test_uv_readiness_tdd.py.
The general ceiling remains 1.0 second for setup + call + teardown. Keep raw
timings visible. Breaches outside Step 1 remain separately tracked under the
prior answer "Track separately; finish Step 1 first".

The user requested publication after being informed that the full run exposed
an intermittent identity-fixture failure not reproduced by focused runs.
This round therefore discloses incomplete validation; do not interpret
publication, the timing exceptions or any focused pass as full functional
proof or commit authorization.

Assess R8 synchronization and the unresolved identity-fixture failure.
Preserve independent real waiters, real Git and every assertion. Step 1 only;
no commit or Step 2 without a later explicit human choice.

Writer response:

The writer accepts Round 3. No reviewer repair was reversed. R1-R6 and
the process-scenario part of R7 remain resolved.

R8: the independent waiter now signals its first real notification wait via
a marker outside the repository. The parent observes it before mutation.
This follows the startup guard and discovery; it preserves the real CLI,
Git, observer, claims, child processes and every assertion. Gate, concluded
and competing-reviewer scenarios share it. Focused waiter/concurrency runs
passed, as did those cases in subsequent affected, coverage and timing runs.
The reviewer-added Missing work bullet is retained with the repair evidence.

R7: the human answered "Keep live UV generation, publish round 4" after the
choice between stored UV fixtures and live generation with timing exceptions
was explained. Retain live generation and accept named exceptions for the
two cases only, at the documented 1.8040s and 1.9385s totals. Keep the general
one-second ceiling and every assertion. The tracked validation and a.commit
now record that decision. No call-only groundhog exclusion was needed.

A separate functional issue remains: sequential timings failed in the Gemini
identity fixture after check/affected/coverage passed. The first resume's
failure was masked by using its missing capability. An early diagnostic
assertion now exposes that operation; focused runs and 80 diagnostic journeys
pass but do not establish the cause or fix it. The writer reports this openly
and requests assessment. The human explicitly requested Round 4 publication
after being told this failure remains unresolved. No new full walk was run
unchanged merely to clear its verdict. No current full-speed proof is claimed.

No commit or Step 2 work is authorized.

### Reviewer focus for step 1 release-project-root (round 4)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-1-round-4 -->

## Round 4 by reviewer - Step 1

- Recorded: 2026-10-22T22:30:24+02:00
- Exchange: code/code/v0.14.0/release-project-root
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.release-project-root.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 1
- Outcome: answer

### Assessed index identity for step 1 release-project-root (exchange 1) (round 4)

Baseline index tree: dfc7d5de4f536615b9eb3859abdfc15f7b64f011

Assessed index tree: b84f6a14b062344d0fed4d70d119bdac58f77d53

### Implementation check for step 1 release-project-root (exchange 1) (round 4)

Result:

No. Step 1 has NOT been fully implemented.

R8 is fixed, and R7 is closed by the human's recorded decision. One
functional item is open: the intermittent Gemini identity-fixture setup failure
that stopped the requestor's whole-suite walk (R9). A small cleanup gap in the
competing-reviewer fixture is new (R10). The reviewer refreshed the Step 1 rows
to match, keeping the exact No sentence.

Changes checked against the diff from the round 3 assessed tree `a54b309a…`
to `dfc7d5de…`. Five files changed: the validation plan, the review-resume
package docstring, `conftest.py`, `test_review_resume_identity_tdd.py` and the
new `waiter_driver.py`. Production code is unchanged since round 3.

- R8: `start_wait` now launches `tests.acceptance.review_resume.waiter_driver`,
  which calls the real `tools.review_exchange_cli.main` in its own process.
  The driver patches `WatchdogNotificationAdapter.wait` to touch a marker on
  its first call, then delegates to the original method. In
  `tools/review_exchange_cli_resume.py::_wait_any_request`, that first call
  comes after the startup status gate, the observer start and the first
  authoritative rescan. A parent mutation after the marker can no longer race
  the startup scan, and the running observer still sees it. The marker lives
  outside the repository and is removed in `finally`. A failed startup kills
  and collects the child. The parent polls for the marker under the existing
  120-second hang guard; this is a signal, not a longer sleep. Gate,
  concluded and competing-reviewer journeys all use it. Every silence check and
  terminal-result assertion stays, and the waiter is still an independent real
  process with real Git. The reviewer's `ghog affected --no-cov` run passed all
  three journeys.
- R7: the human answered "Keep live UV generation, publish round 4".
  `test_uv_readiness_tdd.py` is unchanged since round 3, so both cases still run
  a real `uv lock --offline --no-config` with every shape and readiness
  assertion. The two totals, 1.8040s and 1.9385s, are now recorded as named
  exceptions. The general 1.0s ceiling is unchanged, the raw inventory keeps
  both, and no groundhog exclusion exists.
- Identity diagnostic: the fixture now asserts that every first-resume result
  exited 0 before using its capability. The message carries only exit code,
  operation, outcome and diagnostic, never the ownership pair. This exposes the
  next occurrence but fixes nothing, as the writer states.

R1 to R6 stay resolved; their files are unchanged since round 3.

Architecture: no production change this round. `waiter_driver.py` is 39 lines
of test support with one responsibility.

Performance: production code is unchanged. The test-side timing position is
the two named UV exceptions; the other 48 breaches stay tracked separately by
the human's earlier answer.

Static coverage: no `tools` module changed since round 3, when the full gate
reported 100%. The new driver is test support outside the coverage source and
is used by every waiter scenario.

Feature integrity: no assertion, test, real process boundary or marker was
removed. No `skip`, `xfail`, retry or exclusion was added. The open gap is that
the post-R8 tree has no green whole-suite walk (R9).

Validation plan effects:

The reviewer updated only the Step 1 rows of
`docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md`:

- *Analysis*: kept the exact No sentence. The R7 pointer now names the
  performance check, and the R8 paragraph records the round 4 assessment and
  names the identity failure as the remaining gap.
- *What was implemented*: added the reviewer's round 4 `ghog check` and
  `ghog affected --no-cov` evidence. That parallel pass does not replace the
  failed sequential walk.
- *Missing work*: removed the R7 bullet, now a recorded decision rather than
  work, and the R8 bullet, resolved this round. Kept the identity bullet with
  diagnostic direction, and added R10.
- *Performance check*: moved the complete exception record there: the human's
  answer, both node IDs, both totals and the experiments tried. This removes
  the stale sentence that still called the decision pending.

The document-level line stays `No, it is not implemented`. Other steps, the
plan, the umbrella, implementation, tests and `a.commit` were not edited.

The evidence launcher attributed the patch against the pre-edit blob
`77139c8106677690b825d1fb77b6cbf85b5f12be` (attributable, not created). Only
that patch was staged. The project Markdown check and `git diff --check` pass.
This is review metadata, not a substantive repair.

### Pre-repair mandatory checks and coverage for step 1 release-project-root (exchange 1) (round 4)

Requestor evidence, as reported and not repeated: the post-R8
`ghog day --full=speed --whole-suite` passed `ghog check`, `ghog affected`
over 3,699 tests and `ghog full` at `cov=100`. Its sequential timings stage then
exited 2 with `fail=2`. Both errors were at setup of the Gemini parameter of
`test_review_resume_identity_tdd.py::identity_journey`, raising
`KeyError: 'ownership_generation'` when the second resume used the first
resume's missing capability. The walk produced no speed proof. Focused
identity, review-resume and parked-wait runs passed, as did 80 diagnostic
journeys; none reproduced the failure. The last complete walk, at 17:50:24
+02:00, predates R8.

Reviewer evidence, each command run once from the project root through the
shared `ghog.bat` launcher, with the log-freshness proof and
`SWITCHPY_CHOICE=local` set for that process only:

- `ghog check`: exit 0. All static, EOF and Markdown checks passed.
- `ghog affected --no-cov --scope-file=.reviews/a.review-scope.code.v0.14.0.release-project-root.json`:
  exit 0, scope whole, 3,699 tests, `fail=0 warn=0 xfail=0`. This includes the
  parked-wait, competing-reviewer and identity modules.

The reviewer's run is parallel, like the requestor's affected stage, which
also passed. It cannot clear a failure that appeared only in the sequential
timing pass. The reviewer did not run `ghog day`, `ghog full`, the strict
audit or any coverage measurement. Coverage was assessed statically.

### Resolved validation set and sources for step 1 release-project-root (exchange 1) (round 4)

The request and the current resolver produce the same ordered set as in
round 3:

1. `ghog day --full=speed --whole-suite`: source project.
2. `rg -n 'VIRTUAL_ENV|PYTHONPATH|glob|rglob|import_module' tools/release_workflow`:
   source plan.
3. `ghog check`: source request.

No `.review-validation` file exists. Re-running `resolve_code_review_validation`
from the current `tools/code_review_validation.py` this round reproduced this
exact set. The reviewer did not run the resolved set; its own `ghog check` run
is reviewer evidence. The requestor reports the first command as failed at
the sequential timings stage (R9).

### Resolver drift and direction for step 1 release-project-root (exchange 1) (round 4)

None: ordered commands and source labels agree with the current resolver.

### Repository state around validation for step 1 release-project-root (exchange 1) (round 4)

Request-time and reviewer baseline index tree:
`dfc7d5de4f536615b9eb3859abdfc15f7b64f011` (identical). Final assessed index
tree after the reviewer metadata patch: `b84f6a14b062344d0fed4d70d119bdac58f77d53`.

The same ordered 50-path validation set was captured before and after
assessment: the 48 staged paths plus the ignored `a.ghog.log` and
`a.ghog.status`. Tracked differences appear only for
`docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md` and `<index>`.
Ignored differences appear only for the two ghog files written by the
reviewer's evidence commands, and there are no untracked differences. The
raw `acceptable=false` reflects the intentional Step 1 metadata edit. The
reviewer's ghog runs left no tracked side effect. There is no overlap with
writer work, and the only other working-tree entry is the untracked exchange
transcript, which the protocol owns.

Umbrella `docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md`: applicable,
digest `ca6fe473…0ec992` before and after, unchanged. No umbrella row was
modified.

Retained evidence: `.reviews/a.code-review-evidence.v0.14.0.release-project-root.step-1.json`,
with the inputs under `.reviews/a.release-project-root.step1.tmp.r4.review-*`.

### Repair inventory for step 1 release-project-root (exchange 1) (round 4)

Repairs made:

- Review metadata only: refreshed the Step 1 validation rows. The R7 decision
  record moved from *Missing work* to the performance check, replacing a
  stale "pending" sentence. R8 left *Missing work* as resolved. The reviewer's
  round 4 evidence and the R10 bullet were added, and the identity bullet gained
  diagnostic direction. No implementation, test, plan or `a.commit` repair.

Paths staged:

- docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md (reviewer metadata patch only)

### Commit plan assessment for step 1 release-project-root (exchange 1) (round 4)

Ran `commit-plan-check.bat --format json` independently before assessment and
again after staging the Step 1 metadata. Both returned exit 0, `state=valid`,
`ready=true`, four ordered groups, 48 staged paths and no diagnostics. The JSON
is retained in `.reviews/a.release-project-root.step1.tmp.r4.review-commit-plan.json`
and `.reviews/a.release-project-root.step1.tmp.r4.review-commit-plan-after.json`.

Ordered groups:

1. `docs(review): qualify duplicate headings` (1 path)
2. `perf(tests): reuse CLI and repository initialization` (16 paths)
3. `feat(release): validate setup-owned runtime` (30 paths)
4. `docs(release-project-root): record step 1 validation` (1 path)

Membership, order and conventional subjects match the staged work. The new
`waiter_driver.py` is in group 2, whose body now names the waiter
synchronization and the identity diagnostic. Group 4 records the two named
UV exceptions and the unresolved timing-run failure. The reviewer did not
amend `a.commit`. When R9 is fixed, the body of the group that receives the
fix should name it. Mechanical readiness does not resolve R9 or R10 and does not
authorize a commit.

### Findings and boundaries for step 1 release-project-root (exchange 1) (round 4)

Unresolved findings:

- R9 (P2): the identity fixture fails intermittently, so the requestor's
  resolved validation set is not green. The post-R8
  `ghog day --full=speed --whole-suite` exited 2 in its sequential timings
  stage. Both tests sharing
  `tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_identity_tdd.py::identity_journey[gemini]`
  errored at setup. The first resume's last result carried no ownership
  capability, and setup took 0.933s against about 1.3s for the other
  providers. Only the `gemini` parameter failed. It failed early in a
  single-process run, while the parallel affected stage, this round's reviewer
  run, focused runs and 80 diagnostic journeys all passed. The staged group 2
  change moved these provider variants from child processes to in-process
  `run_inline` calls. That makes order-dependent process state a leading
  suspect: module-level caches, environment, working directory or open file
  handles left by earlier in-process CLI tests. Another candidate is a
  transient Windows file-access error during atomic replacement, which a much
  faster in-process sequence makes more likely. Neither is established. The
  new assertion will name the failing operation and diagnostic. Reproduce in
  one process and the same order before changing code. Fix the cause, not the
  symptom: no retry, skip, xfail or exclusion.
- R10 (P3): the competing-reviewer fixture can leak a real waiter.
  `tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_concurrency_tdd.py:88`
  builds `processes = [start_wait(repo), start_wait(repo)]` before its `try`.
  `start_wait` now waits up to 120 seconds and cleans up only its own child. If
  the second waiter fails to start, the first `wait-any-request` process is
  never killed. It has no deadline and keeps an observer on the temporary
  artifact home. Start an empty list, enter `try`, then append each started
  waiter, so `finally` covers both.

Boundary-crossing work:

- If R9's cause lies in review-exchange production code rather than in the
  staged fixtures or the in-process runner, that repair is outside Step 1.
  Report it with the diagnostic and ask the human for its scope before
  changing production code.

### Human guidance response for step 1 release-project-root (exchange 1) (round 4)

Human guidance:

The user's latest instruction is: "Keep live UV generation, publish round 4."
It follows an explanation of stored lock fixtures versus live UV with timing
exceptions. Preserve live UV generation and all assertions. Record exactly two
named exceptions in `tests/acceptance/release_workflow/test_uv_readiness_tdd.py`:
`test_uv_generated_empty_shapes[no-dev-edges]` at 1.8040s and
`[with-dev-edges]` at 1.9385s. The general ceiling remains 1.0 second for
setup + call + teardown, raw timings stay visible, and breaches outside Step 1
stay tracked separately under "Track separately; finish Step 1 first".

The user requested publication knowing the full run exposed an intermittent
identity-fixture failure that focused runs did not reproduce. Publication,
the exceptions and focused passes are not full functional proof or commit
authorization. Assess R8 synchronization and the unresolved identity-fixture
failure. Preserve independent real waiters, real Git and every assertion.
Step 1 only; no commit or Step 2 without a later explicit human choice.

Guidance response:

The guidance asks for assessment and does not instruct a reviewer repair, so
the reviewer changed no implementation or test file. The request's general
"make every safe repair" wording does not override that rule. Its only change
is the Step 1 validation-row refresh.

Scope: the staged work stays within Step 1. Nothing from Step 2 was found.
This answer authorizes no commit.

R7: the reviewer accepts the human's decision as the disposition of R7.

- Both UV cases still run real offline `uv lock` with every assertion.
- The two named totals match the last complete audit.
- The general ceiling is unchanged, and no exclusion was configured.
- The decision record now sits in the Step 1 performance check rather than
  under missing work.

R8, assessed explicitly: fixed. The signal fires at the first notification
wait, after the startup status gate and first rescan. That is the boundary the
race needed. Waiters stay independent real processes with real Git, every
assertion stays, and the reviewer's affected run passed all three journeys.
R10 is a cleanup gap the change exposed in one fixture, not a flaw in the
synchronization.

The identity failure, assessed explicitly: open as R9 (P2). The new assertion
is sound and reveals no ownership token, but it is diagnosis only. The
reviewer's green parallel run cannot clear a failure that appeared only in a
sequential pass, so the reviewer treats the resolved validation set as failed.

Breaches outside Step 1 remain tracked separately, as the user answered, and
do not count against Step 1.

### Writer instructions for step 1 release-project-root (exchange 1) (round 4)

Fix R9 first. Reproduce the Gemini identity failure in one process and in the
suite's order, for example with the `ghog single` command the failed walk's
report names for the identity module. Use the new assertion's diagnostic to name
the failing operation. Fix the cause in the staged fixtures or the in-process
runner, keeping every identity assertion and the diagnostic. If the cause is
in review-exchange production code, stop and report it as boundary work.

Fix R10 by moving both `start_wait` calls in the competing-reviewer fixture
inside its cleanup scope.

Then run the requestor-owned resolved set green:
`ghog day --full=speed --whole-suite`, the plan's `rg` scan and `ghog check`.
Re-run the strict total-duration audit and confirm that the only Step 1
breaches are the two named UV exceptions. Refresh the Step 1 rows. Open with
`Yes. Step 1 has been fully implemented.` and remove *Missing work for Step 1*
only when R9 and R10 are fixed and that walk is green. Update the `a.commit`
group bodies for the fixes, then publish the replacement request through the
normal requestor workflow.

The reviewer's only staged change is the attributable Step 1 validation-row
refresh.

### Decision rationale for step 1 release-project-root (exchange 1) (round 4)

Recommend changes-requested. The six readiness-floor results are:

1. Identity: PASS. The exact plan, step 1, round 4, occurrence 1, code
   identity, umbrella and request-time index tree agree with the live exchange.
2. Implementation completeness: FAIL. R9, the intermittent identity-fixture
   failure, remains, and R10 is open.
3. Validation and coverage: FAIL. The requestor's resolved
   `ghog day --full=speed --whole-suite` exited 2 in sequential timings, and
   the post-R8 tree has no green walk. The reviewer's `ghog check` and
   `ghog affected --no-cov` are green, and the static coverage walk finds no
   gap.
4. Staged attribution: PASS. The sole reviewer change is the attributable
   Step 1 validation-row refresh. There is no substantive repair and no
   unrelated staged work.
5. Unresolved findings: FAIL. R9 (P2) and R10 (P3) remain. R1 to R8 are
   resolved, R7 by the human's named exceptions.
6. `a.commit`: PASS mechanically. The independent checker reports exit 0,
   valid, ready, with all 48 paths in four accurate groups.

R8 is done well, and the R7 decision is now recorded where it belongs. Step 1
needs a green whole-suite walk before it can be recommended for commit.

### Final reviewer decision for step 1 release-project-root (exchange 1) (round 4)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-1-round-4 -->

## Round 5 by requestor - Step 1

- Recorded: 2026-10-22T23:27:05+02:00
- Exchange: code/code/v0.14.0/release-project-root
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.release-project-root.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 1
- Outcome: request

### Review identity for step 1 release-project-root (round 5)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.release-project-root.md
Implementation step: 1
Review round: 5

### Code review evidence for step 1 release-project-root (round 5)

request_index_tree: a13e5685e914002404399d1c5fe06021fe2844ea
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)
- `rg -n 'VIRTUAL_ENV|PYTHONPATH|glob|rglob|import_module' tools/release_workflow` (sources: plan)
- `ghog check` (sources: request)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "missing", "requirement": "docs/v0.14.0/feature-request.v0.14.0.release-project-root.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: docs(review): qualify duplicate headings
group 1 path: docs/v0.14.0/review.design-specification.v0.14.0.release-project-root.md
group 2: perf(tests): reuse CLI and repository initialization
group 2 path: tests/acceptance/commit_plan_check/__init__.py
group 2 path: tests/acceptance/commit_plan_check/commit_plan_check_support.py
group 2 path: tests/acceptance/commit_plan_check/conftest.py
group 2 path: tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_acceptance_tdd.py
group 2 path: tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_contracts_tdd.py
group 2 path: tests/acceptance/review_resume/__init__.py
group 2 path: tests/acceptance/review_resume/cli_support.py
group 2 path: tests/acceptance/review_resume/conftest.py
group 2 path: tests/acceptance/review_resume/waiter_driver.py
group 2 path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_acceptance_tdd.py
group 2 path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_concurrency_tdd.py
group 2 path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_identity_tdd.py
group 2 path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_parked_wait_tdd.py
group 2 path: tests/acceptance/review_status/conftest.py
group 2 path: tests/unit/tools/git_test_double.py
group 2 path: tests/unit/tools/test_code_reviewer_acceptance/fixtures.py
group 3: feat(release): validate setup-owned runtime
group 3 path: bin/release_runtime_record.bat
group 3 path: docs/v0.14.0/plan.v0.14.0.release-project-root.md
group 3 path: pyproject.toml
group 3 path: senv.bat
group 3 path: tests/acceptance/release_workflow/__init__.py
group 3 path: tests/acceptance/release_workflow/conftest.py
group 3 path: tests/acceptance/release_workflow/process_support.py
group 3 path: tests/acceptance/release_workflow/test_release_readiness_tdd.py
group 3 path: tests/acceptance/release_workflow/test_uv_readiness_tdd.py
group 3 path: tests/unit/tools/release_workflow/__init__.py
group 3 path: tests/unit/tools/release_workflow/conftest.py
group 3 path: tests/unit/tools/release_workflow/test_bootstrap/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_markers/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_markers/test_markers_pbt.py
group 3 path: tests/unit/tools/release_workflow/test_markers/test_markers_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_readiness/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_readiness/test_faults_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_readiness/test_metadata_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_readiness/test_readiness_pbt.py
group 3 path: tests/unit/tools/release_workflow/test_readiness/test_readiness_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_runtime/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_runtime/test_runtime_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_support.py
group 3 path: tools/release_workflow/__init__.py
group 3 path: tools/release_workflow/bootstrap.py
group 3 path: tools/release_workflow/markers.py
group 3 path: tools/release_workflow/readiness.py
group 3 path: tools/release_workflow/runtime_identity.py
group 3 path: uv.lock
group 4: docs(release-project-root): record step 1 validation
group 4 path: docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md
staged path: bin/release_runtime_record.bat
staged path: docs/v0.14.0/plan.v0.14.0.release-project-root.md
staged path: docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md
staged path: docs/v0.14.0/review.design-specification.v0.14.0.release-project-root.md
staged path: pyproject.toml
staged path: senv.bat
staged path: tests/acceptance/commit_plan_check/__init__.py
staged path: tests/acceptance/commit_plan_check/commit_plan_check_support.py
staged path: tests/acceptance/commit_plan_check/conftest.py
staged path: tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_acceptance_tdd.py
staged path: tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_contracts_tdd.py
staged path: tests/acceptance/release_workflow/__init__.py
staged path: tests/acceptance/release_workflow/conftest.py
staged path: tests/acceptance/release_workflow/process_support.py
staged path: tests/acceptance/release_workflow/test_release_readiness_tdd.py
staged path: tests/acceptance/release_workflow/test_uv_readiness_tdd.py
staged path: tests/acceptance/review_resume/__init__.py
staged path: tests/acceptance/review_resume/cli_support.py
staged path: tests/acceptance/review_resume/conftest.py
staged path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_acceptance_tdd.py
staged path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_concurrency_tdd.py
staged path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_identity_tdd.py
staged path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_parked_wait_tdd.py
staged path: tests/acceptance/review_resume/waiter_driver.py
staged path: tests/acceptance/review_status/conftest.py
staged path: tests/unit/tools/git_test_double.py
staged path: tests/unit/tools/release_workflow/__init__.py
staged path: tests/unit/tools/release_workflow/conftest.py
staged path: tests/unit/tools/release_workflow/test_bootstrap/__init__.py
staged path: tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py
staged path: tests/unit/tools/release_workflow/test_markers/__init__.py
staged path: tests/unit/tools/release_workflow/test_markers/test_markers_pbt.py
staged path: tests/unit/tools/release_workflow/test_markers/test_markers_tdd.py
staged path: tests/unit/tools/release_workflow/test_readiness/__init__.py
staged path: tests/unit/tools/release_workflow/test_readiness/test_faults_tdd.py
staged path: tests/unit/tools/release_workflow/test_readiness/test_metadata_tdd.py
staged path: tests/unit/tools/release_workflow/test_readiness/test_readiness_pbt.py
staged path: tests/unit/tools/release_workflow/test_readiness/test_readiness_tdd.py
staged path: tests/unit/tools/release_workflow/test_runtime/__init__.py
staged path: tests/unit/tools/release_workflow/test_runtime/test_runtime_tdd.py
staged path: tests/unit/tools/release_workflow/test_support.py
staged path: tests/unit/tools/test_code_reviewer_acceptance/fixtures.py
staged path: tools/release_workflow/__init__.py
staged path: tools/release_workflow/bootstrap.py
staged path: tools/release_workflow/markers.py
staged path: tools/release_workflow/readiness.py
staged path: tools/release_workflow/runtime_identity.py
staged path: uv.lock
```

### Validation scope for step 1 release-project-root (round 5)

Validation scope: the whole suite.

### Requestor assessment for step 1 release-project-root (round 5)

No. Step 1 has NOT been fully implemented.

The human explicitly authorized this replacement: "yes. Do publish round 5",
in response to the prepared draft and the question whether to publish with
the intermittent identity failure explicitly unresolved. The normal all-green
publication prerequisite is not met; this round records that human exception
and does not claim green validation.

R1-R8 remain resolved, including the human's two named live-UV timing
exceptions. R10 is repaired: the competing-reviewer fixture initializes an
empty process list and appends both waiter starts inside its try/finally.
The first child is therefore covered by cleanup if the second startup fails.
All existing assertions and independent real waiter processes remain. Its
focused groundhog run passed all three tests; the final static check passed.

R9 remains unresolved. The last post-R8 whole-suite speed day passed 3,699
affected tests and 100% tools coverage, then failed in sequential timings
with two setup errors sharing identity_journey[gemini]. The first resume
returned no ownership capability. The early diagnostic assertion improves
failure reporting but is not a root-cause fix.

Focused identity and review-resume runs, 80 independent identity journeys,
a 63-test acceptance prefix in suite order, and the same prefix after full
collection of all 3,699 tests passed without reproducing R9. These selected
diagnostics establish neither a repair nor whole-suite speed proof.
No unchanged full walk was repeated to seek a green result.

Architecture and production behavior are unchanged since Round 3. Test
assertions, real UV generation, and the 1.0-second setup + call + teardown
ceiling remain. The two accepted UV exceptions remain visible in raw timing
reports; 48 other breaches remain separately tracked as authorized.

This request asks for assessment of the R10 repair and the new R9 diagnostic
evidence while retaining the incomplete assessment. No commit or Step 2 is
authorized, and no current full-speed or total-duration compliance is claimed.

### Implementation report for step 1 release-project-root (round 5)

Step 1 produces a setup-owned two-line runtime identity, validates physical
containment, interpreter requirements and the locked release closure, and
delays engine imports until readiness succeeds. R1-R6 repairs remain intact.
The release group stays stdlib-only and is included by dev. The production
CLI remains Step 5 work; Step 1 uses a disposable engine probe and checks
missing-engine failure. No production code changed after Round 3.

Round 4 accepted R8: independent real waiters signal their first notification
wait after startup validation and initial discovery. The parent waits for
that signal before mutation. All silence, terminal-result, Git, notification
and ownership assertions remain.

The writer repaired Round 4 finding R10 in the competing-reviewer fixture.
Both start_wait calls are now inside the try/finally, each appending its
successfully started child to an initially empty list. Cleanup can therefore
collect the first indefinite waiter when the second startup raises. No
assertion or cleanup behavior was removed.

R9 remains open. The post-R8 speed day passed check, 3,699 affected tests and
100% tools coverage, then exited 2 in sequential timings at 21:35:19 +02:00
on 2026-10-22. Both setup errors shared identity_journey[gemini]; its first
resume yielded no ownership capability. The retained early assertion reports
exit code, operation, outcome and diagnostic without ownership credentials.
It is diagnostic only. No production or fixture root cause is established.

New diagnostics tested two specific ordering hypotheses. A sequential run
executed the 63 acceptance tests preceding and including the identity module.
A second run collected the entire 3,699-test suite before executing that same
63-test prefix, to include full-suite import effects. Both passed. The latter
selection uses a private diagnostic plugin only; no tracked gate, selection,
exclusion or test configuration changed. These results do not fix R9 or
replace the failed full walk. Affected, single and timings are sequential;
only ghog full uses xdist. Earlier reviewer descriptions of affected as
parallel were inaccurate and have been corrected in the validation notes.

Evidence:

- .reviews/a.release-project-root.step1.tmp.r5.concurrency.log: three focused
  concurrency tests passed, exit 0, no failures, warnings or xfails.
- .reviews/a.release-project-root.step1.tmp.r5.sequence.log: 63-test sequential
  acceptance prefix passed without reproducing R9.
- .reviews/a.release-project-root.step1.tmp.r5.collection.log and matching
  collection.json: full collection, then the same 63-test prefix; exit 0.
- .reviews/a.release-project-root.step1.tmp.r5.check.log: final static checks
  after the R10 repair and validation-note changes, exit 0.
- .reviews/a.release-project-root.step1.tmp.timing/round4-first-groundhog.log:
  failed whole-suite speed day; successful affected and coverage stages do
  not make its failed sequential timings a speed proof.
- .reviews/a.release-project-root.step1.tmp.r4.identity.log, resume.log and
  identity-probe.log (each with the same a.release-project-root.step1.tmp.r4
  filename prefix): earlier focused passes and 80 diagnostic journeys.

R7 retains real offline UV generation and every shape/readiness assertion.
Accepted named exceptions, measured as setup + call + teardown in the last
successful full audit:

- tests/acceptance/release_workflow/test_uv_readiness_tdd.py::test_uv_generated_empty_shapes[no-dev-edges]: 1.8040s.
- tests/acceptance/release_workflow/test_uv_readiness_tdd.py::test_uv_generated_empty_shapes[with-dev-edges]: 1.9385s.

Attempted improvements split the original combined fixture into one fixture
per shape and tried explicit interpreter selection, reduced workers, isolated
UV settings, console suppression and executable linking. Native UV process
creation alone measured about 0.91s; useful resolution took milliseconds.
None cleared the ceiling. The human chose live integration coverage. No host
settings changed. The general 1.0-second ceiling remains, and raw reports keep
both exceptions. No stored lock, retry, skip, xfail, call-only exclusion or
raised global ceiling was introduced.

Historical pre-R8 proof completed 2026-10-22 17:50:24 +02:00: 3,699 tests,
100% tools coverage and speed proof. Its strict total-phase audit reported
50 breaches and 371.5959s summed phases: setup 302.4019s, call 67.1606s,
teardown 2.0334s. Every Step 1 process scenario was below 0.630s. The other
48 breaches remain deferred by the human. These historical measurements
predate R8 and do not prove the current tree. Evidence is retained under
.reviews/a.release-project-root.step1.tmp.timing/round3-final-*.

Writer notes: `.reviews/a.release-project-root.step1.journal.md` and
`.reviews/a.release-project-root.step1.handoff.md`.

### Change summary for step 1 release-project-root (round 5)

The staged work has four ordered a.commit groups:

1. docs(review): qualify duplicate headings
2. perf(tests): reuse CLI and repository initialization
3. feat(release): validate setup-owned runtime
4. docs(release-project-root): record step 1 validation

The latest canonical wac and commit-plan-check verification passed: ready=true,
48 staged paths, and no diagnostics. Both staged and worktree whitespace
checks pass with CRLF-aware settings. The lock clean filter was retained.

Current staged paths:

- `bin/release_runtime_record.bat`
- `docs/v0.14.0/plan.v0.14.0.release-project-root.md`
- `docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md`
- `docs/v0.14.0/review.design-specification.v0.14.0.release-project-root.md`
- `pyproject.toml`
- `senv.bat`
- `tests/acceptance/commit_plan_check/__init__.py`
- `tests/acceptance/commit_plan_check/commit_plan_check_support.py`
- `tests/acceptance/commit_plan_check/conftest.py`
- `tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_acceptance_tdd.py`
- `tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_contracts_tdd.py`
- `tests/acceptance/release_workflow/__init__.py`
- `tests/acceptance/release_workflow/conftest.py`
- `tests/acceptance/release_workflow/process_support.py`
- `tests/acceptance/release_workflow/test_release_readiness_tdd.py`
- `tests/acceptance/release_workflow/test_uv_readiness_tdd.py`
- `tests/acceptance/review_resume/__init__.py`
- `tests/acceptance/review_resume/cli_support.py`
- `tests/acceptance/review_resume/conftest.py`
- `tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_acceptance_tdd.py`
- `tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_concurrency_tdd.py`
- `tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_identity_tdd.py`
- `tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_parked_wait_tdd.py`
- `tests/acceptance/review_resume/waiter_driver.py`
- `tests/acceptance/review_status/conftest.py`
- `tests/unit/tools/git_test_double.py`
- `tests/unit/tools/release_workflow/__init__.py`
- `tests/unit/tools/release_workflow/conftest.py`
- `tests/unit/tools/release_workflow/test_bootstrap/__init__.py`
- `tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py`
- `tests/unit/tools/release_workflow/test_markers/__init__.py`
- `tests/unit/tools/release_workflow/test_markers/test_markers_pbt.py`
- `tests/unit/tools/release_workflow/test_markers/test_markers_tdd.py`
- `tests/unit/tools/release_workflow/test_readiness/__init__.py`
- `tests/unit/tools/release_workflow/test_readiness/test_faults_tdd.py`
- `tests/unit/tools/release_workflow/test_readiness/test_metadata_tdd.py`
- `tests/unit/tools/release_workflow/test_readiness/test_readiness_pbt.py`
- `tests/unit/tools/release_workflow/test_readiness/test_readiness_tdd.py`
- `tests/unit/tools/release_workflow/test_runtime/__init__.py`
- `tests/unit/tools/release_workflow/test_runtime/test_runtime_tdd.py`
- `tests/unit/tools/release_workflow/test_support.py`
- `tests/unit/tools/test_code_reviewer_acceptance/fixtures.py`
- `tools/release_workflow/__init__.py`
- `tools/release_workflow/bootstrap.py`
- `tools/release_workflow/markers.py`
- `tools/release_workflow/readiness.py`
- `tools/release_workflow/runtime_identity.py`
- `uv.lock`

Round 5 repairs R10 by placing both waiter starts inside the competing-journey
cleanup scope. Group 2 records that repair and retains the earlier R8 waiter
synchronization and identity diagnostic. All assertions remain. The validation
document records the R10 focused pass and sequential diagnostic evidence,
removes R10 from missing work, and keeps R9 and the exact incomplete assessment.
Two additional private diagnostics passed without reproducing R9, including
the 63-test prefix after full-suite collection. Neither supplies a repair or
current speed proof. Production code is unchanged since Round 3. All earlier
repairs remain accepted; no repair was reversed. Staged paths and the four
commit groups are unchanged in membership.

The generated code-review transcript evolves through exchange publication and
remains outside this prepared index. The human explicitly authorized Round 5
publication with R9 open. No commit is authorized or performed.

### Human guidance and writer response for step 1 release-project-root (round 5)

Human guidance:

Existing human instructions remain: keep live UV generation and all
assertions; preserve the 1.0-second setup + call + teardown ceiling and the
two named UV exceptions; track the other 48 timing breaches separately;
finish Step 1 before continuing. Work on one optimization at a time.

The latest human instruction is "yes. Do publish round 5". It answers the
specific question whether to publish the prepared Round 5 with the intermittent
identity failure explicitly unresolved, after the missing green-validation
prerequisite was disclosed. Publish for assessment of the R10 repair and R9
diagnostic evidence. R9 stays open and Step 1 stays incomplete. No current
whole-suite speed proof or total-duration compliance is claimed.

No commit or Step 2 is authorized. The reviewer role remains independent.

Writer response:

The writer accepts the Round 4 assessment and its validation metadata repair.
No reviewer repair has been reversed. R1-R8 remain resolved. R7 retains the
human's live-UV choice and two named exceptions; R8 synchronization remains.

R10 is repaired exactly as requested: initialize an empty process list before
try, then append each start_wait result inside try. The existing finally now
covers a first child when the second startup fails. The focused concurrency
module passed all three tests. Group 2 in a.commit names the cleanup repair.

R9 remains unresolved. Following the requested suite-order investigation,
63 acceptance tests through the identity module passed sequentially. A second
diagnostic collected all 3,699 tests before executing that same prefix and
also passed. Prior focused modules and 80 identity journeys passed. No run
reproduced the missing first-resume capability, and no root-cause repair is
claimed. The early diagnostic assertion remains in place. No retry, skip,
xfail, assertion removal or gate exclusion was added.

The validation plan retains the exact No/incomplete assessment and R9 missing
work. It records the R10 repair and focused pass. It also corrects the
reviewer's description of affected execution: affected and timing stages are
sequential; only the full coverage stage uses xdist. This factual correction
does not reject any repair or weaken R9's unresolved status.

If evidence establishes a cause in review-exchange production code, report
that evidence and obtain a scope decision before changing it outside Step 1.

The human explicitly answered "yes. Do publish round 5" after inspecting
the prepared draft and being asked whether to publish with R9 unresolved.
This authorizes publication despite the missing green-validation prerequisite.
It does not resolve R9, supply current whole-suite proof or authorize a commit
or Step 2 action.

### Reviewer focus for step 1 release-project-root (round 5)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-1-round-5 -->

## Round 5 by reviewer - Step 1

- Recorded: 2026-10-22T23:38:26+02:00
- Exchange: code/code/v0.14.0/release-project-root
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.release-project-root.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 1
- Outcome: answer

### Assessed index identity for step 1 release-project-root (exchange 1) (round 5)

Baseline index tree: a13e5685e914002404399d1c5fe06021fe2844ea

Assessed index tree: 4adfdae9c157e692966835905a42914dd54c6f40

### Implementation check for step 1 release-project-root (exchange 1) (round 5)

Result:

No. Step 1 has NOT been fully implemented.

R10 is fixed. R9, the intermittent Gemini identity-fixture failure, stays
open, so Step 1 still has no green whole-suite walk. The writer's correction
about the affected stage is right, and it changes what the passing runs prove.
Code reading this round found one concrete R9 lead in production code; it is
not established. The reviewer refreshed the Step 1 rows to match and kept the
exact No sentence.

Changes checked against the diff from the round 4 assessed tree `b84f6a14…`
to `a13e5685…`. Two files changed: the validation plan and
`test_review_resume_concurrency_tdd.py`. Production code is unchanged since
round 3.

- R10: `competing_journey` now types an empty `processes` list before `try`
  and appends each `start_wait` result inside it. The existing `finally` kills
  and collects every started child. If the second start raises, the first
  waiter is collected. Every assertion, both independent real waiters and
  real Git stay.
- Affected-stage correction: the writer is right, and the reviewer's round 4
  wording was wrong. In `tools/groundhog/runner.py`, only `ghog full` runs on
  xdist (`worker_run = sub == SUB_FULL and parallel`). `affected` is
  sequential under `--testmon`. `timings` is sequential, without testmon,
  with `--no-cov` and `--durations=0`. Testmon also reorders the run:
  `sort_items_by_duration` sorts selected tests by average duration. So the
  passing affected stages, the writer's and the reviewer's, ran in one
  process but not in collection order, and under testmon's tracer. The
  failing timings stage ran in collection order and uninstrumented. The
  writer's `ghog single` prefix runs had that same shape and passed. So the
  failure is not bound to order alone.
- R9 lead, from code reading only: in the first resume, `claim` with a
  selected role runs `_backfill_selected` in `tools/review_resume_identity.py`.
  That calls `RoleNatureBackfill._replace_all` in
  `tools/review_role_nature.py`, which atomically replaces the request and the
  coordination record with no transient-sharing handling. Any `OSError` there
  becomes "atomic role-nature backfill failed", and the claim then returns no
  capability. The second resume would then raise the observed `KeyError` at
  `conftest.py:263`. The ownership store's `_commit_prepared` and the
  migration journal's `_commit_snapshot` both retry `PermissionError` with
  bounded backoff for exactly this Windows case; the backfill does not. The
  identity journey is the scenario that runs this backfill. A Windows file
  handle still open on either target can cause it: a scanner or indexer, or a
  handle left by an earlier in-process CLI call that only the cyclic garbage
  collector would close. Separate processes always closed such handles at
  exit, which group 2's `run_inline` no longer guarantees. This is
  consistent with the evidence but not proven. The retained diagnostic
  assertion will name the operation and message on the next occurrence.

R1 to R8 stay resolved; their files are unchanged since round 4.

Architecture: no production change this round; the R10 change is three lines
of fixture code.

Performance: production code is unchanged. The test-side position is still
the two named UV exceptions; the other 48 breaches stay tracked separately.

Static coverage: no `tools` module changed since round 3, when the full gate
reported 100%. The post-R8 `ghog full` stage also reported 100%.

Feature integrity: no assertion, test, real process boundary or marker was
removed. No `skip`, `xfail`, retry or exclusion was added. The open gap is
that the current tree has no green whole-suite walk (R9).

Validation plan effects:

The reviewer updated only the Step 1 rows of
`docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md`:

- *Analysis*: kept the exact No sentence. The R8 paragraph now names the
  remaining gap as R9 and records that this review accepted the R10 repair.
- *What was implemented*: added that testmon sorts the affected stage by
  duration, so only the failing timings stage and the prefix runs used
  collection order. Added the reviewer's round 5 `ghog check` and
  `ghog affected --no-cov` evidence.
- *Missing work*: kept the R9 bullet and replaced its two generic candidates
  with the concrete, unproven backfill lead, the confirm-first step, and the
  boundary between a test-side fix and production scope.

The document-level line stays `No, it is not implemented`. Other steps, the
plan, the umbrella, implementation, tests and `a.commit` were not edited.

The evidence launcher attributed the patch against the pre-edit blob
`df90f51c0795ce2d30b7d4e3c414c9f3ed03b74f` (attributable, not created). Only
that patch was staged. The project Markdown check and `git diff --check` pass.
This is review metadata, not a substantive repair.

### Pre-repair mandatory checks and coverage for step 1 release-project-root (exchange 1) (round 5)

Requestor evidence, as reported and not repeated: no green
`ghog day --full=speed --whole-suite` exists for the current tree. The
post-R8 walk passed `ghog check`, `ghog affected` over 3,699 tests and
`ghog full` at `cov=100`. Its timings stage then exited 2 with two setup
errors in `identity_journey[gemini]` (R9). After the R10 repair, the focused
concurrency module passed its three tests and `ghog check` passed. Two private
`ghog single` diagnostics passed: the 63-test collection-order prefix
through the identity module, and the same prefix after collecting all 3,699
tests. Neither reproduced R9. The last complete walk, at 17:50:24 +02:00,
predates R8.

Reviewer evidence, each command run once from the project root through the
shared `ghog.bat` launcher, with the log-freshness proof and
`SWITCHPY_CHOICE=local` set for that process only:

- `ghog check`: exit 0. All static, EOF and Markdown checks passed.
- `ghog affected --no-cov --scope-file=.reviews/a.review-scope.code.v0.14.0.release-project-root.json`:
  exit 0, scope whole, `fail=0 warn=0 xfail=0`. Testmon selected one test
  after the R10 fixture change; the log names no node ID. This is not
  whole-suite evidence.

Correction to the round 4 answer: it called the affected stage parallel. It
is sequential under testmon; only `ghog full` uses xdist. The round 4
conclusion stands for a different reason: testmon reorders by duration, so a
passing affected stage does not reproduce the failing collection-order pass.
The reviewer did not run `ghog day`, `ghog full`, the strict audit or any
coverage measurement. Coverage was assessed statically.

### Resolved validation set and sources for step 1 release-project-root (exchange 1) (round 5)

The request and the current resolver produce the same ordered set as in
round 4:

1. `ghog day --full=speed --whole-suite`: source project.
2. `rg -n 'VIRTUAL_ENV|PYTHONPATH|glob|rglob|import_module' tools/release_workflow`:
   source plan.
3. `ghog check`: source request.

No `.review-validation` file exists. Re-running `resolve_code_review_validation`
from the current `tools/code_review_validation.py` this round reproduced this
exact set. The reviewer did not run the resolved set; its own `ghog check` run
is reviewer evidence. The requestor reports no green run of the first command
on the current tree (R9).

### Resolver drift and direction for step 1 release-project-root (exchange 1) (round 5)

None: ordered commands and source labels agree with the current resolver.

### Repository state around validation for step 1 release-project-root (exchange 1) (round 5)

Request-time and reviewer baseline index tree:
`a13e5685e914002404399d1c5fe06021fe2844ea` (identical). Final assessed index
tree after the reviewer metadata patch: `4adfdae9c157e692966835905a42914dd54c6f40`.

The same ordered 50-path validation set was captured before and after
assessment: the 48 staged paths plus the ignored `a.ghog.log` and
`a.ghog.status`. Tracked differences appear only for
`docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md`. Ignored
differences appear only for the two ghog files written by the reviewer's
evidence commands, and there are no untracked differences. The raw
`acceptable=false` reflects the intentional Step 1 metadata edit. The
reviewer's ghog runs left no tracked side effect. There is no overlap with
writer work, and the only other working-tree entry is the untracked exchange
transcript, which the protocol owns.

Umbrella `docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md`: applicable,
digest `ca6fe473…0ec992` before and after, unchanged. No umbrella row was
modified.

Retained evidence: `.reviews/a.code-review-evidence.v0.14.0.release-project-root.step-1.json`,
with the inputs under `.reviews/a.release-project-root.step1.tmp.r5.review-*`.

### Repair inventory for step 1 release-project-root (exchange 1) (round 5)

Repairs made:

- Review metadata only: refreshed the Step 1 validation rows. The analysis
  names R9 as the remaining gap and records R10 as accepted. The implemented
  row gained the testmon ordering detail and the reviewer's round 5 evidence.
  The R9 missing-work bullet now carries the concrete backfill lead. No
  implementation, test, plan or `a.commit` repair.

Paths staged:

- docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md (reviewer metadata patch only)

### Commit plan assessment for step 1 release-project-root (exchange 1) (round 5)

Ran `commit-plan-check.bat --format json` independently before assessment and
again after staging the Step 1 metadata. Both returned exit 0, `state=valid`,
`ready=true`, four ordered groups, 48 staged paths and no diagnostics. The JSON
is retained in `.reviews/a.release-project-root.step1.tmp.r5.review-commit-plan.json`
and `.reviews/a.release-project-root.step1.tmp.r5.review-commit-plan-after.json`.

Ordered groups:

1. `docs(review): qualify duplicate headings` (1 path)
2. `perf(tests): reuse CLI and repository initialization` (16 paths)
3. `feat(release): validate setup-owned runtime` (30 paths)
4. `docs(release-project-root): record step 1 validation` (1 path)

Membership, order and conventional subjects match the staged work. Group 2's
body now names the R10 cleanup ("Clean up the first waiter if starting its
competitor fails"), and group 4 still records the unresolved timing-run
failure. The reviewer did not amend `a.commit`. When R9 is fixed, the body of
the group that receives the fix should name it. Mechanical readiness does not
resolve R9 and does not authorize a commit.

### Findings and boundaries for step 1 release-project-root (exchange 1) (round 5)

Unresolved findings:

- R9 (P2): the identity fixture fails intermittently, so the requestor's
  resolved validation set is not green on the current tree. The post-R8
  `ghog day --full=speed --whole-suite` exited 2 in its timings stage. Both
  tests sharing
  `tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_identity_tdd.py::identity_journey[gemini]`
  errored at setup, because the first resume returned no capability. The
  passing affected stages ran sequentially under testmon, which sorts tests by
  duration and traces them; the failing timings stage ran in collection order
  without a tracer. The writer's uninstrumented collection-order prefix runs
  passed, so order alone does not explain the failure. Code reading points to
  one concrete, unproven lead. The first resume's `claim` runs
  `RoleNatureBackfill._replace_all` (`tools/review_role_nature.py`), which
  atomically replaces the request and coordination record with no
  transient-sharing handling. Any `OSError` there fails the claim without a
  capability. The ownership store and migration journal retry the same Windows
  `PermissionError` with bounded backoff. Possible holders of the target file
  are an external scanner or indexer, or a handle left open by an earlier
  in-process `run_inline` call until garbage collection. Confirm the operation
  and message before changing anything. A test-side handle leak is a Step 1 fix
  in the staged fixtures or runner. A production retry gap is boundary work.
  Do not add a test-level retry, skip, xfail or exclusion.

Boundary-crossing work:

- If R9's cause is the missing transient-sharing handling in
  `RoleNatureBackfill._replace_all` (`tools/review_role_nature.py`), or any
  other review-exchange production code, that repair is outside Step 1.
  Report the diagnostic and the holder evidence and ask the human for its
  scope before changing production code.

### Human guidance response for step 1 release-project-root (exchange 1) (round 5)

Human guidance:

The user's latest instruction is "yes. Do publish round 5". It answers
whether to publish the prepared round 5 with the intermittent identity failure
explicitly unresolved, after the missing green-validation prerequisite was
disclosed. Publish for assessment of the R10 repair and the R9 diagnostic
evidence. R9 stays open and Step 1 stays incomplete. No current whole-suite
speed proof or total-duration compliance is claimed.

Earlier instructions remain: keep live UV generation and every assertion;
keep the 1.0-second setup + call + teardown ceiling and the two named UV
exceptions; track the other 48 timing breaches separately; finish Step 1
before continuing; work on one optimization at a time. No commit or Step 2 is
authorized, and the reviewer role stays independent.

Guidance response:

The guidance asks for assessment and does not instruct a reviewer repair, so
the reviewer changed no implementation or test file. The request's general
"make every safe repair" wording does not override that rule. Its only change
is the Step 1 validation-row refresh.

Scope: the staged work stays within Step 1. Nothing from Step 2 was found.
This answer authorizes no commit.

The human's "yes. Do publish round 5" is honored as stated: this round is
assessed with R9 open, and nothing in it is treated as whole-suite proof.

R10, assessed explicitly: fixed, as requested, with both real waiters and
every assertion kept.

R9 diagnostic evidence, assessed explicitly:

- The two prefix runs are sound diagnostics. The collection probe is a
  private plugin loaded only through that run's environment. No tracked gate,
  selection or configuration changed.
- The writer correctly claims neither a repair nor proof from them.
- They show that collection order alone does not reproduce the failure.
- The correction that `affected` is sequential is accepted, and the Step 1
  rows already carry it.
- The reviewer adds the testmon reordering detail and the backfill lead.

R7 and the 48 tracked breaches are unchanged and do not count against this
round.

### Writer instructions for step 1 release-project-root (exchange 1) (round 5)

Fix R9. Start with the identity diagnostic. Without running an unchanged full
walk to seek a green result, gather the failing operation and message in one
of two ways:

- run the stage that failed in its exact shape, the uninstrumented
  collection-order timings pass over the whole suite;
- or test the handle lead directly: with `ResourceWarning` enabled, for
  example `PYTHONWARNINGS=always::ResourceWarning`, a focused sequential run
  of the review-resume package reports any file an in-process CLI call leaves
  unclosed.

If the diagnostic shows "atomic role-nature backfill failed" during `claim`,
find what held the request or coordination file. A handle from an earlier
in-process call is a test-side leak: close it at its source, or keep the
affected calls in separate processes, inside the staged fixtures or runner.
An external holder means production `RoleNatureBackfill._replace_all` lacks
the bounded `PermissionError` handling its sibling stores have. Stop and
report that as boundary work for a human scope decision. If the diagnostic
names another operation, fix that cause instead. Keep every identity
assertion and the diagnostic, and add no test-level retry, skip, xfail or
exclusion.

Then run the requestor-owned resolved set green:
`ghog day --full=speed --whole-suite`, the plan's `rg` scan and `ghog check`.
Re-run the strict total-duration audit and confirm that the only Step 1
breaches are the two named UV exceptions. Refresh the Step 1 rows. Open with
`Yes. Step 1 has been fully implemented.` and remove *Missing work for Step 1*
only when R9 is fixed and that walk is green. Name the fix in the body of the
`a.commit` group that receives it, then publish the replacement request
through the normal requestor workflow.

The reviewer's only staged change is the attributable Step 1 validation-row
refresh.

### Decision rationale for step 1 release-project-root (exchange 1) (round 5)

Recommend changes-requested. The six readiness-floor results are:

1. Identity: PASS. The exact plan, step 1, round 5, occurrence 1, code
   identity, umbrella and request-time index tree agree with the live exchange.
2. Implementation completeness: FAIL. R9, the intermittent identity-fixture
   failure, remains.
3. Validation and coverage: FAIL. No green
   `ghog day --full=speed --whole-suite` exists for the current tree. The
   reviewer's `ghog check` and `ghog affected --no-cov` are green, and the
   static coverage walk finds no gap.
4. Staged attribution: PASS. The sole reviewer change is the attributable
   Step 1 validation-row refresh. There is no substantive repair and no
   unrelated staged work.
5. Unresolved findings: FAIL. R9 (P2) remains. R1 to R8 and R10 are
   resolved, R7 by the human's named exceptions.
6. `a.commit`: PASS mechanically. The independent checker reports exit 0,
   valid, ready, with all 48 paths in four accurate groups.

R10 is done exactly as asked, and the writer's diagnostics were careful and
honestly reported. Step 1 still needs R9's cause and a green whole-suite walk
before it can be recommended for commit.

### Final reviewer decision for step 1 release-project-root (exchange 1) (round 5)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-1-round-5 -->

## Round 6 by requestor - Step 1

- Recorded: 2026-10-23T09:46:22+02:00
- Exchange: code/code/v0.14.0/release-project-root
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.release-project-root.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 1
- Outcome: request

### Review identity for step 1 release-project-root (round 6)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.release-project-root.md
Implementation step: 1
Review round: 6

### Code review evidence for step 1 release-project-root (round 6)

request_index_tree: e37db5d545177e2b413807749891128154524339
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)
- `rg -n 'VIRTUAL_ENV|PYTHONPATH|glob|rglob|import_module' tools/release_workflow` (sources: plan)
- `ghog check` (sources: request)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "missing", "requirement": "docs/v0.14.0/feature-request.v0.14.0.release-project-root.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: docs(review): qualify duplicate headings
group 1 path: docs/v0.14.0/review.design-specification.v0.14.0.release-project-root.md
group 2: perf(tests): reuse CLI and repository initialization
group 2 path: tests/acceptance/commit_plan_check/__init__.py
group 2 path: tests/acceptance/commit_plan_check/commit_plan_check_support.py
group 2 path: tests/acceptance/commit_plan_check/conftest.py
group 2 path: tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_acceptance_tdd.py
group 2 path: tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_contracts_tdd.py
group 2 path: tests/acceptance/review_resume/__init__.py
group 2 path: tests/acceptance/review_resume/cli_support.py
group 2 path: tests/acceptance/review_resume/conftest.py
group 2 path: tests/acceptance/review_resume/waiter_driver.py
group 2 path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_acceptance_tdd.py
group 2 path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_concurrency_tdd.py
group 2 path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_identity_tdd.py
group 2 path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_parked_wait_tdd.py
group 2 path: tests/acceptance/review_status/conftest.py
group 2 path: tests/unit/tools/git_test_double.py
group 2 path: tests/unit/tools/test_code_reviewer_acceptance/fixtures.py
group 3: feat(release): validate setup-owned runtime
group 3 path: bin/release_runtime_record.bat
group 3 path: docs/v0.14.0/plan.v0.14.0.release-project-root.md
group 3 path: pyproject.toml
group 3 path: senv.bat
group 3 path: tests/acceptance/release_workflow/__init__.py
group 3 path: tests/acceptance/release_workflow/conftest.py
group 3 path: tests/acceptance/release_workflow/process_support.py
group 3 path: tests/acceptance/release_workflow/test_release_readiness_tdd.py
group 3 path: tests/acceptance/release_workflow/test_uv_readiness_tdd.py
group 3 path: tests/unit/tools/release_workflow/__init__.py
group 3 path: tests/unit/tools/release_workflow/conftest.py
group 3 path: tests/unit/tools/release_workflow/test_bootstrap/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_markers/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_markers/test_markers_pbt.py
group 3 path: tests/unit/tools/release_workflow/test_markers/test_markers_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_readiness/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_readiness/test_faults_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_readiness/test_metadata_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_readiness/test_readiness_pbt.py
group 3 path: tests/unit/tools/release_workflow/test_readiness/test_readiness_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_runtime/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_runtime/test_runtime_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_support.py
group 3 path: tools/release_workflow/__init__.py
group 3 path: tools/release_workflow/bootstrap.py
group 3 path: tools/release_workflow/markers.py
group 3 path: tools/release_workflow/readiness.py
group 3 path: tools/release_workflow/runtime_identity.py
group 3 path: uv.lock
group 4: docs(release-project-root): record step 1 validation
group 4 path: docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md
staged path: bin/release_runtime_record.bat
staged path: docs/v0.14.0/plan.v0.14.0.release-project-root.md
staged path: docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md
staged path: docs/v0.14.0/review.design-specification.v0.14.0.release-project-root.md
staged path: pyproject.toml
staged path: senv.bat
staged path: tests/acceptance/commit_plan_check/__init__.py
staged path: tests/acceptance/commit_plan_check/commit_plan_check_support.py
staged path: tests/acceptance/commit_plan_check/conftest.py
staged path: tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_acceptance_tdd.py
staged path: tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_contracts_tdd.py
staged path: tests/acceptance/release_workflow/__init__.py
staged path: tests/acceptance/release_workflow/conftest.py
staged path: tests/acceptance/release_workflow/process_support.py
staged path: tests/acceptance/release_workflow/test_release_readiness_tdd.py
staged path: tests/acceptance/release_workflow/test_uv_readiness_tdd.py
staged path: tests/acceptance/review_resume/__init__.py
staged path: tests/acceptance/review_resume/cli_support.py
staged path: tests/acceptance/review_resume/conftest.py
staged path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_acceptance_tdd.py
staged path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_concurrency_tdd.py
staged path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_identity_tdd.py
staged path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_parked_wait_tdd.py
staged path: tests/acceptance/review_resume/waiter_driver.py
staged path: tests/acceptance/review_status/conftest.py
staged path: tests/unit/tools/git_test_double.py
staged path: tests/unit/tools/release_workflow/__init__.py
staged path: tests/unit/tools/release_workflow/conftest.py
staged path: tests/unit/tools/release_workflow/test_bootstrap/__init__.py
staged path: tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py
staged path: tests/unit/tools/release_workflow/test_markers/__init__.py
staged path: tests/unit/tools/release_workflow/test_markers/test_markers_pbt.py
staged path: tests/unit/tools/release_workflow/test_markers/test_markers_tdd.py
staged path: tests/unit/tools/release_workflow/test_readiness/__init__.py
staged path: tests/unit/tools/release_workflow/test_readiness/test_faults_tdd.py
staged path: tests/unit/tools/release_workflow/test_readiness/test_metadata_tdd.py
staged path: tests/unit/tools/release_workflow/test_readiness/test_readiness_pbt.py
staged path: tests/unit/tools/release_workflow/test_readiness/test_readiness_tdd.py
staged path: tests/unit/tools/release_workflow/test_runtime/__init__.py
staged path: tests/unit/tools/release_workflow/test_runtime/test_runtime_tdd.py
staged path: tests/unit/tools/release_workflow/test_support.py
staged path: tests/unit/tools/test_code_reviewer_acceptance/fixtures.py
staged path: tools/release_workflow/__init__.py
staged path: tools/release_workflow/bootstrap.py
staged path: tools/release_workflow/markers.py
staged path: tools/release_workflow/readiness.py
staged path: tools/release_workflow/runtime_identity.py
staged path: uv.lock
```

### Validation scope for step 1 release-project-root (round 6)

Validation scope: the whole suite.

### Requestor assessment for step 1 release-project-root (round 6)

No. Step 1 has NOT been fully implemented.

The human explicitly directed: "OK keep R9 unresolved, but let not it block any
review for now. Do publish round 6". R9 remains unresolved but is not a blocker
to review publication for now. This standing review guidance supersedes the
earlier publication prerequisite for this known gap. It does not claim a repair,
complete validation or authority to commit or start Step 2.

R1-R8 and R10 remain resolved. Round 5 accepted the competing-reviewer cleanup
repair and changed only attributable Step 1 validation metadata; that metadata
is accepted. No implementation repair was reversed. Production code and tests
are unchanged since the Round 5 request.

Both remaining reviewer-suggested diagnostics completed without reproducing R9:
the focused ResourceWarning probe and the exact uninstrumented collection-order
whole-suite timings pass. The latter completed 2026-10-23 at 09:18:14 +02:00,
exit 0, fail=0 warn=0 xfail=0 cov=skipped outliers=0 excluded=0 scope=whole.
Its slowest call was 0.95 seconds. Neither diagnostic establishes the failing
operation, a file holder, a root cause or a repair. The backfill lead remains
unproven. No unchanged full-day walk was repeated to seek a green result.

The post-R8 full walk passed static checks, all 3,699 affected tests and
100% tools coverage, then failed in sequential timings. No current complete
whole-suite speed proof or strict total-phase compliance is claimed. The
current request records the new diagnostic evidence and the human's explicit
review exception. The Step 1 validation notes retain the exact No assessment.

The Round 6 documentation update passed a fresh ghog check with no failures,
warnings or xfails. The exact plan source scan and CRLF-aware whitespace checks
passed. Canonical commit-plan-check reports valid, ready=true, four groups,
48 staged paths and no diagnostics. These checks do not replace full validation.

Architecture and production behavior remain unchanged. All assertions and
required real process boundaries remain. The general 1.0-second setup + call +
teardown ceiling, two named live-UV exceptions and separately tracked 48 other
breaches remain as authorized. No retry, skip, xfail or exclusion was added.

### Implementation report for step 1 release-project-root (round 6)

Step 1 produces a setup-owned two-line runtime identity, validates physical
containment, interpreter requirements and the locked release closure, and
delays engine imports until readiness succeeds. R1-R6 repairs remain intact.
The release group stays stdlib-only and is included by dev. The production
CLI remains Step 5 work; Step 1 uses a disposable engine probe and checks
missing-engine failure. No production code changed after Round 3.

Round 4 accepted R8: independent real waiters signal their first notification
wait after startup validation and initial discovery. The parent waits for
that signal before mutation. All silence, terminal-result, Git, notification
and ownership assertions remain.

The writer repaired Round 4 finding R10 in the competing-reviewer fixture.
Both start_wait calls are now inside the try/finally, each appending its
successfully started child to an initially empty list. Cleanup can therefore
collect the first indefinite waiter when the second startup raises. No
assertion or cleanup behavior was removed.

Round 5 accepted R10 and refreshed only attributable validation metadata.
Round 6 changes only the Step 1 validation notes to record the completed
diagnostics and the human's direction that unresolved R9 must not block any
review for now. Production code and tests are unchanged since Round 5.

R9 remains open. The post-R8 speed day passed check, 3,699 affected tests and
100% tools coverage, then exited 2 in sequential timings at 21:35:19 +02:00
on 2026-10-22. Both setup errors shared identity_journey[gemini]; its first
resume yielded no ownership capability. The retained early assertion reports
exit code, operation, outcome and diagnostic without ownership credentials.
It is diagnostic only. No production or fixture root cause is established.

Earlier diagnostics tested two specific ordering hypotheses. A sequential run
executed the 63 acceptance tests preceding and including the identity module.
A second run collected the entire 3,699-test suite before executing that same
63-test prefix, to include full-suite import effects. Both passed. The latter
selection uses a private diagnostic plugin only; no tracked gate, selection,
exclusion or test configuration changed. These results do not fix R9 or
replace the failed full walk. Affected, single and timings are sequential;
only ghog full uses xdist. Earlier reviewer descriptions of affected as
parallel were inaccurate and have been corrected in the validation notes.

Both additional Round 5 suggestions are now complete. The focused review-resume
ResourceWarning probe passed without any resource warning, including final GC.
The exact uninstrumented collection-order whole-suite ghog timings pass ended
2026-10-23 at 09:18:14 +02:00, exit 0, with no failures, warnings, xfails,
outliers or exclusions and coverage skipped. Its slowest call was 0.95 seconds.
The unsupported initial --whole-suite argument was corrected before this test
execution; bare timings already selects the whole suite. No cause, file holder
or repair was established. These passes do not resolve R9 or supply full-day,
coverage or total-phase proof. No further diagnostic or full walk was repeated.

Evidence:

- .reviews/a.release-project-root.step1.tmp.r6.check.log: fresh static check
  after the Round 6 validation-note update, exit 0, fail=0 warn=0 xfail=0.
  The exact plan source scan and CRLF-aware whitespace checks passed, and
  canonical commit-plan-check reports ready=true for 48 paths in four groups.
- .reviews/a.release-project-root.step1.tmp.r6.timings.log: completed exact
  uninstrumented whole-suite diagnostic, exit 0. Detailed limits are retained
  in .reviews/a.release-project-root.step1.tmp.r6.diagnostic-result.md.
- .reviews/a.release-project-root.step1.tmp.r5.resources.log and matching
  resources.json: focused ResourceWarning probe, exit 0, no resource warnings.

- .reviews/a.release-project-root.step1.tmp.r5.concurrency.log: three focused
  concurrency tests passed, exit 0, no failures, warnings or xfails.
- .reviews/a.release-project-root.step1.tmp.r5.sequence.log: 63-test sequential
  acceptance prefix passed without reproducing R9.
- .reviews/a.release-project-root.step1.tmp.r5.collection.log and matching
  collection.json: full collection, then the same 63-test prefix; exit 0.
- .reviews/a.release-project-root.step1.tmp.r5.check.log: final static checks
  after the R10 repair and validation-note changes, exit 0.
- .reviews/a.release-project-root.step1.tmp.timing/round4-first-groundhog.log:
  failed whole-suite speed day; successful affected and coverage stages do
  not make its failed sequential timings a speed proof.
- .reviews/a.release-project-root.step1.tmp.r4.identity.log, resume.log and
  identity-probe.log (each with the same a.release-project-root.step1.tmp.r4
  filename prefix): earlier focused passes and 80 diagnostic journeys.

R7 retains real offline UV generation and every shape/readiness assertion.
Accepted named exceptions, measured as setup + call + teardown in the last
successful full audit:

- tests/acceptance/release_workflow/test_uv_readiness_tdd.py::test_uv_generated_empty_shapes[no-dev-edges]: 1.8040s.
- tests/acceptance/release_workflow/test_uv_readiness_tdd.py::test_uv_generated_empty_shapes[with-dev-edges]: 1.9385s.

Attempted improvements split the original combined fixture into one fixture
per shape and tried explicit interpreter selection, reduced workers, isolated
UV settings, console suppression and executable linking. Native UV process
creation alone measured about 0.91s; useful resolution took milliseconds.
None cleared the ceiling. The human chose live integration coverage. No host
settings changed. The general 1.0-second ceiling remains, and raw reports keep
both exceptions. No stored lock, retry, skip, xfail, call-only exclusion or
raised global ceiling was introduced.

Historical pre-R8 proof completed 2026-10-22 17:50:24 +02:00: 3,699 tests,
100% tools coverage and speed proof. Its strict total-phase audit reported
50 breaches and 371.5959s summed phases: setup 302.4019s, call 67.1606s,
teardown 2.0334s. Every Step 1 process scenario was below 0.630s. The other
48 breaches remain deferred by the human. These historical measurements
predate R8 and do not prove the current tree. Evidence is retained under
.reviews/a.release-project-root.step1.tmp.timing/round3-final-*.

Writer notes: `.reviews/a.release-project-root.step1.journal.md` and
`.reviews/a.release-project-root.step1.handoff.md`.

### Change summary for step 1 release-project-root (round 6)

The staged work has four ordered a.commit groups:

1. docs(review): qualify duplicate headings
2. perf(tests): reuse CLI and repository initialization
3. feat(release): validate setup-owned runtime
4. docs(release-project-root): record step 1 validation

The latest canonical commit-plan-check verification passed: ready=true,
48 staged paths, four groups and no diagnostics. The existing wac-formatted
commit plan remains accurate and unchanged. Both staged and worktree whitespace
checks pass with CRLF-aware settings. The lock clean filter was retained.

Current staged paths:

- `bin/release_runtime_record.bat`
- `docs/v0.14.0/plan.v0.14.0.release-project-root.md`
- `docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md`
- `docs/v0.14.0/review.design-specification.v0.14.0.release-project-root.md`
- `pyproject.toml`
- `senv.bat`
- `tests/acceptance/commit_plan_check/__init__.py`
- `tests/acceptance/commit_plan_check/commit_plan_check_support.py`
- `tests/acceptance/commit_plan_check/conftest.py`
- `tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_acceptance_tdd.py`
- `tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_contracts_tdd.py`
- `tests/acceptance/release_workflow/__init__.py`
- `tests/acceptance/release_workflow/conftest.py`
- `tests/acceptance/release_workflow/process_support.py`
- `tests/acceptance/release_workflow/test_release_readiness_tdd.py`
- `tests/acceptance/release_workflow/test_uv_readiness_tdd.py`
- `tests/acceptance/review_resume/__init__.py`
- `tests/acceptance/review_resume/cli_support.py`
- `tests/acceptance/review_resume/conftest.py`
- `tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_acceptance_tdd.py`
- `tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_concurrency_tdd.py`
- `tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_identity_tdd.py`
- `tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_parked_wait_tdd.py`
- `tests/acceptance/review_resume/waiter_driver.py`
- `tests/acceptance/review_status/conftest.py`
- `tests/unit/tools/git_test_double.py`
- `tests/unit/tools/release_workflow/__init__.py`
- `tests/unit/tools/release_workflow/conftest.py`
- `tests/unit/tools/release_workflow/test_bootstrap/__init__.py`
- `tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py`
- `tests/unit/tools/release_workflow/test_markers/__init__.py`
- `tests/unit/tools/release_workflow/test_markers/test_markers_pbt.py`
- `tests/unit/tools/release_workflow/test_markers/test_markers_tdd.py`
- `tests/unit/tools/release_workflow/test_readiness/__init__.py`
- `tests/unit/tools/release_workflow/test_readiness/test_faults_tdd.py`
- `tests/unit/tools/release_workflow/test_readiness/test_metadata_tdd.py`
- `tests/unit/tools/release_workflow/test_readiness/test_readiness_pbt.py`
- `tests/unit/tools/release_workflow/test_readiness/test_readiness_tdd.py`
- `tests/unit/tools/release_workflow/test_runtime/__init__.py`
- `tests/unit/tools/release_workflow/test_runtime/test_runtime_tdd.py`
- `tests/unit/tools/release_workflow/test_support.py`
- `tests/unit/tools/test_code_reviewer_acceptance/fixtures.py`
- `tools/release_workflow/__init__.py`
- `tools/release_workflow/bootstrap.py`
- `tools/release_workflow/markers.py`
- `tools/release_workflow/readiness.py`
- `tools/release_workflow/runtime_identity.py`
- `uv.lock`

Round 6 changes only the Step 1 validation notes after accepting the Round 5
metadata patch. The notes record the ResourceWarning and whole-suite timings
diagnostics, both passing without reproducing R9, and the human's standing
instruction that R9 must not block reviews for now. R9 and the exact incomplete
assessment remain. Neither diagnostic supplies a repair or current full-speed
proof. Production code and tests are unchanged since Round 5. All earlier
repairs, including R10, remain accepted; no repair was reversed. Staged paths,
the four commit groups and their accurate subjects are unchanged in membership.

The generated code-review transcript evolves through exchange publication and
remains outside this prepared index. The human explicitly authorized Round 6
publication with R9 open and removed R9 as a review blocker for now. No commit
is authorized or performed.

### Human guidance and writer response for step 1 release-project-root (round 6)

Human guidance:

The latest human instruction is: "OK keep R9 unresolved, but let not it block
any review for now. Do publish round 6".

Publish Round 6 now with R9 explicitly unresolved. R9 must not block any review
for now; this is standing review guidance, not a one-round exception. Assess
the staged work and new diagnostic evidence independently, retain the known
gap visibly, and report any other findings normally. Do not require R9 repair
or repeat its already completed diagnostics as a condition of conducting or
publishing a review under this guidance.

R9 is not fixed, Step 1 remains incomplete, and current complete whole-suite
speed proof remains missing. The passing timings diagnostic does not replace
the failed full walk or the strict total-phase audit. The instruction does not
waive unrelated findings or authorize implementation changes, a commit or Step 2.

Keep live UV generation and all assertions; preserve the 1.0-second setup +
call + teardown ceiling and the two named UV exceptions; track the other
48 timing breaches separately; finish Step 1 before continuing. The reviewer
role remains independent.

Writer response:

The writer accepts the Round 5 answer and its attributable Step 1 validation
metadata. R1-R8 and R10 remain resolved. R10's cleanup repair and all identity,
waiter and live-UV assertions are retained. No reviewer repair was reversed;
there is no factual disagreement with the unresolved R9 finding.

Both suggested diagnostic paths have now completed. The focused review-resume
ResourceWarning run passed without unclosed-resource warnings, including final
garbage collection. The exact uninstrumented, collection-order whole-suite
ghog timings pass completed exit 0 without reproducing the identity failure.
The initial unsupported timings --whole-suite invocation stopped at argument
parsing before tests ran; the corrected bare timings command supplied the
completed diagnostic. This was not an unchanged full-day retry.

R9 remains open. Neither diagnostic established a failing operation or holder,
so no speculative test or production change was made. The early capability
diagnostic remains. A production review-exchange repair still requires evidence
and scope direction; no such repair is requested or authorized here.

The human now says: "OK keep R9 unresolved, but let not it block any review for
now. Do publish round 6". Treat R9 as unresolved and non-blocking for review
publication for now. Do not require another publication exception for this
same finding while that instruction remains in force. Continue the independent
assessment of the staged work and record other findings normally.

The Step 1 validation notes now record both diagnostic outcomes and this human
direction while retaining the exact No/incomplete assessment and R9 missing
work. Commit groups, production code and tests are unchanged. Publication does
not imply full-speed proof, total-duration compliance, commit authority or
permission to start Step 2.

### Reviewer focus for step 1 release-project-root (round 6)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-1-round-6 -->

## Round 6 by reviewer - Step 1

- Recorded: 2026-10-23T10:09:14+02:00
- Exchange: code/code/v0.14.0/release-project-root
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.release-project-root.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 1
- Outcome: answer

### Assessed index identity for step 1 release-project-root (exchange 1) (round 6)

Baseline index tree: e37db5d545177e2b413807749891128154524339

Assessed index tree: cfc368a13ddb62d09a6781231308d5e6af75691f

### Implementation check for step 1 release-project-root (exchange 1) (round 6)

Result:

Result:

No. Step 1 has NOT been fully implemented.

R9, the intermittent Gemini identity-fixture failure, is still open, so the
current tree still has no green whole-suite walk. No other gap was found. The
review follows the human's standing guidance: it was run in full, R9 stays
visible, and no further R9 diagnostic is required. That guidance does not turn
R9 into a pass, and the request does not claim that it does.

Changes checked against the round 5 assessed tree `4adfdae9…`. The request-time
tree `e37db5d5…` differs only in the Step 1 rows of the validation plan
(17 lines added, 1 changed). Production code is unchanged since round 3 and
tests since round 5. This reviewer session also re-read the four production
modules, the setup batch entry and the `senv.bat`, `pyproject.toml` and
`uv.lock` changes against the plan's Step 1 contract, and found no defect.

- New validation notes: accurate. They record the human's 2026-10-23
  direction and both diagnostics, claim no cause, repair or speed proof, and
  keep the exact No sentence and the R9 missing-work bullet.
- Timings diagnostic: accepted. In `tools/groundhog/runner.py`, `ghog timings`
  runs the whole suite in one sequential pytest process without coverage,
  testmon or xdist, which is the failing stage's exact shape. It exited 0 with
  no failure or outlier; the slowest call was 0.95s.
- ResourceWarning probe: accepted. Its JSON reports no resource warning across
  38 tests and the final collection. The single warning in its log is raised
  by groundhog's own parent runner (an unclosed `Popen` stdout), outside the
  test process, and has no bearing on R9.
- R9 lead, sharpened by code reading and still unproven. The identity fixture
  rewrites the request and coordination record (`legacy_natures`) just before
  the first `resume`. That resume's `claim` then replaces the same two files
  through `RoleNatureBackfill._replace_all`, which has no bounded
  `PermissionError` retry. Group 2 moved these calls in-process
  (`run_inline`): several CLI process startups used to separate the rewrite
  from the replace, and now milliseconds do. A transient holder of a
  just-written file, such as a scanner or indexer, now overlaps the replace
  far more easily. That fits every fact so far: R9 appeared only after the
  in-process change, it hit one provider once, it does not reproduce on
  demand, and no in-process leak was found. The retained assertion will name
  the failing operation if it recurs.

R1 to R8 and R10 stay resolved; their files are unchanged since round 5.

Architecture: no smell or layer violation. Only plain data crosses the
readiness gate, and the grammar and graph code stays apart from the
filesystem and metadata boundaries.

Performance: production processing stays linear. The test-side position is
unchanged: two named UV exceptions, with the other 48 breaches tracked
separately.

Static coverage: no `tools` module changed since round 3, and the post-R8
`ghog full` stage reported 100%.

Feature integrity: no assertion, real process boundary or marker was removed,
and no skip, xfail, retry or exclusion was added. The open gap is R9.

Validation plan effects:

The reviewer added one paragraph to the Step 1 *What was implemented* row of
`docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md`, after the
writer's diagnostic paragraph. It records the reviewer's round 6
`ghog affected --no-cov` and `ghog check` results and the acceptance of both
diagnostics. It also notes that the clean ResourceWarning probe weakens the
in-process leak branch of the R9 lead, without excluding a claim-time or
external holder.

The analysis keeps the exact No sentence, *Missing work for Step 1* keeps the
R9 bullet, and the document-level line stays `No, it is not implemented`.
Other steps, the plan, the umbrella, implementation, tests and `a.commit` were
not edited.

The evidence launcher attributed the 8-line patch against the pre-edit blob
`e6bb06e9e3c79bc184a69cdfee1e1aae8399d6a1` (attributable, not created). Only
that patch was staged. The project Markdown check, inside the reviewer's
`ghog check`, and the CRLF-aware `git diff --cached --check` pass. This is
review metadata, not a substantive repair.

### Pre-repair mandatory checks and coverage for step 1 release-project-root (exchange 1) (round 6)

Requestor evidence, as reported and not repeated: no green
`ghog day --full=speed --whole-suite` exists for the current tree. The post-R8
walk passed `ghog check`, `ghog affected` over 3,699 tests and `ghog full` at
`cov=100`, then its timings stage exited 2 on `identity_journey[gemini]` (R9).
Since round 5, the writer ran two diagnostics, both exit 0 without reproducing
R9: the focused review-resume ResourceWarning probe (38 tests) and the
whole-suite `ghog timings` pass, completed 2026-10-23 at 09:18:14 +02:00. The
writer's fresh `ghog check` after the round 6 note update also passed. The
last complete walk, at 2026-10-22 17:50:24 +02:00, predates R8.

Reviewer evidence, each command run once from the project root through the
shared `ghog.bat` launcher, with the log-freshness proof and
`SWITCHPY_CHOICE=local` set for that process only:

- `ghog affected --no-cov --scope-file=.reviews/a.review-scope.code.v0.14.0.release-project-root.json`:
  exit 0, scope whole, `fail=0 warn=0 xfail=0`. Testmon selected no test,
  since no Python file changed after round 5. This is not whole-suite evidence.
- `ghog check`, run after the reviewer's validation-row edit: exit 0. All
  static, EOF and Markdown checks passed.

The reviewer did not run `ghog day`, `ghog full`, the strict audit or any
coverage measurement. Coverage was assessed statically.

### Resolved validation set and sources for step 1 release-project-root (exchange 1) (round 6)

The request and the current resolver produce the same ordered set as in
round 5:

1. `ghog day --full=speed --whole-suite`: source project.
2. `rg -n 'VIRTUAL_ENV|PYTHONPATH|glob|rglob|import_module' tools/release_workflow`:
   source plan.
3. `ghog check`: source request.

No `.review-validation` file exists. Re-running `resolve_code_review_validation`
from the current `tools/code_review_validation.py` this round reproduced this
exact set. The reviewer did not run the resolved set; its own `ghog check` run
is reviewer evidence. The requestor reports no green run of the first command
on the current tree (R9).

### Resolver drift and direction for step 1 release-project-root (exchange 1) (round 6)

None: ordered commands and source labels agree with the current resolver.

### Repository state around validation for step 1 release-project-root (exchange 1) (round 6)

Request-time and reviewer baseline index tree:
`e37db5d545177e2b413807749891128154524339` (identical). Final assessed index
tree after the reviewer metadata patch: `cfc368a13ddb62d09a6781231308d5e6af75691f`.

The same ordered 50-path validation set was captured before and after
assessment: the 48 staged paths plus the ignored `a.ghog.log` and
`a.ghog.status`. The only tracked difference is
`docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md`, the intended
Step 1 row edit. The only ignored difference is `a.ghog.status`: the final
`a.ghog.log` matches the writer's earlier `ghog check` log byte for byte.
There are no untracked differences. The raw `acceptable=false` reflects the
intentional metadata edit; the reviewer's ghog runs left no tracked side
effect. There is no overlap with writer work, and the only other working-tree
entry is the untracked exchange transcript, which the protocol owns.

Umbrella `docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md`: applicable,
digest `ca6fe473…0ec992` before and after, unchanged. No umbrella row was
modified.

Retained evidence: `.reviews/a.code-review-evidence.v0.14.0.release-project-root.step-1.json`,
with the inputs under `.reviews/a.release-project-root.step1.tmp.r6.review-*`.

### Repair inventory for step 1 release-project-root (exchange 1) (round 6)

Repairs made:

- Review metadata only: added the reviewer's round 6 evidence paragraph to the
  Step 1 *What was implemented* row. Classification: polishing-only review
  metadata, not substantive. No implementation, test, plan or `a.commit`
  repair.

Paths staged:

- docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md (reviewer metadata patch only)

### Commit plan assessment for step 1 release-project-root (exchange 1) (round 6)

Ran `commit-plan-check.bat --format json` independently before assessment and
again after staging the Step 1 metadata. Both returned exit 0, `state=valid`,
`ready=true`, four ordered groups, 48 staged paths and no diagnostics. The JSON
is retained in `.reviews/a.release-project-root.step1.tmp.r6.review-commit-plan.json`
and `.reviews/a.release-project-root.step1.tmp.r6.review-commit-plan-after.json`.

Ordered groups:

1. `docs(review): qualify duplicate headings` (1 path)
2. `perf(tests): reuse CLI and repository initialization` (16 paths)
3. `feat(release): validate setup-owned runtime` (30 paths)
4. `docs(release-project-root): record step 1 validation` (1 path)

`a.commit` remains accurate: membership, order, conventional subjects and
bodies match the staged work, and group 4 still records the unresolved
timing-run failure. The reviewer did not amend it. When R9 is resolved, the
body of the group that receives the fix should name it. Mechanical readiness
does not resolve R9 and does not authorize a commit.

### Findings and boundaries for step 1 release-project-root (exchange 1) (round 6)

Unresolved findings:

- R9 (P2): the Gemini identity fixture failed once in the post-R8
  `ghog day --full=speed --whole-suite` timings stage, so the requestor's
  resolved validation set has no green run on the current tree. Both
  diagnostics requested in round 5 passed without reproducing it, and the
  human directed that R9 stay open without blocking reviews. Leading, unproven
  explanation: group 2's in-process `run_inline` calls shrank the gap between
  the fixture's `legacy_natures` rewrite of the request and coordination
  record and the first claim's atomic replace of the same files in
  `RoleNatureBackfill._replace_all` (`tools/review_role_nature.py`). That
  replace has no bounded `PermissionError` retry, unlike the exchange store,
  the ownership store and the migration journal. A transient external holder
  of a just-written file would then fail the claim without a capability. No
  test-side handle leak was found. Do not add a test-level retry, sleep, skip,
  xfail or exclusion.

Boundary-crossing work:

- The likely R9 repair is outside Step 1: give
  `RoleNatureBackfill._replace_all` (`tools/review_role_nature.py`) the same
  bounded `PermissionError` retry as `_commit_prepared` in
  `tools/review_exchange_store.py` and
  `tools/review_exchange_ownership_store.py`, with its own unit test. It
  changes review-exchange production code, so the human decides its scope.

### Human guidance response for step 1 release-project-root (exchange 1) (round 6)

Human guidance:

The latest human instruction is: "OK keep R9 unresolved, but let not it block
any review for now. Do publish round 6".

Publish Round 6 now with R9 explicitly unresolved. R9 must not block any review
for now; this is standing review guidance, not a one-round exception. Assess
the staged work and new diagnostic evidence independently, retain the known
gap visibly, and report any other findings normally. Do not require R9 repair
or repeat its already completed diagnostics as a condition of conducting or
publishing a review under this guidance.

R9 is not fixed, Step 1 remains incomplete, and current complete whole-suite
speed proof remains missing. The passing timings diagnostic does not replace
the failed full walk or the strict total-phase audit. The instruction does not
waive unrelated findings or authorize implementation changes, a commit or Step 2.

Keep live UV generation and all assertions; preserve the 1.0-second setup +
call + teardown ceiling and the two named UV exceptions; track the other
48 timing breaches separately; finish Step 1 before continuing. The reviewer
role remains independent.

Guidance response:

The guidance asks for an independent assessment and instructs no reviewer
repair, so the reviewer changed no implementation or test file. The request's
general "make every safe repair" wording does not override that rule. The only
reviewer change is the Step 1 validation-row addition.

How each point was applied:

- R9 did not block this review. The round was assessed and published in
  full, R9 stays visible as the only open finding, and no R9 repair or repeat
  of the completed diagnostics is required. The optional diagnostic in the
  writer instructions is new and is not a condition.
- The new diagnostic evidence was assessed independently and accepted, with
  its limits stated.
- Other findings were reported normally: there are none.
- The standing guidance governs whether R9 blocks a review. It does not change
  the disposition rules, which require a complete implementation, a green
  resolved validation set and no unresolved finding before commit-ready. The
  guidance itself states that R9 is not fixed and Step 1 is incomplete, so the
  advisory disposition stays changes-requested.
- Live UV generation, every assertion, the 1.0-second ceiling, the two named
  UV exceptions and the separate tracking of the other 48 breaches are
  unchanged. No commit or Step 2 is implied, and the reviewer stayed
  independent.

Scope: the staged work stays within Step 1, and nothing from Step 2 was found.
This answer authorizes no commit.

### Writer instructions for step 1 release-project-root (exchange 1) (round 6)

No writer change is needed this round beyond R9. Accept the reviewer's
attributable Step 1 row addition.

Inside Step 1, no R9 action is left without new evidence or a scope decision,
and another unchanged round would add nothing. Bring R9 to the human with
these choices instead:

- Authorize the boundary repair: a bounded `PermissionError` retry in
  `RoleNatureBackfill._replace_all`, matching `_commit_prepared`, with a unit
  test that injects one transient `PermissionError` and asserts the backfill
  still succeeds. The human decides whether it belongs to this effort or to a
  separate one.
- Optionally, before that, run a new and cheap private diagnostic, not a
  repeat of the completed ones: in a scratch folder under `.reviews`, rewrite
  a file and immediately pass it to `_replace_all`, a few thousand times,
  counting each `PermissionError`. A nonzero count shows that this host
  produces transient sharing violations on that path; zero proves nothing.
- Keep R9 open, as now, with Step 1 incomplete.

Do not move the identity journey's claim back to a separate process, add a
sleep, or add a test-level retry, skip, xfail or exclusion to make R9 vanish:
each would hide the gap. Keep every identity assertion and the diagnostic.

Once R9 is resolved, run the requestor-owned resolved set green:
`ghog day --full=speed --whole-suite`, the plan's `rg` scan and `ghog check`.
Re-run the strict total-duration audit and confirm that the only Step 1
breaches are the two named UV exceptions. Then open the Step 1 rows with
`Yes. Step 1 has been fully implemented.`, remove *Missing work for Step 1*,
name the fix in the matching `a.commit` group body, and publish the
replacement request.

### Decision rationale for step 1 release-project-root (exchange 1) (round 6)

Recommend changes-requested. The six readiness-floor results are:

1. Identity: PASS. The exact plan, step 1, round 6, occurrence 1, code
   identity, umbrella and request-time index tree agree with the live
   exchange.
2. Implementation completeness: FAIL. R9 remains, as the writer's own exact
   No assessment states.
3. Validation and coverage: FAIL. No green
   `ghog day --full=speed --whole-suite` exists for the current tree. The
   reviewer's `ghog check` and `ghog affected --no-cov` are green, and the
   static coverage walk finds no gap.
4. Staged attribution: PASS. The only reviewer change is the attributable
   Step 1 validation-row addition. There is no substantive repair and no
   unrelated staged work.
5. Unresolved findings: FAIL. R9 (P2) remains. R1 to R8 and R10 are
   resolved, R7 by the human's named exceptions.
6. `a.commit`: PASS. The independent checker reports exit 0, valid and
   ready, with all 48 paths in four accurate groups.

The human's guidance is applied as written: R9 did not block this review, its
publication or the assessment of everything else, and nothing else blocks
Step 1. The guidance cannot satisfy the completeness and validation results,
and the request claims neither. The diagnostics were careful and honestly
reported. What remains is a human decision on R9's scope, not more writer
work inside Step 1.

### Final reviewer decision for step 1 release-project-root (exchange 1) (round 6)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-1-round-6 -->

## Round 7 by requestor - Step 1

- Recorded: 2026-10-23T13:57:42+02:00
- Exchange: code/code/v0.14.0/release-project-root
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.release-project-root.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 1
- Outcome: request

### Review identity for step 1 release-project-root (round 7)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.release-project-root.md
Implementation step: 1
Review round: 7

### Code review evidence for step 1 release-project-root (round 7)

request_index_tree: d9f84487329e92b82d6daf3790546941fd3b15b8
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)
- `rg -n 'VIRTUAL_ENV|PYTHONPATH|glob|rglob|import_module' tools/release_workflow` (sources: plan)
- `ghog check` (sources: request)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.release-project-root.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: docs(review): qualify duplicate headings
group 1 path: docs/v0.14.0/review.design-specification.v0.14.0.release-project-root.md
group 2: fix(review): retry transient role-nature replace
group 2 path: tools/review_role_nature.py
group 2 path: tests/unit/tools/test_review_role_nature/test_review_role_nature_tdd.py
group 3: perf(tests): reuse CLI and repository initialization
group 3 path: tests/acceptance/commit_plan_check/__init__.py
group 3 path: tests/acceptance/commit_plan_check/commit_plan_check_support.py
group 3 path: tests/acceptance/commit_plan_check/conftest.py
group 3 path: tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_acceptance_tdd.py
group 3 path: tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_contracts_tdd.py
group 3 path: tests/acceptance/review_resume/__init__.py
group 3 path: tests/acceptance/review_resume/cli_support.py
group 3 path: tests/acceptance/review_resume/conftest.py
group 3 path: tests/acceptance/review_resume/waiter_driver.py
group 3 path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_acceptance_tdd.py
group 3 path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_concurrency_tdd.py
group 3 path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_identity_tdd.py
group 3 path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_parked_wait_tdd.py
group 3 path: tests/acceptance/review_status/conftest.py
group 3 path: tests/unit/tools/git_test_double.py
group 3 path: tests/unit/tools/test_code_reviewer_acceptance/fixtures.py
group 4: feat(release): validate setup-owned runtime
group 4 path: bin/release_runtime_record.bat
group 4 path: docs/v0.14.0/plan.v0.14.0.release-project-root.md
group 4 path: pyproject.toml
group 4 path: senv.bat
group 4 path: tests/acceptance/release_workflow/__init__.py
group 4 path: tests/acceptance/release_workflow/conftest.py
group 4 path: tests/acceptance/release_workflow/process_support.py
group 4 path: tests/acceptance/release_workflow/test_release_readiness_tdd.py
group 4 path: tests/acceptance/release_workflow/test_uv_readiness_tdd.py
group 4 path: tests/unit/tools/release_workflow/__init__.py
group 4 path: tests/unit/tools/release_workflow/conftest.py
group 4 path: tests/unit/tools/release_workflow/test_bootstrap/__init__.py
group 4 path: tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py
group 4 path: tests/unit/tools/release_workflow/test_markers/__init__.py
group 4 path: tests/unit/tools/release_workflow/test_markers/test_markers_pbt.py
group 4 path: tests/unit/tools/release_workflow/test_markers/test_markers_tdd.py
group 4 path: tests/unit/tools/release_workflow/test_readiness/__init__.py
group 4 path: tests/unit/tools/release_workflow/test_readiness/test_faults_tdd.py
group 4 path: tests/unit/tools/release_workflow/test_readiness/test_metadata_tdd.py
group 4 path: tests/unit/tools/release_workflow/test_readiness/test_readiness_pbt.py
group 4 path: tests/unit/tools/release_workflow/test_readiness/test_readiness_tdd.py
group 4 path: tests/unit/tools/release_workflow/test_runtime/__init__.py
group 4 path: tests/unit/tools/release_workflow/test_runtime/test_runtime_tdd.py
group 4 path: tests/unit/tools/release_workflow/test_support.py
group 4 path: tools/release_workflow/__init__.py
group 4 path: tools/release_workflow/bootstrap.py
group 4 path: tools/release_workflow/markers.py
group 4 path: tools/release_workflow/readiness.py
group 4 path: tools/release_workflow/runtime_identity.py
group 4 path: uv.lock
group 5: docs(release-project-root): record step 1 validation
group 5 path: docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md
staged path: bin/release_runtime_record.bat
staged path: docs/v0.14.0/plan.v0.14.0.release-project-root.md
staged path: docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md
staged path: docs/v0.14.0/review.design-specification.v0.14.0.release-project-root.md
staged path: pyproject.toml
staged path: senv.bat
staged path: tests/acceptance/commit_plan_check/__init__.py
staged path: tests/acceptance/commit_plan_check/commit_plan_check_support.py
staged path: tests/acceptance/commit_plan_check/conftest.py
staged path: tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_acceptance_tdd.py
staged path: tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_contracts_tdd.py
staged path: tests/acceptance/release_workflow/__init__.py
staged path: tests/acceptance/release_workflow/conftest.py
staged path: tests/acceptance/release_workflow/process_support.py
staged path: tests/acceptance/release_workflow/test_release_readiness_tdd.py
staged path: tests/acceptance/release_workflow/test_uv_readiness_tdd.py
staged path: tests/acceptance/review_resume/__init__.py
staged path: tests/acceptance/review_resume/cli_support.py
staged path: tests/acceptance/review_resume/conftest.py
staged path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_acceptance_tdd.py
staged path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_concurrency_tdd.py
staged path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_identity_tdd.py
staged path: tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_parked_wait_tdd.py
staged path: tests/acceptance/review_resume/waiter_driver.py
staged path: tests/acceptance/review_status/conftest.py
staged path: tests/unit/tools/git_test_double.py
staged path: tests/unit/tools/release_workflow/__init__.py
staged path: tests/unit/tools/release_workflow/conftest.py
staged path: tests/unit/tools/release_workflow/test_bootstrap/__init__.py
staged path: tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py
staged path: tests/unit/tools/release_workflow/test_markers/__init__.py
staged path: tests/unit/tools/release_workflow/test_markers/test_markers_pbt.py
staged path: tests/unit/tools/release_workflow/test_markers/test_markers_tdd.py
staged path: tests/unit/tools/release_workflow/test_readiness/__init__.py
staged path: tests/unit/tools/release_workflow/test_readiness/test_faults_tdd.py
staged path: tests/unit/tools/release_workflow/test_readiness/test_metadata_tdd.py
staged path: tests/unit/tools/release_workflow/test_readiness/test_readiness_pbt.py
staged path: tests/unit/tools/release_workflow/test_readiness/test_readiness_tdd.py
staged path: tests/unit/tools/release_workflow/test_runtime/__init__.py
staged path: tests/unit/tools/release_workflow/test_runtime/test_runtime_tdd.py
staged path: tests/unit/tools/release_workflow/test_support.py
staged path: tests/unit/tools/test_code_reviewer_acceptance/fixtures.py
staged path: tests/unit/tools/test_review_role_nature/test_review_role_nature_tdd.py
staged path: tools/release_workflow/__init__.py
staged path: tools/release_workflow/bootstrap.py
staged path: tools/release_workflow/markers.py
staged path: tools/release_workflow/readiness.py
staged path: tools/release_workflow/runtime_identity.py
staged path: tools/review_role_nature.py
staged path: uv.lock
```

### Validation scope for step 1 release-project-root (round 7)

Validation scope: the whole suite.

### Requestor assessment for step 1 release-project-root (round 7)

Yes. Step 1 has been fully implemented.

The human-authorized R9 boundary repair is implemented and validated. The
before-fix probe reproduced 86/119 wrapped PermissionErrors (WinError 5) in
TEMP/.reviews, and the unchanged after-fix probe completed 5,000 iterations
per folder without escaped or other errors while recording 87/115 retry
sleeps. This demonstrates that bounded production retries absorb the observed
transient failures; the historical R9 exception and file holder remain unknown.

The fresh whole-suite ghog day --full=speed --whole-suite passed with 3,702
tests, 100% tools coverage, proof=speed/reused=none, and no failures, warnings,
xfails, call outliers or exclusions. All identity assertions, including Gemini
in the sequential collection order, pass. The three new role-nature tests
exercise recovery, exhaustion/rollback and immediate plain OSError failure.
The existing rollback test is unchanged. Final ghog check and the exact plan
source scan pass; staged whitespace and the five-group/50-path commit plan
are clean.

Strict setup + call + teardown measurement retains the one-second ceiling
and every result. Its 45 global breaches yield raw verdict 8; only the two
named live-UV exceptions belong to Step 1 (1.1758s/1.1285s). The other 43
belong to deferred topics, including a newly inventoried 1.0092s launcher
smoke case. Release process scenarios peak at 0.6166s and role-nature tests
at 0.0622s. Step 1 meets the human's timing conditions; universal one-second
compliance is not claimed.

Architecture remains within the documented boundaries. The new static helper
matches the existing atomic writer pattern, catches only PermissionError and
preserves preparation, rollback, error wrapping and cleanup. No broader retry
refactor, test-level retry, sleep, process fallback, skip, xfail or exclusion
was introduced. Existing feature behavior passes the complete suite. No new
types or architecture concerns are introduced by this repair.

Round 6 metadata is accepted without disagreement. The validation document
now opens Step 1 with Yes and removes Missing work for Step 1. The document's
overall No remains correct for pending Steps 2-6. The retry is a separately
ordered commit group before in-process orchestration, with the Step 1 plan
file list unchanged. No commit or Step 2 is authorized.

### Implementation report for step 1 release-project-root (round 7)

Step 1 produces the measured setup-owned runtime identity, checks physical
containment, interpreter requirements and locked release dependencies, and
delays engine imports until readiness succeeds. R1-R8 and R10 remain addressed.
The release group remains stdlib-only. The production CLI stays assigned to
Step 5; Step 1 uses a disposable engine probe and checks missing-engine failure.

Round 7 implements the human-authorized R9 boundary repair after running the
reviewer's diagnostic. RoleNatureBackfill now uses a static _commit_prepared
helper with five attempts, catching only PermissionError. Its four possible
delays are 0.01, 0.02, 0.04 and 0.08 seconds. Exhaustion re-raises into the
existing rollback and ReviewExchangeError wrapper. Preparation, rollback and
temporary-file cleanup are unchanged; the other three retry copies are intact.

Three unit tests cover a transient failure followed by both replacements,
persistent failure on the second target with byte-for-byte restoration of the
first, and immediate failure without delay for a plain OSError. Each checks
temporary-file cleanup. Sleep is a delay recorder in these tests. The original
test_commit_failure_rolls_back_every_exposed_replacement is unchanged.
Focused ghog single passed with fail=0 warn=0 xfail=0; evidence:
.reviews/a.release-project-root.step1.tmp.r7.retry.log.

The unchanged private diagnostic runs 5,000 iterations per folder, rewriting
request.md and coordination.md immediately before _replace_all. It counts
wrapped PermissionError by winerror, other errors and real retry sleeps. Its
two script-created scratch folders are checked for containment and removed
after each run. Results:

| Run | Folder | Iterations | Escaped PermissionError | WinError | Other errors | Retry sleeps | Seconds |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: |
| Before | TEMP | 5000 | 86 | 5 | 0 | 0 | 215.4413 |
| Before | .reviews | 5000 | 119 | 5 | 0 | 0 | 231.6360 |
| After | TEMP | 5000 | 0 | none | 0 | 87 | 198.1740 |
| After | .reviews | 5000 | 0 | none | 0 | 115 | 188.3987 |

Evidence: .reviews/a.release-project-root.step1.tmp.r7.diag-before.log and
.reviews/a.release-project-root.step1.tmp.r7.diag-after.log. The probe source
is .reviews/a.release-project-root.step1.tmp.r7.diag.py and was unchanged
between runs. Nonzero after-fix sleeps prove real transient permission errors
were absorbed. The historical R9 exception and file holder remain unobserved;
the connection to that exact failure remains a hypothesis.

The identity journey stays in process with all assertions and its early
operation/outcome diagnostic. No test-level retry, sleep, process fallback,
skip, xfail or exclusion was added. The five-group a.commit puts the retry
before the in-process test initialization changes. The production boundary
file and its test are authorized additions to the commit inventory, with the
implementation plan's Step 1 file list unchanged.

The full `ghog day --full=speed --whole-suite` completed 2026-10-23 at
13:49:45 +02:00, exit 0, proof=speed/reused=none. All 3,702 sequential tests
passed, including the Gemini identity journey in collection order. The full
stage reports tools coverage at 100%, including retry exhaustion; there are
no failures, warnings, xfails, call outliers or exclusions. Evidence:
.reviews/a.release-project-root.step1.tmp.r7.timing/groundhog.log.

The exact plan source scan
`rg -n 'VIRTUAL_ENV|PYTHONPATH|glob|rglob|import_module' tools/release_workflow`
passed. Its only matches are the intended post-gate import_module call and a
comment about global setup. The final standalone ghog check passed, exit 0,
fail=0 warn=0 xfail=0; evidence:
.reviews/a.release-project-root.step1.tmp.r7.check.log.
After recording the final completion assessment, the same speed-day command
confirmed the saved proof on unchanged sources with reused=all; no tests or
check ran in that invocation. Its evidence is
.reviews/a.release-project-root.step1.tmp.r7.final-day.log. The standalone
ghog check was then rerun for the final documentation state.
CRLF-aware staged whitespace and canonical commit-plan-check pass; the latter
reports ready=true for all 50 paths in five groups without diagnostics.

The strict audit measures all 3,702 tests at 319.3208 seconds summed phases:
270.8953 setup, 47.3753 call, 1.0502 teardown. It retains 45 breaches and raw
global exit 8, while groundhog itself exits 0. The audit wrapper surfaces that
raw verdict (PowerShell transport exit 1); this is not a failed test walk.
Only the two accepted live-UV cases breach Step 1's ceiling:

- tests/acceptance/release_workflow/test_uv_readiness_tdd.py::test_uv_generated_empty_shapes[no-dev-edges]: 1.1758s.
- tests/acceptance/release_workflow/test_uv_readiness_tdd.py::test_uv_generated_empty_shapes[with-dev-edges]: 1.1285s.

Release process scenarios peak at 0.6166s; role-nature unit tests peak at
0.0622s. The Gemini identity fixture passes at 0.9982s. The other 43 breaches
belong to deferred topics: six formerly slow tests are now under the ceiling,
and one new non-Step-1 breach is explicitly retained:
tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_launcher_smoke_tdd.py::test_each_code_review_launcher_reaches_its_public_entry_point[code_review_answer.bat]
at 1.0092s, including 1.0083s setup. Evidence is retained in
.reviews/a.release-project-root.step1.tmp.r7.timing/durations.json and its
above-one-second.md inventory.

The general strict ceiling remains 1.0 second for setup + call + teardown.
The human's named live-UV exceptions retain both offline UV generations and
every shape/readiness assertion. Other topics' previously inventoried costs
remain deferred. Raw inventory is retained without exclusions or a raised
ceiling; a green groundhog call-only gate alone does not prove total-duration
compliance. The prior accepted UV totals were 1.8040s and 1.9385s. Attempted
improvements split the fixtures and tried interpreter selection, reduced
workers, isolated settings, console suppression and executable linking.
Windows UV process creation dominated; the human chose retained live
integration coverage. Current Step 1 timing conditions are met, while global
total-duration compliance is not claimed.

Writer notes: `.reviews/a.release-project-root.step1.journal.md` and
`.reviews/a.release-project-root.step1.handoff.md`.

### Change summary for step 1 release-project-root (round 7)

The staged inventory contains 50 paths in five ordered a.commit groups.
Round 7 adds only the authorized role-nature boundary implementation and its
test file, and updates the Step 1 validation evidence. The retry group lands
before the in-process orchestration group. The review transcript is excluded
from this writer-owned inventory; private evidence and a.commit are not staged.

#### Group 1: docs(review): qualify duplicate headings for step 1 release-project-root (round 7)

- `docs/v0.14.0/review.design-specification.v0.14.0.release-project-root.md`

#### Group 2: fix(review): retry transient role-nature replace for step 1 release-project-root (round 7)

- `tools/review_role_nature.py`
- `tests/unit/tools/test_review_role_nature/test_review_role_nature_tdd.py`

#### Group 3: perf(tests): reuse CLI and repository initialization for step 1 release-project-root (round 7)

- `tests/acceptance/commit_plan_check/__init__.py`
- `tests/acceptance/commit_plan_check/commit_plan_check_support.py`
- `tests/acceptance/commit_plan_check/conftest.py`
- `tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_acceptance_tdd.py`
- `tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_contracts_tdd.py`
- `tests/acceptance/review_resume/__init__.py`
- `tests/acceptance/review_resume/cli_support.py`
- `tests/acceptance/review_resume/conftest.py`
- `tests/acceptance/review_resume/waiter_driver.py`
- `tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_acceptance_tdd.py`
- `tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_concurrency_tdd.py`
- `tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_identity_tdd.py`
- `tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_parked_wait_tdd.py`
- `tests/acceptance/review_status/conftest.py`
- `tests/unit/tools/git_test_double.py`
- `tests/unit/tools/test_code_reviewer_acceptance/fixtures.py`

#### Group 4: feat(release): validate setup-owned runtime for step 1 release-project-root (round 7)

- `bin/release_runtime_record.bat`
- `docs/v0.14.0/plan.v0.14.0.release-project-root.md`
- `pyproject.toml`
- `senv.bat`
- `tests/acceptance/release_workflow/__init__.py`
- `tests/acceptance/release_workflow/conftest.py`
- `tests/acceptance/release_workflow/process_support.py`
- `tests/acceptance/release_workflow/test_release_readiness_tdd.py`
- `tests/acceptance/release_workflow/test_uv_readiness_tdd.py`
- `tests/unit/tools/release_workflow/__init__.py`
- `tests/unit/tools/release_workflow/conftest.py`
- `tests/unit/tools/release_workflow/test_bootstrap/__init__.py`
- `tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py`
- `tests/unit/tools/release_workflow/test_markers/__init__.py`
- `tests/unit/tools/release_workflow/test_markers/test_markers_pbt.py`
- `tests/unit/tools/release_workflow/test_markers/test_markers_tdd.py`
- `tests/unit/tools/release_workflow/test_readiness/__init__.py`
- `tests/unit/tools/release_workflow/test_readiness/test_faults_tdd.py`
- `tests/unit/tools/release_workflow/test_readiness/test_metadata_tdd.py`
- `tests/unit/tools/release_workflow/test_readiness/test_readiness_pbt.py`
- `tests/unit/tools/release_workflow/test_readiness/test_readiness_tdd.py`
- `tests/unit/tools/release_workflow/test_runtime/__init__.py`
- `tests/unit/tools/release_workflow/test_runtime/test_runtime_tdd.py`
- `tests/unit/tools/release_workflow/test_support.py`
- `tools/release_workflow/__init__.py`
- `tools/release_workflow/bootstrap.py`
- `tools/release_workflow/markers.py`
- `tools/release_workflow/readiness.py`
- `tools/release_workflow/runtime_identity.py`
- `uv.lock`

#### Group 5: docs(release-project-root): record step 1 validation for step 1 release-project-root (round 7)

- `docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md`

### Human guidance and writer response for step 1 release-project-root (round 7)

Human guidance:

I authorize the R9 boundary repair: a bounded PermissionError retry in
RoleNatureBackfill._replace_all (tools/review_role_nature.py), as part of this
effort and of the Step 1 commit plan. Run the reviewer's cheap diagnostic
first and report its count whatever it is, then apply the repair. Do not hide
R9 with a test-level retry, a sleep, a separate process, a skip, an xfail or
an exclusion.

Writer response:

The Round 6 answer and its eight-line validation metadata addition are accepted
without disagreement or reversal. R1-R8 and R10 remain addressed. The human
explicitly authorized the proposed diagnostic followed by the bounded R9
boundary repair, so this round includes substantive code, tests and commit-plan
changes.

The before-fix probe reproduced wrapped PermissionError in the role-nature
replacement boundary: 86 failures in TEMP and 119 under .reviews across 5,000
iterations in each folder, all WinError 5, with zero other errors. This proves
the local immediate-write/backfill sequence can fail at that boundary. It does
not prove who held the file or which exception caused the historical Gemini
identity setup failure, whose original diagnostic was hidden by the missing
ownership capability. The scanner/temporary-handle explanation for that exact
failure remains a hypothesis.

The implementation copies the existing five-attempt PermissionError pattern
without changing preparation, rollback or cleanup. Three tests record delays
without sleeping and prove recovery, persistent-error rollback and immediate
failure for plain OSError. The original rollback test is unchanged. Identity
journeys remain in process with their diagnostic and every assertion; no
test-level retry, sleep, subprocess fallback, skip, xfail or exclusion was added.

The implementation report records both complete diagnostic runs and every
validation result. Nonzero after-fix sleep counts demonstrate real permission
failures absorbed by the production retry; they are not a count of affected
iterations or proof of the historical R9 holder. The commit plan places this
boundary repair before the in-process orchestration changes. No commit or
Step 2 is authorized.

### Reviewer focus for step 1 release-project-root (round 7)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-1-round-7 -->

## Round 7 by reviewer - Step 1

- Recorded: 2026-10-23T14:19:28+02:00
- Exchange: code/code/v0.14.0/release-project-root
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.release-project-root.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 1
- Outcome: answer

### Assessed index identity for step 1 release-project-root (exchange 1) (round 7)

Baseline index tree: d9f84487329e92b82d6daf3790546941fd3b15b8

Assessed index tree: be3273f8049e7dacea7eaa24ddd5e4650cb829d4

### Implementation check for step 1 release-project-root (exchange 1) (round 7)

Result:

Result:

Yes. Step 1 has been fully implemented.

R9 is resolved by the human-authorized boundary repair, and the requestor's
resolved validation set is green on the current tree. No other gap was found.

Changes checked against the round 6 assessed tree `cfc368a1…`. The
request-time tree `d9f84487…` differs in three paths only:
`tools/review_role_nature.py` (22 lines),
`tests/unit/tools/test_review_role_nature/test_review_role_nature_tdd.py`
(95 lines added) and the Step 1 rows of the validation plan. Every other
staged path is byte-identical to round 6, so the identity journey, its
fixtures and its diagnostic are unchanged.

- Retry: correct and narrow. The new static `_commit_prepared` is a line-for-line
  copy of `_commit_prepared` in `tools/review_exchange_store.py:553`: five
  attempts, delays of 0.01, 0.02, 0.04 and 0.08 seconds, and only
  `PermissionError` is caught. After the last attempt the error is raised
  again into the unchanged `except (OSError, UnicodeError)` block, which rolls
  back the already exposed files and wraps it as
  `atomic role-nature backfill failed`. Preparation and temporary-file cleanup
  are untouched. The three other retry copies are unchanged.
- Tests: the three new unit tests check what they claim, with `time.sleep`
  replaced by a delay recorder. A single `PermissionError` is absorbed with
  one 0.01 delay. A permanent one on the second file exhausts after four
  delays, keeps the `PermissionError` as cause and restores the first file
  byte for byte, CRLF included. A plain `OSError` fails on the first attempt
  with no delay. All three also check that no `.tmp-review-nature-*` file is
  left. The existing rollback test is unchanged and still covers a non-retried
  `OSError` mid-transaction.
- Diagnostic: accepted. The reviewer read
  `.reviews/a.release-project-root.step1.tmp.r7.diag.py`: it repeats the
  fixture's pattern (plain `write_text` of the request and coordination files,
  then `_replace_all` at once), counts wrapped `PermissionError` by `winerror`
  and counts real sleeps. Both logs match the request table. Before the
  repair: 86 failures in TEMP and 119 under `.reviews`, all WinError 5, out of
  5,000 iterations each. After: zero escaped failures, and 87 plus 115 retries
  that then succeeded.
- R9 conclusion: the probe shows, on this host and on the claim's own replace
  path, the exact failure mode the round 6 analysis predicted, and shows the
  bounded retry absorbing every occurrence. Together with the green
  collection-order walk, that is enough to close R9. The exception of the one
  historical failure stays unknown, because its diagnostic was hidden then;
  the retained identity assertion would report operation, outcome and
  diagnostic if a different cause ever appeared.

R1 to R10 are resolved; R7 through the human's two named UV exceptions.

Architecture: no smell or layer violation. The retry is a private helper of
the existing backfill infrastructure class, copies the established pattern and
adds only `time` and `Final` imports. The edited module has 312 lines.

Performance: production processing stays linear. The retry adds at most 0.15
seconds per replacement, only under contention. In the strict audit, the only
Step 1 breaches are the two named UV cases (1.1758s and 1.1285s). The newly
listed launcher smoke case (1.0092s) starts the unchanged
`bin/code_review_answer.bat` in a real process; no Step 1 change touches that
path, so it belongs with the other deferred breaches.

Static coverage: the retry's success, retry, exhaustion and non-retried paths
are each reached by a unit test, and the requestor's `ghog full` stage
reported `cov=100`.

Feature integrity: no assertion, real process boundary or marker was removed,
and no test-level retry, sleep, skip, xfail, exclusion or process fallback was
added.

Validation plan effects:

The reviewer made three additions to the Step 1 rows of
`docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md`:

- *What was implemented*: a "Reviewer evidence for round 7" paragraph with
  the reviewer's `ghog check` and `ghog affected --no-cov` results and the
  acceptance of the probe as R9 closure evidence.
- *Architecture check*: one sentence placing the retry helper and one stating
  the edited module's 312 lines.
- *Performance check*: the closing yes-or-no sentence that
  `implementation-check` requires, which the round 7 rewrite had dropped.

The writer's exact Yes sentence, the removal of *Missing work for Step 1* and
the document-level `No, it is not implemented` line (Steps 2 to 6 pending) are
kept. Other steps, the plan, the umbrella, implementation, tests and
`a.commit` were not edited.

The evidence launcher attributed the patch (15 lines added, 1 changed) against
the pre-edit blob `ed5ac14ca02707143df98c09b07b989f07bc438d` (attributable,
not created). Only that patch was staged. The CRLF-aware
`git diff --cached --check` passes. This is review metadata, not a substantive
repair.

### Pre-repair mandatory checks and coverage for step 1 release-project-root (exchange 1) (round 7)

Requestor evidence, as reported and checked against its logs, not repeated:

- `ghog day --full=speed --whole-suite`: exit 0 at 13:49:45 +02:00,
  `proof=speed reused=none`. Its stages in
  `.reviews/a.release-project-root.step1.tmp.r7.timing/groundhog.log`: check
  exit 0, `affected --no-cov` exit 0, `full` exit 0 with `cov=100`, and
  `timings` exit 0 with `outliers=0 excluded=0`. Gemini included.
- The plan's `rg` scan: passed with only the intended post-gate
  `import_module` call and a setup comment.
- `ghog check`: exit 0 in `.reviews/a.release-project-root.step1.tmp.r7.check.log`.
- Focused `ghog single` on the role-nature tests: 19 tests, exit 0.
- Strict setup + call + teardown audit: 45 global breaches, raw verdict 8.
  The two Step 1 ones are the named UV exceptions; the inventory lists every
  measured cost and changes no ceiling or exclusion.

Reviewer evidence, each command run once from the project root through the
shared `ghog.bat` launcher, with the log-freshness proof and
`SWITCHPY_CHOICE=local` set for that process only:

- `ghog check`: exit 0. All static, EOF and Markdown checks passed.
- `ghog affected --no-cov --scope-file=.reviews/a.review-scope.code.v0.14.0.release-project-root.json`:
  exit 0, scope whole, `fail=0 warn=0 xfail=0`. Testmon selected all 3,702
  tests, the identity journeys included.

The reviewer did not run `ghog day`, `ghog full`, the strict audit or any
coverage measurement. Coverage was assessed statically.

### Resolved validation set and sources for step 1 release-project-root (exchange 1) (round 7)

The request and the current resolver produce the same ordered set as in
round 6:

1. `ghog day --full=speed --whole-suite`: source project.
2. `rg -n 'VIRTUAL_ENV|PYTHONPATH|glob|rglob|import_module' tools/release_workflow`:
   source plan.
3. `ghog check`: source request.

Re-running `resolve_code_review_validation` from the current
`tools/code_review_validation.py` reproduced this exact set. The reviewer did
not run the resolved set; the requestor reports all three green on the
current tree, and the logs agree.

### Resolver drift and direction for step 1 release-project-root (exchange 1) (round 7)

None: ordered commands and source labels agree with the current resolver.

### Repository state around validation for step 1 release-project-root (exchange 1) (round 7)

Request-time and reviewer baseline index tree:
`d9f84487329e92b82d6daf3790546941fd3b15b8` (identical). Final assessed index
tree after the reviewer metadata patch: `be3273f8049e7dacea7eaa24ddd5e4650cb829d4`.

The same ordered 52-path validation set was captured before and after
assessment: the 50 staged paths plus the ignored `a.ghog.log` and
`a.ghog.status`. The only tracked difference is
`docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md`, the intended
Step 1 row edit. The only ignored differences are the two ghog files written
by the reviewer's own runs. There are no untracked differences and no unstaged
changes. The raw `acceptable=false` reflects the intentional metadata edit.

Procedure note: the first after-capture was taken after staging. The reviewer
reset that one index entry to the recorded pre-edit blob, confirmed the tree
was `d9f84487…` again, then recaptured, compared, attributed and staged in the
documented order. The retained results come from that second pass.

Umbrella `docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md`: applicable,
digest `ca6fe473…0ec992` before and after, unchanged. No umbrella row was
modified.

Retained evidence: `.reviews/a.code-review-evidence.v0.14.0.release-project-root.step-1.json`,
with the inputs under `.reviews/a.release-project-root.step1.tmp.r7.review-*`.

### Repair inventory for step 1 release-project-root (exchange 1) (round 7)

Repairs made:

- Review metadata only: three additions to the Step 1 validation rows (round 7
  reviewer evidence, the retry's architecture placement and line count, and
  the missing performance closing sentence). Classification: polishing-only
  review metadata, not substantive. No implementation, test, plan or
  `a.commit` repair.

Paths staged:

- docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md (reviewer metadata patch only)

### Commit plan assessment for step 1 release-project-root (exchange 1) (round 7)

Ran `commit-plan-check.bat --format json` independently before assessment and
again after staging the Step 1 metadata. Both returned exit 0, `state=valid`,
`ready=true`, five ordered groups, 50 staged paths and no diagnostics. The JSON
is retained in `.reviews/a.release-project-root.step1.tmp.r7.review-commit-plan.json`
and `.reviews/a.release-project-root.step1.tmp.r7.review-commit-plan-after.json`.

Ordered groups:

1. `docs(review): qualify duplicate headings` (1 path)
2. `fix(review): retry transient role-nature replace` (2 paths)
3. `perf(tests): reuse CLI and repository initialization` (16 paths)
4. `feat(release): validate setup-owned runtime` (30 paths)
5. `docs(release-project-root): record step 1 validation` (1 path)

`a.commit` remains accurate: membership, order, conventional subjects and
bodies match the staged work. Group 2 names the retry and its three tests and
lands before group 3, so no commit in the series runs the in-process claim
without the retry. Group 5's body now records the R9 repair instead of an open
failure. The reviewer did not amend it. Mechanical readiness does not
authorize a commit.

### Findings and boundaries for step 1 release-project-root (exchange 1) (round 7)

Unresolved findings: None.

Boundary-crossing work: None.

### Human guidance response for step 1 release-project-root (exchange 1) (round 7)

Human guidance:

I authorize the R9 boundary repair: a bounded PermissionError retry in
RoleNatureBackfill._replace_all (tools/review_role_nature.py), as part of this
effort and of the Step 1 commit plan. Run the reviewer's cheap diagnostic
first and report its count whatever it is, then apply the repair. Do not hide
R9 with a test-level retry, a sleep, a separate process, a skip, an xfail or
an exclusion.

Guidance response:

The guidance authorizes writer work and instructs no reviewer repair, so the
reviewer changed no implementation or test file. The request's general "make
every safe repair" wording does not override that rule. The only reviewer
change is the Step 1 validation-row patch.

How each point was checked:

- Scope: the retry lives in `RoleNatureBackfill._replace_all` through a new
  helper in `tools/review_role_nature.py`, and it is part of this effort's
  Step 1 commit plan as group 2. No other production file changed.
- Bounded `PermissionError` retry: five attempts, only `PermissionError`,
  original error raised again at the end. Confirmed in the code and by the
  exhaustion and plain-`OSError` tests.
- Diagnostic first, count reported whatever it is: the before-run log is
  older than the after-run log, the probe source is the same for both, and
  the counts (86 and 119 before, 0 after) are reported in the request and the
  validation plan.
- Not hidden: since round 6, only the role-nature module, its unit test file
  and the validation plan changed. The identity journey still runs in process
  with every assertion and its diagnostic. The full walk reports
  `excluded=0`, and no test-level retry, sleep, process fallback, skip or
  xfail was added. The `time.sleep` replacement exists only inside the new
  unit tests, to record delays without waiting.

Scope: the staged work stays within Step 1 plus the authorized boundary
repair, and nothing from Step 2 was found. This answer authorizes no commit.

### Writer instructions for step 1 release-project-root (exchange 1) (round 7)

No writer change is required. Accept the reviewer's attributable Step 1 row
additions.

This answer is an advisory commit-ready recommendation. Present the
convergence gate to the human and wait for their choice: `Commit` or
`Rework and review again`. Do not commit, and do not start Step 2, before the
human's explicit `Commit`.

### Decision rationale for step 1 release-project-root (exchange 1) (round 7)

Recommend commit-ready (advisory). The six readiness-floor results are:

1. Identity: PASS. The exact plan, step 1, round 7, occurrence 1, code
   identity, umbrella and request-time index tree agree with the live
   exchange.
2. Implementation completeness: PASS. Step 1 is fully implemented, and R9 is
   closed by the authorized boundary repair.
3. Validation and coverage: PASS. The requestor's resolved set is green, with
   `cov=100` and speed proof on the current tree. The reviewer's `ghog check`
   and `ghog affected --no-cov` over all 3,702 tests are green, and the static
   coverage walk finds no gap.
4. Staged attribution: PASS. The only reviewer change is the attributable
   Step 1 validation-row patch. There is no substantive repair and no
   unrelated staged work.
5. Unresolved findings: PASS. R1 to R10 are resolved; R7 through the human's
   named exceptions. No boundary-crossing work remains.
6. `a.commit`: PASS. The independent checker reports exit 0, valid and ready,
   with all 50 paths in five accurate groups.

The repair is narrow, matches the existing writers, is tested in both
directions, and the probe shows it absorbing real failures on this host. The
remaining unknown, the exact exception of the single historical R9 failure,
cannot be recovered and is not a defect in the staged work. This
recommendation does not authorize a commit; the human decides.

### Final reviewer decision for step 1 release-project-root (exchange 1) (round 7)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-1-round-7 -->

## Round 7 by human - Step 1 - human-confirmation

- Recorded: 2026-10-23T21:47:13+02:00
- Exchange: code/code/v0.14.0/release-project-root
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.release-project-root.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 1
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-7 -->

## Round 1 by requestor - Step 2

- Recorded: 2026-10-24T16:47:44+02:00
- Exchange: code/code/v0.14.0/release-project-root
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.release-project-root.md
- Requestor LLM nature: codex
- Reviewer LLM nature: unrecorded
- Implementation step: 2
- Outcome: request

### Review identity for step 2 release-project-root (round 1)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.release-project-root.md
Implementation step: 2
Review round: 1

### Code review evidence for step 2 release-project-root (round 1)

request_index_tree: 6f96be7f882d33a6bafad4bf123ada99cdca97ef
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.release-project-root.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: test(review-resume): isolate immediate discovery
group 1 path: tests/unit/tools/test_review_resume/test_review_resume_expiry_tdd.py
group 2: test(suite): bound covered suite contention
group 2 path: tests/conftest.py
group 2 path: tests/unit/tools/markdown_check/test_runner/test_runner_tdd.py
group 2 path: tests/unit/tools/release_workflow/test_readiness/test_readiness_pbt.py
group 2 path: tests/unit/tools/test_code_review_request_scope/test_code_review_request_scope_tdd.py
group 2 path: tests/unit/tools/test_full_suite_levels_acceptance/test_full_suite_levels_review_acceptance_tdd.py
group 2 path: tests/unit/tools/test_groundhog_group_coverage/test_groundhog_group_coverage_pbt.py
group 2 path: tests/unit/tools/test_linear_order/test_linear_order_tdd.py
group 2 path: tests/unit/tools/test_review_mode_docs_acceptance/test_review_mode_docs_final_acceptance_tdd.py
group 2 path: tests/unit/tools/test_scope_capture/test_scope_capture_pbt.py
group 3: style(docs): format release review transcript
group 3 path: docs/v0.14.0/review.code.v0.14.0.release-project-root.md
group 4: feat(release): isolate Git and physical roots
group 4 path: tools/release_workflow/__init__.py
group 4 path: tools/release_workflow/git_environment.py
group 4 path: tools/release_workflow/git.py
group 4 path: tools/release_workflow/paths.py
group 4 path: tests/unit/tools/release_workflow/conftest.py
group 4 path: tests/unit/tools/release_workflow/git_test_support.py
group 4 path: tests/unit/tools/release_workflow/test_git/__init__.py
group 4 path: tests/unit/tools/release_workflow/test_git/test_config_files_tdd.py
group 4 path: tests/unit/tools/release_workflow/test_git/test_git_tdd.py
group 4 path: tests/unit/tools/release_workflow/test_git_environment/__init__.py
group 4 path: tests/unit/tools/release_workflow/test_git_environment/test_git_environment_tdd.py
group 4 path: tests/unit/tools/release_workflow/test_paths/__init__.py
group 4 path: tests/unit/tools/release_workflow/test_paths/conftest.py
group 4 path: tests/unit/tools/release_workflow/test_paths/test_paths_faults_tdd.py
group 4 path: tests/unit/tools/release_workflow/test_paths/test_paths_pbt.py
group 4 path: tests/unit/tools/release_workflow/test_paths/test_paths_tdd.py
group 5: docs(release-project-root): record step 2 validation
group 5 path: docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md
staged path: docs/v0.14.0/review.code.v0.14.0.release-project-root.md
staged path: tests/conftest.py
staged path: tests/unit/tools/markdown_check/test_runner/test_runner_tdd.py
staged path: tests/unit/tools/release_workflow/conftest.py
staged path: tests/unit/tools/release_workflow/git_test_support.py
staged path: tests/unit/tools/release_workflow/test_git/__init__.py
staged path: tests/unit/tools/release_workflow/test_git/test_config_files_tdd.py
staged path: tests/unit/tools/release_workflow/test_git/test_git_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_environment/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_environment/test_git_environment_tdd.py
staged path: tests/unit/tools/release_workflow/test_paths/__init__.py
staged path: tests/unit/tools/release_workflow/test_paths/conftest.py
staged path: tests/unit/tools/release_workflow/test_paths/test_paths_faults_tdd.py
staged path: tests/unit/tools/release_workflow/test_paths/test_paths_pbt.py
staged path: tests/unit/tools/release_workflow/test_paths/test_paths_tdd.py
staged path: tests/unit/tools/release_workflow/test_readiness/test_readiness_pbt.py
staged path: tests/unit/tools/test_code_review_request_scope/test_code_review_request_scope_tdd.py
staged path: tests/unit/tools/test_full_suite_levels_acceptance/test_full_suite_levels_review_acceptance_tdd.py
staged path: tests/unit/tools/test_groundhog_group_coverage/test_groundhog_group_coverage_pbt.py
staged path: tests/unit/tools/test_linear_order/test_linear_order_tdd.py
staged path: tests/unit/tools/test_review_mode_docs_acceptance/test_review_mode_docs_final_acceptance_tdd.py
staged path: tests/unit/tools/test_review_resume/test_review_resume_expiry_tdd.py
staged path: tests/unit/tools/test_scope_capture/test_scope_capture_pbt.py
staged path: tools/release_workflow/__init__.py
staged path: tools/release_workflow/git.py
staged path: tools/release_workflow/git_environment.py
staged path: tools/release_workflow/paths.py
```

### Validation scope for step 2 release-project-root (round 1)

Validation scope: the whole suite.

### Requestor assessment for step 2 release-project-root (round 1)

Yes. Step 2 has been fully implemented.

Static implementation-check on 2026-10-24 confirmed the exact Step 2 Git,
environment and physical-path boundaries. The validation plan records that
verdict; the overall topic remains incomplete because Steps 3 through 6 remain.
No tests ran during implementation-check.

- Validation: the completed `ghog day --full=speed --whole-suite` exited 0 at
  2026-10-24T01:01:03+02:00. Static checks took 49.0s; affected tests 35.6s;
  full passed 3,855 tests at 100% coverage in 4m05.4s. There were no failures,
  warnings, xfails, call outliers or exclusions. Maximum call was 0.862s.
- Timing provenance: coverage and setup/call/teardown durations came from one
  covered parallel full execution; there was no second timing traversal.
  The repaired canonical Groundhog runner is separate, uncommitted work.
  Measurements retain timing information but are not numerically equivalent
  to the previous sequential, uninstrumented pass.
- Performance: path validation walks only relevant ancestors; alias discovery
  reuses inspected metadata. No sibling scan or Git subprocess per ancestor
  appears. The four-worker full passed the five-minute phase bound but is
  slower overall than the preceding six-worker 3m35s full. Fixture moves do
  not themselves prove a total-runtime gain.
- Timing limits: the same-run inventory has 82 setup+call+teardown totals above
  one second. These are disclosed diagnostics, not a total-duration pass.
  The plan's current gate is call-only. The 33 path cases total 13.2459 worker
  seconds, including 5.0450s setup; the first shared-matrix consumer has 2.2313s
  setup and 2.7791s total. These sums are not elapsed wall time.
- Architecture: environment policy, native process execution and physical
  identity services are separated. New production modules have 143, 129 and
  151 physical lines; initializer 8. New test/support files are at most 167
  lines. The largest modified Python file is 435 lines, below the 550 risk
  band and 650 ceiling. The legacy Git helper is unchanged.
- Coverage: `[tool.coverage.run]` measures `tools`, with 100% reported by the
  completed full run. Dedicated tests cover policy matrices, native argument
  contracts, failures and real A/B, linked/nested repository and junction
  cases. Static reference inspection accounts for all changed test helpers;
  test/support files are outside the coverage percentage.
- Integrity: inherited routing cannot redirect explicit B to A; compatible
  user configuration survives. Separate linked Git metadata remains valid
  while managed paths reject foreign boundaries. The native watcher fixture
  repair does not claim a production watchdog fix. Real file-symlink evidence
  is unavailable on this host (Windows error 1314) and remains for later steps.
- Commit readiness: canonical `commit-plan-check --format json` reports
  ready=true, no diagnostics, all 28 staged paths in five groups. The final
  subject is `docs(release-project-root): record step 2 validation`.

R9 remains unresolved and explicitly nonblocking for review under the user's
instruction. Round 1 publication is authorized; no Step 2 commit is authorized.

### Implementation report for step 2 release-project-root (round 1)

The release foundation now has a dedicated controlled Git adapter and physical
project/path validation. The existing cross-platform Git helper remains unchanged.

- `git_environment.py` copies caller state into a read-only mapping, removes
  routing/configuration injection and execution/output controls, and preserves
  compatible identity, signing, credentials and configuration-file selectors.
  Configuration records retain scope, origin, key and value. The closed routing
  keys are accepted only from repository-owned scopes; command scope is rejected.
- `git.py` selects the first eligible absolute `git.exe` outside the original
  physical cwd, requires Git 2.31.0, and never retries another executable after
  selection. Every subprocess uses native arguments, explicit absolute cwd and
  the controlled environment. Child status/stdout/stderr remain available.
  Configuration inspection precedes internal output overrides. An empty
  `GIT_CONFIG` selector is rejected because it hides the normal configuration chain.
- `paths.py` distinguishes physical worktree, per-worktree Git directory and
  common directory. Explicit roots must equal the physical top-level. Alias
  discovery shares the same physical-root validator and reuses already inspected
  metadata, avoiding duplicate configuration/discovery subprocesses. Managed paths check original and
  resolved ancestor chains for escapes, nested repositories and non-directory
  ancestors, without scanning siblings or invoking Git per ancestor.
- Tests cover environment and configuration tables, first-executable policy,
  preserved subprocess failures, real A/B and linked/nested repositories,
  directory junctions, future destinations, fault boundaries and in-process
  path normalization properties. One minimal real repository is built per
  session and copied per case. A separate read-only linked worktree is shared
  by its configuration and identity checks. Tests select the installed native
  Git binary where available, verify it once and reuse that verified context;
  production executable selection remains unchanged. The real-Git modules
  share an xdist worker. Real fixture subprocesses have ten-second hang bounds.

The full suite exposed a Windows watchdog shutdown hang in the existing expiry
discovery fixture. That immediate-discovery test now injects notifications and
asserts no waiting is needed, while retaining actual request publication,
discovery, expiry and ownership checks. Native watcher acceptance stays intact.
This repairs the test fixture; it does not claim to fix watchdog's native
Windows CloseHandle race in production.

The Windows file-symlink capability probe returned privilege error 1314. No real
file-symlink evidence is claimed; the later Step 4 configuration-symlink cases
and complete-topic acceptance remain pending. Step 2's real directory-junction
cases are exercised.

The historical Step 1 transcript has only mechanical Markdown formatting repairs
identified by the static gate. It was not read as working context.

The user also directed a canonical tooling repair in `../llm-shared`: a speed
full run now collects coverage and durations together, and day no longer adds
a second whole-suite timings pass. That separate checkout's source, regression
tests, instructions and Diataxis changes are not part of this staged step.
The repair passed 250 focused tests and a real two-worker smoke that fails if
any test is executed twice. Four Diataxis pages, 13 links and three existing
wiki structure checks were verified there.

Covered parallel timing exposed contention and repeated fixture work. The
suite's automatic worker count is capped at four; explicit counts and xdist's
environment override still win. The real path authorization matrix shares
immutable validated A/B roots and real junctions, removing repeated config,
discovery and junction processes. Mutation/discovery cases remain isolated.
The Markdown inventory test uses installed native Git when available; it
still executes production lookup and a real tracked-file query. Selected
scope journeys cache real resolutions only for their stable symlink-free
paths; all file contents and review operations remain real.

Only named property-test outliers use smaller generated-example budgets.
Their strategies and assertions are unchanged; explicit shortest, deepest,
dense/cyclic, duplicate, Unicode and maximum-size cases retain boundary
coverage. Isolated profiles dropped graph generation from 1.231s to 0.229s,
fingerprint generation from 0.801s to 0.164s, folder reduction from 0.938s to
0.202s and lexical ordering from 0.641s to 0.213s. These profiles are diagnostic;
the covered full remains authoritative. No duration exclusions or raised
floor are used. Setup and total costs are recorded separately from call time.

The nine-outlier follow-up removes the second real config inspection in the
repository-owned routing test by observing validation's own result. Stable
path resolutions are reused in expiry fixtures; the read-only documentation
audit also reuses file contents. Prepared index and published-review baselines
are asserted in fixtures, with mutations and their assertions in the test call.
Those fixture moves alone are not claimed as total-runtime improvements;
the duration inventory records setup and total cost as well as call time.
The extra Path.resolve wrapper in the full-suite review test was removed
because its existing effort fixture already provides that cache.

Final validation: `ghog day --full=speed --whole-suite` passed with exit 0
and proof=speed at 2026-10-24T01:01:03+02:00. Static checks passed in
49.0s and affected tests in 35.6s. The covered full passed all 3,855 tests
at 100% coverage in 4m05.4s, with zero failures, warnings, xfails, call
outliers or exclusions. Maximum call was 0.862s. No second timings run
followed. Four workers satisfy this gate and the five-minute phase bound;
this is longer than the earlier six-worker 3m35s full, so no overall runtime
reduction is claimed.

The same-run setup/call/teardown inventory contains 82 totals above one
second; that is diagnostic, not the plan's call-only gate. Its 33 path
cases sum to 5.0450s setup, 8.1528s call, 0.0481s teardown and 13.2459s
total worker time. Shared fixture setup is charged to its first consumer;
equivalent-physical-roots has 2.2313s setup and 2.7791s total. These sums
are not wall time. Evidence is in the private timing folder's groundhog.log
and durations.json, measured 2026-10-23T23:01:00.785951+00:00.

Formal implementation-check is complete: Step 2 is fully implemented, while
Steps 3 through 6 and whole-topic completion remain pending. The validation
document records the static source, architecture, coverage, performance and
integrity assessment. No tests were repeated for this static check.

Root `a.commit` contains five ordered groups covering all 28 staged paths
exactly once. The canonical formatter completed and commit-plan-check returned
ready=true with no diagnostics. The validation record is the last group, titled
`docs(release-project-root): record step 2 validation`.

The user authorized Step 2 Round 1 publication on resume if ready. R9 remains
unresolved and explicitly nonblocking for review. Canonical tooling changes
are to be committed later. No Step 2 commit has been made or authorized.

Writer notes: `.reviews/a.release-project-root.step2.journal.md` and
`.reviews/a.release-project-root.step2.handoff.md`.

### Change summary for step 2 release-project-root (round 1)

The staged index contains 28 paths, assigned exactly once to five ordered groups
in root `a.commit`. The canonical readiness check reports ready=true with no
diagnostics. No canonical sibling-checkout repair is included.

#### Group 1 immediate expiry discovery for step 2 release-project-root (round 1)

Subject: `test(review-resume): isolate immediate discovery`

- `tests/unit/tools/test_review_resume/test_review_resume_expiry_tdd.py`

Inject notifications only for an already-published request, assert no wait and
one cleanup, retain real expiry/discovery/ownership and stable path resolution.

#### Group 2 covered suite contention for step 2 release-project-root (round 1)

Subject: `test(suite): bound covered suite contention`

- `tests/conftest.py`
- `tests/unit/tools/markdown_check/test_runner/test_runner_tdd.py`
- `tests/unit/tools/release_workflow/test_readiness/test_readiness_pbt.py`
- `tests/unit/tools/test_code_review_request_scope/test_code_review_request_scope_tdd.py`
- `tests/unit/tools/test_full_suite_levels_acceptance/test_full_suite_levels_review_acceptance_tdd.py`
- `tests/unit/tools/test_groundhog_group_coverage/test_groundhog_group_coverage_pbt.py`
- `tests/unit/tools/test_linear_order/test_linear_order_tdd.py`
- `tests/unit/tools/test_review_mode_docs_acceptance/test_review_mode_docs_final_acceptance_tdd.py`
- `tests/unit/tools/test_scope_capture/test_scope_capture_pbt.py`

Cap automatic workers at four, retain overrides, use native installed Git,
reuse stable resolution/read-only content and assert published baselines in
fixtures. Four named property suites use 25 examples plus explicit boundaries.

#### Group 3 transcript formatting for step 2 release-project-root (round 1)

Subject: `style(docs): format release review transcript`

- `docs/v0.14.0/review.code.v0.14.0.release-project-root.md`

Mechanical historical heading, emphasis and list-spacing repairs from the
static Markdown gate. Review publication appends the new evidence separately.

#### Group 4 Git and physical project boundaries for step 2 release-project-root (round 1)

Subject: `feat(release): isolate Git and physical roots`

- `tools/release_workflow/__init__.py`
- `tools/release_workflow/git_environment.py`
- `tools/release_workflow/git.py`
- `tools/release_workflow/paths.py`
- `tests/unit/tools/release_workflow/conftest.py`
- `tests/unit/tools/release_workflow/git_test_support.py`
- `tests/unit/tools/release_workflow/test_git/__init__.py`
- `tests/unit/tools/release_workflow/test_git/test_config_files_tdd.py`
- `tests/unit/tools/release_workflow/test_git/test_git_tdd.py`
- `tests/unit/tools/release_workflow/test_git_environment/__init__.py`
- `tests/unit/tools/release_workflow/test_git_environment/test_git_environment_tdd.py`
- `tests/unit/tools/release_workflow/test_paths/__init__.py`
- `tests/unit/tools/release_workflow/test_paths/conftest.py`
- `tests/unit/tools/release_workflow/test_paths/test_paths_faults_tdd.py`
- `tests/unit/tools/release_workflow/test_paths/test_paths_pbt.py`
- `tests/unit/tools/release_workflow/test_paths/test_paths_tdd.py`

Implement copied environment/configuration policy, pinned native Git and
physical root/destination validation, with deterministic faults and real
repository/junction matrices. Reuse small real templates and immutable setup;
mutation cases remain isolated. The path property retains 20 examples plus
explicit shortest/deepest boundaries.

#### Group 5 validation record for step 2 release-project-root (round 1)

Subject: `docs(release-project-root): record step 2 validation`

- `docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md`

Record the fully implemented Step 2 verdict, measured evidence and limitations.
The overall topic remains incomplete, and R9 remains nonblocking for review.

### Writer response for step 2 release-project-root (round 1)

Writer response:

This is Step 2 round 1. There is no earlier Step 2 feedback to accept or dispute.
The user authorized publication on resume if ready. The static check is complete
and the grouped commit plan is mechanically ready. The requestor publishes and
waits; the independent reviewer is externally started. No Step 2 commit has been
authorized. R9 remains unresolved and nonblocking as directed by the user.

### Reviewer focus for step 2 release-project-root (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-2-round-1 -->

## Round 1 by reviewer - Step 2

- Recorded: 2026-10-24T17:30:45+02:00
- Exchange: code/code/v0.14.0/release-project-root
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.release-project-root.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 2
- Outcome: answer

### Assessed index identity for step 2 release-project-root (exchange 1) (round 1)

Baseline index tree: 6f96be7f882d33a6bafad4bf123ada99cdca97ef

Assessed index tree: 25f55aeb2b4e568fa512f856221a319614f60e4f

### Implementation check for step 2 release-project-root (exchange 1) (round 1)

Result:

No. Step 2 has NOT been fully implemented.

The pinned executable, copied environment, configuration origin/scope check,
physical identity and managed-path services are in place. Their real A/B,
linked/nested repository and junction tests pass. Three gaps keep Step 2
open, each reproduced against the staged sources with real
`git version 2.54.0.windows.1` (R1 to R3 below). The worst one silently
disables the configuration scope check that Q01 and AC3 rely on.

Plan conformance, checked item by item:

- Q11 selection: `_select_executable` (`git.py:49`) skips empty, relative,
  cwd-identical and inaccessible entries and only considers `git.exe`, so no
  `PATHEXT` shim can win. It returns the first eligible file without fallback.
  `create` rejects unknown, malformed and pre-2.31.0 versions.
- Subprocess boundary: the plan's
  `rg -n 'subprocess|cwd=|shell=|GIT_' tools/release_workflow` scan, run
  read-only, finds one production `subprocess.run` (`git.py:106`). It uses
  the pinned absolute path, native argument lists, `shell=False`, an absolute
  existing cwd checked per call, the copied environment, and detached stdin in
  non-interactive mode. Configuration inspection adds no `-c` option, so
  internal overrides never show as command scope.
- Environment classes: routing, counted and parameter injection, executable
  and template, and pathspec/diff output controls are removed and diagnosed,
  case-insensitively, without mutating the source mapping. Selectors, identity,
  signing, SSH and credential settings survive. The Windows stream-redirection
  variables are missing from the output class (R2).
- Configuration policy: the closed key set `core.worktree`, `core.bare`,
  `extensions.worktreeConfig` is accepted only in `local`/`worktree` scope,
  and every `command` entry fails, with scope, origin and key in the message.
  This holds only while the child's output decodes (R1).
- Identity: `ProjectIdentity` keeps the physical root, per-worktree Git
  directory and common directory apart. Explicit roots must be Git's physical
  top-level by filesystem identity. Discovery reuses the metadata it already
  inspected from the start directory. Its `_validated_identity` call compares
  the discovered root with itself, which is equivalent rather than an extra
  check.
- `authorize_path` walks the supplied spelling and the resolved path once each,
  stops at a filesystem-identical root, and rejects nested worktrees, gitfiles,
  bare layouts, non-directory ancestors and escapes. It does not reject a
  linked worktree's own `.git` gitfile (R3).

Probe evidence (reviewer scratch script run on temporary repositories, outside
the staged tree):

- R1: a global file holding `[user] name = Jos\xe9` (one cp1252 byte) makes
  the config child return exit 0 with `stdout=None`. The strict UTF-8 reader
  thread fails, prints a traceback and drops the stream. `inspect_config`
  then returns `()`. Add `[core] worktree = ../A` to that file and
  `validate_project` accepts the root. The same key without the byte is
  rejected.
- R2: `GIT_REDIRECT_STDOUT`, `GIT_REDIRECT_STDERR` and `GIT_REDIRECT_STDIN`
  survive `controlled_environment`. With `GIT_REDIRECT_STDERR=off`, a failing
  `rev-parse` gives a `GitCommandError` with return code 128 and stderr `''`.
  With `GIT_REDIRECT_STDOUT=off`, `create` fails as "Cannot establish Git
  version". With a file value, Git first writes `git version ...` into that
  file. `GIT_REDIRECT_STDIN` was not probed.
- R3: in a real linked worktree, `authorize_path(identity, ".git")` returns
  `<linked>\.git`, the gitfile that ties the worktree to its metadata. The
  ordinary repository case is rejected.

Architecture: environment policy (`git_environment.py`) is pure data
transformation with no process or filesystem access. `git.py` owns the only
production subprocess boundary. `paths.py` uses that context plus filesystem
identity. The package initializer stays dependency-free for the readiness
bootstrap. The legacy `tools/git_command.py` and its test are unchanged. No
layer violation was found. Physical lines: `git.py` 143, `git_environment.py`
129, `paths.py` 151, initializer 8. The largest new test file is 167 lines and
the largest modified Python file is 435. All are below the 550-line risk band.

Performance: environment copying and configuration parsing are single passes.
Executable selection is linear in PATH entries. Root validation makes one
inspection and one `rev-parse`. Authorization makes two ancestor walks with a
constant number of stat calls per ancestor, with no sibling scan, sort or
pairwise work. No O(n^2) or O(n log n) computation was added.

Static coverage: `[tool.coverage.run] source = ["tools"]` with
`fail_under = 100` measures the three new modules. `__init__.py` is omitted.
Walking each branch of `git_environment.py`, `git.py` and `paths.py` against
`test_git_environment`, `test_git` (adapter and real config files) and
`test_paths` (real, faults, properties) found every existing branch exercised.
This agrees with the requestor's 100%. Test support files are outside the
gate. `GitSandbox`, `create_template`, `copy_template`, `RecordingGit` and the
new fixtures are all referenced. The code R1 to R3 call for needs new tests,
listed in the findings.

Feature integrity: explicit B stays B under stale A routing and index inputs.
Compatible user configuration survives and the parent mapping is unchanged.
The suite-contention changes keep every assertion; the property-test example
caps add explicit boundary examples. The expiry fixture's injected
notification adapter is bound before the `with` block
(`tools/review_exchange_cli_resume.py:331-340`), so its "no wait" and
"one exit" assertions check real calls. R1 to R3 are integrity gaps in the new
services, not regressions of existing features.

Validation plan effects:

Changed only Step 2 rows in
`docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md`:

- *Analysis of Step 2 implementation state* now starts with the exact No
  sentence, followed by a short rationale naming the three gaps.
- A new *Missing work for Step 2* section sits right after *What was
  implemented for Step 2*. It holds one concrete bullet per code or test change
  for R1 to R3.
- The *Feature integrity for Step 2* conclusion now names the same three gaps.

The document-level opening line stays `No, it is not implemented.`. The header
sentence "Step 2's controlled Git and physical-path services pass the full
speed day and static implementation check." lies outside the Step 2 rows and
was left for the writer to refresh. The architecture, performance and coverage
sub-sections, other steps, the plan, the umbrella, implementation, tests and
`a.commit` were not edited.

The evidence launcher attributed the patch from pre-edit blob
`7f63747df61b0a69703fc3bb8ff80bff18f30867` (attributable, not created). Only
that patch was staged. The project Markdown check (`markdown-check.bat --root .`)
passes after the edit. This is review metadata, not a substantive repair.

### Pre-repair mandatory checks and coverage for step 2 release-project-root (exchange 1) (round 1)

Requestor evidence: `ghog day --full=speed --whole-suite` completed on
2026-10-24 at 01:01:03+02:00 with exit 0 and `proof=speed`: 3,855 tests,
100% coverage, no failures, warnings, xfails, call outliers or exclusions.
The request states that this walk used the uncommitted canonical groundhog
repair in the main llm-shared checkout. This is reported evidence; the
reviewer did not repeat it.

Reviewer evidence, each command run once from the project root through the
shared `ghog.bat` launcher with `SWITCHPY_CHOICE=local` for that process and
the log-freshness proof:

- `ghog check`: exit 0, all `check.bat` checks passed for the project
  (`fail=0 warn=0`).
- `ghog affected --no-cov --scope-file=.reviews/a.review-scope.code.v0.14.0.release-project-root.json`:
  exit 0, scope whole, 3,855 tests, `fail=0 warn=0 xfail=0`. The changed
  `tests/conftest.py` selects the whole suite.

The reviewer did not run `ghog day`, `ghog full` or any coverage measurement.
Coverage was assessed statically. R1 to R3 come from a separate reviewer probe
script on temporary repositories, not from the suite.

### Resolved validation set and sources for step 2 release-project-root (exchange 1) (round 1)

The request and the current resolver produce the same ordered set:

1. `ghog day --full=speed --whole-suite`: source project.

No `.review-validation` file exists, so the project default is the built-in
`ghog day --full=speed`, completed with the bound `--whole-suite` selector for
scope `whole`. The comparison ran `resolve_code_review_validation` from the
current `tools/code_review_validation.py` with that default and no additions.
The reviewer did not run the resolved set.

### Resolver drift and direction for step 2 release-project-root (exchange 1) (round 1)

None in resolver output: ordered commands and source labels agree.

Direction note for the requestor: the plan's Step 2 completion names
`rg -n 'subprocess|cwd=|shell=|GIT_' tools/release_workflow`, but the request
does not carry it. As in Step 1 round 1, pass it with
`--plan-validation-command` on the next request so it appears in the resolved
set with its plan source. The reviewer ran it read-only for this assessment.

### Repository state around validation for step 2 release-project-root (exchange 1) (round 1)

Request-time and reviewer baseline index tree:
`6f96be7f882d33a6bafad4bf123ada99cdca97ef` (identical). Final assessed index
tree after the reviewer metadata patch:
`25f55aeb2b4e568fa512f856221a319614f60e4f`.

The same ordered 30-path validation set (the 28 staged paths plus the ignored
`a.ghog.log` and `a.ghog.status`) was captured before and after assessment.
The comparison reports tracked differences only for
`docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md` and `<index>`,
ignored differences only for the two ghog files written by the reviewer's
evidence commands, and no untracked differences. The raw `acceptable=false`
reflects the intentional Step 2 metadata edit; the attribution shows every
changed hunk lies in the Step 2 rows. The reviewer's ghog runs left no tracked
side effect. There is no overlap with writer work. The only other working-tree
change is the protocol-appended round 1 request in the review transcript.

Umbrella `docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md`: applicable,
digest `ca6fe473…0ec992` before and after, unchanged. No umbrella row was
modified.

Retained evidence:
`.reviews/a.code-review-evidence.v0.14.0.release-project-root.step-2.json`,
with the inputs under `.reviews/a.release-project-root.step2.tmp.r1.*`.

### Repair inventory for step 2 release-project-root (exchange 1) (round 1)

Repairs made:

- Review metadata only: changed the Step 2 validation rows to No, added
  *Missing work for Step 2* (R1 to R3) and qualified the feature-integrity
  conclusion. No implementation, test, plan or `a.commit` repair.

Paths staged:

- docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md (reviewer metadata patch only)

### Commit plan assessment for step 2 release-project-root (exchange 1) (round 1)

Ran `commit-plan-check.bat --format json` independently before assessment and
again after staging the Step 2 metadata. Both returned exit 0, `state=valid`,
`ready=true`, five ordered groups, 28 staged paths and no diagnostics. The
post-staging JSON is retained in
`.reviews/a.release-project-root.step2.tmp.r1.commit-plan-after.json`.

Ordered groups:

1. `test(review-resume): isolate immediate discovery` (1 path)
2. `test(suite): bound covered suite contention` (9 paths)
3. `style(docs): format release review transcript` (1 path)
4. `feat(release): isolate Git and physical roots` (16 paths)
5. `docs(release-project-root): record step 2 validation` (1 path)

Membership and conventional subjects match the staged work. Groups 1 to 3
import nothing introduced by group 4, so each intermediate commit stands on
its own. The reviewer did not amend `a.commit`.

Two points need the writer when `a.commit` is regenerated:

- Group 5's body says "Step 2 is fully implemented", which the staged
  validation rows no longer claim. Rewrite it together with the R1 to R3
  fixes.
- Group 3 (R4): batch commit re-runs each block's `git add -A <path>` before
  committing (`tools/git_batch_commit_workflow.py:297`). So group 3 will commit
  the working transcript, which already holds the 362-line protocol-appended
  Step 2 round 1 request and will hold every later round, under a `style(docs)`
  subject that describes only the historical formatting.

Mechanical readiness does not resolve the findings and does not authorize a
commit.

### Findings and boundaries for step 2 release-project-root (exchange 1) (round 1)

Unresolved findings:

- R1 (P1): a non-UTF-8 byte in Git output turns the configuration scope check
  into a silent pass. `_execute` (`tools/release_workflow/git.py:106-110`) uses
  `text=True, encoding="utf-8"` with strict errors. On Windows,
  `subprocess.run(capture_output=True)` decodes in reader threads. A decode
  error only prints a thread traceback, and the run returns exit 0 with
  `stdout=None`. `validate_config(None)` (`git_environment.py:104`) returns
  `()`. Reproduced with real Git: a selected global file holding
  `[user] name = Jos\xe9` plus `[core] worktree = ../A` passes `inspect_config`
  with no entries, and `validate_project` accepts the root. The same key
  without the byte is rejected. A cp1252-saved `.gitconfig` with an accented
  name is a normal Windows setup, so the AC3/Q01 guarantee ("reject routing
  keys supplied outside the selected repository's own configuration") fails
  open there. Capture bytes and decode in `_execute`. Never return an
  undecodable or missing stream as success: either raise `GitPolicyError`
  naming the command, or decode configuration output losslessly (for example
  with `surrogateescape`) so every record is still checked. Recommended:
  lossless decoding for configuration values, so legacy files keep working,
  and strict UTF-8 that fails closed for metadata paths. Add a real-Git case
  to `test_config_files_tdd.py` (cp1252 byte plus external `core.worktree`
  must be rejected) and a unit case in `test_git_tdd.py` for the undecodable
  or missing stream.
- R2 (P2): Git for Windows' stream-redirection variables survive the
  output-shaping policy. The design's output class says "do not inherit
  output-shaping or pathspec overrides" and requires the implementation to
  enumerate that class. `GIT_REDIRECT_STDIN`, `GIT_REDIRECT_STDOUT` and
  `GIT_REDIRECT_STDERR` are absent from `_OUTPUT`
  (`git_environment.py:29-34`). Reproduced: with `GIT_REDIRECT_STDERR=off`, a
  failing child's retained result has return code 128 and stderr `''`. That
  breaks the plan's "keep original child status/stderr available".
  `GIT_REDIRECT_STDOUT=off` makes `create` fail with the misleading
  "Cannot establish Git version ... ''". A file value makes Git write the
  version text into that arbitrary file first. `GIT_REDIRECT_STDIN` would
  replace the detached stdin chosen for non-interactive mode; not probed.
  Add the three names to the removed output inputs, and add them to `REMOVED`
  in `test_git_environment_tdd.py`.
- R3 (P2): a linked worktree's own `.git` gitfile is authorized as a managed
  destination. In a real linked worktree, `authorize_path(identity, ".git")`
  returns `<linked>\.git`. The target is a file, so
  `_check_ancestors` (`paths.py:110-127`) skips the foreign-boundary test, and
  the non-directory test exempts the target itself. A managed write there
  would detach the worktree from its Git directory. In an ordinary
  repository, `.git` is rejected through the bare-layout check, and
  `test_git_metadata_is_not_a_managed_destination` covers only that case. The
  plan keeps linked Git metadata distinct from managed destinations. Reject
  the worktree's own `.git` entry, directory or gitfile, as a target or
  ancestor, and add the linked-worktree case to `test_paths_tdd.py` using the
  existing `linked_sandbox` fixture.
- R4 (P3): `a.commit` group 3 will commit more than its subject says (see the
  commit plan assessment). Step 1 recorded its rounds as
  `docs(review): record step 1 code review` (53f5b8a). When regenerating
  `a.commit` at convergence, give the transcript a subject and body that cover
  the Step 2 review record with the mechanical formatting, or split them.
- R5 (P3): the staged `tests/conftest.py` docstring now places slowness
  detection in "the covered ``ghog full`` run". That describes the uncommitted
  canonical groundhog repair in the main checkout. This branch's
  `tools/groundhog/day.py:24-28` still runs a timed sequential `timings` step
  after a green speed full. Keep wording that is true for this branch, such as
  "the project's own duration gate", until that repair lands here.

Boundary-crossing work: None.

### Writer instructions for step 2 release-project-root (exchange 1) (round 1)

Fix R1 to R3 within Step 2 and add the listed tests. R1 comes first because
it disables the policy check the other cases depend on. For R1, choose between
fail-closed and lossless decoding of configuration output inside the step; the
recommendation is in the finding. Then fix R5 and rewrite the Step 2
validation rows after the fixes. Remove *Missing work for Step 2* only when
every bullet is done, and restore the Yes sentence only then. Also refresh the
document header sentence about Step 2 and the `a.commit` group 5 body, which
the reviewer did not touch. Handle R4 when `a.commit` is regenerated.

Run the requestor-owned resolved set (`ghog day --full=speed --whole-suite`).
Pass the plan's `rg -n 'subprocess|cwd=|shell=|GIT_' tools/release_workflow`
scan as a plan validation command on the next request. Update `a.commit` if
staged membership changes, then publish the replacement request through the
normal requestor workflow.

The request asks for "every safe, unambiguous repair" but carries no literal
`Human guidance:` block, so the reviewer repaired no implementation or test
file. Its only staged change is the attributable Step 2 validation-row patch.
R9 was carried as the user's nonblocking item and was not reassessed.

### Decision rationale for step 2 release-project-root (exchange 1) (round 1)

Recommend changes-requested. The six readiness-floor results are:

1. Identity: PASS. Exact plan, step 2, round 1, occurrence 1, code identity,
   umbrella and request-time index tree agree with the live exchange.
2. Implementation completeness: FAIL. R1 (configuration check fails open on
   undecodable output), R2 (stream-redirection variables survive) and R3
   (linked-worktree gitfile is a managed destination) remain.
3. Validation and coverage: PASS for the current code. Requestor speed and
   coverage evidence is green. The reviewer's `ghog check` and focused
   `ghog affected --no-cov` run (3,855 tests) are green, and the static
   coverage walk finds no gap in the staged code. R1 to R3 still need new
   tests.
4. Staged attribution: PASS. The sole reviewer change is the attributable
   Step 2 validation metadata. There is no substantive repair and no unrelated
   staged work.
5. Unresolved findings: FAIL. R1 to R5 remain open, R1 at P1.
6. `a.commit`: PASS mechanically. The independent checker reports exit 0,
   valid, ready, with all 28 paths in five groups. The group 5 body and the
   group 3 subject (R4) need a refresh.

The implementation and unresolved-findings failures block commit-readiness,
even though the walks are green and the commit plan is valid.

### Final reviewer decision for step 2 release-project-root (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-2-round-1 -->

## Round 2 by requestor - Step 2

- Recorded: 2026-10-24T18:25:17+02:00
- Exchange: code/code/v0.14.0/release-project-root
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.release-project-root.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 2
- Outcome: request

### Review identity for step 2 release-project-root (round 2)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.release-project-root.md
Implementation step: 2
Review round: 2

### Code review evidence for step 2 release-project-root (round 2)

request_index_tree: c93fd095b4e72643398210377ca589a21b1d1d0e
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)
- `rg -n 'subprocess|cwd=|shell=|GIT_' tools/release_workflow` (sources: plan)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.release-project-root.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: test(review-resume): isolate immediate discovery
group 1 path: tests/unit/tools/test_review_resume/test_review_resume_expiry_tdd.py
group 2: test(suite): bound covered suite contention
group 2 path: tests/conftest.py
group 2 path: tests/unit/tools/markdown_check/test_runner/test_runner_tdd.py
group 2 path: tests/unit/tools/release_workflow/test_readiness/test_readiness_pbt.py
group 2 path: tests/unit/tools/test_code_review_request_scope/test_code_review_request_scope_tdd.py
group 2 path: tests/unit/tools/test_full_suite_levels_acceptance/test_full_suite_levels_review_acceptance_tdd.py
group 2 path: tests/unit/tools/test_groundhog_group_coverage/test_groundhog_group_coverage_pbt.py
group 2 path: tests/unit/tools/test_instruction_structure/conftest.py
group 2 path: tests/unit/tools/test_instruction_structure/test_instruction_structure_tdd.py
group 2 path: tests/unit/tools/test_linear_order/test_linear_order_tdd.py
group 2 path: tests/unit/tools/test_review_mode_docs_acceptance/test_review_mode_docs_final_acceptance_tdd.py
group 2 path: tests/unit/tools/test_scope_capture/test_scope_capture_pbt.py
group 3: docs(review): record step 2 code review
group 3 path: docs/v0.14.0/review.code.v0.14.0.release-project-root.md
group 4: feat(release): isolate Git and physical roots
group 4 path: tools/release_workflow/__init__.py
group 4 path: tools/release_workflow/git_environment.py
group 4 path: tools/release_workflow/git.py
group 4 path: tools/release_workflow/paths.py
group 4 path: tests/unit/tools/release_workflow/conftest.py
group 4 path: tests/unit/tools/release_workflow/git_test_support.py
group 4 path: tests/unit/tools/release_workflow/test_git/__init__.py
group 4 path: tests/unit/tools/release_workflow/test_git/conftest.py
group 4 path: tests/unit/tools/release_workflow/test_git/test_config_files_tdd.py
group 4 path: tests/unit/tools/release_workflow/test_git/test_git_tdd.py
group 4 path: tests/unit/tools/release_workflow/test_git_environment/__init__.py
group 4 path: tests/unit/tools/release_workflow/test_git_environment/test_git_environment_tdd.py
group 4 path: tests/unit/tools/release_workflow/test_paths/__init__.py
group 4 path: tests/unit/tools/release_workflow/test_paths/conftest.py
group 4 path: tests/unit/tools/release_workflow/test_paths/test_paths_faults_tdd.py
group 4 path: tests/unit/tools/release_workflow/test_paths/test_paths_pbt.py
group 4 path: tests/unit/tools/release_workflow/test_paths/test_paths_tdd.py
group 5: docs(release-project-root): record step 2 validation
group 5 path: docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md
staged path: docs/v0.14.0/review.code.v0.14.0.release-project-root.md
staged path: tests/conftest.py
staged path: tests/unit/tools/markdown_check/test_runner/test_runner_tdd.py
staged path: tests/unit/tools/release_workflow/conftest.py
staged path: tests/unit/tools/release_workflow/git_test_support.py
staged path: tests/unit/tools/release_workflow/test_git/__init__.py
staged path: tests/unit/tools/release_workflow/test_git/conftest.py
staged path: tests/unit/tools/release_workflow/test_git/test_config_files_tdd.py
staged path: tests/unit/tools/release_workflow/test_git/test_git_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_environment/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_environment/test_git_environment_tdd.py
staged path: tests/unit/tools/release_workflow/test_paths/__init__.py
staged path: tests/unit/tools/release_workflow/test_paths/conftest.py
staged path: tests/unit/tools/release_workflow/test_paths/test_paths_faults_tdd.py
staged path: tests/unit/tools/release_workflow/test_paths/test_paths_pbt.py
staged path: tests/unit/tools/release_workflow/test_paths/test_paths_tdd.py
staged path: tests/unit/tools/release_workflow/test_readiness/test_readiness_pbt.py
staged path: tests/unit/tools/test_code_review_request_scope/test_code_review_request_scope_tdd.py
staged path: tests/unit/tools/test_full_suite_levels_acceptance/test_full_suite_levels_review_acceptance_tdd.py
staged path: tests/unit/tools/test_groundhog_group_coverage/test_groundhog_group_coverage_pbt.py
staged path: tests/unit/tools/test_instruction_structure/conftest.py
staged path: tests/unit/tools/test_instruction_structure/test_instruction_structure_tdd.py
staged path: tests/unit/tools/test_linear_order/test_linear_order_tdd.py
staged path: tests/unit/tools/test_review_mode_docs_acceptance/test_review_mode_docs_final_acceptance_tdd.py
staged path: tests/unit/tools/test_review_resume/test_review_resume_expiry_tdd.py
staged path: tests/unit/tools/test_scope_capture/test_scope_capture_pbt.py
staged path: tools/release_workflow/__init__.py
staged path: tools/release_workflow/git.py
staged path: tools/release_workflow/git_environment.py
staged path: tools/release_workflow/paths.py
```

### Validation scope for step 2 release-project-root (round 2)

Validation scope: the whole suite.

### Requestor assessment for step 2 release-project-root (round 2)

Yes. Step 2 has been fully implemented.

Round 2 repairs the accepted Round 1 gaps in explicit byte decoding,
Windows stream-redirection removal and own-Git-metadata authorization. Real
regressions reproduced the defects first; focused Git/environment/path tests
and the unchanged legacy Git-helper regression pass. The final static
implementation-check updates only Step 2 and the document's summary; Steps
3 through 6 remain pending and the overall status stays No.

The required `ghog day --full=speed --whole-suite` completed on
2026-10-24T18:17:42+02:00, exit 0, proof=speed, reused=none. Static checks
passed in 1m23.7s, affected tests in 18.0s, and the full passed all 3,866 tests
at 100% measured tools coverage in 3m12.0s. There were zero failures, warnings,
xfails, call outliers or exclusions. Maximum call was 0.6740s. Coverage and
durations were collected in that same full run, with no second timing pass.
Evidence: `.reviews/a.release-project-root.step2.tmp.r2.timing/groundhog.log`
and `durations.json` (measured 2026-10-24T16:17:40.839600+00:00).

The exact plan scan `rg -n 'subprocess|cwd=|shell=|GIT_' tools/release_workflow`
was inspected and is included as a plan validation command. The adapter has
one pinned subprocess boundary, native arguments, explicit cwd, copied
environment and shell=False. The existing cross-platform Git helper is
unchanged. Production responsibilities remain separated; no new production
types were added during repair. Production files have 159/130/160 lines;
all changed Python files stay under 650. The existing instruction-structure
test shrinks to 648 lines, with its fixture in a separate 28-line file.

Setup remains accounted for: 67 suite totals exceed one second, a diagnostic
separate from the plan's call gate. The 36 path cases sum to 5.2901s setup,
8.5492s call and 0.0418s teardown, 13.8811s worker time rather than wall time.
The largest total is legacy migration at 30.2061s, including 30.2035s setup.
The final explicit outside-Git probe has setup/call/total
0.6836/0.0012/0.6858s; repository routing 0.8397/0.0011/0.8419s;
diagram check 0.0050/0.0030/0.0087s. Three flagged include cases have
setup 0.3180s to 0.3345s, calls about 0.001s and total 0.3202s to 0.3369s.
Fixtures retain real operations and every assertion/parameter. Phase moves
and variable host contention are not claimed as a causal total-runtime gain.

Static coverage inspection confirms module-named unit suites exercise every
new production boundary. Files under tests are outside the tools coverage
scope; each new helper and fixture is referenced or pytest-discovered. Real
subprocess execution supplies behavior evidence, not child-process coverage.
There is no architecture, call-gate performance, coverage or unreferenced
top-level-symbol issue requiring further Step 2 implementation.

Real directory junctions are covered. File-symlink capability failed with
Windows error 1314, leaving later Step 4/whole-topic evidence pending. The
fixture change does not claim a production watchdog-race repair. Canonical
Groundhog changes remain separate uncommitted sibling work. R9 stays
unresolved and explicitly nonblocking under the user's standing direction.
No Step 2 commit is authorized or made.

### Implementation report for step 2 release-project-root (round 2)

The release foundation has a dedicated controlled Git adapter and physical
project/path validation. Step 2 Round 2 repairs all five accepted Round 1
findings; the existing cross-platform Git helper remains unchanged.

- `git_environment.py` copies caller state into a read-only mapping, removes
  routing/configuration injection and execution/output controls, and preserves
  compatible identity, signing, credentials and configuration-file selectors.
  Configuration records retain scope, origin, key and value. Routing keys are
  accepted only from repository-owned scopes; command scope is rejected.
  The removed output inputs now include all three Windows stream redirects,
  with case-insensitive removal and parent-state preservation tests.
- `git.py` selects the first eligible absolute `git.exe` outside the original
  physical cwd and requires Git 2.31.0. Every subprocess uses native arguments,
  explicit absolute cwd and the copied environment. Capture now returns bytes;
  decoding runs on the caller thread. Missing streams raise a command-naming
  policy error. Configuration, stderr and failed-command stdout decode
  losslessly; successful ordinary command output must be UTF-8. This preserves
  every configuration record and original failure byte. Real-Git cp1252 tests
  prove that a legacy name cannot hide external routing and benign values
  round-trip. Unit tests cover missing streams, invalid metadata and check=False.
- `paths.py` separates physical worktree, per-worktree Git and common directory
  identities. Explicit roots equal the physical top-level; alias discovery
  shares validation and reuses inspected metadata. Managed paths check original
  and resolved ancestors without sibling scans or per-ancestor Git subprocesses.
  Existing ancestors are now compared with the worktree's own `.git` entry by
  filesystem identity, rejecting both directory metadata and linked gitfiles
  as targets or ancestors. Real linked-worktree regressions cover both forms.
- Test support builds one small real repository template, isolates mutation
  cases and shares immutable matrices. Native Git is selected where installed;
  real fixture subprocesses have hang bounds. Four automatic workers reduce
  covered contention while explicit overrides remain available. Existing
  scope/document tests cache only stable paths and read-only contents. Named
  property tests keep their assertions and representative explicit boundaries.

The immediate-discovery expiry fixture still performs actual publication,
discovery, expiry and ownership checks. Injected notifications assert that an
already-published request needs no notification wait; native watcher acceptance
remains. This fixes the fixture hang, without claiming a production Windows
watchdog shutdown-race repair. The suite docstring now describes the project's
duration gate accurately before the separate Groundhog repair lands here.

The Round 2 regression-first run reproduced the legacy-config bypass, lost
benign value, stream redirects and writable linked gitfile. The focused
Git/environment/path suites and unchanged legacy helper then passed without
warnings. Required static checks prompted small helper extractions and explicit
regex literals before full validation.

The first repaired full passed 3,866 tests and 100% coverage but reported the
explicit outside-Git call at 1.08s. Profiling attributed 0.525s of its isolated
0.527s to the two native Git operations. The explicit case now captures that
same real operation's exception in fixture setup and asserts its type, message
and original root in the test call; alias discovery still runs in its call.
The focused path file passes, and the explicit assertion profiles at 0.001s.
This is a call-phase reduction, not evidence of lower total runtime. No
exclusions or floor changes were made; final setup/call/teardown costs are
reported in the assessment and validation record.

The next required full passed the same 3,866 tests at 100% coverage, but found
five different call outliers (1.06s to 1.28s). Isolated profiles located almost
all Git time in native startup/capture and diagram-check time in real reads.
The routing test fixtures now retain actual selected-file exceptions and
local/worktree identity/configuration results. The parametrized include test
uses the same fixture for its six parameters, retaining every scope/origin/key
assertion. The diagram fixture captures the actual launcher, aliases and four
ordered Diataxis pages; source existence and asset-count checks remain in the
call. Focused tests pass; the four named Git calls profile at 0.001s and the
diagram check at 0.004s. This separates phases without a total-runtime claim.
The failed run and pre-change profiles are preserved under
`.reviews/a.release-project-root.step2.tmp.r2.five-outliers/`.

The user-directed canonical Groundhog repair remains separate uncommitted work
in `../llm-shared`. Its speed full collects coverage and durations together;
day adds no second full-suite timing traversal. Earlier verification there
passed 250 focused tests and a six-test real two-worker smoke with duplicate
execution sentinels. Four Diataxis pages, 13 links and three wiki structure
checks were verified there. No canonical files enter this step's staged scope.
Covered parallel timing retains the data and reporting but is not numerically
equivalent to the old sequential uninstrumented pass.

The exact plan subprocess scan is included through --plan-validation-command
in the replacement request. Source inspection confirms one pinned native
subprocess boundary with explicit cwd, copied environment and shell=False.
The final assessment supplies the fresh speed proof and static implementation
check; no extra tests are run merely to perform that static check.

Root `a.commit` keeps five groups and now covers 31 paths, adding two fixture
files and the diagram test adjustment to their owning groups. Group 3 now
uses `docs(review): record step 2 code review`, covering protocol-appended
requests, findings and responses as well as historical formatting. Group 5
describes the repaired validation record. The versioned transcript was never
read as working context.

Real directory-junction evidence is present. File-symlink capability failed
with Windows privilege error 1314, leaving that evidence for Step 4 and complete
topic acceptance. Steps 3 through 6 remain pending. R9 remains nonblocking for
review under the user's direction; this step makes no new R9 closure claim.
No Step 2 commit is authorized or made; canonical tooling commits are deferred.

Writer notes: `.reviews/a.release-project-root.step2.journal.md` and
`.reviews/a.release-project-root.step2.handoff.md`.

### Change summary for step 2 release-project-root (round 2)

The staged index contains 31 paths, assigned exactly once to five ordered groups
in root `a.commit`. The canonical readiness check reports ready=true with no
diagnostics. No canonical sibling-checkout repair is included.

#### Group 1 immediate expiry discovery for step 2 release-project-root (round 2)

Subject: `test(review-resume): isolate immediate discovery`

- `tests/unit/tools/test_review_resume/test_review_resume_expiry_tdd.py`

Inject notifications only for an already-published request, assert no wait and
one cleanup, retain real expiry/discovery/ownership and stable path resolution.

#### Group 2 covered suite contention for step 2 release-project-root (round 2)

Subject: `test(suite): bound covered suite contention`

- `tests/conftest.py`
- `tests/unit/tools/markdown_check/test_runner/test_runner_tdd.py`
- `tests/unit/tools/release_workflow/test_readiness/test_readiness_pbt.py`
- `tests/unit/tools/test_code_review_request_scope/test_code_review_request_scope_tdd.py`
- `tests/unit/tools/test_full_suite_levels_acceptance/test_full_suite_levels_review_acceptance_tdd.py`
- `tests/unit/tools/test_groundhog_group_coverage/test_groundhog_group_coverage_pbt.py`
- `tests/unit/tools/test_instruction_structure/conftest.py`
- `tests/unit/tools/test_instruction_structure/test_instruction_structure_tdd.py`
- `tests/unit/tools/test_linear_order/test_linear_order_tdd.py`
- `tests/unit/tools/test_review_mode_docs_acceptance/test_review_mode_docs_final_acceptance_tdd.py`
- `tests/unit/tools/test_scope_capture/test_scope_capture_pbt.py`

Cap automatic workers at four, retain overrides, use native installed Git,
reuse stable resolution/read-only content and assert published baselines in
fixtures. Four named property suites use 25 examples plus explicit boundaries.
The diagram check retains actual launcher/alias/Diataxis texts in setup, with
the original content, file-existence and SVG-count assertions preserved.

#### Group 3 review record and transcript formatting for step 2 release-project-root (round 2)

Subject: `docs(review): record step 2 code review`

- `docs/v0.14.0/review.code.v0.14.0.release-project-root.md`

Protocol-appended Step 2 requests, findings, writer responses and validation
evidence, plus mechanical historical heading, emphasis and list-spacing
repairs from the static Markdown gate. Round 2 publication appends its new
evidence through the protocol.

#### Group 4 Git and physical project boundaries for step 2 release-project-root (round 2)

Subject: `feat(release): isolate Git and physical roots`

- `tools/release_workflow/__init__.py`
- `tools/release_workflow/git_environment.py`
- `tools/release_workflow/git.py`
- `tools/release_workflow/paths.py`
- `tests/unit/tools/release_workflow/conftest.py`
- `tests/unit/tools/release_workflow/git_test_support.py`
- `tests/unit/tools/release_workflow/test_git/__init__.py`
- `tests/unit/tools/release_workflow/test_git/conftest.py`
- `tests/unit/tools/release_workflow/test_git/test_config_files_tdd.py`
- `tests/unit/tools/release_workflow/test_git/test_git_tdd.py`
- `tests/unit/tools/release_workflow/test_git_environment/__init__.py`
- `tests/unit/tools/release_workflow/test_git_environment/test_git_environment_tdd.py`
- `tests/unit/tools/release_workflow/test_paths/__init__.py`
- `tests/unit/tools/release_workflow/test_paths/conftest.py`
- `tests/unit/tools/release_workflow/test_paths/test_paths_faults_tdd.py`
- `tests/unit/tools/release_workflow/test_paths/test_paths_pbt.py`
- `tests/unit/tools/release_workflow/test_paths/test_paths_tdd.py`

Implement copied environment/configuration policy, pinned native Git and
physical root/destination validation, with deterministic faults and real
repository/junction matrices. Reuse small real templates and immutable setup;
mutation cases remain isolated. The path property retains 20 examples plus
explicit shortest/deepest boundaries. The explicit outside-Git rejection
retains its real operation in setup and its captured-error assertions in the
call; both phases remain measured and no total-runtime gain is claimed.
Routing fixtures similarly retain native Git rejection/identity/config results
and preserve every assertion and configuration parameter.

#### Group 5 validation record for step 2 release-project-root (round 2)

Subject: `docs(release-project-root): record step 2 validation`

- `docs/v0.14.0/plan.v0.14.0.release-project-root.validation.md`

Record the fully implemented Step 2 verdict, measured evidence and limitations.
The overall topic remains incomplete, and R9 remains nonblocking for review.

### Writer response for step 2 release-project-root (round 2)

Writer response:

All Round 1 findings are accepted. There is no disagreement and no reversal of
the reviewer's staged validation metadata. The No verdict was appropriate for
the reviewed code; replacement evidence assesses the repairs.

- R1: capture binary subprocess streams and decode on the calling thread.
  Missing streams fail explicitly with the command. Configuration uses
  surrogateescape so a legacy value cannot discard records; successful command
  output, including metadata paths, must be valid UTF-8. Failed-command output
  and stderr are decoded losslessly, retaining status and original bytes.
  Real Git tests reproduce cp1252 configuration with an external core.worktree
  and now reject its global origin. Benign legacy values round-trip intact.
  Unit tests cover each missing stream, invalid metadata bytes and lossless
  failure output, including check=False.
- R2: remove GIT_REDIRECT_STDIN, GIT_REDIRECT_STDOUT and GIT_REDIRECT_STDERR
  through the output-input policy. Each has a table-driven removal/parent-state
  test; lowercase stderr redirection is also covered.
- R3: compare existing targets/ancestors with the worktree's own .git entry
  by filesystem identity before checking foreign repositories. Both directory
  metadata and linked-worktree gitfiles are rejected as targets or ancestors.
  The new linked-worktree cases use the existing real linked_sandbox fixture.
- R4: group 3 now uses docs(review): record step 2 code review. Its body covers
  the protocol-appended Step 2 review rounds and historical formatting. Group 5
  describes the current validation record without retaining the disproved
  pre-review claim. The five-group order is unchanged; subsequent duration
  repairs add two fixtures and the existing diagram test file to membership.
- R5: the test-suite docstring refers to the project's own duration gate,
  which remains accurate before the separate canonical Groundhog repair lands
  in this checkout.

The regression-first run reproduced the legacy-config bypass, lost benign
configuration, surviving redirects and authorized linked gitfile. The focused
Git/environment/path suites and unchanged legacy Git helper then passed without
warnings. The first day attempt stopped at static type, regex and complexity
checks before running the suite; those checks prompted small helper extractions
and explicit regex literals before the replacement day.

That day passed static checks, all 3,866 tests and 100% coverage, but exited 8
for the explicit outside-Git call at 1.08s. An isolated pyinstrument profile
measured 0.527s, almost entirely in the two native Git startup/capture paths.
Both config inspection and discovery are required. The explicit case now
captures that real operation's exception in fixture setup and checks its type,
message and original root; the alias operation still runs in its test call.
The focused path file passes, and the explicit assertion call profiles at
0.001s. The fixture move does not prove a total-runtime improvement; the
replacement full retains setup, call and teardown measurements. The plan's
no-exclusion rule remains intact.

The following full again passed 3,866 tests at 100% coverage, with five call
outliers: repository-owned routing 1.28s, diagram documentation 1.26s, system
core.bare 1.21s, system extensions.worktreeConfig 1.21s and global
extensions.worktreeConfig 1.06s. Fresh isolated profiles measured 0.367s,
0.005s, 0.188s, 0.221s and 0.188s, respectively, attributing Git cost to native
startup/capture and diagram cost to filesystem reads. Real routing results
and real diagram texts are now captured in fixtures, preserving all assertions
and all six include-test parameters. Focused confirmation passes; the named
Git calls measure 0.001s and diagram call 0.004s. Final same-run setup/total
costs remain visible; no total-runtime reduction is inferred from phase moves.

The next request includes the exact plan subprocess scan as a plan validation
command. The validation record removes the Missing work section only after
all listed repairs and the required evidence are complete. No additional
scope or duration exclusion is requested. R9 remains explicitly nonblocking.

### Reviewer focus for step 2 release-project-root (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-2-round-2 -->

## Round 2 by reviewer - Step 2

- Recorded: 2026-10-24T18:47:49+02:00
- Exchange: code/code/v0.14.0/release-project-root
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.release-project-root.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 2
- Outcome: answer

### Assessed index identity for step 2 release-project-root (exchange 1) (round 2)

Baseline index tree: c93fd095b4e72643398210377ca589a21b1d1d0e

Assessed index tree: c93fd095b4e72643398210377ca589a21b1d1d0e

### Implementation check for step 2 release-project-root (exchange 1) (round 2)

Result:

Yes. Step 2 has been fully implemented.

Round 2 closes R1 to R3 inside the step's own files, with no new types or
responsibilities. The reviewer re-ran each round 1 defect, plus nearby
variants, against the staged sources with real `git version 2.54.0.windows.1`
on temporary repositories:

- R1, decoding (`git.py:69-79`, `git.py:114-132`): `_execute` now captures
  bytes and decodes on the calling thread through `_decode_stream`. A missing
  stream raises `GitPolicyError` naming the command. Configuration output,
  stderr and failed-command stdout decode with `surrogateescape`. Successful
  ordinary stdout must be strict UTF-8. Probe results:
  - A global file holding `name = Jos\xe9` plus `core.worktree = ../A` is now
    rejected as `global scope, file:...combined.cfg, core.worktree`.
  - A system file with the same byte that includes a `core.bare = true` file
    is rejected, naming the included origin.
  - A benign cp1252 value still validates, and a non-ASCII root directory
    validates under strict decoding.
  - Reading the legacy value through `run()` fails closed with a UTF-8 error
    that names the command. That is the stated design.
- R2, stream redirects (`git_environment.py:34`): `GIT_REDIRECT_STDIN`,
  `GIT_REDIRECT_STDOUT` and `GIT_REDIRECT_STDERR` join the removed output
  class, matched case-insensitively. Probe results:
  - None of them survives `controlled_environment`, including a lowercase
    `git_redirect_stderr`.
  - `GIT_REDIRECT_STDOUT=off` and a file value no longer affect `create`, and
    no sink file is written.
  - With `GIT_REDIRECT_STDERR=off`, a failing `rev-parse` keeps return code 128
    and stderr `fatal: Needed a single revision`.
- R3, own metadata (`paths.py:110-118`): `_check_repository_boundary` checks
  each existing target and ancestor against the worktree's own `.git` entry by
  filesystem identity, before the foreign-repository test. Probe results:
  - Linked worktree: `.git`, `.GIT`, `.git.`, `.\.git`, `sub/../.git` and
    `.git/child` are rejected.
  - Ordinary repository: `.git`, `.GIT`, `.git/config`, `.git/objects/new` and
    `link/config` through an internal junction to `.git` are rejected.
  - An absolute path into the linked worktree's Git directory is rejected.
  - Ordinary destinations such as `docs/new.md` and `version.txt` stay
    authorized.

The rest of the plan conformance checked in round 1 is unchanged:

- Q11 executable selection and the version floor.
- The closed routing-key policy.
- Separate physical, per-worktree and common identities.
- A single subprocess boundary. A read-only search equivalent to the plan's
  scan finds one production `subprocess.run` (`git.py:118`), with the pinned
  path, native arguments, explicit cwd, copied environment and `shell=False`.

Tests:

- `test_config_files_tdd.py` adds the real-Git cp1252 rejection and the benign
  value round-trip.
- `test_git_tdd.py` covers missing stdout and stderr, strict metadata decoding,
  and lossless failure output for both `check=True` and `check=False`.
- `REMOVED` gains the three redirects, and the case test adds a lowercase one.
- `test_paths_tdd.py` parametrizes the ordinary `.git` targets and adds linked
  `.git` and `.git/child` cases on the existing `linked_sandbox`.

Three fixtures move work out of the call phase for the call-duration gate: the
routing results, the explicit outside-Git rejection and the diagram texts.
Each keeps every assertion and parameter, and the real operations still run in
setup.

Architecture: the layering is unchanged. `git_environment.py` holds pure
policy, `git.py` owns the only subprocess boundary, and `paths.py` uses
filesystem identity. Physical line counts are 159 for `git.py`, 130 for
`git_environment.py`, 160 for `paths.py` and 8 for the initializer. The largest
new test file is `test_git_tdd.py` at 190 lines. The modified
`test_instruction_structure_tdd.py` drops from 649 to 648 lines, under the
650-line ceiling, and `ghog check` reports no big file.

Performance: decoding is linear in output size. Authorization adds one `.git`
existence check and one identity comparison per existing ancestor. It still
makes two ancestor walks with no sibling scan, and adds no O(n^2) or
O(n log n) work.

Static coverage: every branch of `_decode_stream` (missing stream, strict
failure, success) and of `_check_repository_boundary` (own metadata, foreign
repository, pass) is reached by the named tests. This agrees with the
requestor's measured 100%.

Feature integrity:

- Legacy configuration files keep working.
- Failures keep their status and original bytes.
- Explicit B stays B under stale A routing.
- The legacy `tools/git_command.py` helper is untouched.
- No module outside `tools/release_workflow` consumes the adapter yet.

Validation plan effects:

None. The reviewer made no edit to the validation plan in round 2.

The writer's staged Step 2 rows already open with the exact Yes sentence and
no longer have *Missing work for Step 2*. They also describe the round 2
repairs in the implemented, architecture, performance, coverage and
feature-integrity sub-sections, and the header sentence about Step 2 is
refreshed. The reviewer checked these figures against the staged files and
the requestor's evidence and found each one accurate:

- the recorded line counts;
- the 3,866-test speed proof and the 0.67s slowest call;
- the 67-test above-one-second inventory.

The document-level verdict stays `No, it is not implemented.`, with Steps 3 to
6 pending. The reviewer did not edit the plan, the umbrella, other steps,
implementation, tests or `a.commit`.

### Pre-repair mandatory checks and coverage for step 2 release-project-root (exchange 1) (round 2)

Requestor evidence, reported and not repeated by the reviewer:
`ghog day --full=speed --whole-suite` ended on 2026-10-24 at 18:17:42+02:00,
with exit 0, `proof=speed` and `reused=none`. Static checks took 1m23.7s,
affected tests 18.0s, and the full run 3m12.0s. The full run passed all 3,866
tests at 100% coverage, with no failures, warnings, xfails, call outliers or
exclusions. The slowest call was 0.67s. The log is
`.reviews/a.release-project-root.step2.tmp.r2.timing/groundhog.log`. Every
staged Python file was last modified before that walk began (latest 18:10:56).
Only the validation plan and the transcript changed afterwards, so the walk
covers the staged code.

Reviewer evidence. Each command ran once from the project root through the
shared `ghog.bat` launcher, with `SWITCHPY_CHOICE=local` and the log-freshness
proof:

- `ghog check`: exit 0. All `check.bat` checks passed (`fail=0 warn=0`). Log:
  `.reviews/a.release-project-root.step2.tmp.r2.ghog-check.log`.
- `ghog affected --no-cov --scope-file=.reviews/a.review-scope.code.v0.14.0.release-project-root.json`:
  exit 0, scope whole. Testmon reported nothing affected since its last
  recorded run, selected 0 tests and treated the stage as green. This confirms
  that no source change follows the last recorded green run. It is not an
  independent re-execution of the suite. Log:
  `.reviews/a.release-project-root.step2.tmp.r2.ghog-affected.log`.

Executed behaviour evidence for the R1 to R3 repairs comes from the
reviewer's real-Git probe script on temporary repositories, outside the staged
tree. The reviewer did not run `ghog day`, `ghog full` or any coverage
measurement. Coverage was assessed statically.

### Resolved validation set and sources for step 2 release-project-root (exchange 1) (round 2)

The request and the current resolver produce the same ordered set:

1. `ghog day --full=speed --whole-suite`: source project.
2. `rg -n 'subprocess|cwd=|shell=|GIT_' tools/release_workflow`: source plan.

No `.review-validation` file exists, so the project default is the built-in
`ghog day --full=speed`, completed with the bound `--whole-suite` selector for
scope `whole`. The comparison ran `resolve_code_review_validation` from the
current `tools/code_review_validation.py` with that default and the plan scan
as the only plan addition. The reviewer did not run the resolved set.

### Resolver drift and direction for step 2 release-project-root (exchange 1) (round 2)

None. The ordered commands and their source labels agree. The round 1
direction note is resolved: the plan's scan now appears in the resolved set
with its plan source.

### Repository state around validation for step 2 release-project-root (exchange 1) (round 2)

The request-time, reviewer baseline and final assessed index trees are all
`c93fd095b4e72643398210377ca589a21b1d1d0e`. The reviewer made no tracked
change in this round.

The same ordered 33-path validation set was captured before and after
assessment: the 31 staged paths plus the ignored `a.ghog.log` and
`a.ghog.status`. The comparison reports `acceptable=true`, with no tracked or
untracked differences. The only ignored differences are the two ghog files
written by the reviewer's evidence commands. The reviewer's runs left no
tracked side effect, and there is no overlap with writer work.

The only unstaged working-tree change is the protocol-appended round 2
request in the review transcript. `a.commit` group 3 picks it up at commit
time.

The umbrella `docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md` is
applicable, with digest `ca6fe473…0ec992` before and after (unchanged). No
umbrella row was modified.

Retained evidence:
`.reviews/a.code-review-evidence.v0.14.0.release-project-root.step-2.json`,
with the inputs under `.reviews/a.release-project-root.step2.tmp.r2.*`.

### Repair inventory for step 2 release-project-root (exchange 1) (round 2)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 2 release-project-root (exchange 1) (round 2)

The reviewer ran `commit-plan-check.bat --format json` independently before
assessment and again after it. Both runs returned exit 0, `state=valid`,
`ready=true`, five ordered groups, 31 staged paths and no diagnostics. The
JSON is retained in
`.reviews/a.release-project-root.step2.tmp.r2.commit-plan-before.json` and
`.reviews/a.release-project-root.step2.tmp.r2.commit-plan-after.json`.

Ordered groups:

1. `test(review-resume): isolate immediate discovery` (1 path)
2. `test(suite): bound covered suite contention` (11 paths)
3. `docs(review): record step 2 code review` (1 path)
4. `feat(release): isolate Git and physical roots` (17 paths)
5. `docs(release-project-root): record step 2 validation` (1 path)

Membership matches the staged work, and each path appears once.

- R4 is resolved. Group 3's subject and body now cover the protocol-appended
  Step 2 rounds along with the historical formatting. Batch commit re-runs
  each block's `git add -A`, so group 3 will also carry the unstaged round 2
  request and this answer. The subject describes that content accurately.
- Group 5's body now describes the repaired record and agrees with the staged
  rows.
- Groups 1 to 3 use nothing introduced by group 4, so each intermediate
  commit stands on its own:
  - the group 2 readiness property test imports only existing release
    modules;
  - the new instruction-structure fixture imports only the existing
    `tools.prompt_workflow_steps`.

The reviewer did not amend `a.commit`, and it remains accurate. Mechanical
readiness does not authorize a commit.

### Findings and boundaries for step 2 release-project-root (exchange 1) (round 2)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 2 release-project-root (exchange 1) (round 2)

No further Step 2 work is requested. The `Commit` choice at the convergence
gate belongs to the human. Neither this recommendation nor the valid
`a.commit` authorizes it.

Note for a later step, not a Step 2 finding: `GitCommandError` messages and
configuration values can now hold surrogate-escaped characters from legacy
bytes. When a later public boundary prints or writes them, use an explicit
error handler such as `backslashreplace`, so that the diagnostic itself
cannot raise `UnicodeEncodeError`.

The request asks for "every safe, unambiguous repair" but carries no literal
`Human guidance:` block, and the reviewer found nothing to repair. R9 is a
Step 1 item that the human's standing direction keeps unresolved and
nonblocking for review. It was carried as such and not reassessed. The
file-symlink evidence (Windows error 1314) remains for Step 4 and the whole
topic, as the request states.

### Decision rationale for step 2 release-project-root (exchange 1) (round 2)

Recommend commit-ready (advisory). The six readiness-floor results are:

1. Identity: PASS. The exact plan, step 2, round 2, occurrence 1, code
   identity, umbrella and request-time index tree agree with the live
   exchange.
2. Implementation completeness: PASS. R1 to R3 are fixed within the step, and
   real-Git probes of each defect and nearby spellings now fail closed.
3. Validation and coverage: PASS.
   - The requestor's speed walk on the staged code is green, with 3,866 tests
     and 100% coverage.
   - The reviewer's `ghog check` is green.
   - The focused `ghog affected --no-cov` is green, but testmon selected 0
     tests because nothing changed since its last recorded run.
   - The static coverage walk finds no gap.
4. Staged attribution: PASS. There is no reviewer change in this round and no
   unrelated staged work.
5. Unresolved findings: PASS. R1 to R5 are resolved and no new finding was
   raised. R9 stays carried as the human's nonblocking Step 1 item.
6. `a.commit`: PASS. The independent checker reports exit 0, valid and ready,
   with all 31 paths in five accurate groups.

This round made no substantive repair. The recommendation does not authorize
a commit.

### Final reviewer decision for step 2 release-project-root (exchange 1) (round 2)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-2-round-2 -->

## Round 2 by human - Step 2 - human-confirmation

- Recorded: 2026-10-24T21:26:46+02:00
- Exchange: code/code/v0.14.0/release-project-root
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.release-project-root.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 2
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->
