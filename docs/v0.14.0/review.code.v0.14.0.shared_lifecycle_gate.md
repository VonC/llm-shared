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

## Round 1 by requestor - Step 3

- Recorded: 2026-11-08T23:48:13+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: unrecorded
- Implementation step: 3
- Outcome: request

### Review identity for step 3 shared_lifecycle_gate (round 1)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
Implementation step: 3
Review round: 1

### Code review evidence for step 3 shared_lifecycle_gate (round 1)

request_index_tree: eead05ac8940a0cf531c224ba9467262c005941f
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "missing", "requirement": "docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(lifecycle): enforce worker audit barrier
group 1 path: pyproject.toml
group 1 path: tools/pytest_plugins/llm_shared_process_audit.py
group 1 path: tools/lifecycle_compatibility/__init__.py
group 1 path: tools/lifecycle_compatibility/runner.py
group 1 path: tools/lifecycle_compatibility/scenarios.py
group 1 path: tests/unit/tools/shared_lifecycle/conftest.py
group 1 path: tests/unit/tools/shared_lifecycle/inline_session.py
group 1 path: tests/unit/tools/shared_lifecycle/test_audit_workers/__init__.py
group 1 path: tests/unit/tools/shared_lifecycle/test_audit_workers/test_audit_workers_tdd.py
group 1 path: tests/unit/tools/shared_lifecycle/test_compatibility/__init__.py
group 1 path: tests/unit/tools/shared_lifecycle/test_compatibility/test_compatibility_tdd.py
group 1 path: tests/unit/tools/test_simulation_boundaries.py
group 1 path: tests/conftest.py
group 1 path: tests/lifecycle_cpu_record.py
group 1 path: tests/simulation_policy.py
group 2: perf(tests): read groundhog sources once
group 2 path: tests/unit/tools/test_groundhog_no_machine_queue.py
group 3: docs(shared_lifecycle_gate): record step 3 validation
group 3 path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md
staged path: pyproject.toml
staged path: tests/conftest.py
staged path: tests/lifecycle_cpu_record.py
staged path: tests/simulation_policy.py
staged path: tests/unit/tools/shared_lifecycle/conftest.py
staged path: tests/unit/tools/shared_lifecycle/inline_session.py
staged path: tests/unit/tools/shared_lifecycle/test_audit_workers/__init__.py
staged path: tests/unit/tools/shared_lifecycle/test_audit_workers/test_audit_workers_tdd.py
staged path: tests/unit/tools/shared_lifecycle/test_compatibility/__init__.py
staged path: tests/unit/tools/shared_lifecycle/test_compatibility/test_compatibility_tdd.py
staged path: tests/unit/tools/test_groundhog_no_machine_queue.py
staged path: tests/unit/tools/test_simulation_boundaries.py
staged path: tools/lifecycle_compatibility/__init__.py
staged path: tools/lifecycle_compatibility/runner.py
staged path: tools/lifecycle_compatibility/scenarios.py
staged path: tools/pytest_plugins/llm_shared_process_audit.py
```

### Validation scope for step 3 shared_lifecycle_gate (round 1)

Validation scope: the whole suite.

### Requestor assessment for step 3 shared_lifecycle_gate (round 1)

Step 3 is fully implemented according to its implementation-check section.

The fresh `ghog day --full=speed --whole-suite` ended on 2026-11-08 at
21:40:54+01:00 with exit 0, 100% tools coverage, zero failures, warnings,
xfails, duration outliers or exclusions. Static checks passed in that walk.
No budget, coverage omission or own-suite process permission was added.

The standalone audit imports only stdlib and pytest. Authorization remains
constant time per event; declaration validation and report merging are linear.
Every changed Python file is below the 650-line ceiling (maximum 488).
Finite worker and merge state matrices use deterministic tests; no additional
property test is needed for those finite cases.

Real Python 3.13.9 / pytest 9.1.0 / xdist 3.8.0 probes passed before migration
and after harness refactoring. Invalid declaration, early exit and collection
mismatch each observed a valid peer announcement, no setup/body start,
controller exit 4 and both workers reaped. Python 3.12 executable evidence is
reserved for step 6 and is not claimed here.

Existing policy assertions passed against canonical modules before legacy
removal. Record comparison preserved exception meaning and all other fields,
retained all 5892 prior eligible proofs, added 9, and lost none. Private
continuity evidence remains available for step 7; the live record was not
overwritten.

Markdown lint, canonical spelling and staged whitespace checks passed.
The three-group root a.commit is mechanically ready. Steps 4 through 7 remain
pending. Please assess only step 3 and its staged changes.

### Implementation report for step 3 shared_lifecycle_gate (round 1)

The audit validates declarations with a first-priority collection-finish hook
before xdist announces collection. The controller checks initial worker count,
collection consistency, absent evidence and early exits before scheduling, with
identifying usage errors. Worker permissions are detached for transport and
merged by stable identity with consistent reasons and boolean OR usage.
Reports distinguish tests from fixtures, warn on unused declared permissions
and omit unexercised declarations.

The bounded external smoke harness generates isolated real xdist projects.
Process-free unit tests retain real scenario generation and verdict logic.
The own suite now loads canonical policies after coverage starts. Synthetic
test hubs are isolated while the carrying real audit remains enforced, and
test monkeypatches unwind before restoring the carrying hub. Legacy policy
files were removed only after migrated assertions passed.

Generated inner sessions omit unused debugger, terminal progress, tmpdir and
legacy path plugins while retaining terminal reports, warnings, thread
exception reporting and every behavior assertion. The source marker test now
reads each file once: the actual-function profile changed from 144 reads and
0.115832 seconds to 36 reads and 0.014754 seconds. No isolated measured CPU
improvement is claimed for the child-plugin adjustment.

Validation: fresh whole-suite speed walk exit 0, tools coverage 100%, no
failures, warnings, xfails, outliers or accepted exclusions. Executable smoke
evidence is Windows/Python 3.13 only. The remaining steps retain their own
compatibility, activation and final acceptance obligations.

Writer notes: .reviews/a.shared_lifecycle_gate.step3.journal.md and .reviews/a.shared_lifecycle_gate.step3.handoff.md

### Change summary for step 3 shared_lifecycle_gate (round 1)

Root a.commit has three ordered groups:

1. feat(lifecycle): enforce worker audit barrier
2. perf(tests): read groundhog sources once
3. docs(shared_lifecycle_gate): record step 3 validation

The 17 staged paths are:

- docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md
- pyproject.toml
- tests/conftest.py
- tests/lifecycle_cpu_record.py (deleted)
- tests/simulation_policy.py (deleted)
- tests/unit/tools/shared_lifecycle/conftest.py
- tests/unit/tools/shared_lifecycle/inline_session.py
- `tests/unit/tools/shared_lifecycle/test_audit_workers/__init__.py`
- tests/unit/tools/shared_lifecycle/test_audit_workers/test_audit_workers_tdd.py
- `tests/unit/tools/shared_lifecycle/test_compatibility/__init__.py`
- tests/unit/tools/shared_lifecycle/test_compatibility/test_compatibility_tdd.py
- tests/unit/tools/test_groundhog_no_machine_queue.py
- tests/unit/tools/test_simulation_boundaries.py
- `tools/lifecycle_compatibility/__init__.py`
- tools/lifecycle_compatibility/runner.py
- tools/lifecycle_compatibility/scenarios.py
- tools/pytest_plugins/llm_shared_process_audit.py

Only step 3 validation is marked complete; document-level completion remains No.

### Writer response for step 3 shared_lifecycle_gate (round 1)

Writer response:

This is the first review round for step 3. No previous step 3 reviewer feedback
or disagreement exists. The writer requests an independent assessment of the
exact step and staged implementation, including barrier ordering, bounded
worker cancellation, permission aggregation, preserved outer enforcement,
record continuity and the accuracy of executable evidence claims.

### Reviewer focus for step 3 shared_lifecycle_gate (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-3-round-1 -->

## Round 1 by reviewer - Step 3

- Recorded: 2026-11-09T00:22:27+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 3
- Outcome: answer

### Assessed index identity for step 3 shared_lifecycle_gate (exchange 1) (round 1)

Baseline index tree: eead05ac8940a0cf531c224ba9467262c005941f

Assessed index tree: eead05ac8940a0cf531c224ba9467262c005941f

### Implementation check for step 3 shared_lifecycle_gate (exchange 1) (round 1)

Result:

No. Step 3 is not fully implemented. The controller's node-down hook treats
every worker exit as missing barrier evidence, including exits after the
barrier has completed. The unresolved findings list it with two smaller
defects.

What is in place and matches the plan:

- Validation runs in a `tryfirst` `pytest_collection_finish`. That is ahead of
  xdist 3.8.0's plain `WorkerInteractor.pytest_collection_finish`, which sends
  the announcement. A failure stores the diagnostic in `workeroutput` and
  re-raises, so the worker withholds its announcement. Its
  `pytest_sessionfinish` still runs, and `workerfinished` carries the evidence.
- `pytest_xdist_setupnodes` counts the initial workers.
  `pytest_xdist_node_collection_finished` rejects an inconsistent collection
  before xdist calls `add_node_collection`, as traced in `dsession.py`.
- An invalid worker's diagnostic reaches exit 4 through `pytest_testnodedown`.
  The barrier never completes, so no peer is scheduled.
- Worker records are detached with `asdict`, then validated and merged by
  identity with boolean OR, and conflicting reasons are refused. The summary
  prints once, serially or on the controller, and workers print nothing. It
  separates tests from fixtures, warns on unused permissions and omits
  unexercised declarations.
- The harness in `tools/lifecycle_compatibility/` isolates generated projects
  from plugin autoload, `PYTEST_ADDOPTS`, `PYTHONPATH` and the
  `LLM_SHARED_PYTEST_` variables. It bounds the controller wait at 30 s and
  reaps leftover workers. A Ruff `py312` target and a Pyright 3.12 execution
  environment cover it.
- `tests/conftest.py` loads both canonical policies through `pytest_plugins`,
  and both legacy modules are deleted. The completion searches find no
  executable legacy reference, no `tools.pytest_plugins` import and no policy
  selection in `senv.bat`.
- The autouse fixture in `tests/unit/tools/shared_lifecycle/conftest.py` gives
  synthetic tests a separate hub. The installed dispatcher keeps the carrying
  hub, so real events stay enforced without permissions.

What is missing:

- After the barrier, a crashed worker, a Ctrl-C or a replacement worker is
  reported as a declaration-barrier usage error.
- The `runpy` entry-point test can signal real PIDs on POSIX.
- The review transcript fails Markdown lint.

Architecture: the audit still imports only stdlib and pytest. Worker
coordination stays in its pytest hooks, and the policy never imports the
harness. Apart from the first finding, no architecture issue needs addressing.

Performance: collection comparison, record merging and summaries are linear in
their inputs, and per-event dispatch is unchanged. No performance issue needs
addressing.

Unit test coverage: the coverage source is `tools`, with a 100% gate and no new
omit. Static reading finds every new audit and runner branch reached by the
two new test packages, and the requestor's speed walk reports 100%. The
current code has no coverage gap, but the fix needs post-barrier tests. Test
files sit outside the gate, and all their top-level symbols are referenced.

Feature integrity: xdist's crash report and worker replacement are lost (first
finding). Timing, record continuity and unrelated suite plugins are otherwise
intact. `wiki/reference/test-lifecycle-limits.md` still names
`tests/simulation_policy.py`, but Step 7 owns that page.

Validation plan effects:

No reviewer edit. The writer's Step 3 rows in
`docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md` say
`Yes. Step 3 has been fully implemented.`, which this assessment does not
confirm. The feature integrity row also does not record the lost xdist crash
handling.

The writer should correct those rows together with the rework. The recorded
audit count of 488 physical lines matches the staged file. The document-level
line correctly stays `No, it is not implemented`, and the staged diff touches
only the Step 3 section. Reviewer mode completed no umbrella row, and the
effort has none.

### Pre-repair mandatory checks and coverage for step 3 shared_lifecycle_gate (exchange 1) (round 1)

No repair was made. The pre-repair and assessed states are therefore the same
index tree, `eead05ac8940a0cf531c224ba9467262c005941f`, which equals the
request-time tree.

Requestor evidence, not repeated: `ghog day --full=speed --whole-suite` passed
at 2026-11-08T21:40:54+01:00 with 100% tools coverage and zero failures,
warnings, xfails, outliers and exclusions.

Reviewer evidence, each command run once from the project root with the
worktree environment:

- `ghog check` finished at 2026-11-09T00:10:57+01:00 with `exit=1`. Ty,
  Pyright, Ruff, Radon, Vulture, the 650-line file check, ShellCheck and the
  EOF check all passed. The Markdown check failed with MD050 at lines 1573,
  1575 and 1579 of the unstaged review transcript (third finding).
- `ghog affected --no-cov --scope-file=.reviews/a.review-scope.code.v0.14.0.shared_lifecycle_gate.json`
  finished at 2026-11-09T00:14:30+01:00 with `exit=0`. Testmon found nothing
  affected since the requestor's walk, so 0 tests ran.

Coverage was assessed statically, and no `ghog day` or `ghog full` ran. The
first finding was traced through xdist 3.8.0's `dsession.py`. It was then
confirmed without starting any process, by calling the audit hooks with fake
nodes in xdist's order. A crash after the barrier, a normal finish after a
replacement announced, and a keyboard-interrupt node-down each raised the
`validated collection` usage error.

### Resolved validation set and sources for step 3 shared_lifecycle_gate (exchange 1) (round 1)

The request carries one command, `ghog day --full=speed --whole-suite`, from
the `project` source. The repository has no `.review-validation` declaration,
so the built-in default `ghog day --full=speed` is completed with the bound
whole-suite selector, and the request lists no plan or request additions. The
requestor owns this set and reports it green at 2026-11-08T21:40:54+01:00. The
reviewer did not run it.

The request's `test_scope` shows `proof: missing`. Exchange status still binds
the round to scope `whole` with fingerprint `686958cd`, and the reviewer used
that `paths.scope` capture.

### Resolver drift and direction for step 3 shared_lifecycle_gate (exchange 1) (round 1)

No drift. The current resolver input gives the same single command from the
same source. There is no `.review-validation` declaration, the built-in
default is completed with `--whole-suite` for the bound scope (fingerprint
`686958cd`), and there is no plan or request addition. Neither direction adds
or drops a command.

### Repository state around validation for step 3 shared_lifecycle_gate (exchange 1) (round 1)

The validation path set holds the 17 staged paths, the plan and the root
`a.ghog.log` that the reviewer evidence commands write. It was captured before
assessment and again after both ghog commands.

- `validation-state compare` reported `acceptable: true`, with no tracked or
  untracked path changed and one ignored path changed (`a.ghog.log`).
- `umbrella-digest compare` reported not applicable and unchanged, because the
  request states `Umbrella draft: none`.
- After assessment, the live index tree is still
  `eead05ac8940a0cf531c224ba9467262c005941f`.
- The only unstaged change is the versioned review transcript
  `docs/v0.14.0/review.code.v0.14.0.shared_lifecycle_gate.md`. The exchange
  appended it, and the requestor's residual commit owns it.

### Repair inventory for step 3 shared_lifecycle_gate (exchange 1) (round 1)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 3 shared_lifecycle_gate (exchange 1) (round 1)

An independent `commit-plan-check.bat --format json` rerun on the received
state exited 0 with `state: valid`, `ready: true` and no diagnostics. It listed
the same 17 staged paths and the same three ordered groups as the request
evidence:

1. `feat(lifecycle): enforce worker audit barrier`, 15 paths.
2. `perf(tests): read groundhog sources once`, 1 path.
3. `docs(shared_lifecycle_gate): record step 3 validation`, 1 path.

Reviewer judgment on grouping and scope: every staged path belongs to exactly
one group, and each subject matches its diff. Group 1 holds the plan's Step 3
files together with the migration support in `inline_session.py`, the
`shared_lifecycle` conftest and `test_simulation_boundaries.py`. Group 2 is a
standalone test performance change, and group 3 records the result. No AI
attribution trailer is present.

`a.commit` is accurate for the received state. The rework changes the content
of groups 1 and 3, so their bodies need a refresh. Group 3 must not claim a
completed step until the findings are fixed. The grouping itself can stay.

### Findings and boundaries for step 3 shared_lifecycle_gate (exchange 1) (round 1)

Unresolved findings:

- Worker exits after the barrier become a barrier usage error
  (`llm_shared_process_audit.py`, `pytest_testnodedown`, lines 426-437).
  xdist 3.8.0's `DSession.worker_errordown` calls
  `pytest_testnodedown(node, error)` before `handle_crashitem` and
  `_clone_node`. The hook raises whenever `error` is set or the announced count
  differs from `expected_workers`, even after every initial worker announced
  and tests were scheduled. Three cases fail. First, a test that kills its
  worker (a segfault or `os._exit`) ends the run with exit 4 and "worker
  exited before all validated collection evidence arrived". Without the audit,
  xdist reports "worker 'gw0' crashed while running ..." as a failure and
  starts a replacement worker. Second, a Ctrl-C is reported the same way,
  because xdist follows `workerfinished` with
  `worker_errordown(node, "keyboard-interrupt")`. Third, once a replacement
  worker announces, the announced count exceeds `expected_workers`, so every
  later normal finish raises. The design limits this stop to a worker that
  "finishes before announcing its collection". Calling the hooks in xdist's order with fake nodes confirmed all
  three cases. The existing tests cover only exits before the barrier. A
  related path was traced but not executed: with `--maxfail` and a collection
  error, xdist shuts down and ignores later `collectionfinish` events, and the
  hook would then report missing evidence instead of the interrupted run.
- The module entry-point test can signal real processes on POSIX
  (`test_compatibility_tdd.py`, `test_module_entrypoint_uses_same_harness`,
  lines 231-244). `runpy` runs a second copy of `runner.py`, whose own `alive`
  and `kill_tree` are not patched. The test replaces only `subprocess.run`,
  which covers the Windows branch. On POSIX, `alive(101)` calls the real
  `os.kill(101, 0)` for the fake PIDs that the transport double writes. If the
  user owns a live process with PID 101, `kill_tree` then sends it a real
  `SIGKILL`. If another user owns it, an uncaught `PermissionError` follows.
  This is low severity while the suite runs only on Windows, but the test
  claims POSIX coverage.
- `ghog check` fails on the review transcript
  (`docs/v0.14.0/review.code.v0.14.0.shared_lifecycle_gate.md`, lines 1573,
  1575 and 1579, MD050). The round 1 request's change summary lists the three
  `__init__.py` package markers outside code spans, so their double
  underscores parse as strong emphasis. The staged files pass. The transcript
  is unstaged and requestor-owned, but the next review-record commit would
  carry the lint failure.

Boundary-crossing work: None.

### Writer instructions for step 3 shared_lifecycle_gate (exchange 1) (round 1)

Fix the three findings, then rerun the focused tests and the resolved
`ghog day --full=speed --whole-suite`:

1. Barrier scope: in `pytest_testnodedown`, stop for missing evidence only
   while the initial barrier is incomplete. For example, set a
   `barrier_complete` flag once `announced` reaches `expected_workers`. After
   that, a node-down with an error returns without raising, so xdist reports
   the crash item and replaces the worker or stops, as `--max-worker-restart`
   decides. Merge records only from a worker that sent them. A replacement
   worker's announcement is still checked for consistency, but it must not
   fail later finishes. Add tests for these cases: a crash after the barrier,
   a replacement announcement followed by a normal finish, and a
   keyboard-interrupt node-down after the barrier. Keep the pre-barrier cases.
   Decide whether a controller that is already shutting down before the
   barrier, for example `--maxfail` with a collection error, should keep
   xdist's interrupted result or exit 4 with that cause named. Test whichever
   you choose. An optional post-barrier crash scenario in the smoke harness
   would add executable evidence.
2. Entry-point test: monkeypatch `runner.sys.platform` to `"win32"` in
   `test_module_entrypoint_uses_same_harness`, as the Windows probe test
   already does. Alternatively, patch `os.kill` and `os.killpg` there too, so
   the `runpy` copy never signals a real PID.
3. Transcript: before the review-record commit, put the three `__init__.py`
   paths at lines 1573, 1575 and 1579 in code spans. Write future change-summary
   path lists as code spans.
4. Update the Step 3 validation rows, including the status sentence and
   feature integrity, and refresh the group 1 and group 3 bodies in
   `a.commit`.

Two non-blocking notes:

- `wiki/reference/test-lifecycle-limits.md` still points to the deleted
  `tests/simulation_policy.py`. Step 7 owns that page.
- Optional polish: a worker declaration error is reported with the
  `llm_shared_process_audit:` prefix twice, because `pytest_testnodedown`
  wraps a diagnostic that already carries it.

### Decision rationale for step 3 shared_lifecycle_gate (exchange 1) (round 1)

The six readiness-floor results:

- Identity: pass. The envelope, the readable identity, the plan, step 3,
  round 1, occurrence 1, `Umbrella draft: none` and the request-time index tree
  `eead05ac` all agree with the live exchange and index.
- Completeness: fail. Every Step 3 file and test obligation is present, but
  the controller stops on worker exits after the barrier, against the design's
  limit to exits before announcement.
- Validation and coverage: fail. Reviewer `ghog check` exited 1 on the
  transcript's MD050 lint. `ghog affected --no-cov` exited 0 with nothing
  affected, and static reading finds no coverage gap in the current code.
- Staged attribution: pass. All 17 staged paths are writer work in three
  accurate groups. The reviewer staged nothing and edited nothing tracked.
- Findings: fail. Three findings are unresolved.
- `a.commit`: pass. The independent checker is valid and ready with no
  diagnostics, and the grouping is accurate for the received state.

This round made no repair, substantive or polishing. The request carries no
literal `Human guidance:` block, so the reviewer reports findings only.

Disposition: changes requested.

### Final reviewer decision for step 3 shared_lifecycle_gate (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-3-round-1 -->

## Round 2 by requestor - Step 3

- Recorded: 2026-11-09T10:03:58+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 3
- Outcome: request

### Review identity for step 3 shared_lifecycle_gate (round 2)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
Implementation step: 3
Review round: 2

### Code review evidence for step 3 shared_lifecycle_gate (round 2)

request_index_tree: 3ad5da8d238b0c63f6a79d96dc1ca0cab2e5ae93
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(lifecycle): enforce worker audit barrier
group 1 path: pyproject.toml
group 1 path: tools/pytest_plugins/llm_shared_process_audit.py
group 1 path: tools/lifecycle_compatibility/__init__.py
group 1 path: tools/lifecycle_compatibility/runner.py
group 1 path: tools/lifecycle_compatibility/scenarios.py
group 1 path: tests/unit/tools/shared_lifecycle/conftest.py
group 1 path: tests/unit/tools/shared_lifecycle/inline_session.py
group 1 path: tests/unit/tools/shared_lifecycle/test_audit_workers/__init__.py
group 1 path: tests/unit/tools/shared_lifecycle/test_audit_workers/test_audit_workers_tdd.py
group 1 path: tests/unit/tools/shared_lifecycle/test_compatibility/__init__.py
group 1 path: tests/unit/tools/shared_lifecycle/test_compatibility/test_compatibility_tdd.py
group 1 path: tests/unit/tools/test_simulation_boundaries.py
group 1 path: tests/conftest.py
group 1 path: tests/lifecycle_cpu_record.py
group 1 path: tests/simulation_policy.py
group 2: perf(tests): read groundhog sources once
group 2 path: tests/unit/tools/test_groundhog_no_machine_queue.py
group 3: docs(shared_lifecycle_gate): record step 3 validation
group 3 path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md
staged path: pyproject.toml
staged path: tests/conftest.py
staged path: tests/lifecycle_cpu_record.py
staged path: tests/simulation_policy.py
staged path: tests/unit/tools/shared_lifecycle/conftest.py
staged path: tests/unit/tools/shared_lifecycle/inline_session.py
staged path: tests/unit/tools/shared_lifecycle/test_audit_workers/__init__.py
staged path: tests/unit/tools/shared_lifecycle/test_audit_workers/test_audit_workers_tdd.py
staged path: tests/unit/tools/shared_lifecycle/test_compatibility/__init__.py
staged path: tests/unit/tools/shared_lifecycle/test_compatibility/test_compatibility_tdd.py
staged path: tests/unit/tools/test_groundhog_no_machine_queue.py
staged path: tests/unit/tools/test_simulation_boundaries.py
staged path: tools/lifecycle_compatibility/__init__.py
staged path: tools/lifecycle_compatibility/runner.py
staged path: tools/lifecycle_compatibility/scenarios.py
staged path: tools/pytest_plugins/llm_shared_process_audit.py
```

