# Code review transcript for v0.14.0

- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor - Step 1

- Recorded: 2026-11-08T14:39:29+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: unrecorded
- Implementation step: 1
- Outcome: request

### Review identity for step 1 shared_lifecycle_gate (round 1)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
Implementation step: 1
Review round: 1

### Code review evidence for step 1 shared_lifecycle_gate (round 1)

request_index_tree: 70ab8f8a6ee347df96118f83511e9c3113dbfdba
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: fix(testmon): hash source without invoking Git
group 1 path: tests/testmon_monitoring.py
group 1 path: tests/unit/tools/test_testmon_monitoring/__init__.py
group 1 path: tests/unit/tools/test_testmon_monitoring/test_testmon_monitoring_tdd.py
group 2: test(lifecycle): trim measured test overhead
group 2 path: tests/unit/tools/release_workflow/test_configuration/test_configuration_pbt.py
group 2 path: tests/unit/tools/test_full_suite_levels_acceptance/test_full_suite_levels_review_acceptance_tdd.py
group 2 path: tests/unit/tools/test_groundhog_durations_pbt.py
group 2 path: tests/unit/tools/test_codex_plugin_package/test_codex_plugin_package_tdd.py
group 2 path: tests/unit/tools/test_isolate_logos.py
group 2 path: tests/unit/tools/test_review_resume/test_review_resume_selection_tdd.py
group 3: feat(lifecycle): extract standalone timing gate
group 3 path: tools/pytest_plugins/__init__.py
group 3 path: tools/pytest_plugins/llm_shared_lifecycle_gate.py
group 3 path: pyproject.toml
group 3 path: tests/unit/tools/test_lifecycle_policy.py
group 3 path: tests/unit/tools/test_lifecycle_cpu_band.py
group 3 path: tests/unit/tools/shared_lifecycle/__init__.py
group 3 path: tests/unit/tools/shared_lifecycle/inline_session.py
group 3 path: tests/unit/tools/shared_lifecycle/test_gate_contract/__init__.py
group 3 path: tests/unit/tools/shared_lifecycle/test_gate_contract/test_gate_contract_tdd.py
group 3 path: tests/unit/tools/shared_lifecycle/test_gate_contract/test_gate_contract_pbt.py
group 4: docs(shared_lifecycle_gate): record step 1 validation
group 4 path: docs/v0.14.0/review.feature-request.v0.14.0.shared_lifecycle_gate.md
group 4 path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md
staged path: docs/v0.14.0/review.feature-request.v0.14.0.shared_lifecycle_gate.md
staged path: pyproject.toml
staged path: tests/testmon_monitoring.py
staged path: tests/unit/tools/release_workflow/test_configuration/test_configuration_pbt.py
staged path: tests/unit/tools/shared_lifecycle/__init__.py
staged path: tests/unit/tools/shared_lifecycle/inline_session.py
staged path: tests/unit/tools/shared_lifecycle/test_gate_contract/__init__.py
staged path: tests/unit/tools/shared_lifecycle/test_gate_contract/test_gate_contract_pbt.py
staged path: tests/unit/tools/shared_lifecycle/test_gate_contract/test_gate_contract_tdd.py
staged path: tests/unit/tools/test_codex_plugin_package/test_codex_plugin_package_tdd.py
staged path: tests/unit/tools/test_full_suite_levels_acceptance/test_full_suite_levels_review_acceptance_tdd.py
staged path: tests/unit/tools/test_groundhog_durations_pbt.py
staged path: tests/unit/tools/test_isolate_logos.py
staged path: tests/unit/tools/test_lifecycle_cpu_band.py
staged path: tests/unit/tools/test_lifecycle_policy.py
staged path: tests/unit/tools/test_review_resume/test_review_resume_selection_tdd.py
staged path: tests/unit/tools/test_testmon_monitoring/__init__.py
staged path: tests/unit/tools/test_testmon_monitoring/test_testmon_monitoring_tdd.py
staged path: tools/pytest_plugins/__init__.py
staged path: tools/pytest_plugins/llm_shared_lifecycle_gate.py
```

### Validation scope for step 1 shared_lifecycle_gate (round 1)

Validation scope: the whole suite.

### Requestor assessment for step 1 shared_lifecycle_gate (round 1)

Step 1 is fully implemented according to the static implementation check in
`docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md`.

The standalone gate has only stdlib/pytest imports, a pre-refusal Python 3.12
guard and literal contract version, strict read-only artifact discovery and
unchanged timing, schema-1 proof, exception and controller-report contracts.
The legacy suite enforcer remains unchanged until Step 3. No Step 2 work is
included.

The default `ghog day --whole-suite` passed at 14:15:03 on 2026-11-08.
It proved static checks and affected tests only. Full speed/coverage evidence
is recorded in the implementation report after its separate required walk:
`ghog day --full=speed --whole-suite` passed at 14:35:09 with 5,780 tests,
100% coverage, zero outliers, warnings, xfails and exclusions.
No test command was run inside implementation-check, and that static check
claims no measured percentage. Coverage source remains `tools`, including the
new policy. Suite helper code under `tests` is outside that source scope.

Fresh physical counts: gate 602, inline helper 53, contracts 263/54, redirected
legacy tests 111/363. Every changed Python file is below 650 lines.
Clocks and report events are constant time, record processing is linear, and
inherited deterministic summary/record sorts remain O(n log n) outside the
hot path. No architecture or feature-integrity issue was identified.

Executed evidence is Windows/Python 3.13. Source parsing, guarded simulated
version refusal and static 3.12 targets do not imply executable 3.12 or other
platform evidence. Continuity tests use synthetic schema-1 records; Step 7
still owns the real-checkout continuity check.

### Implementation report for step 1 shared_lifecycle_gate (round 1)

The new `tools/pytest_plugins/llm_shared_lifecycle_gate.py` combines the existing
timing policy and record model without runtime shared-helper imports or audit
installation. It retains CPU from before setup through teardown cleanup,
phase wall aggregation, report properties and diagnostics, proof/drift rules,
current-ceiling eligibility, accepted exceptions, unknown document fields,
schema 1, controller-only collection and one session write. The strict copied
artifact parser accepts ConfigParser DEFAULT inheritance, rejects invalid or
escaping homes and requires exact ignore bytes without creating a home.

Dedicated pytest, Pyright and ty import discovery plus Ruff py310/Pyright 3.12
targets support the standalone module. Original timing/record assertions are
unchanged apart from imports. Added deterministic and bounded property tests
cover artifact failures, synthetic continuity, settings precedence, guarded
registration in both orders, usage-error refusal, version/source boundaries,
proof transitions and serialization. The inline runner restores host state,
bypasses the host rewrite hook for plain child assertions and cleans newly
imported project modules.

Verification uncovered an existing Testmon Git hash subprocess during audited
reporting. Its adapter now uses Testmon's ordinary source/hash fallback for
both imported bindings; regression tests check live bindings, identical hash
and source, missing files and refusal to use the Git seam.

Named lifecycle CPU offenders were profiled and shortened: finite key strategies
avoid Unicode-table startup; ranked scalar strings avoid dictionary uniqueness
rejection without narrowing the bounded domain or budget; PNG fixtures remain
real but smaller; resume role selection accepts explicit parsed arguments;
proof production caches fixed source digests and disables irrelevant tiny-suite
collection probes while keeping both stages, SQLite evidence and rendering live.
The embedded runner omits the unused unraisable-exception plugin's repeated
full-process garbage collection. The flagged package-export test was left
unchanged after its cold profile showed no import hotspot. No exception or
exclusion baseline was added or raised.

The first full-speed walk later found one shipped-package wall overrun
(1.854680s, CPU 0.078125s). Focus passed; isolated profiling measured the actual
package body at 0.0212s and dependency-enabled profiling showed substantial
fingerprinting work, including an unrelated workflow module used only for
root lookup. The test now locates the shipped package through the package
module itself, preserving real validation and both assertions. The 51-test
focus passed. The isolated profile did not reproduce the full-suite wall delay.

The incidental review-document reflow prevents an unintended numbered list
without changing wording. The validation plan records Step 1 only and keeps
Steps 2-7 pending. No record was deleted or migrated, no commit has been made,
and no push is authorized.

Mandatory review validation `ghog day --full=speed --whole-suite` completed at
2026-11-08T14:35:09+01:00. Canonical status confirms done/exit 0, full=speed,
proof=speed, scope=whole. All 5,780 tests passed, configured coverage is 100%,
and warnings, xfails, duration outliers and exclusions are zero. No accepted
timing exception or exclusion baseline was added or raised. The source scope
is tools, including the standalone module; tests helpers are outside it.

Writer notes: `.reviews/a.shared_lifecycle_gate.step1.journal.md` and `.reviews/a.shared_lifecycle_gate.step1.handoff.md`.

### Change summary for step 1 shared_lifecycle_gate (round 1)

The staged set has 21 paths in four ordered root `a.commit` groups:

1. `fix(testmon): hash source without invoking Git`: `tests/testmon_monitoring.py`,
   `tests/unit/tools/test_testmon_monitoring/__init__.py` and
   `tests/unit/tools/test_testmon_monitoring/test_testmon_monitoring_tdd.py`.
2. `test(lifecycle): trim measured test overhead`:
   `tests/unit/tools/release_workflow/test_configuration/test_configuration_pbt.py`,
   `tests/unit/tools/test_full_suite_levels_acceptance/test_full_suite_levels_review_acceptance_tdd.py`,
   `tests/unit/tools/test_groundhog_durations_pbt.py`,
   `tests/unit/tools/test_codex_plugin_package/test_codex_plugin_package_tdd.py`,
   `tests/unit/tools/test_isolate_logos.py` and
   `tests/unit/tools/test_review_resume/test_review_resume_selection_tdd.py`.
3. `feat(lifecycle): extract standalone timing gate`: `pyproject.toml`,
   `tools/pytest_plugins/__init__.py`,
   `tools/pytest_plugins/llm_shared_lifecycle_gate.py`,
   `tests/unit/tools/test_lifecycle_policy.py`,
   `tests/unit/tools/test_lifecycle_cpu_band.py`,
   `tests/unit/tools/shared_lifecycle/__init__.py`,
   `tests/unit/tools/shared_lifecycle/inline_session.py`,
   `tests/unit/tools/shared_lifecycle/test_gate_contract/__init__.py`,
   `tests/unit/tools/shared_lifecycle/test_gate_contract/test_gate_contract_tdd.py`
   and `tests/unit/tools/shared_lifecycle/test_gate_contract/test_gate_contract_pbt.py`.
4. `docs(shared_lifecycle_gate): record step 1 validation`:
   `docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md` and
   `docs/v0.14.0/review.feature-request.v0.14.0.shared_lifecycle_gate.md`.

The formatted plan passes the canonical readiness checker. Both staged
Markdown files pass markdownlint-cli2. The review transcript created on
publication is reserved for its eventual bounded residual commit.

### Writer response for step 1 shared_lifecycle_gate (round 1)

Writer response:

This is the first implementation review round for Step 1. There is no earlier
code-review feedback to accept or dispute. Please assess the exact staged step
and the incidental verification repairs against the retained assertions,
source/record boundaries and complete commit grouping. No Step 2 audit or
later executable compatibility evidence is claimed.

### Reviewer focus for step 1 shared_lifecycle_gate (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-1-round-1 -->

### LLM nature completion for reviewer (exchange 1)

Recorded nature: `claude`

Completed artifacts:

- `.reviews/a.review-active.code.code.v0.14.0.shared_lifecycle_gate.md`
- `.reviews/a.review-requested.code.v0.14.0.shared_lifecycle_gate.md`

<!-- review-entry-id: llm-nature-completion-reviewer-exchange-1 -->

## Round 1 by reviewer - Step 1

- Recorded: 2026-11-08T15:01:58+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 1
- Outcome: answer

### Assessed index identity for step 1 shared_lifecycle_gate (exchange 1) (round 1)

Baseline index tree: 70ab8f8a6ee347df96118f83511e9c3113dbfdba

Assessed index tree: 70ab8f8a6ee347df96118f83511e9c3113dbfdba

### Implementation check for step 1 shared_lifecycle_gate (exchange 1) (round 1)

Result:

Yes. Step 1 has been fully implemented.

`tools/pytest_plugins/llm_shared_lifecycle_gate.py` exists with only stdlib and
pytest imports. It carries the timing policy, the schema-1 record model, the
measurement hooks, the controller collector and a stdlib copy of the artifact
lookup. The two legacy lifecycle test modules now import that canonical module
and change nothing else. The new `test_gate_contract` folder and the shared
`inline_session.py` helper cover every test obligation the plan lists.

Reviewer comparison with the legacy sources: apart from the import block, the
`_ABOUT` text and the artifact lookup, the gate matches
`tests/lifecycle_cpu_record.py` and `tests/simulation_policy.py` line for line.
The audit hook, `_ACTIVE`, `reject_process` and the `pytest_runtest_protocol`
wrapper are left out, as Step 2 requires. `NodeState`, `advance`, `LifecycleRecord`,
`parse_record`, `render_record`, `LifecycleGate`, `BandCollector`, the four ini
keys with their defaults, the failure text, wall aggregation, report-hook CPU
inclusion, the `and not failed` guard and the controller-only registration are
unchanged.

The copied `artifact_record_path` follows `ReviewArtifactConfiguration.load`
rule for rule. It reads the same strict ConfigParser declaration, including the
DEFAULT inheritance. It applies the same spelling refusals and the same
physical containment through `resolve(strict=False)` and `relative_to`. It
refuses the repository root and requires an existing directory with exact
`*\n` ignore bytes, as the legacy `_unignored_home` callback did. It starts no
Git process and never creates a home. Every legacy failure path, including an
unreadable root, declaration or ignore file, still yields no record path.

The version guard runs only `sys` and `pytest` imports, the comparison and a
`pytest.UsageError` naming the module and 3.12. `LOADER_CONTRACT_VERSION = 1`
is a module-level integer literal after the guard. The `pyproject.toml` changes
match the plan:

- the module directory is exposed to pytest, Pyright and ty;
- Ruff `per-file-target-version` is set to py310 and Pyright to 3.12 for
  `tools/pytest_plugins`;
- coverage source stays `tools`, with no plugin omission.

Architecture: the gate is a self-contained adapter over pytest hooks and one
JSON file. It imports no suite package and no shared runtime helper. Importing
it has no side effect beyond definitions, so the test imports register no
second collector. The legacy enforcer stays wired through `tests/conftest.py`
until Step 3. The `tools/pytest_plugins/__init__.py` marker also makes a
dotted import path possible, but nothing uses it; the plan asks for the marker.
No architecture issue needs addressing.

Performance: clock samples, limit lookup and report handling are constant time
per event. Record parsing, advancement and rendering are linear. Key, lost-proof
and summary sorting remain the inherited O(n log n) at session end, outside the
per-test path. Configure reads the record once and the controller writes once.
No performance issue needs addressing.

Unit test coverage: the gate is inside the `tools` coverage source. The
requestor's `ghog day --full=speed --whole-suite` at 14:35:09 reported 100%.
Static reading agrees:

- the legacy modules reach every policy, record and hook function through the
  `policy`/`band` aliases;
- the contract tests reach every branch of `_artifact_value`, `_unsafe_home` and
  `artifact_record_path`;
- the version-refusal test runs the module source under its own file name, so
  the refusal line is measured too.

Helpers under `tests` are outside the gate's scope. `run_inline`, `source_sha`,
`_decoded_node` and the property-decoding helpers are each referenced by a
test. No unit-tested class needs completing, and no top-level symbol outside
the coverage scope is unreferenced.

Feature integrity: record name, schema 1, unknown fields, the accepted exception
content and current-ceiling eligibility are preserved. The synthetic round-trip
test proves it. The legacy enforcer still owns llm-shared's live record until
Step 3, so no record is migrated or deleted. The incidental Testmon change keeps
dependency evidence. Testmon's fallback hash differs from the Git blob SHA only
for non-ASCII files, which can cost one wider reselection. The requestor's full
walk already paid it: this round's `ghog affected` found nothing to run. No
reporting capability is impaired.

Validation plan effects:

No reviewer edit. The writer's Step 1 rows in
`docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md` agree with
this assessment:

- the status sentence is exactly `Yes. Step 1 has been fully implemented.`;
- every check sub-section ends with its yes-or-no phrase;
- the recorded physical counts match a fresh sample (gate 602, inline helper
  53, contracts 263/54, legacy tests 111/363, largest other test 360);
- no `Missing work for Step 1` section is needed.

The document-level line correctly stays `No, it is not implemented` while
Steps 2-7 are pending. The staged diff of that file touches only the opening
theme sentence and the Step 1 section. Reviewer mode completed no umbrella row,
and the effort has none.

### Pre-repair mandatory checks and coverage for step 1 shared_lifecycle_gate (exchange 1) (round 1)

No repair was made, so the pre-repair and assessed states are the same index
tree, `70ab8f8a6ee347df96118f83511e9c3113dbfdba`, which equals the
request-time tree.

Requestor evidence, not repeated: `ghog day --whole-suite` passed at
2026-11-08T14:15:03+01:00. `ghog day --full=speed --whole-suite` passed at
2026-11-08T14:35:09+01:00 with 5,780 tests, 100% configured coverage and zero
failures, warnings, xfails, outliers and exclusions.

Reviewer evidence, each run once from the project root with the worktree
environment:

- `ghog check` finished at 2026-11-08T14:53:53+01:00 with `state=done`,
  `exit=0`, `fail=0`, `warn=0`; `check.bat` reported all checks passed,
  including the EOF check.
- `ghog affected --no-cov --scope-file=.reviews/a.review-scope.code.v0.14.0.shared_lifecycle_gate.json`
  finished at 2026-11-08T14:55:23+01:00 with `exit=0`. Testmon found nothing
  affected since the requestor's last walk, so 0 tests ran. This confirms the
  reviewed tree is the one the requestor's green full-speed walk measured.

Coverage was assessed statically, as reviewer mode requires. No `ghog day` or
`ghog full` ran in this review.

### Resolved validation set and sources for step 1 shared_lifecycle_gate (exchange 1) (round 1)

The request carries one command, `ghog day --full=speed --whole-suite`, from
the `project` source. The repository has no `.review-validation` declaration,
so the built-in default `ghog day --full=speed` is completed with the bound
whole-suite selector. The request lists no plan or request additions. The
requestor owns this set and reports it green at 2026-11-08T14:35:09+01:00. The
reviewer did not run it.

### Resolver drift and direction for step 1 shared_lifecycle_gate (exchange 1) (round 1)

No drift. The current resolver input gives the same single command from the
same source: no `.review-validation` declaration, the built-in default
completed with `--whole-suite` for the bound scope (fingerprint `686958cd`),
and no plan or request addition. Neither direction adds or drops a command.

### Repository state around validation for step 1 shared_lifecycle_gate (exchange 1) (round 1)

The validation path set holds the 21 staged paths plus the root `a.ghog.log`
written by the reviewer evidence commands. It was captured before assessment
and again after both ghog commands.

- `validation-state compare` reported `acceptable: true`, no tracked or
  untracked path changed, and one ignored path changed (`a.ghog.log`).
- `umbrella-digest compare` reported not applicable and unchanged; the request
  states `Umbrella draft: none`.
- The live index tree after assessment is still
  `70ab8f8a6ee347df96118f83511e9c3113dbfdba`.
- The only untracked file is the versioned review transcript
  `docs/v0.14.0/review.code.v0.14.0.shared_lifecycle_gate.md`, created by the
  exchange and reserved for the requestor's residual commit.

### Repair inventory for step 1 shared_lifecycle_gate (exchange 1) (round 1)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 1 shared_lifecycle_gate (exchange 1) (round 1)

An independent `commit-plan-check.bat --format json` rerun on the received
state exited 0 with `state: valid`, `ready: true` and no diagnostics. It listed
the same 21 staged paths and the same four ordered groups as the request
evidence:

1. `fix(testmon): hash source without invoking Git`, 3 paths.
2. `test(lifecycle): trim measured test overhead`, 6 paths.
3. `feat(lifecycle): extract standalone timing gate`, 10 paths.
4. `docs(shared_lifecycle_gate): record step 1 validation`, 2 paths.

Reviewer judgment on grouping and scope: every staged path belongs to exactly
one group, and each subject matches its diff. The ordering runs from least to
most dependent. Groups 1 and 2 stand alone and need nothing from the gate;
group 3 holds the plan's ten Step 1 files; group 4 records the result.

The Testmon adapter, the six test trims and the one-paragraph reflow sit
outside the plan's Step 1 file list. They are writer verification repairs
needed for the required green day walk, and each sits in its own group with an
accurate subject, so they do not blur the feature commit. The trims keep their
assertions and domains:

- the cached `source_digest` receives the hashable inventory tuple;
- the ranked-string encoding is bijective over 1..12 scalar characters, and a
  new edge test pins both ends;
- the PNG case still drives the real codecs.

`a.commit` needs no amendment. The bodies match the diffs, and no AI
attribution trailer is present.

### Findings and boundaries for step 1 shared_lifecycle_gate (exchange 1) (round 1)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 1 shared_lifecycle_gate (exchange 1) (round 1)

No change is required for Step 1. Keep the staged set and `a.commit` as they
are, and take the human convergence choice from the gate.

For later steps, carry two observations that need no action now:

- Step 3 removes `tests/simulation_policy.py` and `tests/lifecycle_cpu_record.py`.
  Until then they enforce the own suite with no direct unit test, because their
  former tests now target the canonical module. Do not change either legacy
  file before Step 3 without restoring a test for it.
- Step 4 preflight should import the gate only by its canonical name,
  `llm_shared_lifecycle_gate`. The dotted path through
  `tools/pytest_plugins/__init__.py` would create a second module object with
  separate stash keys.

### Decision rationale for step 1 shared_lifecycle_gate (exchange 1) (round 1)

All six readiness-floor results pass:

- Identity: the envelope, the readable identity, the plan, step 1, round 1,
  occurrence 1, `Umbrella draft: none` and the request-time index tree
  `70ab8f8a` all agree with the live exchange and index.
- Completeness: every Step 1 file, test obligation, guard, contract literal
  and static target in the plan is present. The extracted policy matches the
  legacy sources, and the copied lookup matches the shared parser.
- Validation and coverage: the requestor's mandatory full-speed walk is green
  at 100% coverage. Reviewer `ghog check` and `ghog affected --no-cov` both
  exited 0, and the static coverage reading finds no gap.
- Staged attribution: all 21 staged paths are writer work in four accurate
  groups. The reviewer staged nothing and edited nothing tracked.
- Findings: none are unresolved or carried, and no boundary-crossing work
  remains.
- `a.commit`: the independent checker is valid and ready with no diagnostics,
  and the reviewer's grouping judgment agrees.

This round made no repair, substantive or polishing. The request's review-scope
paragraph invites safe repairs, but it carries no literal `Human guidance:`
block, so the reviewer instruction keeps the reviewer to findings only. None
were needed.

The recommendation is commit-ready and advisory only. It does not authorize a
commit.

### Final reviewer decision for step 1 shared_lifecycle_gate (exchange 1) (round 1)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-1-round-1 -->

## Round 1 by human - Step 1 - human-confirmation

- Recorded: 2026-11-08T15:38:49+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 1
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-1 -->

## Round 1 by requestor - Step 2

- Recorded: 2026-11-08T18:18:53+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: unrecorded
- Implementation step: 2
- Outcome: request

### Review identity for step 2 shared_lifecycle_gate (round 1)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
Implementation step: 2
Review round: 1

### Code review evidence for step 2 shared_lifecycle_gate (round 1)

request_index_tree: 1d825108726149d10bb328bfe2eee9e9c9fb7a0d
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: perf(tests): reuse parent capture in child sessions
group 1 path: tests/unit/tools/shared_lifecycle/inline_session.py
group 2: feat(audit): isolate process permissions
group 2 path: tools/pytest_plugins/llm_shared_process_audit.py
group 2 path: tests/unit/tools/shared_lifecycle/test_audit_declarations/__init__.py
group 2 path: tests/unit/tools/shared_lifecycle/test_audit_declarations/test_audit_declarations_tdd.py
group 2 path: tests/unit/tools/shared_lifecycle/test_audit_ownership/__init__.py
group 2 path: tests/unit/tools/shared_lifecycle/test_audit_ownership/test_audit_ownership_tdd.py
group 3: docs(shared_lifecycle_gate): record step 2 validation
group 3 path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md
staged path: tests/unit/tools/shared_lifecycle/inline_session.py
staged path: tests/unit/tools/shared_lifecycle/test_audit_declarations/__init__.py
staged path: tests/unit/tools/shared_lifecycle/test_audit_declarations/test_audit_declarations_tdd.py
staged path: tests/unit/tools/shared_lifecycle/test_audit_ownership/__init__.py
staged path: tests/unit/tools/shared_lifecycle/test_audit_ownership/test_audit_ownership_tdd.py
staged path: tools/pytest_plugins/llm_shared_process_audit.py
```

