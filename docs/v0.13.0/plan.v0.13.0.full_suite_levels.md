# v0.13.0 full_suite_levels implementation plan -- levels, proof and test groups

Teach groundhog three on-demand full-suite levels backed by saved proof, narrow
its runs to declared test groups, then carry each effort's scope through `pw`,
the review exchange and the workflow instructions, in nine ordered steps.

- **Levels and proof**: a `FullLevel` value resolved once in the CLI shapes the
  day walk, the full run, the verdicts, the restart lines and a key=value proof
  marker that allows noops and upgrades.
- **Test groups**: a versioned `.ghog-groups` declaration, a scope selector, a
  captured scope, group-scoped runs, a group coverage gate and per-scope
  markers.
- **Workflow scope**: an effort-scope reader, `pw scope`, scope lines in
  `pw progress`, the requestor's `speed` validation in the effort's scope, and
  a bound scope that travels with each published code-review round.
- **Instructions and acceptance**: the development, review, release and
  authoring instructions, the groundhog manual and specification, and an
  acceptance mapping of every design case.

> Markdown lint note: never leave a space immediately inside an inline code span
> (MD038); when a snippet starts or ends with a space, write that space as the
> literal token `[space]`, as in `` `[space]${x}` ``. End any line that would be
> only italic text with a period after the closing underscore (MD036).

## Plan goal for v0.13.0 full_suite_levels

Implement the settled [feature request](feature-request.v0.13.0.full_suite_levels.md)
and [design](design.v0.13.0.full_suite_levels.md), beside the
[canonical draft](draft.v0.13.0.full_suite_levels.md). Every effort document
stays in `docs/v0.13.0/`; this is a standalone effort without an umbrella, and
its requirement carries no `- Test group:` line, so its own walks run on the
whole suite.

- **Step 0 goal**: add time-bound, spawn-counting gates for the cost contracts
  of the new walk, marked `xfail` until their owning step lands.
- **Step 1 goal**: free `commands.py` from the 550-through-650 band and add the
  pure level, proof and marker models, without changing any behavior.
- **Step 2 goal**: wire levels and saved proof through the CLI, the day walk,
  the full run, the reports, the status file and the detached walk, and move
  every caller that needs a full-suite proof to an explicit level.
- **Step 3 goal**: add the group declaration, its matcher and resolver, the
  captured-scope model, and the read-only `ghog groups` and
  `ghog exclude --list` listings.
- **Step 4 goal**: add scope selection to the run commands, narrow the runs to
  the selected group, judge the group coverage gate and group durations, and
  keep one proof marker per scope.
- **Step 5 goal**: add the effort-scope reader, `pw scope`, and the `scope`
  line of `pw progress`.
- **Step 6 goal**: complete the requestor's default validation with the effort
  scope, render the scope evidence and notices, bind the captured scope to
  each published code-review round for its whole lifetime, and ship the
  minimum requestor and reviewer invocation instructions that make the
  required arguments usable at once.
- **Step 7 goal**: update the workflow instructions, templates, adapters and
  groundhog manuals, including the review-off `speed` pass.
- **Step 8 goal**: add the cross-component acceptance suite and map every
  design acceptance case to its test.

---

## Scope anchors for v0.13.0 full_suite_levels plan

This plan implements the design's four outcomes:

1. `ghog day` stops after the affected tests unless a level is selected, and
   every groundhog command that runs or repairs the suite resolves one level
   from `--full`, `GHOG_FULL`, or its command default.
2. Each level has its own full-run shape, verdict, closing instruction and
   restart line, and every walk reports its objective, its valid proof and
   what ran or was reused, in the report and in `ghog status`.
3. The workflow phases ask for the right level: development walks stay on the
   default, the requestor's default validation proves `speed` before each
   request, the review-less step proves `speed` before its commit menu, and
   the prepare-release gate proves `cov`.
4. A versioned `.ghog-groups` declaration and a scope selector narrow every
   leveled run, its coverage gate and its proof to one test group, and the
   workflow carries each effort's declared scope into every ghog command it
   owns, with prepare-release always on the whole suite.

The following are explicitly **in scope** for this plan:

- The level value, its resolution and errors, level-shaped runs and verdicts,
  the sequential timing step of a parallel `speed` walk, and level-aware
  success, noop and restart lines.
- The key=value proof marker, one per scope, its atomic write, the proof
  accumulation and cap, noop and upgrade, and the timing fingerprint.
- The closing-line and status-line evidence keys, and the detached walk's
  level and scope forwarding.
- The group declaration, matcher, membership, fingerprint, captured scope,
  `ghog groups`, `ghog exclude --list` and `--since`, scope selection, grouped
  runs, the group coverage gate, group durations and the failure baseline.
- `tools/effort_scope.py`, `pw scope`, the `scope` and `bound` lines of
  `pw progress`, the requestor default at `speed` in the effort scope, the
  migration notice, the declared-set group statement, `test_scope` evidence,
  the scope capture of `publish-request`, `paths.scope`, `bound_scope`, and the
  scope-change block of a replacement request.
- The instruction, template, adapter, manual and specification updates named
  by the design, and their contract and acceptance tests.

The following are explicitly **deferred** to v0.14.0 and beyond, as the design
states:

- A timing pass inside a direct `ghog full` call in a parallel project.
- A snapshot digest that covers non-Python files, or that is narrowed to one
  group's files.
- One timing floor per group, or any automatic whole-suite `speed` run that
  seeds the floor.
- Reviewer-side changes beyond the captured scope of `ghog affected --no-cov`.
- The transcript-heading defect of a second exchange on one document.

Rollout note: `README.md` and the `wiki/**` pages that mention `ghog day` are
left to the documentation audit that prepare-release already runs through the
`review-and-update-project-docs` skill; `DEVELOPMENT.md`, whose alias list
describes the walk, is updated in Step 7.

---

## Complexity Bound Clarification for v0.13.0

The scaling target for all v0.13.0 code paths is:

- **O(1) amortized per hot-loop event**: each streamed pytest line is still
  parsed once; each project file is matched once against a group's compiled
  pattern list (a fixed, small number of patterns); each capture entry is
  checked for existence once.
- **O(n) total per phase**: one walk of the project's Python files per
  invocation serves both the source digest and the group membership; the
  fingerprints hash the already sorted file lists once; the group coverage
  analysis reads one data file and visits each resolved source once; the
  exclusion listing reads one floor file.

No v0.13.0 code path introduces an `O(n^2)` or a new `O(n log n)` cost on the
response path. The only sort is the one the digest walk already performs;
membership lists, fingerprints and the smallest folder set are derived from
that sorted list in a single pass. Any new path that breaks this bound is a
defect before merge.

---

## File-based IO cost clarification for v0.13.0 full_suite_levels

Every new decision is a small, bounded read placed beside a read groundhog
already pays for; nothing adds a scan, a cache or a second tree walk.

| Path | Reads | Writes | Bound |
| --- | --- | --- | --- |
| Noop or upgrade decision | the walk's own scope marker (five short lines), the floor file for the timing fingerprint, and the existing digest walk | none | one marker, never another scope's marker |
| Group resolution | `.ghog-groups` once, only when a group is selected, plus the pytest and coverage settings already read for the gate | none | membership reuses the digest's single file walk |
| Captured scope (`--scope-file`) | one JSON file and one existence check per listed file | none | never matches patterns, never reads `.ghog-groups` |
| Group coverage gate | one scope-owned data file through the coverage API | the scope-owned data file, by the pytest child | analysis over the resolved sources only |
| Proof marker, status line, capture copies | none | temporary file then atomic replace | one write per walk end |
| `ghog exclude --list` and `--since` | the floor file, and the saved listing for `--since` | none | strict, single read each |
| `pw scope`, `pw progress` scope line | the requirement's metadata lines up to its first heading; a named group adds one project walk | none | no draft read, no cache |
| Request rendering and `publish-request` | the coordination record and the bound capture of the same exchange | the caller's capture output; `paths.scope` | one coordination read per render |

A whole-suite run never reads `.ghog-groups`, so the default walk of an
ungrouped effort keeps today's IO: one digest walk and one marker read, the
marker now holding five short lines instead of one.

---

## Confirmed technical facts for v0.13.0 plan viability

These facts come from direct inspection of the tree at `5780ae9`. Physical
line counts use the metric of the repository big-file gate
(`sum(1 for _ in open(path))` over `tools` and `tests`); `senv.bat` sets
`PYTHON_BIG_FILE_LINE_LIMIT=650`, so 650 is the ceiling for every Python file,
new files included.

**Files over the 650-line repository limit**: none among the involved files.
`tools/review_status.py` sits exactly at 650; this plan does not touch it (the
bound scope reaches `pw progress` through the coordination record instead of
the status projection).

**Files in the 550-through-650 risk band** (avoid growth where practical):

| Path | Lines | Planned treatment |
| --- | --- | --- |
| `tools/groundhog/commands.py` | 637 | Step 1 extracts verdicts and progress; mandatory target at most 500 because creating headroom is the step goal. |
| `tools/code_review_request.py` | 597 | Step 6 first extracts its artifact-home file helpers; mandatory target at most 590 after the step, because the extraction is an explicit Step 6 goal. |
| `tools/review_exchange_models.py` | 562 | Step 6 adds one `ArtifactPaths` field and one `ArchiveKind` member only (about 4 lines). |
| `tools/review_exchange_store.py` | 599 | Not edited: the scope capture gets its own module. |
| `tests/unit/tools/test_instruction_structure/test_instruction_structure_tdd.py` | 649 | Not grown: new instruction contracts go to a new package. |
| `tests/unit/tools/test_review_exchange_cli/test_review_exchange_cli_tdd.py` | 643 | Not grown: new CLI cases go to the boundaries file or a new file. |
| `tests/unit/tools/test_prompt_workflow_main.py` | 614 | Not edited. |
| `tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py` | 597 | Step 2 changes literals; Step 6 adds the required `--scope-capture-output` argument to its calls (about 605); new Step 6 cases go to a new package. |

**Files below 550 and safe to extend** (baseline, involvement, advisory
estimate):

| Path | Lines | Steps and advisory end count |
| --- | --- | --- |
| `tools/prompt_workflow.py` | 540 | Step 5 dispatch, about 545 |
| `tools/review_exchange_cli.py` | 515 | Step 6, about 545 |
| `tools/groundhog/status.py` | 503 | Steps 2 and 4, about 560 (see split guidance) |
| `tools/prompt_workflow_progress.py` | 487 | Step 5, about 495 |
| `tools/review_exchange_human.py` | 480 | Step 6, about 490 |
| `tools/groundhog/reporting.py` | 454 | Step 2, about 475 |
| `tools/prepare_release/prepare_release_plan_workflow.py` | 434 | Steps 2 and 4, strings only |
| `tools/groundhog/cli.py` | 393 | Steps 2, 3 and 4, about 470 |
| `tools/review_exchange_publication.py` | 387 | Step 6, about 420 |
| `tools/groundhog/durations.py` | 368 | Step 4, about 395 |
| `tools/review_exchange_models_coordination.py` | 301 | Step 6, about 315 |
| `tools/review_artifact_registry.py` | 301 | Step 6, about 320 |
| `tools/groundhog/reporting_nextstep.py` | 297 | Steps 2 and 4, about 420 |
| `tools/groundhog/runner.py` | 254 | Steps 2 and 4, about 320 |
| `tools/review_exchange_models_envelope.py` | 231 | Step 6, about 250 |
| `tools/review_exchange_paths.py` | 229 | Step 6, about 232 |
| `tools/groundhog/snapshot.py` | 192 | Steps 1, 2 and 4, about 320 |
| `tools/review_exchange_cli_ownership.py` | 191 | Step 6 signature only |
| `tools/groundhog/exclusions.py` | 186 | Step 3, about 280 |
| `tools/prompt_workflow_parser.py` | 182 | Step 5, about 200 |
| `tools/review_exchange_cli_parser.py` | 159 | Step 6, about 170 |
| `tools/code_review_validation.py` | 153 | Steps 2 and 6, about 240 |
| `tools/groundhog/durations_summary.py` | 146 | Steps 2 and 4, about 200 |
| `tools/groundhog/day.py` | 135 | Steps 2 and 4, about 300 |
| `tools/groundhog/gate.py` | 120 | Step 3 helper move, about 100 |
| `tools/groundhog/context.py` | 96 | Steps 2 and 4, about 120 |
| `tools/groundhog/__init__.py` | 51 | Steps 1, 3 and 4, docstring only |

Existing tests below 550 that steps update: `test_groundhog_cli.py` 525,
`test_prompt_workflow_progress_tdd.py` 502, `test_prepare_release_plan_workflow.py`
488, `test_review_exchange_models_tdd.py` 487, `test_groundhog_acceptance.py`
429, `test_review_exchange_cli_boundaries_tdd.py` 419,
`test_groundhog_commands.py` 418, `test_review_exchange_paths_tdd.py` 414,
`test_groundhog_status.py` 410, `test_groundhog_detach.py` 377,
`test_groundhog_reporting.py` 307, `test_groundhog_runner.py` 305,
`test_groundhog_acceptance_day.py` 256, `test_code_reviewer_instruction_tdd.py`
241, `test_code_review_requestor_instruction_tdd.py` 232,
`test_groundhog_reporting_nextstep.py` 217, `test_groundhog_exclusions.py` 211,
`groundhog_acceptance_support.py` 208, `test_code_review_validation_tdd.py` 170,
`test_groundhog_snapshot.py` 163, `test_review_artifact_registry_tdd.py` 137,
`test_prompt_workflow_parser.py` 132, `test_implement_step_integration_tdd.py`
115, `test_implementation_check_reviewer_mode_tdd.py` 97,
`test_prepare_release_instruction_tdd.py` 93,
`test_review_requestor_instruction_tdd.py` 84,
`test_review_artifact_registry_pbt.py` 52.

**What does not exist yet (all new for v0.13.0)**:

- `tools/groundhog/verdicts.py`, `tools/groundhog/progress.py`,
  `tools/groundhog/levels.py`, `tools/groundhog/proof.py`,
  `tools/groundhog/evidence.py`, `tools/groundhog/group_patterns.py`,
  `tools/groundhog/groups.py`, `tools/groundhog/project_settings.py`,
  `tools/groundhog/listings.py`, `tools/groundhog/scope.py`,
  `tools/groundhog/group_coverage.py`.
- `tools/scope_capture.py`, `tools/effort_scope.py`,
  `tools/prompt_workflow_scope.py`, `tools/code_review_request_files.py`,
  `tools/code_review_request_scope.py`, `tools/review_exchange_scope.py`.
- No `.ghog-groups`, `GHOG_FULL`, `GHOG_GROUP`, `--full`, `--group`,
  `--whole-suite`, `--scope-file` or `--scope-capture-*` exists anywhere in
  code, launchers or tests.

**Other confirmed technical facts that affect plan shape**:

