# Code review transcript for v0.13.0

- Exchange: code/code/v0.13.0/full_suite_levels
- Reviewed document: docs/v0.13.0/plan.v0.13.0.full_suite_levels.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor - Step 0

- Recorded: 2026-10-02T09:36:38+02:00
- Exchange: code/code/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/plan.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Implementation step: 0
- Outcome: request

### Review identity for step 0 full_suite_levels (round 1)

Umbrella draft: none
Implementation plan: docs/v0.13.0/plan.v0.13.0.full_suite_levels.md
Implementation step: 0
Review round: 1

### Code review evidence for step 0 full_suite_levels (round 1)

request_index_tree: 9ac8bb381cae84d955b141ddd1dc382396c962d8
resolved_validation_set:

- ghog day (sources: project, plan)
- rg -n 'xfail\(strict=True' tests/unit/tools/test_groundhog_levels_perf (sources: plan)
- rg -n 'timeout\(GATE_TIMEOUT_SECONDS\)' tests/unit/tools/test_groundhog_levels_perf (sources: plan)

commit_plan_result:

```text
state: valid
ready: true
group 1: test(groundhog): add leveled walk cost gates
group 1 path: tests/unit/tools/test_groundhog_levels_perf/__init__.py
group 1 path: tests/unit/tools/test_groundhog_levels_perf/test_groundhog_levels_perf_tdd.py
group 2: docs(full_suite_levels): record step 0 validation
group 2 path: docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md
staged path: docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md
staged path: tests/unit/tools/test_groundhog_levels_perf/__init__.py
staged path: tests/unit/tools/test_groundhog_levels_perf/test_groundhog_levels_perf_tdd.py
```

### Requestor assessment for step 0 full_suite_levels (round 1)

Step 0 is fully implemented. The validation plan records the exact Yes
verdict for Step 0; Steps 1 to 8 remain pending, so its document-level line
stays `No, it is not implemented.`. This round covers only the test-only cost
gates and their validation record; no production file changed.

The groundhog walk (`ghog day`, the Step 0 gate arguments) finished on
2026-10-02 at 09:26:28 +02:00 with `exit=0`. Ty, Pyright, Ruff, Radon,
Vulture, the 650-line big-file gate, the Markdown check, ShellCheck and the
EOF check passed. The affected phase reported `fail=0 warn=0 xfail=5`; the
full phase reported `fail=0 warn=0 xfail=5 cov=100` in 3m 37.1s, so the only
xfails of the suite are the five new gates. The first walk of the step stopped
at check.bat on a Pyright `reportUnusedFunction` for the private autouse
fixture; renaming it to the public `clear_ambient_selectors`, as the
repository names its other autouse fixtures, cleared it before the green walk.

The two plan completion patterns, `xfail\(strict=True` and
`timeout\(GATE_TIMEOUT_SECONDS\)`, each list five gates over
`tests/unit/tools/test_groundhog_levels_perf`. `rg` is not on the PowerShell
PATH of the writer's shell, so the same ripgrep patterns ran through the
harness search tool.

Coverage is configured for `tools` and omits `*/tests/*`, so both new files
sit outside the gate; every top-level helper of the gate file is referenced by
a gate and the autouse fixture applies to all five. Physical counts are 7 for
the package initializer and 265 for the gate file, against an advisory 190:
recorded as variance below the 550 band, not missing work. No new type, no
production import, and no `O(n^2)` or `O(n log n)` computation was added.

### Implementation report for step 0 full_suite_levels (round 1)

Added the `tests/unit/tools/test_groundhog_levels_perf` package: an
initializer with the plan's `Unit test package for tools/...` docstring and
`# eof`, and `test_groundhog_levels_perf_tdd.py` with five gates. Each gate
carries `@pytest.mark.timeout(GATE_TIMEOUT_SECONDS)` with
`GATE_TIMEOUT_SECONDS: Final = 5` and
`@pytest.mark.xfail(strict=True, reason="removed in Step <N>")`, drives
`cli.main` through `QueueSpawns` and `make_deps` on a `tmp_path` project
(`check.bat`, `pyproject.toml`, `src/mod.py`, `tests/test_mod.py`), and
asserts exit codes and spawned child commands.

Step 2 gates:

- `test_default_walk_spawns_no_full_run`: a green `ghog day` spawns exactly
  the check.bat child and one `--no-cov` affected child.
- `test_upgrade_spawns_only_the_full_run`: after a green default walk,
  `ghog day --full=cov` exits 0 with one child that carries `--cov-report`
  and neither `--cov-append` nor `--durations=0`, counted on the second
  invocation's own queue.
- `test_stronger_saved_proof_spawns_nothing`: after a green `--full=speed`
  walk on a sequential project, `ghog day --full=cov` exits 0 and spawns
  nothing. Asking for `cov` keeps the gate valid even if the speed walk's
  floor write moves the timing fingerprint, since a timing mismatch caps the
  saved proof at `cov`, which still meets the request.