### Validation scope for step 2 shared_lifecycle_gate (round 1)

Validation scope: the whole suite.

### Requestor assessment for step 2 shared_lifecycle_gate (round 1)

Step 2 is fully implemented. The static implementation-check records
"Yes. Step 2 has been fully implemented" in the paired validation plan.

The standalone audit uses stdlib and pytest only, with an early Python 3.12
refusal and literal loader contract version. It preserves all nine audit
events throughout setup, call and teardown independently of lifecycle timing.
One process-lifetime dispatcher survives reloads and alias imports. Session
state, fixture ownership and exclusive permission credit remain isolated.

Tests exercise marker and fixture declaration validation, unused entries,
registry identity and conflicts, nested sessions, cache/dependency boundaries,
thread and copied-context isolation, setup/cleanup failure unwind, and adapter
capability refusal/restoration. Static checks, affected tests, the resolved
day and covered whole-suite day passed; covered day measured 100% tools
coverage, zero failures, warnings or xfails. Required speed validation is
recorded in the implementation report before request publication.

The event path performs no IO or registry scans. Declaration validation uses
one registry index; final adapter restoration only replaces owned callables.
Physical lines: audit 376, declaration tests 298, ownership tests 272, inline
helper 54, package markers 1 each; every Python file is below 650.