- **Runtime**: groundhog, `pw` and the review tools run in the llm-shared venv
  (Python 3.13.9) with coverage 7.14.0, pytest-cov 7.1.0, pytest-xdist 3.8.0,
  pytest-testmon 2.2.0, hypothesis 6.152.7 and pytest-timeout 2.4.0.
  `glob.translate` is available; no `pathspec` is installed. `--strict-markers`
  accepts `pytest.mark.timeout`, already used by
  `test_review_resume_perf` and `test_aggregate_perf_tdd.py`.
- **Process fakes take two arguments**: `Spawns`, `QueueSpawns` and the local
  `_FakeProcess` factories are `(command, cwd)` callables. The child
  environment of a grouped run (`COVERAGE_FILE`) is therefore applied around
  the spawn call in `runner.run_streaming`, not through a new factory
  parameter, so no existing fake changes.
- **Directly built invocations**: several tests build `Invocation` without the
  CLI. A `level` field defaulting to `None` (meaning "the command default") keeps
  their behavior: `full` stays at `speed`, every other command at `none`.
- **argparse exits 2 by `SystemExit`**: the Step 0 gates call `cli.main`
  through a helper that turns `SystemExit` into a returned code, so a gate
  fails on its assertion before its owning step, never by an error.
- **Test pins**: no test pins `implement-step.md` on `ghog day`; the requestor
  and reviewer instruction tests pin the phrases at lines 86, 99, 101 and 231;
  several request and acceptance tests pin the rendered default
  `ghog day (sources: project)`; `test_instruction_structure_tdd.py` requires
  exactly two `.\senv.bat &&` calls in `groundhog.md`; no test reads
  `step-journal.md`, `step-handoff.template.md` or `fix_slow_test.md`; no test
  pins the two prepare-release operation strings.
- **Default versus declared validation**: `load_project_validation_commands`
  returns the default without saying so; Step 6 adds a reader that reports
  whether the set was declared.
- **Review artifacts**: `ArtifactPaths` has a single constructor
  (`ReviewArtifactLocator.exchange_paths`); `publish_atomic` and
  `remove_exact` accept only the six fixed paths; `ArtifactKind` in
  `review_status_models.py` names those six. The scope capture is therefore a
  registered artifact name with its own writer and remover, outside
  `fixed_paths`.
- **`pw scope` arguments**: ghog arguments such as `--full=speed` need an
  `argparse.REMAINDER` positional on the `scope` subparser.
- **Draft metadata**: no code writes `- Type:` or `- Umbrella:`; the
  `- Test group:` line is written by the `process-draft` and
  `write-requirement` instructions, and read by `tools/effort_scope.py`.
- **Prepare-release adapters**: `.claude/skills/prepare-release/SKILL.md` and
  `.github/skills/prepare-release/SKILL.md` mention "run ghog day" and are
  updated with the canonical instruction.

---

## Current test-tree validation snapshot for v0.13.0 full_suite_levels

Existing test packages that v0.13.0 must not break:

- Groundhog flat files `tests/unit/tools/test_groundhog_*.py` (21 files, the
  largest `test_groundhog_cli.py` at 525) and `groundhog_acceptance_support.py`
  (208): their fakes stay valid; new groundhog cases go to new packages.
- `test_code_review_validation`, `test_code_review_request`,
  `test_code_review_request_commit_plan`, `test_code_review_requestor_acceptance`,
  `test_code_reviewer_acceptance`, `test_code_review_answer`: literal updates
  for the new project default (Step 2), and the required
  `--scope-capture-output` argument in every renderer CLI call (Step 6), also
  in `tests/acceptance/commit_plan_check`.
- `test_review_exchange_cli`, `test_review_exchange_lifecycle`,
  `test_review_exchange_paths`, `test_review_exchange_models`,
  `test_review_exchange_acceptance`, `test_review_artifact_home`: legacy
  records and requests without scope evidence keep passing.
- `test_prompt_workflow_progress`, `test_prompt_workflow_parser.py`,
  `test_prompt_workflow_main.py`, `test_prompt_workflow_skill`: unchanged
  routing; new `scope` behavior lives in its own package.
- `prepare_release/`: two operation strings change.
- Instruction tests: Step 6 updates the invocation-contract pins in
  `test_code_review_requestor_instruction`, `test_code_reviewer_instruction`,
  `test_implementation_check_reviewer_mode` and
  `test_review_requestor_instruction`. Step 7 updates the broader requestor
  policy pins; `test_instruction_structure` stays green without edits.
- `tests/acceptance/**`: no groundhog, `pw` or prepare-release case lives
  there; only `commit_plan_check/.../test_commit_plan_check_contracts_tdd.py`
  gains the renderer's required argument in Step 6.

New test leaf directories to create for v0.13.0 (each with an `__init__.py`
holding the `"""Unit test package for tools/<module>.py. ..."""` docstring and a
trailing `# eof`):

- `tests/unit/tools/test_groundhog_levels_perf/`
- `tests/unit/tools/test_groundhog_verdicts/`
- `tests/unit/tools/test_groundhog_levels/`
- `tests/unit/tools/test_groundhog_proof/`
- `tests/unit/tools/test_groundhog_snapshot_marker/`
- `tests/unit/tools/test_groundhog_acceptance_levels/`
- `tests/unit/tools/test_groundhog_group_patterns/`
- `tests/unit/tools/test_groundhog_groups/`
- `tests/unit/tools/test_scope_capture/`
- `tests/unit/tools/test_groundhog_listings/`
- `tests/unit/tools/test_groundhog_scope/`
- `tests/unit/tools/test_groundhog_group_coverage/`
- `tests/unit/tools/test_groundhog_acceptance_groups/`
- `tests/unit/tools/test_effort_scope/`
- `tests/unit/tools/test_prompt_workflow_scope/`
- `tests/unit/tools/test_code_review_request_scope/`
- `tests/unit/tools/test_review_exchange_scope/`
- `tests/unit/tools/test_full_suite_levels_instructions/`
- `tests/unit/tools/test_full_suite_levels_acceptance/`

`tests/__init__.py`, `tests/unit/__init__.py` and `tests/unit/tools/__init__.py`
already exist; new leaf packages need no registration there.

---

## Runtime file note for v0.13.0 full_suite_levels plan

Every runtime file below lives in the review artifact home (`.reviews`, whose
`.gitignore` is `*`), so none is ever committed:

- `a.ghog.day.ok` changes format (key=value proof marker); `a.ghog.day.<group>.ok`
  is new, one per group walked.
- `a.ghog.coverage.<group>`: the scope-owned coverage data file of a grouped
  covered run, set through `COVERAGE_FILE`.
- `a.ghog.day.scope.json`: the capture a detached grouped walk passes to its
  survivor.
- `a.review-scope.code.<version>.<slug>.json`: the core-owned `paths.scope`
  copy of a published round's capture.
- `a.<slug>.step<x>.tmp.scope-capture.json` and
  `a.<slug>.step<x>.tmp.exclusions.txt`: caller-owned step artifacts of the
  requestor and of the review-off pass, deleted by prepare-release.

`.ghog-groups` is a versioned project file at the root, written only by the
`process-draft` flow when a new group is created; llm-shared declares none in
this effort.

---

## Shared execution command checklist for all v0.13.0 full_suite_levels steps

Apply this checklist for every numbered step, filling in the step paths.

1. Count physical lines before editing every step file, tests and
   `__init__.py` files included, with the line-count command below. A missing
   file starts at 0.
2. Write or update the step's tests first, as its "Tests first" list says;
   assert observable outputs (exit codes, printed lines, spawned commands,
   files written) rather than private structure.
3. Implement the step, then run its `rg` inspection commands.
4. Run the shared gate walk below. Its affected phase is the step's targeted
   test run and its full phase covers every existing caller; use
   `ghog single <step test files>` and `ghog affected` only inside the failure
   branch the walk prescribes. Never call `check.bat` or `pytest` directly.
5. Fix what the walk names and walk again until it reports `exit=0`.
6. Count lines again. Any Python file above 650 stops the step: apply its
   split guidance before going on. A file above only its advisory estimate
   while at or below 650 is recorded as variance, not as missing work. A
   mandatory target stated by the step is enforced.
7. Record the actual evidence in the matching step of
   [the validation plan](plan.v0.13.0.full_suite_levels.validation.md) during
   the implementation check, and keep its step sections aligned if the plan
   review renumbers steps.

---

## Ready-to-run command templates for all v0.13.0 full_suite_levels steps

Read [run commands](../../rules/run_commands.md) and the
[groundhog loop](../../instructions/groundhog.md) before execution. Resolve
`<llm-shared>` as the absolute llm-shared checkout that holds those
instructions; never persist a machine path in this plan.

Line count before and after, from PowerShell at the project root:

```powershell
$stepPaths = @('tools/groundhog/commands.py') # Replace with every step file.
$stepPaths | ForEach-Object {
    $lineCount = if (Test-Path -LiteralPath $_) {
        @(Get-Content -LiteralPath $_).Count
    } else { 0 }
    '{0}: {1}' -f $_, $lineCount
}
```

Shared gate, one `ghog day` walk repeated fix-and-walk until it reports the
objective (`exit=0`): groundhog runs check.bat, the step's affected tests and
the full suite with its coverage gate, in order, stopping at the first
non-green step. This effort changes the walk itself, so its own gate names
the level and scope that keep today's llm-shared proof: the full suite with
its coverage gate, without the sequential timing pass that only `speed` adds
in a parallel project:

| Steps | `<gate-arguments>` | Why |
| --- | --- | --- |
| 0 and 1 | `day` | the walk is still the pre-change three-step walk |
| 2 and 3 | `day --full=cov` | Step 2 makes plain `ghog day` stop after the affected tests |
| 4 to 8 | `day --full=cov --whole-suite` | Step 4 adds the selector this ungrouped effort resolves to |

From Step 5 on, `pw scope day --full=cov` prints the same command for this
effort and may be used to produce it.

```powershell
$h = cmd /d /v:on /c "call <llm-shared>\bin\artifact_home.bat . && echo !ARTIFACT_HOME!"; $f = "$h\a.ghog.started"
ni $f -Force | Out-Null; $t = (gi $f).LastWriteTime
cmd /d /c "<llm-shared>\bin\ghog.bat <gate-arguments> > a.ghog.log 2>&1"; $code = $LASTEXITCODE
if (-not ((Test-Path a.ghog.log) -and (gi a.ghog.log).LastWriteTime -gt $t)) {
    "STALE: a.ghog.log was not refreshed - the walk did not run; fix the invocation before reading"
}
ri $f -Force; "exit=$code"
```

Branch on the exit code first, then read the last 5 log lines on exit 0 or
the last 100 otherwise. On a harness that kills long calls, use the detached
form (`ghog.bat <gate-arguments> --detach`, no redirect) and poll
`ghog status`. A step is complete only with a fresh `exit=0` after its last
edit.

- Line count before: the PowerShell block above.
- Targeted tests: inside the walk's affected phase; `ghog single <step test files>`
  only in the failure branch.
- Grep checks: the step's `rg` commands.
- Shared gate loop: the walk above with the step's `<gate-arguments>`.
- Line count after: the PowerShell block above.

---

## Shared timeout target policy for v0.13.0 full_suite_levels perf gates

- Step 0 adds deterministic cost gates in
  `tests/unit/tools/test_groundhog_levels_perf/test_groundhog_levels_perf_tdd.py`.
  Each gate carries `@pytest.mark.timeout(GATE_TIMEOUT_SECONDS)` with
  `GATE_TIMEOUT_SECONDS: Final = 5`, drives `cli.main` with
  `QueueSpawns`/`make_deps` on a `tmp_path` project, and asserts the spawned
  child commands, so the gate measures work avoided, not wall-clock jitter.
- Each gate is `@pytest.mark.xfail(strict=True, reason="removed in Step <N>")`
  until its owning step lands; the owning step deletes the `xfail` mark and
  keeps the timeout.

Gate-to-step ownership for v0.13.0:

- `test_default_walk_spawns_no_full_run` -> remove `xfail` in Step 2.
- `test_upgrade_spawns_only_the_full_run` -> remove `xfail` in Step 2.
- `test_stronger_saved_proof_spawns_nothing` -> remove `xfail` in Step 2.
- `test_grouped_walk_passes_only_group_test_files` -> remove `xfail` in Step 4.
- `test_grouped_walk_walks_the_tree_once` -> remove `xfail` in Step 4.

---

## Numbered steps for v0.13.0 full_suite_levels

### Step 0. Add the cost gates of the leveled walk

#### Step 0 -- analysis and intent for the level cost gates

Issues to address:

- The value of this effort is work not done: a default walk that never spawns
  the full run, an upgrade that reuses check and affected, a noop on stronger
  saved proof, and a grouped walk that runs only its files after one tree
  walk. Nothing guards these contracts today.

Fix intent:

- Add five strict `xfail` gates, each bounded by a timeout and asserting the
  spawned commands, owned by Steps 2 and 4.

Expected outcome:

- The gates xfail today and turn green, with their `xfail` removed, exactly
  in their owning step.

Step framing:

- Design link: "Noop and upgrade", "Level-Shaped Full Runs", "Narrowed
  collection", "Resolved group membership"; write-plans Step 0 policy.
- Execution checklist reference: "Shared execution command checklist for all
  v0.13.0 full_suite_levels steps".

#### Step 0 -- implementation for the level cost gates

**Files involved**:

- `tests/unit/tools/test_groundhog_levels_perf/__init__.py` (new, to be created).
- `tests/unit/tools/test_groundhog_levels_perf/test_groundhog_levels_perf_tdd.py` (new, to be created).

**Tests first**:

- `test_default_walk_spawns_no_full_run`: a green `ghog day` with
  `GHOG_FULL` absent spawns exactly two children (check.bat, affected
  `--no-cov`) and no third.
- `test_upgrade_spawns_only_the_full_run`: after a first green default walk,
  `ghog day --full=cov` on unchanged sources exits 0 after spawning one
  covered full child only (counted for the second invocation).
- `test_stronger_saved_proof_spawns_nothing`: after a green `--full=speed`
  walk on a sequential project, `ghog day --full=cov` exits 0 and spawns
  nothing.
- `test_grouped_walk_passes_only_group_test_files`: with a `.ghog-groups`
  `sentinel` group, `ghog day --full=pass --group=sentinel` exits 0 and
  passes exactly the group's test files as positional paths to the affected
  and full children.
- `test_grouped_walk_walks_the_tree_once`: the same grouped walk exits 0
  with its two group spawns and calls `pathlib.Path.rglob` exactly once
  (counted through `monkeypatch`), so the gate cannot pass on a refused
  command.
- A local `_run(argv, deps)` helper turns `SystemExit` into a return code; no
  PBT is needed for fixed counting contracts.

**Classes and behavior**:

- Test-only step. The gates use `tests.unit.tools.groundhog_acceptance_support`
  (`QueueSpawns`, `make_deps`, `passing_transcript`) and build their project in
  `tmp_path` (`check.bat`, `pyproject.toml`, `src/mod.py`, test files).

**Completion criteria**:

- The shared gate walk with `<gate-arguments>` = `day` reports `exit=0`, with
  the five gates reported as xfailed.
- `rg -n "xfail\(strict=True" tests/unit/tools/test_groundhog_levels_perf` lists five gates.
- `rg -n "timeout\(GATE_TIMEOUT_SECONDS\)" tests/unit/tools/test_groundhog_levels_perf` lists five gates.

#### Step 0 -- addendums for the level cost gates

Line-budget checkpoint:

- [ ] `tests/unit/tools/test_groundhog_levels_perf/test_groundhog_levels_perf_tdd.py`:
  before 0; below-550 safe; repository ceiling <= 650; expected about 190 (advisory).
- [ ] `tests/unit/tools/test_groundhog_levels_perf/__init__.py`: before 0;
  safe; ceiling <= 650; expected 7 (advisory).

Split guidance:

- None expected; split the grouped gates into
  `test_groundhog_levels_perf_groups_tdd.py` if the file nears 650.

Full workflow timing run readiness:

- The gates run inside the walk's affected and full phases; each is bounded
  by its five-second timeout.

Time-gated status for Step 0:

- Five gates added as strict `xfail`; owners are Steps 2 and 4.

---

### Step 1. Free commands.py and add the pure level, proof and marker models

#### Step 1 -- analysis and intent for the pure models

Issues to address:

- `tools/groundhog/commands.py` is at 637 lines, and Steps 2 and 4 add level
  shapes, earned proof and the group gate around its verdicts.
- The level order, the proof accumulation and cap, the noop and upgrade
  decision, and the key=value marker are rules worth testing alone, before
  any wiring.

Fix intent:

- Move the verdict classification and the progress sink out of
  `commands.py`, with no behavior change.
- Add the pure models the next steps wire: levels, proof rules, and the
  marker record with its strict reader and atomic writer.

Expected outcome:

- `commands.py` at most 500 lines; every existing test passes with updated
  references; the new modules are fully unit-tested and unused by the walk.

Step framing:

- Design link: "Level value and ordering", "Resolution rule", "Marker format
  and write", "Proof after a walk", "Noop and upgrade", "Exact-scope proof".
- Execution checklist reference: "Shared execution command checklist for all
  v0.13.0 full_suite_levels steps".

#### Step 1 -- implementation for the pure models

**Files involved**:

- `tools/groundhog/commands.py` (existing, to be updated).
- `tools/groundhog/verdicts.py` (new, to be created).
- `tools/groundhog/progress.py` (new, to be created).
- `tools/groundhog/levels.py` (new, to be created).
- `tools/groundhog/proof.py` (new, to be created).
- `tools/groundhog/snapshot.py` (existing, to be updated).
- `tools/groundhog/__init__.py` (existing, to be updated).
- `tests/unit/tools/test_groundhog_cli.py` (existing, to be updated).
- `tests/unit/tools/test_groundhog_commands.py` (existing, to be updated).
- `tests/unit/tools/test_groundhog_verdicts/__init__.py` (new, to be created).
- `tests/unit/tools/test_groundhog_verdicts/test_groundhog_verdicts_tdd.py` (new, to be created).
- `tests/unit/tools/test_groundhog_levels/__init__.py` (new, to be created).
- `tests/unit/tools/test_groundhog_levels/test_groundhog_levels_tdd.py` (new, to be created).
- `tests/unit/tools/test_groundhog_levels/test_groundhog_levels_pbt.py` (new, to be created).
- `tests/unit/tools/test_groundhog_proof/__init__.py` (new, to be created).
- `tests/unit/tools/test_groundhog_proof/test_groundhog_proof_tdd.py` (new, to be created).
- `tests/unit/tools/test_groundhog_proof/test_groundhog_proof_pbt.py` (new, to be created).
- `tests/unit/tools/test_groundhog_snapshot_marker/__init__.py` (new, to be created).
- `tests/unit/tools/test_groundhog_snapshot_marker/test_groundhog_snapshot_marker_tdd.py` (new, to be created).

**Tests first**:

- Verdicts: move the `classify`, `setup_reason` and coverage-measure cases of
  `test_groundhog_cli.py` into `test_groundhog_verdicts_tdd.py` unchanged, and
  repoint `postfix` and `_Progress` references in `test_groundhog_cli.py` and
  `test_groundhog_commands.py` to `progress`.
- Levels: precedence (`--full` over `GHOG_FULL` over the command default), a
  valid parameter overriding an invalid variable, `none` and unknown values
  rejected for both sources, an empty variable read as absent, `speed` default
  for `full` and `none` for the others, selector text never `--full=none`.
  PBT: any string outside `pass`, `cov`, `speed` raises `LevelError` from
  either source.
- Proof: every example of "Proof after a walk" (saved `pass` with a coverage
  gap keeps `pass`; saved `cov` with outliers keeps `cov`; a full failure caps
  to `none`; a timing-pass failure after a green full run caps to `none`;
  `--force` at `none` keeps saved `speed`; `--force --full=cov` with a gap
  gives `pass`); runs judging no gate keep the saved proof; noop when
  requested <= saved, upgrade when above, walk on a stale digest or `--force`;
  a timing mismatch caps saved proof at `cov`; `effective_saved` returns
  `None` on a scope, fingerprint or digest mismatch and `cov` for a saved
  `speed` marker whose timing differs; the direct `ghog full` earned proof
  table, including `proof=cov` for a green parallel `speed` run.
  PBT: the result never exceeds the highest input, is always below the lowest
  contradicted level, and noop holds exactly when requested <= saved.
- Marker: round trip of the five keys; any missing key, unknown value, extra
  junk line, undecodable or legacy one-line marker reads as no proof; the
  write goes through a temporary file and `replace`; `marker_path_for` names
  `a.ghog.day.ok` and `a.ghog.day.<group>.ok`; `timing_fingerprint` changes
  with line 2 or an exclusion entry and ignores line 1.

**Classes and behavior**:

- `tools/groundhog/verdicts.py`: `classify`, `_classify_no_tests`,
  `_classify_coverage`, `measures_coverage` (renamed from
  `_measures_coverage`) and `setup_reason`, moved verbatim; callers import
  them from here.
- `tools/groundhog/progress.py`: `Progress` (the former `_Progress`) and
  `postfix`, moved verbatim.
- `tools/groundhog/levels.py`: `FullLevel` (ordered `NONE < PASS < COV <
  SPEED`, with a `token`), `LevelSource` (`param`, `env`, `default`),
  `ResolvedLevel`, `ACCEPTED_LEVELS`, `GHOG_FULL_ENV = "GHOG_FULL"`,
  `LevelError(GroundhogError)`, `command_default(sub)`,
  `resolve_level(sub, param, environ)`, `effective_level(level, sub)`,
  `level_selector(level)` (empty at `NONE`), `proof_token(level | None)`
  (`unproven` for `None`).
- `tools/groundhog/proof.py`: `Gate` (check-or-affected, full tests,
  coverage, durations) with its lowest contradicted level,
  `accumulate(earned, saved, contradicted)`, `decide(saved, requested, *,
  digest_matches, timing_matches, force)` returning `NOOP`, `UPGRADE` or
  `WALK`, `cap_for_timing(saved, timing_matches)`,
  `effective_saved(marker, *, scope_key, fingerprint, digest, timing)` (the
  one rule that turns a marker into currently valid proof: `None` unless scope,
  fingerprint and digest all match, then capped at `cov` on a timing
  mismatch), and `earned_by_direct_full(level, exit_code, *, parallel)`.
- `tools/groundhog/snapshot.py`: `ProofMarker` (`scope`, `fingerprint`,
  `timing`, `digest`, `proof`), `read_proof_marker(path)`,
  `write_proof_marker(path, marker)` (temporary file then `replace`, failure
  logged), `remove_proof_marker(path)`, `marker_path_for(root, scope_key)`,
  public `source_files(root)` (the former `_source_files`),
  `source_digest(root, files=None)`, `timing_fingerprint(root)` over the
  active gate floor (`floor.read_floor` or the default) and the effective
  exclusion entries, and `WHOLE_SCOPE_FINGERPRINT`. `is_unchanged` and
  `write_marker` stay until Step 2 removes them.
- `tools/groundhog/__init__.py`: the package docstring names the new modules.

**Completion criteria**:

- The shared gate walk with `<gate-arguments>` = `day` reports `exit=0`.
- `rg -n "def classify|class _Progress|def postfix|def setup_reason" tools/groundhog/commands.py`
  returns nothing.
- `rg -n "from tools.groundhog import .*commands" tools/groundhog/levels.py tools/groundhog/proof.py tools/groundhog/verdicts.py`
  returns nothing (the new modules stay below `commands`).
- No behavior change: every existing groundhog acceptance test passes
  unedited.

#### Step 1 -- addendums for the pure models

Line-budget checkpoint:

- [ ] `tools/groundhog/commands.py`: before 637; 550-through-650 risk;
  repository ceiling <= 650; target <= 500 (mandatory only because freeing
  headroom for Steps 2 and 4 is this step's explicit goal).
- [ ] `tools/groundhog/verdicts.py`: before 0; safe; ceiling <= 650;
  expected about 120 (advisory).
- [ ] `tools/groundhog/progress.py`: before 0; safe; ceiling <= 650;
  expected about 120 (advisory).
- [ ] `tools/groundhog/levels.py`: before 0; safe; ceiling <= 650; expected
  about 170 (advisory).
- [ ] `tools/groundhog/proof.py`: before 0; safe; ceiling <= 650; expected
  about 200 (advisory).
- [ ] `tools/groundhog/snapshot.py`: before 192; safe; ceiling <= 650;
  expected about 310 (advisory).
- [ ] `tests/unit/tools/test_groundhog_cli.py`: before 525; safe; ceiling
  <= 650; expected about 470 after the move (advisory).
- [ ] `tests/unit/tools/test_groundhog_commands.py`: before 418; safe;
  ceiling <= 650; expected about 420 (advisory).
- [ ] New test files: before 0; safe; ceiling <= 650; expected verdicts 120,
  levels 160, levels PBT 70, proof 260, proof PBT 110, marker 200 (advisory).

Split guidance:

- If `commands.py` stays above 500, also move the report assembly
  (`_report`, `_report_run_context`, `_next_steps`, `_single_lines`) into
  `tools/groundhog/commands_report.py`, keeping `emit`, `emit_summary` and
  `emit_line` in `commands.py` for their many callers.
- If `snapshot.py` nears 550, move the marker record and its reader and writer
  into `tools/groundhog/proof_marker.py`.

Full workflow timing run readiness:

- Pure models and moved code only; the walk is the pre-change walk, so the
  gate is `day`.

Time-gated status for Step 1:

- No gate changes status; the five Step 0 gates stay `xfail`.

---

### Step 2. Run the walk and the full run by level, with saved proof

#### Step 2 -- analysis and intent for leveled walks

Issues to address:

- `run_day` always runs three steps; the CLI has no level; verdicts, restart
  lines and success lines assume one objective; the marker holds one digest;
  the closing and status lines carry no evidence; the detached walk drops any
  level.
- When plain `ghog day` stops running the full suite, the requestor's default
  validation, the prepare-release operations and the no-argument
  `ghog_cycle.bat` would silently lose their full-suite proof.

Fix intent:

- Wire `levels`, `proof` and the marker through the CLI, the day walk, the
  full run, the verdicts, the reports, the status file and the detached walk,
  in one switch so that no intermediate state mixes old and new markers.
- In the same step, move every caller that needs a full-suite proof to its
  explicit level: the requestor default to `ghog day --full=speed`, the two
  prepare-release operations to `ghog day --full=cov`, and the no-argument
  cycle to `day` alone.

Expected outcome:

- Every level row of the design's "Acceptance Cases" passes through
  `cli.main`; Step 0 gates for the default walk, the upgrade and the noop are
  green without `xfail`.

Step framing:

- Design link: "Level Model", "Level-Shaped Full Runs", "Snapshot Evidence",
  "Walk Reporting"; design decisions Q01 to Q08; "Default validation command"
  for the constant only.
- Execution checklist reference: "Shared execution command checklist for all
  v0.13.0 full_suite_levels steps".

#### Step 2 -- implementation for leveled walks

**Files involved**:

- `tools/groundhog/context.py` (existing, to be updated).
- `tools/groundhog/cli.py` (existing, to be updated).
- `tools/groundhog/runner.py` (existing, to be updated).
- `tools/groundhog/verdicts.py` (existing after Step 1, to be updated).
- `tools/groundhog/durations_summary.py` (existing, to be updated).
- `tools/groundhog/evidence.py` (new, to be created).
- `tools/groundhog/day.py` (existing, to be updated).
- `tools/groundhog/commands.py` (existing, to be updated).
- `tools/groundhog/reporting_nextstep.py` (existing, to be updated).
- `tools/groundhog/reporting.py` (existing, to be updated).
- `tools/groundhog/status.py` (existing, to be updated).
- `tools/groundhog/snapshot.py` (existing, to be updated).
- `tools/groundhog/__init__.py` (existing, to be updated).
- `tools/code_review_validation.py` (existing, to be updated).
- `tools/prepare_release/prepare_release_plan_workflow.py` (existing, to be updated).
- `bin/ghog_cycle.bat` (existing, to be updated).
- `tests/unit/tools/test_groundhog_levels_perf/test_groundhog_levels_perf_tdd.py` (existing after Step 0, to be updated).
- `tests/unit/tools/test_groundhog_acceptance_levels/__init__.py` (new, to be created).
- `tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_levels_tdd.py` (new, to be created).
- `tests/unit/tools/test_groundhog_acceptance_levels/test_groundhog_acceptance_proof_tdd.py` (new, to be created).
- `tests/unit/tools/test_groundhog_acceptance_day.py` (existing, to be updated).
- `tests/unit/tools/test_groundhog_runner.py` (existing, to be updated).
- `tests/unit/tools/test_groundhog_reporting.py` (existing, to be updated).
- `tests/unit/tools/test_groundhog_reporting_nextstep.py` (existing, to be updated).
- `tests/unit/tools/test_groundhog_status.py` (existing, to be updated).
- `tests/unit/tools/test_groundhog_detach.py` (existing, to be updated).
- `tests/unit/tools/test_groundhog_snapshot.py` (existing, to be updated).
- `tests/unit/tools/test_code_review_validation/test_code_review_validation_tdd.py` (existing, to be updated).
- `tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py` (existing, to be updated).
- `tests/unit/tools/test_code_review_request_commit_plan/test_code_review_request_commit_plan_tdd.py` (existing, to be updated).
- `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py` (existing, to be updated).
- `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py` (existing, to be updated).
- `tests/unit/tools/test_code_reviewer_acceptance/fixtures.py` (existing, to be updated).
- `tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_acceptance_tdd.py` (existing, to be updated).
- `tests/unit/tools/prepare_release/test_prepare_release_plan_workflow.py` (existing, to be updated).

**Tests first**:

- `test_groundhog_acceptance_levels_tdd.py`, one test per design row: default
  green walk (`full=none src=default proof=none`, skip line, no full child);
  `GHOG_FULL=cov` walk with `src=env` and `--full=cov` restart lines;
  `GHOG_FULL=cov` with `ghog full --full=pass` (`src=param proof=pass`);
  `GHOG_FULL=fast`, `--full=fast` and `--full=none` exit 5 naming the three
  values, never 2; `GHOG_FULL=fast` with `--full=cov` runs at `cov`;
  `--full=pass` with a coverage gap and slow calls exits 0 with no covg or
  slow-test line; `--full=cov` in a parallel project runs no timing pass;
  parallel `--full=speed` with an outlier in the timing pass exits 8 with
  `ghog day --full=speed`; a green direct parallel `ghog full` reports
  `proof=cov` and the not-measured line; direct `ghog full --full=pass` with a
  failure exits 2 with `proof=unproven` and `ghog single ... --full=pass`;
  `ghog single ... --full=cov` green prints `Next: ghog day --full=cov`;
  `GHOG_FULL=speed` with a failing check restarts `ghog day --full=speed`; a
  failing default walk restarts with plain `ghog day`; a no-argument
  `bin/ghog_cycle.bat` calls `day` only (file-content contract).
- `test_groundhog_acceptance_proof_tdd.py`: saved `speed` then default walk
  (noop, `reused=all`); saved `none` then `--full=cov` (upgrade, reused
  headers, `reused=check+affected`); saved `pass` with a coverage gap (exit 3,
  `proof=pass`); saved `pass` with a full failure (exit 2, `proof=none`, next
  `--full=pass` walks); the three parallel timing-pass cap cases; outliers
  only in timings (`proof=cov`); legacy one-line marker (whole default walk,
  rewritten with `proof=none`); `--detach --full=cov` (`full=cov src=param
  proof=pending`, then the done line with `proof=` and `reused=`); saved `cov`
  with only line 2 or an exclusion changed and `--full=cov` (noop); saved
  `speed` with only an exclusion changed and `--full=speed` (upgrade); saved
  `speed` with a Python file changed and `--full=cov` (whole chain).
- Update AT11 and AT16 in `test_groundhog_acceptance_day.py` to the default
  two-step walk, the `--full=cov` three-step walk, the proof marker and the
  marker removal on an `unproven` failure.
- Unit updates: runner shapes per level and parallel flag; closing line with
  and without appended keys; restart and success templates per level, with
  the existing "every post-fix message names `ghog day`" rule extended to "and
  never `--full=none`"; status running and done keys; detached forwarding of
  `--full` for `param` only; legacy-marker functions removed from the snapshot
  tests.
- Literal updates of the rendered project default
  (`ghog day --full=speed (sources: project)`) in the request, commit-plan,
  requestor acceptance and reviewer acceptance tests; the two prepare-release
  operation strings asserted in `test_prepare_release_plan_workflow.py`.
- Remove `xfail` from the three Step 2 gates.

**Classes and behavior**:

- `context.Invocation`: `level: FullLevel | None = None` (the command default
  when `None`) and `level_source: LevelSource = LevelSource.DEFAULT`.
  `context.Deps`: `environ: Callable[[str], str | None] = os.environ.get`,
  the injectable environment seam.
- `cli`: a `level_parent` parser adds a free-string `--full` (default `None`)
  to `check`, `full`, `affected`, `single` and `day` only; `main` resolves the
  level after the root and before the live-run check and the lifecycle
  bracket; a `LevelError` prints
  `ghog: invalid full level '<value>' from <--full|GHOG_FULL>; accepted values: pass, cov, speed`
  through `commands.emit_summary` and returns 5.
- `runner.pytest_command(..., level=FullLevel.SPEED)`: a `full` run at `pass`
  is `--no-cov` without `--durations`; at `cov` it is covered without
  `--durations`; at `speed` it is today's command. `measures_durations`
  passes the effective level, so it stays derived from the built command.
  `verdicts.measures_coverage` is false for `full` at `pass`.
- `tools/groundhog/evidence.py`: `RunEvidence` (`level`, `source`, `proof`,
  `reused`, `scope_key`) with `closing_keys()` and `running_keys()`, and
  `RunOutcome(code, evidence)`.
- `day.run_day` keeps returning the exit code and delegates to
  `day.walk(invocation, deps) -> RunOutcome`: it reads the whole-suite marker,
  computes the digest and timing fingerprint, asks `proof.decide`, then
  noops (noop line, `reused=all`), upgrades (`reused from snapshot` headers for
  check and affected, then the full step at the level) or walks. At `none` it
  stops after a green affected step with the skip success line. At `pass`,
  `cov` and `speed` it runs the full step; at `speed` in a parallel project a
  green full step is followed by a timed `timings` step whose exit becomes
  the walk's. It collects contradicted gates, accumulates the proof, then
  rewrites or removes the marker; exits 5 and 9 and an interruption write
  nothing.
- `commands.run_tests` keeps returning the exit code and delegates to
  `commands.run_tests_outcome`: next-step lines come from the level-aware
  builders, a direct `full` run reports its earned proof and, for a green
  parallel `speed` run, the line saying durations were not measured and
  naming `ghog day --full=speed`.
- `reporting_nextstep`: every fixed restart string becomes a builder fed by
  one `restart_command(level, scope_selector="")` helper; per-level success
  lines (`none` skip line, `pass`, `cov`, `speed`), the noop line naming the
  requested level and the saved proof, the timing-failure and outlier lines
  at `speed`, and the covered-affected gate-reached line naming
  `ghog check` then `ghog day` with the carried level. A standalone
  `ghog affected --no-cov` with no carried level keeps `Next: ghog full`.
- `reporting.closing_line(..., evidence: str = "")` appends the keys after
  the current ones; `MSG_STATUS_KILLED` and `MSG_STATUS_NONE` relaunch with
  the `full=` value of the recorded running line when present.
- `status`: `write_running` and `write_done` append the evidence keys before
  `exit=`; `_dispatch` returns a `RunOutcome`; `_detached_day_command`
  forwards `--full=<token>` only for a `param` level.
- `snapshot`: `is_unchanged` and `write_marker` are removed; the walk uses
  the Step 1 marker functions with `scope=whole`, and
  `effective_proof(root, scope_key, fingerprint, files=None)` reads the
  scope's marker, computes the digest and the timing fingerprint, and applies
  `proof.effective_saved`. The walk's noop and upgrade decision and, in Step 6,
  the request evidence both call this one function.
- `code_review_validation.DEFAULT_PROJECT_VALIDATION_COMMANDS =
  ("ghog day --full=speed",)`; `prepare_release_plan_workflow` names
  `run ghog day --full=cov` and `run git range-diff and ghog day --full=cov`;
  `bin/ghog_cycle.bat` runs `day` alone with no argument, and its header
  comment says so.
- Restart lines carry no scope selector yet: `--whole-suite` does not exist
  before Step 4.

**Completion criteria**:

- The shared gate walk with `<gate-arguments>` = `day --full=cov` reports
  `exit=0`, the three Step 2 gates green.
- `rg -n "is_unchanged|write_marker\(" tools/groundhog` returns nothing.
- `rg -n "full=none|--full=default" tools/groundhog` returns nothing.
- `rg -n "\"ghog day\"" tools/code_review_validation.py` returns nothing.
- `rg -n "call :run_one timings" bin/ghog_cycle.bat` returns nothing.

#### Step 2 -- addendums for leveled walks

Line-budget checkpoint:

- [ ] `tools/groundhog/commands.py`: before about 500 (Step 1 result);
  recount; safe below 550; ceiling <= 650; expected about 540 (advisory).
- [ ] `tools/groundhog/status.py`: before 503; safe; ceiling <= 650; expected
  about 535 (advisory).
- [ ] `tools/groundhog/reporting.py`: before 454; safe; ceiling <= 650;
  expected about 475 (advisory).
- [ ] `tools/groundhog/cli.py`: before 393; safe; ceiling <= 650; expected
  about 425 (advisory).
- [ ] `tools/groundhog/reporting_nextstep.py`: before 297; safe; ceiling
  <= 650; expected about 390 (advisory).
- [ ] `tools/groundhog/runner.py`: before 254; safe; ceiling <= 650; expected
  about 270 (advisory).
- [ ] `tools/groundhog/day.py`: before 135; safe; ceiling <= 650; expected
  about 270 (advisory).
- [ ] `tools/groundhog/evidence.py`: before 0; safe; ceiling <= 650; expected
  about 90 (advisory).
- [ ] `tools/groundhog/context.py`, `durations_summary.py`, `snapshot.py`,
  `code_review_validation.py`, `prepare_release_plan_workflow.py`: recount;
  each safe; ceiling <= 650; small deltas (advisory).
- [ ] New acceptance files: before 0; safe; ceiling <= 650; expected levels
  480 and proof 450 (advisory).
- [ ] Updated tests: `test_groundhog_acceptance_day.py` 256 to about 280,
  `test_groundhog_status.py` 410 to about 440, `test_groundhog_detach.py` 377
  to about 395, `test_code_review_request_tdd.py` 597 literal-only (no
  growth); all ceiling <= 650 (advisory).

Split guidance:

- This plan's extraction trigger for `status.py` is 550 lines, distinct from
  the 650-line repository ceiling: if a step would take it past 550, move
  `run_day_detached`, `default_detach_factory`, `_spawn_survivor` and
  `_detached_day_command` into `tools/groundhog/detach.py`, and Step 4 adds
  its scope forwarding there. Neither an advisory end count nor the risk band
  alone is a repository failure; only passing 650 is.
- If `commands.py` would pass 650, apply the Step 1 report-assembly
  extraction.
- If an acceptance file nears 650, split the restart-line cases into
  `test_groundhog_acceptance_restarts_tdd.py` in the same package.

Full workflow timing run readiness:

- `ghog day --full=cov`: check, affected, then the parallel covered full run,
  which is today's proof for llm-shared.

Time-gated status for Step 2:

- Remove `xfail` from `test_default_walk_spawns_no_full_run`,
  `test_upgrade_spawns_only_the_full_run` and
  `test_stronger_saved_proof_spawns_nothing`; keep their timeouts.

---

### Step 3. Declare groups, capture scopes, and list exclusions

#### Step 3 -- analysis and intent for group declarations

Issues to address:

- No group concept exists: no declaration, matcher, membership, fingerprint
  or capture, and nothing for `process-draft` to validate a group with.
- The review-off pass needs a strict, comparable listing of exclusion entries,
  which the tolerant gate reader cannot give.

Fix intent:

- Add the declaration reader, the gitignore-style matcher, the resolver and
  fingerprint, a tools-level captured-scope model shared by groundhog, the
  request renderer and the review core, and the two read-only listings
  `ghog groups [name]` and `ghog exclude --list [--since=<file>]`.

Expected outcome:

- `ghog groups` lists and validates groups with the exit-5 rules a run will
  apply; captures round-trip and refuse tampering; the exclusion listing and
  comparison match the design table. No run is narrowed yet.

Step framing:

- Design link: "Test Group Declaration", "Captured scope", "Exclusion listing
  and comparison"; design decisions Q12, Q17 matching, Q18 capture content.
- Execution checklist reference: "Shared execution command checklist for all
  v0.13.0 full_suite_levels steps".

#### Step 3 -- implementation for group declarations

**Files involved**:

- `tools/scope_capture.py` (new, to be created).
- `tools/groundhog/group_patterns.py` (new, to be created).
- `tools/groundhog/project_settings.py` (new, to be created).
- `tools/groundhog/groups.py` (new, to be created).
- `tools/groundhog/listings.py` (new, to be created).
- `tools/groundhog/gate.py` (existing, to be updated).
- `tools/groundhog/exclusions.py` (existing, to be updated).
- `tools/groundhog/cli.py` (existing, to be updated).
- `tools/groundhog/runner.py` (existing, to be updated).
- `tools/groundhog/__init__.py` (existing, to be updated).
- `tests/unit/tools/test_scope_capture/__init__.py` (new, to be created).
- `tests/unit/tools/test_scope_capture/test_scope_capture_tdd.py` (new, to be created).
- `tests/unit/tools/test_scope_capture/test_scope_capture_pbt.py` (new, to be created).
- `tests/unit/tools/test_groundhog_group_patterns/__init__.py` (new, to be created).
- `tests/unit/tools/test_groundhog_group_patterns/test_groundhog_group_patterns_tdd.py` (new, to be created).
- `tests/unit/tools/test_groundhog_group_patterns/test_groundhog_group_patterns_pbt.py` (new, to be created).
- `tests/unit/tools/test_groundhog_groups/__init__.py` (new, to be created).
- `tests/unit/tools/test_groundhog_groups/test_groundhog_groups_tdd.py` (new, to be created).
- `tests/unit/tools/test_groundhog_listings/__init__.py` (new, to be created).
- `tests/unit/tools/test_groundhog_listings/test_groundhog_listings_tdd.py` (new, to be created).
- `tests/unit/tools/test_groundhog_gate.py` (existing, to be updated).

**Tests first**:

- Patterns: `*` and `?` never cross `/`; `**` spans segments; a slash-free
  pattern matches a name at any depth; a trailing `/**` matches everything
  below; `!` removes earlier matches and the last match wins;
  `**/tests/**/*sentinel*/**` selects the sentinel example. PBT: a slash-free
  pattern matches a basename at every generated depth; `p` then `!p` matches
  nothing; a `*` segment never matches a path containing an extra `/`.
- Groups: INI sections with multi-line `tests` and `sources`; name rule
  (`^[a-z][a-z0-9_-]*$`); unknown, malformed, unreadable, missing-key, empty
  test side and empty source side each raise a `GroupError` whose message
  names the cause or side; the test side keeps only files fitting
  `python_files` (pytest defaults when undeclared) and drops conftest and data
  files; the source side drops coverage `omit` matches; a source outside the
  coverage `source` setting is kept; the fingerprint changes with a pattern or
  a membership change and not with file order.
- Capture: JSON round trip; `validate_capture` refuses a missing key, a
  fingerprint that no longer matches the content, and a listed file that no
  longer exists, each with a `bound scope unusable: <reason>` message; the
  whole-suite capture carries the fixed fingerprint. PBT: the fingerprint is
  independent of the input order of the file lists.
- Listings: `ghog groups` prints each group with its patterns and test and
  source counts and exits 0; `ghog groups <name>` exits 5 with the resolver's
  message; `ghog exclude --list` prints sorted `<node id> = <seconds>` lines
  then `exclusions=<count>`; an absent file or section gives `exclusions=0`;
  an unreadable file or a malformed entry gives `exclusions=unreadable` and
  exit 5; `--since` prints `exclusions=changed` with the added or raised
  entries, `exclusions=unchanged` for lowered or removed entries, and
  `exclusions=unverified` with exit 5 when either side cannot be read; the
  existing `ghog exclude <node> <seconds>` behavior is unchanged; bad argument
  combinations exit 5, never 2.

**Classes and behavior**:

- `tools/scope_capture.py`: `ScopeKind` (`whole`, `group`), `ResolvedScope`
  (kind, name, normalized test and source patterns, sorted test and source
  files, fingerprint, provenance), `scope_fingerprint(...)`,
  `WHOLE_SCOPE`, `selector()` (`--whole-suite` or `--group=<name>`), `key()`
  (`whole` or `group:<name>`), `label()` (`the whole suite` or
  `group <name>`), `to_json`, `from_json`, `CaptureError`,
  `validate_capture(root, text)` and `write_capture(path, scope)` (atomic).
  It imports nothing from `tools.groundhog` or `tools.review_exchange_*`.
- `tools/groundhog/group_patterns.py`: `compile_patterns(lines)` and
  `matches(compiled, relative_posix_path)`, built on
  `glob.translate(pattern, recursive=True, include_hidden=True)`.
- `tools/groundhog/project_settings.py`: `python_files(root)`,
  `coverage_omit(root)`, `coverage_sources(root)`, `coverage_branch(root)`,
  reading `pyproject.toml`, `pytest.ini`, `setup.cfg`, `tox.ini` and
  `.coveragerc`; the TOML table helper moves here from `gate.py`, which
  imports it.
- `tools/groundhog/groups.py`: `GROUPS_FILE = ".ghog-groups"`, `GroupError`,
  `read_declaration(root)`, `resolve_group(root, name, files)` over the file
  list of `snapshot.source_files`, and `list_groups(root, files)`.
- `tools/groundhog/exclusions.py`: `read_exclusions_strict(root)` raising on
  an unreadable file or a malformed entry (reusing `_parse_entry`),
  `listing_lines(entries)`, `parse_listing(text)` and
  `compare_listings(saved, current)`.
- `tools/groundhog/listings.py`: `run_groups(invocation)` and
  `run_exclude_list(invocation)`, both outside the lifecycle bracket like
  `exclude`, printing through `commands.emit_summary`.
- `cli`: a `groups` subcommand with an optional `name`; `exclude` gains
  `--list` and `--since`, its `node` and `seconds` become optional free
  strings validated by groundhog; `groups` and `exclude` accept no `--full`
  and no scope. `runner.SUB_GROUPS = "groups"`.

**Completion criteria**:

- The shared gate walk with `<gate-arguments>` = `day --full=cov` reports
  `exit=0`.
- `rg -n "pathspec|fnmatch" tools/groundhog/group_patterns.py` returns nothing.
- `rg -n "import tools.groundhog|from tools.groundhog|review_exchange" tools/scope_capture.py`
  returns nothing.
- `rg -n "read_text|open\(" tools/groundhog/groups.py` shows only the
  declaration read.

#### Step 3 -- addendums for group declarations

Line-budget checkpoint:

- [ ] `tools/groundhog/cli.py`: before about 425 (Step 2 result); recount;
  safe; ceiling <= 650; expected about 450 (advisory).
- [ ] `tools/groundhog/exclusions.py`: before 186; safe; ceiling <= 650;
  expected about 280 (advisory).
- [ ] `tools/groundhog/gate.py`: before 120; safe; ceiling <= 650; expected
  about 100 (advisory).
- [ ] New modules: before 0; safe; ceiling <= 650; expected
  `scope_capture.py` 230, `group_patterns.py` 110, `project_settings.py` 170,
  `groups.py` 230, `listings.py` 150 (advisory).
- [ ] New tests: before 0; safe; ceiling <= 650; expected capture 200 and
  PBT 60, patterns 180 and PBT 80, groups 330, listings 320 (advisory).

Split guidance:

- If `groups.py` nears 550, move membership filtering (`python_files` and
  `omit`) into `tools/groundhog/group_membership.py`.
- Keep the exclusion comparison in `exclusions.py`, its only parser.

Full workflow timing run readiness:

- New read-only commands and pure modules; the shared walk at `cov` covers
  them.

Time-gated status for Step 3:

- No gate changes status; the two Step 4 gates stay `xfail`.

---

### Step 4. Select a scope and run, gate and prove inside a group

#### Step 4 -- analysis and intent for group-scoped runs

Issues to address:

- Run commands have no scope selector; pytest always collects every test; the
  coverage gate reads the project `TOTAL`; grouped durations would rewrite the
  shared floor file; a marker covers only the whole suite; restart lines and
  the detached walk lose the scope.

Fix intent:

- Resolve one scope per invocation beside the level; narrow the affected,
  full and timing runs to the group's test files; judge the group gate from a
  scope-owned data file through the coverage API; judge grouped durations by
  the saved floor alone without writes; keep one marker per scope; carry the
  selector in every restart line, in the evidence keys and through the
  detached walk's capture; name `--whole-suite` in the prepare-release
  operations.

Expected outcome:

- Every group row of the design's "Acceptance Cases" that groundhog alone
  decides passes through `cli.main`; the two Step 4 gates are green without
  `xfail`.

Step framing:

- Design link: "Scope Selection", "Group-Scoped Runs", "Group Evidence";
  design decisions Q13 to Q16 and the detached part of Q06 and Q18.
- Execution checklist reference: "Shared execution command checklist for all
  v0.13.0 full_suite_levels steps".

#### Step 4 -- implementation for group-scoped runs

**Files involved**:

- `tools/groundhog/scope.py` (new, to be created).
- `tools/groundhog/group_coverage.py` (new, to be created).
- `tools/groundhog/context.py` (existing, to be updated).
- `tools/groundhog/cli.py` (existing, to be updated).
- `tools/groundhog/runner.py` (existing, to be updated).
- `tools/groundhog/commands.py` (existing, to be updated).
- `tools/groundhog/verdicts.py` (existing, to be updated).
- `tools/groundhog/durations.py` (existing, to be updated).
- `tools/groundhog/durations_summary.py` (existing, to be updated).
- `tools/groundhog/day.py` (existing, to be updated).
- `tools/groundhog/evidence.py` (existing after Step 2, to be updated).
- `tools/groundhog/reporting_nextstep.py` (existing, to be updated).
- `tools/groundhog/status.py` (existing, to be updated); when Step 2 extracted the detached walk, its `tools/groundhog/detach.py` takes this change instead.
- `tools/groundhog/__init__.py` (existing, to be updated).
- `tools/prepare_release/prepare_release_plan_workflow.py` (existing, to be updated).
- `tests/unit/tools/groundhog_group_support.py` (new, to be created).
- `tests/unit/tools/test_groundhog_scope/__init__.py` (new, to be created).
- `tests/unit/tools/test_groundhog_scope/test_groundhog_scope_tdd.py` (new, to be created).
- `tests/unit/tools/test_groundhog_group_coverage/__init__.py` (new, to be created).
- `tests/unit/tools/test_groundhog_group_coverage/test_groundhog_group_coverage_tdd.py` (new, to be created).
- `tests/unit/tools/test_groundhog_group_coverage/test_groundhog_group_coverage_pbt.py` (new, to be created).
- `tests/unit/tools/test_groundhog_acceptance_groups/__init__.py` (new, to be created).
- `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_groups_tdd.py` (new, to be created).
- `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_group_gate_tdd.py` (new, to be created).
- `tests/unit/tools/test_groundhog_levels_perf/test_groundhog_levels_perf_tdd.py` (existing after Step 0, to be updated).
- `tests/unit/tools/test_groundhog_runner.py` (existing, to be updated).
- `tests/unit/tools/test_groundhog_durations.py` (existing, to be updated).
- `tests/unit/tools/test_groundhog_detach.py` (existing, to be updated).
- `tests/unit/tools/prepare_release/test_prepare_release_plan_workflow.py` (existing, to be updated).

**Tests first**:

- Scope resolution: explicit `--group`, `--whole-suite` or `--scope-file` wins
  and `GHOG_GROUP` is then not read (an invalid variable included); two
  explicit selectors exit 5 naming both; `GHOG_GROUP` used otherwise; whole
  suite by default without reading `.ghog-groups`; an unusable capture stops
  with `bound scope unusable: <reason>` before any spawn and never falls back.
- Group coverage: the smallest folder set holds every source; the data file
  path; a fully executed source at 100%; a never-executed source at 0%; an
  `omit` file out of the set; a missed branch reported when the project
  measures branches; a missing, unreadable or stale data file raises an
  evidence error. PBT: the folder set covers every source and holds no folder
  inside another.
- `groundhog_group_support.py`: a `tmp_path` project builder with a
  `.ghog-groups` `sentinel` group, and a spawn factory that writes a coverage
  data file to the `COVERAGE_FILE` it sees at spawn time (through
  `coverage.CoverageData`).
- `test_groundhog_acceptance_groups_tdd.py`: group walk positional paths and
  `scope=group:sentinel`; whole-suite `cov` proof then grouped `cov` walks;
  `sentinel` proof then `other` walks; `--group=nope` and an unreadable
  declaration exit 5; an unreadable declaration does not block a whole-suite
  walk; empty test side and empty source side exit 5 naming the side; a valid
  group with nothing affected stays green with `proof=none`; a grouped
  `--full=pass` whose files hold no test exits 5; `GHOG_GROUP=nope` with
  `--whole-suite` walks; grouped failure restarts in the group; a whole-suite
  restart names `--whole-suite` despite `GHOG_GROUP`; membership and pattern
  changes invalidate the group proof; grouped `--full=speed` exits 8 on the
  floor alone with `a.ghog.outliers` byte-identical; an exclusion outside the
  group survives; a new exclusion caps a saved group `speed` proof at `cov`;
  `--detach --group=sentinel` forwards a capture and the status shows the
  scope; an edit of `.ghog-groups` after launch leaves the child on the
  capture's lists; `--scope-file` runs only the captured files after a
  same-name pattern edit; a deleted captured file and an edited capture exit
  5; `--scope-file` with `--group` exits 5.
- `test_groundhog_acceptance_group_gate_tdd.py`: gate at 100% over group
  sources; never-executed source exit 3 listed at 0%; `lib/widget.py` outside
  the coverage `source` measured through the added `--cov` folder; `omit` kept;
  invalid data exit 5 with saved proof unchanged; missed branch exit 3.
- Unit updates: runner positional paths, `--cov=<folder>` options,
  `--cov-fail-under=0` and the spawn-time `COVERAGE_FILE`, restored after a
  normal spawn and after a raising factory, both for a variable that already
  existed (previous value back) and for an absent one (removed); floor-only duration
  rule; detached command scope arguments; prepare-release strings end with
  `--whole-suite`.
- Remove `xfail` from the two Step 4 gates.

**Classes and behavior**:

- `tools/groundhog/scope.py`: `resolve_scope(args, environ, root, files)`
  returning a `ResolvedScope`, `ScopeError`, `GHOG_GROUP_ENV`, and
  `write_detach_capture(root, scope)` to `a.ghog.day.scope.json` through
  `artifact_path`.
- `context.Invocation.scope: ResolvedScope = WHOLE_SCOPE`.
- `cli`: free options `--group`, `--whole-suite` and `--scope-file` on the
  five run commands, resolved once after the level, setup errors exit 5;
  `timings`, `status`, `init`, `exclude` and `groups` take none.
- `runner.pytest_command(..., test_paths=(), cov_folders=())`: grouped
  `full`, `affected` and `timings` commands end with the group's test files;
  grouped covered runs add one `--cov=<folder>` per folder and
  `--cov-fail-under=0`. `StreamConfig.env_overrides` is applied to
  `os.environ` only around the factory call in `run_streaming` and restored in
  a `finally` block, so a factory exception still restores it: a variable that
  existed gets its previous value back, an absent one is deleted again.
- `tools/groundhog/group_coverage.py`: `cov_folders(sources)`,
  `data_file(root, name)` (`a.ghog.coverage.<group>`), `GroupCoverage`
  (percent, gap rows, error) and `judge(root, scope, data_path, started)`,
  reading the data through `coverage.Coverage(data_file=..., config_file=True)`
  restricted to the resolved sources, counting branches when the project
  measures them, and rendering gap rows in the term-missing shape covg reads.
- `commands` and `verdicts`: a grouped full run deletes the data file first
  and judges the group gate at 100%, never the parsed `TOTAL`; a covered
  grouped `affected` appends and judges the gate as an intermediate check that
  records no proof; data errors exit 5 with the data problem named.
- `durations.summarize_by_floor(durations, floor)` and
  `durations_summary.judge` for a grouped run: the saved active floor alone,
  exclusions restricted to the group's node ids and applied read-only,
  nothing written to the floor file.
- `day.walk`: per-scope marker through `marker_path_for(root, scope.key())`,
  `fingerprint` from the scope, the shared file list for digest and
  membership (one tree walk), the timing step narrowed to the group.
- `evidence` and `reporting_nextstep`: `scope=` key on every run command, the
  selector after the level selector in every restart and repair line, success
  and noop lines naming `for the whole suite` or `for group <name>`.
- Detached walk: always passes the scope; `--whole-suite`, or
  `--scope-file=<a.ghog.day.scope.json>` for a group, written before the
  spawn.
- `prepare_release_plan_workflow`: `run ghog day --full=cov --whole-suite`
  and `run git range-diff and ghog day --full=cov --whole-suite`.

**Completion criteria**:

- The shared gate walk with `<gate-arguments>` = `day --full=cov --whole-suite`
  reports `exit=0`, the two Step 4 gates green.
- `rg -n "write_floor|write_exclusions" tools/groundhog/durations_summary.py`
  shows both writes guarded by the whole-suite branch only.
- `rg -n "COVERAGE_FILE" tools/groundhog` names only the runner override and
  `group_coverage`.
- `rg -n "ghog day --full=cov --whole-suite" tools/prepare_release/prepare_release_plan_workflow.py`
  shows both operations.

#### Step 4 -- addendums for group-scoped runs

Line-budget checkpoint:

- [ ] `tools/groundhog/commands.py`: before about 540 (Step 2 result);
  recount; 550-through-650 risk if above 550; ceiling <= 650; expected about
  570 (advisory).
- [ ] `tools/groundhog/status.py` or `detach.py`: recount; ceiling <= 650;
  expected status about 560 without extraction (advisory).
- [ ] `tools/groundhog/cli.py`: before about 450; safe; ceiling <= 650;
  expected about 480 (advisory).
- [ ] `tools/groundhog/reporting_nextstep.py`: before about 390; safe;
  ceiling <= 650; expected about 420 (advisory).
- [ ] `tools/groundhog/durations.py`: before 368; safe; ceiling <= 650;
  expected about 395 (advisory).
- [ ] `tools/groundhog/runner.py`, `day.py`, `durations_summary.py`,
  `context.py`, `evidence.py`: recount; safe; ceiling <= 650; expected runner
  320, day 300, durations_summary 200, context 120, evidence 110 (advisory).
- [ ] New modules: before 0; safe; ceiling <= 650; expected `scope.py` 170,
  `group_coverage.py` 230 (advisory).
- [ ] New tests and support: before 0; safe; ceiling <= 650; expected support
  160, scope 220, coverage 260 and PBT 50, groups acceptance 560, gate
  acceptance 300 (advisory).

Split guidance:

- If `commands.py` would pass 650, move the group-gate branch and data-error
  reporting into `group_coverage.py` and call it from `verdicts.py`; if it
  sits in the risk band, record it and keep further growth out of it.
- Extract `tools/groundhog/detach.py` from `status.py` if it would pass this
  plan's 550-line extraction trigger (the 650-line ceiling stays the only
  repository failure).