Step 4 gates, on a project whose `.ghog-groups` declares `sentinel` with
`tests/sentinel/**` and `src/sentinel/**`, plus `src/sentinel/core.py`,
`tests/sentinel/test_core.py` and a `tests/sentinel/conftest.py` that is no
test file:

- `test_grouped_walk_passes_only_group_test_files`: `ghog day --full=pass
  --group=sentinel` exits 0, its first child is check.bat, and its two other
  children carry exactly `tests/sentinel/test_core.py` as `.py` positional
  paths; paths are compared after resolving against the root, so a relative
  or absolute spelling both qualify.
- `test_grouped_walk_walks_the_tree_once`: the same walk exits 0 with its two
  group children and one `pathlib.Path.rglob` call, counted through a
  `monkeypatch` wrapper that still walks for real. `--full=pass` keeps the
  gate off the group coverage data file.

Every gate fails today on an assertion, never on an error: `_run(argv, deps)`
returns argparse's `SystemExit(2)` code for the unknown `--full` or `--group`
option, every spawn queue holds the children the pre-change walk pops (a
default walk pops three, so the default-walk gate fails on its count), and an
autouse fixture deletes `GHOG_FULL` and `GHOG_GROUP` so an ambient selector
cannot change a gate. No PBT was added: the plan states fixed counting
contracts need none.

The validation plan's Step 0 section records the Yes verdict with evidence,
and its theme sentence now says Step 0 is checked and Steps 1 to 8 pending.

Writer notes: `.reviews/a.full_suite_levels.step0.journal.md` and
`.reviews/a.full_suite_levels.step0.handoff.md`.

### Change summary for step 0 full_suite_levels (round 1)

Three staged paths are covered by the mechanically valid root `a.commit`
(`commit-plan-check` reports `state: valid`, `ready: true`):

1. test(groundhog): add leveled walk cost gates
   - `tests/unit/tools/test_groundhog_levels_perf/__init__.py`
   - `tests/unit/tools/test_groundhog_levels_perf/test_groundhog_levels_perf_tdd.py`
2. docs(full_suite_levels): record step 0 validation
   - `docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md`

The gate package comes first; the completed validation record is the final
documentation group with the exact `record step 0 validation` title. No
production file, caller or unrelated file changed.

### Writer response for step 0 full_suite_levels (round 1)

Writer response:

This is the first implementation review round for Step 0. There is no earlier
code-review feedback to accept or dispute. The settled design and plan
decisions are implemented only to the extent assigned to Step 0: the gates
encode the contracts Steps 2 and 4 must meet, and no behavior is implemented
ahead of those steps.

### Reviewer focus for step 0 full_suite_levels (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-0-round-1 -->

### LLM nature completion for reviewer (exchange 1)

Recorded nature: `codex`

Completed artifacts:

- `.reviews/a.review-active.code.code.v0.13.0.full_suite_levels.md`
- `.reviews/a.review-requested.code.v0.13.0.full_suite_levels.md`

<!-- review-entry-id: llm-nature-completion-reviewer-exchange-1 -->

## Round 1 by reviewer - Step 0

- Recorded: 2026-10-02T09:44:22+02:00
- Exchange: code/code/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/plan.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 0
- Outcome: answer

### Assessed index identity for step 0 full_suite_levels (exchange 1) (round 1)

Baseline index tree: 9ac8bb381cae84d955b141ddd1dc382396c962d8

Assessed index tree: d94e77cac513534dce15621bc53e43fdee96c8a3

### Implementation check for step 0 full_suite_levels (exchange 1) (round 1)

Result:

Yes. Step 0 has been fully implemented.

The staged package implements all five planned contracts through cli.main, QueueSpawns and make_deps on temporary projects. The default gate requires exactly check.bat and affected --no-cov. The upgrade gate measures only the second invocation and requires one covered child without appended coverage or durations. The stronger-proof gate requires zero children when cov follows speed. The grouped gates require the sentinel test file on both test children and exactly one Path.rglob call, after successful execution.

All five gates carry the five-second timeout and strict xfail with the correct Step 2 or Step 4 owner. The SystemExit adapter makes unsupported selectors fail at exit-code assertions. The three-child fake queues cover the current walk; the default gate fails at the expected count. Fixtures clear both ambient selectors and restore patches. The 265-line test module and seven-line initializer remain below the repository ceiling.

No production class changed, no DDD-Hexagonal boundary changed, and no new production complexity or reporting behavior was introduced. The helpers are all referenced: _write through the project builders, the other helpers through the gates, and the autouse fixture through pytest. The coverage gate measures tools and omits tests, so the requestor's 100% is not a coverage claim for these new tests. Expected-failure gates intentionally stop at their first failing assertion until their owning step.