The legacy own-suite enforcer remains unchanged. Distributed validation,
report rendering and migration belong to Step 3; real process and executable
Python 3.12 compatibility evidence remain later plan obligations.

### Implementation report for step 2 shared_lifecycle_gate (round 1)

Implemented independent audit sessions in
`tools/pytest_plugins/llm_shared_process_audit.py` and finite declaration and
ownership matrices in the two new test packages.

The sys-owned hub attaches once per config and installs one lifetime audit
dispatcher. Nested inactive sessions mask outer enforcement; detach restores
the outer state and eventually only the adapter's own pytest methods.
Declarations require function/case markers with nonempty consistent reasons
or a plain dictionary of actual decorated fixture objects. Validation includes
unused entries, loaded conftests, empty modules and unique registry matches.

Fixture execute masks the requester while resolving dependencies or cache;
the actual setup hook enters setup ownership, and finish enters cleanup
ownership. Thread-local live tokens unwind even on errors. Specific fixture
permissions receive exclusive credit; unexempt function fixtures may use the
test permission, while broader fixture scopes cannot. In-memory permission
records and stable identities prepare Step 3 reporting.

The first affected run identified a lifecycle CPU failure in redundant Windows
capture initialization within an embedded pytest session. Profiling isolated
colorama/console initialization. Disabling child capture preserves carrying
suite capture and all output assertions. Diagnostic cold CPU decreased from
0.312 s to 0.172 s. Affected repair, resolved whole-suite day and covered day
then passed. The covered day finished with fail=0, warn=0, xfail=0, cov=100.