- If the groups acceptance file nears 650, move the `--scope-file` and detach
  cases into `test_groundhog_acceptance_group_capture_tdd.py`.

Full workflow timing run readiness:

- `ghog day --full=cov --whole-suite` exercises the whole-suite branch of
  every new path; grouped paths run in the acceptance tests with fakes.

Time-gated status for Step 4:

- Remove `xfail` from `test_grouped_walk_passes_only_group_test_files` and
  `test_grouped_walk_walks_the_tree_once`; keep their timeouts. No gate
  remains `xfail` after this step.

---

### Step 5. Read the effort scope and print it through pw

#### Step 5 -- analysis and intent for the effort scope

Issues to address:

- pw reads no metadata line from a requirement and prints no ghog command;
  `pw progress` shows no scope.

Fix intent:

- Add a shared effort-scope reader over `WorkflowState.requirement`, a
  `pw scope [ghog arguments]` command printing the selector or the completed
  ghog command, and a `scope` line in `pw progress`.

Expected outcome:

- `pw scope day` prints `ghog day --group=sentinel` for a grouped effort and
  `ghog day --whole-suite` otherwise, refuses an invalid group without a
  fallback, and never reads the draft.

Step framing:

- Design link: "The effort's declared scope", "Scope-carrying workflow
  commands", "Scope display in pw progress"; design decisions Q17 and Q19.