No blocking implementation, performance, coverage, or feature-integrity finding remains.

Validation plan effects:

Updated only Step 0 in docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md: recorded the independent assessment, corrected the temporary-project maximum from seven files to eight, and explicitly included the transitively used _write helper. The exact Yes sentence remains. Other steps and the document-level pending verdict remain unchanged. No umbrella applies.

### Pre-repair mandatory checks and coverage for step 0 full_suite_levels (exchange 1) (round 1)

Request-time tree matched the captured baseline 9ac8bb381cae84d955b141ddd1dc382396c962d8. The requestor records a green ghog day completed 2026-10-02 at 09:26:28 +02:00, with five expected failures in affected and full phases and tools coverage 100%. This is requestor evidence, not an independent rerun.

The reviewer inspected the staged diff, plan Step 0, validation record, coverage configuration, existing day walk, shared fake process support, and a.commit. No executed ghog evidence was necessary for this test-only assessment; neither the requestor validation set nor coverage was rerun.

### Resolved validation set and sources for step 0 full_suite_levels (exchange 1) (round 1)

The current resolver contract retains these commands and source labels:

- ghog day (sources: project, plan).
- rg -n 'xfail\(strict=True' tests/unit/tools/test_groundhog_levels_perf (source: plan).
- rg -n 'timeout\(GATE_TIMEOUT_SECONDS\)' tests/unit/tools/test_groundhog_levels_perf (source: plan).

.review-validation is absent, so the current project default remains ghog day. Step 0 supplies the same walk and two counting checks; the request adds none.

### Resolver drift and direction for step 0 full_suite_levels (exchange 1) (round 1)

No drift in commands, order, or source labels. The current default and Step 0 completion criteria match the request's resolved_validation_set. The reviewer did not execute that set.

### Repository state around validation for step 0 full_suite_levels (exchange 1) (round 1)

Baseline index: 9ac8bb381cae84d955b141ddd1dc382396c962d8.
Assessed index: d94e77cac513534dce15621bc53e43fdee96c8a3.

The umbrella comparison reports applicable=false and changed=false. The validation-state comparison reports acceptable=false because the validation plan and index changed. Inspection and the attributable patch explain both differences: only the permitted Step 0 validation metadata was edited and staged. Both test-file digests are unchanged; no untracked difference or tracked validation side effect was reported. This permitted metadata exception satisfies the reviewer boundary.

### Repair inventory for step 0 full_suite_levels (exchange 1) (round 1)

Repairs made:

- docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md: polishing-only review metadata; added independent assessment and corrected the file-count and helper-reference descriptions. The evidence launcher attributed the patch to the captured pre-repair blob, and only that patch was applied to the index. No implementation or test repair.

Paths staged:

- tests/unit/tools/test_groundhog_levels_perf/__init__.py
- tests/unit/tools/test_groundhog_levels_perf/test_groundhog_levels_perf_tdd.py
- docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md

### Commit plan assessment for step 0 full_suite_levels (exchange 1) (round 1)

The reviewer independently ran commit-plan-check.bat --format json against the received state: exit 0, state valid, ready true, diagnostics [].

1. test(groundhog): add leveled walk cost gates
   Paths: tests/unit/tools/test_groundhog_levels_perf/__init__.py and tests/unit/tools/test_groundhog_levels_perf/test_groundhog_levels_perf_tdd.py.
2. docs(full_suite_levels): record step 0 validation
   Path: docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md.

These are the exact three staged paths. Tests precede their validation record; subjects and scope are accurate. The reviewer metadata edit changes no membership, ordering, or grouping, so a.commit remains accurate and was not amended.

### Findings and boundaries for step 0 full_suite_levels (exchange 1) (round 1)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 0 full_suite_levels (exchange 1) (round 1)

The advisory review is complete. Present the commit-ready human gate using the existing requestor workflow; no commit is authorized by this recommendation. No rework is required.

### Decision rationale for step 0 full_suite_levels (exchange 1) (round 1)

Recommend commit-ready. All six readiness criteria pass: exact identity and request-time index; complete Step 0 implementation; requestor validation evidence and satisfactory static coverage assessment; attributable staged scope; no unresolved current or carried finding; and mechanically valid, accurate a.commit grouping.

No substantive code or test repair occurred. The only reviewer changes are permitted Step 0 validation metadata. The generic request scope asks for repairs, but there is no literal Human guidance block authorizing implementation repair, and none was performed. The commit choice remains with the human.

### Final reviewer decision for step 0 full_suite_levels (exchange 1) (round 1)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-0-round-1 -->

## Round 1 by human - Step 0 - human-confirmation

- Recorded: 2026-10-02T10:43:03+02:00
- Exchange: code/code/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/plan.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 0
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-1 -->