### Validation scope for step 3 shared_lifecycle_gate (round 2)

Validation scope: the whole suite.

### Requestor assessment for step 3 shared_lifecycle_gate (round 2)

Step 3 is fully implemented according to its implementation-check section.

The fresh `ghog day --full=speed --whole-suite` ended on 2026-11-09 at
09:58:42+01:00 with exit 0, 100% tools coverage, zero failures, warnings,
xfails, duration outliers or exclusions. Static checks passed in that walk.
No budget, coverage omission or own-suite process permission was added.

The standalone audit imports only stdlib and pytest. Authorization remains
constant time per event; declaration validation and report merging are linear.
Every changed Python file is below the 650-line ceiling (maximum 497).
Finite worker and merge state matrices use deterministic tests; no additional
property test is needed for those finite cases.

Real Python 3.13.9 / pytest 9.1.0 / xdist 3.8.0 probes passed before migration
and after harness refactoring. Invalid declaration, early exit and collection
mismatch each observed a valid peer announcement, no setup/body start,
controller exit 4 and both workers reaped. Python 3.12 executable evidence is
reserved for step 6 and is not claimed here.

Existing policy assertions passed against canonical modules before legacy
removal. Record comparison preserved exception meaning and all other fields,
retained all 5892 prior eligible proofs, added 9, and lost none. Private
continuity evidence remains available for step 7; the live record was not
overwritten.

Static Markdown lint passed. Transcript spelling has seven xdist identifiers awaiting individual user decisions; no commit gate will be presented before they are settled.
The three-group root a.commit is mechanically ready. Steps 4 through 7 remain
pending. Please assess only step 3 and its staged changes.

### Implementation report for step 3 shared_lifecycle_gate (round 2)

The audit validates declarations with a first-priority collection-finish hook
before xdist announces collection. The controller checks initial worker count,
collection consistency, absent evidence and early exits before scheduling, with
identifying usage errors. Worker permissions are detached for transport and
merged by stable identity with consistent reasons and boolean OR usage.
Reports distinguish tests from fixtures, warn on unused declared permissions
and omit unexercised declarations.

Review rework latches completion of the initial barrier, preserves later xdist
crash/replacement/keyboard-interrupt handling and validates records whenever
sent. A worker crash may omit records; successful workers still owe them.
Controller stop/shutdown before the barrier preserves the original cause.
Regressions retain all early-exit cases, add later worker transitions, and
keep replacement collection mismatches invalid. The module-entrypoint test
uses the mocked Windows process transport on every host.
The bounded external smoke harness generates isolated real xdist projects.
Process-free unit tests retain real scenario generation and verdict logic.
The own suite now loads canonical policies after coverage starts. Synthetic
test hubs are isolated while the carrying real audit remains enforced, and
test monkeypatches unwind before restoring the carrying hub. Legacy policy
files were removed only after migrated assertions passed.