- Execution checklist reference: "Shared execution command checklist for all
  v0.13.0 full_suite_levels steps".

#### Step 5 -- implementation for the effort scope

**Files involved**:

- `tools/effort_scope.py` (new, to be created).
- `tools/prompt_workflow_scope.py` (new, to be created).
- `tools/prompt_workflow_parser.py` (existing, to be updated).
- `tools/prompt_workflow.py` (existing, to be updated).
- `tools/prompt_workflow_progress.py` (existing, to be updated).
- `instructions/run-pw.md` (existing, to be updated).
- `tests/unit/tools/test_effort_scope/__init__.py` (new, to be created).
- `tests/unit/tools/test_effort_scope/test_effort_scope_tdd.py` (new, to be created).
- `tests/unit/tools/test_prompt_workflow_scope/__init__.py` (new, to be created).
- `tests/unit/tools/test_prompt_workflow_scope/test_prompt_workflow_scope_tdd.py` (new, to be created).
- `tests/unit/tools/test_prompt_workflow_parser.py` (existing, to be updated).

**Tests first**:

- Effort scope: no requirement (`whole suite`, reason `no requirement yet`,
  no draft read even when the draft names a group); no line (whole suite,
  reason names the requirement); `- Test group: whole suite`; a valid group
  (selector, fingerprint, source path); an unknown or empty group raises an
  error naming the requirement and the cause; two lines raise; the read stops
  at the first level-two heading (`##[space]`).
- `pw scope`: prints `--group=sentinel` or `--whole-suite`; `pw scope day
  --full=speed` prints `ghog day --full=speed --group=sentinel`; ghog
  arguments already carrying a selector are refused with an error naming it,
  in both the equals and the separated forms (`--group=x` and `--group x`,
  `--scope-file=f` and `--scope-file f`) and for `--whole-suite`; an invalid
  group exits 2 with the message and prints no
  selector; `GHOG_GROUP=sentinel` for an ungrouped effort still prints
  `--whole-suite`; a stale draft naming `sentinel` with the requirement line
  removed prints `--whole-suite`; activation after step 2, switching and
  deactivation change the next output.
- `pw progress`: the `scope` line after the `step` and journal lines, or
  after `phase` when no step line exists, for the three source forms and for
  an invalid group (an error text, no fallback).
- Parser: `pw scope`, `pw scope day --full=speed`, and `pw --root X scope day`.

**Classes and behavior**:

- `tools/effort_scope.py`: `TEST_GROUP_PREFIX = "- Test group: "`,
  `WHOLE_SUITE_VALUE = "whole suite"`, `EffortScope` (scope, source path,
  reason text), `EffortScopeError`, and `read_effort_scope(root, requirement)`
  validating a named group through `groundhog.groups.resolve_group` over
  `snapshot.source_files(root)`.
- `tools/prompt_workflow_scope.py`: `run_scope(root, ghog_args)` resolving
  the current topic with `handoff.resolve_current_topic`, `steps.compute_state`
  and `effort_scope`, printing one line; `scope_lines(root, topic, state)`
  returning the `scope` row.
- `prompt_workflow_parser`: a `scope` subparser with an
  `argparse.REMAINDER` positional `ghog_args`; `prompt_workflow._run_report`
  dispatches it; `prompt_workflow_progress._topic_lines` appends
  `scope_lines`.
- `instructions/run-pw.md`: `pw scope` in the command list and the table, and
  the `scope` line in the `pw progress` description.

**Completion criteria**:

- The shared gate walk with `<gate-arguments>` = `day --full=cov --whole-suite`
  reports `exit=0`; `pw scope day --full=cov` prints that same command for this
  effort.
- `rg -n "draft" tools/effort_scope.py` shows no draft read.
- `rg -n "pw scope" instructions/run-pw.md` lists the command.

#### Step 5 -- addendums for the effort scope

Line-budget checkpoint:

- [ ] `tools/prompt_workflow.py`: before 540; safe; ceiling <= 650; expected
  about 545 (advisory).
- [ ] `tools/prompt_workflow_progress.py`: before 487; safe; ceiling <= 650;
  expected about 495 (advisory).
- [ ] `tools/prompt_workflow_parser.py`: before 182; safe; ceiling <= 650;
  expected about 200 (advisory).
- [ ] `tools/effort_scope.py` and `tools/prompt_workflow_scope.py`: before 0;
  safe; ceiling <= 650; expected 150 and 140 (advisory).
- [ ] New tests: before 0; safe; ceiling <= 650; expected effort scope 230,
  pw scope 300 (advisory); `test_prompt_workflow_parser.py` 132 to about 160.

Split guidance:

- Keep `test_prompt_workflow_progress_tdd.py` (502) and
  `test_prompt_workflow_main.py` (614) unchanged; progress scope cases live in
  the new package.

Full workflow timing run readiness:

- The scope reader walks the project once per call; its tests use small
  `tmp_path` trees.

Time-gated status for Step 5:

- No perf gate is affected.

---

### Step 6. Validate requests in the effort scope and bind the round scope

#### Step 6 -- analysis and intent for the bound review scope

Issues to address:

- The request renderer renders the project default without a selector, cannot
  tell a declared set from the default, shows no migration notice or group
  statement, records no scope evidence, and knows nothing of the scope the
  previous round was published with.
- `publish-request` takes no capture; the coordination record keeps no scope
  fingerprint; `status` reports none; `complete`, `force_complete` and the
  escalation resolution have no capture to remove or archive.
- A required renderer argument cannot be discovered from a request that fails
  to render, so the instructions that pass the new arguments, and the reviewer
  contract that consumes the bound capture, must ship with this step rather
  than with Step 7's broad documentation pass.

Fix intent:

- Extract the renderer's file helpers, then add a renderer-side scope module,
  scope evidence in the evidence JSON and the envelope (its proof computed by
  the walk's own `snapshot.effective_proof`), a caller-owned capture output, a
  scope-change input, a core-owned `paths.scope` copy with its fingerprint in
  the coordination record, `bound_scope` in `status`, removal or archival on
  every transition that removes or archives the coordination record, and the
  `bound` line of `pw progress`.
- Ship the minimum invocation contracts with the code: the requestor passes
  `--scope-capture-output` to the renderer and `--scope-capture-file` to
  `publish-request` (plus `--scope-change-file` for a changed replacement),
  and the reviewer and the reviewer-side implementation check run
  `ghog affected --no-cov --scope-file=<paths.scope>`.

Expected outcome:

- A request renders `ghog day --full=speed --group=sentinel` (or
  `--whole-suite`) as its project default, publishes with its capture, and a
  later replacement with a different scope demands `--scope-change-file`;
  legacy records and requests keep working and report `bound_scope: missing`.
- The code review of this very step can already render, publish and consume
  its bound scope by following the instructions available at Step 6.

Step framing:

- Design link: "Requestor Validation at Speed", "Bound scope of a review
  round", "Scope display in pw progress", "Exact-scope proof"; design
  decisions Q10, Q11, Q16 and Q18.
- Execution checklist reference: "Shared execution command checklist for all
  v0.13.0 full_suite_levels steps".

#### Step 6 -- implementation for the bound review scope

**Files involved**:

- `tools/code_review_request_files.py` (new, to be created).
- `tools/code_review_request_scope.py` (new, to be created).
- `tools/code_review_request.py` (existing, to be updated).
- `tools/code_review_validation.py` (existing, to be updated).
- `templates/code-review-request.template.md` (existing, to be updated).
- `tools/review_exchange_scope.py` (new, to be created).
- `tools/review_exchange_models_envelope.py` (existing, to be updated).
- `tools/review_exchange_models_coordination.py` (existing, to be updated).
- `tools/review_exchange_models.py` (existing, to be updated).
- `tools/review_artifact_registry.py` (existing, to be updated).
- `tools/review_exchange_paths.py` (existing, to be updated).
- `tools/review_exchange_cli_parser.py` (existing, to be updated).
- `tools/review_exchange_cli.py` (existing, to be updated).
- `tools/review_exchange_cli_ownership.py` (existing, to be updated).
- `tools/review_exchange_publication.py` (existing, to be updated).
- `tools/review_exchange_human.py` (existing, to be updated).
- `tools/prompt_workflow_scope.py` (existing after Step 5, to be updated).
- `instructions/code-review-requestor.md` (existing, to be updated).
- `instructions/review-requestor.md` (existing, to be updated).
- `instructions/code-reviewer.md` (existing, to be updated).
- `instructions/implementation-check.md` (existing, to be updated).
- `tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py` (existing, to be updated).
- `tests/unit/tools/test_code_review_request_commit_plan/test_code_review_request_commit_plan_tdd.py` (existing, to be updated).
- `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py` (existing, to be updated).
- `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py` (existing, to be updated).
- `tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_contracts_tdd.py` (existing, to be updated).
- `tests/unit/tools/test_code_review_requestor_instruction/test_code_review_requestor_instruction_tdd.py` (existing, to be updated).
- `tests/unit/tools/test_review_requestor_instruction/test_review_requestor_instruction_tdd.py` (existing, to be updated).
- `tests/unit/tools/test_code_reviewer_instruction/test_code_reviewer_instruction_tdd.py` (existing, to be updated).
- `tests/unit/tools/test_implementation_check_reviewer_mode/test_implementation_check_reviewer_mode_tdd.py` (existing, to be updated).
- `tests/unit/tools/test_code_review_request_scope/__init__.py` (new, to be created).
- `tests/unit/tools/test_code_review_request_scope/test_code_review_request_scope_tdd.py` (new, to be created).
- `tests/unit/tools/test_code_review_validation/test_code_review_validation_tdd.py` (existing, to be updated).
- `tests/unit/tools/test_review_exchange_scope/__init__.py` (new, to be created).
- `tests/unit/tools/test_review_exchange_scope/test_review_exchange_scope_tdd.py` (new, to be created).
- `tests/unit/tools/test_review_exchange_models/test_review_exchange_models_scope_tdd.py` (new, to be created).
- `tests/unit/tools/test_review_exchange_cli/test_review_exchange_cli_boundaries_tdd.py` (existing, to be updated).
- `tests/unit/tools/test_review_exchange_paths/test_review_exchange_paths_tdd.py` (existing, to be updated).
- `tests/unit/tools/test_review_artifact_home/test_review_artifact_registry_tdd.py` (existing, to be updated).
- `tests/unit/tools/test_review_artifact_home/test_review_artifact_registry_pbt.py` (existing, to be updated).
- `tests/unit/tools/test_prompt_workflow_scope/test_prompt_workflow_scope_tdd.py` (existing after Step 5, to be updated).

**Tests first**:

- Validation: `load_project_validation` reports `declared` for a
  `.review-validation` file and not for the default; only the default is
  completed with the selector; plan and request additions are rendered as
  given; the migration notice appears when a declared `ghog day` has no
  `--full`, with the qualified wording of the design; for a grouped effort the
  group proof is claimed only when a declared command is a `ghog day` walk
  with `--full=speed` and the exact `--group=<name>`, otherwise the statement
  says no `speed` proof is established for that group.
- Renderer scope: `test_scope` (scope key, group, fingerprint, requirement,
  and the proof returned by `snapshot.effective_proof` for that scope) in the
  evidence JSON and the envelope; a declaration edited between the walk and
  the render shows missing proof; the capture written to
  `--scope-capture-output` validates; a replacement whose current scope
  differs from the bound capture without `--scope-change-file` exits 2 naming
  both scopes, and with it renders the "Scope change" block (previous scope,
  new scope, reason); an invalid effort group exits 2 with the cause.
- Timing validity of rendered proof, for the whole suite and for a group: a
  saved `speed` marker whose source digest and scope fingerprint still match
  but whose gate floor (line 2) or exclusion entries changed renders at most
  `cov`; after a successful `ghog day --full=speed` walk of the same scope
  (driven through `cli.main` with fakes), the render shows `speed` again.
- Exchange: `publish-request --scope-capture-file` for a request carrying
  `test_scope`; an incomplete capture or a fingerprint different from the
  envelope is refused before any write; the copy lands at `paths.scope` and
  the record keeps `bound_scope_fingerprint`; `status` returns `bound_scope`
  and `paths.scope`; a legacy request and record report `bound_scope: missing`
  without `paths.scope`; each publication replaces the copy.
- Capture lifecycle, asserting the resulting artifact set in the artifact
  home after each transition: `complete` removes the capture with the
  coordination record; `complete --force` removes it with the record;
  `resolve` (escalation resolution clearing live evidence through
  `_resolve_live_evidence(archive=False)`) removes it; `archive`
  (`_resolve_live_evidence(archive=True)`) moves it to its archive name beside
  the other archived evidence and lists it among the archived paths; the fresh
  round started by `resolve` or `archive` reports `bound_scope: missing` until
  its next publication.
- Step 6 round trip: in one `tmp_path` repository, render a request with
  `--scope-capture-output`, publish it with `--scope-capture-file`, read
  `paths.scope` from `status`, then run `cli.main` with
  `affected --no-cov --scope-file=<paths.scope>` and assert that only the
  captured test files are passed to the fake pytest child.
- Renderer callers: add `--scope-capture-output` (an ignored `a.*` output in
  the fixture's artifact home) to every existing renderer invocation in
  `test_code_review_request_tdd.py`, `test_code_review_request_commit_plan_tdd.py`,
  `test_code_review_requestor_acceptance_tdd.py`,
  `test_code_review_requestor_io_acceptance_tdd.py` and
  `tests/acceptance/commit_plan_check/test_commit_plan_check_acceptance/test_commit_plan_check_contracts_tdd.py`;
  a missing option is asserted as a renderer error in the new scope package.
  `test_code_reviewer_acceptance_tdd.py` builds `CodeReviewRoundInput`
  directly and stays unchanged because `test_scope` defaults to `None` there.
- Instruction contracts, pinned in the existing instruction test packages:
  `code-review-requestor.md` names `--scope-capture-output`,
  `--scope-capture-file` and `--scope-change-file`; `review-requestor.md`
  names the `--scope-capture-file` input of a code `publish-request` and the
  core-owned `paths.scope`; `code-reviewer.md` and the reviewer evidence setup
  of `implementation-check.md` name
  `ghog affected --no-cov --scope-file=<paths.scope>` and treat a missing,
  legacy or refused capture as missing evidence.
- Models and paths: the optional envelope `test_scope` and record fingerprint
  round trip and stay absent for legacy payloads; `ArtifactPaths.scope` names
  `a.review-scope.code.<version>.<slug>.json`; the registry parses that name
  (PBT round trip extended to the new kind); the ignore probe covers it.
- `pw progress`: the `bound` line shows the bound scope and `pending change`
  when it differs from the effort scope, including a same-name definition
  change.

**Classes and behavior**:

- `tools/code_review_request_files.py`: `_root_file`, `_is_effectively_ignored`,
  `_read_utf8` and `_write_utf8` moved verbatim from `code_review_request.py`
  (public names without the underscore), first, before any growth.
- `tools/code_review_validation.py`: `ProjectValidation(commands, declared)`,
  `load_project_validation(root)` (the old loader returns its commands),
  `complete_project_default(validation, selector)`, `migration_notice(...)`,
  `group_claim_statement(...)`.
- `tools/code_review_request_scope.py`: `resolve_request_scope(root, plan)`
  building the `Topic` from the plan path (draft path beside it), then
  `steps.compute_state` and `effort_scope.read_effort_scope`;
  `scope_evidence(root, scope)` calling `snapshot.effective_proof`, the same
  function the walk uses, so the rendered proof is never higher than the walk
  would accept; `bound_capture(root, context)` reading the coordination
  record and `paths.scope`; `scope_change_block(previous, current, reason)`.
- `tools/code_review_request.py`: new options `--scope-capture-output`
  (required) and `--scope-change-file` (optional); `CodeReviewRoundInput` and
  `_CodeReviewEvidence` gain `test_scope` (default `None` for direct
  constructions, always set by the CLI); `render_code_review_request` passes
  `test_scope` to the envelope; the template gains a `## Validation scope for
  ...` section filled with the migration notice, the group statement and the
  scope-change block.
- `tools/review_exchange_scope.py`: `publish_scope_capture(paths, text,
  expected_fingerprint)` (validate with `scope_capture`, atomic write),
  `remove_scope_capture(paths)`, `archive_scope_capture(paths, compact)`
  (moves the capture to its archive name and returns it), and
  `bound_scope_payload(paths, record)`; `bound_scope_payload` and the
  `pw progress` `bound` line read the capture through
  `scope_capture.validate_capture`, so both report one validity rule.
- Models: `Envelope.test_scope` (optional, legacy-absent),
  `CoordinationRecord.bound_scope_fingerprint` (optional, legacy-absent),
  `ArtifactPaths.scope` (outside `fixed_paths`), `ArchiveKind.SCOPE`,
  `RegisteredArtifactKind.SCOPE_CAPTURE` with its name and regex, the archive
  name and regex accepting the `scope.json` archive kind, and
  `transient_paths_for_ignore` including the live capture.
- CLI and core: `publish-request` gains `--scope-capture-file` (the
  `publish-answer` parser does not); `_dispatch_publication` reads it like the
  content; `CorePort.publish_request(markdown, transcript_content,
  scope_capture=None)`; `publish_request` validates and writes the capture
  inside the transition lock before the final coordination write;
  `_success_payload` adds `bound_scope`; `_paths_payload` adds `scope` when
  bound.
- Capture lifetime follows the coordination record on all three transitions
  of `review_exchange_human.py` that remove or archive it: `complete` and
  `force_complete` call `remove_scope_capture` beside their
  `remove_exact(paths.coordination)`; `_resolve_live_evidence`, shared by
  `resolve` and `archive` through `resolve_escalation`, removes the capture
  when clearing and calls `archive_scope_capture` when archiving, adding the
  archived path to its returned tuple. `review_exchange_store.py` is not
  edited.
- `prompt_workflow_scope.scope_lines` adds the `bound` row for an active code
  exchange of the topic, read from its coordination record and capture, so
  `review_status.py` stays untouched.
- Minimum instruction contracts: `code-review-requestor.md` adds the two
  renderer options and the publication input to its existing render and
  `publish-request` commands (output named
  `a.<slug>.step<x>.tmp.scope-capture.json`); `review-requestor.md` adds the
  code-only `--scope-capture-file` input and `paths.scope`; `code-reviewer.md`
  and the reviewer evidence setup of `implementation-check.md` replace their
  `ghog affected --no-cov` call with the `--scope-file=<paths.scope>` form and
  name a missing, legacy (`bound_scope: missing`) or refused capture as
  missing evidence. Everything else of the design's instruction list stays in
  Step 7.

**Completion criteria**:

- The shared gate walk with `<gate-arguments>` = `day --full=cov --whole-suite`
  reports `exit=0`.
- `rg -n "def _root_file|def _is_effectively_ignored" tools/code_review_request.py`
  returns nothing.
- `rg -n "scope" tools/review_status.py tools/review_status_models.py`
  returns nothing new.
- `rg -n "scope-capture-file" tools/review_exchange_cli_parser.py` shows the
  request parser only.
- `rg -n "remove_scope_capture|archive_scope_capture" tools/review_exchange_human.py`
  shows `complete`, `force_complete` and `_resolve_live_evidence`.
- `rg -n "scope-capture-output|scope-capture-file|scope-file=<paths.scope>" instructions/code-review-requestor.md instructions/review-requestor.md instructions/code-reviewer.md instructions/implementation-check.md`
  lists each instruction.
- The Step 6 round-trip test passes, so this step's own code review can
  render, publish and consume its bound scope with the instructions available
  at Step 6.

#### Step 6 -- addendums for the bound review scope

Line-budget checkpoint:

- [ ] `tools/code_review_request.py`: before 597; 550-through-650 risk;
  ceiling <= 650; target <= 590 after the step (mandatory only because
  extracting the file helpers to keep renderer headroom is this step's explicit
  goal); expected about 580 (advisory).
- [ ] `tools/review_exchange_models.py`: before 562; risk; ceiling <= 650;
  expected about 565 (advisory).
- [ ] `tools/review_exchange_cli.py`: before 515; safe; ceiling <= 650;
  expected about 545 (advisory).
- [ ] `tools/review_exchange_human.py`: before 480; safe; ceiling <= 650;
  expected about 490 (advisory).
- [ ] `tools/review_exchange_publication.py` 387, `review_exchange_models_coordination.py`
  301, `review_artifact_registry.py` 301, `review_exchange_models_envelope.py`
  231, `review_exchange_paths.py` 229, `review_exchange_cli_ownership.py` 191,
  `review_exchange_cli_parser.py` 159, `code_review_validation.py` about 160
  after Step 2: all safe; ceiling <= 650; expected deltas 10 to 80 (advisory).
- [ ] New modules: before 0; safe; ceiling <= 650; expected files 90,
  request scope 220, exchange scope 120 (advisory).
- [ ] New tests: before 0; safe; ceiling <= 650; expected request scope 500,
  exchange scope 420, models scope 140 (advisory); boundaries 419 to about
  450, paths 414 to about 435, registry 137 to about 165, validation 170 to
  about 260.
- [ ] Renderer caller tests (argument edits only): `test_code_review_request_tdd.py`
  597, risk band, ceiling <= 650, expected about 605;
  `test_code_review_request_commit_plan_tdd.py` 243,
  `test_code_review_requestor_acceptance_tdd.py` 488,
  `test_code_review_requestor_io_acceptance_tdd.py` 296 and
  `test_commit_plan_check_contracts_tdd.py` 275, all safe, a few lines each
  (advisory).
- [ ] Instruction tests: requestor 232, review-requestor 84, reviewer 241,
  implementation-check 97; safe; ceiling <= 650; small deltas (advisory).

Split guidance:

- `review_exchange_store.py` (599) and `review_status.py` (650) receive no
  edit; any capture IO goes to `review_exchange_scope.py`.
- If `review_exchange_cli.py` would pass 550, move `bound_scope` and
  `scope` payload building into `review_exchange_scope.py`.
- Keep `test_review_exchange_cli_tdd.py` (643) unchanged; in
  `test_code_review_request_tdd.py` (597) limit the change to the new
  argument, and if a shared fixture helper there must change, extend its
  argument list rather than adding cases; new cases go to the scope package.

Full workflow timing run readiness:

- Renderer and exchange cases use `tmp_path` repositories and in-process
  calls; no new subprocess.

Time-gated status for Step 6:

- No perf gate is affected.

---

### Step 7. Update the workflow instructions, templates and groundhog manuals

#### Step 7 -- analysis and intent for the workflow instructions

Issues to address:

- The development instructions still promise a full coverage pass from
  `ghog day`; the groundhog loop knows no levels or scopes; the requestor
  instruction names only the Step 6 arguments, not the `speed` validation
  policy around them; the review-off chain has no `speed` pass; process-draft and write-requirement
  record no scope; the manuals and the specification describe one objective.

Fix intent:

- Apply the rest of the design's "Workflow Instructions" list in one pass, on
  top of the invocation contracts Step 6 already shipped (renderer and
  publication arguments, reviewer `--scope-file` evidence), keep every
  adapter a redirect, and pin the new contracts in a new instruction test
  package.

Expected outcome:

- Each instruction names the command, level and scope the design gives its
  phase; pinned phrases and adapter checks pass.

Step framing:

- Design link: "Workflow Instructions", "Review-Off Speed Pass", "Group
  Activation and Change", "Bound scope of a review round"; design decisions
  Q02, Q09, Q17 and Q19.
- Execution checklist reference: "Shared execution command checklist for all
  v0.13.0 full_suite_levels steps".

#### Step 7 -- implementation for the workflow instructions

**Files involved**:

- `instructions/implement-step.md` (existing, to be updated).
- `instructions/implement-missing-step.md` (existing, to be updated).
- `instructions/split-large-file.md` (existing, to be updated).
- `instructions/group-commits-msg.md` (existing, to be updated).
- `instructions/write-plans.md` (existing, to be updated).
- `templates/write-plans.template.md` (existing, to be updated).
- `templates/step-handoff.template.md` (existing, to be updated).
- `instructions/step-journal.md` (existing, to be updated).
- `instructions/groundhog.md` (existing, to be updated).
- `instructions/fix_slow_test.md` (existing, to be updated).
- `instructions/code-review-requestor.md` (existing after Step 6, to be updated).
- `instructions/prepare-release.md` (existing, to be updated).
- `instructions/process-draft.md` (existing, to be updated).
- `instructions/write-requirement.md` (existing, to be updated).
- `templates/write-requirement.template.md` (existing, to be updated).
- `GROUNDHOG.md` (existing, to be updated).
- `tools/Pytest reset specs.md` (existing, to be updated).
- `DEVELOPMENT.md` (existing, to be updated).
- `.claude/skills/prepare-release/SKILL.md` (existing, to be updated).
- `.github/skills/prepare-release/SKILL.md` (existing, to be updated).
- `.agents/llm-shared/skills/fix-slow-test/SKILL.md` (existing, to be updated).
- `.agent/workflows/fix-slow-test.md` (existing, to be updated).
- `tests/unit/tools/test_code_review_requestor_instruction/test_code_review_requestor_instruction_tdd.py` (existing after Step 6, to be updated).
- `tests/unit/tools/test_full_suite_levels_instructions/__init__.py` (new, to be created).
- `tests/unit/tools/test_full_suite_levels_instructions/test_full_suite_levels_instructions_tdd.py` (new, to be created).

**Tests first**:

- New contract package: the development instructions run the command printed
  by `pw scope day` and describe check plus affected tests, never a full
  coverage pass; `implement-step.md` orders the review-off `speed` pass after
  the review-mode sample and before the commit menu, names `git add -A`,
  `git write-tree`, `ghog exclude --list`, the saved
  `a.<slug>.step<x>.tmp.exclusions.txt`, `pw scope day --full=speed`,
  `--since`, and the return through `pw handoff check <x>`; `groundhog.md`
  says the loop follows the printed restart and repair lines and keeps its
  starting level and scope, and limits exit 8 to `speed`; `fix_slow_test.md`
  restarts with `ghog day --full=speed`; `process-draft.md` lists the
  test-scope menu after the branch-layout menu and the `- Test group:` line;
  `write-requirement.md` asks only when no choice was recorded;
  `prepare-release.md` names `ghog day --full=cov --whole-suite`; the
  write-plans template ready-to-run command points to `pw scope`; the
  step-handoff "Last gate" names the command with its selector; the
  specification lists the new decision rows and acceptance tests.
- Update the pinned phrases of the requestor instruction test (lines 86, 99
  and 101 today) to the new wording: the `speed` validation default in the
  effort scope, the exclusion evidence, the migration notice and the pending
  scope change at the gate. The reviewer, implementation-check and
  review-requestor pins were already moved by Step 6.
- Keep `test_instruction_structure_tdd.py` (649) green unedited: `groundhog.md`
  keeps exactly two `.\senv.bat &&` calls.

**Classes and behavior**:

- `implement-step.md`, `implement-missing-step.md`, `split-large-file.md`:
  verify with the command `pw scope day` prints (default level), describing
  check.bat plus the affected tests; `implement-step.md` gains the review-off
  `speed` pass with its staged-tree and exclusion comparisons, the journal
  record of each accepted exclusion, and the return through
  implementation-check on a changed or unverified comparison;
  `group-commits-msg.md` step 8 notes that, in the implement chain with review
  mode off, its choices are presented only after that pass and list each
  accepted exclusion.
- `write-plans.md` and `templates/write-plans.template.md`: the ready-to-run
  command, shared gate loop and completion criteria use `pw scope day` with no
  selector written into the plan; `templates/step-handoff.template.md` and
  `step-journal.md` record the gate command with its selector.
- `groundhog.md`: levels, scopes, the default skip line, restart lines as the
  only re-entry, exit 8 only at `speed`, and the objective of a direct loop
  stated through the level the caller asks for; `fix_slow_test.md` applies to
  `speed` walks.
- `code-review-requestor.md`, beyond the Step 6 arguments: the `speed`
  validation before every request in the effort scope, the exclusion evidence
  in the implementation report, the migration notice, the declared-set group
  statement, when a replacement needs `--scope-change-file`, the pending scope
  change at the gate, and no walk at a commit-ready answer.
- `prepare-release.md` and both prepare-release adapters:
  `ghog day --full=cov --whole-suite` at the green gate.
- `process-draft.md`: the test-scope menu (`Whole suite`, each valid group
  from `ghog groups`, `New group`, `Type something else`), the new-group
  creation validated by `ghog groups <name>`, the draft line next to
  `- Type:`, umbrella continuation included, no scope on an umbrella draft;
  `write-requirement.md` and its template carry `- Test group:` and ask only
  when the draft records none.
- `GROUNDHOG.md`, `tools/Pytest reset specs.md` (decision rows from Q71 and
  acceptance tests after AT19) and `DEVELOPMENT.md`: levels, resolution,
  marker and invalidation, closing and status keys, success and restart
  lines, the parallel timing step, the `.review-validation` migration note,
  `ghog exclude --list`, groups (declaration, matching, selection, grouped
  runs and gate, floor handling, per-scope markers, trade-off) and how to
  choose, change and remove an effort's group as opposed to a manual
  `--group` or `GHOG_GROUP`.
- `.agents/llm-shared/skills/fix-slow-test/SKILL.md` and
  `.agent/workflows/fix-slow-test.md`: descriptions name a `speed` walk
  exiting 8; bodies stay redirects (`rules/llm-specific-adapters.md`).

**Completion criteria**:

- The shared gate walk with `<gate-arguments>` = `day --full=cov --whole-suite`
  reports `exit=0`.
- `rg -n "full coverage pass" instructions` returns nothing.
- `rg -n "ghog day --full=cov --whole-suite" instructions/prepare-release.md .claude/skills/prepare-release .github/skills/prepare-release`
  lists every gate mention.
- `rg -n "Rework and review again|ghog day --full=speed" instructions/code-review-requestor.md`
  shows the gate label and the default validation.
- Markdown lint on every edited Markdown file reports `Summary: 0 issues`.

#### Step 7 -- addendums for the workflow instructions

Line-budget checkpoint:

- [ ] `tests/unit/tools/test_full_suite_levels_instructions/test_full_suite_levels_instructions_tdd.py`:
  before 0; safe; ceiling <= 650; expected about 320 (advisory).
- [ ] Updated instruction test: requestor 232 plus its Step 6 delta; safe;
  ceiling <= 650; small delta (advisory).
- [ ] `tests/unit/tools/test_instruction_structure/test_instruction_structure_tdd.py`:
  before 649; risk; ceiling <= 650; no edit.
- [ ] Markdown files carry no Python ceiling; `prepare-release.md` (1333
  lines) changes only its gate mentions.

Split guidance:

- New instruction contracts never go into `test_instruction_structure_tdd.py`;
  split the new package by instruction family if it nears 650.

Full workflow timing run readiness:

- Text-only tests; the shared walk covers them.

Time-gated status for Step 7:

- No perf gate is affected.

---

### Step 8. Prove every design acceptance case

#### Step 8 -- analysis and intent for the acceptance mapping

Issues to address:

- Steps 2 to 6 prove their components; the flows that cross groundhog, `pw`,
  the request renderer and the review exchange need end-to-end tests, and
  every row of the design's "Acceptance Cases" needs a named test.

Fix intent:

- Add an acceptance package driving the real modules through their public
  entry points on `tmp_path` Git repositories, faking only the pytest process
  boundary, and record a row-to-test mapping in the validation plan.

Expected outcome:

- Every design acceptance row maps to at least one passing test; the
  instruction-only rows (process-draft menus, write-requirement asking, the
  review-off procedure) map to Step 7 contracts plus the tool behavior they
  call.

Step framing:

- Design link: "Acceptance Cases for v0.13.0 full suite levels"; feature
  request gap 25; the round-3 reviewer note that the plan carries the
  capture, evidence-error and coverage cases.
- Execution checklist reference: "Shared execution command checklist for all
  v0.13.0 full_suite_levels steps".

#### Step 8 -- implementation for the acceptance mapping

**Files involved**:

- `tests/unit/tools/test_full_suite_levels_acceptance/__init__.py` (new, to be created).
- `tests/unit/tools/test_full_suite_levels_acceptance/conftest.py` (new, to be created).
- `tests/unit/tools/test_full_suite_levels_acceptance/test_full_suite_levels_review_acceptance_tdd.py` (new, to be created).
- `tests/unit/tools/test_full_suite_levels_acceptance/test_full_suite_levels_workflow_acceptance_tdd.py` (new, to be created).

**Tests first**:

- Review flows: a grouped effort renders `ghog day --full=speed --group=sentinel`
  with `test_scope`; the capture publishes to `paths.scope`; after the same
  group's patterns move from `tests/old/**` to `tests/new/**`, reviewer
  evidence `ghog affected --no-cov --scope-file=<paths.scope>` runs only the
  captured `tests/old` files and `pw progress` marks `pending change`; a
  deleted captured file gives exit 5 `bound scope unusable`; a legacy request
  reports `bound_scope: missing`; a replacement after a scope switch without
  `--scope-change-file` exits 2 and with it carries the block and validates in
  the new scope; a declared `.review-validation` with plain `ghog day` shows
  the migration notice; a grouped effort with a declared
  `ghog day --full=speed` claims no group proof; a valid unchanged `speed`
  snapshot makes the replacement validation a noop; a replacement rendered
  after only an exclusion changed shows `cov` proof in `test_scope` until a
  new `speed` walk restores it; an escalated grouped round that is archived
  keeps its capture among the archived evidence, and one that is resolved
  leaves no capture behind.
- Workflow flows: `pw scope` for grouped, ungrouped (with
  `GHOG_GROUP=sentinel` set), stale-draft and invalid-group efforts; scope
  switch back to a group whose marker is still valid reuses it; prepare-release
  operations name `--whole-suite` and a `GHOG_GROUP=sentinel` environment
  cannot narrow them; the review-off tool sequence (`ghog exclude --list`,
  a `speed` walk that only lowers a baseline, `--since` reporting
  `unchanged`; an added exclusion reporting `changed`; an unreadable saved
  listing reporting `unverified` with exit 5); a whole-suite `cov` gate on a
  grouped effort's prepare-release.
- No PBT: the properties live in Steps 1, 3 and 4.

**Classes and behavior**:

- Test-only step. `conftest.py` builds a `tmp_path` Git repository with
  `docs/v9.9.0/` effort documents, a `.ghog-groups` file and an artifact home,
  and reuses `groundhog_group_support.py` and the existing review-exchange
  test harness.

**Completion criteria**:

- The shared gate walk with `<gate-arguments>` = `day --full=cov --whole-suite`
  reports `exit=0`.
- The validation plan's Step 8 section holds a table mapping every design
  acceptance row to its test node ids.
- `rg -n "xfail" tests/unit/tools/test_groundhog_levels_perf` returns nothing.

#### Step 8 -- addendums for the acceptance mapping

Line-budget checkpoint:

- [ ] `test_full_suite_levels_review_acceptance_tdd.py`: before 0; safe;
  ceiling <= 650; expected about 520 (advisory).
- [ ] `test_full_suite_levels_workflow_acceptance_tdd.py`: before 0; safe;
  ceiling <= 650; expected about 420 (advisory).
- [ ] `conftest.py` and `__init__.py`: before 0; safe; ceiling <= 650;
  expected 180 and 7 (advisory).

Split guidance:

- Split the review file into publication and replacement modules if it nears
  650; keep fixtures in `conftest.py`.

Full workflow timing run readiness:

- The final walk runs the whole suite with coverage; the requestor's own
  `speed` validation, when review mode is on, then adds the sequential timing
  pass before the request.

Time-gated status for Step 8:

- No gate remains `xfail`; the five Step 0 gates keep their timeouts.

---

## Implementation decisions for v0.13.0 full_suite_levels

All twenty implementation questions are settled with option A, after two
review rounds. The nine steps can proceed in order from Step 0.

| Question | Decision | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | Keep Step 1 (pure level, proof and marker models plus the `commands.py` extraction, no behavior change) apart from Step 2 (one wiring switch), so the proof rules are proven alone and no interim marker rule is needed. | Plan goal; Steps 1 and 2 | Merging Steps 1 and 2 (one large step mixing refactor and behavior); shipping levels before proof (throwaway interim noop rule). |
| Q02 | Move the verdicts (`verdicts.py`) and the progress sink (`progress.py`) out of `commands.py`, mandatory target at most 500 lines; the report-assembly move stays as fallback guidance. | Confirmed facts (risk band); Step 1 implementation and addendums | Moving the report assembly first (import cycle with the emitters); moving all three at once (largest early churn). |
| Q03 | Move the requestor default, the prepare-release operations and the no-argument `ghog_cycle.bat` to explicit levels in Step 2, with the behavior switch; instruction wording follows later. | Step 2 fix intent and behavior | Moving them with the instructions in Step 7 (no full-suite proof for Steps 2 to 6); also editing the requestor wording in Step 2 (one more edit of the same file). |
| Q04 | This effort's own gate walks `day` for Steps 0 and 1, `day --full=cov` for Steps 2 and 3, and `day --full=cov --whole-suite` from Step 4. | Ready-to-run command templates; each step's completion criteria | The new default walk (no full-suite or coverage proof); `--full=speed` at every step (a timing pass today's gate does not pay). |
| Q05 | `day.walk` and `commands.run_tests_outcome` return a typed `RunOutcome(code, evidence)`; `run_day` and `run_tests` stay integer wrappers. | Step 2 classes and behavior (`evidence.py`, `day`, `commands`, `status`) | Changing every integer return (wide test churn); parsing the printed closing line (status coupled to report text). |
| Q06 | Apply `COVERAGE_FILE` through `StreamConfig.env_overrides` around the spawn only, restored in a `finally` block; tested for a present and an absent variable and a raising factory. | Confirmed facts (process fakes); Step 4 runner behavior and tests | A third `popen_factory` parameter (every fake changes); a generated coverage configuration (replaces the project's `omit` and `branch`). |
| Q07 | `Invocation.level` defaults to `None`, resolved by `levels.effective_level` to the command default (`speed` for `full`, `none` otherwise). | Confirmed facts (directly built invocations); Step 1 levels; Step 2 context | Default `speed` (wrong restart lines for repair commands); a required field (every construction changes). |
| Q08 | The captured-scope schema, fingerprint and validator live in a shared `tools/scope_capture.py`, imported by groundhog, the renderer and the review core. | What does not exist yet; Step 3 implementation | A module inside `tools/groundhog` (review core coupled to groundhog); an opaque capture checked by fingerprint only (no completeness check). |
| Q09 | `paths.scope` is a registered artifact outside `fixed_paths`, with its own module `tools/review_exchange_scope.py`; `review_status.py` and the store stay untouched. | Confirmed facts (review artifacts); Step 6 models and exchange behavior | Adding a seventh kind to `fixed_paths` and `ArtifactKind` (splits of three at-risk files). |
| Q10 | The `pw progress` `bound` line reads the coordination record and the capture in `prompt_workflow_scope.py`, through the shared `scope_capture` validator. | Step 6 `pw progress` behavior | Threading the fingerprint through the `ExchangeStatus` projection (forces a split of `review_status.py`). |
| Q11 | The group gate reads the scope-owned data file through the coverage Python API in groundhog's process; unreadable or incompatible data is an exit-5 evidence error. | Confirmed facts (runtime); Step 4 `group_coverage.py` | A `coverage report` child in the project environment (extra process, text parsing); a pytest-cov JSON export (extra report flags). |
| Q12 | New groundhog tests use one-level `tests/unit/tools/test_groundhog_<module>/` packages beside the existing flat files. | Current test-tree validation snapshot; every step's file list | A `tests/unit/tools/groundhog/` sub-tree (two roots); new flat files (breaks the test convention). |
| Q13 | Step 0 adds five strict `xfail` gates that count spawned children and tree walks under a five-second timeout, owned by Steps 2 and 4. | Shared timeout target policy; Step 0 | Wall-clock timeouts on large synthetic trees (slow, noisy); no Step 0 (cost contracts unguarded). |
| Q14 | Extract `tools/groundhog/detach.py` from `status.py` only when a step would pass this plan's 550-line trigger; 650 stays the only repository failure. | Steps 2 and 4 split guidance | Extracting in Step 2 before the need is known; letting the file grow to 650. |
| Q15 | Keep broad instruction and manual updates in Step 7; ship the minimum invocation contracts with the step that requires them (`run-pw.md` in Step 5; renderer output, publication input and reviewer `--scope-file` evidence in Step 6). | Steps 5, 6 and 7 | Updating every instruction in the step shipping its behavior (large documents edited repeatedly); deferring required arguments to Step 7 (Step 6 review cannot render). |
| Q16 | A dedicated Step 8 in-process acceptance package covers cross-component flows and maps every design acceptance row to tests, beside the per-step groundhog acceptance packages. | Step 8 | Real launchers under `tests/acceptance/` (environment-dependent); no Step 8 (flows needing every component untestable earlier). |
| Q17 | `pw scope` refuses ghog arguments already carrying a selector, in the equals and the separated forms, naming the argument. | Step 5 tests and behavior | Appending anyway (groundhog exit 5 later); silently replacing the caller's selector. |
| Q18 | The capture follows the coordination record on every exit: removed by `complete`, `complete --force` and `resolve`, archived (new `scope.json` archive kind) by `archive`; each tested on its artifact set. | Step 6 capture lifecycle tests and behavior | Removing it only in `complete` and `force_complete` (resolved or archived escalations strand it); only in `complete`. |
| Q19 | `--scope-capture-output` is required for renderer CLI calls; Step 6 updates every caller test and the live requestor and reviewer instructions. | Step 6 renderer, caller tests and instruction contracts | An optional output (requests without a bound scope reach the reviewer as missing evidence). |
| Q20 | Request evidence uses the walk's effective-proof rule (`proof.effective_saved` through `snapshot.effective_proof`): scope, fingerprint and digest must match, and a timing mismatch caps `speed` at `cov`. | Steps 1, 2 and 6; Step 8 review flows | Checking only scope, fingerprint and digest (stale `speed` claims); reporting raw marker fields to the reviewer. |