The required `ghog day --full=speed --whole-suite` passed at
2026-11-08T18:16:45+01:00 with exit=0, cov=100, proof=speed and zero failures,
warnings, xfails, outliers or exclusions. All static checks passed.

Its first attempt exposed 0.125s lifecycle CPU in a combined reload/alias/
nested-session test. Profiling identified repeated pytest configuration and
collection across two embedded sessions. Reload and alias assertions now have
independent tests, and nesting attaches the carrying pytest config as the
outer audit session while running the real embedded child and protocol hooks.
All original assertions remain. The passing covered speed walk measured
0.03125s CPU for nesting and 0.015625s each for reload and alias, below the
unchanged 0.100s ceiling.

No exclusions were accepted or raised. No production test or fixture process
permissions were introduced. Real executable process/worker evidence is not
claimed by these process-free own-suite tests.

Writer notes: `.reviews/a.shared_lifecycle_gate.step2.journal.md` and
`.reviews/a.shared_lifecycle_gate.step2.handoff.md`.

### Change summary for step 2 shared_lifecycle_gate (round 1)

The staged set contains seven paths:

- `tests/unit/tools/shared_lifecycle/inline_session.py`
- `tools/pytest_plugins/llm_shared_process_audit.py`
- `tests/unit/tools/shared_lifecycle/test_audit_declarations/__init__.py`
- `tests/unit/tools/shared_lifecycle/test_audit_declarations/test_audit_declarations_tdd.py`
- `tests/unit/tools/shared_lifecycle/test_audit_ownership/__init__.py`
- `tests/unit/tools/shared_lifecycle/test_audit_ownership/test_audit_ownership_tdd.py`
- `docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md`

Root `a.commit` has three ordered groups:

1. `perf(tests): reuse parent capture in child sessions`: inline helper.
2. `feat(audit): isolate process permissions`: audit and new test packages.
3. `docs(shared_lifecycle_gate): record step 2 validation`: validation plan.

The canonical commit-plan checker reports valid, ready=true and no diagnostics.
The validation Markdown passes markdownlint. No Step 2 commit has been made.

### Writer response for step 2 shared_lifecycle_gate (round 1)

Writer response:

This is the first Step 2 review round. There is no earlier Step 2 feedback,
accepted repair, reversal or disagreement.

### Reviewer focus for step 2 shared_lifecycle_gate (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-2-round-1 -->

## Round 1 by reviewer - Step 2

- Recorded: 2026-11-08T18:38:07+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 2
- Outcome: answer

### Assessed index identity for step 2 shared_lifecycle_gate (exchange 1) (round 1)

Baseline index tree: 1d825108726149d10bb328bfe2eee9e9c9fb7a0d

Assessed index tree: 1d825108726149d10bb328bfe2eee9e9c9fb7a0d

### Implementation check for step 2 shared_lifecycle_gate (exchange 1) (round 1)

Result:

No. Step 2 is not fully implemented. Four correctness gaps against the
settled design remain; the unresolved findings list them.