Generated inner sessions omit unused debugger, terminal progress, tmpdir and
legacy path plugins while retaining terminal reports, warnings, thread
exception reporting and every behavior assertion. The source marker test now
reads each file once: the actual-function profile changed from 144 reads and
0.115832 seconds to 36 reads and 0.014754 seconds. No isolated measured CPU
improvement is claimed for the child-plugin adjustment.

Validation: fresh whole-suite speed walk exit 0, tools coverage 100%, no
failures, warnings, xfails, outliers or accepted exclusions. Executable smoke
evidence is Windows/Python 3.13 only. The remaining steps retain their own
compatibility, activation and final acceptance obligations.

Writer notes: .reviews/a.shared_lifecycle_gate.step3.journal.md and .reviews/a.shared_lifecycle_gate.step3.handoff.md

### Change summary for step 3 shared_lifecycle_gate (round 2)

Root a.commit retains three ordered groups:

1. `feat(lifecycle): enforce worker audit barrier`
2. `perf(tests): read groundhog sources once`
3. `docs(shared_lifecycle_gate): record step 3 validation`

All 17 staged paths remain in the reviewed batch:

- `docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md`
- `pyproject.toml`
- `tests/conftest.py`
- `tests/lifecycle_cpu_record.py`
- `tests/simulation_policy.py`
- `tests/unit/tools/shared_lifecycle/conftest.py`
- `tests/unit/tools/shared_lifecycle/inline_session.py`
- `tests/unit/tools/shared_lifecycle/test_audit_workers/__init__.py`
- `tests/unit/tools/shared_lifecycle/test_audit_workers/test_audit_workers_tdd.py`
- `tests/unit/tools/shared_lifecycle/test_compatibility/__init__.py`
- `tests/unit/tools/shared_lifecycle/test_compatibility/test_compatibility_tdd.py`
- `tests/unit/tools/test_groundhog_no_machine_queue.py`
- `tests/unit/tools/test_simulation_boundaries.py`
- `tools/lifecycle_compatibility/__init__.py`
- `tools/lifecycle_compatibility/runner.py`
- `tools/lifecycle_compatibility/scenarios.py`
- `tools/pytest_plugins/llm_shared_process_audit.py`

Group 1 and 3 bodies now include the xdist regression repairs and validation.
The review transcript remains unstaged for the authorized residual batch.
Transcript spelling decisions remain pending; any resulting dictionary edit
will accompany that transcript. No scope or group-definition change occurred.
Only Step 3 is complete; document-level completion remains No.

### Writer response for step 3 shared_lifecycle_gate (round 2)

Writer response:

All three round 1 findings are accepted; there is no disagreement and the
reviewer made no repairs. The writer changed the reviewed implementation.

The initial collection barrier is now latched. Later crashes retain xdist
replacement handling, and matching replacement announcements cannot invalidate
the completed barrier. Replacement mismatches still fail. Worker keyboard
interrupts preserve both xdist down notifications. Missing crash records are
allowed; any records sent are validated, and successful workers owe records.

Before the barrier, an active controller stop/shutdown or worker keyboard
interrupt preserves the original xdist interruption. An unexplained early
exit still raises the identifying usage error. Tests model collection maxfail
through the actual dsession stop/shutdown fields, which explain why xdist can
withhold collection announcements. Existing pre-barrier cases remain intact.

The entrypoint test now fixes shared sys.platform to win32, matching its
subprocess mocks and preventing real POSIX signals to fake worker PIDs.
Exactly three bare package-marker paths in the round 1 request summary were
wrapped in code spans. Future path lists use code spans throughout.

The validation document and group 1/3 commit bodies describe these repairs.
The unrelated legacy wiki reference remains Step 7 work. No exclusion,
budget increase, process exemption or coverage omission was added.

### Reviewer focus for step 3 shared_lifecycle_gate (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-3-round-2 -->

## Round 2 by reviewer - Step 3

- Recorded: 2026-11-09T10:46:54+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 3
- Outcome: answer

### Assessed index identity for step 3 shared_lifecycle_gate (exchange 1) (round 2)

Baseline index tree: 3ad5da8d238b0c63f6a79d96dc1ca0cab2e5ae93

Assessed index tree: 3ad5da8d238b0c63f6a79d96dc1ca0cab2e5ae93

### Implementation check for step 3 shared_lifecycle_gate (exchange 1) (round 2)

Result:

Yes. Step 3 has been fully implemented.

The round 2 rework fixes all three round 1 findings. Two new items block
commit-ready (see the unresolved findings), but neither changes the step
verdict. First, one new record rule has no test that fails without it.
Second, the reviewer's focused run was red because the machine was busy.

Round 1 findings, rechecked against the xdist 3.8.0 `dsession.py` source:

- Barrier scope: fixed. `AuditSession.barrier_complete` latches when the
  announced count reaches `expected_workers` (`llm_shared_process_audit.py`
  line 425). After that, `pytest_testnodedown` no longer raises for a crash,
  a keyboard interrupt or a replacement worker. `worker_errordown` therefore
  goes on to `handle_crashitem` and `_clone_node` as it does without the
  audit. A replacement's collection is still compared with the first
  collection (line 421), and a mismatch still fails.
- Keyboard interrupt: `worker_workerfinished` calls the hook, then
  `worker_errordown` calls it again. Both calls skip the barrier stop. Merging
  the same records twice is harmless, because `merge` is keyed by identity
  and only ORs `used`.
- Stop before the barrier: the hook still raises, unless the worker reports
  `ExitCode.INTERRUPTED` or the `dsession` plugin has `shouldstop` or
  `shuttingdown` set. xdist registers that plugin under the name `dsession`
  (`plugin.py` line 278). With `--maxfail` and a collection error,
  `_handlefailures` sets `shouldstop` while handling the collect report. That
  report arrives before the worker's `workerfinished`, so xdist's original
  stop reason is kept. A worker declaration diagnostic is still checked first
  and still exits 4.
- Entry-point test: fixed. `test_module_entrypoint_uses_same_harness` sets
  `runner.sys.platform` to `win32`. `alive` and `kill_tree` read
  `sys.platform` at call time from the shared `sys` module, so the `runpy`
  copy takes the mocked `subprocess.run` path and never calls `os.kill`.
- Transcript lint: fixed. The three package markers in the round 1 change
  summary are now code spans, and the Markdown step of the reviewer
  `ghog check` passed.

The rest of the step is unchanged from round 1 and still matches the plan:
validation before the announcement, the initial worker count, the collection
comparison, detached records merged with OR, separate test and fixture
summaries, the bounded harness, canonical policy loading after coverage
starts, removal of both legacy sources, and the completion searches.

Architecture: the audit still imports only stdlib and pytest. The new branch
reads xdist's controller only through `config.pluginmanager.getplugin`, with
`getattr` defaults, so the audit adds no xdist import. No architecture issue
needs addressing.

Performance: each node-down does one plugin lookup and constant-time checks.
Merging stays linear in the records. No performance issue needs addressing.

Unit test coverage: the coverage source is `tools`, with a 100% gate and no
new omit. Every new branch line is reached: the latch by the barrier tests,
the controller-stop skip by the shutdown test, the interrupt skip by the
keyboard-interrupt matrix, and the conditional merge by the crash tests with
and without records. No line or branch is uncovered. One rule is still
untested (first finding). The test files sit outside the gate, and all their
top-level symbols are referenced. Physical line counts match the validation
rows: audit 497, worker tests 287, compatibility tests 248, all under 650.

Feature integrity: xdist's crash reports, worker replacement, interrupt
handling and `--maxfail` stop reasons are preserved after validation.
Declaration failures and unexplained exits before the barrier still exit 4.
`wiki/reference/test-lifecycle-limits.md` still names
`tests/simulation_policy.py`, and Step 7 owns that page.

Validation plan effects:

No reviewer edit. The writer's Step 3 rows in
`docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md` now say
`Yes. Step 3 has been fully implemented.`, which this assessment confirms for
the plan obligations. The rows describe the latched barrier, crash and
interrupt handling, the controller-stop case and the entry-point platform
fix. The recorded line counts match the staged files.

The unit test coverage row lists the post-barrier regressions accurately. It
should name the new missing-records case once the first finding is fixed. The
document-level line correctly stays `No, it is not implemented`, and the
staged diff touches only the Step 3 section. Reviewer mode completed no
umbrella row, and the effort has none.

### Pre-repair mandatory checks and coverage for step 3 shared_lifecycle_gate (exchange 1) (round 2)

No repair was made. The pre-repair and assessed states are therefore the same
index tree, `3ad5da8d238b0c63f6a79d96dc1ca0cab2e5ae93`, which equals the
request-time tree.

Requestor evidence, not repeated: `ghog day --full=speed --whole-suite` passed
at 2026-11-09T09:58:42+01:00 with 100% tools coverage and zero failures,
warnings, xfails, outliers and exclusions.

Reviewer evidence. Each command ran once from the project root through the
worktree's `.\senv.bat` (guard cleared, `SWITCHPY_CHOICE=local`), with the
log-freshness check:

- `ghog check` ended at 2026-11-09T10:25:25+01:00 with `exit=0` after
  3m 07.0s. Every static step passed, including the Markdown check that
  failed in round 1.
- `ghog affected --no-cov --scope-file=.reviews/a.review-scope.code.v0.14.0.shared_lifecycle_gate.json`
  ended at 2026-11-09T10:36:53+01:00 with `exit=2` after 8m 58.4s. Testmon
  selected the whole bound scope, not a subset. It reported `fail=31`, all
  of them lifecycle wall-time overruns while another checkout's pytest walk
  was running (second finding). The reviewer did not re-run it and did not
  follow the report's next-step line.

Coverage was assessed statically, and no `ghog day` or `ghog full` ran. The
rework was traced against xdist 3.8.0's `dsession.py` and `plugin.py`: the
hook order in `worker_workerfinished` and `worker_errordown`, the `dsession`
registration name, and where `_handlefailures` sets `shouldstop`.

### Resolved validation set and sources for step 3 shared_lifecycle_gate (exchange 1) (round 2)

The request carries one command, `ghog day --full=speed --whole-suite`, from
the `project` source. The repository has no `.review-validation` declaration,
so the built-in default `ghog day --full=speed` is completed with the bound
whole-suite selector. The request lists no plan or request additions. The
requestor owns this set and reports it green at 2026-11-09T09:58:42+01:00.
The reviewer did not run it.

The request's `test_scope` now shows `proof: speed`. Exchange status binds the
round to scope `whole` with fingerprint `686958cd`, and the reviewer used
that `paths.scope` capture.

### Resolver drift and direction for step 3 shared_lifecycle_gate (exchange 1) (round 2)

No drift. The current resolver input gives the same single command from the
same source. There is no `.review-validation` declaration, the built-in
default is completed with `--whole-suite` for the bound scope (fingerprint
`686958cd`), and there is no plan or request addition. Neither direction adds
or drops a command.

### Repository state around validation for step 3 shared_lifecycle_gate (exchange 1) (round 2)

The validation path set holds the 17 staged paths, the plan and the root
`a.ghog.log` that the reviewer evidence commands write. It was captured before
assessment and again after both ghog commands.

- `validation-state compare` reported `acceptable: true`. No tracked or
  untracked path changed, and one ignored path changed (`a.ghog.log`).
- `umbrella-digest compare` reported not applicable and unchanged, because the
  request states `Umbrella draft: none`.
- After assessment, the live index tree is still
  `3ad5da8d238b0c63f6a79d96dc1ca0cab2e5ae93`.
- The only unstaged change is the versioned review transcript
  `docs/v0.14.0/review.code.v0.14.0.shared_lifecycle_gate.md`. The exchange
  appended it, and the requestor's residual commit owns it. Its pending
  spelling decisions are outside this staged batch.

### Repair inventory for step 3 shared_lifecycle_gate (exchange 1) (round 2)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 3 shared_lifecycle_gate (exchange 1) (round 2)

An independent `commit-plan-check.bat --format json` rerun on the received
state exited 0 with `state: valid`, `ready: true` and no diagnostics. It listed
the same 17 staged paths and the same three ordered groups as the request
evidence:

1. `feat(lifecycle): enforce worker audit barrier`, 15 paths.
2. `perf(tests): read groundhog sources once`, 1 path.
3. `docs(shared_lifecycle_gate): record step 3 validation`, 1 path.

Reviewer judgment on grouping and scope: every staged path belongs to exactly
one group, and each subject matches its diff. The group 1 body now records the
latched barrier, preserved xdist handling, required records from successful
workers and the POSIX-safe entry-point test. The group 3 body records the
preserved failure handling. No AI attribution trailer is present.

`a.commit` is accurate for the received state. The requested test addition
belongs in group 1, and the coverage-row update belongs in group 3. The
grouping itself can stay.

### Findings and boundaries for step 3 shared_lifecycle_gate (exchange 1) (round 2)

Unresolved findings:

- No test pins the rule that a successful worker must send records
  (`llm_shared_process_audit.py`, `pytest_testnodedown`, line 445). The merge
  now runs only when `_RECORDS in output or (error is None and not
  interrupted)`. The second clause is what rejects a worker that finished
  normally without a records key, for example one that never loaded the
  audit. Every test that reaches this line either has a records key or
  passes an error or an interrupt. `test_missing_or_malformed_worker_records_fail_identifiably`
  covers `None` only as a present value. Reducing the condition to
  `_RECORDS in output` would keep every test green. A worker with no
  records would then add nothing, and the controller would print a complete
  report with that worker's usage missing. That is the case the test's own
  docstring rules out ("Missing usage evidence cannot silently become an
  empty successful report"). The validation rows also say "successful
  workers must send them". Coverage is 100% because the condition is one
  line.
- The reviewer's focused run was red.
  `ghog affected --no-cov --scope-file=.reviews/a.review-scope.code.v0.14.0.shared_lifecycle_gate.json`
  ended at 2026-11-09T10:36:53+01:00 with `exit=2` and `fail=31`. Every one
  of the 31 is a lifecycle teardown error for wall time above the 1.000 s
  limit. CPU stayed within its limit in each case (0.000 to 0.094 s), and
  there was no assertion failure. The errors are spread over 19 files and
  none is in a Step 3 file. The only audit-related one is a Step 2 test,
  `test_all_process_events_cover_entire_protocol[os.system]`: wall 1.597 s,
  CPU 0.094 s. During the run, another checkout's whole-suite pytest walk
  (another checkout, started 10:30) was running, and the processor was
  at 99% load. The legacy `tests/simulation_policy.py` applied the same
  1.0 s wall limit with the same condition, so the migration did not make
  the limit stricter. This is most likely contention, not a code defect, but
  the reviewer evidence is still red and is reported as such.

Boundary-crossing work: None.

### Writer instructions for step 3 shared_lifecycle_gate (exchange 1) (round 2)

1. Pin the record rule. In
   `test_missing_or_malformed_worker_records_fail_identifiably`, or in a
   sibling test, add a case where a worker that announced finishes with
   `error=None`, no interrupt and a `workeroutput` without the records key,
   for example `{}`. Expect the `worker permission records` usage error.
   Keep the crash and interrupt cases, where a missing key is allowed. The
   test must fail if line 445 is reduced to `_RECORDS in output`.
2. Re-run the focused tests while no other pytest walk is running on the
   machine. Then run the resolved `ghog day --full=speed --whole-suite`.
   Confirm that the 31 tests listed in the second finding now pass under the
   1.000 s wall limit. If any still overruns on an idle machine, fix it
   through the groundhog loop. Do not add an exclusion or raise a budget.
3. Update the Step 3 unit test coverage row to mention the new case, and
   refresh the group 1 and group 3 bodies in `a.commit` if their content
   changes.

Non-blocking notes:

- `wiki/reference/test-lifecycle-limits.md` still points to the deleted
  `tests/simulation_policy.py`. Step 7 owns that page.
- Optional polish, carried from round 1 and not addressed: a worker
  declaration error still shows the `llm_shared_process_audit:` prefix twice,
  because `pytest_testnodedown` wraps a diagnostic that already carries it
  (lines 436 and 437).

### Decision rationale for step 3 shared_lifecycle_gate (exchange 1) (round 2)

The six readiness-floor results:

- Identity: pass. The envelope, the readable identity, the plan, step 3,
  round 2, occurrence 1, `Umbrella draft: none` and the request-time index tree
  `3ad5da8d` all agree with the live exchange and index.
- Completeness: pass. Every Step 3 obligation is implemented, and the three
  round 1 findings are fixed.
- Validation and coverage: fail. Reviewer `ghog check` exited 0, but
  `ghog affected --no-cov` exited 2 with 31 wall-time overruns on a loaded
  machine. Static reading finds no uncovered line or branch, but one record
  rule has no test that fails without it.
- Staged attribution: pass. All 17 staged paths are writer work in three
  accurate groups. The reviewer staged nothing and edited nothing tracked.
- Findings: fail. Two findings are unresolved.
- `a.commit`: pass. The independent checker is valid and ready with no
  diagnostics, and the grouping is accurate for the received state.

This round made no repair, substantive or polishing. The request carries no
literal `Human guidance:` block, so the reviewer reports findings only.

Disposition: changes requested.

### Final reviewer decision for step 3 shared_lifecycle_gate (exchange 1) (round 2)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-3-round-2 -->

## Round 3 by requestor - Step 3

- Recorded: 2026-11-09T11:08:04+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 3
- Outcome: request

### Review identity for step 3 shared_lifecycle_gate (round 3)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
Implementation step: 3
Review round: 3

### Code review evidence for step 3 shared_lifecycle_gate (round 3)

request_index_tree: feb9077f3254e515d4d19e989e6938b429d952d1
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(lifecycle): enforce worker audit barrier
group 1 path: pyproject.toml
group 1 path: tools/pytest_plugins/llm_shared_process_audit.py
group 1 path: tools/lifecycle_compatibility/__init__.py
group 1 path: tools/lifecycle_compatibility/runner.py
group 1 path: tools/lifecycle_compatibility/scenarios.py
group 1 path: tests/unit/tools/shared_lifecycle/conftest.py
group 1 path: tests/unit/tools/shared_lifecycle/inline_session.py
group 1 path: tests/unit/tools/shared_lifecycle/test_audit_workers/__init__.py
group 1 path: tests/unit/tools/shared_lifecycle/test_audit_workers/test_audit_workers_tdd.py
group 1 path: tests/unit/tools/shared_lifecycle/test_compatibility/__init__.py
group 1 path: tests/unit/tools/shared_lifecycle/test_compatibility/test_compatibility_tdd.py
group 1 path: tests/unit/tools/test_simulation_boundaries.py
group 1 path: tests/conftest.py
group 1 path: tests/lifecycle_cpu_record.py
group 1 path: tests/simulation_policy.py
group 2: perf(tests): read groundhog sources once
group 2 path: tests/unit/tools/test_groundhog_no_machine_queue.py
group 3: docs(shared_lifecycle_gate): record step 3 validation
group 3 path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md
staged path: pyproject.toml
staged path: tests/conftest.py
staged path: tests/lifecycle_cpu_record.py
staged path: tests/simulation_policy.py
staged path: tests/unit/tools/shared_lifecycle/conftest.py
staged path: tests/unit/tools/shared_lifecycle/inline_session.py
staged path: tests/unit/tools/shared_lifecycle/test_audit_workers/__init__.py
staged path: tests/unit/tools/shared_lifecycle/test_audit_workers/test_audit_workers_tdd.py
staged path: tests/unit/tools/shared_lifecycle/test_compatibility/__init__.py
staged path: tests/unit/tools/shared_lifecycle/test_compatibility/test_compatibility_tdd.py
staged path: tests/unit/tools/test_groundhog_no_machine_queue.py
staged path: tests/unit/tools/test_simulation_boundaries.py
staged path: tools/lifecycle_compatibility/__init__.py
staged path: tools/lifecycle_compatibility/runner.py
staged path: tools/lifecycle_compatibility/scenarios.py
staged path: tools/pytest_plugins/llm_shared_process_audit.py
```

### Validation scope for step 3 shared_lifecycle_gate (round 3)

Validation scope: the whole suite.

### Requestor assessment for step 3 shared_lifecycle_gate (round 3)

Step 3 is fully implemented according to its implementation-check section.

The fresh `ghog day --full=speed --whole-suite` ended on 2026-11-09 at
11:05:14+01:00 with exit 0, 100% tools coverage, zero failures, warnings,
xfails, duration outliers or exclusions. Static checks passed in that walk.
No budget, coverage omission or own-suite process permission was added.

The standalone audit imports only stdlib and pytest. Authorization remains
constant time per event; declaration validation and report merging are linear.
Every changed Python file is below the 650-line ceiling (maximum 497).
Finite worker and merge state matrices use deterministic tests; no additional
property test is needed for those finite cases.

Real Python 3.13.9 / pytest 9.1.0 / xdist 3.8.0 probes passed before migration
and after harness refactoring. Invalid declaration, early exit and collection
mismatch each observed a valid peer announcement, no setup/body start,
controller exit 4 and both workers reaped. Python 3.12 executable evidence is
reserved for step 6 and is not claimed here.

Existing policy assertions passed against canonical modules before legacy
removal. Record comparison preserved exception meaning and all other fields,
retained all 5892 prior eligible proofs, added 9, and lost none. Private
continuity evidence remains available for step 7; the live record was not
overwritten.

Static Markdown lint passed. Transcript spelling has seven xdist identifiers awaiting individual user decisions; no commit gate will be presented before they are settled.
The three-group root a.commit is mechanically ready. Steps 4 through 7 remain
pending. Please assess only step 3 and its staged changes.

### Implementation report for step 3 shared_lifecycle_gate (round 3)

The audit validates declarations with a first-priority collection-finish hook
before xdist announces collection. The controller checks initial worker count,
collection consistency, absent evidence and early exits before scheduling, with
identifying usage errors. Worker permissions are detached for transport and
merged by stable identity with consistent reasons and boolean OR usage.
Reports distinguish tests from fixtures, warn on unused declared permissions
and omit unexercised declarations.

Review rework latches completion of the initial barrier, preserves later xdist
crash/replacement/keyboard-interrupt handling and validates records whenever
sent. A worker crash may omit records; successful workers still owe them.
Controller stop/shutdown before the barrier preserves the original cause.
Regressions retain all early-exit cases, add later worker transitions, and
keep replacement collection mismatches invalid. The module-entrypoint test
uses the mocked Windows process transport on every host.
The bounded external smoke harness generates isolated real xdist projects.
Process-free unit tests retain real scenario generation and verdict logic.
The own suite now loads canonical policies after coverage starts. Synthetic
test hubs are isolated while the carrying real audit remains enforced, and
test monkeypatches unwind before restoring the carrying hub. Legacy policy
files were removed only after migrated assertions passed.

Generated inner sessions omit unused debugger, terminal progress, tmpdir and
legacy path and assertion plugins while retaining terminal reports, warnings, thread
exception reporting and every behavior assertion. The source marker test now
reads each file once: the actual-function profile changed from 144 reads and
0.115832 seconds to 36 reads and 0.014754 seconds. No isolated measured CPU
improvement is claimed for the earlier child-plugin adjustment. The round 3
assertion-plugin removal reduced the flagged actual-function profile from
CPU 0.171875 s / wall 0.186358 s to CPU 0.078125 s / wall 0.101997 s.
A new regression rejects normally finished workers with no records key.
The 19 reviewer-failing files and subsequent shared lifecycle focus passed.

Validation: fresh whole-suite speed walk exit 0, tools coverage 100%, no
failures, warnings, xfails, outliers or accepted exclusions. Executable smoke
evidence is Windows/Python 3.13 only. The remaining steps retain their own
compatibility, activation and final acceptance obligations.

Writer notes: `.reviews/a.shared_lifecycle_gate.step3.journal.md` and
`.reviews/a.shared_lifecycle_gate.step3.handoff.md`.

### Change summary for step 3 shared_lifecycle_gate (round 3)

Root a.commit retains three ordered groups:

1. `feat(lifecycle): enforce worker audit barrier`
2. `perf(tests): read groundhog sources once`
3. `docs(shared_lifecycle_gate): record step 3 validation`

All 17 staged paths remain in the reviewed batch:

- `docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md`
- `pyproject.toml`
- `tests/conftest.py`
- `tests/lifecycle_cpu_record.py`
- `tests/simulation_policy.py`
- `tests/unit/tools/shared_lifecycle/conftest.py`
- `tests/unit/tools/shared_lifecycle/inline_session.py`
- `tests/unit/tools/shared_lifecycle/test_audit_workers/__init__.py`
- `tests/unit/tools/shared_lifecycle/test_audit_workers/test_audit_workers_tdd.py`
- `tests/unit/tools/shared_lifecycle/test_compatibility/__init__.py`
- `tests/unit/tools/shared_lifecycle/test_compatibility/test_compatibility_tdd.py`
- `tests/unit/tools/test_groundhog_no_machine_queue.py`
- `tests/unit/tools/test_simulation_boundaries.py`
- `tools/lifecycle_compatibility/__init__.py`
- `tools/lifecycle_compatibility/runner.py`
- `tools/lifecycle_compatibility/scenarios.py`
- `tools/pytest_plugins/llm_shared_process_audit.py`

Group 1 and 3 bodies now include the xdist regression repairs and validation.
The review transcript remains unstaged for the authorized residual batch.
Transcript spelling decisions remain pending; any resulting dictionary edit
will accompany that transcript. No scope or group-definition change occurred.
Only Step 3 is complete; document-level completion remains No.

### Writer response for step 3 shared_lifecycle_gate (round 3)

Writer response:

The missing-records finding is accepted. The new sibling regression completes
the initial barrier, then finishes an announced worker normally with empty
worker output and expects the identifying permission-records usage error.
Removing the successful-finish clause would make that assertion fail. Existing
crash and interrupt cases remain unchanged. No production fix was needed.

The red reviewer validation is retained as red evidence. The 19 flagged files
plus the worker tests passed in focus at 10:51:41+01:00 with no warnings. The
flagged audit protocol test was then profiled: embedded pytest startup was the
largest cost. The child helper now omits the redundant assertion plugin while
retaining plain Python assertions, real collection and fixture execution,
warnings, thread exception handling and terminal reporting. The actual test
profile changed from CPU 0.171875 s / wall 0.186358 s to CPU 0.078125 s /
wall 0.101997 s. All shared lifecycle tests passed at 10:59:53+01:00.

There is one procedural disagreement: the instruction to validate only while
no other checkout runs pytest conflicts with the canonical Groundhog rule
that forbids a machine-wide queue or an agent convention waiting between
checkouts. Validation follows the prescribed focused/profile repair flow
instead; no other checkout was stopped and no budget or exclusion changed.
The fresh whole-suite proof is recorded in the paired implementation evidence.

The Step 3 coverage and size rows and group 1/3 commit bodies now describe
the regression and timing repair. The old wiki reference remains Step 7 work.
The seven existing transcript spelling decisions remain unanswered; they must
settle before the commit gate.

### Reviewer focus for step 3 shared_lifecycle_gate (round 3)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-3-round-3 -->

## Round 3 by reviewer - Step 3

- Recorded: 2026-11-09T11:17:24+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 3
- Outcome: answer

### Assessed index identity for step 3 shared_lifecycle_gate (exchange 1) (round 3)

Baseline index tree: feb9077f3254e515d4d19e989e6938b429d952d1

Assessed index tree: feb9077f3254e515d4d19e989e6938b429d952d1

### Implementation check for step 3 shared_lifecycle_gate (exchange 1) (round 3)

Result:

Yes. Step 3 has been fully implemented.

Both round 2 findings are resolved, and no new finding was found. The round 3
rework adds one regression test and trims one plugin from the embedded test
sessions. Production code is unchanged since round 2.

Round 2 findings, rechecked:

- Untested record rule: fixed.
  `test_successful_worker_cannot_omit_permission_records` completes the
  initial barrier with two announcements. One announced worker then finishes
  with `error=None`, no interrupt and an empty `workeroutput`, and the test
  expects the `worker permission records` usage error. If line 445 of
  `llm_shared_process_audit.py` were reduced to `_RECORDS in output`, the
  merge would be skipped and the test would fail. The crash and interrupt
  cases, where a missing key is allowed, are unchanged.
- Red reviewer run: resolved. This round's
  `ghog affected --no-cov --scope-file=<paths.scope>` exited 0, and the
  requestor's fresh whole-suite speed walk passed at 11:05:14+01:00 with
  unchanged budgets and no exclusions.

Writer disagreement, accepted: the round 2 instruction to re-run "while no
other pytest walk is running" conflicts with `instructions/groundhog.md`. That
rule says runs of different checkouts never wait for each other, and that no
such wait may be added "in groundhog or as an agent convention". The writer
instead followed the focused re-run and profiling flow, and it found and
removed real startup cost. The reviewer withdraws that part of the
instruction.

Embedded session change in `tests/unit/tools/shared_lifecycle/inline_session.py`:
`--assert=plain` is replaced by `-p no:assertion`. This is sound. pytest
applies `-p no:` blocks before it imports its default plugins, so the
assertion plugin never loads. Without it the `--assert` option is not
registered, and the import-hook setup falls back to plain mode. The host's
rewrite hook is still removed from `sys.meta_path` for the duration (line 34),
so the docstring's plain-assertion claim stays true. Not loading the plugin
also leaves the carrying session's assertion globals untouched. The measured
profile of the flagged audit test fell from CPU 0.171875 s to 0.078125 s.

Architecture: no production change since round 2. The audit still imports only
stdlib and pytest, and the policy never imports the harness. No architecture
issue needs addressing.

Performance: unchanged production complexity. The test-side plugin removal
lowers embedded session startup. No performance issue needs addressing.

Unit test coverage: the coverage source is `tools`, with a 100% gate and no
new omit, and the requestor's walk reports 100%. Every audit branch is
reached, and the record rule now has a test that fails without it. Test files
sit outside the gate, and all their top-level symbols are referenced, including
the new test. Physical line counts match the validation rows: audit 497,
inline helper 62, worker tests 300, all under 650. No unit-tested class is
below 100%, and no top-level symbol outside the gate is unreferenced.

Feature integrity: xdist's crash, replacement, interrupt and `--maxfail`
handling after validation are preserved. Declaration failures and unexplained
exits before the barrier still exit 4, and a successful worker with no records
still fails. `wiki/reference/test-lifecycle-limits.md` still names
`tests/simulation_policy.py`, and Step 7 owns that page.

Validation plan effects:

No reviewer edit. The writer's Step 3 rows in
`docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md` say
`Yes. Step 3 has been fully implemented.`, which this assessment confirms. The
round 3 changes are accurate. The size row now records the inline helper at
62 lines and the worker tests at 300, and both match the staged files. The
performance row records the round 2 overruns, the focused re-run and the
measured child startup reduction. The coverage row names the new
missing-records regression, and the walk timestamp is now 11:05:14+01:00.

The document-level line correctly stays `No, it is not implemented`, and the
staged diff touches only the Step 3 section. Reviewer mode completed no
umbrella row, and the effort has none.

### Pre-repair mandatory checks and coverage for step 3 shared_lifecycle_gate (exchange 1) (round 3)

No repair was made. The pre-repair and assessed states are therefore the same
index tree, `feb9077f3254e515d4d19e989e6938b429d952d1`, which equals the
request-time tree.

Requestor evidence, not repeated: `ghog day --full=speed --whole-suite` passed
at 2026-11-09T11:05:14+01:00 with 100% tools coverage and zero failures,
warnings, xfails, outliers and exclusions. The root `a.ghog.log` tail showed
that result before the reviewer's commands ran.

Reviewer evidence. Each command ran once from the project root through the
worktree's `.\senv.bat` (guard cleared, `SWITCHPY_CHOICE=local`), with the
log-freshness check:

- `ghog check` ended at 2026-11-09T11:13:57+01:00 with `exit=0` after
  1m 14.0s. Every static step passed, including the Markdown check.
- `ghog affected --no-cov --scope-file=.reviews/a.review-scope.code.v0.14.0.shared_lifecycle_gate.json`
  ended at 2026-11-09T11:15:27+01:00 with `exit=0` after 26.0s, `fail=0` and
  `warn=0`. Testmon found nothing affected since the requestor's 11:05:14
  walk, so 0 tests ran, and groundhog treats that as green.

Coverage was assessed statically, and no `ghog day` or `ghog full` ran.

### Resolved validation set and sources for step 3 shared_lifecycle_gate (exchange 1) (round 3)

The request carries one command, `ghog day --full=speed --whole-suite`, from
the `project` source. The repository has no `.review-validation` declaration,
so the built-in default `ghog day --full=speed` is completed with the bound
whole-suite selector. The request lists no plan or request additions. The
requestor owns this set and reports it green at 2026-11-09T11:05:14+01:00,
which the root `a.ghog.log` tail confirmed before the reviewer's own commands
ran. The reviewer did not run it.

The request's `test_scope` shows `proof: speed`. Exchange status binds the
round to scope `whole` with fingerprint `686958cd`, and the reviewer used
that `paths.scope` capture.

### Resolver drift and direction for step 3 shared_lifecycle_gate (exchange 1) (round 3)

No drift. The current resolver input gives the same single command from the
same source. There is no `.review-validation` declaration, the built-in
default is completed with `--whole-suite` for the bound scope (fingerprint
`686958cd`), and there is no plan or request addition. Neither direction adds
or drops a command.

### Repository state around validation for step 3 shared_lifecycle_gate (exchange 1) (round 3)

The validation path set holds the 17 staged paths, the plan and the root
`a.ghog.log` that the reviewer evidence commands write. It was captured before
assessment and again after both ghog commands.

- `validation-state compare` reported `acceptable: true`. No tracked or
  untracked path changed, and one ignored path changed (`a.ghog.log`).
- `umbrella-digest compare` reported not applicable and unchanged, because the
  request states `Umbrella draft: none`.
- After assessment, the live index tree is still
  `feb9077f3254e515d4d19e989e6938b429d952d1`.
- The only unstaged change is the versioned review transcript
  `docs/v0.14.0/review.code.v0.14.0.shared_lifecycle_gate.md`. The exchange
  appended it, and the requestor's residual commit owns it. Its seven pending
  spelling decisions are outside this staged batch, and the requestor has
  said they will be settled before the commit gate.

### Repair inventory for step 3 shared_lifecycle_gate (exchange 1) (round 3)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 3 shared_lifecycle_gate (exchange 1) (round 3)

An independent `commit-plan-check.bat --format json` rerun on the received
state exited 0 with `state: valid`, `ready: true` and no diagnostics. It listed
the same 17 staged paths and the same three ordered groups as the request
evidence:

1. `feat(lifecycle): enforce worker audit barrier`, 15 paths.
2. `perf(tests): read groundhog sources once`, 1 path.
3. `docs(shared_lifecycle_gate): record step 3 validation`, 1 path.

Reviewer judgment on grouping and scope: every staged path belongs to exactly
one group, and each subject matches its diff. The group 1 body now names the
missing-records regression and the trimmed child plugin startup. The group 3
body names the regression and the measured assertion-plugin reduction. Both
round 3 changes belong to group 1 and its validation to group 3, so the
grouping stays correct. No AI attribution trailer is present.

`a.commit` is accurate for the received state, and the reviewer did not amend
it.

### Findings and boundaries for step 3 shared_lifecycle_gate (exchange 1) (round 3)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 3 shared_lifecycle_gate (exchange 1) (round 3)

No further implementation work is requested for Step 3.

Before the commit gate, settle the seven pending transcript spelling decisions
as the request states. Any dictionary edit goes with the transcript in the
residual review-record batch, not in the three reviewed groups.

Non-blocking notes:

- `wiki/reference/test-lifecycle-limits.md` still points to the deleted
  `tests/simulation_policy.py`. Step 7 owns that page.
- Optional polish, carried from round 1: a worker declaration error still
  shows the `llm_shared_process_audit:` prefix twice, because
  `pytest_testnodedown` wraps a diagnostic that already carries it (lines 436
  and 437).

### Decision rationale for step 3 shared_lifecycle_gate (exchange 1) (round 3)

The six readiness-floor results:

- Identity: pass. The envelope, the readable identity, the plan, step 3,
  round 3, occurrence 1, `Umbrella draft: none` and the request-time index tree
  `feb9077f` all agree with the live exchange and index.
- Completeness: pass. Every Step 3 obligation is implemented, and all round 1
  and round 2 findings are resolved.
- Validation and coverage: pass. Reviewer `ghog check` and
  `ghog affected --no-cov` both exited 0, and the requestor's whole-suite
  speed walk is green with 100% tools coverage. Static reading finds no
  coverage gap, and the record rule is now pinned by a test.
- Staged attribution: pass. All 17 staged paths are writer work in three
  accurate groups. The reviewer staged nothing and edited nothing tracked.
- Findings: pass. No current or carried finding is unresolved. The writer's
  procedural disagreement is accepted, and the conflicting round 2
  instruction is withdrawn.
- `a.commit`: pass. The independent checker is valid and ready with no
  diagnostics, and the grouping and bodies are accurate.

This round made no repair, substantive or polishing. The request carries no
literal `Human guidance:` block.

Disposition: commit-ready. This is an advisory recommendation and does not
authorize a commit. The requestor still owns the pending transcript spelling
decisions before presenting the commit gate.

### Final reviewer decision for step 3 shared_lifecycle_gate (exchange 1) (round 3)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-3-round-3 -->

## Round 3 by human - Step 3 - human-confirmation

- Recorded: 2026-11-09T12:31:48+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 3
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-3 -->

## Round 1 by requestor - Step 4

- Recorded: 2026-11-09T15:36:44+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: unrecorded
- Implementation step: 4
- Outcome: request

### Review identity for step 4 shared_lifecycle_gate (round 1)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
Implementation step: 4
Review round: 1

### Code review evidence for step 4 shared_lifecycle_gate (round 1)

request_index_tree: 61d60d980883583c89eed8578bd0047ae02512d2
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)
- `ghog day --whole-suite` (sources: plan)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(pytest): prepare bound policy loading
group 1 path: tools/pytest_plugin_environment.py
group 1 path: tools/pytest_plugin_shell.py
group 1 path: tools/pytest_plugins/llm_shared_pytest_loader.py
group 1 path: bin/prepare_pytest_plugins.bat
group 2: test(pytest): cover prepared policy loading
group 2 path: tests/memory_filesystem.py
group 2 path: tests/unit/tools/shared_lifecycle/test_preparation/__init__.py
group 2 path: tests/unit/tools/shared_lifecycle/test_preparation/test_preparation_tdd.py
group 2 path: tests/unit/tools/shared_lifecycle/test_preparation/test_preparation_pbt.py
group 2 path: tests/unit/tools/shared_lifecycle/test_shell_transport/__init__.py
group 2 path: tests/unit/tools/shared_lifecycle/test_shell_transport/test_shell_transport_tdd.py
group 2 path: tests/unit/tools/shared_lifecycle/test_loader/__init__.py
group 2 path: tests/unit/tools/shared_lifecycle/test_loader/test_loader_tdd.py
group 3: docs(shared_lifecycle_gate): record step 4 validation
group 3 path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md
staged path: bin/prepare_pytest_plugins.bat
staged path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md
staged path: tests/memory_filesystem.py
staged path: tests/unit/tools/shared_lifecycle/test_loader/__init__.py
staged path: tests/unit/tools/shared_lifecycle/test_loader/test_loader_tdd.py
staged path: tests/unit/tools/shared_lifecycle/test_preparation/__init__.py
staged path: tests/unit/tools/shared_lifecycle/test_preparation/test_preparation_pbt.py
staged path: tests/unit/tools/shared_lifecycle/test_preparation/test_preparation_tdd.py
staged path: tests/unit/tools/shared_lifecycle/test_shell_transport/__init__.py
staged path: tests/unit/tools/shared_lifecycle/test_shell_transport/test_shell_transport_tdd.py
staged path: tools/pytest_plugin_environment.py
staged path: tools/pytest_plugin_shell.py
staged path: tools/pytest_plugins/llm_shared_pytest_loader.py
```

### Validation scope for step 4 shared_lifecycle_gate (round 1)

Validation scope: the whole suite.

### Requestor assessment for step 4 shared_lifecycle_gate (round 1)

Yes. Step 4 has been fully implemented.

The Step 4 validation section records the exact Yes verdict. The builder,
Windows transport and independent loader match the settled design. Production
modules stay below 650 lines; processing is linear in input entries/source
bytes, with fixed two-policy selection. The loader imports only stdlib/pytest.
No architecture violation or impaired reporting was found.

Focused preparation, shell transport and loader tests passed. The resolved
default day passed on 2026-11-09 at 15:15:01 +01:00. The full resolved
ghog day --full=speed --whole-suite passed at 15:33:22 +01:00 on the same date:
100% line coverage, zero outliers, zero exclusions, zero failures/warnings/xfails.
Coverage scope is tools, using sysmon line coverage. Evidence is retained in
.reviews/a.shared_lifecycle_gate.step4.tmp.speed.log.
Real Windows caller execution remains Step 7 and real Python 3.12 execution
remains Step 6. Those are not claimed from in-process tests.

### Implementation report for step 4 shared_lifecycle_gate (round 1)

The shared environment builder normalizes selection, binds the consumer root,
preserves unrelated paths/options, and returns a complete independent mapping.
It reads literal source contracts without importing policies, publishes only
the loader in immutable source-SHA-256 cache directories, verifies existing
entries and cleans failed/racing publication scratch. Counted IO tests prove
one read per named live source and cached loader for fresh/repeated preparation.

The Windows adapter owns complete-result serialization, delayed-expansion
escaping, atomic transfer publication and cleanup. The batch caller applies
only successful preparation. Focused tests simulate the transfer protocol for
both expansion states without launching a process.

The independent loader validates all selected live sources before imports,
rejects stale bindings, blocked policies and foreign canonical identities,
and registers/reuses canonical modules before initial conftests. Tests cover
cache/checkout removal, root containment, errors, import isolation and reuse.

No lifecycle budget, coverage omission or process exemption was added.
No new duration exclusion has been accepted for Step 4.

Final validation: ghog day --full=speed --whole-suite passed on 2026-11-09 at
15:33:22 +01:00, cov=100, outliers=0, excluded=0, fail=0, warn=0, xfail=0.
The earlier single uncovered owned-variable removal branch now has a concrete
owned-only deselection regression; no production behavior was changed to reach
coverage. The implementation-check and grouped commit plan were refreshed.

Writer notes: .reviews/a.shared_lifecycle_gate.step4.journal.md and .reviews/a.shared_lifecycle_gate.step4.handoff.md

### Change summary for step 4 shared_lifecycle_gate (round 1)

The staged set contains 13 paths grouped in root a.commit:

1. feat(pytest): prepare bound policy loading
   - tools/pytest_plugin_environment.py
   - tools/pytest_plugin_shell.py
   - tools/pytest_plugins/llm_shared_pytest_loader.py
   - bin/prepare_pytest_plugins.bat
2. test(pytest): cover prepared policy loading
   - tests/memory_filesystem.py
   - `tests/unit/tools/shared_lifecycle/test_preparation/__init__.py`
   - tests/unit/tools/shared_lifecycle/test_preparation/test_preparation_tdd.py
   - tests/unit/tools/shared_lifecycle/test_preparation/test_preparation_pbt.py
   - `tests/unit/tools/shared_lifecycle/test_shell_transport/__init__.py`
   - tests/unit/tools/shared_lifecycle/test_shell_transport/test_shell_transport_tdd.py
   - `tests/unit/tools/shared_lifecycle/test_loader/__init__.py`
   - tests/unit/tools/shared_lifecycle/test_loader/test_loader_tdd.py
3. docs(shared_lifecycle_gate): record step 4 validation
   - docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md

The validation plan's opening summary now reflects Steps 1-4 checked and
Steps 5-7 pending. Only Step 4 detailed rows changed. The commit-plan readiness
checker reports valid with no diagnostics; Markdown lint and spelling passed.

### Writer response for step 4 shared_lifecycle_gate (round 1)

Writer response:

This is the first Step 4 review round. No earlier Step 4 feedback or
disagreement exists. The writer requests independent assessment of the exact
staged implementation and Step 4 validation against the plan boundaries.

### Reviewer focus for step 4 shared_lifecycle_gate (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-4-round-1 -->

## Round 1 by reviewer - Step 4

- Recorded: 2026-11-09T15:56:00+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 4
- Outcome: answer

### Assessed index identity for step 4 shared_lifecycle_gate (exchange 1) (round 1)

Baseline index tree: 61d60d980883583c89eed8578bd0047ae02512d2

Assessed index tree: 61d60d980883583c89eed8578bd0047ae02512d2

### Implementation check for step 4 shared_lifecycle_gate (exchange 1) (round 1)

Result:

No. Step 4 has NOT been fully implemented.

The builder and the loader meet the plan. The Windows transfer does not: it
corrupts non-ASCII values on a default console, and concurrent preparations
can share one transfer file. The plan gives the shell adapter the
complete-result protocol, value preservation and transfer-output cleanup. The
unresolved findings list these with a low-severity builder edge and a
transcript lint failure.

What is in place and matches the plan and design:

- `normalize_selection` deduplicates `lifecycle` and `process` in stable order,
  accepts only an entirely empty declaration as "neither", and rejects
  unknown or empty tokens.
- `prepare_environment` never mutates its input. It recomputes owned
  `PYTHONPATH` entries (the old policy directory and any hash-named cache
  entry) and the injected `-p llm_shared_pytest_loader`, so re-preparation is
  idempotent and deselection removes only owned activation. The bootstrap
  directory comes before the policy directory, and neither the shared root
  nor its `tools` directory is exposed.
- Sources are checked by AST for exactly one literal integer
  `LOADER_CONTRACT_VERSION` before any cache IO, and policy bodies never run.
  Only the loader is cached, under its source SHA-256, outside both
  checkouts. An existing entry is verified and never rewritten. Publication
  uses a same-parent directory rename, verifies a racing winner and removes
  its scratch directory on every path.
- `pytest_plugin_shell.py` calls the shared builder once and does not
  duplicate selection. `tools/__init__.py` loads its submodules lazily, so
  running the adapter in the consumer's interpreter imports only stdlib.
- For ASCII values, the rest of the transfer is correct. The launcher
  detects the caller's delayed-expansion state, and the serializer
  doubles carets and escapes `!` only in records that contain `!`, which
  matches how `cmd` scans a token. Percent, ampersand and quote characters
  arrive through FOR substitution and are never reparsed. Failure applies
  nothing, because the caller's environment returns at `endlocal`.
- The loader keeps the pre-refusal boundary to `sys`, `pytest`, the version
  comparison and the raise. It checks every selected live source before
  importing any. Through `find_spec` it requires the canonical module to
  resolve to the bound policy file, which rules out an installed or cached
  fallback. It rejects blocked selections, both from `PYTEST_ADDOPTS` and
  argv at import time and through `is_blocked` in the hook. Its tryfirst
  `pytest_load_initial_conftests` checks root containment and foreign
  identities before registering anything, and reuses a module that was
  already loaded explicitly. A `UsageError` raised during `-p` import
  reaches pytest's `main` as exit 4.
- The completion search finds only the approved contract names, and all four
  production files parse at Python 3.10.

Missing work:

- A code-page-safe transfer for non-ASCII values, or a refusal before any
  value is applied.
- A unique transfer file for each preparation, and failure cleanup that
  touches only its own file.
- No empty `PYTHONPATH` entry when the incoming value is present but empty.

Architecture: selection and environment computation stay in the builder,
Windows encoding stays in the adapter, and the loader stays standalone with
stdlib and pytest only. No DDD-Hexagonal violation was found, and no
architecture issue needs addressing.

Performance: selection, path and option cleanup are linear. Hashing and AST
checks are linear in source bytes. The counted IO test proves one read per
required source and cached loader. No performance issue needs addressing.

Unit test coverage: the coverage source is `tools`, with a 100% gate, and the
requestor's speed walk reports 100%. Each builder, adapter and loader branch
has a dedicated test, and `bin/prepare_pytest_plugins.bat` lies outside the
gate and is checked by fragment. The transport tests use ASCII values only,
and nothing tests distinct transfer names. The fixes need those tests. The
test files sit outside the gate, and their top-level symbols are referenced.

Feature integrity: own-suite enforcement and reporting are unchanged. The
consumer-facing transfer can alter unrelated entries (first finding) and can
apply nothing while reporting success (second finding).

Validation plan effects:

No reviewer edit. The writer's Step 4 rows in
`docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md` say
`Yes. Step 4 has been fully implemented.`, which this assessment does not
confirm. The rows follow the template, and the recorded line counts (226,
92, 151, 338 and 281 for the largest test) match the staged files. The
transfer rows do not record the code page and transfer-name defects, and the
feature integrity row says unrelated entries are preserved, which the first
finding contradicts.

The document-level line correctly stays `No, it is not implemented`, and its
summary now names Steps 1-4 as checked. The staged diff touches only the
Step 4 section and that summary. Reviewer mode completed no umbrella row, and
the effort has none.

### Pre-repair mandatory checks and coverage for step 4 shared_lifecycle_gate (exchange 1) (round 1)

No repair was made. The pre-repair and assessed states are therefore the same
index tree, `61d60d980883583c89eed8578bd0047ae02512d2`, which equals the
request-time tree.

Requestor evidence, not repeated: `ghog day --whole-suite` passed at
2026-11-09T15:15:01+01:00, and `ghog day --full=speed --whole-suite` passed at
2026-11-09T15:33:22+01:00 with 100% tools coverage and zero failures,
warnings, xfails, outliers and exclusions.

Reviewer evidence. Each command ran once from the project root through the
worktree's `.\senv.bat` (guard cleared, `SWITCHPY_CHOICE=local`), with the
log-freshness check:

- `ghog check` ended at 2026-11-09T15:51:53+01:00 with `exit=1`. Ty,
  Pyright, Ruff, Radon, Vulture, the 650-line file check, ShellCheck and the
  EOF check all passed. The Markdown check failed with MD050 at lines 3015,
  3018 and 3020 of the unstaged review transcript (fourth finding).
- `ghog affected --no-cov --scope-file=.reviews/a.review-scope.code.v0.14.0.shared_lifecycle_gate.json`
  ended at 2026-11-09T15:53:09+01:00 with `exit=0`. Testmon found nothing
  affected since the requestor's walk, so 0 tests ran.

Coverage was assessed statically, and no `ghog day` or `ghog full` ran. Small
probes, run in the reviewer's scratch directory with no repository effect,
confirmed the first three findings:

- the launcher's `for /f` construct applied a UTF-8 non-ASCII value correctly
  under code page 65001 and incorrectly under 850, this machine's OEM
  default;
- four `cmd` processes started together printed the same
  `%RANDOM%-%RANDOM%` value;
- a trailing empty `PYTHONPATH` entry added the current directory to
  `sys.path`.

### Resolved validation set and sources for step 4 shared_lifecycle_gate (exchange 1) (round 1)

The request carries two commands:

- `ghog day --full=speed --whole-suite`, from the `project` source: the
  built-in default completed with the bound whole-suite selector, because
  the repository has no `.review-validation` declaration.
- `ghog day --whole-suite`, from the `plan` source: the shared checklist's
  resolved default day.

The requestor owns this set. It reports the default day green at
2026-11-09T15:15:01+01:00 and the speed day green at
2026-11-09T15:33:22+01:00, with 100% tools coverage, zero outliers and zero
exclusions. The root `a.ghog.log` tail and the retained
`.reviews/a.shared_lifecycle_gate.step4.tmp.speed.log` both showed the 15:33:22
result before the reviewer's commands ran. The reviewer ran neither command.

Exchange status binds the round to scope `whole` with fingerprint `686958cd`,
and the reviewer used that `paths.scope` capture.

### Resolver drift and direction for step 4 shared_lifecycle_gate (exchange 1) (round 1)

No drift. The resolver inputs are unchanged since the request. There is no
`.review-validation` declaration, the plan is the request-time version in the
same index tree, and the bound scope is `whole` (fingerprint `686958cd`). They
give the same two commands from the same sources. Neither direction adds or
drops a command.

### Repository state around validation for step 4 shared_lifecycle_gate (exchange 1) (round 1)

The validation path set holds the 13 staged paths, the plan and the root
`a.ghog.log` that the reviewer evidence commands write. It was captured before
assessment and again after both ghog commands.

- `validation-state compare` reported `acceptable: true`. No tracked or
  untracked path changed, and one ignored path changed (`a.ghog.log`).
- `umbrella-digest compare` reported not applicable and unchanged, because the
  request states `Umbrella draft: none`.
- After assessment, the live index tree is still
  `61d60d980883583c89eed8578bd0047ae02512d2`.
- The only unstaged change is the versioned review transcript
  `docs/v0.14.0/review.code.v0.14.0.shared_lifecycle_gate.md`. The exchange
  appended it, and the requestor's residual commit owns it.
- The reviewer's probes wrote only to its session scratch directory, outside
  the repository.

### Repair inventory for step 4 shared_lifecycle_gate (exchange 1) (round 1)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 4 shared_lifecycle_gate (exchange 1) (round 1)

An independent `commit-plan-check.bat --format json` rerun on the received
state exited 0 with `state: valid`, `ready: true` and no diagnostics. It listed
the same 13 staged paths and the same three ordered groups as the request
evidence:

1. `feat(pytest): prepare bound policy loading`, 4 paths: the builder, the
   shell adapter, the loader and the batch launcher.
2. `test(pytest): cover prepared policy loading`, 8 paths: the three test
   packages and the four-line `tests/memory_filesystem.py` routing change.
3. `docs(shared_lifecycle_gate): record step 4 validation`, 1 path.

Reviewer judgment on grouping and scope: every staged path belongs to exactly
one group, and the order runs from production code to its tests to the
validation record. `tests/memory_filesystem.py` is not in the plan's file
list. Its change only adds the three new test folders to the existing
in-memory scratch routing, so it is test support for this step and sits
correctly in group 2. No AI attribution trailer is present.

`a.commit` is accurate for the received state. The requested fixes belong in
groups 1 and 2, and their validation in group 3, so the grouping can stay.
The bodies will need a refresh.

### Findings and boundaries for step 4 shared_lifecycle_gate (exchange 1) (round 1)

Unresolved findings:

- Non-ASCII values are corrupted by the Windows transfer on a default
  console (`tools/pytest_plugin_shell.py` line 64,
  `bin/prepare_pytest_plugins.bat` line 23). `publish_result` writes the
  transfer file as UTF-8. The launcher reads it back with
  `for /f ... do set "%%V"`, and `cmd` decodes that file with the console
  code page. This machine's OEM code page is 850. A reviewer probe wrote
  `PROBE_VALUE=C:\Users\Rémi\x` as UTF-8 and applied it with the launcher's
  exact `for /f` construct. Under `chcp 850` the applied value did not equal
  the original (`MISMATCH`). Under `chcp 65001` it did (`MATCH`). Every
  transferred key is affected: the bound project root and policy directory,
  the cache entry under a non-ASCII `LOCALAPPDATA` user name, and the
  consumer's own `PYTHONPATH` and `PYTEST_ADDOPTS` entries. The design
  requires unrelated entries to survive unchanged. Instead, a wrong value is
  applied silently with exit 0. For the binding keys, the loader then
  refuses every pytest run. For the consumer's own entries, the corrupted
  value stays in place with no error at all. The focused transport tests use
  ASCII values only, so they cannot see this.
- Concurrent preparations can share one transfer file
  (`bin/prepare_pytest_plugins.bat` line 12). The name is built only from
  `%RANDOM%`, and `cmd` seeds that from the clock in whole seconds. A probe
  started four `cmd` processes together, and all four produced the same
  `%RANDOM%-%RANDOM%` value (`5652-19270`). Shells started together, such as
  several console panes running their `senv.bat` at once, therefore write
  and delete the same `%TEMP%` file. One shell can apply the other's result,
  which carries another project root or selection. Or one shell finds the
  file already deleted, sets nothing, and still exits 0, leaving the shell
  unprepared without a message. The failure path (line 26) can also delete a
  file that belongs to the other shell.
- A present but empty `PYTHONPATH` gains a trailing empty entry
  (`tools/pytest_plugin_environment.py` line 207). `"".split(os.pathsep)`
  is `[""]`, so a selected preparation produces `<entry>;<policy>;`. A probe
  with `PYTHONPATH=C:\probe-entry;` showed that CPython adds the current
  directory to `sys.path` for the empty entry. The design adds only the
  bootstrap and policy directories. `test_unselected_environment_preserves_option_text`
  passes `"PYTHONPATH": ""` with a selection, but asserts only idempotence,
  so it keeps this result. Severity is low, because `cmd` cannot hold an
  empty variable, but the Step 5 groundhog route passes a mapping directly.
- `ghog check` fails on the review transcript
  (`docs/v0.14.0/review.code.v0.14.0.shared_lifecycle_gate.md`, lines 3015,
  3018 and 3020, MD050). The round 1 request's change summary lists the three
  new `__init__.py` package markers without code spans, so their double
  underscores parse as strong emphasis. This is the same defect as Step 3
  round 1. The staged files pass. The transcript is unstaged and
  requestor-owned, but the next review-record commit would carry the lint
  failure.

Boundary-crossing work: None.

### Writer instructions for step 4 shared_lifecycle_gate (exchange 1) (round 1)

1. Code page: make the transfer exact for non-ASCII values, or refuse it
   before anything is applied. Either write the file in the caller's active
   console code page and raise `PreparationError` for a value that code page
   cannot represent, or have the launcher switch to code page 65001 for the
   `for /f` application and restore the previous code page afterwards. Add
   focused tests with a non-ASCII value in both delayed-expansion states.
   Add a non-ASCII path case on the default OEM code page to the Step 7
   executable harness obligations.
2. Transfer name: give each preparation its own transfer file. For example,
   let `pytest_plugin_shell.py` create it with `tempfile.mkstemp` in `%TEMP%`
   and print its path only on success, and have the launcher capture that
   path and treat a missing path as failure. The failure path must delete
   only its own file. Add a focused test showing that two preparations get
   distinct outputs and that a failure leaves another output untouched.
3. Empty `PYTHONPATH`: treat a present but empty value as absent when
   building the selected path list, so no empty entry is added. Extend
   `test_unselected_environment_preserves_option_text`, or add a test, to
   assert that the prepared `PYTHONPATH` has no empty entry.
4. Transcript: before the review-record commit, put the three `__init__.py`
   paths at transcript lines 3015, 3018 and 3020 in code spans. Write every
   path in future change summaries as a code span, as promised in Step 3.
5. Update the Step 4 validation rows (implemented, coverage, feature
   integrity) and the `a.commit` bodies, then rerun the focused tests and
   the resolved walks.

Non-blocking notes:

- `_import_policy` wraps every exception, including the usage error that
  `_live_module` already formatted. An origin or contract mismatch therefore
  repeats the plugin, the selection and "prepare the shell again".
- A project at a drive root passes `"C:\"` to Python. Under Windows
  command-line parsing, the trailing backslash escapes the closing quote.
  Step 7 could include that case, or the launcher could avoid it.

### Decision rationale for step 4 shared_lifecycle_gate (exchange 1) (round 1)

The six readiness-floor results:

- Identity: pass. The envelope, the readable identity, the plan, step 4,
  round 1, occurrence 1, `Umbrella draft: none` and the request-time index tree
  `61d60d98` all agree with the live exchange and index.
- Completeness: fail. Every Step 4 file and test obligation is present, but
  the Windows transfer corrupts non-ASCII values and can share a transfer
  file between concurrent preparations.
- Validation and coverage: fail. Reviewer `ghog check` exited 1 on the
  transcript's MD050 lint. `ghog affected --no-cov` exited 0 with nothing
  affected. Static reading finds no uncovered line, but the transport tests
  have no non-ASCII or distinct-name case.
- Staged attribution: pass. All 13 staged paths are writer work in three
  accurate groups. The reviewer staged nothing and edited nothing tracked.
- Findings: fail. Four findings are unresolved.
- `a.commit`: pass. The independent checker is valid and ready with no
  diagnostics, and the grouping is accurate for the received state.

This round made no repair, substantive or polishing. The request carries no
literal `Human guidance:` block, so the reviewer reports findings only.

Disposition: changes requested.

### Final reviewer decision for step 4 shared_lifecycle_gate (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-4-round-1 -->

## Round 2 by requestor - Step 4

- Recorded: 2026-11-09T16:15:49+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 4
- Outcome: request

### Review identity for step 4 shared_lifecycle_gate (round 2)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
Implementation step: 4
Review round: 2

### Code review evidence for step 4 shared_lifecycle_gate (round 2)

request_index_tree: d199f588c7a5eb432b3b138261ad5ad6eb66e7ca
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)
- `ghog day --whole-suite` (sources: plan)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(pytest): prepare bound policy loading
group 1 path: tools/pytest_plugin_environment.py
group 1 path: tools/pytest_plugin_shell.py
group 1 path: tools/pytest_plugins/llm_shared_pytest_loader.py
group 1 path: bin/prepare_pytest_plugins.bat
group 2: test(pytest): cover prepared policy loading
group 2 path: tests/memory_filesystem.py
group 2 path: tests/unit/tools/shared_lifecycle/test_preparation/__init__.py
group 2 path: tests/unit/tools/shared_lifecycle/test_preparation/test_preparation_tdd.py
group 2 path: tests/unit/tools/shared_lifecycle/test_preparation/test_preparation_pbt.py
group 2 path: tests/unit/tools/shared_lifecycle/test_shell_transport/__init__.py
group 2 path: tests/unit/tools/shared_lifecycle/test_shell_transport/test_shell_transport_tdd.py
group 2 path: tests/unit/tools/shared_lifecycle/test_loader/__init__.py
group 2 path: tests/unit/tools/shared_lifecycle/test_loader/test_loader_tdd.py
group 3: docs(shared_lifecycle_gate): record step 4 validation
group 3 path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
group 3 path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md
staged path: bin/prepare_pytest_plugins.bat
staged path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
staged path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md
staged path: tests/memory_filesystem.py
staged path: tests/unit/tools/shared_lifecycle/test_loader/__init__.py
staged path: tests/unit/tools/shared_lifecycle/test_loader/test_loader_tdd.py
staged path: tests/unit/tools/shared_lifecycle/test_preparation/__init__.py
staged path: tests/unit/tools/shared_lifecycle/test_preparation/test_preparation_pbt.py
staged path: tests/unit/tools/shared_lifecycle/test_preparation/test_preparation_tdd.py
staged path: tests/unit/tools/shared_lifecycle/test_shell_transport/__init__.py
staged path: tests/unit/tools/shared_lifecycle/test_shell_transport/test_shell_transport_tdd.py
staged path: tools/pytest_plugin_environment.py
staged path: tools/pytest_plugin_shell.py
staged path: tools/pytest_plugins/llm_shared_pytest_loader.py
```

### Validation scope for step 4 shared_lifecycle_gate (round 2)

Validation scope: the whole suite.

### Requestor assessment for step 4 shared_lifecycle_gate (round 2)

Yes. Step 4 has been fully implemented.

The builder, caller-code-page Windows transport and standalone loader meet the
Step 4 plan. All four round 1 findings are accepted and addressed with focused
regressions. No reviewer edits were made. Static review finds no architecture
violation or impaired reporting. Processing stays linear in environment/source
size, with fixed two-policy selection; every Python file stays below 650 lines.

The three-package focused run passed, followed by `ghog day --whole-suite` at
2026-11-09T16:06:11+01:00 and `ghog day --full=speed --whole-suite` at
2026-11-09T16:08:38+01:00, both exit 0. The full speed walk measured 100% line
coverage of `tools`, zero outliers/exclusions and zero failures/warnings/xfails.
Freshness was verified and canonical status confirms completion. Logs remain
in the ignored Step 4 artifact home. No coverage omission or budget change.

The refreshed validation plan records Step 4 only. Real Windows callers remain
Step 7 acceptance work; real Python 3.12 remains Step 6. No groundhog spawn
integration from Step 5 was implemented. No requirement or scope definition
changed; the bound whole-suite scope and validation commands remain unchanged.

Please independently assess the exact staged Step 4 repair and its evidence.

### Implementation report for step 4 shared_lifecycle_gate (round 2)

Preparation normalizes selected policies, binds the checkout, preserves
unrelated environment entries and verifies live source contracts by AST without
executing policies. Only the immutable SHA-256 loader cache is published,
outside both checkouts; policy sources remain live in the bound checkout.
The standalone loader preflights every selected policy before canonical
registration, rejects blocked or foreign modules, checks containment and reuses
matching explicitly loaded identities.

Round 1 repairs replace clock-seeded output names with exclusive temporary
files disclosed only after complete writes. The launcher passes its active
console code page; the adapter preserves representable non-ASCII values and
rejects incompatible complete results and filenames. Both delayed-expansion
states preserve metacharacters. Failure cleanup touches only the owned file;
missing result paths/files fail before application. Selected path computation
treats an empty incoming value as absent. The launcher also safely quotes a
drive-root project with a final dot component.

Tests use existing memory-backed scratch routing, with no child processes or
real waits. New finite cases cover code pages 850/65001, both expansion states,
encoding refusal, unique outputs, failure isolation, write and stdout failure,
and no empty selected path entry. Normalization properties retain 100 examples
per property as 20 batches of five bulk-byte examples. Counted IO verifies one
read per required source/cache input on fresh and repeated preparation.

Final validation: `ghog day --whole-suite` passed 2026-11-09T16:06:11+01:00;
`ghog day --full=speed --whole-suite` passed 2026-11-09T16:08:38+01:00 with
coverage 100, outliers 0, excluded 0, fail 0, warn 0 and xfail 0. The logs are
`.reviews/a.shared_lifecycle_gate.step4.tmp.r2.day.log` and
`.reviews/a.shared_lifecycle_gate.step4.tmp.r2.speed.log`. No duration exclusion,
baseline increase, coverage omission, lifecycle budget or process permission
was added. The first repair day caught test-double annotations, corrected
before the final green walks.

Production file lengths are 226/112/151 lines; the largest new test is 281
lines, all below 650. The plan adds only Step 7 executable OEM/non-ASCII,
refusal, concurrency and drive-root acceptance obligations. Actual shell
execution remains unclaimed until Step 7; independent Python 3.12 is Step 6.
All staged paths remain in the three prepared commit groups. Transcript path
code spans were polished, with the transcript unstaged for its residual batch.

Writer notes: .reviews/a.shared_lifecycle_gate.step4.journal.md and .reviews/a.shared_lifecycle_gate.step4.handoff.md

### Change summary for step 4 shared_lifecycle_gate (round 2)

The staged set contains 14 paths in three ordered root `a.commit` groups.

Group 1: `feat(pytest): prepare bound policy loading`

- `tools/pytest_plugin_environment.py`
- `tools/pytest_plugin_shell.py`
- `tools/pytest_plugins/llm_shared_pytest_loader.py`
- `bin/prepare_pytest_plugins.bat`

Group 2: `test(pytest): cover prepared policy loading`

- `tests/memory_filesystem.py`
- `tests/unit/tools/shared_lifecycle/test_preparation/__init__.py`
- `tests/unit/tools/shared_lifecycle/test_preparation/test_preparation_tdd.py`
- `tests/unit/tools/shared_lifecycle/test_preparation/test_preparation_pbt.py`
- `tests/unit/tools/shared_lifecycle/test_shell_transport/__init__.py`
- `tests/unit/tools/shared_lifecycle/test_shell_transport/test_shell_transport_tdd.py`
- `tests/unit/tools/shared_lifecycle/test_loader/__init__.py`
- `tests/unit/tools/shared_lifecycle/test_loader/test_loader_tdd.py`

Group 3: `docs(shared_lifecycle_gate): record step 4 validation`

- `docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md`
- `docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md`

The plan changes only the future Step 7 executable shell obligations raised
by review. The validation plan records refreshed Step 4 implementation,
coverage and feature-integrity evidence; Steps 5-7 remain pending.
The versioned review transcript remains unstaged for the authorized residual
review-record batch. Its three bare package-marker paths were polished.

### Writer response for step 4 shared_lifecycle_gate (round 2)

Writer response:

Accepted all four round 1 findings. The reviewer made no edits; all repairs
are writer-owned and substantive, with no disagreement.

- The launcher reads the active console code page and passes it to the
  transport. Both transferred values and the disclosed filename must encode
  exactly. An unrepresentable value fails before any result is applied.
- Python exclusively creates each result with `tempfile.mkstemp`. It prints
  that unique filename only after closing the complete result, and removes
  only its own file on write or output failure. The launcher rejects an absent
  result path or missing file. No clock-seeded name or cross-preparation
  deletion remains.
- Empty incoming `PYTHONPATH` is absent for selected path construction;
  deselected environments still preserve originally empty unrelated keys.
- The three package-marker paths in the round 1 transcript now have code
  spans. Every path in this round's change summary has a code span.

Focused regressions cover code pages 850 and 65001 with both expansion states,
unrepresentable values and filenames, distinct successful outputs, failure
isolation, interrupted writes, stdout failure, and no empty path entry.

The plan retains default OEM non-ASCII/refusal, concurrent preparations and
drive-root executable acceptance in Step 7. The drive-root argument also now
ends in a dot component, avoiding a backslash before its closing quote.
The advisory duplicate import-error wording is unchanged; its information and
failure behavior are correct, and no repair was requested for it.

Commit grouping is unchanged; the future acceptance clarification joins the
trailing validation documentation group. Bodies reflect the repairs.

### Reviewer focus for step 4 shared_lifecycle_gate (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-4-round-2 -->

## Round 2 by reviewer - Step 4

- Recorded: 2026-11-09T16:26:18+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 4
- Outcome: answer

### Assessed index identity for step 4 shared_lifecycle_gate (exchange 1) (round 2)

Baseline index tree: d199f588c7a5eb432b3b138261ad5ad6eb66e7ca

Assessed index tree: d199f588c7a5eb432b3b138261ad5ad6eb66e7ca

### Implementation check for step 4 shared_lifecycle_gate (exchange 1) (round 2)

Result:

Yes. Step 4 has been fully implemented.

All four round 1 findings are resolved, and no new finding was found. The
builder and loader are unchanged apart from one line. The Windows transfer now
carries the caller's code page and gives each preparation its own transfer
file.

Round 1 findings, rechecked:

- Code page: fixed. The launcher reads the active code page from `chcp` and
  passes it as `--code-page`. `publish_result` encodes the complete result in
  that code page before creating any file, so an unrepresentable value fails
  with `PreparationError` and nothing is applied. The transfer filename must
  also be representable. The reviewer then ran the real launcher under
  `chcp 850` in a scratch project named `Rémi-proj`, with `LOCALAPPDATA` and
  `TEMP` redirected to the scratch directory. With delayed expansion off and
  on, it exited 0, the applied `LLM_SHARED_PYTEST_ROOT` equaled the project
  path byte for byte, the selection read `lifecycle,process`, and no
  transfer file remained.
- Transfer name: fixed. `tempfile.mkstemp` creates each result exclusively,
  and Python prints its path only after the complete write is closed. The
  launcher captures the printed path and treats a missing path or file as
  failure. `%RANDOM%` is gone, and the failure path deletes only a path
  that this preparation received. A failure while writing or printing
  removes only this invocation's own file.
- Empty `PYTHONPATH`: fixed. A present but empty value is treated as absent
  for selected path construction, and the test now asserts no empty entry.
  An unselected environment still keeps the original empty key.
- Transcript lint: fixed. The three package markers at transcript lines 3015,
  3018 and 3020 are now code spans, and the Markdown step of the reviewer
  `ghog check` passed.

The drive-root argument now ends in `\.`, so a project at `C:\` no longer
puts a backslash before the closing quote. The plan adds the non-ASCII,
refusal, concurrency and drive-root cases to Step 7's executable acceptance,
which matches the round 1 instruction and changes no Step 4 scope.

The rest of the step is unchanged from round 1 and still matches the plan and
design: selection normalization, owned-entry recomputation, AST contract
checks without policy execution, the immutable SHA-256 loader cache outside
both checkouts, and the standalone loader's version guard, all-selected
preflight, root containment, blocked and foreign identity rejection, and
duplicate-safe registration.

Architecture: Windows encoding and file handling stay in the shell adapter,
which still calls the shared builder once. The loader keeps only stdlib and
pytest dependencies. No DDD-Hexagonal violation was found, and no
architecture issue needs addressing.

Performance: encoding and serialization are linear in the result size, and
one temporary file is created for each preparation. No performance issue
needs addressing.

Unit test coverage: the coverage source is `tools`, with a 100% gate, and the
requestor's speed walk reports 100%. New tests cover code pages 850 and 65001
in both expansion states, unrepresentable values, an invalid code page, an
unrepresentable filename, distinct outputs, failure isolation, interrupted
writes, stdout failure and the empty path entry. The launcher, outside the
gate, is checked by fragment, including the absence of `%RANDOM%`. Test files
sit outside the gate, and their top-level symbols are referenced. Physical
counts are 226, 112 and 151 for the production modules, 32 for the
launcher, and 281 for the largest test, all under 650. No unit-tested class
is below 100%, and no top-level symbol outside the gate is unreferenced.

Feature integrity: representable unrelated entries survive the shell transfer
unchanged, unrepresentable results are refused before application, and
concurrent preparations no longer interfere. Own-suite enforcement and
reporting are unchanged.

Validation plan effects:

No reviewer edit. The writer's Step 4 rows in
`docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md` say
`Yes. Step 4 has been fully implemented.`, which this assessment confirms. The
round 2 changes are accurate: the implemented row describes the code-page
transfer, exclusive transfer files and drive-root argument; the size row
records the adapter at 112 lines; the performance row carries the 16:06:11
and 16:08:38 walks; and the coverage and feature integrity rows name the new
regressions and the refusal behavior.

The document-level line correctly stays `No, it is not implemented`. The
staged plan change adds only Step 7 acceptance obligations, as requested in
round 1. Reviewer mode completed no umbrella row, and the effort has none.

### Pre-repair mandatory checks and coverage for step 4 shared_lifecycle_gate (exchange 1) (round 2)

No repair was made. The pre-repair and assessed states are therefore the same
index tree, `d199f588c7a5eb432b3b138261ad5ad6eb66e7ca`, which equals the
request-time tree.

Requestor evidence, not repeated: `ghog day --whole-suite` passed at
2026-11-09T16:06:11+01:00, and `ghog day --full=speed --whole-suite` passed at
2026-11-09T16:08:38+01:00 with 100% tools coverage and zero failures,
warnings, xfails, outliers and exclusions. The speed walk reused the check and
affected results of the 16:06:11 walk and ran the full suite fresh. The root
`a.ghog.log` tail showed that result before the reviewer's commands ran.

Reviewer evidence. Each command ran once from the project root through the
worktree's `.\senv.bat` (guard cleared, `SWITCHPY_CHOICE=local`), with the
log-freshness check:

- `ghog check` ended at 2026-11-09T16:22:41+01:00 with `exit=0` after
  1m 58.9s. Every static step passed, including the Markdown check that
  failed in round 1.
- `ghog affected --no-cov --scope-file=.reviews/a.review-scope.code.v0.14.0.shared_lifecycle_gate.json`
  ended at 2026-11-09T16:23:53+01:00 with `exit=0`. Testmon found nothing
  affected since the requestor's walk, so 0 tests ran.

Coverage was assessed statically, and no `ghog day` or `ghog full` ran. One
reviewer probe ran the real `bin/prepare_pytest_plugins.bat` under
`chcp 850` with delayed expansion off and on, as described in the
implementation check. Its project, cache and temporary directories were all
in the reviewer's scratch directory, with no repository effect.

### Resolved validation set and sources for step 4 shared_lifecycle_gate (exchange 1) (round 2)

The request carries two commands:

- `ghog day --full=speed --whole-suite`, from the `project` source: the
  built-in default completed with the bound whole-suite selector, because
  the repository has no `.review-validation` declaration.
- `ghog day --whole-suite`, from the `plan` source: the shared checklist's
  resolved default day.

The requestor owns this set and reports the default day green at
2026-11-09T16:06:11+01:00 and the speed day green at
2026-11-09T16:08:38+01:00. The reviewer ran neither command.

Exchange status binds the round to scope `whole` with fingerprint `686958cd`,
and the reviewer used that `paths.scope` capture.

### Resolver drift and direction for step 4 shared_lifecycle_gate (exchange 1) (round 2)

No drift. There is no `.review-validation` declaration, and the bound scope is
`whole` (fingerprint `686958cd`). The plan's staged change adds only Step 7
acceptance text and no validation command. The resolver inputs therefore give
the same two commands from the same sources. Neither direction adds or drops
a command.

### Repository state around validation for step 4 shared_lifecycle_gate (exchange 1) (round 2)

The validation path set holds the 14 staged paths and the root `a.ghog.log`
that the reviewer evidence commands write. It was captured before assessment
and again after both ghog commands.

- `validation-state compare` reported `acceptable: true`. No tracked or
  untracked path changed, and one ignored path changed (`a.ghog.log`).
- `umbrella-digest compare` reported not applicable and unchanged, because the
  request states `Umbrella draft: none`.
- After assessment, the live index tree is still
  `d199f588c7a5eb432b3b138261ad5ad6eb66e7ca`.
- The only unstaged change is the versioned review transcript
  `docs/v0.14.0/review.code.v0.14.0.shared_lifecycle_gate.md`. The exchange
  appended it, and the requestor's residual commit owns it.
- The reviewer's launcher probe wrote only to its session scratch directory,
  outside the repository.

### Repair inventory for step 4 shared_lifecycle_gate (exchange 1) (round 2)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 4 shared_lifecycle_gate (exchange 1) (round 2)

An independent `commit-plan-check.bat --format json` rerun on the received
state exited 0 with `state: valid`, `ready: true` and no diagnostics. It listed
the same 14 staged paths and the same three ordered groups as the request
evidence:

1. `feat(pytest): prepare bound policy loading`, 4 paths.
2. `test(pytest): cover prepared policy loading`, 8 paths.
3. `docs(shared_lifecycle_gate): record step 4 validation`, 2 paths: the plan
   and the validation plan.

Reviewer judgment on grouping and scope: every staged path belongs to exactly
one group. The round 2 repairs sit in groups 1 and 2, and the Step 7
acceptance text in the plan sits with the validation record in group 3,
which keeps documentation after the code it describes. No AI attribution
trailer is present.

`a.commit` is accurate for the received state, and the reviewer did not amend
it.

### Findings and boundaries for step 4 shared_lifecycle_gate (exchange 1) (round 2)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 4 shared_lifecycle_gate (exchange 1) (round 2)

No further implementation work is requested for Step 4.

Non-blocking notes:

- The launcher reads the code page with `tokens=2 delims=:`. Some localized
  `chcp` messages are reported to end with a period, for example a German
  `Aktive Codepage: 850.`. The installed `en-US` and `fr-FR` messages on this
  machine have none, so this could not be checked here. With a trailing
  period, `--code-page` would fail to parse and preparation would refuse, so
  no wrong value is ever applied. Adding `.` to `delims`, or accepting only
  the digits in Python, would remove the risk. Step 7 could include that case.
- `_import_policy` still repeats the identifying prefix when it wraps a
  usage error from `_live_module`. The writer chose to keep it, and the
  failure behavior is correct.

### Decision rationale for step 4 shared_lifecycle_gate (exchange 1) (round 2)

The six readiness-floor results:

- Identity: pass. The envelope, the readable identity, the plan, step 4,
  round 2, occurrence 1, `Umbrella draft: none` and the request-time index tree
  `d199f588` all agree with the live exchange and index.
- Completeness: pass. Every Step 4 obligation is implemented, and all four
  round 1 findings are fixed. The real launcher preserved a non-ASCII root
  under code page 850 in both expansion states.
- Validation and coverage: pass. Reviewer `ghog check` and
  `ghog affected --no-cov` both exited 0, and the requestor's whole-suite
  speed walk is green with 100% tools coverage. Static reading finds no
  coverage gap.
- Staged attribution: pass. All 14 staged paths are writer work in three
  accurate groups. The reviewer staged nothing and edited nothing tracked.
- Findings: pass. No current or carried finding is unresolved. The two
  remaining notes are non-blocking.
- `a.commit`: pass. The independent checker is valid and ready with no
  diagnostics, and the grouping and bodies are accurate.

This round made no repair, substantive or polishing. The request carries no
literal `Human guidance:` block.

Disposition: commit-ready. This is an advisory recommendation and does not
authorize a commit.

### Final reviewer decision for step 4 shared_lifecycle_gate (exchange 1) (round 2)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-4-round-2 -->

## Round 2 by human - Step 4 - human-confirmation

- Recorded: 2026-11-09T16:56:10+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 4
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->