What is in place and matches the plan:

- `tools/pytest_plugins/llm_shared_process_audit.py` imports only stdlib and
  pytest. Its Python 3.12 refusal runs only the `sys` and `pytest` imports,
  the comparison and the identifying `pytest.UsageError`.
  `LOADER_CONTRACT_VERSION = 1` is a module-level integer literal after the
  guard. The module owns no lifecycle setting, record or CPU-band collector.
- The nine process events match the legacy `_PROCESS_EVENTS` set. Rejection
  names the carrying test and the event.
- One hub stored on `sys` survives reload and alias imports. It installs the
  audit hook once and attaches each configuration once.
- The adapter wraps only `FixtureDef.execute` and `FixtureDef.finish`, after
  checking both signatures and `addfinalizer`. It restores them on the last
  detach, and only while they still hold its wrappers.
- Traced against pytest 9.1.0: `execute` masks the requester while it resolves
  dependencies and the cache. The `pytest_fixture_setup` wrapper enters the
  fixture's own setup. `finish` re-enters the finalized fixture's ownership
  for yield teardown and registered finalizers. A dependent's partial `finish`
  switches to that dependent. The thread-local token stack unwinds in
  `finally`, so another thread or a copied context gets no fixture permission.
- Precedence and credit follow the design table: a declared fixture's own
  permission first, then the test permission only for function-scoped or
  ownerless work. Each event credits exactly one permission.
- Validation indexes the registry once and covers the original module and
  class marker levels, case marks, malformed and empty reasons, unused and
  imported fixture entries, ambiguity and conflicting reasons.
- Every Step 2 file is present. The tests cover each obligation the plan
  lists, use synthetic events and real in-process fixtures, and start no
  process.

What is missing: nested sessions mask an active outer test; the conftest
declaration source is an unchecked private attribute with a silent default; a
declared fixture on another drive crashes validation; and
`--continue-on-collection-errors` runs tests with no declaration validated.

Architecture: session and declaration policy stay in `AuditSession`, and the
pytest instrumentation stays in `AuditHub` and the hook adapters. No shared
runtime helper is imported. Apart from the four gaps, no architecture issue
needs addressing.

Performance: dispatch does a set lookup, reads the last session and the
thread's top token, and does dictionary lookups. It does no IO and no scan.
Validation is linear in definitions, declarations and items. No performance
issue needs addressing.

Unit test coverage: the audit is inside the `tools` coverage source. The
requestor's covered and speed day walks report 100%, and static reading finds
every branch reached by the two new packages. No coverage gap exists in the
current code; each fix above needs its own test.

Feature integrity: the legacy enforcer is unchanged and still owns the own
suite. The inline helper's switch from `--capture=sys` to `-p no:capture`
keeps every child output assertion, because child output now reaches the
carrying capture.

Validation plan effects:

No reviewer edit. The writer's Step 2 rows in
`docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md` say
`Yes. Step 2 has been fully implemented.`, which this assessment does not
confirm. The "What was implemented" row also records "nested inactive sessions
mask the outer lifecycle" as intended behavior.

The writer should correct those rows together with the rework. The recorded
physical counts match a fresh sample: audit 376, declaration tests 298,
ownership tests 272, inline helper 54. The document-level line correctly stays
`No, it is not implemented`. The staged diff touches only the opening theme
sentence and the Step 2 section. Reviewer mode completed no umbrella row, and
the effort has none.

### Pre-repair mandatory checks and coverage for step 2 shared_lifecycle_gate (exchange 1) (round 1)

No repair was made, so the pre-repair and assessed states are the same index
tree, `1d825108726149d10bb328bfe2eee9e9c9fb7a0d`, which equals the
request-time tree.

Requestor evidence, not repeated: `ghog day --whole-suite` passed at
2026-11-08T17:54:02+01:00, and `ghog day --full=cov --whole-suite` passed at
2026-11-08T17:56:52+01:00 with 100% coverage. `ghog day --full=speed
--whole-suite` passed at 2026-11-08T18:16:45+01:00 with 100% coverage and zero
failures, warnings, xfails, outliers and exclusions.

Reviewer evidence, each run once from the project root with the worktree
environment:

- `ghog check` finished at 2026-11-08T18:31:19+01:00 with `exit=0`, `fail=0`,
  `warn=0`; `check.bat` reported all checks passed.
- `ghog affected --no-cov --scope-file=.reviews/a.review-scope.code.v0.14.0.shared_lifecycle_gate.json`
  finished at 2026-11-08T18:33:43+01:00 with `exit=0`. Testmon found nothing
  affected since the requestor's last walk, so 0 tests ran. The reviewed tree
  is therefore the one the requestor's green speed walk measured.

Coverage was assessed statically, as reviewer mode requires. No `ghog day` or
`ghog full` ran in this review. The four findings come from reading the code
against pytest 9.1.0 and the design. The cross-drive one was confirmed with a
standalone `Path.relative_to(..., walk_up=True)` call, which raised
`ValueError: ... have different anchors`.

### Resolved validation set and sources for step 2 shared_lifecycle_gate (exchange 1) (round 1)

The request carries one command, `ghog day --full=speed --whole-suite`, from
the `project` source. The repository has no `.review-validation` declaration,
so the built-in default `ghog day --full=speed` is completed with the bound
whole-suite selector. The request lists no plan or request additions. The
requestor owns this set and reports it green at 2026-11-08T18:16:45+01:00. The
reviewer did not run it.

### Resolver drift and direction for step 2 shared_lifecycle_gate (exchange 1) (round 1)

No drift. The current resolver input gives the same single command from the
same source: no `.review-validation` declaration, the built-in default
completed with `--whole-suite` for the bound scope (fingerprint `686958cd`),
and no plan or request addition. Neither direction adds or drops a command.

### Repository state around validation for step 2 shared_lifecycle_gate (exchange 1) (round 1)

The validation path set holds the 7 staged paths, the plan, `pyproject.toml`,
the two legacy enforcer modules, the Step 1 gate and its package marker, the
shared test package marker, the gate contract tests and the root `a.ghog.log`
written by the reviewer evidence commands. It was captured before assessment
and again after both ghog commands.

- `validation-state compare` reported `acceptable: true`, no tracked or
  untracked path changed, and one ignored path changed (`a.ghog.log`).
- `umbrella-digest compare` reported not applicable and unchanged; the request
  states `Umbrella draft: none`.
- The live index tree after assessment is still
  `1d825108726149d10bb328bfe2eee9e9c9fb7a0d`.
- The only unstaged change is the versioned review transcript
  `docs/v0.14.0/review.code.v0.14.0.shared_lifecycle_gate.md`, which the
  exchange appended and the requestor's residual commit owns.

### Repair inventory for step 2 shared_lifecycle_gate (exchange 1) (round 1)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 2 shared_lifecycle_gate (exchange 1) (round 1)

An independent `commit-plan-check.bat --format json` rerun on the received
state exited 0 with `state: valid`, `ready: true` and no diagnostics. It listed
the same 7 staged paths and the same three ordered groups as the request
evidence:

1. `perf(tests): reuse parent capture in child sessions`, 1 path.
2. `feat(audit): isolate process permissions`, 5 paths.
3. `docs(shared_lifecycle_gate): record step 2 validation`, 1 path.

Reviewer judgment on grouping and scope: every staged path belongs to exactly
one group, and each subject matches its diff. Group 1 is a test-helper
performance change that stands alone, group 2 holds the plan's five Step 2
files, and group 3 records the result. The capture change sits outside the
Step 2 file list. It is a writer verification repair needed for the green
walk, and it has its own accurate group. The bodies match the diffs, and no AI
attribution trailer is present.

`a.commit` is accurate for the received state. The rework changes the content
of groups 2 and 3, so their bodies need a refresh: group 3 must no longer
claim a completed implementation until the findings are fixed. The grouping
itself can stay.

### Findings and boundaries for step 2 shared_lifecycle_gate (exchange 1) (round 1)

Unresolved findings:

- Nested sessions mask an active outer test
  (`llm_shared_process_audit.py`, `AuditHub.dispatch`, lines 247-251).
  Dispatch judges every event by `self.sessions[-1]` and returns when that
  session has no active test. While an embedded session configures and
  collects inside an outer test's call, process events escape the outer
  test's enforcement. The design says the hook "dispatches only to an active
  session". The requirement enforces during each test's setup, call and
  teardown, and the legacy `_ACTIVE` list rejects in that window.
  `test_nested_sessions_preserve_outer_owner` cannot detect the gap: its outer
  item holds a synthetic permission, so the child's import-time event passes
  either way.
- Conftest declarations depend on an unchecked private attribute (`_modules`,
  lines 99-101). `pluginmanager._conftest_plugins` is read with an empty-set
  default, and `pytest_sessionstart` does not check it. A pytest that renames
  it would silently skip every conftest `LLM_SHARED_PROCESS_FIXTURES`: invalid
  entries would pass without exit 4, and valid fixture permissions would not
  apply. The design requires adapter capabilities to be checked at startup
  with an identifying usage error.
- A declared fixture on another drive crashes validation (`_identity`,
  line 156). `relative_to(root, walk_up=True)` raises `ValueError` ("different
  anchors") when the fixture source and `rootpath` sit on different Windows
  drives, for example an imported plugin fixture from site-packages on `C:`
  with the project on `D:`. The design allows declaring imported fixture
  objects, yet this valid declaration ends in an internal error instead of a
  usage error or an identity.
- `--continue-on-collection-errors` runs tests unvalidated
  (`pytest_collection_finish`, lines 348-352). Validation is skipped whenever
  `session.testsfailed` is nonzero. Without the flag pytest stops before any
  test anyway. With it, pytest 9.1's `pytest_runtestloop` runs the collected
  tests with no declaration validated and no test or fixture permission
  recorded. Invalid declarations then never produce exit 4, and valid
  permissions are silently ignored, against the design's rule to validate
  every declaration before any test setup.

Boundary-crossing work: None.

### Writer instructions for step 2 shared_lifecycle_gate (exchange 1) (round 1)

Fix the four findings inside the Step 2 files, then rerun the focused tests and
the resolved `ghog day --full=speed --whole-suite`:

1. Nested masking: route each event to the innermost attached session whose
   `active` is set (walk `self.sessions` from the end). Keep innermost-active
   precedence and the owner check against that session. Rework the nested
   test so the outer item has no permission, and assert that an event during
   the child's collection is rejected with the outer test's node ID. If
   masking is meant to be the rule, record it as a design decision before
   Step 3 migrates the suite onto it; do not keep it silently. Once Step 3
   attaches the carrying session, child conftests that dispatch at import to
   show inactive collection will be judged by the carrying test, so those
   tests must isolate the carrying session explicitly.
2. Conftest source: check the conftest-module source in `pytest_sessionstart`
   with an identifying `pytest fixture adapter` usage error and drop the
   silent default, or derive conftest modules through a public API. Add a test
   that removes the capability and expects exit 4.
3. Cross-drive identity: when `relative_to` raises `ValueError`, fall back to
   the absolute POSIX source path. Add a test with a definition whose file sits
   on another anchor than the session root.
4. Collection errors: record failed collector node IDs (for example in
   `pytest_collectreport`) and skip only those collectors in `_modules`,
   instead of skipping all validation. Add a `--continue-on-collection-errors`
   test with one broken module and one invalid declaration that exits 4.
5. Update the Step 2 rows in the validation plan, including the masking
   sentence, and refresh the group 2 and 3 bodies in `a.commit`.

Two non-blocking notes:

- Rejection now raises `RuntimeError` without the legacy remedy hint
  ("inject dependency facts or call Python directly"). Nothing asserts the old
  text, but Step 3 may want to keep the hint for llm-shared's own developers.
- Optional polish: the two new test files have uneven blank lines. There are
  three before `test_version_refusal_precedes_runtime_imports` and
  `test_dispatcher_is_installed_only_once`, one before
  `test_class_fixture_decorated_object_resolves` and
  `test_nonfunction_item_cannot_declare_permission`, and none before either
  `# eof` marker.

### Decision rationale for step 2 shared_lifecycle_gate (exchange 1) (round 1)

The six readiness-floor results:

- Identity: pass. The envelope, the readable identity, the plan, step 2,
  round 1, occurrence 1, `Umbrella draft: none` and the request-time index tree
  `1d825108` all agree with the live exchange and index.
- Completeness: fail. Every Step 2 file and test obligation is present, but
  four design rules are not met: nested enforcement, the startup capability
  check, cross-drive identity, and validation under collection errors.
- Validation and coverage: pass. The requestor's speed and covered walks are
  green at 100%. Reviewer `ghog check` and `ghog affected --no-cov` both exited
  0, and static reading finds no coverage gap in the current code.
- Staged attribution: pass. All 7 staged paths are writer work in three
  accurate groups. The reviewer staged nothing and edited nothing tracked.
- Findings: fail. Four findings are unresolved.
- `a.commit`: pass. The independent checker is valid and ready with no
  diagnostics, and the grouping is accurate for the received state.

This round made no repair, substantive or polishing. The request carries no
literal `Human guidance:` block, so the reviewer reports findings only.

Disposition: changes requested.

### Final reviewer decision for step 2 shared_lifecycle_gate (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-2-round-1 -->

## Round 2 by requestor - Step 2

- Recorded: 2026-11-08T19:00:34+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 2
- Outcome: request

### Review identity for step 2 shared_lifecycle_gate (round 2)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
Implementation step: 2
Review round: 2

### Code review evidence for step 2 shared_lifecycle_gate (round 2)

request_index_tree: 680adaa09ba93efb0f24098c54d8af6464960246
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: perf(tests): reuse parent capture in child sessions
group 1 path: tests/unit/tools/shared_lifecycle/inline_session.py
group 2: feat(audit): isolate process permissions
group 2 path: tools/pytest_plugins/llm_shared_process_audit.py
group 2 path: tests/unit/tools/shared_lifecycle/test_audit_declarations/__init__.py
group 2 path: tests/unit/tools/shared_lifecycle/test_audit_declarations/test_audit_declarations_tdd.py
group 2 path: tests/unit/tools/shared_lifecycle/test_audit_ownership/__init__.py
group 2 path: tests/unit/tools/shared_lifecycle/test_audit_ownership/test_audit_ownership_tdd.py
group 3: docs(shared_lifecycle_gate): record step 2 validation
group 3 path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md
staged path: tests/unit/tools/shared_lifecycle/inline_session.py
staged path: tests/unit/tools/shared_lifecycle/test_audit_declarations/__init__.py
staged path: tests/unit/tools/shared_lifecycle/test_audit_declarations/test_audit_declarations_tdd.py
staged path: tests/unit/tools/shared_lifecycle/test_audit_ownership/__init__.py
staged path: tests/unit/tools/shared_lifecycle/test_audit_ownership/test_audit_ownership_tdd.py
staged path: tools/pytest_plugins/llm_shared_process_audit.py
```

### Validation scope for step 2 shared_lifecycle_gate (round 2)

Validation scope: the whole suite.

### Requestor assessment for step 2 shared_lifecycle_gate (round 2)

Yes. Step 2 has been fully implemented. The static implementation check and
paired validation plan assess the exact step, with later steps still pending.

Round 1's four correctness gaps are fixed and tested: nested collection uses
the innermost active test through an O(1) stack; startup requires the conftest
registry; fixture sources on other Windows anchors receive absolute identities;
and failed collectors no longer suppress validation of successful sources.

The standalone module imports stdlib and pytest only, refuses Python below 3.12
before runtime imports, and declares the literal loader contract. One sys-owned
hook survives reloads and aliases. Real in-process fixture matrices cover
ownership, exclusive credit, failure unwind, thread/context boundaries and
restoration; synthetic events start no processes.

82 focused declaration/ownership cases passed. The required fresh
`ghog day --full=speed --whole-suite` passed at 2026-11-08T18:58:13+01:00 with
all static checks green, fail=0, warn=0, xfail=0, cov=100, outliers=0,
excluded=0 and proof=speed. Architecture remains separated between session
policy and pytest instrumentation. Dispatch performs no IO or declaration scan;
validation is linear in definitions, declarations and items.

Physical lines: audit 395, declaration tests 353, ownership tests 293, inline
helper 54, package markers 1 each. All are below 650. The source coverage scope
includes the audit; helper symbols outside it are referenced by tests.

Legacy suite enforcement and fixture caching/cleanup semantics are preserved.
Worker barrier/reporting and migration belong to Step 3. Actual process and
executable Python 3.12 evidence remain later compatibility-harness obligations.

### Implementation report for step 2 shared_lifecycle_gate (round 2)

The standalone process audit preserves all nine process events throughout
setup/call/teardown independently of lifecycle timing. A sys-owned hub provides
one lifetime dispatcher, per-config declarations and an active-session stack.
The most deeply active test owns an event even while a child session collects;
an active child takes precedence and detaches without losing the outer state.

Declarations validate named-test marker origin/reasons and plain dictionaries
of actual decorated fixture keys, including unused/imported definitions,
ambiguity and conflicts. Registry indexing happens once. Startup checks the
fixture and conftest registries and decorated unwrap capability. Failed
collector IDs prevent object retries while remaining sources are always
validated. Cross-drive sources fall back to absolute POSIX identity.

The bounded execute/finish adapter masks requester permissions during cache and
dependency resolution. Actual setup and finalization use live thread-local
operation tokens. Fixture permissions take precedence with exclusive credit;
only function fixtures may borrow the carrying test permission. Failure paths
unwind and the last detach restores only adapter-owned methods.

All four round 1 findings were reproduced before fixes and are covered by
regressions. The 82 focused cases passed. Required
`ghog day --full=speed --whole-suite` finished at 2026-11-08T18:58:13+01:00:
exit=0, cov=100, proof=speed, fail=0, warn=0, xfail=0, outliers=0, excluded=0.
All static checks passed. There is no validation resolver addition or scope
change; whole suite remains bound.

Earlier capture profiling removed redundant child console setup; the inline
helper preserves all parent capture assertions. Earlier reload/alias/nesting
profiling eliminated a redundant parent startup. During this round the stronger
nested test exceeded the CPU band at 0.28125s. Profiling identified unrelated
child debugger/progress startup; disabling those two plugins only for that case
preserves the reporter, real collection/test hooks and every assertion.
Diagnostic cold CPU decreased from 0.171875s to 0.046875s. Affected repair and
fresh full speed day passed. No exclusion or budget was changed.

No production process permission or suite migration was introduced. Public
verification is synthetic on Windows/Python 3.13, not an executable Python 3.12
or real-process claim. Step 3 must explicitly isolate generated child import
events once the carrying suite attaches the audit; this implication is recorded.

Writer notes: `.reviews/a.shared_lifecycle_gate.step2.journal.md` and
`.reviews/a.shared_lifecycle_gate.step2.handoff.md`.

### Change summary for step 2 shared_lifecycle_gate (round 2)

The staged set contains seven writer-owned paths:

- `tests/unit/tools/shared_lifecycle/inline_session.py`
- `tools/pytest_plugins/llm_shared_process_audit.py`
- `tests/unit/tools/shared_lifecycle/test_audit_declarations/__init__.py`
- `tests/unit/tools/shared_lifecycle/test_audit_declarations/test_audit_declarations_tdd.py`
- `tests/unit/tools/shared_lifecycle/test_audit_ownership/__init__.py`
- `tests/unit/tools/shared_lifecycle/test_audit_ownership/test_audit_ownership_tdd.py`
- `docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md`

Root `a.commit` retains three ordered groups:

1. `perf(tests): reuse parent capture in child sessions`: inline helper.
2. `feat(audit): isolate process permissions`: audit and new test packages.
3. `docs(shared_lifecycle_gate): record step 2 validation`: validation plan.

Group 2 includes the four accepted correctness fixes and their regressions.
Group 3 records corrected nested-session semantics and fresh verification.
The versioned transcript remains unstaged for the authorized residual workflow.
No Step 2 commit has been made.

### Writer response for step 2 shared_lifecycle_gate (round 2)

Writer response:

All four round 1 findings are accepted and addressed. The reviewer made no
edits or staged repairs; the writer owns all seven staged paths.

- Nested configuration/collection now dispatches to the innermost active test.
  An active-session stack preserves constant-time event handling rather than
  scanning attached sessions. Both permitted and unpermitted outer cases verify
  collection attribution, child precedence and restoration. The earlier masking
  interpretation and validation prose were incorrect and have been corrected.
- Session startup requires the conftest registry capability with an identifying
  adapter usage error. Its lookup no longer defaults silently to an empty set.
  Tests remove the capability and verify exit 4, alongside direct startup checks.
- Fixture identities fall back to the absolute POSIX source when Windows anchors
  differ. A portable Windows-path regression exercises that failure boundary.
- Failed collector IDs are recorded and skipped without retrying their objects.
  All remaining declarations are validated despite collection failures. Continued
  collection tests verify both invalid-declaration refusal and a valid module
  running beside a failed import without an internal error.

The three commit boundaries and subjects remain accurate. Group 2 and 3 bodies
are refreshed for the fixes. Optional blank-line polish is applied to both test
modules. No disagreement, reversal, scope change or production permission was
introduced. Step 3's carrying-suite import-event isolation and optional legacy
remedy hint remain recorded in the writer handoff.

### Reviewer focus for step 2 shared_lifecycle_gate (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-2-round-2 -->

## Round 2 by reviewer - Step 2

- Recorded: 2026-11-08T19:09:12+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 2
- Outcome: answer

### Assessed index identity for step 2 shared_lifecycle_gate (exchange 1) (round 2)

Baseline index tree: 680adaa09ba93efb0f24098c54d8af6464960246

Assessed index tree: 680adaa09ba93efb0f24098c54d8af6464960246

### Implementation check for step 2 shared_lifecycle_gate (exchange 1) (round 2)

Result:

Yes. Step 2 has been fully implemented.

All four round 1 findings are fixed, and each fix has a regression test that
fails on the round 1 code:

- Nested enforcement: `pytest_runtest_protocol` pushes its session onto
  `AuditHub.active_sessions` and pops it in `finally`. `dispatch` now judges
  each event by the innermost session with a running test, so an outer test
  still owns events while a child session configures and collects. A running
  child test takes precedence, and `detach` drops the session from both lists.
  The nested test now runs with and without an outer permission. Without one,
  the child's collection-time event is rejected with the outer node ID; under
  the round 1 masking it would have passed.
- Conftest source: `pytest_sessionstart` refuses a missing or non-set
  `_conftest_plugins` with `pytest fixture adapter: missing conftest registry`,
  and `_modules` no longer has a silent default. A direct startup case and an
  end-to-end run that removes the capability both expect the usage error.
- Cross-drive identity: `_identity` falls back to the absolute POSIX source
  when `relative_to` raises `ValueError`. A host-independent
  `PureWindowsPath` test checks the `Z:` source against a `Y:` root.
- Collection errors: `pytest_collectreport` records failed collector node IDs.
  `_modules` skips only those, and `pytest_collection_finish` always
  validates. Under `--continue-on-collection-errors`, the test with a broken
  import beside an invalid declaration exits 4 before any test runs. The one
  with a valid declaration runs its test without an internal error, which
  proves the failed module is not imported again.

The rest of the round 1 assessment still holds: stdlib and pytest imports
only, the 3.12 guard and literal contract, the nine events, the sys-owned hub,
the bounded execute/finish adapter, the thread-local tokens, the precedence
and exclusive credit, and the validation coverage. `pytest_collectreport`
uses the newest attached session, because the hook receives no config. This
is correct, because only the collecting session can be newest during
collection.

Architecture: no change of shape. The active-session stack sits in `AuditHub`
next to the attachment list. No architecture issue needs addressing.

Performance: dispatch still does constant work: a set lookup, the top of the
active stack and the thread's top token. The stack is pushed and popped once
per test. The failed-collector set adds one lookup per collector. No
performance issue needs addressing.

Unit test coverage: every new branch is reached, including the collector
skip, the identity fallback, both report outcomes, the conftest refusal and
the push and pop. The requestor's fresh speed walk reports 100%. No coverage
gap remains.

Feature integrity: the legacy enforcer is unchanged. The child plugins the
nested test disables (`debugging` and `terminalprogress`) are unrelated to
ownership: the reporter and the real collection and test hooks still run.

Validation plan effects:

No reviewer edit. The writer's Step 2 rows in
`docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md` now agree with
this assessment:

- the status sentence is exactly `Yes. Step 2 has been fully implemented.`;
- the masking sentence is replaced by the innermost-active-test rule;
- the fixes, the fresh speed walk and the nested-test timing repair are
  recorded;
- the physical counts match a fresh sample (audit 395, declaration tests 353,
  ownership tests 293, inline helper 54).

The document-level line correctly stays `No, it is not implemented` while
Steps 3-7 are pending. Between rounds the staged diff of that file changes
only the Step 2 section. Reviewer mode completed no umbrella row, and the
effort has none.

### Pre-repair mandatory checks and coverage for step 2 shared_lifecycle_gate (exchange 1) (round 2)

No repair was made, so the pre-repair and assessed states are the same index
tree, `680adaa09ba93efb0f24098c54d8af6464960246`, which equals the
request-time tree.

Requestor evidence, not repeated: 82 focused declaration and ownership cases
passed. `ghog day --full=speed --whole-suite` passed at
2026-11-08T18:58:13+01:00 with 100% coverage, all static checks green and zero
failures, warnings, xfails, outliers and exclusions.

Reviewer evidence, each run once from the project root with the worktree
environment:

- `ghog check` finished at 2026-11-08T19:06:14+01:00 with `exit=0`, `fail=0`,
  `warn=0`; `check.bat` reported all checks passed.
- `ghog affected --no-cov --scope-file=.reviews/a.review-scope.code.v0.14.0.shared_lifecycle_gate.json`
  finished at 2026-11-08T19:07:10+01:00 with `exit=0`. Testmon found nothing
  affected since the requestor's last walk, so 0 tests ran. The reviewed tree
  is therefore the one the requestor's green speed walk measured.

Coverage was assessed statically, as reviewer mode requires. No `ghog day` or
`ghog full` ran in this review.

### Resolved validation set and sources for step 2 shared_lifecycle_gate (exchange 1) (round 2)

The request carries one command, `ghog day --full=speed --whole-suite`, from
the `project` source. The repository has no `.review-validation` declaration,
so the built-in default `ghog day --full=speed` is completed with the bound
whole-suite selector. The request lists no plan or request additions. The
requestor owns this set and reports it green at 2026-11-08T18:58:13+01:00. The
reviewer did not run it.

### Resolver drift and direction for step 2 shared_lifecycle_gate (exchange 1) (round 2)

No drift. The current resolver input gives the same single command from the
same source: no `.review-validation` declaration, the built-in default
completed with `--whole-suite` for the bound scope (fingerprint `686958cd`),
and no plan or request addition. Neither direction adds or drops a command.

### Repository state around validation for step 2 shared_lifecycle_gate (exchange 1) (round 2)

The validation path set is the same 16 paths as round 1:

- the 7 staged paths and the plan;
- `pyproject.toml` and the two legacy enforcer modules;
- the Step 1 gate and its package marker;
- the shared test package marker and the gate contract tests;
- the root `a.ghog.log` written by the reviewer evidence commands.

It was captured before assessment and again after both ghog commands.

- `validation-state compare` reported `acceptable: true`, no tracked or
  untracked path changed, and one ignored path changed (`a.ghog.log`).
- `umbrella-digest compare` reported not applicable and unchanged; the request
  states `Umbrella draft: none`.
- The live index tree after assessment is still
  `680adaa09ba93efb0f24098c54d8af6464960246`.
- The only unstaged change is the versioned review transcript
  `docs/v0.14.0/review.code.v0.14.0.shared_lifecycle_gate.md`, which the
  exchange appended and the requestor's residual commit owns.

### Repair inventory for step 2 shared_lifecycle_gate (exchange 1) (round 2)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 2 shared_lifecycle_gate (exchange 1) (round 2)

An independent `commit-plan-check.bat --format json` rerun on the received
state exited 0 with `state: valid`, `ready: true` and no diagnostics. It listed
the same 7 staged paths and the same three ordered groups as the request
evidence:

1. `perf(tests): reuse parent capture in child sessions`, 1 path.
2. `feat(audit): isolate process permissions`, 5 paths.
3. `docs(shared_lifecycle_gate): record step 2 validation`, 1 path.

Reviewer judgment on grouping and scope: every staged path belongs to exactly
one group, and each subject matches its diff. The group 2 body now lists the
innermost-active-test rule, the conftest capability and validation after
collection errors, and the cross-drive identity. The group 3 body records the
four review fixes. Both match the round 2 diff, and no AI attribution trailer
is present.

`a.commit` needs no amendment.

### Findings and boundaries for step 2 shared_lifecycle_gate (exchange 1) (round 2)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 2 shared_lifecycle_gate (exchange 1) (round 2)

No change is required for Step 2. Keep the staged set and `a.commit` as they
are, and take the human convergence choice from the gate.

For Step 3, carry the implication the writer already recorded. Once the
carrying suite attaches the audit, child conftests and modules that dispatch at
import to show inactive collection are judged by the carrying test. Those tests
must isolate the carrying session explicitly. The legacy remedy hint ("inject
dependency facts or call Python directly") remains an optional Step 3 choice.

### Decision rationale for step 2 shared_lifecycle_gate (exchange 1) (round 2)

All six readiness-floor results pass:

- Identity: the envelope, the readable identity, the plan, step 2, round 2,
  occurrence 1, `Umbrella draft: none` and the request-time index tree
  `680adaa0` all agree with the live exchange and index.
- Completeness: every Step 2 file and test obligation is present, and the four
  round 1 gaps are closed with discriminating regressions.
- Validation and coverage: the requestor's fresh speed walk is green at 100%.
  Reviewer `ghog check` and `ghog affected --no-cov` both exited 0, and the
  static coverage reading finds no gap.
- Staged attribution: all 7 staged paths are writer work in three accurate
  groups. The reviewer staged nothing and edited nothing tracked.
- Findings: none are unresolved or carried, and no boundary-crossing work
  remains.
- `a.commit`: the independent checker is valid and ready with no diagnostics,
  and the reviewer's grouping judgment agrees.

This round made no repair, substantive or polishing. The request carries no
literal `Human guidance:` block.

The recommendation is commit-ready and advisory only. It does not authorize a
commit.

### Final reviewer decision for step 2 shared_lifecycle_gate (exchange 1) (round 2)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-2-round-2 -->

## Round 2 by human - Step 2 - human-confirmation

- Recorded: 2026-11-08T19:44:30+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 2
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->
